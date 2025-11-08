# 2025-11-09

- 🔗 spaceword.org 🧩 2025-11-08 🏁 score 2173 ranked 3.7% 13/347 ⏱️ 0:35:46.800819
- 🔗 alfagok.diginaut.net 🧩 #372 🥳 20 ⏱️ 0:00:55.147896
- 🔗 alphaguess.com 🧩 #838 🥳 14 ⏱️ 0:00:32.833661
- 🔗 squareword.org 🧩 #1378 🥳 6 ⏱️ 0:02:00.351372
- 🔗 dictionary.com hurdle 🧩 #1408 🥳 17 ⏱️ 0:05:56.647033
- 🔗 dontwordle.com 🧩 #1265 😳 6 ⏱️ 0:00:57.954421
- 🔗 cemantle.certitudes.org 🧩 #1315 🥳 214 ⏱️ 0:02:02.249106
- 🔗 cemantix.certitudes.org 🧩 #1348 🥳 289 ⏱️ 0:02:43.696313

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





# spaceword.org 🧩 2025-11-08 🏁 score 2173 ranked 3.7% 13/347 ⏱️ 0:35:46.800819

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 13/347

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ W _ S Q U E E Z E   
      _ U _ A _ _ _ R E G   
      _ D U C T E D _ P O   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #372 🥳 20 ⏱️ 0:00:55.147896

🤔 20 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+1      [     1] &-tekens     
    @+2      [     2] -cijferig    
    @+3      [     3] -e-mail      
    @+199766 [199766] lijn         q0  ? after
    @+247603 [247603] op           q2  ? after
    @+254008 [254008] out          q5  ? after
    @+254195 [254195] over         q7  ? after
    @+255458 [255458] overleg      q8  ? after
    @+255891 [255891] overs        q9  ? after
    @+256326 [256326] overval      q10 ? after
    @+256419 [256419] overvoed     q12 ? after
    @+256464 [256464] overweg      q13 ? after
    @+256468 [256468] overwegen    q16 ? after
    @+256470 [256470] overwegende  q18 ? after
    @+256471 [256471] overweging   q19 ? it
    @+256471 [256471] overweging   done. it
    @+256472 [256472] overwegingen q17 ? before
    @+256476 [256476] overweldig   q15 ? before
    @+256491 [256491] overwelf     q14 ? before
    @+256517 [256517] overwin      q11 ? before
    @+256765 [256765] pa           q6  ? before
    @+260490 [260490] pater        q4  ? before
    @+273409 [273409] proef        q3  ? before
    @+299650 [299650] schudde      q1  ? before

# alphaguess.com 🧩 #838 🥳 14 ⏱️ 0:00:32.833661

🤔 14 attempts
📜 1 sessions

    @        [     0] aa     
    @+1      [     1] aah    
    @+2      [     2] aahed  
    @+3      [     3] aahing 
    @+98226  [ 98226] mach   q0  ? after
    @+147331 [147331] rho    q1  ? after
    @+153331 [153331] sea    q4  ? after
    @+156468 [156468] shit   q5  ? after
    @+158037 [158037] sine   q6  ? after
    @+158816 [158816] sky    q7  ? after
    @+159007 [159007] slap   q9  ? after
    @+159108 [159108] sleave q10 ? after
    @+159125 [159125] sleazo q12 ? after
    @+159130 [159130] sled   q13 ? it
    @+159130 [159130] sled   done. it
    @+159145 [159145] sleek  q11 ? before
    @+159212 [159212] sleigh q8  ? before
    @+159613 [159613] slug   q3  ? before
    @+171931 [171931] tag    q2  ? before

# squareword.org 🧩 #1378 🥳 6 ⏱️ 0:02:00.351372

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A P S E S
    T R I A L
    L I E G E
    A N G L E
    S T E E P

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1408 🥳 17 ⏱️ 0:05:56.647033

