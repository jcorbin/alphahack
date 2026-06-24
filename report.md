# 2026-06-25

- 🔗 spaceword.org 🧩 2026-06-24 🏁 score 2168 ranked 38.3% 120/313 ⏱️ 0:08:37.759797
- 🔗 Sedecordle Classic 🧩 #1593 🥳 score:51 ⏱️ 0:10:42.506513
- 🔗 cemantix.certitudes.org 🧩 #1576 🥳 266 ⏱️ 0:08:40.459720
- 🔗 alfagok.diginaut.net 🧩 #600 🥳 32 ⏱️ 0:00:43.041528
- 🔗 alphaguess.com 🧩 #1067 🥳 30 ⏱️ 0:00:31.978269
- 🔗 dontwordle.com 🧩 #1493 🥳 6 ⏱️ 0:01:22.036305
- 🔗 dictionary.com hurdle 🧩 #1636 😦 20 ⏱️ 0:03:08.182886
- 🔗 cemantle.certitudes.org 🧩 #1543 🥳 173 ⏱️ 0:01:44.263154
- 🔗 squareword.org 🧩 #1606 🥳 8 ⏱️ 0:02:09.214325
- 🔗 Quordle Classic 🧩 #1613 🥳 score:29 ⏱️ 0:01:46.592399
- 🔗 Octordle Classic 🧩 #1613 🥳 score:50 ⏱️ 0:04:02.653873

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
















# [spaceword.org](spaceword.org) 🧩 2026-06-24 🏁 score 2168 ranked 38.3% 120/313 ⏱️ 0:08:37.759797

📜 2 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 120/313

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ F E M O R A L _ _   
      _ _ _ _ _ _ _ U _ _   
      _ Q _ M O T I V E _   
      _ I X O D I D _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1593 🥳 score:51 ⏱️ 0:10:42.506513

📜 3 sessions

Sedecordle Classic sedecordle.com

1. BRIBE attempts:9 score:0
2. GROAN attempts:10 score:9
3. PRUNE attempts:5 score:0
4. CHORD attempts:8 score:5
5. PINTO attempts:4 score:0
6. ACRID attempts:12 score:4
7. BLIMP attempts:13 score:1
8. BERRY attempts:14 score:3
9. TWIST attempts:15 score:1
10. VAPID attempts:16 score:5
11. BRUNT attempts:9 score:1
12. ARISE attempts:11 score:8
13. DINGO attempts:6 score:1
14. MINUS attempts:7 score:7
15. DOUGH attempts:6 score:0
16. SAUTE attempts:3 score:6

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1576 🥳 266 ⏱️ 0:08:40.459720

🤔 267 attempts
📜 1 sessions
🫧 22 chat sessions
⁉️ 113 chat prompts
🤖 113 dolphin3:latest replies
😱   1 🔥   2 🥵  16 😎  73 🥶 152 🧊  22

      $1 #267 rationnel         100.00°C 🥳 1000‰ ~245 used:0  [244]  source:dolphin3
      $2 #265 rationalité        75.99°C 😱  999‰   ~1 used:0  [0]    source:dolphin3
      $3 #145 raisonnement       58.91°C 🔥  995‰  ~13 used:42 [12]   source:dolphin3
      $4 #150 logique            56.42°C 🔥  991‰   ~8 used:32 [7]    source:dolphin3
      $5 #121 théorie            52.95°C 🥵  987‰  ~69 used:18 [68]   source:dolphin3
      $6 #106 postulat           52.81°C 🥵  986‰  ~68 used:15 [67]   source:dolphin3
      $7 #102 fondement          51.20°C 🥵  978‰  ~15 used:9  [14]   source:dolphin3
      $8 #215 déductif           50.94°C 🥵  976‰   ~9 used:4  [8]    source:dolphin3
      $9 #167 causal             50.78°C 🥵  974‰  ~10 used:4  [9]    source:dolphin3
     $10 #221 déterminisme       48.82°C 🥵  960‰  ~11 used:4  [10]   source:dolphin3
     $11 #173 sens               48.69°C 🥵  958‰   ~4 used:3  [3]    source:dolphin3
     $21  #31 intuitionniste     45.10°C 😎  895‰  ~92 used:26 [91]   source:dolphin3
     $94 #259 objectif           31.94°C 🥶        ~93 used:0  [92]   source:dolphin3
    $246 #141 assomption         -0.54°C 🧊       ~246 used:0  [245]  source:dolphin3

# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #600 🥳 32 ⏱️ 0:00:43.041528

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+786    [   786] aan        q12 ? ␅
    @+786    [   786] aan        q13 ? after
    @+2746   [  2746] aanlok     q16 ? ␅
    @+2746   [  2746] aanlok     q17 ? after
    @+3705   [  3705] aanstel    q18 ? ␅
    @+3705   [  3705] aanstel    q19 ? after
    @+4208   [  4208] aanvlogen  q20 ? ␅
    @+4208   [  4208] aanvlogen  q21 ? after
    @+4456   [  4456] aanwijzen  q22 ? ␅
    @+4456   [  4456] aanwijzen  q23 ? after
    @+4461   [  4461] aanwijzing q30 ? ␅
    @+4461   [  4461] aanwijzing q31 ? it
    @+4461   [  4461] aanwijzing done. it
    @+4481   [  4481] aanwipt    q28 ? ␅
    @+4481   [  4481] aanwipt    q29 ? before
    @+4512   [  4512] aanzei     q26 ? ␅
    @+4512   [  4512] aanzei     q27 ? before
    @+4570   [  4570] aanzuig    q24 ? ␅
    @+4570   [  4570] aanzuig    q25 ? before
    @+4710   [  4710] aardappels q14 ? ␅
    @+4710   [  4710] aardappels q15 ? before
    @+8648   [  8648] af         q10 ? ␅
    @+8648   [  8648] af         q11 ? before
    @+24887  [ 24887] bad        q8  ? ␅
    @+24887  [ 24887] bad        q9  ? before
    @+49816  [ 49816] boks       q4  ? ␅
    @+49816  [ 49816] boks       q5  ? before
    @+99700  [ 99700] ex         q2  ? ␅
    @+99700  [ 99700] ex         q3  ? before
    @+199557 [199557] lij        q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1067 🥳 30 ⏱️ 0:00:31.978269

🤔 30 attempts
📜 1 sessions

    @       [    0] aa        
    @+47380 [47380] dis       q4  ? ␅
    @+47380 [47380] dis       q5  ? after
    @+60081 [60081] face      q8  ? ␅
    @+60081 [60081] face      q9  ? after
    @+63237 [63237] flag      q12 ? ␅
    @+63237 [63237] flag      q13 ? after
    @+64034 [64034] flood     q16 ? ␅
    @+64034 [64034] flood     q17 ? after
    @+64194 [64194] flour     q20 ? ␅
    @+64194 [64194] flour     q21 ? after
    @+64209 [64209] flout     q26 ? ␅
    @+64209 [64209] flout     q27 ? after
    @+64215 [64215] flow      q28 ? ␅
    @+64215 [64215] flow      q29 ? it
    @+64215 [64215] flow      done. it
    @+64226 [64226] flower    q24 ? ␅
    @+64226 [64226] flower    q25 ? before
    @+64280 [64280] flue      q22 ? ␅
    @+64280 [64280] flue      q23 ? before
    @+64377 [64377] fluor     q18 ? ␅
    @+64377 [64377] fluor     q19 ? before
    @+64834 [64834] foment    q14 ? ␅
    @+64834 [64834] foment    q15 ? before
    @+66437 [66437] french    q10 ? ␅
    @+66437 [66437] french    q11 ? before
    @+72797 [72797] gremolata q6  ? ␅
    @+72797 [72797] gremolata q7  ? before
    @+98214 [98214] mach      q1  ? after
    @+98214 [98214] mach      q2  ? ␅
    @+98214 [98214] mach      q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1493 🥳 6 ⏱️ 0:01:22.036305

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:ADDAX n n n n n remain:6032
    ⬜⬜⬜⬜⬜ tried:COOCH n n n n n remain:2625
    ⬜⬜⬜⬜⬜ tried:KININ n n n n n remain:972
    ⬜⬜⬜⬜⬜ tried:SLYLY n n n n n remain:126
    ⬜🟨⬜⬜⬜ tried:JUGUM n m n n n remain:7
    🟩⬜⬜🟩🟩 tried:UPPER Y n n Y Y remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1636 😦 20 ⏱️ 0:03:08.182886

