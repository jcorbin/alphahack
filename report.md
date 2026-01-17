# 2026-01-18

- 🔗 spaceword.org 🧩 2026-01-17 🏁 score 2168 ranked 49.1% 156/318 ⏱️ 0:22:32.119844
- 🔗 alfagok.diginaut.net 🧩 #442 🥳 25 ⏱️ 0:00:54.492227
- 🔗 alphaguess.com 🧩 #909 🥳 14 ⏱️ 0:00:33.153143
- 🔗 dontwordle.com 🧩 #1335 🥳 6 ⏱️ 0:03:29.299763
- 🔗 dictionary.com hurdle 🧩 #1478 🥳 14 ⏱️ 0:02:49.118087
- 🔗 Quordle Classic 🧩 #1455 😦 score:29 ⏱️ 0:02:01.554943
- 🔗 Octordle Classic 🧩 #1455 🥳 score:59 ⏱️ 0:03:30.141624
- 🔗 squareword.org 🧩 #1448 🥳 7 ⏱️ 0:02:04.782780
- 🔗 cemantle.certitudes.org 🧩 #1385 🥳 27 ⏱️ 0:00:55.799370
- 🔗 cemantix.certitudes.org 🧩 #1418 🥳 371 ⏱️ 0:11:29.393105
- 🔗 Quordle Rescue 🧩 #69 🥳 score:22 ⏱️ 0:02:36.254813
- 🔗 Octordle Rescue 🧩 #1455 🥳 score:8 ⏱️ 0:04:33.757051

# Dev

## WIP

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



# [spaceword.org](spaceword.org) 🧩 2026-01-17 🏁 score 2168 ranked 49.1% 156/318 ⏱️ 0:22:32.119844

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 156/318

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ C _ _ _ _ _ _ W _   
      _ O _ O P A Q U E _   
      _ Z O R I L _ _ T _   
      _ _ _ E N E M A S _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #442 🥳 25 ⏱️ 0:00:54.492227

🤔 25 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199833 [199833] lijm      q0  ? after
    @+299738 [299738] schub     q1  ? after
    @+299738 [299738] schub     q2  ? after
    @+311908 [311908] spier     q5  ? after
    @+314617 [314617] st        q6  ? after
    @+316832 [316832] start     q8  ? after
    @+317320 [317320] stee      q10 ? after
    @+317475 [317475] steen     q11 ? after
    @+317794 [317794] steg      q16 ? after
    @+317894 [317894] stek      q17 ? after
    @+317970 [317970] stel      q18 ? after
    @+317995 [317995] stellage  q22 ? after
    @+318000 [318000] stellen   q24 ? it
    @+318000 [318000] stellen   done. it
    @+318006 [318006] stellers  q23 ? before
    @+318017 [318017] stelling  q19 ? before
    @+318105 [318105] stem      q9  ? before
    @+319405 [319405] stik      q7  ? before
    @+324308 [324308] sub       q4  ? before
    @+349515 [349515] vakantie  q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #909 🥳 14 ⏱️ 0:00:33.153143

🤔 14 attempts
📜 1 sessions

    @        [     0] aa     
    @+1      [     1] aah    
    @+2      [     2] aahed  
    @+3      [     3] aahing 
    @+98220  [ 98220] mach   q0  ? after
    @+147373 [147373] rhotic q1  ? after
    @+171643 [171643] ta     q2  ? after
    @+174192 [174192] term   q5  ? after
    @+175500 [175500] thrash q6  ? after
    @+175823 [175823] thunk  q8  ? after
    @+175947 [175947] tick   q9  ? after
    @+175953 [175953] ticket q13 ? it
    @+175953 [175953] ticket done. it
    @+175962 [175962] tickle q12 ? before
    @+175991 [175991] tictac q11 ? before
    @+176041 [176041] tie    q10 ? before
    @+176149 [176149] till   q7  ? before
    @+176814 [176814] toil   q4  ? before
    @+182008 [182008] un     q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1335 🥳 6 ⏱️ 0:03:29.299763

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:POOPY n n n n n remain:6473
    ⬜⬜⬜⬜⬜ tried:JUJUS n n n n n remain:2436
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:753
    ⬜⬜🟨⬜⬜ tried:CHICK n n m n n remain:154
    ⬜⬜⬜🟩⬜ tried:FIXIT n n n Y n remain:16
    ⬜🟩⬜🟩⬜ tried:NEWIE n Y n Y n remain:2

    Undos used: 4

      2 words remaining
    x 7 unused letters
    = 14 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1478 🥳 14 ⏱️ 0:02:49.118087

