# 2026-05-05

- 🔗 spaceword.org 🧩 2026-05-04 🏁 score 2173 ranked 11.9% 39/328 ⏱️ 0:28:58.754429
- 🔗 alfagok.diginaut.net 🧩 #549 🥳 38 ⏱️ 0:00:45.631643
- 🔗 alphaguess.com 🧩 #1016 🥳 20 ⏱️ 0:00:24.503440
- 🔗 dontwordle.com 🧩 #1442 🥳 6 ⏱️ 0:01:23.072433
- 🔗 dictionary.com hurdle 🧩 #1585 🥳 19 ⏱️ 0:03:24.217950
- 🔗 Quordle Classic 🧩 #1562 🥳 score:23 ⏱️ 0:01:31.491842
- 🔗 Octordle Classic 🧩 #1562 🥳 score:59 ⏱️ 0:03:10.473601
- 🔗 squareword.org 🧩 #1555 🥳 7 ⏱️ 0:01:52.816482
- 🔗 cemantle.certitudes.org 🧩 #1492 🥳 323 ⏱️ 0:03:46.428578
- 🔗 cemantix.certitudes.org 🧩 #1525 🥳 170 ⏱️ 0:04:10.687664

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

































































# [spaceword.org](spaceword.org) 🧩 2026-05-04 🏁 score 2173 ranked 11.9% 39/328 ⏱️ 0:28:58.754429

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 39/328

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ M _ J _ T E G U A   
      _ O X E Y E _ A T _   
      _ D _ T O W N E E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #549 🥳 38 ⏱️ 0:00:45.631643

🤔 38 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+199695 [199695] lijk         q0  ? ␅
    @+199695 [199695] lijk         q1  ? after
    @+223673 [223673] molens       q6  ? ␅
    @+223673 [223673] molens       q7  ? after
    @+235668 [235668] odalisk      q10 ? ␅
    @+235668 [235668] odalisk      q11 ? after
    @+238724 [238724] on           q12 ? ␅
    @+238724 [238724] on           q13 ? after
    @+243194 [243194] onroerend    q14 ? ␅
    @+243194 [243194] onroerend    q15 ? after
    @+243354 [243354] ont          q18 ? ␅
    @+243354 [243354] ont          q19 ? after
    @+244374 [244374] ontraad      q20 ? ␅
    @+244374 [244374] ontraad      q21 ? after
    @+244631 [244631] ontsluier    q24 ? ␅
    @+244631 [244631] ontsluier    q25 ? after
    @+244673 [244673] ontsnap      q28 ? ␅
    @+244673 [244673] ontsnap      q29 ? after
    @+244674 [244674] ontsnappen   q36 ? ␅
    @+244674 [244674] ontsnappen   q37 ? it
    @+244674 [244674] ontsnappen   done. it
    @+244675 [244675] ontsnappende q34 ? ␅
    @+244675 [244675] ontsnappende q35 ? before
    @+244676 [244676] ontsnapping  q32 ? ␅
    @+244676 [244676] ontsnapping  q33 ? before
    @+244702 [244702] ontspan      q30 ? ␅
    @+244702 [244702] ontspan      q31 ? before
    @+244759 [244759] ontspring    q26 ? ␅
    @+244759 [244759] ontspring    q27 ? before
    @+244892 [244892] onttakeld    q23 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1016 🥳 20 ⏱️ 0:00:24.503440

🤔 20 attempts
📜 1 sessions

    @       [    0] aa          
    @+1     [    1] aah         
    @+2     [    2] aahed       
    @+3     [    3] aahing      
    @+11763 [11763] back        q6  ? ␅
    @+11763 [11763] back        q7  ? after
    @+17714 [17714] blind       q8  ? ␅
    @+17714 [17714] blind       q9  ? after
    @+20686 [20686] brill       q10 ? ␅
    @+20686 [20686] brill       q11 ? after
    @+22026 [22026] bur         q12 ? ␅
    @+22026 [22026] bur         q13 ? after
    @+22854 [22854] cachalot    q14 ? ␅
    @+22854 [22854] cachalot    q15 ? after
    @+23048 [23048] cage        q18 ? ␅
    @+23048 [23048] cage        q19 ? it
    @+23048 [23048] cage        done. it
    @+23266 [23266] calculation q16 ? ␅
    @+23266 [23266] calculation q17 ? before
    @+23681 [23681] camp        q4  ? ␅
    @+23681 [23681] camp        q5  ? before
    @+47380 [47380] dis         q2  ? ␅
    @+47380 [47380] dis         q3  ? before
    @+98216 [98216] mach        q0  ? ␅
    @+98216 [98216] mach        q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1442 🥳 6 ⏱️ 0:01:23.072433

📜 1 sessions
💰 score: 10

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:PZAZZ n n n n n remain:6291
    ⬜⬜⬜⬜⬜ tried:TITIS n n n n n remain:1519
    ⬜⬜⬜⬜⬜ tried:BOFFO n n n n n remain:503
    ⬜⬜⬜⬜🟩 tried:XYLYL n n n n Y remain:20
    ⬜🟩⬜⬜🟩 tried:GRRRL n Y n n Y remain:2
    🟩🟩⬜🟩🟩 tried:CREEL Y Y n Y Y remain:1

    Undos used: 3

      1 words remaining
    x 10 unused letters
    = 10 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1585 🥳 19 ⏱️ 0:03:24.217950

