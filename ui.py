import argparse
import datetime
import json
import math
import os
import random
import re
import shlex
import sys
import subprocess
import time
import traceback
from warnings import deprecated
import zlib
from base64 import b64encode, b85encode
from bisect import bisect
from contextlib import contextmanager
from collections.abc import Generator, Iterable, MutableMapping, Sequence
from emoji import emoji_count
from io import StringIO
from types import TracebackType
from typing import Callable, Literal, Protocol, Self, TextIO, cast, final, override, runtime_checkable

from strkit import block_lines, matcherate, PeekIter, PeekStr, reflow_block

def join_word_seq(join: str, words: Sequence[str]):
    if len(words) == 1:
        return words[0]
    if len(words) == 2:
        a, b = words
        return f'{a} {join} {b}'
    else:
        return f'{", ".join(words[:-1])}, {join} {words[-1]}'

@final
class Backoff:
    def __init__(
        self,
        base: float = 2.0,
        scale: float = 1.0,
        limit: float = 0.0,
        jitter: float = 1.0,
        random: Callable[[], float] = random.random,
    ):
        self.base = base
        self.scale = scale
        self.limit = limit
        self.jitter = jitter
        self.random = random

    def __call__(self, count: int = 0):
        delay = math.pow(self.base, count)
        if self.scale == 0:
            jitter = self.jitter
            return 0.0 if jitter == 0 else jitter * self.random()
        delay *= self.scale
        if self.limit != 0:
            delay = min(self.limit, delay)
        if self.jitter != 0:
            delay *= self.jitter/2 + self.random()
        return delay

def test_Backoff():
    backoff_max = 12.0
    expected = [
        1.0,
        2.0,
        4.0,
        8.0,
        12.0,
        12.0,
        12.0,
        12.0,
        12.0,
        12.0,
    ]

    bk = Backoff(limit=backoff_max, random=lambda: 0.5)
    for i, x in enumerate(expected):
        assert bk(i) == x

    bk.random = lambda: 0.0000001
    for i, x in enumerate(expected):
        assert bk(i) == pytest.approx(x - x/2) # pyright:ignore [reportUnknownMemberType]

    bk.random = lambda: 0.999999
    for i, x in enumerate(expected):
        assert bk(i) == pytest.approx(x + x/2) # pyright:ignore [reportUnknownMemberType]

@final
class BackoffCounter:
    def __init__(
        self,
        count: int = 0,
        limit: int = 0,
        backoff: Backoff|None = None
    ):
        self.count = count
        self.count_init = count
        self.count_limit = limit
        self.backoff = Backoff() if backoff is None else backoff

    @property
    def done(self):
        return self.count_limit > 0 and self.count >= self.count_limit

    def reset(self, count: int|None = None):
        self.count = self.count_init if count is None else count

    def __enum_call__(self) -> tuple[int, float]:
        count = self.count
        self.count = count + 1
        return count,  0 if count <= 0 else self.backoff(count - 1)

    def enumerate(self) -> Generator[tuple[int, float]]:
        while not self.done:
            yield self.__enum_call__()

    def __call__(self):
        return self.__enum_call__()[1]

    def __iter__(self):
        return self

    def __next__(self):
        if self.done: raise StopIteration
        return self.__enum_call__()[1]

import pytest

@pytest.mark.parametrize('backoff_from,backoff_max,expected', [
    pytest.param(
        0,
        12.0,
        [0.0, 1.0, 2.0, 4.0, 8.0, 12.0, 12.0],
        id='init:0,max:12'),
    pytest.param(
        1,
        12.0,
        [1.0, 2.0, 4.0, 8.0, 12.0, 12.0],
        id='init:1,max:12'),
    pytest.param(
        -1,
        12.0,
        [0.0, 0.0, 1.0, 2.0, 4.0, 8.0, 12.0, 12.0],
        id='init:-1,max:12'),
    pytest.param(
        -3,
        12.0,
        [0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 4.0, 8.0, 12.0, 12.0],
        id='init:-1,max:12'),
])
def test_BackoffCounter(
    backoff_from: int,
    backoff_max: float,
    expected: list[float],
):
    backoff_utpo = backoff_from + len(expected)
    bkc = BackoffCounter(
        limit=backoff_utpo  ,
        count=backoff_from,
        backoff=Backoff(limit=backoff_max, random=lambda: 0.5),
    )
    ix: list[int] = []
    mid_vals: list[float] = []
    for i, val in bkc.enumerate():
        ix.append(i)
        mid_vals.append(val)
    assert ix == list(range(backoff_from, backoff_utpo))
    assert mid_vals == expected
    bkc.reset()
    assert list(bkc) == expected

@runtime_checkable
class Itemsable[K, V](Protocol):
    def items(self) -> Iterable[tuple[K, V]]:
        return ()

class Clipboard(Protocol):
    @property
    def name(self) -> str: return '<abstract>'

    def can_copy(self) -> bool: return False
    def can_paste(self) -> bool: return False
    def copy(self, mess: str) -> None: pass
    def paste(self) -> str: return ''

@final
class NullClipboard:
    @property
    def name(self): return 'null'

    def can_copy(self): return False
    def can_paste(self): return False
    def copy(self, mess: str): _ = mess
    def paste(self): return ''

term_osc = '\033]'
term_st = '\033\\'

def term_osc_seq(code: int, *args: str):
    return f'{term_osc}{code};{";".join(args)}{term_st}'

@final
class OSC52Clipboard:
    notified: bool = False

    def _maybe_not(self):
        if not self.notified:
            self.notified = True
            print('WARNING: OSC-52 paste not-implemented', file=sys.stderr)

    @property
    def name(self): return 'osc52'

    def can_copy(self): return True
    def can_paste(self):
        self._maybe_not()
        return False

    def copy(self, mess: str):
        # TODO print directly to tty? stderr? /dev/fd/2?
        encoded = b64encode(mess.encode())
        encoded_str = encoded.decode().replace("\n", "")
        print(term_osc_seq(52, 'c', encoded_str), end='')

    def paste(self):
        self._maybe_not()
        # TODO implement
        return ''

DefaultClipboard = NullClipboard()

# TODO snip the pyperclip dep, just implement command dispatchers and/or an osc52 fallback provider
try:
    import pyperclip
except:
    pyperclip = None
    pass

if pyperclip and pyperclip.is_available():
    pyp_copy = pyperclip.copy # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    pyp_paste = pyperclip.paste

    @final
    class Pyperclip:
        @property
        def name(self): return 'pyperclip'

        def can_copy(self): return True
        def can_paste(self): return True
        def copy(self, mess: str): pyp_copy(mess)
        def paste(self): return pyp_paste()

    DefaultClipboard = Pyperclip()

else:
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
Listing = MutableMapping[str, 'Listing|State']
Entry = tuple[str, Listing|State]

def descend(par: Listing, name: str) -> Listing:
    prior = par.get(name)
    sub: Listing = (
        {'..': par} if prior is None else
        {'..': par, '.': prior} if callable(prior) else
        prior)
    par[name] = sub
    return sub

def list_entry_name(path: str, ent: State|Listing|None):
    if ent is None:
        return f'{path}∅'
    if callable(ent):
        return f'{path}'
    return path if path.endswith('/') else f'{path}/'

