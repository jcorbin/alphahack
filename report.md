# 2026-02-08

- 🔗 spaceword.org 🧩 2026-02-07 🏁 score 2168 ranked 30.9% 108/350 ⏱️ 0:06:20.367555
- 🔗 alfagok.diginaut.net 🧩 #463 🥳 28 ⏱️ 0:00:36.815476
- 🔗 alphaguess.com 🧩 #930 🥳 22 ⏱️ 0:00:42.815259
- 🔗 dontwordle.com 🧩 #1356 🥳 6 ⏱️ 0:02:04.656346
- 🔗 dictionary.com hurdle 🧩 #1499 🥳 22 ⏱️ 0:03:28.797882
- 🔗 Quordle Classic 🧩 #1476 🥳 score:24 ⏱️ 0:01:43.526101
- 🔗 Octordle Classic 🧩 #1476 🥳 score:60 ⏱️ 0:03:45.771079
- 🔗 squareword.org 🧩 #1469 🥳 8 ⏱️ 0:02:50.985765
- 🔗 cemantle.certitudes.org 🧩 #1406 🥳 243 ⏱️ 0:17:32.579430
- 🔗 cemantix.certitudes.org 🧩 #1439 🥳 64 ⏱️ 0:02:10.396177
- 🔗 Quordle Rescue 🧩 #90 🥳 score:25 ⏱️ 0:03:22.953067

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
























# [spaceword.org](spaceword.org) 🧩 2026-02-07 🏁 score 2168 ranked 30.9% 108/350 ⏱️ 0:06:20.367555

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 108/350

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ G L I A _ _ _   
      _ _ _ H _ _ V _ _ _   
      _ _ _ A _ B I _ _ _   
      _ _ _ Z _ E D _ _ _   
      _ _ _ I _ L I _ _ _   
      _ _ _ _ J I N _ _ _   
      _ _ _ _ _ E _ _ _ _   
      _ _ _ _ I D _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #463 🥳 28 ⏱️ 0:00:36.815476

🤔 28 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+2      [     2] -cijferig   
    @+99751  [ 99751] ex          q2  ? ␅
    @+99751  [ 99751] ex          q3  ? after
    @+111406 [111406] ge          q6  ? ␅
    @+111406 [111406] ge          q7  ? after
    @+130427 [130427] gracieuze   q8  ? ␅
    @+130427 [130427] gracieuze   q9  ? after
    @+135092 [135092] haat        q12 ? ␅
    @+135092 [135092] haat        q13 ? after
    @+136145 [136145] han         q14 ? ␅
    @+136145 [136145] han         q15 ? after
    @+136150 [136150] hand        q22 ? ␅
    @+136150 [136150] hand        q23 ? after
    @+136258 [136258] handbreedte q24 ? ␅
    @+136258 [136258] handbreedte q25 ? after
    @+136302 [136302] handel      q26 ? ␅
    @+136302 [136302] handel      q27 ? it
    @+136302 [136302] handel      done. it
    @+136371 [136371] handels     q20 ? ␅
    @+136371 [136371] handels     q21 ? before
    @+136844 [136844] handen      q18 ? ␅
    @+136844 [136844] handen      q19 ? before
    @+137577 [137577] har         q16 ? ␅
    @+137577 [137577] har         q17 ? before
    @+139784 [139784] hei         q10 ? ␅
    @+139784 [139784] hei         q11 ? before
    @+149447 [149447] huis        q4  ? ␅
    @+149447 [149447] huis        q5  ? before
    @+199826 [199826] lijm        q0  ? ␅
    @+199826 [199826] lijm        q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #930 🥳 22 ⏱️ 0:00:42.815259

