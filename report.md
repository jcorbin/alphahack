# 2025-12-10

- 🔗 spaceword.org 🧩 2025-12-09 🏁 score 2173 ranked 6.1% 21/344 ⏱️ 1:21:02.782405
- 🔗 alfagok.diginaut.net 🧩 #403 🥳 15 ⏱️ 0:01:02.390479
- 🔗 alphaguess.com 🧩 #869 🥳 18 ⏱️ 0:00:36.279121
- 🔗 squareword.org 🧩 #1409 🥳 7 ⏱️ 0:02:13.568818
- 🔗 dictionary.com hurdle 🧩 #1439 😦 17 ⏱️ 0:04:56.793501
- 🔗 dontwordle.com 🧩 #1296 🥳 6 ⏱️ 0:01:58.736333
- 🔗 cemantle.certitudes.org 🧩 #1346 🥳 110 ⏱️ 0:01:11.486655
- 🔗 cemantix.certitudes.org 🧩 #1379 🥳 138 ⏱️ 0:01:30.761316

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














# spaceword.org 🧩 2025-12-09 🏁 score 2173 ranked 6.1% 21/344 ⏱️ 1:21:02.782405

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 21/344

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ Z E D _ _ _   
      _ _ _ _ _ Q _ _ _ _   
      _ _ _ _ T U G _ _ _   
      _ _ _ _ H I _ _ _ _   
      _ _ _ _ E N _ _ _ _   
      _ _ _ _ N O O _ _ _   
      _ _ _ _ A X E _ _ _   
      _ _ _ _ G _ _ _ _ _   
      _ _ _ _ E T A _ _ _   


# alfagok.diginaut.net 🧩 #403 🥳 15 ⏱️ 0:01:02.390479

🤔 15 attempts
📜 2 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+24912  [ 24912] bad       q4  ? after
    @+37366  [ 37366] bescherm  q5  ? after
    @+43072  [ 43072] bij       q6  ? after
    @+43450  [ 43450] bijgebouw q10 ? after
    @+43640  [ 43640] bijklank  q11 ? after
    @+43683  [ 43683] bijl      q12 ? after
    @+43758  [ 43758] bijltje   q13 ? after
    @+43778  [ 43778] bijna     q14 ? it
    @+43778  [ 43778] bijna     done. it
    @+43830  [ 43830] bijplaats q9  ? before
    @+44589  [ 44589] binnen    q8  ? before
    @+46460  [ 46460] blief     q7  ? before
    @+49851  [ 49851] boks      q3  ? before
    @+99760  [ 99760] ex        q2  ? before
    @+199845 [199845] lijm      q0  ? after
    @+199845 [199845] lijm      q1  ? before

# alphaguess.com 🧩 #869 🥳 18 ⏱️ 0:00:36.279121

🤔 18 attempts
📜 1 sessions

    @        [     0] aa       
    @+1      [     1] aah      
    @+2      [     2] aahed    
    @+3      [     3] aahing   
    @+98225  [ 98225] mach     q0  ? after
    @+122110 [122110] par      q3  ? after
    @+128372 [128372] place    q5  ? after
    @+129819 [129819] pol      q7  ? after
    @+130641 [130641] pop      q8  ? after
    @+130642 [130642] popcorn  q17 ? it
    @+130642 [130642] popcorn  done. it
    @+130643 [130643] popcorns q16 ? before
    @+130644 [130644] pope     q15 ? before
    @+130653 [130653] popinjay q14 ? before
    @+130665 [130665] popover  q13 ? before
    @+130688 [130688] poppling q12 ? before
    @+130735 [130735] populist q11 ? before
    @+130833 [130833] port     q10 ? before
    @+131028 [131028] post     q9  ? before
    @+131496 [131496] pots     q6  ? before
    @+134641 [134641] prog     q4  ? before
    @+147330 [147330] rho      q1  ? b/
    @+147330 [147330] rho      q2  ? before

# squareword.org 🧩 #1409 🥳 7 ⏱️ 0:02:13.568818

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C H A S M
    L A N C E
    A L T A R
    S L I N G
    P O S S E

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1439 😦 17 ⏱️ 0:04:56.793501

