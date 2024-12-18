#!/usr/bin/env python

import argparse
import datetime
import json
import math
import re

from collections.abc import Generator, Iterable
from dataclasses import dataclass
from dateutil.tz import gettz
from itertools import chain
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
        self.rank: list[None|int] = []

        self.result_text: str = ''
        self.result: Result|None = None

    @property
    def guesses(self):
        return len(self.words)

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
                try:
                    res = Result.parse(self.result_text)
                except ValueError:
                    self.result = None
                    continue
                self.result = res
                if res.site: self.site = res.site
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
                word :
                \s* " (?P<word> [^"]+ ) "
                \s* (?P<rank> None | -?\d+ )
                $''', rest)
            if match:
                word, rank_str = match.groups()
                rank_str = cast(str, rank_str)
                rank: int|None = None
                if rank_str != 'None':
                    rank = int(rank_str)
                self.words.append(word)
                self.rank.append(rank)
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

            'done': self.finish,

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

        index = list(chain(

            # A ranks
            #     1
            #     2
            #     3
            (i for _, i in sorted(
                (rank, i)
                for i, rank in enumerate(self.rank)
                if rank is not None
                if rank > 0
            )),

            # = rank(s)
            #     0
            (i for i, rank in enumerate(self.rank) if rank == 0),

            # B ranks
            #    -3
            #    -2
            #    -1
            (i for _, i in sorted((
                (-rank, i)
                for i, rank in enumerate(self.rank)
                if rank is not None
                if rank < 0
            ), reverse=True)),

        ))

        yield f'    ⛓️ #0 "{self.top}"'
        for i in index:
            rank = self.rank[i]
            word = self.words[i]
            order = '!' if rank is None else 'A' if rank > 0 else 'B' if rank < 0 else '='
            yield f'    ⛓️ #{i+1} "{word}" {order}'
        yield f'    ⛓️ #{len(self.words)+1} "{self.bottom}"'

    def orient(self, _ui: PromptUI):
        if self.found is not None:
            return self.finish

        return self.ideate

    def generate(self, ui: PromptUI):
        return self.chat_prompt(ui, "I'm looking for a series of words that will connect the meaning of $A to $B.")

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

    def ideate(self, ui: PromptUI) -> PromptUI.State|None:
        if self.found is not None:
            return self.finish

        if self.chat.session.last_role == 'user':
            ui.print('// Last chat prompt interrupted, resume with `.`')
        elif self.chat.session.last_role == 'assistant':
            for line in spliterate(self.chat.session.last_reply, '\n', trim=True):
                ui.print(f'... {line}')

        with self.prompt(ui, '? ') as tokens:
            if not tokens.empty:
                return self.do_ideate(ui)

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

        def extract(self, text: str, tokens: PromptUI.Tokens):
            nth = tokens.have(r'\d+', lambda m: int(m.group(0)))
            if nth is not None:
                self.matches = [
                    word.lower()
                    for line in spliterate(text, '\n')
                    for n, word in find_match_words(line)
                    if n == nth]
            else:
                tok = next(tokens)
                self.matches = [
                    word.lower()
                    for line in spliterate(text, '\n')
                    for _, word in find_match_words(line)
                    if re.match(tok, word) is not None]

        def match(self, ui: PromptUI):
            with self.given as tokens:
                if tokens.empty: return

                word = tokens.have(r'(?x) " ( [^"]+ ) "', lambda m: m.group(0))
                if word is not None:
                    self.word = word
                    return

                if not self.matches:
                    self.extract(self.extract_from, tokens)
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
                if not self.word and not self.given.empty:
                    self.match(ui)

                if not self.word:
                    if self.matches:
                        try:
                            for n, match in enumerate(self.matches, 1):
                                ui.print(f'{n}. {match!r}')
                            self.given = ui.input('select word> ')
                        except KeyboardInterrupt:
                            self.matches.clear()
                    else:
                        for line in spliterate(self.extract_from, '\n', trim=True):
                            ui.print(f'... {line}')
                        self.given = ui.input('match word(s) to extract> ')
                    return

                if self.word in self.search.words: # TODO better lookup?
                    ui.print(f'// "{self.word}" already recorded')
                    return self.search.ideate

                ui.copy(self.word)
                with ui.input(f'📋 "{self.word}" order? ') as tokens:
                    order = tokens.have(r'(?xi) A | B | = | !', lambda m: m.group(0).lower())
                    if order is None:
                        ui.print(f'! must provide "A" "B" "=" or "!" ordering for new word')
                        return
                    return self.search.record(ui, self.word, cast(WordOrder, order.upper()))

    def rankorder(self, order: WordOrder):
        if order == '=':
            return 0
        if order == 'A':
            return len(self.words)+1
        if order == 'B':
            return -(len(self.words)+1)
        return None

    def record(self, ui: PromptUI, word: str, order: WordOrder):
        rank = self.rankorder(order)
        self.words.append(word)
        self.rank.append(rank)
        ui.log(f'word: "{word}" {rank}')
        ui.print(f'💿 "{word}" {order} -> {rank}')
        return self.ideate

    def finish(self, ui: PromptUI):
        if not self.result_text:
            _ = ui.input('Paste share result, then press <Enter>')
            result = ui.paste().strip()
            if not result: return

            ui.log(f'share result: {json.dumps(result)}')
            self.result_text = result

        try:
            res = Result.parse(self.result_text)
        except ValueError as e:
            ui.print(f'! invalid result text: {e}')
            self.result_text = ''
            return

        self.result = res

        if res.site: self.site = res.site

        for line in res.textlines():
            ui.print(f'> {line}')

        if not self.stored:
            raise StopIteration

        return self.review

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

    def chat_prompt(self, ui: PromptUI, prompt: str|None=None) -> PromptUI.State|None:
        # TODO simplify over PromptUI evolution
        with (
            ui.catch_state(KeyboardInterrupt, self.ideate),
            ui.print_exception(Exception, self.ideate)
        ):
            return self.chat.chat_ui(ui, prompt)

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
