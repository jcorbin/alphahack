# 2026-10-21

- 🔗 spaceword.org 🧩 2026-10-20 🏁 score 2170 ranked 27.1% 84/310 ⏱️ 0:07:04.798386
- 🔗 alfagok.diginaut.net 🧩 #718 🥳 24 ⏱️ 0:00:34.295135
- 🔗 alphaguess.com 🧩 #1185 🥳 28 ⏱️ 0:00:34.492479
- 🔗 dontwordle.com 🧩 #1611 🥳 6 ⏱️ 0:01:44.313088
- 🔗 dictionary.com hurdle 🧩 #1754 🥳 19 ⏱️ 0:03:20.641697
- 🔗 Quordle Classic 🧩 #1731 🥳 score:23 ⏱️ 0:01:48.708395
- 🔗 Octordle Classic 🧩 #1731 🥳 score:52 ⏱️ 0:02:39.250969
- 🔗 Sedecordle Classic 🧩 #1711 🥳 score:40 ⏱️ 0:02:57.008839
- 🔗 squareword.org 🧩 #1724 🥳 7 ⏱️ 0:02:04.825683
- 🔗 cemantle.certitudes.org 🧩 #1661 🥳 116 ⏱️ 0:11:26.728803
- 🔗 cemantix.certitudes.org 🧩 #1694 🥳 150 ⏱️ 0:13:43.483142
- 🔗 wordgrid 🧩 #872 🟪 rarity:0.19 ⏱️ 0:02:13.072272

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

















# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #872 🟪 rarity:0.19 ⏱️ 0:02:13.072272

📜 3 sessions
🦄 🦄 🌌
🦄 🦄 🌌
🦄 🌌 🦄
Rarity: 0.19 🟪

# [spaceword.org](spaceword.org) 🧩 2026-10-20 🏁 score 2170 ranked 27.1% 84/310 ⏱️ 0:07:04.798386

📜 2 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 84/310

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ D I E S _ _ _   
      _ _ O A T _ _ _ _ _   
      _ _ _ V _ K A Y _ _   
      _ _ B I Z O N E _ _   
      _ _ I T _ A Y _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #718 🥳 24 ⏱️ 0:00:34.295135

🤔 24 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199631 [199631] lijk      q0  ? ␅
    @+199631 [199631] lijk      q1  ? after
    @+199631 [199631] lijk      q2  ? ␅
    @+199631 [199631] lijk      q3  ? after
    @+199631 [199631] lijk      q4  ? ␅
    @+199631 [199631] lijk      q5  ? after
    @+199631 [199631] lijk      q6  ? ␅
    @+199631 [199631] lijk      q7  ? after
    @+299529 [299529] schroot   q8  ? ␅
    @+299529 [299529] schroot   q9  ? after
    @+324111 [324111] sub       q12 ? ␅
    @+324111 [324111] sub       q13 ? after
    @+330294 [330294] televisie q16 ? ␅
    @+330294 [330294] televisie q17 ? after
    @+333500 [333500] thesis    q18 ? ␅
    @+333500 [333500] thesis    q19 ? after
    @+333628 [333628] thuis     q22 ? ␅
    @+333628 [333628] thuis     q23 ? it
    @+333628 [333628] thuis     done. it
    @+333906 [333906] ti        q20 ? ␅
    @+333906 [333906] ti        q21 ? before
    @+336704 [336704] toetsing  q14 ? ␅
    @+336704 [336704] toetsing  q15 ? before
    @+349311 [349311] vakantie  q10 ? ␅
    @+349311 [349311] vakantie  q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1185 🥳 28 ⏱️ 0:00:34.492479

