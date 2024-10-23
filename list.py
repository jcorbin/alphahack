#!/usr/bin/env python

import argparse
import hashlib
import math
from hack import WordList

def note(s):
    si, _, mark = s.partition(':')
    i = int(si)
    return (i, mark or '???')

parser = argparse.ArgumentParser()
parser.add_argument('--wordfile', type=argparse.FileType('r'), default='alphalist.txt')
parser.add_argument('lo', type=int)
parser.add_argument('hi', type=int)
parser.add_argument('note', type=note, nargs='*')

args = parser.parse_args()

notes = dict(args.note)
wordlist = WordList(args.wordfile)

print(f'loaded {wordlist.size} words from {wordlist.name} {wordlist.sig.hexdigest()}')

word_width = max(
    len(wordlist.words[i])
    for i in range(args.lo, args.hi))

for i in range(args.lo, args.hi): 
    note = notes.get(i) or ''
    print(f'{i} {wordlist.words[i]:{word_width}}{" <-- " if note else ""}{note}')

