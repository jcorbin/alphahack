# 2025-10-06

- 🔗 spaceword.org 🧩 2025-10-05 🏁 score 2173 ranked 7.0% 25/357 ⏱️ 1 day, 1:05:42.795538
- 🔗 alfagok.diginaut.net 🧩 #338 🥳 15 ⏱️ 21:45:57.419550
- 🔗 alphaguess.com 🧩 #804 🥳 14 ⏱️ 21:46:59.202911
- 🔗 squareword.org 🧩 #1344 🥳 7 ⏱️ 1 day, 19:39:00.833857
- 🔗 dictionary.com hurdle 🧩 #1374 🥳 17 ⏱️ 21:55:23.208181
- 🔗 dontwordle.com 🧩 #1231 🥳 6 ⏱️ 21:56:46.165898
- 🔗 cemantle.certitudes.org 🧩 #1281 🥳 266 ⏱️ 22:00:54.749906
- 🔗 cemantix.certitudes.org 🧩 #1314 🥳 432 ⏱️ 22:06:26.198504

# Dev

## WIP

- meta: review works up to rc branch progression
- square: finish questioning work

## TODO

- meta:
  - review should progress main branch too
  - rework command model
    * current `log <solver> ...` and `run <solver>` should instead
    * unify into `<solver> log|run ...`
    * with the same stateful sub-prompting so that we can just say `<solver>`
      and then `log ...` and then `run` obviating the `log continue` command
      separate from just `run`
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

- hurdle report wasn't right out of #1373 -- was missing first few rounds
  - would be nice if it were easier to one-shot report to stdout for dev loop
    i.e. we want to be able to:
    ```shell
    $ LOG_FILE=log/play.dictionary.com_games_todays-hurdle/#1373
    $ python hurdle.py $LOG_FILE -- report
    ```
    to get there:
    1. stored main needs to collect rest args -> first round input
    2. set some flag, or wrap some state, to stop after first round
    3. input injection needs to be reliable, memory is that it's not?
    4. expired prompt may get in the way here?

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

# spaceword.org 🧩 2025-10-05 🏁 score 2173 ranked 7.0% 25/357 ⏱️ 1 day, 1:05:42.795538

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 25/357

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ F A R _ _ _   
      _ _ _ _ _ _ E _ _ _   
      _ _ _ _ _ Z A _ _ _   
      _ _ _ _ J A G _ _ _   
      _ _ _ _ _ P I _ _ _   
      _ _ _ _ _ A N _ _ _   
      _ _ _ _ I T _ _ _ _   
      _ _ _ _ N E E _ _ _   
      _ _ _ _ S O X _ _ _   


# alfagok.diginaut.net 🧩 #338 🥳 15 ⏱️ 21:45:57.419550

🤔 15 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199834 [199834] lijm      q0  ? after
    @+299752 [299752] schub     q1  ? after
    @+302782 [302782] shredder  q6  ? after
    @+304296 [304296] skelet    q7  ? after
    @+304319 [304319] ski       q10 ? after
    @+304422 [304422] skip      q11 ? after
    @+304475 [304475] skunk     q12 ? after
    @+304499 [304499] slaaf     q14 ? it
    @+304499 [304499] slaaf     done. it
    @+304527 [304527] slaap     q9  ? before
    @+304868 [304868] slag      q8  ? before
    @+305815 [305815] slijm     q5  ? before
    @+311921 [311921] spier     q4  ? before
    @+324326 [324326] sub       q3  ? before
    @+349535 [349535] vakantie  q2  ? before

# alphaguess.com 🧩 #804 🥳 14 ⏱️ 21:46:59.202911

🤔 14 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+47392 [47392] dis       q1  ? after
    @+49439 [49439] do        q5  ? after
    @+50416 [50416] dove      q7  ? after
    @+50910 [50910] drawl     q8  ? after
    @+51142 [51142] drive     q9  ? after
    @+51236 [51236] drop      q10 ? after
    @+51318 [51318] drown     q11 ? after
    @+51354 [51354] drug      q12 ? after
    @+51380 [51380] drum      q13 ? it
    @+51380 [51380] drum      done. it
    @+51413 [51413] drunk     q6  ? before
    @+53408 [53408] el        q4  ? before
    @+60095 [60095] face      q3  ? before
    @+72812 [72812] gremolata q2  ? before
    @+98231 [98231] mach      q0  ? before

# squareword.org 🧩 #1344 🥳 7 ⏱️ 1 day, 19:39:00.833857

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟨 🟩 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C R I S P
    H E N N A
    A C T E D
    S T E E D
    M A R R Y

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1374 🥳 17 ⏱️ 21:55:23.208181

