#!/usr/bin/env python

import argparse
import datetime
import json
import math
import re

from collections.abc import Generator, Iterable, Sequence
from dataclasses import dataclass
from dateutil.tz import gettz
from typing import assert_never, cast, final, override, Callable, Literal, Never

from chat import ChatContext, ChatModelError
from mdkit import break_sections, capture_fences, fenceit
from store import StoredLog
from strkit import matchgen, spliterate, MarkedSpec
from ui import PromptUI

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

def match_word_filter(tokens: PromptUI.Tokens) -> Callable[[int, str], bool]:
    if tokens.have(r'[.*_]'):
        return lambda _n, _w: True

    nth = tokens.have(r'\d+', lambda m: int(m.group(0)))
    if nth is not None:
        return lambda n, _: n == nth

    tok = next(tokens)
    return lambda _, word: re.match(tok, word, re.I) is not None

def extract_words(text: str, tokens: PromptUI.Tokens):
    want = match_word_filter(tokens)
    for line in spliterate(text, '\n'):
        for n, word in find_match_words(line):
            if want(n, word):
                yield word

WordRef = (
    tuple[Literal['$'], str]
  | tuple[Literal['$'], int]
  | tuple[Literal['#'], int]
)

word_ref_pattern = re.compile(r'''(?x)
                                \$ ( [a-zA-Z]+ [\w_]* )
                              | \$ ( -? \d+ )
                              | \# ( \d+ )
                              ''')

WordDeref = Callable[[WordRef], str]

WordOrder = Literal['A', 'B', '=', '!']
WordRank = int|Literal[False]|None

def parse_wordrank(s: str) -> WordRank:
    if s == 'False': return False
    if s == 'None': return None
    return int(s)

def word_refs(s: str) -> Generator[WordRef]:
    for match in word_ref_pattern.finditer(s):
        yield word_match_ref(match)

def word_match_ref(match: re.Match[str]) -> WordRef:
    var, varn, ordn = match.groups()
    if var: return '$', cast(str, var)
    elif varn: return '$', int(varn)
    elif ordn: return '#', int(ordn)
    else: raise RuntimeError('invalid word ref match')

def expand_word_refs(s: str, deref: WordDeref):
    return word_ref_pattern.sub(lambda match: deref(word_match_ref(match)), s)

