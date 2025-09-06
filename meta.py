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
from typing import Callable, Protocol, cast, final, override

from store import atomic_rewrite, git_txn
from strkit import PeekIter, PeekStr, spliterate
from ui import PromptUI

_ = load_dotenv()

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

def load_solvers() -> Generator[tuple[str, Callable[[], Solver]]]:
   
    from binartic import Search as Binartic

    def make_alfa():
        alfa = Binartic()
        alfa.site = 'alfagok.diginaut.net'
        alfa.wordlist_file = 'opentaal-wordlist.txt'
        return alfa
    yield 'alfa', make_alfa

    def make_alpha():
        alpha = Binartic()
        alpha.site = 'alphaguess.com'
        alpha.wordlist_file = 'nwl2023.txt'
        return alpha
    yield 'alpha', make_alpha

    from square import Search as Square

    def make_square():
        square = Square()
        square.wordlist_file = 'nwl2023.txt'
        return square
    yield 'square', make_square

    from hurdle import Search as Hurdle

    def make_hurdle():
        hurdle = Hurdle()
        hurdle.wordlist_file = 'nwl2023.txt'
        return hurdle
    yield 'hurdle', make_hurdle

    from dontword import DontWord

    def make_dontword():
        dontword = DontWord()
        dontword.wordlist_file = 'nwl2023.txt'
        return dontword
    yield 'dontword', make_dontword

    from semantic import Search as Semantic

    def make_cemantle():
        cemantle = Semantic()
        return cemantle
    yield 'cemantle', make_cemantle

    def make_cemantix():
        cex = Semantic()
        cex.log_file = 'cemantix.log'
        cex.site = 'cemantix.certitudes.org'
        cex.lang = 'French'
        cex.pub_tzname = 'CET'
        return cex
    yield 'cemantix', make_cemantix

    from spaceword import SpaceWord

    def make_space():
        space = SpaceWord()
        space.wordlist_file = 'nwl2023.txt'
        return space
    yield 'space', make_space

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

solver_items = tuple(load_solvers())
solver_names = tuple(nom for nom, _ in solver_items)
solver_cons = tuple(make_solver for _, make_solver in solver_items)

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
            for i, nom in enumerate(solver_names)
            if pat.match(nom))

        if len(ix) == 0:
            ui.print('! no such solver')
            return -1
        elif len(ix) > 1:
            may = tuple(solver_names[i] for i in ix)
            ui.print(f'! Ambiguous solver; may be: {" ".join(may)}')
            return -1
        return ix[0]

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
            for i in range(len(solver_names)))

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

        notes: list[str] = []
        deets: list[str] = []

        def collect_notes():
            for _solver_i, day, note, head, body in self.read_status(ui):
                if day != today:
                    yield f'! {day} {note}'
                    continue

                notes.append(note)

                if deets:
                    deets.append(f'')
                deets.append(f'# {head}')
                deets.append(f'')
                deets.extend(f'> {line}' for line in trim_lines(body))

        def head_note():
            yield f'# {today}'
            yield f''
            for note in notes:
                yield f'- {note}'

        def summary(link: str=''):
            for note in sum_notes(notes):
                yield f'- {note}'
            if link:
                yield f''
                yield f'Details and spoilers: {link}'

        any_out = False
        for line in collect_notes():
            any_out = True
            ui.print(line)
        if any_out:
            ui.print(f'')

        # TODO maybe prompt rather than pipeline
        # TODO save / reuse summary from report file

        with ui.copy_writer() as cw:
            for line in head_note():
                print(line, file=cw)
            ui.print(f'📋 Share Header')
        _ = ui.input('<Press Enter To Continue>')

        with ui.copy_writer() as cw:
            for line in deets:
                print(line, file=cw)
            ui.print(f'📋 Share Details')
        link = ui.may_paste(subject='Share Details Link')

        with ui.copy_writer() as cw:
            for line in summary(link):
                print(line, file=cw)
            ui.print(f'📋 Share Summary')
        _ = ui.input('<Press Enter To Continue>')

        # def quote_lines(lines: Iterable[str], desc: str = '') -> Generator[str]:
        #     yield f'```{desc}'
        #     yield from lines
        #     yield f'```'

        # for i, section in enumerate((
        #     quote_lines(head_note(), 'Share Header'),
        #     quote_lines(deets, 'Share Details'),
        #     quote_lines(summary(), 'Share Summary'),
        # )):
        #     if i > 0:
        #         ui.print('')
        #     for line in section:
        #         ui.print(line)

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

        # TODO could be solver_class[i]
        solver = solver_cons[solver_i]()
        log_file = solver.log_file

        m = ui.tokens.have(r'(?x) last (?: : ( .* ) )?')
        if m:
            log_file = solver.find_prior_log(ui, m[1] or '')
            if log_file is None:
                return

        if ui.tokens.have('edit'):
            editor = os.environ.get('EDITOR', 'vi')
            _ = ui.check_call(subprocess.Popen((editor, log_file)))
            return

        if ui.tokens.have('rm'):
            ui.print(f'+ rm {log_file}')
            os.unlink(log_file)
            return

        if ui.tokens.have('cont'):
            return self.run_solver(ui, solver_i, log_file=log_file)

        # TODO fin / result

        # TODO share / report

        tail_n = 10 # TODO from terminal size
        _ = ui.check_call(subprocess.Popen(('tail', f'-n{tail_n}', log_file)))

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
        elif solver_i < 0:
            return
        self.run_solver(ui, solver_i)

    def run_solver(self, ui: PromptUI, solver_i: int, log_file: str|None=None):
        solver = solver_cons[solver_i]()

        ui.write(f'*** Running solver {solver_names[solver_i]}')
        if log_file:
            # TODO restore old ; maybe we should have solver_cons[i] ...
            solver.log_file = log_file
            ui.write(f' log_file={log_file}')
        ui.fin()

        ui.interact(solver)

    def do_solvers(self, ui: PromptUI):
        '''
        show known solvers
        '''
        for n, (nom, make_solver) in enumerate(solver_items, 1):
            solver = make_solver()
            ui.print(f'{n}. {nom} site:{solver.site!r} slug:{solver.note_slug!r}')

    def read_status(self, ui: PromptUI, verbose: bool=True):

        # TODO do this once per load_solvers
        solvers = tuple(
            make_solver()
            for make_solver in solver_cons)
        note_slugs = tuple(
            solver.note_slug[0]
            for solver in solvers)
        head_slugs = tuple(
            solver.header_slug
            for solver in solvers)

        days: list[datetime.date] = []
        notes: list[str] = ['' for _ in note_slugs]
        note_days: list[int] = [0 for _ in note_slugs]
        heads: list[str] = ['' for _ in head_slugs]
        bodys: list[tuple[str, ...]] = [() for _ in head_slugs]

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

                    for i, slug in enumerate(note_slugs):
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
                for i, slug in enumerate(head_slugs):
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

            ui.print(f'{mark} {solver_names[i]} {day} {note}')

if __name__ == '__main__':
    Meta.main()
