import argparse
import datetime
import os
import re
import subprocess
from collections.abc import Generator, Iterable
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from dateutil.parser import parse as _parse_datetime
from dateutil.tz import gettz, tzlocal, tzoffset
from typing import cast, final
from types import TracebackType

from mdkit import break_sections, replace_sections
from ui import PromptUI

def parse_datetime(s: str):
    return _parse_datetime(s,
                 tzinfos=lambda name, offset: gettz(name) if name else tzoffset(name, offset))

@contextmanager
def atomic_file(name: str):
    f = open(f'{name}.new', 'x') # TODO random temp suffix
    ok = False
    try:
        with f:
            yield f
            os.rename(f.name, name)
            ok = True
    finally:
        if not ok:
            os.unlink(f.name)

@contextmanager
def atomic_rewrite(name: str):
    with (
        open(name, 'r') as r,
        atomic_file(name) as w,
    ):
        yield r, w

def backup_old(name: str):
    try:
        return open(name, 'x')
    except FileExistsError as err:
        mtime = os.path.getmtime(name)
        bak_name = f'{name}.old_{round(mtime)}'
        if os.path.exists(bak_name):
            raise err
        os.rename(name, bak_name)
    return open(name, 'x')

@final
@dataclass
class LogSession:
    start: datetime.datetime
    elapsed: datetime.timedelta

