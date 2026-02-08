# 2026-02-09

- 🔗 spaceword.org 🧩 2026-02-08 🏁 score 2168 ranked 36.1% 126/349 ⏱️ 0:09:55.328913
- 🔗 alfagok.diginaut.net 🧩 #464 🥳 30 ⏱️ 0:00:38.479325
- 🔗 alphaguess.com 🧩 #931 🥳 36 ⏱️ 0:00:47.031618
- 🔗 dontwordle.com 🧩 #1357 🥳 6 ⏱️ 0:01:34.807903
- 🔗 dictionary.com hurdle 🧩 #1500 😦 18 ⏱️ 0:03:25.848943
- 🔗 Quordle Classic 🧩 #1477 🥳 score:26 ⏱️ 0:02:54.096917
- 🔗 Octordle Classic 🧩 #1477 🥳 score:57 ⏱️ 0:03:26.240944
- 🔗 squareword.org 🧩 #1470 🥳 8 ⏱️ 0:02:05.800316
- 🔗 cemantle.certitudes.org 🧩 #1407 🥳 98 ⏱️ 0:01:45.859178
- 🔗 cemantix.certitudes.org 🧩 #1440 🥳 66 ⏱️ 0:01:07.039724
- 🔗 Quordle Rescue 🧩 #91 🥳 score:22 ⏱️ 0:01:17.191804
- 🔗 Octordle Rescue 🧩 #1477 🥳 score:8 ⏱️ 0:03:47.713218

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

























# [spaceword.org](spaceword.org) 🧩 2026-02-08 🏁 score 2168 ranked 36.1% 126/349 ⏱️ 0:09:55.328913

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 126/349

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ W O _ _ _   
      _ _ T _ _ R A B I _   
      _ _ A Q U I F E R _   
      _ J O I N T _ Y E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #464 🥳 30 ⏱️ 0:00:38.479325

🤔 30 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+49842  [ 49842] boks        q4  ? ␅
    @+49842  [ 49842] boks        q5  ? after
    @+52684  [ 52684] bouw        q12 ? ␅
    @+52684  [ 52684] bouw        q13 ? after
    @+54267  [ 54267] brandstof   q14 ? ␅
    @+54267  [ 54267] brandstof   q15 ? after
    @+55098  [ 55098] brevet      q16 ? ␅
    @+55098  [ 55098] brevet      q17 ? after
    @+55514  [ 55514] brod        q18 ? ␅
    @+55514  [ 55514] brod        q19 ? after
    @+55716  [ 55716] broek       q20 ? ␅
    @+55716  [ 55716] broek       q21 ? after
    @+55771  [ 55771] broekpolder q24 ? ␅
    @+55771  [ 55771] broekpolder q25 ? after
    @+55799  [ 55799] broekvent   q26 ? ␅
    @+55799  [ 55799] broekvent   q27 ? after
    @+55810  [ 55810] broer       q28 ? ␅
    @+55810  [ 55810] broer       q29 ? it
    @+55810  [ 55810] broer       done. it
    @+55825  [ 55825] broezen     q22 ? ␅
    @+55825  [ 55825] broezen     q23 ? before
    @+55934  [ 55934] bron        q10 ? ␅
    @+55934  [ 55934] bron        q11 ? before
    @+62281  [ 62281] cement      q8  ? ␅
    @+62281  [ 62281] cement      q9  ? before
    @+74755  [ 74755] dc          q6  ? ␅
    @+74755  [ 74755] dc          q7  ? before
    @+99751  [ 99751] ex          q2  ? ␅
    @+99751  [ 99751] ex          q3  ? before
    @+199826 [199826] lijm        q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #931 🥳 36 ⏱️ 0:00:47.031618

