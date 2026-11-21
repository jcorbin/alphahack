# 2026-11-22

- 🔗 spaceword.org 🧩 2026-11-21 🏁 score 2173 ranked 11.6% 32/275 ⏱️ 12:06:14.347991
- 🔗 wordgrid 🧩 #904 🟪 rarity:0.23 ⏱️ 0:02:08.131478
- 🔗 alfagok.diginaut.net 🧩 #750 🥳 36 ⏱️ 0:00:48.277227
- 🔗 alphaguess.com 🧩 #1217 🥳 46 ⏱️ 0:00:45.508603
- 🔗 dontwordle.com 🧩 #1643 🥳 6 ⏱️ 0:01:06.673959
- 🔗 dictionary.com hurdle 🧩 #1786 🥳 16 ⏱️ 0:02:25.418966
- 🔗 Quordle Classic 🧩 #1763 🥳 score:28 ⏱️ 0:02:02.644230
- 🔗 Octordle Classic 🧩 #1763 🥳 score:63 ⏱️ 0:02:31.370298
- 🔗 Sedecordle Classic 🧩 #1743 🥳 score:49 ⏱️ 0:03:53.588504
- 🔗 cemantix.certitudes.org 🧩 #1726 🥳 63 ⏱️ 0:00:27.617727
- 🔗 squareword.org 🧩 #1756 🥳 8 ⏱️ 0:02:17.990874
- 🔗 cemantle.certitudes.org 🧩 #1693 🥳 231 ⏱️ 0:00:58.218486

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














# [spaceword.org](spaceword.org) 🧩 2026-11-21 🏁 score 2173 ranked 11.6% 32/275 ⏱️ 12:06:14.347991

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 32/275

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ P I N _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ _ L E V _ _ _   
      _ _ _ _ O _ A _ _ _   
      _ _ _ _ Z _ T _ _ _   
      _ _ _ _ E K E _ _ _   
      _ _ _ _ N O _ _ _ _   
      _ _ _ _ G A Y _ _ _   
      _ _ _ _ E S _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #904 🟪 rarity:0.23 ⏱️ 0:02:08.131478

📜 2 sessions
🦄 🌌 🦄
🦄 🌌 🌌
🌌 🌌 🌌
Rarity: 0.23 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #750 🥳 36 ⏱️ 0:00:48.277227

🤔 36 attempts
📜 2 sessions

    @        [     0] &-teken       
    @+199628 [199628] lijk          q0  ? ␅
    @+199628 [199628] lijk          q1  ? after
    @+299315 [299315] schro         q2  ? ␅
    @+299315 [299315] schro         q3  ? after
    @+349286 [349286] vakantie      q4  ? ␅
    @+349286 [349286] vakantie      q5  ? after
    @+352850 [352850] ver           q8  ? ␅
    @+352850 [352850] ver           q9  ? after
    @+363435 [363435] verzout       q10 ? ␅
    @+363435 [363435] verzout       q11 ? after
    @+368442 [368442] voetbal       q12 ? ␅
    @+368442 [368442] voetbal       q13 ? after
    @+370291 [370291] voor          q14 ? ␅
    @+370291 [370291] voor          q15 ? after
    @+372143 [372143] voortplanting q16 ? ␅
    @+372143 [372143] voortplanting q17 ? after
    @+372577 [372577] voorwereld    q20 ? ␅
    @+372577 [372577] voorwereld    q21 ? after
    @+372675 [372675] voorzien      q24 ? ␅
    @+372675 [372675] voorzien      q25 ? after
    @+372707 [372707] voorzit       q26 ? ␅
    @+372707 [372707] voorzit       q27 ? after
    @+372710 [372710] voorzitten    q32 ? ␅
    @+372710 [372710] voorzitten    q33 ? after
    @+372713 [372713] voorzitter    q34 ? ␅
    @+372713 [372713] voorzitter    q35 ? it
    @+372713 [372713] voorzitter    done. it
    @+372715 [372715] voorzitters   q30 ? ␅
    @+372715 [372715] voorzitters   q31 ? before
    @+372738 [372738] voorzorg      q29 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1217 🥳 46 ⏱️ 0:00:45.508603

