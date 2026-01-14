# 2026-01-15

- 🔗 spaceword.org 🧩 2026-01-14 🏁 score 2165 ranked 47.4% 155/327 ⏱️ 0:10:39.356506
- 🔗 alphaguess.com 🧩 #906 🥳 10 ⏱️ 0:01:31.648627
- 🔗 dictionary.com hurdle 🧩 #1475 🥳 17 ⏱️ 0:03:55.577917
- 🔗 Quordle Classic 🧩 #1452 🥳 score:26 ⏱️ 0:01:50.176973
- 🔗 dontwordle.com 🧩 #1332 🥳 6 ⏱️ 0:04:23.000323
- 🔗 squareword.org 🧩 #1445 🥳 10 ⏱️ 0:02:44.002798
- 🔗 alfagok.diginaut.net 🧩 #439 🥳 12 ⏱️ 0:00:36.136653
- 🔗 Octordle Classic 🧩 #1452 😦 score:60 ⏱️ 0:07:00.742782
- 🔗 cemantle.certitudes.org 🧩 #1382 🥳 171 ⏱️ 0:07:33.326374
- 🔗 cemantix.certitudes.org 🧩 #1415 🥳 159 ⏱️ 0:02:03.709778
- 🔗 Quordle Rescue 🧩 #66 🥳 score:25 ⏱️ 0:01:24.375705
- 🔗 Octordle Rescue 🧩 #1452 😦 score:7 ⏱️ 0:03:57.481683

# Dev

## WIP

- hurdle: add novel words to wordlist

- meta:
  - rework SolverHarness => Solver{ Library, Scope }
  - variants: regression on 01-06 running quordle

- ui:
  - Handle -- stabilizing core over Listing
  - Shell -- minimizing over Handle
- meta: rework command model over Shell

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


















# spaceword.org 🧩 2026-01-11 🏗️ score 2173 current ranking 42/308 ⏱️ 8:04:00.125934

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 42/308

      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ O P _ P O G O E D
      _ W E K A _ _ _ _ O
      _ L _ A D J U R E S
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _





# [spaceword.org](spaceword.org) 🧩 2026-01-14 🏁 score 2165 ranked 47.4% 155/327 ⏱️ 0:10:39.356506

📜 3 sessions
- tiles: 21/21
- score: 2165 bonus: +65
- rank: 155/327

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ V E R B _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ A I R T _ _ _   
      _ _ _ _ S O H _ _ _   
      _ _ _ _ _ M I _ _ _   
      _ _ _ _ _ A E _ _ _   
      _ _ _ _ _ J _ _ _ _   
      _ _ _ Q U I D _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alphaguess.com](alphaguess.com) 🧩 #906 🥳 10 ⏱️ 0:01:31.648627

🤔 10 attempts
📜 1 sessions

    @        [     0] aa      
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98220  [ 98220] mach    q0  ? after
    @+122783 [122783] parr    q2  ? after
    @+135074 [135074] proper  q3  ? after
    @+140523 [140523] rec     q4  ? after
    @+143786 [143786] rem     q5  ? after
    @+144419 [144419] rep     q7  ? after
    @+144608 [144608] replace q9  ? it
    @+144608 [144608] replace done. it
    @+144809 [144809] repp    q8  ? before
    @+145199 [145199] res     q6  ? before
    @+147373 [147373] rhotic  q1  ? before

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1475 🥳 17 ⏱️ 0:03:55.577917

📜 2 sessions
💰 score: 9900

    4/6
    ARISE ⬜🟨⬜🟨⬜
    FOURS ⬜🟨⬜🟩🟨
    SNORT 🟩⬜🟩🟩⬜
    SWORD 🟩🟩🟩🟩🟩
    4/6
    SWORD ⬜⬜⬜⬜⬜
    ANIME ⬜⬜⬜⬜🟩
    BUGLE ⬜🟨⬜🟨🟩
    FLUKE 🟩🟩🟩🟩🟩
    3/6
    FLUKE ⬜⬜⬜🟨⬜
    KINDS 🟨⬜🟨🟨⬜
    DRANK 🟩🟩🟩🟩🟩
    4/6
    DRANK ⬜🟩⬜⬜⬜
    PROSE ⬜🟩⬜⬜⬜
    CRUFT ⬜🟩⬜⬜⬜
    GRIMY 🟩🟩🟩🟩🟩
    Final 2/2
    CHIEF ⬜🟩🟩🟩🟩
    THIEF 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1452 🥳 score:26 ⏱️ 0:01:50.176973

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. STINT attempts:6 score:6
2. WRECK attempts:4 score:4
3. EXTRA attempts:9 score:9
4. PUPIL attempts:7 score:7

# [dontwordle.com](dontwordle.com) 🧩 #1332 🥳 6 ⏱️ 0:04:23.000323

