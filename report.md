# 2026-02-23

- 🔗 spaceword.org 🧩 2026-02-22 🏁 score 2168 ranked 40.4% 135/334 ⏱️ 13:07:17.272728
- 🔗 alfagok.diginaut.net 🧩 #478 🥳 22 ⏱️ 0:00:27.022747
- 🔗 alphaguess.com 🧩 #945 🥳 24 ⏱️ 0:00:30.231473
- 🔗 dontwordle.com 🧩 #1371 🥳 6 ⏱️ 0:01:57.224620
- 🔗 dictionary.com hurdle 🧩 #1514 😦 19 ⏱️ 0:03:21.008520
- 🔗 Quordle Classic 🧩 #1491 😦 score:29 ⏱️ 0:02:35.824014
- 🔗 Octordle Classic 🧩 #1491 🥳 score:51 ⏱️ 0:02:51.409608
- 🔗 squareword.org 🧩 #1484 🥳 8 ⏱️ 0:02:21.520586
- 🔗 cemantle.certitudes.org 🧩 #1421 🥳 164 ⏱️ 0:01:40.897967
- 🔗 cemantix.certitudes.org 🧩 #1454 🥳 44 ⏱️ 0:00:56.255308

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





# [spaceword.org](spaceword.org) 🧩 2026-02-22 🏁 score 2168 ranked 40.4% 135/334 ⏱️ 13:07:17.272728

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 135/334

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ G O _ J _ _ _ K _   
      _ A X _ U _ _ _ I _   
      _ P O U T E D _ R _   
      _ _ _ H E R O I N _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #478 🥳 22 ⏱️ 0:00:27.022747

🤔 22 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199816 [199816] lijm      q0  ? ␅
    @+199816 [199816] lijm      q1  ? after
    @+299721 [299721] schub     q2  ? ␅
    @+299721 [299721] schub     q3  ? after
    @+324287 [324287] sub       q6  ? ␅
    @+324287 [324287] sub       q7  ? after
    @+325783 [325783] suïcide   q14 ? ␅
    @+325783 [325783] suïcide   q15 ? after
    @+326117 [326117] syncope   q18 ? ␅
    @+326117 [326117] syncope   q19 ? after
    @+326242 [326242] systeem   q20 ? ␅
    @+326242 [326242] systeem   q21 ? it
    @+326242 [326242] systeem   done. it
    @+326464 [326464] taak      q16 ? ␅
    @+326464 [326464] taak      q17 ? before
    @+327278 [327278] tafel     q12 ? ␅
    @+327278 [327278] tafel     q13 ? before
    @+330470 [330470] televisie q10 ? ␅
    @+330470 [330470] televisie q11 ? before
    @+336882 [336882] toetsing  q8  ? ␅
    @+336882 [336882] toetsing  q9  ? before
    @+349489 [349489] vakantie  q4  ? ␅
    @+349489 [349489] vakantie  q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #945 🥳 24 ⏱️ 0:00:30.231473

🤔 24 attempts
📜 1 sessions

    @       [    0] aa            
    @+1     [    1] aah           
    @+2     [    2] aahed         
    @+3     [    3] aahing        
    @+5876  [ 5876] angel         q8  ? ␅
    @+5876  [ 5876] angel         q9  ? after
    @+8323  [ 8323] ar            q10 ? ␅
    @+8323  [ 8323] ar            q11 ? after
    @+9341  [ 9341] as            q12 ? ␅
    @+9341  [ 9341] as            q13 ? after
    @+9947  [ 9947] asthenosphere q16 ? ␅
    @+9947  [ 9947] asthenosphere q17 ? after
    @+10247 [10247] atonal        q18 ? ␅
    @+10247 [10247] atonal        q19 ? after
    @+10316 [10316] attach        q22 ? ␅
    @+10316 [10316] attach        q23 ? it
    @+10316 [10316] attach        done. it
    @+10396 [10396] attest        q20 ? ␅
    @+10396 [10396] attest        q21 ? before
    @+10553 [10553] audient       q14 ? ␅
    @+10553 [10553] audient       q15 ? before
    @+11764 [11764] back          q6  ? ␅
    @+11764 [11764] back          q7  ? before
    @+23682 [23682] camp          q4  ? ␅
    @+23682 [23682] camp          q5  ? before
    @+47381 [47381] dis           q2  ? ␅
    @+47381 [47381] dis           q3  ? before
    @+98218 [98218] mach          q0  ? ␅
    @+98218 [98218] mach          q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1371 🥳 6 ⏱️ 0:01:57.224620

📜 1 sessions
💰 score: 12

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:PAPAW n n n n n remain:5916
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:2890
    ⬜⬜⬜⬜⬜ tried:SEEKS n n n n n remain:452
    ⬜⬜⬜⬜⬜ tried:MYTHY n n n n n remain:66
    ⬜🟨⬜⬜⬜ tried:BONGO n m n n n remain:10
    ⬜🟨🟩🟨⬜ tried:QUOLL n m Y m n remain:2

    Undos used: 4

      2 words remaining
    x 6 unused letters
    = 12 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1514 😦 19 ⏱️ 0:03:21.008520

