# 2026-02-06

- 🔗 spaceword.org 🧩 2026-02-05 🏁 score 2173 ranked 2.3% 8/347 ⏱️ 3:40:14.155476
- 🔗 alfagok.diginaut.net 🧩 #461 🥳 38 ⏱️ 0:00:38.935573
- 🔗 alphaguess.com 🧩 #928 🥳 34 ⏱️ 0:00:45.743905
- 🔗 dontwordle.com 🧩 #1354 🥳 6 ⏱️ 0:02:30.321323
- 🔗 dictionary.com hurdle 🧩 #1497 🥳 20 ⏱️ 0:03:46.329539
- 🔗 Quordle Classic 🧩 #1474 🥳 score:19 ⏱️ 0:01:13.320242
- 🔗 Octordle Classic 🧩 #1474 🥳 score:68 ⏱️ 0:04:53.978042
- 🔗 squareword.org 🧩 #1467 🥳 7 ⏱️ 0:02:08.759121
- 🔗 cemantle.certitudes.org 🧩 #1404 🥳 344 ⏱️ 0:29:18.043608
- 🔗 cemantix.certitudes.org 🧩 #1437 🥳 22 ⏱️ 0:00:15.552372
- 🔗 Quordle Rescue 🧩 #88 🥳 score:21 ⏱️ 0:01:08.359389

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






















# [spaceword.org](spaceword.org) 🧩 2026-02-05 🏁 score 2173 ranked 2.3% 8/347 ⏱️ 3:40:14.155476

📜 7 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 8/347

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ Z _ S U B J O I N   
      _ E _ O N _ A H _ I   
      _ E Q U I T Y _ _ L   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #461 🥳 38 ⏱️ 0:00:38.935573

🤔 38 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+199826 [199826] lijm        q0  ? ␅
    @+199826 [199826] lijm        q1  ? after
    @+223772 [223772] molest      q6  ? ␅
    @+223772 [223772] molest      q7  ? after
    @+235746 [235746] odeur       q8  ? ␅
    @+235746 [235746] odeur       q9  ? after
    @+235977 [235977] oer         q16 ? ␅
    @+235977 [235977] oer         q17 ? after
    @+236201 [236201] oever       q18 ? ␅
    @+236201 [236201] oever       q19 ? after
    @+236273 [236273] offer       q20 ? ␅
    @+236273 [236273] offer       q21 ? after
    @+236347 [236347] officia     q22 ? ␅
    @+236347 [236347] officia     q23 ? after
    @+236354 [236354] officie     q28 ? ␅
    @+236354 [236354] officie     q29 ? after
    @+236355 [236355] officieel   q36 ? ␅
    @+236355 [236355] officieel   q37 ? it
    @+236355 [236355] officieel   done. it
    @+236356 [236356] officieels  q34 ? ␅
    @+236356 [236356] officieels  q35 ? before
    @+236357 [236357] officieelst q32 ? ␅
    @+236357 [236357] officieelst q33 ? before
    @+236359 [236359] officier    q30 ? ␅
    @+236359 [236359] officier    q31 ? before
    @+236362 [236362] officiers   q26 ? ␅
    @+236362 [236362] officiers   q27 ? before
    @+236390 [236390] offreer     q24 ? ␅
    @+236390 [236390] offreer     q25 ? before
    @+236433 [236433] ogen        q15 ? before

# [alphaguess.com](alphaguess.com) 🧩 #928 🥳 34 ⏱️ 0:00:45.743905

