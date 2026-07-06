#!/usr/bin/env python

import argparse
from math import nan
import re
from collections import Counter, defaultdict
from collections.abc import Generator, Sequence
from dataclasses import dataclass
from typing import Callable, Literal, cast, final, override, Protocol

from sortem import DiagScores, Randomized
from store import StoredLog, matcher
from strkit import MarkedSpec, spliterate
from ui import PromptUI
from wordlist import WordList

Tier = Literal[
    '❗', # Invalid
    '❓', # Unknown
    '🟩', '🟧', '🟨', '🟦', '🟪', '🌌', '🦄',
]

tiers = (
    '🟩', # Common (>5%)
    '🟧', # Uncommon (3-5%)
    '🟨', # Rare (1.5-3%)
    '🟦', # Epic (0.5-1.5%)
    '🟪', # Legendary (0.1-0.5%)
    '🌌', # Galaxy (<0.1%)
    '🦄', # Unicorn (only player to guess it)
)

tier_rarity = (
    5.0,
    3.0,
    1.5,
    0.5,
    0.1,
    0.01,
)

def label_rarity(score: float) -> Tier:
    for i, lim in enumerate(tier_rarity):
        if score >= lim:
            return tiers[i]
    if score == 0:
        return '🦄'
    return '❗'

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

def n_grams(n: int, s: str):
    for i in range(len(s) - n + 1):
        yield s[i:i+n]

def ContainsRule(*lets: str):
    lets = tuple(c.upper() for c in lets)
    def match(word: str) -> bool:
        return all(c in word.upper() for c in lets)
    return FuncRule(match, f'Contains {lets}')

def RepeatedLetter(n: int):
    def match(word: str) -> bool:
        return any(
            all(ng[0] == c for c in ng[1:])
            for ng in n_grams(2, word))
    return FuncRule(match, f'{n}-repeated letter')

