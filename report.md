# 2026-01-11

- 🔗 spaceword.org 🧩 2026-01-10 🏁 score 2173 ranked 6.0% 19/318 ⏱️ 0:08:33.869813
- 🔗 alfagok.diginaut.net 🧩 #435 🥳 15 ⏱️ 0:00:43.735581
- 🔗 alphaguess.com 🧩 #902 🥳 18 ⏱️ 0:00:51.911238
- 🔗 dontwordle.com 🧩 #1328 🥳 6 ⏱️ 0:01:23.072348
- 🔗 dictionary.com hurdle 🧩 #1471 🥳 16 ⏱️ 0:03:37.296247
- 🔗 Quordle Classic 🧩 #1448 🥳 score:22 ⏱️ 0:01:34.143858
- 🔗 Octordle Classic 🧩 #1448 🥳 score:60 ⏱️ 0:03:27.872162
- 🔗 squareword.org 🧩 #1441 🥳 7 ⏱️ 0:02:13.376328
- 🔗 cemantle.certitudes.org 🧩 #1378 🥳 81 ⏱️ 0:02:05.228001
- 🔗 cemantix.certitudes.org 🧩 #1411 🥳 224 ⏱️ 0:08:21.387230
- 🔗 Quordle Rescue 🧩 #62 🥳 score:28 ⏱️ 0:01:51.429623
- 🔗 Quordle Sequence 🧩 #1448 🥳 score:28 ⏱️ 0:01:53.536499
- 🔗 Quordle Extreme 🧩 #531 🥳 score:23 ⏱️ 0:01:23.920007
- 🔗 Octordle Rescue 🧩 #1448 🥳 score:8 ⏱️ 0:03:53.168706
- 🔗 Octordle Sequence 🧩 #1448 🥳 score:71 ⏱️ 0:03:37.771693
- 🔗 Octordle Extreme 🧩 #1448 🥳 score:60 ⏱️ 0:03:22.888818

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

















# spaceword.org 🧩 2026-01-10 🏁 score 2173 ranked 6.0% 19/318 ⏱️ 0:08:33.869813

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 19/318

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ A _ _ Q _ C _ O N   
      _ V _ G A R I G U E   
      _ A Z O T E S _ R E   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #435 🥳 15 ⏱️ 0:00:43.735581

🤔 15 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199833 [199833] lijm      q0  ? after
    @+247735 [247735] op        q2  ? after
    @+248065 [248065] opdracht  q9  ? after
    @+248149 [248149] opdrogen  q11 ? after
    @+248194 [248194] opeen     q13 ? after
    @+248212 [248212] opeens    q14 ? it
    @+248212 [248212] opeens    done. it
    @+248237 [248237] open      q10 ? before
    @+248410 [248410] opening   q8  ? before
    @+249329 [249329] opgespeld q7  ? before
    @+250923 [250923] oproep    q6  ? before
    @+254139 [254139] out       q5  ? before
    @+260621 [260621] pater     q4  ? before
    @+273540 [273540] proef     q3  ? before
    @+299738 [299738] schub     q1  ? before

# alphaguess.com 🧩 #902 🥳 18 ⏱️ 0:00:51.911238

🤔 18 attempts
📜 1 sessions

    @        [     0] aa           
    @+1      [     1] aah          
    @+2      [     2] aahed        
    @+3      [     3] aahing       
    @+98220  [ 98220] mach         q0  ? after
    @+147373 [147373] rhotic       q1  ? after
    @+159490 [159490] slop         q3  ? after
    @+160969 [160969] soft         q6  ? after
    @+161055 [161055] sol          q8  ? after
    @+161365 [161365] som          q9  ? after
    @+161406 [161406] some         q12 ? after
    @+161408 [161408] somebody     q17 ? it
    @+161408 [161408] somebody     done. it
    @+161409 [161409] someday      q16 ? before
    @+161411 [161411] somehow      q15 ? before
    @+161416 [161416] somersault   q14 ? before
    @+161427 [161427] somethings   q13 ? before
    @+161447 [161447] somnambulate q11 ? before
    @+161533 [161533] sonnet       q10 ? before
    @+161720 [161720] sore         q7  ? before
    @+162477 [162477] spec         q5  ? before
    @+165532 [165532] stick        q4  ? before
    @+171643 [171643] ta           q2  ? before

