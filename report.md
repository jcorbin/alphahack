# 2026-02-01

- 🔗 spaceword.org 🧩 2026-01-31 🏁 score 2173 ranked 3.9% 14/357 ⏱️ 0:31:25.159617
- 🔗 alfagok.diginaut.net 🧩 #456 🥳 42 ⏱️ 0:01:00.935758
- 🔗 alphaguess.com 🧩 #923 🥳 38 ⏱️ 0:00:38.087592
- 🔗 dontwordle.com 🧩 #1349 🥳 6 ⏱️ 0:01:17.727913
- 🔗 dictionary.com hurdle 🧩 #1492 🥳 17 ⏱️ 0:02:37.303803
- 🔗 Quordle Classic 🧩 #1469 🥳 score:24 ⏱️ 0:01:33.887584
- 🔗 Octordle Classic 🧩 #1469 🥳 score:56 ⏱️ 0:03:04.680664
- 🔗 squareword.org 🧩 #1462 🥳 8 ⏱️ 0:02:15.800054
- 🔗 cemantle.certitudes.org 🧩 #1399 🥳 123 ⏱️ 0:01:24.547947
- 🔗 cemantix.certitudes.org 🧩 #1432 🥳 189 ⏱️ 0:04:52.432900
- 🔗 Quordle Rescue 🧩 #83 🥳 score:29 ⏱️ 0:02:25.584895

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

















# [spaceword.org](spaceword.org) 🧩 2026-01-31 🏁 score 2173 ranked 3.9% 14/357 ⏱️ 0:31:25.159617

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 14/357

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ L O W _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ _ I O N _ _ _   
      _ _ _ _ R U T _ _ _   
      _ _ _ _ E G O _ _ _   
      _ _ _ _ _ U N _ _ _   
      _ _ _ _ Q I _ _ _ _   
      _ _ _ _ _ Y _ _ _ _   
      _ _ _ _ F A X _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #456 🥳 42 ⏱️ 0:01:00.935758

🤔 42 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+199833 [199833] lijm         q0  ? ␅
    @+199833 [199833] lijm         q1  ? after
    @+299738 [299738] schub        q2  ? ␅
    @+299738 [299738] schub        q3  ? after
    @+311908 [311908] spier        q8  ? ␅
    @+311908 [311908] spier        q9  ? after
    @+314901 [314901] staats       q12 ? ␅
    @+314901 [314901] staats       q13 ? after
    @+316389 [316389] standaard    q14 ? ␅
    @+316389 [316389] standaard    q15 ? after
    @+317031 [317031] stat         q18 ? ␅
    @+317031 [317031] stat         q19 ? after
    @+317474 [317474] steen        q20 ? ␅
    @+317474 [317474] steen        q21 ? after
    @+317790 [317790] steg         q28 ? ␅
    @+317790 [317790] steg         q29 ? after
    @+317890 [317890] stek         q30 ? ␅
    @+317890 [317890] stek         q31 ? after
    @+317893 [317893] stekel       q34 ? ␅
    @+317893 [317893] stekel       q35 ? after
    @+317926 [317926] stekelvarken q36 ? ␅
    @+317926 [317926] stekelvarken q37 ? after
    @+317933 [317933] steken       q40 ? ␅
    @+317933 [317933] steken       q41 ? it
    @+317933 [317933] steken       done. it
    @+317946 [317946] stekjes      q38 ? ␅
    @+317946 [317946] stekjes      q39 ? before
    @+317966 [317966] stel         q32 ? ␅
    @+317966 [317966] stel         q33 ? before
    @+318101 [318101] stem         q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #923 🥳 38 ⏱️ 0:00:38.087592

