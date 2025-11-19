# 2025-11-20

- 🔗 spaceword.org 🧩 2025-11-19 🏁 score 2168 ranked 41.4% 153/370 ⏱️ 0:32:54.161148
- 🔗 alfagok.diginaut.net 🧩 #383 🥳 14 ⏱️ 0:00:38.473356
- 🔗 alphaguess.com 🧩 #849 🥳 18 ⏱️ 0:00:42.207701
- 🔗 squareword.org 🧩 #1389 🥳 8 ⏱️ 0:02:42.084826
- 🔗 dictionary.com hurdle 🧩 #1419 🥳 16 ⏱️ 0:03:46.029412
- 🔗 dontwordle.com 🧩 #1276 🥳 6 ⏱️ 0:02:20.095649
- 🔗 cemantle.certitudes.org 🧩 #1326 🥳 161 ⏱️ 0:00:54.171687
- 🔗 cemantix.certitudes.org 🧩 #1359 🥳 950 ⏱️ 8:11:21.381744

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
















# spaceword.org 🧩 2025-11-19 🏁 score 2168 ranked 41.4% 153/370 ⏱️ 0:32:54.161148

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 153/370

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ D _ G _ _ _ _ _ _   
      _ E _ R _ Z _ J O _   
      _ A Q U A E _ O D _   
      _ D _ M A N A G E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #383 🥳 14 ⏱️ 0:00:38.473356

🤔 14 attempts
📜 1 sessions

    @        [     0] &-teken       
    @+1      [     1] &-tekens      
    @+2      [     2] -cijferig     
    @+3      [     3] -e-mail       
    @+199763 [199763] lijn          q0  ? after
    @+299646 [299646] schudde       q1  ? after
    @+349377 [349377] vak           q2  ? after
    @+361746 [361746] vervijfvoudig q4  ? after
    @+367898 [367898] vocht         q5  ? after
    @+367918 [367918] vochthoudende q12 ? after
    @+367920 [367920] vochtig       q13 ? it
    @+367920 [367920] vochtig       done. it
    @+367938 [367938] vochtmaat     q11 ? before
    @+367978 [367978] vod           q10 ? before
    @+368058 [368058] voeding       q9  ? before
    @+368453 [368453] voer          q8  ? before
    @+369074 [369074] vogel         q7  ? before
    @+370391 [370391] voor          q6  ? before
    @+374120 [374120] vrij          q3  ? before

# alphaguess.com 🧩 #849 🥳 18 ⏱️ 0:00:42.207701

🤔 18 attempts
📜 1 sessions

    @        [     0] aa       
    @+1      [     1] aah      
    @+2      [     2] aahed    
    @+3      [     3] aahing   
    @+98226  [ 98226] mach     q0  ? after
    @+122111 [122111] par      q2  ? after
    @+134642 [134642] prog     q3  ? after
    @+136062 [136062] psycho   q6  ? after
    @+136791 [136791] pupil    q7  ? after
    @+136823 [136823] pur      q9  ? after
    @+136972 [136972] purs     q10 ? after
    @+136973 [136973] purse    q17 ? it
    @+136973 [136973] purse    done. it
    @+136974 [136974] pursed   q16 ? before
    @+136976 [136976] purser   q15 ? before
    @+136979 [136979] pursier  q14 ? before
    @+136985 [136985] purslane q13 ? before
    @+136998 [136998] pursuits q12 ? before
    @+137023 [137023] pus      q11 ? before
    @+137145 [137145] putt     q8  ? before
    @+137525 [137525] quad     q5  ? before
    @+140528 [140528] rec      q4  ? before
    @+147331 [147331] rho      q1  ? before

# squareword.org 🧩 #1389 🥳 8 ⏱️ 0:02:42.084826

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟨 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A D A P T
    S O R R Y
    S U G A R
    A L O N E
    Y A N K S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1419 🥳 16 ⏱️ 0:03:46.029412

