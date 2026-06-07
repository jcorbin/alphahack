# 2026-06-08

- 🔗 spaceword.org 🧩 2026-06-07 🏁 score 2165 ranked 29.6% 95/321 ⏱️ 1:16:19.020087
- 🔗 alfagok.diginaut.net 🧩 #583 🥳 42 ⏱️ 0:00:49.984183
- 🔗 alphaguess.com 🧩 #1050 🥳 26 ⏱️ 0:00:54.592270
- 🔗 dontwordle.com 🧩 #1476 🥳 6 ⏱️ 0:01:28.288604
- 🔗 dictionary.com hurdle 🧩 #1619 🥳 21 ⏱️ 0:04:22.299263
- 🔗 Quordle Classic 🧩 #1596 🥳 score:25 ⏱️ 0:01:58.881386
- 🔗 cemantix.certitudes.org 🧩 #1559 🥳 150 ⏱️ 0:02:02.317452
- 🔗 Octordle Classic 🧩 #1596 🥳 score:71 ⏱️ 0:03:39.606268
- 🔗 squareword.org 🧩 #1589 🥳 8 ⏱️ 0:01:47.246465
- 🔗 cemantle.certitudes.org 🧩 #1526 🥳 320 ⏱️ 0:57:45.946700

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
























































































# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1585 😦 score:32 ⏱️ 0:02:33.513959

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. GRAPE attempts:8 score:8
2. VALUE attempts:9 score:9
3. YEARN attempts:6 score:6
4. IN_ER -ACDGHLMPSTUVWYZ attempts:9 score:-1












# [spaceword.org](spaceword.org) 🧩 2026-06-07 🏁 score 2165 ranked 29.6% 95/321 ⏱️ 1:16:19.020087

📜 2 sessions
- tiles: 21/21
- score: 2165 bonus: +65
- rank: 95/321

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ J A Y _ _ _ _   
      _ _ _ I _ _ _ T _ _   
      _ _ _ V I D E O _ _   
      _ _ _ Y _ _ _ R _ _   
      _ _ _ _ _ D U I _ _   
      _ _ _ _ _ U _ C _ _   
      _ _ _ A X I S _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #583 🥳 42 ⏱️ 0:00:49.984183

🤔 42 attempts
📜 1 sessions

    @        [     0] &-teken           
    @+24887  [ 24887] bad               q16 ? ␅
    @+24887  [ 24887] bad               q17 ? after
    @+37333  [ 37333] bescherm          q18 ? ␅
    @+37333  [ 37333] bescherm          q19 ? after
    @+37721  [ 37721] beslissing        q26 ? ␅
    @+37721  [ 37721] beslissing        q27 ? after
    @+37774  [ 37774] beslist           q32 ? ␅
    @+37774  [ 37774] beslist           q33 ? after
    @+37795  [ 37795] besluit           q34 ? ␅
    @+37795  [ 37795] besluit           q35 ? after
    @+37803  [ 37803] besluiten         q40 ? ␅
    @+37803  [ 37803] besluiten         q41 ? it
    @+37803  [ 37803] besluiten         done. it
    @+37810  [ 37810] besluitmoratorium q36 ? ␅
    @+37810  [ 37810] besluitmoratorium q37 ? before
    @+37825  [ 37825] besluitvorming    q30 ? ␅
    @+37825  [ 37825] besluitvorming    q31 ? before
    @+37945  [ 37945] bespaar           q28 ? ␅
    @+37945  [ 37945] bespaar           q29 ? before
    @+38170  [ 38170] best              q24 ? ␅
    @+38170  [ 38170] best              q25 ? before
    @+39966  [ 39966] beurs             q22 ? ␅
    @+39966  [ 39966] beurs             q23 ? before
    @+43036  [ 43036] bij               q20 ? ␅
    @+43036  [ 43036] bij               q21 ? before
    @+49815  [ 49815] boks              q12 ? ␅
    @+49815  [ 49815] boks              q13 ? before
    @+99702  [ 99702] ex                q10 ? ␅
    @+99702  [ 99702] ex                q11 ? before
    @+199764 [199764] lijm              q9  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1050 🥳 26 ⏱️ 0:00:54.592270

