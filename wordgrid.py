#!/usr/bin/env python

import argparse
from collections import Counter, defaultdict
import re
from collections.abc import Generator, Sequence
from typing import Callable, cast, final, override, Protocol

from sortem import DiagScores, Randomized
from store import StoredLog, matcher
from ui import PromptUI
from wordlist import WordList

class WordRule(Protocol):
    def match(self, word: str) -> bool:
        return True

@final
class FuncRule:
    def __init__(self, fn: Callable[[str], bool], desc: str):
        self.fn = fn
        self.desc = desc

    def match(self, word: str):
        return self.fn(word)

    @override
    def __str__(self):
        return self.desc

@final
class PatternRule:
    def __init__(self, pattern: str|re.Pattern[str]):
        self.pattern = re.compile(pattern) if isinstance(pattern, str) else pattern

    def match(self, word: str):
        return self.pattern.search(word) is not None

    @override
    def __str__(self):
        return f'Pattern {self.pattern.pattern}'

@final
class NotPatternRule:
    def __init__(self, pattern: str|re.Pattern[str]):
        self.pattern = re.compile(pattern) if isinstance(pattern, str) else pattern

    def match(self, word: str):
        return self.pattern.search(word) is None

    @override
    def __str__(self):
        return f'Not Pattern {self.pattern.pattern}'

TrueRule = FuncRule(lambda _: True, 'Any')

def RepeatedLetter(n: int):
    def match(word: str) -> bool:
        let_counts = Counter(word)
        return n in let_counts.values()
    return FuncRule(match, f'{n}-repeated letter')

