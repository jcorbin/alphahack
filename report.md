# 2026-09-04

- 🔗 spaceword.org 🧩 2026-09-03 🏁 score 2165 ranked 42.6% 155/364 ⏱️ 0:03:57.197233
- 🔗 wordgrid 🧩 #825 🟪 rarity:0.23 ⏱️ 0:02:05.941297
- 🔗 alfagok.diginaut.net 🧩 #671 🥳 38 ⏱️ 0:00:42.405693
- 🔗 alphaguess.com 🧩 #1138 🥳 30 ⏱️ 0:00:36.942045
- 🔗 dontwordle.com 🧩 #1564 🥳 6 ⏱️ 0:03:06.219270
- 🔗 dictionary.com hurdle 🧩 #1707 🥳 20 ⏱️ 0:12:03.539632
- 🔗 Quordle Classic 🧩 #1684 🥳 score:24 ⏱️ 0:01:12.403058
- 🔗 Octordle Classic 🧩 #1684 🥳 score:53 ⏱️ 0:02:33.928734
- 🔗 Sedecordle Classic 🧩 #1664 🥳 score:43 ⏱️ 0:03:01.380908
- 🔗 squareword.org 🧩 #1677 🥳 8 ⏱️ 0:02:35.628297
- 🔗 cemantle.certitudes.org 🧩 #1614 🥳 186 ⏱️ 0:02:16.621446
- 🔗 cemantix.certitudes.org 🧩 #1647 🥳 40 ⏱️ 0:00:37.637728

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































# [spaceword.org](spaceword.org) 🧩 2026-09-03 🏁 score 2165 ranked 42.6% 155/364 ⏱️ 0:03:57.197233

📜 4 sessions
- tiles: 21/21
- score: 2165 bonus: +65
- rank: 155/364

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ T _ Q _ _ _   
      _ _ _ Y E _ U P _ _   
      _ _ Z A I K A I S _   
      _ _ A G N A I L _ _   
      _ _ _ _ D _ _ E _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #825 🟪 rarity:0.23 ⏱️ 0:02:05.941297

📜 2 sessions
🌌 🌌 🌌
🦄 🦄 🦄
🦄 🦄 🦄
Rarity: 0.23 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #671 🥳 38 ⏱️ 0:00:42.405693

🤔 38 attempts
📜 1 sessions

    @       [    0] &-teken            
    @+24880 [24880] bad                q8  ? ␅
    @+24880 [24880] bad                q9  ? after
    @+31106 [31106] begeleiding        q12 ? ␅
    @+31106 [31106] begeleiding        q13 ? after
    @+31453 [31453] begrafenis         q20 ? ␅
    @+31453 [31453] begrafenis         q21 ? after
    @+31604 [31604] begroting          q22 ? ␅
    @+31604 [31604] begroting          q23 ? after
    @+31708 [31708] begrotingssanering q24 ? ␅
    @+31708 [31708] begrotingssanering q25 ? after
    @+31757 [31757] behaaglijk         q26 ? ␅
    @+31757 [31757] behaaglijk         q27 ? after
    @+31784 [31784] behagen            q28 ? ␅
    @+31784 [31784] behagen            q29 ? after
    @+31787 [31787] behalen            q32 ? ␅
    @+31787 [31787] behalen            q33 ? after
    @+31789 [31789] behalende          q34 ? ␅
    @+31789 [31789] behalende          q35 ? after
    @+31790 [31790] behalve            q36 ? ␅
    @+31790 [31790] behalve            q37 ? it
    @+31790 [31790] behalve            done. it
    @+31791 [31791] behandel           q30 ? ␅
    @+31791 [31791] behandel           q31 ? before
    @+31812 [31812] behandeld          q18 ? ␅
    @+31812 [31812] behandeld          q19 ? before
    @+32524 [32524] bejaarden          q16 ? ␅
    @+32524 [32524] bejaarden          q17 ? before
    @+33979 [33979] beleid             q14 ? ␅
    @+33979 [33979] beleid             q15 ? before
    @+37341 [37341] beschermen         q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1138 🥳 30 ⏱️ 0:00:36.942045

