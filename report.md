# 2026-10-05

- 🔗 spaceword.org 🧩 2026-10-04 🏁 score 2165 ranked 46.7% 135/289 ⏱️ 0:30:40.497239
- 🔗 wordgrid 🧩 #856 🟪 rarity:0.32 ⏱️ 0:03:38.371695
- 🔗 alfagok.diginaut.net 🧩 #702 🥳 30 ⏱️ 0:00:35.051380
- 🔗 alphaguess.com 🧩 #1169 🥳 36 ⏱️ 0:00:39.626286
- 🔗 dontwordle.com 🧩 #1595 🥳 6 ⏱️ 0:01:27.232926
- 🔗 dictionary.com hurdle 🧩 #1738 🥳 19 ⏱️ 0:02:44.437166
- 🔗 Quordle Classic 🧩 #1715 🥳 score:25 ⏱️ 0:02:09.636330
- 🔗 Octordle Classic 🧩 #1715 🥳 score:63 ⏱️ 0:01:45.072614
- 🔗 Sedecordle Classic 🧩 #1695 🥳 score:43 ⏱️ 0:04:15.281603
- 🔗 squareword.org 🧩 #1708 🥳 8 ⏱️ 0:02:34.606638
- 🔗 cemantle.certitudes.org 🧩 #1645 🥳 86 ⏱️ 0:01:50.655520
- 🔗 cemantix.certitudes.org 🧩 #1678 🥳 336 ⏱️ 0:31:37.184806

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

# [spaceword.org](spaceword.org) 🧩 2026-10-04 🏁 score 2165 ranked 46.7% 135/289 ⏱️ 0:30:40.497239

📜 2 sessions
- tiles: 21/21
- score: 2165 bonus: +65
- rank: 135/289

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ G _ O _ _   
      _ _ _ K O U M I S _   
      _ _ C A R I O L E _   
      _ _ _ _ _ L _ _ V _   
      _ _ W I T E _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #856 🟪 rarity:0.32 ⏱️ 0:03:38.371695

📜 2 sessions
🌌 🦄 🌌
🌌 🦄 🌌
🌌 🌌 🌌
Rarity: 0.32 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #702 🥳 30 ⏱️ 0:00:35.051380

🤔 30 attempts
📜 1 sessions

    @        [     0] &-teken           
    @+2      [     2] -cijferig         
    @+199528 [199528] lij               q0  ? ␅
    @+199528 [199528] lij               q1  ? after
    @+223512 [223512] molen             q6  ? ␅
    @+223512 [223512] molen             q7  ? after
    @+229513 [229513] natuurbescherming q10 ? ␅
    @+229513 [229513] natuurbescherming q11 ? after
    @+232499 [232499] niets             q12 ? ␅
    @+232499 [232499] niets             q13 ? after
    @+233939 [233939] noord             q14 ? ␅
    @+233939 [233939] noord             q15 ? after
    @+234723 [234723] nuance            q16 ? ␅
    @+234723 [234723] nuance            q17 ? after
    @+234794 [234794] nul               q22 ? ␅
    @+234794 [234794] nul               q23 ? after
    @+234849 [234849] numero            q26 ? ␅
    @+234849 [234849] numero            q27 ? after
    @+234863 [234863] nummer            q28 ? ␅
    @+234863 [234863] nummer            q29 ? it
    @+234863 [234863] nummer            done. it
    @+234903 [234903] nun               q20 ? ␅
    @+234903 [234903] nun               q21 ? before
    @+235092 [235092] object            q18 ? ␅
    @+235092 [235092] object            q19 ? before
    @+235519 [235519] octrooi           q8  ? ␅
    @+235519 [235519] octrooi           q9  ? before
    @+247575 [247575] op                q4  ? ␅
    @+247575 [247575] op                q5  ? before
    @+299479 [299479] schrok            q2  ? ␅
    @+299479 [299479] schrok            q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1169 🥳 36 ⏱️ 0:00:39.626286

