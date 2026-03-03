# 2026-03-04

- 🔗 spaceword.org 🧩 2026-03-03 🏁 score 2168 ranked 40.5% 135/333 ⏱️ 5:31:51.567228
- 🔗 alfagok.diginaut.net 🧩 #487 🥳 26 ⏱️ 0:00:28.094912
- 🔗 alphaguess.com 🧩 #954 🥳 26 ⏱️ 0:00:27.567792
- 🔗 dontwordle.com 🧩 #1380 🥳 6 ⏱️ 0:01:37.479491
- 🔗 dictionary.com hurdle 🧩 #1523 🥳 18 ⏱️ 0:03:01.697674
- 🔗 Quordle Classic 🧩 #1500 🥳 score:29 ⏱️ 0:01:45.448651
- 🔗 Octordle Classic 🧩 #1500 🥳 score:64 ⏱️ 0:03:48.045061
- 🔗 squareword.org 🧩 #1493 🥳 7 ⏱️ 0:02:11.568145
- 🔗 cemantle.certitudes.org 🧩 #1430 🥳 149 ⏱️ 0:01:34.720490
- 🔗 cemantix.certitudes.org 🧩 #1463 🥳 182 ⏱️ 0:17:20.473324

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



# [spaceword.org](spaceword.org) 🧩 2026-03-03 🏁 score 2168 ranked 40.5% 135/333 ⏱️ 5:31:51.567228

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 135/333

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ C _ A _ I _ _ S _   
      _ U _ V I R T U E _   
      _ P R O T E A _ M _   
      _ _ _ W _ _ J _ I _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #487 🥳 26 ⏱️ 0:00:28.094912

🤔 26 attempts
📜 1 sessions

    @        [     0] &-teken       
    @+1      [     1] &-tekens      
    @+2      [     2] -cijferig     
    @+3      [     3] -e-mail       
    @+199812 [199812] lijm          q0  ? ␅
    @+199812 [199812] lijm          q1  ? after
    @+299705 [299705] schub         q2  ? ␅
    @+299705 [299705] schub         q3  ? after
    @+349473 [349473] vakantie      q4  ? ␅
    @+349473 [349473] vakantie      q5  ? after
    @+353041 [353041] ver           q8  ? ␅
    @+353041 [353041] ver           q9  ? after
    @+363624 [363624] verzot        q10 ? ␅
    @+363624 [363624] verzot        q11 ? after
    @+368636 [368636] voetbal       q12 ? ␅
    @+368636 [368636] voetbal       q13 ? after
    @+370485 [370485] voor          q14 ? ␅
    @+370485 [370485] voor          q15 ? after
    @+371409 [371409] voorleg       q18 ? ␅
    @+371409 [371409] voorleg       q19 ? after
    @+371868 [371868] voorschakel   q20 ? ␅
    @+371868 [371868] voorschakel   q21 ? after
    @+372021 [372021] voorst        q22 ? ␅
    @+372021 [372021] voorst        q23 ? after
    @+372106 [372106] voort         q24 ? ␅
    @+372106 [372106] voort         q25 ? it
    @+372106 [372106] voort         done. it
    @+372337 [372337] voortplanting q16 ? ␅
    @+372337 [372337] voortplanting q17 ? before
    @+374214 [374214] vrij          q6  ? ␅
    @+374214 [374214] vrij          q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #954 🥳 26 ⏱️ 0:00:27.567792

🤔 26 attempts
📜 1 sessions

    @       [    0] aa           
    @+1     [    1] aah          
    @+2     [    2] aahed        
    @+3     [    3] aahing       
    @+47381 [47381] dis          q2  ? ␅
    @+47381 [47381] dis          q3  ? after
    @+60084 [60084] face         q6  ? ␅
    @+60084 [60084] face         q7  ? after
    @+66440 [66440] french       q8  ? ␅
    @+66440 [66440] french       q9  ? after
    @+69620 [69620] geosynclinal q10 ? ␅
    @+69620 [69620] geosynclinal q11 ? after
    @+69925 [69925] gi           q16 ? ␅
    @+69925 [69925] gi           q17 ? after
    @+70018 [70018] gig          q20 ? ␅
    @+70018 [70018] gig          q21 ? after
    @+70043 [70043] giggle       q24 ? ␅
    @+70043 [70043] giggle       q25 ? it
    @+70043 [70043] giggle       done. it
    @+70078 [70078] gill         q22 ? ␅
    @+70078 [70078] gill         q23 ? before
    @+70157 [70157] ginger       q18 ? ␅
    @+70157 [70157] ginger       q19 ? before
    @+70412 [70412] glam         q14 ? ␅
    @+70412 [70412] glam         q15 ? before
    @+71210 [71210] gnomist      q12 ? ␅
    @+71210 [71210] gnomist      q13 ? before
    @+72800 [72800] gremmy       q4  ? ␅
    @+72800 [72800] gremmy       q5  ? before
    @+98218 [98218] mach         q0  ? ␅
    @+98218 [98218] mach         q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1380 🥳 6 ⏱️ 0:01:37.479491

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MOTTO n n n n n remain:5765
    ⬜⬜⬜⬜⬜ tried:SHUSH n n n n n remain:2011
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:729
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:146
    ⬜🟨⬜⬜⬜ tried:BEEFY n m n n n remain:17
    🟨🟨⬜⬜🟨 tried:AWAKE m m n n m remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1523 🥳 18 ⏱️ 0:03:01.697674

