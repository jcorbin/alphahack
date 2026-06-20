# 2026-06-21

- 🔗 spaceword.org 🧩 2026-06-20 🏁 score 2173 ranked 11.0% 33/301 ⏱️ 2:31:12.423173
- 🔗 alfagok.diginaut.net 🧩 #596 🥳 38 ⏱️ 0:01:00.721316
- 🔗 alphaguess.com 🧩 #1063 🥳 30 ⏱️ 0:00:45.232132
- 🔗 dictionary.com hurdle 🧩 #1632 🥳 19 ⏱️ 0:04:54.800572
- 🔗 Quordle Classic 🧩 #1609 🥳 score:26 ⏱️ 0:01:29.678974
- 🔗 dontwordle.com 🧩 #1489 🥳 6 ⏱️ 0:02:24.168112
- 🔗 squareword.org 🧩 #1602 🥳 8 ⏱️ 0:03:24.338494
- 🔗 cemantle.certitudes.org 🧩 #1539 🥳 253 ⏱️ 0:12:54.651059
- 🔗 Octordle Classic 🧩 #1609 🥳 score:58 ⏱️ 0:03:48.658156
- 🔗 Sedecordle Classic 🧩 #1589 🥳 score:38 ⏱️ 0:11:45.940252
- 🔗 cemantix.certitudes.org 🧩 #1572 🥳 51 ⏱️ 0:00:27.880789

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












# [spaceword.org](spaceword.org) 🧩 2026-06-20 🏁 score 2173 ranked 11.0% 33/301 ⏱️ 2:31:12.423173

📜 7 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 33/301

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ Y _ F O V E A T E   
      _ A _ O _ _ D E A R   
      _ K I B L A S _ X _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #596 🥳 38 ⏱️ 0:01:00.721316

🤔 38 attempts
📜 1 sessions

    @       [    0] &-teken   
    @+49817 [49817] boks      q6  ? ␅
    @+49817 [49817] boks      q7  ? after
    @+62256 [62256] cement    q10 ? ␅
    @+62256 [62256] cement    q11 ? after
    @+68490 [68490] connectie q12 ? ␅
    @+68490 [68490] connectie q13 ? after
    @+71561 [71561] cru       q14 ? ␅
    @+71561 [71561] cru       q15 ? after
    @+72851 [72851] dag       q16 ? ␅
    @+72851 [72851] dag       q17 ? after
    @+73303 [73303] dagzorg   q20 ? ␅
    @+73303 [73303] dagzorg   q21 ? after
    @+73477 [73477] dal       q22 ? ␅
    @+73477 [73477] dal       q23 ? after
    @+73536 [73536] dalton    q28 ? ␅
    @+73536 [73536] dalton    q29 ? after
    @+73558 [73558] dam       q30 ? ␅
    @+73558 [73558] dam       q31 ? after
    @+73576 [73576] dambord   q32 ? ␅
    @+73576 [73576] dambord   q33 ? after
    @+73584 [73584] damde     q34 ? ␅
    @+73584 [73584] damde     q35 ? after
    @+73586 [73586] dame      q36 ? ␅
    @+73586 [73586] dame      q37 ? it
    @+73586 [73586] dame      done. it
    @+73591 [73591] dames     q24 ? ␅
    @+73591 [73591] dames     q25 ? before
    @+73754 [73754] damp      q18 ? ␅
    @+73754 [73754] damp      q19 ? before
    @+74720 [74720] dc        q9  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1063 🥳 30 ⏱️ 0:00:45.232132

