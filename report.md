# 2026-01-07

- 🔗 spaceword.org 🧩 2026-01-06 🏁 score 2173 ranked 1.9% 8/428 ⏱️ 3:32:22.370937
- 🔗 alfagok.diginaut.net 🧩 #431 🥳 9 ⏱️ 0:00:24.110808
- 🔗 alphaguess.com 🧩 #897 🥳 16 ⏱️ 0:00:32.182493
- 🔗 dontwordle.com 🧩 #1324 🥳 6 ⏱️ 0:01:22.191363
- 🔗 dictionary.com hurdle 🧩 #1467 🥳 19 ⏱️ 0:03:40.781321
- 🔗 Quordle Classic 🧩 #1444 🥳 score:18 ⏱️ 0:01:19.032734
- 🔗 Octordle Classic 🧩 #1444 🥳 score:55 ⏱️ 0:03:19.785836
- 🔗 squareword.org 🧩 #1437 🥳 8 ⏱️ 0:01:56.301086
- 🔗 cemantle.certitudes.org 🧩 #1374 🥳 189 ⏱️ 0:02:28.019271
- 🔗 cemantix.certitudes.org 🧩 #1407 🥳 495 ⏱️ 0:30:58.334374
- 🔗 Quordle Rescue 🧩 #58 🥳 score:26 ⏱️ 0:03:40.036932
- 🔗 Quordle Sequence 🧩 #1444 🥳 score:22 ⏱️ 0:01:51.204363
- 🔗 Octordle Rescue 🧩 #1444 😦 score:5 ⏱️ 0:04:33.561973
- 🔗 Octordle Sequence 🧩 #1444 🥳 score:56 ⏱️ 0:03:04.203607

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













# spaceword.org 🧩 2026-01-06 🏁 score 2173 ranked 1.9% 8/428 ⏱️ 3:32:22.370937

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 8/428

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ C R U _ _ _   
      _ _ _ _ U _ P _ _ _   
      _ _ _ _ B A L _ _ _   
      _ _ _ _ _ Q I _ _ _   
      _ _ _ _ O U T _ _ _   
      _ _ _ _ _ I _ _ _ _   
      _ _ _ _ _ V _ _ _ _   
      _ _ _ _ D E W _ _ _   
      _ _ _ _ O R E _ _ _   


# alfagok.diginaut.net 🧩 #431 🥳 9 ⏱️ 0:00:24.110808

🤔 9 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+1      [     1] &-tekens    
    @+2      [     2] -cijferig   
    @+3      [     3] -e-mail     
    @+199833 [199833] lijm        q0 ? after
    @+299746 [299746] schub       q1 ? after
    @+324322 [324322] sub         q3 ? after
    @+327313 [327313] tafel       q6 ? after
    @+328903 [328903] technologie q7 ? after
    @+329660 [329660] teken       q8 ? it
    @+329660 [329660] teken       done. it
    @+330507 [330507] televisie   q5 ? before
    @+336924 [336924] toetsing    q4 ? before
    @+349531 [349531] vakantie    q2 ? before

# alphaguess.com 🧩 #897 🥳 16 ⏱️ 0:00:32.182493

🤔 16 attempts
📜 1 sessions

    @        [     0] aa        
    @+1      [     1] aah       
    @+2      [     2] aahed     
    @+3      [     3] aahing    
    @+98224  [ 98224] mach      q0  ? after
    @+109943 [109943] ne        q3  ? after
    @+110715 [110715] neuroglia q6  ? after
    @+111104 [111104] niddering q7  ? after
    @+111139 [111139] niff      q10 ? after
    @+111149 [111149] niffy     q12 ? after
    @+111154 [111154] niftiness q13 ? after
    @+111156 [111156] nifty     q15 ? it
    @+111156 [111156] nifty     done. it
    @+111157 [111157] nigella   q14 ? before
    @+111159 [111159] niggard   q11 ? before
    @+111185 [111185] night     q9  ? before
    @+111289 [111289] nim       q8  ? before
    @+111493 [111493] no        q5  ? before
    @+116361 [116361] orchard   q4  ? before
    @+122787 [122787] parr      q2  ? before
    @+147377 [147377] rhotic    q1  ? before

# dontwordle.com 🧩 #1324 🥳 6 ⏱️ 0:01:22.191363

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:YUKKY n n n n n remain:7806
    ⬜⬜⬜⬜⬜ tried:PEEVE n n n n n remain:3039
    ⬜⬜⬜⬜⬜ tried:MACAW n n n n n remain:697
    ⬜⬜⬜⬜⬜ tried:LININ n n n n n remain:137
    ⬜🟨⬜⬜🟨 tried:BOFFO n m n n m remain:10
    🟨⬜🟩🟩⬜ tried:TROOZ m n Y Y n remain:2

    Undos used: 3

      2 words remaining
    x 7 unused letters
    = 14 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1467 🥳 19 ⏱️ 0:03:40.781321

📜 2 sessions
💰 score: 9700

    6/6
    URSAE ⬜⬜🟨⬜🟨
    NOELS ⬜⬜🟩🟩🟨
    SKELP 🟩⬜🟩🟩⬜
    SHELF 🟩⬜🟩🟩⬜
    SMELT 🟩🟩🟩🟩⬜
    SMELL 🟩🟩🟩🟩🟩
    4/6
    SMELL 🟩⬜⬜⬜🟩
    SKOAL 🟩⬜🟩⬜🟩
    SPOOL 🟩⬜🟩⬜🟩
    SCOWL 🟩🟩🟩🟩🟩
    3/6
    SCOWL ⬜🟨⬜⬜⬜
    CERIA 🟩🟨🟨⬜⬜
    CRUDE 🟩🟩🟩🟩🟩
    5/6
    CRUDE ⬜🟨⬜⬜🟨
    YEARS 🟨🟩⬜🟩⬜
    HENRY ⬜🟩⬜🟩🟩
    RETRY 🟨🟩⬜🟩🟩
    BERRY 🟩🟩🟩🟩🟩
    Final 1/2
    EASEL 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1444 🥳 score:18 ⏱️ 0:01:19.032734

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. BEARD attempts:5 score:5
2. SPICY attempts:4 score:4
3. MOIST attempts:6 score:6
4. SWIRL attempts:3 score:3

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1444 🥳 score:55 ⏱️ 0:03:19.785836

