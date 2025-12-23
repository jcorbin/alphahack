#!/usr/bin/env python

from collections import Counter
from collections.abc import Generator, Iterable
from dataclasses import dataclass
from itertools import chain, combinations, permutations
from typing import Callable, Literal, Never, cast, final, override
import re
import sys

from strkit import MarkedSpec, PeekStr
from ui import PromptUI

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

def feedback_letters(res: Feedback):
    for c in res:
        if c == 2: yield 'Y'
        elif c == 1: yield 'm'
        else: yield 'n'

def _parse_feedback(tokensOrStr: PeekStr|str, max: int|None=None) -> Generator[Letres]:
    pk = (
        PeekStr(m[0] for m in re.finditer(r'[^\s+]+', tokensOrStr))
        if isinstance(tokensOrStr, str) else tokensOrStr)
    n = 0
    for m in pk.consume(r'(?x) ([Nn0]) | ([Mm1]) | ([Yy2])'):
        n += 1
        yield (
            0 if m[1] else
            1 if m[2] else
            2)
        if max is not None and n >= max: break

def parse_feedback(tokensOrStr: PeekStr|str, max: int|None=None) -> Feedback:
    return tuple(_parse_feedback(tokensOrStr, max))

@final
class Question:
    def __init__(self,
                 word: str,
                 then: Callable[[str, Feedback], PromptUI.State],
                 reject: Callable[[str], PromptUI.State]|None = None,
                 prefix: Callable[[], str]|str = '',
                 mark: str = '? ',
                 ):
        self.prefix = prefix
        self.mark = mark
        self.word = word
        self.then = then
        self.reject = reject
        self.prompt = PromptUI.Prompt(self.mess, {
            " ": self.parse,
            '/bad': self.do_bad,
            '!': '/bad',
        })

    def parse_feedback(self, ui: PromptUI) -> Feedback:
        if ui.tokens.have(r'(?i)it$'):
            return (2,) * len(self.word)
        return parse_feedback(ui.tokens)

    def do_bad(self, ui: PromptUI):
        if not self.reject:
            ui.print(f'! bad word {self.word!r}')
            raise StopIteration
        return self.reject(self.word)

    def mess_parts(self, ui: PromptUI):
        if self.prefix:
            if callable(self.prefix):
                yield self.prefix()
            else:
                yield self.prefix
        if self.prompt.re == 0:
            ui.copy(self.word)
            yield f'📋 "{self.word}"'
        yield self.mark

    def mess(self, ui: PromptUI):
        return ' '.join(self.mess_parts(ui))

    def parse(self, ui: PromptUI) -> PromptUI.State|None:
        fb = self.parse_feedback(ui)
        if not fb: return None
        if len(fb) < len(self.word):
            ui.print(f'! insufficient feedback, need {len(self.word)} parts')
            return self
        elif len(fb) > len(self.word):
            ui.print(f'! extraneous feedback, only need {len(self.word)} parts')
            return self
        return self.then(self.word, fb)

    def __call__(self, ui: PromptUI):
        return self.prompt(ui)

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

        res = parse_feedback(pk, len(word))
        if require_feedback and not res:
            raise ValueError(f'must provide feedback for word {word!r}')
        if res and len(res) != len(word):
            raise ValueError(f'expected {len(word)} feedback codes, got {len(res)}')

        return cls(word, res)

    @property
    def feedback_letters(self):
        return feedback_letters(self.res)

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
        self.uni = tuple(alpha)
        self.alpha = set(self.uni)
        self.yes: list[str] = [''] * size
        self.may: set[str] = set()
        self.max: dict[str, int] = dict()
        self.can: tuple[set[str], ...] = tuple(
            set(self.alpha) for _ in range(size))

    def __len__(self):
        return len(self.can)

    def reset(self):
        size = len(self)
        self.alpha = set(self.uni)
        self.yes = [''] * size
        self.may = set()
        self.max = dict()
        self.can = tuple(set(self.alpha) for _ in range(size))

    @property
    def possible(self) -> int:
        free = sum(not let for let in self.yes)
        if self.may:
            free -= len(self.may)
        space: int = cast(int, len(self.alpha) ** free) # valid because free is a natural number
        if self.may:
            for n in range(len(self.may), 1, -1): space *= n
        return space

    @property
    def letters(self):
        return tuple(l or '_' for l in self.yes)

    @property
    def word(self):
        return ''.join(self.letters)

    @classmethod
    def parse(cls, tokensOrStr: PeekStr|str):
        parts = (
            PeekStr(m[0] for m in re.finditer(r'[^\s+]+', tokensOrStr))
            if isinstance(tokensOrStr, str) else tokensOrStr)
        if not parts: raise ValueError('invalid Word string')

        # TODO whence alpha
        yes = next(parts).upper()
        size = len(yes)
        self = cls(size)
        for i, c in enumerate(yes):
            self.yes[i] = '' if c == '_' else c

        while parts:
            match = parts.have(r'(?x) ~ ( [^\s]+ )')
            if match:
                may = match[1].upper()
                self.may.update(may)
                continue

            match = parts.have(r'(?x) - ( [^\s]+ )')
            if match:
                nope = match[1].upper()
                for can in self.can:
                    can.difference_update(nope)
                continue

            match = parts.have(r'(?x) ( [^\s] ) : ( \d+ )')
            if match:
                let = match[1].upper()
                self.max[let] = int(match[2])
                continue

            raise ValueError(f'invalid Word string part {parts.peek()!r}')

        return self

    def __bool__(self):
        if any(self.yes): return True
        if self.may: return True
        if self.cant(): return True
        if self.max: return True
        return False

    @override
    def __str__(self):
        return ' '.join(part for part in self.str_parts() if part)

    def str_parts(self):
        yield f'{self.word}'
        if not self.done:
            yield self.may_str()
            yield self.cant_str()
            yield self.max_str()

    def may_str(self):
        return f'~{"".join(sorted(self.may))}' if self.may else ''

    def cant_str(self):
        cant = self.cant()
        return f'-{"".join(sorted(cant))}' if cant else ''

    def max_str(self):
        return ' '.join(
            f'{c}:{self.max[c]}'
            for c in sorted(self.max))

    def cant(self):
        cant = set(self.uni)
        for cn in self.can:
            cant = cant.difference(cn)
        return cant

    @property
    def done(self):
        return all(l for l in self.yes)

    def cannot(self, c: str):
        c = c.upper()
        self.alpha.difference_update((c,))
        if c in self.may:
            self.may.remove(c)
        if c in self.max:
            del self.max[c]
        for known, can in zip(self.yes, self.can):
            if not known:
                can.difference_update((c,))

    def collect(self, at: Attempt):
        at = Attempt(at.word.upper(), at.res)
        for c in set(at.word):
            fis = tuple((f, i) for cc, f, i in at.letter_notes() if cc == c)
            ni = tuple(i for f, i in fis if f == 0)
            mi = tuple(i for f, i in fis if f == 1)
            yi = tuple(i for f, i in fis if f == 2)
            for i in yi:
                self.yes[i] = c
                self.can[i].clear()
                self.can[i].update((c,))
            for i in chain(mi, ni):
                self.can[i].difference_update((c,))
            if mi:
                if c not in self.yes:
                    self.may.add(c)
            elif c in self.may:
                self.may.remove(c)
            if yi or mi:
                if ni and mi:
                    self.max[c] = len(mi)
                elif c in self.max:
                    if len(yi) >= self.max[c]:
                        del self.max[c]
                        for i, can in enumerate(self.can):
                            if i not in yi:
                                can.difference_update((c,))
            elif ni:
                for can in self.can:
                    can.difference_update((c,))
        return at

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

    def re_can_lets(self, void: Iterable[str]|None = None):
        for i, known in enumerate(self.yes):
            yield known or self.re_may(i, void=void)

    def re_can(self, void: Iterable[str]|None = None):
        return ''.join(self.re_can_lets(void))

    def re_may_perms(self):
        may = tuple(sorted(self.may))
        ix = tuple(
            i
            for i, known in enumerate(self.yes)
            if not known)
        for mix in combinations(ix, len(may)):
            for pmay in permutations(may):
                yield mix, pmay

    def re_may_alts(self, void: Iterable[str]|None = None):
        may = tuple(sorted(self.may))
        can = tuple(
            known or self.re_may(i, may, void=void)
            for i, known in enumerate(self.yes))
        for mix, pmay in self.re_may_perms():
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
    - can_lets: ```
    [A-LN-Z]
    [B-LN-Z]
    [A-LN-Z]
    [A-LN-Z]
    [B-LN-Z]
    ```
    - may_alts: ```
    A[B-LN-Z][B-LN-Z][B-LN-Z][B-LN-Z]
    [B-LN-Z][B-LN-Z]A[B-LN-Z][B-LN-Z]
    [B-LN-Z][B-LN-Z][B-LN-Z]A[B-LN-Z]
    ```

    # 2_ideal
    > mamma nMnnn
    > ideal nMnYn
    - str: ___A_ ~D -EILM
    - done: False
    - can_lets: ```
    [B-DF-HJKN-Z]
    [BCF-HJKN-Z]
    [B-DF-HJKN-Z]
    A
    [B-DF-HJKN-Z]
    ```
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

    #hurdle_may_after_yes
    > JUMPY n M n n n
    > MIDST n M n n Y
    > SHAPE n n n n n
    > MONTE n n n M n
    - str: ____T ~IU -ADEHJMNOPSY
    - done: False
    - can_lets: ```
    [BCFGIKLQRT-XZ]
    [BCFGKLQRTV-XZ]
    [BCFGIKLQRT-XZ]
    [BCFGIKLQRU-XZ]
    T
    ```
    - may_alts: ```
    I[BCFGKLQRTV-XZ]U[BCFGIKLQRU-XZ]T
    U[BCFGKLQRTV-XZ]I[BCFGIKLQRU-XZ]T
    I[BCFGKLQRTV-XZ][BCFGIKLQRT-XZ]UT
    U[BCFGKLQRTV-XZ][BCFGIKLQRT-XZ]IT
    [BCFGIKLQRT-XZ][BCFGKLQRTV-XZ]IUT
    [BCFGIKLQRT-XZ][BCFGKLQRTV-XZ]UIT
    ```

    #must_be_aches
    > REAMS n m m n Y
    > RISEN n n m Y n
    > RINSE n n n m m
    > EMCEE n n m Y n
    > SPELL m n m n n
    > CHEAT m m m m n
    - str: ___ES ~ACH -ILMNPRT
    - done: False
    - can_lets: ```
    [ABDF-HJKOQU-Z]
    [A-DFGJKOQSU-Z]
    [BDF-HJKOQU-Z]
    E
    S
    ```
    - may_alts: ```
    ACHES
    ```

    #may_after_max
    > VUGGY n n n n n
    > KAKAS n m n n n
    > AFFIX m n n n n
    - str: _____ ~A -FGIKSUVXY A:1
    - can_lets: ```
    [B-EHJL-RTWZ]
    [B-EHJL-RTWZ]
    [A-EHJL-RTWZ]
    [B-EHJL-RTWZ]
    [A-EHJL-RTWZ]
    ```

