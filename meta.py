#!/usr/bin/env python

import argparse
import datetime
import os
import re
import subprocess
from itertools import chain
from collections.abc import Generator, Iterable
from datetime import date
from dotenv import load_dotenv
from emoji import emoji_count, is_emoji
from functools import partial
from typing import Callable, Protocol, cast, final, override

from store import StoredLog, atomic_rewrite, git_txn
from strkit import PeekIter, spliterate
from ui import PromptUI

_ = load_dotenv()

# TODO move into ui/mkit/strkit modules
def is_mark(s: str):
    if len(s) == 1:
        return True

    # TODO tighten this / make it more specific
    #      ... or disqualify over matches like "... but not if it contains whitespace"
    #      ; what we probably mean here is "an emoji with combining chars is still 'just an emoji'. is mark"
    #      ; also "a pair of emojis is mark"
    #      ; probably "a triple of emojis is mark"
    #      ; do we dgaf whitespace only between emojis in those cases tho?
    if is_emoji(s[0]) or is_emoji(s[-1]):
        return True

    return False

def marked_tokenize(s: str,
                    is_mark: Callable[[str], bool]=is_mark
                    ) -> Generator[str]:
    # NOTE this does a classic whitespace split, but then coalesces marks onto
    #      their subsequent token ; more accurately tho, perhaps we should just
    #      split only on mark tokens, so that we end up with essentially a
    #      variably-bulleted list ; in such case, we probably still break on
    #      newline characters tho, which semantically indicate "<end-of-list>"
    #      framing, unless told otherwise (i.e. unless the user says "no
    #      actually, this entire paragraph is basically one ran-together marked
    #      list)
    tokens = iter(s.split())

    for tok in tokens:
        if is_mark(tok):
            then = next(tokens, None)
            if then is not None:
                tok = f'{tok} {then}'

        # else:
        #     ui.print(f'wat {[c for c in n]!r}')

        yield tok

@final
class Wrapper:
    @staticmethod
    def screen_width(s: str):
        return len(s) + emoji_count(s)

    def __init__(self, width: int):
        self.width = width

    def consume_until(self,
                      tokens: PeekIter[str],
                      sep: str = ' ',
                      prior: str|int = 0):
        pw = self.screen_width(prior) if isinstance(prior, str) else prior
        rem = self.width - pw
        while tokens:
            tok = tokens.peek('')
            part = f'{sep}{tok}'
            pcw = self.screen_width(part)
            rem -= pcw
            if rem < 0: return
            tok = next(tokens)
            yield part

    def write_line(self,
                   ui: PromptUI,
                   tokens: PeekIter[str],
                   indent: str = ''):
        # TODO can be abstracted over the output surface of PromptUI
        if tokens:
            try:
                first = f'{indent}{next(tokens, '')}'
                ui.write(first)
                for part in self.consume_until(tokens, prior=first):
                    ui.write(f'{part}')
            finally:
                ui.fin()

def trim_lines(lines: Iterable[str]):
    st = 0
    for line in lines:
        if line:
            if st > 1:
                for _ in range(st):
                    yield ''
            yield line
            st = 1
        elif st:
            st += 1

class Solver(Protocol):
    log_file: str
    site: str

    # TODO store directory / prior log access

    @property
    def today(self) -> datetime.date|None:
        return None

    def find_prior_log(self, ui: PromptUI, puzzle_id: str|None=None) -> str|None:
        raise NotImplemented

    @property
    def note_slug(self) -> tuple[str, ...]:
        return ('<undefined>',)

    @property
    def header_slug(self) -> tuple[str, ...]:
        return ('<undefined>',)

    def load_log(self, ui: PromptUI, log_file: str|None = None):
        pass

    def __call__(self, ui: PromptUI) -> PromptUI.State|None:
        return None

SolverMaker = Callable[[PromptUI.Tokens], Solver]

