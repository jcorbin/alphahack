#!/usr/bin/env python

import argparse
import datetime
import json
import math
import ollama
import re
import subprocess
from bs4 import BeautifulSoup
from collections import Counter
from collections.abc import Generator, Iterable, Sequence
from dataclasses import dataclass, asdict
from dateutil.tz import gettz
from typing import assert_never, cast, final, override, Any, Callable, Literal
from urllib.parse import urlparse

from store import StoredLog, atomic_file, break_sections, git_txn, replace_sections
from ui import PromptUI

def partition_any(s: str, chars: str):
    for char in chars:
        i = s.find(char)
        if i >= 0:
            return s[:i], s[i], s[i+1:]
    return  s, '', ''

def spliterate(s: str, chars: str, trim: bool = False):
    fin = ''
    while s:
        part, fin, s = partition_any(s, chars)
        if trim and not part: continue
        yield part
        break
    while s:
        part, fin, s = partition_any(s, chars)
        yield part
    if not trim and fin: yield ''

def wraplines(at: int, lines: Iterable[str]):
    for line in lines:
        while len(line) > at:
            i = line.rfind(' ', 0, at)
            if i < 0: i = at
            yield line[:i]
            line = line[i:].lstrip()
        yield line

StrSink = Generator[None, str, None]

FenceWanted = tuple[str, str, StrSink] # start_line, end_line, sink

WantFence = Callable[[int, str], FenceWanted|None]

def fenceit(it: Iterable[str], start: str = '```', end: str = '```') -> Generator[str]:
    yield start
    yield from it
    yield end

tick3_fence = re.compile(r'(?x) ( ``` ) \s* ( .* ) $')

def capture_fences(lines: Iterable[str],
                   wanted: WantFence,
                   pattern: re.Pattern[str] = tick3_fence):

    index = 0
    while True:
        for line in lines:
            match = pattern.match(line)
            if match: break
            yield line
        else: return

        fence, suffix = match.groups()
        want = wanted(index, suffix)
        if want:
            line, end_line, sink = want
            next(sink)
            yield line

            for line in lines:
                if line == fence:
                    sink.close()
                    yield end_line
                    break
                sink.send(line)
                yield line

        else:
            for line in lines:
                yield line
                if line == fence: break

        index += 1

def prog_mark(prog: int|None):
    if prog is None: return ''
    if prog > 1000: return '🚀'
    if prog == 1000: return '🥳'
    if prog >= 999: return '😱'
    if prog >= 990: return '🔥'
    if prog >= 900: return '🥵'
    if prog >= 1: return '😎'

prog_min, prog_max = 1, 1000

def score_mark(score: float):
    if score < 0: return '🧊'
    if score < -100.00: return '☠️'
    return '🥶'

score_min, score_max = -100.00, 100.00

def mark(score: float, prog: int|None = None):
    # TODO use parsed / learnt tiers of prog is None
    return prog_mark(prog) or score_mark(score)

Tier = Literal['🧊']|Literal['🥶']|Literal['😎']|Literal['🥵']|Literal['🔥']|Literal['😱']|Literal['🥳']
Mark = Literal['🚀']|Literal['☠️']|Tier
Scale = dict[Tier, float]

tiers: list[Tier] = [
    '🧊',
    '🥶',
    '😎',
    '🥵',
    '🔥',
    '😱',
    '🥳',
]

scale_fixed: dict[Tier, float] = {}
scale_fixed['🧊'] = -100.0
scale_fixed['🥶'] =    0.0
scale_fixed['🥳'] =  100.0

TierCounts = tuple[
    int,
    int,
    int,
    int,
    int,
    int,
    int,
]

digits = [
    '0️⃣',
    '1️⃣',
    '2️⃣',
    '3️⃣',
    '4️⃣',
    '5️⃣',
    '6️⃣',
    '7️⃣',
    '8️⃣',
    '9️⃣',
]

def parse_digits(s: str):
    while s:
        for i, digit in enumerate(digits):
            if s.startswith(digit):
                yield i
                s = s[len(digit):]
                break
        else:
            raise ValueError(f'invalid digit string {s!r}')

def parse_digit_int(s: str, default: int = 0):
    nn: int|None = None
    for n in parse_digits(s):
        nn = n if nn is None else 10*nn + n
    return default if nn is None else nn

def get_olm_models(client: ollama.Client) -> Generator[str]:
    models = client.list()['models'] # pyright: ignore[reportAny]
    assert isinstance(models, list)
    for x in cast(list[Any], models): # pyright: ignore[reportAny]
        assert isinstance(x, dict)
        x = cast(dict[str, Any], x)
        name = x.get('name')
        assert isinstance(name, str)
        yield name

def olm_find_model(client: ollama.Client, name: str):
    try:
        return max(n for n in get_olm_models(client) if n.startswith(name))
    except ValueError:
        raise RuntimeError(f'Unavailable --ollama-model {name!r} ; available models: {' '.join(sorted(get_olm_models(client)))}')

word_ref_pattern = re.compile(r'(?x) \# ( \d+ ) | \$ ( [TtBb]? ) ( -? \d+ )')
WordRef = Literal['$', '#']
WordDeref = Callable[[WordRef, int], str]

def word_refs(s: str) -> Generator[tuple[WordRef, int]]:
    for match in word_ref_pattern.finditer(s):
        yield from word_match_refs(match)

def unroll_refs(s: str) -> Generator[str]:
    for match in word_ref_pattern.finditer(s):
        yield from unroll_word_match(match)

def unroll_word_match(match: re.Match[str]):
    nth, vartb, varn = match.groups()
    if nth:
        yield f'#{nth}'
    elif vartb:
        if vartb.lower() == 't':
            for n in range(1, int(varn)+1):
                yield f'${n}'
        elif vartb.lower() == 'b':
            for n in range(int(varn), 0, -1):
                yield f'${-n}'
    elif varn:
        yield f'${varn}'

def word_match_refs(match: re.Match[str]):
    nth, vartb, varn = match.groups()
    if nth:
        yield '#', int(nth)
    elif vartb:
        if vartb.lower() == 't':
            for n in range(1, int(varn)+1):
                yield '$', n
        elif vartb.lower() == 'b':
            for n in range(int(varn), 0, -1):
                yield '$', -n
    elif varn:
        yield '$', int(varn)

def expand_word_refs(s: str, deref: WordDeref):
    def repl(match: re.Match[str]):
        try:
            parts = [deref(k, n) for k, n in word_match_refs(match)]
        except Exception as e:
            raise ValueError(f'failed to expand {match.group(0)}: {e}')

        sep = ', '
        join = 'and' # TODO optional from pattern

        if not parts:
            return ''
        elif len(parts) == 1:
            return parts[0]
        elif len(parts) == 2:
            return f'{parts[0]} {join} {parts[1]}'
        else:
            return f'{sep.join(parts[:-1])}{sep}{join} {parts[-1]}'

    return word_ref_pattern.sub(repl, s)

def count_tokens(s: str):
    return sum(1 for _ in re.finditer(r'[^\s]+', s))

