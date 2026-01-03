# 2026-01-04

- 🔗 spaceword.org 🧩 2026-01-03 🏁 score 2168 ranked 41.1% 144/350 ⏱️ 0:09:01.141047
- 🔗 alfagok.diginaut.net 🧩 #428 🥳 17 ⏱️ 0:01:15.601548
- 🔗 alphaguess.com 🧩 #894 🥳 18 ⏱️ 0:00:44.199823
- 🔗 dontwordle.com 🧩 #1321 🥳 6 ⏱️ 0:03:11.904702
- 🔗 dictionary.com hurdle 🧩 #1464 🥳 17 ⏱️ 0:03:00.592089
- 🔗 Quordle Classic 🧩 #1441 🥳 score:22 ⏱️ 0:04:23.609766
- 🔗 Octordle Classic 🧩 #1441 🥳 score:55 ⏱️ 0:04:20.225584
- 🔗 squareword.org 🧩 #1434 🥳 8 ⏱️ 0:03:10.391139
- 🔗 cemantle.certitudes.org 🧩 #1371 🥳 846 ⏱️ 0:59:18.748711
- 🔗 cemantix.certitudes.org 🧩 #1404 🥳 347 ⏱️ 0:12:53.183725
- 🔗 Quordle Rescue 🧩 #55 🥳 score:26 ⏱️ 0:01:31.760611
- 🔗 Quordle Sequence 🧩 #1441 🥳 score:25 ⏱️ 0:01:37.921019

# Dev

## WIP

- meta: rework SolverHarness => Solver{ Library, Scope }

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










# spaceword.org 🧩 2026-01-03 🏁 score 2168 ranked 41.1% 144/350 ⏱️ 0:09:01.141047

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 144/350

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ C _ _ E _ _ _   
      _ _ _ R _ _ X _ _ _   
      _ _ _ E C R U _ _ _   
      _ _ _ A _ E D _ _ _   
      _ _ _ K _ W E _ _ _   
      _ _ _ I _ I _ _ _ _   
      _ _ _ L O R _ _ _ _   
      _ _ _ Y _ E _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #428 🥳 17 ⏱️ 0:01:15.601548

🤔 17 attempts
📜 2 sessions

    @        [     0] &-teken       
    @+1      [     1] &-tekens      
    @+2      [     2] -cijferig     
    @+3      [     3] -e-mail       
    @+99758  [ 99758] ex            q1  ? after
    @+149454 [149454] huis          q2  ? after
    @+153625 [153625] in            q5  ? after
    @+155717 [155717] ingedeeld     q7  ? after
    @+156239 [156239] ingezeept     q9  ? after
    @+156465 [156465] inhoud        q10 ? after
    @+156470 [156470] inhouden      q16 ? it
    @+156470 [156470] inhouden      done. it
    @+156473 [156473] inhouding     q15 ? before
    @+156481 [156481] inhoudsbeheer q14 ? before
    @+156497 [156497] inhoudstabel  q13 ? before
    @+156529 [156529] inhuur        q12 ? before
    @+156604 [156604] injectie      q11 ? before
    @+156760 [156760] inkomens      q8  ? before
    @+157808 [157808] inrichting    q6  ? before
    @+162009 [162009] izabel        q4  ? before
    @+174561 [174561] kind          q3  ? before
    @+199833 [199833] lijm          q0  ? before

# alphaguess.com 🧩 #894 🥳 18 ⏱️ 0:00:44.199823

🤔 18 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+47386 [47386] dis       q1  ? after
    @+72805 [72805] gremmy    q2  ? after
    @+85509 [85509] ins       q3  ? after
    @+91854 [91854] knot      q4  ? after
    @+94951 [94951] lib       q5  ? after
    @+96584 [96584] locks     q6  ? after
    @+96763 [96763] logo      q9  ? after
    @+96816 [96816] loid      q11 ? after
    @+96830 [96830] loll      q12 ? after
    @+96837 [96837] lollers   q14 ? after
    @+96840 [96840] lollingly q15 ? after
    @+96841 [96841] lollipop  q17 ? it
    @+96841 [96841] lollipop  done. it
    @+96842 [96842] lollipops q16 ? before
    @+96843 [96843] lollop    q13 ? before
    @+96866 [96866] lone      q10 ? before
    @+96974 [96974] loo       q8  ? before
    @+97367 [97367] low       q7  ? before
    @+98224 [98224] mach      q0  ? before

# dontwordle.com 🧩 #1321 🥳 6 ⏱️ 0:03:11.904702

📜 1 sessions
💰 score: 21

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:SIBBS n n n n n remain:4209
    ⬜⬜⬜⬜⬜ tried:HOWFF n n n n n remain:1798
    ⬜⬜⬜⬜⬜ tried:YUPPY n n n n n remain:712
    ⬜🟩⬜⬜⬜ tried:CEDED n Y n n n remain:37
    ⬜🟩⬜⬜🟨 tried:GEMMA n Y n n m remain:9
    🟨🟩🟨🟨⬜ tried:LEANT m Y m m n remain:3

    Undos used: 1

      3 words remaining
    x 7 unused letters
    = 21 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1464 🥳 17 ⏱️ 0:03:00.592089

