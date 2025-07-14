#!/usr/bin/env python

import argparse
import json
import re
from collections import Counter, OrderedDict
from collections.abc import Generator, Iterable, Sequence
from dataclasses import dataclass
from itertools import chain
from typing import Callable, cast, final, overload, override

from sortem import Chooser, DiagScores, Possible, RandScores, wrap_item
from store import StoredLog, git_txn
from strkit import MarkedSpec, PeekStr, spliterate
from ui import PromptUI
from wordlish import Attempt, Word
from wordlist import WordList

@final
class Search(StoredLog):
    log_file: str = 'squareword.log'
    default_site: str = 'squareword.org'
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
            self.wordlist_file = wordlist
            self.default_wordlist = wordlist

    def __init__(self):
        super().__init__()

        self.size: int = 5
        self.wordlist_file: str = ''
        self.given_wordlist: bool = False
        self._wordlist: WordList|None = None

        self.grid: list[str] = ['' for _ in range(self.size**2)]

        self.choosing: tuple[int, Word, Possible[str]]|None = None

        self.qmode: str = '?'
        self.questioning: str = ''
        self.question_desc: str = ''

        self.guesses: dict[str, int] = dict() # TODO keep feedback alongside or use Attempt
        self.rejects: set[str] = set()

        self.nope: set[str] = set()
        self.row_may: tuple[set[str], ...] = tuple(set() for _ in range(self.size))

        self.result_text: str = ''
        self._result: Result|None = None

        self.prompt = PromptUI.Prompt(self.prompt_mess, {
            '/attempts': self.do_attempts,
            '/gen': self.do_gen,
            '/guesses': self.do_guesses,
            '/man': self.do_manual_gen,
            '/nope': self.do_nope,
            '*': '/gen',
            '!': '/nope',
            '': self.do_word,
        })

    @property
    def wordlist(self):
        if self._wordlist is not None:
            if self._wordlist.name != self.wordlist_file:
                self._wordlist = None
        if self._wordlist is None:
            self._wordlist = WordList(
                self.wordlist_file,
                exclude_suffix='.squareword_exclude.txt')
        return self._wordlist

    @property
    def result(self):
        if self._result is None and self.result_text:
            try:
                res = Result.parse(self.result_text, self.size)
            except ValueError:
                return None
            self._result = res
        return self._result

    @result.deleter
    def result(self):
        self._result = None

    @override
    def startup(self, ui: PromptUI):
        if not self.puzzle_id:
            ui.br()
            if not self.wordlist_file:
                with ui.input(f'📜 {self.default_wordlist} ? ') as tokens:
                    self.wordlist_file = next(tokens, self.default_wordlist)
            self.do_puzzle(ui)
            if not self.puzzle_id: return

        if not self.wordlist_file:
            self.wordlist_file = self.default_wordlist

        if not self.given_wordlist:
            self.given_wordlist = True
            ui.log(f'wordlist: {self.wordlist_file}')

        if self.questioning:
            return self.question

        if self.choosing is not None:
            return self.present_choice

        return self.display

    @property
    @override
    def run_done(self) -> bool:
        return all(let for let in self.grid)

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
            orig_rest = rest
            with ui.exc_print(lambda: f'while loading {orig_rest!r}'):

                match = re.match(r'''(?x)
                    wordlist :
                    \s+
                    (?P<wordlist> [^\s]+ )
                    \s* ( .* )
                    $''', rest)
                if match:
                    wordlist, rest = match.groups()
                    assert rest == ''
                    self.wordlist_file = wordlist
                    self.given_wordlist = True
                    continue

                match = re.match(r'''(?x)
                    forget :
                    \s+ (?P<index> \d+ )
                    \s* ( .* )
                    $''', rest)
                if match:
                    index, rest = match.groups()
                    assert rest == ''
                    self.forget(ui, int(index))
                    continue

                match = re.match(r'''(?x)
                    may :
                    \s+ (?P<index> \d+ )
                    (?P<may> (?: \s+ [A-Za-z] )* )
                    \s* ( .* )
                    $''', rest)
                if match:
                    index, may, rest = match.groups()
                    assert rest == ''
                    word_i = int(index)
                    may = cast(str, may)
                    rm = self.row_may[word_i]
                    rm.clear()
                    rm.update(let.strip().upper() for let in may.split())
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
                    self.nope = set(let.strip().upper() for let in may.split())
                    continue

                match = re.match(r'''(?x)
                    questioning :
                    \s* (?P<json> .+ )
                    $''', rest)
                if match:
                    raw, = match.groups()
                    dat = cast(object, json.loads(raw))
                    assert isinstance(dat, list)
                    dat = cast(list[object], dat)
                    assert len(dat) == 2
                    word, desc = dat
                    assert isinstance(word, str)
                    assert isinstance(desc, str)
                    _ = self.ask_question(ui, word, desc)
                    continue

                match = re.match(r'''(?x)
                    question \s+ done
                    \s* ( .* )
                    $''', rest)
                if match:
                    rest, = match.groups()
                    assert rest == ''
                    self.question_done(ui)
                    continue

                match = re.match(r'''(?x)
                    guess :
                    \s* (?P<word> \w+ )
                    \s* ( .* )
                    $''', rest)
                if match:
                    word, rest = match.groups()
                    assert rest == ''
                    _ = self.question_guess(ui, word)
                    continue

                match = re.match(r'''(?x)
                    reject :
                    \s+ (?P<word> \w+ )
                    \s* ( .* )
                    $''', rest)
                if match:
                    word, rest = match.groups()
                    assert rest == ''
                    self.question_reject(ui, word)
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
                    word_i = int(index)
                    word = cast(str, word).upper()
                    word = ['' if let == '_' else let for let in word]
                    if len(word) > self.size:
                        word = word[:self.size]
                    while len(word) < self.size: word.append('')
                    for j, c in zip(self.row_word_range(word_i), word):
                        self.grid[j] = c
                    continue

                match = re.match(r'''(?x)
                    result :
                    \s* (?P<json> .+ )
                    $''', rest)
                if match:
                    (raw), = match.groups()
                    dat = cast(object, json.loads(raw))
                    assert isinstance(dat, str)
                    self.result_text = dat
                    continue

                yield t, rest

    def find(self,
             pattern: re.Pattern[str],
             row: int|None = None,
             verbose: Callable[[str], None]|None = None,
             ) -> Generator[str]:
        if row is not None:
            col_may: tuple[set[str], ...] = tuple(set() for _ in range(self.size))
            for col in range(self.size):
                sel = self.select(col=col, avoid=False)
                col_may[col].update(word[row].upper() for word in self._find(sel.pattern))
            if verbose:
                for n, may in enumerate(col_may, 1):
                    verbose(f'col_may_{n}: [{''.join(sorted(may))}]')

            for word in self._find(pattern):
                if all(
                    word[col] in may
                    for col, may in enumerate(col_may)):
                    yield word
                elif verbose:
                    verbose(f'skip:{word}')
            return

        yield from self._find(pattern)

    _find_cache: OrderedDict[str, list[str]] = OrderedDict()

    def _find(self, pattern: re.Pattern[str]):
        if pattern.pattern not in self._find_cache:
            maxsize = self.size**2
            while len(self._find_cache) >= maxsize:
                _ = self._find_cache.popitem(last=True)
            self._find_cache[pattern.pattern] = list(self._match_wordlist(pattern))
        else:
            self._find_cache.move_to_end(pattern.pattern)

        for word in self._find_cache[pattern.pattern]:
            if word in self.rejects: continue
            if word in self.guesses: continue
            yield word

    def _match_wordlist(self, pattern: re.Pattern[str]):
        for word in self.wordlist.words:
            if pattern.fullmatch(word):
                yield word.upper()

    def okay_letters(self) -> Generator[str]:
        for let in self.grid:
            if let: yield let
        for may in self.row_may:
            yield from may

    recent_sug: dict[str, int] = dict()

    def score_words(self,
                    word_i: int,
                    words: Sequence[str],
                    jitter: float = 0.5,
                    ):
        diag = DiagScores(words)

        # count letters not yet seen in prior rounds
        seen = set(self.okay_letters())
        unseens = [
            sum(1 for let in word if let not in seen)
            for word in words]

        # count overlaps with prior attempts
        row_unk = tuple(
            i
            for i, k in enumerate(self.row_word_range(word_i))
            if not self.grid[k])
        neg_unk = set(
            (i, prior[i])
            for prior in self.guesses
            for i in row_unk)
        negs = [
            (sum(1
                for i, l in enumerate(word)
                if (i, l) in neg_unk) + 1)**3
            for word in words]

        # combine scores
        scores = [
            score / neg if neg > 1
            else score * (unseen + 1) if unseen > 0
            else score
            for score, unseen, neg in zip(diag.scores, unseens, negs)]

        rand = None
        if jitter != 0:
            rand = RandScores(scores, jitter)
            scores = rand.scores

        def annotate(i: int) -> Generator[str]:
            score = scores[i]
            yield f'{100*score:0.2f}%'

            if rand is not None:
                yield from rand.explain(i)

            yield from diag.explain(i)

            neg = negs[i]
            if neg > 1:
                yield f'/= neg:{neg}'
            else:
                yield f'*= unseen:{100*unseens[i]:.1f}%'

            wf_parts = list(diag.explain_wf(i))
            if wf_parts:
                yield f'WF:{" ".join(wf_parts)}'
            yield f'LF:{" ".join(diag.explain_lf(i))}'
            yield f'LF norm:{" ".join(diag.explain_lf_norm(i))}'

        return scores, annotate

    @final
    class Select:
        def __init__(self,
                     yes: Iterable[str],
                     may: Iterable[str] = (),
                     void: Iterable[str] = (),
                     nope: Iterable[str] = (),
                     guesses: Iterable[str] = (),
                     row: int|None = None,
                     col: int|None = None,
                     ):
            self.yes = tuple(l.upper() for l in yes)
            self.may = tuple(l.upper() for l in may)
            self.nope = tuple(l.upper() for l in nope)
            self.void = tuple(l.upper() for l in void)
            self.guesses = tuple(w.upper() for w in guesses)
            self.row = row
            self.col = col
            self.word = Word(len(self.yes))
            word = self.word
            for c in self.void:
                if c not in self.yes:
                    word.cannot(c)
            if self.guesses:
                for at in self.attempts:
                    word.collect(at)
                for i, c in enumerate(self.yes):
                    word.yes[i] = c
            else:
                for i, c in enumerate(self.yes):
                    word.yes[i] = c
                word.may.update(self.may)
                for c in self.nope:
                    word.cannot(c)
                for guess in self.guesses:
                    for i, c in enumerate(guess):
                        if self.yes[i] != c:
                            word.can[i].difference_update((c,))

        def feedback(self, word: str):
            mx = self.word.max
            may: Counter[str] = Counter()
            for i, c in enumerate(word):
                y = self.yes[i]
                if y == c:
                    yield 2
                    continue

                if c in self.nope or c in self.void:
                    yield 0
                    continue

                if c in self.yes or c in self.may:
                    x = mx.get(c, None)
                    if x is None or may[c] < x:
                        may[c] += 1
                        yield 1
                        continue

                yield 0

        @property
        def attempts(self):
            for guess in self.guesses:
                yield Attempt(guess, tuple(self.feedback(guess)))

        @override
        def __str__(self):
            def parts():
                if self.row is not None:
                    yield f'row:{self.row}'
                elif self.col is not None:
                    yield f'col:{self.col}'
                yield f'{self.word}'
                if not self.word.done:
                    yield f'({self.word.possible} possible)'
            return ' '.join(parts())

        @property
        def size(self):
            return len(self.word)

        @property
        def pattern(self):
            return self.word.pattern()

    @overload
    def select(self, *, row: int, avoid: bool = True) -> Select: pass

    @overload
    def select(self, *, col: int, avoid: bool = True) -> Select: pass

    def select(self, *, row: int|None = None, col: int|None = None, avoid: bool = True) -> Select:
        prior = set(
            l
            for prior in self.guesses
            for l in prior)

        if row is not None:
            word = tuple(self.grid[k] for k in self.row_word_range(row))
            may = self.row_may[row]
            maybe_not = prior.difference(chain(may, word))
            # TODO reduce possible based on intersecting cols
            return self.Select(
                word,
                may = may,
                void = maybe_not if avoid else (),
                nope = self.nope,
                guesses = self.guesses, # TODO collect and pass attempts instead?
                row = row)

        elif col is not None:
            word = tuple(self.grid[k] for k in self.col_word_range(col))
            maybe_not = prior.difference(word)
            # TODO reduce possible based on intersecting rows
            return self.Select(
                word,
                void = maybe_not if avoid else (),
                nope = self.nope,
                col = col)

        else:
            raise RuntimeError('must provide either row or col')

    skip_show: bool = False

    def show(self, ui: PromptUI):
        if self.skip_show:
            self.skip_show = False
            return
        for word_i in range(self.size):
            ui.print(' | '.join(self.show_parts(word_i)))
        if self.nope:
            ui.print(f'no: {" ".join(sorted(let.upper() for let in self.nope))}')

    def show_parts(self, word_i: int):
        grid_yes = tuple(
            self.grid[k].upper().strip()
            for k in self.row_word_range(word_i))

        yield f'#{word_i+1}'
        yield ' '.join(c or '_' for c in grid_yes)
        yield ' '.join(sorted(let.upper() for let in self.row_may[word_i]))

    def prompt_mess(self, ui: PromptUI):
        self.show(ui)
        return '> '

    def display(self, ui: PromptUI):
        if self.run_done:
            return self.finish
        return self.prompt(ui)

    def do_guesses(self, ui: PromptUI):
        for word in self.guesses:
            ui.print(f'Guesses ({len(self.guesses)})')
            ui.print(f'- {word}')

    def do_nope(self, ui: PromptUI):
        for m in re.finditer(r'[.A-Za-z]', ui.tokens.rest):
            c = m.group(0).upper()
            if c == '.':
                self.nope.clear()
            else:
                self.nope.add(c)
        ui.log(f'nope: {" ".join(sorted(self.nope))}')

    def do_word(self, ui: PromptUI):
        word_i = self.re_word_i(ui)
        if word_i is not None:
            if ui.tokens.rest.strip() == '!':
                self.forget(ui, word_i)
                return

        token = next(ui.tokens, None)
        if not token: return

        if token.startswith('/'):
            ui.print(f'! invalid command {token!r}; maybe ask for /help ?')
            return

        if len(token) != self.size:
            ui.print(f'! wrong size {token!r}')
            return

        return self.ask_question(ui, token, 'entered')

    def row_word_range(self, row: int):
        return range(row * self.size, (row+1) * self.size)

    def col_word_range(self, col: int):
        return range(col, len(self.grid), self.size)

    def forget(self, ui: PromptUI, word_i: int):
        ui.log(f'forget: {word_i}')
        for j in self.row_word_range(word_i):
            self.grid[j] = ''
        self.row_may[word_i].clear()

    def finish(self, _ui: PromptUI):
        return self.finalize

    @override
    def have_result(self):
        return self.result is not None

    @override
    def proc_result(self, ui: PromptUI, text: str):
        self.result_text = text
        del self.result
        if self.have_result():
            ui.log(f'result: {json.dumps(text)}')

    @override
    def review(self, ui: PromptUI):
        # TODO common store result fixup routine
        if not self.result:
            with (
                git_txn(f'{self.site} {self.puzzle_id} result fixup') as txn,
                txn.will_add(self.log_file),
                self.log_to(ui),
            ):
                ui.interact(self.finish)
            return

        return super().review_prompt(ui)

    @property
    @override
    def report_desc(self) -> str:
        res = self.result
        guesses = res.guesses if res else '???'
        status = '🥳' if res else '😦'
        return  f'{status} {guesses} ⏱️ {self.elapsed}'

    @property
    @override
    def report_body(self) -> Generator[str]:
        yield from super().report_body

        yield ''
        yield 'Guesses:'
        for word, i in sorted(self.guesses.items(), key = lambda x: x[1]):
            yield f'{i+1}. {word}'

        res = self.result
        if res:
            yield ''
            yield 'Score Heatmap:'
            for row in res.score_rows:
                yield f'    {" ".join(row)}'
            yield f'    {res.legend_str}'

        yield ''
        yield 'Solution:'
        for word_i in range(self.size):
            lets = ' '.join(
                f'{self.grid[k].upper() or "_"}'
                for k in self.row_word_range(word_i))
            yield f'    {lets}'

    def proc_re_word(self, ui: PromptUI, word_i: int):
        with ui.tokens as _tokens:
            match = self.re_word_match(ui)
            if match:
                return self.proc_re_word_match(ui, word_i, match)
        return False

    def re_word_match(self, ui: PromptUI):
        rest = ui.tokens.rest
        match = re.match(r'''(?x)
            \s* (?P<word> [_A-Za-z ]+ )
            (?: \s* ~ \s* (?P<may> [A-Za-z ]* ) )?
        ''', rest) or re.match(r'''(?x)
            (?P<word> )
            \s* ~ \s* (?P<may> [A-Za-z ]* )
        ''', rest)
        if match:
            ui.tokens.rest = rest[match.end(0):] 
        return match

    def proc_re_word_match(self, ui: PromptUI, word_i: int, match: re.Match[str]):
        word_str = cast(str, match.group(1) or '')
        may_str = cast(str|None, match.group(2))

        may = self.row_may[word_i]

        if word_str:
            lets = (c for c in word_str if c != ' ')
            offset = word_i * self.size
            for i, let in enumerate(lets):
                if i >= self.size:
                    ui.print('! too much input, truncating')
                    break
                c = let.upper()
                if let == '_':
                    self.grid[offset + i] = ''
                elif self.grid[offset + i] != c:
                    self.grid[offset + i] = c
                    if c in may: may.remove(c)

        if may_str is not None:
            may.clear()
            may.update(
                m.group(0).upper()
                for m in re.finditer(r'[A-Za-z]', may_str))

        ui.log(f'word: {word_i} {"".join(self.grid[k] or "_" for k in self.row_word_range(word_i))}')
        ui.log(f'may: {word_i} {" ".join(sorted(self.row_may[word_i]))}')

        return True

    def do_gen(self, ui: PromptUI):
        self.skip_show = True
        return self.do_choose(ui)

    def do_attempts(self, ui: PromptUI):
        avoid = True
        word_i: int|None = None

        while ui.tokens:
            n = ui.tokens.have(r'\d+$', lambda m: int(m.group(0)))
            if n is not None:
                word_i = n-1
                continue

            if ui.tokens.have(r'-sans'):
                avoid = False
                continue

            ui.print(f'! invalid * arg {next(ui.tokens)!r}')
            return

        if word_i is None:
            ui.print(f'! must have word <NUMBER>')
            return

        sel = self.select(row=word_i, avoid=avoid)
        ui.print(f'attempts for: {sel.word}')
        for n, at in enumerate(sel.attempts, 1):
            ui.print(f'{n}. {at}')

    def do_choose(self, ui: PromptUI) -> PromptUI.State|None:
        if self.choosing is None:
            avoid = True
            verbose = 0
            chooser = Chooser()
            word_i: int|None = None

            while ui.tokens:
                n = ui.tokens.have(r'\d+$', lambda m: int(m.group(0)))
                if n is not None:
                    word_i = n-1
                    continue

                match = ui.tokens.have(r'-(v+)')
                if match:
                    ui.print(f'parse choosing verbose: {verbose}')
                    verbose += len(match.group(1))
                    continue

                if ui.tokens.have(r'-sans'):
                    avoid = False
                    continue

                if chooser.collect(ui.tokens):
                    continue

                ui.print(f'! invalid * arg {next(ui.tokens)!r}')
                return

            # TODO expand scoring over all possible words when word_i not given

            sel: Search.Select|None = None

            if word_i is None:
                smallest = 0
                for word_j in range(self.size):
                    p = self.select(row=word_j, avoid=avoid)
                    if p.word.done: continue
                    have = sum(1 for _ in self.find(p.pattern, row=word_j))
                    if not have: continue
                    if not sel or have < smallest:
                        word_i, sel, smallest = word_j, p, have
                if word_i is None or sel is None:
                    ui.print('! unable to select')
                    for word_j in range(self.size):
                        p = self.select(row=word_j, avoid=avoid)
                        lines = self.explain_select(p.word)
                        for line in wrap_item(f'#{word_j+1}: {next(lines)}', lines, indent='   '):
                            ui.print(line)
                    return

            else:
                sel = self.select(row=word_i, avoid=avoid)

            words = tuple(self.find(sel.pattern, row=word_i))
            scores, explain_score = self.score_words(word_i, words)
            for i, word in enumerate(words):
                if word in self.recent_sug:
                    penalty = self.recent_sug[word]
                    if penalty > 1:
                        self.recent_sug[word] = penalty - 1
                    else:
                        del self.recent_sug[word]
                    scores[i] /= penalty

            self.choosing = word_i, sel.word, Possible(
                words,
                lambda _: (scores, explain_score),
                verbose=verbose,
                choices=chooser.choices)

        return self.present_choice

    def do_manual_gen(self, ui: PromptUI):
        verbose = 0
        chooser = Chooser()
        word_i: int|None = None
        word: Word|None = None

        while ui.tokens:
            n = ui.tokens.have(r'\d+$', lambda m: int(m.group(0)))
            if n is not None:
                word_i = n-1
                continue

            match = ui.tokens.have(r'-(v+)')
            if match:
                ui.print(f'parse choosing verbose: {verbose}')
                verbose += len(match.group(1))
                continue

            if chooser.collect(ui.tokens):
                continue

            try:
                word = Word.parse(ui.tokens.rest)
            except ValueError as err:
                ui.print(f'! must have word spec: {err}')
                return

            break

        if word_i is None:
            ui.print(f'! must have word <NUMBER>')
            return

        if word is None:
            ui.print(f'! must have word spec')
            return

        pat = word.pattern()
        if verbose:
            ui.print(f'manual gen {word} {pat}')

        words = tuple(self.find(pat, row=word_i))
        scores, explain_score = self.score_words(word_i, words)

        self.choosing = word_i, word, Possible(
            words,
            lambda _: (scores, explain_score),
            verbose=verbose,
            choices=chooser.choices)

        return self.present_choice

    def explain_select(self, word: Word) -> Generator[str]:
        if word.done:
            yield f'done {word}'
            return

        yield f'for {word}'

        pat = word.pattern()
        yield f'pattern: {pat}'

        # RIP prior over Select
        # extra: list[str] = []
        # have = sum(1 for _ in self.find(pat, row=sel.row, verbose=extra.append))
        # yield f'have: {have}'
        # yield from extra

    def present_choice(self, ui: PromptUI):
        if self.choosing is None:
            return self.display

        word_i, sel_word, pos = self.choosing

        if len(pos.data) == 0:
            lines = self.explain_select(sel_word)
            for line in wrap_item(f'!!! #{word_i+1} no choices', lines, indent='... '):
                ui.print(line)
            self.choosing = None
            return self.display

        if len(pos.data) == 1:
            ui.print(f'=== #{word_i+1} must be')
            i = next(pos.index())
            choice = pos.data[i]
            self.recent_sug[choice] = 10
            return self.ask_question(ui, choice, f'#{word_i+1}')

        ui.print(f'#{word_i+1} {pos} from {sel_word}')
        for line in pos.show_list():
            ui.print(line)

        with (
            ui.catch_state(EOFError, self.choice_abort),
            ui.input('try? ') as tokens):

            if tokens.have(r'\*'):
                self.skip_show = True
                self.choosing = None
                return self.do_choose(ui)

            n = tokens.have(r'\d+', lambda match: int(match[0]))
            i = None
            if n is not None:
                try:
                    i = pos.get(n)
                except IndexError:
                    pass
            if i is not None:
                choice = pos.data[i]
                self.recent_sug[choice] = 10
                return self.ask_question(ui, choice, f'#{word_i+1}')

    def choice_abort(self, _ui: PromptUI):
        self.choosing = None
        return self.display

    def ask_question(self, ui: PromptUI, word: str, desc: str):
        word = word.upper()
        ui.log(f'questioning: {json.dumps([word, desc])}')
        self.qmode = '>' if word in self.guesses else '?' # TODO auto N> wen
        self.questioning = word
        self.question_desc = desc
        self.choosing = None
        return self.question

    def question_abort(self, ui: PromptUI):
        self.question_done(ui)
        ui.print('')
        return self.display

    def question(self, ui: PromptUI):
        with ui.catch_state(EOFError, self.question_abort):
            q = self.qmode
            word = self.questioning.upper()
            desc = self.question_desc
            prompt = f'{word} ( {desc} )' if desc else f'{word}'
            prompt = f'{prompt} {q} '

            word_i = None
            qim = re.fullmatch(r'(?x) ( \d+ ) >', q)
            if qim:
                word_i = int(qim.group(1))-1
                q = '>'

            ui.copy(word)
            self.show(ui)

            with ui.input(prompt) as tokens:
                if q == '?':
                    if tokens.empty:
                        self.question_guess(ui, word)
                        self.qmode = '>' # TODO: auto N> wen
                        return

                    if tokens.rest.strip() == '!':
                        self.question_reject(ui, word)
                        return self.display
                    if tokens.rest.strip() == '.':
                        return self.question_guess(ui, word)

                    word_i = self.re_word_i(ui)
                    if word_i is not None:
                        match = self.re_word_match(ui)
                        if match:
                            self.question_guess(ui, word)
                            if self.proc_re_word_match(ui, word_i, match): word_i += 1

                elif q == '>':
                    if tokens.empty:
                        word_i = 0 if word_i is None else word_i+1
                    else:
                        re_word_i = self.re_word_i(ui)
                        if re_word_i is not None:
                            word_i = re_word_i
                        if word_i is None: return
                        if self.proc_re_word(ui, word_i): word_i += 1

                else:
                    raise RuntimeError(f'invalid qmode:{q!r}')

                if word_i is None: word_i = 0
                if word_i >= self.size:
                    self.question_done(ui)
                    return self.display
                self.qmode = f'{word_i+1}>'

    def re_word_i(self, ui: PromptUI):
        n = ui.tokens.have(r'(\d+):?', lambda m: int(m.group(1)))
        if n is not None:
            word_i = n - 1
            return word_i if 0 <= word_i < self.size else None

    def question_guess(self, ui: PromptUI, word: str):
        word = word.upper()
        ui.log(f'guess: {word}')
        self.qmode = '>'
        if word not in self.guesses:
            self.guesses[word] = len(self.guesses)

    def question_reject(self, ui: PromptUI, word: str):
        word = word.upper()
        ui.log(f'reject: {word}')
        self.rejects.add(word)
        self.questioning = ''
        self.question_desc = ''

    def question_done(self, ui: PromptUI):
        ui.log('question done')
        self.qmode = '?'
        self.questioning = ''
        self.question_desc = ''

