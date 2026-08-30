# 2026-08-30

- 🔗 spaceword.org 🧩 2026-08-29 🏁 score 2173 ranked 12.1% 37/305 ⏱️ 0:09:32.185620
- 🔗 wordgrid 🧩 #820 🟪 rarity:0.18 ⏱️ 0:05:46.824627
- 🔗 alfagok.diginaut.net 🧩 #666 🥳 28 ⏱️ 0:00:39.194696
- 🔗 alphaguess.com 🧩 #1133 🥳 28 ⏱️ 0:00:38.679153
- 🔗 dontwordle.com 🧩 #1559 🥳 6 ⏱️ 0:01:38.500043
- 🔗 dictionary.com hurdle 🧩 #1702 😦 21 ⏱️ 0:04:57.841061
- 🔗 Quordle Classic 🧩 #1679 😦 score:28 ⏱️ 0:02:20.698984
- 🔗 Octordle Classic 🧩 #1679 🥳 score:60 ⏱️ 0:02:23.358435
- 🔗 Sedecordle Classic 🧩 #1659 🥳 score:36 ⏱️ 0:02:28.851691
- 🔗 squareword.org 🧩 #1672 🥳 7 ⏱️ 0:02:16.549037
- 🔗 cemantle.certitudes.org 🧩 #1609 🥳 56 ⏱️ 0:00:40.777068
- 🔗 cemantix.certitudes.org 🧩 #1642 🥳 665 ⏱️ 3:08:26.404169

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


























# [spaceword.org](spaceword.org) 🧩 2026-08-29 🏁 score 2173 ranked 12.1% 37/305 ⏱️ 0:09:32.185620

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 37/305

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ Z _ V A R _ _ P A   
      _ I _ A M O E B A N   
      _ N E W I E S _ R _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #820 🟪 rarity:0.18 ⏱️ 0:05:46.824627

📜 3 sessions
🌌 🌌 🌌
🌌 🌌 🌌
🌌 🦄 🦄
Rarity: 0.18 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #666 🥳 28 ⏱️ 0:00:39.194696

🤔 28 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+2      [     2] -cijferig 
    @+199647 [199647] lijk      q0  ? ␅
    @+199647 [199647] lijk      q1  ? after
    @+199647 [199647] lijk      q2  ? ␅
    @+199647 [199647] lijk      q3  ? after
    @+299551 [299551] schroot   q4  ? ␅
    @+299551 [299551] schroot   q5  ? after
    @+324136 [324136] sub       q8  ? ␅
    @+324136 [324136] sub       q9  ? after
    @+330319 [330319] televisie q12 ? ␅
    @+330319 [330319] televisie q13 ? after
    @+330660 [330660] temp      q20 ? ␅
    @+330660 [330660] temp      q21 ? after
    @+330833 [330833] tempte    q22 ? ␅
    @+330833 [330833] tempte    q23 ? after
    @+330845 [330845] ten       q24 ? ␅
    @+330845 [330845] ten       q25 ? after
    @+330919 [330919] tennis    q26 ? ␅
    @+330919 [330919] tennis    q27 ? it
    @+330919 [330919] tennis    done. it
    @+331006 [331006] tennist   q18 ? ␅
    @+331006 [331006] tennist   q19 ? before
    @+331714 [331714] terug     q16 ? ␅
    @+331714 [331714] terug     q17 ? before
    @+333525 [333525] thesis    q14 ? ␅
    @+333525 [333525] thesis    q15 ? before
    @+336729 [336729] toetsing  q10 ? ␅
    @+336729 [336729] toetsing  q11 ? before
    @+349336 [349336] vakantie  q6  ? ␅
    @+349336 [349336] vakantie  q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1133 🥳 28 ⏱️ 0:00:38.679153

