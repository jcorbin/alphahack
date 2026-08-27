# 2026-08-28

- 🔗 spaceword.org 🧩 2026-08-27 🏁 score 2168 ranked 24.5% 78/318 ⏱️ 0:30:54.644493
- 🔗 wordgrid 🧩 #818 🟪 rarity:0.11 ⏱️ 0:02:37.569724
- 🔗 alfagok.diginaut.net 🧩 #664 🥳 32 ⏱️ 0:00:44.532465
- 🔗 alphaguess.com 🧩 #1131 🥳 30 ⏱️ 0:00:40.694022
- 🔗 dontwordle.com 🧩 #1557 😳 6 ⏱️ 0:01:23.636329
- 🔗 dictionary.com hurdle 🧩 #1700 🥳 18 ⏱️ 0:02:56.256992
- 🔗 Quordle Classic 🧩 #1677 🥳 score:18 ⏱️ 0:01:14.630576
- 🔗 Octordle Classic 🧩 #1677 🥳 score:67 ⏱️ 0:04:19.014508
- 🔗 Sedecordle Classic 🧩 #1657 🥳 score:42 ⏱️ 0:03:35.205171
- 🔗 squareword.org 🧩 #1670 🥳 7 ⏱️ 0:03:03.636371
- 🔗 cemantle.certitudes.org 🧩 #1607 🥳 561 ⏱️ 0:46:27.711959
- 🔗 cemantix.certitudes.org 🧩 #1640 🥳 395 ⏱️ 0:22:50.162928

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







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #781 🟪 rarity:0.15 ⏱️ 0:03:50.236694

📜 2 sessions
🌌 🦄 🦄
🌌 🦄 🦄
🌌 🌌 🌌
Rarity: 0.15 🟪


# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #-1 ❗ rarity:nan ⏱️ 0:05:19.095498

📜 2 sessions
🌌 🦄 🌌
🌌 🦄 🌌
🌌 🦄 🌌
Rarity: nan ❗







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #788 🟪 rarity:0.29 ⏱️ 0:03:24.033720

📜 2 sessions
🦄 🦄 🌌
🦄 🦄 🦄
🌌 🦄 🌌
Rarity: 0.29 🟪


# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #789 🟪 rarity:0.23 ⏱️ 0:02:56.015327

📜 2 sessions
🌌 🌌 🌌
🦄 🦄 🌌
🦄 🦄 🦄
Rarity: 0.23 🟪







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #795 🟪 rarity:0.27 ⏱️ 0:03:44.973967

📜 2 sessions
🦄 🌌 🌌
🌌 🌌 🌌
🦄 🦄 🌌
Rarity: 0.27 🟪
























# [spaceword.org](spaceword.org) 🧩 2026-08-27 🏁 score 2168 ranked 24.5% 78/318 ⏱️ 0:30:54.644493

📜 5 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 78/318

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ C _ _ _ _ J O E _   
      _ O _ R I B I E R _   
      _ Z _ _ _ U N _ U _   
      _ Y A I R D _ _ V _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #818 🟪 rarity:0.11 ⏱️ 0:02:37.569724

📜 3 sessions
🌌 🦄 🦄
🦄 🌌 🌌
🌌 🦄 🦄
Rarity: 0.11 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #664 🥳 32 ⏱️ 0:00:44.532465

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+49809  [ 49809] boks         q8  ? ␅
    @+49809  [ 49809] boks         q9  ? after
    @+74712  [ 74712] dc           q10 ? ␅
    @+74712  [ 74712] dc           q11 ? after
    @+80844  [ 80844] dijk         q14 ? ␅
    @+80844  [ 80844] dijk         q15 ? after
    @+82360  [ 82360] dj           q18 ? ␅
    @+82360  [ 82360] dj           q19 ? after
    @+82445  [ 82445] do           q20 ? ␅
    @+82445  [ 82445] do           q21 ? after
    @+82624  [ 82624] documentaire q26 ? ␅
    @+82624  [ 82624] documentaire q27 ? after
    @+82717  [ 82717] dode         q28 ? ␅
    @+82717  [ 82717] dode         q29 ? after
    @+82742  [ 82742] doden        q30 ? ␅
    @+82742  [ 82742] doden        q31 ? it
    @+82742  [ 82742] doden        done. it
    @+82809  [ 82809] dodijn       q24 ? ␅
    @+82809  [ 82809] dodijn       q25 ? before
    @+83174  [ 83174] dog          q22 ? ␅
    @+83174  [ 83174] dog          q23 ? before
    @+83950  [ 83950] donor        q16 ? ␅
    @+83950  [ 83950] donor        q17 ? before
    @+87170  [ 87170] draag        q12 ? ␅
    @+87170  [ 87170] draag        q13 ? before
    @+99689  [ 99689] ex           q6  ? ␅
    @+99689  [ 99689] ex           q7  ? before
    @+199648 [199648] lijk         q3  ? after
    @+199648 [199648] lijk         q4  ? ␅
    @+199648 [199648] lijk         q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1131 🥳 30 ⏱️ 0:00:40.694022

