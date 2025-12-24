#!/usr/bin/env python

import argparse
import json
import math
import re
import subprocess
from collections.abc import Generator, Iterable
from contextlib import contextmanager
from dataclasses import dataclass
from typing import cast, final, override, Literal
from urllib.parse import urlparse

from store import StoredLog, git_txn, matcher
from strkit import MarkedSpec
from wordlist import Browser as WordBrowser, WordList, format_browser_lines, whatadded
from ui import PromptUI

@contextmanager
def text(ui: PromptUI, lines: Iterable[str]):
    text = ''.join(f'{line}\n' for line in lines)
    ui.print(text)
    def copy():
        ui.copy(text)
        ui.print('📋 copied')
    yield copy

Comparison = Literal[-1, 0, 1]

def rep_compare(c: Comparison):
    if c < 0: return 'before'
    if c > 0: return 'after'
    return 'it'

def parse_compare(s: str) -> Comparison|None:
    if 'after'.startswith(s):
        return 1
    elif 'before'.startswith(s):
        return -1
    elif 'it'.startswith(s):
        return 0
    else:
        return None

SearchResponse = tuple[Comparison, int]

@final
class Result:
    puzzle: int|None = None
    guesses: int|None = None
    time: str = ''
    link: str = ''

    @property
    def site(self):
        u = urlparse(self.link)
        return u.hostname or u.path

    @property
    def any_defined(self):
        if self.puzzle is not None: return True
        if self.guesses is not None: return True
        if self.time: return True
        if self.link: return True
        return False

    def log_items(self) -> Generator[tuple[str, str]]:
        if self.puzzle is not None: yield 'puzzle', str(self.puzzle)
        if self.guesses is not None: yield 'guesses', str(self.guesses)
        if self.time: yield 'time', self.time
        if self.link: yield 'link', self.link

    @classmethod
    def parse(cls, text: str):
        res = cls()

        some = False
        pat_puzzle = re.compile(r'🧩\s*(?:\w+\s*)?#(\d+)')
        pat_guess = re.compile(r'🤔\s*(\d+)(?:\s+\w+)?')
        pat_time = re.compile(r'⏱️\s*(.+)')
        pat_link = re.compile(r'🔗\s*(.+)')

        for line in text.splitlines():
            match = pat_puzzle.match(line)
            if match:
                res.puzzle = int(match.group(1))
                some = True
                continue
            match = pat_guess.match(line)
            if match:
                res.guesses = int(match.group(1))
                some = True
                continue
            match = pat_time.match(line)
            if match:
                res.time = match.group(1)
                some = True
                continue
            match = pat_link.match(line)
            if match:
                res.link = match.group(1)
                some = True
                continue

        if not some:
            raise ValueError('unrecognized result string')

        return res

@final
@dataclass
class Questioned:
    time: float
    lo: int
    q: int
    hi: int
    word: str
    resp: str

@final
@dataclass
class Prompt:
    time: float
    resp: str

    pattern = re.compile(r'''(?x)
        \s*
        >
        \s*

        (?P<resp> .* )

        $
    ''')

    @classmethod
    def match(cls, t: float, line: str):
        match = cls.pattern.match(line)
        if not match: return None
        (resp,) = match.groups()
        return cls(t, resp)

@final
@dataclass
class Done:
    time: float
    lo: int
    q: int
    hi: int
    i: int
    word: str

    pattern = re.compile(r'''(?x)
        # [351593 : 351592 : 351594]
        \s* \[ \s*
            (?P<lo> \d+ )
            \s* : \s*
            (?P<q> \d+ )
            \s* : \s*
            (?P<hi> \d+ )
        \s* \]

        # <Done>.
        \s+ <Done>\.

        # vanwege
        \s+ (?P<word> [^\s]+ )

        $
    ''')

    @classmethod
    def match(cls, t: float, line: str):
        match = cls.pattern.match(line)
        if not match: return None
        lo_s, q_s, hi_s, word = match.groups()
        lo, q, hi = int(lo_s), int(q_s), int(hi_s)
        i = q
        if (i < lo or i >= hi) and hi - lo == 1:
            i = lo
        return cls(t, lo, q, hi, i, word)

