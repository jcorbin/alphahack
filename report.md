# 2026-11-24

- 🔗 spaceword.org 🧩 2026-11-23 🏁 score 2170 ranked 14.0% 56/399 ⏱️ 1:29:20.226042
- 🔗 wordgrid 🧩 #906 🟪 rarity:0.15 ⏱️ 0:02:56.661936
- 🔗 alfagok.diginaut.net 🧩 #752 🥳 28 ⏱️ 0:01:05.563493
- 🔗 alphaguess.com 🧩 #1219 🥳 20 ⏱️ 0:02:06.051348
- 🔗 dontwordle.com 🧩 #1645 🥳 6 ⏱️ 0:04:05.966713
- 🔗 dictionary.com hurdle 🧩 #1788 🥳 19 ⏱️ 0:06:35.742072
- 🔗 Quordle Classic 🧩 #1765 🥳 score:18 ⏱️ 0:01:27.231234
- 🔗 Octordle Classic 🧩 #1765 🥳 score:52 ⏱️ 0:04:46.275061
- 🔗 Sedecordle Classic 🧩 #1745 🥳 score:54 ⏱️ 0:03:32.456999
- 🔗 squareword.org 🧩 #1758 🥳 8 ⏱️ 0:05:19.079360
- 🔗 cemantle.certitudes.org 🧩 #1695 🥳 99 ⏱️ 0:00:29.835311
- 🔗 cemantix.certitudes.org 🧩 #1728 🥳 211 ⏱️ 0:01:05.802453

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
















# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #906 🟪 rarity:0.15 ⏱️ 0:02:56.661936

📜 2 sessions
🌌 🦄 🌌
🦄 🌌 🌌
🌌 🦄 🌌
Rarity: 0.15 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-23 🏁 score 2170 ranked 14.0% 56/399 ⏱️ 1:29:20.226042

📜 5 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 56/399

      _ _ _ _ _ H _ _ _ _   
      _ _ _ _ F O P _ _ _   
      _ _ _ _ _ K A _ _ _   
      _ _ _ _ S E V _ _ _   
      _ _ _ _ I _ I _ _ _   
      _ _ _ _ L _ L _ _ _   
      _ _ _ _ I _ I _ _ _   
      _ _ _ _ Q _ O _ _ _   
      _ _ _ _ U R N _ _ _   
      _ _ _ _ E _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #752 🥳 28 ⏱️ 0:01:05.563493

🤔 28 attempts
📜 1 sessions

    @        [     0] &-teken           
    @+2      [     2] -cijferig         
    @+199621 [199621] lijk              q0  ? ␅
    @+199621 [199621] lijk              q1  ? after
    @+199621 [199621] lijk              q2  ? ␅
    @+199621 [199621] lijk              q3  ? after
    @+223484 [223484] molen             q8  ? ␅
    @+223484 [223484] molen             q9  ? after
    @+229484 [229484] natuurbescherming q12 ? ␅
    @+229484 [229484] natuurbescherming q13 ? after
    @+232470 [232470] niets             q14 ? ␅
    @+232470 [232470] niets             q15 ? after
    @+233188 [233188] nimrod            q18 ? ␅
    @+233188 [233188] nimrod            q19 ? after
    @+233346 [233346] nobel             q22 ? ␅
    @+233346 [233346] nobel             q23 ? after
    @+233380 [233380] nodig             q26 ? ␅
    @+233380 [233380] nodig             q27 ? it
    @+233380 [233380] nodig             done. it
    @+233430 [233430] nog               q24 ? ␅
    @+233430 [233430] nog               q25 ? before
    @+233528 [233528] non               q20 ? ␅
    @+233528 [233528] non               q21 ? before
    @+233910 [233910] noord             q16 ? ␅
    @+233910 [233910] noord             q17 ? before
    @+235490 [235490] octrooi           q10 ? ␅
    @+235490 [235490] octrooi           q11 ? before
    @+247546 [247546] op                q6  ? ␅
    @+247546 [247546] op                q7  ? before
    @+299308 [299308] schro             q4  ? ␅
    @+299308 [299308] schro             q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1219 🥳 20 ⏱️ 0:02:06.051348

