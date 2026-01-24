# 2026-01-25

- 🔗 spaceword.org 🧩 2026-01-24 🏁 score 2165 ranked 45.8% 141/308 ⏱️ 0:45:29.829072
- 🔗 alfagok.diginaut.net 🧩 #449 🥳 32 ⏱️ 0:00:37.007213
- 🔗 alphaguess.com 🧩 #916 🥳 32 ⏱️ 0:00:33.198674
- 🔗 dontwordle.com 🧩 #1342 🥳 6 ⏱️ 0:02:52.312656
- 🔗 dictionary.com hurdle 🧩 #1485 🥳 17 ⏱️ 0:03:07.712932
- 🔗 Quordle Classic 🧩 #1462 😦 score:25 ⏱️ 0:01:43.392561
- 🔗 Octordle Classic 🧩 #1462 🥳 score:68 ⏱️ 0:03:26.537133
- 🔗 squareword.org 🧩 #1455 🥳 8 ⏱️ 0:02:06.008560
- 🔗 cemantle.certitudes.org 🧩 #1392 🥳 199 ⏱️ 0:04:40.412662
- 🔗 cemantix.certitudes.org 🧩 #1425 🥳 226 ⏱️ 0:04:24.504115
- 🔗 Quordle Rescue 🧩 #76 🥳 score:23 ⏱️ 0:01:37.127416

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










# [spaceword.org](spaceword.org) 🧩 2026-01-24 🏁 score 2165 ranked 45.8% 141/308 ⏱️ 0:45:29.829072

📜 3 sessions
- tiles: 21/21
- score: 2165 bonus: +65
- rank: 141/308

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ W _ _ _ _ _   
      _ _ _ F I Z _ _ _ _   
      _ _ B A R O Q U E _   
      _ _ A D R O I T _ _   
      _ _ P E A N _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #449 🥳 32 ⏱️ 0:00:37.007213

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken       
    @+199833 [199833] lijm          q0  ? ␅
    @+199833 [199833] lijm          q1  ? after
    @+299738 [299738] schub         q2  ? ␅
    @+299738 [299738] schub         q3  ? after
    @+349511 [349511] vakantie      q4  ? ␅
    @+349511 [349511] vakantie      q5  ? after
    @+353079 [353079] ver           q8  ? ␅
    @+353079 [353079] ver           q9  ? after
    @+363662 [363662] verzot        q10 ? ␅
    @+363662 [363662] verzot        q11 ? after
    @+368674 [368674] voetbal       q12 ? ␅
    @+368674 [368674] voetbal       q13 ? after
    @+370523 [370523] voor          q14 ? ␅
    @+370523 [370523] voor          q15 ? after
    @+372375 [372375] voortplanting q16 ? ␅
    @+372375 [372375] voortplanting q17 ? after
    @+372809 [372809] voorwereld    q20 ? ␅
    @+372809 [372809] voorwereld    q21 ? after
    @+373020 [373020] vork          q22 ? ␅
    @+373020 [373020] vork          q23 ? after
    @+373030 [373030] vorm          q24 ? ␅
    @+373030 [373030] vorm          q25 ? after
    @+373085 [373085] vormgeving    q28 ? ␅
    @+373085 [373085] vormgeving    q29 ? after
    @+373093 [373093] vorming       q30 ? ␅
    @+373093 [373093] vorming       q31 ? it
    @+373093 [373093] vorming       done. it
    @+373138 [373138] vormloosheid  q26 ? ␅
    @+373138 [373138] vormloosheid  q27 ? before
    @+373246 [373246] vos           q19 ? before

# [alphaguess.com](alphaguess.com) 🧩 #916 🥳 32 ⏱️ 0:00:33.198674

🤔 32 attempts
📜 1 sessions

    @       [    0] aa         
    @+23683 [23683] camp       q4  ? ␅
    @+23683 [23683] camp       q5  ? after
    @+25105 [25105] carp       q12 ? ␅
    @+25105 [25105] carp       q13 ? after
    @+25587 [25587] cat        q14 ? ␅
    @+25587 [25587] cat        q15 ? after
    @+26109 [26109] cavalier   q16 ? ␅
    @+26109 [26109] cavalier   q17 ? after
    @+26160 [26160] caviar     q22 ? ␅
    @+26160 [26160] caviar     q23 ? after
    @+26187 [26187] cavities   q24 ? ␅
    @+26187 [26187] cavities   q25 ? after
    @+26188 [26188] cavity     q30 ? ␅
    @+26188 [26188] cavity     q31 ? it
    @+26188 [26188] cavity     done. it
    @+26189 [26189] cavort     q28 ? ␅
    @+26189 [26189] cavort     q29 ? before
    @+26200 [26200] cay        q26 ? ␅
    @+26200 [26200] cay        q27 ? before
    @+26214 [26214] cease      q20 ? ␅
    @+26214 [26214] cease      q21 ? before
    @+26332 [26332] cell       q18 ? ␅
    @+26332 [26332] cell       q19 ? before
    @+26636 [26636] cep        q10 ? ␅
    @+26636 [26636] cep        q11 ? before
    @+29604 [29604] circuit    q8  ? ␅
    @+29604 [29604] circuit    q9  ? before
    @+35526 [35526] convention q6  ? ␅
    @+35526 [35526] convention q7  ? before
    @+47382 [47382] dis        q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1342 🥳 6 ⏱️ 0:02:52.312656

