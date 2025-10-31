# 2025-11-01

- 🔗 spaceword.org 🧩 2025-10-31 🏁 score 2173 ranked 3.5% 13/368 ⏱️ 0:31:30.702471
- 🔗 alfagok.diginaut.net 🧩 #364 🥳 8 ⏱️ 0:00:31.293179
- 🔗 alphaguess.com 🧩 #830 🥳 16 ⏱️ 0:00:33.958172
- 🔗 squareword.org 🧩 #1370 🥳 8 ⏱️ 0:01:59.943606
- 🔗 dictionary.com hurdle 🧩 #1400 🥳 17 ⏱️ 0:05:46.630869
- 🔗 dontwordle.com 🧩 #1257 🥳 6 ⏱️ 0:02:24.508046
- 🔗 cemantle.certitudes.org 🧩 #1307 🥳 375 ⏱️ 0:12:24.313852
- 🔗 cemantix.certitudes.org 🧩 #1340 🥳 279 ⏱️ 0:15:27.426289

# Dev

## WIP

ui: Shell / Handle revolution

### TODO debug

```
/meta/solvers> ../sh
Traceback (most recent call last):
  File "/home/jcorbin/alphaguess/./meta.py", line 1453, in <module>
    Meta.main()
    ~~~~~~~~~^^
  File "/home/jcorbin/alphaguess/ui.py", line 1968, in main
    return ui.run(self)
           ~~~~~~^^^^^^
  File "/home/jcorbin/alphaguess/ui.py", line 1949, in run
    self.interact(state)
    ~~~~~~~~~~~~~^^^^^^^
  File "/home/jcorbin/alphaguess/ui.py", line 1836, in interact
    self.call_state(state)
    ~~~~~~~~~~~~~~~^^^^^^^
  File "/home/jcorbin/alphaguess/ui.py", line 1887, in call_state
    nxt = state(self)
  File "/home/jcorbin/alphaguess/./meta.py", line 506, in __call__
    ui.run(super().__call__)
    ~~~~~~^^^^^^^^^^^^^^^^^^
  File "/home/jcorbin/alphaguess/ui.py", line 1949, in run
    self.interact(state)
    ~~~~~~~~~~~~~^^^^^^^
  File "/home/jcorbin/alphaguess/ui.py", line 1836, in interact
    self.call_state(state)
    ~~~~~~~~~~~~~~~^^^^^^^
  File "/home/jcorbin/alphaguess/ui.py", line 1887, in call_state
    nxt = state(self)
  File "/home/jcorbin/alphaguess/ui.py", line 1989, in __call__
    return self.shell(ui)
           ~~~~~~~~~~^^^^
  File "/home/jcorbin/alphaguess/ui.py", line 1224, in __call__
    hndl = self.resolve(next(tokens, None))
  File "/home/jcorbin/alphaguess/ui.py", line 1209, in resolve
    for h in self.search(cmd):
             ~~~~~~~~~~~^^^^^
  File "/home/jcorbin/alphaguess/ui.py", line 1205, in search
    yield self.root[cmd]
          ~~~~~~~~~^^^^^
  File "/home/jcorbin/alphaguess/ui.py", line 358, in __getitem__
    return Handle(self, key)
  File "/home/jcorbin/alphaguess/ui.py", line 259, in __init__
    raise KeyError(f'{self.path}/..')
KeyError: '//..'
```

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






# spaceword.org 🧩 2025-10-31 🏁 score 2173 ranked 3.5% 13/368 ⏱️ 0:31:30.702471

📜 6 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 13/368

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ R _ J O _ P _ L A   
      _ E Q U I N E _ E W   
      _ _ _ G L E E M E N   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #364 🥳 8 ⏱️ 0:00:31.293179

🤔 8 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199827 [199827] lijm      q0 ? after
    @+247725 [247725] op        q2 ? after
    @+250914 [250914] oproep    q6 ? after
    @+252517 [252517] oranje    q7 ? it
    @+252517 [252517] oranje    done. it
    @+254130 [254130] out       q5 ? before
    @+260612 [260612] pater     q4 ? before
    @+273531 [273531] proef     q3 ? before
    @+299729 [299729] schub     q1 ? before

# alphaguess.com 🧩 #830 🥳 16 ⏱️ 0:00:33.958172

🤔 16 attempts
📜 1 sessions

    @        [     0] aa          
    @+1      [     1] aah         
    @+2      [     2] aahed       
    @+3      [     3] aahing      
    @+98226  [ 98226] mach        q0  ? after
    @+147331 [147331] rho         q1  ? after
    @+159613 [159613] slug        q3  ? after
    @+165767 [165767] stint       q4  ? after
    @+167291 [167291] sub         q6  ? after
    @+168032 [168032] subs        q7  ? after
    @+168054 [168054] subscript   q12 ? after
    @+168068 [168068] subsegments q13 ? after
    @+168075 [168075] subsequence q14 ? after
    @+168077 [168077] subsequent  q15 ? it
    @+168077 [168077] subsequent  done. it
    @+168081 [168081] subseres    q11 ? before
    @+168130 [168130] subsist     q10 ? before
    @+168227 [168227] substratums q9  ? before
    @+168421 [168421] subway      q8  ? before
    @+168817 [168817] sulfur      q5  ? before
    @+171931 [171931] tag         q2  ? before

