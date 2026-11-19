# 2026-11-20

- 🔗 spaceword.org 🧩 2026-11-19 🏁 score 2168 ranked 49.7% 143/288 ⏱️ 2:27:57.491761
- 🔗 wordgrid 🧩 #902 🟪 rarity:0.27 ⏱️ 0:06:55.629272
- 🔗 alfagok.diginaut.net 🧩 #748 🥳 28 ⏱️ 0:00:47.898704
- 🔗 alphaguess.com 🧩 #1215 🥳 28 ⏱️ 0:00:37.922256
- 🔗 dontwordle.com 🧩 #1641 🥳 6 ⏱️ 0:01:30.954250
- 🔗 dictionary.com hurdle 🧩 #1784 😦 17 ⏱️ 0:03:38.407432
- 🔗 Quordle Classic 🧩 #1761 🥳 score:22 ⏱️ 0:01:42.721077
- 🔗 Octordle Classic 🧩 #1761 🥳 score:58 ⏱️ 0:01:59.574396
- 🔗 Sedecordle Classic 🧩 #1741 🥳 score:44 ⏱️ 0:03:27.747615
- 🔗 squareword.org 🧩 #1754 🥳 7 ⏱️ 0:02:21.520095
- 🔗 cemantle.certitudes.org 🧩 #1691 🥳 496 ⏱️ 0:03:23.228097
- 🔗 cemantix.certitudes.org 🧩 #1724 🥳 166 ⏱️ 0:00:55.507288

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










# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #892 🟪 rarity:0.32 ⏱️ 0:03:10.891631

📜 2 sessions
🌌 🦄 🦄
🌌 🌌 🌌
🦄 🌌 🌌
Rarity: 0.32 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-09 🏁 score 2168 ranked 49.8% 148/297 ⏱️ 0:22:41.164996

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 148/297

      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ G _ _ _ _ K _ L _
      _ O _ C A S A V A _
      _ A _ A _ _ S I G _
      _ D A W E N _ A _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _












# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #902 🟪 rarity:0.27 ⏱️ 0:06:55.629272

📜 2 sessions
🌌 🌌 🌌
🌌 🌌 🌌
🌌 🦄 🌌
Rarity: 0.27 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-19 🏁 score 2168 ranked 49.7% 143/288 ⏱️ 2:27:57.491761

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 143/288

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ V _ _ _ W _ O E _   
      _ A _ F E A S E S _   
      _ P _ _ _ N A _ T _   
      _ E Q U I T Y _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #748 🥳 28 ⏱️ 0:00:47.898704

🤔 28 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+2      [     2] -cijferig    
    @+99672  [ 99672] ex           q4  ? ␅
    @+99672  [ 99672] ex           q5  ? after
    @+149358 [149358] huis         q6  ? ␅
    @+149358 [149358] huis         q7  ? after
    @+174465 [174465] kind         q8  ? ␅
    @+174465 [174465] kind         q9  ? after
    @+187045 [187045] kronen       q10 ? ␅
    @+187045 [187045] kronen       q11 ? after
    @+190269 [190269] la           q12 ? ␅
    @+190269 [190269] la           q13 ? after
    @+190347 [190347] laag         q22 ? ␅
    @+190347 [190347] laag         q23 ? after
    @+190511 [190511] laan         q24 ? ␅
    @+190511 [190511] laan         q25 ? after
    @+190599 [190599] laatst       q26 ? ␅
    @+190599 [190599] laatst       q27 ? it
    @+190599 [190599] laatst       done. it
    @+190692 [190692] laboratorium q20 ? ␅
    @+190692 [190692] laboratorium q21 ? before
    @+191179 [191179] lam          q18 ? ␅
    @+191179 [191179] lam          q19 ? before
    @+192506 [192506] langs        q16 ? ␅
    @+192506 [192506] langs        q17 ? before
    @+194825 [194825] lees         q14 ? ␅
    @+194825 [194825] lees         q15 ? before
    @+199628 [199628] lijk         q0  ? ␅
    @+199628 [199628] lijk         q1  ? after
    @+199628 [199628] lijk         q2  ? ␅
    @+199628 [199628] lijk         q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1215 🥳 28 ⏱️ 0:00:37.922256

