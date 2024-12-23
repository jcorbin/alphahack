# 2026-01-09

- 🔗 spaceword.org 🧩 2026-01-08 🏁 score 2173 ranked 5.9% 19/324 ⏱️ 3:21:39.562587
- 🔗 alfagok.diginaut.net 🧩 #433 🥳 13 ⏱️ 0:00:49.289706
- 🔗 alphaguess.com 🧩 #899 🥳 13 ⏱️ 0:00:42.850556
- 🔗 dontwordle.com 🧩 #1326 🥳 6 ⏱️ 0:02:14.880938
- 🔗 dictionary.com hurdle 🧩 #1469 😦 20 ⏱️ 0:04:01.785935
- 🔗 Quordle Classic 🧩 #1446 🥳 score:18 ⏱️ 0:01:20.078266
- 🔗 Octordle Classic 🧩 #1446 🥳 score:51 ⏱️ 0:03:41.257300
- 🔗 squareword.org 🧩 #1439 🥳 7 ⏱️ 0:01:52.492816
- 🔗 cemantle.certitudes.org 🧩 #1376 🥳 71 ⏱️ 0:01:00.777655
- 🔗 cemantix.certitudes.org 🧩 #1409 🥳 416 ⏱️ 0:09:16.537568
- 🔗 Quordle Rescue 🧩 #60 🥳 score:25 ⏱️ 0:01:25.898903
- 🔗 Quordle Sequence 🧩 #1446 🥳 score:25 ⏱️ 0:01:29.188679
- 🔗 Octordle Rescue 🧩 #1446 🥳 score:8 ⏱️ 0:04:29.220331
- 🔗 Octordle Sequence 🧩 #1446 🥳 score:60 ⏱️ 0:03:15.568408

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















# spaceword.org 🧩 2026-01-08 🏁 score 2173 ranked 5.9% 19/324 ⏱️ 3:21:39.562587

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 19/324

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ K Y E _ _ _   
      _ _ _ _ _ _ Q _ _ _   
      _ _ _ _ F O U _ _ _   
      _ _ _ _ O M A _ _ _   
      _ _ _ _ X _ L _ _ _   
      _ _ _ _ I T _ _ _ _   
      _ _ _ _ E R A _ _ _   
      _ _ _ _ R I N _ _ _   
      _ _ _ _ _ O _ _ _ _   


# alfagok.diginaut.net 🧩 #433 🥳 13 ⏱️ 0:00:49.289706

🤔 13 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+99758  [ 99758] ex         q2  ? after
    @+149454 [149454] huis       q3  ? after
    @+174561 [174561] kind       q4  ? after
    @+187197 [187197] krontjongs q5  ? after
    @+193498 [193498] lavendel   q6  ? after
    @+196514 [196514] les        q7  ? after
    @+198118 [198118] lichaam    q8  ? after
    @+198928 [198928] liefde     q9  ? after
    @+199287 [199287] lieveling  q10 ? after
    @+199534 [199534] lig        q11 ? after
    @+199668 [199668] lijf       q12 ? it
    @+199668 [199668] lijf       done. it
    @+199833 [199833] lijm       q0  ? b
    @+199833 [199833] lijm       q1  ? before

# alphaguess.com 🧩 #899 🥳 13 ⏱️ 0:00:42.850556

🤔 13 attempts
📜 1 sessions

    @        [     0] aa            
    @+1      [     1] aah           
    @+2      [     2] aahed         
    @+3      [     3] aahing        
    @+98220  [ 98220] mach          q0  ? after
    @+147373 [147373] rhotic        q1  ? after
    @+147430 [147430] rib           q10 ? after
    @+147478 [147478] ribonucleases q11 ? after
    @+147496 [147496] rice          q12 ? it
    @+147496 [147496] rice          done. it
    @+147526 [147526] rick          q9  ? before
    @+147699 [147699] right         q8  ? before
    @+148084 [148084] river         q7  ? before
    @+148810 [148810] rot           q6  ? before
    @+150344 [150344] sallow        q5  ? before
    @+153322 [153322] sea           q4  ? before
    @+159490 [159490] slop          q3  ? before
    @+171643 [171643] ta            q2  ? before

# dontwordle.com 🧩 #1326 🥳 6 ⏱️ 0:02:14.880938

📜 1 sessions
💰 score: 12

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:7419
    ⬜⬜⬜⬜⬜ tried:PUPUS n n n n n remain:2497
    ⬜⬜⬜⬜⬜ tried:LIMBI n n n n n remain:721
    ⬜⬜⬜⬜⬜ tried:CRWTH n n n n n remain:101
    ⬜🟨⬜🟨⬜ tried:DOXED n m n m n remain:6
    ⬜🟨🟨⬜⬜ tried:FEOFF n m m n n remain:2

    Undos used: 3

      2 words remaining
    x 6 unused letters
    = 12 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1469 😦 20 ⏱️ 0:04:01.785935

