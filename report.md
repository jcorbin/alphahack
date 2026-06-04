# 2026-06-05

- 🔗 spaceword.org 🧩 2026-06-04 🏁 score 2173 ranked 13.8% 46/334 ⏱️ 1:59:40.851634
- 🔗 alfagok.diginaut.net 🧩 #580 🥳 22 ⏱️ 0:00:26.373870
- 🔗 alphaguess.com 🧩 #1047 🥳 36 ⏱️ 0:00:43.927149
- 🔗 dontwordle.com 🧩 #1473 😳 6 ⏱️ 0:01:04.863101
- 🔗 dictionary.com hurdle 🧩 #1616 🥳 18 ⏱️ 0:03:04.168441
- 🔗 Quordle Classic 🧩 #1593 🥳 score:25 ⏱️ 0:01:39.564426
- 🔗 Octordle Classic 🧩 #1593 🥳 score:57 ⏱️ 0:02:51.232582
- 🔗 squareword.org 🧩 #1586 🥳 8 ⏱️ 0:01:58.096700
- 🔗 cemantle.certitudes.org 🧩 #1523 🥳 108 ⏱️ 0:01:07.355774
- 🔗 cemantix.certitudes.org 🧩 #1556 🥳 41 ⏱️ 0:00:36.489598

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
























































































# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1585 😦 score:32 ⏱️ 0:02:33.513959

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. GRAPE attempts:8 score:8
2. VALUE attempts:9 score:9
3. YEARN attempts:6 score:6
4. IN_ER -ACDGHLMPSTUVWYZ attempts:9 score:-1









# [spaceword.org](spaceword.org) 🧩 2026-06-04 🏁 score 2173 ranked 13.8% 46/334 ⏱️ 1:59:40.851634

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 46/334

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ J _ P I A S A V A   
      _ O _ O _ _ _ M I D   
      _ T O W E R Y _ A S   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #580 🥳 22 ⏱️ 0:00:26.373870

🤔 22 attempts
📜 2 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199766 [199766] lijm      q0  ? ␅
    @+199766 [199766] lijm      q1  ? after
    @+199766 [199766] lijm      q2  ? ␅
    @+199766 [199766] lijm      q3  ? after
    @+223527 [223527] mol       q8  ? ␅
    @+223527 [223527] mol       q9  ? after
    @+224749 [224749] mor       q16 ? ␅
    @+224749 [224749] mor       q17 ? after
    @+224851 [224851] morgen    q20 ? ␅
    @+224851 [224851] morgen    q21 ? it
    @+224851 [224851] morgen    done. it
    @+225055 [225055] mos       q18 ? ␅
    @+225055 [225055] mos       q19 ? before
    @+225972 [225972] mu        q14 ? ␅
    @+225972 [225972] mu        q15 ? before
    @+229544 [229544] natuur    q12 ? ␅
    @+229544 [229544] natuur    q13 ? before
    @+235581 [235581] octrooi   q10 ? ␅
    @+235581 [235581] octrooi   q11 ? before
    @+247637 [247637] op        q6  ? ␅
    @+247637 [247637] op        q7  ? before
    @+299634 [299634] schub     q4  ? ␅
    @+299634 [299634] schub     q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1047 🥳 36 ⏱️ 0:00:43.927149

🤔 36 attempts
📜 1 sessions

    @       [    0] aa        
    @+47380 [47380] dis       q2  ? ␅
    @+47380 [47380] dis       q3  ? after
    @+53396 [53396] el        q8  ? ␅
    @+53396 [53396] el        q9  ? after
    @+53946 [53946] em        q14 ? ␅
    @+53946 [53946] em        q15 ? after
    @+54421 [54421] emotional q16 ? ␅
    @+54421 [54421] emotional q17 ? after
    @+54421 [54421] emotional q18 ? ␅
    @+54421 [54421] emotional q19 ? after
    @+54473 [54473] empathize q26 ? ␅
    @+54473 [54473] empathize q27 ? after
    @+54479 [54479] empathy   q34 ? ␅
    @+54479 [54479] empathy   q35 ? it
    @+54479 [54479] empathy   done. it
    @+54483 [54483] emperor   q30 ? ␅
    @+54483 [54483] emperor   q31 ? before
    @+54494 [54494] emphasize q28 ? ␅
    @+54494 [54494] emphasize q29 ? before
    @+54522 [54522] emplane   q22 ? ␅
    @+54522 [54522] emplane   q23 ? before
    @+54628 [54628] en        q20 ? ␅
    @+54628 [54628] en        q21 ? before
    @+54917 [54917] end       q12 ? ␅
    @+54917 [54917] end       q13 ? before
    @+56739 [56739] equate    q10 ? ␅
    @+56739 [56739] equate    q11 ? before
    @+60081 [60081] face      q6  ? ␅
    @+60081 [60081] face      q7  ? before
    @+72796 [72796] gremmy    q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1473 😳 6 ⏱️ 0:01:04.863101

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:7419
    ⬜⬜⬜⬜⬜ tried:KOOKY n n n n n remain:3142
    ⬜⬜⬜⬜⬜ tried:BUBUS n n n n n remain:880
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:276
    ⬜⬜⬜🟩🟨 tried:PHPHT n n n Y m remain:2
    🟩🟩🟩🟩🟩 tried:TITHE Y Y Y Y Y remain:0

    Undos used: 2

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1616 🥳 18 ⏱️ 0:03:04.168441

