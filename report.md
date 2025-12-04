# 2025-12-05

- 🔗 spaceword.org 🧩 2025-12-04 🏁 score 2173 ranked 9.1% 31/341 ⏱️ 2:32:35.500747
- 🔗 alfagok.diginaut.net 🧩 #398 🥳 17 ⏱️ 0:00:42.658381
- 🔗 alphaguess.com 🧩 #864 🥳 15 ⏱️ 0:00:29.099051
- 🔗 squareword.org 🧩 #1404 🥳 7 ⏱️ 0:01:47.047505
- 🔗 dictionary.com hurdle 🧩 #1434 🥳 14 ⏱️ 0:02:53.524029
- 🔗 dontwordle.com 🧩 #1291 🥳 6 ⏱️ 0:01:06.797176
- 🔗 cemantle.certitudes.org 🧩 #1341 🥳 197 ⏱️ 0:12:05.724452
- 🔗 cemantix.certitudes.org 🧩 #1374 🥳 153 ⏱️ 0:11:20.788921

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









# spaceword.org 🧩 2025-12-04 🏁 score 2173 ranked 9.1% 31/341 ⏱️ 2:32:35.500747

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 31/341

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ V _ _ _ _   
      _ _ _ _ L I T _ _ _   
      _ _ _ _ _ D O _ _ _   
      _ _ _ _ S E W _ _ _   
      _ _ _ _ A _ A _ _ _   
      _ _ _ _ J U G _ _ _   
      _ _ _ _ O P E _ _ _   
      _ _ _ _ U _ _ _ _ _   
      _ _ _ _ S E C _ _ _   


# alfagok.diginaut.net 🧩 #398 🥳 17 ⏱️ 0:00:42.658381

🤔 17 attempts
📜 1 sessions

    @        [     0] &-teken                
    @+1      [     1] &-tekens               
    @+2      [     2] -cijferig              
    @+3      [     3] -e-mail                
    @+199846 [199846] lijm                   q0  ? after
    @+299783 [299783] schub                  q1  ? after
    @+349569 [349569] vakantie               q2  ? after
    @+374313 [374313] vrij                   q3  ? after
    @+375758 [375758] vuur                   q7  ? after
    @+376152 [376152] waak                   q9  ? after
    @+376247 [376247] waar                   q11 ? after
    @+376261 [376261] waarborg               q13 ? after
    @+376273 [376273] waarborgmaatschappijen q14 ? after
    @+376279 [376279] waarborgstempels       q15 ? after
    @+376283 [376283] waard                  q16 ? it
    @+376283 [376283] waard                  done. it
    @+376285 [376285] waarde                 q12 ? before
    @+376349 [376349] waardering             q10 ? before
    @+376554 [376554] waarneming             q8  ? before
    @+377376 [377376] wandel                 q6  ? before
    @+380525 [380525] weer                   q5  ? before
    @+386854 [386854] wind                   q4  ? before

# alphaguess.com 🧩 #864 🥳 15 ⏱️ 0:00:29.099051

🤔 15 attempts
📜 1 sessions

    @        [     0] aa      
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98225  [ 98225] mach    q0  ? after
    @+147330 [147330] rho     q1  ? after
    @+159612 [159612] slug    q3  ? after
    @+165766 [165766] stint   q4  ? after
    @+168816 [168816] sulfur  q5  ? after
    @+169012 [169012] summer  q8  ? after
    @+169080 [169080] sun     q9  ? after
    @+169158 [169158] sunk    q10 ? after
    @+169175 [169175] sunn    q12 ? after
    @+169188 [169188] sunny   q13 ? after
    @+169194 [169194] sunrise q14 ? it
    @+169194 [169194] sunrise done. it
    @+169200 [169200] suns    q11 ? before
    @+169242 [169242] super   q7  ? before
    @+170370 [170370] sustain q6  ? before
    @+171930 [171930] tag     q2  ? before

# squareword.org 🧩 #1404 🥳 7 ⏱️ 0:01:47.047505

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S A L S A
    T R O L L
    R O Y A L
    I M A G E
    P A L S Y

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1434 🥳 14 ⏱️ 0:02:53.524029

