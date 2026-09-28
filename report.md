# 2026-09-29

- 🔗 spaceword.org 🧩 2026-09-28 🏁 score 2172 ranked 17.0% 61/358 ⏱️ 0:05:29.890103
- 🔗 wordgrid 🧩 #850 🟪 rarity:0.12 ⏱️ 0:02:54.403973
- 🔗 alfagok.diginaut.net 🧩 #696 🥳 20 ⏱️ 0:00:48.434223
- 🔗 alphaguess.com 🧩 #1163 🥳 28 ⏱️ 0:00:31.193836
- 🔗 dontwordle.com 🧩 #1589 🥳 6 ⏱️ 0:01:36.458098
- 🔗 dictionary.com hurdle 🧩 #1732 🥳 19 ⏱️ 0:03:19.289464
- 🔗 Quordle Classic 🧩 #1709 🥳 score:21 ⏱️ 0:01:26.291115
- 🔗 Octordle Classic 🧩 #1709 🥳 score:60 ⏱️ 0:01:22.604748
- 🔗 Sedecordle Classic 🧩 #1689 🥳 score:40 ⏱️ 0:04:13.901445
- 🔗 squareword.org 🧩 #1702 🥳 8 ⏱️ 0:02:01.996361
- 🔗 cemantle.certitudes.org 🧩 #1639 🥳 23 ⏱️ 0:03:03.017329
- 🔗 cemantix.certitudes.org 🧩 #1672 🥳 237 ⏱️ 0:15:11.017030

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









# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #850 🟪 rarity:0.12 ⏱️ 0:02:54.403973

📜 2 sessions
🦄 🦄 🌌
🦄 🦄 🌌
🌌 🦄 🌌
Rarity: 0.12 🟪

# [spaceword.org](spaceword.org) 🧩 2026-09-28 🏁 score 2172 ranked 17.0% 61/358 ⏱️ 0:05:29.890103

📜 2 sessions
- tiles: 21/21
- score: 2172 bonus: +72
- rank: 61/358

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ Q _ V _ _ _   
      _ _ _ F U M E _ _ _   
      _ _ _ _ A I N _ _ _   
      _ _ _ Z I N E _ _ _   
      _ _ _ _ L I N _ _ _   
      _ _ _ _ E M E _ _ _   
      _ _ _ I D _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #696 🥳 20 ⏱️ 0:00:48.434223

🤔 20 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+199528 [199528] lij        q0  ? ␅
    @+199528 [199528] lij        q1  ? after
    @+247578 [247578] op         q4  ? ␅
    @+247578 [247578] op         q5  ? after
    @+273370 [273370] proef      q6  ? ␅
    @+273370 [273370] proef      q7  ? after
    @+286390 [286390] rijp       q8  ? ␅
    @+286390 [286390] rijp       q9  ? after
    @+289411 [289411] roo        q12 ? ␅
    @+289411 [289411] roo        q13 ? .
    @+289528 [289528] roodzijden q14 ? ␅
    @+289528 [289528] roodzijden q15 ? after
    @+291074 [291074] ruil       q16 ? ␅
    @+291074 [291074] ruil       q17 ? after
    @+291857 [291857] ruzie      q18 ? ␅
    @+291857 [291857] ruzie      q19 ? it
    @+291857 [291857] ruzie      done. it
    @+292663 [292663] samen      q10 ? ␅
    @+292663 [292663] samen      q11 ? before
    @+299482 [299482] schrok     q2  ? ␅
    @+299482 [299482] schrok     q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1163 🥳 28 ⏱️ 0:00:31.193836

