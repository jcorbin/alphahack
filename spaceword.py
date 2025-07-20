#!/usr/bin/env python

import argparse
import hashlib
import math
import json
import pytest
import re
from collections import Counter, OrderedDict
from collections.abc import Generator, Iterable, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from dateutil.tz import gettz
from itertools import batched, chain, combinations, islice, repeat
from typing import Callable, Literal, Never, Self, cast, final, override

flatten = chain.from_iterable

from sortem import Chooser, MatchPat, Possible, Sample, RandScores, match_show, numbered_item, wrap_item
from store import StoredLog, git_txn
from strkit import MarkedSpec, block_lines, spliterate

from ui import PromptUI
from wordlist import WordList

PlainEntry = tuple[str, 'PlainValue']
PlainData = tuple[PlainEntry, ...]
PlainVal = str|float|int
PlainVals = tuple[str, ...]|tuple[float, ...]|tuple[int, ...]|tuple['PlainVals', ...]
PlainValue = PlainData|PlainVals|PlainVal

def plain_get(dat: PlainData, key: str):
    for k, v in dat:
        if k == key:
            return v

def plain_dictify(dat: PlainData):
    def entries():
        for k, v in dat: yield k, (
            dict(cast(PlainData, v)) if (
                isinstance(v, tuple) and
                all(isinstance(vv, tuple) and len(vv) == 2 for vv in v)
            ) else v)
    return dict(entries())

def plain_chain_matcher(*matchers: Callable[[PlainData], bool]|None) -> Callable[[PlainData], bool]:
    matchers = tuple(m for m in matchers if m is not None)
    if len(matchers) == 0:
        return lambda _: True
    if len(matchers) == 1:
        return matchers[0]
    return lambda dat: all(m(dat) for m in matchers)

def plain_make_matcher(field: str, spat: str):
    pat = re.compile(spat)
    def field_pat_where(dat: PlainData):
        val = plain_get(dat, field)
        if val is None: return False
        return bool(pat.search(val if isinstance(val, str) else repr(val)))
    return field_pat_where

def plain_describe(
    sample: Iterable[float],
    qs: tuple[float, ...]=(0.75, 0.5, 0.25),
) -> Generator[PlainEntry]:
    S = sorted(sample)

    N = len(S)
    yield 'N', N

    if not N: return
    yield 'μ', sum(S) / N

    if N < 2: return
    yield '⊥', min(S)

    n = N - 1
    for q in qs:
        qi = q * n
        i = math.floor(qi)
        j = math.ceil(qi)
        if i == 0 or j == n: continue
        yield f'Q{100*q}', S[i] if i == j else (S[i] + S[j])/2

    yield '⊤', max(S)

def nope(_arg: Never, mess: str =  'inconceivable'):
    assert False, mess

def isurround(pre: str, parts: Iterable[str], post: str):
    any_part = False
    for part in parts:
        if not any_part:
            any_part = True
            yield pre
        yield part
    if any_part:
        yield post

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

def simplify(
    changes: Iterable[tuple[int, str]],
    grid: Sequence[str],
    letters: Sequence[str],
) -> Generator[tuple[int, str]]:
    od: OrderedDict[int, str] = OrderedDict()
    for i, let in changes:
        od[i] = let

    avail = Counter(let for let in letters if let)
    pending = list(od.items())

    while pending:
        for j, (i, let) in enumerate(pending):
            if avail[let] <= 0:
                yield from pending[:j]
                break
            prior = grid[i]
            avail[let] -= 1
            if prior: avail[prior] += 1
        else: break

        pending = pending[j:]

        need = let
        reuse_j = next((
            j
            for j, (i, _) in enumerate(pending)
            if grid[i] == need
        ), None)
        if reuse_j is None:
            raise ValueError('invalid changes')

        i, dep = pending[reuse_j]
        if avail[dep] <= 0:
            yield i, ''
        else:
            yield pending.pop(reuse_j)
            avail[dep] -= 1
        avail[need] += 1

    yield from pending

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

def re_letter(lets: Iterable[str]):
    lets = (l.strip() for l in lets)
    s = ''.join(sorted(l for l in set(lets) if l))
    return f'[{s.lower()}]' if s else '\\0'

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

def test_board_copy():
    board = Board(letters=sorted('helloworld'.upper()))
    assert list(board.show()) == [
        '------------------------',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '------------------------',
        '     D E H L L L O      ',
        '     O R W _ _ _ _      ',
        '------------------------']

    board.update(board.select(board.cursor(2, 2, 'X')).updates('hello'))

    assert list(board.show()) == [
        '------------------------',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ H E L L O _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '------------------------',
        '     D         L        ',
        '     O R W _ _ _ _      ',
        '------------------------']

    other = board.copy(
        board.select(board.cursor(6, 1, 'Y')).updates('world'.upper()))

    assert list(other.show()) == [
        '------------------------',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ W _ _ _   ',
        '  _ _ H E L L O _ _ _   ',
        '  _ _ _ _ _ _ R _ _ _   ',
        '  _ _ _ _ _ _ L _ _ _   ',
        '  _ _ _ _ _ _ D _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '------------------------',
        '                        ',
        '     O     _ _ _ _      ',
        '------------------------']

    assert list(board.show()) == [
        '------------------------',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ H E L L O _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '------------------------',
        '     D         L        ',
        '     O R W _ _ _ _      ',
        '------------------------']

def parse_test_board(s: str):
    lines = list(block_lines(s))
    rows = tuple(
        tuple(b[0] for b in batched(line, 2))
        for line in lines)
    sz = len(rows[0])
    assert all(len(row) == sz for row in rows)
    return Board(size=sz,
        grid = tuple(
            '' if let == '_' else let.upper()
            for row in rows[:sz]
            for let in row),
        letters = tuple(
            '' if let == '_' else let.upper()
            for row in rows[sz:]
            for let in row))

@pytest.mark.parametrize('a, b, expect', [
    pytest.param(
        '''
        _ _ _
        C A T
        _ _ _
        _ _ _
        I E Z
        ''',

        '''
        _ _ _
        A T C
        _ _ _
        ''',

        '''
        4 _
        3 A
        5 C
        4 T
        ''',

        id='cat_atc'),
])
def test_board_diff(a: str, b: str, expect: str):
    ba = parse_test_board(a)
    bb = parse_test_board(b)
    assert list(
        f'{i} {let or "_"}'
        for i, let in ba.diff(bb)
    ) == list(block_lines(expect))

