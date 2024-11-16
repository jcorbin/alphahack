#!/usr/bin/env python

import math
import re
import sys
from dataclasses import dataclass
from collections.abc import Iterable
from typing import cast, final, TextIO

@final
@dataclass
class Loaded:
    time: float
    wordlist: str
    sig: str
    count: int
    excluded: int

    pattern = re.compile(r'''(?x)
    # loaded 400842 words
    loaded \s+ (?P<count> \d+ ) \s+ words

    # from opentaal-wordlist.txt
    \s+ from \s+ (?P<wordlist> [^\s]+ )
    # 12e5fb5e3c73840b583b30016926d1f63a75e9bf1652a3a6634b2ba7c49ad7be
    \s+ (?P<sig>[^\s]+)

    # (10 words excluded)
    \s* \( \s* (?P<excluded>\d+) \s+ words \s+ excluded \s* \)

    \s*
    $
    ''')

    @classmethod
    def match(cls, t: float, line: str):
        match = cls.pattern.match(line)
        if not match: return None
        count, wordlist, sig, excluded = match.groups()
        return cls(t, wordlist, sig, int(count), int(excluded))

@final
@dataclass
class Questioned:
    time: float
    lo: int
    q: int
    hi: int
    word: str
    resp: str

    pattern = re.compile(r'''(?x)
        # [0 : 98266 : 196598]
        \s* \[ \s*
            (?P<lo> \d+ )
            \s* : \s*
            (?P<q> \d+ )
            \s* : \s*
            (?P<hi> \d+ )
        \s* \]

        # mach?
        \s+
        (?P<word> [^\s]+ )
        \?

        # a
        \s+
        (?P<resp> .* )

        $
    ''')

    @classmethod
    def match(cls, t: float, line: str):
        match = cls.pattern.match(line)
        if not match: return None
        lo, q, hi, word, resp = match.groups()
        canon_resp = resp
        for code in ('after', 'before', 'it'):
            if code.startswith(resp.lower()):
                canon_resp = code
                break
        return cls(t, int(lo), int(q), int(hi), word, canon_resp)

@final
@dataclass
class Prompt:
    time: float
    resp: str

    pattern = re.compile(r'''(?x)
        \s*
        >
        \s*

        (?P<resp> .* )

        $
    ''')

    @classmethod
    def match(cls, t: float, line: str):
        match = cls.pattern.match(line)
        if not match: return None
        (resp,) = match.groups()
        return cls(t, resp)

@final
@dataclass
class Done:
    time: float
    lo: int
    q: int
    hi: int
    i: int
    word: str

    pattern = re.compile(r'''(?x)
        # [351593 : 351592 : 351594]
        \s* \[ \s*
            (?P<lo> \d+ )
            \s* : \s*
            (?P<q> \d+ )
            \s* : \s*
            (?P<hi> \d+ )
        \s* \]

        # <Done>.
        \s+ <Done>\.

        # vanwege
        \s+ (?P<word> [^\s]+ )

        $
    ''')

    @classmethod
    def match(cls, t: float, line: str):
        match = cls.pattern.match(line)
        if not match: return None
        lo_s, q_s, hi_s, word = match.groups()
        lo, q, hi = int(lo_s), int(q_s), int(hi_s)
        i = q
        if (i < lo or i >= hi) and hi - lo == 1:
            i = lo
        return cls(t, lo, q, hi, i, word)

