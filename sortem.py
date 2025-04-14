#!/usr/bin/env python

import heapq
import random
from collections import Counter
from collections.abc import Generator, Iterable, Sequence
from functools import reduce
from itertools import count
from typing import final, override, Callable, Literal, Never

def nope(_arg: Never, mess: str =  'inconceivable'):
    assert False, mess

@final
class DiagScores:
    '''
    Diagnostic scores for a list of words.

    Score values are in the unit interval [0, 1].

    An ideally diagnostic letter occurs in half of the word list because, when
    validated or eliminated by a guess, it will winnow away number of words.

    All words in the list are presumed to be of the same length N,
    but the minimal word length is used for the value of N in the event that
    word length varies over the list.

    Each word's diagnostic score is then the average if its letter diagnostics.

    Additionally each word's score is divided by the per-word letter counts, so
    that duplicate letters quickly reduce its score.

    In other words, we would still rather try an uncommon letter, than repeat a
    perfectly diagnostic one.

    Example:
    - working with a list of 9477 5-letter words
    - letter counts across all words:

          4905 S ~ 51.8%
          4810 E ~ 50.8%
          4256 A ~ 44.9%
          3199 O ~ 33.8%
          3061 R ~ 32.3%
          2801 I ~ 29.6%
          2547 L ~ 26.9%
          2445 T ~ 25.8%
          2160 N ~ 22.8%
          1823 U ~ 19.2%
          1808 D ~ 19.1%
          1580 C ~ 16.7%
          1509 Y ~ 15.9%
          1488 P ~ 15.7%
          1431 M ~ 15.1%
          1295 H ~ 13.7%
          1192 G ~ 12.6%
          1161 B ~ 12.3%
          1042 K ~ 11.0%
           832 F ~ 8.8%
           726 W ~ 7.7%
           514 V ~ 5.4%
           277 Z ~ 2.9%
           228 X ~ 2.4%
           208 J ~ 2.2%
            87 Q ~ 0.9%

    - "arose" ranked #1 score: 83.381%
      - diag: 83.4% = avg( E: 98.5% S: 96.5% A: 89.8% O: 67.5% R: 64.6% )

    - "asker" ranked #149 score: 74.277%
      - diag: 74.3% = avg( E: 98.5% S: 96.5% A: 89.8% R: 64.6% K: 22.0% )

    - "kilts" ranked #3264 score: 56.588%
      - diag: 56.6% = avg( S: 96.5% I: 59.1% L: 53.8% T: 51.6% K: 22.0% )

    - ranked #7696 "silks" score: 28.917%
      - diag: 57.8% = avg( S: 96.5% I: 59.1% L: 53.8% K: 22.0% )
      - dupe divisor of 2 due to a single duplicate letter

    - "seeks" ranked #9178 score: 18.081%
      - diag: 72.3% = avg( E: 98.5% S: 96.5% K: 22.0% )
      - dupe divisor of 4 due to 2 duplicate letters

    - "esses" ranked #9271 score: 16.248%
      - diag: 97.5% = avg( E: 98.5% S: 96.5% )
      - dupe divisor of 6 due to a duplicate and a triplicate letter

    - "mamma" ranked #9463 score: 10.001%
      - diag: 60.0% = avg( A: 89.8% M: 30.2% )
      - dupe divisor of 6 due to a duplicate and a triplicate letter

    - "queue" ranked #9439 score: 11.567%
      - diag: 46.3% = avg( E: 98.5% U: 38.5% Q:  1.8% )
      - dupe of 4 due to 2 duplicate letters

    - "civic" ranked #9471 score: 8.609%
      - diag: 34.4% = avg( I: 59.1% C: 33.3% V: 10.8% )
      - dupe of 4 due to 2 duplicate letters

    - "yummy" ranked #9473 score: 8.376%
      - diag: 33.5% = avg( U: 38.5% Y: 31.8% M: 30.2% )
      - dupe of 4 due to 2 duplicate letters
    '''

    def __init__(self, words: Sequence[str]):
        self.lf = Counter(l for word in words for l in word)
        self.lf_norm = {l: c / len(words) for l, c in self.lf.items()}
        self.wfs = [Counter(word) for word in words]
        self.diag_lets = [tuple(
            (l, 1.0 - abs(self.lf_norm[l] - 0.5)/0.5)
            for l in set(word)
            if self.lf_norm[l] < 1 # ignore letters that occur in every word
        ) for word in words]
        self.diags = [
            sum(d for _, d in dlts) / len(dlts) if dlts else 0
            for dlts in self.diag_lets]
        self.dupes = [
            reduce(lambda a, b: a*b, wf.values(), 1)
            for wf in self.wfs]
        self.scores = [
            diag / dupe if dupe != 0 else diag
            for diag, dupe in zip(self.diags, self.dupes)]

    @property
    def lf_lo(self):
        return min(self.lf.values()) if self.lf else 0

    @property
    def lf_hi (self):
        return max(self.lf.values()) if self.lf else 1

    def explain(self, i: int) -> Generator[str]:
        yield f'*= diag:{100*self.diags[i]:5.1f}%'
        if self.dupes[i] > 1:
            yield f'/= dupe:{self.dupes[i]}'

    def explain_wf(self, i: int) -> Generator[str]:
        wf = self.wfs[i]
        for l, n in wf.items():
            if n > 1:
                yield f'{l.upper()}:{n}'

    def explain_lf(self, i: int) -> Generator[str]:
        lf_w = len(str(self.lf_hi))
        wf = self.wfs[i]
        for l in wf:
            yield f'{l.upper()}:{self.lf[l]:{lf_w}}'

    def explain_lf_norm(self, i: int) -> Generator[str]:
        wf = self.wfs[i]
        for l in wf:
            yield f'{l.upper()}:{100*self.lf_norm[l]:5.1f}%'

    def explain_diag(self, i: int) -> Generator[str]:
        for l, d in sorted(self.diag_lets[i], key=lambda ld: ld[1], reverse=True):
            yield f'{l.upper()}:{100*d:5.1f}%'

