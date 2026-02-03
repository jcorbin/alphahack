# 2026-02-04

- 🔗 spaceword.org 🧩 2026-02-03 🏁 score 2173 ranked 5.8% 20/347 ⏱️ 7:06:25.195140
- 🔗 alfagok.diginaut.net 🧩 #459 🥳 22 ⏱️ 0:00:44.679934
- 🔗 alphaguess.com 🧩 #926 🥳 30 ⏱️ 0:00:39.103647
- 🔗 dontwordle.com 🧩 #1352 🥳 6 ⏱️ 0:02:17.505150
- 🔗 dictionary.com hurdle 🧩 #1495 🥳 16 ⏱️ 0:02:59.337216
- 🔗 Quordle Classic 🧩 #1472 🥳 score:23 ⏱️ 0:01:26.983428
- 🔗 Octordle Classic 🧩 #1472 🥳 score:60 ⏱️ 0:03:56.178449
- 🔗 squareword.org 🧩 #1465 🥳 7 ⏱️ 0:01:31.832010
- 🔗 cemantle.certitudes.org 🧩 #1402 🥳 74 ⏱️ 0:04:35.438410
- 🔗 cemantix.certitudes.org 🧩 #1435 🥳 153 ⏱️ 0:03:31.489621
- 🔗 Quordle Rescue 🧩 #86 🥳 score:22 ⏱️ 0:01:42.521533
- 🔗 Octordle Rescue 🧩 #1472 😦 score:7 ⏱️ 0:04:06.505415

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




















# [spaceword.org](spaceword.org) 🧩 2026-02-03 🏁 score 2173 ranked 5.8% 20/347 ⏱️ 7:06:25.195140

📜 6 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 20/347

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ C _ S E Q U O I A   
      _ O L E _ _ _ V _ H   
      _ T _ Z I N G A R A   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #459 🥳 22 ⏱️ 0:00:44.679934

🤔 22 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+49849  [ 49849] boks      q4  ? ␅
    @+49849  [ 49849] boks      q5  ? after
    @+52691  [ 52691] bouw      q12 ? ␅
    @+52691  [ 52691] bouw      q13 ? after
    @+53209  [ 53209] boven     q16 ? ␅
    @+53209  [ 53209] boven     q17 ? after
    @+53716  [ 53716] braak     q18 ? ␅
    @+53716  [ 53716] braak     q19 ? after
    @+53984  [ 53984] brand     q20 ? ␅
    @+53984  [ 53984] brand     q21 ? it
    @+53984  [ 53984] brand     done. it
    @+54274  [ 54274] brandstof q14 ? ␅
    @+54274  [ 54274] brandstof q15 ? before
    @+55941  [ 55941] bron      q10 ? ␅
    @+55941  [ 55941] bron      q11 ? before
    @+62288  [ 62288] cement    q8  ? ␅
    @+62288  [ 62288] cement    q9  ? before
    @+74762  [ 74762] dc        q6  ? ␅
    @+74762  [ 74762] dc        q7  ? before
    @+99758  [ 99758] ex        q2  ? ␅
    @+99758  [ 99758] ex        q3  ? before
    @+199833 [199833] lijm      q0  ? ␅
    @+199833 [199833] lijm      q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #926 🥳 30 ⏱️ 0:00:39.103647

