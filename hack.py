#!/usr/bin/env python

import builtins
import hashlib
import math
import os
import time
import re
from contextlib import contextmanager
from datetime import datetime, timedelta
from collections.abc import Generator, Iterable, Sequence
from typing import cast, final, Callable, Literal, TextIO

def ensure_parent_dir(file: str):
    pardir = os.path.dirname(file)
    if not os.path.exists(pardir):
        os.makedirs(pardir)

@final
class Timer:
    def __init__(self, start: float|None = None):
        self.start = time.clock_gettime(time.CLOCK_MONOTONIC) if start is None else start
        self.last = self.start

    @property
    def now(self):
        now = time.clock_gettime(time.CLOCK_MONOTONIC)
        return now - self.start

    def sub(self):
        return Timer(self.now)

Comparison = Literal[-1, 0, 1]
SearchResponse = tuple[Comparison, int]

@final
class PromptUI:
    def __init__(
        self,
        time: Timer|None = None,
        get_input: Callable[[str], str] = input,
        sink: Callable[[str], None] = lambda _: None,
        copy: Callable[[str], None] = lambda _: None,
        paste: Callable[[], str] = lambda: '',
    ):
        self.time = Timer() if time is None else time
        self.get_input = get_input
        self.sink = sink
        self.copy = copy
        self.paste = paste

    def log(self, mess: str):
        self.sink(f'T{self.time.now} {mess}')

    def print(self, mess: str):
        print(mess)

    def input(self, prompt: str) -> str:
        try:
            resp = self.get_input(prompt)
        except EOFError:
            self.log(f'{prompt}␚')
            raise
        self.log(f'{prompt}{resp}')
        return resp

    @contextmanager
    def deps(self,
             sink: Callable[[str], None] = lambda _: None,
             get_input: Callable[[str], str] = builtins.input,
             copy: Callable[[str], None] = lambda _: None,
             paste: Callable[[], str] = lambda: ''):
        prior_sink = self.sink
        prior_copy = self.copy
        prior_paste = self.paste
        prior_get_input = self.get_input
        try:
            if callable(sink): self.sink = sink
            if callable(copy): self.copy = copy
            if callable(paste): self.paste = paste
            if callable(get_input): self.get_input = get_input
            yield self
        finally:
            self.sink = prior_sink
            self.copy = prior_copy
            self.paste = prior_paste
            self.get_input = prior_get_input

