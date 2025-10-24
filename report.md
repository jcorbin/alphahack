# 2025-10-25

- 🔗 spaceword.org 🧩 2025-10-24 🏁 score 2173 ranked 9.6% 35/363 ⏱️ 0:52:46.361211
- 🔗 alfagok.diginaut.net 🧩 #357 🥳 17 ⏱️ 0:01:27.805117
- 🔗 alphaguess.com 🧩 #823 🥳 15 ⏱️ 0:00:45.009675
- 🔗 squareword.org 🧩 #1363 🥳 7 ⏱️ 0:02:51.163350
- 🔗 dictionary.com hurdle 🧩 #1393 🥳 17 ⏱️ 0:03:30.182310
- 🔗 dontwordle.com 🧩 #1250 🥳 6 ⏱️ 0:01:54.093464
- 🔗 cemantle.certitudes.org 🧩 #1300 🥳 304 ⏱️ 0:20:40.609147
- 🔗 cemantix.certitudes.org 🧩 #1333 🥳 364 ⏱️ 0:23:45.057390

# Dev

## WIP

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






# spaceword.org 🧩 2025-10-24 🏁 score 2173 ranked 9.6% 35/363 ⏱️ 0:52:46.361211

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 35/363

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ T _ _ W _ A M _ D   
      _ O _ O A T L I K E   
      _ E L E G I A C _ X   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #357 🥳 17 ⏱️ 0:01:27.805117

🤔 17 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+1      [     1] &-tekens     
    @+2      [     2] -cijferig    
    @+3      [     3] -e-mail      
    @+99745  [ 99745] ex           q1  ? after
    @+149448 [149448] huis         q2  ? after
    @+174558 [174558] kind         q3  ? after
    @+180868 [180868] koelt        q5  ? after
    @+181560 [181560] kog          q8  ? after
    @+181975 [181975] kolf         q9  ? after
    @+182153 [182153] kom          q10 ? after
    @+182285 [182285] kompas       q11 ? after
    @+182345 [182345] konijnen     q12 ? after
    @+182381 [182381] konijnenpoot q13 ? after
    @+182396 [182396] konijnenvel  q14 ? after
    @+182405 [182405] konijntje    q15 ? after
    @+182410 [182410] koning       q16 ? it
    @+182410 [182410] koning       done. it
    @+182414 [182414] koningin     q7  ? before
    @+183971 [183971] koren        q6  ? before
    @+187194 [187194] krontjongs   q4  ? before
    @+199830 [199830] lijm         q0  ? before

# alphaguess.com 🧩 #823 🥳 15 ⏱️ 0:00:45.009675

🤔 15 attempts
📜 1 sessions

    @       [    0] aa           
    @+1     [    1] aah          
    @+2     [    2] aahed        
    @+3     [    3] aahing       
    @+47391 [47391] dis          q1  ? after
    @+60094 [60094] face         q3  ? after
    @+66450 [66450] french       q4  ? after
    @+66834 [66834] front        q8  ? after
    @+66918 [66918] froth        q10 ? after
    @+66944 [66944] frow         q11 ? after
    @+66949 [66949] frown        q14 ? it
    @+66949 [66949] frown        done. it
    @+66959 [66959] frows        q13 ? before
    @+66974 [66974] frowzinesses q12 ? before
    @+67004 [67004] fruit        q9  ? before
    @+67230 [67230] full         q7  ? before
    @+68016 [68016] gall         q6  ? before
    @+69631 [69631] geosyncline  q5  ? before
    @+72811 [72811] gremolata    q2  ? before
    @+98230 [98230] mach         q0  ? before

# squareword.org 🧩 #1363 🥳 7 ⏱️ 0:02:51.163350

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    T E C H S
    A V A I L
    P E R K Y
    A N G E L
    S T O R Y

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1393 🥳 17 ⏱️ 0:03:30.182310

