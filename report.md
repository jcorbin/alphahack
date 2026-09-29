# 2026-09-30

- 🔗 wordgrid 🧩 #851 🟪 rarity:0.17 ⏱️ 0:03:16.804543
- 🔗 spaceword.org 🧩 2026-09-29 🏁 score 2168 ranked 42.7% 137/321 ⏱️ 0:55:59.506862
- 🔗 alfagok.diginaut.net 🧩 #697 🥳 30 ⏱️ 0:00:33.029596
- 🔗 alphaguess.com 🧩 #1164 🥳 28 ⏱️ 0:00:34.185557
- 🔗 dontwordle.com 🧩 #1590 🥳 6 ⏱️ 0:01:49.841395
- 🔗 dictionary.com hurdle 🧩 #1733 🥳 19 ⏱️ 0:02:59.402238
- 🔗 Quordle Classic 🧩 #1710 😦 score:28 ⏱️ 0:03:09.636835
- 🔗 Octordle Classic 🧩 #1710 🥳 score:52 ⏱️ 0:01:56.639915
- 🔗 Sedecordle Classic 🧩 #1690 🥳 score:46 ⏱️ 0:03:58.717335
- 🔗 squareword.org 🧩 #1703 🥳 7 ⏱️ 0:01:54.523649
- 🔗 cemantle.certitudes.org 🧩 #1640 🥳 44 ⏱️ 0:00:44.141927
- 🔗 cemantix.certitudes.org 🧩 #1673 🥳 153 ⏱️ 0:23:58.105244

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










# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #851 🟪 rarity:0.17 ⏱️ 0:03:16.804543

📜 2 sessions
🌌 🌌 🌌
🦄 🌌 🦄
🦄 🌌 🦄
Rarity: 0.17 🟪

# [spaceword.org](spaceword.org) 🧩 2026-09-29 🏁 score 2168 ranked 42.7% 137/321 ⏱️ 0:55:59.506862

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 137/321

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ C O L D _ _ _ _ _   
      _ E _ O _ _ Z _ N _   
      _ E Q U A T E _ I _   
      _ _ _ P H E N I X _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #697 🥳 30 ⏱️ 0:00:33.029596

🤔 30 attempts
📜 1 sessions

    @        [     0] &-teken        
    @+786    [   786] aan            q10 ? ␅
    @+786    [   786] aan            q11 ? after
    @+893    [   893] aanbid         q22 ? ␅
    @+893    [   893] aanbid         q23 ? after
    @+893    [   893] aanbid         q24 ? ␅
    @+893    [   893] aanbid         q25 ? after
    @+958    [   958] aanblik        q26 ? ␅
    @+958    [   958] aanblik        q27 ? after
    @+963    [   963] aanbod         q28 ? ␅
    @+963    [   963] aanbod         q29 ? it
    @+963    [   963] aanbod         done. it
    @+1029   [  1029] aanbrand       q20 ? ␅
    @+1029   [  1029] aanbrand       q21 ? before
    @+1273   [  1273] aandik         q18 ? ␅
    @+1273   [  1273] aandik         q19 ? before
    @+1767   [  1767] aangemonsterde q16 ? ␅
    @+1767   [  1767] aangemonsterde q17 ? before
    @+2747   [  2747] aanlokkelijk   q14 ? ␅
    @+2747   [  2747] aanlokkelijk   q15 ? before
    @+4713   [  4713] aardappelschil q12 ? ␅
    @+4713   [  4713] aardappelschil q13 ? before
    @+8646   [  8646] af             q8  ? ␅
    @+8646   [  8646] af             q9  ? before
    @+24874  [ 24874] bad            q6  ? ␅
    @+24874  [ 24874] bad            q7  ? before
    @+49802  [ 49802] boks           q4  ? ␅
    @+49802  [ 49802] boks           q5  ? before
    @+99672  [ 99672] ex             q2  ? ␅
    @+99672  [ 99672] ex             q3  ? before
    @+199528 [199528] lij            q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1164 🥳 28 ⏱️ 0:00:34.185557

