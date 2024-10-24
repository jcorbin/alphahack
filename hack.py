#!/usr/bin/env python

import hashlib
import math
import time

from datetime import timedelta

class Timer(object):
    def __init__(self, start = None):
        self.start = time.clock_gettime(time.CLOCK_MONOTONIC) if start is None else start
        self.last = self.start

    @property
    def now(self):
        now = time.clock_gettime(time.CLOCK_MONOTONIC)
        return now - self.start

    def sub(self):
        return Timer(self.now)

class Search(object):
    def __init__(self, words, context=3, log=lambda: None, provide=lambda: None, get_input=input):
        self.words = sorted(words)
        self.context = context
        self.log = log
        self.provide = provide
        self.get_input = get_input

        self.lo = 0
        self.hi = len(self.words)

        self.view_factor = 2
        self.min_context = self.context

        self.may_suggest = True
        self.questioning = None
        self.view_at = 0

        self.added = 0
        self.attempted = 0
        self.entered = 0
        self.questioned = 0
        self.removed = 0
        self.suggested = 0

        self.chosen = None

    @property
    def view_lo(self):
        return max(0, self.view_at - self.context)

    @property
    def view_hi(self):
        return min(self.hi-1, self.view_at + self.context)

    @property
    def result_i(self):
        if self.chosen is not None:
            return self.chosen
        if self.remain == 1:
            return self.lo
        return None

    @property
    def result(self):
        i = self.result_i
        return None if i is None else self.words[i]

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

    def remove(self, at):
        word = self.words.pop(at)
        if at < self.lo: self.lo -= 1
        if at <= self.hi: self.hi -= 1
        if self.questioning is not None and at <= self.questioning:
            self.questioning -= 1
        self.removed += 1

    def insert(self, at, word):
        self.words.insert(at, word)
        if at < self.lo: self.lo += 1
        if at <= self.hi: self.hi += 1
        if self.questioning is not None and at <= self.questioning:
            self.questioning += 1
        self.added += 1

    def progress(self):
        if self.done: raise StopIteration

        compare, index = self.prompt()
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
        # NOTE window order from wider to narrower means first match
        #      will be the one that spans the most word list entries
        for win_lo, win_hi in (
            (lo+offset, lo+offset+n)
            for n in range(hi-lo, 1, -1)
            for offset in range(hi-lo - n + 1)
        ):
            prefix = self.common_prefix(win_lo, win_hi)
            while prefix:
                pi = self.find(prefix)
                if not (self.lo < pi < self.hi): break
                if self.words[pi] == prefix: return pi
                prefix = prefix[:-1]

    def prompt(self):
        self.may_suggest = True
        self.questioning = None
        self.view_at = math.floor(self.lo/2 + self.hi/2)
        self.log(f'... {self.lo} {self.view_lo} {self.view_at} {self.view_hi} {self.hi}')
        while True:
            res = self.question() or self.choose()
            if res is not None: return res

    def input(self, prompt):
        try:
            resp = self.get_input(prompt)
        except EOFError:
            self.log(f'{prompt}␚')
            raise
        self.log(f'{prompt}{resp}')
        return resp

    def question(self, qi=None):
        if qi is None:
            qi = self.questioning
            if qi is None: return
        else:
            self.questioning = qi
            self.questioned += 1

        word = self.words[qi]
        self.provide(word)
        tokens = self.input(f'[{self.lo} : {qi} : {self.hi}] {word}? ').lower().split()
        if len(tokens) > 1:
            self.may_suggest = False
            self.questioning = None
            return self.handle_choose(tokens)

        token = tokens[0] if len(tokens) > 0 else ''
        if all(c == '.' for c in token):
            self.may_suggest = False
            self.questioning = None
            return

        if token == '!':
            self.remove(qi)
            self.questioning = None
            return

        compare = parse_compare(token)
        if compare is None:
            print(f'! invalid direction {token} ; expected a(fter), b(efore), i(t), or ! (to remove word)')
            return

        self.attempted += 1
        return compare, qi

    def choose(self):
        pi = self.valid_prefix(self.view_lo, self.view_hi)

        if self.may_suggest:
            self.suggested += 1
            return self.question(self.view_at if pi is None else pi)

        cur = None
        def note(i, mark=''):
            nonlocal cur
            if cur is not None and cur < i-1:
                print('    ...')
            print(f'    [{i}] {self.words[i]}{mark}')
            cur = i

        note(self.lo)
        if pi is not None and pi < self.view_lo: note(pi, ' <')
        for i in range(self.view_lo, self.view_hi): note(i, ' @' if i == self.view_at else '')
        note(self.hi-1)

        return self.handle_choose(self.input('> ').lower().split())

    def handle_choose(self, tokens):
        try:
            token = tokens[0]
        except IndexError:
            print('! expected response like: `[+|-|<word>]...`')
            return

        if token == '+':
            self.context *= self.view_factor
            return
        if token == '-':
            self.context = max(self.min_context, math.floor(self.context / 2))
            return

        at = self.find(token)
        if self.words[at] != token:
            confirm = (
                len(tokens) > 2 and tokens[2] or
                input(f'! unknown word {token} ; respond . to add, else to re-prompt> '))
            if confirm.strip() == '.':
                self.insert(at, token)

        self.entered += 1
        return self.question(at)

