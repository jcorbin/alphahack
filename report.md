# 2026-09-05

- 🔗 spaceword.org 🧩 2026-09-04 🏁 score 2168 ranked 41.7% 141/338 ⏱️ 1:58:39.754165
- 🔗 wordgrid 🧩 #826 🟪 rarity:0.1 ⏱️ 0:04:27.515115
- 🔗 alfagok.diginaut.net 🧩 #672 🥳 20 ⏱️ 0:00:30.177636
- 🔗 alphaguess.com 🧩 #1139 🥳 30 ⏱️ 0:00:33.236449
- 🔗 dontwordle.com 🧩 #1565 🥳 6 ⏱️ 0:01:27.997216
- 🔗 dictionary.com hurdle 🧩 #1708 🥳 17 ⏱️ 0:02:35.634845
- 🔗 Quordle Classic 🧩 #1685 🥳 score:23 ⏱️ 0:01:20.436316
- 🔗 Octordle Classic 🧩 #1685 🥳 score:62 ⏱️ 0:01:59.540381
- 🔗 Sedecordle Classic 🧩 #1665 🥳 score:42 ⏱️ 0:02:54.164482
- 🔗 squareword.org 🧩 #1678 🥳 8 ⏱️ 0:02:38.958908
- 🔗 cemantle.certitudes.org 🧩 #1615 🥳 124 ⏱️ 0:02:09.694106
- 🔗 cemantix.certitudes.org 🧩 #1648 🥳 291 ⏱️ 0:03:57.182360

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
































# [spaceword.org](spaceword.org) 🧩 2026-09-04 🏁 score 2168 ranked 41.7% 141/338 ⏱️ 1:58:39.754165

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 141/338

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ N _ O _ _ _ Y _ _   
      _ U _ B E T O O K _   
      _ D E I X I S _ E _   
      _ E _ T _ Z _ _ G _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #826 🟪 rarity:0.1 ⏱️ 0:04:27.515115

📜 3 sessions
🦄 🦄 🌌
🌌 🦄 🦄
🦄 🦄 🌌
Rarity: 0.1 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #672 🥳 20 ⏱️ 0:00:30.177636

🤔 20 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+99681  [ 99681] ex        q4  ? ␅
    @+99681  [ 99681] ex        q5  ? after
    @+111336 [111336] ge        q8  ? ␅
    @+111336 [111336] ge        q9  ? after
    @+120826 [120826] gepunt    q12 ? ␅
    @+120826 [120826] gepunt    q13 ? after
    @+125568 [125568] gezapig   q14 ? ␅
    @+125568 [125568] gezapig   q15 ? after
    @+127729 [127729] glas      q16 ? ␅
    @+127729 [127729] glas      q17 ? after
    @+128740 [128740] goed      q18 ? ␅
    @+128740 [128740] goed      q19 ? it
    @+128740 [128740] goed      done. it
    @+130316 [130316] gracht    q10 ? ␅
    @+130316 [130316] gracht    q11 ? before
    @+149367 [149367] huis      q6  ? ␅
    @+149367 [149367] huis      q7  ? before
    @+199640 [199640] lijk      q0  ? ␅
    @+199640 [199640] lijk      q1  ? after
    @+199640 [199640] lijk      q2  ? ␅
    @+199640 [199640] lijk      q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1139 🥳 30 ⏱️ 0:00:33.236449

