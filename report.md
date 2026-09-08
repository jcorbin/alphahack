# 2026-09-09

- 🔗 spaceword.org 🧩 2026-09-08 🏁 score 2164 ranked 46.3% 168/363 ⏱️ 0:17:11.609977
- 🔗 wordgrid 🧩 #830 🟪 rarity:0.32 ⏱️ 0:06:55.901180
- 🔗 alfagok.diginaut.net 🧩 #676 🥳 38 ⏱️ 0:00:51.355856
- 🔗 alphaguess.com 🧩 #1143 🥳 44 ⏱️ 0:00:40.022769
- 🔗 dontwordle.com 🧩 #1569 🥳 6 ⏱️ 0:01:22.904998
- 🔗 dictionary.com hurdle 🧩 #1712 🥳 20 ⏱️ 0:03:07.406897
- 🔗 Quordle Classic 🧩 #1689 🥳 score:22 ⏱️ 0:01:32.607876
- 🔗 Octordle Classic 🧩 #1689 🥳 score:54 ⏱️ 0:02:24.383488
- 🔗 Sedecordle Classic 🧩 #1669 🥳 score:46 ⏱️ 0:02:15.491597
- 🔗 squareword.org 🧩 #1682 🥳 8 ⏱️ 0:02:18.072180
- 🔗 cemantle.certitudes.org 🧩 #1619 🥳 305 ⏱️ 0:04:14.206610
- 🔗 cemantix.certitudes.org 🧩 #1652 🥳 82 ⏱️ 0:01:28.758896

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


# [spaceword.org](spaceword.org) 🧩 2026-09-08 🏁 score 2164 ranked 46.3% 168/363 ⏱️ 0:17:11.609977

📜 5 sessions
- tiles: 21/21
- score: 2164 bonus: +64
- rank: 168/363

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ J _ _ A G   
      _ _ _ _ _ U M _ L A   
      _ _ _ B E T A X E D   
      _ Q U I R E D _ E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #830 🟪 rarity:0.32 ⏱️ 0:06:55.901180

📜 3 sessions
🌌 🌌 🌌
🌌 🌌 🦄
🌌 🌌 🦄
Rarity: 0.32 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #676 🥳 38 ⏱️ 0:00:51.355856

🤔 38 attempts
📜 1 sessions

    @        [     0] &-teken        
    @+99681  [ 99681] ex             q4  ? ␅
    @+99681  [ 99681] ex             q5  ? after
    @+111336 [111336] ge             q8  ? ␅
    @+111336 [111336] ge             q9  ? after
    @+115974 [115974] gek            q14 ? ␅
    @+115974 [115974] gek            q15 ? after
    @+118331 [118331] geluk          q16 ? ␅
    @+118331 [118331] geluk          q17 ? after
    @+118730 [118730] gemeente       q20 ? ␅
    @+118730 [118730] gemeente       q21 ? after
    @+119151 [119151] gemoderniseerd q22 ? ␅
    @+119151 [119151] gemoderniseerd q23 ? after
    @+119304 [119304] gen            q24 ? ␅
    @+119304 [119304] gen            q25 ? after
    @+119423 [119423] genees         q26 ? ␅
    @+119423 [119423] genees         q27 ? after
    @+119494 [119494] genegen        q28 ? ␅
    @+119494 [119494] genegen        q29 ? after
    @+119531 [119531] gener          q30 ? ␅
    @+119531 [119531] gener          q31 ? after
    @+119533 [119533] generaal       q36 ? ␅
    @+119533 [119533] generaal       q37 ? it
    @+119533 [119533] generaal       done. it
    @+119537 [119537] generaals      q34 ? ␅
    @+119537 [119537] generaals      q35 ? before
    @+119549 [119549] generaliseer   q32 ? ␅
    @+119549 [119549] generaliseer   q33 ? before
    @+119570 [119570] generatie      q18 ? ␅
    @+119570 [119570] generatie      q19 ? before
    @+120826 [120826] gepunt         q13 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1143 🥳 44 ⏱️ 0:00:40.022769

