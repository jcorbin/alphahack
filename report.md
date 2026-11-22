# 2026-11-23

- 🔗 spaceword.org 🧩 2026-11-22 🏁 score 2170 ranked 29.2% 84/288 ⏱️ 2:06:31.910216
- 🔗 wordgrid 🧩 #905 🟪 rarity:0.17 ⏱️ 0:03:11.550586
- 🔗 alfagok.diginaut.net 🧩 #751 🥳 50 ⏱️ 0:01:08.096766
- 🔗 alphaguess.com 🧩 #1218 🥳 34 ⏱️ 0:00:38.722225
- 🔗 dontwordle.com 🧩 #1644 🥳 6 ⏱️ 0:01:23.610258
- 🔗 dictionary.com hurdle 🧩 #1787 🥳 17 ⏱️ 0:03:08.998490
- 🔗 Quordle Classic 🧩 #1764 🥳 score:24 ⏱️ 0:01:48.006872
- 🔗 Octordle Classic 🧩 #1764 🥳 score:67 ⏱️ 0:02:28.934364
- 🔗 Sedecordle Classic 🧩 #1744 🥳 score:59 ⏱️ 0:03:57.611608
- 🔗 squareword.org 🧩 #1757 🥳 7 ⏱️ 0:02:24.366409
- 🔗 cemantle.certitudes.org 🧩 #1694 🥳 120 ⏱️ 0:00:39.219211
- 🔗 cemantix.certitudes.org 🧩 #1727 🥳 18 ⏱️ 0:00:11.413929

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















# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #905 🟪 rarity:0.17 ⏱️ 0:03:11.550586

📜 2 sessions
🦄 🌌 🦄
🦄 🌌 🦄
🌌 🌌 🦄
Rarity: 0.17 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-22 🏁 score 2170 ranked 29.2% 84/288 ⏱️ 2:06:31.910216

📜 4 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 84/288

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ A F A R S _ _   
      _ _ _ _ E W _ H _ _   
      _ _ _ Z I N _ A _ _   
      _ _ _ _ J _ _ Y _ _   
      _ _ _ I O T A _ _ _   
      _ _ _ S A E _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #751 🥳 50 ⏱️ 0:01:08.096766

🤔 50 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+199628 [199628] lijk       q0  ? ␅
    @+199628 [199628] lijk       q1  ? after
    @+299315 [299315] schro      q2  ? ␅
    @+299315 [299315] schro      q3  ? after
    @+349286 [349286] vakantie   q4  ? ␅
    @+349286 [349286] vakantie   q5  ? after
    @+374020 [374020] vrij       q6  ? ␅
    @+374020 [374020] vrij       q7  ? after
    @+380230 [380230] weer       q10 ? ␅
    @+380230 [380230] weer       q11 ? after
    @+380699 [380699] weg        q14 ? ␅
    @+380699 [380699] weg        q15 ? after
    @+381884 [381884] wei        q16 ? ␅
    @+381884 [381884] wei        q17 ? after
    @+382000 [382000] weigronden q42 ? ␅
    @+382000 [382000] weigronden q43 ? after
    @+382003 [382003] weijland   q40 ? ␅
    @+382003 [382003] weijland   q41 ? .
    @+382028 [382028] weinig     q48 ? ␅
    @+382028 [382028] weinig     q49 ? it
    @+382028 [382028] weinig     done. it
    @+382053 [382053] weit       q44 ? ␅
    @+382053 [382053] weit       q45 ? before
    @+382111 [382111] wel        q20 ? ␅
    @+382111 [382111] wel        q21 ? before
    @+382512 [382512] welzijn    q18 ? ␅
    @+382512 [382512] welzijn    q19 ? before
    @+383192 [383192] werk       q12 ? ␅
    @+383192 [383192] werk       q13 ? before
    @+386545 [386545] wind       q9  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1218 🥳 34 ⏱️ 0:00:38.722225

