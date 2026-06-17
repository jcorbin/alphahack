# 2026-06-18

- 🔗 spaceword.org 🧩 2026-06-17 🏁 score 2168 ranked 37.2% 119/320 ⏱️ 4:05:10.775773
- 🔗 alfagok.diginaut.net 🧩 #593 🥳 38 ⏱️ 0:00:50.579628
- 🔗 alphaguess.com 🧩 #1060 🥳 16 ⏱️ 0:00:23.583525
- 🔗 dontwordle.com 🧩 #1486 🥳 6 ⏱️ 0:02:27.217712
- 🔗 dictionary.com hurdle 🧩 #1629 🥳 17 ⏱️ 0:03:12.272625
- 🔗 Quordle Classic 🧩 #1606 🥳 score:21 ⏱️ 0:01:22.401733
- 🔗 Octordle Classic 🧩 #1606 🥳 score:64 ⏱️ 0:03:59.571669
- 🔗 squareword.org 🧩 #1599 🥳 8 ⏱️ 0:02:36.081969
- 🔗 cemantle.certitudes.org 🧩 #1536 🥳 417 ⏱️ 0:09:59.093793
- 🔗 cemantix.certitudes.org 🧩 #1570 🥳 72 ⏱️ 0:04:40.369984

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









# [spaceword.org](spaceword.org) 🧩 2026-06-17 🏁 score 2168 ranked 37.2% 119/320 ⏱️ 4:05:10.775773

📜 5 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 119/320

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ J E U X _ _ _   
      _ _ _ U _ G _ _ _ _   
      _ _ _ V U L N _ _ _   
      _ _ _ I _ I _ _ _ _   
      _ _ _ E _ F _ _ _ _   
      _ _ _ S R I _ _ _ _   
      _ _ _ _ _ E _ _ _ _   
      _ _ _ P A S _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #593 🥳 38 ⏱️ 0:00:50.579628

🤔 38 attempts
📜 1 sessions

    @       [    0] &-teken    
    @+49817 [49817] boks       q4  ? ␅
    @+49817 [49817] boks       q5  ? after
    @+74721 [74721] dc         q6  ? ␅
    @+74721 [74721] dc         q7  ? after
    @+87180 [87180] draag      q8  ? ␅
    @+87180 [87180] draag      q9  ? after
    @+90030 [90030] dubbel     q12 ? ␅
    @+90030 [90030] dubbel     q13 ? after
    @+90847 [90847] duivels    q16 ? ␅
    @+90847 [90847] duivels    q17 ? after
    @+91266 [91266] dus        q18 ? ␅
    @+91266 [91266] dus        q19 ? after
    @+91365 [91365] duvel      q22 ? ␅
    @+91365 [91365] duvel      q23 ? after
    @+91375 [91375] duw        q30 ? ␅
    @+91375 [91375] duw        q31 ? after
    @+91383 [91383] duweenheid q34 ? ␅
    @+91383 [91383] duweenheid q35 ? after
    @+91385 [91385] duwen      q36 ? ␅
    @+91385 [91385] duwen      q37 ? it
    @+91385 [91385] duwen      done. it
    @+91391 [91391] duwstang   q32 ? ␅
    @+91391 [91391] duwstang   q33 ? before
    @+91406 [91406] dvd        q28 ? ␅
    @+91406 [91406] dvd        q29 ? before
    @+91468 [91468] dwang      q20 ? ␅
    @+91468 [91468] dwang      q21 ? before
    @+91707 [91707] dwerg      q14 ? ␅
    @+91707 [91707] dwerg      q15 ? before
    @+93395 [93395] eet        q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1060 🥳 16 ⏱️ 0:00:23.583525

🤔 16 attempts
📜 1 sessions

    @        [     0] aa     
    @+1      [     1] aah    
    @+2      [     2] aahed  
    @+3      [     3] aahing 
    @+98214  [ 98214] mach   q0  ? ␅
    @+98214  [ 98214] mach   q1  ? after
    @+98214  [ 98214] mach   q2  ? ␅
    @+98214  [ 98214] mach   q3  ? after
    @+98214  [ 98214] mach   q4  ? ␅
    @+98214  [ 98214] mach   q5  ? after
    @+147364 [147364] rhotic q6  ? ␅
    @+147364 [147364] rhotic q7  ? after
    @+153313 [153313] sea    q12 ? ␅
    @+153313 [153313] sea    q13 ? after
    @+156349 [156349] ship   q14 ? ␅
    @+156349 [156349] ship   q15 ? it
    @+156349 [156349] ship   done. it
    @+159481 [159481] slop   q10 ? ␅
    @+159481 [159481] slop   q11 ? before
    @+171634 [171634] ta     q8  ? ␅
    @+171634 [171634] ta     q9  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1486 🥳 6 ⏱️ 0:02:27.217712

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:7266
    ⬜⬜⬜⬜⬜ tried:ADDAX n n n n n remain:2993
    ⬜⬜⬜⬜⬜ tried:CUPPY n n n n n remain:1048
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:330
    🟨🟨⬜⬜🟩 tried:TESTS m m n n Y remain:5
    ⬜🟨🟨🟨🟩 tried:NOTES n m m m Y remain:1

    Undos used: 3

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1629 🥳 17 ⏱️ 0:03:12.272625

