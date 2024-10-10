#!/usr/bin/env python

import argparse
import datetime
import time

parser = argparse.ArgumentParser()
parser.add_argument('word')
args = parser.parse_args()
word = args.word.strip().lower()

pre = ''
post = ''
guesses = []
found = False
start = time.clock_gettime(time.CLOCK_MONOTONIC)

try:
    while True:
        guess = input(f'{pre} ??? {post} > ').strip().lower()
        guesses.append(guess)

        if guess == word:
            print('Correct:', guess)
            found = True
            break
        elif guess < word:
            print('After', guess)
            if not pre or word > pre: pre = guess
        elif guess > word:
            print('Before', guess)
            if not post or word < post: post = guess
        else:
            raise 'unreachable'
except (EOFError, KeyboardInterrupt, StopIteration):
    pass
end = time.clock_gettime(time.CLOCK_MONOTONIC)


if found:
    took = datetime.timedelta(seconds=end - start)
    print(f'Found after {len(guesses)} guesses in {took}')
