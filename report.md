# 2026-08-11

- 🔗 spaceword.org 🧩 2026-08-10 🏁 score 2165 ranked 47.3% 151/319 ⏱️ 0:28:16.973442
- 🔗 wordgrid 🧩 #801 🟪 rarity:0.11 ⏱️ 0:03:18.898561
- 🔗 alfagok.diginaut.net 🧩 #647 🥳 18 ⏱️ 0:00:28.870804
- 🔗 alphaguess.com 🧩 #1114 🥳 24 ⏱️ 0:00:31.440237
- 🔗 dontwordle.com 🧩 #1540 😳 6 ⏱️ 0:02:24.563516
- 🔗 dictionary.com hurdle 🧩 #1683 🥳 21 ⏱️ 0:05:22.677498
- 🔗 Quordle Classic 🧩 #1660 🥳 score:21 ⏱️ 0:02:04.101234
- 🔗 Octordle Classic 🧩 #1660 🥳 score:60 ⏱️ 0:02:11.250211
- 🔗 Sedecordle Classic 🧩 #1640 🥳 score:38 ⏱️ 0:03:16.857312
- 🔗 squareword.org 🧩 #1653 🥳 10 ⏱️ 0:03:40.568653
- 🔗 cemantle.certitudes.org 🧩 #1590 🥳 303 ⏱️ 0:03:25.549096
- 🔗 cemantix.certitudes.org 🧩 #1623 🥳 32 ⏱️ 0:00:25.494817

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







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #781 🟪 rarity:0.15 ⏱️ 0:03:50.236694

📜 2 sessions
🌌 🦄 🦄
🌌 🦄 🦄
🌌 🌌 🌌
Rarity: 0.15 🟪


# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #-1 ❗ rarity:nan ⏱️ 0:05:19.095498

📜 2 sessions
🌌 🦄 🌌
🌌 🦄 🌌
🌌 🦄 🌌
Rarity: nan ❗







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #788 🟪 rarity:0.29 ⏱️ 0:03:24.033720

📜 2 sessions
🦄 🦄 🌌
🦄 🦄 🦄
🌌 🦄 🌌
Rarity: 0.29 🟪


# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #789 🟪 rarity:0.23 ⏱️ 0:02:56.015327

📜 2 sessions
🌌 🌌 🌌
🦄 🦄 🌌
🦄 🦄 🦄
Rarity: 0.23 🟪







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #795 🟪 rarity:0.27 ⏱️ 0:03:44.973967

📜 2 sessions
🦄 🌌 🌌
🌌 🌌 🌌
🦄 🦄 🌌
Rarity: 0.27 🟪







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #801 🟪 rarity:0.11 ⏱️ 0:03:18.898561

📜 2 sessions
🦄 🦄 🦄
🦄 🦄 🦄
🌌 🌌 🌌
Rarity: 0.11 🟪

# [spaceword.org](spaceword.org) 🧩 2026-08-10 🏁 score 2165 ranked 47.3% 151/319 ⏱️ 0:28:16.973442

📜 3 sessions
- tiles: 21/21
- score: 2165 bonus: +65
- rank: 151/319

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ D _ G O _ _   
      _ _ _ _ E _ O W _ _   
      _ _ _ R A Z E E D _   
      _ _ Q A N A T _ U _   
      _ _ _ I _ _ H _ H _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #647 🥳 18 ⏱️ 0:00:28.870804

🤔 18 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199652 [199652] lijk      q0  ? ␅
    @+199652 [199652] lijk      q1  ? after
    @+199652 [199652] lijk      q2  ? ␅
    @+199652 [199652] lijk      q3  ? after
    @+249574 [249574] opi       q6  ? ␅
    @+249574 [249574] opi       q7  ? after
    @+274495 [274495] prop      q8  ? ␅
    @+274495 [274495] prop      q9  ? after
    @+275941 [275941] punt      q16 ? ␅
    @+275941 [275941] punt      q17 ? it
    @+275941 [275941] punt      done. it
    @+277399 [277399] radio     q14 ? ␅
    @+277399 [277399] radio     q15 ? before
    @+280663 [280663] redding   q12 ? ␅
    @+280663 [280663] redding   q13 ? before
    @+287011 [287011] riool     q10 ? ␅
    @+287011 [287011] riool     q11 ? before
    @+299568 [299568] schroot   q4  ? ␅
    @+299568 [299568] schroot   q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1114 🥳 24 ⏱️ 0:00:31.440237

