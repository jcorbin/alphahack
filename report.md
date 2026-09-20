# 2026-09-21

- 🔗 spaceword.org 🧩 2026-09-20 🏁 score 2168 ranked 44.8% 151/337 ⏱️ 0:35:50.873220
- 🔗 wordgrid 🧩 #842 🟪 rarity:0.21 ⏱️ 0:02:44.457785
- 🔗 alfagok.diginaut.net 🧩 #688 🥳 32 ⏱️ 0:00:40.905818
- 🔗 alphaguess.com 🧩 #1155 🥳 26 ⏱️ 0:00:31.728551
- 🔗 dontwordle.com 🧩 #1581 🥳 6 ⏱️ 0:01:29.551674
- 🔗 dictionary.com hurdle 🧩 #1724 🥳 17 ⏱️ 0:02:24.775697
- 🔗 cemantix.certitudes.org 🧩 #1664 🥳 356 ⏱️ 0:12:43.515568
- 🔗 cemantle.certitudes.org 🧩 #1631 🥳 90 ⏱️ 0:01:29.575379
- 🔗 Quordle Classic 🧩 #1701 🥳 score:20 ⏱️ 0:02:51.931806
- 🔗 Octordle Classic 🧩 #1701 🥳 score:63 ⏱️ 0:02:03.042530
- 🔗 Sedecordle Classic 🧩 #1681 🥳 score:39 ⏱️ 0:01:56.529654
- 🔗 squareword.org 🧩 #1694 🥳 7 ⏱️ 0:01:58.454518

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









# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 2026-09-17 🤔 rarity:nan ⏱️ 0:00:25.671340

📜 1 sessions
❓ ❓ ❓
❓ ❓ ❓
❓ ❓ ❓




# [spaceword.org](spaceword.org) 🧩 2026-09-20 🏁 score 2168 ranked 44.8% 151/337 ⏱️ 0:35:50.873220

📜 6 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 151/337

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ N _ J _ _ _   
      _ _ _ F A _ O _ _ _   
      _ _ _ A U N T _ _ _   
      _ _ _ _ S O _ _ _ _   
      _ _ _ V E T O _ _ _   
      _ _ _ _ A I _ _ _ _   
      _ _ _ _ _ C _ _ _ _   
      _ _ _ W Y E _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #842 🟪 rarity:0.21 ⏱️ 0:02:44.457785

📜 2 sessions
🦄 🌌 🌌
🦄 🌌 🌌
🌌 🌌 🦄
Rarity: 0.21 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #688 🥳 32 ⏱️ 0:00:40.905818

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken         
    @+99675  [ 99675] ex              q2  ? ␅
    @+99675  [ 99675] ex              q3  ? after
    @+149570 [149570] huishoud        q4  ? ␅
    @+149570 [149570] huishoud        q5  ? after
    @+174468 [174468] kind            q6  ? ␅
    @+174468 [174468] kind            q7  ? after
    @+186959 [186959] krom            q8  ? ␅
    @+186959 [186959] krom            q9  ? after
    @+188191 [188191] kunst           q14 ? ␅
    @+188191 [188191] kunst           q15 ? after
    @+189119 [189119] kwaads          q16 ? ␅
    @+189119 [189119] kwaads          q17 ? after
    @+189570 [189570] kwant           q18 ? ␅
    @+189570 [189570] kwant           q19 ? after
    @+189798 [189798] kweek           q20 ? ␅
    @+189798 [189798] kweek           q21 ? after
    @+189927 [189927] kwel            q22 ? ␅
    @+189927 [189927] kwel            q23 ? after
    @+189957 [189957] kwelintensiteit q26 ? ␅
    @+189957 [189957] kwelintensiteit q27 ? after
    @+189972 [189972] kwelwater       q28 ? ␅
    @+189972 [189972] kwelwater       q29 ? after
    @+189978 [189978] kwestie         q30 ? ␅
    @+189978 [189978] kwestie         q31 ? it
    @+189978 [189978] kwestie         done. it
    @+189986 [189986] kwets           q24 ? ␅
    @+189986 [189986] kwets           q25 ? before
    @+190065 [190065] kwijt           q12 ? ␅
    @+190065 [190065] kwijt           q13 ? before
    @+193199 [193199] lat             q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1155 🥳 26 ⏱️ 0:00:31.728551

