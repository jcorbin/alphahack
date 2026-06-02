# 2026-06-03

- 🔗 spaceword.org 🧩 2026-06-02 🏁 score 2173 ranked 6.9% 24/350 ⏱️ 8:46:49.380960
- 🔗 alfagok.diginaut.net 🧩 #578 🥳 26 ⏱️ 0:00:33.238998
- 🔗 alphaguess.com 🧩 #1045 🥳 30 ⏱️ 0:00:41.399473
- 🔗 dontwordle.com 🧩 #1471 🤷 6 ⏱️ 0:01:41.791794
- 🔗 dictionary.com hurdle 🧩 #1614 😦 11 ⏱️ 0:01:38.173650
- 🔗 Quordle Classic 🧩 #1591 🥳 score:23 ⏱️ 0:01:20.528217
- 🔗 Octordle Classic 🧩 #1591 🥳 score:61 ⏱️ 0:03:54.801561
- 🔗 cemantle.certitudes.org 🧩 #1521 🥳 181 ⏱️ 0:01:25.421530
- 🔗 cemantix.certitudes.org 🧩 #1554 🥳 69 ⏱️ 0:00:33.929560
- 🔗 squareword.org 🧩 #1584 🥳 8 ⏱️ 0:03:42.297494

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
























































































# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1585 😦 score:32 ⏱️ 0:02:33.513959

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. GRAPE attempts:8 score:8
2. VALUE attempts:9 score:9
3. YEARN attempts:6 score:6
4. IN_ER -ACDGHLMPSTUVWYZ attempts:9 score:-1







# [spaceword.org](spaceword.org) 🧩 2026-06-02 🏁 score 2173 ranked 6.9% 24/350 ⏱️ 8:46:49.380960

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 24/350

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ R E L O O K I N G   
      _ A _ A N _ I _ _ U   
      _ M Y X O I D _ _ V   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #578 🥳 26 ⏱️ 0:00:33.238998

🤔 26 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199689 [199689] lijk      q0  ? ␅
    @+199689 [199689] lijk      q1  ? after
    @+199689 [199689] lijk      q2  ? ␅
    @+199689 [199689] lijk      q3  ? after
    @+299441 [299441] schro     q4  ? ␅
    @+299441 [299441] schro     q5  ? after
    @+349419 [349419] vakantie  q6  ? ␅
    @+349419 [349419] vakantie  q7  ? after
    @+374159 [374159] vrij      q8  ? ␅
    @+374159 [374159] vrij      q9  ? after
    @+386696 [386696] wind      q10 ? ␅
    @+386696 [386696] wind      q11 ? after
    @+389905 [389905] wrik      q14 ? ␅
    @+389905 [389905] wrik      q15 ? after
    @+390572 [390572] zaad      q18 ? ␅
    @+390572 [390572] zaad      q19 ? after
    @+390718 [390718] zaai      q22 ? ␅
    @+390718 [390718] zaai      q23 ? after
    @+390795 [390795] zaal      q24 ? ␅
    @+390795 [390795] zaal      q25 ? it
    @+390795 [390795] zaal      done. it
    @+390923 [390923] zadel     q20 ? ␅
    @+390923 [390923] zadel     q21 ? before
    @+391327 [391327] zand      q16 ? ␅
    @+391327 [391327] zand      q17 ? before
    @+393113 [393113] zelfmoord q12 ? ␅
    @+393113 [393113] zelfmoord q13 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1045 🥳 30 ⏱️ 0:00:41.399473

🤔 30 attempts
📜 1 sessions

    @       [    0] aa       
    @+47380 [47380] dis      q2  ? ␅
    @+47380 [47380] dis      q3  ? after
    @+72798 [72798] gremmy   q4  ? ␅
    @+72798 [72798] gremmy   q5  ? after
    @+85502 [85502] ins      q6  ? ␅
    @+85502 [85502] ins      q7  ? after
    @+91846 [91846] knot     q8  ? ␅
    @+91846 [91846] knot     q9  ? after
    @+93266 [93266] lar      q12 ? ␅
    @+93266 [93266] lar      q13 ? after
    @+93558 [93558] lati     q16 ? ␅
    @+93558 [93558] lati     q17 ? after
    @+93712 [93712] lava     q18 ? ␅
    @+93712 [93712] lava     q19 ? after
    @+93766 [93766] law      q20 ? ␅
    @+93766 [93766] law      q21 ? after
    @+93829 [93829] lay      q22 ? ␅
    @+93829 [93829] lay      q23 ? after
    @+93863 [93863] lazar    q24 ? ␅
    @+93863 [93863] lazar    q25 ? after
    @+93879 [93879] laziness q26 ? ␅
    @+93879 [93879] laziness q27 ? after
    @+93888 [93888] lazy     q28 ? ␅
    @+93888 [93888] lazy     q29 ? it
    @+93888 [93888] lazy     done. it
    @+93894 [93894] lea      q14 ? ␅
    @+93894 [93894] lea      q15 ? before
    @+94943 [94943] lib      q10 ? ␅
    @+94943 [94943] lib      q11 ? before
    @+98216 [98216] mach     q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1471 🤷 6 ⏱️ 0:01:41.791794

📜 1 sessions
💰 score: 0

