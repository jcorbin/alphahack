# 2026-03-18

- 🔗 spaceword.org 🧩 2026-03-17 🏁 score 2168 ranked 39.0% 115/295 ⏱️ 4:58:43.071007
- 🔗 alfagok.diginaut.net 🧩 #501 🥳 26 ⏱️ 0:00:36.919660
- 🔗 alphaguess.com 🧩 #968 🥳 28 ⏱️ 0:00:32.662790
- 🔗 dontwordle.com 🧩 #1394 🥳 6 ⏱️ 0:01:53.359341
- 🔗 dictionary.com hurdle 🧩 #1537 🥳 20 ⏱️ 0:03:36.655045
- 🔗 Quordle Classic 🧩 #1514 😦 score:27 ⏱️ 0:01:42.079645
- 🔗 Octordle Classic 🧩 #1514 🥳 score:65 ⏱️ 0:03:40.711350
- 🔗 squareword.org 🧩 #1507 🥳 7 ⏱️ 0:01:42.252317
- 🔗 cemantle.certitudes.org 🧩 #1444 🥳 138 ⏱️ 0:05:48.444548
- 🔗 cemantix.certitudes.org 🧩 #1477 🥳 27 ⏱️ 0:00:19.927854

# Dev

## WIP

- new puzzle: https://fubargames.se/squardle/

- hurdle: add novel words to wordlist

- meta:
  - reprise SolverHarness around `do_sol_*`, re-use them under `do_solve`

- ui:
  - Handle -- stabilizing core over Listing
  - Shell -- minimizing over Handle
- meta: rework command model over Shell
- finish `StoredLog.load` decomposition

## TODO

- semantic:
  - allow "stop after next prompt done" interrupt
  - factor out executive multi-strategy full-auto loop around the current
    best/recent "broad" strategy
  - add a "spike"/"depth" strategy that just tried to chase top-N
  - add model attribution to progress table
  - add used/explored/exploited/attempted counts to prog table
  - ... use such count to get better coverage over hot words
  - ... may replace `~N` scoring

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

















# [spaceword.org](spaceword.org) 🧩 2026-03-17 🏁 score 2168 ranked 39.0% 115/295 ⏱️ 4:58:43.071007

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 115/295

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ L O _ _ R _ _ O _   
      _ O W T _ I _ _ B _   
      _ B L E E D _ _ E _   
      _ _ _ E X E Q U Y _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #501 🥳 26 ⏱️ 0:00:36.919660

🤔 26 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199609 [199609] lij       q0  ? ␅
    @+199609 [199609] lij       q1  ? after
    @+199609 [199609] lij       q2  ? ␅
    @+199609 [199609] lij       q3  ? after
    @+299483 [299483] schro     q4  ? ␅
    @+299483 [299483] schro     q5  ? after
    @+349467 [349467] vakantie  q6  ? ␅
    @+349467 [349467] vakantie  q7  ? after
    @+374207 [374207] vrij      q8  ? ␅
    @+374207 [374207] vrij      q9  ? after
    @+386744 [386744] wind      q10 ? ␅
    @+386744 [386744] wind      q11 ? after
    @+393161 [393161] zelfmoord q12 ? ␅
    @+393161 [393161] zelfmoord q13 ? after
    @+396369 [396369] zone      q14 ? ␅
    @+396369 [396369] zone      q15 ? after
    @+397115 [397115] zout      q18 ? ␅
    @+397115 [397115] zout      q19 ? after
    @+397208 [397208] zoutst    q22 ? ␅
    @+397208 [397208] zoutst    q23 ? after
    @+397251 [397251] zoveel    q24 ? ␅
    @+397251 [397251] zoveel    q25 ? it
    @+397251 [397251] zoveel    done. it
    @+397299 [397299] zuid      q20 ? ␅
    @+397299 [397299] zuid      q21 ? before
    @+397994 [397994] zuurstof  q16 ? ␅
    @+397994 [397994] zuurstof  q17 ? before

# [alphaguess.com](alphaguess.com) 🧩 #968 🥳 28 ⏱️ 0:00:32.662790

