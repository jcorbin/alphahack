# 2026-06-16

- 🔗 spaceword.org 🧩 2026-06-15 🏁 score 2173 ranked 2.7% 9/335 ⏱️ 5:30:58.973860
- 🔗 alfagok.diginaut.net 🧩 #591 🥳 34 ⏱️ 0:00:45.039061
- 🔗 alphaguess.com 🧩 #1058 🥳 30 ⏱️ 0:00:32.151737
- 🔗 dontwordle.com 🧩 #1484 🥳 6 ⏱️ 0:01:23.976096
- 🔗 dictionary.com hurdle 🧩 #1627 😦 10 ⏱️ 0:02:15.624417
- 🔗 Quordle Classic 🧩 #1604 🥳 score:19 ⏱️ 0:01:08.720433
- 🔗 Octordle Classic 🧩 #1604 🥳 score:52 ⏱️ 0:02:29.872715
- 🔗 squareword.org 🧩 #1597 🥳 8 ⏱️ 0:02:09.564878
- 🔗 cemantle.certitudes.org 🧩 #1534 🥳 267 ⏱️ 0:15:00.798059
- 🔗 cemantix.certitudes.org 🧩 #1567 🥳 137 ⏱️ 0:01:45.516482

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







# [spaceword.org](spaceword.org) 🧩 2026-06-15 🏁 score 2173 ranked 2.7% 9/335 ⏱️ 5:30:58.973860

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 9/335

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ W U D _ _ _   
      _ _ _ _ _ _ I _ _ _   
      _ _ _ _ E G O _ _ _   
      _ _ _ _ X _ R _ _ _   
      _ _ _ _ U N I _ _ _   
      _ _ _ _ R _ T _ _ _   
      _ _ _ _ B Y E _ _ _   
      _ _ _ _ I _ _ _ _ _   
      _ _ _ _ A J I _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #591 🥳 34 ⏱️ 0:00:45.039061

🤔 34 attempts
📜 1 sessions

    @        [     0] &-teken 
    @+99704  [ 99704] ex      q4  ? ␅
    @+99704  [ 99704] ex      q5  ? after
    @+149390 [149390] huis    q6  ? ␅
    @+149390 [149390] huis    q7  ? after
    @+174497 [174497] kind    q8  ? ␅
    @+174497 [174497] kind    q9  ? after
    @+180689 [180689] koel    q12 ? ␅
    @+180689 [180689] koel    q13 ? after
    @+183819 [183819] kor     q14 ? ␅
    @+183819 [183819] kor     q15 ? after
    @+184488 [184488] kosten  q18 ? ␅
    @+184488 [184488] kosten  q19 ? after
    @+184711 [184711] koster  q22 ? ␅
    @+184711 [184711] koster  q23 ? after
    @+184819 [184819] kot     q24 ? ␅
    @+184819 [184819] kot     q25 ? after
    @+184867 [184867] kotter  q26 ? ␅
    @+184867 [184867] kotter  q27 ? after
    @+184883 [184883] kou     q30 ? ␅
    @+184883 [184883] kou     q31 ? after
    @+184886 [184886] koud    q32 ? ␅
    @+184886 [184886] koud    q33 ? it
    @+184886 [184886] koud    done. it
    @+184897 [184897] koude   q28 ? ␅
    @+184897 [184897] koude   q29 ? before
    @+184940 [184940] kouds   q20 ? ␅
    @+184940 [184940] kouds   q21 ? before
    @+185397 [185397] kracht  q16 ? ␅
    @+185397 [185397] kracht  q17 ? before
    @+187098 [187098] kronkel q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1058 🥳 30 ⏱️ 0:00:32.151737

🤔 30 attempts
📜 1 sessions

    @       [    0] aa        
    @+47380 [47380] dis       q2  ? ␅
    @+47380 [47380] dis       q3  ? after
    @+72797 [72797] gremolata q4  ? ␅
    @+72797 [72797] gremolata q5  ? after
    @+75952 [75952] haw       q10 ? ␅
    @+75952 [75952] haw       q11 ? after
    @+76002 [76002] hay       q20 ? ␅
    @+76002 [76002] hay       q21 ? after
    @+76040 [76040] hazan     q22 ? ␅
    @+76040 [76040] hazan     q23 ? after
    @+76043 [76043] hazard    q26 ? ␅
    @+76043 [76043] hazard    q27 ? after
    @+76048 [76048] hazardous q28 ? ␅
    @+76048 [76048] hazardous q29 ? it
    @+76048 [76048] hazardous done. it
    @+76053 [76053] haze      q24 ? ␅
    @+76053 [76053] haze      q25 ? before
    @+76079 [76079] head      q18 ? ␅
    @+76079 [76079] head      q19 ? before
    @+76287 [76287] heart     q16 ? ␅
    @+76287 [76287] heart     q17 ? before
    @+76695 [76695] helio     q14 ? ␅
    @+76695 [76695] helio     q15 ? before
    @+77496 [77496] hetero    q12 ? ␅
    @+77496 [77496] hetero    q13 ? before
    @+79128 [79128] hood      q8  ? ␅
    @+79128 [79128] hood      q9  ? before
    @+85500 [85500] ins       q6  ? ␅
    @+85500 [85500] ins       q7  ? before
    @+98214 [98214] mach      q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1484 🥳 6 ⏱️ 0:01:23.976096

