# 2026-04-19

- 🔗 spaceword.org 🧩 2026-04-18 🏁 score 2168 ranked 31.9% 105/329 ⏱️ 22:05:36.016007
- 🔗 alfagok.diginaut.net 🧩 #533 🥳 36 ⏱️ 0:00:42.239733
- 🔗 alphaguess.com 🧩 #1000 🥳 26 ⏱️ 0:00:40.823921
- 🔗 dontwordle.com 🧩 #1426 🥳 6 ⏱️ 0:01:46.727929
- 🔗 dictionary.com hurdle 🧩 #1569 😦 19 ⏱️ 0:03:05.497135
- 🔗 Quordle Classic 🧩 #1546 🥳 score:22 ⏱️ 0:01:15.208011
- 🔗 Octordle Classic 🧩 #1546 🥳 score:58 ⏱️ 0:03:39.048228
- 🔗 squareword.org 🧩 #1539 🥳 7 ⏱️ 0:02:45.097215
- 🔗 cemantle.certitudes.org 🧩 #1476 🥳 64 ⏱️ 0:00:34.172589
- 🔗 cemantix.certitudes.org 🧩 #1509 🥳 31 ⏱️ 0:00:25.613833

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

















































# [spaceword.org](spaceword.org) 🧩 2026-04-18 🏁 score 2168 ranked 31.9% 105/329 ⏱️ 22:05:36.016007

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 105/329

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ K _ S H I V E R _   
      _ I _ U _ _ A X E _   
      _ R U E I N G _ L _   
      _ _ _ _ _ _ I _ Y _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #533 🥳 36 ⏱️ 0:00:42.239733

🤔 36 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+199605 [199605] lij         q0  ? ␅
    @+199605 [199605] lij         q1  ? after
    @+247687 [247687] op          q4  ? ␅
    @+247687 [247687] op          q5  ? after
    @+260572 [260572] pater       q8  ? ␅
    @+260572 [260572] pater       q9  ? after
    @+263627 [263627] pi          q12 ? ␅
    @+263627 [263627] pi          q13 ? after
    @+265305 [265305] plaatsing   q14 ? ␅
    @+265305 [265305] plaatsing   q15 ? after
    @+266161 [266161] platen      q16 ? ␅
    @+266161 [266161] platen      q17 ? after
    @+266356 [266356] plattelands q20 ? ␅
    @+266356 [266356] plattelands q21 ? after
    @+266469 [266469] plaît       q24 ? ␅
    @+266469 [266469] plaît       q25 ? after
    @+266508 [266508] pleeg       q26 ? ␅
    @+266508 [266508] pleeg       q27 ? after
    @+266542 [266542] pleegzus    q28 ? ␅
    @+266542 [266542] pleegzus    q29 ? after
    @+266550 [266550] pleet       q32 ? ␅
    @+266550 [266550] pleet       q33 ? after
    @+266555 [266555] plegen      q34 ? ␅
    @+266555 [266555] plegen      q35 ? it
    @+266555 [266555] plegen      done. it
    @+266562 [266562] pleidooien  q30 ? ␅
    @+266562 [266562] pleidooien  q31 ? before
    @+266581 [266581] pleister    q18 ? ␅
    @+266581 [266581] pleister    q19 ? before
    @+267023 [267023] plomp       q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1000 🥳 26 ⏱️ 0:00:40.823921

🤔 26 attempts
📜 1 sessions

    @        [     0] aa         
    @+1      [     1] aah        
    @+2      [     2] aahed      
    @+3      [     3] aahing     
    @+98216  [ 98216] mach       q0  ? ␅
    @+98216  [ 98216] mach       q1  ? after
    @+101133 [101133] medieval   q10 ? ␅
    @+101133 [101133] medieval   q11 ? after
    @+101847 [101847] merc       q14 ? ␅
    @+101847 [101847] merc       q15 ? after
    @+102029 [102029] mes        q16 ? ␅
    @+102029 [102029] mes        q17 ? after
    @+102158 [102158] mesothelia q20 ? ␅
    @+102158 [102158] mesothelia q21 ? after
    @+102178 [102178] mess       q24 ? ␅
    @+102178 [102178] mess       q25 ? it
    @+102178 [102178] mess       done. it
    @+102221 [102221] mestino    q22 ? ␅
    @+102221 [102221] mestino    q23 ? before
    @+102286 [102286] metal      q18 ? ␅
    @+102286 [102286] metal      q19 ? before
    @+102588 [102588] methyl     q12 ? ␅
    @+102588 [102588] methyl     q13 ? before
    @+104071 [104071] minor      q8  ? ␅
    @+104071 [104071] minor      q9  ? before
    @+109933 [109933] ne         q6  ? ␅
    @+109933 [109933] ne         q7  ? before
    @+122777 [122777] parr       q4  ? ␅
    @+122777 [122777] parr       q5  ? before
    @+147371 [147371] rhumb      q2  ? ␅
    @+147371 [147371] rhumb      q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1426 🥳 6 ⏱️ 0:01:46.727929

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MAMMA n n n n n remain:6571
    ⬜⬜⬜⬜⬜ tried:SEXES n n n n n remain:1391
    ⬜⬜⬜⬜⬜ tried:YUKKY n n n n n remain:505
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:145
    ⬜🟨⬜⬜⬜ tried:BOFFO n m n n n remain:19
    🟨⬜⬜🟨⬜ tried:INDOW m n n m n remain:1

    Undos used: 4

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1569 😦 19 ⏱️ 0:03:05.497135