📜 1 sessions
💰 score: 9800

    5/6
    SENOR 🟩🟨⬜⬜⬜
    SLEPT 🟩⬜🟨⬜🟨
    SUITE 🟩⬜⬜🟩🟩
    SKATE 🟩⬜🟩🟩🟩
    STATE 🟩🟩🟩🟩🟩
    4/6
    STATE ⬜⬜⬜⬜⬜
    RINDY ⬜⬜⬜⬜🟩
    LUCKY 🟨⬜🟨⬜🟩
    COYLY 🟩🟩🟩🟩🟩
    4/6
    COYLY ⬜⬜⬜⬜🟩
    UNARY 🟨🟨⬜⬜🟩
    PUNKY ⬜🟩🟩🟩🟩
    FUNKY 🟩🟩🟩🟩🟩
    4/6
    FUNKY ⬜🟩⬜⬜🟩
    RUSTY 🟨🟩⬜⬜🟩
    CURLY ⬜🟩🟩⬜🟩
    HURRY 🟩🟩🟩🟩🟩
    Final 1/2
    FIRST 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1500 🥳 score:29 ⏱️ 0:01:45.448651

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. ENVOY attempts:7 score:7
2. UPPER attempts:5 score:5
3. DERBY attempts:9 score:9
4. LLAMA attempts:8 score:8

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1500 🥳 score:64 ⏱️ 0:03:48.045061

📜 3 sessions

Octordle Classic

1. COURT attempts:5 score:5
2. GLOOM attempts:10 score:10
3. CRISP attempts:6 score:6
4. ELEGY attempts:11 score:11
5. AGENT attempts:3 score:3
6. NOTCH attempts:8 score:8
7. TAFFY attempts:12 score:12
8. BIGOT attempts:9 score:9

# [squareword.org](squareword.org) 🧩 #1493 🥳 7 ⏱️ 0:02:11.568145

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S A L A D
    P R I S E
    R E M I T
    A N O D E
    T A S E R

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1430 🥳 149 ⏱️ 0:01:34.720490

🤔 150 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 21 chat prompts
🤖 21 dolphin3:latest replies
🔥   3 🥵  12 😎  32 🥶 100 🧊   2

      $1 #150 flexible         100.00°C 🥳 1000‰ ~148 used:0  [147]  source:dolphin3
      $2 #117 flexibility       62.69°C 🔥  998‰   ~3 used:8  [2]    source:dolphin3
      $3 #126 adaptable         62.42°C 🔥  997‰   ~2 used:4  [1]    source:dolphin3
      $4 #132 responsive        50.56°C 🔥  992‰   ~1 used:3  [0]    source:dolphin3
      $5  #73 agile             47.79°C 🥵  987‰  ~15 used:6  [14]   source:dolphin3
      $6 #103 innovative        47.52°C 🥵  986‰  ~14 used:2  [13]   source:dolphin3
      $7 #145 versatile         46.44°C 🥵  985‰   ~4 used:0  [3]    source:dolphin3
      $8 #129 elastic           45.24°C 🥵  983‰   ~5 used:0  [4]    source:dolphin3
      $9 #136 dynamic           44.45°C 🥵  981‰   ~6 used:0  [5]    source:dolphin3
     $10 #148 changeable        42.51°C 🥵  969‰   ~7 used:0  [6]    source:dolphin3
     $11 #142 nimble            42.43°C 🥵  968‰   ~8 used:0  [7]    source:dolphin3
     $17 #149 compliant         35.58°C 😎  889‰  ~16 used:0  [15]   source:dolphin3
     $49  #27 autonomous        24.32°C 🥶        ~48 used:0  [47]   source:dolphin3
    $149 #102 gathering         -0.11°C 🧊       ~149 used:0  [148]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1463 🥳 182 ⏱️ 0:17:20.473324

🤔 183 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 34 chat prompts
🤖 34 dolphin3:latest replies
🥵   7 😎  11 🥶 120 🧊  44

      $1 #183 faille             100.00°C 🥳 1000‰ ~139 used:0  [138]  source:dolphin3
      $2 #174 lacune              35.13°C 🥵  983‰   ~1 used:1  [0]    source:dolphin3
      $3 #141 faiblesse           34.69°C 🥵  979‰   ~5 used:8  [4]    source:dolphin3
      $4 #115 bogue               33.38°C 🥵  970‰  ~15 used:16 [14]   source:dolphin3
      $5 #182 brèche              32.59°C 🥵  960‰   ~2 used:0  [1]    source:dolphin3
      $6 #119 défaut              31.26°C 🥵  936‰   ~6 used:10 [5]    source:dolphin3
      $7 #135 imperfection        30.32°C 🥵  917‰   ~4 used:6  [3]    source:dolphin3
      $8 #137 anomalie            29.50°C 🥵  903‰   ~3 used:4  [2]    source:dolphin3
      $9   #2 car                 27.75°C 😎  853‰  ~18 used:21 [17]   source:dolphin3
     $10 #105 dysfonctionnement   26.48°C 😎  791‰  ~16 used:2  [15]   source:dolphin3
     $11 #106 défaillance         26.07°C 😎  758‰   ~7 used:0  [6]    source:dolphin3
     $12 #139 bévue               25.68°C 😎  731‰   ~8 used:0  [7]    source:dolphin3
     $20 #179 avoir               20.01°C 🥶        ~25 used:0  [24]   source:dolphin3
    $140  #62 stationnement       -0.15°C 🧊       ~140 used:0  [139]  source:dolphin3
