# 2026-02-20

- 🔗 alfagok.diginaut.net 🧩 #475 🥳 26 ⏱️ 0:00:27.999173
- 🔗 alphaguess.com 🧩 #942 🥳 28 ⏱️ 0:00:27.439422
- 🔗 dontwordle.com 🧩 #1368 🤷 6 ⏱️ 0:02:18.664877
- 🔗 dictionary.com hurdle 🧩 #1511 🥳 19 ⏱️ 0:03:19.601602
- 🔗 Quordle Classic 🧩 #1488 🥳 score:20 ⏱️ 0:01:09.768349
- 🔗 Octordle Classic 🧩 #1488 🥳 score:61 ⏱️ 0:03:01.465722
- 🔗 squareword.org 🧩 #1481 🥳 8 ⏱️ 0:02:33.112636
- 🔗 cemantle.certitudes.org 🧩 #1418 🥳 69 ⏱️ 0:00:30.363887
- 🔗 cemantix.certitudes.org 🧩 #1451 🥳 265 ⏱️ 0:04:56.308481
- 🔗 Quordle Rescue 🧩 #102 🥳 score:22 ⏱️ 0:01:13.923929

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


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #475 🥳 26 ⏱️ 0:00:27.999173

🤔 26 attempts
📜 1 sessions

    @        [     0] &-teken
    @+1      [     1] &-tekens
    @+2      [     2] -cijferig
    @+3      [     3] -e-mail
    @+199816 [199816] lijm      q0  ? ␅
    @+199816 [199816] lijm      q1  ? after
    @+299721 [299721] schub     q2  ? ␅
    @+299721 [299721] schub     q3  ? after
    @+324287 [324287] sub       q6  ? ␅
    @+324287 [324287] sub       q7  ? after
    @+336882 [336882] toetsing  q8  ? ␅
    @+336882 [336882] toetsing  q9  ? after
    @+339873 [339873] transport q12 ? ␅
    @+339873 [339873] transport q13 ? after
    @+341444 [341444] trompet   q14 ? ␅
    @+341444 [341444] trompet   q15 ? after
    @+341600 [341600] tros      q20 ? ␅
    @+341600 [341600] tros      q21 ? after
    @+341613 [341613] trots     q24 ? ␅
    @+341613 [341613] trots     q25 ? it
    @+341613 [341613] trots     done. it
    @+341655 [341655] trouw     q22 ? ␅
    @+341655 [341655] trouw     q23 ? before
    @+341764 [341764] truc      q18 ? ␅
    @+341764 [341764] truc      q19 ? before
    @+342126 [342126] tuin      q16 ? ␅
    @+342126 [342126] tuin      q17 ? before
    @+343072 [343072] tv        q10 ? ␅
    @+343072 [343072] tv        q11 ? before
    @+349489 [349489] vakantie  q4  ? ␅
    @+349489 [349489] vakantie  q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #942 🥳 28 ⏱️ 0:00:27.439422

🤔 28 attempts
📜 1 sessions

    @        [     0] aa
    @+2      [     2] aahed
    @+98219  [ 98219] mach    q0  ? ␅
    @+98219  [ 98219] mach    q1  ? after
    @+122780 [122780] parr    q4  ? ␅
    @+122780 [122780] parr    q5  ? after
    @+128849 [128849] play    q10 ? ␅
    @+128849 [128849] play    q11 ? after
    @+130063 [130063] poly    q14 ? ␅
    @+130063 [130063] poly    q15 ? after
    @+130484 [130484] pond    q18 ? ␅
    @+130484 [130484] pond    q19 ? after
    @+130565 [130565] poo     q22 ? ␅
    @+130565 [130565] poo     q23 ? after
    @+130590 [130590] pool    q26 ? ␅
    @+130590 [130590] pool    q27 ? it
    @+130590 [130590] pool    done. it
    @+130613 [130613] poor    q24 ? ␅
    @+130613 [130613] poor    q25 ? before
    @+130698 [130698] popular q20 ? ␅
    @+130698 [130698] popular q21 ? before
    @+130931 [130931] pos     q16 ? ␅
    @+130931 [130931] pos     q17 ? before
    @+131959 [131959] prearm  q12 ? ␅
    @+131959 [131959] prearm  q13 ? before
    @+135071 [135071] proper  q6  ? ␅
    @+135071 [135071] proper  q7  ? after
    @+135071 [135071] proper  q8  ? ␅
    @+135071 [135071] proper  q9  ? before
    @+147375 [147375] rhumb   q2  ? ␅
    @+147375 [147375] rhumb   q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1368 🤷 6 ⏱️ 0:02:18.664877

📜 1 sessions
💰 score: 0

ELIMINATED
> Well technically I didn't Wordle!

    ⬜⬜⬜⬜⬜ tried:PAPAW n n n n n remain:5916
    ⬜⬜⬜⬜⬜ tried:BEZEL n n n n n remain:1681
    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:723
    ⬜⬜⬜⬜⬜ tried:TRUTH n n n n n remain:102
    ⬜⬜⬜🟩🟨 tried:GOGOS n n n Y m remain:1
    ⬛⬛⬛⬛⬛ tried:????? remain:0

    Undos used: 5

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1511 🥳 19 ⏱️ 0:03:19.601602

