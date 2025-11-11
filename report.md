# 2025-11-12

- 🔗 spaceword.org 🧩 2025-11-11 🏁 score 2173 ranked 7.1% 26/365 ⏱️ 2:26:02.244156
- 🔗 alfagok.diginaut.net 🧩 #375 🥳 14 ⏱️ 0:00:50.803993
- 🔗 alphaguess.com 🧩 #841 🥳 13 ⏱️ 0:00:29.299618
- 🔗 squareword.org 🧩 #1381 🥳 7 ⏱️ 0:01:59.268388
- 🔗 dictionary.com hurdle 🧩 #1411 🥳 17 ⏱️ 0:03:46.263038
- 🔗 dontwordle.com 🧩 #1268 🥳 6 ⏱️ 0:01:36.446807
- 🔗 cemantle.certitudes.org 🧩 #1318 🥳 235 ⏱️ 0:01:35.330623
- 🔗 cemantix.certitudes.org 🧩 #1351 🥳 218 ⏱️ 0:03:54.250004

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








# spaceword.org 🧩 2025-11-11 🏁 score 2173 ranked 7.1% 26/365 ⏱️ 2:26:02.244156

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 26/365

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ C _ V _ _ _ K O P   
      _ O _ A G O N I S E   
      _ S Q U I R E D _ A   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #375 🥳 14 ⏱️ 0:00:50.803993

🤔 14 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+1      [     1] &-tekens     
    @+2      [     2] -cijferig    
    @+3      [     3] -e-mail      
    @+99842  [ 99842] examen       q1  ? after
    @+149326 [149326] huis         q2  ? after
    @+174543 [174543] kinderboeken q3  ? after
    @+187075 [187075] kroon        q4  ? after
    @+193409 [193409] lawaai       q5  ? after
    @+196573 [196573] let          q6  ? after
    @+198147 [198147] licht        q7  ? after
    @+198494 [198494] lichts       q9  ? after
    @+198649 [198649] lid          q10 ? after
    @+198711 [198711] lied         q11 ? after
    @+198777 [198777] lief         q12 ? after
    @+198800 [198800] liefde       q13 ? it
    @+198800 [198800] liefde       done. it
    @+198848 [198848] liefdes      q8  ? before
    @+199766 [199766] lijn         q0  ? before

# alphaguess.com 🧩 #841 🥳 13 ⏱️ 0:00:29.299618

🤔 13 attempts
📜 1 sessions

    @        [     0] aa     
    @+1      [     1] aah    
    @+2      [     2] aahed  
    @+3      [     3] aahing 
    @+98226  [ 98226] mach   q0  ? after
    @+110131 [110131] need   q3  ? after
    @+116110 [116110] oppo   q4  ? after
    @+118744 [118744] over   q5  ? after
    @+120358 [120358] overt  q6  ? after
    @+120876 [120876] pa     q7  ? after
    @+121490 [121490] pallid q8  ? after
    @+121791 [121791] pang   q9  ? after
    @+121891 [121891] pant   q10 ? after
    @+121975 [121975] pap    q11 ? after
    @+122003 [122003] paper  q12 ? it
    @+122003 [122003] paper  done. it
    @+122111 [122111] par    q2  ? before
    @+147331 [147331] rho    q1  ? before

# squareword.org 🧩 #1381 🥳 7 ⏱️ 0:01:59.268388

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S K A T E
    W A G E D
    A P I N G
    P U L S E
    S T E E D

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1411 🥳 17 ⏱️ 0:03:46.263038

📜 1 sessions
💰 score: 9900

    6/6
    EARLS ⬜⬜🟨⬜⬜
    MINOR ⬜⬜🟨🟨🟨
    CROWN ⬜🟩🟩🟩🟩
    BROWN ⬜🟩🟩🟩🟩
    GROWN ⬜🟩🟩🟩🟩
    FROWN 🟩🟩🟩🟩🟩
    4/6
    FROWN ⬜⬜🟨⬜⬜
    COSET ⬜🟩⬜⬜🟩
    VOMIT ⬜🟩⬜⬜🟩
    DOUBT 🟩🟩🟩🟩🟩
    3/6
    DOUBT ⬜⬜🟨🟨⬜
    BULKS 🟩🟩⬜⬜🟨
    BUSHY 🟩🟩🟩🟩🟩
    3/6
    BUSHY ⬜⬜⬜⬜⬜
    ADORN ⬜⬜⬜🟨🟩
    REIGN 🟩🟩🟩🟩🟩
    Final 1/2
    REPLY 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1268 🥳 6 ⏱️ 0:01:36.446807

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:ADDAX n n n n n remain:6032
    ⬜⬜⬜⬜⬜ tried:PEWEE n n n n n remain:2306
    ⬜⬜⬜⬜⬜ tried:JOMON n n n n n remain:674
    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:223
    ⬜⬜⬜⬜⬜ tried:GRUFF n n n n n remain:2
    🟩⬜🟩🟩🟩 tried:SLYLY Y n Y Y Y remain:1

    Undos used: 4

      1 words remaining
    x 6 unused letters
    = 6 total score

# cemantle.certitudes.org 🧩 #1318 🥳 235 ⏱️ 0:01:35.330623

🤔 236 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 69 chat prompts
🤖 69 gemma3:latest replies
🥵  10 😎  30 🥶 182 🧊  13

      $1 #236   ~1 screening       100.00°C 🥳 1000‰
      $2 #113  ~28 examination      37.61°C 🥵  982‰
      $3 #218   ~5 biopsy           37.01°C 🥵  981‰
      $4  #97  ~34 treatment        36.21°C 🥵  978‰
      $5 #110  ~29 review           36.03°C 🥵  977‰
      $6  #85  ~36 diagnosis        35.88°C 🥵  974‰
      $7 #117  ~27 inspection       35.30°C 🥵  970‰
      $8  #84  ~37 evaluation       33.75°C 🥵  955‰
      $9 #204   ~9 check            31.42°C 🥵  932‰
     $10 #136  ~21 test             31.41°C 🥵  931‰
     $11 #212   ~7 invasive         30.87°C 🥵  925‰
     $12 #105  ~31 verification     29.33°C 😎  899‰
     $42 #111      audit            19.19°C 🥶
    $224 #184      verdict          -0.19°C 🧊

# cemantix.certitudes.org 🧩 #1351 🥳 218 ⏱️ 0:03:54.250004

🤔 219 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 38 chat prompts
🤖 38 gemma3:latest replies
😱   1 🔥   1 🥵   4 😎  29 🥶 174 🧊   9

      $1 #219   ~1 lent             100.00°C 🥳 1000‰
      $2 #156  ~14 lenteur           61.39°C 😱  999‰
      $3 #201   ~8 ralentir          61.33°C 🔥  998‰
      $4 #124  ~19 lourd             41.83°C 🥵  973‰
      $5 #141  ~17 pénible           38.05°C 🥵  938‰
      $6  #56  ~32 intense           36.95°C 🥵  917‰
      $7  #61  ~29 profond           36.46°C 🥵  909‰
      $8  #21  ~36 sombre            35.86°C 😎  898‰
      $9 #103  ~22 frénétique        35.14°C 😎  882‰
     $10  #65  ~27 puissant          34.86°C 😎  877‰
     $11 #107  ~21 subtil            34.50°C 😎  862‰
     $12 #217   ~2 inéluctable       34.19°C 😎  854‰
     $37 #186      mélancolie        25.83°C 🥶
    $211 #147      opprimé           -0.72°C 🧊
