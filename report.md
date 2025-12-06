# 2025-12-07

- 🔗 spaceword.org 🧩 2025-12-06 🏁 score 2173 ranked 4.0% 13/329 ⏱️ 2:06:11.518436
- 🔗 alfagok.diginaut.net 🧩 #400 🥳 30 ⏱️ 0:01:38.864173
- 🔗 alphaguess.com 🧩 #866 🥳 15 ⏱️ 0:00:37.042262
- 🔗 squareword.org 🧩 #1406 🥳 8 ⏱️ 0:02:30.775052
- 🔗 dictionary.com hurdle 🧩 #1436 🥳 15 ⏱️ 0:03:07.427608
- 🔗 dontwordle.com 🧩 #1293 🥳 6 ⏱️ 0:01:21.615840
- 🔗 cemantle.certitudes.org 🧩 #1343 🥳 602 ⏱️ 0:16:13.793625
- 🔗 cemantix.certitudes.org 🧩 #1376 🥳 523 ⏱️ 3:13:41.637387

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











# spaceword.org 🧩 2025-12-06 🏁 score 2173 ranked 4.0% 13/329 ⏱️ 2:06:11.518436

📜 6 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 13/329

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ W _ F _ _ _   
      _ _ _ _ A _ L _ _ _   
      _ _ _ _ L E U _ _ _   
      _ _ _ _ E G O _ _ _   
      _ _ _ _ _ O R _ _ _   
      _ _ _ _ _ T I _ _ _   
      _ _ _ _ H I D _ _ _   
      _ _ _ _ _ Z _ _ _ _   
      _ _ _ _ J E U _ _ _   


# alfagok.diginaut.net 🧩 #400 🥳 30 ⏱️ 0:01:38.864173

🤔 30 attempts
📜 3 sessions

    @        [     0] &-teken           
    @+1      [     1] &-tekens          
    @+2      [     2] -cijferig         
    @+3      [     3] -e-mail           
    @+199845 [199845] lijm              q0  ? after
    @+223807 [223807] molest            q3  ? after
    @+226686 [226686] museum            q19 ? after
    @+227779 [227779] na                q20 ? after
    @+227954 [227954] naam              q23 ? after
    @+228020 [228020] naamsverwisseling q26 ? after
    @+228038 [228038] naar              q27 ? after
    @+228061 [228061] naars             q28 ? after
    @+228070 [228070] naast             q29 ? it
    @+228070 [228070] naast             done. it
    @+228085 [228085] nababbel          q24 ? before
    @+228219 [228219] nacht             q22 ? before
    @+228696 [228696] nagel             q21 ? before
    @+229663 [229663] natuur            q18 ? before
    @+235781 [235781] odeur             q15 ? after
    @+235781 [235781] odeur             q16 ? .
    @+235790 [235790] odium             q17 ? before
    @+247763 [247763] op                q2  ? before
    @+299770 [299770] schub             q1  ? before

# alphaguess.com 🧩 #866 🥳 15 ⏱️ 0:00:37.042262

🤔 15 attempts
📜 1 sessions

    @        [     0] aa     
    @+1      [     1] aah    
    @+2      [     2] aahed  
    @+3      [     3] aahing 
    @+98225  [ 98225] mach   q0  ? after
    @+104173 [104173] miri   q4  ? after
    @+107129 [107129] mort   q5  ? after
    @+108589 [108589] mus    q6  ? after
    @+109356 [109356] nail   q7  ? after
    @+109743 [109743] nation q8  ? after
    @+109934 [109934] nazi   q9  ? after
    @+109944 [109944] ne     q10 ? after
    @+109961 [109961] nears  q13 ? after
    @+109968 [109968] neat   q14 ? it
    @+109968 [109968] neat   done. it
    @+109984 [109984] neb    q12 ? before
    @+110036 [110036] neck   q11 ? before
    @+110130 [110130] need   q3  ? before
    @+122110 [122110] par    q2  ? before
    @+147330 [147330] rho    q1  ? before

# squareword.org 🧩 #1406 🥳 8 ⏱️ 0:02:30.775052

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S A L A D
    P R I D E
    A G A I N
    C O R E S
    E N S U E

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1436 🥳 15 ⏱️ 0:03:07.427608

