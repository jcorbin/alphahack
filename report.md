# 2026-04-13

- 🔗 spaceword.org 🧩 2026-04-12 🏁 score 2173 ranked 11.3% 38/335 ⏱️ 7:16:51.786267
- 🔗 alfagok.diginaut.net 🧩 #527 🥳 32 ⏱️ 0:00:59.382494
- 🔗 alphaguess.com 🧩 #994 🥳 30 ⏱️ 0:00:32.558828
- 🔗 dontwordle.com 🧩 #1420 🥳 6 ⏱️ 0:01:04.712097
- 🔗 dictionary.com hurdle 🧩 #1563 🥳 15 ⏱️ 0:02:44.224924
- 🔗 Quordle Classic 🧩 #1540 🥳 score:23 ⏱️ 0:01:14.880743
- 🔗 Octordle Classic 🧩 #1540 🥳 score:53 ⏱️ 0:02:52.497138
- 🔗 squareword.org 🧩 #1533 🥳 9 ⏱️ 0:02:17.168631
- 🔗 cemantle.certitudes.org 🧩 #1470 🥳 382 ⏱️ 0:37:11.485705
- 🔗 cemantix.certitudes.org 🧩 #1503 🥳 193 ⏱️ 0:28:03.507035

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











































# [spaceword.org](spaceword.org) 🧩 2026-04-12 🏁 score 2173 ranked 11.3% 38/335 ⏱️ 7:16:51.786267

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 38/335

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ D _ E C O Z O N E   
      _ U _ M O _ _ E A R   
      _ B L E W I T _ V _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #527 🥳 32 ⏱️ 0:00:59.382494

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+199605 [199605] lij         q0  ? ␅
    @+199605 [199605] lij         q1  ? after
    @+199605 [199605] lij         q2  ? ␅
    @+199605 [199605] lij         q3  ? after
    @+299473 [299473] schro       q4  ? ␅
    @+299473 [299473] schro       q5  ? after
    @+324408 [324408] subsidie    q8  ? ␅
    @+324408 [324408] subsidie    q9  ? after
    @+335598 [335598] toe         q10 ? ␅
    @+335598 [335598] toe         q11 ? after
    @+342504 [342504] tunnel      q12 ? ␅
    @+342504 [342504] tunnel      q13 ? after
    @+344108 [344108] uit         q14 ? ␅
    @+344108 [344108] uit         q15 ? after
    @+344440 [344440] uitdeden    q22 ? ␅
    @+344440 [344440] uitdeden    q23 ? after
    @+344606 [344606] uitdrupte   q24 ? ␅
    @+344606 [344606] uitdrupte   q25 ? after
    @+344627 [344627] uiteen      q26 ? ␅
    @+344627 [344627] uiteen      q27 ? after
    @+344700 [344700] uiteenval   q28 ? ␅
    @+344700 [344700] uiteenval   q29 ? after
    @+344737 [344737] uiterst     q30 ? ␅
    @+344737 [344737] uiterst     q31 ? it
    @+344737 [344737] uiterst     done. it
    @+344771 [344771] uitga       q20 ? ␅
    @+344771 [344771] uitga       q21 ? before
    @+345442 [345442] uitgestoten q18 ? ␅
    @+345442 [345442] uitgestoten q19 ? before
    @+346776 [346776] uitschreeuw q17 ? before

# [alphaguess.com](alphaguess.com) 🧩 #994 🥳 30 ⏱️ 0:00:32.558828

🤔 30 attempts
📜 1 sessions

    @        [     0] aa           
    @+98216  [ 98216] mach         q0  ? ␅
    @+98216  [ 98216] mach         q1  ? after
    @+122777 [122777] parr         q4  ? ␅
    @+122777 [122777] parr         q5  ? after
    @+135068 [135068] proper       q6  ? ␅
    @+135068 [135068] proper       q7  ? after
    @+140516 [140516] rec          q8  ? ␅
    @+140516 [140516] rec          q9  ? after
    @+143940 [143940] reminisce    q10 ? ␅
    @+143940 [143940] reminisce    q11 ? after
    @+144412 [144412] rep          q14 ? ␅
    @+144412 [144412] rep          q15 ? after
    @+144601 [144601] replace      q18 ? ␅
    @+144601 [144601] replace      q19 ? after
    @+144700 [144700] replumb      q20 ? ␅
    @+144700 [144700] replumb      q21 ? after
    @+144710 [144710] repo         q22 ? ␅
    @+144710 [144710] repo         q23 ? after
    @+144729 [144729] repopularize q26 ? ␅
    @+144729 [144729] repopularize q27 ? after
    @+144739 [144739] report       q28 ? ␅
    @+144739 [144739] report       q29 ? it
    @+144739 [144739] report       done. it
    @+144752 [144752] repos        q24 ? ␅
    @+144752 [144752] repos        q25 ? before
    @+144802 [144802] repp         q16 ? ␅
    @+144802 [144802] repp         q17 ? before
    @+145192 [145192] res          q12 ? ␅
    @+145192 [145192] res          q13 ? before
    @+147371 [147371] rhumb        q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1420 🥳 6 ⏱️ 0:01:04.712097

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:PENNE n n n n n remain:4618
    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:2437
    ⬜⬜⬜⬜⬜ tried:MOMMY n n n n n remain:734
    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:175
    🟨⬜⬜⬜⬜ tried:ADDAX m n n n n remain:65
    ⬜⬜🟩🟨⬜ tried:WHARF n n Y m n remain:1

    Undos used: 2

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1563 🥳 15 ⏱️ 0:02:44.224924

