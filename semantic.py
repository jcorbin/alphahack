#!/usr/bin/env python

import argparse
import bs4
import datetime
import json
import math
import ollama
import re
import requests
from collections import Counter
from collections.abc import Generator, Iterable, Sequence
from dataclasses import dataclass
from dateutil.tz import gettz
from typing import assert_never, cast, final, overload, override, Callable, Literal
from urllib.parse import urlparse

from mdkit import break_sections, capture_fences, fenceit
from store import StoredLog, git_txn
from strkit import matchgen, spliterate, wraplines, MarkedSpec
from ui import PromptUI

def lang_code_to_kind(la: str):
    # TODO better
    la = la.lower()
    if la == 'en': return ''
    if la == 'fr': return 'French'
    raise ValueError(f'unknown language code {la!r}')

def role_content(chat: Iterable[ollama.Message], role: str):
    for mess in chat:
        if mess['role'] != role: continue
        if 'content' not in mess: continue
        yield mess['content']

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

tier_progs: list[int|None] = [
    None, # 🧊
    None, # 🥶
    1,    # 😎
    900,  # 🥵
    990,  # 🔥
    999,  # 😱
    1000, # 🥳
]

scale_fixed: dict[Tier, float] = {}
scale_fixed['🧊'] = -100.0
scale_fixed['🥶'] =    0.0
scale_fixed['🥳'] =  100.0

def parse_scale_score(mark: str, score_str: str, prog_str: str):
    try:
        tier = tiers.index(cast(Tier, mark))
    except IndexError:
        raise ValueError('invalid emoji tier mark')
    prog = int(prog_str.strip()) if prog_str.strip() else None
    if prog != tier_progs[tier]:
        raise ValueError(f'expected {tier_progs[tier]} tier prog have {prog}')
    score = float(score_str.strip())
    if mark in scale_fixed and score != scale_fixed[mark]:
        raise ValueError(f'expected {scale_fixed[mark]} tier score have {score}')
    mark = cast(Tier, mark)
    return mark, score

def scrape_scale_row(row: bs4.Tag):
    mark_cell = row.select_one('td.emoji') # <td class="emoji">🔥</td>
    prog_cell: bs4.Tag|None = None # <td class="number">990</td>
    score_cell: bs4.Tag|None = None # <td class="decimal number">38.29</td>
    for nc in row.select('td.number'):
        if not score_cell and 'decimal' in nc.attrs['class']: score_cell = nc
        if not prog_cell and 'decimal' not in nc.attrs['class']: prog_cell = nc
    if not mark_cell: raise ValueError('no td.emoji mark cell')
    if not score_cell: raise ValueError('no td.number.decimal score cell')
    return parse_scale_score(
        mark_cell.text,
        score_cell.text,
        prog_cell.text if prog_cell else '')

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
    models = cast(object, client.list()['models'])
    assert isinstance(models, list)
    for x in cast(list[object], models):
        assert isinstance(x, dict)
        x = cast(dict[str, object], x)
        name = x.get('name')
        assert isinstance(name, str)
        yield name

def olm_find_model(client: ollama.Client, name: str):
    try:
        return max(n for n in get_olm_models(client) if n.startswith(name))
    except ValueError:
        raise RuntimeError(f'Unavailable --ollama-model {name!r} ; available models: {' '.join(sorted(get_olm_models(client)))}')

word_ref_pattern = re.compile(r'''(?x)
                                \# ( \d+ )
                              | \$ ( [TtBb]? ) ( -? \d+ )
                              ''')
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

def word_match_refs(match: re.Match[str]) -> Generator[tuple[WordRef, int]]:
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

trailer_seps = ';.'

@final
class ChatPrompt:
    pattern = re.compile(r'''(?x)
        give .*? (?P<count> \d+ )
        (?: \s+ (?P<kind> .+? ) )?
        \s+ words
        \s+ (?P<rel> [^;.]+? )
        \s*
        $
    ''')

    def __init__(self,
                 prompt: str = '',
                 count: int = 10,
                 kind: str|None = None,
                 rel: str = 'related',
                 trailer: str|None = None):
        self.prompt = prompt
        self.count = count
        self.kind = kind
        self.rel = rel
        self.trailer = trailer

        for sep in trailer_seps:
            i = prompt.find(sep)
            if i > 0:
                prompt, self.trailer = prompt[:i], prompt[i:]
                break

        for match in word_ref_pattern.finditer(prompt):
            prior = prompt[:match.start(0)]
            match = self.pattern.match(prior)
            break
        else:
            match = self.pattern.match(prompt)

        if match:
            self.count = int(match.group(1))
            self.kind = cast(str|None, match.group(2) or None)
            self.rel = cast(str, match.group(3) or '')

        elif prompt:
            raise ValueError('unrecognized chat prompt')

        vars: list[int] = []
        ords: list[int] = []
        for k, n in word_refs(prompt):
            if k == '$': vars.append(n)
            elif k == '#': ords.append(n)
            else: assert_never(k)
        self.vars = tuple(vars)
        self.ords = tuple(ords)

        if not self.prompt:
            self.prompt = self.rebuild()

    @override
    def __repr__(self):
        return f'ChatPrompt(prompt={self.prompt!r}, count={self.count}, kind={self.kind!r}, rel={self.rel!r}, trailer={self.trailer!r})'

    @property
    def num_refs(self):
        return len(self.vars) + len(self.ords)

    def refs(self) -> Generator[tuple[WordRef, int]]:
        for n in self.vars: yield '$', n
        for n in self.ords: yield '#', n

    def rebuild(self,
        count: int|None = None,
        kind: str|None = None,
        rel: str|None = None,
        like: Sequence[str] = (),
        unlike: Sequence[str] = (),
        trailer: Iterable[str]|str|None = None,
    ):
        return ''.join(build_prompt(
            like, unlike,
            count=count or self.count,
            kind=self.kind if kind is None else kind,
            rel=self.rel if rel is None else rel,
            trailer=self.trailer if trailer is None else trailer,
        ))

def cleanse_rel(rel: str):
    neg: bool = False
    rel = re.sub(r'\s+', ' ', rel.strip())

    if rel.endswith(' each other'):
        rel = rel[:-11]

    for p in ('that ', 'are '):
        if rel.startswith(p): rel = rel[len(p):]

    for p in ('not ', 'do not '):
        if rel.startswith(p):
            neg = True
            rel = rel[len(p):]
            break
    return neg, rel

def phrase_rel(rel: str, neg: bool = False):
    _, rel = cleanse_rel(rel)

    if ' ' not in rel: rel = f'{rel} to'

    for s in (' to', ' with'):
        if rel.endswith(s):
            rel = f'are not {rel}' if neg else f'are {rel}'
            break
    else:
        if neg: rel = f'do not {rel}'

    rel = f'that {rel}'
    return rel

def word_list_parts(words: Sequence[str], sep: str, fin: str):
    n = len(words)
    for i, word in enumerate(words):
        if n > 2 and i > 0: yield sep
        if n > 1 and i == n-1: yield f' {fin}'
        yield f' {word}'

def build_prompt(
    like: Sequence[str],
    unlike: Sequence[str],
    /,
    count: int = 10,
    kind: str|None = None,
    rel: str = 'related',
    trailer: Iterable[str]|str|None = None,
) -> Generator[str]:
    yield f'give me {count} '
    if kind: yield f'{kind.strip()} '
    yield 'words'

    if like or unlike:
        if like:
            yield f' {phrase_rel(rel, False)}'
            yield from word_list_parts(like, ',', 'and')
        if unlike:
            if like: yield ' but'
            yield f' {phrase_rel(rel, True)}'
            yield from word_list_parts(unlike, ',', 'or')
    else:
        yield f' {phrase_rel(rel, True)} each other'

    if trailer:
        for part in [trailer] if isinstance(trailer, str) else trailer:
            havesep = any(part.startswith(c) for c in trailer_seps)
            yield part if havesep else f'{trailer_seps[0]} {part}'

@matchgen(r'''(?x)
    (?P<n> \d+ ) [.)\s]
    \s+

    (?:
        \*\* ( .+? ) \*\*
      | \* ( .+? ) \*
      | \( ( .+? ) \)
      | ( [^(:]+ ) (?= \s+ [\-:(] )
      | ( .+? ) $
    )

''')
def find_match_words(match: re.Match[str]):
    n = int(match.group(1))
    # rest = match.string[ match.end(0): ]
    # print('REST', repr(rest))
    for term in match.groups()[1:]:
        if not isinstance(term, str) or not term: continue
        # print('TERM', repr(term))
        for word in spliterate(term, " ", trim=True):
            for match in re.finditer(r'\w+', word):
                yield n, match.group(0)

