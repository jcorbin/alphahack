# 2026-02-27

- 🔗 spaceword.org 🧩 2026-02-26 🏁 score 2152 ranked 74.8% 267/357 ⏱️ 0:16:20.778735
- 🔗 alfagok.diginaut.net 🧩 #482 🥳 14 ⏱️ 0:00:23.334353
- 🔗 alphaguess.com 🧩 #949 🥳 22 ⏱️ 0:00:24.774798
- 🔗 dontwordle.com 🧩 #1375 🥳 6 ⏱️ 0:01:14.929803
- 🔗 dictionary.com hurdle 🧩 #1518 🥳 15 ⏱️ 0:02:51.484588
- 🔗 Quordle Classic 🧩 #1495 🥳 score:25 ⏱️ 0:02:25.871123
- 🔗 Octordle Classic 🧩 #1495 🥳 score:63 ⏱️ 0:03:35.481448
- 🔗 squareword.org 🧩 #1488 🥳 7 ⏱️ 0:01:58.413466
- 🔗 cemantle.certitudes.org 🧩 #1425 🥳 229 ⏱️ 0:01:49.557312
- 🔗 cemantix.certitudes.org 🧩 #1458 🥳 226 ⏱️ 0:06:52.512053

# Dev

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









# [spaceword.org](spaceword.org) 🧩 2026-02-26 🏁 score 2152 ranked 74.8% 267/357 ⏱️ 0:16:20.778735

📜 3 sessions
- tiles: 21/21
- score: 2152 bonus: +52
- rank: 267/357

      _ _ _ _ O _ _ _ _ _   
      _ _ _ _ P _ _ _ _ _   
      _ _ J _ A _ _ _ _ _   
      _ _ O _ Q _ _ _ _ _   
      _ _ K A U R I _ _ _   
      _ _ I _ E _ _ _ _ _   
      _ _ E _ L _ _ _ _ _   
      _ _ R H Y T O N _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #482 🥳 14 ⏱️ 0:00:23.334353

🤔 14 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+99741  [ 99741] ex        q2  ? ␅
    @+99741  [ 99741] ex        q3  ? after
    @+111396 [111396] ge        q6  ? ␅
    @+111396 [111396] ge        q7  ? after
    @+130417 [130417] gracieuze q8  ? ␅
    @+130417 [130417] gracieuze q9  ? after
    @+139774 [139774] hei       q10 ? ␅
    @+139774 [139774] hei       q11 ? after
    @+144543 [144543] hoek      q12 ? ␅
    @+144543 [144543] hoek      q13 ? it
    @+144543 [144543] hoek      done. it
    @+149437 [149437] huis      q4  ? ␅
    @+149437 [149437] huis      q5  ? before
    @+199816 [199816] lijm      q0  ? ␅
    @+199816 [199816] lijm      q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #949 🥳 22 ⏱️ 0:00:24.774798

🤔 22 attempts
📜 1 sessions

    @        [     0] aa         
    @+1      [     1] aah        
    @+2      [     2] aahed      
    @+3      [     3] aahing     
    @+98218  [ 98218] mach       q0  ? ␅
    @+98218  [ 98218] mach       q1  ? after
    @+147369 [147369] rhotic     q2  ? ␅
    @+147369 [147369] rhotic     q3  ? after
    @+153318 [153318] sea        q8  ? ␅
    @+153318 [153318] sea        q9  ? after
    @+156354 [156354] ship       q10 ? ␅
    @+156354 [156354] ship       q11 ? after
    @+156426 [156426] shirt      q20 ? ␅
    @+156426 [156426] shirt      q21 ? it
    @+156426 [156426] shirt      done. it
    @+156545 [156545] shlemiehls q18 ? ␅
    @+156545 [156545] shlemiehls q19 ? before
    @+156736 [156736] shop       q16 ? ␅
    @+156736 [156736] shop       q17 ? before
    @+157118 [157118] shrub      q14 ? ␅
    @+157118 [157118] shrub      q15 ? before
    @+157882 [157882] sim        q12 ? ␅
    @+157882 [157882] sim        q13 ? before
    @+159486 [159486] slop       q6  ? ␅
    @+159486 [159486] slop       q7  ? before
    @+171639 [171639] ta         q4  ? ␅
    @+171639 [171639] ta         q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1375 🥳 6 ⏱️ 0:01:14.929803

📜 1 sessions
💰 score: 56

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:AUDAD n n n n n remain:4708
    ⬜⬜⬜⬜⬜ tried:HOOCH n n n n n remain:1899
    ⬜⬜⬜⬜⬜ tried:VILLI n n n n n remain:554
    ⬜⬜⬜⬜⬜ tried:PYGMY n n n n n remain:214
    ⬜🟩⬜⬜🟩 tried:FEEZE n Y n n Y remain:15
    ⬜🟩⬜⬜🟩 tried:REBBE n Y n n Y remain:7

    Undos used: 3

      7 words remaining
    x 8 unused letters
    = 56 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1518 🥳 15 ⏱️ 0:02:51.484588

