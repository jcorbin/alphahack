# 2026-08-16

- 🔗 spaceword.org 🧩 2026-08-15 🏁 score 2158 ranked 66.2% 208/314 ⏱️ 0:02:50.316701
- 🔗 wordgrid 🧩 #806 🟪 rarity:0.22 ⏱️ 0:02:18.566009
- 🔗 alfagok.diginaut.net 🧩 #652 🥳 38 ⏱️ 0:00:49.157272
- 🔗 alphaguess.com 🧩 #1119 🥳 24 ⏱️ 0:00:28.248017
- 🔗 dontwordle.com 🧩 #1545 🥳 6 ⏱️ 0:01:24.623977
- 🔗 dictionary.com hurdle 🧩 #1688 🥳 19 ⏱️ 0:06:29.039292
- 🔗 Quordle Classic 🧩 #1665 🥳 score:25 ⏱️ 0:01:50.860635
- 🔗 Octordle Classic 🧩 #1665 🥳 score:52 ⏱️ 0:01:47.304479
- 🔗 Sedecordle Classic 🧩 #1645 🥳 score:39 ⏱️ 0:02:36.372901
- 🔗 squareword.org 🧩 #1658 🥳 8 ⏱️ 0:02:28.876332
- 🔗 cemantle.certitudes.org 🧩 #1595 🥳 118 ⏱️ 0:00:56.114034
- 🔗 cemantix.certitudes.org 🧩 #1628 🥳 157 ⏱️ 0:16:37.493777

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












# [spaceword.org](spaceword.org) 🧩 2026-08-15 🏁 score 2158 ranked 66.2% 208/314 ⏱️ 0:02:50.316701

📜 2 sessions
- tiles: 21/21
- score: 2158 bonus: +58
- rank: 208/314

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ T A G _ L _ _   
      _ _ _ O _ _ _ O _ _   
      _ _ _ X _ _ _ W _ _   
      _ _ R E Q U I N _ _   
      _ _ _ M _ _ _ _ _ _   
      _ _ _ I _ _ _ _ _ _   
      _ _ H A O L E _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #806 🟪 rarity:0.22 ⏱️ 0:02:18.566009

📜 3 sessions
🌌 🌌 🌌
🌌 🦄 🦄
🌌 🦄 🌌
Rarity: 0.22 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #652 🥳 38 ⏱️ 0:00:49.157272

🤔 38 attempts
📜 1 sessions

    @       [    0] &-teken   
    @+24883 [24883] bad       q10 ? ␅
    @+24883 [24883] bad       q11 ? after
    @+37329 [37329] bescherm  q12 ? ␅
    @+37329 [37329] bescherm  q13 ? after
    @+43033 [43033] bij       q14 ? ␅
    @+43033 [43033] bij       q15 ? after
    @+43791 [43791] bijplaats q20 ? ␅
    @+43791 [43791] bijplaats q21 ? after
    @+44172 [44172] bijvul    q22 ? ␅
    @+44172 [44172] bijvul    q23 ? after
    @+44333 [44333] biljart   q24 ? ␅
    @+44333 [44333] biljart   q25 ? after
    @+44442 [44442] bimbam    q28 ? ␅
    @+44442 [44442] bimbam    q29 ? after
    @+44455 [44455] bind      q30 ? ␅
    @+44455 [44455] bind      q31 ? after
    @+44461 [44461] binden    q36 ? ␅
    @+44461 [44461] binden    q37 ? it
    @+44461 [44461] binden    done. it
    @+44472 [44472] binding   q34 ? ␅
    @+44472 [44472] binding   q35 ? before
    @+44500 [44500] bindsel   q32 ? ␅
    @+44500 [44500] bindsel   q33 ? before
    @+44549 [44549] binnen    q18 ? ␅
    @+44549 [44549] binnen    q19 ? before
    @+46420 [46420] blief     q16 ? ␅
    @+46420 [46420] blief     q17 ? before
    @+49811 [49811] boks      q8  ? ␅
    @+49811 [49811] boks      q9  ? before
    @+99691 [99691] ex        q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1119 🥳 24 ⏱️ 0:00:28.248017

