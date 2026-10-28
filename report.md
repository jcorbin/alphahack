# 2026-10-29

- 🔗 spaceword.org 🧩 2026-10-28 🏁 score 2168 ranked 47.7% 143/300 ⏱️ 0:05:49.838499
- 🔗 wordgrid 🧩 #880 🌌 rarity:0.06 ⏱️ 0:02:49.555781
- 🔗 alfagok.diginaut.net 🧩 #726 🥳 36 ⏱️ 0:00:39.799868
- 🔗 alphaguess.com 🧩 #1193 🥳 26 ⏱️ 0:00:38.771637
- 🔗 dontwordle.com 🧩 #1619 🥳 6 ⏱️ 0:01:04.926479
- 🔗 dictionary.com hurdle 🧩 #1762 🥳 18 ⏱️ 0:03:07.321932
- 🔗 Quordle Classic 🧩 #1739 🥳 score:19 ⏱️ 0:01:25.364734
- 🔗 Octordle Classic 🧩 #1739 🥳 score:60 ⏱️ 0:01:51.600833
- 🔗 Sedecordle Classic 🧩 #1719 🥳 score:45 ⏱️ 0:02:31.878786
- 🔗 squareword.org 🧩 #1732 🥳 8 ⏱️ 0:02:07.857351
- 🔗 cemantle.certitudes.org 🧩 #1669 🥳 214 ⏱️ 0:17:47.800734
- 🔗 cemantix.certitudes.org 🧩 #1702 🥳 219 ⏱️ 0:24:07.081241

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
























# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 2026-10-27 🤔 rarity:nan ⏱️ 0:01:43.563056

📜 1 sessions
🌌 🌌 🦄
🌌 🌌 🌌
🦄 🦄 🦄


# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #880 🌌 rarity:0.06 ⏱️ 0:02:49.555781

📜 2 sessions
🌌 🦄 🦄
🦄 🦄 🦄
🌌 🦄 🦄
Rarity: 0.06 🌌

# [spaceword.org](spaceword.org) 🧩 2026-10-28 🏁 score 2168 ranked 47.7% 143/300 ⏱️ 0:05:49.838499

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 143/300

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ D _ D _ E _ A G _   
      _ O _ E M E U T E _   
      _ W O F U L _ T E _   
      _ _ _ _ X _ _ _ Z _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #726 🥳 36 ⏱️ 0:00:39.799868

🤔 36 attempts
📜 1 sessions

    @        [     0] &-teken        
    @+99672  [ 99672] ex             q2  ? ␅
    @+99672  [ 99672] ex             q3  ? after
    @+111327 [111327] ge             q6  ? ␅
    @+111327 [111327] ge             q7  ? after
    @+113644 [113644] gedierte       q14 ? ␅
    @+113644 [113644] gedierte       q15 ? after
    @+114805 [114805] gegalmd        q16 ? ␅
    @+114805 [114805] gegalmd        q17 ? after
    @+114834 [114834] gegeeuwd       q28 ? ␅
    @+114834 [114834] gegeeuwd       q29 ? after
    @+114845 [114845] gegenereerd    q30 ? ␅
    @+114845 [114845] gegenereerd    q31 ? after
    @+114854 [114854] gegespte       q32 ? ␅
    @+114854 [114854] gegespte       q33 ? after
    @+114858 [114858] gegeven        q34 ? ␅
    @+114858 [114858] gegeven        q35 ? it
    @+114858 [114858] gegeven        done. it
    @+114862 [114862] gegevens       q26 ? ␅
    @+114862 [114862] gegevens       q27 ? before
    @+114950 [114950] gegidste       q24 ? ␅
    @+114950 [114950] gegidste       q25 ? before
    @+115095 [115095] gegrint        q20 ? ␅
    @+115095 [115095] gegrint        q21 ? vb
    @+115095 [115095] gegrint        q22 ? ␅
    @+115095 [115095] gegrint        q23 ? before
    @+115385 [115385] gehergroepeerd q18 ? ␅
    @+115385 [115385] gehergroepeerd q19 ? before
    @+115965 [115965] gek            q12 ? ␅
    @+115965 [115965] gek            q13 ? before
    @+120817 [120817] gepunt         q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1193 🥳 26 ⏱️ 0:00:38.771637

