# 2026-06-26

- 🔗 spaceword.org 🧩 2026-06-25 🏁 score 2172 ranked 25.1% 80/319 ⏱️ 0:19:54.272039
- 🔗 alfagok.diginaut.net 🧩 #601 🥳 42 ⏱️ 0:00:57.508244
- 🔗 alphaguess.com 🧩 #1068 🥳 20 ⏱️ 0:00:36.590913
- 🔗 dontwordle.com 🧩 #1494 🥳 6 ⏱️ 0:01:35.883175
- 🔗 dictionary.com hurdle 🧩 #1637 🥳 17 ⏱️ 0:02:57.707541
- 🔗 Quordle Classic 🧩 #1614 🥳 score:26 ⏱️ 0:01:56.794974
- 🔗 Octordle Classic 🧩 #1614 🥳 score:60 ⏱️ 0:03:37.920920
- 🔗 Sedecordle Classic 🧩 #1594 🥳 score:36 ⏱️ 0:12:08.827368
- 🔗 squareword.org 🧩 #1607 🥳 6 ⏱️ 0:01:36.257477
- 🔗 cemantle.certitudes.org 🧩 #1544 🥳 124 ⏱️ 0:01:21.848665
- 🔗 cemantix.certitudes.org 🧩 #1577 🥳 280 ⏱️ 0:05:43.493934

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

















# [spaceword.org](spaceword.org) 🧩 2026-06-25 🏁 score 2172 ranked 25.1% 80/319 ⏱️ 0:19:54.272039

📜 3 sessions
- tiles: 21/21
- score: 2172 bonus: +72
- rank: 80/319

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ P O O R _ _ W _   
      _ _ U _ _ _ _ G I _   
      _ _ T A X E M E S _   
      _ _ Z _ U N I T E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #601 🥳 42 ⏱️ 0:00:57.508244

🤔 42 attempts
📜 1 sessions

    @        [     0] &-teken             
    @+199558 [199558] lij                 q0  ? ␅
    @+199558 [199558] lij                 q1  ? after
    @+199558 [199558] lij                 q2  ? ␅
    @+199558 [199558] lij                 q3  ? after
    @+199558 [199558] lij                 q4  ? ␅
    @+199558 [199558] lij                 q5  ? after
    @+247623 [247623] op                  q8  ? ␅
    @+247623 [247623] op                  q9  ? after
    @+249217 [249217] opgespeld           q18 ? ␅
    @+249217 [249217] opgespeld           q19 ? after
    @+249941 [249941] opleiding           q20 ? ␅
    @+249941 [249941] opleiding           q21 ? after
    @+250150 [250150] oplossing           q24 ? ␅
    @+250150 [250150] oplossing           q25 ? after
    @+250237 [250237] opmerk              q26 ? ␅
    @+250237 [250237] opmerk              q27 ? after
    @+250281 [250281] opname              q28 ? ␅
    @+250281 [250281] opname              q29 ? after
    @+250327 [250327] opnames             q30 ? ␅
    @+250327 [250327] opnames             q31 ? after
    @+250347 [250347] opnemen             q32 ? ␅
    @+250347 [250347] opnemen             q33 ? after
    @+250352 [250352] opneming            q36 ? ␅
    @+250352 [250352] opneming            q37 ? after
    @+250355 [250355] opnemingsvaartuigen q38 ? ␅
    @+250355 [250355] opnemingsvaartuigen q39 ? after
    @+250357 [250357] opnieuw             q40 ? ␅
    @+250357 [250357] opnieuw             q41 ? it
    @+250357 [250357] opnieuw             done. it
    @+250358 [250358] opnoem              q35 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1068 🥳 20 ⏱️ 0:00:36.590913

