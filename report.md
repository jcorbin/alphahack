# 2026-02-11

- 🔗 spaceword.org 🧩 2026-02-10 🏁 score 2173 ranked 7.0% 24/344 ⏱️ 4:43:18.198624
- 🔗 alfagok.diginaut.net 🧩 #466 🥳 50 ⏱️ 0:01:02.079819
- 🔗 alphaguess.com 🧩 #933 🥳 34 ⏱️ 0:00:46.568356
- 🔗 dontwordle.com 🧩 #1359 🥳 6 ⏱️ 0:01:56.992232
- 🔗 dictionary.com hurdle 🧩 #1502 🥳 20 ⏱️ 0:04:47.689911
- 🔗 Quordle Classic 🧩 #1479 🥳 score:26 ⏱️ 0:01:42.711870
- 🔗 Octordle Classic 🧩 #1479 🥳 score:55 ⏱️ 0:03:20.185078
- 🔗 squareword.org 🧩 #1472 🥳 7 ⏱️ 0:02:09.872577
- 🔗 cemantle.certitudes.org 🧩 #1409 🥳 29 ⏱️ 0:23:37.023329
- 🔗 cemantix.certitudes.org 🧩 #1442 🥳 567 ⏱️ 1:46:41.434904
- 🔗 Quordle Rescue 🧩 #93 🥳 score:27 ⏱️ 0:02:04.122615
- 🔗 Octordle Rescue 🧩 #1479 🥳 score:8 ⏱️ 0:03:55.296741

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



























# [spaceword.org](spaceword.org) 🧩 2026-02-10 🏁 score 2173 ranked 7.0% 24/344 ⏱️ 4:43:18.198624

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 24/344

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ E C U _ _ _   
      _ _ _ _ _ _ N _ _ _   
      _ _ _ _ _ I S _ _ _   
      _ _ _ _ H O E _ _ _   
      _ _ _ _ _ N A _ _ _   
      _ _ _ _ W I T _ _ _   
      _ _ _ _ _ Z _ _ _ _   
      _ _ _ _ K E F _ _ _   
      _ _ _ _ I R E _ _ _   


# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1409 🥳 29 ⏱️ 0:23:37.023329

🤔 30 attempts
📜 2 sessions
🫧 13 chat sessions
⁉️ 15 chat prompts
🤖 15 ServiceNow-AI/Apriel-1.6-15b-Thinker:Q4_K_M replies
🥵  3 😎  7 🥶 18 🧊  1

     $1 #30 carol        100.00°C 🥳 1000‰ ~29 used:0  [28]  source:ServiceNow
     $2 #19 song          44.59°C 🥵  964‰  ~3 used:10 [2]   source:ServiceNow
     $3 #27 ditty         41.40°C 🥵  935‰  ~1 used:1  [0]   source:ServiceNow
     $4 #16 melody        39.31°C 🥵  911‰  ~2 used:2  [1]   source:ServiceNow
     $5 #14 music         37.99°C 😎  886‰  ~4 used:1  [3]   source:ServiceNow
     $6 #21 lyric         36.71°C 😎  859‰  ~5 used:0  [4]   source:ServiceNow
     $7  #6 piano         36.33°C 😎  851‰ ~10 used:2  [9]   source:ServiceNow
     $8 #20 chorus        36.30°C 😎  848‰  ~6 used:0  [5]   source:ServiceNow
     $9 #25 ballad        35.57°C 😎  829‰  ~7 used:0  [6]   source:ServiceNow
    $10  #4 lantern       34.75°C 😎  792‰  ~8 used:0  [7]   source:ServiceNow
    $11 #23 anthem        34.34°C 😎  781‰  ~9 used:0  [8]   source:ServiceNow
    $12 #22 tune          25.28°C 🥶       ~11 used:0  [10]  source:ServiceNow
    $13 #28 motif         23.14°C 🥶       ~12 used:0  [11]  source:ServiceNow
    $30 #13 scale         -1.99°C 🧊       ~30 used:0  [29]  source:ServiceNow

# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #466 🥳 50 ⏱️ 0:01:02.079819

