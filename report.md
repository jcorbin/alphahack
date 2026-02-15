# 2026-02-16

- 🔗 spaceword.org 🧩 2026-02-15 🏁 score 2172 ranked 23.8% 79/332 ⏱️ 2:33:01.115335
- 🔗 alfagok.diginaut.net 🧩 #471 🥳 34 ⏱️ 0:00:41.023566
- 🔗 alphaguess.com 🧩 #938 🥳 28 ⏱️ 0:00:30.263730
- 🔗 dontwordle.com 🧩 #1364 🥳 6 ⏱️ 0:01:48.120168
- 🔗 dictionary.com hurdle 🧩 #1507 🥳 20 ⏱️ 0:02:50.648630
- 🔗 Quordle Classic 🧩 #1484 🥳 score:26 ⏱️ 0:01:57.848472
- 🔗 Octordle Classic 🧩 #1484 🥳 score:68 ⏱️ 0:03:42.025412
- 🔗 squareword.org 🧩 #1477 🥳 8 ⏱️ 0:02:06.952217
- 🔗 cemantle.certitudes.org 🧩 #1414 🥳 443 ⏱️ 0:36:29.478887
- 🔗 cemantix.certitudes.org 🧩 #1447 🥳 201 ⏱️ 0:05:11.765627

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
































# [spaceword.org](spaceword.org) 🧩 2026-02-15 🏁 score 2172 ranked 23.8% 79/332 ⏱️ 2:33:01.115335

📜 4 sessions
- tiles: 21/21
- score: 2172 bonus: +72
- rank: 79/332

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ B E E T _ _ _   
      _ _ _ E _ C _ _ _ _   
      _ _ _ D _ H E _ _ _   
      _ _ _ _ Z E N _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ W I N K _ _ _   
      _ _ _ E T U I _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #471 🥳 34 ⏱️ 0:00:41.023566

🤔 34 attempts
📜 1 sessions

    @       [    0] &-teken     
    @+24910 [24910] bad         q6  ? ␅
    @+24910 [24910] bad         q7  ? after
    @+37357 [37357] bescherm    q8  ? ␅
    @+37357 [37357] bescherm    q9  ? after
    @+39992 [39992] beurs       q12 ? ␅
    @+39992 [39992] beurs       q13 ? after
    @+41509 [41509] bewijs      q14 ? ␅
    @+41509 [41509] bewijs      q15 ? after
    @+41578 [41578] bewijzen    q24 ? ␅
    @+41578 [41578] bewijzen    q25 ? after
    @+41596 [41596] bewind      q26 ? ␅
    @+41596 [41596] bewind      q27 ? after
    @+41622 [41622] bewolk      q28 ? ␅
    @+41622 [41622] bewolk      q29 ? after
    @+41626 [41626] bewolkt     q32 ? ␅
    @+41626 [41626] bewolkt     q33 ? it
    @+41626 [41626] bewolkt     done. it
    @+41629 [41629] bewonder    q30 ? ␅
    @+41629 [41629] bewonder    q31 ? before
    @+41649 [41649] bewoners    q20 ? ␅
    @+41649 [41649] bewoners    q21 ? before
    @+41875 [41875] bezet       q18 ? ␅
    @+41875 [41875] bezet       q19 ? before
    @+42260 [42260] bezuiniging q16 ? ␅
    @+42260 [42260] bezuiniging q17 ? before
    @+43062 [43062] bij         q10 ? ␅
    @+43062 [43062] bij         q11 ? before
    @+49841 [49841] boks        q4  ? ␅
    @+49841 [49841] boks        q5  ? before
    @+99741 [99741] ex          q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #938 🥳 28 ⏱️ 0:00:30.263730

