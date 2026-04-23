# 2026-04-24

- 🔗 spaceword.org 🧩 2026-04-23 🏁 score 2173 ranked 5.5% 18/329 ⏱️ 12:24:30.742778
- 🔗 alfagok.diginaut.net 🧩 #538 🥳 44 ⏱️ 0:00:47.031597
- 🔗 alphaguess.com 🧩 #1005 🥳 26 ⏱️ 0:00:29.695098
- 🔗 dontwordle.com 🧩 #1431 🥳 6 ⏱️ 0:01:30.119915
- 🔗 dictionary.com hurdle 🧩 #1574 🥳 23 ⏱️ 0:04:24.777361
- 🔗 Quordle Classic 🧩 #1551 🥳 score:24 ⏱️ 0:01:42.176185
- 🔗 Octordle Classic 🧩 #1551 🥳 score:64 ⏱️ 0:04:15.936941
- 🔗 squareword.org 🧩 #1544 🥳 7 ⏱️ 0:01:37.411461
- 🔗 cemantle.certitudes.org 🧩 #1481 🥳 34 ⏱️ 0:00:28.966652
- 🔗 cemantix.certitudes.org 🧩 #1514 🥳 133 ⏱️ 0:03:52.217802

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






















































# [spaceword.org](spaceword.org) 🧩 2026-04-23 🏁 score 2173 ranked 5.5% 18/329 ⏱️ 12:24:30.742778

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 18/329

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ Y E A _ _ _   
      _ _ _ _ _ _ Q _ _ _   
      _ _ _ _ J E U _ _ _   
      _ _ _ _ A M A _ _ _   
      _ _ _ _ W A E _ _ _   
      _ _ _ _ _ N _ _ _ _   
      _ _ _ _ F A S _ _ _   
      _ _ _ _ _ T _ _ _ _   
      _ _ _ _ D E N _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #538 🥳 44 ⏱️ 0:00:47.031597

🤔 44 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+99736  [ 99736] ex         q4  ? ␅
    @+99736  [ 99736] ex         q5  ? after
    @+149430 [149430] huis       q6  ? ␅
    @+149430 [149430] huis       q7  ? after
    @+174537 [174537] kind       q8  ? ␅
    @+174537 [174537] kind       q9  ? after
    @+187123 [187123] kroniek    q10 ? ␅
    @+187123 [187123] kroniek    q11 ? after
    @+190342 [190342] la         q12 ? ␅
    @+190342 [190342] la         q13 ? after
    @+194898 [194898] lees       q14 ? ␅
    @+194898 [194898] lees       q15 ? after
    @+195314 [195314] leger      q28 ? ␅
    @+195314 [195314] leger      q29 ? after
    @+195633 [195633] leiders    q30 ? ␅
    @+195633 [195633] leiders    q31 ? after
    @+195792 [195792] leken      q32 ? ␅
    @+195792 [195792] leken      q33 ? after
    @+195886 [195886] lel        q34 ? ␅
    @+195886 [195886] lel        q35 ? after
    @+195891 [195891] lelie      q38 ? ␅
    @+195891 [195891] lelie      q39 ? after
    @+195915 [195915] leliewit   q40 ? ␅
    @+195915 [195915] leliewit   q41 ? after
    @+195917 [195917] lelijk     q42 ? ␅
    @+195917 [195917] lelijk     q43 ? it
    @+195917 [195917] lelijk     done. it
    @+195938 [195938] lelletjes  q36 ? ␅
    @+195938 [195938] lelletjes  q37 ? before
    @+195990 [195990] lemsteraak q27 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1005 🥳 26 ⏱️ 0:00:29.695098

