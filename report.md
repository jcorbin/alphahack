# 2026-06-17

- 🔗 spaceword.org 🧩 2026-06-16 🏁 score 2173 ranked 11.4% 36/316 ⏱️ 0:19:04.801445
- 🔗 alfagok.diginaut.net 🧩 #592 🥳 42 ⏱️ 0:01:10.849884
- 🔗 cemantix.certitudes.org 🧩 #1568 🥳 277 ⏱️ 0:12:37.582844
- 🔗 cemantle.certitudes.org 🧩 #1535 🥳 290 ⏱️ 0:02:21.222533
- 🔗 dontwordle.com 🧩 #1485 🥳 6 ⏱️ 0:01:40.332531
- 🔗 alphaguess.com 🧩 #1059 🥳 28 ⏱️ 0:01:27.408991
- 🔗 dictionary.com hurdle 🧩 #1628 🥳 19 ⏱️ 0:07:06.016111
- 🔗 Quordle Classic 🧩 #1605 🥳 score:18 ⏱️ 0:01:31.837907
- 🔗 Octordle Classic 🧩 #1605 🥳 score:59 ⏱️ 0:06:40.408695
- 🔗 squareword.org 🧩 #1598 🥳 7 ⏱️ 0:02:11.192931

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








# [spaceword.org](spaceword.org) 🧩 2026-06-16 🏁 score 2173 ranked 11.4% 36/316 ⏱️ 0:19:04.801445

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 36/316

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ V I N _ _ _   
      _ _ _ _ _ _ E _ _ _   
      _ _ _ _ M A R _ _ _   
      _ _ _ _ _ P O _ _ _   
      _ _ _ _ C E L _ _ _   
      _ _ _ _ _ L I _ _ _   
      _ _ _ _ T I _ _ _ _   
      _ _ _ _ O K E _ _ _   
      _ _ _ _ W E _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #592 🥳 42 ⏱️ 0:01:10.849884

🤔 42 attempts
📜 1 sessions

    @        [     0] &-teken         
    @+199764 [199764] lijm            q0  ? ␅
    @+199764 [199764] lijm            q1  ? after
    @+223525 [223525] mol             q6  ? ␅
    @+223525 [223525] mol             q7  ? after
    @+229542 [229542] natuur          q10 ? ␅
    @+229542 [229542] natuur          q11 ? after
    @+232553 [232553] niets           q12 ? ␅
    @+232553 [232553] niets           q13 ? after
    @+233276 [233276] ninja           q26 ? ␅
    @+233276 [233276] ninja           q27 ? after
    @+233611 [233611] non             q28 ? ␅
    @+233611 [233611] non             q29 ? after
    @+233726 [233726] nood            q30 ? ␅
    @+233726 [233726] nood            q31 ? after
    @+233861 [233861] noodplan        q32 ? ␅
    @+233861 [233861] noodplan        q33 ? after
    @+233927 [233927] noodvaccinaties q34 ? ␅
    @+233927 [233927] noodvaccinaties q35 ? after
    @+233960 [233960] noodzaak        q36 ? ␅
    @+233960 [233960] noodzaak        q37 ? after
    @+233977 [233977] noodziekenhuis  q38 ? ␅
    @+233977 [233977] noodziekenhuis  q39 ? after
    @+233982 [233982] nooit           q40 ? ␅
    @+233982 [233982] nooit           q41 ? it
    @+233982 [233982] nooit           done. it
    @+233993 [233993] noord           q14 ? ␅
    @+233993 [233993] noord           q15 ? before
    @+235574 [235574] octrooi         q8  ? ␅
    @+235574 [235574] octrooi         q9  ? before
    @+247630 [247630] op              q5  ? before

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1568 🥳 277 ⏱️ 0:12:37.582844

