#!/usr/bin/env python

import argparse
import math
import json
import re
from collections import Counter, OrderedDict
from collections.abc import Generator, Iterable, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from dateutil.tz import gettz
from itertools import chain
from typing import Callable, Literal, Never, cast, final, override

from sortem import Chooser, Possible, RandScores
from store import StoredLog
from strkit import MarkedSpec, spliterate
from ui import PromptUI
from wordlist import WordList

def nope(_arg: Never, mess: str =  'inconceivable'):
    assert False, mess

def grep(tokens: Iterable[str],
         pat: re.Pattern[str],
         anchor: Literal['start', 'full']|None = None):
    fn = (
        pat.fullmatch if anchor == 'full' else
        pat.match if anchor == 'start' else
        pat.search)
    for word in tokens:
        if fn(word):
            yield word        

wordlist_cache_limit: int = 10
wordlist_cache: OrderedDict[str, WordList] = OrderedDict()

def load_wordlist(name: str):
    if name not in wordlist_cache:
        while len(wordlist_cache) >= wordlist_cache_limit:
            _ = wordlist_cache.popitem(last=True)
        wordlist_cache[name] = WordList(name, exclude_suffix='.spaceword_exclude.txt')
    else:
        wordlist_cache.move_to_end(name)
    return wordlist_cache[name]

def re_counted(atoms: Iterable[str]):
    return ''.join(re_count(atoms))

def re_count(atoms: Iterable[str]):
    last: str = ''
    n: int = 0
    did: bool = False
    for atom in atoms:
        if atom == last:
            n += 1
        else:
            if last and n:
                yield f'{last}{{{n}}}' if n > 1 else last
                did = True
            last = atom
            n = 1
    if last and n:
        lo = 0 if did else 1
        yield f'{last}{{{lo},{n}}}' if n > 1 else last

def ruler(
    content: str,
    width: int,
    align: Literal['<', '^', '>'] = '<',
    fill: str = '-',
):
    if align == '<':
        return f'{fill}{content:{fill}<{width-1}}'
    elif align == '>':
        return f'{content:{fill}>{width-1}}{fill}'
    elif align == '^':
        return f'{content:{fill}^{width}}'
    else: nope(align, 'invalid ruler align')

