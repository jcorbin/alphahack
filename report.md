# 2026-09-10

- 🔗 spaceword.org 🧩 2026-09-09 🏁 score 2170 ranked 26.2% 98/374 ⏱️ 0:14:19.932154
- 🔗 wordgrid 🧩 #831 🟪 rarity:0.4 ⏱️ 0:02:57.155318
- 🔗 alfagok.diginaut.net 🧩 #677 🥳 42 ⏱️ 0:00:42.546974
- 🔗 alphaguess.com 🧩 #1144 🥳 32 ⏱️ 0:00:33.272833
- 🔗 dontwordle.com 🧩 #1570 🥳 6 ⏱️ 0:01:15.483196
- 🔗 dictionary.com hurdle 🧩 #1713 😦 16 ⏱️ 0:02:55.293401
- 🔗 Quordle Classic 🧩 #1690 🥳 score:21 ⏱️ 0:01:22.229076
- 🔗 Octordle Classic 🧩 #1690 🥳 score:61 ⏱️ 0:02:11.556009
- 🔗 Sedecordle Classic 🧩 #1670 🥳 score:46 ⏱️ 0:02:18.557921
- 🔗 squareword.org 🧩 #1683 🥳 7 ⏱️ 0:01:44.897521
- 🔗 cemantle.certitudes.org 🧩 #1620 🥳 160 ⏱️ 0:22:23.643496
- 🔗 cemantix.certitudes.org 🧩 #1653 🥳 476 ⏱️ 2:07:02.930066

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



# [spaceword.org](spaceword.org) 🧩 2026-09-09 🏁 score 2170 ranked 26.2% 98/374 ⏱️ 0:14:19.932154

📜 4 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 98/374

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ L _ J _ E _ _   
      _ _ _ I _ A I N _ _   
      _ _ _ K _ E _ Z _ _   
      _ _ _ E _ G O Y _ _   
      _ _ _ R U E _ M _ _   
      _ _ _ S _ R _ E _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #831 🟪 rarity:0.4 ⏱️ 0:02:57.155318

📜 3 sessions
🦄 🌌 🌌
🌌 🌌 🌌
🌌 🌌 🌌
Rarity: 0.4 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #677 🥳 42 ⏱️ 0:00:42.546974

🤔 42 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+199640 [199640] lijk         q0  ? ␅
    @+199640 [199640] lijk         q1  ? after
    @+199640 [199640] lijk         q2  ? ␅
    @+199640 [199640] lijk         q3  ? after
    @+299544 [299544] schroot      q4  ? ␅
    @+299544 [299544] schroot      q5  ? after
    @+311832 [311832] spiert       q10 ? ␅
    @+311832 [311832] spiert       q11 ? after
    @+317926 [317926] stem         q12 ? ␅
    @+317926 [317926] stem         q13 ? after
    @+318282 [318282] steno        q20 ? ␅
    @+318282 [318282] steno        q21 ? after
    @+318439 [318439] sterf        q22 ? ␅
    @+318439 [318439] sterf        q23 ? after
    @+318497 [318497] sterilisator q28 ? ␅
    @+318497 [318497] sterilisator q29 ? after
    @+318500 [318500] steriliseer  q34 ? ␅
    @+318500 [318500] steriliseer  q35 ? after
    @+318506 [318506] steriliseert q36 ? ␅
    @+318506 [318506] steriliseert q37 ? after
    @+318509 [318509] steriliseren q38 ? ␅
    @+318509 [318509] steriliseren q39 ? after
    @+318515 [318515] sterk        q40 ? ␅
    @+318515 [318515] sterk        q41 ? it
    @+318515 [318515] sterk        done. it
    @+318518 [318518] sterke       q30 ? ␅
    @+318518 [318518] sterke       q31 ? vb
    @+318518 [318518] sterke       q32 ? ␅
    @+318518 [318518] sterke       q33 ? before
    @+318553 [318553] stern        q27 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1144 🥳 32 ⏱️ 0:00:33.272833

