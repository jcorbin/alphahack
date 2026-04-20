# 2026-04-21

- 🔗 spaceword.org 🧩 2026-04-20 🏁 score 2173 ranked 10.6% 36/340 ⏱️ 6:01:20.104429
- 🔗 alfagok.diginaut.net 🧩 #535 🥳 28 ⏱️ 0:00:46.943260
- 🔗 alphaguess.com 🧩 #1002 🥳 38 ⏱️ 0:00:35.446914
- 🔗 dontwordle.com 🧩 #1428 🥳 6 ⏱️ 0:01:20.655737
- 🔗 dictionary.com hurdle 🧩 #1571 🥳 18 ⏱️ 0:03:54.614777
- 🔗 Quordle Classic 🧩 #1548 🥳 score:26 ⏱️ 0:02:03.128836
- 🔗 Octordle Classic 🧩 #1548 🥳 score:64 ⏱️ 0:04:54.762009
- 🔗 squareword.org 🧩 #1541 🥳 7 ⏱️ 0:02:37.458128
- 🔗 cemantle.certitudes.org 🧩 #1478 🥳 271 ⏱️ 0:04:42.565391
- 🔗 cemantix.certitudes.org 🧩 #1511 🥳 143 ⏱️ 0:04:16.185683

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



















































# [spaceword.org](spaceword.org) 🧩 2026-04-20 🏁 score 2173 ranked 10.6% 36/340 ⏱️ 6:01:20.104429

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 36/340

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ J U T _ _ _   
      _ _ _ _ _ _ A _ _ _   
      _ _ _ _ V _ X _ _ _   
      _ _ _ _ A G O _ _ _   
      _ _ _ _ M E L _ _ _   
      _ _ _ _ O N S _ _ _   
      _ _ _ _ S O _ _ _ _   
      _ _ _ _ E M U _ _ _   
      _ _ _ _ _ E _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #535 🥳 28 ⏱️ 0:00:46.943260

🤔 28 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+2      [     2] -cijferig   
    @+24910  [ 24910] bad         q10 ? ␅
    @+24910  [ 24910] bad         q11 ? after
    @+31137  [ 31137] begeleiding q14 ? ␅
    @+31137  [ 31137] begeleiding q15 ? after
    @+32555  [ 32555] bejaarden   q18 ? ␅
    @+32555  [ 32555] bejaarden   q19 ? after
    @+32624  [ 32624] bek         q22 ? ␅
    @+32624  [ 32624] bek         q23 ? after
    @+32721  [ 32721] beker       q26 ? ␅
    @+32721  [ 32721] beker       q27 ? it
    @+32721  [ 32721] beker       done. it
    @+32931  [ 32931] beklede     q24 ? ␅
    @+32931  [ 32931] beklede     q25 ? before
    @+33241  [ 33241] bel         q20 ? ␅
    @+33241  [ 33241] bel         q21 ? before
    @+34010  [ 34010] beleid      q16 ? ␅
    @+34010  [ 34010] beleid      q17 ? before
    @+37372  [ 37372] beschermen  q12 ? ␅
    @+37372  [ 37372] beschermen  q13 ? before
    @+49840  [ 49840] boks        q8  ? ␅
    @+49840  [ 49840] boks        q9  ? before
    @+99736  [ 99736] ex          q6  ? ␅
    @+99736  [ 99736] ex          q7  ? before
    @+199605 [199605] lij         q0  ? ␅
    @+199605 [199605] lij         q1  ? after
    @+199605 [199605] lij         q2  ? ␅
    @+199605 [199605] lij         q3  ? after
    @+199605 [199605] lij         q4  ? ␅
    @+199605 [199605] lij         q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1002 🥳 38 ⏱️ 0:00:35.446914

🤔 38 attempts
📜 1 sessions

    @       [    0] aa       
    @+11763 [11763] back     q6  ? ␅
    @+11763 [11763] back     q7  ? after
    @+13801 [13801] be       q10 ? ␅
    @+13801 [13801] be       q11 ? after
    @+14164 [14164] bed      q16 ? ␅
    @+14164 [14164] bed      q17 ? after
    @+14390 [14390] bee      q18 ? ␅
    @+14390 [14390] bee      q19 ? after
    @+14471 [14471] beet     q22 ? ␅
    @+14471 [14471] beet     q23 ? after
    @+14472 [14472] beetle   q36 ? ␅
    @+14472 [14472] beetle   q37 ? it
    @+14472 [14472] beetle   done. it
    @+14473 [14473] beetled  q34 ? ␅
    @+14473 [14473] beetled  q35 ? before
    @+14474 [14474] beetler  q32 ? ␅
    @+14474 [14474] beetler  q33 ? before
    @+14476 [14476] beetles  q30 ? ␅
    @+14476 [14476] beetles  q31 ? before
    @+14481 [14481] beeves   q28 ? ␅
    @+14481 [14481] beeves   q29 ? before
    @+14491 [14491] befinger q26 ? ␅
    @+14491 [14491] befinger q27 ? before
    @+14512 [14512] beflower q24 ? ␅
    @+14512 [14512] beflower q25 ? before
    @+14553 [14553] beg      q20 ? ␅
    @+14553 [14553] beg      q21 ? before
    @+14778 [14778] bel      q14 ? ␅
    @+14778 [14778] bel      q15 ? before
    @+15757 [15757] bewrap   q13 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1428 🥳 6 ⏱️ 0:01:20.655737

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:JESSE n n n n n remain:3549
    ⬜⬜⬜⬜⬜ tried:PZAZZ n n n n n remain:1310
    ⬜⬜⬜⬜⬜ tried:HOLLO n n n n n remain:293
    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:67
    ⬜🟨⬜⬜⬜ tried:CIRRI n m n n n remain:3
    ⬜🟩🟩🟩🟩 tried:DYING n Y Y Y Y remain:2

    Undos used: 2

      2 words remaining
    x 7 unused letters
    = 14 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1571 🥳 18 ⏱️ 0:03:54.614777