@final
class Board:
    def __init__(self,
                 size: int = 10,
                 letters: Iterable[str] = (),
                 grid: Iterable[str] = ()):
        self.size = size
        self.letters: list[str] = list(letters)
        self.grid: list[str] = [''] * self.size**2
        for i, l in enumerate(grid):
            if i < len(self.grid):
                self.grid[i] = l

    @property
    def re_letter(self):
        if not any(l for l in self.letters):
            return '\\0'
        ls = set(l for l in self.letters if l)
        return f'[{''.join(sorted(ls)).lower()}]'

    def ix_defined(self):
        sz = self.size
        for i, l in enumerate(self.grid):
            if l:
                y = i // sz
                x = i % sz
                yield i, x, y

    @property
    def defined_rect(self):
        ix = self.ix_defined()
        try:
            _, lo_x, lo_y = next(ix)
        except StopIteration:
            return None
        hi_x = lo_x + 1
        hi_y = lo_y + 1
        for _, x, y in ix:
            lo_x = min(lo_x, x)
            lo_y = min(lo_y, y)
            hi_x = max(hi_x, x + 1)
            hi_y = max(hi_y, y + 1)
        return lo_x, lo_y, hi_x, hi_y

    per_let = 100 # TODO is this also size^2?

    @property
    def score(self):
        let_score = self.per_let*sum(
            1
            for let in self.letters
            if not let)
        return let_score + self.space_bonus

    @property
    def max_score(self):
        return self.per_let*len(self.letters) + self.max_bonus

    @property
    def space_bonus(self):
        area = self.size**2
        w, h = 0, 0
        bounds = self.defined_rect
        if bounds:
            x1, y1, x2, y2 = bounds
            w = abs(x2 - x1)
            h = abs(y2 - y1)
        return area - w*h

    @property
    def max_bonus(self):
        return self.size**2

    def update(self, i: int, let: str):
        prior = self.grid[i]
        if prior == let: return
        if prior:
            last: int|None = None
            for j, l in enumerate(self.letters):
                if not l:
                    last = j
                elif last is not None and l > prior:
                    break
            if last is None:
                raise ValueError('unable to return prior letter')
            self.letters[last] = prior
        if let:
            self.letters[self.letters.index(let)] = ''
        self.grid[i] = let

    def x_cursor(self, x: int, y: int) -> Generator[int]:
        sz = self.size
        yield from range(y*sz + x, (y+1)*sz)

    def y_cursor(self, x: int, y: int) -> Generator[int]:
        sz = self.size
        yield from range(y*sz + x, len(self.grid), sz)

    def show(self,
             head: str|None = '',
             mid: str|None = '',
             foot: str|None = '',
             head_align: Literal['<', '^', '>'] = '<',
             mid_align: Literal['<', '^', '>'] = '<',
             foot_align: Literal['<', '^', '>'] = '<',
             mark: Callable[[int, int], str] = lambda _x, _y: ' '
             ) -> Generator[str]:
        width = 0
        for line in self.show_grid(
                mark=mark,
                head=head, head_align=head_align,
                foot=None):
            width = max(width, len(line))
            yield line
        if mid is not None:
            yield ruler(mid, width, mid_align)
        if any(l for l in self.letters):
            yield from self.show_letters(head=None, width=width,
                                         foot=foot, foot_align=foot_align)
        elif foot:
            yield ruler(foot, width, foot_align)

    def show_letters(self,
                     fill: str = '_',
                     head: str|None = '',
                     foot: str|None = '',
                     head_align: Literal['<', '^', '>'] = '<',
                     foot_align: Literal['<', '^', '>'] = '<',
                     width: int = 0,
                     span: int|None = None,
                     num: int|None = None):
        letters = self.letters
        num = max(len(letters), num or 0)
        nx = span if span else max(7, math.ceil(math.sqrt(num)))
        ny = math.ceil(num / nx)
        w = max(nx * 2, width)
        if head is not None:
            yield ruler(head, w, head_align)
        for y in range(ny):
            row = (
                letters[i] if i < len(letters) else fill
                for i in range(nx*y, nx*y+nx))
            srow = ''.join(f'{let or " "} ' for let in row)
            yield f'{srow: ^{w}}'
        if foot is not None:
            yield ruler(foot, w, foot_align)

    def show_grid(self,
                  head: str|None='',
                  foot: str|None='',
                  head_align: Literal['<', '^', '>'] = '<',
                  foot_align: Literal['<', '^', '>'] = '<',
                  mark: Callable[[int, int], str] = lambda _x, _y: ' '):
        sz = self.size
        grid = self.grid
        w = 2 * (sz + 2)
        if head is not None:
            yield ruler(head, w, head_align)
        for y in range(sz):
            srow = ''.join(
                part
                for x in range(sz)
                for part in (
                    grid[sz * y + x] or '_',
                    mark(x, y)
                ))
            yield f'{srow: ^{w}}'
        if foot is not None:
            yield ruler(foot, w, foot_align)
        return w

    def select(self, ix: Iterable[int]):
        return self.Select(self, ix)

    @final
    class Select:
        def __init__(self, board: 'Board', ix: Iterable[int]):
            self.board = board
            self.ix = tuple(ix)
            for j, i in enumerate(self.ix):
                if not 0 <= i < len(self.board.grid):
                    raise IndexError(f'board ix[{j}] out of range')

        @property
        def letters(self):
            for i in self.ix:
                yield self.board.grid[i].upper()

        @property
        def pattern(self):
            return re.compile(re_counted(self.re_letters))

        @property
        def re_letters(self):
            dot: str = ''
            for let in self.letters:
                if let:
                    yield let.lower()
                elif not dot:
                    dot = self.board.re_letter
                    yield dot
                else:
                    yield dot

        @property
        def cursor(self):
            try:
                i = self.ix[0]
            except IndexError:
                return 'nil_cursor'

            sz = self.board.size
            y = i // sz
            x = i % sz

            try:
                j = self.ix[1]
            except IndexError:
                return f'{x},{y}'

            di = j - i
            orient = (
                'X' if di == 1 else
                'Y' if di == sz else
                '?')

            return f'{x},{y} {orient}+{len(self.ix)}'

        def updates(self, word: str, replace: bool = False):
            lc = Counter(self.board.letters)
            for i, a, b in zip(self.ix, word.upper(), self.letters):
                a, b = a.strip(), b.strip()
                if a == b: continue
                if b and not replace:
                    raise ValueError(f'cannot write {word!r} @<{self.cursor}>: {a} ≠ {b}')
                if lc[a] <= 0:
                    raise ValueError(f'cannot write {word!r} @<{self.cursor}>: {a} exhausted')
                yield i, a
                if a: lc[a] -= 1 # consume new letter
                if b: lc[b] += 1 # release any overwritten prior letter

        def nop_write(self, word: str) -> bool:
            return not any(self.updates(word))

        def can_write(self, word: str, replace: bool = False) -> bool:
            try:
                for _ in self.updates(word, replace=replace):
                    pass
                return True
            except ValueError:
                return False

        # def may_write(word: str) -> bool: TODO cross check

        def suggest(self, oracle: Callable[[re.Pattern[str]], Iterable[str]]):
            for word in oracle(self.pattern):
                if self.nop_write(word): continue
                if not self.can_write(word): continue
                yield word

        def possible(self,
            ui: PromptUI,
            oracle: Callable[[re.Pattern[str]], Iterable[str]],
        ):
            verbose = 0
            wsr = WordScorer(max(2, len(self.ix) - 2))
            chooser = Chooser()

            while ui.tokens:
                match = ui.tokens.have(r'-(v+)')
                if match:
                    verbose += len(match.group(1))
                    continue

                try:
                    if wsr.parse_option(ui.tokens):
                        continue
                    if chooser.collect(ui.tokens):
                        continue
                except ValueError as err:
                    ui.print(f'! {err}')
                    return

                n = ui.tokens.have(r'\d+', lambda match: int(match[0]))
                if n is not None:
                    if n > len(self.ix):
                        ui.print(f'! truncated {n} -> {len(self.ix)}')
                        n = len(self.ix)
                    wsr.ideal_len = n
                    continue

                ui.print(f'! invalid arg {next(ui.tokens)!r}')
                return

            return Possible(
                self.suggest(oracle),
                wsr.score,
                choices=chooser.choices,
                verbose=verbose)

