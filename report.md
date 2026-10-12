# 2026-10-13

- 🔗 spaceword.org 🧩 2026-10-12 🏁 score 2173 ranked 10.2% 33/322 ⏱️ 0:51:17.782450
- 🔗 wordgrid 🧩 #864 🟪 rarity:0.18 ⏱️ 0:02:16.038603
- 🔗 alfagok.diginaut.net 🧩 #710 🥳 34 ⏱️ 0:00:40.392643
- 🔗 alphaguess.com 🧩 #1177 🥳 26 ⏱️ 0:00:49.014735
- 🔗 dontwordle.com 🧩 #1603 🥳 6 ⏱️ 0:01:43.655348
- 🔗 dictionary.com hurdle 🧩 #1746 🥳 18 ⏱️ 0:03:17.488050
- 🔗 Quordle Classic 🧩 #1723 🥳 score:23 ⏱️ 0:01:33.273213
- 🔗 Octordle Classic 🧩 #1723 😦 score:72 ⏱️ 0:02:28.926572
- 🔗 Sedecordle Classic 🧩 #1703 🥳 score:38 ⏱️ 0:02:49.938986
- 🔗 cemantix.certitudes.org 🧩 #1686 🥳 215 ⏱️ 0:20:15.100814
- 🔗 squareword.org 🧩 #1716 🥳 7 ⏱️ 0:02:10.228642
- 🔗 cemantle.certitudes.org 🧩 #1653 🥳 154 ⏱️ 0:09:06.527118

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









# [spaceword.org](spaceword.org) 🧩 2026-10-12 🏁 score 2173 ranked 10.2% 33/322 ⏱️ 0:51:17.782450

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 33/322

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ A H _ T A N U K I   
      _ N E M A _ A _ _ _   
      _ T _ A V O W I N G   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #864 🟪 rarity:0.18 ⏱️ 0:02:16.038603

📜 3 sessions
🦄 🌌 🌌
🌌 🌌 🌌
🦄 🦄 🌌
Rarity: 0.18 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #710 🥳 34 ⏱️ 0:00:40.392643

🤔 34 attempts
📜 1 sessions

    @        [     0] &-teken        
    @+199631 [199631] lijk           q0  ? ␅
    @+199631 [199631] lijk           q1  ? after
    @+299532 [299532] schroot        q2  ? ␅
    @+299532 [299532] schroot        q3  ? after
    @+349314 [349314] vakantie       q4  ? ␅
    @+349314 [349314] vakantie       q5  ? after
    @+352878 [352878] ver            q8  ? ␅
    @+352878 [352878] ver            q9  ? after
    @+358171 [358171] verluiert      q12 ? ␅
    @+358171 [358171] verluiert      q13 ? after
    @+358300 [358300] vermeerder     q22 ? ␅
    @+358300 [358300] vermeerder     q23 ? after
    @+358324 [358324] vermei         q26 ? ␅
    @+358324 [358324] vermei         q27 ? after
    @+358334 [358334] vermeld        q28 ? ␅
    @+358334 [358334] vermeld        q29 ? after
    @+358338 [358338] vermelden      q32 ? ␅
    @+358338 [358338] vermelden      q33 ? it
    @+358338 [358338] vermelden      done. it
    @+358349 [358349] vermemeld      q30 ? ␅
    @+358349 [358349] vermemeld      q31 ? before
    @+358363 [358363] vermenigvuldig q24 ? ␅
    @+358363 [358363] vermenigvuldig q25 ? before
    @+358454 [358454] vermoed        q20 ? ␅
    @+358454 [358454] vermoed        q21 ? before
    @+358744 [358744] vernietig      q18 ? ␅
    @+358744 [358744] vernietig      q19 ? before
    @+359322 [359322] verpot         q16 ? ␅
    @+359322 [359322] verpot         q17 ? before
    @+360483 [360483] verst          q15 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1177 🥳 26 ⏱️ 0:00:49.014735

