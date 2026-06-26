# 2026-06-27

- 🔗 spaceword.org 🧩 2026-06-26 🏁 score 2173 ranked 10.4% 30/288 ⏱️ 1:42:18.738343
- 🔗 alfagok.diginaut.net 🧩 #602 🥳 24 ⏱️ 0:00:33.891607
- 🔗 alphaguess.com 🧩 #1069 🥳 22 ⏱️ 0:00:35.309982
- 🔗 dontwordle.com 🧩 #1495 🤷 6 ⏱️ 0:01:44.020625
- 🔗 dictionary.com hurdle 🧩 #1638 🥳 19 ⏱️ 0:02:57.262318
- 🔗 Quordle Classic 🧩 #1615 🥳 score:21 ⏱️ 0:01:18.473495
- 🔗 Octordle Classic 🧩 #1615 🥳 score:65 ⏱️ 0:04:09.588630
- 🔗 Sedecordle Classic 🧩 #1595 🥳 score:40 ⏱️ 0:12:26.825005
- 🔗 squareword.org 🧩 #1608 🥳 7 ⏱️ 0:02:04.075348
- 🔗 cemantle.certitudes.org 🧩 #1545 🥳 213 ⏱️ 0:02:38.869133
- 🔗 cemantix.certitudes.org 🧩 #1578 🥳 54 ⏱️ 0:01:06.421685

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


















# [spaceword.org](spaceword.org) 🧩 2026-06-26 🏁 score 2173 ranked 10.4% 30/288 ⏱️ 1:42:18.738343

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 30/288

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ V _ S _ S _ R _ E   
      _ E _ A P O G E A N   
      _ E Q U I N O X _ G   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #602 🥳 24 ⏱️ 0:00:33.891607

🤔 24 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+49816  [ 49816] boks      q4  ? ␅
    @+49816  [ 49816] boks      q5  ? after
    @+74719  [ 74719] dc        q6  ? ␅
    @+74719  [ 74719] dc        q7  ? after
    @+77691  [ 77691] der       q12 ? ␅
    @+77691  [ 77691] der       q13 ? after
    @+78434  [ 78434] detentie  q16 ? ␅
    @+78434  [ 78434] detentie  q17 ? after
    @+78578  [ 78578] deur      q22 ? ␅
    @+78578  [ 78578] deur      q23 ? it
    @+78578  [ 78578] deur      done. it
    @+78815  [ 78815] dia       q20 ? ␅
    @+78815  [ 78815] dia       q21 ? before
    @+79193  [ 79193] dicht     q14 ? ␅
    @+79193  [ 79193] dicht     q15 ? before
    @+80851  [ 80851] dijk      q10 ? ␅
    @+80851  [ 80851] dijk      q11 ? before
    @+87177  [ 87177] draag     q8  ? ␅
    @+87177  [ 87177] draag     q9  ? before
    @+99699  [ 99699] ex        q2  ? ␅
    @+99699  [ 99699] ex        q3  ? before
    @+199556 [199556] lij       q0  ? ␅
    @+199556 [199556] lij       q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1069 🥳 22 ⏱️ 0:00:35.309982

🤔 22 attempts
📜 1 sessions

    @        [     0] aa      
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98214  [ 98214] mach    q0  ? ␅
    @+98214  [ 98214] mach    q1  ? after
    @+147364 [147364] rhotic  q2  ? ␅
    @+147364 [147364] rhotic  q3  ? after
    @+153313 [153313] sea     q8  ? ␅
    @+153313 [153313] sea     q9  ? after
    @+156349 [156349] ship    q10 ? ␅
    @+156349 [156349] ship    q11 ? after
    @+157877 [157877] sim     q12 ? ␅
    @+157877 [157877] sim     q13 ? after
    @+158527 [158527] ski     q14 ? ␅
    @+158527 [158527] ski     q15 ? after
    @+159001 [159001] slaps   q16 ? ␅
    @+159001 [159001] slaps   q17 ? after
    @+159238 [159238] slicken q18 ? ␅
    @+159238 [159238] slicken q19 ? after
    @+159336 [159336] slip    q20 ? ␅
    @+159336 [159336] slip    q21 ? it
    @+159336 [159336] slip    done. it
    @+159481 [159481] slop    q6  ? ␅
    @+159481 [159481] slop    q7  ? before
    @+171634 [171634] ta      q4  ? ␅
    @+171634 [171634] ta      q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1495 🤷 6 ⏱️ 0:01:44.020625

📜 1 sessions
💰 score: 0

ELIMINATED
> Well technically I didn't Wordle!

    ⬜⬜⬜⬜⬜ tried:WOWEE n n n n n remain:4227
    ⬜⬜⬜⬜⬜ tried:AUDAD n n n n n remain:723
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:283
    🟩⬜⬜⬜⬜ tried:SYNCS Y n n n n remain:9
    🟩⬜🟨⬜⬜ tried:SKIMP Y n Y n n remain:1
    ⬛⬛⬛⬛⬛ tried:????? remain:0

    Undos used: 5

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1638 🥳 19 ⏱️ 0:02:57.262318