🤔 20 attempts
📜 1 sessions

    @       [    0] aa      
    @+1     [    1] aah     
    @+2     [    2] aahed   
    @+3     [    3] aahing  
    @+49065 [49065] disturb q4  ? ␅
    @+49065 [49065] disturb q5  ? after
    @+54907 [54907] end     q10 ? ␅
    @+54907 [54907] end     q11 ? after
    @+58108 [58108] evangel q12 ? ␅
    @+58108 [58108] evangel q13 ? after
    @+58204 [58204] ever    q18 ? ␅
    @+58204 [58204] ever    q19 ? it
    @+58204 [58204] ever    done. it
    @+58345 [58345] ex      q16 ? ␅
    @+58345 [58345] ex      q17 ? before
    @+59705 [59705] extra   q14 ? ␅
    @+59705 [59705] extra   q15 ? before
    @+61316 [61316] federal q8  ? ␅
    @+61316 [61316] federal q9  ? before
    @+73596 [73596] guide   q6  ? ␅
    @+73596 [73596] guide   q7  ? before
    @+98138 [98138] mac     q0  ? ␅
    @+98138 [98138] mac     q1  ? after
    @+98138 [98138] mac     q2  ? ␅
    @+98138 [98138] mac     q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1645 🥳 6 ⏱️ 0:04:05.966713

📜 2 sessions
💰 score: 10

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:KOOKS n n n n n remain:4279
    ⬜⬜⬜⬜⬜ tried:FATWA n n n n n remain:1209
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:548
    ⬜🟩⬜⬜⬜ tried:BUMPH n Y n n n remain:33
    ⬜🟩🟨⬜⬜ tried:QUEEN n Y m n n remain:8
    ⬜🟩⬜⬜🟩 tried:CURVE n Y n n Y remain:2

    Undos used: 4

      2 words remaining
    x 5 unused letters
    = 10 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1788 🥳 19 ⏱️ 0:06:35.742072

📜 1 sessions
💰 score: 9700

    5/6
    DEARS ⬜⬜⬜⬜🟨
    SHOYU 🟩⬜⬜⬜🟨
    STUNK 🟩⬜🟩🟩🟩
    KALPA 🟨⬜⬜⬜⬜
    SKUNK 🟩🟩🟩🟩🟩
    3/6
    SKUNK 🟩⬜⬜🟩⬜
    STANE 🟩🟨🟨🟩⬜
    SAINT 🟩🟩🟩🟩🟩
    4/6
    SAINT ⬜⬜🟩⬜⬜
    CHILE 🟨⬜🟩⬜🟩
    FJORD ⬜🟨⬜⬜⬜
    JUICE 🟩🟩🟩🟩🟩
    5/6
    JUICE ⬜🟨⬜⬜⬜
    ABOUT 🟨⬜⬜🟨🟩
    UNHAT 🟨⬜⬜🟨🟩
    FANGS 🟩🟩⬜⬜⬜
    FAULT 🟩🟩🟩🟩🟩
    Final 2/2
    TOPED 🟨🟩⬜🟩⬜
    VOTER 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1765 🥳 score:18 ⏱️ 0:01:27.231234

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. DUNCE attempts:6 score:6
2. BOOST attempts:3 score:3
3. BEAST attempts:4 score:4
4. ODDLY attempts:5 score:5

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1765 🥳 score:52 ⏱️ 0:04:46.275061

📜 1 sessions

Octordle Classic

1. TABBY attempts:9 score:9
2. ENSUE attempts:5 score:5
3. SPINE attempts:6 score:6
4. SCARE attempts:3 score:3
5. PLUMP attempts:10 score:10
6. PRUNE attempts:4 score:4
7. OUGHT attempts:7 score:7
8. BUGLE attempts:8 score:8

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1745 🥳 score:54 ⏱️ 0:03:32.456999

📜 1 sessions

Sedecordle Classic sedecordle.com

