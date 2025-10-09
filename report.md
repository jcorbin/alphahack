# 2025-10-10

- 🔗 spaceword.org 🧩 2025-10-09 🏁 score 2173 ranked 5.7% 22/383 ⏱️ 0:40:50.657269
- 🔗 alfagok.diginaut.net 🧩 #342 🥳 17 ⏱️ 0:00:47.677040
- 🔗 alphaguess.com 🧩 #808 🥳 15 ⏱️ 0:00:37.824894
- 🔗 squareword.org 🧩 #1348 🥳 8 ⏱️ 0:02:28.070851
- 🔗 dictionary.com hurdle 🧩 #1378 🥳 21 ⏱️ 0:03:48.443729
- 🔗 dontwordle.com 🧩 #1235 🥳 6 ⏱️ 0:01:27.196253
- 🔗 cemantle.certitudes.org 🧩 #1285 🥳 341 ⏱️ 0:03:22.405257
- 🔗 cemantix.certitudes.org 🧩 #1318 🥳 72 ⏱️ 0:00:42.247862

# Dev

## WIP

- meta: review works up to rc branch progression

- StoredLog: added one-shot canned input from CLI args
  `python whatever.py some/log/maybe -- cmd1 -- cmd2 ...`
- StoredLog: fixed elapsed time reporting

## TODO

- hurdle: report wasn't right out of #1373 -- was missing first few rounds

- square: finish questioning work

- reuse input injection mechanism from store
  - wherever the current input injection usage is
  - and also to allow more seamless meta log continue ...

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



# spaceword.org 🧩 2025-10-09 🏁 score 2173 ranked 5.7% 22/383 ⏱️ 0:40:50.657269

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 22/383

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ Z O O _ J _ H I T   
      _ _ _ O X I D A S E   
      _ _ C H I N E D _ A   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #342 🥳 17 ⏱️ 0:00:47.677040

🤔 17 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+1      [     1] &-tekens    
    @+2      [     2] -cijferig   
    @+3      [     3] -e-mail     
    @+199834 [199834] lijm        q0  ? after
    @+299749 [299749] schub       q1  ? after
    @+349532 [349532] vakantie    q2  ? after
    @+349532 [349532] vakantie    q3  ? after
    @+353100 [353100] ver         q5  ? after
    @+363685 [363685] verzot      q6  ? after
    @+364535 [364535] vier        q9  ? after
    @+364804 [364804] vieux       q12 ? after
    @+364878 [364878] vijf        q13 ? after
    @+364972 [364972] vijfhonderd q14 ? after
    @+365023 [365023] vijftal     q15 ? after
    @+365042 [365042] vijftig     q16 ? it
    @+365042 [365042] vijftig     done. it
    @+365072 [365072] vijgen      q10 ? before
    @+365624 [365624] vis         q8  ? before
    @+368697 [368697] voetbal     q7  ? before
    @+374275 [374275] vrij        q4  ? before

# alphaguess.com 🧩 #808 🥳 15 ⏱️ 0:00:37.824894

🤔 15 attempts
📜 1 sessions

    @       [    0] aa          
    @+1     [    1] aah         
    @+2     [    2] aahed       
    @+3     [    3] aahing      
    @+47392 [47392] dis         q1  ? after
    @+60095 [60095] face        q3  ? after
    @+66451 [66451] french      q4  ? after
    @+69632 [69632] geosyncline q5  ? after
    @+69936 [69936] gi          q8  ? after
    @+69950 [69950] gib         q11 ? after
    @+69989 [69989] gid         q12 ? after
    @+70008 [70008] gif         q13 ? after
    @+70010 [70010] gift        q14 ? it
    @+70010 [70010] gift        done. it
    @+70029 [70029] gig         q10 ? before
    @+70168 [70168] ginger      q9  ? before
    @+70423 [70423] glam        q7  ? before
    @+71223 [71223] gnomon      q6  ? before
    @+72812 [72812] gremolata   q2  ? before
    @+98231 [98231] mach        q0  ? before

# squareword.org 🧩 #1348 🥳 8 ⏱️ 0:02:28.070851

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟨 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S L A S H
    W A S T E
    E T H E R
    A H E A D
    T E N D S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1378 🥳 21 ⏱️ 0:03:48.443729

