# 2026-06-29

- 🔗 spaceword.org 🧩 2026-06-28 🏁 score 2173 ranked 7.9% 12/152 ⏱️ 0:24:36.938669
- 🔗 alfagok.diginaut.net 🧩 #604 🥳 12 ⏱️ 0:00:20.402578
- 🔗 cemantix.certitudes.org 🧩 #1580 🥳 312 ⏱️ 0:07:40.111955
- 🔗 cemantle.certitudes.org 🧩 #1547 🥳 131 ⏱️ 0:00:49.333948
- 🔗 alphaguess.com 🧩 #1071 🥳 36 ⏱️ 0:00:53.366515
- 🔗 dontwordle.com 🧩 #1497 🥳 6 ⏱️ 0:01:59.349319
- 🔗 dictionary.com hurdle 🧩 #1640 🥳 16 ⏱️ 0:03:18.107058
- 🔗 Quordle Classic 🧩 #1617 🥳 score:20 ⏱️ 0:01:04.659464
- 🔗 Octordle Classic 🧩 #1617 🥳 score:54 ⏱️ 0:03:05.626157
- 🔗 Sedecordle Classic 🧩 #1597 🥳 score:47 ⏱️ 0:11:45.756203
- 🔗 squareword.org 🧩 #1610 🥳 7 ⏱️ 0:01:35.866800

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




















# [spaceword.org](spaceword.org) 🧩 2026-06-28 🏁 score 2173 ranked 7.9% 12/152 ⏱️ 0:24:36.938669

📜 6 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 12/152

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ Y E Z _ _ _   
      _ _ _ _ _ Q _ _ _ _   
      _ _ _ _ N U T _ _ _   
      _ _ _ _ _ A W _ _ _   
      _ _ _ _ _ T O _ _ _   
      _ _ _ _ F O O _ _ _   
      _ _ _ _ E R N _ _ _   
      _ _ _ _ _ _ I _ _ _   
      _ _ _ _ H U E _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #604 🥳 12 ⏱️ 0:00:20.402578

🤔 12 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199556 [199556] lij       q0  ? ␅
    @+199556 [199556] lij       q1  ? after
    @+299533 [299533] schrok    q2  ? ␅
    @+299533 [299533] schrok    q3  ? after
    @+349524 [349524] vakanties q4  ? ␅
    @+349524 [349524] vakanties q5  ? after
    @+361965 [361965] vervolg   q8  ? ␅
    @+361965 [361965] vervolg   q9  ? after
    @+368212 [368212] voedsel   q10 ? ␅
    @+368212 [368212] voedsel   q11 ? it
    @+368212 [368212] voedsel   done. it
    @+374521 [374521] vrijst    q6  ? ␅
    @+374521 [374521] vrijst    q7  ? before

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1580 🥳 312 ⏱️ 0:07:40.111955

🤔 313 attempts
📜 1 sessions
🫧 20 chat sessions
⁉️ 85 chat prompts
🤖 85 dolphin3:latest replies
😱   1 🥵  14 😎  35 🥶 208 🧊  54

      $1 #313 joue           100.00°C 🥳 1000‰ ~259 used:0  [258]  source:dolphin3
      $2 #211 lèvre           47.65°C 😱  999‰   ~1 used:42 [0]    source:dolphin3
      $3 #203 visage          34.23°C 🥵  981‰  ~38 used:12 [37]   source:dolphin3
      $4 #145 nez             33.97°C 🥵  980‰  ~39 used:14 [38]   source:dolphin3
      $5 #283 sourire         33.70°C 🥵  979‰   ~8 used:2  [7]    source:dolphin3
      $6 #264 livide          32.57°C 🥵  966‰   ~9 used:2  [8]    source:dolphin3
      $7 #287 grimacer        31.99°C 🥵  961‰   ~2 used:1  [1]    source:dolphin3
      $8 #144 bouche          31.92°C 🥵  959‰  ~12 used:8  [11]   source:dolphin3
      $9 #114 peau            31.77°C 🥵  956‰  ~40 used:16 [39]   source:dolphin3
     $10 #152 narine          31.14°C 🥵  945‰  ~11 used:7  [10]   source:dolphin3
     $11 #146 oreille         30.82°C 🥵  937‰  ~10 used:5  [9]    source:dolphin3
     $17 #274 palpe           29.06°C 😎  881‰  ~13 used:0  [12]   source:dolphin3
     $52  #78 épilatoire      21.80°C 🥶        ~55 used:0  [54]   source:dolphin3
    $260 #191 côlon           -0.06°C 🧊       ~260 used:0  [259]  source:dolphin3

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1547 🥳 131 ⏱️ 0:00:49.333948

🤔 132 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 14 chat prompts
🤖 14 dolphin3:latest replies
🔥   2 🥵   2 😎   8 🥶 113 🧊   6

      $1 #132 layout           100.00°C 🥳 1000‰ ~126 used:0  [125]  source:dolphin3
      $2 #131 interface         44.77°C 🔥  993‰   ~1 used:0  [0]    source:dolphin3
      $3 #129 geometry          42.90°C 🔥  990‰   ~2 used:0  [1]    source:dolphin3
      $4  #71 topological       37.29°C 🥵  948‰   ~4 used:10 [3]    source:dolphin3
      $5  #89 structure         34.86°C 🥵  906‰   ~3 used:6  [2]    source:dolphin3
      $6  #90 alignment         33.11°C 😎  869‰  ~10 used:2  [9]    source:dolphin3
      $7  #79 feature           31.51°C 😎  817‰  ~11 used:2  [10]   source:dolphin3
      $8  #86 map               30.35°C 😎  744‰   ~5 used:0  [4]    source:dolphin3
      $9  #95 grid              29.69°C 😎  696‰   ~6 used:0  [5]    source:dolphin3
     $10  #51 space             26.15°C 😎  315‰  ~12 used:2  [11]   source:dolphin3
     $11  #73 shape             26.06°C 😎  305‰   ~7 used:0  [6]    source:dolphin3
     $12 #125 connectivity      25.95°C 😎  290‰   ~8 used:0  [7]    source:dolphin3
     $14  #96 integration       24.24°C 🥶        ~19 used:0  [18]   source:dolphin3
    $127 #127 division          -0.73°C 🧊       ~127 used:0  [126]  source:dolphin3

