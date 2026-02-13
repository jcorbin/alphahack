# 2026-02-14

- 🔗 spaceword.org 🧩 2026-02-13 🏁 score 2151 ranked 74.1% 263/355 ⏱️ 0:06:10.374288
- 🔗 alfagok.diginaut.net 🧩 #469 🥳 24 ⏱️ 0:00:29.423570
- 🔗 alphaguess.com 🧩 #936 🥳 32 ⏱️ 0:00:30.495449
- 🔗 dontwordle.com 🧩 #1362 🥳 6 ⏱️ 0:01:40.383786
- 🔗 dictionary.com hurdle 🧩 #1505 😦 17 ⏱️ 0:03:12.800845
- 🔗 Quordle Classic 🧩 #1482 🥳 score:21 ⏱️ 0:01:38.024335
- 🔗 Octordle Classic 🧩 #1482 🥳 score:66 ⏱️ 0:04:26.497323
- 🔗 squareword.org 🧩 #1475 🥳 7 ⏱️ 0:01:49.520052
- 🔗 cemantle.certitudes.org 🧩 #1412 🥳 161 ⏱️ 0:01:10.291930
- 🔗 cemantix.certitudes.org 🧩 #1445 🥳 345 ⏱️ 0:08:44.736362
- 🔗 Quordle Rescue 🧩 #96 🥳 score:25 ⏱️ 0:01:38.840831

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






























# [spaceword.org](spaceword.org) 🧩 2026-02-13 🏁 score 2151 ranked 74.1% 263/355 ⏱️ 0:06:10.374288

📜 2 sessions
- tiles: 21/21
- score: 2151 bonus: +51
- rank: 263/355

      _ _ _ _ _ _ _ _ _ _   
      _ _ E _ _ _ _ _ _ _   
      _ _ M I R Z A _ _ _   
      _ _ U _ O _ L _ _ _   
      _ _ _ D U C K I E _   
      _ _ _ _ T _ O _ _ _   
      _ _ _ _ S E X _ _ _   
      _ _ _ _ _ _ Y _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #469 🥳 24 ⏱️ 0:00:29.423570

🤔 24 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+1      [     1] &-tekens     
    @+2      [     2] -cijferig    
    @+3      [     3] -e-mail      
    @+99742  [ 99742] ex           q2  ? ␅
    @+99742  [ 99742] ex           q3  ? after
    @+111397 [111397] ge           q6  ? ␅
    @+111397 [111397] ge           q7  ? after
    @+120908 [120908] gequeruleerd q10 ? ␅
    @+120908 [120908] gequeruleerd q11 ? after
    @+125662 [125662] gezeglijk    q12 ? ␅
    @+125662 [125662] gezeglijk    q13 ? after
    @+128032 [128032] glazen       q14 ? ␅
    @+128032 [128032] glazen       q15 ? after
    @+129207 [129207] gok          q16 ? ␅
    @+129207 [129207] gok          q17 ? after
    @+129284 [129284] golf         q22 ? ␅
    @+129284 [129284] golf         q23 ? it
    @+129284 [129284] golf         done. it
    @+129478 [129478] gon          q20 ? ␅
    @+129478 [129478] gon          q21 ? before
    @+129785 [129785] gos          q18 ? ␅
    @+129785 [129785] gos          q19 ? before
    @+130418 [130418] gracieuze    q8  ? ␅
    @+130418 [130418] gracieuze    q9  ? before
    @+149438 [149438] huis         q4  ? ␅
    @+149438 [149438] huis         q5  ? before
    @+199817 [199817] lijm         q0  ? ␅
    @+199817 [199817] lijm         q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #936 🥳 32 ⏱️ 0:00:30.495449

