# 2026-01-28

- 🔗 spaceword.org 🧩 2026-01-27 🏁 score 2170 ranked 25.2% 84/333 ⏱️ 4:03:10.357927
- 🔗 alfagok.diginaut.net 🧩 #452 🥳 30 ⏱️ 0:00:43.055668
- 🔗 alphaguess.com 🧩 #919 🥳 30 ⏱️ 0:00:32.407870
- 🔗 dontwordle.com 🧩 #1345 😳 6 ⏱️ 0:04:09.719032
- 🔗 dictionary.com hurdle 🧩 #1488 🥳 19 ⏱️ 0:03:19.880746
- 🔗 Quordle Classic 🧩 #1465 🥳 score:20 ⏱️ 0:01:16.304750
- 🔗 Octordle Classic 🧩 #1465 🥳 score:62 ⏱️ 0:04:08.177870
- 🔗 squareword.org 🧩 #1458 🥳 10 ⏱️ 0:02:38.354916
- 🔗 cemantle.certitudes.org 🧩 #1395 🥳 145 ⏱️ 0:11:19.916214
- 🔗 cemantix.certitudes.org 🧩 #1428 🥳 82 ⏱️ 0:10:26.393775
- 🔗 Quordle Rescue 🧩 #79 😦 score:29 ⏱️ 0:01:56.535723
- 🔗 Octordle Rescue 🧩 #1465 😦 score:7 ⏱️ 0:03:51.432575

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













# [spaceword.org](spaceword.org) 🧩 2026-01-27 🏁 score 2170 ranked 25.2% 84/333 ⏱️ 4:03:10.357927

📜 6 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 84/333

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ P _ S E Q U O I A   
      K U F I _ _ _ H _ L   
      _ R E N V O I _ _ T   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #452 🥳 30 ⏱️ 0:00:43.055668

🤔 30 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+199833 [199833] lijm        q0  ? ␅
    @+199833 [199833] lijm        q1  ? after
    @+299738 [299738] schub       q2  ? ␅
    @+299738 [299738] schub       q3  ? after
    @+324308 [324308] sub         q6  ? ␅
    @+324308 [324308] sub         q7  ? after
    @+336905 [336905] toetsing    q8  ? ␅
    @+336905 [336905] toetsing    q9  ? after
    @+336943 [336943] toetsscores q24 ? ␅
    @+336943 [336943] toetsscores q25 ? after
    @+336957 [336957] toeval      q26 ? ␅
    @+336957 [336957] toeval      q27 ? after
    @+336960 [336960] toevallig   q28 ? ␅
    @+336960 [336960] toevallig   q29 ? it
    @+336960 [336960] toevallig   done. it
    @+336981 [336981] toeven      q22 ? ␅
    @+336981 [336981] toeven      q23 ? before
    @+337059 [337059] toewenden   q20 ? ␅
    @+337059 [337059] toewenden   q21 ? before
    @+337213 [337213] toilet      q18 ? ␅
    @+337213 [337213] toilet      q19 ? before
    @+337562 [337562] toneel      q16 ? ␅
    @+337562 [337562] toneel      q17 ? before
    @+338395 [338395] topt        q14 ? ␅
    @+338395 [338395] topt        q15 ? before
    @+339896 [339896] transport   q12 ? ␅
    @+339896 [339896] transport   q13 ? before
    @+343095 [343095] tv          q10 ? ␅
    @+343095 [343095] tv          q11 ? before
    @+349512 [349512] vakantie    q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #919 🥳 30 ⏱️ 0:00:32.407870

🤔 30 attempts
📜 1 sessions

    @       [    0] aa         
    @+23683 [23683] camp       q4  ? ␅
    @+23683 [23683] camp       q5  ? after
    @+35526 [35526] convention q6  ? ␅
    @+35526 [35526] convention q7  ? after
    @+38185 [38185] crazy      q10 ? ␅
    @+38185 [38185] crazy      q11 ? after
    @+38502 [38502] crew       q16 ? ␅
    @+38502 [38502] crew       q17 ? after
    @+38537 [38537] crick      q22 ? ␅
    @+38537 [38537] crick      q23 ? after
    @+38539 [38539] cricket    q28 ? ␅
    @+38539 [38539] cricket    q29 ? it
    @+38539 [38539] cricket    done. it
    @+38548 [38548] cricoid    q26 ? ␅
    @+38548 [38548] cricoid    q27 ? before
    @+38558 [38558] criminal   q24 ? ␅
    @+38558 [38558] criminal   q25 ? before
    @+38583 [38583] crimine    q20 ? ␅
    @+38583 [38583] crimine    q21 ? before
    @+38664 [38664] crisp      q18 ? ␅
    @+38664 [38664] crisp      q19 ? before
    @+38837 [38837] crop       q14 ? ␅
    @+38837 [38837] crop       q15 ? before
    @+39503 [39503] cud        q12 ? ␅
    @+39503 [39503] cud        q13 ? before
    @+40842 [40842] da         q8  ? ␅
    @+40842 [40842] da         q9  ? before
    @+47382 [47382] dis        q2  ? ␅
    @+47382 [47382] dis        q3  ? before
    @+98220 [98220] mach       q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1345 😳 6 ⏱️ 0:04:09.719032

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:YAPPY n n n n n remain:5357
    ⬜⬜⬜⬜⬜ tried:MORRO n n n n n remain:1792
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:629
    ⬜⬜🟨⬜⬜ tried:BLUFF n n m n n remain:80
    ⬜🟨⬜⬜⬜ tried:HUNCH n m n n n remain:4
    🟩🟩🟩🟩🟩 tried:SEGUE Y Y Y Y Y remain:0

    Undos used: 4

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1488 🥳 19 ⏱️ 0:03:19.880746

