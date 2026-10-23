# 2026-10-24

- 🔗 spaceword.org 🧩 2026-10-23 🏁 score 2168 ranked 34.6% 107/309 ⏱️ 0:15:15.242666
- 🔗 wordgrid 🧩 #875 🟪 rarity:0.24 ⏱️ 0:02:58.016373
- 🔗 alfagok.diginaut.net 🧩 #721 🥳 26 ⏱️ 0:00:32.470865
- 🔗 alphaguess.com 🧩 #1188 🥳 32 ⏱️ 0:00:34.590136
- 🔗 dontwordle.com 🧩 #1614 🥳 6 ⏱️ 0:01:37.006751
- 🔗 dictionary.com hurdle 🧩 #1757 🥳 19 ⏱️ 0:04:29.421042
- 🔗 Quordle Classic 🧩 #1734 😦 score:30 ⏱️ 0:03:05.319830
- 🔗 Octordle Classic 🧩 #1734 🥳 score:49 ⏱️ 0:02:07.328397
- 🔗 Sedecordle Classic 🧩 #1714 🥳 score:33 ⏱️ 0:04:42.756046
- 🔗 squareword.org 🧩 #1727 🥳 8 ⏱️ 0:02:23.352626
- 🔗 cemantle.certitudes.org 🧩 #1664 🥳 210 ⏱️ 0:18:30.183657
- 🔗 cemantix.certitudes.org 🧩 #1697 🥳 2298 ⏱️ 2:57:30.076952

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




















# [spaceword.org](spaceword.org) 🧩 2026-10-23 🏁 score 2168 ranked 34.6% 107/309 ⏱️ 0:15:15.242666

📜 2 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 107/309

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ R _ C _ _   
      _ S _ J _ I _ O _ _   
      _ A Z O T E M I A _   
      _ E _ W I L I L Y _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #875 🟪 rarity:0.24 ⏱️ 0:02:58.016373

📜 2 sessions
🌌 🌌 🌌
🌌 🦄 🌌
🌌 🦄 🌌
Rarity: 0.24 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #721 🥳 26 ⏱️ 0:00:32.470865

🤔 26 attempts
📜 1 sessions

    @        [     0] &-teken        
    @+1      [     1] &-tekens       
    @+2      [     2] -cijferig      
    @+3      [     3] -e-mail        
    @+786    [   786] aan            q10 ? ␅
    @+786    [   786] aan            q11 ? after
    @+4713   [  4713] aardappelschil q12 ? ␅
    @+4713   [  4713] aardappelschil q13 ? after
    @+4791   [  4791] aardbeving     q22 ? ␅
    @+4791   [  4791] aardbeving     q23 ? after
    @+4828   [  4828] aarde          q24 ? ␅
    @+4828   [  4828] aarde          q25 ? it
    @+4828   [  4828] aarde          done. it
    @+4868   [  4868] aardgas        q20 ? ␅
    @+4868   [  4868] aardgas        q21 ? before
    @+5078   [  5078] aardst         q18 ? ␅
    @+5078   [  5078] aardst         q19 ? before
    @+5457   [  5457] ablatie        q16 ? ␅
    @+5457   [  5457] ablatie        q17 ? before
    @+6207   [  6207] achter         q14 ? ␅
    @+6207   [  6207] achter         q15 ? before
    @+8646   [  8646] af             q8  ? ␅
    @+8646   [  8646] af             q9  ? before
    @+24874  [ 24874] bad            q6  ? ␅
    @+24874  [ 24874] bad            q7  ? before
    @+49802  [ 49802] boks           q4  ? ␅
    @+49802  [ 49802] boks           q5  ? before
    @+99672  [ 99672] ex             q2  ? ␅
    @+99672  [ 99672] ex             q3  ? before
    @+199631 [199631] lijk           q0  ? ␅
    @+199631 [199631] lijk           q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1188 🥳 32 ⏱️ 0:00:34.590136

