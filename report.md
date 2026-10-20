# 2026-10-20

- 🔗 wordgrid 🧩 #871 🟪 rarity:0.26 ⏱️ 0:02:03.306663
- 🔗 alfagok.diginaut.net 🧩 #717 🥳 32 ⏱️ 0:00:37.396738
- 🔗 alphaguess.com 🧩 #1184 🥳 40 ⏱️ 0:01:00.495435
- 🔗 dontwordle.com 🧩 #1610 🥳 6 ⏱️ 0:01:52.638142
- 🔗 dictionary.com hurdle 🧩 #1753 🥳 18 ⏱️ 0:02:45.050428
- 🔗 Quordle Classic 🧩 #1730 🥳 score:22 ⏱️ 0:01:53.788984
- 🔗 Octordle Classic 🧩 #1730 🥳 score:60 ⏱️ 0:01:40.508270
- 🔗 Sedecordle Classic 🧩 #1710 🥳 score:36 ⏱️ 0:03:00.621197
- 🔗 squareword.org 🧩 #1723 🥳 10 ⏱️ 0:03:06.961948
- 🔗 cemantle.certitudes.org 🧩 #1660 🥳 163 ⏱️ 1:01:32.476616
- 🔗 cemantix.certitudes.org 🧩 #1693 🥳 157 ⏱️ 0:11:08.943019

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
















# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #871 🟪 rarity:0.26 ⏱️ 0:02:03.306663

📜 2 sessions
🌌 🌌 🦄
🌌 🦄 🦄
🌌 🌌 🦄
Rarity: 0.26 🟪

# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #717 🥳 32 ⏱️ 0:00:37.396738

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+199631 [199631] lijk        q0  ? ␅
    @+199631 [199631] lijk        q1  ? after
    @+249545 [249545] opi         q4  ? ␅
    @+249545 [249545] opi         q5  ? after
    @+274461 [274461] prop        q6  ? ␅
    @+274461 [274461] prop        q7  ? after
    @+280559 [280559] red         q10 ? ␅
    @+280559 [280559] red         q11 ? after
    @+283619 [283619] rente       q12 ? ␅
    @+283619 [283619] rente       q13 ? after
    @+284133 [284133] res         q18 ? ␅
    @+284133 [284133] res         q19 ? after
    @+284417 [284417] respirator  q22 ? ␅
    @+284417 [284417] respirator  q23 ? after
    @+284463 [284463] ressort     q26 ? ␅
    @+284463 [284463] ressort     q27 ? after
    @+284480 [284480] rest        q30 ? ␅
    @+284480 [284480] rest        q31 ? it
    @+284480 [284480] rest        done. it
    @+284496 [284496] restaurant  q28 ? ␅
    @+284496 [284496] restaurant  q29 ? before
    @+284535 [284535] restauratie q24 ? ␅
    @+284535 [284535] restauratie q25 ? before
    @+284711 [284711] resumeren   q20 ? ␅
    @+284711 [284711] resumeren   q21 ? before
    @+285294 [285294] reünie      q14 ? ␅
    @+285294 [285294] reünie      q15 ? after
    @+285294 [285294] reünie      q16 ? ␅
    @+285294 [285294] reünie      q17 ? before
    @+286975 [286975] riool       q9  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1184 🥳 40 ⏱️ 0:01:00.495435