📜 1 sessions
💰 score: 10100

    5/6
    NEARS ⬜⬜⬜🟨🟨
    HURST ⬜⬜🟨🟩⬜
    PROSY ⬜🟩⬜🟩⬜
    BRISK ⬜🟩🟩🟩🟩
    FRISK 🟩🟩🟩🟩🟩
    3/6
    FRISK ⬜⬜🟩⬜⬜
    CLINE 🟨⬜🟩⬜🟨
    EDICT 🟩🟩🟩🟩🟩
    3/6
    EDICT ⬜⬜⬜⬜⬜
    FOURS ⬜⬜⬜🟨🟨
    GRASP 🟩🟩🟩🟩🟩
    3/6
    GRASP 🟨⬜⬜🟨⬜
    STUNG 🟨⬜🟨⬜🟨
    BOGUS 🟩🟩🟩🟩🟩
    Final 1/2
    BOSOM 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1293 🥳 6 ⏱️ 0:01:21.615840

📜 1 sessions
💰 score: 18

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:VERVE n n n n n remain:5059
    ⬜⬜⬜⬜⬜ tried:PAPAW n n n n n remain:1968
    ⬜⬜⬜⬜⬜ tried:JUKUS n n n n n remain:472
    ⬜⬜⬜⬜⬜ tried:MYTHY n n n n n remain:90
    ⬜🟩⬜⬜⬜ tried:BIFID n Y n n n remain:5
    ⬜🟩🟩🟨⬜ tried:NINON n Y Y m n remain:3

    Undos used: 3

      3 words remaining
    x 6 unused letters
    = 18 total score

# cemantle.certitudes.org 🧩 #1343 🥳 602 ⏱️ 0:16:13.793625

🤔 603 attempts
📜 1 sessions
🫧 36 chat sessions
⁉️ 176 chat prompts
🤖 56 falcon3:10b replies
🤖 120 wizardlm2:latest replies
😱   1 🔥   3 🥵  25 😎  79 🥶 473 🧊  21

      $1 #603   ~1 geography          100.00°C 🥳 1000‰
      $2 #584  ~11 geographic          62.76°C 😱  999‰
      $3 #558  ~16 demography          51.32°C 🔥  996‰
      $4 #598   ~4 topography          51.29°C 🔥  995‰
      $5   #3 ~109 mathematics         47.80°C 🔥  991‰
      $6  #12 ~107 calculus            45.12°C 🥵  987‰
      $7 #308  ~68 linguistics         45.11°C 🥵  986‰
      $8 #588   ~9 cartography         43.71°C 🥵  982‰
      $9 #551  ~20 ecology             43.50°C 🥵  979‰
     $10 #547  ~23 biology             41.49°C 🥵  975‰
     $11 #546  ~24 science             41.36°C 🥵  974‰
     $31 #103  ~94 physics             34.13°C 😎  897‰
    $110 #580      demographer         23.49°C 🥶
    $583 #475      circular            -0.44°C 🧊

# cemantix.certitudes.org 🧩 #1376 🥳 523 ⏱️ 3:13:41.637387

🤔 524 attempts
📜 1 sessions
🫧 40 chat sessions
⁉️ 200 chat prompts
🤖 63 falcon3:10b replies
🤖 137 wizardlm2:latest replies
😱   1 🔥   2 🥵  24 😎 117 🥶 326 🧊  53

      $1 #524   ~1 acceptable         100.00°C 🥳 1000‰
      $2 #268  ~97 raisonnable         63.66°C 😱  999‰
      $3 #471  ~24 suffisant           59.39°C 🔥  998‰
      $4 #469  ~25 insuffisant         52.23°C 🔥  992‰
      $5 #452  ~29 considérer          50.61°C 🥵  987‰
      $6 #260 ~102 nécessaire          49.61°C 🥵  983‰
      $7 #476  ~23 suffisamment        49.46°C 🥵  982‰
      $8 #354  ~64 raisonnablement     49.06°C 🥵  978‰
      $9 #277  ~91 évident             48.36°C 🥵  975‰
     $10 #289  ~86 viable              47.68°C 🥵  971‰
     $11 #411  ~42 nécessairement      47.33°C 🥵  970‰
     $29 #386  ~52 opportun            41.59°C 😎  892‰
    $146 #292      arbitrage           27.26°C 🥶
    $472 #181      approbatif          -0.07°C 🧊
