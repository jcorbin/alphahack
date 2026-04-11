# 2026-04-12

- 🔗 spaceword.org 🧩 2026-04-11 🏁 score 2173 ranked 6.1% 19/311 ⏱️ 0:49:04.376558
- 🔗 alfagok.diginaut.net 🧩 2026-04-12 😦 38 ⏱️ 0:00:46.840274
- 🔗 alphaguess.com 🧩 #993 🥳 20 ⏱️ 0:00:21.735168
- 🔗 dontwordle.com 🧩 #1419 🥳 6 ⏱️ 0:01:11.264327
- 🔗 dictionary.com hurdle 🧩 #1562 😦 18 ⏱️ 0:03:04.328598
- 🔗 Quordle Classic 🧩 #1539 🥳 score:24 ⏱️ 0:01:28.056764
- 🔗 Octordle Classic 🧩 #1539 🥳 score:62 ⏱️ 0:03:32.601282
- 🔗 squareword.org 🧩 #1532 🥳 8 ⏱️ 0:01:53.864769
- 🔗 cemantle.certitudes.org 🧩 #1469 🥳 246 ⏱️ 0:10:35.811203
- 🔗 cemantix.certitudes.org 🧩 #1502 🥳 50 ⏱️ 0:00:35.803046

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










































# [spaceword.org](spaceword.org) 🧩 2026-04-11 🏁 score 2173 ranked 6.1% 19/311 ⏱️ 0:49:04.376558

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 19/311

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ R E P _ _ _   
      _ _ _ _ _ _ A _ _ _   
      _ _ _ _ J O T _ _ _   
      _ _ _ _ _ X I _ _ _   
      _ _ _ _ G I N _ _ _   
      _ _ _ _ O D E _ _ _   
      _ _ _ _ A I _ _ _ _   
      _ _ _ _ _ S _ _ _ _   
      _ _ _ _ F E Z _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 2026-04-12 😦 38 ⏱️ 0:00:46.840274

🤔 38 attempts
📜 1 sessions

    @        [     0] &-teken              
    @+199606 [199606] lij                  q0  ? ␅
    @+199606 [199606] lij                  q1  ? after
    @+247688 [247688] op                   q4  ? ␅
    @+247688 [247688] op                   q5  ? after
    @+260573 [260573] pater                q8  ? ␅
    @+260573 [260573] pater                q9  ? after
    @+260658 [260658] patiënten            q22 ? ␅
    @+260658 [260658] patiënten            q23 ? after
    @+260704 [260704] patiëntie            q24 ? ␅
    @+260704 [260704] patiëntie            q25 ? after
    @+260714 [260714] patiëntveiligheid    q28 ? ␅
    @+260714 [260714] patiëntveiligheid    q29 ? after
    @+260716 [260716] patiëntvriendelijker q36 ? ␅
    @+260716 [260716] patiëntvriendelijker q37 ? after
    @+260716 [260716] patiëntvriendelijker <<< SEARCH
    @+260717 [260717] patjakker            q34 ? ␅
    @+260717 [260717] patjakker            q35 ? before
    @+260717 [260717] patjakker            >>> SEARCH
    @+260719 [260719] patjepeeër           q32 ? ␅
    @+260719 [260719] patjepeeër           q33 ? before
    @+260723 [260723] patriarch            q26 ? ␅
    @+260723 [260723] patriarch            q27 ? before
    @+260750 [260750] patrijs              q20 ? ␅
    @+260750 [260750] patrijs              q21 ? before
    @+260936 [260936] paus                 q18 ? ␅
    @+260936 [260936] paus                 q19 ? before
    @+261319 [261319] peil                 q16 ? ␅
    @+261319 [261319] peil                 q17 ? before
    @+262097 [262097] pepermunt            q14 ? ␅
    @+262097 [262097] pepermunt            q15 ? before

# [alphaguess.com](alphaguess.com) 🧩 #993 🥳 20 ⏱️ 0:00:21.735168

🤔 20 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+23681 [23681] camp       q4  ? ␅
    @+23681 [23681] camp       q5  ? after
    @+24227 [24227] cap        q14 ? ␅
    @+24227 [24227] cap        q15 ? after
    @+24662 [24662] carbon     q16 ? ␅
    @+24662 [24662] carbon     q17 ? after
    @+24862 [24862] care       q18 ? ␅
    @+24862 [24862] care       q19 ? it
    @+24862 [24862] care       done. it
    @+25103 [25103] carp       q12 ? ␅
    @+25103 [25103] carp       q13 ? before
    @+26634 [26634] cep        q10 ? ␅
    @+26634 [26634] cep        q11 ? before
    @+29602 [29602] circuit    q8  ? ␅
    @+29602 [29602] circuit    q9  ? before
    @+35524 [35524] convention q6  ? ␅
    @+35524 [35524] convention q7  ? before
    @+47380 [47380] dis        q2  ? ␅
    @+47380 [47380] dis        q3  ? before
    @+98216 [98216] mach       q0  ? ␅
    @+98216 [98216] mach       q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1419 🥳 6 ⏱️ 0:01:11.264327

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:BOBOS n n n n n remain:4159
    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:2141
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:1056
    ⬜⬜⬜⬜⬜ tried:FUZZY n n n n n remain:427
    ⬜⬜⬜⬜🟩 tried:GRRRL n n n n Y remain:27
    ⬜⬜⬜🟩🟩 tried:ANNAL n n n Y Y remain:3

    Undos used: 2

      3 words remaining
    x 8 unused letters
    = 24 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1562 😦 18 ⏱️ 0:03:04.328598