🤔 40 attempts
📜 1 sessions

    @       [    0] aa           
    @+47374 [47374] dis          q2  ? ␅
    @+47374 [47374] dis          q3  ? after
    @+60013 [60013] eyewitness   q6  ? ␅
    @+60013 [60013] eyewitness   q7  ? after
    @+66305 [66305] free         q8  ? ␅
    @+66305 [66305] free         q9  ? after
    @+67879 [67879] gain         q12 ? ␅
    @+67879 [67879] gain         q13 ? after
    @+68607 [68607] gas          q14 ? ␅
    @+68607 [68607] gas          q15 ? after
    @+69043 [69043] gee          q16 ? ␅
    @+69043 [69043] gee          q17 ? after
    @+69228 [69228] genera       q18 ? ␅
    @+69228 [69228] genera       q19 ? after
    @+69353 [69353] genoise      q20 ? ␅
    @+69353 [69353] genoise      q21 ? after
    @+69378 [69378] gent         q22 ? ␅
    @+69378 [69378] gent         q23 ? after
    @+69399 [69399] gentle       q26 ? ␅
    @+69399 [69399] gentle       q27 ? after
    @+69403 [69403] gentleman    q30 ? ␅
    @+69403 [69403] gentleman    q31 ? after
    @+69406 [69406] gentlemanly  q34 ? ␅
    @+69406 [69406] gentlemanly  q35 ? after
    @+69407 [69407] gentlemen    q38 ? ␅
    @+69407 [69407] gentlemen    q39 ? it
    @+69407 [69407] gentlemen    done. it
    @+69408 [69408] gentleness   q36 ? ␅
    @+69408 [69408] gentleness   q37 ? before
    @+69409 [69409] gentlenesses q33 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1610 🥳 6 ⏱️ 0:01:52.638142

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:DEWED n n n n n remain:5734
    ⬜⬜⬜⬜⬜ tried:ALLYL n n n n n remain:1642
    ⬜⬜⬜⬜⬜ tried:MUMUS n n n n n remain:294
    ⬜🟩⬜⬜⬜ tried:BIRCH n Y n n n remain:25
    ⬜🟩⬜⬜⬜ tried:JINNI n Y n n n remain:5
    ⬜🟩🟨⬜🟨 tried:ZIPPO n Y m n m remain:2

    Undos used: 3

      2 words remaining
    x 7 unused letters
    = 14 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1753 🥳 18 ⏱️ 0:02:45.050428

📜 1 sessions
💰 score: 9800

    4/6
    REAIS ⬜⬜⬜🟨🟨
    SILTY 🟨🟩⬜⬜🟩
    DEFOG ⬜⬜🟨⬜⬜
    FISHY 🟩🟩🟩🟩🟩
    5/6
    FISHY ⬜⬜⬜⬜⬜
    LONER ⬜⬜⬜🟨⬜
    GETUP ⬜🟩⬜⬜⬜
    DEWAX ⬜🟩🟨🟨⬜
    WEAVE 🟩🟩🟩🟩🟩
    4/6
    WEAVE ⬜⬜🟨🟨⬜
    VAILS 🟩🟨🟨🟩⬜
    VIOLA 🟩🟩⬜🟩🟩
    VILLA 🟩🟩🟩🟩🟩
    4/6
    VILLA ⬜⬜⬜⬜⬜
    STORE 🟩⬜🟩🟩⬜
    SWORN 🟩⬜🟩🟩🟩
    SCORN 🟩🟩🟩🟩🟩
    Final 1/2
    PEARL 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1730 🥳 score:22 ⏱️ 0:01:53.788984

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. COYLY attempts:8 score:8
2. SAUNA attempts:7 score:7
3. TRIAL attempts:3 score:3
4. RASPY attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1730 🥳 score:60 ⏱️ 0:01:40.508270

📜 1 sessions

Octordle Classic

1. FIBER attempts:7 score:7
2. VOMIT attempts:4 score:4
3. CRATE attempts:8 score:8
4. GREEN attempts:5 score:5
5. CORNY attempts:9 score:9
6. NANNY attempts:11 score:11
7. SLACK attempts:10 score:10
8. REBUT attempts:6 score:6


# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1710 🥳 score:36 ⏱️ 0:03:00.621197

📜 1 sessions

Sedecordle Classic sedecordle.com

1. READY attempts:3 score:0
2. IONIC attempts:16 score:3
3. FLEET attempts:7 score:0
4. GAUZE attempts:17 score:7
5. EATER attempts:8 score:0
6. GNOME attempts:5 score:8
7. MISSY attempts:10 score:1
8. PRIOR attempts:9 score:0
9. CHAMP attempts:6 score:0
10. UNLIT attempts:14 score:6
11. IMPLY attempts:15 score:1
12. BOOST attempts:13 score:5
13. SALVO attempts:12 score:1
14. ALONG attempts:4 score:2
15. OPTIC attempts:11 score:1
16. TAKER attempts:18 score:1

