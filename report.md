# 2026-06-28

- 🔗 spaceword.org 🧩 2026-06-27 🏁 score 2168 ranked 36.1% 105/291 ⏱️ 3:04:59.318504
- 🔗 alfagok.diginaut.net 🧩 #603 🥳 26 ⏱️ 0:00:52.453932
- 🔗 alphaguess.com 🧩 #1070 🥳 26 ⏱️ 0:00:35.976588
- 🔗 dontwordle.com 🧩 #1496 🥳 6 ⏱️ 0:01:30.977095
- 🔗 dictionary.com hurdle 🧩 #1639 🥳 16 ⏱️ 0:03:43.921396
- 🔗 Quordle Classic 🧩 #1616 🥳 score:25 ⏱️ 0:01:49.044951
- 🔗 Octordle Classic 🧩 #1616 😦 score:66 ⏱️ 0:04:51.542414
- 🔗 Sedecordle Classic 🧩 #1596 🥳 score:44 ⏱️ 0:13:28.851976
- 🔗 squareword.org 🧩 #1609 🥳 7 ⏱️ 0:01:48.009148
- 🔗 cemantle.certitudes.org 🧩 #1546 🥳 210 ⏱️ 0:02:47.729961
- 🔗 cemantix.certitudes.org 🧩 #1579 🥳 168 ⏱️ 0:03:08.309298

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



















# [spaceword.org](spaceword.org) 🧩 2026-06-27 🏁 score 2168 ranked 36.1% 105/291 ⏱️ 3:04:59.318504

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 105/291

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ I _ _ G _ A _ J _   
      _ L _ G R E I G E _   
      _ K _ _ U _ D _ U _   
      _ S O L E I _ _ X _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #603 🥳 26 ⏱️ 0:00:52.453932

🤔 26 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+1      [     1] &-tekens     
    @+2      [     2] -cijferig    
    @+3      [     3] -e-mail      
    @+199557 [199557] lij          q0  ? ␅
    @+199557 [199557] lij          q1  ? after
    @+223553 [223553] molen        q6  ? ␅
    @+223553 [223553] molen        q7  ? after
    @+235566 [235566] octrooi      q8  ? ␅
    @+235566 [235566] octrooi      q9  ? after
    @+238680 [238680] on           q10 ? ␅
    @+238680 [238680] on           q11 ? after
    @+243150 [243150] onroerend    q12 ? ␅
    @+243150 [243150] onroerend    q13 ? after
    @+245367 [245367] ontwikkeling q14 ? ␅
    @+245367 [245367] ontwikkeling q15 ? after
    @+246495 [246495] onzichtbaar  q16 ? ␅
    @+246495 [246495] onzichtbaar  q17 ? after
    @+246916 [246916] oorlog       q18 ? ␅
    @+246916 [246916] oorlog       q19 ? after
    @+247267 [247267] oorverdovend q20 ? ␅
    @+247267 [247267] oorverdovend q21 ? after
    @+247282 [247282] oorzaak      q24 ? ␅
    @+247282 [247282] oorzaak      q25 ? it
    @+247282 [247282] oorzaak      done. it
    @+247297 [247297] oost         q22 ? ␅
    @+247297 [247297] oost         q23 ? before
    @+247622 [247622] op           q4  ? ␅
    @+247622 [247622] op           q5  ? before
    @+299534 [299534] schrok       q2  ? ␅
    @+299534 [299534] schrok       q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1070 🥳 26 ⏱️ 0:00:35.976588

