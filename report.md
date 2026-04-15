# 2026-04-16

- 🔗 spaceword.org 🧩 2026-04-15 🏁 score 2170 ranked 33.4% 110/329 ⏱️ 2:48:20.502330
- 🔗 alfagok.diginaut.net 🧩 #530 🥳 34 ⏱️ 0:00:51.928115
- 🔗 alphaguess.com 🧩 #997 🥳 34 ⏱️ 0:00:40.279560
- 🔗 dontwordle.com 🧩 #1423 🥳 6 ⏱️ 0:01:49.737492
- 🔗 dictionary.com hurdle 🧩 #1566 🥳 19 ⏱️ 0:05:02.993125
- 🔗 Quordle Classic 🧩 #1543 🥳 score:24 ⏱️ 0:01:47.431599
- 🔗 Octordle Classic 🧩 #1543 😦 score:70 ⏱️ 0:04:55.393790
- 🔗 squareword.org 🧩 #1536 🥳 8 ⏱️ 0:02:02.136728
- 🔗 cemantle.certitudes.org 🧩 #1473 🥳 236 ⏱️ 0:03:30.804119
- 🔗 cemantix.certitudes.org 🧩 #1506 🥳 151 ⏱️ 0:02:53.701573

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














































# [spaceword.org](spaceword.org) 🧩 2026-04-15 🏁 score 2170 ranked 33.4% 110/329 ⏱️ 2:48:20.502330

📜 3 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 110/329

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ B O D _ F _ _ _   
      _ _ _ W E _ O E _ _   
      _ _ H E X E R S _ _   
      _ _ _ _ I R E S _ _   
      _ _ J E E _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #530 🥳 34 ⏱️ 0:00:51.928115

🤔 34 attempts
📜 1 sessions

    @        [     0] &-teken            
    @+199605 [199605] lij                q0  ? ␅
    @+199605 [199605] lij                q1  ? after
    @+299472 [299472] schro              q2  ? ␅
    @+299472 [299472] schro              q3  ? after
    @+324407 [324407] subsidie           q6  ? ␅
    @+324407 [324407] subsidie           q7  ? after
    @+335597 [335597] toe                q8  ? ␅
    @+335597 [335597] toe                q9  ? after
    @+337291 [337291] tol                q14 ? ␅
    @+337291 [337291] tol                q15 ? after
    @+337503 [337503] toneel             q18 ? ␅
    @+337503 [337503] toneel             q19 ? after
    @+337597 [337597] toneelopening      q22 ? ␅
    @+337597 [337597] toneelopening      q23 ? after
    @+337639 [337639] toneelspel         q24 ? ␅
    @+337639 [337639] toneelspel         q25 ? after
    @+337665 [337665] toneelverenigingen q26 ? ␅
    @+337665 [337665] toneelverenigingen q27 ? after
    @+337677 [337677] toneelwerk         q28 ? ␅
    @+337677 [337677] toneelwerk         q29 ? after
    @+337684 [337684] tonelen            q30 ? ␅
    @+337684 [337684] tonelen            q31 ? after
    @+337687 [337687] tonen              q32 ? ␅
    @+337687 [337687] tonen              q33 ? it
    @+337687 [337687] tonen              done. it
    @+337691 [337691] tong               q20 ? ␅
    @+337691 [337691] tong               q21 ? before
    @+338009 [338009] top                q16 ? ␅
    @+338009 [338009] top                q17 ? before
    @+339022 [339022] traan              q13 ? before

# [alphaguess.com](alphaguess.com) 🧩 #997 🥳 34 ⏱️ 0:00:40.279560

🤔 34 attempts
📜 1 sessions

    @       [    0] aa        
    @+11763 [11763] back      q6  ? ␅
    @+11763 [11763] back      q7  ? after
    @+17714 [17714] blind     q8  ? ␅
    @+17714 [17714] blind     q9  ? after
    @+18031 [18031] blow      q16 ? ␅
    @+18031 [18031] blow      q17 ? after
    @+18229 [18229] bluish    q18 ? ␅
    @+18229 [18229] bluish    q19 ? after
    @+18305 [18305] boar      q20 ? ␅
    @+18305 [18305] boar      q21 ? after
    @+18306 [18306] board     q32 ? ␅
    @+18306 [18306] board     q33 ? it
    @+18306 [18306] board     done. it
    @+18307 [18307] boardable q30 ? ␅
    @+18307 [18307] boardable q31 ? before
    @+18309 [18309] boarder   q28 ? ␅
    @+18309 [18309] boarder   q29 ? before
    @+18313 [18313] boarding  q26 ? ␅
    @+18313 [18313] boarding  q27 ? before
    @+18322 [18322] boards    q24 ? ␅
    @+18322 [18322] boards    q25 ? before
    @+18351 [18351] boat      q22 ? ␅
    @+18351 [18351] boat      q23 ? before
    @+18426 [18426] bobs      q14 ? ␅
    @+18426 [18426] bobs      q15 ? before
    @+19159 [19159] boot      q12 ? ␅
    @+19159 [19159] boot      q13 ? before
    @+20686 [20686] brill     q10 ? ␅
    @+20686 [20686] brill     q11 ? before
    @+23681 [23681] camp      q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1423 🥳 6 ⏱️ 0:01:49.737492

📜 2 sessions
💰 score: 288

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:TAZZA n n n n n remain:5598
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:3203
    ⬜⬜⬜⬜⬜ tried:JINNI n n n n n remain:1480
    ⬜⬜⬜⬜⬜ tried:PUPUS n n n n n remain:308
    ⬜🟩⬜⬜⬜ tried:BOFFO n Y n n n remain:55
    ⬜🟩⬜🟩⬜ tried:WOWEE n Y n Y n remain:32

    Undos used: 2

      32 words remaining
    x 9 unused letters
    = 288 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1566 🥳 19 ⏱️ 0:05:02.993125

