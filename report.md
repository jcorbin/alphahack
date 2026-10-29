# 2026-10-30

- 🔗 wordgrid 🧩 #881 🟪 rarity:0.18 ⏱️ 0:03:23.796461
- 🔗 spaceword.org 🧩 2026-10-29 🏁 score 2173 ranked 6.8% 22/323 ⏱️ 0:21:19.828100
- 🔗 alfagok.diginaut.net 🧩 #727 🥳 24 ⏱️ 0:00:32.169118
- 🔗 alphaguess.com 🧩 #1194 🥳 36 ⏱️ 0:00:43.075713
- 🔗 dontwordle.com 🧩 #1620 🥳 6 ⏱️ 0:01:09.111580
- 🔗 dictionary.com hurdle 🧩 #1763 😦 16 ⏱️ 0:02:53.221092
- 🔗 Quordle Classic 🧩 #1740 🥳 score:20 ⏱️ 0:01:18.448148
- 🔗 Octordle Classic 🧩 #1740 🥳 score:58 ⏱️ 0:01:56.806505
- 🔗 Sedecordle Classic 🧩 #1720 🥳 score:37 ⏱️ 0:03:15.118869
- 🔗 squareword.org 🧩 #1733 🥳 8 ⏱️ 0:02:11.543839
- 🔗 cemantle.certitudes.org 🧩 #1670 🥳 1295 ⏱️ 2:59:43.016226
- 🔗 cemantix.certitudes.org 🧩 #1703 😦 1146 ⏱️ 2:09:22.856422

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
























# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 2026-10-27 🤔 rarity:nan ⏱️ 0:01:43.563056

📜 1 sessions
🌌 🌌 🦄
🌌 🌌 🌌
🦄 🦄 🦄



# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #881 🟪 rarity:0.18 ⏱️ 0:03:23.796461

📜 2 sessions
🦄 🦄 🦄
🌌 🦄 🦄
🌌 🌌 🦄
Rarity: 0.18 🟪

# [spaceword.org](spaceword.org) 🧩 2026-10-29 🏁 score 2173 ranked 6.8% 22/323 ⏱️ 0:21:19.828100

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 22/323

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ O H _ _ W _ S I C   
      _ _ A Q U A T O N E   
      _ _ J I T N E Y _ E   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #727 🥳 24 ⏱️ 0:00:32.169118

🤔 24 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+199631 [199631] lijk       q0  ? ␅
    @+199631 [199631] lijk       q1  ? after
    @+299528 [299528] schroot    q2  ? ␅
    @+299528 [299528] schroot    q3  ? after
    @+311814 [311814] spiert     q8  ? ␅
    @+311814 [311814] spiert     q9  ? after
    @+317908 [317908] stem       q10 ? ␅
    @+317908 [317908] stem       q11 ? after
    @+318264 [318264] steno      q18 ? ␅
    @+318264 [318264] steno      q19 ? after
    @+318339 [318339] ster       q22 ? ␅
    @+318339 [318339] ster       q23 ? it
    @+318339 [318339] ster       done. it
    @+318421 [318421] sterf      q20 ? ␅
    @+318421 [318421] sterf      q21 ? before
    @+318645 [318645] sterven    q16 ? ␅
    @+318645 [318645] sterven    q17 ? before
    @+319394 [319394] stimulator q14 ? ␅
    @+319394 [319394] stimulator q15 ? before
    @+320881 [320881] straat     q12 ? ␅
    @+320881 [320881] straat     q13 ? before
    @+324110 [324110] sub        q6  ? ␅
    @+324110 [324110] sub        q7  ? before
    @+349310 [349310] vakantie   q4  ? ␅
    @+349310 [349310] vakantie   q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1194 🥳 36 ⏱️ 0:00:43.075713

