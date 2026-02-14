# 2026-02-15

- 🔗 spaceword.org 🧩 2026-02-14 🏁 score 2173 ranked 9.8% 32/327 ⏱️ 0:19:10.926949
- 🔗 alfagok.diginaut.net 🧩 2026-02-15 😦 36 ⏱️ 0:00:45.663219
- 🔗 alphaguess.com 🧩 #937 🥳 30 ⏱️ 0:00:45.663821
- 🔗 dontwordle.com 🧩 #1363 🥳 6 ⏱️ 0:01:34.572881
- 🔗 dictionary.com hurdle 🧩 #1506 🥳 16 ⏱️ 0:02:52.472429
- 🔗 Quordle Classic 🧩 #1483 😦 score:24 ⏱️ 0:01:47.176454
- 🔗 Octordle Classic 🧩 #1483 🥳 score:58 ⏱️ 0:03:14.896570
- 🔗 squareword.org 🧩 #1476 🥳 7 ⏱️ 0:01:41.856125
- 🔗 cemantle.certitudes.org 🧩 #1413 🥳 44 ⏱️ 0:00:22.228444
- 🔗 cemantix.certitudes.org 🧩 #1446 🥳 58 ⏱️ 0:01:33.072419
- 🔗 Quordle Rescue 🧩 #97 🥳 score:25 ⏱️ 0:02:08.852394

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































# [spaceword.org](spaceword.org) 🧩 2026-02-14 🏁 score 2173 ranked 9.8% 32/327 ⏱️ 0:19:10.926949

📜 2 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 32/327

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ O O F _ _ _   
      _ _ _ _ _ _ I _ _ _   
      _ _ _ _ W A X _ _ _   
      _ _ _ _ E M U _ _ _   
      _ _ _ _ T A R _ _ _   
      _ _ _ _ _ T E _ _ _   
      _ _ _ _ G I _ _ _ _   
      _ _ _ _ _ V _ _ _ _   
      _ _ _ _ S E L _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 2026-02-15 😦 36 ⏱️ 0:00:45.663219

🤔 36 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+199817 [199817] lijm        q0  ? ␅
    @+199817 [199817] lijm        q1  ? after
    @+299722 [299722] schub       q2  ? ␅
    @+299722 [299722] schub       q3  ? after
    @+349490 [349490] vakantie    q4  ? ␅
    @+349490 [349490] vakantie    q5  ? after
    @+374231 [374231] vrij        q6  ? ␅
    @+374231 [374231] vrij        q7  ? after
    @+386772 [386772] wind        q8  ? ␅
    @+386772 [386772] wind        q9  ? after
    @+393189 [393189] zelfmoord   q10 ? ␅
    @+393189 [393189] zelfmoord   q11 ? after
    @+396397 [396397] zone        q12 ? ␅
    @+396397 [396397] zone        q13 ? after
    @+397143 [397143] zout        q16 ? ␅
    @+397143 [397143] zout        q17 ? after
    @+397236 [397236] zoutst      q20 ? ␅
    @+397236 [397236] zoutst      q21 ? after
    @+397279 [397279] zoveel      q22 ? ␅
    @+397279 [397279] zoveel      q23 ? after
    @+397303 [397303] zoölogische q24 ? ␅
    @+397303 [397303] zoölogische q25 ? after
    @+397309 [397309] zoönotische q28 ? ␅
    @+397309 [397309] zoönotische q29 ? after
    @+397312 [397312] zoötropen   q30 ? ␅
    @+397312 [397312] zoötropen   q31 ? after
    @+397312 [397312] zoötropen   <<< SEARCH
    @+397313 [397313] zucht       q34 ? ␅
    @+397313 [397313] zucht       q35 ? before
    @+397313 [397313] zucht       >>> SEARCH


# [alphaguess.com](alphaguess.com) 🧩 #937 🥳 30 ⏱️ 0:00:45.663821

