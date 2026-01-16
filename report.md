# 2026-01-17

- 🔗 spaceword.org 🧩 2026-01-16 🏁 score 2173 ranked 10.5% 35/334 ⏱️ 0:12:50.433977
- 🔗 alfagok.diginaut.net 🧩 #441 🥳 12 ⏱️ 0:00:30.500886
- 🔗 alphaguess.com 🧩 #908 🥳 10 ⏱️ 0:00:27.496937
- 🔗 dictionary.com hurdle 🧩 #1477 🥳 18 ⏱️ 0:03:33.307374
- 🔗 Quordle Classic 🧩 #1454 🥳 score:25 ⏱️ 0:01:48.818413
- 🔗 dontwordle.com 🧩 #1334 🥳 6 ⏱️ 0:04:48.579254
- 🔗 Octordle Classic 🧩 #1454 🥳 score:62 ⏱️ 0:03:56.603545
- 🔗 squareword.org 🧩 #1447 🥳 8 ⏱️ 0:02:42.423498
- 🔗 cemantle.certitudes.org 🧩 #1384 🥳 401 ⏱️ 0:06:58.132684
- 🔗 cemantix.certitudes.org 🧩 #1417 🥳 22 ⏱️ 0:01:48.032818
- 🔗 Quordle Rescue 🧩 #68 🥳 score:27 ⏱️ 0:01:30.726606

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


# [spaceword.org](spaceword.org) 🧩 2026-01-16 🏁 score 2173 ranked 10.5% 35/334 ⏱️ 0:12:50.433977

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 35/334

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ T O _ T A L K I E   
      _ W I F E _ _ _ _ L   
      _ O _ E C Z E M A S   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #441 🥳 12 ⏱️ 0:00:30.500886

🤔 12 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+49849  [ 49849] boks      q2  ? after
    @+51256  [ 51256] boots     q7  ? after
    @+51332  [ 51332] bord      q11 ? it
    @+51332  [ 51332] bord      done. it
    @+51545  [ 51545] bornput   q10 ? before
    @+51833  [ 51833] bos       q8  ? before
    @+52690  [ 52690] bouw      q6  ? before
    @+55940  [ 55940] bron      q5  ? before
    @+62287  [ 62287] cement    q4  ? before
    @+74761  [ 74761] dc        q3  ? before
    @+99757  [ 99757] ex        q1  ? before
    @+199832 [199832] lijm      q0  ? before

# [alphaguess.com](alphaguess.com) 🧩 #908 🥳 10 ⏱️ 0:00:27.496937

🤔 10 attempts
📜 1 sessions

    @        [     0] aa      
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98220  [ 98220] mach    q0  ? after
    @+147373 [147373] rhotic  q1  ? after
    @+159490 [159490] slop    q3  ? after
    @+162477 [162477] spec    q5  ? after
    @+162637 [162637] speed   q9  ? it
    @+162637 [162637] speed   done. it
    @+162845 [162845] spheric q8  ? before
    @+163213 [163213] spit    q7  ? before
    @+164003 [164003] squab   q6  ? before
    @+165532 [165532] stick   q4  ? before
    @+171643 [171643] ta      q2  ? before

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1477 🥳 18 ⏱️ 0:03:33.307374

📜 1 sessions
💰 score: 9800

    6/6
    STARE 🟨🟨🟨⬜⬜
    TAILS 🟨🟩⬜⬜🟨
    PASTY ⬜🟩🟩🟩🟩
    NASTY ⬜🟩🟩🟩🟩
    VASTY ⬜🟩🟩🟩🟩
    HASTY 🟩🟩🟩🟩🟩
    5/6
    HASTY ⬜🟨⬜🟩⬜
    OVATE 🟨⬜🟨🟩⬜
    QUOTA ⬜⬜🟨🟩🟩
    GOTTA ⬜🟩⬜🟩🟩
    AORTA 🟩🟩🟩🟩🟩
    4/6
    AORTA ⬜⬜⬜⬜⬜
    FLIPS ⬜⬜⬜⬜🟨
    SHEND 🟨⬜🟩⬜⬜
    GEESE 🟩🟩🟩🟩🟩
    2/6
    GEESE 🟩🟨⬜⬜⬜
    GAVEL 🟩🟩🟩🟩🟩
    Final 1/2
    EMPTY 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1454 🥳 score:25 ⏱️ 0:01:48.818413

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. ROAST attempts:3 score:3
2. FOLIO attempts:8 score:8
3. DROLL attempts:5 score:5
4. PROVE attempts:9 score:9

