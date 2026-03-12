# 2026-03-13

- 🔗 spaceword.org 🧩 2026-03-12 🏁 score 2168 ranked 47.1% 162/344 ⏱️ 1:26:22.004130
- 🔗 alfagok.diginaut.net 🧩 #496 🥳 18 ⏱️ 0:00:40.286944
- 🔗 alphaguess.com 🧩 #963 🥳 26 ⏱️ 0:00:34.567191
- 🔗 dontwordle.com 🧩 #1389 🥳 6 ⏱️ 0:01:54.493102
- 🔗 dictionary.com hurdle 🧩 #1532 🥳 19 ⏱️ 0:03:22.080756
- 🔗 Quordle Classic 🧩 #1509 🥳 score:22 ⏱️ 0:01:41.040729
- 🔗 Octordle Classic 🧩 #1509 🥳 score:60 ⏱️ 0:03:12.328987
- 🔗 squareword.org 🧩 #1502 🥳 7 ⏱️ 0:01:56.680443
- 🔗 cemantle.certitudes.org 🧩 #1439 🥳 393 ⏱️ 0:32:29.737601
- 🔗 cemantix.certitudes.org 🧩 #1472 🥳 332 ⏱️ 1:04:38.275348

# Dev

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












# [spaceword.org](spaceword.org) 🧩 2026-03-12 🏁 score 2168 ranked 47.1% 162/344 ⏱️ 1:26:22.004130

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 162/344

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ E _ _ _ N _ _ E _   
      _ C _ Q U A E R E _   
      _ O _ _ _ Z _ A L _   
      _ S H A K I L Y _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #496 🥳 18 ⏱️ 0:00:40.286944

🤔 18 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+99737  [ 99737] ex        q4  ? ␅
    @+99737  [ 99737] ex        q5  ? after
    @+124636 [124636] gevoel    q8  ? ␅
    @+124636 [124636] gevoel    q9  ? after
    @+137126 [137126] handt     q10 ? ␅
    @+137126 [137126] handt     q11 ? after
    @+137576 [137576] hard      q16 ? ␅
    @+137576 [137576] hard      q17 ? it
    @+137576 [137576] hard      done. it
    @+138064 [138064] harp      q14 ? ␅
    @+138064 [138064] harp      q15 ? before
    @+139080 [139080] he        q12 ? ␅
    @+139080 [139080] he        q13 ? before
    @+149642 [149642] huishoud  q6  ? ␅
    @+149642 [149642] huishoud  q7  ? before
    @+199609 [199609] lij       q0  ? ␅
    @+199609 [199609] lij       q1  ? after
    @+199609 [199609] lij       q2  ? ␅
    @+199609 [199609] lij       q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #963 🥳 26 ⏱️ 0:00:34.567191

🤔 26 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+47381 [47381] dis       q2  ? ␅
    @+47381 [47381] dis       q3  ? after
    @+72800 [72800] gremmy    q4  ? ␅
    @+72800 [72800] gremmy    q5  ? after
    @+85504 [85504] ins       q6  ? ␅
    @+85504 [85504] ins       q7  ? after
    @+87077 [87077] intima    q12 ? ␅
    @+87077 [87077] intima    q13 ? after
    @+87868 [87868] iris      q14 ? ␅
    @+87868 [87868] iris      q15 ? after
    @+88124 [88124] is        q16 ? ␅
    @+88124 [88124] is        q17 ? after
    @+88159 [88159] island    q24 ? ␅
    @+88159 [88159] island    q25 ? it
    @+88159 [88159] island    done. it
    @+88191 [88191] isobath   q22 ? ␅
    @+88191 [88191] isobath   q23 ? before
    @+88259 [88259] isogenies q20 ? ␅
    @+88259 [88259] isogenies q21 ? before
    @+88394 [88394] isotactic q18 ? ␅
    @+88394 [88394] isotactic q19 ? before
    @+88664 [88664] jacks     q10 ? ␅
    @+88664 [88664] jacks     q11 ? before
    @+91848 [91848] knot      q8  ? ␅
    @+91848 [91848] knot      q9  ? before
    @+98218 [98218] mach      q0  ? ␅
    @+98218 [98218] mach      q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1389 🥳 6 ⏱️ 0:01:54.493102

📜 2 sessions
💰 score: 36

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:ZIZIT n n n n n remain:6979
    ⬜⬜⬜⬜⬜ tried:CAVAS n n n n n remain:1368
    ⬜⬜⬜⬜⬜ tried:MUMMY n n n n n remain:466
    ⬜⬜⬜⬜🟨 tried:GRRRL n n n n m remain:68
    ⬜🟩🟩⬜⬜ tried:DELED n Y Y n n remain:6
    ⬜🟩🟩⬜🟨 tried:HELLO n Y Y n m remain:4

    Undos used: 3

      4 words remaining
    x 9 unused letters
    = 36 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1532 🥳 19 ⏱️ 0:03:22.080756

