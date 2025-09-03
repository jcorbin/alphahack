import argparse
import datetime
import os
import re
import subprocess
from warnings import deprecated
import zlib
from base64 import b85decode, b85encode
from collections.abc import Generator, Iterable
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from dateutil.parser import parse as _parse_datetime
from dateutil.tz import gettz, tzlocal, tzoffset
from typing import Callable, cast, final
from types import TracebackType

from mdkit import break_sections, replace_sections
from ui import LogTime, PromptUI

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
    try:
        r = open(name, 'r')
    except FileNotFoundError:
        r = open('/dev/null', 'r')
    with r, atomic_file(name) as w:
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

@final
class LogParser:
    def __init__(self,
                 rez: Callable[[bytes], None]|None = None,
                 warn: Callable[[str], None]|None = None,
                 ):
        self.log_time = LogTime()
        self.unz = zlib.decompressobj()
        self.rez = rez
        self.warn = warn
        self.zlib_fails: int = 0

    def __call__(self, line: str) -> tuple[float|None, bool, str]:
        orig = line

        tokens = PromptUI.Tokens(line)

        if not self.log_time.parse(tokens):
            if not self.warn:
                raise ValueError('invalid log line, missing time')
            self.warn(f'invalid log line {orig!r}, missing time')
            return None, False, line

        z = bool(tokens.have(r'''(?x) Z $'''))
        if z:
            zline = tokens.rest
            zb = b85decode(zline)
            try:
                b = self.unz.decompress(zb)
            except zlib.error as err:
                if not self.warn:
                    raise
                self.zlib_fails += 1
                if self.zlib_fails <= 1:
                    self.warn(f'failed to decompress line {orig!r}: {err}')
                return self.log_time.t2, False, f'Z {zline}'
            if self.rez is not None:
                self.rez(b)
            tokens.rest = b.decode()

        fails = self.zlib_fails
        if fails:
            if fails > 1 and self.warn:
                self.warn(f'... and {fails-1} more lines')
            self.zlib_fails = 0

        return self.log_time.t2, z, tokens.rest

