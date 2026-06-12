# 2026-06-13

- 🔗 spaceword.org 🧩 2026-06-12 🏁 score 2168 ranked 37.9% 120/317 ⏱️ 20:48:47.325072
- 🔗 alfagok.diginaut.net 🧩 #588 🥳 40 ⏱️ 0:00:47.344944
- 🔗 alphaguess.com 🧩 #1055 🥳 28 ⏱️ 0:00:27.455605
- 🔗 dontwordle.com 🧩 #1481 🥳 6 ⏱️ 0:01:22.264129
- 🔗 dictionary.com hurdle 🧩 #1624 😦 20 ⏱️ 0:03:07.066186
- 🔗 Quordle Classic 🧩 #1601 🥳 score:19 ⏱️ 0:01:01.809436
- 🔗 Octordle Classic 🧩 #1601 🥳 score:52 ⏱️ 0:02:26.865323
- 🔗 squareword.org 🧩 #1594 🥳 7 ⏱️ 0:01:40.783492
- 🔗 cemantle.certitudes.org 🧩 #1531 🥳 1037 ⏱️ 0:14:47.510617
- 🔗 cemantix.certitudes.org 🧩 #1564 🥳 105 ⏱️ 0:01:37.604754

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




# [spaceword.org](spaceword.org) 🧩 2026-06-12 🏁 score 2168 ranked 37.9% 120/317 ⏱️ 20:48:47.325072

📜 2 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 120/317

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ N I G H _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ _ _ J O _ _ _   
      _ _ _ _ O A F _ _ _   
      _ _ _ _ _ R E _ _ _   
      _ _ _ K E I R _ _ _   
      _ _ _ _ _ N _ _ _ _   
      _ _ _ Q U A D _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #588 🥳 40 ⏱️ 0:00:47.344944

🤔 40 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+99704  [ 99704] ex          q2  ? ␅
    @+99704  [ 99704] ex          q3  ? after
    @+149392 [149392] huis        q4  ? ␅
    @+149392 [149392] huis        q5  ? after
    @+151438 [151438] hypotheek   q12 ? ␅
    @+151438 [151438] hypotheek   q13 ? after
    @+151665 [151665] ic          q16 ? ␅
    @+151665 [151665] ic          q17 ? after
    @+151979 [151979] id          q18 ? ␅
    @+151979 [151979] id          q19 ? after
    @+152079 [152079] identiteit  q22 ? ␅
    @+152079 [152079] identiteit  q23 ? after
    @+152147 [152147] idiomatisch q26 ? ␅
    @+152147 [152147] idiomatisch q27 ? after
    @+152182 [152182] idylle      q32 ? ␅
    @+152182 [152182] idylle      q33 ? after
    @+152192 [152192] ie          q34 ? ␅
    @+152192 [152192] ie          q35 ? after
    @+152195 [152195] ieder       q38 ? ␅
    @+152195 [152195] ieder       q39 ? it
    @+152195 [152195] ieder       done. it
    @+152202 [152202] iek         q36 ? ␅
    @+152202 [152202] iek         q37 ? before
    @+152212 [152212] iep         q20 ? ␅
    @+152212 [152212] iep         q21 ? before
    @+152484 [152484] ijshockey   q14 ? ␅
    @+152484 [152484] ijshockey   q15 ? before
    @+153560 [153560] in          q10 ? ␅
    @+153560 [153560] in          q11 ? before
    @+161944 [161944] izabel      q9  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1055 🥳 28 ⏱️ 0:00:27.455605

🤔 28 attempts
📜 1 sessions

    @       [    0] aa        
    @+2     [    2] aahed     
    @+11763 [11763] back      q6  ? ␅
    @+11763 [11763] back      q7  ? after
    @+12178 [12178] baff      q14 ? ␅
    @+12178 [12178] baff      q15 ? after
    @+12333 [12333] bal       q16 ? ␅
    @+12333 [12333] bal       q17 ? after
    @+12430 [12430] ball      q18 ? ␅
    @+12430 [12430] ball      q19 ? after
    @+12471 [12471] ballgames q22 ? ␅
    @+12471 [12471] ballgames q23 ? after
    @+12491 [12491] ballon    q24 ? ␅
    @+12491 [12491] ballon    q25 ? after
    @+12497 [12497] balloon   q26 ? ␅
    @+12497 [12497] balloon   q27 ? it
    @+12497 [12497] balloon   done. it
    @+12511 [12511] ballpark  q20 ? ␅
    @+12511 [12511] ballpark  q21 ? before
    @+12597 [12597] ban       q12 ? ␅
    @+12597 [12597] ban       q13 ? before
    @+13801 [13801] be        q10 ? ␅
    @+13801 [13801] be        q11 ? before
    @+17714 [17714] blind     q8  ? ␅
    @+17714 [17714] blind     q9  ? before
    @+23681 [23681] camp      q4  ? ␅
    @+23681 [23681] camp      q5  ? before
    @+47380 [47380] dis       q2  ? ␅
    @+47380 [47380] dis       q3  ? before
    @+98214 [98214] mach      q0  ? ␅
    @+98214 [98214] mach      q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1481 🥳 6 ⏱️ 0:01:22.264129

📜 1 sessions
💰 score: 16

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:KEEVE n n n n n remain:6101
    ⬜⬜⬜⬜⬜ tried:SUDDS n n n n n remain:1895
    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:765
    ⬜⬜⬜⬜⬜ tried:COOCH n n n n n remain:149
    🟨⬜⬜⬜⬜ tried:GRRRL m n n n n remain:13
    ⬜🟩🟨⬜⬜ tried:PYGMY n Y m n n remain:2

    Undos used: 3

      2 words remaining
    x 8 unused letters
    = 16 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1624 😦 20 ⏱️ 0:03:07.066186

