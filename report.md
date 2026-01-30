# 2026-01-31

- 🔗 spaceword.org 🧩 2026-01-30 🏁 score 2173 ranked 7.6% 26/340 ⏱️ 2:26:28.834961
- 🔗 alfagok.diginaut.net 🧩 #455 🥳 48 ⏱️ 0:01:05.328817
- 🔗 alphaguess.com 🧩 #922 🥳 38 ⏱️ 0:00:53.246900
- 🔗 dontwordle.com 🧩 #1348 🥳 6 ⏱️ 0:02:27.628626
- 🔗 dictionary.com hurdle 🧩 #1491 🥳 16 ⏱️ 0:03:35.845350
- 🔗 Quordle Classic 🧩 #1468 🥳 score:23 ⏱️ 0:01:48.984324
- 🔗 Octordle Classic 🧩 #1468 😦 score:65 ⏱️ 0:04:17.443728
- 🔗 squareword.org 🧩 #1461 🥳 6 ⏱️ 0:01:26.575319
- 🔗 cemantle.certitudes.org 🧩 #1398 🥳 153 ⏱️ 0:20:59.686787
- 🔗 cemantix.certitudes.org 🧩 #1431 🥳 138 ⏱️ 0:05:24.445938
- 🔗 Quordle Rescue 🧩 #82 🥳 score:26 ⏱️ 0:01:46.768016
- 🔗 Octordle Rescue 🧩 #1468 🥳 score:8 ⏱️ 0:03:30.740396

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
















# [spaceword.org](spaceword.org) 🧩 2026-01-30 🏁 score 2173 ranked 7.6% 26/340 ⏱️ 2:26:28.834961

📜 6 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 26/340

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ J U S _ _ _   
      _ _ _ _ _ _ E _ _ _   
      _ _ _ _ Z E D _ _ _   
      _ _ _ _ E _ A _ _ _   
      _ _ _ _ B I T _ _ _   
      _ _ _ _ E _ E _ _ _   
      _ _ _ _ C _ _ _ _ _   
      _ _ _ _ K E A _ _ _   
      _ _ _ _ S L Y _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #455 🥳 48 ⏱️ 0:01:05.328817

🤔 48 attempts
📜 1 sessions

    @       [    0] &-teken      
    @+49849 [49849] boks         q4  ? ␅
    @+49849 [49849] boks         q5  ? after
    @+74762 [74762] dc           q6  ? ␅
    @+74762 [74762] dc           q7  ? after
    @+87223 [87223] draag        q8  ? ␅
    @+87223 [87223] draag        q9  ? after
    @+90075 [90075] dubbel       q12 ? ␅
    @+90075 [90075] dubbel       q13 ? after
    @+90489 [90489] duik         q34 ? ␅
    @+90489 [90489] duik         q35 ? after
    @+90531 [90531] duikel       q40 ? ␅
    @+90531 [90531] duikel       q41 ? after
    @+90538 [90538] duikelen     q44 ? ␅
    @+90538 [90538] duikelen     q45 ? after
    @+90544 [90544] duiken       q46 ? ␅
    @+90544 [90544] duiken       q47 ? it
    @+90544 [90544] duiken       done. it
    @+90547 [90547] duiker       q42 ? ␅
    @+90547 [90547] duiker       q43 ? before
    @+90572 [90572] duikgebieden q38 ? ␅
    @+90572 [90572] duikgebieden q39 ? before
    @+90654 [90654] duim         q36 ? ␅
    @+90654 [90654] duim         q37 ? before
    @+90893 [90893] duivels      q16 ? ␅
    @+90893 [90893] duivels      q17 ? before
    @+91755 [91755] dwerg        q14 ? ␅
    @+91755 [91755] dwerg        q15 ? before
    @+93443 [93443] eet          q10 ? ␅
    @+93443 [93443] eet          q11 ? before
    @+99750 [99750] ex           q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #922 🥳 38 ⏱️ 0:00:53.246900

