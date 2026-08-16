# 2026-08-17

- 🔗 spaceword.org 🧩 2026-08-16 🏁 score 2168 ranked 43.6% 136/312 ⏱️ 4:56:15.929069
- 🔗 wordgrid 🧩 #807 🟪 rarity:0.1 ⏱️ 0:05:45.629623
- 🔗 alfagok.diginaut.net 🧩 #653 🥳 18 ⏱️ 0:00:28.980781
- 🔗 alphaguess.com 🧩 #1120 🥳 34 ⏱️ 0:00:35.512797
- 🔗 dontwordle.com 🧩 #1546 🥳 6 ⏱️ 0:02:05.458868
- 🔗 dictionary.com hurdle 🧩 #1689 🥳 20 ⏱️ 0:05:16.214347
- 🔗 Quordle Classic 🧩 #1666 🥳 score:26 ⏱️ 0:01:31.600048
- 🔗 Octordle Classic 🧩 #1666 🥳 score:54 ⏱️ 0:01:42.672062
- 🔗 Sedecordle Classic 🧩 #1646 🥳 score:41 ⏱️ 0:02:35.096237
- 🔗 squareword.org 🧩 #1659 🥳 7 ⏱️ 0:01:50.607000
- 🔗 cemantle.certitudes.org 🧩 #1596 🥳 189 ⏱️ 0:02:17.162562
- 🔗 cemantix.certitudes.org 🧩 #1629 🥳 57 ⏱️ 0:01:07.185474

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













# [spaceword.org](spaceword.org) 🧩 2026-08-16 🏁 score 2168 ranked 43.6% 136/312 ⏱️ 4:56:15.929069

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 136/312

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ J _ L I V E L Y _   
      _ E _ O _ I _ _ E _   
      _ H A W I N G _ A _   
      _ U T S _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #807 🟪 rarity:0.1 ⏱️ 0:05:45.629623

📜 2 sessions
🦄 🦄 🌌
🌌 🦄 🌌
🌌 🦄 🌌
Rarity: 0.1 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #653 🥳 18 ⏱️ 0:00:28.980781

🤔 18 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199548 [199548] lij       q0  ? ␅
    @+199548 [199548] lij       q1  ? after
    @+199548 [199548] lij       q2  ? ␅
    @+199548 [199548] lij       q3  ? after
    @+247603 [247603] op        q6  ? ␅
    @+247603 [247603] op        q7  ? after
    @+260483 [260483] pater     q10 ? ␅
    @+260483 [260483] pater     q11 ? after
    @+266934 [266934] plomp     q12 ? ␅
    @+266934 [266934] plomp     q13 ? after
    @+270007 [270007] pot       q14 ? ␅
    @+270007 [270007] pot       q15 ? after
    @+271668 [271668] prijs     q16 ? ␅
    @+271668 [271668] prijs     q17 ? it
    @+271668 [271668] prijs     done. it
    @+273400 [273400] proef     q8  ? ␅
    @+273400 [273400] proef     q9  ? before
    @+299514 [299514] schrok    q4  ? ␅
    @+299514 [299514] schrok    q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1120 🥳 34 ⏱️ 0:00:35.512797