📜 1 sessions
💰 score: 9900

    4/6
    ACRES ⬜⬜⬜⬜⬜
    YOGIN 🟨⬜🟨🟨🟨
    LYING ⬜🟩🟩🟩🟩
    DYING 🟩🟩🟩🟩🟩
    4/6
    DYING ⬜⬜⬜⬜⬜
    LACES 🟨🟨⬜⬜⬜
    AFOUL 🟨⬜🟨⬜🟩
    MORAL 🟩🟩🟩🟩🟩
    3/6
    MORAL 🟨⬜⬜🟨⬜
    GAMES ⬜🟨🟨🟨⬜
    ANIME 🟩🟩🟩🟩🟩
    5/6
    ANIME 🟨⬜⬜⬜🟩
    PLATE ⬜⬜🟨⬜🟩
    CARVE 🟩🟩⬜⬜🟩
    CAUSE 🟩🟩⬜⬜🟩
    CACHE 🟩🟩🟩🟩🟩
    Final 1/2
    STOAT 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1606 🥳 score:21 ⏱️ 0:01:22.401733

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. LATCH attempts:6 score:6
2. BRAWL attempts:7 score:7
3. STEEL attempts:3 score:3
4. CRUSH attempts:5 score:5

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1606 🥳 score:64 ⏱️ 0:03:59.571669

📜 2 sessions

Octordle Classic

1. HONOR attempts:8 score:8
2. SOGGY attempts:3 score:3
3. BOUND attempts:10 score:10
4. FLAKE attempts:12 score:12
5. WRIST attempts:6 score:6
6. GROOM attempts:5 score:5
7. SIXTH attempts:9 score:9
8. TOOTH attempts:11 score:11

# [squareword.org](squareword.org) 🧩 #1599 🥳 8 ⏱️ 0:02:36.081969

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟨 🟨 🟩 🟩 🟨
    🟨 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T O A T
    C R O R E
    R A Z E D
    E M E N D
    E S S A Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1536 🥳 417 ⏱️ 0:09:59.093793

🤔 418 attempts
📜 1 sessions
🫧 22 chat sessions
⁉️ 117 chat prompts
🤖 13 qwen3.6:latest replies
🤖 104 dolphin3:latest replies
😱   1 🔥   3 🥵  18 😎  53 🥶 317 🧊  25

      $1 #418 undergo         100.00°C 🥳 1000‰ ~393 used:0  [392]  source:qwen3   
      $2 #374 endure           45.75°C 😱  999‰   ~1 used:29 [0]    source:dolphin3
      $3 #177 perform          43.05°C 🔥  998‰  ~22 used:93 [21]   source:dolphin3
      $4 #238 embark           41.73°C 🔥  996‰  ~19 used:52 [18]   source:dolphin3
      $5 #219 undertake        40.05°C 🔥  992‰   ~6 used:42 [5]    source:dolphin3
      $6 #182 rehabilitation   38.21°C 🥵  989‰  ~20 used:8  [19]   source:dolphin3
      $7 #194 conduct          35.90°C 🥵  979‰   ~7 used:5  [6]    source:dolphin3
      $8 #409 face             34.28°C 🥵  974‰   ~2 used:0  [1]    source:qwen3   
      $9 #263 procedure        33.35°C 🥵  969‰   ~8 used:5  [7]    source:dolphin3
     $10 #250 depart           33.29°C 🥵  968‰   ~9 used:5  [8]    source:dolphin3
     $11 #207 carry            32.78°C 🥵  963‰  ~10 used:5  [9]    source:dolphin3
     $24 #383 survive          29.55°C 😎  898‰  ~23 used:0  [22]   source:qwen3   
     $77 #124 physically       19.84°C 🥶        ~78 used:0  [77]   source:dolphin3
    $394 #304 agreement        -0.03°C 🧊       ~394 used:0  [393]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1570 🥳 72 ⏱️ 0:04:40.369984

🤔 73 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 9 chat prompts
🤖 9 dolphin3:latest replies
🔥  1 🥵  6 😎  5 🥶 45 🧊 15

     $1 #73 galerie        100.00°C 🥳 1000‰ ~58 used:0 [57]  source:dolphin3
     $2 #72 exposition      53.64°C 🔥  998‰  ~1 used:0 [0]   source:dolphin3
     $3 #70 artiste         42.66°C 🥵  989‰  ~2 used:0 [1]   source:dolphin3
     $4 #56 peinture        41.23°C 🥵  984‰  ~5 used:2 [4]   source:dolphin3
     $5 #27 art             37.55°C 🥵  970‰  ~6 used:2 [5]   source:dolphin3
     $6 #23 palais          36.19°C 🥵  953‰  ~7 used:3 [6]   source:dolphin3
     $7 #66 peintre         35.87°C 🥵  951‰  ~3 used:0 [2]   source:dolphin3
     $8 #69 aquarelle       35.37°C 🥵  942‰  ~4 used:0 [3]   source:dolphin3
     $9 #71 dessin          28.16°C 😎  770‰  ~8 used:0 [7]   source:dolphin3
    $10 #48 artistique      27.11°C 😎  709‰  ~9 used:0 [8]   source:dolphin3
    $11 #20 gastronomie     24.10°C 😎  485‰ ~12 used:3 [11]  source:dolphin3
    $12 #45 restaurant      23.20°C 😎  370‰ ~10 used:1 [9]   source:dolphin3
    $14 #40 potager         20.26°C 🥶       ~16 used:1 [15]  source:dolphin3
    $59 #60 traditionnel    -0.06°C 🧊       ~59 used:0 [58]  source:dolphin3

