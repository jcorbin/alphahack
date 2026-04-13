# 2026-04-14

- 🔗 spaceword.org 🧩 2026-04-13 🏁 score 2173 ranked 12.0% 41/342 ⏱️ 5:01:35.783111
- 🔗 alfagok.diginaut.net 🧩 #528 🥳 42 ⏱️ 0:00:49.433846
- 🔗 alphaguess.com 🧩 #995 🥳 34 ⏱️ 0:00:39.319880
- 🔗 dontwordle.com 🧩 #1421 🥳 6 ⏱️ 0:03:31.022659
- 🔗 dictionary.com hurdle 🧩 #1564 😦 16 ⏱️ 0:03:42.919172
- 🔗 Quordle Classic 🧩 #1541 🥳 score:20 ⏱️ 0:01:49.649212
- 🔗 Octordle Classic 🧩 #1541 🥳 score:74 ⏱️ 0:05:23.343361
- 🔗 squareword.org 🧩 #1534 🥳 7 ⏱️ 0:02:31.745101
- 🔗 cemantle.certitudes.org 🧩 #1471 🥳 418 ⏱️ 0:08:51.964679
- 🔗 cemantix.certitudes.org 🧩 #1504 🥳 153 ⏱️ 0:01:52.551851

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












































# [spaceword.org](spaceword.org) 🧩 2026-04-13 🏁 score 2173 ranked 12.0% 41/342 ⏱️ 5:01:35.783111

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 41/342

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ O U R _ _ _   
      _ _ _ _ _ _ E _ _ _   
      _ _ _ _ B O W _ _ _   
      _ _ _ _ E _ A _ _ _   
      _ _ _ _ G _ K _ _ _   
      _ _ _ _ A G E _ _ _   
      _ _ _ _ Z _ S _ _ _   
      _ _ _ _ E N _ _ _ _   
      _ _ _ _ D E L _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #528 🥳 42 ⏱️ 0:00:49.433846

🤔 42 attempts
📜 2 sessions

    @       [    0] &-teken      
    @+24910 [24910] bad          q8  ? ␅
    @+24910 [24910] bad          q9  ? after
    @+37357 [37357] bescherm     q10 ? ␅
    @+37357 [37357] bescherm     q11 ? after
    @+38195 [38195] best         q16 ? ␅
    @+38195 [38195] best         q17 ? after
    @+38640 [38640] bestraal     q20 ? ␅
    @+38640 [38640] bestraal     q21 ? after
    @+38722 [38722] bestseller   q26 ? ␅
    @+38722 [38722] bestseller   q27 ? after
    @+38728 [38728] bestsellers  q32 ? ␅
    @+38728 [38728] bestsellers  q33 ? after
    @+38734 [38734] bestudeer    q34 ? ␅
    @+38734 [38734] bestudeer    q35 ? after
    @+38738 [38738] bestudeert   q36 ? ␅
    @+38738 [38738] bestudeert   q37 ? after
    @+38739 [38739] bestuderen   q40 ? ␅
    @+38739 [38739] bestuderen   q41 ? it
    @+38739 [38739] bestuderen   done. it
    @+38740 [38740] bestuderende q38 ? ␅
    @+38740 [38740] bestuderende q39 ? before
    @+38741 [38741] bestudering  q30 ? ␅
    @+38741 [38741] bestudering  q31 ? before
    @+38760 [38760] besturing    q28 ? ␅
    @+38760 [38760] besturing    q29 ? before
    @+38809 [38809] bestuur      q22 ? ␅
    @+38809 [38809] bestuur      q23 ? before
    @+39091 [39091] bet          q18 ? ␅
    @+39091 [39091] bet          q19 ? before
    @+39991 [39991] beurs        q15 ? before

# [alphaguess.com](alphaguess.com) 🧩 #995 🥳 34 ⏱️ 0:00:39.319880

