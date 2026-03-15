# 2026-03-16

- 🔗 alfagok.diginaut.net 🧩 #499 🥳 22 ⏱️ 0:00:44.118255
- 🔗 alphaguess.com 🧩 #966 🥳 24 ⏱️ 0:00:32.591428
- 🔗 dontwordle.com 🧩 #1392 😳 6 ⏱️ 0:00:29.039412
- 🔗 dictionary.com hurdle 🧩 #1535 😦 6 ⏱️ 0:01:11.759474
- 🔗 Quordle Classic 🧩 #1512 🥳 score:21 ⏱️ 0:01:27.472004
- 🔗 Octordle Classic 🧩 #1512 😦 score:65 ⏱️ 0:04:06.660589
- 🔗 squareword.org 🧩 #1505 🥳 8 ⏱️ 0:02:11.630386
- 🔗 cemantle.certitudes.org 🧩 #1442 🥳 29 ⏱️ 0:00:21.138454
- 🔗 cemantix.certitudes.org 🧩 #1475 🥳 127 ⏱️ 0:02:15.023776

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















# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #499 🥳 22 ⏱️ 0:00:44.118255

🤔 22 attempts
📜 1 sessions

    @        [     0] &-teken         
    @+1      [     1] &-tekens        
    @+2      [     2] -cijferig       
    @+3      [     3] -e-mail         
    @+99737  [ 99737] ex              q2  ? ␅
    @+99737  [ 99737] ex              q3  ? after
    @+149642 [149642] huishoud        q4  ? ␅
    @+149642 [149642] huishoud        q5  ? after
    @+151616 [151616] hé              q12 ? ␅
    @+151616 [151616] hé              q13 ? after
    @+152401 [152401] ijs             q14 ? ␅
    @+152401 [152401] ijs             q15 ? after
    @+152702 [152702] ijssportcentrum q18 ? ␅
    @+152702 [152702] ijssportcentrum q19 ? after
    @+152804 [152804] ijzer           q20 ? ␅
    @+152804 [152804] ijzer           q21 ? it
    @+152804 [152804] ijzer           done. it
    @+153002 [153002] illusie         q16 ? ␅
    @+153002 [153002] illusie         q17 ? before
    @+153604 [153604] in              q10 ? ␅
    @+153604 [153604] in              q11 ? before
    @+162026 [162026] jaar            q8  ? ␅
    @+162026 [162026] jaar            q9  ? before
    @+174540 [174540] kind            q6  ? ␅
    @+174540 [174540] kind            q7  ? before
    @+199609 [199609] lij             q0  ? ␅
    @+199609 [199609] lij             q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #966 🥳 24 ⏱️ 0:00:32.591428

🤔 24 attempts
📜 1 sessions

    @       [    0] aa      
    @+1     [    1] aah     
    @+2     [    2] aahed   
    @+3     [    3] aahing  
    @+11764 [11764] back    q6  ? ␅
    @+11764 [11764] back    q7  ? after
    @+13802 [13802] be      q10 ? ␅
    @+13802 [13802] be      q11 ? after
    @+15758 [15758] bewrap  q12 ? ␅
    @+15758 [15758] bewrap  q13 ? after
    @+16728 [16728] bios    q14 ? ␅
    @+16728 [16728] bios    q15 ? after
    @+17210 [17210] blab    q16 ? ␅
    @+17210 [17210] blab    q17 ? after
    @+17459 [17459] blarney q18 ? ␅
    @+17459 [17459] blarney q19 ? after
    @+17475 [17475] blast   q22 ? ␅
    @+17475 [17475] blast   q23 ? it
    @+17475 [17475] blast   done. it
    @+17585 [17585] bleak   q20 ? ␅
    @+17585 [17585] bleak   q21 ? before
    @+17715 [17715] blind   q8  ? ␅
    @+17715 [17715] blind   q9  ? before
    @+23682 [23682] camp    q4  ? ␅
    @+23682 [23682] camp    q5  ? before
    @+47381 [47381] dis     q2  ? ␅
    @+47381 [47381] dis     q3  ? before
    @+98218 [98218] mach    q0  ? ␅
    @+98218 [98218] mach    q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1392 😳 6 ⏱️ 0:00:29.039412

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    🟨⬜🟨🟨⬜ tried:SERAL m n m m n remain:155
    ⬜🟩🟩⬜🟨 tried:ARAKS n Y Y n m remain:6
    🟩🟩🟩🟩🟩 tried:BRASH Y Y Y Y Y remain:0
    ⬛⬛⬛⬛⬛ tried:????? remain:0
    ⬛⬛⬛⬛⬛ tried:????? remain:0
    ⬛⬛⬛⬛⬛ tried:????? remain:0

    Undos used: 0

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1535 😦 6 ⏱️ 0:01:11.759474