🤔 26 attempts
📜 1 sessions

    @       [    0] aa      
    @+1     [    1] aah     
    @+2     [    2] aahed   
    @+3     [    3] aahing  
    @+1398  [ 1398] acrogen q12 ? ␅
    @+1398  [ 1398] acrogen q13 ? after
    @+2097  [ 2097] ads     q14 ? ␅
    @+2097  [ 2097] ads     q15 ? after
    @+2391  [ 2391] aero    q16 ? ␅
    @+2391  [ 2391] aero    q17 ? after
    @+2544  [ 2544] aff     q18 ? ␅
    @+2544  [ 2544] aff     q19 ? after
    @+2666  [ 2666] afford  q20 ? ␅
    @+2666  [ 2666] afford  q21 ? after
    @+2734  [ 2734] afresh  q22 ? ␅
    @+2734  [ 2734] afresh  q23 ? after
    @+2742  [ 2742] after   q24 ? ␅
    @+2742  [ 2742] after   q25 ? it
    @+2742  [ 2742] after   done. it
    @+2802  [ 2802] ag      q10 ? ␅
    @+2802  [ 2802] ag      q11 ? before
    @+5876  [ 5876] angel   q8  ? ␅
    @+5876  [ 5876] angel   q9  ? before
    @+11763 [11763] back    q6  ? ␅
    @+11763 [11763] back    q7  ? before
    @+23681 [23681] camp    q4  ? ␅
    @+23681 [23681] camp    q5  ? before
    @+47380 [47380] dis     q2  ? ␅
    @+47380 [47380] dis     q3  ? before
    @+98216 [98216] mach    q0  ? ␅
    @+98216 [98216] mach    q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1431 🥳 6 ⏱️ 0:01:30.119915

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MAMMA n n n n n remain:6571
    ⬜⬜⬜⬜⬜ tried:DEKED n n n n n remain:2186
    ⬜⬜⬜⬜⬜ tried:FUGUS n n n n n remain:434
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:179
    ⬜⬜⬜⬜🟨 tried:CRWTH n n n n m remain:3
    🟨🟨⬜⬜🟩 tried:PHONO m m n n Y remain:1

    Undos used: 3

      1 words remaining
    x 6 unused letters
    = 6 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1574 🥳 23 ⏱️ 0:04:24.777361

📜 1 sessions
💰 score: 9300

    6/6
    SERAI ⬜⬜⬜🟨⬜
    MALTY ⬜🟩⬜⬜🟩
    PANDY ⬜🟩🟩⬜🟩
    FANCY ⬜🟩🟩⬜🟩
    HANKY ⬜🟩🟩⬜🟩
    NANNY 🟩🟩🟩🟩🟩
    6/6
    NANNY ⬜🟨⬜⬜⬜
    RESAT 🟨🟨🟨🟩⬜
    ESCAR 🟨🟨⬜🟩🟩
    SPEAR 🟩⬜🟩🟩🟩
    SWEAR 🟩⬜🟩🟩🟩
    SMEAR 🟩🟩🟩🟩🟩
    5/6
    SMEAR ⬜⬜🟨⬜🟩
    LONER ⬜🟨⬜🟩🟩
    OFTER 🟩⬜🟩🟩🟩
    OUTER 🟩⬜🟩🟩🟩
    OTTER 🟩🟩🟩🟩🟩
    5/6
    OTTER ⬜🟨🟩⬜⬜
    ICTUS ⬜⬜🟩⬜⬜
    PATLY ⬜🟩🟩⬜🟩
    FATTY ⬜🟩🟩🟩🟩
    BATTY 🟩🟩🟩🟩🟩
    Final 1/2
    SAMBA 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1551 🥳 score:24 ⏱️ 0:01:42.176185

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. LOWLY attempts:7 score:7
2. RELAX attempts:6 score:6
3. BRASS attempts:8 score:8
4. LUNCH attempts:3 score:3

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1551 🥳 score:64 ⏱️ 0:04:15.936941

📜 1 sessions

Octordle Classic

1. ALERT attempts:6 score:6
2. JUICY attempts:10 score:10
3. REBUT attempts:9 score:9
4. FRITZ attempts:12 score:12
5. DROWN attempts:11 score:11
6. MOVER attempts:8 score:8
7. YEAST attempts:3 score:3
8. VALUE attempts:5 score:5

