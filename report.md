# 2026-11-25

- 🔗 spaceword.org 🧩 2026-11-24 🏁 score 2168 ranked 37.3% 139/373 ⏱️ 1:27:24.846430
- 🔗 wordgrid 🧩 #907 🟪 rarity:0.21 ⏱️ 0:02:09.983868
- 🔗 alfagok.diginaut.net 🧩 #753 🥳 24 ⏱️ 0:00:47.723995
- 🔗 alphaguess.com 🧩 #1220 🥳 24 ⏱️ 0:00:30.186564
- 🔗 dontwordle.com 🧩 #1646 🥳 6 ⏱️ 0:01:21.386880
- 🔗 dictionary.com hurdle 🧩 #1789 🥳 17 ⏱️ 0:02:49.146472
- 🔗 Quordle Classic 🧩 #1766 🥳 score:22 ⏱️ 0:01:37.320578
- 🔗 Octordle Classic 🧩 #1766 🥳 score:52 ⏱️ 0:02:17.652301
- 🔗 Sedecordle Classic 🧩 #1746 🥳 score:49 ⏱️ 0:03:39.767431
- 🔗 squareword.org 🧩 #1759 🥳 7 ⏱️ 0:02:16.190217
- 🔗 cemantle.certitudes.org 🧩 #1696 🥳 208 ⏱️ 0:00:51.098000
- 🔗 cemantix.certitudes.org 🧩 #1729 🥳 59 ⏱️ 0:00:31.146453

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

















# [spaceword.org](spaceword.org) 🧩 2026-11-24 🏁 score 2168 ranked 37.3% 139/373 ⏱️ 1:27:24.846430

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 139/373

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ T E A M _ _ _   
      _ _ _ _ _ _ A _ _ _   
      _ _ _ _ L E X _ _ _   
      _ _ _ _ _ Q I _ _ _   
      _ _ _ _ _ U N _ _ _   
      _ _ _ _ _ A G _ _ _   
      _ _ _ G O T _ _ _ _   
      _ _ _ O W E D _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #907 🟪 rarity:0.21 ⏱️ 0:02:09.983868

📜 2 sessions
🌌 🌌 🌌
🌌 🌌 🌌
🌌 🦄 🦄
Rarity: 0.21 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #753 🥳 24 ⏱️ 0:00:47.723995

🤔 24 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+49802  [ 49802] boks      q6  ? ␅
    @+49802  [ 49802] boks      q7  ? after
    @+74698  [ 74698] dc        q8  ? ␅
    @+74698  [ 74698] dc        q9  ? after
    @+87156  [ 87156] draag     q10 ? ␅
    @+87156  [ 87156] draag     q11 ? after
    @+90006  [ 90006] dubbel    q14 ? ␅
    @+90006  [ 90006] dubbel    q15 ? after
    @+91683  [ 91683] dwerg     q16 ? ␅
    @+91683  [ 91683] dwerg     q17 ? after
    @+92097  [ 92097] ecart     q20 ? ␅
    @+92097  [ 92097] ecart     q21 ? after
    @+92290  [ 92290] economie  q22 ? ␅
    @+92290  [ 92290] economie  q23 ? it
    @+92290  [ 92290] economie  done. it
    @+92512  [ 92512] educatie  q18 ? ␅
    @+92512  [ 92512] educatie  q19 ? before
    @+93368  [ 93368] eet       q12 ? ␅
    @+93368  [ 93368] eet       q13 ? before
    @+99672  [ 99672] ex        q4  ? ␅
    @+99672  [ 99672] ex        q5  ? before
    @+199628 [199628] lijk      q0  ? ␅
    @+199628 [199628] lijk      q1  ? after
    @+199628 [199628] lijk      q2  ? ␅
    @+199628 [199628] lijk      q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1220 🥳 24 ⏱️ 0:00:30.186564

