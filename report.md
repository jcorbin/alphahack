# 2026-09-20

- 🔗 spaceword.org 🧩 2026-09-19 🏁 score 2168 ranked 40.6% 134/330 ⏱️ 0:57:42.078631
- 🔗 wordgrid 🧩 #841 🟪 rarity:0.37 ⏱️ 0:03:03.335265
- 🔗 alfagok.diginaut.net 🧩 #687 🥳 32 ⏱️ 0:00:48.356178
- 🔗 alphaguess.com 🧩 #1154 🥳 38 ⏱️ 0:00:44.278017
- 🔗 dontwordle.com 🧩 #1580 🥳 6 ⏱️ 0:01:50.717348
- 🔗 cemantix.certitudes.org 🧩 #1663 🥳 109 ⏱️ 0:01:35.864349
- 🔗 cemantle.certitudes.org 🧩 #1630 🥳 48 ⏱️ 0:00:54.276961
- 🔗 dictionary.com hurdle 🧩 #1723 🥳 15 ⏱️ 0:02:24.647172
- 🔗 Quordle Classic 🧩 #1700 🥳 score:22 ⏱️ 0:01:19.033783
- 🔗 Octordle Classic 🧩 #1700 🥳 score:52 ⏱️ 0:01:19.024132
- 🔗 Sedecordle Classic 🧩 #1680 🥳 score:50 ⏱️ 0:02:36.712130
- 🔗 squareword.org 🧩 #1693 🥳 8 ⏱️ 0:02:42.637623

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









# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 2026-09-17 🤔 rarity:nan ⏱️ 0:00:25.671340

📜 1 sessions
❓ ❓ ❓
❓ ❓ ❓
❓ ❓ ❓



# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #841 🟪 rarity:0.37 ⏱️ 0:03:03.335265

📜 3 sessions
🦄 🦄 🦄
🌌 🌌 🦄
🦄 🟪 🌌
Rarity: 0.37 🟪

# [spaceword.org](spaceword.org) 🧩 2026-09-19 🏁 score 2168 ranked 40.6% 134/330 ⏱️ 0:57:42.078631

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 134/330

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ J U S _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ _ R E Z _ _ _   
      _ _ _ _ U _ I _ _ _   
      _ _ _ _ B _ N _ _ _   
      _ _ _ H I V E _ _ _   
      _ _ _ A E _ _ _ _ _   
      _ _ _ T R A M _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #687 🥳 32 ⏱️ 0:00:48.356178

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+99675  [ 99675] ex          q2  ? ␅
    @+99675  [ 99675] ex          q3  ? after
    @+124574 [124574] gevoel      q6  ? ␅
    @+124574 [124574] gevoel      q7  ? after
    @+130744 [130744] gras        q10 ? ␅
    @+130744 [130744] gras        q11 ? after
    @+132214 [132214] groen       q14 ? ␅
    @+132214 [132214] groen       q15 ? after
    @+132928 [132928] grond       q16 ? ␅
    @+132928 [132928] grond       q17 ? after
    @+133401 [133401] grondwater  q18 ? ␅
    @+133401 [133401] grondwater  q19 ? after
    @+133518 [133518] groot       q20 ? ␅
    @+133518 [133518] groot       q21 ? after
    @+133706 [133706] grootouder  q22 ? ␅
    @+133706 [133706] grootouder  q23 ? after
    @+133754 [133754] grootte     q26 ? ␅
    @+133754 [133754] grootte     q27 ? after
    @+133763 [133763] grootvader  q30 ? ␅
    @+133763 [133763] grootvader  q31 ? it
    @+133763 [133763] grootvader  done. it
    @+133778 [133778] grootvizier q28 ? ␅
    @+133778 [133778] grootvizier q29 ? before
    @+133801 [133801] grootzeil   q24 ? ␅
    @+133801 [133801] grootzeil   q25 ? before
    @+133903 [133903] grove       q12 ? ␅
    @+133903 [133903] grove       q13 ? before
    @+137060 [137060] handt       q8  ? ␅
    @+137060 [137060] handt       q9  ? before
    @+149570 [149570] huishoud    q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1154 🥳 38 ⏱️ 0:00:44.278017