🤔 28 attempts
📜 1 sessions

    @       [    0] aa              
    @+2     [    2] aahed           
    @+47378 [47378] dis             q4  ? ␅
    @+47378 [47378] dis             q5  ? after
    @+60017 [60017] eyewitness      q8  ? ␅
    @+60017 [60017] eyewitness      q9  ? after
    @+66309 [66309] free            q10 ? ␅
    @+66309 [66309] free            q11 ? after
    @+69482 [69482] geode           q12 ? ␅
    @+69482 [69482] geode           q13 ? after
    @+69920 [69920] gi              q16 ? ␅
    @+69920 [69920] gi              q17 ? after
    @+70493 [70493] glass           q18 ? ␅
    @+70493 [70493] glass           q19 ? after
    @+70741 [70741] glob            q20 ? ␅
    @+70741 [70741] glob            q21 ? after
    @+70765 [70765] globe           q26 ? ␅
    @+70765 [70765] globe           q27 ? it
    @+70765 [70765] globe           done. it
    @+70804 [70804] glockenspiels   q24 ? ␅
    @+70804 [70804] glockenspiels   q25 ? before
    @+70867 [70867] gloss           q22 ? ␅
    @+70867 [70867] gloss           q23 ? before
    @+71072 [71072] glyceraldehydes q14 ? ␅
    @+71072 [71072] glyceraldehydes q15 ? before
    @+72662 [72662] green           q6  ? ␅
    @+72662 [72662] green           q7  ? before
    @+98147 [98147] mac             q0  ? ␅
    @+98147 [98147] mac             q1  ? after
    @+98147 [98147] mac             q2  ? ␅
    @+98147 [98147] mac             q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1559 🥳 6 ⏱️ 0:01:38.500043

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:TWEET n n n n n remain:5004
    ⬜⬜⬜⬜⬜ tried:PZAZZ n n n n n remain:1944
    ⬜⬜⬜⬜⬜ tried:MOSSO n n n n n remain:327
    ⬜⬜⬜⬜⬜ tried:YUKKY n n n n n remain:58
    ⬜⬜⬜⬜🟨 tried:GRRRL n n n n m remain:14
    ⬜🟨🟩⬜⬜ tried:BLIND n m Y n n remain:1

    Undos used: 4

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1702 😦 21 ⏱️ 0:04:57.841061

📜 1 sessions
💰 score: 3360

    4/6
    STARE ⬜⬜⬜⬜⬜
    LINGY 🟨⬜⬜⬜🟩
    FLUKY 🟩🟨⬜⬜🟩
    FOLLY 🟩🟩🟩🟩🟩
    6/6
    FOLLY ⬜🟨⬜⬜⬜
    STORE ⬜⬜🟨⬜⬜
    IMAGO ⬜⬜🟨⬜🟩
    NACHO ⬜🟩⬜⬜🟩
    BAWKS ⬜🟩⬜🟨⬜
    KAZOO 🟩🟩🟩🟩🟩
    5/6
    KAZOO ⬜⬜⬜⬜⬜
    SUINT ⬜🟩⬜⬜⬜
    DUPER 🟨🟩⬜🟨⬜
    ABAFT ⬜⬜⬜🟨⬜
    FUDGE 🟩🟩🟩🟩🟩
    6/6
    ????? ⬜⬜⬜⬜🟨
    ????? ⬜🟨🟨🟨⬜
    ????? ⬜🟩⬜🟩🟩
    ????? ⬜🟩⬜🟩🟩
    ????? ⬜⬜⬜🟨⬜
    ????? ⬜🟩⬜🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1679 😦 score:28 ⏱️ 0:02:20.698984

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. USING attempts:7 score:7
2. SORRY attempts:8 score:8
3. FILET attempts:4 score:4
4. _IPER -ABCDFGLNOSTUVWY attempts:9 score:-1

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1679 🥳 score:60 ⏱️ 0:02:23.358435

📜 1 sessions

Octordle Classic

1. ILIAC attempts:8 score:8
2. BIDDY attempts:10 score:10
3. HEART attempts:4 score:4
4. TERRA attempts:6 score:6
5. LEVER attempts:7 score:7
6. BONUS attempts:9 score:9
7. THEME attempts:11 score:11
8. WORLD attempts:5 score:5

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1659 🥳 score:36 ⏱️ 0:02:28.851691

📜 1 sessions

Sedecordle Classic sedecordle.com

1. PROXY attempts:10 score:1
2. TOXIC attempts:11 score:0
3. PARKA attempts:12 score:1
4. BUSED attempts:19 score:2
5. STALL attempts:13 score:1
6. START attempts:14 score:3
7. LUNAR attempts:5 score:0
8. GRIND attempts:6 score:5
9. DONUT attempts:8 score:0
10. STAMP attempts:15 score:8
11. OLDEN attempts:4 score:0
12. DETOX attempts:9 score:4
13. NEIGH attempts:3 score:0
14. PLUNK attempts:16 score:3
15. MOUND attempts:17 score:1
16. WHALE attempts:7 score:7

