# 2025-12-08

- 🔗 spaceword.org 🧩 2025-12-07 🏁 score 2173 ranked 11.9% 39/327 ⏱️ 0:07:38.394778
- 🔗 alfagok.diginaut.net 🧩 #401 🥳 14 ⏱️ 0:00:50.070958
- 🔗 alphaguess.com 🧩 #867 🥳 13 ⏱️ 0:00:28.270515
- 🔗 squareword.org 🧩 #1407 🥳 7 ⏱️ 0:01:55.883465
- 🔗 dictionary.com hurdle 🧩 #1437 🥳 17 ⏱️ 0:05:14.760980
- 🔗 dontwordle.com 🧩 #1294 🥳 6 ⏱️ 0:01:17.000978
- 🔗 cemantle.certitudes.org 🧩 #1344 🥳 510 ⏱️ 0:05:20.670345
- 🔗 cemantix.certitudes.org 🧩 #1377 🥳 132 ⏱️ 0:02:33.402630

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












# spaceword.org 🧩 2025-12-07 🏁 score 2173 ranked 11.9% 39/327 ⏱️ 0:07:38.394778

📜 2 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 39/327

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ G _ I N V O K E D   
      _ O _ C _ I _ A L E   
      _ A H E A D _ T _ W   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #401 🥳 14 ⏱️ 0:00:50.070958

🤔 14 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199845 [199845] lijm      q0  ? after
    @+247763 [247763] op        q2  ? after
    @+273569 [273569] proef     q3  ? after
    @+280093 [280093] rechtst   q5  ? after
    @+280834 [280834] redding   q8  ? after
    @+280929 [280929] rede      q10 ? after
    @+280965 [280965] reden     q13 ? it
    @+280965 [280965] reden     done. it
    @+281000 [281000] reder     q12 ? before
    @+281070 [281070] reduceer  q11 ? before
    @+281212 [281212] ref       q9  ? before
    @+281605 [281605] regen     q7  ? before
    @+283187 [283187] rel       q6  ? before
    @+286640 [286640] rijs      q4  ? before
    @+299770 [299770] schub     q1  ? before

# alphaguess.com 🧩 #867 🥳 13 ⏱️ 0:00:28.270515

🤔 13 attempts
📜 1 sessions

    @        [     0] aa     
    @+1      [     1] aah    
    @+2      [     2] aahed  
    @+3      [     3] aahing 
    @+98225  [ 98225] mach   q0  ? after
    @+110130 [110130] need   q3  ? after
    @+116109 [116109] oppo   q4  ? after
    @+118743 [118743] over   q5  ? after
    @+120357 [120357] overt  q6  ? after
    @+120875 [120875] pa     q7  ? after
    @+120883 [120883] pac    q11 ? after
    @+120950 [120950] pack   q12 ? it
    @+120950 [120950] pack   done. it
    @+121017 [121017] paddle q10 ? before
    @+121179 [121179] pain   q9  ? before
    @+121489 [121489] pallid q8  ? before
    @+122110 [122110] par    q2  ? before
    @+147330 [147330] rho    q1  ? before

# squareword.org 🧩 #1407 🥳 7 ⏱️ 0:01:55.883465

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S E R I F
    P R O N E
    O R G A N
    R O U N D
    T R E E S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1437 🥳 17 ⏱️ 0:05:14.760980

📜 1 sessions
💰 score: 9900

    4/6
    LASER ⬜⬜🟨⬜🟨
    ROTIS 🟨⬜🟨🟨🟨
    SPIRT 🟨⬜🟩🟨🟩
    WRIST 🟩🟩🟩🟩🟩
    3/6
    WRIST ⬜⬜⬜⬜⬜
    GLACE ⬜⬜🟨🟨🟩
    CANOE 🟩🟩🟩🟩🟩
    5/6
    CANOE ⬜🟨⬜⬜🟩
    STARE 🟩🟩🟩⬜🟩
    STAGE 🟩🟩🟩⬜🟩
    STALE 🟩🟩🟩⬜🟩
    STAKE 🟩🟩🟩🟩🟩
    3/6
    STAKE 🟨⬜🟨⬜🟨
    NARES ⬜🟨⬜🟨🟨
    ESSAY 🟩🟩🟩🟩🟩
    Final 2/2
    JUICE ⬜⬜🟩🟩🟩
    DEICE 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1294 🥳 6 ⏱️ 0:01:17.000978

📜 1 sessions
💰 score: 10

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MIMIC n n n n n remain:6772
    ⬜⬜⬜⬜⬜ tried:SHOOS n n n n n remain:1850
    ⬜⬜⬜⬜⬜ tried:DUDDY n n n n n remain:671
    ⬜⬜⬜⬜🟨 tried:GRRRL n n n n m remain:100
    🟩🟨🟨⬜⬜ tried:BELLE Y m m n n remain:3
    🟩🟩🟩⬜⬜ tried:BLENT Y Y Y n n remain:1

    Undos used: 2

      1 words remaining
    x 10 unused letters
    = 10 total score

# cemantle.certitudes.org 🧩 #1344 🥳 510 ⏱️ 0:05:20.670345

🤔 511 attempts
📜 1 sessions
🫧 15 chat sessions
⁉️ 89 chat prompts
🤖 89 falcon3:10b replies
😱   1 🔥   3 🥵   9 😎  51 🥶 421 🧊  25

      $1 #511   ~1 firearm         100.00°C 🥳 1000‰
      $2 #509   ~3 handgun          77.44°C 😱  999‰
      $3 #482  ~16 gun              74.08°C 🔥  998‰
      $4 #470  ~20 rifle            61.40°C 🔥  995‰
      $5 #501   ~5 shotgun          59.60°C 🔥  994‰
      $6 #483  ~15 ammunition       47.67°C 🥵  984‰
      $7  #14  ~63 vehicle          36.67°C 🥵  946‰
      $8 #481  ~17 bullet           36.14°C 🥵  938‰
      $9 #493  ~10 hunting          35.90°C 🥵  935‰
     $10 #487  ~13 cartridge        35.01°C 🥵  926‰
     $11  #92  ~51 haversack        34.50°C 🥵  920‰
     $15 #408  ~27 canister         32.38°C 😎  894‰
     $66 #157      mask             21.20°C 🥶
    $487 #121      on               -0.05°C 🧊

# cemantix.certitudes.org 🧩 #1377 🥳 132 ⏱️ 0:02:33.402630

🤔 133 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 33 chat prompts
🤖 33 falcon3:10b replies
😱  1 🔥  3 🥵  5 😎 24 🥶 72 🧊 27

      $1 #133   ~1 grossesse        100.00°C 🥳 1000‰
      $2 #112  ~13 accouchement      67.91°C 😱  999‰
      $3 #102  ~15 prématurité       55.85°C 🔥  997‰
      $4  #15  ~34 bébé              55.38°C 🔥  996‰
      $5  #58  ~28 allaitement       53.76°C 🔥  990‰
      $6 #115  ~11 gynécologue       46.11°C 🥵  967‰
      $7 #129   ~3 anténatal         46.11°C 🥵  966‰
      $8 #121   ~6 obstétricien      45.13°C 🥵  961‰
      $9  #97  ~17 néonatal          42.98°C 🥵  946‰
     $10 #124   ~5 périnatal         42.65°C 🥵  943‰
     $11  #99  ~16 néonatalogie      37.89°C 😎  895‰
     $12  #85  ~20 prématuré         37.48°C 😎  891‰
     $35  #70      sein              21.84°C 🥶
    $107  #21      cœur              -0.12°C 🧊
