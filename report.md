# 2026-04-27

- 🔗 spaceword.org 🧩 2026-04-26 🏁 score 2173 ranked 3.2% 12/372 ⏱️ 0:17:17.858260
- 🔗 alfagok.diginaut.net 🧩 #541 🥳 14 ⏱️ 0:00:19.303267
- 🔗 alphaguess.com 🧩 #1008 🥳 32 ⏱️ 0:00:31.311069
- 🔗 dontwordle.com 🧩 #1434 🥳 6 ⏱️ 0:01:25.304101
- 🔗 dictionary.com hurdle 🧩 #1577 🥳 18 ⏱️ 0:03:26.313348
- 🔗 Quordle Classic 🧩 #1554 🥳 score:22 ⏱️ 0:02:18.024257
- 🔗 Octordle Classic 🧩 #1554 🥳 score:52 ⏱️ 0:02:58.392755
- 🔗 squareword.org 🧩 #1547 🥳 7 ⏱️ 0:02:20.889315
- 🔗 cemantle.certitudes.org 🧩 #1484 🥳 85 ⏱️ 0:01:39.277225
- 🔗 cemantix.certitudes.org 🧩 #1517 🥳 89 ⏱️ 0:01:59.669908

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

























































# [spaceword.org](spaceword.org) 🧩 2026-04-26 🏁 score 2173 ranked 3.2% 12/372 ⏱️ 0:17:17.858260

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 12/372

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ C O G _ J _ A _ L   
      _ U _ O Q U A S S A   
      _ T A X I T E _ _ C   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #541 🥳 14 ⏱️ 0:00:19.303267

🤔 14 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199704 [199704] lijk      q0  ? ␅
    @+199704 [199704] lijk      q1  ? after
    @+199704 [199704] lijk      q2  ? ␅
    @+199704 [199704] lijk      q3  ? after
    @+299649 [299649] schroot   q4  ? ␅
    @+299649 [299649] schroot   q5  ? after
    @+324239 [324239] sub       q8  ? ␅
    @+324239 [324239] sub       q9  ? after
    @+330422 [330422] televisie q12 ? ␅
    @+330422 [330422] televisie q13 ? it
    @+330422 [330422] televisie done. it
    @+336834 [336834] toetsing  q10 ? ␅
    @+336834 [336834] toetsing  q11 ? before
    @+349441 [349441] vakantie  q6  ? ␅
    @+349441 [349441] vakantie  q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1008 🥳 32 ⏱️ 0:00:31.311069

🤔 32 attempts
📜 1 sessions

    @        [     0] aa         
    @+98216  [ 98216] mach       q0  ? ␅
    @+98216  [ 98216] mach       q1  ? after
    @+147366 [147366] rhotic     q2  ? ␅
    @+147366 [147366] rhotic     q3  ? after
    @+159483 [159483] slop       q6  ? ␅
    @+159483 [159483] slop       q7  ? after
    @+165525 [165525] stick      q8  ? ␅
    @+165525 [165525] stick      q9  ? after
    @+167044 [167044] stuff      q12 ? ␅
    @+167044 [167044] stuff      q13 ? after
    @+167275 [167275] sub        q14 ? ␅
    @+167275 [167275] sub        q15 ? after
    @+167927 [167927] suborn     q16 ? ␅
    @+167927 [167927] suborn     q17 ? after
    @+168251 [168251] subtext    q18 ? ␅
    @+168251 [168251] subtext    q19 ? after
    @+168330 [168330] subtropic  q22 ? ␅
    @+168330 [168330] subtropic  q23 ? after
    @+168371 [168371] subvene    q24 ? ␅
    @+168371 [168371] subvene    q25 ? after
    @+168393 [168393] subviral   q26 ? ␅
    @+168393 [168393] subviral   q27 ? after
    @+168398 [168398] subvocal   q28 ? ␅
    @+168398 [168398] subvocal   q29 ? after
    @+168405 [168405] subway     q30 ? ␅
    @+168405 [168405] subway     q31 ? it
    @+168405 [168405] subway     done. it
    @+168414 [168414] subwriters q20 ? ␅
    @+168414 [168414] subwriters q21 ? before
    @+168577 [168577] sue        q11 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1434 🥳 6 ⏱️ 0:01:25.304101

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:YUKKY n n n n n remain:7806
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:3922
    ⬜⬜⬜⬜⬜ tried:MATZA n n n n n remain:936
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:266
    ⬜⬜🟩🟨⬜ tried:CHEEP n n Y m n remain:8
    ⬜🟨🟩⬜🟨 tried:WEENS n m Y n m remain:1

    Undos used: 3

      1 words remaining
    x 6 unused letters
    = 6 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1577 🥳 18 ⏱️ 0:03:26.313348

