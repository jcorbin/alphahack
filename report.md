# 2026-02-12

- 🔗 spaceword.org 🧩 2026-02-11 🏁 score 2164 ranked 58.4% 211/361 ⏱️ 1:50:59.693817
- 🔗 alfagok.diginaut.net 🧩 #467 🥳 40 ⏱️ 0:00:42.623275
- 🔗 alphaguess.com 🧩 #934 🥳 22 ⏱️ 0:00:24.298335
- 🔗 dontwordle.com 🧩 #1360 🥳 6 ⏱️ 0:01:41.631587
- 🔗 dictionary.com hurdle 🧩 #1503 🥳 20 ⏱️ 0:03:40.128329
- 🔗 Quordle Classic 🧩 #1480 🥳 score:19 ⏱️ 0:01:20.584169
- 🔗 Octordle Classic 🧩 #1480 🥳 score:62 ⏱️ 0:04:01.887064
- 🔗 squareword.org 🧩 #1473 🥳 8 ⏱️ 0:02:57.254416
- 🔗 cemantle.certitudes.org 🧩 #1410 🥳 670 ⏱️ 0:12:35.264651
- 🔗 cemantix.certitudes.org 🧩 #1443 🥳 193 ⏱️ 0:03:49.429809
- 🔗 Quordle Rescue 🧩 #94 🥳 score:29 ⏱️ 0:02:51.776298

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




























# [spaceword.org](spaceword.org) 🧩 2026-02-11 🏁 score 2164 ranked 58.4% 211/361 ⏱️ 1:50:59.693817

📜 4 sessions
- tiles: 21/21
- score: 2164 bonus: +64
- rank: 211/361

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ S A U _ _ _   
      _ _ _ _ _ V _ _ _ _   
      _ _ _ _ D E F _ _ _   
      _ _ _ _ _ R E _ _ _   
      _ _ _ _ J A M _ _ _   
      _ _ _ _ _ G I _ _ _   
      _ _ _ _ W E N _ _ _   
      _ _ _ _ _ _ I _ _ _   
      _ _ _ _ L I E _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #467 🥳 40 ⏱️ 0:00:42.623275

🤔 40 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+199826 [199826] lijm      q0  ? ␅
    @+199826 [199826] lijm      q1  ? after
    @+299731 [299731] schub     q2  ? ␅
    @+299731 [299731] schub     q3  ? after
    @+349499 [349499] vakantie  q4  ? ␅
    @+349499 [349499] vakantie  q5  ? after
    @+374240 [374240] vrij      q6  ? ␅
    @+374240 [374240] vrij      q7  ? after
    @+386781 [386781] wind      q8  ? ␅
    @+386781 [386781] wind      q9  ? after
    @+393198 [393198] zelfmoord q10 ? ␅
    @+393198 [393198] zelfmoord q11 ? after
    @+396406 [396406] zone      q12 ? ␅
    @+396406 [396406] zone      q13 ? after
    @+397152 [397152] zout      q16 ? ␅
    @+397152 [397152] zout      q17 ? after
    @+397336 [397336] zuid      q18 ? ␅
    @+397336 [397336] zuid      q19 ? after
    @+397626 [397626] zuig      q20 ? ␅
    @+397626 [397626] zuig      q21 ? after
    @+397825 [397825] zuivering q22 ? ␅
    @+397825 [397825] zuivering q23 ? after
    @+397866 [397866] zul       q26 ? ␅
    @+397866 [397866] zul       q27 ? after
    @+397870 [397870] zulle     q32 ? ␅
    @+397870 [397870] zulle     q33 ? after
    @+397871 [397871] zullen    q38 ? ␅
    @+397871 [397871] zullen    q39 ? it
    @+397871 [397871] zullen    done. it
    @+397872 [397872] zullend   q37 ? before

# [alphaguess.com](alphaguess.com) 🧩 #934 🥳 22 ⏱️ 0:00:24.298335

