# 2025-11-26

- 🔗 spaceword.org 🧩 2025-11-25 🏁 score 2172 ranked 24.0% 87/363 ⏱️ 2:53:26.471947
- 🔗 alfagok.diginaut.net 🧩 #389 🥳 19 ⏱️ 0:01:19.543003
- 🔗 alphaguess.com 🧩 #855 🥳 17 ⏱️ 0:00:41.596948
- 🔗 squareword.org 🧩 #1395 🥳 7 ⏱️ 0:05:29.289152
- 🔗 dictionary.com hurdle 🧩 #1425 😦 20 ⏱️ 0:04:29.494315
- 🔗 dontwordle.com 🧩 #1282 🥳 6 ⏱️ 0:02:30.040954
- 🔗 cemantle.certitudes.org 🧩 #1332 🥳 399 ⏱️ 0:12:44.298373
- 🔗 cemantix.certitudes.org 🧩 #1365 🥳 751 ⏱️ 0:20:23.222077

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






















# spaceword.org 🧩 2025-11-25 🏁 score 2172 ranked 24.0% 87/363 ⏱️ 2:53:26.471947

📜 3 sessions
- tiles: 21/21
- score: 2172 bonus: +72
- rank: 87/363

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ J O T A _ _ _   
      _ _ _ _ _ E L _ _ _   
      _ _ _ P A L E _ _ _   
      _ _ _ _ _ O X _ _ _   
      _ _ _ _ _ M I _ _ _   
      _ _ _ _ K I N _ _ _   
      _ _ _ R I C E _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# alfagok.diginaut.net 🧩 #389 🥳 19 ⏱️ 0:01:19.543003

🤔 19 attempts
📜 2 sessions

    @        [     0] &-teken        
    @+1      [     1] &-tekens       
    @+2      [     2] -cijferig      
    @+3      [     3] -e-mail        
    @+199762 [199762] lijn           q0  ? after
    @+223475 [223475] mol            q5  ? after
    @+235528 [235528] octrooi        q6  ? after
    @+238642 [238642] on             q7  ? after
    @+243112 [243112] onroerend      q8  ? after
    @+243272 [243272] ont            q10 ? after
    @+244292 [244292] ontraad        q11 ? after
    @+244810 [244810] onttakeld      q12 ? after
    @+245069 [245069] ontwapen       q13 ? after
    @+245145 [245145] ontwerp        q14 ? after
    @+245237 [245237] ontwerpstudies q15 ? after
    @+245280 [245280] ontwijd        q16 ? after
    @+245300 [245300] ontwikkel      q17 ? after
    @+245313 [245313] ontwikkeld     q18 ? it
    @+245313 [245313] ontwikkeld     done. it
    @+245329 [245329] ontwikkeling   q9  ? before
    @+247584 [247584] op             q2  ? before
    @+299630 [299630] schud          q1  ? before


# alphaguess.com 🧩 #855 🥳 17 ⏱️ 0:00:41.596948

🤔 17 attempts
📜 1 sessions

    @       [    0] aa          
    @+1     [    1] aah         
    @+2     [    2] aahed       
    @+3     [    3] aahing      
    @+47387 [47387] dis         q1  ? after
    @+53403 [53403] el          q4  ? after
    @+56748 [56748] equate      q5  ? after
    @+58364 [58364] ex          q6  ? after
    @+58373 [58373] exact       q12 ? after
    @+58381 [58381] exacting    q14 ? after
    @+58386 [58386] exactions   q15 ? after
    @+58389 [58389] exactly     q16 ? it
    @+58389 [58389] exactly     done. it
    @+58391 [58391] exactnesses q13 ? before
    @+58409 [58409] exalt       q11 ? before
    @+58470 [58470] excavate    q10 ? before
    @+58577 [58577] excitation  q9  ? before
    @+58789 [58789] exempt      q8  ? before
    @+59223 [59223] expel       q7  ? before
    @+60090 [60090] face        q3  ? before
    @+72807 [72807] gremolata   q2  ? before
    @+98226 [98226] mach        q0  ? before

# squareword.org 🧩 #1395 🥳 7 ⏱️ 0:05:29.289152

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C A L D
    P A T I O
    A R R O W
    R E I N S
    E R A S E

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1425 😦 20 ⏱️ 0:04:29.494315

