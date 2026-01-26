# 2026-01-27

- 🔗 spaceword.org 🧩 2026-01-26 🏁 score 2173 ranked 4.4% 14/321 ⏱️ 3:29:54.010679
- 🔗 alfagok.diginaut.net 🧩 #451 🥳 36 ⏱️ 0:00:43.975703
- 🔗 alphaguess.com 🧩 #918 🥳 30 ⏱️ 0:00:36.063036
- 🔗 dontwordle.com 🧩 #1344 🥳 6 ⏱️ 0:02:00.560168
- 🔗 dictionary.com hurdle 🧩 #1487 😦 19 ⏱️ 0:03:18.415890
- 🔗 Quordle Classic 🧩 #1464 🥳 score:22 ⏱️ 0:03:27.754618
- 🔗 Octordle Classic 🧩 #1464 😦 score:59 ⏱️ 0:04:42.643259
- 🔗 squareword.org 🧩 #1457 🥳 10 ⏱️ 0:02:34.021940
- 🔗 cemantle.certitudes.org 🧩 #1394 🥳 33 ⏱️ 0:00:17.837161
- 🔗 cemantix.certitudes.org 🧩 #1427 🥳 248 ⏱️ 0:06:10.798683
- 🔗 Quordle Rescue 🧩 #78 🥳 score:22 ⏱️ 0:01:22.720258

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












# [spaceword.org](spaceword.org) 🧩 2026-01-26 🏁 score 2173 ranked 4.4% 14/321 ⏱️ 3:29:54.010679

📜 7 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 14/321

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ E _ _ J _ F O R B   
      _ V E N I N _ _ Y A   
      _ E _ U N E Q U A L   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #451 🥳 36 ⏱️ 0:00:43.975703

🤔 36 attempts
📜 1 sessions

    @       [    0] &-teken      
    @+24910 [24910] bad          q6  ? ␅
    @+24910 [24910] bad          q7  ? after
    @+37364 [37364] bescherm     q8  ? ␅
    @+37364 [37364] bescherm     q9  ? after
    @+39999 [39999] beurs        q12 ? ␅
    @+39999 [39999] beurs        q13 ? after
    @+40754 [40754] bevoel       q16 ? ␅
    @+40754 [40754] bevoel       q17 ? after
    @+41059 [41059] bewaar       q18 ? ␅
    @+41059 [41059] bewaar       q19 ? after
    @+41151 [41151] bewaking     q22 ? ␅
    @+41151 [41151] bewaking     q23 ? after
    @+41217 [41217] bewas        q24 ? ␅
    @+41217 [41217] bewas        q25 ? after
    @+41232 [41232] beweeg       q26 ? ␅
    @+41232 [41232] beweeg       q27 ? after
    @+41260 [41260] beweegoffers q28 ? ␅
    @+41260 [41260] beweegoffers q29 ? after
    @+41273 [41273] beweer       q30 ? ␅
    @+41273 [41273] beweer       q31 ? after
    @+41279 [41279] bewegelijk   q32 ? ␅
    @+41279 [41279] bewegelijk   q33 ? after
    @+41282 [41282] bewegen      q34 ? ␅
    @+41282 [41282] bewegen      q35 ? it
    @+41282 [41282] bewegen      done. it
    @+41287 [41287] beweging     q20 ? ␅
    @+41287 [41287] beweging     q21 ? before
    @+41516 [41516] bewijs       q14 ? ␅
    @+41516 [41516] bewijs       q15 ? before
    @+43070 [43070] bij          q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #918 🥳 30 ⏱️ 0:00:36.063036

🤔 30 attempts
📜 1 sessions

    @        [     0] aa        
    @+98220  [ 98220] mach      q0  ? ␅
    @+98220  [ 98220] mach      q1  ? after
    @+147373 [147373] rhotic    q2  ? ␅
    @+147373 [147373] rhotic    q3  ? after
    @+171643 [171643] ta        q4  ? ␅
    @+171643 [171643] ta        q5  ? after
    @+174192 [174192] term      q10 ? ␅
    @+174192 [174192] term      q11 ? after
    @+174471 [174471] tet       q16 ? ␅
    @+174471 [174471] tet       q17 ? after
    @+174619 [174619] text      q18 ? ␅
    @+174619 [174619] text      q19 ? after
    @+174692 [174692] thalli    q20 ? ␅
    @+174692 [174692] thalli    q21 ? after
    @+174724 [174724] thank     q22 ? ␅
    @+174724 [174724] thank     q23 ? after
    @+174735 [174735] thankless q26 ? ␅
    @+174735 [174735] thankless q27 ? after
    @+174739 [174739] thanks    q28 ? ␅
    @+174739 [174739] thanks    q29 ? it
    @+174739 [174739] thanks    done. it
    @+174747 [174747] that      q24 ? ␅
    @+174747 [174747] that      q25 ? before
    @+174775 [174775] the       q14 ? ␅
    @+174775 [174775] the       q15 ? before
    @+175500 [175500] thrash    q12 ? ␅
    @+175500 [175500] thrash    q13 ? before
    @+176814 [176814] toil      q8  ? ␅
    @+176814 [176814] toil      q9  ? before
    @+182008 [182008] un        q7  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1344 🥳 6 ⏱️ 0:02:00.560168

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:7419
    ⬜⬜⬜⬜⬜ tried:ORZOS n n n n n remain:1361
    ⬜⬜⬜⬜⬜ tried:MINIM n n n n n remain:399
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:114
    ⬜⬜⬜⬜🟩 tried:PHPHT n n n n Y remain:9
    ⬜🟩⬜⬜🟩 tried:BUTUT n Y n n Y remain:1

    Undos used: 3

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1487 😦 19 ⏱️ 0:03:18.415890

