# 2026-04-28

- 🔗 spaceword.org 🧩 2026-04-27 🏁 score 2173 ranked 6.2% 24/384 ⏱️ 0:14:12.355137
- 🔗 alfagok.diginaut.net 🧩 #542 🥳 36 ⏱️ 0:00:49.232123
- 🔗 alphaguess.com 🧩 #1009 🥳 32 ⏱️ 0:00:32.143737
- 🔗 dontwordle.com 🧩 #1435 😳 6 ⏱️ 0:02:02.320159
- 🔗 dictionary.com hurdle 🧩 #1578 🥳 18 ⏱️ 0:04:07.553101
- 🔗 Quordle Classic 🧩 #1555 🥳 score:21 ⏱️ 0:01:31.264391
- 🔗 Octordle Classic 🧩 #1555 😦 score:66 ⏱️ 0:05:20.866124
- 🔗 squareword.org 🧩 #1548 🥳 8 ⏱️ 0:02:13.416645
- 🔗 cemantle.certitudes.org 🧩 #1485 🥳 267 ⏱️ 0:03:10.884879
- 🔗 cemantix.certitudes.org 🧩 #1518 🥳 109 ⏱️ 0:01:12.329722

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


























































# [spaceword.org](spaceword.org) 🧩 2026-04-27 🏁 score 2173 ranked 6.2% 24/384 ⏱️ 0:14:12.355137

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 24/384

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ F _ D E V _ Q _ L   
      _ A _ A G A T I Z E   
      _ R U G O S A _ _ I   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #542 🥳 36 ⏱️ 0:00:49.232123

🤔 36 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+199704 [199704] lijk        q0  ? ␅
    @+199704 [199704] lijk        q1  ? after
    @+199704 [199704] lijk        q2  ? ␅
    @+199704 [199704] lijk        q3  ? after
    @+199704 [199704] lijk        q4  ? ␅
    @+199704 [199704] lijk        q5  ? after
    @+299649 [299649] schroot     q6  ? ␅
    @+299649 [299649] schroot     q7  ? after
    @+324239 [324239] sub         q10 ? ␅
    @+324239 [324239] sub         q11 ? after
    @+327230 [327230] tafel       q16 ? ␅
    @+327230 [327230] tafel       q17 ? after
    @+328818 [328818] technologie q18 ? ␅
    @+328818 [328818] technologie q19 ? after
    @+328971 [328971] teen        q24 ? ␅
    @+328971 [328971] teen        q25 ? after
    @+329000 [329000] teer        q26 ? ␅
    @+329000 [329000] teer        q27 ? after
    @+329071 [329071] teevee      q28 ? ␅
    @+329071 [329071] teevee      q29 ? after
    @+329084 [329084] tegel       q30 ? ␅
    @+329084 [329084] tegel       q31 ? after
    @+329098 [329098] tegelijk    q34 ? ␅
    @+329098 [329098] tegelijk    q35 ? it
    @+329098 [329098] tegelijk    done. it
    @+329111 [329111] tegeltje    q32 ? ␅
    @+329111 [329111] tegeltje    q33 ? before
    @+329144 [329144] tegen       q22 ? ␅
    @+329144 [329144] tegen       q23 ? before
    @+329575 [329575] teken       q21 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1009 🥳 32 ⏱️ 0:00:32.143737

🤔 32 attempts
📜 1 sessions

    @        [     0] aa       
    @+98216  [ 98216] mach     q0  ? ␅
    @+98216  [ 98216] mach     q1  ? after
    @+147366 [147366] rhotic   q2  ? ␅
    @+147366 [147366] rhotic   q3  ? after
    @+171636 [171636] ta       q4  ? ␅
    @+171636 [171636] ta       q5  ? after
    @+182000 [182000] un       q6  ? ␅
    @+182000 [182000] un       q7  ? after
    @+189262 [189262] vicar    q8  ? ␅
    @+189262 [189262] vicar    q9  ? after
    @+190145 [190145] vivisect q14 ? ␅
    @+190145 [190145] vivisect q15 ? after
    @+190594 [190594] vouvray  q16 ? ␅
    @+190594 [190594] vouvray  q17 ? after
    @+190813 [190813] wae      q18 ? ␅
    @+190813 [190813] wae      q19 ? after
    @+190855 [190855] wag      q22 ? ␅
    @+190855 [190855] wag      q23 ? after
    @+190870 [190870] wagger   q26 ? ␅
    @+190870 [190870] wagger   q27 ? after
    @+190875 [190875] waggish  q28 ? ␅
    @+190875 [190875] waggish  q29 ? after
    @+190879 [190879] waggle   q30 ? ␅
    @+190879 [190879] waggle   q31 ? it
    @+190879 [190879] waggle   done. it
    @+190886 [190886] waggon   q24 ? ␅
    @+190886 [190886] waggon   q25 ? before
    @+190926 [190926] wail     q20 ? ␅
    @+190926 [190926] wail     q21 ? before
    @+191042 [191042] walk     q13 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1435 😳 6 ⏱️ 0:02:02.320159

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:7870
    ⬜⬜⬜⬜⬜ tried:TAZZA n n n n n remain:3091
    ⬜⬜⬜⬜⬜ tried:OPPOS n n n n n remain:569
    ⬜⬜⬜🟩⬜ tried:DRYLY n n n Y n remain:9
    ⬜⬜🟨🟩⬜ tried:KNELL n n m Y n remain:2
    🟩🟩🟩🟩🟩 tried:BUGLE Y Y Y Y Y remain:0

    Undos used: 3

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1578 🥳 18 ⏱️ 0:04:07.553101

