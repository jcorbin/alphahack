# 2026-01-29

- 🔗 spaceword.org 🧩 2026-01-28 🏁 score 2173 ranked 5.2% 18/344 ⏱️ 2:41:00.713025
- 🔗 alfagok.diginaut.net 🧩 #453 🥳 16 ⏱️ 0:00:27.319639
- 🔗 alphaguess.com 🧩 #920 🥳 30 ⏱️ 0:00:32.511269
- 🔗 dontwordle.com 🧩 #1346 🥳 6 ⏱️ 0:03:03.761861
- 🔗 dictionary.com hurdle 🧩 #1489 🥳 15 ⏱️ 0:03:46.033739
- 🔗 Quordle Classic 🧩 #1466 🥳 score:26 ⏱️ 0:01:50.144744
- 🔗 Octordle Classic 🧩 #1466 🥳 score:55 ⏱️ 0:03:50.793244
- 🔗 squareword.org 🧩 #1459 🥳 7 ⏱️ 0:01:59.200101
- 🔗 cemantle.certitudes.org 🧩 #1396 🥳 284 ⏱️ 0:41:26.741361
- 🔗 cemantix.certitudes.org 🧩 #1429 😦 825 ⏱️ 7:04:38.542591

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














# [spaceword.org](spaceword.org) 🧩 2026-01-28 🏁 score 2173 ranked 5.2% 18/344 ⏱️ 2:41:00.713025

📜 6 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 18/344

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ D _ J _ R A D I I   
      _ A M I G A _ E F _   
      _ K _ N I X I E S _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #453 🥳 16 ⏱️ 0:00:27.319639

🤔 16 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199833 [199833] lijm      q0  ? ␅
    @+199833 [199833] lijm      q1  ? after
    @+299738 [299738] schub     q2  ? ␅
    @+299738 [299738] schub     q3  ? after
    @+349512 [349512] vakantie  q4  ? ␅
    @+349512 [349512] vakantie  q5  ? after
    @+374253 [374253] vrij      q6  ? ␅
    @+374253 [374253] vrij      q7  ? after
    @+386794 [386794] wind      q8  ? ␅
    @+386794 [386794] wind      q9  ? after
    @+390003 [390003] wrik      q12 ? ␅
    @+390003 [390003] wrik      q13 ? after
    @+391425 [391425] zand      q14 ? ␅
    @+391425 [391425] zand      q15 ? it
    @+391425 [391425] zand      done. it
    @+393211 [393211] zelfmoord q10 ? ␅
    @+393211 [393211] zelfmoord q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #920 🥳 30 ⏱️ 0:00:32.511269

🤔 30 attempts
📜 1 sessions

    @       [    0] aa        
    @+19    [   19] ab        q16 ? ␅
    @+19    [   19] ab        q17 ? after
    @+355   [  355] abort     q18 ? ␅
    @+355   [  355] abort     q19 ? after
    @+379   [  379] abound    q24 ? ␅
    @+379   [  379] abound    q25 ? after
    @+385   [  385] above     q28 ? ␅
    @+385   [  385] above     q29 ? it
    @+385   [  385] above     done. it
    @+392   [  392] abrachias q26 ? ␅
    @+392   [  392] abrachias q27 ? before
    @+404   [  404] abrasive  q22 ? ␅
    @+404   [  404] abrasive  q23 ? before
    @+451   [  451] abs       q20 ? ␅
    @+451   [  451] abs       q21 ? before
    @+698   [  698] acaleph   q14 ? ␅
    @+698   [  698] acaleph   q15 ? before
    @+1398  [ 1398] acrogen   q12 ? ␅
    @+1398  [ 1398] acrogen   q13 ? before
    @+2802  [ 2802] ag        q10 ? ␅
    @+2802  [ 2802] ag        q11 ? before
    @+5876  [ 5876] angel     q8  ? ␅
    @+5876  [ 5876] angel     q9  ? before
    @+11764 [11764] back      q6  ? ␅
    @+11764 [11764] back      q7  ? before
    @+23683 [23683] camp      q4  ? ␅
    @+23683 [23683] camp      q5  ? before
    @+47382 [47382] dis       q2  ? ␅
    @+47382 [47382] dis       q3  ? before
    @+98220 [98220] mach      q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1346 🥳 6 ⏱️ 0:03:03.761861

📜 1 sessions
💰 score: 9

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:DOODY n n n n n remain:6216
    ⬜⬜⬜⬜⬜ tried:SHAHS n n n n n remain:991
    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:301
    ⬜⬜⬜⬜⬜ tried:FLUFF n n n n n remain:99
    🟨⬜⬜🟨🟨 tried:EGGER m n n m m remain:17
    🟨🟨⬜🟨🟩 tried:METRE m m n m Y remain:1

    Undos used: 4

      1 words remaining
    x 9 unused letters
    = 9 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1489 🥳 15 ⏱️ 0:03:46.033739