🤔 22 attempts
📜 1 sessions

    @       [    0] aa           
    @+1     [    1] aah          
    @+2     [    2] aahed        
    @+3     [    3] aahing       
    @+47381 [47381] dis          q2  ? ␅
    @+47381 [47381] dis          q3  ? after
    @+60084 [60084] face         q6  ? ␅
    @+60084 [60084] face         q7  ? after
    @+66440 [66440] french       q8  ? ␅
    @+66440 [66440] french       q9  ? after
    @+68006 [68006] gall         q12 ? ␅
    @+68006 [68006] gall         q13 ? after
    @+68788 [68788] gate         q14 ? ␅
    @+68788 [68788] gate         q15 ? after
    @+69155 [69155] gem          q16 ? ␅
    @+69155 [69155] gem          q17 ? after
    @+69212 [69212] gen          q18 ? ␅
    @+69212 [69212] gen          q19 ? after
    @+69409 [69409] gentle       q20 ? ␅
    @+69409 [69409] gentle       q21 ? it
    @+69409 [69409] gentle       done. it
    @+69620 [69620] geosynclinal q10 ? ␅
    @+69620 [69620] geosynclinal q11 ? before
    @+72800 [72800] gremmy       q4  ? ␅
    @+72800 [72800] gremmy       q5  ? before
    @+98219 [98219] mach         q0  ? ␅
    @+98219 [98219] mach         q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1356 🥳 6 ⏱️ 0:02:04.656346

📜 1 sessions
💰 score: 63

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:CHAFF n n n n n remain:5130
    ⬜⬜⬜⬜⬜ tried:DEWED n n n n n remain:1687
    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:590
    ⬜⬜⬜⬜⬜ tried:MORRO n n n n n remain:111
    ⬜🟨⬜⬜⬜ tried:XYLYL n m n n n remain:24
    ⬜🟩⬜⬜🟩 tried:KINKY n Y n n Y remain:9

    Undos used: 3

      9 words remaining
    x 7 unused letters
    = 63 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1499 🥳 22 ⏱️ 0:03:28.797882

📜 2 sessions
💰 score: 9400

    5/6
    STEAL ⬜⬜⬜🟨⬜
    ACORN 🟨⬜🟨🟨⬜
    VAPOR ⬜🟩⬜🟩🟩
    MAJOR ⬜🟩⬜🟩🟩
    RAZOR 🟩🟩🟩🟩🟩
    4/6
    RAZOR 🟨⬜⬜⬜⬜
    FIRES ⬜⬜🟨⬜⬜
    CRYPT ⬜🟨⬜⬜🟩
    BLURT 🟩🟩🟩🟩🟩
    6/6
    BLURT ⬜⬜⬜⬜🟩
    FEINT ⬜⬜🟨⬜🟩
    DIVOT ⬜🟩⬜⬜🟩
    MIGHT ⬜🟩🟩🟩🟩
    SIGHT ⬜🟩🟩🟩🟩
    TIGHT 🟩🟩🟩🟩🟩
    5/6
    TIGHT ⬜⬜🟨⬜⬜
    SARGE 🟨🟨⬜🟨⬜
    GOALS 🟩⬜🟩🟨🟩
    GLADS 🟩🟩🟩⬜🟩
    GLASS 🟩🟩🟩🟩🟩
    Final 2/2
    GNOME 🟩⬜🟩⬜🟩
    GEODE 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1476 🥳 score:24 ⏱️ 0:01:43.526101

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. ENJOY attempts:8 score:8
2. MAMBO attempts:7 score:7
3. WRATH attempts:4 score:4
4. STRAP attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1476 🥳 score:60 ⏱️ 0:03:45.771079

📜 1 sessions

Octordle Classic

1. VOILA attempts:8 score:8
2. LOCAL attempts:5 score:5
3. BLACK attempts:4 score:4
4. CHUMP attempts:6 score:6
5. JUMPY attempts:10 score:10
6. FLOAT attempts:11 score:11
7. ILIAC attempts:7 score:7
8. BIDDY attempts:9 score:9

# [squareword.org](squareword.org) 🧩 #1469 🥳 8 ⏱️ 0:02:50.985765

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟨 🟨 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C A M P
    C U T I E
    A R O S E
    L I N E R
    D O E R S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1406 🥳 243 ⏱️ 0:17:32.579430

