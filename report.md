# 2026-01-02

- 🔗 spaceword.org 🧩 2026-01-01 🏁 score 2173 ranked 10.5% 34/323 ⏱️ 0:12:29.932648
- 🔗 alfagok.diginaut.net 🧩 #426 🥳 19 ⏱️ 0:00:47.847332
- 🔗 alphaguess.com 🧩 #892 🥳 19 ⏱️ 0:00:50.302400
- 🔗 dontwordle.com 🧩 #1319 🥳 6 ⏱️ 0:01:57.584258
- 🔗 dictionary.com hurdle 🧩 #1462 🥳 16 ⏱️ 0:03:05.271110
- 🔗 Quordle Classic 🧩 #1439 🥳 score:22 ⏱️ 0:01:19.663546
- 🔗 Octordle Classic 🧩 #1439 🥳 score:59 ⏱️ 0:03:42.032853
- 🔗 squareword.org 🧩 #1432 🥳 8 ⏱️ 0:02:40.640415
- 🔗 cemantle.certitudes.org 🧩 #1369 🥳 609 ⏱️ 0:23:16.200387
- 🔗 cemantix.certitudes.org 🧩 #1402 🥳 140 ⏱️ 0:04:57.635693
- 🔗 Quordle Rescue 🧩 #53 🥳 score:22 ⏱️ 0:01:25.495368
- 🔗 Quordle Sequence 🧩 #1439 🥳 score:25 ⏱️ 0:01:44.023226
- 🔗 Quordle Extreme 🧩 #522 😦 score:24 ⏱️ 0:01:44.383239
- 🔗 Octordle Rescue 🧩 #1439 😦 score:6 ⏱️ 0:03:47.449383
- 🔗 Octordle Sequence 🧩 #1439 🥳 score:66 ⏱️ 0:03:05.203059
- 🔗 Octordle Extreme 🧩 #1439 😦 score:57 ⏱️ 0:24:19.416618

# Dev

## WIP

- ui:
  - Handle -- stabilizing core over Listing
  - Shell -- minimizing over Handle

- meta: rework command model over Shell

## TODO

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








# spaceword.org 🧩 2026-01-01 🏁 score 2173 ranked 10.5% 34/323 ⏱️ 0:12:29.932648

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 34/323

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ E W E _ _ L U R E   
      _ _ _ E Q U A T E D   
      _ M A K I N G _ C _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #426 🥳 19 ⏱️ 0:00:47.847332

🤔 19 attempts
📜 1 sessions

    @        [     0] &-teken       
    @+1      [     1] &-tekens      
    @+2      [     2] -cijferig     
    @+3      [     3] -e-mail       
    @+49849  [ 49849] boks          q2  ? after
    @+62288  [ 62288] cement        q4  ? after
    @+65396  [ 65396] coat          q6  ? after
    @+66948  [ 66948] complet       q7  ? after
    @+67702  [ 67702] concert       q8  ? after
    @+67801  [ 67801] concertzaal   q11 ? after
    @+67849  [ 67849] concipieer    q12 ? after
    @+67861  [ 67861] concludeer    q14 ? after
    @+67865  [ 67865] concluderen   q15 ? after
    @+67867  [ 67867] concluderende q17 ? after
    @+67868  [ 67868] conclusie     q18 ? it
    @+67868  [ 67868] conclusie     done. it
    @+67869  [ 67869] conclusies    q16 ? before
    @+67873  [ 67873] concordantie  q13 ? before
    @+67903  [ 67903] concretiseren q10 ? before
    @+68109  [ 68109] conductor     q9  ? before
    @+68522  [ 68522] connectie     q5  ? before
    @+74762  [ 74762] dc            q3  ? before
    @+99758  [ 99758] ex            q1  ? before
    @+199833 [199833] lijm          q0  ? before

# alphaguess.com 🧩 #892 🥳 19 ⏱️ 0:00:50.302400

