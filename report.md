# 2026-02-25

- 🔗 spaceword.org 🧩 2026-02-24 🏁 score 2173 ranked 8.9% 29/327 ⏱️ 2:33:53.178391
- 🔗 alfagok.diginaut.net 🧩 #480 🥳 32 ⏱️ 0:00:33.686629
- 🔗 alphaguess.com 🧩 #947 🥳 26 ⏱️ 0:00:24.247124
- 🔗 dontwordle.com 🧩 #1373 🥳 6 ⏱️ 0:01:31.391089
- 🔗 dictionary.com hurdle 🧩 #1516 🥳 16 ⏱️ 0:03:19.237378
- 🔗 Quordle Classic 🧩 #1493 🥳 score:24 ⏱️ 0:01:44.208301
- 🔗 Octordle Classic 🧩 #1493 🥳 score:57 ⏱️ 0:03:03.985210
- 🔗 squareword.org 🧩 #1486 🥳 8 ⏱️ 0:01:47.559166
- 🔗 cemantle.certitudes.org 🧩 #1423 🥳 84 ⏱️ 0:00:34.674430
- 🔗 cemantix.certitudes.org 🧩 #1456 🥳 129 ⏱️ 0:02:43.858903

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







# [spaceword.org](spaceword.org) 🧩 2026-02-24 🏁 score 2173 ranked 8.9% 29/327 ⏱️ 2:33:53.178391

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 29/327

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ L _ G _ _ _ S O P   
      _ A _ O X A Z I N E   
      _ T R A U M A _ O W   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #480 🥳 32 ⏱️ 0:00:33.686629

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken       
    @+199816 [199816] lijm          q0  ? ␅
    @+199816 [199816] lijm          q1  ? after
    @+299709 [299709] schub         q2  ? ␅
    @+299709 [299709] schub         q3  ? after
    @+349477 [349477] vakantie      q4  ? ␅
    @+349477 [349477] vakantie      q5  ? after
    @+353045 [353045] ver           q8  ? ␅
    @+353045 [353045] ver           q9  ? after
    @+363628 [363628] verzot        q10 ? ␅
    @+363628 [363628] verzot        q11 ? after
    @+368640 [368640] voetbal       q12 ? ␅
    @+368640 [368640] voetbal       q13 ? after
    @+370489 [370489] voor          q14 ? ␅
    @+370489 [370489] voor          q15 ? after
    @+372341 [372341] voortplanting q16 ? ␅
    @+372341 [372341] voortplanting q17 ? after
    @+372775 [372775] voorwereld    q20 ? ␅
    @+372775 [372775] voorwereld    q21 ? after
    @+372986 [372986] vork          q22 ? ␅
    @+372986 [372986] vork          q23 ? after
    @+372996 [372996] vorm          q24 ? ␅
    @+372996 [372996] vorm          q25 ? after
    @+373051 [373051] vormgeving    q28 ? ␅
    @+373051 [373051] vormgeving    q29 ? after
    @+373059 [373059] vorming       q30 ? ␅
    @+373059 [373059] vorming       q31 ? it
    @+373059 [373059] vorming       done. it
    @+373104 [373104] vormloosheid  q26 ? ␅
    @+373104 [373104] vormloosheid  q27 ? before
    @+373212 [373212] vos           q19 ? before

# [alphaguess.com](alphaguess.com) 🧩 #947 🥳 26 ⏱️ 0:00:24.247124

🤔 26 attempts
📜 1 sessions

    @       [    0] aa     
    @+1     [    1] aah    
    @+2     [    2] aahed  
    @+3     [    3] aahing 
    @+47381 [47381] dis    q2  ? ␅
    @+47381 [47381] dis    q3  ? after
    @+72800 [72800] gremmy q4  ? ␅
    @+72800 [72800] gremmy q5  ? after
    @+85504 [85504] ins    q6  ? ␅
    @+85504 [85504] ins    q7  ? after
    @+88664 [88664] jacks  q10 ? ␅
    @+88664 [88664] jacks  q11 ? after
    @+89430 [89430] jird   q14 ? ␅
    @+89430 [89430] jird   q15 ? after
    @+89777 [89777] joy    q16 ? ␅
    @+89777 [89777] joy    q17 ? after
    @+89982 [89982] jumble q18 ? ␅
    @+89982 [89982] jumble q19 ? after
    @+89992 [89992] jump   q24 ? ␅
    @+89992 [89992] jump   q25 ? it
    @+89992 [89992] jump   done. it
    @+90018 [90018] jun    q22 ? ␅
    @+90018 [90018] jun    q23 ? before
    @+90086 [90086] jura   q20 ? ␅
    @+90086 [90086] jura   q21 ? before
    @+90195 [90195] ka     q12 ? ␅
    @+90195 [90195] ka     q13 ? before
    @+91848 [91848] knot   q8  ? ␅
    @+91848 [91848] knot   q9  ? before
    @+98218 [98218] mach   q0  ? ␅
    @+98218 [98218] mach   q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1373 🥳 6 ⏱️ 0:01:31.391089

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:KABAB n n n n n remain:5942
    ⬜⬜⬜⬜⬜ tried:JIFFS n n n n n remain:1644
    ⬜⬜⬜⬜⬜ tried:YUMMY n n n n n remain:654
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:199
    ⬜⬜⬜⬜🟨 tried:PHPHT n n n n m remain:28
    ⬜🟨⬜🟨⬜ tried:CONTO n m n m n remain:1

    Undos used: 4

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1516 🥳 16 ⏱️ 0:03:19.237378

