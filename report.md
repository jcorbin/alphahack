# 2026-01-16

- 🔗 spaceword.org 🧩 2026-01-15 🏁 score 2173 ranked 6.7% 23/344 ⏱️ 0:25:41.217660
- 🔗 alfagok.diginaut.net 🧩 #440 🥳 18 ⏱️ 0:00:51.105296
- 🔗 alphaguess.com 🧩 #907 🥳 20 ⏱️ 0:00:42.971534
- 🔗 dontwordle.com 🧩 #1333 🥳 6 ⏱️ 0:02:09.502567
- 🔗 dictionary.com hurdle 🧩 #1476 🥳 19 ⏱️ 0:03:03.449137
- 🔗 Quordle Classic 🧩 #1453 🥳 score:26 ⏱️ 0:03:30.002617
- 🔗 Octordle Classic 🧩 #1453 😦 score:77 ⏱️ 0:05:35.618902
- 🔗 squareword.org 🧩 #1446 🥳 7 ⏱️ 0:02:04.613138
- 🔗 cemantle.certitudes.org 🧩 #1383 🥳 47 ⏱️ 0:01:27.650196
- 🔗 cemantix.certitudes.org 🧩 #1416 🥳 339 ⏱️ 0:10:56.225583
- 🔗 Quordle Rescue 🧩 #67 🥳 score:22 ⏱️ 0:02:19.795265

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

# [spaceword.org](spaceword.org) 🧩 2026-01-15 🏁 score 2173 ranked 6.7% 23/344 ⏱️ 0:25:41.217660

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 23/344

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ R H O _ _ _   
      _ _ _ _ _ _ R _ _ _   
      _ _ _ _ Z E E _ _ _   
      _ _ _ _ _ M I _ _ _   
      _ _ _ _ Y O D _ _ _   
      _ _ _ _ U T E _ _ _   
      _ _ _ _ K I _ _ _ _   
      _ _ _ _ _ V _ _ _ _   
      _ _ _ _ T E E _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #440 🥳 18 ⏱️ 0:00:51.105296

🤔 18 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+1      [     1] &-tekens    
    @+2      [     2] -cijferig   
    @+3      [     3] -e-mail     
    @+199833 [199833] lijm        q0  ? after
    @+299738 [299738] schub       q1  ? after
    @+349521 [349521] vakantie    q2  ? after
    @+353089 [353089] ver         q4  ? after
    @+363672 [363672] verzot      q5  ? after
    @+364522 [364522] vier        q8  ? after
    @+364791 [364791] vieux       q11 ? after
    @+364865 [364865] vijf        q12 ? after
    @+364865 [364865] vijf        q13 ? after
    @+364959 [364959] vijfhonderd q14 ? after
    @+365010 [365010] vijftal     q15 ? after
    @+365014 [365014] vijftien    q17 ? it
    @+365014 [365014] vijftien    done. it
    @+365029 [365029] vijftig     q16 ? before
    @+365059 [365059] vijgen      q9  ? before
    @+365611 [365611] vis         q7  ? before
    @+368684 [368684] voetbal     q6  ? before
    @+374262 [374262] vrij        q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #907 🥳 20 ⏱️ 0:00:42.971534

🤔 20 attempts
📜 1 sessions

    @       [    0] aa          
    @+1     [    1] aah         
    @+2     [    2] aahed       
    @+3     [    3] aahing      
    @+47382 [47382] dis         q1  ? after
    @+72801 [72801] gremmy      q2  ? after
    @+85505 [85505] ins         q3  ? after
    @+88665 [88665] jacks       q5  ? after
    @+89456 [89456] jive        q7  ? after
    @+89472 [89472] jo          q9  ? after
    @+89658 [89658] jones       q10 ? after
    @+89751 [89751] joust       q11 ? after
    @+89778 [89778] joy         q12 ? after
    @+89813 [89813] joys        q13 ? after
    @+89830 [89830] jubilate    q14 ? after
    @+89833 [89833] jubilating  q17 ? after
    @+89834 [89834] jubilation  q19 ? it
    @+89834 [89834] jubilation  done. it
    @+89835 [89835] jubilations q18 ? before
    @+89836 [89836] jubile      q16 ? before
    @+89841 [89841] jucos       q15 ? before
    @+89851 [89851] judge       q8  ? before
    @+90255 [90255] kaf         q6  ? before
    @+91850 [91850] knot        q4  ? before
    @+98220 [98220] mach        q0  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1333 🥳 6 ⏱️ 0:02:09.502567

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:7300
    ⬜⬜⬜⬜⬜ tried:EGGED n n n n n remain:2491
    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:1262
    ⬜⬜⬜⬜⬜ tried:BABOO n n n n n remain:115
    ⬜⬜⬜🟨🟩 tried:WRYLY n n n m Y remain:4
    🟨🟩⬜⬜🟩 tried:LUVVY m Y n n Y remain:1

    Undos used: 4

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1476 🥳 19 ⏱️ 0:03:03.449137

