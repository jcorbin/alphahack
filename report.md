# 2026-02-03

- 🔗 spaceword.org 🧩 2026-02-02 🏁 score 2173 ranked 4.5% 16/352 ⏱️ 0:38:59.356595
- 🔗 alfagok.diginaut.net 🧩 #458 🥳 44 ⏱️ 0:00:55.247641
- 🔗 alphaguess.com 🧩 #925 🥳 22 ⏱️ 0:00:27.135565
- 🔗 dontwordle.com 🧩 #1351 🥳 6 ⏱️ 0:02:09.144574
- 🔗 dictionary.com hurdle 🧩 #1494 🥳 16 ⏱️ 0:03:06.265011
- 🔗 Quordle Classic 🧩 #1471 🥳 score:28 ⏱️ 0:02:17.928820
- 🔗 Octordle Classic 🧩 #1471 🥳 score:52 ⏱️ 0:03:02.056951
- 🔗 squareword.org 🧩 #1464 🥳 6 ⏱️ 0:01:20.687891
- 🔗 cemantle.certitudes.org 🧩 #1401 🥳 526 ⏱️ 0:13:28.829981
- 🔗 cemantix.certitudes.org 🧩 #1434 🥳 129 ⏱️ 0:04:15.226562
- 🔗 Quordle Rescue 🧩 #85 🥳 score:24 ⏱️ 0:02:14.792376
- 🔗 Octordle Rescue 🧩 #1471 😦 score:7 ⏱️ 0:04:45.522330

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



















# [spaceword.org](spaceword.org) 🧩 2026-02-02 🏁 score 2173 ranked 4.5% 16/352 ⏱️ 0:38:59.356595

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 16/352

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ I C E _ _ _   
      _ _ _ _ _ _ Q _ _ _   
      _ _ _ _ E A U _ _ _   
      _ _ _ _ _ G I _ _ _   
      _ _ _ _ B I T _ _ _   
      _ _ _ _ _ T E _ _ _   
      _ _ _ _ Z A S _ _ _   
      _ _ _ _ _ T _ _ _ _   
      _ _ _ _ S E V _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #458 🥳 44 ⏱️ 0:00:55.247641

🤔 44 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+24910  [ 24910] bad         q6  ? ␅
    @+24910  [ 24910] bad         q7  ? after
    @+31127  [ 31127] begeleid    q10 ? ␅
    @+31127  [ 31127] begeleid    q11 ? after
    @+34010  [ 34010] beleid      q12 ? ␅
    @+34010  [ 34010] beleid      q13 ? after
    @+34415  [ 34415] belemmer    q18 ? ␅
    @+34415  [ 34415] belemmer    q19 ? after
    @+34622  [ 34622] belkaart    q34 ? ␅
    @+34622  [ 34622] belkaart    q35 ? after
    @+34638  [ 34638] belle       q38 ? ␅
    @+34638  [ 34638] belle       q39 ? after
    @+34651  [ 34651] bellen      q42 ? ␅
    @+34651  [ 34651] bellen      q43 ? it
    @+34651  [ 34651] bellen      done. it
    @+34677  [ 34677] bellettrist q40 ? ␅
    @+34677  [ 34677] bellettrist q41 ? before
    @+34722  [ 34722] belommering q36 ? ␅
    @+34722  [ 34722] belommering q37 ? before
    @+34821  [ 34821] belucht     q16 ? ␅
    @+34821  [ 34821] belucht     q17 ? before
    @+35654  [ 35654] beoordeling q14 ? ␅
    @+35654  [ 35654] beoordeling q15 ? before
    @+37357  [ 37357] bescherm    q8  ? ␅
    @+37357  [ 37357] bescherm    q9  ? before
    @+49842  [ 49842] boks        q4  ? ␅
    @+49842  [ 49842] boks        q5  ? before
    @+99751  [ 99751] ex          q2  ? ␅
    @+99751  [ 99751] ex          q3  ? before
    @+199826 [199826] lijm        q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #925 🥳 22 ⏱️ 0:00:27.135565

