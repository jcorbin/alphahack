# 2026-11-15

- 🔗 wordgrid 🧩 #897 🟪 rarity:0.14 ⏱️ 0:02:57.405793
- 🔗 spaceword.org 🧩 2026-11-14 🏁 score 2168 ranked 36.0% 99/275 ⏱️ 1:10:12.934410
- 🔗 alfagok.diginaut.net 🧩 #743 🥳 34 ⏱️ 0:00:52.982459
- 🔗 alphaguess.com 🧩 #1210 🥳 38 ⏱️ 0:01:11.659378
- 🔗 dontwordle.com 🧩 #1636 🥳 6 ⏱️ 0:01:46.926847
- 🔗 dictionary.com hurdle 🧩 #1779 🥳 16 ⏱️ 0:03:20.619556
- 🔗 Quordle Classic 🧩 #1756 🥳 score:22 ⏱️ 0:02:36.344109
- 🔗 Octordle Classic 🧩 #1756 🥳 score:60 ⏱️ 0:02:06.523927
- 🔗 Sedecordle Classic 🧩 #1736 🥳 score:30 ⏱️ 0:03:20.561535
- 🔗 squareword.org 🧩 #1749 🥳 7 ⏱️ 0:03:09.933013
- 🔗 cemantle.certitudes.org 🧩 #1686 🥳 277 ⏱️ 0:01:09.410878
- 🔗 cemantix.certitudes.org 🧩 #1719 🥳 148 ⏱️ 0:00:51.258443

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










# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #892 🟪 rarity:0.32 ⏱️ 0:03:10.891631

📜 2 sessions
🌌 🦄 🦄
🌌 🌌 🌌
🦄 🌌 🌌
Rarity: 0.32 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-09 🏁 score 2168 ranked 49.8% 148/297 ⏱️ 0:22:41.164996

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 148/297

      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ G _ _ _ _ K _ L _
      _ O _ C A S A V A _
      _ A _ A _ _ S I G _
      _ D A W E N _ A _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #897 🟪 rarity:0.14 ⏱️ 0:02:57.405793

📜 2 sessions
🌌 🦄 🦄
🦄 🦄 🦄
🦄 🌌 🌌
Rarity: 0.14 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-14 🏁 score 2168 ranked 36.0% 99/275 ⏱️ 1:10:12.934410

📜 5 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 99/275

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ Y O M _ _ _   
      _ _ _ _ _ _ E _ _ _   
      _ _ _ I L K A _ _ _   
      _ _ _ _ _ O N _ _ _   
      _ _ _ _ J U T _ _ _   
      _ _ _ F O R _ _ _ _   
      _ _ _ _ _ O _ _ _ _   
      _ _ _ Q U I D _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #743 🥳 34 ⏱️ 0:00:52.982459

🤔 34 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+199631 [199631] lijk       q0  ? ␅
    @+199631 [199631] lijk       q1  ? after
    @+199631 [199631] lijk       q2  ? ␅
    @+199631 [199631] lijk       q3  ? after
    @+199631 [199631] lijk       q4  ? ␅
    @+199631 [199631] lijk       q5  ? after
    @+249538 [249538] opi        q8  ? ␅
    @+249538 [249538] opi        q9  ? after
    @+274524 [274524] proper     q10 ? ␅
    @+274524 [274524] proper     q11 ? after
    @+279624 [279624] rechts     q14 ? ␅
    @+279624 [279624] rechts     q15 ? after
    @+280996 [280996] ref        q18 ? ␅
    @+280996 [280996] ref        q19 ? after
    @+281258 [281258] regel      q22 ? ␅
    @+281258 [281258] regel      q23 ? after
    @+281324 [281324] regelloze  q26 ? ␅
    @+281324 [281324] regelloze  q27 ? after
    @+281327 [281327] regelmatig q32 ? ␅
    @+281327 [281327] regelmatig q33 ? it
    @+281327 [281327] regelmatig done. it
    @+281339 [281339] regelneef  q30 ? ␅
    @+281339 [281339] regelneef  q31 ? before
    @+281357 [281357] regels     q28 ? ␅
    @+281357 [281357] regels     q29 ? before
    @+281389 [281389] regen      q24 ? ␅
    @+281389 [281389] regen      q25 ? before
    @+281620 [281620] regering   q20 ? ␅
    @+281620 [281620] regering   q21 ? before
    @+282395 [282395] reis       q17 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1210 🥳 38 ⏱️ 0:01:11.659378

