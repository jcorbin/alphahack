# 2026-03-17

- 🔗 spaceword.org 🧩 2026-03-16 🏁 score 2168 ranked 42.4% 147/347 ⏱️ 4:12:41.298952
- 🔗 alfagok.diginaut.net 🧩 #500 🥳 24 ⏱️ 0:00:28.991749
- 🔗 alphaguess.com 🧩 #967 🥳 22 ⏱️ 0:00:21.503415
- 🔗 dontwordle.com 🧩 #1393 🥳 6 ⏱️ 0:01:37.200091
- 🔗 dictionary.com hurdle 🧩 #1536 🥳 19 ⏱️ 0:02:59.920842
- 🔗 Quordle Classic 🧩 #1513 🥳 score:26 ⏱️ 0:01:24.112011
- 🔗 Octordle Classic 🧩 #1513 🥳 score:60 ⏱️ 0:03:20.449353
- 🔗 squareword.org 🧩 #1506 🥳 7 ⏱️ 0:02:45.872718
- 🔗 cemantle.certitudes.org 🧩 #1443 🥳 117 ⏱️ 0:03:02.785405
- 🔗 cemantix.certitudes.org 🧩 #1476 🥳 68 ⏱️ 0:00:32.970459

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
















# [spaceword.org](spaceword.org) 🧩 2026-03-16 🏁 score 2168 ranked 42.4% 147/347 ⏱️ 4:12:41.298952

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 147/347

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ Q _ G _ _ _   
      _ _ _ S U P E _ _ _   
      _ _ _ _ I _ N _ _ _   
      _ _ _ _ T O E _ _ _   
      _ _ _ Z E N _ _ _ _   
      _ _ _ _ _ I _ _ _ _   
      _ _ _ O X O _ _ _ _   
      _ _ _ P U N _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #500 🥳 24 ⏱️ 0:00:28.991749

🤔 24 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+1      [     1] &-tekens    
    @+2      [     2] -cijferig   
    @+3      [     3] -e-mail     
    @+199609 [199609] lij         q0  ? ␅
    @+199609 [199609] lij         q1  ? after
    @+199609 [199609] lij         q2  ? ␅
    @+199609 [199609] lij         q3  ? after
    @+199609 [199609] lij         q4  ? ␅
    @+199609 [199609] lij         q5  ? after
    @+247696 [247696] op          q8  ? ␅
    @+247696 [247696] op          q9  ? after
    @+273501 [273501] proef       q10 ? ␅
    @+273501 [273501] proef       q11 ? after
    @+276630 [276630] quarantaine q16 ? ␅
    @+276630 [276630] quarantaine q17 ? after
    @+276855 [276855] raad        q22 ? ␅
    @+276855 [276855] raad        q23 ? it
    @+276855 [276855] raad        done. it
    @+277313 [277313] rad         q20 ? ␅
    @+277313 [277313] rad         q21 ? before
    @+278111 [278111] ram         q18 ? ␅
    @+278111 [278111] ram         q19 ? before
    @+279767 [279767] rechts      q14 ? ␅
    @+279767 [279767] rechts      q15 ? before
    @+286485 [286485] rijns       q12 ? ␅
    @+286485 [286485] rijns       q13 ? before
    @+299483 [299483] schro       q6  ? ␅
    @+299483 [299483] schro       q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #967 🥳 22 ⏱️ 0:00:21.503415

🤔 22 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+23682 [23682] camp       q4  ? ␅
    @+23682 [23682] camp       q5  ? after
    @+23768 [23768] can        q16 ? ␅
    @+23768 [23768] can        q17 ? after
    @+23865 [23865] candle     q20 ? ␅
    @+23865 [23865] candle     q21 ? it
    @+23865 [23865] candle     done. it
    @+23986 [23986] cannibal   q18 ? ␅
    @+23986 [23986] cannibal   q19 ? before
    @+24228 [24228] cap        q14 ? ␅
    @+24228 [24228] cap        q15 ? before
    @+25104 [25104] carp       q12 ? ␅
    @+25104 [25104] carp       q13 ? before
    @+26635 [26635] cep        q10 ? ␅
    @+26635 [26635] cep        q11 ? before
    @+29603 [29603] circuit    q8  ? ␅
    @+29603 [29603] circuit    q9  ? before
    @+35525 [35525] convention q6  ? ␅
    @+35525 [35525] convention q7  ? before
    @+47381 [47381] dis        q2  ? ␅
    @+47381 [47381] dis        q3  ? before
    @+98217 [98217] mach       q0  ? ␅
    @+98217 [98217] mach       q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1393 🥳 6 ⏱️ 0:01:37.200091

📜 1 sessions
💰 score: 56

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:GABBA n n n n n remain:5913
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:2926
    ⬜⬜⬜⬜⬜ tried:FLUFF n n n n n remain:1423
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:471
    ⬜⬜🟩⬜⬜ tried:KOOKY n n Y n n remain:26
    ⬜⬜🟩⬜🟩 tried:EXOME n n Y n Y remain:7

    Undos used: 4

      7 words remaining
    x 8 unused letters
    = 56 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1536 🥳 19 ⏱️ 0:02:59.920842

