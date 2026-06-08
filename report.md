# 2026-06-09

- 🔗 spaceword.org 🧩 2026-06-08 🏁 score 2173 ranked 3.4% 11/325 ⏱️ 1:47:14.754316
- 🔗 alfagok.diginaut.net 🧩 #584 🥳 44 ⏱️ 0:00:49.287160
- 🔗 alphaguess.com 🧩 #1051 🥳 32 ⏱️ 0:00:37.455572
- 🔗 dontwordle.com 🧩 #1477 🥳 6 ⏱️ 0:01:44.320140
- 🔗 dictionary.com hurdle 🧩 #1620 🥳 19 ⏱️ 0:03:08.409969
- 🔗 Quordle Classic 🧩 #1597 🥳 score:20 ⏱️ 0:01:21.709123
- 🔗 Octordle Classic 🧩 #1597 🥳 score:52 ⏱️ 0:03:05.865670
- 🔗 squareword.org 🧩 #1590 🥳 8 ⏱️ 0:02:10.217986
- 🔗 cemantle.certitudes.org 🧩 #1527 🥳 52 ⏱️ 0:00:25.465240
- 🔗 cemantix.certitudes.org 🧩 #1560 🥳 120 ⏱️ 0:02:12.895692

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













# [spaceword.org](spaceword.org) 🧩 2026-06-08 🏁 score 2173 ranked 3.4% 11/325 ⏱️ 1:47:14.754316

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 11/325

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ R _ C H O R I Z O   
      _ E Q U I N E _ I D   
      _ V _ T _ O I _ P _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #584 🥳 44 ⏱️ 0:00:49.287160

🤔 44 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+199766 [199766] lijm      q0  ? ␅
    @+199766 [199766] lijm      q1  ? after
    @+199766 [199766] lijm      q2  ? ␅
    @+199766 [199766] lijm      q3  ? after
    @+247637 [247637] op        q6  ? ␅
    @+247637 [247637] op        q7  ? after
    @+254041 [254041] out       q12 ? ␅
    @+254041 [254041] out       q13 ? after
    @+256797 [256797] pa        q14 ? ␅
    @+256797 [256797] pa        q15 ? after
    @+258412 [258412] pap       q16 ? ␅
    @+258412 [258412] pap       q17 ? after
    @+258702 [258702] para      q20 ? ␅
    @+258702 [258702] para      q21 ? after
    @+259068 [259068] pare      q22 ? ␅
    @+259068 [259068] pare      q23 ? after
    @+259159 [259159] paretten  q26 ? ␅
    @+259159 [259159] paretten  q27 ? after
    @+259191 [259191] pari      q28 ? ␅
    @+259191 [259191] pari      q29 ? after
    @+259220 [259220] paritair  q40 ? ␅
    @+259220 [259220] paritair  q41 ? after
    @+259225 [259225] park      q42 ? ␅
    @+259225 [259225] park      q43 ? it
    @+259225 [259225] park      done. it
    @+259244 [259244] parkeer   q24 ? ␅
    @+259244 [259244] parkeer   q25 ? before
    @+259435 [259435] parlement q18 ? ␅
    @+259435 [259435] parlement q19 ? before
    @+260517 [260517] pater     q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1051 🥳 32 ⏱️ 0:00:37.455572

🤔 32 attempts
📜 1 sessions

    @        [     0] aa        
    @+98214  [ 98214] mach      q0  ? ␅
    @+98214  [ 98214] mach      q1  ? after
    @+122775 [122775] parr      q4  ? ␅
    @+122775 [122775] parr      q5  ? after
    @+125807 [125807] petti     q10 ? ␅
    @+125807 [125807] petti     q11 ? after
    @+127320 [127320] pidgin    q12 ? ␅
    @+127320 [127320] pidgin    q13 ? after
    @+128073 [128073] pis       q14 ? ␅
    @+128073 [128073] pis       q15 ? after
    @+128450 [128450] plain     q16 ? ␅
    @+128450 [128450] plain     q17 ? after
    @+128634 [128634] plasm     q18 ? ␅
    @+128634 [128634] plasm     q19 ? after
    @+128732 [128732] plat      q20 ? ␅
    @+128732 [128732] plat      q21 ? after
    @+128788 [128788] platinoid q22 ? ␅
    @+128788 [128788] platinoid q23 ? after
    @+128817 [128817] platter   q24 ? ␅
    @+128817 [128817] platter   q25 ? after
    @+128823 [128823] platy     q26 ? ␅
    @+128823 [128823] platy     q27 ? after
    @+128834 [128834] platys    q28 ? ␅
    @+128834 [128834] platys    q29 ? after
    @+128839 [128839] plausible q30 ? ␅
    @+128839 [128839] plausible q31 ? it
    @+128839 [128839] plausible done. it
    @+128844 [128844] play      q8  ? ␅
    @+128844 [128844] play      q9  ? before
    @+135066 [135066] proper    q7  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1477 🥳 6 ⏱️ 0:01:44.320140

📜 1 sessions
💰 score: 12

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:YAPPY n n n n n remain:5357
    ⬜⬜⬜⬜⬜ tried:REFER n n n n n remain:1475
    ⬜⬜⬜⬜⬜ tried:COCOS n n n n n remain:115
    ⬜⬜⬜⬜⬜ tried:JUGUM n n n n n remain:34
    ⬜⬜🟩⬜⬜ tried:TWIXT n n Y n n remain:3
    🟩🟩🟩🟩⬜ tried:BLINI Y Y Y Y n remain:2

    Undos used: 4

      2 words remaining
    x 6 unused letters
    = 12 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1620 🥳 19 ⏱️ 0:03:08.409969

