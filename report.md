# 2026-03-21

- 🔗 spaceword.org 🧩 2026-03-20 🏁 score 2170 ranked 34.7% 115/331 ⏱️ 23:37:26.864044
- 🔗 alfagok.diginaut.net 🧩 #504 🥳 32 ⏱️ 0:00:31.975547
- 🔗 alphaguess.com 🧩 #971 🥳 26 ⏱️ 0:00:27.887275
- 🔗 dontwordle.com 🧩 #1397 🥳 6 ⏱️ 0:01:42.344363
- 🔗 dictionary.com hurdle 🧩 #1540 😦 11 ⏱️ 0:01:46.560188
- 🔗 Quordle Classic 🧩 #1517 🥳 score:22 ⏱️ 0:01:28.672356
- 🔗 Octordle Classic 🧩 #1517 🥳 score:58 ⏱️ 0:03:30.776842
- 🔗 squareword.org 🧩 #1510 🥳 7 ⏱️ 0:01:58.423088
- 🔗 cemantle.certitudes.org 🧩 #1447 🥳 158 ⏱️ 0:02:05.209126
- 🔗 cemantix.certitudes.org 🧩 #1480 🥳 243 ⏱️ 0:07:11.503537
- 🔗 Quordle Rescue 🧩 #131 🥳 score:23 ⏱️ 0:01:08.550583

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




















# [spaceword.org](spaceword.org) 🧩 2026-03-20 🏁 score 2170 ranked 34.7% 115/331 ⏱️ 23:37:26.864044

📜 5 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 115/331

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ A _ N _ F _ _   
      _ _ _ J _ A G E _ _   
      _ _ O A K I E R _ _   
      _ _ D R I V E N _ _   
      _ _ _ _ _ E _ Y _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #504 🥳 32 ⏱️ 0:00:31.975547

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+199609 [199609] lij        q0  ? ␅
    @+199609 [199609] lij        q1  ? after
    @+199609 [199609] lij        q2  ? ␅
    @+199609 [199609] lij        q3  ? after
    @+247696 [247696] op         q6  ? ␅
    @+247696 [247696] op         q7  ? after
    @+273501 [273501] proef      q8  ? ␅
    @+273501 [273501] proef      q9  ? after
    @+279767 [279767] rechts     q12 ? ␅
    @+279767 [279767] rechts     q13 ? after
    @+283116 [283116] rel        q14 ? ␅
    @+283116 [283116] rel        q15 ? after
    @+284269 [284269] res        q16 ? ␅
    @+284269 [284269] res        q17 ? after
    @+284518 [284518] respect    q22 ? ␅
    @+284518 [284518] respect    q23 ? after
    @+284569 [284569] respons    q26 ? ␅
    @+284569 [284569] respons    q27 ? after
    @+284599 [284599] ressort    q28 ? ␅
    @+284599 [284599] ressort    q29 ? after
    @+284616 [284616] rest       q30 ? ␅
    @+284616 [284616] rest       q31 ? it
    @+284616 [284616] rest       done. it
    @+284632 [284632] restaurant q24 ? ␅
    @+284632 [284632] restaurant q25 ? before
    @+284800 [284800] resultaat  q20 ? ␅
    @+284800 [284800] resultaat  q21 ? before
    @+285369 [285369] revolver   q18 ? ␅
    @+285369 [285369] revolver   q19 ? before
    @+286485 [286485] rijns      q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #971 🥳 26 ⏱️ 0:00:27.887275

🤔 26 attempts
📜 1 sessions

    @        [     0] aa       
    @+1      [     1] aah      
    @+2      [     2] aahed    
    @+3      [     3] aahing   
    @+98217  [ 98217] mach     q0  ? ␅
    @+98217  [ 98217] mach     q1  ? after
    @+98217  [ 98217] mach     q2  ? ␅
    @+98217  [ 98217] mach     q3  ? after
    @+122778 [122778] parr     q6  ? ␅
    @+122778 [122778] parr     q7  ? after
    @+135069 [135069] proper   q8  ? ␅
    @+135069 [135069] proper   q9  ? after
    @+136428 [136428] pul      q14 ? ␅
    @+136428 [136428] pul      q15 ? after
    @+136753 [136753] punt     q18 ? ␅
    @+136753 [136753] punt     q19 ? after
    @+136812 [136812] pur      q20 ? ␅
    @+136812 [136812] pur      q21 ? after
    @+136950 [136950] purpuras q22 ? ␅
    @+136950 [136950] purpuras q23 ? after
    @+137014 [137014] push     q24 ? ␅
    @+137014 [137014] push     q25 ? it
    @+137014 [137014] push     done. it
    @+137088 [137088] put      q16 ? ␅
    @+137088 [137088] put      q17 ? before
    @+137788 [137788] quart    q12 ? ␅
    @+137788 [137788] quart    q13 ? before
    @+140517 [140517] rec      q10 ? ␅
    @+140517 [140517] rec      q11 ? before
    @+147372 [147372] rhumb    q4  ? ␅
    @+147372 [147372] rhumb    q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1397 🥳 6 ⏱️ 0:01:42.344363

📜 1 sessions
💰 score: 4

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:7870
    ⬜⬜⬜⬜⬜ tried:BOFFO n n n n n remain:3999
    ⬜⬜⬜⬜⬜ tried:GYPSY n n n n n remain:909
    ⬜⬜⬜⬜⬜ tried:CRWTH n n n n n remain:130
    ⬜🟨⬜⬜⬜ tried:KUDZU n m n n n remain:11
    🟩⬜⬜🟩🟩 tried:VENUE Y n n Y Y remain:1

    Undos used: 2

      1 words remaining
    x 4 unused letters
    = 4 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1540 😦 11 ⏱️ 0:01:46.560188

