# 2026-06-07

- 🔗 spaceword.org 🧩 2026-06-06 🏁 score 2168 ranked 45.5% 142/312 ⏱️ 2:38:47.360753
- 🔗 alfagok.diginaut.net 🧩 #582 🥳 38 ⏱️ 0:00:36.767891
- 🔗 alphaguess.com 🧩 #1049 🥳 26 ⏱️ 0:00:26.271440
- 🔗 dontwordle.com 🧩 #1475 🥳 6 ⏱️ 0:01:49.582449
- 🔗 dictionary.com hurdle 🧩 #1618 🥳 20 ⏱️ 0:03:30.377392
- 🔗 Quordle Classic 🧩 #1595 🥳 score:27 ⏱️ 0:01:44.671930
- 🔗 Octordle Classic 🧩 #1595 🥳 score:53 ⏱️ 0:03:06.017661
- 🔗 squareword.org 🧩 #1588 🥳 6 ⏱️ 0:01:41.304008
- 🔗 cemantle.certitudes.org 🧩 #1525 🥳 135 ⏱️ 0:00:51.005689
- 🔗 cemantix.certitudes.org 🧩 #1558 😦 430 ⏱️ 9:46:06.026609

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
























































































# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1585 😦 score:32 ⏱️ 0:02:33.513959

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. GRAPE attempts:8 score:8
2. VALUE attempts:9 score:9
3. YEARN attempts:6 score:6
4. IN_ER -ACDGHLMPSTUVWYZ attempts:9 score:-1











# [spaceword.org](spaceword.org) 🧩 2026-06-06 🏁 score 2168 ranked 45.5% 142/312 ⏱️ 2:38:47.360753

📜 5 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 142/312

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ G O T _ _ _ _   
      _ _ _ A _ U _ _ _ _   
      _ _ _ P O X _ _ _ _   
      _ _ _ _ B E _ _ _ _   
      _ _ _ R E D _ _ _ _   
      _ _ _ _ L O W _ _ _   
      _ _ _ _ I _ _ _ _ _   
      _ _ _ Q A I D _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #582 🥳 38 ⏱️ 0:00:36.767891

🤔 38 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+199766 [199766] lijm      q0  ? ␅
    @+199766 [199766] lijm      q1  ? after
    @+199766 [199766] lijm      q2  ? ␅
    @+199766 [199766] lijm      q3  ? after
    @+299634 [299634] schub     q4  ? ␅
    @+299634 [299634] schub     q5  ? after
    @+349396 [349396] vakantie  q6  ? ␅
    @+349396 [349396] vakantie  q7  ? after
    @+374136 [374136] vrij      q8  ? ␅
    @+374136 [374136] vrij      q9  ? after
    @+386673 [386673] wind      q10 ? ␅
    @+386673 [386673] wind      q11 ? after
    @+393090 [393090] zelfmoord q12 ? ␅
    @+393090 [393090] zelfmoord q13 ? after
    @+394591 [394591] zien      q16 ? ␅
    @+394591 [394591] zien      q17 ? after
    @+395343 [395343] zit       q18 ? ␅
    @+395343 [395343] zit       q19 ? after
    @+395407 [395407] zitting   q24 ? ␅
    @+395407 [395407] zitting   q25 ? after
    @+395445 [395445] zmlk      q26 ? ␅
    @+395445 [395445] zmlk      q27 ? after
    @+395450 [395450] zo        q30 ? ␅
    @+395450 [395450] zo        q31 ? after
    @+395455 [395455] zocht     q32 ? ␅
    @+395455 [395455] zocht     q33 ? after
    @+395457 [395457] zodanig   q36 ? ␅
    @+395457 [395457] zodanig   q37 ? it
    @+395457 [395457] zodanig   done. it
    @+395458 [395458] zodanige  q35 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1049 🥳 26 ⏱️ 0:00:26.271440

