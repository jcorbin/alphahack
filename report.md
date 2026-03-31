# 2026-04-01

- 🔗 spaceword.org 🧩 2026-03-31 🏁 score 2173 ranked 5.9% 21/355 ⏱️ 0:23:59.200934
- 🔗 alfagok.diginaut.net 🧩 #515 🥳 22 ⏱️ 0:00:23.479520
- 🔗 alphaguess.com 🧩 #982 🥳 18 ⏱️ 0:00:22.487431
- 🔗 dontwordle.com 🧩 #1408 🥳 6 ⏱️ 0:01:41.407965
- 🔗 dictionary.com hurdle 🧩 #1551 🥳 19 ⏱️ 0:03:53.409795
- 🔗 Quordle Classic 🧩 #1528 🥳 score:21 ⏱️ 0:01:30.496389
- 🔗 Octordle Classic 🧩 #1528 🥳 score:55 ⏱️ 0:03:07.080821
- 🔗 squareword.org 🧩 #1521 🥳 7 ⏱️ 0:01:45.615979
- 🔗 cemantle.certitudes.org 🧩 #1458 🥳 278 ⏱️ 0:06:11.875545
- 🔗 cemantix.certitudes.org 🧩 #1491 🥳 237 ⏱️ 0:06:52.493728

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































# [spaceword.org](spaceword.org) 🧩 2026-03-31 🏁 score 2173 ranked 5.9% 21/355 ⏱️ 0:23:59.200934

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 21/355

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ V _ _ F A J I T A   
      _ A R I O S O _ O I   
      _ W _ T Y P E D _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #515 🥳 22 ⏱️ 0:00:23.479520

🤔 22 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199809 [199809] lijm      q0  ? ␅
    @+199809 [199809] lijm      q1  ? after
    @+199809 [199809] lijm      q2  ? ␅
    @+199809 [199809] lijm      q3  ? after
    @+223743 [223743] molest    q8  ? ␅
    @+223743 [223743] molest    q9  ? after
    @+229599 [229599] natuur    q12 ? ␅
    @+229599 [229599] natuur    q13 ? after
    @+230357 [230357] naïeve    q18 ? ␅
    @+230357 [230357] naïeve    q19 ? after
    @+230558 [230558] neer      q20 ? ␅
    @+230558 [230558] neer      q21 ? it
    @+230558 [230558] neer      done. it
    @+231121 [231121] neig      q16 ? ␅
    @+231121 [231121] neig      q17 ? before
    @+232646 [232646] nieuw     q14 ? ␅
    @+232646 [232646] nieuw     q15 ? before
    @+235718 [235718] odieus    q10 ? ␅
    @+235718 [235718] odieus    q11 ? before
    @+247693 [247693] op        q6  ? ␅
    @+247693 [247693] op        q7  ? before
    @+299696 [299696] schub     q4  ? ␅
    @+299696 [299696] schub     q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #982 🥳 18 ⏱️ 0:00:22.487431

🤔 18 attempts
📜 1 sessions

    @        [     0] aa     
    @+1      [     1] aah    
    @+2      [     2] aahed  
    @+3      [     3] aahing 
    @+98216  [ 98216] mach   q0  ? ␅
    @+98216  [ 98216] mach   q1  ? after
    @+147371 [147371] rhumb  q2  ? ␅
    @+147371 [147371] rhumb  q3  ? after
    @+159483 [159483] slop   q6  ? ␅
    @+159483 [159483] slop   q7  ? after
    @+159844 [159844] smell  q16 ? ␅
    @+159844 [159844] smell  q17 ? it
    @+159844 [159844] smell  done. it
    @+160222 [160222] snath  q14 ? ␅
    @+160222 [160222] snath  q15 ? before
    @+160962 [160962] soft   q12 ? ␅
    @+160962 [160962] soft   q13 ? before
    @+162470 [162470] spec   q10 ? ␅
    @+162470 [162470] spec   q11 ? before
    @+165525 [165525] stick  q8  ? ␅
    @+165525 [165525] stick  q9  ? before
    @+171636 [171636] ta     q4  ? ␅
    @+171636 [171636] ta     q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1408 🥳 6 ⏱️ 0:01:41.407965

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:BACCA n n n n n remain:5655
    ⬜⬜⬜⬜⬜ tried:DOGGO n n n n n remain:2333
    ⬜⬜⬜⬜⬜ tried:TITTY n n n n n remain:600
    ⬜⬜⬜⬜⬜ tried:HUMPH n n n n n remain:169
    ⬜⬜🟩⬜⬜ tried:FEEZE n n Y n n remain:10
    ⬜⬜🟩🟩🟩 tried:KNELL n n Y Y Y remain:1

    Undos used: 2

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1551 🥳 19 ⏱️ 0:03:53.409795