@final
class WordGrid(StoredLog):
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

    log_file: str = 'wordgrid.log'
    default_site: str = 'https://wordgrid.clevergoat.com/'
    default_wordlist: str = '/usr/share/dict/words'

    def __init__(self):
        super().__init__()

        self.wordlist_file: str = ''
        self.given_wordlist: bool = False
        self._wordlist: WordList|None = None

        self.size = 3
        self.row_rules: list[WordRule] = [TrueRule for _ in range(self.size)]
        self.col_rules: list[WordRule] = [TrueRule for _ in range(self.size)]
        self.words: list[str] = ['' for _ in range(self.size**2)]
        self.scores: defaultdict[int, dict[str, float]] = defaultdict(lambda: {})

        self.questioning: tuple[int, str] = (-1, '')

        self.play_prompt = self.std_prompt
        self.play_prompt.mess = self.play_prompt_mess
        self.play_prompt.update({
            'col': self.do_rule_col,
            'row': self.do_rule_row,
            'guess': self.do_guess,
            '*': 'guess',
        })

    def play_prompt_mess(self, ui: PromptUI):
        ui.write('   ')
        ui.fin(' ' .join(
            '🤔' if rule is TrueRule else '💡' for rule in self.col_rules))
        for row, rule in enumerate(self.row_rules):
            ui.write('🤔' if rule is TrueRule else '💡')
            for word in self.words[row * self.size : (row+1) * self.size]:
                ui.write(' ')
                ui.write('✅' if word else '❓') # '🦄' '🌌' 
            ui.fin()
        return '> '

    @matcher(r'''(?x)
        rule
        \s+
        (?P<kind> col | row ) :
        \s+
        (?P<num> \d+ )
        \s+
        (?P<rule> [^\s]+ )
        ''')
    def load_rule(self, _t: float, m: re.Match[str]):
        kind = m[1]
        num = int(m[2])
        arg = m[3]
        rule = self.parse_rule(arg)
        if rule is not None:
            if kind == 'col':
                self.col_rules[num-1] = rule
            else: # if kind == 'row':
                self.row_rules[num-1] = rule

    def do_rule_col(self, ui: PromptUI):
        '''
        usage: `col <N> [<rule>]`
        '''
        col = 0
        while ui.tokens:
            n = ui.tokens.have(r'\d+', then=lambda m: int(m[0]))
            if n is not None:
                col = n
                continue
            break
        if not col:
            ui.print(f'! missing col <N>')
            return
        arg = ui.tokens.peek()
        if not arg:
            rule = self.col_rules[col-1]
            ui.print(f'. col {col} {rule}')
            return
        rule = self.parse_rule(arg)
        if rule:
            ui.log(f'rule col: {col} {arg}')
            self.col_rules[col-1] = rule

    def do_rule_row(self, ui: PromptUI):
        '''
        usage: `row <N> <rule...>`
        '''
        row = 0
        while ui.tokens:
            n = ui.tokens.have(r'\d+', then=lambda m: int(m[0]))
            if n is not None:
                row = n
                continue
            break
        if not row:
            ui.print(f'! missing row <N>')
            return
        arg = ui.tokens.peek()
        if not arg:
            rule = self.row_rules[row-1]
            ui.print(f'. row {row} {rule}')
            return
        rule = self.parse_rule(arg)
        if rule:
            ui.log(f'rule row: {row} {arg}')
            self.row_rules[row-1] = rule

    def parse_rule(self, arg: str):
        # "#N" => PatternRule('^' + ('.' * n) + '$')
        #     Five letter word
        m = re.match(r'#(\d+)', arg)
        if m is not None:
            return PatternRule(f'^{'.'*int(m[1])}$')

        # "~XXX" => PatternRule('XXX')
        #     PatternRule en
        #     PatternRule pl
        m = re.match(r'~(.+)', arg)
        if m is not None:
            return PatternRule(re.compile(m[1], re.IGNORECASE))

        # "![ABC]" => NotPatternRule('A', 'B', 'C')
        #     Does not contain d, o, s
        #     Does not contain a, s, t
        m = re.match(r'!(.+)', arg)
        if m is not None:
            return NotPatternRule(re.compile(m[1], re.IGNORECASE))

        # "xN" => RepeatedLetter(N)
        #     Double letter
        m = re.match(r'x(\d+)', arg)
        if m is not None:
            return RepeatedLetter(int(m[1]))

        return None

    @property
    def wordlist(self):
        if self._wordlist is not None:
            if self._wordlist.name != self.wordlist_file:
                self._wordlist = None
        if self._wordlist is None:
            self._wordlist = WordList(
                self.wordlist_file,
                exclude_suffix='.wordgrid_exclude.txt')
        return self._wordlist

    def find(self, rule: WordRule):
        for word in self.wordlist.words:
            if rule.match(word): yield word

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

        if self.questioning[1]:
            return lambda ui: self.question(ui, *self.questioning)

        return self.play

    def play(self, ui: PromptUI):
        if self.run_done: return self.finish
        return self.play_prompt(ui)

    def finish(self, _ui: PromptUI):
        # self.check_fail_text(ui)
        return self.finalize

    @matcher(r'''(?x)
        word :
        \s+ (?P<i> \d+ )
        \s+ (?P<word> [^\s]+ )
        \s+ (?P<score> [^\s]+ )
        ''')
    def load_word(self, _t: float, m: re.Match[str]):
        word_i = int(m[1])
        word = m[2]
        score = float(m[3])
        self.words[word_i] = word
        self.scores[word_i][word] = score

    def do_guess(self, ui: PromptUI, show_n: int=10):
        '''
        usage: `guess [<col> [<row>]]`
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

        col: int|None = None
        row: int|None = None
        word_i: int = 0

        while ui.tokens:
            if col is None:
                n = ui.tokens.have(r'\d+', lambda m: int(m[0]))
                if n is not None:
                    col = n
                    if col > self.size:
                        ui.print(f'! col:{col} out of bounds')
                        return
                    continue
            if row is None:
                n = ui.tokens.have(r'\d+', lambda m: int(m[0]))
                if n is not None:
                    row = n
                    if row > self.size:
                        ui.print(f'! row:{row} out of bounds')
                        return
                    continue
            try:
                if may_rand.parse_arg(ui):
                    continue
            except re.PatternError as err:
                ui.print(f'! {err}')
                return
            ui.print(f'! invalid * arg {next(ui.tokens)!r}')
            return

        if col is not None and row is not None:
            word_i = (row - 1) * self.size + (col - 1)
        elif col is not None:
            word_i = col - 1
            while self.words[word_i]:
                word_i += self.size
                if word_i >= len(self.words):
                    ui.print(f'. col {col} complete, specify row to re-guess')
                    return
            row = word_i // self.size
        elif col is None:
            while self.words[word_i]:
                word_i += 1
                if word_i >= len(self.words):
                    ui.print(f'. all cells complete, spcify col & row to re-guess')
                    return
            col = word_i % self.size
            row = word_i // self.size

        rule = self.col_rules[col-1]
        ui.write(f'Filtering col:{col} — {rule}')
        words = set(self.find(rule))
        ui.fin(f' — {len(words)}')

        rule = self.row_rules[row-1]
        ui.write(f'Filtering row:{row} — {rule}')
        words.intersection_update(self.find(rule))
        ui.fin(f' — {len(words)}')

        priors = self.scores[word_i]
        if priors:
            words.difference_update(priors.keys())
            ui.print(f'Dropped {len(priors)} priors')

        pos = may_rand.choose(sorted(words))
        if not pos.data:
            ui.print(f'! no results')
            return

        return ui.interact(pos.choose(
            then=lambda word: self.question(ui, word_i, word),
            head=lambda ui: ui.print(f'col:{col} row:{row} {pos}'),
        ))

    @matcher(r'''(?x)
        questioning :
        \s+ (?P<i> -? \d+ )
        \s* (?P<word> [^\s]* )
        ''')
    def load_question(self, _t: float, m: re.Match[str]):
        self.questioning = (int(m[1]), m[2])

    def question(self, ui: PromptUI, word_i: int, word: str):
        ui.log(f'questioning: {word_i} {word}')
        self.questioning = (word_i, word)
        return self.do_question if word else self.play

    def do_question(self, ui: PromptUI) -> PromptUI.State|None:
        word_i, word = self.questioning
        if word:
            with ui.input(f'🌡️ {word} ? ') as tokens:
                if tokens:
                    score = tokens.have(r'\d*(\.\d*)?', lambda m: float(m[0]))
                    if score is None:
                        return self.do_question
                    ui.log(f'word: {word_i} {word} {score}')
                    self.words[word_i] = word
                    self.scores[word_i][word] = score
        return self.question(ui, -1, '')

# Word Grid #765
# 🌌🟪🟦
# 🌌🟦🟪
# 🦄🦄🦄
# Rarity: 2.58
# wordgrid.clevergoat.com?ref=shared 🐐

# Word Grid #765
# 🦄🟪🦄
# 🦄🦄🦄
# 🦄🦄🦄
# Rarity: 0.28
# wordgrid.clevergoat.com?ref=shared 🐐

if __name__ == '__main__':
    WordGrid.main()