🤔 22 attempts
📜 1 sessions

    @       [    0] aa     
    @+1     [    1] aah    
    @+2     [    2] aahed  
    @+3     [    3] aahing 
    @+5876  [ 5876] angel  q8  ? ␅
    @+5876  [ 5876] angel  q9  ? after
    @+8323  [ 8323] ar     q10 ? ␅
    @+8323  [ 8323] ar     q11 ? after
    @+8824  [ 8824] arid   q14 ? ␅
    @+8824  [ 8824] arid   q15 ? after
    @+9069  [ 9069] arrest q16 ? ␅
    @+9069  [ 9069] arrest q17 ? after
    @+9121  [ 9121] arrow  q20 ? ␅
    @+9121  [ 9121] arrow  q21 ? it
    @+9121  [ 9121] arrow  done. it
    @+9175  [ 9175] art    q18 ? ␅
    @+9175  [ 9175] art    q19 ? before
    @+9341  [ 9341] as     q12 ? ␅
    @+9341  [ 9341] as     q13 ? before
    @+11764 [11764] back   q6  ? ␅
    @+11764 [11764] back   q7  ? before
    @+23683 [23683] camp   q4  ? ␅
    @+23683 [23683] camp   q5  ? before
    @+47382 [47382] dis    q2  ? ␅
    @+47382 [47382] dis    q3  ? before
    @+98220 [98220] mach   q0  ? ␅
    @+98220 [98220] mach   q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1351 🥳 6 ⏱️ 0:02:09.144574

📜 1 sessions
💰 score: 30

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:8089
    ⬜⬜⬜⬜⬜ tried:PZAZZ n n n n n remain:3794
    ⬜⬜⬜⬜⬜ tried:WOOFS n n n n n remain:758
    ⬜⬜⬜⬜⬜ tried:JINNI n n n n n remain:230
    ⬜⬜⬜⬜⬜ tried:CHUCK n n n n n remain:60
    🟩⬜⬜🟩⬜ tried:EDGED Y n n Y n remain:5

    Undos used: 4

      5 words remaining
    x 6 unused letters
    = 30 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1494 🥳 16 ⏱️ 0:03:06.265011

📜 1 sessions
💰 score: 10000

    4/6
    URSAE 🟨⬜⬜⬜⬜
    YOUTH ⬜🟨🟨⬜⬜
    ONIUM 🟨⬜⬜🟨🟨
    JUMBO 🟩🟩🟩🟩🟩
    3/6
    JUMBO ⬜🟨⬜⬜⬜
    ULNAS 🟩⬜⬜🟨🟨
    USAGE 🟩🟩🟩🟩🟩
    4/6
    USAGE ⬜⬜🟨⬜⬜
    TONAL ⬜⬜⬜🟩⬜
    JIHAD ⬜⬜⬜🟩🟩
    DRYAD 🟩🟩🟩🟩🟩
    4/6
    DRYAD ⬜🟨🟨⬜⬜
    RUSTY 🟨⬜⬜⬜🟨
    PYRIC ⬜🟩🟩⬜⬜
    MYRRH 🟩🟩🟩🟩🟩
    Final 1/2
    LOYAL 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1471 🥳 score:28 ⏱️ 0:02:17.928820

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. BOUND attempts:8 score:8
2. ADORE attempts:5 score:5
3. PINKY attempts:7 score:9
4. FLYER attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1471 🥳 score:52 ⏱️ 0:03:02.056951

📜 1 sessions

Octordle Classic

1. GUIDE attempts:3 score:3
2. SHARK attempts:7 score:7
3. COUNT attempts:4 score:4
4. QUACK attempts:6 score:6
5. MANIA attempts:5 score:5
6. SMITE attempts:8 score:8
7. BLEAT attempts:10 score:10
8. BEARD attempts:9 score:9

# [squareword.org](squareword.org) 🧩 #1464 🥳 6 ⏱️ 0:01:20.687891

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P A S T A
    A L T A R
    S L E P T
    T O N E S
    S T O R Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1401 🥳 526 ⏱️ 0:13:28.829981

