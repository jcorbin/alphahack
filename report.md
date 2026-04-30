# 2026-05-01

- 🔗 spaceword.org 🧩 2026-04-30 🏁 score 2173 ranked 7.1% 24/336 ⏱️ 4:39:32.492732
- 🔗 alfagok.diginaut.net 🧩 #545 🥳 50 ⏱️ 0:01:00.104497
- 🔗 alphaguess.com 🧩 #1012 🥳 12 ⏱️ 0:00:22.727610
- 🔗 dontwordle.com 🧩 #1438 🥳 6 ⏱️ 0:01:27.200309
- 🔗 dictionary.com hurdle 🧩 #1581 🥳 17 ⏱️ 0:02:52.602385
- 🔗 Quordle Classic 🧩 #1558 🥳 score:22 ⏱️ 0:01:10.494873
- 🔗 Octordle Classic 🧩 #1558 🥳 score:60 ⏱️ 0:03:02.296428
- 🔗 squareword.org 🧩 #1551 🥳 8 ⏱️ 0:02:27.526397
- 🔗 cemantle.certitudes.org 🧩 #1488 🥳 282 ⏱️ 0:03:21.938191
- 🔗 cemantix.certitudes.org 🧩 #1521 🥳 155 ⏱️ 0:02:56.731555

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





























































# [spaceword.org](spaceword.org) 🧩 2026-04-30 🏁 score 2173 ranked 7.1% 24/336 ⏱️ 4:39:32.492732

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 24/336

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ F _ Q _ _ Z _ K A   
      _ O _ I G U A N I D   
      _ E A S I N G _ D O   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #545 🥳 50 ⏱️ 0:01:00.104497

🤔 50 attempts
📜 1 sessions

    @       [    0] &-teken         
    @+49840 [49840] boks            q4  ? ␅
    @+49840 [49840] boks            q5  ? after
    @+62279 [62279] cement          q8  ? ␅
    @+62279 [62279] cement          q9  ? after
    @+68513 [68513] connectie       q10 ? ␅
    @+68513 [68513] connectie       q11 ? after
    @+71584 [71584] cru             q12 ? ␅
    @+71584 [71584] cru             q13 ? az
    @+71584 [71584] cru             q14 ? ␅
    @+71584 [71584] cru             q15 ? after
    @+72874 [72874] dag             q16 ? ␅
    @+72874 [72874] dag             q17 ? after
    @+73582 [73582] dam             q18 ? ␅
    @+73582 [73582] dam             q19 ? after
    @+73981 [73981] dans            q20 ? ␅
    @+73981 [73981] dans            q21 ? after
    @+74124 [74124] dansopleidingen q24 ? ␅
    @+74124 [74124] dansopleidingen q25 ? after
    @+74192 [74192] danst           q26 ? ␅
    @+74192 [74192] danst           q27 ? after
    @+74229 [74229] danswedstrijd   q28 ? ␅
    @+74229 [74229] danswedstrijd   q29 ? after
    @+74249 [74249] dapper          q48 ? ␅
    @+74249 [74249] dapper          q49 ? it
    @+74249 [74249] dapper          done. it
    @+74257 [74257] dar             q22 ? ␅
    @+74257 [74257] dar             q23 ? before
    @+74744 [74744] dc              q6  ? ␅
    @+74744 [74744] dc              q7  ? before
    @+99727 [99727] ex              q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1012 🥳 12 ⏱️ 0:00:22.727610

🤔 12 attempts
📜 1 sessions

    @       [    0] aa     
    @+1     [    1] aah    
    @+2     [    2] aahed  
    @+3     [    3] aahing 
    @+47380 [47380] dis    q2  ? ␅
    @+47380 [47380] dis    q3  ? after
    @+60083 [60083] face   q6  ? ␅
    @+60083 [60083] face   q7  ? after
    @+63239 [63239] flag   q10 ? ␅
    @+63239 [63239] flag   q11 ? it
    @+63239 [63239] flag   done. it
    @+66439 [66439] french q8  ? ␅
    @+66439 [66439] french q9  ? before
    @+72798 [72798] gremmy q4  ? ␅
    @+72798 [72798] gremmy q5  ? before
    @+98216 [98216] mach   q0  ? ␅
    @+98216 [98216] mach   q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1438 🥳 6 ⏱️ 0:01:27.200309

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:8089
    ⬜⬜⬜⬜⬜ tried:OVOID n n n n n remain:2710
    ⬜⬜⬜⬜⬜ tried:CRUCK n n n n n remain:728
    ⬜⬜⬜⬜🟩 tried:PHPHT n n n n Y remain:32
    ⬜🟨⬜⬜🟩 tried:MANAT n m n n Y remain:3
    🟨🟨⬜🟨🟩 tried:ASSET m m n m Y remain:2

    Undos used: 3

      2 words remaining
    x 7 unused letters
    = 14 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1581 🥳 17 ⏱️ 0:02:52.602385