🤔 38 attempts
📜 1 sessions

    @       [    0] aa            
    @+5876  [ 5876] angel         q8  ? ␅
    @+5876  [ 5876] angel         q9  ? after
    @+8323  [ 8323] ar            q10 ? ␅
    @+8323  [ 8323] ar            q11 ? after
    @+9341  [ 9341] as            q12 ? ␅
    @+9341  [ 9341] as            q13 ? after
    @+9947  [ 9947] asthenosphere q16 ? ␅
    @+9947  [ 9947] asthenosphere q17 ? after
    @+10247 [10247] atonal        q18 ? ␅
    @+10247 [10247] atonal        q19 ? after
    @+10396 [10396] attest        q20 ? ␅
    @+10396 [10396] attest        q21 ? after
    @+10409 [10409] attic         q26 ? ␅
    @+10409 [10409] attic         q27 ? after
    @+10420 [10420] attire        q28 ? ␅
    @+10420 [10420] attire        q29 ? after
    @+10423 [10423] attiring      q32 ? ␅
    @+10423 [10423] attiring      q33 ? after
    @+10424 [10424] attitude      q36 ? ␅
    @+10424 [10424] attitude      q37 ? it
    @+10424 [10424] attitude      done. it
    @+10425 [10425] attitudes     q34 ? ␅
    @+10425 [10425] attitudes     q35 ? before
    @+10426 [10426] attitudinal   q30 ? ␅
    @+10426 [10426] attitudinal   q31 ? before
    @+10432 [10432] attitudinize  q24 ? ␅
    @+10432 [10432] attitudinize  q25 ? before
    @+10472 [10472] attribution   q22 ? ␅
    @+10472 [10472] attribution   q23 ? before
    @+10553 [10553] audient       q15 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1349 🥳 6 ⏱️ 0:01:17.727913

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:7870
    ⬜⬜⬜⬜⬜ tried:YOBBY n n n n n remain:3509
    ⬜⬜⬜⬜⬜ tried:WUSHU n n n n n remain:798
    ⬜🟨⬜⬜⬜ tried:GRRRL n m n n n remain:78
    ⬜🟨⬜⬜🟩 tried:NAVAR n m n n Y remain:4
    🟩⬜⬜🟩🟩 tried:ADDER Y n n Y Y remain:3

    Undos used: 3

      3 words remaining
    x 8 unused letters
    = 24 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1492 🥳 17 ⏱️ 0:02:37.303803

📜 1 sessions
💰 score: 9900

    4/6
    EYRAS 🟨⬜⬜⬜⬜
    OLDIE ⬜🟨⬜⬜🟨
    LUNET 🟨⬜⬜🟨⬜
    WELCH 🟩🟩🟩🟩🟩
    3/6
    WELCH ⬜🟨⬜⬜🟨
    THOSE 🟨🟨🟨🟨🟨
    ETHOS 🟩🟩🟩🟩🟩
    4/6
    ETHOS 🟨⬜⬜⬜🟨
    MARSE ⬜⬜🟩🟨🟩
    SPRUE 🟩⬜🟩🟨🟩
    SURGE 🟩🟩🟩🟩🟩
    4/6
    SURGE ⬜⬜⬜⬜⬜
    PINOT 🟨⬜⬜🟨⬜
    CHOMP ⬜⬜🟩⬜🟨
    LOOPY 🟩🟩🟩🟩🟩
    Final 2/2
    MIDST ⬜🟩⬜🟨🟨
    VISTA 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1469 🥳 score:24 ⏱️ 0:01:33.887584

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SNARL attempts:3 score:3
2. BEGIN attempts:5 score:5
3. FLASK attempts:9 score:9
4. AGONY attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1469 🥳 score:56 ⏱️ 0:03:04.680664

📜 1 sessions

Octordle Classic

1. FAULT attempts:5 score:5
2. TRIPE attempts:10 score:10
3. RUPEE attempts:9 score:9
4. DISCO attempts:3 score:3
5. ANGEL attempts:6 score:6
6. ROVER attempts:12 score:12
7. OMEGA attempts:7 score:7
8. FLIRT attempts:4 score:4

