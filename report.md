# 2026-04-03

- 🔗 spaceword.org 🧩 2026-04-02 🏁 score 2173 ranked 5.4% 18/332 ⏱️ 1:28:05.573753
- 🔗 alfagok.diginaut.net 🧩 #517 🥳 40 ⏱️ 0:01:04.199874
- 🔗 alphaguess.com 🧩 #984 🥳 30 ⏱️ 0:00:34.791441
- 🔗 dontwordle.com 🧩 #1410 🥳 6 ⏱️ 0:01:43.808018
- 🔗 dictionary.com hurdle 🧩 #1553 🥳 18 ⏱️ 0:05:14.922634
- 🔗 Quordle Classic 🧩 #1530 🥳 score:26 ⏱️ 0:02:12.335633
- 🔗 Octordle Classic 🧩 #1530 🥳 score:63 ⏱️ 0:04:15.465749
- 🔗 squareword.org 🧩 #1523 🥳 8 ⏱️ 0:02:53.656262
- 🔗 cemantle.certitudes.org 🧩 #1460 🥳 94 ⏱️ 0:00:55.097589
- 🔗 cemantix.certitudes.org 🧩 #1493 🥳 28 ⏱️ 0:00:28.975230

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

































# [spaceword.org](spaceword.org) 🧩 2026-04-02 🏁 score 2173 ranked 5.4% 18/332 ⏱️ 1:28:05.573753

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 18/332

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ J _ S U R I M I   
      _ N I D E _ U _ E R   
      _ _ G A Z E B O _ K   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #517 🥳 40 ⏱️ 0:01:04.199874

🤔 40 attempts
📜 1 sessions

    @        [     0] &-teken       
    @+49841  [ 49841] boks          q6  ? ␅
    @+49841  [ 49841] boks          q7  ? after
    @+74754  [ 74754] dc            q8  ? ␅
    @+74754  [ 74754] dc            q9  ? after
    @+87213  [ 87213] draag         q10 ? ␅
    @+87213  [ 87213] draag         q11 ? after
    @+93430  [ 93430] eet           q12 ? ␅
    @+93430  [ 93430] eet           q13 ? after
    @+94959  [ 94959] eiwit         q16 ? ␅
    @+94959  [ 94959] eiwit         q17 ? after
    @+95079  [ 95079] el            q22 ? ␅
    @+95079  [ 95079] el            q23 ? after
    @+95129  [ 95129] elco          q34 ? ␅
    @+95129  [ 95129] elco          q35 ? after
    @+95135  [ 95135] elders        q38 ? ␅
    @+95135  [ 95135] elders        q39 ? it
    @+95135  [ 95135] elders        done. it
    @+95145  [ 95145] elect         q36 ? ␅
    @+95145  [ 95145] elect         q37 ? before
    @+95175  [ 95175] elektriciteit q24 ? ␅
    @+95175  [ 95175] elektriciteit q25 ? before
    @+95288  [ 95288] elektro       q20 ? ␅
    @+95288  [ 95288] elektro       q21 ? before
    @+95751  [ 95751] elo           q18 ? ␅
    @+95751  [ 95751] elo           q19 ? before
    @+96565  [ 96565] energiek      q14 ? ␅
    @+96565  [ 96565] energiek      q15 ? before
    @+99733  [ 99733] ex            q4  ? ␅
    @+99733  [ 99733] ex            q5  ? before
    @+199805 [199805] lijm          q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #984 🥳 30 ⏱️ 0:00:34.791441

🤔 30 attempts
📜 1 sessions

    @        [     0] aa          
    @+98216  [ 98216] mach        q0  ? ␅
    @+98216  [ 98216] mach        q1  ? after
    @+122777 [122777] parr        q4  ? ␅
    @+122777 [122777] parr        q5  ? after
    @+135068 [135068] proper      q6  ? ␅
    @+135068 [135068] proper      q7  ? after
    @+140516 [140516] rec         q8  ? ␅
    @+140516 [140516] rec         q9  ? after
    @+143940 [143940] reminisce   q10 ? ␅
    @+143940 [143940] reminisce   q11 ? after
    @+145192 [145192] res         q12 ? ␅
    @+145192 [145192] res         q13 ? after
    @+145657 [145657] resolve     q16 ? ␅
    @+145657 [145657] resolve     q17 ? after
    @+145842 [145842] rest        q18 ? ␅
    @+145842 [145842] rest        q19 ? after
    @+145975 [145975] restrict    q20 ? ␅
    @+145975 [145975] restrict    q21 ? after
    @+145993 [145993] restring    q26 ? ␅
    @+145993 [145993] restring    q27 ? after
    @+146004 [146004] restructure q28 ? ␅
    @+146004 [146004] restructure q29 ? it
    @+146004 [146004] restructure done. it
    @+146012 [146012] restudies   q24 ? ␅
    @+146012 [146012] restudies   q25 ? before
    @+146048 [146048] resume      q22 ? ␅
    @+146048 [146048] resume      q23 ? before
    @+146124 [146124] ret         q14 ? ␅
    @+146124 [146124] ret         q15 ? before
    @+147371 [147371] rhumb       q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1410 🥳 6 ⏱️ 0:01:43.808018

📜 1 sessions
💰 score: 208

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:HEEZE n n n n n remain:5957
    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:3303
    ⬜⬜⬜⬜⬜ tried:CONVO n n n n n remain:1017
    ⬜⬜⬜⬜⬜ tried:FLUFF n n n n n remain:335
    🟨⬜⬜⬜⬜ tried:ABAKA m n n n n remain:83
    ⬜🟩⬜⬜🟩 tried:DADDY n Y n n Y remain:26

    Undos used: 4

      26 words remaining
    x 8 unused letters
    = 208 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1553 🥳 18 ⏱️ 0:05:14.922634