🤔 26 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+23680 [23680] camp       q4  ? ␅
    @+23680 [23680] camp       q5  ? after
    @+35522 [35522] convention q6  ? ␅
    @+35522 [35522] convention q7  ? after
    @+36723 [36723] cos        q12 ? ␅
    @+36723 [36723] cos        q13 ? after
    @+37449 [37449] courant    q14 ? ␅
    @+37449 [37449] courant    q15 ? after
    @+37801 [37801] coz        q16 ? ␅
    @+37801 [37801] coz        q17 ? after
    @+37987 [37987] crane      q18 ? ␅
    @+37987 [37987] crane      q19 ? after
    @+38078 [38078] crash      q20 ? ␅
    @+38078 [38078] crash      q21 ? after
    @+38125 [38125] craven     q22 ? ␅
    @+38125 [38125] craven     q23 ? after
    @+38148 [38148] crawl      q24 ? ␅
    @+38148 [38148] crawl      q25 ? it
    @+38148 [38148] crawl      done. it
    @+38181 [38181] crazy      q10 ? ␅
    @+38181 [38181] crazy      q11 ? before
    @+40838 [40838] da         q8  ? ␅
    @+40838 [40838] da         q9  ? before
    @+47374 [47374] dis        q2  ? ␅
    @+47374 [47374] dis        q3  ? before
    @+98142 [98142] mac        q0  ? ␅
    @+98142 [98142] mac        q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1603 🥳 6 ⏱️ 0:01:43.655348

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:MAMAS n n n n n remain:3350
    ⬜⬜⬜⬜⬜ tried:KEEVE n n n n n remain:1194
    ⬜⬜⬜⬜⬜ tried:DUDDY n n n n n remain:401
    🟨⬜⬜⬜⬜ tried:GRRRL m n n n n remain:37
    ⬜⬜⬜🟩🟨 tried:COHOG n n n Y m remain:4
    ⬜🟨🟩🟩🟩 tried:BIGOT n m Y Y Y remain:1

    Undos used: 3

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1746 🥳 18 ⏱️ 0:03:17.488050

📜 1 sessions
💰 score: 9800

    5/6
    TELOS ⬜⬜🟨🟨⬜
    AHOLD ⬜⬜🟨🟨⬜
    LOGIN 🟩🟩⬜⬜⬜
    ACMES ⬜⬜⬜⬜⬜
    LOBBY 🟩🟩🟩🟩🟩
    4/6
    LOBBY ⬜⬜⬜⬜⬜
    RESID 🟨⬜🟨⬜⬜
    SMART 🟩⬜⬜🟩⬜
    SPURN 🟩🟩🟩🟩🟩
    3/6
    SPURN ⬜🟨⬜🟨🟨
    PRANG 🟩🟩⬜🟩🟩
    PRONG 🟩🟩🟩🟩🟩
    4/6
    PRONG 🟩⬜⬜⬜⬜
    PIXEL 🟩⬜⬜⬜⬜
    PUSHY 🟩⬜⬜🟨⬜
    PATCH 🟩🟩🟩🟩🟩
    Final 2/2
    COMFY ⬜⬜⬜⬜🟩
    QUERY 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1723 🥳 score:23 ⏱️ 0:01:33.273213

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. FLUFF attempts:8 score:8
2. DEBUT attempts:4 score:4
3. TEETH attempts:5 score:5
4. STEIN attempts:6 score:6

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1723 😦 score:72 ⏱️ 0:02:28.926572

📜 1 sessions

Octordle Classic

1. GOING attempts:13 score:13
2. FI_ER -ABCDGHKLMNOPSTUY attempts:13 score:-1
3. REEDY attempts:7 score:7
4. STILT attempts:3 score:3
5. MELEE attempts:8 score:8
6. CURLY attempts:10 score:10
7. STYLE attempts:6 score:6
8. KAPPA attempts:11 score:11

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1703 🥳 score:38 ⏱️ 0:02:49.938986

📜 1 sessions

Sedecordle Classic sedecordle.com

1. THIRD attempts:17 score:1
2. FILMY attempts:18 score:7
3. PRINT attempts:4 score:0
4. ALOUD attempts:16 score:4
5. DERBY attempts:14 score:1
6. CROCK attempts:18 score:4
7. CLIFF attempts:13 score:1
8. PLUCK attempts:5 score:3
9. DUNCE attempts:12 score:1
10. QUEEN attempts:11 score:2
11. CHARM attempts:10 score:1
12. CLAMP attempts:8 score:0
13. FLORA attempts:7 score:0
14. MAXIM attempts:9 score:7
15. PUPAL attempts:6 score:0
16. BIGOT attempts:15 score:6

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1686 🥳 215 ⏱️ 0:20:15.100814

