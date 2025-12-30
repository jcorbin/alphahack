# 2025-12-31

- 🔗 spaceword.org 🧩 2025-12-30 🏁 score 2173 ranked 10.7% 37/347 ⏱️ 0:12:56.676461
- 🔗 alfagok.diginaut.net 🧩 #424 🥳 13 ⏱️ 0:00:57.823169
- 🔗 alphaguess.com 🧩 #890 🥳 17 ⏱️ 0:00:48.127158
- 🔗 dontwordle.com 🧩 #1317 🥳 6 ⏱️ 0:04:05.061371
- 🔗 dictionary.com hurdle 🧩 #1460 🥳 17 ⏱️ 0:02:57.560319
- 🔗 Quordle Classic 🧩 #1437 🥳 score:19 ⏱️ 0:02:44.279279
- 🔗 Octordle Classic 🧩 #1437 😦 score:66 ⏱️ 0:05:41.598725
- 🔗 squareword.org 🧩 #1430 🥳 7 ⏱️ 0:02:41.350731
- 🔗 cemantle.certitudes.org 🧩 #1367 🥳 121 ⏱️ 0:07:42.761668
- 🔗 cemantix.certitudes.org 🧩 #1400 🥳 476 ⏱️ 0:24:59.480179
- 🔗 Quordle Rescue 🧩 #51 🥳 score:26 ⏱️ 0:01:39.703252
- 🔗 Quordle Sequence 🧩 #1437 🥳 score:25 ⏱️ 0:02:21.308955
- 🔗 Quordle Extreme 🧩 #520 😦 score:25 ⏱️ 0:02:49.911537
- 🔗 Octordle Rescue 🧩 #1437 🥳 score:8 ⏱️ 0:04:39.254972
- 🔗 Octordle Sequence 🧩 #1437 🥳 score:67 ⏱️ 0:04:07.358881
- 🔗 Octordle Extreme 🧩 #1437 🥳 score:54 ⏱️ 0:04:44.498407

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






# spaceword.org 🧩 2025-12-30 🏁 score 2173 ranked 10.7% 37/347 ⏱️ 0:12:56.676461

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 37/347

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ J _ G _ _ A A _ Z   
      _ E _ E M O T I V E   
      _ T U Y E R E S _ N   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #424 🥳 13 ⏱️ 0:00:57.823169

🤔 13 attempts
📜 1 sessions

    @        [     0] &-teken       
    @+1      [     1] &-tekens      
    @+2      [     2] -cijferig     
    @+3      [     3] -e-mail       
    @+49849  [ 49849] boks          q2  ? after
    @+50545  [ 50545] bonnen        q8  ? after
    @+50827  [ 50827] boom          q9  ? after
    @+51034  [ 51034] boor          q10 ? after
    @+51145  [ 51145] booronderzoek q11 ? after
    @+51193  [ 51193] boos          q12 ? it
    @+51193  [ 51193] boos          done. it
    @+51256  [ 51256] boots         q7  ? before
    @+52691  [ 52691] bouw          q6  ? before
    @+55941  [ 55941] bron          q5  ? before
    @+62288  [ 62288] cement        q4  ? before
    @+74762  [ 74762] dc            q3  ? before
    @+99758  [ 99758] ex            q1  ? before
    @+199833 [199833] lijm          q0  ? before

# alphaguess.com 🧩 #890 🥳 17 ⏱️ 0:00:48.127158

🤔 17 attempts
📜 1 sessions

    @       [    0] aa              
    @+1     [    1] aah             
    @+2     [    2] aahed           
    @+3     [    3] aahing          
    @+23687 [23687] camp            q2  ? after
    @+29608 [29608] circuit         q4  ? after
    @+32557 [32557] color           q5  ? after
    @+32827 [32827] come            q8  ? after
    @+32868 [32868] comeuppances    q10 ? after
    @+32876 [32876] comfort         q12 ? after
    @+32877 [32877] comfortable     q16 ? it
    @+32877 [32877] comfortable     done. it
    @+32878 [32878] comfortableness q15 ? before
    @+32879 [32879] comfortably     q14 ? before
    @+32882 [32882] comforters      q13 ? before
    @+32888 [32888] comfreys        q11 ? before
    @+32908 [32908] comm            q9  ? before
    @+33114 [33114] common          q7  ? before
    @+33705 [33705] con             q6  ? before
    @+35530 [35530] convention      q3  ? before
    @+47386 [47386] dis             q1  ? before
    @+98224 [98224] mach            q0  ? before

