# 2025-12-01

- 🔗 spaceword.org 🧩 2025-11-30 🏁 score 2173 ranked 9.2% 31/338 ⏱️ 1:23:21.522796
- 🔗 alfagok.diginaut.net 🧩 #394 🥳 9 ⏱️ 0:00:31.463392
- 🔗 alphaguess.com 🧩 #860 🥳 12 ⏱️ 0:00:29.511119
- 🔗 squareword.org 🧩 #1400 🥳 8 ⏱️ 0:03:22.184875
- 🔗 dictionary.com hurdle 🧩 #1430 🥳 16 ⏱️ 0:03:28.758070
- 🔗 dontwordle.com 🧩 #1287 😳 6 ⏱️ 0:01:12.247637
- 🔗 cemantle.certitudes.org 🧩 #1337 🥳 71 ⏱️ 0:00:38.469787
- 🔗 cemantix.certitudes.org 🧩 #1370 🥳 314 ⏱️ 0:28:29.338635

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





# spaceword.org 🧩 2025-11-30 🏁 score 2173 ranked 9.2% 31/338 ⏱️ 1:23:21.522796

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 31/338

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ Q _ _ _ _   
      _ _ _ _ _ U _ _ _ _   
      _ _ _ _ P A W _ _ _   
      _ _ _ _ E D H _ _ _   
      _ _ _ _ A _ A _ _ _   
      _ _ _ _ C O R _ _ _   
      _ _ _ _ O _ V _ _ _   
      _ _ _ _ A N E _ _ _   
      _ _ _ _ T A S _ _ _   


# alfagok.diginaut.net 🧩 #394 🥳 9 ⏱️ 0:00:31.463392

🤔 9 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+49909  [ 49909] bol       q2 ? after
    @+74757  [ 74757] dc        q3 ? after
    @+80983  [ 80983] dijkt     q5 ? after
    @+83774  [ 83774] don       q6 ? after
    @+84106  [ 84106] dood      q8 ? it
    @+84106  [ 84106] dood      done. it
    @+84673  [ 84673] door      q7 ? before
    @+87214  [ 87214] draag     q4 ? before
    @+99838  [ 99838] examen    q1 ? before
    @+199701 [199701] lijm      q0 ? before

# alphaguess.com 🧩 #860 🥳 12 ⏱️ 0:00:29.511119

🤔 12 attempts
📜 1 sessions

    @        [     0] aa          
    @+1      [     1] aah         
    @+2      [     2] aahed       
    @+3      [     3] aahing      
    @+98225  [ 98225] mach        q0  ? after
    @+122110 [122110] par         q2  ? after
    @+134641 [134641] prog        q3  ? after
    @+140527 [140527] rec         q4  ? after
    @+143791 [143791] rem         q5  ? after
    @+145204 [145204] res         q6  ? after
    @+145734 [145734] respade     q8  ? after
    @+145854 [145854] rest        q9  ? after
    @+145950 [145950] restoration q11 ? it
    @+145950 [145950] restoration done. it
    @+146049 [146049] result      q10 ? before
    @+146263 [146263] retest      q7  ? before
    @+147330 [147330] rho         q1  ? before

# squareword.org 🧩 #1400 🥳 8 ⏱️ 0:03:22.184875

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟩
    🟨 🟩 🟩 🟨 🟨
    🟨 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C R U S H
    H E N C E
    A F I R E
    F E T E D
    F R E E S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1430 🥳 16 ⏱️ 0:03:28.758070

📜 1 sessions
💰 score: 10000

    4/6
    LEAST ⬜🟨🟨⬜⬜
    PADRE ⬜🟨🟨⬜🟨
    ACNED 🟨⬜🟨🟨🟩
    KNEAD 🟩🟩🟩🟩🟩
    5/6
    KNEAD ⬜🟨🟨⬜⬜
    STONE ⬜⬜🟨🟨🟨
    RECON ⬜🟩⬜🟩🟩
    LEMON ⬜🟩⬜🟩🟩
    XENON 🟩🟩🟩🟩🟩
    4/6
    XENON ⬜⬜🟨⬜⬜
    USING ⬜⬜⬜🟩🟨
    GRAND 🟩⬜🟩🟩🟩
    GLAND 🟩🟩🟩🟩🟩
    2/6
    GLAND ⬜⬜🟩🟨⬜
    TRAIN 🟩🟩🟩🟩🟩
    Final 1/2
    GUARD 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1287 😳 6 ⏱️ 0:01:12.247637

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:BABKA n n n n n remain:5942
    ⬜⬜⬜⬜⬜ tried:MOSSO n n n n n remain:1467
    ⬜⬜⬜⬜⬜ tried:JIFFY n n n n n remain:391
    ⬜⬜⬜⬜⬜ tried:CUTCH n n n n n remain:86
    ⬜🟩⬜⬜⬜ tried:GRRRL n Y n n n remain:6
    🟩🟩🟩🟩🟩 tried:PREEN Y Y Y Y Y remain:0

    Undos used: 1

      0 words remaining
    x 0 unused letters
    = 0 total score

# cemantle.certitudes.org 🧩 #1337 🥳 71 ⏱️ 0:00:38.469787

🤔 72 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 12 chat prompts
🤖 12 falcon3:10b replies
🔥  1 🥵  4 😎 13 🥶 51 🧊  2

     $1 #72  ~1 menu          100.00°C 🥳 1000‰
     $2 #65  ~3 cuisine        55.90°C 🔥  998‰
     $3 #41  ~9 gourmet        45.94°C 🥵  965‰
     $4 #26 ~17 chef           45.80°C 🥵  964‰
     $5 #66  ~2 dining         44.96°C 🥵  956‰
     $6 #39 ~11 decor          41.48°C 🥵  905‰
     $7 #45  ~8 kitchen        41.20°C 😎  896‰
     $8 #52  ~5 recipe         41.16°C 😎  893‰
     $9 #34 ~15 cookbook       38.42°C 😎  827‰
    $10 #37 ~12 culinary       36.46°C 😎  754‰
    $11 #40 ~10 food           33.70°C 😎  623‰
    $12  #9 ~19 table          33.09°C 😎  578‰
    $20 #57     server         25.25°C 🥶
    $71  #3     dream          -1.01°C 🧊

# cemantix.certitudes.org 🧩 #1370 🥳 314 ⏱️ 0:28:29.338635

🤔 315 attempts
📜 1 sessions
🫧 27 chat sessions
⁉️ 162 chat prompts
🤖 46 mixtral:8x22b replies
🤖 62 glm4:latest replies
🤖 54 falcon3:10b replies
🔥   2 🥵  11 😎  66 🥶 219 🧊  16

      $1 #315   ~1 singulier            100.00°C 🥳 1000‰
      $2 #231  ~30 intime                54.84°C 🔥  996‰
      $3 #300   ~5 étrangeté             54.10°C 🔥  994‰
      $4 #261  ~21 imaginaire            51.32°C 🥵  989‰
      $5 #284  ~11 irréductible          49.54°C 🥵  983‰
      $6  #81  ~65 indicible             48.98°C 🥵  980‰
      $7 #253  ~23 énigmatique           48.84°C 🥵  979‰
      $8 #223  ~33 intimement            48.58°C 🥵  976‰
      $9  #64  ~71 immanent              47.43°C 🥵  958‰
     $10 #310   ~2 subjectif             46.84°C 🥵  947‰
     $11 #267  ~19 irreprésentable       46.60°C 🥵  943‰
     $15 #281  ~12 aporétique            42.93°C 😎  861‰
     $81 #204      obscur                32.87°C 🥶
    $300   #7      soleil                -0.66°C 🧊
