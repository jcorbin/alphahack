# 2025-11-02

- 🔗 spaceword.org 🧩 2025-11-01 🏁 score 2173 ranked 6.6% 24/362 ⏱️ 1:04:43.367685
- 🔗 alfagok.diginaut.net 🧩 #365 🥳 13 ⏱️ 0:00:33.417467
- 🔗 alphaguess.com 🧩 #831 🥳 17 ⏱️ 0:00:41.020275
- 🔗 squareword.org 🧩 #1371 🥳 7 ⏱️ 0:01:45.001795
- 🔗 dictionary.com hurdle 🧩 #1400 🥳 18 ⏱️ 0:03:48.162326
- 🔗 dontwordle.com 🧩 #1258 🤷 6 ⏱️ 0:01:55.742302
- 🔗 cemantle.certitudes.org 🧩 #1308 🥳 239 ⏱️ 0:09:26.735040
- 🔗 cemantix.certitudes.org 🧩 #1341 🥳 162 ⏱️ 0:05:13.203714

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







# spaceword.org 🧩 2025-11-01 🏁 score 2173 ranked 6.6% 24/362 ⏱️ 1:04:43.367685

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 24/362

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ O E _ S E I Z E D   
      _ A M O K _ _ _ L A   
      _ F _ H I J R A S _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #365 🥳 13 ⏱️ 0:00:33.417467

🤔 13 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199827 [199827] lijm      q0  ? after
    @+299729 [299729] schub     q1  ? after
    @+311898 [311898] spier     q4  ? after
    @+313253 [313253] sport     q6  ? after
    @+313923 [313923] spreek    q7  ? after
    @+314233 [314233] sprint    q8  ? after
    @+314309 [314309] sprokkel  q10 ? after
    @+314330 [314330] sprong    q12 ? it
    @+314330 [314330] sprong    done. it
    @+314348 [314348] sprookjes q11 ? before
    @+314415 [314415] spui      q9  ? before
    @+314607 [314607] st        q5  ? before
    @+324303 [324303] sub       q3  ? before
    @+349504 [349504] vakantie  q2  ? before

# alphaguess.com 🧩 #831 🥳 17 ⏱️ 0:00:41.020275

🤔 17 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+47387 [47387] dis       q1  ? after
    @+49434 [49434] do        q5  ? after
    @+49602 [49602] dog       q9  ? after
    @+49726 [49726] dogsled   q10 ? after
    @+49739 [49739] dogtrot   q13 ? after
    @+49749 [49749] dogy      q14 ? after
    @+49754 [49754] doilies   q15 ? after
    @+49756 [49756] doing     q16 ? it
    @+49756 [49756] doing     done. it
    @+49758 [49758] doit      q12 ? before
    @+49787 [49787] dollar    q11 ? before
    @+49855 [49855] dom       q8  ? before
    @+50411 [50411] dove      q7  ? before
    @+51408 [51408] drunk     q6  ? before
    @+53403 [53403] el        q4  ? before
    @+60090 [60090] face      q3  ? before
    @+72807 [72807] gremolata q2  ? before
    @+98226 [98226] mach      q0  ? before

# squareword.org 🧩 #1371 🥳 7 ⏱️ 0:01:45.001795

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    T A M E S
    O V E R T
    M I T R E
    B A R O N
    S N O R T

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1400 🥳 18 ⏱️ 0:03:48.162326

