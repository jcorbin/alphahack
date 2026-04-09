# 2026-04-10

- 🔗 spaceword.org 🧩 2026-04-09 🏁 score 2173 ranked 4.0% 13/327 ⏱️ 0:26:23.935869
- 🔗 alfagok.diginaut.net 🧩 #524 🥳 36 ⏱️ 0:00:41.671922
- 🔗 alphaguess.com 🧩 #991 🥳 26 ⏱️ 0:01:28.680467
- 🔗 dontwordle.com 🧩 #1417 🥳 6 ⏱️ 0:01:10.839537
- 🔗 dictionary.com hurdle 🧩 #1560 🥳 16 ⏱️ 0:04:03.073193
- 🔗 Quordle Classic 🧩 #1537 🥳 score:29 ⏱️ 0:01:50.729210
- 🔗 Octordle Classic 🧩 #1537 🥳 score:60 ⏱️ 0:04:00.563092
- 🔗 squareword.org 🧩 #1530 🥳 7 ⏱️ 0:01:53.200631
- 🔗 cemantle.certitudes.org 🧩 #1467 🥳 102 ⏱️ 0:00:57.934229
- 🔗 cemantix.certitudes.org 🧩 #1500 😦 1375 ⏱️ 8:38:03.488491

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








































# [spaceword.org](spaceword.org) 🧩 2026-04-09 🏁 score 2173 ranked 4.0% 13/327 ⏱️ 0:26:23.935869

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 13/327

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ D _ K _ _ W I L E   
      _ U M I A Q _ _ E N   
      _ H _ R E I F I E D   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #524 🥳 36 ⏱️ 0:00:41.671922

🤔 36 attempts
📜 1 sessions

    @        [     0] &-teken  
    @+99737  [ 99737] ex       q4  ? ␅
    @+99737  [ 99737] ex       q5  ? after
    @+149640 [149640] huishoud q6  ? ␅
    @+149640 [149640] huishoud q7  ? after
    @+174538 [174538] kind     q8  ? ␅
    @+174538 [174538] kind     q9  ? after
    @+187068 [187068] kromme   q10 ? ␅
    @+187068 [187068] kromme   q11 ? after
    @+193269 [193269] lat      q12 ? ␅
    @+193269 [193269] lat      q13 ? after
    @+196435 [196435] leraars  q14 ? ␅
    @+196435 [196435] leraars  q15 ? after
    @+196728 [196728] letter   q20 ? ␅
    @+196728 [196728] letter   q21 ? after
    @+196886 [196886] leugen   q22 ? ␅
    @+196886 [196886] leugen   q23 ? after
    @+196923 [196923] leuke    q26 ? ␅
    @+196923 [196923] leuke    q27 ? after
    @+196948 [196948] leun     q28 ? ␅
    @+196948 [196948] leun     q29 ? after
    @+196951 [196951] leunen   q34 ? ␅
    @+196951 [196951] leunen   q35 ? it
    @+196951 [196951] leunen   done. it
    @+196956 [196956] leuning  q30 ? ␅
    @+196956 [196956] leuning  q31 ? before
    @+196974 [196974] leur     q24 ? ␅
    @+196974 [196974] leur     q25 ? before
    @+197082 [197082] levens   q18 ? ␅
    @+197082 [197082] levens   q19 ? before
    @+197913 [197913] li       q17 ? before

# [alphaguess.com](alphaguess.com) 🧩 #991 🥳 26 ⏱️ 0:01:28.680467

