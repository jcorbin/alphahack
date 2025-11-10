# 2025-11-11

- 🔗 spaceword.org 🧩 2025-11-10 🏁 score 2173 ranked 15.2% 58/381 ⏱️ 0:07:09.759775
- 🔗 alfagok.diginaut.net 🧩 #374 🥳 18 ⏱️ 0:00:59.142296
- 🔗 alphaguess.com 🧩 #840 🥳 13 ⏱️ 0:00:32.662365
- 🔗 squareword.org 🧩 #1380 🥳 8 ⏱️ 0:02:53.486336
- 🔗 dictionary.com hurdle 🧩 #1410 🥳 20 ⏱️ 0:03:36.064511
- 🔗 dontwordle.com 🧩 #1267 🥳 6 ⏱️ 0:01:35.621956
- 🔗 cemantix.certitudes.org 🧩 #1350 😦 645 ⏱️ 0:13:45.005663
- 🔗 cemantle.certitudes.org 🧩 #1317 😦 355 ⏱️ 0:09:37.468267

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

# spaceword.org 🧩 2025-11-04 🏁 score 2173 ranked 6.5% 24/367 ⏱️ 0:20:32.980979

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 24/367

      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ H I P _ _ _
      _ _ _ _ _ _ O _ _ _
      _ _ _ _ S O D _ _ _
      _ _ _ _ E _ U _ _ _
      _ _ _ _ I _ N _ _ _
      _ _ _ _ Z E K _ _ _
      _ _ _ _ U M S _ _ _
      _ _ _ _ R _ _ _ _ _
      _ _ _ _ E V E _ _ _







# spaceword.org 🧩 2025-11-10 🏁 score 2173 ranked 15.2% 58/381 ⏱️ 0:07:09.759775

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 58/381

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ V O C A L _ _ _ W   
      _ _ B O R A N E _ A   
      _ _ E X E G E T E S   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #374 🥳 18 ⏱️ 0:00:59.142296

🤔 18 attempts
📜 2 sessions

    @        [     0] &-teken            
    @+1      [     1] &-tekens           
    @+2      [     2] -cijferig          
    @+3      [     3] -e-mail            
    @+199766 [199766] lijn               q0  ? after
    @+199766 [199766] lijn               q1  ? after
    @+299649 [299649] schudde            q2  ? after
    @+349380 [349380] vak                q3  ? after
    @+361749 [361749] vervijfvoudig      q5  ? after
    @+361831 [361831] vervoer            q11 ? after
    @+361974 [361974] vervolg            q12 ? after
    @+362005 [362005] vervolgde          q14 ? after
    @+362010 [362010] vervolgen          q17 ? it
    @+362010 [362010] vervolgen          done. it
    @+362022 [362022] vervolging         q15 ? before
    @+362043 [362043] vervolgopleidingen q13 ? before
    @+362113 [362113] vervorm            q10 ? before
    @+362501 [362501] verwerking         q9  ? before
    @+363281 [363281] verzet             q8  ? before
    @+364820 [364820] vijfhonderd        q7  ? before
    @+367901 [367901] vocht              q6  ? before
    @+374123 [374123] vrij               q4  ? before

# alphaguess.com 🧩 #840 🥳 13 ⏱️ 0:00:32.662365

🤔 13 attempts
📜 1 sessions

    @        [     0] aa     
    @+1      [     1] aah    
    @+2      [     2] aahed  
    @+3      [     3] aahing 
    @+98226  [ 98226] mach   q0  ? after
    @+147331 [147331] rho    q1  ? after
    @+171931 [171931] tag    q2  ? after
    @+174417 [174417] test   q5  ? after
    @+175629 [175629] thro   q6  ? after
    @+175934 [175934] ti     q7  ? after
    @+176437 [176437] tip    q8  ? after
    @+176483 [176483] tiptoe q11 ? after
    @+176493 [176493] tire   q12 ? it
    @+176493 [176493] tire   done. it
    @+176531 [176531] tit    q10 ? before
    @+176664 [176664] to     q9  ? before
    @+176968 [176968] tom    q4  ? before
    @+182018 [182018] un     q3  ? before

# squareword.org 🧩 #1380 🥳 8 ⏱️ 0:02:53.486336

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    M A C A W
    E E R I E
    A R O M A
    L I N E R
    S E E D Y

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1410 🥳 20 ⏱️ 0:03:36.064511