@final
class SolverHarness:
    Inarguable = Callable[[], Solver]
    Arguable = Callable[[PromptUI.Tokens], Solver]

    @classmethod
    def inarguable(cls, name: str, site: str, log_file: str):
        def wrapper(mak: SolverHarness.Inarguable):
            return cls(name, site, log_file, no_args=mak)
        return wrapper

    @classmethod
    def arguable(cls, name: str, site: str, log_file: str):
        def wrapper(mak: SolverHarness.Arguable):
            return cls(name, site, log_file, with_args=mak)
        return wrapper

    @classmethod
    def stored(cls,
               name: str,
               impl: type[StoredLog],
               site: str|None = None,
               log_file: str|None = None,
               ):
        def wrapper(mak: SolverHarness.Arguable):
            return cls(name,
                       site or impl.default_site,
                       log_file or impl.log_file,
                       with_args=mak)
        return wrapper

    def __init__(self,
                 name: str,
                 site: str,
                 log_file: str,
                 no_args: 'SolverHarness.Inarguable|None' = None,
                 with_args: 'SolverHarness.Arguable|None' = None,
                 ):
        if no_args and with_args:
            raise TypeError('SolverHarness MUST may only have EITHER { no or with }_args')
        self.name = name
        self.site = site
        self.log_file = log_file
        self.no_args = no_args
        self.with_args = with_args

    @override
    def __str__(self):
        return self.name

    def _make(self, tokens: PromptUI.Tokens) -> Solver:
        if self.with_args:
            return self.with_args(tokens)
        if self.no_args:
            return self.no_args()
        raise NotImplementedError(f'no {self.name} solver constructor given')

    # TODO prior log file search/browse

    def make(self,
             tokens: PromptUI.Tokens,
             log_file: str|None = None,
             ) -> Solver:
        solver = self._make(tokens)
        solver.site = self.site
        solver.log_file = log_file or self.log_file
        return solver

    def run(self, ui: PromptUI, log_file: str|None=None):
        # TODO parse optional -log-file arg
        try:
            ui.write(f'*** Running solver {self}')
            solver = self.make(ui.tokens, log_file=log_file)
            if log_file:
                ui.write(f' log_file={log_file}')
        finally:
            ui.fin()
        ui.interact(solver)

def load_solvers() -> Generator[SolverHarness]:
    from binartic import Search as Binartic

    @SolverHarness.stored('alfa', Binartic, site='alfagok.diginaut.net')
    def make_alfa(_tokens: PromptUI.Tokens):
        alfa = Binartic()
        alfa.wordlist_file = 'opentaal-wordlist.txt'
        return alfa
    yield make_alfa

    @SolverHarness.stored('alpha', Binartic, site='alphaguess.com')
    def make_alpha(_tokens: PromptUI.Tokens):
        alpha = Binartic()
        alpha.wordlist_file = 'nwl2023.txt'
        return alpha
    yield make_alpha

    from square import Search as Square

    @SolverHarness.stored('square', Square)
    def make_square(_tokens: PromptUI.Tokens):
        square = Square()
        square.wordlist_file = 'nwl2023.txt'
        return square
    yield make_square

    from hurdle import Search as Hurdle

    @SolverHarness.stored('hurdle', Hurdle)
    def make_hurdle(_tokens: PromptUI.Tokens):
        hurdle = Hurdle()
        hurdle.wordlist_file = 'nwl2023.txt'
        return hurdle
    yield make_hurdle

    from dontword import DontWord

    @SolverHarness.stored('dontword', DontWord)
    def make_dontword(_tokens: PromptUI.Tokens):
        dontword = DontWord()
        dontword.wordlist_file = 'nwl2023.txt'
        return dontword
    yield make_dontword

    from semantic import Search as Semantic

    @SolverHarness.stored('cemantle', Semantic)
    def make_cemantle(tokens: PromptUI.Tokens):
        cem = Semantic()
        cem.full_auto = True
        cem.from_tokens(tokens)
        return cem
    yield make_cemantle

    @SolverHarness.stored('cemantix', Semantic,
                          site='cemantix.certitudes.org',
                          log_file='cemantix.log')
    def make_cemantix(tokens: PromptUI.Tokens):
        cex = Semantic()
        cex.lang = 'French'
        cex.pub_tzname = 'CET'
        cex.full_auto = True
        cex.from_tokens(tokens)
        return cex
    yield make_cemantix

    from spaceword import SpaceWord

    @SolverHarness.stored('space', SpaceWord)
    def make_space(_tokens: PromptUI.Tokens):
        space = SpaceWord()
        space.wordlist_file = 'nwl2023.txt'
        return space
    yield make_space

    # spaceweek = "./spaceword.py --wordlist nwl2023.txt spaceword_weekly.log"

