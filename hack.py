#!/usr/bin/env python

import argparse
import hashlib
import math

class Search(object):
    def __init__(self, words, context=3):
        self.words = sorted(words)
        self.lo = 0
        self.hi = len(self.words)
        self.context = context
        self.chosen = None
        self.logfile = None

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

    def progress(self):
        if self.done: raise StopIteration
        mid = math.floor(self.lo/2 + self.hi/2)
        ctx_lo = max(0, mid - self.context)
        ctx_hi = min(self.hi-1, mid + self.context)
        print(f'... {self.lo} {ctx_lo} {mid} {ctx_hi} {self.hi}', file=self.logfile)

        compare, index = self.prompt(ctx_lo, ctx_hi)
        print(f'{compare} {index} {self.words[index]}', file=self.logfile)

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

    def prompt(self, lo, hi):
        while True:
            for i in range(lo, hi): print(i, self.words[i])
            resp = input('> ')
            print(f'> {resp}', file=self.logfile)

            tokens = resp.lower().split()
            try:
                way, word = tokens
            except ValueError:
                continue

            compare = (
                1 if 'after'.startswith(way)
                else -1 if 'before'.startswith(way)
                else 0 if 'it'.startswith(way)
                else None)
            if compare is None:
                print(f'! invalid direction {way} ; expected a(fter) or b(efore)')
                continue

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
                self.words.insert(at, word)
                return compare, at

parser = argparse.ArgumentParser()
parser.add_argument('--context', type=int, default=3, help='how many words to show +/- query');
parser.add_argument('--log', default='/dev/null', type=argparse.FileType('w'))
parser.add_argument('wordfile', type=argparse.FileType('r'))
args = parser.parse_args()

with args.wordfile as wordfile:
    words = [word.strip().lower() for word in wordfile]

with open(args.wordfile.name, 'rb') as wordfile:
    sig = hashlib.file_digest(wordfile, 'sha256')

words = [word for word in words if "'" not in word]
words = sorted(set(words))
print(f'loaded {len(words)} words from {args.wordfile.name} {sig.hexdigest()}', file=args.log)

search = Search(words, context=args.context)
search.logfile = args.log

try:
    print(f'searching {search.remain} words')
    while search.remain > 0:
        search.progress()
        print(f'{search.remain} words left ( {(search.remain/len(search.words)) * 100}% )')
    print(f'done: {search.result}')
except (EOFError, KeyboardInterrupt, StopIteration):
    pass