📜 1 sessions
💰 score: 9900

    4/6
    LEARS ⬜🟨⬜⬜⬜
    WIDEN ⬜🟨🟨🟨⬜
    DOGIE 🟨⬜⬜🟨🟩
    CHIDE 🟩🟩🟩🟩🟩
    5/6
    CHIDE ⬜⬜🟨⬜⬜
    PALIS 🟨⬜⬜🟨🟨
    WISPY ⬜🟩🟨🟨🟩
    GIPSY ⬜🟩🟩🟩🟩
    TIPSY 🟩🟩🟩🟩🟩
    4/6
    TIPSY 🟨🟨⬜⬜⬜
    RELIT ⬜🟨⬜🟨🟩
    EDICT 🟨⬜🟩⬜🟩
    QUIET 🟩🟩🟩🟩🟩
    3/6
    QUIET ⬜⬜⬜🟩⬜
    WARES 🟨⬜🟨🟩⬜
    OWNER 🟩🟩🟩🟩🟩
    Final 1/2
    LEGIT 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1441 🥳 score:22 ⏱️ 0:04:23.609766

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. STUNG attempts:5 score:5
2. COLOR attempts:4 score:4
3. BRASS attempts:7 score:7
4. CYBER attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1441 🥳 score:55 ⏱️ 0:04:20.225584

📜 1 sessions

Octordle Classic

1. TABOO attempts:7 score:7
2. WHOSE attempts:10 score:10
3. AXION attempts:4 score:4
4. ENJOY attempts:3 score:3
5. MORAL attempts:12 score:12
6. ABBOT attempts:8 score:8
7. BATON attempts:5 score:5
8. BUNNY attempts:6 score:6

# squareword.org 🧩 #1434 🥳 8 ⏱️ 0:03:10.391139

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟨 🟨 🟨 🟨 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C H A S E
    A O R T A
    S A G E S
    K R O N E
    S Y N O D

# cemantle.certitudes.org 🧩 #1371 🥳 846 ⏱️ 0:59:18.748711

🤔 847 attempts
📜 3 sessions
🫧 84 chat sessions
⁉️ 307 chat prompts
🤖 16 ministral-3:14b replies
🤖 3 wizardlm2:8x22b replies
🤖 3 qwen3:14b replies
🤖 42 glm4:latest replies
🤖 2 qwen3:32b replies
🤖 11 mixtral:8x7b replies
🤖 12 llama3.3:latest replies
🤖 192 dolphin3:latest replies
🤖 13 gemma3:27b replies
🤖 12 falcon3:10b replies
🔥   3 🥵  18 😎  82 🥶 662 🧊  81

      $1 #847   ~1 header            100.00°C 🥳 1000‰
      $2 #313  ~96 volley             67.12°C 🔥  998‰
      $3 #355  ~92 deflection         60.94°C 🔥  995‰
      $4 #498  ~56 parry              55.83°C 🔥  993‰
      $5 #119 ~102 thunderbolt        52.00°C 🥵  987‰
      $6 #475  ~59 lob                51.81°C 🥵  986‰
      $7 #367  ~88 kick               50.96°C 🥵  984‰
      $8 #392  ~80 goal               46.43°C 🥵  976‰
      $9 #749  ~16 corner             43.22°C 🥵  962‰
     $10 #682  ~29 flank              42.16°C 🥵  961‰
     $11 #811   ~5 defender           42.01°C 🥵  959‰
     $23 #707  ~23 forehand           33.93°C 😎  895‰
    $105 #103      precipitation      18.48°C 🥶
    $767 #223      activity           -0.03°C 🧊

# cemantix.certitudes.org 🧩 #1404 🥳 347 ⏱️ 0:12:53.183725

🤔 348 attempts
📜 1 sessions
🫧 36 chat sessions
⁉️ 131 chat prompts
🤖 11 ministral-3:14b replies
🤖 16 glm4:latest replies
🤖 104 dolphin3:latest replies
🔥   6 🥵  26 😎  57 🥶 220 🧊  38

      $1 #348   ~1 provenance         100.00°C 🥳 1000‰
      $2  #27  ~88 importation         47.16°C 🔥  997‰
      $3  #61  ~76 destination         44.25°C 🔥  996‰
      $4  #23  ~89 exportation         42.27°C 🔥  995‰
      $5  #53  ~81 importateur         41.23°C 🔥  994‰
      $6  #98  ~62 acheminer           41.19°C 🔥  993‰
      $7 #114  ~54 réexportation       39.96°C 🔥  990‰
      $8 #138  ~41 origine             39.91°C 🥵  989‰
      $9  #58  ~77 transit             39.21°C 🥵  988‰
     $10 #103  ~58 réimportation       35.95°C 🥵  986‰
     $11 #288   ~8 arrivage            35.55°C 🥵  984‰
     $34 #145  ~38 localisation        25.51°C 😎  896‰
     $91  #48      commercial          16.92°C 🥶
    $311 #292      franchise           -0.34°C 🧊


# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #55 🥳 score:26 ⏱️ 0:01:31.760611

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. AMITY attempts:5 score:5
2. TRIBE attempts:8 score:8
3. TIMER attempts:7 score:7
4. SOOTH attempts:6 score:6

# [Quordle Sequence](m-w.com/games/quordle/#/sequence) 🧩 #1441 🥳 score:25 ⏱️ 0:01:37.921019

📜 1 sessions

Quordle Sequence m-w.com/games/quordle/

1. CHARM attempts:4 score:4
2. SPORE attempts:6 score:6
3. THORN attempts:7 score:7
4. SMELL attempts:8 score:8
