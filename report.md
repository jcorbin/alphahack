# 2026-01-05

- 🔗 spaceword.org 🧩 2026-01-04 🏁 score 2173 ranked 7.1% 24/336 ⏱️ 0:19:40.369727
- 🔗 alfagok.diginaut.net 🧩 #429 🥳 20 ⏱️ 0:01:04.159327
- 🔗 alphaguess.com 🧩 #895 🥳 13 ⏱️ 0:00:55.438822
- 🔗 dontwordle.com 🧩 #1322 🥳 6 ⏱️ 0:02:10.479775
- 🔗 dictionary.com hurdle 🧩 #1465 😦 16 ⏱️ 0:03:43.479497
- 🔗 Quordle Classic 🧩 #1442 🥳 score:28 ⏱️ 0:03:32.880547
- 🔗 Octordle Classic 🧩 #1442 🥳 score:62 ⏱️ 0:04:25.923598
- 🔗 squareword.org 🧩 #1435 🥳 8 ⏱️ 0:02:13.124985
- 🔗 cemantle.certitudes.org 🧩 #1372 🥳 158 ⏱️ 0:13:12.715010
- 🔗 cemantix.certitudes.org 🧩 #1405 🥳 173 ⏱️ 0:06:21.592065
- 🔗 Quordle Rescue 🧩 #56 🥳 score:22 ⏱️ 0:02:23.888132
- 🔗 Quordle Sequence 🧩 #1442 🥳 score:26 ⏱️ 0:01:43.336150

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











# spaceword.org 🧩 2026-01-04 🏁 score 2173 ranked 7.1% 24/336 ⏱️ 0:19:40.369727

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 24/336

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ D _ J _ _ _   
      _ _ _ _ O _ O _ _ _   
      _ _ _ _ R A W _ _ _   
      _ _ _ _ _ Q I _ _ _   
      _ _ _ _ _ U N _ _ _   
      _ _ _ _ Y A G _ _ _   
      _ _ _ _ E R _ _ _ _   
      _ _ _ _ L I E _ _ _   
      _ _ _ _ P A _ _ _ _   


# alfagok.diginaut.net 🧩 #429 🥳 20 ⏱️ 0:01:04.159327

🤔 20 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+1      [     1] &-tekens    
    @+2      [     2] -cijferig   
    @+3      [     3] -e-mail     
    @+199833 [199833] lijm        q0  ? after
    @+299746 [299746] schub       q1  ? after
    @+349531 [349531] vakantie    q2  ? after
    @+353099 [353099] ver         q4  ? after
    @+358392 [358392] verluieren  q6  ? after
    @+359012 [359012] vernieuwing q9  ? after
    @+359307 [359307] verpakking  q10 ? after
    @+359419 [359419] verpleeg    q11 ? after
    @+359531 [359531] verpoos     q13 ? after
    @+359583 [359583] verrader    q15 ? after
    @+359600 [359600] verras      q16 ? after
    @+359601 [359601] verrassen   q19 ? it
    @+359601 [359601] verrassen   done. it
    @+359602 [359602] verrassend  q18 ? before
    @+359610 [359610] verrassing  q17 ? before
    @+359640 [359640] verre       q8  ? before
    @+361033 [361033] verstrak    q7  ? before
    @+363682 [363682] verzot      q5  ? before
    @+374273 [374273] vrij        q3  ? before

# alphaguess.com 🧩 #895 🥳 13 ⏱️ 0:00:55.438822

🤔 13 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+47386 [47386] dis        q1  ? after
    @+53402 [53402] el         q4  ? after
    @+54925 [54925] end        q6  ? after
    @+55324 [55324] eng        q8  ? after
    @+55347 [55347] engine     q12 ? it
    @+55347 [55347] engine     done. it
    @+55384 [55384] engraft    q11 ? before
    @+55443 [55443] enharmonic q10 ? before
    @+55562 [55562] enol       q9  ? before
    @+55805 [55805] enter      q7  ? before
    @+56747 [56747] equate     q5  ? before
    @+60089 [60089] face       q3  ? before
    @+72805 [72805] gremmy     q2  ? before
    @+98224 [98224] mach       q0  ? before

# dontwordle.com 🧩 #1322 🥳 6 ⏱️ 0:02:10.479775

📜 1 sessions
💰 score: 12

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:7419
    ⬜⬜⬜⬜⬜ tried:BOBBY n n n n n remain:3170
    ⬜⬜⬜⬜⬜ tried:VIGIL n n n n n remain:1012
    ⬜⬜⬜⬜⬜ tried:SUKHS n n n n n remain:120
    ⬜🟩⬜⬜🟩 tried:FEEZE n Y n n Y remain:13
    ⬜🟩🟩⬜🟩 tried:RENTE n Y Y n Y remain:2

    Undos used: 1

      2 words remaining
    x 6 unused letters
    = 12 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1465 😦 16 ⏱️ 0:03:43.479497

