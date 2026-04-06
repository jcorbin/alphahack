# 2026-04-07

- 🔗 spaceword.org 🧩 2026-04-06 🏁 score 2173 ranked 54.5% 187/343 ⏱️ 12:23:56.088778
- 🔗 alfagok.diginaut.net 🧩 #521 🥳 34 ⏱️ 0:00:45.463365
- 🔗 alphaguess.com 🧩 #988 🥳 28 ⏱️ 0:00:31.703627
- 🔗 dontwordle.com 🧩 #1414 🥳 6 ⏱️ 0:01:55.543946
- 🔗 dictionary.com hurdle 🧩 #1557 😦 10 ⏱️ 0:01:48.655994
- 🔗 Quordle Classic 🧩 #1534 🥳 score:24 ⏱️ 0:01:33.168576
- 🔗 Octordle Classic 🧩 #1534 🥳 score:63 ⏱️ 0:04:23.754155
- 🔗 squareword.org 🧩 #1527 🥳 7 ⏱️ 0:02:20.160883
- 🔗 cemantle.certitudes.org 🧩 #1464 🥳 570 ⏱️ 0:08:11.360738
- 🔗 cemantix.certitudes.org 🧩 #1497 🥳 12 ⏱️ 0:33:48.383115

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





































# [spaceword.org](spaceword.org) 🧩 2026-04-06 🏁 score 2173 ranked 54.5% 187/343 ⏱️ 12:23:56.088778

📜 8 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 187/343

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ Z _ C O A G U L A   
      _ A _ _ _ X _ N U N   
      _ S O A K E R _ G I   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #521 🥳 34 ⏱️ 0:00:45.463365

🤔 34 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+2      [     2] -cijferig    
    @+199606 [199606] lij          q0  ? ␅
    @+199606 [199606] lij          q1  ? after
    @+299474 [299474] schro        q2  ? ␅
    @+299474 [299474] schro        q3  ? after
    @+305553 [305553] sleutel      q10 ? ␅
    @+305553 [305553] sleutel      q11 ? after
    @+308700 [308700] snurk        q12 ? ␅
    @+308700 [308700] snurk        q13 ? after
    @+310087 [310087] spa          q14 ? ␅
    @+310087 [310087] spa          q15 ? after
    @+310422 [310422] spanning     q18 ? ␅
    @+310422 [310422] spanning     q19 ? after
    @+310625 [310625] spawater     q22 ? ␅
    @+310625 [310625] spawater     q23 ? after
    @+310645 [310645] speciaal     q32 ? ␅
    @+310645 [310645] speciaal     q33 ? it
    @+310645 [310645] speciaal     done. it
    @+310670 [310670] specialisten q30 ? ␅
    @+310670 [310670] specialisten q31 ? before
    @+310726 [310726] spectaculair q28 ? ␅
    @+310726 [310726] spectaculair q29 ? before
    @+310824 [310824] speel        q16 ? ␅
    @+310824 [310824] speel        q17 ? before
    @+311857 [311857] spier        q8  ? ␅
    @+311857 [311857] spier        q9  ? before
    @+324409 [324409] subsidie     q6  ? ␅
    @+324409 [324409] subsidie     q7  ? before
    @+349455 [349455] vakantie     q4  ? ␅
    @+349455 [349455] vakantie     q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #988 🥳 28 ⏱️ 0:00:31.703627

🤔 28 attempts
📜 1 sessions

    @        [     0] aa       
    @+2      [     2] aahed    
    @+98216  [ 98216] mach     q0  ? ␅
    @+98216  [ 98216] mach     q1  ? after
    @+147371 [147371] rhumb    q2  ? ␅
    @+147371 [147371] rhumb    q3  ? after
    @+159483 [159483] slop     q6  ? ␅
    @+159483 [159483] slop     q7  ? after
    @+165525 [165525] stick    q8  ? ␅
    @+165525 [165525] stick    q9  ? after
    @+168577 [168577] sue      q10 ? ␅
    @+168577 [168577] sue      q11 ? after
    @+168903 [168903] sulphur  q16 ? ␅
    @+168903 [168903] sulphur  q17 ? after
    @+169065 [169065] sun      q18 ? ␅
    @+169065 [169065] sun      q19 ? after
    @+169143 [169143] sunk     q20 ? ␅
    @+169143 [169143] sunk     q21 ? after
    @+169185 [169185] suns     q22 ? ␅
    @+169185 [169185] suns     q23 ? after
    @+169193 [169193] sunset   q26 ? ␅
    @+169193 [169193] sunset   q27 ? it
    @+169193 [169193] sunset   done. it
    @+169206 [169206] sunstone q24 ? ␅
    @+169206 [169206] sunstone q25 ? before
    @+169227 [169227] super    q14 ? ␅
    @+169227 [169227] super    q15 ? before
    @+170084 [170084] surf     q12 ? ␅
    @+170084 [170084] surf     q13 ? before
    @+171636 [171636] ta       q4  ? ␅
    @+171636 [171636] ta       q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1414 🥳 6 ⏱️ 0:01:55.543946

