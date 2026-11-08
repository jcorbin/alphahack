# 2026-11-09

- 🔗 spaceword.org 🧩 2026-11-08 🏁 score 2168 ranked 48.3% 139/288 ⏱️ 7:18:51.934160
- 🔗 wordgrid 🧩 #891 🟪 rarity:0.33 ⏱️ 0:02:58.794233
- 🔗 alfagok.diginaut.net 🧩 #737 🥳 28 ⏱️ 0:00:39.238307
- 🔗 alphaguess.com 🧩 #1204 🥳 34 ⏱️ 0:00:55.100531
- 🔗 dontwordle.com 🧩 #1630 🥳 6 ⏱️ 0:01:37.348312
- 🔗 dictionary.com hurdle 🧩 #1773 🥳 18 ⏱️ 0:02:30.747801
- 🔗 Quordle Classic 🧩 #1750 🥳 score:22 ⏱️ 0:01:17.246350
- 🔗 Octordle Classic 🧩 #1750 🥳 score:64 ⏱️ 0:02:55.096482
- 🔗 Sedecordle Classic 🧩 #1730 🥳 score:49 ⏱️ 0:04:02.961962
- 🔗 squareword.org 🧩 #1743 🥳 7 ⏱️ 0:02:20.400583
- 🔗 cemantle.certitudes.org 🧩 #1680 🥳 140 ⏱️ 0:09:40.980047
- 🔗 cemantix.certitudes.org 🧩 #1713 🥳 153 ⏱️ 0:02:33.200535

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









# [spaceword.org](spaceword.org) 🧩 2026-11-08 🏁 score 2168 ranked 48.3% 139/288 ⏱️ 7:18:51.934160

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 139/288

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ O L E A _ _ _ _ _   
      _ H E _ _ Z _ _ P _   
      _ S E Q U I N _ Y _   
      _ _ _ I N T A K E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #891 🟪 rarity:0.33 ⏱️ 0:02:58.794233

📜 2 sessions
🌌 🌌 🌌
🌌 🦄 🦄
🌌 🌌 🦄
Rarity: 0.33 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #737 🥳 28 ⏱️ 0:00:39.238307

🤔 28 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+2      [     2] -cijferig 
    @+199631 [199631] lijk      q0  ? ␅
    @+199631 [199631] lijk      q1  ? after
    @+299522 [299522] schroot   q2  ? ␅
    @+299522 [299522] schroot   q3  ? after
    @+349304 [349304] vakantie  q4  ? ␅
    @+349304 [349304] vakantie  q5  ? after
    @+352868 [352868] ver       q8  ? ␅
    @+352868 [352868] ver       q9  ? after
    @+358161 [358161] verluiert q12 ? ␅
    @+358161 [358161] verluiert q13 ? after
    @+359312 [359312] verpot    q16 ? ␅
    @+359312 [359312] verpot    q17 ? after
    @+359623 [359623] vers      q18 ? ␅
    @+359623 [359623] vers      q19 ? after
    @+359716 [359716] verscheur q24 ? ␅
    @+359716 [359716] verscheur q25 ? after
    @+359758 [359758] verschil  q26 ? ␅
    @+359758 [359758] verschil  q27 ? it
    @+359758 [359758] verschil  done. it
    @+359821 [359821] verschot  q22 ? ␅
    @+359821 [359821] verschot  q23 ? before
    @+360023 [360023] verslag   q20 ? ␅
    @+360023 [360023] verslag   q21 ? before
    @+360473 [360473] verst     q14 ? ␅
    @+360473 [360473] verst     q15 ? before
    @+363453 [363453] verzout   q10 ? ␅
    @+363453 [363453] verzout   q11 ? before
    @+374038 [374038] vrij      q6  ? ␅
    @+374038 [374038] vrij      q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1204 🥳 34 ⏱️ 0:00:55.100531

