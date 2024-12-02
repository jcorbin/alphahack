import os
import re
import subprocess
import time
import traceback
from contextlib import contextmanager
from collections.abc import Generator, Sequence
from types import TracebackType
from typing import final, override, Callable, Literal, Protocol, TextIO

from strkit import matcherate, PeekStr

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

@final
class Timer:
    def __init__(self, start: float|None = None):
        self.start = time.clock_gettime(time.CLOCK_MONOTONIC) if start is None else start
        self.last = self.start

    @property
    def now(self):
        now = time.clock_gettime(time.CLOCK_MONOTONIC)
        return now - self.start

    def sub(self):
        return Timer(self.now)

State = Callable[['PromptUI'], 'State|None']

@final
class NextState(BaseException):
    def __init__(self, state: State):
        super().__init__()
        self.state = state

@final
class Tokens(PeekStr):
    pattern = re.compile(r'''(?x)
        # non-space token
        \s* ( [^\s]+ )

        # more tokens after any space
        (?: \s+ ( .+ ) )?

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
        self.get_input = get_input
        self.sink = sink
        self.clip = clip
        self.last: Literal['empty']|Literal['prompt']|Literal['print']|Literal['write']|Literal['remark'] = 'empty'

    @property
    def screen_lines(self):
        return os.get_terminal_size().lines

    @property
    def screen_cols(self):
        return os.get_terminal_size().columns

    def copy(self, mess: str):
        self.clip.copy(mess)

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

    def log(self, mess: str):
        self.sink(f'T{self.time.now} {mess}')

    def write(self, mess: str):
        self.last = 'print' if mess.endswith('\n') else 'write'
        print(mess, end='', flush=True)

    def fin(self):
        if self.last == 'write':
            print('')
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
            yield self
        finally:
            self.sink = prior_sink
            self.clip = prior_clip
            self.get_input = prior_get_input

    State = State
    NextState = NextState

    def interact(self, state: State):
        while True:
            self.tokens.raw = ''

            try:
                state = state(self) or state

            except NextState as n:
                state = n.state

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
    def catch_state(type_: type[BaseException], st: State):
        try:
            yield
        except type_:
            raise NextState(st)

    @contextmanager
    def print_exception(self,
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
            else: raise NextState(then_)

    def run(self, state: State):
        try:
            self.interact(state)
        except (EOFError, KeyboardInterrupt):
            pass

    @classmethod
    def main(cls, state: State):
        ui = cls()
        ui.run(state)
