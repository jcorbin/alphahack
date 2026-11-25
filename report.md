# 2026-11-26

- 🔗 spaceword.org 🧩 2026-11-25 🏁 score 2173 ranked 9.4% 32/341 ⏱️ 0:29:23.452409
- 🔗 wordgrid 🧩 #908 🟪 rarity:0.23 ⏱️ 0:02:32.624748
- 🔗 alfagok.diginaut.net 🧩 #754 🥳 28 ⏱️ 0:00:37.657424
- 🔗 alphaguess.com 🧩 #1221 🥳 32 ⏱️ 0:00:46.097852
- 🔗 dontwordle.com 🧩 #1647 🥳 6 ⏱️ 0:01:16.754402
- 🔗 dictionary.com hurdle 🧩 #1790 🥳 18 ⏱️ 0:02:34.674333
- 🔗 squareword.org 🧩 #1760 🥳 7 ⏱️ 0:01:53.277747
- 🔗 cemantix.certitudes.org 🧩 #1730 🥳 139 ⏱️ 0:00:57.888424
- 🔗 cemantle.certitudes.org 🧩 #1697 🥳 225 ⏱️ 0:00:44.794356
- 🔗 Quordle Classic 🧩 #1767 🥳 score:21 ⏱️ 0:01:28.051488
- 🔗 Octordle Classic 🧩 #1767 🥳 score:59 ⏱️ 0:02:06.011215
- 🔗 Sedecordle Classic 🧩 #1747 🥳 score:39 ⏱️ 0:02:36.078997

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


















# [spaceword.org](spaceword.org) 🧩 2026-11-25 🏁 score 2173 ranked 9.4% 32/341 ⏱️ 0:29:23.452409

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 32/341

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ H A D _ _ _   
      _ _ _ _ _ W E _ _ _   
      _ _ _ _ S E V _ _ _   
      _ _ _ _ Q I S _ _ _   
      _ _ _ _ U N _ _ _ _   
      _ _ _ _ A G O _ _ _   
      _ _ _ _ M _ _ _ _ _   
      _ _ _ _ A R E _ _ _   
      _ _ _ _ E _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #908 🟪 rarity:0.23 ⏱️ 0:02:32.624748

📜 2 sessions
🌌 🌌 🌌
🦄 🦄 🦄
🌌 🌌 🦄
Rarity: 0.23 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #754 🥳 28 ⏱️ 0:00:37.657424

🤔 28 attempts
📜 1 sessions

    @        [     0] &-teken       
    @+2      [     2] -cijferig     
    @+199628 [199628] lijk          q0  ? ␅
    @+199628 [199628] lijk          q1  ? after
    @+199628 [199628] lijk          q2  ? ␅
    @+199628 [199628] lijk          q3  ? after
    @+299315 [299315] schro         q4  ? ␅
    @+299315 [299315] schro         q5  ? after
    @+349286 [349286] vakantie      q6  ? ␅
    @+349286 [349286] vakantie      q7  ? after
    @+352850 [352850] ver           q10 ? ␅
    @+352850 [352850] ver           q11 ? after
    @+363435 [363435] verzout       q12 ? ␅
    @+363435 [363435] verzout       q13 ? after
    @+368442 [368442] voetbal       q14 ? ␅
    @+368442 [368442] voetbal       q15 ? after
    @+370291 [370291] voor          q16 ? ␅
    @+370291 [370291] voor          q17 ? after
    @+372143 [372143] voortplanting q18 ? ␅
    @+372143 [372143] voortplanting q19 ? after
    @+373014 [373014] vos           q20 ? ␅
    @+373014 [373014] vos           q21 ? after
    @+373014 [373014] vos           q22 ? ␅
    @+373014 [373014] vos           q23 ? after
    @+373482 [373482] vredes        q24 ? ␅
    @+373482 [373482] vredes        q25 ? after
    @+373683 [373683] vreemd        q26 ? ␅
    @+373683 [373683] vreemd        q27 ? it
    @+373683 [373683] vreemd        done. it
    @+374020 [374020] vrij          q8  ? ␅
    @+374020 [374020] vrij          q9  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1221 🥳 32 ⏱️ 0:00:46.097852

