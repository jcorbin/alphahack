# 2026-09-27

- 🔗 spaceword.org 🧩 2026-09-26 🏁 score 2172 ranked 15.1% 50/331 ⏱️ 1:06:40.901845
- 🔗 wordgrid 🧩 #848 🟪 rarity:0.28 ⏱️ 0:02:30.863250
- 🔗 alfagok.diginaut.net 🧩 #694 🥳 38 ⏱️ 0:00:53.448008
- 🔗 alphaguess.com 🧩 #1161 🥳 34 ⏱️ 0:00:44.213403
- 🔗 dontwordle.com 🧩 #1587 🥳 6 ⏱️ 0:01:22.622342
- 🔗 dictionary.com hurdle 🧩 #1730 🥳 17 ⏱️ 0:02:36.969978
- 🔗 Quordle Classic 🧩 #1707 🥳 score:24 ⏱️ 0:02:07.568525
- 🔗 Octordle Classic 🧩 #1707 🥳 score:57 ⏱️ 0:02:08.057391
- 🔗 Sedecordle Classic 🧩 #1687 🥳 score:44 ⏱️ 0:04:30.229072
- 🔗 squareword.org 🧩 #1700 🥳 9 ⏱️ 0:03:16.265343
- 🔗 cemantle.certitudes.org 🧩 #1637 🥳 437 ⏱️ 0:08:17.078807
- 🔗 cemantix.certitudes.org 🧩 #1670 🥳 281 ⏱️ 7:18:40.701520

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







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #848 🟪 rarity:0.28 ⏱️ 0:02:30.863250

📜 2 sessions
🌌 🌌 🌌
🦄 🦄 🦄
🦄 🦄 🦄
Rarity: 0.28 🟪

# [spaceword.org](spaceword.org) 🧩 2026-09-26 🏁 score 2172 ranked 15.1% 50/331 ⏱️ 1:06:40.901845

📜 4 sessions
- tiles: 21/21
- score: 2172 bonus: +72
- rank: 50/331

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ S I K E R _ B _   
      _ _ O _ O _ O U R _   
      _ _ U _ J _ V _ A _   
      _ _ _ R I F E L Y _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #694 🥳 38 ⏱️ 0:00:53.448008

🤔 38 attempts
📜 1 sessions

    @        [     0] &-teken             
    @+199528 [199528] lij                 q0  ? ␅
    @+199528 [199528] lij                 q1  ? after
    @+199528 [199528] lij                 q2  ? ␅
    @+199528 [199528] lij                 q3  ? after
    @+299482 [299482] schrok              q4  ? ␅
    @+299482 [299482] schrok              q5  ? after
    @+349467 [349467] vakanties           q6  ? ␅
    @+349467 [349467] vakanties           q7  ? after
    @+349467 [349467] vakanties           q8  ? ␅
    @+349467 [349467] vakanties           q9  ? after
    @+361906 [361906] vervolg             q12 ? ␅
    @+361906 [361906] vervolg             q13 ? after
    @+361929 [361929] vervolgconferenties q30 ? ␅
    @+361929 [361929] vervolgconferenties q31 ? after
    @+361937 [361937] vervolgde           q32 ? ␅
    @+361937 [361937] vervolgde           q33 ? after
    @+361942 [361942] vervolgen           q36 ? ␅
    @+361942 [361942] vervolgen           q37 ? it
    @+361942 [361942] vervolgen           done. it
    @+361950 [361950] vervolgfilm         q28 ? ␅
    @+361950 [361950] vervolgfilm         q29 ? before
    @+361994 [361994] vervolgseries       q26 ? ␅
    @+361994 [361994] vervolgseries       q27 ? before
    @+362083 [362083] vervroeg            q24 ? ␅
    @+362083 [362083] vervroeg            q25 ? before
    @+362274 [362274] verwater            q22 ? ␅
    @+362274 [362274] verwater            q23 ? before
    @+362653 [362653] verwik              q20 ? ␅
    @+362653 [362653] verwik              q21 ? before
    @+363414 [363414] verzorg             q19 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1161 🥳 34 ⏱️ 0:00:44.213403