📜 1 sessions
💰 score: 16

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:YUPPY n n n n n remain:7572
    ⬜⬜⬜⬜⬜ tried:IODID n n n n n remain:2366
    ⬜🟨⬜⬜⬜ tried:CRWTH n m n n n remain:337
    🟨⬜⬜🟨⬜ tried:AFARS m n n m n remain:63
    ⬜🟩⬜🟩🟩 tried:BAKER n Y n Y Y remain:15
    🟩🟩⬜🟩🟩 tried:GAGER Y Y n Y Y remain:2

    Undos used: 2

      2 words remaining
    x 8 unused letters
    = 16 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1627 😦 10 ⏱️ 0:02:15.624417

📜 1 sessions
💰 score: 1280

    4/6
    ALOES 🟨🟨⬜🟩⬜
    LADER 🟩🟩⬜🟩🟩
    LACER 🟩🟩⬜🟩🟩
    LATER 🟩🟩🟩🟩🟩
    6/6
    ????? ⬜⬜⬜🟩⬜
    ????? ⬜🟩⬜🟩🟨
    ????? ⬜🟩🟩🟩🟩
    ????? ⬜🟩🟩🟩🟩
    ????? ⬜🟩🟩🟩🟩
    ????? ⬜🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1604 🥳 score:19 ⏱️ 0:01:08.720433

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SLAIN attempts:4 score:4
2. PLUCK attempts:5 score:5
3. PINTO attempts:7 score:7
4. SLICE attempts:3 score:3

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1604 🥳 score:52 ⏱️ 0:02:29.872715

📜 1 sessions

Octordle Classic

1. ALIBI attempts:9 score:9
2. LURCH attempts:8 score:8
3. SNARL attempts:3 score:3
4. USAGE attempts:5 score:5
5. DOGMA attempts:6 score:6
6. GOODY attempts:7 score:7
7. QUILL attempts:10 score:10
8. FIRST attempts:4 score:4

# [squareword.org](squareword.org) 🧩 #1597 🥳 8 ⏱️ 0:02:09.564878

📜 2 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    M A N G O
    A W A R D
    R O D E O
    S K I E R
    H E R D S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1534 🥳 267 ⏱️ 0:15:00.798059

🤔 268 attempts
📜 1 sessions
🫧 19 chat sessions
⁉️ 89 chat prompts
🤖 89 dolphin3:latest replies
😱   1 🥵  14 😎  31 🥶 206 🧊  15

      $1 #268 impress           100.00°C 🥳 1000‰ ~253 used:0  [252]  source:dolphin3
      $2 #180 dazzle             64.00°C 😱  999‰   ~1 used:53 [0]    source:dolphin3
      $3 #181 captivate          50.88°C 🥵  988‰  ~35 used:18 [34]   source:dolphin3
      $4 #191 enthrall           50.18°C 🥵  987‰  ~13 used:8  [12]   source:dolphin3
      $5 #194 mesmerize          49.20°C 🥵  984‰   ~7 used:2  [6]    source:dolphin3
      $6 #196 entice             46.96°C 🥵  976‰   ~8 used:2  [7]    source:dolphin3
      $7 #185 astound            46.30°C 🥵  974‰   ~9 used:2  [8]    source:dolphin3
      $8 #168 bedazzle           46.14°C 🥵  972‰  ~12 used:3  [11]   source:dolphin3
      $9 #186 beguile            45.98°C 🥵  971‰  ~10 used:2  [9]    source:dolphin3
     $10 #258 spellbind          44.76°C 🥵  967‰  ~11 used:2  [10]   source:dolphin3
     $11 #208 entertain          44.33°C 🥵  964‰   ~2 used:0  [1]    source:dolphin3
     $17 #192 fascinate          38.45°C 😎  887‰  ~15 used:0  [14]   source:dolphin3
     $48 #131 reveal             25.72°C 🥶        ~51 used:0  [50]   source:dolphin3
    $254 #228 effect             -0.19°C 🧊       ~254 used:0  [253]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1567 🥳 137 ⏱️ 0:01:45.516482

🤔 138 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 25 chat prompts
🤖 25 dolphin3:latest replies
🔥  2 🥵  7 😎 31 🥶 80 🧊 17

      $1 #138 panne           100.00°C 🥳 1000‰ ~121 used:0  [120]  source:dolphin3
      $2 #103 dépanneur        46.66°C 🔥  996‰   ~5 used:11 [4]    source:dolphin3
      $3  #90 dépannage        45.76°C 🔥  995‰   ~1 used:8  [0]    source:dolphin3
      $4  #73 maintenance      41.09°C 🥵  988‰   ~7 used:5  [6]    source:dolphin3
      $5 #133 rechange         36.33°C 🥵  975‰   ~2 used:0  [1]    source:dolphin3
      $6 #108 réparateur       34.61°C 🥵  966‰   ~3 used:0  [2]    source:dolphin3
      $7  #31 alternateur      31.99°C 🥵  945‰  ~35 used:14 [34]   source:dolphin3
      $8  #69 réparation       31.50°C 🥵  940‰   ~6 used:3  [5]    source:dolphin3
      $9 #118 machine          30.34°C 🥵  927‰   ~4 used:0  [3]    source:dolphin3
     $10  #10 voiture          29.11°C 🥵  909‰  ~36 used:15 [35]   source:dolphin3
     $11  #30 électrique       27.22°C 😎  869‰  ~40 used:6  [39]   source:dolphin3
     $12  #51 commutateur      27.05°C 😎  864‰  ~37 used:2  [36]   source:dolphin3
     $42 #116 après            16.85°C 🥶        ~41 used:0  [40]   source:dolphin3
    $122  #76 tableau          -0.66°C 🧊       ~122 used:0  [121]  source:dolphin3
