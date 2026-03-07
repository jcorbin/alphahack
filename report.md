# 2026-03-08

- 🔗 spaceword.org 🧩 2026-03-07 🏁 score 2168 ranked 38.1% 123/323 ⏱️ 3:38:29.515737
- 🔗 alfagok.diginaut.net 🧩 #491 🥳 28 ⏱️ 0:00:32.271408
- 🔗 alphaguess.com 🧩 #958 🥳 24 ⏱️ 0:00:30.503899
- 🔗 dontwordle.com 🧩 #1384 🥳 6 ⏱️ 0:01:41.567728
- 🔗 dictionary.com hurdle 🧩 #1527 🥳 15 ⏱️ 0:02:29.736726
- 🔗 Quordle Classic 🧩 #1504 🥳 score:18 ⏱️ 0:01:13.280692
- 🔗 Octordle Classic 🧩 #1504 🥳 score:60 ⏱️ 0:03:42.417500
- 🔗 squareword.org 🧩 #1497 🥳 8 ⏱️ 0:02:27.088682
- 🔗 cemantle.certitudes.org 🧩 #1434 🥳 257 ⏱️ 0:14:28.103263
- 🔗 cemantix.certitudes.org 🧩 #1467 🥳 145 ⏱️ 0:16:11.287524

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







# [spaceword.org](spaceword.org) 🧩 2026-03-07 🏁 score 2168 ranked 38.1% 123/323 ⏱️ 3:38:29.515737

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 123/323

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ R _ E _ H _   
      _ A _ Q U O T H A _   
      _ V _ _ N _ U _ J _   
      _ O N A G R I _ I _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #491 🥳 28 ⏱️ 0:00:32.271408

🤔 28 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+2      [     2] -cijferig 
    @+199812 [199812] lijm      q0  ? ␅
    @+199812 [199812] lijm      q1  ? after
    @+247696 [247696] op        q4  ? ␅
    @+247696 [247696] op        q5  ? after
    @+260582 [260582] pater     q8  ? ␅
    @+260582 [260582] pater     q9  ? after
    @+267035 [267035] plomp     q10 ? ␅
    @+267035 [267035] plomp     q11 ? after
    @+270108 [270108] pot       q12 ? ␅
    @+270108 [270108] pot       q13 ? after
    @+271769 [271769] prijs     q14 ? ␅
    @+271769 [271769] prijs     q15 ? after
    @+272112 [272112] prik      q18 ? ␅
    @+272112 [272112] prik      q19 ? after
    @+272195 [272195] pril      q22 ? ␅
    @+272195 [272195] pril      q23 ? after
    @+272242 [272242] primo     q24 ? ␅
    @+272242 [272242] primo     q25 ? after
    @+272263 [272263] principe  q26 ? ␅
    @+272263 [272263] principe  q27 ? it
    @+272263 [272263] principe  done. it
    @+272286 [272286] prins     q20 ? ␅
    @+272286 [272286] prins     q21 ? before
    @+272579 [272579] privé     q16 ? ␅
    @+272579 [272579] privé     q17 ? before
    @+273501 [273501] proef     q6  ? ␅
    @+273501 [273501] proef     q7  ? before
    @+299699 [299699] schub     q2  ? ␅
    @+299699 [299699] schub     q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #958 🥳 24 ⏱️ 0:00:30.503899

🤔 24 attempts
📜 1 sessions

    @       [    0] aa          
    @+1     [    1] aah         
    @+2     [    2] aahed       
    @+3     [    3] aahing      
    @+23682 [23682] camp        q4  ? ␅
    @+23682 [23682] camp        q5  ? after
    @+35525 [35525] convention  q6  ? ␅
    @+35525 [35525] convention  q7  ? after
    @+36091 [36091] cor         q14 ? ␅
    @+36091 [36091] cor         q15 ? after
    @+36402 [36402] corona      q16 ? ␅
    @+36402 [36402] corona      q17 ? after
    @+36481 [36481] corps       q20 ? ␅
    @+36481 [36481] corps       q21 ? after
    @+36508 [36508] correct     q22 ? ␅
    @+36508 [36508] correct     q23 ? it
    @+36508 [36508] correct     done. it
    @+36564 [36564] corrigendum q18 ? ␅
    @+36564 [36564] corrigendum q19 ? before
    @+36726 [36726] cos         q12 ? ␅
    @+36726 [36726] cos         q13 ? before
    @+38184 [38184] crazy       q10 ? ␅
    @+38184 [38184] crazy       q11 ? before
    @+40841 [40841] da          q8  ? ␅
    @+40841 [40841] da          q9  ? before
    @+47381 [47381] dis         q2  ? ␅
    @+47381 [47381] dis         q3  ? before
    @+98218 [98218] mach        q0  ? ␅
    @+98218 [98218] mach        q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1384 🥳 6 ⏱️ 0:01:41.567728

📜 1 sessions
💰 score: 30

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MUMUS n n n n n remain:4833
    ⬜⬜⬜⬜⬜ tried:NANNA n n n n n remain:1877
    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:824
    ⬜⬜⬜⬜⬜ tried:TOROT n n n n n remain:117
    ⬜🟨⬜⬜⬜ tried:XYLYL n m n n n remain:18
    ⬜🟩🟩⬜🟩 tried:DEEDY n Y Y n Y remain:3

    Undos used: 3

      3 words remaining
    x 10 unused letters
    = 30 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1527 🥳 15 ⏱️ 0:02:29.736726

