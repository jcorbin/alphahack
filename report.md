# 2026-02-10

- 🔗 spaceword.org 🧩 2026-02-09 🏁 score 2168 ranked 33.9% 119/351 ⏱️ 3:08:46.244868
- 🔗 alfagok.diginaut.net 🧩 #465 🥳 28 ⏱️ 0:00:40.775642
- 🔗 alphaguess.com 🧩 #932 🥳 26 ⏱️ 0:00:28.623011
- 🔗 dontwordle.com 🧩 #1358 🥳 6 ⏱️ 0:02:02.736499
- 🔗 dictionary.com hurdle 🧩 #1501 🥳 17 ⏱️ 0:02:59.785064
- 🔗 Quordle Classic 🧩 #1478 🥳 score:18 ⏱️ 0:01:15.623219
- 🔗 Octordle Classic 🧩 #1478 🥳 score:61 ⏱️ 0:03:13.225068
- 🔗 squareword.org 🧩 #1471 🥳 8 ⏱️ 0:02:15.624699
- 🔗 cemantle.certitudes.org 🧩 #1408 🥳 300 ⏱️ 0:03:03.681681
- 🔗 cemantix.certitudes.org 🧩 #1441 🥳 152 ⏱️ 0:02:39.430441
- 🔗 Quordle Rescue 🧩 #92 🥳 score:26 ⏱️ 0:01:39.384455

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


























# [spaceword.org](spaceword.org) 🧩 2026-02-09 🏁 score 2168 ranked 33.9% 119/351 ⏱️ 3:08:46.244868

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 119/351

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ V _ _ _ D _ Q _ _   
      _ I _ O R I G I N _   
      _ E _ _ _ O H _ O _   
      _ R E G U L I _ W _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #465 🥳 28 ⏱️ 0:00:40.775642

🤔 28 attempts
📜 1 sessions

    @        [     0] &-teken        
    @+2      [     2] -cijferig      
    @+199826 [199826] lijm           q0  ? ␅
    @+199826 [199826] lijm           q1  ? after
    @+299731 [299731] schub          q2  ? ␅
    @+299731 [299731] schub          q3  ? after
    @+324297 [324297] sub            q6  ? ␅
    @+324297 [324297] sub            q7  ? after
    @+330480 [330480] televisie      q10 ? ␅
    @+330480 [330480] televisie      q11 ? after
    @+333682 [333682] these          q12 ? ␅
    @+333682 [333682] these          q13 ? after
    @+334094 [334094] ti             q14 ? ␅
    @+334094 [334094] ti             q15 ? after
    @+335492 [335492] tjingel        q16 ? ␅
    @+335492 [335492] tjingel        q17 ? after
    @+336138 [336138] toekomst       q18 ? ␅
    @+336138 [336138] toekomst       q19 ? after
    @+336266 [336266] toeleverancier q22 ? ␅
    @+336266 [336266] toeleverancier q23 ? after
    @+336317 [336317] toen           q24 ? ␅
    @+336317 [336317] toen           q25 ? after
    @+336317 [336317] toen           q26 ? ␅
    @+336317 [336317] toen           q27 ? it
    @+336317 [336317] toen           done. it
    @+336393 [336393] toer           q20 ? ␅
    @+336393 [336393] toer           q21 ? before
    @+336892 [336892] toetsing       q8  ? ␅
    @+336892 [336892] toetsing       q9  ? before
    @+349499 [349499] vakantie       q4  ? ␅
    @+349499 [349499] vakantie       q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #932 🥳 26 ⏱️ 0:00:28.623011

🤔 26 attempts
📜 1 sessions

    @        [     0] aa        
    @+1      [     1] aah       
    @+2      [     2] aahed     
    @+3      [     3] aahing    
    @+98219  [ 98219] mach      q0  ? ␅
    @+98219  [ 98219] mach      q1  ? after
    @+147372 [147372] rhotic    q2  ? ␅
    @+147372 [147372] rhotic    q3  ? after
    @+159489 [159489] slop      q6  ? ␅
    @+159489 [159489] slop      q7  ? after
    @+165531 [165531] stick     q8  ? ␅
    @+165531 [165531] stick     q9  ? after
    @+168583 [168583] sue       q10 ? ␅
    @+168583 [168583] sue       q11 ? after
    @+170090 [170090] surf      q12 ? ␅
    @+170090 [170090] surf      q13 ? after
    @+170863 [170863] switch    q14 ? ␅
    @+170863 [170863] switch    q15 ? after
    @+170948 [170948] swop      q20 ? ␅
    @+170948 [170948] swop      q21 ? after
    @+170954 [170954] sword     q24 ? ␅
    @+170954 [170954] sword     q25 ? it
    @+170954 [170954] sword     done. it
    @+170995 [170995] sybaritic q22 ? ␅
    @+170995 [170995] sybaritic q23 ? before
    @+171039 [171039] syllabi   q18 ? ␅
    @+171039 [171039] syllabi   q19 ? before
    @+171239 [171239] syn       q16 ? ␅
    @+171239 [171239] syn       q17 ? before
    @+171642 [171642] ta        q4  ? ␅
    @+171642 [171642] ta        q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1358 🥳 6 ⏱️ 0:02:02.736499

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:JEEZE n n n n n remain:6889
    ⬜⬜⬜⬜⬜ tried:NAPPA n n n n n remain:2159
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:1158
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:559
    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:126
    ⬜⬜🟩🟩🟩 tried:CHOCK n n Y Y Y remain:2

    Undos used: 3

      2 words remaining
    x 7 unused letters
    = 14 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1501 🥳 17 ⏱️ 0:02:59.785064