📜 1 sessions
💰 score: 9800

    4/6
    LASER ⬜🟩⬜⬜⬜
    PANTO ⬜🟩⬜⬜🟨
    CAHOW ⬜🟩⬜🟩⬜
    BAYOU 🟩🟩🟩🟩🟩
    4/6
    BAYOU ⬜⬜⬜⬜⬜
    RIFTS 🟨🟩⬜⬜🟨
    GIRSH ⬜🟩🟩🟨⬜
    SIREN 🟩🟩🟩🟩🟩
    4/6
    SIREN 🟨⬜⬜⬜⬜
    AUTOS 🟨⬜⬜⬜🟨
    PSALM ⬜🟨🟩🟨⬜
    CLASH 🟩🟩🟩🟩🟩
    5/6
    CLASH ⬜🟩⬜⬜⬜
    ELFIN ⬜🟩⬜🟨🟨
    BLING 🟩🟩🟩🟩⬜
    BLIND 🟩🟩🟩🟩⬜
    BLINK 🟩🟩🟩🟩🟩
    Final 1/2
    TROVE 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1554 🥳 score:22 ⏱️ 0:02:18.024257

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. ARGUE attempts:4 score:4
2. LUNAR attempts:5 score:5
3. SEVER attempts:7 score:7
4. THEIR attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1554 🥳 score:52 ⏱️ 0:02:58.392755

📜 1 sessions

Octordle Classic

1. PAUSE attempts:8 score:8
2. WAIVE attempts:7 score:7
3. GODLY attempts:9 score:9
4. PASTA attempts:10 score:10
5. RECUT attempts:5 score:5
6. STILL attempts:6 score:6
7. MEDIC attempts:4 score:4
8. CURLY attempts:3 score:3

# [squareword.org](squareword.org) 🧩 #1547 🥳 7 ⏱️ 0:02:20.889315

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    R A B I D
    E R A S E
    A G I L E
    C U R E D
    T E N T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1484 🥳 85 ⏱️ 0:01:39.277225

🤔 86 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 10 chat prompts
🤖 10 dolphin3:latest replies
🥵  5 😎  1 🥶 76 🧊  3

     $1 #86 cure          100.00°C 🥳 1000‰ ~83 used:0 [82]  source:dolphin3
     $2 #85 curative       43.09°C 🥵  983‰  ~1 used:0 [0]   source:dolphin3
     $3 #14 treat          38.58°C 🥵  958‰  ~5 used:7 [4]   source:dolphin3
     $4 #66 ointment       37.80°C 🥵  950‰  ~3 used:2 [2]   source:dolphin3
     $5 #81 treatment      36.96°C 🥵  937‰  ~4 used:2 [3]   source:dolphin3
     $6 #68 ailment        35.78°C 🥵  918‰  ~2 used:0 [1]   source:dolphin3
     $7 #78 pain           28.93°C 😎  588‰  ~6 used:0 [5]   source:dolphin3
     $8 #61 medicine       24.79°C 🥶        ~8 used:2 [7]   source:dolphin3
     $9 #83 antibiotic     22.20°C 🥶       ~10 used:0 [9]   source:dolphin3
    $10 #63 doctor         22.17°C 🥶       ~11 used:0 [10]  source:dolphin3
    $11 #74 injection      21.89°C 🥶       ~12 used:0 [11]  source:dolphin3
    $12 #62 prescription   20.45°C 🥶       ~13 used:0 [12]  source:dolphin3
    $13 #70 clinic         20.43°C 🥶       ~14 used:0 [13]  source:dolphin3
    $84 #52 high           -0.58°C 🧊       ~84 used:0 [83]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1517 🥳 89 ⏱️ 0:01:59.669908

🤔 90 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 21 chat prompts
🤖 21 dolphin3:latest replies
😱  1 🔥  1 🥵  7 😎 23 🥶 47 🧊 10

     $1 #90 inattendu        100.00°C 🥳 1000‰ ~80 used:0 [79]  source:dolphin3
     $2 #87 surprenant        66.24°C 😱  999‰  ~1 used:2 [0]   source:dolphin3
     $3 #82 étonnant          56.49°C 🔥  997‰  ~2 used:1 [1]   source:dolphin3
     $4 #79 troublant         48.92°C 🥵  989‰  ~3 used:0 [2]   source:dolphin3
     $5 #77 spectaculaire     47.20°C 🥵  986‰  ~4 used:0 [3]   source:dolphin3
     $6 #36 exubérant         44.30°C 🥵  975‰  ~9 used:9 [8]   source:dolphin3
     $7 #84 extraordinaire    42.88°C 🥵  964‰  ~5 used:0 [4]   source:dolphin3
     $8 #50 fascinant         42.37°C 🥵  960‰  ~8 used:6 [7]   source:dolphin3
     $9 #67 intrigant         41.47°C 🥵  955‰  ~7 used:4 [6]   source:dolphin3
    $10 #74 mystérieux        40.93°C 🥵  946‰  ~6 used:0 [5]   source:dolphin3
    $11 #49 excitant          37.04°C 😎  886‰ ~10 used:0 [9]   source:dolphin3
    $12 #44 captivant         36.97°C 😎  884‰ ~31 used:2 [30]  source:dolphin3
    $34 #23 éclair            25.66°C 🥶       ~33 used:5 [32]  source:dolphin3
    $81 #17 arc               -0.41°C 🧊       ~81 used:0 [80]  source:dolphin3
