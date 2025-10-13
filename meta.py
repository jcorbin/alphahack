#!/usr/bin/env python

import argparse
import datetime
import os
import re
import shlex
import sys
import subprocess
from collections import Counter, defaultdict
from itertools import chain
from collections.abc import Generator, Iterable
from datetime import date
from dotenv import load_dotenv
from emoji import emoji_count, is_emoji
from functools import partial
from os.path import basename
from typing import Callable, Protocol, cast, final, override
from types import TracebackType

from store import StoredLog, atomic_rewrite, git_txn
from strkit import PeekIter, spliterate
from ui import PromptUI

def load_tmuxenv(override: bool = False):
    some = False
    with subprocess.Popen(('tmux', 'showenv'), stdout=subprocess.PIPE, text=True) as showenv:
        assert showenv.stdout is not None
        for line in showenv.stdout:
            m = re.match(r'''(?x)
                (?P<key> [A-Za-z][^=]* )
                =
                (?P<val> .* )
            ''', line)
            if m:
                key, val = m[1], m[2]
                if key not in os.environ or (
                    override and os.environ[key] != val
                ):
                    os.environ[key] = val
                    some = True
    return some

def load_env(override: bool = False):
    prior = dict(os.environ)
    _ = load_tmuxenv(override=override)
    _ = load_dotenv(override=override)
    for name in set(chain(prior, os.environ)):
        old = prior.get(name, '')
        now = os.environ.get(name, '')
        if old != now:
            yield name, now, old

for name, now, _old in load_env(override=True):
    print(f'set ${name} = {now!r}')

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

def screen_width(s: str):
    return len(s) + emoji_count(s)

def screen_truncate(s: str, width: int):
    if screen_width(s) <= width:
        return s
    # TODO this is oblivious to zero-width/combining characters
    s = s[:width]
    # TODO this would probably be better as a binary search
    while screen_width(s) > width:
        s = s[:-1]
    return s

@final
class LineWriter:
    # TODO wants to accept just the output protocol (plus screen
    #      size attrs?)... and implement the same

    def __init__(self, ui: PromptUI, at: int = 0, limit: int = 0):
        self.ui = ui
        self.at = at
        self.limit = limit

    @property
    def remain(self):
        return self.limit - self.at

    def fin(self):
        self.ui.fin()
        self.at = 0

    def write(self, s: str):
        self.ui.write(s)
        _, _, last = s.rpartition('\n')
        # TODO parse ansi positioning sequences
        self.at = screen_width(last)

    def truncate(self, s: str, cont: str = '...'):
        n = self.remain
        if screen_width(s) > n:
            pre = screen_truncate(s, n-screen_width(cont))
            return f'{pre}{cont}'
        return s

    def __enter__(self):
        if not self.limit:
            self.limit = self.ui.screen_cols
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        self.fin()

