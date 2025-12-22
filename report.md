# 2025-12-23

- 🔗 spaceword.org 🧩 2025-12-22 🏁 score 2173 ranked 7.2% 24/335 ⏱️ 0:59:59.988260
- 🔗 alfagok.diginaut.net 🧩 #416 🥳 12 ⏱️ 0:00:37.800534
- 🔗 alphaguess.com 🧩 #882 🥳 17 ⏱️ 0:00:43.398288
- 🔗 squareword.org 🧩 #1422 🥳 8 ⏱️ 0:03:29.810256
- 🔗 dictionary.com hurdle 🧩 #1452 🥳 15 ⏱️ 0:02:41.286880
- 🔗 dontwordle.com 🧩 #1309 🥳 6 ⏱️ 0:01:42.521491
- 🔗 cemantle.certitudes.org 🧩 #1359 🥳 129 ⏱️ 0:05:00.036728
- 🔗 cemantix.certitudes.org 🧩 #1392 🥳 147 ⏱️ 0:04:24.609806
- 🔗 Quordle Classic 🧩 #1429 🥳 score:26 ⏱️ 0:03:22.040322
- 🔗 Quordle Extreme 🧩 #512 😦 score:23 ⏱️ 0:03:02.505680
- 🔗 Quordle Rescue 🧩 #43 🥳 score:29 ⏱️ 0:02:58.796395

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



























# spaceword.org 🧩 2025-12-22 🏁 score 2173 ranked 7.2% 24/335 ⏱️ 0:59:59.988260

📜 6 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 24/335

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ A B _ J _ G O A L   
      _ R O Q U E _ A Y _   
      _ T A _ T R O K E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #416 🥳 12 ⏱️ 0:00:37.800534

🤔 12 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199836 [199836] lijm      q0  ? after
    @+299758 [299758] schub     q1  ? after
    @+349543 [349543] vakantie  q2  ? after
    @+374287 [374287] vrij      q3  ? after
    @+386828 [386828] wind      q4  ? after
    @+390037 [390037] wrik      q6  ? after
    @+390704 [390704] zaad      q8  ? after
    @+390850 [390850] zaai      q10 ? after
    @+390927 [390927] zaal      q11 ? it
    @+390927 [390927] zaal      done. it
    @+391055 [391055] zadel     q9  ? before
    @+391459 [391459] zand      q7  ? before
    @+393245 [393245] zelfmoord q5  ? before

# alphaguess.com 🧩 #882 🥳 17 ⏱️ 0:00:43.398288

🤔 17 attempts
📜 1 sessions

    @        [     0] aa           
    @+1      [     1] aah          
    @+2      [     2] aahed        
    @+3      [     3] aahing       
    @+98225  [ 98225] mach         q0  ? after
    @+147329 [147329] rho          q1  ? after
    @+171929 [171929] tag          q2  ? after
    @+182015 [182015] un           q3  ? after
    @+183831 [183831] unembittered q6  ? after
    @+184278 [184278] ungula       q8  ? after
    @+184298 [184298] unhand       q12 ? after
    @+184311 [184311] unhang       q13 ? after
    @+184320 [184320] unhappiest   q15 ? after
    @+184324 [184324] unhappy      q16 ? it
    @+184324 [184324] unhappy      done. it
    @+184328 [184328] unharness    q11 ? before
    @+184386 [184386] unhistoric   q10 ? before
    @+184496 [184496] uniform      q9  ? before
    @+184728 [184728] universal    q7  ? before
    @+185645 [185645] unretire     q5  ? before
    @+189277 [189277] vicar        q4  ? before

# squareword.org 🧩 #1422 🥳 8 ⏱️ 0:03:29.810256

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟩 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C A R A T
    O P E R A
    S A F E R
    T R E N D
    S T R A Y

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1452 🥳 15 ⏱️ 0:02:41.286880

📜 1 sessions
💰 score: 10100

    3/6
    STEAL ⬜🟨⬜🟩🟨
    BLOAT ⬜🟩🟩🟩🟩
    FLOAT 🟩🟩🟩🟩🟩
    3/6
    FLOAT ⬜⬜⬜⬜🟩
    BRUIT 🟩🟨🟨⬜🟩
    BURNT 🟩🟩🟩🟩🟩
    4/6
    BURNT ⬜⬜⬜⬜🟨
    STALE ⬜🟨⬜⬜🟩
    WHITE 🟨⬜🟩🟨🟩
    TWICE 🟩🟩🟩🟩🟩
    4/6
    TWICE 🟨⬜🟩⬜⬜
    SAINT 🟨⬜🟩⬜🟩
    MOIST ⬜🟩🟩🟩🟩
    HOIST 🟩🟩🟩🟩🟩
    Final 1/2
    METAL 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1309 🥳 6 ⏱️ 0:01:42.521491

