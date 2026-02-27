# 2026-02-28

- 🔗 spaceword.org 🧩 2026-02-27 🏁 score 2173 ranked 9.7% 33/339 ⏱️ 1:00:53.871162
- 🔗 alfagok.diginaut.net 🧩 #483 🥳 40 ⏱️ 0:00:45.846252
- 🔗 alphaguess.com 🧩 #950 🥳 30 ⏱️ 0:00:33.566855
- 🔗 dontwordle.com 🧩 #1376 🥳 6 ⏱️ 0:01:26.647074
- 🔗 dictionary.com hurdle 🧩 #1519 🥳 19 ⏱️ 0:02:33.608580
- 🔗 Quordle Classic 🧩 #1496 🥳 score:21 ⏱️ 0:01:13.008367
- 🔗 Octordle Classic 🧩 #1496 🥳 score:63 ⏱️ 0:03:53.857675
- 🔗 squareword.org 🧩 #1489 🥳 8 ⏱️ 0:03:07.730001
- 🔗 cemantle.certitudes.org 🧩 #1426 🥳 165 ⏱️ 0:02:28.577477
- 🔗 cemantix.certitudes.org 🧩 #1459 🥳 300 ⏱️ 0:09:59.353055

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










# [spaceword.org](spaceword.org) 🧩 2026-02-27 🏁 score 2173 ranked 9.7% 33/339 ⏱️ 1:00:53.871162

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 33/339

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ K A _ O _ J U D O   
      _ I X N A Y _ T E _   
      _ P _ O R O G E N _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #483 🥳 40 ⏱️ 0:00:45.846252

🤔 40 attempts
📜 1 sessions

    @        [     0] &-teken  
    @+49841  [ 49841] boks     q6  ? ␅
    @+49841  [ 49841] boks     q7  ? after
    @+74754  [ 74754] dc       q12 ? ␅
    @+74754  [ 74754] dc       q13 ? after
    @+87213  [ 87213] draag    q14 ? ␅
    @+87213  [ 87213] draag    q15 ? after
    @+87911  [ 87911] dreg     q24 ? ␅
    @+87911  [ 87911] dreg     q25 ? after
    @+87919  [ 87919] dreig    q36 ? ␅
    @+87919  [ 87919] dreig    q37 ? after
    @+87928  [ 87928] dreigen  q38 ? ␅
    @+87928  [ 87928] dreigen  q39 ? it
    @+87928  [ 87928] dreigen  done. it
    @+87936  [ 87936] dreiging q34 ? ␅
    @+87936  [ 87936] dreiging q35 ? before
    @+87967  [ 87967] drek     q32 ? ␅
    @+87967  [ 87967] drek     q33 ? before
    @+88024  [ 88024] drens    q30 ? ␅
    @+88024  [ 88024] drens    q31 ? before
    @+88138  [ 88138] drie     q28 ? ␅
    @+88138  [ 88138] drie     q29 ? before
    @+88620  [ 88620] drink    q20 ? ␅
    @+88620  [ 88620] drink    q21 ? before
    @+90063  [ 90063] dubbel   q18 ? ␅
    @+90063  [ 90063] dubbel   q19 ? before
    @+93430  [ 93430] eet      q16 ? ␅
    @+93430  [ 93430] eet      q17 ? before
    @+99737  [ 99737] ex       q4  ? ␅
    @+99737  [ 99737] ex       q5  ? before
    @+199812 [199812] lijm     q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #950 🥳 30 ⏱️ 0:00:33.566855

🤔 30 attempts
📜 1 sessions

    @       [    0] aa     
    @+47381 [47381] dis    q2  ? ␅
    @+47381 [47381] dis    q3  ? after
    @+60084 [60084] face   q6  ? ␅
    @+60084 [60084] face   q7  ? after
    @+61620 [61620] fen    q12 ? ␅
    @+61620 [61620] fen    q13 ? after
    @+62018 [62018] feudal q16 ? ␅
    @+62018 [62018] feudal q17 ? after
    @+62216 [62216] fickle q18 ? ␅
    @+62216 [62216] fickle q19 ? after
    @+62263 [62263] fiddle q22 ? ␅
    @+62263 [62263] fiddle q23 ? after
    @+62290 [62290] fidge  q24 ? ␅
    @+62290 [62290] fidge  q25 ? after
    @+62293 [62293] fidget q28 ? ␅
    @+62293 [62293] fidget q29 ? it
    @+62293 [62293] fidget done. it
    @+62303 [62303] fido   q26 ? ␅
    @+62303 [62303] fido   q27 ? before
    @+62315 [62315] field  q20 ? ␅
    @+62315 [62315] field  q21 ? before
    @+62424 [62424] fila   q14 ? ␅
    @+62424 [62424] fila   q15 ? before
    @+63240 [63240] flag   q10 ? ␅
    @+63240 [63240] flag   q11 ? before
    @+66440 [66440] french q8  ? ␅
    @+66440 [66440] french q9  ? before
    @+72800 [72800] gremmy q4  ? ␅
    @+72800 [72800] gremmy q5  ? before
    @+98218 [98218] mach   q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1376 🥳 6 ⏱️ 0:01:26.647074

📜 1 sessions
💰 score: 9

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:BABKA n n n n n remain:5942
    ⬜⬜⬜⬜⬜ tried:SHOOS n n n n n remain:1451
    ⬜⬜⬜⬜⬜ tried:YUMMY n n n n n remain:584
    ⬜⬜⬜⬜🟨 tried:GRRRL n n n n m remain:83
    ⬜🟩🟩⬜⬜ tried:CLIFF n Y Y n n remain:4
    🟨🟩🟩🟨⬜ tried:ELIDE m Y Y m n remain:1

    Undos used: 4

      1 words remaining
    x 9 unused letters
    = 9 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1519 🥳 19 ⏱️ 0:02:33.608580

