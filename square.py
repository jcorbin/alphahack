#!/usr/bin/env python

import argparse
import json
import math
import random
import re
from collections import Counter, OrderedDict
from collections.abc import Generator, Iterable
from typing import cast, final, overload, override

from store import StoredLog, git_txn
from strkit import MarkedSpec, PeekStr, spliterate
from ui import PromptUI

def char_pairs(alpha: Iterable[str]):
    a, b = '', ''
    for c in sorted(alpha):
        if not a: a = c
        if not b: b = c
        dcb = ord(c) - ord(b)
        if dcb > 1:
            yield a, b
            a = b = c
        else:
            b = c
    if a and b:
        yield a, b

def char_ranges(alpha: Iterable[str]):
    for a, b in char_pairs(alpha):
        dba = ord(b) - ord(a)
        if dba == 0:
            yield a
        elif dba == 1:
            yield a
            yield b
        else:
            yield a
            yield '-'
            yield b

@final
class Search(StoredLog):
    log_file: str = 'squareword.log'
    default_site: str = 'squareword.org'
    default_wordlist: str = '/usr/share/dict/words'

    @override
    def add_args(self, parser: argparse.ArgumentParser):
        super().add_args(parser)
        _ = parser.add_argument('--wordlist')

    @override
    def from_args(self, args: argparse.Namespace):
        super().from_args(args)
        wordlist = cast(str, args.wordlist)
        if wordlist:
            self.wordlist = wordlist
            self.default_wordlist = wordlist

    def __init__(self):
        super().__init__()

        self.size: int = 5
        self.wordlist: str = ''

        self.grid: list[str] = ['' for _ in range(self.size**2)]
        self.qmode: str = '?'
        self.questioning: str = ''
        self.question_desc: str = ''

        self.guesses: dict[str, int] = dict()
        self.rejects: set[str] = set()

        self.nope: set[str] = set()
        self.row_may: list[set[str]] = [set() for _ in range(self.size)]

        self.result_text: str = ''
        self._result: Result|None = None

    @property
    def result(self):
        if self._result is None and self.result_text:
            try:
                res = Result.parse(self.result_text, self.size)
            except ValueError:
                return None
            self._result = res
        return self._result

    @override
    def startup(self, ui: PromptUI):
        if not self.puzzle_id:
            ui.br()
            if not self.wordlist:
                with ui.input(f'📜 {self.default_wordlist} ? ') as tokens:
                    self.wordlist = next(tokens, self.default_wordlist)
                    ui.log(f'wordlist: {self.wordlist}')
            self.do_puzzle(ui)
            if not self.puzzle_id: return

        return self.question if self.questioning else self.display

    @property
    @override
    def run_done(self) -> bool:
        return all(let for let in self.grid)

    def do_puzzle(self, ui: PromptUI):
        with ui.input(f'🧩 {self.puzzle_id} ? ') as tokens:
            if tokens.peek():
                ps = tokens.have(r'#\d+$', lambda m: m[0])
                if not ps:
                    ui.print('! puzzle_id must be like #<NUMBER>')
                    return
                ui.log(f'puzzle_id: {ps}')
                self.puzzle_id = ps

    @override
    def load(self, ui: PromptUI, lines: Iterable[str]):
        for t, rest in super().load(ui, lines):
            match = re.match(r'''(?x)
                puzzle_id :
                \s+
                (?P<token> [^\s]+ )
                \s* ( .* )
                $''', rest)
            if match:
                token, rest = match.groups()
                assert rest == ''
                self.puzzle_id = token
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
                self.wordlist = wordlist
                continue

            match = re.match(r'''(?x)
                forget :
                \s+ (?P<index> \d+ )
                \s* ( .* )
                $''', rest)
            if match:
                index, rest = match.groups()
                assert rest == ''
                self.forget(ui, int(index))
                continue

            match = re.match(r'''(?x)
                may :
                \s+ (?P<index> \d+ )
                (?P<may> (?: \s+ [A-Za-z] )+ )
                \s* ( .* )
                $''', rest)
            if match:
                index, may, rest = match.groups()
                assert rest == ''
                word_i = int(index)
                may = cast(str, may)
                self.row_may[word_i] = set(let.strip().lower() for let in may.split())
                continue

            match = re.match(r'''(?x)
                nope :
                (?P<may> (?: \s+ [A-Za-z] )+ )
                \s* ( .* )
                $''', rest)
            if match:
                nope, rest = match.groups()
                assert rest == ''
                may = cast(str, nope)
                self.nope = set(let.strip().lower() for let in may.split())
                continue

            match = re.match(r'''(?x)
                questioning :
                \s* (?P<json> .+ )
                $''', rest)
            if match:
                raw, = match.groups()
                dat = cast(object, json.loads(raw))
                assert isinstance(dat, list)
                dat = cast(list[object], dat)
                assert len(dat) == 2
                word, desc = dat
                assert isinstance(word, str)
                assert isinstance(desc, str)
                _ = self.ask_question(ui, word, desc)
                continue

            match = re.match(r'''(?x)
                question \s+ done
                \s* ( .* )
                $''', rest)
            if match:
                rest, = match.groups()
                assert rest == ''
                self.question_done(ui)
                continue

            match = re.match(r'''(?x)
                guess :
                \s* (?P<word> \w+ )
                \s* ( .* )
                $''', rest)
            if match:
                word, rest = match.groups()
                assert rest == ''
                _ = self.question_guess(ui, word)
                continue

            match = re.match(r'''(?x)
                reject :
                \s+ (?P<word> \w+ )
                \s* ( .* )
                $''', rest)
            if match:
                word, rest = match.groups()
                assert rest == ''
                self.question_reject(ui, word)
                continue

            match = re.match(r'''(?x)
                word :
                \s+ (?P<index> \d+ )
                \s+ (?P<word> (?: [_A-Za-z] )+ )
                \s* ( .* )
                $''', rest)
            if match:
                index, word, rest = match.groups()
                assert rest == ''
                word_i = int(index)
                word = cast(str, word).lower()
                word = ['' if let == '_' else let for let in word]
                if len(word) > self.size:
                    word = word[:self.size]
                while len(word) < self.size: word.append('')
                for j, c in zip(self.row_word_range(word_i), word):
                    self.grid[j] = c
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

            yield t, rest

    def find(self, _ui: PromptUI, pattern: re.Pattern[str], row: int|None = None) -> Generator[str]:
        if row is not None:
            col_may: list[set[str]] = [set() for _ in range(self.size)]
            for col in range(self.size):
                p, _ = self.pattern(col=col)
                col_may[col].update(word[row] for word in self._find(re.compile(p)))
            for word in self._find(pattern):
                if all(
                    word[col] in may
                    for col, may in enumerate(col_may)
                ): yield word
            return

        yield from self._find(pattern)

    _find_cache: OrderedDict[str, list[str]] = OrderedDict()

    def _find(self, pattern: re.Pattern[str]):
        if pattern.pattern not in self._find_cache:
            maxsize = self.size**2
            while len(self._find_cache) >= maxsize:
                _ = self._find_cache.popitem(last=True)
            self._find_cache[pattern.pattern] = list(self._match_wordlist(pattern))
        else:
            self._find_cache.move_to_end(pattern.pattern)

        for word in self._find_cache[pattern.pattern]:
            if word in self.rejects: continue
            if word in self.guesses: continue
            yield word

    def _match_wordlist(self, pattern: re.Pattern[str]):
        with open(self.wordlist) as f:
            for line in f:
                line = line.strip().lower()
                word = line.partition(' ')[0]
                word = word.lower()
                if pattern.fullmatch(word): yield word

    def okay_letters(self) -> Generator[str]:
        for let in self.grid:
            if let: yield let
        for may in self.row_may:
            yield from may

    recent_sug: dict[str, int] = dict()

    def select(self, ui: PromptUI, word_i: int|None = None) -> tuple[int, re.Pattern[str]]|None:
        if word_i is not None:
            p, _ = self.pattern(row=word_i)
            pattern = re.compile(p)
            return word_i, pattern

        pattern: re.Pattern[str]|None = None
        smallest = 0
        for word_j in range(self.size):
            if all(self.grid[k] for k in self.row_word_range(word_j)): continue
            p, _ = self.pattern(row=word_j)
            p = re.compile(p)
            have = sum(1 for _ in self.find(ui, p, row=word_j))
            if not have: continue
            if not pattern or have < smallest:
                word_i, pattern, smallest = word_j, p, have

        if word_i is None: return None
        if pattern is None: return None
        return word_i, pattern

    def choose(self, ui: PromptUI, word_i: int|None = None):
        sel = self.select(ui, word_i)
        if not sel: return
        word_i, pattern = sel

        best, choice = 0.0, ''
        count = 0
        okay = set(self.okay_letters())

        for word in self.find(ui, pattern, row=word_i):
            count += 1

            score = random.random()

            novel = sum(1 for let in word if let not in okay)
            if novel > 0:
                score = math.pow(score, 1/novel)
            else:
                lc = Counter(word)
                n = sum(lc.values())
                m = n/len(lc)
                v = sum((v - m)**2 for v in lc.values())
                score = math.pow(score, 0.01 + v)

            if word in self.recent_sug:
                penalty = self.recent_sug[word]
                score /= penalty
                if penalty > 1:
                    self.recent_sug[word] = penalty - 1
                else:
                    del self.recent_sug[word]

            if not word or score > best:
                best, choice = score, word
                self.recent_sug[word] = 10
                yield word_i, best, choice, count

    @overload
    def pattern(self, *, row: int) -> tuple[str, int]: pass

    @overload
    def pattern(self, *, col: int) -> tuple[str, int]: pass

    def pattern(self, *, row: int|None = None, col: int|None = None) -> tuple[str, int]:
        if row is not None:
            word = [self.grid[k] for k in self.row_word_range(row)]
            may = sorted(self.row_may[row])
        elif col is not None:
            word = [self.grid[k] for k in self.col_word_range(col)]
            may = []
        else:
            raise RuntimeError('must provide either row or col')

        alpha = set('abcdefghijklmnopqrstuvwxyz')
        uni = '.'

        # TODO reduce pattern based on other dimension

        if self.nope:
            alpha.difference_update(self.nope)
            uni = f'[{"".join(char_ranges(alpha))}]'

        free = sum((1 for let in word if not let), 0)
        if may: free -= len(may)
        space: int = len(alpha)**free
        if may:
            for n in range(len(may), 1, -1): space *= n

        if not may:
            if free == self.size:
                return uni * self.size, space
            return ''.join(uni if not let else let for let in word), space

        def alts():
            from itertools import combinations, permutations
            ix = [i for i in range(len(word)) if not word[i]]
            for mix in combinations(ix, len(may)):
                parts = [uni if not let else let for let in word]
                for pmay in permutations(may):
                    for j, i in enumerate(mix):
                        parts[i] = pmay[j]
                    yield ''.join(parts)

        return '|'.join(alts()), space

    skip_show: bool = False

    def show(self, ui: PromptUI):
        if self.skip_show:
            self.skip_show = False
            return
        self.show_grid(ui)
        if self.nope:
            ui.print(f'no: {" ".join(sorted(let.upper() for let in self.nope))}')

    def show_grid(self, ui: PromptUI):
        for word_i in range(self.size):
            ui.write(f'#{word_i+1}  | ')
            for k in self.row_word_range(word_i):
                ui.write(f' {self.grid[k].upper() or "_"}')
            ui.write(f'  |  {" ".join(sorted(let.upper() for let in self.row_may[word_i]))}')
            ui.fin()

    def display(self, ui: PromptUI):
        if self.run_done:
            return self.finish

        self.show(ui)
        with ui.input(f'> ') as tokens:
            if tokens.have(r'\*'):
                self.skip_show = True
                return self.do_choose(ui)

            if tokens.have(r'(?x) ( ! | /n(o(pe?)?)? ) $'):
                for m in re.finditer(r'[A-Za-z]', tokens.rest):
                    self.nope.add(m.group(0).lower())
                ui.log(f'nope: {" ".join(sorted(self.nope))}')
                return

            if tokens.have(r'(?x) ( ! | /y(ep?)? ) $'):
                for m in re.finditer(r'[A-Za-z]', tokens.rest):
                    self.nope.remove(m.group(0).lower())
                ui.log(f'nope: {" ".join(sorted(self.nope))}')
                return

            if tokens.have(r'/g(u(e(s(s(es?)?)?)?)?)?'):
                for word in self.guesses:
                    ui.print(f'Guesses ({len(self.guesses)})')
                    ui.print(f'- {word}')
                return

            word_i = self.re_word_i(ui)
            if word_i is not None:
                if tokens.rest.strip() == '!':
                    self.forget(ui, word_i)
                    return

            word = next(tokens, None)
            if word:
                if len(word) == self.size:
                    return self.ask_question(ui, word, 'entered')
                ui.print(f'! wrong size {word!r}')
                return

    def row_word_range(self, row: int):
        return range(row * self.size, (row+1) * self.size)

    def col_word_range(self, col: int):
        return range(col, len(self.grid), self.size)

    def forget(self, ui: PromptUI, word_i: int):
        ui.log(f'forget: {word_i}')
        for j in self.row_word_range(word_i):
            self.grid[j] = ''
        self.row_may[word_i] = set()

    def finish(self, ui: PromptUI):
        res = self.result
        if not res:
            ui.print('Provide share result:')
            self.result_text = ui.may_paste()
            ui.log(f'result: {json.dumps(self.result_text)}')
            return

        raise StopIteration

    @override
    def review(self, ui: PromptUI):
        if not self.result_text:
            with (
                git_txn(f'{self.site} {self.puzzle_id} result fixup') as txn,
                txn.will_add(self.log_file),
                self.log_to(ui),
            ):
                try:
                    st = self.finish
                    while not self.result_text:
                        st = st(ui) or st
                except StopIteration:
                    pass

        self.show_grid(ui)
        with ui.input(f'> ') as tokens:
            if tokens.have(r'report$'):
                return self.do_report(ui)

    @property
    @override
    def report_desc(self) -> str:
        res = self.result
        guesses = res.guesses if res else '???'
        status = '🥳' if res else '😦'
        return  f'{status} {guesses} ⏱️ {self.elapsed}'

    @property
    @override
    def report_body(self) -> Generator[str]:
        yield from super().report_body

        yield ''
        yield 'Guesses:'
        for word, i in sorted(self.guesses.items(), key = lambda x: x[1]):
            yield f'{i+1}. {word}'

        res = self.result
        if res:
            yield ''
            yield 'Score Heatmap:'
            for row in res.score_rows:
                yield f'    {" ".join(row)}'
            yield f'    {res.legend_str}'

        yield ''
        yield 'Solution:'
        for word_i in range(self.size):
            lets = ' '.join(
                f'{self.grid[k].upper() or "_"}'
                for k in self.row_word_range(word_i))
            yield f'    {lets}'

    def proc_re_word(self, ui: PromptUI, word_i: int):
        with ui.tokens as tokens:
            match = self.re_word_match(ui)
            if match:
                return self.proc_re_word_match(ui, word_i, match)

    def re_word_match(self, ui: PromptUI):
        rest = ui.tokens.rest
        match = re.match(r'''(?x)
            \s* (?P<word> [_A-Za-z ]+ )
            (?: \s* ~ \s* (?P<may> [A-Za-z ]* ) )?
        ''', rest) or re.match(r'''(?x)
            (?P<word> )
            \s* ~ \s* (?P<may> [A-Za-z ]* )
        ''', rest)
        if match:
            ui.tokens.rest = rest[match.end(0):] 
        return match

    def proc_re_word_match(self, ui: PromptUI, word_i: int, match: re.Match[str]):
        word_str = cast(str, match.group(1) or '')
        may_str = cast(str|None, match.group(2))

        may = self.row_may[word_i]

        if word_str:
            lets = (c for c in word_str if c != ' ')
            offset = word_i * self.size
            for i, let in enumerate(lets):
                if i >= self.size:
                    ui.print('! too much input, truncating')
                    break
                c = let.lower()
                if let == '_':
                    self.grid[offset + i] = ''
                elif self.grid[offset + i] != c:
                    self.grid[offset + i] = c
                    if c in may: may.remove(c)

        if may_str is not None:
            may.clear()
            may.update(
                m.group(0).lower()
                for m in re.finditer(r'[A-Za-z]', may_str))

        ui.log(f'word: {word_i} {"".join(self.grid[k] or "_" for k in self.row_word_range(word_i))}')
        ui.log(f'may: {word_i} {" ".join(sorted(self.row_may[word_i]))}')

    def do_choose(self, ui: PromptUI) -> PromptUI.State|None:
        word_n = ui.tokens.have(r'\d+$', lambda m: int(m.group(0)))
        word_i = None
        choice = ''
        count = 0

        for word_i, _, choice, count in self.choose(ui, None if word_n is None else word_n-1):
            pass

        if not choice: return
        assert word_i is not None

        _, uni_count = self.pattern(row=word_i)
        return self.ask_question(ui, choice, f'#{word_i+1} found:{count} hypo:{uni_count}')

    def ask_question(self, ui: PromptUI, word: str, desc: str):
        word = word.lower()
        ui.log(f'questioning: {json.dumps([word, desc])}')
        self.qmode = '>' if word in self.guesses else  '?'
        self.questioning = word
        self.question_desc = desc
        return self.question

    def question(self, ui: PromptUI):
        q = self.qmode
        word = self.questioning.lower()
        desc = self.question_desc
        prompt = f'{word} ( {desc} )' if desc else f'{word}'

        ui.copy(word)

        self.show(ui)
        with ui.input(f'{prompt} {q} ') as tokens:
            if tokens.empty:
                self.question_done(ui)
                return self.display

            if q == '?':
                if tokens.rest.strip() == '!':
                    self.question_reject(ui, word)
                    return self.display
                if tokens.rest.strip() == '.':
                    return self.question_guess(ui, word)

                word_i = self.re_word_i(ui)
                if word_i is not None:
                    match = self.re_word_match(ui)
                    if match:
                        self.question_guess(ui, word)
                        return self.proc_re_word_match(ui, word_i, match)

            elif q == '>':
                word_i = self.re_word_i(ui)
                if word_i is not None:
                    return self.proc_re_word(ui, word_i)
                return

            else:
                raise RuntimeError(f'invalid qmode:{q!r}')

    def re_word_i(self, ui: PromptUI):
        n = ui.tokens.have(r'(\d+):?', lambda m: int(m.group(1)))
        if n is not None:
            word_i = n - 1
            return word_i if 0 <= word_i < self.size else None

    def question_guess(self, ui: PromptUI, word: str):
        ui.log(f'guess: {word}')
        self.qmode = '>'
        if word not in self.guesses:
            self.guesses[word] = len(self.guesses)

    def question_reject(self, ui: PromptUI, word: str):
        ui.log(f'reject: {word}')
        self.rejects.add(word.lower())
        self.questioning = ''
        self.question_desc = ''

    def question_done(self, ui: PromptUI):
        ui.log('question done')
        self.qmode = '?'
        self.questioning = ''
        self.question_desc = ''