# [squareword.org](squareword.org) 🧩 #1544 🥳 7 ⏱️ 0:01:37.411461

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B L A S T
    E L I T E
    L A D E N
    O M E N S
    W A S T E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1481 🥳 34 ⏱️ 0:00:28.966652

🤔 35 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 10 chat prompts
🤖 10 dolphin3:latest replies
🔥  2 🥵  1 😎  3 🥶 23 🧊  5

     $1 #35 contrary         100.00°C 🥳 1000‰ ~30 used:0 [29]  source:dolphin3
     $2 #25 antithetical      46.86°C 🥵  989‰  ~2 used:3 [1]   source:dolphin3
     $3 #27 contradictory     46.86°C 🔥  990‰  ~1 used:0 [0]   source:dolphin3
     $4 #26 contradiction     45.09°C 🥵  983‰  ~3 used:1 [2]   source:dolphin3
     $5 #34 conflicting       37.08°C 😎  898‰  ~4 used:0 [3]   source:dolphin3
     $6 #24 antithesis        29.01°C 😎  378‰  ~5 used:3 [4]   source:dolphin3
     $7 #19 contrast          27.45°C 😎  130‰  ~6 used:4 [5]   source:dolphin3
     $8 #22 opposition        24.95°C 🥶        ~7 used:4 [6]   source:dolphin3
     $9 #32 dualistic         24.90°C 🥶        ~9 used:0 [8]   source:dolphin3
    $10 #20 dichotomy         24.41°C 🥶        ~8 used:4 [7]   source:dolphin3
    $11 #17 dualism           23.54°C 🥶       ~10 used:1 [9]   source:dolphin3
    $12 #31 discrepancy       20.27°C 🥶       ~11 used:0 [10]  source:dolphin3
    $13 #18 complementarity   19.01°C 🥶       ~12 used:0 [11]  source:dolphin3
    $31  #2 cheeseburger      -0.35°C 🧊       ~31 used:0 [30]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1514 🥳 133 ⏱️ 0:03:52.217802

🤔 134 attempts
📜 1 sessions
🫧 12 chat sessions
⁉️ 55 chat prompts
🤖 55 dolphin3:latest replies
😱  1 🔥  2 🥵  3 😎  8 🥶 66 🧊 53

      $1 #134 affaiblissement  100.00°C 🥳 1000‰  ~81 used:0  [80]   source:dolphin3
      $2  #99 affaiblir         58.69°C 😱  999‰   ~1 used:35 [0]    source:dolphin3
      $3 #108 effritement       53.10°C 🔥  994‰   ~6 used:14 [5]    source:dolphin3
      $4 #104 fragiliser        50.82°C 🔥  993‰   ~5 used:12 [4]    source:dolphin3
      $5 #113 diminution        49.52°C 🥵  987‰   ~2 used:1  [1]    source:dolphin3
      $6 #109 faiblesse         46.03°C 🥵  974‰   ~3 used:0  [2]    source:dolphin3
      $7 #110 atténuer          40.40°C 🥵  900‰   ~4 used:0  [3]    source:dolphin3
      $8 #117 renforcer         38.83°C 😎  866‰   ~7 used:0  [6]    source:dolphin3
      $9 #131 faible            38.81°C 😎  865‰   ~8 used:0  [7]    source:dolphin3
     $10 #101 diminuer          35.56°C 😎  753‰   ~9 used:0  [8]    source:dolphin3
     $11 #123 réduire           32.35°C 😎  578‰  ~10 used:0  [9]    source:dolphin3
     $12 #129 dégrader          32.01°C 😎  543‰  ~11 used:0  [10]   source:dolphin3
     $16 #102 atteindre         25.22°C 🥶        ~24 used:0  [23]   source:dolphin3
     $82 #114 loin              -0.02°C 🧊        ~82 used:0  [81]   source:dolphin3
