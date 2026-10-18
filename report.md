# 2026-10-19

- 🔗 wordgrid 🧩 #870 🟪 rarity:0.29 ⏱️ 0:03:24.070313
- 🔗 spaceword.org 🧩 2026-10-18 🏁 score 2168 ranked 45.4% 134/295 ⏱️ 3:07:50.537677
- 🔗 alfagok.diginaut.net 🧩 #716 🥳 38 ⏱️ 0:00:55.443204
- 🔗 alphaguess.com 🧩 #1183 🥳 34 ⏱️ 0:00:39.366218
- 🔗 dontwordle.com 🧩 #1609 🥳 6 ⏱️ 0:01:49.842241
- 🔗 dictionary.com hurdle 🧩 #1752 🥳 19 ⏱️ 0:04:10.939986
- 🔗 Quordle Classic 🧩 #1729 😦 score:26 ⏱️ 0:01:58.177567
- 🔗 Octordle Classic 🧩 #1729 🥳 score:69 ⏱️ 0:02:35.508827
- 🔗 Sedecordle Classic 🧩 #1709 🥳 score:49 ⏱️ 0:02:42.458812
- 🔗 squareword.org 🧩 #1722 🥳 8 ⏱️ 0:02:25.812479
- 🔗 cemantle.certitudes.org 🧩 #1659 😦 1197 ⏱️ 11:42:30.562127

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















# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #870 🟪 rarity:0.29 ⏱️ 0:03:24.070313

📜 2 sessions
🦄 🌌 🌌
🦄 🌌 🌌
🦄 🌌 🦄
Rarity: 0.29 🟪

# [spaceword.org](spaceword.org) 🧩 2026-10-18 🏁 score 2168 ranked 45.4% 134/295 ⏱️ 3:07:50.537677

📜 2 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 134/295

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ G O X _ _ _ _ D _   
      _ A _ _ Z _ G _ I _   
      _ D O M I N E _ V _   
      _ _ _ A T O N I A _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #716 🥳 38 ⏱️ 0:00:55.443204

🤔 38 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+199631 [199631] lijk        q0  ? ␅
    @+199631 [199631] lijk        q1  ? after
    @+249545 [249545] opi         q4  ? ␅
    @+249545 [249545] opi         q5  ? after
    @+274461 [274461] prop        q6  ? ␅
    @+274461 [274461] prop        q7  ? after
    @+286975 [286975] riool       q8  ? ␅
    @+286975 [286975] riool       q9  ? after
    @+289410 [289410] rood        q14 ? ␅
    @+289410 [289410] rood        q15 ? after
    @+289966 [289966] ros         q18 ? ␅
    @+289966 [289966] ros         q19 ? after
    @+290065 [290065] rot         q22 ? ␅
    @+290065 [290065] rot         q23 ? after
    @+290344 [290344] rouleer     q24 ? ␅
    @+290344 [290344] rouleer     q25 ? after
    @+290432 [290432] rouw        q26 ? ␅
    @+290432 [290432] rouw        q27 ? after
    @+290532 [290532] rouwstoeten q28 ? ␅
    @+290532 [290532] rouwstoeten q29 ? after
    @+290579 [290579] royale      q32 ? ␅
    @+290579 [290579] royale      q33 ? after
    @+290599 [290599] royeer      q34 ? ␅
    @+290599 [290599] royeer      q35 ? after
    @+290614 [290614] roze        q36 ? ␅
    @+290614 [290614] roze        q37 ? it
    @+290614 [290614] roze        done. it
    @+290630 [290630] rozen       q16 ? ␅
    @+290630 [290630] rozen       q17 ? before
    @+291988 [291988] sa          q13 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1183 🥳 34 ⏱️ 0:00:39.366218

🤔 34 attempts
📜 1 sessions

    @       [    0] aa         
    @+47374 [47374] dis        q2  ? ␅
    @+47374 [47374] dis        q3  ? after
    @+49421 [49421] do         q10 ? ␅
    @+49421 [49421] do         q11 ? after
    @+51395 [51395] drunk      q12 ? ␅
    @+51395 [51395] drunk      q13 ? after
    @+52388 [52388] earth      q14 ? ␅
    @+52388 [52388] earth      q15 ? after
    @+52446 [52446] earwig     q22 ? ␅
    @+52446 [52446] earwig     q23 ? after
    @+52473 [52473] east       q24 ? ␅
    @+52473 [52473] east       q25 ? after
    @+52489 [52489] easy       q26 ? ␅
    @+52489 [52489] easy       q27 ? after
    @+52493 [52493] eat        q28 ? ␅
    @+52493 [52493] eat        q29 ? after
    @+52497 [52497] eater      q30 ? ␅
    @+52497 [52497] eater      q31 ? after
    @+52502 [52502] eating     q32 ? ␅
    @+52502 [52502] eating     q33 ? it
    @+52502 [52502] eating     done. it
    @+52507 [52507] eave       q20 ? ␅
    @+52507 [52507] eave       q21 ? before
    @+52626 [52626] echo       q18 ? ␅
    @+52626 [52626] echo       q19 ? before
    @+52868 [52868] ed         q16 ? ␅
    @+52868 [52868] ed         q17 ? before
    @+53390 [53390] el         q8  ? ␅
    @+53390 [53390] el         q9  ? before
    @+60013 [60013] eyewitness q7  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1609 🥳 6 ⏱️ 0:01:49.842241