def write_tokens(ui: PromptUI,
                 tokens: PeekIter[str],
                 pre: str = '',
                 sep: str = ' ',
                 sub_pre: str = '  ',
                 limit: int = -1,
                 ):
    if not tokens: return
    with LineWriter(ui) as lw:
        first = True
        while tokens and limit != 0:
            lw.write(f'{pre}{next(tokens, '')}')
            while tokens:
                if lw.remain < 0: break
                lw.write(f'{sep}{next(tokens)}')
            if first:
                first = False
                pre = sub_pre
            if limit > 0:
                limit -= 1

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
        try:
            return open(self.filename)
        except FileNotFoundError:
            return open('/dev/null')

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
            'day': self.do_day,
            'env': self.do_env,
            'log': self.do_log,
            'review': self.do_review,
            'run': self.do_run,
            'share': self.do_share,
            'solvers': self.do_solvers,
            'status': self.do_status,
            'sys': self.do_system,
            'tracing': self.do_tracing,
            # TODO share: header, detail, summary
            # TODO clear day
            # TODO flip day
        })

    @override
    def __call__(self, ui: PromptUI):
        ui.run(super().__call__)
        return self.may_reexec

    def may_reexec(self, ui: PromptUI):
        with ui.input('meta done, reexec [ Y / n ] ? ') as tokens:
            if not tokens or tokens.have(r'(?xi) ^ y'):
                argv = (sys.executable, *sys.argv)
                ui.print('')
                ui.print('# Meta script re-executing itself')
                ui.print(f'+ {shlex.join(argv)}')
                os.execv(argv[0], argv)

            if tokens.have(r'(?xi) ^ n'):
                raise StopIteration

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
            with LineWriter(ui) as lw:
                for name, value in os.environ.items():
                    rval = repr(value) # TODO this only needs to quote control chars for ansi sequences
                    lw.write(f'${name} = ')
                    lw.write(lw.truncate(rval))
                    lw.fin()
            return

        if ui.tokens.have('load'):
            some = False
            for name, now, _old in load_env(override=True):
                some = True
                ui.print(f'set ${name} = {now!r}')
            if not some:
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

    def do_system(self, ui: PromptUI):
        '''
        Run arbitrary system command (execv not shell)
        '''
        try:
            cmd = shlex.split(ui.tokens.rest)
            with ui.check_proc(subprocess.Popen(cmd)):
                pass
        except subprocess.CalledProcessError as err:
            ui.print(f'! {err}')

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
            with ui.check_proc(subprocess.Popen((editor, log_file))):
                pass
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
            with ui.check_proc(subprocess.Popen(('tail', f'-n{tail_n}', log_file))):
                pass
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

    def do_review(self, ui: PromptUI):
        try:
            editor = os.environ.get('EDITOR', 'vi')
            git_editor = os.environ.get('GIT_EDITOR', editor)
            seq_editor = os.environ.get('GIT_SEQUENCE_EDITOR', git_editor)

            env = os.environ.copy()
            env['GIT_SEQUENCE_EDITOR'] = EditBack.command('git_seq')

            # TODO we only need to intercept this because of using git-rebase's
            #      stdin/out as out control channel; is it better to connect
            #      edit-back via side channel instead?
            env['GIT_EDITOR'] = EditBack.command('git')
            env['EDITOR'] = EditBack.command()

            with (
                ui.check_proc(subprocess.Popen(
                    ('git', 'rebase', '--rebase-merges', '-i', 'main'),
                    env=env,
                    text=True,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                )) as proc,
                EditBack(proc) as ed,
            ):
                for f in ed:
                    if f.mode == 'git_seq' and basename(f.name) == 'git-rebase-todo':
                        with f as (r, w):
                            rev = Review(r)
                            for line in rev():
                                print(line, file=w)
                    edit = (seq_editor if f.mode == 'git_seq' else
                            git_editor if f.mode == 'git' else
                            editor)
                    cmd = shlex.join((edit, f.name))
                    ui.check_call(subprocess.Popen(cmd, shell=True))
                    ed.done(f.name)

        except subprocess.CalledProcessError as err:
            ui.print(f'! {err}')

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
        for i, day, note, head, _body in self.read_status(ui):
            mark = '❔'
            if day is not None: mark = '✅'
            if head: mark += '📜'
            write_tokens(ui, PeekIter((
                f'{mark} {solver_harness[i]}',
                f'{day}',
                *marked_tokenize(note)
            )))
        self.prompt.re = max(1, self.prompt.re)

