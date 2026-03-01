# 2026-03-03

- 🔗 alfagok.diginaut.net 🧩 #486 🥳 26 ⏱️ 0:00:35.479004
- 🔗 alphaguess.com 🧩 #953 🥳 34 ⏱️ 0:00:29.014667
- 🔗 dontwordle.com 🧩 #1379 🥳 6 ⏱️ 0:01:39.288084
- 🔗 dictionary.com hurdle 🧩 #1522 😦 21 ⏱️ 0:03:33.649351
- 🔗 Quordle Classic 🧩 #1499 🥳 score:22 ⏱️ 0:01:27.728219
- 🔗 Octordle Classic 🧩 #1499 🥳 score:66 ⏱️ 0:03:54.729255
- 🔗 squareword.org 🧩 #1492 🥳 6 ⏱️ 0:01:22.351028
- 🔗 cemantle.certitudes.org 🧩 #1429 🥳 631 ⏱️ 0:28:15.029365
- 🔗 cemantix.certitudes.org 🧩 #1462 🥳 42 ⏱️ 0:00:38.309934

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


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #486 🥳 26 ⏱️ 0:00:35.479004

🤔 26 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+199812 [199812] lijm       q0  ? ␅
    @+199812 [199812] lijm       q1  ? after
    @+247702 [247702] op         q4  ? ␅
    @+247702 [247702] op         q5  ? after
    @+273507 [273507] proef      q6  ? ␅
    @+273507 [273507] proef      q7  ? after
    @+286575 [286575] rijs       q8  ? ␅
    @+286575 [286575] rijs       q9  ? after
    @+288119 [288119] roemrucht  q14 ? ␅
    @+288119 [288119] roemrucht  q15 ? after
    @+288443 [288443] rok        q18 ? ␅
    @+288443 [288443] rok        q19 ? after
    @+288508 [288508] rol        q20 ? ␅
    @+288508 [288508] rol        q21 ? after
    @+288597 [288597] rollen     q24 ? ␅
    @+288597 [288597] rollen     q25 ? it
    @+288597 [288597] rollen     done. it
    @+288685 [288685] rolstempel q22 ? ␅
    @+288685 [288685] rolstempel q23 ? before
    @+288861 [288861] rommel     q16 ? ␅
    @+288861 [288861] rommel     q17 ? before
    @+289670 [289670] roof       q12 ? ␅
    @+289670 [289670] roof       q13 ? before
    @+292803 [292803] samen      q10 ? ␅
    @+292803 [292803] samen      q11 ? before
    @+299705 [299705] schub      q2  ? ␅
    @+299705 [299705] schub      q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #953 🥳 34 ⏱️ 0:00:29.014667

🤔 34 attempts
📜 1 sessions

    @       [    0] aa        
    @+47381 [47381] dis       q2  ? ␅
    @+47381 [47381] dis       q3  ? after
    @+53397 [53397] el        q8  ? ␅
    @+53397 [53397] el        q9  ? after
    @+56742 [56742] equate    q10 ? ␅
    @+56742 [56742] equate    q11 ? after
    @+57525 [57525] et        q14 ? ␅
    @+57525 [57525] et        q15 ? after
    @+57938 [57938] euphemize q16 ? ␅
    @+57938 [57938] euphemize q17 ? after
    @+58148 [58148] evanish   q18 ? ␅
    @+58148 [58148] evanish   q19 ? after
    @+58172 [58172] eve       q20 ? ␅
    @+58172 [58172] eve       q21 ? after
    @+58193 [58193] event     q24 ? ␅
    @+58193 [58193] event     q25 ? after
    @+58217 [58217] ever      q26 ? ␅
    @+58217 [58217] ever      q27 ? after
    @+58233 [58233] evert     q28 ? ␅
    @+58233 [58233] evert     q29 ? after
    @+58241 [58241] every     q30 ? ␅
    @+58241 [58241] every     q31 ? after
    @+58249 [58249] everyone  q32 ? ␅
    @+58249 [58249] everyone  q33 ? it
    @+58249 [58249] everyone  done. it
    @+58257 [58257] evict     q22 ? ␅
    @+58257 [58257] evict     q23 ? before
    @+58358 [58358] ex        q12 ? ␅
    @+58358 [58358] ex        q13 ? before
    @+60084 [60084] face      q7  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1379 🥳 6 ⏱️ 0:01:39.288084

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:7042
    ⬜⬜⬜⬜⬜ tried:AGAMA n n n n n remain:2820
    ⬜⬜⬜⬜⬜ tried:FIZZY n n n n n remain:1119
    ⬜⬜🟨⬜⬜ tried:CHOCK n n m n n remain:256
    ⬜🟩⬜⬜⬜ tried:DORRS n Y n n n remain:10
    ⬜🟩⬜🟩⬜ tried:WOWEE n Y n Y n remain:2

    Undos used: 4

      2 words remaining
    x 7 unused letters
    = 14 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1522 😦 21 ⏱️ 0:03:33.649351

