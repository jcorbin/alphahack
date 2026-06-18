# 2026-06-19

- 🔗 spaceword.org 🧩 2026-06-18 🏁 score 2170 ranked 28.6% 86/301 ⏱️ 0:41:58.226695
- 🔗 alfagok.diginaut.net 🧩 #594 🥳 32 ⏱️ 0:00:47.133672
- 🔗 alphaguess.com 🧩 #1061 🥳 26 ⏱️ 0:00:45.684066
- 🔗 dontwordle.com 🧩 #1487 🥳 6 ⏱️ 0:02:01.609299
- 🔗 dictionary.com hurdle 🧩 #1630 🥳 16 ⏱️ 0:09:26.800264
- 🔗 Quordle Classic 🧩 #1607 🥳 score:22 ⏱️ 0:01:47.843458
- 🔗 Octordle Classic 🧩 #1607 🥳 score:56 ⏱️ 0:03:58.362205
- 🔗 squareword.org 🧩 #1600 🥳 8 ⏱️ 0:02:33.149607
- 🔗 cemantle.certitudes.org 🧩 #1537 🥳 229 ⏱️ 0:02:30.919882
- 🔗 cemantix.certitudes.org 🧩 #1570 🥳 182 ⏱️ 0:02:22.633556

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










# [spaceword.org](spaceword.org) 🧩 2026-06-18 🏁 score 2170 ranked 28.6% 86/301 ⏱️ 0:41:58.226695

📜 3 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 86/301

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ Y _ S A B _ _   
      _ _ _ E _ E _ O _ _   
      _ _ _ A J I _ I _ _   
      _ _ _ _ _ Z _ L _ _   
      _ _ _ _ S O W _ _ _   
      _ _ _ M I R E D _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #594 🥳 32 ⏱️ 0:00:47.133672

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken  
    @+99704  [ 99704] ex       q2  ? ␅
    @+99704  [ 99704] ex       q3  ? after
    @+124603 [124603] gevoel   q6  ? ␅
    @+124603 [124603] gevoel   q7  ? after
    @+137089 [137089] handt    q8  ? ␅
    @+137089 [137089] handt    q9  ? after
    @+139043 [139043] he       q10 ? ␅
    @+139043 [139043] he       q11 ? after
    @+139297 [139297] heem     q20 ? ␅
    @+139297 [139297] heem     q21 ? after
    @+139423 [139423] heer     q22 ? ␅
    @+139423 [139423] heer     q23 ? after
    @+139481 [139481] heers    q24 ? ␅
    @+139481 [139481] heers    q25 ? after
    @+139489 [139489] heersen  q30 ? ␅
    @+139489 [139489] heersen  q31 ? it
    @+139489 [139489] heersen  done. it
    @+139495 [139495] heersers q28 ? ␅
    @+139495 [139495] heersers q29 ? before
    @+139517 [139517] hees     q26 ? ␅
    @+139517 [139517] hees     q27 ? before
    @+139578 [139578] hef      q18 ? ␅
    @+139578 [139578] hef      q19 ? before
    @+140284 [140284] helder   q16 ? ␅
    @+140284 [140284] helder   q17 ? before
    @+141563 [141563] herfst   q14 ? ␅
    @+141563 [141563] herfst   q15 ? before
    @+144288 [144288] hockey   q12 ? ␅
    @+144288 [144288] hockey   q13 ? before
    @+149599 [149599] huishoud q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1061 🥳 26 ⏱️ 0:00:45.684066

🤔 26 attempts
📜 1 sessions

    @        [     0] aa       
    @+1      [     1] aah      
    @+2      [     2] aahed    
    @+3      [     3] aahing   
    @+98214  [ 98214] mach     q0  ? ␅
    @+98214  [ 98214] mach     q1  ? after
    @+147364 [147364] rhotic   q2  ? ␅
    @+147364 [147364] rhotic   q3  ? after
    @+153313 [153313] sea      q8  ? ␅
    @+153313 [153313] sea      q9  ? after
    @+154828 [154828] sequence q12 ? ␅
    @+154828 [154828] sequence q13 ? after
    @+155427 [155427] sha      q14 ? ␅
    @+155427 [155427] sha      q15 ? after
    @+155455 [155455] shad     q22 ? ␅
    @+155455 [155455] shad     q23 ? after
    @+155488 [155488] shadow   q24 ? ␅
    @+155488 [155488] shadow   q25 ? it
    @+155488 [155488] shadow   done. it
    @+155524 [155524] shag     q20 ? ␅
    @+155524 [155524] shag     q21 ? before
    @+155647 [155647] shame    q18 ? ␅
    @+155647 [155647] shame    q19 ? before
    @+155879 [155879] shaw     q16 ? ␅
    @+155879 [155879] shaw     q17 ? before
    @+156349 [156349] ship     q10 ? ␅
    @+156349 [156349] ship     q11 ? before
    @+159481 [159481] slop     q6  ? ␅
    @+159481 [159481] slop     q7  ? before
    @+171634 [171634] ta       q4  ? ␅
    @+171634 [171634] ta       q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1487 🥳 6 ⏱️ 0:02:01.609299

📜 1 sessions
💰 score: 35

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:YUPPY n n n n n remain:7572
    ⬜⬜⬜⬜⬜ tried:NOONS n n n n n remain:1841
    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:742
    ⬜🟩⬜⬜⬜ tried:GRRRL n Y n n n remain:58
    ⬜🟩⬜⬜⬜ tried:CRWTH n Y n n n remain:20
    ⬜🟩🟩⬜⬜ tried:FRIZZ n Y Y n n remain:5

    Undos used: 4

      5 words remaining
    x 7 unused letters
    = 35 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1630 🥳 16 ⏱️ 0:09:26.800264

