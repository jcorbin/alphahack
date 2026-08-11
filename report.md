# 2026-08-12

- 🔗 spaceword.org 🧩 2026-08-11 🏁 score 2168 ranked 39.2% 127/324 ⏱️ 0:05:55.382725
- 🔗 wordgrid 🧩 #802 🟪 rarity:0.21 ⏱️ 0:02:52.660826
- 🔗 alfagok.diginaut.net 🧩 #648 🥳 24 ⏱️ 0:00:31.879066
- 🔗 alphaguess.com 🧩 #1115 🥳 28 ⏱️ 0:00:31.245318
- 🔗 dontwordle.com 🧩 #1541 🥳 6 ⏱️ 0:01:37.808032
- 🔗 dictionary.com hurdle 🧩 #1684 🥳 20 ⏱️ 0:03:35.293339
- 🔗 Quordle Classic 🧩 #1661 🥳 score:23 ⏱️ 0:01:18.379992
- 🔗 Octordle Classic 🧩 #1661 🥳 score:62 ⏱️ 0:02:26.052232
- 🔗 Sedecordle Classic 🧩 #1641 🥳 score:44 ⏱️ 0:02:42.854835
- 🔗 squareword.org 🧩 #1654 🥳 8 ⏱️ 0:02:21.657666
- 🔗 cemantle.certitudes.org 🧩 #1591 🥳 106 ⏱️ 0:00:35.448075
- 🔗 cemantix.certitudes.org 🧩 #1624 🥳 385 ⏱️ 0:06:17.878463

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







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #781 🟪 rarity:0.15 ⏱️ 0:03:50.236694

📜 2 sessions
🌌 🦄 🦄
🌌 🦄 🦄
🌌 🌌 🌌
Rarity: 0.15 🟪


# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #-1 ❗ rarity:nan ⏱️ 0:05:19.095498

📜 2 sessions
🌌 🦄 🌌
🌌 🦄 🌌
🌌 🦄 🌌
Rarity: nan ❗







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #788 🟪 rarity:0.29 ⏱️ 0:03:24.033720

📜 2 sessions
🦄 🦄 🌌
🦄 🦄 🦄
🌌 🦄 🌌
Rarity: 0.29 🟪


# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #789 🟪 rarity:0.23 ⏱️ 0:02:56.015327

📜 2 sessions
🌌 🌌 🌌
🦄 🦄 🌌
🦄 🦄 🦄
Rarity: 0.23 🟪







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #795 🟪 rarity:0.27 ⏱️ 0:03:44.973967

📜 2 sessions
🦄 🌌 🌌
🌌 🌌 🌌
🦄 🦄 🌌
Rarity: 0.27 🟪








# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #802 🟪 rarity:0.21 ⏱️ 0:02:52.660826

📜 2 sessions
🦄 🌌 🌌
🌌 🦄 🌌
🦄 🦄 🌌
Rarity: 0.21 🟪

# [spaceword.org](spaceword.org) 🧩 2026-08-11 🏁 score 2168 ranked 39.2% 127/324 ⏱️ 0:05:55.382725

📜 2 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 127/324

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ B U B O _ _ _   
      _ _ _ _ _ _ S _ _ _   
      _ _ _ _ S I C _ _ _   
      _ _ _ _ E _ U _ _ _   
      _ _ _ _ E _ L _ _ _   
      _ _ _ _ K _ A _ _ _   
      _ _ _ V E X T _ _ _   
      _ _ _ _ R U E _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #648 🥳 24 ⏱️ 0:00:31.879066

🤔 24 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+1      [     1] &-tekens    
    @+2      [     2] -cijferig   
    @+3      [     3] -e-mail     
    @+199548 [199548] lij         q0  ? ␅
    @+199548 [199548] lij         q1  ? after
    @+199548 [199548] lij         q2  ? ␅
    @+199548 [199548] lij         q3  ? after
    @+299514 [299514] schrok      q4  ? ␅
    @+299514 [299514] schrok      q5  ? after
    @+349501 [349501] vakanties   q6  ? ␅
    @+349501 [349501] vakanties   q7  ? after
    @+361941 [361941] vervolg     q10 ? ␅
    @+361941 [361941] vervolg     q11 ? after
    @+365047 [365047] vind        q14 ? ␅
    @+365047 [365047] vind        q15 ? after
    @+365440 [365440] vis         q18 ? ␅
    @+365440 [365440] vis         q19 ? after
    @+365944 [365944] visualiseer q20 ? ␅
    @+365944 [365944] visualiseer q21 ? after
    @+366191 [366191] vlag        q22 ? ␅
    @+366191 [366191] vlag        q23 ? it
    @+366191 [366191] vlag        done. it
    @+366447 [366447] vlees       q16 ? ␅
    @+366447 [366447] vlees       q17 ? before
    @+368188 [368188] voedsel     q12 ? ␅
    @+368188 [368188] voedsel     q13 ? before
    @+374496 [374496] vrijst      q8  ? ␅
    @+374496 [374496] vrijst      q9  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1115 🥳 28 ⏱️ 0:00:31.245318

