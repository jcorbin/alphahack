# 2026-11-13

- 🔗 spaceword.org 🧩 2026-11-12 🏁 score 2160 ranked 60.1% 172/286 ⏱️ 4:59:28.421326
- 🔗 alfagok.diginaut.net 🧩 #741 🥳 40 ⏱️ 0:00:57.332456
- 🔗 alphaguess.com 🧩 #1208 🥳 34 ⏱️ 0:00:41.105853
- 🔗 dontwordle.com 🧩 #1634 🥳 6 ⏱️ 0:01:14.650072
- 🔗 dictionary.com hurdle 🧩 #1777 🥳 21 ⏱️ 0:02:46.406656
- 🔗 Quordle Classic 🧩 #1754 🥳 score:23 ⏱️ 0:01:18.826723
- 🔗 Octordle Classic 🧩 #1754 🥳 score:58 ⏱️ 0:01:57.918848
- 🔗 Sedecordle Classic 🧩 #1734 🥳 score:48 ⏱️ 0:02:45.023649
- 🔗 squareword.org 🧩 #1747 🥳 7 ⏱️ 0:01:40.971947
- 🔗 cemantle.certitudes.org 🧩 #1684 🥳 142 ⏱️ 0:00:39.466827
- 🔗 cemantix.certitudes.org 🧩 #1717 🥳 43 ⏱️ 0:00:23.963007
- 🔗 wordgrid 🧩 #895 🟪 rarity:0.14 ⏱️ 0:01:58.485063

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





# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #895 🟪 rarity:0.14 ⏱️ 0:01:58.485063

📜 2 sessions
🦄 🌌 🌌
🦄 🦄 🦄
🦄 🌌 🌌
Rarity: 0.14 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-12 🏁 score 2160 ranked 60.1% 172/286 ⏱️ 4:59:28.421326

📜 2 sessions
- tiles: 21/21
- score: 2160 bonus: +60
- rank: 172/286

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ N A _ _   
      _ _ _ _ _ B E D _ _   
      _ _ _ R Y E _ I _ _   
      _ _ _ _ _ Z _ E _ _   
      _ _ _ _ _ I _ U _ _   
      _ _ _ _ _ Q _ X _ _   
      _ _ _ T O U R _ _ _   
      _ _ _ _ H E _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #741 🥳 40 ⏱️ 0:00:57.332456

🤔 40 attempts
📜 1 sessions

    @        [     0] &-teken       
    @+199631 [199631] lijk          q0  ? ␅
    @+199631 [199631] lijk          q1  ? after
    @+199631 [199631] lijk          q2  ? ␅
    @+199631 [199631] lijk          q3  ? after
    @+249538 [249538] opi           q6  ? ␅
    @+249538 [249538] opi           q7  ? after
    @+274454 [274454] prop          q8  ? ␅
    @+274454 [274454] prop          q9  ? after
    @+286965 [286965] riool         q10 ? ␅
    @+286965 [286965] riool         q11 ? after
    @+291978 [291978] sa            q12 ? ␅
    @+291978 [291978] sa            q13 ? after
    @+295745 [295745] schelde       q14 ? ␅
    @+295745 [295745] schelde       q15 ? after
    @+297625 [297625] schone        q16 ? ␅
    @+297625 [297625] schone        q17 ? after
    @+298572 [298572] schot         q18 ? ␅
    @+298572 [298572] schot         q19 ? after
    @+299047 [299047] schrijf       q20 ? ␅
    @+299047 [299047] schrijf       q21 ? after
    @+299153 [299153] schrijfster   q24 ? ␅
    @+299153 [299153] schrijfster   q25 ? after
    @+299198 [299198] schrijn       q26 ? ␅
    @+299198 [299198] schrijn       q27 ? after
    @+299211 [299211] schrijnwerk   q30 ? ␅
    @+299211 [299211] schrijnwerk   q31 ? after
    @+299213 [299213] schrijnwerker q34 ? ␅
    @+299213 [299213] schrijnwerker q35 ? after
    @+299218 [299218] schrijvelaar  q36 ? ␅
    @+299218 [299218] schrijvelaar  q37 ? after

# [alphaguess.com](alphaguess.com) 🧩 #1208 🥳 34 ⏱️ 0:00:41.105853

