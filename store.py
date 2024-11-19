import argparse
import datetime
import os
import re
import subprocess
from collections.abc import Generator, Iterable
from contextlib import contextmanager
from dataclasses import dataclass
from dateutil.parser import parse as parse_datetime
from dateutil.tz import tzlocal
from typing import cast, final, Any, Callable

from ui import PromptUI

def replace_sections(
    lines: Iterable[str],
    want: Callable[[str], Iterable[str]|None]
) -> Generator[str]:
    empty = True

    for line in lines:
        line = line.rstrip('\n')

        body = line.startswith('#') and want(line)

        # pass lines from unwanted sections
        if not body:
            yield line
            empty = False if line else True
            continue

        # pass lines from replacement section
        for line in body:
            yield line
            empty = False if line else True

        for line in lines:
            line = line.rstrip('\n')
            if line.startswith('#'):
                if not empty: yield ''
                yield line
                empty = False if line else True
                break

            # else: skip prior section lines


def break_sections(*sections: Iterable[str], br: str = '') -> Generator[str]:
    first = True
    for section in sections:
        if first:
            for _ in section:
                first = False
                yield br
                yield _
                break
        else:
            yield br
        yield from section

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

@final
@dataclass
class LogSession:
    start: datetime.datetime
    elapsed: datetime.timedelta

