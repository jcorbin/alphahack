#!/usr/bin/env python

import argparse
import re
from collections.abc import Generator, Sequence
from typing import cast, final, override

from sortem import DiagScores, Randomized
from store import StoredLog, matcher
from ui import PromptUI
from wordlish import Attempt, Word, parse_feedback
from wordlist import WordList

@final
class Infinidle(StoredLog):
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

    log_file: str = 'infinidle.log'
    default_wordlist: str = '/usr/share/dict/words'
    # https://devbanana.itch.io/infinidle

    def __init__(self):
        super().__init__()

        self.wordlist_file: str = ''
        self.given_wordlist: bool = False
        self._wordlist: WordList|None = None

        self.size: int = 5

        self.questioning: tuple[str, ...] = ()
        self.word = Word(self.size)
        self.attempts: list[Attempt] = []

        self.last_pat: re.Pattern[str] = re.compile('^$')
        self.last_words: set[str] = set()

        self.play_prompt = self.std_prompt
        self.play_prompt.mess = self.play_prompt_mess
        self.play_prompt.update({
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
                exclude_suffix='.infinidle_exclude.txt')
        return self._wordlist

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

        if self.questioning:
            return lambda ui: self.question(ui, *self.questioning)

        return self.play

    def play(self, ui: PromptUI):
        if self.run_done: return self.finish
        self.questioning = ()
        return self.play_prompt(ui)

    def finish(self, _ui: PromptUI):
        # self.check_fail_text(ui)
        return self.finalize

    def play_prompt_mess(self, ui: PromptUI):
        if self.play_prompt.re == 0:
            word = self.word
            s = str(self.word)
            wl = len(self.word)

            try:
                ui.write(f'{s:<{wl}}')
                if word.done:
                    ui.write(f' ✅')
                else:
                    ui.write(f' ❓')
                    pat = word.pattern()
                    words = set(self.find(pat))
                    self.last_pat = pat
                    self.last_words = words
                    ui.write(f' N:{len(words)}')
            finally:
                ui.fin()

        return f'> '

    @matcher(r'''(?x)
        attempt :
        \s+
        (?P<at_str> .* )
        $''')
    def load_attempt(self, _t: float, m: re.Match[str]):
        at = Attempt.parse(m[1])
        self.attempt_update(self.word, self.attempts, at)

    def attempt_update(self, word: Word, ats: list[Attempt], at: Attempt):
        wu = at.word.upper()
        if wu in set(a.word for a in ats):
            redo = [a for a in ats if a.word != wu]
            word.reset()
            ats.clear()
            for a in redo:
                ats.append(word.collect(a))
        ats.append(word.collect(at))

    def do_tried(self, ui: PromptUI):
        '''
        usage: `tried <word> [<word> ...]`
        '''
        word_pat = re.compile(r'[a-zA-Z]{' + str(self.size) +  r'}$')
        words: list[str] = []
        for token in ui.tokens:
            m = word_pat.match(token)
            if not m:
                ui.print(f'! invalid <word> {token!r}; expected {word_pat.pattern}')
                return
            words.append(m[0].upper())
        if not words:
            ui.print('! missing <word>')
            return
        return self.question(ui, *words)

    @matcher(r'''(?x)
        questioning :
        \s+
        (?P<word> [^\s]+ .* )
        $''')
    def load_question(self, _t: float, m: re.Match[str]):
        self.questioning = tuple(m[1].split())

    @matcher(r'''(?x)
        reset
        \s+
        (?P<word> [^\s]+)
        $''')
    def load_reset(self, _t: float, m: re.Match[str]):
        prior = str(m[1])
        if len(prior) == self.size:
            _ = self.do_reset(prior)

    def do_reset(self, prior: str):
        self.word = Word(self.size)
        self.attempts = []
        self.questioning = (prior,)

    def question(self, ui: PromptUI, *words: str):
        # TODO reconcile with wordlish.Question
        ui.log(f'questioning: {" ".join(words)}')
        self.questioning = words
        return self.do_question

    def do_question(self, ui: PromptUI) -> PromptUI.State|None:
        if self.word.done:
            prior = str(self.word)
            ui.log(f'reset {prior}')
            self.do_reset(prior)
            return

        qws = tuple(w.upper() for w in self.questioning)
        for wu in tuple(
            w for w in qws
            if w not in (a.word for a in self.attempts)):
            ui.copy(wu)
            ui.print(f'📋 "{wu}"')
            with ui.input(f'{self.word}? ') as tokens:
                if tokens.have(r'/tried$'):
                    ui.print(f'! retry  -> {tokens.rest}')
                    st = self.do_tried(ui)
                    if st is None: raise StopIteration
                    return st
                n = len(self.word)
                fb = parse_feedback(tokens, n)
                if len(fb) != n:
                    ui.print(f'! invalid feedback length; expected {n}, got {len(fb)}')
                    return None
                at = Attempt(wu, fb)
                self.attempt_update(self.word, self.attempts, at)
                ui.log(f'attempt: {at}')
        return self.play_prompt

    def do_guess(self, ui: PromptUI, show_n: int=10):
        '''
        usage: `guess [-v] [-jitter <prop>] [...chooser options...]`
        '''

        def select(words: Sequence[str]):
            diag = DiagScores(words)
            scores = diag.scores

            def annotate(i: int) -> Generator[str]:
                yield from diag.explain(i)
                wf_parts = list(diag.explain_wf(i))
                if wf_parts:
                    yield f'WF:{" ".join(wf_parts)}'
                yield f'LF:{" ".join(diag.explain_lf(i))}'
                yield f'LF norm:{" ".join(diag.explain_lf_norm(i))}'

            return scores, annotate

        may_rand = Randomized(select, show_n=show_n)

        while ui.tokens:
            try:
                if may_rand.parse_arg(ui):
                    continue
            except re.PatternError as err:
                ui.print(f'! {err}')
                return
            ui.print(f'! invalid * arg {next(ui.tokens)!r}')
            return

        word = self.word
        pat = word.pattern()
        words = set(self.find(pat))
        pos = may_rand.choose(sorted(words))
        if not pos.data:
            ui.print(f'! no results for {pat.pattern} {word}')
            # TODO maybe try harder?
            return

        return ui.interact(pos.choose(
            then=lambda ch: lambda ui: self.question(ui, ch),
            head=lambda ui: ui.print(f'{pos} {word}'),
        ))

# I got a score of 5 on the daily INFINIDLE #1554! Can you beat my score? https://devbanana.itch.io/infinidle
# I got a score of 8 in INFINIDLE unlimited mode! Can you beat my score? https://devbanana.itch.io/infinidle

if __name__ == '__main__':
    Infinidle.main()