🤔 26 attempts
📜 1 sessions

    @        [     0] aa         
    @+1      [     1] aah        
    @+2      [     2] aahed      
    @+3      [     3] aahing     
    @+98140  [ 98140] mac        q0  ? ␅
    @+98140  [ 98140] mac        q1  ? after
    @+147302 [147302] rho        q2  ? ␅
    @+147302 [147302] rho        q3  ? after
    @+153302 [153302] sea        q8  ? ␅
    @+153302 [153302] sea        q9  ? after
    @+156439 [156439] shit       q10 ? ␅
    @+156439 [156439] shit       q11 ? after
    @+157192 [157192] shut       q14 ? ␅
    @+157192 [157192] shut       q15 ? after
    @+157589 [157589] signal     q16 ? ␅
    @+157589 [157589] signal     q17 ? after
    @+157616 [157616] signature  q24 ? ␅
    @+157616 [157616] signature  q25 ? it
    @+157616 [157616] signature  done. it
    @+157642 [157642] signifiers q22 ? ␅
    @+157642 [157642] signifiers q23 ? before
    @+157695 [157695] silent     q20 ? ␅
    @+157695 [157695] silent     q21 ? before
    @+157799 [157799] silt       q18 ? ␅
    @+157799 [157799] silt       q19 ? before
    @+158008 [158008] sine       q12 ? ␅
    @+158008 [158008] sine       q13 ? before
    @+159584 [159584] slug       q6  ? ␅
    @+159584 [159584] slug       q7  ? before
    @+171902 [171902] tag        q4  ? ␅
    @+171902 [171902] tag        q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1619 🥳 6 ⏱️ 0:01:04.926479

📜 1 sessions
💰 score: 15

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:FEEZE n n n n n remain:6482
    ⬜⬜⬜⬜⬜ tried:BABKA n n n n n remain:2366
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:1106
    ⬜⬜⬜⬜⬜ tried:MUMMY n n n n n remain:353
    ⬜⬜⬜⬜⬜ tried:CRWTH n n n n n remain:51
    🟨🟨⬜⬜🟨 tried:PONGO m m n n m remain:3

    Undos used: 3

      3 words remaining
    x 5 unused letters
    = 15 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1762 🥳 18 ⏱️ 0:03:07.321932

📜 1 sessions
💰 score: 9800

    4/6
    LASER 🟨🟨⬜⬜⬜
    CLOAK ⬜🟩⬜🟨⬜
    PLAIN ⬜🟩🟨🟨⬜
    ALIBI 🟩🟩🟩🟩🟩
    4/6
    ALIBI 🟨⬜⬜⬜⬜
    CARES 🟩🟩🟨🟩⬜
    GIPON ⬜⬜🟩⬜⬜
    CAPER 🟩🟩🟩🟩🟩
    5/6
    CAPER ⬜⬜⬜🟨⬜
    STENO ⬜⬜🟨⬜⬜
    GUIDE 🟨🟩⬜⬜🟩
    FLUBS ⬜🟨🟨🟨⬜
    BULGE 🟩🟩🟩🟩🟩
    4/6
    BULGE ⬜⬜⬜⬜🟨
    DEARS ⬜🟨⬜🟩🟨
    SPERM 🟩⬜🟩🟩⬜
    STERN 🟩🟩🟩🟩🟩
    Final 1/2
    MAGIC 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1739 🥳 score:19 ⏱️ 0:01:25.364734

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. PRUDE attempts:3 score:3
2. MINUS attempts:4 score:4
3. SAVOY attempts:7 score:7
4. USHER attempts:5 score:5

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1739 🥳 score:60 ⏱️ 0:01:51.600833

📜 1 sessions

Octordle Classic

1. SWUNG attempts:9 score:9
2. SHRUB attempts:11 score:11
3. MERIT attempts:6 score:6
4. ONSET attempts:5 score:5
5. INFER attempts:4 score:4
6. WHEEL attempts:7 score:7
7. WOMEN attempts:8 score:8
8. WHOSE attempts:10 score:10

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1719 🥳 score:45 ⏱️ 0:02:31.878786

📜 1 sessions

Sedecordle Classic sedecordle.com