🤔 38 attempts
📜 2 sessions

    @        [     0] aa          
    @+98138  [ 98138] mac         q0  ? ␅
    @+98138  [ 98138] mac         q1  ? after
    @+98138  [ 98138] mac         q2  ? ␅
    @+98138  [ 98138] mac         q3  ? after
    @+147299 [147299] rho         q4  ? ␅
    @+147299 [147299] rho         q5  ? after
    @+159581 [159581] slug        q8  ? ␅
    @+159581 [159581] slug        q9  ? after
    @+165740 [165740] stipe       q10 ? ␅
    @+165740 [165740] stipe       q11 ? after
    @+168784 [168784] sulfur      q12 ? ␅
    @+168784 [168784] sulfur      q13 ? after
    @+169210 [169210] super       q16 ? ␅
    @+169210 [169210] super       q17 ? after
    @+169685 [169685] supers      q18 ? ␅
    @+169685 [169685] supers      q19 ? after
    @+169849 [169849] supervision q22 ? ␅
    @+169849 [169849] supervision q23 ? after
    @+169928 [169928] supplicate  q24 ? ␅
    @+169928 [169928] supplicate  q25 ? after
    @+169935 [169935] supplied    q30 ? ␅
    @+169935 [169935] supplied    q31 ? after
    @+169939 [169939] suppling    q32 ? ␅
    @+169939 [169939] suppling    q33 ? after
    @+169940 [169940] supply      q36 ? ␅
    @+169940 [169940] supply      q37 ? it
    @+169940 [169940] supply      done. it
    @+169941 [169941] supplying   q34 ? ␅
    @+169941 [169941] supplying   q35 ? before
    @+169942 [169942] support     q29 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1636 🥳 6 ⏱️ 0:01:46.926847

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:DIDIE n n n n n remain:4209
    ⬜⬜⬜⬜⬜ tried:YOBBY n n n n n remain:1502
    ⬜⬜⬜⬜⬜ tried:JUJUS n n n n n remain:289
    ⬜⬜⬜⬜⬜ tried:CRWTH n n n n n remain:57
    ⬜⬜🟩⬜⬜ tried:AGAMA n n Y n n remain:4
    🟩⬜🟩⬜⬜ tried:PZAZZ Y n Y n n remain:1

    Undos used: 2

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1779 🥳 16 ⏱️ 0:03:20.619556

📜 1 sessions
💰 score: 10000

    3/6
    CARES ⬜⬜🟨⬜🟨
    ROUST 🟨⬜🟩🟨⬜
    SLURP 🟩🟩🟩🟩🟩
    3/6
    SLURP ⬜🟨🟨⬜🟩
    TULIP ⬜🟨🟨⬜🟩
    LAYUP 🟩🟩🟩🟩🟩
    5/6
    LAYUP 🟨⬜⬜⬜⬜
    ROILS ⬜🟨⬜🟨⬜
    CLONE ⬜🟩🟩⬜🟩
    GLOBE ⬜🟩🟩🟨🟩
    BLOKE 🟩🟩🟩🟩🟩
    4/6
    BLOKE ⬜⬜⬜⬜🟩
    RAISE 🟨⬜🟩⬜🟩
    PRICE ⬜🟩🟩🟨🟩
    CRIME 🟩🟩🟩🟩🟩
    Final 1/2
    REBUS 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1756 🥳 score:22 ⏱️ 0:02:36.344109

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. BIRCH attempts:6 score:6
2. BLIND attempts:7 score:7
3. UNITY attempts:4 score:4
4. SCALP attempts:5 score:5

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1756 🥳 score:60 ⏱️ 0:02:06.523927

📜 1 sessions

Octordle Classic

1. WOMEN attempts:8 score:8
2. WHOSE attempts:7 score:7
3. ADAGE attempts:5 score:5
4. BLESS attempts:6 score:6
5. OFFAL attempts:9 score:9
6. APPLE attempts:10 score:10
7. PAPAL attempts:11 score:11
8. LEAST attempts:4 score:4

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1736 🥳 score:30 ⏱️ 0:03:20.561535

📜 1 sessions

Sedecordle Classic sedecordle.com

