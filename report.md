# 2025-11-07

- 🔗 spaceword.org 🧩 2025-11-06 🏁 score 2173 ranked 9.9% 36/365 ⏱️ 2:08:44.124047
- 🔗 alfagok.diginaut.net 🧩 #370 🥳 14 ⏱️ 0:00:40.501313
- 🔗 alphaguess.com 🧩 #836 🥳 9 ⏱️ 0:00:41.430952
- 🔗 squareword.org 🧩 #1376 🥳 6 ⏱️ 0:01:48.170267
- 🔗 dictionary.com hurdle 🧩 #1406 🥳 17 ⏱️ 0:03:03.570929
- 🔗 dontwordle.com 🧩 #1263 🥳 6 ⏱️ 0:01:11.858520
- 🔗 cemantle.certitudes.org 🧩 #1313 🥳 381 ⏱️ 0:15:52.457090
- 🔗 cemantix.certitudes.org 🧩 #1346 🥳 577 ⏱️ 0:28:25.693791

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



# spaceword.org 🧩 2025-11-06 🏁 score 2173 ranked 9.9% 36/365 ⏱️ 2:08:44.124047

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 36/365

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ P _ _ _ _   
      _ _ _ _ C O P _ _ _   
      _ _ _ _ _ N A _ _ _   
      _ _ _ _ S E V _ _ _   
      _ _ _ _ Q _ A _ _ _   
      _ _ _ _ U R N _ _ _   
      _ _ _ _ E _ E _ _ _   
      _ _ _ _ A T _ _ _ _   
      _ _ _ _ K O I _ _ _   


# alfagok.diginaut.net 🧩 #370 🥳 14 ⏱️ 0:00:40.501313

🤔 14 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+99842  [ 99842] examen     q1  ? after
    @+124522 [124522] gevoel     q3  ? after
    @+124604 [124604] gevoelvol  q11 ? after
    @+124619 [124619] gevolg     q13 ? it
    @+124619 [124619] gevolg     done. it
    @+124643 [124643] gevonden   q12 ? before
    @+124683 [124683] gevreeën   q10 ? before
    @+124844 [124844] geweer     q9  ? before
    @+125219 [125219] gewild     q8  ? before
    @+125932 [125932] gezondheid q7  ? before
    @+127358 [127358] gist       q6  ? before
    @+130267 [130267] grachten   q5  ? before
    @+136028 [136028] hand       q4  ? before
    @+149326 [149326] huis       q2  ? before
    @+199766 [199766] lijn       q0  ? before

# alphaguess.com 🧩 #836 🥳 9 ⏱️ 0:00:41.430952

🤔 9 attempts
📜 1 sessions

    @        [     0] aa      
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98226  [ 98226] mach    q0 ? after
    @+110131 [110131] need    q3 ? after
    @+110809 [110809] neurula q6 ? after
    @+110901 [110901] news    q8 ? it
    @+110901 [110901] news    done. it
    @+111141 [111141] niff    q7 ? before
    @+111495 [111495] no      q5 ? before
    @+116110 [116110] oppo    q4 ? before
    @+122111 [122111] par     q2 ? before
    @+147331 [147331] rho     q1 ? before

# squareword.org 🧩 #1376 🥳 6 ⏱️ 0:01:48.170267

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P L A T
    T I A R A
    A N T I S
    G U E S T
    S P R E E

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1406 🥳 17 ⏱️ 0:03:03.570929

📜 1 sessions
💰 score: 9900

    4/6
    RATES ⬜⬜⬜🟩⬜
    MODEL ⬜🟩⬜🟩🟩
    BOWEL ⬜🟩🟩🟩🟩
    VOWEL 🟩🟩🟩🟩🟩
    5/6
    VOWEL ⬜⬜⬜🟨🟨
    LEADS 🟨🟨⬜⬜⬜
    GLIME ⬜🟨⬜⬜🟩
    BUTLE ⬜⬜⬜🟩🟩
    CYCLE 🟩🟩🟩🟩🟩
    4/6
    CYCLE ⬜⬜⬜⬜🟨
    RESAT ⬜🟩⬜⬜🟨
    MENTO ⬜🟩⬜🟨🟨
    DETOX 🟩🟩🟩🟩🟩
    3/6
    DETOX ⬜🟨⬜⬜⬜
    PRASE ⬜🟩⬜⬜🟨
    CRUEL 🟩🟩🟩🟩🟩
    Final 1/2
    BADLY 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1263 🥳 6 ⏱️ 0:01:11.858520

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:7266
    ⬜⬜⬜⬜⬜ tried:DOGGO n n n n n remain:3220
    ⬜⬜⬜⬜⬜ tried:MYTHY n n n n n remain:1070
    ⬜⬜🟩⬜⬜ tried:FLUFF n n Y n n remain:38
    ⬜⬜🟩⬜🟩 tried:PRUNE n n Y n Y remain:4
    🟨⬜🟩⬜🟩 tried:AQUAE m n Y n Y remain:2

    Undos used: 2

      2 words remaining
    x 7 unused letters
    = 14 total score

# cemantle.certitudes.org 🧩 #1313 🥳 381 ⏱️ 0:15:52.457090

🤔 382 attempts
📜 1 sessions
🫧 18 chat sessions
⁉️ 122 chat prompts
🤖 122 gemma3:latest replies
🔥   5 🥵  20 😎  82 🥶 265 🧊   9

      $1 #382   ~1 climb         100.00°C 🥳 1000‰
      $2 #380   ~3 ascend         65.35°C 🔥  998‰
      $3 #381   ~2 ascent         64.34°C 🔥  997‰
      $4 #176  ~74 tumble         56.98°C 🔥  995‰
      $5 #379   ~4 soar           56.10°C 🔥  994‰
      $6 #317  ~27 slide          53.17°C 🔥  991‰
      $7 #179  ~73 plummet        50.64°C 🔥  990‰
      $8 #130  ~93 plunge         49.01°C 🥵  986‰
      $9 #107  ~99 drop           48.68°C 🥵  985‰
     $10 #106 ~100 fall           47.63°C 🥵  982‰
     $11 #152  ~87 steep          45.70°C 🥵  979‰
     $27 #327  ~21 journey        35.95°C 😎  899‰
    $109 #194      vault          21.69°C 🥶
    $374  #99      resonance      -1.23°C 🧊

# cemantix.certitudes.org 🧩 #1346 🥳 577 ⏱️ 0:28:25.693791

🤔 578 attempts
📜 1 sessions
🫧 23 chat sessions
⁉️ 140 chat prompts
🤖 67 llama3.2:latest replies
🤖 73 gemma3:latest replies
🥵  15 😎  68 🥶 361 🧊 133

      $1 #578   ~1 phare              100.00°C 🥳 1000‰
      $2  #37  ~75 lueur               31.87°C 🥵  986‰
      $3  #84  ~69 lumineux            31.38°C 🥵  983‰
      $4 #354  ~31 mer                 30.20°C 🥵  980‰
      $5 #147  ~56 torche              29.94°C 🥵  976‰
      $6  #11  ~82 lumière             29.53°C 🥵  974‰
      $7 #145  ~57 flambeau            29.33°C 🥵  972‰
      $8 #227  ~48 réverbère           29.24°C 🥵  970‰
      $9 #167  ~54 néon                29.06°C 🥵  967‰
     $10 #500  ~13 caravelle           28.74°C 🥵  963‰
     $11 #208  ~49 éclairage           28.34°C 🥵  960‰
     $17 #318  ~39 nocturne            24.88°C 😎  892‰
     $85   #9      éclair              16.82°C 🥶
    $446 #484      photique            -0.04°C 🧊
