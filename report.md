# 2026-11-17

- 🔗 spaceword.org 🧩 2026-11-16 🏁 score 2168 ranked 47.5% 144/303 ⏱️ 1:16:20.093870
- 🔗 wordgrid 🧩 #899 🟪 rarity:0.18 ⏱️ 0:04:50.689346
- 🔗 alfagok.diginaut.net 🧩 #745 🥳 34 ⏱️ 0:00:43.615067
- 🔗 alphaguess.com 🧩 #1212 🥳 30 ⏱️ 0:01:16.645981
- 🔗 dontwordle.com 🧩 #1638 🥳 6 ⏱️ 0:01:57.220565
- 🔗 dictionary.com hurdle 🧩 #1781 😦 22 ⏱️ 0:04:50.440251
- 🔗 Quordle Classic 🧩 #1758 🥳 score:29 ⏱️ 0:01:57.710042
- 🔗 Octordle Classic 🧩 #1758 🥳 score:57 ⏱️ 0:02:14.678345
- 🔗 Sedecordle Classic 🧩 #1738 🥳 score:42 ⏱️ 0:02:59.531736
- 🔗 squareword.org 🧩 #1751 🥳 8 ⏱️ 0:03:02.028670
- 🔗 cemantle.certitudes.org 🧩 #1688 🥳 166 ⏱️ 0:00:36.415618
- 🔗 cemantix.certitudes.org 🧩 #1721 🥳 70 ⏱️ 0:00:40.452432

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









# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #899 🟪 rarity:0.18 ⏱️ 0:04:50.689346

📜 2 sessions
🌌 🌌 🌌
🌌 🦄 🦄
🌌 🌌 🌌
Rarity: 0.18 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-16 🏁 score 2168 ranked 47.5% 144/303 ⏱️ 1:16:20.093870

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 144/303

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ C U R _ _ _ _ _ _   
      _ A _ A _ O _ Z _ _   
      _ G _ J E R S E Y _   
      _ E _ A L S I K E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #745 🥳 34 ⏱️ 0:00:43.615067

🤔 34 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+199628 [199628] lijk         q0  ? ␅
    @+199628 [199628] lijk         q1  ? after
    @+199628 [199628] lijk         q2  ? ␅
    @+199628 [199628] lijk         q3  ? after
    @+199628 [199628] lijk         q4  ? ␅
    @+199628 [199628] lijk         q5  ? after
    @+205792 [205792] maatschappij q14 ? ␅
    @+205792 [205792] maatschappij q15 ? after
    @+206548 [206548] mager        q20 ? ␅
    @+206548 [206548] mager        q21 ? after
    @+206932 [206932] majeure      q22 ? ␅
    @+206932 [206932] majeure      q23 ? after
    @+206994 [206994] makelaars    q26 ? ␅
    @+206994 [206994] makelaars    q27 ? after
    @+207014 [207014] makelaren    q30 ? ␅
    @+207014 [207014] makelaren    q31 ? after
    @+207023 [207023] maken        q32 ? ␅
    @+207023 [207023] maken        q33 ? it
    @+207023 [207023] maken        done. it
    @+207033 [207033] makke        q28 ? ␅
    @+207033 [207033] makke        q29 ? before
    @+207070 [207070] mal          q24 ? ␅
    @+207070 [207070] mal          q25 ? before
    @+207315 [207315] mana         q18 ? ␅
    @+207315 [207315] mana         q19 ? before
    @+208843 [208843] markt        q16 ? ␅
    @+208843 [208843] markt        q17 ? before
    @+212011 [212011] media        q12 ? ␅
    @+212011 [212011] media        q13 ? before
    @+224510 [224510] moord        q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1212 🥳 30 ⏱️ 0:01:16.645981