📜 1 sessions
💰 score: 4860

    4/6
    RAPES ⬜⬜⬜🟩⬜
    OILED ⬜⬜⬜🟩⬜
    UNMET 🟨🟨⬜🟩⬜
    QUEEN 🟩🟩🟩🟩🟩
    4/6
    QUEEN ⬜⬜⬜⬜⬜
    STOAI ⬜⬜⬜🟨⬜
    GLARY ⬜🟨🟩🟨⬜
    BRAWL 🟩🟩🟩🟩🟩
    4/6
    BRAWL ⬜⬜⬜⬜⬜
    SNOUT 🟨🟨🟩⬜⬜
    ICONS ⬜⬜🟩🟨🟨
    NOOSE 🟩🟩🟩🟩🟩
    4/6
    NOOSE ⬜⬜⬜⬜⬜
    RUMLY 🟨🟩⬜⬜⬜
    QUIRK 🟩🟩⬜🟩🟩
    QUARK 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜🟨🟩🟩⬜
    ????? 🟩⬜🟩🟩⬜

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1539 🥳 score:24 ⏱️ 0:01:28.056764

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. STALK attempts:6 score:6
2. OFTEN attempts:3 score:3
3. CLOCK attempts:7 score:7
4. AWAKE attempts:8 score:8

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1539 🥳 score:62 ⏱️ 0:03:32.601282

📜 1 sessions

Octordle Classic

1. PASTA attempts:11 score:11
2. CAPER attempts:12 score:12
3. PURGE attempts:6 score:6
4. UNIFY attempts:8 score:8
5. FELON attempts:9 score:9
6. SWARM attempts:4 score:4
7. GAUDY attempts:5 score:5
8. EERIE attempts:7 score:7

# [squareword.org](squareword.org) 🧩 #1532 🥳 8 ⏱️ 0:01:53.864769

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟨 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C O U T
    H A R S H
    O L D I E
    E V E N S
    S E R G E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1469 🥳 246 ⏱️ 0:10:35.811203

🤔 247 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 48 chat prompts
🤖 31 gemma3:27b replies
🤖 17 dolphin3:latest replies
😱   1 🥵   2 😎  17 🥶 206 🧊  20

      $1 #247 pentagon          100.00°C 🥳 1000‰ ~227 used:0  [226]  source:gemma3  
      $2 #245 hexagon            39.60°C 😱  999‰   ~1 used:0  [0]    source:gemma3  
      $3 #238 triangle           32.32°C 🥵  956‰   ~3 used:2  [2]    source:gemma3  
      $4 #235 polygon            31.72°C 🥵  944‰   ~2 used:0  [1]    source:gemma3  
      $5 #226 geodesic           29.49°C 😎  886‰   ~4 used:1  [3]    source:gemma3  
      $6 #242 hypotenuse         29.19°C 😎  858‰   ~5 used:0  [4]    source:gemma3  
      $7 #223 toroidal           28.29°C 😎  800‰   ~6 used:0  [5]    source:gemma3  
      $8  #77 constellation      27.86°C 😎  762‰  ~20 used:23 [19]   source:gemma3  
      $9  #71 galaxy             27.55°C 😎  733‰  ~18 used:18 [17]   source:gemma3  
     $10 #157 galactic           27.24°C 😎  698‰  ~16 used:6  [15]   source:gemma3  
     $11 #173 chromosphere       26.60°C 😎  632‰  ~13 used:4  [12]   source:gemma3  
     $12  #73 nebula             26.28°C 😎  574‰  ~17 used:6  [16]   source:gemma3  
     $22   #1 chandelier         23.27°C 🥶        ~21 used:13 [20]   source:dolphin3
    $228  #32 heat               -0.10°C 🧊       ~228 used:0  [227]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1502 🥳 50 ⏱️ 0:00:35.803046

🤔 51 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 8 chat prompts
🤖 8 dolphin3:latest replies
😱  1 🔥  1 🥵  5 😎 16 🥶 20 🧊  7

     $1 #51 logiciel        100.00°C 🥳 1000‰ ~44 used:0 [43]  source:dolphin3
     $2 #48 informatique     63.26°C 😱  999‰  ~1 used:0 [0]   source:dolphin3
     $3 #50 interface        56.28°C 🔥  992‰  ~2 used:0 [1]   source:dolphin3
     $4 #14 fichier          51.72°C 🥵  979‰  ~7 used:7 [6]   source:dolphin3
     $5 #38 application      48.49°C 🥵  963‰  ~3 used:0 [2]   source:dolphin3
     $6 #36 système          46.79°C 🥵  958‰  ~6 used:3 [5]   source:dolphin3
     $7 #42 configuration    43.24°C 🥵  919‰  ~4 used:0 [3]   source:dolphin3
     $8 #31 gestion          42.05°C 🥵  904‰  ~5 used:1 [4]   source:dolphin3
     $9 #25 base             41.58°C 😎  898‰ ~23 used:2 [22]  source:dolphin3
    $10 #43 contenu          41.17°C 😎  894‰  ~8 used:0 [7]   source:dolphin3
    $11 #40 automatisation   41.12°C 😎  893‰  ~9 used:0 [8]   source:dolphin3
    $12 #46 exploitation     39.46°C 😎  861‰ ~10 used:0 [9]   source:dolphin3
    $25 #41 communication    25.05°C 🥶       ~24 used:0 [23]  source:dolphin3
    $45  #5 poisson          -1.02°C 🧊       ~45 used:0 [44]  source:dolphin3