📜 1 sessions
💰 score: 9800

    5/6
    NEARS ⬜⬜⬜🟨⬜
    GRIOT ⬜🟩⬜🟩⬜
    BROOD ⬜🟩🟩🟩⬜
    CROOK ⬜🟩🟩🟩⬜
    PROOF 🟩🟩🟩🟩🟩
    3/6
    PROOF 🟨⬜⬜🟩⬜
    TYPOS 🟨⬜🟩🟩⬜
    DEPOT 🟩🟩🟩🟩🟩
    4/6
    DEPOT ⬜🟨⬜⬜⬜
    SANER ⬜⬜🟨🟨🟨
    BRINE ⬜🟩🟩🟩🟩
    URINE 🟩🟩🟩🟩🟩
    5/6
    URINE ⬜🟨🟩⬜⬜
    HAIRS 🟨⬜🟩🟩⬜
    CHIRK ⬜🟩🟩🟩⬜
    THIRL 🟩🟩🟩🟩⬜
    THIRD 🟩🟩🟩🟩🟩
    Final 1/2
    CREPT 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1555 🥳 score:21 ⏱️ 0:01:31.264391

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. CLINK attempts:7 score:7
2. BONUS attempts:5 score:5
3. BRUSH attempts:6 score:6
4. DRIER attempts:3 score:3

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1555 😦 score:66 ⏱️ 0:05:20.866124

📜 1 sessions

Octordle Classic

1. REMIT attempts:13 score:13
2. CHIL_ -ABDEFGKMNOQRSTUXYZ attempts:13 score:-1
3. FOLIO attempts:8 score:8
4. BUYER attempts:7 score:7
5. COULD attempts:6 score:6
6. FIERY attempts:4 score:4
7. GLAZE attempts:9 score:9
8. QUEEN attempts:5 score:5

# [squareword.org](squareword.org) 🧩 #1548 🥳 8 ⏱️ 0:02:13.416645

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟨 🟨
    🟨 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C R E S T
    A O R T A
    M O R A L
    E M O T E
    L Y R E S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1485 🥳 267 ⏱️ 0:03:10.884879

🤔 268 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 55 chat prompts
🤖 55 dolphin3:latest replies
😱   1 🔥   2 🥵  10 😎  54 🥶 188 🧊  12

      $1 #268 hunting         100.00°C 🥳 1000‰ ~256 used:0  [255]  source:dolphin3
      $2 #254 hunt             70.47°C 😱  999‰   ~1 used:3  [0]    source:dolphin3
      $3  #31 fishing          58.21°C 🔥  996‰   ~8 used:71 [7]    source:dolphin3
      $4 #225 deer             55.48°C 🔥  994‰   ~2 used:2  [1]    source:dolphin3
      $5 #248 elk              49.02°C 🥵  988‰   ~3 used:0  [2]    source:dolphin3
      $6 #255 moose            45.83°C 🥵  981‰   ~4 used:0  [3]    source:dolphin3
      $7 #151 angling          45.44°C 🥵  977‰  ~65 used:21 [64]   source:dolphin3
      $8  #97 wildlife         45.10°C 🥵  972‰  ~64 used:17 [63]   source:dolphin3
      $9 #191 boating          41.92°C 🥵  954‰   ~7 used:5  [6]    source:dolphin3
     $10 #121 sportfishing     40.13°C 🥵  946‰   ~9 used:9  [8]    source:dolphin3
     $11  #64 habitat          39.24°C 🥵  931‰  ~10 used:9  [9]    source:dolphin3
     $15 #259 rifle            36.76°C 😎  894‰  ~12 used:0  [11]   source:dolphin3
     $69  #66 saltwater        23.14°C 🥶        ~71 used:0  [70]   source:dolphin3
    $257 #201 anchor           -0.04°C 🧊       ~257 used:0  [256]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1518 🥳 109 ⏱️ 0:01:12.329722

🤔 110 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 16 chat prompts
🤖 16 dolphin3:latest replies
🔥  2 🥵 14 😎 11 🥶 67 🧊 15

      $1 #110 controverse        100.00°C 🥳 1000‰  ~95 used:0 [94]   source:dolphin3
      $2  #68 débat               56.14°C 🔥  997‰   ~1 used:3 [0]    source:dolphin3
      $3  #64 confrontation       43.64°C 🔥  992‰   ~2 used:3 [1]    source:dolphin3
      $4  #57 critique            42.61°C 🥵  987‰  ~15 used:3 [14]   source:dolphin3
      $5  #62 interrogation       41.85°C 🥵  984‰   ~3 used:1 [2]    source:dolphin3
      $6 #103 conflit             41.73°C 🥵  983‰   ~4 used:0 [3]    source:dolphin3
      $7  #66 discussion          39.21°C 🥵  975‰   ~5 used:0 [4]    source:dolphin3
      $8  #61 interprétation      38.68°C 🥵  974‰  ~14 used:2 [13]   source:dolphin3
      $9  #73 questionnement      38.34°C 🥵  972‰   ~6 used:0 [5]    source:dolphin3
     $10 #100 affrontement        37.58°C 🥵  963‰   ~7 used:0 [6]    source:dolphin3
     $11  #98 théorie             37.31°C 🥵  958‰   ~8 used:0 [7]    source:dolphin3
     $18  #83 affirmation         33.66°C 😎  881‰  ~17 used:0 [16]   source:dolphin3
     $29  #97 raisonnement        23.37°C 🥶        ~32 used:0 [31]   source:dolphin3
     $96  #13 section             -0.86°C 🧊        ~96 used:0 [95]   source:dolphin3
