# 2026-03-05

- 🔗 spaceword.org 🧩 2026-03-04 🏁 score 2173 ranked 15.3% 54/352 ⏱️ 0:52:05.528213
- 🔗 alfagok.diginaut.net 🧩 #488 🥳 52 ⏱️ 0:01:00.399233
- 🔗 alphaguess.com 🧩 #955 🥳 28 ⏱️ 0:00:25.407284
- 🔗 dontwordle.com 🧩 #1381 🥳 6 ⏱️ 0:01:28.462236
- 🔗 dictionary.com hurdle 🧩 #1524 🥳 17 ⏱️ 0:02:46.600786
- 🔗 Quordle Classic 🧩 #1501 🥳 score:24 ⏱️ 0:01:26.272711
- 🔗 Octordle Classic 🧩 #1501 🥳 score:68 ⏱️ 0:03:35.681309
- 🔗 squareword.org 🧩 #1494 🥳 8 ⏱️ 0:01:47.167473
- 🔗 cemantle.certitudes.org 🧩 #1431 🥳 169 ⏱️ 0:03:01.747941
- 🔗 cemantix.certitudes.org 🧩 #1464 🥳 539 ⏱️ 0:16:38.351795

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




# [spaceword.org](spaceword.org) 🧩 2026-03-04 🏁 score 2173 ranked 15.3% 54/352 ⏱️ 0:52:05.528213

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 54/352

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ Z E E _ _ _   
      _ _ _ _ _ _ L _ _ _   
      _ _ _ _ J _ O _ _ _   
      _ _ _ _ O _ I _ _ _   
      _ _ _ _ B A G _ _ _   
      _ _ _ _ N _ N _ _ _   
      _ _ _ _ A D S _ _ _   
      _ _ _ _ M A _ _ _ _   
      _ _ _ _ E K E _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #488 🥳 52 ⏱️ 0:01:00.399233

🤔 52 attempts
📜 1 sessions

    @        [     0] &-teken       
    @+199812 [199812] lijm          q0  ? ␅
    @+199812 [199812] lijm          q1  ? after
    @+223584 [223584] mol           q6  ? ␅
    @+223584 [223584] mol           q7  ? after
    @+229602 [229602] natuur        q10 ? ␅
    @+229602 [229602] natuur        q11 ? after
    @+230946 [230946] neg           q14 ? ␅
    @+230946 [230946] neg           q15 ? after
    @+231124 [231124] neig          q20 ? ␅
    @+231124 [231124] neig          q21 ? after
    @+231145 [231145] nek           q24 ? ␅
    @+231145 [231145] nek           q25 ? after
    @+231183 [231183] nel           q26 ? ␅
    @+231183 [231183] nel           q27 ? after
    @+231203 [231203] nelson        q40 ? ␅
    @+231203 [231203] nelson        q41 ? after
    @+231208 [231208] neme          q42 ? ␅
    @+231208 [231208] neme          q43 ? after
    @+231209 [231209] nemen         q50 ? ␅
    @+231209 [231209] nemen         q51 ? it
    @+231209 [231209] nemen         done. it
    @+231210 [231210] nemend        q48 ? ␅
    @+231210 [231210] nemend        q49 ? before
    @+231211 [231211] nemende       q46 ? ␅
    @+231211 [231211] nemende       q47 ? before
    @+231213 [231213] nemers        q44 ? ␅
    @+231213 [231213] nemers        q45 ? before
    @+231217 [231217] neobarok      q22 ? ␅
    @+231217 [231217] neobarok      q23 ? before
    @+231315 [231315] neoromantisch q19 ? before

# [alphaguess.com](alphaguess.com) 🧩 #955 🥳 28 ⏱️ 0:00:25.407284

🤔 28 attempts
📜 1 sessions

    @        [     0] aa             
    @+2      [     2] aahed          
    @+98218  [ 98218] mach           q0  ? ␅
    @+98218  [ 98218] mach           q1  ? after
    @+147369 [147369] rhotic         q2  ? ␅
    @+147369 [147369] rhotic         q3  ? after
    @+159486 [159486] slop           q6  ? ␅
    @+159486 [159486] slop           q7  ? after
    @+162473 [162473] spec           q10 ? ␅
    @+162473 [162473] spec           q11 ? after
    @+163209 [163209] spit           q14 ? ␅
    @+163209 [163209] spit           q15 ? after
    @+163305 [163305] splendid       q20 ? ␅
    @+163305 [163305] splendid       q21 ? after
    @+163353 [163353] splint         q22 ? ␅
    @+163353 [163353] splint         q23 ? after
    @+163364 [163364] split          q26 ? ␅
    @+163364 [163364] split          q27 ? it
    @+163364 [163364] split          done. it
    @+163380 [163380] splosh         q24 ? ␅
    @+163380 [163380] splosh         q25 ? before
    @+163404 [163404] splutter       q18 ? ␅
    @+163404 [163404] splutter       q19 ? before
    @+163604 [163604] sporopollenins q16 ? ␅
    @+163604 [163604] sporopollenins q17 ? before
    @+163999 [163999] squab          q12 ? ␅
    @+163999 [163999] squab          q13 ? before
    @+165528 [165528] stick          q8  ? ␅
    @+165528 [165528] stick          q9  ? before
    @+171639 [171639] ta             q4  ? ␅
    @+171639 [171639] ta             q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1381 🥳 6 ⏱️ 0:01:28.462236

📜 2 sessions
💰 score: 60

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:7419
    ⬜⬜⬜⬜⬜ tried:VEXED n n n n n remain:2921
    ⬜⬜⬜⬜⬜ tried:BUZZY n n n n n remain:1271
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:498
    ⬜⬜⬜⬜🟨 tried:PHPHT n n n n m remain:87
    🟨⬜🟨⬜⬜ tried:TWINK m n m n n remain:12

    Undos used: 4

      12 words remaining
    x 5 unused letters
    = 60 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1524 🥳 17 ⏱️ 0:02:46.600786