🤔 30 attempts
📜 1 sessions

    @        [     0] aa       
    @+98219  [ 98219] mach     q0  ? ␅
    @+98219  [ 98219] mach     q1  ? after
    @+147375 [147375] rhumb    q2  ? ␅
    @+147375 [147375] rhumb    q3  ? after
    @+159487 [159487] slop     q6  ? ␅
    @+159487 [159487] slop     q7  ? after
    @+165529 [165529] stick    q8  ? ␅
    @+165529 [165529] stick    q9  ? after
    @+168581 [168581] sue      q10 ? ␅
    @+168581 [168581] sue      q11 ? after
    @+170088 [170088] surf     q12 ? ␅
    @+170088 [170088] surf     q13 ? after
    @+170090 [170090] surface  q28 ? ␅
    @+170090 [170090] surface  q29 ? it
    @+170090 [170090] surface  done. it
    @+170099 [170099] surfbird q26 ? ␅
    @+170099 [170099] surfbird q27 ? before
    @+170110 [170110] surfeit  q24 ? ␅
    @+170110 [170110] surfeit  q25 ? before
    @+170133 [170133] surge    q22 ? ␅
    @+170133 [170133] surge    q23 ? before
    @+170180 [170180] surpass  q20 ? ␅
    @+170180 [170180] surpass  q21 ? before
    @+170281 [170281] survival q18 ? ␅
    @+170281 [170281] survival q19 ? before
    @+170472 [170472] swamp    q16 ? ␅
    @+170472 [170472] swamp    q17 ? before
    @+170861 [170861] switch   q14 ? ␅
    @+170861 [170861] switch   q15 ? before
    @+171640 [171640] ta       q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1363 🥳 6 ⏱️ 0:01:34.572881

📜 2 sessions
💰 score: 9

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:SENES n n n n n remain:2614
    ⬜⬜⬜⬜⬜ tried:OVOLO n n n n n remain:974
    ⬜⬜⬜⬜⬜ tried:KUDZU n n n n n remain:420
    ⬜⬜⬜⬜🟨 tried:PHPHT n n n n m remain:61
    🟨⬜🟨⬜⬜ tried:ICTIC m n m n n remain:18
    ⬜🟨⬜🟩🟩 tried:FIFTY n m n Y Y remain:1

    Undos used: 3

      1 words remaining
    x 9 unused letters
    = 9 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1506 🥳 16 ⏱️ 0:02:52.472429

📜 1 sessions
💰 score: 10000

    4/6
    STEAL ⬜⬜🟩🟨⬜
    FRENA ⬜⬜🟩⬜🟩
    EDEMA ⬜⬜🟩🟨🟩
    OMEGA 🟩🟩🟩🟩🟩
    2/6
    OMEGA 🟨🟩🟨⬜⬜
    SMOTE 🟩🟩🟩🟩🟩
    4/6
    SMOTE ⬜⬜⬜⬜⬜
    KYLIN ⬜⬜🟩🟩⬜
    CALIF ⬜🟩🟩🟩⬜
    VALID 🟩🟩🟩🟩🟩
    4/6
    VALID ⬜⬜⬜🟨⬜
    TIERS 🟨🟨🟨⬜⬜
    QUIET ⬜⬜🟩🟨🟩
    FEINT 🟩🟩🟩🟩🟩
    Final 2/2
    PICKY ⬜🟩🟨⬜⬜
    BIRCH 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1483 😦 score:24 ⏱️ 0:01:47.176454

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. VOILA attempts:3 score:3
2. SHAKY attempts:5 score:5
3. WHEAT attempts:7 score:7
4. _UMBO -ADEHIJKLNPRSTVWXY attempts:9 score:-1

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1483 🥳 score:58 ⏱️ 0:03:14.896570

📜 1 sessions

Octordle Classic

1. DAILY attempts:8 score:8
2. SHELL attempts:5 score:5
3. RISKY attempts:6 score:6
4. RAISE attempts:2 score:2
5. AVERT attempts:9 score:9
6. HERON attempts:10 score:10
7. STRIP attempts:11 score:11
8. MEDAL attempts:7 score:7

