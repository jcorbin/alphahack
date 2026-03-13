# 2026-03-14

- 🔗 spaceword.org 🧩 2026-03-13 🏁 score 2173 ranked 9.9% 33/332 ⏱️ 3:18:53.143598
- 🔗 alfagok.diginaut.net 🧩 #497 🥳 26 ⏱️ 0:00:34.135137
- 🔗 alphaguess.com 🧩 #964 🥳 36 ⏱️ 0:00:32.551359
- 🔗 dontwordle.com 🧩 #1390 🥳 6 ⏱️ 0:01:11.991024
- 🔗 dictionary.com hurdle 🧩 #1533 🥳 18 ⏱️ 0:02:49.288631
- 🔗 Quordle Classic 🧩 #1510 🥳 score:23 ⏱️ 0:01:30.905097
- 🔗 Octordle Classic 🧩 #1510 😦 score:75 ⏱️ 0:05:12.734815
- 🔗 squareword.org 🧩 #1503 🥳 8 ⏱️ 0:02:04.215821
- 🔗 cemantle.certitudes.org 🧩 #1440 🥳 218 ⏱️ 0:17:25.947416
- 🔗 cemantix.certitudes.org 🧩 #1473 🥳 293 ⏱️ 0:18:32.365894

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













# [spaceword.org](spaceword.org) 🧩 2026-03-13 🏁 score 2173 ranked 9.9% 33/332 ⏱️ 3:18:53.143598

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 33/332

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ J _ B E M I X E S   
      _ E _ O _ _ R _ N U   
      _ T A G L I K E _ E   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #497 🥳 26 ⏱️ 0:00:34.135137

🤔 26 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199609 [199609] lij       q0  ? ␅
    @+199609 [199609] lij       q1  ? after
    @+199609 [199609] lij       q2  ? ␅
    @+199609 [199609] lij       q3  ? after
    @+299483 [299483] schro     q4  ? ␅
    @+299483 [299483] schro     q5  ? after
    @+349467 [349467] vakantie  q6  ? ␅
    @+349467 [349467] vakantie  q7  ? after
    @+374207 [374207] vrij      q8  ? ␅
    @+374207 [374207] vrij      q9  ? after
    @+386744 [386744] wind      q10 ? ␅
    @+386744 [386744] wind      q11 ? after
    @+388334 [388334] woest     q16 ? ␅
    @+388334 [388334] woest     q17 ? after
    @+388412 [388412] wol       q20 ? ␅
    @+388412 [388412] wol       q21 ? after
    @+388693 [388693] wonder    q22 ? ␅
    @+388693 [388693] wonder    q23 ? after
    @+388841 [388841] woning    q24 ? ␅
    @+388841 [388841] woning    q25 ? it
    @+388841 [388841] woning    done. it
    @+389006 [389006] woon      q18 ? ␅
    @+389006 [389006] woon      q19 ? before
    @+389953 [389953] wrik      q14 ? ␅
    @+389953 [389953] wrik      q15 ? before
    @+393161 [393161] zelfmoord q12 ? ␅
    @+393161 [393161] zelfmoord q13 ? before

# [alphaguess.com](alphaguess.com) 🧩 #964 🥳 36 ⏱️ 0:00:32.551359

🤔 36 attempts
📜 1 sessions

    @       [    0] aa         
    @+47381 [47381] dis        q4  ? ␅
    @+47381 [47381] dis        q5  ? after
    @+49428 [49428] do         q12 ? ␅
    @+49428 [49428] do         q13 ? after
    @+51402 [51402] drunk      q14 ? ␅
    @+51402 [51402] drunk      q15 ? after
    @+51896 [51896] dupe       q18 ? ␅
    @+51896 [51896] dupe       q19 ? after
    @+52147 [52147] dyke       q20 ? ␅
    @+52147 [52147] dyke       q21 ? after
    @+52271 [52271] dysprosium q22 ? ␅
    @+52271 [52271] dysprosium q23 ? after
    @+52324 [52324] ear        q24 ? ␅
    @+52324 [52324] ear        q25 ? after
    @+52342 [52342] earl       q26 ? ␅
    @+52342 [52342] earl       q27 ? after
    @+52356 [52356] earls      q30 ? ␅
    @+52356 [52356] earls      q31 ? after
    @+52359 [52359] early      q34 ? ␅
    @+52359 [52359] early      q35 ? it
    @+52359 [52359] early      done. it
    @+52362 [52362] earmark    q32 ? ␅
    @+52362 [52362] earmark    q33 ? before
    @+52368 [52368] earn       q28 ? ␅
    @+52368 [52368] earn       q29 ? before
    @+52395 [52395] earth      q16 ? ␅
    @+52395 [52395] earth      q17 ? before
    @+53397 [53397] el         q10 ? ␅
    @+53397 [53397] el         q11 ? before
    @+60084 [60084] face       q9  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1390 🥳 6 ⏱️ 0:01:11.991024

📜 1 sessions
💰 score: 15

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:PEEVE n n n n n remain:5924
    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:2873
    ⬜⬜⬜⬜⬜ tried:DUSKS n n n n n remain:603
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:262
    ⬜⬜⬜⬜⬜ tried:CRWTH n n n n n remain:30
    ⬜🟩🟩⬜⬜ tried:MINIM n Y Y n n remain:3

    Undos used: 3

      3 words remaining
    x 5 unused letters
    = 15 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1533 🥳 18 ⏱️ 0:02:49.288631

