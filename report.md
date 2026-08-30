# 2026-08-31

- 🔗 spaceword.org 🧩 2026-08-30 🏁 score 2173 ranked 6.2% 21/339 ⏱️ 0:39:09.928494
- 🔗 wordgrid 🧩 #821 🟪 rarity:0.21 ⏱️ 0:02:13.868481
- 🔗 alfagok.diginaut.net 🧩 #667 🥳 32 ⏱️ 0:15:14.057574
- 🔗 alphaguess.com 🧩 #1134 🥳 28 ⏱️ 0:00:34.313991
- 🔗 dontwordle.com 🧩 #1560 🥳 6 ⏱️ 0:01:19.122535
- 🔗 dictionary.com hurdle 🧩 #1703 🥳 17 ⏱️ 0:07:59.463973
- 🔗 Quordle Classic 🧩 #1680 🥳 score:26 ⏱️ 0:01:33.540648
- 🔗 Octordle Classic 🧩 #1680 🥳 score:59 ⏱️ 0:01:57.930204
- 🔗 Sedecordle Classic 🧩 #1660 🥳 score:47 ⏱️ 0:02:51.607828
- 🔗 squareword.org 🧩 #1673 🥳 7 ⏱️ 0:02:19.488779
- 🔗 cemantle.certitudes.org 🧩 #1610 🥳 387 ⏱️ 0:08:15.259701
- 🔗 cemantix.certitudes.org 🧩 #1643 🥳 76 ⏱️ 0:01:48.049323

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



























# [spaceword.org](spaceword.org) 🧩 2026-08-30 🏁 score 2173 ranked 6.2% 21/339 ⏱️ 0:39:09.928494

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 21/339

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ W _ S _ G _ _ J O   
      _ H I A T A L _ E R   
      _ O _ B A R O Q U E   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #821 🟪 rarity:0.21 ⏱️ 0:02:13.868481

📜 2 sessions
🌌 🌌 🌌
🦄 🦄 🌌
🦄 🦄 🌌
Rarity: 0.21 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #667 🥳 32 ⏱️ 0:15:14.057574

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+24880  [ 24880] bad         q8  ? ␅
    @+24880  [ 24880] bad         q9  ? after
    @+27572  [ 27572] basis       q14 ? ␅
    @+27572  [ 27572] basis       q15 ? after
    @+28931  [ 28931] bed         q16 ? ␅
    @+28931  [ 28931] bed         q17 ? after
    @+29169  [ 29169] bedevaart   q20 ? ␅
    @+29169  [ 29169] bedevaart   q21 ? after
    @+29292  [ 29292] bedil       q22 ? ␅
    @+29292  [ 29292] bedil       q23 ? after
    @+29368  [ 29368] bedonder    q24 ? ␅
    @+29368  [ 29368] bedonder    q25 ? after
    @+29400  [ 29400] bedrag      q26 ? ␅
    @+29400  [ 29400] bedrag      q27 ? after
    @+29409  [ 29409] bedreig     q28 ? ␅
    @+29409  [ 29409] bedreig     q29 ? after
    @+29424  [ 29424] bedreven    q30 ? ␅
    @+29424  [ 29424] bedreven    q31 ? it
    @+29424  [ 29424] bedreven    done. it
    @+29443  [ 29443] bedrijf     q18 ? ␅
    @+29443  [ 29443] bedrijf     q19 ? before
    @+31106  [ 31106] begeleiding q12 ? ␅
    @+31106  [ 31106] begeleiding q13 ? before
    @+37341  [ 37341] beschermen  q10 ? ␅
    @+37341  [ 37341] beschermen  q11 ? before
    @+49808  [ 49808] boks        q6  ? ␅
    @+49808  [ 49808] boks        q7  ? before
    @+99688  [ 99688] ex          q4  ? ␅
    @+99688  [ 99688] ex          q5  ? before
    @+199647 [199647] lijk        q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1134 🥳 28 ⏱️ 0:00:34.313991