@final
class WordScorer:
    def __init__(self,
                 ideal_len: int,
                 jitter: float = 0.5):
        self.ideal_len = ideal_len
        self.jitter = jitter

    def parse_option(self, tokens: PromptUI.Tokens):
        match = tokens.have(r'-r(?:and)?(\d*(?:\.\d+)?)')
        if match:
            arg = match[1] if match[1] else tokens.have(r'\d*(?\.\d+)?*', lambda match: match[0])
            if not arg:
                raise ValueError(f'missing -rand value')
            self.jitter = float(arg)
            return True

        match = tokens.have(r'-n(\d*)')
        if match:
            arg = match[1] if match[1] else tokens.have(r'\d*', lambda match: match[0])
            if not arg:
                raise ValueError(f'missing -n value')
            self.ideal_len = int(arg)
            return True

        return False

    def score(self, words: Sequence[str]):
        ws = self.Scores(words, self.ideal_len, self.jitter)
        return ws.scores, ws.explain

    @final
    class Scores:
        def __init__(self,
                     words: Sequence[str],
                     ideal_len: int,
                     jitter: float = 0.5):

            self.ideal_len = ideal_len

            wc = Counter(
                l
                for word in words
                for l in word)

            max_wc = max(wc.values(), default=1)
            self.rare = tuple(
                max(
                    1.0 - wc[l]/max_wc
                    for l in word)
                for word in words)

            self.mid = tuple(
                1.0 - abs(ideal_len - len(word))/ideal_len
                for word in words)

            self.scores = tuple(
                m * r
                for m, r in zip(self.mid, self.rare))

            self.rand = None
            if jitter:
                self.rand = RandScores(self.scores, jitter=jitter)
                self.scores = self.rand.scores

        def explain(self, i: int) -> Generator[str]:
            if self.rand: yield from self.rand.explain(i)
            yield f'*= mid: {100*self.mid[i]:.1f}%'
            yield f'*= rare: {100*self.rare[i]:.1f}%'