@final
class RandScores:
    '''
    Random scoring using a list of weight scores.

    Generates random values in a jitter diameter centered at 0.5;
    i.e. rng value are in the interval [0.5-jitter/2, 0.5+jitter/2).

    Weights are quantized into integers in the range [0, max_weight];
    alternatively the caller may pass pre-multiplied weights, quantization only
    happens here if all given scores are <= 1.0.

    If max_weight is 0, then the population size is used.

    Quantized weights are then used to take the W-th root of each rng value,
    which simulate having sampled from a distribution with W-copies of each item.

    In other words, this is weighed reservoir sampling, but with the reservoir
    left up to the consumer, and support for dampened rng, rather than full
    unit interval randomness.

    Typically the consumer will do something like top-K selection using a heap.

    NOTE: while jitter nominally defaults to 1.0, it will be clamped to the
    rang [0, 0.999] since 1.0 is not actually a useful jitter value:
    - while 0 is useful for disabling jitter entirely, if a tad wastefully
      since the caller really should've just chosen to not use random scoring
    - jitter=1 is actually problematic, since when the rng rolls a hard 0, any
      weight will be annihilated to 0
    - technically, jitter is clamped to 1.0-epsilon, with epsilon being the
      minimal rng value we want to see, which defaults to 0.001
    - if user decides they really must have hard 0 as a valid rng value, they
      may pass epsilon=0
    '''

    def __init__(
        self,
        weights: Sequence[float],
        jitter: float = 1.0,
        max_weight: float = 0,
        seed: str|None = None,
        epsilon: float = 0.001,
    ):
        self.max_weight = len(weights) if not max_weight else max_weight
        self.jitter = max(0, min(1.0 - epsilon, jitter))
        self.jitter_lo = (1.0-jitter)/2
        self.seed = seed
        self.oracle = random.Random(seed)

        self.quant_weights = (
            weights if any(wgt > 1 for wgt in weights)
            else [
                max(1, round(self.max_weight * wgt))
                for wgt in weights])

        self.rng = [
            0.5 if jitter == 0
            else self.jitter_lo + jitter*self.oracle.random()
            for _ in weights]

        self.scores: list[float] = [
            0 if wgt <= 0 else rnd ** (1.0 / float(wgt))
            for rnd, wgt in zip(self.rng, self.quant_weights)]

    def explain(self, i: int) -> Generator[str]:
        yield f'rng:{100*self.rng[i]:5.1f}%'
        yield f'^1/= qwgt:{self.quant_weights[i]}'