@final
@dataclass
class ChatPrompt:
    prompt: str
    vars: tuple[int, ...] = tuple()
    ords: tuple[int, ...] = tuple()

    @classmethod
    def from_prompt(cls, prompt: str):
        vars: list[int] = []
        ords: list[int] = []
        for k, n in word_refs(prompt):
            if k == '$': vars.append(n)
            elif k == '#': ords.append(n)
        return cls(prompt, tuple(vars), tuple(ords))

    @classmethod
    def from_dict(cls, dat: dict[str, Any]):
        prompt = dat['prompt'] # pyright: ignore[reportAny]
        assert isinstance(prompt, str)

        vars: list[Any] = dat.get('vars') or []
        assert isinstance(vars, list)
        assert all(isinstance(_, int) for _ in vars) # pyright: ignore[reportAny]

        ords: list[Any] = dat.get('ords') or []
        assert isinstance(ords, list)
        assert all(isinstance(_, int) for _ in ords) # pyright: ignore[reportAny]

        return cls(prompt, tuple(vars), tuple(ords))

    def expand(self, deref: WordDeref):
        return expand_word_refs(self.prompt, deref)

    def refs(self) -> Generator[tuple[WordRef, int]]:
        for n in self.vars: yield '$', n
        for n in self.ords: yield '#', n

def word_list_parts(words: Sequence[str], sep: str, fin: str):
    n = len(words)
    for i, word in enumerate(words):
        if n > 2 and i > 0: yield sep
        if n > 1 and i == n-1: yield f' {fin}'
        yield f' {word}'

@final
@dataclass
class ChatStats:
    token_count: int
    user_count: int
    assistant_count: int