🤔 24 attempts
📜 1 sessions

    @       [    0] aa           
    @+1     [    1] aah          
    @+2     [    2] aahed        
    @+3     [    3] aahing       
    @+47378 [47378] dis          q4  ? ␅
    @+47378 [47378] dis          q5  ? after
    @+72662 [72662] green        q6  ? ␅
    @+72662 [72662] green        q7  ? after
    @+85397 [85397] inocula      q8  ? ␅
    @+85397 [85397] inocula      q9  ? after
    @+88583 [88583] jacal        q12 ? ␅
    @+88583 [88583] jacal        q13 ? after
    @+90178 [90178] juvenilities q14 ? ␅
    @+90178 [90178] juvenilities q15 ? after
    @+90552 [90552] kay          q18 ? ␅
    @+90552 [90552] kay          q19 ? after
    @+90639 [90639] keen         q22 ? ␅
    @+90639 [90639] keen         q23 ? it
    @+90639 [90639] keen         done. it
    @+90732 [90732] ken          q20 ? ␅
    @+90732 [90732] ken          q21 ? before
    @+90938 [90938] key          q16 ? ␅
    @+90938 [90938] key          q17 ? before
    @+91772 [91772] knight       q10 ? ␅
    @+91772 [91772] knight       q11 ? before
    @+98147 [98147] mac          q0  ? ␅
    @+98147 [98147] mac          q1  ? after
    @+98147 [98147] mac          q2  ? ␅
    @+98147 [98147] mac          q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1540 😳 6 ⏱️ 0:02:24.563516

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:7346
    ⬜⬜⬜⬜⬜ tried:COMMO n n n n n remain:3291
    ⬜⬜⬜⬜⬜ tried:JUKUS n n n n n remain:843
    ⬜⬜⬜⬜🟨 tried:PHPHT n n n n m remain:147
    🟩⬜🟨🟨⬜ tried:ENTER Y n m m n remain:2
    🟩🟩🟩🟩🟩 tried:ELATE Y Y Y Y Y remain:0

    Undos used: 3

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1683 🥳 21 ⏱️ 0:05:22.677498

📜 1 sessions
💰 score: 9500

    6/6
    SABRE ⬜⬜⬜🟨⬜
    CURIO ⬜🟨🟨⬜⬜
    GRUNT ⬜🟩🟩⬜🟨
    TRULY 🟩🟩🟩⬜⬜
    TRUTH 🟩🟩🟩⬜⬜
    TRUMP 🟩🟩🟩🟩🟩
    5/6
    TRUMP 🟨⬜⬜⬜⬜
    FEAST ⬜⬜🟩🟨🟨
    STANG 🟩🟩🟩⬜⬜
    STALK 🟩🟩🟩⬜🟩
    STACK 🟩🟩🟩🟩🟩
    4/6
    STACK ⬜⬜⬜⬜⬜
    LONER ⬜⬜🟨⬜🟨
    BRING 🟩🟩🟩🟩⬜
    BRINY 🟩🟩🟩🟩🟩
    4/6
    BRINY ⬜🟩🟩⬜⬜
    CRISP 🟨🟩🟩⬜⬜
    TRICK 🟩🟩🟩🟩⬜
    TRICE 🟩🟩🟩🟩🟩
    Final 2/2
    SHLEP 🟩⬜🟨🟩🟩
    SLEEP 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1660 🥳 score:21 ⏱️ 0:02:04.101234

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. ONSET attempts:5 score:5
2. BRAWL attempts:6 score:6
3. TEPID attempts:3 score:3
4. SLANG attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1660 🥳 score:60 ⏱️ 0:02:11.250211

📜 1 sessions

Octordle Classic

1. HEARD attempts:7 score:7
2. VAPID attempts:8 score:8
3. DRILL attempts:4 score:4
4. SOBER attempts:10 score:10
5. DRANK attempts:5 score:5
6. WORRY attempts:9 score:9
7. SHIRK attempts:11 score:11
8. PRINT attempts:6 score:6

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1640 🥳 score:38 ⏱️ 0:03:16.857312

📜 1 sessions

Sedecordle Classic sedecordle.com

