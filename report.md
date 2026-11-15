# 2026-11-16

- 🔗 spaceword.org 🧩 2026-11-15 🏁 score 2173 ranked 9.2% 26/284 ⏱️ 0:58:20.268835
- 🔗 alfagok.diginaut.net 🧩 #744 🥳 38 ⏱️ 0:00:46.602797
- 🔗 alphaguess.com 🧩 #1211 🥳 42 ⏱️ 0:00:45.264194
- 🔗 dontwordle.com 🧩 #1637 🥳 6 ⏱️ 0:01:25.515838
- 🔗 dictionary.com hurdle 🧩 #1780 🥳 18 ⏱️ 0:02:34.439224
- 🔗 Quordle Classic 🧩 #1757 🥳 score:25 ⏱️ 0:01:26.701738
- 🔗 Octordle Classic 🧩 #1757 🥳 score:52 ⏱️ 0:01:42.252903
- 🔗 Sedecordle Classic 🧩 #1737 🥳 score:41 ⏱️ 0:03:26.308499
- 🔗 squareword.org 🧩 #1750 🥳 7 ⏱️ 0:02:05.767095
- 🔗 cemantle.certitudes.org 🧩 #1687 🥳 125 ⏱️ 0:00:33.115151
- 🔗 cemantix.certitudes.org 🧩 #1720 🥳 70 ⏱️ 0:00:31.453056
- 🔗 wordgrid 🧩 #898 🟪 rarity:0.19 ⏱️ 0:04:25.431550

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










# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #892 🟪 rarity:0.32 ⏱️ 0:03:10.891631

📜 2 sessions
🌌 🦄 🦄
🌌 🌌 🌌
🦄 🌌 🌌
Rarity: 0.32 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-09 🏁 score 2168 ranked 49.8% 148/297 ⏱️ 0:22:41.164996

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 148/297

      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ G _ _ _ _ K _ L _
      _ O _ C A S A V A _
      _ A _ A _ _ S I G _
      _ D A W E N _ A _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _








# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #898 🟪 rarity:0.19 ⏱️ 0:04:25.431550

📜 2 sessions
🌌 🦄 🌌
🦄 🦄 🦄
🦄 🌌 🦄
Rarity: 0.19 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-15 🏁 score 2173 ranked 9.2% 26/284 ⏱️ 0:58:20.268835

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 26/284

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ C _ W _ _ _   
      _ _ _ _ O K E _ _ _   
      _ _ _ _ Q _ A _ _ _   
      _ _ _ _ U _ R _ _ _   
      _ _ _ _ E _ A _ _ _   
      _ _ _ _ T A B _ _ _   
      _ _ _ _ _ _ L _ _ _   
      _ _ _ _ G I E _ _ _   
      _ _ _ _ O N S _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #744 🥳 38 ⏱️ 0:00:46.602797

🤔 38 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+99672  [ 99672] ex        q4  ? ␅
    @+99672  [ 99672] ex        q5  ? after
    @+149358 [149358] huis      q6  ? ␅
    @+149358 [149358] huis      q7  ? after
    @+174465 [174465] kind      q8  ? ␅
    @+174465 [174465] kind      q9  ? after
    @+187045 [187045] kronen    q10 ? ␅
    @+187045 [187045] kronen    q11 ? after
    @+190269 [190269] la        q12 ? ␅
    @+190269 [190269] la        q13 ? after
    @+194825 [194825] lees      q14 ? ␅
    @+194825 [194825] lees      q15 ? after
    @+197003 [197003] levens    q16 ? ␅
    @+197003 [197003] levens    q17 ? after
    @+198171 [198171] licht     q18 ? ␅
    @+198171 [198171] licht     q19 ? after
    @+198872 [198872] liefdes   q20 ? ␅
    @+198872 [198872] liefdes   q21 ? after
    @+199183 [199183] lieveling q22 ? ␅
    @+199183 [199183] lieveling q23 ? after
    @+199384 [199384] lift      q24 ? ␅
    @+199384 [199384] lift      q25 ? after
    @+199429 [199429] lig       q26 ? ␅
    @+199429 [199429] lig       q27 ? after
    @+199452 [199452] ligfiets  q32 ? ␅
    @+199452 [199452] ligfiets  q33 ? after
    @+199457 [199457] liggen    q36 ? ␅
    @+199457 [199457] liggen    q37 ? it
    @+199457 [199457] liggen    done. it
    @+199462 [199462] ligging   q35 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1211 🥳 42 ⏱️ 0:00:45.264194