🤔 30 attempts
📜 1 sessions

    @       [    0] aa      
    @+49065 [49065] disturb q2  ? ␅
    @+49065 [49065] disturb q3  ? after
    @+61316 [61316] federal q6  ? ␅
    @+61316 [61316] federal q7  ? after
    @+67436 [67436] fur     q8  ? ␅
    @+67436 [67436] fur     q9  ? after
    @+70484 [70484] glass   q10 ? ␅
    @+70484 [70484] glass   q11 ? after
    @+71213 [71213] goa     q14 ? ␅
    @+71213 [71213] goa     q15 ? after
    @+71404 [71404] goglets q18 ? ␅
    @+71404 [71404] goglets q19 ? after
    @+71407 [71407] going   q28 ? ␅
    @+71407 [71407] going   q29 ? it
    @+71407 [71407] going   done. it
    @+71409 [71409] goiter  q26 ? ␅
    @+71409 [71409] goiter  q27 ? before
    @+71412 [71412] goitre  q24 ? ␅
    @+71412 [71412] goitre  q25 ? before
    @+71424 [71424] gold    q22 ? ␅
    @+71424 [71424] gold    q23 ? before
    @+71497 [71497] gombeen q20 ? ␅
    @+71497 [71497] gombeen q21 ? before
    @+71595 [71595] good    q16 ? ␅
    @+71595 [71595] good    q17 ? before
    @+71999 [71999] grad    q12 ? ␅
    @+71999 [71999] grad    q13 ? before
    @+73596 [73596] guide   q4  ? ␅
    @+73596 [73596] guide   q5  ? before
    @+98138 [98138] mac     q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1638 🥳 6 ⏱️ 0:01:57.220565

📜 1 sessions
💰 score: 49

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:KAKAS n n n n n remain:3559
    ⬜⬜⬜⬜⬜ tried:JEEZE n n n n n remain:1420
    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:618
    ⬜⬜⬜⬜⬜ tried:PUPPY n n n n n remain:136
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:28
    🟨🟩⬜⬜⬜ tried:HOWFF m Y n n n remain:7

    Undos used: 5

      7 words remaining
    x 7 unused letters
    = 49 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1781 😦 22 ⏱️ 0:04:50.440251

📜 2 sessions
💰 score: 4460

    5/6
    RAISE ⬜🟨⬜🟨⬜
    COALS 🟨⬜🟩⬜🟨
    STACK 🟩⬜🟩🟩🟩
    HUMAN 🟨⬜⬜🟨⬜
    SHACK 🟩🟩🟩🟩🟩
    5/6
    SHACK ⬜⬜⬜⬜⬜
    LIROT ⬜🟩🟨⬜⬜
    DIVER 🟨🟩⬜⬜🟨
    CADGY ⬜⬜🟨🟨⬜
    RIGID 🟩🟩🟩🟩🟩
    5/6
    RIGID ⬜⬜🟨⬜⬜
    USAGE ⬜🟨⬜🟨🟨
    LUSTY ⬜⬜🟨⬜⬜
    GECKS 🟩🟩⬜⬜🟩
    GENES 🟩🟩🟩🟩🟩
    5/6
    GENES ⬜⬜⬜⬜⬜
    MACRO ⬜🟩⬜🟨⬜
    RAPID 🟨🟩⬜⬜⬜
    BULKY ⬜⬜⬜🟨⬜
    KARAT 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜⬜⬜⬜🟨
    ????? 🟩⬜🟩🟩⬜

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1758 🥳 score:29 ⏱️ 0:01:57.710042

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SLUNG attempts:7 score:7
2. WAGON attempts:8 score:8
3. TESTY attempts:5 score:5
4. ORGAN attempts:9 score:9

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1758 🥳 score:57 ⏱️ 0:02:14.678345

📜 1 sessions

Octordle Classic

1. STONE attempts:7 score:7
2. QUIRK attempts:9 score:9
3. RURAL attempts:8 score:8
4. OXIDE attempts:3 score:3
5. UPPER attempts:10 score:10
6. BLIND attempts:4 score:4
7. DEBAR attempts:5 score:5
8. SPIKY attempts:11 score:11

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1738 🥳 score:42 ⏱️ 0:02:59.531736

📜 1 sessions

Sedecordle Classic sedecordle.com

