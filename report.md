# 2025-12-22

- 🔗 spaceword.org 🧩 2025-12-21 🏁 score 2173 ranked 5.9% 19/321 ⏱️ 1:20:51.267042
- 🔗 alfagok.diginaut.net 🧩 #415 🥳 8 ⏱️ 0:00:23.575001
- 🔗 alphaguess.com 🧩 #881 🥳 14 ⏱️ 0:00:39.405800
- 🔗 squareword.org 🧩 #1421 🥳 8 ⏱️ 0:02:48.824500
- 🔗 dictionary.com hurdle 🧩 #1451 🥳 15 ⏱️ 0:03:48.817080
- 🔗 dontwordle.com 🧩 #1308 🥳 6 ⏱️ 0:01:07.759980
- 🔗 cemantle.certitudes.org 🧩 #1358 🥳 220 ⏱️ 0:35:33.557608
- 🔗 cemantix.certitudes.org 🧩 #1391 🥳 87 ⏱️ 0:09:12.363350

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


























# spaceword.org 🧩 2025-12-21 🏁 score 2173 ranked 5.9% 19/321 ⏱️ 1:20:51.267042

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 19/321

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ J _ F _ _ M _ O W   
      _ I _ R E L I Q U E   
      _ B I O T A S _ D E   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #415 🥳 8 ⏱️ 0:00:23.575001

🤔 8 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199824 [199824] lijm      q0 ? after
    @+299746 [299746] schub     q1 ? after
    @+324322 [324322] sub       q3 ? after
    @+330507 [330507] televisie q5 ? after
    @+331902 [331902] terug     q7 ? it
    @+331902 [331902] terug     done. it
    @+333712 [333712] these     q6 ? before
    @+336924 [336924] toetsing  q4 ? before
    @+349531 [349531] vakantie  q2 ? before

# alphaguess.com 🧩 #881 🥳 14 ⏱️ 0:00:39.405800

🤔 14 attempts
📜 1 sessions

    @        [     0] aa        
    @+1      [     1] aah       
    @+2      [     2] aahed     
    @+3      [     3] aahing    
    @+98225  [ 98225] mach      q0  ? after
    @+147330 [147330] rho       q1  ? after
    @+171930 [171930] tag       q2  ? after
    @+173170 [173170] technical q6  ? after
    @+173279 [173279] teen      q9  ? after
    @+173299 [173299] teeny     q11 ? after
    @+173306 [173306] teeter    q12 ? after
    @+173312 [173312] teeth     q13 ? it
    @+173312 [173312] teeth     done. it
    @+173323 [173323] teetotal  q10 ? before
    @+173394 [173394] tele      q8  ? before
    @+173787 [173787] tempt     q7  ? before
    @+174416 [174416] test      q5  ? before
    @+176967 [176967] tom       q4  ? before
    @+182016 [182016] un        q3  ? before

# squareword.org 🧩 #1421 🥳 8 ⏱️ 0:02:48.824500

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    D E A L T
    I G L O O
    A R G O N
    L E A S E
    S T E E D

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1451 🥳 15 ⏱️ 0:03:48.817080

📜 1 sessions
💰 score: 10100

    3/6
    AISLE ⬜⬜⬜⬜⬜
    PURTY 🟨⬜⬜⬜⬜
    CHOMP 🟩🟩🟩🟩🟩
    3/6
    CHOMP ⬜⬜⬜⬜🟨
    PILES 🟨🟨🟩⬜🟨
    SPLIT 🟩🟩🟩🟩🟩
    4/6
    SPLIT ⬜⬜⬜⬜⬜
    RANDY ⬜🟨🟨⬜⬜
    BEGAN ⬜🟩🟩🟩🟩
    VEGAN 🟩🟩🟩🟩🟩
    4/6
    VEGAN ⬜🟨🟩⬜⬜
    DOGEY ⬜⬜🟩🟩⬜
    LUGER ⬜⬜🟩🟩🟩
    TIGER 🟩🟩🟩🟩🟩
    Final 1/2
    PURGE 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1308 🥳 6 ⏱️ 0:01:07.759980

📜 1 sessions
💰 score: 88

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:PZAZZ n n n n n remain:6291
    ⬜⬜⬜⬜⬜ tried:STOBS n n n n n remain:1132
    ⬜⬜⬜⬜⬜ tried:YUKKY n n n n n remain:486
    ⬜🟨⬜⬜⬜ tried:GRRRL n m n n n remain:69
    🟨🟩⬜⬜⬜ tried:RICIN m Y n n n remain:14
    ⬜🟩⬜🟩🟩 tried:FIFER n Y n Y Y remain:11

    Undos used: 1

      11 words remaining
    x 8 unused letters
    = 88 total score

# cemantle.certitudes.org 🧩 #1358 🥳 220 ⏱️ 0:35:33.557608

🤔 221 attempts
📜 1 sessions
🫧 32 chat sessions
⁉️ 75 chat prompts
🤖 38 mixtral:8x7b replies
🤖 37 smallthinker:latest replies
🥵   8 😎  33 🥶 175 🧊   4

      $1 #221   ~1 breath          100.00°C 🥳 1000‰
      $2 #152  ~19 clammy           38.39°C 🥵  989‰
      $3 #171  ~14 perspiration     35.28°C 🥵  978‰
      $4 #204   ~8 smelling         35.22°C 🥵  977‰
      $5 #115  ~28 perspire         32.68°C 🥵  964‰
      $6 #206   ~7 aroma            32.61°C 🥵  963‰
      $7 #220   ~2 scent            31.82°C 🥵  954‰
      $8  #76  ~34 hands            30.72°C 🥵  933‰
      $9 #212   ~6 stench           29.43°C 🥵  901‰
     $10 #131  ~24 exertion         28.31°C 😎  861‰
     $11 #191  ~11 odor             28.19°C 😎  856‰
     $12 #148  ~22 shivering        28.07°C 😎  852‰
     $43 #142      fatigue          21.61°C 🥶
    $218   #8      robot            -0.38°C 🧊

# cemantix.certitudes.org 🧩 #1391 🥳 87 ⏱️ 0:09:12.363350

🤔 88 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 21 chat prompts
🤖 21 mixtral:8x7b replies
🥵  4 😎 15 🥶 58 🧊 10

     $1 #88  ~1 race           100.00°C 🥳 1000‰
     $2 #55 ~12 animal          36.12°C 🥵  933‰
     $3 #74  ~4 élevage         35.41°C 🥵  922‰
     $4 #30 ~20 félidé          34.80°C 🥵  911‰
     $5 #62  ~7 pelage          34.51°C 🥵  906‰
     $6 #56 ~11 fauve           30.36°C 😎  808‰
     $7 #31 ~19 félin           30.27°C 😎  805‰
     $8 #41 ~17 ocelot          28.92°C 😎  760‰
     $9 #58 ~10 fourrure        28.83°C 😎  753‰
    $10 #43 ~16 chinchilla      26.60°C 😎  638‰
    $11 #77  ~3 bovin           26.44°C 😎  629‰
    $12 #61  ~8 mammifère       25.76°C 😎  580‰
    $21 #57     carnivore       21.29°C 🥶
    $79  #5     gouvernement    -0.22°C 🧊
