# 2026-04-26

- 🔗 spaceword.org 🧩 2026-04-25 🏁 score 2173 ranked 9.9% 21/213 ⏱️ 0:23:12.353595
- 🔗 alfagok.diginaut.net 🧩 #540 🥳 26 ⏱️ 0:00:38.975598
- 🔗 alphaguess.com 🧩 #1007 🥳 36 ⏱️ 0:00:38.352513
- 🔗 dontwordle.com 🧩 #1433 🥳 6 ⏱️ 0:01:39.639622
- 🔗 dictionary.com hurdle 🧩 #1576 🥳 17 ⏱️ 0:04:53.801738
- 🔗 Quordle Classic 🧩 #1553 🥳 score:26 ⏱️ 0:01:49.232428
- 🔗 Octordle Classic 🧩 #1553 🥳 score:60 ⏱️ 0:03:29.418758
- 🔗 squareword.org 🧩 #1546 🥳 10 ⏱️ 0:02:51.121634
- 🔗 cemantle.certitudes.org 🧩 #1483 🥳 324 ⏱️ 0:05:00.855880
- 🔗 cemantix.certitudes.org 🧩 #1516 🥳 323 ⏱️ 0:06:53.095165

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
























































# [spaceword.org](spaceword.org) 🧩 2026-04-25 🏁 score 2173 ranked 9.9% 21/213 ⏱️ 0:23:12.353595

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 21/213

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ T A _ _ _ _   
      _ _ _ _ _ M E _ _ _   
      _ _ _ _ M I X _ _ _   
      _ _ _ _ O D E _ _ _   
      _ _ _ _ T O R _ _ _   
      _ _ _ _ I _ G _ _ _   
      _ _ _ _ V _ U _ _ _   
      _ _ _ _ E K E _ _ _   
      _ _ _ _ D _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #540 🥳 26 ⏱️ 0:00:38.975598

🤔 26 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+199704 [199704] lijk       q0  ? ␅
    @+199704 [199704] lijk       q1  ? after
    @+199704 [199704] lijk       q2  ? ␅
    @+199704 [199704] lijk       q3  ? after
    @+249650 [249650] opinie     q6  ? ␅
    @+249650 [249650] opinie     q7  ? after
    @+262042 [262042] peper      q10 ? ␅
    @+262042 [262042] peper      q11 ? after
    @+268055 [268055] politie    q12 ? ␅
    @+268055 [268055] politie    q13 ? after
    @+271311 [271311] presente   q14 ? ␅
    @+271311 [271311] presente   q15 ? after
    @+272881 [272881] proces     q16 ? ␅
    @+272881 [272881] proces     q17 ? after
    @+273030 [273030] procuratie q22 ? ␅
    @+273030 [273030] procuratie q23 ? after
    @+273077 [273077] product    q24 ? ␅
    @+273077 [273077] product    q25 ? it
    @+273077 [273077] product    done. it
    @+273176 [273176] productief q20 ? ␅
    @+273176 [273176] productief q21 ? before
    @+273478 [273478] proef      q18 ? ␅
    @+273478 [273478] proef      q19 ? before
    @+274572 [274572] prop       q8  ? ␅
    @+274572 [274572] prop       q9  ? before
    @+299649 [299649] schroot    q4  ? ␅
    @+299649 [299649] schroot    q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1007 🥳 36 ⏱️ 0:00:38.352513

🤔 36 attempts
📜 1 sessions

    @        [     0] aa       
    @+98216  [ 98216] mach     q0  ? ␅
    @+98216  [ 98216] mach     q1  ? after
    @+98216  [ 98216] mach     q2  ? ␅
    @+98216  [ 98216] mach     q3  ? after
    @+98216  [ 98216] mach     q4  ? ␅
    @+98216  [ 98216] mach     q5  ? after
    @+98216  [ 98216] mach     q6  ? ␅
    @+98216  [ 98216] mach     q7  ? after
    @+147366 [147366] rhotic   q8  ? ␅
    @+147366 [147366] rhotic   q9  ? after
    @+171636 [171636] ta       q10 ? ␅
    @+171636 [171636] ta       q11 ? after
    @+176813 [176813] toilet   q14 ? ␅
    @+176813 [176813] toilet   q15 ? after
    @+179407 [179407] trictrac q16 ? ␅
    @+179407 [179407] trictrac q17 ? after
    @+180009 [180009] trop     q20 ? ␅
    @+180009 [180009] trop     q21 ? after
    @+180149 [180149] trow     q24 ? ␅
    @+180149 [180149] trow     q25 ? after
    @+180166 [180166] troy     q30 ? ␅
    @+180166 [180166] troy     q31 ? after
    @+180170 [180170] truant   q32 ? ␅
    @+180170 [180170] truant   q33 ? after
    @+180177 [180177] truce    q34 ? ␅
    @+180177 [180177] truce    q35 ? it
    @+180177 [180177] truce    done. it
    @+180182 [180182] truck    q28 ? ␅
    @+180182 [180182] truck    q29 ? before
    @+180224 [180224] true     q27 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1433 🥳 6 ⏱️ 0:01:39.639622

📜 1 sessions
💰 score: 44

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:SHUSH n n n n n remain:4857
    ⬜⬜⬜⬜⬜ tried:NANNA n n n n n remain:1827
    ⬜⬜⬜⬜⬜ tried:POOPY n n n n n remain:586
    ⬜🟩🟨⬜⬜ tried:GRRRL n Y m n n remain:9
    ⬜🟩⬜🟩🟩 tried:FREER n Y n Y Y remain:5
    ⬜🟩🟩🟩🟩 tried:BRIER n Y Y Y Y remain:4

    Undos used: 2

      4 words remaining
    x 11 unused letters
    = 44 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1576 🥳 17 ⏱️ 0:04:53.801738

