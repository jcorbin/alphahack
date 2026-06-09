# 2026-06-10

- 🔗 spaceword.org 🧩 2026-06-09 🏁 score 2173 ranked 10.3% 34/329 ⏱️ 1:30:53.416181
- 🔗 alphaguess.com 🧩 #1052 🥳 24 ⏱️ 0:00:30.463883
- 🔗 dontwordle.com 🧩 #1478 🥳 6 ⏱️ 0:01:25.401687
- 🔗 dictionary.com hurdle 🧩 #1621 🥳 16 ⏱️ 0:04:52.340815
- 🔗 Quordle Classic 🧩 #1598 🥳 score:18 ⏱️ 0:01:05.127619
- 🔗 Octordle Classic 🧩 #1598 🥳 score:55 ⏱️ 0:03:05.322263
- 🔗 squareword.org 🧩 #1591 🥳 7 ⏱️ 0:01:55.208533
- 🔗 cemantle.certitudes.org 🧩 #1528 🥳 484 ⏱️ 0:05:54.518243

# 2026-06-09

- 🔗 alfagok.diginaut.net 🧩 #585 🥳 38 ⏱️ 0:00:39.550341
- 🔗 cemantix.certitudes.org 🧩 #1561 🥳 122 ⏱️ 0:01:47.731838

# 2026-06-10

- 🔗 spaceword.org 🧩 2026-06-09 🏗️ score 2173 current ranking 26/265 ⏱️ 1:30:45.973110

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
























































































# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1585 😦 score:32 ⏱️ 0:02:33.513959

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. GRAPE attempts:8 score:8
2. VALUE attempts:9 score:9
3. YEARN attempts:6 score:6
4. IN_ER -ACDGHLMPSTUVWYZ attempts:9 score:-1














# [spaceword.org](spaceword.org) 🧩 2026-06-09 🏁 score 2173 ranked 10.3% 34/329 ⏱️ 1:30:53.416181

📜 11 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 34/329

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ Y E W _ _ _   
      _ _ _ _ _ Q _ _ _ _   
      _ _ _ _ _ U T _ _ _   
      _ _ _ _ K I R _ _ _   
      _ _ _ _ A T E _ _ _   
      _ _ _ _ _ Y E _ _ _   
      _ _ _ _ _ _ I _ _ _   
      _ _ _ _ E O N _ _ _   
      _ _ _ _ S I G _ _ _   

# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #585 🥳 38 ⏱️ 0:00:39.550341

🤔 38 attempts
📜 1 sessions

    @       [    0] &-teken     
    @+24887 [24887] bad         q8  ? ␅
    @+24887 [24887] bad         q9  ? after
    @+37348 [37348] beschermen  q10 ? ␅
    @+37348 [37348] beschermen  q11 ? after
    @+40187 [40187] beurst      q14 ? ␅
    @+40187 [40187] beurst      q15 ? after
    @+40513 [40513] bever       q20 ? ␅
    @+40513 [40513] bever       q21 ? after
    @+40555 [40555] bevestig    q32 ? ␅
    @+40555 [40555] bevestig    q33 ? after
    @+40559 [40559] bevestigen  q36 ? ␅
    @+40559 [40559] bevestigen  q37 ? it
    @+40559 [40559] bevestigen  done. it
    @+40563 [40563] bevestiging q34 ? ␅
    @+40563 [40563] bevestiging q35 ? before
    @+40591 [40591] bevind      q24 ? ␅
    @+40591 [40591] bevind      q25 ? before
    @+40690 [40690] bevoegd     q22 ? ␅
    @+40690 [40690] bevoegd     q23 ? before
    @+40886 [40886] bevracht    q18 ? ␅
    @+40886 [40886] bevracht    q19 ? before
    @+41600 [41600] bewonder    q16 ? ␅
    @+41600 [41600] bewonder    q17 ? before
    @+43033 [43033] bij         q12 ? ␅
    @+43033 [43033] bij         q13 ? before
    @+49812 [49812] boks        q4  ? ␅
    @+49812 [49812] boks        q5  ? bn
    @+49812 [49812] boks        q6  ? ␅
    @+49812 [49812] boks        q7  ? before
    @+99699 [99699] ex          q3  ? before

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1561 🥳 122 ⏱️ 0:01:47.731838

