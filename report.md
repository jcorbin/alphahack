# 2026-03-06

- 🔗 spaceword.org 🧩 2026-03-05 🏁 score 2173 ranked 10.6% 34/322 ⏱️ 0:38:58.416969
- 🔗 alfagok.diginaut.net 🧩 #489 🥳 28 ⏱️ 0:00:36.527186
- 🔗 alphaguess.com 🧩 #956 🥳 34 ⏱️ 0:00:45.495335
- 🔗 dontwordle.com 🧩 #1382 🥳 6 ⏱️ 0:02:35.480678
- 🔗 dictionary.com hurdle 🧩 #1525 🥳 20 ⏱️ 0:03:54.001717
- 🔗 Quordle Classic 🧩 #1502 🥳 score:22 ⏱️ 0:01:11.504127
- 🔗 Octordle Classic 🧩 #1502 🥳 score:59 ⏱️ 0:08:07.724763
- 🔗 squareword.org 🧩 #1495 🥳 7 ⏱️ 0:02:11.543611
- 🔗 cemantle.certitudes.org 🧩 #1432 🥳 213 ⏱️ 0:05:08.843217
- 🔗 cemantix.certitudes.org 🧩 #1465 🥳 68 ⏱️ 0:01:12.248017

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





# [spaceword.org](spaceword.org) 🧩 2026-03-05 🏁 score 2173 ranked 10.6% 34/322 ⏱️ 0:38:58.416969

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 34/322

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ C _ E P A Z O T E   
      _ I _ _ U _ _ S O W   
      _ S E X T A N _ Y E   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #489 🥳 28 ⏱️ 0:00:36.527186

🤔 28 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+2      [     2] -cijferig   
    @+49841  [ 49841] boks        q4  ? ␅
    @+49841  [ 49841] boks        q5  ? after
    @+62280  [ 62280] cement      q8  ? ␅
    @+62280  [ 62280] cement      q9  ? after
    @+63052  [ 63052] check       q16 ? ␅
    @+63052  [ 63052] check       q17 ? after
    @+63443  [ 63443] chloroplast q18 ? ␅
    @+63443  [ 63443] chloroplast q19 ? a
    @+63443  [ 63443] chloroplast q20 ? ␅
    @+63443  [ 63443] chloroplast q21 ? after
    @+63459  [ 63459] chocolade   q26 ? ␅
    @+63459  [ 63459] chocolade   q27 ? it
    @+63459  [ 63459] chocolade   done. it
    @+63519  [ 63519] chole       q24 ? ␅
    @+63519  [ 63519] chole       q25 ? before
    @+63623  [ 63623] christelijk q22 ? ␅
    @+63623  [ 63623] christelijk q23 ? before
    @+63834  [ 63834] chroom      q14 ? ␅
    @+63834  [ 63834] chroom      q15 ? before
    @+65388  [ 65388] coat        q12 ? ␅
    @+65388  [ 65388] coat        q13 ? before
    @+68514  [ 68514] connectie   q10 ? ␅
    @+68514  [ 68514] connectie   q11 ? before
    @+74754  [ 74754] dc          q6  ? ␅
    @+74754  [ 74754] dc          q7  ? before
    @+99737  [ 99737] ex          q2  ? ␅
    @+99737  [ 99737] ex          q3  ? before
    @+199812 [199812] lijm        q0  ? ␅
    @+199812 [199812] lijm        q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #956 🥳 34 ⏱️ 0:00:45.495335

🤔 34 attempts
📜 1 sessions

    @        [     0] aa         
    @+98218  [ 98218] mach       q0  ? ␅
    @+98218  [ 98218] mach       q1  ? after
    @+98218  [ 98218] mach       q2  ? ␅
    @+98218  [ 98218] mach       q3  ? after
    @+122779 [122779] parr       q6  ? ␅
    @+122779 [122779] parr       q7  ? after
    @+135070 [135070] proper     q8  ? ␅
    @+135070 [135070] proper     q9  ? after
    @+135749 [135749] provincial q16 ? ␅
    @+135749 [135749] provincial q17 ? after
    @+135826 [135826] proximate  q22 ? ␅
    @+135826 [135826] proximate  q23 ? after
    @+135834 [135834] prude      q30 ? ␅
    @+135834 [135834] prude      q31 ? after
    @+135837 [135837] prudent    q32 ? ␅
    @+135837 [135837] prudent    q33 ? it
    @+135837 [135837] prudent    done. it
    @+135844 [135844] prudish    q28 ? ␅
    @+135844 [135844] prudish    q29 ? before
    @+135863 [135863] pruning    q26 ? ␅
    @+135863 [135863] pruning    q27 ? before
    @+135899 [135899] psalm      q20 ? ␅
    @+135899 [135899] psalm      q21 ? before
    @+136052 [136052] psycho     q18 ? ␅
    @+136052 [136052] psycho     q19 ? before
    @+136429 [136429] pul        q14 ? ␅
    @+136429 [136429] pul        q15 ? before
    @+137789 [137789] quart      q12 ? ␅
    @+137789 [137789] quart      q13 ? before
    @+140518 [140518] rec        q11 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1382 🥳 6 ⏱️ 0:02:35.480678

📜 1 sessions
💰 score: 64

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:SHUSH n n n n n remain:4857
    ⬜⬜⬜⬜⬜ tried:NANNA n n n n n remain:1827
    ⬜⬜⬜⬜⬜ tried:IODID n n n n n remain:284
    ⬜⬜🟨⬜⬜ tried:CLEFT n n m n n remain:51
    ⬜🟩⬜⬜⬜ tried:PEWEE n Y n n n remain:12
    ⬜🟩⬜⬜🟩 tried:BEVVY n Y n n Y remain:8

    Undos used: 3

      8 words remaining
    x 8 unused letters
    = 64 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1525 🥳 20 ⏱️ 0:03:54.001717

