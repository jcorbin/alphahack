# 2026-09-22

- 🔗 spaceword.org 🧩 2026-09-21 🏁 score 2168 ranked 41.6% 152/365 ⏱️ 0:32:47.074718
- 🔗 wordgrid 🧩 #843 🟪 rarity:0.11 ⏱️ 0:02:12.429744
- 🔗 alfagok.diginaut.net 🧩 #689 🥳 30 ⏱️ 0:00:34.732210
- 🔗 alphaguess.com 🧩 #1156 🥳 32 ⏱️ 0:00:41.711970
- 🔗 dontwordle.com 🧩 #1582 🥳 6 ⏱️ 0:01:11.934319
- 🔗 dictionary.com hurdle 🧩 #1725 🥳 16 ⏱️ 0:02:28.451572
- 🔗 Quordle Classic 🧩 #1702 😦 score:28 ⏱️ 0:03:53.608875
- 🔗 Octordle Classic 🧩 #1702 🥳 score:59 ⏱️ 0:01:42.435690
- 🔗 Sedecordle Classic 🧩 #1682 🥳 score:38 ⏱️ 0:02:08.707119
- 🔗 squareword.org 🧩 #1695 🥳 8 ⏱️ 0:02:28.627175
- 🔗 cemantle.certitudes.org 🧩 #1632 🥳 136 ⏱️ 0:03:23.156125
- 🔗 cemantix.certitudes.org 🧩 #1665 🥳 249 ⏱️ 0:07:07.397666

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


# [spaceword.org](spaceword.org) 🧩 2026-09-21 🏁 score 2168 ranked 41.6% 152/365 ⏱️ 0:32:47.074718

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 152/365

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ K _ _ R _ _ _   
      _ R _ O I _ O _ M _   
      _ E _ R O M A J I _   
      _ E V E N E R _ C _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #843 🟪 rarity:0.11 ⏱️ 0:02:12.429744

📜 2 sessions
🦄 🦄 🦄
🦄 🦄 🦄
🦄 🌌 🌌
Rarity: 0.11 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #689 🥳 30 ⏱️ 0:00:34.732210

🤔 30 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+199531 [199531] lij       q0  ? ␅
    @+199531 [199531] lij       q1  ? after
    @+299485 [299485] schrok    q2  ? ␅
    @+299485 [299485] schrok    q3  ? after
    @+349470 [349470] vakanties q4  ? ␅
    @+349470 [349470] vakanties q5  ? after
    @+361909 [361909] vervolg   q8  ? ␅
    @+361909 [361909] vervolg   q9  ? after
    @+365015 [365015] vind      q12 ? ␅
    @+365015 [365015] vind      q13 ? after
    @+366415 [366415] vlees     q14 ? ␅
    @+366415 [366415] vlees     q15 ? after
    @+367279 [367279] vlo       q16 ? ␅
    @+367279 [367279] vlo       q17 ? after
    @+367588 [367588] vlucht    q18 ? ␅
    @+367588 [367588] vlucht    q19 ? after
    @+367837 [367837] vocht     q20 ? ␅
    @+367837 [367837] vocht     q21 ? after
    @+367947 [367947] voed      q22 ? ␅
    @+367947 [367947] voed      q23 ? after
    @+367950 [367950] voeden    q28 ? ␅
    @+367950 [367950] voeden    q29 ? it
    @+367950 [367950] voeden    done. it
    @+367953 [367953] voeder    q26 ? ␅
    @+367953 [367953] voeder    q27 ? before
    @+367997 [367997] voeding   q24 ? ␅
    @+367997 [367997] voeding   q25 ? before
    @+368156 [368156] voedsel   q10 ? ␅
    @+368156 [368156] voedsel   q11 ? before
    @+374464 [374464] vrijst    q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1156 🥳 32 ⏱️ 0:00:41.711970

