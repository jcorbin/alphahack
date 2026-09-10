# 2026-09-11

- 🔗 spaceword.org 🧩 2026-09-10 🏁 score 2165 ranked 38.9% 136/350 ⏱️ 0:37:28.920870
- 🔗 wordgrid 🧩 #832 🟪 rarity:0.17 ⏱️ 0:02:32.870282
- 🔗 alfagok.diginaut.net 🧩 #678 🥳 26 ⏱️ 0:00:37.261880
- 🔗 alphaguess.com 🧩 #1145 🥳 36 ⏱️ 0:00:36.548533
- 🔗 dontwordle.com 🧩 #1571 🥳 6 ⏱️ 0:01:46.351317
- 🔗 dictionary.com hurdle 🧩 #1714 🥳 19 ⏱️ 0:03:37.234653
- 🔗 Quordle Classic 🧩 #1691 🥳 score:22 ⏱️ 0:01:25.649150
- 🔗 Octordle Classic 🧩 #1691 🥳 score:61 ⏱️ 0:02:19.797069
- 🔗 Sedecordle Classic 🧩 #1671 🥳 score:35 ⏱️ 0:02:18.991313
- 🔗 squareword.org 🧩 #1684 🥳 7 ⏱️ 0:01:43.661520
- 🔗 cemantle.certitudes.org 🧩 #1621 🥳 152 ⏱️ 0:02:28.255080
- 🔗 cemantix.certitudes.org 🧩 #1654 🥳 372 ⏱️ 5:51:34.825091

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

# [spaceword.org](spaceword.org) 🧩 2026-09-10 🏁 score 2165 ranked 38.9% 136/350 ⏱️ 0:37:28.920870

📜 6 sessions
- tiles: 21/21
- score: 2165 bonus: +65
- rank: 136/350

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ G E T A _ _ _ _   
      _ _ _ _ _ X _ _ _ _   
      _ _ _ _ J O _ C _ _   
      _ _ Q U I N O A _ _   
      _ _ I N G E S T A _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #832 🟪 rarity:0.17 ⏱️ 0:02:32.870282

📜 4 sessions
🦄 🦄 🦄
🦄 🦄 🌌
🦄 🌌 🌌
Rarity: 0.17 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #678 🥳 26 ⏱️ 0:00:37.261880

🤔 26 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199640 [199640] lijk      q0  ? ␅
    @+199640 [199640] lijk      q1  ? after
    @+199640 [199640] lijk      q2  ? ␅
    @+199640 [199640] lijk      q3  ? after
    @+299544 [299544] schroot   q4  ? ␅
    @+299544 [299544] schroot   q5  ? after
    @+349329 [349329] vakantie  q6  ? ␅
    @+349329 [349329] vakantie  q7  ? after
    @+352896 [352896] ver       q10 ? ␅
    @+352896 [352896] ver       q11 ? after
    @+363482 [363482] verzout   q12 ? ␅
    @+363482 [363482] verzout   q13 ? after
    @+368489 [368489] voetbal   q14 ? ␅
    @+368489 [368489] voetbal   q15 ? after
    @+368842 [368842] voeten    q20 ? ␅
    @+368842 [368842] voeten    q21 ? after
    @+369017 [369017] voetzool  q22 ? ␅
    @+369017 [369017] voetzool  q23 ? after
    @+369021 [369021] vogel     q24 ? ␅
    @+369021 [369021] vogel     q25 ? it
    @+369021 [369021] vogel     done. it
    @+369198 [369198] vol       q18 ? ␅
    @+369198 [369198] vol       q19 ? before
    @+370338 [370338] voor      q16 ? ␅
    @+370338 [370338] voor      q17 ? before
    @+374067 [374067] vrij      q8  ? ␅
    @+374067 [374067] vrij      q9  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1145 🥳 36 ⏱️ 0:00:36.548533

