# 2026-03-22

- 🔗 spaceword.org 🧩 2026-03-21 🏁 score 2173 ranked 64.7% 213/329 ⏱️ 3:51:53.147337
- 🔗 alfagok.diginaut.net 🧩 #505 🥳 73 ⏱️ 0:01:43.376216
- 🔗 alphaguess.com 🧩 #972 🥳 30 ⏱️ 0:00:26.902744
- 🔗 dontwordle.com 🧩 #1398 🥳 6 ⏱️ 0:01:02.112500
- 🔗 dictionary.com hurdle 🧩 #1541 🥳 20 ⏱️ 0:02:43.624090
- 🔗 Quordle Classic 🧩 #1518 🥳 score:25 ⏱️ 0:01:28.623972
- 🔗 Octordle Classic 🧩 #1518 🥳 score:57 ⏱️ 0:03:51.125208
- 🔗 squareword.org 🧩 #1511 🥳 9 ⏱️ 0:01:58.536084
- 🔗 cemantle.certitudes.org 🧩 #1448 🥳 265 ⏱️ 0:03:47.294677
- 🔗 cemantix.certitudes.org 🧩 #1481 🥳 142 ⏱️ 0:01:28.374145

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





















# [spaceword.org](spaceword.org) 🧩 2026-03-21 🏁 score 2173 ranked 64.7% 213/329 ⏱️ 3:51:53.147337

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 213/329

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ E F _ J _ G O A   
      _ U R I N A L _ P I   
      _ _ _ R E W A X E S   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #505 🥳 73 ⏱️ 0:01:43.376216

🤔 73 attempts
📜 2 sessions

    @        [     0]           q38 ? ␅
    @+2      [     2] &-tekens   
    @+199610 [199610] lij        q0  ? ␅
    @+199610 [199610] lij        q1  ? after
    @+211614 [211614] mdccxliii  q39 ? ␅
    @+211614 [211614] mdccxliii  q40 ? .
    @+211618 [211618] mdccxlviii q26 ? ␅
    @+211618 [211618] mdccxlviii q27 ? after
    @+211618 [211618] mdccxlviii q28 ? ␅
    @+211618 [211618] mdccxlviii q29 ? after
    @+211618 [211618] mdccxlviii q30 ? ␅
    @+211618 [211618] mdccxlviii q31 ? ^
    @+211618 [211618] mdccxlviii q32 ? ␅
    @+211618 [211618] mdccxlviii q33 ? after
    @+211618 [211618] mdccxlviii q34 ? ␅
    @+211618 [211618] mdccxlviii q35 ? after
    @+211618 [211618] mdccxlviii q36 ? ␅
    @+211618 [211618] mdccxlviii q37 ? .
    @+211722 [211722] mecanicien q43 ? ␅
    @+211722 [211722] mecanicien q44 ? after
    @+212336 [212336] medica     q51 ? ␅
    @+212336 [212336] medica     q52 ? after
    @+212504 [212504] mee        q53 ? ␅
    @+212504 [212504] mee        q54 ? after
    @+212745 [212745] meehelp    q55 ? ␅
    @+212745 [212745] meehelp    q56 ? after
    @+212793 [212793] meel       q57 ? ␅
    @+212793 [212793] meel       q58 ? after
    @+212858 [212858] meeloop    q59 ? ␅
    @+212858 [212858] meeloop    q60 ? after
    @+212880 [212880] meeluister q64 ? after

# [alphaguess.com](alphaguess.com) 🧩 #972 🥳 30 ⏱️ 0:00:26.902744

🤔 30 attempts
📜 1 sessions

    @        [     0] aa        
    @+98217  [ 98217] mach      q0  ? ␅
    @+98217  [ 98217] mach      q1  ? after
    @+98217  [ 98217] mach      q2  ? ␅
    @+98217  [ 98217] mach      q3  ? after
    @+122778 [122778] parr      q6  ? ␅
    @+122778 [122778] parr      q7  ? after
    @+135069 [135069] proper    q8  ? ␅
    @+135069 [135069] proper    q9  ? after
    @+140517 [140517] rec       q10 ? ␅
    @+140517 [140517] rec       q11 ? after
    @+140617 [140617] recce     q22 ? ␅
    @+140617 [140617] recce     q23 ? after
    @+140625 [140625] receipt   q28 ? ␅
    @+140625 [140625] receipt   q29 ? it
    @+140625 [140625] receipt   done. it
    @+140641 [140641] recement  q26 ? ␅
    @+140641 [140641] recement  q27 ? before
    @+140667 [140667] recept    q24 ? ␅
    @+140667 [140667] recept    q25 ? before
    @+140723 [140723] rechart   q20 ? ␅
    @+140723 [140723] rechart   q21 ? before
    @+140934 [140934] recollect q18 ? ␅
    @+140934 [140934] recollect q19 ? before
    @+141352 [141352] recto     q16 ? ␅
    @+141352 [141352] recto     q17 ? before
    @+142213 [142213] ref       q14 ? ␅
    @+142213 [142213] ref       q15 ? before
    @+143941 [143941] reminisce q12 ? ␅
    @+143941 [143941] reminisce q13 ? before
    @+147372 [147372] rhumb     q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1398 🥳 6 ⏱️ 0:01:02.112500

📜 1 sessions
💰 score: 21

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MAMMA n n n n n remain:6571
    ⬜⬜⬜⬜⬜ tried:HOWFF n n n n n remain:2759
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:1520
    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:584
    ⬜⬜🟩⬜⬜ tried:DJINN n n Y n n remain:50
    ⬜⬜🟩🟩⬜ tried:CRICK n n Y Y n remain:3

    Undos used: 2

      3 words remaining
    x 7 unused letters
    = 21 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1541 🥳 20 ⏱️ 0:02:43.624090

