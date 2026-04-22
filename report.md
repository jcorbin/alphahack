# 2026-04-23

- 🔗 spaceword.org 🧩 2026-04-22 🏁 score 2168 ranked 29.1% 105/361 ⏱️ 21:24:02.360666
- 🔗 alfagok.diginaut.net 🧩 #537 🥳 26 ⏱️ 0:00:27.071410
- 🔗 alphaguess.com 🧩 #1004 🥳 34 ⏱️ 0:00:33.223730
- 🔗 dontwordle.com 🧩 #1430 🥳 6 ⏱️ 0:02:24.959865
- 🔗 dictionary.com hurdle 🧩 #1573 🥳 20 ⏱️ 0:06:47.681696
- 🔗 Quordle Classic 🧩 #1550 🥳 score:23 ⏱️ 0:02:45.433247
- 🔗 Octordle Classic 🧩 #1550 🥳 score:65 ⏱️ 0:04:14.721364
- 🔗 squareword.org 🧩 #1543 🥳 7 ⏱️ 0:02:12.511872
- 🔗 cemantle.certitudes.org 🧩 #1480 🥳 75 ⏱️ 0:00:48.141230
- 🔗 cemantix.certitudes.org 🧩 #1513 🥳 77 ⏱️ 0:03:33.098167

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





















































# [spaceword.org](spaceword.org) 🧩 2026-04-22 🏁 score 2168 ranked 29.1% 105/361 ⏱️ 21:24:02.360666

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 105/361

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ B _ Y _ Z _ _ J _   
      _ E _ O _ E R _ U _   
      _ A U G U R E R S _   
      _ L _ I _ K I _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #537 🥳 26 ⏱️ 0:00:27.071410

🤔 26 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+49840  [ 49840] boks       q6  ? ␅
    @+49840  [ 49840] boks       q7  ? after
    @+62279  [ 62279] cement     q10 ? ␅
    @+62279  [ 62279] cement     q11 ? after
    @+68513  [ 68513] connectie  q12 ? ␅
    @+68513  [ 68513] connectie  q13 ? after
    @+68870  [ 68870] consult    q20 ? ␅
    @+68870  [ 68870] consult    q21 ? after
    @+69038  [ 69038] consumptie q22 ? ␅
    @+69038  [ 69038] consumptie q23 ? after
    @+69094  [ 69094] contact    q24 ? ␅
    @+69094  [ 69094] contact    q25 ? it
    @+69094  [ 69094] contact    done. it
    @+69241  [ 69241] container  q18 ? ␅
    @+69241  [ 69241] container  q19 ? before
    @+70049  [ 70049] convulsie  q16 ? ␅
    @+70049  [ 70049] convulsie  q17 ? before
    @+71584  [ 71584] cru        q14 ? ␅
    @+71584  [ 71584] cru        q15 ? before
    @+74753  [ 74753] dc         q8  ? ␅
    @+74753  [ 74753] dc         q9  ? before
    @+99736  [ 99736] ex         q4  ? ␅
    @+99736  [ 99736] ex         q5  ? before
    @+199605 [199605] lij        q0  ? ␅
    @+199605 [199605] lij        q1  ? after
    @+199605 [199605] lij        q2  ? ␅
    @+199605 [199605] lij        q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1004 🥳 34 ⏱️ 0:00:33.223730

🤔 34 attempts
📜 1 sessions

    @        [     0] aa      
    @+98216  [ 98216] mach    q0  ? ␅
    @+98216  [ 98216] mach    q1  ? after
    @+98216  [ 98216] mach    q2  ? ␅
    @+98216  [ 98216] mach    q3  ? after
    @+147366 [147366] rhotic  q4  ? ␅
    @+147366 [147366] rhotic  q5  ? after
    @+148803 [148803] rot     q14 ? ␅
    @+148803 [148803] rot     q15 ? after
    @+149528 [149528] run     q16 ? ␅
    @+149528 [149528] run     q17 ? after
    @+149818 [149818] sac     q18 ? ␅
    @+149818 [149818] sac     q19 ? after
    @+150061 [150061] sag     q20 ? ␅
    @+150061 [150061] sag     q21 ? after
    @+150096 [150096] sagger  q26 ? ␅
    @+150096 [150096] sagger  q27 ? after
    @+150113 [150113] sags    q28 ? ␅
    @+150113 [150113] sags    q29 ? after
    @+150122 [150122] sahuaro q30 ? ␅
    @+150122 [150122] sahuaro q31 ? after
    @+150126 [150126] said    q32 ? ␅
    @+150126 [150126] said    q33 ? it
    @+150126 [150126] said    done. it
    @+150130 [150130] sail    q24 ? ␅
    @+150130 [150130] sail    q25 ? before
    @+150199 [150199] saiyid  q22 ? ␅
    @+150199 [150199] saiyid  q23 ? before
    @+150337 [150337] sallow  q12 ? ␅
    @+150337 [150337] sallow  q13 ? before
    @+153315 [153315] sea     q11 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1430 🥳 6 ⏱️ 0:02:24.959865

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:ADDAX n n n n n remain:6032
    ⬜⬜⬜⬜⬜ tried:GOGOS n n n n n remain:1404
    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:512
    ⬜⬜⬜⬜⬜ tried:MYRRH n n n n n remain:92
    ⬜⬜⬜⬜🟩 tried:BENNE n n n n Y remain:6
    🟨🟨⬜⬜🟩 tried:TUQUE m m n n Y remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1573 🥳 20 ⏱️ 0:06:47.681696

