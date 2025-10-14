# 2025-10-15

- 🔗 spaceword.org 🧩 2025-10-14 🏁 score 2168 ranked 41.6% 151/363 ⏱️ 0:54:23.050115
- 🔗 alfagok.diginaut.net 🧩 #347 🥳 21 ⏱️ 0:01:00.647009
- 🔗 alphaguess.com 🧩 #813 🥳 14 ⏱️ 0:00:41.439823
- 🔗 squareword.org 🧩 #1353 🥳 8 ⏱️ 0:02:17.415581
- 🔗 dictionary.com hurdle 🧩 #1383 😦 13 ⏱️ 0:02:52.110099
- 🔗 dontwordle.com 🧩 #1240 🥳 6 ⏱️ 0:01:44.263830
- 🔗 cemantle.certitudes.org 🧩 #1290 🥳 462 ⏱️ 0:19:11.675760
- 🔗 cemantix.certitudes.org 🧩 #1323 🥳 37 ⏱️ 0:04:02.287441

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


# spaceword.org 🧩 2025-10-14 🏁 score 2168 ranked 41.6% 151/363 ⏱️ 0:54:23.050115

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 151/363

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ U N D O _ _ _   
      _ _ _ _ _ _ W _ _ _   
      _ _ _ I R O N _ _ _   
      _ _ _ _ _ P E _ _ _   
      _ _ _ _ O A R _ _ _   
      _ _ _ _ _ Q _ _ _ _   
      _ _ _ _ F U B _ _ _   
      _ _ _ J E E _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #347 🥳 21 ⏱️ 0:01:00.647009

🤔 21 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+49847  [ 49847] boks      q2  ? after
    @+62286  [ 62286] cement    q5  ? after
    @+68520  [ 68520] connectie q6  ? after
    @+71640  [ 71640] crypt     q7  ? after
    @+72257  [ 72257] curry     q9  ? after
    @+72567  [ 72567] cyclus    q10 ? after
    @+72724  [ 72724] daar      q14 ? after
    @+72744  [ 72744] daarginds q18 ? after
    @+72754  [ 72754] daarmede  q19 ? after
    @+72756  [ 72756] daarna    q20 ? it
    @+72756  [ 72756] daarna    done. it
    @+72763  [ 72763] daarom    q17 ? before
    @+72799  [ 72799] dacht     q15 ? before
    @+72875  [ 72875] dag       q8  ? before
    @+74754  [ 74754] dc        q4  ? before
    @+99741  [ 99741] ex        q1  ? before
    @+199826 [199826] lijm      q0  ? before

# alphaguess.com 🧩 #813 🥳 14 ⏱️ 0:00:41.439823

🤔 14 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+47392 [47392] dis       q1  ? after
    @+72812 [72812] gremolata q2  ? after
    @+85516 [85516] ins       q3  ? after
    @+91861 [91861] knot      q4  ? after
    @+93281 [93281] lar       q6  ? after
    @+93573 [93573] lati      q9  ? after
    @+93637 [93637] laud      q11 ? after
    @+93677 [93677] launch    q12 ? after
    @+93700 [93700] laundry   q13 ? it
    @+93700 [93700] laundry   done. it
    @+93727 [93727] lava      q10 ? before
    @+93909 [93909] lea       q7  ? vb
    @+93909 [93909] lea       q8  ? before
    @+94958 [94958] lib       q5  ? before
    @+98231 [98231] mach      q0  ? before

# squareword.org 🧩 #1353 🥳 8 ⏱️ 0:02:17.415581

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S H A P E
    H O L E D
    A M O N G
    F E N C E
    T R E E D

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1383 😦 13 ⏱️ 0:02:52.110099