def match(cur: Listing, head: str):
    if head in cur:
        yield head
        return

    # TODO handle punctuation more generically:
    #      ... starting punctuation anchors?
    #      ... only .* between non-punct?
    if head.startswith('.'):
        return

    pat = re.compile(
        r'.*'.join(re.escape(c)
        for c in head.lower()))
    for name in cur:
        if pat.match(name):
            yield name

def root(par: Listing):
    while '..' in par:
        ent = par['..']
        assert isinstance(ent, dict)
        par = ent
    return par

def do_tracing(ui: 'PromptUI'):
    '''
    show or set ui state tracing
    '''
    if not ui.tokens:
        ui.print(f'- tracing: {'on' if ui.traced else 'off'}')
        return
    if ui.tokens.have(r'(?ix) on | yes? | t(r(ue?)?)?'):
        return do_tron(ui)
    if ui.tokens.have(r'(?ix) off? | n[oaiue]? | f(a(l(se?)?)?)?'):
        return do_troff(ui)

def do_tron(ui: 'PromptUI'):
    '''
    turn tracing on
    '''
    if ui.traced:
        ui.print('! tracing already on ; noop')
        return
    else:
        raise ui.Tron

def do_troff(ui: 'PromptUI'):
    '''
    turn tracing off
    '''
    if not ui.traced:
        ui.print('! tracing already off ; noop')
        return
    else:
        raise ui.Troff