🤔 38 attempts
📜 1 sessions

    @        [     0] aa          
    @+98142  [ 98142] mac         q0  ? ␅
    @+98142  [ 98142] mac         q1  ? after
    @+122719 [122719] parol       q4  ? ␅
    @+122719 [122719] parol       q5  ? after
    @+123681 [123681] pe          q12 ? ␅
    @+123681 [123681] pe          q13 ? after
    @+124638 [124638] pep         q14 ? ␅
    @+124638 [124638] pep         q15 ? after
    @+124735 [124735] per         q16 ? ␅
    @+124735 [124735] per         q17 ? after
    @+124846 [124846] peregrin    q22 ? ␅
    @+124846 [124846] peregrin    q23 ? after
    @+124882 [124882] perfect     q24 ? ␅
    @+124882 [124882] perfect     q25 ? after
    @+124927 [124927] perforation q26 ? ␅
    @+124927 [124927] perforation q27 ? after
    @+124945 [124945] perfume     q28 ? ␅
    @+124945 [124945] perfume     q29 ? after
    @+124959 [124959] perfuse     q30 ? ␅
    @+124959 [124959] perfuse     q31 ? after
    @+124963 [124963] perfusion   q32 ? ␅
    @+124963 [124963] perfusion   q33 ? after
    @+124968 [124968] pergola     q34 ? ␅
    @+124968 [124968] pergola     q35 ? after
    @+124970 [124970] perhaps     q36 ? ␅
    @+124970 [124970] perhaps     q37 ? it
    @+124970 [124970] perhaps     done. it
    @+124972 [124972] peri        q20 ? ␅
    @+124972 [124972] peri        q21 ? before
    @+125218 [125218] perm        q19 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1580 🥳 6 ⏱️ 0:01:50.717348

📜 1 sessions
💰 score: 99

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:ZANZA n n n n n remain:5808
    ⬜⬜⬜⬜⬜ tried:ESSES n n n n n remain:1158
    ⬜⬜⬜⬜⬜ tried:FLUFF n n n n n remain:452
    ⬜⬜⬜⬜⬜ tried:HOOCH n n n n n remain:64
    ⬜⬜🟨⬜⬜ tried:BRITT n n m n n remain:21
    ⬜🟩⬜⬜⬜ tried:VIVID n Y n n n remain:11

    Undos used: 4

      11 words remaining
    x 9 unused letters
    = 99 total score

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1663 🥳 109 ⏱️ 0:01:35.864349

🤔 110 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 12 chat prompts
🤖 12 gemma4:12b replies
🔥  1 🥵  7 😎 25 🥶 68 🧊  8

      $1 #110 descente       100.00°C 🥳 1000‰ ~102 used:0 [101]  source:gemma4
      $2  #56 dénivelé        57.14°C 🔥  996‰   ~1 used:7 [0]    source:gemma4
      $3  #73 virage          53.41°C 🥵  988‰   ~8 used:2 [7]    source:gemma4
      $4  #64 pente           52.26°C 🥵  984‰   ~2 used:1 [1]    source:gemma4
      $5  #99 ascension       48.51°C 🥵  972‰   ~3 used:0 [2]    source:gemma4
      $6 #109 col             47.34°C 🥵  968‰   ~4 used:0 [3]    source:gemma4
      $7 #107 canyon          44.15°C 🥵  956‰   ~5 used:0 [4]    source:gemma4
      $8  #93 crête           41.80°C 🥵  938‰   ~6 used:0 [5]    source:gemma4
      $9  #82 passage         40.38°C 🥵  929‰   ~7 used:0 [6]    source:gemma4
     $10  #89 altitude        37.38°C 😎  887‰   ~9 used:0 [8]    source:gemma4
     $11  #35 route           37.27°C 😎  885‰  ~31 used:4 [30]   source:gemma4
     $12 #101 déclivité       34.10°C 😎  815‰  ~10 used:0 [9]    source:gemma4
     $35  #20 entraînement    23.30°C 🥶        ~34 used:0 [33]   source:gemma4
    $103  #70 sécurité        -0.55°C 🧊       ~103 used:0 [102]  source:gemma4

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1630 🥳 48 ⏱️ 0:00:54.276961