@final
class SearchLog:
    pattern = re.compile(r'''(?x)
        T (?P<time> \d+ (?: \. \d+ )? )

        \s*

        (?P<line> .* )

        $
    ''')

    done: Done|None = None
    loaded: Loaded|None = None
    quest: list[Questioned] = []
    prompt: list[Prompt] = []

    def __init__(self, lines: Iterable[str]):
        for line in lines:
            line = line.rstrip('\r\n')

            match = self.pattern.match(line)
            if not match: continue
            time, line = match.groups()
            t = float(time)

            l = Loaded.match(t, line)
            if l is not None:
                if self.loaded is not None:
                    raise ValueError('duplicate loaded line')
                self.loaded = l
                continue

            q = Questioned.match(t, line)
            if q is not None:
                self.quest.append(q)
                continue

            p = Prompt.match(t, line)
            if p is not None:
                self.prompt.append(p)
                continue

            d = Done.match(t, line)
            if d is not None:
                if self.done is not None:
                    raise ValueError('duplicate done line')
                self.done = d
                continue

        self.quest = sorted(self.quest, key = lambda x: x.time)
        self.prompt = sorted(self.prompt, key = lambda x: x.time)

    def merge(self):
        qi = 0
        pi = 0
        while True:
            qr = self.quest[qi] if qi < len(self.quest) else None
            pr = self.prompt[pi] if pi < len(self.prompt) else None

            if qr is not None and pr is not None:
                if qr.time < pr.time:
                    pr = None
                else:
                    qr = None

            if qr is not None:
                qi += 1
                yield qr.time, qr, None
                continue

            if pr is not None:
                pi += 1
                yield pr.time, None, pr
                continue

            break

    def summary(self, legend: bool = True):
        max_ix = max(max(r.lo, r.q, r.hi) for r in self.quest)
        t_width = max(4, max(len(f'{r.time:.1f}') for r in self.quest))
        ix_width = max(5, len(str(max_ix)))
        word_width = max(6, max(len(r.word) for r in self.quest))
        resp_width = max(8, max(len(r.resp) for r in self.quest))

        prior_t = 0

        yield f'T{"time":{t_width}} {"ΔT":>{t_width}} [ {"lo":{ix_width}} : {"query":{ix_width}} : {"hi":{ix_width}} ] {"<word>":{word_width}}? response ... analysis'

        done_i = None if self.done is None else self.done.i
        done_found = False

        for t, qn, pr in self.merge():
            dt = t - prior_t

            if qn is not None:
                if qn.q == done_i: done_found = True

                w = qn.hi - qn.lo
                m = math.floor(qn.hi/2+qn.lo/2)
                b = qn.q - m
                yield f'T{t:{t_width}.1f} {dt:{t_width}.1f} [ {qn.lo:{ix_width}} : {qn.q:{ix_width}} : {qn.hi:{ix_width}} ] {qn.word:{word_width}}? {qn.resp:{resp_width}} ... wid:{w:{ix_width}} mid:{m:{ix_width}} bias:{b}'

            elif pr is not None:
                # TODO extract and report viewing window telemetry
                yield f'T{t:{t_width}.1f} {dt:{t_width}.1f} > {pr.resp}'

            prior_t = t

        if self.done is not None and not done_found:
            dn = self.done
            t = dn.time
            dt = t - prior_t
            yield f'T{t:{t_width}.1f} {dt:{t_width}.1f} [ {dn.lo:{ix_width}} : {dn.i:{ix_width}} : {dn.hi:{ix_width}} ] {dn.word:{word_width-1}} {"<Done>.":{resp_width+2}} ... by exhaustion'
            prior_t = t

        if legend:
            yield ''
            yield 'analysis legend:'
            yield '* wid -- search window width, aka `hi-lo`'
            yield '* mid -- classic binary search midpoint, aka `hi/2+lo/2`'
            yield '* bias -- prefix seeking bias applied, aka `query-mid`'

def analyze(lines: Iterable[str]):
    return SearchLog(lines).summary()

def main():
    import argparse

    parser = argparse.ArgumentParser()
    _ = parser.add_argument('logfile', nargs='?', default=sys.stdin, type=argparse.FileType('r'))
    args = parser.parse_args()

    logfile = cast(TextIO, args.logfile)
    log = SearchLog(logfile)
    for line in log.summary():
        print(line)

if __name__ == '__main__':
    main()
