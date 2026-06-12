# 2026-06-12

- 🔗 spaceword.org 🧩 2026-06-11 🏁 score 2168 ranked 35.3% 120/340 ⏱️ 14:20:22.222899
- 🔗 alfagok.diginaut.net 🧩 #587 🥳 22 ⏱️ 0:00:30.799488
- 🔗 alphaguess.com 🧩 #1054 🥳 36 ⏱️ 0:00:40.887372
- 🔗 dontwordle.com 🧩 #1480 🥳 6 ⏱️ 0:01:12.583305
- 🔗 dictionary.com hurdle 🧩 #1623 🥳 20 ⏱️ 0:03:15.321197
- 🔗 Quordle Classic 🧩 #1600 🥳 score:23 ⏱️ 0:01:26.535642
- 🔗 Octordle Classic 🧩 #1600 🥳 score:60 ⏱️ 0:03:21.320693
- 🔗 squareword.org 🧩 #1593 🥳 9 ⏱️ 0:02:29.345022
- 🔗 cemantle.certitudes.org 🧩 #1530 🥳 300 ⏱️ 0:02:58.166936
- 🔗 cemantix.certitudes.org 🧩 #1563 🥳 59 ⏱️ 0:00:50.529778

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



# [spaceword.org](spaceword.org) 🧩 2026-06-11 🏁 score 2168 ranked 35.3% 120/340 ⏱️ 14:20:22.222899

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 120/340

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ A W F U L _ _ _ _   
      _ _ _ _ _ U _ _ H _   
      _ A V O I D S _ I _   
      _ B _ S N O O Z E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #587 🥳 22 ⏱️ 0:00:30.799488

🤔 22 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199766 [199766] lijm      q0  ? ␅
    @+199766 [199766] lijm      q1  ? after
    @+199766 [199766] lijm      q2  ? ␅
    @+199766 [199766] lijm      q3  ? after
    @+299629 [299629] schub     q4  ? ␅
    @+299629 [299629] schub     q5  ? after
    @+311793 [311793] spier     q10 ? ␅
    @+311793 [311793] spier     q11 ? after
    @+314786 [314786] staats    q14 ? ␅
    @+314786 [314786] staats    q15 ? after
    @+316274 [316274] standaard q16 ? ␅
    @+316274 [316274] standaard q17 ? after
    @+316916 [316916] stat      q18 ? ␅
    @+316916 [316916] stat      q19 ? after
    @+317359 [317359] steen     q20 ? ␅
    @+317359 [317359] steen     q21 ? it
    @+317359 [317359] steen     done. it
    @+317986 [317986] stem      q12 ? ␅
    @+317986 [317986] stem      q13 ? before
    @+324189 [324189] sub       q8  ? ␅
    @+324189 [324189] sub       q9  ? before
    @+349391 [349391] vakantie  q6  ? ␅
    @+349391 [349391] vakantie  q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1054 🥳 36 ⏱️ 0:00:40.887372

🤔 36 attempts
📜 1 sessions

    @       [    0] aa         
    @+47380 [47380] dis        q2  ? ␅
    @+47380 [47380] dis        q3  ? after
    @+72797 [72797] gremolata  q4  ? ␅
    @+72797 [72797] gremolata  q5  ? after
    @+85500 [85500] ins        q6  ? ␅
    @+85500 [85500] ins        q7  ? after
    @+88660 [88660] jacks      q10 ? ␅
    @+88660 [88660] jacks      q11 ? after
    @+90191 [90191] ka         q12 ? ␅
    @+90191 [90191] ka         q13 ? after
    @+90396 [90396] kanes      q18 ? ␅
    @+90396 [90396] kanes      q19 ? after
    @+90448 [90448] karat      q22 ? ␅
    @+90448 [90448] karat      q23 ? after
    @+90449 [90449] karate     q34 ? ␅
    @+90449 [90449] karate     q35 ? it
    @+90449 [90449] karate     done. it
    @+90450 [90450] karateist  q32 ? ␅
    @+90450 [90450] karateist  q33 ? before
    @+90451 [90451] karateists q30 ? ␅
    @+90451 [90451] karateists q31 ? before
    @+90454 [90454] karma      q28 ? ␅
    @+90454 [90454] karma      q29 ? before
    @+90460 [90460] karoo      q26 ? ␅
    @+90460 [90460] karoo      q27 ? before
    @+90471 [90471] kart       q24 ? ␅
    @+90471 [90471] kart       q25 ? before
    @+90497 [90497] kas        q20 ? ␅
    @+90497 [90497] kas        q21 ? before
    @+90600 [90600] keck       q17 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1480 🥳 6 ⏱️ 0:01:12.583305

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MOSSO n n n n n remain:4035
    ⬜⬜⬜⬜⬜ tried:DEWED n n n n n remain:1391
    ⬜⬜⬜⬜⬜ tried:YUKKY n n n n n remain:552
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:209
    🟨⬜⬜⬜⬜ tried:GRRRL m n n n n remain:12
    ⬜⬜🟨🟩🟨 tried:VIGIA n n m Y m remain:1

    Undos used: 2

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1623 🥳 20 ⏱️ 0:03:15.321197

