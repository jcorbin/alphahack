# 2026-03-10

- 🔗 spaceword.org 🧩 2026-03-09 🏁 score 2173 ranked 8.6% 31/360 ⏱️ 8:14:28.385067
- 🔗 alfagok.diginaut.net 🧩 #493 🥳 22 ⏱️ 0:00:33.647539
- 🔗 alphaguess.com 🧩 #960 🥳 28 ⏱️ 0:00:27.623511
- 🔗 dontwordle.com 🧩 #1386 🥳 6 ⏱️ 0:01:22.880255
- 🔗 dictionary.com hurdle 🧩 #1529 🥳 17 ⏱️ 0:02:55.889014
- 🔗 Quordle Classic 🧩 #1506 🥳 score:22 ⏱️ 0:01:13.448343
- 🔗 Octordle Classic 🧩 #1506 🥳 score:63 ⏱️ 0:03:16.839506
- 🔗 squareword.org 🧩 #1499 🥳 7 ⏱️ 0:01:52.965776
- 🔗 cemantle.certitudes.org 🧩 #1436 🥳 311 ⏱️ 0:05:27.415970
- 🔗 cemantix.certitudes.org 🧩 #1469 😦 770 ⏱️ 6:29:08.276445

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









# [spaceword.org](spaceword.org) 🧩 2026-03-09 🏁 score 2173 ranked 8.6% 31/360 ⏱️ 8:14:28.385067

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 31/360

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ K _ S A N E L Y   
      _ C E P E _ U _ O E   
      _ _ N O V A T E _ Z   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #493 🥳 22 ⏱️ 0:00:33.647539

🤔 22 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199609 [199609] lij       q0  ? ␅
    @+199609 [199609] lij       q1  ? after
    @+299483 [299483] schro     q2  ? ␅
    @+299483 [299483] schro     q3  ? after
    @+324421 [324421] subsidie  q6  ? ␅
    @+324421 [324421] subsidie  q7  ? after
    @+324756 [324756] suffer    q18 ? ␅
    @+324756 [324756] suffer    q19 ? after
    @+324815 [324815] suiker    q20 ? ␅
    @+324815 [324815] suiker    q21 ? it
    @+324815 [324815] suiker    done. it
    @+325099 [325099] sultan    q16 ? ␅
    @+325099 [325099] sultan    q17 ? before
    @+325782 [325782] swa       q14 ? ␅
    @+325782 [325782] swa       q15 ? before
    @+327210 [327210] tachyon   q12 ? ␅
    @+327210 [327210] tachyon   q13 ? before
    @+329999 [329999] tel       q10 ? ␅
    @+329999 [329999] tel       q11 ? before
    @+335611 [335611] toe       q8  ? ␅
    @+335611 [335611] toe       q9  ? before
    @+349467 [349467] vakantie  q4  ? ␅
    @+349467 [349467] vakantie  q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #960 🥳 28 ⏱️ 0:00:27.623511

🤔 28 attempts
📜 1 sessions

    @        [     0] aa        
    @+2      [     2] aahed     
    @+98218  [ 98218] mach      q0  ? ␅
    @+98218  [ 98218] mach      q1  ? after
    @+98218  [ 98218] mach      q2  ? ␅
    @+98218  [ 98218] mach      q3  ? after
    @+122779 [122779] parr      q6  ? ␅
    @+122779 [122779] parr      q7  ? after
    @+123692 [123692] pe        q14 ? ␅
    @+123692 [123692] pe        q15 ? after
    @+124219 [124219] pelican   q18 ? ␅
    @+124219 [124219] pelican   q19 ? after
    @+124475 [124475] penny     q20 ? ␅
    @+124475 [124475] penny     q21 ? after
    @+124611 [124611] penuchles q22 ? ␅
    @+124611 [124611] penuchles q23 ? after
    @+124640 [124640] people    q26 ? ␅
    @+124640 [124640] people    q27 ? it
    @+124640 [124640] people    done. it
    @+124676 [124676] pepper    q24 ? ␅
    @+124676 [124676] pepper    q25 ? before
    @+124746 [124746] per       q16 ? ␅
    @+124746 [124746] per       q17 ? before
    @+125811 [125811] petti     q12 ? ␅
    @+125811 [125811] petti     q13 ? before
    @+128848 [128848] play      q10 ? ␅
    @+128848 [128848] play      q11 ? before
    @+135070 [135070] proper    q8  ? ␅
    @+135070 [135070] proper    q9  ? before
    @+147373 [147373] rhumb     q4  ? ␅
    @+147373 [147373] rhumb     q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1386 🥳 6 ⏱️ 0:01:22.880255

📜 1 sessions
💰 score: 42

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:PIPIT n n n n n remain:6049
    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:3092
    ⬜⬜⬜⬜⬜ tried:EMCEE n n n n n remain:840
    ⬜⬜⬜⬜⬜ tried:BOFFO n n n n n remain:161
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:45
    ⬜🟩⬜⬜⬜ tried:KUDZU n Y n n n remain:6

    Undos used: 3

      6 words remaining
    x 7 unused letters
    = 42 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1529 🥳 17 ⏱️ 0:02:55.889014