# [alphaguess.com](alphaguess.com) 🧩 #1071 🥳 36 ⏱️ 0:00:53.366515

🤔 36 attempts
📜 1 sessions

    @       [    0] aa          
    @+47380 [47380] dis         q6  ? ␅
    @+47380 [47380] dis         q7  ? ha
    @+47380 [47380] dis         q8  ? ␅
    @+47380 [47380] dis         q9  ? after
    @+60081 [60081] face        q12 ? ␅
    @+60081 [60081] face        q13 ? after
    @+60108 [60108] facet       q28 ? ␅
    @+60108 [60108] facet       q29 ? after
    @+60132 [60132] facile      q30 ? ␅
    @+60132 [60132] facile      q31 ? after
    @+60136 [60136] facilitate  q34 ? ␅
    @+60136 [60136] facilitate  q35 ? it
    @+60136 [60136] facilitate  done. it
    @+60143 [60143] facilitator q32 ? ␅
    @+60143 [60143] facilitator q33 ? before
    @+60154 [60154] fact        q26 ? ␅
    @+60154 [60154] fact        q27 ? before
    @+60228 [60228] fad         q24 ? ␅
    @+60228 [60228] fad         q25 ? before
    @+60426 [60426] fall        q22 ? ␅
    @+60426 [60426] fall        q23 ? before
    @+60848 [60848] fas         q20 ? ␅
    @+60848 [60848] fas         q21 ? before
    @+61617 [61617] fen         q18 ? ␅
    @+61617 [61617] fen         q19 ? before
    @+63237 [63237] flag        q16 ? ␅
    @+63237 [63237] flag        q17 ? before
    @+66437 [66437] french      q14 ? ␅
    @+66437 [66437] french      q15 ? before
    @+72797 [72797] gremolata   q11 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1497 🥳 6 ⏱️ 0:01:59.349319

📜 1 sessions
💰 score: 18

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:7042
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:3521
    ⬜⬜⬜⬜⬜ tried:KOOKY n n n n n remain:1314
    ⬜🟩⬜⬜⬜ tried:GRRRL n Y n n n remain:58
    ⬜🟩🟩🟩⬜ tried:FRASS n Y Y Y n remain:3
    ⬜🟩🟩🟩⬜ tried:CRASH n Y Y Y n remain:2

    Undos used: 4

      2 words remaining
    x 9 unused letters
    = 18 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1640 🥳 16 ⏱️ 0:03:18.107058

📜 1 sessions
💰 score: 10000

    4/6
    TARES 🟨⬜🟨🟨⬜
    RECIT 🟨🟨⬜⬜🟨
    BRUTE ⬜🟨⬜🟨🟨
    ENTRY 🟩🟩🟩🟩🟩
    4/6
    ENTRY ⬜⬜⬜🟨⬜
    SAVOR 🟨⬜⬜⬜🟨
    CRIBS 🟩🟩🟩⬜🟨
    CRISP 🟩🟩🟩🟩🟩
    3/6
    CRISP ⬜⬜⬜🟨🟨
    SPEAK 🟩🟩⬜🟩⬜
    SPLAT 🟩🟩🟩🟩🟩
    4/6
    SPLAT ⬜⬜⬜⬜⬜
    CIDER ⬜⬜🟨⬜⬜
    BOUND ⬜🟩🟩🟩🟩
    FOUND 🟩🟩🟩🟩🟩
    Final 1/2
    TIARA 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1617 🥳 score:20 ⏱️ 0:01:04.659464

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SLURP attempts:4 score:4
2. CRACK attempts:7 score:7
3. CRANK attempts:6 score:6
4. PHONY attempts:3 score:3

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1617 🥳 score:54 ⏱️ 0:03:05.626157

📜 1 sessions

Octordle Classic

1. DRUID attempts:4 score:4
2. UNCLE attempts:5 score:5
3. PULSE attempts:3 score:3
4. SPRIG attempts:6 score:6
5. DEPTH attempts:7 score:7
6. AORTA attempts:8 score:8
7. SKATE attempts:11 score:11
8. NEEDY attempts:10 score:10

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1597 🥳 score:47 ⏱️ 0:11:45.756203

📜 1 sessions

Sedecordle Classic sedecordle.com

1. ETHIC attempts:14 score:1
2. VIDEO attempts:3 score:4
3. BUTCH attempts:15 score:1
4. RADII attempts:19 score:5
5. ODDER attempts:9 score:0
6. HURRY attempts:18 score:9
7. PUNCH attempts:17 score:1
8. SWELL attempts:16 score:7
9. AVIAN attempts:4 score:0
10. CHIDE attempts:13 score:4
11. GRAPE attempts:8 score:0
12. SNAKE attempts:7 score:8
13. BORAX attempts:6 score:0
14. CRIME attempts:12 score:6
15. THROW attempts:10 score:1
16. SPICE attempts:11 score:0

# [squareword.org](squareword.org) 🧩 #1610 🥳 7 ⏱️ 0:01:35.866800

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟩 🟩
    🟩 🟩 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C H A R D
    R A D A R
    O V A R Y
    R E P E L
    E N T R Y
