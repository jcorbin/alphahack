# 2025-10-12

- 🔗 spaceword.org 🧩 2025-10-11 🏁 score 2173 ranked 5.2% 18/348 ⏱️ 2:19:06.328371
- 🔗 alfagok.diginaut.net 🧩 #344 🥳 22 ⏱️ 0:03:37.207097
- 🔗 alphaguess.com 🧩 #810 🥳 16 ⏱️ 0:02:04.616424
- 🔗 squareword.org 🧩 #1350 🥳 7 ⏱️ 0:21:08.821441
- 🔗 dictionary.com hurdle 🧩 #1380 😦 20 ⏱️ 0:20:08.075052
- 🔗 cemantix.certitudes.org 🧩 #1320 🥳 586 ⏱️ 0:08:29.716773
- 🔗 cemantle.certitudes.org 🧩 #1287 🥳 322 ⏱️ 0:05:16.620334

# Dev

## WIP

- meta: review
  - works up to rc branch progression
  - git show bug should be fixed now:
  ```
  fatal: ambiguous argument '95715cb6 ': unknown revision or path not in the working tree.
  Use '--' to separate paths from revisions, like this:
  'git <command> [<revision>...] -- [<file>...]'
  ```

- StoredLog: added one-shot canned input from CLI args
  `python whatever.py some/log/maybe -- cmd1 -- cmd2 ...`
- StoredLog: fixed elapsed time reporting

## TODO

- hurdle: report wasn't right out of #1373 -- was missing first few rounds

- square: finish questioning work

- reuse input injection mechanism from store
  - wherever the current input injection usage is
  - and also to allow more seamless meta log continue ...

- meta:
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




# spaceword.org 🧩 2025-10-10 🏁 score 2173 ranked 7.0% 26/374 ⏱️ 1:26:46.308702

📜 6 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 26/374

      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ Z A S _ _ _
      _ _ _ _ _ C _ _ _ _
      _ _ _ _ J U N _ _ _
      _ _ _ _ _ L A _ _ _
      _ _ _ _ _ E N _ _ _
      _ _ _ _ O I K _ _ _
      _ _ _ _ _ _ E _ _ _
      _ _ _ _ A P E _ _ _
      _ _ _ _ G E N _ _ _


# alfagok.diginaut.net 🧩 #343 🥳 15 ⏱️ 0:02:46.134979

🤔 15 attempts
📜 1 sessions

    @        [     0] &-teken
    @+1      [     1] &-tekens
    @+2      [     2] -cijferig
    @+3      [     3] -e-mail
    @+99749  [ 99749] ex            q1  ? after
    @+149452 [149452] huis          q2  ? after
    @+174562 [174562] kind          q3  ? after
    @+187198 [187198] krontjongs    q4  ? after
    @+193499 [193499] lavendel      q5  ? after
    @+194924 [194924] lees          q7  ? after
    @+195098 [195098] leesstrategie q10 ? after
    @+195133 [195133] leesvermaak   q12 ? after
    @+195150 [195150] leeszaal      q13 ? after
    @+195154 [195154] leeuw         q14 ? it
    @+195154 [195154] leeuw         done. it
    @+195167 [195167] leeuwen       q11 ? before
    @+195272 [195272] leg           q9  ? before
    @+195641 [195641] leid          q8  ? before
    @+196515 [196515] les           q6  ? before
    @+199834 [199834] lijm          q0  ? before

# alphaguess.com 🧩 #809 🥳 11 ⏱️ 0:02:22.076959

🤔 11 attempts
📜 1 sessions

    @       [    0] aa
    @+1     [    1] aah
    @+2     [    2] aahed
    @+3     [    3] aahing
    @+23693 [23693] camp       q2  ? after
    @+26646 [26646] cep        q5  ? after
    @+28124 [28124] chick      q6  ? after
    @+28213 [28213] child      q10 ? it
    @+28213 [28213] child      done. it
    @+28303 [28303] chimb      q9  ? before
    @+28492 [28492] chirp      q8  ? before
    @+28869 [28869] choragic   q7  ? before
    @+29614 [29614] circuit    q4  ? before
    @+35536 [35536] convention q3  ? before
    @+47392 [47392] dis        q1  ? before
    @+98231 [98231] mach       q0  ? before

# squareword.org 🧩 #1349 🥳 10 ⏱️ 0:08:03.254421

📜 3 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟩 🟨
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    W A D E D
    A L I V E
    T O N I C
    C H E C K
    H A R T S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1379 🥳 22 ⏱️ 0:11:10.804963

