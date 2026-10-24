# 2026-10-25

- 🔗 wordgrid 🧩 #876 🟪 rarity:0.14 ⏱️ 0:02:27.139241
- 🔗 spaceword.org 🧩 2026-10-24 🏁 score 2158 ranked 69.2% 207/299 ⏱️ 0:08:45.944156
- 🔗 alfagok.diginaut.net 🧩 #722 🥳 36 ⏱️ 0:00:50.601694
- 🔗 alphaguess.com 🧩 #1189 🥳 42 ⏱️ 0:02:34.255690
- 🔗 dontwordle.com 🧩 #1615 🥳 6 ⏱️ 0:01:12.596406
- 🔗 dictionary.com hurdle 🧩 #1758 🥳 20 ⏱️ 0:03:34.419909
- 🔗 Quordle Classic 🧩 #1735 🥳 score:22 ⏱️ 0:01:18.236278
- 🔗 Octordle Classic 🧩 #1735 🥳 score:53 ⏱️ 0:02:03.133159
- 🔗 Sedecordle Classic 🧩 #1715 🥳 score:50 ⏱️ 0:02:55.775341
- 🔗 squareword.org 🧩 #1728 🥳 7 ⏱️ 0:01:59.125433
- 🔗 cemantle.certitudes.org 🧩 #1665 🥳 206 ⏱️ 0:22:19.264630
- 🔗 cemantix.certitudes.org 🧩 #1698 🥳 335 ⏱️ 0:20:18.621167

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





















# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #876 🟪 rarity:0.14 ⏱️ 0:02:27.139241

📜 2 sessions
🌌 🌌 🦄
🌌 🌌 🌌
🦄 🦄 🌌
Rarity: 0.14 🟪

# [spaceword.org](spaceword.org) 🧩 2026-10-24 🏁 score 2158 ranked 69.2% 207/299 ⏱️ 0:08:45.944156

📜 3 sessions
- tiles: 21/21
- score: 2158 bonus: +58
- rank: 207/299

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ B E D _ _ _ _ _   
      _ _ E M _ _ _ _ _ _   
      _ _ H _ _ _ _ _ _ _   
      _ _ A _ T _ _ _ _ _   
      _ _ V _ A X O N E _   
      _ _ E Q U I N E S _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #722 🥳 36 ⏱️ 0:00:50.601694

🤔 36 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+99672  [ 99672] ex           q2  ? ␅
    @+99672  [ 99672] ex           q3  ? after
    @+111327 [111327] ge           q6  ? ␅
    @+111327 [111327] ge           q7  ? after
    @+130307 [130307] gracht       q8  ? ␅
    @+130307 [130307] gracht       q9  ? after
    @+134991 [134991] haast        q12 ? ␅
    @+134991 [134991] haast        q13 ? after
    @+136086 [136086] handbal      q16 ? ␅
    @+136086 [136086] handbal      q17 ? after
    @+136288 [136288] handels      q18 ? ␅
    @+136288 [136288] handels      q19 ? after
    @+136756 [136756] handelt      q20 ? ␅
    @+136756 [136756] handelt      q21 ? after
    @+136803 [136803] handgel      q26 ? ␅
    @+136803 [136803] handgel      q27 ? after
    @+136825 [136825] handgewricht q28 ? ␅
    @+136825 [136825] handgewricht q29 ? after
    @+136835 [136835] handhaaf     q30 ? ␅
    @+136835 [136835] handhaaf     q31 ? after
    @+136835 [136835] handhaaf     q32 ? ␅
    @+136835 [136835] handhaaf     q33 ? after
    @+136842 [136842] handhaven    q34 ? ␅
    @+136842 [136842] handhaven    q35 ? it
    @+136842 [136842] handhaven    done. it
    @+136847 [136847] handhaving   q24 ? ␅
    @+136847 [136847] handhaving   q25 ? before
    @+136992 [136992] handreiking  q22 ? ␅
    @+136992 [136992] handreiking  q23 ? before
    @+137227 [137227] hang         q15 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1189 🥳 42 ⏱️ 0:02:34.255690

