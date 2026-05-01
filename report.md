# 2026-05-02

- 🔗 spaceword.org 🧩 2026-05-01 🏁 score 2173 ranked 5.8% 20/344 ⏱️ 0:33:39.110634
- 🔗 alfagok.diginaut.net 🧩 #546 🥳 30 ⏱️ 0:02:03.520639
- 🔗 alphaguess.com 🧩 #1013 🥳 32 ⏱️ 0:00:40.575374
- 🔗 dontwordle.com 🧩 #1439 🥳 6 ⏱️ 0:01:51.720091
- 🔗 dictionary.com hurdle 🧩 #1582 😦 19 ⏱️ 0:04:42.681790
- 🔗 Quordle Classic 🧩 #1559 🥳 score:18 ⏱️ 0:01:45.688314
- 🔗 Octordle Classic 🧩 #1559 🥳 score:66 ⏱️ 0:03:53.000309
- 🔗 squareword.org 🧩 #1552 🥳 8 ⏱️ 0:02:26.272262
- 🔗 cemantle.certitudes.org 🧩 #1489 🥳 289 ⏱️ 0:04:14.696084
- 🔗 cemantix.certitudes.org 🧩 #1522 🥳 744 ⏱️ 0:21:24.136885

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






























































# [spaceword.org](spaceword.org) 🧩 2026-05-01 🏁 score 2173 ranked 5.8% 20/344 ⏱️ 0:33:39.110634

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 20/344

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ K _ _ _ _   
      _ _ _ _ Q I _ _ _ _   
      _ _ _ _ _ N U _ _ _   
      _ _ _ _ F E T _ _ _   
      _ _ _ _ A M I _ _ _   
      _ _ _ _ _ A L _ _ _   
      _ _ _ _ B _ I _ _ _   
      _ _ _ _ R E Z _ _ _   
      _ _ _ _ O D E _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #546 🥳 30 ⏱️ 0:02:03.520639

🤔 30 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+199704 [199704] lijk       q0  ? ␅
    @+199704 [199704] lijk       q1  ? after
    @+299460 [299460] schro      q2  ? ␅
    @+299460 [299460] schro      q3  ? after
    @+349441 [349441] vakantie   q4  ? ␅
    @+349441 [349441] vakantie   q5  ? after
    @+353009 [353009] ver        q8  ? ␅
    @+353009 [353009] ver        q9  ? after
    @+363591 [363591] verzot     q10 ? ␅
    @+363591 [363591] verzot     q11 ? after
    @+368603 [368603] voetbal    q12 ? ␅
    @+368603 [368603] voetbal    q13 ? after
    @+369312 [369312] vol        q16 ? ␅
    @+369312 [369312] vol        q17 ? after
    @+369391 [369391] volg       q20 ? ␅
    @+369391 [369391] volg       q21 ? after
    @+369416 [369416] volgeling  q26 ? ␅
    @+369416 [369416] volgeling  q27 ? after
    @+369423 [369423] volgen     q28 ? ␅
    @+369423 [369423] volgen     q29 ? it
    @+369423 [369423] volgen     done. it
    @+369440 [369440] volger     q24 ? ␅
    @+369440 [369440] volger     q25 ? before
    @+369491 [369491] volgroeide q22 ? ␅
    @+369491 [369491] volgroeide q23 ? before
    @+369590 [369590] volks      q18 ? ␅
    @+369590 [369590] volks      q19 ? before
    @+370452 [370452] voor       q14 ? ␅
    @+370452 [370452] voor       q15 ? before
    @+374181 [374181] vrij       q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1013 🥳 32 ⏱️ 0:00:40.575374

