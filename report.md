# 2026-04-11

- 🔗 spaceword.org 🧩 2026-04-10 🏁 score 2173 ranked 4.9% 16/326 ⏱️ 0:10:06.844344
- 🔗 alfagok.diginaut.net 🧩 #525 🥳 32 ⏱️ 0:00:33.823148
- 🔗 alphaguess.com 🧩 #992 🥳 36 ⏱️ 0:00:36.080963
- 🔗 dontwordle.com 🧩 #1418 🥳 6 ⏱️ 0:01:30.311214
- 🔗 dictionary.com hurdle 🧩 #1561 🥳 15 ⏱️ 0:02:49.120600
- 🔗 cemantle.certitudes.org 🧩 #1468 🥳 149 ⏱️ 0:20:58.938750
- 🔗 Quordle Classic 🧩 #1538 🥳 score:24 ⏱️ 0:01:35.888057
- 🔗 Octordle Classic 🧩 #1538 🥳 score:59 ⏱️ 0:03:18.080755
- 🔗 squareword.org 🧩 #1531 🥳 7 ⏱️ 0:01:45.017920
- 🔗 cemantix.certitudes.org 🧩 #1501 🥳 1414 ⏱️ 0:50:41.848776

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









































# [spaceword.org](spaceword.org) 🧩 2026-04-10 🏁 score 2173 ranked 4.9% 16/326 ⏱️ 0:10:06.844344

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 16/326

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ B _ T A T O U A Y   
      _ O N E _ _ R _ X U   
      _ A _ G A Z E D _ K   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #525 🥳 32 ⏱️ 0:00:33.823148

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+49841  [ 49841] boks      q6  ? ␅
    @+49841  [ 49841] boks      q7  ? after
    @+50537  [ 50537] bonnen    q18 ? ␅
    @+50537  [ 50537] bonnen    q19 ? after
    @+50819  [ 50819] boom      q20 ? ␅
    @+50819  [ 50819] boom      q21 ? after
    @+50923  [ 50923] boompje   q24 ? ␅
    @+50923  [ 50923] boompje   q25 ? after
    @+50966  [ 50966] boomt     q26 ? ␅
    @+50966  [ 50966] boomt     q27 ? after
    @+50996  [ 50996] boomzaden q28 ? ␅
    @+50996  [ 50996] boomzaden q29 ? after
    @+51000  [ 51000] boon      q30 ? ␅
    @+51000  [ 51000] boon      q31 ? it
    @+51000  [ 51000] boon      done. it
    @+51026  [ 51026] boor      q22 ? ␅
    @+51026  [ 51026] boor      q23 ? before
    @+51248  [ 51248] boots     q16 ? ␅
    @+51248  [ 51248] boots     q17 ? before
    @+52683  [ 52683] bouw      q14 ? ␅
    @+52683  [ 52683] bouw      q15 ? before
    @+55933  [ 55933] bron      q12 ? ␅
    @+55933  [ 55933] bron      q13 ? before
    @+62280  [ 62280] cement    q10 ? ␅
    @+62280  [ 62280] cement    q11 ? before
    @+74754  [ 74754] dc        q8  ? ␅
    @+74754  [ 74754] dc        q9  ? before
    @+99737  [ 99737] ex        q4  ? ␅
    @+99737  [ 99737] ex        q5  ? before
    @+199606 [199606] lij       q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #992 🥳 36 ⏱️ 0:00:36.080963

🤔 36 attempts
📜 1 sessions

    @        [     0] aa        
    @+98216  [ 98216] mach      q0  ? ␅
    @+98216  [ 98216] mach      q1  ? after
    @+147371 [147371] rhumb     q2  ? ␅
    @+147371 [147371] rhumb     q3  ? after
    @+153315 [153315] sea       q8  ? ␅
    @+153315 [153315] sea       q9  ? after
    @+156351 [156351] ship      q10 ? ␅
    @+156351 [156351] ship      q11 ? after
    @+157879 [157879] sim       q12 ? ␅
    @+157879 [157879] sim       q13 ? after
    @+158529 [158529] ski       q14 ? ␅
    @+158529 [158529] ski       q15 ? after
    @+159003 [159003] slaps     q16 ? ␅
    @+159003 [159003] slaps     q17 ? after
    @+159114 [159114] sled      q20 ? ␅
    @+159114 [159114] sled      q21 ? after
    @+159147 [159147] sleep     q22 ? ␅
    @+159147 [159147] sleep     q23 ? after
    @+159186 [159186] sleeve    q24 ? ␅
    @+159186 [159186] sleeve    q25 ? after
    @+159191 [159191] sleevelet q30 ? ␅
    @+159191 [159191] sleevelet q31 ? after
    @+159193 [159193] sleeves   q34 ? ␅
    @+159193 [159193] sleeves   q35 ? it
    @+159193 [159193] sleeves   done. it
    @+159194 [159194] sleeving  q32 ? ␅
    @+159194 [159194] sleeving  q33 ? before
    @+159196 [159196] sleigh    q28 ? ␅
    @+159196 [159196] sleigh    q29 ? before
    @+159205 [159205] slender   q27 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1418 🥳 6 ⏱️ 0:01:30.311214

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:SIBBS n n n n n remain:4209
    ⬜⬜⬜⬜⬜ tried:EFFED n n n n n remain:1465
    ⬜⬜⬜⬜⬜ tried:JNANA n n n n n remain:377
    ⬜⬜⬜⬜⬜ tried:CRUCK n n n n n remain:81
    ⬜🟨⬜⬜⬜ tried:PHPHT n m n n n remain:3
    🟩🟩🟩🟩⬜ tried:HOLLO Y Y Y Y n remain:1

    Undos used: 4

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1561 🥳 15 ⏱️ 0:02:49.120600

