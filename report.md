# 2026-01-24

- 🔗 spaceword.org 🧩 2026-01-23 🏁 score 2173 ranked 7.1% 23/325 ⏱️ 1:10:48.395443
- 🔗 alfagok.diginaut.net 🧩 #448 🥳 18 ⏱️ 0:00:53.998741
- 🔗 alphaguess.com 🧩 #915 🥳 14 ⏱️ 0:00:34.487005
- 🔗 dontwordle.com 🧩 #1341 🥳 6 ⏱️ 0:04:04.121080
- 🔗 dictionary.com hurdle 🧩 #1484 🥳 18 ⏱️ 0:03:41.407951
- 🔗 Quordle Classic 🧩 #1461 🥳 score:22 ⏱️ 0:02:06.830428
- 🔗 Octordle Classic 🧩 #1461 🥳 score:66 ⏱️ 0:06:57.105085
- 🔗 squareword.org 🧩 #1454 🥳 7 ⏱️ 0:02:31.151433
- 🔗 cemantle.certitudes.org 🧩 #1391 🥳 29 ⏱️ 0:00:59.162510
- 🔗 cemantix.certitudes.org 🧩 #1424 🥳 155 ⏱️ 0:03:31.318963
- 🔗 Quordle Rescue 🧩 #75 🥳 score:25 ⏱️ 0:01:45.919516
- 🔗 Octordle Rescue 🧩 #1461 🥳 score:8 ⏱️ 0:04:14.299975

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









# [spaceword.org](spaceword.org) 🧩 2026-01-23 🏁 score 2173 ranked 7.1% 23/325 ⏱️ 1:10:48.395443

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 23/325

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ G _ J _ O R _ O F   
      _ I _ A E R A D I O   
      _ F A W N E D _ _ X   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #448 🥳 18 ⏱️ 0:00:53.998741

🤔 18 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+1      [     1] &-tekens     
    @+2      [     2] -cijferig    
    @+3      [     3] -e-mail      
    @+199833 [199833] lijm         q0  ? after
    @+299738 [299738] schub        q1  ? after
    @+324308 [324308] sub          q3  ? after
    @+330491 [330491] televisie    q5  ? after
    @+331886 [331886] terug        q7  ? after
    @+332257 [332257] terugleveren q9  ? after
    @+332435 [332435] terugval     q10 ? after
    @+332532 [332532] terugwerpt   q11 ? after
    @+332576 [332576] terugzie     q12 ? after
    @+332588 [332588] terwijl      q17 ? it
    @+332588 [332588] terwijl      done. it
    @+332596 [332596] terzet       q13 ? before
    @+332625 [332625] test         q8  ? before
    @+333693 [333693] these        q6  ? before
    @+336905 [336905] toetsing     q4  ? before
    @+349512 [349512] vakantie     q2  ? before

# [alphaguess.com](alphaguess.com) 🧩 #915 🥳 14 ⏱️ 0:00:34.487005

🤔 14 attempts
📜 1 sessions

    @        [     0] aa       
    @+1      [     1] aah      
    @+2      [     2] aahed    
    @+3      [     3] aahing   
    @+98220  [ 98220] mach     q0  ? after
    @+147373 [147373] rhotic   q1  ? after
    @+171643 [171643] ta       q2  ? after
    @+176814 [176814] toil     q4  ? after
    @+179409 [179409] tricot   q5  ? after
    @+180643 [180643] tum      q6  ? after
    @+180933 [180933] turn     q8  ? after
    @+180975 [180975] turns    q11 ? after
    @+181003 [181003] turquois q12 ? after
    @+181012 [181012] turtle   q13 ? it
    @+181012 [181012] turtle   done. it
    @+181030 [181030] tusche   q10 ? before
    @+181127 [181127] twa      q9  ? before
    @+181321 [181321] twirl    q7  ? before
    @+182008 [182008] un       q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1341 🥳 6 ⏱️ 0:04:04.121080

📜 1 sessions
💰 score: 15

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:7419
    ⬜⬜⬜⬜⬜ tried:SEXES n n n n n remain:1615
    ⬜⬜⬜⬜⬜ tried:COOCH n n n n n remain:464
    ⬜⬜⬜⬜⬜ tried:WRUNG n n n n n remain:65
    ⬜🟩⬜⬜⬜ tried:FILMI n Y n n n remain:19
    ⬜🟩🟩🟩🟩 tried:DITTY n Y Y Y Y remain:3

    Undos used: 4

      3 words remaining
    x 5 unused letters
    = 15 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1484 🥳 18 ⏱️ 0:03:41.407951