🤔 28 attempts
📜 1 sessions

    @       [    0] aa          
    @+2     [    2] aahed       
    @+5876  [ 5876] angel       q10 ? ␅
    @+5876  [ 5876] angel       q11 ? after
    @+6041  [ 6041] animal      q18 ? ␅
    @+6041  [ 6041] animal      q19 ? after
    @+6143  [ 6143] ankle       q20 ? ␅
    @+6143  [ 6143] ankle       q21 ? after
    @+6194  [ 6194] annex       q22 ? ␅
    @+6194  [ 6194] annex       q23 ? after
    @+6224  [ 6224] annotations q24 ? ␅
    @+6224  [ 6224] annotations q25 ? after
    @+6236  [ 6236] annoy       q26 ? ␅
    @+6236  [ 6236] annoy       q27 ? it
    @+6236  [ 6236] annoy       done. it
    @+6254  [ 6254] annuitants  q16 ? ␅
    @+6254  [ 6254] annuitants  q17 ? before
    @+6632  [ 6632] anti        q14 ? ␅
    @+6632  [ 6632] anti        q15 ? before
    @+8323  [ 8323] ar          q12 ? ␅
    @+8323  [ 8323] ar          q13 ? before
    @+11764 [11764] back        q8  ? ␅
    @+11764 [11764] back        q9  ? before
    @+23682 [23682] camp        q6  ? ␅
    @+23682 [23682] camp        q7  ? before
    @+47381 [47381] dis         q4  ? ␅
    @+47381 [47381] dis         q5  ? before
    @+98217 [98217] mach        q0  ? ␅
    @+98217 [98217] mach        q1  ? after
    @+98217 [98217] mach        q2  ? ␅
    @+98217 [98217] mach        q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1394 🥳 6 ⏱️ 0:01:53.359341

📜 1 sessions
💰 score: 48

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:PEEVE n n n n n remain:5924
    ⬜⬜⬜⬜⬜ tried:KININ n n n n n remain:2597
    ⬜⬜⬜⬜⬜ tried:YUMMY n n n n n remain:1051
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:303
    ⬜🟩⬜⬜⬜ tried:BOFFO n Y n n n remain:34
    🟨🟩⬜🟨⬜ tried:SOJAS m Y n m n remain:6

    Undos used: 3

      6 words remaining
    x 8 unused letters
    = 48 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1537 🥳 20 ⏱️ 0:03:36.655045

📜 1 sessions
💰 score: 9600

    5/6
    RAISE ⬜⬜⬜⬜🟩
    LONGE ⬜⬜⬜⬜🟩
    CHUTE ⬜⬜🟨⬜🟩
    UPBYE 🟨⬜⬜⬜🟩
    QUEUE 🟩🟩🟩🟩🟩
    4/6
    QUEUE ⬜🟩⬜⬜⬜
    AUTOS ⬜🟩⬜⬜⬜
    LUDIC 🟨🟩⬜⬜🟨
    CURLY 🟩🟩🟩🟩🟩
    5/6
    CURLY 🟩🟩⬜⬜⬜
    CUTIS 🟩🟩⬜🟩⬜
    CUMIN 🟩🟩⬜🟩⬜
    CUBIC 🟩🟩⬜🟩⬜
    CUPID 🟩🟩🟩🟩🟩
    4/6
    CUPID ⬜⬜⬜🟨⬜
    SIREN ⬜🟩🟨🟩🟨
    FINER ⬜🟩🟩🟩🟩
    LINER 🟩🟩🟩🟩🟩
    Final 2/2
    DORTY 🟨⬜🟩🟨🟩
    TARDY 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1514 😦 score:27 ⏱️ 0:01:42.079645

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. CLIFF attempts:5 score:5
2. EXPEL attempts:6 score:6
3. PRI_E -ABCDFGKLMNOSTXY attempts:9 score:-1
4. FROCK attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1514 🥳 score:65 ⏱️ 0:03:40.711350

📜 1 sessions

Octordle Classic

