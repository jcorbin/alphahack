# 2026-10-12

- 🔗 spaceword.org 🧩 2026-10-11 🏁 score 2168 ranked 54.2% 168/310 ⏱️ 0:20:14.420058
- 🔗 wordgrid 🧩 #863 🟪 rarity:0.26 ⏱️ 0:02:18.884939
- 🔗 alfagok.diginaut.net 🧩 #709 🥳 16 ⏱️ 0:00:45.689977
- 🔗 alphaguess.com 🧩 #1176 🥳 30 ⏱️ 0:00:39.371267
- 🔗 dontwordle.com 🧩 #1602 🥳 6 ⏱️ 0:01:21.100687
- 🔗 dictionary.com hurdle 🧩 #1745 🥳 19 ⏱️ 0:03:50.777611
- 🔗 cemantix.certitudes.org 🧩 #1685 🥳 330 ⏱️ 0:26:49.750940
- 🔗 cemantle.certitudes.org 🧩 #1652 🥳 168 ⏱️ 0:14:06.694961
- 🔗 Quordle Classic 🧩 #1722 🥳 score:20 ⏱️ 0:01:22.409064
- 🔗 Octordle Classic 🧩 #1722 🥳 score:63 ⏱️ 0:01:38.751147
- 🔗 Sedecordle Classic 🧩 #1702 🥳 score:44 ⏱️ 0:03:49.318775
- 🔗 squareword.org 🧩 #1715 🥳 7 ⏱️ 0:02:02.867579

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








# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #863 🟪 rarity:0.26 ⏱️ 0:02:18.884939

📜 2 sessions
🦄 🌌 🌌
🌌 🌌 🦄
🌌 🌌 🦄
Rarity: 0.26 🟪

# [spaceword.org](spaceword.org) 🧩 2026-10-11 🏁 score 2168 ranked 54.2% 168/310 ⏱️ 0:20:14.420058

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 168/310

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ E L _ _ _ _ _ O _   
      _ T O _ _ _ J _ A _   
      _ A G O U T I _ K _   
      _ S _ W H I N E Y _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #709 🥳 16 ⏱️ 0:00:45.689977

🤔 16 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199528 [199528] lij       q0  ? ␅
    @+199528 [199528] lij       q1  ? after
    @+299479 [299479] schrok    q2  ? ␅
    @+299479 [299479] schrok    q3  ? after
    @+311720 [311720] spier     q8  ? ␅
    @+311720 [311720] spier     q9  ? after
    @+313075 [313075] sport     q14 ? ␅
    @+313075 [313075] sport     q15 ? it
    @+313075 [313075] sport     done. it
    @+314811 [314811] staatse   q12 ? ␅
    @+314811 [314811] staatse   q13 ? before
    @+317912 [317912] stem      q10 ? ␅
    @+317912 [317912] stem      q11 ? before
    @+324114 [324114] sub       q6  ? ␅
    @+324114 [324114] sub       q7  ? before
    @+349463 [349463] vakanties q4  ? ␅
    @+349463 [349463] vakanties q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1176 🥳 30 ⏱️ 0:00:39.371267