🤔 46 attempts
📜 1 sessions

    @        [     0] aa      
    @+98138  [ 98138] mac     q0  ? ␅
    @+98138  [ 98138] mac     q1  ? after
    @+98138  [ 98138] mac     q2  ? ␅
    @+98138  [ 98138] mac     q3  ? after
    @+98138  [ 98138] mac     q4  ? ␅
    @+98138  [ 98138] mac     q5  ? after
    @+147299 [147299] rho     q6  ? ␅
    @+147299 [147299] rho     q7  ? after
    @+159581 [159581] slug    q10 ? ␅
    @+159581 [159581] slug    q11 ? after
    @+160341 [160341] sniggle q20 ? ␅
    @+160341 [160341] sniggle q21 ? after
    @+160705 [160705] soap    q22 ? ␅
    @+160705 [160705] soap    q23 ? after
    @+160904 [160904] sodden  q24 ? ␅
    @+160904 [160904] sodden  q25 ? after
    @+161004 [161004] soil    q26 ? ␅
    @+161004 [161004] soil    q27 ? after
    @+161033 [161033] sola    q28 ? ␅
    @+161033 [161033] sola    q29 ? after
    @+161057 [161057] solar   q30 ? ␅
    @+161057 [161057] solar   q31 ? after
    @+161083 [161083] sold    q32 ? ␅
    @+161083 [161083] sold    q33 ? after
    @+161086 [161086] solder  q34 ? ␅
    @+161086 [161086] solder  q35 ? after
    @+161097 [161097] soldi   q36 ? ␅
    @+161097 [161097] soldi   q37 ? after
    @+161098 [161098] soldier q45 ? it
    @+161098 [161098] soldier done. it

# [dontwordle.com](dontwordle.com) 🧩 #1643 🥳 6 ⏱️ 0:01:06.673959

📜 1 sessions
💰 score: 99

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:YOBBO n n n n n remain:6682
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:3499
    ⬜⬜⬜⬜⬜ tried:FLUFF n n n n n remain:1690
    ⬜🟨⬜⬜⬜ tried:CIVIC n m n n n remain:179
    ⬜⬜🟩⬜⬜ tried:DJINN n n Y n n remain:60
    ⬜🟩🟩⬜⬜ tried:KAIAK n Y Y n n remain:11

    Undos used: 2

      11 words remaining
    x 9 unused letters
    = 99 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1786 🥳 16 ⏱️ 0:02:25.418966

📜 1 sessions
💰 score: 10000

    5/6
    AROSE ⬜⬜⬜⬜⬜
    MUHLY ⬜⬜⬜🟨⬜
    CLINK 🟩🟩🟩⬜⬜
    CLIFT 🟩🟩🟩🟩⬜
    CLIFF 🟩🟩🟩🟩🟩
    5/6
    CLIFF ⬜⬜⬜⬜⬜
    TARES ⬜🟩⬜⬜⬜
    MANGY ⬜🟩⬜⬜🟨
    KAYAK ⬜🟩🟨⬜⬜
    YAHOO 🟩🟩🟩🟩🟩
    2/6
    YAHOO ⬜🟩🟨🟩⬜
    HAVOC 🟩🟩🟩🟩🟩
    3/6
    HAVOC ⬜⬜⬜⬜🟨
    SCUDI 🟨🟨⬜⬜⬜
    CREST 🟩🟩🟩🟩🟩
    Final 1/2
    COULD 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1763 🥳 score:28 ⏱️ 0:02:02.644230

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. FAINT attempts:6 score:9
2. GOLLY attempts:8 score:8
3. JAUNT attempts:7 score:7
4. KNELT attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1763 🥳 score:63 ⏱️ 0:02:31.370298

📜 1 sessions

Octordle Classic

1. ELUDE attempts:10 score:10
2. SAVOY attempts:6 score:6
3. SOBER attempts:9 score:9
4. BINGE attempts:11 score:11
5. ISSUE attempts:2 score:2
6. VIRAL attempts:5 score:5
7. MIGHT attempts:12 score:12
8. THICK attempts:8 score:8

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1743 🥳 score:49 ⏱️ 0:03:53.588504

📜 2 sessions

Sedecordle Classic sedecordle.com

