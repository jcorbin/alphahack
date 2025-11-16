# 2025-11-17

- 🔗 spaceword.org 🧩 2025-11-16 🏁 score 2173 ranked 4.3% 15/350 ⏱️ 0:26:56.828484
- 🔗 alfagok.diginaut.net 🧩 #380 🥳 16 ⏱️ 0:00:46.087257
- 🔗 alphaguess.com 🧩 #846 🥳 16 ⏱️ 0:00:36.268978
- 🔗 squareword.org 🧩 #1386 🥳 9 ⏱️ 0:03:08.698476
- 🔗 dictionary.com hurdle 🧩 #1416 🥳 16 ⏱️ 0:02:57.869147
- 🔗 dontwordle.com 🧩 #1273 🤷 6 ⏱️ 0:02:02.316299
- 🔗 cemantle.certitudes.org 🧩 #1323 🥳 312 ⏱️ 0:01:53.846469
- 🔗 cemantix.certitudes.org 🧩 #1356 🥳 838 ⏱️ 0:31:14.342246

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













# spaceword.org 🧩 2025-11-16 🏁 score 2173 ranked 4.3% 15/350 ⏱️ 0:26:56.828484

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 15/350

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ R E B _ _ _   
      _ _ _ _ _ _ U _ _ _   
      _ _ _ _ T A N _ _ _   
      _ _ _ _ A U K _ _ _   
      _ _ _ _ _ X I _ _ _   
      _ _ _ _ L E E _ _ _   
      _ _ _ _ U T _ _ _ _   
      _ _ _ _ V I G _ _ _   
      _ _ _ _ _ C _ _ _ _   


# alfagok.diginaut.net 🧩 #380 🥳 16 ⏱️ 0:00:46.087257

🤔 16 attempts
📜 1 sessions

    @        [     0] &-teken        
    @+1      [     1] &-tekens       
    @+2      [     2] -cijferig      
    @+3      [     3] -e-mail        
    @+199763 [199763] lijn           q0  ? after
    @+299646 [299646] schudde        q1  ? after
    @+311908 [311908] spies          q4  ? after
    @+314765 [314765] staats         q6  ? after
    @+315014 [315014] staatsolie     q9  ? after
    @+315138 [315138] staatswinkels  q10 ? after
    @+315196 [315196] stad           q11 ? after
    @+315221 [315221] stadhuis       q12 ? after
    @+315241 [315241] stadion        q13 ? after
    @+315251 [315251] stadionterrein q14 ? after
    @+315256 [315256] stadium        q15 ? it
    @+315256 [315256] stadium        done. it
    @+315261 [315261] stads          q8  ? before
    @+316253 [316253] standaard      q7  ? before
    @+317975 [317975] stem           q5  ? before
    @+324177 [324177] sub            q3  ? before
    @+349377 [349377] vak            q2  ? before

# alphaguess.com 🧩 #846 🥳 16 ⏱️ 0:00:36.268978

🤔 16 attempts
📜 1 sessions

    @        [     0] aa          
    @+1      [     1] aah         
    @+2      [     2] aahed       
    @+3      [     3] aahing      
    @+98226  [ 98226] mach        q0  ? after
    @+147331 [147331] rho         q1  ? after
    @+159613 [159613] slug        q3  ? after
    @+165767 [165767] stint       q4  ? after
    @+168817 [168817] sulfur      q5  ? after
    @+170371 [170371] sustain     q6  ? after
    @+171139 [171139] symbol      q7  ? after
    @+171522 [171522] synth       q8  ? after
    @+171653 [171653] tab         q9  ? after
    @+171787 [171787] tach        q10 ? after
    @+171831 [171831] tack        q11 ? after
    @+171852 [171852] tackinesses q13 ? after
    @+171862 [171862] tacks       q14 ? after
    @+171866 [171866] taco        q15 ? it
    @+171866 [171866] taco        done. it
    @+171872 [171872] tact        q12 ? before
    @+171931 [171931] tag         q2  ? before

# squareword.org 🧩 #1386 🥳 9 ⏱️ 0:03:08.698476

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟨
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S H A R D
    T O N E R
    R U N N Y
    U S U A L
    T E L L Y

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1416 🥳 16 ⏱️ 0:02:57.869147

