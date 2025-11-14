# 2025-11-15

- 🔗 spaceword.org 🧩 2025-11-14 🏁 score 2170 ranked 23.2% 82/353 ⏱️ 0:39:03.966933
- 🔗 alfagok.diginaut.net 🧩 #378 🥳 10 ⏱️ 0:00:31.776206
- 🔗 alphaguess.com 🧩 #844 🥳 14 ⏱️ 0:00:34.581184
- 🔗 squareword.org 🧩 #1384 🥳 7 ⏱️ 0:01:40.936501
- 🔗 dictionary.com hurdle 🧩 #1414 😦 19 ⏱️ 0:03:10.295978
- 🔗 dontwordle.com 🧩 #1271 🥳 6 ⏱️ 0:01:32.433571
- 🔗 cemantle.certitudes.org 🧩 #1321 🥳 116 ⏱️ 0:00:44.219853
- 🔗 cemantix.certitudes.org 🧩 #1354 🥳 295 ⏱️ 0:10:34.562307

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











# spaceword.org 🧩 2025-11-14 🏁 score 2170 ranked 23.2% 82/353 ⏱️ 0:39:03.966933

📜 3 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 82/353

      _ _ _ _ _ J _ _ _ _   
      _ _ _ _ _ E S _ _ _   
      _ _ _ _ _ D A _ _ _   
      _ _ _ _ S I T _ _ _   
      _ _ _ _ Q _ I _ _ _   
      _ _ _ _ U _ N _ _ _   
      _ _ _ _ E _ Y _ _ _   
      _ _ _ _ E M _ _ _ _   
      _ _ _ _ Z A _ _ _ _   
      _ _ _ _ E C O _ _ _   


# alfagok.diginaut.net 🧩 #378 🥳 10 ⏱️ 0:00:31.776206

🤔 10 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+49910  [ 49910] bol       q2  ? after
    @+51214  [ 51214] boot      q9  ? it
    @+51214  [ 51214] boot      done. it
    @+52689  [ 52689] bouw      q8  ? before
    @+56081  [ 56081] brood     q7  ? before
    @+62286  [ 62286] cement    q6  ? before
    @+74758  [ 74758] dc        q5  ? before
    @+99840  [ 99840] examen    q1  ? before
    @+199764 [199764] lijn      q0  ? before

# alphaguess.com 🧩 #844 🥳 14 ⏱️ 0:00:34.581184

🤔 14 attempts
📜 1 sessions

    @        [     0] aa        
    @+1      [     1] aah       
    @+2      [     2] aahed     
    @+3      [     3] aahing    
    @+98226  [ 98226] mach      q0  ? after
    @+147331 [147331] rho       q1  ? after
    @+159613 [159613] slug      q3  ? after
    @+162646 [162646] speed     q5  ? after
    @+164206 [164206] squilgee  q6  ? after
    @+164254 [164254] squirish  q11 ? after
    @+164266 [164266] squirrel  q13 ? it
    @+164266 [164266] squirrel  done. it
    @+164278 [164278] squirt    q12 ? before
    @+164301 [164301] squush    q10 ? before
    @+164395 [164395] staff     q9  ? before
    @+164596 [164596] staminody q8  ? before
    @+164986 [164986] stay      q7  ? before
    @+165767 [165767] stint     q4  ? before
    @+171931 [171931] tag       q2  ? before

# squareword.org 🧩 #1384 🥳 7 ⏱️ 0:01:40.936501

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟩 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B L U R B
    L A S E R
    A G A V E
    S E G U E
    T R E E D

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1414 😦 19 ⏱️ 0:03:10.295978