🤔 28 attempts
📜 1 sessions

    @        [     0] aa      
    @+2      [     2] aahed   
    @+98142  [ 98142] mac     q0  ? ␅
    @+98142  [ 98142] mac     q1  ? after
    @+147306 [147306] rho     q2  ? ␅
    @+147306 [147306] rho     q3  ? after
    @+159588 [159588] slug    q6  ? ␅
    @+159588 [159588] slug    q7  ? after
    @+165742 [165742] stint   q8  ? ␅
    @+165742 [165742] stint   q9  ? after
    @+168792 [168792] sulfur  q10 ? ␅
    @+168792 [168792] sulfur  q11 ? after
    @+170346 [170346] sustain q12 ? ␅
    @+170346 [170346] sustain q13 ? after
    @+170439 [170439] swain   q20 ? ␅
    @+170439 [170439] swain   q21 ? after
    @+170455 [170455] swam    q24 ? ␅
    @+170455 [170455] swam    q25 ? after
    @+170459 [170459] swamp   q26 ? ␅
    @+170459 [170459] swamp   q27 ? it
    @+170459 [170459] swamp   done. it
    @+170478 [170478] swank   q22 ? ␅
    @+170478 [170478] swank   q23 ? before
    @+170532 [170532] swart   q18 ? ␅
    @+170532 [170532] swart   q19 ? before
    @+170719 [170719] swift   q16 ? ␅
    @+170719 [170719] swift   q17 ? before
    @+171114 [171114] symbol  q14 ? ␅
    @+171114 [171114] symbol  q15 ? before
    @+171906 [171906] tag     q4  ? ␅
    @+171906 [171906] tag     q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1589 🥳 6 ⏱️ 0:01:36.458098

📜 2 sessions
💰 score: 21

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:NAPPA n n n n n remain:4982
    ⬜⬜⬜⬜⬜ tried:WOWEE n n n n n remain:1025
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:502
    ⬜⬜🟩⬜⬜ tried:CHUCK n n Y n n remain:30
    ⬜⬜🟩⬜⬜ tried:GRUFF n n Y n n remain:9
    🟩⬜🟩⬜⬜ tried:SMUTS Y n Y n n remain:3

    Undos used: 3

      3 words remaining
    x 7 unused letters
    = 21 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1732 🥳 19 ⏱️ 0:03:19.289464

📜 2 sessions
💰 score: 9700

    4/6
    TAELS ⬜🟨🟨🟨⬜
    GLARE ⬜🟩🟨⬜🟨
    HEMIN ⬜🟨⬜⬜⬜
    ALLEY 🟩🟩🟩🟩🟩
    5/6
    ALLEY ⬜⬜⬜🟨⬜
    PRISE ⬜🟨⬜⬜🟩
    FORTE 🟩🟩🟩⬜🟩
    MAGIC ⬜⬜🟨⬜⬜
    FORGE 🟩🟩🟩🟩🟩
    4/6
    FORGE ⬜⬜🟩⬜⬜
    DURAS ⬜⬜🟩🟨🟨
    ANOMY 🟨⬜⬜🟨⬜
    MARSH 🟩🟩🟩🟩🟩
    4/6
    MARSH ⬜🟨⬜⬜⬜
    TINEA ⬜⬜🟨🟨🟨
    ALONE 🟨🟩⬜🟨🟨
    CLEAN 🟩🟩🟩🟩🟩
    Final 2/2
    VOCAL ⬜🟩🟩🟩🟩
    LOCAL 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1709 🥳 score:21 ⏱️ 0:01:26.291115

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. BILGE attempts:5 score:5
2. MEDAL attempts:7 score:7
3. LODGE attempts:3 score:3
4. PORCH attempts:6 score:6

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1709 🥳 score:60 ⏱️ 0:01:22.604748

📜 1 sessions

Octordle Classic

1. BEEFY attempts:7 score:7
2. CHECK attempts:8 score:8
3. KNELT attempts:4 score:4
4. PAUSE attempts:9 score:9
5. TULLE attempts:5 score:5
6. SCENT attempts:10 score:10
7. FLAIL attempts:11 score:11
8. MYRRH attempts:6 score:6

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1689 🥳 score:40 ⏱️ 0:04:13.901445

📜 1 sessions

Sedecordle Classic sedecordle.com