📜 1 sessions
💰 score: 9900

    4/6
    NATES ⬜⬜⬜🟨⬜
    REOIL 🟨🟨⬜⬜⬜
    BURKE ⬜⬜🟨🟨🟨
    WRECK 🟩🟩🟩🟩🟩
    3/6
    WRECK ⬜🟨🟨⬜⬜
    STARE 🟨🟨⬜🟨🟩
    TERSE 🟩🟩🟩🟩🟩
    4/6
    TERSE ⬜⬜🟨🟨⬜
    BOARS ⬜⬜🟩🟩🟨
    SWARF 🟩⬜🟩🟩🟩
    SCARF 🟩🟩🟩🟩🟩
    4/6
    SCARF 🟨🟨🟩⬜⬜
    CLASH 🟩🟩🟩🟩⬜
    CLASP 🟩🟩🟩🟩⬜
    CLASS 🟩🟩🟩🟩🟩
    Final 2/2
    GEOID ⬜🟩🟩⬜⬜
    PEONY 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1250 🥳 6 ⏱️ 0:01:54.093464

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:8089
    ⬜⬜⬜⬜⬜ tried:BENNE n n n n n remain:2684
    ⬜⬜⬜⬜⬜ tried:HAHAS n n n n n remain:231
    ⬜⬜⬜⬜⬜ tried:KUDZU n n n n n remain:73
    🟨🟩⬜⬜⬜ tried:CIVIC m Y n n n remain:2
    ⬜🟩🟩🟨⬜ tried:PICOT n Y Y m n remain:1

    Undos used: 4

      1 words remaining
    x 7 unused letters
    = 7 total score

# cemantle.certitudes.org 🧩 #1300 🥳 304 ⏱️ 0:20:40.609147

🤔 305 attempts
📜 1 sessions
🫧 12 chat sessions
⁉️ 74 chat prompts
🤖 8 llama3.2:latest replies
🤖 66 gemma3:latest replies
😱   1 🔥   1 🥵   4 😎  18 🥶 276 🧊   4

      $1 #305   ~1 capitalist       100.00°C 🥳 1000‰
      $2 #177   ~8 capitalism        82.37°C 😱  999‰
      $3 #304   ~2 bourgeois         65.02°C 🔥  992‰
      $4 #180   ~7 consumerism       53.25°C 🥵  961‰
      $5  #98  ~18 ideology          49.95°C 🥵  937‰
      $6 #303   ~3 meritocratic      49.46°C 🥵  931‰
      $7 #208   ~5 meritocracy       47.20°C 🥵  911‰
      $8 #171   ~9 inequality        45.74°C 😎  884‰
      $9 #159  ~11 oppression        44.17°C 😎  852‰
     $10 #152  ~12 society           40.93°C 😎  734‰
     $11  #65  ~22 radical           39.76°C 😎  671‰
     $12 #238   ~4 rational          39.33°C 😎  653‰
     $26 #292      economic          32.38°C 🥶
    $302 #233      revenue           -0.71°C 🧊

# cemantix.certitudes.org 🧩 #1333 🥳 364 ⏱️ 0:23:45.057390

🤔 365 attempts
📜 1 sessions
🫧 16 chat sessions
⁉️ 99 chat prompts
🤖 35 llama3.2:latest replies
🤖 64 gemma3:latest replies
🥵   1 😎  17 🥶 284 🧊  62

      $1 #365   ~1 balle            100.00°C 🥳 1000‰
      $2 #295  ~10 poteau            38.58°C 🥵  947‰
      $3 #132  ~18 arrière           32.62°C 😎  823‰
      $4  #59  ~19 mur               31.04°C 😎  772‰
      $5 #328   ~8 corde             28.96°C 😎  681‰
      $6 #152  ~16 feu               27.29°C 😎  561‰
      $7 #354   ~5 boulet            26.03°C 😎  440‰
      $8 #357   ~3 couteau           26.01°C 😎  435‰
      $9 #277  ~14 cul               25.94°C 😎  427‰
     $10 #286  ~12 chien             25.21°C 😎  343‰
     $11 #186  ~15 derrière          25.16°C 😎  334‰
     $12 #364   ~2 pique             24.85°C 😎  295‰
     $20 #196      côté              23.24°C 🥶
    $304  #71      nacre             -0.15°C 🧊
