# 2026-06-02

- 🔗 spaceword.org 🧩 2026-06-01 🏁 score 2170 ranked 30.7% 107/348 ⏱️ 21:28:03.040786
- 🔗 alfagok.diginaut.net 🧩 #577 🥳 82 ⏱️ 0:02:22.170945
- 🔗 alphaguess.com 🧩 #1044 🥳 32 ⏱️ 0:00:33.071130
- 🔗 dontwordle.com 🧩 #1470 🥳 6 ⏱️ 0:01:23.983499
- 🔗 dictionary.com hurdle 🧩 #1613 🥳 21 ⏱️ 0:03:54.769972
- 🔗 Quordle Classic 🧩 #1590 🥳 score:26 ⏱️ 0:02:28.209118
- 🔗 Octordle Classic 🧩 #1590 🥳 score:59 ⏱️ 0:03:23.649836
- 🔗 squareword.org 🧩 #1583 🥳 8 ⏱️ 0:02:19.934559
- 🔗 cemantle.certitudes.org 🧩 #1520 🥳 314 ⏱️ 0:05:05.468359
- 🔗 cemantix.certitudes.org 🧩 #1553 🥳 549 ⏱️ 0:13:42.997405

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
























































































# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1585 😦 score:32 ⏱️ 0:02:33.513959

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. GRAPE attempts:8 score:8
2. VALUE attempts:9 score:9
3. YEARN attempts:6 score:6
4. IN_ER -ACDGHLMPSTUVWYZ attempts:9 score:-1






# [spaceword.org](spaceword.org) 🧩 2026-06-01 🏁 score 2170 ranked 30.7% 107/348 ⏱️ 21:28:03.040786

📜 4 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 107/348

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ L A G _ J _ _   
      _ _ _ O U R I E _ _   
      _ _ _ _ G O _ E _ _   
      _ _ _ K I P S _ _ _   
      _ _ _ _ T E _ _ _ _   
      _ _ _ X E D _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #577 🥳 82 ⏱️ 0:02:22.170945

🤔 82 attempts
📜 1 sessions

    @       [    0] &-teken      
    @+8648  [ 8648] af           q10 ? ␅
    @+8648  [ 8648] af           q11 ? after
    @+16154 [16154] am           q12 ? ␅
    @+16154 [16154] am           q13 ? after
    @+17108 [17108] analyse      q18 ? ␅
    @+17108 [17108] analyse      q19 ? after
    @+17235 [17235] anciënniteit q56 ? ␅
    @+17235 [17235] anciënniteit q57 ? after
    @+17257 [17257] ander        q60 ? ␅
    @+17257 [17257] ander        q61 ? after
    @+17261 [17261] andere       q80 ? ␅
    @+17261 [17261] andere       q81 ? it
    @+17261 [17261] andere       done. it
    @+17269 [17269] andermaal    q78 ? ␅
    @+17269 [17269] andermaal    q79 ? before
    @+17272 [17272] anders       q58 ? ␅
    @+17272 [17272] anders       q59 ? before
    @+17353 [17353] andrieskruis q52 ? ␅
    @+17353 [17353] andrieskruis q53 ? before
    @+17592 [17592] ani          q20 ? ␅
    @+17592 [17592] ani          q21 ? before
    @+18109 [18109] anti         q16 ? ␅
    @+18109 [18109] anti         q17 ? before
    @+20506 [20506] arg          q14 ? ␅
    @+20506 [20506] arg          q15 ? before
    @+24887 [24887] bad          q8  ? ␅
    @+24887 [24887] bad          q9  ? before
    @+49817 [49817] boks         q6  ? ␅
    @+49817 [49817] boks         q7  ? before
    @+99704 [99704] ex           q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1044 🥳 32 ⏱️ 0:00:33.071130

