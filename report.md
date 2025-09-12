# 2025-09-13

- 🔗 spaceword.org 🧩 2025-09-12 🏗️ score 2160 current ranking 123/185 ⏱️ 1:08:19.546118

# Dev

## WIP

- share conversion is scuffed wrt "dictionary.com hurdle 🧩" ; needs to skip
  any number of tokens up to the puzzle

- missing puzzle id from hurdle and dontwordle should now be fixed
- store: fin seems fine actually?
- space: post fin seems fine actually?

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

  ```

# spaceword.org 🧩 2025-09-12 🏗️ score 2160 current ranking 123/185 ⏱️ 1:08:19.546118

📜 3 sessions
- tiles: 21/21
- score: 2160 bonus: +60
- rank: 123/185

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ O H _ _ _ _ _   
      _ J O V I A L _ _ _   
      _ _ _ I N T A K E _   
      _ B U N _ _ _ _ _ _   
      _ A P E S _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