''')

def test_word(spec: MarkedSpec):
    word = Word(5)
    for line in spec.inlines:
        at = Attempt.parse(line)
        at.word = at.word.upper()
        _ = word.collect(at)
    for key, val in spec.props:
        if key == 'str': assert f'{word}' == val
        elif key == 'can': assert f'{word.re_can()}' == val
        elif key == 'can_lets': assert f'{"\n".join(word.re_can_lets())}' == val
        elif key == 'may_alts': assert f'{"\n".join(word.re_may_alts())}' == val
        elif key == 'pat': assert f'{word.pattern()}' == val
        elif key == 'done': assert f'{word.done}' == val
        else: raise NotImplementedError(f'unknown spec prop {key!r}')

@MarkedSpec.mark('''

    #empty
    > _____
    - str: _____

    #ary
    > _A___ ~R -Y
    - str: _A___ ~R -Y

''')
def test_word_parse(spec: MarkedSpec):
    word = Word.parse(spec.input)
    for key, val in spec.props:
        if key == 'str': assert f'{word}' == val
        else: raise NotImplementedError(f'unknown spec prop {key!r}')

def main():
    def carp(mess: str) -> Never:
        print(f'! {mess}', file=sys.stderr)
        sys.exit(1)

    def usage() -> Generator[str]:
        yield f'Usage: <some_wordlist.txt wordlish.py [options...] <word> <feedback> [<word> <feedback> ...]'
        yield f''
        yield f'Options:'
        yield f'  -v -- increase verbosity'
        yield f''
        yield f'  -length <LENGTH> -- to specify word length (default: {len(word)})'
        yield f'  -len <LENGTH>    -- alias'
        yield f'  -n <LENGTH>      -- alias'
        yield f''
        yield f'  -word ( _ | <LETTER> )... [~ MAY...] [- CANT...] [<LETTER>:<MAX>]'
        yield f''
        yield f'  -void <LETTER...>'
        yield f''
        yield f'NOTE: word-feedback pairs should be given after any -word prior state'

    attempts: list[Attempt] = []
    word = Word(size=5)
    verbose: int = 0
    void: set[str] = set()

    args = PeekStr(sys.argv[1:])
    while args:
        have_opt = args.have(r'-+(.+)', lambda m: (m[0], str(m[1])))
        if have_opt:
            opt, name = have_opt

            if name.lower() in ('h', 'help', '?'):
                for line in usage():
                    print(line, file=sys.stderr)
                return 1

            if name.lower() in ('n', 'len', 'length'):
                n = args.have(r'\d+', lambda m: int(m[0]))
                if n is None:
                    carp(f'{opt} requires an <int> argument')
                if word:
                    carp(f'{opt} given after word feedback')
                word = Word(size=n)
                continue

            if name.lower() in ('w', 'word'):
                if (attempts or word) and not args.have(r'-f'):
                    carp(f'{opt} given after prior word feedback ; give -f to force')
                word = Word.parse(args)
                continue

            if name.lower() == 'v':
                verbose += 1
                continue

            if name.lower() in ('void', 'avoid'):
                lets = args.have(r'^\w+', lambda m: m[0])
                if lets:
                    void.update(lets.upper())
                continue

            carp(f'unknown option {opt}')

        try:
            at = Attempt.parse(args, expected_size=len(word))
        except ValueError as err:
            carp(f'expected attempt <word> <feedback>: {err}')
        attempts.append(word.collect(at))

    if verbose:
        for n, at in enumerate(attempts, 1):
            print(f'{n}. {at}', file=sys.stderr)
        if void:
            print(f'- avoid: {' '.join(sorted(void))}')
        print(word, file=sys.stderr)

    pat = word.pattern(void=void)
    if verbose > 1:
        print(pat, file=sys.stderr)

    found = False
    for line in sys.stdin:
        token, _ , _ = line.upper().strip().partition(' ')
        if len(token) != len(word): continue
        if not pat.match(token): continue
        print(token)
        found = True

    if not found:
        print(f'No Matches; reconsider:', file=sys.stderr)
        for alt in word.re_may_alts(void=void):
            print(f'  | {alt}', file=sys.stderr)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        pass