🤔 32 attempts
📜 1 sessions

    @        [     0] aa         
    @+98142  [ 98142] mac        q0  ? ␅
    @+98142  [ 98142] mac        q1  ? after
    @+109924 [109924] ne         q6  ? ␅
    @+109924 [109924] ne         q7  ? after
    @+116318 [116318] orb        q8  ? ␅
    @+116318 [116318] orb        q9  ? after
    @+117203 [117203] out        q12 ? ␅
    @+117203 [117203] out        q13 ? after
    @+117963 [117963] outpace    q14 ? ␅
    @+117963 [117963] outpace    q15 ? after
    @+118226 [118226] outs       q16 ? ␅
    @+118226 [118226] outs       q17 ? after
    @+118470 [118470] outsulk    q18 ? ␅
    @+118470 [118470] outsulk    q19 ? after
    @+118590 [118590] outwar     q20 ? ␅
    @+118590 [118590] outwar     q21 ? after
    @+118651 [118651] outwork    q22 ? ␅
    @+118651 [118651] outwork    q23 ? after
    @+118685 [118685] ova        q24 ? ␅
    @+118685 [118685] ova        q25 ? after
    @+118704 [118704] ovariotomy q26 ? ␅
    @+118704 [118704] ovariotomy q27 ? after
    @+118711 [118711] ovation    q28 ? ␅
    @+118711 [118711] ovation    q29 ? after
    @+118714 [118714] oven       q30 ? ␅
    @+118714 [118714] oven       q31 ? it
    @+118714 [118714] oven       done. it
    @+118722 [118722] over       q10 ? ␅
    @+118722 [118722] over       q11 ? before
    @+122718 [122718] parol      q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1614 🥳 6 ⏱️ 0:01:37.006751

📜 1 sessions
💰 score: 16

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:PZAZZ n n n n n remain:6291
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:3110
    ⬜⬜⬜⬜⬜ tried:TOOTH n n n n n remain:868
    ⬜⬜⬜⬜⬜ tried:MUMMY n n n n n remain:237
    ⬜🟨⬜⬜⬜ tried:GRRRL n m n n n remain:24
    ⬜🟩🟩🟩🟩 tried:FEWER n Y Y Y Y remain:2

    Undos used: 1

      2 words remaining
    x 8 unused letters
    = 16 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1757 🥳 19 ⏱️ 0:04:29.421042

📜 1 sessions
💰 score: 9700

    5/6
    TOEAS ⬜⬜🟨🟨⬜
    PALER ⬜🟩⬜🟨⬜
    GAMBE 🟩🟩⬜⬜🟩
    FAUGH 🟨🟩⬜🟨⬜
    GAFFE 🟩🟩🟩🟩🟩
    5/6
    GAFFE ⬜⬜⬜⬜🟨
    DOLES ⬜🟨⬜🟨⬜
    NETOP 🟨🟨⬜🟩⬜
    JIVEY ⬜⬜🟩🟨🟩
    ENVOY 🟩🟩🟩🟩🟩
    4/6
    ENVOY 🟨⬜⬜🟨🟩
    POESY ⬜🟩🟨⬜🟩
    HOLEY ⬜🟩⬜🟩🟩
    BOGEY 🟩🟩🟩🟩🟩
    4/6
    BOGEY ⬜🟨⬜⬜⬜
    TAROS ⬜⬜⬜🟨⬜
    CHINO 🟩⬜⬜🟨🟨
    CLOWN 🟩🟩🟩🟩🟩
    Final 1/2
    NAVEL 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1734 😦 score:30 ⏱️ 0:03:05.319830

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. TOXIN attempts:5 score:5
2. SMART attempts:9 score:9
3. _OUSE ~M -ACDHILNPRTXY attempts:9 score:-1
4. STYLE attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1734 🥳 score:49 ⏱️ 0:02:07.328397

📜 1 sessions

Octordle Classic

1. STUCK attempts:8 score:8
2. SWORD attempts:2 score:2
3. ARDOR attempts:3 score:3
4. REVEL attempts:10 score:10
5. RAINY attempts:6 score:6
6. HOWDY attempts:4 score:4
7. COLON attempts:9 score:9
8. PENNE attempts:7 score:7

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1714 🥳 score:33 ⏱️ 0:04:42.756046

📜 2 sessions

Sedecordle Classic sedecordle.com

1. ATOLL attempts:15 score:1
2. TESTY attempts:7 score:5
3. BASIS attempts:3 score:0
4. NINNY attempts:18 score:3
5. SPREE attempts:5 score:0
6. FIEND attempts:13 score:5
7. PARER attempts:11 score:1
8. SCARE attempts:12 score:1
9. RESET attempts:4 score:0
10. ROCKY attempts:14 score:4
11. GULCH attempts:10 score:1
12. CLICK attempts:16 score:0
13. WOULD attempts:19 score:1
14. OUNCE attempts:9 score:9
15. COWER attempts:20 score:2
16. MIMIC attempts:17 score:0

