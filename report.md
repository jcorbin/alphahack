# 2026-10-10

- 🔗 spaceword.org 🧩 2026-10-09 🏁 score 2170 ranked 30.9% 102/330 ⏱️ 0:14:20.416684
- 🔗 wordgrid 🧩 #861 🟪 rarity:0.17 ⏱️ 0:02:41.902146
- 🔗 alfagok.diginaut.net 🧩 #707 🥳 34 ⏱️ 0:00:56.166011
- 🔗 alphaguess.com 🧩 #1174 🥳 32 ⏱️ 0:00:57.623426
- 🔗 dontwordle.com 🧩 #1600 🥳 6 ⏱️ 0:01:48.531518
- 🔗 dictionary.com hurdle 🧩 #1743 🥳 20 ⏱️ 0:04:52.472602
- 🔗 Quordle Classic 🧩 #1720 🥳 score:24 ⏱️ 0:02:24.303668
- 🔗 Octordle Classic 🧩 #1720 😦 score:74 ⏱️ 0:02:59.266038
- 🔗 Sedecordle Classic 🧩 #1700 🥳 score:44 ⏱️ 0:03:45.380523
- 🔗 squareword.org 🧩 #1713 🥳 7 ⏱️ 0:02:21.692859
- 🔗 cemantle.certitudes.org 🧩 #1650 🥳 748 ⏱️ 0:55:47.281992
- 🔗 cemantix.certitudes.org 🧩 #1683 🥳 310 ⏱️ 0:32:09.488289

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






# [spaceword.org](spaceword.org) 🧩 2026-10-09 🏁 score 2170 ranked 30.9% 102/330 ⏱️ 0:14:20.416684

📜 5 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 102/330

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ R O V E _ _ _   
      _ _ _ I _ _ Q _ _ _   
      _ _ _ A _ N U G _ _   
      _ _ _ _ F O I N _ _   
      _ _ _ R E G N A _ _   
      _ _ _ _ _ _ E W _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #861 🟪 rarity:0.17 ⏱️ 0:02:41.902146

📜 2 sessions
🦄 🦄 🌌
🌌 🌌 🌌
🦄 🌌 🦄
Rarity: 0.17 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #707 🥳 34 ⏱️ 0:00:56.166011

🤔 34 attempts
📜 1 sessions

    @        [     0] &-teken         
    @+99672  [ 99672] ex              q2  ? ␅
    @+99672  [ 99672] ex              q3  ? after
    @+111327 [111327] ge              q8  ? ␅
    @+111327 [111327] ge              q9  ? after
    @+116733 [116733] gel             q10 ? ␅
    @+116733 [116733] gel             q11 ? after
    @+120650 [120650] geprepareerd    q12 ? ␅
    @+120650 [120650] geprepareerd    q13 ? after
    @+121854 [121854] ges             q14 ? ␅
    @+121854 [121854] ges             q15 ? after
    @+122533 [122533] gesleutel       q18 ? ␅
    @+122533 [122533] gesleutel       q19 ? after
    @+122857 [122857] gesprek         q20 ? ␅
    @+122857 [122857] gesprek         q21 ? after
    @+122946 [122946] gesprongen      q24 ? ␅
    @+122946 [122946] gesprongen      q25 ? after
    @+122990 [122990] gestagneerd     q26 ? ␅
    @+122990 [122990] gestagneerd     q27 ? after
    @+122996 [122996] gestalte        q32 ? ␅
    @+122996 [122996] gestalte        q33 ? it
    @+122996 [122996] gestalte        done. it
    @+123000 [123000] gestalttherapie q30 ? ␅
    @+123000 [123000] gestalttherapie q31 ? before
    @+123010 [123010] gestand         q28 ? ␅
    @+123010 [123010] gestand         q29 ? before
    @+123034 [123034] geste           q22 ? ␅
    @+123034 [123034] geste           q23 ? before
    @+123211 [123211] gestrand        q16 ? ␅
    @+123211 [123211] gestrand        q17 ? before
    @+124571 [124571] gevoel          q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1174 🥳 32 ⏱️ 0:00:57.623426