📜 1 sessions
💰 score: 4660

    4/6
    AEONS ⬜⬜🟩⬜🟨
    SHOUT 🟩⬜🟩⬜⬜
    SPOIL 🟩⬜🟩⬜🟨
    SCOLD 🟩🟩🟩🟩🟩
    5/6
    SCOLD ⬜⬜⬜🟩⬜
    ANGLE ⬜⬜⬜🟩⬜
    RUMLY ⬜🟩⬜🟩⬜
    BUILT ⬜🟩🟩🟩🟩
    QUILT 🟩🟩🟩🟩🟩
    4/6
    QUILT ⬜⬜⬜⬜⬜
    ROADS ⬜🟨🟨⬜⬜
    BANJO 🟨🟩⬜⬜🟩
    MAMBO 🟩🟩🟩🟩🟩
    5/6
    MAMBO ⬜🟨⬜⬜⬜
    LEADS ⬜⬜🟩⬜🟨
    CRASH ⬜🟨🟩🟨⬜
    START 🟩🟩🟩🟨⬜
    STAIR 🟩🟩🟩🟩🟩
    Final 2/2
    PHASE ⬜🟨🟩🟩⬜
    GNASH ⬜⬜🟩🟩🟩
    FAIL: AWASH

# dontwordle.com 🧩 #1282 🥳 6 ⏱️ 0:02:30.040954

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:WALLA n n n n n remain:5351
    ⬜⬜⬜⬜⬜ tried:JEEZE n n n n n remain:2419
    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:1020
    ⬜⬜⬜⬜⬜ tried:SNUGS n n n n n remain:109
    ⬜⬜⬜⬜🟨 tried:PHPHT n n n n m remain:14
    ⬜🟩⬜🟩⬜ tried:MOTTO n Y n Y n remain:3

    Undos used: 4

      3 words remaining
    x 8 unused letters
    = 24 total score

# cemantle.certitudes.org 🧩 #1332 🥳 399 ⏱️ 0:12:44.298373

🤔 400 attempts
📜 1 sessions
🫧 15 chat sessions
⁉️ 76 chat prompts
🤖 76 llama4:latest replies
🥵  12 😎  58 🥶 317 🧊  12

      $1 #400   ~1 temporary       100.00°C 🥳 1000‰
      $2  #50  ~70 shelter          34.74°C 🥵  986‰
      $3  #70  ~65 respite          34.44°C 🥵  984‰
      $4 #399   ~2 relocation       33.05°C 🥵  976‰
      $5  #54  ~68 refuge           32.62°C 🥵  974‰
      $6 #112  ~58 relief           32.02°C 🥵  973‰
      $7 #175  ~42 housing          31.50°C 🥵  968‰
      $8 #280  ~22 fix              31.29°C 🥵  967‰
      $9 #228  ~39 alleviate        30.65°C 🥵  959‰
     $10 #127  ~52 reprieve         30.27°C 🥵  953‰
     $11 #170  ~45 accommodation    30.11°C 🥵  951‰
     $14 #235  ~34 remedy           27.08°C 😎  892‰
     $72 #287      harborage        18.82°C 🥶
    $389 #110      lair             -0.32°C 🧊

# cemantix.certitudes.org 🧩 #1365 🥳 751 ⏱️ 0:20:23.222077

🤔 752 attempts
📜 1 sessions
🫧 27 chat sessions
⁉️ 151 chat prompts
🤖 151 llama4:latest replies
🔥   6 🥵  23 😎 105 🥶 521 🧊  96

      $1 #752   ~1 corde            100.00°C 🥳 1000‰
      $2 #127 ~101 archet            49.86°C 🔥  996‰
      $3 #155  ~87 glissando         47.88°C 🔥  994‰
      $4 #225  ~73 vibrato           47.35°C 🔥  993‰
      $5 #141  ~96 plectre           46.61°C 🔥  992‰
      $6 #125 ~103 violon            44.41°C 🔥  991‰
      $7  #15 ~131 cithare           43.81°C 🔥  990‰
      $8 #467  ~43 ficelle           43.18°C 🥵  989‰
      $9 #110 ~111 xylophone         42.24°C 🥵  985‰
     $10  #98 ~116 harmonique        41.94°C 🥵  981‰
     $11 #118 ~106 flûte             41.50°C 🥵  979‰
     $31 #191  ~79 sonorité          35.75°C 😎  897‰
    $136 #318      traction          24.71°C 🥶
    $657 #731      récupération      -0.24°C 🧊