class StoredLog:
    @classmethod
    def main(cls):
        import argparse

        search = cls()

        parser = argparse.ArgumentParser()
        search.add_args(parser)
        args = parser.parse_args()
        search.from_args(args)

        return PromptUI.main(search)

    dt_fmt: str = '%Y-%m-%dT%H:%M:%S%Z'
    default_site: str = ''

    ### @override-able surface for extension

    def __init__(self):
        self.start: datetime.datetime|None = None
        self.site: str = self.default_site
        self.puzzle_id: str = ''
        self.sessions: list[LogSession] = []

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

    def hist_body(self, _ui: PromptUI) -> Generator[str]:
        yield f'See {self.storing_file}'

    def review(self, _ui: PromptUI) -> PromptUI.State|None:
        raise NotImplementedError('StoredLog.review')

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

            yield t, rest

        if prior_then is not None and cur_t is not None:
            self.sessions.append(LogSession(prior_then, datetime.timedelta(seconds=cur_t)))

    ### store specifics

    store_dir: str = 'log/'
    hist_file: str = 'hist.md'
    log_file: str = 'unknown.log'
    storing_file: str = ''
    ephemeral: bool = True

    def load_log(self, ui: PromptUI, log_file: str|None = None):
        if log_file is None:
            log_file = self.log_file
        self.__init__()
        if log_file and os.path.exists(log_file):
            with open(log_file, 'r') as f:
                for _ in self.load(ui, f): pass
        self.log_file = log_file

    def __call__(self, ui: PromptUI) -> PromptUI.State|None:
        if self.log_file:
            self.load_log(ui, self.log_file)

        if self.stored:
            return self.review

        if self.is_expired:
            ui.print(f'! expired puzzle log started {self.start:{self.dt_fmt}}, but next puzzle expected at {self.expire:{self.dt_fmt}}')
            return self.expired

        return self.handle

    def handle(self, ui: PromptUI):
        if not self.run_done:
            with self.log_to(ui):
                try:
                    ui.interact(self.run)
                except (EOFError, KeyboardInterrupt):
                    raise StopIteration
        return self.store

    def run(self, ui: PromptUI) -> PromptUI.State|None:
        if self.start is None:
            self.start = datetime.datetime.now(tzlocal())

        expire = self.expire
        ui.print(f'📆 {self.start:%Y-%m-%d}')
        if self.site:
            ui.print(f'🔗 {self.site}')
        if self.puzzle_id:
            ui.print(f'🧩 {self.puzzle_id}')
        if expire is not None:
            ui.print(f'⏰ Expires {expire}')
        ui.print(f'📜 {self.log_file} with {len(self.sessions)} prior sessions over {self.elapsed}')

        return self.startup

    @property
    def is_expired(self):
        exp = self.expire
        return exp is not None and datetime.datetime.now(tzlocal()) >= exp

    def update_hist_file(self, ui: PromptUI):
        if not self.hist_file:
            ui.print('! no hist file set to update')
            return

        date = self.today
        if date is None:
            ui.print('! cannot find hist entry, today undefined')
            return

        site = self.site
        if not site:
            ui.print('! cannot find hist entry, site empty')
            return

        with atomic_file(self.hist_file) as f:
            for line in self.update_hist_lines(ui, date, site):
                print(line, file=f)

        ui.print(f'💾 updated {self.hist_file}')

    def update_hist_lines(self, ui: PromptUI, date: datetime.date, site: str) -> Generator[str]:
        header = f'# {date:%Y-%m-%d} {site}'
        body = self.hist_lines(ui, date)
        with open(self.hist_file, mode='r') as f:
            yield from break_sections(
                replace_sections(f,
                    lambda line: body if line.startswith(header) else None),
                body)

    def hist_lines(self, ui: PromptUI, date: datetime.date) -> Generator[str]:
        it = self.hist_body(ui)
        yield f'# {date:%Y-%m-%d} {self.site}'.strip()
        for line in it:
            if line: yield ''
            yield line
            break
        yield from it

    @property
    def elapsed(self):
        return sum(
            (s.elapsed for s in self.sessions),
            start=datetime.timedelta(seconds=0))

    def reload(self, ui: PromptUI, filename: str):
        self.__init__()
        with open(filename, 'r') as f:
            for _ in self.load(ui, f): pass
        self.log_file = filename

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
        _ = parser.add_argument('--store-hist', default=self.hist_file)
        _ = parser.add_argument('--site', default=self.default_site)
        _ = parser.add_argument('log_file', nargs='?', default=self.log_file)

    def from_args(self, args: argparse.Namespace):
        self.log_file = cast(str, args.log_file)
        self.store_dir = cast(str, args.store_log)
        self.hist_file = cast(str, args.store_hist)
        self.site = self.default_site = cast(str, args.site)

    def store(self, ui: PromptUI) -> PromptUI.State|None:
        if self.stored:
            want_log_file = self.should_store_to
            if want_log_file and self.log_file == want_log_file:
                return self.review

        if not (self.run_done or self.is_expired):
            ui.print('! declining to store unfinished and unexpired log')
            raise StopIteration

        if not self.site:
            token = ui.input('🔗 site ? ').head
            ui.log(f'site: {token}')
            self.site = token

        if not self.puzzle_id:
            token = ui.input('🧩 id ? ').head
            ui.log(f'puzzle_id: {token}')
            self.puzzle_id = token

        self.store_txn(ui)

    @property
    def stored(self):
        if not self.store_dir: return False
        if not self.log_file: return False
        return self.log_file.startswith(self.store_dir)

    @property
    def should_store_to(self):
        if not self.store_dir: return None
        puzzle_id = self.puzzle_id
        if not puzzle_id:
            date = self.today
            if date is None: return None
            puzzle_id = f'{date:%Y-%m-%d}'
        return os.path.join(self.store_dir, self.site, puzzle_id)

    def store_txn(self, ui: PromptUI):
        if not self.run_done:
            raise StopIteration

        if not self.store_dir and not self.hist_file:
            raise StopIteration

        date = self.today
        if date is None:
            default = datetime.datetime.today()
            token = ui.input(f'📆 {default:%Y-%m-%d} ? ').head
            if not token:
                date = default
            else:
                try:
                    date = datetime.datetime.strptime(token, '%Y-%m-%d')
                except ValueError:
                    ui.print('! must enter date in YYYY-MM-DD')
                    return

        puzzle_id = self.puzzle_id
        if not puzzle_id:
            puzzle_id = f'{date:%Y-%m-%d}'

        store_file = self.should_store_to

        ui.print(f'🔗 {self.site}')
        ui.print(f'🧩 {puzzle_id}')
        ui.print(f'📆 {date:%Y-%m-%d}')

        try:
            log_stored = False
            log_removed = False

            if store_file:
                self.storing_file = store_file

            with git_txn(f'{self.site} day {puzzle_id}') as txn:
                self.store_extra(ui, txn)

                if self.hist_file:
                    with open(self.hist_file, mode='a') as f:
                        print('', file=f)
                        for line in self.hist_lines(ui, date):
                            print(line, file=f)
                    txn.add(self.hist_file)
                    ui.print(f'📜 {self.hist_file}')

                if self.log_file and store_file:
                    log_stored = True
                    ensure_parent_dir(store_file)
                    os.link(self.log_file, store_file)
                    txn.add(store_file)

                if self.stored:
                    _ = subprocess.check_call(['git', 'rm', self.log_file])
                    log_removed = True

            if log_stored:
                if not log_removed:
                    os.unlink(self.log_file)
                self.log_file = self.storing_file
                ui.print(f'🗃️ {store_file}')
                self.reload(ui, self.log_file)

        finally:
            self.storing_file = ''

    def store_extra(self, _ui: PromptUI, _txn: 'git_txn'):
        pass

    def expired(self, ui: PromptUI) -> PromptUI.State|None:
        token = ui.input(f'[a]rchive, [r]emove, or [c]ontinue? ').head.lower()

        if 'archive'.startswith(token):
            return self.store

        elif 'remove'.startswith(token):
            os.unlink(self.log_file)
            self.__init__()
            ui.print(f'// removed {self.log_file}')

        elif 'continue'.startswith(token):
            return self.handle

        elif token:
            ui.print('! invalid choice')

@final
class git_txn:
    added: set[str] = set()

    def __init__(self, mess: str):
        self.mess = mess

    def add(self, *paths: str):
        _ = subprocess.check_call(['git', 'add', *paths])
        self.added.update(paths)

    def __enter__(self):
        return self

    def __exit__(self, exc_type: Any, exc: Any, exc_tb: Any): # pyright: ignore[reportAny]
        if self.added:
            if exc is None:
                _ = subprocess.check_call(['git', 'commit', '-m', self.mess])
            else:
                _ = subprocess.check_call(['git', 'reset', '--', *self.added])
                _ = subprocess.check_call(['git', 'restore', '-s', 'HEAD', '--', *self.added])

def ensure_parent_dir(file: str):
    pardir = os.path.dirname(file)
    if pardir and not os.path.exists(pardir):
        os.makedirs(pardir)