📜 1 sessions
💰 score: 9900

    5/6
    SERAL ⬜🟨⬜⬜⬜
    NOTED 🟨⬜⬜🟨⬜
    GYNIE 🟨⬜🟩🟨🟩
    BINGE ⬜🟩🟩🟩🟩
    HINGE 🟩🟩🟩🟩🟩
    5/6
    HINGE ⬜🟨⬜⬜⬜
    ARILS ⬜🟩🟩⬜⬜
    PRICK 🟩🟩🟩⬜⬜
    PRIMO 🟩🟩🟩⬜🟨
    PRIOR 🟩🟩🟩🟩🟩
    3/6
    PRIOR ⬜🟨⬜🟨⬜
    ROUSE 🟨🟨⬜🟨🟩
    SCORE 🟩🟩🟩🟩🟩
    3/6
    SCORE ⬜⬜⬜🟩⬜
    DIARY ⬜🟨🟨🟩🟩
    FAIRY 🟩🟩🟩🟩🟩
    Final 1/2
    FICUS 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1501 🥳 score:24 ⏱️ 0:01:26.272711

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. AGATE attempts:4 score:4
2. GAUNT attempts:5 score:5
3. BRAIN attempts:7 score:7
4. LANCE attempts:8 score:8

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1501 🥳 score:68 ⏱️ 0:03:35.681309

📜 3 sessions

Octordle Classic

1. FROZE attempts:10 score:10
2. FLOUR attempts:9 score:9
3. PANIC attempts:8 score:8
4. SHEEP attempts:12 score:12
5. DUSTY attempts:4 score:4
6. CLAMP attempts:7 score:7
7. NOOSE attempts:13 score:13
8. PALER attempts:5 score:5

# [squareword.org](squareword.org) 🧩 #1494 🥳 8 ⏱️ 0:01:47.167473

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟨 🟩 🟩
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C A V E S
    A G A V E
    R I L E D
    A L O N G
    T E R S E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1431 🥳 169 ⏱️ 0:03:01.747941

🤔 170 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 48 chat prompts
🤖 48 dolphin3:latest replies
🔥   2 🥵   6 😎  21 🥶 135 🧊   5

      $1 #170 inherit       100.00°C 🥳 1000‰ ~165 used:0  [164]  source:dolphin3
      $2 #168 bequeath       61.42°C 🔥  997‰   ~1 used:0  [0]    source:dolphin3
      $3 #155 inheritance    48.73°C 🔥  996‰   ~2 used:2  [1]    source:dolphin3
      $4 #149 heir           39.04°C 🥵  984‰   ~5 used:5  [4]    source:dolphin3
      $5 #104 succeed        38.25°C 🥵  979‰  ~25 used:30 [24]   source:dolphin3
      $6 #147 successor      36.95°C 🥵  970‰   ~4 used:3  [3]    source:dolphin3
      $7 #169 hereditary     36.09°C 🥵  964‰   ~3 used:0  [2]    source:dolphin3
      $8 #112 ascend         33.78°C 🥵  944‰  ~17 used:17 [16]   source:dolphin3
      $9  #96 prosper        32.01°C 🥵  913‰  ~16 used:12 [15]   source:dolphin3
     $10 #131 outshine       30.72°C 😎  891‰  ~18 used:2  [17]   source:dolphin3
     $11 #139 fortune        30.19°C 😎  872‰  ~19 used:2  [18]   source:dolphin3
     $12  #76 grow           28.96°C 😎  827‰  ~28 used:6  [27]   source:dolphin3
     $31 #152 ancestry       21.46°C 🥶        ~37 used:0  [36]   source:dolphin3
    $166 #146 promotion      -0.75°C 🧊       ~166 used:0  [165]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1464 🥳 539 ⏱️ 0:16:38.351795

🤔 540 attempts
📜 1 sessions
🫧 38 chat sessions
⁉️ 188 chat prompts
🤖 188 dolphin3:latest replies
🔥   5 🥵  14 😎  58 🥶 407 🧊  55

      $1 #540 poitrine         100.00°C 🥳 1000‰ ~485 used:0  [484]  source:dolphin3
      $2 #453 épaule            58.02°C 🔥  997‰  ~14 used:36 [13]   source:dolphin3
      $3 #518 cou               56.89°C 🔥  996‰   ~1 used:9  [0]    source:dolphin3
      $4 #455 bras              56.13°C 🔥  995‰   ~8 used:17 [7]    source:dolphin3
      $5 #424 cuisse            55.47°C 🔥  993‰   ~7 used:12 [6]    source:dolphin3
      $6 #432 jambe             54.94°C 🔥  992‰   ~6 used:11 [5]    source:dolphin3
      $7 #488 omoplate          49.14°C 🥵  988‰   ~9 used:2  [8]    source:dolphin3
      $8 #443 hanche            48.20°C 🥵  983‰  ~10 used:2  [9]    source:dolphin3
      $9 #525 sternum           48.11°C 🥵  982‰  ~11 used:2  [10]   source:dolphin3
     $10 #431 genou             47.75°C 🥵  979‰  ~12 used:2  [11]   source:dolphin3
     $11 #475 fesse             47.44°C 🥵  977‰  ~13 used:2  [12]   source:dolphin3
     $21 #363 bouche            39.91°C 😎  882‰  ~51 used:2  [50]   source:dolphin3
     $79 #117 la                29.76°C 🥶        ~92 used:0  [91]   source:dolphin3
    $486 #183 aérien            -0.16°C 🧊       ~486 used:0  [485]  source:dolphin3