🤔 32 attempts
📜 1 sessions

    @        [     0] aa            
    @+98136  [ 98136] mac           q0  ? ␅
    @+98136  [ 98136] mac           q1  ? after
    @+122712 [122712] parol         q4  ? ␅
    @+122712 [122712] parol         q5  ? after
    @+128830 [128830] play          q8  ? ␅
    @+128830 [128830] play          q9  ? after
    @+131910 [131910] prealter      q10 ? ␅
    @+131910 [131910] prealter      q11 ? after
    @+133449 [133449] presift       q12 ? ␅
    @+133449 [133449] presift       q13 ? after
    @+134220 [134220] privies       q14 ? ␅
    @+134220 [134220] privies       q15 ? after
    @+134245 [134245] pro           q18 ? ␅
    @+134245 [134245] pro           q19 ? after
    @+134253 [134253] prob          q22 ? ␅
    @+134253 [134253] prob          q23 ? after
    @+134315 [134315] proboscis     q24 ? ␅
    @+134315 [134315] proboscis     q25 ? after
    @+134332 [134332] procedural    q28 ? ␅
    @+134332 [134332] procedural    q29 ? after
    @+134337 [134337] proceed       q30 ? ␅
    @+134337 [134337] proceed       q31 ? it
    @+134337 [134337] proceed       done. it
    @+134347 [134347] process       q26 ? ␅
    @+134347 [134347] process       q27 ? before
    @+134377 [134377] proclamations q20 ? ␅
    @+134377 [134377] proclamations q21 ? before
    @+134509 [134509] prof          q16 ? ␅
    @+134509 [134509] prof          q17 ? before
    @+134990 [134990] prop          q7  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1647 🥳 6 ⏱️ 0:01:16.754402

📜 1 sessions
💰 score: 5

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:SLYLY n n n n n remain:4093
    ⬜⬜⬜⬜⬜ tried:DJINN n n n n n remain:1383
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:547
    ⬜⬜⬜⬜⬜ tried:GRUFF n n n n n remain:99
    ⬜🟨⬜⬜⬜ tried:KEEVE n m n n n remain:5
    🟨🟨⬜🟨⬜ tried:EMBOW m m n m n remain:1

    Undos used: 3

      1 words remaining
    x 5 unused letters
    = 5 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1790 🥳 18 ⏱️ 0:02:34.674333

📜 1 sessions
💰 score: 9800

    5/6
    AROSE ⬜⬜⬜⬜⬜
    PUNTY ⬜🟩⬜🟨⬜
    BUTCH ⬜🟩🟨⬜⬜
    GUILT ⬜🟩🟩🟩🟩
    QUILT 🟩🟩🟩🟩🟩
    4/6
    QUILT ⬜⬜⬜⬜⬜
    SPORE ⬜⬜🟨⬜⬜
    WOMAN ⬜🟨🟩🟨⬜
    MAMBO 🟩🟩🟩🟩🟩
    4/6
    MAMBO ⬜🟨⬜⬜⬜
    NEARS ⬜⬜🟩🟨🟨
    CRASH ⬜🟨🟩🟨⬜
    STAIR 🟩🟩🟩🟩🟩
    3/6
    STAIR 🟨⬜🟩⬜⬜
    MEALS ⬜⬜🟩⬜🟨
    AWASH 🟩🟩🟩🟩🟩
    Final 2/2
    THEME 🟩🟩⬜🟩🟩
    THYME 🟩🟩🟩🟩🟩

# [squareword.org](squareword.org) 🧩 #1760 🥳 7 ⏱️ 0:01:53.277747

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟨
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P A T S Y
    L L A M A
    U P P E R
    C H I L D
    K A R T S

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1730 🥳 139 ⏱️ 0:00:57.888424