🤔 36 attempts
📜 1 sessions

    @        [     0] aa             
    @+98219  [ 98219] mach           q0  ? ␅
    @+98219  [ 98219] mach           q1  ? after
    @+102761 [102761] mi             q8  ? ␅
    @+102761 [102761] mi             q9  ? after
    @+106331 [106331] mono           q10 ? ␅
    @+106331 [106331] mono           q11 ? after
    @+107681 [107681] mu             q12 ? ␅
    @+107681 [107681] mu             q13 ? after
    @+108234 [108234] multiplicative q16 ? ␅
    @+108234 [108234] multiplicative q17 ? after
    @+108505 [108505] murder         q18 ? ␅
    @+108505 [108505] murder         q19 ? after
    @+108641 [108641] mush           q20 ? ␅
    @+108641 [108641] mush           q21 ? after
    @+108653 [108653] mushroom       q30 ? ␅
    @+108653 [108653] mushroom       q31 ? after
    @+108657 [108657] mushrooms      q32 ? ␅
    @+108657 [108657] mushrooms      q33 ? after
    @+108660 [108660] music          q34 ? ␅
    @+108660 [108660] music          q35 ? it
    @+108660 [108660] music          done. it
    @+108661 [108661] musical        q24 ? ␅
    @+108661 [108661] musical        q25 ? before
    @+108699 [108699] musk           q22 ? ␅
    @+108699 [108699] musk           q23 ? before
    @+108784 [108784] mut            q14 ? ␅
    @+108784 [108784] mut            q15 ? before
    @+109936 [109936] ne             q6  ? ␅
    @+109936 [109936] ne             q7  ? before
    @+122780 [122780] parr           q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1357 🥳 6 ⏱️ 0:01:34.807903

📜 1 sessions
💰 score: 27

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:NANNA n n n n n remain:5978
    ⬜⬜⬜⬜⬜ tried:GOGOS n n n n n remain:1490
    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:573
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:233
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:80
    ⬜🟩⬜⬜⬜ tried:DEWED n Y n n n remain:3

    Undos used: 3

      3 words remaining
    x 9 unused letters
    = 27 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1500 😦 18 ⏱️ 0:03:25.848943

📜 1 sessions
💰 score: 4880

    5/6
    TARES 🟩⬜⬜⬜⬜
    THONG 🟩🟩⬜⬜⬜
    THICK 🟩🟩⬜⬜⬜
    THUMB 🟩🟩🟩🟩⬜
    THUMP 🟩🟩🟩🟩🟩
    4/6
    THUMP ⬜⬜⬜🟨⬜
    MEANS 🟨🟩⬜🟨⬜
    DENIM ⬜🟩🟩⬜🟩
    VENOM 🟩🟩🟩🟩🟩
    3/6
    VENOM ⬜⬜⬜⬜🟩
    CHARM 🟩🟩🟩⬜🟩
    CHASM 🟩🟩🟩🟩🟩
    4/6
    CHASM ⬜⬜⬜⬜⬜
    LURID ⬜⬜🟨⬜⬜
    TOWER 🟨🟨🟨🟨🟨
    WROTE 🟩🟩🟩🟩🟩
    Final 2/2
    ????? 🟩⬜🟩⬜⬜
    ????? 🟩🟩🟩🟩⬜

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1477 🥳 score:26 ⏱️ 0:02:54.096917

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. TODDY attempts:5 score:5
2. DELVE attempts:8 score:8
3. BLUSH attempts:7 score:7
4. WORST attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1477 🥳 score:57 ⏱️ 0:03:26.240944

📜 1 sessions

Octordle Classic

1. FILTH attempts:4 score:4
2. JOIST attempts:12 score:12
3. CHOIR attempts:5 score:5
4. FOLLY attempts:8 score:8
5. SPELL attempts:9 score:9
6. DRYLY attempts:10 score:10
7. CACAO attempts:6 score:6
8. INLAY attempts:3 score:3

# [squareword.org](squareword.org) 🧩 #1470 🥳 8 ⏱️ 0:02:05.800316

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S H R E W
    L E A V E
    O L D I E
    S L I C K
    H O O T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1407 🥳 98 ⏱️ 0:01:45.859178

