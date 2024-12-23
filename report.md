# 2026-04-06

- 🔗 spaceword.org 🧩 2026-04-05 🏁 score 2168 ranked 45.1% 147/326 ⏱️ 1:35:34.754403
- 🔗 alfagok.diginaut.net 🧩 #520 🥳 16 ⏱️ 0:00:35.583695
- 🔗 alphaguess.com 🧩 #987 🥳 28 ⏱️ 0:00:44.126945
- 🔗 dontwordle.com 🧩 #1413 🥳 6 ⏱️ 0:01:34.336025
- 🔗 dictionary.com hurdle 🧩 #1556 🥳 17 ⏱️ 0:03:47.625405
- 🔗 Quordle Classic 🧩 #1533 🥳 score:23 ⏱️ 0:01:36.199153
- 🔗 Octordle Classic 🧩 #1533 😦 score:74 ⏱️ 0:06:28.738616
- 🔗 squareword.org 🧩 #1526 🥳 8 ⏱️ 0:02:17.455569
- 🔗 cemantle.certitudes.org 🧩 #1463 🥳 697 ⏱️ 0:09:44.328357
- 🔗 cemantix.certitudes.org 🧩 #1496 🥳 233 ⏱️ 0:03:43.885436

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




































# [spaceword.org](spaceword.org) 🧩 2026-04-05 🏁 score 2168 ranked 45.1% 147/326 ⏱️ 1:35:34.754403

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 147/326

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ P _ _ M _ _ D _ _   
      _ U _ _ A _ K I F _   
      _ J _ A U R A T E _   
      _ A X I T E S _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #520 🥳 16 ⏱️ 0:00:35.583695

🤔 16 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+24910  [ 24910] bad       q6  ? ␅
    @+24910  [ 24910] bad       q7  ? after
    @+37357  [ 37357] bescherm  q8  ? ␅
    @+37357  [ 37357] bescherm  q9  ? after
    @+38195  [ 38195] best      q14 ? ␅
    @+38195  [ 38195] best      q15 ? it
    @+38195  [ 38195] best      done. it
    @+39992  [ 39992] beurs     q12 ? ␅
    @+39992  [ 39992] beurs     q13 ? before
    @+43062  [ 43062] bij       q10 ? ␅
    @+43062  [ 43062] bij       q11 ? before
    @+49841  [ 49841] boks      q4  ? ␅
    @+49841  [ 49841] boks      q5  ? before
    @+99737  [ 99737] ex        q2  ? ␅
    @+99737  [ 99737] ex        q3  ? before
    @+199606 [199606] lij       q0  ? ␅
    @+199606 [199606] lij       q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #987 🥳 28 ⏱️ 0:00:44.126945

🤔 28 attempts
📜 1 sessions

    @        [     0] aa            
    @+2      [     2] aahed         
    @+98216  [ 98216] mach          q0  ? ␅
    @+98216  [ 98216] mach          q1  ? after
    @+147371 [147371] rhumb         q2  ? ␅
    @+147371 [147371] rhumb         q3  ? after
    @+147423 [147423] rib           q20 ? ␅
    @+147423 [147423] rib           q21 ? after
    @+147471 [147471] ribonucleases q22 ? ␅
    @+147471 [147471] ribonucleases q23 ? after
    @+147489 [147489] rice          q24 ? ␅
    @+147489 [147489] rice          q25 ? after
    @+147501 [147501] rich          q26 ? ␅
    @+147501 [147501] rich          q27 ? it
    @+147501 [147501] rich          done. it
    @+147519 [147519] rick          q18 ? ␅
    @+147519 [147519] rick          q19 ? before
    @+147692 [147692] right         q16 ? ␅
    @+147692 [147692] right         q17 ? before
    @+148077 [148077] river         q14 ? ␅
    @+148077 [148077] river         q15 ? before
    @+148803 [148803] rot           q12 ? ␅
    @+148803 [148803] rot           q13 ? before
    @+150337 [150337] sallow        q10 ? ␅
    @+150337 [150337] sallow        q11 ? before
    @+153315 [153315] sea           q8  ? ␅
    @+153315 [153315] sea           q9  ? before
    @+159483 [159483] slop          q6  ? ␅
    @+159483 [159483] slop          q7  ? before
    @+171636 [171636] ta            q4  ? ␅
    @+171636 [171636] ta            q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1413 🥳 6 ⏱️ 0:01:34.336025

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:7600
    ⬜⬜⬜⬜⬜ tried:MAMBA n n n n n remain:2985
    ⬜⬜⬜⬜⬜ tried:WOOSH n n n n n remain:466
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:173
    ⬜🟨⬜⬜⬜ tried:KUDZU n m n n n remain:23
    ⬜🟨🟨⬜⬜ tried:GRUFF n m m n n remain:4

    Undos used: 3

      4 words remaining
    x 6 unused letters
    = 24 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1556 🥳 17 ⏱️ 0:03:47.625405

