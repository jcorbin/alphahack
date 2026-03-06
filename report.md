# 2026-03-07

- 🔗 spaceword.org 🧩 2026-03-06 🏁 score 2164 ranked 60.5% 201/332 ⏱️ 3:17:13.612826
- 🔗 alfagok.diginaut.net 🧩 #490 🥳 38 ⏱️ 0:00:47.646335
- 🔗 alphaguess.com 🧩 #957 🥳 22 ⏱️ 0:00:23.406123
- 🔗 dontwordle.com 🧩 #1383 🥳 6 ⏱️ 0:01:10.495210
- 🔗 dictionary.com hurdle 🧩 #1526 🥳 16 ⏱️ 0:02:54.760252
- 🔗 Quordle Classic 🧩 #1503 🥳 score:22 ⏱️ 0:01:22.231232
- 🔗 Octordle Classic 🧩 #1503 🥳 score:62 ⏱️ 0:03:56.305759
- 🔗 squareword.org 🧩 #1496 🥳 7 ⏱️ 0:01:40.162839
- 🔗 cemantle.certitudes.org 🧩 #1433 🥳 116 ⏱️ 0:01:09.093902
- 🔗 cemantix.certitudes.org 🧩 #1466 🥳 115 ⏱️ 0:01:24.275915

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






# [spaceword.org](spaceword.org) 🧩 2026-03-06 🏁 score 2164 ranked 60.5% 201/332 ⏱️ 3:17:13.612826

📜 2 sessions
- tiles: 21/21
- score: 2164 bonus: +64
- rank: 201/332

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ A L _ _ _ _ _ T   
      _ _ C _ S E V E R E   
      _ B E A K _ _ _ _ E   
      _ _ _ Y A N Q U I _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #490 🥳 38 ⏱️ 0:00:47.646335

🤔 38 attempts
📜 1 sessions

    @        [     0] &-teken               
    @+199812 [199812] lijm                  q0  ? ␅
    @+199812 [199812] lijm                  q1  ? after
    @+299699 [299699] schub                 q2  ? ␅
    @+299699 [299699] schub                 q3  ? after
    @+349467 [349467] vakantie              q4  ? ␅
    @+349467 [349467] vakantie              q5  ? after
    @+374208 [374208] vrij                  q6  ? ␅
    @+374208 [374208] vrij                  q7  ? after
    @+374551 [374551] vrijmacht             q18 ? ␅
    @+374551 [374551] vrijmacht             q19 ? after
    @+374614 [374614] vrijst                q22 ? ␅
    @+374614 [374614] vrijst                q23 ? after
    @+374654 [374654] vrijt                 q24 ? ␅
    @+374654 [374654] vrijt                 q25 ? after
    @+374671 [374671] vrijwaar              q26 ? ␅
    @+374671 [374671] vrijwaar              q27 ? after
    @+374676 [374676] vrijwaring            q28 ? ␅
    @+374676 [374676] vrijwaring            q29 ? after
    @+374681 [374681] vrijwaringsclausules  q32 ? ␅
    @+374681 [374681] vrijwaringsclausules  q33 ? after
    @+374684 [374684] vrijwaringsverklaring q34 ? ␅
    @+374684 [374684] vrijwaringsverklaring q35 ? after
    @+374685 [374685] vrijwel               q36 ? ␅
    @+374685 [374685] vrijwel               q37 ? it
    @+374685 [374685] vrijwel               done. it
    @+374686 [374686] vrijwiel              q30 ? ␅
    @+374686 [374686] vrijwiel              q31 ? before
    @+374693 [374693] vrijwilligers         q20 ? ␅
    @+374693 [374693] vrijwilligers         q21 ? before
    @+374898 [374898] vrouwen               q17 ? before

# [alphaguess.com](alphaguess.com) 🧩 #957 🥳 22 ⏱️ 0:00:23.406123

🤔 22 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+23682 [23682] camp       q4  ? ␅
    @+23682 [23682] camp       q5  ? after
    @+35525 [35525] convention q6  ? ␅
    @+35525 [35525] convention q7  ? after
    @+35641 [35641] convo      q18 ? ␅
    @+35641 [35641] convo      q19 ? after
    @+35703 [35703] cook       q20 ? ␅
    @+35703 [35703] cook       q21 ? it
    @+35703 [35703] cook       done. it
    @+35779 [35779] coop       q16 ? ␅
    @+35779 [35779] coop       q17 ? before
    @+36091 [36091] cor        q14 ? ␅
    @+36091 [36091] cor        q15 ? before
    @+36726 [36726] cos        q12 ? ␅
    @+36726 [36726] cos        q13 ? before
    @+38184 [38184] crazy      q10 ? ␅
    @+38184 [38184] crazy      q11 ? before
    @+40841 [40841] da         q8  ? ␅
    @+40841 [40841] da         q9  ? before
    @+47381 [47381] dis        q2  ? ␅
    @+47381 [47381] dis        q3  ? before
    @+98218 [98218] mach       q0  ? ␅
    @+98218 [98218] mach       q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1383 🥳 6 ⏱️ 0:01:10.495210

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:POOPY n n n n n remain:6473
    ⬜⬜⬜⬜⬜ tried:SKEES n n n n n remain:1136
    ⬜⬜⬜⬜⬜ tried:DAGGA n n n n n remain:204
    ⬜⬜⬜⬜⬜ tried:CHUFF n n n n n remain:28
    🟨⬜⬜⬜⬜ tried:IMMIX m n n n n remain:7
    🟩⬜🟩🟩⬜ tried:BRITT Y n Y Y n remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1526 🥳 16 ⏱️ 0:02:54.760252