🤔 28 attempts
📜 1 sessions

    @       [    0] aa         
    @+2     [    2] aahed      
    @+24522 [24522] carabin    q4  ? ␅
    @+24522 [24522] carabin    q5  ? after
    @+30622 [30622] clitorides q8  ? ␅
    @+30622 [30622] clitorides q9  ? after
    @+31372 [31372] cock       q14 ? ␅
    @+31372 [31372] cock       q15 ? after
    @+31458 [31458] cocks      q20 ? ␅
    @+31458 [31458] cocks      q21 ? after
    @+31490 [31490] coco       q22 ? ␅
    @+31490 [31490] coco       q23 ? after
    @+31505 [31505] coconut    q26 ? ␅
    @+31505 [31505] coconut    q27 ? it
    @+31505 [31505] coconut    done. it
    @+31522 [31522] cocounsel  q24 ? ␅
    @+31522 [31522] cocounsel  q25 ? before
    @+31555 [31555] cod        q18 ? ␅
    @+31555 [31555] cod        q19 ? before
    @+31751 [31751] coenzyme   q16 ? ␅
    @+31751 [31751] coenzyme   q17 ? before
    @+32129 [32129] col        q12 ? ␅
    @+32129 [32129] col        q13 ? before
    @+33648 [33648] computer   q10 ? ␅
    @+33648 [33648] computer   q11 ? before
    @+36722 [36722] cos        q6  ? ␅
    @+36722 [36722] cos        q7  ? before
    @+49065 [49065] disturb    q2  ? ␅
    @+49065 [49065] disturb    q3  ? before
    @+98138 [98138] mac        q0  ? ␅
    @+98138 [98138] mac        q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1641 🥳 6 ⏱️ 0:01:30.954250

📜 1 sessions
💰 score: 25

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:PEWEE n n n n n remain:5634
    ⬜⬜⬜⬜⬜ tried:YOBBO n n n n n remain:2378
    ⬜⬜⬜⬜⬜ tried:JUGUM n n n n n remain:1037
    ⬜⬜🟨⬜⬜ tried:CHICK n n m n n remain:219
    ⬜⬜⬜🟩⬜ tried:DIXIT n n n Y n remain:24
    ⬜🟨⬜🟩⬜ tried:FAQIR n m n Y n remain:5

    Undos used: 3

      5 words remaining
    x 5 unused letters
    = 25 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1784 😦 17 ⏱️ 0:03:38.407432

📜 1 sessions
💰 score: 4940

    2/6
    AIDES 🟨⬜⬜🟨🟨
    HASTE 🟩🟩🟩🟩🟩
    5/6
    HASTE ⬜🟩⬜⬜⬜
    RAPID ⬜🟩⬜🟩⬜
    MALIC 🟩🟩⬜🟩⬜
    FAUVE 🟨🟩⬜⬜⬜
    MAFIA 🟩🟩🟩🟩🟩
    4/6
    MAFIA ⬜🟨⬜⬜🟨
    SPARE ⬜⬜🟨⬜🟨
    ABLED 🟩⬜⬜🟨🟩
    AHEAD 🟩🟩🟩🟩🟩
    4/6
    AHEAD ⬜⬜🟨⬜⬜
    OSIER ⬜⬜⬜🟨⬜
    LUNGE 🟩⬜⬜⬜🟨
    LEFTY 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜⬜⬜⬜⬜
    ????? ⬜🟩🟨⬜🟨

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1761 🥳 score:22 ⏱️ 0:01:42.721077

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. GRIEF attempts:6 score:6
2. MINOR attempts:4 score:4
3. ABUSE attempts:7 score:7
4. KEBAB attempts:5 score:5

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1761 🥳 score:58 ⏱️ 0:01:59.574396

📜 1 sessions

Octordle Classic

1. WOULD attempts:11 score:11
2. SPORT attempts:7 score:7
3. JUICY attempts:4 score:4
4. PRIVY attempts:6 score:6
5. GLOVE attempts:8 score:8
6. COLOR attempts:3 score:3
7. GUMMY attempts:9 score:9
8. PUPPY attempts:10 score:10

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1741 🥳 score:44 ⏱️ 0:03:27.747615

📜 1 sessions

Sedecordle Classic sedecordle.com