🤔 26 attempts
📜 1 sessions

    @        [     0] aa           
    @+1      [     1] aah          
    @+2      [     2] aahed        
    @+3      [     3] aahing       
    @+98216  [ 98216] mach         q0  ? ␅
    @+98216  [ 98216] mach         q1  ? after
    @+147371 [147371] rhumb        q2  ? ␅
    @+147371 [147371] rhumb        q3  ? after
    @+159483 [159483] slop         q6  ? ␅
    @+159483 [159483] slop         q7  ? after
    @+165525 [165525] stick        q8  ? ␅
    @+165525 [165525] stick        q9  ? after
    @+168577 [168577] sue          q10 ? ␅
    @+168577 [168577] sue          q11 ? after
    @+170084 [170084] surf         q12 ? ␅
    @+170084 [170084] surf         q13 ? after
    @+170176 [170176] surpass      q20 ? ␅
    @+170176 [170176] surpass      q21 ? after
    @+170202 [170202] surprise     q24 ? ␅
    @+170202 [170202] surprise     q25 ? it
    @+170202 [170202] surprise     done. it
    @+170227 [170227] surrebutters q22 ? ␅
    @+170227 [170227] surrebutters q23 ? before
    @+170277 [170277] survival     q18 ? ␅
    @+170277 [170277] survival     q19 ? before
    @+170468 [170468] swamp        q16 ? ␅
    @+170468 [170468] swamp        q17 ? before
    @+170857 [170857] switch       q14 ? ␅
    @+170857 [170857] switch       q15 ? before
    @+171636 [171636] ta           q4  ? ␅
    @+171636 [171636] ta           q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1417 🥳 6 ⏱️ 0:01:10.839537

📜 1 sessions
💰 score: 56

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:KUDZU n n n n n remain:7272
    ⬜⬜⬜⬜⬜ tried:MAMMA n n n n n remain:3338
    ⬜⬜⬜⬜⬜ tried:BOOBS n n n n n remain:730
    ⬜⬜⬜⬜⬜ tried:JINNI n n n n n remain:208
    ⬜🟨⬜⬜⬜ tried:XYLYL n m n n n remain:38
    ⬜⬜🟨⬜🟩 tried:CHEVY n n m n Y remain:8

    Undos used: 1

      8 words remaining
    x 7 unused letters
    = 56 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1560 🥳 16 ⏱️ 0:04:03.073193

📜 1 sessions
💰 score: 10000

    3/6
    MARSE ⬜🟨⬜⬜🟨
    DEALT 🟨🟩🟨🟨⬜
    PEDAL 🟩🟩🟩🟩🟩
    4/6
    PEDAL ⬜⬜⬜🟩🟩
    CORAL ⬜🟨⬜🟩🟩
    SHOAL ⬜⬜🟨🟩🟩
    OFFAL 🟩🟩🟩🟩🟩
    4/6
    OFFAL ⬜⬜⬜⬜🟨
    SILTY ⬜⬜🟨⬜⬜
    BLUED 🟩🟩⬜🟨🟩
    BLEND 🟩🟩🟩🟩🟩
    4/6
    BLEND ⬜⬜⬜⬜⬜
    APORT ⬜⬜🟩🟨⬜
    CROWS 🟩🟩🟩⬜⬜
    CROCK 🟩🟩🟩🟩🟩
    Final 1/2
    SPACE 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1537 🥳 score:29 ⏱️ 0:01:50.729210

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. PUPPY attempts:5 score:5
2. TRADE attempts:8 score:8
3. BRAND attempts:7 score:7
4. KNOCK attempts:9 score:9

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1537 🥳 score:60 ⏱️ 0:04:00.563092

📜 1 sessions

Octordle Classic

1. CHORE attempts:6 score:6
2. CHEAP attempts:9 score:9
3. ABATE attempts:10 score:10
4. GLARE attempts:11 score:11
5. GRAPE attempts:8 score:8
6. POUCH attempts:7 score:7
7. UNSET attempts:4 score:4
8. SUPER attempts:5 score:5

# [squareword.org](squareword.org) 🧩 #1530 🥳 7 ⏱️ 0:01:53.200631

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C H I C K
    R A D I I
    O V E R T
    R E A C T
    E S S A Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1467 🥳 102 ⏱️ 0:00:57.934229

