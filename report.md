# 2025-10-27

- 🔗 spaceword.org 🧩 2025-10-26 🏁 score 2173 ranked 5.1% 19/371 ⏱️ 1:48:55.290597
- 🔗 alfagok.diginaut.net 🧩 #359 🥳 18 ⏱️ 0:00:57.086170
- 🔗 alphaguess.com 🧩 #825 🥳 15 ⏱️ 0:00:46.966429
- 🔗 squareword.org 🧩 #1365 🥳 8 ⏱️ 0:02:30.515893
- 🔗 dictionary.com hurdle 🧩 #1395 🥳 18 ⏱️ 0:02:45.001893
- 🔗 dontwordle.com 🧩 #1252 🥳 6 ⏱️ 0:01:17.018523
- 🔗 cemantle.certitudes.org 🧩 #1302 🥳 106 ⏱️ 0:02:26.900010
- 🔗 cemantix.certitudes.org 🧩 #1335 🥳 436 ⏱️ 0:18:04.505138

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

# spaceword.org 🧩 2025-10-26 🏁 score 2173 ranked 5.1% 19/371 ⏱️ 1:48:55.290597

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 19/371

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ Z A P _ _ _   
      _ _ _ _ _ _ R _ _ _   
      _ _ _ _ V A U _ _ _   
      _ _ _ _ _ E N _ _ _   
      _ _ _ _ A R E _ _ _   
      _ _ _ _ T O R _ _ _   
      _ _ _ _ _ B _ _ _ _   
      _ _ _ _ X I _ _ _ _   
      _ _ _ _ I C E _ _ _   

# alfagok.diginaut.net 🧩 #359 🥳 18 ⏱️ 0:00:57.086170

🤔 18 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+1      [     1] &-tekens     
    @+2      [     2] -cijferig    
    @+3      [     3] -e-mail      
    @+199830 [199830] lijm         q0  ? after
    @+299732 [299732] schub        q1  ? after
    @+299732 [299732] schub        q2  ? after
    @+349507 [349507] vakantie     q3  ? after
    @+353075 [353075] ver          q5  ? after
    @+354157 [354157] verdeel      q9  ? after
    @+354287 [354287] verdicht     q12 ? after
    @+354302 [354302] verdien      q14 ? after
    @+354307 [354307] verdienen    q17 ? it
    @+354307 [354307] verdienen    done. it
    @+354314 [354314] verdienste   q16 ? before
    @+354327 [354327] verdiep      q15 ? before
    @+354356 [354356] verdiets     q13 ? before
    @+354431 [354431] verdof       q11 ? before
    @+354706 [354706] verduidelijk q10 ? before
    @+355256 [355256] verg         q8  ? before
    @+358368 [358368] verluieren   q7  ? before
    @+363660 [363660] verzot       q6  ? before
    @+374250 [374250] vrij         q4  ? before

# alphaguess.com 🧩 #825 🥳 15 ⏱️ 0:00:46.966429

🤔 15 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+47391 [47391] dis       q1  ? after
    @+48413 [48413] disorder  q6  ? after
    @+48926 [48926] distain   q7  ? after
    @+49137 [49137] dit       q8  ? after
    @+49206 [49206] diva      q10 ? after
    @+49235 [49235] diver     q11 ? after
    @+49246 [49246] divers    q12 ? after
    @+49256 [49256] diversify q14 ? it
    @+49256 [49256] diversify done. it
    @+49266 [49266] divert    q13 ? before
    @+49285 [49285] divest    q9  ? before
    @+49438 [49438] do        q5  ? before
    @+53407 [53407] el        q4  ? before
    @+60094 [60094] face      q3  ? before
    @+72811 [72811] gremolata q2  ? before
    @+98230 [98230] mach      q0  ? before

# squareword.org 🧩 #1365 🥳 8 ⏱️ 0:02:30.515893

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S H O R T
    T O W E R
    A L I V E
    V E N U E
    E D G E S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1395 🥳 18 ⏱️ 0:02:45.001893