📜 1 sessions
💰 score: 9700

    4/6
    YEAST ⬜🟨⬜⬜⬜
    BORED ⬜⬜⬜🟨🟨
    NUDIE ⬜⬜🟨🟨🟩
    GLIDE 🟩🟩🟩🟩🟩
    6/6
    GLIDE 🟨🟩🟩⬜⬜
    ALIGN ⬜🟩🟩🟨🟨
    BLING ⬜🟩🟩🟩🟩
    CLING ⬜🟩🟩🟩🟩
    FLING ⬜🟩🟩🟩🟩
    SLING 🟩🟩🟩🟩🟩
    4/6
    SLING ⬜🟨⬜⬜⬜
    LAYER 🟨🟨⬜⬜⬜
    AFOUL 🟩⬜🟩⬜🟩
    ATOLL 🟩🟩🟩🟩🟩
    4/6
    ATOLL ⬜🟨⬜⬜⬜
    UNITS 🟨🟨⬜🟩⬜
    PUNTY ⬜🟩🟨🟩🟩
    NUTTY 🟩🟩🟩🟩🟩
    Final 1/2
    MAUVE 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1615 🥳 score:21 ⏱️ 0:01:18.473495

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. PRINT attempts:5 score:5
2. MARRY attempts:6 score:6
3. SADLY attempts:3 score:3
4. BICEP attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1615 🥳 score:65 ⏱️ 0:04:09.588630

📜 1 sessions

Octordle Classic

1. FIBRE attempts:8 score:8
2. BOULE attempts:9 score:9
3. SLANG attempts:10 score:10
4. CLEAN attempts:5 score:5
5. SLOSH attempts:4 score:4
6. CROCK attempts:12 score:12
7. LATER attempts:6 score:6
8. OTTER attempts:11 score:11

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1595 🥳 score:40 ⏱️ 0:12:26.825005

📜 3 sessions

Sedecordle Classic sedecordle.com

1. RURAL attempts:17 score:1
2. BACON attempts:18 score:7
3. WASTE attempts:7 score:0
4. ALOUD attempts:4 score:7
5. OLIVE attempts:10 score:1
6. MADLY attempts:16 score:0
7. COURT attempts:5 score:0
8. GOLLY attempts:13 score:5
9. ROCKY attempts:11 score:1
10. GAWKY attempts:12 score:1
11. SMIRK attempts:14 score:1
12. GRAVY attempts:15 score:4
13. SPOKE attempts:9 score:0
14. BUSED attempts:19 score:9
15. SUITE attempts:3 score:0
16. PHASE attempts:8 score:3

# [squareword.org](squareword.org) 🧩 #1608 🥳 7 ⏱️ 0:02:04.075348

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C H E S T
    L A T T E
    A S H E N
    S T E N T
    H E R O S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1545 🥳 213 ⏱️ 0:02:38.869133

🤔 214 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 41 chat prompts
🤖 41 dolphin3:latest replies
🔥   4 🥵   4 😎  14 🥶 180 🧊  11

      $1 #214 adventure         100.00°C 🥳 1000‰ ~203 used:0  [202]  source:dolphin3
      $2 #193 excursion          56.18°C 🔥  998‰   ~3 used:5  [2]    source:dolphin3
      $3 #185 journey            50.75°C 🔥  996‰   ~4 used:6  [3]    source:dolphin3
      $4 #208 odyssey            49.52°C 🔥  995‰   ~1 used:0  [0]    source:dolphin3
      $5 #209 expedition         49.48°C 🔥  994‰   ~2 used:0  [1]    source:dolphin3
      $6 #191 trek               43.78°C 🥵  975‰   ~8 used:2  [7]    source:dolphin3
      $7 #204 voyage             43.53°C 🥵  973‰   ~5 used:0  [4]    source:dolphin3
      $8 #213 wanderlust         43.19°C 🥵  971‰   ~6 used:0  [5]    source:dolphin3
      $9 #200 peregrination      39.37°C 🥵  944‰   ~7 used:0  [6]    source:dolphin3
     $10 #207 explorative        35.02°C 😎  868‰   ~9 used:0  [8]    source:dolphin3
     $11 #179 explore            34.52°C 😎  850‰  ~20 used:2  [19]   source:dolphin3
     $12 #206 circumnavigation   34.49°C 😎  848‰  ~10 used:0  [9]    source:dolphin3
     $24 #183 wander             24.90°C 🥶        ~30 used:0  [29]   source:dolphin3
    $204   #7 quantum            -0.38°C 🧊       ~204 used:0  [203]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1578 🥳 54 ⏱️ 0:01:06.421685

🤔 55 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 19 chat prompts
🤖 19 dolphin3:latest replies
😱  1 🔥  1 🥵  2 😎 11 🥶 21 🧊 18

     $1 #55 gestionnaire          100.00°C 🥳 1000‰ ~37 used:0 [36]  source:dolphin3
     $2 #51 gestion                66.16°C 😱  999‰  ~1 used:2 [0]   source:dolphin3
     $3 #52 administration         44.13°C 🔥  990‰  ~2 used:0 [1]   source:dolphin3
     $4 #49 coordination           34.15°C 🥵  906‰  ~4 used:4 [3]   source:dolphin3
     $5 #44 élaboration            34.05°C 🥵  904‰  ~3 used:3 [2]   source:dolphin3
     $6 #39 optimisation           32.64°C 😎  873‰  ~5 used:1 [4]   source:dolphin3
     $7 #29 amélioration           30.55°C 😎  794‰ ~14 used:5 [13]  source:dolphin3
     $8 #24 développement          28.62°C 😎  688‰ ~15 used:5 [14]  source:dolphin3
     $9 #53 analyse                27.07°C 😎  581‰  ~6 used:0 [5]   source:dolphin3
    $10 #28 évolution              26.05°C 😎  505‰ ~13 used:4 [12]  source:dolphin3
    $11 #54 direction              26.00°C 😎  499‰  ~7 used:0 [6]   source:dolphin3
    $12 #41 rationalisation        25.03°C 😎  411‰  ~8 used:0 [7]   source:dolphin3
    $17 #33 diversification        20.90°C 🥶       ~18 used:0 [17]  source:dolphin3
    $38 #30 maturité               -1.83°C 🧊       ~38 used:0 [37]  source:dolphin3