🤔 30 attempts
📜 1 sessions

    @        [     0] aa       
    @+98214  [ 98214] mach     q0  ? ␅
    @+98214  [ 98214] mach     q1  ? after
    @+98214  [ 98214] mach     q2  ? ␅
    @+98214  [ 98214] mach     q3  ? after
    @+104069 [104069] minor    q10 ? ␅
    @+104069 [104069] minor    q11 ? after
    @+106935 [106935] mor      q12 ? ␅
    @+106935 [106935] mor      q13 ? after
    @+107249 [107249] mot      q18 ? ␅
    @+107249 [107249] mot      q19 ? after
    @+107450 [107450] mould    q20 ? ␅
    @+107450 [107450] mould    q21 ? after
    @+107481 [107481] mount    q24 ? ␅
    @+107481 [107481] mount    q25 ? after
    @+107514 [107514] mourn    q26 ? ␅
    @+107514 [107514] mourn    q27 ? after
    @+107532 [107532] mouse    q28 ? ␅
    @+107532 [107532] mouse    q29 ? it
    @+107532 [107532] mouse    done. it
    @+107558 [107558] mousse   q22 ? ␅
    @+107558 [107558] mousse   q23 ? before
    @+107672 [107672] mridanga q16 ? ␅
    @+107672 [107672] mridanga q17 ? before
    @+108415 [108415] mun      q14 ? ␅
    @+108415 [108415] mun      q15 ? before
    @+109931 [109931] ne       q8  ? ␅
    @+109931 [109931] ne       q9  ? before
    @+122775 [122775] parr     q6  ? ␅
    @+122775 [122775] parr     q7  ? before
    @+147364 [147364] rhotic   q5  ? before

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1632 🥳 19 ⏱️ 0:04:54.800572

📜 2 sessions
💰 score: 9700

    4/6
    RAISE 🟨⬜🟨⬜⬜
    CURIO ⬜⬜🟨🟨🟨
    IVORY 🟩⬜🟩🟨🟩
    IRONY 🟩🟩🟩🟩🟩
    4/6
    IRONY 🟨🟨⬜⬜⬜
    MISER ⬜🟩⬜⬜🟨
    RIGHT 🟩🟩⬜⬜⬜
    RIVAL 🟩🟩🟩🟩🟩
    4/6
    RIVAL 🟨⬜⬜🟨⬜
    STARE ⬜⬜🟨🟩⬜
    ACORN 🟨🟨🟨🟩⬜
    COBRA 🟩🟩🟩🟩🟩
    5/6
    COBRA ⬜⬜⬜⬜⬜
    TUILE ⬜⬜🟩🟩🟩
    WHILE ⬜⬜🟩🟩🟩
    SMILE ⬜⬜🟩🟩🟩
    EXILE 🟩🟩🟩🟩🟩
    Final 2/2
    DICKY ⬜🟩🟩🟩🟩
    PICKY 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1609 🥳 score:26 ⏱️ 0:01:29.678974

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. ABBOT attempts:7 score:7
2. NOTCH attempts:8 score:8
3. DREAD attempts:5 score:5
4. LURID attempts:6 score:6

# [dontwordle.com](dontwordle.com) 🧩 #1489 🥳 6 ⏱️ 0:02:24.168112

📜 1 sessions
💰 score: 64

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:PZAZZ n n n n n remain:6291
    ⬜⬜⬜⬜⬜ tried:LULUS n n n n n remain:1775
    ⬜⬜⬜⬜⬜ tried:JINNI n n n n n remain:707
    ⬜⬜⬜⬜⬜ tried:MYTHY n n n n n remain:199
    ⬜🟩⬜⬜⬜ tried:KEEVE n Y n n n remain:14
    ⬜🟩🟨⬜⬜ tried:FEOFF n Y m n n remain:8

    Undos used: 4

      8 words remaining
    x 8 unused letters
    = 64 total score

# [squareword.org](squareword.org) 🧩 #1602 🥳 8 ⏱️ 0:03:24.338494

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T A F F
    M O R A L
    A N G L E
    R E U S E
    T R E E S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1539 🥳 253 ⏱️ 0:12:54.651059