🤔 28 attempts
📜 1 sessions

    @       [    0] aa       
    @+2     [    2] aahed    
    @+11764 [11764] back     q6  ? ␅
    @+11764 [11764] back     q7  ? after
    @+17715 [17715] blind    q8  ? ␅
    @+17715 [17715] blind    q9  ? after
    @+19160 [19160] boot     q12 ? ␅
    @+19160 [19160] boot     q13 ? after
    @+19275 [19275] bore     q18 ? ␅
    @+19275 [19275] bore     q19 ? after
    @+19309 [19309] born     q22 ? ␅
    @+19309 [19309] born     q23 ? after
    @+19326 [19326] boroughs q24 ? ␅
    @+19326 [19326] boroughs q25 ? after
    @+19329 [19329] borrow   q26 ? ␅
    @+19329 [19329] borrow   q27 ? it
    @+19329 [19329] borrow   done. it
    @+19342 [19342] borstal  q20 ? ␅
    @+19342 [19342] borstal  q21 ? before
    @+19409 [19409] bot      q16 ? ␅
    @+19409 [19409] bot      q17 ? before
    @+19874 [19874] bra      q14 ? ␅
    @+19874 [19874] bra      q15 ? before
    @+20687 [20687] brill    q10 ? ␅
    @+20687 [20687] brill    q11 ? before
    @+23682 [23682] camp     q4  ? ␅
    @+23682 [23682] camp     q5  ? before
    @+47381 [47381] dis      q2  ? ␅
    @+47381 [47381] dis      q3  ? before
    @+98219 [98219] mach     q0  ? ␅
    @+98219 [98219] mach     q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1364 🥳 6 ⏱️ 0:01:48.120168

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MERER n n n n n remain:4337
    ⬜⬜⬜⬜⬜ tried:BOFFO n n n n n remain:2100
    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:888
    ⬜🟩⬜⬜⬜ tried:PHPHT n Y n n n remain:31
    ⬜🟩🟨⬜⬜ tried:GHYLL n Y m n n remain:5
    🟩🟩🟩⬜🟩 tried:SHADY Y Y Y n Y remain:1

    Undos used: 4

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1507 🥳 20 ⏱️ 0:02:50.648630

📜 1 sessions
💰 score: 9600

    4/6
    STARE ⬜⬜🟨🟨🟨
    CEDAR ⬜🟨⬜🟩🟨
    BREAK ⬜🟩🟩🟩🟩
    FREAK 🟩🟩🟩🟩🟩
    4/6
    FREAK ⬜🟨🟨🟨⬜
    TEARS ⬜🟨🟨🟨🟨
    SAGER 🟨🟩⬜🟩🟩
    LASER 🟩🟩🟩🟩🟩
    6/6
    LASER ⬜⬜🟨🟨🟨
    SNORE 🟩⬜🟩🟩🟩
    SCORE 🟩⬜🟩🟩🟩
    STORE 🟩⬜🟩🟩🟩
    SHORE 🟩⬜🟩🟩🟩
    SPORE 🟩🟩🟩🟩🟩
    5/6
    SPORE ⬜⬜🟨⬜⬜
    ONTIC 🟨⬜⬜⬜🟨
    MOCHA ⬜🟩🟨🟨⬜
    COUGH 🟨🟩🟩⬜🟩
    VOUCH 🟩🟩🟩🟩🟩
    Final 1/2
    SHEET 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1484 🥳 score:26 ⏱️ 0:01:57.848472

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. CANAL attempts:5 score:5
2. JELLY attempts:8 score:8
3. FALSE attempts:7 score:7
4. NAVAL attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1484 🥳 score:68 ⏱️ 0:03:42.025412

📜 1 sessions

Octordle Classic

1. FERRY attempts:5 score:5
2. ALONE attempts:6 score:6
3. SEWER attempts:11 score:11
4. NAVAL attempts:9 score:9
5. PIXEL attempts:10 score:10
6. WOKEN attempts:12 score:12
7. FROZE attempts:8 score:8
8. FLOUR attempts:7 score:7