class StoredLog:
    @classmethod
    def main(cls):
        import argparse

        self = cls()

        parser = argparse.ArgumentParser()
        self.add_args(parser)
        args = parser.parse_args()
        self.from_args(args)

        return PromptUI.main(self)

    dt_fmt: str = '%Y-%m-%dT%H:%M:%S%Z'
    default_site: str = ''
    site_name: str = ''

    ### @override-able surface for extension

    def __init__(self):
        self.start: datetime.datetime|None = None
        self.site: str = self.default_site
        self.puzzle_id: str = ''
        self.sessions: list[LogSession] = []
        self.loaded: bool = False

    @property
    def expire(self) -> datetime.datetime|None:
        return None

    @property
    def today(self) -> datetime.date|None:
        return None

    def startup(self, _ui: PromptUI) -> PromptUI.State|None:
        raise NotImplementedError('StoredLog.startup')

    @property
    def run_done(self) -> bool:
        return False

    def review(self, ui: PromptUI) -> PromptUI.State|None:
        for line in self.report_body:
            ui.print(line)

        with ui.input(f'> ') as tokens:
            if tokens.have(r'report$'):
                return self.do_report(ui)

            if tokens.have(r'replay$'):
                return self.Replay(self)

            if tokens.have(r'cont(i(n(ue?)?)?)?$'):
                rep = self.Replay(self)
                line_no, time, mess = rep.seek(0)
                rep.cursor = line_no
                ui.print(f'*** {line_no}. T{time:.1f} {mess}')
                return rep.restart(ui, mess=f'^^^ continuing from last line')

            ui.print(f'! invalid review command {tokens.rest!r}')

    @final
    class Replay:
        def __init__(self, stl: 'StoredLog'):
            self.stl = stl
            self.cursor: int = 1

        def skim_log(self) -> Generator[tuple[int, str]]:
            with open(self.stl.log_file, 'r') as f:
                yield from enumerate(f, 1)

        def parse_log(self):
            for line_no, line in self.skim_log():
                match = re.match(r'''(?x)
                    T (?P<time> [^\s]+ )
                    \s+
                    (?P<mess> .+ )
                    $''', line)
                if not match: continue
                time = float(match.group(1))
                mess = str(match.group(2))
                yield line_no, time, mess

        def seek(self, offset: int):
            '''
            Seek line number offset.

            Since line numbers count naturally from 1,
            we use offset 0 to mean last line (aka EOF).

            Furthermore, negative offsets count back from the last line.

            So pass a postive number, and it will be truncated if necessary;
            i.e. `seek(10)` can mean "you wanted line 10, best I can do is 5".

            For the last line `seek(0)`, 2nd-to last line is `seek(-1)`, etc.
            '''
            if offset <= 0:
                line_no = 0
                for line_no, _ in self.skim_log():
                    pass
                offset = max(0, line_no - offset)
            line_no, time, mess = 0, 0.0, ''
            for line_no, time, mess in self.parse_log():
                if line_no >= offset: break
            return line_no, time, mess

        def __call__(self, ui: PromptUI):
            with ui.input(f'replay> ') as tokens:
                if tokens.have(r'cont(i(n(ue?)?)?)?$'):
                    line_no, time, mess = self.seek(0)
                    self.cursor = line_no
                    ui.print(f'*** {line_no}. T{time:.1f} {mess}')
                    return self.restart(ui, mess=f'^^^ continuing from last line')

                C = 5
                line_lo = max(0, self.cursor - C)
                line_hi = self.cursor + C
                found = False
                last_line = 0
                for line_no, time, mess in self.parse_log():
                    if line_lo < line_no <= line_hi:
                        found = True
                        ui.print(f'{"***" if line_no == self.cursor else "   "} {line_no}. T{time:.1f} {mess}')
                    last_line = line_no
                if not found:
                    self.cursor = last_line if self.cursor > last_line else 1

                match = tokens.have(r'S(\d*)')
                if match:
                    sn = str(match.group(1))
                    want = int(sn) if sn else None

                    n = 0
                    for line_no, time, mess in self.parse_log():
                        match = re.match(r'''(?x)
                            now :
                            \s+
                            (?P<then> .+ )
                            $''', mess)
                        if not match: continue
                        n += 1
                        if want is None:
                            then = match.group(1)
                            ui.print(f'... {line_no}. S{n} {then}')
                        elif n == want:
                            self.cursor = line_no
                            return

                    if want is not None:
                        ui.print(f'!!! S{want} not found')
                    ui.print('')
                    return

                at = tokens.have(r'@(\d+)', lambda match: int(match.group(1)))
                if at is not None:
                    self.cursor = at
                    return

                off = tokens.have(r'([\-+]\d+)', lambda match: int(match.group(1)))
                if off is not None:
                    self.cursor = max(1, self.cursor + off)
                    return

                patstr = tokens.have(r'/(.+)', lambda match: str(match[1]))
                if patstr:
                    try:
                        pattern = re.compile(patstr)
                    except re.PatternError as err:
                        ui.print(f'!!! invalid pattern /{patstr}/ : {err}')
                        return
                    for line_no, time, mess in self.parse_log():
                        if not pattern.match(mess): continue
                        ui.print(f'... {line_no}. T{time:.1f} {mess}')
                    ui.print('')
                    return

                litstr = tokens.have(r'"(.+)', lambda match: str(match[1]))
                if litstr:
                    for line_no, time, mess in self.parse_log():
                        if litstr not in mess: continue
                        ui.print(f'... {line_no}. T{time:.1f} {mess}')
                    ui.print('')
                    return

                if tokens.have(r'start$'):
                    return self.restart

        def restart(self,
                    ui: PromptUI,
                    mess: str|None = None):
            init_log_file = self.stl.__class__.log_file
            with ui.input(f'log file (default: {init_log_file}) ? ') as tokens:
                new_log_file = tokens.rest.strip() or init_log_file
                with (
                    open(self.stl.log_file, 'r') as fr,
                    backup_old(new_log_file) as fw):
                    for line_no, line in enumerate(fr, 1):
                        _ = fw.write(line)
                        if line_no >= self.cursor: break
                    if mess is None:
                        ui.print(f'Truncated log into {new_log_file}')
                    elif mess:
                        ui.print(mess)

                return self.stl.load_log(ui, new_log_file)

    def load(self, ui: PromptUI, lines: Iterable[str]):
        prior_t: float|None = None
        prior_then_t: float|None = None
        prior_then: datetime.datetime|None = None
        cur_t: float|None = None

        for line in lines:
            match = re.match(r'''(?x)
                T (?P<time> [^\s]+ )
                \s+
                (?P<rest> .+ )
                $''', line)
            if not match:
                yield 0, line
                continue

            st, rest = match.groups()
            t = float(st)

            match = re.match(r'''(?x)
                now :
                \s+
                (?P<then> .+ )
                $''', rest)
            if match:
                try:
                    sthen, = match.groups()
                    then = parse_datetime(sthen)
                except ValueError:
                    ui.print(f'WARNING: unable to parse prior log start time from {rest!r}')
                else:
                    if self.start is None:
                        self.start = then
                    elif prior_then is not None:
                        dur = 0
                        if prior_t is not None:
                            assert prior_then_t is not None
                            dur = prior_t - prior_then_t
                        self.sessions.append(LogSession(prior_then, datetime.timedelta(seconds=dur)))
                    prior_then = then
                    prior_then_t = t
                    prior_t, cur_t = None, t
                continue

            prior_t, cur_t = cur_t, t

            match = re.match(r'''(?x)
                site :
                \s+
                (?P<token> [^\s]+ )
                \s* ( .* )
                $''', rest)
            if match:
                token, rest = match.groups()
                assert rest == ''
                self.site = token
                continue

            match = re.match(r'''(?x)
                puzzle_id :
                \s+
                (?P<token> [^\s]+ )
                \s* ( .* )
                $''', rest)
            if match:
                token, rest = match.groups()
                assert rest == ''
                self.puzzle_id = token
                continue

            yield t, rest

        if prior_then is not None and cur_t is not None:
            self.sessions.append(LogSession(prior_then, datetime.timedelta(seconds=cur_t)))

    ### store specifics

    store_dir: str = 'log/'
    log_file: str = 'unknown.log'
    ephemeral: bool = True

    def load_log(self, ui: PromptUI, log_file: str|None = None):
        if log_file is None:
            log_file = self.log_file
        if log_file == self.log_file and self.loaded:
            return self
        if not self.ephemeral:
            raise CutoverLogError(log_file)
        if self.loaded:
            self.__init__()
        if log_file and os.path.exists(log_file):
            with open(log_file, 'r') as f:
                for _ in self.load(ui, f): pass
        self.loaded = True
        self.log_file = log_file
        return self

    def __call__(self, ui: PromptUI) -> PromptUI.State|None:
        if self.log_file and not self.loaded:
            return self.load_log(ui)

        if self.stored:
            return self.review

        if self.is_expired:
            ui.print(f'! expired puzzle log started {self.start:{self.dt_fmt}}, but next puzzle expected at {self.expire:{self.dt_fmt}}')
            return self.expired

        return self.handle

    def handle(self, ui: PromptUI):
        if not self.run_done:
            try:
                with self.log_to(ui):
                    ui.interact(self.run)
            except CutoverLogError as cutover:
                self.__init__()
                self.log_file = cutover.log_file
                return self
            except (EOFError, KeyboardInterrupt):
                raise StopIteration
        return self.store

    def run(self, ui: PromptUI) -> PromptUI.State|None:
        if self.start is None:
            self.start = datetime.datetime.now(tzlocal())
            if self.site: ui.log(f'site: {self.site}')
            if self.puzzle_id: ui.log(f'puzzle_id: {self.puzzle_id}')

        ui.print(f'📜 {self.log_file} with {len(self.sessions)} prior sessions over {self.elapsed}')

        expire = self.expire
        if expire is not None: ui.print(f'⏰ Expires {expire}')

        return self.startup

    @property
    def is_expired(self):
        exp = self.expire
        return exp is not None and datetime.datetime.now(tzlocal()) >= exp

    @property
    def elapsed(self):
        return sum(
            (s.elapsed for s in self.sessions),
            start=datetime.timedelta(seconds=0))

    @contextmanager
    def log_to(self, ui: PromptUI, log_file: str|None=None):
        if not self.ephemeral:
            raise RuntimeError('already logging')
        prior_log_file = self.log_file
        try:
            if log_file is not None:
                self.log_file = log_file
            self.ephemeral = False
            with open(self.log_file, 'a') as f:
                with ui.deps(log_file=f) as ui:
                    now = datetime.datetime.now(tzlocal())
                    ui.log(f'now: {now:{self.dt_fmt}}')
                    yield self, ui
        finally:
            self.ephemeral = True
            self.log_file = prior_log_file

    def add_args(self, parser: argparse.ArgumentParser):
        _ = parser.add_argument('--store-log', default=self.store_dir)
        _ = parser.add_argument('--site', default=self.default_site)
        _ = parser.add_argument('log_file', nargs='?', default=self.log_file)

    def from_args(self, args: argparse.Namespace):
        self.log_file = cast(str, args.log_file)
        self.store_dir = cast(str, args.store_log)
        self.site = self.default_site = cast(str, args.site)

    @property
    def stored(self):
        if not self.store_dir: return False
        if not self.log_file: return False
        return self.log_file.startswith(self.store_dir)

    @property
    def store_name(self):
        site = self.site
        if '://' in site:
            _, _, site = site.partition('://')
        site = site.replace('/', '_')
        return site

    @property
    def store_subdir(self):
        if not self.store_dir: return None
        return os.path.join(self.store_dir, self.store_name)

    @property
    def should_store_to(self):
        store_dir = self.store_subdir
        if not store_dir: return None
        puzzle_id = self.puzzle_id
        if not puzzle_id:
            date = self.today
            if date is None: return None
            puzzle_id = f'{date:%Y-%m-%d}'
        return os.path.join(store_dir, puzzle_id)

    def store(self, ui: PromptUI) -> PromptUI.State|None:
        if not self.store_dir:
            ui.print('! no store dir')
            raise StopIteration

        if self.stored:
            want_log_file = self.should_store_to
            if want_log_file and self.log_file == want_log_file:
                return self.review
            ui.print(f'Fixing stored log file name {self.log_file} -> {want_log_file}')

        if not self.site:
            with ui.input('🔗 site ? ') as tokens:
                site = next(tokens, '')
                if not site: return
                ui.log(f'site: {site}')
                self.site = site

        date = self.today
        if date is None:
            date = datetime.datetime.today().date()
            with ui.input(f'📆 {date:%Y-%m-%d} ? ') as tokens:
                if not tokens.empty:
                    try:
                        date = datetime.datetime.strptime(next(tokens), '%Y-%m-%d').date()
                    except ValueError:
                        ui.print('! must enter date in YYYY-MM-DD')
                        return

        if not self.puzzle_id:
            default_puzzle_id = f'{date:%Y-%m-%d}'
            with ui.input(f'🧩 id (default: {default_puzzle_id}) ? ') as tokens:
                puzzle_id = next(tokens, '')
                self.puzzle_id = default_puzzle_id if not puzzle_id else puzzle_id
            ui.log(f'puzzle_id: {self.puzzle_id}')

        ui.print(f'🔗 {self.site} 🧩 {self.puzzle_id} 📆 {date:%Y-%m-%d}')

        self.do_store(ui, date)
        self.do_report(ui)

    def do_store(self, ui: PromptUI, _date: datetime.date):
        with self.storing_to(ui) as txn:
            self.store_extra(ui, txn)

    @contextmanager
    def storing_to(self, ui: PromptUI):
        store_to = self.should_store_to or ''
        prior_log = self.log_file
        if not prior_log or not store_to: return
        was_stored = self.stored
        with git_txn(f'{self.site_name or self.store_name} day {self.puzzle_id}', ui=ui) as txn:
            with (
                txn.will_rm(prior_log) if was_stored else nullcontext(),
                txn.will_add(store_to)):
                ensure_parent_dir(store_to)
                try:
                    os.link(prior_log, store_to)
                except FileExistsError:
                    os.unlink(store_to)
                    os.link(prior_log, store_to)
            yield txn
            txn.commit()
            ui.write(f'🗃️ {store_to}')
            if prior_log not in txn.removed:
                os.unlink(prior_log)
                ui.write(f' <- {prior_log}')
            ui.fin()

        _ = self.load_log(ui, store_to)

    def store_extra(self, _ui: PromptUI, _txn: 'git_txn'):
        pass

    def expired(self, ui: PromptUI) -> PromptUI.State|None:
        with ui.input(f'[a]rchive, [r]emove, or [c]ontinue? ') as tokens:
            token = next(tokens, '').lower()

            if 'archive'.startswith(token):
                ui.print('Archiving expired log')
                return self.store

            elif 'remove'.startswith(token):
                os.unlink(self.log_file)
                ui.print(f'// removed {self.log_file}')
                self.__init__()
                return self

            elif 'continue'.startswith(token):
                return self.handle

            elif token:
                ui.print('! invalid choice')

    report_file: str = 'report.md' # TODO hoist and wire up to arg

    @property
    def report_desc(self) -> str:
        return  f'⏱️ {self.elapsed}'

    def info(self):
        yield f'📜 {len(self.sessions)} sessions'

    @property
    def report_body(self) -> Generator[str]:
        yield from self.info()

    def report_section(self) -> Generator[str]:
        yield self.report_header()
        yield ''
        yield from self.report_body

    def report_header(self, desc: str|None = None) -> str:
        return f'# {self.site_link} 🧩 {self.puzzle_id} {self.report_desc if desc is None else desc}'

    @property
    def site_link(self):
        return f'[{self.site_name}]({self.site})' if self.site_name else f'{self.site}'

    def report_note(self, desc: str|None = None) -> str:
        return  f'- 🔗 {self.site_link} 🧩 {self.puzzle_id} {self.report_desc if desc is None else desc}'

    def do_report(self, ui: PromptUI):
        head_id = self.report_header(desc='')
        note_id = self.report_note(desc='')

        def rep(line: str) -> Iterable[str]|None:
            if line.startswith(head_id):
                return body

        body = self.report_section()

        with (
            git_txn(f'DAILY {self.site_name or self.store_name}', ui=ui) as txn,
            txn.will_add(self.report_file),
            atomic_rewrite(self.report_file) as (r, w)
        ):
            lines = break_sections(replace_sections(r, rep), body)

            note = self.report_note()
            for line in lines:
                if line.startswith(note_id):
                    print(note, file=w)
                    continue

                if not line:
                    print(note, file=w)
                    print(line, file=w)
                    break

                if not line.startswith('- '):
                    print(note, file=w)
                    print('', file=w)
                    print(line, file=w)
                    break

                print(line, file=w)

            for line in lines:
                print(line, file=w)

