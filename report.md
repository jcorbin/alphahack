# 2026-02-22

- 🔗 spaceword.org 🧩 2026-02-21 🏁 score 2165 ranked 44.7% 143/320 ⏱️ 10:34:15.350436
- 🔗 alfagok.diginaut.net 🧩 #477 🥳 34 ⏱️ 0:00:34.759500
- 🔗 alphaguess.com 🧩 #944 🥳 28 ⏱️ 0:00:26.007338
- 🔗 dontwordle.com 🧩 #1370 🥳 6 ⏱️ 0:01:31.767668
- 🔗 dictionary.com hurdle 🧩 #1513 🥳 19 ⏱️ 0:03:20.896970
- 🔗 Quordle Classic 🧩 #1490 🥳 score:26 ⏱️ 0:01:57.280947
- 🔗 Octordle Classic 🧩 #1490 🥳 score:56 ⏱️ 0:03:24.545959
- 🔗 squareword.org 🧩 #1483 🥳 8 ⏱️ 0:02:17.932536
- 🔗 cemantle.certitudes.org 🧩 #1420 🥳 136 ⏱️ 0:01:20.147735
- 🔗 cemantix.certitudes.org 🧩 #1453 🥳 184 ⏱️ 0:04:52.339445

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




# [spaceword.org](spaceword.org) 🧩 2026-02-21 🏁 score 2165 ranked 44.7% 143/320 ⏱️ 10:34:15.350436

📜 2 sessions
- tiles: 21/21
- score: 2165 bonus: +65
- rank: 143/320

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ M _ _ F _ _   
      _ _ _ _ A R _ R _ _   
      _ _ _ _ N O _ A _ _   
      _ _ _ _ H O _ U _ _   
      _ _ _ J O K E D _ _   
      _ _ _ _ L I _ _ _ _   
      _ _ _ Z E E _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #477 🥳 34 ⏱️ 0:00:34.759500

🤔 34 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+99741  [ 99741] ex         q2  ? ␅
    @+99741  [ 99741] ex         q3  ? after
    @+111396 [111396] ge         q6  ? ␅
    @+111396 [111396] ge         q7  ? after
    @+130417 [130417] gracieuze  q8  ? ␅
    @+130417 [130417] gracieuze  q9  ? after
    @+139774 [139774] hei        q10 ? ␅
    @+139774 [139774] hei        q11 ? after
    @+144543 [144543] hoek       q12 ? ␅
    @+144543 [144543] hoek       q13 ? after
    @+146204 [146204] hoofd      q14 ? ␅
    @+146204 [146204] hoofd      q15 ? after
    @+147783 [147783] hooi       q16 ? ␅
    @+147783 [147783] hooi       q17 ? after
    @+148503 [148503] hotel      q18 ? ␅
    @+148503 [148503] hotel      q19 ? after
    @+148611 [148611] hotelwezen q22 ? ␅
    @+148611 [148611] hotelwezen q23 ? after
    @+148648 [148648] houd       q24 ? ␅
    @+148648 [148648] houd       q25 ? after
    @+148665 [148665] houder     q28 ? ␅
    @+148665 [148665] houder     q29 ? after
    @+148675 [148675] houdertjes q30 ? ␅
    @+148675 [148675] houdertjes q31 ? after
    @+148679 [148679] houding    q32 ? ␅
    @+148679 [148679] houding    q33 ? it
    @+148679 [148679] houding    done. it
    @+148685 [148685] houdster   q26 ? ␅
    @+148685 [148685] houdster   q27 ? before
    @+148719 [148719] hout       q21 ? before

# [alphaguess.com](alphaguess.com) 🧩 #944 🥳 28 ⏱️ 0:00:26.007338

