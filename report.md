# 2026-08-23

- 🔗 spaceword.org 🧩 2026-08-22 🏁 score 2173 ranked 8.1% 25/310 ⏱️ 0:40:11.367234
- 🔗 wordgrid 🧩 #813 🟪 rarity:0.17 ⏱️ 0:01:59.620194
- 🔗 alfagok.diginaut.net 🧩 #659 🥳 26 ⏱️ 0:00:40.509986
- 🔗 alphaguess.com 🧩 #1126 🥳 30 ⏱️ 0:00:41.967932
- 🔗 dontwordle.com 🧩 #1552 🥳 6 ⏱️ 0:01:31.607697
- 🔗 dictionary.com hurdle 🧩 #1695 😦 22 ⏱️ 0:04:20.886471
- 🔗 Quordle Classic 🧩 #1672 🥳 score:24 ⏱️ 0:02:26.832834
- 🔗 Octordle Classic 🧩 #1672 🥳 score:58 ⏱️ 0:01:50.295739
- 🔗 Sedecordle Classic 🧩 #1652 🥳 score:44 ⏱️ 0:02:21.781003
- 🔗 squareword.org 🧩 #1665 🥳 8 ⏱️ 0:02:16.485982
- 🔗 cemantle.certitudes.org 🧩 #1602 🥳 126 ⏱️ 0:01:31.520123
- 🔗 cemantix.certitudes.org 🧩 #1635 🥳 510 ⏱️ 0:22:55.064897

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



















# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #813 🟪 rarity:0.17 ⏱️ 0:01:59.620194

📜 2 sessions
🌌 🌌 🌌
🦄 🦄 🦄
🌌 🦄 🦄
Rarity: 0.17 🟪

# [spaceword.org](spaceword.org) 🧩 2026-08-22 🏁 score 2173 ranked 8.1% 25/310 ⏱️ 0:40:11.367234

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 25/310

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ K O R _ _ _   
      _ _ _ _ _ _ E _ _ _   
      _ _ _ _ S U N _ _ _   
      _ _ _ _ O _ V _ _ _   
      _ _ _ _ U D O _ _ _   
      _ _ _ _ R A I _ _ _   
      _ _ _ _ G _ _ _ _ _   
      _ _ _ _ U H _ _ _ _   
      _ _ _ _ M E W _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #659 🥳 26 ⏱️ 0:00:40.509986

🤔 26 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+49811  [ 49811] boks       q4  ? ␅
    @+49811  [ 49811] boks       q5  ? after
    @+74714  [ 74714] dc         q6  ? ␅
    @+74714  [ 74714] dc         q7  ? after
    @+77686  [ 77686] der        q12 ? ␅
    @+77686  [ 77686] der        q13 ? after
    @+77716  [ 77716] derde      q24 ? ␅
    @+77716  [ 77716] derde      q25 ? it
    @+77716  [ 77716] derde      done. it
    @+77783  [ 77783] dereguleer q22 ? ␅
    @+77783  [ 77783] dereguleer q23 ? before
    @+77887  [ 77887] des        q20 ? ␅
    @+77887  [ 77887] des        q21 ? before
    @+78428  [ 78428] detentie   q16 ? ␅
    @+78428  [ 78428] detentie   q17 ? before
    @+79187  [ 79187] dicht      q14 ? ␅
    @+79187  [ 79187] dicht      q15 ? before
    @+80845  [ 80845] dijk       q10 ? ␅
    @+80845  [ 80845] dijk       q11 ? before
    @+87171  [ 87171] draag      q8  ? ␅
    @+87171  [ 87171] draag      q9  ? before
    @+99690  [ 99690] ex         q2  ? ␅
    @+99690  [ 99690] ex         q3  ? before
    @+199649 [199649] lijk       q0  ? ␅
    @+199649 [199649] lijk       q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1126 🥳 30 ⏱️ 0:00:41.967932