@final
@dataclass
class ChatStats:
    token_count: int
    user_count: int
    assistant_count: int

@dataclass
class ChatSession:
    chat: list[ollama.Message]
    model: str

@dataclass
class YesterDatum:
    rank: int
    word: str
    score: float
    prog: int

default_abbr = {
    # '!gim': 'give me $count $kind words',
    # '!rel': 'that are $rel',
    # '!fin': 'each other', XXX lambda ctx: only if !rel and no refs
    # '*': '!gim !rel ... !fin', XXX lambda ctx: proc tokens in ...
    '!new': 'do not list any words that you have already listed above',
    '!cont': 'keep going',
    '!meh': 'none of those word are very good',
    '!bad': 'all of those word are terrible',
}

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

        self.pubtime: datetime.datetime|None = None
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

        self.http_client = requests.Session()
        self.http_client.headers["User-Agent"] = 'github.com/jcorbin/alhpahack'
        self.http_verbose: int = 0
        self.logged_cookies: dict[str, str] = {}

        self.llm_client = ollama.Client()
        self.llm_model: str = self.default_chat_model

        self.abbr: dict[str, str] = dict(default_abbr)
        self.chat: list[ollama.Message] = []
        self.chat_history: list[ChatSession] = []

        self.last_chat_prompt: str|ChatPrompt = ''
        self.last_chat_basis: set[str] = set()

        self.min_word_len: int = 2

        self.chat_extract_info: list[str] = []
        self.chat_extract_from: str = ''
        self.chat_extract_scav: bool = False
        self.extracted: int = 0
        self.extracted_good: int = 0
        self.extracted_bad: int = 0

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
        if self.pubtime is not None: return self.pubtime
        if self.start is None: return None
        return self.next_pub(self.start - datetime.timedelta(days=1))

    def set_pubtime(self, ui: PromptUI, ut: int):
        dut = datetime.datetime.fromtimestamp(ut, datetime.UTC)
        if self.pubtime != dut:
            ui.log(f'pubtime: {ut}')
            self.pubtime = dut

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

    @property
    def startup_done(self):
        if not self.puzzle_id: return False
        if len(self.scale) < len(tiers): return False
        return True

    @override
    def startup(self, ui: PromptUI):
        if self.startup_done: return self.orient

        ui.write('Scraping index...')
        res = self.request(ui, 'get', '/')
        if res.status_code != 200:
            ui.fin(f'failed: {res.status_code} {res.reason}')
        elif res.headers.get('Content-Type', '').partition(';')[0] != 'text/html':
            ui.fin(f'failed: expected text/html content, got {res.headers.get("Content-Type", "")}')
        else:
            soup = bs4.BeautifulSoup(res.content, 'html5lib')

            doc = soup.select_one('html')
            if doc:
                lang = doc.attrs.get('lang')
                if isinstance(lang, str):
                    self.lang = lang_code_to_kind(lang)
                    ui.write(f' 🌎 {lang!r} -> {self.lang!r}')

            script = soup.select_one('#cemantle-script') or soup.select_one('#cemantix-script')
            if script:
                spn = script.attrs.get('data-puzzle-number')
                if isinstance(spn, str):
                    self.puzzle_id = f'#{spn}'
                    ui.log(f'puzzle_id: {self.puzzle_id}')
                    ui.write(f' 🧩 {self.puzzle_id}')

                sut = script.attrs.get('data-utc-time')
                if isinstance(sut, str):
                    self.set_pubtime(ui, int(sut))
                    ui.write(f' 🕛 {self.pubtime}')

            summary = soup.select_one('#cemantle-summary') or soup.select_one('#cemantix-summary')
            if summary:
                n = 0
                for row in summary.select('table.story tbody tr'):
                    if not row.select('td'):
                        if not row.select('th'):
                            ui.print(f'? empty #{summary.attrs["id"]} .story table row: {row}')
                        continue
                    try:
                        tier, score = scrape_scale_row(row)
                    except ValueError as err:
                        ui.print(f'! failed to parse temp scale from {row} : {err}')
                    else:
                        ui.log(f'scale: {tier} {score:.2f} °C')
                        self.scale[tier] = score
                        n += 1

                ui.write(f' 🌡️ {n} tiers')

            ui.fin(' done.')

        if not self.puzzle_id:
            ui.br()
            self.do_site(ui)
            self.do_lang(ui)
            self.do_puzzle(ui)
            if not self.puzzle_id: return
        return self.startup_scale

    def startup_scale(self, ui: PromptUI):
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

                with ui.input(f'{tier} °C ? ') as tokens:
                    if tokens.empty:
                        confirm = next(ui.input(f'skip temp scale entry? '), '')
                        return self.orient if confirm.lower().startswith('y') else None

                    try:
                        temp = float(next(tokens, ''))
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

        return self.orient

    @override
    def hist_body(self, ui: PromptUI):
        return break_sections(
            fenceit(self.describe_result(ui)),
            self.info())

    @override
    def review(self, ui: PromptUI):
        if self.result is None and not self.stored: return self.orient
        self.show_result(ui)
        return self.do_cmd

    @override
    def load(self, ui: PromptUI, lines: Iterable[str]):
        for t, rest in super().load(ui, lines):
            match = re.match(r'''(?x)
                pubtime :
                \s+
                (?P<timestamp> \d+ )
                \s* ( .* )
                $''', rest)
            if match:
                sut, rest = match.groups()
                assert rest == ''
                self.set_pubtime(ui, int(sut))
                continue

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
                    if name == 'prog': prog = None if value == '_' else int(value)
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
                j = self.record(ui, word, score, prog)
                if j != i:
                    raise RuntimeError(f'reload inconsistency attempt({word!r}, {score}, {prog}) -> {j} != {i}')
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
                try:
                    dat = cast(object, json.loads(mess))
                except json.JSONDecodeError:
                    pass
                else:
                    if isinstance(dat, dict) and 'prompt' in dat:
                        mess = cast(object, dat['prompt'])
                        assert isinstance(mess, str)
                _ = self.set_chat_prompt(ui, mess)
                continue

            match = re.match(r'''(?x)
                abbr : \s* (?P<abbr> [^\s]+ )
                (?: \s+ (?P<mess> .+? ) )?
                $''', rest)
            if match:
                abbr, mess = match.groups()
                if mess:
                    self.abbr[abbr] = mess
                elif abbr in self.abbr:
                    del self.abbr[abbr]
                continue

            match = re.match(r'''(?x)
                http \s+ (?P<coll> header | cookie ):
                \s+ (?P<name> [^\s]+ )
                \s+ (?P<value> .+? )
                $''', rest)
            if match:
                coll, name, value = match.groups()

                if coll == 'cookie':
                    if value == '_':
                        del self.http_client.cookies[name]
                    else:
                        value = cast(object, json.loads(value))
                        assert isinstance(value, str)
                        self.http_client.cookies[name] = value

                elif coll == 'header':
                    if value == '_':
                        del self.http_client.headers[name]
                    else:
                        value = cast(object, json.loads(value))
                        assert isinstance(value, str)
                        self.http_client.headers[name] = value

                continue

            match = re.match(r'''(?x)
                session : \s* (?P<mess> .+ )
                $''', rest)
            if match:
                raw, = match.groups()
                if raw.startswith('pop'):
                    if raw != 'pop': raise NotImplementedError(f'chat pop index')
                    _ = self.chat_pop(ui)
                else:
                    mess = cast(object, json.loads(raw))
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
                self.chat_model(ui, model)
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
                rej = cast(object, json.loads(srej))
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

    @override
    def info(self):
        yield f'🤔 {self.attempt} attempts'
        yield f'📜 {len(self.sessions)} sessions'
        yield f'🫧 {len(self.chat_history)} chat sessions'

        role_counts = self.chat_role_counts()
        user = role_counts.get("user", 0)
        asst = role_counts.get("assistant", 0)
        if user: yield f'⁉️ {user} chat prompts'
        if asst: yield f'🤖 {asst} chat replies'

    def chat_role_counts(self):
        role_counts: Counter[str] = Counter()
        for h in self.chat_history:
            for mess in h.chat:
                role_counts.update((mess['role'],))
        return role_counts

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

    @property
    def origin(self):
        origin = self.site
        if '://' not in origin:
            origin = f'https://{origin}'
        return origin.rstrip('/')

    def request(self,
        ui: PromptUI,
        method: str,
        path: str,
        referer: str|None = None,
        headers: dict[str, str]|None=None,
        data: dict[str, object]|None=None,
        allow_redirects: bool=True,
        timeout: int = 3,
        verbose: int|None = None,
    ):
        if verbose is None: verbose = self.http_verbose
        if headers is None: headers = {}

        origin = self.origin
        _ = headers.setdefault('Origin', origin)

        if referer:
            headers['Referer'] = referer
        else:
            _ = headers.setdefault('Referer', f'{origin}/')

        req = self.http_client.prepare_request(requests.Request(
            method=method.upper(),
            url=f'{self.origin}{path}',
            headers=headers,
            data=data,
        ))

        if verbose:
            ui.print(f'> {req.method} {req.url}')
        if verbose > 1:
            for k, v in req.headers.items():
                ui.print(f'> {k}: {v}')
        ui.log(f'request: {json.dumps({
            "method": req.method,
            "url": req.url,
            "headers": dict(req.headers),
            "data": data,
        })}')

        if verbose > 1:
            ui.print(f'* timeout: {timeout}')
            ui.print(f'* allow_redirects: {allow_redirects}')
        res = self.http_client.send(req,
            timeout=timeout,
            allow_redirects=allow_redirects,
        )

        if verbose:
            if verbose > 1:
                ui.print(f'< {res.status_code} {res.reason}')
            else:
                ct = res.headers.get('Content-Type', '<unknown>')
                cl = res.headers.get('Content-Length', '?')
                ui.print(f'< {res.status_code} {res.reason} {ct} {cl} bytes')

        if verbose > 1:
            for k, v in res.headers.items():
                ui.print(f'< {k}: {v}')
        ui.log(f'response: {json.dumps({
            "url": res.url,
            "status": res.status_code,
            "reason": res.reason,
            "headers": dict(res.headers),
            "content": res.content.decode(),
        })}')

        for name, value in self.http_client.cookies.iteritems():
            if self.logged_cookies.get(name, '') != value:
                ui.log(f'http cookie: {name} {json.dumps(value)}')
        prior_keys = set(self.http_client.cookies)
        prior_keys.difference_update(self.http_client.cookies.iterkeys())
        for name in prior_keys:
            ui.log(f'http cookie: {name} _')

        return res

    def do_abbr(self, ui: PromptUI):
        with ui.tokens as tokens:
            if tokens.empty:
                for abbr in sorted(self.abbr):
                    ui.print(f'  {abbr} - {self.abbr[abbr]!r}')
                return

            abbr = next(tokens)
            if not abbr.startswith('!'):
                ui.print(f'abbr should start with !')
                return

            if tokens.empty:
                if abbr in self.abbr:
                    del self.abbr[abbr]
                    ui.print(f'  deleted {abbr}')
                    ui.log(f'abbr: {abbr}') # TODO load
                return

            self.abbr[abbr] = tokens.rest
            ui.print(f'  defined {abbr} = {self.abbr[abbr]!r}')
            ui.log(f'abbr: {abbr} {self.abbr[abbr]}') # TODO load

    def do_cmd(self, ui: PromptUI):
        with ui.tokens_or('> '):
            cmd = next(ui.tokens, None)
            if cmd:
                return self.dispatch_cmd(ui, cmd)

    def dispatch_cmd(self, ui: PromptUI, token: str):
        cmds: dict[str, PromptUI.State] = {
            # TODO proper help command ; reuse for '?' token
            # TODO add '/' prefix here ; generalize dispatch

            'prog': self.show_prog,
            'tiers': self.show_tiers,

            'site': self.do_site,
            'lang': self.do_lang,
            'puzzle': self.do_puzzle,
            'scale': self.do_scale,
            'result': self.show_result,
            'report': self.do_report,
            'yester': self.do_yester,
            'notbad': self.do_notbad,

            'abbr': self.do_abbr,
            'clear': self.chat_clear_cmd,
            'extract': self.chat_extract,
            'model': self.chat_model_cmd,
            'last': self.chat_last,
        }

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

        return cmds[comp[0]](ui)

    def do_site(self, ui: PromptUI):
        with ui.input(f'🔗 {self.site} ? ') as tokens:
            site = next(tokens, None)
            if site:
                self.site = site
                ui.log(f'site: {self.site}')

    def do_lang(self, ui: PromptUI):
        with ui.input(f'🌎 {self.lang} ? ') as tokens:
            lang = next(tokens, None)
            if lang:
                self.lang = lang
                ui.log(f'lang: {self.lang}')

    def do_puzzle(self, ui: PromptUI):
        with ui.input(f'🧩 {self.puzzle_id} ? ') as tokens:
            if tokens.peek():
                ps = tokens.have(r'#\d+$', lambda m: m[0])
                if not ps:
                    ui.print('! puzzle_id must be like #<NUMBER>')
                    return
                ui.log(f'puzzle_id: {ps}')
                self.puzzle_id = ps

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

    @property
    @override
    def report_desc(self) -> str:
        guesses = self.result.guesses if self.result else self.attempt+1
        status = '🥳' if self.result else '😦'
        return f'{status} {guesses} ⏱️ {self.elapsed}'

    @property
    @override
    def report_body(self) -> Generator[str]:
        yield from self.info()
        if self.result:
            yield ' '.join(self.result.count_parts())
        else:
            yield f'😦 {" ".join(self.tier_count_parts())}'
        yield ''
        yield from self.prog_lines(4*len(tiers))

    def do_notbad(self, ui: PromptUI):
        with ui.tokens as tokens:
            word = next(tokens, None)
            if word is not None:
                self.wordbad.remove(word)
                return self.attempt_word(ui, word.lower(), f'reentered')

    def do_yester(self, ui: PromptUI):
        if not self.ephemeral or not self.stored:
            print('! yesterdata is only expected after expiration and store')
            return

        with (
            git_txn(f'{self.site} {self.puzzle_id} yesterdat') as txn,
            txn.will_add(self.log_file),
            self.log_to(ui),
        ):
            ok = False
            with ui.print_exception((IndexError, ValueError, requests.JSONDecodeError), 'pass'):
                self.yesterreq(ui)
                ok = True
            if not ok:
                link = self.result.link if self.result else f'https://{self.site}'
                _ = ui.input(f'Copy html from {link} and press <Enter>')
                self.yesterscrape(ui, ui.paste())

        ui.print(f'🗃️ {self.log_file}')

    def yesterreq(self, ui: PromptUI):
        def scrape():
            ui.write('Scraping index...')
            res = self.request(ui, 'get', '/')
            if res.status_code != 200:
                ui.fin(f'failed: {res.status_code} {res.reason}')
            elif res.headers.get('Content-Type', '').partition(';')[0] != 'text/html':
                ui.fin(f'failed: expected text/html content, got {res.headers.get("Content-Type", "")}')
            else:
                soup = bs4.BeautifulSoup(res.content, 'html5lib')
                # <a id="cemantix-yesterday"><b><u>paire</u></b></a>
                # <a id="cemantle-yesterday"><b><u>suite</u></b></a>
                for q in ('#cemantix-yesterday', '#cemantle-yesterday'):
                    yea = soup.select_one(q)
                    if yea: return yea.text

        def extract(dat: object):
            if not isinstance(dat, list):
                raise ValueError('expected an array')

            dat = cast(list[object], dat)
            if not all(isinstance(x, list) for x in dat):
                raise ValueError('expected an array-of-arrays')

            ui.write('json records')
            dat = cast(list[list[object]], dat)
            for i, el in enumerate(dat):
                ui.write('.')
                word, prog, score = el
                if not isinstance(word, str):
                    raise ValueError(f'invalid response[{i}] [0] word')
                if not isinstance(prog, int):
                    raise ValueError(f'invalid response[{i}] [1] prog')
                if not isinstance(score, float) and not isinstance(score, int):
                    raise ValueError(f'invalid response[{i}] [2] socre')
                yield word, prog, float(score)

        yesterword = self.word[self.found] if self.found else scrape()
        if not yesterword:
            raise ValueError('no word found yesterday to request')

        ui.write(f'Scraping yesterdat from /nearby word={yesterword}...')
        res = self.request(ui, 'post', '/nearby', data={'word': yesterword})
        data = list(extract(cast(object, res.json())))
        return self.yesterdat(ui, yesterword, (
            YesterDatum(rank, word, score, prog)
            for rank, (word, prog, score) in enumerate(data)))

    def yesterscrape(self, ui: PromptUI, content: str):
        soup = bs4.BeautifulSoup(content, 'html5lib')
        for i, line in enumerate(content.splitlines()):
            if i > 9:
                ui.print(f'... {content.count("\n") - 9} more lines')
                break
            ui.print(f'... {line}')

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

        def extract():
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

            some = False
            for row in yb.select('tr'):
                try:
                    srank, word, sscore, _, sprog, _ = (
                        cell.text
                        for cell in row.select('td'))
                    rank = int(srank) if srank else 0
                    some = True
                    yield YesterDatum(rank, word, float(sscore), int(sprog))

                except (ValueError, IndexError) as e:
                    print(f'! failed to extract data from yesterrow {row} : {e}')

            if not some:
                raise ValueError('empty #yestertable #yesterbody, no rows extracted')

        return self.yesterdat(ui, yesterword, extract())

    def yesterdat(self, ui: PromptUI, word: str, records: Iterable[YesterDatum]):
        ranks: list[int] = []
        words: list[str] = []
        scores: list[float] = []
        progs: list[int] = []

        for rec in records:
            ranks.append(rec.rank)
            words.append(rec.word)
            scores.append(rec.score)
            progs.append(rec.prog)

        if len(words) != 101:
            ui.print(f'WARNING: expected to have 101 records of yesterdat, got {len(words)}')

        yesterdat = {
            'word': word,
            'ranks': ranks,
            'words': words,
            'scores': scores,
            'progs': progs,
        }
        ui.log(f'yesterdat: {json.dumps(yesterdat)}')
        ui.print(f'💿 {len(words)} words of yesterdata relating to "{word}"')

    def check_stats(self, ui: PromptUI):
        ui.write('Fetching stats...')
        res = self.request(ui, 'get', '/stats')

        stats = cast(object, res.json())
        if isinstance(stats, dict):
            stats = cast(dict[str, object], stats)
            try:
                num = stats['num']
            except KeyError:
                ui.print(f'! no puzzle num in {stats!r}')
                return
            if self.puzzle_id != f'#{num}':
                ui.print(f'! puzzle id mismatch, expected {self.puzzle_id}, have {num}')
                raise StopIteration

            try:
                solvers = stats['solvers']
            except KeyError:
                pass
            else:
                ui.write(f' 🧩 {self.puzzle_id} with {solvers} solvers')

        ui.fin(' done.')

    def orient(self, ui: PromptUI):
        if self.found is not None:
            return self.finish

        self.check_stats(ui)

        ui.print(f'🌡️ {" ".join(f"{tier} {self.scale[tier]:.2f}°C" for tier in tiers)}')
        if self.prog_at is None:
            self.prog_at = self.scale.get('😎')

        try:
            model = olm_find_model(self.llm_client, self.llm_model)
        except RuntimeError:
            self.chat_model_cmd(ui)
        else:
            self.chat_model(ui, model)

        self.chat_extract_scav = False
        if any(self.chat_extract_words()):
            return self.chat_extract

        return self.ideate

    def generate(self, ui: PromptUI):
        try:
            clear, np = self.build_next_prompt(ui)

        except StopIteration:
            return

        except ValueError as e:
            ui.print(f'* {e}')
            return

        if clear:
            self.chat_clear_cmd(ui)

        st = self.chat_prompt(ui, np)

        return st

    def build_next_prompt(self, ui: PromptUI):
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

        def ref(token: str):
            if any(token.startswith(c) for c in '$#'):
                return token if len(token) > 1 else None

        clear = False
        count: int|None = None
        rel: str|None = None
        like_words: list[str] = []
        unlike_words: list[str] = []
        trailer: list[str] = []
        trailer_given: bool = False

        cp: ChatPrompt|None = None
        if isinstance(self.last_chat_prompt, ChatPrompt):
            cp = self.last_chat_prompt
        elif self.last_chat_prompt:
            try:
                cp = ChatPrompt(self.last_chat_prompt)
            except ValueError:
                pass

        with ui.tokens as tokens:
            if tokens.have(r'.\?'):
                if cp:
                    ui.print('last chat prompt:')
                    ui.print(f'> {cp.prompt}')
                else:
                    ui.print('no last chat prompt')
                raise StopIteration

            first = True
            count_given = False

            for token in tokens:
                if first:
                    first = False
                    token = token[1:] # TODO more general "dispatched command prefix trim"
                    if not token: continue

                if re.match(r'\d+$', token):
                    if count_given:
                        raise ValueError('count already given, did you miss a T or B?')
                    count = int(token)
                    count_given = True

                # TODO can this be an abbr?
                elif len(token) >= 2 and '/clear'.startswith(token):
                    clear = True

                elif token in self.abbr:
                    trailer.append(self.abbr[token])

                elif token in trailer_seps:
                    trailer_given = True
                    rest = tokens.take_rest()
                    if rest.strip():
                        trailer.append(f'{token} {rest.strip()}')
                    break

                elif re.match(r'[Tt]\d+', token):
                    like_words.extend(unroll_refs(f'${token}'))

                elif re.match(r'[Bb]\d+', token):
                    unlike_words.extend(unroll_refs(f'${token}'))

                elif token.startswith('+') and len(token) > 1:
                    token = rec(token[1:], ref, quoted, just)
                    if token: like_words.append(token)
                    else: ui.print(f'! ignoring * token {token}')

                elif token.startswith('-') and len(token) > 1:
                    token = rec(token[1:], ref, quoted, just)
                    if token: unlike_words.append(token)
                    else: ui.print(f'! ignoring * token {token}')

                else:
                    like_tok = rec(token, ref, quoted)
                    if like_tok:
                        like_words.append(like_tok)
                        continue
                    rel = token if not rel else f'{rel} {token}'

        # TODO allow user to override kind via token loop above

        if not cp:
            cp = ChatPrompt(kind=self.lang)

        elif count is None:
            nr = cp.num_refs
            per = math.ceil(cp.count / nr if nr > 0 else 5)
            n = len(like_words) + len(unlike_words)
            count = per * n


        np = cp.rebuild(
            count=count,
            rel=rel,
            like=like_words,
            unlike=unlike_words,
            trailer=trailer if trailer or trailer_given else None,
        )

        return clear, np

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

        if self.last_chat_role == 'user':
            ui.print('// last chat prompt aborted; restart with `.`')

        with self.prompt(ui, '? ') as tokens:
            if tokens.empty:
                if self.attempt == 0 and not self.chat:
                    return self.generate(ui)
                return

            if tokens.peek('').startswith('!'):
                token = next(tokens)
                try:
                    abbr = self.abbr[token]
                except KeyError:
                    ui.print(f'! no such abbr {token!r} ; use /abbr to correct or define new')
                else:
                    return self.chat_prompt(ui, abbr)
                return

            if tokens.peek('').startswith('*'):
                return self.generate(ui)

            if tokens.have(r'_$'):
                return self.chat_prompt(ui, '_') # TODO can this be an abbr?

            if tokens.have(r'\.$'):
                return self.chat_prompt(ui, '.') # TODO can this be an abbr?

            if tokens.peek('').startswith('/'):
                return self.do_cmd(ui)

            match = tokens.have(word_ref_pattern)
            if match:
                return self.ref_word(ui, match)

            # TODO can '> ...' lambda ctx ... be an abbr?
            match = re.match(r'(>+)\s*(.+?)$', tokens.raw)
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

            return self.attempt_word(ui, next(tokens).lower(), f'entered')

    def ref_word(self, ui: PromptUI, match: re.Match[str]):
        refs = list(word_match_refs(match))

        with ui.tokens as tokens:
            if len(refs) == 1:
                some = False
                score: float|None = None
                prog: int|None = None

                for token in tokens:
                    if 'score'.startswith(token.lower()):
                        token = next(tokens)
                        try:
                            score = float(token)
                            assert score_min <= score <= score_max
                        except ValueError:
                            ui.print(f'! invalid word score: not a float {token!r}')
                            return
                        except AssertionError:
                            ui.print(f'! invalid word score, must be in range {score_min} <= {score_max}')
                            return
                        some = True

                    if 'prog'.startswith(token.lower()):
                        token = next(tokens)
                        if token == '_':
                            prog = None
                        else:
                            try:
                                prog = int(token)
                                assert prog_min <= prog <= prog_max
                            except ValueError:
                                ui.print('! invalid word prog‰, not an int {token!r}')
                                return
                            except AssertionError:
                                ui.print(f'! invalid word prog‰, must be in range {prog_min} <= {prog_max}')
                                return
                        some = True

                if some:
                    i, _, _ = self.word_iref(*refs[0])
                    res = 'amended' if self.fix(ui, i, score, prog) else 'no change'
                    ui.print(f'💿 {self.describe_word(i)} ({res})')
                    return

            elif not tokens.empty:
                ui.print('! may only amend a singular word reference')

        for k, n in refs:
            i, ix, _ = self.word_iref(k, n)
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
        elif i in self.prog:
            del self.prog[i]
            parts.append(f'prog:_')

        if not parts: return False

        ui.log(f'fix attempt_{i}: {' '.join(parts)}')
        return True

    def record(self, ui: PromptUI, word: str, score: float, prog: int|None):
        if word in self.wordbad:
            self.wordbad.remove(word)

        if word in self.wordgood:
            # TODO nicer to update, believe the user
            ui.print(f'! ignoring duplicate response for word "{word}"')
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

    @property
    def chat_extract_desc(self):
        desc = self.chat_extract_from
        info = [*self.chat_extract_info]
        info.append(f'found:{self.extracted}')
        if self.extracted_bad: info.append(f'rejects:{self.extracted_bad}')
        if self.extracted_good: info.append(f'prior:{self.extracted_good}')
        if info: desc = f'{desc} ({" ".join(info)})'
        return desc

    def role_history(self, role: str) -> Generator[tuple[int, int, str]]:
        for j, content in enumerate(role_content(reversed(self.chat), role)):
            yield 0, j, content
        for i, h in enumerate(reversed(self.chat_history), 1):
            for j, content in enumerate(role_content(reversed(h.chat), role)):
                yield i, j, content

    def count_role_history(self, role: str):
        hn = sum(
            sum(1 for _ in role_content(h.chat, role))
            for h in self.chat_history)
        sn = len(self.chat_history)
        if self.chat:
            hn += sum(1 for _ in role_content(self.chat, role))
            sn += 1
        return sn, hn

    @overload
    def filter_words(self, it: Iterable[str]) -> Generator[str]:
        pass

    @overload
    def filter_words[V](self,
                        it: Iterable[V],
                        key: Callable[[V], str]) -> Generator[V]:
        pass

    def filter_words[V](self,
                        it: Iterable[V],
                        key: None|Callable[[V], str] = None) -> Generator[V]:
        seen: set[str] = set()
        for val in it:
            word = key(val) if key else cast(str, val)
            if len(word) < self.min_word_len: continue
            word = word.lower()
            if word in seen: continue
            seen.add(word)
            yield val

    def chat_extract_words(self) -> Generator[str]:
        self.extracted = 0
        self.extracted_good = 0
        self.extracted_bad = 0

        for _i, _j, _n, word in self.filter_words(
            self.chat_extract_word_matchs(),
            key = lambda ijn_word: ijn_word[3]):

            word = word.lower()
            self.extracted += 1
            if word in self.wordbad:
                self.extracted_bad += 1
                continue
            if word in self.wordgood:
                self.extracted_good += 1
                continue
            yield word

    def chat_extract_word_matchs(self) -> Generator[tuple[int, int, int, str]]:
        if self.chat_extract_scav:
            self.chat_extract_from = 'chat history'
            sn, hn = self.count_role_history('assistant')
            self.chat_extract_info = [f'replies:{hn}', f'sessions:{sn}']
            yield from (
                (i, j, n, word)
                for i, j, reply in self.role_history('assistant')
                for line in spliterate(reply, '\n', trim=True)
                for n, word in find_match_words(line))

        else:
            self.chat_extract_from = 'last chat reply'
            self.chat_extract_info = []
            reply = next(role_content(reversed(self.chat), 'assistant'), None)
            if reply: yield from (
                (0, 0, n, word)
                for line in spliterate(reply, '\n', trim=True)
                for n, word in find_match_words(line))

    def describe_extracted_word(self, word: str):
        iw = len(str(len(self.word)))+1
        ww = max(len(word) for word in self.word)
        lpad = ' '*(2*iw + 1)
        mpad = ' '*(7 + 2)

        if word in self.wordbad:
            return f'{lpad} {word:{ww}} {mpad} ❌'

        if word in self.wordgood:
            return self.describe_word(self.wordgood[word])

        return f'{lpad} {word:{ww}} {mpad} 🤔'

    def chat_extract_list(self, ui: PromptUI):
        last_chat_i: int|None = None
        last_rep_i: int|None = None
        cw = len(str(len(self.chat_history)))
        rw = max(len(str(len(h.chat))) for h in self.chat_history)

        for chat_i, rep_i, n, word in self.filter_words(
            self.chat_extract_word_matchs(),
            key = lambda ijn_word: ijn_word[3]):

            cee = ' ' * (cw+1)
            if last_chat_i != chat_i:
                last_chat_i = chat_i
                last_rep_i = None
                cee = (f'C{chat_i:<{cw}}')

            ree = ' ' * (rw+1)
            if last_rep_i != rep_i:
                last_rep_i = rep_i
                ree = f'R{rep_i:<{rw}}'

            word = word.lower()
            desc = self.describe_extracted_word(word)
            ui.print(f'{cee} {ree} {n:>2}. {desc}')

    def attempt_word(self, ui: PromptUI, word: str, desc: str) -> PromptUI.State|None:
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
            return self.attempt_score_word(ui, word, desc)

    def attempt_score_word(self, ui: PromptUI, word: str, desc: str) -> PromptUI.State|None:
        orig_desc = desc
        desc = f'🤔 {desc} #{self.attempt+1} "{word}"'

        while True:
            with ui.tokens_or(f'{desc} score? ') as tokens:
                if tokens.empty: return

                tok = tokens.peek('')
                if len(tok) == 2:
                    if tok[0] == ':':
                        sep = next(tokens)[1]
                        i = word.find(sep)
                        if i < 0:
                            ui.print(f'! no {sep!r} separator in {word!r}')
                            return
                        ui.print(f'// split {word} :{sep}')
                        return self.attempt_word(ui, word[:i], f'{orig_desc}:{sep}')

                    if tok[1] == ':':
                        sep = next(tokens)[0]
                        i = word.find(sep)
                        if i < 0:
                            ui.print(f'! no {sep!r} separator in {word!r}')
                            return
                        ui.print(f'// split {word} {sep}:')
                        return self.attempt_word(ui, word[i+1:], f'{orig_desc}{sep}:')

                if tok.startswith('!'):
                    token = next(tokens)
                    self.reject(ui, word)
                    ui.print(f'// rejected {desc}')
                    token = token[1:] or next(tokens, '')
                    if token:
                        return self.attempt_word(ui, token, "corrected")
                    return

                try:
                    score = float(next(tokens))
                except ValueError:
                    ui.print('! invalid word score: not a float')
                    tokens.raw = ''
                    continue

                if not (score_min <= score <= score_max):
                    ui.print(f'! invalid word score, must be in range {score_min} <= {score_max}')
                    tokens.raw = ''
                    continue

                desc = f'{desc} {score:.2f}°C'

                prog_req = False
                if self.prog_at is not None:
                    prog_req = score >= self.prog_at
                elif self.prog:
                    i = self.min_prog[0]
                    prog_req = score >= self.score[i]

                if prog_req or not tokens.empty:
                    return self.attempt_prog_word(ui, word, desc, score, prog_req)

                break

        i = self.record(ui, word, score, None)
        if i is not None:
            ui.print(f'💿 {self.describe_word(i)}')

        if self.found: return self.finish

    def attempt_prog_word(self,
                          ui: PromptUI,
                          word: str,
                          desc: str,
                          score: float,
                          prog_req: bool,
                          ) -> PromptUI.State|None:
        prog: int|None = None

        while True:
            with (
                ui.tokens_or(f'{desc} prog‰ ? ') if prog_req else ui.tokens
            ) as tokens:
                if not tokens.empty:
                    try:
                        prog = int(next(tokens))
                    except ValueError:
                        ui.print(f'! invalid word prog‰, not an int')
                        tokens.raw = ''
                        continue

                    if not (prog_min <= prog <= prog_max):
                        ui.print(f'! invalid word prog‰, must be in range {prog_min} <= {prog_max}')
                        tokens.raw = ''
                        continue

                    break
                elif not prog_req:
                    break

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

        assert_never(k)

    def word_ref(self, k: WordRef, n: int):
        if k == '$':
            ix = n - 1
            i = self.index[ix]
            return f'"{self.word[i]}"'

        elif k == '#':
            i = n - 1
            return f'"{self.word[i]}"'

        assert_never(k)

    def collect_word_ref(self, k: WordRef, n: int):
        word = self.word_ref(k, n)
        self.last_chat_basis.add(word)
        return word

    def set_chat_prompt(self, ui: PromptUI, prompt: str|ChatPrompt):
        if isinstance(prompt, str) and prompt == '_':
            ui.log('chat_prompt: _')
            prompt = self.last_chat_prompt
        elif isinstance(prompt, ChatPrompt):
            ui.log(f'chat_prompt: {prompt.prompt}')
        else:
            ui.log(f'chat_prompt: {prompt}')
            try:
                prompt = ChatPrompt(prompt)
            except ValueError:
                pass

        self.last_chat_prompt = prompt
        self.last_chat_basis = set()
        return expand_word_refs(
            prompt if isinstance(prompt, str) else prompt.prompt,
            self.collect_word_ref)

    def chat_prompt(self, ui: PromptUI, prompt: str) -> PromptUI.State|None:
        with ui.catch_state(KeyboardInterrupt, self.ideate):
            # TODO do we tokenize and abbr-expand prompt here or in set_chat_prompt?

            # TODO can this be an abbr?
            if prompt == '.':
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

            for line in wraplines(ui.screen_cols-4, prompt.splitlines()):
                ui.print(f'>>> {line}')

            # TODO wrapped writer
            # TODO tee content into a word scanner

            ui.write('... ')
            for _, content in self.chat_say(ui, prompt):
                a, sep, b = content.partition('\n')
                ui.write(a)
                while sep:
                    end = sep
                    a, sep, b = b.partition('\n')
                    ui.write(f'{end}... {a}')
            ui.fin()

            self.chat_extract_scav = False
            if any(self.chat_extract_words()):
                return self.chat_extract

            ui.print(f'// No new words extracted from {self.chat_extract_desc}')

    def chat_say(self, ui: PromptUI, prompt: str):
        if self.last_chat_tup != ('user', prompt):
            self.chat_append(ui, {'role': 'user', 'content': prompt})

        # TODO with-pending-append-partial

        parts: list[str] = []

        for resp in self.llm_client.chat(model=self.llm_model, messages=self.chat, stream=True):
            with ui.print_exception(Exception,
                                    extra = lambda ui: ui.print(f'\n! ollama response: {json.dumps(resp)}')):
                mess = cast(object, resp['message'] )
                assert isinstance(mess, dict)
                # TODO validate mess : ollama.Message
                mess = cast(ollama.Message, cast(object, mess))

            # TODO care about resp['done'] / resp['done_reason'] ?

            try:
                role = mess['role']
                assert isinstance(role, str)
                if role != 'assistant':
                    # TODO note?
                    continue

                content = mess.get('content')
                if content is None:
                    # TODO note?
                    continue

                parts.append(content)

                yield role, content

            except:
                ui.print(f'\n! {mess!r}')
                raise

        self.chat_append(ui, {'role': 'assistant', 'content': ''.join(parts)})

    def chat_clear(self, ui: PromptUI):
        ui.log(f'session clear')
        if self.chat:
            self.chat_history.append(ChatSession(self.chat, model=self.llm_model))
        self.chat = []

    def chat_pop(self, ui: PromptUI):
        mess = self.chat.pop()
        ui.log(f'session: pop')
        return mess

    def chat_append(self, ui: PromptUI, mess: ollama.Message):
        ui.log(f'session: {json.dumps(mess)}')
        self.chat.append(mess)

    def chat_stats(self):
        role_counts = Counter(mess['role'] for mess in self.chat)
        token_count = sum(
            count_tokens(mess.get('content', ''))
            for mess in self.chat)
        user_count = role_counts.pop("user", 0)
        assistant_count = role_counts.pop("assistant", 0)
        return ChatStats(token_count, user_count, assistant_count)

    @property
    def last_chat_role(self):
        return self.chat[-1]['role'] if self.chat else ''

    @property
    def last_chat_tup(self):
        last = self.chat[-1] if self.chat else None
        if not last: return (None, None)
        return (last['role'], last.get('content'))

    def note_chat_basis_change(self, ui: PromptUI):
        if isinstance(self.last_chat_prompt, ChatPrompt):
            basis = set(self.word_ref(k, n) for k, n in self.last_chat_prompt.refs())
            diffa = basis.difference(self.last_chat_basis)
            diffb = self.last_chat_basis.difference(basis)
            parts: list[str] = []
            if diffb: parts.append(f'💤 {' '.join(sorted(diffb))}')
            if diffa: parts.append(f'🛜 {' '.join(sorted(diffa))}')
            if parts: ui.print(f'🫧 basis changed {' '.join(parts)}')

    def chat_extract(self, ui: PromptUI) -> PromptUI.State | None:
        with ui.catch_state(KeyboardInterrupt, self.ideate):
            self.chat_extract_scav = False
            do_all = False
            do_list = False

            with ui.tokens as tokens:
                for token in tokens:
                    token = token.lower()
                    if token == 'all':
                        do_all = True
                    elif token == 'ls':
                        do_list = True
                    elif 'scavenge'.startswith(token):
                        self.chat_extract_scav = True
                    else:
                        ui.print(f'! {ui.tokens.raw}')
                        ui.print(f'// Usage: /extract [scavenge] [all|ls]')
                        return

            words = sorted(self.chat_extract_words())

            if do_list:
                self.chat_extract_list(ui)
                return self.ideate

            if not words:
                ui.print(f'// No new words extracted from {self.chat_extract_desc}')
                return self.ideate

            if do_all:
                return self.chat_extract_all

            ui.br()
            ui.print(f'// Extracted {len(words)} new words from {self.chat_extract_desc}')
            iw = len(str(len(words)))
            for i, word in enumerate(words):
                ui.print(f'[{i+1:{iw}}] {word}')

            self.note_chat_basis_change(ui)

            while True:
                with self.prompt(ui, f'extract_') as tokens:
                    if tokens.empty:
                        return self.ideate

                    if tokens.have(r'_$'):
                        return self.chat_prompt(ui, '_')

                    cmd = tokens.have(r'/.+$', lambda m: m[0])
                    if cmd:
                        return self.dispatch_cmd(ui, cmd)

                    if tokens.have(r'\.\.\.$'):
                        return self.chat_extract_all

                    try:
                        n = int(next(tokens))
                    except ValueError:
                        ui.print('! invalid list number, expected integer')
                        continue
                    if not (0 < n <= len(words)):
                        ui.print('! invalid list number, out of range')
                        continue

                    return self.attempt_word(ui, words[n-1], f'extract_{n}/{len(words)}') or self.chat_extract

    def chat_extract_all(self, ui: PromptUI) -> PromptUI.State | None:
        words = sorted(self.chat_extract_words())
        if not words:
            ui.print(f'// No new words extracted from {self.chat_extract_desc}')
            return self.ideate

        with ui.catch_state(KeyboardInterrupt, self.ideate):
            ui.br()
            ui.print(f'// Extracted {len(words)} new words from {self.chat_extract_desc}')
            self.note_chat_basis_change(ui)
            return self.attempt_word(ui, words[0], f'extract_1/{len(words)}')

    def chat_last(self, ui: PromptUI):
        chat = self.chat
        given = False

        with ui.tokens as tokens:
            for token in tokens:
                if given:
                    ui.print(f'! {ui.tokens.raw}')
                    return

                if token == 'pop':
                    try:
                        mess = self.chat_pop(ui)
                    except IndexError:
                        ui.print(f'! no chat messages to pop')
                        return
                    role = mess['role']
                    content = mess.get('content', '')
                    if role == 'user':
                        ui.print(f'popped >>> {content}')
                    elif role == 'assistant':
                        ui.print(f'popped ... 🪙 {count_tokens(content)}')
                    else:
                        ui.print(f'popped [role={role}] {content!r}')
                    return

                try:
                    chat_i = int(token)
                except ValueError:
                    ui.print(f'! {ui.tokens.raw}')
                    return

                given = True

                if chat_i > 0:
                    try:
                        chat = self.chat_history[-chat_i].chat
                    except IndexError:
                        ui.print(f'! no such chat session {chat_i}')
                        return

        if given:
            for mess in chat:
                role = mess['role']
                content = mess.get('content', '')
                if role == 'user':
                    for line in wraplines(ui.screen_cols-4, spliterate(content, '\n', trim=True)):
                        ui.print(f'>>> {line}')
                elif role != 'assistant':
                    continue

                for word in self.filter_words((
                    word.lower()
                    for line in spliterate(content, '\n', trim=True)
                    for _, word in find_match_words(line))):
                    ui.print(self.describe_extracted_word(word))

        else:
            reply = ''
            for mess in chat:
                role = mess['role']
                content = mess.get('content', '')
                if role == 'assistant':
                    reply = content
                elif role == 'user':
                    if reply:
                        ui.print(f'... 🪙 {count_tokens(reply)}')
                        reply = ''
                    for line in wraplines(ui.screen_cols-4, spliterate(content, '\n', trim=True)):
                        ui.print(f'>>> {line}')

            if reply:
                for line in wraplines(ui.screen_cols-4, spliterate(reply, '\n')):
                    ui.print(f'... {line}')

                ext_words = set(
                    word.lower()
                    for line in spliterate(reply, '\n', trim=True)
                    for _n, word in find_match_words(line))

                for i in sorted((
                    self.wordgood[word]
                    for word in ext_words
                    if word in self.wordgood
                ), key=lambda i: self.score[i], reverse=True):
                    word = self.word[i]
                    ui.print(self.describe_extracted_word(word))

            if isinstance(self.last_chat_prompt, ChatPrompt):
                for k, n in self.last_chat_prompt.refs():
                    i, ix, qword = self.word_iref(k, n)
                    desc = self.describe_word(i, ix)
                    mark = '🪨' if qword in self.last_chat_basis else '🔥'
                    ui.print(f'{mark} {desc}')

    def chat_clear_cmd(self, ui: PromptUI):
        ui.print('cleared chat 🪙 = 0')
        self.chat_clear(ui)

    def select_model(self, ui: PromptUI):
        try:
            with ui.tokens as tokens:
                byn: list[str] = []
                while True:
                    if not tokens.empty:
                        mod = ''

                        n = tokens.have(r'\d+$', lambda m: int(m[0]))
                        if n is not None:
                            try:
                                mod = byn[n-1]
                            except IndexError:
                                ui.print(f'! invalid list number')

                        else:
                            mod = next(tokens)

                        if mod:
                            try:
                                mod = olm_find_model(self.llm_client, mod)
                            except RuntimeError:
                                ui.print(f'! unavailable model {mod!r}')
                            else:
                                return mod

                    ui.br()
                    ui.print(f'Available Models:')
                    byn = sorted(get_olm_models(self.llm_client))
                    for i, m in enumerate(byn):
                        mark = '*' if m == self.llm_model else ' '
                        ui.print(f'{i+1}. {mark} {m}')

                    tokens.raw = ui.raw_input('Select model (by name or number)> ')
        except KeyboardInterrupt:
            return

    def chat_model_cmd(self, ui: PromptUI):
        model = self.select_model(ui)
        if not model: return

        self.chat_model(ui, model)

        if len(self.chat) > 0:
            ui.log(f'session clear')
            self.chat = []
            ui.print(f'Using model {self.llm_model!r} ; session cleared')

        else:
            ui.print(f'Using model {self.llm_model!r}')

    def chat_model(self, ui: PromptUI, model: str):
        if self.llm_model != model:
            ui.log(f'session model: {model}')
            self.llm_model = model