@final
class Search(StoredLog):
    log_file: str = 'wordchain.log'
    default_site: str = 'https://wordnerd.co/wordchain'
    site_name: str = 'wordnerd.co chain'

    default_chat_model: str = 'llama'
    default_system_prompt: str = 'You are a related word suggestion oracle. When asked to connect two words, you provide a numbered list of word, each related to the next, eventually connecting the two words given by the user.'

    pub_at = datetime.time(hour=0)
    pub_tzname = 'US/Pacific'

    @override
    def add_args(self, parser: argparse.ArgumentParser):
        super().add_args(parser)
        _ = parser.add_argument('--tz', default=self.pub_tzname)
        _ = parser.add_argument('--model', default=self.default_chat_model)

    @override
    def from_args(self, args: argparse.Namespace):
        super().from_args(args)
        self.pub_tzname = cast(str, args.tz)
        self.default_chat_model = cast(str, args.model)

    def __init__(self):
        super().__init__()

        self.chat = ChatContext(expand=self.set_chat_prompt)
        self.last_chat_prompt: str = ''

        # solver state
        self.top: str = ''
        self.bottom: str = ''
        self.words: list[str] = []
        self.rank: list[WordRank] = []
        self.prior_chains: list[tuple[WordRank, ...]] = []
        self.pruning = False

        self.result_text: str = ''
        self._result: Result|None = None

    @property
    def result(self):
        if self._result is None and self.result_text:
            try:
                res = Result.parse(self.result_text)
            except ValueError:
                return None
            self._result = res
        return self._result

    @property
    def prior_words(self) -> Generator[str]:
        yield self.top
        yield self.bottom
        for i, word in enumerate(self.words):
            rank = self.rank[i]
            if rank is not None:
                yield word

    @property
    def guesses(self):
        return self.chain().size

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

    @property
    @override
    def run_done(self):
        return self.result is not None

    @property
    def found(self):
        try:
            return self.rank.index(0)
        except ValueError:
            return None

    @property
    def startup_done(self):
        # TODO not a thing? if not self.puzzle_id: return False
        if not self.top: return False
        if not self.bottom: return False
        return True

    @override
    def startup(self, ui: PromptUI):
        if self.startup_done: return self.orient

        if self.default_chat_model and not self.chat.wanted_model:
            try:
                self.chat.save_model(ui, self.default_chat_model)
            except ChatModelError as err:
                ui.print(f'! {err}')
                self.chat.choose_model(ui)

        if self.default_system_prompt and not self.chat.system_prompt:
            self.chat.save_system_prompt(ui, self.default_system_prompt)

        if not self.top:
            with ui.input('first word? ') as tokens:
                try:
                    self.top = next(tokens)
                except StopIteration: return

        if not self.bottom:
            with ui.input('last word? ') as tokens:
                try:
                    self.bottom = next(tokens)
                except StopIteration: return

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
            if self.chat.load_line(rest): continue

            match = re.match(r'''(?x)
                chat_prompt : \s* (?P<mess> .+ )
                $''', rest)
            if match:
                mess = match.group(1)
                _ = self.set_chat_prompt(ui, mess)
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
                res = self.result
                if res and res.site: self.site = res.site
                continue

            match = re.match(r'''(?x)
                (?P<init> first | last )
                \s+ word \?
                \s+ (?P<word> [^\s]+ )
                $''', rest)
            if match:
                init, word = match.groups()
                if init == 'first': self.top = word
                elif init == 'last': self.bottom = word
                else: assert_never(cast(Never, init))
                continue

            match = re.match(r'''(?x)
                (?: word : \s* " (?P<word> [^"]+ ) "
                  | rank \s+ (?P<index> \d+ )
                  )
                \s+ (?P<rank> -?\d+ | False | None )
                $''', rest)
            if match:
                word, i_str, rank_str = match.groups()
                rank = parse_wordrank(rank_str)
                if word is not None:
                    _ = self.append(ui, word, rank)
                elif i_str is not None:
                    self.score(ui, int(i_str), rank)
                else: raise RuntimeError('invalid word/rank match')
                continue

            match = re.match(r'''(?x)
                reset
                $''', rest)
            if match:
                self.reset(ui)
                continue

            match = re.match(r'''(?x)
                pop
                \s+ (?P<top> top | bot )
                \s+ " (?P<word> [^"]+ ) " 
                $''', rest)
            if match:
                top, word = match.groups()
                res = self.pop(ui, top == 'top')
                assert res is not None
                _, rword, _ = res
                assert word == rword
                continue

            yield t, rest

    @override
    def info(self):
        yield f'📜 {len(self.sessions)} sessions'
        yield f'🫧 {sum(1 for _ in self.chat.sessions)} chat sessions'
        chat_counts = self.chat.count_models()
        user = chat_counts.get("user", 0)
        if user: yield f'⁉️ {user} chat prompts'
        for role, count in chat_counts.items():
            if role in ('user', 'system'): continue
            if count: yield f'🤖 {count} {role} replies'

    def meta(self):
        if self.today is not None: yield f'📆 {self.today:%Y-%m-%d}'
        if self.site: yield f'🔗 {self.site}'
        if self.puzzle_id: yield f'🧩 {self.puzzle_id}'

    def describe_result(self, ui: PromptUI) -> Generator[str]:
        yield f'🤔 {self.guesses} guesses'
        if self.result:
            yield from self.result.describe()
        elif self.result_text:
            yield from spliterate(self.result_text, '\n', trim=True)
        else:
            yield '😦 No result'
        elapsed = self.elapsed + datetime.timedelta(seconds=ui.time.now)
        yield f'⏱️ {elapsed}'

    def do_cmd(self, ui: PromptUI):
        with ui.tokens_or('> '):
            cmd = next(ui.tokens, None)
            if cmd:
                return self.dispatch_cmd(ui, cmd)

    def dispatch_cmd(self, ui: PromptUI, token: str):
        cmds: dict[str, PromptUI.State] = {
            # TODO proper help command ; reuse for '?' token
            # TODO add '/' prefix here ; generalize dispatch

            'site': self.do_site,
            'puzzle': self.do_puzzle,
            'result': self.show_result,
            'report': self.do_report,

            'show': self.do_show,
            'prune': self.do_prune,
            'done': self.finish,
            'reset': self.do_reset,
            'last': self.do_last,

            'clear': self.chat.clear_cmd,
            'model': self.chat.model_cmd,
            'system': self.chat.system_cmd,
            # TODO chat history
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

    def do_puzzle(self, ui: PromptUI):
        with ui.input(f'🧩 {self.puzzle_id} ? ') as tokens:
            if tokens.peek():
                ps = tokens.have(r'#\d+$', lambda m: m[0])
                if not ps:
                    ui.print('! puzzle_id must be like #<NUMBER>')
                    return
                ui.log(f'puzzle_id: {ps}')
                self.puzzle_id = ps

    def show_result(self, ui: PromptUI):
        ui.br()
        for line in capture_fences(
            break_sections(
                self.meta(),
                fenceit(self.describe_result(ui)),
                self.info()),
            lambda i, _: ('```📋', '```', ui.consume_copy()) if i == 0 else None
        ): ui.print(line)

    def do_show(self, ui: PromptUI):
        with ui.tokens as tokens:
            id = tokens.have(r'\d+$', lambda m: int(m.group(0)))
            if id is not None:
                chain = self.chain(id)
                ui.print(f'#{id} {chain.size} added words:')
                for line in chain.show(self):
                    ui.print(f'⛓️ {line}')
                return self.ideate

            chains = list(self.chains())
            sw = len(str(max(chain.size for chain in chains)))
            ui.print('Chains:')
            for chain in chains:
                mark = '🥳' if chain.complete else '😦'
                ui.print(f'{chain.id} {mark} {chain.size:{sw}} added words')
            return self.ideate

    @property
    @override
    def report_desc(self) -> str:
        count = self.result.count if self.result else 0 # FIXME known so far
        status = '🥳' if self.result else '😦'
        return f'{status} ⛓️ {count} 🤔 {self.guesses} ⏱️ {self.elapsed}'

    @property
    @override
    def report_body(self) -> Generator[str]:
        yield from self.info()
        yield ''

        # if self.result:
        #     yield from self.result.textlines()
        # else:
        #     yield f'😦 {self.guesses}'

        chain = self.chain()
        for line in chain.show(self):
            yield f'    ⛓️ {line}'

    def orient(self, _ui: PromptUI):
        if self.found is not None:
            return self.finish

        return self.ideate

    def generate(self, ui: PromptUI):
        def prompt():
            yield 'Give me a series of words that connects the meaning of $A to $B.'

        return self.chat_prompt(ui, prompt())

    def prompt_parts(self):
        stats = self.chat.session.stats
        if stats.token_count > 0:
            yield f'🤖 {stats.assistant_count}'
            yield f'🫧 {stats.user_count}'
            yield f'🪙 {stats.token_count}'
        yield f'{self.word_a()} ⛓️ {self.word_b()}'
        yield f'#{self.guesses}'

    def write_prompt(self, ui: PromptUI):
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
        if last: ui.write(f'{last} ')

    def prompt(self, ui: PromptUI, prompt: str):
        self.write_prompt(ui)
        return ui.input(f'{prompt}')

    def ideate(self, ui: PromptUI):
        if self.found is not None:
            return self.finish

        if self.chat.session.last_role == 'user':
            ui.print('// Last chat prompt interrupted, resume with `.`')

        with self.prompt(ui, '? ') as tokens:
            if not tokens.empty:
                return self.do_ideate(ui)

    def do_last(self, ui: PromptUI):
        last = next(self.chat.session.pairs(), None)
        if last is not None:
            prompt, reply = last
            if prompt is not None:
                if '\n' in prompt:
                    for line in spliterate(prompt, '\n', trim=True):
                        ui.print(f'>>> {prompt}')
                else:
                    ui.print(f'> {prompt}')
            if reply is not None:
                for line in spliterate(reply, '\n', trim=True):
                    ui.print(f'... {line}')
        return self.ideate

    def do_ideate(self, ui: PromptUI) -> PromptUI.State|None:
        with ui.tokens as tokens:
            if tokens.peek('').startswith('/'):
                return self.do_cmd(ui)
            if tokens.peek('').startswith('*'):
                return self.generate(ui)

            match = tokens.have(word_ref_pattern)
            if match:
                ref = word_match_ref(match)
                if tokens.empty:
                    val = self.expand_word_ref(ref)
                    ui.print(f'{val} // word ref: {ref!r}')
                    return

                ix = self.word_ref_index(ref)
                if ix is None:
                    ui.print(f'! not an indexed word')
                    return

                # rank = tokens.have(r'-?\d+', lambda m: int(m.group(1)))
                # if rank is not None:
                #     self.rank[ix] = rank
                #     ui.print(f'// #{ix+1} rank = {rank}')
                # elif tokens.have(r'[_\-]$'):
                #     self.rank[ix] = None
                #     ui.print(f'// #{ix+1} rank = NA')

                return

            st = self.chat_prompt(ui)
            if st: return st

            if not tokens.empty:
                return self.EnterWord(self, tokens.rest)

    @final
    class EnterWord:
        def __init__(self, search: 'Search', given: str):
            self.search = search
            self.given = PromptUI.Tokens(given)
            self.matches: list[str] = []
            self.word: str = ''

        @property
        def extract_from(self):
            return self.search.chat.session.last_reply

        def match(self, ui: PromptUI):
            with self.given as tokens:
                if tokens.empty:
                    return

                word = tokens.have(r'(?x) " ( [^"]+ ) "', lambda m: m.group(1))
                if word is not None:
                    self.word = word
                    return

                if not self.matches:
                    # TODO detect extracted word looping, warn user, guide them to backtrack
                    self.matches = sorted(set(
                        word.lower()
                        for word in extract_words(self.extract_from, tokens)
                    ).difference(self.search.prior_words))
                    if len(self.matches) == 1:
                        self.word = self.matches[0]

                else:
                    nth = tokens.have(r'\d+', lambda m: int(m.group(0)))
                    if nth is not None:
                        ith = nth-1
                        try:
                            self.word = self.matches[ith]
                        except IndexError:
                            ui.print(f'! invalid selection {nth}')

        def __call__(self, ui: PromptUI):
            with ui.catch_state(KeyboardInterrupt, self.search.ideate):
                if not self.word:
                    self.match(ui)

                if not self.word:
                    if self.matches:
                        try:
                            for n, match in enumerate(self.matches, 1):
                                ui.print(f'{n}. {match!r}')
                            self.given.raw = ui.raw_input('select word> ')
                        except KeyboardInterrupt:
                            self.matches.clear()
                    else:
                        for line in spliterate(self.extract_from, '\n', trim=True):
                            ui.print(f'... {line}')
                        self.given = ui.input('match word(s) to extract> ')
                    return

                try:
                    i = self.search.words.index(self.word) # TODO better lookup?
                except ValueError:
                    pass
                else:
                    rank = self.search.rank[i]
                    if rank is not None:
                        ui.print(f'// "{self.word}" already ranked {self.search.chain().mark(i)}')
                        return self.search.ideate

                ui.copy(self.word)
                with ui.input(f'📋 "{self.word}" order? ') as tokens:
                    order = tokens.have(r'(?xi) A | B | = | !', lambda m: m.group(0).lower())
                    if order is None:
                        ui.print(f'! must provide "A" "B" "=" or "!" ordering for new word')
                        return
                    return self.search.record(ui, self.word, cast(WordOrder, order.upper()))

    def rankorder(self, order: WordOrder) -> WordRank:
        if order == '=':
            return 0
        if order == 'A':
            return len(self.words)+1
        if order == 'B':
            return -(len(self.words)+1)
        if order == '!':
            return False
        assert_never(order)

    def chain(self, id: int = 0):
        rank = self.rank if id == 0 else self.prior_chains[-id]
        return self.Chain(f'#{id}', rank)

    def chains(self):
        yield self.chain(0)
        for i in range(len(self.prior_chains)):
            yield self.chain(i + 1)

    @final
    class Chain:
        def __init__(self, id: str, rank: Sequence[WordRank]):
            self.id = id
            self.rank = rank
            self._ix: tuple[tuple[int, int], ...]|None = None

        @property
        def ix(self):
            if self._ix is None:
                self._ix = tuple(
                    (r, i)
                    for i, r in enumerate(self.rank)
                    if r is not None)
            return self._ix

        @property
        def size(self):
            if self._ix is None:
                return sum(1 for r in self.rank if r is not None)
            else:
                return len(self._ix)

        def mark(self, i: int):
            rank = self.rank[i]
            if rank is None: return '_'
            if rank is False: return '!'
            if rank > 0: return 'A'
            if rank < 0: return 'B'
            return '='

        def __iter__(self):
            return self.order()

        def order(self):

            # A ranks
            #     1
            #     2
            #     3
            for _, i in sorted(
                (r, i)
                for r, i in self.ix
                if r > 0):
                yield i

            # = rank(s)
            #     0
            for r, i in self.ix:
                if r == 0:
                    yield i

            # B ranks
            #    -3
            #    -2
            #    -1
            for _, i in sorted((
                (-r, i)
                for r, i in self.ix
                if r < 0
            ), reverse=True):
                yield i

        def show(self, search: 'Search'):
            iw = len(str(self.size))
            ww = max(
                len(search.top),
                len(search.bottom),
                max((len(search.words[i]) for _, i in self.ix), default=0))
            yield f'#{0:{iw}} {search.top:{ww}}'
            for i in self:
                yield f'#{i+1:{iw}} {search.words[i]:{ww}} {self.mark(i)}'
            yield f'#{len(search.words)+1:{iw}} {search.bottom:{ww}}'

    def record(self, ui: PromptUI, word: str, order: WordOrder):
        i: int|None
        try:
            i = self.words.index(word)
        except ValueError:
            i = None

        rank = self.rankorder(order)
        if i is None:
            i = self.append(ui, word, rank)
            ui.print(f'💿🌑 #{i+1} "{word}" {order} -> {rank}')
        else:
            self.score(ui, i, rank)
            ui.print(f'💿🌕 #{i+1} "{word}" {order} -> {rank}')

        return self.ideate

    def do_prune(self, ui: PromptUI):
        with ui.tokens as tokens:
            if tokens.have('t(op?)?$'):
                return self.prune(ui, True)
            if tokens.have('b(o(t(t(om))?)?)?$'):
                return self.prune(ui, False)
            ui.print('! Usage: /prune top | /prune bot')
            return self.ideate

    def prune(self, ui: PromptUI, top: bool):
        res = self.pop(ui, top)
        if res is not None:
            i, word, mark = res
            ui.print(f'🚫 #{i+1} "{word}" {mark}')
        return self.ideate

    def append(self, ui: PromptUI, word: str, rank: WordRank):
        if self.pruning:
            self.pruning = False
        i = len(self.words)
        self.words.append(word)
        self.rank.append(rank)
        ui.log(f'word: "{word}" {rank}')
        return i

    def score(self, ui: PromptUI, i: int, rank: int|None):
        if self.pruning:
            self.pruning = False
        self.rank[i] = rank
        ui.log(f'rank {i} {rank}')

    def reset(self, ui: PromptUI):
        self.pruning = False
        self.prior_chains.append(tuple(self.rank))
        for i in range(len(self.rank)):
            self.rank[i] = None
        ui.log('reset')

    def pop(self, ui: PromptUI, top: bool):
        if not self.rank: return

        if not self.pruning:
            self.pruning = True
            self.prior_chains.append(tuple(self.rank))

        bot = not top
        word: str|None = None
        mark: str = ''

        i = len(self.rank)
        for _ in range(len(self.rank)):
            i -= 1
            rank = self.rank[i]
            if rank is None: continue

            if rank == 0: mark = '='
            elif rank > 0 and top: mark = 'A'
            elif rank < 0 and bot: mark = 'B'
            else: continue

            word = self.words[i]
            self.rank[i] = None
            ui.log(f'pop {"top" if top else "bot"} "{word}"')
            return i, word, mark

    def do_reset(self, ui: PromptUI):
        self.reset(ui)
        ui.print(f'🚫 try again')
        return self.ideate

    def finish(self, ui: PromptUI):
        res = self.result
        if not res:
            # TODO support parsing and reporting feedback about less than ideal solution
            ui.print('Provide result or say `again` to reset and try again.')
            with ui.input('Press <Enter> to 📋, or `>` for line prompt ') as tokens:
                if tokens.have(r'again$'):
                    return self.do_reset(ui)
                self.result_text = ui.may_paste(tokens).strip()
                ui.log(f'share result: {json.dumps(self.result_text)}')
            return

        if res.site: self.site = res.site

        raise StopIteration

    def expand_word_ref(self, ref: WordRef):
        if ref[0] == '#':
            n = ref[1]
            i = n - 1
            try:
                return f'"{self.words[i]}"'
            except IndexError:
                raise ValueError(f'ordinal ref #{n} out of range')

        elif ref[0] == '$':
            n = ref[1]
            if isinstance(n, int):
                try:
                    i = self.rank.index(n) # TODO better reverse index?
                except ValueError:
                    raise ValueError(f'undefined rank ${n}')
                return f'"{self.words[i]}"'

            else:
                try:
                    return self.get_var(n)
                except KeyError:
                    raise ValueError(f'undefined var ${n}')

        else:
            assert_never(ref)

    def word_ref_index(self, ref: WordRef):
        if ref[0] == '#':
            n = ref[1]
            return n - 1
        elif ref[0] == '$':
            n = ref[1]
            if isinstance(n, int):
                return self.rank.index(n) # TODO better reverse index?
            else:
                return self.get_var_index(n)
        else:
            assert_never(ref)

    def word_a_index(self):
        _, i = max(
            (rank, i)
            for i, rank in enumerate(self.rank)
            if rank is not None and rank > 0)
        return i

    def word_b_index(self):
        _, i = max(
            (-rank, i)
            for i, rank in enumerate(self.rank)
            if rank is not None and rank < 0)
        return i

    def word_a(self):
        try:
            i = self.word_a_index()
        except ValueError:
            return f'{self.top}'
        else:
            return f'{self.words[i]}'

    def word_b(self):
        try:
            i = self.word_b_index()
        except ValueError:
            return f'{self.bottom}'
        else:
            return f'{self.words[i]}'

    def get_var(self, name: str) -> str:
        if name == 'top': return f'"{self.top}"'
        if name == 'bottom': return f'"{self.bottom}"'
        if name == 'A': return f'"{self.word_a()}"'
        if name == 'B': return f'"{self.word_b()}"'
        else: raise KeyError(name)

    def get_var_index(self, name: str) -> int|None:
        if name == 'top': return None
        if name == 'bottom': return None
        if name == 'A': return self.word_a_index()
        if name == 'B': return self.word_b_index()
        else: raise KeyError(name)

    def set_chat_prompt(self, logger: ChatContext.Logger, prompt: str):
        if prompt == '_':
            logger.log('chat_prompt: _')
            prompt = self.last_chat_prompt
        else:
            logger.log(f'chat_prompt: {prompt}')
            self.last_chat_prompt = prompt

        return expand_word_refs(prompt, self.expand_word_ref)

    def chat_prompt(self, ui: PromptUI, prompt: str|Iterable[str]|None=None) -> PromptUI.State|None:
        # TODO simplify over PromptUI evolution
        with (
            ui.catch_state(KeyboardInterrupt, self.ideate),
            ui.print_exception(Exception, self.ideate)
        ):
            if self.chat.chat_ui(ui, prompt):
                return self.ideate

@final
@dataclass
class Result:
    site: str
    count: int
    first: str
    last: str

    def describe(self) -> Generator[str]:
        yield f'🔗 {self.site}'
        yield f'⛓️ {self.count} chain words'
        yield f'from {self.first!r} to {self.last!r}'

    def textlines(self):
        yield 'TODO reconstitute result string'
        # yield f'I found #cemantle #{self.puzzle_id} in {self.guesses} guesses!'
        # for i, count in enumerate(reversed(self.counts), start=1):
        #     if count > 0:
        #         n = 1 # TODO how does upstream choose
        #         yield f'{tiers[-i] * n}{make_digit_str(count)}'
        # yield self.link

    @classmethod
    def parse(cls, s: str) -> 'Result':
        site = ''
        count = 0
        first = ''
        last = ''

        for line in spliterate(s, '\n'):
            if not line.strip(): continue

            match = re.match(r'''(?x)
                             🤓 \s* I \s+ solved \s+ today\'s \s+ word \s+ chain
                             \s+ using \s+ (?P<count> \d+ ) \s+ added \s+ words!
                             ''', line)
            if match:
                n = int(match.group(1))
                if count and n != count:
                    raise ValueError('⛓️ count mismatch')
                else:
                    count = n
                continue

            match = re.match(r'''(?x)
                             (?P<first> [^\s]+ )
                             \s+ (?P<links> 🔗+ )
                             \s+ (?P<last> [^\s]+ )
                             ''', line)
            if match:
                first = cast(str, match.group(1))
                links = cast(str, match.group(2))
                last = cast(str, match.group(3))
                if count and len(links) != count:
                    raise ValueError('⛓️ count mismatch')
                else:
                    count = len(links)
                continue

            match = re.match(r'https?://[^\s]+', line)
            if match:
                site = match.group(0)
                continue

            raise ValueError(f'unrecognized line {line!r}')

        return cls(site, count, first, last)

### tests

@MarkedSpec.mark('''

    #first
    > 🤓 I solved today's word chain using 18 added words!
    >
    > extension 🔗🔗🔗🔗🔗🔗🔗🔗🔗🔗🔗🔗🔗🔗🔗🔗🔗🔗 performance
    >
    > https://wordnerd.co/wordchain
    - first: extension
    - last: performance
    - count: 18
    - site: ```
    https://wordnerd.co/wordchain
    ```

''')
def test_result_parse(spec: MarkedSpec):
    res = Result.parse(spec.input)
    for name, value in spec.props:
        if name == 'count': assert f'{res.count}' == value
        elif name == 'first': assert res.first == value
        elif name == 'last': assert res.last == value
        elif name == 'site': assert res.site == value
        else: raise ValueError(f'unknown test expectation {name}')

### entry point

if __name__ == '__main__':
    Search.main()