@final
class Handle:
    std_specials: Listing = {
        '!tracing': do_tracing,
        '!tron': do_tron,
        '!troff': do_troff,
    }

    par: Listing
    specials: Listing
    name: str = '.'
    may: tuple[str, ...] = ()
    given: tuple[str, ...] = ()
    pre_path: str = ''

    _call_direct: bool = False

    def __init__(
        self,
        arg: 'Handle|Listing|Iterable[Entry]',
        given: str|tuple[str, ...] = '',
        specials: Listing|None = None,
    ):
        init = ()
        if isinstance(arg, Handle):
            par = arg
        elif isinstance(arg, dict):
            par = cast(Listing, arg)
        else:
            init = arg
            par = cast(Listing, {})

        if isinstance(par, Handle):
            self.par = par.par
            self.name = par.name
            self.pre_path = par.path
            self.specials = dict(par.specials)

        else:
            self.specials = dict(self.std_specials)
            self.specials.update({
                'cwd': self.do_cwd,
                'pwd': self.do_cwd,

                'cd': self.do_chdir,
                'chdir': self.do_chdir,

                'dir': self.do_ls,
                'ls': self.do_ls,
                'help': self.do_help,
                # TODO special-er "?" alias for !help
            })
            self.par = par
            self.pre_path = '/' if '..' not in par else ''

        if specials:
            self.specials.update(specials)

        if init:
            for key, ent in init:
                if isinstance(ent, str):
                    ent = self[key]
                self[key] = ent

        if isinstance(given, str):
            given = tuple(given.split('/')) if given else ()

        if isinstance(par, Handle) and par.given:
            self.given = (*par.given, *given)
            return # unresolved parent -> unresolved

        if given and given[0] == '':
            self.par = root(self.par)
            self.name = '.'
            self.pre_path = '/'
            given = given[1:]
        self.given = given

        while self.given:
            part = self.given[0]
            if not part: continue

            if part == '..':
                ent = self.par.get('..')
                if ent is None:
                    break
                assert isinstance(ent, dict)
                self.given = self.given[1:]
                self.par = ent
                self.name = '.'
                self.pre_path, _, _ = self.pre_path.rpartition('/')
                continue

            may = tuple(match(self.par, part))
            if len(may) != 1:
                self.may = may
                break
            self.name = may[0]
            self.given = self.given[1:]

            ent = self.par[self.name]
            if callable(ent):
                break

            if self.pre_path and not self.pre_path.endswith('/'):
                self.pre_path += '/'
            self.pre_path += self.name
            self.par = ent
            self.name = '.'

    @override
    def __str__(self):
        path = self.path
        if not self.given:
            return path
        return ' / '.join((path, *self.given))

    @override
    def __repr__(self):
        return f'Handle<par:{self.par} pre_path:{self.pre_path} name:{self.name} may:{self.may} given:{self.given}>'

    @property
    def describe(self):
        def parts():
            path = self.path
            # XXX specials pathed as-if or as-called !...
            #     else f'!{path[1:]}' if ui.tokens.raw.startswith('!') and path[0] == '/'

            if self and not self.given:
                yield path
                for part in self.given:
                    yield '/'
                    yield part
                return

            yield (
                'unknown command' if not self.may
                else 'ambiguous command' if len(self.may) > 1
                else 'unimplemented command')

            yield path or '<Unknown>'

            if self.given:
                head = self.given[0]
                tail = self.given[1:]
                # TODO unify with __str__
                if not path.endswith('/'):
                    yield '/'
                yield f'{head}'
                if tail:
                    yield '/'
                    yield '/'.join(tail)
            else:
                yield '∅'

        return ' '.join(parts())

    @property
    def path(self):
        path = self.pre_path
        if not path:
            return ''
        if self.name != '.':
            if not path.endswith('/'):
                path += '/'
            if self.name:
                path += self.name.lstrip('/')
            else:
                path += '<Undefined>'
        return path

    @property
    def root(self):
        return Handle(root(self.par))

    def __bool__(self) -> bool:
        if not self.name: return False
        if len(self.may) > 1: return False
        return self.name == '.' or self.name in self.par

    @property
    def ent(self):
        return (
            None if not self else
            self.par if self.name == '.' else
            self.par.get(self.name))

    @ent.setter
    def ent(self, val: Listing|State):
        if self.name != '.':
            self.par = descend(self.par, self.name)
            self.pre_path = f'{self.pre_path}/{self.name}'
            self.name = '.'

        while self.given:
            name = self.given[0]
            if len(self.given) > 1:
                self.par = descend(self.par, name)
                self.pre_path = f'{self.pre_path}/{name}'
                self.given = self.given[1:]
            else:
                self.name = name
                self.given = ()

        if callable(val):
            self.par[self.name] = val

        elif self.name == '.':
            prior = tuple(k for k in self.par.keys() if k != '..')
            if prior:
                raise ValueError('cannot redefine listing')
            self.par.update(
                (k, v)
                for k, v in val.items()
                if k != '..')

        else:
            sub = {**val, '..': self.par}
            self.par[self.name] = sub
            self.pre_path = f'{self.pre_path}/{self.name}'
            self.par = sub
            self.name = '.'

    @ent.deleter
    def ent(self):
        if self.name:
            del self.par[self.name]

    def __getitem__(self, key: str):
        if not self:
            raise ValueError('cannot index unresolved handle')
        return Handle(self, key)

    def __setitem__(self, key: str, val: 'Handle|Listing|State'):
        if isinstance(val, Handle):
            ent = val.ent
            if ent is None:
                raise ValueError('value is an unresovled handle')
            val = ent
        self[key].ent = val

    def __delitem__(self, key: str):
        del self[key].ent

    def __call__(self, ui: 'PromptUI') -> 'PromptUI.State|None':
        self._call_direct = True
        with ui.trace_entry(lambda: f'{list_entry_name(self.path, self.ent)} call') as tr:
            if not self or self.given:
                return self._handle(ui, tr)
            with ui.tokens_or('> ') as tokens:
                return self.resolve(tokens, tr=tr)._handle(ui, tr)

    def search(self, cmd: str):
        while self and not self.given:
            yield self[cmd]
            self = self['..']

        yield Handle(self.specials, cmd)

    def resolve(self,
                tokens: 'PromptUI.Tokens',
                tr: 'PromptUI.Traced.Entish|None' = None):
        if tr is None:
            # with ui.trace_entry(lambda: f'{list_entry_name(self.path, self.ent)} resolve') as tr:
            tr = PromptUI.Traced.NoopEntry()

        if not tokens:
            tr.write(f'no input, just {self}')
            return self

        def prefer(may: Handle, be: Handle|None):
            return (
                may if be is None
                else may if not be and may
                else may if may and len(may.given) < len(be.given)
                else be)

        bang_m = tokens.have(f'!+(.+)')
        if bang_m:
            bang = bang_m[0]
            hndl = Handle(self.specials, bang)
            if not hndl:
                bang = str(bang_m[1])
                hndl = Handle(self.specials, bang)
            tr.write(f'bang {bang!r}')
            return hndl

        if self:
            cmd = next(tokens)
            be: Handle|None = None
            for may in self.search(cmd):
                maybe = prefer(may, be)
                tr.write(f'prefer({may}, {be}) -> {maybe}')
                be = maybe
            if be is not None:
                return be
            tr.write(f'fallthru {self}')
        else:
            tr.write(f'unresolved, just {self}')

        return self

    def handle(self, ui: 'PromptUI'):
        with ui.trace_entry(lambda: f'{list_entry_name(self.path, self.ent)} handle') as tr:
            return self._handle(ui, tr)

    def _handle(self, ui: 'PromptUI', tr: 'PromptUI.Traced.Entish') -> 'PromptUI.State|None':
        path = self.path
        ent = self.ent

        if callable(ent):
            tr.write(f'-> {PromptUI.describe(ent)}')
            return ent(ui)

        if isinstance(ent, dict):
            if self.given:
                gim = ent.get('.%')
                if callable(gim):
                    tr.write(f'.% {self.given!r} -> {PromptUI.describe(gim)}')
                    ui.tokens.give('/'.join(self.given))
                    return gim(ui)

            else:
                if ui.tokens and ui.tokens.peek() != '--':
                    sub = self[next(ui.tokens)]
                    sub._call_direct = False
                    return sub._handle(ui, tr)

                if self._call_direct and '._' in ent:
                    und = ent['._']
                    if callable(und):
                        tr.write(f'._ -> {PromptUI.describe(und)}')
                        return und(ui)

                if '.' in ent:
                    dot = ent['.']
                    if callable(dot):
                        tr.write(f'. -> {PromptUI.describe(dot)}')
                        return dot(ui)

                tr.write(f'/ print_sub_help')
                ui.write(path)
                if not path.endswith('/'): ui.write('/')
                ui.fin(' Commands:')
                ui.print_sub_help(ent, path)
                return

        tr.write(f'-> <Fin>')

        if len(self.may) > 1:
            ui.print(f'{self.describe}; may be: {join_word_seq('or', sorted(self.may))}')
        elif not self.may:
            ui.print(f'{self.describe}; possible commands:')
            for name in sorted(self.par):
                if not name.startswith('.'):
                    ui.print(f'  {name}')
        else:
            # TODO assert unreachable?
            ui.print(self.describe)

    def do_cwd(self, ui: 'PromptUI'):
        # TODO show $PWD? if diff?
        ui.print(self.path)

    def do_chdir(self, ui: 'PromptUI'):
        targ = (
            # TODO $OLDPWD if ui.tokens.have('-')
            # else
            self[next(ui.tokens)] if ui.tokens
            # TODO $HOME
            else self)

        if not targ:
            ui.print(f'! {targ.describe}')
            return

        # TODO set $PWD and $OLDPWD
        ui.print(targ.path)
        return targ

    def do_help(self, ui: 'PromptUI'):
        self.do_ls(ui,
                   handles=(self, self.root),
                   show_help=True)

    def do_ls(self, ui: 'PromptUI',
              handles: Iterable['Handle']|None = None,
              show_help: bool = False,
              show_hidden: bool = False,
              verbose: int = 0):
        args: list[str] = []
        while ui.tokens:
            v = ui.tokens.have('-(v+)', then=lambda m: len(m[1]))
            if v is not None:
                verbose += v
                continue

            if ui.tokens.have('-a'):
                show_hidden = True
                continue

            unk = ui.tokens.have('-.+', then=lambda m: m[0])
            if unk is not None:
                ui.print(f'! unknown ls option {unk}')
                return

            if ui.tokens.have('--'):
                args.extend(ui.tokens)
                break

            args.append(next(ui.tokens))

        if args:
            handles = (self[arg] for arg in args)
        elif handles is None:
            handles = (self,)

        def check(cur: Handle):
            if cur: return
            yield f'unresolved {cur.path}'
            if cur.may:
                yield f'may be {join_word_seq('or', sorted(cur.may))}'
            if cur.given:
                yield f'given ... / {' / '.join(cur.given)}'

        seen: set[str] = set()
        for cur in handles:
            path = cur.path
            if path in seen:
                continue
            else:
                seen.add(path)

            problems = tuple(check(cur))
            if problems:
                for prob in problems:
                    ui.print(f'! {prob}')
                continue

            if verbose:
                ui.print(f'is_root:{cur.name == '.' and '..' not in cur.par}')
                ui.print(f'pre:{cur.pre_path!r} / nom:{cur.name!r}')
                if cur.may: ui.print(f'may:{cur.may!r}')
                if cur.given: ui.print(f'may:{cur.may!r}')
                ui.print(f'type:{type(cur.ent).__name__}')

            try:
                ent = cur.ent
                if ent is None:
                    ui.print(f'{path}∅')
                    continue

                if show_help:
                    ui.print_help(
                        ent,
                        name=path,
                        mark='',
                        short=False,
                        show_hidden=show_hidden)
                    continue

                ui.write(path)
                if not callable(ent):
                    ui.fin('' if path.endswith('/') else '/')
                    for name in sorted(ent):
                        if name.startswith('.') and not show_hidden: continue
                        ui.write(f'  {name}')
                        ui.fin('' if callable(ent[name]) else '/')

            finally:
                ui.fin()

@contextmanager
def just[T](val: T) -> Generator[T]:
    yield val

def test_handle_init():
    root = Handle({})
    assert root.name == '.'
    assert root.path == '/'
    assert root.may == ()
    assert root.given == ()
    assert root.ent == {}

    with just(Handle(root)) as h:
        assert h.name == '.'
        assert h.path == '/'
        assert h.may == ()
        assert h.given == ()
        assert h.ent == {}

@pytest.fixture
def demo_world() -> tuple[Entry, ...]:
    return tuple(demo_world_entries())