🤔 28 attempts
📜 1 sessions

    @       [    0] aa         
    @+2     [    2] aahed      
    @+47378 [47378] dis        q4  ? ␅
    @+47378 [47378] dis        q5  ? after
    @+60017 [60017] eyewitness q8  ? ␅
    @+60017 [60017] eyewitness q9  ? after
    @+63151 [63151] fix        q12 ? ␅
    @+63151 [63151] fix        q13 ? after
    @+63163 [63163] fixed      q26 ? ␅
    @+63163 [63163] fixed      q27 ? it
    @+63163 [63163] fixed      done. it
    @+63183 [63183] fiz        q24 ? ␅
    @+63183 [63183] fiz        q25 ? before
    @+63223 [63223] flaccid    q22 ? ␅
    @+63223 [63223] flaccid    q23 ? before
    @+63300 [63300] flak       q20 ? ␅
    @+63300 [63300] flak       q21 ? before
    @+63476 [63476] flat       q18 ? ␅
    @+63476 [63476] flat       q19 ? before
    @+63929 [63929] flirt      q16 ? ␅
    @+63929 [63929] flirt      q17 ? before
    @+64725 [64725] fold       q14 ? ␅
    @+64725 [64725] fold       q15 ? before
    @+66309 [66309] free       q10 ? ␅
    @+66309 [66309] free       q11 ? before
    @+72662 [72662] green      q6  ? ␅
    @+72662 [72662] green      q7  ? before
    @+98147 [98147] mac        q0  ? ␅
    @+98147 [98147] mac        q1  ? after
    @+98147 [98147] mac        q2  ? ␅
    @+98147 [98147] mac        q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1541 🥳 6 ⏱️ 0:01:37.808032

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:BOFFO n n n n n remain:7320
    ⬜⬜⬜⬜⬜ tried:ZAKAT n n n n n remain:2166
    ⬜⬜⬜⬜⬜ tried:YUMMY n n n n n remain:958
    ⬜🟨⬜⬜⬜ tried:GRRRL n m n n n remain:97
    ⬜🟩⬜⬜🟨 tried:CEDER n Y n n m remain:6
    🟩🟩⬜🟩🟩 tried:RENIN Y Y n Y Y remain:3

    Undos used: 2

      3 words remaining
    x 8 unused letters
    = 24 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1684 🥳 20 ⏱️ 0:03:35.293339

📜 1 sessions
💰 score: 9600

    4/6
    SERAI 🟩⬜⬜⬜⬜
    SOUTH 🟩🟨🟨🟨⬜
    SPOUT 🟩⬜🟩🟩🟩
    SCOUT 🟩🟩🟩🟩🟩
    6/6
    SCOUT ⬜⬜⬜⬜🟩
    INLET 🟨🟨⬜⬜🟩
    GIANT ⬜🟨🟨🟩🟩
    FAINT ⬜🟩🟩🟩🟩
    PAINT ⬜🟩🟩🟩🟩
    TAINT 🟩🟩🟩🟩🟩
    4/6
    TAINT ⬜🟨🟨⬜⬜
    LIDAR 🟨🟨⬜🟨⬜
    CLAIM ⬜🟨🟩🟩🟨
    EMAIL 🟩🟩🟩🟩🟩
    5/6
    EMAIL 🟨⬜⬜⬜⬜
    CODER ⬜⬜⬜🟩🟨
    URGES ⬜🟨⬜🟩🟨
    RESET 🟨⬜🟨🟩⬜
    SHREW 🟩🟩🟩🟩🟩
    Final 1/2
    BLIMP 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1661 🥳 score:23 ⏱️ 0:01:18.379992

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. HOTLY attempts:6 score:6
2. CROWD attempts:4 score:4
3. HEART attempts:5 score:5
4. SWASH attempts:8 score:8

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1661 🥳 score:62 ⏱️ 0:02:26.052232

📜 1 sessions

Octordle Classic

1. VISIT attempts:5 score:5
2. RACER attempts:10 score:10
3. SOOTY attempts:8 score:8
4. TIGER attempts:4 score:4
5. KNACK attempts:11 score:11
6. PUPPY attempts:12 score:12
7. HEFTY attempts:9 score:9
8. GREAT attempts:3 score:3

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1641 🥳 score:44 ⏱️ 0:02:42.854835