🤔 103 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 16 chat prompts
🤖 16 dolphin3:latest replies
🔥  3 🥵  3 😎 10 🥶 82 🧊  4

      $1 #103 exhaust           100.00°C 🥳 1000‰  ~99 used:0 [98]   source:dolphin3
      $2  #94 engine             48.09°C 🔥  994‰   ~3 used:3 [2]    source:dolphin3
      $3  #98 camshaft           48.05°C 🔥  993‰   ~2 used:2 [1]    source:dolphin3
      $4  #95 cylinder           47.16°C 🔥  990‰   ~1 used:0 [0]    source:dolphin3
      $5 #102 crankcase          45.57°C 🥵  985‰   ~4 used:0 [3]    source:dolphin3
      $6  #90 motor              42.21°C 🥵  973‰   ~5 used:1 [4]    source:dolphin3
      $7  #97 piston             41.65°C 🥵  966‰   ~6 used:0 [5]    source:dolphin3
      $8  #32 amplifier          32.33°C 😎  773‰  ~16 used:5 [15]   source:dolphin3
      $9  #31 ammeter            32.14°C 😎  763‰  ~15 used:4 [14]   source:dolphin3
     $10  #96 fuel               31.92°C 😎  752‰   ~7 used:0 [6]    source:dolphin3
     $11  #66 insulation         31.65°C 😎  732‰  ~11 used:2 [10]   source:dolphin3
     $12  #99 air                30.96°C 😎  700‰   ~8 used:0 [7]    source:dolphin3
     $18  #30 reverberation      24.01°C 🥶        ~20 used:0 [19]   source:dolphin3
    $100   #6 literature         -0.18°C 🧊       ~100 used:0 [99]   source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1500 😦 1375 ⏱️ 8:38:03.488491

🤔 1374 attempts
📜 2 sessions
🫧 201 chat sessions
⁉️ 929 chat prompts
🤖 11 lfm2:latest replies
🤖 134 qwen3.5:9b replies
🤖 137 llama3.1:8b replies
🤖 25 gpt-oss:20b replies
🤖 200 dolphin3:latest replies
🤖 4 glm-4.7-flash:latest replies
🤖 47 kimi-k2.5:cloud replies
🤖 63 nemotron-3-nano:latest replies
🤖 130 qwen3.5:27b replies
🤖 17 gemma4:31b replies
🤖 69 llama3.2:latest replies
🤖 92 gemma3:27b replies
😦 😱    1 🔥    8 🥵   62 😎  356 🥶  834 🧊  113

       $1  #277 projet                 46.13°C 😱  999‰   ~65 used:916 [64]    source:dolphin3   
       $2  #725 innovant               44.12°C 🔥  998‰  ~424 used:287 [423]   source:dolphin3   
       $3  #183 accompagnement         41.97°C 🔥  997‰  ~423 used:280 [422]   source:dolphin3   
       $4 #1052 structurant            40.70°C 🔥  996‰   ~29 used:71  [28]    source:kimi       
       $5  #276 potentiel              40.56°C 🔥  995‰   ~30 used:71  [29]    source:dolphin3   
       $6  #801 accompagner            40.11°C 🔥  994‰   ~31 used:71  [30]    source:qwen3.5:27b
       $7  #514 concrétisation         39.85°C 🔥  993‰   ~32 used:71  [31]    source:gemma3     
       $8  #800 valoriser              39.71°C 🔥  992‰   ~33 used:71  [32]    source:qwen3.5:27b
       $9  #704 concrétiser            39.56°C 🔥  990‰   ~34 used:71  [33]    source:dolphin3   
      $10  #809 favoriser              39.48°C 🥵  989‰   ~35 used:8   [34]    source:qwen3.5:27b
      $11   #98 entreprise             38.21°C 🥵  987‰  ~427 used:43  [426]   source:dolphin3   
      $72  #859 investir               30.28°C 😎  898‰   ~66 used:0   [65]    source:qwen3.5:27b
     $428   #33 rural                  18.57°C 🥶        ~429 used:0   [428]   source:dolphin3   
    $1262 #1214 raisonnement           -0.04°C 🧊       ~1262 used:0   [1261]  source:llama3.1   
