# 2026-11-18

- 🔗 spaceword.org 🧩 2026-11-17 🏁 score 2170 ranked 38.0% 103/271 ⏱️ 2:33:17.840192
- 🔗 wordgrid 🧩 #900 🌌 rarity:0.08 ⏱️ 0:03:47.463966
- 🔗 alfagok.diginaut.net 🧩 #746 🥳 54 ⏱️ 0:01:02.773256
- 🔗 alphaguess.com 🧩 #1213 🥳 22 ⏱️ 0:00:27.270064
- 🔗 dontwordle.com 🧩 #1639 🥳 6 ⏱️ 0:01:07.886807
- 🔗 dictionary.com hurdle 🧩 #1782 🥳 16 ⏱️ 0:02:14.390689
- 🔗 Quordle Classic 🧩 #1759 🥳 score:25 ⏱️ 0:02:18.985554
- 🔗 Octordle Classic 🧩 #1759 🥳 score:55 ⏱️ 0:01:59.903312
- 🔗 Sedecordle Classic 🧩 #1739 🥳 score:58 ⏱️ 0:07:55.269138
- 🔗 squareword.org 🧩 #1752 🥳 8 ⏱️ 0:02:24.174848
- 🔗 cemantle.certitudes.org 🧩 #1689 🥳 217 ⏱️ 0:00:52.206305
- 🔗 cemantix.certitudes.org 🧩 #1722 🥳 60 ⏱️ 0:00:24.882688

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










# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #900 🌌 rarity:0.08 ⏱️ 0:03:47.463966

📜 2 sessions
🦄 🦄 🌌
🦄 🌌 🌌
🦄 🌌 🌌
Rarity: 0.08 🌌

# [spaceword.org](spaceword.org) 🧩 2026-11-17 🏁 score 2170 ranked 38.0% 103/271 ⏱️ 2:33:17.840192

📜 3 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 103/271

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ H _ _ B O G _ _   
      _ _ I _ K O I _ _ _   
      _ _ N _ A X L E _ _   
      _ _ D A T E _ _ _ _   
      _ _ _ W A D I _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #746 🥳 54 ⏱️ 0:01:02.773256

🤔 54 attempts
📜 1 sessions

    @       [    0] &-teken  
    @+49802 [49802] boks     q8  ? ␅
    @+49802 [49802] boks     q9  ? after
    @+74698 [74698] dc       q10 ? ␅
    @+74698 [74698] dc       q11 ? after
    @+87156 [87156] draag    q12 ? ␅
    @+87156 [87156] draag    q13 ? after
    @+93368 [93368] eet      q14 ? ␅
    @+93368 [93368] eet      q15 ? after
    @+94894 [94894] eiwit    q18 ? ␅
    @+94894 [94894] eiwit    q19 ? after
    @+95227 [95227] elektro  q22 ? ␅
    @+95227 [95227] elektro  q23 ? after
    @+95396 [95396] elf      q24 ? ␅
    @+95396 [95396] elf      q25 ? after
    @+95525 [95525] elite    q26 ? ␅
    @+95525 [95525] elite    q27 ? after
    @+95561 [95561] elixirs  q36 ? ␅
    @+95561 [95561] elixirs  q37 ? after
    @+95570 [95570] elk      q38 ? ␅
    @+95570 [95570] elk      q39 ? after
    @+95571 [95571] elkaar   q52 ? ␅
    @+95571 [95571] elkaar   q53 ? it
    @+95571 [95571] elkaar   done. it
    @+95572 [95572] elkaars  q50 ? ␅
    @+95572 [95572] elkaars  q51 ? before
    @+95573 [95573] elkander q48 ? ␅
    @+95573 [95573] elkander q49 ? before
    @+95575 [95575] elke     q46 ? ␅
    @+95575 [95575] elke     q47 ? before
    @+95582 [95582] elks     q45 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1213 🥳 22 ⏱️ 0:00:27.270064