🤔 30 attempts
📜 1 sessions

    @        [     0] aa     
    @+98220  [ 98220] mach   q0  ? ␅
    @+98220  [ 98220] mach   q1  ? after
    @+98220  [ 98220] mach   q2  ? ␅
    @+98220  [ 98220] mach   q3  ? after
    @+98220  [ 98220] mach   q4  ? ␅
    @+98220  [ 98220] mach   q5  ? after
    @+147373 [147373] rhotic q6  ? ␅
    @+147373 [147373] rhotic q7  ? after
    @+171643 [171643] ta     q8  ? ␅
    @+171643 [171643] ta     q9  ? after
    @+182008 [182008] un     q10 ? ␅
    @+182008 [182008] un     q11 ? after
    @+189270 [189270] vicar  q12 ? ␅
    @+189270 [189270] vicar  q13 ? after
    @+191050 [191050] walk   q16 ? ␅
    @+191050 [191050] walk   q17 ? after
    @+191913 [191913] we     q18 ? ␅
    @+191913 [191913] we     q19 ? after
    @+192148 [192148] wee    q22 ? ␅
    @+192148 [192148] wee    q23 ? after
    @+192246 [192246] weight q24 ? ␅
    @+192246 [192246] weight q25 ? after
    @+192271 [192271] weird  q28 ? ␅
    @+192271 [192271] weird  q29 ? it
    @+192271 [192271] weird  done. it
    @+192307 [192307] weld   q26 ? ␅
    @+192307 [192307] weld   q27 ? before
    @+192383 [192383] wen    q20 ? ␅
    @+192383 [192383] wen    q21 ? before
    @+192874 [192874] whir   q15 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1352 🥳 6 ⏱️ 0:02:17.505150

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:JINNI n n n n n remain:7302
    ⬜⬜⬜⬜⬜ tried:DOOZY n n n n n remain:2979
    ⬜⬜⬜⬜⬜ tried:MUMUS n n n n n remain:700
    ⬜🟨⬜⬜⬜ tried:PHPHT n m n n n remain:41
    🟨🟩⬜⬜⬜ tried:HELVE m Y n n n remain:5
    ⬜🟩🟩🟩🟩 tried:BEACH n Y Y Y Y remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1495 🥳 16 ⏱️ 0:02:59.337216

📜 1 sessions
💰 score: 10000

    2/6
    NEARS ⬜🟩🟨🟩⬜
    ZEBRA 🟩🟩🟩🟩🟩
    4/6
    ZEBRA ⬜⬜⬜⬜⬜
    LOINS ⬜🟩🟨⬜⬜
    VOMIT ⬜🟩🟨🟩🟨
    MOTIF 🟩🟩🟩🟩🟩
    4/6
    MOTIF ⬜⬜⬜⬜⬜
    ASPER ⬜⬜⬜🟨⬜
    LUNGE 🟨⬜⬜🟩🟨
    ELEGY 🟩🟩🟩🟩🟩
    4/6
    ELEGY ⬜⬜⬜⬜⬜
    TOURS 🟨⬜🟩🟨⬜
    FRUIT ⬜🟩🟩⬜🟩
    BRUNT 🟩🟩🟩🟩🟩
    Final 2/2
    FAWNY 🟩🟩⬜🟩🟩
    FANNY 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1472 🥳 score:23 ⏱️ 0:01:26.983428

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. BLAND attempts:4 score:4
2. HUNKY attempts:5 score:5
3. PUNCH attempts:8 score:8
4. TESTY attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1472 🥳 score:60 ⏱️ 0:03:56.178449

📜 2 sessions

Octordle Classic

1. FORGO attempts:7 score:7
2. SLANT attempts:4 score:4
3. SHRUB attempts:8 score:8
4. MEALY attempts:11 score:11
5. BLURB attempts:5 score:5
6. DIRTY attempts:6 score:6
7. STILT attempts:10 score:10
8. PERKY attempts:9 score:9

# [squareword.org](squareword.org) 🧩 #1465 🥳 7 ⏱️ 0:01:31.832010

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P A L S Y
    E L O P E
    T I B I A
    E V E N S
    R E S E T

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1402 🥳 74 ⏱️ 0:04:35.438410

