# 2026-04-05

- 🔗 spaceword.org 🧩 2026-04-04 🏁 score 2173 ranked 1.6% 5/321 ⏱️ 1:41:57.639149
- 🔗 alfagok.diginaut.net 🧩 #519 🥳 24 ⏱️ 0:00:38.015853
- 🔗 alphaguess.com 🧩 #986 🥳 26 ⏱️ 0:00:46.711720
- 🔗 dontwordle.com 🧩 #1412 😳 6 ⏱️ 0:01:46.656035
- 🔗 dictionary.com hurdle 🧩 #1555 🥳 17 ⏱️ 0:03:59.865342
- 🔗 Quordle Classic 🧩 #1532 🥳 score:20 ⏱️ 0:01:04.175938
- 🔗 Octordle Classic 🧩 #1532 🥳 score:65 ⏱️ 0:05:10.486935
- 🔗 squareword.org 🧩 #1525 🥳 7 ⏱️ 0:01:58.768933
- 🔗 cemantle.certitudes.org 🧩 #1462 🥳 70 ⏱️ 0:00:44.841326
- 🔗 cemantix.certitudes.org 🧩 #1495 🥳 900 ⏱️ 5:08:21.275953

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



































# [spaceword.org](spaceword.org) 🧩 2026-04-04 🏁 score 2173 ranked 1.6% 5/321 ⏱️ 1:41:57.639149

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 5/321

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ D O C _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ _ L A V _ _ _   
      _ _ _ _ _ Q I _ _ _   
      _ _ _ _ F U N _ _ _   
      _ _ _ _ _ A E _ _ _   
      _ _ _ _ _ F _ _ _ _   
      _ _ _ _ Z I T _ _ _   
      _ _ _ _ A T E _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #519 🥳 24 ⏱️ 0:00:38.015853

🤔 24 attempts
📜 1 sessions

    @        [     0] &-teken         
    @+1      [     1] &-tekens        
    @+2      [     2] -cijferig       
    @+3      [     3] -e-mail         
    @+99733  [ 99733] ex              q2  ? ␅
    @+99733  [ 99733] ex              q3  ? a'
    @+99733  [ 99733] ex              q4  ? ␅
    @+99733  [ 99733] ex              q5  ? after
    @+111388 [111388] ge              q8  ? ␅
    @+111388 [111388] ge              q9  ? after
    @+120898 [120898] gequadrilleerde q12 ? ␅
    @+120898 [120898] gequadrilleerde q13 ? after
    @+125653 [125653] gezeglijk       q14 ? ␅
    @+125653 [125653] gezeglijk       q15 ? after
    @+128023 [128023] glazen          q16 ? ␅
    @+128023 [128023] glazen          q17 ? after
    @+128606 [128606] godsdienst      q20 ? ␅
    @+128606 [128606] godsdienst      q21 ? after
    @+128843 [128843] goederen        q22 ? ␅
    @+128843 [128843] goederen        q23 ? it
    @+128843 [128843] goederen        done. it
    @+129198 [129198] gok             q18 ? ␅
    @+129198 [129198] gok             q19 ? before
    @+130408 [130408] gracieust       q10 ? ␅
    @+130408 [130408] gracieust       q11 ? before
    @+149427 [149427] huis            q6  ? ␅
    @+149427 [149427] huis            q7  ? before
    @+199805 [199805] lijm            q0  ? ␅
    @+199805 [199805] lijm            q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #986 🥳 26 ⏱️ 0:00:46.711720

🤔 26 attempts
📜 1 sessions

    @       [    0] aa      
    @+1     [    1] aah     
    @+2     [    2] aahed   
    @+3     [    3] aahing  
    @+47380 [47380] dis     q2  ? ␅
    @+47380 [47380] dis     q3  ? after
    @+72798 [72798] gremmy  q4  ? ␅
    @+72798 [72798] gremmy  q5  ? after
    @+85502 [85502] ins     q6  ? ␅
    @+85502 [85502] ins     q7  ? after
    @+91846 [91846] knot    q8  ? ␅
    @+91846 [91846] knot    q9  ? after
    @+94943 [94943] lib     q10 ? ␅
    @+94943 [94943] lib     q11 ? after
    @+95573 [95573] lin     q14 ? ␅
    @+95573 [95573] lin     q15 ? after
    @+95807 [95807] lion    q18 ? ␅
    @+95807 [95807] lion    q19 ? after
    @+95934 [95934] liqueur q20 ? ␅
    @+95934 [95934] liqueur q21 ? after
    @+95993 [95993] lisp    q22 ? ␅
    @+95993 [95993] lisp    q23 ? after
    @+96009 [96009] list    q24 ? ␅
    @+96009 [96009] list    q25 ? it
    @+96009 [96009] list    done. it
    @+96060 [96060] literal q16 ? ␅
    @+96060 [96060] literal q17 ? before
    @+96576 [96576] locks   q12 ? ␅
    @+96576 [96576] locks   q13 ? before
    @+98216 [98216] mach    q0  ? ␅
    @+98216 [98216] mach    q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1412 😳 6 ⏱️ 0:01:46.656035

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:PUPUS n n n n n remain:4885
    ⬜⬜⬜⬜⬜ tried:EDGED n n n n n remain:1553
    ⬜⬜⬜⬜⬜ tried:ICTIC n n n n n remain:436
    ⬜⬜⬜🟩⬜ tried:MYRRH n n n Y n remain:11
    🟩🟩🟩🟩🟩 tried:FLORA Y Y Y Y Y remain:0
    ⬛⬛⬛⬛⬛ tried:????? remain:0

    Undos used: 4

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1555 🥳 17 ⏱️ 0:03:59.865342