1. THINK attempts:16 score:1
2. FUNKY attempts:19 score:6
3. EPOCH attempts:7 score:0
4. SHAWL attempts:14 score:7
5. TAKEN attempts:8 score:0
6. BUGLE attempts:11 score:8
7. DOWEL attempts:17 score:1
8. SPELT attempts:9 score:7
9. ALIEN attempts:3 score:0
10. ODDLY attempts:5 score:3
11. AMPLY attempts:15 score:1
12. NADIR attempts:4 score:5
13. LEVER attempts:13 score:1
14. GOOSE attempts:12 score:3
15. FREER attempts:10 score:1
16. CHAFF attempts:18 score:0

# [squareword.org](squareword.org) 🧩 #1754 🥳 7 ⏱️ 0:02:21.520095

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    F E L O N
    O L I V E
    R O V E R
    U P E N D
    M E S S Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1691 🥳 496 ⏱️ 0:03:23.228097

🤔 497 attempts
📜 1 sessions
🫧 27 chat sessions
⁉️ 127 chat prompts
🤖 127 glm-5.3-flash:cloud replies
🥵   1 😎  18 🥶 429 🧊  48

      $1 #497 brazil        100.00°C 🥳 1000‰ ~449 used:0  [448]  source:glm
      $2 #492 amazon         38.49°C 🥵  928‰   ~1 used:1  [0]    source:glm
      $3 #347 nance          29.80°C 😎  647‰  ~18 used:44 [17]   source:glm
      $4 #469 rainforest     28.77°C 😎  590‰   ~4 used:7  [3]    source:glm
      $5 #359 cacao          28.01°C 😎  549‰  ~17 used:23 [16]   source:glm
      $6 #162 pacific        27.67°C 😎  536‰  ~19 used:61 [18]   source:glm
      $7 #313 papaw          26.35°C 😎  460‰  ~15 used:9  [14]   source:glm
      $8 #309 sapodilla      25.57°C 😎  391‰  ~13 used:8  [12]   source:glm
      $9 #494 liana          24.59°C 😎  301‰   ~2 used:0  [1]    source:glm
     $10 #258 papaya         24.47°C 😎  289‰  ~16 used:13 [15]   source:glm
     $11 #276 soursop        24.41°C 😎  280‰  ~14 used:8  [13]   source:glm
     $12 #306 breadfruit     23.96°C 😎  231‰   ~5 used:7  [4]    source:glm
     $21 #353 rambutan       22.14°C 🥶        ~30 used:0  [29]   source:glm
    $450   #6 stapler        -0.06°C 🧊       ~450 used:0  [449]  source:glm

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1724 🥳 166 ⏱️ 0:00:55.507288

🤔 167 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 20 chat prompts
🤖 20 glm-5.3-flash:cloud replies
🔥   1 🥵   6 😎  22 🥶 125 🧊  12

      $1 #167 organe            100.00°C 🥳 1000‰ ~155 used:0 [154]  source:glm
      $2 #159 organisme          38.21°C 🔥  992‰   ~1 used:3 [0]    source:glm
      $3  #93 exécutif           36.28°C 🥵  983‰   ~7 used:8 [6]    source:glm
      $4  #99 autorité           35.45°C 🥵  976‰   ~5 used:5 [4]    source:glm
      $5  #96 institution        34.63°C 🥵  962‰   ~6 used:5 [5]    source:glm
      $6 #163 organique          33.57°C 🥵  946‰   ~2 used:0 [1]    source:glm
      $7 #108 fonction           32.66°C 🥵  919‰   ~3 used:1 [2]    source:glm
      $8 #162 cellule            32.33°C 🥵  908‰   ~4 used:0 [3]    source:glm
      $9  #85 administration     31.30°C 😎  870‰   ~8 used:1 [7]    source:glm
     $10  #90 comité             31.17°C 😎  860‰   ~9 used:0 [8]    source:glm
     $11  #41 constitution       31.13°C 😎  859‰  ~28 used:4 [27]   source:glm
     $12 #150 contrôle           30.37°C 😎  832‰  ~10 used:0 [9]    source:glm
     $31  #94 fédération         23.40°C 🥶        ~33 used:0 [32]   source:glm
    $156  #29 collection         -0.05°C 🧊       ~156 used:0 [155]  source:glm
