# 2026-02-24

- 🔗 spaceword.org 🧩 2026-02-23 🏁 score 2173 ranked 4.9% 18/367 ⏱️ 6:27:13.757382
- 🔗 alfagok.diginaut.net 🧩 #479 🥳 30 ⏱️ 0:00:37.063310
- 🔗 alphaguess.com 🧩 #946 🥳 36 ⏱️ 0:00:39.503556
- 🔗 dontwordle.com 🧩 #1372 🤷 6 ⏱️ 0:02:01.040321
- 🔗 dictionary.com hurdle 🧩 #1515 😦 19 ⏱️ 0:02:58.256935
- 🔗 Quordle Classic 🧩 #1492 🥳 score:24 ⏱️ 0:01:39.688093
- 🔗 Octordle Classic 🧩 #1492 🥳 score:58 ⏱️ 0:03:29.970160
- 🔗 squareword.org 🧩 #1485 🥳 8 ⏱️ 0:02:09.580970
- 🔗 cemantle.certitudes.org 🧩 #1422 🥳 249 ⏱️ 0:02:42.785702
- 🔗 cemantix.certitudes.org 🧩 #1455 🥳 359 ⏱️ 1:20:27.047748

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






# [spaceword.org](spaceword.org) 🧩 2026-02-23 🏁 score 2173 ranked 4.9% 18/367 ⏱️ 6:27:13.757382

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 18/367

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ I C Y _ _ _   
      _ _ _ _ _ R _ _ _ _   
      _ _ _ _ T A J _ _ _   
      _ _ _ _ A W E _ _ _   
      _ _ _ _ U _ E _ _ _   
      _ _ _ _ R _ I _ _ _   
      _ _ _ _ I O N _ _ _   
      _ _ _ _ N _ G _ _ _   
      _ _ _ _ E X _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #479 🥳 30 ⏱️ 0:00:37.063310

🤔 30 attempts
📜 1 sessions

    @        [     0] &-teken        
    @+199816 [199816] lijm           q0  ? ␅
    @+199816 [199816] lijm           q1  ? after
    @+247706 [247706] op             q4  ? ␅
    @+247706 [247706] op             q5  ? after
    @+260592 [260592] pater          q8  ? ␅
    @+260592 [260592] pater          q9  ? after
    @+267045 [267045] plomp          q10 ? ␅
    @+267045 [267045] plomp          q11 ? after
    @+270118 [270118] pot            q12 ? ␅
    @+270118 [270118] pot            q13 ? after
    @+270439 [270439] pr             q18 ? ␅
    @+270439 [270439] pr             q19 ? after
    @+270491 [270491] praat          q22 ? ␅
    @+270491 [270491] praat          q23 ? after
    @+270546 [270546] pracht         q24 ? ␅
    @+270546 [270546] pracht         q25 ? after
    @+270562 [270562] prachtig       q28 ? ␅
    @+270562 [270562] prachtig       q29 ? it
    @+270562 [270562] prachtig       done. it
    @+270581 [270581] prachtlievende q26 ? ␅
    @+270581 [270581] prachtlievende q27 ? before
    @+270615 [270615] practicum      q20 ? ␅
    @+270615 [270615] practicum      q21 ? before
    @+270797 [270797] pre            q16 ? ␅
    @+270797 [270797] pre            q17 ? before
    @+271779 [271779] prijs          q14 ? ␅
    @+271779 [271779] prijs          q15 ? before
    @+273511 [273511] proef          q6  ? ␅
    @+273511 [273511] proef          q7  ? before
    @+299709 [299709] schub          q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #946 🥳 36 ⏱️ 0:00:39.503556

