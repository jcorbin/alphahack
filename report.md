# 2026-10-01

- 🔗 spaceword.org 🧩 2026-09-30 🏁 score 2173 ranked 6.6% 22/332 ⏱️ 0:46:05.863276
- 🔗 wordgrid 🧩 #852 🟪 rarity:0.15 ⏱️ 0:02:31.683259
- 🔗 alfagok.diginaut.net 🧩 #698 🥳 30 ⏱️ 0:01:06.864039
- 🔗 alphaguess.com 🧩 #1165 🥳 22 ⏱️ 0:00:26.412126
- 🔗 dontwordle.com 🧩 #1591 🥳 6 ⏱️ 0:01:20.043677
- 🔗 dictionary.com hurdle 🧩 #1734 🥳 16 ⏱️ 0:02:36.954983
- 🔗 Quordle Classic 🧩 #1711 🥳 score:25 ⏱️ 0:01:44.195283
- 🔗 Octordle Classic 🧩 #1711 🥳 score:60 ⏱️ 0:02:09.612617
- 🔗 Sedecordle Classic 🧩 #1691 🥳 score:45 ⏱️ 0:04:27.664447
- 🔗 squareword.org 🧩 #1704 🥳 7 ⏱️ 0:01:36.571989
- 🔗 cemantle.certitudes.org 🧩 #1641 🥳 338 ⏱️ 0:23:05.680373
- 🔗 cemantix.certitudes.org 🧩 #1674 🥳 416 ⏱️ 0:35:40.504011

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











# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #852 🟪 rarity:0.15 ⏱️ 0:02:31.683259

📜 2 sessions
🌌 🌌 🦄
🌌 🌌 🦄
🦄 🌌 🦄
Rarity: 0.15 🟪

# [spaceword.org](spaceword.org) 🧩 2026-09-30 🏁 score 2173 ranked 6.6% 22/332 ⏱️ 0:46:05.863276

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 22/332

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ K _ C A L Q U E   
      _ X E N O N _ I _ A   
      _ _ F O Y E R S _ U   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #698 🥳 30 ⏱️ 0:01:06.864039

🤔 30 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199528 [199528] lij       q0  ? ␅
    @+199528 [199528] lij       q1  ? after
    @+211521 [211521] mdccxiii  q12 ? ␅
    @+211521 [211521] mdccxiii  q13 ? .
    @+211521 [211521] mdccxiii  q14 ? ␅
    @+211521 [211521] mdccxiii  q15 ? .
    @+211603 [211603] me        q16 ? ␅
    @+211603 [211603] me        q17 ? after
    @+213861 [213861] mei       q20 ? ␅
    @+213861 [213861] mei       q21 ? after
    @+214677 [214677] men       q22 ? ␅
    @+214677 [214677] men       q23 ? after
    @+214897 [214897] mens      q26 ? ␅
    @+214897 [214897] mens      q27 ? after
    @+214924 [214924] mensen    q28 ? ␅
    @+214924 [214924] mensen    q29 ? it
    @+214924 [214924] mensen    done. it
    @+215463 [215463] merk      q24 ? ␅
    @+215463 [215463] merk      q25 ? before
    @+216556 [216556] mi        q18 ? ␅
    @+216556 [216556] mi        q19 ? before
    @+223512 [223512] molen     q6  ? ␅
    @+223512 [223512] molen     q7  ? before
    @+247576 [247576] op        q4  ? ␅
    @+247576 [247576] op        q5  ? before
    @+299480 [299480] schrok    q2  ? ␅
    @+299480 [299480] schrok    q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1165 🥳 22 ⏱️ 0:00:26.412126

