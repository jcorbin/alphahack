# 2026-08-19

- 🔗 wordgrid 🧩 #809 🟪 rarity:0.15 ⏱️ 0:05:34.496398
- 🔗 spaceword.org 🧩 2026-08-18 🏁 score 2165 ranked 38.4% 131/341 ⏱️ 1:07:05.129373
- 🔗 alfagok.diginaut.net 🧩 #655 🥳 46 ⏱️ 0:00:58.203593
- 🔗 alphaguess.com 🧩 #1122 🥳 32 ⏱️ 0:00:31.291526
- 🔗 cemantix.certitudes.org 🧩 #1631 🥳 133 ⏱️ 0:16:27.883250
- 🔗 dontwordle.com 🧩 #1548 🥳 6 ⏱️ 0:01:03.409558
- 🔗 dictionary.com hurdle 🧩 #1691 🥳 17 ⏱️ 0:03:04.410299
- 🔗 Quordle Classic 🧩 #1668 🥳 score:22 ⏱️ 0:01:59.556000
- 🔗 Octordle Classic 🧩 #1668 🥳 score:60 ⏱️ 0:02:06.264177
- 🔗 Sedecordle Classic 🧩 #1648 🥳 score:33 ⏱️ 0:03:06.042003
- 🔗 squareword.org 🧩 #1661 🥳 8 ⏱️ 0:02:02.461780
- 🔗 cemantle.certitudes.org 🧩 #1598 🥳 139 ⏱️ 0:09:40.043255

## WIP

- new puzzle: https://fubargames.se/squardle/

- hurdle: add novel words to wordlist

- meta:
  - reprise SolverHarness around `do_sol_*`, re-use them under `do_solve`

- ui:
  - Handle -- stabilizing core over Listing
  - Shell -- minimizing over Handle
- meta: rework command model over Shell
- finish `StoredLog.load` decomposition

## TODO

- semantic:
  - allow "stop after next prompt done" interrupt
  - factor out executive multi-strategy full-auto loop around the current
    best/recent "broad" strategy
  - add a "spike"/"depth" strategy that just tried to chase top-N
  - add model attribution to progress table
  - add used/explored/exploited/attempted counts to prog table
  - ... use such count to get better coverage over hot words
  - ... may replace `~N` scoring