📜 1 sessions
💰 score: 9700

    4/6
    TARES ⬜🟨⬜🟨⬜
    BLADE ⬜🟨🟨🟨🟨
    DECAL 🟨🟩⬜🟩🟩
    MEDAL 🟩🟩🟩🟩🟩
    5/6
    MEDAL ⬜⬜⬜⬜⬜
    RIOTS ⬜🟨⬜🟨🟨
    STINK 🟩🟩🟩⬜⬜
    STICH 🟩🟩🟩⬜⬜
    STIFF 🟩🟩🟩🟩🟩
    4/6
    STIFF 🟨🟨🟩⬜⬜
    WRITS ⬜⬜🟩🟨🟨
    HOIST ⬜🟩🟩🟩🟩
    MOIST 🟩🟩🟩🟩🟩
    4/6
    MOIST ⬜🟨⬜🟨🟨
    STORE 🟨🟨🟨⬜⬜
    AUTOS ⬜🟩🟨🟨🟨
    GUSTO 🟩🟩🟩🟩🟩
    Final 2/2
    RIVEN ⬜🟩⬜🟩⬜
    BICEP 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1528 🥳 score:21 ⏱️ 0:01:30.496389

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SEVEN attempts:5 score:5
2. PRIOR attempts:6 score:6
3. ADAGE attempts:7 score:7
4. AUDIO attempts:3 score:3

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1528 🥳 score:55 ⏱️ 0:03:07.080821

📜 1 sessions

Octordle Classic

1. FROTH attempts:11 score:11
2. SONIC attempts:4 score:4
3. CHAFF attempts:10 score:10
4. WIDOW attempts:9 score:9
5. DENIM attempts:7 score:7
6. TIARA attempts:6 score:6
7. TOUGH attempts:5 score:5
8. RIDGE attempts:3 score:3

# [squareword.org](squareword.org) 🧩 #1521 🥳 7 ⏱️ 0:01:45.615979

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P S A L M
    R A D I O
    I R O N S
    O G R E S
    R E E D Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1458 🥳 278 ⏱️ 0:06:11.875545

🤔 279 attempts
📜 1 sessions
🫧 12 chat sessions
⁉️ 59 chat prompts
🤖 59 dolphin3:latest replies
😱   1 🔥   1 🥵   2 😎   9 🥶 228 🧊  37

      $1 #279 amazon           100.00°C 🥳 1000‰ ~242 used:0  [241]  source:dolphin3
      $2 #261 os                51.30°C 😱  999‰   ~1 used:6  [0]    source:dolphin3
      $3 #225 google            45.51°C 🔥  992‰   ~2 used:20 [1]    source:dolphin3
      $4 #228 android           39.26°C 🥵  959‰   ~4 used:6  [3]    source:dolphin3
      $5 #236 tv                37.22°C 🥵  937‰   ~3 used:4  [2]    source:dolphin3
      $6 #244 ai                30.33°C 😎  636‰   ~5 used:0  [4]    source:dolphin3
      $7  #31 download          30.28°C 😎  631‰  ~13 used:44 [12]   source:dolphin3
      $8 #192 shortener         28.27°C 😎  434‰   ~7 used:13 [6]    source:dolphin3
      $9  #93 online            28.11°C 😎  402‰  ~12 used:21 [11]   source:dolphin3
     $10   #6 internet          28.10°C 😎  401‰   ~8 used:14 [7]    source:dolphin3
     $11 #220 browsing          27.90°C 😎  378‰   ~6 used:1  [5]    source:dolphin3
     $12  #13 browser           27.77°C 😎  363‰   ~9 used:14 [8]    source:dolphin3
     $15  #81 web               25.40°C 🥶        ~14 used:0  [13]   source:dolphin3
    $243 #121 survey            -0.14°C 🧊       ~243 used:0  [242]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1491 🥳 237 ⏱️ 0:06:52.493728

🤔 238 attempts
📜 1 sessions
🫧 18 chat sessions
⁉️ 88 chat prompts
🤖 88 dolphin3:latest replies
😱   1 🔥   3 🥵  21 😎  41 🥶 133 🧊  38

      $1 #238 amoureux            100.00°C 🥳 1000‰ ~200 used:0   [199]  source:dolphin3
      $2 #112 amour                68.69°C 😱  999‰  ~13 used:104 [12]   source:dolphin3
      $3 #157 amant                64.28°C 🔥  998‰  ~25 used:36  [24]   source:dolphin3
      $4 #151 aimer                56.81°C 🔥  995‰  ~15 used:19  [14]   source:dolphin3
      $5 #125 tendresse            53.11°C 🔥  990‰  ~14 used:11  [13]   source:dolphin3
      $6 #221 charmant             52.00°C 🥵  988‰  ~16 used:2   [15]   source:dolphin3
      $7 #122 idylle               51.14°C 🥵  986‰  ~17 used:2   [16]   source:dolphin3
      $8 #187 charme               51.08°C 🥵  985‰  ~18 used:2   [17]   source:dolphin3
      $9 #118 passion              50.38°C 🥵  982‰  ~19 used:2   [18]   source:dolphin3
     $10 #220 charmer              50.27°C 🥵  981‰  ~20 used:2   [19]   source:dolphin3
     $11 #116 couple               48.98°C 🥵  977‰  ~21 used:2   [20]   source:dolphin3
     $27 #181 infidélité           41.52°C 😎  893‰  ~26 used:0   [25]   source:dolphin3
     $68  #88 fidèle               29.00°C 🥶        ~74 used:0   [73]   source:dolphin3
    $201  #42 culture              -0.19°C 🧊       ~201 used:0   [200]  source:dolphin3

