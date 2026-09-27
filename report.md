# 2026-09-28

- 🔗 wordgrid 🧩 #849 🟪 rarity:0.23 ⏱️ 0:02:54.206848
- 🔗 spaceword.org 🧩 2026-09-27 🏁 score 2172 ranked 17.2% 62/360 ⏱️ 0:53:50.995393
- 🔗 alfagok.diginaut.net 🧩 #695 🥳 26 ⏱️ 0:01:00.256982
- 🔗 alphaguess.com 🧩 #1162 🥳 30 ⏱️ 0:00:30.542722
- 🔗 dontwordle.com 🧩 #1588 🥳 6 ⏱️ 0:01:19.053902
- 🔗 dictionary.com hurdle 🧩 #1731 🥳 18 ⏱️ 0:03:02.639005
- 🔗 Quordle Classic 🧩 #1708 😦 score:29 ⏱️ 0:02:25.713892
- 🔗 Octordle Classic 🧩 #1708 🥳 score:60 ⏱️ 0:01:58.688770
- 🔗 Sedecordle Classic 🧩 #1688 🥳 score:44 ⏱️ 0:03:04.759580
- 🔗 squareword.org 🧩 #1701 🥳 7 ⏱️ 0:02:25.531131
- 🔗 cemantle.certitudes.org 🧩 #1638 🥳 207 ⏱️ 0:33:33.573241
- 🔗 cemantix.certitudes.org 🧩 #1671 🥳 401 ⏱️ 0:50:36.738638

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








# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #849 🟪 rarity:0.23 ⏱️ 0:02:54.206848

📜 2 sessions
🦄 🦄 🌌
🌌 🦄 🌌
🦄 🌌 🌌
Rarity: 0.23 🟪

# [spaceword.org](spaceword.org) 🧩 2026-09-27 🏁 score 2172 ranked 17.2% 62/360 ⏱️ 0:53:50.995393

📜 3 sessions
- tiles: 21/21
- score: 2172 bonus: +72
- rank: 62/360

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ X E B E C _ V _   
      _ _ _ T A N U K I _   
      _ _ _ _ I _ T _ M _   
      _ _ A U T O E D _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #695 🥳 26 ⏱️ 0:01:00.256982

🤔 26 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+199531 [199531] lij        q0  ? ␅
    @+199531 [199531] lij        q1  ? after
    @+199531 [199531] lij        q2  ? ␅
    @+199531 [199531] lij        q3  ? after
    @+299484 [299484] schrok     q4  ? ␅
    @+299484 [299484] schrok     q5  ? after
    @+311726 [311726] spier      q10 ? ␅
    @+311726 [311726] spier      q11 ? after
    @+317918 [317918] stem       q12 ? ␅
    @+317918 [317918] stem       q13 ? after
    @+318274 [318274] steno      q20 ? ␅
    @+318274 [318274] steno      q21 ? after
    @+318349 [318349] ster       q24 ? ␅
    @+318349 [318349] ster       q25 ? it
    @+318349 [318349] ster       done. it
    @+318431 [318431] sterf      q22 ? ␅
    @+318431 [318431] sterf      q23 ? before
    @+318655 [318655] sterven    q18 ? ␅
    @+318655 [318655] sterven    q19 ? before
    @+319404 [319404] stimulator q16 ? ␅
    @+319404 [319404] stimulator q17 ? before
    @+320891 [320891] straat     q14 ? ␅
    @+320891 [320891] straat     q15 ? before
    @+324120 [324120] sub        q8  ? ␅
    @+324120 [324120] sub        q9  ? before
    @+349469 [349469] vakanties  q6  ? ␅
    @+349469 [349469] vakanties  q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1162 🥳 30 ⏱️ 0:00:30.542722

