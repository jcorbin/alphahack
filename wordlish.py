from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from itertools import combinations, permutations
from typing import Literal, Never, final, override
import re

from strkit import MarkedSpec, PeekStr

# TODO evolve square to use

def nope(_arg: Never, mess: str =  'inconceivable') -> Never:
    assert False, mess

def char_pairs(alpha: Iterable[str]):
    a, b = '', ''
    for c in sorted(alpha):
        if not a: a = c
        if not b: b = c
        dcb = ord(c) - ord(b)
        if dcb > 1:
            yield a, b
            a = b = c
        else:
            b = c
    if a and b:
        yield a, b

def char_ranges(alpha: Iterable[str]):
    for a, b in char_pairs(alpha):
        dba = ord(b) - ord(a)
        if dba == 0:
            yield a
        elif dba == 1:
            yield a
            yield b
        else:
            yield a
            yield '-'
            yield b

# Feedback represents per-letter feedback for an attempted Wordle word:
# - 0 means an incorrect letter, usually represented by Grey color
# - 1 means a correct letter but wrong position, usually represented by Yellow color
# - 2 means a correct letter and position usually represented by Green color
Letres = Literal[0,1,2]
Feedback = tuple[Letres, ...]

@dataclass
class Attempt:
    '''
    An attempted Wordle word with corresponding per-letter feedback.
    '''

    word: str
    res: Feedback

    @classmethod
    def parse(cls,
              tokensOrStr: PeekStr|str,
              expected_size: int = 0,
              require_feedback: bool = True):
        pk = (
            PeekStr(m[0] for m in re.finditer(r'[^\s+]+', tokensOrStr))
            if isinstance(tokensOrStr, str) else tokensOrStr)

        word = next(pk, None)
        if word is None:
            raise ValueError('must provide attempted word')
        if expected_size and len(word) != expected_size:
            raise ValueError(f'expected word to be {expected_size} letters, got {len(word)}')

        res: Feedback = tuple(
            0 if m[1] else 1 if m[2] else 2
            for m in pk.consume(r'(?x) ([Nn0]) | ([Mm1]) | ([Yy2])'))
        if require_feedback and not res:
            raise ValueError('must provide word feedback')
        if res and len(res) != len(word):
            raise ValueError(f'expected {len(word)} feedback codes, got {len(res)}')

        return cls(word, res)

    @property
    def feedback_letters(self):
        for c in self.res:
            if c == 2: yield 'Y'
            elif c == 1: yield 'm'
            else: yield 'n'

    @override
    def __str__(self):
        return f'{self.word} {" ".join(self.feedback_letters)}'

    def letter_notes(self):
        for i, (c, f) in enumerate(zip(self.word, self.res)):
            yield c, f, i

@MarkedSpec.mark('''
    #meh
    > mamma nMnnn
    m 0 0
    a 1 1
    m 0 2
    m 0 3
    a 0 4

    #yemeh
    > loner YnnMn
    l 2 0
    o 0 1
    n 0 2
    e 1 3
    r 0 4

    #yeye
    > winer YYYYY
    w 2 0
    i 2 1
    n 2 2
    e 2 3
    r 2 4
''')
def test_attempt_notes(spec: MarkedSpec):
    at = Attempt.parse(spec.input)
    assert [
        f'{c} {f} {i}'
        for c, f, i in at.letter_notes()
    ] == list(spec.bodylines)

