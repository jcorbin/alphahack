# 2026-06-01

- 🔗 spaceword.org 🧩 2026-05-31 🏁 score 2173 ranked 9.7% 32/329 ⏱️ 2:02:08.516890
- 🔗 alfagok.diginaut.net 🧩 #576 🥳 20 ⏱️ 0:00:24.278907
- 🔗 alphaguess.com 🧩 #1043 🥳 32 ⏱️ 0:00:32.631325
- 🔗 dontwordle.com 🧩 #1469 😳 6 ⏱️ 0:01:08.567121
- 🔗 dictionary.com hurdle 🧩 #1612 😦 18 ⏱️ 0:02:26.935859
- 🔗 Quordle Classic 🧩 #1589 🥳 score:24 ⏱️ 0:01:30.976228
- 🔗 Octordle Classic 🧩 #1589 🥳 score:52 ⏱️ 0:02:30.312775
- 🔗 squareword.org 🧩 #1582 🥳 7 ⏱️ 0:01:58.856552
- 🔗 cemantle.certitudes.org 🧩 #1519 🥳 55 ⏱️ 0:00:23.857671
- 🔗 cemantix.certitudes.org 🧩 #1552 🥳 421 ⏱️ 1:56:52.156468

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





# [spaceword.org](spaceword.org) 🧩 2026-05-31 🏁 score 2173 ranked 9.7% 32/329 ⏱️ 2:02:08.516890

📜 6 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 32/329

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ W I Z _ _ _   
      _ _ _ _ _ _ Y _ _ _   
      _ _ _ _ E _ D _ _ _   
      _ _ _ _ X _ E _ _ _   
      _ _ _ _ P E C _ _ _   
      _ _ _ _ I _ O _ _ _   
      _ _ _ _ A A S _ _ _   
      _ _ _ _ T I _ _ _ _   
      _ _ _ _ E R N _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #576 🥳 20 ⏱️ 0:00:24.278907

🤔 20 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199689 [199689] lijk      q0  ? ␅
    @+199689 [199689] lijk      q1  ? after
    @+223667 [223667] molens    q6  ? ␅
    @+223667 [223667] molens    q7  ? after
    @+223889 [223889] mond      q18 ? ␅
    @+223889 [223889] mond      q19 ? it
    @+223889 [223889] mond      done. it
    @+224287 [224287] monster   q16 ? ␅
    @+224287 [224287] monster   q17 ? before
    @+225078 [225078] mos       q14 ? ␅
    @+225078 [225078] mos       q15 ? before
    @+226591 [226591] museum    q12 ? ␅
    @+226591 [226591] museum    q13 ? before
    @+229567 [229567] natuur    q10 ? ␅
    @+229567 [229567] natuur    q11 ? before
    @+235662 [235662] odalisk   q8  ? ␅
    @+235662 [235662] odalisk   q9  ? before
    @+247660 [247660] op        q4  ? ␅
    @+247660 [247660] op        q5  ? before
    @+299441 [299441] schro     q2  ? ␅
    @+299441 [299441] schro     q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1043 🥳 32 ⏱️ 0:00:32.631325

🤔 32 attempts
📜 1 sessions

    @        [     0] aa           
    @+98216  [ 98216] mach         q0  ? ␅
    @+98216  [ 98216] mach         q1  ? after
    @+104071 [104071] minor        q8  ? ␅
    @+104071 [104071] minor        q9  ? after
    @+106937 [106937] mor          q10 ? ␅
    @+106937 [106937] mor          q11 ? az
    @+106937 [106937] mor          q12 ? ␅
    @+106937 [106937] mor          q13 ? after
    @+108417 [108417] mun          q14 ? ␅
    @+108417 [108417] mun          q15 ? after
    @+108536 [108536] murk         q20 ? ␅
    @+108536 [108536] murk         q21 ? after
    @+108580 [108580] mus          q22 ? ␅
    @+108580 [108580] mus          q23 ? after
    @+108619 [108619] musculatures q24 ? ␅
    @+108619 [108619] musculatures q25 ? after
    @+108638 [108638] mush         q26 ? ␅
    @+108638 [108638] mush         q27 ? after
    @+108648 [108648] mushing      q28 ? ␅
    @+108648 [108648] mushing      q29 ? after
    @+108650 [108650] mushroom     q30 ? ␅
    @+108650 [108650] mushroom     q31 ? it
    @+108650 [108650] mushroom     done. it
    @+108658 [108658] musical      q18 ? ␅
    @+108658 [108658] musical      q19 ? before
    @+108924 [108924] my           q16 ? ␅
    @+108924 [108924] my           q17 ? before
    @+109933 [109933] ne           q6  ? ␅
    @+109933 [109933] ne           q7  ? before
    @+122777 [122777] parr         q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1469 😳 6 ⏱️ 0:01:08.567121

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:7042
    ⬜⬜⬜⬜⬜ tried:DOODY n n n n n remain:3007
    ⬜⬜⬜🟩⬜ tried:GRRRL n n n Y n remain:121
    🟨⬜⬜🟩⬜ tried:EWERS m n n Y n remain:10
    ⬜⬜🟨🟩🟩 tried:CHARE n n m Y Y remain:5
    🟩🟩🟩🟩🟩 tried:AFIRE Y Y Y Y Y remain:0

    Undos used: 2

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1612 😦 18 ⏱️ 0:02:26.935859

