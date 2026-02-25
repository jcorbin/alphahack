# 2026-02-26

- 🔗 spaceword.org 🧩 2026-02-25 🏁 score 2168 ranked 25.4% 92/362 ⏱️ 2:55:52.577840
- 🔗 alfagok.diginaut.net 🧩 #481 🥳 34 ⏱️ 0:00:37.223758
- 🔗 alphaguess.com 🧩 #948 🥳 28 ⏱️ 0:00:33.214784
- 🔗 dontwordle.com 🧩 #1374 🥳 6 ⏱️ 0:01:45.663894
- 🔗 dictionary.com hurdle 🧩 #1517 🥳 15 ⏱️ 0:02:48.464316
- 🔗 Quordle Classic 🧩 #1494 🥳 score:24 ⏱️ 0:01:37.182023
- 🔗 Octordle Classic 🧩 #1494 🥳 score:69 ⏱️ 0:04:03.058888
- 🔗 squareword.org 🧩 #1487 🥳 8 ⏱️ 0:02:29.224652
- 🔗 cemantle.certitudes.org 🧩 #1424 🥳 209 ⏱️ 0:03:08.630900
- 🔗 cemantix.certitudes.org 🧩 #1457 🥳 510 ⏱️ 1:00:35.002093

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








# [spaceword.org](spaceword.org) 🧩 2026-02-25 🏁 score 2168 ranked 25.4% 92/362 ⏱️ 2:55:52.577840

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 92/362

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ J I B _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ _ T U X _ _ _   
      _ _ _ _ H _ I _ _ _   
      _ _ _ V O T E _ _ _   
      _ _ _ _ L _ R _ _ _   
      _ _ _ O O H _ _ _ _   
      _ _ _ R I A _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #481 🥳 34 ⏱️ 0:00:37.223758

🤔 34 attempts
📜 1 sessions

    @        [     0] &-teken          
    @+49841  [ 49841] boks             q4  ? ␅
    @+49841  [ 49841] boks             q5  ? after
    @+74754  [ 74754] dc               q10 ? ␅
    @+74754  [ 74754] dc               q11 ? after
    @+77726  [ 77726] der              q16 ? ␅
    @+77726  [ 77726] der              q17 ? after
    @+79229  [ 79229] dicht            q18 ? ␅
    @+79229  [ 79229] dicht            q19 ? after
    @+79772  [ 79772] dienst           q20 ? ␅
    @+79772  [ 79772] dienst           q21 ? after
    @+80033  [ 80033] dienstverrichter q24 ? ␅
    @+80033  [ 80033] dienstverrichter q25 ? after
    @+80059  [ 80059] dienstwoning     q30 ? ␅
    @+80059  [ 80059] dienstwoning     q31 ? after
    @+80067  [ 80067] diep             q32 ? ␅
    @+80067  [ 80067] diep             q33 ? it
    @+80067  [ 80067] diep             done. it
    @+80085  [ 80085] diepen           q28 ? ␅
    @+80085  [ 80085] diepen           q29 ? before
    @+80161  [ 80161] diepte           q26 ? ␅
    @+80161  [ 80161] diepte           q27 ? before
    @+80294  [ 80294] dieren           q22 ? ␅
    @+80294  [ 80294] dieren           q23 ? before
    @+80887  [ 80887] dijk             q14 ? ␅
    @+80887  [ 80887] dijk             q15 ? before
    @+87213  [ 87213] draag            q12 ? ␅
    @+87213  [ 87213] draag            q13 ? before
    @+99739  [ 99739] ex               q2  ? ␅
    @+99739  [ 99739] ex               q3  ? before
    @+199814 [199814] lijm             q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #948 🥳 28 ⏱️ 0:00:33.214784

🤔 28 attempts
📜 1 sessions

    @        [     0] aa     
    @+2      [     2] aahed  
    @+98218  [ 98218] mach   q0  ? ␅
    @+98218  [ 98218] mach   q1  ? after
    @+122779 [122779] parr   q4  ? ␅
    @+122779 [122779] parr   q5  ? after
    @+128848 [128848] play   q8  ? ␅
    @+128848 [128848] play   q9  ? after
    @+130062 [130062] poly   q12 ? ␅
    @+130062 [130062] poly   q13 ? after
    @+130930 [130930] pos    q14 ? ␅
    @+130930 [130930] pos    q15 ? after
    @+131370 [131370] pot    q16 ? ␅
    @+131370 [131370] pot    q17 ? after
    @+131488 [131488] pots   q20 ? ␅
    @+131488 [131488] pots   q21 ? after
    @+131550 [131550] poult  q22 ? ␅
    @+131550 [131550] poult  q23 ? after
    @+131564 [131564] pounce q26 ? ␅
    @+131564 [131564] pounce q27 ? it
    @+131564 [131564] pounce done. it
    @+131582 [131582] pour   q24 ? ␅
    @+131582 [131582] pour   q25 ? before
    @+131617 [131617] pow    q18 ? ␅
    @+131617 [131617] pow    q19 ? before
    @+131958 [131958] prearm q10 ? ␅
    @+131958 [131958] prearm q11 ? before
    @+135070 [135070] proper q6  ? ␅
    @+135070 [135070] proper q7  ? before
    @+147374 [147374] rhumb  q2  ? ␅
    @+147374 [147374] rhumb  q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1374 🥳 6 ⏱️ 0:01:45.663894

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MAGMA n n n n n remain:5731
    ⬜⬜⬜⬜⬜ tried:POTTO n n n n n remain:2026
    ⬜⬜⬜⬜⬜ tried:CIVIL n n n n n remain:589
    ⬜⬜⬜⬜⬜ tried:YUKKY n n n n n remain:177
    ⬜🟨⬜⬜⬜ tried:BENNE n m n n n remain:9
    ⬜🟨🟨🟨⬜ tried:DRESS n m m m n remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1517 🥳 15 ⏱️ 0:02:48.464316