📜 1 sessions

Octordle Classic

1. LIMIT attempts:7 score:7
2. DINGO attempts:11 score:11
3. VENUE attempts:10 score:10
4. ALPHA attempts:6 score:6
5. CLIFF attempts:5 score:5
6. FLORA attempts:4 score:4
7. THEIR attempts:3 score:3
8. GLADE attempts:9 score:9

# squareword.org 🧩 #1437 🥳 8 ⏱️ 0:01:56.301086

📜 2 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C R O F T
    R A Z O R
    I V O R Y
    B E N T S
    S L E E T

# cemantle.certitudes.org 🧩 #1374 🥳 189 ⏱️ 0:02:28.019271

🤔 190 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 42 chat prompts
🤖 42 dolphin3:latest replies
🔥   3 🥵   3 😎  26 🥶 141 🧊  16

      $1 #190   ~1 legitimate      100.00°C 🥳 1000‰
      $2 #178   ~7 lawful           51.68°C 🔥  997‰
      $3 #177   ~8 justifiable      51.27°C 🔥  996‰
      $4 #186   ~3 credible         44.73°C 🔥  990‰
      $5 #176   ~9 honest           36.65°C 🥵  966‰
      $6 #189   ~2 legal            36.09°C 🥵  962‰
      $7 #124  ~23 necessary        34.16°C 🥵  925‰
      $8 #144  ~17 right            33.25°C 😎  899‰
      $9 #180   ~5 appropriate      32.80°C 😎  886‰
     $10 #134  ~19 paramount        32.06°C 😎  858‰
     $11  #59  ~33 fundamental      31.79°C 😎  850‰
     $12 #170  ~13 ethical          31.61°C 😎  845‰
     $34  #66      essential        23.80°C 🥶
    $175   #8      ocean            -0.05°C 🧊

# cemantix.certitudes.org 🧩 #1407 🥳 495 ⏱️ 0:30:58.334374

🤔 496 attempts
📜 2 sessions
🫧 47 chat sessions
⁉️ 193 chat prompts
🤖 13 ministral-3:14b replies
🤖 62 glm4:latest replies
🤖 118 dolphin3:latest replies
🔥   1 🥵  10 😎  46 🥶 341 🧊  97

      $1 #496   ~1 vain              100.00°C 🥳 1000‰
      $2 #272  ~35 obstinément        52.28°C 🔥  994‰
      $3 #380  ~17 obstiner           50.20°C 🥵  985‰
      $4 #223  ~41 inlassablement     45.85°C 🥵  962‰
      $5 #111  ~55 obstination        44.49°C 🥵  948‰
      $6 #320  ~23 furieux            43.96°C 🥵  941‰
      $7 #231  ~38 éternel            43.91°C 🥵  940‰
      $8 #307  ~24 obstiné            43.20°C 🥵  929‰
      $9 #273  ~34 désespérément      42.98°C 🥵  925‰
     $10 #493   ~2 inanité            42.78°C 🥵  922‰
     $11 #255  ~36 incessamment       42.21°C 🥵  907‰
     $13 #295  ~27 cruellement        41.55°C 😎  888‰
     $59 #395      péremptoire        31.89°C 🥶
    $400 #238      permanence         -0.10°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #58 🥳 score:26 ⏱️ 0:03:40.036932

📜 7 sessions

Quordle Rescue m-w.com/games/quordle/

1. COMET attempts:7 score:7
2. CHEAP attempts:6 score:6
3. SCOWL attempts:8 score:8
4. PALER attempts:5 score:5

# [Quordle Sequence](m-w.com/games/quordle/#/sequence) 🧩 #1444 🥳 score:22 ⏱️ 0:01:51.204363

📜 2 sessions

Quordle Sequence m-w.com/games/quordle/

1. HONEY attempts:4 score:4
2. RETRY attempts:5 score:5
3. NEIGH attempts:6 score:6
4. MANGE attempts:7 score:7

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1444 😦 score:5 ⏱️ 0:04:33.561973

📜 3 sessions

Octordle Rescue

1. STORE attempts:10 score:13
2. _RO_E -ACDGHIKLNPQSTUWY attempts:10 score:-1
3. ASSAY attempts:3 score:6
4. RIPEN attempts:8 score:11
5. _I_I_ ~C -ADEGHKLNOPQRSTUWY attempts:10 score:-1
6. GROIN attempts:5 score:8
7. GRIND attempts:6 score:9
8. AN_LE -CDGHIKOPQRSTUWY attempts:10 score:-1

# [Octordle Sequence](britannica.com/games/octordle/daily-sequence) 🧩 #1444 🥳 score:56 ⏱️ 0:03:04.203607

📜 1 sessions

Octordle Sequence

1. SETUP attempts:3 score:3
2. SPORT attempts:4 score:4
3. QUOTH attempts:5 score:5
4. FUGUE attempts:6 score:6
5. RELAX attempts:8 score:8
6. GUILD attempts:9 score:9
7. UNION attempts:10 score:10
8. WINCH attempts:11 score:11