def demo_world_entries() -> Generator[Entry]:
    def do_hello(ui: PromptUI):
        '''
        say hi!
        '''
        ui.print('hello world')
    yield 'hello', do_hello

    def do_fb(ui: PromptUI):
        '''
        a classic foil
        '''
        with ui.tokens_or('N> ') as tokens:
            n = tokens.have(r'\d+', then=lambda m: int(m[0]))
            if n is None:
                ui.print(f'! not an int')
                return
            try:
                ui.write(f'{n}: ')
                if n % 3 == 0: ui.write('fizz')
                if n % 5 == 0: ui.write('buzz')
            finally:
                ui.fin()
    yield 'app/fizzbuzz', do_fb

    def do_gen(ui: PromptUI):
        ui.print('do crimes')
    yield 'app/search/gen', do_gen

    def do_search_stuff(ui: PromptUI):
        ui.print(f'tokens:')
        for n, token in enumerate(ui.tokens, 1):
            ui.print(f'{n}. {token}')
    yield 'app/search/.', lambda ui: ui.print(f'dot: {list(ui.tokens)!r}')
    yield 'app/search/.%', do_search_stuff
    yield 'app/search/._', lambda ui: ui.print(f'auto: {list(ui.tokens)!r}')

    def do_greet(ui: PromptUI):
        '''
        say hi to <name>
        '''
        with ui.input('who are you? ') as tokens:
            ui.print(f'hello {tokens.rest}')
    yield 'hello/you', do_greet

    yield 'app/review/.', lambda ui: ui.print('do some review')
    yield 'app/review/log', {
        '.': lambda ui: ui.print('show log'),
        'last': lambda ui: ui.print('last log'),
        'find': lambda ui: ui.print('find log'),
    }
    yield 'app/report', lambda ui: ui.print('boring')

def test_handle_basics(demo_world: Iterable[Entry]):
    # NOTE this test is coupled to the demo_world's entry order
    root = Handle({})
    demo_world_it = iter(demo_world)
    def and_next(n: int=1):
        for _ in range(n):
            key, st = next(demo_world_it)
            root[key] = st

    with PromptUI.TestHarness() as h:
        assert h.run_all(root, '') == reflow_block('''
            >
            / Commands:
            >  <EOF>
            ''')

    and_next()
    assert root['hello'].path == '/hello'

    with PromptUI.TestHarness() as h:
        assert h.run_all(root, '') == reflow_block('''
            >
            / Commands:
            - /hello -- say hi!
            >  <EOF>
            ''')

    with PromptUI.TestHarness() as h:
        assert h.run_all(root, '/helo') == reflow_block('''
            > /helo
            hello world
            >  <EOF>
            ''')

    and_next()
    assert root['app/fizzbuzz'].path == '/app/fizzbuzz'

    with PromptUI.TestHarness() as h:
        assert h.run_all(root, '') == reflow_block('''
            >
            / Commands:
            - /app/
            - /hello -- say hi!
            >  <EOF>
            ''')

    with PromptUI.TestHarness() as h:
        ae = root['app'].ent
        assert isinstance(ae, dict)
        assert ae['..'] == root.ent
        assert h.run_all(root, '/a/f 15') == reflow_block('''
            > /a/f 15
            15: fizzbuzz
            >  <EOF>
            ''')

    and_next()
    assert root['app/search/gen'].path == '/app/search/gen'

    and_next(4)
    assert root['hello/you'].path == '/hello/you'

    with PromptUI.TestHarness() as h:
        assert h.run_all(root, '') == reflow_block('''
            >
            / Commands:
            - /app/
            - /hello/
            >  <EOF>
            ''')

    with PromptUI.TestHarness() as h:
        assert h.run_all(root, '/helo') == reflow_block('''
            > /helo
            hello world
            >  <EOF>
            ''')

    with PromptUI.TestHarness() as h:
        assert h.run_all(root, '/he/you', 'bob') == reflow_block('''
            > /he/you
            who are you? bob
            hello bob
            >  <EOF>
            ''')

    with PromptUI.TestHarness() as h:
        assert h.run_all(root, '/app/search/bob/lob/law yada yoda') == reflow_block('''
            > /app/search/bob/lob/law yada yoda
            tokens:
            1. bob/lob/law
            2. yada
            3. yoda
            >  <EOF>
            ''')

    with PromptUI.TestHarness() as h:
        assert h.run_all(root, '/app/search') == reflow_block('''
            > /app/search
            dot: []
            >  <EOF>
            ''')

    with PromptUI.TestHarness() as h:
        assert h.run_all(root['/app/search'], '') == reflow_block('''
            >
            auto: []
            >  <EOF>
            ''')

    assert root['app/review/..'].path == '/app'
    assert root['app/review']['..'].path == '/app'

    with PromptUI.TestHarness() as h:
        assert h.run_all(root, '/xx') == reflow_block('''
            > /xx
            unknown command / xx; possible commands:
              app
              hello
            >  <EOF>
            ''')

    and_next(3)

    # FIXME back
    with PromptUI.TestHarness() as h:
        assert h.run_all(root, '/app/re') == reflow_block('''
            > /app/re
            ambiguous command /app / re; may be: report or review
            >  <EOF>
            ''')

    with PromptUI.TestHarness() as h:
        assert h.run_all(root, 'app/rep') == reflow_block('''
            > app/rep
            boring
            >  <EOF>
            ''')

    with PromptUI.TestHarness() as h:
        assert h.run_all(root['app/review'], 'nonesuch') == reflow_block('''
            > nonesuch
            unknown command /app/review / nonesuch; possible commands:
              log
            >  <EOF>
            ''')

    with PromptUI.TestHarness() as h:
        assert h.run_all(root['app/review'], '../rep') == reflow_block('''
            > ../rep
            boring
            >  <EOF>
            ''')

    with PromptUI.TestHarness() as h:
        assert h.run_all(root, '../rep') == reflow_block('''
            > ../rep
            unknown command / .. / rep; possible commands:
              app
              hello
            >  <EOF>
            ''')

    del root['app/report']

    with PromptUI.TestHarness() as h:
        assert h.run_all(root, 'app/rep') == reflow_block('''
            > app/rep
            unknown command /app / rep; possible commands:
              fizzbuzz
              review
              search
            >  <EOF>
            ''')

def test_handle_specials(demo_world: Iterable[Entry]):
    root = Handle(demo_world)

    with PromptUI.TestHarness() as h:
        assert h.run_all(root,
            '!invalid',
            '!tracing',
            '!trac on',
            '!tron',
            '!troff',
            '!trac off',
        ) == reflow_block('''
            > !invalid
            unknown command / !invalid; possible commands:
              !tracing
              !troff
              !tron
              dir
              ls
            > !tracing
            - tracing: off
            > !trac on
            🔺 <TRON> -> /
            🔺 /
            🔺 / call> !tron
            🔺 bang '!tron' -> do_tron
            ! tracing already on ; noop
            🔺 -> <AGAIN>
            🔺 /
            🔺 / call> !troff
            🔺 bang '!troff' -> do_troff
            🔺 <!- Next <TROFF> -> /
            > !trac off
            ! tracing already off ; noop
            >  <EOF>
            ''')

    # TODO test !pwd
    # TODO test !chdir
    # TODO test !ls
    # with PromptUI.TestHarness() as h:
    #     assert h.run_all(root,
    #         '!ls',
    #     ) == reflow_block('''
    #         > !ls
    #         ''')

    # TODO test !help

    # TODO currently no easy way to provoke
    # - "unimplemented command" branch
    # - "∅" not-given branch

