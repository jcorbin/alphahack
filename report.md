# 2026-05-04

- 🔗 spaceword.org 🧩 2026-05-03 🏁 score 2173 ranked 5.4% 17/315 ⏱️ 0:04:58.965756
- 🔗 alfagok.diginaut.net 🧩 #548 🥳 36 ⏱️ 0:00:50.391651
- 🔗 alphaguess.com 🧩 #1015 🥳 28 ⏱️ 0:00:37.023961
- 🔗 dontwordle.com 🧩 #1441 🥳 6 ⏱️ 0:01:20.599936
- 🔗 dictionary.com hurdle 🧩 #1584 🥳 19 ⏱️ 0:03:07.771271
- 🔗 Quordle Classic 🧩 #1561 🥳 score:22 ⏱️ 0:01:36.827239
- 🔗 Octordle Classic 🧩 #1561 🥳 score:58 ⏱️ 0:03:52.427650
- 🔗 squareword.org 🧩 #1554 🥳 7 ⏱️ 0:02:31.593674
- 🔗 cemantle.certitudes.org 🧩 #1491 🥳 302 ⏱️ 0:04:57.858340
- 🔗 cemantix.certitudes.org 🧩 #1524 🥳 64 ⏱️ 0:00:40.320701

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
































































# [spaceword.org](spaceword.org) 🧩 2026-05-03 🏁 score 2173 ranked 5.4% 17/315 ⏱️ 0:04:58.965756

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 17/315

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ E L _ D E R I V E   
      _ M O Z O _ Y _ _ R   
      _ _ _ A C Q U I R E   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #548 🥳 36 ⏱️ 0:00:50.391651

🤔 36 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+2      [     2] -cijferig 
    @+199695 [199695] lijk      q0  ? ␅
    @+199695 [199695] lijk      q1  ? after
    @+223673 [223673] molens    q6  ? ␅
    @+223673 [223673] molens    q7  ? after
    @+229573 [229573] natuur    q12 ? ␅
    @+229573 [229573] natuur    q13 ? after
    @+231095 [231095] neig      q16 ? ␅
    @+231095 [231095] neig      q17 ? after
    @+231812 [231812] neuk      q18 ? ␅
    @+231812 [231812] neuk      q19 ? after
    @+232188 [232188] neven     q20 ? ␅
    @+232188 [232188] neven     q21 ? after
    @+232404 [232404] nieges    q28 ? ␅
    @+232404 [232404] nieges    q29 ? after
    @+232443 [232443] nier      q30 ? ␅
    @+232443 [232443] nier      q31 ? after
    @+232526 [232526] nies      q32 ? ␅
    @+232526 [232526] nies      q33 ? after
    @+232551 [232551] niet      q34 ? ␅
    @+232551 [232551] niet      q35 ? it
    @+232551 [232551] niet      done. it
    @+232617 [232617] nieuw     q14 ? ␅
    @+232617 [232617] nieuw     q15 ? before
    @+235665 [235665] odalisk   q10 ? ␅
    @+235665 [235665] odalisk   q11 ? before
    @+247663 [247663] op        q4  ? ␅
    @+247663 [247663] op        q5  ? before
    @+299447 [299447] schro     q2  ? ␅
    @+299447 [299447] schro     q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1015 🥳 28 ⏱️ 0:00:37.023961

🤔 28 attempts
📜 1 sessions

    @       [    0] aa     
    @+2     [    2] aahed  
    @+47380 [47380] dis    q2  ? ␅
    @+47380 [47380] dis    q3  ? after
    @+72798 [72798] gremmy q4  ? ␅
    @+72798 [72798] gremmy q5  ? after
    @+85502 [85502] ins    q6  ? ␅
    @+85502 [85502] ins    q7  ? after
    @+91846 [91846] knot   q8  ? ␅
    @+91846 [91846] knot   q9  ? after
    @+92136 [92136] krone  q16 ? ␅
    @+92136 [92136] krone  q17 ? after
    @+92280 [92280] kyars  q18 ? ␅
    @+92280 [92280] kyars  q19 ? after
    @+92312 [92312] la     q22 ? ␅
    @+92312 [92312] la     q23 ? after
    @+92319 [92319] lab    q24 ? ␅
    @+92319 [92319] lab    q25 ? after
    @+92327 [92327] label  q26 ? ␅
    @+92327 [92327] label  q27 ? it
    @+92327 [92327] label  done. it
    @+92345 [92345] labial q20 ? ␅
    @+92345 [92345] labial q21 ? before
    @+92423 [92423] lac    q14 ? ␅
    @+92423 [92423] lac    q15 ? before
    @+93266 [93266] lar    q12 ? ␅
    @+93266 [93266] lar    q13 ? before
    @+94943 [94943] lib    q10 ? ␅
    @+94943 [94943] lib    q11 ? before
    @+98216 [98216] mach   q0  ? ␅
    @+98216 [98216] mach   q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1441 🥳 6 ⏱️ 0:01:20.599936

📜 1 sessions
💰 score: 136

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:ETWEE n n n n n remain:5004
    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:2688
    ⬜⬜⬜⬜⬜ tried:OVOLO n n n n n remain:1010
    ⬜⬜⬜⬜⬜ tried:YUKKY n n n n n remain:271
    ⬜🟨⬜⬜⬜ tried:BANDA n m n n n remain:33
    ⬜⬜🟩⬜⬜ tried:PZAZZ n n Y n n remain:17

    Undos used: 2

      17 words remaining
    x 8 unused letters
    = 136 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1584 🥳 19 ⏱️ 0:03:07.771271

