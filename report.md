# 2026-02-19

- 🔗 spaceword.org 🧩 2026-02-18 🏁 score 2173 ranked 3.6% 13/363 ⏱️ 0:44:54.929463
- 🔗 alfagok.diginaut.net 🧩 #474 🥳 18 ⏱️ 0:00:33.358956
- 🔗 alphaguess.com 🧩 #941 🥳 38 ⏱️ 0:00:38.023615
- 🔗 dontwordle.com 🧩 #1367 🥳 6 ⏱️ 0:02:08.839685
- 🔗 dictionary.com hurdle 🧩 #1510 😦 17 ⏱️ 0:03:07.195048
- 🔗 Quordle Classic 🧩 #1487 🥳 score:22 ⏱️ 0:01:18.087884
- 🔗 Octordle Classic 🧩 #1487 🥳 score:64 ⏱️ 0:04:04.889643
- 🔗 squareword.org 🧩 #1480 🥳 9 ⏱️ 0:02:54.608644
- 🔗 cemantle.certitudes.org 🧩 #1417 🥳 308 ⏱️ 0:03:49.828149
- 🔗 cemantix.certitudes.org 🧩 #1450 🥳 138 ⏱️ 0:04:36.636599

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



































# [spaceword.org](spaceword.org) 🧩 2026-02-18 🏁 score 2173 ranked 3.6% 13/363 ⏱️ 0:44:54.929463

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 13/363

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ J _ C O A E V A L   
      _ U _ A N I _ _ Y O   
      _ T U Y E R S _ _ X   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #474 🥳 18 ⏱️ 0:00:33.358956

🤔 18 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+199816 [199816] lijm       q0  ? ␅
    @+199816 [199816] lijm       q1  ? after
    @+299721 [299721] schub      q2  ? ␅
    @+299721 [299721] schub      q3  ? after
    @+311891 [311891] spier      q8  ? ␅
    @+311891 [311891] spier      q9  ? after
    @+318084 [318084] stem       q10 ? ␅
    @+318084 [318084] stem       q11 ? after
    @+318822 [318822] sterven    q16 ? ␅
    @+318822 [318822] sterven    q17 ? it
    @+318822 [318822] sterven    done. it
    @+319568 [319568] stimulatie q14 ? ␅
    @+319568 [319568] stimulatie q15 ? before
    @+321058 [321058] straat     q12 ? ␅
    @+321058 [321058] straat     q13 ? before
    @+324287 [324287] sub        q6  ? ␅
    @+324287 [324287] sub        q7  ? before
    @+349489 [349489] vakantie   q4  ? ␅
    @+349489 [349489] vakantie   q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #941 🥳 38 ⏱️ 0:00:38.023615

🤔 38 attempts
📜 1 sessions

    @       [    0] aa             
    @+47381 [47381] dis            q2  ? ␅
    @+47381 [47381] dis            q3  ? after
    @+60084 [60084] face           q6  ? ␅
    @+60084 [60084] face           q7  ? after
    @+63240 [63240] flag           q10 ? ␅
    @+63240 [63240] flag           q11 ? after
    @+64837 [64837] foment         q12 ? ␅
    @+64837 [64837] foment         q13 ? after
    @+65636 [65636] format         q14 ? ␅
    @+65636 [65636] format         q15 ? after
    @+65729 [65729] forsake        q20 ? ␅
    @+65729 [65729] forsake        q21 ? after
    @+65747 [65747] fort           q22 ? ␅
    @+65747 [65747] fort           q23 ? after
    @+65765 [65765] fortifications q26 ? ␅
    @+65765 [65765] fortifications q27 ? after
    @+65772 [65772] fortis         q28 ? ␅
    @+65772 [65772] fortis         q29 ? after
    @+65775 [65775] fortissimos    q32 ? ␅
    @+65775 [65775] fortissimos    q33 ? after
    @+65776 [65776] fortitude      q36 ? ␅
    @+65776 [65776] fortitude      q37 ? it
    @+65776 [65776] fortitude      done. it
    @+65777 [65777] fortitudes     q34 ? ␅
    @+65777 [65777] fortitudes     q35 ? before
    @+65778 [65778] fortnight      q30 ? ␅
    @+65778 [65778] fortnight      q31 ? before
    @+65782 [65782] fortress       q24 ? ␅
    @+65782 [65782] fortress       q25 ? before
    @+65825 [65825] foss           q19 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1367 🥳 6 ⏱️ 0:02:08.839685

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:GABBA n n n n n remain:5913
    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:3209
    ⬜⬜⬜⬜⬜ tried:PEWEE n n n n n remain:907
    ⬜⬜⬜⬜⬜ tried:YUKKY n n n n n remain:242
    ⬜⬜🟩⬜⬜ tried:CHOLO n n Y n n remain:18
    🟩🟨🟩⬜⬜ tried:STOTS Y m Y n n remain:1

    Undos used: 3

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1510 😦 17 ⏱️ 0:03:07.195048