📜 1 sessions
💰 score: 9900

    4/6
    RACES ⬜⬜⬜⬜⬜
    MILTY 🟨⬜⬜⬜🟩
    DUMPY ⬜⬜🟨🟨🟩
    PYGMY 🟩🟩🟩🟩🟩
    4/6
    PYGMY ⬜⬜⬜⬜⬜
    ASTIR 🟨⬜🟨⬜🟨
    TRACE 🟨🟨🟨⬜🟨
    EARTH 🟩🟩🟩🟩🟩
    5/6
    EARTH ⬜🟨⬜⬜⬜
    SLACK 🟩⬜🟩⬜⬜
    SWAMP 🟩⬜🟩⬜🟨
    SPANG 🟩🟨🟩⬜⬜
    SOAPY 🟩🟩🟩🟩🟩
    3/6
    SOAPY ⬜⬜🟨⬜⬜
    ALINE 🟨⬜🟨🟨⬜
    MANIC 🟩🟩🟩🟩🟩
    Final 1/2
    STOVE 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1265 😳 6 ⏱️ 0:00:57.954421

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜🟨🟩⬜⬜ tried:RALES n m Y n n remain:63
    ⬜⬜🟩🟨⬜ tried:LILAC n n Y m n remain:12
    🟩🟩🟩🟩🟩 tried:AGLOW Y Y Y Y Y remain:0
    ⬛⬛⬛⬛⬛ tried:????? remain:0
    ⬛⬛⬛⬛⬛ tried:????? remain:0
    ⬛⬛⬛⬛⬛ tried:????? remain:0

    Undos used: 0

      0 words remaining
    x 0 unused letters
    = 0 total score

# cemantle.certitudes.org 🧩 #1315 🥳 214 ⏱️ 0:02:02.249106

🤔 215 attempts
📜 1 sessions
🫧 12 chat sessions
⁉️ 74 chat prompts
🤖 13 llama3.2:latest replies
🤖 61 gemma3:latest replies
🔥   2 🥵   6 😎  22 🥶 181 🧊   3

      $1 #215   ~1 manuscript      100.00°C 🥳 1000‰
      $2 #206   ~4 codex            55.79°C 🔥  997‰
      $3 #193  ~12 marginalia       51.29°C 🔥  991‰
      $4 #204   ~5 bookplate        49.02°C 🥵  986‰
      $5 #195  ~11 parchment        46.57°C 🥵  971‰
      $6 #198   ~8 antiquarian      45.06°C 🥵  961‰
      $7 #203   ~6 bibliographic    43.32°C 🥵  942‰
      $8  #79  ~24 poetry           42.43°C 🥵  929‰
      $9  #16  ~29 masterpiece      41.38°C 🥵  920‰
     $10  #76  ~25 verse            40.09°C 🥵  900‰
     $11 #197   ~9 scriptorium      39.18°C 😎  892‰
     $12  #87  ~23 sonnet           38.53°C 😎  882‰
     $32  #26      original         25.49°C 🥶
    $213 #106      versatility      -1.24°C 🧊

# cemantix.certitudes.org 🧩 #1348 🥳 289 ⏱️ 0:02:43.696313

🤔 290 attempts
📜 1 sessions
🫧 13 chat sessions
⁉️ 87 chat prompts
🤖 87 gemma3:latest replies
🔥   3 🥵   6 😎  57 🥶 140 🧊  83

      $1 #290   ~1 allocation        100.00°C 🥳 1000‰
      $2 #289   ~2 versement          48.65°C 🔥  996‰
      $3 #275  ~10 indemnité          47.95°C 🔥  993‰
      $4 #268  ~12 indemnisation      44.80°C 🔥  990‰
      $5 #284   ~5 rémunération       42.20°C 🥵  982‰
      $6 #261  ~15 compensation       41.44°C 🥵  980‰
      $7 #287   ~3 rémunérer          38.38°C 🥵  970‰
      $8 #146  ~57 condition          37.83°C 🥵  967‰
      $9 #148  ~56 contrat            35.86°C 🥵  943‰
     $10 #142  ~59 dispositif         33.20°C 🥵  913‰
     $11 #223  ~29 décret             30.71°C 😎  869‰
     $12 #217  ~32 attestation        29.82°C 😎  851‰
     $68 #248      impératif          18.02°C 🥶
    $208 #255      repère             -0.11°C 🧊