# [squareword.org](squareword.org) 🧩 #1727 🥳 8 ⏱️ 0:02:23.352626

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    R E S T S
    E X T R A
    R U R A L
    A D A P T
    N E W S Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1664 🥳 210 ⏱️ 0:18:30.183657

🤔 211 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 40 chat prompts
🤖 40 gemma4:12b replies
🔥   1 🥵   9 😎  54 🥶 141 🧊   5

      $1 #211 kidney                100.00°C 🥳 1000‰ ~206 used:0  [205]  source:gemma4
      $2 #200 transplant             65.34°C 🔥  998‰   ~1 used:5  [0]    source:gemma4
      $3 #203 organ                  52.45°C 🥵  989‰   ~2 used:1  [1]    source:gemma4
      $4  #88 surgery                49.78°C 🥵  985‰  ~63 used:30 [62]   source:gemma4
      $5 #209 heart                  47.90°C 🥵  977‰   ~3 used:0  [2]    source:gemma4
      $6  #49 spinal                 46.59°C 🥵  973‰  ~62 used:25 [61]   source:gemma4
      $7  #61 tissue                 46.13°C 🥵  969‰  ~58 used:19 [57]   source:gemma4
      $8 #152 tumor                  44.52°C 🥵  956‰   ~5 used:8  [4]    source:gemma4
      $9 #141 neurological           43.18°C 🥵  944‰   ~7 used:10 [6]    source:gemma4
     $10 #206 donor                  43.17°C 🥵  943‰   ~4 used:0  [3]    source:gemma4
     $11 #167 brain                  41.88°C 🥵  917‰   ~6 used:8  [5]    source:gemma4
     $12 #181 meningioma             40.29°C 😎  888‰   ~8 used:0  [7]    source:gemma4
     $66 #112 resection              28.55°C 🥶        ~68 used:0  [67]   source:gemma4
    $207  #13 savannah               -0.37°C 🧊       ~207 used:0  [206]  source:gemma4

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1697 🥳 2298 ⏱️ 2:57:30.076952

🤔 2299 attempts
📜 3 sessions
🫧 176 chat sessions
⁉️ 869 chat prompts
🤖 106 gemma4:12b replies
🤖 125 dolphin3:latest replies
🤖 284 nemotron-3-nano:30b-cloud replies
🤖 20 flint:latest replies
🤖 333 llama3.2:latest replies
😱    1 🔥    5 🥵   55 😎  313 🥶 1678 🧊  246

       $1 #2299 entrevoir            100.00°C 🥳 1000‰ ~2053 used:0   [2052]  source:gemma4  
       $2 #1889 surgir                49.25°C 😱  999‰    ~2 used:256 [1]     source:nemotron
       $3 #2047 esquisser             46.49°C 🔥  997‰   ~23 used:77  [22]    source:nemotron
       $4 #2286 pressentir            46.49°C 🔥  998‰    ~1 used:8   [0]     source:gemma4  
       $5  #282 obscur                44.67°C 🔥  995‰  ~372 used:718 [371]   source:gemma4  
       $6 #2103 discerner             44.12°C 🔥  993‰   ~10 used:31  [9]     source:nemotron
       $7 #1722 advenir               43.28°C 🔥  991‰   ~19 used:52  [18]    source:nemotron
       $8 #1819 révéler               42.11°C 🥵  989‰   ~24 used:9   [23]    source:nemotron
       $9 #2195 ébaucher              42.10°C 🥵  988‰   ~11 used:4   [10]    source:nemotron
      $10  #711 immense               42.07°C 🥵  987‰  ~374 used:251 [373]   source:llama3.2
      $11  #378 insondable            41.89°C 🥵  986‰  ~373 used:167 [372]   source:dolphin3
      $63 #2165 explorer              36.31°C 😎  899‰   ~25 used:0   [24]    source:nemotron
     $376  #747 éternellement         26.79°C 🥶        ~375 used:0   [374]   source:llama3.2
    $2054 #2169 varier                -0.07°C 🧊       ~2054 used:0   [2053]  source:nemotron