🤔 30 attempts
📜 1 sessions

    @       [    0] aa              
    @+47378 [47378] dis             q2  ? ␅
    @+47378 [47378] dis             q3  ? after
    @+60017 [60017] eyewitness      q6  ? ␅
    @+60017 [60017] eyewitness      q7  ? after
    @+66309 [66309] free            q8  ? ␅
    @+66309 [66309] free            q9  ? after
    @+69482 [69482] geode           q10 ? ␅
    @+69482 [69482] geode           q11 ? after
    @+69920 [69920] gi              q14 ? ␅
    @+69920 [69920] gi              q15 ? after
    @+70493 [70493] glass           q16 ? ␅
    @+70493 [70493] glass           q17 ? after
    @+70741 [70741] glob            q18 ? ␅
    @+70741 [70741] glob            q19 ? after
    @+70867 [70867] gloss           q20 ? ␅
    @+70867 [70867] gloss           q21 ? after
    @+70917 [70917] glout           q24 ? ␅
    @+70917 [70917] glout           q25 ? after
    @+70921 [70921] glove           q28 ? ␅
    @+70921 [70921] glove           q29 ? it
    @+70921 [70921] glove           done. it
    @+70931 [70931] glow            q26 ? ␅
    @+70931 [70931] glow            q27 ? before
    @+70970 [70970] glucose         q22 ? ␅
    @+70970 [70970] glucose         q23 ? before
    @+71072 [71072] glyceraldehydes q12 ? ␅
    @+71072 [71072] glyceraldehydes q13 ? before
    @+72662 [72662] green           q4  ? ␅
    @+72662 [72662] green           q5  ? before
    @+98147 [98147] mac             q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1552 🥳 6 ⏱️ 0:01:31.607697

📜 1 sessions
💰 score: 21

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:MAMBA n n n n n remain:5774
    ⬜⬜⬜⬜⬜ tried:ESSES n n n n n remain:1193
    ⬜⬜⬜⬜⬜ tried:GONZO n n n n n remain:280
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:85
    ⬜⬜⬜⬜⬜ tried:CRUCK n n n n n remain:14
    ⬜🟩⬜⬜⬜ tried:VIVID n Y n n n remain:3

    Undos used: 4

      3 words remaining
    x 7 unused letters
    = 21 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1695 😦 22 ⏱️ 0:04:20.886471

📜 1 sessions
💰 score: 4480

    4/6
    LORES ⬜⬜🟨🟩⬜
    URAEI ⬜🟩⬜🟩🟨
    FRIED 🟨🟩🟩🟩⬜
    BRIEF 🟩🟩🟩🟩🟩
    4/6
    BRIEF ⬜⬜⬜🟨⬜
    STALE ⬜⬜⬜⬜🟩
    NUDGE 🟨🟨🟩⬜🟩
    UNDUE 🟩🟩🟩🟩🟩
    6/6
    UNDUE 🟨⬜⬜⬜⬜
    LUSTY 🟨🟩⬜⬜⬜
    QUAIL ⬜🟩🟨⬜🟨
    VULVA ⬜🟩🟩⬜🟨
    GOPIK 🟩⬜⬜⬜⬜
    GULAG 🟩🟩🟩🟩🟩
    6/6
    GULAG ⬜🟨🟨⬜⬜
    LOTUS 🟨⬜⬜🟨🟨
    PLUSH ⬜🟩🟩🟩🟩
    BLUSH ⬜🟩🟩🟩🟩
    FLUSH ⬜🟩🟩🟩🟩
    SLUSH 🟩🟩🟩🟩🟩
    Final 2/2
    ????? 🟩⬜🟨🟩🟨
    ????? 🟩⬜🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1672 🥳 score:24 ⏱️ 0:02:26.832834

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. CHASM attempts:4 score:4
2. BLAME attempts:6 score:6
3. PARER attempts:9 score:9
4. BYLAW attempts:5 score:5

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1672 🥳 score:58 ⏱️ 0:01:50.295739

📜 1 sessions

Octordle Classic

1. TIGHT attempts:12 score:12
2. PURER attempts:10 score:10
3. CHORE attempts:4 score:4
4. SATYR attempts:3 score:3
5. ABATE attempts:7 score:7
6. GLASS attempts:6 score:6
7. UNCUT attempts:5 score:5
8. POUND attempts:11 score:11

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1652 🥳 score:44 ⏱️ 0:02:21.781003

📜 1 sessions

Sedecordle Classic sedecordle.com