1. VISTA attempts:8 score:0
2. BLOAT attempts:19 score:8
3. PLAID attempts:5 score:0
4. WENCH attempts:16 score:5
5. LANKY attempts:14 score:1
6. SNEER attempts:4 score:4
7. MOLDY attempts:6 score:0
8. INGOT attempts:9 score:6
9. HEIST attempts:17 score:1
10. GAUNT attempts:10 score:7
11. SCARE attempts:11 score:1
12. SWELL attempts:15 score:1
13. SPERM attempts:3 score:0
14. EDICT attempts:7 score:3
15. DIRTY attempts:12 score:1
16. STANK attempts:13 score:2

# [squareword.org](squareword.org) 🧩 #1702 🥳 8 ⏱️ 0:02:01.996361

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    G R I P S
    R A D I I
    I D L E R
    N I E C E
    D O S E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1639 🥳 23 ⏱️ 0:03:03.017329

🤔 24 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 6 chat prompts
🤖 6 gemma4:12b replies
🔥  1 🥵  1 😎  4 🥶 16 🧊  1

     $1 #24 festival     100.00°C 🥳 1000‰ ~23 used:0 [22]  source:gemma4
     $2 #21 concert       54.93°C 🔥  996‰  ~1 used:2 [0]   source:gemma4
     $3 #15 music         37.35°C 🥵  956‰  ~2 used:3 [1]   source:gemma4
     $4 #22 artist        29.50°C 😎  820‰  ~3 used:0 [2]   source:gemma4
     $5 #12 orchestra     28.89°C 😎  800‰  ~4 used:0 [3]   source:gemma4
     $6 #23 audience      23.82°C 😎  451‰  ~5 used:0 [4]   source:gemma4
     $7 #19 song          21.69°C 😎  172‰  ~6 used:0 [5]   source:gemma4
     $8  #6 marimba       20.39°C 🥶        ~7 used:1 [6]   source:gemma4
     $9 #13 conductor     18.28°C 🥶        ~8 used:0 [7]   source:gemma4
    $10  #8 sourdough     17.20°C 🥶        ~9 used:0 [8]   source:gemma4
    $11 #16 harmony       15.30°C 🥶       ~10 used:0 [9]   source:gemma4
    $12 #17 melody        14.70°C 🥶       ~11 used:0 [10]  source:gemma4
    $13  #2 epoch         12.69°C 🥶       ~12 used:0 [11]  source:gemma4
    $24  #9 velocity      -1.57°C 🧊       ~24 used:0 [23]  source:gemma4

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1672 🥳 237 ⏱️ 0:15:11.017030

🤔 238 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 36 chat prompts
🤖 36 gemma4:12b replies
😱   1 🔥   3 🥵  11 😎  36 🥶 174 🧊  12

      $1 #238 symbolique         100.00°C 🥳 1000‰ ~226 used:0  [225]  source:gemma4
      $2 #140 symbole             64.82°C 😱  999‰   ~1 used:42 [0]    source:gemma4
      $3  #73 signification       58.67°C 🔥  997‰  ~15 used:26 [14]   source:gemma4
      $4 #150 représentation      55.60°C 🔥  996‰  ~10 used:14 [9]    source:gemma4
      $5  #55 symbolisme          52.30°C 🔥  991‰   ~9 used:11 [8]    source:gemma4
      $6 #190 signifiant          51.27°C 🥵  987‰  ~11 used:2  [10]   source:gemma4
      $7  #69 métaphore           49.47°C 🥵  982‰  ~12 used:2  [11]   source:gemma4
      $8 #221 rituel              48.48°C 🥵  979‰  ~13 used:2  [12]   source:gemma4
      $9  #58 allégorie           48.34°C 🥵  977‰   ~2 used:0  [1]    source:gemma4
     $10  #99 rite                47.33°C 🥵  970‰  ~14 used:2  [13]   source:gemma4
     $11  #84 connotation         46.03°C 🥵  960‰   ~3 used:0  [2]    source:gemma4
     $17  #60 conceptuel          41.80°C 😎  894‰  ~16 used:0  [15]   source:gemma4
     $53 #171 manifeste           29.60°C 🥶        ~54 used:0  [53]   source:gemma4
    $227 #189 prototype           -0.28°C 🧊       ~227 used:0  [226]  source:gemma4