🤔 75 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 21 chat prompts
🤖 21 qwen3:1.7b replies
🥵  2 😎  8 🥶 58 🧊  6

     $1 #75   progressive  100.00°C 🥳 1000‰ ~69 used:0  [68] source:qwen3
     $2 #66 revolutionary   41.63°C 🥵  955‰  ~1 used:2   [0] source:qwen3
     $3 #61   ideological   39.68°C 🥵  930‰  ~2 used:6   [1] source:qwen3
     $4 #54      ideology   36.89°C 😎  870‰  ~7 used:2   [6] source:qwen3
     $5 #72    innovative   36.61°C 😎  860‰  ~3 used:0   [2] source:qwen3
     $6 #56      movement   35.38°C 😎  815‰  ~8 used:2   [7] source:qwen3
     $7 #29        social   31.95°C 😎  634‰ ~10 used:4   [9] source:qwen3
     $8 #42       society   29.16°C 😎  337‰  ~9 used:2   [8] source:qwen3
     $9 #52     political   28.73°C 😎  279‰  ~4 used:1   [3] source:qwen3
    $10 #63    revolution   27.82°C 😎  133‰  ~5 used:1   [4] source:qwen3
    $11 #57    philosophy   27.57°C 😎   87‰  ~6 used:0   [5] source:qwen3
    $12 #68        change   25.27°C 🥶       ~11 used:0  [10] source:qwen3
    $13 #23         party   24.21°C 🥶       ~12 used:1  [11] source:qwen3
    $70  #3       pumpkin   -0.50°C 🧊       ~70 used:0  [69] source:qwen3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1435 🥳 153 ⏱️ 0:03:31.489621

🤔 154 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 49 chat prompts
🤖 49 dolphin3:latest replies
🔥   1 🥵   4 😎  17 🥶 117 🧊  14

      $1 #154            boucle  100.00°C 🥳 1000‰ ~140  used:0  [139] source:dolphin3
      $2 #100         itération   41.16°C 🔥  998‰   ~1 used:26    [0] source:dolphin3
      $3 #150         sinusoïde   33.98°C 🥵  983‰   ~2  used:3    [1] source:dolphin3
      $4  #33        ondulation   30.15°C 🥵  948‰  ~22 used:36   [21] source:dolphin3
      $5  #34       oscillateur   28.87°C 🥵  917‰  ~21 used:22   [20] source:dolphin3
      $6  #73           vibreur   28.43°C 🥵  900‰   ~9 used:14    [8] source:dolphin3
      $7 #128        sinusoïdal   27.90°C 😎  882‰  ~10  used:2    [9] source:dolphin3
      $8 #111          itératif   27.07°C 😎  840‰  ~11  used:2   [10] source:dolphin3
      $9  #67           vibrato   26.20°C 😎  772‰  ~12  used:2   [11] source:dolphin3
     $10  #95        répétition   25.38°C 😎  717‰  ~13  used:2   [12] source:dolphin3
     $11  #92           vitesse   25.14°C 😎  700‰  ~14  used:2   [13] source:dolphin3
     $12 #103         répétitif   24.12°C 😎  599‰   ~3  used:1    [2] source:dolphin3
     $24  #46        magnétique   20.32°C 🥶        ~27  used:0   [26] source:dolphin3
    $141  #23           gravité   -0.13°C 🧊       ~141  used:0  [140] source:dolphin3

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #86 🥳 score:22 ⏱️ 0:01:42.521533

📜 2 sessions

Quordle Rescue m-w.com/games/quordle/

1. RERUN attempts:7 score:7
2. HYDRO attempts:4 score:4
3. MADLY attempts:6 score:6
4. MOIST attempts:5 score:5

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1472 😦 score:7 ⏱️ 0:04:06.505415

📜 1 sessions

Octordle Rescue

1. TRUCE attempts:6 score:6
2. CATER attempts:7 score:7
3. GRILL attempts:8 score:8
4. QUARK attempts:10 score:10
5. SWEAT attempts:11 score:11
6. LEAKY attempts:12 score:12
7. GLINT attempts:5 score:5
8. _UTCH -ABDEGIJKLMNOQRSWY attempts:13 score:-1
