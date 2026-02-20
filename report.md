# 2026-02-21

- 🔗 spaceword.org 🧩 2026-02-20 🏁 score 2170 ranked 26.1% 87/333 ⏱️ 4:36:55.801557
- 🔗 alfagok.diginaut.net 🧩 #476 🥳 58 ⏱️ 0:01:12.339539
- 🔗 alphaguess.com 🧩 #943 🥳 36 ⏱️ 0:00:36.485886
- 🔗 dontwordle.com 🧩 #1369 🥳 6 ⏱️ 0:01:11.805667
- 🔗 dictionary.com hurdle 🧩 #1512 😦 21 ⏱️ 0:03:46.426419
- 🔗 Quordle Classic 🧩 #1489 🥳 score:21 ⏱️ 0:01:34.886318
- 🔗 Octordle Classic 🧩 #1489 🥳 score:68 ⏱️ 0:04:42.375327
- 🔗 squareword.org 🧩 #1482 🥳 7 ⏱️ 0:01:38.030490
- 🔗 cemantle.certitudes.org 🧩 #1419 🥳 72 ⏱️ 0:01:09.269976
- 🔗 cemantix.certitudes.org 🧩 #1452 🥳 214 ⏱️ 0:04:35.239986

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



# [spaceword.org](spaceword.org) 🧩 2026-02-20 🏁 score 2170 ranked 26.1% 87/333 ⏱️ 4:36:55.801557

📜 2 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 87/333

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ D E A S H _ _   
      _ _ _ _ _ B _ I _ _   
      _ _ _ J _ U _ V _ _   
      _ _ _ A _ L Y E _ _   
      _ _ _ U N I _ _ _ _   
      _ _ _ K O A N _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #476 🥳 58 ⏱️ 0:01:12.339539

🤔 58 attempts
📜 1 sessions

    @        [     0] &-teken  
    @+199816 [199816] lijm     q0  ? ␅
    @+199816 [199816] lijm     q1  ? after
    @+211784 [211784] medaille q8  ? ␅
    @+211784 [211784] medaille q9  ? after
    @+214752 [214752] memo     q12 ? ␅
    @+214752 [214752] memo     q13 ? after
    @+216241 [216241] meter    q14 ? ␅
    @+216241 [216241] meter    q15 ? after
    @+216618 [216618] meur     q18 ? ␅
    @+216618 [216618] meur     q19 ? after
    @+216631 [216631] meute    q46 ? ␅
    @+216631 [216631] meute    q47 ? after
    @+216642 [216642] mevrouw  q48 ? ␅
    @+216642 [216642] mevrouw  q49 ? after
    @+216645 [216645] mevrouwt q50 ? ␅
    @+216645 [216645] mevrouwt q51 ? after
    @+216648 [216648] mezelf   q56 ? ␅
    @+216648 [216648] mezelf   q57 ? it
    @+216648 [216648] mezelf   done. it
    @+216649 [216649] mezen    q44 ? ␅
    @+216649 [216649] mezen    q45 ? before
    @+216669 [216669] mi       q22 ? ␅
    @+216669 [216669] mi       q23 ? before
    @+216731 [216731] micro    q20 ? ␅
    @+216731 [216731] micro    q21 ? before
    @+216984 [216984] middel   q16 ? ␅
    @+216984 [216984] middel   q17 ? before
    @+217758 [217758] mijns    q10 ? ␅
    @+217758 [217758] mijns    q11 ? before
    @+223750 [223750] molest   q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #943 🥳 36 ⏱️ 0:00:36.485886

🤔 36 attempts
📜 1 sessions

    @       [    0] aa        
    @+1398  [ 1398] acrogen   q12 ? ␅
    @+1398  [ 1398] acrogen   q13 ? after
    @+2097  [ 2097] ads       q14 ? ␅
    @+2097  [ 2097] ads       q15 ? after
    @+2391  [ 2391] aero      q16 ? ␅
    @+2391  [ 2391] aero      q17 ? after
    @+2544  [ 2544] aff       q18 ? ␅
    @+2544  [ 2544] aff       q19 ? after
    @+2666  [ 2666] afford    q20 ? ␅
    @+2666  [ 2666] afford    q21 ? after
    @+2698  [ 2698] affright  q24 ? ␅
    @+2698  [ 2698] affright  q25 ? after
    @+2716  [ 2716] afield    q26 ? ␅
    @+2716  [ 2716] afield    q27 ? after
    @+2724  [ 2724] afore     q28 ? ␅
    @+2724  [ 2724] afore     q29 ? after
    @+2729  [ 2729] aforetime q30 ? ␅
    @+2729  [ 2729] aforetime q31 ? after
    @+2731  [ 2731] afraid    q34 ? ␅
    @+2731  [ 2731] afraid    q35 ? it
    @+2731  [ 2731] afraid    done. it
    @+2732  [ 2732] afreet    q32 ? ␅
    @+2732  [ 2732] afreet    q33 ? before
    @+2734  [ 2734] afresh    q22 ? ␅
    @+2734  [ 2734] afresh    q23 ? before
    @+2802  [ 2802] ag        q10 ? ␅
    @+2802  [ 2802] ag        q11 ? before
    @+5876  [ 5876] angel     q8  ? ␅
    @+5876  [ 5876] angel     q9  ? before
    @+11764 [11764] back      q7  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1369 🥳 6 ⏱️ 0:01:11.805667

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:SEXES n n n n n remain:3586
    ⬜⬜⬜⬜⬜ tried:BROOK n n n n n remain:1087
    ⬜⬜⬜⬜⬜ tried:YUMMY n n n n n remain:398
    ⬜⬜⬜⬜🟩 tried:PHPHT n n n n Y remain:32
    ⬜🟨⬜⬜🟩 tried:ZIZIT n m n n Y remain:14
    ⬜⬜🟩🟨🟩 tried:CLIFT n n Y m Y remain:1

    Undos used: 2

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1512 😦 21 ⏱️ 0:03:46.426419