🤔 34 attempts
📜 2 sessions

    @        [     0] aa           
    @+98142  [ 98142] mac          q0  ? ␅
    @+98142  [ 98142] mac          q1  ? after
    @+122719 [122719] parol        q4  ? ␅
    @+122719 [122719] parol        q5  ? after
    @+134999 [134999] prop         q6  ? ␅
    @+134999 [134999] prop         q7  ? after
    @+135059 [135059] proper       q20 ? ␅
    @+135059 [135059] proper       q21 ? after
    @+135067 [135067] propers      q26 ? ␅
    @+135067 [135067] propers      q27 ? after
    @+135069 [135069] properties   q30 ? ␅
    @+135069 [135069] properties   q31 ? after
    @+135070 [135070] property     q32 ? ␅
    @+135070 [135070] property     q33 ? it
    @+135070 [135070] property     done. it
    @+135071 [135071] propertyless q28 ? ␅
    @+135071 [135071] propertyless q29 ? before
    @+135074 [135074] prophase     q24 ? ␅
    @+135074 [135074] prophase     q25 ? before
    @+135089 [135089] prophet      q22 ? ␅
    @+135089 [135089] prophet      q23 ? before
    @+135116 [135116] propitiator  q18 ? ␅
    @+135116 [135116] propitiator  q19 ? before
    @+135237 [135237] pros         q16 ? ␅
    @+135237 [135237] pros         q17 ? before
    @+135702 [135702] proven       q14 ? ␅
    @+135702 [135702] proven       q15 ? before
    @+136418 [136418] pul          q12 ? ␅
    @+136418 [136418] pul          q13 ? before
    @+138005 [138005] quetzal      q11 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1587 🥳 6 ⏱️ 0:01:22.622342

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:JEEZE n n n n n remain:6889
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:4093
    ⬜⬜⬜⬜⬜ tried:DODOS n n n n n remain:796
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:302
    ⬜⬜⬜⬜⬜ tried:GRUFF n n n n n remain:59
    ⬜⬜⬜🟩🟩 tried:CIVIC n n n Y Y remain:2

    Undos used: 2

      2 words remaining
    x 7 unused letters
    = 14 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1730 🥳 17 ⏱️ 0:02:36.969978

📜 1 sessions
💰 score: 9900

    4/6
    LYASE 🟨⬜🟨⬜🟩
    AGILE 🟨⬜⬜🟨🟩
    ULNAE 🟨🟨⬜🟨🟩
    VALUE 🟩🟩🟩🟩🟩
    2/6
    VALUE 🟨🟨🟨🟨⬜
    UVULA 🟩🟩🟩🟩🟩
    5/6
    UVULA ⬜⬜⬜⬜⬜
    OSIER ⬜⬜🟩⬜⬜
    THING ⬜🟩🟩🟩⬜
    CHINK ⬜🟩🟩🟩⬜
    WHINY 🟩🟩🟩🟩🟩
    4/6
    WHINY ⬜⬜⬜🟩⬜
    AEONS 🟨⬜⬜🟩🟨
    STANK 🟩🟩🟩🟩⬜
    STAND 🟩🟩🟩🟩🟩
    Final 2/2
    BUILD ⬜🟩🟩🟩🟩
    GUILD 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1707 🥳 score:24 ⏱️ 0:02:07.568525

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. VALET attempts:7 score:8
2. CHEST attempts:3 score:3
3. VIGIL attempts:7 score:7
4. PUREE attempts:6 score:6

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1707 🥳 score:57 ⏱️ 0:02:08.057391

📜 1 sessions

Octordle Classic

1. COUNT attempts:8 score:8
2. FIFTH attempts:9 score:9
3. GLAZE attempts:12 score:12
4. GAMMA attempts:4 score:4
5. STAMP attempts:3 score:3
6. RUSTY attempts:5 score:5
7. SLYLY attempts:10 score:10
8. SWAMI attempts:6 score:6

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1687 🥳 score:44 ⏱️ 0:04:30.229072

📜 2 sessions

Sedecordle Classic sedecordle.com

1. MISER attempts:9 score:0
2. RELAX attempts:8 score:9
3. MECCA attempts:10 score:1
4. SWIFT attempts:13 score:0
5. SNOWY attempts:7 score:0
6. GUILT attempts:12 score:7
7. CABIN attempts:5 score:0
8. CAPER attempts:3 score:5
9. PRUNE attempts:6 score:0
10. AGORA attempts:11 score:6
11. RECUT attempts:14 score:1
12. BAWDY attempts:15 score:4
13. DEVIL attempts:16 score:1
14. TONIC attempts:17 score:6
15. DONOR attempts:4 score:0
16. FEMME attempts:18 score:4