🤔 26 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+23681 [23681] camp       q6  ? ␅
    @+23681 [23681] camp       q7  ? after
    @+35524 [35524] convention q8  ? ␅
    @+35524 [35524] convention q9  ? after
    @+38183 [38183] crazy      q12 ? ␅
    @+38183 [38183] crazy      q13 ? after
    @+39501 [39501] cud        q14 ? ␅
    @+39501 [39501] cud        q15 ? after
    @+39772 [39772] cup        q18 ? ␅
    @+39772 [39772] cup        q19 ? after
    @+39959 [39959] curl       q20 ? ␅
    @+39959 [39959] curl       q21 ? after
    @+40060 [40060] curt       q22 ? ␅
    @+40060 [40060] curt       q23 ? after
    @+40103 [40103] curve      q24 ? ␅
    @+40103 [40103] curve      q25 ? it
    @+40103 [40103] curve      done. it
    @+40167 [40167] cuss       q16 ? ␅
    @+40167 [40167] cuss       q17 ? before
    @+40840 [40840] da         q10 ? ␅
    @+40840 [40840] da         q11 ? before
    @+47380 [47380] dis        q4  ? ␅
    @+47380 [47380] dis        q5  ? before
    @+98214 [98214] mach       q0  ? ␅
    @+98214 [98214] mach       q1  ? after
    @+98214 [98214] mach       q2  ? ␅
    @+98214 [98214] mach       q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1475 🥳 6 ⏱️ 0:01:49.582449

📜 2 sessions
💰 score: 207

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:NANNA n n n n n remain:5978
    ⬜⬜⬜⬜⬜ tried:JESSE n n n n n remain:1190
    ⬜⬜⬜⬜⬜ tried:VILLI n n n n n remain:469
    ⬜⬜⬜⬜⬜ tried:TOOTH n n n n n remain:73
    ⬜⬜🟨⬜⬜ tried:CRUCK n n m n n remain:31
    ⬜🟩⬜⬜🟩 tried:BUBBY n Y n n Y remain:23

    Undos used: 4

      23 words remaining
    x 9 unused letters
    = 207 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1618 🥳 20 ⏱️ 0:03:30.377392

📜 1 sessions
💰 score: 9600

    6/6
    LARES 🟨🟨🟨⬜⬜
    GRAIL ⬜🟩🟩⬜🟩
    CRAWL ⬜🟩🟩🟩🟩
    BRAWL ⬜🟩🟩🟩🟩
    TRAWL ⬜🟩🟩🟩🟩
    DRAWL 🟩🟩🟩🟩🟩
    4/6
    DRAWL ⬜⬜🟨⬜⬜
    MANES ⬜🟨🟨⬜🟨
    ANGST 🟩🟩⬜🟩🟨
    ANTSY 🟩🟩🟩🟩🟩
    5/6
    ANTSY ⬜⬜⬜⬜⬜
    CHOIR ⬜⬜⬜⬜🟩
    LEMUR ⬜🟩🟩🟩🟩
    DEMUR ⬜🟩🟩🟩🟩
    FEMUR 🟩🟩🟩🟩🟩
    3/6
    FEMUR 🟩🟩⬜⬜⬜
    FETAL 🟩🟩⬜⬜🟨
    FELON 🟩🟩🟩🟩🟩
    Final 2/2
    FLITE 🟩🟩⬜⬜🟩
    FLEET 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1595 🥳 score:27 ⏱️ 0:01:44.671930

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. QUERY attempts:4 score:4
2. AXION attempts:8 score:8
3. LILAC attempts:6 score:6
4. SWORD attempts:9 score:9

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1595 🥳 score:53 ⏱️ 0:03:06.017661

📜 1 sessions

Octordle Classic

1. BANJO attempts:3 score:3
2. RAPID attempts:9 score:9
3. MASON attempts:4 score:4
4. STOUT attempts:11 score:11
5. SAUCY attempts:5 score:5
6. ALOFT attempts:7 score:7
7. JEWEL attempts:6 score:6
8. PLANT attempts:8 score:8

