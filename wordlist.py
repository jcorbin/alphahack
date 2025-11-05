import hashlib
import json
import math
import os
import subprocess
from collections.abc import Generator, Iterable, Sequence
from typing import final, TextIO

from store import atomic_rewrite, git_txn
from strkit import PeekIter
from ui import PromptUI

def whatadded(filename: str) -> str:
    output = subprocess.check_output([
        'git', 'log',
        '--pretty=%H',
        '--diff-filter=A',
        '--', filename], text=True)
    return output.partition('\n')[0]

def tokens_from(path_or_io: str|Iterable[str]) -> Generator[str]:
    if isinstance(path_or_io, str):
        with open(path_or_io) as f:
            yield from tokens_from(f)
        return
    for line in path_or_io:
        yield line.strip().lower().partition(' ')[0]

default_exclude_suffix = '.exclude.txt'

def exclude_file(name: str, exclude_suffix: str = ''):
    basename = os.path.splitext(name)[0]
    return f'{basename}{exclude_suffix or default_exclude_suffix}'

def merge_words_into(filename: str, words: Iterable[str]):
    words = PeekIter(sorted(words))
    with atomic_rewrite(filename) as (fr, fw):
        lines = PeekIter(fr)
        while lines and words:
            _ = fw.write(
                f'{next(words)}\n'
                if lines.peek('').strip().lower() > words.peek('').lower()
                else next(lines))
        fw.writelines(lines)
        fw.writelines(f'{word}\n' for word in words)

@final
class WordList:
    def __init__(self, fable: str|TextIO, asof: str = '', exclude_suffix: str = ''):
        self.name = fable if isinstance(fable, str) else str(fable.name)
        self.asof = asof
        self.exclude_file = exclude_file(self.name, exclude_suffix)
        self._tokens: tuple[str, ...]|None = None if isinstance(fable, str) else tuple(tokens_from(fable))

    @property
    def tokens(self):
        if self._tokens is None:
            self._tokens = tuple(tokens_from(self.name))
        return self._tokens

    def validate(self, sig: str|None = None, size: int|None = None, excludes: int|None = None):
        have_sig = self.sig.hexdigest()
        if sig and have_sig != sig:
            raise ValueError(f'expected signature {sig}, have {have_sig}')

        have_size = self.size
        if size is not None and have_size != size:
            raise ValueError(f'expected {size} words, have {have_size}')

        have_excludes = len(self.excluded_words)
        if excludes is not None and excludes != have_excludes:
            raise ValueError(f'expected {excludes} excludes, have {have_excludes}')

    @property
    def describe(self):
        en = len(self.excluded_words)
        ex = f' ({en} words excluded)' if en > 0 else ''
        desc = f'loaded {self.size} words from {self.name} {self.sig.hexdigest()}{ex}'
        if self.asof: desc = f'{desc} asof {self.asof}'
        return desc 

    @property
    def words(self):
        return sorted(self.uniq_words)

    @property
    def uniq_words(self):
        return set(self.pruned_words)

    @property
    def cleaned_words(self):
        for word in self.tokens:
            if "'" in word: continue # TODO other charset pruning?
            yield word

    @property
    def pruned_words(self):
        exclude = set(self.excluded_words)
        for word in self.cleaned_words:
            if word in exclude: continue
            yield word

    @property
    def size(self):
        return len(self.uniq_words)

    @property
    def sig(self):
        with open(self.name, 'rb') as f:
            return hashlib.file_digest(f, 'sha256')

    @property
    def exclude_file_tokens(self) -> Generator[str]:
        if self.asof:
            cmd = ['git', 'show', f'{self.asof}:{self.exclude_file}']
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True) as proc:
                assert proc.stdout
                yield from tokens_from(proc.stdout)

        else:
            try:
                yield from tokens_from(self.exclude_file)
            except FileNotFoundError:
                pass

    @property
    def excluded_words(self):
        return set(self.exclude_file_tokens)

    def add_word(self, word: str):
        merge_words_into(self.name, (word,))

    def add_words(self, words: Iterable[str]):
        merge_words_into(self.name, words)

    def remove_word(self, word: str):
        merge_words_into(self.exclude_file, word)

    def remove_words(self, words: Iterable[str]):
        merge_words_into(self.exclude_file, words)

    def do_bad(self, ui: PromptUI, *words: str, mark: str = ''):
        words = tuple(
            word.lower()
            for word in (words if words else ui.tokens))

        ui.log(f'bad: {json.dumps(words)}')

        known = self.uniq_words
        words = tuple(
            word
            for word in words
            if word in known)

        if len(words) == 0:
            ui.print('no known words given')
            return

        elif len(words) > 1:
            mess = f'bad words'
        else:
            mess = f'bad {words[0]!r}'

        if mark:
            mess = f'{mark} {mess}'
        else:
            mess = f'{self.exclude_file}: {mess}'

        with git_txn(mess, ui=ui) as txn:
            with txn.will_add(self.exclude_file):
                self.remove_words(words)

