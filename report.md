# 2026-09-02

- 🔗 spaceword.org 🧩 2026-09-01 🏁 score 2173 ranked 5.8% 21/364 ⏱️ 0:04:43.303779
- 🔗 wordgrid 🧩 #823 🟪 rarity:0.33 ⏱️ 0:02:21.689958
- 🔗 alfagok.diginaut.net 🧩 #669 🥳 22 ⏱️ 0:00:35.030781
- 🔗 alphaguess.com 🧩 #1136 🥳 26 ⏱️ 0:00:36.220176
- 🔗 dontwordle.com 🧩 #1562 🤷 6 ⏱️ 0:02:50.285265
- 🔗 dictionary.com hurdle 🧩 #1705 🥳 18 ⏱️ 0:03:16.181830
- 🔗 Quordle Classic 🧩 #1682 🥳 score:24 ⏱️ 0:02:40.554845
- 🔗 Octordle Classic 🧩 #1682 🥳 score:60 ⏱️ 0:01:48.086124
- 🔗 Sedecordle Classic 🧩 #1662 🥳 score:40 ⏱️ 0:02:46.077504
- 🔗 squareword.org 🧩 #1675 🥳 7 ⏱️ 0:02:12.941389
- 🔗 cemantle.certitudes.org 🧩 #1612 🥳 125 ⏱️ 0:08:13.640522
- 🔗 cemantix.certitudes.org 🧩 #1645 🥳 280 ⏱️ 1:36:28.597604

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







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #781 🟪 rarity:0.15 ⏱️ 0:03:50.236694

📜 2 sessions
🌌 🦄 🦄
🌌 🦄 🦄
🌌 🌌 🌌
Rarity: 0.15 🟪


# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #-1 ❗ rarity:nan ⏱️ 0:05:19.095498

📜 2 sessions
🌌 🦄 🌌
🌌 🦄 🌌
🌌 🦄 🌌
Rarity: nan ❗







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #788 🟪 rarity:0.29 ⏱️ 0:03:24.033720

📜 2 sessions
🦄 🦄 🌌
🦄 🦄 🦄
🌌 🦄 🌌
Rarity: 0.29 🟪


# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #789 🟪 rarity:0.23 ⏱️ 0:02:56.015327

📜 2 sessions
🌌 🌌 🌌
🦄 🦄 🌌
🦄 🦄 🦄
Rarity: 0.23 🟪







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #795 🟪 rarity:0.27 ⏱️ 0:03:44.973967

📜 2 sessions
🦄 🌌 🌌
🌌 🌌 🌌
🦄 🦄 🌌
Rarity: 0.27 🟪





























# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #823 🟪 rarity:0.33 ⏱️ 0:02:21.689958

📜 3 sessions
🦄 🌌 🌌
🌌 🌌 🦄
🌌 🦄 🌌
Rarity: 0.33 🟪

# [spaceword.org](spaceword.org) 🧩 2026-09-01 🏁 score 2173 ranked 5.8% 21/364 ⏱️ 0:04:43.303779

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 21/364

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ C _ _ _ _ _   
      _ _ _ _ A J I _ _ _   
      _ _ _ _ T I _ _ _ _   
      _ _ _ _ E V E _ _ _   
      _ _ _ _ S I X _ _ _   
      _ _ _ _ _ E S _ _ _   
      _ _ _ _ A R E _ _ _   
      _ _ _ _ _ _ C _ _ _   
      _ _ _ _ Y E T _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #669 🥳 22 ⏱️ 0:00:35.030781

🤔 22 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+49808  [ 49808] boks      q6  ? ␅
    @+49808  [ 49808] boks      q7  ? after
    @+55900  [ 55900] bron      q12 ? ␅
    @+55900  [ 55900] bron      q13 ? after
    @+58922  [ 58922] bus       q14 ? ␅
    @+58922  [ 58922] bus       q15 ? after
    @+59220  [ 59220] buurt     q20 ? ␅
    @+59220  [ 59220] buurt     q21 ? it
    @+59220  [ 59220] buurt     done. it
    @+59714  [ 59714] cadeau    q18 ? ␅
    @+59714  [ 59714] cadeau    q19 ? before
    @+60576  [ 60576] cao       q16 ? ␅
    @+60576  [ 60576] cao       q17 ? before
    @+62247  [ 62247] cement    q10 ? ␅
    @+62247  [ 62247] cement    q11 ? before
    @+74711  [ 74711] dc        q8  ? ␅
    @+74711  [ 74711] dc        q9  ? before
    @+99688  [ 99688] ex        q4  ? ␅
    @+99688  [ 99688] ex        q5  ? before
    @+199647 [199647] lijk      q0  ? ␅
    @+199647 [199647] lijk      q1  ? after
    @+199647 [199647] lijk      q2  ? ␅
    @+199647 [199647] lijk      q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1136 🥳 26 ⏱️ 0:00:36.220176

