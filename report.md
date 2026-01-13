# 2026-01-14

- 🔗 spaceword.org 🧩 2026-01-13 🏁 score 2168 ranked 43.5% 146/336 ⏱️ 14:25:39.695381
- 🔗 alfagok.diginaut.net 🧩 #438 🥳 15 ⏱️ 0:00:39.414658
- 🔗 alphaguess.com 🧩 #905 🥳 16 ⏱️ 0:00:39.999322
- 🔗 dictionary.com hurdle 🧩 #1474 🥳 16 ⏱️ 0:03:51.271654
- 🔗 Quordle Classic 🧩 #1451 🥳 score:23 ⏱️ 0:01:39.175590
- 🔗 dontwordle.com 🧩 #1331 🥳 6 ⏱️ 0:02:11.527193
- 🔗 Octordle Classic 🧩 #1451 🥳 score:60 ⏱️ 0:03:46.728130
- 🔗 squareword.org 🧩 #1444 🥳 8 ⏱️ 0:02:02.240034
- 🔗 cemantle.certitudes.org 🧩 #1381 🥳 106 ⏱️ 0:02:31.453444
- 🔗 cemantix.certitudes.org 🧩 #1414 🥳 158 ⏱️ 0:06:21.731012
- 🔗 Quordle Rescue 🧩 #65 🥳 score:30 ⏱️ 0:01:27.024485
- 🔗 Octordle Rescue 🧩 #1451 🥳 score:9 ⏱️ 0:03:23.642870
- 🔗 Quordle Sequence 🧩 #1451 🥳 score:28 ⏱️ 0:01:44.873240

# Dev

## WIP

- hurdle: add novel words to wordlist

- meta:
  - rework SolverHarness => Solver{ Library, Scope }
  - variants: regression on 01-06 running quordle

- ui:
  - Handle -- stabilizing core over Listing
  - Shell -- minimizing over Handle
- meta: rework command model over Shell

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


















# spaceword.org 🧩 2026-01-11 🏗️ score 2173 current ranking 42/308 ⏱️ 8:04:00.125934

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 42/308

      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ O P _ P O G O E D
      _ W E K A _ _ _ _ O
      _ L _ A D J U R E S
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _




# [spaceword.org](spaceword.org) 🧩 2026-01-13 🏁 score 2168 ranked 43.5% 146/336 ⏱️ 14:25:39.695381

📜 6 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 146/336

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ W A B S _ _ _ V _   
      _ _ H I E _ J _ A _   
      _ _ A C I N I _ N _   
      _ _ _ E _ U N I S _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #438 🥳 15 ⏱️ 0:00:39.414658

🤔 15 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+1      [     1] &-tekens    
    @+2      [     2] -cijferig   
    @+3      [     3] -e-mail     
    @+199833 [199833] lijm        q0  ? after
    @+299738 [299738] schub       q1  ? after
    @+324314 [324314] sub         q3  ? after
    @+327305 [327305] tafel       q6  ? after
    @+327604 [327604] tal         q9  ? after
    @+327770 [327770] tam         q10 ? after
    @+327815 [327815] tamelijk    q14 ? it
    @+327815 [327815] tamelijk    done. it
    @+327857 [327857] tand        q11 ? before
    @+328046 [328046] tank        q8  ? before
    @+328893 [328893] technologie q7  ? before
    @+330497 [330497] televisie   q5  ? before
    @+336914 [336914] toetsing    q4  ? before
    @+349521 [349521] vakantie    q2  ? before

# [alphaguess.com](alphaguess.com) 🧩 #905 🥳 16 ⏱️ 0:00:39.999322

🤔 16 attempts
📜 1 sessions

    @        [     0] aa           
    @+1      [     1] aah          
    @+2      [     2] aahed        
    @+3      [     3] aahing       
    @+98220  [ 98220] mach         q0  ? after
    @+147373 [147373] rhotic       q1  ? after
    @+171643 [171643] ta           q2  ? after
    @+182008 [182008] un           q3  ? after
    @+185638 [185638] unretire     q5  ? after
    @+185743 [185743] uns          q8  ? after
    @+186133 [186133] unstep       q9  ? after
    @+186324 [186324] unthink      q10 ? after
    @+186424 [186424] untrim       q11 ? after
    @+186477 [186477] unurged      q12 ? after
    @+186481 [186481] unusual      q15 ? it
    @+186481 [186481] unusual      done. it
    @+186488 [186488] unuttered    q14 ? before
    @+186498 [186498] unveil       q13 ? before
    @+186529 [186529] unwarinesses q7  ? before
    @+187419 [187419] us           q6  ? before
    @+189270 [189270] vicar        q4  ? before

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1474 🥳 16 ⏱️ 0:03:51.271654

📜 1 sessions
💰 score: 10000

    4/6
    ARISE ⬜⬜⬜⬜⬜
    HUNKY 🟨⬜🟩⬜⬜
    MONTH ⬜🟩🟩⬜🟩
    CONCH 🟩🟩🟩🟩🟩
    3/6
    CONCH 🟩⬜⬜⬜🟨
    CHASE 🟩🟩⬜⬜🟨
    CHIEF 🟩🟩🟩🟩🟩
    4/6
    CHIEF ⬜⬜⬜⬜⬜
    SOLAR ⬜⬜🟨🟨⬜
    BLAND ⬜🟨🟨⬜⬜
    APTLY 🟩🟩🟩🟩🟩
    4/6
    APTLY 🟨⬜⬜🟨⬜
    BLARE ⬜🟩🟩⬜⬜
    FLASK ⬜🟩🟩🟨🟩
    SLACK 🟩🟩🟩🟩🟩
    Final 1/2
    MIMIC 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1451 🥳 score:23 ⏱️ 0:01:39.175590

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SWOOP attempts:9 score:9
2. FIRST attempts:7 score:7
3. GHOST attempts:3 score:3
4. ALPHA attempts:4 score:4