🤔 26 attempts
📜 1 sessions

    @        [     0] aa        
    @+1      [     1] aah       
    @+2      [     2] aahed     
    @+3      [     3] aahing    
    @+98142  [ 98142] mac       q0  ? ␅
    @+98142  [ 98142] mac       q1  ? after
    @+147306 [147306] rho       q2  ? ␅
    @+147306 [147306] rho       q3  ? after
    @+153306 [153306] sea       q8  ? ␅
    @+153306 [153306] sea       q9  ? after
    @+154872 [154872] seraph    q12 ? ␅
    @+154872 [154872] seraph    q13 ? after
    @+155613 [155613] sham      q14 ? ␅
    @+155613 [155613] sham      q15 ? after
    @+155890 [155890] she       q16 ? ␅
    @+155890 [155890] she       q17 ? after
    @+156026 [156026] sheik     q20 ? ␅
    @+156026 [156026] sheik     q21 ? after
    @+156052 [156052] shell     q24 ? ␅
    @+156052 [156052] shell     q25 ? it
    @+156052 [156052] shell     done. it
    @+156097 [156097] shelties  q22 ? ␅
    @+156097 [156097] shelties  q23 ? before
    @+156167 [156167] shetlands q18 ? ␅
    @+156167 [156167] shetlands q19 ? before
    @+156443 [156443] shit      q10 ? ␅
    @+156443 [156443] shit      q11 ? before
    @+159588 [159588] slug      q6  ? ␅
    @+159588 [159588] slug      q7  ? before
    @+171906 [171906] tag       q4  ? ␅
    @+171906 [171906] tag       q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1581 🥳 6 ⏱️ 0:01:29.551674

📜 1 sessions
💰 score: 12

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:7266
    ⬜⬜⬜⬜⬜ tried:CANNA n n n n n remain:2583
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:1351
    ⬜⬜⬜⬜⬜ tried:WHERE n n n n n remain:154
    ⬜⬜⬜⬜⬜ tried:JUGUM n n n n n remain:33
    🟨🟨⬜⬜🟨 tried:POTTO m m n n m remain:2

    Undos used: 3

      2 words remaining
    x 6 unused letters
    = 12 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1724 🥳 17 ⏱️ 0:02:24.775697

📜 1 sessions
💰 score: 9900

    4/6
    SNARE ⬜⬜⬜⬜⬜
    DOILY ⬜⬜🟩🟨⬜
    FLICK ⬜🟩🟩🟨⬜
    CLIMB 🟩🟩🟩🟩🟩
    5/6
    CLIMB ⬜⬜⬜⬜⬜
    SORTA ⬜⬜🟨⬜⬜
    NUDER 🟨⬜⬜🟩🟨
    GREEN ⬜🟩🟩🟩🟩
    PREEN 🟩🟩🟩🟩🟩
    3/6
    PREEN ⬜⬜⬜⬜🟨
    UNAIS ⬜🟨🟨🟩⬜
    MANIA 🟩🟩🟩🟩🟩
    4/6
    MANIA ⬜⬜🟨⬜⬜
    NOSED 🟨🟨⬜⬜⬜
    CLOWN ⬜⬜🟨⬜🟨
    UNBOX 🟩🟩🟩🟩🟩
    Final 1/2
    LURCH 🟩🟩🟩🟩🟩

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1664 🥳 356 ⏱️ 0:12:43.515568