# [squareword.org](squareword.org) 🧩 #1672 🥳 7 ⏱️ 0:02:16.549037

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S M A S H
    P E S T O
    A R I A S
    M I D G E
    S T E E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1609 🥳 56 ⏱️ 0:00:40.777068

🤔 57 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 15 chat prompts
🤖 15 dolphin3:latest replies
😱  1 🔥  3 🥵  6 😎  7 🥶 36 🧊  3

     $1 #57 mystery         100.00°C 🥳 1000‰ ~54 used:0 [53]  source:dolphin3
     $2 #42 riddle           67.93°C 😱  999‰  ~1 used:3 [0]   source:dolphin3
     $3 #31 enigma           57.84°C 🔥  996‰  ~4 used:2 [3]   source:dolphin3
     $4 #48 puzzle           54.74°C 🔥  995‰  ~2 used:0 [1]   source:dolphin3
     $5 #47 conundrum        48.11°C 🔥  990‰  ~3 used:0 [2]   source:dolphin3
     $6 #35 enigmatic        45.03°C 🥵  989‰  ~5 used:0 [4]   source:dolphin3
     $7 #56 clue             43.89°C 🥵  987‰  ~6 used:0 [5]   source:dolphin3
     $8 #27 ambiguity        38.89°C 🥵  965‰ ~10 used:6 [9]   source:dolphin3
     $9 #29 confusion        34.70°C 🥵  918‰  ~8 used:4 [7]   source:dolphin3
    $10 #23 uncertainty      34.30°C 🥵  910‰  ~9 used:4 [8]   source:dolphin3
    $11 #53 uncertainly      34.04°C 🥵  906‰  ~7 used:0 [6]   source:dolphin3
    $12 #30 doubt            29.66°C 😎  742‰ ~11 used:0 [10]  source:dolphin3
    $19 #17 teleportation    23.11°C 🥶       ~21 used:2 [20]  source:dolphin3
    $55 #22 transfer         -0.52°C 🧊       ~55 used:0 [54]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1642 🥳 665 ⏱️ 3:08:26.404169

🤔 666 attempts
📜 1 sessions
🫧 88 chat sessions
⁉️ 482 chat prompts
🤖 12 gemma4:12b replies
🤖 16 ornith-1.5:35b replies
🤖 453 dolphin3:latest replies
🔥   1 🥵  26 😎 173 🥶 400 🧊  65

      $1 #666 ponctuel            100.00°C 🥳 1000‰ ~601 used:0   [600]  source:gemma4  
      $2 #576 spécifique           52.47°C 🔥  996‰  ~46 used:102 [45]   source:dolphin3
      $3 #582 particulier          43.30°C 🥵  989‰ ~190 used:36  [189]  source:dolphin3
      $4 #494 complémentaire       41.56°C 🥵  986‰ ~194 used:41  [193]  source:dolphin3
      $5 #183 aide                 40.72°C 🥵  983‰ ~200 used:318 [199]  source:dolphin3
      $6 #450 adapter              40.37°C 🥵  982‰ ~186 used:21  [185]  source:dolphin3
      $7 #116 structure            39.93°C 🥵  981‰ ~199 used:212 [198]  source:dolphin3
      $8 #341 intervenir           38.50°C 🥵  978‰ ~189 used:33  [188]  source:dolphin3
      $9 #365 accompagnement       38.25°C 🥵  975‰  ~55 used:17  [54]   source:dolphin3
     $10 #503 complément           37.97°C 🥵  971‰  ~47 used:11  [46]   source:dolphin3
     $11 #424 divers               37.41°C 🥵  968‰  ~56 used:17  [55]   source:dolphin3
     $29 #587 spécifiquement       32.76°C 😎  899‰   ~4 used:0   [3]    source:dolphin3
    $202 #239 renforcement         21.03°C 🥶       ~201 used:0   [200]  source:dolphin3
    $602 #439 camion               -0.03°C 🧊       ~602 used:0   [601]  source:dolphin3