📜 1 sessions
💰 score: 4780

    4/6
    RASED 🟨⬜⬜⬜⬜
    ORCIN ⬜🟩⬜🟨🟨
    BRING 🟩🟩🟩🟩⬜
    BRINK 🟩🟩🟩🟩🟩
    4/6
    BRINK ⬜⬜⬜⬜⬜
    DEALS ⬜⬜⬜⬜⬜
    HUMPY ⬜🟨⬜🟨🟩
    POUTY 🟩🟩🟩🟩🟩
    4/6
    POUTY ⬜⬜⬜⬜⬜
    LAIRD 🟨🟩⬜⬜⬜
    BALES ⬜🟩🟨🟨⬜
    EAGLE 🟩🟩🟩🟩🟩
    5/6
    EAGLE ⬜⬜⬜⬜⬜
    ROSIN 🟨🟩⬜⬜⬜
    DORTY ⬜🟩🟩⬜⬜
    MORPH 🟨🟩🟩⬜⬜
    FORUM 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜🟩🟨🟩🟩
    ????? 🟩🟩⬜🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1546 🥳 score:22 ⏱️ 0:01:15.208011

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. PEACE attempts:4 score:4
2. ERECT attempts:5 score:5
3. ASSAY attempts:7 score:7
4. SPILL attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1546 🥳 score:58 ⏱️ 0:03:39.048228

📜 2 sessions

Octordle Classic

1. ABLED attempts:6 score:6
2. CAGEY attempts:8 score:8
3. DOUGH attempts:7 score:7
4. GROWN attempts:9 score:9
5. SURLY attempts:10 score:10
6. COUGH attempts:8 score:11
7. PILOT attempts:4 score:4
8. MODEL attempts:3 score:3

# [squareword.org](squareword.org) 🧩 #1539 🥳 7 ⏱️ 0:02:45.097215

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P E S T S
    A L E R T
    P I P E R
    A D I E U
    L E A S T

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1476 🥳 64 ⏱️ 0:00:34.172589

🤔 65 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 8 chat prompts
🤖 8 dolphin3:latest replies
🥵  3 😎 10 🥶 49 🧊  2

     $1 #65 lock          100.00°C 🥳 1000‰ ~63 used:0 [62]  source:dolphin3
     $2 #36 deadbolt       39.14°C 🥵  988‰  ~1 used:1 [0]   source:dolphin3
     $3 #64 bolt           35.02°C 🥵  969‰  ~2 used:0 [1]   source:dolphin3
     $4 #33 door           31.77°C 🥵  922‰  ~3 used:1 [2]   source:dolphin3
     $5 #43 lift           28.09°C 😎  827‰  ~4 used:0 [3]   source:dolphin3
     $6 #42 knob           28.06°C 😎  824‰  ~5 used:0 [4]   source:dolphin3
     $7 #53 weatherstrip   26.70°C 😎  746‰  ~6 used:0 [5]   source:dolphin3
     $8 #41 hinge          26.27°C 😎  725‰  ~7 used:0 [6]   source:dolphin3
     $9 #49 seal           25.81°C 😎  679‰  ~8 used:0 [7]   source:dolphin3
    $10 #37 doorframe      25.22°C 😎  627‰  ~9 used:0 [8]   source:dolphin3
    $11 #30 garage         23.20°C 😎  358‰ ~11 used:2 [10]  source:dolphin3
    $12 #24 storage        23.00°C 😎  327‰ ~12 used:3 [11]  source:dolphin3
    $15 #47 ramp           21.14°C 🥶       ~15 used:0 [14]  source:dolphin3
    $64  #8 sunflower      -1.57°C 🧊       ~64 used:0 [63]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1509 🥳 31 ⏱️ 0:00:25.613833

🤔 32 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 5 chat prompts
🤖 5 dolphin3:latest replies
🥵  2 😎  2 🥶 21 🧊  6

     $1 #32 joli            100.00°C 🥳 1000‰ ~26 used:0 [25]  source:dolphin3
     $2 #14 rose             50.38°C 🥵  962‰  ~1 used:3 [0]   source:dolphin3
     $3  #4 fleur            49.18°C 🥵  952‰  ~2 used:3 [1]   source:dolphin3
     $4  #2 chapeau          38.91°C 😎  582‰  ~3 used:0 [2]   source:dolphin3
     $5 #17 rouge            37.33°C 😎  449‰  ~4 used:0 [3]   source:dolphin3
     $6 #13 pétale           29.07°C 🥶        ~5 used:0 [4]   source:dolphin3
     $7 #16 parfum           28.86°C 🥶        ~6 used:0 [5]   source:dolphin3
     $8 #11 bouquet          27.46°C 🥶        ~7 used:0 [6]   source:dolphin3
     $9  #3 chat             26.95°C 🥶        ~8 used:0 [7]   source:dolphin3
    $10 #24 rosier           24.40°C 🥶        ~9 used:0 [8]   source:dolphin3
    $11  #9 voiture          23.02°C 🥶       ~10 used:0 [9]   source:dolphin3
    $12  #1 bateau           19.39°C 🥶       ~11 used:0 [10]  source:dolphin3
    $13  #6 mouton           18.42°C 🥶       ~12 used:0 [11]  source:dolphin3
    $27 #23 plant            -0.52°C 🧊       ~27 used:0 [26]  source:dolphin3
