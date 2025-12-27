# 2025-12-28

- 🔗 spaceword.org 🧩 2025-12-27 🏁 score 2170 ranked 15.8% 50/316 ⏱️ 3:14:08.282950
- 🔗 alfagok.diginaut.net 🧩 #421 🥳 12 ⏱️ 0:00:34.832148
- 🔗 alphaguess.com 🧩 #887 🥳 16 ⏱️ 0:00:33.326771
- 🔗 dontwordle.com 🧩 #1314 🥳 6 ⏱️ 0:02:06.184982
- 🔗 dictionary.com hurdle 🧩 #1457 🥳 15 ⏱️ 0:03:13.279880
- 🔗 Quordle Classic 🧩 #1434 🥳 score:22 ⏱️ 0:01:52.677114
- 🔗 Octordle Classic 🧩 #1434 🥳 score:56 ⏱️ 0:04:11.681080
- 🔗 squareword.org 🧩 #1427 🥳 7 ⏱️ 0:02:43.151831
- 🔗 cemantle.certitudes.org 🧩 #1364 🥳 66 ⏱️ 0:01:35.511685
- 🔗 cemantix.certitudes.org 🧩 #1397 🥳 1314 ⏱️ 2:28:51.921441
- 🔗 Quordle Extreme 🧩 #517 🥳 score:22 ⏱️ 0:02:13.030788
- 🔗 Quordle Rescue 🧩 #48 🥳 score:25 ⏱️ 0:01:56.125729
- 🔗 Quordle Weekly 🧩 2025-W53 🥳 score:26 ⏱️ 0:02:39.790010
- 🔗 Quordle Sequence 🧩 #1434 🥳 score:22 ⏱️ 0:03:24.807342

# Dev

## WIP

- ui:
  - Handle -- stabilizing core over Listing
  - Shell -- minimizing over Handle

- meta: rework command model over Shell

## TODO

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





# spaceword.org 🧩 2025-12-27 🏁 score 2170 ranked 15.8% 50/316 ⏱️ 3:14:08.282950

📜 4 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 50/316

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ H O P S _ Q _ _   
      _ _ _ I _ W _ U _ _   
      _ _ I L K A _ I _ _   
      _ _ _ _ I R I D _ _   
      _ _ H I D E _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #421 🥳 12 ⏱️ 0:00:34.832148

🤔 12 attempts
📜 1 sessions

    @        [     0] &-teken       >>> SEARCH
    @+1      [     1] &-tekens      
    @+2      [     2] -cijferig     
    @+3      [     3] -e-mail       
    @+199833 [199833] lijm          q0  ? after
    @+199833 [199833] lijm          q1  ? after
    @+299755 [299755] schub         q2  ? after
    @+311925 [311925] spier         q5  ? after
    @+314634 [314634] st            q6  ? after
    @+319428 [319428] stik          q7  ? after
    @+320605 [320605] stop          q9  ? after
    @+321102 [321102] straat        q10 ? after
    @+321384 [321384] straf         q11 ? it
    @+321876 [321876] straten       q8  ? before
    @+324331 [324331] sub           q4  ? before
    @+349540 [349540] vakantie      q3  ? before
    @+399709 [399709] €50-biljetten <<< SEARCH

# alphaguess.com 🧩 #887 🥳 16 ⏱️ 0:00:33.326771

🤔 16 attempts
📜 1 sessions

    @        [     0] aa         >>> SEARCH
    @+1      [     1] aah        
    @+2      [     2] aahed      
    @+3      [     3] aahing     
    @+98225  [ 98225] mach       q0  ? after
    @+147329 [147329] rho        q1  ? a
    @+147329 [147329] rho        q2  ? after
    @+153329 [153329] sea        q5  ? after
    @+154895 [154895] seraph     q7  ? after
    @+155636 [155636] sham       q8  ? after
    @+155913 [155913] she        q9  ? after
    @+155970 [155970] sheen      q12 ? after
    @+155982 [155982] sheep      q13 ? after
    @+156016 [156016] sheepskins q14 ? after
    @+156030 [156030] sheet      q15 ? it
    @+156049 [156049] sheik      q11 ? before
    @+156190 [156190] shetlands  q10 ? before
    @+156466 [156466] shit       q6  ? before
    @+159611 [159611] slug       q4  ? before
    @+171929 [171929] tag        q3  ? before
    @+196537 [196537] zzz        <<< SEARCH

# dontwordle.com 🧩 #1314 🥳 6 ⏱️ 0:02:06.184982

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:LAHAL n n n n n remain:4961
    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:2377
    ⬜⬜⬜⬜⬜ tried:WOOFS n n n n n remain:451
    ⬜⬜🟨⬜⬜ tried:PYGMY n n m n n remain:42
    ⬜⬜🟩🟨🟨 tried:ICING n n Y m m remain:2
    ⬜🟩🟩🟩🟩 tried:REIGN n Y Y Y Y remain:1

    Undos used: 2

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1457 🥳 15 ⏱️ 0:03:13.279880

📜 1 sessions
💰 score: 10100

    4/6
    ALOES ⬜⬜⬜🟨⬜
    URINE 🟨⬜⬜🟨🟩
    NUDGE 🟨🟩🟨⬜🟩
    DUNCE 🟩🟩🟩🟩🟩
    3/6
    DUNCE ⬜⬜⬜⬜🟨
    EARLS 🟨⬜🟩🟨⬜
    PERIL 🟩🟩🟩🟩🟩
    4/6
    PERIL 🟨⬜🟨⬜⬜
    TRAMP ⬜🟨🟨⬜🟨
    VAPOR ⬜🟩🟨⬜🟨
    RASPY 🟩🟩🟩🟩🟩
    3/6
    RASPY ⬜⬜⬜⬜🟩
    HOLEY 🟩🟩🟨⬜🟩
    HOTLY 🟩🟩🟩🟩🟩
    Final 1/2
    RECAP 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle) 🧩 #1434 🥳 score:22 ⏱️ 0:01:52.677114

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. SINGE attempts:3 score:3
2. PAYER attempts:4 score:4
3. BRIDE attempts:7 score:7
4. TRAIT attempts:8 score:8

