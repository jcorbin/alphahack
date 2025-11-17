# 2025-11-18

- 🔗 spaceword.org 🧩 2025-11-17 🏁 score 2173 ranked 6.1% 18/295 ⏱️ 7:24:12.281842
- 🔗 alfagok.diginaut.net 🧩 #381 🥳 16 ⏱️ 0:00:38.883487
- 🔗 dictionary.com hurdle 🧩 #1417 🥳 18 ⏱️ 0:03:09.356501
- 🔗 dontwordle.com 🧩 #1274 🥳 6 ⏱️ 0:01:35.903803
- 🔗 cemantle.certitudes.org 🧩 #1324 🥳 147 ⏱️ 0:01:04.678305
- 🔗 cemantix.certitudes.org 🧩 #1357 🥳 727 ⏱️ 0:54:37.640850
- 🔗 alphaguess.com 🧩 #847 🥳 14 ⏱️ 0:02:16.499974
- 🔗 squareword.org 🧩 #1387 🥳 7 ⏱️ 0:03:21.606104

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














# spaceword.org 🧩 2025-11-17 🏁 score 2173 ranked 6.1% 18/295 ⏱️ 7:24:12.281842

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 18/295

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ K _ V _ R A I N _   
      _ E _ A W A I T E D   
      _ F U C O I D _ G _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #381 🥳 16 ⏱️ 0:00:38.883487

🤔 16 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+1      [     1] &-tekens     
    @+2      [     2] -cijferig    
    @+3      [     3] -e-mail      
    @+99839  [ 99839] examen       q1  ? after
    @+149323 [149323] huis         q2  ? after
    @+174540 [174540] kinderboeken q3  ? after
    @+187072 [187072] kroon        q4  ? after
    @+193406 [193406] lawaai       q5  ? after
    @+194971 [194971] leest        q7  ? after
    @+195208 [195208] leger        q9  ? after
    @+195440 [195440] legitiem     q10 ? after
    @+195509 [195509] leid         q11 ? after
    @+195518 [195518] leiden       q14 ? after
    @+195522 [195522] leider       q15 ? it
    @+195522 [195522] leider       done. it
    @+195527 [195527] leiders      q13 ? before
    @+195591 [195591] leidmotieven q12 ? before
    @+195672 [195672] lek          q8  ? before
    @+196570 [196570] let          q6  ? before
    @+199763 [199763] lijn         q0  ? before

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1417 🥳 18 ⏱️ 0:03:09.356501

📜 1 sessions
💰 score: 9800

    3/6
    AISLE 🟨⬜⬜⬜⬜
    TROAK 🟩⬜⬜🟨⬜
    TAUNT 🟩🟩🟩🟩🟩
    4/6
    TAUNT ⬜🟩⬜⬜🟩
    DAVIT ⬜🟩⬜⬜🟩
    FACET ⬜🟩🟩⬜🟩
    YACHT 🟩🟩🟩🟩🟩
    4/6
    YACHT ⬜🟨⬜⬜🟩
    LEAPT 🟨⬜🟨⬜🟩
    FLOAT ⬜🟩🟩🟩🟩
    BLOAT 🟩🟩🟩🟩🟩
    5/6
    BLOAT 🟩⬜🟨⬜⬜
    BOURN 🟩🟩⬜⬜⬜
    BODES 🟩🟩⬜🟨⬜
    BOGIE 🟩🟩⬜⬜🟩
    BOCCE 🟩🟩🟩🟩🟩
    Final 2/2
    OVATE 🟩⬜🟩🟩🟩
    ORATE 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1274 🥳 6 ⏱️ 0:01:35.903803

📜 1 sessions
💰 score: 21

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:JEEZE n n n n n remain:6889
    ⬜⬜⬜⬜⬜ tried:MAMMA n n n n n remain:2956
    ⬜⬜⬜⬜⬜ tried:BIDIS n n n n n remain:461
    ⬜⬜⬜⬜⬜ tried:FLUFF n n n n n remain:142
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:35
    🟨⬜🟨⬜⬜ tried:KNOWN m n m n n remain:3

    Undos used: 4

      3 words remaining
    x 7 unused letters
    = 21 total score