# dontwordle.com 🧩 #1328 🥳 6 ⏱️ 0:01:23.072348

📜 1 sessions
💰 score: 16

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:DOODY n n n n n remain:6216
    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:2882
    ⬜⬜⬜⬜⬜ tried:SMUTS n n n n n remain:457
    ⬜🟩⬜⬜⬜ tried:GRRRL n Y n n n remain:31
    ⬜🟩🟩⬜⬜ tried:CRICK n Y Y n n remain:8
    🟨🟩🟩⬜⬜ tried:FRIZZ m Y Y n n remain:2

    Undos used: 3

      2 words remaining
    x 8 unused letters
    = 16 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1471 🥳 16 ⏱️ 0:03:37.296247

📜 1 sessions
💰 score: 10000

    5/6
    AISLE ⬜🟨🟨⬜⬜
    TROIS ⬜⬜⬜🟨🟨
    SPINY 🟩⬜🟩⬜⬜
    SWISH 🟩⬜🟩⬜⬜
    SKIFF 🟩🟩🟩🟩🟩
    3/6
    SKIFF ⬜⬜⬜⬜⬜
    BROAD ⬜🟩⬜🟨⬜
    GRATE 🟩🟩🟩🟩🟩
    3/6
    GRATE 🟨⬜🟨⬜⬜
    SIGNA 🟩🟩🟩⬜🟩
    SIGMA 🟩🟩🟩🟩🟩
    4/6
    SIGMA ⬜🟨⬜⬜⬜
    RELIT 🟨⬜⬜🟩⬜
    CHOIR 🟩⬜🟨🟩🟨
    CURIO 🟩🟩🟩🟩🟩
    Final 1/2
    NOMAD 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1448 🥳 score:22 ⏱️ 0:01:34.143858

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SADLY attempts:7 score:7
2. RHINO attempts:4 score:4
3. AGONY attempts:5 score:5
4. HAIRY attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1448 🥳 score:60 ⏱️ 0:03:27.872162

📜 1 sessions

Octordle Classic

1. PAYEE attempts:7 score:7
2. SLUNG attempts:4 score:4
3. CLOSE attempts:5 score:5
4. BRING attempts:9 score:9
5. SLOOP attempts:6 score:6
6. BRAVO attempts:8 score:8
7. BIRTH attempts:10 score:10
8. SALON attempts:11 score:11

# squareword.org 🧩 #1441 🥳 7 ⏱️ 0:02:13.376328

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C U B A
    A R S O N
    L E A S T
    V A G U E
    O M E N S

# cemantle.certitudes.org 🧩 #1378 🥳 81 ⏱️ 0:02:05.228001

🤔 82 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 22 chat prompts
🤖 22 dolphin3:latest replies
🔥  2 🥵  7 😎 16 🥶 53 🧊  3

     $1 #82  ~1 illustration   100.00°C 🥳 1000‰
     $2 #60 ~16 portrait        46.65°C 🔥  993‰
     $3 #80  ~3 picture         46.31°C 🔥  992‰
     $4 #50 ~21 abstract        42.17°C 🥵  980‰
     $5 #75  ~6 photograph      41.08°C 🥵  974‰
     $6 #81  ~2 caricature      39.77°C 🥵  962‰
     $7 #69  ~9 collage         38.80°C 🥵  956‰
     $8 #66 ~11 watercolor      37.98°C 🥵  949‰
     $9 #48 ~22 painting        36.30°C 🥵  927‰
    $10 #70  ~8 artwork         35.56°C 🥵  913‰
    $11 #47 ~23 painter         33.90°C 😎  882‰
    $12 #79  ~4 image           33.90°C 😎  881‰
    $27 #71     drawing         24.04°C 🥶
    $80 #76     body            -0.85°C 🧊

