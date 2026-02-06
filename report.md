# 2026-02-07

- 🔗 spaceword.org 🧩 2026-02-06 🏁 score 2173 ranked 11.7% 41/350 ⏱️ 2:17:12.591346
- 🔗 alfagok.diginaut.net 🧩 #462 🥳 24 ⏱️ 0:00:36.383411
- 🔗 alphaguess.com 🧩 #929 🥳 30 ⏱️ 0:00:30.960002
- 🔗 dontwordle.com 🧩 #1355 🥳 6 ⏱️ 0:03:02.418891
- 🔗 dictionary.com hurdle 🧩 #1498 🥳 20 ⏱️ 0:03:53.498530
- 🔗 Quordle Classic 🧩 #1475 🥳 score:21 ⏱️ 0:01:13.464948
- 🔗 Octordle Classic 🧩 #1475 🥳 score:60 ⏱️ 0:04:11.562640
- 🔗 squareword.org 🧩 #1468 🥳 9 ⏱️ 0:02:52.871377
- 🔗 cemantle.certitudes.org 🧩 #1405 🥳 19 ⏱️ 0:02:22.048614
- 🔗 cemantix.certitudes.org 🧩 #1438 🥳 94 ⏱️ 0:07:29.185508
- 🔗 Quordle Rescue 🧩 #89 🥳 score:29 ⏱️ 0:01:35.388310

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























# [spaceword.org](spaceword.org) 🧩 2026-02-06 🏁 score 2173 ranked 11.7% 41/350 ⏱️ 2:17:12.591346

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 41/350

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ A I M _ _ _   
      _ _ _ _ _ _ U _ _ _   
      _ _ _ _ W A R _ _ _   
      _ _ _ _ _ G I _ _ _   
      _ _ _ _ K E N _ _ _   
      _ _ _ _ _ N E _ _ _   
      _ _ _ _ M I S _ _ _   
      _ _ _ _ _ Z _ _ _ _   
      _ _ _ _ S E A _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #462 🥳 24 ⏱️ 0:00:36.383411

🤔 24 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199826 [199826] lijm      q0  ? ␅
    @+199826 [199826] lijm      q1  ? after
    @+299731 [299731] schub     q2  ? ␅
    @+299731 [299731] schub     q3  ? after
    @+324297 [324297] sub       q6  ? ␅
    @+324297 [324297] sub       q7  ? after
    @+330480 [330480] televisie q10 ? ␅
    @+330480 [330480] televisie q11 ? after
    @+333688 [333688] thesis    q14 ? ␅
    @+333688 [333688] thesis    q15 ? after
    @+334094 [334094] ti        q16 ? ␅
    @+334094 [334094] ti        q17 ? after
    @+334411 [334411] tijd      q22 ? ␅
    @+334411 [334411] tijd      q23 ? it
    @+334411 [334411] tijd      done. it
    @+335492 [335492] tjingel   q20 ? ␅
    @+335492 [335492] tjingel   q21 ? before
    @+336892 [336892] toetsing  q8  ? ␅
    @+336892 [336892] toetsing  q9  ? before
    @+349499 [349499] vakantie  q4  ? ␅
    @+349499 [349499] vakantie  q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #929 🥳 30 ⏱️ 0:00:30.960002

🤔 30 attempts
📜 1 sessions

    @        [     0] aa         
    @+98219  [ 98219] mach       q0  ? ␅
    @+98219  [ 98219] mach       q1  ? after
    @+147372 [147372] rhotic     q2  ? ␅
    @+147372 [147372] rhotic     q3  ? after
    @+171642 [171642] ta         q4  ? ␅
    @+171642 [171642] ta         q5  ? after
    @+182007 [182007] un         q6  ? ␅
    @+182007 [182007] un         q7  ? after
    @+189269 [189269] vicar      q8  ? ␅
    @+189269 [189269] vicar      q9  ? after
    @+192873 [192873] whir       q10 ? ␅
    @+192873 [192873] whir       q11 ? after
    @+194698 [194698] worship    q12 ? ␅
    @+194698 [194698] worship    q13 ? after
    @+194806 [194806] wrath      q20 ? ␅
    @+194806 [194806] wrath      q21 ? after
    @+194855 [194855] wrest      q22 ? ␅
    @+194855 [194855] wrest      q23 ? after
    @+194860 [194860] wrestle    q28 ? ␅
    @+194860 [194860] wrestle    q29 ? it
    @+194860 [194860] wrestle    done. it
    @+194868 [194868] wretch     q26 ? ␅
    @+194868 [194868] wretch     q27 ? before
    @+194890 [194890] wriggliest q24 ? ␅
    @+194890 [194890] wriggliest q25 ? before
    @+194925 [194925] writ       q18 ? ␅
    @+194925 [194925] writ       q19 ? before
    @+195155 [195155] xylems     q16 ? ␅
    @+195155 [195155] xylems     q17 ? before
    @+195612 [195612] yo         q15 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1355 🥳 6 ⏱️ 0:03:02.418891

📜 1 sessions
💰 score: 21

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:CIRRI n n n n n remain:5436
    ⬜⬜⬜⬜⬜ tried:MAMBA n n n n n remain:2094
    ⬜⬜⬜⬜⬜ tried:LOTTO n n n n n remain:450
    ⬜⬜⬜⬜⬜ tried:VUGGY n n n n n remain:122
    ⬜🟨🟩⬜⬜ tried:FEEZE n m Y n n remain:16
    ⬜⬜🟩🟩⬜ tried:WHEEN n n Y Y n remain:3

    Undos used: 4

      3 words remaining
    x 7 unused letters
    = 21 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1498 🥳 20 ⏱️ 0:03:53.498530

