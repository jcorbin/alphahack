# 2026-02-05

- 🔗 spaceword.org 🧩 2026-02-04 🏁 score 2168 ranked 32.9% 116/353 ⏱️ 0:03:56.995474
- 🔗 alphaguess.com 🧩 #927 🥳 24 ⏱️ 0:00:34.327497
- 🔗 dontwordle.com 🧩 #1353 🥳 6 ⏱️ 0:01:46.191789
- 🔗 dictionary.com hurdle 🧩 #1496 🥳 17 ⏱️ 0:03:16.473092
- 🔗 Quordle Classic 🧩 #1473 🥳 score:18 ⏱️ 0:01:09.055913
- 🔗 Octordle Classic 🧩 #1473 🥳 score:56 ⏱️ 0:03:47.439512
- 🔗 squareword.org 🧩 #1466 🥳 8 ⏱️ 0:02:09.328188
- 🔗 cemantle.certitudes.org 🧩 #1403 🥳 139 ⏱️ 1:06:54.196352
- 🔗 alfagok.diginaut.net 🧩 #460 🥳 24 ⏱️ 0:00:30.095499
- 🔗 cemantix.certitudes.org 🧩 #1436 🥳 223 ⏱️ 0:56:45.379101

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





















# [spaceword.org](spaceword.org) 🧩 2026-02-04 🏁 score 2168 ranked 32.9% 116/353 ⏱️ 0:03:56.995474

📜 2 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 116/353

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ B I Z _ _ _ _   
      _ _ _ E _ _ Q _ _ _   
      _ _ _ T O F U _ _ _   
      _ _ _ E _ L A _ _ _   
      _ _ _ L _ A N _ _ _   
      _ _ _ _ J U G _ _ _   
      _ _ _ _ _ T O _ _ _   
      _ _ _ _ _ A _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alphaguess.com](alphaguess.com) 🧩 #927 🥳 24 ⏱️ 0:00:34.327497

🤔 24 attempts
📜 1 sessions

    @       [    0] aa       
    @+1     [    1] aah      
    @+2     [    2] aahed    
    @+3     [    3] aahing   
    @+11764 [11764] back     q6  ? ␅
    @+11764 [11764] back     q7  ? after
    @+17715 [17715] blind    q8  ? ␅
    @+17715 [17715] blind    q9  ? after
    @+20687 [20687] brill    q10 ? ␅
    @+20687 [20687] brill    q11 ? after
    @+22027 [22027] bur      q12 ? ␅
    @+22027 [22027] bur      q13 ? after
    @+22027 [22027] bur      q14 ? ␅
    @+22027 [22027] bur      q15 ? after
    @+22288 [22288] bus      q20 ? ␅
    @+22288 [22288] bus      q21 ? after
    @+22554 [22554] button   q22 ? ␅
    @+22554 [22554] button   q23 ? it
    @+22554 [22554] button   done. it
    @+22855 [22855] cachalot q18 ? ␅
    @+22855 [22855] cachalot q19 ? before
    @+23682 [23682] camp     q4  ? ␅
    @+23682 [23682] camp     q5  ? before
    @+47381 [47381] dis      q2  ? ␅
    @+47381 [47381] dis      q3  ? before
    @+98219 [98219] mach     q0  ? ␅
    @+98219 [98219] mach     q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1353 🥳 6 ⏱️ 0:01:46.191789

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:7419
    ⬜⬜⬜⬜⬜ tried:CEDED n n n n n remain:2420
    ⬜⬜⬜⬜⬜ tried:PIPIT n n n n n remain:769
    ⬜⬜⬜⬜⬜ tried:MUMMS n n n n n remain:116
    ⬜⬜⬜⬜🟨 tried:GRRRL n n n n m remain:25
    ⬜🟨⬜🟨🟩 tried:FLYBY n m n m Y remain:1

    Undos used: 3

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1496 🥳 17 ⏱️ 0:03:16.473092

📜 1 sessions
💰 score: 9900

    5/6
    TOEAS ⬜🟨⬜⬜🟨
    SHORN 🟩⬜🟩⬜⬜
    SCOLD 🟩⬜🟩⬜⬜
    SMOKY 🟩⬜🟩🟨⬜
    SPOOK 🟩🟩🟩🟩🟩
    2/6
    SPOOK ⬜⬜🟩🟩🟩
    BROOK 🟩🟩🟩🟩🟩
    4/6
    BROOK ⬜⬜🟩🟩⬜
    SPOOL 🟩🟨🟩🟩⬜
    SCOOP 🟩⬜🟩🟩🟩
    SNOOP 🟩🟩🟩🟩🟩
    4/6
    SNOOP ⬜⬜⬜🟩⬜
    TUMOR ⬜⬜⬜🟩🟩
    VALOR ⬜🟩🟨🟩🟩
    LABOR 🟩🟩🟩🟩🟩
    Final 2/2
    ARDOR 🟩🟩⬜🟩🟩
    ARMOR 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1473 🥳 score:18 ⏱️ 0:01:09.055913

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. THROB attempts:4 score:4
2. BUILT attempts:5 score:5
3. NOBLE attempts:6 score:6
4. THUMB attempts:3 score:3

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1473 🥳 score:56 ⏱️ 0:03:47.439512

📜 1 sessions

Octordle Classic

1. PENNY attempts:10 score:10
2. MANGY attempts:8 score:8
3. SCION attempts:5 score:5
4. SOLVE attempts:6 score:6
5. THEME attempts:9 score:9
6. ANODE attempts:3 score:3
7. BRINK attempts:11 score:11
8. ACORN attempts:4 score:4

