# 2026-04-04

- 🔗 spaceword.org 🧩 2026-04-03 🏁 score 2168 ranked 40.0% 136/340 ⏱️ 0:22:38.607282
- 🔗 alfagok.diginaut.net 🧩 #518 🥳 40 ⏱️ 0:00:48.191763
- 🔗 alphaguess.com 🧩 #985 🥳 36 ⏱️ 0:00:38.863981
- 🔗 dontwordle.com 🧩 #1411 🥳 6 ⏱️ 0:01:13.176395
- 🔗 dictionary.com hurdle 🧩 #1554 🥳 18 ⏱️ 0:03:15.457321
- 🔗 Quordle Classic 🧩 #1531 🥳 score:26 ⏱️ 0:01:53.152490
- 🔗 Octordle Classic 🧩 #1531 🥳 score:53 ⏱️ 0:03:05.277333
- 🔗 squareword.org 🧩 #1524 🥳 7 ⏱️ 0:02:01.104411
- 🔗 cemantle.certitudes.org 🧩 #1461 🥳 104 ⏱️ 0:01:54.635562
- 🔗 cemantix.certitudes.org 🧩 #1494 🥳 103 ⏱️ 0:00:55.567325

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


































# [spaceword.org](spaceword.org) 🧩 2026-04-03 🏁 score 2168 ranked 40.0% 136/340 ⏱️ 0:22:38.607282

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 136/340

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ U _ C _ _ _ _   
      _ _ _ L O O F _ _ _   
      _ _ _ V _ D O _ _ _   
      _ _ _ A _ E X _ _ _   
      _ _ _ _ _ I T _ _ _   
      _ _ _ _ J A R _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ _ B A T _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #518 🥳 40 ⏱️ 0:00:48.191763

🤔 40 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+199606 [199606] lij          q0  ? ␅
    @+199606 [199606] lij          q1  ? after
    @+199606 [199606] lij          q2  ? ␅
    @+199606 [199606] lij          q3  ? after
    @+247688 [247688] op           q6  ? ␅
    @+247688 [247688] op           q7  ? after
    @+254092 [254092] out          q12 ? ␅
    @+254092 [254092] out          q13 ? after
    @+254279 [254279] over         q16 ? ␅
    @+254279 [254279] over         q17 ? after
    @+254910 [254910] overgevoelig q20 ? ␅
    @+254910 [254910] overgevoelig q21 ? after
    @+254972 [254972] overhaal     q24 ? ␅
    @+254972 [254972] overhaal     q25 ? after
    @+255000 [255000] overhang     q26 ? ␅
    @+255000 [255000] overhang     q27 ? after
    @+255017 [255017] overheen     q30 ? ␅
    @+255017 [255017] overheen     q31 ? after
    @+255020 [255020] overheers    q32 ? ␅
    @+255020 [255020] overheers    q33 ? after
    @+255026 [255026] overheersing q34 ? ␅
    @+255026 [255026] overheersing q35 ? after
    @+255028 [255028] overheerst   q36 ? ␅
    @+255028 [255028] overheerst   q37 ? after
    @+255031 [255031] overheid     q38 ? ␅
    @+255031 [255031] overheid     q39 ? it
    @+255031 [255031] overheid     done. it
    @+255032 [255032] overheids    q22 ? ␅
    @+255032 [255032] overheids    q23 ? before
    @+255541 [255541] overleg      q19 ? before

# [alphaguess.com](alphaguess.com) 🧩 #985 🥳 36 ⏱️ 0:00:38.863981

🤔 36 attempts
📜 1 sessions

    @       [    0] aa       
    @+2802  [ 2802] ag       q14 ? ␅
    @+2802  [ 2802] ag       q15 ? after
    @+4334  [ 4334] alma     q16 ? ␅
    @+4334  [ 4334] alma     q17 ? after
    @+4350  [ 4350] alme     q26 ? ␅
    @+4350  [ 4350] alme     q27 ? after
    @+4361  [ 4361] almond   q28 ? ␅
    @+4361  [ 4361] almond   q29 ? after
    @+4365  [ 4365] almoners q30 ? ␅
    @+4365  [ 4365] almoners q31 ? after
    @+4367  [ 4367] almonry  q32 ? ␅
    @+4367  [ 4367] almonry  q33 ? after
    @+4368  [ 4368] almost   q34 ? ␅
    @+4368  [ 4368] almost   q35 ? it
    @+4368  [ 4368] almost   done. it
    @+4369  [ 4369] alms     q24 ? ␅
    @+4369  [ 4369] alms     q25 ? before
    @+4406  [ 4406] alone    q22 ? ␅
    @+4406  [ 4406] alone    q23 ? before
    @+4477  [ 4477] alt      q20 ? ␅
    @+4477  [ 4477] alt      q21 ? before
    @+4619  [ 4619] am       q18 ? ␅
    @+4619  [ 4619] am       q19 ? before
    @+5876  [ 5876] angel    q12 ? ␅
    @+5876  [ 5876] angel    q13 ? before
    @+11763 [11763] back     q10 ? ␅
    @+11763 [11763] back     q11 ? before
    @+23681 [23681] camp     q8  ? ␅
    @+23681 [23681] camp     q9  ? before
    @+47380 [47380] dis      q7  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1411 🥳 6 ⏱️ 0:01:13.176395

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:YUPPY n n n n n remain:7572
    ⬜⬜⬜⬜⬜ tried:KEBOB n n n n n remain:1494
    ⬜⬜🟩⬜⬜ tried:CHICS n n Y n n remain:63
    ⬜⬜🟩⬜⬜ tried:DJINN n n Y n n remain:35
    ⬜🟨🟩⬜⬜ tried:GLIFF n m Y n n remain:8
    🟩⬜🟩⬜🟩 tried:TWILL Y n Y n Y remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1554 🥳 18 ⏱️ 0:03:15.457321