📜 1 sessions
💰 score: 9700

    4/6
    AROSE ⬜⬜⬜⬜🟨
    LINED ⬜⬜🟨🟩🟩
    UNWED 🟩🟩⬜🟩🟩
    UNFED 🟩🟩🟩🟩🟩
    4/6
    UNFED ⬜🟨⬜⬜⬜
    SIGNA 🟩⬜⬜🟨🟨
    SONAR 🟩⬜🟨🟨⬜
    SPAWN 🟩🟩🟩🟩🟩
    4/6
    SPAWN ⬜⬜⬜⬜⬜
    CIDER ⬜🟩🟨🟨⬜
    FIELD ⬜🟩🟨⬜🟨
    DIODE 🟩🟩🟩🟩🟩
    6/6
    DIODE ⬜⬜🟨⬜⬜
    ARSON ⬜⬜⬜🟨⬜
    TOUCH ⬜🟩⬜⬜⬜
    WOMBY ⬜🟩⬜⬜🟩
    FOLKY 🟩🟩⬜⬜🟩
    FOGGY 🟩🟩🟩🟩🟩
    Final 1/2
    BRICK 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1453 🥳 score:26 ⏱️ 0:03:30.002617

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. UNITY attempts:4 score:4
2. JOLLY attempts:8 score:8
3. LEAKY attempts:5 score:5
4. WARTY attempts:9 score:9

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1453 😦 score:77 ⏱️ 0:05:35.618902

📜 1 sessions

Octordle Classic

1. TOWEL attempts:11 score:11
2. GUESS attempts:7 score:7
3. DITTO attempts:13 score:13
4. MODEM attempts:5 score:5
5. _UM_S ~F -ABDEGHIJKLMNOPRSTUVWY M:1 attempts:13 score:9
6. B____ ~KOR -ABDEFGHIJLMNPSTUVWY attempts:13 score:-1
7. MANGE attempts:6 score:6
8. BELOW attempts:12 score:12

# [squareword.org](squareword.org) 🧩 #1446 🥳 7 ⏱️ 0:02:04.613138

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟩 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A C T E D
    D O U L A
    A B B O T
    G R A P E
    E A S E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1383 🥳 47 ⏱️ 0:01:27.650196

🤔 48 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 11 chat prompts
🤖 11 dolphin3:latest replies
🥵  3 😎  1 🥶 40 🧊  3

     $1 #48  ~1 remedy      100.00°C 🥳 1000‰
     $2 #44  ~4 balm         40.87°C 🥵  974‰
     $3 #35  ~5 treat        36.45°C 🥵  947‰
     $4 #47  ~2 ointment     33.93°C 🥵  920‰
     $5 #45  ~3 healing      25.71°C 😎  469‰
     $6 #46     liniment     23.09°C 🥶
     $7 #29     appetizer    18.06°C 🥶
     $8 #18     bite         18.03°C 🥶
     $9 #38     dessert      17.93°C 🥶
    $10 #25     nibble       16.42°C 🥶
    $11 #26     pain         16.34°C 🥶
    $12 #23     gum          15.77°C 🥶
    $13 #34     tasty        14.81°C 🥶
    $46  #8     guitar       -1.00°C 🧊

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1416 🥳 339 ⏱️ 0:10:56.225583

🤔 340 attempts
📜 1 sessions
🫧 18 chat sessions
⁉️ 87 chat prompts
🤖 87 dolphin3:latest replies
🔥   4 🥵  11 😎  46 🥶 178 🧊 100

      $1 #340   ~1 déterminé       100.00°C 🥳 1000‰
      $2 #195  ~32 lutte            25.21°C 🔥  998‰
      $3 #293  ~15 combatif         23.68°C 🔥  992‰
      $4 #192  ~34 lutter           23.59°C 🔥  991‰
      $5 #310   ~7 mobilisation     23.44°C 🔥  990‰
      $6 #302  ~11 défensive        22.09°C 🥵  982‰
      $7 #319   ~4 force            21.79°C 🥵  980‰
      $8 #188  ~35 adversité        21.66°C 🥵  978‰
      $9 #147  ~46 crise            21.35°C 🥵  975‰
     $10 #172  ~39 cohésion         20.16°C 🥵  959‰
     $11 #200  ~30 survie           19.78°C 🥵  953‰
     $17 #124  ~53 défendre         17.87°C 😎  887‰
     $63 #100      intensifier      12.36°C 🥶
    $241 #339      acharné          -0.04°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #67 🥳 score:22 ⏱️ 0:02:19.795265

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. MAUVE attempts:6 score:6
2. MINOR attempts:5 score:5
3. HANDY attempts:8 score:8
4. GOUGE attempts:3 score:3