📜 1 sessions
💰 score: 10100

    4/6
    TARES ⬜🟨⬜⬜🟨
    CLASH ⬜⬜🟨🟨⬜
    SOMAN 🟩⬜⬜🟩⬜
    SQUAD 🟩🟩🟩🟩🟩
    4/6
    SQUAD ⬜⬜⬜🟨⬜
    CRATE ⬜🟨🟩⬜⬜
    GLARY ⬜⬜🟩🟩⬜
    WHARF 🟩🟩🟩🟩🟩
    3/6
    WHARF ⬜⬜🟩⬜⬜
    LEANT ⬜⬜🟩🟩⬜
    PIANO 🟩🟩🟩🟩🟩
    3/6
    PIANO ⬜🟨⬜⬜🟨
    COILS ⬜🟩🟩🟩⬜
    DOILY 🟩🟩🟩🟩🟩
    Final 1/2
    GRADE 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1466 🥳 score:26 ⏱️ 0:01:50.144744

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. BLACK attempts:4 score:4
2. VOCAL attempts:9 score:9
3. GLADE attempts:6 score:6
4. MAPLE attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1466 🥳 score:55 ⏱️ 0:03:50.793244

📜 1 sessions

Octordle Classic

1. BELCH attempts:10 score:10
2. QUAKE attempts:5 score:5
3. ELATE attempts:12 score:12
4. READY attempts:3 score:3
5. GRAVY attempts:8 score:8
6. CORNY attempts:7 score:7
7. FORUM attempts:4 score:4
8. HUMAN attempts:6 score:6

# [squareword.org](squareword.org) 🧩 #1459 🥳 7 ⏱️ 0:01:59.200101

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    R U I N S
    E N N U I
    S M A R T
    T E N S E
    S T E E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1396 🥳 284 ⏱️ 0:41:26.741361

🤔 285 attempts
📜 5 sessions
🫧 26 chat sessions
⁉️ 74 chat prompts
🤖 71 dolphin3:latest replies
🤖 1 glm-4.7-flash:latest replies
🤖 1 nemotron-3-nano:latest replies
🔥   1 🥵   1 😎  18 🥶 260 🧊   4

      $1 #285   ~1 iron          used: 0 source:dolphin3  100.00°C 🥳 1000‰
      $2 #144  ~17 wood          used:31 source:dolphin3   47.69°C 🔥  998‰
      $3 #191  ~13 wooden        used:19 source:dolphin3   33.59°C 🥵  920‰
      $4 #148  ~16 lumber        used:11 source:dolphin3   30.40°C 😎  803‰
      $5 #275   ~4 pilaster      used: 0 source:dolphin3   29.95°C 😎  771‰
      $6 #133  ~19 bamboo        used: 5 source:dolphin3   29.90°C 😎  766‰
      $7 #242   ~9 dowel         used: 1 source:dolphin3   29.32°C 😎  711‰
      $8 #208  ~11 lattice       used: 6 source:dolphin3   29.14°C 😎  694‰
      $9 #272   ~5 dado          used: 0 source:dolphin3   28.79°C 😎  663‰
     $10  #84  ~20 cane          used: 6 source:dolphin3   27.92°C 😎  567‰
     $11 #240  ~10 corbel        used: 1 source:dolphin3   27.39°C 😎  505‰
     $12 #279   ~3 wainscotting  used: 1 source:dolphin3   26.63°C 😎  390‰
     $22 #221      pulp          used: 0 source:dolphin3   24.46°C 🥶
    $282 #145      board         used: 0 source:dolphin3   -0.51°C 🧊

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1429 😦 825 ⏱️ 7:04:38.542591

🤔 824 attempts
📜 4 sessions
🫧 98 chat sessions
⁉️ 489 chat prompts
🤖 409 dolphin3:latest replies
🤖 44 nemotron-3-nano:latest replies
🤖 9 glm-4.7-flash:latest replies
🤖 24 llama3.3:latest replies
😦 🔥   7 🥵  30 😎  85 🥶 547 🧊 155

      $1 #218  ~93 tante           used:372 source:dolphin3   70.06°C 🔥  998‰
      $2 #204 ~103 mère            used:215 source:dolphin3   66.35°C 🔥  997‰
      $3 #660  ~26 mamie           used: 26 source:llama3     61.74°C 🔥  995‰
      $4 #211  ~99 oncle           used: 54 source:dolphin3   60.16°C 🔥  993‰
      $5 #201 ~106 père            used: 10 source:dolphin3   59.17°C 🔥  992‰
      $6 #212  ~98 sœur            used: 10 source:dolphin3   57.54°C 🔥  990‰
      $7 #375  ~52 soeur           used:  7 source:dolphin3   57.54°C 🔥  990‰
      $8 #206 ~102 cousin          used:  5 source:dolphin3   55.89°C 🥵  988‰
      $9 #316  ~64 maman           used:  4 source:dolphin3   55.43°C 🥵  987‰
     $10 #241  ~85 mari            used:  4 source:dolphin3   55.10°C 🥵  986‰
     $11 #300  ~69 mémé            used:  4 source:dolphin3   53.66°C 🥵  985‰
     $38 #315  ~65 garçon          used:  2 source:dolphin3   37.38°C 😎  898‰
    $123 #307      nounou          used:  0 source:dolphin3   26.15°C 🥶
    $670 #440      employer        used:  0 source:dolphin3   -0.12°C 🧊
