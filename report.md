# 2026-06-24

- 🔗 spaceword.org 🧩 2026-06-23 🏁 score 2173 ranked 7.7% 24/310 ⏱️ 0:19:20.023202
- 🔗 alfagok.diginaut.net 🧩 #599 🥳 24 ⏱️ 0:00:36.493126
- 🔗 alphaguess.com 🧩 #1066 🥳 30 ⏱️ 0:00:40.839829
- 🔗 dontwordle.com 🧩 #1492 😳 6 ⏱️ 0:02:11.222811
- 🔗 dictionary.com hurdle 🧩 #1635 🥳 16 ⏱️ 0:03:25.270550
- 🔗 Quordle Classic 🧩 #1612 🥳 score:26 ⏱️ 0:02:34.609611
- 🔗 Octordle Classic 🧩 #1612 😦 score:69 ⏱️ 0:05:17.119370
- 🔗 squareword.org 🧩 #1605 🥳 8 ⏱️ 0:06:39.448062
- 🔗 cemantle.certitudes.org 🧩 #1542 🥳 212 ⏱️ 0:02:50.390164
- 🔗 cemantix.certitudes.org 🧩 #1575 🥳 65 ⏱️ 0:00:53.781468
- 🔗 Sedecordle Classic 🧩 #1592 🥳 score:44 ⏱️ 0:16:23.281098

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















# [spaceword.org](spaceword.org) 🧩 2026-06-23 🏁 score 2173 ranked 7.7% 24/310 ⏱️ 0:19:20.023202

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 24/310

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ G A L _ _ _   
      _ _ _ _ _ _ A _ _ _   
      _ _ _ _ T E W _ _ _   
      _ _ _ _ _ Q I _ _ _   
      _ _ _ _ _ U N _ _ _   
      _ _ _ _ Z A G _ _ _   
      _ _ _ _ _ T _ _ _ _   
      _ _ _ _ B O O _ _ _   
      _ _ _ _ I R E _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #599 🥳 24 ⏱️ 0:00:36.493126

🤔 24 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+199761 [199761] lijm       q0  ? ␅
    @+199761 [199761] lijm       q1  ? after
    @+299624 [299624] schub      q2  ? ␅
    @+299624 [299624] schub      q3  ? after
    @+311788 [311788] spier      q8  ? ␅
    @+311788 [311788] spier      q9  ? after
    @+317981 [317981] stem       q10 ? ␅
    @+317981 [317981] stem       q11 ? after
    @+318337 [318337] steno      q18 ? ␅
    @+318337 [318337] steno      q19 ? after
    @+318412 [318412] ster       q22 ? ␅
    @+318412 [318412] ster       q23 ? it
    @+318412 [318412] ster       done. it
    @+318494 [318494] sterf      q20 ? ␅
    @+318494 [318494] sterf      q21 ? before
    @+318719 [318719] sterven    q16 ? ␅
    @+318719 [318719] sterven    q17 ? before
    @+319465 [319465] stimulatie q14 ? ␅
    @+319465 [319465] stimulatie q15 ? before
    @+320955 [320955] straat     q12 ? ␅
    @+320955 [320955] straat     q13 ? before
    @+324184 [324184] sub        q6  ? ␅
    @+324184 [324184] sub        q7  ? before
    @+349386 [349386] vakantie   q4  ? ␅
    @+349386 [349386] vakantie   q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1066 🥳 30 ⏱️ 0:00:40.839829