📜 1 sessions
💰 score: 80

    6/6
    ????? 🟨⬜⬜🟩⬜
    ????? 🟨🟨⬜🟩⬜
    ????? ⬜🟩⬜🟩🟩
    ????? ⬜🟩⬜🟩🟩
    ????? ⬜🟩🟩🟩🟩
    ????? ⬜🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1512 🥳 score:21 ⏱️ 0:01:27.472004

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. MURKY attempts:6 score:6
2. AGENT attempts:3 score:3
3. SONIC attempts:5 score:5
4. ALARM attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1512 😦 score:65 ⏱️ 0:04:06.660589

📜 1 sessions

Octordle Classic

1. _ULLY -ABCDEFHIKMNOPRSTW attempts:13 score:-1
2. CHEER attempts:8 score:8
3. MINTY attempts:6 score:6
4. NUTTY attempts:5 score:5
5. SMEAR attempts:7 score:7
6. SWOOP attempts:10 score:10
7. WHIFF attempts:11 score:11
8. SKILL attempts:4 score:4

# [squareword.org](squareword.org) 🧩 #1505 🥳 8 ⏱️ 0:02:11.630386

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟨 🟨 🟨 🟨 🟩
    🟩 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C R A P
    A R O M A
    L A B O R
    E V E N S
    S E D G E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1442 🥳 29 ⏱️ 0:00:21.138454

🤔 30 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 6 chat prompts
🤖 6 dolphin3:latest replies
🔥  3 🥵  7 😎  6 🥶 11 🧊  2

     $1 #30 praise         100.00°C 🥳 1000‰ ~28 used:0 [27]  source:dolphin3
     $2 #20 admiration      63.10°C 🔥  997‰  ~3 used:2 [2]   source:dolphin3
     $3 #19 acclaim         62.57°C 🔥  996‰  ~1 used:1 [0]   source:dolphin3
     $4 #26 compliments     58.21°C 🔥  993‰  ~2 used:0 [1]   source:dolphin3
     $5 #25 adulation       53.45°C 🥵  989‰  ~4 used:0 [3]   source:dolphin3
     $6 #12 applause        52.36°C 🥵  986‰ ~10 used:2 [9]   source:dolphin3
     $7 #21 adoration       47.35°C 🥵  977‰  ~5 used:0 [4]   source:dolphin3
     $8 #29 gratitude       44.38°C 🥵  968‰  ~6 used:0 [5]   source:dolphin3
     $9 #17 ovation         43.62°C 🥵  964‰  ~7 used:0 [6]   source:dolphin3
    $10 #27 esteem          38.72°C 🥵  934‰  ~8 used:0 [7]   source:dolphin3
    $11 #22 applaud         38.50°C 🥵  932‰  ~9 used:0 [8]   source:dolphin3
    $12 #24 enthusiasm      34.44°C 😎  888‰ ~11 used:0 [10]  source:dolphin3
    $18 #14 performance     19.84°C 🥶       ~17 used:0 [16]  source:dolphin3
    $29 #10 volcano         -0.41°C 🧊       ~29 used:0 [28]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1475 🥳 127 ⏱️ 0:02:15.023776

🤔 128 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 37 chat prompts
🤖 37 dolphin3:latest replies
🔥  2 🥵  8 😎 44 🥶 58 🧊 15

      $1 #128 infrastructure        100.00°C 🥳 1000‰ ~113 used:0  [112]  source:dolphin3
      $2  #31 développement          57.45°C 🔥  998‰   ~6 used:42 [5]    source:dolphin3
      $3 #109 interconnexion         49.82°C 🔥  993‰   ~3 used:13 [2]    source:dolphin3
      $4 #122 technologie            46.06°C 🥵  984‰   ~1 used:1  [0]    source:dolphin3
      $5  #71 modernisation          44.49°C 🥵  976‰  ~53 used:12 [52]   source:dolphin3
      $6  #55 renforcement           44.32°C 🥵  972‰   ~9 used:7  [8]    source:dolphin3
      $7  #52 amélioration           42.96°C 🥵  960‰   ~7 used:5  [6]    source:dolphin3
      $8 #112 stratégique            41.99°C 🥵  953‰   ~4 used:2  [3]    source:dolphin3
      $9 #114 technologique          41.07°C 🥵  943‰   ~5 used:2  [4]    source:dolphin3
     $10 #108 coopération            39.58°C 🥵  928‰   ~2 used:1  [1]    source:dolphin3
     $11  #33 intégration            38.62°C 🥵  915‰   ~8 used:6  [7]    source:dolphin3
     $12 #113 synergie               37.53°C 😎  896‰  ~10 used:0  [9]    source:dolphin3
     $56  #12 éducation              23.16°C 🥶        ~55 used:3  [54]   source:dolphin3
    $114  #19 examen                 -0.97°C 🧊       ~114 used:0  [113]  source:dolphin3