🤔 30 attempts
📜 1 sessions

    @       [    0] aa         
    @+23680 [23680] camp       q8  ? ␅
    @+23680 [23680] camp       q9  ? after
    @+35522 [35522] convention q10 ? ␅
    @+35522 [35522] convention q11 ? after
    @+36088 [36088] cor        q18 ? ␅
    @+36088 [36088] cor        q19 ? after
    @+36129 [36129] cord       q24 ? ␅
    @+36129 [36129] cord       q25 ? after
    @+36178 [36178] cordwain   q26 ? ␅
    @+36178 [36178] cordwain   q27 ? after
    @+36186 [36186] core       q28 ? ␅
    @+36186 [36186] core       q29 ? it
    @+36186 [36186] core       done. it
    @+36235 [36235] cork       q22 ? ␅
    @+36235 [36235] cork       q23 ? before
    @+36399 [36399] corona     q20 ? ␅
    @+36399 [36399] corona     q21 ? before
    @+36723 [36723] cos        q16 ? ␅
    @+36723 [36723] cos        q17 ? before
    @+38181 [38181] crazy      q14 ? ␅
    @+38181 [38181] crazy      q15 ? before
    @+40838 [40838] da         q12 ? ␅
    @+40838 [40838] da         q13 ? before
    @+47378 [47378] dis        q6  ? ␅
    @+47378 [47378] dis        q7  ? before
    @+98147 [98147] mac        q1  ? after
    @+98147 [98147] mac        q2  ? ␅
    @+98147 [98147] mac        q3  ? after
    @+98147 [98147] mac        q4  ? ␅
    @+98147 [98147] mac        q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1564 🥳 6 ⏱️ 0:03:06.219270

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:XEBEC n n n n n remain:5141
    ⬜⬜⬜⬜⬜ tried:SLYLY n n n n n remain:1161
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:507
    ⬜⬜🟨⬜⬜ tried:KNURR n n m n n remain:25
    ⬜🟩⬜⬜⬜ tried:JUGUM n Y n n n remain:6
    ⬜🟩🟨⬜⬜ tried:QUIFF n Y m n n remain:1

    Undos used: 3

      1 words remaining
    x 6 unused letters
    = 6 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1707 🥳 20 ⏱️ 0:12:03.539632

📜 1 sessions
💰 score: 9600

    3/6
    STARE 🟩🟩🟩⬜⬜
    STANG 🟩🟩🟩🟨⬜
    STAIN 🟩🟩🟩🟩🟩
    6/6
    STAIN ⬜🟨🟨⬜⬜
    GATER ⬜🟩🟩⬜⬜
    MATCH ⬜🟩🟩🟩🟩
    BICEP ⬜⬜🟨⬜⬜
    WELCH ⬜⬜⬜🟩🟩
    CATCH 🟩🟩🟩🟩🟩
    3/6
    CATCH 🟩🟨🟨⬜⬜
    COAST 🟩🟩🟩⬜🟨
    COATI 🟩🟩🟩🟩🟩
    6/6
    COATI ⬜⬜⬜⬜🟨
    SNIDE ⬜⬜🟨🟨🟨
    IDLER 🟨🟨⬜🟩🟩
    BOKEH ⬜⬜⬜🟩⬜
    WOVEN ⬜⬜🟩🟩⬜
    DIVER 🟩🟩🟩🟩🟩
    Final 2/2
    FLUMP ⬜⬜⬜🟨⬜
    AMAZE 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1684 🥳 score:24 ⏱️ 0:01:12.403058

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. QUICK attempts:6 score:6
2. BEEFY attempts:7 score:7
3. TRUCK attempts:8 score:8
4. SNAIL attempts:3 score:3

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1684 🥳 score:53 ⏱️ 0:02:33.928734

📜 1 sessions

Octordle Classic

1. DETOX attempts:8 score:8
2. KNEEL attempts:11 score:11
3. MEDAL attempts:4 score:4
4. BLURT attempts:7 score:7
5. MAYOR attempts:5 score:5
6. AMUSE attempts:6 score:6
7. YOUTH attempts:9 score:9
8. TARDY attempts:3 score:3

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1664 🥳 score:43 ⏱️ 0:03:01.380908

📜 1 sessions

Sedecordle Classic sedecordle.com