📜 1 sessions
💰 score: 9700

    4/6
    PSOAE ⬜⬜⬜⬜🟨
    TIRED 🟨⬜⬜🟨⬜
    LETCH ⬜🟨🟨🟩⬜
    EJECT 🟩🟩🟩🟩🟩
    5/6
    EJECT ⬜⬜⬜⬜⬜
    SLAIN ⬜⬜⬜⬜⬜
    HUMPY ⬜⬜⬜⬜⬜
    FORDO ⬜🟨🟨🟨🟨
    BROOD 🟩🟩🟩🟩🟩
    5/6
    BROOD ⬜⬜⬜⬜⬜
    SETAL 🟨🟨🟨⬜⬜
    INSET ⬜⬜🟨🟨🟩
    GUEST ⬜🟩🟩🟩🟩
    QUEST 🟩🟩🟩🟩🟩
    4/6
    QUEST ⬜⬜🟨⬜⬜
    ADORE ⬜🟨⬜⬜🟩
    GLIDE ⬜🟨⬜🟨🟩
    DELVE 🟩🟩🟩🟩🟩
    Final 1/2
    IVORY 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1496 🥳 score:21 ⏱️ 0:01:13.008367

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. BERTH attempts:6 score:6
2. SNARE attempts:3 score:3
3. QUILT attempts:8 score:8
4. CRONE attempts:4 score:4

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1496 🥳 score:63 ⏱️ 0:03:53.857675

📜 1 sessions

Octordle Classic

1. HARDY attempts:12 score:12
2. OUGHT attempts:10 score:10
3. BRIAR attempts:7 score:7
4. OMBRE attempts:6 score:6
5. LOGIC attempts:9 score:9
6. NOSEY attempts:5 score:5
7. NEVER attempts:11 score:11
8. ALONG attempts:3 score:3

# [squareword.org](squareword.org) 🧩 #1489 🥳 8 ⏱️ 0:03:07.730001

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T A P H
    C O P R A
    A W A I T
    R E C C E
    F R E E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1426 🥳 165 ⏱️ 0:02:28.577477

🤔 166 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 35 chat prompts
🤖 35 dolphin3:latest replies
🔥   5 🥵  11 😎  33 🥶 113 🧊   3

      $1 #166 nearby         100.00°C 🥳 1000‰ ~163 used:0  [162]  source:dolphin3
      $2 #159 adjacent        61.93°C 😱  999‰   ~1 used:0  [0]    source:dolphin3
      $3 #158 vicinity        60.19°C 🔥  997‰   ~2 used:1  [1]    source:dolphin3
      $4 #106 riverside       46.78°C 🔥  994‰  ~11 used:24 [10]   source:dolphin3
      $5 #136 area            46.74°C 🔥  993‰   ~3 used:4  [2]    source:dolphin3
      $6  #68 riverbank       46.12°C 🔥  992‰  ~12 used:26 [11]   source:dolphin3
      $7 #160 proximity       42.94°C 🥵  989‰   ~4 used:0  [3]    source:dolphin3
      $8 #148 neighborhood    39.73°C 🥵  979‰   ~5 used:0  [4]    source:dolphin3
      $9 #163 town            37.13°C 🥵  963‰   ~6 used:0  [5]    source:dolphin3
     $10 #150 location        36.87°C 🥵  959‰   ~7 used:0  [6]    source:dolphin3
     $11  #16 creek           36.68°C 🥵  957‰  ~48 used:17 [47]   source:dolphin3
     $18  #31 river           32.32°C 😎  887‰  ~49 used:3  [48]   source:dolphin3
     $51  #43 escarpment      22.73°C 🥶        ~51 used:0  [50]   source:dolphin3
    $164 #153 sector          -0.29°C 🧊       ~164 used:0  [163]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1459 🥳 300 ⏱️ 0:09:59.353055

🤔 301 attempts
📜 1 sessions
🫧 17 chat sessions
⁉️ 78 chat prompts
🤖 78 dolphin3:latest replies
🔥   4 🥵  20 😎  31 🥶 170 🧊  75

      $1 #301 cancer              100.00°C 🥳 1000‰ ~226 used:0  [225]  source:dolphin3
      $2 #264 cancérologie         50.14°C 🔥  996‰  ~21 used:12 [20]   source:dolphin3
      $3 #230 tabagisme            49.41°C 🔥  995‰  ~22 used:17 [21]   source:dolphin3
      $4 #239 maladie              48.82°C 🔥  994‰  ~20 used:11 [19]   source:dolphin3
      $5 #291 tumeur               45.04°C 🔥  990‰   ~1 used:5  [0]    source:dolphin3
      $6 #269 chimiothérapie       41.93°C 🥵  978‰   ~2 used:1  [1]    source:dolphin3
      $7 #276 sarcome              40.89°C 🥵  976‰   ~3 used:0  [2]    source:dolphin3
      $8 #287 immunothérapie       39.81°C 🥵  971‰   ~4 used:0  [3]    source:dolphin3
      $9 #249 cancérigène          39.46°C 🥵  970‰   ~5 used:1  [4]    source:dolphin3
     $10 #252 tuberculose          39.30°C 🥵  968‰   ~6 used:0  [5]    source:dolphin3
     $11 #281 oncologie            39.21°C 🥵  967‰   ~7 used:0  [6]    source:dolphin3
     $26 #272 oncogène             31.31°C 😎  873‰  ~25 used:0  [24]   source:dolphin3
     $57 #159 traitement           19.57°C 🥶        ~64 used:0  [63]   source:dolphin3
    $227 #183 séquestration        -0.09°C 🧊       ~227 used:0  [226]  source:dolphin3