📜 2 sessions
💰 score: 10000

    5/6
    NEARS ⬜⬜🟩⬜🟨
    CLASH 🟨🟨🟩🟨⬜
    SCALD 🟩🟩🟩🟩⬜
    SCALP 🟩🟩🟩🟩⬜
    SCALY 🟩🟩🟩🟩🟩
    3/6
    SCALY ⬜⬜⬜🟨⬜
    OLDIE ⬜🟩🟨🟨⬜
    BLIND 🟩🟩🟩🟩🟩
    3/6
    BLIND ⬜🟨⬜⬜⬜
    TESLA 🟩⬜⬜🟩⬜
    TRULY 🟩🟩🟩🟩🟩
    4/6
    TRULY ⬜⬜⬜🟩⬜
    AISLE ⬜⬜⬜🟩⬜
    CHOLO ⬜⬜🟩🟩⬜
    KNOLL 🟩🟩🟩🟩🟩
    Final 1/2
    LEERY 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1493 🥳 score:24 ⏱️ 0:01:44.208301

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SPOOL attempts:4 score:4
2. INDEX attempts:5 score:5
3. BLUER attempts:8 score:8
4. FELON attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1493 🥳 score:57 ⏱️ 0:03:03.985210

📜 1 sessions

Octordle Classic

1. SMART attempts:4 score:4
2. METRO attempts:3 score:3
3. MATEY attempts:5 score:5
4. INNER attempts:10 score:10
5. PORCH attempts:11 score:11
6. SERVE attempts:7 score:7
7. SLING attempts:8 score:8
8. TONAL attempts:9 score:9

# [squareword.org](squareword.org) 🧩 #1486 🥳 8 ⏱️ 0:01:47.559166

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟩 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C L U B S
    O L D E N
    R A D I I
    E M E N D
    S A R G E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1423 🥳 84 ⏱️ 0:00:34.674430

🤔 85 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 11 chat prompts
🤖 11 dolphin3:latest replies
🥵 10 😎 19 🥶 55

     $1 #85 bottle       100.00°C 🥳 1000‰ ~85 used:0 [84]  source:dolphin3
     $2 #60 drink         54.92°C 🥵  988‰  ~9 used:3 [8]   source:dolphin3
     $3 #36 glass         53.62°C 🥵  982‰ ~10 used:3 [9]   source:dolphin3
     $4 #76 beer          52.98°C 🥵  976‰  ~8 used:2 [7]   source:dolphin3
     $5 #82 soda          52.81°C 🥵  974‰  ~1 used:0 [0]   source:dolphin3
     $6 #59 dispenser     51.90°C 🥵  968‰  ~2 used:0 [1]   source:dolphin3
     $7 #52 carbonated    48.66°C 🥵  954‰  ~3 used:0 [2]   source:dolphin3
     $8 #83 whiskey       48.52°C 🥵  953‰  ~4 used:0 [3]   source:dolphin3
     $9 #57 cup           46.64°C 🥵  941‰  ~5 used:0 [4]   source:dolphin3
    $10 #84 wine          46.07°C 🥵  934‰  ~6 used:0 [5]   source:dolphin3
    $11 #68 spoon         43.96°C 🥵  910‰  ~7 used:0 [6]   source:dolphin3
    $12 #78 juice         40.79°C 😎  851‰ ~11 used:0 [10]  source:dolphin3
    $13 #28 milkshake     39.94°C 😎  832‰ ~27 used:2 [26]  source:dolphin3
    $31 #50 candy         27.78°C 🥶       ~31 used:0 [30]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1456 🥳 129 ⏱️ 0:02:43.858903

🤔 130 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 37 chat prompts
🤖 37 dolphin3:latest replies
🔥  1 🥵 12 😎 21 🥶 69 🧊 26

      $1 #130 chemise        100.00°C 🥳 1000‰ ~104 used:0  [103]  source:dolphin3
      $2 #121 veste           62.06°C 🔥  998‰   ~1 used:3  [0]    source:dolphin3
      $3 #117 pull            51.51°C 🥵  985‰   ~8 used:2  [7]    source:dolphin3
      $4 #113 pardessus       49.40°C 🥵  980‰  ~11 used:3  [10]   source:dolphin3
      $5 #107 blouson         49.10°C 🥵  975‰   ~9 used:2  [8]    source:dolphin3
      $6 #114 parka           48.30°C 🥵  968‰  ~10 used:2  [9]    source:dolphin3
      $7 #115 cardigan        48.08°C 🥵  965‰   ~2 used:0  [1]    source:dolphin3
      $8 #112 paletot         47.13°C 🥵  956‰   ~3 used:0  [2]    source:dolphin3
      $9 #111 manteau         46.87°C 🥵  953‰   ~4 used:0  [3]    source:dolphin3
     $10 #127 vêtement        46.32°C 🥵  949‰   ~5 used:0  [4]    source:dolphin3
     $11  #74 casquette       44.59°C 🥵  935‰  ~29 used:20 [28]   source:dolphin3
     $15 #129 blouse          42.43°C 😎  895‰  ~12 used:0  [11]   source:dolphin3
     $36 #110 imperméable     23.76°C 🥶        ~42 used:0  [41]   source:dolphin3
    $105  #45 poney           -0.04°C 🧊       ~105 used:0  [104]  source:dolphin3