📜 1 sessions
💰 score: 9800

    4/6
    TALES ⬜🟨⬜⬜⬜
    APRON 🟨⬜⬜⬜🟨
    KINDA 🟩⬜🟨⬜🟨
    KNACK 🟩🟩🟩🟩🟩
    5/6
    KNACK ⬜🟨⬜⬜⬜
    STONE ⬜⬜🟨🟨🟨
    OLDEN 🟨🟨⬜🟩🟨
    LONER 🟨🟩🟨🟩⬜
    NOVEL 🟩🟩🟩🟩🟩
    4/6
    NOVEL ⬜⬜⬜🟨🟨
    STALE ⬜⬜⬜🟩🟩
    CHILE ⬜⬜⬜🟩🟩
    BUGLE 🟩🟩🟩🟩🟩
    3/6
    BUGLE ⬜⬜⬜⬜🟩
    SWARE 🟩⬜⬜🟩🟩
    SPIRE 🟩🟩🟩🟩🟩
    Final 2/2
    FRONT ⬜🟩🟩🟨⬜
    DROWN 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1461 🥳 score:22 ⏱️ 0:02:06.830428

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. HEIST attempts:5 score:5
2. THEIR attempts:4 score:4
3. DETOX attempts:6 score:6
4. PRESS attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1461 🥳 score:66 ⏱️ 0:06:57.105085

📜 3 sessions

Octordle Classic

1. BASIS attempts:4 score:4
2. RANGE attempts:7 score:7
3. TWIRL attempts:5 score:5
4. MANGO attempts:9 score:9
5. OXIDE attempts:8 score:8
6. SPASM attempts:10 score:10
7. RUMBA attempts:11 score:11
8. FRAUD attempts:12 score:12

# [squareword.org](squareword.org) 🧩 #1454 🥳 7 ⏱️ 0:02:31.151433

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S K I F F
    C A V E R
    O Z O N E
    F O R C E
    F O Y E R

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1391 🥳 29 ⏱️ 0:00:59.162510

🤔 30 attempts
📜 1 sessions
🫧 1 chat sessions
⁉️ 8 chat prompts
🤖 8 dolphin3:latest replies
🔥  2 🥵  2 😎  5 🥶 16 🧊  4

     $1 #30  ~1 specification  100.00°C 🥳 1000‰
     $2 #23  ~4 conformance     47.43°C 🔥  993‰
     $3 #21  ~5 compatibility   46.67°C 🔥  992‰
     $4 #28  ~2 protocol        38.27°C 🥵  960‰
     $5 #27  ~3 guideline       36.44°C 🥵  933‰
     $6 #10  ~9 code            34.33°C 😎  883‰
     $7 #20  ~6 debugger        34.19°C 😎  878‰
     $8 #11  ~8 compiler        30.75°C 😎  718‰
     $9 #17  ~7 syntax          25.90°C 😎  194‰
    $10  #1 ~10 algorithm       24.93°C 😎    9‰
    $11 #18     variable        21.47°C 🥶
    $12 #26     compliance      18.67°C 🥶
    $13  #5     quantum         16.79°C 🥶
    $27  #3     eclipse         -3.01°C 🧊

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1424 🥳 155 ⏱️ 0:03:31.318963

🤔 156 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 41 chat prompts
🤖 41 dolphin3:latest replies
🔥  5 🥵 11 😎 26 🥶 84 🧊 29

      $1 #156   ~1 ange               100.00°C 🥳 1000‰
      $2  #13  ~42 ciel                50.78°C 🔥  996‰
      $3 #103  ~27 paradis             49.78°C 🔥  994‰
      $4 #140  ~11 cieux               49.64°C 🔥  993‰
      $5  #98  ~29 céleste             49.43°C 🔥  992‰
      $6 #111  ~22 amour               47.94°C 🔥  990‰
      $7 #120  ~18 éternel             44.64°C 🥵  984‰
      $8 #127  ~15 éternité            44.34°C 🥵  983‰
      $9 #155   ~2 dieu                44.10°C 🥵  982‰
     $10  #58  ~36 firmament           43.18°C 🥵  976‰
     $11 #148   ~8 sourire             41.92°C 🥵  970‰
     $18 #143  ~10 joie                36.19°C 😎  896‰
     $44  #44      éclat               25.84°C 🥶
    $128 #138      roche               -0.19°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #75 🥳 score:25 ⏱️ 0:01:45.919516

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. SULLY attempts:8 score:8
2. ICILY attempts:6 score:6
3. UNCLE attempts:4 score:4
4. INTER attempts:7 score:7

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1461 🥳 score:8 ⏱️ 0:04:14.299975

📜 2 sessions

Octordle Rescue

1. GRIND attempts:5 score:5
2. ANKLE attempts:7 score:7
3. RALLY attempts:9 score:9
4. TASTE attempts:12 score:12
5. FERAL attempts:8 score:8
6. UTILE attempts:13 score:13
7. SWORE attempts:11 score:11
8. DEVIL attempts:6 score:6
