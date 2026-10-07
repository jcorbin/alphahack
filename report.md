# 2026-10-08

- 🔗 spaceword.org 🧩 2026-10-07 🏁 score 2173 ranked 12.3% 39/317 ⏱️ 0:41:09.319665
- 🔗 wordgrid 🧩 #859 🟪 rarity:0.21 ⏱️ 0:02:24.008073
- 🔗 alfagok.diginaut.net 🧩 #705 🥳 24 ⏱️ 0:00:36.309254
- 🔗 alphaguess.com 🧩 #1172 🥳 28 ⏱️ 0:00:29.216428
- 🔗 dontwordle.com 🧩 #1598 🥳 6 ⏱️ 0:01:31.865010
- 🔗 dictionary.com hurdle 🧩 #1741 😦 16 ⏱️ 0:02:57.139976
- 🔗 Quordle Classic 🧩 #1718 😦 score:30 ⏱️ 0:02:39.963917
- 🔗 Octordle Classic 🧩 #1718 🥳 score:60 ⏱️ 0:01:41.201349
- 🔗 Sedecordle Classic 🧩 #1698 🥳 score:50 ⏱️ 0:02:33.960556
- 🔗 squareword.org 🧩 #1711 🥳 7 ⏱️ 0:01:54.107061
- 🔗 cemantle.certitudes.org 🧩 #1648 🥳 104 ⏱️ 0:04:56.485105
- 🔗 cemantix.certitudes.org 🧩 #1681 🥳 59 ⏱️ 0:01:29.039100

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




# [spaceword.org](spaceword.org) 🧩 2026-10-07 🏁 score 2173 ranked 12.3% 39/317 ⏱️ 0:41:09.319665

📜 8 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 39/317

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ G _ _ B A R _ O I   
      _ A _ Z E T E T I C   
      _ E V A D E S _ _ K   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #859 🟪 rarity:0.21 ⏱️ 0:02:24.008073

📜 2 sessions
🌌 🌌 🌌
🌌 🦄 🦄
🌌 🦄 🌌
Rarity: 0.21 🟪






# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #705 🥳 24 ⏱️ 0:00:36.309254

🤔 24 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+49802  [ 49802] boks      q4  ? ␅
    @+49802  [ 49802] boks      q5  ? after
    @+55894  [ 55894] bron      q12 ? ␅
    @+55894  [ 55894] bron      q13 ? after
    @+56036  [ 56036] brood     q22 ? ␅
    @+56036  [ 56036] brood     q23 ? it
    @+56036  [ 56036] brood     done. it
    @+56249  [ 56249] brouw     q20 ? ␅
    @+56249  [ 56249] brouw     q21 ? before
    @+56612  [ 56612] bruin     q18 ? ␅
    @+56612  [ 56612] bruin     q19 ? before
    @+57402  [ 57402] buig      q16 ? ␅
    @+57402  [ 57402] buig      q17 ? before
    @+58916  [ 58916] bus       q14 ? ␅
    @+58916  [ 58916] bus       q15 ? before
    @+62241  [ 62241] cement    q8  ? ␅
    @+62241  [ 62241] cement    q9  ? vb
    @+62241  [ 62241] cement    q10 ? ␅
    @+62241  [ 62241] cement    q11 ? before
    @+74698  [ 74698] dc        q6  ? ␅
    @+74698  [ 74698] dc        q7  ? before
    @+99672  [ 99672] ex        q2  ? ␅
    @+99672  [ 99672] ex        q3  ? before
    @+199528 [199528] lij       q0  ? ␅
    @+199528 [199528] lij       q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1172 🥳 28 ⏱️ 0:00:29.216428