🤔 36 attempts
📜 1 sessions

    @        [     0] aa      
    @+98218  [ 98218] mach    q0  ? ␅
    @+98218  [ 98218] mach    q1  ? after
    @+147374 [147374] rhumb   q2  ? ␅
    @+147374 [147374] rhumb   q3  ? after
    @+171639 [171639] ta      q4  ? ␅
    @+171639 [171639] ta      q5  ? after
    @+176810 [176810] toil    q8  ? ␅
    @+176810 [176810] toil    q9  ? after
    @+179405 [179405] tricot  q10 ? ␅
    @+179405 [179405] tricot  q11 ? after
    @+180012 [180012] trop    q14 ? ␅
    @+180012 [180012] trop    q15 ? after
    @+180314 [180314] trust   q16 ? ␅
    @+180314 [180314] trust   q17 ? after
    @+180467 [180467] tub     q18 ? ␅
    @+180467 [180467] tub     q19 ? after
    @+180468 [180468] tuba    q34 ? ␅
    @+180468 [180468] tuba    q35 ? it
    @+180468 [180468] tuba    done. it
    @+180469 [180469] tubae   q32 ? ␅
    @+180469 [180469] tubae   q33 ? before
    @+180470 [180470] tubaist q30 ? ␅
    @+180470 [180470] tubaist q31 ? before
    @+180472 [180472] tubal   q28 ? ␅
    @+180472 [180472] tubal   q29 ? before
    @+180476 [180476] tubbed  q26 ? ␅
    @+180476 [180476] tubbed  q27 ? before
    @+180485 [180485] tube    q24 ? ␅
    @+180485 [180485] tube    q25 ? before
    @+180553 [180553] tuchun  q23 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1372 🤷 6 ⏱️ 0:02:01.040321

📜 1 sessions
💰 score: 0

ELIMINATED
> Well technically I didn't Wordle!

    ⬜⬜⬜⬜⬜ tried:STOTS n n n n n remain:3618
    ⬜⬜⬜⬜⬜ tried:KEEVE n n n n n remain:1313
    ⬜⬜⬜⬜⬜ tried:WUDDY n n n n n remain:408
    ⬜🟨⬜⬜⬜ tried:GRRRL n m n n n remain:14
    🟨🟨⬜⬜🟨 tried:RAJAH m m n n m remain:1
    ⬛⬛⬛⬛⬛ tried:????? remain:0

    Undos used: 5

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1515 😦 19 ⏱️ 0:02:58.256935

📜 1 sessions
💰 score: 3560

    3/6
    SATED ⬜🟩⬜⬜⬜
    RACON ⬜🟩⬜⬜🟨
    MANLY 🟩🟩🟩🟩🟩
    4/6
    MANLY ⬜🟨⬜🟨⬜
    LEARS 🟨⬜🟩🟨⬜
    GRAIL ⬜🟨🟩🟩🟨
    FLAIR 🟩🟩🟩🟩🟩
    6/6
    FLAIR ⬜⬜🟨⬜🟨
    RATES 🟨🟩⬜⬜⬜
    BARKY ⬜🟩🟩⬜🟩
    HARPY ⬜🟩🟩⬜🟩
    CARNY ⬜🟩🟩⬜🟩
    MARRY 🟩🟩🟩🟩🟩
    6/6
    ????? ⬜⬜⬜⬜🟩
    ????? 🟩🟩⬜⬜🟩
    ????? 🟩🟩⬜⬜🟩
    ????? 🟩🟩⬜⬜🟩
    ????? 🟩🟩⬜⬜🟩
    ????? 🟩🟩⬜⬜🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1492 🥳 score:24 ⏱️ 0:01:39.688093

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. UDDER attempts:5 score:5
2. BURNT attempts:4 score:4
3. PLUSH attempts:7 score:7
4. VAPOR attempts:8 score:8

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1492 🥳 score:58 ⏱️ 0:03:29.970160

📜 2 sessions

Octordle Classic

1. FORTE attempts:2 score:2
2. STAKE attempts:12 score:12
3. PLEAT attempts:6 score:6
4. BORAX attempts:8 score:8
5. METAL attempts:7 score:7
6. SPOON attempts:4 score:4
7. CURSE attempts:9 score:9
8. FLUID attempts:10 score:10

