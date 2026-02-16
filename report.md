# 2026-02-17

- 🔗 spaceword.org 🧩 2026-02-16 🏁 score 2168 ranked 44.8% 156/348 ⏱️ 5:33:58.128401
- 🔗 alphaguess.com 🧩 #939 🥳 36 ⏱️ 0:00:35.280158
- 🔗 alfagok.diginaut.net 🧩 #472 🥳 28 ⏱️ 0:00:30.543290
- 🔗 dontwordle.com 🧩 #1365 🥳 6 ⏱️ 0:01:50.943875
- 🔗 cemantix.certitudes.org 🧩 #1448 🥳 138 ⏱️ 0:03:04.173155
- 🔗 dictionary.com hurdle 🧩 #1508 😦 18 ⏱️ 0:03:08.208806
- 🔗 Quordle Classic 🧩 #1485 🥳 score:24 ⏱️ 0:01:24.423796
- 🔗 Octordle Classic 🧩 #1485 🥳 score:64 ⏱️ 0:04:31.025531
- 🔗 squareword.org 🧩 #1478 🥳 6 ⏱️ 0:01:50.320050
- 🔗 cemantle.certitudes.org 🧩 #1415 🥳 167 ⏱️ 0:01:26.394527

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

































# [spaceword.org](spaceword.org) 🧩 2026-02-16 🏁 score 2168 ranked 44.8% 156/348 ⏱️ 5:33:58.128401

📜 5 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 156/348

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ O R G _ _ _ _ E _   
      _ I _ _ J _ _ _ P _   
      _ L O Q U A T _ E _   
      _ _ W I N D A G E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alphaguess.com](alphaguess.com) 🧩 #939 🥳 36 ⏱️ 0:00:35.280158

🤔 36 attempts
📜 1 sessions

    @        [     0] aa        
    @+98219  [ 98219] mach      q0  ? ␅
    @+98219  [ 98219] mach      q1  ? after
    @+147375 [147375] rhumb     q2  ? ␅
    @+147375 [147375] rhumb     q3  ? after
    @+159487 [159487] slop      q6  ? ␅
    @+159487 [159487] slop      q7  ? after
    @+162474 [162474] spec      q10 ? ␅
    @+162474 [162474] spec      q11 ? after
    @+164000 [164000] squab     q12 ? ␅
    @+164000 [164000] squab     q13 ? after
    @+164030 [164030] squall    q22 ? ␅
    @+164030 [164030] squall    q23 ? after
    @+164036 [164036] squalling q28 ? ␅
    @+164036 [164036] squalling q29 ? after
    @+164039 [164039] squally   q30 ? ␅
    @+164039 [164039] squally   q31 ? after
    @+164040 [164040] squalor   q34 ? ␅
    @+164040 [164040] squalor   q35 ? it
    @+164040 [164040] squalor   done. it
    @+164041 [164041] squalors  q32 ? ␅
    @+164041 [164041] squalors  q33 ? before
    @+164042 [164042] squama    q26 ? ␅
    @+164042 [164042] squama    q27 ? before
    @+164053 [164053] squander  q24 ? ␅
    @+164053 [164053] squander  q25 ? before
    @+164076 [164076] squash    q20 ? ␅
    @+164076 [164076] squash    q21 ? before
    @+164176 [164176] squid     q18 ? ␅
    @+164176 [164176] squid     q19 ? before
    @+164354 [164354] stack     q17 ? before

# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #472 🥳 28 ⏱️ 0:00:30.543290

🤔 28 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+2      [     2] -cijferig    
    @+99742  [ 99742] ex           q2  ? ␅
    @+99742  [ 99742] ex           q3  ? after
    @+149438 [149438] huis         q4  ? ␅
    @+149438 [149438] huis         q5  ? after
    @+174545 [174545] kind         q6  ? ␅
    @+174545 [174545] kind         q7  ? after
    @+187181 [187181] krontjongs   q8  ? ␅
    @+187181 [187181] krontjongs   q9  ? after
    @+193482 [193482] lavendel     q10 ? ␅
    @+193482 [193482] lavendel     q11 ? after
    @+194907 [194907] lees         q14 ? ␅
    @+194907 [194907] lees         q15 ? after
    @+195624 [195624] leid         q16 ? ␅
    @+195624 [195624] leid         q17 ? after
    @+195633 [195633] leiden       q26 ? ␅
    @+195633 [195633] leiden       q27 ? it
    @+195633 [195633] leiden       done. it
    @+195642 [195642] leiders      q24 ? ␅
    @+195642 [195642] leiders      q25 ? before
    @+195706 [195706] leidmotieven q22 ? ␅
    @+195706 [195706] leidmotieven q23 ? before
    @+195787 [195787] lek          q20 ? ␅
    @+195787 [195787] lek          q21 ? before
    @+196052 [196052] lengte       q18 ? ␅
    @+196052 [196052] lengte       q19 ? before
    @+196498 [196498] les          q12 ? ␅
    @+196498 [196498] les          q13 ? before
    @+199817 [199817] lijm         q0  ? ␅
    @+199817 [199817] lijm         q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1365 🥳 6 ⏱️ 0:01:50.943875

📜 1 sessions
💰 score: 80

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:GAMMA n n n n n remain:5731
    ⬜⬜⬜⬜⬜ tried:TITIS n n n n n remain:1297
    ⬜⬜⬜⬜⬜ tried:YUKKY n n n n n remain:519
    ⬜⬜🟨⬜⬜ tried:BLOND n n m n n remain:42
    ⬜🟨🟨🟨⬜ tried:XEROX n m m m n remain:15
    🟨⬜⬜🟩🟩 tried:OFFER m n n Y Y remain:10

    Undos used: 3

      10 words remaining
    x 8 unused letters
    = 80 total score

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1448 🥳 138 ⏱️ 0:03:04.173155