📜 1 sessions
💰 score: 4860

    5/6
    SERAL ⬜⬜⬜🟨🟨
    COALY ⬜🟨🟨🟨⬜
    TALON ⬜🟨🟨🟨⬜
    ALOUD 🟩🟩🟩⬜⬜
    ALOHA 🟩🟩🟩🟩🟩
    3/6
    ALOHA ⬜🟨🟩⬜⬜
    STOLE ⬜🟨🟩🟩⬜
    TROLL 🟩🟩🟩🟩🟩
    4/6
    TROLL ⬜⬜⬜🟨⬜
    PALES ⬜⬜🟨⬜🟨
    SLINK 🟩🟩🟩⬜⬜
    SLIMY 🟩🟩🟩🟩🟩
    4/6
    SLIMY 🟨⬜⬜⬜⬜
    TRADS 🟨⬜⬜⬜🟨
    GOEST ⬜⬜🟩🟩🟩
    CHEST 🟩🟩🟩🟩🟩
    Final 2/2
    ????? 🟨⬜⬜⬜🟩
    ????? 🟩🟩⬜🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1589 🥳 score:24 ⏱️ 0:01:30.976228

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. STOOD attempts:7 score:7
2. FROND attempts:8 score:8
3. REMIT attempts:4 score:4
4. VOWEL attempts:5 score:5

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1589 🥳 score:52 ⏱️ 0:02:30.312775

📜 1 sessions

Octordle Classic Score: 

1. DEBUG attempts:6 score:6
2. NEWLY attempts:4 score:4
3. EIGHT attempts:7 score:7
4. DAISY attempts:3 score:3
5. MIRTH attempts:9 score:9
6. GAUNT attempts:8 score:8
7. BASIN attempts:5 score:5
8. CROSS attempts:10 score:10

# [squareword.org](squareword.org) 🧩 #1582 🥳 7 ⏱️ 0:01:58.856552

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟨 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S A L S A
    C L O T S
    A T T I C
    R E T R O
    F R O S T

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1519 🥳 55 ⏱️ 0:00:23.857671

🤔 56 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 6 chat prompts
🤖 6 dolphin3:latest replies
🔥  2 🥵  8 😎 13 🥶 32

     $1 #56 judicial        100.00°C 🥳 1000‰ ~56 used:0 [55]  source:dolphin3
     $2  #5 justice          58.76°C 🔥  997‰  ~2 used:8 [1]   source:dolphin3
     $3 #16 jurisprudence    50.47°C 🔥  991‰  ~1 used:6 [0]   source:dolphin3
     $4 #18 court            46.51°C 🥵  979‰  ~3 used:1 [2]   source:dolphin3
     $5 #25 legal            46.13°C 🥵  977‰  ~4 used:0 [3]   source:dolphin3
     $6 #23 judge            43.86°C 🥵  969‰  ~5 used:0 [4]   source:dolphin3
     $7 #19 criminal         41.15°C 🥵  957‰  ~6 used:0 [5]   source:dolphin3
     $8 #33 constitution     40.31°C 🥵  952‰  ~7 used:0 [6]   source:dolphin3
     $9 #24 law              37.91°C 🥵  937‰  ~8 used:0 [7]   source:dolphin3
    $10 #30 case             37.87°C 🥵  936‰  ~9 used:0 [8]   source:dolphin3
    $11 #12 fairness         36.53°C 🥵  921‰ ~10 used:0 [9]   source:dolphin3
    $12 #31 civil            35.08°C 😎  899‰ ~11 used:0 [10]  source:dolphin3
    $13 #13 judgement        34.99°C 😎  896‰ ~12 used:0 [11]  source:dolphin3
    $25 #21 enforcement      23.11°C 🥶       ~24 used:0 [23]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1552 🥳 421 ⏱️ 1:56:52.156468

🤔 422 attempts
📜 1 sessions
🫧 35 chat sessions
⁉️ 178 chat prompts
🤖 178 dolphin3:latest replies
🔥   6 🥵  32 😎 159 🥶 198 🧊  26

      $1 #422 bénéficiaire       100.00°C 🥳 1000‰ ~396 used:0  [395]  source:dolphin3
      $2 #210 versement           58.48°C 🔥  998‰  ~35 used:92 [34]   source:dolphin3
      $3 #416 allocataire         56.35°C 🔥  995‰   ~1 used:5  [0]    source:dolphin3
      $4 #189 contrat             52.63°C 🔥  993‰  ~33 used:62 [32]   source:dolphin3
      $5 #114 allocation          52.37°C 🔥  992‰  ~34 used:71 [33]   source:dolphin3
      $6 #116 attribution         52.25°C 🔥  991‰  ~19 used:41 [18]   source:dolphin3
      $7 #198 prestation          52.14°C 🔥  990‰  ~20 used:41 [19]   source:dolphin3
      $8  #50 aide                51.19°C 🥵  989‰ ~196 used:36 [195]  source:dolphin3
      $9 #327 employeur           48.82°C 🥵  984‰  ~21 used:5  [20]   source:dolphin3
     $10 #122 octroi              47.65°C 🥵  983‰  ~22 used:5  [21]   source:dolphin3
     $11 #331 salarié             47.36°C 🥵  982‰  ~23 used:5  [22]   source:dolphin3
     $40  #74 compensation        39.40°C 😎  895‰  ~36 used:0  [35]   source:dolphin3
    $199 #199 accord              24.27°C 🥶       ~198 used:0  [197]  source:dolphin3
    $397 #239 engageant           -1.84°C 🧊       ~397 used:0  [396]  source:dolphin3
