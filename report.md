# 2026-11-07

- 🔗 wordgrid 🧩 #889 🟪 rarity:0.23 ⏱️ 0:04:54.300517
- 🔗 spaceword.org 🧩 2026-11-06 🏁 score 2168 ranked 35.4% 109/308 ⏱️ 0:29:18.724636
- 🔗 alfagok.diginaut.net 🧩 #735 🥳 26 ⏱️ 0:00:35.525127
- 🔗 alphaguess.com 🧩 #1202 🥳 22 ⏱️ 0:00:32.612539
- 🔗 dontwordle.com 🧩 #1628 🥳 6 ⏱️ 0:01:19.316506
- 🔗 dictionary.com hurdle 🧩 #1771 🥳 18 ⏱️ 0:02:39.070886
- 🔗 Quordle Classic 🧩 #1748 🥳 score:21 ⏱️ 0:01:19.925124
- 🔗 Octordle Classic 🧩 #1748 🥳 score:52 ⏱️ 0:01:54.478594
- 🔗 Sedecordle Classic 🧩 #1728 🥳 score:46 ⏱️ 0:03:52.340865
- 🔗 squareword.org 🧩 #1741 🥳 7 ⏱️ 0:02:11.392474
- 🔗 cemantle.certitudes.org 🧩 #1678 🥳 366 ⏱️ 0:01:36.330600
- 🔗 cemantix.certitudes.org 🧩 #1711 🥳 57 ⏱️ 0:00:21.016145

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







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #889 🟪 rarity:0.23 ⏱️ 0:04:54.300517

📜 2 sessions
🦄 🌌 🦄
🦄 🦄 🌌
🌌 🌌 🌌
Rarity: 0.23 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-06 🏁 score 2168 ranked 35.4% 109/308 ⏱️ 0:29:18.724636

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 109/308

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ E _ _ W _ D _   
      _ J _ L O _ I _ U _   
      _ U _ M A H Z O R _   
      _ T A Y R A _ _ O _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #735 🥳 26 ⏱️ 0:00:35.525127

🤔 26 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199631 [199631] lijk      q0  ? ␅
    @+199631 [199631] lijk      q1  ? after
    @+299522 [299522] schroot   q2  ? ␅
    @+299522 [299522] schroot   q3  ? after
    @+349304 [349304] vakantie  q4  ? ␅
    @+349304 [349304] vakantie  q5  ? after
    @+374038 [374038] vrij      q6  ? ␅
    @+374038 [374038] vrij      q7  ? after
    @+386573 [386573] wind      q8  ? ␅
    @+386573 [386573] wind      q9  ? after
    @+389782 [389782] wrik      q12 ? ␅
    @+389782 [389782] wrik      q13 ? after
    @+391204 [391204] zand      q14 ? ␅
    @+391204 [391204] zand      q15 ? after
    @+392090 [392090] zeem      q16 ? ␅
    @+392090 [392090] zeem      q17 ? after
    @+392461 [392461] zege      q18 ? ␅
    @+392461 [392461] zege      q19 ? after
    @+392622 [392622] zeil      q20 ? ␅
    @+392622 [392622] zeil      q21 ? after
    @+392806 [392806] zelatrice q22 ? ␅
    @+392806 [392806] zelatrice q23 ? after
    @+392828 [392828] zelf      q24 ? ␅
    @+392828 [392828] zelf      q25 ? it
    @+392828 [392828] zelf      done. it
    @+392990 [392990] zelfmoord q10 ? ␅
    @+392990 [392990] zelfmoord q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1202 🥳 22 ⏱️ 0:00:32.612539