1. BLESS attempts:6 score:0
2. CLASH attempts:5 score:6
3. SUING attempts:11 score:1
4. SPIRE attempts:8 score:1
5. LEDGE attempts:7 score:0
6. DADDY attempts:19 score:7
7. GIVEN attempts:9 score:0
8. PLUMB attempts:10 score:9
9. TATTY attempts:12 score:1
10. PUPPY attempts:13 score:2
11. COYLY attempts:20 score:2
12. SNUFF attempts:14 score:0
13. MISSY attempts:15 score:1
14. MOTEL attempts:16 score:5
15. CRACK attempts:17 score:1
16. KHAKI attempts:18 score:7

# [squareword.org](squareword.org) 🧩 #1677 🥳 8 ⏱️ 0:02:35.628297

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T R U T
    E R A S E
    P A G A N
    I M A G E
    A S S E T

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1614 🥳 186 ⏱️ 0:02:16.621446

🤔 187 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 36 chat prompts
🤖 36 dolphin3:latest replies
😱   1 🔥   4 🥵   4 😎  17 🥶 142 🧊  18

      $1 #187 inquiry          100.00°C 🥳 1000‰ ~169 used:0  [168]  source:dolphin3
      $2 #185 investigation     78.02°C 😱  999‰   ~1 used:0  [0]    source:dolphin3
      $3 #181 probe             74.76°C 🔥  998‰   ~4 used:8  [3]    source:dolphin3
      $4 #164 investigate       50.64°C 🔥  995‰   ~5 used:10 [4]    source:dolphin3
      $5 #172 probing           49.91°C 🔥  994‰   ~3 used:7  [2]    source:dolphin3
      $6 #183 review            46.90°C 🔥  991‰   ~2 used:1  [1]    source:dolphin3
      $7 #175 investigator      40.60°C 🥵  985‰   ~6 used:1  [5]    source:dolphin3
      $8 #178 scrutiny          37.90°C 🥵  976‰   ~7 used:0  [6]    source:dolphin3
      $9 #162 inquire           35.97°C 🥵  970‰   ~8 used:1  [7]    source:dolphin3
     $10 #169 examine           33.53°C 🥵  954‰   ~9 used:0  [8]    source:dolphin3
     $11  #70 relation          28.63°C 😎  892‰  ~25 used:11 [24]   source:dolphin3
     $12 #177 scrutinize        28.25°C 😎  883‰  ~10 used:0  [9]    source:dolphin3
     $28 #112 document          16.96°C 🥶        ~34 used:0  [33]   source:dolphin3
    $170  #62 blastoff          -0.11°C 🧊       ~170 used:0  [169]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1647 🥳 40 ⏱️ 0:00:37.637728

🤔 41 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 7 chat prompts
🤖 7 dolphin3:latest replies
🥵  2 😎  6 🥶 22 🧊 10

     $1 #41 clôture    100.00°C 🥳 1000‰ ~31 used:0 [30]  source:dolphin3
     $2 #23 haie        27.57°C 🥵  951‰  ~2 used:3 [1]   source:dolphin3
     $3 #33 pergola     25.37°C 🥵  905‰  ~1 used:0 [0]   source:dolphin3
     $4 #30 barrière    22.02°C 😎  781‰  ~3 used:1 [2]   source:dolphin3
     $5 #36 salle       20.81°C 😎  705‰  ~4 used:0 [3]   source:dolphin3
     $6 #29 mur         18.81°C 😎  514‰  ~7 used:2 [6]   source:dolphin3
     $7 #38 terrain     18.78°C 😎  511‰  ~5 used:0 [4]   source:dolphin3
     $8 #32 grille      15.91°C 😎   95‰  ~6 used:0 [5]   source:dolphin3
     $9 #20 bordure     15.66°C 😎   43‰  ~8 used:3 [7]   source:dolphin3
    $10 #12 parc        14.92°C 🥶        ~9 used:4 [8]   source:dolphin3
    $11  #4 jardin      14.33°C 🥶       ~10 used:2 [9]   source:dolphin3
    $12 #18 terrasse    13.77°C 🥶       ~11 used:0 [10]  source:dolphin3
    $13 #19 allée       13.41°C 🥶       ~12 used:0 [11]  source:dolphin3
    $32  #1 café        -2.29°C 🧊       ~32 used:0 [31]  source:dolphin3
