# 2026-09-16

- 🔗 spaceword.org 🧩 2026-09-15 🏁 score 2173 ranked 8.9% 31/348 ⏱️ 0:53:33.323464
- 🔗 wordgrid 🧩 #837 🟪 rarity:0.29 ⏱️ 0:03:04.866394
- 🔗 alfagok.diginaut.net 🧩 #683 🥳 22 ⏱️ 0:00:33.423352
- 🔗 alphaguess.com 🧩 #1150 🥳 30 ⏱️ 0:00:31.951942
- 🔗 dontwordle.com 🧩 #1576 🥳 6 ⏱️ 0:02:29.304576
- 🔗 dictionary.com hurdle 🧩 #1719 🥳 20 ⏱️ 0:06:06.484035
- 🔗 Quordle Classic 🧩 #1696 🥳 score:24 ⏱️ 0:45:05.897329
- 🔗 Octordle Classic 🧩 #1696 🥳 score:62 ⏱️ 0:02:18.696634
- 🔗 Sedecordle Classic 🧩 #1676 🥳 score:43 ⏱️ 0:08:25.937383
- 🔗 squareword.org 🧩 #1689 🥳 7 ⏱️ 0:02:11.832542
- 🔗 cemantle.certitudes.org 🧩 #1626 🥳 331 ⏱️ 2:39:45.352492
- 🔗 cemantix.certitudes.org 🧩 #1659 🥳 276 ⏱️ 0:23:07.340894

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







# [spaceword.org](spaceword.org) 🧩 2026-09-15 🏁 score 2173 ranked 8.9% 31/348 ⏱️ 0:53:33.323464

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 31/348

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ V _ T O X E M I A   
      _ O _ _ _ _ Y I N S   
      _ E Q U A T E S _ H   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #837 🟪 rarity:0.29 ⏱️ 0:03:04.866394

📜 2 sessions
🦄 🌌 🌌
🦄 🦄 🦄
🌌 🌌 🌌
Rarity: 0.29 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #683 🥳 22 ⏱️ 0:00:33.423352

🤔 22 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199531 [199531] lij       q0  ? ␅
    @+199531 [199531] lij       q1  ? after
    @+247581 [247581] op        q4  ? ␅
    @+247581 [247581] op        q5  ? after
    @+249175 [249175] opgespeld q14 ? ␅
    @+249175 [249175] opgespeld q15 ? after
    @+249899 [249899] opleiding q16 ? ␅
    @+249899 [249899] opleiding q17 ? after
    @+250108 [250108] oplossing q20 ? ␅
    @+250108 [250108] oplossing q21 ? it
    @+250108 [250108] oplossing done. it
    @+250329 [250329] opoffer   q18 ? ␅
    @+250329 [250329] opoffer   q19 ? before
    @+250769 [250769] oproep    q12 ? ␅
    @+250769 [250769] oproep    q13 ? before
    @+253985 [253985] out       q10 ? ␅
    @+253985 [253985] out       q11 ? before
    @+260456 [260456] pater     q8  ? ␅
    @+260456 [260456] pater     q9  ? before
    @+273373 [273373] proef     q6  ? ␅
    @+273373 [273373] proef     q7  ? before
    @+299485 [299485] schrok    q2  ? ␅
    @+299485 [299485] schrok    q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1150 🥳 30 ⏱️ 0:00:31.951942