🤔 28 attempts
📜 1 sessions

    @       [    0] aa         
    @+2     [    2] aahed      
    @+47374 [47374] dis        q2  ? ␅
    @+47374 [47374] dis        q3  ? after
    @+49421 [49421] do         q10 ? ␅
    @+49421 [49421] do         q11 ? after
    @+51395 [51395] drunk      q12 ? ␅
    @+51395 [51395] drunk      q13 ? after
    @+52388 [52388] earth      q14 ? ␅
    @+52388 [52388] earth      q15 ? after
    @+52446 [52446] earwig     q22 ? ␅
    @+52446 [52446] earwig     q23 ? after
    @+52454 [52454] ease       q26 ? ␅
    @+52454 [52454] ease       q27 ? it
    @+52454 [52454] ease       done. it
    @+52473 [52473] east       q24 ? ␅
    @+52473 [52473] east       q25 ? before
    @+52507 [52507] eave       q20 ? ␅
    @+52507 [52507] eave       q21 ? before
    @+52626 [52626] echo       q18 ? ␅
    @+52626 [52626] echo       q19 ? before
    @+52868 [52868] ed         q16 ? ␅
    @+52868 [52868] ed         q17 ? before
    @+53390 [53390] el         q8  ? ␅
    @+53390 [53390] el         q9  ? before
    @+60013 [60013] eyewitness q6  ? ␅
    @+60013 [60013] eyewitness q7  ? before
    @+72657 [72657] green      q4  ? ␅
    @+72657 [72657] green      q5  ? before
    @+98142 [98142] mac        q0  ? ␅
    @+98142 [98142] mac        q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1611 🥳 6 ⏱️ 0:01:44.313088

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:GAMMA n n n n n remain:5731
    ⬜⬜⬜⬜⬜ tried:INION n n n n n remain:1509
    ⬜⬜⬜⬜⬜ tried:YUKKY n n n n n remain:526
    ⬜⬜⬜🟨⬜ tried:CRWTH n n n m n remain:34
    🟨⬜⬜⬜🟩 tried:EBBET m n n n Y remain:5
    ⬜🟨🟨⬜🟩 tried:DELFT n m m n Y remain:2

    Undos used: 3

      2 words remaining
    x 7 unused letters
    = 14 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1754 🥳 19 ⏱️ 0:03:20.641697

📜 2 sessions
💰 score: 9700

    4/6
    ARISE ⬜⬜⬜🟨⬜
    LUNKS ⬜⬜⬜⬜🟨
    SOFTY 🟩🟩⬜🟩🟩
    SOOTY 🟩🟩🟩🟩🟩
    5/6
    SOOTY ⬜⬜⬜⬜⬜
    LUNAR ⬜⬜⬜⬜🟨
    RIDGE 🟨🟨⬜⬜🟩
    CLIMB ⬜⬜🟩⬜⬜
    PRIZE 🟩🟩🟩🟩🟩
    5/6
    PRIZE ⬜⬜⬜⬜🟨
    LEADS 🟨🟨⬜⬜🟨
    FLESH ⬜🟩🟩🟨⬜
    SLEEK 🟩🟩🟩🟩⬜
    SLEET 🟩🟩🟩🟩🟩
    4/6
    SLEET 🟩🟨🟨⬜🟨
    STYLE 🟩🟩⬜🟩🟩
    STALE 🟩🟩⬜🟩🟩
    STOLE 🟩🟩🟩🟩🟩
    Final 1/2
    NYLON 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1731 🥳 score:23 ⏱️ 0:01:48.708395

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. MOIST attempts:4 score:4
2. VALVE attempts:6 score:6
3. VERSE attempts:5 score:5
4. NORTH attempts:8 score:8

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1731 🥳 score:52 ⏱️ 0:02:39.250969

📜 1 sessions

Octordle Classic

1. TORUS attempts:7 score:7
2. PIVOT attempts:9 score:9
3. ACUTE attempts:6 score:6
4. LADEN attempts:8 score:8
5. BESET attempts:5 score:5
6. HYENA attempts:3 score:3
7. THREW attempts:4 score:4
8. STAFF attempts:10 score:10

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1711 🥳 score:40 ⏱️ 0:02:57.008839

📜 2 sessions

Sedecordle Classic sedecordle.com

