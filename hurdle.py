#!/usr/bin/env python

import argparse
import heapq
import json
import math
import random
import re
from collections import Counter
from collections.abc import Generator, Iterable
from dataclasses import dataclass
from typing import cast, final, override

from strkit import spliterate
from ui import PromptUI
from store import StoredLog

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
    @override
    def add_args(self, parser: argparse.ArgumentParser):
        super().add_args(parser)
        _ = parser.add_argument('--wordlist', default=self.default_wordlist)

    @override
    def from_args(self, args: argparse.Namespace):
        super().from_args(args)
        self.default_wordlist = cast(str, args.wordlist)

    log_file: str = 'hurdle.log'
    default_site: str = 'https://play.dictionary.com/games/todays-hurdle'
    default_wordlist: str = '/usr/share/dict/words'
    site_name: str = 'dictionary.com hurdle'

    def __init__(self):
        super().__init__()

        self.size: int = 5
        self.wordlist: str = ''

        self.may_letters: set[str] = set()
        self.nope_letters: set[str] = set()
        self.word: list[str] = ['' for _ in range(self.size)]
        self.tried: list[str] = []
        self.words: list[str] = []

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
            self.puzzle_id = f'#{res.puzzle_id}'
        return self._result

    @override
    def load(self, ui: PromptUI, lines: Iterable[str]):
        for t, rest in super().load(ui, lines):
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
                nope : (?: \s+ ( \w+ ) )?
                \s* ( .* )
                $''', rest)
            if match:
                nope, rest = match.groups()
                assert rest == ''
                self.nope_letters = set(nope or '')
                continue

            match = re.match(r'''(?x)
                may : (?: \s+ ( \w+ ) )?
                \s* ( .* )
                $''', rest)
            if match:
                may, rest = match.groups()
                assert rest == ''
                self.may_letters = set(may or '')
                continue

            match = re.match(r'''(?x)
                tried : \s+ ( [\w_]+ )
                \s* ( .* )
                $''', rest)
            if match:
                word, rest = match.groups()
                assert rest == ''
                self.tried.append(word)
                continue

            match = re.match(r'''(?x)
                word : \s+ ( [\w_]+ )
                \s* ( .* )
                $''', rest)
            if match:
                word, rest = match.groups()
                assert rest == ''
                self.word = [
                    '' if x == '_' else x.lower()
                    for x in word
                ]
                if all(x for x in self.word):
                    self.words.append(''.join(self.word))
                    self.tried.clear()
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

    @override
    def startup(self, ui: PromptUI):
        if not self.wordlist:
            with ui.input(f'📜 {self.default_wordlist} ? ') as tokens:
                self.wordlist = next(tokens, self.default_wordlist)
                ui.log(f'wordlist: {self.wordlist}')

        return self.display

    @property
    @override
    def run_done(self) -> bool:
        if self.result is not None: return True
        return len(self.words) >= self.size

    def display(self, ui: PromptUI):
        if self.run_done:
            raise StopIteration

        if len(self.words) >= self.size:
            return self.finish

        if self.nope_letters:
            ui.print(f'No: {" ".join(x.upper() for x in sorted(self.nope_letters))}')

        if self.may_letters:
            ui.print(f'May: {" ".join(x.upper() for x in sorted(self.may_letters))}')

        if self.word:
            ui.print(f'Word: {" ".join(x.upper() if x else "_" for x in self.word)}')

        with ui.input(f'{len(self.words)+1}.{len(self.tried)+1}> ') as tokens:
            if tokens.have(r'\*'):
                return self.guess(ui)

            if tokens.have(r'fail'):
                self.result_text = ui.paste()
                ui.log(f'result: {json.dumps(self.result_text)}')
                if self.result is None:
                    try:
                        _ = Result.parse(self.result_text, self.size)
                    except ValueError as err:
                        ui.print(f'! invalid result string: {err}')
                    self.result_text = ''
                return

            if tokens.have(r'tried'):
                word = next(tokens, None)
                if word is not None:
                    ui.log(f'tried: {word}')
                    self.tried.append(word)
                return

            if tokens.have(r'no'):
                nop: set[str] = set()

                some = False

                for tok in tokens:
                    if tok.startswith('.'):
                        tok = tok[1:]
                        self.nope_letters = set()
                        some = True
                    nop.update(tok)

                some = some or any(x not in self.nope_letters for x in nop)
                some_may = any(x in self.may_letters for x in nop)
                some_word = any(x in self.word for x in nop)

                self.nope_letters.update(nop)
                self.may_letters.difference_update(nop)
                self.word = ['_' if x in self.nope_letters else x for x in self.word]

                if some:
                    ui.log(f'nope: {"".join(sorted(self.nope_letters))}')
                if some_may:
                    ui.log(f'may: {"".join(sorted(self.may_letters))}')
                if some_word:
                    ui.log(f'word: {"".join(x if x else "_" for x in self.word)}')
                return

            if tokens.have(r'may'):
                some = False
                for tok in tokens:
                    if tok.startswith('.'):
                        tok = tok[1:]
                        self.may_letters = set()
                    self.may_letters.update(tok)
                    some = True
                if some:
                    ui.log(f'may: {"".join(sorted(self.may_letters))}')
                return

            if tokens.have(r'word'):
                lets = next(tokens, None)
                if lets is not None:
                    word = lets.lower()[:self.size]
                    self.word = ['' if x == '_' else x for x in word]
                    ui.log(f'word: {"".join(x if x else "_" for x in self.word)}')
                    if all(x for x in self.word):
                        self.words.append(''.join(self.word))
                        self.tried.clear()
                return

            ui.print(f'unknown input: {tokens.raw!r}')

    def pattern(self, _ui: PromptUI):
        alpha = set('abcdefghjiklmnopqrstuvwxyz')
        uni = '.'

        if self.nope_letters:
            alpha.difference_update(self.nope_letters)
            uni = f'[{"".join(char_ranges(alpha))}]'

        if not self.may_letters:
            pat = ''.join(x if x else uni for x in self.word)
            # ui.print(f'PATTERN {pat!r}')
            return pat

        def alts():
            from itertools import combinations, permutations
            may = sorted(self.may_letters)
            ix = [i for i in range(len(self.word)) if not self.word[i]]
            for mix in combinations(ix, len(may)):
                parts = [uni if not let else let for let in self.word]
                for pmay in permutations(may):
                    for j, i in enumerate(mix):
                        parts[i] = pmay[j]
                    pat = ''.join(parts)
                    # ui.print(f'PATTERN | {pat!r}')
                    yield pat

        return '|'.join(alts())

    def guess(self, ui: PromptUI):
        words = sorted(word for _, word in self.select(ui, 10))
        for n, word in enumerate(words, 1):
            ui.print(f'{n}. {word}')

    def select(self, ui: PromptUI, topn: int):
        choices: list[tuple[float, str]] = []

        pattern = self.pattern(ui)

        for word in self.find(re.compile(pattern)):
            score = random.random()

            for i, let in enumerate(word):
                if let not in self.may_letters: continue
                if any(prior[i] == let for prior in self.tried): 
                    score = 0
                    break

            if score > 0:
                lc = Counter(word)
                n = sum(lc.values())
                m = n/len(lc)
                v = sum((v - m)**2 for v in lc.values())
                score = math.pow(score, 0.01 + v)

            choice = (score, word)
            if len(choices) < topn:
                heapq.heappush(choices, choice)
            elif choice > choices[0]:
                choice = heapq.heapreplace(choices, choice)

        while choices:
            yield heapq.heappop(choices)

    def find(self, pattern: re.Pattern[str]):
        with open(self.wordlist) as f:
            for line in f:
                line = line.strip().lower()
                word = line.partition(' ')[0]
                word = word.lower()
                if pattern.fullmatch(word): yield word

    def finish(self, ui: PromptUI):
        res = self.result
        if not res:
            if self.result_text:
                self.result_text = ''
            with ui.input('Copy share result and press <Enter>'):
                self.result_text = ui.paste()
                ui.log(f'result: {json.dumps(self.result_text)}')
            return

        if not self.puzzle_id:
            self.puzzle_id = f'#{res.puzzle_id}'
            ui.log(f'puzzle_id: {self.puzzle_id}')

        if not self.stored:
            raise StopIteration

        return self.review

    @override
    def review(self, ui: PromptUI):
        if not self.puzzle_id:
            res = self.result
            if res: self.puzzle_id = f'#{res.puzzle_id}'

        return super().review(ui)

    @override
    def info(self) -> Generator[str]:
        res = self.result
        yield from super().info()
        yield f'💰 score: {res.score if res else 0}'

    @property
    @override
    def report_desc(self) -> str:
        res = self.result
        guesses = len(res.records) if res else 0
        status = '🥳' if res and res.found else '😦'
        return  f'{status} {guesses} ⏱️ {self.elapsed}'

    @property
    @override
    def report_body(self) -> Generator[str]:
        yield from super().report_body

        res = self.result
        if not res: return

        recs = iter(res.records)
        for rnd in res.rounds:
            if rnd.note:
                yield f'{rnd.note} {rnd.took}/{rnd.limit}'
            else:
                yield f'{rnd.took}/{rnd.limit}'
            for _ in range(rnd.took):
                rec = next(recs)
                yield ''.join(Result.marks[i] for i in rec)

@final
@dataclass
class Result:
    marks = ('⬜', '🟨', '🟩')

    @final
    @dataclass
    class Round:
        note: str
        took: int
        limit: int

    puzzle_id: int
    size: int
    score: int
    rounds: tuple[Round, ...]            # each round
    records: tuple[tuple[int, ...], ...] # comes with took-many records

    @property
    def found(self):
        return all(x == 2 for x in self.records[-1])

    @classmethod
    def parse(cls, s: str, size: int):
        puzzle_id: int|None = None
        score: int = 0
        rounds: list[Result.Round] = []
        records: list[tuple[int, ...]] = []

        lines = spliterate(s, '\n')
        for line in lines:

            match = re.match(r'(?x) Hurdle \s+ ( \d+ )', line)
            if match:
                puzzle_id = int(match.group(1))
                continue

            match = re.match(r'(?x) score : \s+ ( [\d,]+ )', line)
            if match:
                score = int(match.group(1).replace(',', ''))
                continue

            match = re.match(r'(?x) (?: ( \w+ ) \s+ )? ( \d+ | X ) / ( \d+ )', line)
            if match:
                note = cast(str, match.group(1) or '')
                tooks = match.group(2)
                limit = int(match.group(3))
                took = limit if tooks == 'X' else int(tooks)
                for i in range(took):
                    row = next(lines, None)
                    if row is None:
                        raise ValueError(f'missing record row for round {len(rounds)+1}')
                    try:
                        record = tuple(cls.marks.index(mark) for mark in row)
                    except IndexError:
                        raise ValueError(f'invalid record row for round {len(rounds)+1}')
                    records.append(record)
                rounds.append(cls.Round(note, took, limit))
                continue

        if puzzle_id is None:
            raise ValueError('missing hurdle puzzle id')

        return cls(
            puzzle_id, size,
            score,
            tuple(rounds),
            tuple(records)
        )

from strkit import MarkedSpec

@MarkedSpec.mark('''

    #1069
    > Hurdle 1069
    > 
    > 4/6
    > ⬜⬜🟩🟨⬜
    > ⬜⬜🟩⬜🟨
    > 🟩🟩🟩🟩⬜
    > 🟩🟩🟩🟩🟩
    > 4/6
    > 🟩⬜🟨⬜⬜
    > 🟩🟨⬜⬜🟨
    > 🟩🟨🟩🟨⬜
    > 🟩🟩🟩🟩🟩
    > 4/6
    > ⬜⬜⬜⬜⬜
    > ⬜🟨⬜🟨🟨
    > 🟨🟨🟨🟨⬜
    > 🟩🟩🟩🟩🟩
    > 5/6
    > ⬜🟨⬜⬜🟨
    > ⬜⬜🟨🟨⬜
    > 🟨⬜🟨🟨🟨
    > ⬜🟨🟩🟨🟩
    > 🟩🟩🟩🟩🟩
    > Final 2/2
    > ⬜🟩🟨🟨⬜
    > 🟩🟩🟩🟩🟩
    > score: 9,700
    - size: 5
    - score: 9700
    - found: True
    - round: Result.Round(note='', took=4, limit=6)
    - record: (0, 0, 2, 1, 0)
    - record: (0, 0, 2, 0, 1)
    - record: (2, 2, 2, 2, 0)
    - record: (2, 2, 2, 2, 2)
    - round: Result.Round(note='', took=4, limit=6)
    - record: (2, 0, 1, 0, 0)
    - record: (2, 1, 0, 0, 1)
    - record: (2, 1, 2, 1, 0)
    - record: (2, 2, 2, 2, 2)
    - round: Result.Round(note='', took=4, limit=6)
    - record: (0, 0, 0, 0, 0)
    - record: (0, 1, 0, 1, 1)
    - record: (1, 1, 1, 1, 0)
    - record: (2, 2, 2, 2, 2)
    - round: Result.Round(note='', took=5, limit=6)
    - record: (0, 1, 0, 0, 1)
    - record: (0, 0, 1, 1, 0)
    - record: (1, 0, 1, 1, 1)
    - record: (0, 1, 2, 1, 2)
    - record: (2, 2, 2, 2, 2)
    - round: Result.Round(note='Final', took=2, limit=2)
    - record: (0, 2, 1, 1, 0)
    - record: (2, 2, 2, 2, 2)

    #1072
    > Hurdle 1072
    > 
    > 5/6
    > ⬜⬜⬜⬜⬜
    > ⬜🟨⬜🟨🟨
    > ⬜🟨🟨⬜🟨
    > 🟨⬜⬜🟩🟩
    > 🟩🟩🟩🟩🟩
    > 4/6
    > ⬜⬜🟨⬜🟨
    > ⬜⬜⬜🟨🟩
    > 🟩⬜🟨🟩🟩
    > 🟩🟩🟩🟩🟩
    > 5/6
    > ⬜⬜⬜⬜⬜
    > 🟨⬜🟨⬜⬜
    > 🟩🟨⬜🟨⬜
    > 🟩🟩🟩🟩⬜
    > 🟩🟩🟩🟩🟩
    > 6/6
    > ⬜🟨⬜⬜🟩
    > ⬜⬜🟩⬜🟩
    > 🟩⬜🟩⬜🟩
    > 🟩🟩🟩⬜🟩
    > 🟩🟩🟩⬜🟩
    > 🟩🟩🟩🟩🟩
    > Final X/2
    > ⬜⬜🟨🟩🟨
    > 🟨⬜🟨🟩⬜
    > score: 4,440
    - size: 5
    - score: 4440
    - found: False
    - round: Result.Round(note='', took=5, limit=6)
    - record: (0, 0, 0, 0, 0)
    - record: (0, 1, 0, 1, 1)
    - record: (0, 1, 1, 0, 1)
    - record: (1, 0, 0, 2, 2)
    - record: (2, 2, 2, 2, 2)
    - round: Result.Round(note='', took=4, limit=6)
    - record: (0, 0, 1, 0, 1)
    - record: (0, 0, 0, 1, 2)
    - record: (2, 0, 1, 2, 2)
    - record: (2, 2, 2, 2, 2)
    - round: Result.Round(note='', took=5, limit=6)
    - record: (0, 0, 0, 0, 0)
    - record: (1, 0, 1, 0, 0)
    - record: (2, 1, 0, 1, 0)
    - record: (2, 2, 2, 2, 0)
    - record: (2, 2, 2, 2, 2)
    - round: Result.Round(note='', took=6, limit=6)
    - record: (0, 1, 0, 0, 2)
    - record: (0, 0, 2, 0, 2)
    - record: (2, 0, 2, 0, 2)
    - record: (2, 2, 2, 0, 2)
    - record: (2, 2, 2, 0, 2)
    - record: (2, 2, 2, 2, 2)
    - round: Result.Round(note='Final', took=2, limit=2)
    - record: (0, 0, 1, 2, 1)
    - record: (1, 0, 1, 2, 0)

''')
def test_result_parse(spec: MarkedSpec):
    size: int = 0
    for name, value in spec.props:
        if name == 'size': size = int(value)
    res = Result.parse(spec.input, size)
    round_i = 0
    record_i = 0
    for name, value in spec.props:
        if name == 'puzzle_id': assert str(res.puzzle_id) == value
        elif name == 'score': assert str(res.score) == value
        elif name == 'round':
            assert repr(res.rounds[round_i]) == value, f'rounds[{round_i}]'
            round_i += 1
        elif name == 'record':
            assert repr(res.records[record_i]) == value, f'records[{record_i}]'
            record_i += 1
        elif name == 'found': assert str(res.found) == value
    assert round_i == len(res.rounds)
    assert record_i == len(res.records)

if __name__ == '__main__':
    Search.main()