🤔 139 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 28 chat prompts
🤖 28 dolphin3:latest replies
🔥  1 🥵  2 😎 10 🥶 86 🧊 39

      $1 #139 portable        100.00°C 🥳 1000‰ ~100 used:0  [99]   source:dolphin3
      $2 #136 téléphone        53.95°C 😱  999‰   ~1 used:0  [0]    source:dolphin3
      $3  #80 poche            33.53°C 🥵  913‰   ~9 used:18 [8]    source:dolphin3
      $4  #72 sac              33.38°C 🥵  909‰   ~8 used:15 [7]    source:dolphin3
      $5   #9 voiture          29.32°C 😎  835‰  ~13 used:11 [12]   source:dolphin3
      $6  #88 étui             28.10°C 😎  802‰  ~10 used:2  [9]    source:dolphin3
      $7  #81 valise           24.52°C 😎  606‰  ~11 used:2  [10]   source:dolphin3
      $8  #90 cartable         22.65°C 😎  431‰   ~2 used:1  [1]    source:dolphin3
      $9 #116 toilette         21.52°C 😎  290‰   ~3 used:0  [2]    source:dolphin3
     $10  #96 cabine           21.10°C 😎  221‰  ~12 used:2  [11]   source:dolphin3
     $11  #46 cadeau           21.03°C 😎  210‰   ~4 used:1  [3]    source:dolphin3
     $12  #71 mallette         20.78°C 😎  167‰   ~5 used:1  [4]    source:dolphin3
     $15  #87 pochette         19.66°C 🥶        ~16 used:0  [15]   source:dolphin3
    $101  #41 rêverie          -0.26°C 🧊       ~101 used:0  [100]  source:dolphin3

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1508 😦 18 ⏱️ 0:03:08.208806

📜 1 sessions
💰 score: 4880

    4/6
    RAISE 🟨⬜⬜⬜🟨
    OUTER 🟨⬜⬜🟨🟩
    DECOR ⬜🟨⬜🟩🟩
    ERROR 🟩🟩🟩🟩🟩
    4/6
    ERROR 🟨⬜⬜⬜⬜
    TEAMS 🟩🟩⬜⬜⬜
    TENCH 🟩🟩🟩⬜🟩
    TENTH 🟩🟩🟩🟩🟩
    4/6
    TENTH ⬜⬜🟨⬜⬜
    NARCO 🟨⬜⬜⬜⬜
    SLUNG ⬜🟩🟩🟩⬜
    FLUNK 🟩🟩🟩🟩🟩
    4/6
    FLUNK ⬜⬜⬜🟩⬜
    MEANS ⬜🟨⬜🟩⬜
    DRONE ⬜⬜🟨🟩🟩
    OPINE 🟩🟩🟩🟩🟩
    Final 2/2
    ????? 🟩🟩🟩⬜🟩
    ????? 🟩🟩🟩⬜🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1485 🥳 score:24 ⏱️ 0:01:24.423796

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. MUSTY attempts:7 score:7
2. FICUS attempts:5 score:5
3. BINGE attempts:8 score:8
4. FROND attempts:4 score:4

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1485 🥳 score:64 ⏱️ 0:04:31.025531

📜 1 sessions

Octordle Classic

1. WHINE attempts:9 score:9
2. FERAL attempts:4 score:4
3. SHUNT attempts:8 score:8
4. DOLLY attempts:13 score:13
5. QUILT attempts:11 score:11
6. DEFER attempts:12 score:12
7. NURSE attempts:2 score:2
8. PINEY attempts:5 score:5

# [squareword.org](squareword.org) 🧩 #1478 🥳 6 ⏱️ 0:01:50.320050

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C E A S E
    A R G O N
    R O A R S
    A D I E U
    T E N S E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1415 🥳 167 ⏱️ 0:01:26.394527

🤔 168 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 21 chat prompts
🤖 21 dolphin3:latest replies
🔥   6 🥵  16 😎  26 🥶 113 🧊   6

      $1 #168 electricity       100.00°C 🥳 1000‰ ~162 used:0  [161]  source:dolphin3
      $2 #114 energy             60.30°C 🔥  998‰  ~21 used:12 [20]   source:dolphin3
      $3 #138 hydroelectricity   59.14°C 🔥  997‰   ~3 used:7  [2]    source:dolphin3
      $4  #92 power              58.08°C 🔥  996‰   ~5 used:8  [4]    source:dolphin3
      $5  #87 electrical         57.26°C 🔥  995‰   ~2 used:6  [1]    source:dolphin3
      $6 #137 hydroelectric      53.88°C 🔥  991‰   ~1 used:3  [0]    source:dolphin3
      $7  #89 grid               51.37°C 🔥  990‰   ~4 used:7  [3]    source:dolphin3
      $8 #100 generator          49.62°C 🥵  987‰   ~6 used:0  [5]    source:dolphin3
      $9 #106 transformer        49.48°C 🥵  986‰   ~7 used:0  [6]    source:dolphin3
     $10 #129 renewable          47.85°C 🥵  984‰   ~8 used:0  [7]    source:dolphin3
     $11 #119 substation         46.61°C 🥵  982‰   ~9 used:0  [8]    source:dolphin3
     $24 #146 wind               34.56°C 😎  899‰  ~23 used:0  [22]   source:dolphin3
     $50 #118 station            20.52°C 🥶        ~50 used:0  [49]   source:dolphin3
    $163   #4 origami            -1.46°C 🧊       ~163 used:0  [162]  source:dolphin3