📜 1 sessions
💰 score: 4750

    5/6
    LARES ⬜⬜⬜🟨⬜
    DEIGN ⬜🟩⬜⬜⬜
    HEMPY ⬜🟩🟩🟩⬜
    KEMPT ⬜🟩🟩🟩🟨
    TEMPO 🟩🟩🟩🟩🟩
    5/6
    TEMPO ⬜🟨⬜🟨⬜
    LAPSE ⬜⬜🟩⬜🟨
    RIPED 🟨⬜🟩🟩⬜
    HYPER ⬜⬜🟩🟩🟩
    UPPER 🟩🟩🟩🟩🟩
    4/6
    UPPER ⬜⬜⬜🟩⬜
    SAVED 🟩⬜⬜🟩⬜
    SINEW 🟩⬜⬜🟩🟨
    SWEET 🟩🟩🟩🟩🟩
    3/6
    SWEET 🟨⬜🟨⬜🟩
    HEIST ⬜🟨🟩🟩🟩
    EXIST 🟩🟩🟩🟩🟩
    Final 2/2
    ????? 🟨🟩⬜⬜⬜
    ????? ⬜🟩🟩🟨🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1491 😦 score:29 ⏱️ 0:02:35.824014

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SLINK attempts:5 score:5
2. SUMAC attempts:7 score:7
3. FORAY attempts:8 score:8
4. _RAWN -CDEFGIKLMOSTUY attempts:9 score:-1

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1491 🥳 score:51 ⏱️ 0:02:51.409608

📜 1 sessions

Octordle Classic

1. REPEL attempts:8 score:8
2. STONY attempts:5 score:5
3. BROWN attempts:4 score:4
4. STUNG attempts:9 score:9
5. PRIDE attempts:6 score:6
6. RASPY attempts:2 score:2
7. WEIGH attempts:7 score:7
8. POUND attempts:10 score:10

# [squareword.org](squareword.org) 🧩 #1484 🥳 8 ⏱️ 0:02:21.520586

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟨 🟨 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B R A T S
    R E L I C
    A N I M E
    C A B I N
    E L I D E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1421 🥳 164 ⏱️ 0:01:40.897967

🤔 165 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 26 chat prompts
🤖 26 dolphin3:latest replies
🥵   6 😎  15 🥶 134 🧊   9

      $1 #165 shopping        100.00°C 🥳 1000‰ ~156 used:0  [155]  source:dolphin3
      $2 #145 boutique         39.53°C 🥵  979‰   ~1 used:0  [0]    source:dolphin3
      $3 #126 trendy           35.47°C 🥵  954‰  ~20 used:15 [19]   source:dolphin3
      $4 #127 upscale          35.42°C 🥵  953‰  ~18 used:11 [17]   source:dolphin3
      $5  #57 decor            32.71°C 🥵  926‰  ~19 used:13 [18]   source:dolphin3
      $6 #103 fashionable      31.93°C 🥵  915‰   ~3 used:10 [2]    source:dolphin3
      $7  #94 luxury           31.75°C 🥵  912‰   ~2 used:8  [1]    source:dolphin3
      $8  #91 fashion          30.49°C 😎  888‰   ~4 used:1  [3]    source:dolphin3
      $9 #159 lifestyle        29.73°C 😎  872‰   ~5 used:0  [4]    source:dolphin3
     $10  #34 cafe             29.06°C 😎  858‰  ~21 used:3  [20]   source:dolphin3
     $11 #101 chic             28.61°C 😎  845‰   ~6 used:0  [5]    source:dolphin3
     $12 #129 luxe             28.24°C 😎  835‰   ~7 used:0  [6]    source:dolphin3
     $23 #136 designer         19.37°C 🥶        ~26 used:0  [25]   source:dolphin3
    $157  #42 machine          -0.09°C 🧊       ~157 used:0  [156]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1454 🥳 44 ⏱️ 0:00:56.255308

🤔 45 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 11 chat prompts
🤖 11 dolphin3:latest replies
😱  1 🥵  1 😎  4 🥶 34 🧊  4

     $1 #45 poète          100.00°C 🥳 1000‰ ~41 used:0 [40]  source:dolphin3
     $2 #42 poésie          73.52°C 😱  999‰  ~1 used:1 [0]   source:dolphin3
     $3 #39 lyrique         45.26°C 🥵  952‰  ~2 used:0 [1]   source:dolphin3
     $4 #34 chanson         39.45°C 😎  855‰  ~3 used:0 [2]   source:dolphin3
     $5 #43 rhapsodie       38.05°C 😎  810‰  ~4 used:0 [3]   source:dolphin3
     $6 #32 dithyrambe      37.80°C 😎  799‰  ~5 used:1 [4]   source:dolphin3
     $7 #40 musicien        36.68°C 😎  750‰  ~6 used:0 [5]   source:dolphin3
     $8 #41 mélodie         28.41°C 🥶       ~13 used:0 [12]  source:dolphin3
     $9 #44 récitatif       28.35°C 🥶       ~14 used:0 [13]  source:dolphin3
    $10 #15 bandonéon       26.76°C 🥶        ~8 used:5 [7]   source:dolphin3
    $11 #18 harpe           23.69°C 🥶       ~12 used:2 [11]  source:dolphin3
    $12 #11 flûte           21.31°C 🥶       ~10 used:4 [9]   source:dolphin3
    $13 #29 harmonie        21.26°C 🥶       ~15 used:0 [14]  source:dolphin3
    $42  #3 quasar          -0.09°C 🧊       ~42 used:0 [41]  source:dolphin3
