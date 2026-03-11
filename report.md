# 2026-03-12

- 🔗 spaceword.org 🧩 2026-03-11 🏁 score 2173 ranked 4.0% 15/372 ⏱️ 8:33:17.641103
- 🔗 alfagok.diginaut.net 🧩 #495 🥳 32 ⏱️ 0:00:33.495311
- 🔗 alphaguess.com 🧩 #962 🥳 32 ⏱️ 0:00:29.815538
- 🔗 dontwordle.com 🧩 #1388 🥳 6 ⏱️ 0:01:23.927489
- 🔗 dictionary.com hurdle 🧩 #1531 🥳 20 ⏱️ 0:04:00.440739
- 🔗 Quordle Classic 🧩 #1508 🥳 score:26 ⏱️ 0:01:45.832400
- 🔗 Octordle Classic 🧩 #1508 🥳 score:62 ⏱️ 0:03:14.524905
- 🔗 squareword.org 🧩 #1501 🥳 9 ⏱️ 0:02:13.872276
- 🔗 cemantle.certitudes.org 🧩 #1438 🥳 488 ⏱️ 2:54:36.031772
- 🔗 cemantix.certitudes.org 🧩 #1471 🥳 184 ⏱️ 0:03:41.169477

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











# [spaceword.org](spaceword.org) 🧩 2026-03-11 🏁 score 2173 ranked 4.0% 15/372 ⏱️ 8:33:17.641103

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 15/372

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ D _ A Q U A F I T   
      _ A _ _ _ _ H I C _   
      _ N O V E L I Z E R   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #495 🥳 32 ⏱️ 0:00:33.495311

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken       
    @+49841  [ 49841] boks          q6  ? ␅
    @+49841  [ 49841] boks          q7  ? after
    @+74754  [ 74754] dc            q8  ? ␅
    @+74754  [ 74754] dc            q9  ? after
    @+77726  [ 77726] der           q14 ? ␅
    @+77726  [ 77726] der           q15 ? after
    @+79229  [ 79229] dicht         q16 ? ␅
    @+79229  [ 79229] dicht         q17 ? after
    @+79260  [ 79260] dichtdoe      q26 ? ␅
    @+79260  [ 79260] dichtdoe      q27 ? after
    @+79276  [ 79276] dichte        q28 ? ␅
    @+79276  [ 79276] dichte        q29 ? after
    @+79280  [ 79280] dichter       q30 ? ␅
    @+79280  [ 79280] dichter       q31 ? it
    @+79280  [ 79280] dichter       done. it
    @+79292  [ 79292] dichters      q24 ? ␅
    @+79292  [ 79292] dichters      q25 ? before
    @+79362  [ 79362] dichtgevroren q22 ? ␅
    @+79362  [ 79362] dichtgevroren q23 ? before
    @+79495  [ 79495] dichtst       q20 ? ␅
    @+79495  [ 79495] dichtst       q21 ? before
    @+79772  [ 79772] dienst        q18 ? ␅
    @+79772  [ 79772] dienst        q19 ? before
    @+80887  [ 80887] dijk          q12 ? ␅
    @+80887  [ 80887] dijk          q13 ? before
    @+87213  [ 87213] draag         q10 ? ␅
    @+87213  [ 87213] draag         q11 ? before
    @+99737  [ 99737] ex            q4  ? ␅
    @+99737  [ 99737] ex            q5  ? before
    @+199609 [199609] lij           q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #962 🥳 32 ⏱️ 0:00:29.815538

