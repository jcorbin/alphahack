# 2025-11-03

- 🔗 spaceword.org 🧩 2025-11-02 🏁 score 2168 ranked 20.4% 77/377 ⏱️ 0:35:06.663424
- 🔗 alfagok.diginaut.net 🧩 #366 🥳 8 ⏱️ 0:00:28.758078
- 🔗 alphaguess.com 🧩 #832 🥳 11 ⏱️ 0:00:29.108252
- 🔗 squareword.org 🧩 #1372 🥳 7 ⏱️ 0:01:55.232037
- 🔗 dictionary.com hurdle 🧩 #1402 🥳 18 ⏱️ 0:03:16.216462
- 🔗 dontwordle.com 🧩 #1259 🥳 6 ⏱️ 0:01:15.318159
- 🔗 cemantle.certitudes.org 🧩 #1309 🥳 245 ⏱️ 1:13:29.311101
- 🔗 cemantix.certitudes.org 🧩 #1342 🥳 1109 ⏱️ 1:08:12.879761

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








# spaceword.org 🧩 2025-11-02 🏁 score 2168 ranked 20.4% 77/377 ⏱️ 0:35:06.663424

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 77/377

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ I _ _ S O U P _   
      _ _ L _ F A I R S _   
      _ V I Z I R _ B I _   
      _ _ A _ X I _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #366 🥳 8 ⏱️ 0:00:28.758078

🤔 8 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+24910  [ 24910] bad       q3 ? after
    @+37364  [ 37364] bescherm  q4 ? after
    @+43070  [ 43070] bij       q5 ? after
    @+44587  [ 44587] binnen    q7 ? it
    @+44587  [ 44587] binnen    done. it
    @+46456  [ 46456] blief     q6 ? before
    @+49847  [ 49847] boks      q2 ? before
    @+99745  [ 99745] ex        q1 ? before
    @+199827 [199827] lijm      q0 ? before

# alphaguess.com 🧩 #832 🥳 11 ⏱️ 0:00:29.108252

🤔 11 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+23688 [23688] camp       q2  ? after
    @+29609 [29609] circuit    q4  ? after
    @+30323 [30323] clear      q7  ? after
    @+30695 [30695] clog       q8  ? after
    @+30764 [30764] close      q10 ? it
    @+30764 [30764] close      done. it
    @+30882 [30882] clown      q9  ? before
    @+31084 [31084] coagencies q6  ? before
    @+32558 [32558] color      q5  ? before
    @+35531 [35531] convention q3  ? before
    @+47387 [47387] dis        q1  ? before
    @+98226 [98226] mach       q0  ? before

# squareword.org 🧩 #1372 🥳 7 ⏱️ 0:01:55.232037

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S A M B A
    C R O O N
    A M O N G
    N O D E S
    T R Y S T

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1402 🥳 18 ⏱️ 0:03:16.216462

📜 1 sessions
💰 score: 9800

    3/6
    ANISE ⬜⬜⬜⬜🟨
    TOYED 🟩⬜🟨🟨🟨
    TEDDY 🟩🟩🟩🟩🟩
    4/6
    TEDDY ⬜⬜⬜⬜⬜
    SOLAR ⬜⬜⬜⬜🟨
    BRUNG ⬜🟨⬜⬜⬜
    CHIRP 🟩🟩🟩🟩🟩
    3/6
    CHIRP ⬜🟨⬜⬜⬜
    LATHE ⬜🟨⬜🟨🟩
    HEAVE 🟩🟩🟩🟩🟩
    6/6
    HEAVE ⬜⬜🟨⬜⬜
    SALON ⬜🟩⬜⬜⬜
    PARDI ⬜🟩⬜🟩⬜
    BADDY ⬜🟩🟩🟩🟩
    CADDY ⬜🟩🟩🟩🟩
    DADDY 🟩🟩🟩🟩🟩
    Final 2/2
    ANKLE 🟩🟩⬜🟩🟩
    ANGLE 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1259 🥳 6 ⏱️ 0:01:15.318159

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:YUKKY n n n n n remain:7806
    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:4289
    ⬜⬜⬜⬜⬜ tried:ZANZA n n n n n remain:1475
    ⬜⬜⬜⬜⬜ tried:FLOOD n n n n n remain:249
    ⬜⬜⬜⬜🟨 tried:PHPHT n n n n m remain:39
    🟩🟨⬜🟩⬜ tried:ETWEE Y m n Y n remain:1

    Undos used: 2

      1 words remaining
    x 8 unused letters
    = 8 total score

# cemantle.certitudes.org 🧩 #1309 🥳 245 ⏱️ 1:13:29.311101

🤔 246 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 64 chat prompts
🤖 34 llama3.2:latest replies
🤖 30 gemma3:latest replies
😱   1 🔥   4 🥵  14 😎  34 🥶 177 🧊  15

      $1 #246   ~1 plaintiff         100.00°C 🥳 1000‰
      $2 #208  ~22 claimant           62.15°C 😱  999‰
      $3 #209  ~21 defendant          59.77°C 🔥  998‰
      $4 #227  ~11 litigant           58.96°C 🔥  997‰
      $5 #231   ~9 petitioner         58.66°C 🔥  996‰
      $6 #154  ~48 tort               52.13°C 🔥  991‰
      $7 #175  ~43 litigation         48.56°C 🥵  982‰
      $8 #224  ~12 complainant        48.00°C 🥵  981‰
      $9 #242   ~5 compensable        47.58°C 🥵  980‰
     $10 #158  ~46 causation          46.78°C 🥵  976‰
     $11 #185  ~39 damages            46.11°C 🥵  972‰
     $21 #197  ~29 court              36.34°C 😎  890‰
     $55 #162      causal             20.89°C 🥶
    $232  #74      threat             -0.81°C 🧊

# cemantix.certitudes.org 🧩 #1342 🥳 1109 ⏱️ 1:08:12.879761

🤔 1110 attempts
📜 1 sessions
🫧 59 chat sessions
⁉️ 362 chat prompts
🤖 259 llama3.2:latest replies
🤖 103 gemma3:latest replies
🔥   2 🥵  21 😎  69 🥶 644 🧊 373

       $1 #1110    ~1 élevé            100.00°C 🥳 1000‰
       $2  #967   ~11 précepteur        45.28°C 🔥  998‰
       $3  #301   ~60 père              45.11°C 🔥  997‰
       $4  #311   ~55 mère              37.37°C 🥵  988‰
       $5  #309   ~56 fils              36.38°C 🥵  984‰
       $6  #243   ~66 âge               36.09°C 🥵  982‰
       $7  #153   ~78 aristocrate       35.97°C 🥵  980‰
       $8  #321   ~54 frère             35.23°C 🥵  974‰
       $9  #529   ~42 naissance         35.21°C 🥵  973‰
      $10  #332   ~51 orphelin          33.83°C 🥵  963‰
      $11  #261   ~63 enfance           33.75°C 🥵  960‰
      $25  #304   ~58 adoptif           29.57°C 😎  876‰
      $94  #730       bénédictin        21.90°C 🥶
     $738  #416       instauration      -0.02°C 🧊