🤔 34 attempts
📜 1 sessions

    @       [    0] aa          
    @+23683 [23683] camp        q6  ? ␅
    @+23683 [23683] camp        q7  ? after
    @+29604 [29604] circuit     q10 ? ␅
    @+29604 [29604] circuit     q11 ? after
    @+32553 [32553] color       q12 ? ␅
    @+32553 [32553] color       q13 ? after
    @+33110 [33110] common      q16 ? ␅
    @+33110 [33110] common      q17 ? after
    @+33236 [33236] comp        q20 ? ␅
    @+33236 [33236] comp        q21 ? after
    @+33276 [33276] comparative q24 ? ␅
    @+33276 [33276] comparative q25 ? after
    @+33292 [33292] compart     q26 ? ␅
    @+33292 [33292] compart     q27 ? after
    @+33302 [33302] compas      q28 ? ␅
    @+33302 [33302] compas      q29 ? after
    @+33304 [33304] compass     q30 ? ␅
    @+33304 [33304] compass     q31 ? after
    @+33309 [33309] compassion  q32 ? ␅
    @+33309 [33309] compassion  q33 ? it
    @+33309 [33309] compassion  done. it
    @+33319 [33319] compatible  q22 ? ␅
    @+33319 [33319] compatible  q23 ? before
    @+33399 [33399] complain    q18 ? ␅
    @+33399 [33399] complain    q19 ? before
    @+33701 [33701] con         q14 ? ␅
    @+33701 [33701] con         q15 ? before
    @+35526 [35526] convention  q8  ? ␅
    @+35526 [35526] convention  q9  ? before
    @+47382 [47382] dis         q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1354 🥳 6 ⏱️ 0:02:30.321323

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:SHUSH n n n n n remain:4857
    ⬜⬜⬜⬜⬜ tried:BABKA n n n n n remain:1889
    ⬜⬜⬜⬜⬜ tried:INFIX n n n n n remain:640
    ⬜⬜⬜⬜⬜ tried:OVOLO n n n n n remain:134
    ⬜🟨⬜⬜⬜ tried:CEDED n m n n n remain:5
    🟨⬜🟨⬜🟨 tried:TWERP m n m n m remain:1

    Undos used: 4

      1 words remaining
    x 6 unused letters
    = 6 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1497 🥳 20 ⏱️ 0:03:46.329539

📜 1 sessions
💰 score: 9600

    3/6
    STORE 🟨⬜⬜⬜⬜
    LUNAS 🟨🟨⬜⬜🟨
    BLUSH 🟩🟩🟩🟩🟩
    6/6
    BLUSH ⬜⬜⬜🟨⬜
    RAPES ⬜⬜⬜⬜🟨
    SONIC 🟩🟨🟨⬜⬜
    STONK 🟩⬜🟩🟨⬜
    SNOWY 🟩🟨🟩🟨⬜
    SWOON 🟩🟩🟩🟩🟩
    4/6
    SWOON ⬜⬜⬜⬜⬜
    LATER ⬜⬜⬜🟩⬜
    CHIEF 🟨⬜⬜🟩⬜
    EMCEE 🟩🟩🟩🟩🟩
    5/6
    EMCEE 🟨⬜⬜🟨⬜
    YEARN 🟨🟩⬜⬜⬜
    LEFTY ⬜🟩🟨⬜🟩
    DEIFY ⬜🟩⬜🟩🟩
    BEEFY 🟩🟩🟩🟩🟩
    Final 2/2
    NIGHT 🟨🟨🟨🟨🟨
    THING 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1474 🥳 score:19 ⏱️ 0:01:13.320242

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. RESIN attempts:4 score:4
2. CRUMP attempts:7 score:7
3. RIGOR attempts:5 score:5
4. ETHOS attempts:3 score:3

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1474 🥳 score:68 ⏱️ 0:04:53.978042

📜 1 sessions

Octordle Classic

1. AZURE attempts:9 score:9
2. ASSET attempts:10 score:10
3. SNIDE attempts:11 score:11
4. THREE attempts:8 score:8
5. RARER attempts:7 score:7
6. SMOKE attempts:6 score:6
7. GAILY attempts:4 score:4
8. WITTY attempts:13 score:13