@final
class Search:
    def __init__(
        self,
        ui: PromptUI,
        words: Iterable[str],
        context: int = 3,
        note_removed: Callable[[str], None] = lambda _: None):

        self.ui = ui
        self.words = sorted(words)
        self.note_removed = note_removed

        # view state
        self.context = context
        self.view_factor = 2
        self.min_context = self.context
        self.view_at = 0

        # per-round prompt state
        self.may_suggest = True
        self.can_suggest: int|None = None
        self.questioning: int|None = None

        # search state
        self.lo = 0
        self.hi = len(self.words)
        self.chosen: int|None = None

        # ... stats
        self.added = 0
        self.attempted = 0
        self.entered = 0
        self.questioned = 0
        self.removed = 0
        self.suggested = 0
        self.guessed = 0

    @property
    def view_lo(self):
        return max(0, self.view_at - self.context)

    @property
    def view_hi(self):
        return min(self.hi-1, self.view_at + self.context)

    @property
    def result_i(self) -> int|None:
        if self.chosen is not None:
            return self.chosen
        if self.remain == 1:
            return self.lo
        return None

    @property
    def qi(self) -> int:
        qi = self.questioning
        if qi is None:
            qi = self.view_at
        return qi

    @property
    def q_word(self):
        return self.words[self.qi]

    @property
    def result(self):
        i = self.result_i
        return None if i is None else self.words[i]

    @property
    def done(self):
        if self.result is not None:
            return True
        if self.remain <= 1:
            return True
        return False

    @property
    def remain(self) -> int:
        return self.hi - self.lo

    def remove(self, at: int):
        word = self.words.pop(at)
        self.note_removed(word)
        if at < self.lo: self.lo -= 1
        if at <= self.hi: self.hi -= 1
        if self.questioning is not None and at <= self.questioning:
            self.questioning -= 1
        self.removed += 1

    def insert(self, at: int, word: str):
        self.words.insert(at, word)
        if at < self.lo: self.lo += 1
        if at <= self.hi: self.hi += 1
        if self.questioning is not None and at <= self.questioning:
            self.questioning += 1
        self.added += 1

    def progress(self):
        if self.done:
            res = self.result
            self.ui.log(f'[{self.lo} : {self.qi} : {self.hi}] <Done>. {"<NORESULT>" if res is None else res}')
            raise StopIteration

        compare, index = self.prompt()
        self.ui.log(f'progress: {compare} {index} {self.words[index]}')

        if   compare  < 0: self.hi = index
        elif compare  > 0: self.lo = index + 1
        elif compare == 0: self.chosen = index
        else: raise ValueError('invalid comparison') # unreachable

    def find(self, word: str):
        qi = 0
        qj = len(self.words)-1
        while qi < qj:
            qk = math.floor(qi/2 + qj/2)
            qw = self.words[qk]
            if word == qw: return qk
            if   word < qw: qj = qk
            elif word > qw: qi = qk + 1
        return qi

    def common_prefix(self, i: int, j: int):
        a = self.words[i]
        b = self.words[j]
        n = min(len(a), len(b))
        k = 0
        while k < n and a[k] == b[k]: k += 1
        return a[:k]

    def valid_prefix(self, lo: int, hi: int):
        # NOTE window order from wider to narrower means first match
        #      will be the one that spans the most word list entries
        for win_lo, win_hi in (
            (lo+offset, lo+offset+n)
            for n in range(hi-lo, 1, -1)
            for offset in range(hi-lo - n + 1)
        ):
            prefix = self.common_prefix(win_lo, win_hi)
            while prefix:
                pi = self.find(prefix)
                if not (self.lo < pi < self.hi): break
                if self.words[pi] == prefix: return pi
                prefix = prefix[:-1]

    def prompt(self):
        self.may_suggest = True
        self.can_suggest = None
        self.questioning = None
        self.view_at = math.floor(self.lo/2 + self.hi/2)
        while True:
            res = self.question() or self.choose()
            if res is not None: return res

    def question(self, qi: int|None=None) -> SearchResponse|None:
        if qi is None:
            qi = self.questioning
            if qi is None: return
        else:
            self.questioning = qi
            self.questioned += 1

        word = self.words[qi]
        self.ui.copy(word)
        tokens = self.ui.input(f'[{self.lo} : {qi} : {self.hi}] {word}? ').lower().split()
        if len(tokens) > 1:
            self.may_suggest = False
            self.questioning = None
            return self.handle_choose(tokens)

        token = tokens[0] if len(tokens) > 0 else ''
        if all(c == '.' for c in token):
            self.may_suggest = False
            self.questioning = None
            return

        if token == '!':
            self.remove(qi)
            self.questioning = None
            return

        compare = parse_compare(token)
        if compare is None:
            self.ui.print(f'! invalid direction {token} ; expected a(fter), b(efore), i(t), or ! (to remove word)')
            return

        self.attempted += 1
        return compare, qi

    def choose(self) -> SearchResponse|None:
        if self.may_suggest:
            self.can_suggest = self.valid_prefix(self.view_lo, self.view_hi)
            if self.can_suggest is not None:
                self.suggested += 1
                return self.question(self.can_suggest)
            self.guessed += 1
            return self.question(self.view_at)

        show_lines = 0

        def show(mess: str):
            nonlocal show_lines
            self.ui.print(f'    {mess}')
            show_lines += 1

        cur = None

        def note(i: int, mess: str, elide: bool = True):
            nonlocal cur
            if elide and cur is not None and cur < i-1:
                show('...')
            cur = i
            show(mess)

        def mark(i: int, mark: str = '', elide: bool = True):
            note(i, f'[{i}] {self.words[i]}{mark}', elide=elide)

        screen_lines = os.get_terminal_size().lines

        mark(self.lo)
        if self.can_suggest is not None and self.can_suggest < self.view_lo:
            mark(self.can_suggest, ' <')

        less_lines = show_lines + 4
        free_lines = screen_lines - less_lines
        view_wid = self.view_hi - self.view_lo
        every = 1
        while every < view_wid and math.floor(view_wid / every) > free_lines:
            every *= 2

        if every > 1:
            note(self.view_lo, f'~~~ showing every {every}-th word for context {self.context}')

        for i in range(self.view_lo, self.view_hi, every):
            mark(i, ' @' if i == self.view_at else '', elide=i == self.view_lo)

        mark(self.hi-1)

        self.ui.log(f'viewing: @{self.view_at} C{self.context} [ {self.view_lo} {self.view_hi} ]~{every} search: [ {self.lo} {self.hi} ]')

        return self.handle_choose(self.ui.input('> ').lower().split())

    def handle_choose(self, tokens: Sequence[str]) -> SearchResponse|None:
        try:
            token = tokens[0]
        except IndexError:
            self.ui.print('! expected response like: `[<|^|>|+|-|0|<word>]...`')
            return

        if token == '<':
            self.view_at = max(self.view_lo, self.view_at - self.context)
            return
        if token == '>':
            self.view_at = min(self.view_hi, self.view_at + self.context)
            return
        if token == '^':
            self.view_at = math.floor(self.lo/2 + self.hi/2)
            return

        if token == '-':
            self.context *= self.view_factor
            return
        if token == '+':
            self.context = max(self.min_context, math.floor(self.context / 2))
            return
        if token == '0':
            self.context = self.min_context
            return

        at = self.find(token)
        if self.words[at] != token:
            confirm = (
                len(tokens) > 2 and tokens[2] or
                self.ui.input(f'! unknown word {token} ; respond . to add, else to re-prompt> '))
            if confirm.strip() == '.':
                self.insert(at, token)

        self.entered += 1
        return self.question(at)