🤔 32 attempts
📜 1 sessions

    @        [     0] aa       
    @+98218  [ 98218] mach     q0  ? ␅
    @+98218  [ 98218] mach     q1  ? after
    @+147373 [147373] rhumb    q2  ? ␅
    @+147373 [147373] rhumb    q3  ? after
    @+171638 [171638] ta       q4  ? ␅
    @+171638 [171638] ta       q5  ? after
    @+182002 [182002] un       q6  ? ␅
    @+182002 [182002] un       q7  ? after
    @+189264 [189264] vicar    q8  ? ␅
    @+189264 [189264] vicar    q9  ? after
    @+192868 [192868] whir     q10 ? ␅
    @+192868 [192868] whir     q11 ? after
    @+193484 [193484] win      q14 ? ␅
    @+193484 [193484] win      q15 ? after
    @+194064 [194064] wo       q16 ? ␅
    @+194064 [194064] wo       q17 ? after
    @+194265 [194265] wood     q18 ? ␅
    @+194265 [194265] wood     q19 ? after
    @+194478 [194478] word     q20 ? ␅
    @+194478 [194478] word     q21 ? after
    @+194508 [194508] work     q22 ? ␅
    @+194508 [194508] work     q23 ? after
    @+194587 [194587] works    q24 ? ␅
    @+194587 [194587] works    q25 ? after
    @+194610 [194610] workweek q28 ? ␅
    @+194610 [194610] workweek q29 ? after
    @+194614 [194614] world    q30 ? ␅
    @+194614 [194614] world    q31 ? it
    @+194614 [194614] world    done. it
    @+194632 [194632] worm     q27 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1388 🥳 6 ⏱️ 0:01:23.927489

📜 1 sessions
💰 score: 21

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:FREER n n n n n remain:4802
    ⬜⬜⬜⬜⬜ tried:COCOS n n n n n remain:1063
    ⬜⬜⬜⬜⬜ tried:ADDAX n n n n n remain:275
    ⬜⬜⬜⬜⬜ tried:PYGMY n n n n n remain:43
    ⬜🟨⬜⬜⬜ tried:JINNI n m n n n remain:12
    ⬜⬜🟩⬜⬜ tried:WHIZZ n n Y n n remain:3

    Undos used: 3

      3 words remaining
    x 7 unused letters
    = 21 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1531 🥳 20 ⏱️ 0:04:00.440739

📜 1 sessions
💰 score: 9600

    6/6
    TOEAS ⬜⬜🟨⬜⬜
    CRIED ⬜🟨⬜🟩⬜
    GLUER ⬜🟨⬜🟩🟨
    REBEL 🟩🟩⬜🟩🟩
    REPEL 🟩🟩⬜🟩🟩
    REVEL 🟩🟩🟩🟩🟩
    4/6
    REVEL 🟩⬜⬜⬜⬜
    RATIO 🟩🟨⬜⬜🟨
    ROANS 🟩🟩🟩⬜⬜
    ROACH 🟩🟩🟩🟩🟩
    5/6
    ROACH ⬜🟩⬜⬜⬜
    TOLED ⬜🟩⬜🟨⬜
    NOISE ⬜🟩⬜⬜🟩
    VOGUE ⬜🟩🟨🟨🟩
    GOUGE 🟩🟩🟩🟩🟩
    3/6
    GOUGE ⬜⬜🟩⬜⬜
    BLURT 🟨⬜🟩🟨⬜
    CRUMB 🟩🟩🟩🟩🟩
    Final 2/2
    PAUSE 🟨🟩🟩⬜🟩
    TAUPE 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1508 🥳 score:26 ⏱️ 0:01:45.832400

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. ARTSY attempts:5 score:5
2. GEESE attempts:8 score:8
3. BUGGY attempts:7 score:7
4. FOCUS attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1508 🥳 score:62 ⏱️ 0:03:14.524905

📜 1 sessions

Octordle Classic

1. GRAIN attempts:8 score:8
2. INLET attempts:6 score:6
3. REPEL attempts:5 score:5
4. STONY attempts:4 score:4
5. BROWN attempts:11 score:11
6. STUNG attempts:7 score:7
7. PRIDE attempts:12 score:12
8. RASPY attempts:9 score:9