🤔 26 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+5876  [ 5876] angel      q10 ? ␅
    @+5876  [ 5876] angel      q11 ? after
    @+5914  [ 5914] angioma    q22 ? ␅
    @+5914  [ 5914] angioma    q23 ? after
    @+5927  [ 5927] angle      q24 ? ␅
    @+5927  [ 5927] angle      q25 ? it
    @+5927  [ 5927] angle      done. it
    @+5957  [ 5957] anglo      q20 ? ␅
    @+5957  [ 5957] anglo      q21 ? before
    @+6041  [ 6041] animal     q18 ? ␅
    @+6041  [ 6041] animal     q19 ? before
    @+6254  [ 6254] annuitants q16 ? ␅
    @+6254  [ 6254] annuitants q17 ? before
    @+6632  [ 6632] anti       q14 ? ␅
    @+6632  [ 6632] anti       q15 ? before
    @+8323  [ 8323] ar         q12 ? ␅
    @+8323  [ 8323] ar         q13 ? before
    @+11763 [11763] back       q8  ? ␅
    @+11763 [11763] back       q9  ? before
    @+23680 [23680] camp       q6  ? ␅
    @+23680 [23680] camp       q7  ? before
    @+47378 [47378] dis        q4  ? ␅
    @+47378 [47378] dis        q5  ? before
    @+98147 [98147] mac        q0  ? ␅
    @+98147 [98147] mac        q1  ? after
    @+98147 [98147] mac        q2  ? ␅
    @+98147 [98147] mac        q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1562 🤷 6 ⏱️ 0:02:50.285265

📜 1 sessions
💰 score: 0

ELIMINATED
> Well technically I didn't Wordle!

    ⬜⬜⬜⬜⬜ tried:MAGMA n n n n n remain:5731
    ⬜⬜⬜⬜⬜ tried:PENNE n n n n n remain:1604
    ⬜⬜⬜⬜⬜ tried:SLYLY n n n n n remain:268
    ⬜🟨⬜⬜⬜ tried:FIFTH n m n n n remain:31
    🟨🟨⬜⬜🟩 tried:IROKO m m n n Y remain:1
    ⬛⬛⬛⬛⬛ tried:????? remain:0

    Undos used: 5

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1705 🥳 18 ⏱️ 0:03:16.181830

📜 1 sessions
💰 score: 9800

    4/6
    RESAY ⬜⬜⬜🟨⬜
    PLAIT ⬜⬜🟨🟩🟨
    ACTIN 🟩🟨🟩🟩⬜
    ATTIC 🟩🟩🟩🟩🟩
    4/6
    ATTIC ⬜⬜⬜🟨⬜
    SIREN 🟨🟨⬜⬜⬜
    IDOLS 🟨⬜⬜⬜🟨
    WHISK 🟩🟩🟩🟩🟩
    4/6
    WHISK ⬜⬜🟨⬜⬜
    MINED ⬜🟩⬜⬜⬜
    VIRAL ⬜🟩🟨🟩⬜
    CIGAR 🟩🟩🟩🟩🟩
    4/6
    CIGAR 🟨⬜⬜🟨🟨
    ACRES 🟨🟨🟨🟨⬜
    REACT 🟩🟩🟩🟩⬜
    REACH 🟩🟩🟩🟩🟩
    Final 2/2
    SHEOL 🟩🟩🟩⬜🟨
    SHELF 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1682 🥳 score:24 ⏱️ 0:02:40.554845

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. INCUR attempts:3 score:3
2. FELLA attempts:7 score:7
3. TITAN attempts:8 score:8
4. FROZE attempts:6 score:6

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1682 🥳 score:60 ⏱️ 0:01:48.086124

📜 1 sessions

Octordle Classic

1. ALONG attempts:5 score:5
2. CELLO attempts:9 score:9
3. CIVIL attempts:6 score:6
4. SHORN attempts:4 score:4
5. FEAST attempts:11 score:11
6. WORDY attempts:8 score:8
7. UNMET attempts:7 score:7
8. BEGET attempts:10 score:10

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1662 🥳 score:40 ⏱️ 0:02:46.077504

📜 1 sessions

