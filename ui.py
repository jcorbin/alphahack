import datetime
import json
import math
import os
import random
import re
import shlex
import subprocess
import time
import traceback
from warnings import deprecated
import zlib
from base64 import b64encode, b85encode
from bisect import bisect
from contextlib import contextmanager
from collections.abc import Generator, Iterable, Sequence
from io import StringIO
from types import TracebackType
from typing import Callable, Literal, Protocol, TextIO, cast, final, override, runtime_checkable

from strkit import block_lines, matcherate, PeekStr, reflow_block

def join_word_seq(join: str, words: Sequence[str]):
    if len(words) == 1:
        return words[0]
    if len(words) == 2:
        a, b = words
        return f'{a} {join} {b}'
    else:
        return f'{", ".join(words[:-1])}, {join} {words[-1]}'

def test_retry_backoffs():
    expected = [
        (0.0, 0.0, 0.0),
        (0.5, 1.0, 1.5),
        (1.0, 2.0, 3.0),
        (2.0, 4.0, 6.0),
        (4.0, 8.0, 12.0),
        (6.0, 12.0, 18.0),
        (6.0, 12.0, 18.0),
        (6.0, 12.0, 18.0),
        (6.0, 12.0, 18.0), (6.0, 12.0, 18.0),
        (6.0, 12.0, 18.0),
    ]

    ix: list[int] = []
    min_vals: list[float] = []
    mid_vals: list[float] = []
    max_vals: list[float] = []
    n = len(expected)
    for i, val in retry_backoffs(n-1, random=lambda: 0.0000001):
        ix.append(i)
        min_vals.append(val)
    for i, val in retry_backoffs(n-1, random=lambda: 0.5):
        assert ix[i] == i
        mid_vals.append(val)
    for i, val in retry_backoffs(n-1, random=lambda: 0.999999):
        assert ix[i] == i
        max_vals.append(val)

    assert ix == list(range(n))
    assert min_vals == pytest.approx([lo for lo, _, _ in expected]) # pyright:ignore [reportUnknownMemberType]
    assert mid_vals == pytest.approx([md for _, md, _ in expected]) # pyright:ignore [reportUnknownMemberType]
    assert max_vals == pytest.approx([hi for _, _, hi in expected]) # pyright:ignore [reportUnknownMemberType]

def retry_backoffs(
    retries: int,
    backoff: float = 1.0,
    backoff_max: float = 12.0,
    random: Callable[[], float] = random.random,
):
    yield 0, 0
    retry = 0
    while retries == 0 or retry < retries:
        retry += 1
        delay = min(backoff_max, backoff * math.pow(2, retry-1))
        yield retry, delay * (0.5 + random())

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
    @property
    def name(self): return 'osc52'

    def can_copy(self): return True
    def can_paste(self): return False

    def copy(self, mess: str):
        # TODO print directly to tty? stderr? /dev/fd/2?
        encoded = b64encode(mess.encode())
        encoded_str = encoded.decode().replace("\n", "")
        print(term_osc_seq(52, 'c', encoded_str), end='')

    def paste(self):
        # TODO implement
        return ''

DefaultClipboard = NullClipboard()

# TODO snip the pyperclip dep, just implement command dispatchers and/or an osc52 fallback provider
try:
    import pyperclip # pyright: ignore[reportMissingImports]
except:
    pyperclip = None
    pass

if pyperclip and pyperclip.is_available(): # pyright:ignore [reportUnknownMemberType]
    pyp_copy = pyperclip.copy # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    pyp_paste = pyperclip.paste # pyright:ignore [reportUnknownMemberType, reportUnknownVariableType]

    @final
    class Pyperclip:
        @property
        def name(self): return 'pyperclip'

        def can_copy(self): return True
        def can_paste(self): return True
        def copy(self, mess: str): pyp_copy(mess)
        def paste(self): return pyp_paste() # pyright:ignore [reportUnknownParameterType, reportUnknownVariableType]

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
Listing = dict[str, 'Listing|State']

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
    else:
        pat = re.compile(r'.*'.join(re.escape(head.lower())))
        for name in cur:
            if pat.match(name):
                yield name

def root(par: Listing):
    while '..' in par:
        ent = par['..']
        assert isinstance(ent, dict)
        par = ent
    return par

@final
class Handle:
    par: Listing
    name: str = '.'
    may: tuple[str, ...] = ()
    given: tuple[str, ...] = ()
    pre_path: str = ''

    _call_direct: bool = False

    def __init__(
        self,
        par: 'Handle|Listing',
        given: str|tuple[str, ...] = '',
    ):
        if isinstance(given, str):
            given = tuple(given.split('/')) if given else ()

        if isinstance(par, Handle):
            self.par = par.par
            self.name = par.name
            self.pre_path = par.path
            if par.given:
                self.given = (*par.given, *given)
                return

        else:
            self.par = par
            self.pre_path = '/' if '..' not in par else ''

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
        if self.given:
            path = ' / '.join((path, *self.given))
        return path

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
        return root(self.par)

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
                spec = tokens.have(f'!+(.+)', lambda m: m[1])
                if spec is not None:
                    tr.write(f'bang {spec!r}')
                    tokens.give(spec)
                    return specials(ui)

                return self._handle(ui, tr)

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

        try:
            tr.write(f'-> <Fin>')
            reason = (
                'unknown' if not self.may
                else 'ambiguous' if len(self.may) > 1
                else 'unimplemented')
            mark = (
                '/' if self.given and not path.endswith('/')
                else '' if self.given
                else '∅')
            nom = (
                '<Unknown>' if not path
                else f'!{path[1:]}' if ui.tokens.raw.startswith('!') and path[0] == '/'
                else f'{path}')
            ui.write(f'{reason} command {nom}{mark}')
            if self.given:
                ui.write(f' {self.given[0]}')
                tail = self.given[1:]
                if tail:
                    ui.write(f' / {'/'.join(tail)}')
            if len(self.may) > 1:
                ui.write(f'; may be: {join_word_seq('or', sorted(self.may))}')
            elif not self.may:
                ui.write('; possible commands:')
                for name in sorted(self.par):
                    if not name.startswith('.'):
                        ui.print(f'  {name}')
        finally:
            ui.fin()

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

