# 2026-09-12

- 🔗 spaceword.org 🧩 2026-09-11 🏁 score 2168 ranked 37.8% 129/341 ⏱️ 0:10:07.433202
- 🔗 wordgrid 🧩 #833 🟪 rarity:0.24 ⏱️ 0:02:04.774233
- 🔗 alfagok.diginaut.net 🧩 #679 🥳 36 ⏱️ 0:00:35.915989
- 🔗 alphaguess.com 🧩 #1146 🥳 26 ⏱️ 0:00:27.921309
- 🔗 dontwordle.com 🧩 #1572 🥳 6 ⏱️ 0:01:20.480536
- 🔗 dictionary.com hurdle 🧩 #1715 🥳 16 ⏱️ 0:02:23.095903
- 🔗 Quordle Classic 🧩 #1692 🥳 score:17 ⏱️ 0:01:10.726416
- 🔗 Octordle Classic 🧩 #1692 🥳 score:63 ⏱️ 0:01:28.806954
- 🔗 Sedecordle Classic 🧩 #1672 🥳 score:39 ⏱️ 0:02:11.311085
- 🔗 squareword.org 🧩 #1685 🥳 7 ⏱️ 0:01:52.810710
- 🔗 cemantle.certitudes.org 🧩 #1622 🥳 14 ⏱️ 0:00:32.431560
- 🔗 cemantix.certitudes.org 🧩 #1655 🥳 272 ⏱️ 0:06:07.532044

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


# [spaceword.org](spaceword.org) 🧩 2026-09-11 🏁 score 2168 ranked 37.8% 129/341 ⏱️ 0:10:07.433202

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 129/341

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ F J E L D _ _ _ _   
      _ _ E _ _ _ P _ A _   
      _ Q U I N T E _ W _   
      _ _ _ F O O T I E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 2026-09-11 🤔 rarity:nan ⏱️ 0:00:33.329642

📜 2 sessions
❓ ❓ ❓
❓ ❓ ❓
❓ ❓ ❓



# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #833 🟪 rarity:0.24 ⏱️ 0:02:04.774233

📜 5 sessions
🌌 🌌 🌌
🌌 🌌 🌌
🌌 🌌 🦄
Rarity: 0.24 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #679 🥳 36 ⏱️ 0:00:35.915989

🤔 36 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+199640 [199640] lijk      q0  ? ␅
    @+199640 [199640] lijk      q1  ? '
    @+199640 [199640] lijk      q2  ? ␅
    @+199640 [199640] lijk      q3  ? after
    @+199640 [199640] lijk      q4  ? ␅
    @+199640 [199640] lijk      q5  ? after
    @+299544 [299544] schroot   q6  ? ␅
    @+299544 [299544] schroot   q7  ? after
    @+299571 [299571] schub     q28 ? ␅
    @+299571 [299571] schub     q29 ? after
    @+299608 [299608] schuchter q30 ? ␅
    @+299608 [299608] schuchter q31 ? after
    @+299614 [299614] schudde   q32 ? ␅
    @+299614 [299614] schudde   q33 ? after
    @+299628 [299628] schudden  q34 ? ␅
    @+299628 [299628] schudden  q35 ? it
    @+299628 [299628] schudden  done. it
    @+299646 [299646] schuif    q26 ? ␅
    @+299646 [299646] schuif    q27 ? before
    @+299901 [299901] schuiven  q24 ? ␅
    @+299901 [299901] schuiven  q25 ? before
    @+300258 [300258] schuur    q22 ? ␅
    @+300258 [300258] schuur    q23 ? before
    @+301025 [301025] seks      q20 ? ␅
    @+301025 [301025] seks      q21 ? before
    @+302538 [302538] show      q18 ? ␅
    @+302538 [302538] show      q19 ? before
    @+305631 [305631] slijm     q16 ? ␅
    @+305631 [305631] slijm     q17 ? before
    @+311832 [311832] spiert    q15 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1146 🥳 26 ⏱️ 0:00:27.921309

