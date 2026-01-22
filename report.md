# 2026-01-23

- 🔗 spaceword.org 🧩 2026-01-22 🏁 score 2170 ranked 26.8% 84/314 ⏱️ 0:40:16.306128
- 🔗 alfagok.diginaut.net 🧩 #447 🥳 16 ⏱️ 0:00:50.607409
- 🔗 alphaguess.com 🧩 #914 🥳 14 ⏱️ 0:00:47.527978
- 🔗 dontwordle.com 🧩 #1340 😳 6 ⏱️ 0:02:01.425221
- 🔗 dictionary.com hurdle 🧩 #1483 🥳 20 ⏱️ 0:03:32.633241
- 🔗 Quordle Classic 🧩 #1460 🥳 score:22 ⏱️ 0:01:11.695815
- 🔗 Octordle Classic 🧩 #1460 🥳 score:69 ⏱️ 0:04:23.949882
- 🔗 squareword.org 🧩 #1453 🥳 7 ⏱️ 0:01:57.336126
- 🔗 cemantle.certitudes.org 🧩 #1390 🥳 108 ⏱️ 0:05:22.335921
- 🔗 cemantix.certitudes.org 🧩 #1423 🥳 192 ⏱️ 0:03:52.403523

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








# [spaceword.org](spaceword.org) 🧩 2026-01-22 🏁 score 2170 ranked 26.8% 84/314 ⏱️ 0:40:16.306128

📜 4 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 84/314

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ K _ _ W _ _ _   
      _ _ G O T _ O R _ _   
      _ _ U B I Q U E _ _   
      _ _ D O C I L E _ _   
      _ _ E _ _ _ D _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #447 🥳 16 ⏱️ 0:00:50.607409

🤔 16 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199833 [199833] lijm      q0  ? after
    @+299738 [299738] schub     q1  ? after
    @+324308 [324308] sub       q3  ? after
    @+330491 [330491] televisie q5  ? after
    @+331886 [331886] terug     q7  ? after
    @+332628 [332628] test      q8  ? after
    @+333136 [333136] theater   q9  ? after
    @+333417 [333417] thema     q14 ? after
    @+333549 [333549] theorie   q15 ? it
    @+333549 [333549] theorie   done. it
    @+333692 [333692] these     q6  ? before
    @+336904 [336904] toetsing  q4  ? before
    @+349511 [349511] vakantie  q2  ? before

# [alphaguess.com](alphaguess.com) 🧩 #914 🥳 14 ⏱️ 0:00:47.527978

🤔 14 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+11764 [11764] back      q3  ? after
    @+13802 [13802] be        q5  ? after
    @+14779 [14779] bel       q7  ? after
    @+15268 [15268] berascal  q8  ? after
    @+15323 [15323] beriberis q10 ? after
    @+15351 [15351] berrettas q11 ? after
    @+15354 [15354] berry     q13 ? it
    @+15354 [15354] berry     done. it
    @+15361 [15361] berserk   q12 ? before
    @+15378 [15378] bes       q9  ? before
    @+15758 [15758] bewrap    q6  ? before
    @+17715 [17715] blind     q4  ? before
    @+23683 [23683] camp      q2  ? before
    @+47382 [47382] dis       q1  ? before
    @+98220 [98220] mach      q0  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1340 😳 6 ⏱️ 0:02:01.425221

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:VERVE n n n n n remain:5059
    ⬜⬜⬜⬜⬜ tried:ONION n n n n n remain:1356
    ⬜⬜⬜⬜⬜ tried:YUKKY n n n n n remain:418
    🟨⬜⬜⬜⬜ tried:PHPHT m n n n n remain:38
    ⬜⬜🟩⬜🟩 tried:ABAMP n n Y n Y remain:2
    🟩🟩🟩🟩🟩 tried:SCALP Y Y Y Y Y remain:0

    Undos used: 3

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1483 🥳 20 ⏱️ 0:03:32.633241

