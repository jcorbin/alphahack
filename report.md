# 2026-10-16

- 🔗 spaceword.org 🧩 2026-10-15 🏁 score 2168 ranked 48.9% 151/309 ⏱️ 0:30:07.894328
- 🔗 wordgrid 🧩 #867 🟪 rarity:0.12 ⏱️ 0:02:18.850263
- 🔗 alfagok.diginaut.net 🧩 #713 🥳 18 ⏱️ 0:00:33.601253
- 🔗 alphaguess.com 🧩 #1180 🥳 36 ⏱️ 0:00:38.447362
- 🔗 dontwordle.com 🧩 #1606 🥳 6 ⏱️ 0:01:34.024296
- 🔗 dictionary.com hurdle 🧩 #1749 🥳 17 ⏱️ 0:03:00.109082
- 🔗 Quordle Classic 🧩 #1726 🥳 score:24 ⏱️ 0:01:27.978991
- 🔗 Octordle Classic 🧩 #1726 🥳 score:52 ⏱️ 0:01:37.982508
- 🔗 Sedecordle Classic 🧩 #1706 🥳 score:49 ⏱️ 0:03:06.026346
- 🔗 squareword.org 🧩 #1719 🥳 7 ⏱️ 0:01:48.717804
- 🔗 cemantle.certitudes.org 🧩 #1656 🥳 139 ⏱️ 0:06:48.504473
- 🔗 cemantix.certitudes.org 🧩 #1689 🥳 177 ⏱️ 0:14:08.104752

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












# [spaceword.org](spaceword.org) 🧩 2026-10-15 🏁 score 2168 ranked 48.9% 151/309 ⏱️ 0:30:07.894328

📜 2 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 151/309

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ O X I M E S _ P _   
      _ _ _ L A _ K _ E _   
      _ Q U I N T I C S _   
      _ _ _ A E _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #867 🟪 rarity:0.12 ⏱️ 0:02:18.850263

📜 2 sessions
🌌 🌌 🌌
🌌 🦄 🌌
🌌 🦄 🌌
Rarity: 0.12 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #713 🥳 18 ⏱️ 0:00:33.601253

🤔 18 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+8646   [  8646] af        q8  ? ␅
    @+8646   [  8646] af        q9  ? after
    @+16147  [ 16147] am        q10 ? ␅
    @+16147  [ 16147] am        q11 ? after
    @+17101  [ 17101] analyse   q16 ? ␅
    @+17101  [ 17101] analyse   q17 ? it
    @+17101  [ 17101] analyse   done. it
    @+18102  [ 18102] anti      q14 ? ␅
    @+18102  [ 18102] anti      q15 ? before
    @+20508  [ 20508] arglist   q12 ? ␅
    @+20508  [ 20508] arglist   q13 ? b 
    @+24874  [ 24874] bad       q6  ? ␅
    @+24874  [ 24874] bad       q7  ? before
    @+49802  [ 49802] boks      q4  ? ␅
    @+49802  [ 49802] boks      q5  ? before
    @+99672  [ 99672] ex        q2  ? ␅
    @+99672  [ 99672] ex        q3  ? before
    @+199631 [199631] lijk      q0  ? ␅
    @+199631 [199631] lijk      q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1180 🥳 36 ⏱️ 0:00:38.447362