# [squareword.org](squareword.org) 🧩 #1588 🥳 6 ⏱️ 0:01:41.304008

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S A G A S
    T U L I P
    A R O S E
    T A B L A
    S L E E K

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1525 🥳 135 ⏱️ 0:00:51.005689

🤔 136 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 14 chat prompts
🤖 14 dolphin3:latest replies
😱   1 🔥   1 🥵   9 😎  18 🥶 105 🧊   1

      $1 #136 signature        100.00°C 🥳 1000‰ ~135 used:0  [134]  source:dolphin3
      $2  #56 distinctive       45.58°C 😱  999‰   ~2 used:11 [1]    source:dolphin3
      $3 #116 authenticity      36.37°C 🔥  990‰   ~1 used:0  [0]    source:dolphin3
      $4  #93 authentic         33.74°C 🥵  979‰   ~9 used:3  [8]    source:dolphin3
      $5  #92 original          32.27°C 🥵  964‰  ~11 used:4  [10]   source:dolphin3
      $6  #49 style             32.24°C 🥵  962‰  ~10 used:3  [9]    source:dolphin3
      $7 #115 exquisite         32.03°C 🥵  959‰   ~3 used:0  [2]    source:dolphin3
      $8  #76 unique            31.81°C 🥵  955‰   ~4 used:1  [3]    source:dolphin3
      $9  #80 memorable         31.65°C 🥵  952‰   ~5 used:1  [4]    source:dolphin3
     $10  #45 motif             30.72°C 🥵  940‰   ~6 used:1  [5]    source:dolphin3
     $11  #97 groundbreaking    30.72°C 🥵  941‰   ~7 used:0  [6]    source:dolphin3
     $13 #129 flair             28.30°C 😎  873‰  ~12 used:0  [11]   source:dolphin3
     $31  #90 idiosyncratic     21.27°C 🥶        ~30 used:0  [29]   source:dolphin3
    $136  #48 section           -7.01°C 🧊       ~136 used:0  [135]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1558 😦 430 ⏱️ 9:46:06.026609

🤔 429 attempts
📜 1 sessions
🫧 35 chat sessions
⁉️ 187 chat prompts
🤖 187 dolphin3:latest replies
😦 🥵  22 😎 136 🥶 234 🧊  37

      $1 #350 pourcentage            51.99°C 🥵  988‰ ~157 used:67  [156]  source:dolphin3
      $2 #125 évolution              51.86°C 🥵  986‰ ~158 used:130 [157]  source:dolphin3
      $3 #271 diminution             50.76°C 🥵  983‰ ~155 used:41  [154]  source:dolphin3
      $4 #222 effet                  49.75°C 🥵  979‰ ~152 used:25  [151]  source:dolphin3
      $5  #99 accroissement          49.02°C 🥵  975‰ ~153 used:37  [152]  source:dolphin3
      $6 #119 progression            48.87°C 🥵  973‰ ~144 used:15  [143]  source:dolphin3
      $7 #241 résultat               48.32°C 🥵  969‰ ~128 used:11  [127]  source:dolphin3
      $8  #98 augmentation           48.07°C 🥵  966‰ ~129 used:11  [128]  source:dolphin3
      $9 #237 incidence              46.83°C 🥵  958‰ ~130 used:11  [129]  source:dolphin3
     $10 #329 indicateur             46.48°C 🥵  953‰ ~131 used:11  [130]  source:dolphin3
     $11 #351 proportion             46.22°C 🥵  951‰ ~132 used:11  [131]  source:dolphin3
     $23 #138 variation              41.43°C 😎  888‰ ~145 used:2   [144]  source:dolphin3
    $159  #69 innovation             27.77°C 🥶       ~162 used:0   [161]  source:dolphin3
    $393  #46 location               -1.38°C 🧊       ~393 used:0   [392]  source:dolphin3
