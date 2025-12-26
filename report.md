# 2025-12-27

- 🔗 spaceword.org 🧩 2025-12-26 🏁 score 2168 ranked 34.2% 108/316 ⏱️ 0:35:27.478865
- 🔗 alfagok.diginaut.net 🧩 #420 🥳 10 ⏱️ 0:00:32.926349
- 🔗 alphaguess.com 🧩 #886 🥳 18 ⏱️ 0:00:40.854424
- 🔗 dontwordle.com 🧩 #1313 😳 6 ⏱️ 0:07:44.734569
- 🔗 dictionary.com hurdle 🧩 #1456 🥳 19 ⏱️ 0:03:30.862380
- 🔗 Quordle Classic 🧩 #1433 🥳 score:24 ⏱️ 0:02:09.424637
- 🔗 Octordle Classic 🧩 #1433 🥳 score:53 ⏱️ 0:04:32.297379
- 🔗 squareword.org 🧩 #1426 🥳 8 ⏱️ 0:03:18.438840
- 🔗 cemantle.certitudes.org 🧩 #1363 🥳 99 ⏱️ 0:04:18.790991
- 🔗 cemantix.certitudes.org 🧩 #1396 🥳 100 ⏱️ 0:01:46.764994

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




# spaceword.org 🧩 2025-12-26 🏁 score 2168 ranked 34.2% 108/316 ⏱️ 0:35:27.478865

📜 5 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 108/316

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ L U D E _ _ _   
      _ _ _ _ _ _ X _ _ _   
      _ _ _ _ U _ H _ _ _   
      _ _ _ P R A O _ _ _   
      _ _ _ _ E _ R _ _ _   
      _ _ _ _ M U T _ _ _   
      _ _ _ Q I _ _ _ _ _   
      _ _ _ _ A J I _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #420 🥳 10 ⏱️ 0:00:32.926349

🤔 10 attempts
📜 1 sessions

    @        [     0] &-teken       >>> SEARCH
    @+1      [     1] &-tekens      
    @+2      [     2] -cijferig     
    @+3      [     3] -e-mail       
    @+199833 [199833] lijm          q0  ? after
    @+299755 [299755] schub         q1  ? after
    @+349540 [349540] vakantie      q2  ? after
    @+374284 [374284] vrij          q3  ? after
    @+386825 [386825] wind          q4  ? after
    @+387474 [387474] winter        q8  ? itr
    @+387474 [387474] winter        q9  ? it
    @+388415 [388415] woest         q7  ? before
    @+390034 [390034] wrik          q6  ? before
    @+393242 [393242] zelfmoord     q5  ? before
    @+399709 [399709] €50-biljetten <<< SEARCH

# alphaguess.com 🧩 #886 🥳 18 ⏱️ 0:00:40.854424

🤔 18 attempts
📜 1 sessions

    @        [     0] aa            >>> SEARCH
    @+1      [     1] aah           
    @+2      [     2] aahed         
    @+3      [     3] aahing        
    @+2802   [  2802] ag            q5  ? after
    @+3183   [  3183] agrochemicals q9  ? after
    @+3311   [  3311] air           q10 ? after
    @+3366   [  3366] airfreight    q12 ? after
    @+3392   [  3392] airline       q13 ? after
    @+3409   [  3409] airpark       q14 ? after
    @+3413   [  3413] airplay       q16 ? after
    @+3415   [  3415] airport       q17 ? it
    @+3417   [  3417] airpost       q15 ? before
    @+3425   [  3425] airs          q11 ? before
    @+3563   [  3563] alarm         q7  ? before
    @+4334   [  4334] alma          q6  ? before
    @+5876   [  5876] angel         q4  ? before
    @+11764  [ 11764] back          q3  ? before
    @+23687  [ 23687] camp          q2  ? before
    @+47386  [ 47386] dis           q1  ? before
    @+98224  [ 98224] mach          q0  ? before
    @+196536 [196536] zzz           <<< SEARCH

# dontwordle.com 🧩 #1313 😳 6 ⏱️ 0:07:44.734569

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:COOCH n n n n n remain:6849
    ⬜⬜⬜⬜⬜ tried:DEEDY n n n n n remain:2155
    ⬜⬜⬜⬜⬜ tried:SUNNS n n n n n remain:339
    ⬜⬜⬜⬜⬜ tried:GAZAR n n n n n remain:17
    ⬜🟨🟨⬜⬜ tried:VILLI n m m n n remain:3
    🟩🟩🟩🟩🟩 tried:BLIMP Y Y Y Y Y remain:0

    Undos used: 5

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1456 🥳 19 ⏱️ 0:03:30.862380