📜 1 sessions
💰 score: 4680

    6/6
    LASER ⬜⬜⬜⬜⬜
    UNCOY 🟨🟨🟨⬜⬜
    PUNCH ⬜🟩🟩🟩🟩
    BUNCH ⬜🟩🟩🟩🟩
    HUNCH ⬜🟩🟩🟩🟩
    MUNCH 🟩🟩🟩🟩🟩
    3/6
    MUNCH ⬜⬜🟩🟩⬜
    ZINCY ⬜🟩🟩🟩⬜
    SINCE 🟩🟩🟩🟩🟩
    4/6
    SINCE 🟨⬜⬜⬜⬜
    TORAS ⬜⬜🟨🟨🟨
    GRASP ⬜🟩🟩🟩⬜
    BRASH 🟩🟩🟩🟩🟩
    5/6
    BRASH ⬜⬜🟨⬜⬜
    LADEN ⬜🟨⬜⬜🟨
    ACING 🟨⬜⬜🟨⬜
    UNJAM 🟨🟨🟨🟨⬜
    JUNTA 🟩🟩🟩🟩🟩
    Final 2/2
    PEDRO 🟩🟨⬜🟨🟨
    POWER 🟩🟩⬜🟩🟩
    FAIL: POKER

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1446 🥳 score:18 ⏱️ 0:01:20.078266

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. CRAFT attempts:6 score:6
2. DECAL attempts:3 score:3
3. DWELT attempts:4 score:4
4. TRADE attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1446 🥳 score:51 ⏱️ 0:03:41.257300

📜 1 sessions

Octordle Classic

1. LATER attempts:4 score:4
2. OTHER attempts:7 score:7
3. WHERE attempts:10 score:10
4. BERRY attempts:9 score:9
5. LADEN attempts:5 score:5
6. LARGE attempts:2 score:2
7. THIGH attempts:6 score:6
8. DEBAR attempts:8 score:8

# squareword.org 🧩 #1439 🥳 7 ⏱️ 0:01:52.492816

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟩 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    R E L I C
    O X I D E
    U T T E R
    G R E A T
    E A R L S

# cemantle.certitudes.org 🧩 #1376 🥳 71 ⏱️ 0:01:00.777655

🤔 72 attempts
📜 2 sessions
🫧 1 chat sessions
⁉️ 8 chat prompts
🤖 8 dolphin3:latest replies
🥵  4 😎 10 🥶 54 🧊  3

     $1 #72  ~1 accessory     100.00°C 🥳 1000‰
     $2 #34  ~8 corded         36.83°C 🥵  971‰
     $3 #27  ~9 device         36.55°C 🥵  969‰
     $4 #40  ~6 handset        36.19°C 🥵  963‰
     $5 #17 ~12 cord           34.09°C 🥵  933‰
     $6 #53  ~4 antenna        32.13°C 😎  888‰
     $7 #50  ~5 portable       31.19°C 😎  862‰
     $8 #25 ~10 cords          30.92°C 😎  848‰
     $9 #36  ~7 devices        29.67°C 😎  804‰
    $10 #56  ~3 console        27.84°C 😎  684‰
    $11 #61  ~2 laptop         27.76°C 😎  679‰
    $12 #24 ~11 concealment    24.94°C 😎  369‰
    $16 #37     dock           22.17°C 🥶
    $70 #10     mountain       -1.55°C 🧊

# cemantix.certitudes.org 🧩 #1409 🥳 416 ⏱️ 0:09:16.537568

🤔 417 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 62 chat prompts
🤖 62 dolphin3:latest replies
🔥   2 🥵  15 😎  60 🥶 261 🧊  78

      $1 #417   ~1 probable           100.00°C 🥳 1000‰
      $2 #348  ~19 hypothèse           54.72°C 🔥  994‰
      $3 #398   ~6 prévisible          49.57°C 🔥  990‰
      $4 #366  ~14 évident             46.87°C 🥵  987‰
      $5 #330  ~27 probabilité         44.60°C 🥵  980‰
      $6 #352  ~18 supposition         44.19°C 🥵  977‰
      $7  #93  ~66 effet               43.50°C 🥵  975‰
      $8 #391   ~7 certitude           43.14°C 🥵  971‰
      $9 #139  ~51 certain             42.44°C 🥵  965‰
     $10  #94  ~65 conséquence         42.24°C 🥵  964‰
     $11 #328  ~28 incertitude         40.97°C 🥵  953‰
     $19 #224  ~42 faible              36.58°C 😎  892‰
     $79 #259      circonstanciel      23.64°C 🥶
    $340 #115      développement       -0.08°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #60 🥳 score:25 ⏱️ 0:01:25.898903

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. SKUNK attempts:6 score:6
2. POSIT attempts:4 score:4
3. BENCH attempts:7 score:7
4. CHILD attempts:8 score:8

# [Quordle Sequence](m-w.com/games/quordle/#/sequence) 🧩 #1446 🥳 score:25 ⏱️ 0:01:29.188679

📜 1 sessions

Quordle Sequence m-w.com/games/quordle/

1. SPELL attempts:4 score:4
2. SLIMY attempts:6 score:6
3. SERVE attempts:7 score:7
4. BLIMP attempts:8 score:8

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1446 🥳 score:8 ⏱️ 0:04:29.220331

📜 2 sessions

Octordle Rescue

1. DRAPE attempts:5 score:5
2. CRACK attempts:13 score:13
3. IDLER attempts:7 score:7
4. LURID attempts:6 score:6
5. EXALT attempts:8 score:8
6. OUTER attempts:9 score:9
7. DREAD attempts:10 score:10
8. COYLY attempts:11 score:11

# [Octordle Sequence](britannica.com/games/octordle/daily-sequence) 🧩 #1446 🥳 score:60 ⏱️ 0:03:15.568408

📜 3 sessions

Octordle Sequence

1. QUACK attempts:4 score:4
2. THINK attempts:5 score:5
3. REUSE attempts:6 score:6
4. STONY attempts:7 score:7
5. WORSE attempts:8 score:8
6. DRANK attempts:9 score:9
7. DOWDY attempts:10 score:10
8. ENEMY attempts:11 score:11
