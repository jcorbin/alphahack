# 2025-09-13

- 🔗 spaceword.org 🧩 2025-09-12 🏗️ score 2165 current ranking 102/204 ⏱️ 2:52:58.208380

# Dev

## WIP

- share conversion is scuffed wrt "dictionary.com hurdle 🧩" ; needs to skip
  any number of tokens up to the puzzle

- missing puzzle id from hurdle and dontwordle should now be fixed

- fin on ephemeral stored log should cutover to a non-ephemeral log, whether
  stored or working copy

## TODO

- better meta
  - [ ] store daily share(d) state
  - [ ] better logic circa end of day early play, e.g. doing a CET timezone
        puzzle close late in the "prior" day local (EST) time
  - [ ] similarly, early play of next-day spaceword should work gracefully

- square: finish questioning work

- space higher level automation:
  ```
  {set capn = 750}

  /sea -cap {capn}
  {expect done}
  show done
  show {highest score index ; why isn't this just 1}
  ret
  {:loop}
  /sea -cap {2*capn}
  {expect done ; if not, retry up to 2 times? ; else just continue with earlier result}
  show done
  show {highest score index ; why isn't this just 1}
  ret
  {:continue}

  {present to user for entry}
  {expect score ; are we good enough yet? -- e.g. stop daily at 2173}
  {set capn *= 2}

  /sea -clear -cap {capn}
  {expect done ; if not, retry up to 4 times? does cap grow with retry #?}
  show done
  show {highest score index ; why isn't this just 1}
  ret
  {:loop}
  /sea -cap {capn}
  {expect done ; if not, retry up to 2 times? ; else just continue with earlier result}
  show done
  show {highest score index ; why isn't this just 1}
  ret
  {:continue}

  {present to user for entry}
  {expect score ; are we good enough yet? -- e.g. stop daily at 2173}
  # ...

  # TODO how about a deadline? in terms of state rounds and/or time?

  ```

# spaceword.org 🧩 2025-09-12 🏗️ score 2165 current ranking 102/204 ⏱️ 2:52:58.208380

📜 4 sessions
- tiles: 21/21
- score: 2165 bonus: +65
- rank: 102/204

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ P A I L _ _ _ _   
      _ _ _ V _ _ U _ O _   
      _ _ B A S E N J I _   
      _ _ _ _ H _ _ _ K _   
      _ _ A T O N E _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

