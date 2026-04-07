# 2026-04-08

- 🔗 spaceword.org 🧩 2026-04-07 🏁 score 2173 ranked 6.4% 22/346 ⏱️ 1:21:33.165541
- 🔗 alfagok.diginaut.net 🧩 #522 🥳 20 ⏱️ 0:00:33.799657
- 🔗 alphaguess.com 🧩 #989 🥳 24 ⏱️ 0:01:07.006832
- 🔗 dontwordle.com 🧩 #1415 🥳 6 ⏱️ 0:02:25.678380
- 🔗 dictionary.com hurdle 🧩 #1558 🥳 18 ⏱️ 0:03:59.558530
- 🔗 Quordle Classic 🧩 #1535 🥳 score:22 ⏱️ 0:02:22.638995
- 🔗 Octordle Classic 🧩 #1535 🥳 score:67 ⏱️ 0:04:55.821014
- 🔗 squareword.org 🧩 #1528 🥳 6 ⏱️ 0:01:42.295650
- 🔗 cemantle.certitudes.org 🧩 #1465 🥳 23 ⏱️ 0:00:14.340912
- 🔗 cemantix.certitudes.org 🧩 #1498 🥳 199 ⏱️ 0:02:58.667783

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






































# [spaceword.org](spaceword.org) 🧩 2026-04-07 🏁 score 2173 ranked 6.4% 22/346 ⏱️ 1:21:33.165541

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 22/346

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ V E G _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ _ O _ R _ _ _   
      _ _ _ _ P A H _ _ _   
      _ _ _ _ A X E _ _ _   
      _ _ _ _ Q _ N _ _ _   
      _ _ _ _ U _ S _ _ _   
      _ _ _ _ E L _ _ _ _   
      _ _ _ _ R O E _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #522 🥳 20 ⏱️ 0:00:33.799657

🤔 20 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+1      [     1] &-tekens    
    @+2      [     2] -cijferig   
    @+3      [     3] -e-mail     
    @+199606 [199606] lij         q0  ? ␅
    @+199606 [199606] lij         q1  ? after
    @+247688 [247688] op          q4  ? ␅
    @+247688 [247688] op          q5  ? after
    @+273492 [273492] proef       q6  ? ␅
    @+273492 [273492] proef       q7  ? after
    @+276621 [276621] quarantaine q12 ? ␅
    @+276621 [276621] quarantaine q13 ? after
    @+276846 [276846] raad        q18 ? ␅
    @+276846 [276846] raad        q19 ? it
    @+276846 [276846] raad        done. it
    @+277304 [277304] rad         q16 ? ␅
    @+277304 [277304] rad         q17 ? before
    @+278102 [278102] ram         q14 ? ␅
    @+278102 [278102] ram         q15 ? before
    @+279758 [279758] rechts      q10 ? ␅
    @+279758 [279758] rechts      q11 ? before
    @+286476 [286476] rijns       q8  ? ␅
    @+286476 [286476] rijns       q9  ? before
    @+299474 [299474] schro       q2  ? ␅
    @+299474 [299474] schro       q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #989 🥳 24 ⏱️ 0:01:07.006832

🤔 24 attempts
📜 2 sessions

    @        [     0] aa     
    @+1      [     1] aah    
    @+2      [     2] aahed  
    @+3      [     3] aahing 
    @+98216  [ 98216] mach   q0  ? ␅
    @+98216  [ 98216] mach   q1  ? after
    @+147371 [147371] rhumb  q2  ? ␅
    @+147371 [147371] rhumb  q3  ? after
    @+171636 [171636] ta     q4  ? ␅
    @+171636 [171636] ta     q5  ? after
    @+182000 [182000] un     q6  ? ␅
    @+182000 [182000] un     q7  ? after
    @+189262 [189262] vicar  q8  ? ␅
    @+189262 [189262] vicar  q9  ? after
    @+191042 [191042] walk   q12 ? ␅
    @+191042 [191042] walk   q13 ? after
    @+191069 [191069] wall   q22 ? ␅
    @+191069 [191069] wall   q23 ? it
    @+191069 [191069] wall   done. it
    @+191140 [191140] wame   q20 ? ␅
    @+191140 [191140] wame   q21 ? before
    @+191246 [191246] war    q18 ? ␅
    @+191246 [191246] war    q19 ? before
    @+191453 [191453] wash   q16 ? ␅
    @+191453 [191453] wash   q17 ? before
    @+191905 [191905] we     q14 ? ␅
    @+191905 [191905] we     q15 ? before
    @+192866 [192866] whir   q10 ? ␅
    @+192866 [192866] whir   q11 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1415 🥳 6 ⏱️ 0:02:25.678380

📜 1 sessions
💰 score: 32

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:8089
    ⬜⬜⬜⬜⬜ tried:DEKED n n n n n remain:3108
    ⬜⬜⬜⬜⬜ tried:MAMMA n n n n n remain:1190
    ⬜⬜⬜⬜⬜ tried:BOZOS n n n n n remain:124
    ⬜⬜⬜🟩🟩 tried:PHPHT n n n Y Y remain:7
    ⬜🟩🟩🟩🟩 tried:FIGHT n Y Y Y Y remain:4

    Undos used: 4

      4 words remaining
    x 8 unused letters
    = 32 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1558 🥳 18 ⏱️ 0:03:59.558530