🤔 28 attempts
📜 1 sessions

    @       [    0] aa         
    @+2     [    2] aahed      
    @+47374 [47374] dis        q2  ? ␅
    @+47374 [47374] dis        q3  ? after
    @+60013 [60013] eyewitness q6  ? ␅
    @+60013 [60013] eyewitness q7  ? after
    @+63147 [63147] fix        q10 ? ␅
    @+63147 [63147] fix        q11 ? after
    @+63472 [63472] flat       q16 ? ␅
    @+63472 [63472] flat       q17 ? after
    @+63690 [63690] flee       q18 ? ␅
    @+63690 [63690] flee       q19 ? after
    @+63781 [63781] flex       q20 ? ␅
    @+63781 [63781] flex       q21 ? after
    @+63813 [63813] flexures   q24 ? ␅
    @+63813 [63813] flexures   q25 ? after
    @+63826 [63826] flick      q26 ? ␅
    @+63826 [63826] flick      q27 ? it
    @+63826 [63826] flick      done. it
    @+63845 [63845] flight     q22 ? ␅
    @+63845 [63845] flight     q23 ? before
    @+63925 [63925] flirt      q14 ? ␅
    @+63925 [63925] flirt      q15 ? before
    @+64721 [64721] fold       q12 ? ␅
    @+64721 [64721] fold       q13 ? before
    @+66305 [66305] free       q8  ? ␅
    @+66305 [66305] free       q9  ? before
    @+72657 [72657] green      q4  ? ␅
    @+72657 [72657] green      q5  ? before
    @+98142 [98142] mac        q0  ? ␅
    @+98142 [98142] mac        q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1598 🥳 6 ⏱️ 0:01:31.865010

📜 1 sessions
💰 score: 9

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:BOBBY n n n n n remain:6682
    ⬜⬜⬜⬜⬜ tried:MAMMA n n n n n remain:2783
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:1028
    ⬜⬜⬜⬜⬜ tried:LULUS n n n n n remain:131
    ⬜⬜🟩🟨⬜ tried:CREEK n n Y m n remain:10
    ⬜🟩🟩⬜⬜ tried:FEEZE n Y Y n n remain:1

    Undos used: 3

      1 words remaining
    x 9 unused letters
    = 9 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1741 😦 16 ⏱️ 0:02:57.139976

📜 1 sessions
💰 score: 5080

    4/6
    TARES 🟨🟨⬜⬜🟨
    SHOAT 🟩🟨⬜🟨🟨
    PAWNS ⬜🟨🟨⬜🟨
    SWATH 🟩🟩🟩🟩🟩
    3/6
    SWATH ⬜⬜⬜⬜⬜
    DRILY ⬜⬜🟩⬜⬜
    FEIGN 🟩🟩🟩🟩🟩
    3/6
    FEIGN ⬜⬜🟨🟨⬜
    GIRLS 🟩🟩🟩🟩⬜
    GIRLY 🟩🟩🟩🟩🟩
    4/6
    GIRLY ⬜⬜⬜🟩⬜
    SHALT 🟩⬜🟩🟩🟨
    AKELA 🟨⬜⬜🟩⬜
    STALL 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜⬜⬜🟨⬜
    ????? 🟩🟩🟩⬜🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1718 😦 score:30 ⏱️ 0:02:39.963917

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. _INTY -ABDEFGKLOPRSUVWX attempts:9 score:-1
2. ROWER attempts:7 score:7
3. BROOD attempts:9 score:9
4. RESET attempts:5 score:5

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1718 🥳 score:60 ⏱️ 0:01:41.201349

📜 1 sessions

Octordle Classic

1. AWASH attempts:7 score:7
2. AGONY attempts:5 score:5
3. BIOME attempts:3 score:3
4. BEAST attempts:8 score:8
5. FERRY attempts:12 score:12
6. ALLEY attempts:6 score:6
7. DOUBT attempts:9 score:9
8. DWELL attempts:10 score:10

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1698 🥳 score:50 ⏱️ 0:02:33.960556

📜 1 sessions

Sedecordle Classic sedecordle.com

1. NANNY attempts:18 score:1
2. MERRY attempts:8 score:8
3. TOUGH attempts:7 score:0
4. ATTIC attempts:6 score:7
5. SHIRT attempts:9 score:0
6. HUMOR attempts:10 score:9
7. AUNTY attempts:3 score:0
8. RIVET attempts:11 score:3
9. CRESS attempts:17 score:1
10. ROUND attempts:12 score:7
11. SALLY attempts:13 score:1
12. ALOOF attempts:14 score:3
13. EMPTY attempts:4 score:0
14. HOTLY attempts:5 score:4
15. EATEN attempts:15 score:1
16. FLESH attempts:16 score:5

