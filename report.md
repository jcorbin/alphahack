# 2026-09-14

- 🔗 spaceword.org 🧩 2026-09-13 🏁 score 2164 ranked 49.1% 164/334 ⏱️ 0:23:35.609255
- 🔗 wordgrid 🧩 #835 🟪 rarity:0.34 ⏱️ 0:01:44.712358
- 🔗 cemantle.certitudes.org 🧩 #1624 🥳 196 ⏱️ 0:02:27.242520
- 🔗 alfagok.diginaut.net 🧩 #681 🥳 36 ⏱️ 0:00:43.668046
- 🔗 alphaguess.com 🧩 #1148 🥳 26 ⏱️ 0:00:29.078180
- 🔗 dontwordle.com 🧩 #1574 🥳 6 ⏱️ 0:01:54.195716
- 🔗 dictionary.com hurdle 🧩 #1717 😦 17 ⏱️ 0:04:11.803698
- 🔗 cemantix.certitudes.org 🧩 #1657 🥳 32 ⏱️ 0:00:43.623419
- 🔗 Quordle Classic 🧩 #1694 🥳 score:18 ⏱️ 0:01:09.330339
- 🔗 Octordle Classic 🧩 #1694 😦 score:69 ⏱️ 0:01:52.525437
- 🔗 Sedecordle Classic 🧩 #1674 🥳 score:36 ⏱️ 0:03:39.468224
- 🔗 squareword.org 🧩 #1687 🥳 7 ⏱️ 0:02:05.619173

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


# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 2026-09-11 🤔 rarity:nan ⏱️ 0:00:33.329642

📜 2 sessions
❓ ❓ ❓
❓ ❓ ❓
❓ ❓ ❓





# [spaceword.org](spaceword.org) 🧩 2026-09-13 🏁 score 2164 ranked 49.1% 164/334 ⏱️ 0:23:35.609255

📜 4 sessions
- tiles: 21/21
- score: 2164 bonus: +64
- rank: 164/334

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ F _ J _ _ _ M   
      _ _ _ I _ A X _ _ I   
      _ _ _ C I N E O L E   
      _ Q U O T E D _ _ N   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #835 🟪 rarity:0.34 ⏱️ 0:01:44.712358

📜 2 sessions
🌌 🦄 🦄
🌌 🦄 🌌
🌌 🌌 🌌
Rarity: 0.34 🟪


# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1624 🥳 196 ⏱️ 0:02:27.242520

🤔 197 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 26 chat prompts
🤖 26 qwen3.8:latest replies
🔥   1 🥵   5 😎  25 🥶 137 🧊  28

      $1 #197 execution            100.00°C 🥳 1000‰ ~169 used:0  [168]  source:qwen3.8
      $2 #159 implementation        40.72°C 🔥  995‰   ~1 used:4  [0]    source:qwen3.8
      $3 #195 deployment            30.64°C 🥵  979‰   ~2 used:0  [1]    source:qwen3.8
      $4 #137 conversion            26.44°C 🥵  949‰   ~5 used:8  [4]    source:qwen3.8
      $5 #194 delivery              26.13°C 🥵  943‰   ~3 used:0  [2]    source:qwen3.8
      $6 #171 consummation          25.16°C 🥵  919‰   ~4 used:2  [3]    source:qwen3.8
      $7  #82 acceleration          24.91°C 🥵  912‰  ~28 used:19 [27]   source:qwen3.8
      $8 #146 development           23.87°C 😎  868‰   ~6 used:1  [5]    source:qwen3.8
      $9 #196 enactment             23.70°C 😎  855‰   ~7 used:0  [6]    source:qwen3.8
     $10 #162 integration           22.61°C 😎  796‰   ~8 used:0  [7]    source:qwen3.8
     $11 #190 synchronization       22.34°C 😎  782‰   ~9 used:0  [8]    source:qwen3.8
     $12 #176 closing               21.36°C 😎  716‰  ~10 used:0  [9]    source:qwen3.8
     $33 #140 migration             16.76°C 🥶        ~42 used:0  [41]   source:qwen3.8
    $170 #111 weightlessness        -0.19°C 🧊       ~170 used:0  [169]  source:qwen3.8

# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #681 🥳 36 ⏱️ 0:00:43.668046

🤔 36 attempts
📜 1 sessions

    @       [    0] &-teken      
    @+24880 [24880] bad          q6  ? ␅
    @+24880 [24880] bad          q7  ? after
    @+37341 [37341] beschermen   q8  ? ␅
    @+37341 [37341] beschermen   q9  ? after
    @+40181 [40181] beurst       q12 ? ␅
    @+40181 [40181] beurst       q13 ? after
    @+40507 [40507] bever        q18 ? ␅
    @+40507 [40507] bever        q19 ? after
    @+40687 [40687] bevoegd      q20 ? ␅
    @+40687 [40687] bevoegd      q21 ? after
    @+40728 [40728] bevolking    q22 ? ␅
    @+40728 [40728] bevolking    q23 ? after
    @+40803 [40803] bevolkt      q24 ? ␅
    @+40803 [40803] bevolkt      q25 ? after
    @+40836 [40836] bevoorrading q26 ? ␅
    @+40836 [40836] bevoorrading q27 ? after
    @+40858 [40858] bevorder     q28 ? ␅
    @+40858 [40858] bevorder     q29 ? after
    @+40862 [40862] bevorderd    q32 ? ␅
    @+40862 [40862] bevorderd    q33 ? after
    @+40865 [40865] bevorderen   q34 ? ␅
    @+40865 [40865] bevorderen   q35 ? it
    @+40865 [40865] bevorderen   done. it
    @+40868 [40868] bevordering  q30 ? ␅
    @+40868 [40868] bevordering  q31 ? before
    @+40883 [40883] bevracht     q16 ? ␅
    @+40883 [40883] bevracht     q17 ? before
    @+41597 [41597] bewonder     q14 ? ␅
    @+41597 [41597] bewonder     q15 ? before
    @+43030 [43030] bij          q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1148 🥳 26 ⏱️ 0:00:29.078180

🤔 26 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+47374 [47374] dis        q4  ? ␅
    @+47374 [47374] dis        q5  ? after
    @+60013 [60013] eyewitness q8  ? ␅
    @+60013 [60013] eyewitness q9  ? after
    @+63147 [63147] fix        q12 ? ␅
    @+63147 [63147] fix        q13 ? after
    @+63925 [63925] flirt      q16 ? ␅
    @+63925 [63925] flirt      q17 ? after
    @+64016 [64016] flog       q22 ? ␅
    @+64016 [64016] flog       q23 ? after
    @+64055 [64055] floor      q24 ? ␅
    @+64055 [64055] floor      q25 ? it
    @+64055 [64055] floor      done. it
    @+64114 [64114] floriated  q20 ? ␅
    @+64114 [64114] floriated  q21 ? before
    @+64303 [64303] fluid      q18 ? ␅
    @+64303 [64303] fluid      q19 ? before
    @+64721 [64721] fold       q14 ? ␅
    @+64721 [64721] fold       q15 ? before
    @+66305 [66305] free       q10 ? ␅
    @+66305 [66305] free       q11 ? before
    @+72658 [72658] green      q6  ? ␅
    @+72658 [72658] green      q7  ? before
    @+98143 [98143] mac        q0  ? ␅
    @+98143 [98143] mac        q1  ? after
    @+98143 [98143] mac        q2  ? ␅
    @+98143 [98143] mac        q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1574 🥳 6 ⏱️ 0:01:54.195716

📜 1 sessions
💰 score: 64

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:7346
    ⬜⬜⬜⬜⬜ tried:KOOKS n n n n n remain:1934
    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:775
    ⬜⬜⬜⬜🟩 tried:PYGMY n n n n Y remain:68
    ⬜🟩⬜⬜🟩 tried:CANNY n Y n n Y remain:9
    ⬜🟩⬜⬜🟩 tried:JAZZY n Y n n Y remain:8

    Undos used: 4

      8 words remaining
    x 8 unused letters
    = 64 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1717 😦 17 ⏱️ 0:04:11.803698