@final
class CutoverLogError(RuntimeError):
    def __init__(self, log_file: str):
        super().__init__('cutover to new log file')
        self.log_file = log_file

@final
class git_txn:
    added: set[str] = set()
    removed: set[str] = set()

    def __init__(self, mess: str, ui: PromptUI|None = None):
        self.mess = mess
        self.ui = ui

    def add(self, *paths: str):
        _ = subprocess.check_call(['git', 'add', *paths])
        novl = set(paths).difference(self.removed)
        self.removed.difference_update(paths)
        self.added.update(novl)
        if self.ui:
            self.ui.print(f'📜➕ {" ".join(paths)}')

    def rm(self, *paths: str):
        _ = subprocess.check_call(['git', 'rm', *paths])
        gone = set(paths).difference(self.added)
        self.added.difference_update(paths)
        self.removed.update(gone)
        if self.ui:
            self.ui.print(f'📜➖ {" ".join(paths)}')

    @contextmanager
    def will_add(self, *paths: str):
        try:
            yield
        except:
            _ = subprocess.check_call(['git', 'checkout', *paths])
            raise
        else:
            self.add(*paths)

    @contextmanager
    def will_rm(self, *paths: str):
        try:
            yield
        except:
            _ = subprocess.check_call(['git', 'checkout', *paths])
            raise
        else:
            self.rm(*paths)

    def commit(self):
        if self.added or self.removed:
            _ = subprocess.check_call(['git', 'commit', '-m', self.mess])
            self.added.clear()
            self.removed.clear()

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        if self.added or self.removed:
            if exc is None:
                self.commit()
            else:
                _ = subprocess.check_call(['git', 'reset', '--', *self.added])
                _ = subprocess.check_call(['git', 'restore', '-s', 'HEAD', '--', *self.added])

def ensure_parent_dir(file: str):
    pardir = os.path.dirname(file)
    if pardir and not os.path.exists(pardir):
        os.makedirs(pardir)