📜 1 sessions
💰 score: 9700

    5/6
    TASER ⬜⬜⬜🟨🟨
    BORNE ⬜🟨🟨⬜🟩
    WHORE ⬜⬜🟩🟨🟩
    DROVE ⬜🟩🟩🟩🟩
    GROVE 🟩🟩🟩🟩🟩
    3/6
    GROVE ⬜⬜🟨⬜🟨
    NOSED 🟨🟨⬜🟩⬜
    OFTEN 🟩🟩🟩🟩🟩
    4/6
    OFTEN 🟨⬜⬜⬜⬜
    SCOLD ⬜🟨🟩🟨⬜
    BLOCK ⬜🟩🟩🟩🟩
    CLOCK 🟩🟩🟩🟩🟩
    5/6
    CLOCK ⬜🟨⬜⬜⬜
    MEALS ⬜⬜⬜🟩⬜
    GIRLY ⬜⬜🟨🟩🟩
    TRULY ⬜🟩⬜🟩🟩
    DRYLY 🟩🟩🟩🟩🟩
    Final 2/2
    HARES ⬜🟨🟨🟩⬜
    AMBER 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1597 🥳 score:20 ⏱️ 0:01:21.709123

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. VENOM attempts:6 score:6
2. UNITE attempts:2 score:2
3. SHIRT attempts:8 score:8
4. ANGER attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1597 🥳 score:52 ⏱️ 0:03:05.865670

📜 1 sessions

Octordle Classic

1. WRYLY attempts:7 score:7
2. BRAWL attempts:8 score:8
3. AFTER attempts:9 score:9
4. CHEEK attempts:10 score:10
5. ENSUE attempts:6 score:6
6. CHART attempts:3 score:3
7. ANGST attempts:5 score:5
8. AWAIT attempts:4 score:4

# [squareword.org](squareword.org) 🧩 #1590 🥳 8 ⏱️ 0:02:10.217986

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟨
    🟨 🟨 🟩 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C R A M
    C R E D O
    R A V E L
    I N E P T
    P E L T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1527 🥳 52 ⏱️ 0:00:25.465240

🤔 53 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 8 chat prompts
🤖 8 dolphin3:latest replies
😎  6 🥶 43 🧊  3

     $1 #53 warning        100.00°C 🥳 1000‰ ~50 used:0 [49]  source:dolphin3
     $2 #45 catastrophic    26.87°C 😎  853‰  ~1 used:0 [0]   source:dolphin3
     $3 #29 squall          23.90°C 😎  718‰  ~5 used:4 [4]   source:dolphin3
     $4 #40 thunderstorm    23.35°C 😎  684‰  ~3 used:2 [2]   source:dolphin3
     $5 #14 storm           20.86°C 😎  445‰  ~6 used:5 [5]   source:dolphin3
     $6 #17 thunder         20.86°C 😎  443‰  ~4 used:3 [3]   source:dolphin3
     $7 #48 strike          19.39°C 😎  225‰  ~2 used:0 [1]   source:dolphin3
     $8 #44 weather         18.34°C 🥶        ~7 used:0 [6]   source:dolphin3
     $9 #32 downpour        18.02°C 🥶        ~8 used:0 [7]   source:dolphin3
    $10 #49 thunderhead     17.03°C 🥶        ~9 used:0 [8]   source:dolphin3
    $11 #23 hurricane       16.92°C 🥶       ~10 used:0 [9]   source:dolphin3
    $12 #30 blistering      16.54°C 🥶       ~11 used:0 [10]  source:dolphin3
    $13 #16 lightning       16.47°C 🥶       ~12 used:0 [11]  source:dolphin3
    $51  #2 astronaut       -0.33°C 🧊       ~51 used:0 [50]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1560 🥳 120 ⏱️ 0:02:12.895692

🤔 121 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 28 chat prompts
🤖 28 dolphin3:latest replies
🔥  1 🥵 11 😎 42 🥶 53 🧊 13

      $1 #121 partage             100.00°C 🥳 1000‰ ~108 used:0  [107]  source:dolphin3
      $2 #109 échange              60.81°C 🔥  998‰   ~1 used:5  [0]    source:dolphin3
      $3  #89 collaboratif         42.56°C 🥵  988‰  ~11 used:10 [10]   source:dolphin3
      $4  #64 complémentarité      41.31°C 🥵  984‰  ~51 used:13 [50]   source:dolphin3
      $5  #91 coopératif           38.34°C 🥵  976‰   ~6 used:2  [5]    source:dolphin3
      $6 #111 confrontation        38.02°C 🥵  973‰   ~2 used:1  [1]    source:dolphin3
      $7 #112 dialogue             37.89°C 🥵  972‰   ~3 used:0  [2]    source:dolphin3
      $8  #94 collectif            37.57°C 🥵  968‰   ~7 used:2  [6]    source:dolphin3
      $9  #95 participatif         35.04°C 🥵  945‰   ~4 used:1  [3]    source:dolphin3
     $10  #63 coopération          34.73°C 🥵  941‰   ~9 used:6  [8]    source:dolphin3
     $11  #93 coopérer             32.74°C 🥵  918‰   ~5 used:0  [4]    source:dolphin3
     $14 #120 interactivité        31.82°C 😎  896‰  ~12 used:0  [11]   source:dolphin3
     $56  #62 équipe               20.05°C 🥶        ~56 used:0  [55]   source:dolphin3
    $109  #28 concours             -0.70°C 🧊       ~109 used:0  [108]  source:dolphin3
