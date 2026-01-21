# 2026-01-22

- 🔗 spaceword.org 🧩 2026-01-21 🏁 score 2173 ranked 13.4% 43/320 ⏱️ 1:00:16.682378
- 🔗 alfagok.diginaut.net 🧩 #446 🥳 18 ⏱️ 0:00:48.848044
- 🔗 alphaguess.com 🧩 #913 🥳 13 ⏱️ 0:00:38.670904
- 🔗 dontwordle.com 🧩 #1339 🥳 6 ⏱️ 0:02:26.752861
- 🔗 dictionary.com hurdle 🧩 #1482 🥳 21 ⏱️ 0:04:06.360551
- 🔗 Quordle Classic 🧩 #1459 🥳 score:26 ⏱️ 0:01:56.400121
- 🔗 Octordle Classic 🧩 #1459 🥳 score:53 ⏱️ 0:03:41.128235
- 🔗 squareword.org 🧩 #1452 🥳 8 ⏱️ 0:02:54.896359
- 🔗 cemantle.certitudes.org 🧩 #1389 🥳 289 ⏱️ 0:05:15.192250
- 🔗 cemantix.certitudes.org 🧩 #1422 🥳 623 ⏱️ 0:18:12.434350
- 🔗 Quordle Rescue 🧩 #73 🥳 score:25 ⏱️ 0:01:40.800278
- 🔗 Octordle Rescue 🧩 #1459 🥳 score:9 ⏱️ 0:04:38.294487

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







# [spaceword.org](spaceword.org) 🧩 2026-01-21 🏁 score 2173 ranked 13.4% 43/320 ⏱️ 1:00:16.682378

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 43/320

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ V E T _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ _ _ A X _ _ _   
      _ _ _ _ _ G I _ _ _   
      _ _ _ _ W O N _ _ _   
      _ _ _ _ O N E _ _ _   
      _ _ _ _ _ I S _ _ _   
      _ _ _ _ U S _ _ _ _   
      _ _ _ _ P E C _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #446 🥳 18 ⏱️ 0:00:48.848044

🤔 18 attempts
📜 1 sessions

    @        [     0] &-teken             
    @+1      [     1] &-tekens            
    @+2      [     2] -cijferig           
    @+3      [     3] -e-mail             
    @+49849  [ 49849] boks                q2  ? after
    @+74762  [ 74762] dc                  q3  ? after
    @+87223  [ 87223] draag               q4  ? after
    @+93451  [ 93451] eet                 q5  ? after
    @+94052  [ 94052] eigen               q8  ? after
    @+94497  [ 94497] einde               q9  ? after
    @+94505  [ 94505] eindejaarsmarge     q14 ? after
    @+94509  [ 94509] eindejaarsrally     q15 ? after
    @+94511  [ 94511] eindejaarsuitkering q16 ? after
    @+94512  [ 94512] eindelijk           q17 ? it
    @+94512  [ 94512] eindelijk           done. it
    @+94513  [ 94513] eindeloopbaan       q13 ? before
    @+94533  [ 94533] eindexamen          q12 ? before
    @+94618  [ 94618] eindkandidaten      q11 ? before
    @+94739  [ 94739] eindresultaat       q10 ? before
    @+94980  [ 94980] eiwit               q7  ? before
    @+96590  [ 96590] energiek            q6  ? before
    @+99758  [ 99758] ex                  q1  ? before
    @+199833 [199833] lijm                q0  ? before

# [alphaguess.com](alphaguess.com) 🧩 #913 🥳 13 ⏱️ 0:00:38.670904

🤔 13 attempts
📜 1 sessions

    @        [     0] aa      
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98220  [ 98220] mach    q0  ? after
    @+147373 [147373] rhotic  q1  ? after
    @+171643 [171643] ta      q2  ? after
    @+176814 [176814] toil    q4  ? after
    @+176820 [176820] toilet  q12 ? it
    @+176820 [176820] toilet  done. it
    @+176838 [176838] toit    q11 ? before
    @+176861 [176861] tokomak q10 ? before
    @+176908 [176908] toll    q9  ? before
    @+177041 [177041] ton     q8  ? before
    @+177367 [177367] tor     q7  ? before
    @+178110 [178110] tragi   q6  ? before
    @+179409 [179409] tricot  q5  ? before
    @+182008 [182008] un      q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1339 🥳 6 ⏱️ 0:02:26.752861

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:EBBED n n n n n remain:5399
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:2472
    ⬜⬜⬜⬜⬜ tried:ALGAL n n n n n remain:551
    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:224
    ⬜⬜⬜⬜⬜ tried:WORRY n n n n n remain:24
    ⬜🟨⬜⬜🟨 tried:CUFFS n m n n m remain:1

    Undos used: 4

      1 words remaining
    x 6 unused letters
    = 6 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1482 🥳 21 ⏱️ 0:04:06.360551