# TODO share base class with StoredLog

class Arguable:
    @classmethod
    def main(cls):
        self, args = cls.parse_args()
        trace = cast(bool, args.trace)
        return PromptUI.main(self, trace=trace)

    @classmethod
    def parse_args(cls):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        cls.add_args(parser)
        args = parser.parse_args()
        self = cls()
        return self, args

    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser):
        _ = parser.add_argument('--trace', '-t', action='store_true',
                                help='Enable execution state tracing')

    def __init__(self):
        self.prompt: PromptUI.Prompt = PromptUI.Prompt('> ', {})

    def __call__(self, ui: PromptUI):
        return self.prompt(ui)

# TODO into mdkit

def sections(lines: Iterable[str]) -> Generator[tuple[int, str, Iterable[str]]]:
    r_sec = re.compile(r'(?x) ( [#]+ ) [ ]+ ( .+ )')

    cur = PeekIter(lines)

    def body():
        while cur:
            nxt = cur.peek('')
            if r_sec.match(nxt):
                return
            yield next(cur)

    for line in cur:
        m = r_sec.match(line)
        if m:
            yield len(m[1]), m[2], body()

def items(lines: Iterable[str]):
    within = False
    prior: str|None = None
    for line in lines:
        if not line.strip():
            if within:
                prior = line
            continue
        elif re.match(r'(?x) [ ]* [-*+]', line):
            within = True
            if prior is not None:
                yield prior
                prior = None
            yield line
        else:
            return

# TODO into store module

class Report:
    filename: str = 'report.md'

    def read(self):
        return open(self.filename)

    def rewrite(self):
        return atomic_rewrite(self.filename)

    def sections(self) -> Generator[tuple[int, str, Iterable[str]]]:
        with self.read() as f:
            yield from sections(f)

solver_harness = tuple(load_solvers())

# NOTE likely cannot be abstracted over instantiation, since slugs contain
#      state info from a loaded prior solver log
solver_prior = tuple(
    harness.make(PromptUI.Tokens())
    for harness in solver_harness)
solver_notes = tuple(
    solver.note_slug[0]
    for solver in solver_prior)
solver_heads = tuple(
    solver.header_slug
    for solver in solver_prior)

# TODO is there any utility to using StoredLog? having a proper reified
# "day log"? if sow, what state lives in report.md vs the log? how
# redundant is the report once we have a meta log, and report sections
# can be generated on demand?