1. NUDGE attempts:12 score:1
2. RATIO attempts:4 score:2
3. CAIRN attempts:13 score:1
4. KNEED attempts:14 score:3
5. RADAR attempts:5 score:0
6. FOLLY attempts:9 score:5
7. CRIER attempts:20 score:2
8. IDLER attempts:3 score:1
9. SPICY attempts:15 score:1
10. GLOAT attempts:7 score:5
11. STACK attempts:16 score:1
12. NERVE attempts:17 score:6
13. PIVOT attempts:18 score:1
14. EJECT attempts:19 score:8
15. SKIRT attempts:10 score:1
16. WEIGH attempts:20 score:0

# [squareword.org](squareword.org) 🧩 #1653 🥳 10 ⏱️ 0:03:40.568653

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    H A S T E
    E T H E R
    A R E N A
    R I D E S
    T A S T E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1590 🥳 303 ⏱️ 0:03:25.549096

🤔 304 attempts
📜 1 sessions
🫧 13 chat sessions
⁉️ 61 chat prompts
🤖 61 dolphin3:latest replies
🔥   1 🥵   7 😎  32 🥶 228 🧊  35

      $1 #304 closure          100.00°C 🥳 1000‰ ~269 used:0  [268]  source:dolphin3
      $2 #291 liquidation       45.29°C 🔥  992‰   ~1 used:3  [0]    source:dolphin3
      $3 #280 reorganization    43.50°C 🥵  989‰   ~5 used:8  [4]    source:dolphin3
      $4 #284 downsizing        43.37°C 🥵  987‰   ~4 used:5  [3]    source:dolphin3
      $5 #287 divestiture       40.03°C 🥵  981‰   ~3 used:2  [2]    source:dolphin3
      $6 #201 consolidation     39.59°C 🥵  977‰  ~30 used:30 [29]   source:dolphin3
      $7 #221 expansion         37.13°C 🥵  972‰  ~21 used:19 [20]   source:dolphin3
      $8 #300 reduction         34.84°C 🥵  952‰   ~2 used:0  [1]    source:dolphin3
      $9 #268 construction      30.63°C 🥵  902‰   ~6 used:8  [5]    source:dolphin3
     $10 #292 bankruptcy        30.18°C 😎  889‰   ~7 used:0  [6]    source:dolphin3
     $11 #213 merger            29.99°C 😎  884‰  ~37 used:5  [36]   source:dolphin3
     $12 #263 restoration       29.52°C 😎  868‰  ~22 used:2  [21]   source:dolphin3
     $42 #238 improvement       18.40°C 🥶        ~51 used:0  [50]   source:dolphin3
    $270  #39 mix               -0.01°C 🧊       ~270 used:0  [269]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1623 🥳 32 ⏱️ 0:00:25.494817

🤔 33 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 6 chat prompts
🤖 6 dolphin3:latest replies
🥵  2 😎  6 🥶 13 🧊 11

     $1 #33 attachement   100.00°C 🥳 1000‰ ~22 used:0 [21]  source:dolphin3
     $2 #31 affection      37.23°C 🥵  950‰  ~1 used:2 [0]   source:dolphin3
     $3 #26 fraternité     34.52°C 🥵  924‰  ~2 used:4 [1]   source:dolphin3
     $4 #20 amitié         33.56°C 😎  899‰  ~8 used:2 [7]   source:dolphin3
     $5 #21 amour          28.41°C 😎  706‰  ~3 used:1 [2]   source:dolphin3
     $6 #28 rivalité       24.04°C 😎  256‰  ~4 used:0 [3]   source:dolphin3
     $7 #24 conflit        23.28°C 😎  155‰  ~5 used:0 [4]   source:dolphin3
     $8 #32 affinité       23.26°C 😎  152‰  ~6 used:0 [5]   source:dolphin3
     $9 #27 intimité       22.54°C 😎   41‰  ~7 used:0 [6]   source:dolphin3
    $10 #14 amical         19.27°C 🥶       ~10 used:1 [9]   source:dolphin3
    $11 #22 cohabitation   19.09°C 🥶       ~11 used:0 [10]  source:dolphin3
    $12 #30 éducation      17.25°C 🥶       ~12 used:0 [11]  source:dolphin3
    $13 #15 collègue       13.08°C 🥶       ~13 used:1 [12]  source:dolphin3
    $23 #12 professeur     -0.15°C 🧊       ~23 used:0 [22]  source:dolphin3
