# 2026-03-20

- 🔗 spaceword.org 🧩 2026-03-19 🏁 score 2168 ranked 37.5% 128/341 ⏱️ 23:08:13.662142
- 🔗 alfagok.diginaut.net 🧩 #503 🥳 32 ⏱️ 0:01:05.767228
- 🔗 alphaguess.com 🧩 #970 🥳 38 ⏱️ 0:00:38.751172
- 🔗 dontwordle.com 🧩 #1396 🥳 6 ⏱️ 0:01:33.152105
- 🔗 dictionary.com hurdle 🧩 #1539 🥳 18 ⏱️ 0:03:05.632463
- 🔗 Quordle Classic 🧩 #1516 🥳 score:22 ⏱️ 0:01:35.215933
- 🔗 Octordle Classic 🧩 #1516 🥳 score:59 ⏱️ 0:03:43.218171
- 🔗 squareword.org 🧩 #1509 🥳 8 ⏱️ 0:02:33.377079
- 🔗 cemantle.certitudes.org 🧩 #1446 🥳 12 ⏱️ 0:00:13.854786
- 🔗 cemantix.certitudes.org 🧩 #1479 🥳 168 ⏱️ 0:04:56.457007

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



















# [spaceword.org](spaceword.org) 🧩 2026-03-19 🏁 score 2168 ranked 37.5% 128/341 ⏱️ 23:08:13.662142

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 128/341

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ H _ _ _ _ Q _ L _   
      _ E _ Z _ _ U _ O _   
      _ R _ O A R I N G _   
      _ E X O G E N _ O _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #503 🥳 32 ⏱️ 0:01:05.767228

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+99737  [ 99737] ex         q2  ? ␅
    @+99737  [ 99737] ex         q3  ? after
    @+124636 [124636] gevoel     q6  ? ␅
    @+124636 [124636] gevoel     q7  ? after
    @+125333 [125333] gewild     q16 ? ␅
    @+125333 [125333] gewild     q17 ? after
    @+125406 [125406] gewoon     q22 ? ␅
    @+125406 [125406] gewoon     q23 ? after
    @+125410 [125410] gewoonlijk q28 ? ␅
    @+125410 [125410] gewoonlijk q29 ? after
    @+125410 [125410] gewoonlijk q30 ? ␅
    @+125410 [125410] gewoonlijk q31 ? it
    @+125410 [125410] gewoonlijk done. it
    @+125416 [125416] gewoonte   q26 ? ␅
    @+125416 [125416] gewoonte   q27 ? before
    @+125449 [125449] geworstel  q24 ? ␅
    @+125449 [125449] geworstel  q25 ? before
    @+125498 [125498] gewrocht   q20 ? ␅
    @+125498 [125498] gewrocht   q21 ? before
    @+125669 [125669] gezel      q18 ? ␅
    @+125669 [125669] gezel      q19 ? before
    @+126046 [126046] gezondheid q14 ? ␅
    @+126046 [126046] gezondheid q15 ? before
    @+127714 [127714] glamour    q12 ? ␅
    @+127714 [127714] glamour    q13 ? before
    @+130808 [130808] gras       q10 ? ␅
    @+130808 [130808] gras       q11 ? before
    @+137126 [137126] handt      q8  ? ␅
    @+137126 [137126] handt      q9  ? before
    @+149642 [149642] huishoud   q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #970 🥳 38 ⏱️ 0:00:38.751172

🤔 38 attempts
📜 1 sessions

    @       [    0] aa          
    @+47381 [47381] dis         q2  ? ␅
    @+47381 [47381] dis         q3  ? after
    @+72799 [72799] gremmy      q4  ? ␅
    @+72799 [72799] gremmy      q5  ? after
    @+85503 [85503] ins         q6  ? ␅
    @+85503 [85503] ins         q7  ? after
    @+88663 [88663] jacks       q10 ? ␅
    @+88663 [88663] jacks       q11 ? after
    @+90194 [90194] ka          q12 ? ␅
    @+90194 [90194] ka          q13 ? after
    @+90603 [90603] keck        q16 ? ␅
    @+90603 [90603] keck        q17 ? after
    @+90813 [90813] keratosis   q18 ? ␅
    @+90813 [90813] keratosis   q19 ? after
    @+90901 [90901] keto        q20 ? ␅
    @+90901 [90901] keto        q21 ? after
    @+90943 [90943] key         q22 ? ␅
    @+90943 [90943] key         q23 ? after
    @+90944 [90944] keyboard    q36 ? ␅
    @+90944 [90944] keyboard    q37 ? it
    @+90944 [90944] keyboard    done. it
    @+90945 [90945] keyboarded  q34 ? ␅
    @+90945 [90945] keyboarded  q35 ? before
    @+90946 [90946] keyboarder  q32 ? ␅
    @+90946 [90946] keyboarder  q33 ? before
    @+90948 [90948] keyboarding q30 ? ␅
    @+90948 [90948] keyboarding q31 ? before
    @+90953 [90953] keybuttons  q28 ? ␅
    @+90953 [90953] keybuttons  q29 ? before
    @+90962 [90962] keyhole     q27 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1396 🥳 6 ⏱️ 0:01:33.152105