@final
class Next(BaseException):
    def __init__(self,
                 state: State|None=None,
                 input: str|None=None,
                 set_tracing: bool|None = None,
                 ):
        super().__init__()
        self.state = state
        self.input = input
        self.set_tracing: bool|None = set_tracing

    def annotate(self, ent: 'PromptUI.Traced.Entry'):
        if self.state:
            ent.write(f'next:{PromptUI.describe(self.state)}')
        if self.input is not None:
            ent.write(f'w/ {self.input!r}')
        if self.set_tracing is not None:
            ent.write(f'<TRO{'N' if self.set_tracing else 'FF'}>')

    def resolve(self, ui: 'PromptUI'):
        nxt = self.state
        txt = self.input
        if txt is not None:
            ui.tokens.raw = txt
        return nxt

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

    # TODO unify update* paths

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
        # TODO when is self.tdd_str worth?
        return self.td_str or self.t_str or 'None'

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

def default_dispatch(ui: 'PromptUI'):
    nxt = next(ui.tokens, None)
    if nxt:
        ui.print(f'! invalid command {nxt!r}; maybe ask for /help ?')

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

    def __getitem__(self, name: str):
        st = self.get(name)
        if st is None:
            raise KeyError(name)
        return st

    def __setitem__(self, name: str, then: State|str):
        self.set(name, then)

    def show_help_list(self, ui: 'PromptUI'):
        for name, als, then in zip(self.names, self.alias, self.thens):
            if not name.strip(): continue
            if als:
                ui.print(f'- {name} -- alias for {als}')
            else:
                ui.print_help(then, name=name)

    def do_help(self, ui: 'PromptUI'):
        # TODO reconcile w/ Shell help
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
            ui.print_help(mayst[0], name=maybe[0], short=False)
        else:
            ui.print(f'ambiguous command; may be: {" ".join(repr(s) for s in maybe)}')

    def dispatch(self, ui: 'PromptUI', dflt: State|None = default_dispatch) -> State|None:
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

    def handle(self, ui: 'PromptUI') -> 'PromptUI.State|None':
        dis_tok = ui.tokens.peek('')
        st = self.dispatch(ui, dflt=None)
        if st is not None:
            with ui.trace_entry(f'{dis_tok!r}') as ent:
                ent.write(f'-> {PromptUI.describe(st)}')
            self.re = 0
            if isinstance(st, PromptUI.Dispatcher) and ui.tokens:
                return st.handle(ui)
            return st(ui)
        else:
            with ui.trace_entry(f'{dis_tok!r}') as ent:
                ent.write(f'-> <HELP>')
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

@final
class EnvVars(MutableMapping[str, str]):
    def __init__(self, environ: MutableMapping[str, str]|None=None):
        self.vars: dict[str, str] = {}
        self.environ = os.environ if environ is None else environ

    @override
    def __iter__(self) -> Generator[str]:
        yield from self.vars
        for k in self.environ:
            if k not in self.vars:
                yield k

    @override
    def __len__(self):
        return len(self.vars) + sum(
            1
            for k in self.environ
            if k not in self.vars)

    @override
    def __getitem__(self, key: str):
        try:
            return self.vars[key]
        except KeyError:
            pass
        return self.environ[key]

    @override
    def __setitem__(self, key: str, val: str):
        self.vars[key] = val

    @override
    def __delitem__(self, key: str):
        try:
            del self.vars[key]
        except KeyError:
            pass
        try:
            del self.environ[key]
        except KeyError:
            pass

    def export(self, name: str, value: str|None=None):
        if value is None:
            value = self.vars.get(name)
        if not value:
            try:
                del self.environ[name]
            except KeyError:
                pass
        else:
            self.environ[name] = value
        try:
            del self.vars[name]
        except KeyError:
            pass

def test_EnvVars():
    os_env = {
        'FOO': 'bar',
    }
    vars = EnvVars(os_env)

    assert vars['FOO'] == 'bar'
    os_env['FOO'] = 'baz'
    assert vars['FOO'] == 'baz'

    vars['name'] = 'bob'
    assert vars['name'] == 'bob'
    assert 'name' not in os_env

    vars.export('name')
    assert vars['name'] == 'bob'
    assert os_env['name'] == 'bob'

    vars['name'] = 'sue'
    assert vars['name'] == 'sue'
    assert os_env['name'] == 'bob'

    vars.export('name', 'alice')
    assert vars['name'] == 'alice'
    assert os_env['name'] == 'alice'

    del vars['name']
    assert 'name' not in vars
    assert 'name' not in os_env

@final
class Shell:
    def __init__(self):
        self.root = Handle({})
        self.cur = Handle(self.root)
        self.env: dict[str, str] = {} # TODO allow dotted sub-structure ; nest system env
        self.prompt: str|Callable[['PromptUI', 'Shell'], str] = '> '
        self.re: int = 0
        self.re_prior: str = ''

    def getenv(self, key: str, dflt: str = ''):
        return self.env.get(key, dflt)

    def __call__(self, ui: 'PromptUI'):
        # TODO trace like Dispatcher
        prompt = (
            self.prompt(ui, self) if callable(self.prompt)
            else self.prompt)
        with ui.input(prompt) as tokens:
            hndl = self.cur.resolve(tokens)
            path = hndl.path
            if self.re_prior != path:
                self.re_prior = path
                self.re = 0
            elif hndl:
                self.re = 0
            else:
                self.re += 1
            return hndl.handle(ui)

