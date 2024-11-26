import re
from collections.abc import Generator, Iterable
from typing import Callable

def replace_sections(
    lines: Iterable[str],
    want: Callable[[str], Iterable[str]|None]
) -> Generator[str]:
    empty = True

    for line in lines:
        line = line.rstrip('\n')

        body = line.startswith('#') and want(line)

        # pass lines from unwanted sections
        if not body:
            yield line
            empty = False if line else True
            continue

        # pass lines from replacement section
        for line in body:
            yield line
            empty = False if line else True

        for line in lines:
            line = line.rstrip('\n')
            if line.startswith('#'):
                if not empty: yield ''
                yield line
                empty = False if line else True
                break

            # else: skip prior section lines

def break_sections(*sections: Iterable[str], br: str = '') -> Generator[str]:
    first = True
    for section in sections:
        if first:
            for _ in section:
                first = False
                yield br
                yield _
                break
        else:
            yield br
        yield from section

def fenceit(it: Iterable[str], start: str = '```', end: str = '```') -> Generator[str]:
    yield start
    yield from it
    yield end

StrSink = Generator[None, str, None]
FenceWanted = tuple[str, str, StrSink] # start_line, end_line, sink
WantFence = Callable[[int, str], FenceWanted|None]

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