📜 1 sessions
💰 score: 9800

    4/6
    STARE ⬜⬜🟨⬜🟩
    ANOLE 🟨🟨⬜⬜🟩
    NAIVE 🟨🟩⬜⬜🟩
    DANCE 🟩🟩🟩🟩🟩
    4/6
    DANCE 🟩⬜⬜⬜⬜
    DIRTS 🟩🟩⬜🟨⬜
    DIGIT 🟩🟩⬜⬜🟩
    DIVOT 🟩🟩🟩🟩🟩
    4/6
    DIVOT 🟨⬜⬜⬜⬜
    SWARD ⬜⬜⬜⬜🟩
    MULED 🟨⬜⬜🟨🟩
    EMEND 🟩🟩🟩🟩🟩
    5/6
    EMEND ⬜⬜🟩⬜🟩
    OREAD ⬜🟩🟩🟩🟩
    TREAD ⬜🟩🟩🟩🟩
    BREAD ⬜🟩🟩🟩🟩
    DREAD 🟩🟩🟩🟩🟩
    Final 1/2
    LUNCH 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1252 🥳 6 ⏱️ 0:01:17.018523

📜 1 sessions
💰 score: 5

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:QUEUE n n n n n remain:5479
    ⬜⬜⬜⬜⬜ tried:ZIZIT n n n n n remain:2496
    ⬜⬜⬜⬜⬜ tried:SHOJO n n n n n remain:381
    ⬜⬜⬜⬜⬜ tried:PYGMY n n n n n remain:92
    ⬜⬜🟩⬜⬜ tried:ABACA n n Y n n remain:11
    🟩⬜🟩🟩🟩 tried:FRANK Y n Y Y Y remain:1

    Undos used: 2

      1 words remaining
    x 5 unused letters
    = 5 total score

# cemantle.certitudes.org 🧩 #1302 🥳 106 ⏱️ 0:02:26.900010

🤔 107 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 22 chat prompts
🤖 22 gemma3:latest replies
🔥  1 🥵  1 😎  6 🥶 94 🧊  4

      $1 #107   ~1 conventional   100.00°C 🥳 1000‰
      $2  #65   ~6 static          40.61°C 🔥  991‰
      $3  #91   ~2 rigid           39.25°C 🥵  981‰
      $4  #75   ~5 resistant       32.62°C 😎  827‰
      $5  #31   ~9 deterministic   32.60°C 😎  825‰
      $6  #78   ~4 durable         31.01°C 😎  695‰
      $7  #58   ~8 precision       30.36°C 😎  620‰
      $8  #59   ~7 predictable     30.30°C 😎  613‰
      $9  #88   ~3 reliable        29.07°C 😎  406‰
     $10  #14      multiple        25.82°C 🥶
     $11  #53      logic           24.62°C 🥶
     $12  #77      dense           24.62°C 🥶
     $13  #18      complex         24.59°C 🥶
    $104  #96      tense           -1.04°C 🧊

# cemantix.certitudes.org 🧩 #1335 🥳 436 ⏱️ 0:18:04.505138

🤔 437 attempts
📜 1 sessions
🫧 22 chat sessions
⁉️ 131 chat prompts
🤖 102 llama3.2:latest replies
🤖 29 gemma3:latest replies
🔥   3 🥵  25 😎  81 🥶 211 🧊 116

      $1 #437   ~1 inscription       100.00°C 🥳 1000‰
      $2 #425   ~5 admission          57.39°C 🔥  995‰
      $3 #339  ~37 formulaire         56.17°C 🔥  994‰
      $4 #216  ~73 renseignement      52.13°C 🔥  992‰
      $5 #295  ~52 justificatif       49.70°C 🥵  989‰
      $6 #414  ~10 obligatoire        47.70°C 🥵  985‰
      $7 #433   ~2 candidature        47.09°C 🥵  984‰
      $8 #234  ~69 attestation        46.72°C 🥵  983‰
      $9 #100 ~103 dossier            46.65°C 🥵  982‰
     $10 #335  ~39 demande            46.20°C 🥵  981‰
     $11 #210  ~78 validation         42.99°C 🥵  976‰
     $30 #331  ~42 relevé             34.71°C 😎  897‰
    $111 #347      centre             17.78°C 🥶
    $322 #361      solvabilité        -0.07°C 🧊