# [squareword.org](squareword.org) 🧩 #1711 🥳 7 ⏱️ 0:01:54.107061

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P I R E
    C A N A L
    U P E N D
    B A R G E
    A S T E R

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1648 🥳 104 ⏱️ 0:04:56.485105

🤔 105 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 31 chat prompts
🤖 31 dolphin3:latest replies
🥵 17 😎 15 🥶 67 🧊  5

      $1 #105 profound         100.00°C 🥳 1000‰ ~100 used:0  [99]   source:dolphin3
      $2  #72 dramatic          46.76°C 🥵  987‰  ~32 used:13 [31]   source:dolphin3
      $3 #104 poignant          45.58°C 🥵  983‰   ~1 used:0  [0]    source:dolphin3
      $4  #65 perceptible       44.47°C 🥵  974‰  ~31 used:12 [30]   source:dolphin3
      $5  #99 heartfelt         44.07°C 🥵  971‰   ~7 used:3  [6]    source:dolphin3
      $6  #91 startling         43.18°C 🥵  965‰   ~8 used:3  [7]    source:dolphin3
      $7  #66 stark             42.75°C 🥵  962‰  ~14 used:6  [13]   source:dolphin3
      $8  #28 discernible       42.69°C 🥵  961‰  ~15 used:7  [14]   source:dolphin3
      $9  #85 grievous          41.81°C 🥵  951‰   ~9 used:3  [8]    source:dolphin3
     $10  #88 painful           41.73°C 🥵  949‰   ~4 used:2  [3]    source:dolphin3
     $11  #63 unmistakable      41.07°C 🥵  943‰  ~10 used:3  [9]    source:dolphin3
     $19  #62 tangible          38.15°C 😎  862‰  ~16 used:0  [15]   source:dolphin3
     $34  #97 unexpected        29.93°C 🥶        ~37 used:0  [36]   source:dolphin3
    $101   #1 apple             -2.18°C 🧊       ~101 used:0  [100]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1681 🥳 59 ⏱️ 0:01:29.039100

🤔 60 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 10 chat prompts
🤖 10 dolphin3:latest replies
🔥  2 🥵  7 😎 19 🥶 22 🧊  9

     $1 #60 reconstruction   100.00°C 🥳 1000‰ ~51 used:0 [50]  source:dolphin3
     $2 #48 construction      56.00°C 🔥  998‰  ~2 used:4 [1]   source:dolphin3
     $3 #53 démolition        47.63°C 🔥  994‰  ~1 used:2 [0]   source:dolphin3
     $4 #55 déconstruction    37.61°C 🥵  978‰  ~3 used:0 [2]   source:dolphin3
     $5 #58 démolir           37.52°C 🥵  976‰  ~4 used:0 [3]   source:dolphin3
     $6 #25 infrastructure    33.17°C 🥵  946‰  ~9 used:3 [8]   source:dolphin3
     $7 #36 urbanistique      33.02°C 🥵  943‰  ~5 used:1 [4]   source:dolphin3
     $8 #46 aménagement       31.40°C 🥵  931‰  ~6 used:0 [5]   source:dolphin3
     $9 #49 développement     30.04°C 🥵  911‰  ~7 used:0 [6]   source:dolphin3
    $10 #30 urbanisation      29.59°C 🥵  903‰  ~8 used:0 [7]   source:dolphin3
    $11 #19 habitat           26.60°C 😎  822‰ ~25 used:2 [24]  source:dolphin3
    $12 #52 architectonique   26.43°C 😎  815‰ ~10 used:0 [9]   source:dolphin3
    $30 #39 cité              18.08°C 🥶       ~29 used:0 [28]  source:dolphin3
    $52  #6 piscine           -0.98°C 🧊       ~52 used:0 [51]  source:dolphin3
