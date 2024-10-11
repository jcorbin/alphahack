#!/usr/bin/env python

import argparse
import hashlib
import math
import pyperclip as pc

class Search(object):
    def __init__(self, words, context=3, log=lambda: None):
        self.words = sorted(words)
        self.context = context
        self.log = log

        self.lo = 0
        self.hi = len(self.words)

        self.may_suggest = True
        self.questioning = None
        self.chosen = None

    @property
    def result(self):
        if self.chosen is not None:
            return self.chosen
        if self.remain == 1:
            return self.lo
        return None

    @property
    def done(self):
        if self.result is not None:
            return True
        if self.remain <= 1:
            return True
        return False

    @property
    def remain(self):
        return self.hi - self.lo

    def insert(self, at, word):
        self.words.insert(at, word)
        if at < self.lo: self.lo += 1
        if at <= self.hi: self.hi += 1
        if self.questioning is not None and at <= self.questioning:
            self.questioning += 1

    def progress(self):
        if self.done: raise StopIteration
        mid = math.floor(self.lo/2 + self.hi/2)
        ctx_lo = max(0, mid - self.context)
        ctx_hi = min(self.hi-1, mid + self.context)
        self.log(f'... {self.lo} {ctx_lo} {mid} {ctx_hi} {self.hi}')

        compare, index = self.prompt(ctx_lo, ctx_hi)
        self.log(f'{compare} {index} {self.words[index]}')

        if   compare  < 0: self.hi = index
        elif compare  > 0: self.lo = index + 1
        elif compare == 0: self.chosen = index
        else: raise 'invalid comparison'

    def find(self, word):
        qi = 0
        qj = len(self.words)-1
        while qi < qj:
            qk = math.floor(qi/2 + qj/2)
            qw = self.words[qk]
            if word == qw: return qk
            if   word < qw: qj = qk
            elif word > qw: qi = qk + 1
        return qi

    def common_prefix(self, i, j):
        a = self.words[i]
        b = self.words[j]
        n = min(len(a), len(b))
        k = 0
        while k < n and a[k] == b[k]: k += 1
        return a[:k]

    def valid_prefix(self, lo, hi):
        prefix = self.common_prefix(lo, hi)
        if not prefix: return None
        pi = self.find(prefix)
        if self.lo < pi < self.hi and self.words[pi] == prefix:
            return pi
        mq = hi
        while mq > lo + 1:
            mq -= 1
            qp = self.common_prefix(lo, mq)
            if len(qp) > len(prefix):
                pi = self.find(qp)
                if self.lo < pi < self.hi and self.words[pi] == qp:
                    return pi
        while len(prefix) > 0:
            prefix = prefix[:-1]
            pi = self.find(prefix)
            if self.lo < pi < self.hi and self.words[pi] == prefix:
                return pi

    def prompt(self, lo, hi):
        self.may_suggest = True
        self.questioning = None

        while True:
            res = self.question(lo, hi)
            if res is not None: return res

            res = self.choose(lo, hi)
            if res is not None: return res

    def input(self, prompt):
        resp = input(prompt)
        self.log(f'{prompt}{resp}')
        return resp

    def question(self, lo, hi, qi=None):
        if qi is None:
            qi = self.questioning
            if qi is None: return
        else:
            self.questioning = qi

        word = self.words[qi]
        pc.copy(word)
        tokens = self.input(f'[{self.lo} : {qi} : {self.hi}] {word}? ').lower().split()
        if len(tokens) > 1:
            self.may_suggest = False
            self.questioning = None
            return self.handle_choose(lo, hi, tokens)

        token = tokens[0] if len(tokens) > 0 else ''
        if all(c == '.' for c in token):
            self.may_suggest = False
            self.questioning = None
            return

        compare = parse_compare(token)
        if compare is None:
            print(f'! invalid direction {token} ; expected a(fter), b(efore), or i(t)')
            return

        return compare, qi

    def choose(self, lo, hi):
        pi = self.valid_prefix(lo, hi)
        if pi is not None:
            if self.may_suggest:
                res = self.question(lo, hi, pi)
                if res is not None: return res
            if pi < lo:
                print(pi, self.words[pi])
                if pi < lo-1: print('...')
        for i in range(lo, hi): print(i, self.words[i])
        return self.handle_choose(lo, hi, self.input('> ').lower().split())

    def handle_choose(self, lo, hi, tokens):
        try:
            way = tokens[0]
            word = tokens[1]
        except IndexError:
            print('! expected response like: `[after|before|it|?] <word>`')
            return

        if way == '?':
            at = self.find(word)
            if self.words[at] != word:
                confirm = (
                    len(tokens) > 2 and tokens[2] or
                    input(f'! unknown word {word} ; respond . to add, else to re-prompt> '))
                if confirm.strip() != '.': return
                self.insert(at, word)
            return self.question(lo, hi, at)

        compare = parse_compare(way)
        if compare is None:
            print(f'! invalid direction {way} ; expected a(fter), b(efore), or i(t)')
            return

        at = self.find(word)
        if self.words[at] == word:
            return compare, at

        mi = lo
        mj = hi
        while mi < mj and not self.words[mi].startswith(word): mi += 1
        while mi < mj and not self.words[mj-1].startswith(word): mj -= 1
        em = mj - mi

        confirm = (
            len(tokens) > 2 and tokens[2] or
            input(f'! unknown word {word} ; respond . to add, else to re-prompt> '))

        if confirm.strip() == '.':
            self.insert(at, word)
            return compare, at

def parse_compare(s):
    if 'after'.startswith(s):
        return 1
    elif 'before'.startswith(s):
        return -1
    elif 'it'.startswith(s):
        return 0
    else:
        return None

parser = argparse.ArgumentParser()
parser.add_argument('--context', type=int, default=3, help='how many words to show +/- query');
parser.add_argument('--log', default='/dev/null', type=argparse.FileType('w'))
parser.add_argument('wordfile', type=argparse.FileType('r'))
args = parser.parse_args()

logfile = args.log

def log(*mess):
    print(*mess, file=logfile)
    logfile.flush()

with args.wordfile as wordfile:
    words = [
        word.strip().lower().partition(' ')[0]
        for word in wordfile
    ]

with open(args.wordfile.name, 'rb') as wordfile:
    sig = hashlib.file_digest(wordfile, 'sha256')

words = [word for word in words if "'" not in word]
words = sorted(set(words))
log(f'loaded {len(words)} words from {args.wordfile.name} {sig.hexdigest()}')

search = Search(words, context=args.context, log=log)

try:
    print(f'searching {search.remain} words')
    while search.remain > 0:
        search.progress()
        print(f'{search.remain} words left ( {(search.remain/len(search.words)) * 100}% )')
    print(f'done: {search.result}')
except (EOFError, KeyboardInterrupt, StopIteration):
    pass
