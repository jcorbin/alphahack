# 2026-06-23

- 🔗 spaceword.org 🧩 2026-06-22 🏁 score 2173 ranked 4.5% 14/314 ⏱️ 0:40:11.375746
- 🔗 alfagok.diginaut.net 🧩 #598 🥳 40 ⏱️ 0:00:49.877868
- 🔗 alphaguess.com 🧩 #1065 🥳 22 ⏱️ 0:00:24.320217
- 🔗 dontwordle.com 🧩 #1491 🥳 6 ⏱️ 0:01:37.354994
- 🔗 dictionary.com hurdle 🧩 #1634 🥳 16 ⏱️ 0:04:52.493037
- 🔗 Quordle Classic 🧩 #1611 😦 score:30 ⏱️ 0:02:12.192858
- 🔗 Octordle Classic 🧩 #1611 🥳 score:56 ⏱️ 0:03:54.638196
- 🔗 Sedecordle Classic 🧩 #1591 🥳 score:39 ⏱️ 0:15:05.940956
- 🔗 squareword.org 🧩 #1604 🥳 6 ⏱️ 0:01:47.081053
- 🔗 cemantle.certitudes.org 🧩 #1541 🥳 184 ⏱️ 0:01:29.869145
- 🔗 cemantix.certitudes.org 🧩 #1574 🥳 90 ⏱️ 0:01:07.777102

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














# [spaceword.org](spaceword.org) 🧩 2026-06-22 🏁 score 2173 ranked 4.5% 14/314 ⏱️ 0:40:11.375746

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 14/314

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ O V A _ _ _   
      _ _ _ _ _ _ U _ _ _   
      _ _ _ _ F A B _ _ _   
      _ _ _ _ A N A _ _ _   
      _ _ _ _ _ O D _ _ _   
      _ _ _ _ _ D E _ _ _   
      _ _ _ _ Q I S _ _ _   
      _ _ _ _ _ Z _ _ _ _   
      _ _ _ _ G E N _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #598 🥳 40 ⏱️ 0:00:49.877868

🤔 40 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199761 [199761] lijm      q0  ? ␅
    @+199761 [199761] lijm      q1  ? after
    @+199822 [199822] lijn      q38 ? ␅
    @+199822 [199822] lijn      q39 ? it
    @+199822 [199822] lijn      done. it
    @+199965 [199965] lijst     q36 ? ␅
    @+199965 [199965] lijst     q37 ? before
    @+200294 [200294] lineair   q34 ? ␅
    @+200294 [200294] lineair   q35 ? before
    @+200823 [200823] lis       q30 ? ␅
    @+200823 [200823] lis       q31 ? before
    @+201970 [201970] loo       q28 ? ␅
    @+201970 [201970] loo       q29 ? before
    @+205670 [205670] maas      q26 ? ␅
    @+205670 [205670] maas      q27 ? before
    @+211642 [211642] me        q24 ? ␅
    @+211642 [211642] me        q25 ? before
    @+223513 [223513] mol       q6  ? ␅
    @+223513 [223513] mol       q7  ? before
    @+247623 [247623] op        q4  ? ␅
    @+247623 [247623] op        q5  ? before
    @+299615 [299615] schub     q2  ? ␅
    @+299615 [299615] schub     q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1065 🥳 22 ⏱️ 0:00:24.320217

🤔 22 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+47380 [47380] dis       q4  ? ␅
    @+47380 [47380] dis       q5  ? after
    @+60081 [60081] face      q8  ? ␅
    @+60081 [60081] face      q9  ? after
    @+63237 [63237] flag      q12 ? ␅
    @+63237 [63237] flag      q13 ? after
    @+64034 [64034] flood     q16 ? ␅
    @+64034 [64034] flood     q17 ? after
    @+64194 [64194] flour     q20 ? ␅
    @+64194 [64194] flour     q21 ? it
    @+64194 [64194] flour     done. it
    @+64377 [64377] fluor     q18 ? ␅
    @+64377 [64377] fluor     q19 ? before
    @+64834 [64834] foment    q14 ? ␅
    @+64834 [64834] foment    q15 ? before
    @+66437 [66437] french    q10 ? ␅
    @+66437 [66437] french    q11 ? before
    @+72797 [72797] gremolata q6  ? ␅
    @+72797 [72797] gremolata q7  ? before
    @+98214 [98214] mach      q0  ? ␅
    @+98214 [98214] mach      q1  ? after
    @+98214 [98214] mach      q2  ? ␅
    @+98214 [98214] mach      q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1491 🥳 6 ⏱️ 0:01:37.354994

📜 1 sessions
💰 score: 84

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:7346
    ⬜⬜⬜⬜⬜ tried:MORRO n n n n n remain:2582
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:1278
    ⬜⬜⬜⬜⬜ tried:CHUCK n n n n n remain:425
    ⬜🟩⬜⬜⬜ tried:FEEZE n Y n n n remain:56
    ⬜🟩⬜⬜🟨 tried:PENNA n Y n n m remain:12

    Undos used: 3

      12 words remaining
    x 7 unused letters
    = 84 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1634 🥳 16 ⏱️ 0:04:52.493037

