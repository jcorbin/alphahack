# 2025-10-28

- 🔗 spaceword.org 🧩 2025-10-27 🏁 score 2173 ranked 3.9% 15/384 ⏱️ 1:21:02.170202
- 🔗 alfagok.diginaut.net 🧩 #360 🥳 14 ⏱️ 0:00:40.784784
- 🔗 alphaguess.com 🧩 #826 🥳 13 ⏱️ 0:00:33.898846
- 🔗 squareword.org 🧩 #1366 🥳 10 ⏱️ 0:03:31.029434
- 🔗 dictionary.com hurdle 🧩 #1396 😦 19 ⏱️ 0:02:48.797735
- 🔗 dontwordle.com 🧩 #1253 😳 6 ⏱️ 0:01:20.322172
- 🔗 cemantle.certitudes.org 🧩 #1303 🥳 67 ⏱️ 0:02:43.344024
- 🔗 cemantix.certitudes.org 🧩 #1336 🥳 333 ⏱️ 0:16:23.837424

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


# spaceword.org 🧩 2025-10-27 🏁 score 2173 ranked 3.9% 15/384 ⏱️ 1:21:02.170202

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 15/384

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ J _ W A P I T I   
      _ A U R A T E _ I _   
      _ _ N _ E T H O X Y   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #360 🥳 14 ⏱️ 0:00:40.784784

🤔 14 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199830 [199830] lijm      q0  ? after
    @+299732 [299732] schub     q1  ? after
    @+324306 [324306] sub       q3  ? after
    @+330491 [330491] televisie q5  ? after
    @+331178 [331178] tennist   q8  ? after
    @+331503 [331503] termijn   q9  ? after
    @+331581 [331581] terne     q11 ? after
    @+331623 [331623] terra     q12 ? after
    @+331636 [331636] terras    q13 ? it
    @+331636 [331636] terras    done. it
    @+331682 [331682] terrein   q10 ? before
    @+331886 [331886] terug     q7  ? before
    @+333695 [333695] thesis    q6  ? before
    @+336900 [336900] toetsing  q4  ? before
    @+349507 [349507] vakantie  q2  ? before

# alphaguess.com 🧩 #826 🥳 13 ⏱️ 0:00:33.898846

🤔 13 attempts
📜 1 sessions

    @        [     0] aa       
    @+1      [     1] aah      
    @+2      [     2] aahed    
    @+3      [     3] aahing   
    @+98230  [ 98230] mach     q0  ? after
    @+147335 [147335] rho      q1  ? after
    @+159617 [159617] slug     q3  ? after
    @+162650 [162650] speed    q5  ? after
    @+164210 [164210] squilgee q6  ? after
    @+164990 [164990] stay     q7  ? after
    @+165047 [165047] steam    q10 ? after
    @+165107 [165107] steel    q11 ? after
    @+165138 [165138] steep    q12 ? it
    @+165138 [165138] steep    done. it
    @+165167 [165167] steer    q9  ? before
    @+165351 [165351] stereo   q8  ? before
    @+165771 [165771] stint    q4  ? before
    @+171935 [171935] tag      q2  ? before

# squareword.org 🧩 #1366 🥳 10 ⏱️ 0:03:31.029434

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟨 🟨 🟨 🟩 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C A V E D
    A G A V E
    R I P E R
    A L O N G
    T E R S E

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1396 😦 19 ⏱️ 0:02:48.797735

