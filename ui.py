import math
import os
import re
import subprocess
import time
import traceback
import zlib
from base64 import b85encode
from bisect import bisect
from contextlib import contextmanager
from collections.abc import Generator, Iterable, Sequence
from io import StringIO
from types import TracebackType
from typing import Callable, Literal, Protocol, TextIO, final, override, runtime_checkable

from strkit import block_lines, matcherate, PeekStr

@runtime_checkable
class Itemsable[K, V](Protocol):
    def items(self) -> Iterable[tuple[K, V]]:
        return ()

class Clipboard(Protocol):
    def copy(self, mess: str) -> None:
        pass

    def paste(self) -> str:
        return ''

@final
class NullClipboard:
    def copy(self, mess: str) -> None:
        _ = mess

    def paste(self) -> str:
        return ''

# TODO snip the pyperclip dep, just implement command dispatchers and/or an osc52 fallback provider

try:
    import pyperclip # pyright: ignore[reportMissingImports]

    @final
    class Pyperclip:
        def copy(self, mess: str):
            pyperclip.copy(mess) # pyright: ignore[reportUnknownMemberType]

        def paste(self) -> str:
            return pyperclip.paste() # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

    DefaultClipboard = Pyperclip()

except:
    print('WARNING: no clipboard access available')
    DefaultClipboard = NullClipboard()

@final
class CopyAndThen:
    def __init__(self, clip: Clipboard, cmd: Sequence[str]):
        self.clip = clip
        self.cmd = cmd

    def copy(self, mess: str) -> None:
        self.clip.copy(mess)
        _ = subprocess.call(self.cmd)

    def paste(self) -> str:
        return self.clip.paste()

def fmt_dt(td: float):
    if td >= 1: return f'{td:.1f}s'
    if td >= 1: return f'{td:.1f}s'
    if td >= .000_1: return f'{1_000*td:.2f}ms'
    if td >= .000_000_1: return f'{1_000_000*td:.2f}µs'
    return f'{1_000_000_000*td:.2f}ns'

@final
class Timer:
    def __init__(self, start: float|None = None):
        self.start = time.clock_gettime(time.CLOCK_MONOTONIC) if start is None else start
        self.last = 0

    @property
    def now(self):
        now = time.clock_gettime(time.CLOCK_MONOTONIC)
        return now - self.start

    def sub(self):
        return Timer(self.start + self.now)

    def mark(self):
        now = self.now
        since = now - self.last if self.last else 0
        self.last = now
        return now, since

    @contextmanager
    def elapsed(self,
                name: str,
                collect: Callable[[str, float, float], None] = lambda _lable, _now, _elapsed: None,
                print: Callable[[str], None] = print,
                final: Callable[[str], None]|None = None):

        def fmt(label: str, now: float, elapsed: float):
            return f'T{now:.2f} +{fmt_dt(elapsed)} {name} {label}'

        def obs(label: str, now: float, elapsed: float, print: Callable[[str], None] = print):
            print(fmt(label, now, elapsed))
            collect(label, now, elapsed)

        def mark(label: str, print: Callable[[str], None] = print):
            now, since = t.mark()
            obs(label, now, since, print)

        t = self.sub()
        start = t.now

        yield mark

        end = t.now
        elapsed = end - start
        obs('done', end, elapsed, final or print)

State = Callable[['PromptUI'], 'State|None']

@final
class Next(BaseException):
    def __init__(self, state: State|None=None, input: str|None=None):
        super().__init__()
        self.state = state
        self.input = input

@final
class Tokens(PeekStr):
    pattern = re.compile(r'''(?x)
        # non-space token
        \s* ( [^\s]+ )

        # more tokens after any space
        \s* (?: ( [^\s] .* ) )?

        # end of raw input
        $
    ''')

    def __init__(self, raw: str = ''):
        self._raw = raw
        self._m = matcherate(self.pattern, raw)
        super().__init__(self._m)

    @override
    def __repr__(self):
        return f'Tokens(raw={self._raw!r}, _val={self._val!r}, _rest={self._m.rest!r})'

    @property
    def raw(self):
        return self._raw

    @raw.setter
    def raw(self, raw: str):
        self._raw = raw
        self._m = matcherate(self.pattern, raw)
        super().reset(self._m)

    @property
    def rest(self):
        val = self.val
        if val is not None:
            return f'{val} {self._m.rest}'
        return self._m.rest

    @rest.setter
    def rest(self, rest: str):
        self._m.rest = rest
        self._val = None

    def take_rest(self):
        rest = self.rest
        self._m.rest = ''
        self._val = None
        return rest

    @property
    def empty(self):
        return self.peek() is None

    # TODO refactor to an internal looper that takes an optional ->raw fn
    def next_or_input(self, ui: 'PromptUI', prompt: str):
        token = next(self, None)
        if not token:
            self.raw = ui.raw_input(prompt)
            token = next(self)
        return token

    def __enter__(self):
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        self.raw = ''
        return False

