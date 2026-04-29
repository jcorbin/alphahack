# 2026-04-30

- 🔗 spaceword.org 🧩 2026-04-29 🏁 score 2173 ranked 3.5% 12/344 ⏱️ 1:28:28.009970
- 🔗 alfagok.diginaut.net 🧩 #544 🥳 38 ⏱️ 0:00:53.239644
- 🔗 alphaguess.com 🧩 #1011 🥳 32 ⏱️ 0:00:38.440425
- 🔗 dontwordle.com 🧩 #1437 🥳 6 ⏱️ 0:01:38.152979
- 🔗 dictionary.com hurdle 🧩 #1580 🥳 14 ⏱️ 0:02:44.913240
- 🔗 Quordle Classic 🧩 #1557 🥳 score:22 ⏱️ 0:01:10.111865
- 🔗 Octordle Classic 🧩 #1557 🥳 score:52 ⏱️ 0:03:18.364592
- 🔗 squareword.org 🧩 #1550 🥳 7 ⏱️ 0:01:53.568578
- 🔗 cemantle.certitudes.org 🧩 #1487 🥳 451 ⏱️ 0:11:30.870922
- 🔗 cemantix.certitudes.org 🧩 #1520 🥳 54 ⏱️ 0:00:41.902014

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




























































# [spaceword.org](spaceword.org) 🧩 2026-04-29 🏁 score 2173 ranked 3.5% 12/344 ⏱️ 1:28:28.009970

📜 6 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 12/344

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ B A P _ _ _   
      _ _ _ _ _ _ R _ _ _   
      _ _ _ _ J O E _ _ _   
      _ _ _ _ E _ T _ _ _   
      _ _ _ _ T I Z _ _ _   
      _ _ _ _ F _ E _ _ _   
      _ _ _ _ O I L _ _ _   
      _ _ _ _ I _ _ _ _ _   
      _ _ _ _ L U V _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #544 🥳 38 ⏱️ 0:00:53.239644

🤔 38 attempts
📜 1 sessions

    @       [    0] &-teken   
    @+49840 [49840] boks      q6  ? ␅
    @+49840 [49840] boks      q7  ? after
    @+74753 [74753] dc        q8  ? ␅
    @+74753 [74753] dc        q9  ? after
    @+87212 [87212] draag     q10 ? ␅
    @+87212 [87212] draag     q11 ? after
    @+87910 [87910] dreg      q18 ? ␅
    @+87910 [87910] dreg      q19 ? after
    @+88137 [88137] drie      q20 ? ␅
    @+88137 [88137] drie      q21 ? after
    @+88371 [88371] driest    q22 ? ␅
    @+88371 [88371] driest    q23 ? after
    @+88489 [88489] drift     q24 ? ␅
    @+88489 [88489] drift     q25 ? after
    @+88522 [88522] drijf     q26 ? ␅
    @+88522 [88522] drijf     q27 ? after
    @+88566 [88566] drijft    q28 ? ␅
    @+88566 [88566] drijft    q29 ? after
    @+88577 [88577] drijfwiel q32 ? ␅
    @+88577 [88577] drijfwiel q33 ? after
    @+88580 [88580] drijven   q36 ? ␅
    @+88580 [88580] drijven   q37 ? it
    @+88580 [88580] drijven   done. it
    @+88583 [88583] drijver   q34 ? ␅
    @+88583 [88583] drijver   q35 ? before
    @+88588 [88588] dril      q30 ? ␅
    @+88588 [88588] dril      q31 ? before
    @+88619 [88619] drink     q16 ? ␅
    @+88619 [88619] drink     q17 ? before
    @+90062 [90062] dubbel    q15 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1011 🥳 32 ⏱️ 0:00:38.440425

🤔 32 attempts
📜 1 sessions

    @        [     0] aa     
    @+98216  [ 98216] mach   q0  ? ␅
    @+98216  [ 98216] mach   q1  ? after
    @+147366 [147366] rhotic q2  ? ␅
    @+147366 [147366] rhotic q3  ? after
    @+171636 [171636] ta     q4  ? ␅
    @+171636 [171636] ta     q5  ? after
    @+174185 [174185] term   q10 ? ␅
    @+174185 [174185] term   q11 ? after
    @+175493 [175493] thrash q12 ? ␅
    @+175493 [175493] thrash q13 ? after
    @+176142 [176142] till   q14 ? ␅
    @+176142 [176142] till   q15 ? after
    @+176477 [176477] tire   q16 ? ␅
    @+176477 [176477] tire   q17 ? after
    @+176642 [176642] tizz   q18 ? ␅
    @+176642 [176642] tizz   q19 ? after
    @+176648 [176648] to     q20 ? ␅
    @+176648 [176648] to     q21 ? after
    @+176726 [176726] tod    q22 ? ␅
    @+176726 [176726] tod    q23 ? after
    @+176768 [176768] toff   q24 ? ␅
    @+176768 [176768] toff   q25 ? after
    @+176774 [176774] toft   q28 ? ␅
    @+176774 [176774] toft   q29 ? after
    @+176776 [176776] tofu   q30 ? ␅
    @+176776 [176776] tofu   q31 ? it
    @+176776 [176776] tofu   done. it
    @+176780 [176780] tog    q26 ? ␅
    @+176780 [176780] tog    q27 ? before
    @+176813 [176813] toilet q9  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1437 🥳 6 ⏱️ 0:01:38.152979

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:YUPPY n n n n n remain:7572
    ⬜⬜⬜⬜⬜ tried:MOTTO n n n n n remain:3052
    ⬜⬜⬜⬜⬜ tried:FRERE n n n n n remain:704
    ⬜⬜⬜⬜⬜ tried:SWISS n n n n n remain:80
    🟨⬜⬜⬜⬜ tried:ADDAX m n n n n remain:16
    ⬜🟨🟩⬜🟩 tried:BLANK n m Y n Y remain:1

    Undos used: 4

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1580 🥳 14 ⏱️ 0:02:44.913240