@final
class Review:
    def __init__(self, lines: Iterable[str]):
        def starts(lines: Iterable[str]):
            st = 0
            for i, line in enumerate(lines):
                if line:
                    if not st:
                        yield i
                    st = 1
                else:
                    st = 0

        self.in_lines = tuple(line.rstrip('\n') for line in lines)
        self.starts = tuple(starts(self.in_lines))

        self.section_by: defaultdict[str, dict[str, int]] = defaultdict(lambda: dict())
        for i, section in enumerate(self.starts):
            kind, name = self.section_kind(section)
            self.section_by[kind][name] = i

        self.out: list[list[int|str]] = [
            [i for i, _ in self.section(section)]
            for section in self.starts
        ]
        self.start_out = [
            i
            for i, _ in enumerate(self.starts)
        ]

    def out_lines(self):
        first = True
        for out in self.out:
            if not first:
                yield ''
            first = False
            for part in out:
                if isinstance(part, str):
                    yield part
                else:
                    yield self.in_lines[part]

    def section(self, section: int):
        it = enumerate(self.in_lines)
        for i, line in it:
            if i < section: continue
            yield i, line
            break
        for i, line in it:
            if not line: break
            yield i, line

    def section_kind(self, section: int):
        ac = True
        l = ''
        for _, line in self.section(section):
            ac = ac and line.startswith('#')
            l = line

        if ac and re.match(r'(?x) # \s+ Rebase', self.in_lines[section]):                              
            return 'errata', self.in_lines[section]

        m = re.match(r'(?x) label [ ]+ ( .+ )', l)
        if m:
            return 'label', m[1]

        m = re.match(r'(?x) update-ref [ ]+ ( .+ )', l)
        if m:
            return 'ref', m[1]

        m = re.match(r'(?x) pick [ ]+ ( .+ )', l)
        if m:
            return 'tail', m[1]

        return 'unknown', self.in_lines[section]

    def find_branch(self, name: str):
        wanted = name if '/' in name else f'refs/heads/{name}'
        for nom, i in self.section_by['ref'].items():
            if nom == wanted:
                return i
        if '/' not in name:
            lbl = self.section_by['label']
            if name in lbl:
                return lbl[name]
            may = tuple(nom for nom in lbl if nom.startswith(name))
            if len(may) == 1:
                return lbl[may[0]]
            wip = f'WIP-merge-{name}'
            if wip in lbl:
                return lbl[wip]

    def find_out(self, name: str):
        i = self.find_branch(name)
        if i is not None:
            j = self.start_out[i]
            if 0 <= j < len(self.out):
                return j
        wanted = f'# NOTE {name}'
        for i, out in enumerate(self.out):
            if out[0] == wanted:
                return i
        return self.make_out(name)

    def make_out(self, name: str = '', prepend: bool=False):
        new: list[int|str] = []
        if name:
            new.append(f'# NOTE {name}')

        if prepend:
            self.out.insert(0, new)
            for i, _ in enumerate(self.start_out):
                self.start_out[i] += 1
            return 0

        elif self.section_by['errata']:
            i = max(self.section_by['errata'].values())
            o = self.start_out[i]
            self.out.insert(o, new)
            for j, o2 in enumerate(self.start_out):
                if o2 >= o:
                    self.start_out[j] += 1
            return o

        else:
            o = len(self.out)
            self.out.append(new)
            return o

    def drop_out(self, i: int):
        for j, k in enumerate(self.start_out):
            if k == i:
                self.start_out[j] = -1
        out = self.out.pop(i)
        return out

    def append_pick(self, o: int, line_i: int):
        out = self.out[o]
        j = len(out) - 1
        while j > 0:
            part = out[j]
            if not isinstance(part, str):
                part = self.in_lines[part]
            if part.startswith('pick '):
                break
            j -= 1
        j += 1
        out.insert(j, line_i)

    def collect_tail(self):
        _ = self.find_out('DAILY')
        _ = self.find_out('rc')
        dev_o = self.make_out('dev')
        daily_o = self.find_out('DAILY')
        rc_o = self.find_out('rc')

        def changed_paths(commit: str):
            with subprocess.Popen(
                ('git', 'show', '--oneline', '--name-only', commit),
                stdout=subprocess.PIPE, text=True) as proc:
                assert proc.stdout is not None
                for line in proc.stdout:
                    break
                for line in proc.stdout:
                    yield line.rstrip('\n')

        def categorize(commit: str, oneline: str, default: int|None):
            m = re.match(r'''(?x)
                  ( DAILY \s+ .+ )
                | ( .+ \s+ day \s+ .+ )
                | ( .+ \s+ bad \s+ .+ )
            ''', oneline)
            if not m: return default

            if m[1]:
                return daily_o

            elif m[2] and all(
                path.startswith(StoredLog.store_dir)
                for path in changed_paths(commit)):
                return rc_o

            elif m[3] and all(
                path.endswith('_exclude.txt')
                for path in changed_paths(commit)):
                return rc_o

            return default

        had_daily = len(self.out[daily_o])
        had_rc = len(self.out[rc_o])
        had_dev = len(self.out[dev_o])

        first = True
        for tail_i in self.section_by['tail'].values():
            tail_o = self.start_out[tail_i]
            tail_out = self.out[tail_o]
            section = self.starts[tail_i]
            for line_i, line in self.section(section):
                cat = None if first else dev_o
                m = re.match(r'''(?x)
                    pick
                    \s+ (?P<commit> [^ ]+ )
                    \s+ [#]
                    \s+ (?P<oneline> .+ )
                ''', line)
                if m:
                    commit = m[1]
                    oneline = m[2]
                    cat = categorize(commit, oneline, cat)
                if cat is None:
                    continue
                first = False
                self.append_pick(cat, line_i)
                while line_i in tail_out:
                    tail_out.remove(line_i)

        got_daily = len(self.out[daily_o]) - had_daily
        if got_daily:
            yield f'# NOTE collected {got_daily} DAILY commits'

        got_rc = len(self.out[rc_o]) - had_rc
        if got_rc:
            yield f'# NOTE collected {got_rc} RC commits'

        got_dev = len(self.out[dev_o]) - had_dev
        if got_dev:
            yield f'# NOTE demarcated {got_dev} DEV commits'

    def compact_daily(self):
        daily_o = self.find_out('DAILY')
        daily_out = self.out[daily_o]

        keep_last = 30
        today = datetime.datetime.today().date()

        cur_d: datetime.date|None = None
        days: list[tuple[int, datetime.date, str, str]] = []
        fxd: Counter[datetime.date] = Counter()
        for i, part in enumerate(daily_out):
            if not isinstance(part, str):
                part = self.in_lines[part]

            m = re.match(r'''(?x)
                # pick <commit> # <oneline>
                p(?: ick )?
                \s+ (?P<commit> [^\s]+ )
                \s+ [#] \s+
                (?P<oneline> .+ )
            ''', part)
            if m:
                commit = m[1]
                oneline = m[2]
                m = re.match(r'''(?x)
                    # DAILY YYYY-MM-DD
                    DAILY \s+ (?P<date> (?P<yyyy> \d{4}) - (?P<mm> \d{2}) - (?P<dd> \d{2}) )
                ''', oneline)
                if m:
                    cur_d = datetime.date(int(m[2]), int(m[3]), int(m[4]))
                    days.append((i, cur_d, commit, oneline))

                elif cur_d is not None and cur_d != today:
                    daily_out[i] = f'fixup {commit} # {oneline}'
                    fxd[cur_d] += 1
                continue

        pr = 0
        if len(days) > keep_last:
            prior_old_i = days[0][0]
            for i, date, commit, oneline in days[:-keep_last]:
                if fxd[date]: break
                d = i - prior_old_i
                if d > 1: break
                if d == 1:
                    daily_out[i] = f'fixup -C {commit} # {oneline}'
                    pr += 1
                prior_old_i = i

        fx = sum(fxd.values())
        yield f'# NOTE found {len(days)} DAILY reports pruned:{pr} squashed:{fx}'

    def __call__(self) -> Generator[str]:
        head_i = self.make_out(prepend=True)
        head_out = self.out[head_i]
        head_out.extend(self.collect_tail())
        head_out.extend(self.compact_daily())
        if not head_out:
            head_out.append('# NOTE review noop')
        yield from self.out_lines()

    @staticmethod
    def main(*args: str):
        import fileinput
        rev = Review(fileinput.input(args))
        for line in rev():
            print(line)