📜 1 sessions
💰 score: 970

    6/6
    RALES ⬜⬜🟩🟨⬜
    MELIC ⬜🟩🟩⬜⬜
    FELON ⬜🟩🟩⬜⬜
    VELDT ⬜🟩🟩⬜⬜
    BELLY ⬜🟩🟩🟩🟩
    JELLY 🟩🟩🟩🟩🟩
    5/6
    JELLY ⬜🟨⬜⬜⬜
    TORSE ⬜⬜⬜🟨🟨
    DINES ⬜⬜🟨🟩🟨
    ASHEN 🟩🟩⬜🟩🟩
    ASPEN 🟩🟩🟩🟩🟩
    3/6
    ASPEN 🟨⬜⬜⬜⬜
    CAROL ⬜🟨🟩🟨⬜
    FORAY 🟩🟩🟩🟩🟩
    4/6
    FORAY ⬜⬜🟨🟨⬜
    LASER ⬜🟩⬜⬜🟨
    RABID 🟩🟩🟩🟨⬜
    RABBI 🟩🟩🟩🟩🟩
    Final 1/2
    RENAL 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle) 🧩 #1433 🥳 score:24 ⏱️ 0:02:09.424637

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. FLAME attempts:5 score:5
2. SCOWL attempts:3 score:3
3. EMBER attempts:7 score:7
4. ROVER attempts:9 score:9

# [Octordle Classic](https://www.britannica.com/games/octordle/daily) 🧩 #1433 🥳 score:53 ⏱️ 0:04:32.297379

📜 1 sessions

Octordle Classic

1. VISTA attempts:7 score:7
2. GUARD attempts:8 score:8
3. BADLY attempts:9 score:9
4. SOOTH attempts:4 score:4
5. MOURN attempts:5 score:5
6. ROUTE attempts:3 score:3
7. SPITE attempts:6 score:6
8. FUZZY attempts:11 score:11

# squareword.org 🧩 #1426 🥳 8 ⏱️ 0:03:18.438840

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟩
    🟨 🟨 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    M A M B A
    A W A R D
    R A C E D
    C R A V E
    H E W E D

# cemantle.certitudes.org 🧩 #1363 🥳 99 ⏱️ 0:04:18.790991

🤔 100 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 10 chat prompts
🤖 10 dolphin3:latest replies
😎  1 🥶 82 🧊 16

      $1 #100   ~1 rare         100.00°C 🥳 1000‰
      $2  #70   ~2 clutch        24.00°C 😎  382‰
      $3  #22      bird          18.13°C 🥶
      $4  #62      steak         16.34°C 🥶
      $5  #86      flock         16.08°C 🥶
      $6  #68      eagle         15.89°C 🥶
      $7  #96      carving       14.26°C 🥶
      $8  #28      diamond       14.17°C 🥶
      $9  #42      hawk          14.10°C 🥶
     $10  #80      prey          13.28°C 🥶
     $11  #63      sushi         13.00°C 🥶
     $12  #82      soar          12.41°C 🥶
     $13  #81      roost         11.95°C 🥶
     $85   #5      boat          -0.01°C 🧊

# cemantix.certitudes.org 🧩 #1396 🥳 100 ⏱️ 0:01:46.764994

🤔 101 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 21 chat prompts
🤖 21 dolphin3:latest replies
🔥  1 🥵  5 😎 14 🥶 59 🧊 21

      $1 #101   ~1 intensité        100.00°C 🥳 1000‰
      $2  #62  ~13 éclairement       48.32°C 🔥  992‰
      $3  #81   ~6 luminance         42.04°C 🥵  969‰
      $4  #56  ~15 polarisation      38.67°C 🥵  923‰
      $5  #30  ~19 lumière           37.84°C 🥵  910‰
      $6  #29  ~20 chromatique       37.71°C 🥵  905‰
      $7  #86   ~3 réverbération     37.70°C 🥵  903‰
      $8  #46  ~17 absorption        37.20°C 😎  884‰
      $9  #73  ~10 polariseur        35.86°C 😎  826‰
     $10  #83   ~4 obscurité         34.92°C 😎  774‰
     $11  #50  ~16 interférence      34.67°C 😎  758‰
     $12  #98   ~2 brillance         33.92°C 😎  711‰
     $22  #53      intensification   28.25°C 🥶
     $81  #57      pôle              -1.23°C 🧊
