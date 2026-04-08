# 2026-04-09

- 🔗 spaceword.org 🧩 2026-04-08 🏁 score 2173 ranked 7.0% 24/344 ⏱️ 4:02:48.757252
- 🔗 alfagok.diginaut.net 🧩 #523 🥳 18 ⏱️ 0:00:23.063676
- 🔗 alphaguess.com 🧩 #990 🥳 22 ⏱️ 0:00:23.439339
- 🔗 dontwordle.com 🧩 #1416 🥳 6 ⏱️ 0:01:53.536088
- 🔗 dictionary.com hurdle 🧩 #1559 😦 17 ⏱️ 0:03:39.703894
- 🔗 Quordle Classic 🧩 #1536 🥳 score:21 ⏱️ 0:01:32.871889
- 🔗 Octordle Classic 🧩 #1536 🥳 score:60 ⏱️ 0:03:19.073027
- 🔗 squareword.org 🧩 #1529 🥳 8 ⏱️ 0:02:03.880573
- 🔗 cemantle.certitudes.org 🧩 #1466 🥳 302 ⏱️ 0:04:57.049011
- 🔗 cemantix.certitudes.org 🧩 #1499 🥳 55 ⏱️ 0:01:14.049870

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







































# [spaceword.org](spaceword.org) 🧩 2026-04-08 🏁 score 2173 ranked 7.0% 24/344 ⏱️ 4:02:48.757252

📜 6 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 24/344

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ P _ W _ _ V _ G O   
      _ S _ A Q U I F E R   
      _ I O D I N E _ D A   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #523 🥳 18 ⏱️ 0:00:23.063676

🤔 18 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+49841  [ 49841] boks      q4  ? ␅
    @+49841  [ 49841] boks      q5  ? after
    @+74754  [ 74754] dc        q6  ? ␅
    @+74754  [ 74754] dc        q7  ? after
    @+87213  [ 87213] draag     q8  ? ␅
    @+87213  [ 87213] draag     q9  ? after
    @+93430  [ 93430] eet       q10 ? ␅
    @+93430  [ 93430] eet       q11 ? after
    @+94031  [ 94031] eigen     q16 ? ␅
    @+94031  [ 94031] eigen     q17 ? it
    @+94031  [ 94031] eigen     done. it
    @+94959  [ 94959] eiwit     q14 ? ␅
    @+94959  [ 94959] eiwit     q15 ? before
    @+96569  [ 96569] energiek  q12 ? ␅
    @+96569  [ 96569] energiek  q13 ? before
    @+99737  [ 99737] ex        q2  ? ␅
    @+99737  [ 99737] ex        q3  ? before
    @+199606 [199606] lij       q0  ? ␅
    @+199606 [199606] lij       q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #990 🥳 22 ⏱️ 0:00:23.439339

🤔 22 attempts
📜 1 sessions

    @       [    0] aa     
    @+1     [    1] aah    
    @+2     [    2] aahed  
    @+3     [    3] aahing 
    @+47380 [47380] dis    q4  ? ␅
    @+47380 [47380] dis    q5  ? after
    @+72798 [72798] gremmy q6  ? ␅
    @+72798 [72798] gremmy q7  ? after
    @+85502 [85502] ins    q8  ? ␅
    @+85502 [85502] ins    q9  ? after
    @+91846 [91846] knot   q10 ? ␅
    @+91846 [91846] knot   q11 ? after
    @+93266 [93266] lar    q14 ? ␅
    @+93266 [93266] lar    q15 ? after
    @+93894 [93894] lea    q16 ? ␅
    @+93894 [93894] lea    q17 ? after
    @+94407 [94407] leis   q18 ? ␅
    @+94407 [94407] leis   q19 ? after
    @+94666 [94666] letter q20 ? ␅
    @+94666 [94666] letter q21 ? it
    @+94666 [94666] letter done. it
    @+94943 [94943] lib    q12 ? ␅
    @+94943 [94943] lib    q13 ? before
    @+98216 [98216] mach   q0  ? ␅
    @+98216 [98216] mach   q1  ? after
    @+98216 [98216] mach   q2  ? ␅
    @+98216 [98216] mach   q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1416 🥳 6 ⏱️ 0:01:53.536088

📜 1 sessions
💰 score: 32

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:DOGGO n n n n n remain:6524
    ⬜⬜⬜⬜⬜ tried:YUMMY n n n n n remain:3556
    ⬜⬜⬜⬜⬜ tried:SEXES n n n n n remain:592
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:219
    ⬜⬜⬜⬜⬜ tried:ZANZA n n n n n remain:20
    🟨🟨⬜⬜⬜ tried:CIVIC m m n n n remain:4

    Undos used: 3

      4 words remaining
    x 8 unused letters
    = 32 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1559 😦 17 ⏱️ 0:03:39.703894