# [squareword.org](squareword.org) 🧩 #1723 🥳 10 ⏱️ 0:03:06.961948

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟩
    🟨 🟩 🟨 🟩 🟩
    🟨 🟨 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S H O W S
    L A P E L
    A B I D E
    T I N G E
    S T E E P

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1660 🥳 163 ⏱️ 1:01:32.476616

🤔 164 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 49 chat prompts
🤖 11 dolphin3:latest replies
🤖 38 gemma4:12b replies
🔥   1 🥵   7 😎  16 🥶 129 🧊  10

      $1 #164 miller          100.00°C 🥳 1000‰ ~154 used:0  [153]  source:dolphin3
      $2 #159 maltster         46.45°C 🔥  991‰   ~1 used:3  [0]    source:dolphin3
      $3  #50 granary          41.22°C 🥵  973‰  ~24 used:41 [23]   source:gemma4  
      $4  #72 baker            40.04°C 🥵  961‰  ~23 used:23 [22]   source:gemma4  
      $5  #23 mill             39.33°C 🥵  953‰  ~16 used:18 [15]   source:gemma4  
      $6  #81 maize            38.83°C 🥵  949‰  ~12 used:11 [11]   source:gemma4  
      $7  #21 grain            38.01°C 🥵  932‰  ~13 used:11 [12]   source:gemma4  
      $8  #73 barley           37.93°C 🥵  929‰  ~14 used:11 [13]   source:gemma4  
      $9  #28 wheat            36.60°C 🥵  903‰  ~15 used:11 [14]   source:gemma4  
     $10  #62 farming          35.91°C 😎  882‰  ~17 used:2  [16]   source:gemma4  
     $11  #36 farm             35.66°C 😎  874‰  ~18 used:2  [17]   source:gemma4  
     $12  #19 artisan          34.44°C 😎  814‰  ~19 used:2  [18]   source:gemma4  
     $26  #34 crop             26.49°C 🥶        ~27 used:0  [26]   source:gemma4  
    $155  #26 proof            -0.65°C 🧊       ~155 used:0  [154]  source:gemma4  

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1693 🥳 157 ⏱️ 0:11:08.943019

🤔 158 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 31 chat prompts
🤖 18 dolphin3:latest replies
🤖 13 gemma4:12b replies
🔥   2 🥵  13 😎  17 🥶 108 🧊  17

      $1 #158 désespéré          100.00°C 🥳 1000‰ ~141 used:0  [140]  source:dolphin3
      $2 #132 malheureux          47.58°C 🔥  997‰  ~10 used:12 [9]    source:dolphin3
      $3 #121 misérable           45.61°C 🔥  993‰  ~11 used:12 [10]   source:dolphin3
      $4 #145 détresse            42.01°C 🥵  985‰   ~1 used:1  [0]    source:dolphin3
      $5 #119 dépravé             41.52°C 🥵  982‰  ~12 used:5  [11]   source:dolphin3
      $6 #127 pitié               41.16°C 🥵  980‰   ~2 used:1  [1]    source:dolphin3
      $7 #141 misère              40.65°C 🥵  975‰   ~3 used:0  [2]    source:dolphin3
      $8 #116 déshérité           39.81°C 🥵  967‰  ~13 used:5  [12]   source:dolphin3
      $9 #144 désespérance        39.25°C 🥵  964‰   ~4 used:0  [3]    source:dolphin3
     $10 #149 infortuné           38.52°C 🥵  952‰   ~5 used:0  [4]    source:dolphin3
     $11 #153 inconsolable        38.25°C 🥵  951‰   ~6 used:0  [5]    source:dolphin3
     $17 #134 désarroi            35.73°C 😎  882‰  ~14 used:0  [13]   source:dolphin3
     $34 #150 misérabilisme       27.39°C 🥶        ~37 used:0  [36]   source:dolphin3
    $142 #112 écoute              -0.20°C 🧊       ~142 used:0  [141]  source:gemma4  
