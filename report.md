# 2025-12-09

- 🔗 spaceword.org 🧩 2025-12-08 🏁 score 2173 ranked 3.2% 11/345 ⏱️ 4:21:35.030772
- 🔗 alfagok.diginaut.net 🧩 #402 🥳 22 ⏱️ 0:01:05.581866
- 🔗 alphaguess.com 🧩 #868 🥳 11 ⏱️ 0:00:25.140427
- 🔗 squareword.org 🧩 #1408 🥳 8 ⏱️ 0:03:11.157175
- 🔗 dictionary.com hurdle 🧩 #1438 🥳 19 ⏱️ 0:05:05.597099
- 🔗 dontwordle.com 🧩 #1295 🥳 6 ⏱️ 0:01:32.188081
- 🔗 cemantle.certitudes.org 🧩 #1345 🥳 929 ⏱️ 0:52:31.997788
- 🔗 cemantix.certitudes.org 🧩 #1378 🥳 118 ⏱️ 0:03:21.884445

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













# spaceword.org 🧩 2025-12-08 🏁 score 2173 ranked 3.2% 11/345 ⏱️ 4:21:35.030772

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 11/345

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ Q U A _ _ _   
      _ _ _ _ I N _ _ _ _   
      _ _ _ _ _ A G _ _ _   
      _ _ _ _ F I R _ _ _   
      _ _ _ _ R _ O _ _ _   
      _ _ _ _ O _ V _ _ _   
      _ _ _ _ U S E _ _ _   
      _ _ _ _ Z _ _ _ _ _   
      _ _ _ _ Y O D _ _ _   


# alfagok.diginaut.net 🧩 #402 🥳 22 ⏱️ 0:01:05.581866

🤔 22 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+99760  [ 99760] ex        q2  ? after
    @+111415 [111415] ge        q4  ? after
    @+120906 [120906] gepunte   q6  ? after
    @+125654 [125654] gezeefd   q7  ? after
    @+127808 [127808] glas      q8  ? after
    @+128819 [128819] goed      q9  ? after
    @+129599 [129599] gooi      q10 ? after
    @+129606 [129606] gooien    q21 ? it
    @+129606 [129606] gooien    done. it
    @+129611 [129611] gooilijn  q20 ? before
    @+129617 [129617] goor      q13 ? before
    @+129670 [129670] gord      q12 ? before
    @+129864 [129864] goud      q11 ? before
    @+130397 [130397] gracht    q5  ? before
    @+149457 [149457] huis      q3  ? before
    @+199839 [199839] lijm      q0  ? after
    @+199839 [199839] lijm      q1  ? before

# alphaguess.com 🧩 #868 🥳 11 ⏱️ 0:00:25.140427

🤔 11 attempts
📜 1 sessions

    @        [     0] aa        
    @+1      [     1] aah       
    @+2      [     2] aahed     
    @+3      [     3] aahing    
    @+98225  [ 98225] mach      q0  ? after
    @+147330 [147330] rho       q1  ? after
    @+171930 [171930] tag       q2  ? after
    @+171972 [171972] tail      q10 ? it
    @+171972 [171972] tail      done. it
    @+172064 [172064] take      q9  ? before
    @+172208 [172208] tally     q8  ? before
    @+172492 [172492] tap       q7  ? before
    @+173170 [173170] technical q6  ? before
    @+174416 [174416] test      q5  ? before
    @+176967 [176967] tom       q4  ? before
    @+182017 [182017] un        q3  ? before

# squareword.org 🧩 #1408 🥳 8 ⏱️ 0:03:11.157175

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟩 🟨
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A M I S S
    P I V O T
    A N O D E
    R E R A N
    T R Y S T

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1438 🥳 19 ⏱️ 0:05:05.597099