def parse_compare(s: str) -> Comparison|None:
    if 'after'.startswith(s):
        return 1
    elif 'before'.startswith(s):
        return -1
    elif 'it'.startswith(s):
        return 0
    else:
        return None

@final
class WordList:
    def __init__(self, fable: TextIO):
        self.name = fable.name
        with fable as f:
            self.tokens = [
                line.strip().lower().partition(' ')[0]
                for line in f
            ]

    @property
    def describe(self):
        en = len(self.excluded_words)
        ex = f' ({en} words excluded)' if en > 0 else ''
        return f'loaded {self.size} words from {self.name} {self.sig.hexdigest()}{ex}'

    @property
    def words(self):
        return sorted(self.uniq_words)

    @property
    def uniq_words(self):
        return set(self.pruned_words)

    @property
    def pruned_words(self):
        exclude = set(self.excluded_words)
        for word in self.tokens:
            if "'" in word: continue # TODO other charset pruning?
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
    def exclude_file(self):
        return f'{os.path.splitext(self.name)[0]}.exclude.txt'

    @property
    def excluded_tokens(self):
        try:
            with open(self.exclude_file) as f:
                for line in f:
                    yield line.strip().lower().partition(' ')[0]
        except FileNotFoundError:
            pass

    @property
    def excluded_words(self):
        return set(self.excluded_tokens)

    def exclude_word(self, word: str):
        words = set(self.excluded_words)
        words.add(word)
        swords = sorted(words)
        with open(self.exclude_file, mode='w') as f:
            for w in swords:
                print(w, file=f)

@final
class ShareResult:
    puzzle: int|None = None
    guesses: int|None = None
    time: str|None = None
    link: str|None = None

    @property
    def any_defined(self):
        if self.puzzle is not None: return True
        if self.guesses is not None: return True
        if self.time is not None: return True
        if self.link is not None: return True
        return False

    def log_items(self) -> Generator[tuple[str, str]]:
        if self.puzzle is not None: yield 'puzzle', str(self.puzzle)
        if self.guesses is not None: yield 'guesses', str(self.guesses)
        if self.time is not None: yield 'time', self.time
        if self.link is not None: yield 'link', self.link

def parse_share_result(text: str) -> ShareResult:
    res = ShareResult()

    pat_puzzle = re.compile(r'🧩\s*(?:\w+\s*)?#(\d+)')
    pat_guess = re.compile(r'🤔\s*(\d+)(?:\s+\w+)?')
    pat_time = re.compile(r'⏱️\s*(.+)')
    pat_link = re.compile(r'🔗\s*(.+)')

    for line in text.splitlines():
        match = pat_puzzle.match(line)
        if match:
            res.puzzle = int(match.group(1))
            continue
        match = pat_guess.match(line)
        if match:
            res.guesses = int(match.group(1))
            continue
        match = pat_time.match(line)
        if match:
            res.time = match.group(1)
            continue
        match = pat_link.match(line)
        if match:
            res.link = match.group(1)
            continue

    return res

