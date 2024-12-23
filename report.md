# 2026-03-29

- 🔗 spaceword.org 🧩 2026-03-28 🏁 score 2173 ranked 7.7% 25/324 ⏱️ 5:56:48.279806
- 🔗 alfagok.diginaut.net 🧩 #512 🥳 28 ⏱️ 0:00:41.046939
- 🔗 alphaguess.com 🧩 #979 🥳 40 ⏱️ 0:00:47.982970
- 🔗 dontwordle.com 🧩 #1405 🥳 6 ⏱️ 0:02:04.208469
- 🔗 dictionary.com hurdle 🧩 #1548 🥳 18 ⏱️ 0:02:58.784516
- 🔗 Quordle Classic 🧩 #1525 🥳 score:18 ⏱️ 0:01:20.751793
- 🔗 Octordle Classic 🧩 #1525 🥳 score:60 ⏱️ 0:04:21.140612
- 🔗 squareword.org 🧩 #1518 🥳 8 ⏱️ 0:02:20.041236
- 🔗 cemantle.certitudes.org 🧩 #1455 🥳 837 ⏱️ 1:01:09.178341
- 🔗 cemantix.certitudes.org 🧩 #1488 🥳 88 ⏱️ 0:01:27.716527

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




























# [spaceword.org](spaceword.org) 🧩 2026-03-28 🏁 score 2173 ranked 7.7% 25/324 ⏱️ 5:56:48.279806

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 25/324

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ G I E _ _ _   
      _ _ _ _ _ _ V _ _ _   
      _ _ _ _ R E Z _ _ _   
      _ _ _ _ E _ O _ _ _   
      _ _ _ _ B _ N _ _ _   
      _ _ _ _ U T E _ _ _   
      _ _ _ _ K A S _ _ _   
      _ _ _ _ E _ _ _ _ _   
      _ _ _ _ R U B _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #512 🥳 28 ⏱️ 0:00:41.046939

🤔 28 attempts
📜 1 sessions

    @        [     0] &-teken       
    @+2      [     2] -cijferig     
    @+99737  [ 99737] ex            q2  ? ␅
    @+99737  [ 99737] ex            q3  ? after
    @+149642 [149642] huishoud      q4  ? ␅
    @+149642 [149642] huishoud      q5  ? after
    @+174540 [174540] kind          q6  ? ␅
    @+174540 [174540] kind          q7  ? after
    @+180732 [180732] koel          q10 ? ␅
    @+180732 [180732] koel          q11 ? after
    @+182135 [182135] kom           q14 ? ␅
    @+182135 [182135] kom           q15 ? after
    @+182165 [182165] komeet        q24 ? ␅
    @+182165 [182165] komeet        q25 ? after
    @+182176 [182176] komen         q26 ? ␅
    @+182176 [182176] komen         q27 ? it
    @+182176 [182176] komen         done. it
    @+182197 [182197] komiek        q22 ? ␅
    @+182197 [182197] komiek        q23 ? before
    @+182264 [182264] komodovaranen q20 ? ␅
    @+182264 [182264] komodovaranen q21 ? before
    @+182392 [182392] koning        q18 ? ␅
    @+182392 [182392] koning        q19 ? before
    @+182848 [182848] kool          q16 ? ␅
    @+182848 [182848] kool          q17 ? before
    @+183863 [183863] koraal        q12 ? ␅
    @+183863 [183863] koraal        q13 ? before
    @+187070 [187070] kromme        q8  ? ␅
    @+187070 [187070] kromme        q9  ? before
    @+199608 [199608] lij           q0  ? ␅
    @+199608 [199608] lij           q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #979 🥳 40 ⏱️ 0:00:47.982970