@final
class Browser:
    def __init__(
        self,
        words: Sequence[str],
        context: int = 3,
    ):
        self.words = words
        self.cur = 0
        self.setat = 0
        self.context = context
        self.last_context = context
        self.zoom_factor = 2
        self.min_context = self.context
        self.every = 1

    @property
    def lo(self):
        return max(0, self.cur - self.context)

    @property
    def hi(self):
        return min(len(self.words)-1, self.cur + self.context)

    @property
    def at(self):
        return self.cur

    @at.setter
    def at(self, at: int):
        self.cur = at
        self.setat = at

    @property
    def describe(self):
        desc = f'[ {self.lo} {self.hi} ]'
        if self.every > 1:
            desc = f'{desc}~{self.every}'
        desc = f'C{self.last_context} {desc}'
        desc = f'@{self.at} {desc}'
        return desc

    def expand(self, inotes: Iterable[tuple[int, str]], limit: int = 1) -> Generator[tuple[int, str]]:
        notes = sorted(inotes, key=lambda x: x[0])

        at = self.cur
        c = self.context

        lo = max(0, self.cur - c)
        hi = min(len(self.words)-1, self.cur + c)
        wid = hi - lo
        while wid > limit and c > 0:
            c -= 1
            lo = max(0, self.cur - c)
            hi = min(len(self.words)-1, self.cur + c)
            wid = hi - lo
        self.last_context = c

        in_notes = sum(1 for i, _ in notes if lo <= i < hi)
        out_notes = len(notes) - in_notes

        free_lines = limit
        free_lines -= out_notes

        while free_lines < in_notes:
            # trim furthest note
            try:
                ni, (i, _) = max(enumerate(notes), key=lambda inote: abs(inote[1][0] - at))
            except ValueError:
                break

            # at-notes are irreducible
            if i == at: break

            _ = notes.pop(ni)
            if out_notes > 0:
                out_notes -= 1
                free_lines += 1
            else:
                in_notes -= 1

        self.every = 1
        while self.every < wid and math.floor(wid / self.every) > free_lines:
            self.every *= 2

        notesi = 0

        def notes_thru(thru: int|None = None):
            nonlocal notesi
            while notesi < len(notes):
                i, note = notes[notesi]
                if thru is not None and i > thru: break
                yield i, note
                notesi += 1

        yield from notes_thru(lo-1)
        for i in range(lo, hi+1, self.every):
            some = False
            for i, note in notes_thru(i):
                yield i, note
                some = True
            if not some:
                yield i, ''
        yield from notes_thru()

    def handle(self, tokens: PromptUI.Tokens) -> bool:
        if tokens.have(r'<$'):
            self.cur = max(self.lo, self.cur - self.context)
            return True
        if tokens.have(r'>$'):
            self.cur = min(self.hi, self.cur + self.context)
            return True
        if tokens.have(r'^$'):
            self.cur = self.setat
            return True

        match = tokens.have(r'@([\-+]?\d+)')
        if match:
            self.cur += int(match[1])
            return True

        if tokens.have(r'-$'):
            self.context *= self.zoom_factor
            return True
        if tokens.have(r'\+$'):
            self.context = max(self.min_context, math.floor(self.context / 2))
            return True
        if tokens.have('0$'):
            self.context = self.min_context
            return True

        return False

def format_browser_lines(words: Sequence[str],
                         inotes: Iterable[tuple[int, str]],
                         at: int|None = None):
    ix: list[int] = []
    notes: list[str] = []
    for i, note in inotes:
        ix.append(i)
        notes.append(note)

    ix_words = [words[i] for i in ix]
    word_width = max(len(w) for w in ix_words)

    ix_width = max(len(str(i)) for i in ix)

    if at is None:
        for i, word, note in zip(ix, ix_words, notes):
            yield f'[{i:>{ix_width}}] {word:<{word_width}} {note}'
    else:
        deltas = list('@' if i == at else f'@{i - at:+}' for i in ix)
        delta_width = max(len(d) for d in deltas)
        for delta, i, word, note in zip(deltas, ix, ix_words, notes):
            yield f'{delta:<{delta_width}} [{i:>{ix_width}}] {word:<{word_width}} {note}'
