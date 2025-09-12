# Dev

## WIP

- share conversion is scuffed wrt "dictionary.com hurdle 🧩" ; needs to skip
  any number of tokens up to the puzzle

- missing puzzle id from hurdle and dontwordle should now be fixed

- meta is basically done
  - [ ] store daily share(d) state
  - [ ] better logic circa end of day early play, e.g. doing a CET timezone
        puzzle close late in the "prior" day local (EST) time
  - [ ] similarly, early play of next-day spaceword should work gracefully

## TODO

- store: fin is not quite right yet
- space: post fin `! store -> tail -> continue` implies `not run_done`
- square: finish questioning work