📜 1 sessions
💰 score: 10100

    3/6
    RALES ⬜⬜⬜🟨⬜
    NEIGH ⬜🟨⬜⬜🟩
    EPOCH 🟩🟩🟩🟩🟩
    3/6
    EPOCH ⬜🟨🟩⬜⬜
    PROBS 🟨⬜🟩⬜🟨
    STOMP 🟩🟩🟩🟩🟩
    4/6
    STOMP ⬜⬜⬜⬜⬜
    ALDER 🟨🟩⬜⬜⬜
    BLACK ⬜🟩🟩⬜⬜
    FLAIL 🟩🟩🟩🟩🟩
    3/6
    FLAIL ⬜⬜⬜⬜⬜
    YOURS 🟨⬜🟨🟨⬜
    BUYER 🟩🟩🟩🟩🟩
    Final 2/2
    AWASH ⬜⬜🟩🟩🟩
    GNASH 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1494 🥳 score:24 ⏱️ 0:01:37.182023

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. ACTOR attempts:4 score:4
2. ENEMY attempts:6 score:6
3. GONER attempts:9 score:9
4. SCENE attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1494 🥳 score:69 ⏱️ 0:04:03.058888

📜 1 sessions

Octordle Classic

1. WARTY attempts:4 score:4
2. BLUFF attempts:11 score:11
3. GRIPE attempts:7 score:7
4. REFER attempts:13 score:13
5. GLYPH attempts:8 score:8
6. OPERA attempts:5 score:5
7. SINGE attempts:9 score:9
8. MOOSE attempts:12 score:12

# [squareword.org](squareword.org) 🧩 #1487 🥳 8 ⏱️ 0:02:29.224652

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T R A P
    C H O S E
    R O U S E
    A S T E R
    M E E T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1424 🥳 209 ⏱️ 0:03:08.630900

🤔 210 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 39 chat prompts
🤖 39 dolphin3:latest replies
🔥   1 🥵   5 😎  29 🥶 168 🧊   6

      $1 #210 sword         100.00°C 🥳 1000‰ ~204 used:0  [203]  source:dolphin3
      $2 #209 spear          52.65°C 🔥  992‰   ~1 used:0  [0]    source:dolphin3
      $3 #147 serpent        49.30°C 🥵  980‰  ~26 used:23 [25]   source:dolphin3
      $4 #173 dragon         48.03°C 🥵  974‰  ~19 used:14 [18]   source:dolphin3
      $5 #208 blade          45.58°C 🥵  965‰   ~2 used:1  [1]    source:dolphin3
      $6 #207 lance          43.38°C 🥵  943‰   ~3 used:2  [2]    source:dolphin3
      $7 #175 basilisk       40.62°C 🥵  909‰  ~18 used:11 [17]   source:dolphin3
      $8 #189 talon          39.03°C 😎  878‰  ~20 used:2  [19]   source:dolphin3
      $9 #111 clasp          37.13°C 😎  837‰  ~35 used:12 [34]   source:dolphin3
     $10 #141 snake          36.38°C 😎  812‰  ~29 used:4  [28]   source:dolphin3
     $11 #108 bow            36.22°C 😎  805‰  ~34 used:6  [33]   source:dolphin3
     $12 #134 garter         36.14°C 😎  797‰  ~30 used:4  [29]   source:dolphin3
     $37  #87 necktie        27.82°C 🥶        ~38 used:0  [37]   source:dolphin3
    $205  #43 depth          -0.60°C 🧊       ~205 used:0  [204]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1457 🥳 510 ⏱️ 1:00:35.002093

🤔 511 attempts
📜 1 sessions
🫧 32 chat sessions
⁉️ 166 chat prompts
🤖 166 dolphin3:latest replies
🔥   2 🥵  22 😎 102 🥶 345 🧊  39

      $1 #511 aspiration          100.00°C 🥳 1000‰ ~472 used:0   [471]  source:dolphin3
      $2 #383 épanouissement       46.83°C 🔥  994‰  ~20 used:97  [19]   source:dolphin3
      $3 #215 émancipateur         44.67°C 🔥  990‰ ~113 used:101 [112]  source:dolphin3
      $4 #176 démocratique         44.21°C 🥵  989‰ ~124 used:50  [123]  source:dolphin3
      $5 #139 émancipation         42.49°C 🥵  983‰ ~121 used:21  [120]  source:dolphin3
      $6 #263 propre               38.75°C 🥵  967‰   ~8 used:8   [7]    source:dolphin3
      $7 #268 vie                  38.62°C 🥵  965‰   ~9 used:8   [8]    source:dolphin3
      $8 #414 conscience           38.58°C 🥵  964‰  ~10 used:8   [9]    source:dolphin3
      $9 #182 social               38.57°C 🥵  963‰  ~12 used:8   [11]   source:dolphin3
     $10 #379 conscient            38.57°C 🥵  962‰  ~11 used:8   [10]   source:dolphin3
     $11 #152 politique            38.38°C 🥵  960‰  ~13 used:8   [12]   source:dolphin3
     $26 #406 enracinement         33.62°C 😎  888‰  ~21 used:0   [20]   source:dolphin3
    $128 #287 plus                 24.01°C 🥶       ~129 used:0   [128]  source:dolphin3
    $473  #76 responsable          -0.03°C 🧊       ~473 used:0   [472]  source:dolphin3