🤔 50 attempts
📜 1 sessions

    @       [    0] &-teken   
    @+49842 [49842] boks      q4  ? ␅
    @+49842 [49842] boks      q5  ? after
    @+74755 [74755] dc        q6  ? ␅
    @+74755 [74755] dc        q7  ? after
    @+87216 [87216] draag     q8  ? ␅
    @+87216 [87216] draag     q9  ? after
    @+90068 [90068] dubbel    q12 ? ␅
    @+90068 [90068] dubbel    q13 ? after
    @+90258 [90258] dubbels   q36 ? ␅
    @+90258 [90258] dubbels   q37 ? after
    @+90371 [90371] ducht     q40 ? ␅
    @+90371 [90371] ducht     q41 ? after
    @+90415 [90415] duf       q42 ? ␅
    @+90415 [90415] duf       q43 ? after
    @+90435 [90435] duid      q44 ? ␅
    @+90435 [90435] duid      q45 ? after
    @+90438 [90438] duidelijk q48 ? ␅
    @+90438 [90438] duidelijk q49 ? it
    @+90438 [90438] duidelijk done. it
    @+90457 [90457] duif      q46 ? ␅
    @+90457 [90457] duif      q47 ? before
    @+90481 [90481] duik      q34 ? ␅
    @+90481 [90481] duik      q35 ? before
    @+90885 [90885] duivels   q16 ? ␅
    @+90885 [90885] duivels   q17 ? before
    @+91747 [91747] dwerg     q14 ? ␅
    @+91747 [91747] dwerg     q15 ? before
    @+93435 [93435] eet       q10 ? ␅
    @+93435 [93435] eet       q11 ? before
    @+99742 [99742] ex        q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #933 🥳 34 ⏱️ 0:00:46.568356

🤔 34 attempts
📜 1 sessions

    @        [     0] aa           
    @+98219  [ 98219] mach         q0  ? ␅
    @+98219  [ 98219] mach         q1  ? after
    @+122780 [122780] parr         q4  ? ␅
    @+122780 [122780] parr         q5  ? after
    @+135071 [135071] proper       q6  ? ␅
    @+135071 [135071] proper       q7  ? after
    @+137791 [137791] quart        q10 ? ␅
    @+137791 [137791] quart        q11 ? after
    @+137862 [137862] quass        q20 ? ␅
    @+137862 [137862] quass        q21 ? after
    @+137898 [137898] quays        q22 ? ␅
    @+137898 [137898] quays        q23 ? after
    @+137908 [137908] queasiest    q26 ? ␅
    @+137908 [137908] queasiest    q27 ? after
    @+137911 [137911] queasinesses q30 ? ␅
    @+137911 [137911] queasinesses q31 ? after
    @+137912 [137912] queasy       q32 ? ␅
    @+137912 [137912] queasy       q33 ? it
    @+137912 [137912] queasy       done. it
    @+137913 [137913] queazier     q28 ? ␅
    @+137913 [137913] queazier     q29 ? before
    @+137918 [137918] queen        q24 ? ␅
    @+137918 [137918] queen        q25 ? before
    @+137940 [137940] queer        q18 ? ␅
    @+137940 [137940] queer        q19 ? before
    @+138104 [138104] quiff        q16 ? ␅
    @+138104 [138104] quiff        q17 ? before
    @+138419 [138419] rabbit       q14 ? ␅
    @+138419 [138419] rabbit       q15 ? before
    @+139060 [139060] ram          q13 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1359 🥳 6 ⏱️ 0:01:56.992232

📜 1 sessions
💰 score: 9

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:YUMMY n n n n n remain:7572
    ⬜⬜⬜⬜⬜ tried:BOBOS n n n n n remain:2134
    ⬜⬜⬜⬜⬜ tried:PIPIT n n n n n remain:666
    ⬜🟩⬜⬜⬜ tried:GRRRL n Y n n n remain:43
    ⬜🟩🟩⬜⬜ tried:CREEK n Y Y n n remain:5
    🟨🟩🟩⬜⬜ tried:ARENA m Y Y n n remain:1

    Undos used: 3

      1 words remaining
    x 9 unused letters
    = 9 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1502 🥳 20 ⏱️ 0:04:47.689911