🤔 32 attempts
📜 1 sessions

    @        [     0] aa          
    @+98142  [ 98142] mac         q0  ? ␅
    @+98142  [ 98142] mac         q1  ? after
    @+122089 [122089] par         q4  ? ␅
    @+122089 [122089] par         q5  ? after
    @+128387 [128387] placid      q8  ? ␅
    @+128387 [128387] placid      q9  ? after
    @+129516 [129516] po          q10 ? ␅
    @+129516 [129516] po          q11 ? after
    @+132098 [132098] precept     q12 ? ␅
    @+132098 [132098] precept     q13 ? after
    @+132135 [132135] precinct    q26 ? ␅
    @+132135 [132135] precinct    q27 ? after
    @+132139 [132139] precious    q30 ? ␅
    @+132139 [132139] precious    q31 ? it
    @+132139 [132139] precious    done. it
    @+132153 [132153] precipitant q28 ? ␅
    @+132153 [132153] precipitant q29 ? before
    @+132172 [132172] precipitous q24 ? ␅
    @+132172 [132172] precipitous q25 ? before
    @+132248 [132248] preconcert  q20 ? ␅
    @+132248 [132248] preconcert  q21 ? before
    @+132402 [132402] predict     q18 ? ␅
    @+132402 [132402] predict     q19 ? before
    @+132720 [132720] prehension  q16 ? ␅
    @+132720 [132720] prehension  q17 ? before
    @+133343 [133343] prese       q14 ? ␅
    @+133343 [133343] prese       q15 ? before
    @+134683 [134683] progress    q6  ? ␅
    @+134683 [134683] progress    q7  ? before
    @+147304 [147304] rho         q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1600 🥳 6 ⏱️ 0:01:48.531518

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:YABBY n n n n n remain:5520
    ⬜⬜⬜⬜⬜ tried:GOGOS n n n n n remain:1236
    ⬜⬜⬜⬜⬜ tried:CHUCK n n n n n remain:493
    ⬜🟩⬜⬜⬜ tried:FILMI n Y n n n remain:61
    🟨🟩⬜🟩⬜ tried:DIRER m Y n Y n remain:14
    ⬜🟩⬜🟩🟨 tried:PIPED n Y n Y m remain:1

    Undos used: 3

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1743 🥳 20 ⏱️ 0:04:52.472602

📜 2 sessions
💰 score: 9600

    6/6
    TASER ⬜🟩⬜🟩🟩
    PAGER ⬜🟩⬜🟩🟩
    WALER ⬜🟩⬜🟩🟩
    BACKS ⬜🟩🟩⬜⬜
    FARMS ⬜🟩🟨⬜⬜
    RACER 🟩🟩🟩🟩🟩
    6/6
    RACER ⬜⬜⬜🟨⬜
    LENDS ⬜🟨⬜⬜🟨
    THOSE 🟨⬜⬜🟨🟩
    KYLIX ⬜⬜⬜🟨⬜
    BUMPS ⬜⬜🟨⬜🟨
    SMITE 🟩🟩🟩🟩🟩
    3/6
    SMITE ⬜⬜🟩⬜🟩
    ALIVE 🟩🟩🟩⬜🟩
    ALIKE 🟩🟩🟩🟩🟩
    3/6
    ALIKE ⬜⬜🟨⬜⬜
    TONIC 🟨🟨⬜🟩⬜
    ORBIT 🟩🟩🟩🟩🟩
    Final 2/2
    PYLON 🟩🟨🟩⬜⬜
    PALSY 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1720 🥳 score:24 ⏱️ 0:02:24.303668

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. SWEAT attempts:6 score:6
2. THIRD attempts:7 score:7
3. RURAL attempts:8 score:8
4. CLASP attempts:3 score:3

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1720 😦 score:74 ⏱️ 0:02:59.266038

📜 1 sessions

Octordle Classic

1. ALLOT attempts:4 score:4
2. GRO_S -ABCDEHIJKLMNPTUVWY attempts:13 score:-1
3. MOVER attempts:12 score:12
4. CLOUT attempts:5 score:5
5. MERRY attempts:9 score:9
6. GULCH attempts:7 score:7
7. DRIVE attempts:13 score:13
8. JUMBO attempts:10 score:10

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1700 🥳 score:44 ⏱️ 0:03:45.380523

📜 1 sessions

Sedecordle Classic sedecordle.com

1. CEASE attempts:8 score:0
2. BRASS attempts:19 score:8
3. URINE attempts:15 score:1
4. TAFFY attempts:19 score:5
5. STOVE attempts:16 score:1
6. BURLY attempts:14 score:6
7. FLANK attempts:18 score:1
8. MISSY attempts:13 score:8
9. ROOMY attempts:12 score:1
10. SCARE attempts:5 score:2
11. ERROR attempts:11 score:1
12. SCORE attempts:6 score:1
13. QUACK attempts:10 score:1
14. TRACK attempts:4 score:0
15. LEVER attempts:17 score:1
16. KRILL attempts:3 score:7

