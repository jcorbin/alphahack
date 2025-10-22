# 2025-10-23

- 🔗 spaceword.org 🧩 2025-10-22 🏁 score 2173 ranked 5.9% 22/375 ⏱️ 4:32:46.369809
- 🔗 alfagok.diginaut.net 🧩 2025-10-23 😦 19 ⏱️ 0:00:53.484841
- 🔗 alphaguess.com 🧩 #821 🥳 16 ⏱️ 0:00:37.115474
- 🔗 squareword.org 🧩 #1361 🥳 7 ⏱️ 0:02:20.122203
- 🔗 dictionary.com hurdle 🧩 #1391 😦 6 ⏱️ 0:01:35.723810
- 🔗 dontwordle.com 🧩 #1248 🥳 6 ⏱️ 0:01:27.705651
- 🔗 cemantle.certitudes.org 🧩 #1298 🥳 318 ⏱️ 0:26:12.054728
- 🔗 cemantix.certitudes.org 🧩 #1331 🥳 330 ⏱️ 0:15:01.491017

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




# spaceword.org 🧩 2025-10-22 🏁 score 2173 ranked 5.9% 22/375 ⏱️ 4:32:46.369809

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 22/375

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ Q I _ O W _ _ U P   
      _ I S O H E L _ T E   
      _ _ _ M O T I V E S   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 2025-10-23 😦 19 ⏱️ 0:00:53.484841

🤔 19 attempts
📜 2 sessions

    @        [     0] &-teken          
    @+1      [     1] &-tekens         
    @+2      [     2] -cijferig        
    @+3      [     3] -e-mail          
    @+24910  [ 24910] bad              q3  ? after
    @+27603  [ 27603] basis            q6  ? after
    @+28962  [ 28962] bed              q7  ? after
    @+29200  [ 29200] bedevaart        q9  ? after
    @+29323  [ 29323] bedil            q10 ? after
    @+29362  [ 29362] bedlamp          q12 ? after
    @+29370  [ 29370] bedoe            q13 ? after
    @+29386  [ 29386] bedoeïen         q14 ? after
    @+29388  [ 29388] bedoeïenentent   q17 ? after
    @+29389  [ 29389] bedoeïenententen q18 ? after
    @+29389  [ 29389] bedoeïenententen <<< SEARCH
    @+29390  [ 29390] bedolah          q16 ? before
    @+29390  [ 29390] bedolah          >>> SEARCH
    @+29393  [ 29393] bedompt          q15 ? before
    @+29399  [ 29399] bedonder         q11 ? before
    @+29474  [ 29474] bedrijf          q8  ? before
    @+31127  [ 31127] begeleid         q5  ? before
    @+37364  [ 37364] bescherm         q4  ? before
    @+49847  [ 49847] boks             q2  ? before
    @+99745  [ 99745] ex               q1  ? before
    @+199830 [199830] lijm             q0  ? before

# alphaguess.com 🧩 #821 🥳 16 ⏱️ 0:00:37.115474

🤔 16 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+47391 [47391] dis        q1  ? after
    @+72811 [72811] gremolata  q2  ? after
    @+85515 [85515] ins        q3  ? after
    @+85593 [85593] inseminate q10 ? after
    @+85631 [85631] inset      q11 ? after
    @+85638 [85638] insheath   q13 ? after
    @+85645 [85645] inshrine   q14 ? after
    @+85649 [85649] inside     q15 ? it
    @+85649 [85649] inside     done. it
    @+85653 [85653] insidious  q12 ? before
    @+85676 [85676] insinuate  q9  ? before
    @+85841 [85841] instant    q8  ? before
    @+86175 [86175] inter      q7  ? before
    @+87088 [87088] intima     q6  ? before
    @+88675 [88675] jacks      q5  ? before
    @+91860 [91860] knot       q4  ? before
    @+98230 [98230] mach       q0  ? before

# squareword.org 🧩 #1361 🥳 7 ⏱️ 0:02:20.122203

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    T R O L L
    R A D I O
    A D D E D
    S I E G E
    H I R E S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1391 😦 6 ⏱️ 0:01:35.723810

📜 1 sessions
💰 score: 60

    6/6
    PARSE ⬜🟨⬜🟨⬜
    SLANT 🟩⬜🟩⬜🟨
    STACK 🟩🟩🟩⬜⬜
    STAGY 🟩🟩🟩⬜⬜
    STAID 🟩🟩🟩⬜⬜
    STABS 🟩🟩🟩⬜⬜
    FAIL: STAFF

# dontwordle.com 🧩 #1248 🥳 6 ⏱️ 0:01:27.705651

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:FEMME n n n n n remain:5567
    ⬜⬜⬜⬜⬜ tried:BABKA n n n n n remain:1983
    ⬜⬜⬜⬜⬜ tried:HOOCH n n n n n remain:545
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:137
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:46
    ⬜🟨🟨⬜⬜ tried:GUSTS n m m n n remain:2

    Undos used: 3

      2 words remaining
    x 7 unused letters
    = 14 total score

# cemantle.certitudes.org 🧩 #1298 🥳 318 ⏱️ 0:26:12.054728

🤔 319 attempts
📜 1 sessions
🫧 13 chat sessions
⁉️ 75 chat prompts
🤖 17 llama3.2:latest replies
🤖 58 gemma3:latest replies
🔥   1 🥵   4 😎  40 🥶 262 🧊  11

      $1 #319   ~1 valve            100.00°C 🥳 1000‰
      $2 #301   ~5 gasket            62.82°C 🔥  998‰
      $3 #282  ~11 faucet            53.74°C 🥵  980‰
      $4 #308   ~3 pipe              50.88°C 🥵  966‰
      $5 #133  ~28 hydrostatic       48.28°C 🥵  950‰
      $6 #136  ~27 membrane          46.22°C 🥵  924‰
      $7  #77  ~40 leak              44.99°C 😎  895‰
      $8 #247  ~15 sealant           44.17°C 😎  876‰
      $9  #36  ~44 rupture           43.58°C 😎  863‰
     $10 #297   ~7 aerator           42.92°C 😎  851‰
     $11  #32  ~45 fluid             42.19°C 😎  829‰
     $12  #85  ~38 cavity            41.27°C 😎  800‰
     $47 #272      permeation        31.00°C 🥶
    $309 #180      resilient         -0.01°C 🧊

# cemantix.certitudes.org 🧩 #1331 🥳 330 ⏱️ 0:15:01.491017

🤔 331 attempts
📜 1 sessions
🫧 14 chat sessions
⁉️ 92 chat prompts
🤖 92 gemma3:latest replies
🔥   1 🥵  11 😎  36 🥶 171 🧊 111

      $1 #331   ~1 visiteur         100.00°C 🥳 1000‰
      $2 #329   ~2 visite            49.36°C 🔥  997‰
      $3  #25  ~42 découvrir         39.15°C 🥵  989‰
      $4  #88  ~33 curiosité         30.99°C 🥵  970‰
      $5 #180  ~18 pèlerin           29.68°C 🥵  964‰
      $6 #106  ~32 voyageur          29.24°C 🥵  959‰
      $7 #112  ~29 nouveauté         28.60°C 🥵  949‰
      $8  #13  ~46 promenade         28.50°C 🥵  947‰
      $9 #150  ~23 navigation        28.37°C 🥵  944‰
     $10 #318   ~6 admirer           27.72°C 🥵  932‰
     $11   #4  ~49 flâner            27.24°C 🥵  926‰
     $14  #11  ~48 balade            25.38°C 😎  890‰
     $50 #217      illumination      14.40°C 🥶
    $221 #305      vision            -0.04°C 🧊