🤔 34 attempts
📜 1 sessions

    @        [     0] aa        
    @+98139  [ 98139] mac       q0  ? ␅
    @+98139  [ 98139] mac       q1  ? after
    @+147300 [147300] rho       q2  ? ␅
    @+147300 [147300] rho       q3  ? after
    @+171899 [171899] tag       q4  ? ␅
    @+171899 [171899] tag       q5  ? after
    @+181984 [181984] un        q6  ? ␅
    @+181984 [181984] un        q7  ? after
    @+189246 [189246] vicar     q8  ? ␅
    @+189246 [189246] vicar     q9  ? after
    @+192850 [192850] whir      q10 ? ␅
    @+192850 [192850] whir      q11 ? after
    @+194674 [194674] worship   q12 ? ␅
    @+194674 [194674] worship   q13 ? after
    @+195588 [195588] yo        q14 ? ␅
    @+195588 [195588] yo        q15 ? after
    @+195701 [195701] you       q20 ? ␅
    @+195701 [195701] you       q21 ? after
    @+195757 [195757] ytterbias q22 ? ␅
    @+195757 [195757] ytterbias q23 ? after
    @+195786 [195786] yuk       q24 ? ␅
    @+195786 [195786] yuk       q25 ? after
    @+195799 [195799] yulan     q26 ? ␅
    @+195799 [195799] yulan     q27 ? after
    @+195805 [195805] yum       q28 ? ␅
    @+195805 [195805] yum       q29 ? after
    @+195809 [195809] yumminess q30 ? ␅
    @+195809 [195809] yumminess q31 ? after
    @+195811 [195811] yummy     q33 ? it
    @+195811 [195811] yummy     done. it

# [dontwordle.com](dontwordle.com) 🧩 #1634 🥳 6 ⏱️ 0:01:14.650072

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:EGGED n n n n n remain:5334
    ⬜⬜⬜⬜⬜ tried:ANNAL n n n n n remain:1467
    ⬜⬜⬜⬜⬜ tried:TOOTH n n n n n remain:316
    ⬜⬜⬜⬜⬜ tried:PUPPY n n n n n remain:66
    ⬜🟨⬜⬜⬜ tried:CIRRI n m n n n remain:5
    🟩⬜🟩⬜⬜ tried:SWIMS Y n Y n n remain:1

    Undos used: 3

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1777 🥳 21 ⏱️ 0:02:46.406656

📜 1 sessions
💰 score: 9500

    4/6
    AROSE 🟨⬜⬜⬜⬜
    LANKY 🟨🟨⬜🟨⬜
    BLACK ⬜🟨🟩🟨🟩
    CHALK 🟩🟩🟩🟩🟩
    6/6
    CHALK ⬜⬜⬜⬜⬜
    EOSIN 🟨🟩⬜⬜⬜
    DOWER ⬜🟩⬜🟩🟩
    VOTER ⬜🟩⬜🟩🟩
    GOFER 🟨🟩⬜🟩🟩
    ROGER 🟩🟩🟩🟩🟩
    4/6
    ROGER ⬜🟨⬜🟨⬜
    SLOPE ⬜⬜🟨🟨🟨
    DEPOT ⬜🟩🟨🟩⬜
    BEBOP 🟩🟩🟩🟩🟩
    5/6
    BEBOP ⬜🟨⬜🟨⬜
    WORSE ⬜🟩⬜⬜🟨
    LODEN ⬜🟩🟨🟩🟩
    DOVEN 🟩🟩⬜🟩🟩
    DOZEN 🟩🟩🟩🟩🟩
    Final 2/2
    TALCS ⬜🟨🟩🟨⬜
    LILAC 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1754 🥳 score:23 ⏱️ 0:01:18.826723

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. BRAND attempts:5 score:5
2. FIBER attempts:6 score:6
3. STOOL attempts:4 score:4
4. STASH attempts:8 score:8

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1754 🥳 score:58 ⏱️ 0:01:57.918848

📜 2 sessions

Octordle Classic

1. AGAPE attempts:10 score:10
2. AMEND attempts:9 score:9
3. WAIST attempts:5 score:5
4. SPITE attempts:4 score:4
5. THING attempts:8 score:8
6. TOUGH attempts:7 score:7
7. PASTA attempts:3 score:3
8. COUCH attempts:12 score:12

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1734 🥳 score:48 ⏱️ 0:02:45.023649