📜 1 sessions
💰 score: 10200

    5/6
    EARLS 🟨⬜⬜⬜⬜
    TONED ⬜⬜🟨🟨⬜
    BEGUN ⬜🟨⬜⬜🟨
    CHINE 🟨🟨🟨🟨🟩
    NICHE 🟩🟩🟩🟩🟩
    2/6
    NICHE 🟩⬜⬜🟨⬜
    NORTH 🟩🟩🟩🟩🟩
    3/6
    NORTH ⬜🟩⬜⬜⬜
    LODES 🟨🟩🟨⬜🟨
    SOLID 🟩🟩🟩🟩🟩
    2/6
    SOLID 🟩🟨🟨⬜⬜
    SLOTH 🟩🟩🟩🟩🟩
    Final 2/2
    FLORA 🟩🟩🟩🟨⬜
    FLOUR 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1557 🥳 score:22 ⏱️ 0:01:10.111865

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. LOYAL attempts:7 score:7
2. CACHE attempts:4 score:4
3. SWEAT attempts:6 score:6
4. LIGHT attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1557 🥳 score:52 ⏱️ 0:03:18.364592

📜 2 sessions

Octordle Classic

1. RUGBY attempts:10 score:10
2. CACHE attempts:5 score:5
3. ABUSE attempts:8 score:8
4. BELLE attempts:9 score:9
5. AXIOM attempts:7 score:7
6. FAITH attempts:3 score:3
7. DECOR attempts:4 score:4
8. DRYER attempts:6 score:6

# [squareword.org](squareword.org) 🧩 #1550 🥳 7 ⏱️ 0:01:53.568578

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟨 🟨 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S N A P S
    C O B R A
    A V O I D
    N A V E L
    S E E D Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1487 🥳 451 ⏱️ 0:11:30.870922

🤔 452 attempts
📜 1 sessions
🫧 21 chat sessions
⁉️ 105 chat prompts
🤖 105 dolphin3:latest replies
🥵   5 😎  24 🥶 382 🧊  40

      $1 #452 accompany         100.00°C 🥳 1000‰ ~412 used:0  [411]  source:dolphin3
      $2 #246 escort             37.73°C 🥵  978‰  ~26 used:83 [25]   source:dolphin3
      $3 #411 supervise          37.05°C 🥵  975‰   ~2 used:22 [1]    source:dolphin3
      $4 #329 chaperone          34.28°C 🥵  952‰  ~13 used:35 [12]   source:dolphin3
      $5 #451 accompaniment      32.56°C 🥵  923‰   ~1 used:1  [0]    source:dolphin3
      $6 #358 chaperon           32.53°C 🥵  920‰   ~3 used:22 [2]    source:dolphin3
      $7 #146 itinerary          30.58°C 😎  874‰  ~29 used:33 [28]   source:dolphin3
      $8 #418 oversee            30.50°C 😎  869‰   ~4 used:3  [3]    source:dolphin3
      $9 #129 trip               29.00°C 😎  798‰  ~28 used:19 [27]   source:dolphin3
     $10  #79 travel             28.89°C 😎  794‰  ~27 used:10 [26]   source:dolphin3
     $11 #169 guide              28.54°C 😎  769‰  ~22 used:5  [21]   source:dolphin3
     $12 #218 guided             26.59°C 😎  635‰  ~23 used:5  [22]   source:dolphin3
     $31 #203 diary              21.73°C 🥶        ~35 used:0  [34]   source:dolphin3
    $413 #172 itch               -0.16°C 🧊       ~413 used:0  [412]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1520 🥳 54 ⏱️ 0:00:41.902014

🤔 55 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 9 chat prompts
🤖 9 dolphin3:latest replies
😱  1 🔥  1 🥵  6 😎 12 🥶 25 🧊  9

     $1 #55 constitutionnel  100.00°C 🥳 1000‰ ~46 used:0 [45]  source:dolphin3
     $2 #21 constitution      74.70°C 😱  999‰  ~1 used:7 [0]   source:dolphin3
     $3 #29 souveraineté      57.96°C 🔥  995‰  ~2 used:3 [1]   source:dolphin3
     $4 #28 république        47.71°C 🥵  971‰  ~3 used:0 [2]   source:dolphin3
     $5 #19 souverain         46.57°C 🥵  969‰  ~8 used:2 [7]   source:dolphin3
     $6 #32 droit             45.05°C 🥵  960‰  ~4 used:0 [3]   source:dolphin3
     $7 #25 monarchie         44.71°C 🥵  959‰  ~5 used:0 [4]   source:dolphin3
     $8 #24 indépendance      41.13°C 🥵  933‰  ~6 used:0 [5]   source:dolphin3
     $9 #52 état              39.40°C 🥵  912‰  ~7 used:0 [6]   source:dolphin3
    $10 #41 autorité          37.92°C 😎  889‰  ~9 used:0 [8]   source:dolphin3
    $11 #47 législation       37.65°C 😎  883‰ ~10 used:0 [9]   source:dolphin3
    $12 #45 constituant       37.44°C 😎  876‰ ~11 used:0 [10]  source:dolphin3
    $22 #16 héréditaire       23.69°C 🥶       ~21 used:0 [20]  source:dolphin3
    $47  #7 voile             -0.09°C 🧊       ~47 used:0 [46]  source:dolphin3