# cemantle.certitudes.org 🧩 #1324 🥳 147 ⏱️ 0:01:04.678305

🤔 148 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 46 chat prompts
🤖 46 gemma3:latest replies
🔥   1 🥵   8 😎  21 🥶 107 🧊  10

      $1 #148   ~1 exemption        100.00°C 🥳 1000‰
      $2 #144   ~3 permit            44.39°C 🔥  990‰
      $3 #114  ~18 permission        40.52°C 🥵  980‰
      $4 #110  ~19 authorization     37.63°C 🥵  962‰
      $5 #130   ~8 privilege         35.92°C 🥵  951‰
      $6 #125  ~11 jurisdiction      35.70°C 🥵  947‰
      $7  #99  ~23 approval          34.09°C 🥵  925‰
      $8 #109  ~20 sanction          34.09°C 🥵  924‰
      $9 #124  ~12 grant             33.35°C 🥵  917‰
     $10 #126  ~10 license           32.89°C 🥵  905‰
     $11 #120  ~14 consent           31.86°C 😎  888‰
     $12 #116  ~17 authority         31.78°C 😎  887‰
     $32  #73      favor             19.05°C 🥶
    $139  #39      anchor            -0.29°C 🧊

# cemantix.certitudes.org 🧩 #1357 🥳 727 ⏱️ 0:54:37.640850

🤔 728 attempts
📜 4 sessions
🫧 81 chat sessions
⁉️ 548 chat prompts
🤖 548 gemma3:latest replies
🔥   4 🥵  26 😎 140 🥶 392 🧊 165

      $1 #728   ~1 trimestre         100.00°C 🥳 1000‰
      $2 #703   ~6 mois               49.56°C 🔥  998‰
      $3 #466  ~55 annuel             46.86°C 🔥  995‰
      $4 #202 ~143 chiffre            45.49°C 🔥  994‰
      $5 #643  ~22 mensuel            44.53°C 🔥  993‰
      $6 #237 ~134 année              42.31°C 🥵  989‰
      $7 #117 ~158 progression        42.11°C 🥵  988‰
      $8 #348  ~83 période            40.29°C 🥵  987‰
      $9 #646  ~20 cotisation         38.98°C 🥵  986‰
     $10 #121 ~157 taux               38.29°C 🥵  985‰
     $11 #304 ~101 montant            36.88°C 🥵  983‰
     $32 #685   ~9 consolider         28.53°C 😎  897‰
    $172 #235      comptabilité       15.76°C 🥶
    $564 #102      issue              -0.01°C 🧊

# alphaguess.com 🧩 #847 🥳 14 ⏱️ 0:02:16.499974

🤔 14 attempts
📜 2 sessions

    @       [    0] aa          
    @+1     [    1] aah         
    @+2     [    2] aahed       
    @+3     [    3] aahing      
    @+47387 [47387] dis         q1  ? after
    @+53403 [53403] el          q4  ? after
    @+54926 [54926] end         q6  ? after
    @+55806 [55806] enter       q7  ? after
    @+56275 [56275] ephedrin    q8  ? after
    @+56512 [56512] epinastic   q9  ? after
    @+56630 [56630] epithelioma q10 ? after
    @+56682 [56682] eponym      q11 ? after
    @+56713 [56713] equable     q12 ? after
    @+56717 [56717] equal       q13 ? it
    @+56717 [56717] equal       done. it
    @+56748 [56748] equate      q5  ? before
    @+60090 [60090] face        q3  ? before
    @+72807 [72807] gremolata   q2  ? before
    @+98226 [98226] mach        q0  ? before

# squareword.org 🧩 #1387 🥳 7 ⏱️ 0:03:21.606104

📜 3 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    G R A S P
    R A D I O
    A D O R E
    F I R E S
    T I N N Y
