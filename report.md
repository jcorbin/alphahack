# 2026-04-17

- 🔗 spaceword.org 🧩 2026-04-16 🏁 score 2173 ranked 51.2% 171/334 ⏱️ 4:43:50.725933
- 🔗 alfagok.diginaut.net 🧩 #531 🥳 18 ⏱️ 0:00:24.504664
- 🔗 alphaguess.com 🧩 #998 🥳 34 ⏱️ 0:00:45.856765
- 🔗 dontwordle.com 🧩 #1424 🥳 6 ⏱️ 0:01:08.600556
- 🔗 dictionary.com hurdle 🧩 #1567 🥳 16 ⏱️ 0:02:44.207603
- 🔗 Quordle Classic 🧩 #1544 😦 score:29 ⏱️ 0:02:16.994481
- 🔗 Octordle Classic 🧩 #1544 🥳 score:61 ⏱️ 0:03:19.449669
- 🔗 squareword.org 🧩 #1537 🥳 7 ⏱️ 0:01:38.320351
- 🔗 cemantle.certitudes.org 🧩 #1474 🥳 156 ⏱️ 0:01:46.610788
- 🔗 cemantix.certitudes.org 🧩 #1507 🥳 258 ⏱️ 0:04:20.774826

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















































# [spaceword.org](spaceword.org) 🧩 2026-04-16 🏁 score 2173 ranked 51.2% 171/334 ⏱️ 4:43:50.725933

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 171/334

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ E S T _ B _ X _ O   
      _ _ _ A P A R E J O   
      _ Q U O I N E D _ H   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #531 🥳 18 ⏱️ 0:00:24.504664

🤔 18 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199605 [199605] lij       q0  ? ␅
    @+199605 [199605] lij       q1  ? after
    @+299472 [299472] schro     q2  ? ␅
    @+299472 [299472] schro     q3  ? after
    @+311855 [311855] spier     q8  ? ␅
    @+311855 [311855] spier     q9  ? after
    @+318048 [318048] stem      q10 ? ␅
    @+318048 [318048] stem      q11 ? after
    @+321022 [321022] straat    q12 ? ␅
    @+321022 [321022] straat    q13 ? after
    @+322685 [322685] strooi    q14 ? ␅
    @+322685 [322685] strooi    q15 ? after
    @+323410 [323410] studie    q16 ? ␅
    @+323410 [323410] studie    q17 ? it
    @+323410 [323410] studie    done. it
    @+324407 [324407] subsidie  q6  ? ␅
    @+324407 [324407] subsidie  q7  ? before
    @+349453 [349453] vakantie  q4  ? ␅
    @+349453 [349453] vakantie  q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #998 🥳 34 ⏱️ 0:00:45.856765

🤔 34 attempts
📜 1 sessions

    @        [     0] aa     
    @+98216  [ 98216] mach   q0  ? ␅
    @+98216  [ 98216] mach   q1  ? after
    @+147371 [147371] rhumb  q2  ? ␅
    @+147371 [147371] rhumb  q3  ? after
    @+171636 [171636] ta     q4  ? ␅
    @+171636 [171636] ta     q5  ? after
    @+182000 [182000] un     q6  ? ␅
    @+182000 [182000] un     q7  ? after
    @+189262 [189262] vicar  q8  ? ␅
    @+189262 [189262] vicar  q9  ? after
    @+192866 [192866] whir   q10 ? ␅
    @+192866 [192866] whir   q11 ? after
    @+192942 [192942] whit   q18 ? ␅
    @+192942 [192942] whit   q19 ? after
    @+193050 [193050] who    q20 ? ␅
    @+193050 [193050] who    q21 ? after
    @+193109 [193109] whoosh q22 ? ␅
    @+193109 [193109] whoosh q23 ? after
    @+193140 [193140] whorl  q24 ? ␅
    @+193140 [193140] whorl  q25 ? after
    @+193144 [193144] whort  q30 ? ␅
    @+193144 [193144] whort  q31 ? after
    @+193150 [193150] whose  q32 ? ␅
    @+193150 [193150] whose  q33 ? it
    @+193150 [193150] whose  done. it
    @+193157 [193157] whoso  q28 ? ␅
    @+193157 [193157] whoso  q29 ? before
    @+193173 [193173] wicca  q16 ? ␅
    @+193173 [193173] wicca  q17 ? before
    @+193481 [193481] win    q15 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1424 🥳 6 ⏱️ 0:01:08.600556

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:7300
    ⬜⬜⬜⬜⬜ tried:BABAS n n n n n remain:1741
    ⬜⬜⬜⬜⬜ tried:KININ n n n n n remain:660
    ⬜⬜⬜⬜⬜ tried:CYCLO n n n n n remain:97
    ⬜⬜⬜⬜⬜ tried:JUGUM n n n n n remain:28
    🟩🟩⬜🟩⬜ tried:DEWED Y Y n Y n remain:1

    Undos used: 2

      1 words remaining
    x 6 unused letters
    = 6 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1567 🥳 16 ⏱️ 0:02:44.207603