📜 2 sessions
💰 score: 9600

    6/6
    RESAT 🟨⬜🟨⬜⬜
    DUROS ⬜🟨🟨⬜🟨
    BRUSH ⬜🟨🟩🟨⬜
    SLURP 🟩⬜🟩🟩⬜
    SCURF 🟩⬜🟩🟩🟩
    SMURF 🟩🟩🟩🟩🟩
    4/6
    SMURF ⬜⬜⬜⬜⬜
    NODAL 🟨⬜⬜⬜⬜
    WINGY 🟩🟨🟨⬜⬜
    WHINE 🟩🟩🟩🟩🟩
    4/6
    WHINE ⬜⬜🟨⬜⬜
    LIMAS ⬜🟩⬜⬜🟨
    SICKY 🟩🟩⬜⬜🟩
    SIXTY 🟩🟩🟩🟩🟩
    4/6
    SIXTY ⬜⬜⬜⬜⬜
    ARGOL ⬜⬜⬜⬜⬜
    MUNCH ⬜⬜⬜🟩🟨
    CHECK 🟩🟩🟩🟩🟩
    Final 2/2
    BURET 🟨🟨🟨🟨🟩
    REBUT 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1550 🥳 score:23 ⏱️ 0:02:45.433247

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. KNEAD attempts:5 score:5
2. PULSE attempts:7 score:7
3. CRUST attempts:8 score:8
4. TASTE attempts:3 score:3

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1550 🥳 score:65 ⏱️ 0:04:14.721364

📜 1 sessions

Octordle Classic

1. WINCE attempts:11 score:11
2. SIXTY attempts:12 score:12
3. ABACK attempts:6 score:6
4. DULLY attempts:8 score:8
5. BLOND attempts:4 score:4
6. MIMIC attempts:9 score:9
7. GRADE attempts:5 score:5
8. SPORT attempts:10 score:10

# [squareword.org](squareword.org) 🧩 #1543 🥳 7 ⏱️ 0:02:12.511872

📜 3 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T R E P
    C R O N E
    R I O T S
    U P S E T
    M E T R O

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1480 🥳 75 ⏱️ 0:00:48.141230

🤔 76 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 12 chat prompts
🤖 12 dolphin3:latest replies
🔥  3 🥵  8 😎 18 🥶 46

     $1 #76 snow         100.00°C 🥳 1000‰ ~76 used:0 [75]  source:dolphin3
     $2 #71 rain          62.57°C 🔥  993‰  ~1 used:0 [0]   source:dolphin3
     $3 #74 slushy        59.56°C 🔥  991‰  ~2 used:0 [1]   source:dolphin3
     $4 #70 icy           56.07°C 🔥  990‰  ~3 used:0 [2]   source:dolphin3
     $5 #47 ice           53.92°C 🥵  985‰ ~11 used:3 [10]  source:dolphin3
     $6 #49 snowflake     50.46°C 🥵  980‰  ~8 used:2 [7]   source:dolphin3
     $7 #63 slush         50.27°C 🥵  979‰  ~9 used:2 [8]   source:dolphin3
     $8 #52 winter        48.99°C 🥵  975‰ ~10 used:2 [9]   source:dolphin3
     $9 #65 arctic        42.65°C 🥵  953‰  ~4 used:0 [3]   source:dolphin3
    $10 #57 frostbite     41.87°C 🥵  949‰  ~5 used:0 [4]   source:dolphin3
    $11 #67 cold          40.92°C 🥵  940‰  ~6 used:0 [5]   source:dolphin3
    $12 #54 chilly        38.74°C 🥵  914‰  ~7 used:0 [6]   source:dolphin3
    $13 #56 freezing      37.64°C 😎  899‰ ~12 used:0 [11]  source:dolphin3
    $31 #26 spongy        22.87°C 🥶       ~31 used:3 [30]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1513 🥳 77 ⏱️ 0:03:33.098167

🤔 78 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 8 chat prompts
🤖 8 dolphin3:latest replies
🥵  9 😎 12 🥶 36 🧊 20

     $1 #78 cohésion         100.00°C 🥳 1000‰ ~58 used:0 [57]  source:dolphin3
     $2 #72 solidarité        41.50°C 🥵  989‰  ~6 used:2 [5]   source:dolphin3
     $3 #62 communautaire     40.04°C 🥵  986‰  ~1 used:1 [0]   source:dolphin3
     $4 #77 union             39.37°C 🥵  978‰  ~2 used:0 [1]   source:dolphin3
     $5 #68 intégration       36.38°C 🥵  950‰  ~3 used:0 [2]   source:dolphin3
     $6 #53 social            36.31°C 🥵  945‰  ~7 used:2 [6]   source:dolphin3
     $7 #60 action            36.31°C 🥵  946‰  ~4 used:0 [3]   source:dolphin3
     $8 #32 développement     34.42°C 🥵  921‰  ~8 used:3 [7]   source:dolphin3
     $9 #31 durable           34.11°C 🥵  918‰  ~9 used:3 [8]   source:dolphin3
    $10 #74 égalité           33.56°C 🥵  907‰  ~5 used:0 [4]   source:dolphin3
    $11 #64 engagement        31.31°C 😎  837‰ ~10 used:0 [9]   source:dolphin3
    $12 #54 stratégique       30.23°C 😎  791‰ ~11 used:0 [10]  source:dolphin3
    $23 #44 conception        20.96°C 🥶       ~23 used:0 [22]  source:dolphin3
    $59 #21 cours             -0.05°C 🧊       ~59 used:0 [58]  source:dolphin3