📜 1 sessions
💰 score: 9800

    6/6
    LOSER 🟨⬜⬜⬜⬜
    IMPLY ⬜⬜⬜🟨⬜
    CLUNK ⬜🟨⬜🟨⬜
    BANAL ⬜🟩🟨🟩🟩
    NAVAL 🟩🟩⬜🟩🟩
    NATAL 🟩🟩🟩🟩🟩
    4/6
    NATAL ⬜⬜⬜⬜⬜
    SOWER ⬜⬜⬜🟩🟩
    CIDER 🟩🟨⬜🟩🟩
    CRIER 🟩🟩🟩🟩🟩
    3/6
    CRIER ⬜🟩⬜⬜⬜
    FROGS 🟨🟩⬜🟨⬜
    GRAFT 🟩🟩🟩🟩🟩
    4/6
    GRAFT ⬜⬜⬜⬜⬜
    COSIE ⬜🟨🟨⬜⬜
    SWOUN 🟩🟩🟩⬜⬜
    SWOOP 🟩🟩🟩🟩🟩
    Final 1/2
    MOVIE 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1593 🥳 score:25 ⏱️ 0:01:39.564426

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. RECUR attempts:6 score:6
2. SCOUT attempts:7 score:7
3. SCOWL attempts:4 score:4
4. CHORD attempts:5 score:8

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1593 🥳 score:57 ⏱️ 0:02:51.232582

📜 1 sessions

Octordle Classic

1. STAID attempts:4 score:4
2. COVET attempts:7 score:7
3. PLUCK attempts:9 score:9
4. WISPY attempts:10 score:10
5. REACH attempts:11 score:11
6. SALON attempts:5 score:5
7. STING attempts:3 score:3
8. SHRUB attempts:8 score:8

# [squareword.org](squareword.org) 🧩 #1586 🥳 8 ⏱️ 0:01:58.096700

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B R A S S
    A O R T A
    L O G I N
    S T O L E
    A S T E R

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1523 🥳 108 ⏱️ 0:01:07.355774

🤔 109 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 26 chat prompts
🤖 26 dolphin3:latest replies
🔥  2 🥵  8 😎 21 🥶 72 🧊  5

      $1 #109 violent         100.00°C 🥳 1000‰ ~104 used:0  [103]  source:dolphin3
      $2  #97 brutal           54.12°C 🔥  998‰   ~1 used:0  [0]    source:dolphin3
      $3 #108 vicious          52.52°C 🔥  997‰   ~2 used:0  [1]    source:dolphin3
      $4  #93 savage           47.49°C 🥵  988‰   ~7 used:2  [6]    source:dolphin3
      $5  #95 belligerent      42.09°C 🥵  954‰   ~3 used:0  [2]    source:dolphin3
      $6  #94 barbaric         41.35°C 🥵  941‰   ~4 used:0  [3]    source:dolphin3
      $7  #78 hostile          40.82°C 🥵  937‰   ~9 used:6  [8]    source:dolphin3
      $8  #80 angry            39.99°C 🥵  927‰  ~10 used:6  [9]    source:dolphin3
      $9  #96 bloodthirsty     39.77°C 🥵  926‰   ~5 used:0  [4]    source:dolphin3
     $10 #106 ruthless         38.65°C 🥵  908‰   ~6 used:0  [5]    source:dolphin3
     $11  #84 ferocious        38.50°C 🥵  903‰   ~8 used:3  [7]    source:dolphin3
     $12  #98 cruel            37.69°C 😎  890‰  ~11 used:0  [10]   source:dolphin3
     $33  #60 irritable        25.77°C 🥶        ~38 used:0  [37]   source:dolphin3
    $105   #1 algorithm        -0.91°C 🧊       ~105 used:0  [104]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1556 🥳 41 ⏱️ 0:00:36.489598

🤔 42 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 8 chat prompts
🤖 8 dolphin3:latest replies
🔥  3 🥵  4 😎 14 🥶  9 🧊 11

     $1 #42 partenariat         100.00°C 🥳 1000‰ ~31 used:0 [30]  source:dolphin3
     $2 #37 coopération          70.75°C 🔥  998‰  ~2 used:3 [1]   source:dolphin3
     $3 #23 collaboration        65.61°C 🔥  997‰  ~3 used:4 [2]   source:dolphin3
     $4 #27 développement        55.92°C 🔥  994‰  ~1 used:2 [0]   source:dolphin3
     $5 #13 formation            44.92°C 🥵  957‰  ~7 used:3 [6]   source:dolphin3
     $6 #21 innovation           42.75°C 🥵  941‰  ~6 used:2 [5]   source:dolphin3
     $7 #29 intégration          41.77°C 🥵  927‰  ~4 used:0 [3]   source:dolphin3
     $8 #32 technologique        40.63°C 🥵  915‰  ~5 used:0 [4]   source:dolphin3
     $9 #22 académique           37.49°C 😎  869‰  ~8 used:0 [7]   source:dolphin3
    $10 #26 durable              37.47°C 😎  868‰  ~9 used:0 [8]   source:dolphin3
    $11 #28 interdisciplinaire   33.02°C 😎  767‰ ~10 used:0 [9]   source:dolphin3
    $12 #15 université           31.55°C 😎  715‰ ~11 used:0 [10]  source:dolphin3
    $23 #20 diplôme              17.02°C 🥶       ~22 used:0 [21]  source:dolphin3
    $32 #31 rendement            -1.28°C 🧊       ~32 used:0 [31]  source:dolphin3
