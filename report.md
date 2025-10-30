# 2025-10-31

- 🔗 spaceword.org 🧩 2025-10-30 🏁 score 2168 ranked 33.5% 128/382 ⏱️ 1:28:41.559351
- 🔗 alfagok.diginaut.net 🧩 #363 🥳 13 ⏱️ 0:00:34.540241
- 🔗 alphaguess.com 🧩 #829 🥳 12 ⏱️ 0:00:29.307333
- 🔗 squareword.org 🧩 #1369 🥳 9 ⏱️ 0:02:14.081087
- 🔗 dictionary.com hurdle 🧩 #1399 🥳 16 ⏱️ 0:02:53.579672
- 🔗 dontwordle.com 🧩 #1256 🥳 6 ⏱️ 0:01:37.883431
- 🔗 cemantle.certitudes.org 🧩 #1306 🥳 129 ⏱️ 0:15:26.858343
- 🔗 cemantix.certitudes.org 🧩 #1339 🥳 100 ⏱️ 0:04:21.419307

# Dev

## WIP

ui: Shell / Handle revolution

## TODO

- meta: alfagok lines not getting collected
  ```
  pick 4754d78e # alfagok.diginaut.net day #345
  ```

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





# spaceword.org 🧩 2025-10-30 🏁 score 2168 ranked 33.5% 128/382 ⏱️ 1:28:41.559351

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 128/382

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ G U L L _ _ _ Z _   
      _ R _ O U T V I E _   
      _ E M O T E _ _ K _   
      _ E _ F E _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #363 🥳 13 ⏱️ 0:00:34.540241

🤔 13 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+99745  [ 99745] ex        q1  ? after
    @+111400 [111400] ge        q3  ? after
    @+120891 [120891] gepunte   q5  ? after
    @+121927 [121927] ges       q7  ? after
    @+123448 [123448] get       q8  ? after
    @+123996 [123996] getwijfel q10 ? after
    @+124022 [124022] geur      q12 ? it
    @+124022 [124022] geur      done. it
    @+124187 [124187] gevangen  q11 ? before
    @+124544 [124544] gevijlde  q9  ? before
    @+125639 [125639] gezeefd   q6  ? before
    @+130388 [130388] gracht    q4  ? before
    @+149448 [149448] huis      q2  ? before
    @+199827 [199827] lijm      q0  ? before

# alphaguess.com 🧩 #829 🥳 12 ⏱️ 0:00:29.307333

🤔 12 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+47387 [47387] dis       q1  ? after
    @+72807 [72807] gremolata q2  ? after
    @+85511 [85511] ins       q3  ? after
    @+91856 [91856] knot      q4  ? after
    @+93276 [93276] lar       q6  ? after
    @+93568 [93568] lati      q8  ? after
    @+93632 [93632] laud      q10 ? after
    @+93672 [93672] launch    q11 ? it
    @+93672 [93672] launch    done. it
    @+93722 [93722] lava      q9  ? before
    @+93904 [93904] lea       q7  ? before
    @+94953 [94953] lib       q5  ? before
    @+98226 [98226] mach      q0  ? before

# squareword.org 🧩 #1369 🥳 9 ⏱️ 0:02:14.081087

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟩
    🟨 🟨 🟩 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T A C K
    C O L O N
    A T O N E
    R A N G E
    F L E A S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1399 🥳 16 ⏱️ 0:02:53.579672

📜 1 sessions
💰 score: 10000

    4/6
    ARISE ⬜🟨⬜⬜🟩
    ROGUE 🟨⬜⬜🟨🟩
    LUCRE ⬜🟩🟨🟨🟩
    CURVE 🟩🟩🟩🟩🟩
    4/6
    CURVE ⬜🟨⬜⬜⬜
    STUPA 🟩🟨🟨⬜⬜
    SHOUT 🟩⬜🟩🟩🟩
    SNOUT 🟩🟩🟩🟩🟩
    3/6
    SNOUT ⬜🟨⬜⬜⬜
    ALIEN ⬜🟨🟩⬜🟨
    LYING 🟩🟩🟩🟩🟩
    4/6
    LYING ⬜⬜⬜🟨⬜
    ANTES ⬜🟩🟨🟩⬜
    UNWET 🟩🟩⬜🟩🟩
    UNMET 🟩🟩🟩🟩🟩
    Final 1/2
    RINSE 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1256 🥳 6 ⏱️ 0:01:37.883431

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:JINNI n n n n n remain:7302
    ⬜⬜⬜⬜⬜ tried:DEWED n n n n n remain:2909
    ⬜⬜⬜⬜⬜ tried:ABAKA n n n n n remain:932
    ⬜⬜⬜⬜⬜ tried:SHULS n n n n n remain:72
    🟩⬜🟨⬜⬜ tried:CRYPT Y n m n n remain:3
    🟩🟩🟩⬜🟩 tried:COMMY Y Y Y n Y remain:1

    Undos used: 4

      1 words remaining
    x 6 unused letters
    = 6 total score

# cemantle.certitudes.org 🧩 #1306 🥳 129 ⏱️ 0:15:26.858343

🤔 130 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 42 chat prompts
🤖 4 llama3.2:latest replies
🤖 38 gemma3:latest replies
🥵   4 😎  11 🥶 100 🧊  14

      $1 #130   ~1 restaurant     100.00°C 🥳 1000‰
      $2 #126   ~5 cuisine         56.57°C 🥵  980‰
      $3 #127   ~4 chef            55.71°C 🥵  978‰
      $4  #53  ~15 gourmet         46.16°C 🥵  940‰
      $5 #128   ~3 food            42.04°C 🥵  906‰
      $6 #111   ~8 gastronomic     40.37°C 😎  888‰
      $7  #64  ~12 culinary        39.40°C 😎  868‰
      $8  #89  ~10 delicious       35.41°C 😎  780‰
      $9  #56  ~14 flavorful       34.33°C 😎  745‰
     $10  #63  ~13 savory          31.27°C 😎  604‰
     $11 #100   ~9 delectable      28.78°C 😎  452‰
     $12 #129   ~2 recipe          28.26°C 😎  413‰
     $17 #109      appetizing      23.95°C 🥶
    $117  #20      dynamic         -0.22°C 🧊

# cemantix.certitudes.org 🧩 #1339 🥳 100 ⏱️ 0:04:21.419307

🤔 101 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 24 chat prompts
🤖 24 gemma3:latest replies
😱  1 🥵  3 😎  5 🥶 61 🧊 30

      $1 #101   ~1 héritier        100.00°C 🥳 1000‰
      $2  #90   ~8 héritage         65.38°C 😱  999‰
      $3  #92   ~7 descendance      47.23°C 🥵  986‰
      $4  #97   ~3 filiation        43.22°C 🥵  976‰
      $5  #95   ~5 dynastie         40.01°C 🥵  961‰
      $6 #100   ~2 génération       33.22°C 😎  861‰
      $7  #96   ~4 ascendant        33.10°C 😎  856‰
      $8  #93   ~6 ascendance       30.37°C 😎  749‰
      $9  #81  ~10 passé            29.83°C 😎  727‰
     $10  #83   ~9 ancien           28.15°C 😎  644‰
     $11  #54      insaisissable    22.02°C 🥶
     $12  #99      généalogie       20.62°C 🥶
     $13  #91      antiquité        16.23°C 🥶
     $72   #1      chanson          -0.11°C 🧊