🤔 49 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 8 chat prompts
🤖 8 gemma4:12b replies
😎 10 🥶 36 🧊  2

     $1 #49 projection      100.00°C 🥳 1000‰ ~47 used:0 [46]  source:gemma4
     $2 #40 ellipsoid        25.77°C 😎  778‰  ~1 used:0 [0]   source:gemma4
     $3 #36 curvature        24.81°C 😎  713‰  ~7 used:3 [6]   source:gemma4
     $4 #29 spherical        23.18°C 😎  524‰  ~9 used:4 [8]   source:gemma4
     $5 #48 parabola         22.97°C 😎  481‰  ~2 used:0 [1]   source:gemma4
     $6 #23 convex           22.64°C 😎  433‰ ~10 used:4 [9]   source:gemma4
     $7 #22 concave          22.45°C 😎  411‰  ~8 used:3 [7]   source:gemma4
     $8 #38 distortion       21.83°C 😎  299‰  ~3 used:0 [2]   source:gemma4
     $9 #24 diagonal         21.10°C 😎  139‰  ~4 used:1 [3]   source:gemma4
    $10 #46 metric           21.08°C 😎  133‰  ~5 used:0 [4]   source:gemma4
    $11 #43 isometric        20.58°C 😎    8‰  ~6 used:0 [5]   source:gemma4
    $12 #33 arc              19.90°C 🥶       ~13 used:0 [12]  source:gemma4
    $13 #12 polygon          19.72°C 🥶       ~12 used:2 [11]  source:gemma4
    $48 #10 sourdough        -1.37°C 🧊       ~48 used:0 [47]  source:gemma4

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1723 🥳 15 ⏱️ 0:02:24.647172

📜 1 sessions
💰 score: 10100

    3/6
    STALE 🟨⬜🟩⬜⬜
    ROANS ⬜🟨🟩⬜🟩
    CHAOS 🟩🟩🟩🟩🟩
    3/6
    CHAOS 🟨⬜⬜⬜⬜
    ERUCT ⬜🟩🟩🟩🟨
    TRUCK 🟩🟩🟩🟩🟩
    4/6
    TRUCK ⬜⬜⬜⬜⬜
    DALES ⬜⬜🟨⬜🟨
    SHILY 🟩⬜🟩🟩⬜
    SPILL 🟩🟩🟩🟩🟩
    4/6
    SPILL 🟨⬜⬜⬜⬜
    AROSE ⬜⬜🟨🟨🟨
    OMENS 🟩⬜🟨🟨🟨
    ONSET 🟩🟩🟩🟩🟩
    Final 1/2
    PINKY 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1700 🥳 score:22 ⏱️ 0:01:19.033783

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. DERBY attempts:5 score:5
2. LIMBO attempts:4 score:4
3. GAWKY attempts:6 score:6
4. REIGN attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1700 🥳 score:52 ⏱️ 0:01:19.024132

📜 1 sessions

Octordle Classic

1. RAINY attempts:3 score:3
2. HOWDY attempts:10 score:10
3. COLON attempts:4 score:4
4. PENNE attempts:8 score:8
5. TIARA attempts:6 score:6
6. MARCH attempts:5 score:5
7. DRUID attempts:9 score:9
8. CRYPT attempts:7 score:7

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1680 🥳 score:50 ⏱️ 0:02:36.712130

📜 1 sessions

Sedecordle Classic sedecordle.com

1. VIRUS attempts:13 score:1
2. VALVE attempts:14 score:3
3. BAGGY attempts:16 score:1
4. TEDDY attempts:7 score:6
5. CONIC attempts:18 score:1
6. BLACK attempts:15 score:8
7. SHIRK attempts:11 score:1
8. SPEND attempts:6 score:1
9. FOIST attempts:18 score:1
10. STAGE attempts:2 score:9
11. PERCH attempts:8 score:0
12. REMIT attempts:17 score:8
13. IDLER attempts:10 score:1
14. SCREE attempts:4 score:0
15. DOWNY attempts:9 score:0
16. CHEST attempts:5 score:9

# [squareword.org](squareword.org) 🧩 #1693 🥳 8 ⏱️ 0:02:42.637623

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟩 🟨
    🟨 🟨 🟨 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    H E N C E
    A L O H A
    R I V E R
    S T E E L
    H E L P S