📜 1 sessions
💰 score: 9900

    3/6
    STANE ⬜⬜⬜🟩⬜
    YOUNG ⬜⬜⬜🟩🟩
    CLING 🟩🟩🟩🟩🟩
    4/6
    CLING ⬜🟨⬜🟨⬜
    NOELS 🟨⬜🟨🟨⬜
    PANEL ⬜🟨🟨🟨🟨
    LEARN 🟩🟩🟩🟩🟩
    4/6
    LEARN ⬜⬜⬜🟨⬜
    RIOTS 🟨🟩⬜⬜🟩
    BIRDS ⬜🟩🟩⬜🟩
    VIRUS 🟩🟩🟩🟩🟩
    5/6
    VIRUS ⬜⬜⬜⬜🟨
    ONSET 🟨⬜🟨🟨🟨
    THOSE 🟨⬜🟩🟨🟩
    SMOTE 🟩⬜🟩🟨🟩
    STOKE 🟩🟩🟩🟩🟩
    Final 1/2
    RANCH 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1533 🥳 score:23 ⏱️ 0:01:36.199153

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. CHIEF attempts:4 score:4
2. IDLER attempts:5 score:5
3. PASTA attempts:8 score:8
4. BRIAR attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1533 😦 score:74 ⏱️ 0:06:28.738616

📜 1 sessions

Octordle Classic

1. DROOP attempts:10 score:10
2. LEAFY attempts:12 score:12
3. TRYST attempts:5 score:5
4. CINCH attempts:7 score:7
5. GAU_E -BCDFHIKLMNOPRSTY attempts:13 score:-1
6. NIECE attempts:8 score:8
7. AUDIT attempts:4 score:4
8. _A_ER -BCDFGHIKLMNOPSTUY attempts:13 score:-1

# [squareword.org](squareword.org) 🧩 #1526 🥳 8 ⏱️ 0:02:17.455569

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B A R E D
    A L I V E
    T O P I C
    C H E C K
    H A R T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1463 🥳 697 ⏱️ 0:09:44.328357

🤔 698 attempts
📜 1 sessions
🫧 31 chat sessions
⁉️ 165 chat prompts
🤖 165 dolphin3:latest replies
🔥   2 🥵  16 😎  72 🥶 583 🧊  24

      $1 #698 discharge             100.00°C 🥳 1000‰ ~674 used:0   [673]  source:dolphin3
      $2 #685 effluent               40.37°C 🔥  995‰   ~1 used:1   [0]    source:dolphin3
      $3 #677 wastewater             38.23°C 🔥  992‰   ~2 used:2   [1]    source:dolphin3
      $4 #672 floc                   37.13°C 🥵  987‰   ~3 used:2   [2]    source:dolphin3
      $5 #401 removal                36.45°C 🥵  983‰  ~89 used:101 [88]   source:dolphin3
      $6 #318 germicide              35.02°C 🥵  979‰  ~85 used:77  [84]   source:dolphin3
      $7 #600 desorption             34.51°C 🥵  974‰  ~48 used:19  [47]   source:dolphin3
      $8 #643 flocculation           34.51°C 🥵  975‰   ~5 used:6   [4]    source:dolphin3
      $9 #645 filtrate               34.47°C 🥵  973‰   ~6 used:6   [5]    source:dolphin3
     $10 #279 treatment              34.42°C 🥵  972‰  ~81 used:31  [80]   source:dolphin3
     $11 #297 disinfection           34.13°C 🥵  967‰  ~42 used:11  [41]   source:dolphin3
     $20 #638 chlorination           31.18°C 😎  897‰   ~8 used:1   [7]    source:dolphin3
     $92 #648 colloid                24.13°C 🥶        ~95 used:0   [94]   source:dolphin3
    $675 #655 protein                -0.03°C 🧊       ~675 used:0   [674]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1496 🥳 233 ⏱️ 0:03:43.885436

🤔 234 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 50 chat prompts
🤖 50 dolphin3:latest replies
🔥   1 🥵  18 😎  51 🥶 105 🧊  58

      $1 #234 dynamisme        100.00°C 🥳 1000‰ ~176 used:0  [175]  source:dolphin3
      $2 #155 créativité        50.61°C 🔥  994‰   ~9 used:26 [8]    source:dolphin3
      $3 #187 adaptabilité      44.58°C 🥵  980‰  ~16 used:8  [15]   source:dolphin3
      $4 #161 inventivité       43.16°C 🥵  972‰  ~17 used:8  [16]   source:dolphin3
      $5 #190 réactivité        43.05°C 🥵  970‰   ~4 used:2  [3]    source:dolphin3
      $6 #227 capacité          41.36°C 🥵  960‰   ~5 used:2  [4]    source:dolphin3
      $7 #145 croissance        41.05°C 🥵  957‰  ~18 used:8  [17]   source:dolphin3
      $8 #162 originalité       40.49°C 🥵  953‰  ~10 used:3  [9]    source:dolphin3
      $9 #222 talent            39.80°C 🥵  947‰   ~1 used:1  [0]    source:dolphin3
     $10 #137 opportunité       39.66°C 🥵  945‰  ~14 used:6  [13]   source:dolphin3
     $11 #126 innovation        39.53°C 🥵  943‰  ~15 used:6  [14]   source:dolphin3
     $21 #216 polyvalence       35.40°C 😎  897‰  ~19 used:0  [18]   source:dolphin3
     $72 #233 capable           20.23°C 🥶        ~78 used:0  [77]   source:dolphin3
    $177  #84 marin             -0.36°C 🧊       ~177 used:0  [176]  source:dolphin3
