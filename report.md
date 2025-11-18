# 2025-11-19

- 🔗 spaceword.org 🧩 2025-11-18 🏁 score 2173 ranked 11.3% 38/337 ⏱️ 0:13:52.229756
- 🔗 alfagok.diginaut.net 🧩 #382 🥳 17 ⏱️ 0:00:46.023374
- 🔗 alphaguess.com 🧩 #848 🥳 12 ⏱️ 0:00:28.737293
- 🔗 squareword.org 🧩 #1388 🥳 8 ⏱️ 0:02:24.305184
- 🔗 dictionary.com hurdle 🧩 #1418 😦 16 ⏱️ 0:02:52.279628
- 🔗 dontwordle.com 🧩 #1275 🥳 6 ⏱️ 0:01:25.876029
- 🔗 cemantle.certitudes.org 🧩 #1325 🥳 441 ⏱️ 0:10:20.351182
- 🔗 cemantix.certitudes.org 🧩 #1358 🥳 435 ⏱️ 0:10:19.823107

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















# spaceword.org 🧩 2025-11-18 🏁 score 2173 ranked 11.3% 38/337 ⏱️ 0:13:52.229756

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 38/337

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ C O G _ _ _   
      _ _ _ _ _ _ A _ _ _   
      _ _ _ _ M A N _ _ _   
      _ _ _ _ E _ E _ _ _   
      _ _ _ _ T A V _ _ _   
      _ _ _ _ A R S _ _ _   
      _ _ _ _ Z _ _ _ _ _   
      _ _ _ _ O A T _ _ _   
      _ _ _ _ A X _ _ _ _   


# alfagok.diginaut.net 🧩 #382 🥳 17 ⏱️ 0:00:46.023374

🤔 17 attempts
📜 1 sessions

    @        [     0] &-teken        
    @+1      [     1] &-tekens       
    @+2      [     2] -cijferig      
    @+3      [     3] -e-mail        
    @+199763 [199763] lijn           q0  ? after
    @+299646 [299646] schudde        q1  ? after
    @+349377 [349377] vak            q2  ? after
    @+355127 [355127] verg           q5  ? after
    @+356766 [356766] verken         q7  ? after
    @+357598 [357598] verkreuk       q8  ? after
    @+357786 [357786] verlating      q10 ? after
    @+357789 [357789] verlazen       q15 ? after
    @+357791 [357791] verleden       q16 ? it
    @+357791 [357791] verleden       done. it
    @+357792 [357792] verlee         q14 ? before
    @+357806 [357806] verleg         q13 ? before
    @+357826 [357826] verleide       q12 ? before
    @+357871 [357871] verleng        q11 ? before
    @+357979 [357979] verlies        q9  ? before
    @+358433 [358433] vermenigvuldig q6  ? before
    @+361746 [361746] vervijfvoudig  q4  ? before
    @+374120 [374120] vrij           q3  ? before

# alphaguess.com 🧩 #848 🥳 12 ⏱️ 0:00:28.737293

🤔 12 attempts
📜 1 sessions

    @       [    0] aa          
    @+1     [    1] aah         
    @+2     [    2] aahed       
    @+3     [    3] aahing      
    @+47387 [47387] dis         q1  ? after
    @+60090 [60090] face        q4  ? after
    @+66446 [66446] french      q5  ? after
    @+69627 [69627] geosyncline q6  ? after
    @+71218 [71218] gnomon      q7  ? after
    @+72013 [72013] gracious    q8  ? after
    @+72404 [72404] grass       q9  ? after
    @+72603 [72603] grazing     q10 ? after
    @+72674 [72674] green       q11 ? it
    @+72674 [72674] green       done. it
    @+72807 [72807] gremolata   q2  ? after
    @+72807 [72807] gremolata   q3  ? before
    @+98226 [98226] mach        q0  ? before

# squareword.org 🧩 #1388 🥳 8 ⏱️ 0:02:24.305184

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B L A D E
    A L L O W
    R A I S E
    E M B E R
    R A I D S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1418 😦 16 ⏱️ 0:02:52.279628