🤔 34 attempts
📜 1 sessions

    @        [     0] aa          
    @+98139  [ 98139] mac         q0  ? ␅
    @+98139  [ 98139] mac         q1  ? after
    @+147300 [147300] rho         q2  ? ␅
    @+147300 [147300] rho         q3  ? after
    @+171900 [171900] tag         q4  ? ␅
    @+171900 [171900] tag         q5  ? after
    @+174386 [174386] test        q10 ? ␅
    @+174386 [174386] test        q11 ? after
    @+175598 [175598] thro        q12 ? ␅
    @+175598 [175598] thro        q13 ? after
    @+175903 [175903] ti          q14 ? ␅
    @+175903 [175903] ti          q15 ? after
    @+176406 [176406] tip         q16 ? ␅
    @+176406 [176406] tip         q17 ? after
    @+176633 [176633] to          q18 ? ␅
    @+176633 [176633] to          q19 ? after
    @+176765 [176765] tog         q20 ? ␅
    @+176765 [176765] tog         q21 ? after
    @+176772 [176772] togavirus   q28 ? ␅
    @+176772 [176772] togavirus   q29 ? after
    @+176773 [176773] togaviruses q32 ? ␅
    @+176773 [176773] togaviruses q33 ? it
    @+176773 [176773] togaviruses done. it
    @+176774 [176774] together    q30 ? ␅
    @+176774 [176774] together    q31 ? before
    @+176779 [176779] toggery     q26 ? ␅
    @+176779 [176779] toggery     q27 ? before
    @+176792 [176792] toil        q24 ? ␅
    @+176792 [176792] toil        q25 ? before
    @+176843 [176843] tola        q23 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1630 🥳 6 ⏱️ 0:01:37.348312

📜 1 sessions
💰 score: 32

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:NANNA n n n n n remain:5978
    ⬜⬜⬜⬜⬜ tried:KEEVE n n n n n remain:2382
    ⬜⬜⬜⬜⬜ tried:BOBOS n n n n n remain:401
    ⬜⬜⬜⬜⬜ tried:PUPPY n n n n n remain:100
    ⬜⬜⬜⬜🟨 tried:GRRRL n n n n m remain:21
    ⬜⬜🟨🟨⬜ tried:CHILD n n m m n remain:4

    Undos used: 3

      4 words remaining
    x 8 unused letters
    = 32 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1773 🥳 18 ⏱️ 0:02:30.747801

📜 1 sessions
💰 score: 9800

    3/6
    NARES ⬜🟩🟩🟨⬜
    BARGE ⬜🟩🟩⬜🟨
    EARTH 🟩🟩🟩🟩🟩
    5/6
    EARTH ⬜🟨⬜⬜⬜
    DIALS ⬜⬜🟩⬜🟨
    SPANK 🟩🟨🟩⬜⬜
    SWAMP 🟩⬜🟩⬜🟨
    SOAPY 🟩🟩🟩🟩🟩
    4/6
    SOAPY ⬜⬜🟨⬜⬜
    ALDER 🟨⬜⬜⬜⬜
    CABIN 🟨🟩⬜🟩🟨
    MANIC 🟩🟩🟩🟩🟩
    5/6
    MANIC ⬜⬜⬜⬜⬜
    PROST ⬜⬜🟩🟨🟨
    SLOTH 🟩⬜🟩🟨⬜
    STOKE 🟩🟩🟩⬜🟩
    STOVE 🟩🟩🟩🟩🟩
    Final 1/2
    SABLE 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1750 🥳 score:22 ⏱️ 0:01:17.246350

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. UNMET attempts:5 score:5
2. SINEW attempts:4 score:4
3. NADIR attempts:6 score:6
4. VOGUE attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1750 🥳 score:64 ⏱️ 0:02:55.096482

📜 1 sessions

Octordle Classic

1. FIELD attempts:5 score:5
2. TOTAL attempts:11 score:11
3. SNARL attempts:6 score:6
4. COMFY attempts:8 score:8
5. ABOUT attempts:12 score:12
6. JETTY attempts:10 score:10
7. PENAL attempts:9 score:9
8. RINSE attempts:3 score:3

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1730 🥳 score:49 ⏱️ 0:04:02.961962

📜 1 sessions

Sedecordle Classic sedecordle.com