# [squareword.org](squareword.org) 🧩 #1466 🥳 8 ⏱️ 0:02:09.328188

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟨
    🟨 🟩 🟨 🟨 🟩
    🟨 🟩 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    M A N G A
    A L O U D
    L I V I D
    T E A S E
    S N E E R

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1403 🥳 139 ⏱️ 1:06:54.196352

🤔 140 attempts
📜 27 sessions
🫧 11 chat sessions
⁉️ 28 chat prompts
🤖 6 qwen3:14b replies
🤖 22 qwen3:1.7b replies
🥵   3 😎  12 🥶 119 🧊   5

      $1 #140    citation  100.00°C 🥳 1000‰ ~135  used:0  [134] source:qwen3:14b 
      $2 #120       essay   33.39°C 🥵  962‰   ~3  used:8    [2] source:qwen3:1.7b
      $3 #123        poem   30.44°C 🥵  940‰   ~2  used:5    [1] source:qwen3:1.7b
      $4 #121     journal   28.91°C 🥵  904‰   ~1  used:3    [0] source:qwen3:1.7b
      $5  #73        book   24.08°C 😎  700‰  ~14  used:6   [13] source:qwen3:1.7b
      $6 #134      thesis   24.05°C 😎  696‰   ~4  used:1    [3] source:qwen3:1.7b
      $7 #119     article   23.84°C 😎  677‰   ~5  used:0    [4] source:qwen3:1.7b
      $8   #4         dog   23.27°C 😎  620‰  ~15 used:12   [14] source:qwen3:1.7b
      $9 #135       verse   22.08°C 😎  500‰   ~6  used:0    [5] source:qwen3:1.7b
     $10 #136    argument   21.84°C 😎  476‰   ~7  used:0    [6] source:qwen3:14b 
     $11  #95        text   21.60°C 😎  440‰  ~13  used:2   [12] source:qwen3:1.7b
     $12 #113       sheet   21.28°C 😎  394‰   ~8  used:0    [7] source:qwen3:1.7b
     $17  #26       brake   18.72°C 🥶        ~17  used:3   [16] source:qwen3:1.7b
    $136  #70        void   -0.15°C 🧊       ~136  used:0  [135] source:qwen3:1.7b

# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #460 🥳 24 ⏱️ 0:00:30.095499

🤔 24 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199826 [199826] lijm      q0  ? ␅
    @+199826 [199826] lijm      q1  ? after
    @+299731 [299731] schub     q2  ? ␅
    @+299731 [299731] schub     q3  ? after
    @+349501 [349501] vakantie  q4  ? ␅
    @+349501 [349501] vakantie  q5  ? after
    @+353069 [353069] ver       q8  ? ␅
    @+353069 [353069] ver       q9  ? after
    @+363652 [363652] verzot    q10 ? ␅
    @+363652 [363652] verzot    q11 ? after
    @+368664 [368664] voetbal   q12 ? ␅
    @+368664 [368664] voetbal   q13 ? after
    @+369017 [369017] voeten    q18 ? ␅
    @+369017 [369017] voeten    q19 ? after
    @+369192 [369192] voetzool  q20 ? ␅
    @+369192 [369192] voetzool  q21 ? after
    @+369196 [369196] vogel     q22 ? ␅
    @+369196 [369196] vogel     q23 ? it
    @+369196 [369196] vogel     done. it
    @+369373 [369373] vol       q16 ? ␅
    @+369373 [369373] vol       q17 ? before
    @+370513 [370513] voor      q14 ? ␅
    @+370513 [370513] voor      q15 ? before
    @+374242 [374242] vrij      q6  ? ␅
    @+374242 [374242] vrij      q7  ? before

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1436 🥳 223 ⏱️ 0:56:45.379101

🤔 224 attempts
📜 2 sessions
🫧 12 chat sessions
⁉️ 60 chat prompts
🤖 60 qwen3:14b replies
😱   1 🔥   4 🥵  12 😎  21 🥶 156 🧊  29

      $1 #224 géant               100.00°C 🥳 1000‰ ~195 used:0   [194] source:qwen3
      $2 #208 gigantesque          60.54°C 😱  999‰   ~1 used:24    [0] source:qwen3
      $3 #216 mastodonte           49.18°C 🔥  998‰   ~4 used:7     [3] source:qwen3
      $4 #218 monstre              43.03°C 🔥  996‰   ~3 used:6     [2] source:qwen3
      $5 #210 immense              41.87°C 🔥  992‰   ~2 used:5     [1] source:qwen3
      $6 #205 colossal             40.56°C 🔥  991‰   ~5 used:7     [4] source:qwen3
      $7 #220 monstrueux           39.68°C 🥵  989‰   ~6 used:0     [5] source:qwen3
      $8 #214 titanesque           39.32°C 🥵  988‰   ~7 used:0     [6] source:qwen3
      $9 #215 énorme               38.90°C 🥵  987‰   ~8 used:0     [7] source:qwen3
     $10 #201 impressionnant       37.36°C 🥵  981‰  ~12 used:3    [11] source:qwen3
     $11 #206 imposant             36.44°C 🥵  978‰   ~9 used:0     [8] source:qwen3
     $19 #154 légendaire           30.00°C 😎  869‰  ~27 used:2    [26] source:qwen3
     $40  #17 météore              22.81°C 🥶        ~39 used:0    [38] source:qwen3
    $196   #7 plaire               -0.13°C 🧊       ~196 used:0   [195] source:qwen3
