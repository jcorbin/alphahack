# 2025-10-29

- 🔗 spaceword.org 🧩 2025-10-28 🏁 score 2173 ranked 8.6% 33/384 ⏱️ 0:37:09.324548
- 🔗 alfagok.diginaut.net 🧩 #361 🥳 14 ⏱️ 0:00:43.332645
- 🔗 alphaguess.com 🧩 #827 🥳 19 ⏱️ 0:00:41.156971
- 🔗 squareword.org 🧩 #1367 🥳 7 ⏱️ 0:01:57.661531
- 🔗 dictionary.com hurdle 🧩 #1397 🥳 23 ⏱️ 0:03:28.868767
- 🔗 dontwordle.com 🧩 #1254 🥳 6 ⏱️ 0:02:03.461160
- 🔗 cemantix.certitudes.org 🧩 #1337 🥳 509 ⏱️ 0:23:30.582120
- 🔗 cemantle.certitudes.org 🧩 #1304 🥳 440 ⏱️ 1:07:59.417518

# Dev

## WIP

ui: Shell / Handle revolution

## TODO

- meta: alfagok lines not getting collected
  ```
  pick 4754d78e # alfagok.diginaut.net day #345
  ```

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



# spaceword.org 🧩 2025-10-28 🏁 score 2173 ranked 8.6% 33/384 ⏱️ 0:37:09.324548

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 33/384

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ I _ _ W _ A R _ O   
      _ C _ H A U T E U R   
      _ K L E E N E X _ G   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #361 🥳 14 ⏱️ 0:00:43.332645

🤔 14 attempts
📜 2 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+99745  [ 99745] ex         q1  ? after
    @+149448 [149448] huis       q2  ? after
    @+174558 [174558] kind       q3  ? after
    @+187194 [187194] krontjongs q4  ? after
    @+190345 [190345] ként       q9  ? after
    @+191101 [191101] lager      q11 ? after
    @+191172 [191172] laken      q13 ? it
    @+191172 [191172] laken      done. it
    @+191271 [191271] lam        q12 ? before
    @+191868 [191868] landen     q10 ? before
    @+193492 [193492] lavendel   q5  ? before
    @+199827 [199827] lijm       q0  ? before

# alphaguess.com 🧩 #827 🥳 19 ⏱️ 0:00:41.156971

🤔 19 attempts
📜 1 sessions

    @       [    0] aa           
    @+1     [    1] aah          
    @+2     [    2] aahed        
    @+3     [    3] aahing       
    @+47391 [47391] dis          q1  ? after
    @+60094 [60094] face         q3  ? after
    @+61630 [61630] fen          q6  ? after
    @+62434 [62434] fila         q7  ? after
    @+62837 [62837] fire         q8  ? after
    @+62879 [62879] fired        q11 ? after
    @+62888 [62888] firefang     q13 ? after
    @+62892 [62892] firefight    q14 ? after
    @+62893 [62893] firefighter  q18 ? it
    @+62893 [62893] firefighter  done. it
    @+62894 [62894] firefighters q17 ? before
    @+62895 [62895] firefighting q16 ? before
    @+62898 [62898] fireflies    q15 ? before
    @+62903 [62903] fireguards   q12 ? before
    @+62927 [62927] fireplace    q10 ? before
    @+63023 [63023] fish         q9  ? before
    @+63250 [63250] flag         q5  ? before
    @+66450 [66450] french       q4  ? before
    @+72811 [72811] gremolata    q2  ? before
    @+98230 [98230] mach         q0  ? before

# squareword.org 🧩 #1367 🥳 7 ⏱️ 0:01:57.661531

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C H A T S
    O U G H T
    A T R I A
    S C E N T
    T H E S E

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1397 🥳 23 ⏱️ 0:03:28.868767