📜 1 sessions
💰 score: 9800

    5/6
    REAIS ⬜🟨⬜🟨🟨
    SLIDE 🟨⬜🟩⬜🟩
    GUISE ⬜⬜🟩🟩🟩
    NOISE ⬜🟩🟩🟩🟩
    POISE 🟩🟩🟩🟩🟩
    4/6
    POISE ⬜⬜⬜⬜🟨
    ALDER ⬜⬜⬜🟨⬜
    TENCH ⬜🟩🟩🟩🟩
    BENCH 🟩🟩🟩🟩🟩
    5/6
    BENCH ⬜🟨🟨⬜⬜
    ANISE ⬜🟩⬜🟨🟩
    SNORE 🟨🟩⬜⬜🟩
    ENSUE 🟨🟩🟩🟨🟩
    UNSEE 🟩🟩🟩🟩🟩
    3/6
    UNSEE ⬜⬜🟨🟩⬜
    TARES 🟨⬜⬜🟩🟨
    ISLET 🟩🟩🟩🟩🟩
    Final 1/2
    TABBY 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1535 🥳 score:22 ⏱️ 0:02:22.638995

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. IDEAL attempts:3 score:3
2. PULPY attempts:8 score:8
3. HUMPH attempts:5 score:5
4. RETCH attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1535 🥳 score:67 ⏱️ 0:04:55.821014

📜 2 sessions

Octordle Classic

1. AWAKE attempts:8 score:8
2. COUGH attempts:9 score:9
3. TOAST attempts:10 score:10
4. STYLE attempts:6 score:6
5. PAGAN attempts:7 score:7
6. BOOZY attempts:12 score:12
7. EXULT attempts:4 score:4
8. FAVOR attempts:11 score:11

# [squareword.org](squareword.org) 🧩 #1528 🥳 6 ⏱️ 0:01:42.295650

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    M A R S H
    I R A T E
    M O V I E
    E M E N D
    D A R T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1465 🥳 23 ⏱️ 0:00:14.340912

🤔 24 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 6 chat prompts
🤖 6 dolphin3:latest replies
🥵  1 😎  2 🥶 18 🧊  2

     $1 #24 echo           100.00°C 🥳 1000‰ ~22 used:0 [21]  source:dolphin3
     $2 #17 sound           41.62°C 🥵  964‰  ~1 used:2 [0]   source:dolphin3
     $3 #18 acoustics       28.16°C 😎  206‰  ~2 used:0 [1]   source:dolphin3
     $4 #20 noise           28.11°C 😎  197‰  ~3 used:0 [2]   source:dolphin3
     $5 #22 amplification   26.89°C 🥶        ~4 used:0 [3]   source:dolphin3
     $6 #19 frequency       23.04°C 🥶        ~5 used:0 [4]   source:dolphin3
     $7 #14 audio           23.01°C 🥶        ~6 used:0 [5]   source:dolphin3
     $8 #11 amplifier       17.58°C 🥶        ~7 used:0 [6]   source:dolphin3
     $9 #23 bass            17.50°C 🥶        ~8 used:0 [7]   source:dolphin3
    $10  #6 guitar          17.48°C 🥶        ~9 used:1 [8]   source:dolphin3
    $11 #12 instrument      16.70°C 🥶       ~10 used:0 [9]   source:dolphin3
    $12 #13 music           15.19°C 🥶       ~11 used:0 [10]  source:dolphin3
    $13 #16 recording       12.65°C 🥶       ~12 used:0 [11]  source:dolphin3
    $23  #3 carrot          -1.59°C 🧊       ~23 used:0 [22]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1498 🥳 199 ⏱️ 0:02:58.667783

🤔 200 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 28 chat prompts
🤖 28 dolphin3:latest replies
🔥   1 😎   4 🥶 104 🧊  90

      $1 #200 acier           100.00°C 🥳 1000‰ ~110 used:0  [109]  source:dolphin3
      $2 #199 alliage          46.81°C 🔥  992‰   ~1 used:2  [0]    source:dolphin3
      $3 #194 métallurgie      33.61°C 😎  750‰   ~4 used:5  [3]    source:dolphin3
      $4 #198 forge            33.20°C 😎  732‰   ~2 used:4  [1]    source:dolphin3
      $5 #160 fabrication      30.59°C 😎  577‰   ~5 used:10 [4]    source:dolphin3
      $6 #181 usinage          30.08°C 😎  539‰   ~3 used:4  [2]    source:dolphin3
      $7 #155 usine            25.78°C 🥶         ~7 used:7  [6]    source:dolphin3
      $8 #129 industriel       24.90°C 🥶         ~8 used:7  [7]    source:dolphin3
      $9 #146 manufacturier    23.84°C 🥶        ~10 used:5  [9]    source:dolphin3
     $10 #193 moulage          23.72°C 🥶        ~20 used:0  [19]   source:dolphin3
     $11 #190 construction     22.51°C 🥶        ~21 used:0  [20]   source:dolphin3
     $12  #99 armé             21.47°C 🥶        ~15 used:2  [14]   source:dolphin3
     $13 #145 industrie        20.82°C 🥶        ~22 used:0  [21]   source:dolphin3
    $111  #34 malfaiteur       -0.02°C 🧊       ~111 used:0  [110]  source:dolphin3