🤔 34 attempts
📜 1 sessions

    @       [    0] aa         
    @+47378 [47378] dis        q4  ? ␅
    @+47378 [47378] dis        q5  ? after
    @+60017 [60017] eyewitness q8  ? ␅
    @+60017 [60017] eyewitness q9  ? after
    @+66309 [66309] free       q10 ? ␅
    @+66309 [66309] free       q11 ? after
    @+67084 [67084] fuck       q16 ? ␅
    @+67084 [67084] fuck       q17 ? after
    @+67264 [67264] fumarates  q20 ? ␅
    @+67264 [67264] fumarates  q21 ? after
    @+67331 [67331] fund       q22 ? ␅
    @+67331 [67331] fund       q23 ? after
    @+67386 [67386] fungo      q24 ? ␅
    @+67386 [67386] fungo      q25 ? after
    @+67402 [67402] funk       q26 ? ␅
    @+67402 [67402] funk       q27 ? after
    @+67420 [67420] funnel     q28 ? ␅
    @+67420 [67420] funnel     q29 ? after
    @+67432 [67432] funnily    q30 ? ␅
    @+67432 [67432] funnily    q31 ? after
    @+67436 [67436] funny      q32 ? ␅
    @+67436 [67436] funny      q33 ? it
    @+67436 [67436] funny      done. it
    @+67444 [67444] fur        q18 ? ␅
    @+67444 [67444] fur        q19 ? before
    @+67884 [67884] gain       q14 ? ␅
    @+67884 [67884] gain       q15 ? before
    @+69482 [69482] geode      q12 ? ␅
    @+69482 [69482] geode      q13 ? before
    @+72662 [72662] green      q7  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1546 🥳 6 ⏱️ 0:02:05.458868

📜 1 sessions
💰 score: 40

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:YUMMY n n n n n remain:7572
    ⬜⬜⬜⬜⬜ tried:ABBAS n n n n n remain:1642
    ⬜⬜⬜⬜⬜ tried:KININ n n n n n remain:540
    ⬜🟩⬜🟩⬜ tried:CORER n Y n Y n remain:52
    ⬜🟩⬜🟩⬜ tried:DOZED n Y n Y n remain:8
    ⬜🟩⬜🟩⬜ tried:WOWEE n Y n Y n remain:4

    Undos used: 4

      4 words remaining
    x 10 unused letters
    = 40 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1689 🥳 20 ⏱️ 0:05:16.214347

📜 1 sessions
💰 score: 9600

    5/6
    ARLES ⬜🟨⬜⬜🟨
    ROSTI 🟨⬜🟨⬜⬜
    PURSY ⬜🟨🟩🟨⬜
    CHAMP ⬜🟩⬜⬜⬜
    SHRUB 🟩🟩🟩🟩🟩
    5/6
    SHRUB 🟩⬜⬜⬜⬜
    STOLE 🟩⬜⬜⬜⬜
    SNICK 🟩🟩🟩⬜⬜
    SNIPS 🟩🟩🟩⬜⬜
    SNIFF 🟩🟩🟩🟩🟩
    5/6
    SNIFF 🟩⬜⬜⬜⬜
    SEPAL 🟩⬜⬜🟨⬜
    STACK 🟩🟨🟨⬜⬜
    SORTA 🟩⬜🟨🟨🟨
    SATYR 🟩🟩🟩🟩🟩
    3/6
    SATYR ⬜🟨🟨⬜🟨
    HEART ⬜⬜🟩🟩🟩
    QUART 🟩🟩🟩🟩🟩
    Final 2/2
    MODAL ⬜⬜⬜⬜⬜
    EYING 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1666 🥳 score:26 ⏱️ 0:01:31.600048

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. BLIMP attempts:7 score:7
2. DRYER attempts:8 score:8
3. MINER attempts:5 score:5
4. BIDDY attempts:6 score:6

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1666 🥳 score:54 ⏱️ 0:01:42.672062

📜 1 sessions

Octordle Classic

1. ABASE attempts:5 score:5
2. WRUNG attempts:6 score:6
3. FLOUR attempts:11 score:11
4. DRINK attempts:3 score:3
5. AMITY attempts:7 score:7
6. GRAVY attempts:10 score:10
7. HEIST attempts:8 score:8
8. ARTSY attempts:4 score:4

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1646 🥳 score:41 ⏱️ 0:02:35.096237

📜 1 sessions

Sedecordle Classic sedecordle.com

1. QUART attempts:6 score:0
2. HORDE attempts:7 score:6
3. TENTH attempts:8 score:0
4. FROND attempts:16 score:8
5. PATTY attempts:9 score:0
6. FLICK attempts:17 score:9
7. RUSTY attempts:5 score:0
8. NOBLE attempts:10 score:5
9. BOSOM attempts:11 score:1
10. NYMPH attempts:4 score:1
11. QUARK attempts:12 score:1
12. MAKER attempts:13 score:2
13. BUYER attempts:14 score:1
14. KNEAD attempts:15 score:4
15. LUNAR attempts:3 score:0
16. HANDY attempts:17 score:3

