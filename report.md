# 2026-01-10

- 🔗 spaceword.org 🧩 2026-01-09 🏁 score 2168 ranked 47.1% 152/323 ⏱️ 0:08:41.061172
- 🔗 alfagok.diginaut.net 🧩 #434 🥳 19 ⏱️ 0:00:43.310936
- 🔗 alphaguess.com 🧩 #900 🥳 10 ⏱️ 0:00:28.855424
- 🔗 dontwordle.com 🧩 #1327 🥳 6 ⏱️ 0:01:47.239395
- 🔗 dictionary.com hurdle 🧩 #1470 🥳 21 ⏱️ 0:04:10.687599
- 🔗 Quordle Classic 🧩 #1447 🥳 score:27 ⏱️ 0:01:43.623355
- 🔗 Octordle Classic 🧩 #1447 🥳 score:52 ⏱️ 0:02:48.152028
- 🔗 squareword.org 🧩 #1440 🥳 7 ⏱️ 0:01:50.686301
- 🔗 cemantle.certitudes.org 🧩 #1377 🥳 28 ⏱️ 0:00:58.951344
- 🔗 cemantix.certitudes.org 🧩 #1410 🥳 189 ⏱️ 0:12:49.253705
- 🔗 Quordle Rescue 🧩 #61 🥳 score:22 ⏱️ 0:01:45.214253
- 🔗 Quordle Sequence 🧩 #1447 🥳 score:22 ⏱️ 0:01:33.812764
- 🔗 Quordle Extreme 🧩 #530 😦 score:23 ⏱️ 0:01:44.231512
- 🔗 Octordle Rescue 🧩 #1447 🥳 score:8 ⏱️ 0:03:39.249929
- 🔗 Octordle Sequence 🧩 #1447 🥳 score:60 ⏱️ 0:02:50.276541
- 🔗 Octordle Extreme 🧩 #1447 🥳 score:67 ⏱️ 0:04:10.113253

# Dev

## WIP

- hurdle: add novel words to wordlist

- meta:
  - rework SolverHarness => Solver{ Library, Scope }
  - variants: regression on 01-06 running quordle

- ui:
  - Handle -- stabilizing core over Listing
  - Shell -- minimizing over Handle
- meta: rework command model over Shell

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
















# spaceword.org 🧩 2026-01-09 🏁 score 2168 ranked 47.1% 152/323 ⏱️ 0:08:41.061172

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 152/323

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ U G H _ _ O A R _   
      _ _ O _ P A R V O _   
      _ L O X E D _ A D _   
      _ _ _ _ W _ _ _ E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #434 🥳 19 ⏱️ 0:00:43.310936

🤔 19 attempts
📜 1 sessions

    @        [     0] &-teken        
    @+1      [     1] &-tekens       
    @+2      [     2] -cijferig      
    @+3      [     3] -e-mail        
    @+199833 [199833] lijm           q0  ? after
    @+299739 [299739] schub          q1  ? after
    @+324315 [324315] sub            q3  ? after
    @+330500 [330500] televisie      q5  ? after
    @+333705 [333705] these          q6  ? after
    @+334118 [334118] ti             q7  ? after
    @+335516 [335516] tjingel        q9  ? after
    @+335810 [335810] toegang        q11 ? after
    @+335986 [335986] toegeschroefde q12 ? after
    @+336007 [336007] toegestemd     q15 ? after
    @+336017 [336017] toegestuurde   q16 ? after
    @+336022 [336022] toegetelde     q17 ? after
    @+336026 [336026] toegeven       q18 ? it
    @+336026 [336026] toegeven       done. it
    @+336027 [336027] toegevend      q14 ? before
    @+336074 [336074] toegrijnsde    q13 ? before
    @+336162 [336162] toekomst       q10 ? before
    @+336916 [336916] toetsing       q4  ? before
    @+349523 [349523] vakantie       q2  ? before

# alphaguess.com 🧩 #900 🥳 10 ⏱️ 0:00:28.855424