📜 1 sessions
💰 score: 9700

    6/6
    ARLES ⬜⬜🟨⬜⬜
    LINGO 🟨⬜⬜⬜🟨
    CLOUT ⬜🟩🟩⬜⬜
    BLOWY 🟩🟩🟩⬜⬜
    BLOOD 🟩🟩🟩🟩⬜
    BLOOM 🟩🟩🟩🟩🟩
    5/6
    BLOOM ⬜⬜⬜⬜⬜
    RESAT ⬜🟨⬜🟨⬜
    ACHED 🟨⬜⬜🟨⬜
    KNAVE ⬜🟨🟨🟩🟩
    NAIVE 🟩🟩🟩🟩🟩
    4/6
    NAIVE ⬜⬜⬜⬜🟩
    HOUSE ⬜⬜⬜⬜🟩
    MERGE ⬜🟩⬜🟩🟩
    LEDGE 🟩🟩🟩🟩🟩
    3/6
    LEDGE 🟨🟨🟨⬜⬜
    OILED 🟨⬜🟨🟩🟨
    DOWEL 🟩🟩🟩🟩🟩
    Final 1/2
    LARVA 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1488 🥳 score:20 ⏱️ 0:01:09.768349

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. CARGO attempts:3 score:3
2. DIRTY attempts:5 score:5
3. CHILI attempts:8 score:8
4. TRIAD attempts:4 score:4

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1488 🥳 score:61 ⏱️ 0:03:01.465722

📜 1 sessions

Octordle Classic

1. NINTH attempts:6 score:6
2. STOIC attempts:7 score:7
3. FLING attempts:8 score:8
4. CLANK attempts:9 score:9
5. MUCUS attempts:10 score:10
6. TATTY attempts:12 score:12
7. ROYAL attempts:5 score:5
8. PLANT attempts:4 score:4

# [squareword.org](squareword.org) 🧩 #1481 🥳 8 ⏱️ 0:02:33.112636

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟩 🟨 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S W A B S
    H A B I T
    A G I L E
    L E D G E
    T R E E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1418 🥳 69 ⏱️ 0:00:30.363887

🤔 70 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 10 chat prompts
🤖 10 dolphin3:latest replies
🥵  1 😎  4 🥶 63 🧊  1

     $1 #70 icon            100.00°C 🥳 1000‰ ~69 used:0 [68]  source:dolphin3
     $2 #15 image            33.54°C 🥵  931‰  ~1 used:7 [0]   source:dolphin3
     $3 #30 screen           28.78°C 😎  759‰  ~4 used:2 [3]   source:dolphin3
     $4 #67 wallpaper        26.61°C 😎  610‰  ~2 used:0 [1]   source:dolphin3
     $5 #62 portrait         26.31°C 😎  577‰  ~3 used:0 [2]   source:dolphin3
     $6 #20 display          23.01°C 😎   34‰  ~5 used:3 [4]   source:dolphin3
     $7 #34 dashboard        20.71°C 🥶        ~7 used:1 [6]   source:dolphin3
     $8 #65 slide            20.61°C 🥶        ~8 used:0 [7]   source:dolphin3
     $9 #38 interface        20.05°C 🥶        ~9 used:1 [8]   source:dolphin3
    $10 #40 recognition      19.74°C 🥶       ~10 used:0 [9]   source:dolphin3
    $11 #16 photo            19.33°C 🥶        ~6 used:3 [5]   source:dolphin3
    $12 #46 annotation       18.26°C 🥶       ~11 used:0 [10]  source:dolphin3
    $13 #14 snapshot         17.90°C 🥶       ~12 used:0 [11]  source:dolphin3
    $70  #4 chocolate        -0.45°C 🧊       ~70 used:0 [69]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1451 🥳 265 ⏱️ 0:04:56.308481

🤔 266 attempts
📜 1 sessions
🫧 14 chat sessions
⁉️ 62 chat prompts
🤖 62 dolphin3:latest replies
😱   1 🔥   2 🥵  21 😎  51 🥶 151 🧊  39

      $1 #266 autochtone      100.00°C 🥳 1000‰ ~227 used:0  [226]  source:dolphin3
      $2 #264 indigène         63.56°C 😱  999‰   ~1 used:1  [0]    source:dolphin3
      $3 #137 bantou           48.09°C 🔥  992‰  ~20 used:37 [19]   source:dolphin3
      $4 #200 ethnie           47.81°C 🔥  990‰   ~7 used:12 [6]    source:dolphin3
      $5 #208 tribu            45.16°C 🥵  984‰  ~21 used:4  [20]   source:dolphin3
      $6 #265 aborigène        43.85°C 🥵  979‰   ~2 used:0  [1]    source:dolphin3
      $7 #175 soninké          43.31°C 🥵  978‰  ~22 used:7  [21]   source:dolphin3
      $8 #153 haoussa          42.60°C 🥵  974‰  ~23 used:8  [22]   source:dolphin3
      $9 #189 kanak            42.23°C 🥵  971‰   ~8 used:2  [7]    source:dolphin3
     $10 #151 ethnique         41.98°C 🥵  967‰  ~17 used:3  [16]   source:dolphin3
     $11 #186 akan             41.91°C 🥵  966‰   ~9 used:2  [8]    source:dolphin3
     $26 #162 ashanti          37.61°C 😎  897‰  ~24 used:0  [23]   source:dolphin3
     $77 #231 coexistence      24.95°C 🥶        ~89 used:0  [88]   source:dolphin3
    $228  #63 amande           -0.18°C 🧊       ~228 used:0  [227]  source:dolphin3

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #102 🥳 score:22 ⏱️ 0:01:13.923929

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. BEACH attempts:6 score:6
2. HOLLY attempts:7 score:7
3. BRICK attempts:5 score:5
4. BRUTE attempts:4 score:4