📜 1 sessions
💰 score: 10100

    3/6
    PARSE ⬜⬜⬜🟨🟩
    STILE 🟩🟩⬜⬜🟩
    STONE 🟩🟩🟩🟩🟩
    3/6
    STONE 🟩⬜⬜🟩⬜
    SWANK 🟩⬜⬜🟩🟩
    SLINK 🟩🟩🟩🟩🟩
    3/6
    SLINK ⬜🟨🟩⬜⬜
    TRIAL ⬜⬜🟩⬜🟨
    CHILD 🟩🟩🟩🟩🟩
    5/6
    CHILD ⬜⬜⬜⬜⬜
    STORE ⬜⬜⬜🟨🟨
    FREAK ⬜🟨🟨🟨⬜
    PAGER ⬜🟩🟩🟩🟩
    WAGER 🟩🟩🟩🟩🟩
    Final 1/2
    DRONE 🟩🟩🟩🟩🟩

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1468 🥳 149 ⏱️ 0:20:58.938750

🤔 150 attempts
📜 1 sessions
🫧 19 chat sessions
⁉️ 50 chat prompts
🤖 34 dolphin3:latest replies
🤖 16 gemma4:26b replies
🥵   3 😎  18 🥶 125 🧊   3

      $1 #150 pair           100.00°C 🥳 1000‰ ~147 used:0  [146]  source:dolphin3
      $2 #129 twin            38.87°C 🥵  986‰   ~3 used:6  [2]    source:dolphin3
      $3 #147 twins           34.39°C 🥵  971‰   ~1 used:1  [0]    source:dolphin3
      $4 #139 multiple        30.64°C 🥵  952‰   ~2 used:2  [1]    source:dolphin3
      $5  #53 lace            28.11°C 😎  893‰  ~20 used:21 [19]   source:dolphin3
      $6  #21 sateen          26.63°C 😎  851‰  ~21 used:33 [20]   source:gemma4  
      $7 #116 shantung        26.13°C 😎  828‰  ~15 used:4  [14]   source:dolphin3
      $8 #127 knot            25.86°C 😎  815‰   ~4 used:0  [3]    source:dolphin3
      $9 #145 quadruplet      25.56°C 😎  795‰   ~5 used:0  [4]    source:dolphin3
     $10 #138 identical       25.41°C 😎  786‰   ~6 used:0  [5]    source:dolphin3
     $11  #12 satin           25.21°C 😎  773‰  ~19 used:15 [18]   source:gemma4  
     $12 #125 doublet         24.87°C 😎  746‰   ~9 used:2  [8]    source:dolphin3
     $23  #49 lightweight     19.92°C 🥶        ~22 used:0  [21]   source:dolphin3
    $148 #117 gathered        -1.23°C 🧊       ~148 used:0  [147]  source:dolphin3

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1538 🥳 score:24 ⏱️ 0:01:35.888057

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. MINER attempts:8 score:8
2. PLIER attempts:4 score:4
3. PASTE attempts:5 score:5
4. PITCH attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1538 🥳 score:59 ⏱️ 0:03:18.080755

📜 1 sessions

Octordle Classic

1. REGAL attempts:7 score:7
2. SHIRK attempts:9 score:9
3. KNOLL attempts:8 score:8
4. CHASM attempts:3 score:3
5. PIXIE attempts:5 score:5
6. FELLA attempts:6 score:6
7. DEALT attempts:11 score:11
8. GUILT attempts:10 score:10

# [squareword.org](squareword.org) 🧩 #1531 🥳 7 ⏱️ 0:01:45.017920

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S H E R D
    C A M E O
    A T O L L
    M E T A L
    P R E Y S

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1501 🥳 1414 ⏱️ 0:50:41.848776

🤔 1415 attempts
📜 1 sessions
🫧 132 chat sessions
⁉️ 585 chat prompts
🤖 414 llama3.2:latest replies
🤖 171 dolphin3:latest replies
🔥   7 🥵  45 😎 199 🥶 915 🧊 248

       $1 #1415 unanime            100.00°C 🥳 1000‰ ~1167 used:0   [1166]  source:llama3  
       $2  #295 saluer              46.87°C 🔥  998‰  ~247 used:485 [246]   source:dolphin3
       $3 #1373 consensus           46.64°C 🔥  997‰    ~3 used:15  [2]     source:llama3  
       $4  #289 féliciter           45.21°C 🔥  995‰  ~243 used:257 [242]   source:dolphin3
       $5  #522 exprimer            43.03°C 🔥  994‰   ~23 used:86  [22]    source:llama3  
       $6  #151 réitérer            42.95°C 🔥  993‰   ~24 used:90  [23]    source:dolphin3
       $7  #277 applaudir           42.33°C 🔥  991‰   ~21 used:81  [20]    source:dolphin3
       $8  #437 réjouir             41.55°C 🔥  990‰   ~22 used:81  [21]    source:llama3  
       $9 #1041 désapprobation      41.43°C 🥵  989‰   ~25 used:9   [24]    source:llama3  
      $10  #575 déplorer            41.25°C 🥵  988‰   ~26 used:9   [25]    source:llama3  
      $11  #270 souligner           41.13°C 🥵  987‰   ~27 used:9   [26]    source:dolphin3
      $54 #1034 désapprouver        31.57°C 😎  893‰   ~47 used:0   [46]    source:llama3  
     $253  #897 scandale            21.00°C 🥶        ~256 used:0   [255]   source:llama3  
    $1168  #351 nouvelle            -0.02°C 🧊       ~1168 used:0   [1167]  source:dolphin3
