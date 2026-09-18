# 2026-09-19

- 🔗 spaceword.org 🧩 2026-09-18 🏁 score 2168 ranked 42.1% 153/363 ⏱️ 1:31:59.587107
- 🔗 wordgrid 🧩 #840 🟪 rarity:0.11 ⏱️ 0:01:53.302700
- 🔗 alfagok.diginaut.net 🧩 #686 🥳 42 ⏱️ 0:00:51.546115
- 🔗 alphaguess.com 🧩 #1153 🥳 32 ⏱️ 0:00:36.337860
- 🔗 dontwordle.com 🧩 #1579 🥳 6 ⏱️ 0:01:42.058891
- 🔗 dictionary.com hurdle 🧩 #1722 😦 16 ⏱️ 0:02:23.569215
- 🔗 Quordle Classic 🧩 #1699 🥳 score:22 ⏱️ 0:01:25.567687
- 🔗 Octordle Classic 🧩 #1699 🥳 score:61 ⏱️ 0:02:20.744531
- 🔗 Sedecordle Classic 🧩 #1679 🥳 score:50 ⏱️ 0:03:01.835653
- 🔗 squareword.org 🧩 #1692 🥳 7 ⏱️ 0:02:00.046400
- 🔗 cemantle.certitudes.org 🧩 #1629 🥳 215 ⏱️ 0:06:00.782996
- 🔗 cemantix.certitudes.org 🧩 #1662 🥳 547 ⏱️ 0:25:41.275933

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


# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 2026-09-11 🤔 rarity:nan ⏱️ 0:00:33.329642

📜 2 sessions
❓ ❓ ❓
❓ ❓ ❓
❓ ❓ ❓









# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 2026-09-17 🤔 rarity:nan ⏱️ 0:00:25.671340

📜 1 sessions
❓ ❓ ❓
❓ ❓ ❓
❓ ❓ ❓


# [spaceword.org](spaceword.org) 🧩 2026-09-18 🏁 score 2168 ranked 42.1% 153/363 ⏱️ 1:31:59.587107

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 153/363

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ K N O W _ _ _ _ _   
      _ Y _ F O O T E R _   
      _ E _ _ _ _ I _ U _   
      _ S Q U I R E _ G _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #840 🟪 rarity:0.11 ⏱️ 0:01:53.302700

📜 2 sessions
🦄 🦄 🦄
🌌 🌌 🦄
🦄 🌌 🦄
Rarity: 0.11 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #686 🥳 42 ⏱️ 0:00:51.546115

🤔 42 attempts
📜 1 sessions

    @        [     0] &-teken          
    @+199531 [199531] lij              q0  ? ␅
    @+199531 [199531] lij              q1  ? after
    @+299485 [299485] schrok           q2  ? ␅
    @+299485 [299485] schrok           q3  ? after
    @+349470 [349470] vakanties        q4  ? ␅
    @+349470 [349470] vakanties        q5  ? after
    @+349470 [349470] vakanties        q6  ? ␅
    @+349470 [349470] vakanties        q7  ? after
    @+352238 [352238] vel              q14 ? ␅
    @+352238 [352238] vel              q15 ? after
    @+353071 [353071] verantwoordelijk q18 ? ␅
    @+353071 [353071] verantwoordelijk q19 ? after
    @+353269 [353269] verbeter         q22 ? ␅
    @+353269 [353269] verbeter         q23 ? after
    @+353319 [353319] verbetert        q26 ? ␅
    @+353319 [353319] verbetert        q27 ? after
    @+353339 [353339] verbeuzel        q28 ? ␅
    @+353339 [353339] verbeuzel        q29 ? after
    @+353346 [353346] verbied          q32 ? ␅
    @+353346 [353346] verbied          q33 ? after
    @+353347 [353347] verbieden        q40 ? ␅
    @+353347 [353347] verbieden        q41 ? it
    @+353347 [353347] verbieden        done. it
    @+353348 [353348] verbiedende      q38 ? ␅
    @+353348 [353348] verbiedende      q39 ? before
    @+353349 [353349] verbiedt         q34 ? ␅
    @+353349 [353349] verbiedt         q35 ? after
    @+353349 [353349] verbiedt         q36 ? ␅
    @+353349 [353349] verbiedt         q37 ? before
    @+353352 [353352] verbijster       q31 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1153 🥳 32 ⏱️ 0:00:36.337860

