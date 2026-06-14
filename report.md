# 2026-06-15

- 🔗 spaceword.org 🧩 2026-06-14 🏁 score 2164 ranked 47.3% 147/311 ⏱️ 0:20:38.854803
- 🔗 alfagok.diginaut.net 🧩 #590 🥳 26 ⏱️ 0:00:50.023313
- 🔗 alphaguess.com 🧩 #1057 🥳 30 ⏱️ 0:01:00.167498
- 🔗 dontwordle.com 🧩 #1483 🥳 6 ⏱️ 0:02:05.257261
- 🔗 dictionary.com hurdle 🧩 #1626 🥳 19 ⏱️ 0:04:21.554541
- 🔗 Quordle Classic 🧩 #1603 🥳 score:18 ⏱️ 0:01:10.119916
- 🔗 Octordle Classic 🧩 #1603 🥳 score:58 ⏱️ 0:03:03.937196
- 🔗 squareword.org 🧩 #1596 🥳 8 ⏱️ 0:02:32.089243
- 🔗 cemantle.certitudes.org 🧩 #1533 🥳 135 ⏱️ 0:01:55.800107
- 🔗 cemantix.certitudes.org 🧩 #1566 🥳 180 ⏱️ 1:04:52.234416

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






# [spaceword.org](spaceword.org) 🧩 2026-06-14 🏁 score 2164 ranked 47.3% 147/311 ⏱️ 0:20:38.854803

📜 4 sessions
- tiles: 21/21
- score: 2164 bonus: +64
- rank: 147/311

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ O _ _ _ C _ _ _ _   
      _ X _ _ K I _ _ _ O   
      _ E O L I T H _ _ D   
      _ R _ I T E M I Z E   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #590 🥳 26 ⏱️ 0:00:50.023313

🤔 26 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199766 [199766] lijm      q0  ? ␅
    @+199766 [199766] lijm      q1  ? after
    @+199766 [199766] lijm      q2  ? ␅
    @+199766 [199766] lijm      q3  ? after
    @+247637 [247637] op        q6  ? ␅
    @+247637 [247637] op        q7  ? after
    @+273434 [273434] proef     q8  ? ␅
    @+273434 [273434] proef     q9  ? after
    @+286502 [286502] rijs      q10 ? ␅
    @+286502 [286502] rijs      q11 ? after
    @+292729 [292729] samen     q12 ? ␅
    @+292729 [292729] samen     q13 ? after
    @+296162 [296162] schepping q14 ? ␅
    @+296162 [296162] schepping q15 ? after
    @+297746 [297746] school    q16 ? ␅
    @+297746 [297746] school    q17 ? after
    @+298654 [298654] schot     q18 ? ␅
    @+298654 [298654] schot     q19 ? after
    @+298731 [298731] schouder  q24 ? ␅
    @+298731 [298731] schouder  q25 ? it
    @+298731 [298731] schouder  done. it
    @+298892 [298892] schraap   q22 ? ␅
    @+298892 [298892] schraap   q23 ? before
    @+299129 [299129] schrijf   q20 ? ␅
    @+299129 [299129] schrijf   q21 ? before
    @+299628 [299628] schub     q4  ? ␅
    @+299628 [299628] schub     q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1057 🥳 30 ⏱️ 0:01:00.167498

🤔 30 attempts
📜 1 sessions

    @        [     0] aa     
    @+98214  [ 98214] mach   q0  ? ␅
    @+98214  [ 98214] mach   q1  ? after
    @+147364 [147364] rhotic q2  ? ␅
    @+147364 [147364] rhotic q3  ? after
    @+153313 [153313] sea    q8  ? ␅
    @+153313 [153313] sea    q9  ? after
    @+156349 [156349] ship   q10 ? ␅
    @+156349 [156349] ship   q11 ? after
    @+156731 [156731] shop   q16 ? ␅
    @+156731 [156731] shop   q17 ? after
    @+156909 [156909] shovel q18 ? ␅
    @+156909 [156909] shovel q19 ? after
    @+157007 [157007] shred  q20 ? ␅
    @+157007 [157007] shred  q21 ? after
    @+157032 [157032] shri   q22 ? ␅
    @+157032 [157032] shri   q23 ? after
    @+157072 [157072] shrine q24 ? ␅
    @+157072 [157072] shrine q25 ? after
    @+157076 [157076] shrink q28 ? ␅
    @+157076 [157076] shrink q29 ? it
    @+157076 [157076] shrink done. it
    @+157087 [157087] shrive q26 ? ␅
    @+157087 [157087] shrive q27 ? before
    @+157113 [157113] shrub  q14 ? ␅
    @+157113 [157113] shrub  q15 ? before
    @+157877 [157877] sim    q12 ? ␅
    @+157877 [157877] sim    q13 ? before
    @+159481 [159481] slop   q6  ? ␅
    @+159481 [159481] slop   q7  ? before
    @+171634 [171634] ta     q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1483 🥳 6 ⏱️ 0:02:05.257261

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:YUMMY n n n n n remain:7572
    ⬜⬜⬜⬜⬜ tried:OXBOW n n n n n remain:3834
    ⬜⬜⬜⬜⬜ tried:KININ n n n n n remain:1454
    ⬜⬜⬜⬜🟨 tried:PHPHT n n n n m remain:231
    ⬜🟨⬜🟨⬜ tried:CASTS n m n m n remain:20
    ⬜🟨🟩🟨🟨 tried:TETRA n m Y m m remain:3

    Undos used: 3

      3 words remaining
    x 8 unused letters
    = 24 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1626 🥳 19 ⏱️ 0:04:21.554541