### tests

@MarkedSpec.mark('''

    #cemantle
    > <div id="cemantle-summary" style="display:run-in">
    >     <p id="cemantle-day-meter">🧊🧊🧊🧊🧊🧊🧊🧊🧊🧊</p>
    >     <table class="story">
    >         <thead>
    >         <tr><th class="number"><b>‰</b></th><th class="emoji">🌡</th><th class="number"><b>°C</b></th></tr>
    >         </thead>
    >         <tr><td class="number">1000</td><td class="emoji">🥳</td><td class="decimal number">100</td></tr>
    >         <tr><td class="number">999</td><td class="emoji">😱</td><td class="decimal number">60.49</td></tr>
    >         <tr><td class="number">990</td><td class="emoji">🔥</td><td class="decimal number">44.0</td></tr>
    >         <tr><td class="number">900</td><td class="emoji">🥵</td><td class="decimal number">36.51</td></tr>
    >         <tr><td class="number">1</td><td class="emoji">😎</td><td class="decimal number">27.11</td></tr>
    >         <tr><td class="number"></td><td class="emoji">🥶</td><td class="decimal number">0</td></tr>
    >         <tr><td class="number"></td><td class="emoji">🧊</td><td class="decimal number">-100</td></tr>
    >     </table>
    >     <div class="yesterday">
    >     Yesterday’s word was <a id="cemantle-yesterday"><b><u>suite</u></b></a>
    >     </div>
    >     🇫🇷 <a href="https://cemantix.certitudes.org/">cémantix</a>
    > </div>
    - expect: 🥳 100
    - expect: 😱 60.49
    - expect: 🔥 44.0
    - expect: 🥵 36.51
    - expect: 😎 27.11
    - expect: 🥶 0
    - expect: 🧊 -100

    #cemantix
    > <div id="cemantix-summary" style="display:run-in">
    >     <p id="cemantix-day-meter">🧊🧊🧊🧊🧊🧊🧊🧊🧊🧊</p>
    >     <table class="story">
    >         <thead>
    >         <tr><th class="number"><b>‰</b></th><th class="emoji">🌡</th><th class="number"><b>°C</b></th></tr>
    >         </thead>
    >         <tr><td class="number">1000</td><td class="emoji">🥳</td><td class="decimal number">100</td></tr>
    >         <tr><td class="number">999</td><td class="emoji">😱</td><td class="decimal number">59.41</td></tr>
    >         <tr><td class="number">990</td><td class="emoji">🔥</td><td class="decimal number">38.29</td></tr>
    >         <tr><td class="number">900</td><td class="emoji">🥵</td><td class="decimal number">28.51</td></tr>
    >         <tr><td class="number">1</td><td class="emoji">😎</td><td class="decimal number">19.95</td></tr>
    >         <tr><td class="number"></td><td class="emoji">🥶</td><td class="decimal number">0</td></tr>
    >         <tr><td class="number"></td><td class="emoji">🧊</td><td class="decimal number">-100</td></tr>
    >     </table>
    >     <div class="yesterday">
    >     Le mot d’hier était <a id="cemantix-yesterday"><b><u>regret</u></b></a>
    >     </div>
    >     🇺🇸 <a href="https://cemantle.certitudes.org/">cemantle</a>
    > </div>
    - expect: 🥳 100
    - expect: 😱 59.41
    - expect: 🔥 38.29
    - expect: 🥵 28.51
    - expect: 😎 19.95
    - expect: 🥶 0
    - expect: 🧊 -100

''')
def test_scrape_scale_row(spec: MarkedSpec):
    expect: list[tuple[str, float]] = []
    for name, value in spec.props:
        if name == 'expect':
            tier, _, score_str = value.partition(' ')
            score = float(score_str.strip())
            expect.append((tier, score))
        else: raise ValueError(f'unknown test expectation {name}')

    soup = bs4.BeautifulSoup(spec.input, 'html5lib')
    summary = soup.select_one('#cemantle-summary') or soup.select_one('#cemantix-summary')
    assert summary

    have: list[tuple[str, float]] = []
    for row in summary.select('table.story tbody tr'):
        try:
            have.append(scrape_scale_row(row))
        except:
            print(f'! {row}')
            raise
    assert have == expect