📜 1 sessions

Sedecordle Classic sedecordle.com

1. SCION attempts:10 score:1
2. CLUCK attempts:9 score:0
3. SHRUB attempts:17 score:1
4. KNAVE attempts:18 score:7
5. STAKE attempts:11 score:1
6. FEMUR attempts:5 score:1
7. MURAL attempts:6 score:0
8. CRONE attempts:12 score:6
9. SAUCE attempts:4 score:0
10. KAYAK attempts:13 score:4
11. FERAL attempts:18 score:1
12. SHALE attempts:3 score:9
13. OFFAL attempts:7 score:0
14. SPURT attempts:14 score:7
15. LAPEL attempts:15 score:1
16. STOMP attempts:8 score:5

# [squareword.org](squareword.org) 🧩 #1654 🥳 8 ⏱️ 0:02:21.657666

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟩 🟨
    🟨 🟨 🟨 🟨 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    D E C A L
    A L O N E
    T O R T E
    U P P E R
    M E S S Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1591 🥳 106 ⏱️ 0:00:35.448075

🤔 107 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 11 chat prompts
🤖 11 dolphin3:latest replies
😱  1 🔥  2 🥵 10 😎 25 🥶 64 🧊  4

      $1 #107 pollution        100.00°C 🥳 1000‰ ~103 used:0 [102]  source:dolphin3
      $2  #93 pollutant         69.95°C 😱  999‰   ~1 used:2 [0]    source:dolphin3
      $3  #82 emission          66.68°C 🔥  998‰   ~2 used:4 [1]    source:dolphin3
      $4  #60 environmental     58.62°C 🔥  993‰   ~3 used:4 [2]    source:dolphin3
      $5  #92 ozone             49.96°C 🥵  989‰   ~4 used:0 [3]    source:dolphin3
      $6 #100 mercury           49.48°C 🥵  987‰   ~5 used:0 [4]    source:dolphin3
      $7  #55 contamination     49.35°C 🥵  986‰   ~6 used:0 [5]    source:dolphin3
      $8  #84 carbon            45.64°C 🥵  975‰   ~7 used:0 [6]    source:dolphin3
      $9 #103 noise             44.13°C 🥵  966‰   ~8 used:0 [7]    source:dolphin3
     $10  #96 dioxide           41.80°C 🥵  957‰   ~9 used:0 [8]    source:dolphin3
     $11  #52 waste             41.26°C 🥵  954‰  ~13 used:2 [12]   source:dolphin3
     $15  #75 conservation      36.47°C 😎  882‰  ~14 used:0 [13]   source:dolphin3
     $40  #69 particle          23.59°C 🥶        ~39 used:0 [38]   source:dolphin3
    $104   #4 compass           -1.01°C 🧊       ~104 used:0 [103]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1624 🥳 385 ⏱️ 0:06:17.878463

🤔 386 attempts
📜 1 sessions
🫧 19 chat sessions
⁉️ 91 chat prompts
🤖 91 dolphin3:latest replies
😱   1 🔥   6 🥵  13 😎  25 🥶 291 🧊  49

      $1 #386 silencieux       100.00°C 🥳 1000‰ ~337 used:0  [336]  source:dolphin3
      $2 #383 silence           59.26°C 😱  999‰   ~1 used:0  [0]    source:dolphin3
      $3 #341 bruyant           54.72°C 🔥  998‰  ~17 used:17 [16]   source:dolphin3
      $4 #360 ronronnement      48.58°C 🔥  997‰  ~16 used:11 [15]   source:dolphin3
      $5 #385 muet              48.35°C 🔥  995‰   ~2 used:0  [1]    source:dolphin3
      $6 #342 discret           48.10°C 🔥  994‰   ~4 used:9  [3]    source:dolphin3
      $7 #376 cliquetis         47.32°C 🔥  992‰   ~3 used:0  [2]    source:dolphin3
      $8 #328 bruissement       46.96°C 🔥  990‰   ~5 used:10 [4]    source:dolphin3
      $9 #367 assourdissant     45.76°C 🥵  988‰   ~6 used:0  [5]    source:dolphin3
     $10 #364 grondement        44.39°C 🥵  986‰   ~7 used:0  [6]    source:dolphin3
     $11 #359 murmure           43.69°C 🥵  984‰   ~8 used:0  [7]    source:dolphin3
     $22  #87 échappement       32.00°C 😎  801‰  ~45 used:59 [44]   source:dolphin3
     $47 #375 ronron            24.47°C 🥶        ~58 used:0  [57]   source:dolphin3
    $338 #242 comprimé          -0.10°C 🧊       ~338 used:0  [337]  source:dolphin3