@final
class Board:
    def __init__(self,
                 size: int = 10,
                 letters: Iterable[str] = (),
                 grid: Iterable[str] = ()):
        self.size = size
        self.letters: list[str] = [let.upper() for let in letters]
        self.grid: list[str] = [''] * self.size**2
        for i, l in enumerate(grid):
            if i < len(self.grid):
                self.grid[i] = l

    def to_bone(self):
        dat = ''.join(
            let or ' '
            for let in chain(self.grid, self.letters))
        return f'{self.size}:{dat}'

    @classmethod
    def from_bone(cls, s: str):
        m = re.match(r'(\d+):(.+)', s)
        if not m:
            raise ValueError('invalid bone string')
        size = int(m[1])
        s = m[2]
        n = size * size
        l = tuple(let.strip() for let in s)
        return cls(size, grid=l[:n], letters=l[n:])

    def load_line(self, line: str):
        match = re.match(r'''(?x)
            letters :
            \s+
            \|
            (?P<letters> .* )
            \|
            $''', line)
        if match:
            self.letters = list(match[1])
            return True

        match = re.match(r'''(?x)
            change :
            \s+ (?P<i> \d+ )
            (?: \s+ (?P<let> [a-zA-Z] ) )?
            ''', line)
        if match:
            i = int(match[1])
            let = str(match[2] or '')
            self.set(i, let)
            return True

        return False

    def copy(self, updates: Iterable[tuple[int, str]] = ()):
        b = Board(self.size, self.letters, self.grid)
        for ilet in updates: b.set(*ilet)
        return b

    def shift(self, dx: int, dy: int) -> Generator[tuple[int, str]]:
        if dx == 0 and dy == 0:
            return
        sz = self.size
        ix = tuple(self.ix_defined())
        jx = tuple(
            (y + dy)*sz + (x + dx)
            for _, x, y in self.ix_defined())
        ls = tuple(self.grid[i] for i, _, _ in ix)
        def updates():
            for i, _, _ in ix:
                yield i, ''
            for j, l in zip(jx, ls):
                if 0 <= j < len(self.grid):
                    yield j, l
        yield from simplify(updates(), self.grid, self.letters)

    def diff(self, other: 'Board') -> Generator[tuple[int, str]]:
        if self.size != other.size:
            raise ValueError(f'board size mismatch mine:{self.size} vs theirs:{other.size}')
        def updates():
            for i, (a, b) in enumerate(zip(self.grid, other.grid)):
                if a and a != b:
                    # TODO could narrow down to "only if needed for reuse"
                    yield i, ''
            for i, (a, b) in enumerate(zip(self.grid, other.grid)):
                if b and a != b: yield i, b
        yield from simplify(updates(), self.grid, self.letters)

    def seeds(self):
        bounds = self.defined_rect
        if not bounds:
            # TODO just straight up mid?
            sz = self.size
            at = sz // 5
            yield self.cursor(at, at, 'X')
            yield self.cursor(at, at, 'Y')
        else:
            lo_x, lo_y, hi_x, hi_y = bounds
            for y in range(lo_y, hi_y):
                yield self.cursor(lo_x, y, 'X')
            for x in range(lo_x, hi_x):
                yield self.cursor(x, lo_y, 'Y')

    @property
    def re_letter_avail(self):
        return re_letter(self.letters)

    @property
    def re_letter_all(self):
        return re_letter(chain(self.letters, self.grid))

    @property
    def all_pattern(self):
        return re.compile(f'{self.re_letter_all}{{2,{self.size}}}')

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
        return self.per_let*self.used_letters + self.space_bonus

    @property
    def used_letters(self):
        return sum(
            1
            for let in self.letters
            if not let)

    @property
    def free_letters(self):
        return len(self.letters) - self.used_letters

    @property
    def done(self):
        return self.free_letters <= 0

    @property
    def max_score(self):
        return self.per_let*len(self.letters) + self.max_bonus

    @property
    def defined_area(self):
        bounds = self.defined_rect
        if not bounds:
            return 0
        x1, y1, x2, y2 = bounds
        w = abs(x2 - x1)
        h = abs(y2 - y1)
        return w*h

    @property
    def max_area(self):
        return self.size**2

    @property
    def space_bonus(self):
        return self.max_area - self.defined_area

    @property
    def max_bonus(self):
        return self.size**2

    def update(self, changes: Iterable[tuple[int, str]]):
        for i, let in changes:
            self.set(i, let)

    def set(self, i: int, let: str):
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

    def cursor(self, x: int, y: int, axis: Literal['X', 'Y']):
        return self.Cursor(x, y, axis, self.size, len(self.grid))

    def all_words(self):
        bounds = self.defined_rect
        if bounds:
            lo_x, lo_y, hi_x, hi_y = bounds
            for cur in chain(
                (self.cursor(lo_x, y, 'X') for y in range(lo_y, hi_y)),
                (self.cursor(x, lo_y, 'Y') for x in range(lo_x, hi_x)),
            ):
                for token in self.select(cur).tokens():
                    if len(token) > 1:
                        yield token

    def word_affixes(self) -> Generator['Select']:
        all_words = tuple(self.all_words())
        word_count = Counter(
            i
            for token in all_words
            for i in token.ix)
        cixs = tuple(
            tuple(word_count[i] for i in token.ix)
            for token in all_words)
        heads = tuple(cix[0] for cix in cixs)
        tails = tuple(cix[-1] for cix in cixs)
        want = min(min(heads), min(tails))

        def extract(i: int):
            token = all_words[i]
            cix = cixs[i]
            i = 0
            if cix[i] == want:
                while cix[i] == want:
                    i += 1
                    if i == len(cix): return
                yield token.slice(i)
            i = -1
            if cix[i] == want:
                while cix[i] == want: i -= 1
                yield token.slice(i+1, len(token))

        for i in range(len(all_words)):
            yield from extract(i)

    @final
    class Cursor:
        def __init__(self, x: int, y: int, axis: Literal['X', 'Y'], size: int, max: int):
            self.x = x
            self.y = y
            self.axis: Literal['X', 'Y'] = axis
            self.size = size
            self.max = max

        @override
        def __str__(self):
            if self.size == 0 or self.max == 0:
                return 'nil_cursor'
            return f'{self.x},{self.y}+{self.axis}'

        def range(self):
            x = self.x
            y = self.y
            axis = self.axis
            sz = self.size
            if axis == 'X':
                return range(y*sz + x, (y+1)*sz)
            elif axis == 'Y':
                return range(y*sz + x, self.max, sz)
            else:
                return range(0)

        def __iter__(self):
            return iter(self.range())

        def pre(self):
            cls = self.__class__
            if self.axis == 'X':
                for x in range(0, self.x):
                    yield cls(x, self.y, self.axis, self.size, self.max)
            elif self.axis == 'Y':
                for y in range(0, self.y):
                    yield cls(self.x, y, self.axis, self.size, self.max)

    def show(self,
             head: str|None = '',
             mid: str|None = '',
             foot: str|None = '',
             head_align: Literal['<', '^', '>'] = '<',
             mid_align: Literal['<', '^', '>'] = '<',
             foot_align: Literal['<', '^', '>'] = '<',
             mark: Callable[[int, int, int], str] = lambda _x, _y, _i: ' '
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
                  cell: Callable[[int, int, int], str] | None = None,
                  mark: Callable[[int, int, int], str] = lambda _x, _y, _i: ' ',
                  ):
        if cell is None:
            grid = self.grid
            cell = lambda x, y, i: grid[i] or '_'
        sz = self.size
        w = 2 * (sz + 2)
        if head is not None:
            yield ruler(head, w, head_align)
        for y in range(sz):
            srow = ''.join(
                part
                for x in range(sz)
                for i in (sz * y + x,)
                for part in (
                    cell(x, y, i),
                    mark(x, y, i)
                ))
            yield f'{srow: ^{w}}'
        if foot is not None:
            yield ruler(foot, w, foot_align)
        return w

    def select(self, ix: Iterable[int]):
        for j, i in enumerate(ix):
            if not 0 <= i < len(self.grid):
                raise IndexError(f'board ix[{j}] out of range')
        return self.Select(self, ix)

    @final
    class Select:
        def __init__(self, board: 'Board', ix: Iterable[int]):
            self.board = board
            self.ix = tuple(ix)

        def __len__(self):
            return len(self.ix)

        def __iter__(self):
            for i in self.ix:
                yield self.board.grid[i]

        @override
        def __str__(self):
            return ''.join(self).lower()

        def iter_xy(self):
            sz = self.board.size
            for i in self.ix:
                y = i // sz
                x = i % sz
                yield x, y, i

        @property
        def letters(self):
            for let in self:
                yield let.upper()

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
                    dot = self.board.re_letter_avail
                    yield dot
                else:
                    yield dot

        @property
        def cursor(self):
            try:
                i = self.ix[0]
            except IndexError:
                return Board.Cursor(0, 0, 'X', 0, 0)
            sz = self.board.size
            mx = max(self.ix)
            dmx = mx - i
            y = i // sz
            x = i % sz
            return Board.Cursor(x, y, 'Y' if (dmx % sz) == 0 else 'X', sz, mx+1)

        def index(self,
                  where: Callable[[str, int], bool] = lambda c, _i: bool(c),
                  start: int = 0):
            for i in iter(range(start, len(self.ix))):
                c = self.board.grid[self.ix[i]]
                if where(c, i): return i
            return -1

        def slice(self, start: int, end: int|None = None) -> Self:
            if end is None:
                start, end = 0, start
            return self.__class__(self.board, self.ix[start:end])

        def token_ranges(self):
            i = 0
            n = len(self.ix)
            while i < n:
                i = self.index(lambda c, _i: bool(c), i)
                if i < 0: break
                j = self.index(lambda c, _i: not c, i)
                if j < 0:
                    yield i, n
                    break
                yield i, j
                i = j + 1

        def tokens(self):
            cls = self.__class__
            for i, j in self.token_ranges():
                yield cls(self.board, self.ix[i:j])

        def expand(self, max: int|None = None):
            cur = self.cursor
            cur.max = max or len(self.board.grid)
            return self.board.select(cur)

        def continuations(self):
            may = self.expand()
            i = len(self)
            while True:
                j = may.index(lambda c, _i: bool(c), start=i)
                if j - i < 2: break
                for k in range(i+1, j-1):
                    yield may.slice(k)
                i = j+1
            yield may

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