🤔 36 attempts
📜 1 sessions

    @       [    0] aa           
    @+23680 [23680] camp         q4  ? ␅
    @+23680 [23680] camp         q5  ? after
    @+35522 [35522] convention   q6  ? ␅
    @+35522 [35522] convention   q7  ? after
    @+40838 [40838] da           q8  ? ␅
    @+40838 [40838] da           q9  ? after
    @+44066 [44066] den          q10 ? ␅
    @+44066 [44066] den          q11 ? after
    @+45658 [45658] dev          q12 ? ␅
    @+45658 [45658] dev          q13 ? after
    @+46067 [46067] diagram      q16 ? ␅
    @+46067 [46067] diagram      q17 ? after
    @+46167 [46167] diamin       q20 ? ␅
    @+46167 [46167] diamin       q21 ? after
    @+46219 [46219] diapir       q22 ? ␅
    @+46219 [46219] diapir       q23 ? after
    @+46233 [46233] diarist      q26 ? ␅
    @+46233 [46233] diarist      q27 ? after
    @+46240 [46240] diarrhetic   q28 ? ␅
    @+46240 [46240] diarrhetic   q29 ? after
    @+46244 [46244] diarthrosis  q30 ? ␅
    @+46244 [46244] diarthrosis  q31 ? after
    @+46245 [46245] diary        q34 ? ␅
    @+46245 [46245] diary        q35 ? it
    @+46245 [46245] diary        done. it
    @+46246 [46246] diaspora     q32 ? ␅
    @+46246 [46246] diaspora     q33 ? before
    @+46247 [46247] diasporas    q24 ? ␅
    @+46247 [46247] diasporas    q25 ? before
    @+46274 [46274] diastrophism q19 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1595 🥳 6 ⏱️ 0:01:27.232926

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:8089
    ⬜⬜⬜⬜⬜ tried:JAVAS n n n n n remain:1929
    ⬜⬜⬜⬜⬜ tried:HOOCH n n n n n remain:683
    ⬜⬜⬜⬜⬜ tried:KININ n n n n n remain:186
    ⬜⬜🟨⬜⬜ tried:FRUMP n n m n n remain:15
    ⬜⬜🟨🟩⬜ tried:QUEUE n n m Y n remain:4

    Undos used: 4

      4 words remaining
    x 6 unused letters
    = 24 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1738 🥳 19 ⏱️ 0:02:44.437166

📜 1 sessions
💰 score: 9700

    4/6
    ORLES ⬜⬜⬜🟨⬜
    IDENT 🟨⬜🟨⬜⬜
    AMICE ⬜🟨🟩🟨🟩
    CHIME 🟩🟩🟩🟩🟩
    4/6
    CHIME ⬜🟨⬜⬜⬜
    SOUTH ⬜⬜⬜⬜🟩
    GLYPH ⬜⬜⬜⬜🟩
    RAJAH 🟩🟩🟩🟩🟩
    5/6
    RAJAH ⬜🟨⬜⬜⬜
    AISLE 🟨⬜⬜🟨🟩
    PLAGE 🟩🟩🟩⬜🟩
    ACTIN 🟨🟨⬜⬜⬜
    PLACE 🟩🟩🟩🟩🟩
    4/6
    PLACE ⬜⬜🟨🟩⬜
    RANCH ⬜🟩⬜🟩🟩
    WOMBS ⬜⬜⬜🟨⬜
    BATCH 🟩🟩🟩🟩🟩
    Final 2/2
    FUDGE ⬜⬜🟩⬜🟩
    LADLE 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1715 🥳 score:25 ⏱️ 0:02:09.636330

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. SIXTH attempts:7 score:7
2. SPEAK attempts:4 score:4
3. SEDAN attempts:6 score:6
4. HEIST attempts:8 score:8

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1715 🥳 score:63 ⏱️ 0:01:45.072614

📜 1 sessions

Octordle Classic

1. DOWDY attempts:10 score:10
2. GROWN attempts:9 score:9
3. SUSHI attempts:5 score:5
4. COUGH attempts:11 score:11
5. PINCH attempts:12 score:12
6. MODEL attempts:6 score:6
7. CREED attempts:7 score:7
8. LUSTY attempts:3 score:3

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1695 🥳 score:43 ⏱️ 0:04:15.281603

📜 5 sessions

Sedecordle Classic sedecordle.com