📜 1 sessions
💰 score: 12

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:DOODY n n n n n remain:6216
    ⬜⬜⬜⬜⬜ tried:PENNE n n n n n remain:1935
    ⬜⬜⬜⬜⬜ tried:SWIMS n n n n n remain:240
    ⬜⬜⬜⬜⬜ tried:GRUFF n n n n n remain:42
    🟨⬜⬜⬜⬜ tried:ABAKA m n n n n remain:3
    ⬜🟩🟩🟩🟩 tried:CATCH n Y Y Y Y remain:2

    Undos used: 3

      2 words remaining
    x 6 unused letters
    = 12 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1557 😦 10 ⏱️ 0:01:48.655994

📜 1 sessions
💰 score: 1280

    4/6
    ETNAS ⬜⬜🟨⬜⬜
    UNRIP 🟨🟨🟨⬜⬜
    BOURN ⬜🟩🟩🟩🟩
    MOURN 🟩🟩🟩🟩🟩
    6/6
    ????? ⬜⬜⬜⬜🟨
    ????? 🟨⬜🟨⬜⬜
    ????? ⬜🟩🟩⬜⬜
    ????? 🟨🟩🟩⬜⬜
    ????? ⬜🟩🟩🟩🟩
    ????? ⬜🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1534 🥳 score:24 ⏱️ 0:01:33.168576

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. FIFTY attempts:9 score:9
2. SHUSH attempts:5 score:5
3. HELLO attempts:3 score:3
4. ZEBRA attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1534 🥳 score:63 ⏱️ 0:04:23.754155

📜 1 sessions

Octordle Classic

1. SLIME attempts:11 score:11
2. PARTY attempts:12 score:12
3. SADLY attempts:6 score:6
4. PENAL attempts:10 score:10
5. OVINE attempts:9 score:9
6. CRASS attempts:3 score:3
7. TRUSS attempts:4 score:4
8. HOVEL attempts:8 score:8

# [squareword.org](squareword.org) 🧩 #1527 🥳 7 ⏱️ 0:02:20.160883

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    F L O A T
    L A T H E
    E T H E R
    S T E A M
    H E R D S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1464 🥳 570 ⏱️ 0:08:11.360738

🤔 571 attempts
📜 1 sessions
🫧 27 chat sessions
⁉️ 142 chat prompts
🤖 142 dolphin3:latest replies
🔥   2 🥵  14 😎  77 🥶 420 🧊  57

      $1 #571 survivor        100.00°C 🥳 1000‰ ~514 used:0   [513]  source:dolphin3
      $2 #565 victim           49.92°C 🔥  998‰   ~1 used:2   [0]    source:dolphin3
      $3 #204 rescuer          40.40°C 🔥  996‰  ~86 used:126 [85]   source:dolphin3
      $4 #306 heroism          34.88°C 🥵  980‰  ~93 used:57  [92]   source:dolphin3
      $5 #563 rescued          34.25°C 🥵  976‰   ~2 used:1   [1]    source:dolphin3
      $6 #529 shipmate         33.57°C 🥵  972‰   ~5 used:7   [4]    source:dolphin3
      $7 #393 medic            33.38°C 🥵  969‰  ~87 used:14  [86]   source:dolphin3
      $8 #246 hero             32.99°C 🥵  960‰  ~88 used:16  [87]   source:dolphin3
      $9 #267 bravery          32.79°C 🥵  954‰  ~79 used:11  [78]   source:dolphin3
     $10 #438 trauma           32.66°C 🥵  950‰  ~80 used:11  [79]   source:dolphin3
     $11 #193 friend           32.18°C 🥵  945‰  ~81 used:11  [80]   source:dolphin3
     $18 #245 worker           29.61°C 😎  896‰  ~89 used:2   [88]   source:dolphin3
     $95 #427 driver           19.51°C 🥶       ~106 used:0   [105]  source:dolphin3
    $515 #114 slumber          -0.05°C 🧊       ~515 used:0   [514]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1497 🥳 12 ⏱️ 0:33:48.383115

🤔 13 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 4 chat prompts
🤖 4 dolphin3:latest replies
😱 1 🔥 3 🥶 7 🧊 1

     $1 #13 gris     100.00°C 🥳 1000‰ ~12 used:0 [11]  source:dolphin3
     $2 #11 noir      66.73°C 😱  999‰  ~1 used:0 [0]   source:dolphin3
     $3 #12 blanc     65.30°C 🔥  998‰  ~2 used:0 [1]   source:dolphin3
     $4 #10 bleu      65.17°C 🔥  997‰  ~3 used:0 [2]   source:dolphin3
     $5  #2 couleur   59.58°C 🔥  993‰  ~4 used:1 [3]   source:dolphin3
     $6  #1 chapeau   22.40°C 🥶        ~5 used:0 [4]   source:dolphin3
     $7  #8 voiture   19.10°C 🥶        ~6 used:0 [5]   source:dolphin3
     $8  #4 jardin    13.29°C 🥶        ~7 used:0 [6]   source:dolphin3
     $9  #3 gâteau    10.59°C 🥶        ~8 used:0 [7]   source:dolphin3
    $10  #7 ville      4.83°C 🥶        ~9 used:0 [8]   source:dolphin3
    $11  #6 musique    4.14°C 🥶       ~10 used:0 [9]   source:dolphin3
    $12  #5 livre      2.50°C 🥶       ~11 used:0 [10]  source:dolphin3
    $13  #9 école    -13.55°C 🧊       ~13 used:0 [12]  source:dolphin3