🤔 26 attempts
📜 1 sessions

    @       [    0] aa          
    @+1     [    1] aah         
    @+2     [    2] aahed       
    @+3     [    3] aahing      
    @+47378 [47378] dis         q4  ? ␅
    @+47378 [47378] dis         q5  ? after
    @+72662 [72662] green       q6  ? ␅
    @+72662 [72662] green       q7  ? after
    @+79019 [79019] hone        q10 ? ␅
    @+79019 [79019] hone        q11 ? after
    @+82206 [82206] imbitter    q12 ? ␅
    @+82206 [82206] imbitter    q13 ? after
    @+83234 [83234] in          q14 ? ␅
    @+83234 [83234] in          q15 ? after
    @+84311 [84311] induce      q16 ? ␅
    @+84311 [84311] induce      q17 ? after
    @+84442 [84442] inefficient q22 ? ␅
    @+84442 [84442] inefficient q23 ? after
    @+84509 [84509] inevitable  q24 ? ␅
    @+84509 [84509] inevitable  q25 ? it
    @+84509 [84509] inevitable  done. it
    @+84579 [84579] infant      q20 ? ␅
    @+84579 [84579] infant      q21 ? before
    @+84849 [84849] info        q18 ? ␅
    @+84849 [84849] info        q19 ? before
    @+85397 [85397] inocula     q8  ? ␅
    @+85397 [85397] inocula     q9  ? before
    @+98147 [98147] mac         q0  ? ␅
    @+98147 [98147] mac         q1  ? after
    @+98147 [98147] mac         q2  ? ␅
    @+98147 [98147] mac         q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1572 🥳 6 ⏱️ 0:01:20.480536

📜 1 sessions
💰 score: 232

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:MORRO n n n n n remain:5248
    ⬜⬜⬜⬜⬜ tried:JEEZE n n n n n remain:2540
    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:1009
    ⬜⬜⬜⬜⬜ tried:YUPPY n n n n n remain:303
    🟨⬜⬜⬜⬜ tried:ADDAX m n n n n remain:151
    ⬜⬜🟩⬜⬜ tried:GNAWN n n Y n n remain:29

    Undos used: 4

      29 words remaining
    x 8 unused letters
    = 232 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1715 🥳 16 ⏱️ 0:02:23.095903

📜 1 sessions
💰 score: 10000

    4/6
    GEARS ⬜🟨⬜🟩⬜
    UTERI ⬜⬜🟩🟩⬜
    ONERY ⬜⬜🟩🟩🟩
    EVERY 🟩🟩🟩🟩🟩
    3/6
    EVERY ⬜🟨⬜⬜⬜
    VIALS 🟩⬜🟨🟩⬜
    VAULT 🟩🟩🟩🟩🟩
    3/6
    VAULT 🟩⬜⬜⬜⬜
    VOIDS 🟩🟨🟨🟨⬜
    VIDEO 🟩🟩🟩🟩🟩
    4/6
    VIDEO ⬜🟨⬜⬜⬜
    PARIS ⬜⬜⬜🟨🟨
    TULSI ⬜🟩⬜🟨🟨
    SUING 🟩🟩🟩🟩🟩
    Final 2/2
    SHOCK 🟩🟩🟩⬜🟩
    SHOOK 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1692 🥳 score:17 ⏱️ 0:01:10.726416

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SUPER attempts:2 score:2
2. BRUSH attempts:5 score:5
3. RESET attempts:4 score:4
4. SOWER attempts:6 score:6

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1692 🥳 score:63 ⏱️ 0:01:28.806954

📜 1 sessions

Octordle Classic

1. SCAMP attempts:10 score:10
2. CLOWN attempts:11 score:11
3. SOGGY attempts:4 score:4
4. GUIDE attempts:7 score:7
5. NIECE attempts:12 score:12
6. FEMUR attempts:8 score:8
7. AMASS attempts:6 score:6
8. ASSAY attempts:5 score:5

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1672 🥳 score:39 ⏱️ 0:02:11.311085

📜 1 sessions

Sedecordle Classic sedecordle.com