📜 1 sessions
💰 score: 4680

    5/6
    NAPES ⬜🟨⬜⬜⬜
    ULTRA ⬜⬜⬜🟩🟨
    CHARD ⬜⬜🟩🟩🟨
    DWARF 🟩⬜🟩🟩⬜
    DIARY 🟩🟩🟩🟩🟩
    4/6
    DIARY ⬜⬜⬜🟩🟩
    LOURY ⬜⬜⬜🟩🟩
    ENTRY 🟨⬜🟩🟩🟩
    RETRY 🟩🟩🟩🟩🟩
    6/6
    RETRY 🟨⬜⬜⬜⬜
    ARSON 🟨🟨⬜⬜⬜
    CHAIR 🟨🟨🟨⬜🟨
    LARCH ⬜🟩🟩🟩🟩
    MARCH ⬜🟩🟩🟩🟩
    PARCH 🟩🟩🟩🟩🟩
    3/6
    PARCH ⬜🟨⬜⬜⬜
    LEADS ⬜🟨🟩🟩⬜
    EVADE 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜🟩⬜🟩🟩
    ????? 🟩🟩⬜🟩🟩

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1543 🥳 173 ⏱️ 0:01:44.263154

🤔 174 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 28 chat prompts
🤖 28 dolphin3:latest replies
😱   1 🔥   1 🥵  10 😎  20 🥶 133 🧊   8

      $1 #174 beginner        100.00°C 🥳 1000‰ ~166 used:0  [165]  source:dolphin3
      $2 #169 novice           62.76°C 😱  999‰   ~1 used:2  [0]    source:dolphin3
      $3  #61 belay            41.89°C 🔥  991‰   ~9 used:26 [8]    source:dolphin3
      $4 #170 skill            40.64°C 🥵  989‰   ~2 used:0  [1]    source:dolphin3
      $5 #136 skiing           39.82°C 🥵  987‰  ~10 used:4  [9]    source:dolphin3
      $6 #154 instructor       38.21°C 🥵  978‰   ~3 used:1  [2]    source:dolphin3
      $7 #143 ski              35.28°C 🥵  958‰   ~8 used:2  [7]    source:dolphin3
      $8 #172 teach            34.97°C 🥵  956‰   ~4 used:0  [3]    source:dolphin3
      $9 #159 snowboard        34.79°C 🥵  950‰   ~5 used:0  [4]    source:dolphin3
     $10  #37 mountaineering   34.61°C 🥵  948‰  ~28 used:16 [27]   source:dolphin3
     $11 #145 snowboarding     33.75°C 🥵  935‰   ~6 used:0  [5]    source:dolphin3
     $14  #62 bike             31.93°C 😎  889‰  ~29 used:2  [28]   source:dolphin3
     $34  #30 rope             22.33°C 🥶        ~34 used:0  [33]   source:dolphin3
    $167   #3 chair            -0.09°C 🧊       ~167 used:0  [166]  source:dolphin3

# [squareword.org](squareword.org) 🧩 #1606 🥳 8 ⏱️ 0:02:09.214325

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟨 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C R A G S
    L E M O N
    A C U T E
    W A S T E
    S P E A R

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1613 🥳 score:29 ⏱️ 0:01:46.592399

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SHELF attempts:7 score:7
2. TAWNY attempts:5 score:5
3. HYPER attempts:8 score:8
4. SOLVE attempts:9 score:9

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1613 🥳 score:50 ⏱️ 0:04:02.653873

📜 1 sessions

Octordle Classic

1. MUMMY attempts:10 score:10
2. ALPHA attempts:3 score:3
3. CLIFF attempts:5 score:5
4. FLORA attempts:2 score:2
5. MOTTO attempts:9 score:9
6. GLADE attempts:6 score:6
7. BEADY attempts:7 score:7
8. SHYLY attempts:8 score:8
