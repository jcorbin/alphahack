#!/usr/bin/env python

import math
import re
import sys
from dataclasses import dataclass

@dataclass
class Questioned:
    time: float
    lo: int
    q: int
    hi: int
    word: str
    resp: str

    pattern = re.compile(r'''(?x)
        # T4.0846012760011945
        T (?P<time> \d+ (?: \. \d+ )? )

        # [0 : 98266 : 196598]
        \s+ \[ \s*
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
    def match(cls, line):
        match = cls.pattern.match(line)
        if not match: return None
        t, lo, q, hi, word, resp = match.groups()
        canon_resp = resp
        for code in ('after', 'before', 'it'):
            if code.startswith(resp.lower()):
                canon_resp = code
                break
        return cls(float(t), int(lo), int(q), int(hi), word, canon_resp)

@dataclass
class Prompt:
    time: float
    resp: str

    pattern = re.compile(r'''(?x)
        T (?P<time> \d+ (?: \. \d+ )? )

        \s+
        >
        \s*

        (?P<resp> .* )

        $
    ''')

    @classmethod
    def match(cls, line):
        match = cls.pattern.match(line)
        if not match: return None
        t, resp = match.groups()
        return cls(float(t), resp)

def analyze(lines):
    quest = []
    prompt = []

    for line in lines:
        line = line.rstrip('\r\n')

        q = Questioned.match(line)
        if q is not None:
            quest.append(q)
            continue

        p = Prompt.match(line)
        if p is not None:
            prompt.append(p)
            continue

    quest = sorted(quest, key = lambda x: x.time)
    prompt = sorted(prompt, key = lambda x: x.time)

    def merge():
        qi = 0
        pi = 0
        while True:
            qt = quest[qi].time if qi < len(quest) else None
            pt = prompt[pi].time if pi < len(prompt) else None
            if qt is None and pt is None:
                break

            if pt is None or qt <= pt:
                qr = quest[qi]
                qi += 1
                yield qt, qr, None
                continue

            if qt is None or pt < qt:
                pr = prompt[pi]
                pi += 1
                yield pt, None, pr
                continue

            raise RuntimeError('unreachable merge state')

    max_ix = max(max(r.lo, r.q, r.hi) for r in quest)
    t_width = max(4, max(len(f'{r.time:.1f}') for r in quest))
    ix_width = max(5, len(str(max_ix)))
    word_width = max(6, max(len(r.word) for r in quest))
    resp_width = max(8, max(len(r.resp) for r in quest))

    prior_t = 0

    yield f'T{"time":{t_width}} {"ΔT":>{t_width}} [ {"lo":{ix_width}} : {"query":{ix_width}} : {"hi":{ix_width}} ] {"<word>":{word_width}}? response ... analysis'

    for t, qn, pr in merge():
        dt = t - prior_t

        if qn is not None:
            w = qn.hi - qn.lo
            m = math.floor(qn.hi/2+qn.lo/2)
            b = qn.q - m
            yield f'T{t:{t_width}.1f} {dt:{t_width}.1f} [ {qn.lo:{ix_width}} : {qn.q:{ix_width}} : {qn.hi:{ix_width}} ] {qn.word:{word_width}}? {qn.resp:{resp_width}} ... wid:{w:{ix_width}} mid:{m:{ix_width}} bias:{b}'

        elif pr is not None:
            # TODO extract and report viewing window telemetry
            yield f'T{t:{t_width}.1f} {dt:{t_width}.1f} > {pr.resp}'

        prior_t = t

    yield ''
    yield 'analysis legend:'
    yield '* wid -- search window width, aka `hi-lo`'
    yield '* mid -- classic binary search midpoint, aka `hi/2+lo/2`'
    yield '* bias -- prefix seeking bias applied, aka `query-mid`'

if __name__ == '__main__':
    for line in analyze(sys.stdin):
        print(line)
