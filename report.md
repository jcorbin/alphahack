# 2026-02-18

- 🔗 spaceword.org 🧩 2026-02-17 😦 incomplete score 2164 ⏱️ 14:57:02.567886
- 🔗 alfagok.diginaut.net 🧩 #473 🥳 20 ⏱️ 0:00:31.175225
- 🔗 alphaguess.com 🧩 #940 🥳 39 ⏱️ 0:00:36.647952
- 🔗 dontwordle.com 🧩 #1366 🥳 6 ⏱️ 0:01:45.880068
- 🔗 dictionary.com hurdle 🧩 #1509 🥳 17 ⏱️ 0:03:01.672524
- 🔗 Quordle Classic 🧩 #1486 🥳 score:17 ⏱️ 0:01:31.278952
- 🔗 Octordle Classic 🧩 #1486 🥳 score:63 ⏱️ 0:05:06.274660
- 🔗 squareword.org 🧩 #1479 🥳 7 ⏱️ 0:02:11.030386
- 🔗 cemantle.certitudes.org 🧩 #1416 🥳 380 ⏱️ 0:06:01.714176
- 🔗 cemantix.certitudes.org 🧩 #1449 🥳 143 ⏱️ 0:01:55.078892
- 🔗 Quordle Rescue 🧩 #100 🥳 score:27 ⏱️ 0:01:59.801834

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


































# [spaceword.org](spaceword.org) 🧩 2026-02-17 😦 incomplete score 2164 ⏱️ 14:57:02.567886

📜 2 sessions
- tiles: 21/21
- score: 2164 bonus: +64

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ V U G _ _ _   
      _ _ _ _ _ _ U _ _ _   
      _ _ _ _ _ K I _ _ _   
      _ _ _ _ O A T _ _ _   
      _ _ _ _ _ M A _ _ _   
      _ _ _ D O O R _ _ _   
      _ _ _ _ _ T _ _ _ _   
      _ _ _ P A I N _ _ _   
      _ _ _ _ _ Q _ _ _ _   

# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #473 🥳 20 ⏱️ 0:00:31.175225

🤔 20 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+99742  [ 99742] ex         q2  ? ␅
    @+99742  [ 99742] ex         q3  ? after
    @+149438 [149438] huis       q4  ? ␅
    @+149438 [149438] huis       q5  ? after
    @+174545 [174545] kind       q6  ? ␅
    @+174545 [174545] kind       q7  ? after
    @+187181 [187181] krontjongs q8  ? ␅
    @+187181 [187181] krontjongs q9  ? after
    @+193482 [193482] lavendel   q10 ? ␅
    @+193482 [193482] lavendel   q11 ? after
    @+196498 [196498] les        q12 ? ␅
    @+196498 [196498] les        q13 ? after
    @+196736 [196736] letter     q18 ? ␅
    @+196736 [196736] letter     q19 ? it
    @+196736 [196736] letter     done. it
    @+197091 [197091] levens     q16 ? ␅
    @+197091 [197091] levens     q17 ? before
    @+198102 [198102] lichaam    q14 ? ␅
    @+198102 [198102] lichaam    q15 ? before
    @+199817 [199817] lijm       q0  ? ␅
    @+199817 [199817] lijm       q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #940 🥳 39 ⏱️ 0:00:36.647952

🤔 39 attempts
📜 2 sessions

    @       [    0] aa       
    @+47381 [47381] dis      q2  ? ␅
    @+47381 [47381] dis      q3  ? after
    @+72800 [72800] gremmy   q4  ? ␅
    @+72800 [72800] gremmy   q5  ? after
    @+85504 [85504] ins      q6  ? ␅
    @+85504 [85504] ins      q7  ? after
    @+88664 [88664] jacks    q10 ? ␅
    @+88664 [88664] jacks    q11 ? after
    @+90254 [90254] kaf      q12 ? ␅
    @+90254 [90254] kaf      q13 ? after
    @+90645 [90645] keen     q16 ? ␅
    @+90645 [90645] keen     q17 ? after
    @+90848 [90848] kern     q20 ? ␅
    @+90848 [90848] kern     q21 ? after
    @+90893 [90893] ketch    q24 ? ␅
    @+90893 [90893] ketch    q25 ? after
    @+90895 [90895] ketchup  q28 ? ␅
    @+90895 [90895] ketchup  q29 ? 🧩 Puzzle #940
    @+90895 [90895] ketchup  q37 ? ␅
    @+90895 [90895] ketchup  q38 ? it
    @+90895 [90895] ketchup  done. it
    @+90898 [90898] ketchups q30 ? ␅
    @+90898 [90898] ketchups q31 ? 🤔 14 guesses
    @+90898 [90898] ketchups q32 ? ␅
    @+90898 [90898] ketchups q33 ? ⏱️ 21s
    @+90898 [90898] ketchups q34 ? ␅
    @+90898 [90898] ketchups q35 ? 🔗 alphaguess.com/940
    @+90898 [90898] ketchups q36 ? ␅
    @+90902 [90902] keto     q26 ? ␅
    @+90902 [90902] keto     q27 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1366 🥳 6 ⏱️ 0:01:45.880068

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:SEXES n n n n n remain:3586
    ⬜⬜⬜⬜⬜ tried:ZIZIT n n n n n remain:1660
    ⬜⬜⬜⬜⬜ tried:BUBBY n n n n n remain:579
    ⬜🟨⬜⬜⬜ tried:DOGGO n m n n n remain:78
    ⬜⬜🟨⬜⬜ tried:KNOWN n n m n n remain:18
    ⬜🟩⬜🟩🟨 tried:HAVOC n Y n Y m remain:2

    Undos used: 5

      2 words remaining
    x 7 unused letters
    = 14 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1509 🥳 17 ⏱️ 0:03:01.672524