ELIMINATED
> Well technically I didn't Wordle!

    ⬜⬜⬜⬜⬜ tried:EBBED n n n n n remain:5399
    ⬜⬜⬜⬜⬜ tried:SHAHS n n n n n remain:877
    ⬜⬜⬜⬜⬜ tried:LININ n n n n n remain:197
    ⬜⬜🟨⬜⬜ tried:PYGMY n n m n n remain:7
    🟩🟩🟨⬜⬜ tried:GRUFF Y Y m n n remain:1
    ⬛⬛⬛⬛⬛ tried:????? remain:0

    Undos used: 5

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1614 😦 11 ⏱️ 0:01:38.173650

📜 2 sessions
💰 score: 1180

    5/6
    RACES ⬜⬜⬜🟨⬜
    ELOIN 🟨⬜🟩⬜⬜
    QUOTE ⬜⬜🟩⬜🟩
    GEODE ⬜⬜🟩⬜🟩
    BOOZE 🟩🟩🟩🟩🟩
    6/6
    ????? ⬜⬜⬜⬜⬜
    ????? ⬜🟨⬜🟨⬜
    ????? ⬜🟨🟨🟨⬜
    ????? ⬜🟩🟩🟩🟩
    ????? ⬜🟩🟩🟩🟩
    ????? ⬜🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1591 🥳 score:23 ⏱️ 0:01:20.528217

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. MOODY attempts:8 score:8
2. JEWEL attempts:5 score:5
3. BLEAT attempts:7 score:7
4. SOAPY attempts:3 score:3

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1591 🥳 score:61 ⏱️ 0:03:54.801561

📜 1 sessions

Octordle Classic

1. POUCH attempts:9 score:9
2. FLUME attempts:11 score:11
3. ANGER attempts:8 score:8
4. TEACH attempts:7 score:7
5. MURAL attempts:12 score:12
6. ACTOR attempts:3 score:3
7. GUARD attempts:5 score:5
8. DEBIT attempts:6 score:6

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1521 🥳 181 ⏱️ 0:01:25.421530

🤔 182 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 25 chat prompts
🤖 25 dolphin3:latest replies
🥵   6 😎  27 🥶 130 🧊  18

      $1 #182 pipeline        100.00°C 🥳 1000‰ ~164 used:0  [163]  source:dolphin3
      $2  #44 terminal         36.12°C 🥵  983‰  ~29 used:20 [28]   source:dolphin3
      $3 #133 transmission     35.94°C 🥵  981‰   ~4 used:8  [3]    source:dolphin3
      $4 #146 infrastructure   35.58°C 🥵  978‰   ~3 used:6  [2]    source:dolphin3
      $5 #179 highway          30.40°C 🥵  938‰   ~1 used:0  [0]    source:dolphin3
      $6 #151 conduit          29.47°C 🥵  922‰   ~2 used:1  [1]    source:dolphin3
      $7  #63 line             28.93°C 🥵  910‰  ~28 used:12 [27]   source:dolphin3
      $8  #33 vessel           27.98°C 😎  890‰  ~33 used:5  [32]   source:dolphin3
      $9  #31 port             27.59°C 😎  878‰  ~30 used:2  [29]   source:dolphin3
     $10 #144 distribution     27.55°C 😎  875‰   ~5 used:0  [4]    source:dolphin3
     $11  #91 stream           26.48°C 😎  847‰  ~31 used:2  [30]   source:dolphin3
     $12 #178 flow             26.15°C 😎  828‰   ~6 used:0  [5]    source:dolphin3
     $35  #37 dock             17.50°C 🥶        ~34 used:0  [33]   source:dolphin3
    $165  #49 handling         -0.09°C 🧊       ~165 used:0  [164]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1554 🥳 69 ⏱️ 0:00:33.929560

🤔 70 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 8 chat prompts
🤖 8 dolphin3:latest replies
🔥  2 🥵  2 😎 20 🥶 40 🧊  5

     $1 #70 pompe          100.00°C 🥳 1000‰ ~65 used:0 [64]  source:dolphin3
     $2 #54 manomètre       47.94°C 🔥  995‰  ~2 used:2 [1]   source:dolphin3
     $3 #50 injecteur       47.15°C 🔥  992‰  ~1 used:1 [0]   source:dolphin3
     $4 #31 carburateur     40.42°C 🥵  974‰  ~4 used:2 [3]   source:dolphin3
     $5 #57 tuyau           38.19°C 🥵  958‰  ~3 used:0 [2]   source:dolphin3
     $6 #39 adoucisseur     33.87°C 😎  873‰  ~5 used:0 [4]   source:dolphin3
     $7 #67 injection       33.87°C 😎  872‰  ~6 used:0 [5]   source:dolphin3
     $8 #48 filtre          33.05°C 😎  853‰  ~7 used:0 [6]   source:dolphin3
     $9 #33 essence         31.40°C 😎  818‰  ~8 used:1 [7]   source:dolphin3
    $10 #27 alternateur     29.96°C 😎  746‰  ~9 used:1 [8]   source:dolphin3
    $11 #45 culasse         29.85°C 😎  739‰ ~10 used:0 [9]   source:dolphin3
    $12 #68 liquide         28.31°C 😎  670‰ ~11 used:0 [10]  source:dolphin3
    $26  #9 voiture         21.49°C 🥶       ~25 used:4 [24]  source:dolphin3
    $66  #8 ville           -1.59°C 🧊       ~66 used:0 [65]  source:dolphin3

# [squareword.org](squareword.org) 🧩 #1584 🥳 8 ⏱️ 0:03:42.297494

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P I F F
    M U R A L
    A P A C E
    R A T E S
    T E E T H