def test_board_bones():
    board = Board(letters='bdehlllmooorw')
    board.update(board.select(board.cursor(3, 3, 'X')).updates('hello'))
    board.update(board.select(board.cursor(7, 2, 'Y')).updates('world'))

    assert list(board.show()) == [
        '------------------------',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ W _ _   ',
        '  _ _ _ H E L L O _ _   ',
        '  _ _ _ _ _ _ _ R _ _   ',
        '  _ _ _ _ _ _ _ L _ _   ',
        '  _ _ _ _ _ _ _ D _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '------------------------',
        '     B                  ',
        '     M   O O     _      ',
        '------------------------']

    bone = board.to_bone()
    assert bone == ''.join((
        '10:',
        '          ',
        '          ',
        '       W  ',
        '   HELLO  ',
        '       R  ',
        '       L  ',
        '       D  ',
        '          ',
        '          ',
        '          ',
        'B      M OO  '))

    reboard = Board.from_bone(bone)
    assert list(reboard.show()) == [
        '------------------------',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ W _ _   ',
        '  _ _ _ H E L L O _ _   ',
        '  _ _ _ _ _ _ _ R _ _   ',
        '  _ _ _ _ _ _ _ L _ _   ',
        '  _ _ _ _ _ _ _ D _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '  _ _ _ _ _ _ _ _ _ _   ',
        '------------------------',
        '     B                  ',
        '     M   O O     _      ',
        '------------------------']

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
        self.best: Board|None = None
        self.result_text: str = ''
        self._result: Result|None = None

        self.sids: set[str] = set()
        self.last_sid: str = ''

        self.num_letters: int = 0

        self.at_cursor: tuple[int, int, Literal['X', 'Y']] = (0, 0, 'X')

        self.play = PromptUI.Prompt(self.prompt_mess, {
            '/at': self.cmd_at,
            '/bad': self.cmd_bad,
            '/center': self.cmd_center,
            '/centre': '/center',
            '/clear': self.cmd_clear,
            '/erase': self.cmd_erase,
            '/generate': self.cmd_generate,
            '/letters': self.cmd_letters,
            '/priors': self.cmd_priors,
            '/rejects': self.cmd_rejects,
            '/result': self.cmd_result,
            '/search': self.cmd_search,
            '/shift': self.cmd_shift,
            '/store': self.cmd_store,
            '/write': self.cmd_write,

            '@': '/at', # TODO wants to be an under... prefix
            '_': '/erase', # TODO wants to match r'(?x) ( \d* ) _ | _ ( \d* )'
            '*': '/generate',
            '~': '/search',
            '^': '/write', # TODO wants to be an under... prefix
        })

    def make_sid(self, hash: str):
        n = 6
        while hash[:n] in self.sids and n < len(hash):
            n += 1
        sid = hash[:n]
        self.sids.add(sid)
        return sid

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

    @override
    def have_result(self):
        return self.result is not None

    @override
    def fin_result(self):
        res = self.result
        return res is not None and res.final

    @override
    def proc_result(self, ui: PromptUI, text: str):
        self.result_text = text
        del self.result
        res = self._parse_result()
        ui.log(f'result: {json.dumps(self.result_text)}')
        if res.score == self.board.score:
            self.best = self.board.copy()

    @property
    @override
    def report_desc(self) -> str:
        def parts():
            res = self.result
            if not res:
                yield f'😦 incomplete score {self.board.score}'
            else:
                r1, r2 = res.rank
                if res.final:
                    yield f'🏁 score {res.score} ranked {100*r1/r2:.1f}% {r1}/{r2}'
                else:
                    yield f'🏗️ score {res.score} current ranking {r1}/{r2}'

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

    def prior_result_boards(self):
        board = Board(self.board.size)
        for _n, _t, _z, line in self.parse_log():
            if board.load_line(line):
                # TODO maybe examine intermediate boards
                continue
            if re.match(r'(?x) result :', line):
                yield board

    def prior_reject_bones(self):
        for _n, _t, _z, line in self.parse_log():
            match = re.match(r'''(?x)
                reject
                \s+
                sid : (?P<sid> [^\s]+ )
                \s+
                bone : (?P<bone> .* )
                $''', line)
            if match:
                sid = match[1]
                bone = match[2]
                yield sid, bone

    def prior_reject_sids(self):
        for sid, _ in self.prior_reject_bones():
            yield sid

    def prior_reject_boards(self, sid: str=''):
        for s, bone in self.prior_reject_bones():
            if not sid or s == sid:
                try:
                    board = Board.from_bone(bone)
                except ValueError:
                    pass
                else:
                    yield board

    def browse_reject_boards(self):
        def bind(sid: str):
            return lambda: self.prior_reject_boards(sid)

        seen: set[str] = set()
        for sid, _ in self.prior_reject_bones():
            if sid not in seen:
                seen.add(sid)
                yield sid, bind(sid)
        yield 'all', lambda: self.prior_reject_boards()

    @override
    def load(self, ui: PromptUI, lines: Iterable[str]):
        for t, rest in super().load(ui, lines):
            orig_rest = rest
            with ui.exc_print(lambda: f'while loading {orig_rest!r}'):
                if self.board.load_line(rest):
                    continue

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
                    try:
                        self.proc_result(ui, dat)
                    except:
                        pass
                    continue

                match = re.match(r'''(?x)
                    reject
                    \s+
                    sid : (?P<sid> [^\s]+ )
                    \s+
                    bone : (?P<bone> .* )
                    $''', rest)
                if match:
                    self.sids.add(match[1])
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
                    at :
                    \s+ (?P<x> \d+ )
                    \s+ (?P<y> \d+ )
                    \s+ (?P<dir> [xyXY] )
                    $''', rest)
                if match:
                    x = int(match[1])
                    y = int(match[2])
                    xy = cast(Literal['X', 'Y'], match[3].upper())
                    self.at_cursor = x, y , xy
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

    @override
    def expired_prompt_mess(self, _ui: PromptUI):
        return f'[f]inalize, [a]rchive, [r]emove, or [c]ontinue? '

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
    class EditLetters(PromptUI.Prompt):
        def __init__(self,
                     board: Board,
                     num: int,
                     ret: PromptUI.State,
                     ):
            self.board = board
            self.num = num
            self.ret = ret
            self.span = max(7, math.ceil(math.sqrt(self.num)))
            super().__init__(self.show_prompt, {
                '/back': self.do_back,
                '/clear': self.do_clear,
                '/span': self.do_span,
                '': self.do_letters,
            })

        def show_prompt(self, ui: PromptUI):
            for line in self.board.show_letters(
                fill='?',
                head=f'{self.num} Letters',
                num=self.num,
                span=self.span,
            ): ui.print(line)
            return f'letters{self.sigil} '

        @property
        def sigil(self):
            return (
                '!' if len(self.board.letters) > self.num else
                '.' if len(self.board.letters) == self.num else
                '?')

        def do_back(self, ui: PromptUI):
            '''
            erase last row
            '''
            i = (len(self.board.letters) // self.span) * self.span
            if i < len(self.board.letters):
                self.board.letters = self.board.letters[:i]
                ui.log(f'letters: |{"".join(self.board.letters)}|')
                ui.print(f'- truncated letters :{i}')

        def do_clear(self, ui: PromptUI):
            '''
            clear all rows
            '''
            self.board.letters = []
            ui.log(f'letters: |{"".join(self.board.letters)}|')
            ui.print('- cleared letters')

        def do_letters(self, ui: PromptUI):
            if ui.tokens.empty:
                if self.sigil == '.': return self.ret
            else:
                addlet = [
                    let
                    for token in ui.tokens
                    for let in token.strip().upper()]
                self.board.letters.extend(addlet)
                ui.log(f'letters: |{"".join(self.board.letters)}|')
                ui.print(f'- added letters: {" ".join(addlet)}')

        def do_span(self, ui: PromptUI):
            '''
            show/change row span
            '''
            n = ui.tokens.have(r'\d+', lambda match: int(match[0]))
            if n is None:
                ui.print(f'- span: {self.span}')
            else:
                self.span = n
                ui.print(f'- set span: {self.span}')

    def show_board(self, board: Board) -> Generator[str]:
        yield from board.show(
            head=f'<{self.at_cursor[0]} {self.at_cursor[1]} {self.at_cursor[2]}>',
            mid=f'[score: {board.score}]', mid_align='>',
            mark=lambda x, y, i: '@' if self.at_cursor[0] == x and self.at_cursor[1] == y else ' ',)

        wordset = self.wordlist.uniq_words
        good_words: list[str] = []
        bad_words: list[tuple[str, Board.Cursor]] = []
        for word in board.all_words():
            w = str(word)
            if w in wordset: good_words.append(w)
            else: bad_words.append((w, word.cursor))
        if good_words:
            yield f'* Good Words: {" ".join(good_words)}'
        if bad_words:
            yield f'* Bad Words:'
            for word, cur in bad_words:
                yield f'  - @{cur} {word}'

    def prompt_mess(self, ui: PromptUI):
        for line in self.show_board(self.board):
            ui.print(line)
        return f'[{' '.join(self.prompt_parts())}]> '

    def prompt_parts(self):
        sc = self.board.score
        res = self.result
        prior = (
            self.best.score if self.best is not None else
            res.score if res is not None else
            0)
        if prior:
            yield f'prior:{prior}'
            if sc > prior:
                yield f'bet:{sc}'
            elif sc != prior:
                yield f'meh:{sc}'
        else:
            yield f'doit:{sc}'

    def cmd_at(self, ui: PromptUI):
        '''
        move editor cursor; usage `/at <X> [<Y>] [X|Y]`
        '''
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
            if x is None: x = self.at_cursor[0]
            if y is None: y = self.at_cursor[1]
            if xy is None: xy = self.at_cursor[2]
            self.move_to(ui, x, y, xy)

    def cmd_bad(self, ui: PromptUI):
        '''
        remove one or more words from the list; usage `/bad <word> [<word> ...]`
        '''
        words = tuple(
            word.lower()
            for word in ui.tokens)
        if not words:
            ui.print('usage: /bad <word> [<word> ...]')
            return

        known = self.wordlist.uniq_words
        words = tuple(
            word
            for word in words
            if word in known)
        if not words:
            ui.print('no known words given')
            return

        with git_txn(f'{self.site} bad {"words" if len(words) > 1 else "word"}', ui=ui) as txn:
            with txn.will_add(self.wordlist.exclude_file):
                self.wordlist.remove_words(words)

    def cmd_center(self, ui: PromptUI):
        '''
        recenter the board
        '''
        bounds = self.board.defined_rect
        if not bounds:
            ui.print('empty board, what even is center')
            return

        x1, y1, x2, y2 = bounds
        h = self.board.size//2
        cx, cy = math.floor(x1/2 + x2/2), math.floor(y1/2 + y2/2)
        if cx == h and cy == h:
            ui.print('board already centered')
            return

        dx, dy = h - cx, h - cy
        self.update(ui, self.board.shift(dx, dy))
        ui.print(f'centered board D:{dx:+},{dy:+}')

    def cmd_clear(self, ui: PromptUI):
        '''
        clear the board
        '''
        self.update(ui, (
            (i, '')
            for i, let in enumerate(self.board.grid)
            if let))
        ui.print('cleared board')

    def cmd_erase(self, ui: PromptUI):
        '''
        erase at cursor; usage `/erase <COUNT>`
        '''
        n = ui.tokens.have(r'\d+', lambda match: int(match[0]))
        if n is None:
            ui.print('usage: /erase <COUNT>')
            return
        self.erase_at(ui, n)

    def cmd_generate(self, ui: PromptUI):
        '''
        generate word suggestions
        '''
        sel = self.board.select(self.cursor)
        pos = sel.possible(ui, lambda pat: grep(self.wordlist.words, pat, anchor='full'))
        if not pos: return

        def interact(ui: PromptUI):
            ui.print(f'{pos} to write @{sel.cursor}+{len(sel)}')
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
                ui.print(f'- writing {word!r} @{sel.cursor}+{len(sel)}')
                self.update(ui, sel.updates(word))
                return self.play

        return interact

    def cmd_letters(self, _ui: PromptUI):
        '''
        edit board free letters
        '''
        return self.EditLetters(self.board, self.num_letters, self.play)

    def cmd_priors(self, ui: PromptUI):
        '''
        list prior result boards
        '''
        for n, board in enumerate(self.prior_result_boards(), 1):
            for line in board.show_grid(head=f'Prior {n}:', foot=None):
                ui.print(line)
        # TODO final foot?

    def cmd_rejects(self, ui: PromptUI):
        '''
        list search-rejected boards
        '''
        arg = next(ui.tokens, '')
        if not arg:
            cur, n = '', 0
            for sid, bone in self.prior_reject_bones():
                if sid == cur:
                    n += 1
                else:
                    if n:
                        ui.print(f'- {cur} {n}')
                    cur, n = sid, 1
            if n:
                ui.print(f'- {cur} {n}')
            return
        want_sid = self.last_sid if arg.lower().startswith('last') else arg

        arg = next(ui.tokens, '')
        if not arg:
            ui.print(f'Reject {want_sid}:')
            for n, (sid, bone) in enumerate(self.prior_reject_bones(), 1):
                if sid == want_sid:
                    try:
                        board = Board.from_bone(bone)
                    except Exception as err:
                        ui.print(f'{n}. err:{err}')
                    else:
                        ui.print(f'{n}. score:{board.score}')
            return
        want_n = int(arg)

        for n, (sid, bone) in enumerate(self.prior_reject_bones(), 1):
            if n == want_n:
                try:
                    board = Board.from_bone(bone)
                except Exception as err:
                    ui.print(f'{n}. err:{err}')
                    ui.print(f'  bone:{bone!r}')
                else:
                    for line in board.show_grid(head=f'[ Reject {want_sid} {n} ]', foot=None):
                        ui.print(line)

    def cmd_result(self, ui: PromptUI):
        '''
        record share result from site
        '''
        ui.print('Provide share result:')
        try:
            self.proc_result(ui, ui.may_paste())
        except ValueError as err:
            ui.print(f'! {err}')

    def cmd_search(self, ui: PromptUI):
        '''
        start a search session
        '''
        h = hashlib.sha256(f'{self.start} + {ui.time.now}'.encode())
        sid = self.make_sid(h.hexdigest())
        self.last_sid = sid

        def done(board: Board|None):
            if board:
                self.update(ui, self.board.diff(board))
            return self.play

        def is_improvement(board: Board):
            sc = board.score
            res = self.result
            if res and sc <= res.score: return False
            if sc <= self.board.score: return False
            return True

        def reject(board: Board):
            if not is_improvement(board):
                ui.logz(f'reject sid:{sid} bone:{board.to_bone()}')
                return True
            return False

        return Search(
            sid,
            self.board,
            self.wordlist,
            done,
            reject=reject,
            sources=(
                ('priors', self.prior_result_boards),
                ('rejects', self.browse_reject_boards),
            ),
        )

    def cmd_shift(self, ui: PromptUI):
        '''
        shift the board; usage `/shift <dX> <dY>`
        '''
        dx, dy = 0, 0
        while ui.tokens:
            match = ui.tokens.have(r'([xyXY])([-+]\d+)')
            if match:
                xy = str(match[1])
                d = int(match[2])
                if xy.lower() == 'x':
                    dx = d
                    continue
                if xy.lower() == 'y':
                    dy = d
                    continue

            ui.print(f'! invalid arg {next(ui.tokens)!r}')
            return

        if dx == 0 and dy == 0:
            ui.print('shift noop')
        else:
            self.update(ui, self.board.shift(dx, dy))
            ui.print(f'shifted board D:{dx:+},{dy:+}')

    def cmd_store(self, _ui: PromptUI):
        '''
        store log and enter review mode
        '''
        return self.store

    def cmd_write(self, ui: PromptUI):
        '''
        write letters at curtsor; usage `/write ABCDEF...`
        '''
        word = ''.join(
            let
            for match in ui.tokens.consume(r'[a-zA-Z]+')
            for let in str(match[0])
        ).upper()

        sel = self.board.select(self.cursor)
        if len(word) > len(sel.ix):
            ui.print(f'! cannot write {word!r} @ {self.at_cursor}: not enough space')
            return

        try:
            for _ in sel.updates(word): pass
        except ValueError as err:
            ui.print(f'! {err}')
            return

        ui.print(f'- writing {word!r} @{sel.cursor}+{len(sel)}')
        self.update(ui, sel.updates(word))

    def move_to(self, ui: PromptUI, x: int, y: int, xy: Literal['X', 'Y'] = 'X'):
        self.at_cursor = x, y, xy
        ui.log(f'at: {x} {y} {xy}')

    @property
    def cursor(self):
        return self.board.cursor(*self.at_cursor)

    def erase_at(self, ui: PromptUI, erase_n: int):
        cur = self.cursor
        prior = tuple(self.board.grid[i] for i in cur)

        changes = tuple(
            (i, '')
            for i, l in zip(cur, prior[:erase_n])
            if l)
        if not changes:
            ui.print(f'- noop erase {erase_n} @ {self.at_cursor}')
            return

        lets = tuple(self.board.grid[i] for i, _ in changes)
        ui.print(f'- erasing @ {self.at_cursor} -- {' '.join(lets)}')
        self.update(ui, changes)

    def update(self, ui: PromptUI, changes: Iterable[tuple[int, str]]):
        for i, let in changes:
            self.board.set(i, let)
            ui.log(f'change: {i} {let}')

SourceEntry = tuple[str, 'Source'] | Board
Source = Callable[[], Iterable[SourceEntry]]

@final
class Search:
    def __init__(self,
                 sid: str,
                 board: Board,
                 wordlist: WordList,
                 ret: Callable[[Board|None], PromptUI.State],
                 reject: Callable[[Board], bool] = lambda _: False,
                 sources: Iterable[tuple[str, Source]] | None = None,
                 verbose: int = 0,
                 ):
        self.sid = sid
        self.board = board.copy()
        self.wordlist = wordlist
        self.ret = ret
        self.reject = reject
        self.sources = dict(sources or ()) 
        self.verbose = verbose

        self.frontier: Halo = Halo.of([self.board])
        self.frontier_cap: int = 0
        self.halos: dict[str, Halo] = dict()
        self.last_shown: str|None = None
        self.history: list[PlainData] = []
        self.explored: set[str] = set()

        self.prompt = PromptUI.Prompt(self.make_prompt, {
            'add': self.do_add,
            'auto': self.do_auto,
            'board': self.do_board,
            'cap': self.do_cap,
            'center': self.do_center,
            'clear': self.do_clear,
            'drop': self.do_drop,
            'history': self.do_hist,
            'import': self.do_import,
            'prune': self.do_prune,
            'reset': self.do_reset,
            'return': self.do_ret,
            'show': self.do_show,
            'take': self.do_take,
            'verbose': self.do_verbose,
            'zero': self.do_zero,

            '*': 'add',
            '**': 'auto',
        })

    def get_source(self, token: str) -> Source|None:
        src: Source|None = lambda: ((nom, sub) for nom, sub in self.sources.items())
        for name in token.split('/'):
            if not name: break
            got: Source|None = None
            for ent in src():
                if not isinstance(ent, tuple): continue
                nom, sub = ent
                if nom == name:
                    got = cast(Source, sub)
            if not got: return None
            src = got
        return src

    def __call__(self, ui: PromptUI):
        with ui.catch_state(EOFError, lambda _ui: self.ret(None)):
            return self.prompt(ui)

    def make_prompt(self, _ui: PromptUI):
        def halo_sort_key(k: str):
            halo = self.halos[k]
            sc = math.floor(max(halo.scores))
            return (
                2*sc if sc > 0 else
                2*(-sc) + 1 if sc < 0 else
                0)

        def prompt_parts() -> Generator[str]:
            yield f'{len(self.frontier)}'
            cap = self.frontier_cap
            if cap:
                yield f'cap:{cap}'
            for key in sorted(self.halos, key=halo_sort_key):
                yield f'{key}:{len(self.halos[key])}'

        return f'search {self.sid} {" ".join(isurround("[", prompt_parts(), "]"))}> '

    def do_add(self, ui: PromptUI):
        '''
        generates new boards by adding a word to each frontier boards
        usage: `add [-v[v...]] [<COUNT-PER> = <CAP>/<FRONTIER>(min:3) or 10] [...chooser-per options]`
        '''

        chooser = Chooser(show_n=10)
        jitter: float = 0.5
        verbose = self.verbose

        if self.frontier_cap:
            chooser.show_n = max(3, math.ceil(self.frontier_cap / len(self.frontier)))
        while ui.tokens:
            mn = ui.tokens.have(r'\d+', lambda m: int(m[0]))
            if mn is not None:
                chooser.show_n = mn
                continue

            match = ui.tokens.have(r'-(v+)')
            if match:
                verbose += len(match.group(1))
                continue

            try:
                if chooser.collect(ui.tokens):
                    continue
            except ValueError as err:
                ui.print(f'! {err}')
                return

            ui.print(f'! invalid arg {next(ui.tokens)!r}')
            return

        timing: list[tuple[str, float, float]] = list()
        with ui.time.elapsed('add_word',
                             collect=lambda label, now, elapsed: timing.append((label, now, elapsed)),
                             print=ui.print if verbose > 1 else lambda _: None,
                             final=ui.print if verbose > 0 else lambda _: None,
                             ) as mark:

            # NOTE should be redundant by proper result handling
            ded = self.frontier.split(lambda board, i: not any(l for l in board.letters))
            if ded and verbose:
                ui.print(f'pruned {len(ded)} boards from frontier')
            mark('prune')

            boards = tuple(self.frontier)

            # seed points for each board:
            # - for empty boards, this is just a couple of empty selections
            #   somewhere in the middle
            # - for boards with a region of defined letters, this is every
            #   row/col selection over the region's bounding rectangle
            seed_points = tuple(tuple(board.seeds()) for board in boards)
            mark('seed points')

            # collect potential word fragments for every board:
            # - a fragment is a sequence of defined letters in some row/col
            # - that is at least 2 letters long and not in the wordlist
            wordset = set(self.all_words())
            fragments = tuple(
                tuple(
                    frag
                    for point in points
                    for seed in (board.select(point),)
                    if any(seed)
                    for frag in islice((
                        frag
                        for frag in seed.tokens()
                        if len(frag) > 1
                        if str(frag) not in wordset
                    ), 1))
                for board, points in zip(boards, seed_points))
            mark('fragments')

            # seeds are selected regions of each board where we'll try to write a new word
            # - first, we'll try to complete any fragments, since fragments
            #   will kill a board solution if not completed
            # - but if there are no fragments, then we'll consider every row
            #   and column that intersects each board's already written region
            # - which degenerates to a point selection somewhere in the middle of an empty board
            seeds = tuple(
                (board, frags, seed)
                for board, points, frags in zip(boards, seed_points, fragments)
                for seed in (
                    flatten(
                        flatten(
                            board.select(pre).continuations()
                            for pre in frag.cursor.pre())
                        for frag in frags)
                    if frags else (
                        seed
                        for point in points
                        for sel in (board.select(point),)
                        for seed in chain(
                            (sel,),
                            # TODO relax and evaluate pre-cursors ex nihilo?
                            (board.select(pre) for pre in point.pre()) if any(sel) else ()
                        ))
                ))
            mark('elaborate seeds')

            if verbose:
                ui.print(f'searching {len(seeds)} seeds from {len(boards)} boards')


            # pull all possible words for every boards' seeds...
            seed_words = tuple(
                (board, frags, seed, self.search(seed.pattern))
                for board, frags, seed in seeds)
            mark('grep words')

            # ...but the regex may be too permissive, so apply a further
            # feasibility filter on each boards' possible words per-seed
            seed_words = tuple(
                (board, frags, seed, tuple(
                    word for word in words
                    if not seed.nop_write(word)
                    if seed.can_write(word)))
                for board, frags, seed, words in seed_words)
            mark('filter words')

            def ideal_len_for(seed: Board.Select):
                board = seed.board

                bounds = board.defined_rect
                if bounds:
                    lo_x, lo_y, hi_x, hi_y = bounds
                    return max(2, sum(
                        1
                        for x, y, _ in seed.iter_xy()
                        if lo_x < x < hi_x
                        if lo_y < y < hi_y
                    ))

                # TODO is this useful?
                # return max(2, board.size//2)

                return max(2, len(seed.ix) - 2)

            # now, that's getting to be **rather a lot** of words, so take a
            # parametric sample of each boards' filtered word list 
            seed_pos = tuple(
                (board, frags, seed, Possible(
                    words,
                    wsr.score,
                    choices=chooser.choices,
                    verbose=verbose))
                for board, frags, seed, words in seed_words
                for wsr in (WordScorer(ideal_len_for(seed), jitter=jitter),))
            mark('seed pos')

            # unroll and enumerate each possible word for every board
            seed_posi = tuple(
                (board, frags, seed, pos, pi)
                for board, frags, seed, pos in seed_pos
                for pi in pos.index())
            mark('seed posi')

            if not seed_posi:
                ui.print(f'no search seeds possible ; make some edits?')
                return

            # finally apply possible words, generating new potential boards
            may_boards = tuple(
                board.copy(seed.updates(pos.data[pi]))
                for board, _, seed, pos, pi in seed_posi)
            mark('may boards')

            # remnants are like fragments above, but for each potential board
            remnants = tuple(
                tuple(
                    frag
                    for point in board.seeds()
                    for seed in (board.select(point),)
                    if any(seed)
                    for frag in islice((
                        frag
                        for frag in seed.tokens()
                        if len(frag) > 1
                        if str(frag) not in wordset
                    ), 1))
                for board in may_boards)
            mark('remnants')

            # each potential board gets a bonus score based on how many
            # fragments it fixed or caused:
            # - if a potential board fixes N fragments, its score gets an N+1 weight boon
            # - but if a potential board adds N fragments, its score gets an N-exponential bane
            bonus = tuple(
                len(frags) - len(rems)
                for ((_, frags, _, _, _), rems) in zip(seed_posi, remnants))

            # each final board score is its possible word score
            # amplified/attenuated by any boon/bane
            scores = tuple(
                pos.scores[pi] ** (1.0 / (1 + boon)) if boon > 0 else
                pos.scores[pi] ** -boon if boon < 0 else
                pos.scores[pi]
                for ((_, _, _, pos, pi), boon) in zip(seed_posi, bonus))

            from_boards = tuple(b for (b, _, _, _, _) in seed_posi)
            mark('offer prep')

        self.explored.update(board.to_bone() for board in boards)

        def explain(i: int) -> Generator[str]:
            _, frags, seed, pos, pi = seed_posi[i]
            rems = remnants[i]
            yield f'word:{pos.data[pi]!r}'
            yield f'@{seed.cursor}+{len(seed)}'
            yield f'*= word_score: {100*pos.scores[pi]:.2f}%'
            yield from isurround(f'= (', pos.explain(pi), f')')

            boon = bonus[i]
            if boon > 0:
                yield f'^1/= boon:{1+boon}'
            elif boon < 0:
                yield f'^= bane:{-boon}'

            def parts():
                a = set(str(sel) for sel in frags)
                b = set(str(sel) for sel in rems)
                x = a.symmetric_difference(b)
                u = a.union(b)
                for token in x:
                    if token in a: yield f'-{token}'
                    if token in b: yield f'+{token}'
                for token in u: yield f'={token}'

            yield from isurround(f'frags:(', parts(), f')')

        def meta() -> Generator[PlainEntry]:
            yield 'action', 'add word',
            yield 'ded_pruned', len(ded) if ded else 0,
            yield 'from', len(boards),
            yield 'seeds', len(seeds),
            tim = tuple(
                (label, elapsed)
                for label, _now, elapsed in timing)
            yield 'timing', tim
            # TODO frag stats

        self.offer_boards(
            from_boards, may_boards,
            pos_scores=scores,
            explain_pos_score=explain,
            wordlist=self.all_words(),
            metadata=meta())

    def do_auto(self, ui: PromptUI):
        '''
        start auto generation loop
        '''
        if not self.frontier_cap:
            ui.print('! refusing to auto generate without a frontier cap')
            return self

        verbose = self.verbose
        while ui.tokens:
            match = ui.tokens.have(r'-(v+)')
            if match:
                verbose += len(match.group(1))
                continue

            ui.print(f'! invalid arg {next(ui.tokens)!r}')
            return
        self.verbose = verbose

        # TODO maybe parse program
        prog = self.auto_mod.compile('*?TC')
        if self.board.done:
            expand = prog
            sub = self.auto_mod.extend(*self.nom_ops(
                ('?', self.may_op(
                    lambda ui: 'may' not in self.halos,
                    'Prune exhausted',
                    expand)),
                ('_', self.may_op(
                    lambda ui: len(self.frontier) >= self.frontier_cap // 2,
                    lambda ui: f'Reduced {len(self.frontier)} boards, expanding',
                    expand)),
            ))
            prog = sub.compile('P?TC_')

        def monitor(state: PromptUI.State):
            def mon(ui: PromptUI):
                # TODO collect and report run stats
                with ui.catch_state(KeyboardInterrupt, self):
                    st = state(ui)
                    if st is None or st is self: return st
                    return monitor(st)
            return mon

        if self.verbose:
            ui.print('Auto Generation Starting')
        else:
            ui.write('Auto generating: ')

        return monitor(prog)

    def do_board(self, ui: PromptUI):
        '''
        show referent board ( the prior passed in at search start )
        '''
        for line in self.board.show(
            mid=f'[score: {self.board.score}]', mid_align='>',
        ): ui.print(line)

    def do_cap(self, ui: PromptUI):
        '''
        frontier size limit, show or set
        '''
        n = ui.tokens.have(r'\d+', lambda m: int(m[0]))
        if n is None:
            ui.print(f'cap: {self.frontier_cap}')
        else:
            self.frontier_cap = n
            prior = len(self.frontier)
            if n > 0 and len(self.frontier) > n:
                self.frontier = self.frontier.take(n)
            def meta() -> Generator[PlainEntry]:
                yield 'action', 'cap'
                yield 'cap', self.frontier_cap
                if n:
                    yield 'prior', prior
            self.history.append(tuple(meta()))
            ui.print(
                f'set cap: {self.frontier_cap}'
                if n else f'cleared cap')

    def do_center(self, ui: PromptUI):
        '''
        recenter all frontier boards
        '''
        verbose = self.verbose
        while ui.tokens:
            match = ui.tokens.have(r'-(v+)')
            if match:
                verbose += len(match.group(1))
                continue

            ui.print(f'! invalid arg {next(ui.tokens)!r}')
            return

        boards = tuple(self.frontier)
        shifts = tuple(
            ( h - math.floor(bounds[0]/2 + bounds[2]/2),
              h - math.floor(bounds[1]/2 + bounds[3]/2)
            ) if bounds else (0, 0)
            for board in boards
            for bounds in (board.defined_rect,)
            for h in (board.size//2,))

        for n, (board, (dx, dy)) in enumerate(zip(boards, shifts), 1):
            if dx != 0 or dy != 0:
                if verbose:
                    ui.write(f'{n}. D:{dx:+},{dy:+}: ')
                board.update(board.shift(dx, dy))
                if verbose:
                    ui.fin()

        def meta() -> Generator[PlainEntry]:
            yield 'action', 'center'
            yield 'shifts', shifts

        self.history.append(tuple(meta()))

    def do_clear(self, ui: PromptUI):
        '''
        clear referent board grid, freeing all letters
        '''
        self.board.update((i, '') for i, let in enumerate(self.board.grid) if let)
        ui.print('Cleared board.')

    def do_drop(self, ui: PromptUI):
        '''
        remove trailing N frontier boards; usage `drop <COUNT>`
        '''
        n = ui.tokens.have(r'\d+', lambda m: int(m[0]))
        if n is None:
            ui.print('usage: drop <COUNT>')
            return

        m = min(len(self.frontier), n)
        prior = len(self.frontier)
        self.frontier = self.frontier.take(-m)
        def meta() -> Generator[PlainEntry]:
            yield 'action', 'drop'
            yield 'given', n
            yield 'drop', m
            yield 'prior', prior
        self.history.append(tuple(meta()))
        ui.print(f'dropped {m} from frontier')

    def do_hist(self, ui: PromptUI):
        '''
        show search history; usage `hist [-json] [/q:[FIELD:]PATTERN]`
        '''
        as_json = False
        wheres: list[Callable[[PlainData], bool]] = []

        while ui.tokens:
            if ui.tokens.have(r'-j(s(on?)?)?'):
                as_json = True
                continue

            match = ui.tokens.have(r'/q:(?:(.+?):)?(.+)')
            if match:
                wheres.append(plain_make_matcher(match[1] or 'action', match[2]))
                continue

            ui.print(f'! invalid arg {next(ui.tokens)!r}')
            return

        data = self.history
        if wheres:
            where = plain_chain_matcher(*wheres)
            data = [dat for dat in data if where(dat)]

        if as_json:
            with ui.copy_writer() as w:
                _ = w.write('[')
                for i, h in enumerate(data):
                    if i > 0: _ = w.write(',')
                    json.dump(plain_dictify(h), w)
                _ = w.write(']')
                ui.print(f'📋 {len(data)} history entries as JSON')
        elif not data:
            ui.print('-- empty --')
        else:
            # TODO maybe do a table
            for n, h in enumerate(data, 1):
                ui.print(f'{n}. {plain_dictify(h)!r}')

    def do_import(self, ui: PromptUI):
        '''
        available prior source boards, list and merge into frontier
        usage: `import <NAME> [<NAME> ...]`
        '''
        if not ui.tokens:
            ui.print('Available Sources')
            for name in sorted(self.sources):
                ui.print(f'- {name}')
            return

        names = tuple(ui.tokens)
        srcs = tuple(self.get_source(name) for name in names)

        entries = tuple(
            cast(tuple[SourceEntry, ...],
                tuple(src()) if src else ())
            for src in srcs)

        if not any(srcs):
            ui.print('! no valid sources provided ; run without arg to list available')
            return

        any_feedback = False
        for name, src, got in zip(names, srcs, entries):
            if not src:
                ui.print(f'! ignoring unknown source {name!r}')
                any_feedback = True
            elif name.endswith('/'):
                ui.print(f'- listing {name}')
                boards = 0
                for ent in got:
                    if isinstance(ent, Board):
                        boards += 1
                    else:
                        ui.print(f'  - {ent[0]}/')
                if boards:
                    ui.print(f'  * {boards} boards')
                any_feedback = True
        if any_feedback:
            return

        boards = tuple(
            tuple(
                ent
                for ent in ents
                if isinstance(ent, Board))
            for ents in entries)

        for name, got in zip(names, boards):
            ui.print(f'* importing {len(got)} boards from {name!r}')

        self.frontier = Halo.of(
            chain(self.frontier, chain.from_iterable(boards)),
            Halo.WithWordLabels(self.wordlist))

        if self.frontier_cap:
            self.frontier = self.frontier.take(self.frontier_cap)

        def meta() -> Generator[PlainEntry]:
            yield 'action', 'import'
            yield 'sources', names
            yield 'cap', self.frontier_cap
            yield 'got', tuple(
                -1 if src is None else len(bs) # TODO maybe math.nan instead?
                for src, bs in zip(srcs, boards))
        self.history.append(tuple(meta()))

    def do_prune(self, ui: PromptUI):
        '''
        generates new boards by pruning word(s) from frontier boards
        usage: `prune [-v[v...]] [<COUNT>]
        '''

        num_prunes = 1
        verbose = self.verbose
        while ui.tokens:
            match = ui.tokens.have(r'-(v+)')
            if match:
                verbose += len(match.group(1))
                continue

            mn = ui.tokens.have(r'\d+', lambda m: int(m[0]))
            if mn is not None:
                num_prunes = mn
                continue

            ui.print(f'! invalid arg {next(ui.tokens)!r}')
            return

        timing: list[tuple[str, float, float]] = list()
        with ui.time.elapsed('prune_word',
                             collect=lambda label, now, elapsed: timing.append((label, now, elapsed)),
                             print=ui.print if verbose > 1 else lambda _: None,
                             final=ui.print if verbose > 0 else lambda _: None,
                             ) as mark:

            boards = tuple(self.frontier)
            affixes = tuple(
                tuple(board.word_affixes())
                for board in boards)
            mark('affixes')

            choose = tuple(
                max(1, min(len(afs), num_prunes))
                for afs in affixes)

            board_choices = tuple(
                (board, choices)
                for board, afs, bn in zip(boards, affixes, choose)
                for choices in combinations(afs, bn))
            mark('choose tokens')

            may_boards = tuple(
                board.copy(
                    (i, '')
                    for token in choices
                    for i in token.ix)
                for board, choices in board_choices)
            mark('gen boards')

            from_boards = tuple(
                board
                for board, _choices in board_choices)

        # TODO particular socring?
        # def explain(i: int) -> Generator[str]:
        #     pass

        def meta() -> Generator[PlainEntry]:
            yield 'action', 'prune word',

        self.offer_boards(
            from_boards, may_boards,
            # pos_scores=scores,
            # explain_pos_score=explain,
            metadata=meta())

    def do_reset(self, ui: PromptUI):
        '''
        reset history, reset frontier to referent prior board
        '''
        self.explored.clear()
        self.history.clear()
        self.frontier = Halo.of([self.board])
        self.halos.clear()
        ui.print('Frontier Reset.')

    def do_ret(self, ui: PromptUI):
        '''
        return a result board; usage: `ret [<halo>] [<N>]` defaults to last shown, 'done', or 'frontier' halo
        '''
        try_keys: tuple[str|None, ...] = (
            ui.tokens.have(r'[^\d].*', lambda m: m[0]),
            self.last_shown, 'done', 'frontier')

        halo: Halo|None = None
        key: str|None = None
        for key in try_keys:
            if not key: continue
            halo = self.get_halo(key)
            if halo: break
        else:
            ui.print(f'! no {key} halo')
            return
        assert halo and key

        board, reason = halo.ref(ui)
        if not board:
            ui.print(f'! {key} halo {reason}')
            return
        ui.print(f'returning {key} halo {reason}')
        return self.ret(board)

    def do_show(self, ui: PromptUI):
        '''
        show a board from a halo; usage: `show [<halo>] [<N>]` defaults to last shown, 'may', or 'frontier' halo
        '''
        try_keys: tuple[str|None, ...] = (
            ui.tokens.have(r'[^\d].*', lambda m: m[0]),
            self.last_shown, 'may', 'frontier')

        halo: Halo|None = None
        key: str|None = None
        for key in try_keys:
            if not key: continue
            halo = self.get_halo(key)
            if halo: break
        else:
            ui.print(f'! no {key} halo')
            return
        assert halo and key

        n = ui.tokens.have(r'\d+', lambda m: int(m[0]))
        if n is not None:
            halo.show_n(ui, n, f'{key} halo')
        else:
            halo.show(ui, title=f'{key} halo')
            self.last_shown = key
        return

    def do_take(self, ui: PromptUI):
        '''
        sort halo boards into frontier
        usage: `take [-v] [<HALO> = may] [<COUNT> = <CAP>]`
        '''
        name: str = ''
        take_n: int|None = None
        verbose = self.verbose
        while ui.tokens:
            match = ui.tokens.have(r'-(v+)')
            if match:
                verbose += len(match.group(1))
                continue

            n = ui.tokens.have(r'\d+', lambda m: int(m[0]))
            if n is not None:
                if take_n is not None:
                    ui.print(f'! usage: take [<HALO>] [<COUNT>]')
                    return
                take_n = n
                continue

            if not name:
                name = next(ui.tokens)
                continue

            ui.print(f'! usage: take [<HALO>] [<COUNT>]')
            return

        if not name:
            name = 'may'
        halo = self.get_halo(name)
        if not halo:
            ui.print(f'! no {name} halo')
            return
        have = len(halo)

        if self.frontier_cap:
            take_n = take_n or self.frontier_cap
        if not halo.parse_choices(ui, prior_n=take_n):
            return
        choices = set(halo.choices())
        take = halo.split(lambda board, i: i in choices)
        if not take:
            return

        self.frontier = Halo.of(
            chain(self.frontier, take),
            Halo.WithWordLabels(self.wordlist))

        if self.frontier_cap:
            self.frontier = self.frontier.take(self.frontier_cap)

        def meta() -> Generator[PlainEntry]:
            yield 'action', 'take'
            yield 'sample', str(halo.sample)
            yield 'name', name
            yield 'count', take_n or have
            yield 'halo', have
            yield 'frontier', len(self.frontier)
            yield 'cap', self.frontier_cap

        def parts():
            yield f'Took {halo.sample} from {name}'
            yield f'had {have}'
            yield f'frontier now {len(self.frontier)}'
            if self.frontier_cap:
                yield f'cap {self.frontier_cap}'

        if verbose:
            ui.print(' '.join(parts()))

        self.history.append(tuple(meta()))

    def do_verbose(self, ui: PromptUI):
        n = ui.tokens.have(r'\d+', lambda m: int(m[0]))
        if n is None:
            ui.print(f'verbose: {self.verbose}')
        else:
            self.verbose = n
            ui.print(f'set verbose:{self.verbose}')

    def do_zero(self, ui: PromptUI):
        '''
        reset history, reset frontier to empty
        '''
        self.explored.clear()
        self.history.clear()
        self.frontier = Halo.of([])
        self.halos.clear()
        ui.print('Frontier Zeroed.')

    def get_halo(self, key: str) -> 'Halo|None':
        return self.frontier if key == 'frontier' else self.halos.get(key)

    def update_halos(self, items: Iterable[tuple[str, 'Halo|None']]):
        for key, halo in items:
            if halo:
                self.halos[key] = halo
            elif key in self.halos:
                del self.halos[key]

    def offer_halo(self, may: 'Halo'):
        have: set[str] = set()
        rex: set[str] = set()
        def seen_before(board: Board, _i: int):
            bone = board.to_bone()
            if bone in self.explored:
                rex.add(bone)
                return True
            if bone in have: return True
            have.add(bone)
            return False
        prune = may.split(seen_before)

        done = may.split(lambda board, i: may.scores[i] > 1)
        reject = None if done is None else done.split(lambda board, i: self.reject(board))
        dead = may.split(lambda board, i: may.scores[i] < 0)

        def meta() -> Generator[PlainEntry]:
            yield from may.meta
            yield 'may', len(may)
            yield 'done', len(done) if done else 0
            yield 'prune', len(prune) if prune else 0
            yield 'explored', len(rex)
            yield 'duped', len(have)
            yield 'dead', len(dead) if dead else 0
            yield 'reject', len(reject) if reject else 0
        self.history.append(tuple(meta()))
        self.update_halos((
            ('may', may),
            ('done', done),
            ('prune', prune),
            ('dead', dead),
            ('reject', reject),
        ))

    _all_words: tuple[str, ...] | None = None

    def all_words(self):
        if self._all_words is None:
            self._all_words = tuple(grep(
                self.wordlist.words,
                self.board.all_pattern,
                anchor='full'))
        return self._all_words

    _search_cache: OrderedDict[re.Pattern[str], tuple[str, ...]] = OrderedDict()

    def search(self, pattern: re.Pattern[str]):
        if pattern not in self._search_cache:
            self._search_cache[pattern] = tuple(
                grep(self.all_words(), pattern, anchor='full'))
        return self._search_cache[pattern]


    def offer_boards(self,
                     from_boards: tuple[Board, ...],
                     new_boards: tuple[Board, ...],
                     pos_scores: tuple[float, ...]|None = None,
                     explain_pos_score: Callable[[int], Iterable[str]]|None = None,
                     metadata: Iterable[PlainEntry] = (),
                     wordlist: Iterable[str]|None = None,
                     ):
        wordset = set(self.all_words() if wordlist is None else wordlist)

        # TODO catch and try to fix bad words earlier ; i.e. they're actually critical seed sites
        all_words = tuple(
            tuple(board.all_words())
            for board in new_boards)
        bad_words = tuple(
            tuple(
                word
                for word in aw
                if str(word) not in wordset)
            for aw in all_words)

        uplifts = tuple(
            0.5 + b.score/b.max_score/2 - a.score/b.max_score/2
            for a, b in zip(from_boards, new_boards))

        scores = tuple(
            ps * uplift if any(l for l in may_board.letters)
            else -2.0 if bw
            else 2.0
            for (
                may_board,
                ps,
                uplift,
                bw
            ) in zip(
                new_boards,
                repeat(0.0) if pos_scores is None else pos_scores,
                uplifts,
                bad_words,
            ))

        def explain(i: int) -> Generator[str]:
            from_board = from_boards[i]
            new_board = new_boards[i]
            score = scores[i]
            if score > 1:
                yield f'done; score:{new_board.score - self.board.score:+}'
                yield f'all words: {" ".join(str(w) for w in all_words[i])}'

            elif score < 0:
                yield f'bad words: {" ".join(str(w) for w in bad_words[i])}'

            else:
                yield f'score:{100*score:.2f}%'
                yield f'*= uplift: {100*uplifts[i]:.2f}% ('
                yield f'score:{new_board.score - from_board.score:+}'
                yield f'bonus:{new_board.space_bonus - from_board.space_bonus:+}'
                yield f')'

                if explain_pos_score:
                    yield from explain_pos_score(i)

        def meta() -> Generator[PlainEntry]:
            yield from metadata
            yield 'words', tuple(plain_describe(len(aw) for aw in all_words))
            yield 'bad_words', tuple(plain_describe(len(bw) for bw in all_words))
            if pos_scores:
                yield 'pos', tuple(plain_describe(pos_scores))
            yield 'uplifts', tuple(plain_describe(uplifts))
            yield 'scores', tuple(plain_describe(scores))

        self.offer_halo(Halo(
            new_boards, scores, explain,
            meta = meta(),
        ))

    def prune_word(self,
                   ui: PromptUI,
                   num_prunes: int = 1):

        verbose = self.verbose
        while ui.tokens:
            match = ui.tokens.have(r'-(v+)')
            if match:
                verbose += len(match.group(1))
                continue

            mn = ui.tokens.have(r'\d+', lambda m: int(m[0]))
            if mn is not None:
                num_prunes = mn
                continue

            ui.print(f'! invalid arg {next(ui.tokens)!r}')
            return

        timing: list[tuple[str, float, float]] = list()
        with ui.time.elapsed('add_word',
                             collect=lambda label, now, elapsed: timing.append((label, now, elapsed)),
                             print=ui.print if verbose > 1 else lambda _: None,
                             final=ui.print if verbose > 0 else lambda _: None,
                             ) as mark:

            boards = tuple(self.frontier)
            affixes = tuple(
                tuple(board.word_affixes())
                for board in boards)
            mark('affixes')

            choose = tuple(
                max(1, min(len(afs), num_prunes))
                for afs in affixes)

            board_choices = tuple(
                (board, choices)
                for board, afs, bn in zip(boards, affixes, choose)
                for choices in combinations(afs, bn))
            mark('choose tokens')

            may_boards = tuple(
                board.copy(
                    (i, '')
                    for token in choices
                    for i in token.ix)
                for board, choices in board_choices)
            mark('gen boards')

            from_boards = tuple(
                board
                for board, _choices in board_choices)

        # TODO particular socring?
        # def explain(i: int) -> Generator[str]:
        #     pass

        def meta() -> Generator[PlainEntry]:
            yield 'action', 'prune word',

        self.offer_boards(
            from_boards, may_boards,
            # pos_scores=scores,
            # explain_pos_score=explain,
            metadata=meta())

    def generate(self, ui: PromptUI):
        # TODO do_center wen
        # TODO do_prune wen
        return self.do_add(ui)

    @dataclass
    class NomOp:
        srch: 'Search'
        nom: str
        op: PromptUI.State
        def __call__(self, ui: PromptUI):
            if not self.srch.verbose: ui.write(self.nom)
            return self.op(ui)

    def nom_op(self, nom: str, op: PromptUI.State):
        return self.NomOp(self, nom, op)

    def may_op(self,
               when: Callable[[PromptUI], bool],
               mess: Callable[[PromptUI], str]|str,
               then: PromptUI.State,
               ):
        def may_state(ui: PromptUI):
            if when(ui):
                if self.verbose:
                    ui.print(mess(ui) if callable(mess) else mess)
                else:
                    ui.fin()
                return then
        return may_state

    def nom_ops(self, *nomops: tuple[str, PromptUI.State]):
        for nom, op in nomops:
            yield nom, self.NomOp(self, nom, op)

    @final
    class Module:
        def __init__(self, *ops: tuple[str, PromptUI.State]):
            self.ops = dict(ops)

        def compile(self, src: str, *then: PromptUI.State):
            return PromptUI.Chain(*(self.ops[op] for op in src), *then)

        def extend(self, *ops: tuple[str, PromptUI.State]):
            return self.__class__(*chain(self.ops.items(), ops))

    @property
    def auto_mod(self):
        return self.Module(*self.nom_ops(
            ('*', self.generate),
            ('C', self.do_center),
            ('P', self.do_prune),
            ('T', self.do_take),
            ('?', self.may_op(
                lambda ui: 'done' in self.halos or 'may' not in self.halos,
                'Auto Generation Finished',
                self)),
        ))

@final
class Halo:
    Explainer = Callable[[int], Iterable[str]]
    Scorer = Callable[[Sequence[Board]], tuple[tuple[float, ...], Explainer]]

    @staticmethod
    def ExplainBoard(board: Board):
        yield f'('
        yield f'score:{board.score}'
        yield f'bonus:{board.space_bonus:+}'
        yield f')'

    @staticmethod
    def NaturalScores(boards: Sequence[Board]):
        scores = tuple(board.score/board.max_score for board in boards)
        def explain(i: int) -> Iterable[str]:
            score = scores[i]
            yield f'score:{100*score:.2f}%'
            yield from Halo.ExplainBoard(boards[i])
        return scores, explain

    @staticmethod
    def WithWordLabels(wordlist: WordList, scorer: Scorer = NaturalScores) -> Scorer:
        def with_words(boards: Sequence[Board]):
            ok_words = wordlist.uniq_words
            scores, sub_explain = scorer(boards)

            def explain(i: int) -> Iterable[str]:
                yield from sub_explain(i)

                board = boards[i]
                aw = tuple(str(w) for w in board.all_words())
                bw = tuple(
                    word
                    for word in aw
                    if word not in ok_words)
                aw = tuple(w for w in aw if w not in bw)
                yield f'all words: {aw!r}'
                if bw: yield f'bad words: {bw!r}'

            return scores, explain

        return with_words

    @classmethod
    def of(cls, itBoards: Iterable[Board], scorer: Scorer = NaturalScores):
        boards = tuple(itBoards)
        scores, explain = scorer(boards)
        return cls(boards, scores, explain)

    def __init__(self,
                 boards: tuple[Board, ...],
                 scores: tuple[float, ...],
                 explain: Callable[[int], Iterable[str]] = lambda _i: (),
                 ix: Iterable[int]|None = None,
                 meta: Iterable[PlainEntry] = (),
                 ):
        self.boards = boards
        self.scores = scores
        self.explain = explain
        self.ix: tuple[int, ...]|None = tuple(ix) if ix is not None else None
        self.meta = tuple(meta)

        self.sample: Sample|None = None
        self.last_shown: int|None = None

    def __len__(self):
        return len(self.ix) if self.ix is not None else len(self.boards)

    def __iter__(self):
        for i in self.ix or range(len(self.scores)):
            yield self.boards[i]

    def take(self, n: int):
        if n < 0:
            n = len(self) + n
        return self.__class__(
            self.boards,
            self.scores,
            self.explain,
            ix=tuple(islice(self.descending(), n)))

    def descending(self):
        ix = sorted(
            self.ix or range(len(self.scores)),
            key=lambda i: self.scores[i],
            reverse = True)
        for i in ix:
            yield i

    def set_choices(self, *choices: Sample.Choice|MatchPat):
        self.sample = Sample(Sample.compile_choices(
            choices,
            lambda pats: match_show(self.explain, pats)))

    def choices(self):
        if not self.sample:
            self.set_choices()
            assert self.sample
        return self.sample.index(self.scores, self.ix)

    def split(self, where: Callable[[Board, int], bool]):
        ix = self.ix or range(len(self.scores))
        other = self.__class__(self.boards,
                               self.scores,
                               self.explain,
                               ix=(i for i in ix if where(self.boards[i], i)))
        if other.ix:
            self.ix = tuple(i for i in ix if i not in set(other.ix))
            return other
        return None

    def parse_choices(self,
                      ui: PromptUI,
                      prior_n: int | None = None,
                      ):
        chooser = Chooser()
        any_choice = False

        if prior_n is not None:
            chooser.show_n = prior_n
            any_choice = True

        while ui.tokens:
            n = ui.tokens.have(r'\d+', lambda m: int(m[0]))
            if n is not None:
                chooser.show_n = n
                any_choice = True
                continue

            if chooser.parse(ui.tokens):
                any_choice = True
                continue

            ui.print(f'! invalid arg {ui.tokens.rest}')
            return False

        if any_choice:
            self.set_choices(*chooser.choices)

        return True

    def show(self, ui: PromptUI, title: str = ''):
        n = ui.tokens.have(r'\d+', lambda m: int(m[0]))
        if n is not None:
            return self.show_n(ui, n, title)

        chooser = Chooser()
        while ui.tokens:
            if chooser.parse(ui.tokens):
                continue
            ui.print(f'! invalid arg {ui.tokens.rest}')
            return
        self.set_choices(*chooser.choices)

        ui.print(f'{title} {self.sample}:' if title else f'{self.sample}:')
        for n, i in enumerate(self.choices(), 1):
            for line in wrap_item(*numbered_item(n, self.explain(i))):
                ui.print(line)

    def show_n(self, ui: PromptUI, n: int, title: str = ''):
        ui.print(f'{title} #{n}' if title else f'#{n}')
        for m, i in enumerate(self.choices(), 1):
            if m == n:
                board = self.boards[i]
                for line in board.show(
                    mid=f'[score: {board.score}]', mid_align='>',
                ): ui.print(line)
                self.last_shown = n
                return
        ui.print(f'! invalid {title} choice {n}' if title else f'! invalid choice {n}')

    def ref(self, ui: PromptUI, n: int|None = None):
        if n is None:
            n = ui.tokens.have(r'\d+', lambda m: int(m[0]))

        if n is not None:
            for m, i in enumerate(self.choices(), 1):
                if m == n: return self.boards[i], f'#{n} given'
            return None, f'#{n} not found'

        if n is None:
            n = self.last_shown
            for m, i in enumerate(self.choices(), 1):
                if m == n: return self.boards[i], f'#{n} last shown'

        for i in self.choices():
            return self.boards[i], '#1 default'

        return None, 'empty'

@dataclass
class Result:
    title: str
    url: str
    score: int
    rank: tuple[int, int]
    tiles: tuple[int, int]
    bonus: int
    final: bool

    @classmethod
    def parse(cls, s: str):
        title = ''
        url = ''
        score = 0
        rank = (0, 0)
        final = False
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
                ( Final \s+ )? Rank:
                \s*
                ( \d+ ) \s* / \s* ( \d+ )
                ''', line)
            if match:
                final = True if match[1] else False
                rank = int(match[2]), int(match[3])
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
        return cls(title, url, score, rank, tiles, bonus, final)

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
    - url: ```
    https://spaceword.org
    ```
    - score: 2158
    - rank: (165, 322)
    - tiles: (21, 21)
    - bonus: 58
    - final: False

    #final_solve
    > ✨ Spaceword.org Daily 2025-05-15 ✨
    > 
    > 🏆 Score: 2168
    > 🏅 Final Rank: 178/520 👏
    > 🧩 Tiles: 21/21 ✅
    > 📏 Space Bonus: +68
    > 
    > 
    > Play at https://spaceword.org
    > #spaceword
    - title: Daily 2025-05-15
    - url: ```
    https://spaceword.org
    ```
    - score: 2168
    - rank: (178, 520)
    - tiles: (21, 21)
    - bonus: 68
    - final: True

''')
def test_parse_result(spec: MarkedSpec):
    res = Result.parse(spec.input)
    for key, value in spec.props:
        if key == 'title': assert res.title == value
        elif key == 'url': assert res.url == value
        elif key == 'score': assert f'{res.score}' == value
        elif key == 'rank': assert f'{res.rank}' == value
        elif key == 'tiles': assert f'{res.tiles}' == value
        elif key == 'bonus': assert f'{res.bonus}' == value
        elif key == 'final': assert f'{res.final}' == value

if __name__ == '__main__':
    SpaceWord.main()