🤔 278 attempts
📜 1 sessions
🫧 22 chat sessions
⁉️ 114 chat prompts
🤖 113 gemma4:e2b replies
🤖 1 gemma4:12b replies
😱   1 🔥   5 🥵  12 😎  58 🥶 181 🧊  20

      $1 #278 génie            100.00°C 🥳 1000‰ ~258 used:0   [257]  source:gemma4:e2b
      $2 #154 prodigieux        47.46°C 😱  999‰   ~4 used:140 [3]    source:gemma4:e2b
      $3 #211 visionnaire       44.10°C 🔥  998‰   ~8 used:33  [7]    source:gemma4:e2b
      $4 #164 admirable         42.23°C 🔥  997‰  ~16 used:48  [15]   source:gemma4:e2b
      $5 #263 inventeur         40.36°C 🔥  995‰   ~1 used:4   [0]    source:gemma4:e2b
      $6  #87 sublime           39.53°C 🔥  993‰   ~9 used:37  [8]    source:gemma4:e2b
      $7 #265 ingénieux         38.59°C 🥵  989‰   ~2 used:5   [1]    source:gemma4:e2b
      $8 #272 ingéniosité       35.54°C 🥵  977‰   ~3 used:1   [2]    source:gemma4:e2b
      $9 #139 brillant          35.51°C 🥵  976‰  ~10 used:4   [9]    source:gemma4:e2b
     $10  #98 gloire            33.90°C 🥵  965‰  ~18 used:6   [17]   source:gemma4:e2b
     $11 #227 audace            33.78°C 🥵  964‰   ~5 used:3   [4]    source:gemma4:e2b
     $20 #268 talentueux        30.58°C 😎  897‰  ~19 used:0   [18]   source:gemma4:e2b
     $78 #150 excellence        22.53°C 🥶        ~86 used:0   [85]   source:gemma4:e2b
    $259  #18 défense           -0.23°C 🧊       ~259 used:0   [258]  source:gemma4:e2b

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1535 🥳 290 ⏱️ 0:02:21.222533

🤔 291 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 36 chat prompts
🤖 36 dolphin3:latest replies
😱   1 🔥   2 🥵   9 😎  36 🥶 222 🧊  20

      $1 #291 voting          100.00°C 🥳 1000‰ ~271 used:0  [270]  source:dolphin3
      $2 #290 vote             72.74°C 😱  999‰   ~1 used:1  [0]    source:dolphin3
      $3 #277 ballot           57.43°C 🔥  997‰   ~2 used:2  [1]    source:dolphin3
      $4 #274 election         50.66°C 🔥  994‰   ~3 used:4  [2]    source:dolphin3
      $5 #281 elector          43.65°C 🥵  989‰   ~4 used:0  [3]    source:dolphin3
      $6 #287 precinct         42.02°C 🥵  984‰   ~5 used:0  [4]    source:dolphin3
      $7 #285 poll             41.18°C 🥵  981‰   ~6 used:0  [5]    source:dolphin3
      $8 #282 electorate       38.51°C 🥵  972‰   ~7 used:0  [6]    source:dolphin3
      $9 #247 candidate        30.35°C 🥵  933‰  ~10 used:5  [9]    source:dolphin3
     $10 #276 nomination       30.25°C 🥵  931‰   ~8 used:0  [7]    source:dolphin3
     $11 #268 nominee          29.84°C 🥵  928‰   ~9 used:1  [8]    source:dolphin3
     $14 #109 postal           26.72°C 😎  880‰  ~48 used:10 [47]   source:dolphin3
     $50 #150 security         16.87°C 🥶        ~49 used:0  [48]   source:dolphin3
    $272  #79 comprehensive    -0.35°C 🧊       ~272 used:0  [271]  source:dolphin3

# [dontwordle.com](dontwordle.com) 🧩 #1485 🥳 6 ⏱️ 0:01:40.332531

📜 1 sessions
💰 score: 4

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:KAPPA n n n n n remain:5707
    ⬜⬜⬜⬜⬜ tried:MUMUS n n n n n remain:1921
    ⬜⬜⬜⬜⬜ tried:JIFFY n n n n n remain:645
    ⬜⬜⬜⬜⬜ tried:CRWTH n n n n n remain:106
    ⬜🟩⬜⬜⬜ tried:DOGGO n Y n n n remain:8
    ⬜🟩⬜🟨🟨 tried:VOXEL n Y n m m remain:1

    Undos used: 2

      1 words remaining
    x 4 unused letters
    = 4 total score