class StoredLog:
    @classmethod
    def main(cls):
        import argparse

        self = cls()

        parser = argparse.ArgumentParser()
        self.add_args(parser)
        args = parser.parse_args()
        self.from_args(args)
        trace = cast(bool, args.trace)

        return PromptUI.main(self, trace=trace)

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
        self.log_start: datetime.datetime|None = None

        self.expired_prompt: PromptUI.Prompt = PromptUI.Prompt(self.expired_prompt_mess, {
            'archive': self.expired_do_archive,
            'continue': lambda _: self.handle,
            'finalize': self.do_finalize,
            'remove': self.expired_do_remove,
            'result': self.do_result,
        })

        self.review_prompt: PromptUI.Prompt = PromptUI.Prompt(self.review_prompt_mess, {
            'compress': self.review_do_comp,
            'continue': self.review_do_cont,
            'finalize': self.do_finalize,
            'replay': lambda _: self.Replay(self),
            'report': self.do_report,
            'result': self.do_result,
        })

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

    def review_prompt_mess(self, ui: PromptUI):
        if self.review_prompt.re == 0:
            for line in self.report_body:
                ui.print(line)
        return '> '

    @deprecated('use .review_prompt directly')
    def review(self, ui: PromptUI) -> PromptUI.State|None:
        return self.review_prompt(ui)

    @deprecated('use .review_prompt.handle directly')
    def handle_review(self, ui: PromptUI):
        return self.review_prompt.handle(ui)

    def do_finalize(self, ui: PromptUI):
        return (
            self.interact(ui, self.finalize)
            if self.ephemeral else self.finalize)

    def do_result(self, ui: PromptUI):
        return (
            self.interact(ui, self.prompt_result)
            if self.ephemeral else self.prompt_result)

    @property
    def init_log_file(self):
        return self.__class__.log_file

    def finalize(self, ui: PromptUI):
        if not self.fin_result():
            return self.prompt_result(ui, 'final' if self.have_result() else '')

        if not self.stored:
            return self.store

        if self.dirty:
            with git_txn(f'{self.site_name or self.store_name} {self.puzzle_id} result', ui=ui) as txn:
                txn.add(self.log_file)
            if self.in_report(ui):
                self.do_report(ui)
            raise StopIteration

        return self.review_prompt

    def prompt_result(self, ui: PromptUI, reason: str=''):
        subject = f'{reason} share result' if reason else 'share result'
        try:
            self.proc_result(ui, ui.may_paste(subject=subject))
        except ValueError as err:
            ui.print(f'! {err}')
        return self.finalize

    def have_result(self) -> bool:
        raise NotImplementedError('abstract result processing')

    def proc_result(self, _ui: PromptUI, _text: str) -> None:
        raise NotImplementedError('abstract result processing')

    def fin_result(self) -> bool:
        return self.have_result()

    def skim_log(self) -> Generator[tuple[int, str]]:
        with open(self.log_file, 'r') as f:
            yield from enumerate(f, 1)

    def parse_log(self, warn: Callable[[str], None]|None=None):
        if warn:
            sink = warn
            def log_warn(mess: str):
                sink(f'#{n}: {mess}')
            warn = log_warn
        parse = LogParser(warn=warn)
        for n, line in self.skim_log():
            yield n, *parse(line)

    def review_do_comp(self, ui: PromptUI):
        pat = re.compile(ui.tokens.rest) if ui.tokens else None
        count = 0
        skip = 0

        before = os.stat(self.log_file)
        with atomic_rewrite(self.log_file) as (r, w):
            rez = zlib.compressobj()
            parse = LogParser(
                warn=lambda mess: ui.print(f'! rez parse {mess}'))
            log_time = LogTime()
            for line in r:
                t, z, line = parse(line)
                if t is None:
                    log_time.reset()
                else:
                    log_time.update(t)
                if not z:
                    if line.startswith('Z '):
                        skip += 1
                        continue
                    if pat and pat.search(line):
                        z = True
                        count += 1

                if z:
                    zb1 = rez.compress(line.encode())
                    zb2 = rez.flush(zlib.Z_SYNC_FLUSH)
                    _ = w.write(f'{log_time} Z {b85encode(zb1 + zb2).decode()}\n')
                else:
                    _ = w.write(f'{log_time} {line}\n')

            w.flush()
        after = os.stat(self.log_file)

        ds = after.st_size - before.st_size
        ch = after.st_size/before.st_size - 1.0
        ui.print(f'compressed {count} lines, {skip} elided, change: {ds:+} bytes ( {100*ch:.1f}% )')

    def cont_rep(self, ui: PromptUI):
        rep = self.Replay(self)
        line_no, time, mess = rep.seek(0, warn=lambda mess: ui.print(f'! seek {mess}'))
        rep.cursor = line_no
        ui.print(f'*** {line_no}. T{time:.1f} {mess}')
        return rep

    def review_do_cont(self, ui: PromptUI):
        rep = self.cont_rep(ui)
        return rep.restart(ui, mess=f'^^^ continuing from last line')

    @final
    class Replay:
        def __init__(self, stl: 'StoredLog'):
            self.stl = stl
            self.cursor: int = 1
            self.prompt = PromptUI.Prompt(self.prompt_mess, {
                'at': self.do_at,
                'contains': self.do_contains,
                'continue': self.do_continue,
                'grep': self.do_grep,
                'offset': self.do_offset,
                'session': self.do_session,
                'start': self.do_start,

                '@': 'at',
                # TODO would be nice to match r'([\-+]\d+)' -> offset
                # TODO would be nice to match r'S(\d*)'
            })

        def __call__(self, ui: PromptUI):
            return self.prompt(ui)

        def seek(self, offset: int, warn: Callable[[str], None]|None=None):
            '''
            Seek line number offset.

            Since line numbers count naturally from 1,
            we use offset 0 to mean last line (aka EOF).

            Furthermore, negative offsets count back from the last line.

            So pass a postive number, and it will be truncated if necessary;
            i.e. `seek(10)` can mean "you wanted line 10, best I can do is 5".

            For the last line `seek(0)`, 2nd-to last line is `seek(-1)`, etc.

            If warn is given, unparseable lines will be skipped, so the
            returned line number will be the first parseable line after offset.
            '''
            if offset <= 0:
                line_no = 0
                for line_no, _ in self.stl.skim_log():
                    pass
                offset = max(0, line_no - offset)
            line_no, time, mess = 0, 0.0, ''
            for line_no, time, _z, mess in self.stl.parse_log(warn=warn):
                if line_no >= offset: break
            return line_no, time, mess

        def prompt_mess(self, ui: PromptUI):
            if self.prompt.re == 0:
                C = 5
                line_lo = max(0, self.cursor - C)
                line_hi = self.cursor + C
                found = False
                last_line = 0
                for line_no, time, _z, mess in self.stl.parse_log():
                    if line_lo < line_no <= line_hi:
                        found = True
                        ui.print(f'{"***" if line_no == self.cursor else "   "} {line_no}. T{time:.1f} {mess}')
                    last_line = line_no
                if not found:
                    self.cursor = last_line if self.cursor > last_line else 1
            return f'replay> '

        def do_at(self, ui: PromptUI):
            n = ui.tokens.have(r'\d+', lambda m: int(m[0]))
            if n is None:
                ui.print(f'at: {self.cursor}')
            else:
                ui.print(f'at: {n} <- {self.cursor}')
                self.cursor = n

        def do_contains(self, ui: PromptUI):
            '''
            print lines that contain all given tokens
            usage: `contains <token> [<token> ...]`
            '''
            lits = tuple(ui.tokens)
            if not lits: return
            for line_no, time, _z, mess in self.stl.parse_log():
                if not any(lit in mess for lit in lits): continue
                ui.print(f'... {line_no}. T{time:.1f} {mess}')
            ui.print('')

        def do_continue(self, ui: PromptUI):
            '''
            continue after last prior line
            '''
            line_no, time, mess = self.seek(0)
            self.cursor = line_no
            ui.print(f'*** {line_no}. T{time:.1f} {mess}')
            return self.restart(ui, mess=f'^^^ continuing from last line')

        def do_grep(self, ui: PromptUI):
            '''
            print lines that match give regular expression
            usage: `grep <pattern ...>`
            '''
            patstr = ui.tokens.rest
            if not patstr:
                ui.print('! missing pattern')
                return

            try:
                pattern = re.compile(patstr)
            except re.PatternError as err:
                ui.print(f'!!! invalid pattern /{patstr}/ : {err}')
                return
            for line_no, time, _z, mess in self.stl.parse_log():
                if not pattern.match(mess): continue
                ui.print(f'... {line_no}. T{time:.1f} {mess}')
            ui.print('')

        def do_offset(self, ui: PromptUI):
            off = ui.tokens.have(r'[\-+]\d+', lambda m: int(m[0]))
            if off is not None:
                n = max(1, self.cursor + off)
                ui.print(f'at: {n} <- {self.cursor}')
                self.cursor = n

        def do_session(self, ui: PromptUI):
            want = ui.tokens.have(r'\d+', lambda m: int(m[0]))

            n = 0
            for line_no, _t, _z, mess in self.stl.parse_log():
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
                    ui.print(f'at: {line_no} <- {self.cursor}')
                    self.cursor = line_no
                    return

            if want is not None:
                ui.print(f'!!! S{want} not found')
            ui.print('')

        def do_start(self, _ui: PromptUI):
            '''
            start a new session at current line
            '''
            return self.restart

        def restart(self,
                    ui: PromptUI,
                    mess: str|None = None,
                    log_file: str|None = None,
                    then: PromptUI.State|None = None):
            if then is None:
                then = self.stl

            if log_file is None:
                log_file = self.stl.init_log_file
                with ui.input(f'log file (default: {log_file}) ? ') as tokens:
                    log_file = tokens.rest.strip() or log_file

            with (
                open(self.stl.log_file, 'r') as fr,
                backup_old(log_file) as fw):
                for line_no, line in enumerate(fr, 1):
                    _ = fw.write(line)
                    if line_no >= self.cursor: break
                if mess is None:
                    ui.print(f'Truncated log into {log_file}')
                elif mess:
                    ui.print(mess)

            self.stl.load_log(ui, log_file)
            return then

    def load(self, ui: PromptUI, lines: Iterable[str]) -> Generator[tuple[float, str]]:
        rez = zlib.compressobj()
        def flushit(b: bytes):
            _ = rez.compress(b)
            _ = rez.flush(zlib.Z_SYNC_FLUSH)
        parse = LogParser(
            rez=flushit,
            warn=lambda mess: ui.print(f'! parse #{no}: {mess}'))

        prior_t: float|None = None
        prior_then: datetime.datetime|None = None
        cur_t: float|None = None

        for no, line in enumerate(lines, 1):
            t, _z, rest = parse(line)

            if t is None:
                yield 0, line
                continue

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
                        dur = 0 if prior_t is None else prior_t
                        self.sessions.append(LogSession(prior_then, datetime.timedelta(seconds=dur)))
                    if self.log_start is None:
                        self.log_start = then
                    prior_then = then
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

        ui.zlog = rez

    ### store specifics

    store_dir: str = 'log/'
    log_file: str = 'unknown.log'
    ephemeral: bool = True

    def load_log(self, ui: PromptUI, log_file: str|None = None):
        if log_file is None:
            log_file = self.log_file
        if log_file == self.log_file and self.loaded:
            return
        if not self.ephemeral:
            raise CutoverLogError(log_file)
        self.set_log_file(ui, log_file)

    def set_log_file(self, ui: PromptUI, log_file: str):
        if self.loaded:
            self.__init__()
        if log_file and os.path.exists(log_file):
            with open(log_file, 'r') as f:
                for _ in self.load(ui, f): pass
        self.loaded = True
        self.log_file = log_file

    def __call__(self, ui: PromptUI) -> PromptUI.State|None:
        spec_match = re.fullmatch(r'''(?x)
                                  (?P<puzzle_id> .*? )
                                  :
                                  (?P<action> .* )
                                  ''', self.log_file)
        if spec_match:
            puzzle_id = str(spec_match[1])
            action = str(spec_match[2])

            sd = self.store_subdir
            if not sd:
                ui.print(f'! no store directory available to look for {puzzle_id!r}')
                raise StopIteration

            def find():
                if not puzzle_id:
                    return max((
                        ent.path
                        for ent in os.scandir(sd)
                        if ent.is_file()
                    ), default='')

                maybe_log_file = os.path.join(sd, puzzle_id)
                if os.path.isfile(maybe_log_file):
                    return maybe_log_file

                mayhaps = tuple(
                    ent.path
                    for ent in os.scandir(sd)
                    if puzzle_id in ent.name)
                if len(mayhaps) == 1:
                    return mayhaps[0]

                if len(mayhaps) > 1:
                    ui.print(f'! ambiguous substring, mayhaps: {mayhaps!r}')

            found_log_file = find()
            if not found_log_file:
                ui.print(f'! unable to find prior log {puzzle_id!r} in {sd}')
                raise StopIteration

            ui.print(f'Found log file {found_log_file}')
            self.log_file = found_log_file

            if action:
                ui.tokens = ui.Tokens(action)

        if self.log_file and not self.loaded:
            self.load_log(ui)
            return

        if self.stored:
            return self.review_prompt

        if self.is_expired:
            ui.print(f'! expired puzzle log started {self.start:{self.dt_fmt}}, but next puzzle expected at {self.expire:{self.dt_fmt}}')
            return self.expired_prompt

        return self.handle

    def handle(self, ui: PromptUI):
        if not self.run_done:
            self.interact(ui, self.run)
        return self.store

    def interact(self, ui: PromptUI, st: PromptUI.State):
        while True:
            try:
                with self.log_to(ui):
                    ui.call_state(st)
            except CutoverLogError as cutover:
                self.__init__()
                self.log_file = cutover.log_file
            except (EOFError, KeyboardInterrupt):
                raise StopIteration

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
        prior_log_start = self.log_start
        try:
            self.log_start = None
            if log_file is not None:
                self.log_file = log_file
            if self.stored:
                yield self, ui
            else:
                self.ephemeral = False
                with open(self.log_file, 'a') as f:
                    with ui.deps(log_file=f) as ui:
                        now = datetime.datetime.now(tzlocal())
                        self.log_start = now
                        ui.log(f'now: {now:{self.dt_fmt}}')
                        yield self, ui
        finally:
            self.ephemeral = True
            self.log_file = prior_log_file
            self.log_start = prior_log_start

    def add_args(self, parser: argparse.ArgumentParser):
        _ = parser.add_argument('--trace', '-t', action='store_true',
                                help='Enable execution state tracing')
        _ = parser.add_argument('--store-log', default=self.store_dir)
        _ = parser.add_argument('--site', default=self.default_site)
        _ = parser.add_argument('log_file', nargs='?', default=self.log_file,
                                metavar='FILE | [PUZZLE_ID]:[COMMAND]',
                                help='E.g. pass `:cont` to continue the latest stored log')

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
    def dirty(self):
        if self.ephemeral: return False # not appending to log
        if not self.stored: return False # untracked log
        code = subprocess.call(['git', 'diff', '--quiet', self.log_file])
        if code == 0: return False
        if code == 1: return True
        raise RuntimeError(f'unexpected git-diff exit code {code}')

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
                return self.review_prompt
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
                    ui.print(f'📁🔗 {prior_log} -> {store_to}')
                except FileExistsError:
                    os.unlink(store_to)
                    ui.print(f'📁🪓 {store_to}')
                    os.link(prior_log, store_to)
                    ui.print(f'📁🔗 {prior_log} -> {store_to}')
            yield txn
            txn.commit()
            ui.print(f'🗃️ {txn.mess}')
            if prior_log not in txn.removed:
                os.unlink(prior_log)
                ui.print(f'📁🪓 {prior_log}')

        self.load_log(ui, store_to)

    def store_extra(self, _ui: PromptUI, _txn: 'git_txn'):
        pass

    def expired_prompt_mess(self, _ui: PromptUI):
        return f'[a]rchive, [r]emove, or [c]ontinue? '

    @deprecated('use .expired_prompt directly')
    def expired(self, ui: PromptUI) -> PromptUI.State|None:
        return self.expired_prompt(ui)

    @deprecated('use .expired_prompt.handle directly')
    def handle_expired(self, ui: PromptUI):
        return self.expired_prompt.handle(ui)

    def expired_do_archive(self, ui: PromptUI):
        ui.print('Archiving expired log')
        return self.store

    def expired_do_remove(self, ui: PromptUI):
        os.unlink(self.log_file)
        ui.print(f'// removed {self.log_file}')
        self.__init__()
        return self

    report_file: str = 'report.md' # TODO hoist and wire up to arg

    @property
    def report_date(self) -> datetime.date|None:
        return self.today

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
        return  f'- 🔗 {self.site_name or self.site} 🧩 {self.puzzle_id} {self.report_desc if desc is None else desc}'

    def in_report(self, _ui: PromptUI):
        prefixes = (
            self.report_header(desc=''),
            self.report_note(desc=''),
        )
        with open(self.report_file) as lines:
            return any(
                any(
                    line.startswith(prefix)
                    for prefix in prefixes)
                for line in lines)

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
            rep_day = self.report_date or datetime.datetime.today().date()
            in_today = 0

            for line in lines:
                tokens = PromptUI.Tokens(line)

                if tokens.have(r'#+'):
                    sec_day = tokens.have(r'(?x) ( \d{4} ) - ( \d{2} ) - ( \d{2} )',
                                          then=lambda m: datetime.date(int(m[1]), int(m[2]), int(m[3])))
                    if sec_day == rep_day:
                        print(f'{line}', file=w)
                        in_today = 1
                        continue

                    else:
                        print(f'# {rep_day}', file=w)
                        print('', file=w)
                        print(note, file=w)
                        print('', file=w)
                        print(line, file=w)
                        in_today = 0
                        break

                if line.startswith(note_id):
                    print(note, file=w)
                    break

                if in_today:
                    if in_today == 1 and line.startswith('- '):
                        print(line, file=w)
                        in_today = 2
                    elif in_today == 2 and not line.startswith('- '):
                        print(note, file=w)
                        print(line, file=w)
                        break
                    elif in_today == 1 and not line.startswith('- ') and line.strip():
                        print(note, file=w)
                        print('', file=w)
                        print(line, file=w)
                        break
                    else:
                        print(line, file=w)

                elif line:
                    print(f'# {rep_day}', file=w)
                    print('', file=w)
                    print(note, file=w)
                    if not line:
                        print('', file=w)
                    print(line, file=w)
                    break

            for line in lines:
                if in_today and line.startswith('#'):
                    in_today = 0
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