🤔 30 attempts
📜 1 sessions

    @       [    0] aa         
    @+23680 [23680] camp       q6  ? ␅
    @+23680 [23680] camp       q7  ? after
    @+35522 [35522] convention q8  ? ␅
    @+35522 [35522] convention q9  ? after
    @+40838 [40838] da         q10 ? ␅
    @+40838 [40838] da         q11 ? after
    @+41163 [41163] dan        q18 ? ␅
    @+41163 [41163] dan        q19 ? after
    @+41346 [41346] darn       q20 ? ␅
    @+41346 [41346] darn       q21 ? after
    @+41448 [41448] dative     q22 ? ␅
    @+41448 [41448] dative     q23 ? after
    @+41460 [41460] daub       q26 ? ␅
    @+41460 [41460] daub       q27 ? after
    @+41476 [41476] daughter   q28 ? ␅
    @+41476 [41476] daughter   q29 ? it
    @+41476 [41476] daughter   done. it
    @+41490 [41490] daunt      q24 ? ␅
    @+41490 [41490] daunt      q25 ? before
    @+41548 [41548] day        q16 ? ␅
    @+41548 [41548] day        q17 ? before
    @+42373 [42373] deco       q14 ? ␅
    @+42373 [42373] deco       q15 ? before
    @+44070 [44070] den        q12 ? ␅
    @+44070 [44070] den        q13 ? before
    @+47378 [47378] dis        q4  ? ␅
    @+47378 [47378] dis        q5  ? before
    @+98147 [98147] mac        q1  ? after
    @+98147 [98147] mac        q2  ? ␅
    @+98147 [98147] mac        q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1565 🥳 6 ⏱️ 0:01:27.997216

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:7346
    ⬜⬜⬜⬜⬜ tried:TOROT n n n n n remain:2239
    ⬜⬜⬜⬜⬜ tried:YUMMY n n n n n remain:927
    ⬜🟨⬜⬜⬜ tried:BEECH n m n n n remain:106
    ⬜⬜🟩⬜🟩 tried:AGAPE n n Y n Y remain:7
    🟩⬜🟩⬜🟩 tried:SWALE Y n Y n Y remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1708 🥳 17 ⏱️ 0:02:35.634845

📜 1 sessions
💰 score: 9900

    4/6
    LARES ⬜⬜⬜⬜🟨
    NOISY ⬜🟨⬜🟨⬜
    SPOUT 🟩🟨🟩⬜⬜
    SCOOP 🟩🟩🟩🟩🟩
    4/6
    SCOOP ⬜⬜⬜⬜⬜
    LATER ⬜⬜⬜🟨🟨
    FIERY ⬜⬜🟩🟩⬜
    WHERE 🟩🟩🟩🟩🟩
    4/6
    WHERE ⬜⬜⬜⬜🟩
    ANISE ⬜🟨🟨⬜🟩
    DINGE ⬜🟩🟩⬜🟩
    MINCE 🟩🟩🟩🟩🟩
    4/6
    MINCE ⬜⬜⬜⬜⬜
    BOART 🟩⬜🟨⬜⬜
    BALDS 🟩🟨⬜⬜⬜
    BYWAY 🟩🟩🟩🟩🟩
    Final 1/2
    CHEAP 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1685 🥳 score:23 ⏱️ 0:01:20.436316

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. GNASH attempts:5 score:5
2. GEEKY attempts:3 score:3
3. WHELP attempts:7 score:7
4. PUTTY attempts:8 score:8

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1685 🥳 score:62 ⏱️ 0:01:59.540381

📜 1 sessions

Octordle Classic

1. MOODY attempts:12 score:12
2. GREAT attempts:8 score:8
3. PLANE attempts:3 score:3
4. SAINT attempts:4 score:4
5. SHAPE attempts:9 score:9
6. QUELL attempts:6 score:6
7. EATEN attempts:13 score:13
8. RECUT attempts:7 score:7

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1665 🥳 score:42 ⏱️ 0:02:54.164482

📜 1 sessions

Sedecordle Classic sedecordle.com

1. BICEP attempts:4 score:0
2. BITTY attempts:5 score:4
3. BEACH attempts:6 score:0
4. PRICE attempts:7 score:6
5. FJORD attempts:8 score:0
6. SHYLY attempts:9 score:8
7. SWIFT attempts:12 score:1
8. COVET attempts:11 score:2
9. TAMER attempts:13 score:1
10. EMBED attempts:14 score:3
11. RUMOR attempts:10 score:1
12. DANCE attempts:15 score:0
13. PLIED attempts:16 score:1
14. EXACT attempts:17 score:6
15. CAUSE attempts:18 score:1
16. CRUEL attempts:19 score:8