🤔 26 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+47380 [47380] dis       q2  ? ␅
    @+47380 [47380] dis       q3  ? after
    @+60081 [60081] face      q6  ? ␅
    @+60081 [60081] face      q7  ? after
    @+60228 [60228] fad       q18 ? ␅
    @+60228 [60228] fad       q19 ? after
    @+60319 [60319] faint     q20 ? ␅
    @+60319 [60319] faint     q21 ? after
    @+60334 [60334] fair      q24 ? ␅
    @+60334 [60334] fair      q25 ? it
    @+60334 [60334] fair      done. it
    @+60367 [60367] faith     q22 ? ␅
    @+60367 [60367] faith     q23 ? before
    @+60426 [60426] fall      q16 ? ␅
    @+60426 [60426] fall      q17 ? before
    @+60848 [60848] fas       q14 ? ␅
    @+60848 [60848] fas       q15 ? before
    @+61617 [61617] fen       q12 ? ␅
    @+61617 [61617] fen       q13 ? before
    @+63237 [63237] flag      q10 ? ␅
    @+63237 [63237] flag      q11 ? before
    @+66437 [66437] french    q8  ? ␅
    @+66437 [66437] french    q9  ? before
    @+72797 [72797] gremolata q4  ? ␅
    @+72797 [72797] gremolata q5  ? before
    @+98214 [98214] mach      q0  ? ␅
    @+98214 [98214] mach      q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1496 🥳 6 ⏱️ 0:01:30.977095

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:EGGED n n n n n remain:5334
    ⬜⬜⬜⬜⬜ tried:YOBBO n n n n n remain:2317
    ⬜⬜⬜⬜⬜ tried:PIKIS n n n n n remain:270
    ⬜⬜⬜⬜⬜ tried:CHUFF n n n n n remain:71
    ⬜🟨⬜⬜🟨 tried:TAZZA n m n n m remain:8
    🟩⬜🟨🟨⬜ tried:AXMAN Y n m m n remain:1

    Undos used: 2

      1 words remaining
    x 6 unused letters
    = 6 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1639 🥳 16 ⏱️ 0:03:43.921396

📜 1 sessions
💰 score: 10000

    3/6
    HEADS 🟨🟨⬜⬜⬜
    WHITE ⬜🟩⬜🟩🟩
    CHUTE 🟩🟩🟩🟩🟩
    2/6
    CHUTE 🟩🟩⬜🟨⬜
    CHANT 🟩🟩🟩🟩🟩
    4/6
    CHANT ⬜⬜⬜🟩⬜
    LIENS ⬜🟨⬜🟩⬜
    GRIND 🟨⬜🟩🟩🟨
    DOING 🟩🟩🟩🟩🟩
    5/6
    DOING ⬜⬜⬜⬜⬜
    HATER ⬜🟩⬜⬜🟨
    LARKS 🟨🟩🟨⬜⬜
    RAWLY 🟩🟩⬜🟩🟩
    RALLY 🟩🟩🟩🟩🟩
    Final 2/2
    MENUS ⬜🟩🟨🟩🟩
    NEXUS 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1616 🥳 score:25 ⏱️ 0:01:49.044951

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. RUPEE attempts:4 score:4
2. TOPAZ attempts:5 score:5
3. FULLY attempts:7 score:7
4. BEING attempts:9 score:9

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1616 😦 score:66 ⏱️ 0:04:51.542414

📜 1 sessions

Octordle Classic

1. FUROR attempts:9 score:9
2. GUSTY attempts:12 score:12
3. SCION attempts:5 score:5
4. CURVY attempts:3 score:3
5. HEIGH attempts:10 score:10
6. BROO_ -ACDEFGHIJLMNPSTUVYZ attempts:13 score:-1
7. SYNOD attempts:6 score:6
8. OZONE attempts:7 score:7

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1596 🥳 score:44 ⏱️ 0:13:28.851976

📜 1 sessions

Sedecordle Classic sedecordle.com

1. GAVEL attempts:18 score:1
2. GLOBE attempts:19 score:8
3. FRESH attempts:7 score:0
4. STRIP attempts:4 score:7
5. MEDIA attempts:15 score:1
6. GRIEF attempts:17 score:5
7. MACAW attempts:14 score:1
8. FLOCK attempts:13 score:4
9. SAINT attempts:5 score:0
10. EXPEL attempts:3 score:5
11. AWOKE attempts:10 score:1
12. PARSE attempts:6 score:0
13. ALLOW attempts:11 score:1
14. FETID attempts:12 score:1
15. SHANK attempts:9 score:0
16. ASSAY attempts:8 score:9