🤔 28 attempts
📜 1 sessions

    @        [     0] aa           
    @+2      [     2] aahed        
    @+98218  [ 98218] mach         q0  ? ␅
    @+98218  [ 98218] mach         q1  ? after
    @+98218  [ 98218] mach         q2  ? ␅
    @+98218  [ 98218] mach         q3  ? after
    @+104073 [104073] minor        q10 ? ␅
    @+104073 [104073] minor        q11 ? after
    @+106939 [106939] mor          q12 ? ␅
    @+106939 [106939] mor          q13 ? after
    @+108419 [108419] mun          q14 ? ␅
    @+108419 [108419] mun          q15 ? after
    @+108538 [108538] murk         q20 ? ␅
    @+108538 [108538] murk         q21 ? after
    @+108582 [108582] mus          q22 ? ␅
    @+108582 [108582] mus          q23 ? after
    @+108600 [108600] muscle       q26 ? ␅
    @+108600 [108600] muscle       q27 ? it
    @+108600 [108600] muscle       done. it
    @+108621 [108621] musculatures q24 ? ␅
    @+108621 [108621] musculatures q25 ? before
    @+108660 [108660] musical      q18 ? ␅
    @+108660 [108660] musical      q19 ? before
    @+108926 [108926] my           q16 ? ␅
    @+108926 [108926] my           q17 ? before
    @+109935 [109935] ne           q8  ? ␅
    @+109935 [109935] ne           q9  ? before
    @+122779 [122779] parr         q6  ? ␅
    @+122779 [122779] parr         q7  ? before
    @+147374 [147374] rhumb        q4  ? ␅
    @+147374 [147374] rhumb        q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1370 🥳 6 ⏱️ 0:01:31.767668

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:FEEZE n n n n n remain:6482
    ⬜⬜⬜⬜⬜ tried:MIMIC n n n n n remain:2944
    ⬜⬜⬜⬜⬜ tried:DOGGO n n n n n remain:1110
    ⬜⬜⬜⬜⬜ tried:SLYLY n n n n n remain:152
    🟨⬜⬜⬜⬜ tried:ABAKA m n n n n remain:12
    ⬜🟨⬜🟨🟨 tried:PUJAH n m n m m remain:1

    Undos used: 4

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1513 🥳 19 ⏱️ 0:03:20.896970

📜 1 sessions
💰 score: 9700

    3/6
    STOAE ⬜⬜⬜⬜⬜
    CURLY 🟨🟩⬜⬜🟩
    JUICY 🟩🟩🟩🟩🟩
    4/6
    JUICY ⬜⬜⬜⬜⬜
    ROADS ⬜⬜🟨⬜🟨
    STELA 🟨⬜⬜🟨🟨
    NASAL 🟩🟩🟩🟩🟩
    5/6
    NASAL 🟨⬜🟨⬜⬜
    OMENS ⬜⬜🟩🟨🟨
    STERN 🟩⬜🟩⬜🟩
    SKEIN 🟩⬜🟩⬜🟩
    SHEEN 🟩🟩🟩🟩🟩
    5/6
    SHEEN 🟨⬜⬜⬜⬜
    LOTSA ⬜⬜⬜🟩🟨
    GRASP ⬜⬜🟨🟩⬜
    DAISY ⬜🟨🟩🟩⬜
    AMISS 🟩🟩🟩🟩🟩
    Final 2/2
    AGLOW 🟩⬜🟨🟩⬜
    ALOOF 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1490 🥳 score:26 ⏱️ 0:01:57.280947

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SIXTH attempts:5 score:5
2. FRAUD attempts:8 score:8
3. YACHT attempts:6 score:6
4. LEMUR attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1490 🥳 score:56 ⏱️ 0:03:24.545959

📜 1 sessions

Octordle Classic

1. SPICY attempts:3 score:3
2. GUPPY attempts:8 score:8
3. MATCH attempts:10 score:10
4. LURCH attempts:4 score:4
5. ROBOT attempts:6 score:6
6. VITAL attempts:5 score:5
7. BRAWN attempts:11 score:11
8. FLUME attempts:9 score:9