🤔 40 attempts
📜 1 sessions

    @       [    0] aa            
    @+5876  [ 5876] angel         q10 ? ␅
    @+5876  [ 5876] angel         q11 ? after
    @+8323  [ 8323] ar            q12 ? ␅
    @+8323  [ 8323] ar            q13 ? after
    @+9341  [ 9341] as            q14 ? ␅
    @+9341  [ 9341] as            q15 ? after
    @+10553 [10553] audient       q16 ? ␅
    @+10553 [10553] audient       q17 ? after
    @+11149 [11149] ava           q18 ? ␅
    @+11149 [11149] ava           q19 ? after
    @+11297 [11297] avirulent     q24 ? ␅
    @+11297 [11297] avirulent     q25 ? after
    @+11367 [11367] awake         q26 ? ␅
    @+11367 [11367] awake         q27 ? after
    @+11402 [11402] awes          q28 ? ␅
    @+11402 [11402] awes          q29 ? after
    @+11403 [11403] awesome       q38 ? ␅
    @+11403 [11403] awesome       q39 ? it
    @+11403 [11403] awesome       done. it
    @+11404 [11404] awesomely     q36 ? ␅
    @+11404 [11404] awesomely     q37 ? before
    @+11406 [11406] awesomenesses q34 ? ␅
    @+11406 [11406] awesomenesses q35 ? before
    @+11409 [11409] awful         q32 ? ␅
    @+11409 [11409] awful         q33 ? before
    @+11418 [11418] awkward       q30 ? ␅
    @+11418 [11418] awkward       q31 ? before
    @+11443 [11443] ax            q20 ? ␅
    @+11443 [11443] ax            q21 ? before
    @+11763 [11763] back          q9  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1405 🥳 6 ⏱️ 0:02:04.208469

📜 1 sessions
💰 score: 21

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:7346
    ⬜⬜⬜⬜⬜ tried:MAGMA n n n n n remain:2845
    ⬜⬜⬜⬜⬜ tried:JEEZE n n n n n remain:1208
    ⬜⬜⬜⬜⬜ tried:BUBUS n n n n n remain:203
    ⬜🟨⬜⬜⬜ tried:XYLYL n m n n n remain:55
    ⬜⬜🟨🟨⬜ tried:CRYPT n n m m n remain:3

    Undos used: 3

      3 words remaining
    x 7 unused letters
    = 21 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1548 🥳 18 ⏱️ 0:02:58.784516

📜 1 sessions
💰 score: 9800

    5/6
    AISLE ⬜⬜⬜⬜🟩
    TRONE ⬜🟩🟩🟩🟩
    CRONE ⬜🟩🟩🟩🟩
    DRONE ⬜🟩🟩🟩🟩
    PRONE 🟩🟩🟩🟩🟩
    3/6
    PRONE 🟨⬜🟨⬜⬜
    TYPOS ⬜⬜🟩🟩⬜
    BIPOD 🟩🟩🟩🟩🟩
    4/6
    BIPOD ⬜⬜🟩⬜⬜
    SUPRA ⬜⬜🟩⬜🟩
    ALPHA 🟨⬜🟩⬜🟩
    KAPPA 🟩🟩🟩🟩🟩
    4/6
    KAPPA ⬜⬜⬜⬜⬜
    NOISE 🟨⬜🟨⬜⬜
    TUNIC ⬜⬜🟩🟩🟩
    CYNIC 🟩🟩🟩🟩🟩
    Final 2/2
    STERN ⬜🟨🟨🟨🟨
    ENTER 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1525 🥳 score:18 ⏱️ 0:01:20.751793

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. DELAY attempts:3 score:3
2. STONY attempts:4 score:4
3. MONTH attempts:5 score:5
4. PARTY attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1525 🥳 score:60 ⏱️ 0:04:21.140612

📜 3 sessions

Octordle Classic

1. IRATE attempts:5 score:5
2. DERBY attempts:7 score:7
3. SAFER attempts:11 score:11
4. BRICK attempts:9 score:9
5. STRAP attempts:10 score:10
6. HANDY attempts:8 score:8
7. LOATH attempts:4 score:4
8. LUMPY attempts:6 score:6