🤔 30 attempts
📜 1 sessions

    @        [     0] aa        
    @+98142  [ 98142] mac       q0  ? ␅
    @+98142  [ 98142] mac       q1  ? after
    @+122718 [122718] parol     q4  ? ␅
    @+122718 [122718] parol     q5  ? after
    @+134997 [134997] prop      q6  ? ␅
    @+134997 [134997] prop      q7  ? after
    @+138003 [138003] quetzal   q10 ? ␅
    @+138003 [138003] quetzal   q11 ? after
    @+139503 [139503] rate      q12 ? ␅
    @+139503 [139503] rate      q13 ? after
    @+139516 [139516] ratfink   q22 ? ␅
    @+139516 [139516] ratfink   q23 ? after
    @+139520 [139520] rath      q24 ? ␅
    @+139520 [139520] rath      q25 ? after
    @+139522 [139522] rather    q28 ? ␅
    @+139522 [139522] rather    q29 ? it
    @+139522 [139522] rather    done. it
    @+139524 [139524] ratholes  q26 ? ␅
    @+139524 [139524] ratholes  q27 ? before
    @+139528 [139528] raticides q20 ? ␅
    @+139528 [139528] raticides q21 ? before
    @+139552 [139552] ration    q18 ? ␅
    @+139552 [139552] ration    q19 ? before
    @+139654 [139654] raucous   q16 ? ␅
    @+139654 [139654] raucous   q17 ? before
    @+139807 [139807] re        q14 ? ␅
    @+139807 [139807] re        q15 ? before
    @+141010 [141010] recon     q8  ? ␅
    @+141010 [141010] recon     q9  ? before
    @+147304 [147304] rho       q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1602 🥳 6 ⏱️ 0:01:21.100687

📜 1 sessions
💰 score: 63

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:ADDAX n n n n n remain:6032
    ⬜⬜⬜⬜⬜ tried:YOBBO n n n n n remain:2541
    ⬜⬜⬜⬜⬜ tried:JUGUM n n n n n remain:1299
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:509
    ⬜⬜🟩⬜⬜ tried:FRIZZ n n Y n n remain:39
    🟩⬜🟩⬜⬜ tried:SWISS Y n Y n n remain:9

    Undos used: 3

      9 words remaining
    x 7 unused letters
    = 63 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1745 🥳 19 ⏱️ 0:03:50.777611

📜 1 sessions
💰 score: 9700

    6/6
    ALOES ⬜⬜⬜🟩⬜
    TRIED ⬜🟨🟨🟩⬜
    FINER ⬜🟩⬜🟩🟩
    CALIX ⬜⬜⬜🟨⬜
    VIPER 🟨🟩⬜🟩🟩
    GIVER 🟩🟩🟩🟩🟩
    5/6
    GIVER 🟩⬜⬜⬜⬜
    GOALS 🟩⬜🟨⬜⬜
    GAMUT 🟩🟩🟩⬜⬜
    ABACK 🟨⬜🟨⬜⬜
    GAMMA 🟩🟩🟩🟩🟩
    4/6
    GAMMA ⬜🟩⬜⬜⬜
    DARES ⬜🟩🟨⬜🟨
    RASPY 🟨🟩🟨⬜⬜
    SAVOR 🟩🟩🟩🟩🟩
    3/6
    SAVOR ⬜⬜⬜⬜🟨
    LURID ⬜🟨🟨🟩🟩
    DRUID 🟩🟩🟩🟩🟩
    Final 1/2
    UPEND 🟩🟩🟩🟩🟩

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1685 🥳 330 ⏱️ 0:26:49.750940

🤔 331 attempts
📜 1 sessions
🫧 24 chat sessions
⁉️ 124 chat prompts
🤖 21 gemma4:12b replies
🤖 103 dolphin3:latest replies
😱   1 🔥   4 🥵  11 😎  44 🥶 168 🧊 102

      $1 #331 tournée          100.00°C 🥳 1000‰ ~229 used:0   [228]  source:gemma4  
      $2  #25 concert           59.61°C 😱  999‰   ~1 used:192 [0]    source:dolphin3
      $3 #167 medley            45.21°C 🔥  995‰  ~14 used:53  [13]   source:dolphin3
      $4  #84 live              43.00°C 🔥  992‰  ~12 used:39  [11]   source:dolphin3
      $5  #63 album             42.94°C 🔥  991‰   ~3 used:25  [2]    source:dolphin3
      $6 #169 single            41.14°C 🔥  990‰   ~2 used:23  [1]    source:dolphin3
      $7  #24 festival          39.61°C 🥵  986‰  ~16 used:10  [15]   source:dolphin3
      $8  #41 show              39.56°C 🥵  985‰  ~13 used:4   [12]   source:dolphin3
      $9  #34 spectacle         38.76°C 🥵  984‰   ~4 used:3   [3]    source:dolphin3
     $10 #151 récital           37.74°C 🥵  982‰   ~5 used:3   [4]    source:dolphin3
     $11  #11 chanson           36.24°C 🥵  976‰  ~15 used:8   [14]   source:dolphin3
     $18 #243 jazzman           28.24°C 😎  878‰  ~17 used:0   [16]   source:dolphin3
     $62 #107 vinyl             17.22°C 🥶        ~61 used:0   [60]   source:dolphin3
    $230 #117 direct            -0.04°C 🧊       ~230 used:0   [229]  source:dolphin3

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1652 🥳 168 ⏱️ 0:14:06.694961

