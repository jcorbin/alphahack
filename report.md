# 2026-06-04

- 🔗 spaceword.org 🧩 2026-06-03 🏁 score 2173 ranked 12.5% 42/336 ⏱️ 1:05:08.018213
- 🔗 alfagok.diginaut.net 🧩 #579 🥳 26 ⏱️ 0:00:33.558333
- 🔗 alphaguess.com 🧩 #1046 🥳 22 ⏱️ 0:00:25.856331
- 🔗 dontwordle.com 🧩 #1472 🥳 6 ⏱️ 0:01:44.559399
- 🔗 dictionary.com hurdle 🧩 #1615 😦 16 ⏱️ 0:03:50.081360
- 🔗 Quordle Classic 🧩 #1592 🥳 score:20 ⏱️ 0:01:12.570203
- 🔗 Octordle Classic 🧩 #1592 🥳 score:60 ⏱️ 0:03:23.318036
- 🔗 squareword.org 🧩 #1585 🥳 9 ⏱️ 0:03:51.631297
- 🔗 cemantle.certitudes.org 🧩 #1522 🥳 78 ⏱️ 0:01:23.236957
- 🔗 cemantix.certitudes.org 🧩 #1555 🥳 81 ⏱️ 0:01:53.618271

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








# [spaceword.org](spaceword.org) 🧩 2026-06-03 🏁 score 2173 ranked 12.5% 42/336 ⏱️ 1:05:08.018213

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 42/336

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ E T _ S U C K L E   
      _ C O M E _ O _ _ W   
      _ O _ E V I L E R _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #579 🥳 26 ⏱️ 0:00:33.558333

🤔 26 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+49817  [ 49817] boks      q6  ? ␅
    @+49817  [ 49817] boks      q7  ? after
    @+74721  [ 74721] dc        q8  ? ␅
    @+74721  [ 74721] dc        q9  ? after
    @+87180  [ 87180] draag     q10 ? ␅
    @+87180  [ 87180] draag     q11 ? after
    @+93397  [ 93397] eet       q12 ? ␅
    @+93397  [ 93397] eet       q13 ? after
    @+93998  [ 93998] eigen     q18 ? ␅
    @+93998  [ 93998] eigen     q19 ? after
    @+94217  [ 94217] eikel     q22 ? ␅
    @+94217  [ 94217] eikel     q23 ? after
    @+94295  [ 94295] eiland    q24 ? ␅
    @+94295  [ 94295] eiland    q25 ? it
    @+94295  [ 94295] eiland    done. it
    @+94443  [ 94443] einde     q20 ? ␅
    @+94443  [ 94443] einde     q21 ? before
    @+94926  [ 94926] eiwit     q16 ? ␅
    @+94926  [ 94926] eiwit     q17 ? before
    @+96536  [ 96536] energiek  q14 ? ␅
    @+96536  [ 96536] energiek  q15 ? before
    @+99704  [ 99704] ex        q4  ? ␅
    @+99704  [ 99704] ex        q5  ? before
    @+199766 [199766] lijm      q0  ? ␅
    @+199766 [199766] lijm      q1  ? after
    @+199766 [199766] lijm      q2  ? ␅
    @+199766 [199766] lijm      q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1046 🥳 22 ⏱️ 0:00:25.856331

🤔 22 attempts
📜 1 sessions

    @        [     0] aa          
    @+1      [     1] aah         
    @+2      [     2] aahed       
    @+3      [     3] aahing      
    @+98216  [ 98216] mach        q0  ? ␅
    @+98216  [ 98216] mach        q1  ? after
    @+122777 [122777] parr        q4  ? ␅
    @+122777 [122777] parr        q5  ? after
    @+128846 [128846] play        q8  ? ␅
    @+128846 [128846] play        q9  ? after
    @+131956 [131956] prearm      q10 ? ␅
    @+131956 [131956] prearm      q11 ? after
    @+132732 [132732] prehensions q14 ? ␅
    @+132732 [132732] prehensions q15 ? after
    @+133059 [133059] prep        q16 ? ␅
    @+133059 [133059] prep        q17 ? after
    @+133285 [133285] presa       q18 ? ␅
    @+133285 [133285] presa       q19 ? after
    @+133368 [133368] present     q20 ? ␅
    @+133368 [133368] present     q21 ? it
    @+133368 [133368] present     done. it
    @+133508 [133508] press       q12 ? ␅
    @+133508 [133508] press       q13 ? before
    @+135068 [135068] proper      q6  ? ␅
    @+135068 [135068] proper      q7  ? before
    @+147366 [147366] rhotic      q2  ? ␅
    @+147366 [147366] rhotic      q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1472 🥳 6 ⏱️ 0:01:44.559399

📜 1 sessions
💰 score: 88

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MAMBA n n n n n remain:5774
    ⬜⬜⬜⬜⬜ tried:HEEZE n n n n n remain:2103
    ⬜⬜⬜⬜⬜ tried:TUTUS n n n n n remain:414
    ⬜⬜⬜⬜⬜ tried:JINNI n n n n n remain:124
    ⬜⬜⬜⬜🟨 tried:GRRRL n n n n m remain:30
    ⬜🟨🟨⬜⬜ tried:CLOCK n m m n n remain:11

    Undos used: 4

      11 words remaining
    x 8 unused letters
    = 88 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1615 😦 16 ⏱️ 0:03:50.081360