🤔 34 attempts
📜 1 sessions

    @       [    0] aa         
    @+1398  [ 1398] acrogen    q14 ? ␅
    @+1398  [ 1398] acrogen    q15 ? after
    @+1616  [ 1616] ad         q18 ? ␅
    @+1616  [ 1616] ad         q19 ? after
    @+1737  [ 1737] adeem      q22 ? ␅
    @+1737  [ 1737] adeem      q23 ? after
    @+1762  [ 1762] adenosine  q26 ? ␅
    @+1762  [ 1762] adenosine  q27 ? after
    @+1772  [ 1772] adept      q28 ? ␅
    @+1772  [ 1772] adept      q29 ? after
    @+1779  [ 1779] adequacies q30 ? ␅
    @+1779  [ 1779] adequacies q31 ? after
    @+1781  [ 1781] adequate   q32 ? ␅
    @+1781  [ 1781] adequate   q33 ? it
    @+1781  [ 1781] adequate   done. it
    @+1786  [ 1786] adhere     q24 ? ␅
    @+1786  [ 1786] adhere     q25 ? before
    @+1857  [ 1857] adjudge    q20 ? ␅
    @+1857  [ 1857] adjudge    q21 ? before
    @+2097  [ 2097] ads        q16 ? ␅
    @+2097  [ 2097] ads        q17 ? before
    @+2802  [ 2802] ag         q12 ? ␅
    @+2802  [ 2802] ag         q13 ? before
    @+5876  [ 5876] angel      q10 ? ␅
    @+5876  [ 5876] angel      q11 ? before
    @+11763 [11763] back       q8  ? ␅
    @+11763 [11763] back       q9  ? before
    @+23681 [23681] camp       q6  ? ␅
    @+23681 [23681] camp       q7  ? before
    @+47380 [47380] dis        q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1421 🥳 6 ⏱️ 0:03:31.022659

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:TENNE n n n n n remain:4097
    ⬜⬜⬜⬜⬜ tried:OVOLO n n n n n remain:1646
    ⬜⬜⬜⬜⬜ tried:PUPPY n n n n n remain:653
    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:223
    ⬜⬜🟩⬜⬜ tried:AWARD n n Y n n remain:11
    🟩🟨🟩⬜⬜ tried:SKAGS Y m Y n n remain:1

    Undos used: 5

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1564 😦 16 ⏱️ 0:03:42.919172

📜 1 sessions
💰 score: 2260

    4/6
    PARSE ⬜🟨⬜⬜⬜
    CLAIM ⬜⬜🟩⬜⬜
    THANG 🟩🟩🟩🟩⬜
    THANK 🟩🟩🟩🟩🟩
    6/6
    THANK ⬜⬜⬜⬜⬜
    SOBER ⬜⬜⬜⬜🟨
    GURDY ⬜🟩🟩⬜🟩
    CURLY 🟩🟩🟩⬜🟩
    CURVY 🟩🟩🟩⬜🟩
    CURRY 🟩🟩🟩🟩🟩
    6/6
    ????? ⬜⬜🟨⬜⬜
    ????? 🟨🟨⬜⬜🟨
    ????? ⬜🟩⬜🟩🟩
    ????? ⬜🟩⬜🟩🟩
    ????? ⬜🟩⬜🟩🟩
    ????? ⬜🟩⬜🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1541 🥳 score:20 ⏱️ 0:01:49.649212

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. STUNT attempts:7 score:7
2. CHINA attempts:4 score:4
3. LANCE attempts:3 score:3
4. SLINK attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1541 🥳 score:74 ⏱️ 0:05:23.343361

📜 1 sessions

Octordle Classic

1. BRAVE attempts:13 score:13
2. VIPER attempts:8 score:8
3. SEEDY attempts:9 score:9
4. SORRY attempts:12 score:12
5. SALVE attempts:11 score:11
6. MAIZE attempts:6 score:6
7. SYRUP attempts:10 score:10
8. SLINK attempts:5 score:5