@MarkedSpec.mark('''
    > _
    - rebuild: give me 10 words that are not related to each other

    > give me 15 French words that are not related to each other
    - kind: French
    - count: 15
    - rel: that are not related to each other

    > give me 10 French words that are similar to $1 and $2
    - kind: French
    - count: 10
    - rel: that are similar to

    > give me 15 French words that are similar to $1, $2, and $3
    - kind: French
    - count: 15
    - rel: that are similar to
    - clean_rel: similar to
    - neg_rel: that are not similar to

    > give me 10 French words that are related to $1 and $2
    - rel: that are related to
    - clean_rel: related to
    - neg_rel: that are not related to

    > give me 10 French words that are read with $1 and $2
    - rel: that are read with
    - clean_rel: read with
    - neg_rel: that are not read with

    > give me 10 French words that are seen with $1 and $2
    - rel: that are seen with
    - clean_rel: seen with
    - neg_rel: that are not seen with

    > give me 10 words that are not related to each other; do not list any words that you have already listed above.
    - rel: that are not related to each other
    - clean_rel: related to
    - trailer: ; do not list any words that you have already listed above.

    > give me 10 words that are not related to each other; do not list any words that you have already listed above
    - rel: that are not related to each other
    - clean_rel: related to
    - trailer: ; do not list any words that you have already listed above

    // TODO more examples if needed
    // give me 15 French words that are related to $1, $2, $3, $4, and $5
    // give me 15 French words that are related to $1, $2, and $3
    // give me 15 French words that are related to $1, $2, and #123
    // give me 16 French words that are related to $1, $2, $3, and $4
    // give me 20 French words that are related to $1, $2, $3, and $4
    // give me 25 French words that are related to $1, $2, $3, $4, and $5
    // give me 5 French words that are related to $1

    // give me 10 French words that are read with $1 and $2
    // give me 10 French words that are seen with $1 and $2

    // TODO give me 5 French words that are related to $t2
    // TODO give me 15 French words that are related to $t3
    // TODO give me 5 French words that are related to $t3
''')
def test_chat_prompts(spec: MarkedSpec):
    prompt = spec.input
    if prompt == '_': prompt = ''

    expect_rebuild = prompt
    expect_kind: str|None = None
    expect_count: int|None = None
    expect_rel: str|None = None
    expect_clean_rel: str|None = None
    expect_neg_rel: str|None = None
    expect_trailer: str|None = None

    for name, value in spec.props:
        if name == 'rebuild': expect_rebuild = value
        elif name == 'kind': expect_kind = value
        elif name == 'count': expect_count = int(value)
        elif name == 'rel': expect_rel = value
        elif name == 'clean_rel': expect_clean_rel = value
        elif name == 'neg_rel': expect_neg_rel = value
        elif name == 'trailer': expect_trailer = value
        else:
            raise ValueError(f'unknown chat prompt test expectation {name}')

    cp = ChatPrompt(prompt)

    if expect_kind is not None:
        assert cp.kind == expect_kind
    if expect_count is not None:
        assert cp.count == expect_count
    if expect_clean_rel is not None:
        assert cleanse_rel(cp.rel)[1] == expect_clean_rel
    if expect_neg_rel is not None:
        assert phrase_rel(cp.rel, neg=True) == expect_neg_rel
    if expect_rel is not None:
        assert cp.rel == expect_rel
    if expect_trailer is not None:
        assert cp.trailer == expect_trailer

    terms: list[str] =  []
    terms.extend(f'${n}' for n in cp.vars)
    terms.extend(f'#{n}' for n in cp.ords)
    assert cp.rebuild(like=terms) == expect_rebuild