🤔 36 attempts
📜 1 sessions

    @       [    0] aa          
    @+2     [    2] aahed       
    @+23680 [23680] camp        q4  ? ␅
    @+23680 [23680] camp        q5  ? after
    @+35522 [35522] convention  q6  ? ␅
    @+35522 [35522] convention  q7  ? after
    @+40838 [40838] da          q8  ? ␅
    @+40838 [40838] da          q9  ? after
    @+41548 [41548] day         q14 ? ␅
    @+41548 [41548] day         q15 ? after
    @+41651 [41651] dead        q18 ? ␅
    @+41651 [41651] dead        q19 ? after
    @+41696 [41696] deadness    q30 ? ␅
    @+41696 [41696] deadness    q31 ? after
    @+41716 [41716] deaerations q32 ? ␅
    @+41716 [41716] deaerations q33 ? after
    @+41719 [41719] deaf        q34 ? ␅
    @+41719 [41719] deaf        q35 ? it
    @+41719 [41719] deaf        done. it
    @+41736 [41736] deal        q20 ? ␅
    @+41736 [41736] deal        q21 ? before
    @+41829 [41829] deb         q16 ? ␅
    @+41829 [41829] deb         q17 ? before
    @+42369 [42369] deco        q12 ? ␅
    @+42369 [42369] deco        q13 ? before
    @+44066 [44066] den         q10 ? ␅
    @+44066 [44066] den         q11 ? before
    @+47374 [47374] dis         q2  ? ␅
    @+47374 [47374] dis         q3  ? before
    @+98143 [98143] mac         q0  ? ␅
    @+98143 [98143] mac         q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1571 🥳 6 ⏱️ 0:01:46.351317

📜 1 sessions
💰 score: 21

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:HEEZE n n n n n remain:5957
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:3265
    ⬜⬜⬜⬜⬜ tried:COCOS n n n n n remain:622
    ⬜⬜⬜⬜⬜ tried:KNURR n n n n n remain:117
    ⬜🟩⬜⬜⬜ tried:FATWA n Y n n n remain:21
    ⬜🟩🟨⬜🟩 tried:YABBY n Y m n Y remain:3

    Undos used: 5

      3 words remaining
    x 7 unused letters
    = 21 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1714 🥳 19 ⏱️ 0:03:37.234653

📜 2 sessions
💰 score: 9700

    4/6
    YEARS 🟨⬜🟨⬜⬜
    YAPON 🟨🟩⬜⬜⬜
    YACHT 🟨🟩🟨⬜🟨
    CATTY 🟩🟩🟩🟩🟩
    4/6
    CATTY ⬜⬜⬜⬜🟩
    DOPEY 🟩⬜⬜⬜🟩
    DIMLY 🟩🟩⬜🟩🟩
    DILLY 🟩🟩🟩🟩🟩
    4/6
    DILLY 🟨⬜⬜⬜⬜
    SAROD ⬜🟨⬜⬜🟩
    ANTED 🟩🟨⬜🟨🟩
    AMEND 🟩🟩🟩🟩🟩
    5/6
    AMEND ⬜⬜🟨⬜🟨
    SLIDE ⬜⬜⬜🟩🟩
    CRUDE ⬜⬜🟩🟩🟩
    EXUDE 🟩⬜🟩🟩🟩
    ETUDE 🟩🟩🟩🟩🟩
    Final 2/2
    FIGHT ⬜⬜⬜🟨⬜
    HOLLY 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1691 🥳 score:22 ⏱️ 0:01:25.649150

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. PLUSH attempts:7 score:7
2. PAINT attempts:6 score:6
3. RIVAL attempts:5 score:5
4. AFOUL attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1691 🥳 score:61 ⏱️ 0:02:19.797069

📜 1 sessions

Octordle Classic

1. EVENT attempts:4 score:4
2. FLAKY attempts:12 score:12
3. BEGIN attempts:6 score:6
4. NOBLY attempts:5 score:5
5. UNFIT attempts:8 score:8
6. FLIRT attempts:7 score:7
7. CLASH attempts:10 score:10
8. PROVE attempts:9 score:9

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1671 🥳 score:35 ⏱️ 0:02:18.991313

📜 1 sessions

Sedecordle Classic sedecordle.com

1. SHARE attempts:7 score:0
2. QUEEN attempts:9 score:7
3. THRUM attempts:3 score:0
4. SPEAK attempts:8 score:3
5. DODGE attempts:12 score:1
6. RETRY attempts:6 score:2
7. WARTY attempts:5 score:0
8. WAIST attempts:4 score:5
9. NYMPH attempts:10 score:1
10. SHOUT attempts:11 score:0
11. POISE attempts:13 score:1
12. SENSE attempts:17 score:3
13. HONEY attempts:14 score:1
14. ROUGH attempts:15 score:4
15. DINER attempts:16 score:1
16. GUMBO attempts:17 score:6