🤔 24 attempts
📜 1 sessions

    @        [     0] aa       
    @+1      [     1] aah      
    @+2      [     2] aahed    
    @+3      [     3] aahing   
    @+98147  [ 98147] mac      q0  ? ␅
    @+98147  [ 98147] mac      q1  ? after
    @+98147  [ 98147] mac      q2  ? ␅
    @+98147  [ 98147] mac      q3  ? after
    @+147311 [147311] rho      q4  ? ␅
    @+147311 [147311] rho      q5  ? after
    @+148014 [148014] risus    q16 ? ␅
    @+148014 [148014] risus    q17 ? after
    @+148185 [148185] rob      q20 ? ␅
    @+148185 [148185] rob      q21 ? after
    @+148261 [148261] rock     q22 ? ␅
    @+148261 [148261] rock     q23 ? it
    @+148261 [148261] rock     done. it
    @+148361 [148361] roentgen q18 ? ␅
    @+148361 [148361] roentgen q19 ? before
    @+148717 [148717] rose     q14 ? ␅
    @+148717 [148717] rose     q15 ? before
    @+150207 [150207] sal      q12 ? ␅
    @+150207 [150207] sal      q13 ? before
    @+153311 [153311] sea      q10 ? ␅
    @+153311 [153311] sea      q11 ? before
    @+159593 [159593] slug     q8  ? ␅
    @+159593 [159593] slug     q9  ? before
    @+171911 [171911] tag      q6  ? ␅
    @+171911 [171911] tag      q7  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1545 🥳 6 ⏱️ 0:01:24.623977

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:CEDED n n n n n remain:5104
    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:2502
    ⬜⬜⬜⬜⬜ tried:SMUTS n n n n n remain:381
    ⬜⬜⬜🟨⬜ tried:GHYLL n n n m n remain:29
    ⬜🟨🟨⬜⬜ tried:FLAVA n m m n n remain:6
    🟨⬜🟩🟨⬜ tried:AZLON m n Y m n remain:1

    Undos used: 4

      1 words remaining
    x 6 unused letters
    = 6 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1688 🥳 19 ⏱️ 0:06:29.039292

📜 1 sessions
💰 score: 9700

    4/6
    STARE ⬜🟨⬜⬜⬜
    UNITY ⬜⬜🟨🟨⬜
    OPTIC 🟨⬜🟨🟩🟩
    TOXIC 🟩🟩🟩🟩🟩
    3/6
    TOXIC ⬜🟨⬜⬜🟨
    ORCAS 🟨🟨🟩🟨⬜
    MACRO 🟩🟩🟩🟩🟩
    5/6
    MACRO ⬜⬜⬜🟩🟨
    TOURS 🟨🟨⬜🟩🟨
    SKORT 🟩⬜🟩🟩🟩
    PHONE ⬜⬜🟩🟨⬜
    SNORT 🟩🟩🟩🟩🟩
    5/6
    SNORT ⬜⬜⬜🟨🟨
    IRATE ⬜🟨🟨🟨🟨
    ALTER 🟨⬜🟩🟩🟩
    CAGED 🟩🟩⬜🟩⬜
    ????? 🟩🟩🟩🟩🟩
    Final 2/2
    LAWNY 🟨🟨⬜⬜⬜
    POLAR 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1665 🥳 score:25 ⏱️ 0:01:50.860635

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. BLIND attempts:6 score:6
2. FROTH attempts:7 score:7
3. FLOUR attempts:8 score:8
4. ESTER attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1665 🥳 score:52 ⏱️ 0:01:47.304479

📜 1 sessions

Octordle Classic

1. BRIAR attempts:3 score:3
2. OMEGA attempts:7 score:7
3. LOGIC attempts:6 score:6
4. NOTCH attempts:9 score:9
5. WHOLE attempts:10 score:10
6. ALONG attempts:8 score:8
7. CELLO attempts:4 score:4
8. CIVIL attempts:5 score:5

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1645 🥳 score:39 ⏱️ 0:02:36.372901

📜 1 sessions

Sedecordle Classic sedecordle.com

