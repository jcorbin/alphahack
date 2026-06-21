# 2026-06-22

- 🔗 spaceword.org 🧩 2026-06-21 🏁 score 2168 ranked 30.8% 97/315 ⏱️ 1:06:02.916083
- 🔗 alfagok.diginaut.net 🧩 #597 🥳 22 ⏱️ 0:00:34.242809
- 🔗 alphaguess.com 🧩 #1064 🥳 34 ⏱️ 0:00:43.066947
- 🔗 dontwordle.com 🧩 #1490 🥳 6 ⏱️ 0:02:19.015906
- 🔗 dictionary.com hurdle 🧩 #1633 🥳 16 ⏱️ 0:02:38.644602
- 🔗 Quordle Classic 🧩 #1610 😦 score:28 ⏱️ 0:02:20.259620
- 🔗 squareword.org 🧩 #1603 🥳 8 ⏱️ 0:03:24.555794
- 🔗 cemantle.certitudes.org 🧩 #1540 🥳 159 ⏱️ 0:01:09.052667
- 🔗 cemantix.certitudes.org 🧩 #1573 🥳 152 ⏱️ 0:04:39.929681
- 🔗 Octordle Classic 🧩 #1610 🥳 score:65 ⏱️ 0:04:55.279904
- 🔗 Sedecordle Classic 🧩 #1590 🥳 score:48 ⏱️ 0:14:16.484149

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













# [spaceword.org](spaceword.org) 🧩 2026-06-21 🏁 score 2168 ranked 30.8% 97/315 ⏱️ 1:06:02.916083

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 97/315

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ Z O I C _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ _ F _ V _ _ _   
      _ _ _ D I T E _ _ _   
      _ _ _ _ X _ R _ _ _   
      _ _ _ _ U _ U _ _ _   
      _ _ _ _ R I P _ _ _   
      _ _ _ O E S _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #597 🥳 22 ⏱️ 0:00:34.242809

🤔 22 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199762 [199762] lijm      q0  ? ␅
    @+199762 [199762] lijm      q1  ? after
    @+223523 [223523] mol       q6  ? ␅
    @+223523 [223523] mol       q7  ? after
    @+225968 [225968] mu        q12 ? ␅
    @+225968 [225968] mu        q13 ? after
    @+227740 [227740] naakt     q14 ? ␅
    @+227740 [227740] naakt     q15 ? after
    @+227915 [227915] naar      q20 ? ␅
    @+227915 [227915] naar      q21 ? it
    @+227915 [227915] naar      done. it
    @+228096 [228096] nacht     q18 ? ␅
    @+228096 [228096] nacht     q19 ? before
    @+228502 [228502] nag       q16 ? ␅
    @+228502 [228502] nag       q17 ? before
    @+229540 [229540] natuur    q10 ? ␅
    @+229540 [229540] natuur    q11 ? before
    @+235577 [235577] octrooi   q8  ? ␅
    @+235577 [235577] octrooi   q9  ? before
    @+247633 [247633] op        q4  ? ␅
    @+247633 [247633] op        q5  ? before
    @+299625 [299625] schub     q2  ? ␅
    @+299625 [299625] schub     q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1064 🥳 34 ⏱️ 0:00:43.066947