📜 1 sessions
💰 score: 9500

    5/6
    STORE 🟨⬜⬜⬜⬜
    HAILS ⬜🟨⬜⬜🟩
    QUAGS ⬜⬜🟨⬜🟩
    CYMAS ⬜🟨⬜🟨🟩
    ABYSS 🟩🟩🟩🟩🟩
    6/6
    ABYSS 🟨⬜⬜⬜⬜
    CARET 🟨🟩🟨🟩⬜
    MACER ⬜🟩🟩🟩🟩
    PACER ⬜🟩🟩🟩🟩
    FACER ⬜🟩🟩🟩🟩
    RACER 🟩🟩🟩🟩🟩
    6/6
    RACER ⬜⬜⬜🟨⬜
    LEGIT ⬜🟨⬜🟨🟨
    WHITE ⬜⬜🟩🟩🟩
    SPITE 🟩⬜🟩🟩🟩
    SUITE 🟩⬜🟩🟩🟩
    SMITE 🟩🟩🟩🟩🟩
    3/6
    SMITE ⬜⬜🟩⬜🟩
    ALIVE 🟩🟩🟩⬜🟩
    ALIKE 🟩🟩🟩🟩🟩
    Final 1/2
    ORBIT 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1235 🥳 6 ⏱️ 0:01:27.196253

📜 1 sessions
💰 score: 49

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:8089
    ⬜⬜⬜⬜⬜ tried:EBBED n n n n n remain:3180
    ⬜⬜⬜⬜⬜ tried:KININ n n n n n remain:1218
    ⬜⬜⬜⬜⬜ tried:ROTOR n n n n n remain:222
    ⬜⬜⬜⬜⬜ tried:CHUFF n n n n n remain:46
    🟨⬜🟩⬜⬜ tried:PZAZZ m n Y n n remain:7

    Undos used: 3

      7 words remaining
    x 7 unused letters
    = 49 total score

# cemantle.certitudes.org 🧩 #1285 🥳 341 ⏱️ 0:03:22.405257

🤔 342 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 58 chat prompts
🤖 58 gemma3:12b replies
🔥   3 🥵  29 😎  69 🥶 192 🧊  48

      $1 #342   ~1 founder         100.00°C 🥳 1000‰
      $2 #288  ~24 executive        49.59°C 🔥  992‰
      $3 #232  ~54 pioneer          49.20°C 🔥  991‰
      $4 #286  ~26 director         47.71°C 🔥  990‰
      $5 #246  ~49 organizer        46.57°C 🥵  988‰
      $6 #309  ~14 chairperson      45.01°C 🥵  986‰
      $7 #219  ~60 philanthropist   40.12°C 🥵  982‰
      $8 #226  ~58 visionary        38.75°C 🥵  979‰
      $9 #231  ~55 leader           37.81°C 🥵  977‰
     $10 #235  ~52 activist         37.78°C 🥵  976‰
     $11 #276  ~31 patron           35.85°C 🥵  966‰
     $34 #260  ~41 associate        28.62°C 😎  895‰
    $103 #229      idealist         16.70°C 🥶
    $295  #49      narrative        -0.01°C 🧊

# cemantix.certitudes.org 🧩 #1318 🥳 72 ⏱️ 0:00:42.247862

🤔 73 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 11 chat prompts
🤖 11 gemma3:12b replies
🔥  2 🥵  6 😎 16 🥶 33 🧊 15

     $1 #73  ~1 diagnostic       100.00°C 🥳 1000‰
     $2 #35 ~21 analyse           53.76°C 🔥  996‰
     $3 #62  ~6 évaluation        52.39°C 🔥  995‰
     $4 #64  ~4 bilan             43.18°C 🥵  976‰
     $5 #49 ~15 indicateur        42.04°C 🥵  968‰
     $6 #36 ~20 amélioration      41.78°C 🥵  964‰
     $7 #61  ~7 étude             41.33°C 🥵  960‰
     $8 #34 ~22 mise              39.35°C 🥵  929‰
     $9 #66  ~3 estimation        38.65°C 🥵  916‰
    $10 #58 ~10 stratégie         34.59°C 😎  764‰
    $11 #72  ~2 contrôle          34.53°C 😎  759‰
    $12 #60  ~8 vérification      34.37°C 😎  752‰
    $26 #65     calcul            26.88°C 🥶
    $59  #4     fenêtre           -1.10°C 🧊