📜 1 sessions
💰 score: 9800

    4/6
    READS ⬜⬜🟨🟩⬜
    BANDY ⬜🟩🟩🟩🟩
    CANDY ⬜🟩🟩🟩🟩
    HANDY 🟩🟩🟩🟩🟩
    3/6
    HANDY ⬜🟩⬜🟨⬜
    RATED 🟩🟩⬜⬜🟩
    RABID 🟩🟩🟩🟩🟩
    6/6
    RABID ⬜⬜⬜🟨⬜
    TINGE ⬜🟩⬜⬜⬜
    MILKY ⬜🟩🟩⬜🟩
    FILLY ⬜🟩🟩🟩🟩
    HILLY ⬜🟩🟩🟩🟩
    SILLY 🟩🟩🟩🟩🟩
    3/6
    SILLY ⬜⬜🟨⬜⬜
    ALONE ⬜🟨🟨⬜⬜
    MOGUL 🟩🟩🟩🟩🟩
    Final 2/2
    TOWER ⬜🟩⬜🟩🟩
    COVER 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1510 🥳 score:23 ⏱️ 0:01:30.905097

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. CONDO attempts:4 score:4
2. MUSKY attempts:6 score:6
3. RATER attempts:8 score:8
4. SNORT attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1510 😦 score:75 ⏱️ 0:05:12.734815

📜 3 sessions

Octordle Classic

1. BASTE attempts:4 score:4
2. SHEEN attempts:6 score:6
3. CRAZE attempts:11 score:11
4. DOWDY attempts:13 score:13
5. VOILA attempts:9 score:9
6. LOCAL attempts:10 score:10
7. BLACK attempts:5 score:-1
8. CHUMP attempts:8 score:8

# [squareword.org](squareword.org) 🧩 #1503 🥳 8 ⏱️ 0:02:04.215821

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C H A R D
    R A D I I
    O L I V E
    F L E E T
    T O U T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1440 🥳 218 ⏱️ 0:17:25.947416

🤔 219 attempts
📜 1 sessions
🫧 23 chat sessions
⁉️ 105 chat prompts
🤖 9 nemotron-3-nano:latest replies
🤖 33 gemma3:27b replies
🤖 63 dolphin3:latest replies
🔥   3 🥵   9 😎  24 🥶 162 🧊  20

      $1 #219 exempt           100.00°C 🥳 1000‰ ~199 used:0  [198]  source:nemotron
      $2 #150 prohibited        54.14°C 🔥  998‰  ~12 used:60 [11]   source:dolphin3
      $3 #146 barred            51.98°C 🔥  996‰   ~2 used:39 [1]    source:dolphin3
      $4 #153 banned            42.58°C 🥵  989‰   ~1 used:38 [0]    source:dolphin3
      $5 #148 forbidden         41.77°C 🥵  987‰  ~10 used:5  [9]    source:dolphin3
      $6 #199 shielded          40.53°C 🥵  982‰  ~11 used:5  [10]   source:gemma3  
      $7 #142 restricted        39.04°C 🥵  972‰   ~3 used:4  [2]    source:dolphin3
      $8 #164 verboten          37.05°C 🥵  960‰   ~4 used:4  [3]    source:dolphin3
      $9 #163 outlawed          36.74°C 🥵  959‰   ~5 used:4  [4]    source:dolphin3
     $10 #197 opposed           35.88°C 🥵  947‰   ~6 used:4  [5]    source:gemma3  
     $11 #141 protected         35.56°C 🥵  944‰   ~7 used:4  [6]    source:dolphin3
     $14 #191 governed          31.42°C 😎  887‰  ~13 used:0  [12]   source:gemma3  
     $38 #158 proscription      21.07°C 🥶        ~49 used:0  [48]   source:dolphin3
    $200  #36 pattern           -0.05°C 🧊       ~200 used:0  [199]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1473 🥳 293 ⏱️ 0:18:32.365894

🤔 294 attempts
📜 1 sessions
🫧 16 chat sessions
⁉️ 86 chat prompts
🤖 44 gemma3:27b replies
🤖 42 dolphin3:latest replies
🥵  14 😎  66 🥶 196 🧊  17

      $1 #294 temporaire       100.00°C 🥳 1000‰ ~277 used:0  [276]  source:gemma3  
      $2 #106 dérogation        35.46°C 🥵  977‰  ~76 used:33 [75]   source:gemma3  
      $3  #34 interruption      34.56°C 🥵  974‰  ~80 used:63 [79]   source:dolphin3
      $4  #37 cessation         34.42°C 🥵  973‰  ~78 used:44 [77]   source:dolphin3
      $5 #157 maintien          34.40°C 🥵  972‰   ~4 used:6  [3]    source:gemma3  
      $6  #79 restriction       33.69°C 🥵  967‰   ~5 used:6  [4]    source:gemma3  
      $7  #92 limitation        33.69°C 🥵  968‰   ~6 used:6  [5]    source:gemma3  
      $8 #110 autorisation      33.11°C 🥵  963‰   ~7 used:6  [6]    source:gemma3  
      $9 #192 prorogation       32.21°C 🥵  953‰   ~8 used:6  [7]    source:gemma3  
     $10 #268 durée             31.66°C 🥵  943‰   ~1 used:3  [0]    source:gemma3  
     $11 #262 période           30.89°C 🥵  928‰   ~2 used:4  [1]    source:gemma3  
     $16 #197 recours           29.51°C 😎  893‰  ~11 used:0  [10]   source:gemma3  
     $81 #234 apurement         19.00°C 🥶        ~67 used:0  [66]   source:gemma3  
    $278 #124 tolérance         -0.29°C 🧊       ~278 used:0  [277]  source:gemma3  
