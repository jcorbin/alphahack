# 2025-11-27

- 🔗 spaceword.org 🧩 2025-11-26 🏁 score 2173 ranked 10.7% 38/354 ⏱️ 0:16:27.125467
- 🔗 alfagok.diginaut.net 🧩 #390 🥳 19 ⏱️ 0:00:56.398852
- 🔗 alphaguess.com 🧩 #856 🥳 15 ⏱️ 0:00:52.757013
- 🔗 squareword.org 🧩 #1396 🥳 7 ⏱️ 0:02:36.456120
- 🔗 dictionary.com hurdle 🧩 #1426 🥳 18 ⏱️ 0:03:50.287564
- 🔗 dontwordle.com 🧩 #1283 🥳 6 ⏱️ 0:01:50.669556
- 🔗 cemantle.certitudes.org 🧩 #1333 🥳 585 ⏱️ 0:43:25.890927
- 🔗 cemantix.certitudes.org 🧩 #1366 🥳 269 ⏱️ 0:25:43.252306

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

# spaceword.org 🧩 2025-11-26 🏁 score 2173 ranked 10.7% 38/354 ⏱️ 0:16:27.125467

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 38/354

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ L O O _ G I N _ V   
      _ _ _ A P A R E J O   
      _ M U R I N E _ _ W   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #390 🥳 19 ⏱️ 0:00:56.398852

🤔 19 attempts
📜 1 sessions

    @        [     0] &-teken         
    @+1      [     1] &-tekens        
    @+2      [     2] -cijferig       
    @+3      [     3] -e-mail         
    @+199762 [199762] lijn            q0  ? after
    @+199762 [199762] lijn            q1  ? after
    @+201914 [201914] loo             q7  ? after
    @+203392 [203392] lucht           q8  ? after
    @+204499 [204499] lul             q9  ? after
    @+205057 [205057] ma              q10 ? after
    @+205180 [205180] maai            q12 ? after
    @+205235 [205235] maal            q13 ? after
    @+205264 [205264] maaltijd        q14 ? after
    @+205299 [205299] maaltijdviering q15 ? after
    @+205307 [205307] maan            q16 ? after
    @+205320 [205320] maanbrieven     q17 ? after
    @+205325 [205325] maand           q18 ? it
    @+205325 [205325] maand           done. it
    @+205333 [205333] maandag         q11 ? before
    @+205614 [205614] maas            q6  ? before
    @+211608 [211608] me              q5  ? before
    @+223475 [223475] mol             q4  ? before
    @+247584 [247584] op              q3  ? before
    @+299630 [299630] schud           q2  ? before

# alphaguess.com 🧩 #856 🥳 15 ⏱️ 0:00:52.757013

🤔 15 attempts
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
    @+171285 [171285] sync        q9  ? after
    @+171344 [171344] syncopation q11 ? after
    @+171370 [171370] syndactyl   q12 ? after
    @+171385 [171385] syndic      q13 ? after
    @+171391 [171391] syndicate   q14 ? it
    @+171391 [171391] syndicate   done. it
    @+171403 [171403] syne        q10 ? before
    @+171522 [171522] synth       q8  ? before
    @+171931 [171931] tag         q2  ? before

# squareword.org 🧩 #1396 🥳 7 ⏱️ 0:02:36.456120

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S H A M E
    T O N A L
    A T O N E
    M E D I C
    P L E A T

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1426 🥳 18 ⏱️ 0:03:50.287564

