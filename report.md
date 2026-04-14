# 2026-04-15

- 🔗 spaceword.org 🧩 2026-04-14 🏁 score 2173 ranked 9.7% 34/350 ⏱️ 0:58:44.972173
- 🔗 alfagok.diginaut.net 🧩 #529 🥳 36 ⏱️ 0:00:38.816912
- 🔗 alphaguess.com 🧩 #996 🥳 38 ⏱️ 0:00:34.870397
- 🔗 dontwordle.com 🧩 #1422 🥳 6 ⏱️ 0:01:55.896569
- 🔗 dictionary.com hurdle 🧩 #1565 🥳 22 ⏱️ 0:03:29.921839
- 🔗 Quordle Classic 🧩 #1542 🥳 score:22 ⏱️ 0:01:31.352696
- 🔗 Octordle Classic 🧩 #1542 🥳 score:60 ⏱️ 0:03:45.904214
- 🔗 squareword.org 🧩 #1535 🥳 8 ⏱️ 0:02:24.649260
- 🔗 cemantle.certitudes.org 🧩 #1472 🥳 78 ⏱️ 0:10:31.770673
- 🔗 cemantix.certitudes.org 🧩 #1505 🥳 39 ⏱️ 0:00:41.592910

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













































# [spaceword.org](spaceword.org) 🧩 2026-04-14 🏁 score 2173 ranked 9.7% 34/350 ⏱️ 0:58:44.972173

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 34/350

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ L E V _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ _ _ E M _ _ _   
      _ _ _ _ _ L I _ _ _   
      _ _ _ _ J E T _ _ _   
      _ _ _ _ _ G O _ _ _   
      _ _ _ _ G I _ _ _ _   
      _ _ _ _ A S K _ _ _   
      _ _ _ _ S E A _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #529 🥳 36 ⏱️ 0:00:38.816912

🤔 36 attempts
📜 1 sessions

    @       [    0] &-teken       
    @+49841 [49841] boks          q8  ? ␅
    @+49841 [49841] boks          q9  ? after
    @+62280 [62280] cement        q12 ? ␅
    @+62280 [62280] cement        q13 ? after
    @+65388 [65388] coat          q16 ? ␅
    @+65388 [65388] coat          q17 ? after
    @+66940 [66940] complet       q18 ? ␅
    @+66940 [66940] complet       q19 ? after
    @+67694 [67694] concert       q20 ? ␅
    @+67694 [67694] concert       q21 ? after
    @+67793 [67793] concertzaal   q26 ? ␅
    @+67793 [67793] concertzaal   q27 ? after
    @+67841 [67841] concipieer    q28 ? ␅
    @+67841 [67841] concipieer    q29 ? after
    @+67865 [67865] concordantie  q30 ? ␅
    @+67865 [67865] concordantie  q31 ? after
    @+67876 [67876] concours      q32 ? ␅
    @+67876 [67876] concours      q33 ? after
    @+67884 [67884] concreet      q34 ? ␅
    @+67884 [67884] concreet      q35 ? it
    @+67884 [67884] concreet      done. it
    @+67895 [67895] concretiseren q24 ? ␅
    @+67895 [67895] concretiseren q25 ? before
    @+68101 [68101] conductor     q22 ? ␅
    @+68101 [68101] conductor     q23 ? before
    @+68514 [68514] connectie     q14 ? ␅
    @+68514 [68514] connectie     q15 ? before
    @+74754 [74754] dc            q10 ? ␅
    @+74754 [74754] dc            q11 ? before
    @+99737 [99737] ex            q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #996 🥳 38 ⏱️ 0:00:34.870397

🤔 38 attempts
📜 1 sessions

    @       [    0] aa        
    @+47380 [47380] dis       q6  ? ␅
    @+47380 [47380] dis       q7  ? after
    @+72798 [72798] gremmy    q8  ? ␅
    @+72798 [72798] gremmy    q9  ? after
    @+85502 [85502] ins       q10 ? ␅
    @+85502 [85502] ins       q11 ? after
    @+91846 [91846] knot      q12 ? ␅
    @+91846 [91846] knot      q13 ? after
    @+92423 [92423] lac       q18 ? ␅
    @+92423 [92423] lac       q19 ? after
    @+92799 [92799] lam       q20 ? ␅
    @+92799 [92799] lam       q21 ? after
    @+92998 [92998] land      q22 ? ␅
    @+92998 [92998] land      q23 ? after
    @+93094 [93094] lang      q24 ? ␅
    @+93094 [93094] lang      q25 ? after
    @+93180 [93180] lantern   q26 ? ␅
    @+93180 [93180] lantern   q27 ? after
    @+93199 [93199] lap       q28 ? ␅
    @+93199 [93199] lap       q29 ? after
    @+93233 [93233] lapilli   q30 ? ␅
    @+93233 [93233] lapilli   q31 ? after
    @+93248 [93248] laps      q32 ? ␅
    @+93248 [93248] laps      q33 ? after
    @+93257 [93257] lapstrake q34 ? ␅
    @+93257 [93257] lapstrake q35 ? after
    @+93262 [93262] laptop    q36 ? ␅
    @+93262 [93262] laptop    q37 ? it
    @+93262 [93262] laptop    done. it
    @+93266 [93266] lar       q17 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1422 🥳 6 ⏱️ 0:01:55.896569

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:PEWEE n n n n n remain:5634
    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:2917
    ⬜⬜⬜⬜⬜ tried:BUBUS n n n n n remain:681
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:265
    ⬜🟩⬜⬜⬜ tried:FORTH n Y n n n remain:21
    🟨🟩⬜⬜⬜ tried:GONZO m Y n n n remain:1

    Undos used: 5

      1 words remaining
    x 6 unused letters
    = 6 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1565 🥳 22 ⏱️ 0:03:29.921839