📜 1 sessions
💰 score: 9900

    3/6
    EARLS ⬜⬜⬜🟩⬜
    FITLY ⬜⬜⬜🟩🟩
    GODLY 🟩🟩🟩🟩🟩
    5/6
    GODLY ⬜⬜⬜⬜⬜
    TRACE ⬜⬜⬜⬜🟩
    SNIPE ⬜⬜🟨⬜🟩
    KUBIE ⬜🟨🟩🟨🟩
    IMBUE 🟩🟩🟩🟩🟩
    4/6
    IMBUE 🟨⬜⬜⬜🟨
    DRIES ⬜⬜🟩🟨⬜
    NEIGH 🟨🟨🟩🟨⬜
    EKING 🟩🟩🟩🟩🟩
    4/6
    EKING 🟨⬜⬜⬜⬜
    PEARS ⬜🟨🟩⬜🟨
    STALE 🟨⬜🟩⬜🟩
    CHASE 🟩🟩🟩🟩🟩
    Final 1/2
    ADMIN 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1478 🥳 score:18 ⏱️ 0:01:15.623219

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. DRAPE attempts:4 score:4
2. RAMEN attempts:6 score:6
3. TITAN attempts:3 score:3
4. IMPLY attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1478 🥳 score:61 ⏱️ 0:03:13.225068

📜 1 sessions

Octordle Classic

1. GLAND attempts:5 score:5
2. GOOEY attempts:6 score:6
3. GLAZE attempts:7 score:7
4. KAPPA attempts:11 score:11
5. BRIEF attempts:8 score:8
6. REPLY attempts:9 score:9
7. EDIFY attempts:3 score:3
8. BAWDY attempts:12 score:12

# [squareword.org](squareword.org) 🧩 #1471 🥳 8 ⏱️ 0:02:15.624699

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟨 🟨 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    R A J A H
    E L U D E
    D O N O R
    I N T R O
    D E A N S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1408 🥳 300 ⏱️ 0:03:03.681681

🤔 301 attempts
📜 19 sessions
🫧 10 chat sessions
⁉️ 43 chat prompts
🤖 43 dolphin3:latest replies
🔥   7 🥵  14 😎  33 🥶 218 🧊  28

      $1 #301 liable            100.00°C 🥳 1000‰ ~273 used:0  [272]  source:dolphin3
      $2 #299 accountable        52.30°C 🔥  998‰   ~1 used:0  [0]    source:dolphin3
      $3 #204 indemnify          49.83°C 🔥  997‰  ~17 used:20 [16]   source:dolphin3
      $4 #217 liability          49.77°C 🔥  996‰  ~16 used:12 [15]   source:dolphin3
      $5 #247 negligent          48.36°C 🔥  995‰   ~5 used:7  [4]    source:dolphin3
      $6 #231 negligence         45.28°C 🔥  994‰   ~3 used:6  [2]    source:dolphin3
      $7 #300 culpable           44.84°C 🔥  993‰   ~2 used:0  [1]    source:dolphin3
      $8 #211 damages            43.41°C 🔥  991‰   ~4 used:6  [3]    source:dolphin3
      $9 #295 wrongful           42.79°C 🥵  989‰   ~6 used:0  [5]    source:dolphin3
     $10 #203 reimburse          42.16°C 🥵  986‰   ~7 used:0  [6]    source:dolphin3
     $11 #160 compensate         39.21°C 🥵  981‰  ~18 used:3  [17]   source:dolphin3
     $23 #294 punitive           29.33°C 😎  880‰  ~21 used:0  [20]   source:dolphin3
     $56 #285 arbitration        19.52°C 🥶        ~63 used:0  [62]   source:dolphin3
    $274   #7 serenade           -0.01°C 🧊       ~274 used:0  [273]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1441 🥳 152 ⏱️ 0:02:39.430441

🤔 153 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 25 chat prompts
🤖 25 dolphin3:latest replies
😱  1 🔥  6 🥵 24 😎 49 🥶 53 🧊 19

      $1 #153 réglementation   100.00°C 🥳 1000‰ ~134 used:0 [133]  source:dolphin3
      $2 #142 législation       75.12°C 😱  999‰   ~1 used:1 [0]    source:dolphin3
      $3 #131 réglementaire     65.53°C 🔥  998‰   ~3 used:2 [2]    source:dolphin3
      $4  #97 norme             62.72°C 🔥  997‰   ~7 used:7 [6]    source:dolphin3
      $5  #81 conformité        54.98°C 🔥  995‰   ~6 used:6 [5]    source:dolphin3
      $6 #127 obligation        54.83°C 🔥  994‰   ~4 used:3 [3]    source:dolphin3
      $7 #102 règle             54.76°C 🔥  993‰   ~5 used:5 [4]    source:dolphin3
      $8  #65 contrôle          52.71°C 🔥  991‰   ~8 used:8 [7]    source:dolphin3
      $9 #136 directive         52.67°C 🔥  990‰   ~2 used:0 [1]    source:dolphin3
     $10  #78 sécurité          51.74°C 🥵  988‰  ~30 used:4 [29]   source:dolphin3
     $11 #115 prescription      49.10°C 🥵  983‰   ~9 used:0 [8]    source:dolphin3
     $33 #141 législateur       37.22°C 😎  888‰  ~32 used:0 [31]   source:dolphin3
     $82  #44 stratégie         22.52°C 🥶        ~81 used:0 [80]   source:dolphin3
    $135 #119 conformisme       -1.31°C 🧊       ~135 used:0 [134]  source:dolphin3

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #92 🥳 score:26 ⏱️ 0:01:39.384455

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. DROLL attempts:4 score:4
2. ROCKY attempts:6 score:6
3. AMISS attempts:9 score:9
4. SPICE attempts:7 score:7
