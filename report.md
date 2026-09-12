# 2026-09-13

- 🔗 spaceword.org 🧩 2026-09-12 🏁 score 2168 ranked 37.9% 118/311 ⏱️ 0:27:16.565761
- 🔗 wordgrid 🧩 #834 🟪 rarity:0.27 ⏱️ 0:02:20.396295
- 🔗 alfagok.diginaut.net 🧩 #680 🥳 52 ⏱️ 0:01:15.280004
- 🔗 alphaguess.com 🧩 #1147 🥳 28 ⏱️ 0:00:29.519864
- 🔗 dontwordle.com 🧩 #1573 🥳 6 ⏱️ 0:02:48.810069
- 🔗 dictionary.com hurdle 🧩 #1716 🥳 17 ⏱️ 0:03:01.412006
- 🔗 Quordle Classic 🧩 #1693 🥳 score:18 ⏱️ 0:01:07.616897
- 🔗 Octordle Classic 🧩 #1693 🥳 score:64 ⏱️ 0:01:49.114409
- 🔗 Sedecordle Classic 🧩 #1673 🥳 score:38 ⏱️ 0:02:10.548732
- 🔗 squareword.org 🧩 #1686 🥳 8 ⏱️ 0:02:20.550752
- 🔗 cemantle.certitudes.org 🧩 #1623 🥳 162 ⏱️ 0:11:22.048866
- 🔗 cemantix.certitudes.org 🧩 #1656 🥳 68 ⏱️ 0:02:28.884251

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


# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 2026-09-11 🤔 rarity:nan ⏱️ 0:00:33.329642

📜 2 sessions
❓ ❓ ❓
❓ ❓ ❓
❓ ❓ ❓




# [spaceword.org](spaceword.org) 🧩 2026-09-12 🏁 score 2168 ranked 37.9% 118/311 ⏱️ 0:27:16.565761

📜 2 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 118/311

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ X I S _ _ _   
      _ _ _ _ _ _ I _ _ _   
      _ _ _ _ R E P _ _ _   
      _ _ _ _ I _ I _ _ _   
      _ _ _ F O I N _ _ _   
      _ _ _ _ J _ G _ _ _   
      _ _ _ T A O _ _ _ _   
      _ _ _ _ S E Z _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #834 🟪 rarity:0.27 ⏱️ 0:02:20.396295

📜 2 sessions
🦄 🦄 🌌
🌌 🦄 🌌
🌌 🌌 🌌
Rarity: 0.27 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #680 🥳 52 ⏱️ 0:01:15.280004

🤔 52 attempts
📜 1 sessions

    @       [    0] &-teken      
    @+8646  [ 8646] af           q10 ? ␅
    @+8646  [ 8646] af           q11 ? after
    @+16147 [16147] am           q12 ? ␅
    @+16147 [16147] am           q13 ? after
    @+18102 [18102] anti         q16 ? ␅
    @+18102 [18102] anti         q17 ? after
    @+18602 [18602] antithese    q20 ? ␅
    @+18602 [18602] antithese    q21 ? after
    @+18722 [18722] antwoord     q26 ? ␅
    @+18722 [18722] antwoord     q27 ? after
    @+18781 [18781] antwoordt    q28 ? ␅
    @+18781 [18781] antwoordt    q29 ? after
    @+18810 [18810] aortaklep    q44 ? ␅
    @+18810 [18810] aortaklep    q45 ? after
    @+18811 [18811] aow-leeftijd q42 ? ␅
    @+18811 [18811] aow-leeftijd q43 ? .
    @+18820 [18820] apache       q46 ? ␅
    @+18820 [18820] apache       q47 ? after
    @+18828 [18828] apaches      q48 ? ␅
    @+18828 [18828] apaches      q49 ? after
    @+18832 [18832] apart        q50 ? ␅
    @+18832 [18832] apart        q51 ? it
    @+18832 [18832] apart        done. it
    @+18836 [18836] apartheid    q22 ? ␅
    @+18836 [18836] apartheid    q23 ? before
    @+19094 [19094] app          q18 ? ␅
    @+19094 [19094] app          q19 ? before
    @+20493 [20493] arg          q14 ? ␅
    @+20493 [20493] arg          q15 ? before
    @+24874 [24874] bad          q9  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1147 🥳 28 ⏱️ 0:00:29.519864