🤔 30 attempts
📜 1 sessions

    @       [    0] aa         
    @+2     [    2] aahed      
    @+47374 [47374] dis        q2  ? ␅
    @+47374 [47374] dis        q3  ? after
    @+60013 [60013] eyewitness q6  ? ␅
    @+60013 [60013] eyewitness q7  ? after
    @+66305 [66305] free       q8  ? ␅
    @+66305 [66305] free       q9  ? after
    @+67080 [67080] fuck       q14 ? ␅
    @+67080 [67080] fuck       q15 ? after
    @+67440 [67440] fur        q16 ? ␅
    @+67440 [67440] fur        q17 ? after
    @+67547 [67547] furrow     q22 ? ␅
    @+67547 [67547] furrow     q23 ? after
    @+67556 [67556] further    q28 ? ␅
    @+67556 [67556] further    q29 ? it
    @+67556 [67556] further    done. it
    @+67575 [67575] fury       q26 ? ␅
    @+67575 [67575] fury       q27 ? before
    @+67603 [67603] fusil      q24 ? ␅
    @+67603 [67603] fusil      q25 ? before
    @+67660 [67660] futharc    q20 ? ␅
    @+67660 [67660] futharc    q21 ? before
    @+67879 [67879] gain       q12 ? ␅
    @+67879 [67879] gain       q13 ? before
    @+69477 [69477] geode      q10 ? ␅
    @+69477 [69477] geode      q11 ? before
    @+72657 [72657] green      q4  ? ␅
    @+72657 [72657] green      q5  ? before
    @+98142 [98142] mac        q0  ? ␅
    @+98142 [98142] mac        q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1576 🥳 6 ⏱️ 0:02:29.304576

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:PUPUS n n n n n remain:4885
    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:2416
    ⬜⬜⬜⬜⬜ tried:CALLA n n n n n remain:623
    ⬜⬜⬜⬜⬜ tried:ROTOR n n n n n remain:73
    ⬜🟩🟩⬜⬜ tried:FEEZE n Y Y n n remain:5
    🟩🟩🟩⬜🟩 tried:WEENY Y Y Y n Y remain:1

    Undos used: 4

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1719 🥳 20 ⏱️ 0:06:06.484035

📜 1 sessions
💰 score: 9600

    4/6
    REAIS ⬜⬜⬜🟨⬜
    GLINT 🟨⬜🟩🟩🟨
    THING 🟩⬜🟩🟩🟩
    TYING 🟩🟩🟩🟩🟩
    4/6
    TYING ⬜⬜🟩⬜⬜
    CRIES ⬜🟨🟩⬜🟨
    SHIRK 🟩⬜🟩🟩🟩
    SMIRK 🟩🟩🟩🟩🟩
    5/6
    SMIRK ⬜⬜🟨⬜⬜
    LINEY ⬜🟩⬜⬜🟩
    DITZY ⬜🟩🟨⬜🟩
    WIFTY ⬜🟩🟩🟩🟩
    FIFTY 🟩🟩🟩🟩🟩
    5/6
    FIFTY ⬜🟨⬜⬜⬜
    RAILS ⬜⬜🟩🟨🟨
    SLICE 🟩🟩🟩⬜🟩
    AMPED ⬜⬜⬜🟨🟨
    SLIDE 🟩🟩🟩🟩🟩
    Final 2/2
    UPBOW ⬜⬜🟨⬜⬜
    ABACK 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1696 🥳 score:24 ⏱️ 0:45:05.897329

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SPEAR attempts:4 score:4
2. PRICE attempts:5 score:5
3. BLUNT attempts:8 score:8
4. FISHY attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1696 🥳 score:62 ⏱️ 0:02:18.696634

📜 1 sessions

Octordle Classic

1. BONUS attempts:4 score:4
2. MOUND attempts:11 score:11
3. WORRY attempts:12 score:12
4. CUTIE attempts:5 score:5
5. COACH attempts:7 score:7
6. SWEAT attempts:9 score:9
7. FOIST attempts:8 score:8
8. FILTH attempts:6 score:6

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1676 🥳 score:43 ⏱️ 0:08:25.937383

📜 10 sessions

Sedecordle Classic sedecordle.com

1. TRUST attempts:11 score:1
2. NERDY attempts:3 score:1
3. SPOOK attempts:14 score:1
4. RUPEE attempts:5 score:4
5. HEFTY attempts:15 score:1
6. WRONG attempts:7 score:5
7. SKULK attempts:16 score:1
8. KOALA attempts:17 score:6
9. SNARL attempts:18 score:1
10. WAIST attempts:8 score:8
11. SIEVE attempts:9 score:0
12. SCAMP attempts:19 score:9
13. TASTY attempts:12 score:1
14. TEDDY attempts:10 score:2
15. MUSTY attempts:20 score:2
16. MARRY attempts:20 score:0