📜 1 sessions
💰 score: 9800

    5/6
    AISLE 🟨⬜🟨⬜🟨
    NEARS ⬜🟨🟨⬜🟨
    SATED 🟩🟨🟨🟨⬜
    STEAM 🟩🟨🟩🟩⬜
    SWEAT 🟩🟩🟩🟩🟩
    4/6
    SWEAT 🟨⬜⬜🟩⬜
    MINAS ⬜⬜⬜🟩🟨
    OSCAR ⬜🟩⬜🟩⬜
    USUAL 🟩🟩🟩🟩🟩
    4/6
    USUAL ⬜🟨⬜🟨🟨
    TESLA ⬜🟩🟨🟨🟨
    LEADS 🟩🟩🟩⬜🟨
    LEASH 🟩🟩🟩🟩🟩
    3/6
    LEASH ⬜🟨⬜🟨⬜
    PIERS ⬜⬜🟩⬜🟨
    SCENT 🟩🟩🟩🟩🟩
    Final 2/2
    GRIOT ⬜🟩🟩⬜🟩
    DRIFT 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1531 🥳 score:26 ⏱️ 0:01:53.152490

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. MOTEL attempts:9 score:9
2. COVEN attempts:7 score:7
3. DRIER attempts:4 score:4
4. SCOLD attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1531 🥳 score:53 ⏱️ 0:03:05.277333

📜 2 sessions

Octordle Classic

1. DRILL attempts:4 score:4
2. AVAIL attempts:7 score:7
3. MOTIF attempts:6 score:6
4. LEAKY attempts:8 score:8
5. KNOWN attempts:11 score:11
6. EPOXY attempts:9 score:9
7. GROUT attempts:3 score:3
8. DALLY attempts:5 score:5

# [squareword.org](squareword.org) 🧩 #1524 🥳 7 ⏱️ 0:02:01.104411

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B R A W L
    R E T R Y
    O T T E R
    T R I C E
    H O C K S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1461 🥳 104 ⏱️ 0:01:54.635562

🤔 105 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 34 chat prompts
🤖 34 dolphin3:latest replies
🥵  5 😎 14 🥶 85

      $1 #105 shade            100.00°C 🥳 1000‰ ~105 used:0  [104]  source:dolphin3
      $2 #102 tint              47.47°C 🥵  984‰   ~2 used:4  [1]    source:dolphin3
      $3 #103 color             42.80°C 🥵  927‰   ~1 used:2  [0]    source:dolphin3
      $4  #43 glow              42.41°C 🥵  916‰  ~18 used:25 [17]   source:dolphin3
      $5  #65 colors            42.10°C 🥵  908‰  ~15 used:15 [14]   source:dolphin3
      $6  #87 hue               42.04°C 🥵  907‰   ~3 used:10 [2]    source:dolphin3
      $7  #91 illumination      37.90°C 😎  746‰  ~16 used:2  [15]   source:dolphin3
      $8  #42 shimmer           37.76°C 😎  739‰  ~19 used:3  [18]   source:dolphin3
      $9  #99 coloration        37.66°C 😎  731‰   ~4 used:0  [3]    source:dolphin3
     $10  #57 iridescence       36.99°C 😎  692‰  ~17 used:2  [16]   source:dolphin3
     $11  #59 opalescent        36.31°C 😎  639‰   ~5 used:1  [4]    source:dolphin3
     $12 #100 pigmentation      35.04°C 😎  546‰   ~6 used:0  [5]    source:dolphin3
     $13  #82 luminous          34.45°C 😎  490‰   ~7 used:0  [6]    source:dolphin3
     $21  #88 pigment           30.57°C 🥶        ~25 used:0  [24]   source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1494 🥳 103 ⏱️ 0:00:55.567325

🤔 104 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 11 chat prompts
🤖 11 dolphin3:latest replies
🔥  2 🥵 10 😎 19 🥶 46 🧊 26

      $1 #104 pacte             100.00°C 🥳 1000‰  ~78 used:0 [77]   source:dolphin3
      $2  #50 politique          40.38°C 🔥  998‰   ~2 used:8 [1]    source:dolphin3
      $3  #60 gouvernement       40.33°C 🔥  997‰   ~1 used:6 [0]    source:dolphin3
      $4 #102 loi                35.03°C 🥵  989‰   ~3 used:0 [2]    source:dolphin3
      $5  #97 démocratique       32.85°C 🥵  981‰   ~4 used:0 [3]    source:dolphin3
      $6  #69 réforme            31.76°C 🥵  977‰   ~5 used:1 [4]    source:dolphin3
      $7  #78 social             30.15°C 🥵  962‰   ~6 used:0 [5]    source:dolphin3
      $8  #85 parlement          29.55°C 🥵  960‰   ~7 used:0 [6]    source:dolphin3
      $9  #65 constitutionnel    29.39°C 🥵  956‰   ~8 used:0 [7]    source:dolphin3
     $10  #99 gouvernemental     28.81°C 🥵  948‰   ~9 used:0 [8]    source:dolphin3
     $11  #80 économique         27.75°C 🥵  929‰  ~10 used:0 [9]    source:dolphin3
     $14  #67 législatif         26.24°C 😎  896‰  ~13 used:0 [12]   source:dolphin3
     $33  #95 dialogue           16.81°C 🥶        ~35 used:0 [34]   source:dolphin3
     $79  #31 artistique         -0.02°C 🧊        ~79 used:0 [78]   source:dolphin3