📜 1 sessions
💰 score: 9400

    5/6
    SERAL ⬜⬜⬜⬜🟨
    OCULI 🟨⬜⬜🟩⬜
    GODLY ⬜🟩⬜🟩🟩
    JOWLY 🟩🟩⬜🟩🟩
    JOLLY 🟩🟩🟩🟩🟩
    5/6
    JOLLY ⬜⬜⬜⬜🟩
    STRAY ⬜⬜⬜⬜🟩
    PINEY 🟨🟩⬜⬜🟩
    GIMPY ⬜🟩🟩🟩🟩
    WIMPY 🟩🟩🟩🟩🟩
    4/6
    WIMPY ⬜⬜⬜⬜⬜
    SONAR 🟩🟨🟨⬜🟨
    SCORN 🟩⬜🟩🟩🟩
    SHORN 🟩🟩🟩🟩🟩
    6/6
    SHORN 🟩⬜⬜🟨⬜
    SAYER 🟩⬜⬜🟩🟩
    SPIER 🟩⬜⬜🟩🟩
    SUBER 🟩⬜⬜🟩🟩
    SEWER 🟩🟩⬜🟩🟩
    SEVER 🟩🟩🟩🟩🟩
    Final 2/2
    DELAY ⬜🟩🟩🟩🟩
    BELAY 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1542 🥳 score:22 ⏱️ 0:01:31.352696

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. PIVOT attempts:6 score:6
2. ELECT attempts:4 score:4
3. STORE attempts:5 score:5
4. CREME attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1542 🥳 score:60 ⏱️ 0:03:45.904214

📜 2 sessions

Octordle Classic

1. FROND attempts:8 score:8
2. FJORD attempts:7 score:7
3. BEGAN attempts:11 score:11
4. BLOND attempts:9 score:9
5. AUGUR attempts:5 score:5
6. BUDDY attempts:10 score:10
7. SUGAR attempts:4 score:4
8. TORUS attempts:6 score:6

# [squareword.org](squareword.org) 🧩 #1535 🥳 8 ⏱️ 0:02:24.649260

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟩 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C A V E D
    O P E R A
    M A N O R
    P R U D E
    S T E E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1472 🥳 78 ⏱️ 0:10:31.770673

🤔 79 attempts
📜 1 sessions
🫧 12 chat sessions
⁉️ 18 chat prompts
🤖 8 dolphin3:latest replies
🤖 10 gemma4:26b replies
😱  1 😎 10 🥶 65 🧊  2

     $1 #79 nut          100.00°C 🥳 1000‰ ~77 used:0  [76]  source:dolphin3
     $2 #62 nuts          64.88°C 😱  999‰  ~1 used:3  [0]   source:dolphin3
     $3 #77 locknut       33.00°C 😎  865‰  ~2 used:0  [1]   source:dolphin3
     $4 #56 fastener      32.35°C 😎  836‰  ~3 used:1  [2]   source:dolphin3
     $5 #50 bolt          30.78°C 😎  729‰  ~4 used:1  [3]   source:dolphin3
     $6 #44 rivet         29.44°C 😎  582‰ ~10 used:2  [9]   source:dolphin3
     $7 #52 chewing       28.41°C 😎  394‰  ~5 used:1  [4]   source:dolphin3
     $8 #27 slicer        27.47°C 😎  228‰ ~11 used:3  [10]  source:dolphin3
     $9 #58 gum           27.45°C 😎  221‰  ~6 used:0  [5]   source:dolphin3
    $10 #43 reamer        27.24°C 😎  176‰  ~7 used:1  [6]   source:dolphin3
    $11 #47 snip          27.17°C 😎  157‰  ~8 used:1  [7]   source:dolphin3
    $12 #72 cutter        26.79°C 😎   70‰  ~9 used:0  [8]   source:dolphin3
    $13 #57 grommet       26.48°C 🥶       ~14 used:0  [13]  source:dolphin3
    $78  #6 orbit         -1.92°C 🧊       ~78 used:0  [77]  source:gemma4  

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1505 🥳 39 ⏱️ 0:00:41.592910

🤔 40 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 10 chat prompts
🤖 10 dolphin3:latest replies
🥵  3 😎  7 🥶 19 🧊 10

     $1 #40 échéance         100.00°C 🥳 1000‰ ~30 used:0 [29]  source:dolphin3
     $2 #12 mois              40.67°C 🥵  976‰  ~3 used:7 [2]   source:dolphin3
     $3 #17 date              40.06°C 🥵  970‰  ~2 used:5 [1]   source:dolphin3
     $4 #16 calendrier        36.96°C 🥵  945‰  ~1 used:3 [0]   source:dolphin3
     $5 #11 année             28.83°C 😎  762‰  ~4 used:0 [3]   source:dolphin3
     $6 #29 trimestre         28.51°C 😎  744‰  ~5 used:0 [4]   source:dolphin3
     $7 #20 lunaison          24.94°C 😎  505‰  ~6 used:0 [5]   source:dolphin3
     $8 #23 rentrée           23.35°C 😎  323‰  ~7 used:0 [6]   source:dolphin3
     $9 #26 mensuel           22.59°C 😎  233‰  ~8 used:0 [7]   source:dolphin3
    $10  #5 jour              22.16°C 😎  189‰  ~9 used:1 [8]   source:dolphin3
    $11 #38 planning          21.54°C 😎  102‰ ~10 used:0 [9]   source:dolphin3
    $12 #14 semaine           20.14°C 🥶       ~11 used:0 [10]  source:dolphin3
    $13 #19 heure             19.75°C 🥶       ~12 used:0 [11]  source:dolphin3
    $31 #13 dimanche          -0.98°C 🧊       ~31 used:0 [30]  source:dolphin3
