# 2025-12-14

- 🔗 spaceword.org 🧩 2025-12-13 🏁 score 2168 ranked 45.4% 139/306 ⏱️ 1:10:56.389748
- 🔗 alfagok.diginaut.net 🧩 #407 🥳 19 ⏱️ 0:00:55.134627
- 🔗 alphaguess.com 🧩 #873 🥳 11 ⏱️ 0:00:27.517578
- 🔗 squareword.org 🧩 #1413 🥳 8 ⏱️ 0:02:34.291030
- 🔗 dictionary.com hurdle 🧩 #1443 🥳 15 ⏱️ 0:02:47.306493
- 🔗 dontwordle.com 🧩 #1300 🥳 6 ⏱️ 0:01:29.179299
- 🔗 cemantle.certitudes.org 🧩 #1350 🥳 128 ⏱️ 0:01:40.048684
- 🔗 cemantix.certitudes.org 🧩 #1383 🥳 404 ⏱️ 0:08:45.381928

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


















# spaceword.org 🧩 2025-12-13 🏁 score 2168 ranked 45.4% 139/306 ⏱️ 1:10:56.389748

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 139/306

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ Q I S _ _ _ _   
      _ _ _ _ _ A _ _ _ _   
      _ _ _ F _ V _ _ _ _   
      _ _ _ A _ O _ _ _ _   
      _ _ _ L O U P _ _ _   
      _ _ _ C _ R _ _ _ _   
      _ _ _ E K E _ _ _ _   
      _ _ _ S A D E _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #407 🥳 19 ⏱️ 0:00:55.134627

🤔 19 attempts
📜 2 sessions

    @        [     0] &-teken      
    @+1      [     1] &-tekens     
    @+2      [     2] -cijferig    
    @+3      [     3] -e-mail      
    @+199839 [199839] lijm         q0  ? after
    @+223639 [223639] mol          q3  ? after
    @+229657 [229657] natuur       q5  ? after
    @+232674 [232674] niets        q6  ? after
    @+234119 [234119] noord        q7  ? after
    @+234308 [234308] noordoost    q10 ? after
    @+234406 [234406] noordzeekrab q13 ? after
    @+234427 [234427] noot         q18 ? it
    @+234427 [234427] noot         done. it
    @+234443 [234443] nop          q14 ? before
    @+234499 [234499] normaal      q9  ? before
    @+234898 [234898] nuance       q8  ? before
    @+235693 [235693] octopus      q4  ? before
    @+247752 [247752] op           q2  ? before
    @+299759 [299759] schub        q1  ? before

# alphaguess.com 🧩 #873 🥳 11 ⏱️ 0:00:27.517578

🤔 11 attempts
📜 1 sessions

    @       [    0] aa          
    @+1     [    1] aah         
    @+2     [    2] aahed       
    @+3     [    3] aahing      
    @+47387 [47387] dis         q1  ? after
    @+72806 [72806] gremmy      q2  ? after
    @+85510 [85510] ins         q3  ? after
    @+87083 [87083] intima      q6  ? after
    @+87874 [87874] iris        q7  ? after
    @+87892 [87892] iron        q10 ? it
    @+87892 [87892] iron        done. it
    @+88002 [88002] irredentist q9  ? before
    @+88130 [88130] is          q8  ? before
    @+88670 [88670] jacks       q5  ? before
    @+91855 [91855] knot        q4  ? before
    @+98225 [98225] mach        q0  ? before

# squareword.org 🧩 #1413 🥳 8 ⏱️ 0:02:34.291030

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟨 🟩 🟩 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A M B E R
    L A R V A
    G R I E F
    A G E N T
    L E F T S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1443 🥳 15 ⏱️ 0:02:47.306493

