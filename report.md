# 2026-10-27

- 🔗 spaceword.org 🧩 2026-10-26 🏁 score 2168 ranked 48.4% 151/312 ⏱️ 3:15:55.960031
- 🔗 alfagok.diginaut.net 🧩 #724 🥳 26 ⏱️ 0:00:32.878972
- 🔗 alphaguess.com 🧩 #1191 🥳 30 ⏱️ 0:00:38.871802
- 🔗 dontwordle.com 🧩 #1617 🥳 6 ⏱️ 0:01:30.518562
- 🔗 dictionary.com hurdle 🧩 #1760 🥳 17 ⏱️ 0:02:46.394278
- 🔗 Quordle Classic 🧩 #1737 🥳 score:21 ⏱️ 0:01:20.333704
- 🔗 Octordle Classic 🧩 #1737 🥳 score:60 ⏱️ 0:02:23.001755
- 🔗 Sedecordle Classic 🧩 #1717 🥳 score:36 ⏱️ 0:03:01.545737
- 🔗 squareword.org 🧩 #1730 🥳 8 ⏱️ 0:02:29.027596
- 🔗 cemantle.certitudes.org 🧩 #1667 🥳 136 ⏱️ 0:09:42.715900
- 🔗 cemantix.certitudes.org 🧩 #1700 🥳 223 ⏱️ 1:27:25.814678
- 🔗 wordgrid 🧩 #878 🟪 rarity:0.25 ⏱️ 0:03:01.763621

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























# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #878 🟪 rarity:0.25 ⏱️ 0:03:01.763621

📜 3 sessions
🌌 🌌 🌌
🦄 🦄 🦄
🌌 🦄 🌌
Rarity: 0.25 🟪

# [spaceword.org](spaceword.org) 🧩 2026-10-26 🏁 score 2168 ranked 48.4% 151/312 ⏱️ 3:15:55.960031

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 151/312

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ Y _ E _ _   
      _ P _ S Q U I R M _   
      _ A _ U _ K _ A I _   
      _ T O N I E R _ X _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   




# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #724 🥳 26 ⏱️ 0:00:32.878972

🤔 26 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+49802  [ 49802] boks      q4  ? ␅
    @+49802  [ 49802] boks      q5  ? after
    @+50498  [ 50498] bonnen    q16 ? ␅
    @+50498  [ 50498] bonnen    q17 ? after
    @+50598  [ 50598] bonus     q20 ? ␅
    @+50598  [ 50598] bonus     q21 ? after
    @+50656  [ 50656] boodschap q22 ? ␅
    @+50656  [ 50656] boodschap q23 ? after
    @+50694  [ 50694] boog      q24 ? ␅
    @+50694  [ 50694] boog      q25 ? it
    @+50694  [ 50694] boog      done. it
    @+50780  [ 50780] boom      q18 ? ␅
    @+50780  [ 50780] boom      q19 ? before
    @+51209  [ 51209] boots     q14 ? ␅
    @+51209  [ 51209] boots     q15 ? before
    @+52644  [ 52644] bouw      q12 ? ␅
    @+52644  [ 52644] bouw      q13 ? before
    @+55894  [ 55894] bron      q10 ? ␅
    @+55894  [ 55894] bron      q11 ? before
    @+62241  [ 62241] cement    q8  ? ␅
    @+62241  [ 62241] cement    q9  ? before
    @+74698  [ 74698] dc        q6  ? ␅
    @+74698  [ 74698] dc        q7  ? before
    @+99672  [ 99672] ex        q2  ? ␅
    @+99672  [ 99672] ex        q3  ? before
    @+199631 [199631] lijk      q0  ? ␅
    @+199631 [199631] lijk      q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1191 🥳 30 ⏱️ 0:00:38.871802