📜 1 sessions
💰 score: 9900

    3/6
    ALOES ⬜⬜🟩⬜🟨
    PORTS 🟨🟨⬜🟨🟨
    SPOUT 🟩🟩🟩🟩🟩
    5/6
    SPOUT ⬜⬜⬜🟨⬜
    GUARD 🟨🟩⬜⬜⬜
    FUGLY ⬜🟩🟨🟨⬜
    BULGE ⬜🟩🟨🟩🟩
    LUNGE 🟩🟩🟩🟩🟩
    5/6
    LUNGE 🟨⬜⬜⬜🟩
    STALE ⬜⬜🟩🟨🟩
    BLADE ⬜🟩🟩⬜🟩
    FLAKE 🟩🟩🟩⬜🟩
    FLAME 🟩🟩🟩🟩🟩
    3/6
    FLAME ⬜⬜🟩⬜⬜
    BRATS ⬜🟩🟩⬜🟨
    CRASH 🟩🟩🟩🟩🟩
    Final 1/2
    SHINE 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1532 🥳 score:20 ⏱️ 0:01:04.175938

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. PLUSH attempts:3 score:3
2. GRATE attempts:6 score:6
3. DEALT attempts:4 score:4
4. LABEL attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1532 🥳 score:65 ⏱️ 0:05:10.486935

📜 2 sessions

Octordle Classic

1. CREAM attempts:6 score:6
2. FILER attempts:8 score:8
3. FAUNA attempts:9 score:9
4. VIVID attempts:4 score:4
5. CLUCK attempts:10 score:10
6. DRIVE attempts:5 score:5
7. ENNUI attempts:11 score:11
8. CANON attempts:12 score:12

# [squareword.org](squareword.org) 🧩 #1525 🥳 7 ⏱️ 0:01:58.768933

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S M A R T
    L E V E R
    A L I B I
    B E A U T
    S E N S E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1462 🥳 70 ⏱️ 0:00:44.841326

🤔 71 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 14 chat prompts
🤖 14 dolphin3:latest replies
🥵  2 😎  7 🥶 57 🧊  4

     $1 #71 auction        100.00°C 🥳 1000‰ ~67 used:0  [66]  source:dolphin3
     $2 #15 art             27.29°C 🥵  915‰  ~6 used:12 [5]   source:dolphin3
     $3 #46 painting        26.89°C 🥵  907‰  ~1 used:7  [0]   source:dolphin3
     $4 #45 museum          25.69°C 😎  890‰  ~7 used:2  [6]   source:dolphin3
     $5 #70 watercolor      22.35°C 😎  773‰  ~2 used:0  [1]   source:dolphin3
     $6 #56 gallery         22.14°C 😎  759‰  ~3 used:0  [2]   source:dolphin3
     $7 #38 presentation    22.02°C 😎  750‰  ~8 used:2  [7]   source:dolphin3
     $8 #23 craftsmanship   18.67°C 😎  410‰  ~9 used:5  [8]   source:dolphin3
     $9 #39 appeal          18.16°C 😎  324‰  ~4 used:1  [3]   source:dolphin3
    $10 #68 portrait        16.49°C 😎    1‰  ~5 used:0  [4]   source:dolphin3
    $11 #47 sculpture       16.32°C 🥶       ~14 used:0  [13]  source:dolphin3
    $12 #61 acrylic         15.94°C 🥶       ~15 used:0  [14]  source:dolphin3
    $13  #1 bonsai          13.87°C 🥶       ~10 used:8  [9]   source:dolphin3
    $68 #35 freshness       -0.70°C 🧊       ~68 used:0  [67]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1495 🥳 900 ⏱️ 5:08:21.275953

🤔 901 attempts
📜 1 sessions
🫧 147 chat sessions
⁉️ 428 chat prompts
🤖 101 gemma3:27b replies
🤖 174 dolphin3:latest replies
🤖 6 llama3.1:8b replies
🤖 97 nemotron-cascade-2:latest replies
🤖 12 gemma4:26b replies
🤖 38 gemma4:latest replies
😱   1 🔥   5 🥵  39 😎 160 🥶 609 🧊  86

      $1 #901 gosse           100.00°C 🥳 1000‰ ~815 used:0   [814]  source:gemma3       
      $2 #871 gamin            78.39°C 😱  999‰   ~1 used:5   [0]    source:gemma3       
      $3 #845 morveux          53.37°C 🔥  997‰   ~6 used:11  [5]    source:gemma3       
      $4 #199 foutre           53.21°C 🔥  996‰ ~202 used:370 [201]  source:dolphin3     
      $5 #120 putain           53.07°C 🔥  995‰ ~200 used:177 [199]  source:dolphin3     
      $6 #119 merde            51.95°C 🔥  993‰  ~43 used:93  [42]   source:dolphin3     
      $7 #352 fou              50.01°C 🔥  990‰  ~26 used:71  [25]   source:nemotron     
      $8 #346 connard          49.94°C 🥵  989‰  ~27 used:8   [26]   source:nemotron     
      $9 #693 chialer          49.91°C 🥵  988‰  ~28 used:8   [27]   source:gemma3       
     $10 #819 mec              49.85°C 🥵  987‰   ~7 used:4   [6]    source:gemma3       
     $11 #567 crever           49.70°C 🥵  986‰  ~29 used:8   [28]   source:gemma3       
     $48 #731 trimer           42.13°C 😎  896‰  ~44 used:0   [43]   source:gemma3       
    $207 #307 réprimander      31.62°C 🥶       ~206 used:0   [205]  source:nemotron     
    $816 #161 tranche          -0.11°C 🧊       ~816 used:0   [815]  source:dolphin3     
