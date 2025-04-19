#!/usr/bin/env python

import argparse
import re
from collections import Counter, OrderedDict
from collections.abc import Iterable
from typing import Literal, cast, final, override

from sortem import RandScores, Sample
from store import StoredLog
from ui import PromptUI

@final
class Search(StoredLog):
    log_file: str = 'spaceword.log'
    default_site: str = 'spaceword.org'
    default_wordlist: str = '/usr/share/dict/words'

    @override
    def add_args(self, parser: argparse.ArgumentParser):
        super().add_args(parser)
        _ = parser.add_argument('--wordlist')

    @override
    def from_args(self, args: argparse.Namespace):
        super().from_args(args)
        wordlist = cast(str, args.wordlist)
        if wordlist:
            self.wordlist = wordlist
            self.default_wordlist = wordlist

    def __init__(self):
        super().__init__()

        self.wordlist: str = ''
        self.given_wordlist: bool = False

        self.size = 10
        self.let_size: tuple[int, int] = (7, 3)

        self.letters: list[str] = []
        self.grid: list[str] = [''] * self.size**2

        self.cursor: tuple[int, int, Literal['X', 'Y']] = (0, 0, 'X')

    @override
    def load(self, ui: PromptUI, lines: Iterable[str]):
        for t, rest in super().load(ui, lines):
            orig_rest = rest
            with ui.exc_print(lambda: f'while loading {orig_rest!r}'):

                match = re.match(r'''(?x)
                    letters :
                    \s+
                    \|
                    (?P<letters> .* )
                    \|
                    $''', rest)
                if match:
                    self.letters = list(match[1])
                    continue

                match = re.match(r'''(?x)
                    at :
                    \s+ (?P<x> \d+ )
                    \s+ (?P<y> \d+ )
                    \s+ (?P<dir> [xyXY] )
                    $''', rest)
                if match:
                    x = int(match[1])
                    y = int(match[2])
                    xy = cast(Literal['X', 'Y'], match[3].upper())
                    self.cursor = x, y , xy
                    continue

                yield t, rest

    _find_cache: OrderedDict[str, tuple[str, ...]] = OrderedDict()

    def find(self, pattern: re.Pattern[str]):
        if pattern.pattern not in self._find_cache:
            maxsize = self.size**2
            while len(self._find_cache) >= maxsize:
                _ = self._find_cache.popitem(last=True)
            self._find_cache[pattern.pattern] = tuple(self._match_wordlist(pattern))
        else:
            self._find_cache.move_to_end(pattern.pattern)
        return self._find_cache[pattern.pattern]

    def _match_wordlist(self, pattern: re.Pattern[str]):
        with open(self.wordlist) as f:
            for line in f:
                line = line.strip().lower()
                word = line.partition(' ')[0]
                word = word.lower()
                if pattern.fullmatch(word): yield word

    @override
    def startup(self, ui: PromptUI):
        if not self.wordlist:
            with ui.input(f'📜 {self.default_wordlist} ? ') as tokens:
                self.wordlist = next(tokens, self.default_wordlist)
        if not self.given_wordlist:
            self.given_wordlist = True
            ui.log(f'wordlist: {self.wordlist}')

        nx, ny = self.let_size
        n = nx*ny
        if len(self.letters) != n:
            return self.edit_letters

        return self.play

    def show_letters(self, ui: PromptUI,
                     fill: str = '_',
                     head: str|None = '',
                     foot: str|None = '',
                     width: int = 0):
        nx, ny = self.let_size
        w = max(nx * 2, width)
        if head is not None:
            ui.print(f'-{head:-<{w-1}}')
        for y in range(ny):
            row = (
                self.letters[i] if i < len(self.letters) else fill
                for i in range(nx*y, nx*y+nx))
            srow = ''.join(f'{let} ' for let in row)
            ui.print(f'{srow: ^{w}}')
        if foot is not None:
            ui.print(f'-{foot:-<{w-1}}')

    def show_grid(self, ui: PromptUI,
                  head: str|None='',
                  foot: str|None=''):
        sz = self.size
        def cell_str(x: int, y: int):
            i = sz * y + x
            let = self.grid[i]
            mark = '@' if self.cursor[0] == x and self.cursor[1] == y else ' '
            return f'{let or '_'}{mark}'

        w = 2 * (self.size + 2)
        if head is not None:
            ui.print(f'-{head:-<{w-1}}')
        for y in range(sz):
            srow = ''.join(cell_str(x, y) for x in range(sz))
            ui.print(f'{srow: ^{w}}')
        if foot is not None:
            ui.print(f'-{foot:-<{w-1}}')
        return w

    def edit_letters(self, ui: PromptUI):
        self.show_letters(ui, fill = '?', head='Edit Letters')

        nx, ny = self.let_size
        n = nx*ny
        sep = (
            '!' if len(self.letters) > n else
            '.' if len(self.letters) == n else
            '?')
        with ui.input(f'letters{sep} ') as tokens:
            if tokens.empty:
                if sep == '.':
                    return self.play
                return

            if tokens.have('/clear'):
                self.letters = []
                ui.print('- cleared letters')
            else:
                addlet = [
                    let
                    for token in tokens
                    for let in token.strip().upper()]
                self.letters.extend(addlet)
                ui.print(f'- added lettes: {" ".join(addlet)}')

            ui.log(f'letters: |{"".join(self.letters)}|')

    def play(self, ui: PromptUI):
        width = self.show_grid(ui)
        self.show_letters(ui, head=None, width=width)

        with ui.input(f'> ') as tokens:
            if tokens.have(r'/let(ters)?'):
                return self.edit_letters

            gen = tokens.have(r'\*(.*)', lambda match: str(match[1]))
            if gen is not None:
                return self.generate(ui, gen)

            if tokens.have(r'@'):
                x = tokens.have(r'\d+', lambda match: int(match[0]))
                y = tokens.have(r'\d+', lambda match: int(match[0]))
                xy = cast(Literal['X', 'Y'], tokens.have(r'[xyXY]', lambda match: match[0].upper()) or 'X')
                if x is None or y is None or tokens:
                    ui.print('! usage: @ x y [X|Y]')
                    return
                self.cursor = x, y, xy
                ui.log(f'at: {x} {y} {xy}')
                return

            # TODO write from letters -> cursor

            ui.print(f'TODO wat {tokens.rest}')

    def generate(self, ui: PromptUI, arg: str = ''):
        cur_rem = (
            self.size - self.cursor[0] if self.cursor[2] == 'X'
            else self.size - self.cursor[1])

        # TODO consider cur_rum
        ideal_word_len = self.size // 2
        verbose = 0
        show_n = 10

        try:
            ideal_word_len = int(arg)
        except ValueError:
            pass

        choices: list[Sample.Choice|re.Pattern[str]] = []
        while ui.tokens:
            match = ui.tokens.have(r'-(v+)')
            if match:
                verbose += len(match.group(1))
                continue

            ch = (
                Sample.parse_choice_arg(ui.tokens, show_n=show_n) or
                ui.tokens.have(r'/(.+)', lambda match: re.compile(str(match[1]))))
            if ch is not None:
                choices.append(ch)
                continue

            ui.print(f'! invalid * arg {next(ui.tokens)!r}')
            return

        samp = Sample(
            Sample.compile_choices(choices,
                lambda pats: lambda i: any(
                    pat.search(line)
                    for line in display(i)
                    for pat in pats))
            if choices else (('top', show_n),))

        lc = Counter(self.letters)
        al = ''.join(sorted(lc)).lower()
        pattern = re.compile(f'[{al}]{{{1},{cur_rem}}}')

        ui.print(f'- find {pattern}')
        words = self.find(pattern)
        ui.print(f'- found: {len(words)}')

        words = tuple( word for word in words if not any(
            wn > lc[l]
            for l, wn in Counter(word.upper()).items()
        ))
        ui.print(f'- filtered: {len(words)}')

        midsc = tuple(
            1.0 - abs(ideal_word_len - len(word))/ideal_word_len
            for word in words)

        rand = RandScores(midsc, jitter = 0.5)

        scores = rand.scores

        def display(i: int):
            yield f'[{i}]'

            word = words[i]
            yield f'{word}'

        for n, i in enumerate(samp.index(scores), 1):
            mess = ' '.join(display(i)) # TODO wrapping ex hurdle/square
            ui.print(f'{n}. {mess}')

if __name__ == '__main__':
    Search.main()
