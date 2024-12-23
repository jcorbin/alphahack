# 2026-09-18

- 🔗 spaceword.org 🧩 2026-09-17 🏁 score 2172 ranked 21.0% 76/362 ⏱️ 4:50:04.842632
- 🔗 wordgrid 🧩 #839 🟪 rarity:0.17 ⏱️ 0:02:53.065444
- 🔗 alfagok.diginaut.net 🧩 #685 🥳 40 ⏱️ 0:00:49.428750
- 🔗 alphaguess.com 🧩 #1152 🥳 26 ⏱️ 0:00:32.326053
- 🔗 dontwordle.com 🧩 #1578 🥳 6 ⏱️ 0:01:36.412210
- 🔗 dictionary.com hurdle 🧩 #1721 😦 17 ⏱️ 0:04:46.177048
- 🔗 Quordle Classic 🧩 #1698 🥳 score:23 ⏱️ 0:02:06.014664
- 🔗 Octordle Classic 🧩 #1698 🥳 score:60 ⏱️ 0:01:58.333560
- 🔗 Sedecordle Classic 🧩 #1678 🥳 score:44 ⏱️ 0:02:26.722327
- 🔗 squareword.org 🧩 #1691 🥳 9 ⏱️ 0:03:34.515276
- 🔗 cemantle.certitudes.org 🧩 #1628 🥳 124 ⏱️ 0:22:07.292860
- 🔗 cemantix.certitudes.org 🧩 #1661 🥳 72 ⏱️ 0:00:46.415032

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









# [spaceword.org](spaceword.org) 🧩 2026-09-17 🏁 score 2172 ranked 21.0% 76/362 ⏱️ 4:50:04.842632

📜 4 sessions
- tiles: 21/21
- score: 2172 bonus: +72
- rank: 76/362

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ L A X _ G _ S _   
      _ _ I _ _ G O _ O _   
      _ _ T O W I E _ K _   
      _ _ _ P O T S I E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 2026-09-17 🤔 rarity:nan ⏱️ 0:00:25.671340

📜 1 sessions
❓ ❓ ❓
❓ ❓ ❓
❓ ❓ ❓

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #839 🟪 rarity:0.17 ⏱️ 0:02:53.065444

📜 3 sessions
🦄 🦄 🌌
🦄 🦄 🌌
🦄 🦄 🌌
Rarity: 0.17 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #685 🥳 40 ⏱️ 0:00:49.428750

🤔 40 attempts
📜 1 sessions

    @        [     0] &-teken       
    @+99675  [ 99675] ex            q2  ? ␅
    @+99675  [ 99675] ex            q3  ? after
    @+124574 [124574] gevoel        q6  ? ␅
    @+124574 [124574] gevoel        q7  ? after
    @+137060 [137060] handt         q8  ? ␅
    @+137060 [137060] handt         q9  ? after
    @+139014 [139014] he            q10 ? ␅
    @+139014 [139014] he            q11 ? after
    @+139549 [139549] hef           q18 ? ␅
    @+139549 [139549] hef           q19 ? after
    @+139549 [139549] hef           q20 ? ␅
    @+139549 [139549] hef           q21 ? after
    @+139552 [139552] hefboom       q28 ? ␅
    @+139552 [139552] hefboom       q29 ? after
    @+139568 [139568] hefboomsarmen q30 ? ␅
    @+139568 [139568] hefboomsarmen q31 ? after
    @+139576 [139576] hefeiland     q32 ? ␅
    @+139576 [139576] hefeiland     q33 ? after
    @+139578 [139578] heffe         q34 ? ␅
    @+139578 [139578] heffe         q35 ? after
    @+139580 [139580] heffen        q38 ? ␅
    @+139580 [139580] heffen        q39 ? it
    @+139580 [139580] heffen        done. it
    @+139581 [139581] heffer        q36 ? ␅
    @+139581 [139581] heffer        q37 ? before
    @+139583 [139583] heffing       q26 ? ␅
    @+139583 [139583] heffing       q27 ? before
    @+139698 [139698] hei           q24 ? ␅
    @+139698 [139698] hei           q25 ? before
    @+139896 [139896] heilig        q23 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1152 🥳 26 ⏱️ 0:00:32.326053