🤔 42 attempts
📜 2 sessions

    @       [    0] aa         
    @+23680 [23680] camp       q6  ? ␅
    @+23680 [23680] camp       q7  ? after
    @+35522 [35522] convention q8  ? ␅
    @+35522 [35522] convention q9  ? after
    @+40838 [40838] da         q10 ? ␅
    @+40838 [40838] da         q11 ? after
    @+42369 [42369] deco       q14 ? ␅
    @+42369 [42369] deco       q15 ? after
    @+42550 [42550] decoy      q20 ? ␅
    @+42550 [42550] decoy      q21 ? after
    @+42641 [42641] dedicate   q22 ? ␅
    @+42641 [42641] dedicate   q23 ? after
    @+42672 [42672] dee        q24 ? ␅
    @+42672 [42672] dee        q25 ? after
    @+42691 [42691] deep       q26 ? ␅
    @+42691 [42691] deep       q27 ? after
    @+42697 [42697] deepens    q32 ? ␅
    @+42697 [42697] deepens    q33 ? after
    @+42698 [42698] deeper     q40 ? ␅
    @+42698 [42698] deeper     q41 ? it
    @+42698 [42698] deeper     done. it
    @+42699 [42699] deepest    q38 ? ␅
    @+42699 [42699] deepest    q39 ? before
    @+42700 [42700] deepfreeze q30 ? ␅
    @+42700 [42700] deepfreeze q31 ? before
    @+42711 [42711] deer       q28 ? ␅
    @+42711 [42711] deer       q29 ? before
    @+42733 [42733] def        q18 ? ␅
    @+42733 [42733] def        q19 ? before
    @+43210 [43210] degrade    q17 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1615 🥳 6 ⏱️ 0:01:12.596406

📜 1 sessions
💰 score: 105

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:MOTTO n n n n n remain:5765
    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:2817
    ⬜⬜⬜⬜⬜ tried:VUGGY n n n n n remain:1153
    🟨⬜⬜⬜⬜ tried:ADDAX m n n n n remain:376
    ⬜⬜🟨⬜⬜ tried:CHAFF n n m n n remain:116
    ⬜🟩⬜🟨⬜ tried:ZAZEN n Y n m n remain:15

    Undos used: 2

      15 words remaining
    x 7 unused letters
    = 105 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1758 🥳 20 ⏱️ 0:03:34.419909

📜 1 sessions
💰 score: 9600

    4/6
    RAISE 🟨⬜⬜🟩🟩
    PROSE ⬜🟨⬜🟩🟩
    BACON ⬜⬜⬜⬜⬜
    TERSE 🟩🟩🟩🟩🟩
    6/6
    TERSE ⬜⬜🟨🟨⬜
    RAKIS 🟨🟨⬜⬜🟨
    ARSON 🟨🟨🟨⬜⬜
    SCAUR 🟩🟩🟩⬜🟨
    PUFFY ⬜⬜🟨⬜⬜
    SCARF 🟩🟩🟩🟩🟩
    4/6
    SCARF 🟨🟨🟩⬜⬜
    CLASH 🟩🟩🟩🟩⬜
    PACTS ⬜🟨🟨⬜🟩
    ????? 🟩🟩🟩🟩🟩
    4/6
    CLASS ⬜⬜⬜⬜⬜
    IRONE ⬜⬜🟩🟩🟨
    EBONY 🟨⬜🟩🟩🟩
    PEONY 🟩🟩🟩🟩🟩
    Final 2/2
    WAKED ⬜🟨🟨🟨⬜
    STEAK 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1735 🥳 score:22 ⏱️ 0:01:18.236278

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. RAINY attempts:3 score:3
2. BUSED attempts:7 score:7
3. PROXY attempts:4 score:4
4. UNDID attempts:8 score:8

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1735 🥳 score:53 ⏱️ 0:02:03.133159

📜 1 sessions

Octordle Classic

1. DOUBT attempts:5 score:5
2. DWELL attempts:6 score:6
3. SAVOR attempts:3 score:3
4. SKUNK attempts:8 score:8
5. PIANO attempts:4 score:4
6. RAYON attempts:9 score:9
7. FLEET attempts:11 score:11
8. ADOBE attempts:7 score:7

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1715 🥳 score:50 ⏱️ 0:02:55.775341

📜 1 sessions

Sedecordle Classic sedecordle.com

