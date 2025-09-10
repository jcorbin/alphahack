#!/usr/bin/env python

import argparse
import json
import re
from collections.abc import Generator, Iterable, Sequence
from dataclasses import dataclass
from itertools import combinations
from os import path
from typing import cast, final, override

from sortem import Chooser, DiagScores, MatchPat, Possible, RandScores
from store import StoredLog, git_txn
from strkit import spliterate
from ui import PromptUI
from wordlish import Attempt, Feedback, Question, Word
from wordlist import WordList

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

        self.tried: list[Attempt] = []
        self.void_letters: set[str] = set()
        self.word = Word(self.size)

        self.failed: bool = False
        self.fail_text: str = ''

        self.result_text: str = ''
        self._result: Result|None = None

        self.play_prompt = PromptUI.Prompt(self.play_prompt_mess, {
            '/site': self.cmd_site_link,
            '/store': self.cmd_store,

            'fail': self.do_fail,
            'guess': self.do_guess,
            'tried': self.do_tried,
            'undo': self.do_undo,
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
        if self._result is not None:
            return self._result
        elif self.result_text:
            try:
                self.result = Result.parse(self.result_text)
            except ValueError:
                return None
            return self._result

    @result.setter
    def result(self, res: 'Result'):
        self._result = res
        self.puzzle_id = f'#{res.puzzle_id}'

    @result.deleter
    def result(self):
        self._result = None
        self.result_text = ''

    def set_result_text(self, txt: str):
        del self.result
        self.result_text = txt
        self.result = Result.parse(txt)

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
                    tried :
                    \s+ (?P<attempt> .+ )
                    $''', rest)
                if match:
                    self.apply_tried(Attempt.parse(match[1], expected_size=self.size))
                    continue

                match = re.match(r'''(?x)
                    undo
                    \s* ( .* )
                    $''', rest)
                if match:
                    rest = match[1]
                    assert rest == ''
                    self.apply_undo()
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
                        self.set_result_text(dat)
                    except ValueError:
                        pass
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

        if not (self.tried or self.void_letters):
            self.cmd_site_link(ui)

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
            for n, at in enumerate(self.tried, 1):
                ui.print(f'{n}. {at}')
            if self.void_letters:
                ui.print(f'Avoid: {" ".join(x.upper() for x in sorted(self.void_letters))}')
        return f'{len(self.tried)+1}> '

    def play(self, ui: PromptUI):
        if self.run_done: return self.finish
        if self.word.done: return self.finish
        if len(self.tried) >= 6: return self.finish
        return self.play_prompt(ui)

    def do_undo(self, ui: PromptUI):
        '''
        rollback last `tried <word>`
        '''
        if len(self.tried) > 0:
            self.record_undo(ui)

    def record_undo(self, ui: PromptUI):
        ui.log('undo')
        self.apply_undo()

    def word_letters(self) -> Generator[str]:
        for c in self.word.yes:
            if c: yield c
        yield from self.word.may

    def apply_undo(self):
        prior = set(self.word_letters())
        tried = self.tried[:-1]
        void = tuple(self.void_letters)
        self.reset_word()
        for at in tried:
            self.apply_tried(at)
        prior.difference_update(self.word_letters())
        self.void_letters.update(void)
        self.void_letters.update(prior)

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

    def do_tried(self, ui: PromptUI):
        '''
        record an attempted word; usage: `tried <word>`
        '''
        try:
            at = Attempt.parse(ui.tokens, expected_size=self.size)
        except ValueError as err:
            ui.print(f'! {err}')
            return
        self.handle_tried(ui, at)

    def handle_tried(self, ui: PromptUI, at: Attempt):
        at.word = at.word.upper()
        ui.log(f'tried: {at}')
        self.apply_tried(at)

    def apply_tried(self, at: Attempt):
        self.tried.append(at)
        self.word.collect(at)

    def reset_word(self):
        self.tried = []
        self.void_letters = set()
        self.word.reset()

    def guess(self, ui: PromptUI, show_n: int=10):
        verbose = 0
        jitter = 0.5
        sans = False
        chooser = Chooser(show_n=show_n)

        while ui.tokens:
            try:
                if chooser.collect(ui.tokens):
                    continue
            except re.PatternError as err:
                ui.print(f'! {err}')
                return

            match = ui.tokens.have(r'-(v+)')
            if match:
                verbose += len(match.group(1))
                continue

            if ui.tokens.have(r'-sans'):
                sans = True
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

        match_words, tried_words = self._guess(ui, verbose=verbose, sans=sans)

        pos = Possible(
            match_words,
            lambda words: self.select(ui, words, jitter=jitter),
            choices=chooser.choices,
            verbose=verbose)

        if not pos.data and not sans and not chooser and self.void_letters:
            sans_words, sans_tried_words = self._guess(ui, verbose=verbose, sans=True)
            if sans_words:
                tried_words = sans_tried_words
                how = '-sans'
                for k in range(1, len(self.void_letters)):
                    k_pats = tuple(
                        MatchPat(re.compile(f'[{''.join(comb)}]', flags=re.I), neg=True)
                        for comb in combinations(self.void_letters, len(self.void_letters)-k))
                    k_pos = tuple(
                        Possible(
                            sans_words,
                            lambda words: self.select(ui, words, jitter=jitter),
                            choices=(pat,),
                            verbose=verbose)
                        for pat in k_pats)
                    k_have = tuple(
                        sum(1 for _ in ps.index())
                        for ps in k_pos)
                    if any(k_have):
                        min_i = min((
                            (n, i)
                            for i, n in enumerate(k_have)
                            if n > 0
                        ), key=lambda ni: ni[0])[1]
                        pos = k_pos[min_i]
                        have = k_have[min_i]
                        how = f'{how} {k_pats[min_i].arg_str()}'
                        break
                else:
                    pos = Possible(
                        sans_words,
                        lambda words: self.select(ui, words, jitter=jitter),
                        choices=chooser.choices,
                        verbose=verbose)
                    have = sum(1 for _ in pos.index())
                ui.print(f'auto try harder: {how} ... {have} / {pos}')

        def parts():
            yield f'{pos} from {self.word}'
            if tried_words:
                yield f'less ∩tried {len(tried_words)}'

        if pos.data:
            return ui.interact(pos.choose(
                then=self.question,
                head=lambda ui: ui.print(' '.join(parts())),
            ))

        elif tried_words:
            return ui.interact(ui.Choose(
                range(len(tried_words)),
                then=lambda i: self.question(tried_words[i][1]), # XXX ret from
                head=lambda ui: ui.print(f'{' '.join(parts())}; maybe reconsider:')
            ))

    def _guess(self,
               ui: PromptUI,
               verbose: int=0,
               sans: bool=False):

        void = None if sans or not self.void_letters else self.void_letters
        pat = self.word.pattern(void=void)
        if verbose:
            for n, part in enumerate(self.word.re_can_lets(void=void), 1):
                ui.print(f'* re_can_let_{n}: {part}')
            for part in self.word.re_may_alts(void=void):
                ui.print(f'* re_may_alt: {part}')
            ui.print(f'* pattern: {pat}')
        words = set(self.find(pat))

        # drop any words that intersect tried prior letters
        tried_words = [
            (wi, word)
            for wi, word in enumerate(words)
            if any(
                not self.word.yes[li]
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
                            if not self.word.yes[i]:
                                ui.print(f'    - {let.upper()} from {self.tried[j]!r}[{i}]')

        return tuple(sorted(words)), tried_words

    def question(self, word: str):
        def then(word: str, res: Feedback):
            def and_then(ui: PromptUI):
                self.handle_tried(ui, Attempt(word, res))
                raise StopIteration()
            return and_then
        return Question(word, then=then)

    def tried_letters(self, word: str):
        for i, let in enumerate(word):
            if let not in self.word.may: continue
            for j, prior in enumerate(self.tried):
                if prior.word[i] == let:
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
        return self.finalize

    @override
    def have_result(self):
        return self.result is not None

    @override
    def proc_result(self, ui: PromptUI, text: str):
        del self.result
        self.result_text = text
        res = self.result
        if not res: return

        if not res.puzzle_id:
            del self.result
            return

        puzzle_id = f'#{res.puzzle_id}'
        self.puzzle_id = puzzle_id
        if self.puzzle_id != puzzle_id:
            ui.log(f'puzzle_id: {self.puzzle_id}')
        ui.log(f'result: {json.dumps(text)}')

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

        return super().review_prompt(ui)

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
        status = (
            '❓' if not res else
            '🥳' if not res.found else
            '😳' if res.oops else
            '🤷')
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
    marks = ('⬜', '🟨', '🟩', '⬛')

    @final
    @dataclass
    class Round:
        note: str
        took: int
        limit: int

    puzzle_id: int
    outcome: str
    fortune: str
    records: tuple[tuple[int, ...], ...]
    remains: tuple[int, ...] # after each record
    undos: int
    remain: int
    unused: int
    score: int

    def report_body(self, tried: Iterable[Attempt]):
        ws = tuple(tried)
        yield self.outcome
        yield f'> {self.fortune}'
        yield ''
        for ri, (rec, rem) in enumerate(zip(self.records, self.remains)):
            word = ws[ri] if ri < len(ws) else '?????'
            marks = ''.join(self.marks[i] for i in rec)
            yield f'    {marks} tried:{word} remain:{rem}'
        yield ''
        yield f'    Undos used: {self.undos}'
        yield ''
        yield f'      {self.remain} words remaining'
        yield f'    x {self.unused} unused letters'
        yield f'    = {self.score} total score'

    @property
    def found(self):
        return all(x in (2, 3) for x in self.records[-1])

    @property
    def oops(self):
        return self.found and self.outcome != 'ELIMINATED'

    @classmethod
    def parse(cls, s: str):
        puzzle_id: int|None = None
        outcome: str = 'UNKNOWN'
        fortune: str = 'Outlook Cloudy'
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
                assert outcome in ('ELIMINATED', 'SURVIVED', 'WORDLED') # TODO others?
                fortune = next(lines)
                continue

            match = re.match(r'''(?x)
                             \s*
                             (?P<marks> [⬜🟨🟩⬛]{5} )
                             \s*
                             (?P<rem> \d+ )?
                             ''', line)
            if match:
                marks = match[1]
                rem = int(match[2]) if match[2] else 0
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
            fortune,
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
    - fortune: Hooray! I didn't Wordle today!
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
    - found: False
    - undos: 0
    - remain: 2
    - unused: 10
    - score: 20

    #fail
    > Don't Wordle 1105 - ELIMINATED
    > Well technically I didn't Wordle!
    > ⬜⬜⬜⬜⬜6049
    > ⬜⬜⬜⬜⬜2118
    > ⬜⬜⬜🟩⬜185
    > ⬜⬜⬜🟩⬜5
    > ⬜⬜🟨🟩🟩1
    > ⬛⬛⬛⬛⬛
    > Undos used: 5
    - puzzle_id: 1105
    - outcome: ELIMINATED
    - fortune: Well technically I didn't Wordle!
    - record: (0, 0, 0, 0, 0)
    - rem: 6049
    - record: (0, 0, 0, 0, 0)
    - rem: 2118
    - record: (0, 0, 0, 2, 0)
    - rem: 185
    - record: (0, 0, 0, 2, 0)
    - rem: 5
    - record: (0, 0, 1, 2, 2)
    - rem: 1
    - record: (3, 3, 3, 3, 3)
    - rem: 0
    - found: True
    - undos: 5
    - remain: 0
    - unused: 0
    - score: 0

    #oops
    > Don't Wordle 1109 - WORDLED
    > I must admit that I Wordled!
    > ⬜⬜⬜⬜⬜6482
    > ⬜⬜⬜⬜⬜3628
    > ⬜⬜⬜⬜⬜783
    > ⬜⬜🟨⬜⬜81
    > 🟨🟩⬜⬜⬜8
    > 🟩🟩🟩🟩🟩0
    > Undos used: 0
    - puzzle_id: 1109
    - outcome: WORDLED
    - fortune: I must admit that I Wordled!
    - record: (0, 0, 0, 0, 0)
    - rem: 6482
    - record: (0, 0, 0, 0, 0)
    - rem: 3628
    - record: (0, 0, 0, 0, 0)
    - rem: 783
    - record: (0, 0, 1, 0, 0)
    - rem: 81
    - record: (1, 2, 0, 0, 0)
    - rem: 8
    - record: (2, 2, 2, 2, 2)
    - rem: 0
    - found: True
    - undos: 0
    - remain: 0
    - unused: 0
    - score: 0

''')
def test_result_parse(spec: MarkedSpec):
    res = Result.parse(spec.input)
    record_i = 0
    rem_i = 0
    for name, value in spec.props:
        if name == 'puzzle_id': assert str(res.puzzle_id) == value
        elif name == 'outcome': assert res.outcome == value
        elif name == 'fortune': assert res.fortune == value
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
        elif name == 'found': assert str(res.found) == value
    assert record_i == len(res.records) == rem_i

if __name__ == '__main__':
    DontWord.main()

