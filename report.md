# 2026-02-13

- 🔗 spaceword.org 🧩 2026-02-12 🏁 score 2168 ranked 32.7% 116/355 ⏱️ 0:18:44.510396
- 🔗 alfagok.diginaut.net 🧩 #468 🥳 32 ⏱️ 0:00:41.490081
- 🔗 alphaguess.com 🧩 #935 🥳 22 ⏱️ 0:00:23.967066
- 🔗 dontwordle.com 🧩 #1361 🥳 6 ⏱️ 0:02:21.116199
- 🔗 dictionary.com hurdle 🧩 #1504 🥳 15 ⏱️ 0:03:04.273994
- 🔗 Quordle Classic 🧩 #1481 🥳 score:26 ⏱️ 0:03:26.689991
- 🔗 Octordle Classic 🧩 #1481 🥳 score:60 ⏱️ 0:03:32.457414
- 🔗 squareword.org 🧩 #1474 🥳 10 ⏱️ 0:05:31.330841
- 🔗 cemantle.certitudes.org 🧩 #1411 🥳 233 ⏱️ 0:02:07.577166
- 🔗 cemantix.certitudes.org 🧩 #1444 🥳 128 ⏱️ 0:01:28.609704
- 🔗 Quordle Rescue 🧩 #95 🥳 score:25 ⏱️ 0:01:32.299400

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





























# [spaceword.org](spaceword.org) 🧩 2026-02-12 🏁 score 2168 ranked 32.7% 116/355 ⏱️ 0:18:44.510396

📜 2 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 116/355

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ V I G A _ _ _   
      _ _ _ _ _ _ C _ _ _   
      _ _ _ _ Z _ Q _ _ _   
      _ _ _ _ O _ U _ _ _   
      _ _ _ R A G I _ _ _   
      _ _ _ _ R O T _ _ _   
      _ _ _ _ I _ S _ _ _   
      _ _ _ E A R _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #468 🥳 32 ⏱️ 0:00:41.490081

🤔 32 attempts
📜 2 sessions

    @        [     0] &-teken    
    @+199817 [199817] lijm       q0  ? ␅
    @+199817 [199817] lijm       q1  ? after
    @+299722 [299722] schub      q2  ? ␅
    @+299722 [299722] schub      q3  ? after
    @+324288 [324288] sub        q6  ? ␅
    @+324288 [324288] sub        q7  ? after
    @+336883 [336883] toetsing   q8  ? ␅
    @+336883 [336883] toetsing   q9  ? after
    @+336959 [336959] toeven     q22 ? ␅
    @+336959 [336959] toeven     q23 ? after
    @+336990 [336990] toevoeg    q24 ? ␅
    @+336990 [336990] toevoeg    q25 ? after
    @+336995 [336995] toevoegen  q30 ? ␅
    @+336995 [336995] toevoegen  q31 ? it
    @+336995 [336995] toevoegen  done. it
    @+336998 [336998] toevoeging q28 ? ␅
    @+336998 [336998] toevoeging q29 ? before
    @+337007 [337007] toevoer    q26 ? ␅
    @+337007 [337007] toevoer    q27 ? before
    @+337037 [337037] toewenden  q20 ? ␅
    @+337037 [337037] toewenden  q21 ? before
    @+337191 [337191] toilet     q18 ? ␅
    @+337191 [337191] toilet     q19 ? before
    @+337540 [337540] toneel     q16 ? ␅
    @+337540 [337540] toneel     q17 ? before
    @+338373 [338373] topt       q14 ? ␅
    @+338373 [338373] topt       q15 ? before
    @+339874 [339874] transport  q12 ? ␅
    @+339874 [339874] transport  q13 ? before
    @+343073 [343073] tv         q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #935 🥳 22 ⏱️ 0:00:23.967066

🤔 22 attempts
📜 1 sessions

    @        [     0] aa       
    @+1      [     1] aah      
    @+2      [     2] aahed    
    @+3      [     3] aahing   
    @+98219  [ 98219] mach     q0  ? ␅
    @+98219  [ 98219] mach     q1  ? after
    @+147375 [147375] rhumb    q2  ? ␅
    @+147375 [147375] rhumb    q3  ? after
    @+159487 [159487] slop     q6  ? ␅
    @+159487 [159487] slop     q7  ? after
    @+159848 [159848] smell    q16 ? ␅
    @+159848 [159848] smell    q17 ? after
    @+160033 [160033] smoulder q18 ? ␅
    @+160033 [160033] smoulder q19 ? after
    @+160121 [160121] snake    q20 ? ␅
    @+160121 [160121] snake    q21 ? it
    @+160121 [160121] snake    done. it
    @+160226 [160226] snath    q14 ? ␅
    @+160226 [160226] snath    q15 ? before
    @+160966 [160966] soft     q12 ? ␅
    @+160966 [160966] soft     q13 ? before
    @+162474 [162474] spec     q10 ? ␅
    @+162474 [162474] spec     q11 ? before
    @+165529 [165529] stick    q8  ? ␅
    @+165529 [165529] stick    q9  ? before
    @+171640 [171640] ta       q4  ? ␅
    @+171640 [171640] ta       q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1361 🥳 6 ⏱️ 0:02:21.116199

📜 2 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:7870
    ⬜⬜⬜⬜⬜ tried:DEWED n n n n n remain:3118
    ⬜⬜⬜⬜⬜ tried:KAZOO n n n n n remain:375
    ⬜⬜⬜⬜⬜ tried:GHYLL n n n n n remain:86
    🟨⬜⬜⬜🟩 tried:UNCUT m n n n Y remain:6
    ⬜🟨🟨🟩🟩 tried:TRUST n m m Y Y remain:1

    Undos used: 5

      1 words remaining
    x 6 unused letters
    = 6 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1504 🥳 15 ⏱️ 0:03:04.273994

