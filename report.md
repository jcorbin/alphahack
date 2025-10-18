# 2025-10-19

- 🔗 spaceword.org 🧩 2025-10-18 🏁 score 2168 ranked 26.7% 73/273 ⏱️ 4:56:49.677307
- 🔗 alfagok.diginaut.net 🧩 #351 🥳 10 ⏱️ 0:00:29.748194
- 🔗 alphaguess.com 🧩 #817 🥳 12 ⏱️ 0:00:23.040983
- 🔗 squareword.org 🧩 #1357 🥳 11 ⏱️ 0:03:48.329326
- 🔗 dictionary.com hurdle 🧩 #1387 😦 21 ⏱️ 0:03:24.875331
- 🔗 dontwordle.com 🧩 #1244 🥳 6 ⏱️ 0:01:10.168565
- 🔗 cemantle.certitudes.org 🧩 #1294 🥳 422 ⏱️ 0:12:14.311906
- 🔗 cemantix.certitudes.org 🧩 #1327 🥳 878 ⏱️ 0:33:28.461602

# 2025-10-20

- 🔗 spaceword.org 🧩 2025-10-19 🏗️ score 2168 current ranking 72/167 ⏱️ 0:09:48.349262

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






# spaceword.org 🧩 2025-10-18 🏁 score 2168 ranked 26.7% 73/273 ⏱️ 4:56:49.677307

📜 6 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 73/273

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ M _ _ R _ O X _   
      _ D A I Q U I R I _   
      _ A Y _ _ E _ T _ _   
      _ G O J I S _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #351 🥳 10 ⏱️ 0:00:29.748194

🤔 10 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+49847  [ 49847] boks      q3  ? after
    @+74758  [ 74758] dc        q5  ? after
    @+77730  [ 77730] der       q8  ? after
    @+79233  [ 79233] dicht     q9  ? it
    @+79233  [ 79233] dicht     done. it
    @+80891  [ 80891] dijk      q7  ? before
    @+87218  [ 87218] draag     q6  ? before
    @+99745  [ 99745] ex        q2  ? before
    @+199830 [199830] lijm      q0  ? after
    @+199830 [199830] lijm      q1  ? before

# alphaguess.com 🧩 #817 🥳 12 ⏱️ 0:00:23.040983

🤔 12 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+47392 [47392] dis       q2  ? after
    @+60095 [60095] face      q4  ? after
    @+61631 [61631] fen       q7  ? after
    @+62435 [62435] fila      q8  ? after
    @+62512 [62512] fill      q11 ? it
    @+62512 [62512] fill      done. it
    @+62631 [62631] fin       q10 ? before
    @+62838 [62838] fire      q9  ? before
    @+63251 [63251] flag      q6  ? before
    @+66451 [66451] french    q5  ? before
    @+72812 [72812] gremolata q3  ? before
    @+98231 [98231] mach      q0  ? after
    @+98231 [98231] mach      q1  ? before

# squareword.org 🧩 #1357 🥳 11 ⏱️ 0:03:48.329326

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟨 🟩 🟨 🟩 🟩
    🟨 🟨 🟨 🟨 🟧
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P A P A L
    E E R I E
    E R O D E
    R I V E R
    S E E D Y

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1387 😦 21 ⏱️ 0:03:24.875331

📜 2 sessions
💰 score: 4580

    4/6
    SNARE 🟨⬜🟨⬜⬜
    TAPIS ⬜🟩⬜⬜🟩
    CALMS ⬜🟩⬜🟨🟩
    MAGUS 🟩🟩🟩🟩🟩
    4/6
    MAGUS ⬜⬜⬜⬜⬜
    TRIOL ⬜⬜🟨⬜⬜
    VINED 🟨🟩⬜⬜🟨
    DIVVY 🟩🟩🟩🟩🟩
    6/6
    DIVVY ⬜⬜⬜⬜⬜
    SOLAR ⬜⬜🟨⬜⬜
    CLUNG ⬜🟩🟩⬜⬜
    BLUME ⬜🟩🟩🟩🟩
    FLUME ⬜🟩🟩🟩🟩
    PLUME 🟩🟩🟩🟩🟩
    5/6
    PLUME ⬜🟩⬜⬜🟩
    ALKIE 🟨🟩⬜⬜🟩
    BLASE ⬜🟩🟩⬜🟩
    GLADE 🟩🟩🟩⬜🟩
    GLARE 🟩🟩🟩🟩🟩
    Final 2/2
    SHARE 🟩⬜🟩🟩🟩
    SCARE 🟩⬜🟩🟩🟩
    FAIL: STARE