📜 1 sessions
💰 score: 10000

    4/6
    AEONS ⬜⬜⬜⬜⬜
    FLUTY ⬜🟨⬜⬜🟨
    LYRIC 🟩🟩⬜⬜⬜
    LYMPH 🟩🟩🟩🟩🟩
    4/6
    LYMPH ⬜⬜⬜⬜⬜
    AIDER 🟨⬜⬜⬜⬜
    BANJO 🟨🟩⬜⬜🟩
    TABOO 🟩🟩🟩🟩🟩
    3/6
    TABOO 🟨⬜⬜⬜⬜
    ISLET 🟩⬜⬜⬜🟨
    ITCHY 🟩🟩🟩🟩🟩
    4/6
    ITCHY 🟨⬜⬜⬜⬜
    SLAIN ⬜🟨🟨🟨⬜
    RIVAL ⬜🟩🟨🟨🟨
    VIOLA 🟩🟩🟩🟩🟩
    Final 1/2
    ABHOR 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1607 🥳 score:22 ⏱️ 0:01:47.843458

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. ALOUD attempts:5 score:5
2. POINT attempts:7 score:7
3. GLOBE attempts:6 score:6
4. GROIN attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1607 🥳 score:56 ⏱️ 0:03:58.362205

📜 1 sessions

Octordle Classic

1. MAYOR attempts:8 score:8
2. VOGUE attempts:10 score:10
3. SLURP attempts:5 score:5
4. TWIXT attempts:6 score:6
5. STAIN attempts:9 score:9
6. MAGIC attempts:10 score:11
7. THRUM attempts:3 score:3
8. UNSET attempts:4 score:4

# [squareword.org](squareword.org) 🧩 #1600 🥳 8 ⏱️ 0:02:33.149607

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C A R S
    C O R A L
    A M I G O
    R E S E T
    F R E S H

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1537 🥳 229 ⏱️ 0:02:30.919882

🤔 230 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 39 chat prompts
🤖 39 dolphin3:latest replies
🔥   2 🥵  13 😎  30 🥶 156 🧊  28

      $1 #230 aviation        100.00°C 🥳 1000‰ ~202 used:0  [201]  source:dolphin3
      $2 #202 aircraft         61.36°C 🔥  997‰   ~1 used:3  [0]    source:dolphin3
      $3 #218 airplane         54.14°C 🔥  992‰   ~2 used:3  [1]    source:dolphin3
      $4 #203 airport          50.10°C 🥵  989‰   ~3 used:0  [2]    source:dolphin3
      $5 #220 jet              47.77°C 🥵  986‰   ~4 used:0  [3]    source:dolphin3
      $6 #209 plane            43.31°C 🥵  977‰   ~5 used:0  [4]    source:dolphin3
      $7 #120 cargo            41.39°C 🥵  969‰  ~40 used:15 [39]   source:dolphin3
      $8 #191 air              40.46°C 🥵  967‰  ~10 used:3  [9]    source:dolphin3
      $9 #201 transportation   40.33°C 🥵  966‰   ~6 used:1  [5]    source:dolphin3
     $10 #167 trucking         38.20°C 🥵  954‰  ~14 used:7  [13]   source:dolphin3
     $11 #222 cockpit          37.63°C 🥵  953‰   ~7 used:0  [6]    source:dolphin3
     $17 #206 freighter        32.40°C 😎  898‰  ~15 used:0  [14]   source:dolphin3
     $47 #184 insurance        18.06°C 🥶        ~48 used:0  [47]   source:dolphin3
    $203  #94 hubcap           -0.02°C 🧊       ~203 used:0  [202]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1570 🥳 182 ⏱️ 0:02:22.633556

🤔 183 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 19 chat prompts
🤖 19 dolphin3:latest replies
🔥  4 🥵 12 😎 27 🥶 90 🧊 49

      $1 #183 galerie          100.00°C 🥳 1000‰ ~134 used:0  [133]  source:dolphin3
      $2 #162 exposition        53.64°C 🔥  998‰   ~2 used:2  [1]    source:dolphin3
      $3 #181 vernissage        51.21°C 🔥  997‰   ~1 used:0  [0]    source:dolphin3
      $4 #115 photographie      44.44°C 🔥  992‰   ~4 used:10 [3]    source:dolphin3
      $5 #123 photo             43.78°C 🔥  991‰   ~3 used:8  [2]    source:dolphin3
      $6  #65 artiste           42.66°C 🥵  989‰  ~16 used:6  [15]   source:dolphin3
      $7  #60 peinture          41.23°C 🥵  984‰  ~15 used:4  [14]   source:dolphin3
      $8  #73 fresque           37.83°C 🥵  971‰  ~13 used:3  [12]   source:dolphin3
      $9  #42 art               37.55°C 🥵  970‰  ~12 used:2  [11]   source:dolphin3
     $10  #18 collection        36.88°C 🥵  959‰  ~14 used:3  [13]   source:dolphin3
     $11  #92 fresquiste        36.86°C 🥵  958‰   ~5 used:0  [4]    source:dolphin3
     $18  #98 portraitiste      31.32°C 😎  871‰  ~17 used:0  [16]   source:dolphin3
     $45  #97 paysagiste        19.41°C 🥶        ~46 used:0  [45]   source:dolphin3
    $135  #13 école             -0.11°C 🧊       ~135 used:0  [134]  source:dolphin3
