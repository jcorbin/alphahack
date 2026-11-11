# 2026-11-12

- 🔗 wordgrid 🧩 #894 🟪 rarity:0.26 ⏱️ 0:02:48.661674
- 🔗 spaceword.org 🧩 2026-11-11 🏁 score 2173 ranked 6.9% 21/303 ⏱️ 2:07:00.883074
- 🔗 alfagok.diginaut.net 🧩 #740 🥳 36 ⏱️ 0:00:58.838780
- 🔗 alphaguess.com 🧩 #1207 🥳 28 ⏱️ 0:00:37.941844
- 🔗 dontwordle.com 🧩 #1633 🥳 6 ⏱️ 0:01:34.232837
- 🔗 dictionary.com hurdle 🧩 #1776 🥳 17 ⏱️ 0:02:56.620648
- 🔗 Quordle Classic 🧩 #1753 😦 score:30 ⏱️ 0:02:11.841005
- 🔗 Octordle Classic 🧩 #1753 🥳 score:59 ⏱️ 0:02:00.449421
- 🔗 Sedecordle Classic 🧩 #1733 🥳 score:33 ⏱️ 0:03:41.509662
- 🔗 squareword.org 🧩 #1746 🥳 8 ⏱️ 0:05:08.228950
- 🔗 cemantle.certitudes.org 🧩 #1683 🥳 247 ⏱️ 0:42:35.860473
- 🔗 cemantix.certitudes.org 🧩 #1716 🥳 196 ⏱️ 0:20:04.948297

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




# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #894 🟪 rarity:0.26 ⏱️ 0:02:48.661674

📜 2 sessions
🌌 🦄 🌌
🦄 🌌 🦄
🌌 🌌 🌌
Rarity: 0.26 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-11 🏁 score 2173 ranked 6.9% 21/303 ⏱️ 2:07:00.883074

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 21/303

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ H _ J E T F O I L   
      _ O _ I _ A I _ T E   
      _ W A N K E R _ _ Y   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #740 🥳 36 ⏱️ 0:00:58.838780

🤔 36 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+99672  [ 99672] ex         q2  ? ␅
    @+99672  [ 99672] ex         q3  ? after
    @+149358 [149358] huis       q4  ? ␅
    @+149358 [149358] huis       q5  ? after
    @+174465 [174465] kind       q6  ? ␅
    @+174465 [174465] kind       q7  ? after
    @+187045 [187045] kronen     q10 ? ␅
    @+187045 [187045] kronen     q11 ? after
    @+190269 [190269] la         q12 ? ␅
    @+190269 [190269] la         q13 ? after
    @+194825 [194825] lees       q14 ? ␅
    @+194825 [194825] lees       q15 ? after
    @+195241 [195241] leger      q24 ? ␅
    @+195241 [195241] leger      q25 ? after
    @+195560 [195560] leiders    q26 ? ␅
    @+195560 [195560] leiders    q27 ? after
    @+195719 [195719] leken      q28 ? ␅
    @+195719 [195719] leken      q29 ? after
    @+195760 [195760] lekke      q32 ? ␅
    @+195760 [195760] lekke      q33 ? after
    @+195764 [195764] lekker     q34 ? ␅
    @+195764 [195764] lekker     q35 ? it
    @+195764 [195764] lekker     done. it
    @+195813 [195813] lel        q30 ? ␅
    @+195813 [195813] lel        q31 ? before
    @+195915 [195915] lemsteraak q22 ? ␅
    @+195915 [195915] lemsteraak q23 ? before
    @+197003 [197003] levens     q16 ? ␅
    @+197003 [197003] levens     q17 ? before
    @+199628 [199628] lijk       q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1207 🥳 28 ⏱️ 0:00:37.941844

