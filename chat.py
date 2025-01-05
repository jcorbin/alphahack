import json
import ollama
import re

from collections import Counter
from collections.abc import Callable, Generator, Iterable, Sequence
from dataclasses import dataclass
from typing import cast, final

from strkit import spliterate, wraplines
from ui import PromptUI

def get_olm_models(client: ollama.Client) -> Generator[str]:
    # TODO inline
    for model in client.list().models:
        if model.model is not None:
            yield model.model

def count_tokens(s: str):
    return sum(1 for _ in re.finditer(r'[^\s]+', s))

@final
@dataclass
class ChatStats:
    token_count: int
    user_count: int
    assistant_count: int

@dataclass
class ChatSession:
    model: str
    chat: list[ollama.Message]

    @property
    def last(self):
        return self.chat[-1] if self.chat else None

    @property
    def last_role(self):
        mess = self.last
        return mess['role'] if mess else ''

    @property
    def last_reply(self):
        for mess in reversed(self.chat):
            if mess['role'] != 'assistant': continue
            if 'content' not in mess: continue
            return mess['content']
        return ''

    @property
    def stats(self):
        role_counts = Counter(mess['role'] for mess in self.chat)
        token_count = sum(
            count_tokens(mess.get('content', ''))
            for mess in self.chat)
        user_count = role_counts.pop("user", 0)
        assistant_count = role_counts.pop("assistant", 0)
        return ChatStats(token_count, user_count, assistant_count)

    def pairs(self) -> Generator[tuple[str|None, str|None]]:
        rev = reversed(self.chat)
        while True:
            for mess in rev:
                if mess['role'] == 'user':
                    if 'content' not in mess: continue
                    prompt = mess['content']
                    yield prompt, None
                    continue

                if mess['role'] == 'assistant':
                    if 'content' not in mess: continue
                    reply = mess['content']
                    break

            else: break

            for mess in rev:
                if mess['role'] == 'user':
                    if 'content' not in mess: continue
                    prompt = mess['content']
                    yield prompt, reply
                    break
            else:
                yield None, reply
                break

@final
class ChatModelError(ValueError):
    def __init__(self, wanted: str, available: Sequence[str]):
        super().__init__(f'invalid chat model {wanted!r}, available: {" ".join(self.available)}')
        self.wanted = wanted
        self.available = available

from typing import Protocol

class Logger(Protocol):
    def log(self, mess: str) -> None:
        pass

ChatExpander = Callable[[Logger, str], str]