🤔 22 attempts
📜 1 sessions

    @        [     0] aa       
    @+1      [     1] aah      
    @+2      [     2] aahed    
    @+3      [     3] aahing   
    @+98142  [ 98142] mac      q0  ? ␅
    @+98142  [ 98142] mac      q1  ? after
    @+147306 [147306] rho      q2  ? ␅
    @+147306 [147306] rho      q3  ? after
    @+159588 [159588] slug     q6  ? ␅
    @+159588 [159588] slug     q7  ? after
    @+162621 [162621] speed    q10 ? ␅
    @+162621 [162621] speed    q11 ? after
    @+164181 [164181] squilgee q12 ? ␅
    @+164181 [164181] squilgee q13 ? after
    @+164961 [164961] stay     q14 ? ␅
    @+164961 [164961] stay     q15 ? after
    @+165018 [165018] steam    q20 ? ␅
    @+165018 [165018] steam    q21 ? it
    @+165018 [165018] steam    done. it
    @+165138 [165138] steer    q18 ? ␅
    @+165138 [165138] steer    q19 ? before
    @+165322 [165322] stereo   q16 ? ␅
    @+165322 [165322] stereo   q17 ? before
    @+165742 [165742] stint    q8  ? ␅
    @+165742 [165742] stint    q9  ? before
    @+171906 [171906] tag      q4  ? ␅
    @+171906 [171906] tag      q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1591 🥳 6 ⏱️ 0:01:20.043677

📜 1 sessions
💰 score: 21

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:JINNI n n n n n remain:7302
    ⬜⬜⬜⬜⬜ tried:TAZZA n n n n n remain:2891
    ⬜⬜⬜⬜⬜ tried:SULUS n n n n n remain:636
    🟩⬜⬜⬜⬜ tried:PYGMY Y n n n n remain:33
    🟩⬜🟩⬜⬜ tried:POOCH Y n Y n n remain:4
    🟩🟩🟩⬜🟩 tried:PROVE Y Y Y n Y remain:3

    Undos used: 3

      3 words remaining
    x 7 unused letters
    = 21 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1734 🥳 16 ⏱️ 0:02:36.954983

📜 2 sessions
💰 score: 10000

    4/6
    REAPS ⬜⬜⬜⬜⬜
    LUNGI 🟨🟨⬜⬜⬜
    FLOUT 🟨🟩⬜🟨⬜
    BLUFF 🟩🟩🟩🟩🟩
    4/6
    BLUFF ⬜⬜⬜⬜⬜
    RATES ⬜🟩🟨🟨🟨
    CHAMP ⬜⬜🟨⬜🟨
    PASTE 🟩🟩🟩🟩🟩
    4/6
    PASTE ⬜⬜⬜🟨🟨
    TONER 🟩⬜⬜🟩🟩
    BAGEL ⬜⬜⬜🟩⬜
    TIMER 🟩🟩🟩🟩🟩
    3/6
    TIMER 🟨⬜🟨⬜⬜
    MOUTH 🟩🟩🟩🟨⬜
    MOUNT 🟩🟩🟩🟩🟩
    Final 1/2
    COMIC 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1711 🥳 score:25 ⏱️ 0:01:44.195283

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. NAVEL attempts:4 score:4
2. SHEER attempts:7 score:7
3. BIRTH attempts:6 score:6
4. TACKY attempts:8 score:8

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1711 🥳 score:60 ⏱️ 0:02:09.612617

📜 1 sessions

Octordle Classic

1. GAZER attempts:6 score:6
2. DOPEY attempts:4 score:4
3. TOPAZ attempts:5 score:5
4. CHAOS attempts:9 score:9
5. PRANK attempts:10 score:10
6. CRIED attempts:8 score:8
7. GROWL attempts:7 score:7
8. DATUM attempts:11 score:11

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1691 🥳 score:45 ⏱️ 0:04:27.664447

📜 2 sessions

Sedecordle Classic sedecordle.com

1. FENCE attempts:12 score:1
2. SHALL attempts:10 score:2
3. RABID attempts:16 score:1
4. NEWLY attempts:6 score:6
5. PASTE attempts:14 score:1
6. RIVET attempts:3 score:4
7. BLEED attempts:17 score:1
8. MIMIC attempts:7 score:7
9. CRUMB attempts:15 score:1
10. TRYST attempts:8 score:5
11. FROST attempts:13 score:1
12. SCARE attempts:9 score:3
13. FIBER attempts:18 score:1
14. JUMPY attempts:18 score:9
15. HATER attempts:11 score:1
16. RELAX attempts:4 score:1