1. MOTOR attempts:7 score:0
2. ZESTY attempts:12 score:7
3. ANNOY attempts:8 score:0
4. REARM attempts:9 score:8
5. VISTA attempts:5 score:0
6. HUSKY attempts:18 score:5
7. EARLY attempts:3 score:0
8. CLACK attempts:20 score:3
9. RIGID attempts:6 score:0
10. PYGMY attempts:10 score:6
11. TROLL attempts:11 score:1
12. ACTOR attempts:13 score:1
13. LEARN attempts:2 score:0
14. SMALL attempts:14 score:2
15. AMITY attempts:15 score:1
16. TAPER attempts:16 score:5

# [squareword.org](squareword.org) 🧩 #1685 🥳 7 ⏱️ 0:01:52.810710

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    G L U E D
    R O N D O
    A T T I C
    S T I C K
    P O E T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1622 🥳 14 ⏱️ 0:00:32.431560

🤔 15 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 4 chat prompts
🤖 4 qwen3.8:latest replies
🥵 2 😎 1 🥶 8 🧊 3

     $1 #15 airport     100.00°C 🥳 1000‰ ~12 used:0 [11]  source:qwen3
     $2 #13 aviation     50.10°C 🥵  987‰  ~1 used:0 [0]   source:qwen3
     $3 #14 aircraft     47.29°C 🥵  981‰  ~2 used:0 [1]   source:qwen3
     $4 #11 autopilot    19.87°C 😎  264‰  ~3 used:0 [2]   source:qwen3
     $5  #1 drone        17.76°C 🥶        ~4 used:1 [3]   source:qwen3
     $6  #8 vortex        8.69°C 🥶        ~5 used:0 [4]   source:qwen3
     $7  #2 glitch        8.11°C 🥶        ~6 used:0 [5]   source:qwen3
     $8  #9 whisper       5.18°C 🥶        ~7 used:0 [6]   source:qwen3
     $9  #5 quantum       4.67°C 🥶        ~8 used:0 [7]   source:qwen3
    $10 #10 zephyr        3.86°C 🥶        ~9 used:0 [8]   source:qwen3
    $11  #7 squeeze       2.94°C 🥶       ~10 used:0 [9]   source:qwen3
    $12  #6 saffron       1.98°C 🥶       ~11 used:0 [10]  source:qwen3
    $13  #4 nebula       -0.79°C 🧊       ~13 used:0 [12]  source:qwen3
    $14 #12 automation   -1.54°C 🧊       ~14 used:0 [13]  source:qwen3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1655 🥳 272 ⏱️ 0:06:07.532044

🤔 273 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 54 chat prompts
🤖 54 qwen3.8:latest replies
🔥   1 🥵   2 😎  40 🥶 208 🧊  21

      $1 #273 sémantique       100.00°C 🥳 1000‰ ~252 used:0  [251]  source:qwen3
      $2 #272 syntaxe           57.16°C 🔥  992‰   ~1 used:0  [0]    source:qwen3
      $3 #264 formalisme        49.08°C 🥵  959‰   ~2 used:0  [1]    source:qwen3
      $4  #81 isomorphisme      45.25°C 🥵  908‰  ~40 used:41 [39]   source:qwen3
      $5 #260 concept           43.66°C 😎  880‰   ~3 used:0  [2]    source:qwen3
      $6  #80 invariant         43.18°C 😎  868‰  ~43 used:26 [42]   source:qwen3
      $7  #96 foncteur          43.05°C 😎  865‰  ~42 used:15 [41]   source:qwen3
      $8 #262 définition        42.34°C 😎  848‰   ~4 used:0  [3]    source:qwen3
      $9 #216 abstraction       42.04°C 😎  840‰  ~12 used:2  [11]   source:qwen3
     $10  #90 morphisme         41.44°C 😎  827‰  ~39 used:4  [38]   source:qwen3
     $11  #93 algébrique        40.15°C 😎  786‰  ~13 used:2  [12]   source:qwen3
     $12 #267 lemme             39.91°C 😎  780‰   ~5 used:0  [4]    source:qwen3
     $45 #270 postulat          27.74°C 🥶        ~49 used:0  [48]   source:qwen3
    $253 #203 rang              -0.12°C 🧊       ~253 used:0  [252]  source:qwen3
