#!/usr/bin/env python

description = '''
Sorts a list of words from stdin by diagnostic score.

An ideal diagnostic letter is one that occurs in half of the word list,
so that its presence or lack will eliminate half of the candidates.

The words are assumed to be of a fixed length K;
but if they vary, the minimum given word length is the value of K.

A word's diagnostic score then is the product of its top K letter diagnostics,
divided by its constituent letter counts to discount words with duplicate letters.

We could say more to try to explain these maths with examples,
but you're probably better off just inspecting -vv output.
'''

epilog = '''

NOTE: RNG values are in the interval [0.5-jitter/2, 0.5+jitter/2).
      So in practice, jitter maximum is slightly less than 1.0, say 0.99.
      Problem with 1.0 is that a 0 RNG result annihilates any weight to 0.

Basic usage to get 10 weighted-random 5-grams from a larger wordlist:

    $ grep '^.....$' words | sortem.py | head

Disable RNG and inspect diagnostic details:

    $ grep '^.....$' words | sortem.py -vv -j 0 | less

Experiment with different jitter values:

    $ grep '^.....$' words | sortem.py -v -j 0.99 --seed yolo | less
'''

import argparse

parser = argparse.ArgumentParser(
    description=description,
    epilog=epilog,
    formatter_class=argparse.RawDescriptionHelpFormatter)

_ = parser.add_argument('-v', default=0, action='count',
                        help='print verbose output, explaining word scores; ' +
                             'give a second time for even more detail')
_ = parser.add_argument('-j', '--jitter', default=0.2, type=float,
                        help='value between 0.0 and 1.0 to enable random sampling, defaults to 0.2')
_ = parser.add_argument('-m', '--max-weight', default=100.0, type=float,
                        help='maximum ideal weight (number of sample copies), defaults to 100')
_ = parser.add_argument('-s', '--seed',
                        help='RNG seed for any jitter')

# parse args and setup deps
args = parser.parse_args()

import random
import sys
from collections import Counter
from collections.abc import Generator, Iterable
from functools import reduce
from typing import cast

jitter = max(0, min(1, cast(float, args.jitter)))
max_weight = cast(float, args.max_weight)
rng_seed = cast(str|None, args.seed)
verbose = cast(int, args.v)

oracle = random.Random(rng_seed)

def prod_top_k(k: int,ns: Iterable[float]):
    samp: list[float] = []
    try:
        it = iter(ns)
        for i in range(k):
            samp.append(next(it))
        for c in it:
            for i in range(k):
                if samp[i] < c:
                    samp[i] = c
                    break
    except StopIteration:
        pass
    return reduce(lambda a, b: a*b, samp, 1.0)

# wordlist from stdin, any filtering left as caller's exercise 
words = [
    str(line).strip().lower()
    for line in sys.stdin]

# letter frequency over all possible words
lf = Counter(l for word in words for l in word)
lf_lo = min(lf.values()) if lf else 0
lf_hi = max(lf.values()) if lf else 1
lf_norm = {l: c / lf_hi for l, c in lf.items()}

# letter frequency per-word
wfs = [Counter(word) for word in words]

# an ideally diagnostic letter occurs in half of possible words
#
# so define a diagnostic score based on each letter's
# absolute distance from occurring in 50% of words
#
# these score values are weights, higher value better,
# but normalized to unit interval
diag_lets = [tuple(
    (l, 1.0 - abs(lf_norm[l] - 0.5)/0.5)
    for l in set(word)
    if lf_norm[l] < 1 # ignore letters that occur in every word
) for word in words]

# each word gets a diagnostic score: product of the top-K letter scores
diag_k = min(len(word) for word in words) // 2
diags = [
    prod_top_k(diag_k, (d for _, d in dlts))
    for dlts in diag_lets]

# exponentially growing duplicate count
dupes = [
    reduce(lambda a, b: a*b, wf.values())
    for wf in wfs]

# combined word weight: diagnostic good, duplicate letters bad
weights = [
    diag / dupe if dupe != 0 else diag
    for diag, dupe in zip(diags, dupes)]

# quantize unit weights
quant_weights = [
    max(1, round(max_weight * wgt))
    for wgt in weights]

# weighted random sample
jitter_lo = (1.0-jitter)/2
rng = [
    0.5 if jitter == 0
    else jitter_lo + jitter*oracle.random()
    for _ in weights]

scores: list[float] = weights if jitter == 0 else [
    rnd ** (1.0 / float(wgt))
    for rnd, wgt in zip(rng, quant_weights)]

ix = sorted(
    range(len(words)),
    key=lambda i: scores[i],
    reverse=True)

def result(i: int) -> Generator[str]:
    yield words[i]
    if verbose:
        yield from explain_score(i)

def explain_score(i: int) -> Generator[str]:
    yield f'{100*scores[i]:5.3f}%'

    if jitter != 0:
        yield f'rng:{100*rng[i]:5.1f}%'
        yield f'^1/= qwgt:{quant_weights[i]}'
        yield from explain_weight(i)
    else:
        yield from explain_weight(i)

def explain_weight(i: int) -> Generator[str]:
    yield f'*= diag:{100*diags[i]:5.1f}%'
    if dupes[i] > 1:
        yield f'/= dupe:{100*dupes[i]:5.1f}%'

def explain_wf(i: int) -> Generator[str]:
    wf = wfs[i]
    for l, n in wf.items():
        if n > 1:
            yield f'{l.upper()}:{n}'

def explain_lf(i: int) -> Generator[str]:
    lf_w = len(str(lf_hi))
    wf = wfs[i]
    for l in wf:
        yield f'{l.upper()}:{lf[l]:{lf_w}}'

def explain_lf_norm(i: int) -> Generator[str]:
    wf = wfs[i]
    for l in wf:
        yield f'{l.upper()}:{100*lf_norm[l]:5.1f}%'

def explain_diag(i: int) -> Generator[str]:
    for l, d in diag_lets[i]:
        yield f'{l.upper()}:{100*d:5.1f}%'

try:

    if verbose > 0:
        print(f'- wordlist size:{len(words)}')
        if verbose > 1:
            print(f'- LF lo:{lf_lo} hi:{lf_hi}')
        if jitter != 0:
            print(f'- jitter: {100*jitter:.1f}%')
            if rng_seed is not None:
                print(f'- seed: {rng_seed!r}')
            print(f'- max_weight: {max_weight}')
        print()

    for n, i in enumerate(ix, 1):
        if verbose > 0:
            print(f'{n}. [{i}]', *result(i))
        else:
            print(*result(i))

        if verbose > 1:
            bw = len(f'{n}.')
            indent = ' ' * bw
            wf_parts = list(explain_wf(i))
            if wf_parts:
                print(indent, f'- WF', *wf_parts)
            print(indent, f'- diag = prod_top_{diag_k}(', *explain_diag(i), ')')
            print(indent, f'- LF', *explain_lf(i))
            print(indent, f'- LF norm', *explain_lf_norm(i))

except BrokenPipeError:
    pass