📜 1 sessions
💰 score: 9900

    4/6
    ARISE ⬜🟨⬜⬜⬜
    LURCH ⬜⬜🟨⬜🟨
    THORN ⬜🟨🟨🟨🟨
    HONOR 🟩🟩🟩🟩🟩
    3/6
    HONOR 🟨⬜⬜⬜⬜
    CHAIS ⬜🟨🟨⬜⬜
    LAUGH 🟩🟩🟩🟩🟩
    4/6
    LAUGH 🟨⬜⬜⬜⬜
    SPLIT ⬜⬜🟨⬜🟨
    MOTEL ⬜🟩🟨🟩🟩
    TOWEL 🟩🟩🟩🟩🟩
    5/6
    TOWEL ⬜🟩🟩🟩⬜
    DOWER ⬜🟩🟩🟩🟩
    POWER ⬜🟩🟩🟩🟩
    SOWER ⬜🟩🟩🟩🟩
    COWER 🟩🟩🟩🟩🟩
    Final 1/2
    SALON 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1506 🥳 score:22 ⏱️ 0:01:13.448343

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. AWARE attempts:5 score:5
2. WORDY attempts:6 score:6
3. PETTY attempts:7 score:7
4. POWER attempts:4 score:4

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1506 🥳 score:63 ⏱️ 0:03:16.839506

📜 2 sessions

Octordle Classic

1. SWUNG attempts:4 score:4
2. DROLL attempts:5 score:5
3. QUELL attempts:6 score:6
4. FREAK attempts:10 score:10
5. STOVE attempts:11 score:11
6. RAINY attempts:8 score:8
7. TAPER attempts:12 score:12
8. NIGHT attempts:7 score:7

# [squareword.org](squareword.org) 🧩 #1499 🥳 7 ⏱️ 0:01:52.965776

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A C R I D
    G L A C E
    L O G I N
    O V E N S
    W E D G E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1436 🥳 311 ⏱️ 0:05:27.415970

🤔 312 attempts
📜 1 sessions
🫧 19 chat sessions
⁉️ 106 chat prompts
🤖 106 dolphin3:latest replies
🔥   1 🥵   6 😎  53 🥶 224 🧊  27

      $1 #312 coordinator      100.00°C 🥳 1000‰ ~285 used:0  [284]  source:dolphin3
      $2 #303 liaison           51.48°C 🔥  991‰   ~1 used:9  [0]    source:dolphin3
      $3 #145 outreach          46.26°C 🥵  984‰  ~59 used:76 [58]   source:dolphin3
      $4 #183 volunteer         41.42°C 🥵  972‰  ~54 used:44 [53]   source:dolphin3
      $5 #243 coordinate        40.31°C 🥵  964‰  ~17 used:18 [16]   source:dolphin3
      $6 #242 organize          35.94°C 🥵  944‰  ~16 used:12 [15]   source:dolphin3
      $7 #148 advocacy          35.19°C 🥵  936‰  ~18 used:19 [17]   source:dolphin3
      $8 #173 organization      32.13°C 🥵  906‰  ~15 used:11 [14]   source:dolphin3
      $9 #113 marketing         31.00°C 😎  886‰  ~60 used:10 [59]   source:dolphin3
     $10 #295 activist          30.70°C 😎  882‰  ~19 used:2  [18]   source:dolphin3
     $11  #89 coordination      29.56°C 😎  862‰  ~58 used:7  [57]   source:dolphin3
     $12 #128 program           28.37°C 😎  849‰  ~50 used:3  [49]   source:dolphin3
     $62 #108 funding           15.64°C 🥶        ~68 used:0  [67]   source:dolphin3
    $286   #4 car               -0.18°C 🧊       ~286 used:0  [285]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1469 😦 770 ⏱️ 6:29:08.276445

🤔 769 attempts
📜 3 sessions
🫧 106 chat sessions
⁉️ 502 chat prompts
🤖 215 llama3.2:latest replies
🤖 164 dolphin3:latest replies
🤖 68 falcon3:10b replies
🤖 55 llama3.1:8b replies
😦 🔥   7 🥵  33 😎 141 🥶 494 🧊  94

      $1 #156 accroître           64.94°C 🔥  998‰ ~174 used:399 [173]  source:dolphin3
      $2 #122 accroissement       60.60°C 🔥  997‰ ~171 used:248 [170]  source:dolphin3
      $3 #144 multiplication      53.31°C 🔥  996‰  ~38 used:74  [37]   source:dolphin3
      $4 #263 accentuer           52.93°C 🔥  995‰   ~2 used:68  [1]    source:llama3.1
      $5 #169 croître             52.05°C 🔥  994‰   ~3 used:68  [2]    source:dolphin3
      $6 #131 intensification     47.11°C 🔥  991‰   ~1 used:67  [0]    source:dolphin3
      $7 #126 augmentation        45.96°C 🔥  990‰   ~4 used:68  [3]    source:dolphin3
      $8 #181 diminution          44.71°C 🥵  986‰   ~5 used:7   [4]    source:dolphin3
      $9 #150 multiplier          44.65°C 🥵  985‰   ~6 used:7   [5]    source:dolphin3
     $10 #240 décroître           44.64°C 🥵  984‰   ~7 used:7   [6]    source:llama3.1
     $11 #440 prépondérance       43.10°C 🥵  979‰   ~8 used:7   [7]    source:llama3.2
     $41 #193 conséquence         36.01°C 😎  896‰  ~39 used:0   [38]   source:llama3.1
    $182 #612 risque              23.60°C 🥶       ~169 used:0   [168]  source:llama3.2
    $676 #250 préjudicier         -0.01°C 🧊       ~676 used:0   [675]  source:llama3.1