# [squareword.org](squareword.org) 🧩 #1467 🥳 7 ⏱️ 0:02:08.759121

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟨
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    M A C A W
    A R O M A
    D E M U R
    A N I S E
    M A C E S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1404 🥳 344 ⏱️ 0:29:18.043608

🤔 345 attempts
📜 11 sessions
🫧 25 chat sessions
⁉️ 112 chat prompts
🤖 94 dolphin3:latest replies
🤖 18 qwen3:14b replies
🔥   5 🥵  20 😎  41 🥶 261 🧊  17

      $1 #345 literacy         100.00°C 🥳 1000‰ ~328 used:0   [327]  source:dolphin3
      $2 #205 education         59.38°C 🔥  998‰  ~21 used:57  [20]   source:qwen3   
      $3  #23 math              53.74°C 🔥  997‰  ~65 used:101 [64]   source:dolphin3
      $4 #259 educational       53.37°C 🔥  996‰   ~4 used:20  [3]    source:dolphin3
      $5 #134 mathematics       51.41°C 🔥  995‰  ~20 used:39  [19]   source:dolphin3
      $6 #203 curriculum        47.96°C 🔥  992‰   ~3 used:16  [2]    source:qwen3   
      $7  #41 algebra           42.24°C 🥵  983‰  ~66 used:20  [65]   source:dolphin3
      $8 #211 teaching          42.04°C 🥵  981‰   ~5 used:2   [4]    source:qwen3   
      $9 #344 numeracy          41.74°C 🥵  980‰   ~1 used:1   [0]    source:dolphin3
     $10 #201 learning          40.51°C 🥵  977‰   ~6 used:2   [5]    source:qwen3   
     $11  #72 arithmetic        38.86°C 🥵  968‰  ~23 used:8   [22]   source:dolphin3
     $27 #231 graduation        31.93°C 😎  895‰  ~24 used:0   [23]   source:dolphin3
     $68  #40 yoga              19.90°C 🥶        ~67 used:0   [66]   source:dolphin3
    $329 #146 convex            -0.32°C 🧊       ~329 used:0   [328]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1437 🥳 22 ⏱️ 0:00:15.552372

🤔 23 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 4 chat prompts
🤖 4 dolphin3:latest replies
🥵  1 😎  4 🥶  7 🧊 10

     $1 #23 bibliothèque   100.00°C 🥳 1000‰ ~13 used:0 [12]  source:dolphin3
     $2  #6 livre           41.28°C 🥵  972‰  ~1 used:5 [0]   source:dolphin3
     $3 #14 édition         25.34°C 😎  770‰  ~2 used:1 [1]   source:dolphin3
     $4 #12 auteur          20.56°C 😎  568‰  ~3 used:0 [2]   source:dolphin3
     $5 #19 index           19.67°C 😎  498‰  ~4 used:0 [3]   source:dolphin3
     $6 #18 illustration    18.01°C 😎  318‰  ~5 used:0 [4]   source:dolphin3
     $7 #13 roman           14.80°C 🥶        ~6 used:0 [5]   source:dolphin3
     $8 #16 chapitre        14.20°C 🥶        ~7 used:0 [6]   source:dolphin3
     $9 #20 page            13.80°C 🥶        ~8 used:0 [7]   source:dolphin3
    $10 #17 couverture      10.31°C 🥶        ~9 used:0 [8]   source:dolphin3
    $11  #2 book             9.02°C 🥶       ~10 used:0 [9]   source:dolphin3
    $12 #22 anthologie       9.02°C 🥶       ~11 used:0 [10]  source:dolphin3
    $13 #21 paragraphe       5.71°C 🥶       ~12 used:0 [11]  source:dolphin3
    $14  #5 fleur           -1.66°C 🧊       ~14 used:0 [13]  source:dolphin3

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #88 🥳 score:21 ⏱️ 0:01:08.359389

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. TUNIC attempts:3 score:3
2. BIGOT attempts:7 score:7
3. SWOON attempts:5 score:5
4. POUCH attempts:6 score:6