📜 1 sessions
💰 score: 102

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:KABAB n n n n n remain:5942
    ⬜⬜⬜⬜⬜ tried:WOOZY n n n n n remain:2526
    ⬜⬜⬜⬜⬜ tried:LUSUS n n n n n remain:538
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:241
    ⬜🟨⬜⬜⬜ tried:FEMME n m n n n remain:45
    🟨⬜🟨⬜⬜ tried:EXING m n m n n remain:17

    Undos used: 5

      17 words remaining
    x 6 unused letters
    = 102 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1485 🥳 17 ⏱️ 0:03:07.712932

📜 1 sessions
💰 score: 9900

    3/6
    LEAST 🟨🟨⬜⬜🟨
    MOTEL ⬜⬜🟨🟨🟩
    ETHYL 🟩🟩🟩🟩🟩
    4/6
    ETHYL 🟨⬜⬜⬜⬜
    REDOS ⬜🟨⬜🟨⬜
    WOMEN ⬜🟨⬜🟨⬜
    ABOVE 🟩🟩🟩🟩🟩
    4/6
    ABOVE ⬜⬜⬜⬜⬜
    TULIP ⬜⬜⬜🟨⬜
    SMIRK 🟨⬜🟨🟨🟨
    RISKY 🟩🟩🟩🟩🟩
    4/6
    RISKY ⬜🟨⬜⬜⬜
    INLET 🟨⬜🟩🟨⬜
    HELIX ⬜🟩🟩🟩⬜
    BELIE 🟩🟩🟩🟩🟩
    Final 2/2
    FONTS ⬜🟩⬜🟨🟨
    JOUST 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1462 😦 score:25 ⏱️ 0:01:43.392561

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. _ATCH -BDEFIKLMNOPRSUWY attempts:9 score:-1
2. TABBY attempts:7 score:7
3. HUMOR attempts:4 score:4
4. DATUM attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1462 🥳 score:68 ⏱️ 0:03:26.537133

📜 1 sessions

Octordle Classic

1. BILGE attempts:7 score:7
2. PLIED attempts:10 score:10
3. FURRY attempts:11 score:11
4. BLEND attempts:6 score:6
5. VINYL attempts:5 score:5
6. RUGBY attempts:8 score:8
7. UNFED attempts:12 score:12
8. ETHOS attempts:9 score:9

# [squareword.org](squareword.org) 🧩 #1455 🥳 8 ⏱️ 0:02:06.008560

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟨 🟨 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B L E S S
    R A N C H
    U N D E R
    S C O N E
    H E W E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1392 🥳 199 ⏱️ 0:04:40.412662

🤔 200 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 36 chat prompts
🤖 36 dolphin3:latest replies
🥵   4 😎  16 🥶 153 🧊  26

      $1 #200   ~1 scout          100.00°C 🥳 1000‰
      $2 #159   ~9 recruit         33.46°C 🥵  973‰
      $3  #75  ~19 pick            32.84°C 🥵  970‰
      $4  #56  ~20 draft           30.84°C 🥵  940‰
      $5 #179   ~4 talent          30.78°C 🥵  937‰
      $6 #163   ~8 team            27.50°C 😎  857‰
      $7 #136  ~11 evaluate        26.66°C 😎  812‰
      $8  #43  ~21 fan             25.34°C 😎  749‰
      $9 #170   ~7 enlist          24.83°C 😎  713‰
     $10 #172   ~6 hire            24.70°C 😎  703‰
     $11 #138  ~10 assess          23.18°C 😎  568‰
     $12 #180   ~3 talented        22.46°C 😎  484‰
     $22  #80      favorite        19.70°C 🥶
    $175 #124      stream          -0.32°C 🧊

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1425 🥳 226 ⏱️ 0:04:24.504115

🤔 227 attempts
📜 1 sessions
🫧 13 chat sessions
⁉️ 51 chat prompts
🤖 51 dolphin3:latest replies
😱   1 🥵  10 😎  15 🥶 166 🧊  34

      $1 #227   ~1 vache          100.00°C 🥳 1000‰
      $2 #145  ~16 lait            53.75°C 😱  999‰
      $3 #135  ~19 chèvre          44.58°C 🥵  986‰
      $4 #121  ~22 foin            40.36°C 🥵  975‰
      $5 #223   ~3 crottin         40.04°C 🥵  973‰
      $6 #144  ~17 fromage         39.14°C 🥵  968‰
      $7 #143  ~18 bœuf            37.44°C 🥵  955‰
      $8  #79  ~25 herbage         36.45°C 🥵  942‰
      $9  #85  ~24 fumier          34.04°C 🥵  915‰
     $10 #208   ~5 camembert       33.89°C 🥵  912‰
     $11 #124  ~20 prairie         33.78°C 🥵  909‰
     $13 #119  ~23 fourrage        33.15°C 😎  892‰
     $28  #91      fumière         21.92°C 🥶
    $194 #101      désherbage      -0.19°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #76 🥳 score:23 ⏱️ 0:01:37.127416

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. LORRY attempts:9 score:9
2. TOAST attempts:3 score:3
3. CHEST attempts:5 score:5
4. SPARK attempts:6 score:6