🤔 22 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+49065 [49065] disturb   q4  ? ␅
    @+49065 [49065] disturb   q5  ? after
    @+61316 [61316] federal   q8  ? ␅
    @+61316 [61316] federal   q9  ? after
    @+62814 [62814] fire      q14 ? ␅
    @+62814 [62814] fire      q15 ? after
    @+63592 [63592] flavones  q16 ? ␅
    @+63592 [63592] flavones  q17 ? after
    @+63777 [63777] flex      q20 ? ␅
    @+63777 [63777] flex      q21 ? it
    @+63777 [63777] flex      done. it
    @+63977 [63977] floc      q18 ? ␅
    @+63977 [63977] floc      q19 ? before
    @+64370 [64370] fluoresce q12 ? ␅
    @+64370 [64370] fluoresce q13 ? before
    @+67436 [67436] fur       q10 ? ␅
    @+67436 [67436] fur       q11 ? before
    @+73596 [73596] guide     q6  ? ␅
    @+73596 [73596] guide     q7  ? before
    @+98138 [98138] mac       q0  ? ␅
    @+98138 [98138] mac       q1  ? after
    @+98138 [98138] mac       q2  ? ␅
    @+98138 [98138] mac       q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1639 🥳 6 ⏱️ 0:01:07.886807

📜 1 sessions
💰 score: 16

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:TEETH n n n n n remain:4651
    ⬜⬜⬜⬜⬜ tried:YUMMY n n n n n remain:2224
    ⬜⬜⬜⬜⬜ tried:OPPOS n n n n n remain:389
    ⬜⬜⬜⬜⬜ tried:JINNI n n n n n remain:72
    ⬜⬜🟩⬜⬜ tried:ABAKA n n Y n n remain:7
    ⬜🟩🟩⬜⬜ tried:DRAFF n Y Y n n remain:2

    Undos used: 2

      2 words remaining
    x 8 unused letters
    = 16 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1782 🥳 16 ⏱️ 0:02:14.390689

📜 1 sessions
💰 score: 10000

    4/6
    LEAST ⬜⬜🟨⬜🟩
    ARGOT 🟨⬜⬜⬜🟩
    HAUNT 🟨🟩⬜⬜🟩
    YACHT 🟩🟩🟩🟩🟩
    3/6
    YACHT ⬜🟨⬜⬜🟩
    ROAST ⬜🟨🟨⬜🟩
    BLOAT 🟩🟩🟩🟩🟩
    5/6
    BLOAT 🟩⬜🟨⬜⬜
    BONUS 🟩🟩⬜⬜⬜
    BORED 🟩🟩⬜🟨⬜
    BOGIE 🟩🟩⬜⬜🟩
    BOCCE 🟩🟩🟩🟩🟩
    3/6
    BOCCE ⬜🟨⬜⬜🟩
    AROSE 🟨🟩🟨⬜🟩
    ORATE 🟩🟩🟩🟩🟩
    Final 1/2
    BROTH 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1759 🥳 score:25 ⏱️ 0:02:18.985554

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. CREEK attempts:7 score:7
2. MACHO attempts:5 score:5
3. SLUSH attempts:9 score:9
4. MINUS attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1759 🥳 score:55 ⏱️ 0:01:59.903312

📜 1 sessions

Octordle Classic

1. RADII attempts:12 score:12
2. REMIT attempts:3 score:3
3. CYNIC attempts:6 score:6
4. POSSE attempts:8 score:8
5. HOTLY attempts:4 score:4
6. BREAD attempts:10 score:10
7. LAUGH attempts:7 score:7
8. SHIRE attempts:5 score:5

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1739 🥳 score:58 ⏱️ 0:07:55.269138

📜 2 sessions

Sedecordle Classic sedecordle.com