🤔 30 attempts
📜 1 sessions

    @       [    0] aa            
    @+47380 [47380] dis           q2  ? ␅
    @+47380 [47380] dis           q3  ? after
    @+49427 [49427] do            q10 ? ␅
    @+49427 [49427] do            q11 ? after
    @+49457 [49457] doc           q20 ? ␅
    @+49457 [49457] doc           q21 ? after
    @+49515 [49515] document      q22 ? ␅
    @+49515 [49515] document      q23 ? after
    @+49555 [49555] dodecaphonies q24 ? ␅
    @+49555 [49555] dodecaphonies q25 ? after
    @+49559 [49559] dodge         q28 ? ␅
    @+49559 [49559] dodge         q29 ? it
    @+49559 [49559] dodge         done. it
    @+49576 [49576] dodo          q26 ? ␅
    @+49576 [49576] dodo          q27 ? before
    @+49595 [49595] dog           q18 ? ␅
    @+49595 [49595] dog           q19 ? before
    @+49848 [49848] dom           q16 ? ␅
    @+49848 [49848] dom           q17 ? before
    @+50404 [50404] dove          q14 ? ␅
    @+50404 [50404] dove          q15 ? before
    @+51401 [51401] drunk         q12 ? ␅
    @+51401 [51401] drunk         q13 ? before
    @+53396 [53396] el            q8  ? ␅
    @+53396 [53396] el            q9  ? before
    @+60081 [60081] face          q6  ? ␅
    @+60081 [60081] face          q7  ? before
    @+72797 [72797] gremolata     q4  ? ␅
    @+72797 [72797] gremolata     q5  ? before
    @+98214 [98214] mach          q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1492 😳 6 ⏱️ 0:02:11.222811

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:LEVEL n n n n n remain:5302
    ⬜⬜⬜⬜⬜ tried:AYAYA n n n n n remain:2091
    ⬜⬜⬜⬜⬜ tried:SCUZZ n n n n n remain:307
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:118
    ⬜⬜🟩⬜⬜ tried:BRING n n Y n n remain:2
    🟩🟩🟩🟩🟩 tried:IDIOM Y Y Y Y Y remain:0

    Undos used: 3

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1635 🥳 16 ⏱️ 0:03:25.270550

📜 1 sessions
💰 score: 10000

    3/6
    IDEAS ⬜⬜🟨🟨⬜
    CRATE ⬜🟨🟩⬜🟩
    FLARE 🟩🟩🟩🟩🟩
    3/6
    FLARE ⬜⬜🟨🟩🟨
    AVERT 🟨⬜🟩🟩⬜
    OPERA 🟩🟩🟩🟩🟩
    5/6
    OPERA ⬜⬜🟨⬜⬜
    SIDHE ⬜⬜⬜⬜🟨
    MELTY ⬜🟩🟨⬜⬜
    BEVEL 🟩🟩⬜🟩🟩
    BEZEL 🟩🟩🟩🟩🟩
    3/6
    BEZEL ⬜⬜🟩⬜⬜
    SIZAR ⬜🟩🟩🟨⬜
    PIZZA 🟩🟩🟩🟩🟩
    Final 2/2
    SALIC ⬜🟨🟩🟨⬜
    INLAY 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1612 🥳 score:26 ⏱️ 0:02:34.609611

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SOBER attempts:9 score:9
2. ECLAT attempts:3 score:3
3. GOOSE attempts:8 score:8
4. NINNY attempts:6 score:6

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1612 😦 score:69 ⏱️ 0:05:17.119370

📜 1 sessions

Octordle Classic

1. ROWER attempts:12 score:12
2. CARRY attempts:13 score:13
3. SPLAT attempts:4 score:4
4. SLEPT attempts:5 score:5
5. SPREE attempts:8 score:8
6. REPAY attempts:6 score:6
7. CA_TE ~S -BDGILMNOPRVWY attempts:13 score:-1
8. SPITE attempts:7 score:7

# [squareword.org](squareword.org) 🧩 #1605 🥳 8 ⏱️ 0:06:39.448062

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟨 🟨 🟨 🟨
    🟩 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P S A L M
    A T R I A
    R I G O R
    A L O N G
    S E N S E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1542 🥳 212 ⏱️ 0:02:50.390164