📜 1 sessions
💰 score: 9800

    3/6
    DARES ⬜⬜🟨⬜⬜
    RUTIN 🟨⬜⬜🟩⬜
    CHOIR 🟩🟩🟩🟩🟩
    4/6
    CHOIR ⬜⬜⬜⬜⬜
    UNLET ⬜🟩⬜🟨⬜
    SNEAK 🟩🟩🟨🟨🟨
    SNAKE 🟩🟩🟩🟩🟩
    5/6
    SNAKE ⬜⬜🟨🟨🟨
    BAKER ⬜🟩🟩🟩🟩
    TAKER ⬜🟩🟩🟩🟩
    FAKER ⬜🟩🟩🟩🟩
    MAKER 🟩🟩🟩🟩🟩
    4/6
    MAKER ⬜🟨⬜⬜⬜
    ULANS ⬜⬜🟩⬜⬜
    CHAPT 🟩🟩🟩⬜⬜
    CHAFF 🟩🟩🟩🟩🟩
    Final 2/2
    TOLAN 🟩🟩🟨🟩🟨
    TONAL 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1283 🥳 6 ⏱️ 0:01:50.669556

📜 2 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:WALLA n n n n n remain:5351
    ⬜⬜⬜⬜⬜ tried:JUJUS n n n n n remain:1931
    ⬜⬜⬜⬜⬜ tried:CHOOK n n n n n remain:602
    ⬜⬜⬜⬜🟩 tried:PYGMY n n n n Y remain:78
    ⬜🟨⬜⬜🟩 tried:BIFFY n m n n Y remain:2
    ⬜🟩🟩⬜🟩 tried:VEINY n Y Y n Y remain:1

    Undos used: 4

      1 words remaining
    x 6 unused letters
    = 6 total score

# cemantle.certitudes.org 🧩 #1333 🥳 585 ⏱️ 0:43:25.890927

🤔 586 attempts
📜 2 sessions
🫧 12 chat sessions
⁉️ 74 chat prompts
🤖 74 gpt-oss:120b replies
😱   1 🥵   4 😎  39 🥶 499 🧊  42

      $1 #586   ~1 fate              100.00°C 🥳 1000‰
      $2 #585   ~2 destiny            54.94°C 😱  999‰
      $3 #485  ~16 savior             33.96°C 🥵  984‰
      $4 #362  ~25 saga               33.35°C 🥵  978‰
      $5 #498  ~14 salvation          33.33°C 🥵  977‰
      $6 #441  ~20 odyssey            27.70°C 🥵  904‰
      $7 #355  ~26 epitaph            26.42°C 😎  875‰
      $8 #377  ~24 tale               26.41°C 😎  872‰
      $9 #576   ~3 providence         26.28°C 😎  865‰
     $10 #565   ~5 mercy              25.78°C 😎  839‰
     $11 #566   ~4 allegiance         25.47°C 😎  825‰
     $12 #545   ~6 lifeline           24.94°C 😎  795‰
     $46 #380      fable              19.59°C 🥶
    $545  #40      agglutination      -0.07°C 🧊

# cemantix.certitudes.org 🧩 #1366 🥳 269 ⏱️ 0:25:43.252306

🤔 270 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 54 chat prompts
🤖 54 gpt-oss:120b replies
🔥   1 🥵  18 😎  84 🥶 130 🧊  36

      $1 #270   ~1 informatique      100.00°C 🥳 1000‰
      $2 #184  ~35 maintenance        50.89°C 🔥  991‰
      $3 #225  ~17 numérique          49.65°C 🥵  986‰
      $4  #37  ~98 gestion            49.22°C 🥵  985‰
      $5 #110  ~70 application        45.03°C 🥵  972‰
      $6 #132  ~61 utilisateur        44.98°C 🥵  971‰
      $7 #143  ~52 documentation      41.84°C 🥵  958‰
      $8  #78  ~77 interfaçage        41.49°C 🥵  956‰
      $9 #130  ~62 service            41.32°C 🥵  955‰
     $10  #55  ~89 système            40.21°C 🥵  951‰
     $11  #74  ~79 dépannage          40.07°C 🥵  948‰
     $21  #53  ~90 supervision        35.15°C 😎  896‰
    $105  #92      surveillance       20.39°C 🥶
    $235  #91      scénario           -0.89°C 🧊