@final
class SpaceWord(StoredLog):
    log_file: str = 'spaceword.log'
    default_site: str = 'spaceword.org'
    default_wordlist: str = '/usr/share/dict/words'
    pub_tzname = 'US/Eastern'

    @override
    def add_args(self, parser: argparse.ArgumentParser):
        super().add_args(parser)
        _ = parser.add_argument('--wordlist')

    @override
    def from_args(self, args: argparse.Namespace):
        super().from_args(args)
        wordlist = cast(str, args.wordlist)
        if wordlist:
            self.wordlist_file = wordlist
            self.default_wordlist = wordlist

    def __init__(self):
        super().__init__()

        self.wordlist_file: str = ''
        self.given_wordlist: bool = False

        self.board = Board()
        self.result_text: str = ''
        self._result: Result|None = None

        self.num_letters: int = 0

        self.cursor: tuple[int, int, Literal['X', 'Y']] = (0, 0, 'X')

    def _parse_result(self):
        res = Result.parse(self.result_text)
        parts = self._id_parts()
        if parts:
            kind, d = parts
            if res.title != f'{kind.title()} {d:%Y-%m-%d}':
                raise ValueError( f'{res.title!r} != result title mismatch: "{kind.title()} {d:%Y-%m-%d}"')
        return res

    @property
    def result(self):
        if self._result is None and self.result_text:
            try:
                self._result = self._parse_result()
            except ValueError:
                return None
        return self._result

    @result.deleter
    def result(self):
        self._result = None

    @property
    @override
    def report_desc(self) -> str:
        def parts():
            res = self.result
            if not res:
                yield f'😦 incomplete {self.board.score}'
            else:
                yield f'🥳 {res.score} rank {res.rank[0]}'
            yield f'⏱️ {self.elapsed}'
        return ' '.join(parts())

    @property
    @override
    def report_body(self) -> Generator[str]:
        yield from super().report_body

        res = self.result
        if not res:
            used = sum(1
                for l in self.board.letters
                if not l)
            yield f'- tiles: {used}/{len(self.board.letters)}'
            yield f'- score: {self.board.score} bonus: {self.board.space_bonus:+}'

        else:
            yield f'- tiles: {res.tiles[0]}/{res.tiles[1]}'
            yield f'- score: {res.score} bonus: {res.bonus:+}'
            yield f'- rank: {res.rank[0]}/{res.rank[1]}'

        yield ''
        for line in self.board.show_grid(head=None, foot=None):
            yield f'    {line}'

    @override
    def load(self, ui: PromptUI, lines: Iterable[str]):
        for t, rest in super().load(ui, lines):
            orig_rest = rest
            with ui.exc_print(lambda: f'while loading {orig_rest!r}'):

                match = re.match(r'''(?x)
                    wordlist :
                    \s+
                    (?P<wordlist> [^\s]+ )
                    \s* ( .* )
                    $''', rest)
                if match:
                    wordlist, rest = match.groups()
                    assert rest == ''
                    self.wordlist_file = wordlist
                    self.given_wordlist = True
                    continue

                match = re.match(r'''(?x)
                    result :
                    \s* (?P<json> .+ )
                    $''', rest)
                if match:
                    (raw), = match.groups()
                    dat = cast(object, json.loads(raw))
                    assert isinstance(dat, str)
                    self.result_text = dat
                    continue

                match = re.match(r'''(?x)
                    num_letters :
                    \s+
                    (?P<n> \d+ )
                    $''', rest)
                if match:
                    self.set_num_letters(ui, int(match[1]))
                    continue

                match = re.match(r'''(?x)
                    letters :
                    \s+
                    \|
                    (?P<letters> .* )
                    \|
                    $''', rest)
                if match:
                    self.board.letters = list(match[1])
                    continue

                match = re.match(r'''(?x)
                    at :
                    \s+ (?P<x> \d+ )
                    \s+ (?P<y> \d+ )
                    \s+ (?P<dir> [xyXY] )
                    $''', rest)
                if match:
                    x = int(match[1])
                    y = int(match[2])
                    xy = cast(Literal['X', 'Y'], match[3].upper())
                    self.cursor = x, y , xy
                    continue

                match = re.match(r'''(?x)
                    change :
                    \s+ (?P<i> \d+ )
                    (?: \s+ (?P<let> [a-zA-Z] ) )?
                    ''', rest)
                if match:
                    i = int(match[1])
                    let = str(match[2] or '')
                    self.update(ui, ((i, let),))
                    continue

                yield t, rest

    @property
    def wordlist(self):
        return load_wordlist(self.wordlist_file)

    def set_num_letters(self, ui: PromptUI, n: int):
        ui.log(f'num_letters: {n}')
        self.num_letters = n

    @override
    def startup(self, ui: PromptUI):
        if not self.wordlist_file:
            with ui.input(f'📜 {self.default_wordlist} ? ') as tokens:
                self.wordlist_file = next(tokens, self.default_wordlist)
        if not self.given_wordlist:
            self.given_wordlist = True
            ui.log(f'wordlist: {self.wordlist_file}')

        if not self.puzzle_id:
            with ui.input(f'🧩 {self.puzzle_id} ? ') as tokens:
                match = re.match(r'''(?x)
                    (?P<kind> daily | weekly )
                    \s+
                    (?P<year> \d{4} )
                    (?: \s* | - )
                    (?P<month> \d{2} )
                    (?: \s* | - )
                    (?P<day> \d{2} )
                    ''', tokens.raw)
                if not match: return
                kind = str(match[1])
                y, m, d = int(match[2]), int(match[3]), int(match[4])
                if kind == 'weekly':
                    self.puzzle_id = f'{date(y, m, d+1):%Y-W%V}'
                else:
                    self.puzzle_id = f'{date(y, m, d):%Y-%m-%d}'
                ui.log(f'puzzle_id: {self.puzzle_id}')

        if not self.num_letters:
            dflt = (
                21 if self.kind == 'daily' else
                63 if self.kind == 'weekly' else
                None)
            with ui.input(
                    f'num letters (default: {dflt}) ? ' if dflt
                    else 'num letters? ') as tokens:
                n = tokens.have(r'\d+', lambda match: int(match[0])) or dflt
                if n is None: return
                self.set_num_letters(ui, n)

        if len(self.board.letters) != self.num_letters:
            return self.EditLetters(self.board, self.num_letters, self.play)

        return self.play

    def _id_parts(self) -> tuple[Literal['daily', 'weekly'], date] | None:
        match = re.match(r'''(?x)
            (?P<year> \d{4} ) - (?:
                (?P<month> \d{2} ) - (?P<day> \d{2} )
              | W (?P<week> \d{2} ) )
            ''', self.puzzle_id)
        if not match:
            return None

        y = int(match.group('year'))
        gw = cast(str|None, match.group('week'))
        if gw:
            dt = date.fromisocalendar(y, int(gw), 1)
            return 'weekly', dt - timedelta(days=1)

        gm = cast(str|None, match.group('month'))
        gd = cast(str|None, match.group('day'))
        if gm and gd:
            return 'daily', date(y, int(gm), int(gd))

    @property
    def kind(self) -> Literal['daily', 'weekly'] | None:
        parts = self._id_parts()
        if not parts:
            return None
        return parts[0]

    @property
    @override
    def today(self) -> date | None:
        parts = self._id_parts()
        if not parts:
            return None
        return parts[1]

    @property
    def pub_tz(self):
        if not self.pub_tzname:
            raise RuntimeError('no publish timezone set')
        tz = gettz(self.pub_tzname)
        if not tz:
            raise RuntimeError(f'unable to load publish timezone {self.pub_tzname}')
        return tz

    @property
    @override
    def expire(self) -> datetime|None:
        parts = self._id_parts()
        if not parts:
            return None
        kind, d = parts
        dt = timedelta(days=1 if kind == 'daily' else 7)
        return datetime.combine(d + dt, datetime.min.time(), self.pub_tz)

    @final
    class EditLetters:
        def __init__(self,
                     board: Board,
                     num: int,
                     ret: PromptUI.State,
                     ):
            self.board = board
            self.num = num
            self.ret = ret
            self.span = max(7, math.ceil(math.sqrt(self.num)))

        def __call__(self, ui: PromptUI):
            for line in self.board.show_letters(
                fill='?',
                head=f'{self.num} Letters',
                num=self.num,
                span=self.span,
            ): ui.print(line)

            sep = (
                '!' if len(self.board.letters) > self.num else
                '.' if len(self.board.letters) == self.num else
                '?')
            with ui.input(f'letters{sep} ') as tokens:
                if tokens.empty:
                    if sep == '.': return self.ret

                elif tokens.under('/span'):
                    n = ui.tokens.have(r'\d+', lambda match: int(match[0]))
                    if n is None:
                        ui.print(f'- span: {self.span}')
                    else:
                        self.span = n
                        ui.print(f'- set span: {self.span}')

                elif tokens.have('/clear'):
                    self.board.letters = []
                    ui.log(f'letters: |{"".join(self.board.letters)}|')
                    ui.print('- cleared letters')

                elif tokens.have('/back'):
                    i = (len(self.board.letters) // self.span) * self.span
                    if i < len(self.board.letters):
                        self.board.letters = self.board.letters[:i]
                        ui.log(f'letters: |{"".join(self.board.letters)}|')
                        ui.print(f'- truncated letters :{i}')

                else:
                    addlet = [
                        let
                        for token in tokens
                        for let in token.strip().upper()]
                    self.board.letters.extend(addlet)
                    ui.log(f'letters: |{"".join(self.board.letters)}|')
                    ui.print(f'- added letters: {" ".join(addlet)}')

    def play(self, ui: PromptUI):
        for line in self.board.show(
            head=f'<{self.cursor[0]} {self.cursor[1]} {self.cursor[2]}>',
            mid=f'[score: {self.board.score}]', mid_align='>',
            mark=lambda x, y: '@' if self.cursor[0] == x and self.cursor[1] == y else ' ',
        ): ui.print(line)
        def prompt_parts():
            sc = self.board.score
            res = self.result
            if res:
                yield f'prior:{res.score}'
                if sc > res.score:
                    yield f'bet:{sc}'
            else:
                yield f'cur:{sc}'

        with ui.input(f'[{' '.join(prompt_parts())}]> '):
            return self.handle_play(ui)

    def handle_play(self, ui: PromptUI):
        if not ui.tokens:
            return

        if ui.tokens.have(r'/res(ult)?'):
            ui.print('Provide share result:')
            self.result_text = ui.may_paste()
            del self.result
            try:
                _ = self._parse_result()
            except ValueError as err:
                ui.print(f'! {err}')
            else:
                ui.log(f'result: {json.dumps(self.result_text)}')
            return

        if ui.tokens.have(r'/st(ore)?'):
            return self.store

        if ui.tokens.have(r'/let(ters)?'):
            return self.EditLetters(self.board, self.num_letters, self.play)

        if ui.tokens.have(r'/cl(ear)?'):
            self.update(ui, (
                (i, '')
                for i, let in enumerate(self.board.grid)
                if let))
            ui.print('cleared board')
            return

        if ui.tokens.under(r'\*'):
            return self.generate(ui)

        if ui.tokens.under(r'@'):
            x = ui.tokens.have(r'\d+', lambda match: int(match[0]))
            y = ui.tokens.have(r'\d+', lambda match: int(match[0]))
            xy = cast(Literal['X', 'Y']|None, ui.tokens.have(
                r'([xXrRhH])|([yYdDvV])',
                lambda match: 'Y' if match[2] else 'X')
            )
            if x is None and y is None and xy is None:
                ui.print('! usage: @ x')
                ui.print('       : @ x y')
                ui.print('       : @ x y X|Y')
                ui.print('       : @ X|Y')
            else:
                if x is None: x = self.cursor[0]
                if y is None: y = self.cursor[1]
                if xy is None: xy = self.cursor[2]
                self.move_to(ui, x, y, xy)
            return

        match = ui.tokens.have(r'\^([a-zA-Z]*)')
        if match:
            word = ''.join(
                let
                for part in chain(
                    str(match[1]),
                    ui.tokens.consume(r'[a-zA-Z]+', lambda match: str(match[0])))
                for let in part
            ).upper()

            sel = self.board.select(self.iter_curosr())
            if len(word) > len(sel.ix):
                ui.print(f'! cannot write {word!r} @ {self.cursor}: not enough space')
                return

            try:
                for _ in sel.updates(word): pass
            except ValueError as err:
                ui.print(f'! {err}')
                return

            ui.print(f'- writing {word!r} @ {sel.cursor}')
            self.update(ui, sel.updates(word))
            return

        erase_n = ui.tokens.have(
            r'(?x) ( \d* ) _ | _ ( \d* )', lambda match:
                int(match[1]) if match[1] else
                int(match[2]) if match[2] else
                1)
        if erase_n is not None:
            self.erase_at(ui, erase_n)
            return

        ui.print(f'! unknown input {ui.tokens.rest!r}')

    def move_to(self, ui: PromptUI, x: int, y: int, xy: Literal['X', 'Y'] = 'X'):
        self.cursor = x, y, xy
        ui.log(f'at: {x} {y} {xy}')

    def iter_curosr(self):
        x, y, xy = self.cursor
        if xy == 'X': return self.board.x_cursor(x, y)
        else:         return self.board.y_cursor(x, y)

    def erase_at(self, ui: PromptUI, erase_n: int):
        ic = tuple(self.iter_curosr())
        prior = tuple(self.board.grid[i] for i in ic)

        changes = tuple(
            (i, '')
            for i, l in zip(ic, prior[:erase_n])
            if l)
        if not changes:
            ui.print(f'- noop erase {erase_n} @ {self.cursor}')
            return

        lets = tuple(self.board.grid[i] for i, _ in changes)
        ui.print(f'- erasing @ {self.cursor} -- {' '.join(lets)}')
        self.update(ui, changes)

    def update(self, ui: PromptUI, changes: Iterable[tuple[int, str]]):
        for i, let in changes:
            self.board.update(i, let)
            ui.log(f'change: {i} {let}')

    def generate(self, ui: PromptUI):
        sel = self.board.select(self.iter_curosr())
        pos = sel.possible(ui, lambda pat: grep(self.wordlist.words, pat, anchor='full'))
        if not pos: return

        def interact(ui: PromptUI):
            ui.print(f'{pos} to write @{sel.cursor}')
            for line in pos.show_list():
                ui.print(line)
            with (
                ui.catch_state(EOFError, self.play),
                ui.input(f'try? ')):
                n = ui.tokens.have(r'(\d+)', lambda match: int(match[1]))
                if n is None: return
                try:
                    word = pos.data[pos.get(n)]
                except IndexError as err:
                    ui.print(f'! invalid *-list reference: {err}')
                    return
                ui.print(f'- writing {word!r} @ {sel.cursor}')
                self.update(ui, sel.updates(word))
                return self.play

        return interact

@dataclass
class Result:
    title: str
    url: str
    score: int
    rank: tuple[int, int]
    tiles: tuple[int, int]
    bonus: int

    @classmethod
    def parse(cls, s: str):
        title = ''
        url = ''
        score = 0
        rank = (0, 0)
        tiles = (0, 0)
        bonus = 0

        for line in spliterate(s, '\n', trim=True):

            match = re.match(r'''(?x)
                ✨
                \s* Spaceword.org
                \s* ( .+? ) \s*
                ✨
                ''', line)
            if match:
                title = match[1]
                continue

            match = re.match(r'''(?x)
                Play
                \s+
                at
                \s+
                ( .+ )
                ''', line)
            if match:
                url = match[1]
                continue

            match = re.match(r'''(?x)
                🏆
                \s*
                Score:
                \s*
                ( \d+ )
                ''', line)
            if match:
                score = int(match[1])
                continue

            match = re.match(r'''(?x)
                🏅
                \s*
                Rank:
                \s*
                ( \d+ ) \s* / \s* ( \d+ )
                ''', line)
            if match:
                rank = int(match[1]), int(match[2])
                continue

            match = re.match(r'''(?x)
                🧩
                \s*
                Tiles:
                \s*
                ( \d+ ) \s* / \s* ( \d+ )
                \s*
                ✅
                ''', line)
            if match:
                tiles = int(match[1]), int(match[2])
                continue

            match = re.match(r'''(?x)
                📏
                \s*
                Space
                \s*
                Bonus:
                \s*
                [+-]? ( \d+ )

                ''', line)
            if match:
                bonus = int(match[1])
                continue

        if not title: raise ValueError('missing spaceword result title')
        return cls(title, url, score, rank, tiles, bonus)

@MarkedSpec.mark('''

    #first_solve
    > ✨ Spaceword.org Daily 2025-04-25 ✨
    > 
    > 🏆 Score: 2158
    > 🏅 Rank: 165/322 😀
    > 🧩 Tiles: 21/21 ✅
    > 📏 Space Bonus: +58
    > 
    > 
    > Play at https://spaceword.org
    > #spaceword
    - title: Daily 2025-04-25
    - score: 2158
    - rank: (165, 322)
    - tiles: (21, 21)
    - bonus: 58

''')
def test_parse_result(spec: MarkedSpec):
    res = Result.parse(spec.input)
    for key, value in spec.props:
        if key == 'title': assert res.title == value
        elif key == 'score': assert f'{res.score}' == value
        elif key == 'rank': assert f'{res.rank}' == value
        elif key == 'tiles': assert f'{res.tiles}' == value
        elif key == 'bonus': assert f'{res.bonus}' == value

if __name__ == '__main__':
    SpaceWord.main()