# [squareword.org](squareword.org) 🧩 #1477 🥳 8 ⏱️ 0:02:06.952217

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟨
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    G R A S P
    R A Z O R
    U V U L A
    N E R V Y
    T R E E S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1414 🥳 443 ⏱️ 0:36:29.478887

🤔 444 attempts
📜 1 sessions
🫧 30 chat sessions
⁉️ 99 chat prompts
🤖 33 dolphin3:latest replies
🤖 60 glm-4.7-flash:latest replies
🤖 5 ServiceNow-AI/Apriel-1.6-15b-Thinker:Q4_K_M replies
🥵   8 😎  47 🥶 371 🧊  17

      $1 #444 animation         100.00°C 🥳 1000‰ ~427 used:0  [426]  source:dolphin3  
      $2 #397 visual             42.67°C 🥵  975‰  ~30 used:11 [29]   source:dolphin3  
      $3 #340 typography         41.11°C 🥵  967‰  ~31 used:16 [30]   source:dolphin3  
      $4 #394 graphic            40.32°C 🥵  963‰   ~4 used:4  [3]    source:dolphin3  
      $5 #436 creative           39.29°C 🥵  958‰   ~1 used:1  [0]    source:dolphin3  
      $6 #434 art                38.67°C 🥵  950‰   ~2 used:1  [1]    source:dolphin3  
      $7 #190 morpheme           37.22°C 🥵  933‰  ~50 used:56 [49]   source:glm       
      $8 #412 visualization      35.82°C 🥵  915‰   ~3 used:3  [2]    source:dolphin3  
      $9 #359 script             35.15°C 🥵  904‰   ~5 used:5  [4]    source:dolphin3  
     $10 #438 imagery            34.85°C 😎  897‰   ~6 used:0  [5]    source:dolphin3  
     $11 #386 typographic        34.48°C 😎  888‰   ~7 used:0  [6]    source:dolphin3  
     $12 #320 rendering          34.27°C 😎  885‰  ~43 used:4  [42]   source:dolphin3  
     $58 #377 text               23.72°C 🥶        ~58 used:0  [57]   source:dolphin3  
    $428 #309 base               -0.02°C 🧊       ~428 used:0  [427]  source:dolphin3  

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1447 🥳 201 ⏱️ 0:05:11.765627

🤔 202 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 38 chat prompts
🤖 38 dolphin3:latest replies
🔥   3 🥵  16 😎  45 🥶 109 🧊  28

      $1 #202 structurel          100.00°C 🥳 1000‰ ~174 used:0  [173]  source:dolphin3
      $2 #200 macroéconomique      55.38°C 🔥  998‰   ~1 used:0  [0]    source:dolphin3
      $3 #169 économique           53.35°C 🔥  997‰   ~6 used:15 [5]    source:dolphin3
      $4 #143 évolution            49.88°C 🔥  991‰   ~7 used:19 [6]    source:dolphin3
      $5 #195 ajustement           48.75°C 🥵  989‰   ~2 used:1  [1]    source:dolphin3
      $6 #155 processus            46.42°C 🥵  981‰  ~19 used:7  [18]   source:dolphin3
      $7 #128 approche             46.13°C 🥵  977‰  ~14 used:3  [13]   source:dolphin3
      $8 #121 analyse              46.03°C 🥵  975‰   ~8 used:2  [7]    source:dolphin3
      $9 #142 transformation       44.88°C 🥵  964‰   ~9 used:2  [8]    source:dolphin3
     $10 #178 stabilité            44.61°C 🥵  962‰  ~10 used:2  [9]    source:dolphin3
     $11 #118 stratégie            44.20°C 🥵  958‰  ~16 used:5  [15]   source:dolphin3
     $21  #76 économie             40.00°C 😎  899‰  ~62 used:2  [61]   source:dolphin3
     $66 #127 vision               27.72°C 🥶        ~70 used:0  [69]   source:dolphin3
    $175  #12 arbre                -0.12°C 🧊       ~175 used:0  [174]  source:dolphin3
