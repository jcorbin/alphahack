# 2025-12-15

- 🔗 spaceword.org 🧩 2025-12-14 🏁 score 2173 ranked 16.8% 54/321 ⏱️ 1:28:37.839955
- 🔗 alfagok.diginaut.net 🧩 #408 🥳 11 ⏱️ 0:00:49.991828
- 🔗 alphaguess.com 🧩 #874 🥳 16 ⏱️ 0:00:32.358111
- 🔗 squareword.org 🧩 #1414 🥳 7 ⏱️ 0:02:21.463665
- 🔗 dictionary.com hurdle 🧩 #1444 🥳 17 ⏱️ 0:03:29.241636
- 🔗 dontwordle.com 🧩 #1301 🥳 6 ⏱️ 0:02:10.092335
- 🔗 cemantle.certitudes.org 🧩 #1351 🥳 320 ⏱️ 0:04:05.019409
- 🔗 cemantix.certitudes.org 🧩 #1384 🥳 288 ⏱️ 0:23:29.513141

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



















# spaceword.org 🧩 2025-12-14 🏁 score 2173 ranked 16.8% 54/321 ⏱️ 1:28:37.839955

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 54/321

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ R E S _ _ _   
      _ _ _ _ _ _ E _ _ _   
      _ _ _ _ _ R E _ _ _   
      _ _ _ _ J E T _ _ _   
      _ _ _ _ _ A H _ _ _   
      _ _ _ _ _ W E _ _ _   
      _ _ _ _ H A _ _ _ _   
      _ _ _ _ O K E _ _ _   
      _ _ _ _ M E L _ _ _   


# alfagok.diginaut.net 🧩 #408 🥳 11 ⏱️ 0:00:49.991828

🤔 11 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199839 [199839] lijm      q0  ? after
    @+299764 [299764] schub     q1  ? after
    @+311934 [311934] spier     q4  ? after
    @+314643 [314643] st        q5  ? after
    @+316858 [316858] start     q7  ? after
    @+318137 [318137] stem      q8  ? after
    @+318568 [318568] ster      q10 ? it
    @+318568 [318568] ster      done. it
    @+319437 [319437] stik      q6  ? before
    @+324340 [324340] sub       q3  ? before
    @+349549 [349549] vakantie  q2  ? before

# alphaguess.com 🧩 #874 🥳 16 ⏱️ 0:00:32.358111

🤔 16 attempts
📜 1 sessions

    @       [    0] aa           
    @+1     [    1] aah          
    @+2     [    2] aahed        
    @+3     [    3] aahing       
    @+23688 [23688] camp         q2  ? after
    @+25110 [25110] carp         q6  ? after
    @+25592 [25592] cat          q7  ? after
    @+25853 [25853] catfall      q9  ? after
    @+25985 [25985] cattish      q10 ? after
    @+26017 [26017] caudillismos q12 ? after
    @+26020 [26020] caudle       q14 ? after
    @+26022 [26022] caught       q15 ? it
    @+26022 [26022] caught       done. it
    @+26023 [26023] caul         q13 ? before
    @+26048 [26048] causal       q11 ? before
    @+26114 [26114] cavalier     q8  ? before
    @+26641 [26641] cep          q5  ? before
    @+29609 [29609] circuit      q4  ? before
    @+35531 [35531] convention   q3  ? before
    @+47387 [47387] dis          q1  ? before
    @+98225 [98225] mach         q0  ? before

# squareword.org 🧩 #1414 🥳 7 ⏱️ 0:02:21.463665

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    M E T A L
    A L O H A
    R O W E R
    S P E A K
    H E R D S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1444 🥳 17 ⏱️ 0:03:29.241636