# [squareword.org](squareword.org) 🧩 #1684 🥳 7 ⏱️ 0:01:43.661520

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P L A T
    C H A F E
    R O S I N
    I N E R T
    P Y R E S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1621 🥳 152 ⏱️ 0:02:28.255080

🤔 153 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 53 chat prompts
🤖 53 dolphin3:latest replies
🔥  3 🥵 16 😎 32 🥶 99 🧊  2

      $1 #153 worthy             100.00°C 🥳 1000‰ ~151 used:0  [150]  source:dolphin3
      $2  #93 noble               49.41°C 🔥  993‰  ~17 used:27 [16]   source:dolphin3
      $3  #94 praiseworthy        48.73°C 🔥  992‰  ~16 used:22 [15]   source:dolphin3
      $4  #89 admirable           47.05°C 🔥  991‰   ~3 used:16 [2]    source:dolphin3
      $5  #90 commendable         42.65°C 🥵  986‰   ~4 used:2  [3]    source:dolphin3
      $6  #88 laudable            40.87°C 🥵  981‰   ~5 used:2  [4]    source:dolphin3
      $7 #132 edifying            38.46°C 🥵  961‰   ~6 used:2  [5]    source:dolphin3
      $8 #142 exemplary           38.28°C 🥵  960‰   ~7 used:2  [6]    source:dolphin3
      $9 #137 ennobling           38.25°C 🥵  958‰   ~8 used:2  [7]    source:dolphin3
     $10  #92 meritorious         37.83°C 🥵  950‰   ~9 used:2  [8]    source:dolphin3
     $11  #98 estimable           37.29°C 🥵  940‰  ~10 used:2  [9]    source:dolphin3
     $21 #111 honorable           35.26°C 😎  888‰  ~19 used:0  [18]   source:dolphin3
     $53 #123 philanthropic       26.41°C 🥶        ~59 used:0  [58]   source:dolphin3
    $152   #3 computer            -0.73°C 🧊       ~152 used:0  [151]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1654 🥳 372 ⏱️ 5:51:34.825091

🤔 373 attempts
📜 1 sessions
🫧 27 chat sessions
⁉️ 129 chat prompts
🤖 71 dolphin3:latest replies
🤖 17 gemma3:27b replies
🤖 18 gemma4:12b replies
🤖 22 ornith-1.5:35b replies
😱   1 🔥   2 🥵   7 😎  52 🥶 276 🧊  34

      $1 #373 épuiser          100.00°C 🥳 1000‰ ~339 used:0   [338]  source:dolphin3
      $2 #142 épuisement        59.72°C 😱  999‰   ~1 used:129 [0]    source:dolphin3
      $3 #166 épuisant          41.94°C 🔥  992‰   ~8 used:49  [7]    source:dolphin3
      $4 #250 inanition         40.69°C 🔥  991‰   ~2 used:26  [1]    source:gemma4  
      $5 #140 fatigue           38.57°C 🥵  983‰  ~49 used:11  [48]   source:dolphin3
      $6 #164 épuisé            38.32°C 🥵  982‰   ~3 used:3   [2]    source:dolphin3
      $7 #353 endormir          36.82°C 🥵  978‰   ~4 used:3   [3]    source:dolphin3
      $8 #348 éreinter          36.63°C 🥵  976‰   ~5 used:3   [4]    source:dolphin3
      $9 #136 lassitude         36.07°C 🥵  972‰   ~9 used:5   [8]    source:dolphin3
     $10 #350 fatigant          32.69°C 🥵  932‰   ~6 used:3   [5]    source:dolphin3
     $11 #165 exsangue          32.19°C 🥵  922‰   ~7 used:3   [6]    source:dolphin3
     $12 #336 frénésie          30.62°C 😎  869‰  ~10 used:0   [9]    source:gemma3  
     $64 #273 effort            22.59°C 🥶        ~73 used:0   [72]   source:gemma4  
    $340 #155 apraxie           -0.07°C 🧊       ~340 used:0   [339]  source:dolphin3