# [squareword.org](squareword.org) 🧩 #1704 🥳 7 ⏱️ 0:01:36.571989

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S W A T H
    C A M E O
    O D O R S
    R E U S E
    E R R E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1641 🥳 338 ⏱️ 0:23:05.680373

🤔 339 attempts
📜 2 sessions
🫧 19 chat sessions
⁉️ 111 chat prompts
🤖 6 dolphin3:latest replies
🤖 105 ornith-1.5:35b replies
😱   1 🥵  10 😎  35 🥶 271 🧊  21

      $1 #339 relief         100.00°C 🥳 1000‰ ~318 used:0  [317]  source:dolphin3
      $2 #336 aid             51.62°C 😱  999‰   ~1 used:0  [0]    source:dolphin3
      $3 #306 disaster        38.49°C 🥵  988‰  ~35 used:27 [34]   source:ornith  
      $4 #335 emergency       36.48°C 🥵  985‰   ~2 used:1  [1]    source:dolphin3
      $5 #275 hardship        31.92°C 🥵  974‰  ~34 used:21 [33]   source:ornith  
      $6 #285 calamity        31.83°C 🥵  973‰   ~9 used:8  [8]    source:ornith  
      $7 #292 suffering       30.31°C 🥵  960‰   ~5 used:6  [4]    source:ornith  
      $8 #272 devastation     29.68°C 🥵  952‰   ~6 used:6  [5]    source:ornith  
      $9 #334 pain            29.56°C 🥵  951‰   ~3 used:3  [2]    source:ornith  
     $10 #313 misery          29.03°C 🥵  945‰   ~7 used:6  [6]    source:ornith  
     $11 #286 distress        28.99°C 🥵  944‰   ~4 used:5  [3]    source:ornith  
     $13 #254 hunger          25.86°C 😎  885‰  ~38 used:5  [37]   source:ornith  
     $48 #271 desolation      17.13°C 🥶        ~54 used:0  [53]   source:ornith  
    $319 #120 cooker          -0.01°C 🧊       ~319 used:0  [318]  source:ornith  

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1674 🥳 416 ⏱️ 0:35:40.504011

🤔 417 attempts
📜 1 sessions
🫧 28 chat sessions
⁉️ 171 chat prompts
🤖 143 ornith-1.5:35b replies
🤖 15 dolphin3:latest replies
🤖 14 gemma4:12b replies
🔥   2 🥵  32 😎 102 🥶 252 🧊  28

      $1 #417 successif         100.00°C 🥳 1000‰ ~389 used:0  [388]  source:ornith  
      $2 #360 antérieur          50.56°C 🔥  996‰   ~1 used:29 [0]    source:ornith  
      $3 #307 simultanément      46.17°C 🔥  992‰  ~22 used:46 [21]   source:ornith  
      $4 #251 période            44.97°C 🥵  988‰ ~134 used:38 [133]  source:ornith  
      $5 #287 simultané          44.55°C 🥵  986‰  ~96 used:17 [95]   source:ornith  
      $6 #267 enchaînement       44.36°C 🥵  983‰  ~23 used:7  [22]   source:ornith  
      $7 #281 simultanéité       43.55°C 🥵  980‰  ~16 used:4  [15]   source:ornith  
      $8 #272 chronologique      43.23°C 🥵  979‰  ~17 used:4  [16]   source:ornith  
      $9 #339 superposition      43.11°C 🥵  978‰  ~18 used:4  [17]   source:ornith  
     $10 #316 juxtaposer         42.51°C 🥵  975‰  ~19 used:4  [18]   source:ornith  
     $11 #375 ultérieur          42.08°C 🥵  973‰  ~20 used:4  [19]   source:ornith  
     $36 #201 itération          36.30°C 😎  893‰  ~28 used:1  [27]   source:ornith  
    $139 #173 cycle              25.64°C 🥶       ~144 used:0  [143]  source:ornith  
    $390 #377 venir              -0.42°C 🧊       ~390 used:0  [389]  source:ornith  
