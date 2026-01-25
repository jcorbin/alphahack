# 2026-01-26

- 🔗 spaceword.org 🧩 2026-01-25 🏁 score 2170 ranked 26.9% 86/320 ⏱️ 0:53:49.541236
- 🔗 alfagok.diginaut.net 🧩 #450 🥳 32 ⏱️ 0:00:41.490385
- 🔗 alphaguess.com 🧩 #917 🥳 22 ⏱️ 0:00:26.078154
- 🔗 dontwordle.com 🧩 #1343 🥳 6 ⏱️ 0:04:23.593603
- 🔗 dictionary.com hurdle 🧩 #1486 🥳 17 ⏱️ 0:03:28.923205
- 🔗 Quordle Classic 🧩 #1463 😦 score:25 ⏱️ 0:02:22.906472
- 🔗 Octordle Classic 🧩 #1463 🥳 score:59 ⏱️ 0:04:01.397014
- 🔗 squareword.org 🧩 #1456 🥳 8 ⏱️ 0:02:05.897159
- 🔗 cemantle.certitudes.org 🧩 #1393 🥳 249 ⏱️ 0:05:09.826228
- 🔗 cemantix.certitudes.org 🧩 #1426 🥳 274 ⏱️ 0:12:22.953623
- 🔗 Quordle Rescue 🧩 #77 🥳 score:26 ⏱️ 0:01:44.618264

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











# [spaceword.org](spaceword.org) 🧩 2026-01-25 🏁 score 2170 ranked 26.9% 86/320 ⏱️ 0:53:49.541236

📜 3 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 86/320

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ T E G U _ _ _ _   
      _ _ S R I _ _ _ _ _   
      _ _ U _ _ T O W _ _   
      _ _ B I F I D A _ _   
      _ _ A _ _ Z A X _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #450 🥳 32 ⏱️ 0:00:41.490385

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+199833 [199833] lijm        q0  ? ␅
    @+199833 [199833] lijm        q1  ? after
    @+299738 [299738] schub       q2  ? ␅
    @+299738 [299738] schub       q3  ? after
    @+324308 [324308] sub         q6  ? ␅
    @+324308 [324308] sub         q7  ? after
    @+327299 [327299] tafel       q12 ? ␅
    @+327299 [327299] tafel       q13 ? after
    @+328040 [328040] tank        q16 ? ␅
    @+328040 [328040] tank        q17 ? after
    @+328450 [328450] tart        q18 ? ␅
    @+328450 [328450] tart        q19 ? after
    @+328647 [328647] taxi        q20 ? ␅
    @+328647 [328647] taxi        q21 ? after
    @+328764 [328764] teak        q22 ? ␅
    @+328764 [328764] teak        q23 ? after
    @+328772 [328772] team        q24 ? ␅
    @+328772 [328772] team        q25 ? after
    @+328830 [328830] tearjerker  q26 ? ␅
    @+328830 [328830] tearjerker  q27 ? after
    @+328853 [328853] techniek    q28 ? ␅
    @+328853 [328853] techniek    q29 ? after
    @+328864 [328864] technisch   q30 ? ␅
    @+328864 [328864] technisch   q31 ? it
    @+328864 [328864] technisch   done. it
    @+328887 [328887] technologie q14 ? ␅
    @+328887 [328887] technologie q15 ? before
    @+330491 [330491] televisie   q10 ? ␅
    @+330491 [330491] televisie   q11 ? before
    @+336905 [336905] toetsing    q9  ? before

# [alphaguess.com](alphaguess.com) 🧩 #917 🥳 22 ⏱️ 0:00:26.078154

🤔 22 attempts
📜 1 sessions

    @       [    0] aa            
    @+1     [    1] aah           
    @+2     [    2] aahed         
    @+3     [    3] aahing        
    @+47382 [47382] dis           q2  ? ␅
    @+47382 [47382] dis           q3  ? after
    @+60085 [60085] face          q6  ? ␅
    @+60085 [60085] face          q7  ? after
    @+66441 [66441] french        q8  ? ␅
    @+66441 [66441] french        q9  ? after
    @+68007 [68007] gall          q12 ? ␅
    @+68007 [68007] gall          q13 ? after
    @+68158 [68158] galvanometers q18 ? ␅
    @+68158 [68158] galvanometers q19 ? after
    @+68212 [68212] game          q20 ? ␅
    @+68212 [68212] game          q21 ? it
    @+68212 [68212] game          done. it
    @+68309 [68309] gan           q16 ? ␅
    @+68309 [68309] gan           q17 ? before
    @+68789 [68789] gate          q14 ? ␅
    @+68789 [68789] gate          q15 ? before
    @+69621 [69621] geosynclinal  q10 ? ␅
    @+69621 [69621] geosynclinal  q11 ? before
    @+72801 [72801] gremmy        q4  ? ␅
    @+72801 [72801] gremmy        q5  ? before
    @+98220 [98220] mach          q0  ? ␅
    @+98220 [98220] mach          q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1343 🥳 6 ⏱️ 0:04:23.593603