🤔 44 attempts
📜 1 sessions

    @        [     0] aa       
    @+98147  [ 98147] mac      q0  ? ␅
    @+98147  [ 98147] mac      q1  ? after
    @+98147  [ 98147] mac      q2  ? ␅
    @+98147  [ 98147] mac      q3  ? after
    @+98147  [ 98147] mac      q4  ? ␅
    @+98147  [ 98147] mac      q5  ? after
    @+147311 [147311] rho      q6  ? ␅
    @+147311 [147311] rho      q7  ? after
    @+171911 [171911] tag      q8  ? ␅
    @+171911 [171911] tag      q9  ? after
    @+181996 [181996] un       q10 ? ␅
    @+181996 [181996] un       q11 ? after
    @+189258 [189258] vicar    q12 ? ␅
    @+189258 [189258] vicar    q13 ? after
    @+192862 [192862] whir     q14 ? ␅
    @+192862 [192862] whir     q15 ? after
    @+193477 [193477] win      q18 ? ␅
    @+193477 [193477] win      q19 ? after
    @+193602 [193602] windsurf q24 ? ␅
    @+193602 [193602] windsurf q25 ? after
    @+193648 [193648] wing     q26 ? ␅
    @+193648 [193648] wing     q27 ? after
    @+193690 [193690] wining   q28 ? ␅
    @+193690 [193690] wining   q29 ? after
    @+193692 [193692] wink     q32 ? ␅
    @+193692 [193692] wink     q33 ? after
    @+193698 [193698] winkle   q34 ? ␅
    @+193698 [193698] winkle   q35 ? after
    @+193704 [193704] winks    q36 ? ␅
    @+193704 [193704] winks    q37 ? after

# [dontwordle.com](dontwordle.com) 🧩 #1569 🥳 6 ⏱️ 0:01:22.904998

📜 1 sessions
💰 score: 5

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:7870
    ⬜⬜⬜⬜⬜ tried:EDGED n n n n n remain:2937
    ⬜⬜⬜⬜⬜ tried:WAZOO n n n n n remain:383
    ⬜⬜⬜⬜⬜ tried:FLYBY n n n n n remain:111
    ⬜⬜🟩⬜⬜ tried:CHUCK n n Y n n remain:10
    🟩🟨🟩⬜⬜ tried:STUNS Y m Y n n remain:1

    Undos used: 4

      1 words remaining
    x 5 unused letters
    = 5 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1712 🥳 20 ⏱️ 0:03:07.406897

📜 1 sessions
💰 score: 9600

    6/6
    REAIS 🟨🟨⬜⬜🟩
    OGRES ⬜⬜🟨🟨🟩
    PREYS ⬜🟩🟩⬜🟩
    TREWS ⬜🟩🟩⬜🟩
    CREDS 🟩🟩🟩⬜🟩
    CRESS 🟩🟩🟩🟩🟩
    4/6
    CRESS 🟨⬜⬜⬜⬜
    HOICK ⬜⬜⬜🟩⬜
    TALCY ⬜🟩⬜🟩🟩
    FANCY 🟩🟩🟩🟩🟩
    5/6
    FANCY ⬜⬜🟨⬜⬜
    NORIS 🟨⬜⬜🟨⬜
    INTEL 🟨🟨⬜🟨⬜
    DEIGN ⬜🟩🟩🟨🟨
    BEING 🟩🟩🟩🟩🟩
    4/6
    BEING ⬜🟨⬜⬜⬜
    RASED ⬜🟩⬜🟩⬜
    LACEY 🟨🟩⬜🟩⬜
    HAZEL 🟩🟩🟩🟩🟩
    Final 1/2
    THUMB 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1689 🥳 score:22 ⏱️ 0:01:32.607876

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. HAPPY attempts:8 score:8
2. GONER attempts:7 score:7
3. SMACK attempts:3 score:3
4. MOTIF attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1689 🥳 score:54 ⏱️ 0:02:24.383488

📜 1 sessions

Octordle Classic

1. GENIE attempts:6 score:6
2. MOGUL attempts:7 score:7
3. TILDE attempts:3 score:3
4. SPARK attempts:10 score:10
5. POUTY attempts:4 score:4
6. HAPPY attempts:11 score:11
7. ANNUL attempts:5 score:5
8. SNOWY attempts:8 score:8

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1669 🥳 score:46 ⏱️ 0:02:15.491597

📜 1 sessions

Sedecordle Classic sedecordle.com