# [squareword.org](squareword.org) 🧩 #1483 🥳 8 ⏱️ 0:02:17.932536

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟩 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T A K E
    C H I N A
    A R S E S
    M E L E E
    S W E L L

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1420 🥳 136 ⏱️ 0:01:20.147735

🤔 137 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 18 chat prompts
🤖 18 dolphin3:latest replies
😱  1 🔥  2 🥵 12 😎 22 🥶 91 🧊  8

      $1 #137 scholar           100.00°C 🥳 1000‰ ~129 used:0  [128]  source:dolphin3
      $2  #75 historian          66.18°C 😱  999‰   ~1 used:14 [0]    source:dolphin3
      $3  #95 linguist           56.56°C 🔥  993‰   ~3 used:3  [2]    source:dolphin3
      $4  #89 sociologist        56.34°C 🔥  992‰   ~2 used:2  [1]    source:dolphin3
      $5  #77 researcher         53.51°C 🥵  987‰   ~4 used:1  [3]    source:dolphin3
      $6  #79 anthropologist     53.41°C 🥵  986‰   ~5 used:0  [4]    source:dolphin3
      $7  #74 biographer         51.07°C 🥵  975‰   ~6 used:0  [5]    source:dolphin3
      $8  #87 philologist        49.67°C 🥵  972‰   ~7 used:0  [6]    source:dolphin3
      $9  #92 ethnographer       49.41°C 🥵  971‰   ~8 used:0  [7]    source:dolphin3
     $10  #82 chronicler         48.92°C 🥵  969‰   ~9 used:0  [8]    source:dolphin3
     $11  #73 author             46.32°C 🥵  961‰  ~10 used:0  [9]    source:dolphin3
     $17  #98 psychologist       39.69°C 😎  878‰  ~16 used:0  [15]   source:dolphin3
     $39  #99 research           26.21°C 🥶        ~42 used:0  [41]   source:dolphin3
    $130 #107 primary            -1.04°C 🧊       ~130 used:0  [129]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1453 🥳 184 ⏱️ 0:04:52.339445

🤔 185 attempts
📜 1 sessions
🫧 12 chat sessions
⁉️ 57 chat prompts
🤖 57 dolphin3:latest replies
😱   1 🔥   1 🥵  10 😎  34 🥶 128 🧊  10

      $1 #185 inconscient     100.00°C 🥳 1000‰ ~175 used:0  [174]  source:dolphin3
      $2 #184 subconscient     64.53°C 😱  999‰   ~1 used:1  [0]    source:dolphin3
      $3 #140 pensée           56.99°C 🔥  992‰   ~2 used:40 [1]    source:dolphin3
      $4 #123 conscience       55.94°C 🥵  989‰  ~43 used:21 [42]   source:dolphin3
      $5 #135 mental           51.35°C 🥵  976‰   ~7 used:8  [6]    source:dolphin3
      $6  #40 émotionnel       49.33°C 🥵  965‰  ~44 used:23 [43]   source:dolphin3
      $7 #120 intuition        48.75°C 🥵  962‰   ~3 used:5  [2]    source:dolphin3
      $8 #127 instinct         47.97°C 🥵  959‰   ~4 used:5  [3]    source:dolphin3
      $9  #53 désir            47.59°C 🥵  955‰  ~42 used:12 [41]   source:dolphin3
     $10 #171 croyance         46.08°C 🥵  948‰   ~5 used:5  [4]    source:dolphin3
     $11  #37 affectivité      43.73°C 🥵  921‰  ~41 used:11 [40]   source:dolphin3
     $14 #152 intellect        42.54°C 😎  890‰   ~9 used:0  [8]    source:dolphin3
     $48 #141 ressenti         29.43°C 🥶        ~51 used:0  [50]   source:dolphin3
    $176  #10 école            -0.70°C 🧊       ~176 used:0  [175]  source:dolphin3
