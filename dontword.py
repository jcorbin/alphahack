#!/usr/bin/env python

import argparse
import json
import re
from collections.abc import Generator, Iterable, Sequence
from dataclasses import dataclass
from os import path
from typing import cast, final, override

from sortem import Chooser, DiagScores, Possible, RandScores
from store import StoredLog, git_txn
from strkit import spliterate
from ui import PromptUI
from wordlist import WordList

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
class DontWord(StoredLog):
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
            self.wordlist_file = wordlist

    log_file: str = 'dontword.log'
    default_site: str = 'dontwordle.com'
    default_wordlist: str = '/usr/share/dict/words'

    def __init__(self):
        super().__init__()

        self.size: int = 5
        self.wordlist_file: str = ''
        self.given_wordlist: bool = False
        self._wordlist: WordList|None = None

        self.may_letters: set[str] = set()
        self.nope_letters: set[str] = set()
        self.word: list[str] = ['' for _ in range(self.size)]
        self.tried: list[str] = []

        self.failed: bool = False
        self.fail_text: str = ''

        self.result_text: str = ''
        self._result: Result|None = None

        self.play_prompt = PromptUI.Prompt(self.play_prompt_mess, {
            'fail': self.do_fail,
            'guess': self.do_guess,
            'may': self.do_may,
            'no': self.do_no,
            'tried': self.do_tried,
            'undo': self.do_undo,
            'word': self.do_word,
            '*': 'guess',
        })

    @property
    def wordlist(self):
        if self._wordlist is not None:
            if self._wordlist.name != self.wordlist_file:
                self._wordlist = None
        if self._wordlist is None:
            self._wordlist = WordList(
                self.wordlist_file,
                exclude_suffix='.dontword_exclude.txt')
        return self._wordlist

    @property
    def result(self):
        if self._result is None and self.result_text:
            try:
                res = Result.parse(self.result_text)
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
                    self.wordlist_file = wordlist
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
                    undo
                    \s* ( .* )
                    $''', rest)
                if match:
                    rest = match[1]
                    assert rest == ''
                    self.tried = self.tried[:-1]
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
        if not self.wordlist_file:
            with ui.input(f'📜 {self.default_wordlist} ? ') as tokens:
                self.wordlist_file = next(tokens, self.default_wordlist)
            if not self.wordlist_file:
                return

        if not self.given_wordlist:
            self.given_wordlist = True
            ui.log(f'wordlist: {self.wordlist_file}')

        return self.play

    @property
    @override
    def run_done(self) -> bool:
        if self.result is not None: return True
        if self.failed: return True
        elif self.fail_text:
            self.failed = True
            return True
        return False

    def play_prompt_mess(self, ui: PromptUI):
        if self.play_prompt.re == 0:
            if self.nope_letters:
                ui.print(f'No: {" ".join(x.upper() for x in sorted(self.nope_letters))}')
            if self.may_letters:
                ui.print(f'May: {" ".join(x.upper() for x in sorted(self.may_letters))}')
            if self.word:
                ui.print(f'Word: {" ".join(x.upper() if x else "_" for x in self.word)}')
        return f'{len(self.tried)+1}> '

    def play(self, ui: PromptUI):
        if self.run_done: return self.finish
        if all(self.word): return self.finish
        if len(self.tried) >= 6: return self.finish
        return self.play_prompt(ui)

    def do_undo(self, ui: PromptUI):
        '''
        rollback last `tried <word>`
        '''
        if len(self.tried) > 0:
            # TODO would be nice to undo word feedback as well
            self.tried = self.tried[:-1]
            ui.log('undo')

    def do_guess(self, ui: PromptUI):
        '''
        generate word word suggestions; usage `guess [<COUNT default: 10>]`
        '''
        show_n = ui.tokens.have(r'\d+', lambda m: int(m[0])) or 10
        return self.guess(ui, show_n=show_n)

    def do_fail(self, ui: PromptUI):
        '''
        record failure word for current run and terminate.
        '''
        self.failed = True
        self.fail_text = ui.tokens.rest
        ui.log(f'fail: {self.fail_text}')
        return self.finish

    def do_may(self, ui: PromptUI):
        '''
        record feedback on letters that may be used; usage `may AB C D ...`

        NOTE: use `may .` to clear all prior may letters
        '''
        some = False
        for tok in ui.tokens:
            if tok.startswith('.'):
                tok = tok[1:]
                self.may_letters = set()
            self.may_letters.update(tok)
            some = True
        if some:
            ui.log(f'may: {"".join(sorted(self.may_letters))}')

    def do_no(self, ui: PromptUI):
        '''
        record feedback on letters that cannot be used; usage `no AB C D ...`
        '''
        nop: set[str] = set()
        some = False
        for tok in ui.tokens:
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

    def do_tried(self, ui: PromptUI):
        '''
        record an attempted word; usage: `tried <word>`
        '''
        word = next(ui.tokens, None)
        if word is not None:
            if len(word) != self.size:
                ui.print(f'expected {self.size}-length word, got {len(word)}')
                return
            ui.log(f'tried: {word}')
            self.tried.append(word)

    def do_word(self, ui: PromptUI):
        '''
        record feedback on found word letters; usage: `word A_B_C` ( _ means unknown )
        '''
        if not ui.tokens:
            ui.print('no word feedback given')
            return
        word = next(ui.tokens)
        if len(word) > self.size:
            ui.print(f'given word too long ({len(word)}) must be at most {self.size}')
            return
        self.update_word(ui, word)

    def update_word(self, ui: PromptUI, word: str):
        word = word.lower()
        for i, x in enumerate(word[:self.size]):
            self.word[i] = '' if x == '_' else x

        word = ''.join(x if x else '_' for x in self.word)
        ui.log(f'word: {word}')

        if all(self.word):
            if word not in self.tried:
                self.tried.append(word)
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
        scores = tuple(1.0-score for score in diag.scores)

        rand = None if jitter == 0 else RandScores(scores, jitter=jitter)
        if rand is not None:
            scores = rand.scores

        def annotate(i: int) -> Generator[str]:
            if rand is not None:
                yield from rand.explain(i)
            yield '1-='
            yield from diag.explain(i)
            wf_parts = list(diag.explain_wf(i))
            if wf_parts:
                yield f'WF:{" ".join(wf_parts)}'
            yield f'LF:{" ".join(diag.explain_lf(i))}'
            yield f'LF norm:{" ".join(diag.explain_lf_norm(i))}'
        return scores, annotate

    def find(self, pattern: re.Pattern[str]):
        for word in self.wordlist.words:
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

        with git_txn(f'{path.basename(self.wordlist_file)}: add missing {word!r}') as txn:
            with txn.will_add(self.wordlist_file):
                self.wordlist.add_word(word)
            txn.commit()
            ui.write(f'🗃️ {self.wordlist_file} added {word!r}')

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
        status = '🥳' if res and not res.found else '😦'
        return  f'{status} {guesses} ⏱️ {self.elapsed}'

    @property
    @override
    def report_body(self) -> Generator[str]:
        yield from super().report_body
        res = self.result
        if res is not None:
            yield ''
            yield from res.report_body(self.tried)

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
    outcome: str
    records: tuple[tuple[int, ...], ...]
    remains: tuple[int, ...] # after each record
    undos: int
    remain: int
    unused: int
    score: int

    def report_body(self, words: Iterable[str]):
        ws = tuple(words)
        yield self.outcome
        yield ''
        for ri, (rec, rem) in enumerate(zip(self.records, self.remains)):
            word = ws[ri] if ri < len(ws) else '?????'
            marks = ''.join(self.marks[i] for i in rec)
            yield f'    {marks} tried:{word!r} remain:{rem}'
        yield ''
        yield f'    Undos used: {self.undos}'
        yield ''
        yield f'      {self.remain} words remaining'
        yield f'    x {self.unused} unused letters'
        yield f'    = {self.score} total score'

    @property
    def found(self):
        return all(x == 2 for x in self.records[-1])

    @classmethod
    def parse(cls, s: str):
        puzzle_id: int|None = None
        outcome: str = 'UNKNOWN'
        records: list[tuple[int, ...]] = []
        rems: list[int] = []
        undos: int = 0
        final_rem: int = 0
        unused: int = 0
        score: int = 0

        lines = spliterate(s, '\n')
        for line in lines:

            match = re.match(r'''(?x)
                             Don't \s+ Wordle
                             \s+ (?P<puzzle_id> \d+ )
                             \s+ - \s+
                             (?P<outcome> [^\s]+ )
                             ''', line)
            if match:
                puzzle_id = int(match[1])
                outcome = match[2]
                assert outcome == 'SURVIVED' # TODO what does failure look like
                continue

            # TODO gaf? 'Hooray! I didn't Wordle today!'

            match = re.match(r'''(?x)
                             # TODO
                             # '⬜⬜⬜⬜⬜6482'
                             # '⬜⬜⬜⬜⬜2683'
                             # '⬜🟨⬜🟩⬜44'
                             # '🟩⬜⬜🟩⬜17'
                             # '🟩⬜⬜🟩⬜7'
                             # '🟩⬜🟩🟩🟨2'
                             \s*
                             (?P<marks> [⬜🟨🟩]{5} )
                             \s*
                             (?P<rem> \d+ )
                             ''', line)
            if match:
                marks = match[1]
                rem = int(match[2])
                record = tuple(cls.marks.index(mark) for mark in marks)
                records.append(record)
                rems.append(rem)
                continue

            match = re.match(r'''(?x)
                             \s*
                             Undos
                             \s+
                             used:
                             \s+
                             (?P<undos> \d+ )
                             ''', line)
            if match:
                undos = int(match[1])
                continue

            match = re.match(r'''(?x)
                             \s*
                             (?P<rem> \d+ )
                             \s+ words \s+ remaining
                             ''', line)
            if match:
                final_rem = int(match[1])
                continue

            match = re.match(r'''(?x)
                             \s* x
                             \s+ (?P<unused> \d+ )
                             \s+ unused \s+ letters
                             ''', line)
            if match:
                unused = int(match[1])
                continue

            match = re.match(r'''(?x)
                             \s*
                             =
                             \s+ (?P<score> \d+ )
                             \s+ total \s+ score
                             ''', line)
            if match:
                score = int(match[1])
                continue

        if puzzle_id is None:
            raise ValueError('missing dontwordle puzzle id')

        return cls(
            puzzle_id,
            outcome,
            tuple(records),
            tuple(rems),
            undos,
            final_rem,
            unused,
            score,
        )

from strkit import MarkedSpec

@MarkedSpec.mark('''

    #first
    > Don't Wordle 1095 - SURVIVED
    > Hooray! I didn't Wordle today!
    > ⬜⬜⬜⬜⬜6482
    > ⬜⬜⬜⬜⬜2683
    > ⬜🟨⬜🟩⬜44
    > 🟩⬜⬜🟩⬜17
    > 🟩⬜⬜🟩⬜7
    > 🟩⬜🟩🟩🟨2
    > Undos used: 0
    > 
    >   2 words remaining
    > x 10 unused letters
    > = 20 total score
    - puzzle_id: 1095
    - outcome: SURVIVED
    - record: (0, 0, 0, 0, 0)
    - rem: 6482
    - record: (0, 0, 0, 0, 0)
    - rem: 2683
    - record: (0, 1, 0, 2, 0)
    - rem: 44
    - record: (2, 0, 0, 2, 0)
    - rem: 17
    - record: (2, 0, 0, 2, 0)
    - rem: 7
    - record: (2, 0, 2, 2, 1)
    - rem: 2
    - undos: 0
    - remain: 2
    - unused: 10
    - score: 20

''')
def test_result_parse(spec: MarkedSpec):
    res = Result.parse(spec.input)
    record_i = 0
    rem_i = 0
    for name, value in spec.props:
        if name == 'puzzle_id': assert str(res.puzzle_id) == value
        elif name == 'outcome': assert res.outcome == value
        elif name == 'record':
            try:
                rec = res.records[record_i]
            except IndexError:
                rec = None
            assert repr(rec) == value, f'records[{record_i}]'
            record_i += 1
        elif name == 'rem':
            try:
                rem = res.remains[rem_i]
            except IndexError:
                rem = None
            assert repr(rem) == value, f'remains[{rem_i}]'
            rem_i += 1
        elif name == 'undos': assert str(res.undos) == value
        elif name == 'remain': assert str(res.remain) == value
        elif name == 'unused': assert str(res.unused) == value
        elif name == 'score': assert str(res.score) == value
    assert record_i == len(res.records) == rem_i

if __name__ == '__main__':
    DontWord.main()