1. CURIO attempts:16 score:1
2. TOXIC attempts:13 score:6
3. CRAWL attempts:18 score:1
4. CORAL attempts:15 score:9
5. BLURB attempts:3 score:0
6. SHONE attempts:14 score:3
7. DREAD attempts:18 score:1
8. ROUGE attempts:6 score:8
9. BALMY attempts:10 score:1
10. MARRY attempts:12 score:0
11. SPURN attempts:4 score:0
12. TOXIN attempts:8 score:4
13. TRAMP attempts:9 score:0
14. TRAWL attempts:5 score:9
15. RAYON attempts:11 score:1
16. JOINT attempts:7 score:1

# [squareword.org](squareword.org) 🧩 #1732 🥳 8 ⏱️ 0:02:07.857351

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩 🟨 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C R A P
    A L O H A
    L O D E S
    S W E A T
    A N O D E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1669 🥳 214 ⏱️ 0:17:47.800734

🤔 215 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 55 chat prompts
🤖 9 dolphin3:latest replies
🤖 45 gemma4:12b replies
😱   1 🔥   3 🥵  21 😎  42 🥶 136 🧊  11

      $1 #215 passenger       100.00°C 🥳 1000‰ ~204 used:0  [203]  source:dolphin3
      $2  #88 cargo            52.07°C 😱  999‰   ~2 used:70 [1]    source:gemma4  
      $3  #94 vehicle          51.15°C 🔥  998‰  ~22 used:30 [21]   source:gemma4  
      $4 #208 airport          47.70°C 🔥  994‰   ~1 used:2  [0]    source:dolphin3
      $5 #150 airplane         46.00°C 🔥  990‰  ~15 used:14 [14]   source:gemma4  
      $6  #98 freight          44.33°C 🥵  985‰  ~23 used:4  [22]   source:gemma4  
      $7 #103 truck            42.46°C 🥵  981‰  ~16 used:2  [15]   source:gemma4  
      $8 #133 plane            41.77°C 🥵  979‰  ~17 used:2  [16]   source:gemma4  
      $9  #25 cabin            41.42°C 🥵  978‰  ~67 used:11 [66]   source:gemma4  
     $10 #140 aircraft         40.97°C 🥵  976‰  ~18 used:2  [17]   source:gemma4  
     $11 #172 flight           39.37°C 🥵  967‰  ~19 used:2  [18]   source:gemma4  
     $27  #91 container        33.35°C 😎  898‰  ~25 used:0  [24]   source:gemma4  
     $69 #124 dock             19.51°C 🥶        ~76 used:0  [75]   source:gemma4  
    $205   #7 syntax           -0.18°C 🧊       ~205 used:0  [204]  source:gemma4  

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1702 🥳 219 ⏱️ 0:24:07.081241

🤔 220 attempts
📜 1 sessions
🫧 14 chat sessions
⁉️ 71 chat prompts
🤖 14 dolphin3:latest replies
🤖 56 gemma4:12b replies
🔥   5 🥵  11 😎  45 🥶 139 🧊  19

      $1 #220 patrie           100.00°C 🥳 1000‰ ~201 used:0  [200]  source:dolphin3
      $2 #142 patriotisme       61.63°C 😱  999‰   ~1 used:38 [0]    source:gemma4  
      $3 #159 nation            61.17°C 🔥  998‰   ~8 used:16 [7]    source:gemma4  
      $4 #185 peuple            59.66°C 🔥  997‰   ~3 used:6  [2]    source:dolphin3
      $5 #191 patriote          55.96°C 🔥  996‰   ~2 used:5  [1]    source:dolphin3
      $6  #39 gloire            50.66°C 🔥  994‰  ~11 used:72 [10]   source:gemma4  
      $7 #124 héroïsme          45.18°C 🥵  985‰  ~12 used:9  [11]   source:gemma4  
      $8 #148 fraternité        44.81°C 🥵  983‰   ~9 used:2  [8]    source:gemma4  
      $9 #128 sacrifice         44.63°C 🥵  981‰  ~10 used:7  [9]    source:gemma4  
     $10  #35 fierté            44.03°C 🥵  976‰  ~60 used:25 [59]   source:gemma4  
     $11 #198 nationalisme      42.94°C 🥵  972‰   ~4 used:0  [3]    source:dolphin3
     $18 #168 liberté           38.11°C 😎  899‰  ~13 used:0  [12]   source:gemma4  
     $63 #112 ardeur            27.74°C 🥶        ~62 used:0  [61]   source:gemma4  
    $202 #206 intégration       -0.27°C 🧊       ~202 used:0  [201]  source:dolphin3