📜 1 sessions
💰 score: 4760

    6/6
    TSADE ⬜🟨🟨⬜⬜
    NAILS ⬜🟩⬜⬜🟨
    MASHY ⬜🟩🟨⬜🟩
    SAURY 🟩🟩⬜⬜🟩
    SAVOY 🟩🟩🟩⬜🟩
    SAVVY 🟩🟩🟩🟩🟩
    4/6
    SAVVY 🟩⬜⬜⬜⬜
    SHOTE 🟩⬜⬜⬜⬜
    SLUMP 🟩🟩🟩⬜🟩
    SLURP 🟩🟩🟩🟩🟩
    3/6
    SLURP ⬜🟨🟨⬜🟩
    TULIP ⬜🟨🟨⬜🟩
    LAYUP 🟩🟩🟩🟩🟩
    4/6
    LAYUP 🟨⬜⬜⬜⬜
    IDLES ⬜⬜🟨🟨⬜
    CLERK ⬜🟩🟨⬜🟨
    BLOKE 🟩🟩🟩🟩🟩
    Final 2/2
    DIRGE ⬜🟨🟨⬜🟩
    WRITE ⬜🟩🟩⬜🟩
    FAIL: CRIME

# dontwordle.com 🧩 #1271 🥳 6 ⏱️ 0:01:32.433571

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:BABKA n n n n n remain:5942
    ⬜⬜⬜⬜⬜ tried:WOOZY n n n n n remain:2526
    ⬜⬜⬜⬜⬜ tried:JUJUS n n n n n remain:740
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:204
    ⬜🟨⬜⬜⬜ tried:CIVIC n m n n n remain:15
    🟨⬜🟩⬜⬜ tried:EXINE m n Y n n remain:2

    Undos used: 4

      2 words remaining
    x 7 unused letters
    = 14 total score

# cemantle.certitudes.org 🧩 #1321 🥳 116 ⏱️ 0:00:44.219853

🤔 117 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 32 chat prompts
🤖 32 gemma3:latest replies
🥵   2 😎   8 🥶 103 🧊   3

      $1 #117   ~1 diagnostic       100.00°C 🥳 1000‰
      $2  #85   ~5 calibration       47.77°C 🥵  948‰
      $3  #69   ~6 quantification    46.88°C 🥵  940‰
      $4  #66   ~7 measurement       43.39°C 😎  880‰
      $5 #105   ~3 testing           42.66°C 😎  866‰
      $6  #64   ~8 evaluation        39.73°C 😎  773‰
      $7 #101   ~4 validation        38.78°C 😎  731‰
      $8  #60  ~10 quantitative      37.51°C 😎  666‰
      $9 #109   ~2 sensor            32.83°C 😎  244‰
     $10  #21  ~11 analysis          32.54°C 😎  196‰
     $11  #61   ~9 assessment        32.54°C 😎  197‰
     $12 #115      mapping           30.92°C 🥶
     $13  #25      research          30.69°C 🥶
    $115   #2      ephemeral         -1.89°C 🧊

# cemantix.certitudes.org 🧩 #1354 🥳 295 ⏱️ 0:10:34.562307

🤔 296 attempts
📜 1 sessions
🫧 14 chat sessions
⁉️ 84 chat prompts
🤖 82 gemma3:latest replies
🤖 2 qwen3:8b replies
🔥   2 🥵   9 😎  34 🥶 205 🧊  45

      $1 #296   ~1 chaussure        100.00°C 🥳 1000‰
      $2 #238  ~13 chaussures        60.57°C 🔥  998‰
      $3 #280   ~8 semelle           59.28°C 🔥  997‰
      $4 #288   ~4 botte             52.00°C 🥵  986‰
      $5 #294   ~3 talon             48.57°C 🥵  973‰
      $6 #227  ~19 pantalon          48.23°C 🥵  971‰
      $7 #287   ~5 cuir              45.19°C 🥵  957‰
      $8 #229  ~18 veste             43.82°C 🥵  948‰
      $9 #232  ~17 bermuda           40.65°C 🥵  922‰
     $10 #236  ~14 cuissard          40.01°C 🥵  917‰
     $11 #221  ~21 short             39.73°C 🥵  910‰
     $13 #202  ~26 culotte           38.00°C 😎  887‰
     $47  #62      satiné            21.59°C 🥶
    $252  #45      velouté           -0.14°C 🧊
