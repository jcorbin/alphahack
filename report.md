# 2026-09-15

- 🔗 spaceword.org 🧩 2026-09-14 🏁 score 2173 ranked 6.3% 23/364 ⏱️ 0:17:30.706371
- 🔗 wordgrid 🧩 #836 🟪 rarity:0.13 ⏱️ 0:02:10.517423
- 🔗 alfagok.diginaut.net 🧩 #682 🥳 30 ⏱️ 0:00:32.407153
- 🔗 alphaguess.com 🧩 #1149 🥳 28 ⏱️ 0:00:34.121237
- 🔗 dontwordle.com 🧩 #1575 🥳 6 ⏱️ 0:01:14.904763
- 🔗 dictionary.com hurdle 🧩 #1718 🥳 20 ⏱️ 0:03:12.273972
- 🔗 Quordle Classic 🧩 #1695 🥳 score:25 ⏱️ 0:01:50.100023
- 🔗 Octordle Classic 🧩 #1695 🥳 score:67 ⏱️ 0:01:36.175086
- 🔗 Sedecordle Classic 🧩 #1675 🥳 score:40 ⏱️ 0:02:06.600429
- 🔗 squareword.org 🧩 #1688 🥳 7 ⏱️ 0:02:01.007839
- 🔗 cemantle.certitudes.org 🧩 #1625 🥳 302 ⏱️ 0:14:01.569937
- 🔗 cemantix.certitudes.org 🧩 #1658 🥳 16 ⏱️ 0:00:17.371837

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


# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 2026-09-11 🤔 rarity:nan ⏱️ 0:00:33.329642

📜 2 sessions
❓ ❓ ❓
❓ ❓ ❓
❓ ❓ ❓






# [spaceword.org](spaceword.org) 🧩 2026-09-14 🏁 score 2173 ranked 6.3% 23/364 ⏱️ 0:17:30.706371

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 23/364

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ G _ A S _ U H _ B   
      _ O _ W O O R A R I   
      _ A L E X I N _ _ Z   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #836 🟪 rarity:0.13 ⏱️ 0:02:10.517423

📜 2 sessions
🦄 🌌 🦄
🦄 🌌 🌌
🌌 🦄 🌌
Rarity: 0.13 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #682 🥳 30 ⏱️ 0:00:32.407153

🤔 30 attempts
📜 1 sessions

    @        [     0] &-teken        
    @+199531 [199531] lij            q0  ? ␅
    @+199531 [199531] lij            q1  ? after
    @+299485 [299485] schrok         q2  ? ␅
    @+299485 [299485] schrok         q3  ? after
    @+349471 [349471] vakanties      q4  ? ␅
    @+349471 [349471] vakanties      q5  ? after
    @+374465 [374465] vrijst         q6  ? ␅
    @+374465 [374465] vrijst         q7  ? after
    @+386849 [386849] winkel         q8  ? ␅
    @+386849 [386849] winkel         q9  ? after
    @+392850 [392850] zelf           q10 ? ␅
    @+392850 [392850] zelf           q11 ? after
    @+394386 [394386] ziel           q14 ? ␅
    @+394386 [394386] ziel           q15 ? after
    @+395265 [395265] zit            q16 ? ␅
    @+395265 [395265] zit            q17 ? after
    @+395402 [395402] zoek           q20 ? ␅
    @+395402 [395402] zoek           q21 ? after
    @+395418 [395418] zoeken         q28 ? ␅
    @+395418 [395418] zoeken         q29 ? it
    @+395418 [395418] zoeken         done. it
    @+395440 [395440] zoekgigant     q26 ? ␅
    @+395440 [395440] zoekgigant     q27 ? before
    @+395477 [395477] zoekopdrachten q24 ? ␅
    @+395477 [395477] zoekopdrachten q25 ? before
    @+395551 [395551] zoel           q22 ? ␅
    @+395551 [395551] zoel           q23 ? before
    @+395705 [395705] zog            q18 ? ␅
    @+395705 [395705] zog            q19 ? before
    @+396154 [396154] zonde          q13 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1149 🥳 28 ⏱️ 0:00:34.121237