📜 1 sessions
💰 score: 4580

    4/6
    READS ⬜⬜🟨⬜⬜
    FAINT ⬜🟨⬜🟨⬜
    ONLAY ⬜🟩🟨🟨⬜
    ANNUL 🟩🟩🟩🟩🟩
    4/6
    ANNUL 🟨⬜⬜⬜🟩
    FRAIL ⬜⬜🟨⬜🟩
    PETAL ⬜🟨⬜🟨🟩
    BAGEL 🟩🟩🟩🟩🟩
    5/6
    BAGEL 🟩⬜⬜⬜⬜
    BRISK 🟩⬜⬜⬜⬜
    BUMPY 🟩⬜⬜⬜🟩
    BOTHY 🟩🟩🟨⬜🟩
    BOOTY 🟩🟩🟩🟩🟩
    6/6
    BOOTY ⬜⬜⬜🟨⬜
    RESAT ⬜🟨⬜⬜🟩
    INLET 🟨⬜⬜🟨🟩
    EIGHT 🟩🟨⬜⬜🟩
    EDICT 🟩⬜🟩🟩🟩
    EVICT 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜🟩🟩⬜🟨
    ????? ⬜🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1499 🥳 score:22 ⏱️ 0:01:27.728219

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. GNOME attempts:4 score:4
2. HARDY attempts:7 score:7
3. ISLET attempts:5 score:5
4. ALLOY attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1499 🥳 score:66 ⏱️ 0:03:54.729255

📜 1 sessions

Octordle Classic

1. CAVIL attempts:13 score:13
2. FORCE attempts:4 score:4
3. SEIZE attempts:11 score:11
4. GLIDE attempts:8 score:8
5. DONOR attempts:10 score:10
6. STOCK attempts:5 score:5
7. WEEDY attempts:9 score:9
8. FRAME attempts:6 score:6

# [squareword.org](squareword.org) 🧩 #1492 🥳 6 ⏱️ 0:01:22.351028

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B L A S T
    E A G L E
    G R A I N
    E V I C T
    T A N K S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1429 🥳 631 ⏱️ 0:28:15.029365

🤔 632 attempts
📜 1 sessions
🫧 63 chat sessions
⁉️ 344 chat prompts
🤖 344 dolphin3:latest replies
🥵  15 😎  70 🥶 531 🧊  15

      $1 #632 humanity            100.00°C 🥳 1000‰ ~617 used:0   [616]  source:dolphin3
      $2 #480 compassion           52.14°C 🥵  989‰  ~81 used:103 [80]   source:dolphin3
      $3 #308 limitlessness        50.64°C 🥵  986‰  ~84 used:204 [83]   source:dolphin3
      $4 #297 endlessness          49.38°C 🥵  981‰  ~82 used:114 [81]   source:dolphin3
      $5 #578 holiness             47.08°C 🥵  971‰   ~6 used:16  [5]    source:dolphin3
      $6 #583 sacredness           45.55°C 🥵  960‰   ~7 used:16  [6]    source:dolphin3
      $7 #487 kindness             45.18°C 🥵  956‰   ~8 used:16  [7]    source:dolphin3
      $8 #269 boundlessness        44.88°C 🥵  951‰  ~75 used:47  [74]   source:dolphin3
      $9 #176 wholeness            44.39°C 🥵  944‰  ~79 used:52  [78]   source:dolphin3
     $10 #167 interrelatedness     43.79°C 🥵  930‰  ~49 used:36  [48]   source:dolphin3
     $11 #230 aliveness            43.58°C 🥵  925‰  ~52 used:37  [51]   source:dolphin3
     $17 #283 eternal              42.52°C 😎  899‰  ~53 used:4   [52]   source:dolphin3
     $87 #621 emptiness            32.16°C 🥶        ~91 used:0   [90]   source:dolphin3
    $618 #571 guidance             -0.05°C 🧊       ~618 used:0   [617]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1462 🥳 42 ⏱️ 0:00:38.309934

🤔 43 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 7 chat prompts
🤖 7 dolphin3:latest replies
🥵  2 😎  6 🥶 28 🧊  6

     $1 #43 boisson     100.00°C 🥳 1000‰ ~37 used:0 [36]  source:dolphin3
     $2 #31 breuvage     39.25°C 🥵  979‰  ~1 used:3 [0]   source:dolphin3
     $3  #1 café         37.85°C 🥵  970‰  ~2 used:9 [1]   source:dolphin3
     $4 #12 cappuccino   23.19°C 😎  481‰  ~8 used:3 [7]   source:dolphin3
     $5 #18 ristretto    20.91°C 😎  224‰  ~3 used:1 [2]   source:dolphin3
     $6 #21 chocolat     20.83°C 😎  214‰  ~4 used:0 [3]   source:dolphin3
     $7 #25 lait         20.31°C 😎  143‰  ~5 used:0 [4]   source:dolphin3
     $8 #32 concentré    20.04°C 😎   89‰  ~6 used:0 [5]   source:dolphin3
     $9 #17 espresso     19.82°C 😎   56‰  ~7 used:0 [6]   source:dolphin3
    $10  #7 kilo         18.87°C 🥶        ~9 used:0 [8]   source:dolphin3
    $11 #35 glacé        17.92°C 🥶       ~10 used:0 [9]   source:dolphin3
    $12 #42 chaud        17.14°C 🥶       ~11 used:0 [10]  source:dolphin3
    $13 #24 gourmand     16.43°C 🥶       ~12 used:0 [11]  source:dolphin3
    $38 #16 arabe        -0.77°C 🧊       ~38 used:0 [37]  source:dolphin3