🤔 32 attempts
📜 1 sessions

    @        [     0] aa         
    @+98142  [ 98142] mac        q0  ? ␅
    @+98142  [ 98142] mac        q1  ? after
    @+104006 [104006] minis      q8  ? ␅
    @+104006 [104006] minis      q9  ? after
    @+104100 [104100] minute     q18 ? ␅
    @+104100 [104100] minute     q19 ? after
    @+104129 [104129] mir        q20 ? ␅
    @+104129 [104129] mir        q21 ? after
    @+104133 [104133] miracidial q28 ? ␅
    @+104133 [104133] miracidial q29 ? after
    @+104135 [104135] miracle    q30 ? ␅
    @+104135 [104135] miracle    q31 ? it
    @+104135 [104135] miracle    done. it
    @+104137 [104137] miraculous q26 ? ␅
    @+104137 [104137] miraculous q27 ? before
    @+104142 [104142] mirage     q24 ? ␅
    @+104142 [104142] mirage     q25 ? before
    @+104155 [104155] miri       q22 ? ␅
    @+104155 [104155] miri       q23 ? before
    @+104195 [104195] mis        q16 ? ␅
    @+104195 [104195] mis        q17 ? before
    @+104680 [104680] miser      q14 ? ␅
    @+104680 [104680] miser      q15 ? before
    @+105382 [105382] mist       q12 ? ␅
    @+105382 [105382] mist       q13 ? before
    @+106929 [106929] mora       q10 ? ␅
    @+106929 [106929] mora       q11 ? before
    @+109924 [109924] ne         q6  ? ␅
    @+109924 [109924] ne         q7  ? before
    @+122719 [122719] parol      q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1579 🥳 6 ⏱️ 0:01:42.058891

📜 2 sessions
💰 score: 35

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:BENNE n n n n n remain:4801
    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:2330
    ⬜⬜⬜⬜⬜ tried:MOSSO n n n n n remain:356
    ⬜⬜⬜⬜⬜ tried:KUDZU n n n n n remain:136
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:38
    ⬜⬜⬜⬜🟨 tried:PHPHT n n n n m remain:5

    Undos used: 4

      5 words remaining
    x 7 unused letters
    = 35 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1722 😦 16 ⏱️ 0:02:23.569215

📜 2 sessions
💰 score: 5060

    3/6
    CARSE ⬜🟨⬜🟨⬜
    ANILS 🟨🟨⬜🟨🟨
    SLANG 🟩🟩🟩🟩🟩
    4/6
    SLANG 🟨⬜🟩⬜⬜
    BEARS ⬜⬜🟩⬜🟨
    COAST ⬜⬜🟩🟩🟩
    AVAST 🟩🟩🟩🟩🟩
    5/6
    AVAST 🟨⬜🟨⬜⬜
    RELAY ⬜⬜⬜🟩⬜
    DUNAM ⬜⬜🟨🟩⬜
    BOGAN ⬜⬜🟩🟩🟩
    PAGAN 🟩🟩🟩🟩🟩
    2/6
    PAGAN 🟩⬜⬜🟩🟩
    PECAN 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜🟩🟩⬜⬜
    ????? ⬜🟩🟩⬜🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1699 🥳 score:22 ⏱️ 0:01:25.567687

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SCOPE attempts:4 score:4
2. HEIST attempts:7 score:7
3. PULSE attempts:5 score:5
4. CHAMP attempts:6 score:6

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1699 🥳 score:61 ⏱️ 0:02:20.744531

📜 1 sessions

Octordle Classic

1. FILET attempts:6 score:6
2. SLEEK attempts:10 score:10
3. STOIC attempts:3 score:3
4. TWEED attempts:11 score:11
5. RANCH attempts:7 score:7
6. LUMEN attempts:4 score:4
7. SHELL attempts:8 score:8
8. AVIAN attempts:12 score:12

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1679 🥳 score:50 ⏱️ 0:03:01.835653

📜 2 sessions

Sedecordle Classic sedecordle.com

