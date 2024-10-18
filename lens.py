#!/usr/bin/env python

from collections import Counter
import sys

seen = set()
lens = Counter()

for line in sys.stdin:
    word = line.strip().lower().partition(' ')[0]
    if "'" in word: continue
    if word in seen: continue
    lens[len(word)] += 1
    seen.add(word)

for n in range(max(lens)+1):
    count = lens[n]
    print(f'{n : > 3} {count}')
