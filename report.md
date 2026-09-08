# 2026-09-08

- 🔗 alfagok.diginaut.net 🧩 #675 🥳 34 ⏱️ 0:00:45.351414
- 🔗 alphaguess.com 🧩 #1142 🥳 32 ⏱️ 0:00:34.296284
- 🔗 dontwordle.com 🧩 #1568 😳 6 ⏱️ 0:01:46.263178
- 🔗 dictionary.com hurdle 🧩 #1711 🥳 16 ⏱️ 0:02:33.512749
- 🔗 Quordle Classic 🧩 #1688 🥳 score:26 ⏱️ 0:01:36.942261
- 🔗 Octordle Classic 🧩 #1688 🥳 score:61 ⏱️ 0:02:12.115847
- 🔗 Sedecordle Classic 🧩 #1668 🥳 score:48 ⏱️ 0:02:08.189976
- 🔗 squareword.org 🧩 #1681 🥳 8 ⏱️ 0:02:21.357475
- 🔗 cemantle.certitudes.org 🧩 #1618 🥳 270 ⏱️ 0:03:05.076549
- 🔗 cemantix.certitudes.org 🧩 #1651 🥳 50 ⏱️ 0:01:14.967333

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

# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #675 🥳 34 ⏱️ 0:00:45.351414

🤔 34 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+199640 [199640] lijk       q0  ? ␅
    @+199640 [199640] lijk       q1  ? after
    @+199640 [199640] lijk       q2  ? ␅
    @+199640 [199640] lijk       q3  ? after
    @+299544 [299544] schroot    q4  ? ␅
    @+299544 [299544] schroot    q5  ? after
    @+349329 [349329] vakantie   q6  ? ␅
    @+349329 [349329] vakantie   q7  ? after
    @+351088 [351088] vecht      q12 ? ␅
    @+351088 [351088] vecht      q13 ? after
    @+351463 [351463] veen       q16 ? ␅
    @+351463 [351463] veen       q17 ? after
    @+351593 [351593] veer       q20 ? ␅
    @+351593 [351593] veer       q21 ? after
    @+351711 [351711] veest      q22 ? ␅
    @+351711 [351711] veest      q23 ? after
    @+351769 [351769] vege       q24 ? ␅
    @+351769 [351769] vege       q25 ? after
    @+351805 [351805] vegeteer   q26 ? ␅
    @+351805 [351805] vegeteer   q27 ? after
    @+351823 [351823] vei        q28 ? ␅
    @+351823 [351823] vei        q29 ? after
    @+351826 [351826] veil       q30 ? ␅
    @+351826 [351826] veil       q31 ? after
    @+351836 [351836] veilig     q32 ? ␅
    @+351836 [351836] veilig     q33 ? it
    @+351836 [351836] veilig     done. it
    @+351845 [351845] veiligheid q14 ? ␅
    @+351845 [351845] veiligheid q15 ? before
    @+352896 [352896] ver        q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1142 🥳 32 ⏱️ 0:00:34.296284

🤔 32 attempts
📜 1 sessions

    @        [     0] aa           
    @+98147  [ 98147] mac          q0  ? ␅
    @+98147  [ 98147] mac          q1  ? after
    @+98147  [ 98147] mac          q2  ? ␅
    @+98147  [ 98147] mac          q3  ? after
    @+98147  [ 98147] mac          q4  ? ␅
    @+98147  [ 98147] mac          q5  ? after
    @+122724 [122724] parol        q8  ? ␅
    @+122724 [122724] parol        q9  ? after
    @+135004 [135004] prop         q10 ? ␅
    @+135004 [135004] prop         q11 ? after
    @+141017 [141017] recon        q12 ? ␅
    @+141017 [141017] recon        q13 ? after
    @+141103 [141103] recons       q22 ? ␅
    @+141103 [141103] recons       q23 ? after
    @+141110 [141110] reconsider   q30 ? ␅
    @+141110 [141110] reconsider   q31 ? it
    @+141110 [141110] reconsider   done. it
    @+141115 [141115] reconsign    q28 ? ␅
    @+141115 [141115] reconsign    q29 ? before
    @+141128 [141128] reconstitute q26 ? ␅
    @+141128 [141128] reconstitute q27 ? before
    @+141159 [141159] recontour    q24 ? ␅
    @+141159 [141159] recontour    q25 ? before
    @+141219 [141219] recount      q20 ? ␅
    @+141219 [141219] recount      q21 ? before
    @+141425 [141425] red          q18 ? ␅
    @+141425 [141425] red          q19 ? before
    @+142208 [142208] ref          q16 ? ␅
    @+142208 [142208] ref          q17 ? before
    @+144150 [144150] rend         q15 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1568 😳 6 ⏱️ 0:01:46.263178

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:COOCH n n n n n remain:6849
    ⬜⬜⬜⬜⬜ tried:YUPPY n n n n n remain:3694
    ⬜⬜⬜⬜⬜ tried:BIBBS n n n n n remain:788
    ⬜⬜⬜⬜🟩 tried:GRRRL n n n n Y remain:36
    ⬜🟩⬜⬜🟩 tried:FATAL n Y n n Y remain:2
    🟩🟩🟩🟩🟩 tried:NAVEL Y Y Y Y Y remain:0

    Undos used: 3

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1711 🥳 16 ⏱️ 0:02:33.512749