🤔 24 attempts
📜 1 sessions

    @        [     0] aa        
    @+1      [     1] aah       
    @+2      [     2] aahed     
    @+3      [     3] aahing    
    @+98136  [ 98136] mac       q0  ? ␅
    @+98136  [ 98136] mac       q1  ? after
    @+98136  [ 98136] mac       q2  ? ␅
    @+98136  [ 98136] mac       q3  ? after
    @+147297 [147297] rho       q4  ? ␅
    @+147297 [147297] rho       q5  ? after
    @+171896 [171896] tag       q6  ? ␅
    @+171896 [171896] tag       q7  ? after
    @+172458 [172458] tap       q16 ? ␅
    @+172458 [172458] tap       q17 ? after
    @+172467 [172467] tape      q22 ? ␅
    @+172467 [172467] tape      q23 ? it
    @+172467 [172467] tape      done. it
    @+172532 [172532] tar       q20 ? ␅
    @+172532 [172532] tar       q21 ? before
    @+172794 [172794] tattle    q18 ? ␅
    @+172794 [172794] tattle    q19 ? before
    @+173136 [173136] technical q14 ? ␅
    @+173136 [173136] technical q15 ? before
    @+174382 [174382] test      q12 ? ␅
    @+174382 [174382] test      q13 ? before
    @+176933 [176933] tom       q10 ? ␅
    @+176933 [176933] tom       q11 ? before
    @+181981 [181981] un        q8  ? ␅
    @+181981 [181981] un        q9  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1646 🥳 6 ⏱️ 0:01:21.386880

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:WANNA n n n n n remain:5495
    ⬜⬜⬜⬜⬜ tried:JEEZE n n n n n remain:2466
    ⬜⬜⬜⬜⬜ tried:CUDDY n n n n n remain:745
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:224
    ⬜⬜⬜⬜🟩 tried:PHPHT n n n n Y remain:13
    🟩🟨⬜⬜🟩 tried:FIXIT Y m n n Y remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1789 🥳 17 ⏱️ 0:02:49.146472

📜 1 sessions
💰 score: 9900

    5/6
    ROSET ⬜⬜⬜⬜⬜
    LINKY 🟨🟨⬜⬜⬜
    CALIF ⬜⬜🟨🟨⬜
    BLIMP 🟩🟨🟩⬜⬜
    BUILD 🟩🟩🟩🟩🟩
    4/6
    BUILD ⬜⬜🟩⬜⬜
    PRIES ⬜🟨🟩🟨⬜
    REIFY 🟨🟨🟩🟨⬜
    AFIRE 🟩🟩🟩🟩🟩
    3/6
    AFIRE ⬜🟨⬜🟩🟨
    FERRY 🟨🟩🟨🟩🟩
    REFRY 🟩🟩🟩🟩🟩
    4/6
    REFRY 🟩⬜⬜⬜⬜
    RIOTS 🟩⬜🟨⬜⬜
    RADON 🟩⬜🟨🟨🟨
    ROUND 🟩🟩🟩🟩🟩
    Final 1/2
    SPOIL 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1766 🥳 score:22 ⏱️ 0:01:37.320578

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. PULPY attempts:5 score:5
2. LEACH attempts:8 score:8
3. ROUTE attempts:3 score:3
4. MOURN attempts:6 score:6

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1766 🥳 score:52 ⏱️ 0:02:17.652301

📜 2 sessions

Octordle Classic

1. CRUEL attempts:9 score:9
2. SCRAP attempts:4 score:4
3. QUACK attempts:7 score:7
4. BOOST attempts:10 score:10
5. OPERA attempts:3 score:3
6. HUMOR attempts:6 score:6
7. YACHT attempts:5 score:5
8. BRAWL attempts:8 score:8

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1746 🥳 score:49 ⏱️ 0:03:39.767431

📜 1 sessions

Sedecordle Classic sedecordle.com