🤔 36 attempts
📜 1 sessions

    @       [    0] aa           
    @+49066 [49066] disturb      q2  ? ␅
    @+49066 [49066] disturb      q3  ? la
    @+49066 [49066] disturb      q4  ? ␅
    @+49066 [49066] disturb      q5  ? after
    @+54908 [54908] end          q10 ? ␅
    @+54908 [54908] end          q11 ? after
    @+55270 [55270] enfilade     q18 ? ␅
    @+55270 [55270] enfilade     q19 ? after
    @+55446 [55446] enjoin       q20 ? ␅
    @+55446 [55446] enjoin       q21 ? after
    @+55539 [55539] enoki        q22 ? ␅
    @+55539 [55539] enoki        q23 ? after
    @+55560 [55560] enormous     q26 ? ␅
    @+55560 [55560] enormous     q27 ? after
    @+55564 [55564] enosis       q32 ? ␅
    @+55564 [55564] enosis       q33 ? after
    @+55566 [55566] enough       q34 ? ␅
    @+55566 [55566] enough       q35 ? it
    @+55566 [55566] enough       done. it
    @+55568 [55568] enounce      q30 ? ␅
    @+55568 [55568] enounce      q31 ? before
    @+55574 [55574] enplane      q28 ? ␅
    @+55574 [55574] enplane      q29 ? before
    @+55586 [55586] enrage       q24 ? ␅
    @+55586 [55586] enrage       q25 ? before
    @+55636 [55636] ens          q16 ? ␅
    @+55636 [55636] ens          q17 ? before
    @+56509 [56509] epiphenomena q14 ? ␅
    @+56509 [56509] epiphenomena q15 ? before
    @+58109 [58109] evangel      q13 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1620 🥳 6 ⏱️ 0:01:09.111580

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:AYAYA n n n n n remain:6270
    ⬜⬜⬜⬜⬜ tried:BUBUS n n n n n remain:1917
    ⬜⬜⬜⬜⬜ tried:ZIZIT n n n n n remain:685
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:195
    ⬜⬜🟨⬜⬜ tried:CHOCK n n m n n remain:40
    ⬜⬜🟩🟩🟩 tried:JOMON n n Y Y Y remain:1

    Undos used: 2

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1763 😦 16 ⏱️ 0:02:53.221092

📜 2 sessions
💰 score: 5080

    3/6
    TASER 🟨🟨⬜⬜⬜
    ALTHO 🟩⬜🟨⬜🟨
    ABOUT 🟩🟩🟩🟩🟩
    4/6
    ABOUT 🟩⬜⬜⬜⬜
    AGILE 🟩⬜🟩🟨🟩
    KNAVE ⬜⬜🟨🟩🟩
    ALIVE 🟩🟩🟩🟩🟩
    2/6
    ALIVE ⬜⬜🟩🟨🟩
    VOICE 🟩🟩🟩🟩🟩
    5/6
    VOICE ⬜⬜🟨🟩⬜
    BITCH ⬜🟩🟩🟩🟩
    FADGE ⬜⬜⬜⬜⬜
    WHAPS ⬜🟨⬜⬜⬜
    HITCH 🟩🟩🟩🟩🟩
    Final 2/2
    ????? 🟩⬜⬜🟩🟩
    ????? 🟩⬜🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1740 🥳 score:20 ⏱️ 0:01:18.448148

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. ULCER attempts:7 score:7
2. DIMLY attempts:6 score:6
3. BRAIN attempts:4 score:4
4. BEGUN attempts:3 score:3

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1740 🥳 score:58 ⏱️ 0:01:56.806505

📜 1 sessions

Octordle Classic

1. POUCH attempts:10 score:10
2. CROOK attempts:7 score:7
3. LINER attempts:6 score:6
4. SENSE attempts:10 score:11
5. DECOY attempts:4 score:4
6. ROAST attempts:3 score:3
7. NOOSE attempts:8 score:8
8. STIFF attempts:9 score:9

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1720 🥳 score:37 ⏱️ 0:03:15.118869

📜 1 sessions

Sedecordle Classic sedecordle.com

1. YIELD attempts:18 score:1
2. GIRLY attempts:8 score:8
3. FLUKE attempts:15 score:1
4. EVADE attempts:5 score:5
5. BAYOU attempts:13 score:1
6. CRASH attempts:7 score:3
7. CASTE attempts:11 score:1
8. REPLY attempts:17 score:1
9. SHADY attempts:2 score:0
10. CLOAK attempts:10 score:2
11. AROMA attempts:12 score:1
12. OCTET attempts:9 score:2
13. TORSO attempts:14 score:1
14. SENSE attempts:18 score:4
15. HONEY attempts:6 score:0
16. QUEST attempts:16 score:6

# [squareword.org](squareword.org) 🧩 #1733 🥳 8 ⏱️ 0:02:11.543839

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟩
    🟨 🟨 🟨 🟨 🟩
    🟨 🟨 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C O U R T
    R I S E R
    A L I V E
    V E N U E
    E D G E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1670 🥳 1295 ⏱️ 2:59:43.016226

