# 2025-10-16

- 🔗 spaceword.org 🧩 2025-10-15 🏁 score 2173 ranked 6.5% 25/387 ⏱️ 0:34:01.345084
- 🔗 alfagok.diginaut.net 🧩 #348 🥳 25 ⏱️ 0:01:48.786680
- 🔗 alphaguess.com 🧩 #814 🥳 12 ⏱️ 0:00:26.772952
- 🔗 squareword.org 🧩 #1354 🥳 7 ⏱️ 0:02:20.957647
- 🔗 dictionary.com hurdle 🧩 #1384 🥳 18 ⏱️ 0:03:04.921615
- 🔗 dontwordle.com 🧩 #1241 🥳 6 ⏱️ 0:01:35.301594
- 🔗 cemantle.certitudes.org 🧩 #1291 🥳 705 ⏱️ 0:07:23.788429
- 🔗 cemantix.certitudes.org 🧩 #1324 🥳 67 ⏱️ 0:00:34.083280

# Dev

## WIP

## TODO

- meta: alfagok lines not getting collected
  ```
  pick 4754d78e # alfagok.diginaut.net day #345
  ```

- dontword:
  - upsteam site seems to be glitchy wrt generating result copy on mobile
  - workaround by synthesizing?
  - workaround by storing complete-but-unverified anyhow?

- hurdle: report wasn't right out of #1373 -- was missing first few rounds

- square: finish questioning work

- reuse input injection mechanism from store
  - wherever the current input injection usage is
  - and also to allow more seamless meta log continue ...

- meta:
  - `day` command needs to be able to progress even without all solvers done
  - `day` pruning should be more agro
  - rework command model
    * current `log <solver> ...` and `run <solver>` should instead
    * unify into `<solver> log|run ...`
    * with the same stateful sub-prompting so that we can just say `<solver>`
      and then `log ...` and then `run` obviating the `log continue` command
      separate from just `run`
  - review should progress main branch too
  - better logic circa end of day early play, e.g. doing a CET timezone puzzle
    close late in the "prior" day local (EST) time; similarly, early play of
    next-day spaceword should work gracefully
  - support other intervals like weekly/monthly for spaceword

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



# spaceword.org 🧩 2025-10-15 🏁 score 2173 ranked 6.5% 25/387 ⏱️ 0:34:01.345084

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 25/387

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ J _ _ _ _   
      _ _ _ _ N O H _ _ _   
      _ _ _ _ _ T E _ _ _   
      _ _ _ _ P A X _ _ _   
      _ _ _ _ E _ O _ _ _   
      _ _ _ _ E O N _ _ _   
      _ _ _ _ K _ E _ _ _   
      _ _ _ _ E L _ _ _ _   
      _ _ _ _ D I F _ _ _   


# alfagok.diginaut.net 🧩 #348 🥳 25 ⏱️ 0:01:48.786680

🤔 25 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199831 [199831] lijm      q0  ? after
    @+211743 [211743] me        q4  ? after
    @+217701 [217701] mijnbouw  q5  ? after
    @+217929 [217929] milieu    q17 ? after
    @+218381 [218381] milieus   q22 ? after
    @+218514 [218514] militair  q23 ? after
    @+218514 [218514] militair  q24 ? it
    @+218514 [218514] militair  done. it
    @+218571 [218571] miljard   q20 ? after
    @+218571 [218571] miljard   q21 ? before
    @+218641 [218641] miljoen   q18 ? after
    @+218641 [218641] miljoen   q19 ? before
    @+218859 [218859] min       q16 ? before
    @+220063 [220063] mistastte q15 ? before
    @+220688 [220688] mmcmlxxxi q14 ? .
    @+223664 [223664] molen     q3  ? before
    @+247734 [247734] op        q2  ? before
    @+299738 [299738] schub     q1  ? before

# alphaguess.com 🧩 #814 🥳 12 ⏱️ 0:00:26.772952

🤔 12 attempts
📜 1 sessions

    @        [     0] aa     
    @+1      [     1] aah    
    @+2      [     2] aahed  
    @+3      [     3] aahing 
    @+98231  [ 98231] mach   q0  ? after
    @+147336 [147336] rho    q1  ? after
    @+171936 [171936] tag    q2  ? after
    @+182023 [182023] un     q3  ? after
    @+189286 [189286] vicar  q4  ? after
    @+191066 [191066] walk   q7  ? after
    @+191270 [191270] war    q10 ? after
    @+191359 [191359] warm   q11 ? it
    @+191359 [191359] warm   done. it
    @+191477 [191477] wash   q9  ? before
    @+191929 [191929] we     q8  ? before
    @+192890 [192890] whir   q5  ? after
    @+192890 [192890] whir   q6  ? before

