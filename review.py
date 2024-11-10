#!/usr/bin/env python

import math
import re
import sys
from dataclasses import dataclass

@dataclass
class Response:
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
        (?P<word> \w+ )
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

def analyze(lines):
    responses = []

    for line in lines:
        line = line.rstrip('\r\n')

        r = Response.match(line)
        if r is not None:
            responses.append(r)
            continue


    max_ix = max(max(r.lo, r.q, r.hi) for r in responses)
    t_width = max(4, max(len(f'{r.time:.1f}') for r in responses))
    ix_width = max(5, len(str(max_ix)))
    word_width = max(6, max(len(r.word) for r in responses))
    resp_width = max(8, max(len(r.resp) for r in responses))

    prior_t = 0

    yield f'T{"time":{t_width}} {"ΔT":>{t_width}} [ {"lo":{ix_width}} : {"query":{ix_width}} : {"hi":{ix_width}} ] {"<word>":{word_width}}? response ... analysis'

    for r in responses:
        t = r.time
        dt = t - prior_t

        w = r.hi - r.lo
        m = math.floor(r.hi/2+r.lo/2)
        b = r.q - m
        yield f'T{t:{t_width}.1f} {dt:{t_width}.1f} [ {r.lo:{ix_width}} : {r.q:{ix_width}} : {r.hi:{ix_width}} ] {r.word:{word_width}}? {r.resp:{resp_width}} ... wid:{w:{ix_width}} mid:{m:{ix_width}} bias:{b}'

        prior_t = t

    yield ''
    yield 'analysis legend:'
    yield '* wid -- search window width, aka `hi-lo`'
    yield '* mid -- classic binary search midpoint, aka `hi/2+lo/2`'
    yield '* bias -- prefix seeking bias applied, aka `query-mid`'

if __name__ == '__main__':
    for line in analyze(sys.stdin):
        print(line)