📜 1 sessions
💰 score: 10200

    3/6
    LAMES ⬜🟨⬜⬜⬜
    ANDRO 🟨⬜⬜🟨⬜
    WRATH 🟩🟩🟩🟩🟩
    4/6
    WRATH ⬜⬜⬜⬜⬜
    NOISY 🟨⬜🟩⬜⬜
    BLIND ⬜⬜🟩🟨⬜
    KNIFE 🟩🟩🟩🟩🟩
    3/6
    KNIFE ⬜🟨⬜⬜🟨
    STENO 🟩⬜🟨🟨⬜
    SEDAN 🟩🟩🟩🟩🟩
    3/6
    SEDAN ⬜⬜⬜⬜⬜
    LYRIC 🟨⬜🟨🟩⬜
    BROIL 🟩🟩🟩🟩🟩
    Final 1/2
    TACKY 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1291 🥳 6 ⏱️ 0:01:06.797176

📜 1 sessions
💰 score: 30

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:BABKA n n n n n remain:5942
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:2905
    ⬜⬜⬜⬜⬜ tried:FUZZY n n n n n remain:1326
    ⬜⬜⬜⬜⬜ tried:CRWTH n n n n n remain:243
    ⬜🟨⬜⬜⬜ tried:JOMON n m n n n remain:17
    ⬜🟩🟩⬜⬜ tried:GLOGG n Y Y n n remain:6

    Undos used: 3

      6 words remaining
    x 5 unused letters
    = 30 total score

# cemantle.certitudes.org 🧩 #1341 🥳 197 ⏱️ 0:12:05.724452

🤔 198 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 36 chat prompts
🤖 36 mixtral:8x22b replies
🥵   1 😎  23 🥶 161 🧊  12

      $1 #198   ~1 ease               100.00°C 🥳 1000‰
      $2 #193   ~4 simplicity          33.78°C 😎  897‰
      $3 #190   ~5 simplified          29.03°C 😎  772‰
      $4 #129  ~16 speed               28.99°C 😎  771‰
      $5 #121  ~18 efficiency          28.78°C 😎  764‰
      $6 #179   ~6 streamlined         26.98°C 😎  672‰
      $7 #131  ~14 briskness           26.46°C 😎  631‰
      $8 #109  ~20 responsiveness      25.54°C 😎  558‰
      $9 #135  ~13 swiftness           25.42°C 😎  541‰
     $10 #197   ~2 uncomplicated       25.36°C 😎  535‰
     $11 #125  ~17 effectiveness       25.26°C 😎  525‰
     $12 #161   ~9 efficiently         25.16°C 😎  520‰
     $26 #149      productivity        21.47°C 🥶
    $187  #27      binocular           -0.26°C 🧊

# cemantix.certitudes.org 🧩 #1374 🥳 153 ⏱️ 0:11:20.788921

🤔 154 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 28 chat prompts
🤖 28 mixtral:8x22b replies
🔥  1 🥵  8 😎 25 🥶 97 🧊 22

      $1 #154   ~1 meurtrier        100.00°C 🥳 1000‰
      $2 #153   ~2 sanglant          59.18°C 🔥  997‰
      $3 #149   ~5 effroyable        49.92°C 🥵  979‰
      $4 #129  ~17 atroce            49.83°C 🥵  978‰
      $5 #147   ~6 cruel             45.84°C 🥵  965‰
      $6 #112  ~28 abominable        43.96°C 🥵  949‰
      $7 #141   ~9 impitoyable       43.93°C 🥵  947‰
      $8 #122  ~22 horrible          43.37°C 🥵  939‰
      $9 #124  ~20 impitoyablement   42.82°C 🥵  932‰
     $10 #102  ~33 dévastation       41.46°C 🥵  908‰
     $11 #111  ~29 brutal            40.52°C 😎  893‰
     $12 #145   ~7 monstrueux        40.21°C 😎  889‰
     $36  #64      ravin             26.80°C 🥶
    $133   #3      crayon            -0.16°C 🧊