🤔 36 attempts
📜 1 sessions

    @        [     0] aa             
    @+98142  [ 98142] mac            q0  ? ␅
    @+98142  [ 98142] mac            q1  ? after
    @+147304 [147304] rho            q2  ? ␅
    @+147304 [147304] rho            q3  ? after
    @+159586 [159586] slug           q6  ? ␅
    @+159586 [159586] slug           q7  ? after
    @+165740 [165740] stint          q8  ? ␅
    @+165740 [165740] stint          q9  ? after
    @+168790 [168790] sulfur         q10 ? ␅
    @+168790 [168790] sulfur         q11 ? after
    @+169216 [169216] super          q14 ? ␅
    @+169216 [169216] super          q15 ? after
    @+169691 [169691] supers         q16 ? ␅
    @+169691 [169691] supers         q17 ? after
    @+169855 [169855] supervision    q20 ? ␅
    @+169855 [169855] supervision    q21 ? after
    @+169934 [169934] supplicate     q22 ? ␅
    @+169934 [169934] supplicate     q23 ? after
    @+169941 [169941] supplied       q28 ? ␅
    @+169941 [169941] supplied       q29 ? after
    @+169943 [169943] suppliers      q32 ? ␅
    @+169943 [169943] suppliers      q33 ? after
    @+169944 [169944] supplies       q34 ? ␅
    @+169944 [169944] supplies       q35 ? it
    @+169944 [169944] supplies       done. it
    @+169945 [169945] suppling       q30 ? ␅
    @+169945 [169945] suppling       q31 ? before
    @+169948 [169948] support        q26 ? ␅
    @+169948 [169948] support        q27 ? before
    @+169976 [169976] supposititious q25 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1606 🥳 6 ⏱️ 0:01:34.024296

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:TUTUS n n n n n remain:4338
    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:2187
    ⬜⬜⬜⬜⬜ tried:RECCE n n n n n remain:388
    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:148
    ⬜⬜⬜🟨⬜ tried:GHYLL n n n m n remain:11
    ⬜🟩🟩⬜⬜ tried:FLOWN n Y Y n n remain:4

    Undos used: 4

      4 words remaining
    x 6 unused letters
    = 24 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1749 🥳 17 ⏱️ 0:03:00.109082

📜 1 sessions
💰 score: 9900

    3/6
    LEARS ⬜🟩🟩🟩⬜
    DEARY ⬜🟩🟩🟩⬜
    HEART 🟩🟩🟩🟩🟩
    5/6
    HEART ⬜⬜⬜⬜⬜
    NOILS 🟨⬜🟨⬜⬜
    MINCY ⬜🟩🟩⬜🟩
    GAPED ⬜⬜⬜⬜🟨
    WINDY 🟩🟩🟩🟩🟩
    4/6
    WINDY ⬜⬜⬜⬜⬜
    LOSER ⬜🟨⬜⬜🟩
    TUMOR ⬜🟩⬜🟩🟩
    JUROR 🟩🟩🟩🟩🟩
    4/6
    JUROR ⬜⬜⬜⬜⬜
    AISLE ⬜🟩⬜⬜🟨
    WIDEN ⬜🟩🟩🟩⬜
    BIDET 🟩🟩🟩🟩🟩
    Final 1/2
    BLEAT 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1726 🥳 score:24 ⏱️ 0:01:27.978991

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SHORT attempts:5 score:5
2. WORTH attempts:7 score:7
3. JOIST attempts:8 score:8
4. SLUNK attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1726 🥳 score:52 ⏱️ 0:01:37.982508

📜 1 sessions

Octordle Classic

1. ABUSE attempts:7 score:7
2. BELLE attempts:5 score:5
3. AXIOM attempts:10 score:10
4. FALSE attempts:6 score:6
5. DECOR attempts:3 score:3
6. VICAR attempts:4 score:4
7. TRUER attempts:8 score:8
8. FEWER attempts:9 score:9

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1706 🥳 score:49 ⏱️ 0:03:06.026346

📜 1 sessions

Sedecordle Classic sedecordle.com

1. VINYL attempts:3 score:0
2. CRONY attempts:17 score:3
3. CHURN attempts:16 score:1
4. AWFUL attempts:13 score:6
5. TRASH attempts:12 score:1
6. MUNCH attempts:10 score:2
7. FABLE attempts:14 score:1
8. SHANK attempts:11 score:4
9. BASIS attempts:15 score:1
10. GUISE attempts:6 score:5
11. PARER attempts:17 score:1
12. AXIOM attempts:8 score:8
13. RIGOR attempts:7 score:0
14. TAKEN attempts:5 score:7
15. PATSY attempts:9 score:0
16. OLIVE attempts:4 score:9

