import re
from collections.abc import Generator, Iterable, Iterator
from hashlib import md5
from itertools import chain
from typing import cast, final, overload, Callable

@final
class matcherate:
    def __init__(self, pattern: str|re.Pattern[str], s: str):
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        self.pattern = pattern
        self.rest: str = s

    def __iter__(self):
        return self

    def __next__(self):
        rest = self.rest
        if rest:
            match = self.pattern.match(rest)
            if match:
                head, rest = match.groups()
                self.rest = rest if isinstance(rest, str) else ''
                return head if isinstance(head, str) else ''
            self.rest = rest = ''
        if not rest: raise StopIteration
        return rest

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

def first_indent(first: str):
    match = re.match(r'\s+', first)
    if not match:
        return '', first
    return match.group(0), first[match.end(0):]

def striperate(lines: Iterable[str], pattern: re.Pattern[str]|None = None) -> Generator[str]:
    it = iter(lines)
    if pattern is None:
        first = next(it, None)
        if first is None: return
        indent, first = first_indent(first)
        yield first
        if not indent:
            yield from it
            return
        pattern = re.compile(indent)

    for line in lines:
        match = pattern.match(line)
        yield line[match.end(0):] if match else line

def wraplines(at: int, lines: Iterable[str]):
    for line in lines:
        while len(line) > at:
            i = line.rfind(' ', 0, at)
            if i < 0: i = at
            yield line[:i]
            line = line[i:].lstrip()
        yield line

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

class PeekIter[V]:
    def __init__(self, it: Iterable[V]):
        self.it: Iterator[V] = iter(it)
        self._val: V|None = None

    def reset(self, it: Iterable[V]):
        self.it = iter(it)
        self._val = None

    def __iter__(self):
        return self

    def __next__(self):
        if self._val is not None:
            val = self._val
            self._val = None
            return val
        return next(self.it)

    @property
    def val(self):
        return self._val

    @overload
    def peek(self) -> V|None: pass

    @overload
    def peek(self, default: V) -> V: pass

    def peek(self, default: V|None=None):
        if self._val is None:
            self._val = next(self.it, default)
        return self._val

    # TODO @deprecated('just use next(...)')
    def take(self):
        val = self._val
        if val is None:
            val = next(self.it)
        else:
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

    def consume_until(self, pattern: str|re.Pattern[str], trim: bool = False):
        while True:
            token = self.peek()
            if token is None: return
            match = re.match(pattern, token) if isinstance(pattern, str) else pattern.match(token)
            if match:
                if trim:
                    _ = self.take()
                return
            yield self.take()

class MarkedSpec:
    @classmethod
    def iterlines(cls, spec: str):
        lines = spliterate(spec, '\n', trim=True)
        lines = striperate(lines)
        lines = (
            line
            for line in lines
            if not line.startswith('//'))
        return lines

    @classmethod
    def itersections(cls, spec: str):
        lines = cls.iterlines(spec)
        buffer: list[str] = []
        for line in lines:
            if line:
                buffer.append(line)
            elif buffer:
                yield '\n'.join(buffer)
                buffer.clear()
        if buffer:
            yield '\n'.join(buffer)

    @classmethod
    def iterspecs(cls, spec: str):
        for sec in cls.itersections(spec):
            yield cls(sec)

    id_pattern: re.Pattern[str] = re.compile(r'(?x) \# .+ $')
    input_pattern: re.Pattern[str] = re.compile(r'''(?x)
                                                    >
                                                    (?:
                                                        [ ]?
                                                        ( .*? )
                                                    )?
                                                    $
                                                ''')
    prop_pattern: re.Pattern[str] = re.compile(r'''(?x)
                                                   (?:
                                                       - \s+ ( [^\s]+ ) :
                                                     | ( \d+ ) [.)]
                                                   )
                                                   \s+ ( .+? )
                                                   $
                                               ''')

    prop_end_pattern: re.Pattern[str] = re.compile(r'''(?x)
                                                         - \s+ [^\s]
                                                       | \d+ [.)]
                                                       | $
                                                   ''')

    def __init__(self, spec: str):
        self.spec: str = spec
        self._lines: PeekStr|None = None

    @property
    def speclines(self):
        self._lines = PeekStr(self.iterlines(self.spec))
        return self._lines

    def get_id(self):
        lines = self.speclines
        id = lines.have(self.id_pattern, lambda m: m.group(0))
        if id: return id
        h = md5()
        for line in lines.consume(self.input_pattern, lambda m: cast(str, m.group(1) or '')):
            h.update(line.encode())
        return f'input_md5_{h.hexdigest()}'

    @property
    def id(self):
        return self.get_id()

    @property
    def input(self):
        lines = self.speclines
        for _ in lines.consume(self.id_pattern): pass
        return '\n'.join(lines.consume(self.input_pattern, lambda m: cast(str, m.group(1) or '')))

    @property
    def props(self):
        lines = self.speclines
        for _ in lines.consume(self.id_pattern): pass
        for _ in lines.consume(self.input_pattern): pass
        for match in lines.consume(self.prop_pattern):
            value = cast(str, match.group(3))
            if value == '```':
                first = next(lines)
                indent, first = first_indent(first)
                body = lines.consume_until(f'{indent}```$', trim=True)
                body = striperate(body, re.compile(indent)) if indent else body
                value = '\n'.join(chain((first,), body))
            else:
                value = f'{value}{"\n".join(lines.consume_until(self.prop_end_pattern))}'

            li = cast(str, match.group(1))
            if li:
                yield li, value
                continue

            li = cast(str, match.group(2))
            if li:
                yield int(li), value
                continue

            assert False, 'must have either bullet match $1 (unordered) or $2 (ordered)'

    @property
    def trailer(self):
        for _ in self.props: pass
        assert self._lines
        return self._lines

    def assert_no_trailer(self):
        lines = self.trailer
        if lines.peek() == '': _ = next(lines)
        assert list(lines) == []