📜 1 sessions
💰 score: 9600

    5/6
    ROTES ⬜⬜⬜⬜⬜
    INLAY ⬜⬜🟨🟨⬜
    AWFUL 🟨⬜⬜🟨🟨
    LAUGH 🟨🟩🟩⬜⬜
    CAULK 🟩🟩🟩🟩🟩
    4/6
    CAULK 🟩⬜⬜⬜⬜
    CRIME 🟩🟩⬜⬜🟩
    CRONE 🟩🟩⬜⬜🟩
    CREPE 🟩🟩🟩🟩🟩
    4/6
    CREPE ⬜⬜⬜⬜⬜
    INLAY ⬜⬜🟨⬜⬜
    LOTUS 🟨🟩⬜🟨⬜
    WOULD 🟩🟩🟩🟩🟩
    5/6
    WOULD ⬜⬜⬜⬜🟨
    ASIDE ⬜⬜🟨🟨🟨
    DEBIT 🟨🟨⬜🟨⬜
    INDEX 🟨⬜🟩🟩⬜
    CIDER 🟩🟩🟩🟩🟩
    Final 2/2
    QUITE ⬜🟩🟩⬜🟩
    GUISE 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1460 🥳 score:22 ⏱️ 0:01:11.695815

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. WRECK attempts:4 score:4
2. GUARD attempts:5 score:5
3. BELIE attempts:7 score:7
4. BRAVO attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1460 🥳 score:69 ⏱️ 0:04:23.949882

📜 4 sessions

Octordle Classic

1. SPRAY attempts:6 score:6
2. RENEW attempts:8 score:8
3. CASTE attempts:3 score:5
4. SPIRE attempts:6 score:7
5. DRANK attempts:9 score:9
6. WATER attempts:10 score:10
7. MERRY attempts:13 score:13
8. PESKY attempts:11 score:11

# [squareword.org](squareword.org) 🧩 #1453 🥳 7 ⏱️ 0:01:57.336126

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S A T E D
    A D O R E
    T I T A N
    Y E A S T
    R U L E S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1390 🥳 108 ⏱️ 0:05:22.335921

🤔 109 attempts
📜 2 sessions
🫧 7 chat sessions
⁉️ 15 chat prompts
🤖 12 dolphin3:latest replies
🤖 3 glm-4.7-flash:latest replies
🔥  1 🥵  3 😎 24 🥶 71 🧊  9

      $1 #109   ~1 recording     100.00°C 🥳 1000‰
      $2 #102   ~6 music          43.47°C 🔥  993‰
      $3  #40  ~22 singing        34.02°C 🥵  949‰
      $4  #81  ~13 band           33.33°C 🥵  942‰
      $5  #57  ~20 performing     32.98°C 🥵  938‰
      $6   #6  ~29 lullaby        28.68°C 😎  855‰
      $7  #36  ~23 crooning       28.58°C 😎  852‰
      $8 #103   ~5 musical        28.08°C 😎  834‰
      $9  #90   ~9 artist         27.65°C 😎  821‰
     $10  #83  ~11 concert        26.84°C 😎  792‰
     $11 #106   ~3 performer      25.57°C 😎  731‰
     $12  #22  ~26 melody         25.46°C 😎  723‰
     $30 #101      live           19.11°C 🥶
    $101  #46      alluring       -0.01°C 🧊

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1423 🥳 192 ⏱️ 0:03:52.403523

🤔 193 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 48 chat prompts
🤖 48 dolphin3:latest replies
🥵   7 😎  43 🥶 105 🧊  37

      $1 #193   ~1 impératif         100.00°C 🥳 1000‰
      $2 #139  ~19 logique            48.64°C 🥵  982‰
      $3 #166   ~9 systématiquement   43.34°C 🥵  946‰
      $4 #117  ~21 cohérence          42.37°C 🥵  938‰
      $5 #157  ~11 normatif           41.19°C 🥵  929‰
      $6  #96  ~32 adéquation         40.25°C 🥵  923‰
      $7 #141  ~18 rationnel          40.23°C 🥵  922‰
      $8 #111  ~23 équité             40.08°C 🥵  919‰
      $9  #37  ~51 équilibre          38.79°C 😎  890‰
     $10 #125  ~20 cohérent           38.68°C 😎  887‰
     $11 #145  ~17 systématique       38.55°C 😎  883‰
     $12  #84  ~37 rationalisation    37.91°C 😎  866‰
     $52 #171      méthodique         25.84°C 🥶
    $157 #169      automatisé         -0.19°C 🧊