📜 1 sessions
💰 score: 9900

    6/6
    LOSER ⬜⬜🟨⬜⬜
    UNITS ⬜⬜⬜⬜🟨
    PSHAW ⬜🟨🟨🟨⬜
    CHASM ⬜🟩🟩🟨⬜
    SHADY 🟩🟩🟩⬜🟩
    SHAKY 🟩🟩🟩🟩🟩
    4/6
    SHAKY ⬜⬜⬜⬜⬜
    PRION ⬜🟨⬜🟨⬜
    DOTER ⬜🟩🟨🟨🟨
    FORTE 🟩🟩🟩🟩🟩
    2/6
    FORTE ⬜🟩🟩🟨⬜
    WORST 🟩🟩🟩🟩🟩
    4/6
    WORST ⬜⬜⬜⬜🟩
    LEANT ⬜⬜🟨🟩🟩
    PAINT ⬜🟩🟩🟩🟩
    FAINT 🟩🟩🟩🟩🟩
    Final 1/2
    OFFER 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1558 🥳 score:22 ⏱️ 0:01:10.494873

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. LUMEN attempts:3 score:3
2. LINEN attempts:4 score:4
3. GOING attempts:9 score:9
4. THANK attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1558 🥳 score:60 ⏱️ 0:03:02.296428

📜 2 sessions

Octordle Classic

1. JUICE attempts:6 score:6
2. WIDER attempts:7 score:7
3. SLICK attempts:9 score:9
4. COLOR attempts:10 score:10
5. GUMMY attempts:4 score:4
6. PUPIL attempts:11 score:11
7. ASKEW attempts:5 score:5
8. CHASE attempts:8 score:8

# [squareword.org](squareword.org) 🧩 #1551 🥳 8 ⏱️ 0:02:27.526397

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C R E E P
    H A L L O
    A D D E R
    N I E C E
    T O R T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1488 🥳 282 ⏱️ 0:03:21.938191

🤔 283 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 49 chat prompts
🤖 49 dolphin3:latest replies
😱   1 🔥   3 🥵  15 😎  49 🥶 210 🧊   4

      $1 #283 upward           100.00°C 🥳 1000‰ ~279 used:0  [278]  source:dolphin3
      $2 #197 downward          83.93°C 😱  999‰   ~2 used:24 [1]    source:dolphin3
      $3 #262 upwards           73.98°C 🔥  998‰   ~3 used:3  [2]    source:dolphin3
      $4 #198 downwards         69.64°C 🔥  997‰   ~4 used:10 [3]    source:dolphin3
      $5 #271 skyward           51.00°C 🔥  993‰   ~1 used:1  [0]    source:dolphin3
      $6 #153 eastward          46.39°C 🥵  989‰  ~18 used:7  [17]   source:dolphin3
      $7 #161 westward          45.77°C 🥵  987‰  ~17 used:5  [16]   source:dolphin3
      $8 #282 trajectory        42.17°C 🥵  980‰   ~5 used:0  [4]    source:dolphin3
      $9 #270 rising            39.65°C 🥵  973‰   ~6 used:0  [5]    source:dolphin3
     $10 #108 direction         39.10°C 🥵  969‰  ~19 used:9  [18]   source:dolphin3
     $11 #200 incline           38.62°C 🥵  965‰   ~7 used:0  [6]    source:dolphin3
     $21 #176 down              31.94°C 😎  890‰  ~20 used:0  [19]   source:dolphin3
     $70  #75 plume             21.75°C 🥶        ~72 used:1  [71]   source:dolphin3
    $280  #34 effusive          -0.73°C 🧊       ~280 used:0  [279]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1521 🥳 155 ⏱️ 0:02:56.731555

🤔 156 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 37 chat prompts
🤖 37 dolphin3:latest replies
🥵   7 😎  11 🥶 109 🧊  28

      $1 #156 enveloppe       100.00°C 🥳 1000‰ ~128 used:0  [127]  source:dolphin3
      $2 #149 expéditeur       32.98°C 🥵  972‰   ~5 used:3  [4]    source:dolphin3
      $3 #140 envoi            32.76°C 🥵  970‰   ~7 used:5  [6]    source:dolphin3
      $4 #129 colis            32.71°C 🥵  969‰   ~6 used:4  [5]    source:dolphin3
      $5 #133 expédier         30.94°C 🥵  963‰   ~1 used:1  [0]    source:dolphin3
      $6 #147 postal           30.64°C 🥵  961‰   ~3 used:2  [2]    source:dolphin3
      $7 #118 courrier         30.12°C 🥵  957‰   ~4 used:2  [3]    source:dolphin3
      $8 #143 paquet           29.91°C 🥵  952‰   ~2 used:0  [1]    source:dolphin3
      $9 #144 lettre           24.83°C 😎  831‰   ~8 used:0  [7]    source:dolphin3
     $10 #146 facture          24.79°C 😎  829‰   ~9 used:0  [8]    source:dolphin3
     $11 #136 réceptionner     22.50°C 😎  670‰  ~10 used:0  [9]    source:dolphin3
     $12  #78 poste            22.33°C 😎  653‰  ~17 used:6  [16]   source:dolphin3
     $20  #73 définitif        17.80°C 🥶        ~27 used:1  [26]   source:dolphin3
    $129 #114 stratégie        -0.11°C 🧊       ~129 used:0  [128]  source:dolphin3
