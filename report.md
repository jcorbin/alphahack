# 2026-11-14

- 🔗 wordgrid 🧩 #896 🟪 rarity:0.18 ⏱️ 0:02:19.143661
- 🔗 spaceword.org 🧩 2026-11-13 🏁 score 2173 ranked 11.3% 33/292 ⏱️ 1:41:11.962569
- 🔗 alfagok.diginaut.net 🧩 #742 🥳 38 ⏱️ 0:00:46.209833
- 🔗 alphaguess.com 🧩 #1209 🥳 20 ⏱️ 0:00:29.019217
- 🔗 dontwordle.com 🧩 #1635 🥳 6 ⏱️ 0:01:55.462466
- 🔗 dictionary.com hurdle 🧩 #1778 🥳 19 ⏱️ 0:05:01.082970
- 🔗 Quordle Classic 🧩 #1755 🥳 score:18 ⏱️ 0:01:23.521191
- 🔗 cemantle.certitudes.org 🧩 #1685 🥳 273 ⏱️ 0:01:01.347314
- 🔗 Octordle Classic 🧩 #1755 🥳 score:55 ⏱️ 0:01:30.507131
- 🔗 Sedecordle Classic 🧩 #1735 🥳 score:49 ⏱️ 0:02:45.655233
- 🔗 squareword.org 🧩 #1748 🥳 9 ⏱️ 0:02:50.431417
- 🔗 cemantix.certitudes.org 🧩 #1718 🥳 36 ⏱️ 0:04:44.167737

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










# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #892 🟪 rarity:0.32 ⏱️ 0:03:10.891631

📜 2 sessions
🌌 🦄 🦄
🌌 🌌 🌌
🦄 🌌 🌌
Rarity: 0.32 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-09 🏁 score 2168 ranked 49.8% 148/297 ⏱️ 0:22:41.164996

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 148/297

      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ G _ _ _ _ K _ L _
      _ O _ C A S A V A _
      _ A _ A _ _ S I G _
      _ D A W E N _ A _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _






# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #896 🟪 rarity:0.18 ⏱️ 0:02:19.143661

📜 2 sessions
🦄 🌌 🌌
🦄 🦄 🦄
🌌 🌌 🌌
Rarity: 0.18 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-13 🏁 score 2173 ranked 11.3% 33/292 ⏱️ 1:41:11.962569

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 33/292

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ V _ Z _ S _ _ O H   
      _ O _ A N E M O N E   
      _ E R G A T E _ E X   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #742 🥳 38 ⏱️ 0:00:46.209833

🤔 38 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+1      [     1] &-tekens    
    @+2      [     2] -cijferig   
    @+3      [     3] -e-mail     
    @+199628 [199628] lijk        q0  ? ␅
    @+199628 [199628] lijk        q1  ? after
    @+199628 [199628] lijk        q2  ? ␅
    @+199628 [199628] lijk        q3  ? after
    @+212011 [212011] media       q10 ? ␅
    @+212011 [212011] media       q11 ? after
    @+217767 [217767] milieu      q12 ? ␅
    @+217767 [217767] milieu      q13 ? after
    @+221087 [221087] mmm         q14 ? ␅
    @+221087 [221087] mmm         q15 ? after
    @+222263 [222263] mod         q16 ? ␅
    @+222263 [222263] mod         q17 ? after
    @+222409 [222409] model       q36 ? ␅
    @+222409 [222409] model       q37 ? it
    @+222409 [222409] model       done. it
    @+222812 [222812] module      q34 ? ␅
    @+222812 [222812] module      q35 ? before
    @+223391 [223391] mohammedaan q32 ? ␅
    @+223391 [223391] mohammedaan q33 ? before
    @+224510 [224510] moord       q8  ? ␅
    @+224510 [224510] moord       q9  ? before
    @+249528 [249528] opi         q6  ? ␅
    @+249528 [249528] opi         q7  ? before
    @+299509 [299509] schroot     q4  ? ␅
    @+299509 [299509] schroot     q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1209 🥳 20 ⏱️ 0:00:29.019217