📜 1 sessions
💰 score: 10100

    4/6
    RAISE ⬜⬜⬜⬜⬜
    PLUMY ⬜🟩🟩⬜⬜
    CLUNK 🟩🟩🟩⬜🟩
    CLUCK 🟩🟩🟩🟩🟩
    2/6
    CLUCK 🟨🟨🟨⬜🟨
    LUCKY 🟩🟩🟩🟩🟩
    4/6
    LUCKY 🟨⬜⬜⬜⬜
    FILES ⬜⬜🟨🟨⬜
    PLEAD ⬜🟩🟨🟨🟨
    BLADE 🟩🟩🟩🟩🟩
    3/6
    BLADE ⬜⬜⬜⬜🟨
    RESIN 🟨🟨⬜⬜🟩
    GREEN 🟩🟩🟩🟩🟩
    Final 2/2
    TABLE ⬜🟨🟩🟩🟩
    AMBLE 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1481 🥳 score:26 ⏱️ 0:03:26.689991

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. ALLOT attempts:6 score:6
2. LEERY attempts:8 score:8
3. SCALD attempts:3 score:3
4. STEED attempts:9 score:9

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1481 🥳 score:60 ⏱️ 0:03:32.457414

📜 1 sessions

Octordle Classic

1. ANGRY attempts:4 score:4
2. THINK attempts:9 score:9
3. RUMOR attempts:5 score:5
4. LOWER attempts:11 score:11
5. GOLEM attempts:6 score:6
6. GRAFT attempts:7 score:7
7. OLIVE attempts:8 score:8
8. AFOUL attempts:10 score:10

# [squareword.org](squareword.org) 🧩 #1474 🥳 10 ⏱️ 0:05:31.330841

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟨 🟨
    🟨 🟩 🟩 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T A R K
    T E N O N
    A M I G O
    S P O U T
    H O N E S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1411 🥳 233 ⏱️ 0:02:07.577166

🤔 234 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 33 chat prompts
🤖 33 dolphin3:latest replies
😱   1 🔥   2 🥵  13 😎  29 🥶 175 🧊  13

      $1 #234 kit            100.00°C 🥳 1000‰ ~221 used:0  [220]  source:dolphin3
      $2  #20 waterproof      46.33°C 😱  999‰   ~2 used:50 [1]    source:dolphin3
      $3 #217 adapter         44.98°C 🔥  998‰   ~3 used:5  [2]    source:dolphin3
      $4 #205 charger         41.40°C 🔥  990‰   ~1 used:4  [0]    source:dolphin3
      $5 #139 carabiner       40.50°C 🥵  987‰  ~14 used:4  [13]   source:dolphin3
      $6 #115 duffel          38.66°C 🥵  980‰  ~15 used:7  [14]   source:dolphin3
      $7  #46 backpack        38.42°C 🥵  976‰  ~16 used:7  [15]   source:dolphin3
      $8 #100 rainproof       38.37°C 🥵  975‰  ~10 used:2  [9]    source:dolphin3
      $9  #80 pouch           37.71°C 🥵  968‰  ~13 used:3  [12]   source:dolphin3
     $10  #14 gear            37.12°C 🥵  959‰  ~11 used:2  [10]   source:dolphin3
     $11 #202 duffle          36.14°C 🥵  948‰   ~4 used:1  [3]    source:dolphin3
     $18 #219 converter       32.88°C 😎  866‰  ~17 used:0  [16]   source:dolphin3
     $47  #79 pocket          24.00°C 🥶        ~46 used:0  [45]   source:dolphin3
    $222  #67 tight           -0.26°C 🧊       ~222 used:0  [221]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1444 🥳 128 ⏱️ 0:01:28.609704

🤔 129 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 24 chat prompts
🤖 24 dolphin3:latest replies
😱  1 🥵  3 😎 25 🥶 90 🧊  9

      $1 #129 terreur          100.00°C 🥳 1000‰ ~120 used:0  [119]  source:dolphin3
      $2 #126 effroi            54.94°C 😱  999‰   ~1 used:0  [0]    source:dolphin3
      $3 #124 épouvante         48.20°C 🔥  990‰   ~2 used:0  [1]    source:dolphin3
      $4  #98 dévastation       41.18°C 🥵  933‰  ~23 used:11 [22]   source:dolphin3
      $5  #60 désolation        39.95°C 🥵  904‰  ~24 used:15 [23]   source:dolphin3
      $6  #99 anéantissement    39.12°C 😎  883‰  ~28 used:4  [27]   source:dolphin3
      $7  #76 angoisse          38.59°C 😎  870‰  ~27 used:3  [26]   source:dolphin3
      $8  #75 abjection         38.49°C 😎  867‰  ~29 used:4  [28]   source:dolphin3
      $9 #119 extermination     37.10°C 😎  836‰   ~3 used:0  [2]    source:dolphin3
     $10  #35 désespoir         36.03°C 😎  800‰  ~25 used:2  [24]   source:dolphin3
     $11  #88 accablement       36.02°C 😎  799‰   ~4 used:1  [3]    source:dolphin3
     $12  #91 démoralisation    35.11°C 😎  755‰   ~5 used:1  [4]    source:dolphin3
     $31 #115 hécatombe         27.56°C 🥶        ~34 used:0  [33]   source:dolphin3
    $121   #5 jardin            -0.22°C 🧊       ~121 used:0  [120]  source:dolphin3

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #95 🥳 score:25 ⏱️ 0:01:32.299400

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. NEVER attempts:8 score:8
2. STAVE attempts:7 score:7
3. LOUSE attempts:4 score:4
4. QUALM attempts:6 score:6