# [squareword.org](squareword.org) 🧩 #1534 🥳 7 ⏱️ 0:02:31.745101

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    R A P I D
    O P I N E
    M A T T E
    A C T E D
    N E A R S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1471 🥳 418 ⏱️ 0:08:51.964679

🤔 419 attempts
📜 1 sessions
🫧 27 chat sessions
⁉️ 140 chat prompts
🤖 140 dolphin3:latest replies
🔥   4 🥵  18 😎  48 🥶 341 🧊   7

      $1 #419 absorb           100.00°C 🥳 1000‰ ~412 used:0  [411]  source:dolphin3
      $2 #285 compensate        49.94°C 🔥  997‰  ~21 used:37 [20]   source:dolphin3
      $3 #376 cope              48.07°C 🔥  993‰   ~2 used:10 [1]    source:dolphin3
      $4 #380 withstand         47.60°C 🔥  992‰   ~1 used:9  [0]    source:dolphin3
      $5 #254 sustain           46.79°C 🔥  991‰  ~17 used:25 [16]   source:dolphin3
      $6 #256 adjust            45.88°C 🥵  988‰  ~22 used:9  [21]   source:dolphin3
      $7 #314 offset            45.16°C 🥵  986‰  ~18 used:3  [17]   source:dolphin3
      $8 #416 handle            44.33°C 🥵  984‰   ~3 used:0  [2]    source:dolphin3
      $9 #312 counteract        43.67°C 🥵  982‰  ~19 used:3  [18]   source:dolphin3
     $10 #339 neutralize        43.48°C 🥵  981‰   ~7 used:2  [6]    source:dolphin3
     $11 #257 adapt             42.95°C 🥵  975‰   ~8 used:2  [7]    source:dolphin3
     $24 #272 endure            34.35°C 😎  883‰  ~23 used:0  [22]   source:dolphin3
     $72 #147 adjustment        24.31°C 🥶        ~81 used:0  [80]   source:dolphin3
    $413  #99 freedom           -0.14°C 🧊       ~413 used:0  [412]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1504 🥳 153 ⏱️ 0:01:52.551851

🤔 154 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 24 chat prompts
🤖 24 dolphin3:latest replies
🔥  1 🥵  8 😎 27 🥶 92 🧊 25

      $1 #154 vidéo            100.00°C 🥳 1000‰ ~129 used:0  [128]  source:dolphin3
      $2 #142 audio             58.25°C 🔥  998‰   ~1 used:0  [0]    source:dolphin3
      $3  #68 image             47.75°C 🥵  988‰  ~29 used:12 [28]   source:dolphin3
      $4  #97 reportage         46.96°C 🥵  985‰   ~7 used:6  [6]    source:dolphin3
      $5  #89 interview         43.87°C 🥵  979‰   ~4 used:4  [3]    source:dolphin3
      $6  #92 montage           38.20°C 🥵  957‰   ~3 used:3  [2]    source:dolphin3
      $7  #88 format            36.94°C 🥵  941‰   ~2 used:1  [1]    source:dolphin3
      $8  #78 caméra            36.64°C 🥵  938‰   ~6 used:5  [5]    source:dolphin3
      $9  #81 documentaire      36.21°C 🥵  935‰   ~8 used:6  [7]    source:dolphin3
     $10  #76 film              35.88°C 🥵  931‰   ~5 used:4  [4]    source:dolphin3
     $11  #66 visuel            33.77°C 😎  898‰  ~34 used:4  [33]   source:dolphin3
     $12 #105 actualité         32.83°C 😎  884‰   ~9 used:0  [8]    source:dolphin3
     $38  #61 créatif           18.41°C 🥶        ~38 used:0  [37]   source:dolphin3
    $130 #120 son               -0.01°C 🧊       ~130 used:0  [129]  source:dolphin3