@MarkedSpec.mark('''

    #french_10_rng
    > Here are 10 French words that do not typically appear together:
    >
    > 1. Le fromage (cheese)
    > 2. La bibliothèque (library)
    > 3. L'astronomie (astronomy)
    > 4. Le jardinier (gardener)
    > 5. La cuisine (kitchen)
    > 6. L'hôpital (hospital)
    > 7. La photographie (photography)
    > 8. Le métal (metal)
    > 9. L'école (school)
    > 10. La musique (music)
    >
    > These words are often used in different contexts and do not typically
    > appear together in a single sentence or phrase.
    1. Le fromage
    2. La bibliothèque
    3. L astronomie
    4. Le jardinier
    5. La cuisine
    6. L hôpital
    7. La photographie
    8. Le métal
    9. L école
    10. La musique

    #french_15_t5
    > Here are 15 French words related to "sillon", "fleur", "mille", "papillon", and "manteau":
    >
    > 1. Sillon -> Canapé (a type of sofa)
    > 2. Fleur -> Tournesol (sunflower)
    > 3. Mille -> Milliardaire (billionaire)
    > 4. Papillon -> Papillon (butterfly)
    > 5. Manteau -> Capuche (hood, part of a coat or cape)
    > 6. Sillon -> Chaise longue (long chair, similar to a sofa)
    > 7. Fleur -> Pétale (petal of a flower)
    > 8. Mille -> Milieu (middle, middle-ground)
    > 9. Papillon -> Aile de papillon (wings of a butterfly)
    > 10. Manteau -> Capelet (small cape or hood)
    > 11. Sillon -> Divan (a type of sofa or couch)
    > 12. Fleur -> Fleurs d'oranger (orange blossoms)
    > 13. Mille -> Milliardaire (billionaire)
    > 14. Papillon -> Papillon de Néphésis (a mythological nymph with wings, inspired by butterflies)
    > 15. Manteau -> Écharpe (cloak or mantle)
    >
    > Note: Some of these words may have multiple related meanings or connotations, but I've tried to provide a variety of connections to the given root words.
    1. Sillon Canapé
    2. Fleur Tournesol
    3. Mille Milliardaire
    4. Papillon Papillon
    5. Manteau Capuche
    6. Sillon Chaise longue
    7. Fleur Pétale
    8. Mille Milieu
    9. Papillon Aile de papillon
    10. Manteau Capelet
    11. Sillon Divan
    12. Fleur Fleurs d oranger
    13. Mille Milliardaire
    14. Papillon Papillon de Néphésis
    15. Manteau Écharpe

''')
def test_word_extraction(spec: MarkedSpec):
    expected: list[tuple[int, str]] = []
    for key, value in spec.props:
        if isinstance(key, int):
            expected.extend((key, token) for token in value.split())
        else:
            raise ValueError(f'unknown word extraction test expectation {key}')
    assert [
        nword
        for line in spliterate(spec.input, '\n', trim=True)
        for nword in find_match_words(line.strip())
    ] == expected

