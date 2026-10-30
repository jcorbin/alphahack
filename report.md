# 2026-10-31

- 🔗 wordgrid 🧩 #882 🟪 rarity:0.27 ⏱️ 0:02:26.676059
- 🔗 spaceword.org 🧩 2026-10-30 🏁 score 2170 ranked 35.1% 108/308 ⏱️ 2:03:37.179910
- 🔗 alfagok.diginaut.net 🧩 #728 🥳 38 ⏱️ 0:00:56.343385
- 🔗 alphaguess.com 🧩 #1195 🥳 26 ⏱️ 0:00:48.540526
- 🔗 dontwordle.com 🧩 #1621 🥳 6 ⏱️ 0:01:38.514664
- 🔗 dictionary.com hurdle 🧩 #1764 🥳 19 ⏱️ 0:03:03.825524
- 🔗 Quordle Classic 🧩 #1741 🥳 score:22 ⏱️ 0:01:32.163688
- 🔗 Octordle Classic 🧩 #1741 🥳 score:52 ⏱️ 0:02:07.026951
- 🔗 Sedecordle Classic 🧩 #1721 🥳 score:39 ⏱️ 0:03:16.057332
- 🔗 squareword.org 🧩 #1734 🥳 8 ⏱️ 0:02:29.067629
- 🔗 cemantle.certitudes.org 🧩 #1671 🥳 677 ⏱️ 0:44:16.179692
- 🔗 cemantix.certitudes.org 🧩 #1704 🥳 379 ⏱️ 0:33:06.518703

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
























# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 2026-10-27 🤔 rarity:nan ⏱️ 0:01:43.563056

📜 1 sessions
🌌 🌌 🦄
🌌 🌌 🌌
🦄 🦄 🦄




# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #882 🟪 rarity:0.27 ⏱️ 0:02:26.676059

📜 2 sessions
🌌 🌌 🌌
🌌 🌌 🌌
🦄 🌌 🌌
Rarity: 0.27 🟪

# [spaceword.org](spaceword.org) 🧩 2026-10-30 🏁 score 2170 ranked 35.1% 108/308 ⏱️ 2:03:37.179910

📜 3 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 108/308

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ A R A M E S _ _   
      _ _ G _ _ I _ _ _ _   
      _ _ _ R _ K _ _ _ _   
      _ _ _ O X E Y E _ _   
      _ _ V O U D O N _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #728 🥳 38 ⏱️ 0:00:56.343385

🤔 38 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+199631 [199631] lijk        q0  ? ␅
    @+199631 [199631] lijk        q1  ? after
    @+199631 [199631] lijk        q2  ? ␅
    @+199631 [199631] lijk        q3  ? after
    @+199631 [199631] lijk        q4  ? ␅
    @+199631 [199631] lijk        q5  ? after
    @+212017 [212017] media       q12 ? ␅
    @+212017 [212017] media       q13 ? after
    @+217773 [217773] milieu      q14 ? ␅
    @+217773 [217773] milieu      q15 ? after
    @+218583 [218583] millennium  q24 ? ␅
    @+218583 [218583] millennium  q25 ? after
    @+218982 [218982] minimum     q26 ? ␅
    @+218982 [218982] minimum     q27 ? after
    @+219198 [219198] minivoetbal q28 ? ␅
    @+219198 [219198] minivoetbal q29 ? after
    @+219305 [219305] minus       q30 ? ␅
    @+219305 [219305] minus       q31 ? after
    @+219328 [219328] minuut      q36 ? ␅
    @+219328 [219328] minuut      q37 ? it
    @+219328 [219328] minuut      done. it
    @+219360 [219360] mirakel     q34 ? ␅
    @+219360 [219360] mirakel     q35 ? before
    @+219413 [219413] mis         q22 ? ␅
    @+219413 [219413] mis         q23 ? before
    @+221093 [221093] mmm         q20 ? ␅
    @+221093 [221093] mmm         q21 ? before
    @+224523 [224523] moord       q10 ? ␅
    @+224523 [224523] moord       q11 ? before
    @+249541 [249541] opi         q9  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1195 🥳 26 ⏱️ 0:00:48.540526

