# 2026-10-04

- 🔗 spaceword.org 🧩 2026-10-03 🏁 score 2160 ranked 59.0% 177/300 ⏱️ 0:28:43.017106
- 🔗 wordgrid 🧩 #855 🟪 rarity:0.16 ⏱️ 0:01:55.047668
- 🔗 alfagok.diginaut.net 🧩 #701 🥳 32 ⏱️ 0:00:48.109738
- 🔗 alphaguess.com 🧩 #1168 🥳 28 ⏱️ 0:00:41.581183
- 🔗 dontwordle.com 🧩 #1594 🥳 6 ⏱️ 0:01:34.752551
- 🔗 dictionary.com hurdle 🧩 #1737 🥳 20 ⏱️ 0:04:10.727037
- 🔗 Quordle Classic 🧩 #1714 🥳 score:19 ⏱️ 0:01:29.985006
- 🔗 Octordle Classic 🧩 #1714 🥳 score:71 ⏱️ 0:02:53.666696
- 🔗 Sedecordle Classic 🧩 #1694 🥳 score:47 ⏱️ 0:04:09.099355
- 🔗 squareword.org 🧩 #1707 🥳 8 ⏱️ 0:02:47.841972
- 🔗 cemantle.certitudes.org 🧩 #1644 🥳 260 ⏱️ 0:07:48.048644
- 🔗 cemantix.certitudes.org 🧩 #1677 🥳 207 ⏱️ 1:02:20.241894

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














# [spaceword.org](spaceword.org) 🧩 2026-10-03 🏁 score 2160 ranked 59.0% 177/300 ⏱️ 0:28:43.017106

📜 3 sessions
- tiles: 21/21
- score: 2160 bonus: +60
- rank: 177/300

      _ _ _ _ _ _ _ _ _ _   
      _ _ Q U I P _ _ _ _   
      _ _ _ _ F _ D _ _ _   
      _ _ _ _ F R O _ _ _   
      _ _ _ _ _ E T _ _ _   
      _ _ _ _ _ W E _ _ _   
      _ _ _ _ _ O _ _ _ _   
      _ _ _ J A R _ _ _ _   
      _ _ _ O L E O _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #855 🟪 rarity:0.16 ⏱️ 0:01:55.047668

📜 3 sessions
🌌 🌌 🦄
🦄 🦄 🌌
🌌 🌌 🦄
Rarity: 0.16 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #701 🥳 32 ⏱️ 0:00:48.109738

🤔 32 attempts
📜 1 sessions

    @       [    0] &-teken        
    @+49802 [49802] boks           q4  ? ␅
    @+49802 [49802] boks           q5  ? after
    @+55894 [55894] bron           q10 ? ␅
    @+55894 [55894] bron           q11 ? after
    @+58916 [58916] bus            q12 ? ␅
    @+58916 [58916] bus            q13 ? after
    @+59214 [59214] buurt          q18 ? ␅
    @+59214 [59214] buurt          q19 ? after
    @+59336 [59336] buurtnetwerken q22 ? ␅
    @+59336 [59336] buurtnetwerken q23 ? after
    @+59394 [59394] buurtsuper     q24 ? ␅
    @+59394 [59394] buurtsuper     q25 ? after
    @+59426 [59426] buurtweg       q26 ? ␅
    @+59426 [59426] buurtweg       q27 ? after
    @+59436 [59436] buurtwinkel    q28 ? ␅
    @+59436 [59436] buurtwinkel    q29 ? after
    @+59445 [59445] buurvrouw      q30 ? ␅
    @+59445 [59445] buurvrouw      q31 ? it
    @+59445 [59445] buurvrouw      done. it
    @+59458 [59458] buxus          q20 ? ␅
    @+59458 [59458] buxus          q21 ? before
    @+59708 [59708] cadeau         q16 ? ␅
    @+59708 [59708] cadeau         q17 ? before
    @+60570 [60570] cao            q14 ? ␅
    @+60570 [60570] cao            q15 ? before
    @+62241 [62241] cement         q8  ? ␅
    @+62241 [62241] cement         q9  ? before
    @+74698 [74698] dc             q6  ? ␅
    @+74698 [74698] dc             q7  ? before
    @+99672 [99672] ex             q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1168 🥳 28 ⏱️ 0:00:41.581183

