# 2025-12-12

- 🔗 spaceword.org 🧩 2025-12-11 🏁 score 2173 ranked 7.5% 26/348 ⏱️ 0:26:35.043665
- 🔗 alfagok.diginaut.net 🧩 #405 🥳 14 ⏱️ 0:00:37.783602
- 🔗 alphaguess.com 🧩 #871 🥳 14 ⏱️ 0:00:34.830965
- 🔗 squareword.org 🧩 #1411 🥳 8 ⏱️ 0:04:31.179468
- 🔗 dictionary.com hurdle 🧩 #1441 🥳 19 ⏱️ 0:03:05.272785
- 🔗 dontwordle.com 🧩 #1298 😳 6 ⏱️ 0:01:27.064490
- 🔗 cemantle.certitudes.org 🧩 #1348 🥳 759 ⏱️ 1:32:59.693858
- 🔗 cemantix.certitudes.org 🧩 #1381 🥳 265 ⏱️ 0:03:24.904498

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
















# spaceword.org 🧩 2025-12-11 🏁 score 2173 ranked 7.5% 26/348 ⏱️ 0:26:35.043665

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 26/348

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ J O G _ _ _   
      _ _ _ _ _ _ A _ _ _   
      _ _ _ _ C O T _ _ _   
      _ _ _ _ L Y E _ _ _   
      _ _ _ _ A _ A _ _ _   
      _ _ _ _ V _ U _ _ _   
      _ _ _ _ A S _ _ _ _   
      _ _ _ _ T I N _ _ _   
      _ _ _ _ E X _ _ _ _   


# alfagok.diginaut.net 🧩 #405 🥳 14 ⏱️ 0:00:37.783602

🤔 14 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+786    [   786] aan        q5  ? after
    @+2746   [  2746] aanlok     q7  ? after
    @+3705   [  3705] aanstel    q8  ? after
    @+3933   [  3933] aantrek    q10 ? after
    @+3945   [  3945] aantrekken q13 ? it
    @+3945   [  3945] aantrekken done. it
    @+3962   [  3962] aantrof    q12 ? before
    @+3990   [  3990] aanval     q11 ? before
    @+4208   [  4208] aanvlogen  q9  ? before
    @+4710   [  4710] aardappels q6  ? before
    @+8648   [  8648] af         q4  ? before
    @+24912  [ 24912] bad        q3  ? before
    @+49851  [ 49851] boks       q2  ? before
    @+99760  [ 99760] ex         q1  ? before
    @+199839 [199839] lijm       q0  ? before

# alphaguess.com 🧩 #871 🥳 14 ⏱️ 0:00:34.830965

🤔 14 attempts
📜 1 sessions

    @        [     0] aa           
    @+1      [     1] aah          
    @+2      [     2] aahed        
    @+3      [     3] aahing       
    @+98225  [ 98225] mach         q0  ? after
    @+147330 [147330] rho          q1  ? after
    @+171930 [171930] tag          q2  ? after
    @+176967 [176967] tom          q4  ? after
    @+179491 [179491] trifurcate   q5  ? after
    @+180109 [180109] troubles     q8  ? after
    @+180185 [180185] truant       q11 ? after
    @+180225 [180225] truculencies q12 ? after
    @+180239 [180239] true         q13 ? it
    @+180239 [180239] true         done. it
    @+180265 [180265] trugs        q10 ? before
    @+180420 [180420] tsar         q9  ? before
    @+180741 [180741] tune         q6  ? before
    @+182016 [182016] un           q3  ? before

# squareword.org 🧩 #1411 🥳 8 ⏱️ 0:04:31.179468

📜 3 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟨 🟩 🟩 🟨 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟨 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    L A T C H
    E E R I E
    G R A D E
    A I D E D
    L E E R S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1441 🥳 19 ⏱️ 0:03:05.272785