🤔 28 attempts
📜 1 sessions

    @        [     0] aa            
    @+2      [     2] aahed         
    @+98143  [ 98143] mac           q0  ? ␅
    @+98143  [ 98143] mac           q1  ? after
    @+122720 [122720] parol         q4  ? ␅
    @+122720 [122720] parol         q5  ? after
    @+128838 [128838] play          q8  ? ␅
    @+128838 [128838] play          q9  ? after
    @+131919 [131919] prealter      q10 ? ␅
    @+131919 [131919] prealter      q11 ? after
    @+133459 [133459] presift       q12 ? ␅
    @+133459 [133459] presift       q13 ? after
    @+134230 [134230] privies       q14 ? ␅
    @+134230 [134230] privies       q15 ? after
    @+134255 [134255] pro           q18 ? ␅
    @+134255 [134255] pro           q19 ? after
    @+134263 [134263] prob          q22 ? ␅
    @+134263 [134263] prob          q23 ? after
    @+134325 [134325] proboscis     q24 ? ␅
    @+134325 [134325] proboscis     q25 ? after
    @+134357 [134357] process       q26 ? ␅
    @+134357 [134357] process       q27 ? it
    @+134357 [134357] process       done. it
    @+134387 [134387] proclamations q20 ? ␅
    @+134387 [134387] proclamations q21 ? before
    @+134519 [134519] prof          q16 ? ␅
    @+134519 [134519] prof          q17 ? before
    @+135000 [135000] prop          q6  ? ␅
    @+135000 [135000] prop          q7  ? before
    @+147307 [147307] rho           q2  ? ␅
    @+147307 [147307] rho           q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1575 🥳 6 ⏱️ 0:01:14.904763

📜 1 sessions
💰 score: 30

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:FEEZE n n n n n remain:6482
    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:3121
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:1541
    ⬜⬜⬜⬜⬜ tried:STOSS n n n n n remain:133
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:32
    ⬜🟨⬜⬜🟨 tried:BUMPH n m n n m remain:5

    Undos used: 4

      5 words remaining
    x 6 unused letters
    = 30 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1718 🥳 20 ⏱️ 0:03:12.273972

📜 1 sessions
💰 score: 9600

    6/6
    ORLES 🟨⬜⬜⬜🟩
    NOCKS ⬜🟩⬜⬜🟩
    TOGAS ⬜🟩⬜⬜🟩
    MODUS 🟨🟩⬜⬜🟩
    WOMBS ⬜🟩🟨⬜🟩
    ZOOMS 🟩🟩🟩🟩🟩
    4/6
    ZOOMS ⬜⬜⬜⬜⬜
    ALDER ⬜⬜⬜⬜🟨
    TRUNK 🟨🟨⬜⬜⬜
    GIRTH 🟩🟩🟩🟩🟩
    5/6
    GIRTH ⬜⬜🟨⬜⬜
    ARSON ⬜🟨⬜🟨⬜
    DOWER 🟨🟨⬜🟩🟩
    OLDER 🟩⬜🟩🟩🟩
    ODDER 🟩🟩🟩🟩🟩
    4/6
    ODDER ⬜⬜⬜🟨⬜
    LEAPS ⬜🟨⬜⬜🟨
    SUITE 🟨🟨🟨⬜🟩
    ISSUE 🟩🟩🟩🟩🟩
    Final 1/2
    SIXTH 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1695 🥳 score:25 ⏱️ 0:01:50.100023

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SHUSH attempts:8 score:8
2. LITHE attempts:6 score:6
3. DELTA attempts:7 score:7
4. BUGLE attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1695 🥳 score:67 ⏱️ 0:01:36.175086

📜 1 sessions

Octordle Classic

1. ROUND attempts:7 score:7
2. PREEN attempts:6 score:6
3. SKATE attempts:11 score:11
4. JUROR attempts:12 score:12
5. UNTIE attempts:4 score:4
6. ALLOY attempts:8 score:8
7. DANDY attempts:9 score:9
8. SHARK attempts:10 score:10

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1675 🥳 score:40 ⏱️ 0:02:06.600429

📜 1 sessions

Sedecordle Classic sedecordle.com