1. SERIF attempts:3 score:0
2. WIGHT attempts:16 score:3
3. TROVE attempts:9 score:0
4. ALLOT attempts:8 score:9
5. QUEUE attempts:15 score:1
6. FRILL attempts:4 score:5
7. CATER attempts:14 score:1
8. CHOKE attempts:10 score:4
9. SPUNK attempts:5 score:0
10. PROXY attempts:6 score:5
11. SPASM attempts:17 score:1
12. SWEET attempts:11 score:7
13. SWEAR attempts:13 score:1
14. FLING attempts:7 score:3
15. DAUNT attempts:18 score:1
16. AVIAN attempts:12 score:8

# [squareword.org](squareword.org) 🧩 #1759 🥳 7 ⏱️ 0:02:16.190217

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T A G S
    T U N I C
    A L I V E
    R I S E N
    S P E N T

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1696 🥳 208 ⏱️ 0:00:51.098000

🤔 209 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 26 chat prompts
🤖 26 glm-5.3-flash:cloud replies
🥵   2 😎  23 🥶 171 🧊  12

      $1 #209 confidential    100.00°C 🥳 1000‰ ~197 used:0  [196]  source:glm
      $2 #198 discreet         35.80°C 🥵  970‰   ~1 used:2  [0]    source:glm
      $3  #90 amicable         31.24°C 🥵  936‰  ~16 used:20 [15]   source:glm
      $4  #95 compromising     27.82°C 😎  857‰  ~25 used:10 [24]   source:glm
      $5 #113 cordial          26.05°C 😎  791‰  ~17 used:2  [16]   source:glm
      $6  #53 negotiation      25.92°C 😎  784‰  ~24 used:5  [23]   source:glm
      $7 #167 respectful       24.95°C 😎  732‰  ~18 used:2  [17]   source:glm
      $8 #133 courteous        24.86°C 😎  728‰  ~19 used:2  [18]   source:glm
      $9 #124 tactful          24.40°C 😎  703‰  ~20 used:2  [19]   source:glm
     $10 #143 civil            22.75°C 😎  562‰  ~21 used:2  [20]   source:glm
     $11  #75 settlement       22.41°C 😎  513‰  ~23 used:3  [22]   source:glm
     $12 #105 negotiable       22.41°C 😎  512‰   ~2 used:1  [1]    source:glm
     $27 #207 cautious         18.85°C 🥶        ~28 used:0  [27]   source:glm
    $198   #1 banana           -0.13°C 🧊       ~198 used:0  [197]  source:glm

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1729 🥳 59 ⏱️ 0:00:31.146453

🤔 60 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 7 chat prompts
🤖 7 glm-5.3-flash:cloud replies
🥵  1 😎 16 🥶 39 🧊  3

     $1 #60 quête          100.00°C 🥳 1000‰ ~57 used:0 [56]  source:glm
     $2 #42 rêve            37.86°C 🥵  980‰  ~1 used:2 [0]   source:glm
     $3 #24 chimère         32.28°C 😎  889‰ ~17 used:3 [16]  source:glm
     $4 #45 utopie          29.87°C 😎  802‰ ~15 used:2 [14]  source:glm
     $5 #56 onirique        29.78°C 😎  794‰  ~2 used:0 [1]   source:glm
     $6 #53 idéal           29.59°C 😎  784‰  ~3 used:0 [2]   source:glm
     $7 #36 fantasme        29.21°C 😎  761‰  ~4 used:0 [3]   source:glm
     $8 #48 aspiration      28.09°C 😎  680‰  ~5 used:0 [4]   source:glm
     $9 #52 espoir          27.99°C 😎  673‰  ~6 used:0 [5]   source:glm
    $10 #40 magie           27.73°C 😎  647‰  ~7 used:0 [6]   source:glm
    $11 #33 chimérique      27.49°C 😎  624‰  ~8 used:0 [7]   source:glm
    $12 #22 illusion        26.83°C 😎  560‰ ~16 used:2 [15]  source:glm
    $19 #55 imagination     22.37°C 🥶       ~20 used:0 [19]  source:glm
    $58 #11 eau             -1.37°C 🧊       ~58 used:0 [57]  source:glm
