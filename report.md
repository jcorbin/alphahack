# 2026-06-20

- 🔗 spaceword.org 🧩 2026-06-19 🏁 score 2173 ranked 10.4% 31/299 ⏱️ 2:50:44.191798
- 🔗 alfagok.diginaut.net 🧩 #595 🥳 22 ⏱️ 0:00:31.334067
- 🔗 alphaguess.com 🧩 #1062 🥳 26 ⏱️ 0:00:31.504949
- 🔗 dontwordle.com 🧩 #1488 🥳 6 ⏱️ 0:01:14.616317
- 🔗 dictionary.com hurdle 🧩 #1631 🥳 17 ⏱️ 0:03:27.744620
- 🔗 Quordle Classic 🧩 #1608 🥳 score:19 ⏱️ 0:01:26.741853
- 🔗 Octordle Classic 🧩 #1608 🥳 score:58 ⏱️ 0:03:51.603180
- 🔗 Sedecordle Classic 🧩 #1588 🥳 score:53 ⏱️ 0:13:46.816997
- 🔗 squareword.org 🧩 #1601 🥳 8 ⏱️ 0:02:06.799359
- 🔗 cemantle.certitudes.org 🧩 #1538 🥳 231 ⏱️ 0:03:00.529360
- 🔗 cemantix.certitudes.org 🧩 #1571 🥳 147 ⏱️ 0:02:11.431365

# Dev

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











# [spaceword.org](spaceword.org) 🧩 2026-06-19 🏁 score 2173 ranked 10.4% 31/299 ⏱️ 2:50:44.191798

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 31/299

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ I _ W _ _ B E A K   
      _ O D E U M _ _ T I   
      _ N _ T H I E V E D   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #595 🥳 22 ⏱️ 0:00:31.334067

🤔 22 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199762 [199762] lijm      q0  ? ␅
    @+199762 [199762] lijm      q1  ? after
    @+299625 [299625] schub     q2  ? ␅
    @+299625 [299625] schub     q3  ? after
    @+349387 [349387] vakantie  q4  ? ␅
    @+349387 [349387] vakantie  q5  ? after
    @+374127 [374127] vrij      q6  ? ␅
    @+374127 [374127] vrij      q7  ? after
    @+386664 [386664] wind      q8  ? ␅
    @+386664 [386664] wind      q9  ? after
    @+388254 [388254] woest     q14 ? ␅
    @+388254 [388254] woest     q15 ? after
    @+388332 [388332] wol       q18 ? ␅
    @+388332 [388332] wol       q19 ? after
    @+388613 [388613] wonder    q20 ? ␅
    @+388613 [388613] wonder    q21 ? it
    @+388613 [388613] wonder    done. it
    @+388926 [388926] woon      q16 ? ␅
    @+388926 [388926] woon      q17 ? before
    @+389873 [389873] wrik      q12 ? ␅
    @+389873 [389873] wrik      q13 ? before
    @+393081 [393081] zelfmoord q10 ? ␅
    @+393081 [393081] zelfmoord q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1062 🥳 26 ⏱️ 0:00:31.504949

🤔 26 attempts
📜 1 sessions

    @        [     0] aa     
    @+1      [     1] aah    
    @+2      [     2] aahed  
    @+3      [     3] aahing 
    @+98214  [ 98214] mach   q0  ? ␅
    @+98214  [ 98214] mach   q1  ? after
    @+147364 [147364] rhotic q2  ? ␅
    @+147364 [147364] rhotic q3  ? after
    @+159481 [159481] slop   q6  ? ␅
    @+159481 [159481] slop   q7  ? after
    @+165523 [165523] stick  q8  ? ␅
    @+165523 [165523] stick  q9  ? after
    @+168575 [168575] sue    q10 ? ␅
    @+168575 [168575] sue    q11 ? after
    @+170082 [170082] surf   q12 ? ␅
    @+170082 [170082] surf   q13 ? after
    @+170466 [170466] swamp  q16 ? ␅
    @+170466 [170466] swamp  q17 ? after
    @+170551 [170551] swash  q20 ? ␅
    @+170551 [170551] swash  q21 ? after
    @+170595 [170595] swear  q22 ? ␅
    @+170595 [170595] swear  q23 ? after
    @+170603 [170603] sweat  q24 ? ␅
    @+170603 [170603] sweat  q25 ? it
    @+170603 [170603] sweat  done. it
    @+170653 [170653] sweet  q18 ? ␅
    @+170653 [170653] sweet  q19 ? before
    @+170855 [170855] switch q14 ? ␅
    @+170855 [170855] switch q15 ? before
    @+171634 [171634] ta     q4  ? ␅
    @+171634 [171634] ta     q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1488 🥳 6 ⏱️ 0:01:14.616317

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:NANNA n n n n n remain:5978
    ⬜⬜⬜⬜⬜ tried:JUKUS n n n n n remain:1953
    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:871
    ⬜⬜⬜⬜⬜ tried:MYRRH n n n n n remain:166
    ⬜🟨⬜⬜⬜ tried:BOFFO n m n n n remain:20
    ⬜🟨🟨⬜⬜ tried:GLOGG n m m n n remain:3

    Undos used: 2

      3 words remaining
    x 8 unused letters
    = 24 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1631 🥳 17 ⏱️ 0:03:27.744620