@MarkedSpec.mark('''

    #init_10
    > *
    - prompt: give me 10 words that are not related to each other
    - clear: false

    #t3
    > * t3
    - prior: give me 10 words that are not related to each other
    - prompt: give me 15 words that are related to $1, $2, and $3
    - clear: false

    #t3_x9
    > *9 t3
    - prior: give me 10 words that are not related to each other
    - prompt: give me 9 words that are related to $1, $2, and $3
    - clear: false

    #t4_clear
    > *t4 /clear
    - prior: give me 9 words that are related to $1, $2, and $3
    - prompt: give me 12 words that are related to $1, $2, $3, and $4
    - clear: true

    #few_novel
    > * $1 $10 $13 !new
    - prior: give me 8 French words that are related to $1 and $2
    - prompt: give me 12 French words that are related to $1, $10, and $13; do not list any words that you have already listed above
    - clear: false

    #related_t2_novel
    > * related t2 !new
    - prior: give me 5 French words that are not related to $1
    - prompt: give me 10 French words that are related to $1 and $2; do not list any words that you have already listed above
    - clear: false

    #t2_plus6_clear_dot
    > * t2 $6 /clear .
    - prior: give me 10 words that are related to $1 and $2
    - prompt: give me 15 words that are related to $1, $2, and $6
    - clear: true

    #french_seen_with_x9_1_novel
    > *9 seen with $1 !new
    - prior: give me 10 French words that are not related to each other
    - prompt: give me 9 French words that are seen with $1; do not list any words that you have already listed above
    - clear: false

    #..._x15_similar_t3
    > *15 similar t3 // NOTE trailing space before comment was regression cause
    - prior: give me 9 French words that are seen with $1; do not list any words that you have already listed above
    - prompt: give me 15 French words that are similar to $1, $2, and $3; do not list any words that you have already listed above
    - clear: false

''')
def test_gen_prompt(spec: MarkedSpec):
    input = spec.input
    prior = ''
    prompt = ''
    clear = False

    for name, value in spec.props:
        if name == 'prior': prior = value
        elif name == 'prompt': prompt = value
        elif name == 'clear': clear = value.lower().startswith('t')
        else:
            raise ValueError(f'unknown gen prompt test expectation {name}')

    def eof_input(_s: str): raise EOFError
    ui = PromptUI(
        get_input = eof_input,
        sink = lambda s: print('LOG', s),
    )
    ui.tokens.raw = input

    search = Search()
    search.last_chat_prompt = prior
    clear, np = search.build_next_prompt(ui)

    assert clear == clear
    assert np == prompt

### entry point

if __name__ == '__main__':
    Search.main()