# [squareword.org](squareword.org) 🧩 #1713 🥳 7 ⏱️ 0:02:21.692859

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    O C T E T
    A R E N A
    S A N D S
    I N S E T
    S E E D Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1650 🥳 748 ⏱️ 0:55:47.281992

🤔 749 attempts
📜 1 sessions
🫧 42 chat sessions
⁉️ 224 chat prompts
🤖 124 llama3.2:latest replies
🤖 75 dolphin3:latest replies
🤖 25 gemma4:12b replies
🔥   2 🥵  17 😎  70 🥶 618 🧊  41

      $1 #749 practitioner         100.00°C 🥳 1000‰ ~708 used:0   [707]  source:llama3.2
      $2 #432 doctor                55.65°C 🔥  995‰  ~69 used:110 [68]   source:llama3.2
      $3 #745 clinician             54.10°C 🔥  994‰   ~1 used:11  [0]    source:llama3.2
      $4 #672 dentist               50.98°C 🥵  984‰  ~76 used:21  [75]   source:llama3.2
      $5 #447 pharmacist            50.72°C 🥵  983‰  ~78 used:40  [77]   source:llama3.2
      $6 #541 therapist             50.46°C 🥵  982‰  ~70 used:12  [69]   source:llama3.2
      $7 #419 nurse                 50.14°C 🥵  981‰  ~71 used:12  [70]   source:llama3.2
      $8 #624 endodontist           48.89°C 🥵  975‰   ~8 used:8   [7]    source:llama3.2
      $9 #599 dentistry             47.29°C 🥵  966‰   ~9 used:8   [8]    source:llama3.2
     $10 #737 medico                46.26°C 🥵  963‰  ~10 used:8   [9]    source:llama3.2
     $11 #723 prosthodontist        45.76°C 🥵  960‰   ~2 used:7   [1]    source:llama3.2
     $21 #601 gastroenterology      39.09°C 😎  895‰  ~15 used:0   [14]   source:llama3.2
     $91 #721 sedation              26.11°C 🥶       ~104 used:0   [103]  source:llama3.2
    $709 #574 board                 -0.01°C 🧊       ~709 used:0   [708]  source:llama3.2

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1683 🥳 310 ⏱️ 0:32:09.488289

🤔 311 attempts
📜 1 sessions
🫧 14 chat sessions
⁉️ 72 chat prompts
🤖 10 dolphin3:latest replies
🤖 62 gemma4:12b replies
😱   1 🔥   3 🥵  24 😎  57 🥶 182 🧊  43

      $1 #311 sincère           100.00°C 🥳 1000‰ ~268 used:0  [267]  source:dolphin3
      $2 #273 sincérité          64.17°C 😱  999‰   ~1 used:45 [0]    source:gemma4  
      $3 #277 honnêteté          54.21°C 🔥  996‰   ~9 used:19 [8]    source:gemma4  
      $4 #185 sympathie          51.63°C 🔥  992‰  ~27 used:34 [26]   source:gemma4  
      $5 #155 amitié             49.87°C 🔥  991‰  ~25 used:21 [24]   source:gemma4  
      $6 #151 sentiment          47.95°C 🥵  988‰  ~75 used:11 [74]   source:gemma4  
      $7 #154 amour              47.87°C 🥵  987‰  ~26 used:3  [25]   source:gemma4  
      $8 #290 vérité             47.71°C 🥵  986‰  ~10 used:2  [9]    source:gemma4  
      $9 #227 générosité         45.20°C 🥵  981‰  ~11 used:2  [10]   source:gemma4  
     $10 #283 droiture           44.87°C 🥵  979‰  ~12 used:2  [11]   source:gemma4  
     $11 #310 authentique        44.29°C 🥵  976‰   ~2 used:0  [1]    source:dolphin3
     $30 #204 empathie           38.17°C 😎  897‰  ~28 used:0  [27]   source:gemma4  
     $87 #269 voix               25.83°C 🥶        ~91 used:0  [90]   source:gemma4  
    $269  #13 stylo              -0.02°C 🧊       ~269 used:0  [268]  source:gemma4  