📜 1 sessions
💰 score: 9800

    2/6
    TOEAS ⬜🟨🟨🟨🟨
    AROSE 🟩🟩🟩🟩🟩
    4/6
    AROSE ⬜🟨⬜⬜🟨
    INTER ⬜🟨⬜🟩🟩
    NEVER 🟩🟩⬜🟩🟩
    NEWER 🟩🟩🟩🟩🟩
    5/6
    NEWER ⬜⬜⬜⬜⬜
    LOTAS 🟨⬜⬜⬜⬜
    GULPY ⬜⬜🟨⬜⬜
    FLICK ⬜🟩🟩🟩🟩
    CLICK 🟩🟩🟩🟩🟩
    5/6
    CLICK ⬜⬜🟨⬜⬜
    NITRE ⬜🟨⬜🟨🟨
    DEAIR ⬜🟩⬜🟩🟨
    REMIX 🟨🟩⬜🟩⬜
    SERIF 🟩🟩🟩🟩🟩
    Final 2/2
    GUIDE ⬜🟩🟩⬜🟩
    QUITE 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1258 🤷 6 ⏱️ 0:01:55.742302

📜 1 sessions
💰 score: 0

ELIMINATED
> Well technically I didn't Wordle!

    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:7266
    ⬜⬜⬜⬜⬜ tried:TENET n n n n n remain:2001
    ⬜⬜⬜⬜⬜ tried:DADAS n n n n n remain:258
    ⬜⬜⬜⬜⬜ tried:LOWLY n n n n n remain:11
    ⬜🟨⬜⬜⬜ tried:HUMPH n m n n n remain:1
    ⬛⬛⬛⬛⬛ tried:GRUFF Y Y Y Y Y remain:0

    Undos used: 5

      0 words remaining
    x 0 unused letters
    = 0 total score

# cemantle.certitudes.org 🧩 #1308 🥳 239 ⏱️ 0:09:26.735040

🤔 240 attempts
📜 1 sessions
🫧 12 chat sessions
⁉️ 80 chat prompts
🤖 20 llama3.2:latest replies
🤖 60 gemma3:latest replies
😱   1 🔥   4 🥵  29 😎  41 🥶 158 🧊   6

      $1 #240   ~1 burning        100.00°C 🥳 1000‰
      $2  #54  ~57 burn            75.92°C 😱  999‰
      $3 #208  ~16 smoldering      59.63°C 🔥  996‰
      $4 #198  ~23 fire            50.56°C 🔥  993‰
      $5 #214  ~13 flammable       47.91°C 🔥  991‰
      $6 #114  ~34 blackened       47.06°C 🔥  990‰
      $7  #46  ~63 smolder         46.65°C 🥵  989‰
      $8 #201  ~21 blazing         46.57°C 🥵  988‰
      $9  #99  ~44 scorched        45.37°C 🥵  986‰
     $10  #38  ~66 inferno         45.15°C 🥵  984‰
     $11  #89  ~49 smoke           43.82°C 🥵  981‰
     $36 #236   ~3 vaporization    32.64°C 😎  895‰
     $77 #153      flint           21.32°C 🥶
    $235 #128      gloom           -0.14°C 🧊

# cemantix.certitudes.org 🧩 #1341 🥳 162 ⏱️ 0:05:13.203714

🤔 163 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 35 chat prompts
🤖 35 gemma3:latest replies
🔥  3 🥵 14 😎 38 🥶 80 🧊 27

      $1 #163   ~1 vérification      100.00°C 🥳 1000‰
      $2 #143  ~14 contrôle           63.71°C 🔥  998‰
      $3 #135  ~21 conformité         56.12°C 🔥  996‰
      $4 #132  ~24 validation         54.69°C 🔥  994‰
      $5 #151   ~9 justification      42.23°C 🥵  970‰
      $6 #150  ~10 examen             41.30°C 🥵  963‰
      $7 #141  ~16 audit              40.97°C 🥵  958‰
      $8 #109  ~41 donnée             40.25°C 🥵  955‰
      $9 #106  ~42 application        39.71°C 🥵  952‰
     $10 #145  ~12 correction         39.61°C 🥵  950‰
     $11 #140  ~17 évaluation         39.12°C 🥵  938‰
     $19 #131  ~25 traitement         36.61°C 😎  897‰
     $57  #85      référence          24.22°C 🥶
    $137  #42      ruban              -1.23°C 🧊