📜 1 sessions
💰 score: 9900

    2/6
    STARE ⬜🟩🟨⬜🟩
    ATONE 🟩🟩🟩🟩🟩
    5/6
    ATONE 🟨⬜⬜⬜🟨
    WEARS ⬜🟩🟨🟨⬜
    RELAY 🟩🟩⬜🟩⬜
    RECAP 🟩🟩⬜🟩⬜
    REHAB 🟩🟩🟩🟩🟩
    4/6
    REHAB ⬜⬜🟨⬜⬜
    DITCH ⬜🟨⬜⬜🟨
    WHINY ⬜🟩🟩🟩🟩
    SHINY 🟩🟩🟩🟩🟩
    5/6
    SHINY 🟨⬜🟨⬜⬜
    ISLED 🟨🟨⬜⬜⬜
    RIFTS ⬜🟨⬜⬜🟩
    PUBIS ⬜⬜🟨🟩🟩
    BASIS 🟩🟩🟩🟩🟩
    Final 1/2
    INTRO 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1486 🥳 score:17 ⏱️ 0:01:31.278952

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. SNARL attempts:7 score:7
2. SOAPY attempts:5 score:5
3. RUSTY attempts:2 score:2
4. SERUM attempts:3 score:3

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1486 🥳 score:63 ⏱️ 0:05:06.274660

📜 1 sessions

Octordle Classic

1. GRUFF attempts:8 score:8
2. STOOD attempts:5 score:5
3. MUMMY attempts:9 score:10
4. DEBUG attempts:4 score:4
5. OZONE attempts:6 score:6
6. TROOP attempts:7 score:7
7. MODEL attempts:10 score:11
8. POPPY attempts:11 score:12

# [squareword.org](squareword.org) 🧩 #1479 🥳 7 ⏱️ 0:02:11.030386

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    L A M E D
    A B O D E
    M O T E L
    A R O M A
    S T R A Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1416 🥳 380 ⏱️ 0:06:01.714176

🤔 381 attempts
📜 1 sessions
🫧 20 chat sessions
⁉️ 97 chat prompts
🤖 97 dolphin3:latest replies
🥵   4 😎  36 🥶 328 🧊  12

      $1 #381 boot               100.00°C 🥳 1000‰ ~369 used:0  [368]  source:dolphin3
      $2 #375 shoes               38.25°C 🥵  982‰   ~2 used:5  [1]    source:dolphin3
      $3 #110 rack                38.03°C 🥵  978‰  ~38 used:89 [37]   source:dolphin3
      $4 #220 gear                37.39°C 🥵  971‰  ~32 used:41 [31]   source:dolphin3
      $5 #377 footwear            34.63°C 🥵  937‰   ~1 used:2  [0]    source:dolphin3
      $6 #327 helmet              32.45°C 😎  895‰  ~26 used:4  [25]   source:dolphin3
      $7 #316 saddle              32.27°C 😎  880‰  ~14 used:3  [13]   source:dolphin3
      $8 #229 gearshift           31.50°C 😎  845‰  ~37 used:8  [36]   source:dolphin3
      $9 #355 disc                31.27°C 😎  837‰   ~6 used:2  [5]    source:dolphin3
     $10  #13 upright             30.67°C 😎  810‰  ~40 used:29 [39]   source:dolphin3
     $11 #374 visor               30.45°C 😎  800‰   ~7 used:2  [6]    source:dolphin3
     $12 #175 drive               30.17°C 😎  780‰  ~36 used:6  [35]   source:dolphin3
     $42 #353 back                24.43°C 🥶        ~42 used:0  [41]   source:dolphin3
    $370 #309 section             -0.47°C 🧊       ~370 used:0  [369]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1449 🥳 143 ⏱️ 0:01:55.078892

🤔 144 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 22 chat prompts
🤖 22 dolphin3:latest replies
🔥  2 🥵 15 😎 36 🥶 76 🧊 14

      $1 #144 rémunération     100.00°C 🥳 1000‰ ~130 used:0  [129]  source:dolphin3
      $2 #127 salarié           53.54°C 🔥  995‰   ~1 used:4  [0]    source:dolphin3
      $3  #96 employeur         53.09°C 🔥  993‰  ~10 used:11 [9]    source:dolphin3
      $4 #112 contrat           49.42°C 🥵  984‰   ~2 used:1  [1]    source:dolphin3
      $5  #73 qualification     44.88°C 🥵  972‰  ~16 used:8  [15]   source:dolphin3
      $6  #30 entreprise        43.22°C 🥵  963‰  ~17 used:8  [16]   source:dolphin3
      $7  #68 emploi            43.17°C 🥵  962‰  ~15 used:3  [14]   source:dolphin3
      $8  #94 personnel         42.78°C 🥵  959‰  ~11 used:2  [10]   source:dolphin3
      $9 #137 durée             42.55°C 🥵  958‰   ~3 used:0  [2]    source:dolphin3
     $10  #56 professionnel     41.47°C 🥵  944‰  ~12 used:2  [11]   source:dolphin3
     $11  #66 stagiaire         41.05°C 🥵  940‰  ~13 used:2  [12]   source:dolphin3
     $19 #108 activité          36.23°C 😎  884‰  ~18 used:0  [17]   source:dolphin3
     $55  #70 entretien         21.48°C 🥶        ~56 used:0  [55]   source:dolphin3
    $131  #71 interview         -0.35°C 🧊       ~131 used:0  [130]  source:dolphin3

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #100 🥳 score:27 ⏱️ 0:01:59.801834

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. VOILA attempts:8 score:8
2. SILLY attempts:9 score:9
3. AWAKE attempts:6 score:6
4. PHONE attempts:4 score:4