1. ALONE attempts:16 score:1
2. GLAND attempts:16 score:7
3. MAFIA attempts:13 score:1
4. ABACK attempts:15 score:3
5. YEARN attempts:4 score:0
6. WRACK attempts:16 score:4
7. BELOW attempts:5 score:0
8. OCCUR attempts:7 score:5
9. WEIGH attempts:6 score:0
10. MAGMA attempts:11 score:6
11. RUMOR attempts:8 score:0
12. OWNER attempts:10 score:8
13. LINEN attempts:16 score:1
14. TIPSY attempts:9 score:9
15. CRUSH attempts:14 score:1
16. CRACK attempts:12 score:4

# [squareword.org](squareword.org) 🧩 #1728 🥳 7 ⏱️ 0:01:59.125433

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B R A S H
    A O R T A
    S U G A R
    A T O N E
    L E N D S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1665 🥳 206 ⏱️ 0:22:19.264630

🤔 207 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 43 chat prompts
🤖 29 dolphin3:latest replies
🤖 14 gemma4:12b replies
🥵  11 😎  33 🥶 152 🧊  10

      $1 #207 impose          100.00°C 🥳 1000‰ ~197 used:0  [196]  source:dolphin3
      $2 #147 restrict         48.71°C 🥵  989‰  ~34 used:13 [33]   source:dolphin3
      $3 #161 constrain        45.23°C 🥵  977‰   ~7 used:7  [6]    source:dolphin3
      $4 #165 curtail          44.79°C 🥵  971‰   ~3 used:3  [2]    source:dolphin3
      $5 #168 rein             43.86°C 🥵  961‰   ~4 used:3  [3]    source:dolphin3
      $6 #118 regulate         43.68°C 🥵  960‰  ~35 used:13 [34]   source:dolphin3
      $7 #130 govern           43.45°C 🥵  956‰   ~8 used:8  [7]    source:dolphin3
      $8 #150 restrain         41.60°C 🥵  947‰   ~1 used:2  [0]    source:dolphin3
      $9  #77 amend            40.82°C 🥵  940‰  ~36 used:17 [35]   source:gemma4  
     $10 #134 dictate          40.60°C 🥵  935‰   ~5 used:3  [4]    source:dolphin3
     $11 #148 confine          40.14°C 🥵  930‰   ~6 used:3  [5]    source:dolphin3
     $13 #143 limit            38.35°C 😎  899‰   ~9 used:1  [8]    source:dolphin3
     $46  #64 change           25.20°C 🥶        ~51 used:1  [50]   source:gemma4  
    $198   #3 kaleidoscope     -0.84°C 🧊       ~198 used:0  [197]  source:gemma4  

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1698 🥳 335 ⏱️ 0:20:18.621167

🤔 336 attempts
📜 1 sessions
🫧 17 chat sessions
⁉️ 91 chat prompts
🤖 77 nemotron-3-nano:30b-cloud replies
🤖 14 gemma4:12b replies
😱   1 🔥   4 🥵  17 😎  54 🥶 219 🧊  40

      $1 #336 millénaire         100.00°C 🥳 1000‰ ~296 used:0  [295]  source:nemotron
      $2 #326 siècle              62.31°C 😱  999‰   ~1 used:7  [0]    source:nemotron
      $3  #90 civilisation        51.87°C 🔥  998‰  ~20 used:86 [19]   source:gemma4  
      $4 #278 ère                 46.23°C 🔥  995‰   ~4 used:28 [3]    source:nemotron
      $5  #98 humanité            44.47°C 🔥  994‰  ~18 used:55 [17]   source:gemma4  
      $6 #239 ancestral           44.47°C 🔥  993‰   ~3 used:21 [2]    source:nemotron
      $7 #240 antiquité           39.44°C 🥵  979‰   ~5 used:3  [4]    source:nemotron
      $8 #108 tradition           38.70°C 🥵  975‰  ~71 used:11 [70]   source:gemma4  
      $9 #175 ancêtre             37.64°C 🥵  971‰  ~17 used:5  [16]   source:nemotron
     $10 #188 génération          36.46°C 🥵  967‰  ~14 used:4  [13]   source:nemotron
     $11  #66 planète             36.43°C 🥵  966‰  ~19 used:8  [18]   source:gemma4  
     $24  #99 héritage            32.37°C 😎  898‰  ~22 used:0  [21]   source:gemma4  
     $78 #302 évolutionnisme      21.85°C 🥶        ~78 used:0  [77]   source:nemotron
    $297 #203 gardien             -0.03°C 🧊       ~297 used:0  [296]  source:nemotron