🤔 357 attempts
📜 1 sessions
🫧 16 chat sessions
⁉️ 84 chat prompts
🤖 16 dolphin3:latest replies
🤖 68 gemma4:12b replies
😱   1 🔥   2 🥵  14 😎  70 🥶 220 🧊  49

      $1 #357 réformer          100.00°C 🥳 1000‰ ~308 used:0   [307]  source:dolphin3
      $2 #130 réforme            76.00°C 😱  999‰   ~3 used:111 [2]    source:gemma4  
      $3 #162 gouvernement       53.08°C 🔥  996‰  ~16 used:43  [15]   source:gemma4  
      $4 #333 réformateur        50.87°C 🔥  994‰   ~1 used:6   [0]    source:dolphin3
      $5 #148 modernisation      44.21°C 🥵  987‰  ~81 used:19  [80]   source:gemma4  
      $6 #191 parlement          44.18°C 🥵  986‰   ~6 used:3   [5]    source:gemma4  
      $7 #176 loi                43.08°C 🥵  983‰   ~7 used:3   [6]    source:gemma4  
      $8 #165 politique          42.48°C 🥵  979‰   ~8 used:3   [7]    source:gemma4  
      $9 #121 institution        42.12°C 🥵  976‰   ~9 used:3   [8]    source:gemma4  
     $10 #313 fiscalité          39.48°C 🥵  964‰   ~4 used:2   [3]    source:dolphin3
     $11 #320 gouvernemental     38.38°C 🥵  957‰   ~5 used:2   [4]    source:dolphin3
     $19 #194 république         34.00°C 😎  875‰  ~17 used:0   [16]   source:gemma4  
     $89 #319 financier          22.30°C 🥶        ~92 used:0   [91]   source:dolphin3
    $309 #236 agilité            -0.29°C 🧊       ~309 used:0   [308]  source:gemma4  

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1631 🥳 90 ⏱️ 0:01:29.575379

🤔 91 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 15 chat prompts
🤖 15 gemma4:12b replies
🥵  4 😎 10 🥶 73 🧊  3

     $1 #91 highway        100.00°C 🥳 1000‰ ~88 used:0 [87]  source:gemma4
     $2 #75 boulevard       49.91°C 🥵  980‰  ~1 used:2 [0]   source:gemma4
     $3 #72 corridor        49.02°C 🥵  977‰  ~2 used:4 [1]   source:gemma4
     $4 #56 border          42.23°C 🥵  940‰  ~4 used:8 [3]   source:gemma4
     $5 #69 checkpoint      38.62°C 🥵  913‰  ~3 used:5 [2]   source:gemma4
     $6 #76 crossing        35.66°C 😎  873‰  ~5 used:0 [4]   source:gemma4
     $7 #83 patrol          33.64°C 😎  837‰  ~6 used:0 [5]   source:gemma4
     $8 #60 fence           28.91°C 😎  646‰  ~7 used:1 [6]   source:gemma4
     $9 #87 station         28.22°C 😎  615‰  ~8 used:0 [7]   source:gemma4
    $10 #88 toll            26.68°C 😎  531‰  ~9 used:0 [8]   source:gemma4
    $11 #57 frontier        26.09°C 😎  498‰ ~10 used:0 [9]   source:gemma4
    $12 #89 avenue          24.78°C 😎  395‰ ~11 used:0 [10]  source:gemma4
    $16 #73 aisle           19.50°C 🥶       ~20 used:0 [19]  source:gemma4
    $89 #37 plasma          -1.69°C 🧊       ~89 used:0 [88]  source:gemma4

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1701 🥳 score:20 ⏱️ 0:02:51.931806

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. WAXEN attempts:8 score:8
2. HIPPO attempts:4 score:4
3. PETAL attempts:5 score:5
4. LEASH attempts:3 score:3

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1701 🥳 score:63 ⏱️ 0:02:03.042530

📜 1 sessions

Octordle Classic

1. YOUTH attempts:4 score:4
2. TARDY attempts:5 score:5
3. UPSET attempts:11 score:11
4. GRADE attempts:6 score:6
5. BILLY attempts:13 score:13
6. ALARM attempts:7 score:7
7. WHILE attempts:8 score:8
8. TROVE attempts:9 score:9

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1681 🥳 score:39 ⏱️ 0:01:56.529654

📜 1 sessions

Sedecordle Classic sedecordle.com

1. JEWEL attempts:17 score:1
2. MANGY attempts:11 score:7
3. MODAL attempts:12 score:1
4. ERECT attempts:5 score:2
5. GAUNT attempts:4 score:0
6. AGREE attempts:3 score:4
7. SPERM attempts:10 score:1
8. SOLID attempts:9 score:0
9. HAPPY attempts:15 score:1
10. CACTI attempts:6 score:5
11. PIXEL attempts:13 score:1
12. TRUNK attempts:7 score:3
13. EBONY attempts:8 score:0
14. HAVEN attempts:16 score:8
15. SHONE attempts:14 score:1
16. SKILL attempts:18 score:4

# [squareword.org](squareword.org) 🧩 #1694 🥳 7 ⏱️ 0:01:58.454518

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟨 🟨 🟨
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    D R I F T
    R A C E R
    A T O N E
    W I N C E
    N O S E D
