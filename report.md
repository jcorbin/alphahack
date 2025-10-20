# 2025-10-21

- 🔗 spaceword.org 🧩 2025-10-20 🏁 score 2172 ranked 19.7% 75/381 ⏱️ 2:44:26.074485
- 🔗 alfagok.diginaut.net 🧩 #353 🥳 12 ⏱️ 0:00:34.827281
- 🔗 alphaguess.com 🧩 #819 🥳 18 ⏱️ 0:00:47.375056
- 🔗 squareword.org 🧩 #1359 🥳 7 ⏱️ 0:02:29.628627
- 🔗 dictionary.com hurdle 🧩 #1389 🥳 20 ⏱️ 0:04:09.253984
- 🔗 dontwordle.com 🧩 #1246 🥳 6 ⏱️ 0:01:48.018489
- 🔗 cemantle.certitudes.org 🧩 #1296 🥳 40 ⏱️ 0:01:15.445519
- 🔗 cemantix.certitudes.org 🧩 #1329 🥳 97 ⏱️ 0:04:09.401528

# Dev

## WIP

## TODO

- meta: alfagok lines not getting collected
  ```
  pick 4754d78e # alfagok.diginaut.net day #345
  ```

- dontword:
  - upsteam site seems to be glitchy wrt generating result copy on mobile
  - workaround by synthesizing?
  - workaround by storing complete-but-unverified anyhow?

- hurdle: report wasn't right out of #1373 -- was missing first few rounds

- square: finish questioning work

- reuse input injection mechanism from store
  - wherever the current input injection usage is
  - and also to allow more seamless meta log continue ...

- meta:
  - `day` command needs to be able to progress even without all solvers done
  - `day` pruning should be more agro
  - rework command model
    * current `log <solver> ...` and `run <solver>` should instead
    * unify into `<solver> log|run ...`
    * with the same stateful sub-prompting so that we can just say `<solver>`
      and then `log ...` and then `run` obviating the `log continue` command
      separate from just `run`
  - review should progress main branch too
  - better logic circa end of day early play, e.g. doing a CET timezone puzzle
    close late in the "prior" day local (EST) time; similarly, early play of
    next-day spaceword should work gracefully
  - support other intervals like weekly/monthly for spaceword

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


# spaceword.org 🧩 2025-10-20 🏁 score 2172 ranked 19.7% 75/381 ⏱️ 2:44:26.074485

📜 5 sessions
- tiles: 21/21
- score: 2172 bonus: +72
- rank: 75/381

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ V E E P _ _ _   
      _ _ _ _ _ X I _ _ _   
      _ _ _ _ K E N _ _ _   
      _ _ _ F I C O _ _ _   
      _ _ _ _ _ U N _ _ _   
      _ _ _ L I T E _ _ _   
      _ _ _ _ _ E S _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #353 🥳 12 ⏱️ 0:00:34.827281

🤔 12 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+199830 [199830] lijm       q0  ? after
    @+299737 [299737] schub      q1  ? after
    @+349512 [349512] vakantie   q2  ? after
    @+374255 [374255] vrij       q3  ? after
    @+377318 [377318] wandel     q6  ? after
    @+377621 [377621] wanproduct q9  ? after
    @+377650 [377650] want       q11 ? it
    @+377650 [377650] want       done. it
    @+377686 [377686] wapen      q10 ? before
    @+377924 [377924] war        q8  ? before
    @+378544 [378544] water      q7  ? before
    @+380467 [380467] weer       q5  ? before
    @+386796 [386796] wind       q4  ? before

# alphaguess.com 🧩 #819 🥳 18 ⏱️ 0:00:47.375056

🤔 18 attempts
📜 1 sessions

    @       [    0] aa          
    @+1     [    1] aah         
    @+2     [    2] aahed       
    @+3     [    3] aahing      
    @+2802  [ 2802] ag          q5  ? after
    @+3564  [ 3564] alarm       q7  ? after
    @+3950  [ 3950] alipeds     q8  ? after
    @+4044  [ 4044] all         q9  ? after
    @+4117  [ 4117] allergen    q12 ? after
    @+4154  [ 4154] alliances   q13 ? after
    @+4158  [ 4158] allies      q16 ? after
    @+4159  [ 4159] alligator   done. it
    @+4160  [ 4160] alligators  q17 ? before
    @+4161  [ 4161] alliterate  q15 ? before
    @+4173  [ 4173] alloantigen q14 ? before
    @+4191  [ 4191] allod       q11 ? before
    @+4335  [ 4335] alma        q6  ? before
    @+5881  [ 5881] angel       q4  ? before
    @+11769 [11769] back        q3  ? before
    @+23692 [23692] camp        q2  ? before
    @+47391 [47391] dis         q1  ? before
    @+98230 [98230] mach        q0  ? before