🤔 10 attempts
📜 1 sessions

    @        [     0] aa      
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98220  [ 98220] mach    q0  ? after
    @+122783 [122783] parr    q2  ? after
    @+128852 [128852] play    q4  ? after
    @+130066 [130066] poly    q6  ? after
    @+130487 [130487] pond    q8  ? after
    @+130701 [130701] popular q9  ? it
    @+130701 [130701] popular done. it
    @+130934 [130934] pos     q7  ? before
    @+131962 [131962] prearm  q5  ? before
    @+135074 [135074] proper  q3  ? before
    @+147373 [147373] rhotic  q1  ? before

# dontwordle.com 🧩 #1327 🥳 6 ⏱️ 0:01:47.239395

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MADAM n n n n n remain:5246
    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:2539
    ⬜⬜⬜⬜⬜ tried:TUTTY n n n n n remain:903
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:259
    ⬜⬜🟨⬜⬜ tried:WHOOF n n m n n remain:37
    ⬜🟩⬜⬜🟨 tried:CONNS n Y n n m remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1470 🥳 21 ⏱️ 0:04:10.687599

📜 1 sessions
💰 score: 9500

    5/6
    RITES 🟨⬜⬜⬜⬜
    LOURY ⬜🟨⬜🟨⬜
    APRON ⬜⬜🟨🟩⬜
    BROOK ⬜🟩🟩🟩⬜
    GROOM 🟩🟩🟩🟩🟩
    4/6
    GROOM ⬜⬜⬜⬜⬜
    TAILS ⬜⬜🟩⬜🟨
    KNISH ⬜⬜🟩🟩🟩
    SWISH 🟩🟩🟩🟩🟩
    6/6
    SWISH ⬜⬜⬜⬜⬜
    HARES ⬜🟩⬜⬜⬜
    BATON ⬜🟩⬜⬜⬜
    CAMPY ⬜🟩⬜⬜🟩
    GAUDY ⬜🟩⬜⬜🟩
    JAZZY 🟩🟩🟩🟩🟩
    4/6
    JAZZY ⬜🟨⬜⬜🟩
    SCARY ⬜⬜🟨⬜🟩
    TODAY ⬜⬜⬜🟨🟩
    AMPLY 🟩🟩🟩🟩🟩
    Final 2/2
    MOUNT 🟩🟩⬜⬜🟨
    MOTTO 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1447 🥳 score:27 ⏱️ 0:01:43.623355

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. HALVE attempts:6 score:6
2. FLUFF attempts:8 score:8
3. BELOW attempts:4 score:4
4. DINER attempts:9 score:9

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1447 🥳 score:52 ⏱️ 0:02:48.152028

📜 1 sessions

Octordle Classic

1. BIOME attempts:8 score:8
2. CATCH attempts:6 score:6
3. LIMBO attempts:7 score:7
4. GUSTO attempts:3 score:3
5. CLOUT attempts:5 score:5
6. FLEET attempts:4 score:4
7. SPIKE attempts:10 score:10
8. EXILE attempts:9 score:9

# squareword.org 🧩 #1440 🥳 7 ⏱️ 0:01:50.686301

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟨 🟩 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B L A S T
    R A D A R
    A T O N E
    S C R E E
    S H E R D

# cemantle.certitudes.org 🧩 #1377 🥳 28 ⏱️ 0:00:58.951344

🤔 29 attempts
📜 2 sessions
🫧 1 chat sessions
⁉️ 7 chat prompts
🤖 7 dolphin3:latest replies
🥵  1 😎  3 🥶 20 🧊  4

     $1 #29  ~1 renewable     100.00°C 🥳 1000‰
     $2 #24  ~2 conservation   39.22°C 🥵  959‰
     $3 #13  ~5 agriculture    32.09°C 😎  887‰
     $4 #20  ~3 fertilizer     25.68°C 😎  654‰
     $5 #16  ~4 irrigation     22.08°C 😎  221‰
     $6 #15     farming        20.30°C 🥶
     $7 #14     cultivation    19.64°C 🥶
     $8 #12     farm           17.98°C 🥶
     $9 #21     harvesting     17.89°C 🥶
    $10 #22     livestock      17.19°C 🥶
    $11 #26     development    17.11°C 🥶
    $12 #18     soil           16.25°C 🥶
    $13  #3     carrot         15.75°C 🥶
    $26  #4     elevator       -0.60°C 🧊

