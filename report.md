# 2026-10-14

- 🔗 wordgrid 🧩 #865 🟪 rarity:0.35 ⏱️ 0:04:28.914989
- 🔗 spaceword.org 🧩 2026-10-13 🏁 score 2172 ranked 20.2% 65/321 ⏱️ 0:04:03.661302
- 🔗 alfagok.diginaut.net 🧩 #711 🥳 26 ⏱️ 0:00:34.971560
- 🔗 alphaguess.com 🧩 #1178 🥳 26 ⏱️ 0:00:35.442560
- 🔗 dontwordle.com 🧩 #1604 🥳 6 ⏱️ 0:01:32.107584
- 🔗 dictionary.com hurdle 🧩 #1747 🥳 17 ⏱️ 0:02:45.892884
- 🔗 Quordle Classic 🧩 #1724 🥳 score:23 ⏱️ 0:02:07.192093
- 🔗 Octordle Classic 🧩 #1724 🥳 score:63 ⏱️ 0:01:38.533106
- 🔗 Sedecordle Classic 🧩 #1704 🥳 score:38 ⏱️ 0:02:57.094526
- 🔗 squareword.org 🧩 #1717 🥳 9 ⏱️ 0:02:43.747866
- 🔗 cemantle.certitudes.org 🧩 #1654 🥳 277 ⏱️ 0:09:48.243756
- 🔗 cemantix.certitudes.org 🧩 #1687 🥳 294 ⏱️ 0:39:39.044672

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










# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #865 🟪 rarity:0.35 ⏱️ 0:04:28.914989

📜 2 sessions
🌌 🌌 🦄
🌌 🌌 🦄
🌌 🌌 🌌
Rarity: 0.35 🟪

# [spaceword.org](spaceword.org) 🧩 2026-10-13 🏁 score 2172 ranked 20.2% 65/321 ⏱️ 0:04:03.661302

📜 2 sessions
- tiles: 21/21
- score: 2172 bonus: +72
- rank: 65/321

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ N I C K E L _ _   
      _ _ I _ O _ _ O F _   
      _ _ T _ C _ T W O _   
      _ _ E _ O Z O N E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #711 🥳 26 ⏱️ 0:00:34.971560

🤔 26 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199631 [199631] lijk      q0  ? ␅
    @+199631 [199631] lijk      q1  ? after
    @+299532 [299532] schroot   q2  ? ␅
    @+299532 [299532] schroot   q3  ? after
    @+349314 [349314] vakantie  q4  ? ␅
    @+349314 [349314] vakantie  q5  ? after
    @+374048 [374048] vrij      q6  ? ␅
    @+374048 [374048] vrij      q7  ? after
    @+386583 [386583] wind      q8  ? ␅
    @+386583 [386583] wind      q9  ? after
    @+388173 [388173] woest     q14 ? ␅
    @+388173 [388173] woest     q15 ? after
    @+388845 [388845] woon      q16 ? ␅
    @+388845 [388845] woon      q17 ? after
    @+389153 [389153] woord     q18 ? ␅
    @+389153 [389153] woord     q19 ? after
    @+389473 [389473] wort      q20 ? ␅
    @+389473 [389473] wort      q21 ? after
    @+389625 [389625] wraak     q22 ? ␅
    @+389625 [389625] wraak     q23 ? after
    @+389709 [389709] wreed     q24 ? ␅
    @+389709 [389709] wreed     q25 ? it
    @+389709 [389709] wreed     done. it
    @+389792 [389792] wrik      q12 ? ␅
    @+389792 [389792] wrik      q13 ? before
    @+393000 [393000] zelfmoord q10 ? ␅
    @+393000 [393000] zelfmoord q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1178 🥳 26 ⏱️ 0:00:35.442560

