# 2025-10-17

- 🔗 spaceword.org 🧩 2025-10-16 🏁 score 2173 ranked 5.5% 21/381 ⏱️ 0:19:33.677450
- 🔗 alfagok.diginaut.net 🧩 #349 🥳 15 ⏱️ 0:00:43.924261
- 🔗 alphaguess.com 🧩 #815 🥳 18 ⏱️ 0:00:50.169258
- 🔗 squareword.org 🧩 #1355 🥳 7 ⏱️ 0:02:18.276379
- 🔗 dictionary.com hurdle 🧩 #1385 🥳 18 ⏱️ 0:03:38.171102
- 🔗 dontwordle.com 🧩 #1242 🥳 6 ⏱️ 0:01:41.056870
- 🔗 cemantle.certitudes.org 🧩 #1292 🥳 198 ⏱️ 0:01:14.112112
- 🔗 cemantix.certitudes.org 🧩 #1325 🥳 217 ⏱️ 0:02:09.091742

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




# spaceword.org 🧩 2025-10-16 🏁 score 2173 ranked 5.5% 21/381 ⏱️ 0:19:33.677450

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 21/381

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ V _ Z O O T O M Y   
      _ A _ _ I _ W _ O E   
      _ T H U L I A S _ T   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #349 🥳 15 ⏱️ 0:00:43.924261

🤔 15 attempts
📜 1 sessions

    @        [     0] &-teken       
    @+1      [     1] &-tekens      
    @+2      [     2] -cijferig     
    @+3      [     3] -e-mail       
    @+99746  [ 99746] ex            q1  ? after
    @+149449 [149449] huis          q2  ? after
    @+174559 [174559] kind          q3  ? after
    @+187195 [187195] krontjongs    q4  ? after
    @+193496 [193496] lavendel      q5  ? after
    @+194921 [194921] lees          q7  ? after
    @+195095 [195095] leesstrategie q10 ? after
    @+195130 [195130] leesvermaak   q12 ? after
    @+195147 [195147] leeszaal      q13 ? after
    @+195151 [195151] leeuw         q14 ? it
    @+195151 [195151] leeuw         done. it
    @+195164 [195164] leeuwen       q11 ? before
    @+195269 [195269] leg           q9  ? before
    @+195638 [195638] leid          q8  ? before
    @+196512 [196512] les           q6  ? before
    @+199831 [199831] lijm          q0  ? before

# alphaguess.com 🧩 #815 🥳 18 ⏱️ 0:00:50.169258

🤔 18 attempts
📜 1 sessions

    @        [     0] aa        
    @+1      [     1] aah       
    @+2      [     2] aahed     
    @+3      [     3] aahing    
    @+98231  [ 98231] mach      q0  ? after
    @+147336 [147336] rho       q1  ? after
    @+171936 [171936] tag       q2  ? after
    @+182023 [182023] un        q3  ? after
    @+189286 [189286] vicar     q4  ? after
    @+192890 [192890] whir      q5  ? after
    @+194715 [194715] worship   q6  ? after
    @+194823 [194823] wrath     q10 ? after
    @+194841 [194841] wreath    q12 ? after
    @+194851 [194851] wreck     q13 ? after
    @+194861 [194861] wren      q14 ? after
    @+194862 [194862] wrench    done. it
    @+194863 [194863] wrenched  q17 ? before
    @+194864 [194864] wrencher  q16 ? before
    @+194867 [194867] wrenching q15 ? before
    @+194872 [194872] wrest     q11 ? before
    @+194942 [194942] writ      q9  ? before
    @+195172 [195172] xylems    q8  ? before
    @+195629 [195629] yo        q7  ? before

# squareword.org 🧩 #1355 🥳 7 ⏱️ 0:02:18.276379

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    D I S C S
    E N N U I
    A P A R T
    N U R S E
    S T E E D

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1385 🥳 18 ⏱️ 0:03:38.171102