🤔 22 attempts
📜 1 sessions

    @       [    0] aa      
    @+1     [    1] aah     
    @+2     [    2] aahed   
    @+3     [    3] aahing  
    @+49066 [49066] disturb q2  ? ␅
    @+49066 [49066] disturb q3  ? after
    @+61317 [61317] federal q6  ? ␅
    @+61317 [61317] federal q7  ? after
    @+67437 [67437] fur     q8  ? ␅
    @+67437 [67437] fur     q9  ? after
    @+67789 [67789] gad     q16 ? ␅
    @+67789 [67789] gad     q17 ? after
    @+67876 [67876] gain    q20 ? ␅
    @+67876 [67876] gain    q21 ? it
    @+67876 [67876] gain    done. it
    @+67961 [67961] gale    q18 ? ␅
    @+67961 [67961] gale    q19 ? before
    @+68152 [68152] gam     q14 ? ␅
    @+68152 [68152] gam     q15 ? before
    @+68960 [68960] gazabo  q12 ? ␅
    @+68960 [68960] gazabo  q13 ? before
    @+70485 [70485] glass   q10 ? ␅
    @+70485 [70485] glass   q11 ? before
    @+73597 [73597] guide   q4  ? ␅
    @+73597 [73597] guide   q5  ? before
    @+98139 [98139] mac     q0  ? ␅
    @+98139 [98139] mac     q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1628 🥳 6 ⏱️ 0:01:19.316506

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:8089
    ⬜⬜⬜⬜⬜ tried:SEEPS n n n n n remain:1598
    ⬜⬜⬜⬜⬜ tried:HOWFF n n n n n remain:545
    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:187
    ⬜🟨⬜⬜⬜ tried:CIRRI n m n n n remain:24
    🟩⬜🟨⬜⬜ tried:AJIVA Y n m n n remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1771 🥳 18 ⏱️ 0:02:39.070886

📜 1 sessions
💰 score: 9800

    4/6
    STOAE ⬜⬜⬜⬜🟩
    GRIPE ⬜⬜⬜⬜🟩
    DUNCE ⬜⬜⬜🟨🟩
    CYCLE 🟩🟩🟩🟩🟩
    4/6
    CYCLE ⬜⬜⬜⬜🟨
    RESAT ⬜🟩⬜⬜🟨
    NETOP ⬜🟩🟩🟩⬜
    DETOX 🟩🟩🟩🟩🟩
    5/6
    DETOX ⬜🟨⬜⬜⬜
    PARES ⬜⬜🟨🟩⬜
    RIVEN 🟨⬜⬜🟩⬜
    GLUER ⬜🟨🟩🟩🟨
    CRUEL 🟩🟩🟩🟩🟩
    4/6
    CRUEL ⬜⬜⬜⬜🟨
    LOINS 🟨⬜⬜⬜⬜
    PALMY ⬜🟩🟨⬜🟩
    BADLY 🟩🟩🟩🟩🟩
    Final 1/2
    WOMEN 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1748 🥳 score:21 ⏱️ 0:01:19.925124

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. PROUD attempts:8 score:8
2. ROCKY attempts:3 score:3
3. FLAKY attempts:4 score:4
4. MONTH attempts:6 score:6

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1748 🥳 score:52 ⏱️ 0:01:54.478594

📜 2 sessions

Octordle Classic

1. ARENA attempts:7 score:7
2. FOCAL attempts:10 score:10
3. DIODE attempts:6 score:6
4. SCOPE attempts:8 score:8
5. LYRIC attempts:5 score:5
6. TALLY attempts:4 score:4
7. ALBUM attempts:3 score:3
8. SPIEL attempts:9 score:9

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1728 🥳 score:46 ⏱️ 0:03:52.340865

📜 2 sessions

Sedecordle Classic sedecordle.com

1. CHIEF attempts:19 score:1
2. WELCH attempts:17 score:9
3. WEIGH attempts:10 score:1
4. ANNEX attempts:15 score:0
5. MANGO attempts:9 score:0
6. ARBOR attempts:14 score:9
7. HEIST attempts:7 score:0
8. SMALL attempts:11 score:7
9. JELLY attempts:21 score:2
10. AWARD attempts:6 score:1
11. FIXER attempts:16 score:1
12. EATER attempts:13 score:6
13. HINGE attempts:5 score:0
14. ENSUE attempts:12 score:5
15. HORDE attempts:4 score:0
16. LAUGH attempts:18 score:4

