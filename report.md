# 2025-11-10

- 🔗 spaceword.org 🧩 2025-11-09 🏁 score 2168 ranked 45.5% 87/191 ⏱️ 0:24:18.686462
- 🔗 alfagok.diginaut.net 🧩 #373 🥳 9 ⏱️ 0:00:31.484077
- 🔗 alphaguess.com 🧩 #839 🥳 15 ⏱️ 0:00:43.480158
- 🔗 squareword.org 🧩 #1379 🥳 8 ⏱️ 0:03:12.067921
- 🔗 dictionary.com hurdle 🧩 #1409 🥳 20 ⏱️ 0:03:47.071575
- 🔗 dontwordle.com 🧩 #1266 🥳 6 ⏱️ 0:02:06.808572
- 🔗 cemantle.certitudes.org 🧩 #1316 🥳 284 ⏱️ 0:04:18.782796
- 🔗 cemantix.certitudes.org 🧩 #1349 🥳 47 ⏱️ 0:00:18.977770

# Dev

## WIP

- ui:
  - Handle -- stabilizing core over Listing
  - Shell -- minimizing over Handle

- meta: rework command model over Shell

## TODO

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

# spaceword.org 🧩 2025-11-04 🏁 score 2173 ranked 6.5% 24/367 ⏱️ 0:20:32.980979

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 24/367

      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ H I P _ _ _
      _ _ _ _ _ _ O _ _ _
      _ _ _ _ S O D _ _ _
      _ _ _ _ E _ U _ _ _
      _ _ _ _ I _ N _ _ _
      _ _ _ _ Z E K _ _ _
      _ _ _ _ U M S _ _ _
      _ _ _ _ R _ _ _ _ _
      _ _ _ _ E V E _ _ _






# spaceword.org 🧩 2025-11-09 🏁 score 2168 ranked 45.5% 87/191 ⏱️ 0:24:18.686462

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 87/191

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ Q _ B E C K O N _   
      _ I _ U _ O _ N A _   
      _ S O N A R _ E W _   
      _ _ _ A _ F _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #373 🥳 9 ⏱️ 0:00:31.484077

🤔 9 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199766 [199766] lijn      q0 ? after
    @+211612 [211612] me        q5 ? after
    @+212874 [212874] meer      q8 ? it
    @+212874 [212874] meer      done. it
    @+214576 [214576] melodie   q7 ? before
    @+217549 [217549] mijmer    q6 ? before
    @+223491 [223491] mol       q3 ? before
    @+247602 [247602] op        q2 ? before
    @+299649 [299649] schudde   q1 ? before

# alphaguess.com 🧩 #839 🥳 15 ⏱️ 0:00:43.480158

🤔 15 attempts
📜 1 sessions

    @        [     0] aa         
    @+1      [     1] aah        
    @+2      [     2] aahed      
    @+3      [     3] aahing     
    @+98226  [ 98226] mach       q0  ? after
    @+147331 [147331] rho        q1  ? after
    @+171931 [171931] tag        q2  ? after
    @+176968 [176968] tom        q4  ? after
    @+179492 [179492] trifurcate q5  ? after
    @+180743 [180743] tune       q6  ? after
    @+181380 [181380] two        q7  ? after
    @+181517 [181517] typo       q9  ? after
    @+181596 [181596] tzar       q10 ? after
    @+181619 [181619] tziganes   q12 ? after
    @+181631 [181631] ubique     q13 ? after
    @+181635 [181635] ubiquitous q14 ? it
    @+181635 [181635] ubiquitous done. it
    @+181642 [181642] udo        q11 ? before
    @+181694 [181694] ulcer      q8  ? before
    @+182018 [182018] un         q3  ? before

# squareword.org 🧩 #1379 🥳 8 ⏱️ 0:03:12.067921

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C H A S M
    R E C T A
    E N T E R
    S C O R E
    T E R N S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1409 🥳 20 ⏱️ 0:03:47.071575