🤔 19 attempts
📜 1 sessions

    @        [     0] aa            
    @+1      [     1] aah           
    @+2      [     2] aahed         
    @+3      [     3] aahing        
    @+98224  [ 98224] mach          q0  ? after
    @+122109 [122109] par           q2  ? after
    @+134640 [134640] prog          q3  ? after
    @+140526 [140526] rec           q4  ? after
    @+143789 [143789] rem           q5  ? after
    @+145202 [145202] res           q6  ? after
    @+146261 [146261] retest        q7  ? after
    @+146477 [146477] retranslation q9  ? after
    @+146527 [146527] retro         q10 ? after
    @+146610 [146610] retrovirus    q14 ? after
    @+146612 [146612] retry         q18 ? it
    @+146612 [146612] retry         done. it
    @+146614 [146614] rets          q17 ? before
    @+146623 [146623] return        q16 ? before
    @+146650 [146650] reunifies     q15 ? before
    @+146690 [146690] rev           q8  ? before
    @+147325 [147325] rho           q1  ? before

# dontwordle.com 🧩 #1319 🥳 6 ⏱️ 0:01:57.584258

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:PAMPA n n n n n remain:5554
    ⬜⬜⬜⬜⬜ tried:ESSES n n n n n remain:1173
    ⬜⬜⬜⬜⬜ tried:JOCKO n n n n n remain:339
    ⬜⬜⬜⬜⬜ tried:FUZZY n n n n n remain:63
    ⬜🟩⬜⬜🟨 tried:VILLI n Y n n m remain:5
    🟨🟩⬜🟩⬜ tried:DIXIT m Y n Y n remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1462 🥳 16 ⏱️ 0:03:05.271110

📜 1 sessions
💰 score: 10000

    3/6
    TEALS ⬜⬜🟩🟨⬜
    GRAIL ⬜🟨🟩⬜🟨
    ALARM 🟩🟩🟩🟩🟩
    4/6
    ALARM 🟩⬜🟨⬜⬜
    ANTES 🟩🟨⬜⬜⬜
    AGONY 🟩⬜⬜🟨⬜
    AVIAN 🟩🟩🟩🟩🟩
    3/6
    AVIAN ⬜⬜⬜🟩🟩
    ROMAN 🟨🟨⬜🟩🟩
    ORGAN 🟩🟩🟩🟩🟩
    4/6
    ORGAN 🟨🟨⬜🟨⬜
    ABORT 🟨⬜🟨🟨⬜
    VAPOR ⬜🟩⬜🟨🟨
    RADIO 🟩🟩🟩🟩🟩
    Final 2/2
    BLURT 🟩🟩🟩🟩⬜
    BLURB 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1439 🥳 score:22 ⏱️ 0:01:19.663546

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SALLY attempts:4 score:4
2. INERT attempts:7 score:7
3. PINEY attempts:6 score:6
4. SOUTH attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1439 🥳 score:59 ⏱️ 0:03:42.032853

📜 1 sessions

Octordle Classic

1. VAULT attempts:11 score:11
2. BUNCH attempts:8 score:8
3. CHOCK attempts:10 score:10
4. MYRRH attempts:5 score:5
5. RINSE attempts:3 score:3
6. CHEAT attempts:9 score:9
7. MOSSY attempts:7 score:7
8. STUDY attempts:6 score:6

# squareword.org 🧩 #1432 🥳 8 ⏱️ 0:02:40.640415

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟨 🟩 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P A M S
    P O S I T
    A P P L Y
    S P E L L
    M A N S E

# cemantle.certitudes.org 🧩 #1369 🥳 609 ⏱️ 0:23:16.200387

🤔 610 attempts
📜 1 sessions
🫧 42 chat sessions
⁉️ 164 chat prompts
🤖 7 llama3.3:latest replies
🤖 25 falcon3:10b replies
🤖 132 dolphin3:latest replies
🔥   2 🥵  16 😎  87 🥶 479 🧊  25

      $1 #610   ~1 adjacent          100.00°C 🥳 1000‰
      $2 #609   ~2 vicinity           53.43°C 🔥  995‰
      $3 #458  ~32 entrance           48.03°C 🔥  991‰
      $4 #172  ~89 area               43.54°C 🥵  976‰
      $5 #467  ~29 entryway           42.31°C 🥵  971‰
      $6 #390  ~50 enclosed           42.15°C 🥵  968‰
      $7 #307  ~62 plaza              41.67°C 🥵  966‰
      $8 #312  ~59 walkway            40.92°C 🥵  958‰
      $9 #598   ~4 entranceway        40.85°C 🥵  957‰
     $10  #57 ~104 building           40.74°C 🥵  955‰
     $11 #499  ~26 corridor           40.58°C 🥵  953‰
     $20 #300  ~64 parking            35.96°C 😎  897‰
    $107 #472      hallway            23.90°C 🥶
    $586 #524      less               -0.26°C 🧊