📜 2 sessions
💰 score: 9400

    5/6
    LARES ⬜⬜⬜⬜⬜
    PINOT ⬜🟨🟨🟩⬜
    INBOX 🟨🟩⬜🟩⬜
    ONION ⬜🟩🟩🟩🟩
    UNION 🟩🟩🟩🟩🟩
    4/6
    UNION 🟨⬜⬜⬜⬜
    ABUSE ⬜⬜🟨🟨⬜
    MURKS 🟩🟩⬜🟩🟨
    MUSKY 🟩🟩🟩🟩🟩
    5/6
    MUSKY ⬜⬜⬜⬜⬜
    ALTER ⬜⬜⬜🟩🟩
    CODER ⬜⬜⬜🟩🟩
    INFER 🟩🟩⬜🟩🟩
    INNER 🟩🟩🟩🟩🟩
    6/6
    INNER ⬜⬜⬜⬜⬜
    OPALS ⬜⬜⬜⬜🟨
    TUSHY 🟨🟩🟩⬜🟩
    DUSTY ⬜🟩🟩🟩🟩
    MUSTY ⬜🟩🟩🟩🟩
    GUSTY 🟩🟩🟩🟩🟩
    Final 2/2
    BEARD 🟩🟨🟩🟩⬜
    BLARE 🟩🟩🟩🟩🟩

# cemantix.certitudes.org 🧩 #1319 🥳 336 ⏱️ 0:02:58.963547

🤔 337 attempts
📜 3 sessions
🫧 14 chat sessions
⁉️ 90 chat prompts
🤖 90 gemma3:latest replies
😱   1 🔥   4 🥵  18 😎  58 🥶 228 🧊  27

      $1 #337   ~1 conducteur        100.00°C 🥳 1000‰
      $2 #218  ~46 véhicule           56.21°C 😱  999‰
      $3 #335   ~2 chauffeur          50.26°C 🔥  998‰
      $4 #175  ~59 conduite           47.69°C 🔥  996‰
      $5 #328   ~3 volant             45.86°C 🔥  995‰
      $6 #127  ~66 accident           44.60°C 🔥  993‰
      $7 #206  ~54 freinage           41.66°C 🥵  989‰
      $8 #239  ~32 voiture            41.29°C 🥵  988‰
      $9 #325   ~4 passager           39.29°C 🥵  984‰
     $10 #202  ~56 signalisation      38.10°C 🥵  978‰
     $11 #272  ~25 limiteur           36.95°C 🥵  961‰
     $25 #233  ~37 remorquage         30.78°C 😎  893‰
     $83 #198      manoeuvre          19.87°C 🥶
    $311  #63      défense            -0.14°C 🧊

# cemantle.certitudes.org 🧩 #1286 🥳 399 ⏱️ 0:03:40.229938

🤔 400 attempts
📜 1 sessions
🫧 22 chat sessions
⁉️ 146 chat prompts
🤖 146 gemma3:latest replies
🔥   2 🥵  15 😎  43 🥶 318 🧊  21

      $1 #400   ~1 homeland            100.00°C 🥳 1000‰
      $2 #360  ~24 exile                46.58°C 🔥  997‰
      $3 #353  ~27 diaspora             41.05°C 🔥  991‰
      $4 #364  ~22 asylum               37.43°C 🥵  986‰
      $5 #363  ~23 refugee              36.16°C 🥵  979‰
      $6 #375  ~13 ancestry             35.75°C 🥵  978‰
      $7 #383  ~10 sovereignty          34.91°C 🥵  970‰
      $8 #374  ~14 stateless            34.68°C 🥵  968‰
      $9 #373  ~15 roots                34.66°C 🥵  967‰
     $10 #376  ~12 citizenship          33.70°C 🥵  963‰
     $11 #136  ~59 oppressed            33.60°C 🥵  961‰
     $19 #198  ~48 repression           30.16°C 😎  889‰
     $62  #74      sorrow               21.07°C 🥶
    $380 #143      chained              -0.08°C 🧊

# spaceword.org 🧩 2025-10-11 🏁 score 2173 ranked 5.2% 18/348 ⏱️ 2:19:06.328371

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 18/348

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ K _ S E I D E L   
      _ W I P E _ _ U N I   
      _ _ F I X A T E _ B   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #344 🥳 22 ⏱️ 0:03:37.207097

🤔 22 attempts
📜 2 sessions

    @        [     0] &-teken       
    @+1      [     1] &-tekens      
    @+2      [     2] -cijferig     
    @+3      [     3] -e-mail       
    @+49847  [ 49847] boks          q2  ? after
    @+74758  [ 74758] dc            q3  ? after
    @+87219  [ 87219] draag         q4  ? after
    @+93447  [ 93447] eet           q5  ? after
    @+96581  [ 96581] energiek      q6  ? after
    @+97547  [ 97547] er            q7  ? after
    @+98648  [ 98648] etablissement q8  ? after
    @+99115  [ 99115] euro          q10 ? after
    @+99304  [ 99304] eva           q12 ? after
    @+99472  [ 99472] even          q13 ? after
    @+99480  [ 99480] evenaren      q17 ? after
    @+99485  [ 99485] evenbeelden   q18 ? after
    @+99487  [ 99487] eveneens      q21 ? it
    @+99487  [ 99487] eveneens      done. it
    @+99488  [ 99488] evenement     q19 ? before
    @+99489  [ 99489] evenementen   q16 ? before
    @+99538  [ 99538] evennaasten   q15 ? before
    @+99605  [ 99605] evenzo        q14 ? before
    @+99746  [ 99746] ex            q1  ? before
    @+199831 [199831] lijm          q0  ? before