📜 1 sessions
💰 score: 10000

    4/6
    SNARE 🟨⬜⬜⬜🟩
    TOUSE ⬜🟨⬜🟩🟩
    CHOSE ⬜⬜🟨🟩🟩
    OBESE 🟩🟩🟩🟩🟩
    4/6
    OBESE 🟨⬜⬜⬜⬜
    TOLAR ⬜🟨🟩🟨⬜
    AGLOW 🟩⬜🟩🟩🟩
    ALLOW 🟩🟩🟩🟩🟩
    4/6
    ALLOW 🟩⬜⬜⬜⬜
    AIDES 🟩🟨🟨⬜⬜
    ADMIN 🟩🟩🟩🟩⬜
    ADMIT 🟩🟩🟩🟩🟩
    3/6
    ADMIT 🟨⬜🟨⬜🟨
    MEATS 🟩⬜🟨🟨⬜
    MATCH 🟩🟩🟩🟩🟩
    Final 1/2
    TREAD 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1688 🥳 score:26 ⏱️ 0:01:36.942261

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. FLUNG attempts:5 score:5
2. DIARY attempts:6 score:6
3. HALVE attempts:7 score:7
4. BERTH attempts:8 score:8

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1688 🥳 score:61 ⏱️ 0:02:12.115847

📜 1 sessions

Octordle Classic

1. IVORY attempts:4 score:4
2. OVOID attempts:5 score:5
3. QUASH attempts:7 score:7
4. ICING attempts:6 score:6
5. VERVE attempts:12 score:12
6. APPLY attempts:9 score:9
7. THUMP attempts:8 score:8
8. JAZZY attempts:10 score:10

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1668 🥳 score:48 ⏱️ 0:02:08.189976

📜 1 sessions

Sedecordle Classic sedecordle.com

1. UNTIL attempts:4 score:0
2. HOTLY attempts:3 score:4
3. QUEUE attempts:12 score:1
4. CURVE attempts:10 score:2
5. EARLY attempts:5 score:0
6. LOFTY attempts:6 score:5
7. TRUNK attempts:8 score:0
8. GUESS attempts:11 score:8
9. CROWN attempts:14 score:1
10. SWAMP attempts:13 score:4
11. CHASM attempts:9 score:0
12. SHAFT attempts:7 score:9
13. LUMPY attempts:15 score:1
14. SAVOR attempts:16 score:5
15. PRUNE attempts:17 score:1
16. FIGHT attempts:18 score:7

# [squareword.org](squareword.org) 🧩 #1681 🥳 8 ⏱️ 0:02:21.357475

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟨 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S L A G S
    P I L O T
    A M O U R
    T I N G E
    S T E E P

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1618 🥳 270 ⏱️ 0:03:05.076549

🤔 271 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 49 chat prompts
🤖 49 dolphin3:latest replies
🔥   1 🥵   6 😎  31 🥶 226 🧊   6

      $1 #271 tunnel           100.00°C 🥳 1000‰ ~265 used:0  [264]  source:dolphin3
      $2 #270 trench            46.81°C 🔥  995‰   ~1 used:0  [0]    source:dolphin3
      $3 #233 pipe              40.45°C 🥵  978‰   ~7 used:6  [6]    source:dolphin3
      $4 #252 flume             38.95°C 🥵  973‰   ~5 used:4  [4]    source:dolphin3
      $5 #249 culvert           38.16°C 🥵  970‰   ~6 used:4  [5]    source:dolphin3
      $6 #247 aqueduct          37.37°C 🥵  965‰   ~2 used:2  [1]    source:dolphin3
      $7 #246 canal             36.40°C 🥵  958‰   ~4 used:3  [3]    source:dolphin3
      $8 #219 cavity            33.76°C 🥵  917‰   ~3 used:2  [2]    source:dolphin3
      $9 #257 waterway          30.46°C 😎  846‰   ~8 used:0  [7]    source:dolphin3
     $10 #258 dam               29.77°C 😎  835‰   ~9 used:0  [8]    source:dolphin3
     $11 #241 conduit           28.94°C 😎  799‰  ~10 used:0  [9]    source:dolphin3
     $12 #254 sewer             28.03°C 😎  750‰  ~11 used:0  [10]   source:dolphin3
     $40 #237 surface           20.91°C 🥶        ~45 used:0  [44]   source:dolphin3
    $266 #216 volume            -1.15°C 🧊       ~266 used:0  [265]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1651 🥳 50 ⏱️ 0:01:14.967333

🤔 51 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 18 chat prompts
🤖 18 dolphin3:latest replies
😱  1 🔥  1 😎  5 🥶 26 🧊 17

     $1 #51 urgent          100.00°C 🥳 1000‰ ~34 used:0  [33]  source:dolphin3
     $2 #43 urgence          57.93°C 😱  999‰  ~1 used:3  [0]   source:dolphin3
     $3 #45 priorité         39.87°C 🔥  996‰  ~2 used:0  [1]   source:dolphin3
     $4 #46 péril            24.30°C 😎  784‰  ~3 used:0  [2]   source:dolphin3
     $5 #26 garde            21.11°C 😎  557‰  ~5 used:3  [4]   source:dolphin3
     $6 #28 secours          21.06°C 😎  550‰  ~6 used:3  [5]   source:dolphin3
     $7 #14 chiot            19.51°C 😎  383‰  ~7 used:13 [6]   source:dolphin3
     $8 #29 service          17.97°C 😎  139‰  ~4 used:1  [3]   source:dolphin3
     $9 #42 réanimation      17.09°C 🥶       ~12 used:0  [11]  source:dolphin3
    $10 #31 vigilance        16.71°C 🥶       ~13 used:0  [12]  source:dolphin3
    $11 #36 sauvetage        16.27°C 🥶       ~14 used:0  [13]  source:dolphin3
    $12 #39 médical          15.36°C 🥶       ~15 used:0  [14]  source:dolphin3
    $13 #50 sécurité         14.60°C 🥶       ~16 used:0  [15]  source:dolphin3
    $35 #27 patrouille       -0.42°C 🧊       ~35 used:0  [34]  source:dolphin3