🤔 28 attempts
📜 1 sessions

    @       [    0] aa         
    @+2     [    2] aahed      
    @+47374 [47374] dis        q4  ? ␅
    @+47374 [47374] dis        q5  ? after
    @+60013 [60013] eyewitness q8  ? ␅
    @+60013 [60013] eyewitness q9  ? after
    @+63147 [63147] fix        q12 ? ␅
    @+63147 [63147] fix        q13 ? after
    @+63472 [63472] flat       q18 ? ␅
    @+63472 [63472] flat       q19 ? after
    @+63690 [63690] flee       q20 ? ␅
    @+63690 [63690] flee       q21 ? after
    @+63736 [63736] flench     q24 ? ␅
    @+63736 [63736] flench     q25 ? after
    @+63748 [63748] flesh      q26 ? ␅
    @+63748 [63748] flesh      q27 ? it
    @+63748 [63748] flesh      done. it
    @+63781 [63781] flex       q22 ? ␅
    @+63781 [63781] flex       q23 ? before
    @+63925 [63925] flirt      q16 ? ␅
    @+63925 [63925] flirt      q17 ? before
    @+64721 [64721] fold       q14 ? ␅
    @+64721 [64721] fold       q15 ? before
    @+66305 [66305] free       q10 ? ␅
    @+66305 [66305] free       q11 ? before
    @+72657 [72657] green      q6  ? ␅
    @+72657 [72657] green      q7  ? before
    @+98142 [98142] mac        q0  ? ␅
    @+98142 [98142] mac        q1  ? after
    @+98142 [98142] mac        q2  ? ␅
    @+98142 [98142] mac        q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1594 🥳 6 ⏱️ 0:01:34.752551

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:BUBBY n n n n n remain:7824
    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:4132
    ⬜⬜⬜⬜⬜ tried:SIMPS n n n n n remain:692
    ⬜⬜🟩⬜⬜ tried:GRRRL n n Y n n remain:36
    🟩🟩🟩⬜⬜ tried:FORDO Y Y Y n n remain:5
    🟩🟩🟩⬜⬜ tried:FORTH Y Y Y n n remain:3

    Undos used: 3

      3 words remaining
    x 8 unused letters
    = 24 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1737 🥳 20 ⏱️ 0:04:10.727037

📜 1 sessions
💰 score: 9600

    4/6
    TAPES ⬜⬜⬜⬜🟨
    LOUSY ⬜🟩⬜🟨🟩
    BRAND ⬜⬜⬜⬜⬜
    SOGGY 🟩🟩🟩🟩🟩
    5/6
    SOGGY ⬜⬜⬜⬜⬜
    CITER 🟩⬜⬜⬜⬜
    CHUNK 🟩⬜⬜⬜⬜
    ALBUM 🟨🟩⬜⬜🟨
    CLAMP 🟩🟩🟩🟩🟩
    5/6
    CLAMP ⬜⬜⬜⬜⬜
    ROSTI ⬜⬜⬜🟨🟨
    IDENT 🟨⬜⬜⬜🟨
    THIGH 🟩⬜🟨⬜⬜
    TIZZY 🟩🟩🟩🟩🟩
    5/6
    TIZZY ⬜🟨⬜⬜⬜
    IDEAS 🟨🟨⬜🟨⬜
    RAPID 🟩🟩⬜🟩🟨
    COMIX ⬜⬜⬜🟩⬜
    RADII 🟩🟩🟩🟩🟩
    Final 1/2
    TULIP 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1714 🥳 score:19 ⏱️ 0:01:29.985006

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. INFER attempts:3 score:3
2. RAINY attempts:4 score:4
3. THING attempts:5 score:5
4. ARENA attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1714 🥳 score:71 ⏱️ 0:02:53.666696

📜 1 sessions

Octordle Classic

1. GRAFT attempts:5 score:5
2. DODGE attempts:11 score:11
3. STRIP attempts:6 score:6
4. MELON attempts:7 score:7
5. PARTY attempts:8 score:8
6. FORTY attempts:9 score:9
7. RIDER attempts:13 score:13
8. SWILL attempts:12 score:12

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1694 🥳 score:47 ⏱️ 0:04:09.099355

📜 1 sessions

Sedecordle Classic sedecordle.com