🤔 26 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+23680 [23680] camp       q4  ? ␅
    @+23680 [23680] camp       q5  ? after
    @+35522 [35522] convention q6  ? ␅
    @+35522 [35522] convention q7  ? after
    @+40838 [40838] da         q8  ? ␅
    @+40838 [40838] da         q9  ? after
    @+41163 [41163] dan        q16 ? ␅
    @+41163 [41163] dan        q17 ? after
    @+41346 [41346] darn       q18 ? ␅
    @+41346 [41346] darn       q19 ? after
    @+41393 [41393] dashi      q22 ? ␅
    @+41393 [41393] dashi      q23 ? after
    @+41415 [41415] data       q24 ? ␅
    @+41415 [41415] data       q25 ? it
    @+41415 [41415] data       done. it
    @+41448 [41448] dative     q20 ? ␅
    @+41448 [41448] dative     q21 ? before
    @+41548 [41548] day        q14 ? ␅
    @+41548 [41548] day        q15 ? before
    @+42369 [42369] deco       q12 ? ␅
    @+42369 [42369] deco       q13 ? before
    @+44066 [44066] den        q10 ? ␅
    @+44066 [44066] den        q11 ? before
    @+47374 [47374] dis        q2  ? ␅
    @+47374 [47374] dis        q3  ? before
    @+98142 [98142] mac        q0  ? ␅
    @+98142 [98142] mac        q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1604 🥳 6 ⏱️ 0:01:32.107584

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:FEEZE n n n n n remain:6482
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:3628
    ⬜⬜⬜⬜⬜ tried:YOBBY n n n n n remain:1269
    ⬜⬜⬜⬜⬜ tried:JUGUM n n n n n remain:470
    ⬜🟨⬜⬜⬜ tried:PHPHT n m n n n remain:31
    ⬜🟨⬜🟨🟩 tried:RANCH n m n m Y remain:1

    Undos used: 4

      1 words remaining
    x 6 unused letters
    = 6 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1747 🥳 17 ⏱️ 0:02:45.892884

📜 1 sessions
💰 score: 9900

    4/6
    TORES 🟨🟨🟨🟩⬜
    OATER 🟩⬜🟩🟩🟩
    UNFIX 🟨⬜⬜⬜⬜
    OUTER 🟩🟩🟩🟩🟩
    4/6
    OUTER ⬜🟨⬜⬜⬜
    SCULP ⬜⬜🟩⬜⬜
    GAUDY ⬜🟨🟩⬜⬜
    ABUZZ 🟩🟩🟩🟩🟩
    4/6
    ABUZZ ⬜⬜⬜⬜⬜
    ROLES ⬜🟩⬜🟩⬜
    TONED 🟩🟩🟨🟩⬜
    TOKEN 🟩🟩🟩🟩🟩
    4/6
    TOKEN ⬜⬜⬜⬜⬜
    RAILS 🟨⬜🟩🟩⬜
    BADGE ⬜⬜🟨⬜⬜
    DRILL 🟩🟩🟩🟩🟩
    Final 1/2
    DRILL 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1724 🥳 score:23 ⏱️ 0:02:07.192093

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. TIMID attempts:4 score:4
2. GROUP attempts:5 score:5
3. GRILL attempts:6 score:6
4. EVERY attempts:8 score:8

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1724 🥳 score:63 ⏱️ 0:01:38.533106

📜 1 sessions

Octordle Classic

1. SLYLY attempts:5 score:5
2. SWAMI attempts:10 score:10
3. OMBRE attempts:11 score:11
4. IDIOM attempts:6 score:6
5. SNEER attempts:8 score:8
6. HAUNT attempts:4 score:4
7. DEMON attempts:7 score:7
8. BOARD attempts:12 score:12

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1704 🥳 score:38 ⏱️ 0:02:57.094526

📜 1 sessions

Sedecordle Classic sedecordle.com

1. NAVAL attempts:17 score:1
2. QUASH attempts:5 score:7
3. TASTE attempts:16 score:1
4. CLERK attempts:15 score:6
5. PLEAD attempts:3 score:0
6. SWAMI attempts:14 score:3
7. STRUT attempts:13 score:1
8. ALIGN attempts:7 score:3
9. VOGUE attempts:12 score:1
10. BLANK attempts:11 score:2
11. SULLY attempts:4 score:0
12. MOGUL attempts:9 score:4
13. CLEAN attempts:8 score:0
14. CHOCK attempts:18 score:8
15. EXULT attempts:10 score:1
16. BRAID attempts:6 score:0

