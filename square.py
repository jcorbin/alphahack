#!/usr/bin/env python

import argparse
import json
import math
import random
import re
from collections import Counter
from collections.abc import Generator, Iterable
from typing import cast, final, override

from store import StoredLog, git_txn
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
        _ = parser.add_argument('--wordlist', default=self.wordlist)

    @override
    def from_args(self, args: argparse.Namespace):
        super().from_args(args)
        self.wordlist = cast(str, args.wordlist)

    def __init__(self):
        super().__init__()

        self.wordlist: str = ''

        self.length: int = 5
        self.rejects: set[str] = set()

        self.word: list[list[str]] = [
            ['' for _ in range(self.length)]
            for _ in range(self.length)
        ]
        self.nope: set[str] = set()
        self.may: list[set[str]] = [set() for _ in range(self.length)]
        # TODO col hints?

        self.result_text: str = ''

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

        return self.display

    @property
    @override
    def run_done(self) -> bool:
        return all(
            all(let for let in word)
            for word in self.word
        )

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
                i = int(index)
                self.word[i] = ['' for _ in range(self.length)]
                self.may[i] = set()
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
                i = int(index)
                may = cast(str, may)
                self.may[i] = set(let.strip().lower() for let in may.split())
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
                reject :
                \s+ (?P<word> \w+ )
                \s* ( .* )
                $''', rest)
            if match:
                word, rest = match.groups()
                assert rest == ''
                self.rejects.add(word.lower())
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
                i = int(index)
                word = cast(str, word).lower()
                word = ['' if let == '_' else let for let in word]
                if len(word) > self.length:
                    word = word[:self.length]
                while len(word) < self.length: word.append('')
                self.word[i] = word
                continue

            yield t, rest

    def find(self, ui: PromptUI, pattern: re.Pattern[str]):
        ui.write(f'searching: {pattern.pattern}')
        with open(self.wordlist) as f:
            for line in f:
                line = line.strip().lower()
                word = line.partition(' ')[0]
                if word.lower() in self.rejects: continue
                if pattern.fullmatch(word): yield word

    def okay_letters(self) -> Generator[str]:
        for word in self.word:
            for let in word:
                if let: yield let
        for may in self.may:
            yield from may

    recent_sug: dict[str, int] = dict()

    def choose(self, ui: PromptUI, word_i: int|None = None):
        pattern: re.Pattern[str]|None = None
        if word_i is not None:
            p, _ = self.pattern(word_i)
            pattern = re.compile(p)
            ui.print(f'! [{word_i}] {p!r}')
        else:
            smallest = 0
            for i, word in enumerate(self.word):
                if all(word): continue
                p, space = self.pattern(i)
                ui.write(f'may:{space} ')
                p = re.compile(p)
                have = sum(1 for _ in self.find(ui, p))
                if not have: continue
                ui.write(f' found:{have}')
                ui.fin()
                if not pattern or have < smallest:
                    word_i, pattern, smallest = i, p, have
        ui.fin()

        # TODO try column patterns

        if not pattern: return

        best, choice = 0.0, ''
        count = 0
        okay = set(self.okay_letters())

        for word in self.find(ui, pattern):
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
        ui.fin()

    def pattern(self, word_i: int) -> tuple[str, int]:
        word = self.word[word_i]
        may = sorted(self.may[word_i])

        alpha = set('abcdefghijklmnopqrstuvwxyz')
        uni = '.'

        if self.nope:
            alpha.difference_update(self.nope)
            uni = f'[{"".join(char_ranges(alpha))}]'

        free = sum((1 for let in word if not let), 0)
        if may: free -= len(may)
        space: int = len(alpha)**free
        if may:
            for n in range(len(may), 1, -1): space *= n

        print(f'[{word_i}] may {may}')
        print(f'[{word_i}] word {word}')

        if not may:
            free = sum(1 for let in word if not let)
            if free == self.length:
                return uni * self.length, space
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

    def display(self, ui: PromptUI):
        if self.run_done:
            return self.finish

        for i, word in enumerate(self.word):
            ui.write(f'{i+1}  |  ')
            for let in word:
                ui.write(f' {let.upper() or "_"}')
            ui.write(f'  |  {" ".join(sorted(let.upper() for let in self.may[i]))}')
            ui.fin()

        if self.nope:
            ui.print(f'no: {" ".join(sorted(let.upper() for let in self.nope))}')

        with ui.input(f'> ') as tokens:
            return self.proc(ui)

    def finish(self, ui: PromptUI):
        with ui.input('Copy share result and press <Enter>'):
            self.result_text = ui.paste()
            ui.log(f'result: {json.dumps(self.result_text)}')

            # TODO parse
            # squareword.org 1031: 17 guesses
            #
            # 🟧🟨🟨🟨🟨
            # 🟩🟨🟩🟨🟩
            # 🟨🟧🟧🟩🟨
            # 🟨🟨🟨🟨🟨
            # 🟥🟨🟥🟥🟩
            #
            # <6:🟩 <11:🟨 <16:🟧 16+:🟥
            # #squareword #squareword1031

        return self.review

    @override
    def review(self, ui: PromptUI):
        if not self.result_text:
            with (
                git_txn(f'{self.site} {self.puzzle_id} result fixup') as txn,
                txn.will_add(self.log_file),
                self.log_to(ui),
            ):
                st = self.finish
                while not self.result_text:
                    st = st(ui) or st

        for i, word in enumerate(self.word):
            ui.write(f'{i+1}  |  ')
            for let in word:
                ui.write(f' {let.upper() or "_"}')
            ui.fin()

        with ui.input(f'> ') as tokens:
            pass

    def proc(self, ui: PromptUI):
        with ui.tokens as tokens:
            if tokens.have(r'\*'):
                return self.do_choose(ui)

            if tokens.have(r'n(o(pe?)?)?$'):
                for m in re.finditer(r'[A-Za-z]', tokens.rest):
                    self.nope.add(m.group(0).lower())
                ui.log(f'nope: {" ".join(sorted(self.nope))}')
                return

            n = tokens.have(r'(\d+):?', lambda m: int(m.group(1)))
            if n is None: return

            word_i = n - 1
            if word_i < 0 or word_i >= self.length: return

            if tokens.rest.strip() == '!':
                ui.log(f'forget: {word_i}')
                self.word[word_i] = ['' for _ in range(self.length)]
                self.may[word_i] = set()
                return

            if tokens.have(r'~$'):
                self.may[word_i] = set(
                    m.group(0).lower()
                    for m in re.finditer(r'[A-Za-z]', tokens.rest))
                ui.log(f'may: {word_i} {" ".join(sorted(self.may[word_i]))}')
                return

            may = self.may[word_i]
            word = self.word[word_i]
            ui.print(f'? {tokens.peek('')!r} {tokens.rest!r}')
            for i, m in enumerate(re.finditer(r'[_A-Za-z]', tokens.rest)):
                if i >= len(word):
                    ui.print('! too much input, truncating')
                    break
                let = m.group(0)
                if let != '_':
                    c = let.lower()
                    if word[i] != c:
                        word[i] = c
                        if c in may: may.remove(c)
                else:
                    word[i] = ''
            ui.log(f'may: {word_i} {" ".join(sorted(self.may[word_i]))}')
            ui.log(f'word: {word_i} {"".join(let or "_" for let in word)}')

    def do_choose(self, ui: PromptUI) -> PromptUI.State|None:
        word_n = ui.tokens.have(r'\d+$', lambda m: int(m.group(0)))
        word_i = None
        choice = ''
        count = 0

        for word_i, _, choice, count in self.choose(ui, None if word_n is None else word_n-1):
            pass

        if not choice: return
        assert word_i is not None

        ui.copy(choice)
        _, uni_count = self.pattern(word_i)
        with ui.input(f'{choice} ( #{word_i+1} found:{count} hypo:{uni_count} ) ? ') as tokens:
            if tokens.rest.strip() == '!':
                self.rejects.add(choice.lower())
                ui.log(f'reject: {choice}')
            return self.proc(ui) or self.display

if __name__ == '__main__':
    Search.main()
