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
from collections.abc import Generator, Iterable, Iterator, Sequence
from dataclasses import dataclass
from dateutil.tz import gettz
from typing import assert_never, cast, final, overload, override, Any, Callable, Literal
from urllib.parse import urlparse

from store import StoredLog, atomic_file, break_sections, git_txn, replace_sections
from ui import PromptUI

def match(pattern: str|re.Pattern[str]):
    if isinstance(pattern, str):
        pattern = re.compile(pattern)
    def decorator[V](extract: Callable[[re.Match[str]], V|None]):
        def matcher(s: str) -> V|None:
            match = pattern.match(s)
            return extract(match) if match else None
        return matcher
    return decorator

def matchgen(pattern: str|re.Pattern[str]):
    if isinstance(pattern, str):
        pattern = re.compile(pattern)
    def decorator[V](extract: Callable[[re.Match[str]], Generator[V]]):
        def matcher(s: str) -> Generator[V]:
            match = pattern.match(s)
            if match: yield from extract(match)
        return matcher
    return decorator

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

def role_content(chat: Iterable[ollama.Message], role: str):
    for mess in chat:
        if mess['role'] != role: continue
        if 'content' not in mess: continue
        yield mess['content']

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
    (?P<term>
        \*\* .+? \*\*
      | \* .+? \*
      | .+?
    ) [\-):]?
    (?P<rest>
        \s+ [\-(] \s* .+
      | \s+ .+
    )?
    $
''')
def find_match_words(match: re.Match[str]):
    ns, term, _rest = match.groups()
    n = int(ns)
    term = cast(str, term).strip('*:)').strip()
    term = re.sub(r'(?x) \( .*? (?: \) | $ )', '', term).strip()
    for word in spliterate(term, ' ', trim=True):
        for token in spliterate(word, "-'"):
            token = token.strip('*:)').strip()
            yield n, token

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

        self.abbr: dict[str, str] = dict()
        self.chat: list[ollama.Message] = []
        self.chat_role_counts: Counter[str] = Counter()
        self.last_chat_prompt: str|ChatPrompt = ''
        self.last_chat_basis: set[str] = set()

        self.min_word_len: int = 2

        self.chat_extract_from: str = ''
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

        # self.abbr['!gim'] = 'give me $count $kind words'
        # self.abbr['!rel'] = 'that are $rel'
        # self.abbr['!fin'] = 'each other' XXX lambda ctx: only if !rel and no refs
        # self.abbr['*'] = '!gim !rel ... !fin' XXX lambda ctx: proc tokens in ...
        self.abbr['!new'] = 'do not list any words that you have already listed above'
        self.abbr['!cont'] = 'keep going'
        self.abbr['!meh'] = 'none of those word are very good'
        self.abbr['!bad'] = 'all of those word are terrible'

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
                try:
                    dat = json.loads(mess) # pyright: ignore[reportAny]
                except json.JSONDecodeError:
                    pass
                else:
                    if isinstance(dat, dict) and 'prompt' in dat:
                        mess = cast(Any, dat['prompt']) # pyright: ignore[reportAny]
                        assert isinstance(mess, str)
                _ = self.set_chat_prompt(ui, mess)
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

        if any(self.chat_extract_words()):
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

        count: int|None = None
        rel: str|None = None
        like_words: list[str] = []
        unlike_words: list[str] = []

        if tokens is None: tokens = PromptUI.Tokens()

        token = tokens.token
        if len(token) > 1 and token[1:] == '?':
            cp = self.last_chat_prompt
            ui.print('last chat prompt:')
            if isinstance(cp, str):
                ui.print(f'> {cp}')
            else:
                ui.print(f'> {cp.prompt}')
            return

        if len(token) > 1:
            try:
                count = int(token[1:])
            except ValueError:
                ui.print('! invalid *<INT>')
                return

        clear = False

        cp = self.last_chat_prompt if isinstance(self.last_chat_prompt, ChatPrompt) else ChatPrompt()

        trailer: list[str] = []
        trailer_given: bool = False

        for token in tokens:
            if len(token) >= 2 and '/clear'.startswith(token): # TODO can this bi an abbr
                clear = True

            elif token in self.abbr:
                trailer.append(self.abbr[token])

            elif token in trailer_seps:
                trailer_given = True
                if tokens.rest.strip():
                    trailer.append(f'{token} {tokens.rest.strip()}')
                break

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

        if count is None:
            nr = cp.num_refs
            per = math.ceil(cp.count / nr if nr > 0 else 5)
            n = len(like_words) + len(unlike_words)
            count = per * n

        if clear: self.chat_clear(ui)

        kind = self.lang # TODO more flexible kind-vs-lang handling

        np = cp.rebuild(
            count=count,
            kind=kind, # TODO more flexible kind-vs-lang handling
            rel=rel,
            like=like_words,
            unlike=unlike_words,
            trailer=trailer if trailer or trailer_given else None,
        )

        return self.chat_prompt(ui, np)

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

        if token in self.abbr:
            return self.chat_prompt(ui, self.abbr[token])

        if token == '_': return self.chat_prompt(ui, '_') # TODO can this be an abbr?
        if token == '.': return self.chat_prompt(ui, '.') # TODO can this be an abbr?

        if token.startswith('/'): return self.do_cmd(ui)

        # TODO can '> ...' lambda ctx ... be an abbr?
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

    @property
    def chat_extract_desc(self):
        desc = self.chat_extract_from
        info: list[str] = []
        info.append(f'found:{self.extracted}')
        if self.extracted_bad: info.append(f'rejects:{self.extracted_bad}')
        if self.extracted_good: info.append(f'prior:{self.extracted_good}')
        if info: desc = f'{desc} ({" ".join(info)})'
        return desc

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

        for _n, word in self.filter_words(
            self.chat_extract_word_matchs(),
            key = lambda n_word: n_word[1]):

            word = word.lower()
            self.extracted += 1
            if word in self.wordbad:
                self.extracted_bad += 1
                continue
            if word in self.wordgood:
                self.extracted_good += 1
                continue
            yield word

    def chat_extract_word_matchs(self) -> Generator[tuple[int, str]]:
        self.chat_extract_from = 'last chat reply'
        reply = next(role_content(reversed(self.chat), 'assistant'), None)
        if reply: yield from (
            (n, word)
            for line in spliterate(reply, '\n', trim=True)
            for n, word in find_match_words(line))

    def chat_extract_list(self, ui: PromptUI):
        for n, word in self.filter_words(
            self.chat_extract_word_matchs(),
            key = lambda n_word: n_word[1]):

            word = word.lower()

            iw = len(str(len(self.word)))+1
            ww = max(len(word) for word in self.word)
            lpad = ' '*(2*iw + 1)
            mpad = ' '*(7 + 2)

            desc = ''
            if word in self.wordbad:
                desc = f'{lpad} {word:{ww}} {mpad} ❌'
            elif word in self.wordgood:
                desc = self.describe_word(self.wordgood[word])
            else:
                desc = f'{lpad} {word:{ww}} {mpad} 🤔'

            ui.print(f'{n}. {desc}')

    def attempt_word(self, ui: PromptUI, word: str, desc: str, tokens: PromptUI.Tokens|None = None) -> PromptUI.State|None:
        if not word: return
        orig_desc = desc

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

                if len(token) == 2:
                    if token[0] == ':':
                        sep = token[1]
                        i = word.find(sep)
                        if i < 0:
                            ui.print(f'! no {sep!r} separator in {word!r}')
                            return
                        ui.print(f'// split {word} :{sep}')
                        return self.attempt_word(ui, word[:i], f'{orig_desc}:{sep}')

                    if token[1] == ':':
                        sep = token[0]
                        i = word.find(sep)
                        if i < 0:
                            ui.print(f'! no {sep!r} separator in {word!r}')
                            return
                        ui.print(f'// split {word} {sep}:')
                        return self.attempt_word(ui, word[i+1:], f'{orig_desc}{sep}:')

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

            if any(self.chat_extract_words()):
                return self.chat_extract

            ui.print(f'// No new words extracted from {self.chat_extract_desc}')

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
            do_all = False
            do_list = False

            for token in (ui.tokens.token, *ui.tokens):
                if not token: break
                token = token.lower()
                if token == 'all':
                    do_all = True
                elif token == 'ls':
                    do_list = True
                else:
                    ui.print(f'! {ui.tokens.raw}')
                    ui.print(f'// Usage: /extract [ls]')
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

        if isinstance(self.last_chat_prompt, ChatPrompt):
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

class PeekIter[V]:
    def __init__(self, it: Iterable[V]):
        self.it: Iterator[V] = iter(it)
        self._val: V|None = None

    def __iter__(self):
        return self

    def __next__(self):
        if self._val is not None:
            val = self._val
            self._val = None
            return val
        return next(self.it)

    def peek(self):
        if self._val is not None:
            return self._val
        val = next(self.it, None)
        self._val = val
        return val

    def take(self):
        val = self._val
        if val is None:
            return next(self.it)
        self._val = None
        return val

class PeekStr(PeekIter[str]):
    @overload
    def have(self, pattern: str|re.Pattern[str]) -> re.Match[str]|None:
        pass

    @overload
    def have[V](self, pattern: str|re.Pattern[str],
                then: Callable[[re.Match[str]], V]) -> V|None:
        pass

    @overload
    def have[V](self, pattern: str|re.Pattern[str],
                then: Callable[[re.Match[str]], V],
                default: V = None) -> V:
        pass

    def have[V](self, pattern: str|re.Pattern[str],
                then: None|Callable[[re.Match[str]], V] = None,
                default: None|V = None):
        token = self.peek()
        if token is None: return default
        match = re.match(pattern, token) if isinstance(pattern, str) else pattern.match(token)
        if match: _ = self.take()
        if then:
            return then(match) if match else default
        return match

    @overload
    def consume(self, pattern: str|re.Pattern[str]) -> Generator[re.Match[str]]:
        pass

    @overload
    def consume[V](self, pattern: str|re.Pattern[str],
                then: Callable[[re.Match[str]], V]) -> Generator[V]:
        pass

    def consume[V](self, pattern: str|re.Pattern[str],
                then: None|Callable[[re.Match[str]], V] = None):
        while True:
            token = self.peek()
            if token is None: return
            match = re.match(pattern, token) if isinstance(pattern, str) else pattern.match(token)
            if not match: return
            _ = self.take()
            yield then(match) if then else match

### tests

import pytest

@dataclass
class ChatPromptTestCase:
    @classmethod
    def mark(cls, spec: str):
        cases = list(cls.parseiter(spec))
        ids = [case.id for case in cases]
        return pytest.mark.parametrize('case', cases, ids=ids)

    @staticmethod
    def peek_or_scan(spec: str|PeekStr):
        if not isinstance(spec, PeekStr):
            lines = (
                s.strip()
                for s in spliterate(spec, '\n', trim = True))
            lines = (
                line
                for line in lines
                if line
                if not line.startswith('//'))
            spec = PeekStr(lines)
        return spec

    @classmethod
    def parseiter(cls, spec: str|PeekStr):
        spec = cls.peek_or_scan(spec)
        try:
            while True:
                yield cls.parse(spec)
        except StopIteration: pass

    @classmethod
    def parse(cls, spec: str|PeekStr):
        spec = cls.peek_or_scan(spec)
        prompt = spec.take()
        if prompt == '_': prompt = ''

        expect_rebuild = spec.have(r'> +(.+)$', lambda match: cast(str, match.group(1)), prompt)

        expect_kind: str|None = None
        expect_count: int|None = None
        expect_rel: str|None = None
        expect_clean_rel: str|None = None
        expect_neg_rel: str|None = None
        expect_trailer: str|None = None

        for name, value in spec.consume(
            r'- +([\w_\-]+): *(.+?)$', lambda match: (
                cast(str, match.group(1)),
                cast(str, match.group(2))
            )
        ):
            if name == 'kind': expect_kind = value
            elif name == 'count': expect_count = int(value)
            elif name == 'rel': expect_rel = value
            elif name == 'clean_rel': expect_clean_rel = value
            elif name == 'neg_rel': expect_neg_rel = value
            elif name == 'trailer': expect_trailer = value
            else:
                raise ValueError(f'unknown chat prompt test expectation {name}')

        return cls(prompt,
                   expect_kind, expect_count, expect_rel,
                   expect_clean_rel, expect_neg_rel,
                   expect_trailer,
                   expect_rebuild)

    prompt: str
    expect_kind: str|None
    expect_count: int|None
    expect_rel: str|None
    expect_clean_rel: str|None
    expect_neg_rel: str|None
    expect_trailer: str|None
    expect_rebuild: str

    @property
    def id(self):
        return f'#{self.prompt.replace(" ", "_")}' if self.prompt else '#empty'

    def check(self, cp: ChatPrompt):
        if self.expect_kind is not None:
            assert cp.kind == self.expect_kind
        if self.expect_count is not None:
            assert cp.count == self.expect_count
        if self.expect_clean_rel is not None:
            assert cleanse_rel(cp.rel)[1] == self.expect_clean_rel
        if self.expect_neg_rel is not None:
            assert phrase_rel(cp.rel, neg=True) == self.expect_neg_rel
        if self.expect_rel is not None:
            assert cp.rel == self.expect_rel
        if self.expect_trailer is not None:
            assert cp.trailer == self.expect_trailer

        terms: list[str] =  []
        terms.extend(f'${n}' for n in cp.vars)
        terms.extend(f'#{n}' for n in cp.ords)
        assert cp.rebuild(like=terms) == self.expect_rebuild

@ChatPromptTestCase.mark('''
    _
    > give me 10 words that are not related to each other

    give me 15 French words that are not related to each other
    - kind: French
    - count: 15
    - rel: that are not related to each other

    give me 10 French words that are similar to $1 and $2
    - kind: French
    - count: 10
    - rel: that are similar to

    give me 15 French words that are similar to $1, $2, and $3
    - kind: French
    - count: 15
    - rel: that are similar to
    - clean_rel: similar to
    - neg_rel: that are not similar to

    give me 10 French words that are related to $1 and $2
    - rel: that are related to
    - clean_rel: related to
    - neg_rel: that are not related to

    give me 10 French words that are read with $1 and $2
    - rel: that are read with
    - clean_rel: read with
    - neg_rel: that are not read with

    give me 10 French words that are seen with $1 and $2
    - rel: that are seen with
    - clean_rel: seen with
    - neg_rel: that are not seen with

    give me 10 words that are not related to each other; do not list any words that you have already listed above.
    - rel: that are not related to each other
    - clean_rel: related to
    - trailer: ; do not list any words that you have already listed above.

    give me 10 words that are not related to each other; do not list any words that you have already listed above
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
def test_chat_prompts(case: ChatPromptTestCase):
    cp = ChatPrompt(case.prompt)
    case.check(cp)

### entry point

if __name__ == '__main__':
    Search.main()