# alphaguess.com 🧩 #810 🥳 16 ⏱️ 0:02:04.616424

🤔 16 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+47392 [47392] dis       q1  ? after
    @+49439 [49439] do        q6  ? after
    @+49607 [49607] dog       q10 ? after
    @+49731 [49731] dogsled   q11 ? after
    @+49792 [49792] dollar    q12 ? after
    @+49821 [49821] dolma     q13 ? after
    @+49838 [49838] dolor     q14 ? after
    @+49847 [49847] dolphin   q15 ? it
    @+49847 [49847] dolphin   done. it
    @+49860 [49860] dom       q9  ? before
    @+50416 [50416] dove      q8  ? before
    @+51413 [51413] drunk     q7  ? before
    @+53408 [53408] el        q5  ? before
    @+60095 [60095] face      q3  ? bb
    @+60095 [60095] face      q4  ? before
    @+72812 [72812] gremolata q2  ? before
    @+98231 [98231] mach      q0  ? before

# squareword.org 🧩 #1350 🥳 7 ⏱️ 0:21:08.821441

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟩 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    L A S S O
    A G A I N
    B I K E S
    O L I V E
    R E S E T

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1380 😦 20 ⏱️ 0:20:08.075052

📜 1 sessions
💰 score: 4660

    5/6
    SMEAR ⬜⬜🟨⬜⬜
    TONED ⬜🟨⬜🟨⬜
    GECKO ⬜🟩⬜⬜🟩
    HELIO 🟩🟩🟩⬜🟩
    HELLO 🟩🟩🟩🟩🟩
    6/6
    HELLO ⬜🟨⬜⬜⬜
    ASIDE ⬜⬜🟨⬜🟨
    INEPT 🟨⬜🟨⬜⬜
    WIFEY ⬜🟩⬜🟩⬜
    BIKER ⬜🟩⬜🟩🟩
    GIVER 🟩🟩🟩🟩🟩
    4/6
    GIVER 🟩⬜⬜⬜⬜
    GLOAM 🟩⬜⬜🟨🟨
    GAUMS 🟩🟩⬜🟩⬜
    GAMMA 🟩🟩🟩🟩🟩
    3/6
    GAMMA ⬜🟩⬜⬜⬜
    TARES ⬜🟩🟨⬜🟨
    SAVOR 🟩🟩🟩🟩🟩
    Final 2/2
    BRUIN ⬜🟩🟩🟩⬜
    FRUIT ⬜🟩🟩🟩⬜
    FAIL: DRUID

# cemantix.certitudes.org 🧩 #1320 🥳 586 ⏱️ 0:08:29.716773

🤔 587 attempts
📜 1 sessions
🫧 31 chat sessions
⁉️ 195 chat prompts
🤖 96 llama3.2:latest replies
🤖 99 gemma3:latest replies
🔥   3 🥵  30 😎 164 🥶 344 🧊  45

      $1 #587   ~1 mutuel           100.00°C 🥳 1000‰
      $2  #47 ~192 assurance         50.74°C 🔥  997‰
      $3  #78 ~178 prévoyance        50.72°C 🔥  996‰
      $4 #487  ~24 assuré            45.65°C 🔥  993‰
      $5 #271 ~112 solidarité        41.66°C 🥵  988‰
      $6 #484  ~26 assureur          41.09°C 🥵  986‰
      $7 #300  ~94 social            39.08°C 🥵  981‰
      $8 #353  ~73 organisme         38.54°C 🥵  979‰
      $9 #384  ~59 commun            38.20°C 🥵  978‰
     $10 #292  ~98 complémentaire    36.60°C 🥵  973‰
     $11 #462  ~33 échange           35.84°C 🥵  971‰
     $35 #209 ~136 remboursement     29.48°C 😎  897‰
    $199  #97      discipline        18.69°C 🥶
    $543 #545      récépissé         -0.24°C 🧊

# cemantle.certitudes.org 🧩 #1287 🥳 322 ⏱️ 0:05:16.620334

🤔 323 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 65 chat prompts
🤖 49 llama3.2:latest replies
🤖 16 gemma3:latest replies
🔥   3 🥵  12 😎  40 🥶 248 🧊  19

      $1 #323   ~1 earnings              100.00°C 🥳 1000‰
      $2 #307  ~12 profitability          57.30°C 🔥  996‰
      $3 #311   ~8 dividend               53.61°C 🔥  995‰
      $4 #303  ~16 revenue                52.12°C 🔥  992‰
      $5 #265  ~29 fiscal                 46.86°C 🥵  989‰
      $6 #287  ~22 growth                 42.46°C 🥵  984‰
      $7 #306  ~13 depreciation           41.09°C 🥵  979‰
      $8 #305  ~14 amortization           37.76°C 🥵  966‰
      $9 #304  ~15 capitalization         35.03°C 🥵  960‰
     $10 #316   ~6 investment             31.75°C 🥵  930‰
     $11 #318   ~4 acquirer               31.28°C 🥵  925‰
     $17 #264  ~30 economy                28.91°C 😎  891‰
     $57 #160      compensation           16.47°C 🥶
    $305 #285      evaluation             -0.12°C 🧊