# cemantix.certitudes.org 🧩 #1411 🥳 224 ⏱️ 0:08:21.387230

🤔 225 attempts
📜 1 sessions
🫧 15 chat sessions
⁉️ 63 chat prompts
🤖 63 dolphin3:latest replies
🥵   3 😎  22 🥶 153 🧊  46

      $1 #225   ~1 occupation      100.00°C 🥳 1000‰
      $2 #168   ~7 tenure           30.47°C 🥵  950‰
      $3 #113  ~15 mainmorte        29.61°C 🥵  935‰
      $4 #147  ~10 seigneurial      28.56°C 🥵  919‰
      $5 #106  ~18 bail             25.56°C 😎  837‰
      $6  #88  ~21 féodal           24.70°C 😎  798‰
      $7 #180   ~6 affectation      24.70°C 😎  796‰
      $8 #222   ~2 détention        23.83°C 😎  757‰
      $9 #127  ~12 sépulture        23.79°C 😎  756‰
     $10 #197   ~4 exploitation     23.51°C 😎  736‰
     $11 #137  ~11 nécropole        23.20°C 😎  719‰
     $12 #157   ~8 domination       22.62°C 😎  668‰
     $27 #160      régence          17.74°C 🥶
    $180  #30      car              -0.13°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #62 🥳 score:28 ⏱️ 0:01:51.429623

📜 2 sessions

Quordle Rescue m-w.com/games/quordle/

1. FRIED attempts:9 score:9
2. BELCH attempts:6 score:6
3. CURSE attempts:5 score:5
4. STOUT attempts:8 score:8

# [Quordle Sequence](m-w.com/games/quordle/#/sequence) 🧩 #1448 🥳 score:28 ⏱️ 0:01:53.536499

📜 2 sessions

Quordle Sequence m-w.com/games/quordle/

1. EVICT attempts:4 score:4
2. FIELD attempts:7 score:7
3. WISER attempts:8 score:8
4. PANEL attempts:9 score:9

# [Quordle Extreme](m-w.com/games/quordle/#/extreme) 🧩 #531 🥳 score:23 ⏱️ 0:01:23.920007

📜 1 sessions

Quordle Extreme m-w.com/games/quordle/

1. WHINY attempts:4 score:4
2. HUNKY attempts:5 score:5
3. CRACK attempts:6 score:6
4. BATTY attempts:8 score:8

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1448 🥳 score:8 ⏱️ 0:03:53.168706

📜 1 sessions

Octordle Rescue

1. STUMP attempts:10 score:10
2. TREAD attempts:8 score:8
3. CHAIN attempts:6 score:6
4. UPPER attempts:13 score:13
5. CHEER attempts:7 score:7
6. SOBER attempts:9 score:9
7. ROUGE attempts:11 score:11
8. WINDY attempts:5 score:5

# [Octordle Sequence](britannica.com/games/octordle/daily-sequence) 🧩 #1448 🥳 score:71 ⏱️ 0:03:37.771693

📜 1 sessions

Octordle Sequence

1. VERSE attempts:3 score:3
2. EXTOL attempts:6 score:6
3. BURNT attempts:7 score:7
4. TOAST attempts:9 score:9
5. FARCE attempts:10 score:10
6. SORRY attempts:11 score:11
7. SCARF attempts:12 score:12
8. ATOLL attempts:13 score:13

# [Octordle Extreme](britannica.com/games/octordle/extreme) 🧩 #1448 🥳 score:60 ⏱️ 0:03:22.888818

📜 1 sessions

Octordle Extreme

1. SUITE attempts:6 score:6
2. USURP attempts:5 score:5
3. OMBRE attempts:7 score:7
4. PARKA attempts:8 score:8
5. MAVEN attempts:9 score:9
6. MICRO attempts:4 score:4
7. PROUD attempts:10 score:10
8. PESKY attempts:11 score:11