def top(k: int,
        get_score: Callable[[int], float],
        ix: Iterable[int]|None = None):
    choices: list[tuple[float, int]] = []
    if not ix:
        ix = count()
    dirty = False
    for i in ix:
        try:
            score = get_score(i)
        except IndexError:
            break
        if not k or len(choices) < k:
            choices.append((score, i))
            dirty = len(choices) > 1
        else:
            if dirty:
                heapq.heapify(choices)
                dirty = False
            if score > choices[0][0]:
                _ = heapq.heappushpop(choices, (score, i))
    choices = [(-score, i) for score, i in choices]
    heapq.heapify(choices)
    while choices:
        _, i = heapq.heappop(choices)
        yield i

@final
class Sample:
    Filter = Callable[[int], bool]
    Choice = tuple[Literal['head','top','bot','rand'], int] | Filter

    def __init__(self, choices: Iterable[Choice]):
        self.choices = tuple(choices)

    def partition(self) -> tuple['Sample', Filter, 'Sample']|None:
        for i, ch in enumerate(self.choices):
            if callable(ch):
                head = Sample(self.choices[:i])
                tail = Sample(self.choices[i+1:])
                return head, ch, tail
        return None

    def index(self,
              scores: Sequence[float],
              ix: Iterable[int]|None = None,
              ) -> Generator[int]:
        if not self.choices:
            yield from ix or range(len(scores))

        part = self.partition()
        if part:
            head, f, tail = part
            def apply_filter():
                got = 0
                for i in head.index(scores, ix):
                    if f(i):
                        got += 1
                        yield i
            yield from tail.index(scores, apply_filter())
            return

        for ch in self.choices:
            if callable(ch):
                continue # inconceivable, partition-ed above
            k, n = ch
            if k == 'head':
                yield from range(min(len(scores), n))
            elif k == 'top':
                yield from top(n, scores.__getitem__, ix)
            elif k == 'bot':
                yield from top(n, lambda i: -scores[i], ix)
            elif k == 'rand':
                def rand(i: int):
                    if i < len(scores): return random.random()
                    else: raise IndexError('list index out of range')
                yield from top(n, rand, ix)
            else:
                nope(k, f'inconceivable choice kind {k!r}')

    def describe(self) -> Generator[str]:
        if not self.choices:
            yield 'all natural'

        part = self.partition()
        if part:
            head, _f, tail = part
            def parts():
                if head.choices:
                    yield str(head)
                yield 'wanted'
                if tail.choices:
                    yield str(tail)
            yield ' then '.join(parts())
            return

        for ch in self.choices:
            if callable(ch):
                continue # inconceivable, partition-ed above
            k, n = ch
            if k == 'head':
                yield f'head-{n}'
            elif k == 'top':
                if n: yield f'top-{n}'
                else: yield 'all descending'
            elif k == 'bot':
                if n: yield f'bot-{n}'
                else: yield 'all ascending'
            elif k == 'rand':
                if n: yield f'random-{n}'
                else: yield 'all shuffled'
            else:
                nope(k, f'inconceivable choice kind {k!r}')

    @override
    def __str__(self):
        return ' and '.join(self.describe())

