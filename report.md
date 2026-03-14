# 2026-03-15

- 🔗 spaceword.org 🧩 2026-03-14 🏁 score 2151 ranked 77.5% 258/333 ⏱️ 0:02:53.490324
- 🔗 alfagok.diginaut.net 🧩 #498 🥳 36 ⏱️ 0:00:35.174634
- 🔗 alphaguess.com 🧩 #965 🥳 34 ⏱️ 0:00:33.672086
- 🔗 dontwordle.com 🧩 #1391 🥳 6 ⏱️ 0:01:44.006757
- 🔗 dictionary.com hurdle 🧩 #1534 😦 19 ⏱️ 0:03:44.491461
- 🔗 Quordle Classic 🧩 #1511 🥳 score:25 ⏱️ 0:02:08.176321
- 🔗 Octordle Classic 🧩 #1511 🥳 score:59 ⏱️ 0:04:39.289369
- 🔗 squareword.org 🧩 #1504 🥳 8 ⏱️ 0:02:48.984219
- 🔗 cemantle.certitudes.org 🧩 #1441 🥳 396 ⏱️ 0:06:03.742694
- 🔗 cemantix.certitudes.org 🧩 #1474 🥳 121 ⏱️ 0:01:29.587561

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














# [spaceword.org](spaceword.org) 🧩 2026-03-14 🏁 score 2151 ranked 77.5% 258/333 ⏱️ 0:02:53.490324

📜 2 sessions
- tiles: 21/21
- score: 2151 bonus: +51
- rank: 258/333

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ K O T O _ _ _ _   
      _ _ _ _ R _ _ _ _ _   
      _ _ S A I G A _ _ _   
      _ _ _ A V I S O S _   
      _ _ _ _ I _ _ _ _ _   
      _ _ _ _ U _ _ _ _ _   
      _ _ C W M _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #498 🥳 36 ⏱️ 0:00:35.174634

🤔 36 attempts
📜 1 sessions

    @       [    0] &-teken   
    @+24910 [24910] bad       q8  ? ␅
    @+24910 [24910] bad       q9  ? after
    @+37357 [37357] bescherm  q10 ? ␅
    @+37357 [37357] bescherm  q11 ? after
    @+38195 [38195] best      q16 ? ␅
    @+38195 [38195] best      q17 ? after
    @+38240 [38240] bestand   q24 ? ␅
    @+38240 [38240] bestand   q25 ? after
    @+38315 [38315] beste     q26 ? ␅
    @+38315 [38315] beste     q27 ? after
    @+38319 [38319] bestede   q30 ? ␅
    @+38319 [38319] bestede   q31 ? after
    @+38320 [38320] besteden  q34 ? ␅
    @+38320 [38320] besteden  q35 ? it
    @+38320 [38320] besteden  done. it
    @+38321 [38321] bestedend q32 ? ␅
    @+38321 [38321] bestedend q33 ? before
    @+38323 [38323] besteding q28 ? ␅
    @+38323 [38323] besteding q29 ? before
    @+38398 [38398] bestel    q22 ? ␅
    @+38398 [38398] bestel    q23 ? before
    @+38640 [38640] bestraal  q20 ? ␅
    @+38640 [38640] bestraal  q21 ? before
    @+39092 [39092] bet       q18 ? ␅
    @+39092 [39092] bet       q19 ? before
    @+39992 [39992] beurs     q14 ? ␅
    @+39992 [39992] beurs     q15 ? before
    @+43062 [43062] bij       q12 ? ␅
    @+43062 [43062] bij       q13 ? before
    @+49841 [49841] boks      q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #965 🥳 34 ⏱️ 0:00:33.672086

🤔 34 attempts
📜 1 sessions

    @       [    0] aa           
    @+47381 [47381] dis          q4  ? ␅
    @+47381 [47381] dis          q5  ? after
    @+60084 [60084] face         q8  ? ␅
    @+60084 [60084] face         q9  ? after
    @+66440 [66440] french       q10 ? ␅
    @+66440 [66440] french       q11 ? after
    @+69620 [69620] geosynclinal q12 ? ␅
    @+69620 [69620] geosynclinal q13 ? after
    @+71210 [71210] gnomist      q14 ? ␅
    @+71210 [71210] gnomist      q15 ? after
    @+72005 [72005] gracioso     q16 ? ␅
    @+72005 [72005] gracioso     q17 ? after
    @+72398 [72398] grass        q18 ? ␅
    @+72398 [72398] grass        q19 ? after
    @+72482 [72482] grave        q22 ? ␅
    @+72482 [72482] grave        q23 ? after
    @+72540 [72540] gravities    q24 ? ␅
    @+72540 [72540] gravities    q25 ? after
    @+72549 [72549] gravlax      q30 ? ␅
    @+72549 [72549] gravlax      q31 ? after
    @+72553 [72553] gravy        q32 ? ␅
    @+72553 [72553] gravy        q33 ? it
    @+72553 [72553] gravy        done. it
    @+72556 [72556] gray         q26 ? ␅
    @+72556 [72556] gray         q27 ? before
    @+72596 [72596] grazing      q20 ? ␅
    @+72596 [72596] grazing      q21 ? before
    @+72799 [72799] gremmy       q6  ? ␅
    @+72799 [72799] gremmy       q7  ? before
    @+98217 [98217] mach         q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1391 🥳 6 ⏱️ 0:01:44.006757

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:7042
    ⬜⬜⬜⬜⬜ tried:ERRED n n n n n remain:2086
    ⬜⬜⬜⬜⬜ tried:GLOGG n n n n n remain:611
    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:167
    ⬜🟨⬜🟩⬜ tried:NYMPH n m n Y n remain:5
    ⬜🟩⬜🟩🟩 tried:ZIPPY n Y n Y Y remain:1

    Undos used: 4

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1534 😦 19 ⏱️ 0:03:44.491461