🤔 216 attempts
📜 1 sessions
🫧 17 chat sessions
⁉️ 95 chat prompts
🤖 11 gemma4:12b replies
🤖 84 dolphin3:latest replies
🔥   2 🥵  12 😎  56 🥶 116 🧊  29

      $1 #216 faisceau           100.00°C 🥳 1000‰ ~187 used:0  [186]  source:gemma4  
      $2 #118 polarimètre         50.94°C 🔥  995‰  ~10 used:73 [9]    source:dolphin3
      $3 #168 photon              50.78°C 🔥  994‰   ~1 used:28 [0]    source:dolphin3
      $4 #176 laser               44.09°C 🥵  965‰  ~11 used:8  [10]   source:dolphin3
      $5  #89 diffraction         43.31°C 🥵  961‰  ~66 used:31 [65]   source:dolphin3
      $6 #130 polarimétrique      43.16°C 🥵  958‰  ~12 used:10 [11]   source:dolphin3
      $7 #156 dichroïsme          42.89°C 🥵  957‰   ~2 used:6  [1]    source:dolphin3
      $8 #103 polarisation        42.76°C 🥵  956‰   ~9 used:7  [8]    source:dolphin3
      $9 #121 optique             41.97°C 🥵  949‰   ~3 used:6  [2]    source:dolphin3
     $10 #105 réfraction          41.36°C 🥵  942‰   ~4 used:6  [3]    source:dolphin3
     $11 #102 luminescence        40.68°C 🥵  935‰   ~5 used:6  [4]    source:dolphin3
     $16 #151 spectroscope        38.43°C 😎  888‰  ~13 used:0  [12]   source:dolphin3
     $72 #162 réfrangibilité      26.67°C 🥶        ~75 used:0  [74]   source:dolphin3
    $188  #31 domestique          -0.10°C 🧊       ~188 used:0  [187]  source:dolphin3

# [squareword.org](squareword.org) 🧩 #1716 🥳 7 ⏱️ 0:02:10.228642

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟨 🟩
    🟨 🟩 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S H A L T
    M E L E E
    A L T A R
    S L E D S
    H O R S E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1653 🥳 154 ⏱️ 0:09:06.527118

🤔 155 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 26 chat prompts
🤖 26 gemma4:12b replies
🥵   3 😎  21 🥶 125 🧊   5

      $1 #155 discovery        100.00°C 🥳 1000‰ ~150 used:0  [149]  source:gemma4
      $2 #153 breakthrough      34.00°C 🥵  944‰   ~1 used:1  [0]    source:gemma4
      $3  #81 development       32.96°C 🥵  924‰  ~19 used:22 [18]   source:gemma4
      $4  #78 synthesis         32.09°C 🥵  904‰  ~11 used:18 [10]   source:gemma4
      $5 #123 realization       31.18°C 😎  877‰  ~23 used:6  [22]   source:gemma4
      $6  #88 advancement       30.71°C 😎  863‰  ~12 used:2  [11]   source:gemma4
      $7  #29 existence         30.27°C 😎  844‰  ~20 used:3  [19]   source:gemma4
      $8  #50 emergence         30.24°C 😎  841‰  ~13 used:2  [12]   source:gemma4
      $9  #73 nucleosynthesis   30.03°C 😎  832‰  ~14 used:2  [13]   source:gemma4
     $10  #17 formation         29.63°C 😎  808‰  ~24 used:6  [23]   source:gemma4
     $11  #86 occurrence        28.90°C 😎  775‰  ~15 used:2  [14]   source:gemma4
     $12  #70 evolution         28.45°C 😎  740‰  ~16 used:2  [15]   source:gemma4
     $26 #147 collection        23.05°C 🥶        ~25 used:0  [24]   source:gemma4
    $151  #13 period            -0.26°C 🧊       ~151 used:0  [150]  source:gemma4