from dataclasses import dataclass
@dataclass
class Result:
    size: int
    site: str
    puzzle_id: str
    guesses: int
    scores: list[int] # NOTE actually a size,size shaped matrix
    legend: dict[int, str]
    trailer: str

    score_marks: tuple[tuple[str, int], ...] = (
        ('🟥', 1),
        ('🟧', 2),
        ('🟨', 3),
        ('🟩', 4),
    )

    @property
    def legend_str(self):
        rev = {score: mark for mark, score in self.score_marks}
        return ' '.join(
            f'{rev[score]}:{desc}'
            for score, desc in sorted(self.legend.items(), reverse=True)
        )

    @property
    def score_rows(self):
        rev = {score: mark for mark, score in self.score_marks}
        for offset in range(0, len(self.scores), self.size):
            yield tuple(
                rev[self.scores[k]]
                for k in range(offset, offset+self.size))

    @classmethod
    def parse(cls, s: str, size: int):
        lines = PeekStr(spliterate(s, '\n', trim=True))

        match = lines.have(r'''(?x)
            (?P<site> [^\s]+ )
            \s+ (?P<id> [^\s]+ )
            :
            \s+ (?P<guesses> \d+ )
            \s+ guesses
            $
        ''')
        if not match:
            raise ValueError('first line should have site/puzzle id and guess count')
        site, puzzle_id, gs = match.groups()
        guesses = int(gs)


        scores: list[int] = [0 for _ in range(size*size)]

        fwd = {mark: score for mark, score in cls.score_marks}

        if lines.have(r'\s*$'):
            offset: int = 0
            for line in lines:
                if not line.strip(): break

                if len(line) != size:
                    raise ValueError(f'invalid grid line, expected {size} characters got {len(line)}')

                if any(x not in fwd for x in line):
                    bad = [f'{x!r}' for x in line if x not in fwd]
                    raise ValueError(f'invalid grid line marks: {bad!r}')

                assert offset < len(scores)
                for c in line:
                    scores[offset] = fwd[c]
                    offset += 1

            if offset < len(scores):
                raise ValueError('short grid score table')

        legend: dict[int, str] = dict()
        for match in re.finditer(
            r'(?x) \s* ( < \d+ | \d+ \+? ) : ( [🟥🟧🟨🟩] )',
            next(lines, '')):
            desc, mark = match.groups()
            score = fwd[mark]
            legend[score] = desc
        if not all(score in legend for score in fwd.values()):
            raise ValueError('incomplete legend')

        trailer = '\n'.join(lines)

        return cls(
            size,
            site, puzzle_id, guesses,
            scores, legend, trailer
        )