📜 1 sessions
💰 score: 10100

    4/6
    LAIRS ⬜⬜🟩⬜⬜
    THINE ⬜⬜🟩⬜⬜
    ODIUM 🟨🟩🟩⬜🟩
    IDIOM 🟩🟩🟩🟩🟩
    4/6
    IDIOM ⬜🟨⬜⬜⬜
    SHARD ⬜⬜🟩🟨🟨
    TRADE ⬜🟩🟩🟨🟩
    DRAKE 🟩🟩🟩🟩🟩
    3/6
    DRAKE ⬜⬜⬜⬜⬜
    STICH ⬜⬜⬜🟨⬜
    CLUMP 🟩🟩🟩🟩🟩
    3/6
    CLUMP ⬜⬜⬜⬜🟨
    SPADE ⬜🟨⬜🟩🟩
    PRIDE 🟩🟩🟩🟩🟩
    Final 1/2
    SKIER 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1495 🥳 score:25 ⏱️ 0:02:25.871123

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. STIFF attempts:6 score:6
2. SINCE attempts:8 score:8
3. PATSY attempts:4 score:4
4. METAL attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1495 🥳 score:63 ⏱️ 0:03:35.481448

📜 2 sessions

Octordle Classic

1. SWINE attempts:9 score:9
2. ANIME attempts:10 score:10
3. STAIN attempts:2 score:2
4. STEAM attempts:11 score:11
5. SPICE attempts:5 score:5
6. LYING attempts:6 score:6
7. GULLY attempts:12 score:12
8. CHEER attempts:8 score:8

# [squareword.org](squareword.org) 🧩 #1488 🥳 7 ⏱️ 0:01:58.413466

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟨 🟨
    🟨 🟨 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A C R E S
    P L U M P
    S A M B A
    E M B E R
    S P A D E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1425 🥳 229 ⏱️ 0:01:49.557312

🤔 230 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 29 chat prompts
🤖 29 dolphin3:latest replies
🔥   3 🥵   7 😎  32 🥶 163 🧊  24

      $1 #230 rent           100.00°C 🥳 1000‰ ~206 used:0  [205]  source:dolphin3
      $2 #206 rental          70.48°C 🔥  998‰   ~2 used:3  [1]    source:dolphin3
      $3 #214 lease           54.86°C 🔥  996‰   ~3 used:3  [2]    source:dolphin3
      $4 #213 landlord        52.93°C 🔥  994‰   ~1 used:1  [0]    source:dolphin3
      $5 #170 accommodation   43.65°C 🥵  982‰  ~10 used:8  [9]    source:dolphin3
      $6 #183 condo           43.39°C 🥵  980‰   ~8 used:3  [7]    source:dolphin3
      $7 #179 apartment       40.02°C 🥵  971‰   ~7 used:2  [6]    source:dolphin3
      $8 #173 lodging         36.69°C 🥵  945‰   ~9 used:3  [8]    source:dolphin3
      $9 #196 condominium     36.12°C 🥵  943‰   ~4 used:1  [3]    source:dolphin3
     $10 #190 loft            35.52°C 🥵  935‰   ~5 used:0  [4]    source:dolphin3
     $11 #212 housing         34.26°C 🥵  921‰   ~6 used:0  [5]    source:dolphin3
     $12 #188 house           32.22°C 😎  886‰  ~11 used:0  [10]   source:dolphin3
     $44 #167 room            20.22°C 🥶        ~46 used:0  [45]   source:dolphin3
    $207 #129 tray            -0.17°C 🧊       ~207 used:0  [206]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1458 🥳 226 ⏱️ 0:06:52.512053

🤔 227 attempts
📜 1 sessions
🫧 19 chat sessions
⁉️ 99 chat prompts
🤖 99 dolphin3:latest replies
🔥   4 🥵  28 😎  73 🥶 104 🧊  17

      $1 #227 motivation            100.00°C 🥳 1000‰ ~210 used:0  [209]  source:dolphin3
      $2 #219 candidature            49.02°C 🔥  994‰   ~1 used:2  [0]    source:dolphin3
      $3  #58 aptitude               45.58°C 🔥  993‰  ~31 used:92 [30]   source:dolphin3
      $4  #29 expérience             45.05°C 🔥  992‰  ~30 used:65 [29]   source:dolphin3
      $5 #108 réussite               42.60°C 🔥  990‰  ~20 used:44 [19]   source:dolphin3
      $6  #28 connaissance           41.66°C 🥵  989‰  ~32 used:10 [31]   source:dolphin3
      $7  #59 compétence             41.49°C 🥵  988‰  ~21 used:5  [20]   source:dolphin3
      $8 #183 profil                 40.86°C 🥵  986‰  ~22 used:5  [21]   source:dolphin3
      $9 #155 personnel              40.03°C 🥵  982‰  ~23 used:5  [22]   source:dolphin3
     $10 #216 candidat               39.94°C 🥵  981‰   ~2 used:1  [1]    source:dolphin3
     $11 #111 adéquation             39.33°C 🥵  979‰  ~24 used:5  [23]   source:dolphin3
     $34  #36 psychologie            31.22°C 😎  893‰  ~33 used:0  [32]   source:dolphin3
    $107 #221 mérite                 18.27°C 🥶       ~106 used:0  [105]  source:dolphin3
    $211 #206 civil                  -0.14°C 🧊       ~211 used:0  [210]  source:dolphin3