🤔 22 attempts
📜 1 sessions

    @        [     0] aa      
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98219  [ 98219] mach    q0  ? ␅
    @+98219  [ 98219] mach    q1  ? after
    @+147375 [147375] rhumb   q2  ? ␅
    @+147375 [147375] rhumb   q3  ? after
    @+171640 [171640] ta      q4  ? ␅
    @+171640 [171640] ta      q5  ? after
    @+182005 [182005] un      q6  ? ␅
    @+182005 [182005] un      q7  ? after
    @+189267 [189267] vicar   q8  ? ␅
    @+189267 [189267] vicar   q9  ? after
    @+192871 [192871] whir    q10 ? ␅
    @+192871 [192871] whir    q11 ? after
    @+193487 [193487] win     q14 ? ␅
    @+193487 [193487] win     q15 ? after
    @+194067 [194067] wo      q16 ? ␅
    @+194067 [194067] wo      q17 ? after
    @+194268 [194268] wood    q18 ? ␅
    @+194268 [194268] wood    q19 ? after
    @+194481 [194481] word    q20 ? ␅
    @+194481 [194481] word    q21 ? it
    @+194481 [194481] word    done. it
    @+194696 [194696] worship q12 ? ␅
    @+194696 [194696] worship q13 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1360 🥳 6 ⏱️ 0:01:41.631587

📜 1 sessions
💰 score: 56

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:YUPPY n n n n n remain:7572
    ⬜⬜⬜⬜⬜ tried:KABAB n n n n n remain:3107
    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:1340
    ⬜⬜⬜⬜⬜ tried:TOOTH n n n n n remain:276
    ⬜🟩🟨⬜⬜ tried:DEEDS n Y m n n remain:29
    ⬜🟩⬜🟨⬜ tried:JEWEL n Y n m n remain:7

    Undos used: 3

      7 words remaining
    x 8 unused letters
    = 56 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1503 🥳 20 ⏱️ 0:03:40.128329

📜 3 sessions
💰 score: 9600

    5/6
    TASER ⬜⬜🟨🟨⬜
    SLIPE 🟩⬜⬜⬜🟩
    SMOKE 🟩⬜⬜⬜🟩
    SENSE 🟩🟩⬜⬜🟩
    SEGUE 🟩🟩🟩🟩🟩
    4/6
    SEGUE ⬜🟩⬜⬜⬜
    RELIC 🟩🟩⬜⬜⬜
    READY 🟩🟩⬜⬜⬜
    RETRO 🟩🟩🟩🟩🟩
    4/6
    RETRO ⬜⬜🟨⬜⬜
    UNITS ⬜🟨⬜🟨🟨
    STAND 🟩🟨🟩🟩⬜
    SCANT 🟩🟩🟩🟩🟩
    5/6
    SCANT ⬜⬜🟨⬜⬜
    IDEAL ⬜⬜🟨🟨🟨
    LARGE 🟨🟩⬜⬜🟩
    MAYBE ⬜🟩⬜🟨🟩
    FABLE 🟩🟩🟩🟩🟩
    Final 2/2
    WIRES 🟩🟩🟨🟩🟨
    WISER 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1480 🥳 score:19 ⏱️ 0:01:20.584169

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. POLYP attempts:7 score:7
2. GUIDE attempts:4 score:4
3. MILKY attempts:3 score:3
4. MINER attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1480 🥳 score:62 ⏱️ 0:04:01.887064

📜 1 sessions

Octordle Classic

1. CANAL attempts:5 score:5
2. TRIBE attempts:6 score:6
3. PATCH attempts:4 score:4
4. HEAVY attempts:11 score:11
5. KAYAK attempts:7 score:7
6. SHAPE attempts:8 score:8
7. SCENT attempts:9 score:9
8. MAUVE attempts:12 score:12

# [squareword.org](squareword.org) 🧩 #1473 🥳 8 ⏱️ 0:02:57.254416