import pytest

@pytest.mark.parametrize('input,tokens', [
    ('', []),
    ('hello', ['hello']),
    ('hello world', ['hello', 'world']),
    ('  ', []),
    ('  hello', ['hello']),
    ('  hello world', ['hello', 'world']),
    ('hello  ', ['hello']),
    ('hello world  ', ['hello', 'world']),
    ('  hello  ', ['hello']),
    ('  hello world  ', ['hello', 'world']),
])
def test_tokens(input: str, tokens: list[str]):
    assert list(Tokens(input)) == tokens

@final
class PromptUI:
    @staticmethod
    def end_input(_: str):
        raise EOFError

    @staticmethod
    def int_input(_: str):
        raise KeyboardInterrupt

    @classmethod
    def test_ui(cls):
        return PromptUI(
            # TODO capture output for inspection

            # TODO provide canned input
            get_input = PromptUI.end_input,

            # TODO provide canned clipboard
            clip = NullClipboard(),
        )

    Tokens = Tokens

    def __init__(
        self,
        time: Timer|None = None,
        get_input: Callable[[str], str] = input,
        log_file: TextIO|None = None,
        sink: Callable[[str], None]|None = None,
        clip: Clipboard = DefaultClipboard,
    ):
        if log_file is not None and sink is not None:
            raise ValueError('must provide either sink or log_file, not both')
        elif log_file is not None:
            sink = lambda mess: print(mess, file=log_file, flush=True)
        elif sink is None:
            sink = lambda _: None

        self.time = Timer() if time is None else time
        self.t1 = math.nan
        self.t2 = math.nan

        self.get_input = get_input
        self.sink = sink
        self.clip = clip
        self.last: Literal['empty']|Literal['prompt']|Literal['print']|Literal['write']|Literal['remark'] = 'empty'
        self.zlog = zlib.compressobj()

    @property
    def screen_lines(self):
        return os.get_terminal_size().lines

    @property
    def screen_cols(self):
        return os.get_terminal_size().columns

    def copy(self, mess: str):
        self.clip.copy(mess)

    @contextmanager
    def copy_writer(self):
        buf = StringIO()
        yield buf
        self.clip.copy(buf.getvalue())

    def consume_copy(self, final_newline: bool = True, nl: str = '\n') -> Generator[None, str, None]:
        lines: list[str] = []
        try:
            while True: lines.append(( yield ))
        except GeneratorExit:
            s = nl.join(lines)
            if final_newline: s += nl
            self.copy(s)

    def paste(self) -> str:
        return self.clip.paste()

    def may_paste(self, tokens: Tokens|None = None):
        if tokens is None:
            tokens = self.input('Press <Enter> to 📋 or `>` for line prompt ')

        with tokens:
            if tokens.empty: return self.paste()

            if not tokens.have('>$'):
                return ''

        def read():
            self.print('Provide content, then eof or interreupt')
            try:
                while True:
                    yield self.raw_input('> ')
            except (EOFError, KeyboardInterrupt):
                return

        return '\n'.join(read())

    def _log_now(self):
        now = self.time.now
        d2 = now - self.t2
        d1 = self.t2 - self.t1
        a1 = d2 - d1
        self.t1, self.t2 = self.t2, now
        if not math.isnan(a1):
            return f'TDD{int(a1 * 1e6)}'
        if not math.isnan(d2):
            return f'TD{int(d2 * 1e6)}'
        return f'T{now}'

    def log(self, mess: str):
        now = self._log_now()
        self.sink(f'{now} {mess}')

    def logz(self, s: str):
        now = self._log_now()
        zb1 = self.zlog.compress(s.encode())
        zb2 = self.zlog.flush(zlib.Z_SYNC_FLUSH)
        self.sink(f'{now} Z {b85encode(zb1 + zb2).decode()}')

    def write(self, mess: str):
        self.last = 'print' if mess.endswith('\n') else 'write'
        print(mess, end='', flush=True)

    def fin(self, final: str = ''):
        if self.last == 'write':
            print(final)
            self.last = 'print'

    def br(self):
        self.fin()
        if self.last == 'print':
            print('')
            self.last = 'empty'

    def print(self, mess: str):
        self.fin()
        if mess.startswith('//'):
            if self.last != 'remark':
                print('')
            print(mess, flush=True)
            self.last = 'remark'
            return

        self.last = 'empty' if not mess.strip() else 'print'
        print(mess, flush=True)

    def raw_input(self, prompt: str):
        try:
            resp = self.get_input(prompt)
        except EOFError:
            self.log(f'{prompt}␚')
            raise
        self.log(f'{prompt}{resp}')
        self.last = 'prompt'
        return resp

    tokens: Tokens = Tokens()

    def input(self, prompt: str):
        self.tokens = Tokens(self.raw_input(prompt))
        return self.tokens

    def tokens_or(self, prompt: str):
        return self.input(prompt) if self.tokens.empty else self.tokens

    class Dispatcher:
        def __init__(self, spec: dict[str, State|str]):
            def resolve(name: str) -> State:
                st = spec[name]
                return resolve(st) if isinstance(st, str) else st
            self.names: list[str] = sorted(spec)
            self.thens: list[State] = [resolve(name) for name in self.names]
            self.alias: list[str] = [
                res if isinstance(res, str) else ''
                for name in self.names
                for res in (spec[name],)]
            self.re: int = 0

        def get(self, name: str):
            i = bisect(self.names, name)
            if 0 < i <= len(self.names) and self.names[i-1] == name:
                return self.thens[i-1]

        def update(self, items: Itemsable[str, State|str]|Iterable[tuple[str, State|str]]):
            if isinstance(items, Itemsable):
                items = items.items()
            for name, then in items:
                self.set(name, then)

        def set(self, name: str, then: State|str):
            alas = ''
            if isinstance(then, str):
                alas = then
                st = self.get(then)
                if st is None:
                    raise KeyError('undefined alias target')
                then = st
            i = bisect(self.names, name)
            if 0 <= i < len(self.names) and self.names[i] == name:
                self.thens[i] = then
                self.alias[i] = alas
            else:
                self.names.insert(i, name)
                self.thens.insert(i, then)
                self.alias.insert(i, alas)

        def show_help(self, ui: 'PromptUI', name: str, then: State, short: bool=True):
            ui.write(f'- {name}')
            doc = then.__doc__
            if doc:
                lines = block_lines(doc)
                ui.fin(f' -- {next(lines)}')
                for line in lines:
                    if short and not line: break
                    ui.print(f'  {line}')
            else:
                ui.fin()

        def show_help_list(self, ui: 'PromptUI'):
            for name, als, then in zip(self.names, self.alias, self.thens):
                if not name.strip(): continue
                if als:
                    ui.print(f'- {name} -- alias for {als}')
                else:
                    self.show_help(ui, name, then)

        def do_help(self, ui: 'PromptUI'):
            if not ui.tokens:
                return self.show_help_list(ui)
            maybe: list[str] = []
            mayst: list[State] = []
            token = next(ui.tokens)
            for name, then in zip(self.names, self.thens):
                if name.startswith(token):
                    maybe.append(name)
                    mayst.append(then)
            if not maybe:
                ui.print(f'invalid command {token!r}')
            elif len(maybe) == 1:
                self.show_help(ui, maybe[0], mayst[0], short=False)
            else:
                ui.print(f'ambiguous command; may be: {" ".join(repr(s) for s in maybe)}')

        def dispatch(self, ui: 'PromptUI') -> State|None:
            if ui.tokens.have(r'/help|\?+'):
                return self.do_help

            token = ui.tokens.peek()
            slurp: State|None = None
            dflt: State|None = None
            only: State|None = None
            maybe: list[str] = []
            for name, then in zip(self.names, self.thens):
                if name == token:
                    _ = next(ui.tokens, None)
                    return then
                if name == '': dflt = then
                elif name == ' ': slurp = then
                elif token and name.startswith(token):
                    only = then if not maybe else None
                    maybe.append(name)

            if ui.tokens and slurp is not None:
                return slurp
            if only:
                _ = next(ui.tokens, None)
                return only
            if maybe:
                return lambda ui: ui.print(f'! ambiguous command {token!r}; may be: {" ".join(repr(s) for s in maybe)}')
            if dflt is not None:
                return dflt
            if ui.tokens:
                return lambda ui: ui.print(f'! invalid command {token!r}; maybe ask for /help ?')

        def handle(self, ui: 'PromptUI'):
            st = self.dispatch(ui)
            if st is not None:
                self.re = 0
                return st(ui)
            else:
                self.re += 1
                if self.re > 1:
                    self.show_help_list(ui)

        def __call__(self, ui: 'PromptUI'):
            return self.handle(ui)

    class Prompt(Dispatcher):
        def __init__(self,
                     mess: str|Callable[['PromptUI'], str],
                     spec: dict[str, State|str]):
            super().__init__(spec)
            self.mess: str|Callable[['PromptUI'], str] = mess

        @override
        def __call__(self, ui: 'PromptUI'):
            mess = self.mess(ui) if callable(self.mess) else self.mess
            with ui.input(mess):
                return super().__call__(ui)

    def dispatch(self, spec: dict[str, State|str]):
        return self.Dispatcher(spec)(self)

    @contextmanager
    def deps(self,
             log_file: TextIO|None = None,
             sink: Callable[[str], None]|None = None,
             get_input: Callable[[str], str]|None = None,
             clip: Clipboard|None = None):
        if log_file is not None and sink is not None:
            raise ValueError('must provide either sink or log_file, not both')
        elif log_file is not None:
            sink = lambda mess: print(mess, file=log_file, flush=True)
        prior_sink = self.sink
        prior_clip = self.clip
        prior_get_input = self.get_input
        try:
            if callable(sink): self.sink = sink
            if callable(clip): self.clip = clip
            if callable(get_input): self.get_input = get_input
            self.t1 = math.nan
            self.t2 = math.nan
            yield self
        finally:
            self.sink = prior_sink
            self.clip = prior_clip
            self.get_input = prior_get_input

    State = State
    Next = Next

    @final
    class Chain:
        def __init__(self, *states: State):
            self.states = states

        def __call__(self, ui: 'PromptUI'):
            for state in self.states:
                st = state(ui)
                if st is not None: return st

    def interact(self, state: State):
        while True:
            try:
                state = state(self) or state

            except Next as n:
                state = n.state or state
                if n.input is not None:
                    self.tokens.raw = n.input

            except EOFError:
                self.log('<EOF>')
                self.print(' <EOF>')
                raise

            except KeyboardInterrupt:
                self.log('<INT>')
                self.print(' <INT>')
                raise

            except StopIteration:
                self.log('<STOP>')
                self.print(' <STOP>')
                return

    @staticmethod
    @contextmanager
    def catch_state(type_: type[BaseException]|tuple[type[BaseException], ...], st: State):
        try:
            yield
        except type_:
            raise Next(st)

    @contextmanager
    def exc_print(self, mess: str|Callable[[], str]):
        try:
            yield
        except:
            if callable(mess): mess = mess()
            self.print(mess)
            raise

    @contextmanager
    def catch_exception(self,
                        type_: type[BaseException]|tuple[type[BaseException], ...],
                        then_: Literal['pass', 'stop']|Exception|State = 'stop',
                        extra: Callable[['PromptUI'], None]|None = None,
                        ):
        try:
            yield
        except type_ as exc:
            tb = traceback.TracebackException.from_exception(exc)
            if extra: extra(self)
            for chunk in tb.format():
                for line in chunk.rstrip('\n').splitlines():
                    self.print(f'! {line}')
            if then_ == 'pass': return
            elif then_ == 'stop': raise StopIteration
            elif isinstance(then_, Exception): raise then_
            else: raise Next(then_)

    def print_exception(self, exc: BaseException):
        tb = traceback.TracebackException.from_exception(exc)
        for chunk in tb.format():
            for line in chunk.rstrip('\n').splitlines():
                self.print(f'! {line}')

    def run(self, state: State):
        try:
            self.interact(state)
        except (EOFError, KeyboardInterrupt):
            pass

    @classmethod
    def main(cls, state: State):
        ui = cls()
        ui.run(state)