# dontwordle.com 🧩 #1244 🥳 6 ⏱️ 0:01:10.168565

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:WHOOF n n n n n remain:6599
    ⬜⬜⬜⬜⬜ tried:MINIM n n n n n remain:2801
    ⬜⬜⬜⬜⬜ tried:YUPPY n n n n n remain:1170
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:278
    ⬜🟨⬜⬜⬜ tried:CEDED n m n n n remain:19
    🟩⬜🟨🟩⬜ tried:STETS Y n m Y n remain:1

    Undos used: 2

      1 words remaining
    x 8 unused letters
    = 8 total score

# cemantle.certitudes.org 🧩 #1294 🥳 422 ⏱️ 0:12:14.311906

🤔 423 attempts
📜 1 sessions
🫧 18 chat sessions
⁉️ 116 chat prompts
🤖 40 llama3.2:latest replies
🤖 76 gemma3:latest replies
🔥   3 🥵  15 😎  67 🥶 325 🧊  12

      $1 #423   ~1 induce                 100.00°C 🥳 1000‰
      $2 #185  ~51 inhibit                 54.15°C 🔥  996‰
      $3 #162  ~57 suppress                51.89°C 🔥  995‰
      $4 #126  ~75 counteract              49.82°C 🔥  990‰
      $5 #166  ~55 deaden                  48.17°C 🥵  985‰
      $6 #398   ~3 coerce                  47.51°C 🥵  984‰
      $7 #272  ~29 modulate                47.41°C 🥵  982‰
      $8 #216  ~44 attenuate               46.77°C 🥵  979‰
      $9 #411   ~2 compel                  46.64°C 🥵  978‰
     $10 #137  ~70 stifle                  43.69°C 🥵  969‰
     $11 #215  ~45 ameliorate              43.21°C 🥵  964‰
     $20 #250  ~31 relieve                 38.43°C 😎  897‰
     $87 #176      eradicate               29.34°C 🥶
    $412 #210      cordon                  -0.43°C 🧊

# spaceword.org 🧩 2025-10-19 🏗️ score 2168 current ranking 72/167 ⏱️ 0:09:48.349262

📜 2 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 72/167

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ D _ A W _   
      _ Q _ Y A U T I A _   
      _ I _ _ _ O I _ F _   
      _ S E X I S T _ F _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# cemantix.certitudes.org 🧩 #1327 🥳 878 ⏱️ 0:33:28.461602

🤔 879 attempts
📜 2 sessions
🫧 38 chat sessions
⁉️ 197 chat prompts
🤖 72 gemma3:latest replies
🤖 123 llama3.2:latest replies
😱   1 🔥   7 🥵  25 😎  70 🥶 531 🧊 244

      $1 #879   ~1 minuit             100.00°C 🥳 1000‰
      $2 #512  ~37 soir                58.07°C 😱  999‰
      $3 #324  ~54 matin               51.42°C 🔥  998‰
      $4  #73  ~97 nuit                51.24°C 🔥  997‰
      $5  #98  ~92 heure               47.23°C 🔥  996‰
      $6 #597  ~30 midi                46.61°C 🔥  995‰
      $7 #493  ~38 dimanche            43.68°C 🔥  994‰
      $8 #172  ~72 soirée              41.85°C 🔥  993‰
      $9 #166  ~73 coucher             41.55°C 🔥  992‰
     $10 #133  ~77 nocturne            36.51°C 🥵  984‰
     $11 #688  ~19 vêpres              35.36°C 🥵  981‰
     $35 #121  ~83 avant               26.45°C 😎  895‰
    $105 #140      réception           17.69°C 🥶
    $636 #738      présent             -0.01°C 🧊
