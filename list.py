#!/usr/bin/env python

import argparse
from collections.abc import Sequence
from typing import cast, TextIO

from hack import WordList

Note = tuple[int, str]

def note(s: str) -> Note:
    si, _, mark = s.partition(':')
    i = int(si)
    return (i, mark or '???')

parser = argparse.ArgumentParser()
_ = parser.add_argument('--wordfile', type=argparse.FileType('r'), default='alphalist.txt')
_ = parser.add_argument('lo', type=int)
_ = parser.add_argument('hi', type=int)
_ = parser.add_argument('note', type=note, nargs='*')

args = parser.parse_args()

notes = dict(cast(Sequence[Note], args.note))
wordlist = WordList(cast(TextIO, args.wordfile))
print(wordlist.describe)
words = wordlist.words

word_range = range(cast(int, args.lo), cast(int, args.hi))

word_width = max(len(words[i]) for i in word_range)

for i in word_range: 
    i_note = notes.get(i, '')
    i_mark = f' <-- {i_note}' if i_note else ''
    print(f'{i} {words[i]:{word_width}}{i_mark}')

