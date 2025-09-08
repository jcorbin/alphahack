import math
import os
import re
import subprocess
import time
import traceback
import zlib
from base64 import b64encode, b85encode
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
    def can_copy(self) -> bool: return False
    def can_paste(self) -> bool: return False
    def copy(self, mess: str) -> None: pass
    def paste(self) -> str: return ''

@final
class NullClipboard:
    def can_copy(self) -> bool: return False
    def can_paste(self) -> bool: return False

    def copy(self, mess: str) -> None:
        _ = mess

    def paste(self) -> str:
        return ''

@final
class OSC52Clipboard:
    def can_copy(self) -> bool: return True
    def can_paste(self) -> bool: return False

    def copy(self, mess: str) -> None:
        # TODO print directly to tty? stderr? /dev/fd/2?
        encoded = b64encode(mess.encode())
        encoded_str = encoded.decode().replace("\n", "")
        print(f'\033]52;c;{encoded_str}\007', end='')

    def paste(self) -> str:
        # TODO implement
        return ''

DefaultClipboard = NullClipboard()

# TODO snip the pyperclip dep, just implement command dispatchers and/or an osc52 fallback provider
try:
    import pyperclip # pyright: ignore[reportMissingImports, reportMissingTypeStubs]
except:
    pyperclip = None
    pass

if pyperclip and  pyperclip.is_available():
    pyp_copy = pyperclip.copy # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    pyp_paste = pyperclip.paste

    @final
    class Pyperclip:
        def can_copy(self) -> bool: return True
        def can_paste(self) -> bool: return True

        def copy(self, mess: str):
            pyp_copy(mess)

        def paste(self) -> str:
            return pyp_paste()

    DefaultClipboard = Pyperclip()

else:
    print('WARNING: falling back on OSC-52 half-implemented clipboard')
    DefaultClipboard = OSC52Clipboard()

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

    def resolve(self, ui: 'PromptUI'):
        if self.input is not None:
            ui.tokens.raw = self.input
        return self.state

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
class LogTime:
    def __init__(self,
            t1: float = math.nan,
            t2: float = math.nan,
            d1: float = math.nan,
            d2: float = math.nan,
            a1: float = math.nan):
        self.t1: float = t1
        self.t2: float = t2
        self.d1: float = d1
        self.d2: float = d2
        self.a1: float = a1

    def reset(self):
        self.__init__()

    def update(self, now: float):
        t2 = self.t2
        t1 = self.t1
        d2 = now - t2
        d1 = t2 - t1
        a1 = d2 - d1
        self.t2 = now
        self.t1 = t2
        self.d2 = d2
        self.d1 = d1
        self.a1 = a1

    def update_d(self, td: float):
        t1 = self.t2
        d2 = self.d2
        t2 = t1 + td
        a1 = td - d2
        self.t2 = t2
        self.t1 = t1
        self.d2 = td
        self.d1 = d2
        self.a1 = a1

    def update_dd(self, tdd: float):
        t1 = self.t2
        d1 = self.d2
        d2 = tdd + d1
        t2 = t1 + d2
        self.t2 = t2
        self.t1 = t1
        self.d2 = d2
        self.d1 = d1
        self.a1 = tdd

    def parse(self, tokens: PeekStr):
        t = tokens.have(r'(?x) T ( [-+]? \d+ [^\s]* )', then=lambda m: float(m[1]))
        if t is not None:
            self.update(t)
            return True

        td = tokens.have(r'(?x) TD ( [-+]? \d+ [^\s]* )', then=lambda m: float(m[1])/1e6)
        if td is not None:
            self.update_d(td)
            return True

        tdd = tokens.have(r'(?x) TDD ( [-+]? \d+ [^\s]* )', then=lambda m: float(m[1])/1e6)
        if tdd is not None:
            self.update_dd(tdd)
            return True

        self.reset()
        return False

    @property
    def tdd_str(self):
        return '' if math.isnan(self.a1) else f'TDD{int(self.a1 * 1e6)}'

    @property
    def td_str(self):
        return '' if math.isnan(self.d2) else f'TD{int(self.d2 * 1e6)}'

    @property
    def t_str(self):
        return '' if math.isnan(self.t2) else f'T{self.t2}'

    @override
    def __str__(self):
        return self.tdd_str or self.td_str or self.t_str or 'None'

    def items(self) -> Generator[tuple[str, float]]:
        yield 't1', self.t1
        yield 't2', self.t2
        yield 'd1', self.d1
        yield 'd2', self.d2
        yield 'a1', self.a1

    @override
    def __repr__(self):
        def parts() -> Generator[str]:
            for k, v in self.items():
                if not math.isnan(v): yield f'{k}={v}'
        return f'LogTime({", ".join(parts())})'