@final
class Search(StoredLog):
    log_file: str = 'cemantle.log'
    default_site: str = 'cemantle.certitudes.org'
    default_lang: str = ''
    default_chat_model: str = 'llama'

    pub_at = datetime.time(hour=0)
    pub_tzname = 'US/Pacific'

    @override
    def add_args(self, parser: argparse.ArgumentParser):
        super().add_args(parser)
        _ = parser.add_argument('--lang', default=self.lang)
        _ = parser.add_argument('--tz', default=self.pub_tzname)
        _ = parser.add_argument('--model', default=self.default_chat_model)

    @override
    def from_args(self, args: argparse.Namespace):
        super().from_args(args)
        lang = cast(str, args.lang)
        self.lang = self.default_lang = lang
        self.pub_tzname = cast(str, args.tz)
        self.default_chat_model = cast(str, args.model)

    def __init__(self):
        super().__init__()

        self.lang: str = self.default_lang
        self.scale: Scale = dict(scale_fixed)
        self.prog_at: float|None = None

        self.top_n: int = 3
        self.bot_n: int = 3

        self.attempt: int = 0
        self.word: list[str] = []
        self.score: list[float] = []
        self.prog: dict[int, int] = dict()
        self.index: list[int] = []

        self.wordbad: set[str] = set()
        self.wordgood: dict[str, int] = dict()

        self.result_text: str = ''
        self.result: Search.Result|None = None

        self.llm_client = ollama.Client()
        self.llm_model: str = self.default_chat_model

        self.chat: list[ollama.Message] = []
        self.chat_role_counts: Counter[str] = Counter()
        self.last_chat_prompt: ChatPrompt|None = None
        self.last_chat_basis: set[str] = set()

    @property
    def pub_tz(self):
        if not self.pub_tzname:
            raise RuntimeError('no publish timezone set')
        tz = gettz(self.pub_tzname)
        if not tz:
            raise RuntimeError(f'unable to load publish timezone {self.pub_tzname}')
        return tz

    def next_pub(self, t: datetime.datetime):
        # we want the next publish time in **our** (local) timezone

        # publish time in **their** (puzzle) timezone 
        nt = self.pub_at.replace(tzinfo=self.pub_tz)

        # publish time for **their** timezone notion of "that day"
        nt = t.combine(t.date(), nt, tzinfo=nt.tzinfo)

        # **our** notion of when **their** day was/is
        nt = nt.astimezone(t.tzinfo)

        # ensure that we're in **our** notion of tomorrow
        # i.e. *their* notion of "that day" may have been **our** yester
        d_seconds = max(0, (t - nt).total_seconds())
        d_days = d_seconds / 60 / 60 / 24
        nt += datetime.timedelta(days=math.ceil(d_days))

        return nt

    @property
    def pub(self):
        if self.start is None: return None
        return self.next_pub(self.start - datetime.timedelta(days=1))

    @property
    @override
    def expire(self):
        return None if self.start is None else self.next_pub(self.start)

    @property
    @override
    def today(self):
        d = self.pub
        return None if d is None else d.date()

    @final
    @dataclass
    class Result:
        puzzle_id: int
        guesses: int
        link: str
        site: str
        counts: TierCounts

        def describe(self) -> Generator[str]:
            yield f'🔗 {self.site or self.link}'
            yield f'🧩 {self.puzzle_id}'
            yield f'🤔 {self.guesses} guesses'
            for part in self.count_parts():
                yield f'    {part}'

        def count_parts(self):
            cw = max(len(str(c)) for c in self.counts)
            for i, count in enumerate(reversed(self.counts), start=1):
                if count > 0:
                    yield f'{tiers[-i]} {count:>{cw}}'

        @classmethod
        def parse(cls, s: str):
            puzzle_id: int|None = None
            guesses: int = 0
            link: str = ''
            counts = [0 for _ in tiers]

            for line in s.splitlines():
                match = re.match(r'''(?x)
                    I \s+ found
                    \s+ \#cemantle
                    \s+ \# (?P<num> \d+ )
                    \s+ in
                    \s+ (?P<guesses> \d+ ) \s+ guesses \s* !
                ''', line) or re.match(r'''(?x)
                    J'ai \s+ trouvé
                    \s+ \#cemantix
                    \s+ nº (?P<num> \d+ )
                    \s+ en
                    \s+ (?P<guesses> \d+ )
                    \s+ coups
                    \s* \!
                ''', line)
                if match:
                    ns, gs = match.groups()
                    puzzle_id = int(ns)
                    guesses = int(gs)
                    continue

                if line.startswith('http') and not link:
                    link = line
                    continue

                found = False
                for i, tier in enumerate(tiers):
                    if line.startswith(tier):
                        found = True
                        cs = line.lstrip(tier).strip()
                        counts[i] = parse_digit_int(cs, default=1)
                        break
                if found: continue

            if puzzle_id is None:
                raise ValueError('missing puzzle #id')

            if sum(counts) != guesses:
                raise ValueError('tier count sum doesn\'t match guess count')

            site = urlparse(link).hostname or ''

            return cls(puzzle_id, guesses, link, site, cast(TierCounts, tuple(counts)))

    @property
    @override
    def run_done(self):
        return self.result is not None

    @override
    def startup(self, ui: PromptUI):
        if not self.puzzle_id:
            ui.br()
            self.do_site(ui)
            self.do_lang(ui)
            self.do_puzzle(ui)
            if not self.puzzle_id: return

        return self.startup_scale

    def startup_scale(self, ui: PromptUI):
        ui.br()
        if len(self.scale) < len(tiers):
            ui.print(f'Populating temp scale {len(self.scale)} / {len(tiers)}')
            self.scale.update(scale_fixed)

            for i in range(2, len(tiers)-1):
                tier = tiers[i]
                if tier in self.scale: continue

                prior_tier = tiers[i-1]
                next_tier: Tier = '🥳'
                for j in range(len(tiers)-2, i, -1):
                    if tiers[j] in self.scale:
                        next_tier = tiers[j]

                prior_temp = self.scale[prior_tier]
                next_temp = self.scale[next_tier]

                token = ui.input(f'{tier} °C ? ').head
                if not token:
                    confirm = ui.input(f'skip temp scale entry? ').head
                    if confirm.lower().startswith('y'):
                        return self.orient

                try:
                    temp = float(token)
                except ValueError:
                    ui.print('! must be a float')
                    return

                if temp <= prior_temp:
                    ui.print(f'! must be over {prior_tier} {prior_temp:.2f}°C')
                    return

                if temp >= next_temp:
                    ui.print(f'! must be under {next_tier} {next_temp:.2f}°C')
                    return

                ui.log(f'scale: {tier} {temp:.2f} °C')
                self.scale[tier] = temp
                if self.prog_at is None and tier == '😎':
                    self.prog_at = temp

                return

            ui.print(f'WARNING: incomplete temp scale ; use /scale to inspect and fix')

        if self.prog_at is None:
            self.prog_at = self.scale.get('😎')

        return self.orient

    @override
    def hist_body(self, ui: PromptUI):
        return break_sections(
            fenceit(self.describe_result(ui)),
            self.info())

    @override
    def review(self, ui: PromptUI):
        if self.result is None: return self.orient
        self.show_result(ui)
        return self.do_cmd

    @override
    def load(self, ui: PromptUI, lines: Iterable[str]):
        for t, rest in super().load(ui, lines):
            match = re.match(r'''(?x)
                lang :
                \s+
                (?P<token> [^\s]+ )
                \s* ( .* )
                $''', rest)
            if match:
                token, rest = match.groups()
                assert rest == ''
                self.lang = token
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

            match = re.match(r'''(?x)
                scale :
                \s+ (?P<tier> 🧊|🥶|😎|🥵|🔥|😱|🥳 )
                \s+ (?P<temp> [^\s]+ )
                \s* °C
                \s* ( .* )
                $''', rest)
            if match:
                stier, stemp, rest = match.groups()
                temp = float(stemp)
                assert rest == ''

                tier = cast(Tier, stier)
                j = tiers.index(tier)
                if tier in scale_fixed:
                    if temp != scale_fixed[tier]:
                        ui.print(f'WARNING: ignoring incorrect scale fixed point {tier} {temp:.2f} °C')
                    # otherwise it's just a bit redundant, idk
                    continue

                i = j - 1
                k = j + 1
                while k < len(tiers)-1:
                    if tiers[k] in self.scale: break
                    k += 1

                prior_tier = tiers[i]
                next_tier = tiers[k]
                prior_temp = self.scale[prior_tier]
                next_temp = self.scale[next_tier]
                if not (prior_temp < temp < next_temp):
                    ui.print(f'WARNING: ignoring invalid scale {tier} {temp:.2f}°C ; must be in range {prior_tier} {prior_temp:.2f}°C {next_tier} {next_temp:.2f}°C')
                    continue

                self.scale[tier] = temp
                if self.prog_at is None and tier == '😎':
                    self.prog_at = temp

                continue

            match = re.match(r'''(?x)
                fix \s+ attempt_ (?P<attempt> \d+ ) :
                \s* (?P<rest> .* )
                $''', rest)
            if match:
                si, rest = match.groups()
                i = int(si)
                score: float|None = None
                prog: int|None = None
                for match in re.finditer(r'''(?x)
                    \s* (?P<name> score | prog ) : \s* (?P<value> [^\s]+ )
                ''', rest):
                    name, value = match.groups()
                    if name == 'score': score = float(value)
                    if name == 'prog': prog = int(value)
                assert self.fix(ui, i, score, prog)
                continue

            match = re.match(r'''(?x)
                attempt_ (?P<attempt> \d+ ) :
                \s+
                " (?P<word> .+? ) "
                \s+
                score : (?P<score> -? \d+(?:\.\d*)? )
                \s+
                prog : (?P<prog> None | \d+ )
                \s* (?P<rest> .* )
                $''', rest)
            if match:
                si, word, ss, ps, rest = match.groups()
                i = int(si)
                score = float(ss)
                prog = None if ps == 'None' else int(ps)
                assert i == self.attempt
                assert rest == ''
                assert self.record(ui, word, score, prog) == i
                continue

            match = re.match(r'''(?x)
                reject :
                \s+
                " (?P<word> .+? ) "
                \s* (?P<rest> .* )
                $''', rest)
            if match:
                word, rest = match.groups()
                assert rest == ''
                self.reject(ui, word)
                continue

            match = re.match(r'''(?x)
                chat_prompt : \s* (?P<mess> .+ )
                $''', rest)
            if match:
                mess, = match.groups()
                if mess == '_':
                    assert self.last_chat_prompt is not None
                    _ = self.regen_chat_prompt(ui)
                else:
                    _ = self.set_chat_prompt(ui,
                        ChatPrompt.from_dict(json.loads(mess))) # pyright: ignore[reportAny]
                continue

            match = re.match(r'''(?x)
                session : \s* (?P<mess> .+ )
                $''', rest)
            if match:
                mess_json, = match.groups()
                mess = json.loads(mess_json) # pyright: ignore[reportAny]
                mess = cast(ollama.Message, mess) # TODO validate
                self.chat_append(ui, mess)
                continue

            match = re.match(r'''(?x)
                session \s+ model :
                \s*
                (?P<model> [^\s]+ )
                \s* (?P<rest> .* )
                $''', rest)
            if match:
                model, rest = match.groups()
                assert rest == ''
                self.llm_model = model
                continue

            match = re.match(r'''(?x)
                session \s+ clear
                \s* (?P<rest> .* )
                $''', rest)
            if match:
                rest, = match.groups()
                assert rest == ''
                self.chat_clear(ui)
                continue

            match = re.match(r'''(?x)
                share \s+ result:
                \s+ (?P<result> .* )
                $''', rest)
            if match:
                srej, = match.groups()
                rej = json.loads(srej) # pyright: ignore[reportAny]
                if not isinstance(rej, str): continue
                self.result_text = rej
                try:
                    res = self.Result.parse(self.result_text)
                except ValueError:
                    self.result = None
                    continue
                self.result = res
                if res.site: self.site = res.site
                if not self.puzzle_id:
                    self.puzzle_id = f'#{res.puzzle_id}'
                continue

            yield t, rest

    def describe_word(self, i: int, ix: int|None = None, word: str|None = None):
        if word is not None:
            assert self.word[i] == word
        else:
            word = self.word[i]

        if ix is None:
            ix = self.index.index(i)
            if ix < 0: ix = None
        else:
            assert self.index[ix] == i

        score = self.score[i]
        prog = self.prog.get(i)
        progs = '' if prog is None else f'{prog:>5}‰'
        var = '<no-index>' if ix is None else f'${ix+1}'
        nth = f'#{i+1}'

        ww = max(len(word) for word in self.word)
        iw = len(str(len(self.word)))+1
        return f'{var:>{iw}} {nth:>{iw}} {word:{ww}} {score:>7.2f}°C {mark(score, prog)}{progs}'

    @property
    def found(self):
        if not self.index: return None
        i = self.index[0]
        score = self.score[i]
        if score < score_max: return None
        prog = self.prog.get(i)
        if not prog or prog < prog_max: return None
        return i

    @property
    def min_prog(self):
        i, prog = min(self.prog.items(), key = lambda iprog: iprog[1])
        return i, prog

    @property
    def max_prog(self):
        i, prog = max(self.prog.items(), key = lambda iprog: iprog[1])
        return i, prog

    def top_bot_index(self, top: int|None = None, bot: int|None = None):
        if top is None: top = self.top_n
        if bot is None: bot = self.bot_n
        ni = len(self.index)
        ti = min(ni-1, top-1)
        for ix in range(ti+1):
            yield True, ix
        bi = max(ti+1, len(self.index) - bot)
        if bi > 0 and bi < ni:
            for ix in range(bi, ni):
                yield False, ix

    def show_prog(self, ui: PromptUI):
        lines = self.prog_lines(limit=max(len(tiers), math.ceil(ui.screen_lines*4/5)))
        for line in lines:
            ui.br()
            ui.print(line)
            break
        for line in lines:
            ui.print(line)

    def prog_lines(self, limit: int):
        iw = len(str(len(self.word))) + 1
        for ix, i, desc in self.describe_prog(limit = limit):
            var = '<no-index>' if ix < 0 else f'${ix+1}'
            nth = f'#{i+1}'
            yield f'    {var:>{iw}} {nth:>{iw}} {desc}'

    def describe_prog(self, limit: int = 10):
        rem = [sum(1 for _ in words())-1 for _, words in self.tier_words()]
        counts = [1 for _ in rem]

        while sum(counts) < limit and sum(rem) > 0:
            for i, r in enumerate(rem):
                if r > 0:
                    n = min(limit - sum(counts), r)
                    rem[i] -= n
                    counts[i] += n
                    break

        if not len(self.word): return
        ww = max(len(word) for word in self.word)
        ix = 0
        for lim, (tier, words) in zip(counts, self.tier_words()):
            for word in words():
                if lim > 0:
                    i = self.index[ix]
                    prog = self.prog.get(i)
                    score = self.score[i]
                    word = self.word[i]
                    ps = '' if prog is None else f' {prog:>4}‰'
                    yield ix, i, f'{word:{ww}} {score:>7.2f}°C {tier}{ps}'
                    lim -= 1
                ix += 1

    def show_tiers(self, ui: PromptUI):
        cw = len(str(self.attempt))
        for tier, words in self.tier_words():
            it = words()
            parts: list[str] = []
            n = 0
            for c, word in enumerate(it):
                if c > 2:
                    parts.append('...')
                    break
                n = c+1
                parts.append(word)
            n = sum((1 for _ in it), start=n)
            ui.print(f'    {tier} {n:>{cw}} {' '.join(parts)}')

    def tier_words(self) -> Generator[tuple[Mark, Callable[[], Generator[str]]]]:
        prior = ''
        for ix, i in enumerate(self.index):
            mrk = mark(self.score[i], self.prog.get(i))
            if mrk == prior: continue
            prior = mrk
            j = ix
            mk = mrk
            def rest():
                for k in range(j, len(self.index)):
                    i = self.index[k]
                    if mark(self.score[i], self.prog.get(i)) != mk: break
                    yield self.word[i]
            yield mrk, rest

    def show_vars(self, ui: PromptUI):
        if not len(self.index):
            return

        # TODO more prog tier transition points of interest

        self.show_tbix(ui, self.top_bot_index())

    def show_tbix(self, ui: PromptUI, tbix: Iterable[tuple[bool, int]]):
        top_n = 0
        bot_n = 0
        index: list[int] = []
        for tb, ix in tbix:
            index.append(ix)
            if tb: top_n += 1
            else: bot_n += 1

        ui.br()
        if top_n > 0 and bot_n > 0: ui.print(f'Top {top_n} / Bottom {bot_n} words:')
        elif top_n > 0: ui.print(f'Top {top_n} words:')
        elif bot_n > 0: ui.print(f'Bottom {bot_n} words:')
        for ix in index:
            ui.print(f'    {self.describe_word(self.index[ix], ix=ix)}')

    def info(self):
        yield f'🤔 {self.attempt} attempts'
        yield f'📜 {len(self.sessions)} sessions'

        role_counts = self.chat_role_counts
        user = role_counts.get("user", 0)
        asst = role_counts.get("assistant", 0)
        if user: yield f'⁉️ {user} chat prompts'
        if asst: yield f'🤖 {asst} chat replies'

    def meta(self):
        if self.today is not None: yield f'📆 {self.today:%Y-%m-%d}'
        if self.site: yield f'🔗 {self.site}'
        if self.puzzle_id: yield f'🧩 {self.puzzle_id}'
        if self.lang: yield f'🌎 {self.lang}'

    def describe_result(self, ui: PromptUI) -> Generator[str]:
        if self.result:
            yield from self.result.describe()
        elif self.result_text:
            yield from spliterate(self.result_text, '\n', trim=True)
        else:
            yield '😦 No result'
            for ix, i, desc in self.describe_prog():
                var = '<no-index>' if ix < 0 else f'${ix+1}'
                nth = f'#{i+1}'
                yield f'    {var} {nth} {desc}'
        elapsed = self.elapsed + datetime.timedelta(seconds=ui.time.now)
        yield f'⏱️ {elapsed}'

    def tier_count_parts(self):
        cw = len(str(self.attempt))
        for tier, words in self.tier_words():
            n = sum(1 for _ in words())
            yield f'{tier} {n:>{cw}}'

    def do_cmd(self, ui: PromptUI):
        cmds: dict[str, PromptUI.State] = {
            # TODO proper help command ; reuse for '?' token
            # TODO add '/' prefix here ; generalize dispatch

            'prog': self.show_prog,
            'tiers': self.show_tiers,
            'vars': self.show_vars,

            'site': self.do_site,
            'lang': self.do_lang,
            'puzzle': self.do_puzzle,
            'scale': self.do_scale,
            'result': self.show_result,
            'report': self.do_report,
            'yester': self.do_yester,

            'clear': self.chat_clear,
            'extract': self.chat_extract,
            'model': self.chat_model,
            'last': self.chat_last,
        }

        token = ui.head_or('> ')

        if token == '?' or token == '/?':
            for cmd in sorted(cmds):
                ui.print(f'    /{cmd}')
            return

        if not token.startswith('/'): return

        tok = token[1:].lower()
        comp = [cmd for cmd in cmds if cmd.startswith(tok)]
        if not comp:
            ui.print(f'! unknown command {token}')
            return

        if len(comp) > 1:
            comp = sorted(f'/{cmd}' for cmd in comp)
            ui.print(f'! ambiguous command {token}; clarify: {' '.join(comp)}')
            return

        _ = ui.tokens.next()
        return cmds[comp[0]](ui)

    def do_site(self, ui: PromptUI):
        token = ui.input(f'🔗 {self.site} ? ').head
        if token:
            self.site = token
        ui.log(f'site: {self.site}')

    def do_lang(self, ui: PromptUI):
        token = ui.input(f'🌎 {self.lang} ? ').head
        if token:
            self.lang = token
        ui.log(f'lang: {self.lang}')

    def do_puzzle(self, ui: PromptUI):
        token = ui.input(f'🧩 {self.puzzle_id} ? ').head
        if token:
            if not re.match(r'#\d+$', token):
                ui.print('! puzzle_id must be like #<NUMBER>')
                return
            ui.log(f'puzzle_id: {token}')
            self.puzzle_id = token

    def do_scale(self, ui: PromptUI):
        # TODO interactions to set/delete

        done: set[str] = set()
        for i, tier in enumerate(tiers):
            temp = self.scale.get(tier)
            if temp is None:
                ui.print(f'{i}. {tier} ???')
            else:
                ui.print(f'{i}. {tier} {temp:.2f}°C')
            done.add(tier)

        i = len(tiers)
        for tier, temp in self.scale.items():
            if tier not in done:
                ui.print(f'{i}. {tier} {temp:.2f}°C <INVALID TIER>')
                done.add(tier)
                i += 1

    def show_result(self, ui: PromptUI):
        ui.br()
        for line in capture_fences(
            break_sections(
                self.meta(),
                fenceit(self.describe_result(ui)),
                self.info()),
            lambda i, _: ('```📋', '```', ui.consume_copy()) if i == 0 else None
        ): ui.print(line)

    def do_report(self, ui: PromptUI):
        report_file = 'report.md' # TODO hoist and wire up to arg

        title = f'{self.site} 🧩 {self.puzzle_id}'
        guesses = self.result.guesses if self.result else self.attempt+1
        status = '🥳' if self.result else '😦'

        deets = f'{status} {guesses} ⏱️ {self.elapsed}'

        note_id = f'- 🔗 {title}'
        head_id = f'# {title}'

        note = f'{note_id} {deets}'
        header = f'{head_id} {deets}'

        def body_lines() -> Generator[str]:
            yield header

            yield ''
            yield from self.info()
            if self.result:
                yield ' '.join(self.result.count_parts())
            else:
                yield f'😦 {" ".join(self.tier_count_parts())}'
            yield ''

            yield from self.prog_lines(4*len(tiers))

        def rep(line: str) -> Iterable[str]|None:
            if line.startswith(head_id):
                return body

        body = body_lines()

        with atomic_file(report_file) as w:
            with open(report_file, 'r') as r:
                lines = break_sections(replace_sections(r, rep), body)

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
        ui.print(f'💾 updated {report_file}')

    def do_yester(self, ui: PromptUI):
        if not self.ephemeral or not self.stored:
            print('! scraping is only intended to be used after expiration and store')
            return

        try:
            with git_txn(f'{self.site} {self.puzzle_id} yesterdat') as txn:
                with self.log_to(ui):
                    # TODO why does this not work:
                    # page = requests.get('https://cemantle.certitudes.org/')
                    link = self.result.link if self.result else f'https://{self.site}'
                    _ = ui.input(f'Copy html from {link} and press <Enter>')
                    content = ui.paste()
                    soup = BeautifulSoup(content, 'html.parser')
                    for i, line in enumerate(content.splitlines()):
                        if i > 9:
                            ui.print(f'... {content.count("\n") - 9} more lines')
                            break
                        ui.print(f'... {line}')
                    self.yesterextract(ui, soup)
                txn.add(self.log_file)
        except ValueError as e:
            ui.print(f'! {e}')
            _ = subprocess.check_call(['git', 'checkout', self.log_file])
        else:
            ui.print(f'🗃️ {self.log_file}')

    def yesterextract(self, ui: PromptUI, soup: BeautifulSoup):
        yt = soup.select_one('#yestertable')
        if not yt:
            raise ValueError('missing #yestertable element')

        h = yt.select_one('h3')
        if not h:
            raise ValueError('missing #yestertable h3 element')

        match = re.match(r'''(?x)
            (?: Words \s+ close \s+ to
              | Mots \s+ proches \s+ de
            )
            \s+ (?P<word> [^\s]+ )
            ''', h.text)
        if not match:
            raise ValueError(f'unrecognized #yestertable h3 content: {h.text!r}')

        yesterword = cast(str, match.group(1))
        if self.found:
            have = self.word[self.found]
            if yesterword != have:
                raise ValueError(f'yesterword "{yesterword}" disagrees with found "{have}"')

        yb = yt.select_one('#yesterbody')
        if not yb:
            raise ValueError('missing #yestertable #yesterbody element')

        # TODO extract scheme from
        # <thead>
        # 	<tr>
        # 	<th class="number">#</th>
        # 	<th class="word">Word&nbsp;&nbsp;&nbsp;</th>
        # 	<th class="number">°C</th>
        # 	<th>&nbsp;&nbsp;&nbsp;</th>
        # 	<th class="number">‰</th>
        # 	<th></th>
        # 	</tr>
        # </thead>

        ranks: list[int] = []
        words: list[str] = []
        scores: list[float] = []
        progs: list[int] = []
        for row in yb.select('tr'):
            try:
                srank, word, sscore, _, sprog, _ = (
                    cell.text
                    for cell in row.select('td'))
                rank = int(srank) if srank else 0
                score = float(sscore)
                prog = int(sprog)
                ranks.append(rank)
                words.append(word)
                scores.append(score)
                progs.append(prog)
            except (ValueError, IndexError) as e:
                print(f'! failed to extrac data from yesterrow {row} : {e}')

        if not len(words):
            raise ValueError('emptry #yestertable #yesterbody, no rows extracted')

        if len(words) != 101:
            ui.print(f'WARNING: expected to extract 101 rows from #yestertable #yesterbody got {len(words)}')

        yesterdat = {
            'word': yesterword,
            'ranks': ranks,
            'words': words,
            'scores': scores,
            'progs': progs,
        }
        ui.log(f'yesterdat: {json.dumps(yesterdat)}')
        ui.print(f'💿 {len(words)} words of yesterdata relating to "{yesterword}"')

    def orient(self, ui: PromptUI):
        if self.found is not None:
            return self.finish

        try:
            model = olm_find_model(self.llm_client, self.llm_model)
        except RuntimeError:
            self.chat_model(ui)
        else:
            if self.llm_model != model:
                ui.log(f'session model: {self.llm_model}')
                self.llm_model = model

        if any(word for _, word in self.reply_words()):
            return self.chat_extract

        return self.ideate

    def generate(self, ui: PromptUI, tokens: PromptUI.Tokens|None = None):
        def rec(token: str, *maybe: Callable[[str], str|None]):
            for may in maybe:
                tok = may(token)
                if tok: return tok

        def just(token: str):
            return token

        def quoted(token: str):
            if token.startswith('"'):
                if token == '""': return
                return token if token.endswith('"') else f'{token}"'
            if token.startswith("'"):
                if token == "''": return
                return token if token.endswith("'") else f"{token}'"

        def var(token: str):
            if token.startswith('$'):
                return token if len(token) > 1 else None

        def ord(token: str):
            if token.startswith('#'):
                return token if len(token) > 1 else None

        count = 10
        rel: str|None = None
        like_words: list[str] = []
        unlike_words: list[str] = []

        if tokens is None: tokens = PromptUI.Tokens()

        token = tokens.token

        if len(token) > 1:
            try:
                count = int(token[1:])
            except ValueError:
                ui.print('! invalid *<INT>')
                return

        clear = False

        for token in tokens:
            if len(token) >= 2 and '/clear'.startswith(token):
                clear = True

            elif re.match(r'[Tt]\d+', token):
                like_words.extend(unroll_refs(f'${token}'))

            elif re.match(r'[Bb]\d+', token):
                unlike_words.extend(unroll_refs(f'${token}'))

            elif token.startswith('+') and len(token) > 1:
                token = rec(token[1:], var, ord, quoted, just)
                if token: like_words.append(token)
                else: ui.print(f'! ignoring * token {token}')

            elif token.startswith('-') and len(token) > 1:
                token = rec(token[1:], var, ord, quoted, just)
                if token: unlike_words.append(token)
                else: ui.print(f'! ignoring * token {token}')

            else:
                like_tok = rec(token, var, ord, quoted)
                if like_tok:
                    like_words.append(like_tok)
                    continue
                rel = token if not rel else f'{rel} {token}'

        if not rel: rel = 'similar'
        if ' ' not in rel: rel = f'{rel} to'

        lang = f'{self.lang} ' if self.lang else ''

        parts: list[str] = []

        parts.append(f'give me {count} {lang}words')

        parts.append(f' that are')

        if like_words or unlike_words:

            if like_words:
                parts.append(f' {rel}')
                parts.extend(word_list_parts(like_words, ',', 'and'))

            if unlike_words:
                if like_words: parts.append(' but')
                parts.append(f' not {rel}')
                parts.extend(word_list_parts(unlike_words, ',', 'or'))

        else:
            parts.append(f' not {rel} each other')

        if clear: self.chat_clear(ui)

        return self.chat_prompt(ui, ''.join(parts))

    def prompt_parts(self):
        stats = self.chat_stats()
        if stats.token_count > 0:
            yield f'🤖 {stats.assistant_count}'
            yield f'🫧 {stats.user_count}'
            yield f'🪙 {stats.token_count}'
        yield f'#{self.attempt+1}'

    def prompt(self, ui: PromptUI, prompt: str):
        first = True
        last = ''
        for part in self.prompt_parts():
            if last:
                if first:
                    ui.write(last)
                    first = False
                else:
                    ui.write(f' {last}')
            last = part
        ui.fin()
        return ui.input(f'{last} {prompt}')

    def ideate(self, ui: PromptUI) -> PromptUI.State|None:
        if self.found is not None:
            return self.finish

        if self.chat and self.chat[-1]['role'] == 'user':
            ui.print('// last chat prompt aborted; restart with `.`')

        token = self.prompt(ui, '? ').head

        if not token:
            if self.attempt == 0 and not self.chat:
                return self.generate(ui)
            return

        if token == '_': return self.chat_prompt(ui, '_')
        if token == '.': return self.chat_prompt(ui, '.')
        if token.startswith('/'): return self.do_cmd(ui)

        match = re.match(r'(>+)\s*(.+?)$', ui.tokens.raw)
        if match:
            mark, rest = match.groups()
            parts: list[str] = [rest]

            if len(mark) > 1:
                while True:
                    raw = ui.raw_input('>>> ')
                    rest = raw.lstrip('>').lstrip()
                    if not rest: break
                    parts.append(rest)

            return self.chat_prompt(ui, ' '.join(parts))

        if token.startswith('$'):
            try:
                n = int(token[1:])
                if n < 1: raise ValueError
            except ValueError:
                ui.print('! must be $<NUMBER>')
            else:
                ix = n-1
                i = self.prog[ix]
                return self.re_word(ui, i, ix)
            return

        if token.startswith('#'):
            try:
                n = int(token[1:])
                if n < 1: raise ValueError
            except ValueError:
                ui.print('! must be #<NUMBER>')
            else:
                i = n-1
                return self.re_word(ui, i)
            return

        if token.startswith('*'):
            return self.generate(ui, ui.tokens) # TODO pushdown

        match = re.match(r'(?xi) (?: T ( \d+ ) )? (?: B ( \d+ ) )?', token)
        if match:
            ts, bs = match.groups()
            if ts or bs:
                t = int(ts) if ts else None
                b = int(bs) if bs else None
                self.show_tbix(ui, self.top_bot_index(t, b))
                return

        return self.attempt_word(ui, ui.tokens.head.lower(), f'entered', ui.tokens) # TODO pushdown

    def re_word(self, ui: PromptUI, i: int, ix: int|None = None):
        score: float|None = None
        prog: int|None = None

        for token in ui.tokens:
            if 'score'.startswith(token.lower()):
                token = ui.tokens.next()
                try:
                    score = float(token)
                    assert score_min <= score <= score_max
                except ValueError:
                    ui.print(f'! invalid word score: not a float {token!r}')
                    return
                except AssertionError:
                    ui.print(f'! invalid word score, must be in range {score_min} <= {score_max}')
                    return

            if 'prog'.startswith(token.lower()):
                token = ui.tokens.next()
                try:
                    prog = int(token)
                    assert prog_min <= prog <= prog_max
                except ValueError:
                    ui.print('! invalid word prog‰, not an int {token!r}')
                    return
                except AssertionError:
                    ui.print(f'! invalid word prog‰, must be in range {prog_min} <= {prog_max}')
                    return

        if self.fix(ui, i, score, prog):
            ui.print(f'💿 {self.describe_word(i)} (fixed)')
            return

        ui.print(f'💿 {self.describe_word(i, ix)}')

    def finish(self, ui: PromptUI):
        it = self.found
        if it is None: return self.orient

        ui.print(f'Fin {self.describe_word(it)}')

        if not self.result_text:
            _ = ui.input('Paste share result, then preses <Enter>')

            result = ui.paste().strip()
            if not result: return

            ui.log(f'share result: {json.dumps(result)}')
            self.result_text = result

        try:
            res = self.Result.parse(self.result_text)
        except ValueError as e:
            ui.print(f'! invalid result text: {e}')
            self.result_text = ''
            return

        self.result = res

        if res.site: self.site = res.site
        if not self.puzzle_id:
            self.puzzle_id = f'#{res.puzzle_id}'

        cw = max(len(str(c)) for c in res.counts)
        for i, count in enumerate(reversed(res.counts), start=1):
            tier = tiers[-i]
            ui.print(f'    {tier} {count:>{cw}}')

        if res.guesses != self.attempt:
            ui.print(f"// result guess count {res.guesses} doesn't match our {self.attempt}")

        if not self.stored:
            raise StopIteration

        return self.review

    def fix(self, ui: PromptUI, i: int, score: float|None, prog: int|None) -> bool:
        parts: list[str] = []

        if score is not None:
            self.score[i] = score
            self.index = sorted(self.index, key=lambda i: self.score[i], reverse=True)
            parts.append(f'score:{score:.2f}')

        if prog is not None:
            self.prog[i] = prog
            parts.append(f'prog:{prog}')

        if not parts: return False

        ui.log(f'fix attempt_{i}: {' '.join(parts)}')
        return True

    def record(self, ui: PromptUI, word: str, score: float, prog: int|None):
        if word in self.wordbad:
            # TODO nicer to update, believe the user
            ui.print('! ignoring rejected response for word "{word}"')
            return

        if word in self.wordgood:
            # TODO nicer to update, believe the user
            ui.print('! ignoring duplicate response for word "{word}"')
            return

        i = len(self.word)
        assert i == self.attempt

        # TODO prog rank should be unique

        ui.log(f'attempt_{i}: "{word}" score:{score:.2f} prog:{prog}')
        self.word.append(word)
        self.score.append(score)
        if prog is not None:
            self.prog[i] = prog

        self.index.append(i)
        self.index = sorted(self.index, key=lambda i: self.score[i], reverse=True)

        self.attempt += 1
        self.wordgood[word] = i

        return i

    def reject(self, ui: PromptUI, word: str):
        if word in self.wordbad: return
        if word in self.wordgood:
            # TODO nicer to update, believe the user
            ui.print('! ignoring duplicate response for word "{word}"')
            return
        ui.log(f'reject: "{word}"')
        self.wordbad.add(word)

    def last_reply(self):
        for mess in reversed(self.chat):
            if mess['role'] == 'assistant':
                return mess.get('content', '')
        return ''

    def reply_words(self) -> Generator[tuple[int, str]]:
        reply = self.last_reply()
        seen: set[str] = set()
        for line in reply.splitlines():
            match = re.match(r'''(?x)
                (?P<n> \d+ ) [.)\s]
                \s*
                (?P<word> [^\s]+ )
                (?: \s+ (?P<rest> .+ ) )?
                $
            ''', line)
            if match:
                ns, word, _rest = match.groups()
                for sm in re.finditer(r'\w+', word.lower()):
                    word = sm.group(0)
                    if word in seen: continue
                    seen.add(word)
                    if word in self.wordbad: continue
                    if word in self.wordgood: continue
                    yield int(ns), word

    def attempt_word(self, ui: PromptUI, word: str, desc: str, tokens: PromptUI.Tokens|None = None) -> PromptUI.State|None:
        if not word: return

        if word in self.wordbad:
            ui.print(f'! "{word}" has already been rejected')
            return

        if word in self.wordgood:
            i = self.wordgood[word]
            ui.print(f'{self.describe_word(i, word=word)} is already known')
            return

        with ui.catch_state(KeyboardInterrupt, self.ideate):
            ui.br()
            ui.copy(word)
            desc = f'🤔 {desc} #{self.attempt+1} "{word}"'

            if not tokens: tokens = PromptUI.Tokens()

            while True:
                token = tokens.next_or_input(ui, f'{desc} score? ')
                if not token: return

                if token.startswith('!'):
                    self.reject(ui, word)
                    ui.print(f'// rejected {desc}')
                    token = token[1:] or tokens.next()
                    if token:
                        return self.attempt_word(ui, token, "corrected", tokens)
                    return

                try:
                    score = float(token)
                except ValueError:
                    ui.print('! invalid word score: not a float')
                    ui.tokens = PromptUI.Tokens()
                    continue

                if not (score_min <= score <= score_max):
                    ui.print(f'! invalid word score, must be in range {score_min} <= {score_max}')
                    ui.tokens = PromptUI.Tokens()
                    continue

                desc = f'{desc} {score:.2f}°C'
                break

            prog_req = False
            if self.prog_at is not None:
                prog_req = score >= self.prog_at
            elif self.prog:
                i = self.min_prog[0]
                prog_req = score >= self.score[i]

            prog: int|None = None

            while True:
                token = tokens.next_or_input(ui, f'{desc} prog‰ ? ') if prog_req else tokens.next()
                if token:
                    try:
                        prog = int(token)
                    except ValueError:
                        ui.print(f'! invalid word prog‰, not an int') # XXX loops
                        ui.tokens = PromptUI.Tokens()
                        continue

                    if not (prog_min <= prog <= prog_max):
                        ui.print(f'! invalid word prog‰, must be in range {prog_min} <= {prog_max}')
                        ui.tokens = PromptUI.Tokens()
                        continue

                    break
                elif not prog_req:
                    break

                if not token: break

            if prog_req and prog is None:
                ui.print('! prog‰ is required after {self.prog_at:.2f}°C for {desc}')
                return

            i = self.record(ui, word, score, prog)
            if i is not None:
                ui.print(f'💿 {self.describe_word(i)}')

            if self.found: return self.finish

    def word_iref(self, k: WordRef, n: int):
        if k == '$':
            ix = n - 1
            i = self.index[ix]
            return i, ix, f'"{self.word[i]}"'

        elif k == '#':
            i = n - 1
            return i, None, f'"{self.word[i]}"'

    def word_ref(self, k: WordRef, n: int):
        if k == '$':
            ix = n - 1
            i = self.index[ix]
            return f'"{self.word[i]}"'

        elif k == '#':
            i = n - 1
            return f'"{self.word[i]}"'

        assert_never(k)

    def set_chat_prompt(self, ui: PromptUI, prompt: str|ChatPrompt):
        cp = ChatPrompt.from_prompt(prompt) if isinstance(prompt, str) else prompt
        basis = set(self.word_ref(k, n) for k, n in cp.refs())
        if not basis and isinstance(prompt, str):
            self.last_chat_prompt = None
            self.last_chat_basis = set()
            return prompt

        ui.log(f'chat_prompt: {json.dumps(asdict(cp))}')
        self.last_chat_prompt = cp
        self.last_chat_basis = basis

        return cp.expand(self.word_ref)

    def regen_chat_prompt(self, ui: PromptUI):
        prompt = self.last_chat_prompt
        assert prompt is not None

        basis = set(self.word_ref(k, n) for k, n in prompt.refs())
        exp = prompt.expand(self.word_ref)

        ui.log(f'chat_prompt: _')
        self.last_chat_basis = basis

        return exp

    def chat_prompt(self, ui: PromptUI, prompt: str) -> PromptUI.State|None:
        with ui.catch_state(KeyboardInterrupt, self.ideate):

            if prompt == '_':
                cp = self.last_chat_prompt
                if not cp:
                    ui.print('! no last chat prompt available')
                    return

                prompt = self.regen_chat_prompt(ui)

            elif prompt == '.':
                for mess in reversed(self.chat):
                    if mess['role'] == 'user' and 'content' in mess:
                        prompt = mess['content']
                        break
                else:
                    ui.print('! no last chat message to repeat')
                    return

            else:
                try:
                    prompt = self.set_chat_prompt(ui, prompt)
                except ValueError as e:
                    ui.print('! {e}')
                    return

            last = self.chat[-1] if self.chat else None
            lastt = (last['role'], last.get('content')) if last else (None, None)
            if lastt != ('user', prompt):
                self.chat_append(ui, {'role': 'user', 'content': prompt})

            for line in wraplines(ui.screen_cols-4, prompt.splitlines()):
                ui.print(f'>>> {line}')

            # TODO wrapped writer
            # TODO tee content into a word scanner

            parts: list[str] = []
            ui.write('... ')
            for resp in self.llm_client.chat(model=self.llm_model, messages=self.chat, stream=True):
                try:
                    mess = resp['message'] # pyright: ignore[reportAny]
                    assert isinstance(mess, dict)
                    mess = cast(dict[str, Any], mess)
                except:
                    ui.print(f'\n! {resp!r}')
                    raise

                try:
                    role = mess['role'] # pyright: ignore[reportAny]
                    assert isinstance(role, str)
                    if role != 'assistant':
                        # TODO note?
                        continue

                    content = mess['content'] # pyright: ignore[reportAny]
                    assert isinstance(content, str)

                    parts.append(content)

                    # TODO care about resp['done'] / resp['done_reason'] ?

                    a, sep, b = content.partition('\n')
                    ui.write(a)
                    while sep:
                        end = sep
                        a, sep, b = b.partition('\n')
                        ui.write(f'{end}... {a}')

                except:
                    ui.print(f'\n! {mess!r}')
                    raise
            ui.fin()
            self.chat_append(ui, {'role': 'assistant', 'content': ''.join(parts)})

            if any(self.reply_words()):
                return self.chat_extract

            ui.print(f'// No new words extracted from last chat reply')

    def chat_append(self, ui: PromptUI, mess: ollama.Message):
        ui.log(f'session: {json.dumps(mess)}')
        self.chat.append(mess)
        self.chat_role_counts.update((mess['role'],))

    def chat_stats(self):
        role_counts = Counter(mess['role'] for mess in self.chat)
        token_count = sum(
            count_tokens(mess.get('content', ''))
            for mess in self.chat)
        user_count = role_counts.pop("user", 0)
        assistant_count = role_counts.pop("assistant", 0)
        return ChatStats(token_count, user_count, assistant_count)

    def note_chat_basis_change(self, ui: PromptUI):
        if self.last_chat_prompt:
            basis = set(self.word_ref(k, n) for k, n in self.last_chat_prompt.refs())
            diffa = basis.difference(self.last_chat_basis)
            diffb = self.last_chat_basis.difference(basis)
            parts: list[str] = []
            if diffb: parts.append(f'💤 {' '.join(sorted(diffb))}')
            if diffa: parts.append(f'🛜 {' '.join(sorted(diffa))}')
            if parts: ui.print(f'🫧 basis changed {' '.join(parts)}')

    def chat_extract(self, ui: PromptUI) -> PromptUI.State | None:
        with ui.catch_state(KeyboardInterrupt, self.ideate):
            words = sorted(word for _, word in self.reply_words())
            ui.br()

            if not words:
                ui.print(f'// No new words extracted from last chat reply')
                return self.ideate

            ui.print(f'// Extracted {len(words)} new words from last chat reply')
            iw = len(str(len(words)))
            for i, word in enumerate(words):
                ui.print(f'[{i+1:{iw}}] {word}')

            self.note_chat_basis_change(ui)

            while True:
                token = self.prompt(ui, f'extract_').head
                if not token: return self.ideate
                if token == '_':
                    return self.chat_prompt(ui, '_')
                if token.startswith('/'):
                    return self.do_cmd(ui)
                if token == '...':
                    return self.chat_extract_all

                try:
                    n = int(token)
                except ValueError:
                    ui.print('! invalid list number, expected integer')
                    continue
                if not (0 < n <= len(words)):
                    ui.print('! invalid list number, out of range')
                    continue

                return self.attempt_word(ui, words[n-1], f'extract_{n}/{len(words)}') or self.chat_extract

    def chat_extract_all(self, ui: PromptUI) -> PromptUI.State | None:
        with ui.catch_state(KeyboardInterrupt, self.ideate):
            words = sorted(word for _, word in self.reply_words())
            if words:
                ui.br()
                self.note_chat_basis_change(ui)
                st = self.attempt_word(ui, words[0], f'extract_1/{len(words)}')
                if st: return st
                if len(words) > 1:
                    return self.chat_extract_all
        return self.ideate

    def chat_last(self, ui: PromptUI):
        reply = ''

        for mess in self.chat:
            role = mess['role']
            content = mess.get('content', '')
            if role == 'assistant':
                reply = content
            elif role == 'user':
                if reply:
                    ui.print(f'... 🪙 {count_tokens(reply)}')
                    reply = ''
                for line in wraplines(ui.screen_cols-4, content.splitlines()):
                    ui.print(f'>>> {line}')

        if reply:
            for line in wraplines(ui.screen_cols-4, reply.splitlines()):
                ui.print(f'... {line}')

        if self.last_chat_prompt:
            for k, n in self.last_chat_prompt.refs():
                i, ix, qword = self.word_iref(k, n)
                desc = self.describe_word(i, ix)
                mark = '🪨' if qword in self.last_chat_basis else '🔥'
                ui.print(f'{mark} {desc}')

    def chat_clear(self, ui: PromptUI):
        ui.print('cleared chat 🪙 = 0')
        ui.log(f'session clear')
        self.chat = []

    def chat_model(self, ui: PromptUI):
        byn: list[str] = []

        model = ui.tokens.next()
        while True:
            if model:
                try:
                    n = int(model)
                except ValueError:
                    pass
                else:
                    model = byn[n-1]

                try:
                    model = olm_find_model(self.llm_client, model)
                except RuntimeError:
                    ui.print(f'! unavailable model {model!r}')
                else:
                    break

            ui.br()
            ui.print(f'Available Models:')
            byn = sorted(get_olm_models(self.llm_client))
            for i, model in enumerate(byn):
                mark = '*' if model == self.llm_model else ' '
                ui.print(f'{i+1}. {mark} {model}')

            model = ui.input('Select model (by name or number)> ').next()
            if not model: return

        ui.log(f'session model: {model}')
        self.llm_model = model

        if len(self.chat) > 0:
            ui.log(f'session clear')
            self.chat = []
            ui.print(f'Using model {self.llm_model!r} ; session cleared')

        else:
            ui.print(f'Using model {self.llm_model!r}')

if __name__ == '__main__':
    Search.main()