# [dontwordle.com](dontwordle.com) 🧩 #1334 🥳 6 ⏱️ 0:04:48.579254

📜 2 sessions
💰 score: 9

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:JNANA n n n n n remain:5846
    ⬜⬜⬜⬜⬜ tried:MOTTO n n n n n remain:2128
    ⬜⬜⬜⬜⬜ tried:SUDDS n n n n n remain:455
    ⬜⬜🟨⬜⬜ tried:GHYLL n n m n n remain:61
    🟩🟩⬜⬜🟩 tried:FIZZY Y Y n n Y remain:2
    🟩🟩⬜🟩🟩 tried:FIRRY Y Y n Y Y remain:1

    Undos used: 5

      1 words remaining
    x 9 unused letters
    = 9 total score

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1454 🥳 score:62 ⏱️ 0:03:56.603545

📜 1 sessions

Octordle Classic

1. BATTY attempts:12 score:12
2. EGRET attempts:6 score:6
3. WAXEN attempts:9 score:9
4. MAMMA attempts:13 score:13
5. APTLY attempts:3 score:3
6. RANCH attempts:4 score:4
7. GUIDE attempts:7 score:7
8. SHARK attempts:8 score:8

# [squareword.org](squareword.org) 🧩 #1447 🥳 8 ⏱️ 0:02:42.423498

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P U R T
    T A S E R
    O L I V E
    V E N U E
    E D G E S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1384 🥳 401 ⏱️ 0:06:58.132684

🤔 402 attempts
📜 1 sessions
🫧 19 chat sessions
⁉️ 97 chat prompts
🤖 97 dolphin3:latest replies
🔥   3 🥵  21 😎  83 🥶 283 🧊  11

      $1 #402   ~1 dental             100.00°C 🥳 1000‰
      $2 #386   ~8 dentist             66.43°C 🔥  997‰
      $3  #83  ~82 medical             56.76°C 🔥  992‰
      $4 #361  ~16 chiropractic        56.07°C 🔥  990‰
      $5 #401   ~2 denture             55.24°C 🥵  989‰
      $6  #36 ~103 health              49.27°C 🥵  977‰
      $7 #259  ~49 surgical            49.02°C 🥵  976‰
      $8  #59  ~93 physician           47.30°C 🥵  969‰
      $9  #35 ~104 healthcare          46.56°C 🥵  964‰
     $10  #44 ~101 doctor              43.99°C 🥵  955‰
     $11 #246  ~57 diagnostic          43.79°C 🥵  954‰
     $27 #363  ~15 occupational        37.90°C 😎  898‰
    $109 #281      cervix              23.21°C 🥶
    $392 #313      control             -0.20°C 🧊

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1417 🥳 22 ⏱️ 0:01:48.032818

🤔 23 attempts
📜 1 sessions
🫧 1 chat sessions
⁉️ 5 chat prompts
🤖 5 dolphin3:latest replies
🔥 1 🥵 1 😎 5 🥶 7 🧊 8

     $1 #23  ~1 bombardement  100.00°C 🥳 1000‰
     $2 #21  ~2 artillerie     47.92°C 🔥  991‰
     $3 #20  ~3 munition       39.40°C 🥵  939‰
     $4 #15  ~7 grenade        32.09°C 😎  819‰
     $5 #17  ~5 canon          28.69°C 😎  674‰
     $6  #9  ~8 sapeur         26.45°C 😎  538‰
     $7 #18  ~4 explosif       26.44°C 😎  535‰
     $8 #16  ~6 artificier     24.10°C 😎  360‰
     $9 #22     batterie       16.35°C 🥶
    $10 #19     maraudeur      10.80°C 🥶
    $11 #11     étoile          6.29°C 🥶
    $12 #14     extincteur      4.91°C 🥶
    $13 #13     casque          3.68°C 🥶
    $16  #1     bain           -0.54°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #68 🥳 score:27 ⏱️ 0:01:30.726606

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. THORN attempts:4 score:4
2. ANNOY attempts:6 score:6
3. PUFFY attempts:9 score:9
4. JAZZY attempts:8 score:8