🤔 20 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+49065 [49065] disturb   q2  ? ␅
    @+49065 [49065] disturb   q3  ? after
    @+61316 [61316] federal   q6  ? ␅
    @+61316 [61316] federal   q7  ? after
    @+62814 [62814] fire      q12 ? ␅
    @+62814 [62814] fire      q13 ? after
    @+63000 [63000] fish      q18 ? ␅
    @+63000 [63000] fish      q19 ? it
    @+63000 [63000] fish      done. it
    @+63199 [63199] flab      q16 ? ␅
    @+63199 [63199] flab      q17 ? before
    @+63592 [63592] flavones  q14 ? ␅
    @+63592 [63592] flavones  q15 ? before
    @+64370 [64370] fluoresce q10 ? ␅
    @+64370 [64370] fluoresce q11 ? before
    @+67436 [67436] fur       q8  ? ␅
    @+67436 [67436] fur       q9  ? before
    @+73596 [73596] guide     q4  ? ␅
    @+73596 [73596] guide     q5  ? before
    @+98138 [98138] mac       q0  ? ␅
    @+98138 [98138] mac       q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1635 🥳 6 ⏱️ 0:01:55.462466

📜 1 sessions
💰 score: 104

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:ENDED n n n n n remain:4755
    ⬜⬜⬜⬜⬜ tried:YUKKY n n n n n remain:2414
    ⬜⬜⬜⬜⬜ tried:GLOOM n n n n n remain:588
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:150
    ⬜🟩⬜⬜⬜ tried:QAJAQ n Y n n n remain:33
    ⬜🟩⬜⬜🟩 tried:FAFFS n Y n n Y remain:13

    Undos used: 3

      13 words remaining
    x 8 unused letters
    = 104 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1778 🥳 19 ⏱️ 0:05:01.082970

📜 1 sessions
💰 score: 9700

    5/6
    STARE ⬜⬜🟨⬜🟩
    ALINE 🟨⬜⬜⬜🟩
    GAMBE 🟩🟩⬜⬜🟩
    GAUZE 🟩🟩🟩⬜🟩
    GAUGE 🟩🟩🟩🟩🟩
    4/6
    GAUGE 🟩🟨⬜⬜⬜
    GROAN 🟩🟩⬜🟨🟨
    DATES ⬜🟨🟨⬜⬜
    GRANT 🟩🟩🟩🟩🟩
    3/6
    GRANT 🟨⬜⬜⬜🟨
    THUGS 🟩🟩⬜🟩⬜
    THIGH 🟩🟩🟩🟩🟩
    5/6
    THIGH ⬜⬜⬜🟩⬜
    RANGE ⬜⬜⬜🟩🟩
    BULGE ⬜🟩⬜🟩🟩
    FUDGE ⬜🟩🟩🟩🟩
    JUDGE 🟩🟩🟩🟩🟩
    Final 2/2
    CYMES ⬜🟨⬜⬜⬜
    YOUTH 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1755 🥳 score:18 ⏱️ 0:01:23.521191

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. STAIN attempts:4 score:4
2. ANGER attempts:3 score:3
3. SHRUG attempts:6 score:6
4. COLOR attempts:5 score:5

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1685 🥳 273 ⏱️ 0:01:01.347314