1. STAFF attempts:16 score:1
2. FROST attempts:15 score:6
3. NEEDY attempts:7 score:0
4. HOBBY attempts:9 score:7
5. NOBLY attempts:3 score:0
6. SLOPE attempts:4 score:3
7. DOUGH attempts:8 score:0
8. SWASH attempts:17 score:8
9. SILLY attempts:5 score:0
10. GAYLY attempts:10 score:5
11. AMPLE attempts:12 score:1
12. WIELD attempts:18 score:2
13. TORSO attempts:18 score:1
14. SPUNK attempts:11 score:8
15. WAXEN attempts:14 score:1
16. SCOLD attempts:6 score:4

# [squareword.org](squareword.org) 🧩 #1707 🥳 8 ⏱️ 0:02:47.841972

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T A T S
    C A B I N
    A L O N E
    R O U G E
    E N T E R

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1644 🥳 260 ⏱️ 0:07:48.048644

🤔 261 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 40 chat prompts
🤖 40 dolphin3:latest replies
😱   1 🔥   4 🥵  10 😎  21 🥶 203 🧊  21

      $1 #261 shortage           100.00°C 🥳 1000‰ ~240 used:0  [239]  source:dolphin3
      $2 #235 scarcity            72.47°C 😱  999‰   ~1 used:9  [0]    source:dolphin3
      $3 #241 dearth              71.51°C 🔥  998‰   ~4 used:3  [3]    source:dolphin3
      $4 #252 shortfall           58.67°C 🔥  995‰   ~5 used:3  [4]    source:dolphin3
      $5 #249 paucity             57.74°C 🔥  994‰   ~2 used:0  [1]    source:dolphin3
      $6 #247 supply              51.17°C 🔥  992‰   ~3 used:0  [2]    source:dolphin3
      $7 #244 lack                44.50°C 🥵  981‰   ~6 used:0  [5]    source:dolphin3
      $8 #260 rationing           42.95°C 🥵  978‰   ~7 used:0  [6]    source:dolphin3
      $9 #240 constraint          40.57°C 🥵  971‰   ~8 used:0  [7]    source:dolphin3
     $10 #255 deficiency          40.50°C 🥵  970‰   ~9 used:0  [8]    source:dolphin3
     $11 #248 inadequacy          37.86°C 🥵  965‰  ~10 used:0  [9]    source:dolphin3
     $17 #224 inundation          29.83°C 😎  887‰  ~16 used:0  [15]   source:dolphin3
     $38 #245 rarity              19.31°C 🥶        ~42 used:0  [41]   source:dolphin3
    $241 #167 convergent          -0.09°C 🧊       ~241 used:0  [240]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1677 🥳 207 ⏱️ 1:02:20.241894

🤔 208 attempts
📜 1 sessions
🫧 21 chat sessions
⁉️ 114 chat prompts
🤖 38 gemma4:12b replies
🤖 76 dolphin3:latest replies
😱   1 🔥   4 🥵  17 😎  35 🥶 116 🧊  34

      $1 #208 miracle           100.00°C 🥳 1000‰ ~174 used:0   [173]  source:gemma4  
      $2  #88 miraculeux         69.81°C 😱  999‰   ~1 used:144 [0]    source:dolphin3
      $3  #98 prodige            53.98°C 🔥  998‰  ~21 used:55  [20]   source:dolphin3
      $4 #119 miraculeusement    49.34°C 🔥  997‰  ~19 used:28  [18]   source:dolphin3
      $5  #73 incroyable         45.07°C 🔥  996‰   ~2 used:18  [1]    source:dolphin3
      $6  #91 surnaturel         43.17°C 🔥  994‰   ~3 used:19  [2]    source:dolphin3
      $7  #68 extraordinaire     40.90°C 🥵  988‰  ~22 used:6   [21]   source:dolphin3
      $8  #71 merveilleux        40.56°C 🥵  986‰  ~20 used:3   [19]   source:dolphin3
      $9 #152 inespéré           39.57°C 🥵  982‰   ~4 used:2   [3]    source:gemma4  
     $10  #78 étonnant           38.72°C 🥵  977‰   ~5 used:2   [4]    source:dolphin3
     $11  #93 divin              38.52°C 🥵  976‰   ~6 used:2   [5]    source:dolphin3
     $24 #120 surprenant         32.61°C 😎  890‰  ~23 used:0   [22]   source:dolphin3
     $59 #190 halluciner         24.47°C 🥶        ~65 used:0   [64]   source:gemma4  
    $175   #8 musique            -0.69°C 🧊       ~175 used:0   [174]  source:dolphin3
