# 2025-11-08

- 🔗 spaceword.org 🧩 2025-11-07 🏁 score 2173 ranked 2.8% 10/359 ⏱️ 3:52:55.707647
- 🔗 alfagok.diginaut.net 🧩 #371 🥳 13 ⏱️ 0:00:34.753420
- 🔗 alphaguess.com 🧩 #837 🥳 13 ⏱️ 0:00:36.114628
- 🔗 squareword.org 🧩 #1377 🥳 7 ⏱️ 0:02:20.450905
- 🔗 dictionary.com hurdle 🧩 #1407 🥳 18 ⏱️ 0:02:58.698143
- 🔗 dontwordle.com 🧩 #1264 🥳 6 ⏱️ 0:02:37.367114
- 🔗 cemantle.certitudes.org 🧩 #1314 🥳 660 ⏱️ 0:48:30.112232
- 🔗 cemantix.certitudes.org 🧩 #1347 🥳 241 ⏱️ 0:04:25.252257

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




# spaceword.org 🧩 2025-11-07 🏁 score 2173 ranked 2.8% 10/359 ⏱️ 3:52:55.707647

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 10/359

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ I C Y _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ _ J A W _ _ _   
      _ _ _ _ _ Q I _ _ _   
      _ _ _ _ _ U N _ _ _   
      _ _ _ _ T A G _ _ _   
      _ _ _ _ _ R _ _ _ _   
      _ _ _ _ R I N _ _ _   
      _ _ _ _ E A U _ _ _   


# alfagok.diginaut.net 🧩 #371 🥳 13 ⏱️ 0:00:34.753420

🤔 13 attempts
📜 1 sessions

    @        [     0] &-teken        
    @+1      [     1] &-tekens       
    @+2      [     2] -cijferig      
    @+3      [     3] -e-mail        
    @+99842  [ 99842] examen         q1  ? after
    @+102861 [102861] fel            q6  ? after
    @+103510 [103510] fietsen        q8  ? after
    @+103872 [103872] fietsvriend    q9  ? after
    @+103922 [103922] figurentheater q11 ? after
    @+103926 [103926] figuur         q12 ? it
    @+103926 [103926] figuur         done. it
    @+103972 [103972] fijn           q10 ? before
    @+104233 [104233] film           q7  ? before
    @+105983 [105983] fluctueren     q5  ? before
    @+112129 [112129] geboorte       q4  ? before
    @+124522 [124522] gevoel         q3  ? before
    @+149326 [149326] huis           q2  ? before
    @+199766 [199766] lijn           q0  ? before

# alphaguess.com 🧩 #837 🥳 13 ⏱️ 0:00:36.114628

🤔 13 attempts
📜 1 sessions

    @        [     0] aa            
    @+1      [     1] aah           
    @+2      [     2] aahed         
    @+3      [     3] aahing        
    @+98226  [ 98226] mach          q0  ? after
    @+122111 [122111] par           q2  ? after
    @+134642 [134642] prog          q3  ? after
    @+134983 [134983] pronoun       q8  ? after
    @+135002 [135002] pronunciation q11 ? after
    @+135005 [135005] proof         q12 ? it
    @+135005 [135005] proof         done. it
    @+135019 [135019] prop          q10 ? before
    @+135156 [135156] proportion    q9  ? before
    @+135348 [135348] proso         q7  ? before
    @+136062 [136062] psycho        q6  ? before
    @+137525 [137525] quad          q5  ? before
    @+140528 [140528] rec           q4  ? before
    @+147331 [147331] rho           q1  ? before

# squareword.org 🧩 #1377 🥳 7 ⏱️ 0:02:20.450905

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S H A R P
    M O R A L
    O M E G A
    T E N E T
    E R A S E

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1407 🥳 18 ⏱️ 0:02:58.698143