📜 1 sessions
💰 score: 9

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:FEEZE n n n n n remain:6482
    ⬜⬜⬜⬜⬜ tried:PIPIT n n n n n remain:2683
    ⬜⬜⬜⬜⬜ tried:MORRO n n n n n remain:779
    ⬜🟨⬜⬜⬜ tried:XYLYL n m n n n remain:123
    ⬜🟨⬜⬜🟩 tried:BUBBY n m n n Y remain:4
    ⬜🟩🟩⬜🟩 tried:GAUDY n Y Y n Y remain:1

    Undos used: 3

      1 words remaining
    x 9 unused letters
    = 9 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1539 🥳 18 ⏱️ 0:03:05.632463

📜 1 sessions
💰 score: 9800

    4/6
    STALE 🟩⬜⬜⬜🟩
    SHIRE 🟩⬜🟩⬜🟩
    SPINE 🟩⬜🟩🟩🟩
    SWINE 🟩🟩🟩🟩🟩
    4/6
    SWINE ⬜⬜⬜⬜⬜
    MORAY ⬜⬜🟩🟨🟩
    PARTY 🟩🟩🟩⬜🟩
    PARRY 🟩🟩🟩🟩🟩
    4/6
    PARRY ⬜⬜⬜⬜⬜
    OLEIN ⬜⬜⬜🟨🟨
    STING ⬜🟨🟩🟩⬜
    THINK 🟩🟩🟩🟩🟩
    5/6
    THINK 🟨⬜⬜⬜⬜
    STEAL ⬜🟨🟩⬜⬜
    CREPT ⬜🟨🟩⬜🟩
    OVERT ⬜⬜🟩🟩🟩
    EXERT 🟩🟩🟩🟩🟩
    Final 1/2
    COUPE 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1516 🥳 score:22 ⏱️ 0:01:35.215933

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. BUSED attempts:6 score:6
2. FRONT attempts:4 score:4
3. JEWEL attempts:5 score:5
4. TRIPE attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1516 🥳 score:59 ⏱️ 0:03:43.218171

📜 1 sessions

Octordle Classic

1. DECAL attempts:7 score:7
2. MONEY attempts:9 score:9
3. APING attempts:12 score:12
4. FOCAL attempts:6 score:6
5. SAUNA attempts:3 score:3
6. WHINY attempts:5 score:5
7. TILDE attempts:4 score:4
8. MOWER attempts:9 score:13

# [squareword.org](squareword.org) 🧩 #1509 🥳 8 ⏱️ 0:02:33.377079

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    T W I S T
    H E N N A
    R A D A R
    E V I C T
    W E E K S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1446 🥳 12 ⏱️ 0:00:13.854786

🤔 13 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 3 chat prompts
🤖 3 dolphin3:latest replies
🔥 1 😎 2 🥶 9

     $1 #13 rhythm    100.00°C 🥳 1000‰ ~13 used:0 [12]  source:dolphin3
     $2 #12 melody     49.21°C 🔥  993‰  ~1 used:0 [0]   source:dolphin3
     $3  #7 music      33.83°C 😎  787‰  ~2 used:1 [1]   source:dolphin3
     $4 #11 harmony    32.83°C 😎  727‰  ~3 used:0 [2]   source:dolphin3
     $5  #2 beach      10.60°C 🥶        ~4 used:0 [3]   source:dolphin3
     $6  #4 car         8.77°C 🥶        ~5 used:0 [4]   source:dolphin3
     $7  #9 pizza       8.46°C 🥶        ~6 used:0 [5]   source:dolphin3
     $8  #6 dog         8.09°C 🥶        ~7 used:0 [6]   source:dolphin3
     $9  #5 computer    7.05°C 🥶        ~8 used:0 [7]   source:dolphin3
    $10 #10 space       5.71°C 🥶        ~9 used:0 [8]   source:dolphin3
    $11  #8 phone       5.61°C 🥶       ~10 used:0 [9]   source:dolphin3
    $12  #3 book        4.03°C 🥶       ~11 used:0 [10]  source:dolphin3
    $13  #1 apple       1.25°C 🥶       ~12 used:0 [11]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1479 🥳 168 ⏱️ 0:04:56.457007

🤔 169 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 56 chat prompts
🤖 56 dolphin3:latest replies
🔥  5 🥵 22 😎 53 🥶 56 🧊 32

      $1 #169 stage               100.00°C 🥳 1000‰ ~137 used:0  [136]  source:dolphin3
      $2  #59 formation            61.33°C 🔥  998‰  ~26 used:43 [25]   source:dolphin3
      $3  #30 cursus               59.87°C 🔥  997‰  ~24 used:38 [23]   source:dolphin3
      $4  #74 master               49.35°C 🔥  994‰   ~8 used:18 [7]    source:dolphin3
      $5  #69 perfectionnement     48.87°C 🔥  993‰   ~7 used:11 [6]    source:dolphin3
      $6 #162 module               47.64°C 🔥  990‰   ~1 used:6  [0]    source:dolphin3
      $7 #167 session              46.81°C 🥵  988‰   ~2 used:1  [1]    source:dolphin3
      $8  #91 formateur            46.74°C 🥵  986‰   ~9 used:2  [8]    source:dolphin3
      $9  #72 professionnel        46.39°C 🥵  985‰  ~10 used:2  [9]    source:dolphin3
     $10 #116 alternance           45.61°C 🥵  984‰  ~11 used:2  [10]   source:dolphin3
     $11  #18 cours                45.60°C 🥵  983‰  ~27 used:8  [26]   source:dolphin3
     $29  #35 programme            32.51°C 😎  889‰  ~28 used:0  [27]   source:dolphin3
     $82 #155 valorisation         17.89°C 🥶        ~81 used:0  [80]   source:dolphin3
    $138   #9 linge                -0.11°C 🧊       ~138 used:0  [137]  source:dolphin3