1. ULTRA attempts:16 score:1
2. CABBY attempts:17 score:6
3. LYRIC attempts:8 score:0
4. INERT attempts:3 score:8
5. FIGHT attempts:18 score:1
6. QUICK attempts:10 score:8
7. NERVE attempts:12 score:1
8. MERGE attempts:15 score:2
9. EXTOL attempts:6 score:0
10. LIBEL attempts:13 score:6
11. MINIM attempts:9 score:0
12. CURIO attempts:4 score:9
13. SCOUT attempts:11 score:1
14. SLEPT attempts:7 score:1
15. TEMPO attempts:5 score:0
16. LOGIN attempts:14 score:5

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1726 🥳 63 ⏱️ 0:00:27.617727

🤔 64 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 10 chat prompts
🤖 10 glm-5.3-flash:cloud replies
🥵  5 😎 10 🥶 41 🧊  7

     $1 #64 démon         100.00°C 🥳 1000‰ ~57 used:0 [56]  source:glm
     $2 #63 diable         52.35°C 🥵  985‰  ~1 used:0 [0]   source:glm
     $3 #44 ténèbres       50.69°C 🥵  977‰  ~5 used:5 [4]   source:glm
     $4 #62 exorcisme      49.41°C 🥵  973‰  ~2 used:0 [1]   source:glm
     $5 #54 enfer          44.82°C 🥵  953‰  ~4 used:4 [3]   source:glm
     $6 #56 damnation      41.50°C 🥵  921‰  ~3 used:1 [2]   source:glm
     $7 #33 sombre         37.24°C 😎  832‰  ~6 used:1 [5]   source:glm
     $8 #39 obscurité      35.39°C 😎  772‰  ~7 used:0 [6]   source:glm
     $9 #49 ombre          34.34°C 😎  726‰  ~8 used:0 [7]   source:glm
    $10 #55 abysse         33.89°C 😎  706‰  ~9 used:0 [8]   source:glm
    $11 #61 désespoir      33.61°C 😎  693‰ ~10 used:0 [9]   source:glm
    $12 #47 noirceur       33.41°C 😎  681‰ ~11 used:0 [10]  source:glm
    $17 #60 cadavre        27.24°C 🥶       ~18 used:0 [17]  source:glm
    $58  #5 fourchette     -0.05°C 🧊       ~58 used:0 [57]  source:glm

# [squareword.org](squareword.org) 🧩 #1756 🥳 8 ⏱️ 0:02:17.990874

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟨 🟨 🟨 🟨 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S E D A N
    C R O N E
    R O U G E
    I D L E D
    P E A L S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1693 🥳 231 ⏱️ 0:00:58.218486

🤔 232 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 34 chat prompts
🤖 34 glm-5.3-flash:cloud replies
🔥   2 🥵   5 😎  50 🥶 173 🧊   1

      $1 #232 classic         100.00°C 🥳 1000‰ ~231 used:0  [230]  source:glm
      $2 #230 quintessential   59.45°C 🔥  997‰   ~1 used:1  [0]    source:glm
      $3 #231 archetypal       54.58°C 🔥  994‰   ~2 used:0  [1]    source:glm
      $4  #88 delightful       42.11°C 🥵  962‰  ~53 used:19 [52]   source:glm
      $5 #199 inspired         41.28°C 🥵  958‰   ~4 used:7  [3]    source:glm
      $6 #176 peerless         39.69°C 🥵  936‰   ~5 used:8  [4]    source:glm
      $7 #107 glorious         39.59°C 🥵  933‰   ~6 used:10 [5]    source:glm
      $8 #210 captivating      38.33°C 🥵  910‰   ~3 used:2  [2]    source:glm
      $9 #127 sublime          37.51°C 😎  887‰   ~7 used:1  [6]    source:glm
     $10 #122 elegant          37.34°C 😎  884‰   ~8 used:0  [7]    source:glm
     $11 #226 whimsical        37.16°C 😎  878‰   ~9 used:0  [8]    source:glm
     $12 #128 sumptuous        36.79°C 😎  865‰  ~10 used:0  [9]    source:glm
     $59  #79 savory           28.60°C 🥶        ~63 used:0  [62]   source:glm
    $232  #95 mouth            -1.78°C 🧊       ~232 used:0  [231]  source:glm