📜 1 sessions
💰 score: 9300

    6/6
    AEONS 🟨🟨⬜⬜⬜
    RATED 🟨🟩⬜🟩⬜
    CAPER ⬜🟩⬜🟩🟩
    WAGER ⬜🟩⬜🟩🟩
    BALER ⬜🟩🟨🟩🟩
    LAYER 🟩🟩🟩🟩🟩
    4/6
    LAYER 🟨🟨⬜⬜⬜
    SOLAN ⬜⬜🟨🟨⬜
    QUAIL ⬜⬜🟨🟨🟨
    ALIBI 🟩🟩🟩🟩🟩
    6/6
    ALIBI 🟨⬜⬜⬜⬜
    NARES ⬜🟩🟨🟩⬜
    TAPER ⬜🟩🟩🟩🟩
    JAPER ⬜🟩🟩🟩🟩
    PAPER ⬜🟩🟩🟩🟩
    CAPER 🟩🟩🟩🟩🟩
    5/6
    CAPER ⬜⬜⬜🟨⬜
    LIENS 🟨⬜🟨⬜⬜
    HOYLE ⬜⬜⬜🟨🟩
    GLUME 🟨🟨🟨⬜🟩
    BULGE 🟩🟩🟩🟩🟩
    Final 2/2
    REDON 🟨🟨⬜⬜🟩
    STERN 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1254 🥳 6 ⏱️ 0:02:03.461160

📜 2 sessions
💰 score: 16

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:YUPPY n n n n n remain:7572
    ⬜⬜⬜⬜⬜ tried:TEETH n n n n n remain:2267
    ⬜⬜⬜⬜⬜ tried:GOGOS n n n n n remain:393
    ⬜⬜🟨⬜⬜ tried:KLICK n n m n n remain:86
    ⬜⬜⬜🟩🟨 tried:VIVID n n n Y m remain:5
    🟨🟨⬜🟩⬜ tried:ADMIX m m n Y n remain:2

    Undos used: 3

      2 words remaining
    x 8 unused letters
    = 16 total score

# cemantix.certitudes.org 🧩 #1337 🥳 509 ⏱️ 0:23:30.582120

🤔 510 attempts
📜 1 sessions
🫧 22 chat sessions
⁉️ 133 chat prompts
🤖 48 llama3.2:latest replies
🤖 85 gemma3:latest replies
🥵   3 😎  31 🥶 397 🧊  78

      $1 #510   ~1 sac             100.00°C 🥳 1000‰
      $2 #342  ~21 sangle           40.05°C 🥵  931‰
      $3 #264  ~27 parapluie        39.37°C 🥵  925‰
      $4 #400  ~18 gilet            38.81°C 🥵  915‰
      $5 #320  ~23 chariot          35.48°C 😎  825‰
      $6 #394  ~19 cuir             35.26°C 😎  817‰
      $7 #313  ~24 manteau          34.90°C 😎  807‰
      $8 #432  ~12 bouclette        33.05°C 😎  717‰
      $9 #468   ~4 tablier          32.31°C 😎  676‰
     $10  #93  ~33 ombrelle         31.96°C 😎  655‰
     $11 #249  ~30 chaise           31.55°C 😎  629‰
     $12 #418  ~15 collier          31.53°C 😎  627‰
     $36 #384      bâton            26.11°C 🥶
    $433  #86      opale            -0.07°C 🧊

# cemantle.certitudes.org 🧩 #1304 🥳 440 ⏱️ 1:07:59.417518

🤔 441 attempts
📜 1 sessions
🫧 15 chat sessions
⁉️ 85 chat prompts
🤖 54 llama3.2:latest replies
🤖 31 gemma3:latest replies
🔥   3 🥵   6 😎  22 🥶 349 🧊  60

      $1 #441   ~1 league           100.00°C 🥳 1000‰
      $2 #440   ~2 game              53.74°C 🔥  998‰
      $3 #219  ~29 season            51.87°C 🔥  995‰
      $4 #424   ~7 tournament        47.99°C 🔥  992‰
      $5 #375  ~23 championship      40.41°C 🥵  980‰
      $6 #417  ~11 undefeated        35.84°C 🥵  968‰
      $7 #429   ~4 divisional        33.50°C 🥵  947‰
      $8 #393  ~17 career            31.65°C 🥵  927‰
      $9 #427   ~5 division          31.44°C 🥵  924‰
     $10 #422   ~9 win               30.93°C 🥵  916‰
     $11 #412  ~14 rivalry           27.53°C 😎  842‰
     $12 #433   ~3 captaincy         26.77°C 😎  821‰
     $33 #420      victorious        17.63°C 🥶
    $382 #200      astral            -0.01°C 🧊