# [squareword.org](squareword.org) 🧩 #1719 🥳 7 ⏱️ 0:01:48.717804

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟨 🟩
    🟩 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T I R S
    T E N O N
    U N D U E
    B E I G E
    S T E E R

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1656 🥳 139 ⏱️ 0:06:48.504473

🤔 140 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 42 chat prompts
🤖 42 dolphin3:latest replies
🔥  1 🥵  8 😎 31 🥶 97 🧊  2

      $1 #140 dignity         100.00°C 🥳 1000‰ ~138 used:0  [137]  source:dolphin3
      $2  #97 dignified        59.82°C 😱  999‰   ~1 used:15 [0]    source:dolphin3
      $3 #139 decorum          47.87°C 🥵  982‰   ~2 used:0  [1]    source:dolphin3
      $4  #94 honorable        47.30°C 🥵  980‰   ~4 used:8  [3]    source:dolphin3
      $5  #32 courage          46.36°C 🥵  975‰  ~40 used:25 [39]   source:dolphin3
      $6  #47 steadfastness    44.37°C 🥵  960‰  ~38 used:16 [37]   source:dolphin3
      $7  #38 fortitude        41.00°C 🥵  929‰  ~37 used:13 [36]   source:dolphin3
      $8  #72 indomitability   40.87°C 🥵  926‰   ~5 used:10 [4]    source:dolphin3
      $9  #44 spirit           40.30°C 🥵  917‰  ~36 used:11 [35]   source:dolphin3
     $10 #124 respectful       39.63°C 🥵  908‰   ~3 used:1  [2]    source:dolphin3
     $11 #109 dignifying       37.93°C 😎  862‰   ~6 used:0  [5]    source:dolphin3
     $12  #56 stoicism         37.83°C 😎  859‰  ~39 used:2  [38]   source:dolphin3
     $42  #78 stability        28.51°C 🥶        ~46 used:0  [45]   source:dolphin3
    $139   #6 quantum          -0.50°C 🧊       ~139 used:0  [138]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1689 🥳 177 ⏱️ 0:14:08.104752

🤔 178 attempts
📜 1 sessions
🫧 15 chat sessions
⁉️ 83 chat prompts
🤖 83 dolphin3:latest replies
😱  1 🔥  2 🥵 15 😎 67 🥶 73 🧊 19

      $1 #178 orienter           100.00°C 🥳 1000‰ ~159 used:0  [158]  source:dolphin3
      $2 #166 orientation         54.90°C 😱  999‰   ~2 used:15 [1]    source:dolphin3
      $3 #169 structurer          51.26°C 🔥  998‰   ~3 used:7  [2]    source:dolphin3
      $4 #177 réorienter          45.30°C 🔥  993‰   ~1 used:1  [0]    source:dolphin3
      $5  #70 structure           41.95°C 🥵  977‰  ~85 used:53 [84]   source:dolphin3
      $6  #88 approche            41.16°C 🥵  970‰  ~82 used:32 [81]   source:dolphin3
      $7  #58 évoluer             40.21°C 🥵  962‰  ~76 used:20 [75]   source:dolphin3
      $8 #164 connaissance        40.05°C 🥵  959‰   ~4 used:1  [3]    source:dolphin3
      $9 #105 technique           38.58°C 🥵  947‰  ~15 used:9  [14]   source:dolphin3
     $10 #171 structuration       38.52°C 🥵  946‰   ~5 used:0  [4]    source:dolphin3
     $11  #86 évolution           38.31°C 🥵  943‰   ~9 used:8  [8]    source:dolphin3
     $20  #28 formation           35.22°C 😎  897‰  ~84 used:5  [83]   source:dolphin3
     $87 #168 orienté             22.64°C 🥶        ~87 used:0  [86]   source:dolphin3
    $160  #22 livre               -0.55°C 🧊       ~160 used:0  [159]  source:dolphin3