🤔 26 attempts
📜 2 sessions

    @        [     0] aa     
    @+1      [     1] aah    
    @+2      [     2] aahed  
    @+3      [     3] aahing 
    @+98139  [ 98139] mac    q0  ? ␅
    @+98139  [ 98139] mac    q1  ? after
    @+147301 [147301] rho    q2  ? ␅
    @+147301 [147301] rho    q3  ? after
    @+159583 [159583] slug   q6  ? ␅
    @+159583 [159583] slug   q7  ? after
    @+165737 [165737] stint  q8  ? ␅
    @+165737 [165737] stint  q9  ? after
    @+165911 [165911] stoic  q18 ? ␅
    @+165911 [165911] stoic  q19 ? after
    @+165932 [165932] stole  q24 ? ␅
    @+165932 [165932] stole  q25 ? it
    @+165932 [165932] stole  done. it
    @+165953 [165953] stoma  q22 ? ␅
    @+165953 [165953] stoma  q23 ? before
    @+165993 [165993] stomp  q20 ? ␅
    @+165993 [165993] stomp  q21 ? before
    @+166093 [166093] stop   q16 ? ␅
    @+166093 [166093] stop   q17 ? before
    @+166496 [166496] streak q14 ? ␅
    @+166496 [166496] streak q15 ? before
    @+167261 [167261] sub    q12 ? ␅
    @+167261 [167261] sub    q13 ? before
    @+168787 [168787] sulfur q10 ? ␅
    @+168787 [168787] sulfur q11 ? before
    @+171901 [171901] tag    q4  ? ␅
    @+171901 [171901] tag    q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1621 🥳 6 ⏱️ 0:01:38.514664

📜 1 sessions
💰 score: 42

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:7419
    ⬜⬜⬜⬜⬜ tried:PEEPS n n n n n remain:1350
    ⬜⬜⬜⬜⬜ tried:WHICH n n n n n remain:402
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:123
    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:18
    ⬜🟩🟩⬜🟩 tried:KOOKY n Y Y n Y remain:6

    Undos used: 4

      6 words remaining
    x 7 unused letters
    = 42 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1764 🥳 19 ⏱️ 0:03:03.825524

📜 1 sessions
💰 score: 9700

    5/6
    AROSE ⬜⬜🟩🟨⬜
    CLOPS ⬜⬜🟩⬜🟨
    SHOWN 🟩⬜🟩⬜🟨
    STONK 🟩🟨🟩🟨⬜
    SNOUT 🟩🟩🟩🟩🟩
    4/6
    SNOUT ⬜🟨⬜⬜⬜
    CLEAN ⬜🟨⬜⬜🟨
    VINYL ⬜🟨🟨🟨🟨
    LYING 🟩🟩🟩🟩🟩
    5/6
    LYING ⬜⬜⬜🟨⬜
    OCEAN ⬜⬜🟨⬜🟨
    TUNED 🟨🟨🟨🟩⬜
    MEOWS 🟨🟨⬜⬜⬜
    UNMET 🟩🟩🟩🟩🟩
    4/6
    UNMET ⬜🟨⬜🟨⬜
    SHONE 🟨⬜⬜🟨🟩
    CHILD ⬜⬜🟨⬜⬜
    RINSE 🟩🟩🟩🟩🟩
    Final 1/2
    ALONG 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1741 🥳 score:22 ⏱️ 0:01:32.163688

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. ANIME attempts:4 score:4
2. SWARM attempts:5 score:5
3. CHALK attempts:6 score:6
4. RAJAH attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1741 🥳 score:52 ⏱️ 0:02:07.026951

📜 1 sessions

Octordle Classic

1. STAMP attempts:4 score:4
2. RUSTY attempts:8 score:8
3. SLYLY attempts:6 score:6
4. SWAMI attempts:3 score:3
5. OMBRE attempts:5 score:5
6. IDIOM attempts:7 score:7
7. SNEER attempts:10 score:10
8. HAUNT attempts:9 score:9

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1721 🥳 score:39 ⏱️ 0:03:16.057332

📜 1 sessions

Sedecordle Classic sedecordle.com

1. ARRAY attempts:3 score:0
2. FAITH attempts:17 score:3
3. AUGUR attempts:5 score:0
4. SPEAK attempts:17 score:5
5. CANNY attempts:13 score:1
6. CLICK attempts:14 score:3
7. BORAX attempts:8 score:0
8. WINCH attempts:15 score:8
9. DOPEY attempts:4 score:0
10. MOTEL attempts:11 score:4
11. ALIBI attempts:7 score:0
12. UPSET attempts:6 score:7
13. SCRAM attempts:10 score:1
14. FREED attempts:12 score:0
15. SEIZE attempts:16 score:1
16. GROAN attempts:9 score:6