🤔 213 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 47 chat prompts
🤖 47 dolphin3:latest replies
🔥   2 🥵  10 😎  38 🥶 159 🧊   3

      $1 #213 desirable       100.00°C 🥳 1000‰ ~210 used:0  [209]  source:dolphin3
      $2 #188 advantageous     64.31°C 🔥  998‰   ~2 used:10 [1]    source:dolphin3
      $3 #212 preferable       55.50°C 🔥  996‰   ~1 used:2  [0]    source:dolphin3
      $4 #191 beneficial       51.09°C 🥵  989‰   ~6 used:3  [5]    source:dolphin3
      $5 #147 suitable         49.15°C 🥵  986‰  ~49 used:17 [48]   source:dolphin3
      $6  #57 essential        44.39°C 🥵  972‰  ~50 used:19 [49]   source:dolphin3
      $7 #194 expedient        44.32°C 🥵  971‰   ~3 used:1  [2]    source:dolphin3
      $8 #189 conducive        43.73°C 🥵  968‰   ~5 used:2  [4]    source:dolphin3
      $9 #124 appropriate      40.42°C 🥵  935‰  ~10 used:7  [9]    source:dolphin3
     $10 #162 apt              40.28°C 🥵  932‰   ~7 used:6  [6]    source:dolphin3
     $11 #208 useful           40.27°C 🥵  931‰   ~4 used:0  [3]    source:dolphin3
     $14 #108 imperative       37.65°C 😎  888‰  ~11 used:0  [10]   source:dolphin3
     $52 #136 competent        26.50°C 🥶        ~60 used:0  [59]   source:dolphin3
    $211   #8 telescope        -0.86°C 🧊       ~211 used:0  [210]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1575 🥳 65 ⏱️ 0:00:53.781468

🤔 66 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 13 chat prompts
🤖 13 dolphin3:latest replies
🥵  5 😎  9 🥶 42 🧊  9

     $1 #66 bagage        100.00°C 🥳 1000‰ ~57 used:0 [56]  source:dolphin3
     $2 #43 avion          36.94°C 🥵  988‰  ~4 used:5 [3]   source:dolphin3
     $3 #46 vol            36.23°C 🥵  986‰  ~5 used:5 [4]   source:dolphin3
     $4 #63 aéroport       34.76°C 🥵  978‰  ~2 used:2 [1]   source:dolphin3
     $5 #64 arrivée        32.74°C 🥵  964‰  ~1 used:0 [0]   source:dolphin3
     $6 #42 transport      27.32°C 🥵  900‰  ~3 used:2 [2]   source:dolphin3
     $7 #47 destination    25.50°C 😎  860‰  ~6 used:0 [5]   source:dolphin3
     $8 #37 séjour         23.47°C 😎  777‰ ~13 used:2 [12]  source:dolphin3
     $9 #48 décollage      22.65°C 😎  743‰  ~7 used:0 [6]   source:dolphin3
    $10 #51 réservation    22.62°C 😎  741‰  ~8 used:0 [7]   source:dolphin3
    $11 #16 gare           21.88°C 😎  707‰ ~14 used:3 [13]  source:dolphin3
    $12 #29 compagnie      20.51°C 😎  611‰  ~9 used:1 [8]   source:dolphin3
    $16 #58 porte          15.95°C 🥶       ~18 used:0 [17]  source:dolphin3
    $58 #17 animaux        -0.32°C 🧊       ~58 used:0 [57]  source:dolphin3

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1592 🥳 score:44 ⏱️ 0:16:23.281098

📜 1 sessions

Sedecordle Classic sedecordle.com

1. LEVER attempts:14 score:1
2. NERVE attempts:13 score:4
3. RENAL attempts:3 score:0
4. PUPAL attempts:10 score:3
5. SISSY attempts:12 score:1
6. PUFFY attempts:15 score:2
7. JUMPY attempts:9 score:0
8. COMIC attempts:16 score:9
9. SPENT attempts:11 score:1
10. WORLD attempts:6 score:1
11. SLUNG attempts:17 score:1
12. STAID attempts:8 score:7
13. ALLAY attempts:5 score:0
14. EJECT attempts:7 score:5
15. SHANK attempts:18 score:1
16. MOURN attempts:4 score:8