🤔 28 attempts
📜 1 sessions

    @        [     0] aa      
    @+2      [     2] aahed   
    @+98143  [ 98143] mac     q0  ? ␅
    @+98143  [ 98143] mac     q1  ? after
    @+147307 [147307] rho     q2  ? ␅
    @+147307 [147307] rho     q3  ? after
    @+150203 [150203] sal     q12 ? ␅
    @+150203 [150203] sal     q13 ? after
    @+150917 [150917] sap     q16 ? ␅
    @+150917 [150917] sap     q17 ? after
    @+151203 [151203] sat     q18 ? ␅
    @+151203 [151203] sat     q19 ? after
    @+151331 [151331] satyr   q22 ? ␅
    @+151331 [151331] satyr   q23 ? after
    @+151340 [151340] sau     q24 ? ␅
    @+151340 [151340] sau     q25 ? after
    @+151399 [151399] sausage q26 ? ␅
    @+151399 [151399] sausage q27 ? it
    @+151399 [151399] sausage done. it
    @+151457 [151457] savor   q20 ? ␅
    @+151457 [151457] savor   q21 ? before
    @+151723 [151723] scan    q14 ? ␅
    @+151723 [151723] scan    q15 ? before
    @+153307 [153307] sea     q8  ? ␅
    @+153307 [153307] sea     q9  ? after
    @+153307 [153307] sea     q10 ? ␅
    @+153307 [153307] sea     q11 ? before
    @+159589 [159589] slug    q6  ? ␅
    @+159589 [159589] slug    q7  ? before
    @+171907 [171907] tag     q4  ? ␅
    @+171907 [171907] tag     q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1573 🥳 6 ⏱️ 0:02:48.810069

📜 2 sessions
💰 score: 16

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:POOPY n n n n n remain:6473
    ⬜⬜⬜⬜⬜ tried:ALGAL n n n n n remain:2076
    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:766
    ⬜⬜⬜🟩⬜ tried:JETES n n n Y n remain:24
    ⬜🟨⬜🟩⬜ tried:CURER n m n Y n remain:4
    🟩⬜⬜🟩🟩 tried:UMMED Y n n Y Y remain:2

    Undos used: 5

      2 words remaining
    x 8 unused letters
    = 16 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1716 🥳 17 ⏱️ 0:03:01.412006

📜 1 sessions
💰 score: 9900

    4/6
    ASTER ⬜⬜⬜⬜🟨
    RUING 🟨🟩⬜⬜⬜
    CURLY 🟩🟩🟩⬜🟩
    CURVY 🟩🟩🟩🟩🟩
    4/6
    CURVY ⬜🟨🟨⬜⬜
    ERUPT ⬜🟩🟨🟨⬜
    PROUD 🟨🟩🟩🟩⬜
    GROUP 🟩🟩🟩🟩🟩
    5/6
    GROUP ⬜⬜🟩⬜⬜
    SWOLE 🟨⬜🟩⬜🟩
    CHOSE ⬜⬜🟩🟩🟩
    NOOSE ⬜🟩🟩🟩🟩
    MOOSE 🟩🟩🟩🟩🟩
    2/6
    MOOSE 🟨🟩⬜⬜🟨
    HOMER 🟩🟩🟩🟩🟩
    Final 2/2
    BANAL 🟨⬜⬜⬜⬜
    PROBE 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1693 🥳 score:18 ⏱️ 0:01:07.616897

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. LUCID attempts:6 score:6
2. SPRAY attempts:3 score:3
3. MANGE attempts:4 score:4
4. EMAIL attempts:5 score:5

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1693 🥳 score:64 ⏱️ 0:01:49.114409

📜 1 sessions

Octordle Classic

1. TESTY attempts:7 score:7
2. CHORD attempts:8 score:8
3. RIVAL attempts:10 score:10
4. EQUIP attempts:2 score:2
5. BEECH attempts:9 score:9
6. FRAME attempts:12 score:12
7. GRATE attempts:5 score:5
8. ATOLL attempts:11 score:11

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1673 🥳 score:38 ⏱️ 0:02:10.548732

📜 1 sessions

Sedecordle Classic sedecordle.com