📜 1 sessions
💰 score: 1180

    5/6
    AEONS ⬜⬜⬜🟩⬜
    RUING ⬜⬜🟩🟩🟩
    LYING ⬜🟩🟩🟩🟩
    DYING ⬜🟩🟩🟩🟩
    VYING 🟩🟩🟩🟩🟩
    6/6
    ????? ⬜⬜⬜⬜🟨
    ????? ⬜⬜🟨🟨🟨
    ????? 🟨🟩🟩🟩⬜
    ????? ⬜🟩🟩🟩🟩
    ????? ⬜🟩🟩🟩🟩
    ????? ⬜🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1517 🥳 score:22 ⏱️ 0:01:28.672356

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. LEVEL attempts:6 score:6
2. MAPLE attempts:7 score:7
3. BRAID attempts:4 score:4
4. CORAL attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1517 🥳 score:58 ⏱️ 0:03:30.776842

📜 1 sessions

Octordle Classic

1. CHARD attempts:6 score:6
2. SNARL attempts:3 score:3
3. WHIRL attempts:4 score:4
4. PLUMP attempts:10 score:10
5. STEAD attempts:7 score:7
6. ARBOR attempts:8 score:8
7. DOWEL attempts:9 score:9
8. MOUND attempts:11 score:11

# [squareword.org](squareword.org) 🧩 #1510 🥳 7 ⏱️ 0:01:58.423088

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    M A R S H
    I R A T E
    L E V E E
    K N E E L
    Y A R D S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1447 🥳 158 ⏱️ 0:02:05.209126

🤔 159 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 24 chat prompts
🤖 24 dolphin3:latest replies
🔥   1 🥵   5 😎  11 🥶 134 🧊   7

      $1 #159 concrete          100.00°C 🥳 1000‰ ~152 used:0  [151]  source:dolphin3
      $2 #157 cement             55.17°C 🔥  998‰   ~1 used:0  [0]    source:dolphin3
      $3 #145 gypsum             44.33°C 🥵  976‰   ~2 used:1  [1]    source:dolphin3
      $4 #152 wall               41.11°C 🥵  962‰   ~3 used:0  [2]    source:dolphin3
      $5 #148 sealant            40.50°C 🥵  957‰   ~4 used:0  [3]    source:dolphin3
      $6 #132 drywall            39.60°C 🥵  949‰   ~5 used:4  [4]    source:dolphin3
      $7 #112 cladding           39.32°C 🥵  944‰   ~6 used:9  [5]    source:dolphin3
      $8 #154 reinforcement      35.41°C 😎  885‰   ~7 used:0  [6]    source:dolphin3
      $9 #129 insulation         34.81°C 😎  872‰  ~16 used:2  [15]   source:dolphin3
     $10 #126 facade             34.47°C 😎  858‰   ~8 used:0  [7]    source:dolphin3
     $11 #125 exterior           33.94°C 😎  837‰   ~9 used:0  [8]    source:dolphin3
     $12 #149 spackle            33.52°C 😎  824‰  ~10 used:0  [9]    source:dolphin3
     $19  #91 rod                24.40°C 🥶        ~25 used:2  [24]   source:dolphin3
    $153   #1 algorithm          -0.36°C 🧊       ~153 used:0  [152]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1480 🥳 243 ⏱️ 0:07:11.503537

🤔 244 attempts
📜 1 sessions
🫧 18 chat sessions
⁉️ 81 chat prompts
🤖 81 dolphin3:latest replies
🔥   4 🥵  12 😎  34 🥶 166 🧊  27

      $1 #244 néant               100.00°C 🥳 1000‰ ~217 used:0  [216]  source:dolphin3
      $2 #227 éternité             46.37°C 🔥  998‰   ~2 used:18 [1]    source:dolphin3
      $3 #183 infini               45.62°C 🔥  997‰  ~12 used:38 [11]   source:dolphin3
      $4 #211 abîme                45.39°C 🔥  996‰   ~1 used:17 [0]    source:dolphin3
      $5 #174 insondable           41.85°C 🔥  991‰   ~8 used:23 [7]    source:dolphin3
      $6 #194 éternel              41.29°C 🥵  988‰  ~13 used:5  [12]   source:dolphin3
      $7 #199 éternellement        38.49°C 🥵  977‰   ~9 used:3  [8]    source:dolphin3
      $8 #182 inexprimable         37.80°C 🥵  968‰  ~10 used:3  [9]    source:dolphin3
      $9 #168 ineffable            37.65°C 🥵  965‰  ~11 used:3  [10]   source:dolphin3
     $10 #186 infinitude           37.14°C 🥵  960‰   ~3 used:2  [2]    source:dolphin3
     $11 #229 immortalité          36.95°C 🥵  958‰   ~4 used:2  [3]    source:dolphin3
     $18 #181 incommensurable      33.24°C 😎  877‰  ~16 used:0  [15]   source:dolphin3
     $52 #134 imaginaire           24.06°C 🥶        ~55 used:0  [54]   source:dolphin3
    $218  #65 to                   -0.48°C 🧊       ~218 used:0  [217]  source:dolphin3

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #131 🥳 score:23 ⏱️ 0:01:08.550583

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. SCOPE attempts:5 score:5
2. BLOKE attempts:8 score:8
3. ROACH attempts:4 score:4
4. BONGO attempts:6 score:6