📜 1 sessions
💰 score: 56

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:7419
    ⬜⬜⬜⬜⬜ tried:MIMIC n n n n n remain:3545
    ⬜⬜⬜⬜⬜ tried:KOOKY n n n n n remain:1135
    ⬜⬜⬜⬜⬜ tried:VUGGS n n n n n remain:165
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:63
    ⬜🟨⬜🟩🟩 tried:DEWED n m n Y Y remain:8

    Undos used: 3

      8 words remaining
    x 7 unused letters
    = 56 total score

# cemantle.certitudes.org 🧩 #1359 🥳 129 ⏱️ 0:05:00.036728

🤔 130 attempts
📜 6 sessions
🫧 2 chat sessions
⁉️ 24 chat prompts
🤖 24 dolphin3:latest replies
🔥  3 🥵  2 😎 29 🥶 89 🧊  6

      $1 #130   ~1 desk          100.00°C 🥳 1000‰
      $2 #110  ~11 drawer         47.63°C 🔥  995‰
      $3 #123   ~5 bookcase       47.39°C 🔥  993‰
      $4  #52  ~29 notepad        47.24°C 🔥  992‰
      $5 #128   ~3 table          40.46°C 🥵  971‰
      $6 #107  ~12 tray           38.60°C 🥵  960‰
      $7  #33  ~35 pencil         33.41°C 😎  887‰
      $8  #69  ~23 fax            33.17°C 😎  883‰
      $9  #92  ~14 phone          32.17°C 😎  862‰
     $10 #129   ~2 chair          31.50°C 😎  837‰
     $11 #126   ~4 library        31.36°C 😎  834‰
     $12  #40  ~32 pen            31.01°C 😎  821‰
     $36  #65      coffee         22.21°C 🥶
    $125  #15      kaleidoscope   -0.97°C 🧊

# cemantix.certitudes.org 🧩 #1392 🥳 147 ⏱️ 0:04:24.609806

🤔 148 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 29 chat prompts
🤖 29 dolphin3:latest replies
🥵  2 😎  7 🥶 93 🧊 45

      $1 #148   ~1 mensonge        100.00°C 🥳 1000‰
      $2 #147   ~2 tromper          48.22°C 🥵  974‰
      $3 #132   ~6 croire           42.70°C 🥵  922‰
      $4 #130   ~8 dissimuler       39.96°C 😎  877‰
      $5 #131   ~7 cacher           36.47°C 😎  776‰
      $6 #143   ~3 masquer          35.27°C 😎  723‰
      $7 #139   ~5 illusionner      35.22°C 😎  720‰
      $8  #85   ~9 détourner        35.14°C 😎  715‰
      $9 #140   ~4 jurer            31.68°C 😎  499‰
     $10  #82  ~10 détournement     28.50°C 😎  115‰
     $11 #111      fuir             24.71°C 🥶
     $12 #141      laisser          24.67°C 🥶
     $13  #93      faire            23.55°C 🥶
    $104  #31      lave             -0.09°C 🧊

# [Quordle Classic](m-w.com/games/quordle) 🧩 #1429 🥳 score:26 ⏱️ 0:03:22.040322

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. GLOAT attempts:5 score:5
2. CLASP attempts:7 score:7
3. USAGE attempts:6 score:6
4. BONGO attempts:8 score:8


# [Quordle Extreme](m-w.com/games/quordle/#/extreme) 🧩 #512 😦 score:23 ⏱️ 0:03:02.505680

📜 1 sessions

Quordle Extreme m-w.com/games/quordle/

1. MATCH attempts:6 score:6
2. ITCHY attempts:5 score:5
3. MYRRH attempts:4 score:4
4. FI_ER -ACDHLMOPSTWXY attempts:8 score:-1

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #43 🥳 score:29 ⏱️ 0:02:58.796395

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. POPPY attempts:9 score:9
2. FRAIL attempts:8 score:8
3. DOZEN attempts:5 score:5
4. STIFF attempts:7 score:7
