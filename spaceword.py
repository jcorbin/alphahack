#!/usr/bin/env python

import argparse
import re
from collections import Counter, OrderedDict
from collections.abc import Iterable
from typing import cast, final, override

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
        w = 2 * (sz + 2)
        if head is not None:
            ui.print(f'-{head:-<{w-1}}')
        for y in range(sz):
            row = (
                self.grid[i]
                for i in range(sz*y, sz*y+sz))
            srow = ''.join(f'{let or "_"} ' for let in row)
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

            # TODO * to search for words

            # TODO @x,y cursor

            # TODO write from letters -> cursor

            ui.print('TODO wat f{tokens.rest}')

    def generate(self, ui: PromptUI, arg: str = ''):
        gen_n = 10
        try:
            gen_n = int(arg)
        except ValueError:
            pass

        lc = Counter(self.letters)
        al = ''.join(sorted(lc)).lower()
        pattern = re.compile(f'[{al}]{{{1},{self.size}}}')

        ui.print(f'/{pattern}')
        words = self.find(pattern)
        ui.print(f'- found: {len(words)}')

        words = tuple( word for word in words if not any(
            wn > lc[l]
            for l, wn in Counter(word.upper()).items()
        ))
        ui.print(f'- filtered: {len(words)}')

        for i, word in enumerate(words):
            if i > gen_n-1: break
            ui.print(f'{i+1}. {word}')

if __name__ == '__main__':
    Search.main()
