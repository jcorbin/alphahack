# 2026-06-06

- 🔗 spaceword.org 🧩 2026-06-05 🏁 score 2168 ranked 42.0% 136/324 ⏱️ 1 day, 4:58:05.054304
- 🔗 alfagok.diginaut.net 🧩 #581 🥳 16 ⏱️ 0:00:23.095098
- 🔗 cemantix.certitudes.org 🧩 #1557 🥳 602 ⏱️ 0:31:43.487820
- 🔗 alphaguess.com 🧩 #1048 🥳 34 ⏱️ 0:00:30.342699
- 🔗 dontwordle.com 🧩 #1474 🥳 6 ⏱️ 0:01:42.064093
- 🔗 dictionary.com hurdle 🧩 #1617 🥳 19 ⏱️ 0:03:02.064134
- 🔗 Quordle Classic 🧩 #1594 🥳 score:29 ⏱️ 0:02:09.288942
- 🔗 Octordle Classic 🧩 #1594 🥳 score:60 ⏱️ 0:03:33.328389
- 🔗 squareword.org 🧩 #1587 🥳 6 ⏱️ 0:01:23.099940
- 🔗 cemantle.certitudes.org 🧩 #1524 🥳 34 ⏱️ 0:00:15.746798

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










# [spaceword.org](spaceword.org) 🧩 2026-06-05 🏁 score 2168 ranked 42.0% 136/324 ⏱️ 1 day, 4:58:05.054304

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 136/324

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ R I S E _ _ _ _ _   
      _ _ _ C _ L _ B _ _   
      _ _ _ A D A G I O _   
      _ J A R O V I Z E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #581 🥳 16 ⏱️ 0:00:23.095098

🤔 16 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+99704  [ 99704] ex        q2  ? ␅
    @+99704  [ 99704] ex        q3  ? after
    @+149392 [149392] huis      q4  ? ␅
    @+149392 [149392] huis      q5  ? after
    @+174499 [174499] kind      q6  ? ␅
    @+174499 [174499] kind      q7  ? after
    @+187100 [187100] kronkel   q8  ? ␅
    @+187100 [187100] kronkel   q9  ? after
    @+187558 [187558] kruis     q14 ? ␅
    @+187558 [187558] kruis     q15 ? it
    @+187558 [187558] kruis     done. it
    @+188222 [188222] kunst     q12 ? ␅
    @+188222 [188222] kunst     q13 ? before
    @+190304 [190304] la        q10 ? ␅
    @+190304 [190304] la        q11 ? before
    @+199766 [199766] lijm      q0  ? ␅
    @+199766 [199766] lijm      q1  ? before

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1557 🥳 602 ⏱️ 0:31:43.487820

🤔 603 attempts
📜 2 sessions
🫧 78 chat sessions
⁉️ 409 chat prompts
🤖 409 dolphin3:latest replies
🔥   7 🥵  40 😎 116 🥶 408 🧊  31

      $1 #603 étendue          100.00°C 🥳 1000‰ ~572 used:0   [571]  source:dolphin3
      $2 #149 sablonneux        44.34°C 🔥  998‰ ~161 used:358 [160]  source:dolphin3
      $3 #472 steppique         43.77°C 🔥  997‰  ~43 used:97  [42]   source:dolphin3
      $4 #108 désertique        41.66°C 🔥  996‰ ~159 used:194 [158]  source:dolphin3
      $5 #211 tourbeux          41.34°C 🔥  993‰  ~42 used:81  [41]   source:dolphin3
      $6 #284 végétation        40.88°C 🔥  992‰   ~3 used:65  [2]    source:dolphin3
      $7 #269 lacs              40.54°C 🔥  991‰   ~4 used:65  [3]    source:dolphin3
      $8  #28 escarpement       40.24°C 🥵  989‰   ~5 used:65  [4]    source:dolphin3
      $9 #168 rocailleux        40.19°C 🥵  988‰   ~6 used:7   [5]    source:dolphin3
     $10 #350 toundra           39.96°C 🥵  987‰   ~7 used:7   [6]    source:dolphin3
     $11 #394 herbeux           39.91°C 🥵  986‰   ~8 used:7   [7]    source:dolphin3
     $49 #579 oligotrophe       32.65°C 😎  899‰  ~44 used:0   [43]   source:dolphin3
    $165  #38 glace             22.75°C 🥶       ~165 used:0   [164]  source:dolphin3
    $573 #529 stratégie         -0.01°C 🧊       ~573 used:0   [572]  source:dolphin3

# [alphaguess.com](alphaguess.com) 🧩 #1048 🥳 34 ⏱️ 0:00:30.342699