# squareword.org 🧩 #1370 🥳 8 ⏱️ 0:01:59.943606

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A L B U M
    B O R N E
    A C I D S
    T U N E S
    E M E R Y

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1400 🥳 17 ⏱️ 0:05:46.630869

📜 1 sessions
💰 score: 9900

    4/6
    MARSE ⬜🟨🟨🟩🟩
    PRASE ⬜🟩🟨🟩🟩
    ARISE 🟩🟩⬜🟩🟩
    AROSE 🟩🟩🟩🟩🟩
    4/6
    AROSE ⬜🟨⬜⬜🟨
    RILEY 🟨⬜⬜🟩⬜
    TUNER ⬜⬜🟨🟩🟩
    NEWER 🟩🟩🟩🟩🟩
    5/6
    NEWER ⬜⬜⬜⬜⬜
    LOAMY 🟨⬜⬜⬜⬜
    BUILT ⬜⬜🟩🟨⬜
    CLIPS 🟩🟩🟩⬜⬜
    CLICK 🟩🟩🟩🟩🟩
    3/6
    CLICK ⬜⬜🟨⬜⬜
    RINSE 🟨🟨⬜🟨🟨
    SERIF 🟩🟩🟩🟩🟩
    Final 1/2
    QUITE 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1257 🥳 6 ⏱️ 0:02:24.508046

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:WANNA n n n n n remain:5495
    ⬜⬜⬜⬜⬜ tried:JUJUS n n n n n remain:1953
    ⬜⬜⬜⬜⬜ tried:CHOCK n n n n n remain:622
    ⬜⬜⬜🟨⬜ tried:PYGMY n n n m n remain:62
    🟨🟩⬜⬜⬜ tried:MELEE m Y n n n remain:5
    ⬜🟩🟩🟩⬜ tried:BEMIX n Y Y Y n remain:2

    Undos used: 2

      2 words remaining
    x 7 unused letters
    = 14 total score

# cemantle.certitudes.org 🧩 #1307 🥳 375 ⏱️ 0:12:24.313852

🤔 376 attempts
📜 1 sessions
🫧 12 chat sessions
⁉️ 74 chat prompts
🤖 23 llama3.2:latest replies
🤖 51 gemma3:latest replies
😱   1 🔥   2 🥵   8 😎  40 🥶 312 🧊  12

      $1 #376   ~1 machinery      100.00°C 🥳 1000‰
      $2 #373   ~3 equipment       59.41°C 😱  999‰
      $3 #276  ~24 machine         52.61°C 🔥  998‰
      $4 #184  ~38 metalworking    45.39°C 🔥  994‰
      $5 #109  ~42 welding         40.08°C 🥵  985‰
      $6 #274  ~25 hydraulic       39.43°C 🥵  981‰
      $7 #259  ~28 lathe           38.45°C 🥵  977‰
      $8  #64  ~51 steel           37.78°C 🥵  972‰
      $9  #87  ~47 grinding        36.62°C 🥵  960‰
     $10 #352   ~8 sander          33.64°C 🥵  929‰
     $11 #252  ~29 grinder         32.62°C 🥵  912‰
     $13  #93  ~45 metallurgy      31.52°C 😎  892‰
     $53 #343      moulder         22.47°C 🥶
    $365 #339      fitting         -0.26°C 🧊

# cemantix.certitudes.org 🧩 #1340 🥳 279 ⏱️ 0:15:27.426289

🤔 280 attempts
📜 1 sessions
🫧 13 chat sessions
⁉️ 85 chat prompts
🤖 24 llama3.2:latest replies
🤖 61 gemma3:latest replies
🔥   4 🥵  22 😎  89 🥶 138 🧊  26

      $1 #280   ~1 autonomie          100.00°C 🥳 1000‰
      $2  #76 ~103 capacité            53.38°C 🔥  997‰
      $3  #97  ~93 compétence          48.17°C 🔥  996‰
      $4 #254  ~14 autonomisation      45.71°C 🔥  992‰
      $5 #180  ~51 polyvalence         44.92°C 🔥  990‰
      $6 #266   ~7 responsabilité      44.88°C 🥵  989‰
      $7 #236  ~25 individuel          44.16°C 🥵  987‰
      $8 #179  ~52 adaptabilité        43.95°C 🥵  986‰
      $9  #38 ~116 épanouissement      41.30°C 🥵  978‰
     $10 #146  ~71 objectif            40.66°C 🥵  973‰
     $11 #278   ~3 organisation        40.58°C 🥵  971‰
     $28 #197  ~39 logique             35.48°C 😎  897‰
    $117  #27      fluidité            23.12°C 🥶
    $255 #239      ligne               -0.82°C 🧊