🤔 123 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 22 chat prompts
🤖 22 dolphin3:latest replies
🔥  2 🥵  4 😎 11 🥶 84 🧊 21

      $1 #123 étiquette      100.00°C 🥳 1000‰ ~102 used:0  [101]  source:dolphin3
      $2 #103 emballage       44.23°C 🔥  996‰   ~2 used:6  [1]    source:dolphin3
      $3 #113 blister         41.42°C 🔥  993‰   ~1 used:2  [0]    source:dolphin3
      $4 #105 packaging       32.71°C 🥵  964‰   ~3 used:1  [2]    source:dolphin3
      $5 #102 carton          32.45°C 🥵  960‰   ~4 used:0  [3]    source:dolphin3
      $6  #95 papier          31.34°C 🥵  949‰   ~5 used:1  [4]    source:dolphin3
      $7 #108 boîte           30.77°C 🥵  939‰   ~6 used:0  [5]    source:dolphin3
      $8 #122 sachet          26.84°C 😎  860‰   ~7 used:0  [6]    source:dolphin3
      $9  #86 feuillet        26.28°C 😎  839‰   ~8 used:1  [7]    source:dolphin3
     $10  #84 feuille         25.77°C 😎  824‰  ~16 used:2  [15]   source:dolphin3
     $11 #112 étui            25.43°C 😎  815‰   ~9 used:0  [8]    source:dolphin3
     $12 #104 enveloppe       24.70°C 😎  784‰  ~10 used:0  [9]    source:dolphin3
     $19 #110 coffret         17.99°C 🥶        ~23 used:0  [22]   source:dolphin3
    $103  #54 sel             -0.13°C 🧊       ~103 used:0  [102]  source:dolphin3








# [alphaguess.com](alphaguess.com) 🧩 #1052 🥳 24 ⏱️ 0:00:30.463883

🤔 24 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+5876  [ 5876] angel      q8  ? ␅
    @+5876  [ 5876] angel      q9  ? after
    @+5893  [ 5893] anger      q22 ? ␅
    @+5893  [ 5893] anger      q23 ? it
    @+5893  [ 5893] anger      done. it
    @+5914  [ 5914] angioma    q20 ? ␅
    @+5914  [ 5914] angioma    q21 ? before
    @+5957  [ 5957] anglo      q18 ? ␅
    @+5957  [ 5957] anglo      q19 ? before
    @+6041  [ 6041] animal     q16 ? ␅
    @+6041  [ 6041] animal     q17 ? before
    @+6254  [ 6254] annuitants q14 ? ␅
    @+6254  [ 6254] annuitants q15 ? before
    @+6632  [ 6632] anti       q12 ? ␅
    @+6632  [ 6632] anti       q13 ? before
    @+8323  [ 8323] ar         q10 ? ␅
    @+8323  [ 8323] ar         q11 ? before
    @+11763 [11763] back       q6  ? ␅
    @+11763 [11763] back       q7  ? before
    @+23681 [23681] camp       q4  ? ␅
    @+23681 [23681] camp       q5  ? before
    @+47380 [47380] dis        q2  ? ␅
    @+47380 [47380] dis        q3  ? before
    @+98214 [98214] mach       q0  ? ␅
    @+98214 [98214] mach       q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1478 🥳 6 ⏱️ 0:01:25.401687

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MAGMA n n n n n remain:5731
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:3410
    ⬜⬜⬜⬜⬜ tried:JESSE n n n n n remain:504
    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:160
    ⬜⬜⬜⬜🟩 tried:NUDZH n n n n Y remain:18
    🟩🟩⬜⬜🟩 tried:TOOTH Y Y n n Y remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score


# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1621 🥳 16 ⏱️ 0:04:52.340815

📜 1 sessions
💰 score: 10000

    3/6
    YEARS ⬜⬜⬜⬜⬜
    LUDIC ⬜🟨🟩🟩⬜
    UNDID 🟩🟩🟩🟩🟩
    4/6
    UNDID ⬜⬜⬜🟨⬜
    LIERS ⬜🟩⬜⬜⬜
    PITHY 🟨🟩⬜🟨⬜
    HIPPO 🟩🟩🟩🟩🟩
    3/6
    HIPPO ⬜⬜⬜⬜🟩
    MACRO ⬜⬜🟩⬜🟩
    GECKO 🟩🟩🟩🟩🟩
    4/6
    GECKO 🟩🟩⬜⬜⬜
    GENTS 🟩🟩🟩⬜⬜
    GENRE 🟩🟩🟩⬜🟩
    GENIE 🟩🟩🟩🟩🟩
    Final 2/2
    GATED 🟩⬜⬜🟩🟩
    GREED 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1598 🥳 score:18 ⏱️ 0:01:05.127619

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. BELIE attempts:5 score:5
2. TEACH attempts:6 score:6
3. GUEST attempts:3 score:3
4. NOOSE attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1598 🥳 score:55 ⏱️ 0:03:05.322263

📜 1 sessions

Octordle Classic

1. BASIC attempts:4 score:4
2. BURLY attempts:5 score:5
3. PLAIN attempts:3 score:3
4. FREER attempts:9 score:9
5. PLAID attempts:6 score:6
6. YIELD attempts:7 score:7
7. MOIST attempts:10 score:10
8. CLICK attempts:11 score:11

# [squareword.org](squareword.org) 🧩 #1591 🥳 7 ⏱️ 0:01:55.208533

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    R A R E R
    A L O N E
    N O V A E
    C H E C K
    H A R T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1528 🥳 484 ⏱️ 0:05:54.518243

🤔 485 attempts
📜 1 sessions
🫧 19 chat sessions
⁉️ 98 chat prompts
🤖 98 dolphin3:latest replies
🔥   2 🥵  15 😎  69 🥶 377 🧊  21

      $1 #485 missile           100.00°C 🥳 1000‰ ~464 used:0  [463]  source:dolphin3
      $2 #333 drone              51.43°C 🔥  993‰   ~9 used:35 [8]    source:dolphin3
      $3 #390 unmanned           47.53°C 🔥  990‰   ~3 used:18 [2]    source:dolphin3
      $4 #222 aircraft           45.67°C 🥵  986‰  ~78 used:30 [77]   source:dolphin3
      $5 #472 spacecraft         42.51°C 🥵  974‰   ~4 used:2  [3]    source:dolphin3
      $6 #478 ballistic          40.92°C 🥵  967‰   ~1 used:0  [0]    source:dolphin3
      $7 #456 satellite          40.38°C 🥵  963‰   ~5 used:2  [4]    source:dolphin3
      $8 #393 payload            39.82°C 🥵  961‰  ~10 used:4  [9]    source:dolphin3
      $9 #428 reconnaissance     38.10°C 🥵  956‰   ~7 used:3  [6]    source:dolphin3
     $10 #477 orbit              36.97°C 🥵  951‰   ~2 used:0  [1]    source:dolphin3
     $11 #215 airliner           35.29°C 🥵  940‰  ~76 used:18 [75]   source:dolphin3
     $19 #433 intelligence       30.80°C 😎  887‰  ~15 used:0  [14]   source:dolphin3
     $88 #204 refuel             18.80°C 🥶        ~93 used:0  [92]   source:dolphin3
    $465 #112 emergence          -0.48°C 🧊       ~465 used:0  [464]  source:dolphin3