🤔 30 attempts
📜 1 sessions

    @        [     0] aa             
    @+98142  [ 98142] mac            q0  ? ␅
    @+98142  [ 98142] mac            q1  ? after
    @+122089 [122089] par            q6  ? ␅
    @+122089 [122089] par            q7  ? after
    @+128395 [128395] plack          q10 ? ␅
    @+128395 [128395] plack          q11 ? after
    @+129516 [129516] po             q12 ? ␅
    @+129516 [129516] po             q13 ? after
    @+132109 [132109] precess        q14 ? ␅
    @+132109 [132109] precess        q15 ? after
    @+133343 [133343] prese          q16 ? ␅
    @+133343 [133343] prese          q17 ? after
    @+133645 [133645] pretension     q20 ? ␅
    @+133645 [133645] pretension     q21 ? after
    @+133802 [133802] prevision      q22 ? ␅
    @+133802 [133802] prevision      q23 ? after
    @+133875 [133875] price          q24 ? ␅
    @+133875 [133875] price          q25 ? after
    @+133912 [133912] pride          q26 ? ␅
    @+133912 [133912] pride          q27 ? after
    @+133927 [133927] priest         q28 ? ␅
    @+133927 [133927] priest         q29 ? it
    @+133927 [133927] priest         done. it
    @+133959 [133959] prim           q18 ? ␅
    @+133959 [133959] prim           q19 ? before
    @+134703 [134703] prohibit       q8  ? ␅
    @+134703 [134703] prohibit       q9  ? before
    @+147304 [147304] rho            q2  ? ␅
    @+147304 [147304] rho            q3  ? b b
    @+147327 [147327] rhombencephala q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1617 🥳 6 ⏱️ 0:01:30.518562

📜 1 sessions
💰 score: 12

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:PEEVE n n n n n remain:5924
    ⬜⬜⬜⬜⬜ tried:KLOOF n n n n n remain:2015
    ⬜⬜⬜⬜⬜ tried:MUMUS n n n n n remain:494
    ⬜🟨⬜⬜⬜ tried:BIDDY n m n n n remain:85
    ⬜⬜🟨⬜⬜ tried:WHIRR n n m n n remain:13
    🟨⬜⬜🟨⬜ tried:AGAIN m n n m n remain:2

    Undos used: 3

      2 words remaining
    x 6 unused letters
    = 12 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1760 🥳 17 ⏱️ 0:02:46.394278

📜 1 sessions
💰 score: 9900

    4/6
    TOEAS 🟨🟨⬜⬜⬜
    PINOT ⬜🟩⬜🟩🟩
    BIGOT ⬜🟩⬜🟩🟩
    DIVOT 🟩🟩🟩🟩🟩
    4/6
    DIVOT 🟨⬜⬜⬜⬜
    MAUDS 🟨⬜⬜🟨⬜
    EMBED 🟩🟩⬜🟨🟩
    EMEND 🟩🟩🟩🟩🟩
    4/6
    EMEND ⬜⬜🟩⬜🟩
    TREAD ⬜🟩🟩🟩🟩
    BREAD ⬜🟩🟩🟩🟩
    DREAD 🟩🟩🟩🟩🟩
    3/6
    DREAD ⬜⬜⬜⬜⬜
    NICOL 🟨⬜🟨⬜🟨
    LUNCH 🟩🟩🟩🟩🟩
    Final 2/2
    PASTY ⬜⬜🟩🟩🟩
    MUSTY 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1737 🥳 score:21 ⏱️ 0:01:20.333704

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. ANKLE attempts:3 score:3
2. HAVOC attempts:6 score:6
3. SULKY attempts:5 score:5
4. WHITE attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1737 🥳 score:60 ⏱️ 0:02:23.001755

📜 1 sessions

Octordle Classic

1. SHADE attempts:8 score:8
2. MINCE attempts:12 score:12
3. FLUID attempts:3 score:3
4. PLUSH attempts:9 score:9
5. TODAY attempts:7 score:7
6. JAUNT attempts:11 score:11
7. FILER attempts:4 score:4
8. RABID attempts:6 score:6

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1717 🥳 score:36 ⏱️ 0:03:01.545737

📜 1 sessions

Sedecordle Classic sedecordle.com

1. AGAPE attempts:16 score:1
2. ICILY attempts:12 score:6
3. STIFF attempts:20 score:2
4. FRILL attempts:17 score:0
5. CANNY attempts:13 score:1
6. SNOOP attempts:9 score:3
7. PRICK attempts:15 score:1
8. SCRUM attempts:8 score:5
9. MORPH attempts:10 score:1
10. SPILL attempts:7 score:0
11. QUEUE attempts:18 score:1
12. TUMOR attempts:4 score:8
13. ERROR attempts:11 score:1
14. BUILD attempts:5 score:1
15. PORCH attempts:14 score:1
16. CRUMP attempts:6 score:4