# squareword.org 🧩 #1354 🥳 7 ⏱️ 0:02:20.957647

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟩
    🟨 🟩 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C H O W S
    H A Z E L
    A B O D E
    T I N G E
    S T E E P

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1384 🥳 18 ⏱️ 0:03:04.921615

📜 1 sessions
💰 score: 9800

    4/6
    RAISE ⬜⬜⬜⬜🟩
    UNCLE ⬜⬜⬜🟨🟩
    GLOVE ⬜🟨⬜⬜🟩
    MELEE 🟩🟩🟩🟩🟩
    4/6
    MELEE ⬜🟩⬜⬜⬜
    REINS 🟨🟩⬜⬜⬜
    WEARY ⬜🟩🟩🟩⬜
    HEART 🟩🟩🟩🟩🟩
    4/6
    HEART ⬜⬜⬜⬜⬜
    USING ⬜⬜🟨🟨⬜
    YONIC 🟨⬜🟩🟨⬜
    WINDY 🟩🟩🟩🟩🟩
    5/6
    WINDY ⬜⬜⬜⬜⬜
    ROBES 🟨🟨⬜⬜⬜
    ACTOR ⬜⬜⬜🟩🟩
    HUMOR ⬜🟩⬜🟩🟩
    JUROR 🟩🟩🟩🟩🟩
    Final 1/2
    BIDET 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1241 🥳 6 ⏱️ 0:01:35.301594

📜 1 sessions
💰 score: 28

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:7600
    ⬜⬜⬜⬜⬜ tried:EDGED n n n n n remain:2794
    ⬜⬜⬜⬜⬜ tried:TOROT n n n n n remain:752
    ⬜⬜⬜⬜⬜ tried:PLUMP n n n n n remain:127
    ⬜🟨⬜⬜⬜ tried:QAJAQ n m n n n remain:26
    🟩⬜🟩⬜⬜ tried:SWABS Y n Y n n remain:4

    Undos used: 3

      4 words remaining
    x 7 unused letters
    = 28 total score

# cemantle.certitudes.org 🧩 #1291 🥳 705 ⏱️ 0:07:23.788429

🤔 706 attempts
📜 1 sessions
🫧 28 chat sessions
⁉️ 168 chat prompts
🤖 28 gemma3:latest replies
🤖 140 llama3.2:latest replies
🔥   3 🥵  19 😎  84 🥶 482 🧊 117

      $1 #706   ~1 colleague        100.00°C 🥳 1000‰
      $2 #116  ~97 journalist        51.96°C 🔥  995‰
      $3 #129  ~94 correspondent     48.05°C 🔥  992‰
      $4 #131  ~92 reporter          46.73°C 🔥  990‰
      $5 #185  ~76 columnist         44.99°C 🥵  984‰
      $6 #361  ~42 aide              42.93°C 🥵  980‰
      $7 #321  ~56 commentator       41.27°C 🥵  972‰
      $8 #583  ~14 lecturer          41.08°C 🥵  970‰
      $9  #68 ~104 editor            40.96°C 🥵  969‰
     $10 #186  ~75 blogger           40.50°C 🥵  966‰
     $11 #270  ~66 intern            40.45°C 🥵  965‰
     $24 #348  ~44 speechwriter      34.23°C 😎  898‰
    $108 #596      student           23.16°C 🥶
    $590 #606      institutional     -0.02°C 🧊

# cemantix.certitudes.org 🧩 #1324 🥳 67 ⏱️ 0:00:34.083280

🤔 68 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 16 chat prompts
🤖 16 gemma3:latest replies
🥵  3 😎 10 🥶 48 🧊  6

     $1 #68  ~1 sucre         100.00°C 🥳 1000‰
     $2 #60  ~3 farine         43.65°C 🥵  983‰
     $3 #19 ~14 biscuit        36.42°C 🥵  942‰
     $4 #57  ~6 beurre         35.01°C 🥵  924‰
     $5 #50  ~8 cannelle       29.42°C 😎  770‰
     $6 #49  ~9 épice          27.89°C 😎  672‰
     $7 #61  ~2 blé            27.87°C 😎  671‰
     $8 #38 ~10 pâte           27.61°C 😎  641‰
     $9 #20 ~13 arôme          26.84°C 😎  589‰
    $10 #59  ~4 cuire          26.77°C 😎  580‰
    $11 #26 ~11 brioche        24.32°C 😎  315‰
    $12 #58  ~5 cuisson        23.18°C 😎  149‰
    $15 #63     ingrédient     21.16°C 🥶
    $63  #3     chanson        -0.14°C 🧊