@final
class ChatContext:
    Logger = Logger

    def __init__(self,
                 model: str = '',
                 system: str = '',
                 expand: ChatExpander = lambda _, prompt: prompt
                 ):
        self.client = ollama.Client()
        self.system_prompt: str = system
        self.expand = expand
        self.messages: list[ollama.Message] = []
        self.history: list[ChatSession] = []
        self.wanted_model: str = model
        self._model: str = ''

    @property
    def model(self):
        if not self._model:
            name = self.wanted_model
            available = sorted(get_olm_models(self.client))
            try:
                self._model = next(n for n in available if n.startswith(name))
            except StopIteration:
                raise ChatModelError(name, available)
        return self._model

    @model.setter
    def model(self, model: str):
        if self.wanted_model != model:
            self.wanted_model = model
            self._model = ''

    def load_line(self, line: str):
        match = re.match(r'''(?x)
            system_prompt : \s* (?P<mess> .+ )
            $''', line)
        if match:
            mess, = match.groups()
            try:
                dat = cast(object, json.loads(mess))
            except json.JSONDecodeError:
                pass
            else:
                if isinstance(dat, str):
                    self.system_prompt = dat
            return True

        match = re.match(r'''(?x)
            session \s+ model :
            \s*
            (?P<model> [^\s]+ )
            \s* (?P<rest> .* )
            $''', line)
        if match:
            model, rest = match.groups()
            assert rest == ''
            self.model = model
            return True

        match = re.match(r'''(?x)
            session \s+ clear
            \s* (?P<rest> .* )
            $''', line)
        if match:
            rest, = match.groups()
            assert rest == ''
            self.messages.clear()
            return True

        match = re.match(r'''(?x)
            session : \s* (?P<mess> .+ )
            $''', line)
        if match:
            raw, = match.groups()
            if raw.startswith('pop'):
                if raw != 'pop': raise NotImplementedError(f'chat pop index')
                _ = self.messages.pop()
            else:
                mess = cast(object, json.loads(raw))
                mess = cast(ollama.Message, mess) # TODO validate
                self.messages.append(mess)
            return True

        return False

    def save_system_prompt(self, logger: Logger, system: str):
        self.system_prompt = system
        logger.log(f'system_prompt: {json.dumps(self.system_prompt)}')

    def save_model(self, logger: Logger, model: str):
        self.model = model
        model = self.model
        logger.log(f'session model: {model}')

    def clear(self, logger: Logger):
        if self.messages:
            self.history.append(ChatSession(self.model, self.messages))
        self.messages = []
        logger.log(f'session clear')

    def pop(self, logger: Logger):
        mess = self.messages.pop()
        logger.log(f'session: pop')
        return mess

    def append(self, logger: Logger, mess: ollama.Message):
        logger.log(f'session: {json.dumps(mess)}')
        self.messages.append(mess)

    @property
    def session(self):
        return ChatSession(self.model, self.messages)

    @property
    def sessions(self) -> Generator[ChatSession]:
        yield self.session
        yield from reversed(self.history)

    def count_models(self):
        return Counter(
            h.model if mess['role'] == 'assistant' else mess['role']
            for h in self.sessions
            for mess in h.chat)

    def count_roles(self):
        return Counter(
            mess['role']
            for h in self.sessions
            for mess in h.chat)

    def _is_last(self, prompt: str):
        if not self.messages: return False
        last = self.messages[-1]
        if last['role'] != 'user': return False
        if 'content' not in last: return False
        return last['content'] == prompt

    def chat(self, logger: Logger, prompt: str) -> Generator[str]:
        model = self.model

        if not self.messages and self.system_prompt:
            self.append(logger, {'role': 'system', 'content': self.system_prompt})

        if not self._is_last(prompt):
            self.append(logger, {'role': 'user', 'content': prompt})

        # TODO with-pending-append-partial

        parts: list[str] = []

        for resp in self.client.chat(model=model, messages=self.messages, stream=True):
            resp = cast(ollama.ChatResponse, resp)

            # TODO care about resp['done'] / resp['done_reason'] ?

            mess = resp['message'] 
            role = mess['role']

            if role != 'assistant':
                # TODO note?
                continue

            content = mess.get('content')
            if content is None:
                # TODO note?
                continue

            parts.append(content)

            yield content

        self.append(logger, {'role': 'assistant', 'content': ''.join(parts)})

    def chat_cmd(self, ui: PromptUI):
        if ui.tokens.empty: _ = ui.input('> ')
        prompt = self.input_prompt(ui)
        return self.chat_ui(ui, prompt) if prompt else None

    def input_prompt(self, ui: PromptUI):
        if ui.tokens.have(r'\.$'):
            ui.tokens.rest = ''
            last = next(self.session.pairs(), None)
            if last is None: return None
            lp, _ = last
            return lp

        match = re.match(r'(>+)\s*(.+?)$', ui.tokens.raw)
        if not match:
            return None

        ui.tokens.rest = ''
        mark, rest = match.groups()
        parts: list[str] = [rest]
        if len(mark) > 1:
            while True:
                raw = ui.raw_input(f'{mark} ')
                rest = raw.lstrip('>').lstrip()
                if not rest: break
                parts.append(rest)
        prompt = ' '.join(parts)

        return self.expand(ui, prompt)

    def chat_ui(self, ui: PromptUI, prompt: str|Iterable[str]|None = None):
        if prompt is None:
            prompt = self.input_prompt(ui)
        else:
            if not isinstance(prompt, str):
                prompt = '\n'.join(prompt)
            prompt = self.expand(ui, prompt)

        if not prompt: return False

        for line in wraplines(ui.screen_cols-4, prompt.splitlines()):
            ui.print(f'>>> {line}')

        # TODO wrapped writer
        # TODO tee content into a word scanner

        try:
            for content in self.chat(ui, prompt):
                a, sep, b = content.partition('\n')
                ui.write(a if ui.last == 'write' else f'... {a}')
                while sep:
                    end = sep
                    a, sep, b = b.partition('\n')
                    ui.write(f'{end}... {a}')

        # TODO ollama inspect / config state
        # except ollama.ResponseError as err:
        #     ui.print(f'! ollama error: {err}')

        finally:
            ui.fin()

        return True

    def clear_cmd(self, ui: PromptUI):
        ui.print('cleare chat 🪙 = 0')
        self.clear(ui)

    def system_cmd(self, ui: PromptUI):
        with ui.tokens as tokens:
            if tokens.empty:
                for line in spliterate(self.system_prompt, '\n', trim=True):
                    ui.print(f'[system]> {line}')
            else:
                self.save_system_prompt(ui, tokens.rest)

    def model_cmd(self, ui: PromptUI):
        try:
            self.choose_model(ui)
        except KeyboardInterrupt:
            return

    def choose_model(self, ui: PromptUI):
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
                            self.save_model(ui, mod)
                        except ChatModelError as err:
                            ui.print(f'! {err}')
                        else: break

                ui.br()
                ui.print(f'Available Models:')
                byn = sorted(get_olm_models(self.client))
                mark: Callable[[str], str] = lambda _: ''
                try:
                    mod = self.model
                    mark = lambda s: ' *' if re.fullmatch(mod, s) else ''
                except ChatModelError:
                    mod = self.wanted_model
                    mark = lambda s: ' ?' if re.match(mod, s) else ''
                for i, m in enumerate(byn):
                    ui.print(f'{i+1}. {mark(m)}{m}')

                tokens.raw = ui.raw_input('Select model (by name or number)> ')

        if len(self.messages) > 0:
            self.clear(ui)
            ui.print(f'Using model {self.model!r} ; session cleared')

        else:
            ui.print(f'Using model {self.model!r}')