🤔 28 attempts
📜 1 sessions

    @       [    0] aa       
    @+2     [    2] aahed    
    @+47378 [47378] dis      q2  ? ␅
    @+47378 [47378] dis      q3  ? after
    @+72662 [72662] green    q4  ? ␅
    @+72662 [72662] green    q5  ? after
    @+73047 [73047] groan    q16 ? ␅
    @+73047 [73047] groan    q17 ? after
    @+73093 [73093] groom    q22 ? ␅
    @+73093 [73093] groom    q23 ? after
    @+73101 [73101] groove   q26 ? ␅
    @+73101 [73101] groove   q27 ? it
    @+73101 [73101] groove   done. it
    @+73113 [73113] grope    q24 ? ␅
    @+73113 [73113] grope    q25 ? before
    @+73142 [73142] grot     q20 ? ␅
    @+73142 [73142] grot     q21 ? before
    @+73243 [73243] grouse   q18 ? ␅
    @+73243 [73243] grouse   q19 ? before
    @+73443 [73443] gruyeres q14 ? ␅
    @+73443 [73443] gruyeres q15 ? before
    @+74223 [74223] gyve     q12 ? ␅
    @+74223 [74223] gyve     q13 ? before
    @+75781 [75781] hat      q10 ? ␅
    @+75781 [75781] hat      q11 ? before
    @+79019 [79019] hone     q8  ? ␅
    @+79019 [79019] hone     q9  ? before
    @+85397 [85397] inocula  q6  ? ␅
    @+85397 [85397] inocula  q7  ? before
    @+98147 [98147] mac      q0  ? ␅
    @+98147 [98147] mac      q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1560 🥳 6 ⏱️ 0:01:19.122535

📜 1 sessions
💰 score: 21

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:FEEZE n n n n n remain:6482
    ⬜⬜⬜⬜⬜ tried:HOLLO n n n n n remain:2418
    ⬜⬜⬜⬜⬜ tried:MUMUS n n n n n remain:565
    ⬜🟨⬜⬜⬜ tried:BIDDY n m n n n remain:103
    ⬜⬜🟩⬜⬜ tried:CRICK n n Y n n remain:15
    🟨⬜🟩⬜⬜ tried:AJIVA m n Y n n remain:3

    Undos used: 3

      3 words remaining
    x 7 unused letters
    = 21 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1703 🥳 17 ⏱️ 0:07:59.463973

📜 1 sessions
💰 score: 9900

    3/6
    RALES ⬜🟨⬜🟨🟨
    SPATE 🟨🟨🟩⬜🟩
    PHASE 🟩🟩🟩🟩🟩
    5/6
    PHASE ⬜⬜⬜⬜🟨
    ORIEL ⬜🟨⬜🟩⬜
    MURED ⬜🟨🟨🟩🟨
    UNDER 🟩⬜🟩🟩🟩
    UDDER 🟩🟩🟩🟩🟩
    3/6
    UDDER ⬜⬜⬜🟨🟨
    BEARS 🟨🟨🟨🟩🟨
    SABRE 🟩🟩🟩🟩🟩
    5/6
    SABRE 🟩🟨⬜🟩🟩
    SCARE 🟩⬜🟩🟩🟩
    SHARE 🟩⬜🟩🟩🟩
    SPENT 🟩⬜🟨🟨⬜
    SNARE 🟩🟩🟩🟩🟩
    Final 1/2
    HEDGE 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1680 🥳 score:26 ⏱️ 0:01:33.540648

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. ALIVE attempts:7 score:7
2. LOUSE attempts:5 score:5
3. ABOVE attempts:6 score:6
4. MOSSY attempts:8 score:8

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1680 🥳 score:59 ⏱️ 0:01:57.930204

📜 1 sessions

Octordle Classic

1. MORAL attempts:11 score:11
2. SOAPY attempts:3 score:3
3. SHOWY attempts:5 score:5
4. STARK attempts:8 score:8
5. KEBAB attempts:9 score:9
6. CAVIL attempts:10 score:10
7. AFIRE attempts:6 score:6
8. SWEET attempts:7 score:7

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1660 🥳 score:47 ⏱️ 0:02:51.607828

📜 1 sessions

Sedecordle Classic sedecordle.com

