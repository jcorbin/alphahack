import os
import re
import subprocess
import time
from contextlib import contextmanager
from collections.abc import Sequence
from typing import cast, final, Any, Callable, Literal, Protocol, TextIO

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
class PromptUI:
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
        self.last: Literal['empty']|Literal['prompt']|Literal['print']|Literal['write'] = 'empty'

    @property
    def screen_lines(self):
        return os.get_terminal_size().lines

    @property
    def screen_cols(self):
        return os.get_terminal_size().columns

    def copy(self, mess: str):
        self.clip.copy(mess)

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

    @final
    class Tokens:
        def __init__(self, raw: str = ''):
            self.raw = raw
            self.token = ''
            self.rest = raw

        @property
        def empty(self):
            return not self.token and not self.rest

        @property
        def raw_empty(self):
            return not self.raw.strip()

        @property
        def head(self):
            if self.token: return self.token
            for token in self:
                if token: return token
            return ''

        def next(self) -> str:
            match = re.match(r'\s*([^\s]+)(?:\s+(.+))?$', self.rest)
            if match:
                self.token = cast(str, match.group(1))
                self.rest = cast(str, match.group(2) or '')
            else:
                self.token, self.rest = '', ''
            return self.token

        def next_or_input(self, ui: 'PromptUI', prompt: str):
            token = self.next()
            if not token:
                self.rest = ui.raw_input(prompt)
                token = self.next()
            return token

        def __iter__(self):
            while self.next():
                yield self.token

    tokens: Tokens = Tokens()

    def input(self, prompt: str):
        self.tokens = self.Tokens(self.raw_input(prompt))
        return self.tokens

    def head_or(self, prompt: str):
        return self.tokens.head or self.input(prompt).head

    def next_or(self, prompt: str):
        return self.tokens.next() or self.input(prompt).head

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
            try:
                state = state(self) or state
                self.tokens = self.Tokens()

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
    def catch_state(t: Any, st: State): # pyright: ignore[reportAny]
        try:
            yield
        except t as e: # pyright: ignore[reportAny]
            raise NextState(st)

    def run(self, state: State):
        try:
            self.interact(state)
        except (EOFError, KeyboardInterrupt):
            pass

    @classmethod
    def main(cls, state: State):
        ui = cls()
        ui.run(state)
