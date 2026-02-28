# 2026-03-01

- 🔗 spaceword.org 🧩 2026-02-28 🏁 score 2170 ranked 33.7% 105/312 ⏱️ 0:33:08.424982
- 🔗 alfagok.diginaut.net 🧩 #484 🥳 24 ⏱️ 0:00:28.534927
- 🔗 alphaguess.com 🧩 #951 🥳 26 ⏱️ 0:00:34.863353
- 🔗 dontwordle.com 🧩 #1377 🥳 6 ⏱️ 0:01:54.598951
- 🔗 dictionary.com hurdle 🧩 #1520 🥳 18 ⏱️ 0:03:36.000766
- 🔗 Quordle Classic 🧩 #1497 🥳 score:22 ⏱️ 0:01:07.663865
- 🔗 Octordle Classic 🧩 #1497 🥳 score:65 ⏱️ 0:03:52.801353
- 🔗 squareword.org 🧩 #1490 🥳 10 ⏱️ 0:02:45.583112
- 🔗 cemantle.certitudes.org 🧩 #1427 🥳 195 ⏱️ 0:03:51.206573
- 🔗 cemantix.certitudes.org 🧩 #1460 🥳 481 ⏱️ 0:10:13.742608

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











# [spaceword.org](spaceword.org) 🧩 2026-02-28 🏁 score 2170 ranked 33.7% 105/312 ⏱️ 0:33:08.424982

📜 2 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 105/312

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ J _ C _ _   
      _ _ _ O B E _ O _ _   
      _ _ _ D A W _ Z _ _   
      _ _ _ _ R E _ I _ _   
      _ _ _ A G L E E _ _   
      _ _ _ R E S _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #484 🥳 24 ⏱️ 0:00:28.534927

🤔 24 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199814 [199814] lijm      q0  ? ␅
    @+199814 [199814] lijm      q1  ? after
    @+299707 [299707] schub     q2  ? ␅
    @+299707 [299707] schub     q3  ? after
    @+349475 [349475] vakantie  q4  ? ␅
    @+349475 [349475] vakantie  q5  ? after
    @+374216 [374216] vrij      q6  ? ␅
    @+374216 [374216] vrij      q7  ? after
    @+380428 [380428] weer      q10 ? ␅
    @+380428 [380428] weer      q11 ? after
    @+383404 [383404] werk      q12 ? ␅
    @+383404 [383404] werk      q13 ? after
    @+385076 [385076] whatsapp  q14 ? ␅
    @+385076 [385076] whatsapp  q15 ? after
    @+385614 [385614] wij       q16 ? ␅
    @+385614 [385614] wij       q17 ? after
    @+385634 [385634] wijd      q22 ? ␅
    @+385634 [385634] wijd      q23 ? it
    @+385634 [385634] wijd      done. it
    @+385728 [385728] wijk      q20 ? ␅
    @+385728 [385728] wijk      q21 ? before
    @+385931 [385931] wijn      q18 ? ␅
    @+385931 [385931] wijn      q19 ? before
    @+386757 [386757] wind      q8  ? ␅
    @+386757 [386757] wind      q9  ? before

# [alphaguess.com](alphaguess.com) 🧩 #951 🥳 26 ⏱️ 0:00:34.863353

🤔 26 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+5876  [ 5876] angel      q8  ? ␅
    @+5876  [ 5876] angel      q9  ? after
    @+6632  [ 6632] anti       q12 ? ␅
    @+6632  [ 6632] anti       q13 ? after
    @+7465  [ 7465] any        q14 ? ␅
    @+7465  [ 7465] any        q15 ? after
    @+7883  [ 7883] app        q16 ? ␅
    @+7883  [ 7883] app        q17 ? after
    @+7989  [ 7989] appetences q20 ? ␅
    @+7989  [ 7989] appetences q21 ? after
    @+8014  [ 8014] apple      q24 ? ␅
    @+8014  [ 8014] apple      q25 ? it
    @+8014  [ 8014] apple      done. it
    @+8042  [ 8042] applier    q22 ? ␅
    @+8042  [ 8042] applier    q23 ? before
    @+8094  [ 8094] appraise   q18 ? ␅
    @+8094  [ 8094] appraise   q19 ? before
    @+8323  [ 8323] ar         q10 ? ␅
    @+8323  [ 8323] ar         q11 ? before
    @+11764 [11764] back       q6  ? ␅
    @+11764 [11764] back       q7  ? before
    @+23682 [23682] camp       q4  ? ␅
    @+23682 [23682] camp       q5  ? before
    @+47381 [47381] dis        q2  ? ␅
    @+47381 [47381] dis        q3  ? before
    @+98218 [98218] mach       q0  ? ␅
    @+98218 [98218] mach       q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1377 🥳 6 ⏱️ 0:01:54.598951

📜 2 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:TEETH n n n n n remain:4651
    ⬜⬜⬜⬜⬜ tried:DOGGO n n n n n remain:1966
    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:874
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:389
    ⬜🟩⬜⬜⬜ tried:BUBUS n Y n n n remain:14
    🟩🟩🟩⬜⬜ tried:QUAFF Y Y Y n n remain:1

    Undos used: 4

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1520 🥳 18 ⏱️ 0:03:36.000766