# TODO def test_shell():

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

    @final
    class TestHarness:
        def __init__(self):
            self.input: list[str|BaseException] = []
            self.input_i: int = 0

            self.output: list[str] = []
            self.output_i: int = 0

            self.logs: list[str] = []

            self.may_copy: bool = True
            self.may_paste: bool = True
            self.clipboard: str = ''

            self.ui = PromptUI(
                sink = self.write,
                log_sink = self.log_write,
                get_input = self.get_input,
                clip = self,
            )

        def run_all(self, st: State, *ins: str):
            if ins:
                self.reset()
                self.input.extend(ins)
            else:
                self.clear()
            self.ui.interact(st)
            return self.all_output()

        def __enter__(self):
            return self

        def __exit__(
            self,
            type_: type[BaseException] | None,
            value: BaseException | None,
            traceback: TracebackType | None,
        ) -> bool:
            self.reset()
            return False

        def reset(self):
            self.input = []
            self.input_i = 0

            self.may_copy = True
            self.may_paste = True
            self.clipboard = ''

            self.clear()

        def clear(self):
            self.output = []
            self.output_i = 0
            self.logs = []

        def get_input(self, prompt: str):
            self.output.append(prompt)
            try:
                r = self.input[self.input_i]
            except IndexError:
                raise EOFError()
            self.input_i += 1
            if isinstance(r, str):
                self.output.append(f'{r}\n')
                return r
            raise r

        def write(self, s: str):
            self.output.append(s)

        def log_write(self, s: str):
            self.logs.append(s)

        def next_output_line(self):
            def parts():
                while True:
                    try:
                        i = self.output_i
                        part = self.output[i]
                    except IndexError:
                        return
                    self.output_i = i + 1
                    head, sep, tail = part.partition('\n')
                    if sep:
                        part = f'{head}{sep}'
                        if tail:
                            self.output[i] = part
                            self.output.insert(i+1, tail)
                        yield part
                        return
                    yield part
            return ''.join(parts())

        def output_lines(self):
            while self.output_i < len(self.output):
                yield self.next_output_line()

        def all_output(self):
            return ''.join(
                f'{line.rstrip()}\n'
                for line in self.output_lines())

        @property
        def name(self):
            return 'TestHarness'

        def can_copy(self): return self.may_copy
        def can_paste(self): return self.may_paste

        def copy(self, mess: str):
            self.clipboard = mess

        def paste(self):
            return self.clipboard

    Tokens = Tokens

    def __init__(
        self,
        time: Timer|None = None,
        get_input: Callable[[str], str] = input,
        sink: Callable[[str], None]|None = None,
        log_file: TextIO|None = None,
        log_sink: Callable[[str], None]|None = None,
        clip: Clipboard = DefaultClipboard,
    ):
        if log_file is not None and log_sink is not None:
            raise ValueError('must provide either log_sink or log_file, not both')
        elif log_file is not None:
            log_sink = lambda mess: print(mess, file=log_file, flush=True)
        elif log_sink is None:
            log_sink = lambda _: None
        if sink is None:
            sink = lambda s: print(s, end='', flush=True)

        self.time = Timer() if time is None else time
        self._log_time = LogTime()

        self.get_input: Callable[[str], str] = get_input
        self.sink = sink
        self.log_sink = log_sink
        self.clip = clip
        self.last: Literal['empty','pending','prompt','print','write','remark'] = 'empty'
        self.zlog = zlib.compressobj()

        self.traced = False
        self.tracer: PromptUI.Traced|None = None

        self.vars = EnvVars()

    @contextmanager
    def maybe_tracer(self, st: State):
        old_traced = self.traced
        old_tracer = self.tracer

        try:
            if self.traced:
                if not isinstance(st, PromptUI.Traced):
                    st = PromptUI.Traced(st)
                if self.tracer is not st:
                    self.tracer = st
            elif isinstance(st, PromptUI.Traced):
                self.traced = True
                self.tracer = st

            yield cast(PromptUI.State, st)

        except Next as n:
            if n.set_tracing is False:
                old_traced = False
                old_tracer = None
            raise n

        finally:
            self.traced = old_traced
            self.tracer = old_tracer

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
        self.copy(buf.getvalue())

    def line_consumer(self, end: str='\n') -> Generator[None, str, None]:
        with self.copy_writer() as w:
            try:
                print((( yield )), end=end, file=w)
            except GeneratorExit:
                pass

    def consume_lines(self, lines: Iterable[str], end: str='\n'):
        with self.copy_writer() as w:
            for line in lines:
                print(line, end=end, file=w)

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
        # TODO support one-shot paste replay: Callable[[subject: str], tuple[method: str, content: str]]
        def howdo(tokens: Tokens|None = None):
            if not self.clip.can_paste():
                return 'read:must:stdin', self.paste_read(subject)
            if tokens is None:
                tokens = self.input('Press <Enter> to 📋 {subject} or `>` to enter directly')
            with tokens:
                if tokens.empty:
                    return (
                        f'clipboard:{self.clip.name}',
                        self.clip.paste())
                elif tokens.have('>$'):
                    return 'read:user:stdin', self.paste_read(subject)
                else:
                    return 'noop:user', ''
            return 'noop:fallthru', ''

        method, content = howdo(tokens)
        self.log(f'pasted: {json.dumps({
            "subject": subject,
            "method": method,
            "content": content,
        })}')
        return content

    def log(self, mess: str):
        self._log_time.update(self.time.now)
        self.log_sink(f'{self._log_time} {mess}')

    def logz(self, s: str):
        self._log_time.update(self.time.now)
        zb1 = self.zlog.compress(s.encode())
        zb2 = self.zlog.flush(zlib.Z_SYNC_FLUSH)
        self.log_sink(f'{self._log_time} Z {b85encode(zb1 + zb2).decode()}')

    def line_writer(self, at: int = 0, limit: int = 0):
        return LineWriter(self, at, limit)

    def write(self, mess: str):
        self.last = 'print' if mess.endswith('\n') else 'write'
        self.sink(mess)

    def fin(self, final: str = ''):
        if self.last == 'write':
            self.sink(final + '\n')
            self.last = 'print'

    def br(self):
        self.fin()
        if self.last == 'print':
            self.sink('\n')
            self.last = 'empty'

    def link(self, url: str):
        # TODO url-escape any ';'s ?
        self.sink(term_osc_seq(8, '', url))

    @contextmanager
    def linked(self, url: str):
        self.link(url)
        yield self.link
        self.link('')

    def print(self, mess: str):
        self.fin()
        if mess.startswith('//'):
            if self.last != 'remark':
                self.sink('\n')
            self.sink(mess + '\n')
            self.last = 'remark'
            return

        self.last = 'empty' if not mess.strip() else 'print'
        self.sink(mess + '\n')

    def print_help(self,
                   ent: State|Listing,
                   name: str|None='',
                   short: bool=True,
                   mark: str = '-',
                   indent: str = '  ',
                   show_hidden: bool=False,
                   sep: str = ' -- '):
        try:
            if mark:
                self.write(f'{mark} ')
            if name:
                self.write(name)
            if callable(ent):
                if name == '':
                    self.write(ent.__name__)
                _ = self.print_block(ent.__doc__ or '', short=short, first=sep, rest=indent)
            else:
                if name and not name.endswith('/'):
                    self.write('/')
                if not short:
                    self.print_sub_help(
                        ent,
                        name or '<Unknown>',
                        short=True,
                        mark=f'{indent}{mark}',
                        indent=f'{indent}{' '*len(mark)} ',
                        show_hidden=show_hidden,
                        sep=sep)
        finally:
            self.fin()

    def print_sub_help(self,
                       ent: Listing,
                       path: str,
                       short: bool=True,
                       show_hidden: bool=False,
                       mark: str = '-',
                       indent: str = '  ',
                       sep: str = ' -- '):
        if not path.endswith('/'):
            path = f'{path}/'
        for sub in sorted(ent):
            if sub.startswith('.') and not show_hidden: continue
            self.fin()
            self.print_help(
                ent[sub],
                name=f'{path}{sub}',
                short=short,
                mark=mark,
                indent=indent,
                sep=sep)

    def print_block(self, mess: str,
                    short: bool=False,
                    first: str = '',
                    rest: str = ''):
        lines = block_lines(mess)
        line = next(lines, None)
        if line is not None:
            self.fin(f'{first}{line}')
            for line in lines:
                if short and not line: break
                self.print(f'{rest}{line}')
            return True
        else:
            return False

    def raw_input(self, prompt: str):
        self.last = 'pending'

        self.log(f'{prompt}␅')
        try:
            resp = self.get_input(prompt)
        except EOFError:
            self.log(f'␄')
            raise
        self.log(f'␆{resp}')
        self.log(f'{prompt}{resp}') # TODO deprecated and redundant by above logs
        self.last = 'prompt'
        return resp

    tokens: Tokens = Tokens()

    def input(self, prompt: str):
        self.tokens = Tokens(self.raw_input(prompt))
        return self.tokens

    def tokens_or(self, prompt: str):
        return self.input(prompt) if self.tokens.empty else self.tokens

    Dispatcher = Dispatcher
    Prompt = Prompt
    Shell = Shell
    Handle = Handle

    def dispatch(self, spec: dict[str, State|str]):
        return self.Dispatcher(spec)(self)

    @contextmanager
    def deps(self,
             log_file: TextIO|None = None,
             log_sink: Callable[[str], None]|None = None,
             get_input: Callable[[str], str]|None = None,
             # TODO sink
             clip: Clipboard|None = None):
        if log_file is not None and log_sink is not None:
            raise ValueError('must provide either log_sink or log_file, not both')
        elif log_file is not None:
            log_sink = lambda mess: print(mess, file=log_file, flush=True)
        prior_log_sink = self.log_sink
        prior_clip = self.clip
        prior_get_input = self.get_input
        try:
            if callable(log_sink): self.log_sink = log_sink
            if callable(clip): self.clip = clip
            if callable(get_input): self.get_input = get_input
            self._log_time.reset()
            yield self
        finally:
            self.log_sink = prior_log_sink
            self.clip = prior_clip
            self.get_input = prior_get_input

    @staticmethod
    def describe(st: State|None) -> str:
        if st is None:
            return '<AGAIN>'
        if isinstance(st, PromptUI.Traced):
            st = st.state
        try:
            fn = cast(object, getattr(st, '__func__', st))
            nom = cast(object, getattr(fn, '__qualname__') or getattr(fn, '__name__'))
            if isinstance(nom, str):
                return nom
        except AttributeError:
            pass
        return f'{st}'

    State = State
    Listing = Listing
    Entry = Entry

    Next = Next
    Troff = Next(set_tracing=False)
    Tron = Next(set_tracing=True)

    @final
    class Traced:
        @staticmethod
        @deprecated('use PromptUI.describe')
        def describe(st: State|None) -> str:
            return PromptUI.describe(st)

        @staticmethod
        def explain(err: Exception) -> str:
            if isinstance(err, StopIteration):
                return '<STOP>'
            elif isinstance(err, EOFError):
                return '<EOF>'
            elif isinstance(err, KeyboardInterrupt):
                return '<INT>'
            else:
                return repr(err)

        def __init__(self, st: State):
            self.mark: str = '🔺'
            self.state = st

        @classmethod
        def MayTron(cls,
                    ui: 'PromptUI',
                    state: 'PromptUI.State',
                    n: Next):
            # NOTE this is essentially an `except Next` handler for
            #      PromptUI to keep the Tracer aware parts collected
            # NOTE the corresponding MayTroff handling is within
            #      Tracer.__call__ / except Next
            nxt = n.resolve(ui) or state
            if (
                n.set_tracing is True
                and not isinstance(state, cls)
            ):
                self = cls(nxt)
                ui.traced = True
                ui.tracer = self
                with self.entry(ui, '<TRON>') as ent:
                    ent.write(f'-> {PromptUI.describe(nxt)}')
                return self
            return nxt

        @final
        class Entry:
            def __init__(self, ui: 'PromptUI', mark: str):
                self.ui = ui
                self.mark = mark
                # TODO integrate or merge with PromptUI.last
                self.last: Literal['space','mess'] = 'space'

            @staticmethod
            @deprecated('use PromptUI.describe')
            def describe(st: State|None) -> str:
                return PromptUI.describe(st)

            def __enter__(self):
                self.ui.fin()
                return self

            def __exit__(
                self,
                type_: type[BaseException] | None,
                value: BaseException | None,
                traceback: TracebackType | None,
            ) -> bool:
                self.ui.fin()
                return False

            # NOTE this wants to be a subset of the PromptUI surface,
            # particularly, the output printing / formatting sub-surface

            def fin(self):
                if self.ui.last in ('pending', 'prompt', 'write'):
                    self.ui.write(f'\n{self.mark} ')
                else:
                    self.ui.write(f'{self.mark} ')
                    self.ui.last = 'write'
                self.last = 'space'

            def write(self, mess: str):
                while mess:
                    if self.ui.last != 'write':
                        self.ui.write(f'{self.mark} ')
                        self.last = 'space'

                    head, sep, mess = mess.partition('\n')
                    pre = '' if self.last == 'space' else ' '
                    self.ui.write(f'{pre}{head}{sep}')
                    self.last = 'space' if sep or head.rstrip() != head else 'mess'

        @final
        class NoopEntry:
            @staticmethod
            def describe(_st: State|None) -> str:
                return ''

            def __enter__(self):
                return self

            def __exit__(
                self,
                type_: type[BaseException] | None,
                value: BaseException | None,
                traceback: TracebackType | None,
            ) -> bool:
                return False

            # NOTE noop output surface ... aka NullOutput
            def fin(self): pass
            def write(self, _mess: str): pass

        Entish = Entry|NoopEntry

        @contextmanager
        def entry(self, ui: 'PromptUI', mess: str):
            with self.Entry(ui, self.mark) as ent:
                ent.write(mess)
                yield ent

        def __call__(self, ui: 'PromptUI') -> 'PromptUI.State|None':
            with self.entry(ui, f'{PromptUI.describe(self.state)}') as ent:
                try:
                    nxt = self.state(ui)

                except Next as n:
                    ent.write(f'<!- Next')

                    ret = False
                    if n.set_tracing is False:
                        ui.traced = False
                        ui.tracer = None
                        ret = True

                    n.annotate(ent)

                    nxt = n.resolve(ui)
                    if ret:
                        if nxt is None:
                            nxt = self.state
                        ent.write(f'-> {PromptUI.describe(nxt)}')
                        return nxt

                except Exception as err:
                    ent.write(f'-!> {self.explain(err)}')
                    raise

                else:
                    ent.write(f'-> {PromptUI.describe(nxt)}')

                if nxt is not None:
                    self.state = nxt

    @contextmanager
    def trace_entry(self, mess: str|Callable[[], str]):
        if self.tracer:
            with self.tracer.entry(self, mess() if callable(mess) else mess) as ent:
                yield ent
        else:
            yield PromptUI.Traced.NoopEntry()

    def interact(self, state: State):
        try:
            self.call_state(state)

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

    def call_state(self,
                   state: State,
                   thrash_backoff: bool = False,
                   thrash_after: int = 3,
                   ):
        thrashing = BackoffCounter(
            count=-thrash_after + 1,
            backoff=Backoff(limit = 16, jitter = 0))

        def unwrap(state: State):
            if isinstance(state, PromptUI.Traced):
                state = state.state
            return state

        last = unwrap(state)
        last_t = self.time.now

        with self.maybe_tracer(state) as state:
            while True:
                if thrash_backoff and thrashing.count > 0:
                    since = self.time.now - last_t
                    delay = thrashing.backoff(thrashing.count-1)
                    rem = delay - since
                    self.print(f'! 💤 ui thrash {datetime.timedelta(seconds=delay)} (rem: {datetime.timedelta(seconds=rem)})')
                    time.sleep(delay - since)

                last_t = self.time.now

                get_input = self.get_input
                did_input = False
                def got_input(mess: str):
                    nonlocal did_input
                    did_input = True
                    return get_input(mess)
                self.get_input = got_input

                try:
                    nxt = state(self)
                    # TODO did call input?
                except Next as n:
                    nxt = PromptUI.Traced.MayTron(self, state, n)
                finally:
                    self.get_input = get_input

                mon = nxt and unwrap(nxt)
                if did_input:
                    thrashing.reset()
                elif mon is None or mon is last:
                    thrashing.count += 1
                last = mon

                state = nxt or state

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
    @deprecated('use PromptUI.Arguable')
    def main(cls, state: State, trace: bool = False):
        ui = cls()
        ui.traced = trace
        ui.run(state)

    class Arguable[T : State]:
        @classmethod
        def main(cls):
            self, args = cls.parse_args()
            trace = cast(bool, args.trace)

            ui = PromptUI()
            ui.traced = trace
            return ui.run(self)

        @classmethod
        def parse_args(cls) -> tuple[Self, argparse.Namespace]:
            parser = argparse.ArgumentParser(
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            )
            cls.add_args(parser)
            args = parser.parse_args()
            self = cls()
            return self, args

        @classmethod
        def add_args(cls, parser: argparse.ArgumentParser):
            _ = parser.add_argument('--trace', '-t', action='store_true',
                                    help='Enable execution state tracing')

        def make_root(self) -> T:
            # TODO wants to be an abstract base class?
            raise NotImplemented('must implement make_root')

        def __init__(self):
            self.root: T = self.make_root()

        def __call__(self, ui: 'PromptUI'):
            return self.root(ui)

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

    def retries(self,
                what: str,
                verbose: int = 0,
                retries: int = 3,
                backoff: float = 1.0,
                backoff_max: float = 12.0,
                ):
        for retry, delay in BackoffCounter(
            limit=retries,
            backoff=Backoff(scale=backoff, limit=backoff_max),
        ).enumerate():
            if delay > 0:
                self.print(f'* backing off {datetime.timedelta(seconds=delay)}...')
                t1 = self.time.now
                try:
                    time.sleep(delay)
                except KeyboardInterrupt:
                    t2 = self.time.now
                    td = datetime.timedelta(seconds=t2 - t1)
                    self.print(f'... backoff sleep interrupted after {td}, retrying')
            if verbose > 1:
                self.print(f'* {what} attempt {retry}')
            elif verbose > 0 and retry > 0:
                self.print(f'* {what} retry {retry}')
            yield retry

    @contextmanager
    def check_proc[T: (str, bytes)](self, proc: subprocess.Popen[T]):
        with proc:
            self.print(f'$ {
               str(proc.args) if isinstance(proc.args, os.PathLike) else
               proc.args if isinstance(proc.args, str) else
               proc.args.decode() if isinstance(proc.args, bytes) else
               shlex.join(str(arg) for arg in proc.args) }')
            try:
                yield proc
            except:
                proc.kill()
                raise
        retcode = proc.returncode
        if retcode != 0:
            self.print(f'! exited {retcode}')
            raise subprocess.CalledProcessError(retcode, proc.args)

    def check_call[T: (str, bytes)](self, proc: subprocess.Popen[T]):
        with self.check_proc(proc):
            pass