- [regexle](https://regexle.com): on program

- dontword:
  - upstream site seems to be glitchy wrt generating result copy on mobile
  - workaround by synthesizing?
  - workaround by storing complete-but-unverified anyhow?

- hurdle: report wasn't right out of #1373 -- was missing first few rounds

- square: finish questioning work

- reuse input injection mechanism from store
  - wherever the current input injection usage is
  - and also to allow more seamless meta log continue ...

- meta:
  - alfagok lines not getting collected
    ```
    pick 4754d78e # alfagok.diginaut.net day #345
    ```
  - `day` command needs to be able to progress even without all solvers done
  - `day` pruning should be more agro
  - better logic circa end of day early play, e.g. doing a CET timezone puzzle
    close late in the "prior" day local (EST) time; similarly, early play of
    next-day spaceword should work gracefully
  - support other intervals like weekly/monthly for spaceword
  - review should progress main branch too

- StoredLog:
  - log compression can sometimes get corrupted; spaceword in particular tends
    to provoke this bug
  - log event generation and pattern matching are currently too disjointed
    - currently the event matching is all collected under a `load` method override:
      ```python
      class Whatever(StoredLog):
        @override
        def load(self, ui: PromptUI, lines: Iterable[str]):
          for t, rest in super().load(ui, lines):
            orig_rest = rest
            with ui.exc_print(lambda: f'while loading {orig_rest!r}'):

              m = re.match(r'''(?x)
                bob \s+ ( .+ )
                $''', rest)
              if m:
                  wat = m[1]
                  self.apply_bla(wat)
                  continue

              yield t, rest

      ```
      * not all subclasses provide the exception printing facility...
      * many similar `if-match-continue` leg under the loop-with
      * ideally state re-application is a cleanly nominated method like `self.applay_bla`
    - so then event generation usually looks like:
      ```python
      class Whatever(StoredLog):
        def do_bla(self, ui: PromptUI):
          wat = 'lob law'
          ui.log(f'bob {wat}')
          self.apply_bla(wat)

        def apply_bla(self, wat: str):
          self.wat.append(wat)

        def __init__(self):
          self.wat: list[str] = []
      ```
      * this again is in an ideal, in practice logging is frequently intermixed
        with state mutation; i.e. the `apply_` and `do_` methods are fused
      * note also there is the matter of state (re-)initialization to keep in
        mind as well; every part must have a declaration under `__init__`
    - so a first seam to start pulling at here would be to unify event
      generation and matching with some kinda decorator like:
      ```python
      class Whatever(StoredLog):
        @StateEvent(
          lambda wat: f'bob {wat}',
          r'''(?x)
            bob \s+ ( .+ )
            $''',
        )
        def apply_bla(self, wat: str):
          self.wat.append(wat)
      ```
  - would be nice if logs could contain multiple concurrent sessions
    - each session would need an identifier
    - each session would then name its parent(s)
    - at least for bakcwards compat, we need to support reading sid-less logs
      - so each log entry's sid needs to default to last-seen
      - and each session needs to get a default sid generated
      - for default parentage, we'll just go with last-wins semantics
    - but going forward the log format becomes `S<id> T<t> ...`
      - or is that `T[sid.]t ...` ; i.e. session id is just an extra dimension
        of time... oh I like that...
    - so replay needs to support a frontier of concurrent sessions
    - and load should at least collect extant sibling IDs
    - so a merge would look like:
      1. prior log contains concurrent sessions A and B
      2. start new session C parented to A
      3. its load logic sees extant B
         * loads B's state
         * reconciles, logging catch-up state mutations
         * ending in reconciliation done log entry
      4. load logic no longer recognizes B as extant
         * ... until/unless novel log entries are seen from it

- expired prompt could be better:
  ```
  🔺 -> <ui.Prompt object at 0x754fdf9f6190>
  🔺 <ui.Prompt object at 0x754fdf9f6190>[f]inalize, [a]rchive, [r]emove, or [c]ontinue? rem
  🔺 'rem' -> StoredLog.expired_do_remove
  ```
  - `rm` alias
  - dynamically generated suggestion prompt, or at least one that's correct ( as "r" is ambiguously actually )

- ui: [disabled] thrash detection works too well
  - triggers on semantic's extract-next-token tight loop
  - best way to reliably fix it is to capture per-round output, and only count
    thrash if output is looping

- long lines like these are hard to read; a line-breaking pretty formatter
  would be nice:
  ```
  🔺 -> functools.partial(<function Search.do_round.<locals>.wrap at 0x7f8ef4e0f100>, st=<wordlish.Question object at 0x7f8ef4e52e90>)
  🔺 functools.partial(<function Search.do_round.<locals>.wrap at 0x7f8ef4e0f100>, st=<wordlish.Question object at 0x7f8ef4e52e90>)#1 ____S ~E -ANT  📋 "elder" ? _L__S ~ ESD
  ```

- semantic: final stats seems lightly off ; where's the party?
  ```
  Fin   $1 #234 compromise         100.00°C 🥳 1000‰
      🥳   0
      😱   0
      🔥   5
      🥵   6
      😎  37
      🥶 183
      🧊   2
  ```

- replay last paste to ease dev sometimes

- space: can loose the wordlist plot:
  ```
  *** Running solver space
  🔺 <spaceword.SpaceWord object at 0x71b358e51350> -> <SELF>
  🔺 <spaceword.SpaceWord object at 0x71b358e51350>
  ! expired puzzle log started 2025-09-13T15:10:26UTC, but next puzzle expected at 2025-09-14T00:00:00EDT
  🔺 -> <ui.Prompt object at 0x71b358e5a040>
  🔺 <ui.Prompt object at 0x71b358e5a040>[f]inalize, [a]rchive, [r]emove, or [c]ontinue? rem
  🔺 'rem' -> StoredLog.expired_do_remove

  // removed spaceword.log
  🔺 -> <spaceword.SpaceWord object at 0x71b358e51350>
  🔺 <spaceword.SpaceWord object at 0x71b358e51350> -> <SELF>
  🔺 <spaceword.SpaceWord object at 0x71b358e51350> -> StoredLog.handle
  🔺 StoredLog.handle
  🔺 StoredLog.run
  📜 spaceword.log with 0 prior sessions over 0:00:00
  🔺 -> SpaceWord.startup
  🔺 SpaceWord.startup📜 /usr/share/dict/words ?
  ```

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







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #781 🟪 rarity:0.15 ⏱️ 0:03:50.236694

📜 2 sessions
🌌 🦄 🦄
🌌 🦄 🦄
🌌 🌌 🌌
Rarity: 0.15 🟪


# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #-1 ❗ rarity:nan ⏱️ 0:05:19.095498

📜 2 sessions
🌌 🦄 🌌
🌌 🦄 🌌
🌌 🦄 🌌
Rarity: nan ❗







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #788 🟪 rarity:0.29 ⏱️ 0:03:24.033720

📜 2 sessions
🦄 🦄 🌌
🦄 🦄 🦄
🌌 🦄 🌌
Rarity: 0.29 🟪


# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #789 🟪 rarity:0.23 ⏱️ 0:02:56.015327

📜 2 sessions
🌌 🌌 🌌
🦄 🦄 🌌
🦄 🦄 🦄
Rarity: 0.23 🟪







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #795 🟪 rarity:0.27 ⏱️ 0:03:44.973967

📜 2 sessions
🦄 🌌 🌌
🌌 🌌 🌌
🦄 🦄 🌌
Rarity: 0.27 🟪















# [spaceword.org](spaceword.org) 🧩 2026-08-18 🏁 score 2165 ranked 38.4% 131/341 ⏱️ 1:07:05.129373

📜 3 sessions
- tiles: 21/21
- score: 2165 bonus: +65
- rank: 131/341

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ O _ C U E _ _   
      _ _ _ R _ O _ L _ _   
      _ _ _ Z _ Q _ L _ _   
      _ _ _ O _ U _ _ _ _   
      _ _ _ S W I M _ _ _   
      _ _ _ _ _ T A U _ _   
      _ _ _ _ H O _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #809 🟪 rarity:0.15 ⏱️ 0:05:34.496398

📜 2 sessions
🌌 🌌 🌌
🌌 🦄 🦄
🦄 🦄 🦄
Rarity: 0.15 🟪



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #655 🥳 46 ⏱️ 0:00:58.203593

🤔 46 attempts
📜 1 sessions

    @        [     0] &-teken         
    @+199547 [199547] lij             q0  ? ␅
    @+199547 [199547] lij             q1  ? after
    @+199547 [199547] lij             q2  ? ␅
    @+199547 [199547] lij             q3  ? after
    @+199547 [199547] lij             q4  ? ␅
    @+199547 [199547] lij             q5  ? after
    @+223533 [223533] molen           q10 ? ␅
    @+223533 [223533] molen           q11 ? after
    @+229509 [229509] natuur          q14 ? ␅
    @+229509 [229509] natuur          q15 ? after
    @+232520 [232520] niets           q16 ? ␅
    @+232520 [232520] niets           q17 ? after
    @+233243 [233243] ninja           q30 ? ␅
    @+233243 [233243] ninja           q31 ? after
    @+233578 [233578] non             q32 ? ␅
    @+233578 [233578] non             q33 ? after
    @+233693 [233693] nood            q34 ? ␅
    @+233693 [233693] nood            q35 ? after
    @+233828 [233828] noodplan        q36 ? ␅
    @+233828 [233828] noodplan        q37 ? after
    @+233894 [233894] noodvaccinaties q38 ? ␅
    @+233894 [233894] noodvaccinaties q39 ? after
    @+233927 [233927] noodzaak        q40 ? ␅
    @+233927 [233927] noodzaak        q41 ? after
    @+233944 [233944] noodziekenhuis  q42 ? ␅
    @+233944 [233944] noodziekenhuis  q43 ? after
    @+233949 [233949] nooit           q44 ? ␅
    @+233949 [233949] nooit           q45 ? it
    @+233949 [233949] nooit           done. it
    @+233960 [233960] noord           q19 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1122 🥳 32 ⏱️ 0:00:31.291526

🤔 32 attempts
📜 1 sessions

    @        [     0] aa       
    @+98147  [ 98147] mac      q0  ? ␅
    @+98147  [ 98147] mac      q1  ? after
    @+98147  [ 98147] mac      q2  ? ␅
    @+98147  [ 98147] mac      q3  ? after
    @+98147  [ 98147] mac      q4  ? ␅
    @+98147  [ 98147] mac      q5  ? after
    @+122724 [122724] parol    q10 ? ␅
    @+122724 [122724] parol    q11 ? after
    @+128842 [128842] play     q14 ? ␅
    @+128842 [128842] play     q15 ? after
    @+130056 [130056] poly     q18 ? ␅
    @+130056 [130056] poly     q19 ? after
    @+130985 [130985] possess  q20 ? ␅
    @+130985 [130985] possess  q21 ? after
    @+131364 [131364] pot      q22 ? ␅
    @+131364 [131364] pot      q23 ? after
    @+131381 [131381] potato   q30 ? ␅
    @+131381 [131381] potato   q31 ? it
    @+131381 [131381] potato   done. it
    @+131404 [131404] potent   q28 ? ␅
    @+131404 [131404] potent   q29 ? before
    @+131482 [131482] pots     q26 ? ␅
    @+131482 [131482] pots     q27 ? before
    @+131623 [131623] power    q24 ? ␅
    @+131623 [131623] power    q25 ? before
    @+131923 [131923] prealter q16 ? ␅
    @+131923 [131923] prealter q17 ? before
    @+135004 [135004] prop     q12 ? ␅
    @+135004 [135004] prop     q13 ? before
    @+147311 [147311] rho      q9  ? before

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1631 🥳 133 ⏱️ 0:16:27.883250

🤔 134 attempts
📜 1 sessions
🫧 13 chat sessions
⁉️ 62 chat prompts
🤖 62 dolphin3:latest replies
🔥   3 🥵   3 😎   4 🥶 107 🧊  16

      $1 #134 brouillard      100.00°C 🥳 1000‰ ~118 used:0  [117]  source:dolphin3
      $2 #128 nuage            62.92°C 🔥  998‰   ~3 used:2  [2]    source:dolphin3
      $3 #130 orage            49.90°C 🔥  991‰   ~1 used:0  [0]    source:dolphin3
      $4 #131 pluie            49.71°C 🔥  990‰   ~2 used:0  [1]    source:dolphin3
      $5 #129 ciel             43.77°C 🥵  973‰   ~4 used:0  [3]    source:dolphin3
      $6 #124 ombre            42.55°C 🥵  968‰   ~6 used:10 [5]    source:dolphin3
      $7 #132 tempête          36.96°C 🥵  908‰   ~5 used:0  [4]    source:dolphin3
      $8  #28 panache          29.66°C 😎  682‰  ~10 used:34 [9]    source:dolphin3
      $9 #126 silhouette       26.88°C 😎  432‰   ~8 used:3  [7]    source:dolphin3
     $10 #125 ombreux          26.21°C 😎  344‰   ~7 used:0  [6]    source:dolphin3
     $11  #58 manteau          25.53°C 😎  228‰   ~9 used:31 [8]    source:dolphin3
     $12   #8 voile            24.09°C 🥶        ~11 used:40 [10]   source:dolphin3
     $13  #40 capuche          22.86°C 🥶        ~15 used:7  [14]   source:dolphin3
    $119 #121 cachemire        -0.37°C 🧊       ~119 used:0  [118]  source:dolphin3

# [dontwordle.com](dontwordle.com) 🧩 #1548 🥳 6 ⏱️ 0:01:03.409558

📜 1 sessions
💰 score: 16

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:7346
    ⬜⬜⬜⬜⬜ tried:MORRO n n n n n remain:2582
    ⬜⬜⬜⬜⬜ tried:JUKUS n n n n n remain:586
    ⬜⬜⬜⬜🟩 tried:PHPHT n n n n Y remain:35
    🟨⬜⬜⬜🟩 tried:ABAFT m n n n Y remain:5
    ⬜🟨🟨🟨🟩 tried:TACET n m m m Y remain:2

    Undos used: 1

      2 words remaining
    x 8 unused letters
    = 16 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1691 🥳 17 ⏱️ 0:03:04.410299

📜 1 sessions
💰 score: 9900

    3/6
    TASER 🟩🟨⬜⬜🟨
    TRAIN 🟩🟩🟩⬜⬜
    TRACK 🟩🟩🟩🟩🟩
    4/6
    TRACK ⬜⬜⬜⬜🟨
    HIKES ⬜⬜🟨⬜🟨
    SULKY 🟩⬜⬜🟩🟩
    SMOKY 🟩🟩🟩🟩🟩
    4/6
    SMOKY ⬜🟨🟨⬜⬜
    LEMON ⬜⬜🟨🟨⬜
    MICRO 🟩⬜🟩⬜🟨
    MOCHA 🟩🟩🟩🟩🟩
    4/6
    MOCHA ⬜⬜⬜🟩⬜
    EIGHT 🟨🟩⬜🟩🟨
    WALKS ⬜⬜🟨⬜⬜
    LITHE 🟩🟩🟩🟩🟩
    Final 2/2
    ROWED 🟩🟩🟩🟩⬜
    ROWER 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1668 🥳 score:22 ⏱️ 0:01:59.556000

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. BINGE attempts:6 score:6
2. RIVAL attempts:4 score:4
3. PIVOT attempts:5 score:5
4. MAIZE attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1668 🥳 score:60 ⏱️ 0:02:06.264177

📜 1 sessions

Octordle Classic

1. BLAST attempts:4 score:4
2. VERGE attempts:8 score:8
3. PUSHY attempts:5 score:5
4. TRAIN attempts:9 score:9
5. GLEAN attempts:7 score:7
6. IMBUE attempts:6 score:6
7. MACRO attempts:10 score:10
8. TENOR attempts:11 score:11

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1648 🥳 score:33 ⏱️ 0:03:06.042003

📜 1 sessions

Sedecordle Classic sedecordle.com

1. TWIST attempts:7 score:0
2. CRIME attempts:8 score:7
3. CHILD attempts:4 score:0
4. TRUER attempts:9 score:4
5. ROUGE attempts:10 score:1
6. PALSY attempts:6 score:0
7. CYCLE attempts:5 score:0
8. CRAZE attempts:19 score:5
9. GLOSS attempts:11 score:1
10. CLAMP attempts:12 score:1
11. CLASP attempts:19 score:2
12. BELIE attempts:13 score:0
13. EXCEL attempts:14 score:1
14. SINGE attempts:15 score:4
15. WRITE attempts:16 score:1
16. SKUNK attempts:17 score:6

# [squareword.org](squareword.org) 🧩 #1661 🥳 8 ⏱️ 0:02:02.461780

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    L A T C H
    A L O H A
    D I N E R
    E V I C T
    N E C K S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1598 🥳 139 ⏱️ 0:09:40.043255

🤔 140 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 47 chat prompts
🤖 10 gemma4:12b replies
🤖 37 dolphin3:latest replies
🥵   6 😎  16 🥶 110 🧊   7

      $1 #140 ruin          100.00°C 🥳 1000‰ ~133 used:0  [132]  source:gemma4  
      $2 #102 disintegrate   47.56°C 🥵  976‰  ~21 used:31 [20]   source:dolphin3
      $3 #103 crumble        46.66°C 🥵  973‰  ~20 used:22 [19]   source:dolphin3
      $4  #84 erode          41.85°C 🥵  939‰  ~18 used:15 [17]   source:dolphin3
      $5 #127 shatter        40.74°C 🥵  928‰   ~2 used:5  [1]    source:gemma4  
      $6 #134 collapse       39.77°C 🥵  918‰   ~1 used:3  [0]    source:gemma4  
      $7 #114 disappear      38.69°C 🥵  901‰   ~3 used:10 [2]    source:dolphin3
      $8 #124 vanish         36.90°C 😎  863‰  ~19 used:2  [18]   source:dolphin3
      $9 #110 deteriorate    36.77°C 😎  859‰   ~4 used:1  [3]    source:dolphin3
     $10 #101 degrade        36.19°C 😎  844‰   ~5 used:0  [4]    source:dolphin3
     $11  #31 precipice      34.69°C 😎  794‰  ~22 used:8  [21]   source:dolphin3
     $12 #137 wither         34.52°C 😎  783‰   ~6 used:0  [5]    source:gemma4  
     $24  #42 rocky          26.72°C 🥶        ~23 used:6  [22]   source:dolphin3
    $134  #92 process        -0.62°C 🧊       ~134 used:0  [133]  source:dolphin3