@final
class Word:
    '''
    Word carries search state for a wordle-style game.
    '''

    def __init__(self,
                 size: int,
                 alpha: Iterable[str] = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                 ):
        uni = tuple(alpha)
        self.alpha = uni
        self.yes: list[str] = [''] * size
        self.may: set[str] = set()
        self.max: dict[str, int] = dict()
        self.can: tuple[set[str], ...] = tuple(set(uni) for _ in range(size))

    def __len__(self):
        return len(self.can)

    def reset(self):
        size = len(self)
        self.yes = [''] * size
        self.may = set()
        self.max = dict()
        self.can = tuple(set(self.alpha) for _ in range(size))

    @property
    def word(self):
        return ''.join(l or '_' for l in self.yes)

    @override
    def __str__(self):
        def parts():
            yield f'{self.word}'
            if self.done: return

            if self.may:
                yield f'~{"".join(sorted(self.may))}'

            cant = set(self.alpha)
            for cn in self.can:
                cant.difference_update(cn)
            if cant:
                yield f'-{"".join(sorted(cant))}'

            for c in sorted(self.max):
                yield f'{c}:{self.max[c]}'

        return ' '.join(parts())

    @property
    def done(self):
        return all(l for l in self.yes)

    def cannot(self, c: str):
        if c in self.may:
            self.may.remove(c)
        if c in self.max:
            del self.max[c]
        for known, can in zip(self.yes, self.can):
            if not known:
                can.difference_update((c,))

    def collect(self, at: Attempt):
        mayc: set[str] = set()
        for c, f, i in at.letter_notes():
            if f in (0, 1):
                mayc.add(c)
            elif f == 2:
                self.yes[i] = c
                self.can[i].clear()
                self.can[i].update((c,))

                if self.max.get(c):
                    self.max[c] -= 1
                    if self.max[c] < 1:
                        if c in self.may:
                            self.may.remove(c)
                        for j, cn in enumerate(self.can):
                            if j != i and c in cn:
                                cn.remove(c)

                if c in self.may:
                    self.may.remove(c)

            else: nope(f, 'invalid feedback')
        for c in mayc:
            may = sum(f == 1 for cc, f, _ in at.letter_notes() if cc == c)
            if may:
                self.may.add(c)
                if any(f == 0 for cc, f, _ in at.letter_notes() if cc == c):
                    self.max[c] = may
                for cc, f, i in at.letter_notes():
                    if cc == c and f != 2:
                        self.can[i].difference_update((c,))
            else:
                self.cannot(c)

    def re_may(self,
               i: int,
               less: Iterable[str]|None = None,
               void: Iterable[str]|None = None,
               ):
        alpha = self.can[i]
        if less is not None:
            lc = Counter(less)
            alpha = alpha.difference(
                c
                for c, n in lc.items()
                if c in self.max
                if self.max[c] - n <= 0)
        if void is not None:
            alpha = alpha.difference(void)
        return f'[{"".join(char_ranges(alpha))}]'

    def re_can(self, void: Iterable[str]|None = None):
        return ''.join(
            known or self.re_may(i, void=void)
            for i, known in enumerate(self.yes))

    def re_may_alts(self, void: Iterable[str]|None = None):
        may = tuple(sorted(self.may))
        can = tuple(
            known or self.re_may(i, may, void=void)
            for i, known in enumerate(self.yes))
        ix = tuple(
            i
            for i, known in enumerate(self.yes)
            if not known)
        for mix in combinations(ix, len(may)):
            for pmay in permutations(may):
                if any(
                    pmay[j] not in self.can[i]
                    for j, i in enumerate(mix)
                ): continue
                parts = list(can)
                for j, i in enumerate(mix):
                    parts[i] = pmay[j]
                yield ''.join(parts)

    def patstr(self, void: Iterable[str]|None = None):
        return '|'.join(self.re_may_alts(void=void)) if self.may else self.re_can(void=void)

    def pattern(self, void: Iterable[str]|None = None):
        return re.compile(self.patstr(void=void), flags=re.I)

    # TODO def filter(self, word: str):

@MarkedSpec.mark('''

    # zero
    - done: False
    - str: _____

    # 1_mamma
    > mamma nMnnn
    - str: _____ ~A -M A:1
    - done: False
    - can: [A-LN-Z][B-LN-Z][A-LN-Z][A-LN-Z][B-LN-Z]
    - may_alts: ```
    A[B-LN-Z][B-LN-Z][B-LN-Z][B-LN-Z]
    [B-LN-Z][B-LN-Z]A[B-LN-Z][B-LN-Z]
    [B-LN-Z][B-LN-Z][B-LN-Z]A[B-LN-Z]
    ```

    # 2_ideal
    > mamma nMnnn
    > ideal nMnYn
    - str: ___A_ ~D -EILM A:0
    - done: False
    - can: [B-DF-HJKN-Z][BCF-HJKN-Z][B-DF-HJKN-Z]A[B-DF-HJKN-Z]
    - may_alts: ```
    D[BCF-HJKN-Z][B-DF-HJKN-Z]A[B-DF-HJKN-Z]
    [B-DF-HJKN-Z][BCF-HJKN-Z]DA[B-DF-HJKN-Z]
    [B-DF-HJKN-Z][BCF-HJKN-Z][B-DF-HJKN-Z]AD
    ```

    # 3_ducat
    > mamma nMnnn
    > ideal nMnYn
    > ducat YYYYY
    - str: DUCAT
    - done: True
    - can: DUCAT

''')
def test_word(spec: MarkedSpec):
    word = Word(5)
    for line in spec.inlines:
        at = Attempt.parse(line)
        at.word = at.word.upper()
        word.collect(at)
    for key, val in spec.props:
        if key == 'str': assert f'{word}' == val
        elif key == 'can': assert f'{word.re_can()}' == val
        elif key == 'may_alts': assert f'{"\n".join(word.re_may_alts())}' == val
        elif key == 'pat': assert f'{word.pattern()}' == val
        elif key == 'done': assert f'{word.done}' == val
        else: raise NotImplementedError(f'unknown spec prop {key!r}')