def test_logtime():
    # TODO parametrize
    raw_log = '''
    T1.23 one d1 nan d2 nan a1 nan
    T2.34 two d1 nan d2 1.11 a1 nan
    T3.45 three d1 1.11 d2 1.11 a1 0.00
    T4.56 five
    T5.67 six
    T6.78 seven
    T7.89 eight
    '''

    def parse_times(lines: Iterable[str]):
        lt = LogTime()
        for ln, line in enumerate(lines, 1):
            tokens = PeekStr(m[0] for m in re.finditer(r'[^\s+]+', line))
            assert lt.parse(tokens), f'#{ln} must parse time token'
            yield lt, tokens

    def isclose(a: float, b: float):
        return math.isclose(a, b, abs_tol=1e-5)

    def check_entry(lt: LogTime, tokens: Iterable[str], mark: str = ''):
        it = iter(tokens)
        parts = dict(lt.items())
        rest: list[str] = []
        for tok in it:
            rest.append(tok)
            if tok in {'t1', 't2', 'd1', 'd2', 'a1'}:
                vtok = next(it, None)
                assert vtok is not None, f'{mark}must have {tok} value'
                rest.append(vtok)
                val = float(vtok)
                got = parts.pop(tok)
                assert (
                    ( math.isnan(got) and math.isnan(val) )
                    or isclose(got, val)
                ), f'{mark}expected {tok} {got} =~ {val}'

    orig_lines = tuple(block_lines(raw_log))
    orig_times: list[float] = []
    td_log_lines: list[str] = []
    tdd_log_lines: list[str] = []

    for ln, (lt, pk) in enumerate(parse_times(orig_lines), 1):
        tokens = tuple(pk)
        check_entry(lt, tokens, mark=f'T #{ln} ')
        orig_times.append(lt.t2)
        mess = ' '.join(tokens)
        td_log_lines.append(f'{lt.td_str or lt.t_str or "None"} {mess}')
        tdd_log_lines.append(f'{lt} {mess}')

    for li, (lt, tokens) in enumerate(parse_times(td_log_lines)):
        ln = li + 1
        assert isclose(lt.t2, orig_times[li]), f'TD #{ln} time roundtrip'
        check_entry(lt, tokens, mark=f'TD #{ln} ')

    for li, (lt, tokens) in enumerate(parse_times(tdd_log_lines)):
        ln = li + 1
        assert isclose(lt.t2, orig_times[li]), f'TDD #{ln} time roundtrip'
        check_entry(lt, tokens, mark=f'TDD #{ln} ')