def screen_width(s: str):
    return len(s) + emoji_count(s)

def screen_truncate(s: str, width: int):
    if screen_width(s) <= width:
        return s
    # TODO this is oblivious to zero-width/combining characters
    s = s[:width]
    # TODO this would probably be better as a binary search
    while screen_width(s) > width:
        s = s[:-1]
    return s

@final
class LineWriter:
    # TODO wants to accept just the output protocol (plus screen
    #      size attrs?)... and implement the same

    def __init__(self, ui: PromptUI, at: int = 0, limit: int = 0):
        self.ui = ui
        self.at = at
        self.limit = limit

    @property
    def remain(self):
        return self.limit - self.at

    def fin(self):
        self.ui.fin()
        self.at = 0

    def write(self, s: str):
        self.ui.write(s)
        _, nl, last = s.rpartition('\n')
        # TODO parse ansi positioning sequences
        if nl:
            self.at = screen_width(last)
        else:
            self.at += screen_width(last)

    def truncate(self, s: str, cont: str = '...'):
        n = self.remain
        if screen_width(s) > n:
            pre = screen_truncate(s, n-screen_width(cont))
            return f'{pre}{cont}'
        return s

    def __enter__(self):
        if not self.limit:
            self.limit = self.ui.screen_cols
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        self.fin()

    def wrap_tokens(
        self,
        tokens: PeekIter[str],
        pre: str = '',
        sep: str = ' ',
        sub_pre: str = '  ',
    ):
        if not tokens: return
        try:
            first = True
            while tokens:
                self.write(f'{pre}{next(tokens, '')}')
                while tokens:
                    part = f'{sep}{next(tokens)}'
                    n = screen_width(part)
                    if self.remain < n: break
                    self.write(part)
                if first:
                    first = False
                    pre = sub_pre
        finally:
            self.fin()