🤔 28 attempts
📜 1 sessions

    @        [     0] aa         
    @+1      [     1] aah        
    @+2      [     2] aahed      
    @+3      [     3] aahing     
    @+98142  [ 98142] mac        q0  ? ␅
    @+98142  [ 98142] mac        q1  ? after
    @+109924 [109924] ne         q6  ? ␅
    @+109924 [109924] ne         q7  ? after
    @+116318 [116318] orb        q8  ? ␅
    @+116318 [116318] orb        q9  ? after
    @+116337 [116337] orc        q22 ? ␅
    @+116337 [116337] orc        q23 ? after
    @+116382 [116382] orcin      q24 ? ␅
    @+116382 [116382] orcin      q25 ? after
    @+116397 [116397] order      q26 ? ␅
    @+116397 [116397] order      q27 ? it
    @+116397 [116397] order      done. it
    @+116425 [116425] ordination q20 ? ␅
    @+116425 [116425] ordination q21 ? before
    @+116531 [116531] orgiast    q18 ? ␅
    @+116531 [116531] orgiast    q19 ? before
    @+116745 [116745] ortho      q14 ? ␅
    @+116745 [116745] ortho      q15 ? before
    @+117203 [117203] out        q12 ? ␅
    @+117203 [117203] out        q13 ? before
    @+118722 [118722] over       q10 ? ␅
    @+118722 [118722] over       q11 ? before
    @+122718 [122718] parol      q4  ? ␅
    @+122718 [122718] parol      q5  ? before
    @+147305 [147305] rho        q2  ? ␅
    @+147305 [147305] rho        q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1590 🥳 6 ⏱️ 0:01:49.841395

📜 1 sessions
💰 score: 27

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:DEKED n n n n n remain:5348
    ⬜⬜⬜⬜⬜ tried:HALAL n n n n n remain:1538
    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:739
    ⬜⬜⬜⬜⬜ tried:MUMMY n n n n n remain:192
    ⬜🟨⬜⬜🟨 tried:BOFFO n m n n m remain:15
    🟨🟩⬜🟩🟨 tried:OPPOS m Y n Y m remain:3

    Undos used: 2

      3 words remaining
    x 9 unused letters
    = 27 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1733 🥳 19 ⏱️ 0:02:59.402238

📜 1 sessions
💰 score: 9700

    5/6
    STELA ⬜⬜⬜⬜⬜
    YOURN ⬜🟨🟨🟨⬜
    DUROC ⬜🟩🟨🟩⬜
    HUMOR ⬜🟩🟩🟩🟩
    RUMOR 🟩🟩🟩🟩🟩
    4/6
    RUMOR 🟨🟩⬜⬜⬜
    SURGE 🟨🟩🟩⬜🟩
    BACON ⬜⬜⬜⬜🟨
    NURSE 🟩🟩🟩🟩🟩
    4/6
    NURSE ⬜⬜⬜⬜🟩
    MAILE ⬜🟨⬜🟨🟩
    GLADE 🟩🟩🟩⬜🟩
    GLAZE 🟩🟩🟩🟩🟩
    4/6
    GLAZE 🟩⬜⬜⬜🟨
    GORES 🟩🟩🟨🟩⬜
    COMFY ⬜🟩⬜🟨⬜
    GOFER 🟩🟩🟩🟩🟩
    Final 2/2
    CHILD ⬜🟨⬜⬜⬜
    MONTH 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1710 😦 score:28 ⏱️ 0:03:09.636835

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. CHOKE attempts:4 score:4
2. BATCH attempts:7 score:7
3. MOSSY attempts:8 score:8
4. _AGER -BCDHIKLMNOPSTUWY attempts:9 score:-1

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1710 🥳 score:52 ⏱️ 0:01:56.639915

📜 1 sessions

Octordle Classic

1. TEARY attempts:3 score:3
2. EDIFY attempts:4 score:4
3. SWOOP attempts:9 score:9
4. CREDO attempts:6 score:6
5. SLIMY attempts:10 score:10
6. INLAY attempts:5 score:5
7. WOVEN attempts:8 score:8
8. BRAVO attempts:7 score:7

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1690 🥳 score:46 ⏱️ 0:03:58.717335

📜 3 sessions

Sedecordle Classic sedecordle.com