@dataclass
class Result:
    size: int
    site: str
    puzzle_id: str
    guesses: int
    scores: list[int] # NOTE actually a size,size shaped matrix
    legend: dict[int, str]
    trailer: str

    score_marks: tuple[tuple[str, int], ...] = (
        ('🟥', 1),
        ('🟧', 2),
        ('🟨', 3),
        ('🟩', 4),
    )

    @property
    def legend_str(self):
        rev = {score: mark for mark, score in self.score_marks}
        return ' '.join(
            f'{rev[score]}:{desc}'
            for score, desc in sorted(self.legend.items(), reverse=True)
        )

    @property
    def score_rows(self):
        rev = {score: mark for mark, score in self.score_marks}
        for offset in range(0, len(self.scores), self.size):
            yield tuple(
                rev[self.scores[k]]
                for k in range(offset, offset+self.size))

    @classmethod
    def parse(cls, s: str, size: int):
        lines = PeekStr(spliterate(s, '\n', trim=True))

        match = lines.have(r'''(?x)
            (?P<site> [^\s]+ )
            \s+ (?P<id> [^\s]+ )
            :
            \s+ (?P<guesses> \d+ )
            \s+ guesses
            $
        ''')
        if not match:
            raise ValueError('first line should have site/puzzle id and guess count')
        site, puzzle_id, gs = match.groups()
        guesses = int(gs)


        scores: list[int] = [0 for _ in range(size*size)]

        fwd = {mark: score for mark, score in cls.score_marks}

        if lines.have(r'\s*$'):
            offset: int = 0
            for line in lines:
                if not line.strip(): break

                if len(line) != size:
                    raise ValueError(f'invalid grid line, expected {size} characters got {len(line)}')

                if any(x not in fwd for x in line):
                    bad = [f'{x!r}' for x in line if x not in fwd]
                    raise ValueError(f'invalid grid line marks: {bad!r}')

                assert offset < len(scores)
                for c in line:
                    scores[offset] = fwd[c]
                    offset += 1

            if offset < len(scores):
                raise ValueError('short grid score table')

        legend: dict[int, str] = dict()
        for match in re.finditer(
            r'(?x) \s* ( < \d+ | \d+ \+? ) : ( [🟥🟧🟨🟩] )',
            next(lines, '')):
            desc, mark = match.groups()
            score = fwd[mark]
            legend[score] = desc
        if not all(score in legend for score in fwd.values()):
            raise ValueError('incomplete legend')

        trailer = '\n'.join(lines)

        return cls(
            size,
            site, puzzle_id, guesses,
            scores, legend, trailer
        )