# [squareword.org](squareword.org) 🧩 #1609 🥳 7 ⏱️ 0:01:48.009148

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    T O P A Z
    A P A C E
    L I S T S
    O N S E T
    N E E D Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1546 🥳 210 ⏱️ 0:02:47.729961

🤔 211 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 55 chat prompts
🤖 55 dolphin3:latest replies
🔥   1 🥵   7 😎  37 🥶 160 🧊   5

      $1 #211 ideology         100.00°C 🥳 1000‰ ~206 used:0  [205]  source:dolphin3
      $2 #116 philosophy        58.89°C 🔥  991‰   ~2 used:33 [1]    source:dolphin3
      $3 #161 idealism          56.16°C 🥵  980‰  ~34 used:11 [33]   source:dolphin3
      $4 #194 pragmatism        55.25°C 🥵  975‰   ~3 used:4  [2]    source:dolphin3
      $5 #202 subjectivism      54.14°C 🥵  964‰   ~4 used:4  [3]    source:dolphin3
      $6 #190 humanism          52.53°C 🥵  956‰   ~1 used:2  [0]    source:dolphin3
      $7 #154 rationalism       51.89°C 🥵  947‰   ~5 used:7  [4]    source:dolphin3
      $8 #109 empiricism        49.75°C 🥵  914‰  ~35 used:12 [34]   source:dolphin3
      $9  #76 rationality       49.41°C 🥵  910‰  ~36 used:15 [35]   source:dolphin3
     $10 #192 materialism       48.82°C 😎  899‰   ~6 used:0  [5]    source:dolphin3
     $11 #197 libertarianism    48.54°C 😎  886‰   ~7 used:0  [6]    source:dolphin3
     $12 #186 monism            47.80°C 😎  865‰   ~8 used:0  [7]    source:dolphin3
     $47 #160 values            35.05°C 🥶        ~54 used:0  [53]   source:dolphin3
    $207  #11 keyboard          -0.20°C 🧊       ~207 used:0  [206]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1579 🥳 168 ⏱️ 0:03:08.309298

🤔 169 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 47 chat prompts
🤖 47 dolphin3:latest replies
😱   1 🥵  10 😎  34 🥶 101 🧊  22

      $1 #169 aviation         100.00°C 🥳 1000‰ ~147 used:0  [146]  source:dolphin3
      $2 #141 aviateur          61.77°C 😱  999‰   ~1 used:7  [0]    source:dolphin3
      $3  #87 avion             53.50°C 🥵  987‰  ~36 used:25 [35]   source:dolphin3
      $4 #143 dirigeable        51.75°C 🥵  984‰   ~2 used:1  [1]    source:dolphin3
      $5 #129 planeur           50.87°C 🥵  981‰   ~9 used:7  [8]    source:dolphin3
      $6 #139 aérostat          48.51°C 🥵  977‰   ~3 used:1  [2]    source:dolphin3
      $7 #156 pilote            46.69°C 🥵  972‰   ~4 used:0  [3]    source:dolphin3
      $8 #140 astronautique     46.40°C 🥵  971‰   ~5 used:0  [4]    source:dolphin3
      $9 #128 parachutiste      40.09°C 🥵  951‰   ~8 used:3  [7]    source:dolphin3
     $10  #95 hélicoptère       39.90°C 🥵  949‰  ~29 used:12 [28]   source:dolphin3
     $11 #145 commandant        36.07°C 🥵  924‰   ~6 used:0  [5]    source:dolphin3
     $13 #150 instructeur       33.56°C 😎  893‰  ~10 used:0  [9]    source:dolphin3
     $47  #56 vapeur            16.42°C 🥶        ~48 used:0  [47]   source:dolphin3
    $148 #148 formation         -0.02°C 🧊       ~148 used:0  [147]  source:dolphin3
