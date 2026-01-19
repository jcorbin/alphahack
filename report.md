# 2026-01-20

- 🔗 spaceword.org 🧩 2026-01-19 🏁 score 2170 ranked 32.3% 108/334 ⏱️ 13:03:52.720669
- 🔗 alfagok.diginaut.net 🧩 #444 🥳 17 ⏱️ 0:00:51.461810
- 🔗 alphaguess.com 🧩 #911 🥳 15 ⏱️ 0:00:47.968142
- 🔗 dontwordle.com 🧩 #1337 🥳 6 ⏱️ 0:01:31.305106
- 🔗 dictionary.com hurdle 🧩 #1480 🥳 12 ⏱️ 0:02:48.503752
- 🔗 Quordle Classic 🧩 #1457 🥳 score:22 ⏱️ 0:01:56.136946
- 🔗 Octordle Classic 🧩 #1457 🥳 score:62 ⏱️ 0:04:10.593252
- 🔗 squareword.org 🧩 #1450 🥳 7 ⏱️ 0:01:50.983793
- 🔗 cemantle.certitudes.org 🧩 #1387 🥳 260 ⏱️ 0:30:13.595526
- 🔗 cemantix.certitudes.org 🧩 #1420 🥳 153 ⏱️ 0:03:20.708628
- 🔗 Quordle Rescue 🧩 #71 🥳 score:22 ⏱️ 0:01:33.072713
- 🔗 Octordle Rescue 🧩 #1457 🥳 score:9 ⏱️ 0:03:23.897987

# Dev

## WIP

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





# [spaceword.org](spaceword.org) 🧩 2026-01-19 🏁 score 2170 ranked 32.3% 108/334 ⏱️ 13:03:52.720669

📜 7 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 108/334

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ F _ K _ J _ _ _   
      _ _ A D O B E _ _ _   
      _ _ V E R I T E _ _   
      _ _ O M A _ _ _ _ _   
      _ _ R O T I _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #444 🥳 17 ⏱️ 0:00:51.461810

🤔 17 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+99758  [ 99758] ex         q1  ? after
    @+149454 [149454] huis       q2  ? after
    @+174561 [174561] kind       q3  ? after
    @+187197 [187197] krontjongs q4  ? after
    @+193498 [193498] lavendel   q5  ? after
    @+194923 [194923] lees       q7  ? after
    @+195640 [195640] leid       q8  ? after
    @+196068 [196068] lengte     q9  ? after
    @+196233 [196233] lente      q10 ? after
    @+196375 [196375] lep        q13 ? after
    @+196445 [196445] lept       q14 ? after
    @+196453 [196453] leraar     q16 ? it
    @+196453 [196453] leraar     done. it
    @+196472 [196472] leraren    q15 ? before
    @+196512 [196512] les        q6  ? before
    @+199831 [199831] lijm       q0  ? before

# [alphaguess.com](alphaguess.com) 🧩 #911 🥳 15 ⏱️ 0:00:47.968142

🤔 15 attempts
📜 1 sessions

    @        [     0] aa     
    @+1      [     1] aah    
    @+2      [     2] aahed  
    @+3      [     3] aahing 
    @+98220  [ 98220] mach   q0  ? after
    @+147373 [147373] rhotic q1  ? after
    @+171643 [171643] ta     q2  ? after
    @+182008 [182008] un     q3  ? after
    @+189270 [189270] vicar  q4  ? after
    @+191050 [191050] walk   q6  ? after
    @+191913 [191913] we     q7  ? after
    @+192383 [192383] wen    q8  ? after
    @+192485 [192485] wha    q10 ? after
    @+192535 [192535] wharf  q11 ? after
    @+192547 [192547] what   q12 ? after
    @+192561 [192561] whats  q13 ? after
    @+192572 [192572] wheat  q14 ? it
    @+192572 [192572] wheat  done. it
    @+192587 [192587] whee   q9  ? before
    @+192874 [192874] whir   q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1337 🥳 6 ⏱️ 0:01:31.305106

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:HOWFF n n n n n remain:6599
    ⬜⬜⬜⬜⬜ tried:VILLI n n n n n remain:3033
    ⬜⬜⬜⬜⬜ tried:DURUM n n n n n remain:685
    ⬜🟩⬜⬜⬜ tried:BENNE n Y n n n remain:51
    ⬜🟩⬜⬜🟨 tried:PEPPY n Y n n m remain:5
    🟩🟩⬜⬜🟨 tried:YEGGS Y Y n n m remain:1

    Undos used: 2

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1480 🥳 12 ⏱️ 0:02:48.503752