🤔 32 attempts
📜 1 sessions

    @        [     0] aa       
    @+98216  [ 98216] mach     q0  ? ␅
    @+98216  [ 98216] mach     q1  ? after
    @+98216  [ 98216] mach     q2  ? ␅
    @+98216  [ 98216] mach     q3  ? after
    @+147366 [147366] rhotic   q4  ? ␅
    @+147366 [147366] rhotic   q5  ? after
    @+153315 [153315] sea      q10 ? ␅
    @+153315 [153315] sea      q11 ? after
    @+154830 [154830] sequence q14 ? ␅
    @+154830 [154830] sequence q15 ? after
    @+155429 [155429] sha      q16 ? ␅
    @+155429 [155429] sha      q17 ? after
    @+155526 [155526] shag     q22 ? ␅
    @+155526 [155526] shag     q23 ? after
    @+155587 [155587] shako    q24 ? ␅
    @+155587 [155587] shako    q25 ? after
    @+155600 [155600] shall    q28 ? ␅
    @+155600 [155600] shall    q29 ? after
    @+155607 [155607] shallow  q30 ? ␅
    @+155607 [155607] shallow  q31 ? it
    @+155607 [155607] shallow  done. it
    @+155618 [155618] shalt    q26 ? ␅
    @+155618 [155618] shalt    q27 ? before
    @+155649 [155649] shame    q20 ? ␅
    @+155649 [155649] shame    q21 ? before
    @+155881 [155881] shaw     q18 ? ␅
    @+155881 [155881] shaw     q19 ? before
    @+156351 [156351] ship     q12 ? ␅
    @+156351 [156351] ship     q13 ? before
    @+159483 [159483] slop     q9  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1470 🥳 6 ⏱️ 0:01:23.983499

📜 1 sessions
💰 score: 48

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:AYAYA n n n n n remain:6270
    ⬜⬜⬜⬜⬜ tried:KEEVE n n n n n remain:2372
    ⬜⬜⬜⬜⬜ tried:OXBOW n n n n n remain:822
    ⬜⬜⬜⬜⬜ tried:FLUFF n n n n n remain:222
    ⬜⬜🟩⬜⬜ tried:DJINN n n Y n n remain:57
    ⬜🟩🟩⬜⬜ tried:CHIMP n Y Y n n remain:8

    Undos used: 4

      8 words remaining
    x 6 unused letters
    = 48 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1613 🥳 21 ⏱️ 0:03:54.769972

📜 1 sessions
💰 score: 9500

    3/6
    SENOR ⬜🟨⬜⬜⬜
    IDEAL ⬜⬜🟨🟨⬜
    ACUTE 🟩🟩🟩🟩🟩
    5/6
    ACUTE ⬜🟨⬜⬜⬜
    COILS 🟩⬜🟩🟩⬜
    CHILD 🟩🟩🟩🟩⬜
    CHILL 🟩🟩🟩🟩⬜
    CHILI 🟩🟩🟩🟩🟩
    5/6
    CHILI ⬜⬜⬜⬜⬜
    MASER ⬜🟨⬜⬜🟨
    GRAFT ⬜🟩🟨⬜⬜
    BROAD ⬜🟩🟨🟨⬜
    ARROW 🟩🟩🟩🟩🟩
    6/6
    ARROW 🟨🟨⬜⬜⬜
    SHARE ⬜⬜🟨🟨🟨
    TAPER ⬜🟩⬜🟩🟩
    GAMER ⬜🟩⬜🟩🟩
    LAYER 🟨🟩⬜🟩🟩
    BALER 🟩🟩🟩🟩🟩
    Final 2/2
    BEADS 🟩🟩🟨⬜⬜
    BEGAN 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1590 🥳 score:26 ⏱️ 0:02:28.209118

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. GRAIL attempts:9 score:9
2. STRUT attempts:5 score:5
3. SHALE attempts:8 score:8
4. SORRY attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1590 🥳 score:59 ⏱️ 0:03:23.649836

📜 1 sessions

Octordle Classic

1. DOING attempts:8 score:8
2. DRUNK attempts:5 score:5
3. RADAR attempts:6 score:6
4. FROND attempts:7 score:7
5. CYNIC attempts:3 score:3
6. POSIT attempts:9 score:9
7. HOTLY attempts:11 score:11
8. BREAD attempts:10 score:10

