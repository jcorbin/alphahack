#!/usr/bin/env python

import argparse
import json
import re
from collections import OrderedDict
from collections.abc import Generator, Iterable, Sequence
from dataclasses import dataclass
from typing import Callable, cast, final, overload, override

from sortem import Chooser, DiagScores, Possible, RandScores, wrap_item
from store import StoredLog, git_txn
from strkit import MarkedSpec, PeekStr, spliterate
from ui import PromptUI
from wordlist import WordList

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
    if a and b:
        yield a, b

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

        self.choosing: tuple[int, 'Search.Select', Possible[str]]|None = None

        self.qmode: str = '?'
        self.questioning: str = ''
        self.question_desc: str = ''

        self.guesses: dict[str, int] = dict()
        self.rejects: set[str] = set()

        self.nope: set[str] = set()
        self.row_may: list[set[str]] = [set() for _ in range(self.size)]

        self.result_text: str = ''
        self._result: Result|None = None

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
                    self.row_may[word_i] = set(let.strip().lower() for let in may.split())
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
                    word = cast(str, word).lower()
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
                sel = self.select(col=col)
                col_may[col].update(word[row] for word in self._find(sel.pattern))
            if verbose:
                verbose(f'col_may: {''.join(
                    f'[{''.join(sorted(may)).upper()}]'
                    for may in col_may
                )}')

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
            if pattern.fullmatch(word): yield word

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
        alphabet = 'abcdefghijklmnopqrstuvwxyz'

        def __init__(self,
                     word: Iterable[str],
                     may: Iterable[str] = (),
                     nope: Iterable[str] = (),
                     row: int|None = None,
                     col: int|None = None,
                     ):
            self.word = tuple(word)
            self.may = tuple(sorted(may))
            self.nope = tuple(sorted(nope))
            self.row = row
            self.col = col

            self.alpha = set(self.alphabet)
            self.uni = '.'
            if self.nope:
                self.alpha.difference_update(self.nope)
                self.uni = f'[{"".join(char_ranges(self.alpha))}]'

            self.free = sum((1 for let in self.word if not let), 0)
            if self.may:
                self.free -= len(self.may)

            self.space: int = len(self.alpha)**self.free
            if self.may:
                for n in range(len(self.may), 1, -1): self.space *= n

        @override
        def __str__(self):
            def parts():
                if self.row is not None:
                    yield f'row:{self.row}'
                elif self.col is not None:
                    yield f'col:{self.col}'

                word = ''.join(l if l else '_' for l in self.word).upper()
                yield f'word:{word}'
                if self.may:
                    may = ''.join(self.may).upper()
                    yield f'may:{may}'
                if self.nope:
                    nope = ''.join(self.nope).upper()
                    yield f'nope:{nope}'
                yield f'hypo:{self.space}'
            return ' '.join(parts())

        @property
        def size(self):
            return len(self.word)

        @property
        def pattern_str(self):
            if self.free == self.size:
                return self.uni * self.size

            if not self.may:
                return ''.join(
                    self.uni if not let else let
                    for let in self.word)

            def alts():
                from itertools import combinations, permutations
                ix = [i for i in range(len(self.word)) if not self.word[i]]
                for mix in combinations(ix, len(self.may)):
                    parts = [self.uni if not let else let for let in self.word]
                    for pmay in permutations(self.may):
                        for j, i in enumerate(mix):
                            parts[i] = pmay[j]
                        yield ''.join(parts)

            return '|'.join(alts())

        @property
        def pattern(self):
            return re.compile(self.pattern_str)

    @overload
    def select(self, *, row: int) -> Select: pass

    @overload
    def select(self, *, col: int) -> Select: pass

    def select(self, *, row: int|None = None, col: int|None = None) -> Select:
        if row is not None:
            # TODO reduce possible based on intersecting cols
            return self.Select(
                (self.grid[k] for k in self.row_word_range(row)),
                may = self.row_may[row],
                nope = self.nope,
                row = row)

        elif col is not None:
            # TODO reduce possible based on intersecting rows
            return self.Select(
                (self.grid[k] for k in self.col_word_range(col)),
                nope = self.nope,
                col = col)

        else:
            raise RuntimeError('must provide either row or col')

    skip_show: bool = False

    def show(self, ui: PromptUI):
        if self.skip_show:
            self.skip_show = False
            return
        self.show_grid(ui)
        if self.nope:
            ui.print(f'no: {" ".join(sorted(let.upper() for let in self.nope))}')

    def show_grid(self, ui: PromptUI):
        for word_i in range(self.size):
            ui.write(f'#{word_i+1}  | ')
            for k in self.row_word_range(word_i):
                ui.write(f' {self.grid[k].upper() or "_"}')
            ui.write(f'  |  {" ".join(sorted(let.upper() for let in self.row_may[word_i]))}')
            ui.fin()

    def display(self, ui: PromptUI):
        if self.run_done:
            return self.finish

        self.show(ui)
        with ui.input(f'> ') as tokens:

            if tokens.have(r'\*'):
                self.skip_show = True
                return self.do_choose(ui)

            if tokens.have(r'(?x) ( ! | /n(o(pe?)?)? ) $'):
                for m in re.finditer(r'[.A-Za-z]', tokens.rest):
                    c = m.group(0).lower()
                    if c == '.':
                        self.nope.clear()
                    else:
                        self.nope.add(c)
                ui.log(f'nope: {" ".join(sorted(self.nope))}')
                return

            if tokens.have(r'/g(u(e(s(s(es?)?)?)?)?)?'):
                for word in self.guesses:
                    ui.print(f'Guesses ({len(self.guesses)})')
                    ui.print(f'- {word}')
                return

            word_i = self.re_word_i(ui)
            if word_i is not None:
                if tokens.rest.strip() == '!':
                    self.forget(ui, word_i)
                    return

            word = next(tokens, None)
            if word:
                if len(word) == self.size:
                    return self.ask_question(ui, word, 'entered')
                ui.print(f'! wrong size {word!r}')
                return

    def row_word_range(self, row: int):
        return range(row * self.size, (row+1) * self.size)

    def col_word_range(self, col: int):
        return range(col, len(self.grid), self.size)

    def forget(self, ui: PromptUI, word_i: int):
        ui.log(f'forget: {word_i}')
        for j in self.row_word_range(word_i):
            self.grid[j] = ''
        self.row_may[word_i] = set()

    def finish(self, ui: PromptUI):
        res = self.result
        if res:
            raise StopIteration

        ui.print('Provide share result:')
        self.result_text = ui.may_paste()
        ui.log(f'result: {json.dumps(self.result_text)}')

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

        return super().review(ui)

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
                c = let.lower()
                if let == '_':
                    self.grid[offset + i] = ''
                elif self.grid[offset + i] != c:
                    self.grid[offset + i] = c
                    if c in may: may.remove(c)

        if may_str is not None:
            may.clear()
            may.update(
                m.group(0).lower()
                for m in re.finditer(r'[A-Za-z]', may_str))

        ui.log(f'word: {word_i} {"".join(self.grid[k] or "_" for k in self.row_word_range(word_i))}')
        ui.log(f'may: {word_i} {" ".join(sorted(self.row_may[word_i]))}')

        return True

    def do_choose(self, ui: PromptUI) -> PromptUI.State|None:
        if self.choosing is None:
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

                if chooser.collect(ui.tokens):
                    continue

                ui.print(f'! invalid * arg {next(ui.tokens)!r}')
                return

            # TODO expand scoring over all possible words when word_i not given

            sel: Search.Select|None = None

            if word_i is None:
                smallest = 0
                for word_j in range(self.size):
                    p = self.select(row=word_j)
                    if all(p.word): continue
                    have = sum(1 for _ in self.find(p.pattern, row=word_j))
                    if not have: continue
                    if not sel or have < smallest:
                        word_i, sel, smallest = word_j, p, have
                if word_i is None or sel is None:
                    ui.print('! unable to select')
                    for word_j in range(self.size):
                        p = self.select(row=word_j)
                        lines = self.explain_select(p)
                        for line in wrap_item(f'#{word_j+1}: {next(lines)}', lines, indent='   '):
                            ui.print(line)
                    return

            else:
                sel = self.select(row=word_i)

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

            self.choosing = word_i, sel, Possible(
                words,
                lambda _: (scores, explain_score),
                verbose=verbose,
                choices=chooser.choices)

        return self.present_choice

    def explain_select(self, sel: Select) -> Generator[str]:
        if all(sel.word):
            yield f'done {sel}'
            return

        yield f'for {sel}'

        pat = sel.pattern
        yield f'pattern: {pat}'

        extra: list[str] = []
        have = sum(1 for _ in self.find(pat, row=sel.row, verbose=extra.append))
        yield f'have: {have}'
        yield from extra

    def present_choice(self, ui: PromptUI):
        if self.choosing is None:
            return self.display

        word_i, sel, pos = self.choosing

        if len(pos.data) == 0:
            lines = self.explain_select(sel)
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

        ui.print(f'#{word_i+1} {pos} from {sel}')
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
        word = word.lower()
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
            word = self.questioning.lower()
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
        ui.log(f'guess: {word}')
        self.qmode = '>'
        if word not in self.guesses:
            self.guesses[word] = len(self.guesses)

    def question_reject(self, ui: PromptUI, word: str):
        ui.log(f'reject: {word}')
        self.rejects.add(word.lower())
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
            expect_scores = val
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