📜 1 sessions
💰 score: 9500

    6/6
    TARES 🟨⬜⬜⬜🟨
    SOUTH 🟩🟨⬜🟨⬜
    STONY 🟩🟩🟩⬜⬜
    STOCK 🟩🟩🟩⬜⬜
    STOMP 🟩🟩🟩⬜🟩
    STOOP 🟩🟩🟩🟩🟩
    4/6
    STOOP ⬜⬜⬜⬜⬜
    ANILE 🟨🟨🟨⬜⬜
    NICAD 🟨🟨⬜🟨⬜
    GRAIN 🟩🟩🟩🟩🟩
    4/6
    GRAIN ⬜⬜⬜🟨⬜
    BIELD ⬜🟨🟨🟨⬜
    IMPEL 🟨⬜⬜🟨🟨
    OLIVE 🟩🟩🟩🟩🟩
    5/6
    OLIVE ⬜🟩⬜⬜🟨
    SLEPT ⬜🟩🟨⬜⬜
    CLUED ⬜🟩🟩🟩⬜
    BLUEY 🟩🟩🟩🟩⬜
    BLUER 🟩🟩🟩🟩🟩
    Final 2/2
    HUNKY 🟩🟩🟩⬜⬜
    HUNCH 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1459 🥳 score:26 ⏱️ 0:01:56.400121

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. FRONT attempts:4 score:4
2. QUOTE attempts:5 score:5
3. RAISE attempts:9 score:9
4. POKER attempts:8 score:8

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1459 🥳 score:53 ⏱️ 0:03:41.128235

📜 1 sessions

Octordle Classic

1. ELFIN attempts:9 score:9
2. BROOM attempts:11 score:11
3. SHELF attempts:8 score:8
4. TRIED attempts:3 score:3
5. CREEK attempts:6 score:6
6. KOALA attempts:7 score:7
7. WRITE attempts:4 score:4
8. TIGHT attempts:5 score:5

# [squareword.org](squareword.org) 🧩 #1452 🥳 8 ⏱️ 0:02:54.896359

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟩 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟨 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P E C S
    H A V O C
    A P A C E
    R A D O N
    P L E A T

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1389 🥳 289 ⏱️ 0:05:15.192250

🤔 290 attempts
📜 2 sessions
🫧 12 chat sessions
⁉️ 60 chat prompts
🤖 60 dolphin3:latest replies
🔥   2 🥵   9 😎  22 🥶 241 🧊  15

      $1 #290   ~1 buck             100.00°C 🥳 1000‰
      $2 #231  ~10 deer              38.17°C 🔥  996‰
      $3 #171  ~22 bull              37.13°C 🔥  993‰
      $4 #260   ~7 elk               35.56°C 🥵  987‰
      $5 #257   ~8 antler            35.26°C 🥵  986‰
      $6 #271   ~6 antlered          35.01°C 🥵  984‰
      $7 #108  ~30 prey              31.04°C 🥵  963‰
      $8 #228  ~11 hunting           30.46°C 🥵  954‰
      $9 #193  ~18 cow               30.28°C 🥵  949‰
     $10 #115  ~28 scapegoat         30.04°C 🥵  944‰
     $11 #286   ~3 fawn              29.43°C 🥵  935‰
     $13 #197  ~16 porterhouse       27.56°C 😎  881‰
     $35 #131      bully             20.66°C 🥶
    $276 #148      rage              -0.02°C 🧊

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1422 🥳 623 ⏱️ 0:18:12.434350

🤔 624 attempts
📜 1 sessions
🫧 49 chat sessions
⁉️ 239 chat prompts
🤖 239 dolphin3:latest replies
😱   1 🔥   6 🥵  25 😎 174 🥶 339 🧊  78

      $1 #624   ~1 demandeur            100.00°C 🥳 1000‰
      $2 #609  ~10 demande               60.07°C 😱  999‰
      $3  #42 ~200 emploi                58.74°C 🔥  997‰
      $4  #45 ~197 employeur             51.75°C 🔥  996‰
      $5 #114 ~154 insertion             50.52°C 🔥  995‰
      $6  #41 ~201 chômeur               47.83°C 🔥  994‰
      $7 #255 ~103 qualification         47.04°C 🔥  991‰
      $8  #48 ~195 salarié               45.89°C 🔥  990‰
      $9  #52 ~192 formation             45.58°C 🥵  989‰
     $10 #553  ~19 reclassement          45.00°C 🥵  988‰
     $11  #83 ~175 professionnel         44.74°C 🥵  987‰
     $34 #540  ~24 inscription           34.63°C 😎  899‰
    $208  #79      entretien             20.28°C 🥶
    $547 #322      solide                -0.10°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #73 🥳 score:25 ⏱️ 0:01:40.800278

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. FEMUR attempts:4 score:4
2. SNACK attempts:6 score:6
3. ANIME attempts:7 score:7
4. POOCH attempts:8 score:8

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1459 🥳 score:9 ⏱️ 0:04:38.294487

📜 2 sessions

Octordle Rescue

1. AWAKE attempts:9 score:9
2. NINJA attempts:12 score:12
3. WINCH attempts:5 score:5
4. CHEAT attempts:6 score:6
5. BISON attempts:8 score:8
6. STORK attempts:10 score:10
7. EYING attempts:11 score:11
8. MAGMA attempts:7 score:7