1. SCOUT attempts:4 score:0
2. MANLY attempts:5 score:4
3. UNFIT attempts:7 score:0
4. CRAFT attempts:6 score:7
5. SLACK attempts:8 score:0
6. RASPY attempts:9 score:8
7. PULPY attempts:10 score:1
8. SHINY attempts:11 score:0
9. SWILL attempts:12 score:1
10. EPOXY attempts:13 score:2
11. SPEND attempts:14 score:1
12. HOTLY attempts:15 score:4
13. UNLIT attempts:18 score:1
14. MUSTY attempts:16 score:9
15. FOGGY attempts:17 score:1
16. TRUCK attempts:18 score:7

# [squareword.org](squareword.org) 🧩 #1703 🥳 7 ⏱️ 0:01:54.523649

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A C R E S
    W E A V E
    A L D E R
    S L A N G
    H O R S E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1640 🥳 44 ⏱️ 0:00:44.141927

🤔 45 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 6 chat prompts
🤖 6 gemma4:12b replies
😱  1 🔥  3 🥵  8 😎 11 🥶 19 🧊  2

     $1 #45 supporter     100.00°C 🥳 1000‰ ~43 used:0 [42]  source:gemma4
     $2 #32 backer         70.55°C 😱  999‰  ~1 used:0 [0]   source:gemma4
     $3 #41 proponent      69.53°C 🔥  998‰  ~2 used:0 [1]   source:gemma4
     $4 #29 advocate       56.49°C 🔥  996‰  ~4 used:2 [3]   source:gemma4
     $5 #33 believer       52.19°C 🔥  993‰  ~3 used:0 [2]   source:gemma4
     $6 #31 ally           48.79°C 🥵  987‰  ~5 used:0 [4]   source:gemma4
     $7 #30 activist       44.96°C 🥵  980‰  ~6 used:0 [5]   source:gemma4
     $8 #44 sponsor        41.06°C 🥵  967‰  ~7 used:0 [6]   source:gemma4
     $9 #36 crusader       39.31°C 🥵  962‰  ~8 used:0 [7]   source:gemma4
    $10 #35 cheerleader    38.92°C 🥵  959‰  ~9 used:0 [8]   source:gemma4
    $11 #21 instigator     36.62°C 🥵  944‰ ~11 used:3 [10]  source:gemma4
    $14 #24 promoter       31.26°C 😎  848‰ ~13 used:1 [12]  source:gemma4
    $25 #20 influence      17.76°C 🥶       ~25 used:0 [24]  source:gemma4
    $44  #7 solder         -1.13°C 🧊       ~44 used:0 [43]  source:gemma4

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1673 🥳 153 ⏱️ 0:23:58.105244

🤔 154 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 49 chat prompts
🤖 49 gemma4:12b replies
😱   1 🔥   2 🥵   5 😎  21 🥶 104 🧊  20

      $1 #154 incompatible     100.00°C 🥳 1000‰ ~134 used:0  [133]  source:gemma4
      $2 #115 incompatibilité   51.23°C 😱  999‰   ~1 used:51 [0]    source:gemma4
      $3 #149 inconciliable     49.45°C 🔥  998‰   ~4 used:15 [3]    source:gemma4
      $4 #137 contradictoire    47.53°C 🔥  995‰   ~3 used:14 [2]    source:gemma4
      $5 #111 contradiction     41.21°C 🥵  987‰   ~9 used:10 [8]    source:gemma4
      $6 #153 antagoniste       40.93°C 🥵  984‰   ~2 used:1  [1]    source:gemma4
      $7 #142 irréconciliable   39.81°C 🥵  981‰   ~5 used:2  [4]    source:gemma4
      $8 #110 antinomie         33.96°C 🥵  943‰   ~8 used:6  [7]    source:gemma4
      $9 #101 antagonisme       33.55°C 🥵  937‰   ~7 used:5  [6]    source:gemma4
     $10 #117 paradoxe          31.76°C 🥵  900‰   ~6 used:3  [5]    source:gemma4
     $11 #126 dualité           31.73°C 😎  898‰  ~10 used:0  [9]    source:gemma4
     $12 #106 incohérence       31.61°C 😎  896‰  ~25 used:2  [24]   source:gemma4
     $31  #95 fragmentation     21.39°C 🥶        ~38 used:0  [37]   source:gemma4
    $135  #30 prestance         -0.06°C 🧊       ~135 used:0  [134]  source:gemma4