1. POUND attempts:6 score:0
2. OPTIC attempts:3 score:6
3. PRIOR attempts:9 score:0
4. KOALA attempts:10 score:9
5. AGENT attempts:14 score:1
6. DRUNK attempts:8 score:4
7. PURSE attempts:5 score:0
8. GONER attempts:15 score:5
9. OUNCE attempts:4 score:0
10. DANDY attempts:17 score:4
11. LURCH attempts:13 score:1
12. WINDY attempts:12 score:3
13. FIBER attempts:16 score:1
14. DODGY attempts:17 score:6
15. BELLE attempts:11 score:1
16. TARDY attempts:7 score:1

# [squareword.org](squareword.org) 🧩 #1751 🥳 8 ⏱️ 0:03:02.028670

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟨 🟨 🟩 🟩 🟨
    🟨 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A S S A Y
    C U T I E
    T I A R A
    O T T E R
    R E E D S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1688 🥳 166 ⏱️ 0:00:36.415618

🤔 167 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 21 chat prompts
🤖 21 glm-5.3-flash:cloud replies
🔥   2 🥵  20 😎  32 🥶 102 🧊  10

      $1 #167 dean            100.00°C 🥳 1000‰ ~157 used:0  [156]  source:glm
      $2  #93 chancellor       54.48°C 🔥  993‰  ~19 used:13 [18]   source:glm
      $3  #88 regent           51.01°C 🔥  990‰  ~18 used:11 [17]   source:glm
      $4 #121 superintendent   50.52°C 🥵  989‰  ~20 used:2  [19]   source:glm
      $5  #56 director         50.46°C 🥵  988‰  ~21 used:5  [20]   source:glm
      $6 #113 administrator    47.37°C 🥵  985‰   ~1 used:0  [0]    source:glm
      $7 #124 university       47.24°C 🥵  983‰   ~2 used:1  [1]    source:glm
      $8  #49 assistant        46.15°C 🥵  981‰  ~22 used:5  [21]   source:glm
      $9  #87 president        44.15°C 🥵  969‰   ~3 used:1  [2]    source:glm
     $10  #81 chairwoman       44.03°C 🥵  968‰   ~4 used:0  [3]    source:glm
     $11  #79 chairman         43.23°C 🥵  961‰   ~5 used:0  [4]    source:glm
     $24  #44 supervisor       34.58°C 😎  895‰  ~52 used:2  [51]   source:glm
     $56 #150 general          19.44°C 🥶        ~51 used:0  [50]   source:glm
    $158  #30 pencil           -0.12°C 🧊       ~158 used:0  [157]  source:glm

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1721 🥳 70 ⏱️ 0:00:40.452432

🤔 71 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 9 chat prompts
🤖 9 glm-5.3-flash:cloud replies
🔥  1 🥵  5 😎 22 🥶 41 🧊  1

     $1 #71 pâte          100.00°C 🥳 1000‰ ~70 used:0 [69]  source:glm
     $2 #63 farine         43.44°C 🔥  990‰  ~1 used:2 [0]   source:glm
     $3 #66 pâtisserie     39.58°C 🥵  983‰  ~2 used:0 [1]   source:glm
     $4 #48 levain         37.23°C 🥵  970‰  ~3 used:1 [2]   source:glm
     $5 #24 mascarpone     36.55°C 🥵  962‰  ~6 used:4 [5]   source:glm
     $6 #61 égouttage      36.30°C 🥵  956‰  ~4 used:0 [3]   source:glm
     $7 #29 caillage       34.13°C 🥵  926‰  ~5 used:2 [4]   source:glm
     $8 #69 levure         32.67°C 😎  897‰  ~7 used:0 [6]   source:glm
     $9 #18 caillé         31.97°C 😎  870‰ ~27 used:3 [26]  source:glm
    $10 #39 tarte          31.81°C 😎  863‰  ~8 used:0 [7]   source:glm
    $11 #31 faisselle      31.66°C 😎  859‰  ~9 used:0 [8]   source:glm
    $12 #59 présure        31.50°C 😎  854‰ ~10 used:0 [9]   source:glm
    $30 #36 petit          20.86°C 🥶       ~29 used:0 [28]  source:glm
    $71  #1 bibliothèque   -1.16°C 🧊       ~71 used:0 [70]  source:glm