@final
class Search(StoredLog):
    log_file: str = 'binartic.log'
    default_wordlist: str = '/usr/share/dict/words'
    default_asof: str = 'main'

    @override
    def add_args(self, parser: argparse.ArgumentParser):
        super().add_args(parser)
        _ = parser.add_argument('--words', default=self.default_wordlist)
        _ = parser.add_argument('--asof', default=self.default_asof)

    @override
    def from_args(self, args: argparse.Namespace):
        super().from_args(args)
        wordlist = cast(str, args.words)
        if wordlist:
            self.default_wordlist = wordlist
            self.wordlist_file = wordlist
        self.default_asof = cast(str, args.asof)

    def __init__(self):
        super().__init__()

        self.wordlist_file: str = ''
        self.wordlist_asof: str = self.default_asof

        # loaded word list and pending edits
        self.wordlist: WordList|None = None
        self.words: list[str] = []
        self.wordix: list[int|None] = []
        self.inserts: set[str] = set()
        self.rejects: dict[str, int] = dict()

        # search state
        self.lo: int = 0
        self.hi: int = 0
        self.chosen: int|None = None
        self._result: Result|None = None

        # per-round prompt state
        self.view = WordBrowser(self.words)
        self.may_suggest: bool = True
        self.can_suggest: int|None = None
        self.questioning: int|None = None

        # history
        self.quest: list[Questioned] = []
        self.quest_adjust: list[tuple[int, int, int]] = []
        self.prompt_hist: list[Prompt] = []
        self.done: Done|None = None

        # stats
        self.added: int = 0
        self.attempted: int = 0
        self.entered: int = 0
        self.questioned: int = 0
        self.removed: int = 0
        self.suggested: int = 0
        self.guessed: int = 0

        self.review_prompt.set('show', self.show_quest)
        self.review_prompt.set('list', 'show')
        self.review_prompt.set('ls', 'list')
        self.review_prompt.set('summary', self.show_summary)

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
        self._result = res
        self.puzzle_id = f'#{res.puzzle}'
        if not self.site: self.site = res.site

    @result.deleter
    def result(self):
        self._result = None
        self.result_text = ''

    @override
    def have_result(self):
        return self.result is not None

    @override
    def proc_result(self, ui: PromptUI, text: str) -> None:
        super().proc_result(ui, text)
        if self.result:
            for k, v in self.result.log_items():
                ui.log(f'result {k}: {v}')

    @override
    def set_result_text(self, txt: str):
        del self.result
        super().set_result_text(txt)
        self.result = Result.parse(txt)

    ### words routines

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

    def adjust(self, qix: int, ix: int):
        for qi, i, adj in self.quest_adjust:
            if qi > qix:
                if ix >= i: ix += adj
        return ix

    @matcher(r'''(?x)
        wordlist \s+ insert :
        \s+ (?P<at> \d+ )
        \s+ (?P<word> [^\s]+ )
        \s* ( .* ) $''')
    def load_insert(self, _t: float, match: re.Match[str]):
        ixs, word, rest = match.groups()
        assert rest == ''
        ix = int(ixs)
        self.apply_insert(ix, word)

    def insert(self, ui: PromptUI, at: int, word: str):
        ui.log(f'wordlist insert: {at} {word}')
        self.apply_insert(at, word)

    def apply_insert(self, at: int, word: str):
        self.quest_adjust.append((len(self.quest), at, 1))
        self.words.insert(at, word)
        self.wordix.insert(at, None)
        if at < self.lo: self.lo += 1
        if at <= self.hi: self.hi += 1
        if self.questioning is not None and at <= self.questioning:
            self.questioning += 1
        self.added += 1
        self.inserts.add(word)

    def remove(self, at: int):
        self.quest_adjust.append((len(self.quest), at, -1))
        word = self.words.pop(at)
        actual = self.wordix.pop(at)
        if actual is not None:
            self.rejects[word] = actual
        if at < self.lo: self.lo -= 1
        if at <= self.hi: self.hi -= 1
        if self.questioning is not None and at <= self.questioning:
            self.questioning -= 1
        self.removed += 1

    ### ui routines

    @override
    def load(self, ui: PromptUI, lines: Iterable[str]):
        for t, rest in super().load(ui, lines):
            orig_rest = rest
            with ui.exc_print(lambda: f'while loading {orig_rest!r}'):

                pr = Prompt.match(t, rest)
                if pr is not None:
                    self.prompt_hist.append(pr)
                    continue

                dn = Done.match(t, rest)
                if dn is not None:
                    self.done = dn
                    continue

                yield t, rest

    @matcher(r'''(?x)
        loaded \s+ (?P<loaded> \d+ )
        \s+ words \s+ from
        \s+ (?P<file> [^\s]+ )
        \s+ (?P<sig> [^\s]+ )
        (?: \s* \( \s* (?P<excluded> \d+ ) \s+ words \s+ excluded \s* \) )?
        (?: \s+ asof \s+ (?P<asof> [^\s]+ ) )?
        \s* ( .* ) $''')
    def load_wordlist(self, _t: float, match: re.Match[str]):
        cs, file, sig, es, asof, rest = match.groups()
        assert rest == ''
        count = int(cs)
        excluded = None if not es else int(es)
        if not asof:
            log_added = self.stored and whatadded(self.log_file)
            if log_added:
                asof = f'{log_added}^'
        wl = WordList(file, asof=asof)
        try:
            wl.validate(sig, count, excluded)
        except ValueError as e:
            raise RuntimeError(f'invalid wordlist: {e}')
        self.set_wordlist(wl)

    def set_wordlist(self, wl: WordList):
        self.wordlist = wl
        self._set_words(wl.uniq_words)

    def set_words(self, ui: PromptUI, words: Iterable[str]):
        wordseq = sorted(words)
        ui.log(f'using {len(wordseq)} fixed words')
        self.wordlist = None
        self._set_words(wordseq)

    def _set_words(self, words: Iterable[str]|list[str]):
        self.words = words if isinstance(words, list) else sorted(words)
        self.wordix = list(range(len(self.words)))
        self.view = WordBrowser(self.words)
        self.lo = 0
        self.hi = len(self.words)

    @override
    def startup(self, ui: PromptUI) -> PromptUI.State|None:
        if self.words:
            ui.print(f'Using anonymous list of words')

        elif self.wordlist is not None:
            ui.print(f'Using wordlist {self.wordlist.name} (already loaded!)')
            ui.log(self.wordlist.describe)

        else:
            if not self.wordlist_file:
                with ui.input(f'📜 {self.default_wordlist} ? ') as tokens:
                    self.wordlist_file = next(tokens, self.default_wordlist)

            asof = self.wordlist_asof
            if asof:
                stdout = subprocess.check_output(['git' , 'rev-parse', asof], text=True)
                asof = stdout.partition('\n')[0]

            wl = WordList(self.wordlist_file, asof=asof)
            self.set_wordlist(wl)
            ui.log(wl.describe)

            if self.wordlist:
                ui.print(f'Using wordlist {self.wordlist.name}')

        if self.remain <= 0:
            ui.print('empty wordlist')
            raise StopIteration
        ui.print(f'searching {self.remain} words')

        if self.lo == 0 and self.hi == len(self.words):
            self.cmd_site_link(ui)

        return self.prompt

    @property
    def remain(self) -> int:
        return self.hi - self.lo

    @property
    def found(self) -> int|None:
        return None if self.chosen is None else self.chosen

    def prompt(self, ui: PromptUI):
        found = self.found
        if found is not None:
            word = self.words[found]
            ui.log(f'[{self.lo} : {found} : {self.hi}] <Done>.')
            ui.print(f'found: {word}')
            ui.copy(word)
            return self.finish

        if self.remain < 1:
            ui.log(f'[{self.lo} : ∅ : {self.hi}] <Fail>.')
            ui.print('Search failed; no more words possible')
            return self.store

        self.may_suggest = True
        self.can_suggest = None
        self.questioning = None
        self.view.at = math.floor(self.lo/2 + self.hi/2)
        return self.round

    def round(self, ui: PromptUI):
        res = self.question(ui) or self.choose(ui)
        if res is None: return None

        cmp, ix = res
        self.progress(ui, ix, cmp)

        return self.prompt

    @matcher(r'''(?x)
        # [0 : 98266 : 196598]
        \s* \[ \s*
            (?P<lo> \d+ )
            \s* : \s*
            (?P<q> \d+ )
            \s* : \s*
            (?P<hi> \d+ )
        \s* \]

        # mach?
        \s+
        (?P<word> [^\s]+ )
        \?

        # a
        \s+
        (?P<resp> .* )

        $''')
    def load_question(self, t: float, match: re.Match[str]):
        lo, q, hi, word, resp = match.groups()
        canon_resp = resp
        for code in ('after', 'before', 'it'):
            if code.startswith(resp.lower()):
                canon_resp = code
                break
        qn = Questioned(t, int(lo), int(q), int(hi), word, canon_resp)
        self.quest.append(qn)
        if qn.resp == '!':
            self.remove(qn.q)

    def question(self, ui: PromptUI, qi: int|None=None) -> SearchResponse|None:
        if qi is None:
            qi = self.questioning
            if qi is None: return
        else:
            self.questioning = qi
            self.questioned += 1

        word = self.words[qi]
        ui.copy(word)
        with ui.input(f'[{self.lo} : {qi} : {self.hi}] {word}? ') as tokens:
            if tokens.have(r'\.+$'):
                self.may_suggest = False
                self.questioning = None
                return

            self.quest.append(Questioned(ui.time.now, self.lo, qi, self.hi, word, tokens.raw))

            if tokens.have(r'!$'):
                self.remove(qi)
                self.questioning = None
                return

            if not tokens: return
            token = next(tokens)

            if tokens.rest:
                tokens.give(token)
                self.may_suggest = False
                self.questioning = None
                return self.handle_choose(ui)

            compare = parse_compare(token)
            if compare is not None:
                self.attempted += 1
                return compare, qi

            ui.print(f'! invalid direction {token} ; expected a(fter), b(efore), i(t), or ! (to remove word)')

    def view_notes(self) -> Generator[tuple[int, str]]:
        found = self.found

        qs = self.quest
        qw = len(str(len(qs)))
        q: Questioned|None = None
        for i, q in enumerate(qs):
            if q.word in self.rejects:
                continue
            ai = self.adjust(i, q.q)
            assert q.word == self.words[ai]
            yield ai, f'q{i:<{qw}} ? {q.resp}'

        if found is None:
            yield self.lo, '>>> SEARCH'
            yield self.hi-1, '<<< SEARCH'
            if self.can_suggest is not None:
                yield self.can_suggest, '??? SUGGEST'

        else:
            fqi = len(qs)
            if q and q.q == found: fqi -= 1
            ai = self.adjust(fqi, found)
            yield ai, f'done. it'

    def choose(self, ui: PromptUI) -> SearchResponse|None:
        if self.may_suggest:
            self.can_suggest = self.suggest()
            if self.can_suggest is not None:
                self.suggested += 1
                return self.question(ui, self.can_suggest)
            self.guessed += 1
            return self.question(ui, self.view.at)

        inotes = self.view.expand(self.view_notes(), limit=ui.screen_lines - 2)
        for line in format_browser_lines(self.words, inotes, at=self.view.at):
            ui.print(f'    {line}')

        ui.log(f'viewing: {self.view.describe} search: [ {self.lo} {self.hi} ]')

        return self.handle_choose(ui)

    def handle_choose(self, ui: PromptUI) -> SearchResponse|None:
        with ui.tokens_or('> ') as tokens:
            if self.view.handle(tokens):
                return

            at = self.select_word(ui)
            if at is not None:
                self.entered += 1
                self.view.cur = at
                return self.question(ui, at)

            if not tokens.empty:
                ui.print('! expected response like: `[<|^|>|+|-|0|<word>]...`')
                return

            return self.question(ui, self.view.at)

    def select_word(self, ui: PromptUI) -> int|None:
        with ui.tokens as tokens:
            if tokens.empty: return

            rel = tokens.have(r'@(.*)$', lambda m: cast(str, m[1]))
            if rel:
                offset = int(rel) if rel else 0
                return self.view.at + offset

            sug = tokens.have(r'\?(.*)', lambda m: cast(str, m[1]))
            if sug:
                if any(c != '?' for c in sug):
                    ui.print(f'! unknown suggestion command')
                    return

                n = len(sug) - 1
                if n > 0:
                    n -= 1

                    max_context = 1000 # TODO share with suggest
                    while n > 0 and self.view.context < max_context:
                        n -= 1
                        self.view.context *= 2

                    self.can_suggest = self.suggest()

                if self.can_suggest is None:
                    ui.print(f'! no suggestion available')
                return self.can_suggest

            word = next(tokens)
            at = self.find(word)
            if self.words[at] == word:
                return at

            confirm = tokens.next_or_input(ui, f'! unknown word {word} ; respond . to add, else to re-prompt> ')
            if confirm.strip() == '.':
                self.insert(ui, at, word)
                return at

    def suggest(self) -> int|None:
        max_context = 1000
        at = self.view.at
        context = min(max_context, self.view.context)
        lo = max(0, at - context)
        hi = min(len(self.words)-1, at + context)
        return self.valid_prefix(lo, hi)

    def progress(self, ui: PromptUI, ix: int, cmp: Comparison, word: str = ''):
        self.apply_progress(ix, cmp, word)
        ui.log(f'progress: {cmp} {ix} {word}')

    @matcher(r'''(?x)
        progress :
        \s+ (?P<cmp> -1|0|1 )
        \s+ (?P<index> \d+ )
        \s+ (?P<word> [^\s]+ )
        \s* ( .* ) $''')
    def load_progress(self, _t: float, match: re.Match[str]):
        if self.wordlist is None:
            raise RuntimeError('cannot load progress before wordlist')
        cs, ixs, word, rest = match.groups()
        assert rest == ''
        cmp = cast(Comparison, int(cs))
        ix = int(ixs)
        self.apply_progress(ix, cmp, word)

    def apply_progress(self, ix: int, cmp: Comparison, word: str = ''):
        if not word:
            word = self.words[ix]
        else:
            assert self.words[ix] == word
        if   cmp  < 0: self.hi = ix
        elif cmp  > 0: self.lo = ix + 1
        elif cmp == 0: self.chosen = ix
        else: raise ValueError('invalid comparison') # unreachable

    def finish(self, _ui: PromptUI) -> PromptUI.State|None:
        return self.finalize

    @property
    @override
    def run_done(self) -> bool:
        return self.result is not None

    @override
    def store_extra(self, ui: PromptUI, txn: git_txn):
        wl = self.wordlist
        if not wl: return

        if self.rejects:
            exc = wl.excluded_words
            exc.update(self.rejects)
            with open(wl.exclude_file, mode='w') as f:
                for w in sorted(exc):
                    print(w, file=f)
            txn.add(wl.exclude_file)

        if self.inserts and wl.name:
            uni = set(wl.cleaned_words)
            uni.update(self.inserts)
            with open(wl.name, mode='w') as f:
                for w in sorted(uni):
                    print(w, file=f)
            txn.add(wl.name)

    @override
    def review(self, ui: PromptUI) -> PromptUI.State|None:
        # TODO converge store result fixup

        i = self.found
        if i is not None: self.view.at = i

        res = self.result
        if res and not res.puzzle:
            del self.result

        if not self.result:
            with self.log_to(ui):
                ui.interact(self.finish)

        want_log_file = self.should_store_to
        if want_log_file and self.log_file != want_log_file:
            return self.store

        # TODO converge with
        # return super().review(ui)

        return self.show_quest

    @override
    def info(self):
        yield f'🤔 {len(self.quest)} attempts'
        yield f'📜 {len(self.sessions)} sessions'

    @property
    @override
    def report_desc(self) -> str:
        guesses = len(self.quest)
        status = '🥳' if self.result else '😦'
        return f'{status} {guesses} ⏱️ {self.elapsed}'

    @property
    @override
    def report_body(self) -> Generator[str]:
        yield from self.info()
        yield ''
        inotes = self.view.expand(self.view_notes(), limit=30)
        for line in format_browser_lines(self.words, inotes, at=self.view.at):
            yield f'    {line}'

    def show_summary(self, ui: PromptUI):
        with text(ui, self.summary(legend=True)) as copy:
            tokens = ui.input('summary> ')

            # TODO also use command dispatch rather than require bounce back to review_prompt

            token = tokens.peek('')
            if token and 'copy'.startswith(token):
                _ = next(tokens)
                copy()
                return

        return self.review_prompt

    def show_quest(self, ui: PromptUI):
        inotes = self.view.expand(self.view_notes(), limit=ui.screen_lines)
        lines = format_browser_lines(self.words, inotes, at=self.view.at)
        with text(ui, lines) as copy:
            tokens = ui.input('show> ')

            # TODO also use command dispatch rather than require bounce back to review_prompt

            token = tokens.peek('')

            if token and 'copy'.startswith(token):
                _ = next(tokens)
                copy()
                return

            if token == 'it':
                _ = next(tokens)
                i = self.found
                if i is not None: self.view.at = i
                return

            if token.startswith('q'):
                try:
                    qi = int(token[1:])
                except ValueError:
                    ui.print(f'! invalid q<INDEX> -- not an integer')
                    return

                try: 
                    q = self.quest[qi]
                except IndexError:
                    ui.print(f'! invalid q<INDEX> -- out of range [0 : {len(self.quest)}]')
                    return

                self.view.at = self.adjust(qi, q.q)
                return

        return self.review_prompt

    def history(self) -> Generator[Questioned|Prompt]:
        qi = 0
        pi = 0
        while True:
            qr = self.quest[qi] if qi < len(self.quest) else None
            pr = self.prompt_hist[pi] if pi < len(self.prompt_hist) else None

            if qr is not None and pr is not None:
                if qr.time < pr.time:
                    pr = None
                else:
                    qr = None

            if qr is not None:
                qi += 1
                yield qr
                continue

            if pr is not None:
                pi += 1
                yield pr
                continue

            break

    def summary(self, legend: bool = True):
        max_ix = max(max(r.lo, r.q, r.hi) for r in self.quest)
        t_width = max(4, max(len(f'{r.time:.1f}') for r in self.quest))
        ix_width = max(5, len(str(max_ix)))
        word_width = max(6, max(len(r.word) for r in self.quest))
        resp_width = max(8, max(len(r.resp) for r in self.quest))

        prior_t = 0

        yield f'T{"time":{t_width}} {"ΔT":>{t_width}} [ {"lo":{ix_width}} : {"query":{ix_width}} : {"hi":{ix_width}} ] {"<word>":{word_width}}? response ... analysis'

        done_i = None if self.done is None else self.done.i
        done_found = False

        for ent in self.history():
            t = ent.time

            dt = t - prior_t

            if isinstance(ent, Questioned):
                if ent.q == done_i: done_found = True

                w = ent.hi - ent.lo
                m = math.floor(ent.hi/2+ent.lo/2)
                b = ent.q - m
                yield f'T{t:{t_width}.1f} {dt:{t_width}.1f} [ {ent.lo:{ix_width}} : {ent.q:{ix_width}} : {ent.hi:{ix_width}} ] {ent.word:{word_width}}? {ent.resp:{resp_width}} ... wid:{w:{ix_width}} mid:{m:{ix_width}} bias:{b}'

            else: # elif isinstance(ent, Prompt):
                # TODO extract and report viewing window telemetry
                yield f'T{t:{t_width}.1f} {dt:{t_width}.1f} > {ent.resp}'

            prior_t = t

        if self.done is not None and not done_found:
            dn = self.done
            t = dn.time
            dt = t - prior_t
            yield f'T{t:{t_width}.1f} {dt:{t_width}.1f} [ {dn.lo:{ix_width}} : {dn.i:{ix_width}} : {dn.hi:{ix_width}} ] {dn.word:{word_width-1}} {"<Done>.":{resp_width+2}} ... by exhaustion'
            prior_t = t

        if legend:
            yield ''
            yield 'analysis legend:'
            yield '* wid -- search window width, aka `hi-lo`'
            yield '* mid -- classic binary search midpoint, aka `hi/2+lo/2`'
            yield '* bias -- prefix seeking bias applied, aka `query-mid`'

@MarkedSpec.mark(r'''

    #ex
    > 🧩 Puzzle #536
    > 
    > 🤔 12 guesses
    > 
    > ⏱️ 21s
    > 
    > 🔗 alphaguess.com
    - puzzle: 536
    - guesses: 12
    - time: 21s
    - link: alphaguess.com

    #reload
    > json:"\ud83e\udde9 Puzzle #536\n\n\ud83e\udd14 12 guesses\n\n\u23f1\ufe0f 21s\n\n\ud83d\udd17 alphaguess.com"
    - puzzle: 536
    - guesses: 12
    - time: 21s
    - link: alphaguess.com

''')
def test_parse_result(spec: MarkedSpec):
    sin = spec.input
    if sin.startswith('json:'):
        rej = cast(object, json.loads(sin[5:]))
        assert isinstance(rej, str)
        sin = rej
    res = Result.parse(sin)
    for name, value in spec.props:
        if name == 'puzzle': assert f'{res.puzzle}' == value
        elif name == 'guesses': assert f'{res.guesses}' == value
        elif name == 'time': assert f'{res.time}' == value
        elif name == 'link': assert f'{res.link}' == value
        else: raise ValueError(f'unknown test expectation {name}')

if __name__ == '__main__':
    Search.main()