# [squareword.org](squareword.org) 🧩 #1476 🥳 7 ⏱️ 0:01:41.856125

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P I R E
    C A N A L
    U P E N D
    B A R G E
    A L T E R

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1413 🥳 44 ⏱️ 0:00:22.228444

🤔 45 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 7 chat prompts
🤖 7 dolphin3:latest replies
🔥  1 🥵  1 😎  4 🥶 34 🧊  4

     $1 #45 critique     100.00°C 🥳 1000‰ ~41 used:0 [40]  source:dolphin3
     $2 #20 critic        51.53°C 🔥  991‰  ~1 used:3 [0]   source:dolphin3
     $3 #30 commentary    45.63°C 🥵  971‰  ~2 used:0 [1]   source:dolphin3
     $4 #22 narrative     38.74°C 😎  872‰  ~5 used:3 [4]   source:dolphin3
     $5 #24 prose         37.55°C 😎  825‰  ~6 used:3 [5]   source:dolphin3
     $6 #28 analysis      33.36°C 😎  518‰  ~4 used:2 [3]   source:dolphin3
     $7 #35 essayist      30.87°C 😎  182‰  ~3 used:0 [2]   source:dolphin3
     $8 #29 article       29.43°C 🥶       ~10 used:1 [9]   source:dolphin3
     $9 #42 sonnet        29.29°C 🥶       ~11 used:0 [10]  source:dolphin3
    $10 #38 literary      29.06°C 🥶       ~12 used:0 [11]  source:dolphin3
    $11 #39 lyrical       28.72°C 🥶       ~13 used:0 [12]  source:dolphin3
    $12 #17 anthology     28.54°C 🥶        ~7 used:3 [6]   source:dolphin3
    $13 #16 literature    28.52°C 🥶       ~14 used:1 [13]  source:dolphin3
    $42 #13 volume        -0.14°C 🧊       ~42 used:0 [41]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1446 🥳 58 ⏱️ 0:01:33.072419

🤔 59 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 22 chat prompts
🤖 22 dolphin3:latest replies
😱  1 🔥  1 😎 12 🥶 35 🧊  9

     $1 #59 boutique      100.00°C 🥳 1000‰ ~50 used:0  [49]  source:dolphin3
     $2 #49 magasin        66.92°C 😱  999‰  ~1 used:7  [0]   source:dolphin3
     $3 #45 épicerie       48.77°C 🔥  992‰  ~2 used:8  [1]   source:dolphin3
     $4 #23 boulangerie    33.00°C 😎  848‰ ~14 used:11 [13]  source:dolphin3
     $5 #40 confiserie     32.60°C 😎  838‰ ~11 used:4  [10]  source:dolphin3
     $6 #15 chocolatier    30.71°C 😎  788‰ ~13 used:7  [12]  source:dolphin3
     $7 #22 pâtisserie     30.23°C 😎  776‰ ~12 used:4  [11]  source:dolphin3
     $8 #42 café           29.84°C 😎  765‰  ~3 used:1  [2]   source:dolphin3
     $9 #46 panier         28.09°C 😎  701‰  ~4 used:0  [3]   source:dolphin3
    $10 #36 cupcake        27.43°C 😎  668‰  ~9 used:3  [8]   source:dolphin3
    $11 #47 épicier        27.13°C 😎  656‰  ~5 used:0  [4]   source:dolphin3
    $12 #27 petit          26.02°C 😎  589‰  ~8 used:2  [7]   source:dolphin3
    $16  #7 macaron        19.14°C 🥶       ~15 used:1  [14]  source:dolphin3
    $51 #34 chou           -0.17°C 🧊       ~51 used:0  [50]  source:dolphin3

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #97 🥳 score:25 ⏱️ 0:02:08.852394

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. GLADE attempts:4 score:4
2. CRANK attempts:8 score:8
3. ROCKY attempts:7 score:7
4. KNEEL attempts:6 score:6