🤔 34 attempts
📜 1 sessions

    @       [    0] aa            
    @+24522 [24522] carabin       q6  ? ␅
    @+24522 [24522] carabin       q7  ? after
    @+36722 [36722] cos           q8  ? ␅
    @+36722 [36722] cos           q9  ? after
    @+42889 [42889] defi          q10 ? ␅
    @+42889 [42889] defi          q11 ? after
    @+44430 [44430] depersonalise q18 ? ␅
    @+44430 [44430] depersonalise q19 ? after
    @+44814 [44814] derive        q22 ? ␅
    @+44814 [44814] derive        q23 ? after
    @+45006 [45006] desert        q24 ? ␅
    @+45006 [45006] desert        q25 ? after
    @+45018 [45018] desertions    q30 ? ␅
    @+45018 [45018] desertions    q31 ? after
    @+45021 [45021] deserve       q32 ? ␅
    @+45021 [45021] deserve       q33 ? it
    @+45021 [45021] deserve       done. it
    @+45029 [45029] deserving     q28 ? ␅
    @+45029 [45029] deserving     q29 ? before
    @+45051 [45051] desi          q26 ? ␅
    @+45051 [45051] desi          q27 ? before
    @+45200 [45200] despise       q20 ? ␅
    @+45200 [45200] despise       q21 ? before
    @+45976 [45976] diabase       q14 ? ␅
    @+45976 [45976] diabase       q15 ? before
    @+49063 [49063] disturb       q4  ? ␅
    @+49063 [49063] disturb       q5  ? before
    @+98136 [98136] mac           q1  ? after
    @+98136 [98136] mac           q2  ? ␅
    @+98136 [98136] mac           q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1644 🥳 6 ⏱️ 0:01:23.610258

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:FEMME n n n n n remain:5567
    ⬜⬜⬜⬜⬜ tried:LININ n n n n n remain:1991
    ⬜⬜⬜⬜⬜ tried:DODOS n n n n n remain:299
    ⬜⬜⬜⬜⬜ tried:YUPPY n n n n n remain:72
    ⬜🟨⬜⬜⬜ tried:GABBA n m n n n remain:14
    ⬜⬜🟩🟩🟩 tried:THACK n n Y Y Y remain:2

    Undos used: 4

      2 words remaining
    x 7 unused letters
    = 14 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1787 🥳 17 ⏱️ 0:03:08.998490

📜 1 sessions
💰 score: 9900

    4/6
    TEALS ⬜🟨⬜⬜🟩
    RODES 🟨⬜🟨🟨🟩
    CREDS ⬜🟩🟩🟨🟩
    DRESS 🟩🟩🟩🟩🟩
    3/6
    DRESS 🟨⬜⬜⬜⬜
    VALID ⬜⬜⬜🟩🟩
    HUMID 🟩🟩🟩🟩🟩
    4/6
    HUMID ⬜⬜⬜⬜⬜
    STORE ⬜⬜🟩⬜🟨
    EPOXY 🟩⬜🟩⬜🟩
    EBONY 🟩🟩🟩🟩🟩
    5/6
    EBONY ⬜⬜🟩⬜⬜
    FROTH ⬜🟩🟩⬜⬜
    CAPED ⬜⬜⬜⬜🟨
    DROOL 🟩🟩🟩⬜🟩
    DROLL 🟩🟩🟩🟩🟩
    Final 1/2
    SKIRT 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1764 🥳 score:24 ⏱️ 0:01:48.006872

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. RAINY attempts:3 score:3
2. BAGGY attempts:7 score:7
3. CADDY attempts:9 score:9
4. MOVIE attempts:5 score:5

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1764 🥳 score:67 ⏱️ 0:02:28.934364

📜 1 sessions

Octordle Classic

1. SPRIG attempts:10 score:10
2. REPEL attempts:8 score:8
3. CASTE attempts:13 score:13
4. SPLAT attempts:6 score:6
5. DRAPE attempts:11 score:11
6. WAXEN attempts:3 score:3
7. METER attempts:9 score:9
8. PETAL attempts:7 score:7

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1744 🥳 score:59 ⏱️ 0:03:57.611608

📜 1 sessions

Sedecordle Classic sedecordle.com