📜 1 sessions
💰 score: 10000

    4/6
    ELANS ⬜🟨⬜⬜⬜
    DOILY ⬜🟨🟨🟨⬜
    CIBOL ⬜🟩⬜🟩🟨
    PILOT 🟩🟩🟩🟩🟩
    3/6
    PILOT ⬜⬜⬜🟨🟩
    FROST 🟩🟩🟩⬜🟩
    FRONT 🟩🟩🟩🟩🟩
    3/6
    FRONT ⬜⬜🟨⬜⬜
    COMES ⬜🟩⬜🟨⬜
    LODGE 🟩🟩🟩🟩🟩
    4/6
    LODGE ⬜🟩⬜⬜⬜
    ROAST ⬜🟩⬜🟨🟨
    FONTS ⬜🟩⬜🟩🟨
    SOUTH 🟩🟩🟩🟩🟩
    Final 2/2
    CAGEY ⬜⬜🟨🟨🟩
    GEEKY 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1544 😦 score:29 ⏱️ 0:02:16.994481

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. SMOCK attempts:7 score:7
2. _RACK -DEFGHILMNOSTWY attempts:9 score:-1
3. SAINT attempts:4 score:4
4. YIELD attempts:9 score:9

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1544 🥳 score:61 ⏱️ 0:03:19.449669

📜 1 sessions

Octordle Classic

1. COACH attempts:4 score:4
2. PARTY attempts:5 score:5
3. FOGGY attempts:12 score:12
4. STEAM attempts:9 score:9
5. MORAL attempts:8 score:8
6. BOAST attempts:6 score:6
7. PLUMP attempts:7 score:7
8. SWORE attempts:10 score:10

# [squareword.org](squareword.org) 🧩 #1537 🥳 7 ⏱️ 0:01:38.320351

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C R A P
    A R E N A
    M I T T S
    B E R E T
    A R O S E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1474 🥳 156 ⏱️ 0:01:46.610788

🤔 157 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 31 chat prompts
🤖 31 dolphin3:latest replies
🔥   4 🥵   4 😎  13 🥶 126 🧊   9

      $1 #157 lover           100.00°C 🥳 1000‰ ~148 used:0  [147]  source:dolphin3
      $2 #148 boyfriend        63.75°C 🔥  997‰   ~3 used:4  [2]    source:dolphin3
      $3 #150 girlfriend       61.41°C 🔥  996‰   ~1 used:1  [0]    source:dolphin3
      $4 #155 beau             60.94°C 🔥  995‰   ~2 used:0  [1]    source:dolphin3
      $5 #139 fiancé           59.95°C 🔥  994‰   ~4 used:5  [3]    source:dolphin3
      $6 #156 husband          52.89°C 🥵  983‰   ~5 used:0  [4]    source:dolphin3
      $7 #154 romantic         51.83°C 🥵  981‰   ~6 used:0  [5]    source:dolphin3
      $8 #135 romance          50.29°C 🥵  967‰   ~8 used:4  [7]    source:dolphin3
      $9 #131 love             48.61°C 🥵  955‰   ~7 used:1  [6]    source:dolphin3
     $10 #140 seduction        42.04°C 😎  852‰   ~9 used:0  [8]    source:dolphin3
     $11 #141 sweetheart       41.15°C 😎  819‰  ~10 used:0  [9]    source:dolphin3
     $12 #136 affair           39.17°C 😎  738‰  ~11 used:0  [10]   source:dolphin3
     $22  #80 charming         32.43°C 🥶        ~16 used:5  [15]   source:dolphin3
    $149  #48 over             -0.21°C 🧊       ~149 used:0  [148]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1507 🥳 258 ⏱️ 0:04:20.774826

🤔 259 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 55 chat prompts
🤖 55 dolphin3:latest replies
🥵  14 😎  72 🥶 132 🧊  40

      $1 #259 impact                100.00°C 🥳 1000‰ ~219 used:0  [218]  source:dolphin3
      $2 #149 évolution              48.12°C 🥵  988‰  ~86 used:34 [85]   source:dolphin3
      $3 #249 risque                 46.84°C 🥵  983‰   ~4 used:4  [3]    source:dolphin3
      $4 #239 efficacité             45.70°C 🥵  979‰   ~3 used:2  [2]    source:dolphin3
      $5 #241 analyse                43.70°C 🥵  971‰   ~1 used:1  [0]    source:dolphin3
      $6 #144 stratégie              43.26°C 🥵  968‰  ~84 used:20 [83]   source:dolphin3
      $7 #112 économique             42.46°C 🥵  964‰  ~12 used:10 [11]   source:dolphin3
      $8 #184 amélioration           42.20°C 🥵  960‰   ~9 used:7  [8]    source:dolphin3
      $9 #147 écosystème             41.23°C 🥵  953‰   ~5 used:6  [4]    source:dolphin3
     $10 #103 développement          39.96°C 🥵  946‰  ~10 used:7  [9]    source:dolphin3
     $11  #59 apport                 38.79°C 🥵  930‰  ~11 used:9  [10]   source:dolphin3
     $16 #199 processus              37.19°C 😎  898‰  ~13 used:0  [12]   source:dolphin3
     $88 #206 réseau                 24.15°C 🥶        ~95 used:0  [94]   source:dolphin3
    $220 #168 privé                  -0.51°C 🧊       ~220 used:0  [219]  source:dolphin3