📜 1 sessions
💰 score: 4950

    3/6
    REAPS ⬜🟨⬜🟨🟨
    SPELT 🟩🟩🟨⬜⬜
    SPIKE 🟩🟩🟩🟩🟩
    3/6
    SPIKE 🟩🟨⬜⬜🟨
    SETUP 🟩🟨🟨⬜🟨
    SLEPT 🟩🟩🟩🟩🟩
    5/6
    SLEPT ⬜⬜🟨⬜⬜
    GRADE ⬜🟨⬜⬜🟨
    BONER 🟨⬜⬜🟩🟩
    UMBER ⬜🟩🟩🟩🟩
    EMBER 🟩🟩🟩🟩🟩
    4/6
    EMBER 🟨⬜⬜⬜⬜
    VEALS ⬜🟨🟨🟩⬜
    ANGLE 🟩⬜🟨🟩🟩
    AGILE 🟩🟩🟩🟩🟩
    Final 2/2
    MUNCH 🟨🟩⬜⬜⬜
    FUZZY ⬜🟩⬜⬜🟩
    FAIL: DUMMY

# dontwordle.com 🧩 #1296 🥳 6 ⏱️ 0:01:58.736333

📜 1 sessions
💰 score: 108

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:ZANZA n n n n n remain:5808
    ⬜⬜⬜⬜⬜ tried:ESSES n n n n n remain:1158
    ⬜⬜⬜⬜⬜ tried:IODID n n n n n remain:172
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:62
    ⬜🟩⬜⬜⬜ tried:JUGUM n Y n n n remain:21
    ⬜🟩⬜⬜🟩 tried:BUBBY n Y n n Y remain:12

    Undos used: 5

      12 words remaining
    x 9 unused letters
    = 108 total score

# cemantle.certitudes.org 🧩 #1346 🥳 110 ⏱️ 0:01:11.486655

🤔 111 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 23 chat prompts
🤖 23 falcon3:10b replies
😱  1 🔥  3 🥵  5 😎 28 🥶 70 🧊  3

      $1 #111   ~1 forecast         100.00°C 🥳 1000‰
      $2  #29  ~33 forecasting       71.66°C 😱  999‰
      $3  #88   ~9 estimate          62.73°C 🔥  997‰
      $4  #43  ~26 projection        62.64°C 🔥  996‰
      $5  #39  ~28 prediction        62.21°C 🔥  995‰
      $6 #103   ~3 fiscal            38.81°C 🥵  981‰
      $7 #108   ~2 contraction       36.15°C 🥵  972‰
      $8  #30  ~32 growth            36.00°C 🥵  971‰
      $9  #45  ~24 sales             31.78°C 🥵  931‰
     $10  #35  ~31 estimation        30.47°C 🥵  910‰
     $11  #67  ~16 scenario          28.61°C 😎  876‰
     $12  #21  ~36 demand            27.96°C 😎  863‰
     $39  #92      guess             17.64°C 🥶
    $109  #51      behavior          -1.64°C 🧊

# cemantix.certitudes.org 🧩 #1379 🥳 138 ⏱️ 0:01:30.761316

🤔 139 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 23 chat prompts
🤖 23 falcon3:10b replies
🥵   2 😎  15 🥶 107 🧊  14

      $1 #139   ~1 psychologique     100.00°C 🥳 1000‰
      $2  #15  ~18 physique           51.30°C 🥵  989‰
      $3  #58  ~13 corporel           44.04°C 🥵  955‰
      $4  #91   ~8 anxiété            39.87°C 😎  895‰
      $5  #93   ~6 dépression         38.85°C 😎  877‰
      $6  #53  ~15 résilience         34.87°C 😎  751‰
      $7  #92   ~7 douleur            34.07°C 😎  703‰
      $8  #86  ~11 maladie            32.43°C 😎  594‰
      $9  #89  ~10 guérison           32.24°C 😎  577‰
     $10  #99   ~5 biologique         32.20°C 😎  574‰
     $11 #107   ~3 nutritionnel       31.09°C 😎  487‰
     $12 #105   ~4 immunitaire        29.31°C 😎  307‰
     $19  #26      tension            26.24°C 🥶
    $126  #27      centre             -0.12°C 🧊