📜 1 sessions
💰 score: 9800

    5/6
    AIDES ⬜⬜⬜🟨⬜
    WHORE ⬜⬜🟩⬜🟩
    GNOME ⬜🟨🟩⬜🟩
    CLONE ⬜⬜🟩🟩🟩
    OZONE 🟩🟩🟩🟩🟩
    4/6
    OZONE 🟨⬜🟨⬜⬜
    SOAPY ⬜🟩⬜🟨⬜
    TOPIC ⬜🟩🟨🟩⬜
    POLIO 🟩🟩🟩🟩🟩
    4/6
    POLIO 🟩⬜🟨⬜⬜
    PENAL 🟩🟩⬜🟩🟩
    PEDAL 🟩🟩⬜🟩🟩
    PETAL 🟩🟩🟩🟩🟩
    3/6
    PETAL ⬜🟩🟨🟨⬜
    TEARS 🟩🟩🟨🟩⬜
    TERRA 🟩🟩🟩🟩🟩
    Final 2/2
    KNOWS 🟩🟩🟩🟩⬜
    KNOWN 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1497 🥳 score:22 ⏱️ 0:01:07.663865

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. NERDY attempts:5 score:5
2. ADEPT attempts:6 score:6
3. PRIMO attempts:7 score:7
4. HUMID attempts:4 score:4

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1497 🥳 score:65 ⏱️ 0:03:52.801353

📜 1 sessions

Octordle Classic

1. TITHE attempts:13 score:13
2. GHOUL attempts:7 score:7
3. HONOR attempts:6 score:6
4. INANE attempts:4 score:4
5. EXERT attempts:10 score:10
6. BRAKE attempts:12 score:12
7. QUEEN attempts:5 score:5
8. FLOUT attempts:8 score:8

# [squareword.org](squareword.org) 🧩 #1490 🥳 10 ⏱️ 0:02:45.583112

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟩 🟨
    🟨 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C L A P S
    Z E B R A
    A V O I D
    R E V E L
    S E E D Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1427 🥳 195 ⏱️ 0:03:51.206573

🤔 196 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 34 chat prompts
🤖 34 dolphin3:latest replies
😱   1 🔥   1 🥵   2 😎  15 🥶 162 🧊  14

      $1 #196 hurricane     100.00°C 🥳 1000‰ ~182 used:0  [181]  source:dolphin3
      $2 #189 storm          73.22°C 😱  999‰   ~1 used:2  [0]    source:dolphin3
      $3 #194 flood          47.89°C 🔥  991‰   ~2 used:0  [1]    source:dolphin3
      $4 #190 blizzard       40.84°C 🥵  978‰   ~3 used:0  [2]    source:dolphin3
      $5 #180 weather        33.92°C 🥵  961‰   ~4 used:4  [3]    source:dolphin3
      $6 #191 downpour       27.45°C 😎  893‰   ~5 used:0  [4]    source:dolphin3
      $7 #188 rain           27.06°C 😎  887‰   ~6 used:1  [5]    source:dolphin3
      $8 #193 drought        25.15°C 😎  836‰   ~7 used:0  [6]    source:dolphin3
      $9 #185 forecast       24.97°C 😎  830‰   ~8 used:0  [7]    source:dolphin3
     $10  #17 bird           23.73°C 😎  789‰  ~19 used:30 [18]   source:dolphin3
     $11 #176 forecasting    22.75°C 😎  742‰   ~9 used:1  [8]    source:dolphin3
     $12 #187 humidity       22.51°C 😎  727‰  ~10 used:0  [9]    source:dolphin3
     $21 #137 mammal         16.85°C 🥶        ~23 used:0  [22]   source:dolphin3
    $183  #94 buzzer         -0.07°C 🧊       ~183 used:0  [182]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1460 🥳 481 ⏱️ 0:10:13.742608

🤔 482 attempts
📜 1 sessions
🫧 25 chat sessions
⁉️ 128 chat prompts
🤖 128 dolphin3:latest replies
🔥   3 🥵  27 😎 104 🥶 294 🧊  53

      $1 #482 paragraphe         100.00°C 🥳 1000‰ ~429 used:0   [428]  source:dolphin3
      $2 #190 énoncer             50.01°C 🔥  997‰ ~129 used:106 [128]  source:dolphin3
      $3 #438 chapitre            48.80°C 🔥  995‰   ~1 used:6   [0]    source:dolphin3
      $4 #437 article             45.70°C 🔥  993‰   ~2 used:7   [1]    source:dolphin3
      $5 #241 mentionner          44.96°C 🥵  989‰ ~133 used:41  [132]  source:dolphin3
      $6 #221 énumérer            44.25°C 🥵  988‰ ~131 used:23  [130]  source:dolphin3
      $7 #449 annexe              43.95°C 🥵  987‰   ~3 used:1   [2]    source:dolphin3
      $8 #184 définir             43.10°C 🥵  984‰  ~24 used:9   [23]   source:dolphin3
      $9 #209 spécifier           42.09°C 🥵  980‰  ~16 used:7   [15]   source:dolphin3
     $10 #167 expliciter          41.12°C 🥵  979‰  ~17 used:7   [16]   source:dolphin3
     $11 #336 énumération         40.89°C 🥵  978‰  ~11 used:6   [10]   source:dolphin3
     $32 #303 notification        33.01°C 😎  899‰  ~27 used:0   [26]   source:dolphin3
    $135 #187 rédiger             21.66°C 🥶       ~128 used:0   [127]  source:dolphin3
    $430 #268 feeling             -0.20°C 🧊       ~430 used:0   [429]  source:dolphin3
