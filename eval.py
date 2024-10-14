#!/usr/bin/env python

import argparse
import hashlib
import math

parser = argparse.ArgumentParser()
parser.add_argument('--wordfile', type=argparse.FileType('r'), default='/usr/share/dict/words')
parser.add_argument('--strat', default='basic')
parser.add_argument('word')

args = parser.parse_args()
word = args.word.strip().lower()

def interval_guesser(words, choose):
    lo, hi = 0, len(words)
    def guess():
        if lo >= hi-1: raise StopIteration
        qi = choose(lo, hi)
        if qi is None: raise StopIteration
        def feedback(compare):
            nonlocal lo, hi
            if   compare > 0: lo = qi+1
            elif compare < 0: hi = qi
            else:         lo, hi = qi, qi+1
        return words[qi], feedback
    return guess

def strat_basic(words):
    return interval_guesser(words,
        lambda lo, hi: math.floor(lo/2 + hi/2))

def strat_prefix_c3(words):
    # This strategy works by looking at a context window around search mid point,
    # looking back to find any root/stem word that is common to all or most of the window words
    #
    # Basically consider the common situations like:
    #
    #     verb
    #     verbed
    #     verbing
    #     verbs
    #
    #     noun
    #     nouners
    #     nouns
    #
    # The basic motivation here is to try simpler root words first.

    # TODO would be nice to have parameterized strategies
    context = 3

    def find(word):
        qi = 0
        qj = len(words)-1
        while qi < qj:
            qk = math.floor(qi/2 + qj/2)
            qw = words[qk]
            if word == qw: return qk
            if   word < qw: qj = qk
            elif word > qw: qi = qk + 1
        return qi

    def common_prefix(i, j):
        a = words[i]
        b = words[j]
        n = min(len(a), len(b))
        k = 0
        while k < n and a[k] == b[k]: k += 1
        return a[:k]

    def choose(lo, hi):
        view_at = math.floor(lo/2 + hi/2)
        view_lo = max(0, view_at - context)
        view_hi = min(hi-1, view_at + context)

        prefix = common_prefix(view_lo, view_hi)
        if prefix:
            # if prefix is a valid word, try it
            pi = find(prefix)
            if lo < pi < hi and words[pi] == prefix: return pi

            # try truncating the window to see if we get a longer common prefix
            mq = view_hi
            while mq > view_lo + 1:
                mq -= 1
                qp = common_prefix(view_lo, mq)
                if len(qp) > len(prefix):
                    pi = find(qp)
                    if lo < pi < hi and words[pi] == qp: return pi

            # try shortening the common prefix to see if it has a valid word prefix
            while len(prefix) > 0:
                prefix = prefix[:-1]
                pi = find(prefix)
                if lo < pi < hi and words[pi] == prefix: return pi

        return view_at

    return interval_guesser(words, choose)

def evaluate(guess):
    guesses = []
    while True:
        try:
            resp, feedback = guess()
        except StopIteration:
            break

        if len(guesses) >= 3 and all(prior == resp for prior in guesses[-3:]):
            break
        # TODO better loop detection than just "same guess last 3 turns"

        guesses.append(resp)

        cmp = resp.strip().lower()
        compare = (
             1 if word > cmp else
            -1 if word < cmp else
            0)
        feedback(compare)
        yield resp, compare

try:
    strat = locals()[f'strat_{args.strat}']
    if not callable(strat):
        raise TypeError
except (KeyError, TypeError):
    parser.error(f'Invalid strategy; choose one of: {' '.join(
        name[6:]
        for name, val in locals().items()
        if callable(val) and name.startswith("strat_")
    )}')

with args.wordfile as wordfile:
    words = [
        word.strip().lower().partition(' ')[0]
        for word in wordfile
    ]

with open(args.wordfile.name, 'rb') as wordfile:
    sig = hashlib.file_digest(wordfile, 'sha256')

words = [word for word in words if "'" not in word]
words = sorted(set(words))
print(f'loaded {len(words)} words from {args.wordfile.name} {sig.hexdigest()}')

count = 0
for guess, compare in evaluate(strat(words)):
    print(f'- {guess} => {"before" if compare < 0 else "after" if compare > 0 else "it"}')
    count += 1
print()
print(f'done after {count} guesses')