🤔 42 attempts
📜 1 sessions

    @        [     0] aa           
    @+98138  [ 98138] mac          q0  ? ␅
    @+98138  [ 98138] mac          q1  ? after
    @+98138  [ 98138] mac          q2  ? ␅
    @+98138  [ 98138] mac          q3  ? after
    @+147299 [147299] rho          q4  ? ␅
    @+147299 [147299] rho          q5  ? after
    @+171898 [171898] tag          q6  ? ␅
    @+171898 [171898] tag          q7  ? after
    @+174384 [174384] test         q12 ? ␅
    @+174384 [174384] test         q13 ? after
    @+174384 [174384] test         q14 ? ␅
    @+174384 [174384] test         q15 ? after
    @+174751 [174751] the          q18 ? ␅
    @+174751 [174751] the          q19 ? after
    @+175167 [175167] thick        q20 ? ␅
    @+175167 [175167] thick        q21 ? after
    @+175362 [175362] tho          q22 ? ␅
    @+175362 [175362] tho          q23 ? after
    @+175419 [175419] thoro        q26 ? ␅
    @+175419 [175419] thoro        q27 ? after
    @+175447 [175447] thou         q28 ? ␅
    @+175447 [175447] thou         q29 ? after
    @+175461 [175461] thous        q30 ? ␅
    @+175461 [175461] thous        q31 ? after
    @+175462 [175462] thousand     q40 ? ␅
    @+175462 [175462] thousand     q41 ? it
    @+175462 [175462] thousand     done. it
    @+175463 [175463] thousandfold q38 ? ␅
    @+175463 [175463] thousandfold q39 ? before
    @+175464 [175464] thousands    q37 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1637 🥳 6 ⏱️ 0:01:25.515838

📜 2 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:CANNA n n n n n remain:5012
    ⬜⬜⬜⬜⬜ tried:POOPY n n n n n remain:1998
    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:820
    ⬜⬜⬜⬜⬜ tried:DILLS n n n n n remain:40
    ⬜🟩⬜⬜🟩 tried:FEEZE n Y n n Y remain:5
    ⬜🟩🟩🟩🟩 tried:MERGE n Y Y Y Y remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1780 🥳 18 ⏱️ 0:02:34.439224

📜 1 sessions
💰 score: 9800

    5/6
    PARES ⬜🟨⬜⬜🟨
    ALIST 🟨⬜⬜🟨⬜
    SHAWN 🟩⬜🟨⬜⬜
    SCUBA 🟩⬜🟩🟨🟨
    SQUAB 🟩🟩🟩🟩🟩
    3/6
    SQUAB ⬜⬜⬜⬜🟨
    TRIBE ⬜⬜🟩🟨🟩
    BEIGE 🟩🟩🟩🟩🟩
    5/6
    BEIGE ⬜⬜⬜⬜⬜
    ROYAL 🟨⬜⬜⬜⬜
    TRUMP ⬜🟩🟩⬜⬜
    DRUNK ⬜🟩🟩⬜⬜
    CRUSH 🟩🟩🟩🟩🟩
    3/6
    CRUSH ⬜🟨🟨🟨🟨
    HURTS 🟨🟨🟩⬜🟨
    SHRUG 🟩🟩🟩🟩🟩
    Final 2/2
    UMBRA 🟨🟨🟨🟨🟩
    RUMBA 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1757 🥳 score:25 ⏱️ 0:01:26.701738

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. RAZOR attempts:9 score:9
2. TUBER attempts:4 score:4
3. MOUTH attempts:5 score:5
4. ALOUD attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1757 🥳 score:52 ⏱️ 0:01:42.252903

📜 1 sessions

Octordle Classic

1. NERVE attempts:9 score:9
2. GUEST attempts:4 score:4
3. FULLY attempts:8 score:8
4. CRASH attempts:7 score:7
5. BADLY attempts:5 score:5
6. RISEN attempts:10 score:10
7. ELEGY attempts:3 score:3
8. TUBER attempts:6 score:6

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1737 🥳 score:41 ⏱️ 0:03:26.308499