1. MATEY attempts:7 score:0
2. CREPT attempts:14 score:7
3. FULLY attempts:18 score:1
4. TOXIC attempts:15 score:8
5. MOTOR attempts:5 score:0
6. HOIST attempts:3 score:5
7. RIGHT attempts:4 score:0
8. HAIRY attempts:6 score:4
9. GAUNT attempts:8 score:0
10. TENTH attempts:16 score:8
11. TROVE attempts:10 score:1
12. SAVOY attempts:9 score:0
13. HORDE attempts:11 score:1
14. ALIBI attempts:17 score:1
15. MERRY attempts:12 score:1
16. VAGUE attempts:13 score:2

# [squareword.org](squareword.org) 🧩 #1658 🥳 8 ⏱️ 0:02:28.876332

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟩 🟨 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P A T S
    A R G O T
    G U A N O
    E N T E R
    S E E D Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1595 🥳 118 ⏱️ 0:00:56.114034

🤔 119 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 13 chat prompts
🤖 13 dolphin3:latest replies
🔥  1 🥵  6 😎 15 🥶 89 🧊  7

      $1 #119 vacation       100.00°C 🥳 1000‰ ~112 used:0 [111]  source:dolphin3
      $2 #118 travel          44.87°C 🔥  990‰   ~1 used:0 [0]    source:dolphin3
      $3 #113 resort          43.82°C 🥵  985‰   ~2 used:0 [1]    source:dolphin3
      $4  #69 backpacking     43.03°C 🥵  982‰   ~5 used:5 [4]    source:dolphin3
      $5  #29 camping         40.93°C 🥵  972‰   ~7 used:6 [6]    source:dolphin3
      $6  #26 adventure       36.42°C 🥵  946‰   ~6 used:5 [5]    source:dolphin3
      $7  #98 tour            35.17°C 🥵  933‰   ~3 used:1 [2]    source:dolphin3
      $8  #25 hiking          33.10°C 🥵  904‰   ~4 used:4 [3]    source:dolphin3
      $9 #117 tourism         30.77°C 😎  867‰   ~8 used:0 [7]    source:dolphin3
     $10 #114 scenic          29.26°C 😎  834‰   ~9 used:0 [8]    source:dolphin3
     $11  #50 solitude        29.25°C 😎  833‰  ~10 used:0 [9]    source:dolphin3
     $12  #71 scenery         28.90°C 😎  823‰  ~11 used:0 [10]   source:dolphin3
     $24  #48 restorative     19.25°C 🥶        ~25 used:0 [24]   source:dolphin3
    $113  #70 challenge       -0.60°C 🧊       ~113 used:0 [112]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1628 🥳 157 ⏱️ 0:16:37.493777

🤔 158 attempts
📜 1 sessions
🫧 17 chat sessions
⁉️ 92 chat prompts
🤖 92 dolphin3:latest replies
🔥  2 🥵 10 😎 24 🥶 94 🧊 27

      $1 #158 certitude        100.00°C 🥳 1000‰ ~131 used:0   [130]  source:dolphin3
      $2 #154 conviction        54.50°C 🔥  996‰   ~1 used:2   [0]    source:dolphin3
      $3  #58 intuition         53.23°C 🔥  995‰  ~25 used:110 [24]   source:dolphin3
      $4 #117 supposition       50.28°C 🥵  985‰  ~26 used:11  [25]   source:dolphin3
      $5 #150 raison            49.31°C 🥵  982‰   ~2 used:1   [1]    source:dolphin3
      $6 #149 pensée            49.18°C 🥵  981‰   ~3 used:0   [2]    source:dolphin3
      $7  #70 pressentiment     49.10°C 🥵  979‰  ~35 used:39  [34]   source:dolphin3
      $8 #120 hypothèse         45.48°C 🥵  953‰   ~6 used:6   [5]    source:dolphin3
      $9  #55 conscience        45.41°C 🥵  952‰  ~29 used:20  [28]   source:dolphin3
     $10 #111 preuve            43.88°C 🥵  929‰   ~5 used:4   [4]    source:dolphin3
     $11  #68 sentiment         43.46°C 🥵  925‰  ~27 used:11  [26]   source:dolphin3
     $14 #113 indiscernable     42.15°C 😎  895‰   ~7 used:0   [6]    source:dolphin3
     $38 #127 logique           29.88°C 🥶        ~46 used:0   [45]   source:dolphin3
    $132  #25 petit             -0.04°C 🧊       ~132 used:0   [131]  source:dolphin3