🤔 1296 attempts
📜 2 sessions
🫧 72 chat sessions
⁉️ 383 chat prompts
🤖 43 nemotron-3-nano:30b-cloud replies
🤖 32 dolphin3:latest replies
🤖 18 qwen3.8:latest replies
🤖 21 gemma4:31b replies
🤖 75 ornith-1.5:35b replies
🤖 3 flint:latest replies
🤖 22 gemma4:12b replies
🤖 170 llama3.2:latest replies
🔥    5 🥵   29 😎  120 🥶 1080 🧊   61

       $1 #1296 besides             100.00°C 🥳 1000‰ ~1235 used:0   [1234]  source:nemotron  
       $2 #1217 other                47.91°C 🔥  998‰   ~17 used:31  [16]    source:nemotron  
       $3  #204 like                 44.28°C 🔥  997‰  ~150 used:341 [149]   source:llama3.2  
       $4  #680 preclude             38.76°C 🔥  993‰   ~69 used:194 [68]    source:llama3.2  
       $5 #1284 instead              38.45°C 🔥  992‰    ~1 used:5   [0]     source:nemotron  
       $6 #1107 none                 38.39°C 🔥  991‰   ~18 used:36  [17]    source:qwen3.8   
       $7 #1246 thus                 37.93°C 🥵  989‰    ~3 used:2   [2]     source:nemotron  
       $8 #1260 anyhow               37.49°C 🥵  986‰    ~4 used:2   [3]     source:nemotron  
       $9 #1239 such                 36.89°C 🥵  982‰    ~5 used:2   [4]     source:nemotron  
      $10 #1242 hence                36.39°C 🥵  979‰    ~6 used:2   [5]     source:nemotron  
      $11 #1227 one                  35.23°C 🥵  976‰    ~7 used:2   [6]     source:nemotron  
      $36  #569 overlook             30.36°C 😎  896‰   ~70 used:2   [69]    source:llama3.2  
     $156  #395 abhor                21.52°C 🥶        ~163 used:0   [162]   source:llama3.2  
    $1236  #108 spellbinding         -0.05°C 🧊       ~1236 used:0   [1235]  source:llama3.2  

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1703 😦 1146 ⏱️ 2:09:22.856422

🤔 1145 attempts
📜 1 sessions
🫧 139 chat sessions
⁉️ 771 chat prompts
🤖 21 qwen3.8:latest replies
🤖 56 dolphin3:latest replies
🤖 639 nemotron-3-nano:30b-cloud replies
🤖 55 gemma4:12b replies
😦 😱    1 🔥    9 🥵   48 😎  220 🥶  549 🧊  318

       $1  #102 recrutement          74.86°C 😱  999‰   ~50 used:724 [49]    source:gemma4  
       $2  #474 embaucher            63.43°C 🔥  998‰  ~278 used:331 [277]   source:nemotron
       $3  #100 poste                53.81°C 🔥  997‰  ~276 used:186 [275]   source:gemma4  
       $4  #345 postuler             51.93°C 🔥  996‰   ~43 used:71  [42]    source:nemotron
       $5  #136 emploi               50.22°C 🔥  995‰   ~44 used:71  [43]    source:gemma4  
       $6  #112 embauche             49.68°C 🔥  994‰   ~45 used:71  [44]    source:gemma4  
       $7  #425 pourvoir             46.94°C 🔥  993‰   ~46 used:71  [45]    source:nemotron
       $8  #318 ingénieur            46.84°C 🔥  992‰   ~47 used:71  [46]    source:nemotron
       $9  #611 diplômé              46.74°C 🔥  991‰   ~48 used:71  [47]    source:nemotron
      $10  #137 intérim              45.92°C 🔥  990‰   ~49 used:71  [48]    source:gemma4  
      $11   #92 collaborateur        44.84°C 🥵  989‰   ~51 used:8   [50]    source:gemma4  
      $59  #315 cadre                31.51°C 😎  896‰   ~57 used:0   [56]    source:nemotron
     $279  #394 accueil              16.40°C 🥶        ~275 used:0   [274]   source:nemotron
     $828   #40 capteur              -0.02°C 🧊        ~828 used:0   [827]   source:gemma4  
