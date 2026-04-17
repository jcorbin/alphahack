# 2026-04-18

- 🔗 spaceword.org 🧩 2026-04-17 🏁 score 2173 ranked 4.9% 17/350 ⏱️ 3:02:06.142810
- 🔗 alfagok.diginaut.net 🧩 #532 🥳 36 ⏱️ 0:00:34.534993
- 🔗 alphaguess.com 🧩 #999 🥳 26 ⏱️ 0:00:26.351142
- 🔗 dontwordle.com 🧩 #1425 🥳 6 ⏱️ 0:02:13.831048
- 🔗 dictionary.com hurdle 🧩 #1568 😦 6 ⏱️ 0:01:35.999429
- 🔗 Quordle Classic 🧩 #1545 🥳 score:19 ⏱️ 0:01:24.087314
- 🔗 Octordle Classic 🧩 #1545 🥳 score:64 ⏱️ 0:03:55.416405
- 🔗 squareword.org 🧩 #1538 🥳 7 ⏱️ 0:01:20.798768
- 🔗 cemantle.certitudes.org 🧩 #1475 🥳 12 ⏱️ 0:00:10.597006
- 🔗 cemantix.certitudes.org 🧩 #1508 🥳 104 ⏱️ 0:01:30.782666

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
















































# [spaceword.org](spaceword.org) 🧩 2026-04-17 🏁 score 2173 ranked 4.9% 17/350 ⏱️ 3:02:06.142810

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 17/350

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ V _ Q I _ _ F _ B   
      _ O _ I R O N I Z E   
      _ E A S E F U L _ L   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #532 🥳 36 ⏱️ 0:00:34.534993

🤔 36 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+24910  [ 24910] bad        q12 ? ␅
    @+24910  [ 24910] bad        q13 ? after
    @+37372  [ 37372] beschermen q14 ? ␅
    @+37372  [ 37372] beschermen q15 ? after
    @+43061  [ 43061] bij        q16 ? ␅
    @+43061  [ 43061] bij        q17 ? after
    @+46449  [ 46449] blief      q18 ? ␅
    @+46449  [ 46449] blief      q19 ? after
    @+48140  [ 48140] bobslee    q20 ? ␅
    @+48140  [ 48140] bobslee    q21 ? after
    @+48593  [ 48593] boek       q22 ? ␅
    @+48593  [ 48593] boek       q23 ? after
    @+48894  [ 48894] boekhoud   q26 ? ␅
    @+48894  [ 48894] boekhoud   q27 ? after
    @+49051  [ 49051] boekversie q28 ? ␅
    @+49051  [ 49051] boekversie q29 ? after
    @+49121  [ 49121] boemel     q30 ? ␅
    @+49121  [ 49121] boemel     q31 ? after
    @+49160  [ 49160] boer       q32 ? ␅
    @+49160  [ 49160] boer       q33 ? after
    @+49167  [ 49167] boerderij  q34 ? ␅
    @+49167  [ 49167] boerderij  q35 ? it
    @+49167  [ 49167] boerderij  done. it
    @+49205  [ 49205] boeren     q24 ? ␅
    @+49205  [ 49205] boeren     q25 ? before
    @+49840  [ 49840] boks       q10 ? ␅
    @+49840  [ 49840] boks       q11 ? before
    @+99736  [ 99736] ex         q8  ? ␅
    @+99736  [ 99736] ex         q9  ? before
    @+199605 [199605] lij        q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #999 🥳 26 ⏱️ 0:00:26.351142

🤔 26 attempts
📜 1 sessions

    @       [    0] aa     
    @+1     [    1] aah    
    @+2     [    2] aahed  
    @+3     [    3] aahing 
    @+47380 [47380] dis    q2  ? ␅
    @+47380 [47380] dis    q3  ? after
    @+72798 [72798] gremmy q4  ? ␅
    @+72798 [72798] gremmy q5  ? after
    @+74359 [74359] had    q12 ? ␅
    @+74359 [74359] had    q13 ? after
    @+75051 [75051] hand   q14 ? ␅
    @+75051 [75051] hand   q15 ? after
    @+75444 [75444] hard   q16 ? ␅
    @+75444 [75444] hard   q17 ? after
    @+75693 [75693] harsh  q18 ? ␅
    @+75693 [75693] harsh  q19 ? after
    @+75785 [75785] hat    q20 ? ␅
    @+75785 [75785] hat    q21 ? after
    @+75823 [75823] hate   q24 ? ␅
    @+75823 [75823] hate   q25 ? it
    @+75823 [75823] hate   done. it
    @+75869 [75869] haul   q22 ? ␅
    @+75869 [75869] haul   q23 ? before
    @+75954 [75954] haw    q10 ? ␅
    @+75954 [75954] haw    q11 ? before
    @+79130 [79130] hood   q8  ? ␅
    @+79130 [79130] hood   q9  ? before
    @+85502 [85502] ins    q6  ? ␅
    @+85502 [85502] ins    q7  ? before
    @+98216 [98216] mach   q0  ? ␅
    @+98216 [98216] mach   q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1425 🥳 6 ⏱️ 0:02:13.831048