# [squareword.org](squareword.org) 🧩 #1659 🥳 7 ⏱️ 0:01:50.607000

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T O P S
    T U L I P
    U N D E R
    N I E C E
    S C R E E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1596 🥳 189 ⏱️ 0:02:17.162562

🤔 190 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 48 chat prompts
🤖 48 dolphin3:latest replies
🔥   1 🥵  10 😎  27 🥶 148 🧊   3

      $1 #190 castle          100.00°C 🥳 1000‰ ~187 used:0  [186]  source:dolphin3
      $2 #189 manor            61.58°C 🔥  998‰   ~1 used:0  [0]    source:dolphin3
      $3 #138 farmhouse        54.16°C 🥵  989‰  ~24 used:19 [23]   source:dolphin3
      $4 #163 villa            53.30°C 🥵  987‰   ~6 used:6  [5]    source:dolphin3
      $5 #135 cottage          49.42°C 🥵  977‰  ~23 used:14 [22]   source:dolphin3
      $6 #187 inn              48.86°C 🥵  975‰   ~2 used:0  [1]    source:dolphin3
      $7 #148 bungalow         46.55°C 🥵  960‰   ~4 used:4  [3]    source:dolphin3
      $8 #169 chalet           46.26°C 🥵  958‰   ~5 used:4  [4]    source:dolphin3
      $9 #170 house            46.01°C 🥵  956‰   ~3 used:1  [2]    source:dolphin3
     $10  #68 countryside      42.62°C 🥵  922‰  ~34 used:30 [33]   source:dolphin3
     $11  #61 meadow           42.12°C 🥵  913‰  ~33 used:22 [32]   source:dolphin3
     $13 #152 estate           39.19°C 😎  848‰  ~25 used:2  [24]   source:dolphin3
     $40 #140 homely           28.97°C 🥶        ~43 used:0  [42]   source:dolphin3
    $188   #9 programming      -1.89°C 🧊       ~188 used:0  [187]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1629 🥳 57 ⏱️ 0:01:07.185474

🤔 58 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 19 chat prompts
🤖 19 dolphin3:latest replies
🔥  1 🥵  5 😎  9 🥶 25 🧊 17

     $1 #58 solidarité        100.00°C 🥳 1000‰ ~41 used:0  [40]  source:dolphin3
     $2 #49 égalité            47.43°C 🔥  994‰  ~1 used:3  [0]   source:dolphin3
     $3 #51 équité             45.07°C 🥵  987‰  ~2 used:0  [1]   source:dolphin3
     $4 #53 inégalité          38.82°C 🥵  958‰  ~3 used:0  [2]   source:dolphin3
     $5 #52 injustice          38.19°C 🥵  949‰  ~4 used:0  [3]   source:dolphin3
     $6 #13 éducation          37.78°C 🥵  943‰ ~11 used:14 [10]  source:dolphin3
     $7 #50 épanouissement     34.43°C 🥵  901‰  ~5 used:0  [4]   source:dolphin3
     $8 #55 discrimination     33.54°C 😎  883‰  ~6 used:0  [5]   source:dolphin3
     $9 #35 développement      30.02°C 😎  803‰ ~15 used:5  [14]  source:dolphin3
    $10 #43 culture            28.36°C 😎  740‰ ~12 used:2  [11]  source:dolphin3
    $11 #37 intégration        28.24°C 😎  732‰ ~13 used:2  [12]  source:dolphin3
    $12 #45 diversité          26.83°C 😎  655‰  ~7 used:0  [6]   source:dolphin3
    $17 #38 compétence         19.58°C 🥶       ~19 used:0  [18]  source:dolphin3
    $42  #9 voyage             -0.41°C 🧊       ~42 used:0  [41]  source:dolphin3