🤔 32 attempts
📜 1 sessions

    @        [     0] aa        
    @+98142  [ 98142] mac       q0  ? ␅
    @+98142  [ 98142] mac       q1  ? after
    @+147306 [147306] rho       q2  ? ␅
    @+147306 [147306] rho       q3  ? after
    @+171906 [171906] tag       q4  ? ␅
    @+171906 [171906] tag       q5  ? after
    @+181991 [181991] un        q6  ? ␅
    @+181991 [181991] un        q7  ? after
    @+185621 [185621] unretire  q10 ? ␅
    @+185621 [185621] unretire  q11 ? after
    @+187402 [187402] us        q12 ? ␅
    @+187402 [187402] us        q13 ? after
    @+187865 [187865] vambrace  q16 ? ␅
    @+187865 [187865] vambrace  q17 ? after
    @+187876 [187876] vamp      q22 ? ␅
    @+187876 [187876] vamp      q23 ? after
    @+187881 [187881] vampiest  q26 ? ␅
    @+187881 [187881] vampiest  q27 ? after
    @+187883 [187883] vampire   q30 ? ␅
    @+187883 [187883] vampire   q31 ? it
    @+187883 [187883] vampire   done. it
    @+187884 [187884] vampires  q28 ? ␅
    @+187884 [187884] vampires  q29 ? before
    @+187886 [187886] vampirish q24 ? ␅
    @+187886 [187886] vampirish q25 ? before
    @+187895 [187895] van       q20 ? ␅
    @+187895 [187895] van       q21 ? before
    @+188050 [188050] var       q18 ? ␅
    @+188050 [188050] var       q19 ? before
    @+188328 [188328] veal      q15 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1582 🥳 6 ⏱️ 0:01:11.934319

📜 1 sessions
💰 score: 48

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:ICTIC n n n n n remain:6058
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:3382
    ⬜⬜⬜⬜⬜ tried:DOGGO n n n n n remain:1289
    ⬜⬜⬜⬜⬜ tried:HUMPH n n n n n remain:444
    ⬜🟨⬜⬜⬜ tried:FEEZE n m n n n remain:63
    ⬜🟩⬜🟩🟨 tried:WAKEN n Y n Y m remain:8

    Undos used: 2

      8 words remaining
    x 6 unused letters
    = 48 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1725 🥳 16 ⏱️ 0:02:28.451572

📜 1 sessions
💰 score: 10000

    4/6
    ACRES 🟩⬜⬜🟨⬜
    ANOLE 🟩🟩⬜🟩🟩
    EKING 🟨🟨⬜🟨⬜
    ANKLE 🟩🟩🟩🟩🟩
    4/6
    ANKLE ⬜⬜⬜⬜🟨
    DREGS ⬜⬜🟨⬜🟨
    PESTO 🟨🟨🟩🟨⬜
    UPSET 🟩🟩🟩🟩🟩
    4/6
    UPSET ⬜⬜⬜⬜⬜
    INDOL ⬜⬜⬜⬜⬜
    CRAZY 🟩🟩🟩⬜⬜
    CRACK 🟩🟩🟩🟩🟩
    3/6
    CRACK ⬜🟨⬜🟩⬜
    RETCH 🟨🟩⬜🟩⬜
    MERCY 🟩🟩🟩🟩🟩
    Final 1/2
    ICHOR 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1702 😦 score:28 ⏱️ 0:03:53.608875

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. COMFY attempts:9 score:9
2. LOBBY attempts:6 score:6
3. DRE_S -ABCFGIKLMNOPTWY attempts:9 score:-1
4. PANEL attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1702 🥳 score:59 ⏱️ 0:01:42.435690

📜 1 sessions

Octordle Classic

1. BIGOT attempts:6 score:6
2. BELOW attempts:7 score:7
3. VAUNT attempts:10 score:10
4. RALLY attempts:3 score:3
5. BUDDY attempts:8 score:8
6. CANAL attempts:11 score:11
7. DRIFT attempts:5 score:5
8. HAVOC attempts:9 score:9

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1682 🥳 score:38 ⏱️ 0:02:08.707119

📜 1 sessions

Sedecordle Classic sedecordle.com