# [squareword.org](squareword.org) 🧩 #1730 🥳 8 ⏱️ 0:02:29.027596

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟨 🟨 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P E A R
    T I L D E
    R A D O N
    I N E R T
    P O R E S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1667 🥳 136 ⏱️ 0:09:42.715900

🤔 137 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 24 chat prompts
🤖 24 dolphin3:latest replies
😱   1 🔥   2 🥵   7 😎   9 🥶 114 🧊   3

      $1 #137 dad            100.00°C 🥳 1000‰ ~134 used:0  [133]  source:dolphin3
      $2 #131 father          80.41°C 😱  999‰   ~1 used:5  [0]    source:dolphin3
      $3 #129 uncle           70.80°C 🔥  993‰   ~2 used:6  [1]    source:dolphin3
      $4 #130 brother         69.92°C 🔥  992‰   ~3 used:7  [2]    source:dolphin3
      $5 #126 nephew          62.03°C 🥵  981‰   ~4 used:1  [3]    source:dolphin3
      $6 #123 aunt            57.97°C 🥵  976‰   ~5 used:0  [4]    source:dolphin3
      $7 #124 cousin          57.35°C 🥵  972‰   ~6 used:0  [5]    source:dolphin3
      $8 #127 niece           55.31°C 🥵  969‰   ~7 used:0  [6]    source:dolphin3
      $9  #47 family          48.74°C 🥵  943‰  ~14 used:20 [13]   source:dolphin3
     $10 #125 grandparent     44.37°C 🥵  924‰   ~8 used:0  [7]    source:dolphin3
     $11 #122 sibling         41.51°C 🥵  903‰   ~9 used:1  [8]    source:dolphin3
     $12  #50 love            39.72°C 😎  882‰  ~19 used:7  [18]   source:dolphin3
     $21 #107 joy             26.09°C 🥶        ~23 used:0  [22]   source:dolphin3
    $135  #56 belonging       -0.25°C 🧊       ~135 used:0  [134]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1700 🥳 223 ⏱️ 1:27:25.814678

🤔 224 attempts
📜 1 sessions
🫧 14 chat sessions
⁉️ 70 chat prompts
🤖 7 gemma4:12b replies
🤖 63 dolphin3:latest replies
🔥   1 🥵   7 😎  32 🥶 103 🧊  80

      $1 #224 forum           100.00°C 🥳 1000‰ ~144 used:0  [143]  source:gemma4  
      $2 #184 discussion       55.87°C 🔥  998‰   ~1 used:27 [0]    source:dolphin3
      $3 #160 sujet            42.83°C 🥵  985‰  ~21 used:20 [20]   source:dolphin3
      $4 #164 thème            33.78°C 🥵  936‰  ~19 used:14 [18]   source:dolphin3
      $5 #101 participant      33.69°C 🥵  935‰  ~32 used:23 [31]   source:dolphin3
      $6 #110 contributeur     33.65°C 🥵  934‰  ~20 used:15 [19]   source:dolphin3
      $7 #125 membre           33.24°C 🥵  931‰  ~18 used:11 [17]   source:dolphin3
      $8  #24 concours         31.24°C 🥵  908‰  ~34 used:29 [33]   source:dolphin3
      $9  #62 liste            31.12°C 🥵  906‰  ~33 used:24 [32]   source:dolphin3
     $10 #188 débat            29.87°C 😎  894‰  ~22 used:2  [21]   source:dolphin3
     $11  #91 réponse          29.32°C 😎  889‰  ~35 used:3  [34]   source:dolphin3
     $12  #89 question         29.14°C 😎  887‰  ~36 used:3  [35]   source:dolphin3
     $42 #216 parole           14.53°C 🥶        ~45 used:0  [44]   source:gemma4  
    $145 #103 engagement       -0.03°C 🧊       ~145 used:0  [144]  source:dolphin3