📜 1 sessions
💰 score: 4580

    3/6
    LARES 🟨⬜⬜⬜⬜
    WILCO ⬜🟨🟨🟩⬜
    FLICK 🟩🟩🟩🟩🟩
    5/6
    FLICK ⬜⬜🟩⬜⬜
    TRINE ⬜🟩🟩⬜🟩
    PRIDE ⬜🟩🟩⬜🟩
    GRIME ⬜🟩🟩⬜🟩
    ARISE 🟩🟩🟩🟩🟩
    5/6
    ARISE ⬜⬜⬜⬜⬜
    TOUCH ⬜⬜🟨⬜⬜
    LUMPY ⬜🟩⬜🟨🟩
    PUNKY 🟩🟩⬜⬜🟩
    PUDGY 🟩🟩🟩🟩🟩
    6/6
    PUDGY 🟩⬜⬜⬜⬜
    PHASE 🟩⬜🟨⬜🟨
    PANEL 🟩🟩⬜🟩⬜
    PACER 🟩🟩⬜🟩🟩
    PAVER 🟩🟩⬜🟩🟩
    PAPER 🟩🟩🟩🟩🟩
    Final 2/2
    ????? 🟩🟩⬜🟩🟩
    ????? 🟩🟩⬜🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1489 🥳 score:21 ⏱️ 0:01:34.886318

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. DRUNK attempts:5 score:5
2. WITTY attempts:7 score:7
3. FROWN attempts:6 score:6
4. REACH attempts:3 score:3

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1489 🥳 score:68 ⏱️ 0:04:42.375327

📜 2 sessions

Octordle Classic

1. STRUT attempts:7 score:7
2. WEARY attempts:10 score:10
3. STORE attempts:8 score:8
4. REIGN attempts:11 score:11
5. CAROL attempts:3 score:3
6. RIVER attempts:12 score:12
7. REVEL attempts:12 score:13
8. SANER attempts:4 score:4

# [squareword.org](squareword.org) 🧩 #1482 🥳 7 ⏱️ 0:01:38.030490

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P A C T S
    A L L E Y
    S T E R N
    T O R S O
    A S K E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1419 🥳 72 ⏱️ 0:01:09.269976

🤔 73 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 19 chat prompts
🤖 19 dolphin3:latest replies
😎  4 🥶 59 🧊  9

     $1 #73 hip              100.00°C 🥳 1000‰ ~64 used:0 [63]  source:dolphin3
     $2 #70 trendy            40.22°C 😎  889‰  ~1 used:0 [0]   source:dolphin3
     $3 #67 chic              36.55°C 😎  842‰  ~2 used:0 [1]   source:dolphin3
     $4 #69 fashion           25.92°C 😎  278‰  ~3 used:0 [2]   source:dolphin3
     $5 #71 contemporary      25.68°C 😎  237‰  ~4 used:0 [3]   source:dolphin3
     $6 #72 cool              22.47°C 🥶       ~14 used:0 [13]  source:dolphin3
     $7 #68 elegant           22.46°C 🥶       ~15 used:0 [14]  source:dolphin3
     $8 #66 style             20.89°C 🥶       ~16 used:0 [15]  source:dolphin3
     $9 #56 elegance          17.75°C 🥶       ~17 used:1 [16]  source:dolphin3
    $10 #61 graceful          17.55°C 🥶       ~18 used:0 [17]  source:dolphin3
    $11 #62 gracefulness      16.71°C 🥶       ~19 used:0 [18]  source:dolphin3
    $12 #28 alignment         15.88°C 🥶        ~5 used:9 [4]   source:dolphin3
    $13 #65 sophistication    15.81°C 🥶       ~20 used:0 [19]  source:dolphin3
    $65 #57 orderliness       -0.13°C 🧊       ~65 used:0 [64]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1452 🥳 214 ⏱️ 0:04:35.239986

🤔 215 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 52 chat prompts
🤖 52 dolphin3:latest replies
🔥   2 🥵  12 😎  33 🥶 125 🧊  42

      $1 #215 colline         100.00°C 🥳 1000‰ ~173 used:0  [172]  source:dolphin3
      $2 #204 escarpement      56.49°C 🔥  994‰   ~1 used:7  [0]    source:dolphin3
      $3 #153 flanc            55.81°C 🔥  992‰   ~8 used:25 [7]    source:dolphin3
      $4 #197 rocher           51.44°C 🥵  978‰   ~9 used:6  [8]    source:dolphin3
      $5 #192 falaise          48.77°C 🥵  974‰   ~5 used:2  [4]    source:dolphin3
      $6 #188 montagne         48.28°C 🥵  972‰   ~6 used:2  [5]    source:dolphin3
      $7 #211 ravin            46.46°C 🥵  965‰   ~2 used:0  [1]    source:dolphin3
      $8 #191 crête            45.13°C 🥵  958‰   ~7 used:2  [6]    source:dolphin3
      $9  #93 contrefort       43.78°C 🥵  949‰  ~40 used:15 [39]   source:dolphin3
     $10 #195 pente            43.43°C 🥵  946‰   ~3 used:0  [2]    source:dolphin3
     $11  #55 ruine            42.16°C 🥵  924‰  ~44 used:25 [43]   source:dolphin3
     $16  #52 masure           40.08°C 😎  888‰  ~45 used:3  [44]   source:dolphin3
     $49  #68 chaumière        28.08°C 🥶        ~54 used:0  [53]   source:dolphin3
    $174  #53 militaire        -0.02°C 🧊       ~174 used:0  [173]  source:dolphin3