# [squareword.org](squareword.org) 🧩 #1734 🥳 8 ⏱️ 0:02:29.067629

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟨 🟩 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B L U R B
    L A T H E
    U N T I E
    S C E N T
    H E R O S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1671 🥳 677 ⏱️ 0:44:16.179692

🤔 678 attempts
📜 2 sessions
🫧 52 chat sessions
⁉️ 288 chat prompts
🤖 67 nemotron-3-nano:30b-cloud replies
🤖 140 llama3.2:latest replies
🤖 49 dolphin3:latest replies
🤖 32 gemma4:12b replies
😱   1 🔥   3 🥵  23 😎  77 🥶 492 🧊  81

      $1 #678 nursing            100.00°C 🥳 1000‰ ~597 used:0   [596]  source:nemotron
      $2 #508 nurse               64.25°C 😱  999‰   ~1 used:79  [0]    source:nemotron
      $3 #625 hospice             55.27°C 🔥  998‰   ~2 used:9   [1]    source:nemotron
      $4 #491 medical             50.00°C 🔥  995‰  ~27 used:33  [26]   source:nemotron
      $5 #492 hospital            49.10°C 🔥  992‰  ~19 used:20  [18]   source:nemotron
      $6 #639 caregiver           48.65°C 🥵  989‰   ~3 used:1   [2]    source:nemotron
      $7 #511 care                48.28°C 🥵  988‰  ~26 used:3   [25]   source:nemotron
      $8 #499 patient             47.50°C 🥵  987‰  ~20 used:2   [19]   source:nemotron
      $9 #525 pharmacy            47.06°C 🥵  985‰  ~21 used:2   [20]   source:nemotron
     $10 #567 radiology           45.00°C 🥵  981‰  ~22 used:2   [21]   source:nemotron
     $11 #603 pediatric           44.04°C 🥵  976‰  ~23 used:2   [22]   source:nemotron
     $29 #566 psychiatry          33.38°C 😎  884‰  ~28 used:0   [27]   source:nemotron
    $106 #579 vaccination         19.47°C 🥶       ~108 used:0   [107]  source:nemotron
    $598 #196 form                -0.05°C 🧊       ~598 used:0   [597]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1704 🥳 379 ⏱️ 0:33:06.518703

🤔 380 attempts
📜 1 sessions
🫧 15 chat sessions
⁉️ 78 chat prompts
🤖 4 nemotron-3-nano:30b-cloud replies
🤖 74 gemma4:12b replies
😱   1 🔥   3 🥵  18 😎  66 🥶 267 🧊  24

      $1 #380 apparence       100.00°C 🥳 1000‰ ~356 used:0  [355]  source:nemotron
      $2 #283 apparent         59.15°C 😱  999‰   ~2 used:64 [1]    source:gemma4  
      $3 #378 illusion         52.43°C 🔥  998‰   ~1 used:1  [0]    source:nemotron
      $4 #316 trompeur         48.01°C 🔥  994‰  ~12 used:21 [11]   source:gemma4  
      $5 #225 banal            47.75°C 🔥  993‰  ~13 used:30 [12]   source:gemma4  
      $6 #194 superficiel      46.23°C 🥵  986‰  ~81 used:16 [80]   source:gemma4  
      $7 #108 subtil           44.47°C 🥵  982‰  ~83 used:22 [82]   source:gemma4  
      $8 #160 évanescent       43.50°C 🥵  970‰  ~20 used:8  [19]   source:gemma4  
      $9 #246 évident          43.13°C 🥵  965‰  ~14 used:3  [13]   source:gemma4  
     $10 #143 pur              43.03°C 🥵  962‰  ~19 used:7  [18]   source:gemma4  
     $11 #272 réel             42.78°C 🥵  959‰   ~3 used:2  [2]    source:gemma4  
     $24 #377 simplement       39.53°C 😎  894‰  ~21 used:0  [20]   source:gemma4  
     $90 #168 infime           30.63°C 🥶        ~96 used:0  [95]   source:gemma4  
    $357 #116 fin              -0.10°C 🧊       ~357 used:0  [356]  source:gemma4  