@final
class PromptUI:
    @staticmethod
    def then_eof(_ui: 'PromptUI'):
        raise EOFError()

    @staticmethod
    def end_input(_: str):
        raise EOFError()

    @staticmethod
    def then_int(_ui: 'PromptUI'):
        raise KeyboardInterrupt()

    @staticmethod
    def int_input(_: str):
        raise KeyboardInterrupt()

    @staticmethod
    def then_stop(_ui: 'PromptUI'):
        raise StopIteration()

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
        self._log_time = LogTime()

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

    def paste_lines(self):
        try:
            while True:
                yield self.raw_input('📋> ')
        except EOFError:
            return

    def paste_read(self, subject: str = 'content'):
        self.print(f'Provide {subject}, then <EOF>')
        return '\n'.join(self.paste_lines())

    def may_paste(self, tokens: Tokens|None = None, subject: str = 'content'):
        if not self.clip.can_paste():
            return self.paste_read(subject)
        if tokens is None:
            tokens = self.input('Press <Enter> to 📋 {subject} or `>` to enter directly')
        with tokens:
            if tokens.empty: return self.paste()
            if not tokens.have('>$'):
                return ''
        return self.paste_read()

    def log(self, mess: str):
        self._log_time.update(self.time.now)
        self.sink(f'{self._log_time} {mess}')

    def logz(self, s: str):
        self._log_time.update(self.time.now)
        zb1 = self.zlog.compress(s.encode())
        zb2 = self.zlog.flush(zlib.Z_SYNC_FLUSH)
        self.sink(f'{self._log_time} Z {b85encode(zb1 + zb2).decode()}')

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
            '''
            Spec keys match next token, preferring exact match, then
            unambiguous prefix match.

            The special key " " may provide preemptively parse a state,
            overriding such exact or prefix matching.

            The special key "" can override default fallthrough behavior, which
            just prints '! invalid command ...'.

            '''
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

        def items(self) -> Generator[tuple[str, State|str]]:
            for name, als, then in zip(self.names, self.alias, self.thens):
                if not als: yield name, then
            for name, als, then in zip(self.names, self.alias, self.thens):
                if als: yield name, als

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

        def dispatch(self,
                     ui: 'PromptUI',
                     dflt: State|None = lambda ui: ui.print(f'! invalid command {next(ui.tokens)!r}; maybe ask for /help ?'),
                     ) -> State|None:
            if ui.tokens.have(r'/help|\?+'):
                return self.do_help

            token = ui.tokens.peek()
            slurp: State|None = None
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
                st = slurp(ui)
                if st is not None: return st
            if only:
                _ = next(ui.tokens, None)
                return only
            if maybe:
                return lambda ui: ui.print(f'! ambiguous command {token!r}; may be: {" ".join(repr(s) for s in maybe)}')
            return dflt

        def dispatch_all(self, ui: 'PromptUI'):
            do_help = False
            cont: list[PromptUI.State] = []
            while ui.tokens:
                if ui.tokens.have(r'/help|\?+'):
                    do_help = True
                    continue
                st = self.dispatch(ui, dflt=None)
                if st:
                    st = st(ui)
                    if st:
                        cont.append(st)
                elif ui.tokens:
                    ui.print(f'! unrecognized token {next(ui.tokens)!r} ; try /help')
                    return
                else:
                    break

            if do_help:
                self.do_help(ui)
                raise StopIteration()

            for st in cont:
                try:
                    # TODO this is the (only? first?)) one-shot state execution
                    #      loop; is that okay?'should we make that more of a
                    #      thing separate from Dispatcher?
                    while st:
                        st = st(ui)
                except (EOFError, StopIteration):
                    continue

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
            self._log_time.reset()
            yield self
        finally:
            self.sink = prior_sink
            self.clip = prior_clip
            self.get_input = prior_get_input

    State = State
    Next = Next

    def interact(self, state: State):
        while True:
            try:
                state = state(self) or state

            except Next as n:
                state = n.resolve(self) or state

            except StopIteration:
                return

            except EOFError:
                self.log('<EOF>')
                self.print(' <EOF>')
                return

            except KeyboardInterrupt:
                self.log('<INT>')
                self.print(' <INT>')
                raise

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
        except KeyboardInterrupt:
            pass

    @classmethod
    def main(cls, state: State):
        ui = cls()
        ui.run(state)

    @final
    class Chain:
        def __init__(self, *states: State):
            self.states = states

        def __call__(self, ui: 'PromptUI'):
            for state in self.states:
                st = state(ui)
                if st is not None: return st

    @final
    class Choose[D]:
        def __init__(self,
                     items: Iterable[D],
                     then: Callable[[D], State|None],
                     show: Callable[['PromptUI', D], None] = lambda ui, d: ui.print(f'{d}'),
                     head: Callable[['PromptUI'], None] = lambda _: None,
                     foot: Callable[['PromptUI'], None] = lambda _: None,
                     mess: str|Callable[['PromptUI'], str] = '? ',
                     ) -> None:
            self.items = tuple(items)
            self.then = then
            self.show = show
            self.head = head
            self.foot = foot
            self.mess = mess
            self.prompt = PromptUI.Prompt(self.show_list, {
                " ": self.slurp_num,
            })

        def show_list(self, ui: 'PromptUI'):
            self.head(ui)
            for n, d in enumerate(self.items, 1):
                ui.write(f'{n}. ')
                self.show(ui, d)
                ui.fin()
            self.foot(ui)
            return self.mess(ui) if callable(self.mess) else self.mess

        def slurp_num(self, ui: 'PromptUI') -> State|None:
            n = ui.tokens.have(r'\d+', lambda m: int(m[0]))
            if n is None: return
            i = n - 1
            if 0 <= i < len(self.items):
                return lambda _: self.then(self.items[i])
            ui.print(f'selection out of range')

        def __call__(self, ui: 'PromptUI'):
            if not len(self.items):
                raise StopIteration()
            if len(self.items) == 1:
                return self.then(self.items[0])
            return self.prompt(ui)