🤔 28 attempts
📜 1 sessions

    @       [    0] aa       
    @+2     [    2] aahed    
    @+49066 [49066] disturb  q2  ? ␅
    @+49066 [49066] disturb  q3  ? after
    @+61317 [61317] federal  q6  ? ␅
    @+61317 [61317] federal  q7  ? after
    @+67437 [67437] fur      q8  ? ␅
    @+67437 [67437] fur      q9  ? after
    @+70485 [70485] glass    q10 ? ␅
    @+70485 [70485] glass    q11 ? after
    @+72000 [72000] grad     q12 ? ␅
    @+72000 [72000] grad     q13 ? after
    @+72797 [72797] grew     q14 ? ␅
    @+72797 [72797] grew     q15 ? after
    @+72996 [72996] grison   q18 ? ␅
    @+72996 [72996] grison   q19 ? after
    @+73093 [73093] groove   q20 ? ␅
    @+73093 [73093] groove   q21 ? after
    @+73114 [73114] groschen q24 ? ␅
    @+73114 [73114] groschen q25 ? after
    @+73117 [73117] gross    q26 ? ␅
    @+73117 [73117] gross    q27 ? it
    @+73117 [73117] gross    done. it
    @+73134 [73134] grot     q22 ? ␅
    @+73134 [73134] grot     q23 ? before
    @+73194 [73194] grounds  q16 ? ␅
    @+73194 [73194] grounds  q17 ? before
    @+73597 [73597] guide    q4  ? ␅
    @+73597 [73597] guide    q5  ? before
    @+98139 [98139] mac      q0  ? ␅
    @+98139 [98139] mac      q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1633 🥳 6 ⏱️ 0:01:34.232837

📜 2 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:OXBOW n n n n n remain:7173
    ⬜⬜⬜⬜⬜ tried:MUMMY n n n n n remain:3834
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:1829
    ⬜⬜⬜⬜🟨 tried:GRRRL n n n n m remain:329
    ⬜🟨🟨⬜⬜ tried:CLEEK n m m n n remain:53
    ⬜🟩⬜🟩🟩 tried:FILLE n Y n Y Y remain:3

    Undos used: 2

      3 words remaining
    x 8 unused letters
    = 24 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1776 🥳 17 ⏱️ 0:02:56.620648

📜 1 sessions
💰 score: 9900

    3/6
    NEARS ⬜⬜⬜⬜⬜
    DIMLY 🟩⬜⬜⬜⬜
    DOUBT 🟩🟩🟩🟩🟩
    4/6
    DOUBT ⬜⬜🟨🟨⬜
    URBAN 🟨⬜🟨⬜⬜
    BUMPS 🟩🟩⬜⬜🟨
    BUSHY 🟩🟩🟩🟩🟩
    4/6
    BUSHY ⬜⬜⬜⬜⬜
    AIDER ⬜🟨⬜🟨🟨
    TRIPE ⬜🟨🟩⬜🟨
    REIGN 🟩🟩🟩🟩🟩
    5/6
    REIGN 🟩🟩⬜⬜⬜
    REAMS 🟩🟩⬜⬜⬜
    REBUY 🟩🟩⬜⬜🟩
    FAKED ⬜⬜⬜🟨⬜
    REPLY 🟩🟩🟩🟩🟩
    Final 1/2
    GUILE 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1753 😦 score:30 ⏱️ 0:02:11.841005

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. GLOBE attempts:7 score:7
2. MURAL attempts:8 score:8
3. WORTH attempts:6 score:6
4. _RANK -BCDEGHILMOPSTUVW attempts:9 score:-1

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1753 🥳 score:59 ⏱️ 0:02:00.449421

📜 1 sessions

Octordle Classic

1. MOWER attempts:10 score:10
2. RENAL attempts:3 score:3
3. FORGO attempts:8 score:8
4. GAUDY attempts:11 score:11
5. SHUSH attempts:5 score:5
6. MISSY attempts:6 score:6
7. ILIAC attempts:7 score:7
8. HOVER attempts:9 score:9

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1733 🥳 score:33 ⏱️ 0:03:41.509662

📜 2 sessions

Sedecordle Classic sedecordle.com

1. JUMPY attempts:14 score:1
2. FROND attempts:4 score:4
3. FJORD attempts:5 score:0
4. SHALT attempts:17 score:5
5. REEDY attempts:13 score:1
6. MASSE attempts:8 score:3
7. RIVER attempts:15 score:1
8. AGREE attempts:7 score:5
9. TANGY attempts:10 score:1
10. BATTY attempts:18 score:0
11. TULIP attempts:12 score:1
12. RANGE attempts:9 score:2
13. ELOPE attempts:6 score:0
14. SPEAR attempts:11 score:6
15. LURID attempts:3 score:0
16. THROW attempts:19 score:3