🤔 26 attempts
📜 1 sessions

    @        [     0] aa      
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98142  [ 98142] mac     q0  ? ␅
    @+98142  [ 98142] mac     q1  ? after
    @+122719 [122719] parol   q4  ? ␅
    @+122719 [122719] parol   q5  ? after
    @+134999 [134999] prop    q6  ? ␅
    @+134999 [134999] prop    q7  ? after
    @+134999 [134999] prop    q8  ? ␅
    @+134999 [134999] prop    q9  ? after
    @+141012 [141012] recon   q10 ? ␅
    @+141012 [141012] recon   q11 ? after
    @+144145 [144145] rend    q12 ? ␅
    @+144145 [144145] rend    q13 ? after
    @+144403 [144403] rep     q18 ? ␅
    @+144403 [144403] rep     q19 ? after
    @+144519 [144519] repel   q20 ? ␅
    @+144519 [144519] repel   q21 ? after
    @+144582 [144582] repin   q22 ? ␅
    @+144582 [144582] repin   q23 ? after
    @+144619 [144619] replay  q24 ? ␅
    @+144619 [144619] replay  q25 ? it
    @+144619 [144619] replay  done. it
    @+144659 [144659] replica q16 ? ␅
    @+144659 [144659] replica q17 ? before
    @+145183 [145183] res     q14 ? ␅
    @+145183 [145183] res     q15 ? before
    @+147306 [147306] rho     q2  ? ␅
    @+147306 [147306] rho     q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1578 🥳 6 ⏱️ 0:01:36.412210

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:7266
    ⬜⬜⬜⬜⬜ tried:DOODY n n n n n remain:3005
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:1338
    ⬜⬜⬜⬜⬜ tried:JUGUM n n n n n remain:513
    ⬜🟨⬜⬜⬜ tried:CANNA n m n n n remain:64
    ⬜⬜🟩🟩⬜ tried:FRASS n n Y Y n remain:1

    Undos used: 2

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1721 😦 17 ⏱️ 0:04:46.177048

📜 2 sessions
💰 score: 2170

    5/6
    LEARS ⬜🟩⬜⬜⬜
    TEPID ⬜🟩⬜⬜🟨
    BENDY ⬜🟩⬜🟨🟩
    CHEVY 🟨⬜🟨⬜🟩
    DECOY 🟩🟩🟩🟩🟩
    6/6
    DECOY 🟩⬜⬜⬜⬜
    DINAR 🟩⬜⬜🟨🟨
    KLONG ⬜⬜⬜⬜⬜
    DARTS 🟩🟨🟨⬜⬜
    EMBOW ⬜🟨⬜⬜⬜
    DRAMA 🟩🟩🟩🟩🟩
    6/6
    ????? ⬜⬜⬜⬜⬜
    ????? 🟨⬜⬜⬜⬜
    ????? ⬜🟩⬜🟩🟩
    ????? ⬜🟩⬜🟩🟩
    ????? ⬜⬜⬜⬜⬜
    ????? ⬜🟩🟨🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1698 🥳 score:23 ⏱️ 0:02:06.014664

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. MUCUS attempts:8 score:8
2. MIRTH attempts:4 score:4
3. APPLE attempts:6 score:6
4. TILDE attempts:5 score:5

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1698 🥳 score:60 ⏱️ 0:01:58.333560

📜 1 sessions

Octordle Classic

1. SUSHI attempts:6 score:6
2. COUGH attempts:9 score:9
3. PINCH attempts:12 score:12
4. MODEL attempts:7 score:7
5. CREED attempts:10 score:10
6. LUSTY attempts:3 score:3
7. MOUSE attempts:5 score:5
8. CADET attempts:8 score:8

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1678 🥳 score:44 ⏱️ 0:02:26.722327

📜 1 sessions

Sedecordle Classic sedecordle.com

