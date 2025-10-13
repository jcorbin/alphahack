# 2025-10-14

- 🔗 spaceword.org 🧩 2025-10-13 🏁 score 2173 ranked 5.8% 23/397 ⏱️ 0:37:58.664665
- 🔗 alfagok.diginaut.net 🧩 #346 🥳 13 ⏱️ 0:00:57.908591
- 🔗 alphaguess.com 🧩 #812 🥳 12 ⏱️ 0:00:48.142590
- 🔗 squareword.org 🧩 #1352 🥳 8 ⏱️ 0:02:29.162169
- 🔗 dictionary.com hurdle 🧩 #1382 🥳 20 ⏱️ 0:05:17.460800
- 🔗 dontwordle.com 🧩 #1239 🥳 6 ⏱️ 0:01:56.320660
- 🔗 cemantle.certitudes.org 🧩 #1289 🥳 39 ⏱️ 0:00:18.574713
- 🔗 cemantix.certitudes.org 🧩 #1322 🥳 318 ⏱️ 0:03:51.371048

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

# spaceword.org 🧩 2025-10-13 🏁 score 2173 ranked 5.8% 23/397 ⏱️ 0:37:58.664665

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 23/397

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ H I C _ D _ Q _ E   
      _ O _ U N I T I V E   
      _ N E P E T A _ _ K   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #346 🥳 13 ⏱️ 0:00:57.908591

🤔 13 attempts
📜 1 sessions

    @        [     0] &-teken       
    @+1      [     1] &-tekens      
    @+2      [     2] -cijferig     
    @+3      [     3] -e-mail       
    @+199831 [199831] lijm          q0  ? after
    @+299746 [299746] schub         q1  ? after
    @+311915 [311915] spier         q4  ? after
    @+314624 [314624] st            q5  ? after
    @+314908 [314908] staats        q9  ? after
    @+315157 [315157] staatsolie    q10 ? after
    @+315281 [315281] staatswinkels q11 ? after
    @+315339 [315339] stad          q12 ? it
    @+315339 [315339] stad          done. it
    @+315404 [315404] stads         q8  ? before
    @+316839 [316839] start         q7  ? before
    @+319419 [319419] stik          q6  ? before
    @+324320 [324320] sub           q3  ? before
    @+349521 [349521] vakantie      q2  ? before

# alphaguess.com 🧩 #812 🥳 12 ⏱️ 0:00:48.142590

🤔 12 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+47392 [47392] dis       q1  ? after
    @+60095 [60095] face      q3  ? after
    @+60862 [60862] fas       q7  ? after
    @+60912 [60912] fash      q10 ? after
    @+60933 [60933] fast      q11 ? it
    @+60933 [60933] fast      done. it
    @+60962 [60962] fat       q9  ? before
    @+61243 [61243] feast     q8  ? before
    @+61631 [61631] fen       q6  ? before
    @+63251 [63251] flag      q5  ? before
    @+66451 [66451] french    q4  ? before
    @+72812 [72812] gremolata q2  ? before
    @+98231 [98231] mach      q0  ? before

# squareword.org 🧩 #1352 🥳 8 ⏱️ 0:02:29.162169

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T E W S
    T U L I P
    A N O D E
    R I P E N
    S C E N T

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1382 🥳 20 ⏱️ 0:05:17.460800

📜 1 sessions
💰 score: 9600

    5/6
    SLATE ⬜⬜⬜⬜🟨
    DENIM ⬜🟨⬜⬜⬜
    HYPER ⬜⬜🟨🟩🟩
    POWER 🟩⬜⬜🟩🟩
    PURER 🟩🟩🟩🟩🟩
    3/6
    PURER ⬜🟩⬜🟩🟩
    TUNER 🟨🟩⬜🟩🟩
    OUTER 🟩🟩🟩🟩🟩
    5/6
    OUTER ⬜🟨⬜⬜⬜
    UNLAY 🟨⬜⬜🟨⬜
    HAIKU ⬜🟨⬜⬜🟨
    SCUBA ⬜⬜🟩🟨🟨
    ABUZZ 🟩🟩🟩🟩🟩
    5/6
    ABUZZ ⬜⬜⬜⬜⬜
    NOISE 🟨🟩⬜⬜🟨
    WOMEN ⬜🟩⬜🟩🟩
    CODEN ⬜🟩⬜🟩🟩
    TOKEN 🟩🟩🟩🟩🟩
    Final 2/2
    GRIMY ⬜🟩🟩⬜⬜
    DRILL 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1239 🥳 6 ⏱️ 0:01:56.320660

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:FREER n n n n n remain:4802
    ⬜⬜⬜⬜⬜ tried:DODOS n n n n n remain:1134
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:476
    ⬜⬜⬜⬜⬜ tried:JINNI n n n n n remain:114
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:27
    ⬜⬜🟩🟨⬜ tried:ABAKA n n Y m n remain:1

    Undos used: 4

      1 words remaining
    x 8 unused letters
    = 8 total score

# cemantle.certitudes.org 🧩 #1289 🥳 39 ⏱️ 0:00:18.574713

🤔 40 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 8 chat prompts
🤖 8 gemma3:latest replies
🔥  1 🥵  3 😎  3 🥶 26 🧊  6

     $1 #40  ~1 accuracy      100.00°C 🥳 1000‰
     $2 #39  ~2 precision      54.42°C 🔥  998‰
     $3  #9  ~8 velocity       38.97°C 🥵  958‰
     $4 #13  ~7 speed          36.31°C 🥵  932‰
     $5 #34  ~4 dexterity      34.93°C 🥵  910‰
     $6 #33  ~5 agility        34.29°C 😎  893‰
     $7 #21  ~6 swiftness      31.59°C 😎  815‰
     $8 #37  ~3 gracefulness   27.32°C 😎  545‰
     $9  #6     quantum        22.20°C 🥶
    $10 #15     acceleration   20.72°C 🥶
    $11 #38     kinetic        19.34°C 🥶
    $12 #17     flow           16.63°C 🥶
    $13  #7     quartz         16.53°C 🥶
    $35 #30     sprint         -0.09°C 🧊

# cemantix.certitudes.org 🧩 #1322 🥳 318 ⏱️ 0:03:51.371048

🤔 319 attempts
📜 1 sessions
🫧 14 chat sessions
⁉️ 89 chat prompts
🤖 89 gemma3:latest replies
🔥   1 🥵   6 😎  35 🥶 244 🧊  32

      $1 #319   ~1 bouteille         100.00°C 🥳 1000‰
      $2 #308   ~4 verre              51.63°C 🔥  997‰
      $3 #318   ~2 vin                48.56°C 🥵  988‰
      $4 #316   ~3 bière              45.79°C 🥵  976‰
      $5 #190  ~27 vodka              45.03°C 🥵  969‰
      $6 #198  ~24 liqueur            42.23°C 🥵  950‰
      $7 #152  ~34 distillat          41.40°C 🥵  943‰
      $8 #288   ~8 tonneau            39.61°C 🥵  916‰
      $9 #248  ~18 kir                37.58°C 😎  887‰
     $10 #212  ~22 pastis             36.86°C 😎  880‰
     $11 #196  ~25 spiritueux         35.45°C 😎  848‰
     $12 #192  ~26 brandy             35.09°C 😎  839‰
     $44 #204      élixir             24.40°C 🥶
    $288 #177      précipité          -0.82°C 🧊
