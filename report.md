# 2026-08-10

- 🔗 spaceword.org 🧩 2026-08-09 🏁 score 2173 ranked 4.5% 14/312 ⏱️ 0:41:23.765228
- 🔗 wordgrid 🧩 #800 🟪 rarity:0.13 ⏱️ 0:02:28.663058
- 🔗 alfagok.diginaut.net 🧩 #646 🥳 34 ⏱️ 0:00:45.739519
- 🔗 alphaguess.com 🧩 #1113 🥳 30 ⏱️ 0:01:05.816143
- 🔗 dontwordle.com 🧩 #1539 🥳 6 ⏱️ 0:01:43.044850
- 🔗 dictionary.com hurdle 🧩 #1682 🥳 18 ⏱️ 0:03:38.805918
- 🔗 Quordle Classic 🧩 #1659 🥳 score:25 ⏱️ 0:02:43.935410
- 🔗 Octordle Classic 🧩 #1659 🥳 score:58 ⏱️ 0:02:10.275723
- 🔗 Sedecordle Classic 🧩 #1639 🥳 score:57 ⏱️ 0:02:37.348925
- 🔗 squareword.org 🧩 #1652 🥳 6 ⏱️ 0:01:59.830872
- 🔗 cemantle.certitudes.org 🧩 #1589 🥳 171 ⏱️ 0:03:44.577784
- 🔗 cemantix.certitudes.org 🧩 #1622 🥳 112 ⏱️ 0:01:33.851880

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






# [spaceword.org](spaceword.org) 🧩 2026-08-09 🏁 score 2173 ranked 4.5% 14/312 ⏱️ 0:41:23.765228

📜 6 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 14/312

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ L U M _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ _ Q A T _ _ _   
      _ _ _ _ _ G I _ _ _   
      _ _ _ _ D O L _ _ _   
      _ _ _ _ _ N E _ _ _   
      _ _ _ _ _ I _ _ _ _   
      _ _ _ _ A Z O _ _ _   
      _ _ _ _ H E X _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #800 🟪 rarity:0.13 ⏱️ 0:02:28.663058

📜 2 sessions
🌌 🌌 🦄
🦄 🦄 🦄
🌌 🌌 🦄
Rarity: 0.13 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #646 🥳 34 ⏱️ 0:00:45.739519

🤔 34 attempts
📜 1 sessions

    @        [     0] &-teken          
    @+99692  [ 99692] ex               q2  ? ␅
    @+99692  [ 99692] ex               q3  ? after
    @+149378 [149378] huis             q4  ? ␅
    @+149378 [149378] huis             q5  ? after
    @+174485 [174485] kind             q6  ? ␅
    @+174485 [174485] kind             q7  ? after
    @+187066 [187066] kronen           q8  ? ␅
    @+187066 [187066] kronen           q9  ? after
    @+190290 [190290] la               q10 ? ␅
    @+190290 [190290] la               q11 ? after
    @+194846 [194846] lees             q12 ? ␅
    @+194846 [194846] lees             q13 ? after
    @+197026 [197026] levens           q14 ? ␅
    @+197026 [197026] levens           q15 ? after
    @+198194 [198194] licht            q16 ? ␅
    @+198194 [198194] licht            q17 ? after
    @+198895 [198895] liefdes          q18 ? ␅
    @+198895 [198895] liefdes          q19 ? after
    @+199206 [199206] lieveling        q20 ? ␅
    @+199206 [199206] lieveling        q21 ? after
    @+199307 [199307] lievelingsplant  q26 ? ␅
    @+199307 [199307] lievelingsplant  q27 ? after
    @+199357 [199357] lievelingswerken q28 ? ␅
    @+199357 [199357] lievelingswerken q29 ? after
    @+199368 [199368] liever           q32 ? ␅
    @+199368 [199368] liever           q33 ? it
    @+199368 [199368] liever           done. it
    @+199382 [199382] lievevrouw       q30 ? ␅
    @+199382 [199382] lievevrouw       q31 ? before
    @+199407 [199407] lift             q23 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1113 🥳 30 ⏱️ 0:01:05.816143