📜 1 sessions
💰 score: 4760

    5/6
    UREAS ⬜⬜🟨⬜⬜
    OILED ⬜⬜🟩🟨⬜
    FELTY ⬜🟩🟩⬜⬜
    WELCH ⬜🟩🟩⬜⬜
    BELLE 🟩🟩🟩🟩🟩
    3/6
    BELLE 🟩⬜⬜⬜⬜
    BRATS 🟩🟨⬜🟨🟨
    BURST 🟩🟩🟩🟩🟩
    4/6
    TALES ⬜⬜🟩⬜⬜
    BURST ⬜🟨⬜🟩⬜
    AIRED 🟩⬜🟩🟩⬜
    AGREE 🟩🟩🟩🟩🟩
    5/6
    AGREE ⬜⬜⬜⬜⬜
    NOILS 🟨🟩⬜⬜🟩
    YONKS ⬜🟩🟩⬜🟩
    FONTS ⬜🟩🟩⬜🟩
    BONUS 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜🟩⬜🟩🟩
    ????? ⬜🟩⬜🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1464 🥳 score:22 ⏱️ 0:03:27.754618

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. QUALM attempts:6 score:6
2. SHARD attempts:4 score:4
3. MIGHT attempts:7 score:7
4. DWELT attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1464 😦 score:59 ⏱️ 0:04:42.643259

📜 1 sessions

Octordle Classic

1. CHORD attempts:6 score:6
2. CHAIR attempts:5 score:5
3. _ITCH -ABDEGKLMNORSUWY attempts:13 score:-1
4. MIMIC attempts:7 score:7
5. STUNT attempts:11 score:11
6. CRANE attempts:3 score:3
7. CHEEK attempts:9 score:9
8. HURRY attempts:4 score:4

# [squareword.org](squareword.org) 🧩 #1457 🥳 10 ⏱️ 0:02:34.021940

📜 2 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟨 🟨 🟨 🟨 🟨
    🟨 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S W A T S
    T H R E E
    E A S E D
    A L O N G
    D E N S E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1394 🥳 33 ⏱️ 0:00:17.837161

🤔 34 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 7 chat prompts
🤖 7 dolphin3:latest replies
🔥  1 🥵  1 😎 10 🥶 19 🧊  2

     $1 #34  ~1 yield       100.00°C 🥳 1000‰
     $2 #23  ~4 crop         35.47°C 🔥  991‰
     $3 #27  ~3 harvest      32.16°C 🥵  980‰
     $4 #19  ~7 fertilizer   25.34°C 😎  784‰
     $5 #15 ~10 sprout       22.98°C 😎  543‰
     $6 #29  ~2 soil         22.69°C 😎  498‰
     $7 #17  ~8 seedling     22.33°C 😎  445‰
     $8 #20  ~6 leaf         22.06°C 😎  382‰
     $9 #13 ~11 seed         21.57°C 😎  287‰
    $10  #9 ~12 sunflower    21.47°C 😎  264‰
    $11 #21  ~5 bloom        21.23°C 😎  202‰
    $12 #16  ~9 root         21.04°C 😎  158‰
    $14 #11     petal        19.19°C 🥶
    $33  #5     guitar       -0.42°C 🧊

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1427 🥳 248 ⏱️ 0:06:10.798683

🤔 249 attempts
📜 1 sessions
🫧 16 chat sessions
⁉️ 82 chat prompts
🤖 82 dolphin3:latest replies
😎  15 🥶 194 🧊  39

      $1 #249   ~1 sceptique         100.00°C 🥳 1000‰
      $2  #98  ~14 surprenant         35.46°C 😎  866‰
      $3  #72  ~16 étonnant           32.65°C 😎  736‰
      $4 #223   ~2 utopique           30.80°C 😎  620‰
      $5 #186   ~5 illusoire          30.31°C 😎  576‰
      $6 #185   ~6 inexplicable       30.00°C 😎  543‰
      $7 #177   ~7 paranormal         29.23°C 😎  468‰
      $8 #102  ~13 énormité           29.16°C 😎  458‰
      $9 #170   ~8 métaphysique       29.07°C 😎  451‰
     $10  #75  ~15 étonnement         29.05°C 😎  446‰
     $11 #211   ~3 panacée            28.13°C 😎  347‰
     $12 #134  ~11 intéressant        26.86°C 😎  173‰
     $17 #212      rêveur             25.64°C 🥶
    $211 #217      harmonie           -0.05°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #78 🥳 score:22 ⏱️ 0:01:22.720258

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. GROWN attempts:4 score:4
2. ODDER attempts:7 score:7
3. SCAMP attempts:5 score:5
4. TACIT attempts:6 score:6
