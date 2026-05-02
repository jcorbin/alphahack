# 2026-05-03

- 🔗 spaceword.org 🧩 2026-05-02 🏁 score 2173 ranked 5.5% 18/325 ⏱️ 1:42:56.848002
- 🔗 alfagok.diginaut.net 🧩 #547 🥳 32 ⏱️ 0:00:31.078454
- 🔗 alphaguess.com 🧩 #1014 🥳 22 ⏱️ 0:00:29.666617
- 🔗 dontwordle.com 🧩 #1440 🥳 6 ⏱️ 0:02:09.795133
- 🔗 dictionary.com hurdle 🧩 #1583 🥳 18 ⏱️ 0:05:26.122866
- 🔗 Quordle Classic 🧩 #1560 🥳 score:25 ⏱️ 0:01:24.944246
- 🔗 Octordle Classic 🧩 #1560 🥳 score:57 ⏱️ 0:03:16.321222
- 🔗 squareword.org 🧩 #1553 🥳 8 ⏱️ 0:03:24.705262
- 🔗 cemantle.certitudes.org 🧩 #1490 🥳 233 ⏱️ 0:03:13.563394
- 🔗 cemantix.certitudes.org 🧩 #1523 🥳 76 ⏱️ 0:02:55.996789

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































































# [spaceword.org](spaceword.org) 🧩 2026-05-02 🏁 score 2173 ranked 5.5% 18/325 ⏱️ 1:42:56.848002

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 18/325

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ Z A P _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ _ E _ L _ _ _   
      _ _ _ _ S H E _ _ _   
      _ _ _ _ Q _ A _ _ _   
      _ _ _ _ U _ X _ _ _   
      _ _ _ _ I F _ _ _ _   
      _ _ _ _ R I N _ _ _   
      _ _ _ _ E R E _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #547 🥳 32 ⏱️ 0:00:31.078454

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+199704 [199704] lijk       q0  ? ␅
    @+199704 [199704] lijk       q1  ? after
    @+299460 [299460] schro      q2  ? ␅
    @+299460 [299460] schro      q3  ? after
    @+349441 [349441] vakantie   q4  ? ␅
    @+349441 [349441] vakantie   q5  ? after
    @+374181 [374181] vrij       q6  ? ␅
    @+374181 [374181] vrij       q7  ? after
    @+375626 [375626] vuur       q14 ? ␅
    @+375626 [375626] vuur       q15 ? after
    @+376020 [376020] waak       q18 ? ␅
    @+376020 [376020] waak       q19 ? after
    @+376217 [376217] waardering q20 ? ␅
    @+376217 [376217] waardering q21 ? after
    @+376317 [376317] waardin    q22 ? ␅
    @+376317 [376317] waardin    q23 ? after
    @+376370 [376370] waarlijk   q24 ? ␅
    @+376370 [376370] waarlijk   q25 ? after
    @+376392 [376392] waarna     q26 ? ␅
    @+376392 [376392] waarna     q27 ? after
    @+376398 [376398] waarneem   q28 ? ␅
    @+376398 [376398] waarneem   q29 ? after
    @+376409 [376409] waarnemen  q30 ? ␅
    @+376409 [376409] waarnemen  q31 ? it
    @+376409 [376409] waarnemen  done. it
    @+376422 [376422] waarneming q16 ? ␅
    @+376422 [376422] waarneming q17 ? before
    @+377244 [377244] wandel     q12 ? ␅
    @+377244 [377244] wandel     q13 ? before
    @+380393 [380393] weer       q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1014 🥳 22 ⏱️ 0:00:29.666617

🤔 22 attempts
📜 2 sessions

    @        [     0] aa       
    @+1      [     1] aah      
    @+2      [     2] aahed    
    @+3      [     3] aahing   
    @+98216  [ 98216] mach     q0  ? ␅
    @+98216  [ 98216] mach     q1  ? after
    @+147366 [147366] rhotic   q2  ? ␅
    @+147366 [147366] rhotic   q3  ? after
    @+159483 [159483] slop     q6  ? ␅
    @+159483 [159483] slop     q7  ? after
    @+165525 [165525] stick    q8  ? ␅
    @+165525 [165525] stick    q9  ? after
    @+166284 [166284] straddle q16 ? ␅
    @+166284 [166284] straddle q17 ? after
    @+166660 [166660] stria    q18 ? ␅
    @+166660 [166660] stria    q19 ? after
    @+166846 [166846] strong   q20 ? ␅
    @+166846 [166846] strong   q21 ? it
    @+166846 [166846] strong   done. it
    @+167044 [167044] stuff    q14 ? ␅
    @+167044 [167044] stuff    q15 ? before
    @+168577 [168577] sue      q10 ? ␅
    @+168577 [168577] sue      q11 ? vb
    @+168577 [168577] sue      q12 ? ␅
    @+168577 [168577] sue      q13 ? before
    @+171636 [171636] ta       q4  ? ␅
    @+171636 [171636] ta       q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1440 🥳 6 ⏱️ 0:02:09.795133

📜 2 sessions
💰 score: 28

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:7600
    ⬜⬜⬜⬜⬜ tried:JOOKS n n n n n remain:2071
    ⬜⬜⬜⬜⬜ tried:GUNGY n n n n n remain:641
    ⬜🟨⬜⬜⬜ tried:MAMMA n m n n n remain:148
    ⬜🟨🟨⬜⬜ tried:BLAFF n m m n n remain:16
    ⬜🟩🟨🟩⬜ tried:RELAX n Y m Y n remain:4

    Undos used: 3

      4 words remaining
    x 7 unused letters
    = 28 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1583 🥳 18 ⏱️ 0:05:26.122866

