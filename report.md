# 2026-10-23

- 🔗 spaceword.org 🧩 2026-10-22 🏁 score 2168 ranked 41.6% 127/305 ⏱️ 2:10:27.167437
- 🔗 wordgrid 🧩 #874 🟪 rarity:0.24 ⏱️ 0:02:36.094930
- 🔗 alfagok.diginaut.net 🧩 #720 🥳 30 ⏱️ 0:00:47.841662
- 🔗 alphaguess.com 🧩 #1187 🥳 34 ⏱️ 0:00:50.391352
- 🔗 dontwordle.com 🧩 #1613 🥳 6 ⏱️ 0:01:40.178994
- 🔗 dictionary.com hurdle 🧩 #1756 🥳 20 ⏱️ 0:03:22.385600
- 🔗 Quordle Classic 🧩 #1733 🥳 score:22 ⏱️ 0:01:32.474062
- 🔗 Octordle Classic 🧩 #1733 🥳 score:68 ⏱️ 0:04:01.497254
- 🔗 Sedecordle Classic 🧩 #1713 🥳 score:40 ⏱️ 0:05:15.464718
- 🔗 squareword.org 🧩 #1726 🥳 8 ⏱️ 0:02:19.435685
- 🔗 cemantle.certitudes.org 🧩 #1663 🥳 97 ⏱️ 0:07:00.201715
- 🔗 cemantix.certitudes.org 🧩 #1696 🥳 167 ⏱️ 0:09:37.328740

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



















# [spaceword.org](spaceword.org) 🧩 2026-10-22 🏁 score 2168 ranked 41.6% 127/305 ⏱️ 2:10:27.167437

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 127/305

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ C U P _ _ _ _   
      _ _ _ U T E _ _ _ _   
      _ _ _ R _ K I _ _ _   
      _ _ _ _ G O O _ _ _   
      _ _ _ _ _ E N _ _ _   
      _ _ _ _ _ S I _ _ _   
      _ _ _ _ _ _ Z _ _ _   
      _ _ _ J A D E _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #874 🟪 rarity:0.24 ⏱️ 0:02:36.094930

📜 2 sessions
🌌 🌌 🦄
🌌 🌌 🌌
🦄 🌌 🌌
Rarity: 0.24 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #720 🥳 30 ⏱️ 0:00:47.841662

🤔 30 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+2      [     2] -cijferig  
    @+199631 [199631] lijk       q0  ? ␅
    @+199631 [199631] lijk       q1  ? after
    @+224526 [224526] moord      q6  ? ␅
    @+224526 [224526] moord      q7  ? after
    @+224541 [224541] moorddadig q26 ? ␅
    @+224541 [224541] moorddadig q27 ? after
    @+224550 [224550] moorden    q28 ? ␅
    @+224550 [224550] moorden    q29 ? it
    @+224550 [224550] moorden    done. it
    @+224568 [224568] moordgeval q24 ? ␅
    @+224568 [224568] moordgeval q25 ? before
    @+224610 [224610] moordwapen q22 ? ␅
    @+224610 [224610] moordwapen q23 ? before
    @+224693 [224693] mor        q20 ? ␅
    @+224693 [224693] mor        q21 ? before
    @+225243 [225243] mossel     q18 ? ␅
    @+225243 [225243] mossel     q19 ? before
    @+225994 [225994] mui        q16 ? ␅
    @+225994 [225994] mui        q17 ? before
    @+227487 [227487] myriade    q14 ? ␅
    @+227487 [227487] myriade    q15 ? before
    @+230446 [230446] neer       q10 ? ␅
    @+230446 [230446] neer       q11 ? before
    @+237014 [237014] om         q8  ? ␅
    @+237014 [237014] om         q9  ? before
    @+249548 [249548] opinie     q4  ? ␅
    @+249548 [249548] opinie     q5  ? before
    @+299528 [299528] schroot    q2  ? ␅
    @+299528 [299528] schroot    q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1187 🥳 34 ⏱️ 0:00:50.391352