📜 1 sessions
💰 score: 10100

    3/6
    ABLES ⬜⬜⬜🟨⬜
    THEIR 🟨⬜🟨⬜🟨
    ROUTE 🟩🟩🟩🟩🟩
    3/6
    ROUTE 🟨⬜🟨⬜⬜
    DURAS ⬜🟩🟩⬜🟨
    SURLY 🟩🟩🟩🟩🟩
    4/6
    SURLY ⬜🟨🟨⬜⬜
    PRUNE ⬜🟨🟨⬜🟩
    ROGUE 🟩⬜⬜🟩🟩
    REVUE 🟩🟩🟩🟩🟩
    4/6
    REVUE ⬜⬜⬜⬜🟩
    AISLE ⬜⬜🟨⬜🟩
    THOSE ⬜🟩🟩🟩🟩
    CHOSE 🟩🟩🟩🟩🟩
    Final 1/2
    DECRY 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1504 🥳 score:18 ⏱️ 0:01:13.280692

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. RETCH attempts:6 score:6
2. SLANG attempts:4 score:4
3. AGONY attempts:5 score:5
4. MURKY attempts:3 score:3

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1504 🥳 score:60 ⏱️ 0:03:42.417500

📜 1 sessions

Octordle Classic

1. WHOOP attempts:5 score:5
2. GONER attempts:10 score:10
3. OPIUM attempts:4 score:4
4. CHOSE attempts:7 score:7
5. WIDTH attempts:8 score:8
6. CRIED attempts:9 score:9
7. CLING attempts:11 score:11
8. MARSH attempts:6 score:6

# [squareword.org](squareword.org) 🧩 #1497 🥳 8 ⏱️ 0:02:27.088682

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S E E D S
    T A R O T
    A T O N E
    L E D G E
    K N E A D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1434 🥳 257 ⏱️ 0:14:28.103263

🤔 258 attempts
📜 1 sessions
🫧 17 chat sessions
⁉️ 82 chat prompts
🤖 82 dolphin3:latest replies
🔥   1 🥵   6 😎  29 🥶 205 🧊  16

      $1 #258 convenient       100.00°C 🥳 1000‰ ~242 used:0  [241]  source:dolphin3
      $2 #249 accessible        52.51°C 🔥  992‰   ~1 used:5  [0]    source:dolphin3
      $3 #231 reliable          44.38°C 🥵  978‰  ~14 used:12 [13]   source:dolphin3
      $4 #184 safe              39.69°C 🥵  967‰  ~30 used:28 [29]   source:dolphin3
      $5 #255 securely          37.29°C 🥵  948‰   ~3 used:3  [2]    source:dolphin3
      $6 #136 access            36.93°C 🥵  943‰  ~31 used:32 [30]   source:dolphin3
      $7 #233 dependable        36.03°C 🥵  934‰   ~4 used:7  [3]    source:dolphin3
      $8 #251 available         33.95°C 🥵  902‰   ~2 used:0  [1]    source:dolphin3
      $9  #59 interface         31.80°C 😎  844‰  ~36 used:35 [35]   source:dolphin3
     $10 #257 approachable      31.74°C 😎  839‰   ~5 used:0  [4]    source:dolphin3
     $11 #158 secure            31.47°C 😎  830‰  ~32 used:4  [31]   source:dolphin3
     $12  #55 gateway           31.31°C 😎  825‰  ~35 used:17 [34]   source:dolphin3
     $38  #84 wireless          21.77°C 🥶        ~45 used:0  [44]   source:dolphin3
    $243   #7 quantum           -0.55°C 🧊       ~243 used:0  [242]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1467 🥳 145 ⏱️ 0:16:11.287524

🤔 146 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 29 chat prompts
🤖 29 dolphin3:latest replies
🔥  1 🥵  6 😎 26 🥶 76 🧊 36

      $1 #146 médecine            100.00°C 🥳 1000‰ ~110 used:0  [109]  source:dolphin3
      $2  #83 faculté              54.66°C 🔥  998‰   ~6 used:26 [5]    source:dolphin3
      $3 #141 pharmacologie        44.88°C 🥵  979‰   ~1 used:0  [0]    source:dolphin3
      $4 #128 biologie             44.02°C 🥵  972‰   ~7 used:3  [6]    source:dolphin3
      $5 #129 anatomie             42.04°C 🥵  956‰   ~5 used:2  [4]    source:dolphin3
      $6 #133 embryologie          40.22°C 🥵  943‰   ~2 used:0  [1]    source:dolphin3
      $7 #142 toxicologie          39.31°C 🥵  926‰   ~3 used:0  [2]    source:dolphin3
      $8 #136 immunologie          38.89°C 🥵  920‰   ~4 used:0  [3]    source:dolphin3
      $9 #110 scientifique         34.44°C 😎  839‰  ~31 used:3  [30]   source:dolphin3
     $10 #130 biochimie            31.28°C 😎  759‰   ~8 used:0  [7]    source:dolphin3
     $11  #75 université           30.62°C 😎  737‰  ~33 used:9  [32]   source:dolphin3
     $12 #126 professeur           30.34°C 😎  728‰   ~9 used:0  [8]    source:dolphin3
     $35 #107 postdoctoral         20.46°C 🥶        ~39 used:0  [38]   source:dolphin3
    $111  #14 accord               -0.37°C 🧊       ~111 used:0  [110]  source:dolphin3
