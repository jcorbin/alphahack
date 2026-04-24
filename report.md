# 2026-04-25

- 🔗 spaceword.org 🧩 2026-04-24 🏁 score 2173 ranked 3.7% 12/328 ⏱️ 0:13:21.925721
- 🔗 alfagok.diginaut.net 🧩 #539 🥳 30 ⏱️ 0:00:38.415472
- 🔗 alphaguess.com 🧩 #1006 🥳 26 ⏱️ 0:00:38.175540
- 🔗 dontwordle.com 🧩 #1432 🥳 6 ⏱️ 0:01:11.143577
- 🔗 dictionary.com hurdle 🧩 #1575 😦 21 ⏱️ 0:03:24.073390
- 🔗 Quordle Classic 🧩 #1552 🥳 score:22 ⏱️ 0:01:11.792200
- 🔗 Octordle Classic 🧩 #1552 🥳 score:57 ⏱️ 0:03:26.490522
- 🔗 squareword.org 🧩 #1545 🥳 8 ⏱️ 0:03:07.992653
- 🔗 cemantle.certitudes.org 🧩 #1482 🥳 215 ⏱️ 0:02:27.701790
- 🔗 cemantix.certitudes.org 🧩 #1515 🥳 75 ⏱️ 0:00:55.007376

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























































# [spaceword.org](spaceword.org) 🧩 2026-04-24 🏁 score 2173 ranked 3.7% 12/328 ⏱️ 0:13:21.925721

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 12/328

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ L _ P U L Q U E S   
      _ I _ I _ I _ _ M I   
      _ P A N Z E R _ O X   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #539 🥳 30 ⏱️ 0:00:38.415472

🤔 30 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+199708 [199708] lijk       q0  ? ␅
    @+199708 [199708] lijk       q1  ? after
    @+199708 [199708] lijk       q2  ? ␅
    @+199708 [199708] lijk       q3  ? after
    @+299653 [299653] schroot    q4  ? ␅
    @+299653 [299653] schroot    q5  ? after
    @+349445 [349445] vakantie   q6  ? ␅
    @+349445 [349445] vakantie   q7  ? after
    @+374185 [374185] vrij       q8  ? ␅
    @+374185 [374185] vrij       q9  ? after
    @+375630 [375630] vuur       q16 ? ␅
    @+375630 [375630] vuur       q17 ? after
    @+376024 [376024] waak       q20 ? ␅
    @+376024 [376024] waak       q21 ? after
    @+376221 [376221] waardering q22 ? ␅
    @+376221 [376221] waardering q23 ? after
    @+376321 [376321] waardin    q24 ? ␅
    @+376321 [376321] waardin    q25 ? after
    @+376340 [376340] waarheid   q28 ? ␅
    @+376340 [376340] waarheid   q29 ? it
    @+376340 [376340] waarheid   done. it
    @+376374 [376374] waarlijk   q26 ? ␅
    @+376374 [376374] waarlijk   q27 ? before
    @+376426 [376426] waarneming q18 ? ␅
    @+376426 [376426] waarneming q19 ? before
    @+377248 [377248] wandel     q14 ? ␅
    @+377248 [377248] wandel     q15 ? before
    @+380397 [380397] weer       q12 ? ␅
    @+380397 [380397] weer       q13 ? before
    @+386722 [386722] wind       q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1006 🥳 26 ⏱️ 0:00:38.175540

🤔 26 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+47380 [47380] dis        q2  ? ␅
    @+47380 [47380] dis        q3  ? after
    @+72798 [72798] gremmy     q4  ? ␅
    @+72798 [72798] gremmy     q5  ? after
    @+79130 [79130] hood       q8  ? ␅
    @+79130 [79130] hood       q9  ? after
    @+80715 [80715] hydroxy    q12 ? ␅
    @+80715 [80715] hydroxy    q13 ? after
    @+81506 [81506] iamb       q14 ? ␅
    @+81506 [81506] iamb       q15 ? after
    @+81907 [81907] ignitor    q16 ? ␅
    @+81907 [81907] ignitor    q17 ? after
    @+81925 [81925] ignorami   q22 ? ␅
    @+81925 [81925] ignorami   q23 ? after
    @+81934 [81934] ignore     q24 ? ␅
    @+81934 [81934] ignore     q25 ? it
    @+81934 [81934] ignore     done. it
    @+81943 [81943] iguanians  q20 ? ␅
    @+81943 [81943] iguanians  q21 ? before
    @+81978 [81978] ill        q18 ? ␅
    @+81978 [81978] ill        q19 ? before
    @+82307 [82307] immaterial q10 ? ␅
    @+82307 [82307] immaterial q11 ? before
    @+85502 [85502] ins        q6  ? ␅
    @+85502 [85502] ins        q7  ? before
    @+98216 [98216] mach       q0  ? ␅
    @+98216 [98216] mach       q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1432 🥳 6 ⏱️ 0:01:11.143577

📜 1 sessions
💰 score: 27

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:YUMMY n n n n n remain:7572
    ⬜⬜⬜⬜⬜ tried:EBBED n n n n n remain:2762
    ⬜⬜⬜⬜⬜ tried:INION n n n n n remain:501
    ⬜🟩⬜⬜⬜ tried:PHPHT n Y n n n remain:22
    ⬜🟩🟩⬜⬜ tried:CHAFF n Y Y n n remain:6
    🟩🟩🟩⬜⬜ tried:SHAGS Y Y Y n n remain:3

    Undos used: 2

      3 words remaining
    x 9 unused letters
    = 27 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1575 😦 21 ⏱️ 0:03:24.073390