1. TRAMP attempts:11 score:1
2. LIGHT attempts:16 score:1
3. HAUTE attempts:3 score:0
4. NOOSE attempts:15 score:3
5. MANGO attempts:10 score:1
6. INDEX attempts:12 score:0
7. COURT attempts:6 score:0
8. WOULD attempts:9 score:6
9. ACUTE attempts:5 score:0
10. BROTH attempts:18 score:5
11. CLACK attempts:14 score:1
12. HORDE attempts:7 score:4
13. CHURN attempts:4 score:0
14. CAMEO attempts:8 score:4
15. PICKY attempts:13 score:1
16. EAGLE attempts:17 score:3

# [squareword.org](squareword.org) 🧩 #1749 🥳 7 ⏱️ 0:03:09.933013

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟨 🟨
    🟨 🟩 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T A B S
    T A R O T
    O P E R A
    M I N O R
    P R A N K

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1686 🥳 277 ⏱️ 0:01:09.410878

🤔 278 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 48 chat prompts
🤖 48 glm-5.3-flash:cloud replies
🔥   5 🥵  26 😎  51 🥶 176 🧊  19

      $1 #278 instructional   100.00°C 🥳 1000‰ ~259 used:0  [258]  source:glm
      $2 #192 instruction      65.15°C 😱  999‰   ~1 used:45 [0]    source:glm
      $3 #148 teaching         53.95°C 🔥  998‰  ~31 used:23 [30]   source:glm
      $4 #106 classroom        53.50°C 🔥  997‰  ~28 used:14 [27]   source:glm
      $5 #108 curriculum       53.21°C 🔥  996‰  ~26 used:11 [25]   source:glm
      $6 #113 learning         47.09°C 🔥  991‰  ~27 used:11 [26]   source:glm
      $7 #223 pedagogical      42.90°C 🥵  988‰  ~29 used:2  [28]   source:glm
      $8 #122 school           42.39°C 🥵  986‰   ~2 used:0  [1]    source:glm
      $9 #125 teacher          42.24°C 🥵  984‰   ~3 used:0  [2]    source:glm
     $10 #126 training         41.92°C 🥵  983‰   ~4 used:0  [3]    source:glm
     $11 #133 coursework       40.89°C 🥵  980‰   ~5 used:0  [4]    source:glm
     $33 #208 schooling        29.74°C 😎  885‰  ~32 used:0  [31]   source:glm
     $84 #241 pedagogue        19.27°C 🥶        ~87 used:0  [86]   source:glm
    $260  #60 gamma            -0.01°C 🧊       ~260 used:0  [259]  source:glm

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1719 🥳 148 ⏱️ 0:00:51.258443

🤔 149 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 16 chat prompts
🤖 16 glm-5.3-flash:cloud replies
😱  1 🔥  1 🥵 15 😎 21 🥶 65 🧊 45

      $1 #149 universitaire  100.00°C 🥳 1000‰ ~105 used:0 [104]  source:glm
      $2 #139 étudiant        70.76°C 😱  999‰   ~1 used:0 [0]    source:glm
      $3 #116 université      68.38°C 🔥  998‰   ~2 used:4 [1]    source:glm
      $4 #136 recherche       48.52°C 🥵  989‰   ~3 used:0 [2]    source:glm
      $5 #138 étude           46.08°C 🥵  986‰   ~4 used:0 [3]    source:glm
      $6 #142 master          45.22°C 🥵  984‰   ~5 used:0 [4]    source:glm
      $7 #128 diplôme         44.86°C 🥵  982‰   ~6 used:0 [5]    source:glm
      $8 #132 faculté         44.60°C 🥵  980‰   ~7 used:0 [6]    source:glm
      $9 #119 campus          43.38°C 🥵  976‰  ~16 used:2 [15]   source:glm
     $10 #130 doctorat        41.15°C 🥵  971‰   ~8 used:0 [7]    source:glm
     $11 #135 professeur      39.88°C 🥵  956‰   ~9 used:0 [8]    source:glm
     $19 #118 bourse          32.81°C 😎  863‰  ~18 used:0 [17]   source:glm
     $40  #38 patrimoine      20.07°C 🥶        ~41 used:1 [40]   source:glm
    $105  #71 poésie          -0.75°C 🧊       ~106 used:0 [105]  source:glm