1. PEDAL attempts:8 score:0
2. GENRE attempts:5 score:8
3. DOLLY attempts:16 score:1
4. SHEER attempts:9 score:6
5. HYMEN attempts:3 score:0
6. BOOZY attempts:18 score:3
7. SWUNG attempts:6 score:0
8. ELOPE attempts:10 score:6
9. DWELL attempts:7 score:0
10. ANGST attempts:11 score:7
11. SNUFF attempts:19 score:1
12. GRAPE attempts:12 score:9
13. GROWN attempts:13 score:1
14. RANGE attempts:4 score:3
15. THROW attempts:14 score:1
16. SHOVE attempts:15 score:4

# [squareword.org](squareword.org) 🧩 #1692 🥳 7 ⏱️ 0:02:00.046400

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P A S T S
    A S P E N
    S H O N E
    T E R S E
    A S T E R

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1629 🥳 215 ⏱️ 0:06:00.782996

🤔 216 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 52 chat prompts
🤖 52 gemma4:12b replies
🔥   3 🥵  20 😎  33 🥶 155 🧊   4

      $1 #216 torture           100.00°C 🥳 1000‰ ~212 used:0  [211]  source:gemma4
      $2 #171 brutality          54.47°C 🔥  995‰  ~15 used:12 [14]   source:gemma4
      $3 #189 repression         50.18°C 🔥  993‰   ~1 used:8  [0]    source:gemma4
      $4 #173 persecution        50.09°C 🔥  992‰   ~2 used:9  [1]    source:gemma4
      $5 #182 sadism             47.54°C 🥵  989‰  ~16 used:2  [15]   source:gemma4
      $6 #144 mutilation         47.01°C 🥵  987‰  ~55 used:17 [54]   source:gemma4
      $7 #207 inhumane           46.05°C 🥵  984‰   ~3 used:0  [2]    source:gemma4
      $8 #180 cruelty            45.96°C 🥵  983‰   ~4 used:1  [3]    source:gemma4
      $9 #166 humiliation        44.72°C 🥵  981‰  ~17 used:4  [16]   source:gemma4
     $10 #170 oppression         44.29°C 🥵  980‰   ~5 used:1  [4]    source:gemma4
     $11 #195 coercion           43.99°C 🥵  979‰   ~6 used:0  [5]    source:gemma4
     $25 #174 servitude          36.44°C 😎  899‰  ~22 used:0  [21]   source:gemma4
     $58 #194 suppression        24.04°C 🥶        ~69 used:0  [68]   source:gemma4
    $213   #8 suede              -1.01°C 🧊       ~213 used:0  [212]  source:gemma4

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1662 🥳 547 ⏱️ 0:25:41.275933

🤔 548 attempts
📜 1 sessions
🫧 34 chat sessions
⁉️ 191 chat prompts
🤖 19 dolphin3:latest replies
🤖 172 gemma4:12b replies
🔥   3 🥵  12 😎  77 🥶 396 🧊  59

      $1 #548 paralyser                100.00°C 🥳 1000‰ ~489 used:0   [488]  source:dolphin3
      $2 #252 paralysie                 56.60°C 😱  999‰   ~1 used:264 [0]    source:gemma4  
      $3 #403 paralysant                49.30°C 🔥  996‰   ~9 used:74  [8]    source:gemma4  
      $4 #353 tétaniser                 46.38°C 🔥  993‰   ~2 used:68  [1]    source:gemma4  
      $5 #193 blocage                   43.46°C 🥵  989‰  ~91 used:44  [90]   source:gemma4  
      $6 #276 léthargie                 38.87°C 🥵  966‰  ~79 used:14  [78]   source:gemma4  
      $7 #311 engourdissement           37.17°C 🥵  949‰  ~10 used:8   [9]    source:gemma4  
      $8 #236 immobilisme               37.08°C 🥵  948‰  ~78 used:11  [77]   source:gemma4  
      $9 #416 inefficace                36.16°C 🥵  936‰   ~3 used:7   [2]    source:gemma4  
     $10 #278 impuissance               35.96°C 🥵  930‰   ~4 used:7   [3]    source:gemma4  
     $11 #329 prostration               35.82°C 🥵  927‰   ~5 used:7   [4]    source:gemma4  
     $17 #303 incapacité                34.47°C 😎  897‰  ~12 used:0   [11]   source:gemma4  
     $94 #227 obstruction               24.68°C 🥶       ~103 used:0   [102]  source:gemma4  
    $490  #38 métal                     -0.27°C 🧊       ~490 used:0   [489]  source:gemma4  