# [squareword.org](squareword.org) 🧩 #1746 🥳 8 ⏱️ 0:05:08.228950

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P E A K S
    A T O N E
    S H R E W
    T I T L E
    S C A L D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1683 🥳 247 ⏱️ 0:42:35.860473

🤔 248 attempts
📜 1 sessions
🫧 26 chat sessions
⁉️ 95 chat prompts
🤖 49 dolphin3:latest replies
🤖 46 glm-5.3-flash:cloud replies
🔥   3 🥵  12 😎  52 🥶 172 🧊   8

      $1 #248 regret           100.00°C 🥳 1000‰ ~240 used:0  [239]  source:dolphin3
      $2 #236 sorrow            62.28°C 🔥  998‰   ~3 used:4  [2]    source:dolphin3
      $3 #240 sadness           60.71°C 🔥  997‰   ~1 used:1  [0]    source:dolphin3
      $4 #245 disappointment    58.48°C 🔥  996‰   ~2 used:0  [1]    source:dolphin3
      $5 #104 gratitude         50.17°C 🥵  988‰  ~66 used:69 [65]   source:glm     
      $6 #193 sympathy          46.31°C 🥵  981‰  ~53 used:18 [52]   source:dolphin3
      $7 #246 heartache         45.67°C 🥵  978‰   ~4 used:0  [3]    source:dolphin3
      $8 #237 grief             44.15°C 🥵  974‰   ~5 used:0  [4]    source:dolphin3
      $9 #234 concern           42.34°C 🥵  964‰   ~7 used:2  [6]    source:dolphin3
     $10  #62 admiration        41.82°C 🥵  960‰  ~65 used:45 [64]   source:glm     
     $11 #244 despair           41.41°C 🥵  956‰   ~6 used:0  [5]    source:dolphin3
     $17 #120 thankful          36.12°C 😎  888‰  ~55 used:2  [54]   source:glm     
     $69  #55 contemplation     24.61°C 🥶        ~70 used:0  [69]   source:glm     
    $241 #206 being             -0.19°C 🧊       ~241 used:0  [240]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1716 🥳 196 ⏱️ 0:20:04.948297

🤔 197 attempts
📜 1 sessions
🫧 19 chat sessions
⁉️ 49 chat prompts
🤖 4 dolphin3:latest replies
🤖 45 glm-5.3-flash:cloud replies
🔥   1 🥵   7 😎  32 🥶 140 🧊  16

      $1 #197 continent       100.00°C 🥳 1000‰ ~181 used:0  [180]  source:dolphin3
      $2  #77 océan            47.18°C 🔥  991‰   ~4 used:38 [3]    source:glm     
      $3 #108 île              42.17°C 🥵  977‰   ~7 used:9  [6]    source:glm     
      $4 #131 insulaire        41.74°C 🥵  975‰   ~5 used:4  [4]    source:glm     
      $5 #119 archipel         41.65°C 🥵  974‰   ~6 used:4  [5]    source:glm     
      $6 #136 péninsule        39.09°C 🥵  956‰   ~1 used:3  [0]    source:glm     
      $7  #22 lointain         37.46°C 🥵  942‰  ~40 used:11 [39]   source:glm     
      $8  #70 immense          37.35°C 🥵  940‰   ~2 used:3  [1]    source:glm     
      $9  #54 vaste            35.96°C 🥵  916‰   ~3 used:3  [2]    source:glm     
     $10  #49 immensité        34.58°C 😎  895‰   ~8 used:0  [7]    source:glm     
     $11 #181 caraïbe          34.35°C 😎  890‰   ~9 used:0  [8]    source:glm     
     $12  #78 océanique        34.31°C 😎  885‰  ~10 used:0  [9]    source:glm     
     $42  #28 inconnu          22.58°C 🥶        ~42 used:0  [41]   source:glm     
    $182 #155 navigateur       -0.01°C 🧊       ~182 used:0  [181]  source:glm     