📜 2 sessions
💰 score: 2260

    4/6
    STARE 🟨⬜🟩⬜⬜
    PLANS ⬜🟩🟩⬜🟨
    CLASH ⬜🟩🟩🟩🟩
    FLASH 🟩🟩🟩🟩🟩
    6/6
    FLASH ⬜⬜🟩⬜⬜
    DRAPE ⬜🟩🟩⬜⬜
    BRANK ⬜🟩🟩⬜🟩
    TRACK ⬜🟩🟩🟩🟩
    CRACK ⬜🟩🟩🟩🟩
    WRACK 🟩🟩🟩🟩🟩
    6/6
    ????? ⬜⬜⬜⬜⬜
    ????? ⬜⬜⬜⬜⬜
    ????? ⬜⬜🟨🟩🟩
    ????? ⬜🟩🟩🟩🟩
    ????? ⬜🟩🟩🟩🟩
    ????? ⬜🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1442 🥳 score:28 ⏱️ 0:03:32.880547

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. OWNER attempts:5 score:5
2. VILLA attempts:9 score:9
3. BEARD attempts:8 score:8
4. METER attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1442 🥳 score:62 ⏱️ 0:04:25.923598

📜 4 sessions

Octordle Classic

1. CLASS attempts:13 score:13
2. SNAIL attempts:5 score:5
3. PATIO attempts:6 score:6
4. HEARD attempts:11 score:11
5. KNELT attempts:7 score:7
6. NEWER attempts:9 score:9
7. ELOPE attempts:3 score:3
8. SAVOR attempts:8 score:8

# squareword.org 🧩 #1435 🥳 8 ⏱️ 0:02:13.124985

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟩 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P A L S Y
    S L A T E
    Y O D E L
    C H E A P
    H A N K S

# cemantle.certitudes.org 🧩 #1372 🥳 158 ⏱️ 0:13:12.715010

🤔 159 attempts
📜 1 sessions
🫧 13 chat sessions
⁉️ 47 chat prompts
🤖 20 dolphin3:latest replies
🤖 27 ministral-3:14b replies
😱  1 🔥  8 🥵 13 😎 40 🥶 84 🧊 12

      $1 #159   ~1 proud          100.00°C 🥳 1000‰
      $2  #94  ~32 thrilled        72.84°C 😱  999‰
      $3  #86  ~40 pleased         71.24°C 🔥  998‰
      $4  #74  ~48 delighted       70.18°C 🔥  997‰
      $5  #80  ~44 grateful        70.07°C 🔥  996‰
      $6  #98  ~29 excited         68.33°C 🔥  995‰
      $7  #71  ~49 glad            65.73°C 🔥  994‰
      $8  #66  ~53 thankful        64.43°C 🔥  992‰
      $9  #88  ~38 happy           63.60°C 🔥  991‰
     $10  #68  ~51 appreciative    62.48°C 🔥  990‰
     $11 #120  ~19 gratified       60.81°C 🥵  989‰
     $24  #97  ~30 eager           35.53°C 😎  895‰
     $64  #51      smile           20.72°C 🥶
    $148   #5      kaleidoscope    -0.06°C 🧊

# cemantix.certitudes.org 🧩 #1405 🥳 173 ⏱️ 0:06:21.592065

🤔 174 attempts
📜 1 sessions
🫧 14 chat sessions
⁉️ 41 chat prompts
🤖 26 ministral-3:14b replies
🤖 15 dolphin3:latest replies
🔥   4 🥵  10 😎  26 🥶 113 🧊  20

      $1 #174   ~1 bâton         100.00°C 🥳 1000‰
      $2 #121  ~17 épée           46.95°C 😱  999‰
      $3 #110  ~19 cimeterre      43.96°C 🔥  996‰
      $4 #120  ~18 hache          41.48°C 🔥  992‰
      $5 #134  ~11 glaive         40.81°C 🔥  991‰
      $6   #4  ~41 chapeau        40.25°C 🥵  989‰
      $7 #102  ~25 sabre          37.59°C 🥵  980‰
      $8 #144   ~6 couteau        35.98°C 🥵  971‰
      $9 #128  ~15 poignard       35.19°C 🥵  961‰
     $10  #79  ~30 brodequin      35.01°C 🥵  960‰
     $11  #78  ~31 bras           34.94°C 🥵  959‰
     $16 #133  ~12 gantelet       32.22°C 😎  892‰
     $42  #56      calot          23.27°C 🥶
    $155  #11      école          -0.08°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #56 🥳 score:22 ⏱️ 0:02:23.888132

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. SAVOR attempts:4 score:4
2. CHOKE attempts:3 score:3
3. FURRY attempts:7 score:7
4. PAGAN attempts:8 score:8

# [Quordle Sequence](m-w.com/games/quordle/#/sequence) 🧩 #1442 🥳 score:26 ⏱️ 0:01:43.336150

📜 1 sessions

Quordle Sequence m-w.com/games/quordle/

1. HARSH attempts:4 score:4
2. ASCOT attempts:5 score:5
3. UDDER attempts:8 score:8
4. LABEL attempts:9 score:9