🤔 34 attempts
📜 1 sessions

    @        [     0] aa          
    @+98142  [ 98142] mac         q0  ? ␅
    @+98142  [ 98142] mac         q1  ? after
    @+122718 [122718] parol       q4  ? ␅
    @+122718 [122718] parol       q5  ? after
    @+134997 [134997] prop        q6  ? ␅
    @+134997 [134997] prop        q7  ? after
    @+135057 [135057] proper      q20 ? ␅
    @+135057 [135057] proper      q21 ? after
    @+135061 [135061] properest   q28 ? ␅
    @+135061 [135061] properest   q29 ? after
    @+135062 [135062] properly    q32 ? ␅
    @+135062 [135062] properly    q33 ? it
    @+135062 [135062] properly    done. it
    @+135063 [135063] properness  q30 ? ␅
    @+135063 [135063] properness  q31 ? before
    @+135065 [135065] propers     q26 ? ␅
    @+135065 [135065] propers     q27 ? before
    @+135072 [135072] prophase    q24 ? ␅
    @+135072 [135072] prophase    q25 ? before
    @+135087 [135087] prophet     q22 ? ␅
    @+135087 [135087] prophet     q23 ? before
    @+135114 [135114] propitiator q18 ? ␅
    @+135114 [135114] propitiator q19 ? before
    @+135235 [135235] pros        q16 ? ␅
    @+135235 [135235] pros        q17 ? before
    @+135700 [135700] proven      q14 ? ␅
    @+135700 [135700] proven      q15 ? before
    @+136416 [136416] pul         q12 ? ␅
    @+136416 [136416] pul         q13 ? before
    @+138003 [138003] quetzal     q11 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1613 🥳 6 ⏱️ 0:01:40.178994

📜 1 sessions
💰 score: 88

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:COOCH n n n n n remain:6849
    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:3740
    ⬜⬜⬜⬜⬜ tried:VUGGY n n n n n remain:1621
    ⬜⬜🟩⬜⬜ tried:ABAFT n n Y n n remain:119
    🟩⬜🟩🟨⬜ tried:SNAPS Y n Y m n remain:12
    🟩🟩🟩⬜⬜ tried:SPAZZ Y Y Y n n remain:11

    Undos used: 2

      11 words remaining
    x 8 unused letters
    = 88 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1756 🥳 20 ⏱️ 0:03:22.385600

📜 1 sessions
💰 score: 9600

    4/6
    TOEAS 🟨⬜🟨⬜⬜
    LITER ⬜⬜🟨🟨🟨
    BRUTE 🟩🟨⬜🟩🟨
    BERTH 🟩🟩🟩🟩🟩
    5/6
    BERTH 🟨🟩🟨⬜⬜
    DEBAR ⬜🟩🟩⬜🟨
    REBUS 🟩🟩🟩⬜⬜
    CLAMP ⬜🟨⬜⬜⬜
    REBEL 🟩🟩🟩🟩🟩
    5/6
    REBEL 🟨⬜🟨⬜⬜
    BRASH 🟩🟩🟩⬜⬜
    BRAIN 🟩🟩🟩⬜🟨
    KITED ⬜⬜⬜⬜🟩
    BRAND 🟩🟩🟩🟩🟩
    4/6
    BRAND ⬜⬜⬜⬜🟨
    LOIDS ⬜🟨⬜🟩⬜
    GEODE ⬜⬜🟨🟩⬜
    OUTDO 🟩🟩🟩🟩🟩
    Final 2/2
    MAGIC ⬜⬜⬜⬜🟨
    HENCE 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1733 🥳 score:22 ⏱️ 0:01:32.474062

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. BLIMP attempts:4 score:4
2. HOIST attempts:7 score:7
3. FRIED attempts:6 score:6
4. LURID attempts:5 score:5

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1733 🥳 score:68 ⏱️ 0:04:01.497254

📜 1 sessions

Octordle Classic

1. TAPER attempts:12 score:12
2. UNDID attempts:13 score:13
3. LIEGE attempts:6 score:6
4. CAUSE attempts:4 score:4
5. PAGAN attempts:8 score:8
6. QUICK attempts:5 score:5
7. FIELD attempts:9 score:9
8. TOTAL attempts:11 score:11

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1713 🥳 score:40 ⏱️ 0:05:15.464718

📜 1 sessions

Sedecordle Classic sedecordle.com