🤔 34 attempts
📜 1 sessions

    @        [     0] aa          
    @+98216  [ 98216] mach        q0  ? ␅
    @+98216  [ 98216] mach        q1  ? after
    @+147366 [147366] rhotic      q2  ? ␅
    @+147366 [147366] rhotic      q3  ? after
    @+171636 [171636] ta          q4  ? ␅
    @+171636 [171636] ta          q5  ? after
    @+182000 [182000] un          q6  ? ␅
    @+182000 [182000] un          q7  ? after
    @+189262 [189262] vicar       q8  ? ␅
    @+189262 [189262] vicar       q9  ? after
    @+191042 [191042] walk        q12 ? ␅
    @+191042 [191042] walk        q13 ? after
    @+191246 [191246] war         q18 ? ␅
    @+191246 [191246] war         q19 ? after
    @+191335 [191335] warm        q20 ? ␅
    @+191335 [191335] warm        q21 ? after
    @+191388 [191388] warrant     q22 ? ␅
    @+191388 [191388] warrant     q23 ? after
    @+191403 [191403] warrantors  q26 ? ␅
    @+191403 [191403] warrantors  q27 ? after
    @+191405 [191405] warranty    q32 ? ␅
    @+191405 [191405] warranty    q33 ? it
    @+191405 [191405] warranty    done. it
    @+191406 [191406] warrantying q30 ? ␅
    @+191406 [191406] warrantying q31 ? before
    @+191408 [191408] warren      q28 ? ␅
    @+191408 [191408] warren      q29 ? before
    @+191417 [191417] wars        q24 ? ␅
    @+191417 [191417] wars        q25 ? before
    @+191453 [191453] wash        q17 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1474 🥳 6 ⏱️ 0:01:42.064093

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:BENNE n n n n n remain:4801
    ⬜⬜⬜⬜⬜ tried:KOOKS n n n n n remain:1155
    ⬜⬜⬜⬜⬜ tried:MUMMY n n n n n remain:431
    ⬜⬜⬜⬜⬜ tried:CRWTH n n n n n remain:60
    ⬜🟨⬜⬜⬜ tried:QAJAQ n m n n n remain:12
    🟩⬜🟩⬜⬜ tried:PZAZZ Y n Y n n remain:1

    Undos used: 5

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1617 🥳 19 ⏱️ 0:03:02.064134

📜 1 sessions
💰 score: 9700

    4/6
    TESLA ⬜🟨⬜⬜⬜
    CREDO ⬜🟨🟩⬜⬜
    QUERY ⬜⬜🟩🟩🟩
    FIERY 🟩🟩🟩🟩🟩
    4/6
    FIERY ⬜🟩⬜⬜⬜
    PILOT ⬜🟩⬜⬜🟩
    DIGHT ⬜🟩🟨⬜🟩
    GIANT 🟩🟩🟩🟩🟩
    5/6
    GIANT ⬜⬜🟨🟨⬜
    RAMEN ⬜🟩⬜⬜🟨
    BANKS ⬜🟩🟨⬜⬜
    NACHO 🟩🟩⬜⬜⬜
    NAVAL 🟩🟩🟩🟩🟩
    4/6
    NAVAL ⬜⬜⬜⬜⬜
    OUTER ⬜⬜🟨⬜⬜
    SIGHT 🟩🟨⬜⬜🟨
    STICK 🟩🟩🟩🟩🟩
    Final 2/2
    SCALP 🟩🟩🟩🟩⬜
    SCALD 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1594 🥳 score:29 ⏱️ 0:02:09.288942

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SIEVE attempts:5 score:5
2. PHONY attempts:7 score:7
3. GIVER attempts:9 score:9
4. KNOWN attempts:8 score:8

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1594 🥳 score:60 ⏱️ 0:03:33.328389

📜 1 sessions

Octordle Classic

1. SANDY attempts:9 score:9
2. CORNY attempts:10 score:10
3. CHILI attempts:12 score:12
4. YOUTH attempts:7 score:7
5. NOISE attempts:3 score:3
6. BRINY attempts:6 score:6
7. TEDDY attempts:8 score:8
8. PASTY attempts:5 score:5

# [squareword.org](squareword.org) 🧩 #1587 🥳 6 ⏱️ 0:01:23.099940

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    D R A G S
    W A G O N
    A D O R E
    R A N G E
    F R Y E R


# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1524 🥳 34 ⏱️ 0:00:15.746798

🤔 35 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 5 chat prompts
🤖 5 dolphin3:latest replies
😎  3 🥶 27 🧊  4

     $1 #35 exploration    100.00°C 🥳 1000‰ ~31 used:0 [30]  source:dolphin3
     $2 #34 energy          28.40°C 😎  678‰  ~1 used:0 [0]   source:dolphin3
     $3 #11 astronomy       26.27°C 😎  582‰  ~3 used:3 [2]   source:dolphin3
     $4 #14 planetarium     21.28°C 😎   69‰  ~2 used:2 [1]   source:dolphin3
     $5 #10 telescope       19.93°C 🥶        ~4 used:1 [3]   source:dolphin3
     $6 #16 comet           19.29°C 🥶        ~5 used:0 [4]   source:dolphin3
     $7 #24 space           18.87°C 🥶        ~6 used:0 [5]   source:dolphin3
     $8 #23 solar           18.85°C 🥶        ~7 used:0 [6]   source:dolphin3
     $9 #30 celestial       17.85°C 🥶        ~8 used:0 [7]   source:dolphin3
    $10 #21 meteorite       17.36°C 🥶        ~9 used:0 [8]   source:dolphin3
    $11 #19 hole            15.71°C 🥶       ~10 used:0 [9]   source:dolphin3
    $12  #8 quantum         15.39°C 🥶       ~11 used:0 [10]  source:dolphin3
    $13 #12 constellation   15.11°C 🥶       ~12 used:0 [11]  source:dolphin3
    $32  #1 banana          -0.39°C 🧊       ~32 used:0 [31]  source:dolphin3