📜 1 sessions
💰 score: 10200

    4/6
    STALE ⬜⬜⬜🟨🟨
    IDLER ⬜⬜🟩🟨⬜
    MELON ⬜🟩🟩⬜⬜
    BELCH 🟩🟩🟩🟩🟩
    3/6
    BELCH 🟩🟩⬜⬜⬜
    BEATS 🟩🟩🟩🟨🟨
    BEAST 🟩🟩🟩🟩🟩
    3/6
    BEAST ⬜⬜🟨⬜🟨
    ACTOR 🟨⬜🟩🟨⬜
    PATIO 🟩🟩🟩🟩🟩
    2/6
    PATIO ⬜🟨⬜🟩🟨
    AVOID 🟩🟩🟩🟩🟩
    Final 2/2
    YEARN 🟨🟩🟩🟩⬜
    WEARY 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1455 😦 score:29 ⏱️ 0:02:01.554943

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. BATTY attempts:7 score:7
2. TWINE attempts:5 score:5
3. DEBUT attempts:8 score:8
4. TAL_Y -BCDEFGIKMNOPRSUW attempts:9 score:-1

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1455 🥳 score:59 ⏱️ 0:03:30.141624

📜 1 sessions

Octordle Classic

1. STAID attempts:6 score:6
2. TOOTH attempts:8 score:8
3. THROW attempts:9 score:9
4. UNMET attempts:5 score:5
5. PARKA attempts:10 score:10
6. EARLY attempts:3 score:3
7. TODAY attempts:7 score:7
8. PRISM attempts:11 score:11

# [squareword.org](squareword.org) 🧩 #1448 🥳 7 ⏱️ 0:02:04.782780

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S A B E R
    E L I D E
    D O N G A
    A N G E R
    N E E D S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1385 🥳 27 ⏱️ 0:00:55.799370

🤔 28 attempts
📜 1 sessions
🫧 1 chat sessions
⁉️ 6 chat prompts
🤖 6 dolphin3:latest replies
🔥  1 🥵  5 😎  5 🥶 14 🧊  2

     $1 #28  ~1 orbit          100.00°C 🥳 1000‰
     $2 #24  ~4 orbital         63.82°C 🔥  997‰
     $3 #19  ~7 shuttle         52.69°C 🥵  985‰
     $4 #13 ~11 astronaut       52.57°C 🥵  984‰
     $5 #26  ~2 geostationary   50.87°C 🥵  979‰
     $6 #10 ~12 rocket          45.96°C 🥵  969‰
     $7 #17  ~9 mission         38.12°C 🥵  912‰
     $8 #25  ~3 altitude        33.62°C 😎  849‰
     $9 #22  ~6 docking         32.99°C 😎  837‰
    $10 #23  ~5 launch          26.16°C 😎  577‰
    $11 #15 ~10 exploration     24.90°C 😎  480‰
    $12 #18  ~8 moonwalk        21.56°C 😎   31‰
    $13 #21     cargo           21.16°C 🥶
    $27  #8     guitar          -0.96°C 🧊

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1418 🥳 371 ⏱️ 0:11:29.393105

🤔 372 attempts
📜 1 sessions
🫧 31 chat sessions
⁉️ 111 chat prompts
🤖 111 dolphin3:latest replies
😱   1 🔥   3 🥵  15 😎  66 🥶 252 🧊  34

      $1 #372   ~1 rompre           100.00°C 🥳 1000‰
      $2 #261  ~23 rupture           59.39°C 😱  999‰
      $3  #55  ~81 renoncer          42.28°C 🔥  994‰
      $4 #365   ~5 disloquer         41.49°C 🔥  993‰
      $5  #57  ~80 défaire           39.80°C 🔥  990‰
      $6  #69  ~77 refuser           37.30°C 🥵  985‰
      $7  #48  ~84 abandonner        37.25°C 🥵  984‰
      $8  #93  ~67 opposer           36.90°C 🥵  983‰
      $9 #246  ~26 affaiblir         36.72°C 🥵  982‰
     $10 #111  ~59 dénouer           35.51°C 🥵  977‰
     $11 #192  ~42 compromettre      34.96°C 🥵  971‰
     $21 #149  ~52 alliance          31.53°C 😎  899‰
     $87 #140      dénaturer         23.55°C 🥶
    $339   #3      gâteau            -0.34°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #69 🥳 score:22 ⏱️ 0:02:36.254813

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. ATONE attempts:6 score:6
2. SLURP attempts:4 score:4
3. UPSET attempts:5 score:5
4. JAUNT attempts:7 score:7

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1455 🥳 score:8 ⏱️ 0:04:33.757051

📜 2 sessions

Octordle Rescue

1. DRAIN attempts:7 score:7
2. GULLY attempts:13 score:13
3. PRONG attempts:5 score:5
4. LARVA attempts:10 score:10
5. SPOIL attempts:6 score:6
6. AUDIT attempts:8 score:8
7. SUAVE attempts:9 score:9
8. CLOWN attempts:12 score:12