1. KNELT attempts:18 score:1
2. WIELD attempts:12 score:8
3. MANGY attempts:18 score:1
4. OLIVE attempts:10 score:9
5. ROUND attempts:6 score:0
6. VYING attempts:15 score:6
7. EARTH attempts:7 score:0
8. TEMPO attempts:4 score:7
9. GOODY attempts:16 score:1
10. JUNTO attempts:5 score:6
11. GIANT attempts:8 score:0
12. PIZZA attempts:14 score:8
13. BRIEF attempts:13 score:1
14. ROWER attempts:11 score:3
15. FLUSH attempts:17 score:1
16. BONGO attempts:9 score:7

# [squareword.org](squareword.org) 🧩 #1757 🥳 7 ⏱️ 0:02:24.366409

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟨 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C R A N E
    H E R O N
    A R G O T
    P A U S E
    S N E E R

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1694 🥳 120 ⏱️ 0:00:39.219211

🤔 121 attempts
📜 2 sessions
🫧 4 chat sessions
⁉️ 17 chat prompts
🤖 17 glm-5.3-flash:cloud replies
🔥  1 🥵  6 😎 20 🥶 89 🧊  4

      $1 #121 mature       100.00°C 🥳 1000‰ ~117 used:0 [116]  source:glm
      $2  #90 immature      58.56°C 🔥  997‰   ~1 used:6 [0]    source:glm
      $3 #110 grown         41.59°C 🥵  986‰   ~6 used:2 [5]    source:glm
      $4 #111 adult         36.39°C 🥵  958‰   ~2 used:0 [1]    source:glm
      $5  #72 pubescent     35.96°C 🥵  951‰   ~7 used:4 [6]    source:glm
      $6  #95 callow        35.58°C 🥵  946‰   ~3 used:0 [2]    source:glm
      $7 #109 growing       35.22°C 🥵  939‰   ~4 used:0 [3]    source:glm
      $8 #112 age           34.23°C 🥵  921‰   ~5 used:0 [4]    source:glm
      $9  #99 naive         32.50°C 😎  871‰   ~8 used:0 [7]    source:glm
     $10 #105 budding       32.00°C 😎  855‰   ~9 used:0 [8]    source:glm
     $11  #85 weedy         31.12°C 😎  814‰  ~10 used:0 [9]    source:glm
     $12 #118 fledged       30.40°C 😎  769‰  ~11 used:0 [10]   source:glm
     $29  #76 gnarled       24.30°C 🥶        ~31 used:0 [30]   source:glm
    $118   #7 thunder       -0.55°C 🧊       ~118 used:0 [117]  source:glm

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1727 🥳 18 ⏱️ 0:00:11.413929

🤔 19 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 5 chat prompts
🤖 5 glm-5.3-flash:cloud replies
🔥 1 🥵 2 😎 4 🥶 8 🧊 3

     $1 #19 marin         100.00°C 🥳 1000‰ ~16 used:0 [15]  source:glm
     $2 #12 mer            60.47°C 🔥  998‰  ~1 used:2 [0]   source:glm
     $3 #18 bateau         50.30°C 🥵  976‰  ~2 used:0 [1]   source:glm
     $4 #13 océan          46.29°C 🥵  957‰  ~3 used:0 [2]   source:glm
     $5 #17 algue          35.65°C 😎  742‰  ~4 used:0 [3]   source:glm
     $6 #15 poisson        30.20°C 😎  495‰  ~5 used:0 [4]   source:glm
     $7 #11 coquillage     28.12°C 😎  358‰  ~6 used:0 [5]   source:glm
     $8 #14 plage          26.34°C 😎  217‰  ~7 used:0 [6]   source:glm
     $9  #4 coquille       16.76°C 🥶        ~8 used:1 [7]   source:glm
    $10 #16 vague          16.39°C 🥶        ~9 used:0 [8]   source:glm
    $11 #10 parapluie      14.28°C 🥶       ~10 used:0 [9]   source:glm
    $12  #8 nuage          11.29°C 🥶       ~11 used:0 [10]  source:glm
    $13  #2 bicyclette      5.64°C 🥶       ~12 used:0 [11]  source:glm
    $17  #7 marmotte       -0.29°C 🧊       ~17 used:0 [16]  source:glm