📜 1 sessions
💰 score: 4950

    3/6
    ASTER ⬜⬜🟩⬜⬜
    OPTIC ⬜🟨🟩🟨🟨
    PITCH 🟩🟩🟩🟩🟩
    4/6
    PITCH ⬜⬜⬜🟩🟩
    ORACH ⬜🟨🟨🟩🟩
    LARCH ⬜🟩🟩🟩🟩
    MARCH 🟩🟩🟩🟩🟩
    4/6
    MARCH ⬜🟨🟨⬜⬜
    AGERS 🟨⬜⬜🟨⬜
    TRONA ⬜🟩🟨⬜🟨
    BRAVO 🟩🟩🟩🟩🟩
    4/6
    BRAVO ⬜🟨🟨⬜⬜
    CARES 🟩🟩🟩⬜⬜
    CARNY 🟩🟩🟩⬜⬜
    CARAT 🟩🟩🟩🟩🟩
    Final 2/2
    ????? 🟨⬜🟨⬜⬜
    ????? ⬜🟩🟩🟨⬜

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1536 🥳 score:21 ⏱️ 0:01:32.871889

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SKIMP attempts:3 score:3
2. BAWDY attempts:5 score:5
3. WHERE attempts:6 score:6
4. DECOR attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1536 🥳 score:60 ⏱️ 0:03:19.073027

📜 1 sessions

Octordle Classic

1. SNOWY attempts:4 score:4
2. POLYP attempts:5 score:5
3. DIMLY attempts:6 score:6
4. UNTIL attempts:7 score:7
5. ROCKY attempts:8 score:8
6. HILLY attempts:10 score:10
7. MONTH attempts:9 score:9
8. TAKER attempts:11 score:11

# [squareword.org](squareword.org) 🧩 #1529 🥳 8 ⏱️ 0:02:03.880573

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A S S E T
    S H A M E
    C A B I N
    O V E R S
    T E R S E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1466 🥳 302 ⏱️ 0:04:57.049011

🤔 303 attempts
📜 1 sessions
🫧 17 chat sessions
⁉️ 93 chat prompts
🤖 93 dolphin3:latest replies
🔥   1 🥵  29 😎 104 🥶 167 🧊   1

      $1 #303 breakfast     100.00°C 🥳 1000‰ ~302 used:0  [301]  source:dolphin3
      $2 #169 dessert        53.37°C 🔥  992‰  ~12 used:50 [11]   source:dolphin3
      $3 #299 snack          51.27°C 🥵  989‰  ~16 used:6  [15]   source:dolphin3
      $4 #221 croissant      49.86°C 🥵  987‰ ~129 used:13 [128]  source:dolphin3
      $5 #237 oatmeal        49.76°C 🥵  986‰   ~8 used:4  [7]    source:dolphin3
      $6 #190 sandwich       48.00°C 🥵  981‰ ~128 used:12 [127]  source:dolphin3
      $7   #9 pizza          47.99°C 🥵  980‰ ~132 used:69 [131]  source:dolphin3
      $8 #302 coffee         47.86°C 🥵  979‰   ~1 used:2  [0]    source:dolphin3
      $9 #219 hamburger      46.72°C 🥵  974‰  ~17 used:6  [16]   source:dolphin3
     $10 #155 burger         46.46°C 🥵  973‰  ~25 used:9  [24]   source:dolphin3
     $11  #82 salad          46.20°C 🥵  971‰ ~130 used:20 [129]  source:dolphin3
     $32  #59 fondue         38.97°C 😎  898‰  ~27 used:0  [26]   source:dolphin3
    $136 #134 pizzeria       24.53°C 🥶       ~135 used:0  [134]  source:dolphin3
    $303  #58 con            -0.05°C 🧊       ~303 used:0  [302]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1499 🥳 55 ⏱️ 0:01:14.049870

🤔 56 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 15 chat prompts
🤖 15 dolphin3:latest replies
😱  1 🥵  4 😎 14 🥶 27 🧊  9

     $1 #56 comptabilité  100.00°C 🥳 1000‰ ~47 used:0  [46]  source:dolphin3
     $2 #52 comptable      79.50°C 😱  999‰  ~1 used:2  [0]   source:dolphin3
     $3 #21 réviseur       35.82°C 🥵  959‰ ~18 used:12 [17]  source:dolphin3
     $4 #26 exercice       34.27°C 🥵  943‰  ~3 used:5  [2]   source:dolphin3
     $5 #36 contrôleur     32.94°C 🥵  935‰  ~4 used:5  [3]   source:dolphin3
     $6 #38 vérificateur   30.83°C 🥵  905‰  ~2 used:3  [1]   source:dolphin3
     $7 #54 assistant      29.97°C 😎  885‰  ~5 used:0  [4]   source:dolphin3
     $8 #51 évaluation     26.75°C 😎  786‰  ~6 used:0  [5]   source:dolphin3
     $9 #35 étude          25.49°C 😎  729‰  ~7 used:0  [6]   source:dolphin3
    $10 #53 agréé          24.53°C 😎  670‰  ~8 used:0  [7]   source:dolphin3
    $11 #48 travail        24.09°C 😎  646‰  ~9 used:0  [8]   source:dolphin3
    $12 #28 examen         23.79°C 😎  624‰ ~10 used:0  [9]   source:dolphin3
    $21 #50 étudiant       17.23°C 🥶       ~20 used:0  [19]  source:dolphin3
    $48 #10 église         -7.09°C 🧊       ~48 used:0  [47]  source:dolphin3