📜 2 sessions
💰 score: 9900

    5/6
    RAGES 🟨🟩⬜🟩⬜
    LATER ⬜🟩🟩🟩🟩
    HATER ⬜🟩🟩🟩🟩
    WATER ⬜🟩🟩🟩🟩
    EATER 🟩🟩🟩🟩🟩
    3/6
    EATER 🟩⬜🟨🟨⬜
    ETICS 🟩🟨⬜⬜⬜
    EVENT 🟩🟩🟩🟩🟩
    4/6
    EVENT ⬜⬜⬜⬜🟨
    TACOS 🟩⬜⬜🟩⬜
    THROB 🟩🟩🟩🟩⬜
    THROW 🟩🟩🟩🟩🟩
    3/6
    THROW 🟨⬜⬜🟩⬜
    MAGOT ⬜⬜⬜🟩🟨
    EXTOL 🟩🟩🟩🟩🟩
    Final 2/2
    CRASH ⬜🟨🟨⬜🟨
    HYDRA 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1608 🥳 score:19 ⏱️ 0:01:26.741853

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SLAIN attempts:3 score:3
2. TAMER attempts:7 score:7
3. VIPER attempts:4 score:4
4. FALSE attempts:5 score:5

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1608 🥳 score:58 ⏱️ 0:03:51.603180

📜 3 sessions

Octordle Classic

1. CHOCK attempts:10 score:10
2. NADIR attempts:7 score:7
3. RIPEN attempts:8 score:8
4. CHEAT attempts:6 score:6
5. THIEF attempts:3 score:3
6. STUFF attempts:4 score:4
7. OUNCE attempts:9 score:9
8. ROGUE attempts:11 score:11

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1588 🥳 score:53 ⏱️ 0:13:46.816997

📜 2 sessions

Sedecordle Classic sedecordle.com

1. BERTH attempts:12 score:1
2. BAGGY attempts:9 score:2
3. SHALE attempts:18 score:1
4. POSER attempts:19 score:8
5. QUIRK attempts:17 score:1
6. LEERY attempts:4 score:7
7. FLUNG attempts:5 score:0
8. FLYER attempts:6 score:5
9. BEGET attempts:16 score:1
10. BUNNY attempts:10 score:6
11. POLKA attempts:15 score:1
12. GLEAM attempts:11 score:5
13. QUEER attempts:8 score:0
14. JETTY attempts:14 score:8
15. GROWN attempts:7 score:0
16. SPECK attempts:13 score:7

# [squareword.org](squareword.org) 🧩 #1601 🥳 8 ⏱️ 0:02:06.799359

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟩 🟨 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    O P A L S
    C R O O N
    T U R B O
    E N T E R
    T E A S E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1538 🥳 231 ⏱️ 0:03:00.529360

🤔 232 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 48 chat prompts
🤖 48 dolphin3:latest replies
🥵   5 😎  25 🥶 193 🧊   8

      $1 #232 equivalent       100.00°C 🥳 1000‰ ~224 used:0  [223]  source:dolphin3
      $2 #174 total             39.67°C 🥵  986‰  ~17 used:15 [16]   source:dolphin3
      $3 #121 less              36.62°C 🥵  976‰  ~28 used:30 [27]   source:dolphin3
      $4  #99 worth             36.30°C 🥵  972‰  ~27 used:24 [26]   source:dolphin3
      $5 #160 fraction          35.74°C 🥵  970‰   ~2 used:10 [1]    source:dolphin3
      $6 #194 proportional      32.25°C 🥵  936‰   ~1 used:7  [0]    source:dolphin3
      $7 #200 proportionate     30.42°C 😎  891‰   ~3 used:0  [2]    source:dolphin3
      $8  #59 reduced           29.93°C 😎  875‰  ~30 used:9  [29]   source:dolphin3
      $9 #226 calculation       29.44°C 😎  856‰   ~4 used:0  [3]    source:dolphin3
     $10 #222 reduction         28.67°C 😎  810‰   ~5 used:0  [4]    source:dolphin3
     $11 #134 amount            28.36°C 😎  787‰  ~18 used:2  [17]   source:dolphin3
     $12  #64 decreased         28.32°C 😎  783‰  ~29 used:6  [28]   source:dolphin3
     $32 #196 comparative       22.00°C 🥶        ~35 used:0  [34]   source:dolphin3
    $225 #148 design            -0.09°C 🧊       ~225 used:0  [224]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1571 🥳 147 ⏱️ 0:02:11.431365

🤔 148 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 27 chat prompts
🤖 27 dolphin3:latest replies
🔥   2 🥵   1 😎  12 🥶 120 🧊  12

      $1 #148 bête          100.00°C 🥳 1000‰ ~136 used:0  [135]  source:dolphin3
      $2 #144 idiot          48.26°C 🔥  992‰   ~2 used:4  [1]    source:dolphin3
      $3 #147 fou            48.22°C 🔥  991‰   ~1 used:2  [0]    source:dolphin3
      $4 #117 bébête         45.70°C 🥵  975‰   ~3 used:6  [2]    source:dolphin3
      $5 #124 rire           38.87°C 😎  767‰   ~8 used:3  [7]    source:dolphin3
      $6 #141 crétin         37.18°C 😎  640‰   ~4 used:0  [3]    source:dolphin3
      $7 #112 sauterelle     36.77°C 😎  604‰  ~11 used:5  [10]   source:dolphin3
      $8 #115 gamin          36.55°C 😎  575‰   ~9 used:3  [8]    source:dolphin3
      $9 #146 benêt          35.52°C 😎  456‰   ~5 used:0  [4]    source:dolphin3
     $10  #61 oiselle        34.71°C 😎  356‰  ~15 used:12 [14]   source:dolphin3
     $11 #145 abruti         34.52°C 😎  321‰   ~6 used:0  [5]    source:dolphin3
     $12  #98 grenouille     34.47°C 😎  311‰  ~10 used:3  [9]    source:dolphin3
     $17  #19 oiseau         32.70°C 🥶        ~16 used:8  [15]   source:dolphin3
    $137 #143 démenti        -0.07°C 🧊       ~137 used:0  [136]  source:dolphin3
