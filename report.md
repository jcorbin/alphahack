# 2025-10-30

- 🔗 spaceword.org 🧩 2025-10-29 🏁 score 2173 ranked 3.2% 12/377 ⏱️ 2:25:56.470675
- 🔗 alfagok.diginaut.net 🧩 #362 🥳 12 ⏱️ 0:00:33.830839
- 🔗 alphaguess.com 🧩 #828 🥳 20 ⏱️ 0:00:46.790237
- 🔗 squareword.org 🧩 #1368 🥳 9 ⏱️ 0:03:18.818703
- 🔗 dictionary.com hurdle 🧩 #1398 😦 14 ⏱️ 0:02:50.845656
- 🔗 dontwordle.com 🧩 #1255 🥳 6 ⏱️ 0:01:45.911929
- 🔗 cemantle.certitudes.org 🧩 #1305 🥳 377 ⏱️ 1:24:28.503159
- 🔗 cemantix.certitudes.org 🧩 #1338 🥳 679 ⏱️ 0:31:35.018359

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




# spaceword.org 🧩 2025-10-29 🏁 score 2173 ranked 3.2% 12/377 ⏱️ 2:25:56.470675

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 12/377

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ T I C _ _ _   
      _ _ _ _ E _ O _ _ _   
      _ _ _ _ L A W _ _ _   
      _ _ _ _ _ L I _ _ _   
      _ _ _ _ _ F E _ _ _   
      _ _ _ _ C A R _ _ _   
      _ _ _ _ _ Q _ _ _ _   
      _ _ _ _ N U _ _ _ _   
      _ _ _ _ O I K _ _ _   


# alfagok.diginaut.net 🧩 #362 🥳 12 ⏱️ 0:00:33.830839

🤔 12 attempts
📜 2 sessions

    @        [     0] &-teken       
    @+1      [     1] &-tekens      
    @+2      [     2] -cijferig     
    @+3      [     3] -e-mail       
    @+199827 [199827] lijm          q0  ? after
    @+299729 [299729] schub         q1  ? after
    @+311898 [311898] spier         q4  ? after
    @+314607 [314607] st            q5  ? after
    @+319402 [319402] stik          q6  ? after
    @+321850 [321850] straten       q7  ? after
    @+322157 [322157] stres         q10 ? after
    @+322266 [322266] strijd        q11 ? it
    @+322266 [322266] strijd        done. it
    @+322463 [322463] strik         q9  ? before
    @+323075 [323075] structuralist q8  ? before
    @+324303 [324303] sub           q3  ? before
    @+349504 [349504] vakantie      q2  ? before

# alphaguess.com 🧩 #828 🥳 20 ⏱️ 0:00:46.790237

🤔 20 attempts
📜 1 sessions

    @       [    0] aa           
    @+1     [    1] aah          
    @+2     [    2] aahed        
    @+3     [    3] aahing       
    @+2802  [ 2802] ag           q5  ? after
    @+4335  [ 4335] alma         q6  ? after
    @+4407  [ 4407] alone        q9  ? after
    @+4432  [ 4432] alphabet     q10 ? after
    @+4452  [ 4452] alphanumeric q11 ? after
    @+4462  [ 4462] alpine       q12 ? after
    @+4469  [ 4469] alps         q17 ? after
    @+4470  [ 4470] already      q19 ? it
    @+4470  [ 4470] already      done. it
    @+4471  [ 4471] alright      q18 ? before
    @+4472  [ 4472] als          q8  ? before
    @+4620  [ 4620] am           q7  ? before
    @+5877  [ 5877] angel        q4  ? before
    @+11765 [11765] back         q3  ? before
    @+23688 [23688] camp         q2  ? before
    @+47387 [47387] dis          q1  ? before
    @+98226 [98226] mach         q0  ? before

# squareword.org 🧩 #1368 🥳 9 ⏱️ 0:03:18.818703

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟨
    🟨 🟨 🟨 🟨 🟨
    🟨 🟩 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P A C T S
    R E L I C
    A R O M A
    M I N E R
    S E E D Y

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1398 😦 14 ⏱️ 0:02:50.845656

