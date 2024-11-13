#!/usr/bin/env python

from collections import Counter
import sys

seen: set[str] = set()
lens: Counter[int] = Counter()

for line in sys.stdin:
    word = line.strip().lower().partition(' ')[0]
    if "'" in word: continue
    if word in seen: continue
    lens[len(word)] += 1
    seen.add(word)

on = False
for n in range(max(lens)+1):
    count = lens[n]
    if not count and not on: continue
    on = True
    print(f'{n : > 3} {count}')