📜 1 sessions
💰 score: 10000

    5/6
    TEARS ⬜⬜🟨⬜⬜
    ALOIN 🟨⬜🟨⬜🟩
    WAGON ⬜🟩⬜🟩🟩
    BACON ⬜🟩🟨🟩🟩
    CANON 🟩🟩🟩🟩🟩
    3/6
    CANON ⬜🟩⬜⬜⬜
    LATER ⬜🟩🟨🟨⬜
    HASTE 🟩🟩🟩🟩🟩
    3/6
    HASTE ⬜🟩⬜⬜⬜
    MANIC 🟩🟩⬜🟩⬜
    MAFIA 🟩🟩🟩🟩🟩
    4/6
    MAFIA ⬜🟨⬜⬜🟨
    SLAVE ⬜⬜🟨⬜🟨
    CEDAR ⬜🟨🟨🟩⬜
    AHEAD 🟩🟩🟩🟩🟩
    Final 1/2
    LEFTY 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1276 🥳 6 ⏱️ 0:02:20.095649

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:EVOKE n n n n n remain:3766
    ⬜⬜⬜⬜⬜ tried:FULLY n n n n n remain:1309
    ⬜⬜⬜⬜🟩 tried:PHPHT n n n n Y remain:64
    ⬜🟨⬜⬜🟩 tried:BINIT n m n n Y remain:11
    ⬜⬜🟩🟩🟩 tried:GRIST n n Y Y Y remain:4
    ⬜🟩🟩🟩🟩 tried:MAIST n Y Y Y Y remain:2

    Undos used: 5

      2 words remaining
    x 7 unused letters
    = 14 total score

# cemantle.certitudes.org 🧩 #1326 🥳 161 ⏱️ 0:00:54.171687

🤔 162 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 29 chat prompts
🤖 29 gemma3:latest replies
🥵   6 😎  13 🥶 139 🧊   3

      $1 #162   ~1 complexity      100.00°C 🥳 1000‰
      $2  #64  ~13 fragmentation    44.63°C 🥵  984‰
      $3  #82   ~9 ambiguity        44.17°C 🥵  979‰
      $4 #158   ~4 complex          41.74°C 🥵  946‰
      $5 #159   ~3 convoluted       39.79°C 🥵  929‰
      $6  #15  ~19 absurdity        39.40°C 🥵  917‰
      $7 #128   ~6 opacity          38.55°C 🥵  900‰
      $8   #5  ~20 paradox          37.76°C 😎  879‰
      $9 #126   ~7 arcane           37.07°C 😎  856‰
     $10  #74  ~11 uncertainty      35.45°C 😎  789‰
     $11  #60  ~14 entropy          35.33°C 😎  785‰
     $12 #144   ~5 fragmented       35.14°C 😎  779‰
     $21  #54      distortion       28.15°C 🥶
    $160  #49      aberration       -1.03°C 🧊

# cemantix.certitudes.org 🧩 #1359 🥳 950 ⏱️ 8:11:21.381744

🤔 951 attempts
📜 3 sessions
🫧 160 chat sessions
⁉️ 1015 chat prompts
🤖 47 llama3.2:latest replies
🤖 949 gemma3:latest replies
🤖 18 qwen3:8b replies
😱   1 🔥   7 🥵  24 😎  89 🥶 760 🧊  69

      $1 #951   ~1 jaune            100.00°C 🥳 1000‰
      $2 #802  ~18 rouge             77.31°C 😱  999‰
      $3 #266  ~84 bleu              73.84°C 🔥  998‰
      $4 #298  ~71 violet            66.66°C 🔥  997‰
      $5 #314  ~65 blanc             66.08°C 🔥  996‰
      $6 #171  ~92 vert              61.52°C 🔥  995‰
      $7 #296  ~72 mauve             58.54°C 🔥  994‰
      $8 #207  ~90 gris              58.44°C 🔥  993‰
      $9  #47 ~116 couleur           57.01°C 🔥  991‰
     $10 #434  ~46 noir              56.45°C 🥵  989‰
     $11 #925   ~7 marron            52.18°C 🥵  986‰
     $34 #386  ~52 iridescent        37.40°C 😎  877‰
    $123  #10      étoile            25.96°C 🥶
    $883 #638      mouvement         -0.05°C 🧊