📜 1 sessions
💰 score: 9800

    5/6
    TEARS ⬜🟨⬜⬜🟨
    NOISE ⬜⬜⬜🟨🟨
    FUSED ⬜⬜🟨🟨⬜
    SKELP 🟩🟨🟩⬜🟨
    SPECK 🟩🟩🟩🟩🟩
    4/6
    SPECK ⬜⬜⬜🟨⬜
    ICHOR 🟨🟩⬜⬜⬜
    ACIDY 🟩🟩🟩⬜⬜
    ACING 🟩🟩🟩🟩🟩
    3/6
    ACING 🟨⬜⬜🟨⬜
    RANKS 🟨🟩🟩⬜🟨
    SANER 🟩🟩🟩🟩🟩
    4/6
    SANER ⬜⬜⬜⬜⬜
    YOGIC ⬜🟩⬜⬜🟨
    BOTCH ⬜🟩🟨🟩🟩
    TOUCH 🟩🟩🟩🟩🟩
    Final 2/2
    FRIAR ⬜🟩🟩🟩🟩
    BRIAR 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1242 🥳 6 ⏱️ 0:01:41.056870

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:CALLA n n n n n remain:4913
    ⬜⬜⬜⬜⬜ tried:WOOZY n n n n n remain:2044
    ⬜⬜⬜⬜⬜ tried:SUMPS n n n n n remain:380
    ⬜⬜🟨⬜⬜ tried:GRIFF n n m n n remain:60
    ⬜⬜⬜🟩⬜ tried:KININ n n n Y n remain:4
    ⬜🟩⬜🟩🟩 tried:EEJIT n Y n Y Y remain:1

    Undos used: 4

      1 words remaining
    x 6 unused letters
    = 6 total score

# cemantle.certitudes.org 🧩 #1292 🥳 198 ⏱️ 0:01:14.112112

🤔 199 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 48 chat prompts
🤖 48 gemma3:latest replies
🔥   2 🥵  11 😎  32 🥶 147 🧊   6

      $1 #199   ~1 workout          100.00°C 🥳 1000‰
      $2 #107  ~32 fitness           53.21°C 🔥  997‰
      $3 #151  ~12 aerobic           52.87°C 🔥  996‰
      $4 #131  ~19 training          46.32°C 🥵  988‰
      $5 #114  ~31 exercise          44.88°C 🥵  986‰
      $6 #153  ~10 hydration         38.01°C 🥵  967‰
      $7  #85  ~38 stamina           37.55°C 🥵  963‰
      $8  #92  ~36 endurance         35.91°C 🥵  953‰
      $9  #69  ~41 athletic          34.63°C 🥵  939‰
     $10 #127  ~22 routine           34.46°C 🥵  938‰
     $11 #152  ~11 anaerobic         32.50°C 🥵  917‰
     $15 #145  ~14 carbohydrate      30.96°C 😎  890‰
     $47  #59      breeze            20.28°C 🥶
    $194  #19      current           -0.37°C 🧊

# cemantix.certitudes.org 🧩 #1325 🥳 217 ⏱️ 0:02:09.091742

🤔 218 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 56 chat prompts
🤖 56 gemma3:latest replies
🥵   4 😎  16 🥶 166 🧊  31

      $1 #218   ~1 assaut           100.00°C 🥳 1000‰
      $2 #202   ~5 escarmouche       47.63°C 🥵  979‰
      $3 #206   ~4 combat            45.93°C 🥵  971‰
      $4 #149  ~20 bastion           41.88°C 🥵  944‰
      $5 #194   ~8 forteresse        40.58°C 🥵  927‰
      $6 #201   ~6 tenaille          35.97°C 😎  840‰
      $7 #150  ~19 citadelle         35.83°C 😎  838‰
      $8 #172  ~16 casemate          35.11°C 😎  813‰
      $9 #171  ~17 rempart           34.35°C 😎  785‰
     $10 #178  ~14 trouée            33.75°C 😎  765‰
     $11 #146  ~21 muraille          33.51°C 😎  753‰
     $12 #192   ~9 patrouille        33.22°C 😎  743‰
     $22 #147      bastille          25.59°C 🥶
    $188 #154      foyer             -0.05°C 🧊