# squareword.org 🧩 #1359 🥳 7 ⏱️ 0:02:29.628627

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟩
    🟩 🟨 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S M E A R
    T E M P I
    O R C A S
    P I E C E
    S T E E R

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1389 🥳 20 ⏱️ 0:04:09.253984

📜 1 sessions
💰 score: 9600

    4/6
    SPEAR 🟨🟨🟨⬜⬜
    TOPES ⬜🟩🟨🟨🟨
    POISE 🟩🟩⬜🟩🟩
    POSSE 🟩🟩🟩🟩🟩
    5/6
    POSSE ⬜🟩🟨⬜⬜
    TOLAS 🟨🟩⬜⬜🟨
    SOUTH 🟩🟩⬜🟩⬜
    SOFTY 🟩🟩⬜🟩🟩
    SOOTY 🟩🟩🟩🟩🟩
    4/6
    SOOTY ⬜⬜⬜⬜⬜
    PRICE 🟩🟩🟩⬜🟩
    PRIME 🟩🟩🟩⬜🟩
    PRIZE 🟩🟩🟩🟩🟩
    6/6
    PRIZE ⬜⬜⬜⬜🟨
    DEATH ⬜🟨⬜🟨⬜
    BYTES ⬜⬜🟨🟩🟨
    ONSET ⬜⬜🟨🟩🟩
    SWEET 🟩⬜🟩🟩🟩
    SLEET 🟩🟩🟩🟩🟩
    Final 1/2
    STOLE 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1246 🥳 6 ⏱️ 0:01:48.018489

📜 1 sessions
💰 score: 5

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:WHIFF n n n n n remain:6776
    ⬜⬜⬜⬜⬜ tried:KEEVE n n n n n remain:2782
    ⬜⬜⬜⬜⬜ tried:DAGGA n n n n n remain:780
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:380
    ⬜⬜🟩⬜⬜ tried:CRUMB n n Y n n remain:11
    🟨⬜🟩⬜🟩 tried:STUNT m n Y n Y remain:1

    Undos used: 5

      1 words remaining
    x 5 unused letters
    = 5 total score

# cemantle.certitudes.org 🧩 #1296 🥳 40 ⏱️ 0:01:15.445519

🤔 41 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 9 chat prompts
🤖 9 gemma3:latest replies
🔥  2 🥵  2 😎  7 🥶 26 🧊  3

     $1 #41  ~1 lucky          100.00°C 🥳 1000‰
     $2 #30  ~6 fortunate       70.68°C 😱  999‰
     $3 #35  ~3 blessed         48.64°C 🔥  993‰
     $4 #19  ~9 fortuitous      42.08°C 🥵  985‰
     $5 #11 ~11 chance          38.57°C 🥵  973‰
     $6 #26  ~8 happenstance    29.75°C 😎  808‰
     $7 #33  ~4 auspicious      28.69°C 😎  743‰
     $8  #7 ~12 serendipity     26.35°C 😎  560‰
     $9 #32  ~5 advantageous    24.27°C 😎  315‰
    $10 #28  ~7 eventful        23.97°C 😎  260‰
    $11 #13 ~10 random          23.76°C 😎  228‰
    $12 #38  ~2 fortune         22.72°C 😎   32‰
    $13 #27     coincidental    20.50°C 🥶
    $39 #15     variance        -1.01°C 🧊

# cemantix.certitudes.org 🧩 #1329 🥳 97 ⏱️ 0:04:09.401528

🤔 98 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 23 chat prompts
🤖 23 gemma3:latest replies
😱  1 🥵  2 😎 18 🥶 61 🧊 15

     $1 #98  ~1 précaire      100.00°C 🥳 1000‰
     $2 #87 ~10 précarité      70.86°C 😱  999‰
     $3 #95  ~4 instable       37.41°C 🥵  951‰
     $4 #97  ~2 pauvreté       37.04°C 🥵  946‰
     $5 #96  ~3 insécurité     32.59°C 😎  899‰
     $6 #91  ~8 fragilité      30.86°C 😎  852‰
     $7  #5 ~22 pénible        30.74°C 😎  851‰
     $8 #12 ~21 difficile      30.65°C 😎  846‰
     $9 #42 ~18 difficulté     29.08°C 😎  794‰
    $10 #93  ~6 désœuvrement   27.60°C 😎  719‰
    $11 #94  ~5 instabilité    26.74°C 😎  663‰
    $12 #34 ~19 incessant      26.36°C 😎  631‰
    $23 #84     frustration    20.40°C 🥶
    $84 #46     prétentieux    -0.42°C 🧊