📜 2 sessions
💰 score: 4980

    4/6
    SERAI 🟩🟨⬜⬜🟨
    SNIDE 🟩⬜🟨⬜🟩
    SIEGE 🟩🟩🟩⬜🟩
    SIEVE 🟩🟩🟩🟩🟩
    4/6
    SIEVE ⬜⬜⬜⬜⬜
    LOFTY ⬜🟩⬜⬜⬜
    MONAD ⬜🟩⬜🟨🟩
    BOARD 🟩🟩🟩🟩🟩
    3/6
    BOARD ⬜⬜🟨🟨🟨
    DARES 🟩🟨🟨🟨⬜
    DREAM 🟩🟩🟩🟩🟩
    4/6
    DREAM ⬜🟨🟨🟨⬜
    SCARE ⬜⬜🟨🟨🟨
    TAPER ⬜🟨⬜🟩🟩
    ANGER 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜🟩🟩🟩🟩
    ????? ⬜🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1487 🥳 score:22 ⏱️ 0:01:18.087884

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. MODEL attempts:4 score:4
2. LOAMY attempts:6 score:6
3. GUMMY attempts:7 score:7
4. SLEET attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1487 🥳 score:64 ⏱️ 0:04:04.889643

📜 1 sessions

Octordle Classic

1. WHICH attempts:12 score:12
2. RODEO attempts:9 score:9
3. OCEAN attempts:4 score:4
4. ICILY attempts:5 score:5
5. PUTTY attempts:6 score:6
6. SALSA attempts:10 score:10
7. ADOPT attempts:7 score:7
8. BLISS attempts:11 score:11

# [squareword.org](squareword.org) 🧩 #1480 🥳 9 ⏱️ 0:02:54.608644

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟩 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S M A S H
    C O U P E
    A R D O R
    L A I R D
    P L O T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1417 🥳 308 ⏱️ 0:03:49.828149

🤔 309 attempts
📜 1 sessions
🫧 14 chat sessions
⁉️ 71 chat prompts
🤖 71 dolphin3:latest replies
😱   1 🔥   1 🥵   6 😎  22 🥶 260 🧊  18

      $1 #309 incorrect         100.00°C 🥳 1000‰ ~291 used:0  [290]  source:dolphin3
      $2 #305 erroneous          75.75°C 😱  999‰   ~1 used:1  [0]    source:dolphin3
      $3 #307 faulty             57.62°C 🔥  995‰   ~2 used:0  [1]    source:dolphin3
      $4 #301 unfounded          45.52°C 🥵  976‰   ~7 used:4  [6]    source:dolphin3
      $5 #306 fallacious         44.04°C 🥵  966‰   ~3 used:0  [2]    source:dolphin3
      $6 #171 assumptive         37.65°C 🥵  913‰  ~27 used:42 [26]   source:dolphin3
      $7 #304 baseless           37.64°C 🥵  912‰   ~4 used:2  [3]    source:dolphin3
      $8 #302 unjustified        37.28°C 🥵  905‰   ~5 used:2  [4]    source:dolphin3
      $9 #297 unwarranted        37.14°C 🥵  901‰   ~6 used:2  [5]    source:dolphin3
     $10 #308 groundless         34.50°C 😎  850‰   ~8 used:0  [7]    source:dolphin3
     $11 #186 presumptuous       32.46°C 😎  790‰  ~29 used:17 [28]   source:dolphin3
     $12  #60 prescient          30.27°C 😎  693‰  ~30 used:31 [29]   source:dolphin3
     $32 #108 statistical        23.11°C 🥶        ~41 used:2  [40]   source:dolphin3
    $292 #287 evident            -0.52°C 🧊       ~292 used:0  [291]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1450 🥳 138 ⏱️ 0:04:36.636599

🤔 139 attempts
📜 1 sessions
🫧 12 chat sessions
⁉️ 57 chat prompts
🤖 57 dolphin3:latest replies
😱  1 🥵  7 😎 16 🥶 80 🧊 34

      $1 #139 idéologie        100.00°C 🥳 1000‰ ~105 used:0  [104]  source:dolphin3
      $2 #135 idéologique       78.94°C 😱  999‰   ~1 used:2  [0]    source:dolphin3
      $3  #83 dogme             57.29°C 🥵  986‰  ~24 used:39 [23]   source:dolphin3
      $4  #75 dogmatisme        55.81°C 🥵  975‰  ~22 used:26 [21]   source:dolphin3
      $5  #82 dogmatique        55.28°C 🥵  968‰  ~17 used:11 [16]   source:dolphin3
      $6  #73 conservatisme     52.90°C 🥵  939‰  ~18 used:11 [17]   source:dolphin3
      $7  #74 fondamentalisme   52.21°C 🥵  926‰  ~19 used:11 [18]   source:dolphin3
      $8  #79 réactionnaire     52.13°C 🥵  924‰  ~20 used:11 [19]   source:dolphin3
      $9  #95 doctrinaire       51.99°C 🥵  919‰  ~21 used:11 [20]   source:dolphin3
     $10  #66 traditionalisme   50.88°C 😎  883‰   ~2 used:1  [1]    source:dolphin3
     $11  #96 doctrine          50.03°C 😎  863‰   ~3 used:1  [2]    source:dolphin3
     $12  #56 conformisme       49.48°C 😎  843‰   ~4 used:1  [3]    source:dolphin3
     $26  #67 héritage          36.77°C 🥶        ~32 used:0  [31]   source:dolphin3
    $106  #23 évaluation        -0.39°C 🧊       ~106 used:0  [105]  source:dolphin3