@final
class Meta(Arguable):
    @override
    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser):
        super().add_args(parser)
        _ = parser.add_argument('--report',
                                default=Report.filename,
                                help='Report file name')

    @override
    @classmethod
    def parse_args(cls):
        self, args = super().parse_args()
        self.report.filename = cast(str, args.report)
        return self, args

    def __init__(self):
        super().__init__()
        self.report = Report()
        self.prompt.mess = self.prompt_mess
        self.prompt.update({
            'solvers': self.do_solvers,
            'status': self.do_status,
            'run': self.do_run,
            'log': self.do_log,
            'share': self.do_share,
            'day': self.do_day,
            'env': self.do_env,
            'tracing': self.do_tracing,
            # TODO share: header, detail, summary
            # TODO clear day
            # TODO flip day
        })

    def prompt_mess(self, ui: PromptUI):
        if self.prompt.re == 0:
            self.do_status(ui)
        return 'meta> '

    # TODO txn.will_add(self.report.filename)

    def choose_solver(self, ui: PromptUI):
        if not ui.tokens:
            return
        name = next(ui.tokens).lower()

        pat = re.compile('.*'.join(name))
        ix = tuple(
            i
            for i, harness in enumerate(solver_harness)
            if pat.match(harness.name))

        if len(ix) == 0:
            ui.print('! no such solver')
            return -1
        elif len(ix) > 1:
            may = tuple(solver_harness[i].name for i in ix)
            ui.print(f'! Ambiguous solver; may be: {" ".join(may)}')
            return -1
        return ix[0]

    def do_tracing(self, ui: PromptUI):
        '''
        show or set ui state tracing
        '''
        if not ui.tokens:
            ui.print(f'- tracing: {"on" if ui.traced else "off"}')
            return

        if ui.tokens.have(r'(?ix) on | yes? | t(r(ue?)?)?'):
            if ui.traced:
                ui.print('! tracing already on ; noop')
                return
            else:
                raise ui.Tron

        if ui.tokens.have(r'(?ix) off? | n[oaiue]? | f(a(l(se?)?)?)?'):
            if not ui.traced:
                ui.print('! tracing already off ; noop')
                return
            else:
                raise ui.Troff

    def do_env(self, ui: PromptUI):
        '''
        show / set / (re)load environment
        usage: env $NAME
               env $NAME = <VALUE>
               env load
        '''
        if not ui.tokens:
            for name, value in os.environ.items():
                ui.print(f'${name} = ${value!r}')
            return

        if ui.tokens.have('load'):
            prior = dict(os.environ)
            if load_dotenv(override=True):
                for name in set(chain(prior, os.environ)):
                    old = prior.get(name, '')
                    now = os.environ.get(name, '')
                    if old != now:
                        ui.print(f'set ${name} = {now!r}')
            else:
                ui.print(f'no env change')
            return

        name = ui.tokens.have(r'\$(.+)', then=lambda m: m[1])
        if name is not None:
            if ui.tokens.have(r'='):
                value = ui.tokens.rest
                if value:
                    os.environ[name] = value
                    ui.print(f'set ${name} = {value!r}')
                else:
                    del os.environ[name]
                    ui.print(f'unset ${name}')
                return
            value = os.environ.get(name, '')
            ui.print(f'${name} = {value!r}')
            return

    def do_day(self, ui: PromptUI):
        '''
        clear out today sections if done
        '''
        day_solves: dict[date|None, set[int]] = {}
        day_sections: dict[date|None, set[str]] = {}
        for solver_i, day, _note, head, _body in self.read_status(ui):
            day_solves.setdefault(day, set()).add(solver_i)
            if head:
                day_sections.setdefault(day, set()).add(head)

        today = datetime.datetime.today().date()
        today_solves = day_solves.get(today, ())
        today_solved = all(
            i in today_solves
            for i in range(len(solver_harness)))

        # TODO once share records state, determine today_shared

        ui.print(f'today: {today}')
        ui.print(f'today_solves: {today_solves}')
        ui.print(f'today_solved: {today_solved}')

        for day in day_solves:
            ui.write(f'- {day}')
            ui.write(f' solves: {day_solves[day]}')
            ui.fin()
            for section in day_sections.get(day, ()):
                ui.print(f'  * {section}')

        prune_sections: set[str] = set()
        if today_solved: # TODO and today_shared
            prune_sections.add(str(today))
            prune_sections.update(day_sections.get(today, ()))

        # TODO prune_sections.update(day_sections[None])
        # TODO prune_sections.update(day_sections[ older days ])

        # ui.print(f'prune_sections: {prune_sections}')

        with git_txn(f'DAILY {today} prune') as txn:
            with (txn.will_add(self.report.filename),
                  self.report.rewrite() as (r, w)):
                for level, text, body in sections(r):
                    # TODO ui.print( -+ )
                    if text in prune_sections:
                        continue
                    mark = '#'*level
                    print(f'{mark} {text}', file=w)
                    for line in body:
                        print(line.rstrip(), file=w)

    def do_share(self, ui: PromptUI):
        '''
        prepare and copy share content for chat
        '''
        today = ui.tokens.have(
            r'(?x) (\d{4}) [-_/.]? (\d{2}) [-_/.]? (\d{2})',
            then=lambda m: date(int(m[1]), int(m[2]), int(m[3])),
            default=datetime.datetime.today().date())

        def sum_notes(notes: Iterable[str],
                       flag: Callable[[str, str], None]|None = None):
            for note in notes:
                tokens = spliterate(note, ' ')

                tok = next(tokens)
                if tok != '🔗':
                    if flag:
                        flag('unrecognized', note)
                    yield f'- {note}'
                    continue

                parts: list[str] = []

                puzzle_id = ''
                site = ''
                for tok in tokens:
                    if tok == '🧩':
                        site = ' '.join(parts)
                        puzzle_id = next(tokens)
                    else:
                        parts.append(tok)

                if not puzzle_id and flag:
                    flag('missing puzzle_id', site)

                parts.extend(tokens)
                yield  ' '.join(parts)

        def collect_notes():
            for _solver_i, day, note, _head, _body in self.read_status(ui):
                if day != today:
                    yield f'! {day} {note}'
                else:
                    yield note

        def collect_deet_secs():
            for _solver_i, day, _note, head, body in self.read_status(ui):
                if day == today:
                    yield head, body

        def deet_sec(head: str, body: Iterable[str]):
            yield f'# {head}'
            yield ''
            for line in trim_lines(body):
                yield f'> {line}'

        def collect_deets() -> Generator[str]:
            first = True
            for head, body in collect_deet_secs():
                if not first: yield ''
                yield from deet_sec(head, body)
                first = False

        def head_note():
            yield f'# {today}'
            yield f''
            for note in collect_notes():
                yield f'- {note}'

        def summary(link: str=''):
            for note in sum_notes(collect_notes()):
                yield f'- {note}'
            if link:
                yield f''
                yield f'Details and spoilers: {link}'

        def share_header(ui: PromptUI):
            with ui.copy_writer() as cw:
                for line in head_note():
                    print(line, file=cw)
            ui.print(f'📋 Share Header')

        def share_details(ui: PromptUI):
            with ui.copy_writer() as cw:
                for line in collect_deets():
                    print(line, file=cw)
            ui.print(f'📋 Share Details')

        def share_each_detail(ui: PromptUI):
            for head, body in collect_deet_secs():
                with ui.copy_writer() as cw:
                    for line in deet_sec(head, body):
                        print(line, file=cw)
                _ = ui.input(f'📋 Share {head} ; <Enter> to continue')

        def share_summary(ui: PromptUI):
            link = ui.may_paste(subject='Share Details Link')
            # TODO { reuse link from / save summary to } report file
            with ui.copy_writer() as cw:
                for line in summary(link):
                    print(line, file=cw)
            ui.print(f'📋 Share Summary')

        def share_all(ui: PromptUI):
            share_header(ui)
            _ = ui.input('<Press Enter To Continue>')
            share_details(ui)
            _ = ui.input('<Press Enter To Continue>')
            share_summary(ui)
            _ = ui.input('<Press Enter To Continue>')

        def print_notes(ui: PromptUI):
            any_out = False
            for line in collect_notes():
                any_out = True
                ui.print(line)
            if any_out:
                ui.print(f'')

        pr = ui.Prompt('share> ', {
            'all': share_all,
            'head': share_header,
            'details': ui.Prompt('details> ', {
                'each': share_each_detail,
                'all': share_details,
            }),
            'summary': share_summary,
        })
        if ui.tokens:
            return pr.handle(ui)
        try:
            print_notes(ui)
            ui.call_state(pr)
        except (EOFError, StopIteration):
            pass

    def do_log(self, ui: PromptUI):
        '''
        manage solver log(s)
        '''
        solver_i = self.choose_solver(ui)
        if solver_i is None:
            ui.print('! must name a solver')
            return
        elif solver_i < 0:
            return

        harness = solver_harness[solver_i]
        log_file = harness.log_file

        def use_last(ui: PromptUI, puzzle_id: str = ''):
            nonlocal log_file
            found = harness.make(ui.tokens).find_prior_log(ui, puzzle_id)
            if found is None:
                ui.print(f'! could not find last log file')
                return
            ui.print(f'Found last log_file: {log_file}')
            log_file = found
            if ui.tokens:
                return pr.handle(ui)
            else:
                return pr

        def do_edit(ui: PromptUI):
            editor = os.environ.get('EDITOR', 'vi')
            _ = ui.check_call(subprocess.Popen((editor, log_file)))
            raise StopIteration

        def do_rm(ui: PromptUI):
            ui.print(f'+ rm {log_file}')
            os.unlink(log_file)
            raise StopIteration

        def do_cont(ui: PromptUI):
            return solver_harness[solver_i].run(ui, log_file)

        def do_tail(ui: PromptUI):
            tail_n = (
                3 if ui.screen_lines < 10 else
                10 if ui.screen_lines < 20 else
                ui.screen_lines//2)
            _ = ui.check_call(subprocess.Popen(('tail', f'-n{tail_n}', log_file)))
            raise StopIteration

        pr = ui.Prompt(lambda _: f'{log_file}> ', {
            'last': use_last,
            'ls': partial(use_last, puzzle_id='*'),

            'cont': do_cont,
            'edit': do_edit,
            'tail': do_tail,
            'rm': do_rm,

            # TODO fin / result
            # TODO share / report
        })

        try:
            ui.call_state(lambda ui: pr.handle(ui) or pr if ui.tokens else pr)
        except (StopIteration, EOFError):
            return self.prompt

    def do_run(self, ui: PromptUI):
        '''
        run a solver, by name or inferred "next"
        '''
        solver_i = self.choose_solver(ui)
        if solver_i is None:
            for solver_i, day, _note, head, _body in self.read_status(ui, verbose=False):
                if day is None or not head:
                    break
            else:
                ui.print('! all solvers reported, specify particular?')
                return
        if solver_i >= 0:
            return solver_harness[solver_i].run(ui)

    def do_solvers(self, ui: PromptUI):
        '''
        show known solvers
        '''
        for n, (harness, note) in enumerate(zip(solver_harness, solver_notes), 1):
            ui.print(f'{n}. {harness} site:{harness.site!r} slug:{note!r}')

    def read_status(self, ui: PromptUI, verbose: bool=True):

        days: list[datetime.date] = []
        notes: list[str] = ['' for _ in solver_notes]
        note_days: list[int] = [0 for _ in solver_notes]
        heads: list[str] = ['' for _ in solver_heads]
        bodys: list[tuple[str, ...]] = [() for _ in solver_heads]

        for _level, text, body in self.report.sections():
            m = re.match(r'(?x) (\d{4}) [-_/.]? (\d{2}) [-_/.]? (\d{2})', text.strip())
            if m:
                dd = date(int(m[1]), int(m[2]), int(m[3]))
                days.append(dd)
                dd_n = len(days)
                for line in items(body):
                    line = line.rstrip()
                    m = re.match(r'(?x) [ ]* [-+*] [ ]* ( .+ )', line.rstrip())
                    if not m: continue
                    line = m[1]

                    for i, slug in enumerate(solver_notes):
                        if line.startswith(slug):
                            notes[i] = line
                            note_days[i] = dd_n
                            # TODO support multi
                            break

                    else:
                        if verbose:
                            ui.print('Unknown note:')
                            ui.print(f'> {line}')
                            ui.print('')

            else:
                for i, slug in enumerate(solver_heads):
                    if text.startswith(slug):
                        heads[i] = text
                        bodys[i] = tuple(line.rstrip() for line in body)
                        break

                # TODO else: report unknown sections?

        for solver_i, (dd_n, note, head, body) in enumerate(zip(note_days, notes, heads, bodys)):
            day = days[dd_n-1] if dd_n else None
            yield solver_i, day, note, head, body

    def do_status(self, ui: PromptUI):
        '''
        show solver status
        '''

        scw = Wrapper(ui.screen_cols)

        for i, day, note, head, _body in self.read_status(ui):
            mark = '❔'
            if day is not None: mark = '✅'
            if head: mark += '📜'

            tokens = PeekIter((
                f'{mark} {solver_harness[i]}',
                f'{day}',
                *marked_tokenize(note)
            ))
            scw.write_line(ui, tokens)
            # TODO wrap subsequent lines like:
            # ```python
            # while tokens:
            #     scw.write_line(ui, tokens, indent='... ')
            # ```

if __name__ == '__main__':
    Meta.main()