🤔 32 attempts
📜 1 sessions

    @       [    0] aa           
    @+47380 [47380] dis          q2  ? ␅
    @+47380 [47380] dis          q3  ? after
    @+60083 [60083] face         q6  ? ␅
    @+60083 [60083] face         q7  ? after
    @+63239 [63239] flag         q10 ? ␅
    @+63239 [63239] flag         q11 ? after
    @+64036 [64036] flood        q14 ? ␅
    @+64036 [64036] flood        q15 ? after
    @+64379 [64379] fluor        q16 ? ␅
    @+64379 [64379] fluor        q17 ? after
    @+64432 [64432] fluorometric q22 ? ␅
    @+64432 [64432] fluorometric q23 ? after
    @+64458 [64458] flurries     q24 ? ␅
    @+64458 [64458] flurries     q25 ? after
    @+64461 [64461] flus         q26 ? ␅
    @+64461 [64461] flus         q27 ? after
    @+64473 [64473] fluster      q28 ? ␅
    @+64473 [64473] fluster      q29 ? after
    @+64478 [64478] flute        q30 ? ␅
    @+64478 [64478] flute        q31 ? it
    @+64478 [64478] flute        done. it
    @+64484 [64484] flutey       q20 ? ␅
    @+64484 [64484] flutey       q21 ? before
    @+64594 [64594] foam         q18 ? ␅
    @+64594 [64594] foam         q19 ? before
    @+64836 [64836] foment       q12 ? ␅
    @+64836 [64836] foment       q13 ? before
    @+66439 [66439] french       q8  ? ␅
    @+66439 [66439] french       q9  ? before
    @+72798 [72798] gremmy       q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1439 🥳 6 ⏱️ 0:01:51.720091

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:PAPAW n n n n n remain:5916
    ⬜⬜⬜⬜⬜ tried:SEXES n n n n n remain:1272
    ⬜⬜⬜⬜⬜ tried:ONION n n n n n remain:152
    ⬜🟨⬜⬜⬜ tried:GRRRL n m n n n remain:5
    🟩⬜🟨⬜⬜ tried:RHUMB Y n m n n remain:2
    🟩🟩⬜⬜🟩 tried:RUTTY Y Y n n Y remain:1

    Undos used: 4

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1582 😦 19 ⏱️ 0:04:42.681790

📜 1 sessions
💰 score: 4770

    4/6
    IDEAS ⬜⬜🟨🟨🟨
    STARE 🟨🟨🟩⬜🟨
    BEATS ⬜🟩🟩🟨🟨
    FEAST 🟩🟩🟩🟩🟩
    4/6
    FEAST ⬜⬜🟨⬜🟨
    CANTO ⬜🟨⬜🟨⬜
    TRIAL 🟨🟨⬜🟩🟨
    ALTAR 🟩🟩🟩🟩🟩
    4/6
    ALTAR 🟨⬜⬜⬜⬜
    PANES 🟨🟨⬜🟨🟨
    SCAPE 🟩⬜🟨🟨🟨
    SEPIA 🟩🟩🟩🟩🟩
    5/6
    SEPIA ⬜🟨⬜⬜⬜
    OUTER ⬜⬜🟨🟨⬜
    ETHYL 🟨🟨⬜⬜🟨
    BLENT ⬜🟩🟩⬜🟩
    CLEFT 🟩🟩🟩🟩🟩
    Final 2/2
    ????? 🟩🟨🟨⬜⬜
    ????? 🟩🟩🟩⬜🟨

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1559 🥳 score:18 ⏱️ 0:01:45.688314

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. DENIM attempts:4 score:4
2. WAIVE attempts:6 score:6
3. CHANT attempts:5 score:5
4. RENAL attempts:3 score:3

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1559 🥳 score:66 ⏱️ 0:03:53.000309

📜 1 sessions

Octordle Classic

1. POWER attempts:8 score:8
2. CRIED attempts:4 score:4
3. GROWL attempts:9 score:9
4. THORN attempts:10 score:10
5. SHOCK attempts:5 score:5
6. OFFER attempts:12 score:12
7. TIDAL attempts:7 score:7
8. ANVIL attempts:11 score:11