🤔 140 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 14 chat prompts
🤖 14 glm-5.3-flash:cloud replies
🔥  1 🥵  6 😎 19 🥶 97 🧊 16

      $1 #140 virtuel         100.00°C 🥳 1000‰ ~124 used:0 [123]  source:glm
      $2  #91 interactif       53.99°C 🔥  998‰   ~1 used:5 [0]    source:glm
      $3 #126 numérique        43.64°C 🥵  989‰   ~2 used:1 [1]    source:glm
      $4 #124 immersif         39.41°C 🥵  983‰   ~3 used:0 [2]    source:glm
      $5 #121 collaboratif     36.46°C 🥵  971‰   ~4 used:0 [3]    source:glm
      $6 #125 multimédia       34.40°C 🥵  952‰   ~5 used:0 [4]    source:glm
      $7 #132 digital          33.27°C 🥵  942‰   ~6 used:0 [5]    source:glm
      $8 #118 ludique          32.05°C 🥵  920‰   ~7 used:0 [6]    source:glm
      $9 #103 échange          28.88°C 😎  865‰   ~8 used:0 [7]    source:glm
     $10  #95 partage          27.19°C 😎  811‰   ~9 used:0 [8]    source:glm
     $11 #127 tactile          27.08°C 😎  805‰  ~10 used:0 [9]    source:glm
     $12  #99 réseau           27.06°C 😎  804‰  ~11 used:0 [10]   source:glm
     $28  #66 connaissance     18.77°C 🥶        ~31 used:1 [30]   source:glm
    $125  #79 étude            -0.03°C 🧊       ~125 used:0 [124]  source:glm

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1697 🥳 225 ⏱️ 0:00:44.794356

🤔 226 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 33 chat prompts
🤖 33 glm-5.3-flash:cloud replies
🔥   1 🥵   9 😎  51 🥶 163 🧊   1

      $1 #226 metal           100.00°C 🥳 1000‰ ~225 used:0  [224]  source:glm
      $2 #157 plastic          51.09°C 🔥  991‰   ~1 used:18 [0]    source:glm
      $3 #179 vinyl            47.63°C 🥵  986‰   ~8 used:6  [7]    source:glm
      $4 #138 wood             45.66°C 🥵  979‰   ~9 used:6  [8]    source:glm
      $5 #109 fiberglass       44.89°C 🥵  971‰   ~6 used:5  [5]    source:glm
      $6 #128 plywood          43.04°C 🥵  958‰   ~7 used:5  [6]    source:glm
      $7 #189 ductile          42.91°C 🥵  957‰   ~2 used:2  [1]    source:glm
      $8  #80 resin            42.88°C 🥵  954‰  ~10 used:9  [9]    source:glm
      $9 #194 material         40.31°C 🥵  916‰   ~3 used:2  [2]    source:glm
     $10 #119 thermoplastic    40.20°C 🥵  913‰   ~4 used:2  [3]    source:glm
     $11 #164 urethane         39.77°C 🥵  900‰   ~5 used:2  [4]    source:glm
     $12  #41 rubber           39.41°C 😎  895‰  ~61 used:8  [60]   source:glm
     $63  #27 grommet          29.04°C 🥶        ~64 used:0  [63]   source:glm
    $226 #211 free             -3.17°C 🧊       ~226 used:0  [225]  source:glm

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1767 🥳 score:21 ⏱️ 0:01:28.051488

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SHARP attempts:5 score:5
2. COPSE attempts:6 score:6
3. REBUT attempts:3 score:3
4. FLECK attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1767 🥳 score:59 ⏱️ 0:02:06.011215

📜 1 sessions

Octordle Classic

1. PLAIN attempts:7 score:7
2. FREER attempts:9 score:9
3. PLAID attempts:5 score:5
4. YOUNG attempts:11 score:11
5. MOIST attempts:10 score:10
6. CLIFF attempts:8 score:8
7. SCOWL attempts:6 score:6
8. BRASH attempts:3 score:3

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1747 🥳 score:39 ⏱️ 0:02:36.078997

📜 1 sessions

Sedecordle Classic sedecordle.com

1. BADGE attempts:16 score:1
2. STAID attempts:17 score:6
3. DROOP attempts:15 score:1
4. TENSE attempts:9 score:5
5. DENIM attempts:11 score:1
6. RUPEE attempts:7 score:1
7. BLOND attempts:14 score:1
8. GREAT attempts:8 score:4
9. FLOOR attempts:5 score:0
10. SHREW attempts:12 score:5
11. PLAIN attempts:10 score:1
12. LINGO attempts:3 score:0
13. GRAVE attempts:18 score:1
14. OUNCE attempts:4 score:8
15. CHAFF attempts:13 score:1
16. ALGAE attempts:6 score:3