@final
class EditFile:
    def __init__(self, mode: str, name: str):
        self.mode = mode
        self.name = name
        self.r = None
        self.w = None

    def __enter__(self):
        try:
            self.r = open(self.name, 'r')
        except FileNotFoundError:
            self.r = open('/dev/null', 'r')
        self.w = open(f'{self.name}.new', 'x') # TODO random temp suffix
        return self.r, self.w

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        try:
            if exc is None:
                self.save()
        finally:
            self.close()

    def save(self):
        w = self.w
        if w is not None:
            try:
                os.rename(w.name, self.name)
            except: pass

    def close(self):
        r = self.r
        if r is not None:
            r.close()
            self.r = None
        w = self.w
        if w is not None:
            try:
                os.unlink(w.name)
            except: pass
            w.close()
            self.w = None

@final
class EditBack:
    def __init__(self, proc: subprocess.Popen[str]):
        assert proc.stdin is not None
        assert proc.stdout is not None
        self.proc = proc
        self.stdin = proc.stdin
        self.stdout = proc.stdout
        self.files: list[EditFile] = []

    def send(self, mess: str):
        print(f'{mess.rstrip("\n")}\n', file=self.stdin, flush=True)

    def done(self, name: str):
        self.send(f'done edit file: {name}')

    def abort(self, code: int|None=None):
        self.send('abort' if code is None else f'abort {code}')

    def __iter__(self):
        return self

    def __next__(self):
        for line in self.stdout:
            line = line.rstrip('\n')

            m = re.match(r'''(?x)
                edit
                (?:
                    - (?P<mode> [^\s]+ )
                )?
                \s+
                file
                : \s+
                (?P<filename> .+ )
            ''', line)
            if m:
                mode = m[1] or ''
                name = m[2]
                f = EditFile(mode, name)
                self.files.append(f)
                return f

        raise StopIteration()

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        ok = exc is None
        try:
            for f in self.files:
                f.close()
        except:
            ok = False
        finally:
            if ok:
                self.stdin.close()
            else:
                self.proc.terminate()

    @staticmethod
    def command(mode: str=''):
        ed = f'edit-back-{mode}' if mode else 'edit-back'
        return shlex.join((sys.executable, sys.argv[0], ed))

    @staticmethod
    def main(mode: str, *args: str):
        ed = f'edit-{mode}' if mode else 'edit'
        pending: set[str] = set()
        for arg in args:
            print(f'{ed} file: {arg}', flush=True)
            pending.add(arg)

        for line in sys.stdin:
            line = line.rstrip('\n')

            m = re.match(r'''(?x)
                done \s+ edit \s+ file
                : \s+
                (?P<filename> .+ )
            ''', line)
            if m:
                pending.remove(m[1])
                if not pending:
                    break
                continue

            m = re.match(r'''(?x)
                abort (?: \s+ ( \d+ ) )?
            ''', line)
            if m:
                code = int(m[1] or '1')
                sys.exit(code)

            if line:
                print(f'edit-back got unknown response {line!r}', file=sys.stderr, flush=True)

if __name__ == '__main__':
    args = sys.argv[1:]
    first = args[0] if args else ''
    edit_m = re.match(r'(?x) edit-back (?: - (?P<mode> [^\s]+ ) )?', first)
    if edit_m:
        EditBack.main(edit_m[1] or '', *args[1:])
    elif first == 'review':
        Review.main(*args[1:])
    else:
        Meta.main()