📜 1 sessions
💰 score: 4580

    4/6
    STARE ⬜⬜⬜⬜⬜
    LYING ⬜⬜🟨🟨🟨
    GIPON 🟨🟨⬜⬜🟨
    FUNGI 🟩🟩🟩🟩🟩
    5/6
    FUNGI ⬜⬜🟩⬜⬜
    MONAS ⬜🟩🟩⬜⬜
    RONDE ⬜🟩🟩⬜⬜
    CONKY ⬜🟩🟩🟩🟩
    WONKY 🟩🟩🟩🟩🟩
    4/6
    WONKY ⬜⬜⬜⬜⬜
    SERAL ⬜⬜🟨🟨⬜
    CAIRD ⬜🟨⬜🟨🟩
    FRAUD 🟩🟩🟩🟩🟩
    6/6
    FRAUD ⬜⬜⬜⬜⬜
    INSET ⬜⬜⬜⬜⬜
    BLOCK ⬜⬜🟨⬜⬜
    GYPPO ⬜🟨🟩🟩🟨
    HOPPY ⬜🟩🟩🟩🟩
    POPPY 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜🟩🟩⬜🟩
    ????? ⬜🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1552 🥳 score:22 ⏱️ 0:01:11.792200

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. RESET attempts:7 score:7
2. DRINK attempts:4 score:4
3. DEITY attempts:5 score:5
4. SLACK attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1552 🥳 score:57 ⏱️ 0:03:26.490522

📜 1 sessions

Octordle Classic

1. BOOZY attempts:12 score:12
2. EYING attempts:3 score:3
3. PASTE attempts:6 score:6
4. REPEL attempts:7 score:7
5. TEPEE attempts:5 score:5
6. DITTO attempts:9 score:9
7. BLOOM attempts:11 score:11
8. GIVEN attempts:4 score:4

# [squareword.org](squareword.org) 🧩 #1545 🥳 8 ⏱️ 0:03:07.992653

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟩 🟨
    🟨 🟨 🟩 🟨 🟨
    🟨 🟨 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    U P P E R
    D R A M A
    D O Y E N
    E V E N T
    R E E D S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1482 🥳 215 ⏱️ 0:02:27.701790

🤔 216 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 36 chat prompts
🤖 36 dolphin3:latest replies
🔥   2 🥵   2 😎   9 🥶 184 🧊  18

      $1 #216 fiscal            100.00°C 🥳 1000‰ ~198 used:0  [197]  source:dolphin3
      $2 #213 budget             59.00°C 🔥  998‰   ~1 used:1  [0]    source:dolphin3
      $3 #215 financial          50.82°C 🔥  996‰   ~2 used:0  [1]    source:dolphin3
      $4 #178 period             32.55°C 🥵  938‰   ~8 used:15 [7]    source:dolphin3
      $5 #206 year               29.83°C 🥵  908‰   ~3 used:6  [2]    source:dolphin3
      $6 #189 calendar           24.37°C 😎  756‰  ~11 used:4  [10]   source:dolphin3
      $7 #119 phase              23.67°C 😎  724‰  ~13 used:8  [12]   source:dolphin3
      $8 #214 expense            22.13°C 😎  624‰   ~4 used:0  [3]    source:dolphin3
      $9 #175 system             20.90°C 😎  519‰  ~10 used:3  [9]    source:dolphin3
     $10 #177 cycle              19.42°C 😎  321‰   ~9 used:2  [8]    source:dolphin3
     $11 #157 balance            19.31°C 😎  306‰   ~5 used:1  [4]    source:dolphin3
     $12 #199 decade             19.21°C 😎  284‰   ~6 used:1  [5]    source:dolphin3
     $15  #52 thermal            17.06°C 🥶        ~14 used:10 [13]   source:dolphin3
    $199   #2 banana             -0.21°C 🧊       ~199 used:0  [198]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1515 🥳 75 ⏱️ 0:00:55.007376

🤔 76 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 17 chat prompts
🤖 17 dolphin3:latest replies
🔥  1 🥵  5 😎 10 🥶 53 🧊  6

     $1 #76 noyau          100.00°C 🥳 1000‰ ~70 used:0  [69]  source:dolphin3
     $2 #74 nucléon         46.40°C 🔥  996‰  ~1 used:2  [0]   source:dolphin3
     $3 #47 atome           42.27°C 🥵  988‰  ~5 used:7  [4]   source:dolphin3
     $4 #75 neutron         41.72°C 🥵  983‰  ~2 used:0  [1]   source:dolphin3
     $5 #58 proton          40.91°C 🥵  975‰  ~3 used:0  [2]   source:dolphin3
     $6 #66 électron        37.40°C 🥵  926‰  ~4 used:0  [3]   source:dolphin3
     $7  #8 galaxie         36.51°C 🥵  908‰ ~13 used:13 [12]  source:dolphin3
     $8 #51 masse           35.81°C 😎  880‰ ~15 used:3  [14]  source:dolphin3
     $9 #45 particule       34.88°C 😎  846‰ ~14 used:2  [13]  source:dolphin3
    $10 #50 isotope         34.25°C 😎  815‰  ~6 used:0  [5]   source:dolphin3
    $11 #28 densité         33.63°C 😎  795‰  ~7 used:1  [6]   source:dolphin3
    $12 #46 supernova       31.02°C 😎  612‰  ~8 used:0  [7]   source:dolphin3
    $18 #26 antimatière     25.42°C 🥶       ~19 used:0  [18]  source:dolphin3
    $71  #5 école           -0.52°C 🧊       ~71 used:0  [70]  source:dolphin3