# [squareword.org](squareword.org) 🧩 #1700 🥳 9 ⏱️ 0:03:16.265343

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟩
    🟩 🟨 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟨 🟨 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    G R A F T
    R O G E R
    A G A T E
    P U P A E
    H E E L S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1637 🥳 437 ⏱️ 0:08:17.078807

🤔 438 attempts
📜 1 sessions
🫧 38 chat sessions
⁉️ 120 chat prompts
🤖 7 ornith-1.5:35b replies
🤖 9 dolphin3:latest replies
🤖 42 gemma4:31b-cloud replies
🤖 12 nemotron-3-super:cloud replies
🤖 49 nemotron-3-nano:30b-cloud replies
🔥   3 🥵  10 😎  62 🥶 346 🧊  16

      $1 #438 react            100.00°C 🥳 1000‰ ~422 used:0   [421]  source:ornith          
      $2  #61 reaction          52.63°C 🔥  996‰  ~70 used:120 [69]   source:nemotron-3-nano 
      $3 #345 adapt             51.96°C 🔥  995‰   ~2 used:38  [1]    source:gemma4          
      $4 #346 adjust            48.70°C 🔥  994‰   ~1 used:35  [0]    source:gemma4          
      $5 #112 perturb           41.18°C 🥵  981‰  ~72 used:25  [71]   source:nemotron-3-nano 
      $6 #140 response          40.41°C 🥵  978‰  ~71 used:13  [70]   source:nemotron-3-nano 
      $7 #217 flinch            39.14°C 🥵  970‰  ~10 used:8   [9]    source:nemotron-3-super
      $8 #150 act               38.07°C 🥵  962‰   ~3 used:7   [2]    source:nemotron-3-nano 
      $9 #287 activate          35.96°C 🥵  937‰   ~4 used:7   [3]    source:gemma4          
     $10 #139 recoil            35.40°C 🥵  924‰   ~5 used:7   [4]    source:nemotron-3-nano 
     $11 #162 evolve            34.85°C 🥵  910‰   ~7 used:7   [6]    source:nemotron-3-nano 
     $15 #344 disconcert        34.16°C 😎  897‰  ~11 used:0   [10]   source:gemma4          
     $77 #352 grow              24.76°C 🥶        ~80 used:0   [79]   source:gemma4          
    $423 #312 fulfillment       -0.10°C 🧊       ~423 used:0   [422]  source:gemma4          

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1670 🥳 281 ⏱️ 7:18:40.701520

🤔 282 attempts
📜 2 sessions
🫧 21 chat sessions
⁉️ 115 chat prompts
🤖 5 dolphin3:latest replies
🤖 110 gemma4:12b replies
😱   1 🔥   6 🥵  21 😎  62 🥶 155 🧊  36

      $1 #282 célébrer         100.00°C 🥳 1000‰ ~246 used:0  [245]  source:dolphin3
      $2 #180 célébration       73.02°C 😱  999‰   ~1 used:90 [0]    source:gemma4  
      $3 #176 fête              56.49°C 🔥  996‰  ~26 used:35 [25]   source:gemma4  
      $4 #198 anniversaire      55.43°C 🔥  995‰  ~25 used:14 [24]   source:gemma4  
      $5 #193 commémoration     53.55°C 🔥  994‰   ~4 used:10 [3]    source:gemma4  
      $6 #200 festivité         53.22°C 🔥  993‰   ~5 used:10 [4]    source:gemma4  
      $7 #158 solennité         51.50°C 🔥  992‰   ~2 used:9  [1]    source:gemma4  
      $8 #174 cérémonie         51.18°C 🔥  991‰   ~3 used:9  [2]    source:gemma4  
      $9 #210 jubilé            47.51°C 🥵  987‰   ~6 used:0  [5]    source:gemma4  
     $10  #36 solennel          47.06°C 🥵  986‰  ~88 used:56 [87]   source:gemma4  
     $11 #195 réjouissance      44.11°C 🥵  981‰   ~7 used:0  [6]    source:gemma4  
     $30 #212 pèlerinage        33.81°C 😎  897‰  ~27 used:0  [26]   source:gemma4  
     $92 #155 prestige          20.14°C 🥶        ~94 used:0  [93]   source:gemma4  
    $247  #34 patrimonial       -0.14°C 🧊       ~247 used:0  [246]  source:gemma4  