1. FREER attempts:9 score:0
2. CREAM attempts:12 score:9
3. BLADE attempts:17 score:1
4. STUCK attempts:11 score:7
5. ABODE attempts:16 score:1
6. KNEEL attempts:8 score:6
7. MUSTY attempts:14 score:1
8. TRUST attempts:15 score:4
9. LIGHT attempts:3 score:0
10. INPUT attempts:5 score:3
11. CHAFF attempts:13 score:1
12. RISER attempts:7 score:3
13. RERUN attempts:6 score:0
14. DUMMY attempts:18 score:6
15. UNTIL attempts:4 score:0
16. SISSY attempts:10 score:4

# [squareword.org](squareword.org) 🧩 #1682 🥳 8 ⏱️ 0:02:18.072180

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟩
    🟩 🟩 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S L O S H
    H I P P O
    A V I A N
    F E N C E
    T R E E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1619 🥳 305 ⏱️ 0:04:14.206610

🤔 306 attempts
📜 1 sessions
🫧 13 chat sessions
⁉️ 70 chat prompts
🤖 70 dolphin3:latest replies
😱   1 🔥   4 🥵  37 😎  81 🥶 178 🧊   4

      $1 #306 tired            100.00°C 🥳 1000‰ ~302 used:0  [301]  source:dolphin3
      $2 #288 fatigued          68.37°C 😱  999‰   ~1 used:9  [0]    source:dolphin3
      $3 #293 weary             66.51°C 🔥  998‰   ~2 used:1  [1]    source:dolphin3
      $4 #134 frustrated        61.40°C 🔥  995‰  ~41 used:45 [40]   source:dolphin3
      $5 #143 irritated         57.28°C 🔥  994‰  ~38 used:33 [37]   source:dolphin3
      $6 #137 annoyed           56.96°C 🔥  993‰  ~18 used:18 [17]   source:dolphin3
      $7 #208 impatient         55.09°C 🔥  990‰  ~17 used:11 [16]   source:dolphin3
      $8 #292 exhausted         54.64°C 🥵  989‰   ~3 used:0  [2]    source:dolphin3
      $9 #148 restless          51.69°C 🥵  983‰  ~19 used:2  [18]   source:dolphin3
     $10 #141 exasperated       50.88°C 🥵  981‰  ~20 used:2  [19]   source:dolphin3
     $11 #212 cranky            50.36°C 🥵  979‰  ~21 used:2  [20]   source:dolphin3
     $44 #213 furious           40.60°C 😎  887‰  ~43 used:0  [42]   source:dolphin3
    $125 #138 bitter            28.68°C 🥶       ~129 used:0  [128]  source:dolphin3
    $303  #70 undetermined      -0.53°C 🧊       ~303 used:0  [302]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1652 🥳 82 ⏱️ 0:01:28.758896

🤔 83 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 23 chat prompts
🤖 23 dolphin3:latest replies
😱  1 🔥  1 🥵  3 😎 28 🥶 41 🧊  8

     $1 #83 pilier          100.00°C 🥳 1000‰ ~75 used:0  [74]  source:dolphin3
     $2 #54 socle            49.59°C 😱  999‰  ~1 used:6  [0]   source:dolphin3
     $3 #65 voûte            46.56°C 🔥  998‰  ~2 used:4  [1]   source:dolphin3
     $4 #51 contrefort       34.47°C 🥵  968‰  ~5 used:2  [4]   source:dolphin3
     $5 #71 poutre           32.92°C 🥵  948‰  ~3 used:0  [2]   source:dolphin3
     $6 #62 imposte          31.38°C 🥵  936‰  ~4 used:0  [3]   source:dolphin3
     $7 #61 encorbellement   28.94°C 😎  898‰  ~6 used:0  [5]   source:dolphin3
     $8 #69 fronton          28.55°C 😎  889‰  ~7 used:0  [6]   source:dolphin3
     $9 #48 brique           28.37°C 😎  883‰  ~8 used:0  [7]   source:dolphin3
    $10 #26 mur              27.89°C 😎  871‰ ~33 used:11 [32]  source:dolphin3
    $11 #23 granit           27.34°C 😎  848‰ ~32 used:7  [31]  source:dolphin3
    $12 #29 pierre           26.83°C 😎  827‰ ~29 used:3  [28]  source:dolphin3
    $35 #55 appui            17.99°C 🥶       ~35 used:0  [34]  source:dolphin3
    $76 #20 boulder          -0.76°C 🧊       ~76 used:0  [75]  source:dolphin3