🤔 38 attempts
📜 1 sessions

    @        [     0] aa         
    @+98220  [ 98220] mach       q0  ? ␅
    @+98220  [ 98220] mach       q1  ? after
    @+147373 [147373] rhotic     q2  ? ␅
    @+147373 [147373] rhotic     q3  ? after
    @+159490 [159490] slop       q6  ? ␅
    @+159490 [159490] slop       q7  ? after
    @+165532 [165532] stick      q8  ? ␅
    @+165532 [165532] stick      q9  ? after
    @+166291 [166291] straddle   q14 ? ␅
    @+166291 [166291] straddle   q15 ? after
    @+166667 [166667] stria      q16 ? ␅
    @+166667 [166667] stria      q17 ? after
    @+166745 [166745] string     q20 ? ␅
    @+166745 [166745] string     q21 ? after
    @+166774 [166774] strip      q22 ? ␅
    @+166774 [166774] strip      q23 ? after
    @+166775 [166775] stripe     q36 ? ␅
    @+166775 [166775] stripe     q37 ? it
    @+166775 [166775] stripe     done. it
    @+166776 [166776] striped    q34 ? ␅
    @+166776 [166776] striped    q35 ? before
    @+166777 [166777] stripeless q32 ? ␅
    @+166777 [166777] stripeless q33 ? before
    @+166779 [166779] stripers   q30 ? ␅
    @+166779 [166779] stripers   q31 ? before
    @+166784 [166784] striping   q28 ? ␅
    @+166784 [166784] striping   q29 ? before
    @+166794 [166794] stript     q26 ? ␅
    @+166794 [166794] stript     q27 ? before
    @+166811 [166811] strobil    q25 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1348 🥳 6 ⏱️ 0:02:27.628626

📜 2 sessions
💰 score: 63

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:PZAZZ n n n n n remain:6291
    ⬜⬜⬜⬜⬜ tried:EBBED n n n n n remain:2059
    ⬜⬜⬜⬜⬜ tried:COOCH n n n n n remain:611
    ⬜⬜⬜⬜⬜ tried:JUJUS n n n n n remain:98
    ⬜🟨⬜⬜⬜ tried:TITTY n m n n n remain:10
    🟨⬜⬜⬜⬜ tried:IMMIX m n n n n remain:7

    Undos used: 3

      7 words remaining
    x 9 unused letters
    = 63 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1491 🥳 16 ⏱️ 0:03:35.845350

📜 2 sessions
💰 score: 10000

    4/6
    AROSE ⬜⬜⬜🟨🟩
    SNIPE 🟩🟨🟨⬜🟩
    SINCE 🟩🟩🟩⬜🟩
    SINGE 🟩🟩🟩🟩🟩
    6/6
    SINGE 🟩⬜⬜⬜⬜
    SPOUT 🟩⬜⬜🟨⬜
    SAUCY 🟩⬜🟩⬜⬜
    SMUSH 🟩⬜🟩🟩🟩
    SLUSH 🟩⬜🟩🟩🟩
    SHUSH 🟩🟩🟩🟩🟩
    3/6
    SHUSH ⬜⬜⬜⬜⬜
    ALIEN 🟨⬜🟨⬜⬜
    TAPIR 🟩🟩🟩🟩🟩
    2/6
    TAPIR 🟨🟨⬜🟨🟨
    IRATE 🟩🟩🟩🟩🟩
    Final 1/2
    GROWN 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1468 🥳 score:23 ⏱️ 0:01:48.984324

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. GRAPE attempts:7 score:7
2. GENRE attempts:3 score:3
3. BEARD attempts:5 score:5
4. RIVER attempts:8 score:8

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1468 😦 score:65 ⏱️ 0:04:17.443728

📜 2 sessions

Octordle Classic

1. DOPEY attempts:9 score:9
2. BLOAT attempts:12 score:12
3. MUCKY attempts:5 score:5
4. _ATER -BCDFGHIKLMNOPSUWY attempts:13 score:-1
5. DIODE attempts:7 score:7
6. GENIE attempts:6 score:6
7. TEDDY attempts:8 score:8
8. CRUEL attempts:4 score:4

# [squareword.org](squareword.org) 🧩 #1461 🥳 6 ⏱️ 0:01:26.575319

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    R A F T S
    A G L O W
    C R O N E
    E E R I E
    R E A C T

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1398 🥳 153 ⏱️ 0:20:59.686787