🤔 26 attempts
📜 1 sessions

    @        [     0] aa     
    @+1      [     1] aah    
    @+2      [     2] aahed  
    @+3      [     3] aahing 
    @+98214  [ 98214] mach   q0  ? ␅
    @+98214  [ 98214] mach   q1  ? after
    @+147364 [147364] rhotic q2  ? ␅
    @+147364 [147364] rhotic q3  ? after
    @+159481 [159481] slop   q6  ? ␅
    @+159481 [159481] slop   q7  ? after
    @+159660 [159660] slung  q18 ? ␅
    @+159660 [159660] slung  q19 ? after
    @+159747 [159747] smalt  q20 ? ␅
    @+159747 [159747] smalt  q21 ? after
    @+159773 [159773] smart  q22 ? ␅
    @+159773 [159773] smart  q23 ? after
    @+159800 [159800] smash  q24 ? ␅
    @+159800 [159800] smash  q25 ? it
    @+159800 [159800] smash  done. it
    @+159842 [159842] smell  q16 ? ␅
    @+159842 [159842] smell  q17 ? before
    @+160220 [160220] snath  q14 ? ␅
    @+160220 [160220] snath  q15 ? before
    @+160960 [160960] soft   q12 ? ␅
    @+160960 [160960] soft   q13 ? before
    @+162468 [162468] spec   q10 ? ␅
    @+162468 [162468] spec   q11 ? before
    @+165523 [165523] stick  q8  ? ␅
    @+165523 [165523] stick  q9  ? before
    @+171634 [171634] ta     q4  ? ␅
    @+171634 [171634] ta     q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1476 🥳 6 ⏱️ 0:01:28.288604

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:AYAYA n n n n n remain:6270
    ⬜⬜⬜⬜⬜ tried:ETWEE n n n n n remain:1854
    ⬜⬜⬜⬜⬜ tried:SHUSH n n n n n remain:332
    ⬜⬜⬜⬜⬜ tried:JINNI n n n n n remain:70
    ⬜🟩⬜⬜⬜ tried:GRRRL n Y n n n remain:15
    🟩🟩🟩⬜⬜ tried:BROCK Y Y Y n n remain:3

    Undos used: 2

      3 words remaining
    x 8 unused letters
    = 24 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1619 🥳 21 ⏱️ 0:04:22.299263

📜 1 sessions
💰 score: 9500

    4/6
    SERAL 🟩🟨⬜⬜⬜
    STIPE 🟩⬜⬜⬜🟩
    SCONE 🟩🟩⬜🟩🟩
    SCENE 🟩🟩🟩🟩🟩
    5/6
    SCENE ⬜⬜⬜⬜⬜
    LARGO ⬜⬜🟨⬜🟨
    FROTH ⬜🟨🟩⬜⬜
    IVORY ⬜⬜🟩🟨🟩
    ROOMY 🟩🟩🟩🟩🟩
    6/6
    ROOMY 🟨⬜⬜⬜⬜
    GEARS ⬜⬜🟩🟨⬜
    TRAIN ⬜🟩🟩⬜🟩
    PRAWN ⬜🟩🟩🟩🟩
    DRAWN ⬜🟩🟩🟩🟩
    BRAWN 🟩🟩🟩🟩🟩
    5/6
    BRAWN 🟨🟨⬜⬜⬜
    TURBO ⬜⬜🟨🟨⬜
    FIBER ⬜⬜🟩🟩🟩
    EMBER ⬜⬜🟩🟩🟩
    CYBER 🟩🟩🟩🟩🟩
    Final 1/2
    FILET 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1596 🥳 score:25 ⏱️ 0:01:58.881386

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. CURSE attempts:4 score:4
2. DROVE attempts:8 score:8
3. SNOWY attempts:6 score:6
4. DEBUG attempts:7 score:7

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1559 🥳 150 ⏱️ 0:02:02.317452