📜 1 sessions
💰 score: 9

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:GAMMA n n n n n remain:5731
    ⬜⬜⬜⬜⬜ tried:FEEZE n n n n n remain:2258
    ⬜⬜⬜⬜⬜ tried:SHOOS n n n n n remain:321
    ⬜🟨⬜⬜⬜ tried:XYLYL n m n n n remain:100
    ⬜⬜🟨⬜🟨 tried:CRYPT n n m n m remain:19
    ⬜🟨⬜🟩🟩 tried:TUTTY n m n Y Y remain:1

    Undos used: 3

      1 words remaining
    x 9 unused letters
    = 9 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1752 🥳 19 ⏱️ 0:04:10.939986

📜 1 sessions
💰 score: 9700

    5/6
    TORES ⬜⬜⬜⬜⬜
    LINKY ⬜🟩⬜⬜🟩
    PIGMY ⬜🟩⬜⬜🟩
    DHOBI 🟩⬜⬜⬜🟨
    DIVVY 🟩🟩🟩🟩🟩
    5/6
    DIVVY ⬜⬜⬜⬜⬜
    SORTA ⬜⬜⬜⬜⬜
    LUMEN 🟨🟨🟨🟨⬜
    BEFOG ⬜🟨⬜⬜⬜
    PLUME 🟩🟩🟩🟩🟩
    4/6
    PLUME ⬜🟩⬜⬜🟩
    ALIVE 🟨🟩⬜⬜🟩
    BERGS ⬜🟨🟨🟨⬜
    GLARE 🟩🟩🟩🟩🟩
    3/6
    GLARE ⬜⬜🟩🟩🟩
    INAPT ⬜⬜🟩⬜🟨
    STARE 🟩🟩🟩🟩🟩
    Final 2/2
    CHAFE ⬜⬜⬜⬜⬜
    BRISK 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1729 😦 score:26 ⏱️ 0:01:58.177567

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. EXIST attempts:4 score:4
2. DECOY attempts:6 score:6
3. _ITCH -ABDEFGLMNOPRSUWXY attempts:9 score:-1
4. FLUID attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1729 🥳 score:69 ⏱️ 0:02:35.508827

📜 2 sessions

Octordle Classic

1. STEEP attempts:11 score:11
2. RETRO attempts:12 score:13
3. GEEKY attempts:10 score:10
4. SNAIL attempts:3 score:3
5. REBUS attempts:8 score:8
6. CHAIN attempts:5 score:5
7. MAJOR attempts:7 score:7
8. COWER attempts:12 score:12

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1709 🥳 score:49 ⏱️ 0:02:42.458812

📜 1 sessions

Sedecordle Classic sedecordle.com

1. TABOO attempts:13 score:1
2. LOWLY attempts:6 score:3
3. SEEDY attempts:16 score:1
4. CELLO attempts:15 score:6
5. BROWN attempts:3 score:0
6. ROOMY attempts:8 score:3
7. LUMEN attempts:5 score:0
8. SLAIN attempts:4 score:5
9. BUILT attempts:12 score:1
10. MASSE attempts:7 score:2
11. SEPIA attempts:9 score:0
12. TURBO attempts:10 score:9
13. GORGE attempts:19 score:1
14. RIVAL attempts:11 score:9
15. DROOP attempts:17 score:1
16. VOUCH attempts:14 score:7

# [squareword.org](squareword.org) 🧩 #1722 🥳 8 ⏱️ 0:02:25.812479

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟩 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C A N S
    A R G O T
    L E A V E
    E A T E N
    S M E L T

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1659 😦 1197 ⏱️ 11:42:30.562127

🤔 1196 attempts
📜 2 sessions
🫧 86 chat sessions
⁉️ 469 chat prompts
🤖 96 gemma4:12b replies
🤖 94 dolphin3:latest replies
🤖 279 llama3.2:latest replies
😦 😱    1 🔥    3 🥵   28 😎  180 🥶  876 🧊  108

       $1 #1077 congratulate       40.23°C 😱  999‰    ~1 used:165 [0]     source:llama3.2
       $2  #965 commend            37.56°C 🔥  996‰  ~131 used:120 [130]   source:llama3.2
       $3  #682 representative     35.51°C 🔥  995‰  ~199 used:207 [198]   source:llama3.2
       $4  #345 onus               32.70°C 🔥  992‰  ~200 used:235 [199]   source:gemma4  
       $5  #246 obligation         32.44°C 🥵  989‰  ~211 used:137 [210]   source:gemma4  
       $6  #773 counsel            32.21°C 🥵  988‰  ~108 used:11  [107]   source:llama3.2
       $7  #346 owe                31.87°C 🥵  986‰  ~204 used:40  [203]   source:gemma4  
       $8  #115 rely               30.71°C 🥵  979‰  ~208 used:60  [207]   source:dolphin3
       $9 #1163 congratulations    30.26°C 🥵  974‰  ~109 used:11  [108]   source:dolphin3
      $10  #757 solicitor          29.79°C 🥵  968‰  ~110 used:11  [109]   source:llama3.2
      $11  #718 lawyer             29.69°C 🥵  967‰  ~111 used:11  [110]   source:llama3.2
      $33  #196 dedication         25.86°C 😎  897‰  ~133 used:2   [132]   source:gemma4  
     $213  #967 recognize          17.43°C 🥶        ~217 used:0   [216]   source:llama3.2
    $1089  #344 measure            -0.01°C 🧊       ~1089 used:0   [1088]  source:gemma4  