1. FIFTH attempts:17 score:1
2. HAREM attempts:14 score:7
3. EVERY attempts:18 score:1
4. LANCE attempts:12 score:8
5. QUEST attempts:5 score:0
6. HYDRO attempts:10 score:5
7. SLEET attempts:7 score:0
8. TATTY attempts:16 score:7
9. GRUNT attempts:17 score:2
10. PERKY attempts:15 score:0
11. SNIFF attempts:8 score:0
12. SWUNG attempts:4 score:8
13. CHASE attempts:19 score:1
14. BUYER attempts:11 score:9
15. BEEFY attempts:9 score:0
16. QUARK attempts:6 score:9

# [squareword.org](squareword.org) 🧩 #1752 🥳 8 ⏱️ 0:02:24.174848

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟨 🟩 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C A R S
    T H R E E
    R E D I D
    A M O N G
    W O R S E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1689 🥳 217 ⏱️ 0:00:52.206305

🤔 218 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 26 chat prompts
🤖 26 glm-5.3-flash:cloud replies
😱   1 🔥   5 🥵  18 😎  40 🥶 146 🧊   7

      $1 #218 translation       100.00°C 🥳 1000‰ ~211 used:0 [210]  source:glm
      $2 #204 transliteration    59.62°C 😱  999‰   ~1 used:5 [0]    source:glm
      $3 #210 language           54.41°C 🔥  998‰   ~2 used:1 [1]    source:glm
      $4 #216 localization       50.74°C 🔥  996‰   ~3 used:0 [2]    source:glm
      $5 #165 pronunciation      48.24°C 🔥  993‰   ~6 used:4 [5]    source:glm
      $6 #217 multilingual       47.09°C 🔥  991‰   ~4 used:0 [3]    source:glm
      $7 #177 phonemic           46.62°C 🔥  990‰   ~5 used:2 [4]    source:glm
      $8 #155 orthography        46.59°C 🥵  989‰  ~23 used:4 [22]   source:glm
      $9 #203 transcription      46.16°C 🥵  987‰   ~7 used:0 [6]    source:glm
     $10 #156 phonetics          44.96°C 🥵  986‰  ~20 used:2 [19]   source:glm
     $11 #139 phonology          44.75°C 🥵  985‰  ~21 used:2 [20]   source:glm
     $26 #120 declension         36.05°C 😎  893‰  ~63 used:3 [62]   source:glm
     $66  #43 approximation      23.89°C 🥶        ~65 used:4 [64]   source:glm
    $212  #53 integral           -0.05°C 🧊       ~212 used:0 [211]  source:glm

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1722 🥳 60 ⏱️ 0:00:24.882688

🤔 61 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 6 chat prompts
🤖 6 glm-5.3-flash:cloud replies
😱  1 🔥  5 🥵  7 😎 16 🥶 30 🧊  1

     $1 #61 ombre          100.00°C 🥳 1000‰ ~60 used:0 [59]  source:glm
     $2 #21 sombre          62.01°C 😱  999‰  ~1 used:6 [0]   source:glm
     $3 #30 obscurité       59.46°C 🔥  996‰  ~5 used:3 [4]   source:glm
     $4 #17 brume           55.29°C 🔥  995‰  ~6 used:3 [5]   source:glm
     $5 #23 crépuscule      54.37°C 🔥  993‰  ~2 used:0 [1]   source:glm
     $6 #42 obscur          52.45°C 🔥  992‰  ~3 used:0 [2]   source:glm
     $7 #46 ténébreux       52.04°C 🔥  991‰  ~4 used:0 [3]   source:glm
     $8 #18 ciel            48.64°C 🥵  976‰  ~7 used:0 [6]   source:glm
     $9 #29 noirceur        47.72°C 🥵  969‰  ~8 used:0 [7]   source:glm
    $10 #44 silence         46.71°C 🥵  964‰  ~9 used:0 [8]   source:glm
    $11 #53 crépusculaire   45.70°C 🥵  954‰ ~10 used:0 [9]   source:glm
    $15 #22 brouillard      42.55°C 😎  899‰ ~14 used:0 [13]  source:glm
    $31 #33 froid           30.15°C 🥶       ~30 used:0 [29]  source:glm
    $61  #1 bibliothèque    -7.14°C 🧊       ~61 used:0 [60]  source:glm