# [squareword.org](squareword.org) 🧩 #1462 🥳 8 ⏱️ 0:02:15.800054

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B U S E S
    A S I D E
    R A N G E
    E G G E D
    R E E D Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1399 🥳 123 ⏱️ 0:01:24.547947

🤔 124 attempts
📜 2 sessions
🫧 5 chat sessions
⁉️ 19 chat prompts
🤖 19 dolphin3:latest replies
🔥  2 🥵  8 😎 37 🥶 71 🧊  5

      $1 #124    operational  100.00°C 🥳 1000‰  ~1 used:0  [235] source:dolphin3
      $2 #119      strategic   48.06°C 🔥  996‰  ~2 used:1    [0] source:dolphin3
      $3 #117 organizational   44.87°C 🔥  994‰  ~4 used:0    [2] source:dolphin3
      $4  #51     management   39.11°C 🥵  987‰ ~32 used:7   [18] source:dolphin3
      $5 #115 implementation   37.60°C 🥵  979‰  ~5 used:0    [4] source:dolphin3
      $6 #112     capability   36.39°C 🥵  973‰  ~8 used:0    [6] source:dolphin3
      $7  #62    integration   34.61°C 🥵  960‰ ~25 used:3   [16] source:dolphin3
      $8  #64   optimization   34.42°C 🥵  958‰ ~24 used:1    [8] source:dolphin3
      $9 #110     functional   33.09°C 🥵  944‰ ~10 used:1   [10] source:dolphin3
     $10  #54     automation   32.32°C 🥵  938‰ ~29 used:0   [12] source:dolphin3
     $11  #58     efficiency   30.31°C 🥵  908‰ ~27 used:0   [14] source:dolphin3
     $12  #81       planning   28.97°C 😎  884‰ ~16 used:0   [20] source:dolphin3
     $48  #39      authority   19.99°C 🥶           used:0   [80] source:dolphin3
    $120 #121         talent   -0.22°C 🧊           used:0  [236] source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1432 🥳 189 ⏱️ 0:04:52.432900

🤔 190 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 47 chat prompts
🤖 47 dolphin3:latest replies
🔥  2 🥵  7 😎 31 🥶 85 🧊 64

      $1 #190   reconnaissant  100.00°C 🥳 1000‰ ~126  used:0  [125] source:dolphin3
      $2 #183       gratitude   53.47°C 🔥  998‰   ~2  used:2    [1] source:dolphin3
      $3 #188    remerciement   43.67°C 🔥  992‰   ~1  used:1    [0] source:dolphin3
      $4 #153         dévouer   41.38°C 🥵  987‰  ~36 used:17   [35] source:dolphin3
      $5 #128         sincère   39.21°C 🥵  984‰  ~35 used:15   [34] source:dolphin3
      $6 #131      dévouement   38.71°C 🥵  980‰   ~6  used:9    [5] source:dolphin3
      $7 #187           merci   34.76°C 🥵  955‰   ~3  used:0    [2] source:dolphin3
      $8 #102         honneur   33.43°C 🥵  944‰   ~7  used:9    [6] source:dolphin3
      $9  #96      admiration   33.32°C 🥵  942‰   ~4  used:8    [3] source:dolphin3
     $10 #123          estime   31.75°C 🥵  922‰   ~5  used:8    [4] source:dolphin3
     $11 #125         louange   30.38°C 😎  895‰   ~8  used:0    [7] source:dolphin3
     $12 #176          fidèle   28.94°C 😎  875‰   ~9  used:0    [8] source:dolphin3
     $42 #172          vérité   17.16°C 🥶        ~53  used:0   [52] source:dolphin3
    $127  #19         fromage   -0.05°C 🧊       ~127  used:1  [126] source:dolphin3

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #83 🥳 score:29 ⏱️ 0:02:25.584895

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. SNIDE attempts:5 score:5
2. HENCE attempts:7 score:7
3. ENSUE attempts:8 score:8
4. GULCH attempts:9 score:9