📜 1 sessions
💰 score: 9600

    4/6
    SLATE ⬜🟨⬜⬜🟨
    LOVED 🟩⬜⬜🟨⬜
    LEMUR 🟩🟩⬜⬜⬜
    LEECH 🟩🟩🟩🟩🟩
    5/6
    LEECH 🟨⬜⬜⬜⬜
    FOALS ⬜⬜⬜🟨⬜
    BULGY ⬜⬜🟨🟨⬜
    GLINT 🟨🟨🟨⬜⬜
    VIGIL 🟩🟩🟩🟩🟩
    5/6
    VIGIL ⬜⬜⬜🟩⬜
    CURIA 🟨⬜⬜🟩🟨
    ANTIC 🟨🟨⬜🟩🟩
    MANIC ⬜🟩🟩🟩🟩
    PANIC 🟩🟩🟩🟩🟩
    4/6
    PANIC ⬜🟨⬜⬜⬜
    TEARS ⬜🟨🟨⬜⬜
    ABLED 🟩⬜⬜🟨⬜
    AWOKE 🟩🟩🟩🟩🟩
    Final 2/2
    CASTE 🟩🟩🟨⬜🟩
    CAUSE 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1518 🥳 score:25 ⏱️ 0:01:28.623972

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SPLAT attempts:4 score:4
2. BACON attempts:8 score:8
3. CAIRN attempts:7 score:7
4. AWFUL attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1518 🥳 score:57 ⏱️ 0:03:51.125208

📜 2 sessions

Octordle Classic

1. SULKY attempts:4 score:4
2. GODLY attempts:9 score:9
3. TRACT attempts:11 score:11
4. SUNNY attempts:3 score:3
5. SAUTE attempts:5 score:5
6. RAVEN attempts:8 score:8
7. TEASE attempts:10 score:10
8. ALGAE attempts:7 score:7

# [squareword.org](squareword.org) 🧩 #1511 🥳 9 ⏱️ 0:01:58.536084

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C A V E D
    E R O D E
    D O D G E
    A S K E D
    R E A D S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1448 🥳 265 ⏱️ 0:03:47.294677

🤔 266 attempts
📜 1 sessions
🫧 12 chat sessions
⁉️ 59 chat prompts
🤖 59 dolphin3:latest replies
🔥   1 🥵  17 😎  45 🥶 179 🧊  23

      $1 #266 recover         100.00°C 🥳 1000‰ ~243 used:0  [242]  source:dolphin3
      $2 #265 reclaim          58.42°C 🔥  994‰   ~1 used:0  [0]    source:dolphin3
      $3 #242 rebuild          49.12°C 🥵  989‰  ~13 used:8  [12]   source:dolphin3
      $4 #243 restore          47.00°C 🥵  986‰  ~11 used:5  [10]   source:dolphin3
      $5 #233 mend             46.42°C 🥵  985‰  ~10 used:4  [9]    source:dolphin3
      $6 #249 rehabilitate     44.73°C 🥵  979‰   ~5 used:2  [4]    source:dolphin3
      $7 #246 reconstruct      43.66°C 🥵  975‰   ~6 used:2  [5]    source:dolphin3
      $8 #248 regenerate       42.33°C 🥵  970‰   ~7 used:2  [6]    source:dolphin3
      $9 #264 revive           41.06°C 🥵  966‰   ~2 used:1  [1]    source:dolphin3
     $10 #158 subside          40.45°C 🥵  959‰  ~60 used:30 [59]   source:dolphin3
     $11 #253 resurrect        40.17°C 🥵  958‰   ~3 used:1  [2]    source:dolphin3
     $20 #241 reassemble       33.70°C 😎  883‰  ~14 used:0  [13]   source:dolphin3
     $65 #127 smother          21.92°C 🥶        ~70 used:0  [69]   source:dolphin3
    $244  #19 minivan          -0.02°C 🧊       ~244 used:0  [243]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1481 🥳 142 ⏱️ 0:01:28.374145

🤔 143 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 19 chat prompts
🤖 19 dolphin3:latest replies
😱   1 🔥   3 🥵   2 😎  17 🥶 100 🧊  19

      $1 #143 rival            100.00°C 🥳 1000‰ ~124 used:0 [123]  source:dolphin3
      $2 #103 rivalité          54.48°C 😱  999‰   ~1 used:7 [0]    source:dolphin3
      $3 #109 adversaire        52.87°C 🔥  998‰   ~2 used:1 [1]    source:dolphin3
      $4  #97 concurrent        52.24°C 🔥  997‰   ~4 used:2 [3]    source:dolphin3
      $5 #105 suprématie        51.44°C 🔥  995‰   ~3 used:1 [2]    source:dolphin3
      $6 #111 affrontement      42.17°C 🥵  975‰   ~5 used:0 [4]    source:dolphin3
      $7 #118 dissension        41.57°C 🥵  970‰   ~6 used:0 [5]    source:dolphin3
      $8  #71 rang              33.37°C 😎  846‰  ~22 used:5 [21]   source:dolphin3
      $9  #95 champion          32.65°C 😎  814‰   ~7 used:0 [6]    source:dolphin3
     $10  #99 gloire            30.80°C 😎  702‰   ~8 used:0 [7]    source:dolphin3
     $11 #123 opposition        30.59°C 😎  687‰   ~9 used:0 [8]    source:dolphin3
     $12 #141 combat            30.08°C 😎  643‰  ~10 used:0 [9]    source:dolphin3
     $25  #64 course            25.25°C 🥶        ~27 used:1 [26]   source:dolphin3
    $125   #2 chaton            -0.23°C 🧊       ~125 used:0 [124]  source:dolphin3