🤔 30 attempts
📜 1 sessions

    @       [    0] aa              
    @+47378 [47378] dis             q4  ? ␅
    @+47378 [47378] dis             q5  ? after
    @+72662 [72662] green           q6  ? ␅
    @+72662 [72662] green           q7  ? after
    @+79019 [79019] hone            q10 ? ␅
    @+79019 [79019] hone            q11 ? after
    @+82206 [82206] imbitter        q12 ? ␅
    @+82206 [82206] imbitter        q13 ? after
    @+83234 [83234] in              q14 ? ␅
    @+83234 [83234] in              q15 ? after
    @+83504 [83504] incertitudes    q20 ? ␅
    @+83504 [83504] incertitudes    q21 ? after
    @+83514 [83514] inch            q28 ? ␅
    @+83514 [83514] inch            q29 ? it
    @+83514 [83514] inch            done. it
    @+83532 [83532] incident        q26 ? ␅
    @+83532 [83532] incident        q27 ? before
    @+83569 [83569] incitable       q24 ? ␅
    @+83569 [83569] incitable       q25 ? before
    @+83634 [83634] incog           q22 ? ␅
    @+83634 [83634] incog           q23 ? before
    @+83773 [83773] incoordinations q18 ? ␅
    @+83773 [83773] incoordinations q19 ? before
    @+84311 [84311] induce          q16 ? ␅
    @+84311 [84311] induce          q17 ? before
    @+85397 [85397] inocula         q8  ? ␅
    @+85397 [85397] inocula         q9  ? before
    @+98147 [98147] mac             q1  ? after
    @+98147 [98147] mac             q2  ? ␅
    @+98147 [98147] mac             q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1539 🥳 6 ⏱️ 0:01:43.044850

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:LLAMA n n n n n remain:4962
    ⬜⬜⬜⬜⬜ tried:EDGED n n n n n remain:1585
    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:538
    ⬜⬜⬜⬜⬜ tried:CROCK n n n n n remain:62
    🟨🟨⬜⬜⬜ tried:INFIX m m n n n remain:14
    ⬜🟨⬜🟩🟨 tried:JINNS n m n Y m remain:2

    Undos used: 4

      2 words remaining
    x 7 unused letters
    = 14 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1682 🥳 18 ⏱️ 0:03:38.805918

📜 1 sessions
💰 score: 9800

    4/6
    RESAT ⬜🟨⬜🟨⬜
    LACED ⬜🟩⬜🟨⬜
    MANGE ⬜🟩⬜🟨🟩
    GAUZE 🟩🟩🟩🟩🟩
    3/6
    GAUZE ⬜🟨🟨⬜⬜
    ULTRA 🟨🟩⬜⬜🟨
    ALBUM 🟩🟩🟩🟩🟩
    6/6
    ALBUM 🟨⬜⬜⬜⬜
    YEARS ⬜🟨🟩🟨⬜
    TRACE ⬜🟩🟩⬜🟩
    GRADE 🟩🟩🟩⬜🟩
    PAVED ⬜🟨⬜🟨⬜
    GRAZE 🟩🟩🟩🟩🟩
    4/6
    GRAZE ⬜🟨⬜⬜⬜
    TORUS ⬜🟩🟨⬜⬜
    ROWDY 🟨🟩⬜🟨⬜
    DONOR 🟩🟩🟩🟩🟩
    Final 1/2
    BLUNT 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1659 🥳 score:25 ⏱️ 0:02:43.935410

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. GAVEL attempts:6 score:6
2. CRUSH attempts:7 score:7
3. SPEED attempts:9 score:9
4. ETHOS attempts:3 score:3

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1659 🥳 score:58 ⏱️ 0:02:10.275723

📜 1 sessions

Octordle Classic

1. MATCH attempts:6 score:6
2. LURID attempts:3 score:3
3. AROSE attempts:4 score:4
4. VIVID attempts:7 score:7
5. BRAWN attempts:10 score:10
6. FLUNG attempts:11 score:11
7. MILKY attempts:8 score:8
8. CABAL attempts:9 score:9

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1639 🥳 score:57 ⏱️ 0:02:37.348925

📜 1 sessions

Sedecordle Classic sedecordle.com