🤔 99 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 31 chat prompts
🤖 31 dolphin3:latest replies
🥵 10 😎 17 🥶 60 🧊 11

     $1 #99 acquisition      100.00°C 🥳 1000‰ ~88 used:0  [87]  source:dolphin3
     $2 #81 expansion         46.98°C 🥵  988‰  ~8 used:9  [7]   source:dolphin3
     $3 #50 integration       46.78°C 🥵  987‰ ~27 used:16 [26]  source:dolphin3
     $4 #61 consolidation     43.46°C 🥵  983‰ ~26 used:11 [25]  source:dolphin3
     $5 #55 amalgamation      39.25°C 🥵  970‰  ~7 used:5  [6]   source:dolphin3
     $6 #56 merging           36.83°C 🥵  960‰  ~3 used:4  [2]   source:dolphin3
     $7 #78 development       35.49°C 🥵  953‰  ~4 used:4  [3]   source:dolphin3
     $8 #67 incorporation     33.90°C 🥵  943‰  ~1 used:3  [0]   source:dolphin3
     $9 #60 combination       33.19°C 🥵  936‰  ~5 used:4  [4]   source:dolphin3
    $10 #87 transformation    31.66°C 🥵  925‰  ~2 used:3  [1]   source:dolphin3
    $11 #71 accretion         31.00°C 🥵  915‰  ~6 used:4  [5]   source:dolphin3
    $12 #91 extension         29.29°C 😎  887‰  ~9 used:0  [8]   source:dolphin3
    $29 #93 changeover        17.33°C 🥶       ~37 used:0  [36]  source:dolphin3
    $89 #64 coherence         -0.59°C 🧊       ~89 used:0  [88]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1440 🥳 66 ⏱️ 0:01:07.039724

🤔 67 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 19 chat prompts
🤖 19 dolphin3:latest replies
😎  4 🥶 55 🧊  7

     $1 #67 couteau         100.00°C 🥳 1000‰ ~60 used:0  [59]  source:dolphin3
     $2 #14 baguette         33.96°C 😎  847‰  ~4 used:18 [3]   source:dolphin3
     $3 #57 fourchette       29.84°C 😎  689‰  ~1 used:2  [0]   source:dolphin3
     $4  #6 pain             25.07°C 😎  180‰  ~3 used:15 [2]   source:dolphin3
     $5 #33 pâté             24.76°C 😎  114‰  ~2 used:11 [1]   source:dolphin3
     $6 #51 rôti             23.27°C 🥶        ~9 used:0  [8]   source:dolphin3
     $7 #63 viande           21.60°C 🥶       ~10 used:0  [9]   source:dolphin3
     $8 #37 gâteau           20.76°C 🥶        ~8 used:3  [7]   source:dolphin3
     $9 #41 chaud            20.55°C 🥶       ~11 used:1  [10]  source:dolphin3
    $10 #61 piment           20.40°C 🥶       ~12 used:0  [11]  source:dolphin3
    $11 #23 noix             20.36°C 🥶        ~6 used:7  [5]   source:dolphin3
    $12 #46 truffe           19.93°C 🥶       ~13 used:0  [12]  source:dolphin3
    $13 #12 pâtisserie       19.84°C 🥶        ~5 used:9  [4]   source:dolphin3
    $61 #35 chouquet         -2.36°C 🧊       ~61 used:0  [60]  source:dolphin3

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #91 🥳 score:22 ⏱️ 0:01:17.191804

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. VALVE attempts:7 score:7
2. STONE attempts:5 score:5
3. LOFTY attempts:4 score:4
4. CACTI attempts:6 score:6

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1477 🥳 score:8 ⏱️ 0:03:47.713218

📜 1 sessions

Octordle Rescue

1. CADET attempts:8 score:8
2. FLAIR attempts:13 score:13
3. AWARE attempts:7 score:7
4. DOPEY attempts:10 score:10
5. TRITE attempts:12 score:12
6. DEBIT attempts:6 score:6
7. ABACK attempts:5 score:5
8. HARDY attempts:11 score:11