import pytest

@pytest.mark.parametrize('spec', [
    '''
    > squareword.org 1031: 17 guesses
    >
    > 🟧🟨🟨🟨🟨
    > 🟩🟨🟩🟨🟩
    > 🟨🟧🟧🟩🟨
    > 🟨🟨🟨🟨🟨
    > 🟥🟨🟥🟥🟩
    >
    > <6:🟩 <11:🟨 <16:🟧 16+:🟥
    > #squareword #squareword1031
    - size: 5
    - site: squareword.org
    - puzzle_id: 1031
    - guesses: 17
    - scores: [
        2, 3, 3, 3, 3,
        4, 3, 4, 3, 4,
        3, 2, 2, 4, 3,
        3, 3, 3, 3, 3,
        1, 3, 1, 1, 4
      ]
    - legend: [ [4, "<6"], [3, "<11"], [2, "<16"], [1, "16+"] ]
    - trailer: ```
      #squareword #squareword1031
      ```
    ''',
], ids=['first_solve'])
def test_parse_result(spec: str):
    ts = MarkedSpec(spec)

    size = 0
    expect_site: str|None = None
    expect_puzzle_id: str|None = None
    expect_guesses: int|None = None
    expect_scores: list[int]|None = None
    expect_legend: dict[int, str]|None = None
    expect_trailer: str|None = None

    for key, value in ts.props:
        if key == 'size': size = int(value)
        elif key == 'site': expect_site = value
        elif key == 'puzzle_id': expect_puzzle_id = value
        elif key == 'guesses': expect_guesses = int(value)
        elif key == 'scores':
            val = cast(object, json.loads(value))
            assert isinstance(val, list)
            assert all(isinstance(x, int) for x in cast(list[object], val))
            expect_scores = val
        elif key == 'legend':
            val = cast(object, json.loads(value))
            assert isinstance(val, list)
            assert all(isinstance(x, list) for x in cast(list[object], val))
            assert all(len(x) == 2 for x in cast(list[list[object]], val))
            assert all(isinstance(k, int) and isinstance(v, str) for k, v in cast(list[list[object]], val))
            expect_legend = dict(
                (cast(int, k), cast(str, v))
                for k, v in cast(list[list[object]], val))
        elif key == 'trailer':
            expect_trailer = value
        else: raise ValueError(r'unknown spec key {key!r}')

    ts.assert_no_trailer()

    res = Result.parse(ts.input, size)

    if expect_site is not None: assert res.site == expect_site
    if expect_puzzle_id is not None: assert res.puzzle_id == expect_puzzle_id
    if expect_guesses is not None: assert res.guesses == expect_guesses
    if expect_scores is not None: assert res.scores == expect_scores
    if expect_legend is not None: assert res.legend == expect_legend
    if expect_trailer is not None: assert res.trailer == expect_trailer

if __name__ == '__main__':
    Search.main()
