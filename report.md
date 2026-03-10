# 2026-03-11

- 🔗 spaceword.org 🧩 2026-03-10 🏁 score 2172 ranked 23.2% 83/358 ⏱️ 2:23:23.152821
- 🔗 alfagok.diginaut.net 🧩 #494 🥳 42 ⏱️ 0:00:46.775507
- 🔗 alphaguess.com 🧩 #961 🥳 30 ⏱️ 0:01:33.488119
- 🔗 dontwordle.com 🧩 #1387 🥳 6 ⏱️ 0:02:15.352157
- 🔗 dictionary.com hurdle 🧩 #1530 🥳 17 ⏱️ 0:03:40.457439
- 🔗 Quordle Classic 🧩 #1507 🥳 score:20 ⏱️ 0:02:15.448548
- 🔗 Octordle Classic 🧩 #1507 😦 score:68 ⏱️ 0:05:07.938535
- 🔗 squareword.org 🧩 #1500 🥳 9 ⏱️ 0:02:49.777115
- 🔗 cemantle.certitudes.org 🧩 #1437 🥳 38 ⏱️ 0:00:24.962073
- 🔗 cemantix.certitudes.org 🧩 #1470 🥳 99 ⏱️ 0:01:47.164021

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










# [spaceword.org](spaceword.org) 🧩 2026-03-10 🏁 score 2172 ranked 23.2% 83/358 ⏱️ 2:23:23.152821

📜 3 sessions
- tiles: 21/21
- score: 2172 bonus: +72
- rank: 83/358

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ W _ R _ _ A _   
      _ _ K I _ O _ _ G _   
      _ _ I S O T O P E _   
      _ _ R E F I X E D _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #494 🥳 42 ⏱️ 0:00:46.775507

🤔 42 attempts
📜 1 sessions

    @        [     0] &-teken         
    @+199609 [199609] lij             q0  ? ␅
    @+199609 [199609] lij             q1  ? after
    @+199609 [199609] lij             q2  ? ␅
    @+199609 [199609] lij             q3  ? after
    @+299483 [299483] schro           q4  ? ␅
    @+299483 [299483] schro           q5  ? after
    @+349467 [349467] vakantie        q6  ? ␅
    @+349467 [349467] vakantie        q7  ? after
    @+353035 [353035] ver             q10 ? ␅
    @+353035 [353035] ver             q11 ? after
    @+358327 [358327] verluierde      q14 ? ␅
    @+358327 [358327] verluierde      q15 ? after
    @+358475 [358475] vermeesterd     q26 ? ␅
    @+358475 [358475] vermeesterd     q27 ? after
    @+358492 [358492] vermeld         q32 ? ␅
    @+358492 [358492] vermeld         q33 ? after
    @+358495 [358495] vermelde        q36 ? ␅
    @+358495 [358495] vermelde        q37 ? after
    @+358496 [358496] vermelden       q40 ? ␅
    @+358496 [358496] vermelden       q41 ? it
    @+358496 [358496] vermelden       done. it
    @+358497 [358497] vermeldende     q38 ? ␅
    @+358497 [358497] vermeldende     q39 ? before
    @+358498 [358498] vermeldenswaard q34 ? ␅
    @+358498 [358498] vermeldenswaard q35 ? before
    @+358509 [358509] vermemelen      q30 ? ␅
    @+358509 [358509] vermemelen      q31 ? before
    @+358543 [358543] vermetel        q28 ? ␅
    @+358543 [358543] vermetel        q29 ? before
    @+358623 [358623] vermoei         q23 ? before

# [alphaguess.com](alphaguess.com) 🧩 #961 🥳 30 ⏱️ 0:01:33.488119

🤔 30 attempts
📜 1 sessions

    @       [    0] aa       
    @+47381 [47381] dis      q4  ? ␅
    @+47381 [47381] dis      q5  ? after
    @+72800 [72800] gremmy   q6  ? ␅
    @+72800 [72800] gremmy   q7  ? after
    @+75956 [75956] haw      q12 ? ␅
    @+75956 [75956] haw      q13 ? after
    @+76083 [76083] head     q20 ? ␅
    @+76083 [76083] head     q21 ? after
    @+76187 [76187] headrail q22 ? ␅
    @+76187 [76187] headrail q23 ? after
    @+76239 [76239] headwork q24 ? ␅
    @+76239 [76239] headwork q25 ? after
    @+76264 [76264] heap     q26 ? ␅
    @+76264 [76264] heap     q27 ? after
    @+76271 [76271] hear     q28 ? ␅
    @+76271 [76271] hear     q29 ? it
    @+76271 [76271] hear     done. it
    @+76291 [76291] heart    q18 ? ␅
    @+76291 [76291] heart    q19 ? before
    @+76699 [76699] helio    q16 ? ␅
    @+76699 [76699] helio    q17 ? before
    @+77500 [77500] hetero   q14 ? ␅
    @+77500 [77500] hetero   q15 ? before
    @+79132 [79132] hood     q10 ? ␅
    @+79132 [79132] hood     q11 ? before
    @+85504 [85504] ins      q8  ? ␅
    @+85504 [85504] ins      q9  ? before
    @+98218 [98218] mach     q1  ? after
    @+98218 [98218] mach     q2  ? ␅
    @+98218 [98218] mach     q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1387 🥳 6 ⏱️ 0:02:15.352157

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:YUMMY n n n n n remain:7572
    ⬜⬜⬜⬜⬜ tried:JAVAS n n n n n remain:1691
    ⬜⬜⬜⬜⬜ tried:RIGID n n n n n remain:286
    ⬜⬜⬜⬜🟨 tried:PHPHT n n n n m remain:39
    ⬜🟩⬜🟨⬜ tried:CONTO n Y n m n remain:3
    ⬜🟩🟨🟩🟩 tried:BOTEL n Y m Y Y remain:1

    Undos used: 3

      1 words remaining
    x 6 unused letters
    = 6 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1530 🥳 17 ⏱️ 0:03:40.457439