1. DADDY attempts:14 score:1
2. AXIOM attempts:9 score:4
3. MECCA attempts:15 score:1
4. ORBIT attempts:7 score:5
5. CLUED attempts:17 score:1
6. PIVOT attempts:4 score:8
7. THIEF attempts:5 score:0
8. DITTY attempts:17 score:5
9. PRIED attempts:6 score:0
10. RANDY attempts:8 score:6
11. CABBY attempts:13 score:1
12. RASPY attempts:2 score:3
13. SHOWN attempts:10 score:1
14. VALOR attempts:3 score:0
15. PLUSH attempts:11 score:1
16. PARKA attempts:12 score:1

# [squareword.org](squareword.org) 🧩 #1695 🥳 8 ⏱️ 0:02:28.627175

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟨 🟨 🟨 🟨 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P R A T
    C R E D O
    R I G O R
    A D A P T
    M E L T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1632 🥳 136 ⏱️ 0:03:23.156125

🤔 137 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 32 chat prompts
🤖 32 gemma4:12b replies
🥵  7 😎 40 🥶 86 🧊  3

      $1 #137 sugar          100.00°C 🥳 1000‰ ~134 used:0  [133]  source:gemma4
      $2 #118 pectin          50.26°C 🥵  976‰   ~4 used:7  [3]    source:gemma4
      $3  #20 juice           48.84°C 🥵  969‰  ~46 used:30 [45]   source:gemma4
      $4  #10 citrus          48.45°C 🥵  966‰  ~45 used:23 [44]   source:gemma4
      $5 #130 confectionery   47.01°C 🥵  951‰   ~3 used:3  [2]    source:gemma4
      $6 #131 candy           45.57°C 🥵  928‰   ~1 used:0  [0]    source:gemma4
      $7  #90 nutrient        43.79°C 🥵  903‰  ~37 used:13 [36]   source:gemma4
      $8 #132 caramel         43.77°C 🥵  901‰   ~2 used:0  [1]    source:gemma4
      $9  #11 grapefruit      41.95°C 😎  864‰  ~47 used:5  [46]   source:gemma4
     $10  #24 fruit           41.76°C 😎  857‰  ~38 used:2  [37]   source:gemma4
     $11  #19 clementine      41.62°C 😎  853‰  ~39 used:2  [38]   source:gemma4
     $12 #135 glucose         41.49°C 😎  849‰   ~5 used:0  [4]    source:gemma4
     $49  #94 dietary         29.63°C 🥶        ~48 used:0  [47]   source:gemma4
    $135 #128 wall            -1.15°C 🧊       ~135 used:0  [134]  source:gemma4

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1665 🥳 249 ⏱️ 0:07:07.397666

🤔 250 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 60 chat prompts
🤖 60 gemma4:12b replies
🥵  10 😎  35 🥶 174 🧊  30

      $1 #250 manipulation     100.00°C 🥳 1000‰ ~220 used:0  [219]  source:gemma4
      $2  #42 méthode           37.52°C 🥵  987‰  ~45 used:52 [44]   source:gemma4
      $3  #78 procédé           33.51°C 🥵  966‰  ~44 used:34 [43]   source:gemma4
      $4 #248 logiciel          33.13°C 🥵  959‰   ~1 used:1  [0]    source:gemma4
      $5 #157 manuel            33.01°C 🥵  956‰  ~42 used:17 [41]   source:gemma4
      $6  #53 outil             32.74°C 🥵  953‰  ~36 used:11 [35]   source:gemma4
      $7 #103 machine           32.57°C 🥵  951‰  ~37 used:11 [36]   source:gemma4
      $8 #197 consigne          32.35°C 🥵  948‰  ~38 used:11 [37]   source:gemma4
      $9 #212 précaution        31.88°C 🥵  942‰  ~39 used:11 [38]   source:gemma4
     $10  #94 matériel          31.85°C 🥵  940‰  ~40 used:11 [39]   source:gemma4
     $11  #62 technique         31.64°C 🥵  934‰  ~41 used:11 [40]   source:gemma4
     $12  #88 appareil          30.49°C 😎  896‰  ~43 used:2  [42]   source:gemma4
     $47  #69 script            22.65°C 🥶        ~52 used:0  [51]   source:gemma4
    $221 #141 industrie         -0.11°C 🧊       ~221 used:0  [220]  source:gemma4