def main():
    import argparse
    import shlex
    import subprocess
    import traceback

    try:
        import pyperclip # pyright: ignore[reportMissingImports]
    except:
        print('WARNING: no clipboard access available')
        pyperclip = None

    from review import analyze

    parser = argparse.ArgumentParser()
    _ = parser.add_argument('--context', type=int, default=3, help='how many words to show +/- query');
    _ = parser.add_argument('--provide', help='command to run after clipboard copy');
    _ = parser.add_argument('--log', default='hack.log', type=argparse.FileType('w'))
    _ = parser.add_argument('--input', action='extend', nargs='+', type=str)
    _ = parser.add_argument('--at', nargs=2, type=int)
    _ = parser.add_argument('--words', default='/usr/share/dict/words', type=argparse.FileType('r'))
    _ = parser.add_argument('--store-log', default='log/')
    _ = parser.add_argument('--store-hist', default='hist.md')
    args = parser.parse_args()

    log_dir = cast(str, args.store_log)
    log_file = cast(TextIO, args.log)
    hist_file = cast(str, args.store_hist)
    words_io = cast(TextIO, args.words)
    provide_arg = cast(str, args.provide)
    given_input = cast(Sequence[str], args.input)
    view_context = cast(int, args.context)
    at_arg = cast(Sequence[int], args.at)

    provide_cmd = shlex.split(provide_arg) if provide_arg else ()
    view_window: None|tuple[int, int] = cast(tuple[int, int], tuple(at_arg)) if at_arg else None

    def write_log(mess: str):
        print(mess, file=log_file)
        log_file.flush()

    def clipboard_give(mess: str):
        if pyperclip:
            pyperclip.copy(mess) # pyright: ignore[reportUnknownMemberType]
        # else: TODO osc fallback?
        if provide_cmd:
            _ = subprocess.call(provide_cmd)

    def clipboard_get() -> str:
        if pyperclip:
            return pyperclip.paste() # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        return ''

    input_index = 0

    def get_input(prompt: str):
        nonlocal input_index
        if given_input and input_index < len(given_input):
            prov = given_input[input_index]
            ui.print(f'{prompt}{prov}')
            input_index += 1
            return prov
        return input(prompt)

    ui = PromptUI(
        sink=write_log,
        copy=clipboard_give,
        paste=clipboard_get,
        get_input=get_input,
    )

    def get_puzzle_id() -> tuple[int, ShareResult, str]:
        while True:
            resp = ui.input(f'enter puzzle id or copy share result and press <Return>: ')
            if resp:
                try:
                    puzzle_id = int(resp.strip())
                except ValueError:
                    ui.print('Invalid puzzle monotonic id; leave empty to parse clipboard')
                    continue
                return puzzle_id, ShareResult(), ''
            share_text = ui.paste().strip('\n')
            share_result = parse_share_result(share_text)
            puzzle_id = share_result.puzzle
            if puzzle_id is not None:
                return puzzle_id, share_result, share_text

    wordlist = WordList(words_io)
    ui.log(wordlist.describe)

    search = Search(
        ui,
        wordlist.uniq_words,
        context=view_context,
        note_removed=wordlist.exclude_word,
    )
    if view_window is not None:
        search.lo, search.hi = view_window

    try:
        ui.print(f'searching {search.remain} words')
        while search.remain > 0:
            search.progress()
    except EOFError:
        ui.print(' <EOF>')
    except KeyboardInterrupt:
        ui.print(' <INT>')
    except StopIteration:
        ui.print(' <STOP>')
    ui.print('')

    took = timedelta(seconds=ui.time.now)
    res = f'gave up' if search.result is None else f'found "{search.result}"'

    def details():
        if search.questioned != search.attempted:
            yield f'questioned:{search.questioned}'
        if search.guessed != 0:
            yield f'guessed:{search.guessed}'
        if search.suggested != 0:
            yield f'suggested:{search.suggested}'
        if search.entered != 0:
            yield f'manual:{search.entered}'
        if search.added != 0:
            yield f'added:{search.added}'
        if search.removed != 0:
            yield f'removed:{search.removed}'

    deets = ' '.join(details())
    if deets: deets = f' ( {deets} )'

    ui.print('')
    ui.print(f'{res} after {search.attempted} guesses in {took}{deets}')

    result_word = search.result
    if result_word is None: return
    ui.copy(result_word)
    ui.print(f'📋 search result "{result_word}"')

    puzzle_id, share_result, share_text = get_puzzle_id()
    for key, value in share_result.log_items():
        ui.log(f'result {key}: {value}')
    ui.print(f'🧩 {puzzle_id}')

    try:
        with open(log_file.name) as f:
            analysis = ''.join(f'{line}\n' for line in analyze(f)).strip('\n')
        ui.copy(analysis)
        ui.print('📋 Analysis')
        ui.print('```')
        ui.print(analysis)
        ui.print('```')
    except:
        ui.print(f'⚠️ Analysis failed')
        ui.print('```')
        ui.print(traceback.format_exc())
        ui.print('```')

    today = f'{datetime.today():%Y-%m-%d}'
    print(f'📆 {today}')

    git_added = False

    site = share_result.link

    if share_result.any_defined and hist_file:
        with open(hist_file, mode='a') as f:
            print(file=f)
            print(f'# {today} {site}'.strip(), file=f)
            print('```', file=f)
            print(share_text, file=f)
            print('```', file=f)
        _ = subprocess.check_call(['git', 'add', hist_file])
        git_added = True
        ui.print(f'📜 {hist_file}')

    if log_dir:
        puzzle_log_file = f'{log_dir}{site}/{puzzle_id}' if site else f'{log_dir}/{puzzle_id}'
        ensure_parent_dir(puzzle_log_file)
        os.rename(log_file.name, puzzle_log_file)
        _ = subprocess.check_call(['git', 'add', puzzle_log_file, wordlist.exclude_file])
        git_added = True
        ui.print(f'🗃️ {puzzle_log_file}')

    if git_added:
        mess = f'{site} day {puzzle_id}'.strip()
        _ = subprocess.check_call(['git', 'commit', '-m', mess])

if __name__ == '__main__':
    main()