📜 1 sessions
💰 score: 9700

    4/6
    ARLES 🟨🟨⬜⬜🟨
    ROAST 🟨⬜🟩🟨⬜
    SHARK 🟩⬜🟩🟩🟩
    SNARK 🟩🟩🟩🟩🟩
    4/6
    SNARK ⬜⬜🟨⬜🟨
    ALKIE 🟨⬜🟨⬜⬜
    KAPOW 🟨🟩⬜⬜🟨
    WACKY 🟩🟩🟩🟩🟩
    5/6
    WACKY ⬜⬜⬜⬜⬜
    OLEIN 🟨⬜⬜⬜⬜
    TOURS 🟨🟨⬜🟨⬜
    BROTH ⬜🟩🟩🟩🟩
    FROTH 🟩🟩🟩🟩🟩
    4/6
    FROTH ⬜🟨⬜⬜⬜
    EYRAS 🟨⬜🟩⬜🟨
    PURSE ⬜🟩🟩🟨🟨
    SURER 🟩🟩🟩🟩🟩
    Final 2/2
    ARMOR 🟩🟩⬜🟩🟩
    ARBOR 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1513 🥳 score:26 ⏱️ 0:01:24.112011

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. GREET attempts:5 score:5
2. BROOD attempts:6 score:6
3. GRIME attempts:5 score:8
4. SQUAT attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1513 🥳 score:60 ⏱️ 0:03:20.449353

📜 1 sessions

Octordle Classic

1. NEVER attempts:10 score:10
2. ALONG attempts:7 score:7
3. CELLO attempts:8 score:8
4. CIVIL attempts:9 score:9
5. SHORE attempts:11 score:11
6. FEAST attempts:5 score:5
7. CLEFT attempts:6 score:6
8. UNITY attempts:4 score:4

# [squareword.org](squareword.org) 🧩 #1506 🥳 7 ⏱️ 0:02:45.872718

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟨 🟩
    🟨 🟨 🟩 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C H E E P
    L A R V A
    A P R O N
    S P O K E
    P Y R E S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1443 🥳 117 ⏱️ 0:03:02.785405

🤔 118 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 40 chat prompts
🤖 40 dolphin3:latest replies
😱  1 🔥  1 🥵  4 😎 27 🥶 81 🧊  3

      $1 #118 manipulate      100.00°C 🥳 1000‰ ~115 used:0  [114]  source:dolphin3
      $2  #43 manipulation     65.00°C 😱  999‰   ~1 used:58 [0]    source:dolphin3
      $3 #111 coerce           51.53°C 🔥  993‰   ~2 used:7  [1]    source:dolphin3
      $4  #87 manipulative     49.82°C 🥵  987‰  ~30 used:18 [29]   source:dolphin3
      $5 #114 exploit          46.29°C 🥵  964‰   ~3 used:1  [2]    source:dolphin3
      $6  #70 devious          45.41°C 🥵  958‰  ~29 used:14 [28]   source:dolphin3
      $7 #109 deceive          44.42°C 🥵  953‰   ~4 used:0  [3]    source:dolphin3
      $8 #115 sway             39.94°C 😎  873‰   ~5 used:0  [4]    source:dolphin3
      $9  #66 influence        39.56°C 😎  863‰  ~31 used:2  [30]   source:dolphin3
     $10  #92 deceitful        39.54°C 😎  861‰  ~32 used:2  [31]   source:dolphin3
     $11  #99 deviously        39.24°C 😎  854‰   ~6 used:1  [5]    source:dolphin3
     $12 #108 scheming         38.22°C 😎  832‰   ~7 used:0  [6]    source:dolphin3
     $35  #74 artifice         28.60°C 🥶        ~36 used:0  [35]   source:dolphin3
    $116  #29 rate             -1.48°C 🧊       ~116 used:0  [115]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1476 🥳 68 ⏱️ 0:00:32.970459

🤔 69 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 8 chat prompts
🤖 8 dolphin3:latest replies
🔥  1 🥵  4 😎  1 🥶 39 🧊 23

     $1 #69 républicain    100.00°C 🥳 1000‰ ~46 used:0 [45]  source:dolphin3
     $2 #60 démocratique    58.15°C 🔥  998‰  ~1 used:0 [0]   source:dolphin3
     $3 #68 progressiste    48.83°C 🥵  973‰  ~2 used:0 [1]   source:dolphin3
     $4 #30 civique         47.91°C 🥵  971‰  ~5 used:2 [4]   source:dolphin3
     $5 #32 citoyen         47.23°C 🥵  967‰  ~3 used:0 [2]   source:dolphin3
     $6 #67 libéral         44.26°C 🥵  943‰  ~4 used:0 [3]   source:dolphin3
     $7 #33 citoyenneté     37.90°C 😎  843‰  ~6 used:0 [5]   source:dolphin3
     $8 #12 école           24.96°C 🥶        ~7 used:5 [6]   source:dolphin3
     $9 #14 éducation       23.85°C 🥶        ~8 used:4 [7]   source:dolphin3
    $10 #41 primaire        22.80°C 🥶       ~11 used:0 [10]  source:dolphin3
    $11 #59 communauté      21.09°C 🥶       ~12 used:0 [11]  source:dolphin3
    $12 #55 scolaire        20.24°C 🥶       ~13 used:0 [12]  source:dolphin3
    $13 #26 devoir          19.52°C 🥶       ~10 used:2 [9]   source:dolphin3
    $47 #47 concours        -0.32°C 🧊       ~47 used:0 [46]  source:dolphin3