📜 1 sessions
💰 score: 4660

    4/6
    STOAE 🟩🟨⬜🟨⬜
    SALUT 🟩🟨⬜⬜🟩
    SCART 🟩⬜🟩🟩🟩
    SMART 🟩🟩🟩🟩🟩
    4/6
    SMART ⬜🟨🟩🟩⬜
    INARM ⬜⬜🟩🟩🟩
    CHARM ⬜⬜🟩🟩🟩
    REARM 🟩🟩🟩🟩🟩
    5/6
    REARM ⬜⬜⬜⬜⬜
    LINOS 🟩🟩⬜⬜⬜
    LICHT 🟩🟩⬜⬜⬜
    LIPID 🟩🟩⬜🟩🟩
    LIVID 🟩🟩🟩🟩🟩
    5/6
    LIVID ⬜⬜⬜⬜⬜
    AROSE ⬜⬜⬜⬜🟨
    HYMEN ⬜🟨⬜🟨⬜
    PICKY 🟩⬜⬜⬜🟩
    PETTY 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜🟩🟩⬜⬜
    ????? ⬜🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1601 🥳 score:19 ⏱️ 0:01:01.809436

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. DEALT attempts:3 score:3
2. STEED attempts:4 score:4
3. BELIE attempts:5 score:5
4. GULLY attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1601 🥳 score:52 ⏱️ 0:02:26.865323

📜 1 sessions

Octordle Classic

1. FORUM attempts:5 score:5
2. BADLY attempts:10 score:10
3. TREAD attempts:7 score:7
4. CLOUD attempts:6 score:6
5. SATIN attempts:4 score:4
6. DEITY attempts:9 score:9
7. USING attempts:3 score:3
8. FLOAT attempts:8 score:8

# [squareword.org](squareword.org) 🧩 #1594 🥳 7 ⏱️ 0:01:40.783492

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟩 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P R O M S
    R E P E L
    A F I R E
    T I N G E
    S T E E P

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1531 🥳 1037 ⏱️ 0:14:47.510617

🤔 1038 attempts
📜 1 sessions
🫧 46 chat sessions
⁉️ 237 chat prompts
🤖 237 dolphin3:latest replies
🔥   5 🥵  18 😎  78 🥶 810 🧊 126

       $1 #1038 twice            100.00°C 🥳 1000‰  ~912 used:0   [911]   source:dolphin3
       $2  #809 times             55.32°C 🔥  998‰   ~41 used:107 [40]    source:dolphin3
       $3 #1003 once              51.86°C 🔥  997‰    ~4 used:2   [3]     source:dolphin3
       $4 #1037 three             44.27°C 🔥  994‰    ~1 used:0   [0]     source:dolphin3
       $5 #1010 again             44.06°C 🔥  992‰    ~2 used:0   [1]     source:dolphin3
       $6 #1030 regularly         43.53°C 🔥  990‰    ~3 used:0   [2]     source:dolphin3
       $7 #1006 regular           36.87°C 🥵  968‰    ~5 used:1   [4]     source:dolphin3
       $8  #643 beaten            36.62°C 🥵  967‰   ~95 used:107 [94]    source:dolphin3
       $9  #963 second            36.39°C 🥵  964‰   ~12 used:10  [11]    source:dolphin3
      $10  #769 first             36.25°C 🥵  962‰   ~66 used:22  [65]    source:dolphin3
      $11  #875 beat              36.14°C 🥵  961‰   ~42 used:11  [41]    source:dolphin3
      $25  #610 one               29.05°C 😎  899‰   ~65 used:21  [64]    source:dolphin3
     $103  #375 baseline          18.20°C 🥶        ~108 used:0   [107]   source:dolphin3
     $913  #357 airstrip          -0.04°C 🧊        ~913 used:0   [912]   source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1564 🥳 105 ⏱️ 0:01:37.604754

🤔 106 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 18 chat prompts
🤖 18 dolphin3:latest replies
🥵  2 😎 18 🥶 71 🧊 14

      $1 #106 doctrine         100.00°C 🥳 1000‰  ~92 used:0  [91]   source:dolphin3
      $2 #102 jurisprudence     48.08°C 🥵  979‰   ~1 used:3  [0]    source:dolphin3
      $3  #58 politique         43.74°C 🥵  918‰  ~12 used:11 [11]   source:dolphin3
      $4  #50 constitutionnel   42.27°C 😎  881‰  ~20 used:5  [19]   source:dolphin3
      $5  #56 législateur       40.45°C 😎  828‰  ~17 used:3  [16]   source:dolphin3
      $6  #41 souverain         39.77°C 😎  800‰  ~18 used:4  [17]   source:dolphin3
      $7  #89 juridique         39.23°C 😎  778‰   ~2 used:0  [1]    source:dolphin3
      $8  #38 légitimité        38.98°C 😎  768‰  ~19 used:4  [18]   source:dolphin3
      $9  #53 droit             38.09°C 😎  716‰   ~3 used:1  [2]    source:dolphin3
     $10  #28 souveraineté      37.76°C 😎  691‰  ~13 used:2  [12]   source:dolphin3
     $11  #70 opinion           37.60°C 😎  684‰   ~4 used:0  [3]    source:dolphin3
     $12  #31 constitution      37.48°C 😎  678‰  ~14 used:2  [13]   source:dolphin3
     $22  #86 défense           28.55°C 🥶        ~24 used:0  [23]   source:dolphin3
     $93  #12 trèfle            -4.75°C 🧊        ~93 used:0  [92]   source:dolphin3