1. MARCH attempts:10 score:1
2. REGAL attempts:3 score:0
3. SUNNY attempts:6 score:0
4. DRAMA attempts:11 score:6
5. APPLY attempts:12 score:1
6. MOUND attempts:13 score:2
7. LARGE attempts:2 score:0
8. SPOOL attempts:14 score:2
9. ATONE attempts:8 score:0
10. RECUT attempts:15 score:8
11. SLOTH attempts:7 score:0
12. RELAX attempts:4 score:7
13. THROW attempts:17 score:1
14. CABIN attempts:16 score:7
15. BUNNY attempts:18 score:1
16. CLINK attempts:19 score:8

# [squareword.org](squareword.org) 🧩 #1691 🥳 9 ⏱️ 0:03:34.515276

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟨 🟨
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C O F F
    H A L L O
    U D D E R
    T R E A T
    S E N S E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1628 🥳 124 ⏱️ 0:22:07.292860

🤔 125 attempts
📜 3 sessions
🫧 7 chat sessions
⁉️ 17 chat prompts
🤖 14 gemma4:31b-cloud replies
😱  1 🔥  2 🥵 12 😎 34 🥶 72 🧊  3

      $1 #125 underground   100.00°C 🥳 1000‰ ~122 used:0 [121]  source:gemma4
      $2 #121 subterranean   66.70°C 😱  999‰   ~1 used:1 [0]    source:gemma4
      $3  #80 cavern         52.49°C 🔥  997‰   ~2 used:6 [1]    source:gemma4
      $4  #76 tunnel         45.37°C 🔥  995‰   ~3 used:8 [2]    source:gemma4
      $5  #72 mine           40.05°C 🥵  986‰  ~14 used:3 [13]   source:gemma4
      $6  #59 pipe           37.89°C 🥵  982‰  ~13 used:2 [12]   source:gemma4
      $7 #108 underworld     37.00°C 🥵  978‰   ~4 used:1 [3]    source:gemma4
      $8  #77 adit           36.83°C 🥵  977‰   ~5 used:0 [4]    source:gemma4
      $9 #110 catacomb       36.51°C 🥵  975‰   ~6 used:0 [5]    source:gemma4
     $10 #114 dungeon        36.15°C 🥵  970‰   ~7 used:0 [6]    source:gemma4
     $11  #97 digging        35.79°C 🥵  968‰   ~8 used:0 [7]    source:gemma4
     $17  #90 stalactite     30.56°C 😎  887‰  ~16 used:0 [15]   source:gemma4
     $51  #27 basalt         21.53°C 🥶        ~51 used:0 [50]   source:gemma4
    $123  #23 luster         -0.71°C 🧊       ~123 used:0 [122]  source:gemma4

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1661 🥳 72 ⏱️ 0:00:46.415032

🤔 73 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 10 chat prompts
🤖 10 gemma4:31b-cloud replies
🔥  2 🥵  7 😎 21 🥶 40 🧊  2

     $1 #73 chaleur         100.00°C 🥳 1000‰ ~71 used:0 [70]  source:gemma4
     $2 #67 humidité         52.78°C 🔥  995‰  ~2 used:2 [1]   source:gemma4
     $3 #53 température      51.94°C 🔥  993‰  ~1 used:1 [0]   source:gemma4
     $4 #71 humide           48.40°C 🥵  989‰  ~3 used:0 [2]   source:gemma4
     $5 #14 pluie            43.26°C 🥵  971‰  ~9 used:5 [8]   source:gemma4
     $6 #22 atmosphère       41.23°C 🥵  956‰  ~6 used:3 [5]   source:gemma4
     $7 #21 hygrométrie      40.97°C 🥵  952‰  ~7 used:3 [6]   source:gemma4
     $8 #37 évaporation      40.64°C 🥵  949‰  ~4 used:0 [3]   source:gemma4
     $9 #17 bruine           38.20°C 🥵  915‰  ~8 used:3 [7]   source:gemma4
    $10 #38 air              37.93°C 🥵  912‰  ~5 used:0 [4]   source:gemma4
    $11 #48 oxygène          35.49°C 😎  865‰ ~10 used:0 [9]   source:gemma4
    $12 #27 condensation     35.41°C 😎  860‰ ~11 used:0 [10]  source:gemma4
    $32 #72 moisissure       24.33°C 🥶       ~31 used:0 [30]  source:gemma4
    $72 #51 précipité        -0.57°C 🧊       ~72 used:0 [71]  source:gemma4