📜 1 sessions
💰 score: 9800

    3/6
    EARNS 🟨⬜⬜🟩⬜
    DWINE ⬜🟩🟩🟩🟩
    TWINE 🟩🟩🟩🟩🟩
    4/6
    TWINE 🟨⬜⬜⬜⬜
    AUTOS ⬜⬜🟨🟨🟨
    SHORT 🟨🟩🟩⬜🟩
    GHOST 🟩🟩🟩🟩🟩
    4/6
    GHOST ⬜⬜🟩⬜⬜
    ALONE ⬜⬜🟩🟩⬜
    IRONY ⬜🟩🟩🟩🟩
    CRONY 🟩🟩🟩🟩🟩
    5/6
    CRONY ⬜⬜⬜⬜⬜
    PILEA ⬜⬜🟨⬜⬜
    BLUSH ⬜🟨🟩🟨⬜
    SKULK 🟩🟩🟩🟩⬜
    SKULL 🟩🟩🟩🟩🟩
    Final 2/2
    PADLE 🟨🟨⬜🟩🟩
    AMPLE 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1264 🥳 6 ⏱️ 0:02:37.367114

📜 1 sessions
💰 score: 5

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:SHUSH n n n n n remain:4857
    ⬜⬜⬜⬜⬜ tried:VILLI n n n n n remain:2150
    ⬜⬜⬜⬜⬜ tried:PYGMY n n n n n remain:847
    ⬜🟨⬜⬜⬜ tried:BOFFO n m n n n remain:104
    ⬜⬜🟨⬜⬜ tried:CROWD n n m n n remain:6
    ⬜🟩⬜🟨🟩 tried:TAXON n Y n m Y remain:1

    Undos used: 4

      1 words remaining
    x 5 unused letters
    = 5 total score

# cemantle.certitudes.org 🧩 #1314 🥳 660 ⏱️ 0:48:30.112232

🤔 661 attempts
📜 1 sessions
🫧 40 chat sessions
⁉️ 243 chat prompts
🤖 188 gemma3:latest replies
🤖 39 llama3.2:latest replies
🤖 16 deepseek-r1:latest replies
🔥   5 🥵  23 😎  79 🥶 525 🧊  28

      $1 #661   ~1 suicide            100.00°C 🥳 1000‰
      $2 #384  ~49 homicide            51.37°C 🔥  998‰
      $3 #350  ~56 murder              49.83°C 🔥  997‰
      $4 #273  ~73 death               47.81°C 🔥  996‰
      $5 #658   ~2 depression          42.65°C 🔥  992‰
      $6 #346  ~59 assassination       41.23°C 🔥  991‰
      $7 #439  ~35 arson               40.51°C 🥵  988‰
      $8 #347  ~58 martyrdom           39.53°C 🥵  986‰
      $9 #223  ~86 violence            39.18°C 🥵  985‰
     $10 #434  ~36 immolation          37.94°C 🥵  983‰
     $11 #388  ~47 killing             37.89°C 🥵  981‰
     $30 #468  ~30 accident            29.59°C 😎  898‰
    $109 #457      stigma              19.70°C 🥶
    $634 #448      reckoning           -0.18°C 🧊

# cemantix.certitudes.org 🧩 #1347 🥳 241 ⏱️ 0:04:25.252257

🤔 242 attempts
📜 1 sessions
🫧 15 chat sessions
⁉️ 103 chat prompts
🤖 12 llama3.2:latest replies
🤖 91 gemma3:latest replies
🔥   5 🥵  29 😎  74 🥶 107 🧊  26

      $1 #242   ~1 emprunt           100.00°C 🥳 1000‰
      $2 #168  ~30 endettement        50.24°C 🔥  997‰
      $3  #89  ~75 dette              48.77°C 🔥  994‰
      $4  #86  ~78 prêt               47.16°C 🔥  993‰
      $5  #88  ~76 crédit             45.80°C 🔥  991‰
      $6 #238   ~3 amortissement      45.73°C 🔥  990‰
      $7 #186  ~21 hypothécaire       45.23°C 🥵  989‰
      $8  #42 ~104 trésorerie         44.97°C 🥵  988‰
      $9  #72  ~88 investissement     41.39°C 🥵  980‰
     $10 #103  ~63 remboursement      40.55°C 🥵  976‰
     $11 #135  ~47 montant            39.48°C 🥵  975‰
     $36  #65  ~93 bancaire           30.03°C 😎  898‰
    $110 #232      délai              15.92°C 🥶
    $217 #220      expertise          -0.21°C 🧊