📜 1 sessions
💰 score: 9600

    6/6
    AROSE 🟨⬜⬜🟩⬜
    PLASM ⬜⬜🟨🟩⬜
    TANSY ⬜🟩⬜🟩🟩
    DAISY ⬜🟩⬜🟩🟩
    GAWSY 🟩🟩⬜🟩🟩
    GASSY 🟩🟩🟩🟩🟩
    3/6
    GASSY ⬜🟨⬜🟩🟩
    ANTSY 🟩⬜🟩🟩🟩
    ARTSY 🟩🟩🟩🟩🟩
    4/6
    ARTSY 🟩🟨⬜⬜⬜
    ANGER 🟩⬜⬜⬜🟨
    ALARM 🟩⬜🟩🟩⬜
    AWARD 🟩🟩🟩🟩🟩
    5/6
    AWARD ⬜⬜⬜⬜⬜
    HOTEL ⬜⬜⬜🟨⬜
    IMBUE ⬜🟨⬜⬜🟩
    MENSE 🟨🟩⬜⬜🟩
    FEMME 🟩🟩🟩🟩🟩
    Final 2/2
    CRIMP ⬜🟩🟩🟩🟩
    PRIMP 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1502 🥳 score:22 ⏱️ 0:01:11.504127

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. CHILD attempts:4 score:4
2. VIRAL attempts:5 score:5
3. GNASH attempts:6 score:6
4. STONY attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1502 🥳 score:59 ⏱️ 0:08:07.724763

📜 1 sessions

Octordle Classic

1. SCRUM attempts:6 score:6
2. FLUTE attempts:10 score:10
3. NINJA attempts:5 score:5
4. SMELT attempts:3 score:3
5. SHACK attempts:11 score:11
6. URBAN attempts:9 score:9
7. RABBI attempts:7 score:7
8. ESTOP attempts:8 score:8

# [squareword.org](squareword.org) 🧩 #1495 🥳 7 ⏱️ 0:02:11.543611

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C H A M P
    A U D I O
    S M O T E
    T A P E S
    E N T R Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1432 🥳 213 ⏱️ 0:05:08.843217

🤔 214 attempts
📜 1 sessions
🫧 14 chat sessions
⁉️ 69 chat prompts
🤖 69 dolphin3:latest replies
🥵   9 😎  41 🥶 156 🧊   7

      $1 #214 possess         100.00°C 🥳 1000‰ ~207 used:0  [206]  source:dolphin3
      $2 #176 imbue            40.49°C 🥵  984‰  ~33 used:16 [32]   source:dolphin3
      $3 #105 innate           38.44°C 🥵  969‰  ~49 used:37 [48]   source:dolphin3
      $4 #187 impart           38.42°C 🥵  967‰  ~30 used:11 [29]   source:dolphin3
      $5 #123 endowed          37.50°C 🥵  959‰  ~34 used:17 [33]   source:dolphin3
      $6  #49 skill            37.32°C 🥵  958‰  ~48 used:33 [47]   source:dolphin3
      $7 #160 bestow           35.20°C 🥵  934‰  ~31 used:11 [30]   source:dolphin3
      $8  #50 aptitude         34.98°C 🥵  928‰  ~47 used:22 [46]   source:dolphin3
      $9 #146 trait            34.65°C 🥵  921‰  ~32 used:11 [31]   source:dolphin3
     $10 #211 inherit          34.25°C 🥵  911‰   ~1 used:0  [0]    source:dolphin3
     $11 #174 knowledge        33.08°C 😎  887‰   ~2 used:1  [1]    source:dolphin3
     $12 #179 combine          33.05°C 😎  884‰   ~3 used:1  [2]    source:dolphin3
     $52  #52 talent           24.77°C 🥶        ~54 used:0  [53]   source:dolphin3
    $208   #2 banana           -0.71°C 🧊       ~208 used:0  [207]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1465 🥳 68 ⏱️ 0:01:12.248017

🤔 69 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 16 chat prompts
🤖 16 dolphin3:latest replies
😱  1 🔥  1 🥵  6 😎 16 🥶 31 🧊 13

     $1 #69 primordial      100.00°C 🥳 1000‰ ~56 used:0 [55]  source:dolphin3
     $2 #67 essentiel        69.47°C 😱  999‰  ~1 used:0 [0]   source:dolphin3
     $3 #68 fondamental      55.04°C 🔥  994‰  ~2 used:0 [1]   source:dolphin3
     $4 #62 nécessaire       52.74°C 🥵  989‰  ~3 used:0 [2]   source:dolphin3
     $5 #61 nécessité        51.24°C 🥵  987‰  ~4 used:1 [3]   source:dolphin3
     $6 #58 impératif        47.78°C 🥵  981‰  ~6 used:5 [5]   source:dolphin3
     $7 #18 devoir           45.61°C 🥵  975‰  ~8 used:9 [7]   source:dolphin3
     $8 #50 besoin           43.32°C 🥵  957‰  ~7 used:7 [6]   source:dolphin3
     $9 #53 exigence         42.66°C 🥵  947‰  ~5 used:2 [4]   source:dolphin3
    $10 #28 potentiel        39.33°C 😎  896‰  ~9 used:0 [8]   source:dolphin3
    $11 #60 contrainte       38.07°C 😎  872‰ ~10 used:0 [9]   source:dolphin3
    $12 #26 objectif         37.89°C 😎  868‰ ~11 used:0 [10]  source:dolphin3
    $26 #21 adaptation       23.56°C 🥶       ~27 used:0 [26]  source:dolphin3
    $57 #42 récréation       -0.04°C 🧊       ~57 used:0 [56]  source:dolphin3