🤔 30 attempts
📜 1 sessions

    @        [     0] aa     
    @+98147  [ 98147] mac    q0  ? ␅
    @+98147  [ 98147] mac    q1  ? after
    @+98147  [ 98147] mac    q2  ? ␅
    @+98147  [ 98147] mac    q3  ? after
    @+98147  [ 98147] mac    q4  ? ␅
    @+98147  [ 98147] mac    q5  ? after
    @+147311 [147311] rho    q6  ? ␅
    @+147311 [147311] rho    q7  ? after
    @+153311 [153311] sea    q12 ? ␅
    @+153311 [153311] sea    q13 ? after
    @+156448 [156448] shit   q14 ? ␅
    @+156448 [156448] shit   q15 ? after
    @+158017 [158017] sine   q16 ? ␅
    @+158017 [158017] sine   q17 ? after
    @+158796 [158796] sky    q18 ? ␅
    @+158796 [158796] sky    q19 ? after
    @+159192 [159192] sleigh q20 ? ␅
    @+159192 [159192] sleigh q21 ? after
    @+159379 [159379] slips  q22 ? ␅
    @+159379 [159379] slips  q23 ? after
    @+159479 [159479] slop   q24 ? ␅
    @+159479 [159479] slop   q25 ? after
    @+159535 [159535] slough q26 ? ␅
    @+159535 [159535] slough q27 ? after
    @+159549 [159549] slow   q28 ? ␅
    @+159549 [159549] slow   q29 ? it
    @+159549 [159549] slow   done. it
    @+159593 [159593] slug   q10 ? ␅
    @+159593 [159593] slug   q11 ? before
    @+171911 [171911] tag    q9  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1557 😳 6 ⏱️ 0:01:23.636329

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:7266
    ⬜⬜⬜⬜⬜ tried:SULUS n n n n n remain:2095
    ⬜⬜⬜⬜⬜ tried:MYRRH n n n n n remain:448
    ⬜🟨⬜⬜⬜ tried:CODON n m n n n remain:9
    ⬜🟨🟨⬜⬜ tried:FEOFF n m m n n remain:3
    🟩🟩🟩🟩🟩 tried:OVATE Y Y Y Y Y remain:0

    Undos used: 3

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1700 🥳 18 ⏱️ 0:02:56.256992

📜 1 sessions
💰 score: 9800

    4/6
    PANES ⬜🟨⬜🟨🟨
    TESLA ⬜🟨🟨⬜🟨
    SHARE 🟩⬜🟩🟩🟩
    SCARE 🟩🟩🟩🟩🟩
    5/6
    SCARE ⬜⬜🟨🟨⬜
    RADON 🟨🟩⬜⬜⬜
    KAFIR ⬜🟩⬜⬜🟨
    GARTH ⬜🟩🟩🟩⬜
    PARTY 🟩🟩🟩🟩🟩
    4/6
    PARTY ⬜⬜🟨🟨⬜
    TIERS 🟨⬜🟨🟨⬜
    OUTER 🟩⬜🟨🟩🟩
    OTHER 🟩🟩🟩🟩🟩
    3/6
    OTHER 🟨⬜🟨🟨⬜
    HELOS 🟩🟨⬜🟨🟨
    HOUSE 🟩🟩🟩🟩🟩
    Final 2/2
    AUDIO 🟩🟨🟨⬜🟨
    ALOUD 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1677 🥳 score:18 ⏱️ 0:01:14.630576

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. WAIST attempts:6 score:6
2. EDICT attempts:5 score:5
3. BONUS attempts:3 score:3
4. DEUCE attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1677 🥳 score:67 ⏱️ 0:04:19.014508

📜 1 sessions

Octordle Classic

1. SUING attempts:9 score:9
2. STOOD attempts:3 score:3
3. BROWN attempts:10 score:10
4. STUNK attempts:11 score:11
5. PRIED attempts:12 score:12
6. RATIO attempts:5 score:5
7. WEIRD attempts:4 score:4
8. POUTY attempts:13 score:13

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1657 🥳 score:42 ⏱️ 0:03:35.205171

📜 1 sessions

Sedecordle Classic sedecordle.com