📜 1 sessions
💰 score: 2580

    4/6
    ORLES 🟨🟨⬜⬜⬜
    RATIO 🟨🟨⬜⬜🟨
    HOARD ⬜🟨🟨🟨⬜
    APRON 🟩🟩🟩🟩🟩
    3/6
    APRON 🟩🟨⬜⬜⬜
    ADAPT 🟩🟩⬜🟩🟩
    ADEPT 🟩🟩🟩🟩🟩
    6/6
    ADEPT ⬜⬜🟨⬜⬜
    ORLES ⬜🟨⬜🟨🟨
    SERIF 🟨🟩🟨🟩⬜
    BEGIN ⬜🟩⬜🟩🟩
    VENIN ⬜🟩⬜🟩🟩
    HEMIN ⬜🟩⬜🟩🟩
    FAIL: RESIN

# dontwordle.com 🧩 #1240 🥳 6 ⏱️ 0:01:44.263830

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:VILLI n n n n n remain:6812
    ⬜⬜⬜⬜⬜ tried:EBBED n n n n n remain:2576
    ⬜⬜⬜⬜⬜ tried:POOPY n n n n n remain:823
    ⬜⬜⬜🟨⬜ tried:CRWTH n n n m n remain:58
    ⬜🟨⬜🟩⬜ tried:ATMAN n m n Y n remain:3
    🟨🟨⬜🟩🟨 tried:TUFAS m m n Y m remain:1

    Undos used: 2

      1 words remaining
    x 6 unused letters
    = 6 total score

# cemantle.certitudes.org 🧩 #1290 🥳 462 ⏱️ 0:19:11.675760

🤔 463 attempts
📜 1 sessions
🫧 17 chat sessions
⁉️ 102 chat prompts
🤖 65 llama3.2:latest replies
🤖 37 gemma3:latest replies
😱   1 🔥   2 🥵  21 😎  72 🥶 361 🧊   5

      $1 #463   ~1 horizontal        100.00°C 🥳 1000‰
      $2 #192  ~74 vertical           67.61°C 😱  999‰
      $3 #193  ~73 perpendicular      60.24°C 🔥  996‰
      $4 #290  ~44 diagonal           54.01°C 🔥  990‰
      $5 #251  ~59 sigmoidal          53.68°C 🥵  988‰
      $6 #372  ~21 arcuate            53.43°C 🥵  987‰
      $7 #280  ~47 orthogonal         52.17°C 🥵  986‰
      $8 #257  ~58 curved             51.10°C 🥵  983‰
      $9 #228  ~66 angular            50.88°C 🥵  982‰
     $10  #73  ~88 contour            50.72°C 🥵  979‰
     $11 #430   ~6 radial             50.35°C 🥵  976‰
     $26 #232  ~64 axial              45.46°C 😎  895‰
     $98 #278      geometrically      34.44°C 🥶
    $459  #30      momentum           -0.33°C 🧊

# cemantix.certitudes.org 🧩 #1323 🥳 37 ⏱️ 0:04:02.287441

🤔 38 attempts
📜 2 sessions
🫧 3 chat sessions
⁉️ 12 chat prompts
🤖 12 gemma3:latest replies
😎  6 🥶 22 🧊  9

     $1 #38  ~1 refuge         100.00°C 🥳 1000‰
     $2 #16  ~6 solitude        26.36°C 😎  817‰
     $3  #6  ~7 repos           25.69°C 😎  784‰
     $4 #32  ~3 nuit            24.98°C 😎  756‰
     $5 #27  ~5 calme           23.11°C 😎  631‰
     $6 #30  ~4 désert          19.22°C 😎  175‰
     $7 #37  ~2 peur            18.66°C 😎   75‰
     $8 #28     isolement       14.44°C 🥶
     $9  #8     vent            12.33°C 🥶
    $10 #33     lointain        12.13°C 🥶
    $11 #22     contemplation   12.06°C 🥶
    $12 #13     silence         11.20°C 🥶
    $13 #34     ombre            9.90°C 🥶
    $30 #36     voile           -1.18°C 🧊
