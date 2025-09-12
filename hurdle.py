#!/usr/bin/env python

import argparse
import json
import re
from collections.abc import Generator, Iterable, Sequence
from dataclasses import dataclass
from itertools import zip_longest
from os import path
from typing import cast, final, override

from sortem import Chooser, DiagScores, Possible, RandScores
from store import StoredLog, git_txn
from strkit import spliterate
from ui import PromptUI
from wordlish import Attempt, Feedback, Question, Word
from wordlist import WordList

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
            self.wordlist_file = wordlist

    log_file: str = 'hurdle.log'
    default_site: str = 'https://play.dictionary.com/games/todays-hurdle'
    default_wordlist: str = '/usr/share/dict/words'
    site_name: str = 'dictionary.com hurdle'

    def __init__(self):
        super().__init__()

        self.debug = 0

        self.size: int = 5
        self.wordlist_file: str = ''
        self.given_wordlist: bool = False
        self._wordlist: WordList|None = None

        self.tried: list[Attempt] = []
        self.word = Word(self.size)

        self.attempts: list[tuple[str, ...]] = []
        self.words: list[str] = []

        self.failed: bool = False
        self.fail_text: str = ''

        self._result: Result|None = None

        self.prompt = PromptUI.Prompt(self.display_mess, {
            '/site': self.cmd_site_link,
            '/store': self.cmd_store,

            'gen': self.do_gen,
            'fail': self.do_fail,
            'tried': self.do_tried,
            'word': self.do_word,
            '*': 'gen',
        })

    @property
    def wordlist(self):
        if self._wordlist is not None:
            if self._wordlist.name != self.wordlist_file:
                self._wordlist = None
        if self._wordlist is None:
            self._wordlist = WordList(
                self.wordlist_file,
                exclude_suffix='.hurdle_exclude.txt')
        return self._wordlist

    @property
    def result(self):
        if self._result is not None:
            return self._result
        elif self.result_text:
            try:
                self.result = Result.parse(self.result_text, self.size)
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

    @override
    def set_result_text(self, txt: str):
        del self.result
        super().set_result_text(txt)
        self.result = Result.parse(txt, self.size)

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
                    self.apply_failed(rest)
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
                    tried : \s+ ( .+ )
                    $''', rest)
                if match:
                    at = Attempt.parse(match[1], expected_size=self.size)
                    _ = self.apply_tried(at)
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

        if not (self.tried or self.words):
            self.cmd_site_link(ui)

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

    def prompt_prefix(self):
        word_n = len(self.words) + 1
        word_m = len(self.tried) + 1
        return f'{word_n}.{word_m}'

    def display_mess(self, ui: PromptUI):
        if self.prompt.re == 0:
            if self.word:
                ui.print(f'Word: {self.word}')
            word_n = len(self.words) + 1
            for m, at in enumerate(self.tried, 1):
                ui.print(f'{word_n}.{m}: {at}')
        return f'{self.prompt_prefix()}> '

    def display(self, ui: PromptUI):
        if self.run_done or len(self.words) >= self.size:
            return self.finish

        # question prior words at start of round
        word_n = len(self.words) + 1
        num_priors = (
            0 if word_n <= 1
            else len(self.words) if word_n == self.size
            else 1)
        prior_back = num_priors - len(self.tried)
        back_i = len(self.words) - prior_back
        if 0 <= back_i < len(self.words):
            q = self.question(self.words[back_i])
            rename: dict[str, str] = dict()
            for name, then in self.prompt.items():
                if re.match(r'[a-zA-Z]', name):
                    nom = f'/{name}'
                    rename[name] = nom
                    name = nom
                if isinstance(then, str) and then in rename:
                    then = rename[then]
                q.prompt.set(name, then)
            return ui.interact(q)

        return self.prompt(ui)

    def do_gen(self, ui: PromptUI):
        '''
        generate [<NUMBER>=10]  # presents N score-randomized words
        '''
        n = ui.tokens.have(r'\d+', lambda m: int(m[0])) or 10
        return self.guess(ui, show_n=n)

    def do_fail(self, ui: PromptUI):
        '''
        fail <WORD>  # marks the puzzle search as failed, providing the unfound word
        '''
        if not ui.tokens:
            ui.print(f'! must provide fail word')
            return
        word = next(ui.tokens).upper()
        if len(word) != self.size:
            ui.print(f'! wrong sized fail word; must be {self.size} got {len(word)}')
            return
        self.fail_text = word
        ui.log(f'fail: {self.fail_text}')
        self.apply_failed(word)
        return self.finish

    def apply_failed(self, text: str):
        self.failed = True
        self.fail_text = text
        self.attempts.append(tuple(at.word for at in self.tried))

    def do_tried(self, ui: PromptUI):
        '''
        tried <WORD> <FEEDBACK>  # records an attempted word

        Feedback is a word-sized sequence of n/m/y responses

        Word and feedback case does not matter
        '''
        try:
            at = Attempt.parse(ui.tokens, expected_size=self.size)
        except ValueError as err:
            ui.print(f'! {err}')
            return
        self.handle_tried(ui, at)

    def do_word(self, ui: PromptUI):
        '''
        word <WORD>  # records a found word
        '''
        word = next(ui.tokens)
        if len(word) != self.size:
            ui.print(f'! given word wrong size ({len(word)}), must be {self.size}')
            return
        self.handle_tried(ui, Attempt(word, tuple(2 for _ in word)))

    def handle_tried(self, ui: PromptUI, at: Attempt):
        at.word = at.word.upper()
        ui.log(f'tried: {at}')
        if self.apply_tried(at):
            ui.print('')
            ui.print('--- next word')

    def apply_tried(self, at: Attempt) -> bool:
        self.tried.append(at)
        self.word.collect(at)
        if self.word.done:
            self.words.append(self.word.word.lower())
            self.attempts.append(tuple(at.word for at in self.tried))
            self.word.reset()
            self.tried = []
            return True
        return False

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

        words = set(self.find(re.compile(self.word.pattern())))

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
            if self.debug > 1:
                ui.log(f'skip ∩tried remain:{len(words)} dropped:{len(skip_words)} -- {sorted(skip_words)!r}')
            if verbose:
                ui.print(f'- pruned {len(skip_words)} words based on priors')
                if verbose > 1:
                    for i, word in tried_words:
                        ui.print(f'  {i+1}. {word}')
                        for let, j, i in self.tried_letters(word):
                            if not self.word.yes[i]:
                                ui.print(f'    - {let.upper()} from {self.tried[j]!r}[{i}]')

        pos = Possible(
            sorted(words),
            lambda words: self.select(ui, words, jitter=jitter),
            choices=chooser.choices,
            verbose=verbose)

        def parts():
            yield f'{pos} from {self.word}'
            if tried_words:
                yield f'less ∩tried {len(tried_words)}'

        if pos.data:
            return ui.interact(pos.choose(
                then=self.question,
                head=lambda ui: ui.print(' '.join(parts())),
                mess=f'{self.prompt_prefix()} ? ',
            ))

        elif tried_words:
            return ui.interact(ui.Choose(
                range(len(tried_words)),
                then=lambda i: self.question(tried_words[i][1]),
                head=lambda ui: ui.print(f'{' '.join(parts())}; maybe reconsider:'),
            ))

    def question(self, word: str):
        def then(word: str, res: Feedback):
            def and_then(ui: PromptUI):
                self.handle_tried(ui, Attempt(word, res))
                raise StopIteration()
            return and_then

        def reject(ui: PromptUI, word: str):
            self.wordlist.do_bad(ui, word, mark=f'{self.site}:')
            raise StopIteration()

        return Question(word,
                        prefix=self.prompt_prefix(),
                        then=then,
                        reject=lambda word: lambda ui: reject(ui, word))

    def tried_letters(self, word: str):
        for i, let in enumerate(word):
            if let not in self.word.may: continue
            for j, prior in enumerate(self.tried):
                if prior.word[i] == let:
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
        for word in self.wordlist.words:
            if pattern.fullmatch(word): yield word

    def check_fail_text(self, ui: PromptUI):
        try:
            word = self.fail_text.strip().split()[0].lower()
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
    def proc_result(self, ui: PromptUI, text: str) -> None:
        del self.result
        self.result_text = text
        res = self.result
        if not res: return

        if not res.puzzle_id:
            del self.result
            return

        puzzle_id = f'#{res.puzzle_id}'
        if self.puzzle_id != puzzle_id:
            self.puzzle_id = puzzle_id
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
        status = '🥳' if res and res.found else '😦'
        return  f'{status} {guesses} ⏱️ {self.elapsed}'

    @property
    @override
    def report_body(self) -> Generator[str]:
        yield from super().report_body

        res = self.result
        if res:

            yield ''

            recs = iter(res.records)
            for (rnd, attempts) in zip_longest(res.rounds, self.attempts, fillvalue=None):
                if rnd is None:
                    yield f'    ??? No Round'
                elif rnd.note:
                    yield f'    {rnd.note} {rnd.took}/{rnd.limit}'
                else:
                    yield f'    {rnd.took}/{rnd.limit}'

                n = rnd.took if rnd is not None else len(attempts) if attempts is not None else 0
                sa = () if attempts is None else attempts[-n:]
                for i in range(n):
                    rec = next(recs, None)
                    marks = () if rec is None else tuple(Result.marks[i] for i in rec)
                    at = sa[i] if i < len(sa) else '?'*self.size
                    yield f'    {at} {"".join(marks)}'

        if self.fail_text:
            yield f'    FAIL: {self.fail_text}'

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
