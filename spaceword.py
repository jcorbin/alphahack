#!/usr/bin/env python

import argparse
import re
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

    @override
    def startup(self, ui: PromptUI):
        if not self.wordlist:
            with ui.input(f'📜 {self.default_wordlist} ? ') as tokens:
                self.wordlist = next(tokens, self.default_wordlist)
        if not self.given_wordlist:
            self.given_wordlist = True
            ui.log(f'wordlist: {self.wordlist}')

        return self.edit_letters

    def show_letters(self, ui: PromptUI, fill: str = '_'):
        nx, ny = self.let_size
        rule = f'|{"|".join(["---"] * nx)}|'
        ui.print(rule)
        for y in range(ny):
            row = (
                self.letters[i] if i < len(self.letters) else fill
                for i in range(nx*y, nx*y+nx))
            ui.print(f'| {" | ".join(row)} |')
        ui.print(rule)

    def edit_letters(self, ui: PromptUI):
        self.show_letters(ui, fill = '?')

        nx, ny = self.let_size
        n = nx*ny
        sep = (
            '!' if len(self.letters) > n else
            '.' if len(self.letters) == n else
            '?')
        with ui.input(f'letters{sep} ') as tokens:
            if tokens.empty:
                ui.print(f'NOP {tokens.rest!r}')
                if sep == '.':
                    return self.play
                return

            if tokens.have('/clear'):
                ui.print('- cleared letters')
            else:
                ui.print(f'EXT {tokens.rest!r}')
                self.letters.extend(
                    let
                    for token in tokens
                    for let in token.strip().upper())

            self.letters = []
            ui.log(f'letters: |{"".join(self.letters)}|')

    def play(self, ui: PromptUI):
        # TODO show grid
        self.show_letters(ui)

        with ui.input(f'> ') as tokens:
            if tokens.have(r'/let(ters)?'):
                return self.edit_letters

            ui.print('TODO wat f{tokens.rest}')

            # TODO * to search for words

            # TODO @x,y WORD

if __name__ == '__main__':
    Search.main()