# [squareword.org](squareword.org) 🧩 #1485 🥳 8 ⏱️ 0:02:09.580970

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟩 🟨 🟨 🟨
    🟨 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C L A S H
    H I P P O
    A V I A N
    S I N C E
    E D G E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1422 🥳 249 ⏱️ 0:02:42.785702

🤔 250 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 52 chat prompts
🤖 52 dolphin3:latest replies
🥵   8 😎  14 🥶 219 🧊   8

      $1 #250 typical          100.00°C 🥳 1000‰ ~242 used:0  [241]  source:dolphin3
      $2 #166 traditional       44.42°C 🥵  985‰  ~17 used:22 [16]   source:dolphin3
      $3 #204 norm              41.45°C 🥵  982‰   ~3 used:10 [2]    source:dolphin3
      $4 #164 classic           39.44°C 🥵  979‰  ~14 used:14 [13]   source:dolphin3
      $5 #167 conventional      37.88°C 🥵  973‰  ~12 used:11 [11]   source:dolphin3
      $6 #195 customary         36.90°C 🥵  965‰   ~2 used:6  [1]    source:dolphin3
      $7 #142 ideal             36.16°C 🥵  960‰  ~13 used:13 [12]   source:dolphin3
      $8 #236 style             34.80°C 🥵  942‰   ~1 used:2  [0]    source:dolphin3
      $9  #78 like              34.58°C 🥵  939‰  ~15 used:18 [14]   source:dolphin3
     $10 #151 perfect           31.84°C 😎  877‰  ~18 used:3  [17]   source:dolphin3
     $11 #152 standard          31.47°C 😎  862‰  ~16 used:2  [15]   source:dolphin3
     $12 #179 old               29.20°C 😎  715‰   ~4 used:1  [3]    source:dolphin3
     $24  #69 approach          24.32°C 🥶        ~32 used:0  [31]   source:dolphin3
    $243  #40 concealment       -0.20°C 🧊       ~243 used:0  [242]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1455 🥳 359 ⏱️ 1:20:27.047748

🤔 360 attempts
📜 1 sessions
🫧 19 chat sessions
⁉️ 99 chat prompts
🤖 99 dolphin3:latest replies
😱   1 🔥   2 🥵  20 😎  60 🥶 243 🧊  33

      $1 #360 tir              100.00°C 🥳 1000‰ ~327 used:0  [326]  source:dolphin3
      $2 #269 carabine          55.54°C 😱  999‰   ~1 used:58 [0]    source:dolphin3
      $3 #289 projectile        49.81°C 🔥  997‰  ~16 used:24 [15]   source:dolphin3
      $4 #346 balle             47.38°C 🔥  996‰  ~11 used:12 [10]   source:dolphin3
      $5 #282 munition          43.24°C 🥵  987‰  ~17 used:4  [16]   source:dolphin3
      $6 #299 missile           42.50°C 🥵  985‰  ~12 used:2  [11]   source:dolphin3
      $7 #266 fusil             41.56°C 🥵  982‰  ~13 used:2  [12]   source:dolphin3
      $8 #286 pistolet          41.33°C 🥵  981‰  ~14 used:2  [13]   source:dolphin3
      $9 #283 obus              41.07°C 🥵  979‰  ~15 used:2  [14]   source:dolphin3
     $10 #260 artillerie        40.58°C 🥵  978‰  ~19 used:6  [18]   source:dolphin3
     $11 #277 obusier           39.33°C 🥵  974‰   ~2 used:0  [1]    source:dolphin3
     $25 #326 tactique          32.68°C 😎  899‰  ~21 used:0  [20]   source:dolphin3
     $85 #113 poussée           19.73°C 🥶        ~86 used:0  [85]   source:dolphin3
    $328   #7 musique           -0.03°C 🧊       ~328 used:0  [327]  source:dolphin3