Sedecordle Classic sedecordle.com

1. REPAY attempts:4 score:0
2. CLASS attempts:11 score:4
3. TALON attempts:6 score:0
4. BELLY attempts:17 score:6
5. JOUST attempts:12 score:1
6. DRAWN attempts:7 score:2
7. CLASP attempts:13 score:1
8. TEPEE attempts:3 score:3
9. SWARM attempts:10 score:1
10. SHOAL attempts:5 score:0
11. BROWN attempts:16 score:1
12. SLINK attempts:18 score:6
13. STUFF attempts:14 score:1
14. SHONE attempts:8 score:4
15. GOOEY attempts:18 score:1
16. SMEAR attempts:9 score:9

# [squareword.org](squareword.org) 🧩 #1675 🥳 7 ⏱️ 0:02:12.941389

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    T E L L S
    A V A I L
    P E R K Y
    A N G E L
    S T O N Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1612 🥳 125 ⏱️ 0:08:13.640522

🤔 126 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 56 chat prompts
🤖 56 dolphin3:latest replies
🔥  2 🥵  3 😎 16 🥶 83 🧊 21

      $1 #126 defend         100.00°C 🥳 1000‰ ~105 used:0  [104]  source:dolphin3
      $2 #123 protect         60.00°C 🔥  997‰   ~2 used:5  [1]    source:dolphin3
      $3 #125 safeguard       48.88°C 🔥  994‰   ~1 used:2  [0]    source:dolphin3
      $4 #113 fortify         44.15°C 🥵  987‰   ~5 used:7  [4]    source:dolphin3
      $5 #119 defense         41.20°C 🥵  973‰   ~4 used:6  [3]    source:dolphin3
      $6 #117 bolster         36.98°C 🥵  920‰   ~3 used:5  [2]    source:dolphin3
      $7 #118 buttress        34.44°C 😎  845‰   ~6 used:0  [5]    source:dolphin3
      $8 #115 strengthen      32.89°C 😎  788‰   ~7 used:1  [6]    source:dolphin3
      $9  #81 agitate         31.12°C 😎  688‰  ~20 used:17 [19]   source:dolphin3
     $10  #93 mobilize        30.78°C 😎  670‰  ~15 used:10 [14]   source:dolphin3
     $11  #94 unite           29.63°C 😎  579‰  ~14 used:9  [13]   source:dolphin3
     $12 #102 unify           29.08°C 😎  539‰  ~12 used:4  [11]   source:dolphin3
     $23 #122 guard           24.63°C 🥶        ~28 used:0  [27]   source:dolphin3
    $106  #74 stimulus        -0.47°C 🧊       ~106 used:0  [105]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1645 🥳 280 ⏱️ 1:36:28.597604

🤔 281 attempts
📜 1 sessions
🫧 36 chat sessions
⁉️ 200 chat prompts
🤖 200 dolphin3:latest replies
🔥   5 🥵  12 😎  26 🥶 201 🧊  36

      $1 #281 fouet           100.00°C 🥳 1000‰ ~245 used:0  [244]  source:dolphin3
      $2 #171 massue           46.36°C 🔥  998‰  ~16 used:77 [15]   source:dolphin3
      $3 #194 bâton            42.92°C 🔥  996‰   ~4 used:33 [3]    source:dolphin3
      $4 #198 marteau          37.83°C 🔥  993‰   ~1 used:30 [0]    source:dolphin3
      $5 #119 poignard         37.70°C 🔥  991‰  ~13 used:41 [12]   source:dolphin3
      $6 #127 épée             37.54°C 🔥  990‰   ~5 used:39 [4]    source:dolphin3
      $7 #209 cimeterre        35.94°C 🥵  984‰   ~6 used:4  [5]    source:dolphin3
      $8 #129 couteau          34.45°C 🥵  972‰  ~15 used:7  [14]   source:dolphin3
      $9 #113 empoigner        34.42°C 🥵  971‰  ~36 used:21 [35]   source:dolphin3
     $10 #192 hache            33.33°C 🥵  967‰   ~2 used:3  [1]    source:dolphin3
     $11 #261 matraque         32.47°C 🥵  956‰   ~3 used:3  [2]    source:dolphin3
     $19 #185 battre           28.80°C 😎  890‰  ~17 used:0  [16]   source:dolphin3
     $45 #100 chasser          20.86°C 🥶        ~56 used:0  [55]   source:dolphin3
    $246  #38 défense          -0.34°C 🧊       ~246 used:0  [245]  source:dolphin3