# [squareword.org](squareword.org) 🧩 #1678 🥳 8 ⏱️ 0:02:38.958908

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C L A S S
    R A D O N
    E X I L E
    P E E V E
    T R U E R

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1615 🥳 124 ⏱️ 0:02:09.694106

🤔 125 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 40 chat prompts
🤖 40 dolphin3:latest replies
🔥  2 🥵 12 😎 21 🥶 79 🧊 10

      $1 #125 boost           100.00°C 🥳 1000‰ ~115 used:0  [114]  source:dolphin3
      $2 #122 enhance          53.54°C 🔥  993‰   ~1 used:2  [0]    source:dolphin3
      $3 #102 reinvigorate     53.50°C 🔥  992‰   ~6 used:18 [5]    source:dolphin3
      $4 #103 rejuvenate       52.38°C 🥵  989‰  ~14 used:8  [13]   source:dolphin3
      $5 #114 invigorate       52.16°C 🥵  988‰  ~12 used:3  [11]   source:dolphin3
      $6 #121 stimulate        51.69°C 🥵  987‰   ~7 used:2  [6]    source:dolphin3
      $7  #94 revive           50.33°C 🥵  986‰  ~13 used:4  [12]   source:dolphin3
      $8 #110 energize         49.91°C 🥵  984‰   ~8 used:2  [7]    source:dolphin3
      $9 #104 revitalize       48.64°C 🥵  983‰   ~9 used:2  [8]    source:dolphin3
     $10 #124 augment          45.42°C 🥵  978‰   ~2 used:0  [1]    source:dolphin3
     $11 #106 rekindle         42.85°C 🥵  963‰  ~10 used:2  [9]    source:dolphin3
     $16 #108 replenish        36.82°C 😎  895‰  ~15 used:0  [14]   source:dolphin3
     $37 #111 activate         19.93°C 🥶        ~44 used:0  [43]   source:dolphin3
    $116  #61 delightful       -0.47°C 🧊       ~116 used:0  [115]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1648 🥳 291 ⏱️ 0:03:57.182360

🤔 292 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 54 chat prompts
🤖 54 dolphin3:latest replies
🔥   4 🥵   8 😎  48 🥶 183 🧊  48

      $1 #292 contestation       100.00°C 🥳 1000‰ ~244 used:0  [243]  source:dolphin3
      $2 #244 opposition          54.01°C 🔥  998‰   ~4 used:8  [3]    source:dolphin3
      $3 #273 protestation        52.97°C 🔥  997‰   ~1 used:1  [0]    source:dolphin3
      $4 #263 contestataire       49.44°C 🔥  995‰   ~2 used:0  [1]    source:dolphin3
      $5 #288 conflit             46.19°C 🔥  991‰   ~3 used:0  [2]    source:dolphin3
      $6 #289 contradiction       39.92°C 🥵  971‰   ~5 used:0  [4]    source:dolphin3
      $7 #198 partisan            38.74°C 🥵  965‰  ~45 used:12 [44]   source:dolphin3
      $8 #190 politique           35.85°C 🥵  935‰  ~46 used:13 [45]   source:dolphin3
      $9 #207 réformiste          35.60°C 🥵  930‰   ~8 used:4  [7]    source:dolphin3
     $10 #268 grève               35.42°C 🥵  926‰   ~6 used:0  [5]    source:dolphin3
     $11 #168 décision            35.22°C 🥵  922‰  ~10 used:9  [9]    source:dolphin3
     $14 #166 autorité            33.30°C 😎  873‰  ~47 used:2  [46]   source:dolphin3
     $62 #140 statut              24.37°C 🥶        ~68 used:0  [67]   source:dolphin3
    $245  #39 scène               -0.14°C 🧊       ~245 used:0  [244]  source:dolphin3