📜 1 sessions
💰 score: 9600

    5/6
    RAISE 🟨🟨⬜🟨⬜
    ORCAS ⬜🟨⬜🟨🟨
    SUTRA 🟩⬜⬜🟩🟨
    SHARK 🟩⬜🟩🟩🟩
    SPARK 🟩🟩🟩🟩🟩
    5/6
    SPARK ⬜⬜⬜🟨⬜
    IRONY 🟨🟨⬜⬜⬜
    RIGHT 🟨🟩⬜⬜⬜
    LIFER ⬜🟩🟨🟩🟩
    FIBER 🟩🟩🟩🟩🟩
    3/6
    FIBER ⬜🟨⬜⬜⬜
    SAINT 🟩⬜🟨🟨⬜
    SONIC 🟩🟩🟩🟩🟩
    6/6
    SONIC ⬜⬜⬜⬜⬜
    LAYER ⬜🟨⬜🟨⬜
    DEATH ⬜🟨🟩⬜⬜
    QUAKE ⬜⬜🟩⬜🟩
    AMAZE 🟩⬜🟩⬜🟩
    AGAPE 🟩🟩🟩🟩🟩
    Final 1/2
    PINCH 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1600 🥳 score:23 ⏱️ 0:01:26.535642

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. TENTH attempts:5 score:5
2. SHOAL attempts:6 score:6
3. JELLY attempts:8 score:8
4. UNIFY attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1600 🥳 score:60 ⏱️ 0:03:21.320693

📜 1 sessions

Octordle Classic

1. PULSE attempts:3 score:3
2. SPRIG attempts:6 score:6
3. DEPTH attempts:4 score:4
4. AORTA attempts:8 score:8
5. SKATE attempts:9 score:9
6. NEEDY attempts:11 score:11
7. BILLY attempts:10 score:12
8. SMALL attempts:7 score:7

# [squareword.org](squareword.org) 🧩 #1593 🥳 9 ⏱️ 0:02:29.345022

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟩 🟨 🟩 🟨
    🟩 🟨 🟩 🟩 🟩
    🟩 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    T A M E D
    A G A V E
    R A V E N
    O P E N S
    T E N S E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1530 🥳 300 ⏱️ 0:02:58.166936

🤔 301 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 45 chat prompts
🤖 45 dolphin3:latest replies
😱   1 🔥   3 🥵   6 😎  19 🥶 264 🧊   7

      $1 #301 fluid             100.00°C 🥳 1000‰ ~294 used:0  [293]  source:dolphin3
      $2 #240 liquid             50.21°C 😱  999‰   ~1 used:9  [0]    source:dolphin3
      $3 #216 fluidity           48.36°C 🔥  997‰   ~4 used:6  [3]    source:dolphin3
      $4 #221 capillary          45.70°C 🔥  994‰   ~3 used:4  [2]    source:dolphin3
      $5 #234 viscosity          45.47°C 🔥  991‰   ~2 used:3  [1]    source:dolphin3
      $6 #224 laminar            43.55°C 🥵  981‰   ~5 used:0  [4]    source:dolphin3
      $7 #276 vapor              43.27°C 🥵  977‰   ~6 used:0  [5]    source:dolphin3
      $8  #73 kinetic            41.76°C 🥵  951‰  ~29 used:28 [28]   source:dolphin3
      $9 #123 dynamic            40.72°C 🥵  924‰  ~26 used:16 [25]   source:dolphin3
     $10  #98 paramagnetic       40.51°C 🥵  918‰  ~25 used:13 [24]   source:dolphin3
     $11 #157 oxygen             39.66°C 🥵  901‰  ~24 used:11 [23]   source:dolphin3
     $12 #266 blood              39.44°C 😎  899‰   ~7 used:0  [6]    source:dolphin3
     $31 #121 transduction       31.46°C 🥶        ~35 used:0  [34]   source:dolphin3
    $295 #280 dish               -0.25°C 🧊       ~295 used:0  [294]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1563 🥳 59 ⏱️ 0:00:50.529778

🤔 60 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 6 chat prompts
🤖 6 dolphin3:latest replies
😱  1 🔥  1 🥵  5 😎 13 🥶 31 🧊  8

     $1 #60 rive         100.00°C 🥳 1000‰ ~52 used:0 [51]  source:dolphin3
     $2 #21 fleuve        65.05°C 😱  999‰  ~1 used:6 [0]   source:dolphin3
     $3 #50 rivière       52.33°C 🔥  995‰  ~2 used:2 [1]   source:dolphin3
     $4 #36 lac           44.83°C 🥵  987‰  ~7 used:3 [6]   source:dolphin3
     $5 #59 marécage      40.36°C 🥵  965‰  ~3 used:0 [2]   source:dolphin3
     $6 #42 estuaire      39.52°C 🥵  960‰  ~4 used:0 [3]   source:dolphin3
     $7 #58 lacs          36.26°C 🥵  932‰  ~5 used:0 [4]   source:dolphin3
     $8 #54 étang         35.61°C 🥵  917‰  ~6 used:0 [5]   source:dolphin3
     $9 #52 torrent       34.83°C 😎  893‰  ~8 used:0 [7]   source:dolphin3
    $10 #47 mer           34.76°C 😎  892‰  ~9 used:0 [8]   source:dolphin3
    $11 #19 brume         34.43°C 😎  889‰ ~10 used:1 [9]   source:dolphin3
    $12 #26 river         33.04°C 😎  849‰ ~11 used:0 [10]  source:dolphin3
    $22 #23 montagne      23.45°C 🥶       ~22 used:0 [21]  source:dolphin3
    $53  #4 gâteau        -0.01°C 🧊       ~53 used:0 [52]  source:dolphin3