📜 1 sessions
💰 score: 9700

    6/6
    ARISE ⬜🟨⬜⬜🟨
    TOYER ⬜🟩⬜🟩🟩
    COWER ⬜🟩🟩🟩🟩
    LOWER ⬜🟩🟩🟩🟩
    MOWER ⬜🟩🟩🟩🟩
    POWER 🟩🟩🟩🟩🟩
    4/6
    POWER ⬜🟩⬜⬜⬜
    MOATS ⬜🟩⬜🟨⬜
    NOTCH 🟨🟩🟨🟨⬜
    COUNT 🟩🟩🟩🟩🟩
    3/6
    COUNT ⬜⬜⬜⬜🟨
    TESLA 🟩🟨⬜🟩⬜
    TITLE 🟩🟩🟩🟩🟩
    5/6
    TITLE ⬜🟨⬜🟨⬜
    ALIGN ⬜🟩🟩⬜⬜
    FLICK ⬜🟩🟩🟩🟩
    CLICK ⬜🟩🟩🟩🟩
    SLICK 🟩🟩🟩🟩🟩
    Final 1/2
    DRAPE 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1543 🥳 score:24 ⏱️ 0:01:47.431599

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. LIBEL attempts:6 score:6
2. COURT attempts:3 score:3
3. SULLY attempts:7 score:7
4. VERSE attempts:8 score:8

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1543 😦 score:70 ⏱️ 0:04:55.393790

📜 3 sessions

Octordle Classic

1. CHOKE attempts:4 score:4
2. RETCH attempts:10 score:10
3. GECKO attempts:5 score:5
4. SNACK attempts:6 score:6
5. REBEL attempts:13 score:13
6. CHAIN attempts:7 score:7
7. MAIZE attempts:11 score:11
8. CO_ER -ABDGHIKLMNPSTUVZ attempts:13 score:-1

# [squareword.org](squareword.org) 🧩 #1536 🥳 8 ⏱️ 0:02:02.136728

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B R A C T
    L E M U R
    A D O R E
    R I N S E
    E D G E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1473 🥳 236 ⏱️ 0:03:30.804119

🤔 237 attempts
📜 1 sessions
🫧 12 chat sessions
⁉️ 49 chat prompts
🤖 49 dolphin3:latest replies
😎  10 🥶 203 🧊  23

      $1 #237 hurt             100.00°C 🥳 1000‰ ~214 used:0  [213]  source:dolphin3
      $2 #211 pain              29.60°C 😎  659‰   ~1 used:1  [0]    source:dolphin3
      $3 #227 think             27.44°C 😎  513‰   ~2 used:0  [1]    source:dolphin3
      $4 #191 fall              26.71°C 😎  437‰   ~3 used:0  [2]    source:dolphin3
      $5 #189 doubt             26.40°C 😎  405‰   ~4 used:0  [3]    source:dolphin3
      $6 #230 tired             26.01°C 😎  360‰   ~5 used:0  [4]    source:dolphin3
      $7 #190 down              25.42°C 😎  298‰   ~6 used:0  [5]    source:dolphin3
      $8 #192 fear              25.34°C 😎  286‰   ~7 used:0  [6]    source:dolphin3
      $9 #202 joke              24.22°C 😎  142‰   ~8 used:0  [7]    source:dolphin3
     $10 #193 feel              23.48°C 😎   27‰   ~9 used:0  [8]    source:dolphin3
     $11 #216 see               23.48°C 😎   28‰  ~10 used:0  [9]    source:dolphin3
     $12  #58 confidence        22.94°C 🥶        ~11 used:38 [10]   source:dolphin3
     $13  #34 strength          22.80°C 🥶        ~12 used:35 [11]   source:dolphin3
    $215 #135 robustness        -0.14°C 🧊       ~215 used:0  [214]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1506 🥳 151 ⏱️ 0:02:53.701573

🤔 152 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 32 chat prompts
🤖 32 dolphin3:latest replies
🥵   3 😎  22 🥶 110 🧊  16

      $1 #152 char           100.00°C 🥳 1000‰ ~136 used:0  [135]  source:dolphin3
      $2 #114 chariot         35.80°C 🥵  957‰   ~2 used:6  [1]    source:dolphin3
      $3 #125 attelage        34.72°C 🥵  948‰   ~3 used:6  [2]    source:dolphin3
      $4 #134 timon           33.14°C 🥵  925‰   ~1 used:3  [0]    source:dolphin3
      $5  #72 roue            31.66°C 😎  884‰  ~25 used:14 [24]   source:dolphin3
      $6 #120 cheval          31.61°C 😎  882‰   ~4 used:0  [3]    source:dolphin3
      $7  #68 camion          30.37°C 😎  836‰  ~24 used:9  [23]   source:dolphin3
      $8 #110 camionnette     29.57°C 😎  792‰  ~21 used:5  [20]   source:dolphin3
      $9  #74 tracteur        29.21°C 😎  775‰  ~16 used:3  [15]   source:dolphin3
     $10  #61 pied            29.03°C 😎  763‰  ~20 used:4  [19]   source:dolphin3
     $11  #33 barque          28.82°C 😎  753‰  ~22 used:5  [21]   source:dolphin3
     $12  #64 remorque        28.33°C 😎  725‰  ~17 used:3  [16]   source:dolphin3
     $27   #9 mer             22.21°C 🥶        ~26 used:1  [25]   source:dolphin3
    $137  #88 différentiel    -0.38°C 🧊       ~137 used:0  [136]  source:dolphin3