📜 1 sessions
💰 score: 9700

    6/6
    LARES 🟨⬜⬜⬜🟩
    IDOLS ⬜⬜🟩🟨🟩
    BLOGS ⬜🟩🟩⬜🟩
    CLOPS ⬜🟩🟩⬜🟩
    FLOWS 🟩🟩🟩⬜🟩
    FLOSS 🟩🟩🟩🟩🟩
    3/6
    FLOSS ⬜⬜⬜🟩⬜
    ARISE ⬜🟨⬜🟩🟩
    PURSE 🟩🟩🟩🟩🟩
    5/6
    PURSE 🟩⬜⬜⬜🟩
    PLANE 🟩⬜⬜⬜🟩
    PYXIE 🟩⬜⬜⬜🟩
    POMBE 🟩⬜⬜⬜🟩
    PEEVE 🟩🟩🟩🟩🟩
    3/6
    PEEVE ⬜⬜⬜⬜🟩
    ANILE 🟨⬜⬜🟩🟩
    SCALE 🟩🟩🟩🟩🟩
    Final 2/2
    HUMIC ⬜🟩🟩🟩🟨
    CUMIN 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1603 🥳 score:18 ⏱️ 0:01:10.119916

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. GAUNT attempts:6 score:6
2. SNEAK attempts:5 score:5
3. ROUTE attempts:3 score:3
4. POKER attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1603 🥳 score:58 ⏱️ 0:03:03.937196

📜 1 sessions

Octordle Classic

1. ADAPT attempts:8 score:8
2. TEPID attempts:9 score:9
3. PIANO attempts:7 score:7
4. CEASE attempts:4 score:4
5. BORAX attempts:10 score:10
6. AGATE attempts:11 score:11
7. CHAOS attempts:3 score:3
8. QUASI attempts:6 score:6

# [squareword.org](squareword.org) 🧩 #1596 🥳 8 ⏱️ 0:02:32.089243

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P A S M
    T E M P I
    R O B O T
    I N E R T
    P Y R E S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1533 🥳 135 ⏱️ 0:01:55.800107

🤔 136 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 29 chat prompts
🤖 29 dolphin3:latest replies
🔥   2 🥵   5 😎  19 🥶 104 🧊   5

      $1 #136 implication      100.00°C 🥳 1000‰ ~131 used:0  [130]  source:dolphin3
      $2 #133 consequence       53.58°C 🔥  997‰   ~1 used:2  [0]    source:dolphin3
      $3 #127 inference         51.84°C 🔥  996‰   ~2 used:4  [1]    source:dolphin3
      $4  #80 contradiction     48.47°C 🥵  989‰  ~23 used:16 [22]   source:dolphin3
      $5 #112 assumption        46.10°C 🥵  981‰   ~3 used:1  [2]    source:dolphin3
      $6  #86 dichotomy         44.18°C 🥵  973‰  ~21 used:13 [20]   source:dolphin3
      $7  #60 paradox           40.95°C 🥵  943‰  ~22 used:13 [21]   source:dolphin3
      $8 #130 presumption       40.06°C 🥵  932‰   ~4 used:0  [3]    source:dolphin3
      $9 #110 hypothesis        37.81°C 😎  893‰   ~5 used:1  [4]    source:dolphin3
     $10  #65 theory            37.78°C 😎  892‰  ~24 used:2  [23]   source:dolphin3
     $11  #62 perception        37.50°C 😎  885‰  ~25 used:2  [24]   source:dolphin3
     $12  #99 ambiguity         37.47°C 😎  883‰   ~6 used:1  [5]    source:dolphin3
     $28  #72 paradoxical       28.37°C 🥶        ~32 used:0  [31]   source:dolphin3
    $132  #30 night             -0.49°C 🧊       ~132 used:0  [131]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1566 🥳 180 ⏱️ 1:04:52.234416

🤔 181 attempts
📜 1 sessions
🫧 13 chat sessions
⁉️ 57 chat prompts
🤖 57 dolphin3:latest replies
😱   1 🔥   2 🥵  11 😎  29 🥶 100 🧊  37

      $1 #181 architecte       100.00°C 🥳 1000‰ ~144 used:0  [143]  source:dolphin3
      $2  #54 architecture      63.70°C 😱  999‰   ~1 used:75 [0]    source:dolphin3
      $3  #53 architectural     63.35°C 🔥  998‰  ~13 used:30 [12]   source:dolphin3
      $4 #153 bâtiment          53.20°C 🔥  994‰   ~7 used:13 [6]    source:dolphin3
      $5  #56 construction      48.09°C 🥵  987‰  ~14 used:7  [13]   source:dolphin3
      $6 #166 édifice           44.87°C 🥵  983‰   ~8 used:2  [7]    source:dolphin3
      $7 #145 bâtisseur         44.53°C 🥵  981‰   ~9 used:2  [8]    source:dolphin3
      $8  #72 urbanisme         44.11°C 🥵  980‰  ~10 used:2  [9]    source:dolphin3
      $9 #150 urbanistique      42.64°C 🥵  975‰  ~11 used:2  [10]   source:dolphin3
     $10 #177 architectonique   39.29°C 🥵  957‰   ~2 used:1  [1]    source:dolphin3
     $11 #111 façade            38.48°C 🥵  953‰  ~12 used:2  [11]   source:dolphin3
     $16 #105 maçonnerie        31.81°C 😎  889‰  ~15 used:0  [14]   source:dolphin3
     $45  #98 moderne           18.24°C 🥶        ~51 used:0  [50]   source:dolphin3
    $145 #155 glossaire         -0.29°C 🧊       ~145 used:0  [144]  source:dolphin3