# cemantix.certitudes.org 🧩 #1410 🥳 189 ⏱️ 0:12:49.253705

🤔 190 attempts
📜 2 sessions
🫧 8 chat sessions
⁉️ 58 chat prompts
🤖 58 dolphin3:latest replies
😱  1 🥵  6 😎 36 🥶 90 🧊 56

      $1 #190   ~1 performance      100.00°C 🥳 1000‰
      $2 #184   ~4 fiabilité         58.77°C 😱  999‰
      $3 #102  ~35 flexibilité       39.88°C 🥵  959‰
      $4 #136  ~24 stratégie         38.93°C 🥵  956‰
      $5 #167   ~7 souplesse         38.49°C 🥵  942‰
      $6 #124  ~28 innovation        37.54°C 🥵  929‰
      $7 #128  ~27 intégrer          36.84°C 🥵  918‰
      $8 #122  ~29 management        36.06°C 🥵  901‰
      $9 #146  ~17 évolution         35.22°C 😎  886‰
     $10  #85  ~42 analyse           35.01°C 😎  881‰
     $11 #100  ~37 adaptabilité      34.07°C 😎  857‰
     $12 #113  ~31 gestion           33.66°C 😎  847‰
     $45 #126      agile             23.30°C 🥶
    $135 #109      approcher         -0.27°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #61 🥳 score:22 ⏱️ 0:01:45.214253

📜 3 sessions

Quordle Rescue m-w.com/games/quordle/

1. ENEMY attempts:5 score:5
2. FINCH attempts:7 score:7
3. BUYER attempts:6 score:6
4. GRAIN attempts:4 score:4

# [Quordle Sequence](m-w.com/games/quordle/#/sequence) 🧩 #1447 🥳 score:22 ⏱️ 0:01:33.812764

📜 2 sessions

Quordle Sequence m-w.com/games/quordle/

1. PREEN attempts:4 score:4
2. MEDAL attempts:5 score:5
3. IMPLY attempts:6 score:6
4. REPEL attempts:7 score:7

# [Quordle Extreme](m-w.com/games/quordle/#/extreme) 🧩 #530 😦 score:23 ⏱️ 0:01:44.231512

📜 1 sessions

Quordle Extreme m-w.com/games/quordle/

1. SINGE attempts:7 score:7
2. CA__E ~R -FGHILMNOPSTUVY attempts:8 score:-1
3. MOULT attempts:5 score:5
4. SHIFT attempts:3 score:3

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1447 🥳 score:8 ⏱️ 0:03:39.249929

📜 1 sessions

Octordle Rescue

1. CROWN attempts:10 score:10
2. PLUME attempts:5 score:5
3. VOMIT attempts:6 score:6
4. ACUTE attempts:7 score:7
5. FOAMY attempts:12 score:12
6. BELIE attempts:8 score:8
7. PRUDE attempts:9 score:9
8. TANGY attempts:13 score:13

# [Octordle Sequence](britannica.com/games/octordle/daily-sequence) 🧩 #1447 🥳 score:60 ⏱️ 0:02:50.276541

📜 1 sessions

Octordle Sequence

1. COLON attempts:4 score:4
2. ELDER attempts:5 score:5
3. BRUSH attempts:6 score:6
4. STEEL attempts:7 score:7
5. DICEY attempts:8 score:8
6. GEEKY attempts:9 score:9
7. AUGUR attempts:10 score:10
8. TERSE attempts:11 score:11

# [Octordle Extreme](britannica.com/games/octordle/extreme) 🧩 #1447 🥳 score:67 ⏱️ 0:04:10.113253

📜 1 sessions

Octordle Extreme

1. HOLLY attempts:12 score:12
2. MURAL attempts:9 score:9
3. ECLAT attempts:4 score:4
4. BOSON attempts:10 score:10
5. IMBUE attempts:8 score:8
6. CACTI attempts:6 score:6
7. INERT attempts:7 score:7
8. CHECK attempts:11 score:11