📜 1 sessions
💰 score: 5280

    3/6
    SABER ⬜🟩⬜⬜🟨
    RANID 🟩🟩🟨🟨⬜
    RAINY 🟩🟩🟩🟩🟩
    4/6
    RAINY ⬜🟨⬜⬜⬜
    PLEAS ⬜⬜⬜🟨⬜
    GUACO ⬜🟨🟨⬜🟨
    ABOUT 🟩🟩🟩🟩🟩
    3/6
    ABOUT 🟩⬜⬜⬜⬜
    ALIEN 🟩🟩🟩🟨⬜
    ALIVE 🟩🟩🟩🟩🟩
    2/6
    ALIVE ⬜⬜🟩🟨🟩
    VOICE 🟩🟩🟩🟩🟩
    Final 2/2
    DITCH ⬜🟩🟩🟩🟩
    WITCH ⬜🟩🟩🟩🟩
    FAIL: HITCH

# dontwordle.com 🧩 #1255 🥳 6 ⏱️ 0:01:45.911929

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:7042
    ⬜⬜⬜⬜⬜ tried:GOGOS n n n n n remain:2007
    ⬜⬜⬜⬜⬜ tried:JIFFY n n n n n remain:733
    🟨⬜⬜⬜⬜ tried:ADDAX m n n n n remain:206
    ⬜⬜🟨⬜⬜ tried:CHARR n n m n n remain:29
    ⬜🟩🟩⬜🟩 tried:NAPPE n Y Y n Y remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# cemantle.certitudes.org 🧩 #1305 🥳 377 ⏱️ 1:24:28.503159

🤔 378 attempts
📜 1 sessions
🫧 13 chat sessions
⁉️ 76 chat prompts
🤖 24 llama3.2:latest replies
🤖 52 gemma3:latest replies
🔥   3 🥵  11 😎  31 🥶 298 🧊  34

      $1 #378   ~1 abortion         100.00°C 🥳 1000‰
      $2 #344  ~13 contraception     57.76°C 🔥  998‰
      $3 #286  ~30 reproductive      49.81°C 🔥  993‰
      $4 #283  ~32 fetus             46.78°C 🔥  990‰
      $5 #269  ~41 embryo            46.13°C 🥵  988‰
      $6 #281  ~34 pregnancy         43.14°C 🥵  982‰
      $7 #347  ~11 infertility       40.19°C 🥵  970‰
      $8 #265  ~43 childbirth        39.92°C 🥵  969‰
      $9 #282  ~33 prenatal          38.95°C 🥵  964‰
     $10 #271  ~39 fetal             38.08°C 🥵  961‰
     $11 #370   ~3 vasectomy         37.45°C 🥵  953‰
     $16 #310  ~24 abruption         33.77°C 😎  898‰
     $47  #51      pastoral          22.00°C 🥶
    $345  #58      rustic            -0.04°C 🧊

# cemantix.certitudes.org 🧩 #1338 🥳 679 ⏱️ 0:31:35.018359

🤔 680 attempts
📜 1 sessions
🫧 30 chat sessions
⁉️ 195 chat prompts
🤖 65 llama3.2:latest replies
🤖 130 gemma3:latest replies
🥵  24 😎 122 🥶 454 🧊  79

      $1 #680   ~1 équivalent        100.00°C 🥳 1000‰
      $2 #612  ~10 minimal            48.72°C 🥵  989‰
      $3 #163 ~111 niveau             45.29°C 🥵  988‰
      $4 #412  ~45 minimum            41.77°C 🥵  981‰
      $5 #345  ~66 moyen              41.03°C 🥵  978‰
      $6 #103 ~139 pourcentage        41.00°C 🥵  977‰
      $7 #430  ~34 total              39.96°C 🥵  972‰
      $8 #118 ~130 proportion         39.62°C 🥵  970‰
      $9 #161 ~112 proportionnel      39.09°C 🥵  965‰
     $10 #266  ~87 comparaison        38.76°C 🥵  962‰
     $11 #413  ~44 montant            38.39°C 🥵  959‰
     $26 #125 ~129 taux               34.41°C 😎  897‰
    $148 #127      équation           22.33°C 🥶
    $602 #634      simplicité         -0.01°C 🧊