specials = Handle({
    'tracing': do_tracing,
    'tron': do_tron,
    'troff': do_troff,
})

def test_handle():
    @contextmanager
    def just[T](val: T) -> Generator[T]:
        yield val

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

    with PromptUI.TestHarness() as h:
        assert h.run_all(root, '') == reflow_block('''
            >
            / Commands:
            >  <EOF>
            ''')

    def do_hello(ui: PromptUI):
        '''
        say hi!
        '''
        ui.print('hello world')
    root['hello'] = do_hello
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
    root['app/fizzbuzz'] = do_fb
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

    def do_gen(ui: PromptUI):
        ui.print('do crimes')
    root['app/search/gen'] = do_gen
    assert root['app/search/gen'].path == '/app/search/gen'

    def do_search_stuff(ui: PromptUI):
        ui.print(f'tokens:')
        for n, token in enumerate(ui.tokens, 1):
            ui.print(f'{n}. {token}')
    root['app/search/.'] = lambda ui: ui.print(f'dot: {list(ui.tokens)!r}')
    root['app/search/.%'] = do_search_stuff
    root['app/search/._'] = lambda ui: ui.print(f'auto: {list(ui.tokens)!r}')

    def do_greet(ui: PromptUI):
        '''
        say hi to <name>
        '''
        with ui.input('who are you? ') as tokens:
            ui.print(f'hello {tokens.rest}')
    root['hello/you'] = do_greet
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

    root['app/review/.'] = lambda ui: ui.print('do some review')
    root['app/review/log'] = {
        '.': lambda ui: ui.print('show log'),
        'last': lambda ui: ui.print('last log'),
        'find': lambda ui: ui.print('find log'),
    }
    root['app/report'] = lambda ui: ui.print('boring')

    with PromptUI.TestHarness() as h:
        assert h.run_all(root, '/app/re') == reflow_block('''
            > /app/re
            ambiguous command /app/ re; may be: report or review
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
            unknown command /app/review/ nonesuch; possible commands:
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
            unknown command /app/ rep; possible commands:
              fizzbuzz
              review
              search
            >  <EOF>
            ''')

    def symbolize(s: str):
        sym: dict[str, str] = {}
        def make_sym(m: re.Match[str]) -> str:
            key = m[1]
            if key not in sym:
                sym[key] = f'sym_{len(sym)}'
            return sym[key]
        return re.sub(r'0x([0-9a-fA-F]+)', make_sym, s)

    with PromptUI.TestHarness() as h:
        assert symbolize(h.run_all(root,
            '!invalid',
            '!tracing',
            '!trac on',
            '!tron',
            '!troff',
            '!trac off',
        )) == reflow_block('''
            > !invalid
            unknown command ! invalid; possible commands:
              tracing
              troff
              tron
            > !tracing
            - tracing: off
            > !trac on
            🔺 <TRON> -> /
            🔺 /
            🔺 / call> !tron
            🔺 bang 'tron'
            🔺 / call -> do_tron
            ! tracing already on ; noop
            🔺 -> <AGAIN>
            🔺 /
            🔺 / call> !troff
            🔺 bang 'troff'
            🔺 / call -> do_troff
            🔺 <!- Next <TROFF> -> /
            > !trac off
            ! tracing already off ; noop
            >  <EOF>
            ''')

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

    def show_help_list(self, ui: 'PromptUI'):
        for name, als, then in zip(self.names, self.alias, self.thens):
            if not name.strip(): continue
            if als:
                ui.print(f'- {name} -- alias for {als}')
            else:
                ui.print_help(then, name=name)

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
        self.last: Literal['empty','prompt','print','write','remark'] = 'empty'
        self.zlog = zlib.compressobj()

        self.traced = False
        self.tracer: PromptUI.Traced|None = None

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

    Dispatcher = Dispatcher
    Prompt = Prompt

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
                if self.ui.last in ('prompt', 'write'):
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

    def call_state(self, state: State):
        with self.maybe_tracer(state) as state:
            while True:
                try:
                    nxt = state(self)
                except Next as n:
                    nxt = PromptUI.Traced.MayTron(self, state, n)
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
    def main(cls, state: State, trace: bool = False):
        ui = cls()
        ui.traced = trace
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

    def retries(self,
                what: str,
                verbose: int = 0,
                retries: int = 3,
                backoff: float = 1.0,
                backoff_max: float = 12.0,
                ):
        for retry, delay in retry_backoffs(retries, backoff, backoff_max):
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