# [squareword.org](squareword.org) 🧩 #1689 🥳 7 ⏱️ 0:02:11.832542

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟨 🟨 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S M O T E
    M O U R N
    A L T A R
    R A D I O
    T R O L L

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1626 🥳 331 ⏱️ 2:39:45.352492

🤔 332 attempts
📜 2 sessions
🫧 22 chat sessions
⁉️ 118 chat prompts
🤖 21 llama3.2:latest replies
🤖 8 dolphin3:latest replies
🤖 89 gemma4:12b replies
🔥   1 🥵  10 😎  34 🥶 270 🧊  16

      $1 #332 partial             100.00°C 🥳 1000‰ ~316 used:0  [315]  source:llama3.2
      $2 #191 gradual              37.02°C 🔥  994‰   ~7 used:84 [6]    source:gemma4  
      $3 #290 substantial          34.54°C 🥵  988‰   ~6 used:5  [5]    source:llama3.2
      $4 #310 modest               33.93°C 🥵  986‰   ~3 used:2  [2]    source:llama3.2
      $5 #145 proportional         33.11°C 🥵  982‰  ~39 used:46 [38]   source:gemma4  
      $6 #311 slight               32.69°C 🥵  980‰   ~1 used:1  [0]    source:llama3.2
      $7 #284 limited              31.78°C 🥵  972‰   ~4 used:2  [3]    source:llama3.2
      $8 #193 simultaneous         29.71°C 🥵  942‰  ~34 used:16 [33]   source:gemma4  
      $9 #192 probable             28.87°C 🥵  919‰  ~32 used:11 [31]   source:gemma4  
     $10 #222 delayed              28.82°C 🥵  916‰  ~33 used:11 [32]   source:gemma4  
     $11 #302 large                28.80°C 🥵  914‰   ~2 used:0  [1]    source:llama3.2
     $13 #149 proportionate        27.79°C 😎  887‰  ~40 used:6  [39]   source:gemma4  
     $47 #158 scaled               21.03°C 🥶        ~50 used:0  [49]   source:gemma4  
    $317   #4 marmalade            -0.20°C 🧊       ~317 used:0  [316]  source:gemma4  

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1659 🥳 276 ⏱️ 0:23:07.340894

🤔 277 attempts
📜 1 sessions
🫧 17 chat sessions
⁉️ 91 chat prompts
🤖 91 gemma4:12b replies
🥵   1 😎  17 🥶 226 🧊  32

      $1 #277 carré           100.00°C 🥳 1000‰ ~245 used:0  [244]  source:gemma4
      $2 #274 angle            35.24°C 🥵  949‰   ~1 used:2  [0]    source:gemma4
      $3 #269 symétrie         30.49°C 😎  868‰   ~3 used:5  [2]    source:gemma4
      $4 #242 pointillé        30.42°C 😎  866‰  ~14 used:18 [13]   source:gemma4
      $5  #38 couleur          28.42°C 😎  807‰  ~18 used:75 [17]   source:gemma4
      $6 #273 géométrie        28.36°C 😎  802‰   ~2 used:2  [1]    source:gemma4
      $7 #226 aplat            27.48°C 😎  775‰   ~6 used:13 [5]    source:gemma4
      $8 #197 hachure          26.99°C 😎  758‰  ~17 used:20 [16]   source:gemma4
      $9 #238 bicolore         24.49°C 😎  613‰   ~4 used:11 [3]    source:gemma4
     $10 #166 surface          24.42°C 😎  608‰  ~15 used:18 [14]   source:gemma4
     $11 #145 épaisseur        24.27°C 😎  586‰  ~12 used:14 [11]   source:gemma4
     $12 #237 monochrome       23.09°C 😎  484‰   ~5 used:11 [4]    source:gemma4
     $20 #254 camaïeu          20.05°C 🥶        ~23 used:0  [22]   source:gemma4
    $246 #155 relevé           -0.29°C 🧊       ~246 used:0  [245]  source:gemma4