# dontwordle.com 🧩 #1317 🥳 6 ⏱️ 0:04:05.061371

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:8089
    ⬜⬜⬜⬜⬜ tried:GOOKS n n n n n remain:1914
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:741
    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:237
    ⬜⬜🟩⬜⬜ tried:EMEER n n Y n n remain:5
    ⬜🟨🟩⬜⬜ tried:FAENA n m Y n n remain:1

    Undos used: 2

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1460 🥳 17 ⏱️ 0:02:57.560319

📜 1 sessions
💰 score: 9900

    3/6
    TASER ⬜🟨🟨⬜⬜
    CLAMS ⬜⬜🟩⬜🟨
    SHANK 🟩🟩🟩🟩🟩
    4/6
    SHANK ⬜⬜⬜⬜⬜
    OLDER ⬜🟩🟨🟨⬜
    GLIDE ⬜🟩⬜🟩🟩
    ELUDE 🟩🟩🟩🟩🟩
    5/6
    ELUDE ⬜🟩⬜⬜🟩
    ALONE ⬜🟩🟩⬜🟩
    CLOZE ⬜🟩🟩⬜🟩
    GLOBE 🟩🟩🟩⬜🟩
    GLOVE 🟩🟩🟩🟩🟩
    4/6
    GLOVE ⬜🟨🟨🟨🟨
    LOVES 🟨🟩🟩🟩⬜
    NOVEL ⬜🟩🟩🟩🟩
    HOVEL 🟩🟩🟩🟩🟩
    Final 1/2
    QUOTE 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1437 🥳 score:19 ⏱️ 0:02:44.279279

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. ADMIN attempts:4 score:4
2. YIELD attempts:7 score:7
3. STEEL attempts:3 score:3
4. FLICK attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1437 😦 score:66 ⏱️ 0:05:41.598725

📜 1 sessions

Octordle Classic

1. WAXEN attempts:10 score:10
2. MAM_A -BCDEFGHIKLNOPQRSTUVWXY attempts:13 score:-1
3. APTLY attempts:4 score:4
4. RANCH attempts:8 score:8
5. GUIDE attempts:12 score:12
6. SHARK attempts:7 score:7
7. COUNT attempts:5 score:5
8. QUACK attempts:6 score:6

# squareword.org 🧩 #1430 🥳 7 ⏱️ 0:02:41.350731

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A D A P T
    D E B A R
    O C H R E
    P R O S E
    T Y R E S

# cemantle.certitudes.org 🧩 #1367 🥳 121 ⏱️ 0:07:42.761668

🤔 122 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 14 chat prompts
🤖 14 dolphin3:latest replies
🔥   1 🥵   1 😎  17 🥶 101 🧊   1

      $1 #122   ~1 urgent          100.00°C 🥳 1000‰
      $2 #103   ~8 emergency        46.86°C 🔥  994‰
      $3 #105   ~6 crisis           30.01°C 🥵  910‰
      $4  #69  ~17 vulnerable       29.70°C 😎  899‰
      $5 #104   ~7 ambulance        28.90°C 😎  875‰
      $6 #106   ~5 evacuation       28.58°C 😎  867‰
      $7  #71  ~16 assistance       27.99°C 😎  853‰
      $8 #113   ~3 medical          27.52°C 😎  835‰
      $9  #63  ~18 endangered       26.77°C 😎  812‰
     $10  #75  ~15 critically       25.42°C 😎  730‰
     $11  #77  ~14 ecological       24.99°C 😎  702‰
     $12 #101   ~9 care             24.61°C 😎  651‰
     $21 #109      help             20.10°C 🥶
    $122   #6      motorcycle       -1.82°C 🧊