# [squareword.org](squareword.org) 🧩 #1583 🥳 8 ⏱️ 0:02:19.934559

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟨 🟨 🟨 🟩 🟩
    🟩 🟨 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P E L T
    P O L A R
    A S I D E
    T I T L E
    S T E E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1520 🥳 314 ⏱️ 0:05:05.468359

🤔 315 attempts
📜 1 sessions
🫧 13 chat sessions
⁉️ 65 chat prompts
🤖 65 dolphin3:latest replies
😱   1 🔥   1 🥵   9 😎  25 🥶 261 🧊  17

      $1 #315 ratio          100.00°C 🥳 1000‰ ~298 used:0  [297]  source:dolphin3
      $2 #307 average         48.53°C 😱  999‰   ~1 used:0  [0]    source:dolphin3
      $3 #273 rate            45.74°C 🔥  997‰   ~5 used:12 [4]    source:dolphin3
      $4 #312 metric          37.15°C 🥵  987‰   ~2 used:0  [1]    source:dolphin3
      $5 #200 low             36.53°C 🥵  985‰  ~35 used:15 [34]   source:dolphin3
      $6 #306 index           33.73°C 🥵  971‰   ~7 used:3  [6]    source:dolphin3
      $7 #211 minimum         33.18°C 🥵  968‰  ~10 used:8  [9]    source:dolphin3
      $8 #264 denominator     32.90°C 🥵  965‰   ~8 used:3  [7]    source:dolphin3
      $9 #262 lowest          32.50°C 🥵  959‰   ~6 used:2  [5]    source:dolphin3
     $10 #219 level           30.90°C 🥵  936‰   ~9 used:6  [8]    source:dolphin3
     $11 #309 divisor         29.59°C 🥵  910‰   ~3 used:0  [2]    source:dolphin3
     $13 #311 indicator       28.84°C 😎  884‰  ~11 used:0  [10]   source:dolphin3
     $38 #245 position        21.31°C 🥶        ~48 used:0  [47]   source:dolphin3
    $299 #216 entry           -0.14°C 🧊       ~299 used:0  [298]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1553 🥳 549 ⏱️ 0:13:42.997405

🤔 550 attempts
📜 1 sessions
🫧 38 chat sessions
⁉️ 194 chat prompts
🤖 194 dolphin3:latest replies
🔥   2 🥵  11 😎  56 🥶 387 🧊  93

      $1 #550 esclave          100.00°C 🥳 1000‰ ~457 used:0  [456]  source:dolphin3
      $2 #433 serf              49.59°C 🔥  993‰   ~3 used:68 [2]    source:dolphin3
      $3 #517 servage           48.95°C 🔥  991‰   ~2 used:19 [1]    source:dolphin3
      $4 #279 peuple            39.54°C 🥵  967‰  ~64 used:79 [63]   source:dolphin3
      $5 #363 noble             38.92°C 🥵  962‰  ~44 used:27 [43]   source:dolphin3
      $6 #495 patricien         38.08°C 🥵  953‰   ~4 used:7  [3]    source:dolphin3
      $7 #258 descendant        37.34°C 🥵  948‰  ~58 used:46 [57]   source:dolphin3
      $8 #361 souverain         36.24°C 🥵  933‰  ~38 used:11 [37]   source:dolphin3
      $9 #169 indigène          36.11°C 🥵  931‰  ~63 used:67 [62]   source:dolphin3
     $10 #177 indigénat         35.76°C 🥵  924‰  ~59 used:48 [58]   source:dolphin3
     $11 #479 paria             35.38°C 🥵  920‰   ~5 used:7  [4]    source:dolphin3
     $15 #357 roi               33.94°C 😎  896‰  ~39 used:2  [38]   source:dolphin3
     $71  #67 pâtre             23.98°C 🥶        ~75 used:0  [74]   source:dolphin3
    $458  #38 grenouille        -0.13°C 🧊       ~458 used:0  [457]  source:dolphin3