1. SMIRK attempts:12 score:1
2. GROOM attempts:14 score:2
3. SAPPY attempts:17 score:1
4. BLAST attempts:5 score:7
5. GRUFF attempts:13 score:1
6. WORLD attempts:6 score:3
7. RETCH attempts:3 score:0
8. INLAY attempts:10 score:3
9. QUICK attempts:11 score:1
10. STOIC attempts:4 score:1
11. HAUNT attempts:7 score:0
12. CROSS attempts:8 score:7
13. RAYON attempts:9 score:0
14. ULTRA attempts:15 score:9
15. PARKA attempts:16 score:1
16. TOXIN attempts:18 score:6

# [squareword.org](squareword.org) 🧩 #1708 🥳 8 ⏱️ 0:02:34.606638

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟨 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P E R P S
    E X A L T
    A T R I A
    C R E E P
    H A R S H

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1645 🥳 86 ⏱️ 0:01:50.655520

🤔 87 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 17 chat prompts
🤖 17 dolphin3:latest replies
😱  1 🔥  1 🥵  6 😎 16 🥶 61 🧊  1

     $1 #87 template        100.00°C 🥳 1000‰ ~86 used:0 [85]  source:dolphin3
     $2 #74 blueprint        56.01°C 😱  999‰  ~1 used:3 [0]   source:dolphin3
     $3 #85 model            44.84°C 🔥  996‰  ~2 used:0 [1]   source:dolphin3
     $4 #86 outline          39.31°C 🥵  984‰  ~3 used:0 [2]   source:dolphin3
     $5 #33 illustration     35.75°C 🥵  957‰  ~7 used:8 [6]   source:dolphin3
     $6 #41 concept          34.31°C 🥵  930‰  ~8 used:9 [7]   source:dolphin3
     $7 #39 sketch           33.89°C 🥵  918‰  ~6 used:6 [5]   source:dolphin3
     $8 #84 map              33.89°C 🥵  917‰  ~4 used:0 [3]   source:dolphin3
     $9 #83 diagram          33.69°C 🥵  910‰  ~5 used:0 [4]   source:dolphin3
    $10 #64 inspiration      33.11°C 😎  892‰  ~9 used:0 [8]   source:dolphin3
    $11 #66 original         30.91°C 😎  822‰ ~10 used:0 [9]   source:dolphin3
    $12 #56 thumbnail        30.90°C 😎  821‰ ~11 used:0 [10]  source:dolphin3
    $26  #6 pencil           22.72°C 🥶       ~25 used:7 [24]  source:dolphin3
    $87 #32 taking          -12.62°C 🧊       ~87 used:0 [86]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1678 🥳 336 ⏱️ 0:31:37.184806

🤔 337 attempts
📜 1 sessions
🫧 31 chat sessions
⁉️ 160 chat prompts
🤖 160 dolphin3:latest replies
😱   1 🔥   3 🥵   6 😎  37 🥶 221 🧊  68

      $1 #337 noble              100.00°C 🥳 1000‰ ~269 used:0  [268]  source:dolphin3
      $2 #306 noblesse            65.64°C 😱  999‰   ~2 used:18 [1]    source:dolphin3
      $3 #331 aristocrate         56.07°C 🔥  997‰   ~3 used:3  [2]    source:dolphin3
      $4 #307 aristocratie        54.81°C 🔥  996‰   ~4 used:9  [3]    source:dolphin3
      $5 #332 aristocratique      54.18°C 🔥  994‰   ~1 used:0  [0]    source:dolphin3
      $6 #277 gloire              44.08°C 🥵  965‰  ~27 used:16 [26]   source:dolphin3
      $7 #320 lignage             42.98°C 🥵  958‰   ~5 used:0  [4]    source:dolphin3
      $8 #301 magnanimité         42.71°C 🥵  949‰   ~6 used:2  [5]    source:dolphin3
      $9 #247 glorieux            42.23°C 🥵  945‰  ~40 used:30 [39]   source:dolphin3
     $10 #249 fastueux            41.37°C 🥵  931‰  ~39 used:23 [38]   source:dolphin3
     $11 #237 illustre            41.14°C 🥵  928‰  ~28 used:19 [27]   source:dolphin3
     $12 #333 chevalerie          39.99°C 😎  898‰   ~7 used:0  [6]    source:dolphin3
     $49 #205 intellectuel        29.00°C 🥶        ~58 used:0  [57]   source:dolphin3
    $270 #109 filer               -0.21°C 🧊       ~270 used:0  [269]  source:dolphin3