🤔 34 attempts
📜 1 sessions

    @        [     0] aa        
    @+98214  [ 98214] mach      q0  ? ␅
    @+98214  [ 98214] mach      q1  ? after
    @+109931 [109931] ne        q6  ? ␅
    @+109931 [109931] ne        q7  ? after
    @+111481 [111481] no        q10 ? ␅
    @+111481 [111481] no        q11 ? after
    @+113844 [113844] nu        q12 ? ␅
    @+113844 [113844] nu        q13 ? after
    @+114428 [114428] object    q16 ? ␅
    @+114428 [114428] object    q17 ? after
    @+114570 [114570] obscene   q20 ? ␅
    @+114570 [114570] obscene   q21 ? after
    @+114628 [114628] obsess    q22 ? ␅
    @+114628 [114628] obsess    q23 ? after
    @+114647 [114647] obsidian  q26 ? ␅
    @+114647 [114647] obsidian  q27 ? after
    @+114657 [114657] obsolete  q28 ? ␅
    @+114657 [114657] obsolete  q29 ? after
    @+114662 [114662] obsoletes q30 ? ␅
    @+114662 [114662] obsoletes q31 ? after
    @+114664 [114664] obstacle  q32 ? ␅
    @+114664 [114664] obstacle  q33 ? it
    @+114664 [114664] obstacle  done. it
    @+114666 [114666] obstetric q24 ? ␅
    @+114666 [114666] obstetric q25 ? before
    @+114715 [114715] obtrude   q18 ? ␅
    @+114715 [114715] obtrude   q19 ? before
    @+115011 [115011] od        q14 ? ␅
    @+115011 [115011] od        q15 ? before
    @+116349 [116349] orchard   q9  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1490 🥳 6 ⏱️ 0:02:19.015906

📜 2 sessions
💰 score: 16

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:QUEUE n n n n n remain:5479
    ⬜⬜⬜⬜⬜ tried:MIMIC n n n n n remain:2358
    ⬜⬜⬜⬜⬜ tried:RAGGA n n n n n remain:484
    ⬜🟨⬜⬜⬜ tried:PHPHT n m n n n remain:37
    🟩⬜🟨⬜⬜ tried:HWYLS Y n m n n remain:4
    🟩🟩⬜⬜🟩 tried:HOODY Y Y n n Y remain:2

    Undos used: 4

      2 words remaining
    x 8 unused letters
    = 16 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1633 🥳 16 ⏱️ 0:02:38.644602

📜 1 sessions
💰 score: 10000

    5/6
    ELANS 🟨⬜⬜⬜🟨
    SPIRE 🟨⬜⬜🟨🟨
    ROSET 🟨⬜🟨🟨🟩
    CREST ⬜🟩🟩🟩🟩
    WREST 🟩🟩🟩🟩🟩
    3/6
    WREST ⬜⬜⬜⬜🟨
    PATIO 🟨🟨🟨⬜🟨
    TOPAZ 🟩🟩🟩🟩🟩
    3/6
    TOPAZ ⬜⬜⬜⬜⬜
    RUNIC 🟨🟨🟨⬜⬜
    DRUNK 🟩🟩🟩🟩🟩
    4/6
    DRUNK ⬜⬜⬜🟨⬜
    INSET ⬜🟨⬜🟨⬜
    CANOE ⬜🟨🟨⬜🟨
    GLEAN 🟩🟩🟩🟩🟩
    Final 1/2
    PRINT 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1610 😦 score:28 ⏱️ 0:02:20.259620

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. WAXEN attempts:7 score:7
2. APNEA attempts:3 score:3
3. CHIME attempts:9 score:9
4. WA_ER -CDFGHIKLMNPSTX attempts:9 score:-1

# [squareword.org](squareword.org) 🧩 #1603 🥳 8 ⏱️ 0:03:24.555794

📜 2 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟩
    🟩 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    W A N T S
    A L O H A
    R E V E L
    D R A M A
    S T E E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1540 🥳 159 ⏱️ 0:01:09.052667