📜 1 sessions
💰 score: 9600

    4/6
    RESIN ⬜⬜⬜🟨🟩
    AXION 🟨⬜🟨⬜🟩
    WITAN ⬜🟩🟩🟩🟩
    TITAN 🟩🟩🟩🟩🟩
    5/6
    TITAN ⬜⬜⬜⬜⬜
    SURLY ⬜🟨🟨⬜⬜
    CRUMP ⬜🟩🟩🟩🟩
    FRUMP ⬜🟩🟩🟩🟩
    GRUMP 🟩🟩🟩🟩🟩
    5/6
    GRUMP ⬜🟨⬜⬜⬜
    SOLAR ⬜⬜⬜⬜🟨
    INERT ⬜⬜🟨🟨⬜
    DERBY ⬜🟩🟩⬜🟩
    JERKY 🟩🟩🟩🟩🟩
    5/6
    JERKY ⬜⬜⬜⬜⬜
    TAILS ⬜⬜⬜🟨⬜
    MULCH ⬜🟨🟨🟨⬜
    CLOUD 🟩🟩⬜🟨⬜
    CLUNG 🟩🟩🟩🟩🟩
    Final 1/2
    BROWN 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1267 🥳 6 ⏱️ 0:01:35.621956

📜 1 sessions
💰 score: 5

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:7870
    ⬜⬜⬜⬜⬜ tried:SOOKS n n n n n remain:2209
    ⬜⬜⬜⬜⬜ tried:PUPPY n n n n n remain:956
    ⬜⬜⬜⬜⬜ tried:CRWTH n n n n n remain:181
    ⬜🟩⬜⬜⬜ tried:BANAL n Y n n n remain:12
    ⬜🟩⬜🟨⬜ tried:DAZED n Y n m n remain:1

    Undos used: 2

      1 words remaining
    x 5 unused letters
    = 5 total score

# cemantix.certitudes.org 🧩 #1350 😦 645 ⏱️ 0:13:45.005663

🤔 644 attempts
📜 1 sessions
🫧 48 chat sessions
⁉️ 331 chat prompts
🤖 331 gemma3:latest replies
😦 🥵  15 😎  48 🥶 330 🧊 251

      $1 #490  ~32 sport              47.59°C 🥵  989‰
      $2 #635   ~5 sportif            45.50°C 🥵  985‰
      $3 #506  ~26 stade              42.86°C 🥵  976‰
      $4 #431  ~39 match              42.50°C 🥵  974‰
      $5 #505  ~27 championnat        42.25°C 🥵  972‰
      $6 #429  ~41 entraîneur         41.61°C 🥵  969‰
      $7 #295  ~50 compétition        41.02°C 🥵  968‰
      $8 #430  ~40 joueur             40.95°C 🥵  967‰
      $9 #577  ~12 volley             37.77°C 🥵  951‰
     $10 #448  ~36 arbitre            37.60°C 🥵  950‰
     $11 #497  ~30 champion           37.24°C 🥵  948‰
     $16 #544  ~17 athlète            29.20°C 😎  882‰
     $64 #291      duel               14.49°C 🥶
    $394  #71      festin             -0.02°C 🧊

# cemantle.certitudes.org 🧩 #1317 😦 355 ⏱️ 0:09:37.468267

🤔 354 attempts
📜 2 sessions
🫧 30 chat sessions
⁉️ 203 chat prompts
🤖 194 gemma3:latest replies
🤖 8 llama3.2:latest replies
😦 🥵   3 😎  37 🥶 290 🧊  24

      $1 #293  ~11 transportation    34.57°C 🥵  927‰
      $2 #266  ~16 infrastructure    33.62°C 🥵  909‰
      $3 #182  ~28 technology        33.53°C 🥵  904‰
      $4 #184  ~27 automation        31.72°C 😎  864‰
      $5 #147  ~34 innovation        31.61°C 😎  858‰
      $6 #334   ~7 consumer          31.61°C 😎  859‰
      $7 #288  ~13 logistics         28.01°C 😎  743‰
      $8 #291  ~12 management        27.33°C 😎  710‰
      $9 #269  ~15 energy            27.21°C 😎  702‰
     $10  #52  ~40 connectivity      26.40°C 😎  664‰
     $11 #350   ~1 productivity      26.22°C 😎  652‰
     $12 #339   ~4 retail            26.09°C 😎  641‰
     $41 #151      transformation    20.69°C 🥶
    $331 #197      prototype         -0.24°C 🧊