# [dontwordle.com](dontwordle.com) 🧩 #1331 🥳 6 ⏱️ 0:02:11.527193

📜 2 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:TAZZA n n n n n remain:5598
    ⬜⬜⬜⬜⬜ tried:WHICH n n n n n remain:2468
    ⬜⬜⬜⬜⬜ tried:DRYLY n n n n n remain:470
    ⬜🟩⬜⬜⬜ tried:BOFFO n Y n n n remain:68
    ⬜🟩⬜⬜🟨 tried:GONGS n Y n n m remain:3
    ⬜🟩⬜🟩🟩 tried:POSSE n Y n Y Y remain:1

    Undos used: 4

      1 words remaining
    x 7 unused letters
    = 7 total score

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1451 🥳 score:60 ⏱️ 0:03:46.728130

📜 1 sessions

Octordle Classic

1. WIDEN attempts:9 score:9
2. PUFFY attempts:10 score:10
3. SWING attempts:7 score:7
4. ALLAY attempts:8 score:8
5. ALIVE attempts:4 score:4
6. SIGMA attempts:6 score:6
7. USURP attempts:11 score:11
8. COVEN attempts:5 score:5

# [squareword.org](squareword.org) 🧩 #1444 🥳 8 ⏱️ 0:02:02.240034

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟩 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S M A S H
    P A S T A
    O U T E R
    O V E R T
    F E R N S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1381 🥳 106 ⏱️ 0:02:31.453444

🤔 107 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 23 chat prompts
🤖 23 dolphin3:latest replies
🥵  6 😎 15 🥶 80 🧊  5

      $1 #107   ~1 battery               100.00°C 🥳 1000‰
      $2  #96   ~6 voltage                38.66°C 🥵  982‰
      $3  #98   ~5 capacitance            37.01°C 🥵  974‰
      $4  #87  ~11 electric               34.55°C 🥵  945‰
      $5  #40  ~17 cell                   34.23°C 🥵  940‰
      $6  #70  ~14 alkaline               32.97°C 🥵  923‰
      $7 #101   ~4 electromotive          32.70°C 🥵  918‰
      $8 #103   ~3 inductance             29.14°C 😎  812‰
      $9  #25  ~19 power                  28.89°C 😎  804‰
     $10  #85  ~12 charge                 28.31°C 😎  779‰
     $11  #62  ~15 acid                   27.35°C 😎  735‰
     $12  #93   ~8 electrostatics         26.54°C 😎  690‰
     $23  #91      electromagnetism       19.87°C 🥶
    $103  #55      recognition            -0.32°C 🧊

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1414 🥳 158 ⏱️ 0:06:21.731012

🤔 159 attempts
📜 1 sessions
🫧 12 chat sessions
⁉️ 30 chat prompts
🤖 30 dolphin3:latest replies
🔥  1 🥵  4 😎 12 🥶 91 🧊 50

      $1 #159   ~1 fabrication       100.00°C 🥳 1000‰
      $2 #142   ~7 production         57.79°C 🔥  998‰
      $3 #108  ~16 artisanal          48.95°C 🥵  975‰
      $4 #117  ~15 industriel         47.27°C 🥵  962‰
      $5 #133  ~12 sécheur            42.21°C 🥵  909‰
      $6 #147   ~4 conception         41.95°C 🥵  905‰
      $7 #140   ~8 matériel           41.32°C 😎  888‰
      $8 #137  ~10 industrie          38.02°C 😎  794‰
      $9  #32  ~18 savonnerie         36.82°C 😎  754‰
     $10 #131  ~13 séchage            35.67°C 😎  709‰
     $11 #145   ~5 transformation     34.64°C 😎  658‰
     $12 #124  ~14 manufacturier      34.59°C 😎  655‰
     $19 #157      développement      27.75°C 🥶
    $110  #62      pinceau            -0.15°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #65 🥳 score:30 ⏱️ 0:01:27.024485

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. MERIT attempts:6 score:6
2. TRUST attempts:7 score:7
3. TAROT attempts:8 score:8
4. GOOSE attempts:9 score:9

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1451 🥳 score:9 ⏱️ 0:03:23.642870

📜 1 sessions

Octordle Rescue

1. MOTOR attempts:5 score:5
2. LARGE attempts:8 score:8
3. BLUSH attempts:9 score:9
4. CREME attempts:6 score:6
5. ROOST attempts:7 score:7
6. COVEN attempts:12 score:12
7. PLANK attempts:10 score:10
8. JOKER attempts:11 score:11

# [Quordle Sequence](m-w.com/games/quordle/#/sequence) 🧩 #1451 🥳 score:28 ⏱️ 0:01:44.873240

📜 1 sessions

Quordle Sequence m-w.com/games/quordle/

1. CAGEY attempts:4 score:4
2. RENAL attempts:7 score:7
3. PREEN attempts:8 score:8
4. WHEEL attempts:9 score:9