# [squareword.org](squareword.org) 🧩 #1741 🥳 7 ⏱️ 0:02:11.392474

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟩 🟨
    🟨 🟨 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C A R F
    P A G E R
    E R A S E
    C R I E S
    S Y N T H

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1678 🥳 366 ⏱️ 0:01:36.330600

🤔 367 attempts
📜 1 sessions
🫧 12 chat sessions
⁉️ 59 chat prompts
🤖 59 nemotron-3-nano:30b-cloud replies
😱   1 🔥   3 🥵   5 😎  10 🥶 333 🧊  14

      $1 #367 warfare          100.00°C 🥳 1000‰ ~353 used:0  [352]  source:nemotron
      $2 #350 war               53.14°C 😱  999‰   ~1 used:2  [0]    source:nemotron
      $3 #338 conflict          45.19°C 🔥  995‰   ~4 used:3  [3]    source:nemotron
      $4 #358 hostilities       44.00°C 🔥  993‰   ~2 used:0  [1]    source:nemotron
      $5 #353 combat            43.59°C 🔥  991‰   ~3 used:0  [2]    source:nemotron
      $6 #348 fighting          41.14°C 🥵  983‰   ~5 used:0  [4]    source:nemotron
      $7 #341 battle            40.98°C 🥵  982‰   ~6 used:0  [5]    source:nemotron
      $8 #349 strife            39.86°C 🥵  978‰   ~7 used:0  [6]    source:nemotron
      $9 #365 skirmish          37.34°C 🥵  951‰   ~8 used:0  [7]    source:nemotron
     $10 #366 violence          36.55°C 🥵  934‰   ~9 used:0  [8]    source:nemotron
     $11 #339 confrontation     34.93°C 😎  894‰  ~10 used:0  [9]    source:nemotron
     $12 #359 insurgence        34.47°C 😎  875‰  ~11 used:0  [10]   source:nemotron
     $21 #237 aridity           26.50°C 🥶        ~22 used:19 [21]   source:nemotron
    $354 #108 dune              -0.07°C 🧊       ~354 used:0  [353]  source:nemotron

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1711 🥳 57 ⏱️ 0:00:21.016145

🤔 58 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 12 chat prompts
🤖 12 nemotron-3-nano:30b-cloud replies
😱  1 🔥  1 🥵  5 😎 12 🥶 24 🧊 14

     $1 #58 entrepreneur    100.00°C 🥳 1000‰ ~44 used:0 [43]  source:nemotron
     $2 #44 entreprise       62.68°C 😱  999‰  ~1 used:4 [0]   source:nemotron
     $3 #46 dirigeant        45.42°C 🔥  994‰  ~2 used:1 [1]   source:nemotron
     $4 #50 création         32.56°C 🥵  956‰  ~3 used:0 [2]   source:nemotron
     $5 #45 commerce         32.49°C 🥵  954‰  ~4 used:0 [3]   source:nemotron
     $6 #48 société          31.82°C 🥵  949‰  ~5 used:0 [4]   source:nemotron
     $7 #39 projet           29.76°C 🥵  929‰  ~6 used:1 [5]   source:nemotron
     $8 #54 travail          28.12°C 🥵  902‰  ~7 used:0 [6]   source:nemotron
     $9 #49 activité         27.16°C 😎  881‰  ~8 used:0 [7]   source:nemotron
    $10 #21 développement    26.26°C 😎  857‰ ~18 used:3 [17]  source:nemotron
    $11 #57 croissance       22.63°C 😎  735‰  ~9 used:0 [8]   source:nemotron
    $12 #30 exécution        21.67°C 😎  684‰ ~10 used:0 [9]   source:nemotron
    $21 #32 ingénierie       15.62°C 🥶       ~22 used:0 [21]  source:nemotron
    $45  #1 bonheur          -0.71°C 🧊       ~45 used:0 [44]  source:nemotron