1. QUEEN attempts:5 score:5
2. FLOUT attempts:8 score:8
3. FUNGI attempts:7 score:7
4. FUNNY attempts:9 score:9
5. RETRY attempts:3 score:3
6. OUTER attempts:10 score:10
7. ELDER attempts:11 score:11
8. SHORT attempts:12 score:12

# [squareword.org](squareword.org) 🧩 #1507 🥳 7 ⏱️ 0:01:42.252317

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟨 🟨
    🟩 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P S A L M
    A T R I A
    P O S E R
    A L O N G
    S E N S E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1444 🥳 138 ⏱️ 0:05:48.444548

🤔 139 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 38 chat prompts
🤖 5 gemma3:27b replies
🤖 33 dolphin3:latest replies
😎   7 🥶 127 🧊   4

      $1 #139 grace          100.00°C 🥳 1000‰ ~135 used:0  [134]  source:gemma3  
      $2  #29 canticle        36.38°C 😎  895‰   ~8 used:31 [7]    source:dolphin3
      $3 #137 devotion        33.99°C 😎  801‰   ~1 used:0  [0]    source:gemma3  
      $4  #88 diminuendo      32.59°C 😎  703‰   ~7 used:16 [6]    source:dolphin3
      $5  #84 adagio          31.91°C 😎  638‰   ~4 used:8  [3]    source:dolphin3
      $6 #135 solemnity       31.58°C 😎  609‰   ~2 used:1  [1]    source:gemma3  
      $7 #120 lyricism        29.40°C 😎  328‰   ~5 used:8  [4]    source:dolphin3
      $8 #106 arioso          29.27°C 😎  307‰   ~6 used:8  [5]    source:dolphin3
      $9  #24 aria            27.53°C 😎    3‰   ~3 used:7  [2]    source:dolphin3
     $10  #92 pianissimo      26.96°C 🥶        ~13 used:0  [12]   source:dolphin3
     $11  #46 serenade        26.93°C 🥶        ~11 used:3  [10]   source:dolphin3
     $12 #100 decrescendo     25.29°C 🥶        ~14 used:0  [13]   source:dolphin3
     $13  #71 psalm           25.01°C 🥶        ~15 used:0  [14]   source:dolphin3
    $136   #5 parrot          -0.33°C 🧊       ~136 used:0  [135]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1477 🥳 27 ⏱️ 0:00:19.927854

🤔 28 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 5 chat prompts
🤖 5 dolphin3:latest replies
🔥 1 🥵 4 😎 7 🥶 6 🧊 9

     $1 #28 discipline     100.00°C 🥳 1000‰ ~19 used:0 [18]  source:dolphin3
     $2 #12 enseignement    63.38°C 🔥  998‰  ~1 used:4 [0]   source:dolphin3
     $3 #14 professeur      45.62°C 🥵  969‰  ~2 used:1 [1]   source:dolphin3
     $4 #17 apprentissage   41.99°C 🥵  952‰  ~3 used:0 [2]   source:dolphin3
     $5 #16 étudiant        40.04°C 🥵  930‰  ~4 used:0 [3]   source:dolphin3
     $6 #27 classe          39.97°C 🥵  927‰  ~5 used:0 [4]   source:dolphin3
     $7 #11 école           37.62°C 😎  890‰  ~6 used:1 [5]   source:dolphin3
     $8 #18 devoir          34.67°C 😎  795‰  ~7 used:0 [6]   source:dolphin3
     $9 #22 programme       31.29°C 😎  633‰  ~8 used:0 [7]   source:dolphin3
    $10 #13 cours           30.36°C 😎  555‰  ~9 used:0 [8]   source:dolphin3
    $11 #23 question        28.58°C 😎  410‰ ~10 used:0 [9]   source:dolphin3
    $12 #19 examen          27.61°C 😎  308‰ ~11 used:0 [10]  source:dolphin3
    $14 #25 bibliothèque    21.09°C 🥶       ~13 used:0 [12]  source:dolphin3
    $20  #6 napoléon        -0.06°C 🧊       ~20 used:0 [19]  source:dolphin3