📜 1 sessions
💰 score: 63

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MAMMA n n n n n remain:6571
    ⬜⬜⬜⬜⬜ tried:ICTIC n n n n n remain:2707
    ⬜⬜⬜⬜⬜ tried:YUPPY n n n n n remain:1155
    ⬜🟨⬜⬜⬜ tried:GRRRL n m n n n remain:108
    ⬜🟩⬜⬜🟩 tried:DONOR n Y n n Y remain:10
    ⬜🟩⬜🟩🟩 tried:HOVER n Y n Y Y remain:7

    Undos used: 3

      7 words remaining
    x 9 unused letters
    = 63 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1568 😦 6 ⏱️ 0:01:35.999429

📜 1 sessions
💰 score: 80

    6/6
    ????? 🟨⬜🟨⬜⬜
    ????? 🟨⬜🟩🟨⬜
    ????? 🟨⬜🟩🟩🟩
    ????? ⬜🟩🟩🟩🟩
    ????? ⬜🟩🟩🟩🟩
    ????? ⬜🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1545 🥳 score:19 ⏱️ 0:01:24.087314

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. STEAL attempts:2 score:2
2. CURIO attempts:6 score:6
3. SCOOP attempts:7 score:7
4. BETEL attempts:4 score:4

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1545 🥳 score:64 ⏱️ 0:03:55.416405

📜 2 sessions

Octordle Classic

1. MOTOR attempts:11 score:11
2. KNOCK attempts:12 score:12
3. GRAFT attempts:5 score:5
4. DODGE attempts:3 score:3
5. STRAY attempts:10 score:10
6. MELEE attempts:9 score:9
7. PARSE attempts:6 score:6
8. FORTY attempts:8 score:8

# [squareword.org](squareword.org) 🧩 #1538 🥳 7 ⏱️ 0:01:20.798768

📜 2 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟩 🟩 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C R I S P
    H E N N A
    A L T E R
    T I R E S
    S C O R E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1475 🥳 12 ⏱️ 0:00:10.597006

🤔 13 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 3 chat prompts
🤖 3 dolphin3:latest replies
🔥 1 🥵 1 😎 1 🥶 9

     $1 #13 fruit      100.00°C 🥳 1000‰ ~13 used:0 [12]  source:dolphin3
     $2 #11 apple       64.10°C 🔥  997‰  ~1 used:0 [0]   source:dolphin3
     $3  #1 banana      52.22°C 🥵  965‰  ~2 used:1 [1]   source:dolphin3
     $4  #3 chocolate   40.93°C 😎  778‰  ~3 used:0 [2]   source:dolphin3
     $5  #7 oxygen      14.79°C 🥶        ~4 used:0 [3]   source:dolphin3
     $6  #2 bicycle     14.10°C 🥶        ~5 used:0 [4]   source:dolphin3
     $7 #10 volcano     13.40°C 🥶        ~6 used:0 [5]   source:dolphin3
     $8  #4 cloud       12.35°C 🥶        ~7 used:0 [6]   source:dolphin3
     $9 #12 computer     8.70°C 🥶        ~8 used:0 [7]   source:dolphin3
    $10  #9 symphony     6.90°C 🥶        ~9 used:0 [8]   source:dolphin3
    $11  #6 orchestra    6.11°C 🥶       ~10 used:0 [9]   source:dolphin3
    $12  #8 quantum      5.14°C 🥶       ~11 used:0 [10]  source:dolphin3
    $13  #5 internet     3.99°C 🥶       ~12 used:0 [11]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1508 🥳 104 ⏱️ 0:01:30.782666

🤔 105 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 17 chat prompts
🤖 17 dolphin3:latest replies
😱  1 🔥  1 🥵  7 😎 30 🥶 49 🧊 16

      $1 #105 continuité       100.00°C 🥳 1000‰  ~89 used:0 [88]   source:dolphin3
      $2 #102 cohérence         60.26°C 😱  999‰   ~1 used:2 [0]    source:dolphin3
      $3  #90 homogénéité       47.53°C 🔥  994‰   ~2 used:9 [1]    source:dolphin3
      $4  #85 cohésion          39.57°C 🥵  966‰   ~7 used:5 [6]    source:dolphin3
      $5  #94 homogène          38.37°C 🥵  957‰   ~3 used:0 [2]    source:dolphin3
      $6  #99 équilibre         37.80°C 🥵  943‰   ~4 used:0 [3]    source:dolphin3
      $7  #51 objectif          37.64°C 🥵  940‰   ~9 used:8 [8]    source:dolphin3
      $8  #84 hétérogénéité     36.46°C 🥵  921‰   ~8 used:5 [7]    source:dolphin3
      $9  #60 diversité         36.32°C 🥵  919‰   ~6 used:3 [5]    source:dolphin3
     $10  #92 multiplicité      35.53°C 🥵  903‰   ~5 used:1 [4]    source:dolphin3
     $11  #50 intégration       35.27°C 😎  897‰  ~37 used:2 [36]   source:dolphin3
     $12  #88 convergence       35.25°C 😎  895‰  ~10 used:0 [9]    source:dolphin3
     $41  #52 professionnel     24.35°C 🥶        ~41 used:0 [40]   source:dolphin3
     $90  #47 goal              -2.31°C 🧊        ~90 used:0 [89]   source:dolphin3