📜 1 sessions
💰 score: 10000

    3/6
    LARES 🟨⬜⬜🟨🟨
    SLEPT 🟩🟨🟩🟨🟩
    SPELT 🟩🟩🟩🟩🟩
    4/6
    SPELT 🟩⬜🟨⬜⬜
    SNARE 🟩⬜🟩🟩🟩
    SCARE 🟩⬜🟩🟩🟩
    SHARE 🟩🟩🟩🟩🟩
    3/6
    SHARE 🟩⬜🟨⬜⬜
    SALON 🟩🟩⬜⬜⬜
    SAUCY 🟩🟩🟩🟩🟩
    5/6
    SAUCY ⬜⬜⬜⬜🟩
    EBONY ⬜⬜⬜⬜🟩
    IMPLY 🟨🟨⬜⬜🟩
    GRIMY ⬜⬜🟨🟩🟩
    JIMMY 🟩🟩🟩🟩🟩
    Final 1/2
    CLOAK 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1611 😦 score:30 ⏱️ 0:02:12.192858

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. ARDOR attempts:7 score:7
2. _ADDY -BCEFGHIKLMNOPRSTVW attempts:9 score:-1
3. SERVE attempts:9 score:9
4. SHEAR attempts:5 score:5

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1611 🥳 score:56 ⏱️ 0:03:54.638196

📜 1 sessions

Octordle Classic

1. UNWED attempts:5 score:5
2. VIPER attempts:11 score:11
3. MIDST attempts:8 score:8
4. THETA attempts:6 score:6
5. ELFIN attempts:3 score:3
6. TWICE attempts:4 score:4
7. SHELL attempts:7 score:7
8. TRIPE attempts:12 score:12

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1591 🥳 score:39 ⏱️ 0:15:05.940956

📜 1 sessions

Sedecordle Classic sedecordle.com

1. ETHIC attempts:4 score:0
2. AMONG attempts:18 score:4
3. ANKLE attempts:8 score:0
4. DETER attempts:9 score:8
5. KNIFE attempts:10 score:1
6. BUSED attempts:19 score:0
7. LEASH attempts:6 score:0
8. LIEGE attempts:15 score:6
9. GULCH attempts:16 score:1
10. PAGAN attempts:17 score:6
11. CRASH attempts:5 score:0
12. MISER attempts:20 score:5
13. GRASS attempts:14 score:1
14. STINK attempts:11 score:4
15. PRAWN attempts:12 score:1
16. SINGE attempts:13 score:2

# [squareword.org](squareword.org) 🧩 #1604 🥳 6 ⏱️ 0:01:47.081053

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C O U T
    C A U S E
    A N N U L
    L O C A L
    P E E L S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1541 🥳 184 ⏱️ 0:01:29.869145

🤔 185 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 18 chat prompts
🤖 18 dolphin3:latest replies
🔥   1 🥵   7 😎  28 🥶 139 🧊   9

      $1 #185 diamond            100.00°C 🥳 1000‰ ~176 used:0 [175]  source:dolphin3
      $2 #184 gemstone            66.54°C 😱  999‰   ~1 used:0 [0]    source:dolphin3
      $3 #154 mining              40.84°C 🥵  963‰   ~4 used:3 [3]    source:dolphin3
      $4 #173 mineral             40.16°C 🥵  960‰   ~2 used:0 [1]    source:dolphin3
      $5  #99 cobalt              39.87°C 🥵  957‰   ~8 used:8 [7]    source:dolphin3
      $6 #108 tungsten            38.90°C 🥵  953‰   ~7 used:5 [6]    source:dolphin3
      $7 #175 ore                 37.22°C 🥵  937‰   ~3 used:0 [2]    source:dolphin3
      $8  #82 carbide             35.72°C 🥵  918‰   ~6 used:4 [5]    source:dolphin3
      $9 #123 nickel              34.84°C 🥵  910‰   ~5 used:3 [4]    source:dolphin3
     $10 #104 metal               32.63°C 😎  868‰   ~9 used:0 [8]    source:dolphin3
     $11 #172 mine                32.20°C 😎  860‰  ~10 used:0 [9]    source:dolphin3
     $12 #171 metallurgical       31.42°C 😎  835‰  ~11 used:0 [10]   source:dolphin3
     $38 #118 gas                 21.53°C 🥶        ~39 used:0 [38]   source:dolphin3
    $177 #181 ventilation         -0.58°C 🧊       ~177 used:0 [176]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1574 🥳 90 ⏱️ 0:01:07.777102

🤔 91 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 17 chat prompts
🤖 17 dolphin3:latest replies
🔥  1 🥵  4 😎  4 🥶 58 🧊 23

     $1 #91 compromis        100.00°C 🥳 1000‰ ~68 used:0  [67]  source:dolphin3
     $2 #59 accord            45.67°C 🔥  990‰  ~1 used:7  [0]   source:dolphin3
     $3 #79 conflit           40.06°C 🥵  974‰  ~2 used:1  [1]   source:dolphin3
     $4 #76 équilibre         38.72°C 🥵  962‰  ~3 used:0  [2]   source:dolphin3
     $5 #26 arrangement       36.50°C 🥵  935‰  ~7 used:11 [6]   source:dolphin3
     $6 #88 réconciliation    34.43°C 🥵  900‰  ~4 used:0  [3]   source:dolphin3
     $7 #89 arbitrage         31.50°C 😎  797‰  ~5 used:0  [4]   source:dolphin3
     $8 #58 convergence       28.59°C 😎  631‰  ~9 used:3  [8]   source:dolphin3
     $9 #34 harmonisation     28.05°C 😎  579‰  ~8 used:2  [7]   source:dolphin3
    $10 #61 cohérence         25.32°C 😎  280‰  ~6 used:0  [5]   source:dolphin3
    $11 #69 rapprochement     22.34°C 🥶       ~12 used:0  [11]  source:dolphin3
    $12 #51 conception        21.23°C 🥶       ~13 used:0  [12]  source:dolphin3
    $13 #84 adhésion          21.17°C 🥶       ~14 used:0  [13]  source:dolphin3
    $69 #28 interlude         -1.70°C 🧊       ~69 used:0  [68]  source:dolphin3