🤔 20 attempts
📜 1 sessions

    @        [     0] aa      
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98214  [ 98214] mach    q0  ? ␅
    @+98214  [ 98214] mach    q1  ? after
    @+147364 [147364] rhotic  q2  ? ␅
    @+147364 [147364] rhotic  q3  ? after
    @+171634 [171634] ta      q4  ? ␅
    @+171634 [171634] ta      q5  ? after
    @+181998 [181998] un      q6  ? ␅
    @+181998 [181998] un      q7  ? after
    @+189260 [189260] vicar   q8  ? ␅
    @+189260 [189260] vicar   q9  ? after
    @+192864 [192864] whir    q10 ? ␅
    @+192864 [192864] whir    q11 ? after
    @+193479 [193479] win     q14 ? ␅
    @+193479 [193479] win     q15 ? after
    @+193734 [193734] winter  q18 ? ␅
    @+193734 [193734] winter  q19 ? it
    @+193734 [193734] winter  done. it
    @+194059 [194059] wo      q16 ? ␅
    @+194059 [194059] wo      q17 ? before
    @+194688 [194688] worship q12 ? ␅
    @+194688 [194688] worship q13 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1494 🥳 6 ⏱️ 0:01:35.883175

📜 1 sessions
💰 score: 18

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:YUPPY n n n n n remain:7572
    ⬜⬜⬜⬜⬜ tried:GABBA n n n n n remain:3106
    ⬜⬜⬜⬜⬜ tried:MINIM n n n n n remain:1111
    ⬜⬜⬜⬜⬜ tried:OVOLO n n n n n remain:286
    ⬜🟨⬜🟨⬜ tried:CEDED n m n m n remain:11
    ⬜⬜🟩⬜🟩 tried:FRERE n n Y n Y remain:2

    Undos used: 3

      2 words remaining
    x 9 unused letters
    = 18 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1637 🥳 17 ⏱️ 0:02:57.707541

📜 1 sessions
💰 score: 9900

    3/6
    RAPES 🟨⬜🟨⬜⬜
    CRIMP ⬜🟩🟩🟩🟨
    PRIMO 🟩🟩🟩🟩🟩
    4/6
    PRIMO ⬜⬜⬜⬜⬜
    ELANS ⬜⬜🟨🟨⬜
    CANTY ⬜🟨🟨⬜⬜
    UNBAN 🟩🟩🟩🟩🟩
    5/6
    UNBAN ⬜⬜⬜🟩⬜
    SCRAP ⬜⬜🟨🟩⬜
    TRIAL ⬜🟨⬜🟩⬜
    REWAX 🟩⬜⬜🟩⬜
    RADAR 🟩🟩🟩🟩🟩
    3/6
    RADAR ⬜⬜⬜🟩⬜
    PENAL ⬜⬜⬜🟩🟩
    OCTAL 🟩🟩🟩🟩🟩
    Final 2/2
    FIVES 🟩🟩⬜⬜⬜
    FIZZY 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1614 🥳 score:26 ⏱️ 0:01:56.794974

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. JUICE attempts:4 score:4
2. ARRAY attempts:6 score:6
3. BONEY attempts:7 score:7
4. SKIFF attempts:9 score:9

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1614 🥳 score:60 ⏱️ 0:03:37.920920

📜 1 sessions

Octordle Classic

1. ANGST attempts:4 score:4
2. AWAIT attempts:5 score:5
3. ISSUE attempts:10 score:10
4. CRIME attempts:7 score:7
5. TRAMP attempts:6 score:6
6. GAVEL attempts:11 score:11
7. TEMPO attempts:8 score:8
8. SKIFF attempts:9 score:9

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1594 🥳 score:36 ⏱️ 0:12:08.827368

📜 5 sessions

Sedecordle Classic sedecordle.com

1. WELCH attempts:13 score:1
2. MUCUS attempts:16 score:3
3. BLURT attempts:4 score:0
4. BREAK attempts:8 score:4
5. ROYAL attempts:10 score:1
6. BELCH attempts:11 score:0
7. WIDEN attempts:14 score:1
8. BROOM attempts:15 score:4
9. SALLY attempts:11 score:1
10. SKIFF attempts:17 score:8
11. INANE attempts:3 score:0
12. SHANK attempts:13 score:3
13. STANK attempts:7 score:0
14. BLOKE attempts:6 score:7
15. SHOCK attempts:12 score:1
16. AZURE attempts:5 score:2

