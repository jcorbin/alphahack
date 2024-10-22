#!/usr/bin/env python

import math
import re
import sys
from collections import namedtuple

Response = namedtuple('Response', ['time', 'lo', 'q', 'hi', 'word', 'resp'])
          
pat = re.compile(r'''(?x)
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

def normalize_resp(resp):
    for code in ('after', 'before', 'it'):
        if code.startswith(resp.lower()):
            return code
    return resp

def parse_responses(lines):
    for line in lines:
        line = line.rstrip('\r\n')
        match = pat.match(line)
        if match:
            t_str, lo_str, q_str, hi_str, word, resp = match.groups()
            t = float(t_str)
            lo = int(lo_str)
            q = int(q_str)
            hi = int(hi_str)
            yield Response(t, lo, q, hi, word, normalize_resp(resp))

responses = list(parse_responses(sys.stdin))

max_ix = max(max(r.lo, r.q, r.hi) for r in responses)
t_width = max(4, max(len(f'{r.time:.1f}') for r in responses))
ix_width = max(5, len(str(max_ix)))
word_width = max(6, max(len(r.word) for r in responses))
resp_width = max(8, max(len(r.resp) for r in responses))

prior_t = 0

print(f'T{"time":{t_width}} {"ΔT":>{t_width}} [ {"lo":{ix_width}} : {"query":{ix_width}} : {"hi":{ix_width}} ] {"<word>":{word_width}}? response ... analysis')
for t, lo, q, hi, word, resp in responses:
    dt = t - prior_t
    w = hi - lo
    m = math.floor(hi/2+lo/2)
    b = q - m
    print(f'T{t:{t_width}.1f} {dt:{t_width}.1f} [ {lo:{ix_width}} : {q:{ix_width}} : {hi:{ix_width}} ] {word:{word_width}}? {resp:{resp_width}} ... wid:{w:{ix_width}} mid:{m:{ix_width}} bias:{b}')
    prior_t = t

print()
print('analysis legend:')
print('* wid -- search window width, aka `hi-lo`')
print('* mid -- classic binary search midpoint, aka `hi/2+lo/2`')
print('* bias -- prefix seeking bias applied, aka `query-mid`')