class Lister(Protocol):
    def __len__(self) -> int:
        return 0

    def display(self, ui: PromptUI, offset: int, limit: int):
        return None

    def select(self, ui: PromptUI) -> PromptUI.State|None:
        return None

@final
class Paginator:
    def __init__(self,
                 list: Lister,
                 mess: str = 'select> ',
                 limit: int = 10,
                 ):
        self.list = list
        self.mess = mess
        self.limit = limit
        self.offset = 0
        self.re = 0

    def prompt(self, ui: PromptUI):
        if self.re == 0:
            lim = len(self.list)
            hi = min(lim, self.offset + self.limit)
            ui.print(f'{self.list} [ {self.offset} : {hi} / {lim} ]')
            self.list.display(ui, self.offset, self.limit)
            if self.offset > 0:
                ui.print(f'/P -> <Prev Page>')
            if len(self.list) > self.offset + self.limit:
                ui.print(f'/N -> <Next Page>')
        return self.mess

    def __call__(self, ui: PromptUI):
        with ui.input(self.prompt(ui)) as tokens:
            if not tokens:
                self.re += 1
                return
            self.re = 0
            if tokens.have(r'(?xi) /P(r(ev?)?)?'):
                self.offset = max(0, self.offset-self.limit)
                return self
            if tokens.have(r'(?xi) /N(e(xt?)?)?'):
                self.offset = min(len(self.list) - self.limit, self.offset+self.limit)
                return self
            return self.list.select(ui)

@final
class SeqLister[T]:
    def __init__(self,
                 name: str,
                 items: Iterable[T],
                 show: Callable[[T], str] = lambda x: str(x),
                 ret: Callable[[T], State] = lambda _x: PromptUI.then_stop,
                 perse: Callable[[PromptUI], T|None] = lambda _ui: None,
                 ):
        self.name = name
        self.nitems = tuple(enumerate(items, 1))
        self.show = show
        self.perse = perse
        self.ret = ret
        self.choice: T|None = None

    @override
    def __str__(self):
        return self.name

    def __len__(self):
        return len(self.nitems)

    def display(self, ui: PromptUI, offset: int, limit: int):
        for n, item in self.nitems[offset:offset+limit]:
            ui.print(f'{n}. {self.show(item)}')

    def select(self, ui: PromptUI) -> State|None:
        m = ui.tokens.have(r'\d+', then=lambda m: int(m[0]))
        if m is not None:
            for n, item in self.nitems:
                if n == m:
                    self.choice = item
                    break
        else:
            self.choice = self.perse(ui)
        if self.choice is not None:
            return self.ret(self.choice)