🤔 32 attempts
📜 2 sessions

    @       [    0] aa           
    @+47381 [47381] dis          q2  ? ␅
    @+47381 [47381] dis          q3  ? after
    @+60084 [60084] face         q6  ? ␅
    @+60084 [60084] face         q7  ? after
    @+66440 [66440] french       q8  ? ␅
    @+66440 [66440] french       q9  ? after
    @+69620 [69620] geosynclinal q10 ? ␅
    @+69620 [69620] geosynclinal q11 ? after
    @+69925 [69925] gi           q16 ? ␅
    @+69925 [69925] gi           q17 ? after
    @+69926 [69926] giant        q30 ? ␅
    @+69926 [69926] giant        q31 ? it
    @+69926 [69926] giant        done. it
    @+69927 [69927] giantess     q28 ? ␅
    @+69927 [69927] giantess     q29 ? before
    @+69929 [69929] giantism     q26 ? ␅
    @+69929 [69929] giantism     q27 ? before
    @+69932 [69932] giants       q24 ? ␅
    @+69932 [69932] giants       q25 ? before
    @+69939 [69939] gib          q22 ? ␅
    @+69939 [69939] gib          q23 ? before
    @+70018 [70018] gig          q20 ? ␅
    @+70018 [70018] gig          q21 ? before
    @+70157 [70157] ginger       q18 ? ␅
    @+70157 [70157] ginger       q19 ? before
    @+70412 [70412] glam         q14 ? ␅
    @+70412 [70412] glam         q15 ? before
    @+71210 [71210] gnomist      q12 ? ␅
    @+71210 [71210] gnomist      q13 ? before
    @+72800 [72800] gremmy       q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1362 🥳 6 ⏱️ 0:01:40.383786

📜 1 sessions
💰 score: 80

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:QUEUE n n n n n remain:5479
    ⬜⬜⬜⬜⬜ tried:ROTOR n n n n n remain:1636
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:660
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:284
    🟨⬜⬜⬜🟩 tried:ABACA m n n n Y remain:30
    ⬜🟩⬜⬜🟩 tried:FANGA n Y n n Y remain:10

    Undos used: 3

      10 words remaining
    x 8 unused letters
    = 80 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1505 😦 17 ⏱️ 0:03:12.800845

📜 1 sessions
💰 score: 4960

    4/6
    PEARS ⬜⬜🟨⬜⬜
    FINAL ⬜🟨⬜🟨🟨
    DAILY ⬜🟨🟩🟩⬜
    VOILA 🟩🟩🟩🟩🟩
    4/6
    VOILA ⬜⬜⬜⬜⬜
    THRUM ⬜🟨⬜🟨⬜
    HUSKY 🟨🟩⬜⬜🟩
    DUCHY 🟩🟩🟩🟩🟩
    4/6
    DUCHY 🟨⬜⬜⬜⬜
    RADIO ⬜🟨🟨⬜⬜
    STAND ⬜⬜🟨⬜🟩
    PLEAD 🟩🟩🟩🟩🟩
    3/6
    PLEAD 🟩🟨⬜⬜⬜
    PILOT 🟩⬜🟩🟩⬜
    PYLON 🟩🟩🟩🟩🟩
    Final 2/2
    ????? 🟨⬜⬜🟩🟩
    ????? ⬜🟩⬜🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1482 🥳 score:21 ⏱️ 0:01:38.024335

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. TABOO attempts:6 score:6
2. BASIC attempts:3 score:3
3. SLOOP attempts:7 score:7
4. VOICE attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1482 🥳 score:66 ⏱️ 0:04:26.497323

📜 1 sessions

Octordle Classic

1. VAPOR attempts:8 score:8
2. SHOOK attempts:11 score:11
3. SLATE attempts:3 score:3
4. GOUGE attempts:6 score:6
5. EMBER attempts:12 score:12
6. CRUST attempts:4 score:4
7. REVUE attempts:9 score:9
8. WAFER attempts:13 score:13

# [squareword.org](squareword.org) 🧩 #1475 🥳 7 ⏱️ 0:01:49.520052

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C O N C H
    A L O H A
    R I V A L
    O V E R T
    B E L T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1412 🥳 161 ⏱️ 0:01:10.291930