📜 1 sessions
💰 score: 9900

    2/6
    ALOES 🟩⬜⬜🟨🟨
    ASIDE 🟩🟩🟩🟩🟩
    4/6
    ASIDE ⬜⬜⬜⬜🟨
    ENROL 🟨⬜⬜⬜⬜
    WECHT 🟨🟨⬜⬜🟩
    TWEET 🟩🟩🟩🟩🟩
    5/6
    TWEET ⬜🟨⬜⬜⬜
    WOADS 🟨🟨⬜⬜🟨
    SCOWL 🟩⬜🟩🟩⬜
    SHOWY 🟩🟩🟩🟩⬜
    SHOWN 🟩🟩🟩🟩🟩
    4/6
    SHOWN ⬜⬜⬜⬜⬜
    LITER ⬜⬜🟨⬜🟨
    PARTY 🟨⬜🟨🟨🟨
    CRYPT 🟩🟩🟩🟩🟩
    Final 2/2
    BORDE ⬜🟨🟨🟨🟨
    OLDER 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1231 🥳 6 ⏱️ 21:56:46.165898

📜 1 sessions
💰 score: 12

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:JINNI n n n n n remain:7302
    ⬜⬜⬜⬜⬜ tried:POOPY n n n n n remain:3137
    ⬜⬜⬜⬜⬜ tried:KUDZU n n n n n remain:1452
    ⬜🟨⬜⬜⬜ tried:CRWTH n m n n n remain:211
    ⬜🟨🟨⬜⬜ tried:BARBS n m m n n remain:23
    ⬜🟩🟩🟩⬜ tried:ALARM n Y Y Y n remain:2

    Undos used: 2

      2 words remaining
    x 6 unused letters
    = 12 total score

# cemantle.certitudes.org 🧩 #1281 🥳 266 ⏱️ 22:00:54.749906

🤔 267 attempts
📜 1 sessions
🫧 14 chat sessions
⁉️ 85 chat prompts
🤖 27 llama3.2:latest replies
🤖 58 gemma3:latest replies
🔥   2 🥵  16 😎  52 🥶 182 🧊  14

      $1 #267   ~1 consultation     100.00°C 🥳 1000‰
      $2  #78  ~56 review            47.73°C 🔥  997‰
      $3 #144  ~40 input             42.44°C 🔥  993‰
      $4  #83  ~53 evaluation        39.67°C 🥵  988‰
      $5  #81  ~55 assessment        36.58°C 🥵  983‰
      $6  #84  ~52 feedback          36.16°C 🥵  981‰
      $7 #200  ~21 mediation         34.85°C 🥵  970‰
      $8 #196  ~22 implementation    34.63°C 🥵  967‰
      $9 #193  ~24 framework         33.63°C 🥵  961‰
     $10 #150  ~38 examination       33.44°C 🥵  959‰
     $11 #266   ~2 clarification     33.38°C 🥵  958‰
     $20 #260   ~6 reevaluation      30.57°C 😎  890‰
     $72 #156      research          20.78°C 🥶
    $254   #4      melancholy        -0.61°C 🧊

# cemantix.certitudes.org 🧩 #1314 🥳 432 ⏱️ 22:06:26.198504

🤔 433 attempts
📜 1 sessions
🫧 20 chat sessions
⁉️ 125 chat prompts
🤖 20 llama3.2:latest replies
🤖 105 gemma3:latest replies
😱   1 🔥   5 🥵   8 😎  72 🥶 273 🧊  73

      $1 #433   ~1 mondialisation        100.00°C 🥳 1000‰
      $2 #348  ~35 globalisation          79.59°C 😱  999‰
      $3 #401  ~10 capitalisme            58.41°C 🔥  997‰
      $4 #365  ~24 économique             56.61°C 🔥  996‰
      $5 #354  ~31 internationalisation   54.88°C 🔥  995‰
      $6 #400  ~11 libéralisme            53.18°C 🔥  993‰
      $7 #355  ~30 mondial                53.07°C 🔥  992‰
      $8 #364  ~25 économie               52.04°C 🥵  988‰
      $9 #350  ~34 délocalisation         51.17°C 🥵  984‰
     $10 #408   ~5 politique              47.95°C 🥵  972‰
     $11 #153  ~66 émergence              44.43°C 🥵  957‰
     $16 #206  ~58 crise                  38.36°C 😎  875‰
     $88 #193      renouveau              24.76°C 🥶
    $361 #170      sédiment               -0.11°C 🧊