1. HOLLY attempts:19 score:1
2. DEATH attempts:4 score:9
3. TONGA attempts:8 score:0
4. LEAKY attempts:13 score:8
5. WRUNG attempts:15 score:1
6. OLIVE attempts:10 score:5
7. STILT attempts:9 score:0
8. SNARL attempts:11 score:9
9. FAIRY attempts:12 score:1
10. PUTTY attempts:17 score:2
11. CADET attempts:7 score:0
12. IRATE attempts:3 score:7
13. BLURT attempts:14 score:1
14. FETCH attempts:16 score:4
15. KAYAK attempts:18 score:1
16. DRIED attempts:6 score:8

# [squareword.org](squareword.org) 🧩 #1652 🥳 6 ⏱️ 0:01:59.830872

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    M U L L S
    I N L E T
    S T A V E
    T I M E R
    Y E A R N

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1589 🥳 171 ⏱️ 0:03:44.577784

🤔 172 attempts
📜 1 sessions
🫧 14 chat sessions
⁉️ 79 chat prompts
🤖 79 dolphin3:latest replies
🔥   2 🥵   9 😎  26 🥶 131 🧊   3

      $1 #172 graphic          100.00°C 🥳 1000‰ ~169 used:0  [168]  source:dolphin3
      $2 #137 explicit          48.33°C 🔥  991‰   ~7 used:16 [6]    source:dolphin3
      $3 #161 vivid             47.69°C 🔥  990‰   ~1 used:8  [0]    source:dolphin3
      $4 #163 descriptive       42.38°C 🥵  976‰   ~9 used:3  [8]    source:dolphin3
      $5 #145 detailed          40.90°C 🥵  969‰   ~2 used:1  [1]    source:dolphin3
      $6 #155 explicitness      40.84°C 🥵  968‰   ~3 used:0  [2]    source:dolphin3
      $7 #165 illustrative      39.82°C 🥵  959‰   ~4 used:0  [3]    source:dolphin3
      $8 #127 racy              39.19°C 🥵  956‰  ~10 used:7  [9]    source:dolphin3
      $9 #138 risqué            38.24°C 🥵  950‰   ~8 used:2  [7]    source:dolphin3
     $10 #167 colorful          36.83°C 🥵  928‰   ~5 used:0  [4]    source:dolphin3
     $11 #140 titillating       36.17°C 🥵  919‰   ~6 used:0  [5]    source:dolphin3
     $13 #112 salacious         34.92°C 😎  897‰  ~32 used:9  [31]   source:dolphin3
     $39 #119 coarse            24.21°C 🥶        ~46 used:0  [45]   source:dolphin3
    $170  #92 taking            -0.79°C 🧊       ~170 used:0  [169]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1622 🥳 112 ⏱️ 0:01:33.851880

🤔 113 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 22 chat prompts
🤖 22 dolphin3:latest replies
🥵  4 😎 19 🥶 74 🧊 15

      $1 #113 mécanique       100.00°C 🥳 1000‰  ~98 used:0  [97]   source:dolphin3
      $2  #67 assemblage       43.28°C 🥵  957‰   ~2 used:6  [1]    source:dolphin3
      $3  #95 fabrication      40.00°C 🥵  920‰   ~1 used:4  [0]    source:dolphin3
      $4  #11 automobile       38.86°C 🥵  906‰  ~19 used:18 [18]   source:dolphin3
      $5  #35 carrosserie      38.57°C 🥵  900‰  ~18 used:12 [17]   source:dolphin3
      $6  #75 rivetage         36.82°C 😎  848‰   ~3 used:0  [2]    source:dolphin3
      $7 #109 composant        36.17°C 😎  831‰   ~4 used:0  [3]    source:dolphin3
      $8  #92 conception       35.95°C 😎  821‰   ~5 used:0  [4]    source:dolphin3
      $9 #103 prototypage      34.01°C 😎  754‰   ~6 used:0  [5]    source:dolphin3
     $10  #85 visserie         31.82°C 😎  660‰   ~7 used:0  [6]    source:dolphin3
     $11  #68 boulonnage       31.14°C 😎  616‰   ~8 used:0  [7]    source:dolphin3
     $12 #108 aérospatiale     30.73°C 😎  589‰   ~9 used:0  [8]    source:dolphin3
     $25  #46 châssis          25.41°C 🥶        ~26 used:0  [25]   source:dolphin3
     $99  #58 garnison         -0.99°C 🧊        ~99 used:0  [98]   source:dolphin3