🤔 30 attempts
📜 1 sessions

    @        [     0] aa         
    @+98142  [ 98142] mac        q0  ? ␅
    @+98142  [ 98142] mac        q1  ? after
    @+98142  [ 98142] mac        q2  ? ␅
    @+98142  [ 98142] mac        q3  ? after
    @+147306 [147306] rho        q4  ? ␅
    @+147306 [147306] rho        q5  ? after
    @+150202 [150202] sal        q12 ? ␅
    @+150202 [150202] sal        q13 ? after
    @+151722 [151722] scan       q14 ? ␅
    @+151722 [151722] scan       q15 ? after
    @+152514 [152514] scombrid   q16 ? ␅
    @+152514 [152514] scombrid   q17 ? after
    @+152910 [152910] scried     q18 ? ␅
    @+152910 [152910] scried     q19 ? after
    @+152944 [152944] script     q24 ? ␅
    @+152944 [152944] script     q25 ? after
    @+152977 [152977] scrods     q26 ? ␅
    @+152977 [152977] scrods     q27 ? after
    @+152984 [152984] scroll     q28 ? ␅
    @+152984 [152984] scroll     q29 ? it
    @+152984 [152984] scroll     done. it
    @+153009 [153009] scrotal    q22 ? ␅
    @+153009 [153009] scrotal    q23 ? before
    @+153107 [153107] scrutinize q20 ? ␅
    @+153107 [153107] scrutinize q21 ? before
    @+153306 [153306] sea        q10 ? ␅
    @+153306 [153306] sea        q11 ? before
    @+159588 [159588] slug       q8  ? ␅
    @+159588 [159588] slug       q9  ? before
    @+171906 [171906] tag        q7  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1588 🥳 6 ⏱️ 0:01:19.053902

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:YUMMY n n n n n remain:7572
    ⬜⬜⬜⬜⬜ tried:COCOS n n n n n remain:1954
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:694
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:290
    ⬜⬜⬜⬜🟩 tried:FEEZE n n n n Y remain:25
    ⬜⬜🟩⬜🟩 tried:AWAKE n n Y n Y remain:3

    Undos used: 2

      3 words remaining
    x 8 unused letters
    = 24 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1731 🥳 18 ⏱️ 0:03:02.639005

📜 1 sessions
💰 score: 9800

    4/6
    STARE 🟩🟨⬜⬜⬜
    SIGHT 🟩🟨⬜⬜🟩
    SLIPT 🟩⬜🟩⬜🟩
    SWIFT 🟩🟩🟩🟩🟩
    4/6
    SWIFT 🟩⬜⬜⬜⬜
    SLAKE 🟩⬜⬜⬜⬜
    SPRUG 🟩⬜🟨🟩⬜
    SCOUR 🟩🟩🟩🟩🟩
    4/6
    SCOUR ⬜⬜⬜⬜⬜
    ANILE ⬜🟨⬜⬜🟨
    TYNED ⬜🟨🟨🟨🟨
    NEEDY 🟩🟩🟩🟩🟩
    4/6
    NEEDY ⬜⬜⬜⬜⬜
    ACROS 🟨⬜🟨⬜🟨
    SMART 🟨⬜🟩🟨🟨
    TRASH 🟩🟩🟩🟩🟩
    Final 2/2
    PARVO ⬜⬜🟨⬜⬜
    DRIED 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1708 😦 score:29 ⏱️ 0:02:25.713892

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. BRUNT attempts:7 score:-1
2. TORSO attempts:5 score:5
3. STONE attempts:6 score:6
4. HEATH attempts:9 score:9

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1708 🥳 score:60 ⏱️ 0:01:58.688770

📜 1 sessions

Octordle Classic

1. CAPER attempts:8 score:8
2. PUSHY attempts:3 score:3
3. CLEAR attempts:9 score:9
4. FEMME attempts:6 score:6
5. SEDAN attempts:10 score:10
6. GAUGE attempts:12 score:12
7. EGRET attempts:5 score:5
8. MUCKY attempts:7 score:7

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1688 🥳 score:44 ⏱️ 0:03:04.759580

📜 1 sessions

Sedecordle Classic sedecordle.com

1. EGRET attempts:6 score:0
2. STEEP attempts:9 score:6
3. BISON attempts:4 score:0
4. RIDGE attempts:3 score:4
5. OFFER attempts:10 score:1
6. EAGLE attempts:7 score:0
7. LYRIC attempts:5 score:0
8. FUNNY attempts:11 score:5
9. TRICK attempts:8 score:0
10. COAST attempts:12 score:8
11. LEAKY attempts:13 score:1
12. THINK attempts:15 score:3
13. DOWDY attempts:18 score:1
14. SPAWN attempts:14 score:8
15. ESSAY attempts:16 score:1
16. WITTY attempts:17 score:6