📜 1 sessions
💰 score: 5060

    3/6
    HARES 🟨🟨⬜⬜⬜
    CHALK 🟩🟩🟩⬜⬜
    CHAIN 🟩🟩🟩🟩🟩
    3/6
    CHAIN 🟨⬜🟨🟩🟨
    MANIC ⬜🟨🟨🟩🟩
    ANTIC 🟩🟩🟩🟩🟩
    4/6
    ANTIC ⬜🟨🟨⬜⬜
    DENTS ⬜⬜🟨🟨⬜
    THORN 🟩🟩🟩⬜🟨
    THONG 🟩🟩🟩🟩🟩
    4/6
    THONG ⬜⬜⬜⬜⬜
    SPEAR ⬜🟨⬜⬜⬜
    IMPLY 🟨⬜🟩🟨⬜
    PUPIL 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜🟨🟩⬜⬜
    ????? ⬜⬜🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1592 🥳 score:20 ⏱️ 0:01:12.570203

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. ENSUE attempts:5 score:5
2. YACHT attempts:3 score:3
3. CURRY attempts:8 score:8
4. NASTY attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1592 🥳 score:60 ⏱️ 0:03:23.318036

📜 1 sessions

Octordle Classic

1. GUMMY attempts:8 score:8
2. PUPIL attempts:11 score:11
3. ASKEW attempts:9 score:9
4. CHASE attempts:7 score:7
5. THROW attempts:10 score:10
6. FENCE attempts:6 score:6
7. LYMPH attempts:5 score:5
8. SNIPE attempts:4 score:4

# [squareword.org](squareword.org) 🧩 #1585 🥳 9 ⏱️ 0:03:51.631297

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟨
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟨 🟩
    🟨 🟩 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T E A D
    L I M B O
    A B B O T
    S I E V E
    H A R E S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1522 🥳 78 ⏱️ 0:01:23.236957

🤔 79 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 16 chat prompts
🤖 16 dolphin3:latest replies
🥵  1 😎 15 🥶 61 🧊  1

     $1 #79 matrix          100.00°C 🥳 1000‰ ~78 used:0 [77]  source:dolphin3
     $2 #43 membrane         46.26°C 🥵  920‰  ~1 used:9 [0]   source:dolphin3
     $3 #38 organelle        44.60°C 😎  857‰ ~16 used:8 [15]  source:dolphin3
     $4 #55 cytoplasmic      44.17°C 😎  836‰ ~13 used:3 [12]  source:dolphin3
     $5 #75 cytosol          43.60°C 😎  804‰  ~2 used:0 [1]   source:dolphin3
     $6 #68 glycoprotein     41.23°C 😎  655‰  ~3 used:0 [2]   source:dolphin3
     $7 #72 vesicle          40.96°C 😎  626‰  ~4 used:0 [3]   source:dolphin3
     $8 #57 microsomal       40.81°C 😎  611‰  ~5 used:0 [4]   source:dolphin3
     $9 #32 melanocyte       40.43°C 😎  574‰ ~15 used:5 [14]  source:dolphin3
    $10 #48 epithelial       39.20°C 😎  441‰  ~6 used:0 [5]   source:dolphin3
    $11 #46 lipid            38.92°C 😎  398‰  ~7 used:0 [6]   source:dolphin3
    $12 #39 cytoplasm        38.43°C 😎  344‰ ~12 used:2 [11]  source:dolphin3
    $18 #62 ribosome         35.28°C 🥶       ~17 used:0 [16]  source:dolphin3
    $79  #8 rocket           -2.57°C 🧊       ~79 used:0 [78]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1555 🥳 81 ⏱️ 0:01:53.618271

🤔 82 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 15 chat prompts
🤖 15 dolphin3:latest replies
🥵  2 😎  5 🥶 58 🧊 16

     $1 #82 exil           100.00°C 🥳 1000‰ ~66 used:0 [65]  source:dolphin3
     $2 #56 solitude        37.57°C 🥵  968‰  ~2 used:4 [1]   source:dolphin3
     $3 #80 désertion       35.39°C 🥵  941‰  ~1 used:2 [0]   source:dolphin3
     $4 #47 adieu           29.28°C 😎  682‰  ~3 used:0 [2]   source:dolphin3
     $5 #38 mélancolie      28.76°C 😎  644‰  ~4 used:1 [3]   source:dolphin3
     $6 #48 chagrin         24.56°C 😎   81‰  ~5 used:0 [4]   source:dolphin3
     $7 #78 éloignement     24.42°C 😎   46‰  ~6 used:0 [5]   source:dolphin3
     $8 #53 perpétuité      24.40°C 😎   42‰  ~7 used:0 [6]   source:dolphin3
     $9 #67 orient          23.98°C 🥶       ~13 used:0 [12]  source:dolphin3
    $10 #55 rêverie         23.88°C 🥶       ~14 used:0 [13]  source:dolphin3
    $11 #60 tristesse       23.80°C 🥶       ~15 used:0 [14]  source:dolphin3
    $12 #16 crépuscule      22.10°C 🥶        ~8 used:8 [7]   source:dolphin3
    $13 #35 albe            21.58°C 🥶       ~11 used:3 [10]  source:dolphin3
    $67 #65 matinée         -0.11°C 🧊       ~67 used:0 [66]  source:dolphin3