📜 3 sessions
💰 score: 9700

    4/6
    SAICE 🟨⬜⬜⬜🟨
    ROSET ⬜⬜🟩🟩🟩
    UPSET 🟩⬜🟩🟩🟩
    UNSET 🟩🟩🟩🟩🟩
    5/6
    UNSET ⬜⬜⬜⬜⬜
    LOGIC ⬜🟩⬜⬜🟨
    ROCKY ⬜🟩🟨⬜⬜
    POACH ⬜🟩🟩🟩🟩
    COACH 🟩🟩🟩🟩🟩
    4/6
    COACH ⬜⬜🟨⬜⬜
    SERAL 🟨⬜⬜🟨⬜
    WAINS 🟩🟩⬜⬜🟨
    WASPY 🟩🟩🟩🟩🟩
    4/6
    WASPY ⬜🟨🟨⬜⬜
    STEAL 🟨🟨⬜🟨⬜
    AIRTS 🟩⬜🟨🟨🟨
    ASTRO 🟩🟩🟩🟩🟩
    Final 2/2
    SLUTS 🟩⬜🟩🟨⬜
    STUFF 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1295 🥳 6 ⏱️ 0:01:32.188081

📜 2 sessions
💰 score: 36

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:CALLA n n n n n remain:4913
    ⬜⬜⬜⬜⬜ tried:ESSES n n n n n remain:941
    ⬜⬜⬜⬜⬜ tried:HOKKU n n n n n remain:132
    ⬜⬜⬜⬜🟩 tried:PYGMY n n n n Y remain:36
    ⬜🟩🟨⬜🟩 tried:BIDDY n Y m n Y remain:5
    🟩🟩⬜⬜🟩 tried:DIVVY Y Y n n Y remain:4

    Undos used: 3

      4 words remaining
    x 9 unused letters
    = 36 total score

# cemantle.certitudes.org 🧩 #1345 🥳 929 ⏱️ 0:52:31.997788

🤔 930 attempts
📜 2 sessions
🫧 87 chat sessions
⁉️ 473 chat prompts
🤖 81 glm4:latest replies
🤖 263 falcon3:7b replies
🤖 12 smallthinker:latest replies
🤖 17 llama3.3:latest replies
🤖 44 falcon3:10b replies
🤖 48 gemma3:27b replies
🤖 2 gpt-oss:20b replies
🤖 5 alibayram/hunyuan:7b replies
😱   1 🔥   6 🥵  16 😎  66 🥶 830 🧊  10

      $1 #930   ~1 moreover            100.00°C 🥳 1000‰
      $2 #926   ~3 furthermore          65.78°C 😱  999‰
      $3 #718  ~46 therefore            64.49°C 🔥  998‰
      $4 #708  ~50 nevertheless         56.69°C 🔥  997‰
      $5 #719  ~45 hence                56.29°C 🔥  996‰
      $6 #705  ~52 consequently         55.81°C 🔥  995‰
      $7 #838  ~14 evidently            51.33°C 🔥  992‰
      $8 #763  ~32 manifestly           51.28°C 🔥  991‰
      $9 #706  ~51 however              50.81°C 🥵  989‰
     $10 #711  ~49 thus                 50.60°C 🥵  988‰
     $11 #746  ~37 clearly              47.73°C 🥵  984‰
     $25  #76  ~89 implication          41.72°C 😎  897‰
     $91 #424      tacit                33.47°C 🥶
    $921 #571      incident             -0.12°C 🧊

# cemantix.certitudes.org 🧩 #1378 🥳 118 ⏱️ 0:03:21.884445

🤔 119 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 46 chat prompts
🤖 46 falcon3:10b replies
🥵  8 😎 20 🥶 76 🧊 14

      $1 #119   ~1 suspension       100.00°C 🥳 1000‰
      $2  #76  ~21 interdiction      35.65°C 🥵  982‰
      $3  #88  ~18 annulation        35.08°C 🥵  980‰
      $4 #111   ~7 référé            33.66°C 🥵  973‰
      $5  #57  ~26 annuler           33.34°C 🥵  972‰
      $6 #116   ~4 décision          31.64°C 🥵  955‰
      $7 #103  ~12 exécution         31.63°C 🥵  954‰
      $8  #94  ~16 révoquer          31.45°C 🥵  952‰
      $9 #109   ~9 exécutoire        29.50°C 🥵  910‰
     $10  #64  ~25 rejeter           27.25°C 😎  847‰
     $11 #113   ~6 autorisation      27.02°C 😎  841‰
     $12 #118   ~2 motif             26.98°C 😎  839‰
     $29 #114      contestation      20.19°C 🥶
    $106  #24      prix              -0.12°C 🧊