📜 1 sessions
💰 score: 9600

    6/6
    RALES ⬜⬜⬜🟨🟨
    STONE 🟨🟨⬜⬜🟨
    FEIST ⬜🟩⬜🟨🟨
    ZESTY ⬜🟩🟩🟩🟩
    PESTY ⬜🟩🟩🟩🟩
    TESTY 🟩🟩🟩🟩🟩
    4/6
    TESTY 🟨⬜🟨⬜⬜
    STAIR 🟩🟨⬜⬜🟨
    SHORT 🟩⬜⬜🟩🟩
    SPURT 🟩🟩🟩🟩🟩
    4/6
    SPURT ⬜⬜⬜🟨⬜
    AREIC ⬜🟨🟨⬜⬜
    OLDER 🟨⬜🟨🟨🟨
    HORDE 🟩🟩🟩🟩🟩
    4/6
    HORDE ⬜🟨🟨⬜⬜
    PROST ⬜🟨🟨⬜⬜
    VIGOR ⬜🟩⬜🟨🟨
    MICRO 🟩🟩🟩🟩🟩
    Final 2/2
    SLUNG 🟩🟩🟩🟩⬜
    SLUNK 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1266 🥳 6 ⏱️ 0:02:06.808572

📜 1 sessions
💰 score: 9

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:HOLLO n n n n n remain:5815
    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:3156
    ⬜⬜⬜⬜⬜ tried:DUFUS n n n n n remain:646
    ⬜🟩⬜⬜⬜ tried:BENNE n Y n n n remain:42
    ⬜🟩🟨⬜🟨 tried:GEMMA n Y m n m remain:2
    ⬜🟩🟩⬜🟨 tried:REARM n Y Y n m remain:1

    Undos used: 4

      1 words remaining
    x 9 unused letters
    = 9 total score

# cemantle.certitudes.org 🧩 #1316 🥳 284 ⏱️ 0:04:18.782796

🤔 285 attempts
📜 1 sessions
🫧 20 chat sessions
⁉️ 121 chat prompts
🤖 118 gemma3:latest replies
🤖 2 llama3.2:latest replies
🔥   4 🥵   6 😎  29 🥶 236 🧊   9

      $1 #285   ~1 flagstone        100.00°C 🥳 1000‰
      $2  #91  ~28 granite           61.93°C 🔥  998‰
      $3 #123  ~25 limestone         56.73°C 🔥  996‰
      $4 #164  ~19 marble            56.49°C 🔥  995‰
      $5  #29  ~37 stone             53.16°C 🔥  993‰
      $6 #234   ~8 brick             51.25°C 🥵  988‰
      $7 #220   ~9 masonry           46.16°C 🥵  956‰
      $8 #243   ~6 countertop        44.58°C 🥵  940‰
      $9 #239   ~7 slab              43.82°C 🥵  925‰
     $10  #76  ~30 quartzite         42.96°C 🥵  910‰
     $11  #53  ~34 gravel            42.89°C 🥵  908‰
     $12 #281   ~2 decorative        42.40°C 😎  898‰
     $41  #84      ridge             30.45°C 🥶
    $277 #114      peak              -0.28°C 🧊

# cemantix.certitudes.org 🧩 #1349 🥳 47 ⏱️ 0:00:18.977770

🤔 48 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 10 chat prompts
🤖 10 gemma3:latest replies
🥵  1 😎  6 🥶 34 🧊  6

     $1 #48  ~1 angle         100.00°C 🥳 1000‰
     $2 #47  ~2 prisme         42.37°C 🥵  973‰
     $3 #37  ~6 diffraction    31.47°C 😎  714‰
     $4 #16  ~7 luminosité     29.74°C 😎  616‰
     $5 #40  ~4 intensité      29.15°C 😎  571‰
     $6  #3  ~8 lumière        25.13°C 😎  163‰
     $7 #43  ~3 lentille       24.89°C 😎  113‰
     $8 #38  ~5 dioptrique     24.55°C 😎   57‰
     $9 #31     gradient       22.69°C 🥶
    $10 #33     dioptrie       22.50°C 🥶
    $11 #34     chromatisme    22.04°C 🥶
    $12 #13     rayon          21.47°C 🥶
    $13 #41     interférence   21.09°C 🥶
    $43 #32     brûler         -3.29°C 🧊