🤔 32 attempts
📜 1 sessions

    @        [     0] aa          
    @+98147  [ 98147] mac         q0  ? ␅
    @+98147  [ 98147] mac         q1  ? after
    @+98147  [ 98147] mac         q2  ? ␅
    @+98147  [ 98147] mac         q3  ? after
    @+122724 [122724] parol       q6  ? ␅
    @+122724 [122724] parol       q7  ? after
    @+122724 [122724] parol       q8  ? ␅
    @+122724 [122724] parol       q9  ? after
    @+122724 [122724] parol       q10 ? ␅
    @+122724 [122724] parol       q11 ? after
    @+135004 [135004] prop        q12 ? ␅
    @+135004 [135004] prop        q13 ? after
    @+136423 [136423] pul         q18 ? ␅
    @+136423 [136423] pul         q19 ? after
    @+136807 [136807] pur         q22 ? ␅
    @+136807 [136807] pur         q23 ? after
    @+136826 [136826] pure        q30 ? ␅
    @+136826 [136826] pure        q31 ? it
    @+136826 [136826] pure        done. it
    @+136851 [136851] purgatorial q28 ? ␅
    @+136851 [136851] purgatorial q29 ? before
    @+136894 [136894] purl        q26 ? ␅
    @+136894 [136894] purl        q27 ? before
    @+137009 [137009] push        q24 ? ␅
    @+137009 [137009] push        q25 ? before
    @+137217 [137217] pyjamas     q20 ? ␅
    @+137217 [137217] pyjamas     q21 ? before
    @+138010 [138010] quetzal     q16 ? ␅
    @+138010 [138010] quetzal     q17 ? before
    @+141017 [141017] recon       q15 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1570 🥳 6 ⏱️ 0:01:15.483196

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:WANNA n n n n n remain:5495
    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:2938
    ⬜⬜⬜⬜⬜ tried:MUMMY n n n n n remain:1165
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:353
    ⬜⬜⬜⬜🟩 tried:BOFFO n n n n Y remain:4
    ⬜🟩⬜⬜🟩 tried:DEKKO n Y n n Y remain:3

    Undos used: 3

      3 words remaining
    x 8 unused letters
    = 24 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1713 😦 16 ⏱️ 0:02:55.293401

📜 1 sessions
💰 score: 5080

    3/6
    ROAST ⬜⬜🟩⬜🟩
    LEANT 🟨🟨🟩⬜🟩
    EXALT 🟩🟩🟩🟩🟩
    4/6
    EXALT 🟨⬜🟨⬜⬜
    SANER 🟩🟨⬜🟨🟩
    SEWAR 🟩🟨⬜🟩🟩
    SHEAR 🟩🟩🟩🟩🟩
    3/6
    SHEAR ⬜🟨⬜⬜⬜
    OUGHT 🟨⬜⬜🟨🟨
    BOTCH 🟩🟩🟩🟩🟩
    4/6
    BOTCH ⬜⬜⬜🟩🟩
    RANCH ⬜⬜⬜🟩🟩
    MULCH ⬜🟩🟩🟩🟩
    GULCH 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜⬜🟩⬜⬜
    ????? 🟩🟩🟩⬜🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1690 🥳 score:21 ⏱️ 0:01:22.229076

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. AGENT attempts:7 score:7
2. EXILE attempts:6 score:6
3. TITAN attempts:5 score:5
4. RUPEE attempts:3 score:3

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1690 🥳 score:61 ⏱️ 0:02:11.556009

📜 1 sessions

Octordle Classic

1. HILLY attempts:12 score:12
2. SWARM attempts:9 score:9
3. BLARE attempts:6 score:6
4. FUSSY attempts:11 score:11
5. BLUER attempts:5 score:5
6. BLOCK attempts:7 score:7
7. CANNY attempts:3 score:3
8. POINT attempts:8 score:8

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1670 🥳 score:46 ⏱️ 0:02:18.557921

📜 1 sessions

Sedecordle Classic sedecordle.com

1. KINKY attempts:19 score:1
2. GNOME attempts:4 score:9
3. TATTY attempts:11 score:1
4. SHEEN attempts:13 score:1
5. DREAM attempts:6 score:0
6. BLOOM attempts:5 score:6
7. SNARL attempts:3 score:0
8. MEDIA attempts:7 score:3
9. WOMAN attempts:8 score:0
10. PLANK attempts:19 score:8
11. DILLY attempts:9 score:0
12. PRIME attempts:15 score:9
13. CARRY attempts:16 score:1
14. FRANK attempts:17 score:6
15. TALON attempts:10 score:1
16. PAPAL attempts:18 score:0