1. BRUSH attempts:9 score:0
2. PLEAD attempts:7 score:9
3. SHALL attempts:14 score:1
4. CURSE attempts:10 score:4
5. TIMID attempts:4 score:0
6. GAZER attempts:15 score:4
7. FUNNY attempts:11 score:1
8. QUIET attempts:3 score:1
9. HUMUS attempts:12 score:1
10. HOTLY attempts:13 score:2
11. DIZZY attempts:16 score:1
12. CHARM attempts:8 score:6
13. CHESS attempts:16 score:1
14. GROUT attempts:5 score:7
15. PLEAT attempts:16 score:1
16. SLANG attempts:6 score:8

# [squareword.org](squareword.org) 🧩 #1673 🥳 7 ⏱️ 0:02:19.488779

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟨 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C R E S T
    H E N N A
    A C T O R
    S T E R N
    M A R T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1610 🥳 387 ⏱️ 0:08:15.259701

🤔 388 attempts
📜 1 sessions
🫧 27 chat sessions
⁉️ 154 chat prompts
🤖 154 dolphin3:latest replies
🔥   5 🥵  28 😎 105 🥶 246 🧊   3

      $1 #388 creature        100.00°C 🥳 1000‰ ~385 used:0   [384]  source:dolphin3
      $2 #343 lizard           66.44°C 🔥  998‰  ~14 used:31  [13]   source:dolphin3
      $3 #109 mammal           66.20°C 🔥  997‰ ~133 used:135 [132]  source:dolphin3
      $4 #299 reptile          62.92°C 🔥  994‰  ~15 used:51  [14]   source:dolphin3
      $5 #371 serpent          60.07°C 🔥  993‰   ~6 used:11  [5]    source:dolphin3
      $6 #338 crocodilian      58.96°C 🔥  992‰   ~7 used:11  [6]    source:dolphin3
      $7 #322 reptilian        56.48°C 🥵  987‰  ~19 used:7   [18]   source:dolphin3
      $8 #350 snake            55.96°C 🥵  984‰   ~8 used:2   [7]    source:dolphin3
      $9 #342 turtle           55.61°C 🥵  983‰   ~9 used:2   [8]    source:dolphin3
     $10 #229 otter            55.06°C 🥵  981‰ ~136 used:23  [135]  source:dolphin3
     $11 #146 canid            55.00°C 🥵  980‰ ~134 used:19  [133]  source:dolphin3
     $35  #36 species          49.36°C 😎  892‰ ~135 used:2   [134]  source:dolphin3
    $140  #42 plumage          36.76°C 🥶       ~139 used:0   [138]  source:dolphin3
    $386 #214 four             -0.56°C 🧊       ~386 used:0   [385]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1643 🥳 76 ⏱️ 0:01:48.049323

🤔 77 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 24 chat prompts
🤖 24 dolphin3:latest replies
🔥  2 🥵 10 😎 13 🥶 30 🧊 21

     $1 #77 stabilisation     100.00°C 🥳 1000‰ ~57 used:0  [56]  source:dolphin3
     $2 #63 consolidation      49.71°C 🔥  997‰  ~7 used:15 [6]   source:dolphin3
     $3 #60 renforcement       44.52°C 🔥  993‰  ~6 used:12 [5]   source:dolphin3
     $4 #55 augmentation       42.57°C 🥵  989‰ ~10 used:4  [9]   source:dolphin3
     $5 #62 accroissement      41.74°C 🥵  987‰  ~8 used:2  [7]   source:dolphin3
     $6 #33 amélioration       41.36°C 🥵  985‰ ~11 used:5  [10]  source:dolphin3
     $7 #20 croissance         40.45°C 🥵  981‰ ~12 used:6  [11]  source:dolphin3
     $8 #45 évolution          39.26°C 🥵  974‰  ~9 used:2  [8]   source:dolphin3
     $9 #67 élargissement      38.11°C 🥵  966‰  ~1 used:1  [0]   source:dolphin3
    $10 #36 progression        37.46°C 🥵  960‰  ~2 used:1  [1]   source:dolphin3
    $11 #68 consolider         37.19°C 🥵  958‰  ~3 used:0  [2]   source:dolphin3
    $14 #35 mise               32.03°C 😎  867‰ ~13 used:0  [12]  source:dolphin3
    $27 #24 fermentation       22.52°C 🥶       ~28 used:0  [27]  source:dolphin3
    $57  #7 nuage              -0.23°C 🧊       ~56 used:5  [55]  source:dolphin3