def MultiLetter(let: str):
    let = let.upper()
    def match(word: str) -> bool:
        let_counts = Counter(word.upper())
        return let_counts[let] > 1
    return FuncRule(match, f'Multiple {let}\'s')

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
    site_name = 'wordgrid'
    default_wordlist: str = '/usr/share/dict/words'

    def __init__(self):
        super().__init__()

        self.wordlist_file: str = ''
        self.given_wordlist: bool = False
        self._wordlist: WordList|None = None
        self._result: Result|None = None

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
            'set': self.do_set,
            '*': 'guess',
            '=': 'set',
        })

    def row_labels(self, row: int) -> Generator[Tier]:
        for word_i in range(row * self.size, (row+1) * self.size):
            status: Tier =  '❓'
            word = self.words[word_i]
            if word:
                score = self.scores[word_i][word]
                status = label_rarity(score)
            yield status

    def play_prompt_mess(self, ui: PromptUI):
        def out(*parts: str):
            ui.print(' '.join(parts))
        out( '  ', *(
            '🤔' if rule is TrueRule else '💡'
            for rule in self.col_rules))
        for row, rule in enumerate(self.row_rules):
            out(
                '🤔' if rule is TrueRule else '💡',
                *self.row_labels(row))
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

        ### Word must contain all listed letters in any order
        # "&ABC" => ContainsRule('A', 'B', 'C)
        #     Contains X, Y, Z
        #     Contains g, t
        m = re.match(r'&(.+)', arg)
        if m is not None:
            return ContainsRule(*m[1])

        # "xN" => RepeatedLetter(N)
        #     Double letter
        m = re.match(r'x(\d+)', arg)
        if m is not None:
            return RepeatedLetter(int(m[1]))

        # "+A" => MultiLetter('A')
        #     Multiple T’s
        m = re.match(r'\+([a-zA-Z])', arg)
        if m is not None:
            return MultiLetter(m[1])

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

    def do_set(self, ui: PromptUI):
        '''
        usage: `set <col> <row> <word>`
        '''

        col: int|None = None
        row: int|None = None
        word: str = ''

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
            if not word:
                word = next(ui.tokens)
                continue
            ui.print(f'! invalid * arg {next(ui.tokens)!r}')
            return

        if col is None:
            ui.print(f'! missing <col> arg')
            return
        if row is None:
            ui.print(f'! missing <row> arg')
            return

        word_i = (row - 1) * self.size + (col - 1)
        return self.question(ui, word_i, word)

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
            col = (word_i % self.size) + 1
            row = (word_i // self.size) + 1

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
            ui.copy(word)
            with ui.input(f'🌡️ {word} 📋 ? ') as tokens:
                if tokens:
                    score = tokens.have(r'\d*(\.\d*)?$', lambda m: float(m[0]))
                    if score is None:
                        return self.do_question
                    ui.log(f'word: {word_i} {word} {score}')
                    self.words[word_i] = word
                    self.scores[word_i][word] = score
        return self.question(ui, -1, '')

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
    def report_desc(self) -> str:
        res = self.result
        status = '🤔'
        score = nan
        if res:
            score = res.rarity
            status = label_rarity(score)
        return  f'{status} rarity:{score} ⏱️ {self.elapsed}'

    @property
    @override
    def report_body(self) -> Generator[str]:
        yield from super().report_body

        # TODO self.grid_labels(self)
        for row, _ in enumerate(self.row_rules):
            yield ' '.join(self.row_labels(row))

        res = self.result
        if res:
            yield f'Rarity: {res.rarity} {label_rarity(res.rarity)}'
            # TODO res.grid vs ^^

        # TODO describe how many attempts were used, and other historical/effort notes

@dataclass
class Result:
    id: int
    grid: tuple[str, ...]
    rarity: float

    @classmethod
    def parse(cls, s: str):
        id = -1
        grid: list[str] = []
        rarity = nan

        state = 0
        for line in spliterate(s, '\n', trim=True):
            # Word Grid #765
            if state == 0:
                m = re.match(r'''(?x)
                    Word \s+ Grid
                    \s+ \# (?P<id> \d+ )
                ''', line)
                if m:
                    id = int(m[1])
                    state = 1
                    continue

            # 🌌🟪🟦
            # 🌌🟦🟪
            # 🦄🦄🦄
            elif state == 1:
                if all(c in tiers for c in line):
                    grid.extend(line)
                    continue

                state = 2

            # Rarity: 2.58
            m = re.match(r'''(?x)
                Rarity :
                \s* (?P<rarity> \d* (?: \. \d* )? )
            ''', line)
            if m:
                rarity = float(m[1])
                continue

        return cls(
            id,
            tuple(grid),
            rarity,
        )

@MarkedSpec.mark('''

    #first
    > Word Grid #765
    > 🌌🟪🟦
    > 🌌🟦🟪
    > 🦄🦄🦄
    > Rarity: 2.58
    > wordgrid.clevergoat.com?ref=shared 🐐
    - id: 765
    - rarity: 2.58
    - grid: 🌌🟪🟦🌌🟦🟪🦄🦄🦄

    #second_3
    > Word Grid #766
    > 🌌🟨🟩
    > 🟦🟪🟪
    > 🦄🟦🟪
    > Rarity: 10.75
    > wordgrid.clevergoat.com?ref=shared 🐐
    - id: 766
    - rarity: 10.75
    - grid: 🌌🟨🟩🟦🟪🟪🦄🟦🟪

    #second_4
    > Word Grid #766
    > 🌌🌌🦄
    > 🌌🌌🟧
    > 🦄🦄🦄
    > Rarity: 3.73
    > wordgrid.clevergoat.com?ref=shared 🐐
    - id: 766
    - rarity: 3.73
    - grid: 🌌🌌🦄🌌🌌🟧🦄🦄🦄

''')
def test_parse_result(spec: MarkedSpec):
    res = Result.parse(spec.input)
    for key, value in spec.props:
        if key == 'id': assert str(res.id) == value
        elif key == 'rarity': assert str(res.rarity) == value
        elif key == 'grid': assert ''.join(res.grid) == value

# # Types of Categories
# 
# Here are some of the types of categories you might see:
# 
# | Category Type        | Example                | Rule                                              |
# |----------------------|------------------------|---------------------------------------------------|
# | X letter word        | 6-letter word          | Word must be exactly X letters long               |
# | Starts with X        | Starts with ph         | Word must begin with that letter/sequence         |
# | Ends with X          | Ends with ing          | Word must end in that letter/sequence             |
# | Contains X, Y, Z     | Contains g, t          | Word must contain all listed letters in any order |
# | Contains XY          | Contains th            | Word must include that exact sequence             |
# | Double letter        | Any letter             | Word must contain two identical letters in a row  |
# | Multiple letter X’s  | Multiple T’s           | Word must include that letter more than once      |
# | Starts & ends with X | Starts and ends with D | Word must start and end with the same letter      |
# | Infinity (∞)         | -                      | No restrictions. Any word is valid.               |
# 
# # Rarity Tiers
# 
# Every word earns a rarity score based on how many other players also picked it:
# - 🟩 Common (>5%)
# - 🟧 Uncommon (3-5%)
# - 🟨 Rare (1.5-3%)
# - 🟦 Epic (0.5-1.5%)
# - 🟪 Legendary (0.1-0.5%)
# - 🌌 Galaxy (<0.1%)
# - 🦄 Unicorn (only player to guess it)

if __name__ == '__main__':
    WordGrid.main()