def main():
    import argparse
    import re
    import sys
    from typing import cast

    from strkit import striperate, spliterate
    def dedent(s: str):
        return '\n'.join(striperate(spliterate(s, '\n')))

    description = 'Sorts a list of words from stdin by diagnostic score.'

    epilog = dedent('''
    Basic usage to get 10 weighted-random 5-grams from a larger wordlist:

        $ grep '^.....$' words | sortem.py | head

    Disable RNG and inspect diagnostic details:

        $ grep '^.....$' words | sortem.py -vv -j 0 | less

    Experiment with different jitter values:

        $ grep '^.....$' words | sortem.py -v -j 1 --seed yolo | less
    ''')

    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    _ = parser.add_argument('--help-diag', action='store_true',
                            help='print detailed help topic explaining diagnostic scores')
    _ = parser.add_argument('--help-rand', action='store_true',
                            help='print detailed help topic explaining randomized scores')

    _ = parser.add_argument('-v', default=0, action='count',
                            help='print verbose output, explaining word scores; ' +
                                 'give a second time for even more detail')

    _ = parser.add_argument('-j', '--jitter', default=0.5, type=float,
                            help='value between 0.0 and 1.0 to enable random sampling, defaults to 0.2')
    _ = parser.add_argument('-m', '--max-weight', default=0.0, type=float,
                            help='maximum ideal weight (number of sample copies), defaults to 100')
    _ = parser.add_argument('-s', '--seed',
                            help='RNG seed for any jitter')

    _ = parser.add_argument('-t', '--top', metavar='K', action='append', dest='choices',
                            type=lambda arg: cast(Sample.Choice, ('top', int(arg))),
                            help='limit output to top K words; K=0 for "all descending", which is the default modality')
    _ = parser.add_argument('-b', '--bot', metavar='K', action='append', dest='choices',
                            type=lambda arg: cast(Sample.Choice, ('bot', int(arg))),
                            help='limit output to bottom K words; K=0 for "all ascending"')
    _ = parser.add_argument('-r', '--random', metavar='K', action='append', dest='choices',
                            type=lambda arg: cast(Sample.Choice, ('rand', int(arg))),
                            help='shuffle output irrespective of score values; K=0 for "all shuffled"')
    _ = parser.add_argument('-g', '--grep', metavar='REGEX', action='append', dest='choices',
                            type=re.compile,
                            help='limit output to entries which match one or more regular expressions')
    _ = parser.add_argument('--head', metavar='K', action='append', dest='choices',
                            type=lambda arg: cast(Sample.Choice, ('head', int(arg))),
                            help='limit output to first K words')

    # parse args and setup deps
    args = parser.parse_args()

    if cast(bool, args.help_diag):
        print(DiagScores.__doc__)
        parser.exit()
    if cast(bool, args.help_rand):
        print(RandScores.__doc__)
        parser.exit()

    jitter = max(0, min(1, cast(float, args.jitter)))
    max_weight = cast(float, args.max_weight)
    rng_seed = cast(str|None, args.seed)
    verbose = cast(int, args.v)

    def make_result_filter(*pats: re.Pattern[str]) -> Sample.Filter:
        return lambda i: any(
            pat.search(line)
            for line in result(i)
            for pat in pats)

    def arg_samp_choices() -> Generator[Sample.Choice]:
        choices = cast(list[Sample.Choice|re.Pattern[str]]|None, args.choices)
        if not choices:
            yield 'top', 0
            return

        for ch in choices:
            if isinstance(ch, re.Pattern):
                yield make_result_filter(ch)
            else:
                yield ch

    samp = Sample(arg_samp_choices())

    # wordlist from stdin, any filtering left as caller's exercise 
    words = [
        str(line).strip().lower()
        for line in sys.stdin]

    diag = DiagScores(words)
    rng = None if jitter == 0 else RandScores(
        diag.scores,
        jitter = jitter,
        max_weight = max_weight,
        seed = rng_seed)
    scores = diag.scores if rng is None else rng.scores

    def result(i: int) -> Generator[str]:
        yield words[i]
        if verbose:
            yield f'{100*scores[i]:5.3f}%'
            if rng is not None:
                yield from rng.explain(i)
            yield from diag.explain(i)

    if verbose > 0:
        print(f'- wordlist size:{len(words)}')
        if verbose > 2:
            nw = len(str(diag.lf_hi))
            for let, n in sorted(diag.lf.items(), key=lambda ln: ln[1], reverse=True):
                print(f'- LF {n:{nw}} {let.upper()} ~ {100*diag.lf_norm[let]:.1f}%')
        elif verbose > 1:
            print(f'- LF lo:{diag.lf_lo} hi:{diag.lf_hi}')
        if rng is not None:
            print(f'- jitter: {100*rng.jitter:.1f}%')
            if rng_seed is not None:
                print(f'- seed: {rng_seed!r}')
            print(f'- max_weight: {rng.max_weight}')
        print(f'- sampling: {samp}')
        print()

    for n, i in enumerate(samp.index(scores), 1):
        if verbose > 0:
            print(f'{n}. [{i}]', *result(i))
        else:
            print(*result(i))

        if verbose > 1:
            bw = len(f'{n}.')
            indent = ' ' * bw
            wf_parts = list(diag.explain_wf(i))
            if wf_parts:
                print(indent, f'- WF', *wf_parts)
            print(indent, f'- diag = avg(', *diag.explain_diag(i), ')')
            if verbose == 2:
                print(indent, f'- LF', *diag.explain_lf(i))
                print(indent, f'- LF norm', *diag.explain_lf_norm(i))

if __name__ == '__main__':
    try:
        main()
    except BrokenPipeError:
        pass