📜 2 sessions
💰 score: 4960

    5/6
    ASPER 🟨🟨⬜⬜🟨
    BRATS ⬜🟨🟨🟨🟨
    STRIA 🟩🟩🟩⬜🟨
    STRAW 🟩🟩🟩🟩⬜
    STRAY 🟩🟩🟩🟩🟩
    3/6
    STRAY ⬜⬜🟨⬜🟨
    CYDER ⬜🟨⬜🟨🟨
    RHYME 🟩🟩🟩🟩🟩
    3/6
    RHYME ⬜⬜⬜⬜⬜
    ALIST 🟩⬜🟩⬜⬜
    AXING 🟩🟩🟩🟩🟩
    4/6
    AXING ⬜⬜🟨⬜⬜
    SIDLE ⬜🟨⬜⬜🟩
    OURIE ⬜⬜🟩🟩🟩
    EERIE 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜⬜⬜⬜⬜
    ????? ⬜🟩🟩⬜🟩

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1657 🥳 32 ⏱️ 0:00:43.623419

🤔 33 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 5 chat prompts
🤖 5 qwen3.8:latest replies
😱  1 🔥  1 🥵  6 😎  9 🥶 15

     $1 #33 rocher       100.00°C 🥳 1000‰ ~33 used:0 [32]  source:qwen3.8
     $2 #22 falaise       64.35°C 😱  999‰  ~1 used:2 [0]   source:qwen3.8
     $3 #31 promontoire   57.49°C 🔥  996‰  ~2 used:0 [1]   source:qwen3.8
     $4 #29 grotte        49.48°C 🥵  984‰  ~3 used:0 [2]   source:qwen3.8
     $5 #27 escarpement   49.17°C 🥵  980‰  ~4 used:0 [3]   source:qwen3.8
     $6 #17 crête         46.49°C 🥵  966‰  ~7 used:4 [6]   source:qwen3.8
     $7 #32 précipice     45.88°C 🥵  959‰  ~5 used:0 [4]   source:qwen3.8
     $8 #25 corniche      42.92°C 🥵  930‰  ~6 used:0 [5]   source:qwen3.8
     $9  #6 montagne      42.25°C 🥵  920‰  ~8 used:4 [7]   source:qwen3.8
    $10 #30 paroi         36.51°C 😎  753‰  ~9 used:0 [8]   source:qwen3.8
    $11 #18 arête         35.58°C 😎  702‰ ~10 used:0 [9]   source:qwen3.8
    $12 #24 caverne       34.80°C 😎  665‰ ~11 used:0 [10]  source:qwen3.8
    $13  #9 soleil        33.18°C 😎  515‰ ~12 used:0 [11]  source:qwen3.8
    $19 #20 bivouac       25.50°C 🥶       ~18 used:0 [17]  source:qwen3.8

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1694 🥳 score:18 ⏱️ 0:01:09.330339

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. ZEBRA attempts:6 score:6
2. LEGAL attempts:5 score:5
3. RATIO attempts:3 score:3
4. TROLL attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1694 😦 score:69 ⏱️ 0:01:52.525437

📜 1 sessions

Octordle Classic

1. WRUNG attempts:9 score:9
2. ARRAY attempts:6 score:6
3. WATER attempts:13 score:-1
4. LOUSE attempts:13 score:13
5. STERN attempts:4 score:4
6. ARGUE attempts:5 score:5
7. BREAK attempts:11 score:11
8. IRONY attempts:7 score:7

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1674 🥳 score:36 ⏱️ 0:03:39.468224

📜 1 sessions

Sedecordle Classic sedecordle.com

1. THINK attempts:9 score:0
2. PURER attempts:20 score:9
3. SHIED attempts:10 score:1
4. BLADE attempts:16 score:0
5. FEIGN attempts:11 score:1
6. SHAVE attempts:14 score:1
7. ANGST attempts:3 score:0
8. BENCH attempts:17 score:3
9. HOARD attempts:12 score:1
10. WINCE attempts:15 score:2
11. TOTEM attempts:13 score:1
12. EXCEL attempts:7 score:3
13. SLEEK attempts:18 score:1
14. GOOEY attempts:4 score:8
15. SCONE attempts:5 score:0
16. NICER attempts:6 score:5

# [squareword.org](squareword.org) 🧩 #1687 🥳 7 ⏱️ 0:02:05.619173

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟩 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C R A P
    E R O D E
    B E A D S
    U P S E T
    M E T R O