📜 1 sessions
💰 score: 54

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:QUEUE n n n n n remain:5479
    ⬜⬜⬜⬜⬜ tried:WIGGY n n n n n remain:1920
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:879
    ⬜🟩⬜⬜⬜ tried:BOBOS n Y n n n remain:48
    ⬜🟩⬜⬜🟩 tried:DONNA n Y n n Y remain:11
    ⬜🟩⬜⬜🟩 tried:MOMMA n Y n n Y remain:6

    Undos used: 5

      6 words remaining
    x 9 unused letters
    = 54 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1486 🥳 17 ⏱️ 0:03:28.923205

📜 1 sessions
💰 score: 9900

    5/6
    RALES ⬜⬜🟨⬜⬜
    LOGIN 🟨⬜⬜🟨🟨
    CLINK ⬜🟩🟩🟩⬜
    BLIND ⬜🟩🟩🟩⬜
    FLINT 🟩🟩🟩🟩🟩
    3/6
    FLINT ⬜⬜⬜⬜⬜
    ROAMS 🟨⬜⬜⬜🟨
    USHER 🟩🟩🟩🟩🟩
    3/6
    USHER 🟨⬜⬜🟨🟨
    PURGE 🟩🟨🟨⬜🟩
    PRUNE 🟩🟩🟩🟩🟩
    4/6
    PRUNE ⬜🟨⬜⬜⬜
    HORSY 🟨⬜🟨⬜⬜
    THIRL ⬜🟩🟨🟨⬜
    CHAIR 🟩🟩🟩🟩🟩
    Final 2/2
    NOVEL 🟨⬜⬜🟩🟩
    KNEEL 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1463 😦 score:25 ⏱️ 0:02:22.906472

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. CRACK attempts:9 score:9
2. DEVIL attempts:4 score:4
3. _AKER -CDFGHILNOPSTVW attempts:9 score:-1
4. SAVOR attempts:3 score:3

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1463 🥳 score:59 ⏱️ 0:04:01.397014

📜 1 sessions

Octordle Classic

1. THIGH attempts:7 score:7
2. DEBAR attempts:8 score:8
3. PHONY attempts:9 score:9
4. AMISS attempts:10 score:10
5. UNDER attempts:3 score:3
6. POSER attempts:6 score:6
7. WEAVE attempts:11 score:11
8. BLIMP attempts:5 score:5

# [squareword.org](squareword.org) 🧩 #1456 🥳 8 ⏱️ 0:02:05.897159

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S E N S E
    A R E N A
    H O V E R
    I D E A L
    B E R K S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1393 🥳 249 ⏱️ 0:05:09.826228

🤔 250 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 56 chat prompts
🤖 56 dolphin3:latest replies
🔥   1 🥵  15 😎  48 🥶 173 🧊  12

      $1 #250   ~1 contractor      100.00°C 🥳 1000‰
      $2 #149  ~30 engineer         50.31°C 🔥  995‰
      $3  #79  ~58 construction     47.06°C 🥵  989‰
      $4 #145  ~32 roofing          46.16°C 🥵  988‰
      $5  #88  ~52 plumbing         42.11°C 🥵  977‰
      $6 #144  ~33 landscaping      40.85°C 🥵  971‰
      $7 #128  ~38 drywall          39.60°C 🥵  963‰
      $8 #122  ~42 masonry          38.33°C 🥵  954‰
      $9 #233   ~5 maintenance      37.94°C 🥵  951‰
     $10 #175  ~19 flooring         37.60°C 🥵  946‰
     $11 #153  ~27 waterproofing    37.49°C 🥵  942‰
     $18 #171  ~21 project          34.32°C 😎  894‰
     $66  #65      paint            19.39°C 🥶
    $239 #242      selection        -0.14°C 🧊

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1426 🥳 274 ⏱️ 0:12:22.953623

🤔 275 attempts
📜 1 sessions
🫧 23 chat sessions
⁉️ 99 chat prompts
🤖 5 ministral-3:14b replies
🤖 2 llama3.3:latest replies
🤖 4 glm-4.7-flash:latest replies
🤖 14 falcon3:10b replies
🤖 73 dolphin3:latest replies
🥵   3 😎  14 🥶 214 🧊  43

      $1 #275   ~1 sou              100.00°C 🥳 1000‰
      $2 #259   ~5 obole             38.87°C 🥵  970‰
      $3 #246  ~11 pauvre            38.76°C 🥵  969‰
      $4 #272   ~3 denier            34.75°C 🥵  925‰
      $5 #247  ~10 aumône            32.08°C 😎  853‰
      $6 #256   ~7 largesse          30.69°C 😎  801‰
      $7 #269   ~4 mendiant          30.08°C 😎  774‰
      $8 #255   ~8 indigent          29.51°C 😎  740‰
      $9  #46  ~18 bonbon            29.48°C 😎  737‰
     $10 #254   ~9 gueux             28.91°C 😎  701‰
     $11 #257   ~6 miséreux          28.34°C 😎  649‰
     $12 #103  ~16 petit             28.14°C 😎  629‰
     $19 #155      tante             23.50°C 🥶
    $233 #189      impur             -0.26°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #77 🥳 score:26 ⏱️ 0:01:44.618264

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. WREAK attempts:6 score:6
2. WHICH attempts:5 score:5
3. CUTIE attempts:7 score:7
4. CRIER attempts:7 score:8