🤔 151 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 34 chat prompts
🤖 34 dolphin3:latest replies
🔥  2 🥵 12 😎 47 🥶 58 🧊 31

      $1 #151 lancement        100.00°C 🥳 1000‰ ~120 used:0  [119]  source:dolphin3
      $2 #145 démarrage         48.96°C 🔥  997‰   ~1 used:2  [0]    source:dolphin3
      $3  #75 déploiement       40.30°C 🔥  990‰   ~5 used:24 [4]    source:dolphin3
      $4  #81 mise              38.27°C 🥵  983‰  ~11 used:9  [10]   source:dolphin3
      $5 #122 opération         36.47°C 🥵  977‰   ~9 used:4  [8]    source:dolphin3
      $6  #52 promotion         34.71°C 🥵  963‰  ~60 used:11 [59]   source:dolphin3
      $7 #126 réalisation       33.95°C 🥵  954‰   ~6 used:3  [5]    source:dolphin3
      $8  #71 développement     33.15°C 🥵  950‰  ~10 used:5  [9]    source:dolphin3
      $9  #93 initiative        32.61°C 🥵  944‰   ~7 used:3  [6]    source:dolphin3
     $10  #79 innovation        31.48°C 🥵  936‰   ~8 used:3  [7]    source:dolphin3
     $11 #107 présentation      30.96°C 🥵  930‰   ~3 used:2  [2]    source:dolphin3
     $16  #39 consultation      28.57°C 😎  896‰  ~13 used:1  [12]   source:dolphin3
     $63  #66 convention        16.61°C 🥶        ~62 used:0  [61]   source:dolphin3
    $121 #123 continue          -0.25°C 🧊       ~121 used:0  [120]  source:dolphin3

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1596 🥳 score:71 ⏱️ 0:03:39.606268

📜 2 sessions

Octordle Classic

1. WOVEN attempts:13 score:13
2. BUGLE attempts:5 score:5
3. UDDER attempts:6 score:6
4. BLURB attempts:7 score:7
5. LINEN attempts:8 score:8
6. DINGY attempts:9 score:9
7. MUMMY attempts:11 score:11
8. ALPHA attempts:12 score:12

# [squareword.org](squareword.org) 🧩 #1589 🥳 8 ⏱️ 0:01:47.246465

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S W I S H
    P H O T O
    R E N A L
    A R I S E
    T E C H S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1526 🥳 320 ⏱️ 0:57:45.946700

🤔 321 attempts
📜 1 sessions
🫧 22 chat sessions
⁉️ 108 chat prompts
🤖 108 dolphin3:latest replies
🥵   2 😎  38 🥶 260 🧊  20

      $1 #321 mechanic       100.00°C 🥳 1000‰ ~301 used:0  [300]  source:dolphin3
      $2 #162 carburetor      42.18°C 🥵  928‰  ~34 used:67 [33]   source:dolphin3
      $3 #160 engine          40.49°C 🥵  902‰  ~30 used:42 [29]   source:dolphin3
      $4 #146 gearbox         37.90°C 😎  854‰  ~39 used:17 [38]   source:dolphin3
      $5 #207 pilot           37.48°C 😎  844‰  ~24 used:4  [23]   source:dolphin3
      $6 #118 repair          37.45°C 😎  841‰  ~36 used:10 [35]   source:dolphin3
      $7 #197 muffler         37.24°C 😎  834‰  ~25 used:4  [24]   source:dolphin3
      $8  #85 hydraulic       37.03°C 😎  825‰  ~37 used:10 [36]   source:dolphin3
      $9 #147 motor           37.01°C 😎  824‰  ~26 used:4  [25]   source:dolphin3
     $10 #130 maintenance     36.39°C 😎  803‰  ~27 used:4  [26]   source:dolphin3
     $11 #210 lifter          35.74°C 😎  784‰  ~28 used:4  [27]   source:dolphin3
     $12 #312 tester          34.91°C 😎  761‰   ~1 used:1  [0]    source:dolphin3
     $42 #214 gasket          25.83°C 🥶        ~41 used:0  [40]   source:dolphin3
    $302  #67 tape            -0.21°C 🧊       ~302 used:0  [301]  source:dolphin3