1. SWEAT attempts:2 score:0
2. LEECH attempts:11 score:2
3. DIMLY attempts:10 score:1
4. BINGE attempts:12 score:0
5. GRIEF attempts:8 score:0
6. PRISM attempts:17 score:8
7. FORAY attempts:9 score:0
8. POPPY attempts:13 score:9
9. CRAZE attempts:20 score:2
10. ADOPT attempts:5 score:0
11. STEER attempts:7 score:0
12. PIXEL attempts:19 score:7
13. LITHE attempts:14 score:1
14. AUGUR attempts:6 score:4
15. BROOK attempts:15 score:1
16. BRING attempts:16 score:5

# [squareword.org](squareword.org) 🧩 #1726 🥳 8 ⏱️ 0:02:19.435685

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟩 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P R I G
    C R A N E
    R I V E N
    A D E P T
    M E L T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1663 🥳 97 ⏱️ 0:07:00.201715

🤔 98 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 12 chat prompts
🤖 12 gemma4:12b replies
🔥  1 😎  7 🥶 84 🧊  5

     $1 #98 stream          100.00°C 🥳 1000‰ ~93 used:0 [92]  source:gemma4
     $2 #85 flow             43.55°C 🔥  995‰  ~1 used:1 [0]   source:gemma4
     $3 #95 route            25.22°C 😎  688‰  ~2 used:0 [1]   source:gemma4
     $4 #37 static           24.06°C 😎  586‰  ~7 used:6 [6]   source:gemma4
     $5 #73 path             22.71°C 😎  439‰  ~3 used:0 [2]   source:gemma4
     $6 #23 matrix           21.88°C 😎  303‰  ~8 used:6 [7]   source:gemma4
     $7 #54 linear           21.73°C 😎  273‰  ~6 used:5 [5]   source:gemma4
     $8 #61 basis            21.58°C 😎  238‰  ~4 used:1 [3]   source:gemma4
     $9 #47 network          20.93°C 😎   86‰  ~5 used:3 [4]   source:gemma4
    $10 #30 system           19.59°C 🥶       ~12 used:0 [11]  source:gemma4
    $11 #40 constant         19.52°C 🥶       ~13 used:0 [12]  source:gemma4
    $12 #70 hub              19.17°C 🥶       ~14 used:0 [13]  source:gemma4
    $13 #48 structure        18.11°C 🥶       ~15 used:0 [14]  source:gemma4
    $94  #8 sourdough        -0.57°C 🧊       ~94 used:0 [93]  source:gemma4

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1696 🥳 167 ⏱️ 0:09:37.328740

🤔 168 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 24 chat prompts
🤖 24 gemma4:12b replies
🥵   5 😎  24 🥶 105 🧊  33

      $1 #168 crédibilité    100.00°C 🥳 1000‰ ~135 used:0  [134]  source:gemma4
      $2  #84 conviction      42.96°C 🥵  983‰   ~5 used:10 [4]    source:gemma4
      $3 #107 opinion         39.12°C 🥵  956‰   ~4 used:8  [3]    source:gemma4
      $4 #144 certitude       35.43°C 🥵  915‰   ~2 used:4  [1]    source:gemma4
      $5 #135 ambition        34.75°C 🥵  904‰   ~1 used:3  [0]    source:gemma4
      $6 #111 volonté         34.67°C 🥵  901‰   ~3 used:5  [2]    source:gemma4
      $7 #145 affirmation     33.90°C 😎  884‰   ~6 used:0  [5]    source:gemma4
      $8 #131 argumentaire    33.36°C 😎  867‰   ~7 used:0  [6]    source:gemma4
      $9 #123 position        33.27°C 😎  864‰   ~8 used:0  [7]    source:gemma4
     $10  #98 engagement      32.47°C 😎  831‰   ~9 used:0  [8]    source:gemma4
     $11 #103 intention       31.53°C 😎  786‰  ~10 used:0  [9]    source:gemma4
     $12 #115 attitude        30.53°C 😎  737‰  ~11 used:0  [10]   source:gemma4
     $31 #122 point           23.54°C 🥶        ~34 used:0  [33]   source:gemma4
    $136  #31 aventure        -0.72°C 🧊       ~136 used:0  [135]  source:gemma4