🤔 244 attempts
📜 1 sessions
🫧 28 chat sessions
⁉️ 76 chat prompts
🤖 38 dolphin3:latest replies
🤖 38 qwen3:8b replies
🔥   3 🥵  10 😎  33 🥶 168 🧊  29

      $1 #244 activate          100.00°C 🥳 1000‰ ~218 used:0  [217]  source:dolphin3
      $2 #146 synchronize        45.52°C 🔥  993‰   ~6 used:39 [5]    source:dolphin3
      $3 #243 initialize         44.78°C 🔥  991‰   ~1 used:2  [0]    source:dolphin3
      $4 #220 configure          44.30°C 🔥  990‰   ~4 used:12 [3]    source:dolphin3
      $5 #143 modify             43.13°C 🥵  986‰  ~42 used:12 [41]   source:dolphin3
      $6 #154 switch             41.88°C 🥵  982‰  ~10 used:5  [9]    source:dolphin3
      $7 #126 adjust             39.15°C 🥵  972‰  ~12 used:8  [11]   source:dolphin3
      $8 #130 calibrate          37.93°C 🥵  960‰  ~11 used:6  [10]   source:dolphin3
      $9 #219 connect            37.76°C 🥵  958‰   ~7 used:4  [6]    source:dolphin3
     $10 #179 rearrange          37.22°C 🥵  949‰   ~8 used:4  [7]    source:dolphin3
     $11 #189 coordinate         36.51°C 🥵  938‰   ~9 used:4  [8]    source:dolphin3
     $15 #134 customize          34.27°C 😎  898‰  ~43 used:3  [42]   source:dolphin3
     $48 #141 improve            24.41°C 🥶        ~47 used:0  [46]   source:dolphin3
    $216 #152 circuit            -0.28°C 🧊       ~219 used:0  [218]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1439 🥳 64 ⏱️ 0:02:10.396177

🤔 65 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 24 chat prompts
🤖 24 dolphin3:latest replies
😱  1 🥵  1 😎 14 🥶 45 🧊  3

     $1 #65 douceur         100.00°C 🥳 1000‰ ~62 used:0  [61]  source:dolphin3
     $2 #63 doux             71.30°C 😱  999‰  ~1 used:4  [0]   source:dolphin3
     $3 #30 senteur          42.73°C 🥵  933‰ ~13 used:24 [12]  source:dolphin3
     $4 #16 parfum           39.27°C 😎  881‰ ~16 used:13 [15]  source:dolphin3
     $5 #40 parfumé          38.19°C 😎  842‰ ~15 used:5  [14]  source:dolphin3
     $6 #64 douce            37.42°C 😎  810‰  ~2 used:1  [1]   source:dolphin3
     $7 #47 effluve          36.60°C 😎  773‰  ~5 used:2  [4]   source:dolphin3
     $8 #10 soleil           34.65°C 😎  672‰ ~14 used:3  [13]  source:dolphin3
     $9  #4 fleur            34.55°C 😎  667‰  ~6 used:2  [5]   source:dolphin3
    $10 #39 odeur            33.52°C 😎  604‰  ~7 used:2  [6]   source:dolphin3
    $11 #27 fragrance        33.20°C 😎  586‰  ~8 used:2  [7]   source:dolphin3
    $12 #34 ambiance         30.87°C 😎  382‰  ~9 used:2  [8]   source:dolphin3
    $18 #33 sentiment        27.40°C 🥶       ~17 used:0  [16]  source:dolphin3
    $63 #45 allégeance       -0.40°C 🧊       ~63 used:0  [62]  source:dolphin3

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #90 🥳 score:25 ⏱️ 0:03:22.953067

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. SCENE attempts:8 score:8
2. BLARE attempts:6 score:6
3. BRINE attempts:7 score:7
4. INFER attempts:4 score:4