# [squareword.org](squareword.org) 🧩 #1518 🥳 8 ⏱️ 0:02:20.041236

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    G R A S P
    R O D E O
    A B O V E
    P I P E S
    E N T R Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1455 🥳 837 ⏱️ 1:01:09.178341

🤔 838 attempts
📜 3 sessions
🫧 78 chat sessions
⁉️ 317 chat prompts
🤖 138 dolphin3:latest replies
🤖 112 llama3.1:8b replies
🤖 38 minicpm-v:latest replies
🤖 16 gpt-oss:20b replies
🤖 7 gemma3:27b replies
🤖 6 qwen3.5:27b replies
🔥   2 🥵  18 😎 109 🥶 693 🧊  15

      $1 #838 conception           100.00°C 🥳 1000‰ ~823 used:0   [822]  source:dolphin3
      $2 #828 gestation             53.05°C 🔥  997‰   ~1 used:4   [0]    source:dolphin3
      $3 #406 conceptualization     48.59°C 🔥  993‰ ~123 used:256 [122]  source:dolphin3
      $4 #820 birth                 46.03°C 🥵  988‰   ~4 used:7   [3]    source:dolphin3
      $5 #835 pregnancy             44.03°C 🥵  983‰   ~2 used:1   [1]    source:dolphin3
      $6 #646 presupposition        43.23°C 🥵  978‰ ~127 used:54  [126]  source:llama3  
      $7 #148 teleology             42.52°C 🥵  973‰ ~129 used:130 [128]  source:dolphin3
      $8 #675 preconception         42.19°C 🥵  970‰  ~37 used:11  [36]   source:llama3  
      $9 #628 idealization          42.17°C 🥵  969‰  ~38 used:11  [37]   source:llama3  
     $10 #787 reproduction          41.67°C 🥵  967‰  ~39 used:11  [38]   source:llama3  
     $11 #837 childbirth            41.38°C 🥵  963‰   ~3 used:0   [2]    source:dolphin3
     $22 #230 determinist           37.29°C 😎  896‰  ~47 used:2   [46]   source:dolphin3
    $131 #614 typology              28.03°C 🥶       ~133 used:0   [132]  source:llama3  
    $824 #567 community             -0.08°C 🧊       ~824 used:0   [823]  source:minicpm 

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1488 🥳 88 ⏱️ 0:01:27.716527

🤔 89 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 11 chat prompts
🤖 11 dolphin3:latest replies
🔥  3 🥵  5 😎 15 🥶 40 🧊 25

     $1 #89 expansion        100.00°C 🥳 1000‰ ~64 used:0 [63]  source:dolphin3
     $2 #74 croissance        54.99°C 🔥  998‰  ~3 used:2 [2]   source:dolphin3
     $3 #88 développement     47.42°C 🔥  996‰  ~1 used:0 [0]   source:dolphin3
     $4 #83 accélération      44.77°C 🔥  994‰  ~2 used:0 [1]   source:dolphin3
     $5 #71 diversification   40.87°C 🥵  986‰  ~5 used:2 [4]   source:dolphin3
     $6 #61 économique        39.78°C 🥵  982‰  ~8 used:5 [7]   source:dolphin3
     $7 #69 investissement    35.53°C 🥵  950‰  ~7 used:4 [6]   source:dolphin3
     $8 #87 dynamisme         33.66°C 🥵  922‰  ~4 used:0 [3]   source:dolphin3
     $9 #64 industrie         33.53°C 🥵  921‰  ~6 used:2 [5]   source:dolphin3
    $10 #65 économie          32.17°C 😎  892‰  ~9 used:0 [8]   source:dolphin3
    $11 #29 capital           30.59°C 😎  841‰ ~22 used:2 [21]  source:dolphin3
    $12 #73 concurrentiel     29.77°C 😎  808‰ ~10 used:0 [9]   source:dolphin3
    $25 #85 attraction        21.27°C 🥶       ~24 used:0 [23]  source:dolphin3
    $65 #21 country           -0.16°C 🧊       ~65 used:0 [64]  source:dolphin3