1. MARCH attempts:5 score:0
2. MINOR attempts:4 score:5
3. ETHOS attempts:3 score:0
4. LIVER attempts:18 score:3
5. SLEPT attempts:8 score:0
6. LUCID attempts:12 score:8
7. ROGUE attempts:13 score:1
8. PROXY attempts:10 score:3
9. WOULD attempts:11 score:1
10. CAROL attempts:6 score:1
11. CREPE attempts:7 score:0
12. SASSY attempts:19 score:7
13. SPRIG attempts:9 score:0
14. BLOKE attempts:14 score:9
15. MAGMA attempts:15 score:1
16. MOWER attempts:16 score:5

# [squareword.org](squareword.org) 🧩 #1665 🥳 8 ⏱️ 0:02:16.485982

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟨 🟩 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P E A R S
    A L L O W
    G U I L E
    E D G E D
    D E N S E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1602 🥳 126 ⏱️ 0:01:31.520123

🤔 127 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 26 chat prompts
🤖 14 ornith-1.5:35b replies
🤖 12 dolphin3:latest replies
🥵 12 😎 21 🥶 90 🧊  3

      $1 #127 invitation        100.00°C 🥳 1000‰ ~124 used:0  [123]  source:ornith  
      $2  #64 greeting           35.36°C 🥵  980‰  ~31 used:14 [30]   source:dolphin3
      $3  #89 cordially          35.24°C 🥵  978‰   ~9 used:4  [8]    source:ornith  
      $4  #54 letter             35.04°C 🥵  977‰  ~11 used:9  [10]   source:dolphin3
      $5  #60 salutation         34.60°C 🥵  971‰  ~10 used:5  [9]    source:dolphin3
      $6 #117 reception          34.49°C 🥵  969‰   ~5 used:2  [4]    source:ornith  
      $7  #98 farewell           33.26°C 🥵  964‰   ~1 used:0  [0]    source:ornith  
      $8  #70 email              32.54°C 🥵  957‰   ~8 used:3  [7]    source:dolphin3
      $9  #76 formal             31.68°C 🥵  947‰   ~6 used:2  [5]    source:ornith  
     $10  #77 informal           31.51°C 🥵  944‰   ~2 used:1  [1]    source:ornith  
     $11  #83 welcome            30.60°C 🥵  933‰   ~7 used:2  [6]    source:ornith  
     $14  #73 missive            28.54°C 😎  893‰  ~12 used:0  [11]   source:dolphin3
     $35 #115 hostess            17.80°C 🥶        ~40 used:0  [39]   source:ornith  
    $125  #71 digital            -0.64°C 🧊       ~125 used:0  [124]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1635 🥳 510 ⏱️ 0:22:55.064897

🤔 511 attempts
📜 1 sessions
🫧 33 chat sessions
⁉️ 176 chat prompts
🤖 44 qwen3.5:9b replies
🤖 94 gemma4:12b replies
🤖 30 ornith-1.5:35b replies
🤖 8 dolphin3:latest replies
🔥   2 🥵  12 😎  78 🥶 393 🧊  25

      $1 #511 poing           100.00°C 🥳 1000‰ ~486 used:0   [485]  source:qwen3   
      $2 #452 coup             44.26°C 🔥  992‰   ~5 used:13  [4]    source:qwen3   
      $3 #431 frapper          43.88°C 🔥  990‰   ~6 used:14  [5]    source:qwen3   
      $4 #502 assommer         43.13°C 🥵  987‰   ~7 used:2   [6]    source:qwen3   
      $5 #477 violemment       42.77°C 🥵  982‰   ~8 used:2   [7]    source:qwen3   
      $6 #444 assener          42.00°C 🥵  978‰   ~9 used:2   [8]    source:qwen3   
      $7 #446 cogner           41.77°C 🥵  976‰  ~10 used:2   [9]    source:qwen3   
      $8  #66 furieux          39.26°C 🥵  958‰  ~92 used:135 [91]   source:dolphin3
      $9 #445 balancer         39.21°C 🥵  957‰   ~1 used:1   [0]    source:qwen3   
     $10  #84 violent          39.03°C 🥵  951‰  ~89 used:85  [88]   source:ornith  
     $11 #475 transpercer      37.13°C 🥵  928‰   ~2 used:0   [1]    source:qwen3   
     $16 #408 arme             35.74°C 😎  899‰  ~45 used:2   [44]   source:qwen3   
     $94 #252 horrible         24.14°C 🥶        ~93 used:0   [92]   source:gemma4  
    $487  #10 éphémère         -0.17°C 🧊       ~487 used:0   [486]  source:ornith  