📜 2 sessions
💰 score: 4760

    5/6
    STANE 🟨⬜⬜⬜⬜
    MILOS ⬜⬜⬜🟨🟩
    DROPS ⬜⬜🟨⬜🟩
    HOCKS ⬜🟩🟩⬜🟩
    FOCUS 🟩🟩🟩🟩🟩
    3/6
    FOCUS ⬜⬜🟨⬜⬜
    CRANE 🟩🟩🟩🟩⬜
    CRANK 🟩🟩🟩🟩🟩
    4/6
    CRANK ⬜⬜⬜⬜⬜
    ISLET 🟨🟨⬜⬜🟩
    HOIST 🟨⬜🟩🟨🟩
    SHIFT 🟩🟩🟩🟩🟩
    5/6
    SHIFT ⬜⬜⬜⬜⬜
    OLDER ⬜⬜🟩⬜⬜
    PUDGY ⬜🟩🟩⬜🟩
    BUDDY ⬜🟩🟩🟩🟩
    MUDDY 🟩🟩🟩🟩🟩
    Final 2/2
    ????? 🟨🟩⬜⬜🟩
    ????? ⬜🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1511 🥳 score:25 ⏱️ 0:02:08.176321

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. GRILL attempts:9 score:9
2. WALTZ attempts:4 score:4
3. TROVE attempts:7 score:7
4. TOTAL attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1511 🥳 score:59 ⏱️ 0:04:39.289369

📜 1 sessions

Octordle Classic

1. SINGE attempts:8 score:8
2. MOOSE attempts:10 score:10
3. SNUCK attempts:6 score:6
4. SHOVE attempts:11 score:11
5. STANK attempts:7 score:7
6. KARMA attempts:9 score:9
7. WINCH attempts:5 score:5
8. AFIRE attempts:3 score:3

# [squareword.org](squareword.org) 🧩 #1504 🥳 8 ⏱️ 0:02:48.984219

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A S S E T
    L U N A R
    G R A T E
    A G R E E
    L E E R S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1441 🥳 396 ⏱️ 0:06:03.742694

🤔 397 attempts
📜 1 sessions
🫧 22 chat sessions
⁉️ 109 chat prompts
🤖 109 dolphin3:latest replies
😱   1 🔥   1 🥵   6 😎  25 🥶 328 🧊  35

      $1 #397 bargaining       100.00°C 🥳 1000‰ ~362 used:0  [361]  source:dolphin3
      $2 #380 negotiation       64.35°C 😱  999‰   ~1 used:9  [0]    source:dolphin3
      $3 #384 conciliation      50.66°C 🔥  995‰   ~2 used:0  [1]    source:dolphin3
      $4 #388 mediation         41.96°C 🔥  990‰   ~3 used:0  [2]    source:dolphin3
      $5 #383 compromise        40.25°C 🥵  983‰   ~4 used:0  [3]    source:dolphin3
      $6 #381 arbitration       38.37°C 🥵  972‰   ~7 used:3  [6]    source:dolphin3
      $7 #378 agreement         37.19°C 🥵  970‰   ~8 used:3  [7]    source:dolphin3
      $8 #385 contract          29.48°C 🥵  928‰   ~5 used:0  [4]    source:dolphin3
      $9 #387 diplomacy         29.45°C 🥵  927‰   ~6 used:0  [5]    source:dolphin3
     $10 #392 settlement        25.66°C 😎  845‰   ~9 used:0  [8]    source:dolphin3
     $11 #349 consolidation     25.23°C 😎  836‰  ~22 used:4  [21]   source:dolphin3
     $12 #246 drafting          24.60°C 😎  816‰  ~31 used:32 [30]   source:dolphin3
     $35 #120 transfer          17.57°C 🥶        ~37 used:6  [36]   source:dolphin3
    $363 #163 liquid            -0.10°C 🧊       ~363 used:0  [362]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1474 🥳 121 ⏱️ 0:01:29.587561

🤔 122 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 20 chat prompts
🤖 20 dolphin3:latest replies
🥵  6 😎 11 🥶 88 🧊 16

      $1 #122 variété         100.00°C 🥳 1000‰ ~106 used:0 [105]  source:dolphin3
      $2  #79 cultiver         44.34°C 🥵  985‰   ~5 used:6 [4]    source:dolphin3
      $3  #65 plant            41.20°C 🥵  965‰   ~6 used:6 [5]    source:dolphin3
      $4  #99 hybride          40.43°C 🥵  955‰   ~1 used:1 [0]    source:dolphin3
      $5  #77 plante           40.14°C 🥵  952‰   ~4 used:5 [3]    source:dolphin3
      $6  #72 semence          38.43°C 🥵  933‰   ~2 used:1 [1]    source:dolphin3
      $7  #96 floraison        38.29°C 🥵  929‰   ~3 used:0 [2]    source:dolphin3
      $8 #100 pollinisateur    35.92°C 😎  879‰   ~7 used:0 [6]    source:dolphin3
      $9  #56 fruit            35.39°C 😎  862‰  ~16 used:3 [15]   source:dolphin3
     $10  #94 croisement       32.79°C 😎  728‰   ~8 used:0 [7]    source:dolphin3
     $11  #76 arbuste          31.98°C 😎  674‰   ~9 used:0 [8]    source:dolphin3
     $12  #92 récolte          31.96°C 😎  672‰  ~10 used:0 [9]    source:dolphin3
     $19 #109 potager          25.64°C 🥶        ~26 used:0 [25]   source:dolphin3
    $107  #60 arrière          -0.38°C 🧊       ~107 used:0 [106]  source:dolphin3