# [squareword.org](squareword.org) 🧩 #1607 🥳 6 ⏱️ 0:01:36.257477

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P I L A F
    A R O M A
    P A G E R
    A T O N E
    L E N D S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1544 🥳 124 ⏱️ 0:01:21.848665

🤔 125 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 15 chat prompts
🤖 15 dolphin3:latest replies
🥵  8 😎 13 🥶 89 🧊 14

      $1 #125 demonstration  100.00°C 🥳 1000‰ ~111 used:0 [110]  source:dolphin3
      $2 #116 workshop        37.38°C 🥵  989‰   ~7 used:2 [6]    source:dolphin3
      $3  #78 event           36.30°C 🥵  985‰   ~8 used:2 [7]    source:dolphin3
      $4  #99 display         35.39°C 🥵  984‰   ~1 used:1 [0]    source:dolphin3
      $5  #82 gathering       32.90°C 🥵  976‰   ~2 used:1 [1]    source:dolphin3
      $6  #92 celebration     31.06°C 🥵  966‰   ~3 used:0 [2]    source:dolphin3
      $7 #108 parade          28.58°C 🥵  951‰   ~4 used:0 [3]    source:dolphin3
      $8 #100 exhibition      28.31°C 🥵  947‰   ~5 used:0 [4]    source:dolphin3
      $9 #112 show            27.62°C 🥵  938‰   ~6 used:0 [5]    source:dolphin3
     $10 #120 meeting         25.33°C 😎  896‰   ~9 used:0 [8]    source:dolphin3
     $11  #95 concert         24.15°C 😎  866‰  ~10 used:0 [9]    source:dolphin3
     $12 #109 recital         23.10°C 😎  828‰  ~11 used:0 [10]   source:dolphin3
     $23  #16 branch          16.40°C 🥶        ~22 used:9 [21]   source:dolphin3
    $112  #24 flitter         -0.05°C 🧊       ~112 used:0 [111]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1577 🥳 280 ⏱️ 0:05:43.493934

🤔 281 attempts
📜 1 sessions
🫧 15 chat sessions
⁉️ 72 chat prompts
🤖 72 dolphin3:latest replies
🔥   1 🥵  13 😎  68 🥶 120 🧊  78

      $1 #281 sport          100.00°C 🥳 1000‰ ~203 used:0  [202]  source:dolphin3
      $2 #183 athlétisme      48.13°C 🔥  993‰   ~4 used:42 [3]    source:dolphin3
      $3 #148 natation        46.22°C 🥵  987‰  ~78 used:28 [77]   source:dolphin3
      $4  #27 cyclisme        45.05°C 🥵  981‰  ~79 used:37 [78]   source:dolphin3
      $5 #216 tennis          43.03°C 🥵  974‰   ~5 used:5  [4]    source:dolphin3
      $6 #236 volley          42.22°C 🥵  971‰   ~6 used:5  [5]    source:dolphin3
      $7 #268 paralympique    41.63°C 🥵  970‰   ~1 used:2  [0]    source:dolphin3
      $8  #44 compétition     40.90°C 🥵  967‰  ~75 used:19 [74]   source:dolphin3
      $9 #206 basket          40.10°C 🥵  960‰   ~2 used:4  [1]    source:dolphin3
     $10 #102 athlète         39.44°C 🥵  955‰   ~9 used:7  [8]    source:dolphin3
     $11 #136 triathlon       38.21°C 🥵  945‰  ~10 used:7  [9]    source:dolphin3
     $16 #190 licencié        32.84°C 😎  899‰  ~11 used:0  [10]   source:dolphin3
     $84 #168 nage            14.56°C 🥶        ~83 used:0  [82]   source:dolphin3
    $204 #164 canot           -0.05°C 🧊       ~204 used:0  [203]  source:dolphin3