📜 1 sessions
💰 score: 9900

    4/6
    DATES ⬜⬜🟨⬜⬜
    TULIP 🟨⬜⬜⬜⬜
    FORTY 🟩🟩🟩🟩⬜
    FORTH 🟩🟩🟩🟩🟩
    4/6
    FORTH ⬜⬜⬜⬜⬜
    ALIGN 🟨⬜⬜⬜⬜
    CAPES ⬜🟨⬜🟨🟨
    SUAVE 🟩🟩🟩🟩🟩
    4/6
    SUAVE ⬜⬜⬜⬜⬜
    IRONY ⬜⬜🟨⬜🟩
    GODLY ⬜🟩⬜⬜🟩
    COMFY 🟩🟩🟩🟩🟩
    3/6
    COMFY 🟨🟩⬜⬜⬜
    DOCKS ⬜🟩🟨⬜⬜
    NOTCH 🟩🟩🟩🟩🟩
    Final 2/2
    POUND ⬜🟩🟩🟩🟩
    BOUND 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1301 🥳 6 ⏱️ 0:02:10.092335

📜 1 sessions
💰 score: 42

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MUMMY n n n n n remain:7572
    ⬜⬜⬜⬜⬜ tried:ABACA n n n n n remain:3016
    ⬜⬜⬜⬜⬜ tried:JESSE n n n n n remain:330
    ⬜⬜⬜⬜⬜ tried:FIXIT n n n n n remain:57
    ⬜⬜🟩⬜⬜ tried:KNOWN n n Y n n remain:12
    ⬜🟨🟩⬜⬜ tried:GLOGG n m Y n n remain:6

    Undos used: 4

      6 words remaining
    x 7 unused letters
    = 42 total score

# cemantle.certitudes.org 🧩 #1351 🥳 320 ⏱️ 0:04:05.019409

🤔 321 attempts
📜 1 sessions
🫧 1 chat sessions
⁉️ 28 chat prompts
🤖 28 dolphin3:latest replies
🔥   4 🥵  13 😎  25 🥶 246 🧊  32

      $1 #321   ~1 saint          100.00°C 🥳 1000‰
      $2 #261  ~15 beatified       61.93°C 🔥  998‰
      $3 #256  ~17 canonization    58.92°C 🔥  996‰
      $4 #262  ~14 canonized       58.20°C 🔥  995‰
      $5 #255  ~18 martyr          54.83°C 🔥  991‰
      $6 #317   ~2 pope            53.29°C 🥵  988‰
      $7 #257  ~16 beatification   51.70°C 🥵  985‰
      $8 #203  ~27 basilica        48.55°C 🥵  970‰
      $9 #163  ~40 shrine          47.86°C 🥵  964‰
     $10 #274   ~9 intercession    47.55°C 🥵  963‰
     $11 #175  ~36 consecrated     47.34°C 🥵  961‰
     $19 #169  ~38 pilgrimage      41.88°C 😎  891‰
     $44 #182      baptismal       30.07°C 🥶
    $290  #79      orbital         -0.11°C 🧊

# cemantix.certitudes.org 🧩 #1384 🥳 288 ⏱️ 0:23:29.513141

🤔 289 attempts
📜 2 sessions
🫧 9 chat sessions
⁉️ 91 chat prompts
🤖 57 falcon3:10b replies
🤖 34 dolphin3:latest replies
😱   1 🔥   3 🥵  17 😎  66 🥶 170 🧊  31

      $1 #289   ~1 destin          100.00°C 🥳 1000‰
      $2 #260  ~14 tragique         56.58°C 😱  999‰
      $3 #272   ~9 malheur          49.09°C 🔥  996‰
      $4  #72  ~81 amour            47.66°C 🔥  992‰
      $5 #262  ~13 tragédie         46.96°C 🔥  991‰
      $6 #285   ~4 désespoir        45.95°C 🥵  987‰
      $7 #264  ~12 âme              45.29°C 🥵  986‰
      $8  #47  ~88 rêve             45.18°C 🥵  984‰
      $9 #100  ~70 éternel          44.62°C 🥵  982‰
     $10 #126  ~61 éternité         43.77°C 🥵  977‰
     $11 #227  ~27 tourment         42.06°C 🥵  968‰
     $23 #168  ~45 mystérieux       37.70°C 😎  887‰
     $89 #275      malchance        28.32°C 🥶
    $259   #8      fête             -0.02°C 🧊