def parse_compare(s):
    if 'after'.startswith(s):
        return 1
    elif 'before'.startswith(s):
        return -1
    elif 'it'.startswith(s):
        return 0
    else:
        return None

class WordList(object):
    def __init__(self, fable):
        self.name = fable.name
        with fable as f:
            words = [
                line.strip().lower().partition(' ')[0]
                for line in f
            ]
        words = [word for word in words if "'" not in word]
        words = sorted(set(words))
        self.words = words

    @property
    def size(self):
        return len(self.words)

    @property
    def sig(self):
        with open(self.name, 'rb') as f:
            return hashlib.file_digest(f, 'sha256')

def main():
    import argparse
    import pyperclip as pc
    import shlex
    import subprocess

    parser = argparse.ArgumentParser()
    parser.add_argument('--context', type=int, default=3, help='how many words to show +/- query');
    parser.add_argument('--provide', help='command to run after clipboard copy');
    parser.add_argument('--log', default='hack.log', type=argparse.FileType('w'))
    parser.add_argument('--input', action='extend', nargs='+', type=str)
    parser.add_argument('--at', nargs=2, type=int)
    parser.add_argument('--words', default='alphalist.txt', type=argparse.FileType('r'))
    args = parser.parse_args()

    logtime = Timer()
    logfile = args.log

    def log(*mess):
        print(f'T{logtime.now}', *mess, file=logfile)
        logfile.flush()

    provide_args = shlex.split(args.provide) if args.provide else ()

    def provide(word):
        pc.copy(word)
        if provide_args:
            subprocess.call(provide_args)

    input_index = 0

    def get_input(prompt):
        global input_index
        if args.input and input_index < len(args.input):
            prov = args.input[input_index]
            print(f'{prompt}{prov}')
            input_index += 1
            return prov
        return input(prompt)

    wordlist = WordList(args.words)
    log(f'loaded {wordlist.size} words from {wordlist.name} {wordlist.sig.hexdigest()}')

    search = Search(
        wordlist.words,
        context=args.context,
        log=log,
        provide=provide,
        get_input=get_input,
    )
    if args.at is not None:
        search.lo, search.hi = args.at

    try:
        print(f'searching {search.remain} words')
        while search.remain > 0:
            search.progress()
    except EOFError:
        print(' <EOF>')
    except KeyboardInterrupt:
        print(' <INT>')
    except StopIteration:
        print(' <STOP>')
    print()

    took = timedelta(seconds=logtime.now)
    res = f'gave up' if search.result is None else f'found "{search.result}"'

    def details():
        if search.questioned != search.attempted:
            yield f'questioned:{search.questioned}'
        if search.suggested != 0:
            yield f'auto:{search.suggested}'
        if search.entered != 0:
            yield f'manual:{search.entered}'
        if search.added != 0:
            yield f'added:{search.added}'
        if search.removed != 0:
            yield f'removed:{search.removed}'

    deets = ' '.join(details())
    if deets: deets = f' ( {deets} )'

    print(f'{res} after {search.attempted} guesses in {took}{deets}')

if __name__ == '__main__':
    main()