📜 1 sessions

Sedecordle Classic sedecordle.com

1. TWICE attempts:4 score:0
2. FIBER attempts:17 score:4
3. FINER attempts:16 score:1
4. WOODY attempts:13 score:6
5. EXTOL attempts:7 score:0
6. HOLLY attempts:14 score:7
7. BRINE attempts:5 score:0
8. QUICK attempts:10 score:5
9. HEART attempts:6 score:0
10. CONDO attempts:11 score:6
11. KNEAD attempts:9 score:0
12. LOCAL attempts:18 score:9
13. ONSET attempts:8 score:0
14. CHORE attempts:12 score:8
15. APRON attempts:2 score:0
16. SHIFT attempts:15 score:2

# [squareword.org](squareword.org) 🧩 #1747 🥳 7 ⏱️ 0:01:40.971947

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟩 🟨
    🟨 🟩 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S O R E S
    C R A V E
    U D D E R
    B E I N G
    A R I S E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1684 🥳 142 ⏱️ 0:00:39.466827

🤔 143 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 16 chat prompts
🤖 16 glm-5.3-flash:cloud replies
🔥   1 🥵   4 😎  17 🥶 115 🧊   5

      $1 #143 equation        100.00°C 🥳 1000‰ ~138 used:0 [137]  source:glm
      $2 #138 formula          42.23°C 🔥  994‰   ~1 used:2 [0]    source:glm
      $3 #141 calculation      39.94°C 🥵  988‰   ~2 used:0 [1]    source:glm
      $4  #87 criterion        36.10°C 🥵  971‰   ~4 used:8 [3]    source:glm
      $5  #93 metric           32.69°C 🥵  923‰   ~3 used:6 [2]    source:glm
      $6  #71 means            31.68°C 🥵  908‰   ~5 used:8 [4]    source:glm
      $7 #106 yardstick        31.32°C 😎  899‰   ~6 used:0 [5]    source:glm
      $8  #82 measure          29.77°C 😎  852‰   ~7 used:1 [6]    source:glm
      $9  #48 approach         29.53°C 😎  837‰   ~8 used:0 [7]    source:glm
     $10 #133 strategy         28.35°C 😎  775‰   ~9 used:0 [8]    source:glm
     $11  #96 parameter        27.97°C 😎  751‰  ~10 used:0 [9]    source:glm
     $12  #27 way              27.40°C 😎  713‰  ~22 used:4 [21]   source:glm
     $24 #116 indicator        21.86°C 🥶        ~24 used:0 [23]   source:glm
    $139 #112 diagnostic       -0.13°C 🧊       ~139 used:0 [138]  source:glm

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1717 🥳 43 ⏱️ 0:00:23.963007

🤔 44 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 7 chat prompts
🤖 7 glm-5.3-flash:cloud replies
🥵  8 😎  7 🥶 28

     $1 #44 flot        100.00°C 🥳 1000‰ ~44 used:0 [43]  source:glm
     $2 #19 rivage       44.92°C 🥵  977‰  ~8 used:5 [7]   source:glm
     $3 #34 océan        44.06°C 🥵  973‰  ~6 used:2 [5]   source:glm
     $4 #26 brise        41.93°C 🥵  965‰  ~1 used:1 [0]   source:glm
     $5 #43 déferlante   41.48°C 🥵  961‰  ~2 used:0 [1]   source:glm
     $6 #31 houle        41.17°C 🥵  955‰  ~3 used:1 [2]   source:glm
     $7 #11 brume        39.70°C 🥵  941‰  ~7 used:4 [6]   source:glm
     $8 #39 tempête      39.05°C 🥵  931‰  ~4 used:0 [3]   source:glm
     $9 #23 marée        37.92°C 🥵  914‰  ~5 used:1 [4]   source:glm
    $10 #32 jetée        34.30°C 😎  812‰  ~9 used:0 [8]   source:glm
    $11 #40 abysse       31.95°C 😎  690‰ ~10 used:0 [9]   source:glm
    $12  #7 nuage        31.93°C 😎  687‰ ~11 used:1 [10]  source:glm
    $13  #1 bateau       30.74°C 😎  583‰ ~12 used:0 [11]  source:glm
    $17 #12 brouillard   25.22°C 🥶       ~16 used:0 [15]  source:glm