📜 1 sessions

Sedecordle Classic sedecordle.com

1. DRAPE attempts:15 score:1
2. HALVE attempts:15 score:6
3. IDYLL attempts:9 score:0
4. TAPIR attempts:2 score:9
5. POLAR attempts:3 score:0
6. CAROL attempts:6 score:3
7. DEBUG attempts:11 score:1
8. DEBUT attempts:7 score:1
9. TRITE attempts:14 score:1
10. PRIDE attempts:8 score:4
11. STORK attempts:13 score:1
12. RASPY attempts:10 score:3
13. GAYER attempts:12 score:1
14. PUPIL attempts:4 score:2
15. GULLY attempts:15 score:1
16. TRAIL attempts:5 score:7

# [squareword.org](squareword.org) 🧩 #1750 🥳 7 ⏱️ 0:02:05.767095

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    G R A D E
    R U D E R
    A M O U R
    F O R C E
    T R E E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1687 🥳 125 ⏱️ 0:00:33.115151

🤔 126 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 14 chat prompts
🤖 14 glm-5.3-flash:cloud replies
🔥  4 🥵 11 😎 20 🥶 86 🧊  4

      $1 #126 palace        100.00°C 🥳 1000‰ ~122 used:0 [121]  source:glm
      $2  #97 villa          58.15°C 🔥  997‰   ~4 used:5 [3]    source:glm
      $3 #106 mansion        58.10°C 🔥  996‰   ~1 used:1 [0]    source:glm
      $4  #93 palatial       56.50°C 🔥  993‰   ~2 used:1 [1]    source:glm
      $5 #123 chateau        55.49°C 🔥  992‰   ~3 used:0 [2]    source:glm
      $6  #92 ornate         44.84°C 🥵  957‰   ~5 used:1 [4]    source:glm
      $7  #91 opulent        44.67°C 🥵  954‰   ~6 used:0 [5]    source:glm
      $8  #88 gilded         43.95°C 🥵  948‰   ~7 used:0 [6]    source:glm
      $9 #100 courtyard      43.02°C 🥵  938‰   ~8 used:0 [7]    source:glm
     $10  #73 grotto         42.59°C 🥵  934‰  ~15 used:4 [14]   source:glm
     $11 #105 manor          42.38°C 🥵  930‰   ~9 used:0 [8]    source:glm
     $17 #122 chalet         38.96°C 😎  876‰  ~16 used:0 [15]   source:glm
     $37  #86 elegant        25.96°C 🥶        ~40 used:0 [39]   source:glm
    $123  #58 navigator      -0.12°C 🧊       ~123 used:0 [122]  source:glm

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1720 🥳 70 ⏱️ 0:00:31.453056

🤔 71 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 10 chat prompts
🤖 10 glm-5.3-flash:cloud replies
😱  1 🥵  1 😎  6 🥶 34 🧊 28

     $1 #71 abonné          100.00°C 🥳 1000‰ ~43 used:0 [42]  source:glm
     $2 #70 abonnement       66.73°C 😱  999‰  ~1 used:2 [0]   source:glm
     $3 #37 lecteur          33.97°C 🥵  944‰  ~2 used:8 [1]   source:glm
     $4 #46 magazine         27.52°C 😎  833‰  ~3 used:1 [2]   source:glm
     $5 #44 journal          24.32°C 😎  711‰  ~4 used:0 [3]   source:glm
     $6 #69 tirage           23.26°C 😎  661‰  ~5 used:0 [4]   source:glm
     $7 #52 revue            22.33°C 😎  603‰  ~6 used:0 [5]   source:glm
     $8  #1 bibliothèque     19.87°C 😎  381‰  ~8 used:5 [7]   source:glm
     $9 #54 signet           19.21°C 😎  324‰  ~7 used:0 [6]   source:glm
    $10 #21 page             15.81°C 🥶        ~9 used:3 [8]   source:glm
    $11 #68 sommaire         14.68°C 🥶       ~12 used:0 [11]  source:glm
    $12 #27 index            14.04°C 🥶       ~11 used:2 [10]  source:glm
    $13 #15 auteur           13.62°C 🥶       ~10 used:3 [9]   source:glm
    $44 #58 épigraphe        -0.15°C 🧊       ~44 used:0 [43]  source:glm
