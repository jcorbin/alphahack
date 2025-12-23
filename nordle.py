#!/usr/bin/env python

import argparse
import os
import re
from dataclasses import dataclass
from collections.abc import Generator, Sequence
from typing import cast, final, override

from store import StoredLog, matcher
from strkit import MarkedSpec, consume_codes, consume_digits, spliterate
from sortem import Chooser, DiagScores, Possible, RandScores
from wordlish import Attempt, Word, parse_feedback
from wordlist import WordList
from ui import PromptUI

@final
class Nordle(StoredLog):
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

    log_file: str = 'nordle.log'
    default_wordlist: str = '/usr/share/dict/words'

    # TODO m-w.com/games/quordle/

    def __init__(self):
        super().__init__()

        self.wordlist_file: str = ''
        self.given_wordlist: bool = False
        self._wordlist: WordList|None = None

        self.kind: str = '' # e.g. "Quordle" "Octordle"
        self.mode: str = '' # e.g. "Classic" "Extreme" "Rescue" etc
        self.size: int = 5
        self.num_words: int = 4

        # TODO support sequence mode

        self.questioning: str = ''
        self.words: Sequence[Word] = tuple(
            Word(self.size)
            for _ in range(self.num_words))
        self.attempts: Sequence[list[Attempt]] = tuple(
            []
            for _ in range(self.num_words))

        self._result: Result|None = None

        self.play_prompt = self.std_prompt
        self.play_prompt.mess = self.play_prompt_mess
        self.play_prompt.update({
            'feedback': self.do_feedback,
            'guess': self.do_guess,
            'tried': self.do_tried,
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
                exclude_suffix='.quordle_exclude.txt')
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
        if self.kind:
            if f'{res.kind}ordle' != self.kind:
                raise ValueError(f"result kind mismatch expected {self.kind!r} got '{res.kind}ordle'")
            if not self.mode:
                self.mode = res.mode
            elif res.mode != f'{self.mode}':
                raise ValueError(f'result mode mismatch expected {self.mode!r} got {res.mode!r}')
        if res.id:
            if not self.puzzle_id:
                self.puzzle_id = f'#{res.id}'
            elif self.puzzle_id != f'#{res.id}':
                raise ValueError(f"result id mismatch, expected {self.puzzle_id!r} got '#{res.id}'")
        self._result = res

    @result.deleter
    def result(self):
        self._result = None
        self.result_text = ''

    @override
    def set_result_text(self, txt: str):
        del self.result
        super().set_result_text(txt)
        self.result = Result.parse(txt)

    @override
    def have_result(self):
        return self.result is not None

    @property
    @override
    def puzzle_name(self):
        res = self.result
        if res:
            return f'{res.kind}ordle {res.mode}'
        elif self.kind:
            return f'{self.kind} {self.mode or "Classic"}'
        else:
            return '?-ordle'

    @override
    def store_subents(self):
        res = self.result
        if res:
            yield f'{res.kind}ordle'
            yield res.mode
        elif self.kind:
            yield f'{self.kind}'
            yield self.mode or "Classic"
        else:
            yield self.store_name

    @property
    @override
    def report_desc(self) -> str:
        res = self.result
        status = (
            '🤔' if not res else
            '🥳' if res.solved else
            '😦')
        score = res.score_or() if res else -1
        return  f'{status} score:{score} ⏱️ {self.elapsed}'

    @property
    @override
    def report_body(self) -> Generator[str]:
        yield from super().report_body

        res = self.result
        if res:
            yield ''
            parts = [f'{res.kind}ordle', res.mode]
            if res.trailer:
                parts.append(res.trailer)
            yield ' '.join(parts)

        yield ''
        for i, word in enumerate(self.words):
            n = i + 1

            guesses = -1
            try:
                guesses = len(self.attempts[i])
                # TODO discount given priors from rescue mode
            except IndexError: pass

            score = -1
            if res:
                try:
                    score = res.turns[i]
                except IndexError: pass

            yield f'{n}. {word} attempts:{guesses} score:{score}'

    def find(self, pattern: re.Pattern[str]):
        for word in self.wordlist.words:
            if pattern.fullmatch(word): yield word

    @matcher(r'''(?x)
        wordlist :
        \s+
        (?P<wordlist> [^\s]+ )
        \s* ( .* )
        $''')
    def load_wordlist(self, _t: float, m: re.Match[str]):
        assert m[2] == ''
        self.wordlist_file = m[1]
        self.given_wordlist = True

    @override
    def startup(self, ui: PromptUI) -> PromptUI.State | None:
        if not self.wordlist_file:
            with ui.input(f'📜 {self.default_wordlist} ? ') as tokens:
                self.wordlist_file = next(tokens, self.default_wordlist)
            if not self.wordlist_file:
                return

        if not self.given_wordlist:
            self.given_wordlist = True
            ui.log(f'wordlist: {self.wordlist_file}')

        if not any(word for word in self.words):
            self.cmd_site_link(ui)

        if self.questioning:
            return lambda ui: self.question(ui, self.questioning)

        return self.play

    @property
    @override
    def run_done(self) -> bool:
        # TODO if self.result is not None: return True
        if all(word.done for word in self.words): return True
        return False

    def play(self, ui: PromptUI):
        if self.run_done: return self.finish
        self.questioning = ''
        return self.play_prompt(ui)

    def finish(self, ui: PromptUI):
        # self.check_fail_text(ui)
        return self.finalize

    def play_prompt_mess(self, ui: PromptUI):
        if self.play_prompt.re == 0:
            ws = tuple(str(w) for w in self.words)
            wl = max(len(w) for w in ws)
            for n, (word, s) in enumerate(zip(self.words, ws), 1):
                try:
                    ui.write(f'{n}. {s:<{wl}}')
                    if word.done:
                        ui.write(f' ✅')
                    else:
                        ui.write(f' ❓')
                        pat = word.pattern()
                        words = set(self.find(pat))
                        ui.write(f' #{len(words)}')
                finally:
                    ui.fin()

        return f'> '

    @matcher(r'''(?x)
        attempt :
        \s+
        (?P<index> \d+ )
        \s+
        (?P<at_str> .* )
        $''')
    def load_attempt(self, _t: float, m: re.Match[str]):
        i = int(m[1])
        at = Attempt.parse(m[2])
        self.attempt_update(self.words[i], self.attempts[i], at)

    def attempt_update(self, word: Word, ats: list[Attempt], at: Attempt):
        wu = at.word.upper()
        if wu in set(a.word for a in ats):
            redo = [a for a in ats if a.word != wu]
            word.reset()
            ats.clear()
            for a in redo:
                ats.append(word.collect(a))
        ats.append(word.collect(at))

    def do_feedback(self, ui: PromptUI):
        '''
        usage: `feedback <N> <word> <feedback>`
        '''
        n = ui.tokens.have(r'\d+', then=lambda m: int(m[0]))
        if n is None:
            ui.print('! missing <number>')
            return
        i = n - 1
        try:
            word = self.words[i]
            ats = self.attempts[i]
        except IndexError:
            ui.print('! invalid <number>')
            return
        try:
            at = Attempt.parse(ui.tokens, len(word))
        except ValueError as err:
            ui.print(f'! invalid <word> <feedback> -- {err}')
            return
        self.attempt_update(word, ats, at)
        ui.log(f'attempt: {i} {at}')

    def do_tried(self, ui: PromptUI):
        '''
        usage: `tried <word>`
        '''
        if not ui.tokens:
            ui.print('! missing <word>')
            return
        word_str = next(ui.tokens)
        if len(word_str) != self.size:
            ui.print(f'! invalid <word> length; expected {self.size} got {len(word_str)}')
            return
        return self.question(ui, word_str)

    @matcher(r'''(?x)
        questioning :
        \s+
        \s* (?P<word> [^\s]+ )
        $''')
    def load_question(self, _t: float, m: re.Match[str]):
        self.questioning = m[1]

    def question(self, ui: PromptUI, word_str: str):
        # TODO reconcile with wordlish.Question
        ui.log(f'questioning: {word_str}')
        self.questioning = word_str
        ui.copy(word_str)
        ui.print(f'📋 "{word_str}"')
        wu = word_str.upper()
        for i, (word, priors) in enumerate(zip(self.words, self.attempts)):
            if word.done:
                continue
            n = i + 1
            if any(a.word == wu for a in priors):
                continue
            while True:
                with ui.input(f'#{n} {word}? ') as tokens:
                    fb = parse_feedback(tokens, len(word))
                    if len(fb) != len(word):
                        ui.print(f'! invalid feedback length; expected {len(word)}, got {len(fb)}')
                        continue
                    at = Attempt(wu, fb)
                    self.attempt_update(word, priors, at)
                    ui.log(f'attempt: {i} {at}')
                    break
        return self.play

    def do_guess(self, ui: PromptUI, show_n: int=10):
        '''
        usage: `guess <N>`
        '''

        n = ui.tokens.have(r'\d+', then=lambda m: int(m[0]))
        if n is None:
            ui.print('! missing <number>')
            return
        i = n - 1
        try:
            word = self.words[i]
        except IndexError:
            ui.print('! invalid <number>')
            return

        verbose = 0
        jitter = 0.5
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

        pat = word.pattern()
        words = set(self.find(pat))
        match_words = tuple(sorted(words))

        def select(words: Sequence[str], jitter: float = 0.5):
            diag = DiagScores(words)
            scores = diag.scores

            rand = None if jitter == 0 else RandScores(scores, jitter=jitter)
            if rand is not None:
                scores = rand.scores

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

        pos = Possible(
            match_words,
            lambda words: select(words, jitter=jitter),
            choices=chooser.choices,
            verbose=verbose)

        if not pos.data:
            ui.print(f'! no results for {pat.pattern} for {word}')
            # TODO maybe try harder?
            return

        return ui.interact(pos.choose(
            then=lambda ch: lambda ui: self.question(ui, ch),
            head=lambda ui: ui.print(f'{pos} from {word}'),
        ))

score_codes = {
    '🟥': -1,
    '0️⃣': 0,
    '1️⃣': 1,
    '2️⃣': 2,
    '3️⃣': 3,
    '4️⃣': 4,
    '5️⃣': 5,
    '6️⃣': 6,
    '7️⃣': 7,
    '8️⃣': 8,
    '9️⃣': 9,
    '🔟': 10,
    '🕚': 11,
    '🕛': 12,
    '🕐': 13,
    # TODO higher clock codes?
}

@dataclass
class Result:
    kind: str
    mode: str
    mark: str
    id: int
    turns: tuple[int, ...]
    score: int
    trailer: str

    @property
    def solved(self):
        return -1 not in self.turns

    def max_guesses(self):
        if self.kind == 'Qu':
            if self.mode == 'Classic': return 9
            elif self.mode == 'Chill': return 12
            elif self.mode == 'Extreme': return 8
            elif self.mode == 'Rescue': return 9 # XXX or 7, given 2
            elif self.mode == 'Sequence': return 10
            # TODO how do weekly?
        elif self.kind == 'Oct':
            if self.mode == 'Classic': return 13
            elif self.mode == 'Rescue': return 13 # XXX or 9, given 4
            elif self.mode == 'Sequence': return 15
            # TODO elif self.mode == 'Challenge': return 13 ?
            elif self.mode == 'Easy': return 16
            # TODO Casual -> unlimited?
        return -1

    def score_turns(self, max: int = -1):
        if max < 0: max = self.max_guesses()
        for t in self.turns:
            if t >= 0: yield t
            elif max < 0: yield -1
            else: yield max

    def score_or(self, max: int = -1):
        if self.score: return self.score
        ts = tuple(self.score_turns(max))
        return -1 if any(t < 0 for t in ts) else sum(ts)

    @classmethod
    def parse(cls, s: str):
        kind = ''
        mode = ''
        mark = ''
        id = 0
        turns: list[int] = []
        score = 0
        trailer = ''

        for line in spliterate(s, '\n', trim=True):

            m = re.match(r'''(?x)
                (?: (?P<mark> [^\s]+ ) \s+ )?
                Daily
                \s+ (?P<kind> [^\s]+ ) ordle
                \s+ [#]? (?P<id> [\d]+ )
            ''', line)
            if m:
                kind = m.group('kind')
                mark = m.group('mark')
                id_str = m.group('id')
                if id_str: id = int(id_str)
                continue

            m = re.match(r'''(?x)
                (?: (?P<mark> [^\s]+ ) \s+ )?
                Daily
                \s+ (?P<mode> [^\s]+ )
                \s+ [#]? (?P<id> [\d]+ )
            ''', line)
            if m:
                mark = m.group('mark')
                mode = m.group('mode')
                id_str = m.group('id')
                if id_str: id = int(id_str)
                continue

            m = re.match(r'''(?x)
                (?P<mode> [^\s]+ )
                \s+ (?P<kind> [^\s]+ ) ordle
                (?: \s+ [#]? (?P<id> [\d]+ ) )?
            ''', line)
            if m:
                mode = m.group('mode')
                kind = m.group('kind')
                id_str = m.group('id')
                if id_str: id = int(id_str)
                continue

            # TODO or 🕛 ... maybe spoilers
            cd = consume_codes(score_codes.items(), line)
            digits = tuple(cd)
            if digits:
                turns.extend(digits)
                continue

            m = re.match(r'''(?x)
                Score :
                \s+
                (?P<score> \d+ )
            ''', line)
            if m:
                score = int(m[1])
                continue

            if turns and not trailer:
                trailer = line
                continue

        return cls(
            kind=kind or 'Qu',
            mode=mode or 'Classic',
            mark=mark,
            id=id,
            turns=tuple(turns),
            score=score,
            trailer=trailer,
        )

@MarkedSpec.mark('''

    #first_solve
    > 🙂 Daily Quordle 1428
    > 4️⃣6️⃣
    > 8️⃣5️⃣
    > m-w.com/games/quordle/
    - kind: Qu
    - mode: Classic
    - id: 1428
    - turns: (4, 6, 8, 5)
    - trailer: m-w.com/games/quordle/
    - score: 0

    #extreme_solve
    > 🥵 Daily Extreme 511
    > 7️⃣4️⃣
    > 6️⃣5️⃣
    > m-w.com/games/quordle/
    - kind: Qu
    - mode: Extreme
    - id: 511
    - turns: (7, 4, 6, 5)
    - trailer: m-w.com/games/quordle/
    - score: 0

    #rescue_solve
    > Daily Rescue 42
    > 4️⃣5️⃣
    > 7️⃣6️⃣
    > m-w.com/games/quordle/
    - kind: Qu
    - mode: Rescue
    - id: 42
    - turns: (4, 5, 7, 6)
    - trailer: m-w.com/games/quordle/
    - score: 0

    #practice_solve
    > Practice Quordle
    > 4️⃣3️⃣ HARDY - EXTRA
    > 7️⃣8️⃣ STUFF - GAUDY
    > m-w.com/games/quordle/
    - kind: Qu
    - mode: Practice
    - id: 0
    - turns: (4, 3, 7, 8)
    // HARDY - EXTRA
    // STUFF - GAUDY
    - trailer: m-w.com/games/quordle/
    - score: 0

    #octordle_solve
    > Daily Octordle #1428
    > 6️⃣🔟
    > 7️⃣8️⃣
    > 🕐🕛
    > 4️⃣9️⃣
    > Score: 69
    - kind: Oct
    - mode: Classic
    - id: 1428
    - turns: (6, 10, 7, 8, 13, 12, 4, 9)
    - trailer:
    - score: 69

''')
def test_parse_result(spec: MarkedSpec):
    res = Result.parse(spec.input)
    for key, value in spec.props:
        pass
        if key == 'kind': assert res.kind == value
        elif key == 'mode': assert res.mode == value
        elif key == 'id': assert str(res.id) == value
        elif key == 'turns': assert str(res.turns) == value
        elif key == 'score': assert str(res.score) == value
        elif key == 'trailer': assert res.trailer == value

if __name__ == '__main__':
    Nordle.main()