📜 2 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟩 🟨
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T E E P
    H O V E L
    A W A R E
    M E D I A
    S L E E T

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1410 🥳 670 ⏱️ 0:12:35.264651

🤔 671 attempts
📜 2 sessions
🫧 38 chat sessions
⁉️ 197 chat prompts
🤖 197 dolphin3:latest replies
😱   1 🔥   3 🥵  18 😎  92 🥶 459 🧊  97

      $1 #671 closing           100.00°C 🥳 1000‰ ~574 used:0   [573]  source:dolphin3
      $2 #638 closed             65.05°C 😱  999‰   ~1 used:16  [0]    source:dolphin3
      $3  #98 opening            60.65°C 🔥  998‰ ~111 used:184 [110]  source:dolphin3
      $4 #124 opened             43.77°C 🔥  994‰ ~110 used:142 [109]  source:dolphin3
      $5  #90 open               40.63°C 🔥  991‰ ~109 used:114 [108]  source:dolphin3
      $6 #647 shuttered          38.66°C 🥵  988‰   ~7 used:2   [6]    source:dolphin3
      $7 #669 finishing          35.56°C 🥵  983‰   ~2 used:1   [1]    source:dolphin3
      $8 #397 dropping           33.79°C 🥵  981‰ ~105 used:11  [104]  source:dolphin3
      $9 #541 knocking           32.68°C 🥵  980‰   ~9 used:10  [8]    source:dolphin3
     $10 #545 demolishing        32.27°C 🥵  979‰  ~10 used:10  [9]    source:dolphin3
     $11 #635 razing             30.97°C 🥵  969‰   ~3 used:1   [2]    source:dolphin3
     $25  #93 shattering         25.65°C 😎  899‰  ~17 used:0   [16]   source:dolphin3
    $116 #619 removal            15.62°C 🥶       ~118 used:0   [117]  source:dolphin3
    $575 #187 grow               -0.19°C 🧊       ~575 used:0   [574]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1443 🥳 193 ⏱️ 0:03:49.429809

🤔 194 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 44 chat prompts
🤖 44 dolphin3:latest replies
😎   5 🥶 158 🧊  30

      $1 #194 plateau         100.00°C 🥳 1000‰ ~164 used:0  [163]  source:dolphin3
      $2  #97 fromage          25.08°C 😎  704‰   ~5 used:27 [4]    source:dolphin3
      $3 #181 verre            24.22°C 😎  627‰   ~3 used:5  [2]    source:dolphin3
      $4 #171 assiette         22.56°C 😎  408‰   ~2 used:4  [1]    source:dolphin3
      $5  #92 déjeuner         21.00°C 😎  108‰   ~4 used:22 [3]    source:dolphin3
      $6 #190 croûte           20.73°C 😎   45‰   ~1 used:0  [0]    source:dolphin3
      $7 #120 chèvre           20.13°C 🥶         ~9 used:5  [8]    source:dolphin3
      $8  #12 latte            20.07°C 🥶         ~6 used:22 [5]    source:dolphin3
      $9 #177 poivrière        19.30°C 🥶        ~13 used:0  [12]   source:dolphin3
     $10 #193 plastique        19.08°C 🥶        ~14 used:0  [13]   source:dolphin3
     $11 #141 charcuterie      19.06°C 🥶        ~15 used:0  [14]   source:dolphin3
     $12 #186 pichet           18.31°C 🥶        ~16 used:0  [15]   source:dolphin3
     $13 #146 blanc            17.84°C 🥶        ~17 used:0  [16]   source:dolphin3
    $165 #134 quiche           -0.07°C 🧊       ~165 used:0  [164]  source:dolphin3

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #94 🥳 score:29 ⏱️ 0:02:51.776298

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. FOYER attempts:9 score:9
2. PRONE attempts:7 score:7
3. STERN attempts:5 score:5
4. SHEEN attempts:8 score:8
