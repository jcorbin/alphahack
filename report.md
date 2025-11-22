# 2025-11-23

- 🔗 spaceword.org 🧩 2025-11-22 🏁 score 2168 ranked 46.0% 159/346 ⏱️ 3:41:46.632828
- 🔗 alfagok.diginaut.net 🧩 #386 🥳 13 ⏱️ 0:00:33.388642
- 🔗 alphaguess.com 🧩 #852 🥳 13 ⏱️ 0:00:28.769243
- 🔗 squareword.org 🧩 #1392 🥳 9 ⏱️ 0:03:25.918919
- 🔗 dictionary.com hurdle 🧩 #1422 🥳 16 ⏱️ 0:03:06.660352
- 🔗 dontwordle.com 🧩 #1279 🥳 6 ⏱️ 0:01:33.374980
- 🔗 cemantle.certitudes.org 🧩 #1329 🥳 364 ⏱️ 0:06:48.889651
- 🔗 cemantix.certitudes.org 🧩 #1362 🥳 357 ⏱️ 0:04:11.684111

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



















# spaceword.org 🧩 2025-11-22 🏁 score 2168 ranked 46.0% 159/346 ⏱️ 3:41:46.632828

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 159/346

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ G _ A H _   
      _ W _ _ J O _ G I _   
      _ E _ N O O S E D _   
      _ E Q U E S _ D _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #386 🥳 13 ⏱️ 0:00:33.388642

🤔 13 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+24909  [ 24909] bad       q3  ? after
    @+31126  [ 31126] begeleid  q5  ? after
    @+31468  [ 31468] begraaf   q9  ? after
    @+31547  [ 31547] begrijp   q11 ? after
    @+31564  [ 31564] begrip    q12 ? it
    @+31564  [ 31564] begrip    done. it
    @+31634  [ 31634] begroting q10 ? before
    @+31821  [ 31821] behandel  q8  ? before
    @+32554  [ 32554] bejaarden q7  ? before
    @+34009  [ 34009] beleid    q6  ? before
    @+37363  [ 37363] bescherm  q4  ? before
    @+49909  [ 49909] bol       q2  ? before
    @+99839  [ 99839] examen    q1  ? before
    @+199763 [199763] lijn      q0  ? before

# alphaguess.com 🧩 #852 🥳 13 ⏱️ 0:00:28.769243

🤔 13 attempts
📜 1 sessions

    @        [     0] aa         
    @+1      [     1] aah        
    @+2      [     2] aahed      
    @+3      [     3] aahing     
    @+98226  [ 98226] mach       q0  ? after
    @+122111 [122111] par        q2  ? after
    @+134642 [134642] prog       q3  ? after
    @+140528 [140528] rec        q4  ? after
    @+141910 [141910] ree        q6  ? after
    @+142657 [142657] reg        q7  ? after
    @+143132 [143132] rein       q8  ? after
    @+143462 [143462] rekey      q9  ? after
    @+143542 [143542] relativize q11 ? after
    @+143582 [143582] release    q12 ? it
    @+143582 [143582] release    done. it
    @+143627 [143627] releves    q10 ? before
    @+143792 [143792] rem        q5  ? before
    @+147331 [147331] rho        q1  ? before

# squareword.org 🧩 #1392 🥳 9 ⏱️ 0:03:25.918919

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B R I N E
    L E M O N
    O R B I T
    C A U S E
    S N E E R

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1422 🥳 16 ⏱️ 0:03:06.660352