📜 1 sessions
💰 score: 10100

    3/6
    ANTES 🟨⬜⬜⬜⬜
    MORAL ⬜🟨🟩🟨⬜
    CARGO 🟩🟩🟩🟩🟩
    4/6
    CARGO ⬜🟨⬜🟨⬜
    AGILE 🟨🟨⬜🟨🟩
    GLAZE 🟩🟩🟩⬜🟩
    GLADE 🟩🟩🟩🟩🟩
    2/6
    GLADE ⬜🟩⬜⬜🟩
    SLOPE 🟩🟩🟩🟩🟩
    5/6
    SLOPE 🟩⬜⬜⬜🟩
    STARE 🟩🟩🟩⬜🟩
    STAGE 🟩🟩🟩⬜🟩
    STAKE 🟩🟩🟩⬜🟩
    STAVE 🟩🟩🟩🟩🟩
    Final 1/2
    SOBER 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1300 🥳 6 ⏱️ 0:01:29.179299

📜 1 sessions
💰 score: 42

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MAGMA n n n n n remain:5731
    ⬜⬜⬜⬜⬜ tried:JINNI n n n n n remain:2904
    ⬜⬜⬜⬜⬜ tried:SCUZZ n n n n n remain:697
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:288
    ⬜🟨⬜⬜⬜ tried:PHPHT n m n n n remain:16
    🟩🟩⬜⬜⬜ tried:HOWFF Y Y n n n remain:6

    Undos used: 5

      6 words remaining
    x 7 unused letters
    = 42 total score

# cemantle.certitudes.org 🧩 #1350 🥳 128 ⏱️ 0:01:40.048684

🤔 129 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 26 chat prompts
🤖 26 dolphin3:latest replies
😱  1 🔥  3 🥵  5 😎 13 🥶 95 🧊 11

      $1 #129   ~1 surplus           100.00°C 🥳 1000‰
      $2 #125   ~5 deficit            58.15°C 😱  999‰
      $3 #128   ~2 shortfall          56.99°C 🔥  998‰
      $4 #124   ~6 budget             47.46°C 🔥  994‰
      $5 #111  ~14 fiscal             43.25°C 🔥  992‰
      $6 #112  ~13 allocation         36.29°C 🥵  978‰
      $7 #115  ~12 expenditure        36.00°C 🥵  976‰
      $8 #127   ~3 gap                33.70°C 🥵  960‰
      $9 #122   ~8 spending           31.60°C 🥵  940‰
     $10 #126   ~4 debt               31.50°C 🥵  938‰
     $11 #104  ~19 cash               27.37°C 😎  854‰
     $12 #116  ~11 funding            27.06°C 😎  840‰
     $24  #83      easing             18.68°C 🥶
    $119  #51      oximeter           -0.08°C 🧊

# cemantix.certitudes.org 🧩 #1383 🥳 404 ⏱️ 0:08:45.381928

🤔 405 attempts
📜 1 sessions
🫧 19 chat sessions
⁉️ 126 chat prompts
🤖 126 dolphin3:latest replies
🔥   5 🥵  19 😎  47 🥶 226 🧊 107

      $1 #405   ~1 pompier             100.00°C 🥳 1000‰
      $2  #46  ~54 secours              57.35°C 🔥  997‰
      $3 #275  ~21 incendie             53.82°C 🔥  995‰
      $4  #37  ~62 ambulance            53.32°C 🔥  994‰
      $5  #47  ~53 secouriste           53.26°C 🔥  993‰
      $6 #391   ~3 caserne              52.22°C 🔥  992‰
      $7  #42  ~58 sauveteur            49.52°C 🔥  990‰
      $8  #35  ~63 ambulancier          41.16°C 🥵  979‰
      $9 #298  ~10 police               40.25°C 🥵  977‰
     $10 #139  ~43 secourisme           40.12°C 🥵  976‰
     $11 #291  ~14 feu                  39.96°C 🥵  974‰
     $26 #149  ~40 sinistre             30.94°C 😎  894‰
     $73 #255      bus                  17.47°C 🥶
    $299 #264      exposition           -0.01°C 🧊
