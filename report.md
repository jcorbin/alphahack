# 2025-11-04

- 🔗 spaceword.org 🧩 2025-11-03 🏁 score 2173 ranked 8.0% 31/389 ⏱️ 0:26:44.989244
- 🔗 alfagok.diginaut.net 🧩 #367 🥳 10 ⏱️ 0:00:32.886651
- 🔗 alphaguess.com 🧩 #833 🥳 18 ⏱️ 0:00:38.376961
- 🔗 squareword.org 🧩 #1373 🥳 10 ⏱️ 0:03:00.139536
- 🔗 dictionary.com hurdle 🧩 #1403 🥳 15 ⏱️ 0:02:51.001779
- 🔗 dontwordle.com 🧩 #1260 🥳 6 ⏱️ 0:01:56.418638
- 🔗 cemantle.certitudes.org 🧩 #1310 🥳 372 ⏱️ 0:11:48.242856
- 🔗 cemantix.certitudes.org 🧩 #1343 🥳 112 ⏱️ 0:04:21.520931

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









# spaceword.org 🧩 2025-11-03 🏁 score 2173 ranked 8.0% 31/389 ⏱️ 0:26:44.989244

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 31/389

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ K E N _ _ _   
      _ _ _ _ A X _ _ _ _   
      _ _ _ _ S U P _ _ _   
      _ _ _ _ _ D O _ _ _   
      _ _ _ _ _ A G _ _ _   
      _ _ _ _ _ T O _ _ _   
      _ _ _ _ Y E N _ _ _   
      _ _ _ _ _ _ I _ _ _   
      _ _ _ _ Z O A _ _ _   


# alfagok.diginaut.net 🧩 #367 🥳 10 ⏱️ 0:00:32.886651

🤔 10 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199827 [199827] lijm      q0  ? after
    @+223614 [223614] mol       q3  ? after
    @+226059 [226059] mu        q6  ? after
    @+226500 [226500] munt      q9  ? it
    @+226500 [226500] munt      done. it
    @+226942 [226942] muur      q8  ? before
    @+227832 [227832] naakt     q7  ? before
    @+229633 [229633] natuur    q5  ? before
    @+235669 [235669] octrooi   q4  ? before
    @+247725 [247725] op        q2  ? before
    @+299729 [299729] schub     q1  ? before

# alphaguess.com 🧩 #833 🥳 18 ⏱️ 0:00:38.376961

🤔 18 attempts
📜 1 sessions

    @        [     0] aa           
    @+1      [     1] aah          
    @+2      [     2] aahed        
    @+3      [     3] aahing       
    @+98226  [ 98226] mach         q0  ? after
    @+110131 [110131] need         q3  ? after
    @+111495 [111495] no           q5  ? after
    @+112545 [112545] noni         q7  ? after
    @+113163 [113163] nonsocial    q8  ? after
    @+113472 [113472] norm         q9  ? after
    @+113473 [113473] normal       q17 ? it
    @+113473 [113473] normal       done. it
    @+113474 [113474] normalcies   q16 ? before
    @+113475 [113475] normalcy     q15 ? before
    @+113478 [113478] normalise    q14 ? before
    @+113484 [113484] normalizable q13 ? before
    @+113496 [113496] normative    q12 ? before
    @+113518 [113518] north        q11 ? before
    @+113563 [113563] nos          q10 ? before
    @+113787 [113787] novel        q6  ? before
    @+116110 [116110] oppo         q4  ? before
    @+122111 [122111] par          q2  ? before
    @+147331 [147331] rho          q1  ? before

# squareword.org 🧩 #1373 🥳 10 ⏱️ 0:03:00.139536

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟨
    🟨 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S W A T H
    P A D R E
    I N D I E
    K N E L L
    E A R L S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1403 🥳 15 ⏱️ 0:02:51.001779