# [squareword.org](squareword.org) 🧩 #1701 🥳 7 ⏱️ 0:02:25.531131

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T E A M
    P R U N E
    A O R T A
    S P O I L
    M E S S Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1638 🥳 207 ⏱️ 0:33:33.573241

🤔 208 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 41 chat prompts
🤖 12 dolphin3:latest replies
🤖 1 gemma4:26b replies
🤖 26 gemma4:12b replies
🔥   4 🥵  15 😎  40 🥶 133 🧊  15

      $1 #208 ranking          100.00°C 🥳 1000‰ ~193 used:0  [192]  source:dolphin3  
      $2 #139 rank              62.74°C 🔥  998‰  ~17 used:22 [16]   source:gemma4:12b
      $3 #154 echelon           57.05°C 🔥  997‰  ~14 used:12 [13]   source:gemma4:12b
      $4 #142 hierarchy         40.78°C 🔥  994‰  ~12 used:11 [11]   source:gemma4:12b
      $5 #165 tier              40.49°C 🔥  993‰  ~13 used:11 [12]   source:gemma4:12b
      $6 #159 level             37.39°C 🥵  987‰   ~1 used:0  [0]    source:gemma4:12b
      $7 #146 seniority         36.42°C 🥵  986‰   ~2 used:1  [1]    source:gemma4:12b
      $8 #122 prestige          35.72°C 🥵  985‰  ~18 used:3  [17]   source:gemma4:12b
      $9 #173 priority          35.54°C 🥵  982‰   ~3 used:0  [2]    source:gemma4:12b
     $10 #153 position          35.32°C 🥵  981‰   ~4 used:0  [3]    source:gemma4:12b
     $11 #126 status            33.62°C 🥵  976‰  ~15 used:2  [14]   source:gemma4:12b
     $21 #143 notoriety         25.17°C 😎  899‰  ~20 used:0  [19]   source:gemma4:12b
     $61  #45 power             15.38°C 🥶        ~60 used:0  [59]   source:gemma4:12b
    $194 #191 zone              -0.91°C 🧊       ~194 used:0  [193]  source:gemma4:12b

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1671 🥳 401 ⏱️ 0:50:36.738638

🤔 402 attempts
📜 1 sessions
🫧 60 chat sessions
⁉️ 376 chat prompts
🤖 17 ornith-1.5:35b replies
🤖 258 dolphin3:latest replies
🤖 101 gemma4:12b replies
🔥   8 🥵  33 😎 130 🥶 205 🧊  25

      $1 #402 acquis             100.00°C 🥳 1000‰ ~377 used:0   [376]  source:ornith  
      $2 #145 validation          51.55°C 🔥  998‰ ~170 used:282 [169]  source:gemma4  
      $3  #83 compétence          48.98°C 🔥  997‰ ~168 used:186 [167]  source:gemma4  
      $4  #77 formation           46.71°C 🔥  996‰  ~38 used:76  [37]   source:gemma4  
      $5 #125 diplôme             46.46°C 🔥  995‰   ~3 used:45  [2]    source:gemma4  
      $6 #285 connaissance        44.09°C 🔥  994‰   ~4 used:45  [3]    source:dolphin3
      $7 #123 qualification       44.01°C 🔥  993‰   ~1 used:44  [0]    source:gemma4  
      $8 #117 expérience          43.74°C 🔥  991‰   ~5 used:45  [4]    source:gemma4  
      $9 #244 professionnel       43.01°C 🔥  990‰   ~2 used:44  [1]    source:gemma4  
     $10  #79 apprentissage       42.28°C 🥵  989‰   ~6 used:5   [5]    source:gemma4  
     $11 #303 valider             41.60°C 🥵  985‰   ~7 used:5   [6]    source:dolphin3
     $43 #137 motivation          30.36°C 😎  898‰  ~40 used:0   [39]   source:gemma4  
    $173 #249 référence           18.66°C 🥶       ~175 used:0   [174]  source:gemma4  
    $378  #25 montage             -0.18°C 🧊       ~378 used:0   [377]  source:gemma4  