🤔 254 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 49 chat prompts
🤖 49 dolphin3:latest replies
😱   1 🔥   8 🥵  29 😎  62 🥶 139 🧊  14

      $1 #254 counsel         100.00°C 🥳 1000‰ ~240 used:0  [239]  source:dolphin3
      $2  #70 attorney         66.77°C 😱  999‰   ~7 used:51 [6]    source:dolphin3
      $3  #80 lawyer           64.96°C 🔥  998‰  ~36 used:23 [35]   source:dolphin3
      $4  #85 solicitor        55.75°C 🔥  997‰   ~8 used:8  [7]    source:dolphin3
      $5 #234 litigator        53.65°C 🔥  996‰   ~2 used:5  [1]    source:dolphin3
      $6 #233 adviser          48.47°C 🔥  994‰   ~3 used:5  [2]    source:dolphin3
      $7  #68 advisor          47.73°C 🔥  993‰   ~4 used:5  [3]    source:dolphin3
      $8  #73 barrister        46.44°C 🔥  992‰   ~5 used:5  [4]    source:dolphin3
      $9  #84 secretary        46.41°C 🔥  991‰   ~6 used:5  [5]    source:dolphin3
     $10 #192 prosecutor       46.35°C 🔥  990‰   ~1 used:4  [0]    source:dolphin3
     $11  #90 litigation       45.31°C 🥵  989‰   ~9 used:0  [8]    source:dolphin3
     $40 #250 secretaryship    30.92°C 😎  878‰  ~39 used:0  [38]   source:dolphin3
    $102  #64 mentor           19.26°C 🥶       ~101 used:0  [100]  source:dolphin3
    $241  #37 sheet            -0.34°C 🧊       ~241 used:0  [240]  source:dolphin3

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1609 🥳 score:58 ⏱️ 0:03:48.658156

📜 2 sessions

Octordle Classic

1. HEAVE attempts:7 score:7
2. WACKY attempts:5 score:5
3. PAYEE attempts:6 score:6
4. FEWER attempts:8 score:8
5. INANE attempts:9 score:9
6. STEEL attempts:11 score:11
7. SERIF attempts:2 score:2
8. SLUSH attempts:10 score:10

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1589 🥳 score:38 ⏱️ 0:11:45.940252

📜 3 sessions

Sedecordle Classic sedecordle.com

1. NUDGE attempts:17 score:1
2. EAGER attempts:19 score:7
3. DEBIT attempts:16 score:1
4. CREDO attempts:3 score:6
5. ORGAN attempts:15 score:1
6. CURVY attempts:14 score:5
7. GLARE attempts:6 score:1
8. ROOMY attempts:13 score:0
9. TRYST attempts:12 score:1
10. SLOPE attempts:5 score:2
11. CLERK attempts:4 score:0
12. SCOUR attempts:8 score:4
13. HUSSY attempts:11 score:1
14. RIVAL attempts:9 score:1
15. HARPY attempts:7 score:0
16. GRASP attempts:6 score:7

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1572 🥳 51 ⏱️ 0:00:27.880789

🤔 52 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 7 chat prompts
🤖 7 dolphin3:latest replies
🥵  1 😎  3 🥶 30 🧊 17

     $1 #52 commande    100.00°C 🥳 1000‰ ~35 used:0 [34]  source:dolphin3
     $2 #51 bouton       40.63°C 🥵  979‰  ~1 used:0 [0]   source:dolphin3
     $3 #35 appareil     25.57°C 😎  529‰  ~2 used:1 [1]   source:dolphin3
     $4 #44 navigation   23.61°C 😎  337‰  ~3 used:1 [2]   source:dolphin3
     $5 #36 boîte        21.78°C 😎   83‰  ~4 used:1 [3]   source:dolphin3
     $6 #12 véhicule     19.51°C 🥶        ~5 used:4 [4]   source:dolphin3
     $7 #42 manette      18.93°C 🥶        ~7 used:1 [6]   source:dolphin3
     $8 #38 clé          17.86°C 🥶        ~8 used:0 [7]   source:dolphin3
     $9 #43 molette      17.47°C 🥶        ~9 used:0 [8]   source:dolphin3
    $10 #41 levier       16.72°C 🥶       ~10 used:0 [9]   source:dolphin3
    $11 #29 chaussures   10.50°C 🥶       ~11 used:1 [10]  source:dolphin3
    $12 #45 pneu         10.36°C 🥶       ~12 used:0 [11]  source:dolphin3
    $13 #48 sécurité     10.21°C 🥶       ~13 used:0 [12]  source:dolphin3
    $36 #15 vélo         -0.36°C 🧊       ~36 used:0 [35]  source:dolphin3