1. PLAID attempts:8 score:0
2. LUSTY attempts:3 score:8
3. ENNUI attempts:4 score:0
4. SLICE attempts:15 score:4
5. FAUNA attempts:9 score:0
6. HUNCH attempts:18 score:9
7. ELDER attempts:10 score:1
8. IVORY attempts:7 score:0
9. PULSE attempts:11 score:1
10. ROCKY attempts:14 score:1
11. PIANO attempts:6 score:0
12. CLASH attempts:16 score:6
13. LABOR attempts:12 score:1
14. SURLY attempts:13 score:2
15. NOISE attempts:5 score:0
16. MANGE attempts:17 score:5

# [squareword.org](squareword.org) 🧩 #1686 🥳 8 ⏱️ 0:02:20.550752

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟨 🟨 🟩 🟨
    🟨 🟨 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A C R E S
    T H U M P
    L I M B O
    A M B E R
    S P A D E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1623 🥳 162 ⏱️ 0:11:22.048866

🤔 163 attempts
📜 1 sessions
🫧 15 chat sessions
⁉️ 60 chat prompts
🤖 43 gemma4:12b replies
🤖 17 qwen3.8:latest replies
🔥   1 🥵   7 😎  39 🥶 114 🧊   1

      $1 #163 explosion        100.00°C 🥳 1000‰ ~162 used:0  [161]  source:gemma4 
      $2  #83 inferno           51.81°C 🔥  994‰   ~1 used:51 [0]    source:gemma4 
      $3  #81 blaze             46.49°C 🥵  986‰  ~43 used:22 [42]   source:gemma4 
      $4 #120 fire              43.45°C 🥵  982‰  ~40 used:11 [39]   source:gemma4 
      $5 #107 ignited           38.12°C 🥵  956‰   ~6 used:7  [5]    source:gemma4 
      $6  #73 conflagration     37.26°C 🥵  950‰   ~2 used:6  [1]    source:gemma4 
      $7 #140 arson             33.50°C 🥵  922‰   ~3 used:6  [2]    source:gemma4 
      $8 #143 flashover         33.22°C 🥵  920‰   ~4 used:6  [3]    source:gemma4 
      $9  #93 flare             32.45°C 🥵  905‰   ~5 used:6  [4]    source:gemma4 
     $10 #131 smoldering        31.42°C 😎  887‰   ~7 used:0  [6]    source:gemma4 
     $11 #153 pyrotechnics      28.28°C 😎  827‰   ~8 used:0  [7]    source:gemma4 
     $12 #112 burning           27.72°C 😎  810‰   ~9 used:0  [8]    source:gemma4 
     $49  #28 radiation         18.50°C 🥶        ~49 used:3  [48]   source:qwen3.8
    $163  #48 stochastic        -2.20°C 🧊       ~163 used:0  [162]  source:qwen3.8

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1656 🥳 68 ⏱️ 0:02:28.884251

🤔 69 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 21 chat prompts
🤖 21 gemma4:12b replies
🔥  1 🥵  4 😎  9 🥶 49 🧊  5

     $1 #69 hostilité        100.00°C 🥳 1000‰ ~64 used:0 [63]  source:gemma4
     $2 #60 animosité         52.86°C 🔥  998‰  ~1 used:2 [0]   source:gemma4
     $3 #62 dissension        44.47°C 🥵  988‰  ~2 used:1 [1]   source:gemma4
     $4 #61 conflit           44.02°C 🥵  986‰  ~3 used:0 [2]   source:gemma4
     $5 #66 antipathie        43.76°C 🥵  985‰  ~4 used:0 [3]   source:gemma4
     $6 #63 désaccord         37.08°C 🥵  913‰  ~5 used:0 [4]   source:gemma4
     $7 #65 schisme           35.98°C 😎  891‰  ~6 used:0 [5]   source:gemma4
     $8 #30 désunion          30.77°C 😎  652‰ ~13 used:6 [12]  source:gemma4
     $9 #57 discorde          30.24°C 😎  596‰  ~7 used:1 [6]   source:gemma4
    $10 #35 abandon           29.79°C 😎  564‰ ~11 used:3 [10]  source:gemma4
    $11 #51 ébranlement       28.36°C 😎  415‰ ~12 used:3 [11]  source:gemma4
    $12 #43 déroute           27.42°C 😎  280‰ ~10 used:2 [9]   source:gemma4
    $16 #67 brusquerie        25.54°C 🥶       ~19 used:0 [18]  source:gemma4
    $65  #7 nuage             -0.57°C 🧊       ~65 used:0 [64]  source:gemma4