1. TWIRL attempts:11 score:1
2. SAUCE attempts:12 score:1
3. MUDDY attempts:7 score:0
4. DULLY attempts:5 score:7
5. NAVEL attempts:8 score:0
6. VOMIT attempts:9 score:8
7. LATCH attempts:10 score:1
8. IDLER attempts:4 score:0
9. ESTER attempts:13 score:1
10. JUMBO attempts:16 score:3
11. STAKE attempts:18 score:1
12. OPIUM attempts:6 score:8
13. INLAY attempts:3 score:0
14. DITTY attempts:14 score:3
15. POLYP attempts:15 score:1
16. TOUCH attempts:18 score:5

# [squareword.org](squareword.org) 🧩 #1688 🥳 7 ⏱️ 0:02:01.007839

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟨 🟩 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C O O P
    M A U V E
    A C T O R
    S H E I K
    H E R D S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1625 🥳 302 ⏱️ 0:14:01.569937

🤔 303 attempts
📜 1 sessions
🫧 12 chat sessions
⁉️ 62 chat prompts
🤖 62 gemma4:12b replies
🔥   2 🥵  19 😎  24 🥶 198 🧊  59

      $1 #303 statistics     100.00°C 🥳 1000‰ ~244 used:0  [243]  source:gemma4
      $2 #290 data            53.79°C 🔥  995‰   ~1 used:1  [0]    source:gemma4
      $3 #278 report          45.12°C 🔥  994‰   ~2 used:2  [1]    source:gemma4
      $4 #288 census          38.76°C 🥵  989‰   ~3 used:0  [2]    source:gemma4
      $5 #280 tally           38.63°C 🥵  988‰  ~17 used:2  [16]   source:gemma4
      $6 #284 analysis        36.30°C 🥵  982‰   ~4 used:0  [3]    source:gemma4
      $7 #302 information     35.55°C 🥵  980‰   ~5 used:0  [4]    source:gemma4
      $8 #227 prediction      32.19°C 🥵  971‰  ~22 used:6  [21]   source:gemma4
      $9 #287 bulletin        31.00°C 🥵  966‰   ~6 used:0  [5]    source:gemma4
     $10 #299 summary         30.91°C 🥵  965‰   ~7 used:0  [6]    source:gemma4
     $11 #272 database        29.85°C 🥵  956‰   ~8 used:0  [7]    source:gemma4
     $24 #276 logbook         24.88°C 😎  875‰  ~23 used:0  [22]   source:gemma4
     $47 #195 timeline        15.63°C 🥶        ~59 used:0  [58]   source:gemma4
    $245  #39 savory          -0.12°C 🧊       ~245 used:0  [244]  source:gemma4

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1658 🥳 16 ⏱️ 0:00:17.371837

🤔 17 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 4 chat prompts
🤖 4 gemma4:12b replies
😎  1 🥶 14 🧊  1

     $1 #17 gravité     100.00°C 🥳 1000‰ ~16 used:0 [15]  source:gemma4
     $2 #11 astre        24.56°C 😎   81‰  ~1 used:1 [0]   source:gemma4
     $3 #13 planète      19.48°C 🥶        ~2 used:1 [1]   source:gemma4
     $4 #16 cosmos       19.21°C 🥶        ~3 used:0 [2]   source:gemma4
     $5 #15 univers      17.86°C 🥶        ~4 used:0 [3]   source:gemma4
     $6 #12 comète       15.56°C 🥶        ~5 used:0 [4]   source:gemma4
     $7 #10 étoile       13.97°C 🥶        ~6 used:1 [5]   source:gemma4
     $8  #1 brouillage   10.73°C 🥶        ~7 used:0 [6]   source:gemma4
     $9 #14 soleil        9.92°C 🥶        ~8 used:0 [7]   source:gemma4
    $10  #2 brouillard    7.92°C 🥶        ~9 used:0 [8]   source:gemma4
    $11  #3 chiffre       6.98°C 🥶       ~10 used:0 [9]   source:gemma4
    $12  #7 horizon       5.00°C 🥶       ~11 used:0 [10]  source:gemma4
    $13  #4 clavier       2.90°C 🥶       ~12 used:0 [11]  source:gemma4
    $17  #5 fenêtre      -0.44°C 🧊       ~17 used:0 [16]  source:gemma4