🤔 527 attempts
📜 1 sessions
🫧 23 chat sessions
⁉️ 134 chat prompts
🤖 33 hermes3:8b replies
🤖 101 dolphin3:latest replies
😱   1 🔥   6 🥵  35 😎 123 🥶 356 🧊   5

      $1 #527              sad  100.00°C 🥳 1000‰ ~522   used:0  [521] source:hermes3 
      $2 #220    heartbreaking   65.74°C 😱  999‰   ~6 used:138    [5] source:dolphin3
      $3 #192    disheartening   65.07°C 🔥  998‰  ~42  used:63   [41] source:dolphin3
      $4 #204      distressing   63.99°C 🔥  997‰  ~41  used:32   [40] source:dolphin3
      $5 #126      bittersweet   61.75°C 🔥  994‰  ~38  used:22   [37] source:dolphin3
      $6 #229           tragic   61.13°C 🔥  993‰   ~5  used:12    [4] source:dolphin3
      $7 #206        regretful   60.35°C 🔥  992‰   ~3  used:11    [2] source:dolphin3
      $8 #188      heartbroken   59.42°C 🔥  991‰   ~4  used:11    [3] source:dolphin3
      $9 #213       depressing   59.18°C 🥵  989‰   ~7   used:2    [6] source:dolphin3
     $10 #284      regrettable   58.05°C 🥵  987‰   ~8   used:2    [7] source:dolphin3
     $11 #151        sorrowful   55.68°C 🥵  982‰  ~39   used:3   [38] source:dolphin3
     $44 #144     heartrending   43.47°C 😎  899‰  ~43   used:0   [42] source:dolphin3
    $166 #231          pensive   28.93°C 🥶       ~160   used:0  [159] source:dolphin3
    $523 #240           listed   -0.29°C 🧊       ~523   used:0  [522] source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1434 🥳 129 ⏱️ 0:04:15.226562

🤔 130 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 41 chat prompts
🤖 41 dolphin3:latest replies
🔥  3 🥵 11 😎 29 🥶 76 🧊 10

      $1 #130            chaos  100.00°C 🥳 1000‰ ~120  used:0  [119] source:dolphin3
      $2 #122    apocalyptique   44.65°C 🔥  993‰   ~2  used:4    [1] source:dolphin3
      $3 #117       terrifiant   44.56°C 🔥  992‰   ~3  used:7    [2] source:dolphin3
      $4 #128       cataclysme   43.98°C 🔥  990‰   ~1  used:1    [0] source:dolphin3
      $5  #51           obscur   40.52°C 🥵  977‰  ~43 used:32   [42] source:dolphin3
      $6 #129   anéantissement   40.30°C 🥵  975‰   ~4  used:0    [3] source:dolphin3
      $7 #124         désastre   39.36°C 🥵  969‰   ~5  used:0    [4] source:dolphin3
      $8  #54           sombre   37.92°C 🥵  954‰  ~42 used:19   [41] source:dolphin3
      $9  #55        ténébreux   37.70°C 🥵  948‰  ~41 used:13   [40] source:dolphin3
     $10  #66         ténèbres   37.22°C 🥵  944‰  ~10  used:8    [9] source:dolphin3
     $11 #107  cauchemardesque   36.85°C 🥵  938‰   ~7  used:4    [6] source:dolphin3
     $16 #115           effroi   34.60°C 😎  875‰  ~12  used:0   [11] source:dolphin3
     $45  #82        illusoire   25.73°C 🥶        ~47  used:0   [46] source:dolphin3
    $121  #78            léger   -0.64°C 🧊       ~121  used:0  [120] source:dolphin3

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #85 🥳 score:24 ⏱️ 0:02:14.792376

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. KNOCK attempts:7 score:7
2. BADLY attempts:4 score:4
3. ABLED attempts:5 score:5
4. HARDY attempts:8 score:8

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1471 😦 score:7 ⏱️ 0:04:45.522330

📜 1 sessions

Octordle Rescue

1. GROVE attempts:11 score:11
2. SATYR attempts:9 score:9
3. BLUFF attempts:12 score:12
4. FIELD attempts:13 score:13
5. PO__Y -ABCDEFGHIKLMNRSTUVW attempts:13 score:-1
6. DINGY attempts:8 score:8
7. OCTET attempts:5 score:5
8. TWIRL attempts:7 score:7