🤔 154 attempts
📜 6 sessions
🫧 7 chat sessions
⁉️ 39 chat prompts
🤖 39 dolphin3:latest replies
🥵   1 😎  13 🥶 131 🧊   8

      $1 #154    substitute  100.00°C 🥳 1000‰  ~1  used:0  [289] source:dolphin3
      $2 #112    supplement   31.15°C 🥵  957‰ ~10 used:13    [2] source:dolphin3
      $3 #152     sweetener   26.33°C 😎  875‰  ~2  used:1    [0] source:dolphin3
      $4 #145    reinforcer   25.49°C 😎  851‰  ~4  used:3   [12] source:dolphin3
      $5 #121  preservative   23.29°C 😎  752‰  ~7  used:3   [14] source:dolphin3
      $6 #117    emulsifier   22.56°C 😎  708‰  ~8  used:3   [16] source:dolphin3
      $7 #129     humectant   21.32°C 😎  575‰  ~5  used:3   [18] source:dolphin3
      $8  #95     flavoring   20.69°C 😎  482‰ ~13  used:4   [22] source:dolphin3
      $9 #149    flavouring   20.69°C 😎  482‰  ~3  used:2    [4] source:dolphin3
     $10 #113      additive   20.66°C 😎  477‰  ~9  used:3   [20] source:dolphin3
     $11 #124        sealer   20.63°C 😎  473‰  ~6  used:2    [6] source:dolphin3
     $12 #109      enhancer   20.14°C 😎  387‰ ~12  used:2    [8] source:dolphin3
     $16 #123     protector   18.53°C 🥶            used:0   [30] source:dolphin3
    $147  #79      infinity   -0.01°C 🧊            used:0  [290] source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1431 🥳 138 ⏱️ 0:05:24.445938

🤔 139 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 38 chat prompts
🤖 38 dolphin3:latest replies
🥵  3 😎 11 🥶 98 🧊 26

      $1 #139        cauchemar  100.00°C 🥳 1000‰  ~1 used:0  [223] source:dolphin3
      $2 #108    hallucination   44.56°C 🥵  986‰ ~13 used:3    [2] source:dolphin3
      $3 #117          monstre   40.47°C 🥵  971‰  ~9 used:4    [4] source:dolphin3
      $4 #128       sombrement   36.26°C 🥵  927‰  ~3 used:2    [0] source:dolphin3
      $5 #127           sombre   34.56°C 😎  883‰  ~4 used:1    [6] source:dolphin3
      $6 #109          chimère   32.84°C 😎  840‰ ~12 used:2   [24] source:dolphin3
      $7 #124         noirceur   30.43°C 😎  720‰  ~6 used:1    [8] source:dolphin3
      $8 #123          ténèbre   29.62°C 😎  642‰  ~7 used:1   [10] source:dolphin3
      $9 #110         illusion   29.59°C 😎  639‰ ~11 used:1   [12] source:dolphin3
     $10 #106           mirage   28.29°C 😎  538‰ ~14 used:1   [14] source:dolphin3
     $11 #120            ombre   28.23°C 😎  532‰  ~8 used:1   [16] source:dolphin3
     $12 #115            hydre   27.16°C 😎  418‰ ~10 used:1   [18] source:dolphin3
     $16  #99           obscur   24.53°C 🥶           used:1   [32] source:dolphin3
    $114  #78            clair   -0.49°C 🧊           used:0  [224] source:dolphin3

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #82 🥳 score:26 ⏱️ 0:01:46.768016

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. BASIL attempts:5 score:5
2. STUNK attempts:6 score:6
3. CLASP attempts:7 score:7
4. IDEAL attempts:8 score:8

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1468 🥳 score:8 ⏱️ 0:03:30.740396

📜 2 sessions

Octordle Rescue

1. PLANK attempts:12 score:12
2. JOKER attempts:13 score:13
3. CORAL attempts:5 score:5
4. UNWED attempts:9 score:9
5. SWARM attempts:10 score:10
6. FLIRT attempts:8 score:8
7. TROVE attempts:7 score:7
8. AUDIO attempts:6 score:6
