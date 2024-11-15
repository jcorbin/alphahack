#!/usr/bin/env python

import math
from collections.abc import Sequence
from typing import cast, Callable, TextIO

from wordlist import WordList
from hack import Comparison, Search
from ui import PromptUI

Feedback = Callable[[Comparison], None]
Guess = tuple[str, Feedback]
Guesser = Callable[[], Guess]
Strat = Callable[[Sequence[str]], Guesser]

strats: dict[str, Strat] = dict()

def strat(fn: Strat):
    name = fn.__name__
    if name.startswith('strat_'): name = name[6:]
    assert name not in strats
    strats[name] = fn

@strat
def strat_hack(words: Sequence[str], context: int=3, echo: bool=False, log: bool=False) -> Guesser:
    def end_input(_: str): raise EOFError
    def int_input(_: str): raise KeyboardInterrupt

    ui = PromptUI(get_input=end_input)
    search = Search(ui, words, context=context)
    fin = False

    def guess() -> Guess:
        nonlocal fin

        with ui.deps(get_input=int_input):
            try:
                search.progress()

            except StopIteration:
                if not fin:
                    fin = True
                    return search.result or '', lambda _: None
                raise

            except KeyboardInterrupt:
                def feedback(compare: Comparison):
                    resp: str|None = (
                        'a' if compare > 0 else
                        'b' if compare < 0 else
                        'it')

                    def giver(prompt: str):
                        nonlocal resp
                        if resp is not None:
                            ret = resp
                            resp = None
                            if echo: print(f'PROMPT: {prompt}{ret}')
                            return ret
                        if echo: print(f'PROMPT: {prompt}<EOF>')
                        raise EOFError

                    with ui.deps(
                        get_input=giver,
                        sink=lambda mess: print(f'LOG: {mess}') if log else None,
                    ): search.progress()

                return search.q_word, feedback

            raise EOFError

    return guess

IntervalChooser = Callable[[int, int], int|None]

def interval_guesser(words: Sequence[str], choose: IntervalChooser):
    lo: int = 0
    hi: int = len(words)
    def guess() -> Guess:
        if lo >= hi-1: raise StopIteration
        qi = choose(lo, hi)
        if qi is None: raise StopIteration
        def feedback(compare: Comparison):
            nonlocal lo, hi
            if   compare > 0: lo = qi+1
            elif compare < 0: hi = qi
            else:         lo, hi = qi, qi+1
        return words[qi], feedback
    return guess

@strat
def strat_basic(words: Sequence[str]):
    return interval_guesser(words,
        lambda lo, hi: math.floor(lo/2 + hi/2))

@strat
def strat_prefix_c3(words: Sequence[str]):
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

    def find(word: str):
        qi = 0
        qj = len(words)-1
        while qi < qj:
            qk = math.floor(qi/2 + qj/2)
            qw = words[qk]
            if word == qw: return qk
            if   word < qw: qj = qk
            elif word > qw: qi = qk + 1
        return qi

    def common_prefix(i: int, j: int):
        a = words[i]
        b = words[j]
        n = min(len(a), len(b))
        k = 0
        while k < n and a[k] == b[k]: k += 1
        return a[:k]

    def choose(lo: int, hi: int):
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

def evaluate(word: str, guess: Guesser):
    guesses: list[str] = []
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

def main():
    import argparse

    parser = argparse.ArgumentParser()
    _ = parser.add_argument('--wordfile', type=argparse.FileType('r'), default='alphalist.txt')
    _ = parser.add_argument('--strat', default='basic', choices=sorted(strats))
    _ = parser.add_argument('word')

    args = parser.parse_args()
    word = cast(str, args.word).strip().lower()
    strat = strats[cast(str, args.strat)]

    wordlist = WordList(cast(TextIO, args.wordfile))
    print(wordlist.describe)
    words = wordlist.words

    count = 0
    for guess, compare in evaluate(word, strat(words)):
        print(f'- {guess} => {"before" if compare < 0 else "after" if compare > 0 else "it"}')
        count += 1
    print()
    print(f'done after {count} guesses')

if __name__ == '__main__':
    main()