📜 1 sessions
💰 score: 9700

    4/6
    NOISE 🟨⬜⬜🟨🟨
    ETNAS 🟨⬜🟨⬜🟨
    SHEND 🟩⬜🟩🟩🟩
    SPEND 🟩🟩🟩🟩🟩
    4/6
    SPEND ⬜⬜🟨🟨⬜
    LONER ⬜⬜🟨🟩⬜
    MAVEN ⬜🟩⬜🟩🟩
    TAKEN 🟩🟩🟩🟩🟩
    5/6
    TAKEN 🟨⬜⬜⬜🟨
    COUNT ⬜⬜⬜🟩🟩
    FLINT ⬜⬜🟩🟩🟩
    PRINT ⬜⬜🟩🟩🟩
    STINT 🟩🟩🟩🟩🟩
    5/6
    STINT ⬜⬜⬜⬜⬜
    ROYAL ⬜⬜🟨⬜⬜
    HYPED ⬜🟨⬜⬜⬜
    MUCKY ⬜🟩🟨⬜🟩
    CUBBY 🟩🟩🟩🟩🟩
    Final 1/2
    IMAGE 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1561 🥳 score:22 ⏱️ 0:01:36.827239

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. IMBUE attempts:7 score:7
2. FIFTY attempts:4 score:4
3. STEEP attempts:6 score:6
4. PINTO attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1561 🥳 score:58 ⏱️ 0:03:52.427650

📜 1 sessions

Octordle Classic

1. CRIMP attempts:7 score:7
2. GUILE attempts:5 score:5
3. FIBER attempts:12 score:12
4. LOGIN attempts:4 score:4
5. CRATE attempts:6 score:6
6. GREED attempts:8 score:8
7. CORER attempts:10 score:13
8. NAIVE attempts:3 score:3

# [squareword.org](squareword.org) 🧩 #1554 🥳 7 ⏱️ 0:02:31.593674

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    L O A F S
    E X T R A
    V I R A L
    E D I C T
    L E A K Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1491 🥳 302 ⏱️ 0:04:57.858340

🤔 303 attempts
📜 1 sessions
🫧 15 chat sessions
⁉️ 77 chat prompts
🤖 77 dolphin3:latest replies
😱   1 🔥   3 🥵   6 😎  34 🥶 227 🧊  31

      $1 #303 librarian          100.00°C 🥳 1000‰ ~272 used:0  [271]  source:dolphin3
      $2 #152 library             62.30°C 😱  999‰   ~4 used:49 [3]    source:dolphin3
      $3 #291 archivist           58.74°C 🔥  998‰   ~1 used:0  [0]    source:dolphin3
      $4 #292 bibliographer       54.31°C 🔥  996‰   ~2 used:0  [1]    source:dolphin3
      $5 #297 curator             50.05°C 🔥  992‰   ~3 used:0  [2]    source:dolphin3
      $6 #300 historian           42.52°C 🥵  971‰   ~5 used:0  [4]    source:dolphin3
      $7 #154 yearbook            39.19°C 🥵  935‰  ~39 used:18 [38]   source:dolphin3
      $8 #143 literary            39.16°C 🥵  934‰   ~9 used:9  [8]    source:dolphin3
      $9 #190 scholarly           38.30°C 🥵  920‰   ~8 used:7  [7]    source:dolphin3
     $10 #298 editor              37.97°C 🥵  914‰   ~6 used:0  [5]    source:dolphin3
     $11 #222 bookbinding         37.65°C 🥵  906‰   ~7 used:5  [6]    source:dolphin3
     $12 #130 poetry              36.83°C 😎  888‰  ~42 used:4  [41]   source:dolphin3
     $46  #48 sewing              25.75°C 🥶        ~45 used:18 [44]   source:dolphin3
    $273  #77 threads             -0.03°C 🧊       ~273 used:0  [272]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1524 🥳 64 ⏱️ 0:00:40.320701

🤔 65 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 7 chat prompts
🤖 7 dolphin3:latest replies
😱  1 🥵  1 😎 13 🥶 36 🧊 13

     $1 #65 dépendant      100.00°C 🥳 1000‰ ~52 used:0 [51]  source:dolphin3
     $2 #42 dépendance      61.79°C 😱  999‰  ~1 used:1 [0]   source:dolphin3
     $3 #38 conséquence     33.96°C 🥵  941‰  ~2 used:0 [1]   source:dolphin3
     $4 #49 relation        30.37°C 😎  831‰  ~3 used:0 [2]   source:dolphin3
     $5 #51 régulation      27.17°C 😎  642‰  ~4 used:0 [3]   source:dolphin3
     $6 #47 perturbation    26.70°C 😎  591‰  ~5 used:0 [4]   source:dolphin3
     $7 #64 évolution       26.64°C 😎  587‰  ~6 used:0 [5]   source:dolphin3
     $8 #43 influence       26.38°C 😎  553‰  ~7 used:0 [6]   source:dolphin3
     $9 #35 interaction     25.86°C 😎  503‰  ~8 used:1 [7]   source:dolphin3
    $10 #48 processus       25.14°C 😎  403‰  ~9 used:0 [8]   source:dolphin3
    $11 #26 pollinisation   24.86°C 😎  359‰ ~14 used:2 [13]  source:dolphin3
    $12 #52 stabilité       24.58°C 😎  315‰ ~10 used:0 [9]   source:dolphin3
    $17 #20 croissance      22.21°C 🥶       ~17 used:2 [16]  source:dolphin3
    $53 #17 arbre           -1.66°C 🧊       ~53 used:0 [52]  source:dolphin3