📜 1 sessions
💰 score: 10100

    3/6
    SLATE 🟩🟨🟨⬜⬜
    SALON 🟩🟨🟨🟨⬜
    SHOAL 🟩🟩🟩🟩🟩
    3/6
    SHOAL ⬜🟨⬜⬜🟨
    BLECH ⬜🟨⬜🟩🟩
    MULCH 🟩🟩🟩🟩🟩
    4/6
    MULCH ⬜⬜⬜⬜⬜
    AROSE 🟨🟨⬜🟨🟨
    WEARS 🟨🟨🟨🟨🟨
    SWEAR 🟩🟩🟩🟩🟩
    4/6
    SWEAR ⬜⬜⬜🟨🟨
    TRAIN ⬜🟨🟩⬜⬜
    HOARY ⬜🟨🟩🟩🟩
    OVARY 🟩🟩🟩🟩🟩
    Final 1/2
    VINYL 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1260 🥳 6 ⏱️ 0:01:56.418638

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:7266
    ⬜⬜⬜⬜⬜ tried:WOODY n n n n n remain:2727
    ⬜⬜⬜⬜⬜ tried:CURCH n n n n n remain:784
    ⬜🟩⬜⬜⬜ tried:FEEZE n Y n n n remain:107
    ⬜🟩🟨⬜🟨 tried:JELLS n Y m n m remain:4
    🟨🟩⬜🟨🟨 tried:SEPAL m Y n m m remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# cemantle.certitudes.org 🧩 #1310 🥳 372 ⏱️ 0:11:48.242856

🤔 373 attempts
📜 1 sessions
🫧 16 chat sessions
⁉️ 100 chat prompts
🤖 27 llama3.2:latest replies
🤖 73 gemma3:latest replies
🔥   3 🥵  21 😎  76 🥶 264 🧊   8

      $1 #373   ~1 coordination     100.00°C 🥳 1000‰
      $2  #25  ~93 coordinated       55.10°C 🔥  997‰
      $3 #366   ~4 collaboration     47.42°C 🔥  994‰
      $4  #47  ~80 oversight         44.45°C 🔥  991‰
      $5  #96  ~68 synergy           42.71°C 🥵  989‰
      $6 #317  ~18 facilitation      42.58°C 🥵  988‰
      $7  #56  ~76 synchronization   40.05°C 🥵  979‰
      $8 #371   ~2 congruence        38.77°C 🥵  972‰
      $9  #39  ~82 integration       38.73°C 🥵  971‰
     $10  #28  ~90 collaborative     38.45°C 🥵  969‰
     $11 #215  ~39 interrelation     38.35°C 🥵  966‰
     $26  #58  ~74 concerted         32.12°C 😎  898‰
    $101 #250      synaptic          21.50°C 🥶
    $366 #256      adjusted          -0.07°C 🧊

# cemantix.certitudes.org 🧩 #1343 🥳 112 ⏱️ 0:04:21.520931

🤔 113 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 22 chat prompts
🤖 22 gemma3:latest replies
🥵  3 😎 19 🥶 69 🧊 21

      $1 #113   ~1 interface        100.00°C 🥳 1000‰
      $2  #77   ~9 donnée            45.74°C 🥵  967‰
      $3  #70  ~14 paramètre         45.02°C 🥵  963‰
      $4  #60  ~21 système           43.07°C 🥵  945‰
      $5  #80   ~7 fonction          40.09°C 😎  897‰
      $6  #68  ~16 modélisation      39.66°C 😎  890‰
      $7  #27  ~23 flux              38.81°C 😎  875‰
      $8  #72  ~13 réseau            38.60°C 😎  869‰
      $9  #73  ~12 simulation        37.31°C 😎  840‰
     $10  #66  ~17 capteur           36.73°C 😎  826‰
     $11  #69  ~15 optimisation      36.32°C 😎  807‰
     $12 #105   ~3 modèle            35.20°C 😎  772‰
     $24  #36      soluté            26.40°C 🥶
     $93  #10      énigme            -1.46°C 🧊