📜 1 sessions
💰 score: 9800

    4/6
    LEANS ⬜⬜⬜🟩⬜
    PORNY ⬜⬜🟨🟩⬜
    RUING 🟨⬜🟩🟩🟩
    BRING 🟩🟩🟩🟩🟩
    5/6
    BRING ⬜🟨⬜⬜⬜
    RHEAS 🟨⬜⬜🟨⬜
    AMORT 🟨⬜⬜🟩⬜
    CLARY 🟩⬜🟨🟩🟩
    CARRY 🟩🟩🟩🟩🟩
    3/6
    CARRY ⬜⬜🟨⬜⬜
    TROGS 🟩🟨⬜⬜⬜
    THEIR 🟩🟩🟩🟩🟩
    5/6
    THEIR ⬜⬜🟨⬜🟩
    ASPER ⬜⬜⬜🟩🟩
    LOVER ⬜⬜⬜🟩🟩
    NUDER ⬜⬜🟨🟩🟩
    DEFER 🟩🟩🟩🟩🟩
    Final 1/2
    LEMON 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1548 🥳 score:26 ⏱️ 0:02:03.128836

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. FLUTE attempts:4 score:4
2. KITTY attempts:8 score:8
3. AFIRE attempts:5 score:5
4. GRANT attempts:9 score:9

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1548 🥳 score:64 ⏱️ 0:04:54.762009

📜 1 sessions

Octordle Classic

1. HELLO attempts:5 score:5
2. OCEAN attempts:6 score:6
3. BENCH attempts:9 score:9
4. ADEPT attempts:7 score:7
5. DRAMA attempts:11 score:11
6. FRILL attempts:10 score:10
7. LEECH attempts:4 score:4
8. GOOSE attempts:12 score:12

# [squareword.org](squareword.org) 🧩 #1541 🥳 7 ⏱️ 0:02:37.458128

📜 2 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S M A L L
    M E L E E
    O L I V E
    C O V E R
    K N E E S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1478 🥳 271 ⏱️ 0:04:42.565391

🤔 272 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 45 chat prompts
🤖 45 dolphin3:latest replies
🔥   1 🥵   3 😎  23 🥶 233 🧊  11

      $1 #272 tumor              100.00°C 🥳 1000‰ ~261 used:0  [260]  source:dolphin3
      $2 #265 cancer              63.16°C 🔥  992‰   ~1 used:0  [0]    source:dolphin3
      $3 #269 malignant           58.05°C 🥵  975‰   ~2 used:0  [1]    source:dolphin3
      $4 #268 leukemia            56.72°C 🥵  970‰   ~3 used:0  [2]    source:dolphin3
      $5 #261 oncogene            51.26°C 🥵  931‰   ~4 used:2  [3]    source:dolphin3
      $6 #184 embryonal           45.73°C 😎  778‰  ~26 used:12 [25]   source:dolphin3
      $7 #140 mutation            43.55°C 😎  669‰  ~27 used:15 [26]   source:dolphin3
      $8 #168 aneuploidy          42.99°C 😎  635‰  ~24 used:5  [23]   source:dolphin3
      $9 #171 mosaicism           42.54°C 😎  604‰  ~14 used:2  [13]   source:dolphin3
     $10 #146 gene                41.34°C 😎  516‰  ~15 used:2  [14]   source:dolphin3
     $11 #198 embryo              41.29°C 😎  511‰  ~16 used:2  [15]   source:dolphin3
     $12 #237 cytogenetic         40.89°C 😎  460‰  ~17 used:2  [16]   source:dolphin3
     $29 #210 villus              36.73°C 🥶        ~36 used:0  [35]   source:dolphin3
    $262  #88 counting            -0.30°C 🧊       ~262 used:0  [261]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1511 🥳 143 ⏱️ 0:04:16.185683

🤔 144 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 33 chat prompts
🤖 33 dolphin3:latest replies
🥵   1 😎  21 🥶 100 🧊  21

      $1 #144 alimentation       100.00°C 🥳 1000‰ ~123 used:0  [122]  source:dolphin3
      $2  #61 transformateur      37.33°C 🥵  961‰  ~19 used:24 [18]   source:dolphin3
      $3  #54 énergétique         32.37°C 😎  898‰  ~22 used:15 [21]   source:dolphin3
      $4  #52 électrique          31.05°C 😎  865‰  ~21 used:7  [20]   source:dolphin3
      $5  #51 volt                29.78°C 😎  821‰   ~9 used:2  [8]    source:dolphin3
      $6 #102 distribution        28.38°C 😎  747‰  ~10 used:2  [9]    source:dolphin3
      $7 #106 générateur          27.77°C 😎  709‰  ~11 used:2  [10]   source:dolphin3
      $8  #81 stockage            27.75°C 😎  707‰  ~12 used:2  [11]   source:dolphin3
      $9  #53 énergie             27.60°C 😎  697‰  ~13 used:2  [12]   source:dolphin3
     $10  #58 inductance          26.53°C 😎  620‰  ~14 used:2  [13]   source:dolphin3
     $11 #126 électricité         25.95°C 😎  569‰  ~15 used:2  [14]   source:dolphin3
     $12  #79 convertisseur       25.93°C 😎  566‰  ~16 used:2  [15]   source:dolphin3
     $24  #60 thermique           22.08°C 🥶        ~29 used:0  [28]   source:dolphin3
    $124  #43 soutien             -0.37°C 🧊       ~124 used:0  [123]  source:dolphin3