🤔 162 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 20 chat prompts
🤖 20 dolphin3:latest replies
😱  1 🔥  4 🥵 27 😎 27 🥶 99 🧊  3

      $1 #162 tension           100.00°C 🥳 1000‰ ~159 used:0  [158]  source:dolphin3
      $2 #155 friction           71.98°C 😱  999‰   ~1 used:0  [0]    source:dolphin3
      $3 #107 animosity          62.61°C 🔥  998‰   ~4 used:2  [3]    source:dolphin3
      $4 #132 antagonism         62.34°C 🔥  997‰   ~2 used:0  [1]    source:dolphin3
      $5  #98 discord            61.12°C 🔥  996‰   ~5 used:6  [4]    source:dolphin3
      $6 #129 acrimony           57.95°C 🔥  993‰   ~3 used:0  [2]    source:dolphin3
      $7 #125 strife             54.94°C 🥵  989‰  ~29 used:2  [28]   source:dolphin3
      $8 #146 rancor             54.62°C 🥵  987‰   ~6 used:0  [5]    source:dolphin3
      $9 #120 hostility          54.09°C 🥵  986‰   ~7 used:1  [6]    source:dolphin3
     $10 #158 mistrust           52.36°C 🥵  982‰   ~8 used:0  [7]    source:dolphin3
     $11  #92 rift               51.73°C 🥵  981‰  ~32 used:6  [31]   source:dolphin3
     $34 #104 alienation         40.12°C 😎  896‰  ~33 used:0  [32]   source:dolphin3
     $61 #122 misalignment       25.21°C 🥶        ~65 used:0  [64]   source:dolphin3
    $160   #1 blueberry          -0.53°C 🧊       ~160 used:0  [159]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1445 🥳 345 ⏱️ 0:08:44.736362

🤔 346 attempts
📜 1 sessions
🫧 23 chat sessions
⁉️ 114 chat prompts
🤖 114 dolphin3:latest replies
🔥   7 🥵  10 😎  62 🥶 215 🧊  51

      $1 #346 remarquable         100.00°C 🥳 1000‰ ~295 used:0  [294]  source:dolphin3
      $2 #343 admirable            54.78°C 😱  999‰   ~1 used:0  [0]    source:dolphin3
      $3 #314 exceptionnel         52.59°C 🔥  997‰   ~6 used:8  [5]    source:dolphin3
      $4 #321 extraordinaire       52.57°C 🔥  996‰   ~4 used:4  [3]    source:dolphin3
      $5 #320 incomparable         51.74°C 🔥  994‰   ~3 used:3  [2]    source:dolphin3
      $6 #337 étonnant             51.68°C 🔥  993‰   ~2 used:1  [1]    source:dolphin3
      $7 #308 impressionnant       50.82°C 🔥  991‰   ~5 used:5  [4]    source:dolphin3
      $8 #267 originalité          49.68°C 🔥  990‰  ~12 used:32 [11]   source:dolphin3
      $9 #160 finesse              48.44°C 🥵  987‰  ~77 used:68 [76]   source:dolphin3
     $10 #336 spectaculaire        45.33°C 🥵  980‰   ~7 used:0  [6]    source:dolphin3
     $11 #213 érudition            42.51°C 🥵  969‰  ~71 used:27 [70]   source:dolphin3
     $19 #279 variété              36.08°C 😎  897‰  ~14 used:0  [13]   source:dolphin3
     $81 #180 délicatesse          23.54°C 🥶        ~84 used:0  [83]   source:dolphin3
    $296 #299 entrepreneur         -0.30°C 🧊       ~296 used:0  [295]  source:dolphin3

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #96 🥳 score:25 ⏱️ 0:01:38.840831

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. CLUNG attempts:6 score:6
2. SYNOD attempts:4 score:4
3. MELEE attempts:7 score:7
4. CLANG attempts:6 score:8