📜 1 sessions
💰 score: 9700

    4/6
    ANTES 🟨⬜⬜🟨⬜
    RELAY ⬜🟩⬜🟨⬜
    BEACH ⬜🟩🟩🟩🟩
    PEACH 🟩🟩🟩🟩🟩
    3/6
    PEACH ⬜🟨🟨⬜⬜
    ASTER 🟨⬜🟨🟩🟩
    TAKER 🟩🟩🟩🟩🟩
    4/6
    TAKER 🟨⬜⬜⬜⬜
    UNLIT ⬜🟨🟨🟨🟩
    FLINT ⬜🟩🟩🟩🟩
    GLINT 🟩🟩🟩🟩🟩
    6/6
    GLINT ⬜⬜⬜🟨⬜
    NARES 🟨⬜⬜⬜⬜
    DUNCH ⬜🟩🟩🟩🟩
    BUNCH ⬜🟩🟩🟩🟩
    MUNCH ⬜🟩🟩🟩🟩
    PUNCH 🟩🟩🟩🟩🟩
    Final 2/2
    BRAIN ⬜🟩🟩🟩🟩
    DRAIN 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1509 🥳 score:22 ⏱️ 0:01:41.040729

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SCARY attempts:7 score:7
2. MOURN attempts:4 score:4
3. WHARF attempts:6 score:6
4. SHARP attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1509 🥳 score:60 ⏱️ 0:03:12.328987

📜 1 sessions

Octordle Classic

1. HOWDY attempts:10 score:10
2. HOUND attempts:10 score:11
3. ATONE attempts:8 score:8
4. SHAKE attempts:9 score:9
5. VIRUS attempts:7 score:7
6. RABID attempts:6 score:6
7. SWORD attempts:5 score:5
8. TIDAL attempts:4 score:4

# [squareword.org](squareword.org) 🧩 #1502 🥳 7 ⏱️ 0:01:56.680443

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A W A S H
    B A L T I
    O N I O N
    D E B U T
    E D I T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1439 🥳 393 ⏱️ 0:32:29.737601

🤔 394 attempts
📜 1 sessions
🫧 56 chat sessions
⁉️ 133 chat prompts
🤖 8 gemma3:27b replies
🤖 28 lfm2.5-thinking:latest replies
🤖 27 qwen3:14b replies
🤖 12 hermes3:8b replies
🤖 20 falcon3:10b replies
🤖 38 dolphin3:latest replies
🔥   1 😎   5 🥶 291 🧊  96

      $1 #394 exclusion        100.00°C 🥳 1000‰ ~298 used:0   [297]  source:gemma3  
      $2 #390 preclusion        40.62°C 🔥  992‰   ~1 used:1   [0]    source:gemma3  
      $3 #393 barring           31.88°C 😎  854‰   ~2 used:0   [1]    source:gemma3  
      $4 #385 recourse          29.45°C 😎  745‰   ~3 used:0   [2]    source:gemma3  
      $5 #377 indemnity         24.87°C 😎   66‰   ~4 used:1   [3]    source:gemma3  
      $6 #381 compensation      24.81°C 😎   44‰   ~5 used:0   [4]    source:gemma3  
      $7  #11 protection        24.62°C 😎    7‰   ~6 used:118 [5]    source:dolphin3
      $8  #50 shielding         24.36°C 🥶         ~7 used:56  [6]    source:dolphin3
      $9 #378 alleviation       23.55°C 🥶        ~17 used:0   [16]   source:gemma3  
     $10 #384 mitigation        23.50°C 🥶        ~18 used:0   [17]   source:gemma3  
     $11  #64 protected         22.86°C 🥶         ~9 used:32  [8]    source:dolphin3
     $12  #23 shielded          22.56°C 🥶         ~8 used:36  [7]    source:dolphin3
     $13 #382 coverage          21.22°C 🥶        ~19 used:0   [18]   source:gemma3  
    $299  #82 boat              -0.03°C 🧊       ~299 used:0   [298]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1472 🥳 332 ⏱️ 1:04:38.275348

🤔 333 attempts
📜 1 sessions
🫧 20 chat sessions
⁉️ 113 chat prompts
🤖 25 gemma3:27b replies
🤖 88 dolphin3:latest replies
😱   1 🔥   1 🥵  16 😎  98 🥶 200 🧊  16

      $1 #333 touchant         100.00°C 🥳 1000‰ ~317 used:0   [316]  source:gemma3  
      $2 #307 émouvant          73.20°C 😱  999‰   ~1 used:4   [0]    source:gemma3  
      $3 #103 tendresse         57.26°C 🔥  994‰ ~107 used:112 [106]  source:dolphin3
      $4 #218 drôlerie          54.53°C 🥵  989‰ ~108 used:16  [107]  source:gemma3  
      $5 #130 émotion           50.49°C 🥵  986‰ ~114 used:48  [113]  source:dolphin3
      $6  #60 drôle             49.22°C 🥵  984‰ ~113 used:26  [112]  source:dolphin3
      $7 #193 humour            48.48°C 🥵  983‰ ~106 used:11  [105]  source:dolphin3
      $8 #121 amour             46.83°C 🥵  974‰   ~6 used:10  [5]    source:dolphin3
      $9 #185 délicatesse       45.81°C 🥵  969‰   ~7 used:10  [6]    source:dolphin3
     $10 #166 sentimentalité    44.51°C 🥵  957‰   ~8 used:10  [7]    source:dolphin3
     $11 #261 pathos            44.14°C 🥵  954‰   ~3 used:5   [2]    source:gemma3  
     $20 #270 espièglerie       40.02°C 😎  892‰  ~13 used:0   [12]   source:gemma3  
    $118 #279 réconfort         27.19°C 🥶       ~117 used:0   [116]  source:gemma3  
    $318 #260 imprégnation      -0.20°C 🧊       ~318 used:0   [317]  source:gemma3  