1. LIEGE attempts:17 score:1
2. DECAL attempts:13 score:8
3. SALON attempts:17 score:1
4. CHANT attempts:17 score:7
5. MIMIC attempts:12 score:1
6. SHONE attempts:8 score:2
7. WREST attempts:16 score:1
8. DODGE attempts:3 score:6
9. SPLIT attempts:15 score:1
10. CYNIC attempts:6 score:5
11. OVERT attempts:9 score:0
12. DAILY attempts:4 score:9
13. LANKY attempts:14 score:1
14. SMOCK attempts:10 score:4
15. KNIFE attempts:11 score:1
16. EXTRA attempts:7 score:1

# [squareword.org](squareword.org) 🧩 #1743 🥳 7 ⏱️ 0:02:20.400583

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T A R S
    C A B I N
    A L O N E
    R O U S E
    E N T E R

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1680 🥳 140 ⏱️ 0:09:40.980047

🤔 141 attempts
📜 2 sessions
🫧 12 chat sessions
⁉️ 42 chat prompts
🤖 16 glm-5.3-flash:cloud replies
🤖 4 nemotron-3-nano:30b-cloud replies
🤖 20 gemma4:12b replies
😱   1 🥵   3 😎  15 🥶 115 🧊   6

      $1 #141 grab           100.00°C 🥳 1000‰ ~135 used:0  [134]  source:glm     
      $2 #137 snatch          68.94°C 😱  999‰   ~1 used:2  [0]    source:glm     
      $3  #60 snap            39.65°C 🥵  959‰  ~17 used:29 [16]   source:gemma4  
      $4 #125 slam            38.50°C 🥵  943‰   ~2 used:3  [1]    source:glm     
      $5  #93 smash           36.63°C 🥵  918‰   ~3 used:6  [2]    source:glm     
      $6 #109 pulverize       33.79°C 😎  840‰   ~4 used:0  [3]    source:glm     
      $7  #75 break           31.62°C 😎  768‰  ~18 used:4  [17]   source:gemma4  
      $8 #129 knock           30.90°C 😎  738‰   ~5 used:0  [4]    source:glm     
      $9  #36 quick           28.96°C 😎  643‰  ~19 used:11 [18]   source:gemma4  
     $10  #86 whip            28.62°C 😎  617‰   ~6 used:1  [5]    source:glm     
     $11 #130 smack           28.54°C 😎  607‰   ~7 used:0  [6]    source:glm     
     $12 #138 wham            26.89°C 😎  464‰   ~8 used:0  [7]    source:glm     
     $21 #134 whack           23.45°C 🥶        ~29 used:0  [28]   source:glm     
    $136  #61 abrupt          -0.29°C 🧊       ~136 used:0  [135]  source:gemma4  

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1713 🥳 153 ⏱️ 0:02:33.200535

🤔 154 attempts
📜 1 sessions
🫧 12 chat sessions
⁉️ 22 chat prompts
🤖 22 glm-5.3-flash:cloud replies
🔥  1 🥵  1 😎 28 🥶 89 🧊 34

      $1 #154 palais          100.00°C 🥳 1000‰ ~120 used:0  [119]  source:glm
      $2 #144 château          41.36°C 🔥  996‰   ~1 used:1  [0]    source:glm
      $3  #29 carrousel        36.55°C 🥵  970‰  ~30 used:21 [29]   source:glm
      $4 #115 jardin           30.72°C 😎  894‰  ~28 used:2  [27]   source:glm
      $5 #147 cérémonie        29.09°C 😎  856‰   ~2 used:0  [1]    source:glm
      $6 #128 statue           28.92°C 😎  847‰  ~29 used:2  [28]   source:glm
      $7 #132 roi              28.40°C 😎  826‰   ~3 used:1  [2]    source:glm
      $8 #149 monarque         28.15°C 😎  818‰   ~4 used:0  [3]    source:glm
      $9 #116 monument         27.87°C 😎  805‰   ~5 used:0  [4]    source:glm
     $10 #145 cour             27.56°C 😎  798‰   ~6 used:0  [5]    source:glm
     $11 #142 carrosse         27.18°C 😎  785‰   ~7 used:0  [6]    source:glm
     $12 #108 triomphe         27.17°C 😎  784‰   ~8 used:1  [7]    source:glm
     $32 #146 couronne         19.56°C 🥶        ~32 used:0  [31]   source:glm
    $121  #42 pesant           -0.02°C 🧊       ~121 used:0  [120]  source:glm