🤔 160 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 23 chat prompts
🤖 23 dolphin3:latest replies
😎   8 🥶 142 🧊   9

      $1 #160 beam          100.00°C 🥳 1000‰ ~151 used:0  [150]  source:dolphin3
      $2  #61 floor          35.11°C 😎  846‰   ~8 used:21 [7]    source:dolphin3
      $3 #146 staircase      33.47°C 😎  760‰   ~5 used:4  [4]    source:dolphin3
      $4 #136 ceiling        31.54°C 😎  629‰   ~1 used:1  [0]    source:dolphin3
      $5 #134 wall           31.52°C 😎  627‰   ~4 used:2  [3]    source:dolphin3
      $6 #137 cladding       28.98°C 😎  330‰   ~2 used:1  [1]    source:dolphin3
      $7 #150 chandelier     27.99°C 😎  171‰   ~3 used:0  [2]    source:dolphin3
      $8  #91 tile           27.67°C 😎  107‰   ~7 used:16 [6]    source:dolphin3
      $9  #18 glass          27.38°C 😎   60‰   ~6 used:13 [5]    source:dolphin3
     $10 #118 epoxy          26.96°C 🥶        ~14 used:0  [13]   source:dolphin3
     $11 #141 light          26.76°C 🥶        ~15 used:0  [14]   source:dolphin3
     $12  #42 mirror         26.15°C 🥶         ~9 used:4  [8]    source:dolphin3
     $13  #68 lighting       26.13°C 🥶        ~11 used:2  [10]   source:dolphin3
    $152  #27 change         -0.36°C 🧊       ~152 used:0  [151]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1573 🥳 152 ⏱️ 0:04:39.929681

🤔 153 attempts
📜 1 sessions
🫧 13 chat sessions
⁉️ 61 chat prompts
🤖 61 dolphin3:latest replies
🥵   4 😎  20 🥶 107 🧊  21

      $1 #153 féminin           100.00°C 🥳 1000‰ ~132 used:0  [131]  source:dolphin3
      $2  #77 glamour            36.93°C 🥵  967‰  ~20 used:36 [19]   source:dolphin3
      $3  #98 séduction          34.70°C 🥵  949‰  ~19 used:22 [18]   source:dolphin3
      $4 #111 séducteur          33.03°C 🥵  939‰   ~8 used:13 [7]    source:dolphin3
      $5  #84 élégance           30.04°C 🥵  905‰   ~7 used:11 [6]    source:dolphin3
      $6 #152 fashion            28.03°C 😎  854‰   ~1 used:1  [0]    source:dolphin3
      $7  #71 raffiné            25.61°C 😎  754‰  ~21 used:4  [20]   source:dolphin3
      $8  #66 élégant            25.51°C 😎  747‰  ~22 used:4  [21]   source:dolphin3
      $9 #143 diva               24.87°C 😎  711‰   ~9 used:2  [8]    source:dolphin3
     $10 #104 séduisant          23.92°C 😎  650‰  ~10 used:2  [9]    source:dolphin3
     $11  #25 exceller           23.84°C 😎  642‰  ~24 used:20 [23]   source:dolphin3
     $12 #135 irrésistible       23.56°C 😎  616‰  ~11 used:2  [10]   source:dolphin3
     $26  #35 premier            19.39°C 🥶        ~25 used:7  [24]   source:dolphin3
    $133  #48 perfectionner      -0.24°C 🧊       ~133 used:0  [132]  source:dolphin3

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1610 🥳 score:65 ⏱️ 0:04:55.279904

📜 1 sessions

Octordle Classic

1. DRAWL attempts:8 score:8
2. CARAT attempts:9 score:9
3. RAINY attempts:10 score:10
4. GIANT attempts:11 score:11
5. HONEY attempts:6 score:6
6. CHUNK attempts:5 score:5
7. HARRY attempts:9 score:12
8. TRACT attempts:4 score:4

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1590 🥳 score:48 ⏱️ 0:14:16.484149

📜 3 sessions

Sedecordle Classic sedecordle.com

1. FRONT attempts:5 score:0
2. ORDER attempts:6 score:5
3. SPURN attempts:7 score:0
4. AMPLE attempts:8 score:7
5. FLUFF attempts:14 score:1
6. STEIN attempts:9 score:4
7. OFTEN attempts:11 score:1
8. BUILD attempts:12 score:1
9. FOIST attempts:12 score:1
10. SNOWY attempts:15 score:8
11. SCARF attempts:16 score:1
12. SHIRK attempts:13 score:6
13. LAPSE attempts:3 score:0
14. INFER attempts:10 score:3
15. SHARK attempts:16 score:1
16. KNEED attempts:17 score:9