# cemantix.certitudes.org 🧩 #1402 🥳 140 ⏱️ 0:04:57.635693

🤔 141 attempts
📜 2 sessions
🫧 9 chat sessions
⁉️ 34 chat prompts
🤖 34 dolphin3:latest replies
🔥  2 🥵  8 😎 17 🥶 51 🧊 62

      $1 #141   ~1 consensus        100.00°C 🥳 1000‰
      $2 #124  ~10 divergence        54.80°C 🔥  997‰
      $3 #125   ~9 désaccord         48.55°C 🔥  993‰
      $4 #106  ~18 opposition        43.05°C 🥵  979‰
      $5 #139   ~3 convergence       42.97°C 🥵  977‰
      $6 #130   ~6 divergent         42.63°C 🥵  974‰
      $7  #96  ~20 confrontation     42.23°C 🥵  972‰
      $8 #109  ~17 conflictuel       38.98°C 🥵  941‰
      $9 #138   ~4 accord            37.77°C 🥵  919‰
     $10 #114  ~13 opposer           37.48°C 🥵  912‰
     $11  #89  ~23 conflit           37.19°C 🥵  908‰
     $12 #116  ~12 antagonisme       36.58°C 😎  892‰
     $29 #117      contraire         23.85°C 🥶
     $80  #23      pêcheur           -0.71°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #53 🥳 score:22 ⏱️ 0:01:25.495368

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. ARBOR attempts:6 score:6
2. PRIED attempts:5 score:5
3. BISON attempts:7 score:7
4. PLACE attempts:4 score:4

# [Quordle Sequence](m-w.com/games/quordle/#/sequence) 🧩 #1439 🥳 score:25 ⏱️ 0:01:44.023226

📜 1 sessions

Quordle Sequence m-w.com/games/quordle/

1. ETUDE attempts:4 score:4
2. MUSKY attempts:6 score:6
3. GRASP attempts:7 score:7
4. CREDO attempts:8 score:8

# [Quordle Extreme](m-w.com/games/quordle/#/extreme) 🧩 #522 😦 score:24 ⏱️ 0:01:44.383239

📜 1 sessions

Quordle Extreme m-w.com/games/quordle/

1. PROUD attempts:5 score:5
2. PANTS attempts:4 score:4
3. BADLY attempts:7 score:7
4. _UROR -ABCDEIJLMNPSTWY attempts:8 score:-1

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1439 😦 score:6 ⏱️ 0:03:47.449383

📜 1 sessions

Octordle Rescue

1. ORDER attempts:3 score:6
2. EVOKE attempts:7 score:10
3. BLUER attempts:6 score:9
4. PURGE attempts:4 score:7
5. TU__E ~L -ABCDFGKNOPRSV E:1 attempts:10 score:-1
6. STEEP attempts:8 score:11
7. TRACT attempts:10 score:13
8. _O___ ~ALV -BCDEFGKNPRSTU attempts:10 score:-1

# [Octordle Sequence](britannica.com/games/octordle/daily-sequence) 🧩 #1439 🥳 score:66 ⏱️ 0:03:05.203059

📜 1 sessions

Octordle Sequence

1. STORM attempts:3 score:3
2. LUCKY attempts:6 score:6
3. BROOM attempts:7 score:7
4. THERE attempts:8 score:8
5. SPICY attempts:9 score:9
6. TABLE attempts:10 score:10
7. CUTIE attempts:11 score:11
8. LOAMY attempts:12 score:12

# [Octordle Extreme](britannica.com/games/octordle/extreme) 🧩 #1439 😦 score:57 ⏱️ 0:24:19.416618

📜 2 sessions

Octordle Extreme

1. CHIVE attempts:4 score:4
2. FERRY attempts:10 score:10
3. _O_U_ -ABCDEFGHIJKLMNRSTVWY attempts:12 score:-1
4. LUSTY attempts:7 score:7
5. BRUIN attempts:6 score:6
6. ORBIT attempts:5 score:5
7. FREER attempts:9 score:9
8. VITAL attempts:3 score:3
