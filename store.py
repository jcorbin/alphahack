import argparse
import datetime
import json
import os
import re
import subprocess
import shlex
import zlib
from base64 import b85decode, b85encode
from collections.abc import Generator, Iterable, Sequence
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from dateutil.parser import parse as _parse_datetime
from dateutil.tz import gettz, tzlocal, tzoffset
from typing import Callable, Self, cast, final
from types import TracebackType
from warnings import deprecated

from mdkit import break_sections, replace_sections
from ui import LogTime, Paginator, PromptUI, SeqLister

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
    class Parser:
        def __init__(self):
            self.start: datetime.datetime|None = None
            self.first_t: float = 0.0
            self.last_t: float|None = None
            self.prior: LogSession|None = None

        def elapsed(self):
            if self.last_t is None:
                return datetime.timedelta()
            return datetime.timedelta(seconds=self.last_t - self.first_t)

        def session(self):
            if self.start is None:
                return None
            return LogSession(self.start, self.elapsed())

        def __call__(self, ui: PromptUI, t: float, rest: str):
            try:
                m = re.match(r'''(?x)
                    now :
                    \s+
                    (?P<then> .+ )
                    $''', rest)
                if not m: return False
                self.prior = self.session()
                self.start = None
                self.first_t = t
                try:
                    self.start = parse_datetime(m[1])
                except ValueError:
                    ui.print(f'WARNING: unable to parse prior log start time from {rest!r}')
                return True
            finally:
                self.last_t = t

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

def make_oneshot(
    st: PromptUI.State,
    given_input: Sequence[str] = (),
    keep_going: bool = False, # after given_input exhausted
):
    def init(_ui: PromptUI):
        input_i = 0

        def until_input(ui: PromptUI):
            actual_input = ui.get_input

            def monitor_input(mess: str) -> str:
                nonlocal input_i
                if input_i < len(given_input):
                    sin = given_input[input_i]
                    input_i += 1
                    return sin
                if not keep_going:
                    raise EOFError()
                input_i += 1
                return actual_input(mess)

            nonlocal st
            with ui.trace_entry('until_input') as ent:
                ent.write(f'-> {PromptUI.describe(st)}')

                ui.get_input = monitor_input
                try:
                    nxt = st(ui)
                except PromptUI.Next as n:
                    nxt = n.resolve(ui)
                finally:
                    ui.get_input = actual_input

                if nxt:
                    st = nxt
                    if input_i < len(given_input):
                        ent.write(f'-> until_input w/ {PromptUI.describe(st)}')
                        return until_input

                # NOTE strict equality allows keep_going=True, since input_i will be > len
                if input_i == len(given_input):
                    ent.write(f'-> <STOP>')
                    raise StopIteration

                ent.write(f'-> {PromptUI.describe(st)}')
                return st

        return until_input

    return init

def part_seq[T](sq: Sequence[T], token: T):
    cur: list[T] = []
    for i, t in enumerate(sq):
        if t == token:
            yield tuple(cur)
            cur = []
        else:
            cur.append(t)
        if cur:
            yield tuple(cur)

@final
class Matcher[T]:
    def __init__(self, pat: re.Pattern[str], then: Callable[[T, float, re.Match[str]], None]):
        self.pat = pat
        self.then = then

    def __call__(self, ctx: T, t: float, rest: str):
        match = self.pat.match(rest)
        if match:
            self.then(ctx, t, match)
            return True
        return False

def matcher(pat: str|re.Pattern[str]):
    if isinstance(pat, str):
        pat = re.compile(pat)
    def inner[T](then: Callable[[T, float, re.Match[str]], None]):
        return Matcher(pat, then)
    return inner