import pytest

@pytest.mark.parametrize('spec', [
    '''
    > squareword.org 1031: 17 guesses
    >
    > 🟧🟨🟨🟨🟨
    > 🟩🟨🟩🟨🟩
    > 🟨🟧🟧🟩🟨
    > 🟨🟨🟨🟨🟨
    > 🟥🟨🟥🟥🟩
    >
    > <6:🟩 <11:🟨 <16:🟧 16+:🟥
    > #squareword #squareword1031
    - size: 5
    - site: squareword.org
    - puzzle_id: 1031
    - guesses: 17
    - scores: [
        2, 3, 3, 3, 3,
        4, 3, 4, 3, 4,
        3, 2, 2, 4, 3,
        3, 3, 3, 3, 3,
        1, 3, 1, 1, 4
      ]
    - legend: [ [4, "<6"], [3, "<11"], [2, "<16"], [1, "16+"] ]
    - trailer: ```
      #squareword #squareword1031
      ```
    ''',
], ids=['first_solve'])
def test_parse_result(spec: str):
    ts = MarkedSpec(spec)

    size = 0
    expect_site: str|None = None
    expect_puzzle_id: str|None = None
    expect_guesses: int|None = None
    expect_scores: list[int]|None = None
    expect_legend: dict[int, str]|None = None
    expect_trailer: str|None = None

    for key, value in ts.props:
        if key == 'size': size = int(value)
        elif key == 'site': expect_site = value
        elif key == 'puzzle_id': expect_puzzle_id = value
        elif key == 'guesses': expect_guesses = int(value)
        elif key == 'scores':
            val = cast(object, json.loads(value))
            assert isinstance(val, list)
            assert all(isinstance(x, int) for x in cast(list[object], val))
            expect_scores = cast(list[int], val)
        elif key == 'legend':
            val = cast(object, json.loads(value))
            assert isinstance(val, list)
            assert all(isinstance(x, list) for x in cast(list[object], val))
            assert all(len(x) == 2 for x in cast(list[list[object]], val))
            assert all(isinstance(k, int) and isinstance(v, str) for k, v in cast(list[list[object]], val))
            expect_legend = dict(
                (cast(int, k), cast(str, v))
                for k, v in cast(list[list[object]], val))
        elif key == 'trailer':
            expect_trailer = value
        else: raise ValueError(r'unknown spec key {key!r}')

    ts.assert_no_trailer()

    res = Result.parse(ts.input, size)

    if expect_site is not None: assert res.site == expect_site
    if expect_puzzle_id is not None: assert res.puzzle_id == expect_puzzle_id
    if expect_guesses is not None: assert res.guesses == expect_guesses
    if expect_scores is not None: assert res.scores == expect_scores
    if expect_legend is not None: assert res.legend == expect_legend
    if expect_trailer is not None: assert res.trailer == expect_trailer

if __name__ == '__main__':
    Search.main()