📜 1 sessions
💰 score: 9700

    5/6
    STOAE ⬜⬜🟨⬜⬜
    INCOG ⬜🟨⬜🟨⬜
    YOURN ⬜🟩🟩⬜🟨
    BOUND ⬜🟩🟩🟩🟩
    POUND 🟩🟩🟩🟩🟩
    4/6
    POUND ⬜⬜⬜⬜⬜
    RAISE ⬜⬜🟨🟩⬜
    BITSY ⬜🟩⬜🟩🟩
    MISSY 🟩🟩🟩🟩🟩
    4/6
    MISSY ⬜🟨⬜⬜⬜
    ELAIN ⬜⬜⬜🟨⬜
    BRICK ⬜🟨🟩⬜🟩
    QUIRK 🟩🟩🟩🟩🟩
    5/6
    QUIRK ⬜⬜⬜⬜⬜
    PSOAE ⬜⬜⬜⬜🟨
    WYLED ⬜⬜⬜🟩⬜
    BEGET ⬜🟩⬜🟩🟩
    TENET 🟩🟩🟩🟩🟩
    Final 1/2
    TEARY 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1562 🥳 score:23 ⏱️ 0:01:31.491842

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. SNEER attempts:4 score:4
2. NEVER attempts:6 score:6
3. RAMEN attempts:5 score:5
4. TODDY attempts:8 score:8

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1562 🥳 score:59 ⏱️ 0:03:10.473601

📜 1 sessions

Octordle Classic

1. HOUND attempts:9 score:9
2. STORE attempts:3 score:3
3. TORSO attempts:2 score:2
4. PITHY attempts:11 score:11
5. ACUTE attempts:12 score:12
6. LADEN attempts:5 score:5
7. BESET attempts:7 score:7
8. HYENA attempts:10 score:10

# [squareword.org](squareword.org) 🧩 #1555 🥳 7 ⏱️ 0:01:52.816482

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟨 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P A R E
    C O L O N
    A L O U D
    L I E G E
    D O S E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1492 🥳 323 ⏱️ 0:03:46.428578

🤔 324 attempts
📜 1 sessions
🫧 14 chat sessions
⁉️ 65 chat prompts
🤖 65 dolphin3:latest replies
🔥   2 🥵   5 😎  24 🥶 269 🧊  23

      $1 #324 technician         100.00°C 🥳 1000‰ ~301 used:0  [300]  source:dolphin3
      $2 #317 engineer            60.22°C 🔥  996‰   ~1 used:5  [0]    source:dolphin3
      $3 #261 welder              54.29°C 🔥  993‰   ~3 used:25 [2]    source:dolphin3
      $4  #66 engineering         39.53°C 🥵  943‰  ~30 used:52 [29]   source:dolphin3
      $5 #319 manager             39.50°C 🥵  942‰   ~2 used:0  [1]    source:dolphin3
      $6 #231 welding             38.14°C 🥵  919‰  ~11 used:12 [10]   source:dolphin3
      $7  #68 equipment           37.87°C 🥵  915‰  ~25 used:30 [24]   source:dolphin3
      $8 #129 computer            37.33°C 🥵  906‰  ~12 used:20 [11]   source:dolphin3
      $9 #173 machine             35.93°C 😎  875‰  ~26 used:3  [25]   source:dolphin3
     $10  #60 calibration         35.49°C 😎  863‰  ~31 used:6  [30]   source:dolphin3
     $11  #91 electrical          34.42°C 😎  839‰  ~27 used:3  [26]   source:dolphin3
     $12  #71 maintenance         31.85°C 😎  768‰  ~28 used:3  [27]   source:dolphin3
     $33  #36 training            22.71°C 🥶        ~34 used:2  [33]   source:dolphin3
    $302 #268 forge               -0.37°C 🧊       ~302 used:0  [301]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1525 🥳 170 ⏱️ 0:04:10.687664

🤔 171 attempts
📜 1 sessions
🫧 12 chat sessions
⁉️ 60 chat prompts
🤖 60 dolphin3:latest replies
🔥   1 🥵   9 😎  38 🥶 109 🧊  13

      $1 #171 litre            100.00°C 🥳 1000‰ ~158 used:0  [157]  source:dolphin3
      $2 #170 gallon            49.62°C 🔥  994‰   ~1 used:2  [0]    source:dolphin3
      $3  #51 gasoil            45.57°C 🥵  986‰  ~48 used:53 [47]   source:dolphin3
      $4  #22 carburant         43.62°C 🥵  981‰  ~47 used:35 [46]   source:dolphin3
      $5  #85 cylindrée         43.24°C 🥵  978‰  ~44 used:17 [43]   source:dolphin3
      $6 #133 fuel              39.96°C 🥵  964‰  ~39 used:11 [38]   source:dolphin3
      $7 #159 kilomètre         39.87°C 🥵  963‰   ~2 used:4  [1]    source:dolphin3
      $8  #27 mazout            37.50°C 🥵  945‰  ~40 used:11 [39]   source:dolphin3
      $9 #121 aérateur          36.60°C 🥵  934‰  ~41 used:11 [40]   source:dolphin3
     $10  #40 essence           36.19°C 🥵  929‰  ~42 used:11 [41]   source:dolphin3
     $11  #39 diesel            35.89°C 🥵  923‰  ~43 used:11 [42]   source:dolphin3
     $12  #96 débit             34.61°C 😎  899‰  ~45 used:2  [44]   source:dolphin3
     $50  #84 composteur        23.81°C 🥶        ~51 used:0  [50]   source:dolphin3
    $159 #164 réactivité        -0.51°C 🧊       ~159 used:0  [158]  source:dolphin3