class StoredLog:
    @classmethod
    def main(cls):
        import argparse

        ui = PromptUI()
        self = cls()

        parser = argparse.ArgumentParser()
        self.add_args(parser)

        args, rest = parser.parse_known_args()
        ui.traced = cast(bool, args.trace)
        self.from_args(args)
        st: PromptUI.State = self

        while rest and rest[0].startswith('-'):
            if rest[0] == '--':
                _ = rest.pop(0)
            else:
                parser.error(f'unknown option {rest[0]}')
        if rest:
            given_input = tuple(
                shlex.join(sin)
                for sin in part_seq(rest, '--'))
            with ui.trace_entry('main') as ent:
                ent.write(f'w/ {given_input!r}')
            st = make_oneshot(st, given_input)

        with self:
            return ui.run(st)

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
        self.result_text: str = ''

        self.std_prompt: PromptUI.Prompt = PromptUI.Prompt('> ', {
            '/result': self.cmd_result,
            '/site': self.cmd_site_link,
            '/store': self.cmd_store,
        })

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
            'debug': self.do_debug,
        })

    def __enter__(self):
        # TODO log file handling here?
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        # TODO log file handling here?
        pass

    @property
    def expire(self) -> datetime.datetime|None:
        return None

    @property
    def today(self) -> datetime.date|None:
        return None

    def cmd_site_link(self, ui: PromptUI):
        '''
        present puzzle site hyperlink... or "copy" to clipboard
        '''

        # TODO if ui.tokens -> set and log?
        #     site = next(tokens, None)
        #     if site:
        #         self.site = site
        #         ui.log(f'site: {self.site}')

        label = self.site_name or self.site
        url = self.site
        if '://'not in url:
            url = f'https://{url}'

        # TODO maybe factor out a ui.open(url, name) facility?

        try:
            ui.write(f'🔗 ')
            ui.link(url)
            ui.write(f' {label}')
            ui.link('')

            while True:
                with ui.input(' ...') as tokens:
                    nxt = next(tokens, '').lower()
                    if not nxt: return
                    if 'copy'.startswith(nxt):
                        ui.write(f' 📋')
                        ui.copy(url)
                    else:
                        ui.write(f' ?')

        finally:
            ui.fin()

    def startup(self, ui: PromptUI) -> PromptUI.State|None:
        self.cmd_site_link(ui)

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
        # TODO maybe finish like square
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

    def do_debug(self, ui: PromptUI):
        parse = LogParser(
            warn=lambda mess: ui.print(f'! debug parse {mess}'))
        session_parser = LogSession.Parser()
        with open(self.log_file) as r:
            for line in r:
                t, z, rest = parse(line)
                if t is None:
                    ui.print(f'T:{t} Z:{z} ! {rest!r}')
                    continue
                if session_parser(ui, t, rest) and session_parser.prior is not None:
                    ui.print(f'+++ prior session {session_parser.prior}')
                ui.print(f'T:{t} Z:{z} {rest!r}')
            sess = session_parser.session()
            if sess is not None:
                ui.print(f'+++ last session {sess}')

    @property
    def init_log_file(self):
        return self.__class__.log_file

    def finalize(self, ui: PromptUI):
        if self.stored and self.ephemeral:
            return self.cont_rep(ui).restart(
                ui,
                mess='^^^ finalizing after last (stored) session',
                log_file=f'{self.init_log_file}.fin',
                then=self.finalize)

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

    def cmd_result(self, ui: PromptUI):
        '''
        record share result from site
        '''
        ui.print('Provide share result:')
        try:
            self.proc_result(ui, ui.may_paste())
        except ValueError as err:
            ui.print(f'! {err}')

    @matcher(r'''(?x)
        (?: share \s+ )?  # pattern for legacy log lines
        result :
        \s* (?P<json> .* )
        $''')
    def load_result(self, _t: float, m: re.Match[str]):
        dat = cast(object, json.loads(m[1]))
        assert isinstance(dat, str)
        try:
            self.set_result_text(dat)
        except:
            pass

    def set_result_text(self, txt: str):
        self.result_text = txt

    def proc_result(self, ui: PromptUI, text: str) -> None:
        self.set_result_text(text)
        if self.have_result():
            ui.log(f'result: {json.dumps(text)}')

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
            if not self.stl.ephemeral:
                return then

            try:
                with self.stl.log_to(ui):
                    ui.call_state(then)
            except CutoverLogError as cutover:
                with ui.trace_entry('restart <!- cutover') as ent:
                    st = cutover.resolve(self.stl, ui, self.stl)
                    ent.write(f'-> {PromptUI.describe(st)}')
                    return st
            except EOFError:
                return

    def load(self, ui: PromptUI, lines: Iterable[str]) -> Generator[tuple[float, str]]:
        rez = zlib.compressobj()
        def flushit(b: bytes):
            _ = rez.compress(b)
            _ = rez.flush(zlib.Z_SYNC_FLUSH)
        parse = LogParser(
            rez=flushit,
            warn=lambda mess: ui.print(f'! parse #{no}: {mess}'))
        session_parser = LogSession.Parser()

        def match_session(self: Self, t: float, rest: str):
            if not t and not rest:
                sess = session_parser.session()
                if sess is not None:
                    self.sessions.append(sess)
                return True
            if session_parser(ui, t, rest):
                if session_parser.prior is not None:
                    self.sessions.append(session_parser.prior)
                if self.start is None:
                    self.start = session_parser.start
                if self.log_start is None:
                    self.log_start = session_parser.start
                return True
            return False

        matchers: list[Callable[[Self, float, str], bool]] = []
        matchers.append(match_session)

        # TODO matcher to rehydrate dev clipboard
        # self.log(f'pasted: {json.dumps({
        #     "subject": subject,
        #     "method": method,
        #     "content": content,
        # })}')

        for prop in dir(self):
            if prop.startswith('_'): continue
            val = cast(object, getattr(self.__class__, prop, None))
            if isinstance(val, Matcher):
                matchers.append(cast(Matcher[Self], val))

        mrs = tuple(matchers)
        for no, line in enumerate(lines, 1):
            with ui.exc_print(lambda: f'while loading L{no} {line!r}'):
                t, _z, rest = parse(line)
                if t is None:
                    yield 0, line
                elif not any(mr(self, t, rest) for mr in mrs):
                    yield t, rest
        for mr in mrs:
            _ = mr(self, 0, '')
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
        if self.loaded and log_file == self.log_file:
            with ui.trace_entry('set_log_file noop') as ent:
                ent.write(f'ephemeral:{self.ephemeral}')
            return
        if not self.ephemeral:
            with ui.trace_entry('set_log_file not-ephemeral') as ent:
                raise RuntimeError('set_log_file must be ephemeral (pre load and append/log_to')
        if self.loaded:
            self.__init__()
        if log_file and os.path.exists(log_file):
            with open(log_file, 'r') as f:
                for _ in self.load(ui, f):
                    # TODO or do we match pasted log here?
                    pass
        self.loaded = True
        self.log_file = log_file

    def find_prior_log(self, ui: PromptUI, puzzle_id: str|None=None) -> str|None:
        if puzzle_id is None:
            puzzle_id = next(ui.tokens, '')

        sd = self.store_subdir
        if not sd:
            ui.print(f'! no store directory available to look for {puzzle_id!r}')
            raise StopIteration

        ents = tuple(sorted((
                ent
                for ent in os.scandir(sd)
                if ent.is_file()
            ),
            key=lambda ent: ent.stat().st_mtime,
            reverse=True))

        def try_token(puzzle_id: str):
            for ent in ents:
                if ent.name == puzzle_id:
                    return ent
            mayhaps = tuple(
                ent
                for ent in ents
                if puzzle_id in ent.name)
            if len(mayhaps) == 1:
                return mayhaps[0]
            elif len(mayhaps) > 1:
                mayname = tuple(ent.name for ent in mayhaps)
                ui.print(f'! ambiguous substring, mayhaps: {mayname!r}')

        choice = ents[0] if ents else None

        if puzzle_id == '*':
            ls = SeqLister(
                f'{sd}/',
                ents,
                show=lambda ent: f'{ent.name}',
                perse=lambda ui: try_token(next(ui.tokens)) if ui.tokens else None,
            )
            try:
                ui.call_state(Paginator(ls))
            except StopIteration:
                pass
            choice = ls.choice

        elif puzzle_id:
            choice = try_token(puzzle_id)

        if choice is None:
            ui.print(
                f'! unable to find prior log {puzzle_id!r} in {sd}'
                if puzzle_id else
                f'! no prior logs in {sd}')
            return None
        return choice.path

    def __call__(self, ui: PromptUI) -> PromptUI.State|None:
        spec_match = re.fullmatch(r'''(?x)
                                  (?P<puzzle_id> .*? )
                                  :
                                  (?P<action> .* )
                                  ''', self.log_file)
        if spec_match:
            puzzle_id = str(spec_match[1])
            action = str(spec_match[2])
            found_log_file = self.find_prior_log(ui, puzzle_id)
            if not found_log_file:
                raise StopIteration

            ui.print(f'Found log file {found_log_file}')
            self.log_file = found_log_file

            if action:
                ui.tokens = ui.Tokens(action)

        if self.log_file and not self.loaded:
            self.load_log(ui)
            return self

        if self.stored:
            return self.review_prompt

        if self.is_expired:
            ui.print(f'! expired puzzle log started {self.start:{self.dt_fmt}}, but next puzzle expected at {self.expire:{self.dt_fmt}}')
            return self.expired_prompt

        return self.handle

    def handle(self, ui: PromptUI):
        if not (self.run_done and self.have_result()):
            return self.call_state(ui, self.run)
        return self.store

    def call_state(self,
                   ui: PromptUI,
                   st: PromptUI.State,
                   then: PromptUI.State|None = None):
        try:
            with self.log_to(ui):
                ui.call_state(st)
        except CutoverLogError as cutover:
            if not self.ephemeral:
                raise
            with ui.trace_entry('call_state <!- cutover') as ent:
                if not self.ephemeral:
                    # TODO is it okay to loose then?
                    ent.write(f'-!> not ephemeral yet, re-raise')
                    if then is not None:
                        ent.write(f'lost {PromptUI.describe(then)}')
                    raise
                st = cutover.resolve(self, ui, then or PromptUI.then_eof)
                ent.write(f'-> {PromptUI.describe(st)}')
                return st

    def interact(self, ui: PromptUI, st: PromptUI.State):
        while True:
            try:
                return self.call_state(ui, st)
            except (EOFError, KeyboardInterrupt):
                raise StopIteration

    @matcher(r'''(?x)
        site :
        \s+
        (?P<token> [^\s]+ )
        \s* ( .* )
        $''')
    def load_site(self, _t: float, m: re.Match[str]):
        assert m[2] == ''
        self.site = m[1]

    @matcher(r'''(?x)
        puzzle_id :
        \s+
        (?P<token> [^\s]+ )
        \s* ( .* )
        $''')
    def load_puzzle_id(self, _t: float, m: re.Match[str]):
        assert m[2] == ''
        self.puzzle_id = m[1]

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
            if log_file is not None and log_file != self.log_file:
                raise RuntimeError(f'already logging to {self.log_file} want {log_file}')
            with ui.trace_entry('redundant store.log_to') as ent:
                how = 'implicit' if log_file is None else 'explicit'
                ent.write(f'to {self.log_file!r} {how}')
            yield
            return

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
                        with ui.trace_entry('starting ui log') as ent:
                            how = 'implicit' if log_file is None else 'explicit'
                            ent.write(f'to {self.log_file!r} {how}')
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

    def cmd_store(self, _ui: PromptUI):
        '''
        store log and enter review mode
        '''
        return self.store

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

        try:
            self.do_store(ui, date)
        except CutoverLogError as cutover:
            then: list[PromptUI.State] = [
                self.do_report,
                PromptUI.then_eof if self.run_done
                else self.review_do_cont
            ]
            with ui.trace_entry('store <!- cutover') as ent:
                for st in then:
                    ent.fin()
                    ent.write(f'  cutover.next.append({PromptUI.describe(st)})\n')
                    cutover.next.append(st)
            raise
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

    @property
    def note_slug(self):
        return tuple(self.slug(link=False))

    @property
    def header_slug(self):
        return tuple(self.slug(link=True))

    def slug(self, link: bool = True):
        site = self.site or self.default_site

        if self.site_name:
            yield f'[{self.site_name}]({site})' if link else f'🔗 {self.site_name}'
        else:
            yield site if link else f'🔗 {site}'

        if self.puzzle_id:
            yield f'🧩 {self.puzzle_id}'

    def report_header(self, desc: str|None = None) -> str:
        return f'# {" ".join(self.header_slug)} {self.report_desc if desc is None else desc}'

    def report_note(self, desc: str|None = None) -> str:
        return  f'- {" ".join(self.note_slug)} {self.report_desc if desc is None else desc}'

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

        # TODO factor def rep_lines(lines: Iterable[str]) -> Generator[str] out of below

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
    def __init__(self, log_file: str, nxt: PromptUI.State|None=None):
        super().__init__(f'cutover to {log_file}')
        self.log_file = log_file
        self.next: list[PromptUI.State] = []
        if nxt:
            self.next.append(nxt)

    def resolve(self, stored: StoredLog, ui: PromptUI, then: PromptUI.State):
        with ui.trace_entry('cutover.resolve') as ent:
            if stored.log_file != self.log_file:
                ent.fin()
                ent.write(f'  set_log_file {self.log_file}')
                stored.set_log_file(ui, self.log_file)

            if self.next:
                ent.fin()
                ent.write(f'  cutover.next.append({PromptUI.describe(then)})\n')
                self.next.append(then)
                return self

            else:
                ent.write(f'-> {PromptUI.describe(then)}')
                return then

    def __call__(self, ui: PromptUI):
        with ui.trace_entry('cutover') as ent:
            if not self.next:
                ent.write('-> <STOP>')
                raise StopIteration
            nx = self.next.pop(0)
            if not self.next:
                ent.write(f'-> {PromptUI.describe(nx)}')
                return nx
            ent.write(f'( {PromptUI.describe(nx)}')
            try:
                mx = nx(ui)
                if mx:
                    ent.write(f'-> {PromptUI.describe(mx)}')
                    self.next.insert(0, mx)
            finally:
                ent.write(f')')

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