# [squareword.org](squareword.org) 🧩 #1501 🥳 9 ⏱️ 0:02:13.872276

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P E N D
    C U R I O
    A P A C E
    L A S E R
    P E E R S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1438 🥳 488 ⏱️ 2:54:36.031772

🤔 489 attempts
📜 2 sessions
🫧 60 chat sessions
⁉️ 236 chat prompts
🤖 18 llama3.1:8b replies
🤖 6 qwen3:4b replies
🤖 3 lfm2.5-thinking:latest replies
🤖 75 glm-4.7-flash:latest replies
🤖 121 dolphin3:latest replies
🤖 3 nemotron-3-nano:latest replies
🤖 10 falcon3:10b replies
🥵   4 😎  37 🥶 428 🧊  19

      $1 #489 wander          100.00°C 🥳 1000‰ ~470 used:0  [469]  source:llama3  
      $2 #435 rummage          47.08°C 🥵  959‰  ~16 used:13 [15]   source:llama3  
      $3 #481 go               45.78°C 🥵  949‰   ~1 used:1  [0]    source:llama3  
      $4 #469 peruse           44.84°C 🥵  936‰   ~3 used:5  [2]    source:llama3  
      $5 #447 browse           43.41°C 🥵  921‰   ~2 used:4  [1]    source:llama3  
      $6 #453 prowl            40.66°C 😎  886‰   ~4 used:0  [3]    source:llama3  
      $7 #264 solitude         39.93°C 😎  873‰  ~41 used:74 [40]   source:dolphin3
      $8 #265 lonely           39.76°C 😎  868‰  ~36 used:33 [35]   source:dolphin3
      $9 #249 secluded         38.00°C 😎  834‰  ~33 used:27 [32]   source:dolphin3
     $10 #443 scour            37.79°C 😎  826‰   ~5 used:0  [4]    source:llama3  
     $11 #457 delve            36.87°C 😎  796‰   ~6 used:0  [5]    source:llama3  
     $12 #455 scavenge         35.94°C 😎  760‰   ~7 used:0  [6]    source:llama3  
     $43 #278 serenity         28.77°C 🥶        ~53 used:0  [52]   source:dolphin3
    $471  #75 dioxide          -0.47°C 🧊       ~471 used:0  [470]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1471 🥳 184 ⏱️ 0:03:41.169477

🤔 185 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 48 chat prompts
🤖 48 dolphin3:latest replies
🔥   2 🥵   1 😎  23 🥶 137 🧊  21

      $1 #185 thé          100.00°C 🥳 1000‰ ~164 used:0  [163]  source:dolphin3
      $2 #179 tasse         60.59°C 😱  999‰   ~1 used:11 [0]    source:dolphin3
      $3 #180 théière       52.34°C 🔥  997‰   ~2 used:6  [1]    source:dolphin3
      $4 #153 terrasse      34.33°C 🥵  917‰  ~10 used:17 [9]    source:dolphin3
      $5 #166 verre         33.50°C 😎  896‰  ~11 used:2  [10]   source:dolphin3
      $6 #178 pichet        30.81°C 😎  819‰   ~3 used:0  [2]    source:dolphin3
      $7 #174 bol           29.49°C 😎  752‰   ~4 used:0  [3]    source:dolphin3
      $8 #111 canapé        27.90°C 😎  658‰  ~26 used:12 [25]   source:dolphin3
      $9 #181 fleur         27.66°C 😎  639‰   ~5 used:0  [4]    source:dolphin3
     $10 #160 carafe        27.43°C 😎  618‰  ~12 used:2  [11]   source:dolphin3
     $11 #107 lounge        27.14°C 😎  596‰  ~22 used:5  [21]   source:dolphin3
     $12 #129 jardin        26.91°C 😎  571‰  ~13 used:2  [12]   source:dolphin3
     $28  #51 sac           22.17°C 🥶        ~30 used:3  [29]   source:dolphin3
    $165  #94 hygiène       -0.87°C 🧊       ~165 used:0  [164]  source:dolphin3
