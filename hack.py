#!/usr/bin/env python

import argparse
import math

class Search(object):
    def __init__(self, words, context=3):
        self.words = sorted(words)
        self.lo = 0
        self.hi = len(self.words)
        self.context = context
        self.logfile = None

    @property
    def result(self):
        return None

    @property
    def done(self):
        if self.result is not None:
            return True
        if self.remain <= 0:
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

        ctx = self.words[ctx_lo:ctx_hi]
        way, index = self.prompt(ctx, ctx_lo)
        print(f'{way} {index} {self.words[index]}', file=self.logfile)

        assert(index >= ctx_lo)
        assert(index < ctx_hi)
        if way > 0:
            self.lo = index
        elif way < 0:
            self.hi = index + 1
        else:
            raise 'invalid way code'

    def prompt(self, ctx, offset):
        for i, word in enumerate(ctx):
            print(offset + i, word)
        while True:
            resp = input('> ')
            print(f'> {resp}', file=self.logfile)

            try:
                way, which = resp.split()
            except ValueError:
                continue

            way_code = (
                1 if way.lower().startswith('a')
                else -1 if way.lower().startswith('b')
                else None)
            if way_code is None:
                print('! invalid direction', way, '; expected a(fter) or b(efore)')
                continue

            for i, word in enumerate(ctx, start=offset):
                if self.words[i] == word.lower():
                    return way_code, i

            which_ix = [
                i
                for i, word in enumerate(ctx, start=offset)
                if word.startswith(which.lower())]

            if len(which_ix) == 0:
                print('! invalid word', which, '; choose one of:')
                for i, word in enumerate(ctx):
                    print(offset + i, word)
                # TODO use the result anyhow? if user meant it...
                continue

            if len(which_ix) > 1:
                print('! ambiguous word', which, '; could be:')
                for i in which_ix:
                    print(i, self.words[i])
                # TODO use the result anyhow? if user meant it...
                continue

            return way_code, which_ix[0]

parser = argparse.ArgumentParser()
parser.add_argument('--context', type=int, default=3, help='how many words to show +/- query');
parser.add_argument('--log', default='/dev/null', type=argparse.FileType('w'))
parser.add_argument('wordfile', type=argparse.FileType('r'))
args = parser.parse_args()

with args.wordfile as wordfile:
    words = [word.strip().lower() for word in wordfile]

words = [word for word in words if "'" not in word]

search = Search(words, context=args.context)
search.logfile = args.log

try:
    while search.remain > 0:
        print(f'{search.remain} words left ( {(search.remain/len(search.words)) * 100}% )')
        search.progress()
except (EOFError, KeyboardInterrupt, StopIteration):
    pass