📜 1 sessions
💰 score: 9900

    3/6
    SOLAR ⬜🟨🟨🟨🟨
    ARGOL 🟨🟨⬜🟩🟩
    CAROL 🟩🟩🟩🟩🟩
    4/6
    CAROL ⬜🟨⬜⬜🟩
    PETAL ⬜🟩🟩🟩🟩
    METAL ⬜🟩🟩🟩🟩
    FETAL 🟩🟩🟩🟩🟩
    5/6
    FETAL ⬜⬜⬜🟨⬜
    ROANS ⬜🟨🟨🟨⬜
    BACON ⬜🟩⬜🟨🟨
    DANIO ⬜🟩🟩⬜🟩
    MANGO 🟩🟩🟩🟩🟩
    3/6
    MANGO ⬜🟨🟩⬜🟨
    DONAS ⬜🟩🟩🟩🟨
    SONAR 🟩🟩🟩🟩🟩
    Final 2/2
    AVERT 🟨⬜🟨🟨🟨
    TRADE 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1553 🥳 score:26 ⏱️ 0:01:49.232428

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. PITHY attempts:6 score:6
2. BOAST attempts:7 score:7
3. PRIED attempts:8 score:8
4. BLIMP attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1553 🥳 score:60 ⏱️ 0:03:29.418758

📜 1 sessions

Octordle Classic

1. PRIDE attempts:6 score:6
2. FLASK attempts:9 score:9
3. FEMUR attempts:4 score:4
4. TOPAZ attempts:7 score:7
5. BLAME attempts:5 score:5
6. FROCK attempts:8 score:8
7. LOYAL attempts:10 score:10
8. GROAN attempts:11 score:11

# [squareword.org](squareword.org) 🧩 #1546 🥳 10 ⏱️ 0:02:51.121634

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟨 🟩
    🟩 🟨 🟨 🟨 🟨
    🟨 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B A T C H
    E E R I E
    G R A T E
    A I D E D
    N E E D S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1483 🥳 324 ⏱️ 0:05:00.855880

🤔 325 attempts
📜 1 sessions
🫧 16 chat sessions
⁉️ 76 chat prompts
🤖 76 dolphin3:latest replies
🔥   5 🥵  10 😎  39 🥶 241 🧊  29

      $1 #325 inspector        100.00°C 🥳 1000‰ ~296 used:0  [295]  source:dolphin3
      $2 #297 supervisor        56.27°C 😱  999‰   ~1 used:7  [0]    source:dolphin3
      $3 #293 inspectorate      52.87°C 🔥  996‰   ~4 used:2  [3]    source:dolphin3
      $4 #140 inspection        51.87°C 🔥  995‰  ~12 used:94 [11]   source:dolphin3
      $5 #298 surveyor          50.47°C 🔥  993‰   ~2 used:1  [1]    source:dolphin3
      $6 #300 administrator     49.22°C 🔥  992‰   ~3 used:0  [2]    source:dolphin3
      $7 #291 examiner          46.43°C 🥵  986‰   ~5 used:0  [4]    source:dolphin3
      $8 #258 auditor           42.92°C 🥵  979‰  ~46 used:18 [45]   source:dolphin3
      $9 #321 appraiser         42.89°C 🥵  977‰   ~6 used:0  [5]    source:dolphin3
     $10 #287 assessor          42.49°C 🥵  974‰   ~7 used:1  [6]    source:dolphin3
     $11 #312 magistrate        42.14°C 🥵  970‰   ~8 used:0  [7]    source:dolphin3
     $17 #224 enforcement       34.26°C 😎  896‰  ~47 used:2  [46]   source:dolphin3
     $56  #59 horticulture      20.99°C 🥶        ~57 used:4  [56]   source:dolphin3
    $297 #221 treatment         -0.06°C 🧊       ~297 used:0  [296]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1516 🥳 323 ⏱️ 0:06:53.095165

🤔 324 attempts
📜 1 sessions
🫧 17 chat sessions
⁉️ 85 chat prompts
🤖 85 dolphin3:latest replies
🔥   4 🥵  14 😎  57 🥶 212 🧊  36

      $1 #324 réciproque          100.00°C 🥳 1000‰ ~288 used:0  [287]  source:dolphin3
      $2 #208 mutuel               53.36°C 🔥  995‰  ~11 used:54 [10]   source:dolphin3
      $3 #116 échange              50.98°C 🔥  994‰  ~16 used:71 [15]   source:dolphin3
      $4 #322 interdépendance      46.96°C 🔥  992‰   ~1 used:0  [0]    source:dolphin3
      $5 #285 commun               46.26°C 🔥  990‰   ~2 used:16 [1]    source:dolphin3
      $6 #255 partage              45.03°C 🥵  987‰  ~12 used:6  [11]   source:dolphin3
      $7 #319 interrelation        42.79°C 🥵  979‰   ~4 used:3  [3]    source:dolphin3
      $8  #57 dialogue             42.74°C 🥵  978‰  ~75 used:32 [74]   source:dolphin3
      $9  #18 coopération          42.27°C 🥵  977‰  ~74 used:19 [73]   source:dolphin3
     $10  #24 complémentarité      41.42°C 🥵  972‰  ~13 used:6  [12]   source:dolphin3
     $11  #32 interaction          40.42°C 🥵  965‰  ~14 used:6  [13]   source:dolphin3
     $20 #259 partager             34.93°C 😎  878‰  ~17 used:0  [16]   source:dolphin3
     $77 #195 affrontement         24.63°C 🥶        ~76 used:0  [75]   source:dolphin3
    $289 #159 symposium            -0.10°C 🧊       ~289 used:0  [288]  source:dolphin3