📜 2 sessions
💰 score: 9600

    5/6
    STORE 🟩⬜⬜🟨🟨
    SAVER 🟩⬜⬜🟩🟨
    SHRED 🟩⬜🟩🟩⬜
    SIREN 🟩⬜🟩🟩⬜
    SCREW 🟩🟩🟩🟩🟩
    3/6
    SCREW ⬜⬜⬜🟨⬜
    DEALT ⬜🟩🟩⬜🟩
    MEANT 🟩🟩🟩🟩🟩
    5/6
    MEANT ⬜⬜⬜⬜⬜
    FOURS ⬜⬜⬜⬜🟨
    SILKY 🟨🟩⬜⬜🟩
    GIPSY ⬜🟩🟨🟨🟩
    WISPY 🟩🟩🟩🟩🟩
    6/6
    WISPY ⬜🟨⬜⬜⬜
    ALIKE 🟨⬜🟩⬜⬜
    CHINA ⬜⬜🟩⬜🟩
    TAIGA ⬜⬜🟩⬜🟩
    MOIRA ⬜🟨🟩⬜🟩
    OUIJA 🟩🟩🟩🟩🟩
    Final 1/2
    INDEX 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1475 🥳 score:21 ⏱️ 0:01:13.464948

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. APPLE attempts:7 score:7
2. RAZOR attempts:5 score:5
3. CAMEL attempts:6 score:6
4. MOTIF attempts:3 score:3

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1475 🥳 score:60 ⏱️ 0:04:11.562640

📜 1 sessions

Octordle Classic

1. JOINT attempts:8 score:8
2. LARVA attempts:11 score:11
3. EXTOL attempts:4 score:4
4. TENOR attempts:3 score:3
5. NATAL attempts:5 score:5
6. CURVE attempts:11 score:12
7. GROWN attempts:7 score:7
8. CRONE attempts:10 score:10

# [squareword.org](squareword.org) 🧩 #1468 🥳 9 ⏱️ 0:02:52.871377

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟨 🟩 🟩 🟩
    🟩 🟨 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C A R E
    H O N O R
    A M O U R
    L E D G E
    T R E E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1405 🥳 19 ⏱️ 0:02:22.048614

🤔 20 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 4 chat prompts
🤖 4 glm-4.7-flash:latest replies
🥵  1 😎  4 🥶 13 🧊  1

     $1 #20 gear         100.00°C 🥳 1000‰ ~19 used:0 [18]  source:glm
     $2 #10 pedal         31.11°C 🥵  911‰  ~1 used:3 [0]   source:glm
     $3 #13 crank         30.18°C 😎  882‰  ~2 used:0 [1]   source:glm
     $4 #12 brake         27.63°C 😎  789‰  ~3 used:0 [2]   source:glm
     $5  #2 bicycle       27.07°C 😎  768‰  ~4 used:1 [3]   source:glm
     $6 #16 axle          26.15°C 😎  711‰  ~5 used:0 [4]   source:glm
     $7 #18 cycle         18.78°C 🥶        ~6 used:0 [5]   source:glm
     $8 #19 drive         18.41°C 🥶        ~7 used:0 [6]   source:glm
     $9 #14 ride          16.71°C 🥶        ~8 used:0 [7]   source:glm
    $10 #11 accelerator   15.87°C 🥶        ~9 used:0 [8]   source:glm
    $11 #17 chain         12.55°C 🥶       ~10 used:0 [9]   source:glm
    $12 #15 transport     10.32°C 🥶       ~11 used:0 [10]  source:glm
    $13  #1 algorithm      9.93°C 🥶       ~12 used:0 [11]  source:glm
    $20  #6 gravestone    -1.15°C 🧊       ~20 used:0 [19]  source:glm

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1438 🥳 94 ⏱️ 0:07:29.185508

🤔 95 attempts
📜 1 sessions
🫧 15 chat sessions
⁉️ 24 chat prompts
🤖 11 dolphin3:latest replies
🤖 13 glm-4.7-flash:latest replies
🔥  3 🥵  8 😎 21 🥶 51 🧊 11

     $1 #95 dramatique     100.00°C 🥳 1000‰ ~84 used:0  [83]  source:dolphin3
     $2 #36 drame           64.10°C 🔥  998‰  ~5 used:13 [4]   source:dolphin3
     $3 #87 tragédie        58.56°C 🔥  997‰  ~1 used:9  [0]   source:dolphin3
     $4 #23 protagoniste    50.78°C 🔥  993‰  ~6 used:17 [5]   source:glm     
     $5 #51 scène           47.42°C 🥵  988‰  ~9 used:3  [8]   source:dolphin3
     $6 #27 intrigue        43.28°C 🥵  965‰ ~11 used:4  [10]  source:glm     
     $7 #26 comédie         43.27°C 🥵  964‰  ~7 used:2  [6]   source:glm     
     $8 #90 catastrophe     41.76°C 🥵  955‰  ~8 used:2  [7]   source:dolphin3
     $9 #44 dénouement      41.75°C 🥵  954‰  ~2 used:1  [1]   source:dolphin3
    $10 #58 narration       41.02°C 🥵  947‰  ~3 used:1  [2]   source:dolphin3
    $11 #16 personnage      39.67°C 🥵  923‰ ~10 used:3  [9]   source:glm     
    $13 #92 péripétie       38.45°C 😎  899‰ ~12 used:0  [11]  source:dolphin3
    $34 #70 rivalité        26.72°C 🥶       ~33 used:0  [32]  source:dolphin3
    $85 #53 développement   -0.01°C 🧊       ~85 used:0  [84]  source:dolphin3

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #89 🥳 score:29 ⏱️ 0:01:35.388310

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. CANON attempts:7 score:7
2. FAUNA attempts:8 score:8
3. FLEET attempts:5 score:5
4. SMITH attempts:9 score:9