📜 2 sessions
💰 score: 9800

    5/6
    RATES 🟨⬜⬜🟨⬜
    FORCE ⬜🟨🟨⬜🟩
    PRONE ⬜🟩🟩⬜🟩
    DROVE 🟨🟩🟩⬜🟩
    ERODE 🟩🟩🟩🟩🟩
    5/6
    ERODE ⬜🟨⬜⬜⬜
    SARIN 🟩🟨🟨⬜⬜
    SCART 🟩⬜🟩🟩⬜
    SHARP 🟩🟩🟩🟩⬜
    SHARK 🟩🟩🟩🟩🟩
    3/6
    SHARK 🟩⬜⬜🟨⬜
    SUPER 🟩🟨⬜🟨🟨
    SERUM 🟩🟩🟩🟩🟩
    3/6
    SERUM ⬜🟩⬜⬜⬜
    LEGIT ⬜🟩⬜🟨🟨
    DEITY 🟩🟩🟩🟩🟩
    Final 2/2
    NAMER ⬜🟩🟩🟩🟩
    GAMER 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1530 🥳 score:26 ⏱️ 0:02:12.335633

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. PINEY attempts:5 score:5
2. TRUSS attempts:7 score:7
3. HALVE attempts:6 score:6
4. SPOOF attempts:8 score:8

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1530 🥳 score:63 ⏱️ 0:04:15.465749

📜 1 sessions

Octordle Classic

1. AVIAN attempts:5 score:5
2. BAGEL attempts:6 score:6
3. FUSSY attempts:11 score:11
4. UNFIT attempts:12 score:12
5. DUVET attempts:8 score:8
6. REFIT attempts:10 score:10
7. ABBEY attempts:7 score:7
8. NUDGE attempts:4 score:4

# [squareword.org](squareword.org) 🧩 #1523 🥳 8 ⏱️ 0:02:53.656262

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟨 🟨 🟨 🟨
    🟩 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P E A R S
    A P R O N
    R O G U E
    A C U T E
    S H E E R

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1460 🥳 94 ⏱️ 0:00:55.097589

🤔 95 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 14 chat prompts
🤖 14 dolphin3:latest replies
😱  1 🔥  1 🥵  4 😎 24 🥶 61 🧊  3

     $1 #95 supplement     100.00°C 🥳 1000‰ ~92 used:0 [91]  source:dolphin3
     $2 #86 augment         56.31°C 😱  999‰  ~1 used:2 [0]   source:dolphin3
     $3 #87 bolster         39.36°C 🔥  993‰  ~2 used:1 [1]   source:dolphin3
     $4 #90 fortify         35.44°C 🥵  976‰  ~3 used:0 [2]   source:dolphin3
     $5 #64 boost           35.03°C 🥵  974‰  ~5 used:2 [4]   source:dolphin3
     $6 #82 enhance         33.03°C 🥵  949‰  ~4 used:1 [3]   source:dolphin3
     $7 #31 diet            31.74°C 🥵  927‰  ~6 used:7 [5]   source:dolphin3
     $8 #35 nutrition       30.57°C 😎  890‰ ~25 used:2 [24]  source:dolphin3
     $9 #84 strengthen      30.43°C 😎  885‰  ~7 used:0 [6]   source:dolphin3
    $10 #77 nutrient        29.60°C 😎  858‰  ~8 used:0 [7]   source:dolphin3
    $11 #74 micronutrient   29.58°C 😎  857‰  ~9 used:0 [8]   source:dolphin3
    $12 #92 expand          29.39°C 😎  846‰ ~10 used:0 [9]   source:dolphin3
    $32 #28 cleanse         21.10°C 🥶       ~31 used:0 [30]  source:dolphin3
    $93  #9 volcano         -0.77°C 🧊       ~93 used:0 [92]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1493 🥳 28 ⏱️ 0:00:28.975230

🤔 29 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 9 chat prompts
🤖 9 dolphin3:latest replies
🔥  1 🥵  6 😎  3 🥶 10 🧊  8

     $1 #29 synthèse       100.00°C 🥳 1000‰ ~21 used:0 [20]  source:dolphin3
     $2 #27 analyse         65.42°C 🔥  998‰  ~1 used:0 [0]   source:dolphin3
     $3 #16 bibliographie   45.43°C 🥵  980‰  ~7 used:5 [6]   source:dolphin3
     $4 #21 résumé          45.28°C 🥵  979‰  ~4 used:2 [3]   source:dolphin3
     $5 #15 conclusion      41.74°C 🥵  968‰  ~6 used:3 [5]   source:dolphin3
     $6 #22 sommaire        39.63°C 🥵  950‰  ~5 used:2 [4]   source:dolphin3
     $7 #23 annexe          38.68°C 🥵  938‰  ~2 used:1 [1]   source:dolphin3
     $8 #25 documentation   38.25°C 🥵  934‰  ~3 used:0 [2]   source:dolphin3
     $9 #26 référence       33.49°C 😎  848‰  ~8 used:0 [7]   source:dolphin3
    $10 #17 glossaire       32.58°C 😎  812‰  ~9 used:0 [8]   source:dolphin3
    $11 #11 chapitre        27.78°C 😎  532‰ ~10 used:2 [9]   source:dolphin3
    $12 #28 plan            22.12°C 🥶       ~12 used:0 [11]  source:dolphin3
    $13 #19 postface        20.18°C 🥶       ~13 used:0 [12]  source:dolphin3
    $22  #2 arbre           -7.03°C 🧊       ~22 used:0 [21]  source:dolphin3