🤔 274 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 31 chat prompts
🤖 31 glm-5.3-flash:cloud replies
😱   1 🔥   5 🥵   6 😎  25 🥶 227 🧊   9

      $1 #274 slavery         100.00°C 🥳 1000‰ ~265 used:0  [264]  source:glm
      $2 #273 slave            72.60°C 😱  999‰   ~1 used:0  [0]    source:glm
      $3 #259 enslavement      67.17°C 🔥  998‰   ~3 used:2  [2]    source:glm
      $4 #251 servitude        56.82°C 🔥  995‰   ~6 used:3  [5]    source:glm
      $5 #252 subjugation      54.20°C 🔥  994‰   ~4 used:2  [3]    source:glm
      $6 #266 emancipation     53.82°C 🔥  992‰   ~2 used:0  [1]    source:glm
      $7 #243 bondage          52.76°C 🔥  990‰   ~5 used:2  [4]    source:glm
      $8 #248 manumission      50.29°C 🥵  983‰   ~7 used:0  [6]    source:glm
      $9 #241 serfdom          47.94°C 🥵  976‰  ~12 used:2  [11]   source:glm
     $10 #245 feudalism        47.68°C 🥵  975‰   ~8 used:0  [7]    source:glm
     $11 #263 chattel          42.68°C 🥵  955‰   ~9 used:0  [8]    source:glm
     $14 #185 patriarchal      38.31°C 😎  897‰  ~34 used:8  [33]   source:glm
     $39 #114 codex            26.74°C 🥶        ~43 used:0  [42]   source:glm
    $266  #65 weathered        -0.25°C 🧊       ~266 used:0  [265]  source:glm

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1755 🥳 score:55 ⏱️ 0:01:30.507131

📜 1 sessions

Octordle Classic

1. FIGHT attempts:11 score:11
2. FORTE attempts:10 score:10
3. ALIBI attempts:8 score:8
4. PIPER attempts:6 score:6
5. ADAPT attempts:4 score:4
6. WRING attempts:9 score:9
7. PICKY attempts:5 score:5
8. CEDAR attempts:2 score:2

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1735 🥳 score:49 ⏱️ 0:02:45.655233

📜 1 sessions

Sedecordle Classic sedecordle.com

1. FUNNY attempts:17 score:1
2. SPEND attempts:3 score:7
3. ASSET attempts:8 score:0
4. FLOUR attempts:17 score:8
5. OCCUR attempts:14 score:1
6. TODDY attempts:7 score:4
7. TERSE attempts:5 score:0
8. VOMIT attempts:9 score:5
9. MACHO attempts:13 score:1
10. VIVID attempts:10 score:3
11. SPANK attempts:15 score:1
12. RIDGE attempts:4 score:5
13. CROSS attempts:6 score:0
14. COUGH attempts:12 score:6
15. ZEBRA attempts:16 score:1
16. FLUID attempts:11 score:6

# [squareword.org](squareword.org) 🧩 #1748 🥳 9 ⏱️ 0:02:50.431417

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    T S A R S
    A L L O T
    P O P P A
    E T H E R
    S H A D E

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1718 🥳 36 ⏱️ 0:04:44.167737

🤔 37 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 10 chat prompts
🤖 10 gemma4:12b replies
😱  1 🔥  1 🥵  6 😎 11 🥶 16 🧊  1

     $1 #37 étrange           100.00°C 🥳 1000‰ ~36 used:0  [35]  source:gemma4
     $2 #13 mystérieux         74.46°C 😱  999‰  ~1 used:11 [0]   source:gemma4
     $3 #17 énigmatique        64.03°C 🔥  996‰  ~2 used:4  [1]   source:gemma4
     $4 #25 inexplicable       56.32°C 🥵  987‰  ~3 used:0  [2]   source:gemma4
     $5 #15 inconnu            55.73°C 🥵  985‰  ~4 used:0  [3]   source:gemma4
     $6 #12 obscur             53.94°C 🥵  982‰  ~5 used:0  [4]   source:gemma4
     $7 #36 sombre             52.14°C 🥵  972‰  ~6 used:0  [5]   source:gemma4
     $8 #24 indéchiffrable     50.13°C 🥵  964‰  ~7 used:0  [6]   source:gemma4
     $9 #30 ténébreux          49.19°C 🥵  959‰  ~8 used:0  [7]   source:gemma4
    $10 #32 insolite           44.37°C 😎  898‰  ~9 used:0  [8]   source:gemma4
    $11  #6 obscurité          42.85°C 😎  856‰ ~10 used:1  [9]   source:gemma4
    $12 #28 taciturne          42.34°C 😎  839‰ ~11 used:0  [10]  source:gemma4
    $21 #26 inintelligible     33.18°C 🥶       ~20 used:0  [19]  source:gemma4
    $37  #8 véhicule           -9.11°C 🧊       ~37 used:0  [36]  source:gemma4