📜 1 sessions
💰 score: 5060

    4/6
    RATES 🟨⬜⬜⬜⬜
    PRION ⬜🟨⬜🟨⬜
    WORLD ⬜🟩🟨⬜🟩
    GOURD 🟩🟩🟩🟩🟩
    4/6
    GOURD ⬜⬜⬜⬜⬜
    SCALE 🟨⬜🟨⬜🟩
    HASTE ⬜🟩🟩🟩🟩
    WASTE 🟩🟩🟩🟩🟩
    3/6
    WASTE ⬜⬜🟩⬜⬜
    BISON 🟩⬜🟩🟨⬜
    BOSSY 🟩🟩🟩🟩🟩
    3/6
    BOSSY ⬜⬜🟨⬜⬜
    STEAM 🟩🟨🟨🟨⬜
    SLATE 🟩🟩🟩🟩🟩
    Final 2/2
    CRIME ⬜🟨⬜⬜🟩
    NERVE ⬜🟩🟩🟩🟩
    FAIL: VERVE

# dontwordle.com 🧩 #1275 🥳 6 ⏱️ 0:01:25.876029

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:BABKA n n n n n remain:5942
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:2470
    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:1211
    ⬜⬜⬜⬜⬜ tried:POOPS n n n n n remain:155
    ⬜⬜⬜⬜⬜ tried:YUMMY n n n n n remain:36
    🟨⬜⬜🟩⬜ tried:ENDED m n n Y n remain:1

    Undos used: 3

      1 words remaining
    x 8 unused letters
    = 8 total score

# cemantle.certitudes.org 🧩 #1325 🥳 441 ⏱️ 0:10:20.351182

🤔 442 attempts
📜 1 sessions
🫧 38 chat sessions
⁉️ 251 chat prompts
🤖 251 gemma3:latest replies
🔥   4 🥵   7 😎  47 🥶 363 🧊  20

      $1 #442   ~1 poetry              100.00°C 🥳 1000‰
      $2 #386  ~13 literary             63.84°C 🔥  997‰
      $3 #334  ~35 poetic               63.09°C 🔥  995‰
      $4 #375  ~16 prose                62.34°C 🔥  994‰
      $5 #367  ~22 sonnet               61.30°C 🔥  993‰
      $6 #427   ~5 anthology            57.02°C 🥵  989‰
      $7 #333  ~36 lyrical              54.09°C 🥵  987‰
      $8 #364  ~24 verse                51.76°C 🥵  984‰
      $9 #436   ~4 elegy                45.74°C 🥵  946‰
     $10 #362  ~25 lyric                45.37°C 🥵  940‰
     $11  #25  ~57 meditation           44.80°C 🥵  929‰
     $13 #406   ~7 manuscript           42.43°C 😎  886‰
     $60 #103      divinity             31.28°C 🥶
    $423   #6      rust                 -0.02°C 🧊

# cemantix.certitudes.org 🧩 #1358 🥳 435 ⏱️ 0:10:19.823107

🤔 436 attempts
📜 1 sessions
🫧 32 chat sessions
⁉️ 213 chat prompts
🤖 213 gemma3:latest replies
🔥   2 🥵   4 😎  29 🥶 236 🧊 164

      $1 #436   ~1 tabac             100.00°C 🥳 1000‰
      $2 #430   ~4 fumer              59.66°C 🔥  997‰
      $3 #325  ~13 alcool             52.60°C 🔥  995‰
      $4 #432   ~3 fumoir             36.18°C 🥵  972‰
      $5 #425   ~5 fumée              29.69°C 🥵  934‰
      $6 #170  ~21 saccharine         28.53°C 🥵  918‰
      $7  #58  ~34 boisson            28.44°C 🥵  917‰
      $8 #113  ~28 caféine            26.05°C 😎  889‰
      $9 #341  ~12 houblon            24.61°C 😎  856‰
     $10 #177  ~20 sucrerie           23.77°C 😎  838‰
     $11  #80  ~31 café               23.58°C 😎  833‰
     $12 #153  ~23 sucre              23.19°C 😎  829‰
     $37 #154      dextrose           14.47°C 🥶
    $273 #327      vinification       -0.06°C 🧊