1. SLEEK attempts:3 score:0
2. DRIED attempts:14 score:3
3. NOISE attempts:4 score:0
4. CLONE attempts:5 score:4
5. INLAY attempts:9 score:0
6. NEIGH attempts:6 score:9
7. SAVVY attempts:15 score:1
8. FLOAT attempts:10 score:5
9. STINT attempts:17 score:1
10. FECAL attempts:8 score:7
11. CRATE attempts:11 score:1
12. ROWER attempts:19 score:1
13. OLDER attempts:7 score:0
14. PAYER attempts:16 score:7
15. OMEGA attempts:12 score:1
16. MARRY attempts:20 score:2

# [squareword.org](squareword.org) 🧩 #1670 🥳 7 ⏱️ 0:03:03.636371

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟨
    🟩 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P L A T
    C R E D O
    R I G O R
    A D A P T
    M E L T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1607 🥳 561 ⏱️ 0:46:27.711959

🤔 562 attempts
📜 1 sessions
🫧 52 chat sessions
⁉️ 268 chat prompts
🤖 8 llama3.2:latest replies
🤖 1 qwen3.5:27b replies
🤖 215 dolphin3:latest replies
🤖 27 ornith-1.5:35b replies
🤖 16 lfm2.5:latest replies
😱   1 🔥   2 🥵  25 😎 104 🥶 400 🧊  29

      $1 #562 jean            100.00°C 🥳 1000‰ ~533 used:0   [532]  source:llama3  
      $2 #481 denim            69.98°C 😱  999‰   ~1 used:108 [0]    source:dolphin3
      $3 #528 chambray         55.03°C 🔥  996‰   ~2 used:27  [1]    source:dolphin3
      $4 #162 chic             52.04°C 🔥  992‰ ~119 used:215 [118]  source:dolphin3
      $5 #356 camisole         50.66°C 🥵  987‰ ~123 used:47  [122]  source:dolphin3
      $6 #477 pants            50.55°C 🥵  986‰   ~7 used:4   [6]    source:dolphin3
      $7 #189 couture          50.21°C 🥵  982‰ ~124 used:60  [123]  source:dolphin3
      $8 #422 blouse           49.50°C 🥵  979‰  ~21 used:8   [20]   source:dolphin3
      $9 #358 corset           48.38°C 🥵  975‰  ~22 used:8   [21]   source:dolphin3
     $10 #478 cardigan         48.37°C 🥵  974‰   ~8 used:4   [7]    source:dolphin3
     $11 #355 bra              48.27°C 🥵  973‰  ~23 used:8   [22]   source:dolphin3
     $30 #480 corduroy         42.02°C 😎  897‰  ~24 used:0   [23]   source:dolphin3
    $134 #440 collar           27.17°C 🥶       ~137 used:0   [136]  source:dolphin3
    $534   #5 quantum          -0.20°C 🧊       ~534 used:0   [533]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1640 🥳 395 ⏱️ 0:22:50.162928

🤔 396 attempts
📜 1 sessions
🫧 30 chat sessions
⁉️ 155 chat prompts
🤖 155 dolphin3:latest replies
🔥   1 🥵  11 😎  72 🥶 211 🧊 100

      $1 #396 handicapé           100.00°C 🥳 1000‰ ~296 used:0  [295]  source:dolphin3
      $2 #379 accessibilité        44.73°C 🔥  991‰   ~1 used:12 [0]    source:dolphin3
      $3 #234 insertion            38.95°C 🥵  985‰  ~81 used:75 [80]   source:dolphin3
      $4 #368 réinsertion          35.41°C 🥵  970‰   ~5 used:7  [4]    source:dolphin3
      $5 #298 accueillir           33.00°C 🥵  959‰  ~73 used:28 [72]   source:dolphin3
      $6 #285 solidarité           32.70°C 🥵  954‰  ~27 used:20 [26]   source:dolphin3
      $7 #325 accueil              32.15°C 🥵  951‰  ~25 used:11 [24]   source:dolphin3
      $8  #53 association          31.95°C 🥵  949‰  ~82 used:75 [81]   source:dolphin3
      $9 #108 emploi               30.67°C 🥵  936‰  ~77 used:34 [76]   source:dolphin3
     $10 #356 accès                30.41°C 🥵  930‰   ~3 used:4  [2]    source:dolphin3
     $11 #381 accessible           28.88°C 🥵  916‰   ~4 used:4  [3]    source:dolphin3
     $14 #359 foyer                27.65°C 😎  898‰   ~6 used:0  [5]    source:dolphin3
     $86  #68 ligue                13.83°C 🥶        ~90 used:0  [89]   source:dolphin3
    $297 #158 talent               -0.01°C 🧊       ~297 used:0  [296]  source:dolphin3