# cemantix.certitudes.org 🧩 #1400 🥳 476 ⏱️ 0:24:59.480179

🤔 477 attempts
📜 1 sessions
🫧 31 chat sessions
⁉️ 134 chat prompts
🤖 97 dolphin3:latest replies
🤖 1 falcon3:1b replies
🤖 14 llama3.3:latest replies
🤖 14 falcon3:10b replies
🤖 6 gemma3:27b replies
😱   1 🔥   4 🥵   8 😎  58 🥶 329 🧊  76

      $1 #477   ~1 surplus              100.00°C 🥳 1000‰
      $2 #469   ~4 excédent              57.87°C 😱  999‰
      $3 #306  ~40 quantité              45.12°C 🔥  996‰
      $4 #460   ~8 bénéfice              44.92°C 🔥  995‰
      $5 #464   ~6 profit                44.35°C 🔥  994‰
      $6 #336  ~35 somme                 43.31°C 🔥  993‰
      $7 #339  ~34 dépense               37.45°C 🥵  958‰
      $8 #427  ~13 revenu                36.56°C 🥵  950‰
      $9 #345  ~31 compensation          35.28°C 🥵  935‰
     $10 #359  ~28 augmentation          35.21°C 🥵  934‰
     $11 #360  ~27 accumulation          34.93°C 🥵  921‰
     $15 #294  ~45 coût                  33.18°C 😎  871‰
     $73 #465      bénéficiaire          23.49°C 🥶
    $402 #254      démocratie            -0.05°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #51 🥳 score:26 ⏱️ 0:01:39.703252

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. SLURP attempts:6 score:6
2. BOOTH attempts:5 score:5
3. PRONE attempts:7 score:7
4. SCONE attempts:8 score:8

# [Quordle Sequence](m-w.com/games/quordle/#/sequence) 🧩 #1437 🥳 score:25 ⏱️ 0:02:21.308955

📜 2 sessions

Quordle Sequence m-w.com/games/quordle/

1. ALLEY attempts:4 score:4
2. LLAMA attempts:6 score:6
3. CANNY attempts:7 score:7
4. MEDAL attempts:8 score:8

# [Quordle Extreme](m-w.com/games/quordle/#/extreme) 🧩 #520 😦 score:25 ⏱️ 0:02:49.911537

📜 1 sessions

Quordle Extreme m-w.com/games/quordle/

1. HALAL attempts:8 score:8
2. _O___ ~AGN -CDEHIKLMRSUVY A:1 attempts:8 score:-1
3. DRIVE attempts:5 score:5
4. LUCRE attempts:4 score:4

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1437 🥳 score:8 ⏱️ 0:04:39.254972

📜 3 sessions

Octordle Rescue

1. ZEBRA attempts:12 score:12
2. TROLL attempts:10 score:10
3. VIOLA attempts:11 score:11
4. TIMID attempts:9 score:9
5. SOUTH attempts:6 score:6
6. GAZER attempts:13 score:13
7. HEATH attempts:8 score:8
8. TWANG attempts:7 score:7

# [Octordle Sequence](britannica.com/games/octordle/daily-sequence) 🧩 #1437 🥳 score:67 ⏱️ 0:04:07.358881

📜 1 sessions

Octordle Sequence

1. RAINY attempts:3 score:3
2. SAUCY attempts:5 score:5
3. SPRIG attempts:6 score:6
4. WAGON attempts:7 score:7
5. FOIST attempts:10 score:10
6. GULCH attempts:11 score:11
7. HELIX attempts:12 score:12
8. THYME attempts:13 score:13

# [Octordle Extreme](britannica.com/games/octordle/extreme) 🧩 #1437 🥳 score:54 ⏱️ 0:04:44.498407

📜 1 sessions

Octordle Extreme

1. EXIST attempts:10 score:10
2. RIPEN attempts:3 score:3
3. UNZIP attempts:5 score:5
4. CHIRP attempts:4 score:4
5. OUTGO attempts:8 score:8
6. BEERY attempts:11 score:11
7. AZURE attempts:6 score:6
8. BIDET attempts:7 score:7