📜 1 sessions
💰 score: 10000

    5/6
    SCARE ⬜⬜⬜⬜🟩
    BILGE ⬜🟨⬜⬜🟩
    TWINE ⬜⬜🟨🟨🟩
    NUDIE 🟨⬜🟩🟩🟩
    INDIE 🟩🟩🟩🟩🟩
    3/6
    INDIE ⬜⬜⬜⬜⬜
    COURT 🟨⬜⬜⬜⬜
    SHACK 🟩🟩🟩🟩🟩
    4/6
    SHACK ⬜⬜⬜⬜⬜
    MINOR ⬜🟩⬜⬜🟨
    TIRED ⬜🟩🟨⬜🟩
    RIGID 🟩🟩🟩🟩🟩
    3/6
    RIGID ⬜⬜🟨⬜⬜
    GALES 🟩⬜⬜🟩🟩
    GENES 🟩🟩🟩🟩🟩
    Final 1/2
    KARAT 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1273 🤷 6 ⏱️ 0:02:02.316299

📜 1 sessions
💰 score: 0

ELIMINATED
> Well technically I didn't Wordle!

    ⬜⬜⬜⬜⬜ tried:LAHAL n n n n n remain:4961
    ⬜⬜⬜⬜⬜ tried:ZIZIT n n n n n remain:2336
    ⬜⬜⬜⬜⬜ tried:DRUNK n n n n n remain:312
    ⬜🟨⬜⬜⬜ tried:FEMME n m n n n remain:43
    🟨🟨🟩⬜⬜ tried:SPECS m m Y n n remain:1
    ⬛⬛⬛⬛⬛ tried:????? remain:0

    Undos used: 5

      0 words remaining
    x 0 unused letters
    = 0 total score

# cemantle.certitudes.org 🧩 #1323 🥳 312 ⏱️ 0:01:53.846469

🤔 313 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 72 chat prompts
🤖 72 gemma3:latest replies
🔥   1 🥵   6 😎  16 🥶 236 🧊  53

      $1 #313   ~1 charter         100.00°C 🥳 1000‰
      $2 #300   ~9 constitution     38.14°C 🔥  996‰
      $3 #312   ~2 amendment        30.84°C 🥵  970‰
      $4 #203  ~19 covenant         28.48°C 🥵  950‰
      $5 #309   ~5 statute          28.17°C 🥵  947‰
      $6 #307   ~6 oversight        27.61°C 🥵  934‰
      $7 #271  ~14 governance       26.42°C 🥵  912‰
      $8 #305   ~7 mandate          25.98°C 🥵  904‰
      $9 #120  ~24 renewal          25.74°C 😎  897‰
     $10 #201  ~20 agreement        25.14°C 😎  871‰
     $11 #299  ~10 authority        24.29°C 😎  832‰
     $12 #200  ~21 accord           23.03°C 😎  745‰
     $26 #209      foundation       17.58°C 🥶
    $261 #283      verity           -0.13°C 🧊

# cemantix.certitudes.org 🧩 #1356 🥳 838 ⏱️ 0:31:14.342246

🤔 839 attempts
📜 4 sessions
🫧 97 chat sessions
⁉️ 598 chat prompts
🤖 598 gemma3:latest replies
😱   1 🥵   1 😎  68 🥶 620 🧊 148

      $1 #839   ~1 romain          100.00°C 🥳 1000‰
      $2 #214  ~54 antique          59.33°C 😱  999‰
      $3 #204  ~57 antiquité        49.37°C 🥵  974‰
      $4 #820   ~2 procurateur      40.23°C 😎  883‰
      $5 #645  ~12 légat            39.54°C 😎  863‰
      $6 #576  ~18 épigraphique     39.20°C 😎  859‰
      $7 #647  ~11 titulature       39.07°C 😎  853‰
      $8 #479  ~33 épigraphie       38.74°C 😎  846‰
      $9  #56  ~70 vestige          38.42°C 😎  839‰
     $10 #180  ~59 empire           38.24°C 😎  836‰
     $11 #571  ~20 épigraphiste     36.99°C 😎  806‰
     $12 #812   ~3 impérial         36.69°C 😎  801‰
     $72 #535      noble            24.08°C 🥶
    $692 #201      société          -0.02°C 🧊