📜 1 sessions
💰 score: 9600

    4/6
    ASTER ⬜🟨🟨⬜⬜
    STOIC 🟩🟩🟩⬜⬜
    STOMP 🟩🟩🟩⬜⬜
    STONY 🟩🟩🟩🟩🟩
    5/6
    STONY 🟩⬜⬜⬜⬜
    SHARK 🟩🟩🟩⬜⬜
    SHAME 🟩🟩🟩⬜🟩
    SHADE 🟩🟩🟩⬜🟩
    SHAVE 🟩🟩🟩🟩🟩
    3/6
    SHAVE ⬜⬜🟨⬜⬜
    MORAL 🟨🟨⬜🟨⬜
    AMINO 🟩🟩🟩🟩🟩
    6/6
    AMINO ⬜⬜⬜⬜🟨
    LOSER ⬜🟨⬜🟨🟨
    OVERT 🟨⬜🟨🟨⬜
    PROBE ⬜🟩🟩⬜🟩
    ERODE ⬜🟩🟩⬜🟩
    FROZE 🟩🟩🟩🟩🟩
    Final 2/2
    COURT ⬜🟨🟨🟨🟨
    TUTOR 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1479 🥳 score:26 ⏱️ 0:01:42.711870

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. TRYST attempts:4 score:4
2. LIEGE attempts:8 score:8
3. ANGER attempts:5 score:5
4. HUTCH attempts:9 score:9

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1479 🥳 score:55 ⏱️ 0:03:20.185078

📜 1 sessions

Octordle Classic

1. AUNTY attempts:3 score:3
2. ENEMY attempts:6 score:6
3. BEZEL attempts:12 score:12
4. TULLE attempts:4 score:4
5. TREND attempts:7 score:7
6. HEADY attempts:8 score:8
7. FANCY attempts:10 score:10
8. RHINO attempts:5 score:5

# [squareword.org](squareword.org) 🧩 #1472 🥳 7 ⏱️ 0:02:09.872577

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    F U T O N
    U N I T E
    S T A T E
    S I R E D
    Y E A R S

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1442 🥳 567 ⏱️ 1:46:41.434904

🤔 568 attempts
📜 1 sessions
🫧 66 chat sessions
⁉️ 297 chat prompts
🤖 10 ServiceNow-AI/Apriel-1.6-15b-Thinker:Q4_K_M replies
🤖 236 dolphin3:latest replies
🤖 51 granite-code:8b replies
🔥   7 🥵  24 😎  73 🥶 328 🧊 135

      $1 #568 crédible          100.00°C 🥳 1000‰ ~433 used:0   [432]  source:ServiceNow
      $2 #362 convaincant        59.63°C 🔥  998‰  ~97 used:231 [96]   source:dolphin3  
      $3 #476 réaliste           56.44°C 🔥  997‰  ~11 used:39  [10]   source:dolphin3  
      $4 #567 réellement         50.60°C 🔥  996‰   ~1 used:0   [0]    source:ServiceNow
      $5 #293 convaincre         49.89°C 🔥  995‰  ~92 used:141 [91]   source:dolphin3  
      $6 #479 plausible          48.98°C 🔥  994‰   ~4 used:29  [3]    source:dolphin3  
      $7 #492 cohérent           48.98°C 🔥  993‰   ~5 used:30  [4]    source:dolphin3  
      $8 #444 vrai               48.29°C 🔥  991‰  ~12 used:40  [11]   source:dolphin3  
      $9 #374 évident            44.96°C 🥵  985‰  ~96 used:21  [95]   source:dolphin3  
     $10 #485 sérieux            43.53°C 🥵  981‰   ~6 used:3   [5]    source:dolphin3  
     $11 #414 clair              43.47°C 🥵  980‰  ~24 used:10  [23]   source:dolphin3  
     $33 #289 supposer           36.80°C 😎  897‰  ~26 used:0   [25]   source:dolphin3  
    $106 #317 démentir           24.48°C 🥶       ~113 used:0   [112]  source:dolphin3  
    $434 #143 détecteur          -0.02°C 🧊       ~434 used:0   [433]  source:dolphin3  

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #93 🥳 score:27 ⏱️ 0:02:04.122615

📜 2 sessions

Quordle Rescue m-w.com/games/quordle/

1. RABBI attempts:6 score:6
2. SUING attempts:8 score:8
3. RISEN attempts:4 score:4
4. SWOOP attempts:9 score:9

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1479 🥳 score:8 ⏱️ 0:03:55.296741

📜 1 sessions

Octordle Rescue

1. BLESS attempts:8 score:8
2. SHOOK attempts:6 score:6
3. PANEL attempts:12 score:12
4. STUFF attempts:10 score:10
5. SMOCK attempts:5 score:5
6. CRISP attempts:7 score:7
7. LEVEL attempts:13 score:13
8. GOURD attempts:9 score:9