📜 1 sessions
💰 score: 10400

    3/6
    TASER 🟩⬜🟨🟨⬜
    THENS 🟩🟩🟩⬜🟨
    THESE 🟩🟩🟩🟩🟩
    2/6
    THESE ⬜🟩⬜⬜⬜
    CHINA 🟩🟩🟩🟩🟩
    3/6
    CHINA ⬜⬜🟩⬜⬜
    TRIED 🟨🟩🟩🟨⬜
    WRITE 🟩🟩🟩🟩🟩
    3/6
    WRITE ⬜⬜⬜🟨⬜
    OATHS 🟨🟨🟨⬜⬜
    GLOAT 🟩🟩🟩🟩🟩
    Final 1/2
    WOUND 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1457 🥳 score:22 ⏱️ 0:01:56.136946

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. MONEY attempts:6 score:6
2. TRASH attempts:4 score:4
3. TROPE attempts:7 score:7
4. SHADE attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1457 🥳 score:62 ⏱️ 0:04:10.593252

📜 2 sessions

Octordle Classic

1. AMAZE attempts:11 score:11
2. FROWN attempts:12 score:12
3. ADULT attempts:4 score:4
4. ORDER attempts:5 score:5
5. AVOID attempts:6 score:6
6. QUAIL attempts:7 score:7
7. AZURE attempts:8 score:8
8. ASSET attempts:9 score:9

# [squareword.org](squareword.org) 🧩 #1450 🥳 7 ⏱️ 0:01:50.983793

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S E W E D
    L L A M A
    A I D E D
    S T E N O
    H E R D S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1387 🥳 260 ⏱️ 0:30:13.595526

🤔 261 attempts
📜 1 sessions
🫧 16 chat sessions
⁉️ 81 chat prompts
🤖 45 dolphin3:latest replies
🤖 36 nemotron-3-nano:latest replies
🔥   6 🥵  24 😎  46 🥶 177 🧊   7

      $1 #261   ~1 occasion          100.00°C 🥳 1000‰
      $2 #127  ~35 centenary          41.73°C 🔥  995‰
      $3  #59  ~66 commemoration      41.41°C 🔥  994‰
      $4  #60  ~65 anniversary        40.76°C 🔥  993‰
      $5 #256   ~4 celebratory        40.59°C 🔥  992‰
      $6 #102  ~45 jubilee            40.15°C 🔥  991‰
      $7  #58  ~67 celebration        39.94°C 🔥  990‰
      $8 #121  ~38 commemorate        38.07°C 🥵  987‰
      $9  #55  ~69 festivity          35.62°C 🥵  978‰
     $10 #162  ~21 celebrate          35.20°C 🥵  977‰
     $11 #173  ~16 tercentennial      35.04°C 🥵  975‰
     $32  #69  ~59 jollity            28.65°C 😎  881‰
     $78 #100      adulation          21.06°C 🥶
    $255 #125      archive            -0.56°C 🧊

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1420 🥳 153 ⏱️ 0:03:20.708628

🤔 154 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 33 chat prompts
🤖 33 dolphin3:latest replies
🔥  1 🥵 14 😎 25 🥶 80 🧊 33

      $1 #154   ~1 cotisation      100.00°C 🥳 1000‰
      $2 #118  ~17 rémunération     47.25°C 🔥  990‰
      $3 #136   ~9 adhésion         46.74°C 🥵  988‰
      $4 #129  ~13 salaire          46.62°C 🥵  987‰
      $5 #149   ~4 revenu           46.09°C 🥵  985‰
      $6  #75  ~34 employeur        45.44°C 🥵  984‰
      $7 #115  ~20 indemnité        43.40°C 🥵  979‰
      $8 #144   ~6 impôt            42.55°C 🥵  975‰
      $9  #90  ~27 salarié          42.43°C 🥵  973‰
     $10 #128  ~14 rémunérer        40.86°C 🥵  962‰
     $11 #112  ~23 prime            39.77°C 🥵  953‰
     $17 #123  ~15 compensation     34.05°C 😎  877‰
     $42 #119      rétrocession     18.24°C 🥶
    $122   #5      croissant        -0.11°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #71 🥳 score:22 ⏱️ 0:01:33.072713

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. BRUSH attempts:7 score:7
2. ACORN attempts:8 score:8
3. IRONY attempts:3 score:3
4. JOINT attempts:4 score:4

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1457 🥳 score:9 ⏱️ 0:03:23.897987

📜 2 sessions

Octordle Rescue

1. EATER attempts:8 score:8
2. RIPER attempts:12 score:12
3. DROOL attempts:9 score:9
4. WHEAT attempts:10 score:10
5. FAUNA attempts:11 score:11
6. SHAKY attempts:7 score:7
7. EXTOL attempts:5 score:5
8. NURSE attempts:6 score:6