📜 1 sessions
💰 score: 4780

    3/6
    IDEAS 🟨🟨⬜🟨⬜
    AROID 🟩⬜🟨🟩🟨
    AUDIO 🟩🟩🟩🟩🟩
    6/6
    AUDIO 🟨⬜⬜⬜⬜
    REALS 🟨🟨🟩⬜⬜
    CRAVE 🟨🟩🟩⬜🟩
    GRACE ⬜🟩🟩🟩🟩
    TRACE ⬜🟩🟩🟩🟩
    BRACE 🟩🟩🟩🟩🟩
    4/6
    BRACE ⬜⬜⬜⬜⬜
    SILTY ⬜⬜⬜⬜⬜
    MOUND ⬜🟩🟩⬜🟨
    DOUGH 🟩🟩🟩🟩🟩
    4/6
    DOUGH 🟩⬜⬜⬜⬜
    DRYAS 🟩⬜🟨⬜⬜
    DEITY 🟩🟩🟩⬜🟩
    DEIFY 🟩🟩🟩🟩🟩
    Final 2/2
    PRONE 🟩🟩🟩⬜🟩
    PROVE 🟩🟩🟩⬜🟩
    FAIL: PROSE

# dontwordle.com 🧩 #1253 😳 6 ⏱️ 0:01:20.322172

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:7870
    ⬜⬜⬜⬜⬜ tried:SOOKS n n n n n remain:2209
    ⬜⬜⬜⬜⬜ tried:CUPPY n n n n n remain:761
    ⬜⬜🟩⬜⬜ tried:ABAFT n n Y n n remain:40
    ⬜⬜🟩⬜🟩 tried:GNAWN n n Y n Y remain:2
    🟩🟩🟩🟩🟩 tried:LEARN Y Y Y Y Y remain:0

    Undos used: 2

      0 words remaining
    x 0 unused letters
    = 0 total score

# cemantle.certitudes.org 🧩 #1303 🥳 67 ⏱️ 0:02:43.344024

🤔 68 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 18 chat prompts
🤖 18 gemma3:latest replies
🔥  2 🥵  8 😎 12 🥶 45

     $1 #68  ~1 distant      100.00°C 🥳 1000‰
     $2 #20 ~18 dim           43.24°C 🔥  997‰
     $3 #23 ~17 faint         38.70°C 🔥  992‰
     $4 #51  ~7 desolate      38.41°C 🥵  988‰
     $5 #29 ~13 hazy          36.81°C 🥵  984‰
     $6 #49  ~9 bleak         35.79°C 🥵  981‰
     $7 #19 ~19 misty         35.23°C 🥵  977‰
     $8 #50  ~8 barren        34.52°C 🥵  973‰
     $9 #52  ~6 faded         32.60°C 🥵  943‰
    $10 #16 ~20 evanescent    32.51°C 🥵  940‰
    $11 #12 ~21 fleeting      31.44°C 🥵  906‰
    $12 #25 ~15 ghostly       30.84°C 😎  878‰
    $13 #59  ~4 sparse        30.55°C 😎  862‰
    $24 #27     gossamer      24.03°C 🥶

# cemantix.certitudes.org 🧩 #1336 🥳 333 ⏱️ 0:16:23.837424

🤔 334 attempts
📜 1 sessions
🫧 14 chat sessions
⁉️ 94 chat prompts
🤖 94 gemma3:latest replies
😱   1 🔥   3 🥵  17 😎  56 🥶 177 🧊  79

      $1 #334   ~1 procureur       100.00°C 🥳 1000‰
      $2 #282  ~25 juge             54.12°C 😱  999‰
      $3 #278  ~28 tribunal         48.01°C 🔥  996‰
      $4 #304  ~13 flagrance        47.00°C 🔥  995‰
      $5 #315   ~7 perquisition     43.94°C 🔥  990‰
      $6 #204  ~58 inculpation      43.92°C 🥵  989‰
      $7 #329   ~3 enquêteur        42.71°C 🥵  987‰
      $8 #230  ~49 infraction       42.68°C 🥵  986‰
      $9 #284  ~23 déposition       42.15°C 🥵  985‰
     $10 #197  ~61 accusation       41.68°C 🥵  982‰
     $11  #95  ~76 instruction      39.76°C 🥵  974‰
     $23 #260  ~36 saisine          32.49°C 😎  899‰
     $79 #225      imputabilité     18.13°C 🥶
    $256 #328      détection        -0.03°C 🧊