📜 1 sessions
💰 score: 9700

    5/6
    EARNS ⬜⬜🟩⬜🟨
    SIRUP 🟩⬜🟩🟩⬜
    SCRUB 🟩⬜🟩🟩⬜
    SHRUG 🟩⬜🟩🟩⬜
    STRUT 🟩🟩🟩🟩🟩
    4/6
    STRUT ⬜⬜⬜⬜⬜
    ANODE 🟨⬜⬜🟨⬜
    DAILY 🟨🟨🟨🟨⬜
    PLAID 🟩🟩🟩🟩🟩
    4/6
    PLAID ⬜⬜⬜🟨⬜
    TIERS ⬜🟨⬜🟨⬜
    INCUR 🟨🟨⬜🟨🟨
    RUING 🟩🟩🟩🟩🟩
    4/6
    RUING ⬜⬜⬜⬜⬜
    SOLVE 🟨🟨⬜⬜⬜
    OATHS 🟨🟨🟨⬜🟨
    ASCOT 🟩🟩🟩🟩🟩
    Final 2/2
    BALES ⬜🟩🟩🟨🟨
    FALSE 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1465 🥳 score:20 ⏱️ 0:01:16.304750

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. INGOT attempts:3 score:3
2. IGLOO attempts:4 score:4
3. GONER attempts:5 score:5
4. FLAKE attempts:8 score:8

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1465 🥳 score:62 ⏱️ 0:04:08.177870

📜 2 sessions

Octordle Classic

1. JIFFY attempts:11 score:11
2. AORTA attempts:3 score:3
3. HAZEL attempts:4 score:4
4. CROWN attempts:9 score:9
5. BILLY attempts:12 score:12
6. PETAL attempts:7 score:7
7. WREAK attempts:10 score:10
8. SPINY attempts:6 score:6

# [squareword.org](squareword.org) 🧩 #1458 🥳 10 ⏱️ 0:02:38.354916

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    G R A F T
    R O W E R
    A G A T E
    P U R E E
    H E E D S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1395 🥳 145 ⏱️ 0:11:19.916214

🤔 146 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 24 chat prompts
🤖 1 nemotron-3-nano:latest replies
🤖 3 dolphin3:latest replies
🤖 19 lfm2.5-thinking:latest replies
🔥   1 🥵   7 😎  14 🥶 112 🧊  11

      $1 #146   ~1 transparency   100.00°C 🥳 1000‰
      $2  #99  ~14 clarity         55.60°C 🔥  995‰
      $3 #141   ~3 honesty         48.07°C 🥵  982‰
      $4 #100  ~13 consistency     44.95°C 🥵  976‰
      $5 #105  ~11 stability       43.20°C 🥵  970‰
      $6 #145   ~2 opacity         41.61°C 🥵  966‰
      $7 #128   ~9 coherence       40.95°C 🥵  959‰
      $8  #98  ~15 adherence       38.55°C 🥵  940‰
      $9 #104  ~12 simplicity      37.61°C 🥵  928‰
     $10  #75  ~19 reliability     35.45°C 😎  899‰
     $11  #97  ~16 accuracy        34.96°C 😎  886‰
     $12  #71  ~23 certainty       34.08°C 😎  864‰
     $24 #129      conciseness     23.53°C 🥶
    $136   #1      apple           -0.62°C 🧊

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1428 🥳 82 ⏱️ 0:10:26.393775

🤔 83 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 12 chat prompts
🤖 12 nemotron-3-nano:latest replies
🔥  1 🥵  5 😎 15 🥶 55 🧊  6

     $1 #83  ~1 prince          100.00°C 🥳 1000‰
     $2 #72  ~9 souverain        54.93°C 🔥  995‰
     $3 #75  ~6 courtisan        49.24°C 🥵  986‰
     $4 #60 ~11 majesté          45.06°C 🥵  975‰
     $5 #28 ~16 galanterie       40.19°C 🥵  929‰
     $6 #53 ~13 noblesse         40.19°C 🥵  928‰
     $7 #81  ~3 magnanime        40.01°C 🥵  924‰
     $8 #77  ~5 dynastie         38.53°C 😎  898‰
     $9 #12 ~22 chevalier        37.04°C 😎  867‰
    $10 #56 ~12 aristocratie     36.94°C 😎  863‰
    $11 #80  ~4 impérial         36.91°C 😎  862‰
    $12 #62 ~10 auguste          36.74°C 😎  856‰
    $23 #24     bravoure         26.65°C 🥶
    $78 #66     gravité          -0.42°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #79 😦 score:29 ⏱️ 0:01:56.535723

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. DRUNK attempts:7 score:7
2. HAPPY attempts:5 score:5
3. INANE attempts:8 score:8
4. _AKER -BCDGHILNOPSTUWY attempts:9 score:-1

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1465 😦 score:7 ⏱️ 0:03:51.432575

📜 1 sessions

Octordle Rescue

1. GUESS attempts:5 score:5
2. BUDDY attempts:11 score:11
3. TIMER attempts:6 score:6
4. ALOUD attempts:7 score:7
5. CURVY attempts:10 score:10
6. ANGRY attempts:9 score:9
7. _AGER -BCDFHILMNOPSTUVWY attempts:13 score:-1
8. DENSE attempts:8 score:8