# [Octordle Classic](https://www.britannica.com/games/octordle/daily) 🧩 #1434 🥳 score:56 ⏱️ 0:04:11.681080

📜 1 sessions

Octordle Classic

1. SCALE attempts:10 score:10
2. PINKY attempts:4 score:4
3. ADAPT attempts:6 score:6
4. SPURN attempts:3 score:3
5. PROUD attempts:5 score:5
6. CEASE attempts:11 score:11
7. LOBBY attempts:8 score:8
8. AGATE attempts:9 score:9

# squareword.org 🧩 #1427 🥳 7 ⏱️ 0:02:43.151831

📜 4 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A D A G E
    F E L L A
    O U T E R
    O C E A N
    T E R M S

# cemantle.certitudes.org 🧩 #1364 🥳 66 ⏱️ 0:01:35.511685

🤔 67 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 13 chat prompts
🤖 13 dolphin3:latest replies
🔥  1 🥵  2 😎  7 🥶 56

     $1 #67  ~1 fraction       100.00°C 🥳 1000‰
     $2 #65  ~3 proportion      45.19°C 🔥  993‰
     $3 #66  ~2 percentage      35.90°C 🥵  957‰
     $4 #61  ~5 scale           34.97°C 🥵  950‰
     $5 #63  ~4 magnitude       27.58°C 😎  783‰
     $6 #48  ~9 time            25.13°C 😎  649‰
     $7 #33 ~11 complexity      24.13°C 😎  569‰
     $8 #59  ~7 scope           22.51°C 😎  398‰
     $9 #46 ~10 space           21.68°C 😎  264‰
    $10 #55  ~8 extent          21.31°C 😎  190‰
    $11 #60  ~6 range           20.91°C 😎   97‰
    $12  #9     quantum         20.06°C 🥶
    $13 #58     realm           19.28°C 🥶
    $14 #53     duration        19.12°C 🥶

# cemantix.certitudes.org 🧩 #1397 🥳 1314 ⏱️ 2:28:51.921441

🤔 1315 attempts
📜 5 sessions
🫧 174 chat sessions
⁉️ 734 chat prompts
🤖 22 llama3.3:latest replies
🤖 15 glm4:latest replies
🤖 23 granite-code:34b replies
🤖 3 qwen3:32b replies
🤖 20 wizardlm2:latest replies
🤖 10 mixtral:8x7b replies
🤖 361 dolphin3:latest replies
🤖 125 gemma3:27b replies
🤖 155 falcon3:10b replies
😱   1 🔥   5 🥵  64 😎 383 🥶 712 🧊 149

       $1 #1315    ~1 complémentaire        100.00°C 🥳 1000‰
       $2  #612  ~214 spécifique             65.76°C 😱  999‰
       $3 #1287   ~15 complément             65.08°C 🔥  998‰
       $4  #778  ~160 modalité               54.38°C 🔥  996‰
       $5  #167  ~388 formation              53.90°C 🔥  995‰
       $6  #660  ~200 différent              51.38°C 🔥  991‰
       $7  #966   ~97 nécessaire             51.16°C 🔥  990‰
       $8  #319  ~317 compétence             51.06°C 🥵  987‰
       $9  #536  ~244 activité               50.81°C 🥵  986‰
      $10  #854  ~131 intégrer               50.55°C 🥵  984‰
      $11  #179  ~383 professionnel          49.73°C 🥵  982‰
      $71 #1079   ~60 indispensable          41.76°C 😎  899‰
     $455  #482       surveillance           26.40°C 🥶
    $1167  #441       self                   -0.01°C 🧊


# [Quordle Extreme](m-w.com/games/quordle/#/extreme) 🧩 #517 🥳 score:22 ⏱️ 0:02:13.030788

📜 2 sessions

Quordle Extreme m-w.com/games/quordle/

1. RAYON attempts:7 score:7
2. MOCHA attempts:4 score:4
3. WRATH attempts:5 score:5
4. USURY attempts:6 score:6

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #48 🥳 score:25 ⏱️ 0:01:56.125729

📜 2 sessions

Quordle Rescue m-w.com/games/quordle/

1. DRAFT attempts:6 score:6
2. DRAIN attempts:7 score:7
3. BANJO attempts:8 score:8
4. GUEST attempts:4 score:4

# [Quordle Weekly](m-w.com/games/quordle/#/weekly) 🧩 2025-W53 🥳 score:26 ⏱️ 0:02:39.790010

📜 2 sessions

Quordle Weekly m-w.com/games/quordle/

1. SHELL attempts:7 score:7
2. CRUSH attempts:8 score:8
3. FAITH attempts:6 score:6
4. ADBOE attempts:5 score:5

# [Quordle Sequence](m-w.com/games/quordle/#/sequence) 🧩 #1434 🥳 score:22 ⏱️ 0:03:24.807342

📜 6 sessions

Quordle Sequence m-w.com/games/quordle/

1. DINGY attempts:4 score:4
2. GRUNT attempts:5 score:5
3. THEME attempts:6 score:6
4. BLEEP attempts:7 score:7