# [squareword.org](squareword.org) 🧩 #1717 🥳 9 ⏱️ 0:02:43.747866

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    H A V O C
    O D O U R
    S M I T E
    T I L E S
    S T A R T

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1654 🥳 277 ⏱️ 0:09:48.243756

🤔 278 attempts
📜 1 sessions
🫧 13 chat sessions
⁉️ 63 chat prompts
🤖 63 dolphin3:latest replies
🔥   1 🥵  10 😎  33 🥶 229 🧊   4

      $1 #278 biology            100.00°C 🥳 1000‰ ~274 used:0  [273]  source:dolphin3
      $2 #254 science             67.76°C 🔥  997‰   ~2 used:11 [1]    source:dolphin3
      $3 #213 neuroscience        57.90°C 🥵  989‰  ~35 used:14 [34]   source:dolphin3
      $4 #148 mathematics         56.22°C 🥵  985‰  ~37 used:17 [36]   source:dolphin3
      $5 #167 physics             53.86°C 🥵  979‰   ~8 used:7  [7]    source:dolphin3
      $6 #245 psychology          51.09°C 🥵  966‰   ~4 used:4  [3]    source:dolphin3
      $7 #192 linguistics         51.08°C 🥵  965‰   ~7 used:6  [6]    source:dolphin3
      $8 #149 algebra             48.36°C 🥵  945‰   ~5 used:5  [4]    source:dolphin3
      $9 #113 engineering         47.44°C 🥵  936‰  ~36 used:15 [35]   source:dolphin3
     $10 #252 interdisciplinary   46.34°C 🥵  926‰   ~3 used:2  [2]    source:dolphin3
     $11 #139 computational       45.40°C 🥵  919‰   ~6 used:5  [5]    source:dolphin3
     $13 #179 calculus            42.80°C 😎  883‰   ~9 used:0  [8]    source:dolphin3
     $46 #102 learning            28.15°C 🥶        ~53 used:0  [52]   source:dolphin3
    $275 #107 reporting           -0.07°C 🧊       ~275 used:0  [274]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1687 🥳 294 ⏱️ 0:39:39.044672

🤔 295 attempts
📜 1 sessions
🫧 13 chat sessions
⁉️ 70 chat prompts
🤖 20 dolphin3:latest replies
🤖 50 gemma4:12b replies
😱   1 🔥   1 🥵  12 😎  58 🥶 188 🧊  34

      $1 #295 objection           100.00°C 🥳 1000‰ ~261 used:0  [260]  source:dolphin3
      $2 #285 argument             57.74°C 😱  999‰   ~1 used:2  [0]    source:dolphin3
      $3 #286 argumentation        51.40°C 🔥  997‰   ~2 used:1  [1]    source:dolphin3
      $4 #273 sophisme             43.79°C 🥵  985‰   ~7 used:6  [6]    source:dolphin3
      $5 #254 contradiction        42.40°C 🥵  974‰   ~8 used:8  [7]    source:dolphin3
      $6  #96 évident              41.06°C 🥵  967‰  ~71 used:54 [70]   source:gemma4  
      $7 #264 désaccord            39.67°C 🥵  955‰   ~5 used:4  [4]    source:dolphin3
      $8 #294 justification        39.24°C 🥵  949‰   ~3 used:0  [2]    source:dolphin3
      $9 #126 catégorique          39.02°C 🥵  946‰  ~68 used:33 [67]   source:gemma4  
     $10 #155 contradictoire       38.70°C 🥵  940‰  ~56 used:18 [55]   source:gemma4  
     $11 #292 critique             38.40°C 🥵  938‰   ~4 used:0  [3]    source:dolphin3
     $16 #166 discutable           36.30°C 😎  891‰  ~57 used:2  [56]   source:gemma4  
     $74 #268 défaut               25.28°C 🥶        ~78 used:0  [77]   source:dolphin3
    $262 #181 mystérieux           -0.02°C 🧊       ~262 used:0  [261]  source:gemma4  
