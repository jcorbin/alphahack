#!/usr/bin/env python

import argparse
import json
import re
from collections.abc import Generator, Iterable, Sequence
from dataclasses import dataclass
from os import path
from typing import cast, final, override

from sortem import Chooser, DiagScores, Possible, RandScores
from strkit import spliterate, PeekIter
from ui import PromptUI
from store import StoredLog, atomic_rewrite, git_txn

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
        wordlist = cast(str, args.wordlist)
        if wordlist:
            self.default_wordlist = wordlist
            self.wordlist = wordlist

    log_file: str = 'hurdle.log'
    default_site: str = 'https://play.dictionary.com/games/todays-hurdle'
    default_wordlist: str = '/usr/share/dict/words'
    site_name: str = 'dictionary.com hurdle'

    def __init__(self):
        super().__init__()

        self.debug = 0

        self.size: int = 5
        self.wordlist: str = ''
        self.given_wordlist: bool = False

        self.may_letters: set[str] = set()
        self.nope_letters: set[str] = set()
        self.word: list[str] = ['' for _ in range(self.size)]
        self.tried: list[str] = []
        self.attempts: list[list[str]] = []
        self.words: list[str] = []

        self.failed: bool = False
        self.fail_text: str = ''

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

    @result.deleter
    def result(self):
        self._result = None
        self.result_text = ''

    @override
    def load(self, ui: PromptUI, lines: Iterable[str]):
        for t, rest in super().load(ui, lines):
            orig_rest = rest
            with ui.exc_print(lambda: f'while loading {orig_rest!r}'):

                match = re.match(r'''(?x)
                    fail :
                    \s+
                    (?P<rest> .* )
                    $''', rest)
                if match:
                    rest, = match.groups()
                    self.failed = True
                    self.fail_text = rest
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
                    self.given_wordlist = True
                    continue

                match = re.match(r'''(?x)
                    nope : (?: \s+ ( [^\s]+ ) )?
                    \s* ( .* )
                    $''', rest)
                if match:
                    nope, rest = match.groups()
                    assert rest == ''
                    self.nope_letters = set(nope or '')
                    continue

                match = re.match(r'''(?x)
                    may : (?: \s+ ( [^\s]+ ) )?
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
                    word : \s+ ( [^\s]+ )
                    \s* ( .* )
                    $''', rest)
                if match:
                    word, rest = match.groups()
                    assert rest == ''
                    self.update_word(ui, word)
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
            if not self.wordlist:
                return

        if not self.given_wordlist:
            self.given_wordlist = True
            ui.log(f'wordlist: {self.wordlist}')

        return self.display

    @property
    @override
    def run_done(self) -> bool:
        if self.failed: return True
        elif self.fail_text:
            self.failed = True
            return True
        if self.result is not None: return True
        return False

    def display(self, ui: PromptUI):
        if self.run_done or len(self.words) >= self.size:
            return self.finish

        if self.nope_letters:
            ui.print(f'No: {" ".join(x.upper() for x in sorted(self.nope_letters))}')

        if self.may_letters:
            ui.print(f'May: {" ".join(x.upper() for x in sorted(self.may_letters))}')

        if self.word:
            ui.print(f'Word: {" ".join(x.upper() if x else "_" for x in self.word)}')

        with ui.input(f'{len(self.words)+1}.{len(self.tried)+1}> ') as tokens:
            match = tokens.have(r'(\*+)(\d+)?')
            if match:
                guess = int(match.group(2)) if match.group(2) else 0 if len(match.group(1)) > 1 else 10
                return self.guess(ui, show_n=guess)

            if tokens.have(r'fail'):
                self.failed = True
                self.fail_text = tokens.rest
                ui.log('fail: {self.fail_text}')
                return self.finish

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
                if not tokens.empty:
                    self.update_word(ui, next(tokens))
                return

            ui.print(f'unknown input: {tokens.raw!r}')

    def update_word(self, ui: PromptUI, word: str):
        word = word.lower()
        for i, x in enumerate(word[:self.size]):
            self.word[i] = '' if x == '_' else x

        word = ''.join(x if x else '_' for x in self.word)
        ui.log(f'word: {word}')

        if all(x for x in self.word):
            if word not in self.tried:
                self.tried.append(word)
            self.words.append(word)
            self.attempts.append(self.tried)
            self.reset_word()

    def reset_word(self):
        for i in range(self.size): self.word[i] = ''
        self.tried = []
        self.nope_letters = set()
        self.may_letters = set()

    def describe_space(self):
        def parts():
            word = ''.join(l if l else '_' for l in self.word).upper()
            yield f'{word}'
            if self.may_letters:
                may = ''.join(self.may_letters).upper()
                yield f'may: {may}'
            if self.nope_letters:
                nope = ''.join(self.nope_letters).upper()
                yield f'nope: {nope}'
        return ' '.join(parts())

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

    def guess(self, ui: PromptUI, show_n: int=10):
        verbose = 0
        jitter = 0.5
        chooser = Chooser(show_n=show_n)

        while ui.tokens:
            if chooser.collect(ui.tokens):
                continue

            match = ui.tokens.have(r'-(v+)')
            if match:
                verbose += len(match.group(1))
                continue

            if ui.tokens.have(r'-j(itter)?'):
                n = ui.tokens.have(r'\d+(?:\.\d+)?', lambda match: float(match[0]))
                if n is not None:
                    if n < 0:
                        jitter = 0
                        ui.print('! clamped -jitter value to 0')
                    elif n > 1:
                        jitter = 1
                        ui.print('! clamped -jitter value to 1')
                    else:
                        jitter = n
                else:
                    ui.print('! -jitter expected value')
                continue

            ui.print(f'! invalid * arg {next(ui.tokens)!r}')
            return

        words = set(self.find(re.compile(self.pattern(ui))))

        # drop any words that intersect tried prior letters
        tried_words = [
            (wi, word)
            for wi, word in enumerate(words)
            if any(
                not self.word[li]
                for _, _, li in self.tried_letters(word))]
        skip_words = set(word for _, word in tried_words)
        words.difference_update(skip_words)
        if skip_words:
            if self.debug > 1:
                ui.log(f'skip ∩tried remain:{len(words)} dropped:{len(skip_words)} -- {sorted(skip_words)!r}')
            if verbose:
                ui.print(f'- pruned {len(skip_words)} words based on priors')
                if verbose > 1:
                    for i, word in tried_words:
                        ui.print(f'  {i+1}. {word}')
                        for let, j, i in self.tried_letters(word):
                            if not self.word[i]:
                                ui.print(f'    - {let.upper()} from {self.tried[j]!r}[{i}]')

        pos = Possible(
            sorted(words),
            lambda words: self.select(ui, words, jitter=jitter),
            choices=chooser.choices,
            verbose=verbose)

        def parts():
            yield f'{pos} from {self.describe_space()}'
            if tried_words:
                yield f'less ∩tried {len(tried_words)}'

        ui.print(' '.join(parts()))
        for line in pos.show_list():
            ui.print(line)

        if not pos.data and tried_words:
            ui.print('; maybe reconsider:')
            for i, word in tried_words:
                ui.print(f'{i+1}. {word}')

    def tried_letters(self, word: str):
        for i, let in enumerate(word):
            if let not in self.may_letters: continue
            for j, prior in enumerate(self.tried):
                if prior[i] == let:
                    yield let, j, i

    def select(self, _ui: PromptUI, words: Sequence[str], jitter: float = 0.5):
        diag = DiagScores(words)
        rand = None if jitter == 0 else RandScores(diag.scores, jitter=jitter)
        scores = diag.scores if rand is None else rand.scores
        def annotate(i: int) -> Generator[str]:
            if rand is not None:
                yield from rand.explain(i)
            yield from diag.explain(i)
            wf_parts = list(diag.explain_wf(i))
            if wf_parts:
                yield f'WF:{" ".join(wf_parts)}'
            yield f'LF:{" ".join(diag.explain_lf(i))}'
            yield f'LF norm:{" ".join(diag.explain_lf_norm(i))}'
        return scores, annotate

    def find(self, pattern: re.Pattern[str]):
        with open(self.wordlist) as f:
            for line in f:
                line = line.strip().lower()
                word = line.partition(' ')[0]
                word = word.lower()
                if pattern.fullmatch(word): yield word

    def check_fail_text(self, ui: PromptUI):
        try:
            word = self.fail_text.strip().split()[0]
        except IndexError:
            return
        if not word:
            return

        if len(word) != self.size:
            ui.print(f'! invalid fail word:{word!r} length:{len(word)} ; expected {self.size}')
            return

        if any(self.find(re.compile(re.escape(word)))):
            ui.print(f'ℹ️ fail word {word!r} already in list')
            return

        with git_txn(f'{path.basename(self.wordlist)}: add missing {word!r}') as txn:
            with (
                txn.will_add(self.wordlist),
                atomic_rewrite(self.wordlist) as (fr, fw)):
                for line in fr:
                    if line.lower() > word:
                        _ = fw.write(f'{word}\n')
                        _ = fw.write(line)
                        break
                    _ = fw.write(line)
                fw.writelines(fr)
            txn.commit()
            ui.write(f'🗃️ {self.wordlist} added {word!r}')

    def finish(self, ui: PromptUI):
        self.check_fail_text(ui)

        res = self.result
        if res:
            if not res.puzzle_id:
                del self.result
                return
            self.puzzle_id = f'#{res.puzzle_id}'
            ui.log(f'puzzle_id: {self.puzzle_id}')
            raise StopIteration

        ui.print('Provide share result:')
        self.result_text = ui.may_paste()
        ui.log(f'result: {json.dumps(self.result_text)}')

    @override
    def review(self, ui: PromptUI):
        # TODO common store result fixup routine
        if not self.result:
            with (
                git_txn(f'{self.site} {self.puzzle_id} result fixup') as txn,
                txn.will_add(self.log_file),
                self.log_to(ui),

            ):
                ui.interact(self.finish)
            return

        self.check_fail_text(ui)

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

        def history() -> Generator[tuple[str, bool|None]]:
            priors: set[str] = set()
            for i, word in enumerate(self.words):
                last: str = ''
                for w in self.attempts[i]:
                    if last:
                        yield last, last in priors
                    last = w
                if last and last != word:
                    yield last, last in priors
                yield word, None
                priors.add(word)
            if self.tried:
                for w in self.tried:
                    yield w, w in priors

        hist = PeekIter(enumerate(history(), 1))

        res = self.result
        if res:

            yield ''

            recs = iter(res.records)
            for rnd in res.rounds:
                if rnd.note:
                    yield f'    {rnd.note} {rnd.took}/{rnd.limit}'
                else:
                    yield f'    {rnd.took}/{rnd.limit}'

                if rnd.note.lower() == 'final':
                    for _, (_, kind) in hist:
                        if kind is not True: break

                for _ in range(rnd.took):
                    rec = next(recs)
                    for _, (word, kind) in hist:
                        if kind is not True:
                            yield f'    > {" ".join(word.upper())}'
                            break
                    yield f'      {"".join(Result.marks[i] for i in rec)}'

        if hist.peek() is not None:
            yield ''
            for n, (word, kind) in hist:
                yield f'{n}. {word} {"it" if kind is None else "prior" if kind is True else ""}'

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
                for _ in range(took):
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