# [alphaguess.com](alphaguess.com) 🧩 #1059 🥳 28 ⏱️ 0:01:27.408991

🤔 28 attempts
📜 1 sessions

    @        [     0] aa      
    @+2      [     2] aahed   
    @+98214  [ 98214] mach    q0  ? ␅
    @+98214  [ 98214] mach    q1  ? after
    @+98214  [ 98214] mach    q2  ? ␅
    @+98214  [ 98214] mach    q3  ? after
    @+122775 [122775] parr    q6  ? ␅
    @+122775 [122775] parr    q7  ? after
    @+123688 [123688] pe      q14 ? ␅
    @+123688 [123688] pe      q15 ? after
    @+123753 [123753] peak    q24 ? ␅
    @+123753 [123753] peak    q25 ? after
    @+123780 [123780] pearl   q26 ? ␅
    @+123780 [123780] pearl   q27 ? it
    @+123780 [123780] pearl   done. it
    @+123815 [123815] peas    q22 ? ␅
    @+123815 [123815] peas    q23 ? before
    @+123941 [123941] pedal   q20 ? ␅
    @+123941 [123941] pedal   q21 ? before
    @+124215 [124215] pelican q18 ? ␅
    @+124215 [124215] pelican q19 ? before
    @+124742 [124742] per     q16 ? ␅
    @+124742 [124742] per     q17 ? before
    @+125807 [125807] petti   q12 ? ␅
    @+125807 [125807] petti   q13 ? before
    @+128844 [128844] play    q10 ? ␅
    @+128844 [128844] play    q11 ? before
    @+135066 [135066] proper  q8  ? ␅
    @+135066 [135066] proper  q9  ? before
    @+147364 [147364] rhotic  q4  ? ␅
    @+147364 [147364] rhotic  q5  ? before

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1628 🥳 19 ⏱️ 0:07:06.016111

📜 1 sessions
💰 score: 9700

    4/6
    LARES ⬜⬜⬜🟨🟨
    STONE 🟨🟨⬜⬜🟨
    HEIST ⬜🟩⬜🟨🟨
    ZESTY 🟩🟩🟩🟩🟩
    5/6
    ZESTY ⬜🟨🟨🟨⬜
    RATES ⬜⬜🟨🟨🟨
    STENO 🟨🟨🟩⬜⬜
    CHEST ⬜⬜🟩🟩🟩
    GUEST 🟩🟩🟩🟩🟩
    4/6
    GUEST ⬜⬜⬜⬜🟨
    RATIO 🟨⬜🟨⬜🟨
    THROW 🟩🟨🟩🟨⬜
    TORCH 🟩🟩🟩🟩🟩
    4/6
    TORCH 🟨⬜⬜⬜⬜
    NEATS ⬜🟨⬜🟨🟨
    SLEPT 🟩⬜🟩⬜🟨
    STEED 🟩🟩🟩🟩🟩
    Final 2/2
    JOINT ⬜🟩🟩🟩🟩
    POINT 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1605 🥳 score:18 ⏱️ 0:01:31.837907

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. HOIST attempts:5 score:5
2. PLUSH attempts:4 score:4
3. GROUP attempts:6 score:6
4. LEMUR attempts:3 score:3

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1605 🥳 score:59 ⏱️ 0:06:40.408695

📜 1 sessions

Octordle Classic

1. SHRUG attempts:11 score:11
2. TOTEM attempts:7 score:7
3. LIMBO attempts:5 score:5
4. ACRID attempts:8 score:8
5. UNITE attempts:9 score:9
6. STEAL attempts:10 score:10
7. NICER attempts:3 score:3
8. BLOKE attempts:6 score:6

# [squareword.org](squareword.org) 🧩 #1598 🥳 7 ⏱️ 0:02:11.192931

📜 2 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B E V E L
    E X I L E
    S E T U P
    T R A D E
    S T E E R