📜 1 sessions
💰 score: 10000

    4/6
    SERAL ⬜⬜⬜🟨⬜
    PIANO ⬜🟨🟨⬜🟨
    AVOID 🟩⬜🟨🟨⬜
    AXIOM 🟩🟩🟩🟩🟩
    4/6
    AXIOM ⬜⬜⬜⬜⬜
    WURST ⬜⬜🟨🟩⬜
    FRESH ⬜🟩🟩🟩⬜
    DRESS 🟩🟩🟩🟩🟩
    3/6
    DRESS 🟨⬜⬜⬜⬜
    HALID 🟩⬜⬜🟩🟩
    HUMID 🟩🟩🟩🟩🟩
    4/6
    HUMID ⬜⬜⬜⬜⬜
    ROAST ⬜🟨⬜⬜⬜
    ELBOW 🟩⬜🟨🟨⬜
    EBONY 🟩🟩🟩🟩🟩
    Final 1/2
    DROLL 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1279 🥳 6 ⏱️ 0:01:33.374980

📜 1 sessions
💰 score: 18

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:FEMME n n n n n remain:5567
    ⬜⬜⬜⬜⬜ tried:BUBBY n n n n n remain:2936
    ⬜⬜⬜⬜⬜ tried:KININ n n n n n remain:1009
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:302
    ⬜🟨⬜⬜⬜ tried:PHPHT n m n n n remain:21
    🟨🟨⬜⬜🟨 tried:COOCH m m n n m remain:2

    Undos used: 3

      2 words remaining
    x 9 unused letters
    = 18 total score

# cemantle.certitudes.org 🧩 #1329 🥳 364 ⏱️ 0:06:48.889651

🤔 365 attempts
📜 1 sessions
🫧 34 chat sessions
⁉️ 169 chat prompts
🤖 11 llama3.2:latest replies
🤖 158 gemma3:latest replies
🔥   3 🥵   7 😎  45 🥶 289 🧊  20

      $1 #365   ~1 divorce         100.00°C 🥳 1000‰
      $2 #358   ~6 marital          62.55°C 🔥  997‰
      $3 #359   ~5 spousal          59.01°C 🔥  996‰
      $4 #354   ~7 alimony          56.92°C 🔥  994‰
      $5 #297  ~15 guardianship     48.04°C 🥵  983‰
      $6 #277  ~20 probate          46.29°C 🥵  977‰
      $7 #265  ~23 inheritance      42.77°C 🥵  966‰
      $8 #264  ~24 estate           38.14°C 🥵  939‰
      $9 #316  ~12 intestate        37.51°C 🥵  934‰
     $10 #188  ~41 legal            35.02°C 🥵  905‰
     $11 #189  ~40 court            34.75°C 🥵  902‰
     $12 #349   ~8 intestacy        34.58°C 😎  899‰
     $57 #279      succession       21.33°C 🥶
    $346   #2      echo             -0.06°C 🧊

# cemantix.certitudes.org 🧩 #1362 🥳 357 ⏱️ 0:04:11.684111

🤔 358 attempts
📜 1 sessions
🫧 18 chat sessions
⁉️ 119 chat prompts
🤖 28 llama3.2:latest replies
🤖 91 gemma3:latest replies
😱   1 🔥   3 🥵  33 😎  94 🥶 176 🧊  50

      $1 #358   ~1 placement         100.00°C 🥳 1000‰
      $2 #254  ~44 épargne            54.44°C 😱  999‰
      $3 #182  ~75 portefeuille       46.48°C 🔥  993‰
      $4 #139 ~102 investisseur       43.29°C 🔥  991‰
      $5 #145  ~98 liquidité          43.00°C 🔥  990‰
      $6 #282  ~30 financier          40.24°C 🥵  988‰
      $7 #126 ~109 capitalisation     40.12°C 🥵  987‰
      $8 #117 ~114 investissement     39.31°C 🥵  985‰
      $9 #129 ~107 rendement          38.15°C 🥵  981‰
     $10 #123 ~111 capital            38.11°C 🥵  980‰
     $11 #205  ~61 fonds              38.11°C 🥵  979‰
     $39 #189  ~70 cotation           28.76°C 😎  898‰
    $133 #281      expertise          17.06°C 🥶
    $309  #44      subtilité          -0.05°C 🧊