# [squareword.org](squareword.org) 🧩 #1683 🥳 7 ⏱️ 0:01:44.897521

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟨 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P O L L S
    O P I U M
    R E T R O
    C R E E K
    H A R D Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1620 🥳 160 ⏱️ 0:22:23.643496

🤔 161 attempts
📜 1 sessions
🫧 13 chat sessions
⁉️ 68 chat prompts
🤖 31 ornith-1.5:35b replies
🤖 37 dolphin3:latest replies
🔥   1 🥵   5 😎  23 🥶 122 🧊   9

      $1 #161 architect        100.00°C 🥳 1000‰ ~152 used:0  [151]  source:ornith  
      $2 #121 builder           50.24°C 🔥  994‰   ~3 used:11 [2]    source:ornith  
      $3 #100 contractor        43.91°C 🥵  982‰  ~23 used:13 [22]   source:ornith  
      $4 #122 mason             38.82°C 🥵  958‰   ~4 used:4  [3]    source:ornith  
      $5  #89 renovation        37.85°C 🥵  945‰  ~24 used:16 [23]   source:ornith  
      $6 #125 electrician       37.34°C 🥵  939‰   ~1 used:1  [0]    source:ornith  
      $7 #141 bricklayer        35.25°C 🥵  900‰   ~2 used:1  [1]    source:ornith  
      $8 #129 plumber           33.66°C 😎  867‰   ~5 used:0  [4]    source:ornith  
      $9  #98 remodel           33.36°C 😎  854‰  ~26 used:4  [25]   source:ornith  
     $10 #146 facade            32.81°C 😎  837‰   ~6 used:0  [5]    source:ornith  
     $11 #148 masonry           32.19°C 😎  816‰   ~7 used:0  [6]    source:ornith  
     $12  #96 construction      32.11°C 😎  812‰  ~25 used:2  [24]   source:ornith  
     $31 #127 foundation        22.81°C 🥶        ~41 used:0  [40]   source:ornith  
    $153  #77 over              -0.03°C 🧊       ~153 used:0  [152]  source:ornith  

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1653 🥳 476 ⏱️ 2:07:02.930066

🤔 477 attempts
📜 1 sessions
🫧 93 chat sessions
⁉️ 287 chat prompts
🤖 185 ornith-1.5:35b replies
🤖 102 dolphin3:latest replies
🥵  15 😎  70 🥶 303 🧊  88

      $1 #477 teneur            100.00°C 🥳 1000‰ ~389 used:0   [388]  source:ornith  
      $2 #295 concentration      42.00°C 🥵  986‰  ~81 used:103 [80]   source:ornith  
      $3 #367 turbidité          41.46°C 🥵  981‰  ~66 used:22  [65]   source:ornith  
      $4 #431 quantité           40.62°C 🥵  975‰   ~2 used:6   [1]    source:ornith  
      $5  #95 malique            39.95°C 🥵  972‰  ~84 used:130 [83]   source:dolphin3
      $6 #366 salinité           39.46°C 🥵  968‰   ~3 used:6   [2]    source:ornith  
      $7  #67 saccharose         38.99°C 🥵  961‰  ~79 used:60  [78]   source:dolphin3
      $8 #389 proportion         38.04°C 🥵  946‰   ~4 used:6   [3]    source:ornith  
      $9  #88 acidité            37.62°C 🥵  938‰  ~67 used:22  [66]   source:dolphin3
     $10 #403 échantillonnage    37.53°C 🥵  937‰   ~5 used:6   [4]    source:ornith  
     $11 #399 échantillon        37.22°C 🥵  932‰   ~6 used:6   [5]    source:ornith  
     $17 #443 conductivité       36.06°C 😎  898‰   ~9 used:0   [8]    source:ornith  
     $86 #432 gramme             25.47°C 🥶        ~37 used:0   [36]   source:ornith  
    $390  #20 brioche            -0.03°C 🧊       ~390 used:0   [389]  source:dolphin3
