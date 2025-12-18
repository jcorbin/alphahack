# 2025-12-19

- 🔗 spaceword.org 🧩 2025-12-18 🏁 score 2173 ranked 5.5% 18/328 ⏱️ 1:35:39.364495
- 🔗 alfagok.diginaut.net 🧩 #412 🥳 12 ⏱️ 0:00:32.103199
- 🔗 alphaguess.com 🧩 #878 🥳 14 ⏱️ 0:00:26.982681
- 🔗 squareword.org 🧩 #1418 🥳 6 ⏱️ 0:02:05.641471
- 🔗 dictionary.com hurdle 🧩 #1448 🥳 16 ⏱️ 0:03:35.685114
- 🔗 dontwordle.com 🧩 #1305 🥳 6 ⏱️ 0:01:39.408436
- 🔗 cemantle.certitudes.org 🧩 #1355 🥳 113 ⏱️ 0:04:34.140967
- 🔗 cemantix.certitudes.org 🧩 #1388 🥳 156 ⏱️ 0:08:55.982920

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























# spaceword.org 🧩 2025-12-18 🏁 score 2173 ranked 5.5% 18/328 ⏱️ 1:35:39.364495

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 18/328

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ F E E _ _ _   
      _ _ _ _ _ _ Q _ _ _   
      _ _ _ _ J _ U _ _ _   
      _ _ _ _ A M I _ _ _   
      _ _ _ _ R U N _ _ _   
      _ _ _ _ H _ O _ _ _   
      _ _ _ _ E _ X _ _ _   
      _ _ _ _ A D _ _ _ _   
      _ _ _ _ D A S _ _ _   


# alfagok.diginaut.net 🧩 #412 🥳 12 ⏱️ 0:00:32.103199

🤔 12 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199838 [199838] lijm      q0  ? after
    @+299760 [299760] schub     q1  ? after
    @+302790 [302790] shredder  q6  ? after
    @+304304 [304304] skelet    q7  ? after
    @+304877 [304877] slag      q8  ? after
    @+305351 [305351] slecht    q9  ? after
    @+305583 [305583] sleper    q10 ? after
    @+305623 [305623] sleutel   q11 ? it
    @+305623 [305623] sleutel   done. it
    @+305824 [305824] slijm     q5  ? before
    @+311930 [311930] spier     q4  ? before
    @+324336 [324336] sub       q3  ? before
    @+349545 [349545] vakantie  q2  ? before

# alphaguess.com 🧩 #878 🥳 14 ⏱️ 0:00:26.982681

🤔 14 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+47387 [47387] dis        q1  ? after
    @+49434 [49434] do         q5  ? after
    @+49855 [49855] dom        q8  ? after
    @+49940 [49940] don        q10 ? after
    @+49955 [49955] done       q13 ? it
    @+49955 [49955] done       done. it
    @+49982 [49982] donne      q12 ? before
    @+50037 [50037] doohickies q11 ? before
    @+50133 [50133] dopiest    q9  ? before
    @+50411 [50411] dove       q7  ? before
    @+51408 [51408] drunk      q6  ? before
    @+53403 [53403] el         q4  ? before
    @+60090 [60090] face       q3  ? before
    @+72806 [72806] gremmy     q2  ? before
    @+98225 [98225] mach       q0  ? before

# squareword.org 🧩 #1418 🥳 6 ⏱️ 0:02:05.641471

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P A L E D
    O L I V E
    O P T I C
    C H E C K
    H A R T S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1448 🥳 16 ⏱️ 0:03:35.685114

📜 2 sessions
💰 score: 10000

    3/6
    STARE ⬜⬜🟨⬜🟨
    AMEND 🟩⬜🟨🟨⬜
    ANGEL 🟩🟩🟩🟩🟩
    3/6
    ANGEL ⬜⬜⬜🟨⬜
    VERST ⬜🟨🟩🟩⬜
    CURSE 🟩🟩🟩🟩🟩
    4/6
    CURSE ⬜⬜🟩🟨🟩
    SARGE 🟩⬜🟩⬜🟩
    SERVE 🟩🟨🟩⬜🟩
    SPREE 🟩🟩🟩🟩🟩
    4/6
    SPREE ⬜⬜⬜🟨⬜
    KNELT ⬜⬜🟨⬜⬜
    DEMOI ⬜🟩⬜⬜🟨
    WEIGH 🟩🟩🟩🟩🟩
    Final 2/2
    SCOUT 🟩🟩⬜🟨⬜
    SCUFF 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1305 🥳 6 ⏱️ 0:01:39.408436

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:FEMME n n n n n remain:5567
    ⬜⬜⬜⬜⬜ tried:PAPPY n n n n n remain:1743
    ⬜⬜⬜⬜⬜ tried:BRILL n n n n n remain:360
    ⬜⬜⬜⬜⬜ tried:NUDZH n n n n n remain:44
    ⬜🟨⬜⬜🟨 tried:GOGOS n m n n m remain:2
    🟩🟩🟩⬜⬜ tried:STOTT Y Y Y n n remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# cemantle.certitudes.org 🧩 #1355 🥳 113 ⏱️ 0:04:34.140967

🤔 114 attempts
📜 1 sessions
🫧 1 chat sessions
⁉️ 19 chat prompts
🤖 19 dolphin3:latest replies
🔥  2 🥵  6 😎 11 🥶 86 🧊  8

      $1 #114   ~1 pregnancy      100.00°C 🥳 1000‰
      $2  #53  ~16 childbirth      64.75°C 🔥  997‰
      $3  #59  ~13 postpartum      60.35°C 🔥  995‰
      $4  #54  ~15 birth           56.15°C 🥵  983‰
      $5  #65  ~10 postnatal       55.55°C 🥵  979‰
      $6  #60  ~12 baby            52.40°C 🥵  967‰
      $7  #75   ~9 newborn         50.20°C 🥵  958‰
      $8  #88   ~5 doula           45.16°C 🥵  923‰
      $9  #29  ~20 child           43.67°C 🥵  902‰
     $10  #76   ~8 placenta        43.20°C 😎  896‰
     $11  #82   ~7 neonatal        42.71°C 😎  883‰
     $12  #85   ~6 infant          41.72°C 😎  871‰
     $21  #87      checkup         27.59°C 🥶
    $107  #15      umbrella        -0.06°C 🧊

# cemantix.certitudes.org 🧩 #1388 🥳 156 ⏱️ 0:08:55.982920

🤔 157 attempts
📜 1 sessions
🫧 1 chat sessions
⁉️ 49 chat prompts
🤖 49 dolphin3:latest replies
😱   1 🔥   1 🥵   9 😎  18 🥶 109 🧊  18

      $1 #157   ~1 poésie          100.00°C 🥳 1000‰
      $2 #153   ~5 poétique         79.30°C 😱  999‰
      $3 #156   ~2 poète            73.52°C 🔥  997‰
      $4 #154   ~4 lyrique          51.07°C 🥵  981‰
      $5 #107  ~11 élégie           50.94°C 🥵  980‰
      $6  #72  ~24 chanson          46.19°C 🥵  960‰
      $7 #148   ~8 rêverie          45.43°C 🥵  953‰
      $8  #95  ~16 chant            45.03°C 🥵  951‰
      $9 #152   ~6 imaginaire       44.40°C 🥵  944‰
     $10 #155   ~3 métaphorique     42.20°C 🥵  925‰
     $11  #66  ~25 musique          41.77°C 🥵  919‰
     $13  #91  ~18 romantique       40.76°C 😎  890‰
     $31  #30      subtilité        28.14°C 🥶
    $140  #15      cassis           -0.12°C 🧊