# [squareword.org](squareword.org) 🧩 #1552 🥳 8 ⏱️ 0:02:26.272262

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C A M P S
    A L O H A
    S P R A T
    T H E S E
    E A S E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1489 🥳 289 ⏱️ 0:04:14.696084

🤔 290 attempts
📜 1 sessions
🫧 13 chat sessions
⁉️ 65 chat prompts
🤖 65 dolphin3:latest replies
🥵   2 😎  19 🥶 235 🧊  33

      $1 #290 maker          100.00°C 🥳 1000‰ ~257 used:0  [256]  source:dolphin3
      $2 #233 packaging       28.97°C 🥵  934‰   ~4 used:15 [3]    source:dolphin3
      $3 #142 coated          26.74°C 🥵  906‰  ~13 used:44 [12]   source:dolphin3
      $4  #73 chips           25.79°C 😎  886‰  ~21 used:34 [20]   source:dolphin3
      $5 #284 based           25.47°C 😎  881‰   ~1 used:1  [0]    source:dolphin3
      $6 #259 machine         25.02°C 😎  865‰   ~5 used:2  [4]    source:dolphin3
      $7 #152 coating         24.39°C 😎  836‰  ~18 used:8  [17]   source:dolphin3
      $8  #20 confectionery   24.11°C 😎  828‰  ~20 used:18 [19]   source:dolphin3
      $9 #232 machinery       23.47°C 😎  797‰   ~6 used:2  [5]    source:dolphin3
     $10 #237 textile         19.84°C 😎  542‰   ~7 used:2  [6]    source:dolphin3
     $11 #177 powdered        19.10°C 😎  466‰  ~14 used:5  [13]   source:dolphin3
     $12 #156 encased         19.03°C 😎  460‰  ~10 used:4  [9]    source:dolphin3
     $23  #43 butter          16.53°C 🥶        ~24 used:5  [23]   source:dolphin3
    $258  #79 fruit           -0.06°C 🧊       ~258 used:0  [257]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1522 🥳 744 ⏱️ 0:21:24.136885

🤔 745 attempts
📜 1 sessions
🫧 56 chat sessions
⁉️ 296 chat prompts
🤖 296 dolphin3:latest replies
🔥   3 🥵  26 😎 175 🥶 516 🧊  24

      $1 #745 dominant              100.00°C 🥳 1000‰ ~721 used:0   [720]  source:dolphin3
      $2 #739 hégémonique            55.37°C 🔥  996‰   ~1 used:7   [0]    source:dolphin3
      $3 #228 idéologique            54.11°C 🔥  994‰ ~200 used:261 [199]  source:dolphin3
      $4 #738 dominante              52.60°C 🔥  991‰   ~2 used:7   [1]    source:dolphin3
      $5 #129 idéologie              50.06°C 🥵  986‰ ~204 used:165 [203]  source:dolphin3
      $6 #733 hégémonie              49.25°C 🥵  985‰   ~5 used:2   [4]    source:dolphin3
      $7 #499 logique                48.71°C 🥵  983‰ ~202 used:44  [201]  source:dolphin3
      $8 #298 culturaliste           47.25°C 🥵  979‰ ~198 used:22  [197]  source:dolphin3
      $9 #367 holiste                46.57°C 🥵  977‰ ~122 used:11  [121]  source:dolphin3
     $10 #252 individualiste         44.82°C 🥵  974‰ ~123 used:11  [122]  source:dolphin3
     $11 #740 majoritaire            44.54°C 🥵  971‰   ~3 used:0   [2]    source:dolphin3
     $31 #300 fonctionnalisme        39.37°C 😎  896‰ ~138 used:2   [137]  source:dolphin3
    $206 #179 économie               29.44°C 🥶       ~208 used:0   [207]  source:dolphin3
    $722  #11 académie               -0.13°C 🧊       ~722 used:0   [721]  source:dolphin3