📜 1 sessions
💰 score: 42

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:OPPOS n n n n n remain:4100
    ⬜⬜⬜⬜⬜ tried:WANNA n n n n n remain:1330
    ⬜⬜⬜⬜⬜ tried:VERVE n n n n n remain:263
    ⬜⬜⬜⬜⬜ tried:ZIZIT n n n n n remain:62
    ⬜⬜🟨⬜⬜ tried:BLUFF n n m n n remain:20
    ⬜🟩⬜⬜🟨 tried:JUGUM n Y n n m remain:6

    Undos used: 5

      6 words remaining
    x 7 unused letters
    = 42 total score

# [squareword.org](squareword.org) 🧩 #1445 🥳 10 ⏱️ 0:02:44.002798

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C R A P S
    H E R O N
    E A G L E
    F L U K E
    S M E A R

# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #439 🥳 12 ⏱️ 0:00:36.136653

🤔 12 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+1      [     1] &-tekens    
    @+2      [     2] -cijferig   
    @+3      [     3] -e-mail     
    @+49846  [ 49846] boks        q2  ? after
    @+74759  [ 74759] dc          q3  ? after
    @+87220  [ 87220] draag       q4  ? after
    @+90072  [ 90072] dubbel      q6  ? after
    @+91760  [ 91760] dwerg       q7  ? after
    @+92589  [ 92589] educatie    q8  ? after
    @+92756  [ 92756] een         q9  ? after
    @+92923  [ 92923] eenheid     q11 ? it
    @+92923  [ 92923] eenheid     done. it
    @+93099  [ 93099] eenpersoons q10 ? before
    @+93448  [ 93448] eet         q5  ? before
    @+99755  [ 99755] ex          q1  ? before
    @+199830 [199830] lijm        q0  ? before

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1452 😦 score:60 ⏱️ 0:07:00.742782

📜 2 sessions

Octordle Classic

1. WACKY attempts:12 score:12
2. HORSE attempts:3 score:3
3. SHRUG attempts:7 score:7
4. SHA_E -CDGIJKLMNOPRTUWY attempts:13 score:-1
5. CANOE attempts:4 score:4
6. ROACH attempts:5 score:5
7. TENTH attempts:6 score:6
8. SHEER attempts:9 score:9

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1382 🥳 171 ⏱️ 0:07:33.326374

🤔 172 attempts
📜 1 sessions
🫧 12 chat sessions
⁉️ 47 chat prompts
🤖 47 dolphin3:latest replies
🔥   3 🥵  13 😎  41 🥶 108 🧊   6

      $1 #172   ~1 trustee         100.00°C 🥳 1000‰
      $2 #115  ~27 treasurer        59.21°C 😱  999‰
      $3 #130  ~23 administrator    52.43°C 🔥  997‰
      $4  #99  ~34 board            48.81°C 🔥  996‰
      $5 #168   ~5 principal        45.22°C 🥵  989‰
      $6 #164   ~8 chairman         43.85°C 🥵  985‰
      $7  #67  ~52 auditor          42.82°C 🥵  982‰
      $8 #146  ~17 president        40.25°C 🥵  969‰
      $9  #69  ~51 bookkeeper       39.07°C 🥵  961‰
     $10 #152  ~14 supervisor       38.74°C 🥵  957‰
     $11  #63  ~54 accountant       37.83°C 🥵  954‰
     $18  #59  ~57 director         32.88°C 😎  895‰
     $59 #126      organization     18.90°C 🥶
    $167  #46      brass            -2.34°C 🧊

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1415 🥳 159 ⏱️ 0:02:03.709778

🤔 160 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 25 chat prompts
🤖 25 dolphin3:latest replies
🔥  2 🥵 14 😎 31 🥶 56 🧊 56

      $1 #160   ~1 ordonnance       100.00°C 🥳 1000‰
      $2 #132  ~23 décret            63.13°C 😱  999‰
      $3 #125  ~28 loi               56.43°C 🔥  998‰
      $4 #129  ~26 code              44.32°C 🥵  986‰
      $5  #89  ~36 arrêté            44.10°C 🥵  985‰
      $6 #144  ~14 instruction       42.35°C 🥵  981‰
      $7 #131  ~24 disposition       41.52°C 🥵  979‰
      $8 #133  ~22 juridiction       41.18°C 🥵  978‰
      $9 #147  ~11 procédure         40.40°C 🥵  973‰
     $10 #154   ~4 circulaire        40.13°C 🥵  971‰
     $11  #87  ~38 règlement         38.65°C 🥵  959‰
     $18 #134  ~21 législation       32.93°C 😎  864‰
     $49  #68      définir           19.37°C 🥶
    $105 #109      recherche         -0.04°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #66 🥳 score:25 ⏱️ 0:01:24.375705

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. GUARD attempts:4 score:4
2. HUMAN attempts:7 score:7
3. LATCH attempts:6 score:6
4. JERKY attempts:8 score:8

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1452 😦 score:7 ⏱️ 0:03:57.481683

📜 1 sessions

Octordle Rescue

1. THIRD attempts:7 score:7
2. DOWNY attempts:11 score:11
3. CLEAN attempts:8 score:8
4. MARSH attempts:5 score:5
5. ODDER attempts:13 score:13
6. SKILL attempts:9 score:9
7. _A__R ~O -BCDEHIKLMNSTUWY attempts:13 score:-1
8. WORDY attempts:10 score:10
