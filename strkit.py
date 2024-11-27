import re
from collections.abc import Generator, Iterable, Iterator
from typing import overload, Callable

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

    @overload
    def peek(self) -> V|None: pass

    @overload
    def peek(self, default: V) -> V: pass

    def peek(self, default: V|None=None):
        if self._val is None:
            self._val = next(self.it, default)
        return self._val

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