📜 1 sessions
💰 score: 10100

    3/6
    EYRAS ⬜🟨🟨⬜⬜
    ROUPY 🟨🟨⬜🟨🟩
    PROXY 🟩🟩🟩🟩🟩
    4/6
    PROXY ⬜🟩⬜⬜⬜
    ARISE ⬜🟩⬜🟩⬜
    CRUST ⬜🟩🟩🟩⬜
    BRUSH 🟩🟩🟩🟩🟩
    4/6
    BRUSH ⬜🟨⬜⬜⬜
    RATIO 🟨⬜🟩🟨⬜
    NITRE ⬜🟨🟩🟩🟨
    PETRI 🟩🟩🟩🟩🟩
    3/6
    PETRI 🟨⬜⬜🟨🟨
    CRISP ⬜🟨🟨⬜🟨
    RAPID 🟩🟩🟩🟩🟩
    Final 1/2
    PUPPY 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1540 🥳 score:23 ⏱️ 0:01:14.880743

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. INCUR attempts:3 score:3
2. FLAKE attempts:7 score:7
3. FLASK attempts:8 score:8
4. WORDY attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1540 🥳 score:53 ⏱️ 0:02:52.497138

📜 1 sessions

Octordle Classic

1. MUSKY attempts:9 score:9
2. SLOSH attempts:8 score:8
3. SWIRL attempts:4 score:4
4. TASTE attempts:5 score:5
5. IMBUE attempts:6 score:6
6. RUDER attempts:11 score:11
7. STEIN attempts:3 score:3
8. ABUSE attempts:7 score:7

# [squareword.org](squareword.org) 🧩 #1533 🥳 9 ⏱️ 0:02:17.168631

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟩
    🟩 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C A R F
    L A G E R
    E R A S E
    D R I E S
    S Y N T H

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1470 🥳 382 ⏱️ 0:37:11.485705

🤔 383 attempts
📜 1 sessions
🫧 42 chat sessions
⁉️ 197 chat prompts
🤖 11 llama3.1:8b replies
🤖 49 gemma3:27b replies
🤖 17 gpt-oss:20b replies
🤖 120 dolphin3:latest replies
🔥   6 🥵  24 😎  69 🥶 273 🧊  10

      $1 #383 mere              100.00°C 🥳 1000‰ ~373 used:0   [372]  source:llama3  
      $2 #193 measly             57.50°C 🔥  998‰  ~99 used:123 [98]   source:dolphin3
      $3 #100 trifling           55.14°C 🔥  997‰  ~98 used:118 [97]   source:dolphin3
      $4  #92 paltry             52.29°C 🔥  995‰  ~28 used:61  [27]   source:dolphin3
      $5  #84 insignificant      49.05°C 🔥  993‰   ~1 used:31  [0]    source:dolphin3
      $6  #98 inconsequential    48.94°C 🔥  992‰   ~2 used:31  [1]    source:dolphin3
      $7 #147 piddling           48.27°C 🔥  991‰   ~3 used:31  [2]    source:dolphin3
      $8 #222 scant              47.20°C 🔥  990‰   ~4 used:31  [3]    source:dolphin3
      $9 #263 minuscule          46.74°C 🥵  989‰   ~5 used:4   [4]    source:dolphin3
     $10  #83 trivial            45.84°C 🥵  988‰   ~6 used:4   [5]    source:dolphin3
     $11 #367 meaningless        45.66°C 🥵  987‰   ~7 used:4   [6]    source:llama3  
     $32 #309 picayune           35.66°C 😎  897‰  ~29 used:0   [28]   source:gemma3  
    $101 #164 scanty             26.69°C 🥶       ~108 used:0   [107]  source:dolphin3
    $374   #5 pottery            -1.00°C 🧊       ~374 used:0   [373]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1503 🥳 193 ⏱️ 0:28:03.507035

🤔 194 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 33 chat prompts
🤖 33 dolphin3:latest replies
🔥   1 🥵  12 😎  39 🥶 114 🧊  27

      $1 #194 progressif        100.00°C 🥳 1000‰ ~167 used:0  [166]  source:dolphin3
      $2 #118 évolution          47.19°C 🔥  990‰   ~4 used:28 [3]    source:dolphin3
      $3 #191 accélération       45.15°C 🥵  983‰   ~5 used:3  [4]    source:dolphin3
      $4 #126 progression        44.07°C 🥵  982‰  ~51 used:12 [50]   source:dolphin3
      $5 #122 diversification    42.05°C 🥵  974‰  ~11 used:6  [10]   source:dolphin3
      $6 #115 transition         42.04°C 🥵  973‰   ~6 used:3  [5]    source:dolphin3
      $7 #187 renforcement       41.17°C 🥵  964‰   ~7 used:3  [6]    source:dolphin3
      $8 #188 consolidation      40.57°C 🥵  954‰   ~2 used:2  [1]    source:dolphin3
      $9 #120 transformation     40.14°C 🥵  949‰   ~8 used:3  [7]    source:dolphin3
     $10 #100 adaptation         39.26°C 🥵  940‰   ~9 used:3  [8]    source:dolphin3
     $11  #29 niveau             38.31°C 🥵  932‰  ~50 used:11 [49]   source:dolphin3
     $14  #84 approche           36.89°C 😎  899‰   ~3 used:2  [2]    source:dolphin3
     $54 #153 paradigme          24.34°C 🥶        ~56 used:0  [55]   source:dolphin3
    $168  #45 vidanger           -0.18°C 🧊       ~168 used:0  [167]  source:dolphin3