1. MEDIC attempts:18 score:1
2. BLEND attempts:4 score:8
3. NAVEL attempts:3 score:0
4. GULLY attempts:17 score:3
5. FLAKY attempts:16 score:1
6. MINUS attempts:13 score:6
7. BLAST attempts:5 score:0
8. UNTIE attempts:11 score:5
9. HEAVE attempts:9 score:0
10. INANE attempts:12 score:9
11. BRASH attempts:6 score:0
12. STRAW attempts:10 score:6
13. TWIST attempts:7 score:0
14. TITHE attempts:14 score:7
15. HOTLY attempts:8 score:0
16. LEDGE attempts:15 score:8

# [squareword.org](squareword.org) 🧩 #1758 🥳 8 ⏱️ 0:05:19.079360

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    V I L L A
    I D E A S
    S L A S H
    T E N S E
    A R S O N

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1695 🥳 99 ⏱️ 0:00:29.835311

🤔 100 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 12 chat prompts
🤖 12 glm-5.3-flash:cloud replies
🥵  2 😎 25 🥶 71 🧊  1

      $1 #100 grass         100.00°C 🥳 1000‰  ~99 used:0 [98]   source:glm
      $2  #82 moss           51.87°C 🥵  982‰   ~2 used:2 [1]    source:glm
      $3  #80 greenery       46.92°C 🥵  952‰   ~1 used:1 [0]    source:glm
      $4  #90 foliage        42.64°C 😎  876‰   ~3 used:0 [2]    source:glm
      $5  #98 lichen         41.30°C 😎  847‰   ~4 used:0 [3]    source:glm
      $6  #93 rhizome        39.29°C 😎  762‰   ~5 used:0 [4]    source:glm
      $7  #88 copse          38.46°C 😎  711‰   ~6 used:0 [5]    source:glm
      $8  #67 grove          38.39°C 😎  707‰  ~24 used:3 [23]   source:glm
      $9  #79 fern           38.20°C 😎  692‰   ~7 used:0 [6]    source:glm
     $10  #97 algae          37.83°C 😎  677‰   ~8 used:0 [7]    source:glm
     $11  #77 deciduous      37.48°C 😎  658‰   ~9 used:0 [8]    source:glm
     $12  #32 bamboo         36.82°C 😎  604‰  ~27 used:6 [26]   source:glm
     $29  #52 maple          29.61°C 🥶        ~28 used:0 [27]   source:glm
    $100   #7 telescope      -4.32°C 🧊       ~100 used:0 [99]   source:glm

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1728 🥳 211 ⏱️ 0:01:05.802453

🤔 212 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 23 chat prompts
🤖 23 glm-5.3-flash:cloud replies
🔥   4 🥵  16 😎  29 🥶 101 🧊  61

      $1 #212 jury            100.00°C 🥳 1000‰ ~151 used:0 [150]  source:glm
      $2 #186 candidat         52.70°C 🔥  998‰   ~2 used:2 [1]    source:glm
      $3 #181 concours         49.69°C 🔥  996‰   ~3 used:4 [2]    source:glm
      $4 #200 présélection     47.26°C 🔥  994‰   ~1 used:0 [0]    source:glm
      $5 #171 épreuve          45.93°C 🔥  990‰   ~4 used:7 [3]    source:glm
      $6 #183 admissibilité    44.62°C 🥵  988‰   ~5 used:0 [4]    source:glm
      $7 #157 examen           42.97°C 🥵  986‰  ~18 used:2 [17]   source:glm
      $8 #190 candidature      39.66°C 🥵  985‰   ~6 used:0 [5]    source:glm
      $9 #179 admission        39.61°C 🥵  984‰   ~7 used:0 [6]    source:glm
     $10 #166 sélection        39.51°C 🥵  983‰   ~8 used:0 [7]    source:glm
     $11 #175 dossier          35.95°C 🥵  970‰   ~9 used:0 [8]    source:glm
     $22 #107 tirage           26.94°C 😎  874‰  ~46 used:3 [45]   source:glm
     $51 #149 arbitrage        13.67°C 🥶        ~55 used:0 [54]   source:glm
    $152  #78 mets             -0.24°C 🧊       ~152 used:0 [151]  source:glm