📜 1 sessions
💰 score: 9700

    4/6
    SLATE 🟩⬜⬜⬜⬜
    SWORD 🟩⬜🟩⬜⬜
    SHOCK 🟩⬜🟩🟩🟩
    SMOCK 🟩🟩🟩🟩🟩
    5/6
    SMOCK ⬜⬜🟩⬜⬜
    ALONE ⬜⬜🟩⬜⬜
    FROTH ⬜⬜🟩🟩🟩
    TOOTH ⬜🟩🟩🟩🟩
    BOOTH 🟩🟩🟩🟩🟩
    5/6
    BOOTH ⬜🟨⬜⬜⬜
    ARSON ⬜🟨⬜🟩⬜
    VIGOR ⬜⬜⬜🟩🟨
    REDOX 🟨🟩⬜🟩🟩
    XEROX 🟩🟩🟩🟩🟩
    4/6
    XEROX ⬜⬜🟩⬜⬜
    BURST ⬜⬜🟩⬜⬜
    ACRID 🟨⬜🟩🟨⬜
    VIRAL 🟩🟩🟩🟩🟩
    Final 1/2
    TROOP 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1298 😳 6 ⏱️ 0:01:27.064490

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:KOOKY n n n n n remain:6657
    ⬜⬜⬜⬜⬜ tried:FAVAS n n n n n remain:1219
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:560
    ⬜⬜🟨⬜⬜ tried:JUGUM n n m n n remain:59
    🟨⬜🟩⬜⬜ tried:GRRRL m n Y n n remain:3
    🟩🟩🟩🟩🟩 tried:DIRGE Y Y Y Y Y remain:0

    Undos used: 2

      0 words remaining
    x 0 unused letters
    = 0 total score

# cemantle.certitudes.org 🧩 #1348 🥳 759 ⏱️ 1:32:59.693858

🤔 760 attempts
📜 1 sessions
🫧 33 chat sessions
⁉️ 181 chat prompts
🤖 98 dolphin3:latest replies
🤖 8 falcon3:10b replies
🤖 75 goliath:latest replies
😱   1 🔥   3 🥵  15 😎  86 🥶 613 🧊  41

      $1 #760   ~1 simplify           100.00°C 🥳 1000‰
      $2 #731   ~5 streamline          79.92°C 😱  999‰
      $3 #263  ~93 simplified          70.44°C 🔥  998‰
      $4 #608  ~18 simplification      61.48°C 🔥  995‰
      $5 #256  ~98 streamlined         58.92°C 🔥  994‰
      $6 #316  ~72 intuitive           44.11°C 🥵  974‰
      $7 #481  ~42 complexity          43.59°C 🥵  972‰
      $8 #307  ~77 workflow            43.07°C 🥵  971‰
      $9 #574  ~31 automation          42.33°C 🥵  965‰
     $10 #564  ~32 cumbersome          42.03°C 🥵  958‰
     $11 #600  ~21 modify              41.36°C 🥵  953‰
     $21 #371  ~59 hassle              36.05°C 😎  896‰
    $107 #320      responsive          22.87°C 🥶
    $720 #702      spotless            -0.01°C 🧊

# cemantix.certitudes.org 🧩 #1381 🥳 265 ⏱️ 0:03:24.904498

🤔 266 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 51 chat prompts
🤖 50 dolphin3:latest replies
😱   1 🔥   3 🥵   6 😎  48 🥶 179 🧊  28

      $1 #266   ~1 réaliste          100.00°C 🥳 1000‰
      $2 #258   ~6 réalisme           68.33°C 😱  999‰
      $3  #92  ~53 vision             50.90°C 🔥  995‰
      $4 #137  ~42 réalité            48.16°C 🔥  992‰
      $5 #251  ~10 utopique           47.55°C 🔥  991‰
      $6  #80  ~54 ambitieux          44.77°C 🥵  984‰
      $7 #213  ~20 réalisable         43.91°C 🥵  980‰
      $8  #99  ~50 montrer            39.18°C 🥵  958‰
      $9 #188  ~27 approche           37.27°C 🥵  937‰
     $10 #203  ~24 atteignable        36.55°C 🥵  929‰
     $11 #179  ~31 narration          35.61°C 🥵  901‰
     $12 #149  ~39 envisageable       35.57°C 😎  899‰
     $60 #232      grandiose          24.43°C 🥶
    $239  #68      gestion            -0.02°C 🧊