1. CRYPT attempts:6 score:0
2. SNIPE attempts:7 score:6
3. BASIC attempts:9 score:0
4. UTILE attempts:3 score:9
5. PUREE attempts:11 score:1
6. FENCE attempts:13 score:1
7. ANVIL attempts:8 score:0
8. CHOCK attempts:15 score:8
9. START attempts:4 score:0
10. CHARM attempts:17 score:4
11. GAMUT attempts:10 score:1
12. MACHO attempts:18 score:0
13. TAKEN attempts:14 score:1
14. PUSHY attempts:16 score:4
15. SPLIT attempts:5 score:0
16. FETAL attempts:12 score:5

# [squareword.org](squareword.org) 🧩 #1724 🥳 7 ⏱️ 0:02:04.825683

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    H A S T E
    O P E R A
    S P R A T
    E L I D E
    D E F E R

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1661 🥳 116 ⏱️ 0:11:26.728803

🤔 117 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 29 chat prompts
🤖 29 dolphin3:latest replies
🔥  3 🥵  9 😎 29 🥶 75

      $1 #117 cart         100.00°C 🥳 1000‰ ~117 used:0  [116]  source:dolphin3
      $2 #110 trolley       57.45°C 🔥  998‰   ~1 used:16 [0]    source:dolphin3
      $3  #22 truck         49.12°C 🔥  996‰   ~9 used:25 [8]    source:dolphin3
      $4  #86 van           49.10°C 🔥  995‰   ~2 used:16 [1]    source:dolphin3
      $5  #84 scooter       43.82°C 🥵  978‰  ~11 used:6  [10]   source:dolphin3
      $6  #87 hauler        41.11°C 🥵  965‰   ~3 used:2  [2]    source:dolphin3
      $7  #17 bus           40.99°C 🥵  963‰  ~12 used:6  [11]   source:dolphin3
      $8  #33 trailer       39.38°C 🥵  952‰  ~10 used:4  [9]    source:dolphin3
      $9  #85 taxi          38.12°C 🥵  943‰   ~4 used:2  [3]    source:dolphin3
     $10  #89 minivan       37.16°C 🥵  929‰   ~5 used:2  [4]    source:dolphin3
     $11  #99 pickup        37.07°C 🥵  928‰   ~6 used:2  [5]    source:dolphin3
     $12  #15 bike          36.90°C 🥵  924‰   ~7 used:2  [6]    source:dolphin3
     $14   #3 car           33.74°C 😎  871‰  ~41 used:2  [40]   source:dolphin3
     $43  #56 gear          23.13°C 🥶        ~42 used:0  [41]   source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1694 🥳 150 ⏱️ 0:13:43.483142

🤔 151 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 32 chat prompts
🤖 12 gemma4:12b replies
🤖 20 dolphin3:latest replies
🥵   4 😎  15 🥶 114 🧊  17

      $1 #151 caméra           100.00°C 🥳 1000‰ ~134 used:0  [133]  source:gemma4  
      $2 #104 micro             39.42°C 🥵  964‰  ~11 used:13 [10]   source:dolphin3
      $3  #46 capteur           36.94°C 🥵  946‰  ~13 used:29 [12]   source:dolphin3
      $4 #149 vidéo             36.64°C 🥵  940‰   ~1 used:2  [0]    source:gemma4  
      $5  #95 microphone        33.56°C 🥵  903‰  ~10 used:11 [9]    source:dolphin3
      $6 #138 enregistreur      33.15°C 😎  897‰   ~2 used:1  [1]    source:gemma4  
      $7 #105 magnétoscope      33.12°C 😎  896‰  ~12 used:2  [11]   source:dolphin3
      $8 #143 magnétophone      32.71°C 😎  884‰   ~3 used:1  [2]    source:gemma4  
      $9  #80 senseur           32.34°C 😎  879‰  ~19 used:7  [18]   source:dolphin3
     $10  #68 détecteur         32.10°C 😎  869‰  ~17 used:5  [16]   source:dolphin3
     $11 #114 oculaire          29.96°C 😎  806‰   ~4 used:0  [3]    source:dolphin3
     $12 #131 microscope        27.92°C 😎  735‰   ~5 used:0  [4]    source:gemma4  
     $21 #142 magnéto           21.26°C 🥶        ~25 used:0  [24]   source:gemma4  
    $135  #15 huile             -0.24°C 🧊       ~135 used:0  [134]  source:dolphin3