🤔 169 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 38 chat prompts
🤖 38 gemma4:12b replies
🔥   1 🥵  15 😎  35 🥶 111 🧊   6

      $1 #169 assure         100.00°C 🥳 1000‰ ~163 used:0  [162]  source:gemma4
      $2 #133 safeguard       52.57°C 🔥  993‰   ~5 used:13 [4]    source:gemma4
      $3 #131 protect         47.62°C 🥵  987‰  ~11 used:6  [10]   source:gemma4
      $4 #109 maintain        47.59°C 🥵  986‰  ~12 used:6  [11]   source:gemma4
      $5 #128 secure          44.94°C 🥵  980‰   ~6 used:2  [5]    source:gemma4
      $6  #65 facilitate      42.04°C 🥵  971‰  ~46 used:17 [45]   source:gemma4
      $7 #158 attest          41.21°C 🥵  964‰   ~7 used:2  [6]    source:gemma4
      $8 #125 verify          38.54°C 🥵  948‰   ~8 used:2  [7]    source:gemma4
      $9 #110 affirm          38.32°C 🥵  942‰   ~1 used:0  [0]    source:gemma4
     $10  #93 encourage       38.18°C 🥵  940‰  ~13 used:8  [12]   source:gemma4
     $11 #113 certify         37.88°C 🥵  935‰   ~9 used:2  [8]    source:gemma4
     $18  #95 strengthen      35.52°C 😎  895‰  ~15 used:0  [14]   source:gemma4
     $53  #55 agitate         22.94°C 🥶        ~56 used:0  [55]   source:gemma4
    $164 #111 anchor          -0.28°C 🧊       ~164 used:0  [163]  source:gemma4

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1722 🥳 score:20 ⏱️ 0:01:22.409064

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. HELLO attempts:7 score:7
2. BELOW attempts:3 score:3
3. RIGHT attempts:6 score:6
4. SLANT attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1722 🥳 score:63 ⏱️ 0:01:38.751147

📜 1 sessions

Octordle Classic

1. PROSE attempts:8 score:8
2. TIPSY attempts:4 score:4
3. BLAND attempts:10 score:10
4. FROND attempts:11 score:12
5. RAZOR attempts:7 score:7
6. WALTZ attempts:6 score:6
7. GAMUT attempts:5 score:5
8. PINKY attempts:11 score:11

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1702 🥳 score:44 ⏱️ 0:03:49.318775

📜 2 sessions

Sedecordle Classic sedecordle.com

1. MANOR attempts:18 score:1
2. SLEPT attempts:17 score:8
3. GUAVA attempts:7 score:0
4. CANOE attempts:16 score:7
5. OFFAL attempts:6 score:0
6. SPINE attempts:15 score:6
7. BEECH attempts:14 score:1
8. RIVET attempts:4 score:4
9. REFER attempts:13 score:1
10. PARTY attempts:9 score:3
11. TRASH attempts:3 score:0
12. ENNUI attempts:12 score:3
13. STING attempts:8 score:0
14. FILTH attempts:5 score:8
15. AWOKE attempts:11 score:1
16. DAILY attempts:10 score:1

# [squareword.org](squareword.org) 🧩 #1715 🥳 7 ⏱️ 0:02:02.867579

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    R A F T S
    A G L O W
    D R O N E
    A E R I E
    R E A C T