📜 1 sessions
💰 score: 10000

    4/6
    RATES 🟨⬜🟨⬜⬜
    TORIC 🟨⬜🟨🟨⬜
    FRITH 🟩🟩🟩🟩⬜
    FRITZ 🟩🟩🟩🟩🟩
    3/6
    FRITZ ⬜⬜⬜⬜⬜
    SALON ⬜🟨⬜🟩🟨
    ANNOY 🟩🟩🟩🟩🟩
    3/6
    ANNOY ⬜⬜⬜⬜🟩
    STUDY 🟩⬜⬜⬜🟩
    SPICY 🟩🟩🟩🟩🟩
    5/6
    SPICY ⬜⬜🟨⬜⬜
    AILED ⬜🟩⬜⬜⬜
    NITRO 🟩🟩🟨⬜⬜
    NIGHT 🟩🟩⬜🟨🟨
    NINTH 🟩🟩🟩🟩🟩
    Final 1/2
    ACTOR 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1503 🥳 score:22 ⏱️ 0:01:22.231232

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. AMBLE attempts:6 score:6
2. HOUSE attempts:5 score:5
3. PAINT attempts:4 score:4
4. AORTA attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1503 🥳 score:62 ⏱️ 0:03:56.305759

📜 1 sessions

Octordle Classic

1. MODEL attempts:5 score:5
2. POPPY attempts:12 score:12
3. SOGGY attempts:7 score:7
4. BOWEL attempts:4 score:4
5. STILL attempts:6 score:6
6. ANNUL attempts:8 score:8
7. GIVEN attempts:9 score:9
8. STUCK attempts:11 score:11

# [squareword.org](squareword.org) 🧩 #1496 🥳 7 ⏱️ 0:01:40.162839

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟩 🟨
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    R O V E R
    E X I L E
    D I O D E
    I D L E D
    D E A R S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1433 🥳 116 ⏱️ 0:01:09.093902

🤔 117 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 19 chat prompts
🤖 19 dolphin3:latest replies
🔥  2 🥵  2 😎 10 🥶 89 🧊 13

      $1 #117 memorial        100.00°C 🥳 1000‰ ~104 used:0 [103]  source:dolphin3
      $2 #115 monument         69.60°C 🔥  998‰   ~1 used:0 [0]    source:dolphin3
      $3 #116 cenotaph         60.37°C 🔥  995‰   ~2 used:0 [1]    source:dolphin3
      $4 #113 statue           50.85°C 🥵  983‰   ~3 used:0 [2]    source:dolphin3
      $5  #96 sculpture        41.88°C 🥵  954‰   ~4 used:7 [3]    source:dolphin3
      $6  #80 replica          33.12°C 😎  867‰  ~14 used:8 [13]   source:dolphin3
      $7  #71 likeness         28.49°C 😎  769‰  ~13 used:5 [12]   source:dolphin3
      $8  #24 portrait         26.64°C 😎  691‰  ~12 used:4 [11]   source:dolphin3
      $9  #49 donation         26.61°C 😎  688‰   ~9 used:2 [8]    source:dolphin3
     $10  #70 artwork          25.64°C 😎  631‰  ~10 used:2 [9]    source:dolphin3
     $11 #106 sculptural       23.81°C 😎  506‰   ~5 used:1 [4]    source:dolphin3
     $12 #103 marble           23.38°C 😎  469‰   ~6 used:0 [5]    source:dolphin3
     $16  #14 tattoo           19.66°C 🥶        ~15 used:5 [14]   source:dolphin3
    $105  #56 pricing          -0.42°C 🧊       ~105 used:0 [104]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1466 🥳 115 ⏱️ 0:01:24.275915

🤔 116 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 17 chat prompts
🤖 17 dolphin3:latest replies
🔥  4 🥵  7 😎 31 🥶 60 🧊 13

      $1 #116 installation     100.00°C 🥳 1000‰ ~103 used:0  [102]  source:dolphin3
      $2  #75 équipement        58.82°C 😱  999‰   ~1 used:7  [0]    source:dolphin3
      $3  #46 maintenance       57.34°C 🔥  998‰  ~10 used:13 [9]    source:dolphin3
      $4  #91 exploitation      53.71°C 🔥  996‰   ~2 used:2  [1]    source:dolphin3
      $5  #57 matériel          49.80°C 🔥  991‰   ~3 used:6  [2]    source:dolphin3
      $6  #95 configuration     45.35°C 🥵  986‰   ~4 used:0  [3]    source:dolphin3
      $7  #52 dépannage         41.72°C 🥵  964‰  ~11 used:5  [10]   source:dolphin3
      $8 #110 fourniture        41.03°C 🥵  960‰   ~5 used:0  [4]    source:dolphin3
      $9 #107 technique         39.52°C 🥵  941‰   ~6 used:0  [5]    source:dolphin3
     $10  #82 infrastructure    36.83°C 🥵  908‰   ~7 used:0  [6]    source:dolphin3
     $11  #65 surveillance      36.65°C 🥵  902‰   ~8 used:0  [7]    source:dolphin3
     $13  #73 technicien        36.01°C 😎  891‰  ~12 used:0  [11]   source:dolphin3
     $44  #83 planification     23.42°C 🥶        ~45 used:0  [44]   source:dolphin3
    $104 #113 non               -0.08°C 🧊       ~104 used:0  [103]  source:dolphin3