📜 1 sessions
💰 score: 9900

    4/6
    TASER 🟩🟩⬜⬜⬜
    TALON 🟩🟩🟩⬜⬜
    TALKY 🟩🟩🟩⬜🟩
    TALLY 🟩🟩🟩🟩🟩
    2/6
    TALLY ⬜🟩⬜⬜🟩
    HARDY 🟩🟩🟩🟩🟩
    5/6
    HARDY 🟨⬜⬜⬜⬜
    SOUTH ⬜🟩⬜🟩🟩
    MONTH ⬜🟩⬜🟩🟩
    BOOTH ⬜🟩🟩🟩🟩
    TOOTH 🟩🟩🟩🟩🟩
    4/6
    TOOTH ⬜⬜⬜⬜⬜
    SANER ⬜🟨⬜⬜🟨
    DIARY ⬜⬜🟨🟩⬜
    UMBRA 🟩🟩🟩🟩🟩
    Final 2/2
    RELIC 🟨🟨🟩🟨⬜
    FILER 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1507 🥳 score:20 ⏱️ 0:02:15.448548

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. BOUGH attempts:4 score:4
2. TOTEM attempts:6 score:6
3. NEIGH attempts:3 score:3
4. PENAL attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1507 😦 score:68 ⏱️ 0:05:07.938535

📜 1 sessions

Octordle Classic

1. TAMER attempts:7 score:7
2. ODDLY attempts:10 score:10
3. DREAD attempts:12 score:12
4. _ONIC -ABDEGHLMPRSTUXY attempts:13 score:-1
5. EXTRA attempts:5 score:5
6. SCORE attempts:9 score:9
7. SHONE attempts:8 score:8
8. RIGHT attempts:3 score:3

# [squareword.org](squareword.org) 🧩 #1500 🥳 9 ⏱️ 0:02:49.777115

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟩 🟨 🟩
    🟩 🟩 🟨 🟩 🟩
    🟩 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    G R A M S
    R E L I C
    A N I M E
    S E V E N
    S W E D E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1437 🥳 38 ⏱️ 0:00:24.962073

🤔 39 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 8 chat prompts
🤖 8 dolphin3:latest replies
🔥  1 🥵  1 😎  4 🥶 30 🧊  2

     $1 #39 shelf           100.00°C 🥳 1000‰ ~37 used:0 [36]  source:dolphin3
     $2 #38 bookshelf        44.53°C 😱  999‰  ~1 used:1 [0]   source:dolphin3
     $3 #36 table            35.97°C 🥵  985‰  ~2 used:2 [1]   source:dolphin3
     $4 #15 catalog          26.68°C 😎  834‰  ~6 used:3 [5]   source:dolphin3
     $5 #34 jacket           23.14°C 😎  508‰  ~3 used:1 [2]   source:dolphin3
     $6 #22 hardcover        22.18°C 😎  339‰  ~5 used:2 [4]   source:dolphin3
     $7 #24 paperback        21.23°C 😎  147‰  ~4 used:1 [3]   source:dolphin3
     $8 #30 contents         20.45°C 🥶        ~9 used:0 [8]   source:dolphin3
     $9 #28 bibliography     20.41°C 🥶       ~10 used:0 [9]   source:dolphin3
    $10 #11 library          18.54°C 🥶        ~7 used:3 [6]   source:dolphin3
    $11 #20 format           18.17°C 🥶       ~11 used:0 [10]  source:dolphin3
    $12 #33 index            16.80°C 🥶       ~12 used:0 [11]  source:dolphin3
    $13 #37 volume           16.22°C 🥶       ~13 used:0 [12]  source:dolphin3
    $38 #13 study            -0.49°C 🧊       ~38 used:0 [37]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1470 🥳 99 ⏱️ 0:01:47.164021

🤔 100 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 33 chat prompts
🤖 33 dolphin3:latest replies
😱  1 🔥  3 🥵  7 😎 16 🥶 62 🧊 10

      $1 #100 gain               100.00°C 🥳 1000‰  ~90 used:0  [89]   source:dolphin3
      $2  #98 avantage            51.73°C 😱  999‰   ~1 used:0  [0]    source:dolphin3
      $3  #96 rendement           48.67°C 🔥  998‰   ~4 used:2  [3]    source:dolphin3
      $4  #97 productivité        47.61°C 🔥  997‰   ~2 used:0  [1]    source:dolphin3
      $5  #95 performance         43.20°C 🔥  990‰   ~3 used:0  [2]    source:dolphin3
      $6  #80 efficacité          40.43°C 🥵  984‰   ~8 used:8  [7]    source:dolphin3
      $7  #93 réduire             39.20°C 🥵  976‰   ~5 used:0  [4]    source:dolphin3
      $8  #54 rapide              35.94°C 🥵  962‰  ~25 used:19 [24]   source:dolphin3
      $9  #34 puissance           32.58°C 🥵  926‰  ~24 used:15 [23]   source:dolphin3
     $10  #82 performant          32.17°C 🥵  915‰   ~7 used:3  [6]    source:dolphin3
     $11  #36 vitesse             31.95°C 🥵  909‰  ~23 used:11 [22]   source:dolphin3
     $13  #26 accélération        31.22°C 😎  890‰  ~27 used:3  [26]   source:dolphin3
     $29  #30 démarrage           20.85°C 🥶        ~32 used:0  [31]   source:dolphin3
     $91  #22 minibus             -0.29°C 🧊        ~91 used:0  [90]   source:dolphin3