📜 1 sessions
💰 score: 9800

    4/6
    PEARS ⬜🟨🟩🟨⬜
    CRATE 🟨🟩🟩⬜🟩
    BRACE ⬜🟩🟩🟩🟩
    GRACE 🟩🟩🟩🟩🟩
    5/6
    GRACE ⬜🟨⬜⬜🟨
    SORED ⬜⬜🟨🟩⬜
    VILER ⬜⬜⬜🟩🟩
    MUTER ⬜⬜🟨🟩🟩
    ETHER 🟩🟩🟩🟩🟩
    3/6
    ETHER ⬜🟨⬜⬜🟨
    ROAST 🟨🟩⬜🟩🟨
    TORSO 🟩🟩🟩🟩🟩
    4/6
    TORSO ⬜⬜⬜⬜⬜
    ELAND 🟨🟩⬜⬜⬜
    PLUME 🟨🟩⬜⬜🟨
    BLEEP 🟩🟩🟩🟩🟩
    Final 2/2
    YOUTH ⬜🟩🟩🟩🟩
    MOUTH 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1560 🥳 score:25 ⏱️ 0:01:24.944246

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. HATER attempts:5 score:5
2. FORCE attempts:7 score:7
3. BASTE attempts:4 score:4
4. TROUT attempts:9 score:9

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1560 🥳 score:57 ⏱️ 0:03:16.321222

📜 1 sessions

Octordle Classic

1. BLANK attempts:10 score:10
2. TWEED attempts:11 score:11
3. CHOKE attempts:4 score:4
4. RETCH attempts:9 score:9
5. GECKO attempts:5 score:5
6. SNACK attempts:3 score:3
7. REBEL attempts:8 score:8
8. CHAIN attempts:7 score:7

# [squareword.org](squareword.org) 🧩 #1553 🥳 8 ⏱️ 0:03:24.705262

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟨 🟨 🟨 🟨 🟨
    🟨 🟩 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S M A S H
    P A S T E
    I N T E R
    K N E A D
    Y A R D S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1490 🥳 233 ⏱️ 0:03:13.563394

🤔 234 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 56 chat prompts
🤖 56 dolphin3:latest replies
🔥   4 🥵   8 😎  47 🥶 158 🧊  16

      $1 #234 appoint         100.00°C 🥳 1000‰ ~218 used:0  [217]  source:dolphin3
      $2 #230 nominate         63.88°C 🔥  998‰   ~1 used:4  [0]    source:dolphin3
      $3 #113 appointment      59.15°C 🔥  997‰  ~12 used:43 [11]   source:dolphin3
      $4  #60 appointee        54.93°C 🔥  995‰   ~7 used:36 [6]    source:dolphin3
      $5  #80 designate        53.39°C 🔥  992‰   ~6 used:31 [5]    source:dolphin3
      $6 #145 assign           45.44°C 🥵  980‰   ~8 used:4  [7]    source:dolphin3
      $7 #218 relinquish       42.65°C 🥵  969‰   ~4 used:3  [3]    source:dolphin3
      $8  #75 successor        41.56°C 🥵  961‰   ~9 used:4  [8]    source:dolphin3
      $9 #136 vacancy          41.26°C 🥵  959‰  ~10 used:4  [9]    source:dolphin3
     $10 #233 endorse          41.02°C 🥵  956‰   ~2 used:1  [1]    source:dolphin3
     $11 #166 resignation      40.36°C 🥵  947‰   ~5 used:3  [4]    source:dolphin3
     $14 #183 recruit          35.93°C 😎  893‰  ~13 used:0  [12]   source:dolphin3
     $61 #121 role             22.93°C 🥶        ~65 used:0  [64]   source:dolphin3
    $219  #23 backpack         -0.07°C 🧊       ~219 used:0  [218]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1523 🥳 76 ⏱️ 0:02:55.996789

🤔 77 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 23 chat prompts
🤖 23 dolphin3:latest replies
🔥  1 🥵  8 😎 17 🥶 46 🧊  4

     $1 #77 indifférence     100.00°C 🥳 1000‰ ~73 used:0  [72]  source:dolphin3
     $2 #75 dégoût            50.72°C 🔥  990‰  ~1 used:0  [0]   source:dolphin3
     $3 #52 sentiment         49.96°C 🥵  987‰ ~23 used:14 [22]  source:dolphin3
     $4 #53 souffrance        49.73°C 🥵  986‰  ~8 used:9  [7]   source:dolphin3
     $5 #72 apathie           48.18°C 🥵  979‰  ~2 used:1  [1]   source:dolphin3
     $6 #76 désintérêt        47.68°C 🥵  976‰  ~3 used:0  [2]   source:dolphin3
     $7 #51 désarroi          46.22°C 🥵  963‰  ~6 used:8  [5]   source:dolphin3
     $8 #60 misère            45.56°C 🥵  955‰  ~4 used:5  [3]   source:dolphin3
     $9 #26 tristesse         42.07°C 🥵  908‰  ~7 used:8  [6]   source:dolphin3
    $10 #40 peur              42.06°C 🥵  907‰  ~5 used:6  [4]   source:dolphin3
    $11 #27 détresse          39.59°C 😎  845‰  ~9 used:0  [8]   source:dolphin3
    $12 #20 sentimentalité    39.36°C 😎  837‰ ~25 used:5  [24]  source:dolphin3
    $28 #34 regret            30.23°C 🥶       ~27 used:0  [26]  source:dolphin3
    $74  #5 lave              -0.80°C 🧊       ~74 used:0  [73]  source:dolphin3
