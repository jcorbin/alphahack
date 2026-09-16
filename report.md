# 2026-09-17

- 🔗 spaceword.org 🧩 2026-09-16 🏁 score 2168 ranked 29.3% 107/365 ⏱️ 3:11:28.778591
- 🔗 wordgrid 🧩 #838 🟪 rarity:0.25 ⏱️ 0:04:26.807670
- 🔗 alfagok.diginaut.net 🧩 #684 🥳 36 ⏱️ 0:01:19.288418
- 🔗 alphaguess.com 🧩 #1151 🥳 18 ⏱️ 0:00:26.439106
- 🔗 dontwordle.com 🧩 #1577 🥳 6 ⏱️ 0:01:27.319979
- 🔗 dictionary.com hurdle 🧩 #1720 🥳 21 ⏱️ 0:05:37.956637
- 🔗 Quordle Classic 🧩 #1697 🥳 score:26 ⏱️ 0:01:41.929476
- 🔗 Octordle Classic 🧩 #1697 🥳 score:60 ⏱️ 0:01:39.824946
- 🔗 Sedecordle Classic 🧩 #1677 🥳 score:48 ⏱️ 0:03:17.865042
- 🔗 squareword.org 🧩 #1690 🥳 7 ⏱️ 0:02:18.638287
- 🔗 cemantle.certitudes.org 🧩 #1627 🥳 132 ⏱️ 0:03:43.596832
- 🔗 cemantix.certitudes.org 🧩 #1660 🥳 131 ⏱️ 0:04:35.706881

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


# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 2026-09-11 🤔 rarity:nan ⏱️ 0:00:33.329642

📜 2 sessions
❓ ❓ ❓
❓ ❓ ❓
❓ ❓ ❓








# [spaceword.org](spaceword.org) 🧩 2026-09-16 🏁 score 2168 ranked 29.3% 107/365 ⏱️ 3:11:28.778591

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 107/365

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ H U P _ _ _ _   
      _ _ _ I _ I _ _ _ _   
      _ _ _ _ _ Q I _ _ _   
      _ _ _ _ L U N _ _ _   
      _ _ _ _ _ E W _ _ _   
      _ _ _ F A D O _ _ _   
      _ _ _ _ _ _ V _ _ _   
      _ _ _ T U N E _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #838 🟪 rarity:0.25 ⏱️ 0:04:26.807670

📜 4 sessions
🌌 🌌 🌌
🦄 🦄 🌌
🦄 🌌 🌌
Rarity: 0.25 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #684 🥳 36 ⏱️ 0:01:19.288418

🤔 36 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+199531 [199531] lij        q0  ? ␅
    @+199531 [199531] lij        q1  ? /site
    @+199531 [199531] lij        q2  ? ␅
    @+199531 [199531] lij        q3  ? after
    @+199531 [199531] lij        q4  ? ␅
    @+199531 [199531] lij        q5  ? after
    @+299485 [299485] schrok     q6  ? ␅
    @+299485 [299485] schrok     q7  ? after
    @+302532 [302532] show       q16 ? ␅
    @+302532 [302532] show       q17 ? after
    @+304065 [304065] skateboard q18 ? ␅
    @+304065 [304065] skateboard q19 ? after
    @+304679 [304679] slag       q20 ? ␅
    @+304679 [304679] slag       q21 ? after
    @+304701 [304701] slagbomen  q32 ? ␅
    @+304701 [304701] slagbomen  q33 ? after
    @+304711 [304711] slagen     q34 ? ␅
    @+304711 [304711] slagen     q35 ? it
    @+304711 [304711] slagen     done. it
    @+304723 [304723] slagers    q30 ? ␅
    @+304723 [304723] slagers    q31 ? before
    @+304777 [304777] slaglinies q28 ? ␅
    @+304777 [304777] slaglinies q29 ? before
    @+304875 [304875] slak       q26 ? ␅
    @+304875 [304875] slak       q27 ? before
    @+305145 [305145] slavist    q24 ? ␅
    @+305145 [305145] slavist    q25 ? before
    @+305607 [305607] slijk      q14 ? ␅
    @+305607 [305607] slijk      q15 ? before
    @+311727 [311727] spier      q13 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1151 🥳 18 ⏱️ 0:00:26.439106

🤔 18 attempts
📜 1 sessions

    @        [     0] aa     
    @+1      [     1] aah    
    @+2      [     2] aahed  
    @+3      [     3] aahing 
    @+98143  [ 98143] mac    q0  ? ␅
    @+98143  [ 98143] mac    q1  ? after
    @+109925 [109925] ne     q6  ? ␅
    @+109925 [109925] ne     q7  ? after
    @+111475 [111475] no     q10 ? ␅
    @+111475 [111475] no     q11 ? after
    @+113838 [113838] nu     q12 ? ␅
    @+113838 [113838] nu     q13 ? after
    @+114422 [114422] object q16 ? ␅
    @+114422 [114422] object q17 ? it
    @+114422 [114422] object done. it
    @+115068 [115068] odor   q14 ? ␅
    @+115068 [115068] odor   q15 ? before
    @+116319 [116319] orb    q8  ? ␅
    @+116319 [116319] orb    q9  ? before
    @+122720 [122720] parol  q4  ? ␅
    @+122720 [122720] parol  q5  ? before
    @+147307 [147307] rho    q2  ? ␅
    @+147307 [147307] rho    q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1577 🥳 6 ⏱️ 0:01:27.319979

📜 1 sessions
💰 score: 36

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:NANNA n n n n n remain:5978
    ⬜⬜⬜⬜⬜ tried:DEKED n n n n n remain:2057
    ⬜⬜⬜⬜⬜ tried:HOOCH n n n n n remain:629
    ⬜⬜⬜⬜⬜ tried:VILLI n n n n n remain:170
    ⬜🟨⬜⬜⬜ tried:BUBBY n m n n n remain:24
    ⬜⬜🟩⬜⬜ tried:GRUFF n n Y n n remain:4

    Undos used: 3

      4 words remaining
    x 9 unused letters
    = 36 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1720 🥳 21 ⏱️ 0:05:37.956637

📜 1 sessions
💰 score: 9500

    5/6
    ASTER ⬜⬜⬜⬜🟨
    RUING 🟨⬜⬜⬜⬜
    HYDRO ⬜⬜⬜🟨🟨
    BICEP ⬜⬜⬜⬜🟨
    PROWL 🟩🟩🟩🟩🟩
    6/6
    PROWL ⬜⬜⬜⬜🟨
    SCALE ⬜⬜⬜🟩🟨
    BAKED ⬜⬜⬜🟨⬜
    FANGS ⬜⬜⬜⬜⬜
    ENJOY 🟩⬜⬜⬜⬜
    EXULT 🟩🟩🟩🟩🟩
    4/6
    EXULT ⬜⬜🟨⬜⬜
    MURAS 🟩🟨⬜⬜🟩
    ADMIN ⬜⬜🟨🟨🟨
    MINUS 🟩🟩🟩🟩🟩
    5/6
    MINUS 🟨⬜⬜⬜⬜
    ARMED ⬜⬜🟩⬜⬜
    LYMPH ⬜⬜🟩⬜⬜
    BACON 🟨⬜🟨🟨⬜
    COMBO 🟩🟩🟩🟩🟩
    Final 1/2
    QUALM 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1697 🥳 score:26 ⏱️ 0:01:41.929476

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. CRIER attempts:7 score:8
2. CHIRP attempts:7 score:7
3. NEIGH attempts:5 score:5
4. FREER attempts:6 score:6

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1697 🥳 score:60 ⏱️ 0:01:39.824946

📜 1 sessions

Octordle Classic

1. WHACK attempts:4 score:4
2. STALL attempts:5 score:5
3. SKULL attempts:6 score:6
4. STAVE attempts:10 score:10
5. MOTTO attempts:7 score:7
6. KNOCK attempts:8 score:8
7. GRAFT attempts:11 score:11
8. DODGE attempts:9 score:9

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1677 🥳 score:48 ⏱️ 0:03:17.865042

📜 1 sessions

Sedecordle Classic sedecordle.com

1. KAPPA attempts:9 score:0
2. GRIND attempts:13 score:9
3. VOMIT attempts:4 score:0
4. BROKE attempts:8 score:4
5. RELIC attempts:5 score:0
6. MINCE attempts:6 score:5
7. BRINY attempts:7 score:0
8. BRAIN attempts:10 score:7
9. IMAGE attempts:11 score:1
10. FLING attempts:12 score:1
11. WENCH attempts:14 score:1
12. LEPER attempts:15 score:4
13. STRAY attempts:16 score:1
14. SOGGY attempts:17 score:6
15. GOODY attempts:18 score:1
16. INGOT attempts:19 score:8

# [squareword.org](squareword.org) 🧩 #1690 🥳 7 ⏱️ 0:02:18.638287

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    R A G E D
    E L U D E
    A L I G N
    P O S E S
    S W E D E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1627 🥳 132 ⏱️ 0:03:43.596832

🤔 133 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 32 chat prompts
🤖 32 gemma4:12b replies
🔥  3 🥵 14 😎 33 🥶 80 🧊  2

      $1 #133 immune         100.00°C 🥳 1000‰ ~131 used:0  [130]  source:gemma4
      $2  #99 cytokine        46.04°C 🔥  996‰   ~3 used:17 [2]    source:gemma4
      $3  #19 metabolism      45.04°C 🔥  991‰  ~14 used:28 [13]   source:gemma4
      $4  #17 enzyme          44.69°C 🔥  990‰  ~13 used:23 [12]   source:gemma4
      $5  #84 endocrine       42.81°C 🥵  984‰  ~15 used:3  [14]   source:gemma4
      $6  #81 secretion       42.10°C 🥵  978‰  ~16 used:3  [15]   source:gemma4
      $7 #102 interleukin     41.61°C 🥵  975‰   ~4 used:2  [3]    source:gemma4
      $8 #107 interferon      41.31°C 🥵  971‰   ~5 used:2  [4]    source:gemma4
      $9  #31 protein         40.85°C 🥵  969‰  ~17 used:3  [16]   source:gemma4
     $10 #120 oxidative       39.98°C 🥵  961‰   ~6 used:2  [5]    source:gemma4
     $11 #108 macrophage      39.56°C 🥵  952‰   ~7 used:2  [6]    source:gemma4
     $19  #41 inhibition      36.00°C 😎  872‰  ~18 used:0  [17]   source:gemma4
     $52  #40 glycolysis      26.34°C 🥶        ~51 used:0  [50]   source:gemma4
    $132  #88 release         -2.26°C 🧊       ~132 used:0  [131]  source:gemma4

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1660 🥳 131 ⏱️ 0:04:35.706881

🤔 132 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 21 chat prompts
🤖 21 gemma4:12b replies
😱  1 🔥  1 🥵  7 😎 23 🥶 79 🧊 20

      $1 #132 gare            100.00°C 🥳 1000‰ ~112 used:0 [111]  source:gemma4
      $2 #131 train            67.22°C 😱  999‰   ~1 used:1 [0]    source:gemma4
      $3 #117 bus              50.34°C 🔥  993‰   ~2 used:0 [1]    source:gemma4
      $4  #96 navette          45.73°C 🥵  988‰   ~7 used:7 [6]    source:gemma4
      $5 #104 navetteur        41.60°C 🥵  976‰   ~6 used:6 [5]    source:gemma4
      $6  #63 trajet           39.46°C 🥵  967‰   ~9 used:8 [8]    source:gemma4
      $7 #100 voyageur         38.75°C 🥵  962‰   ~5 used:4 [4]    source:gemma4
      $8  #61 autoroute        38.32°C 🥵  961‰   ~8 used:7 [7]    source:gemma4
      $9 #118 camion           32.78°C 🥵  912‰   ~3 used:0 [2]    source:gemma4
     $10  #91 convoi           32.19°C 🥵  901‰   ~4 used:2 [3]    source:gemma4
     $11  #60 route            31.83°C 😎  892‰  ~10 used:1 [9]    source:gemma4
     $12  #62 boulevard        30.97°C 😎  879‰  ~11 used:0 [10]   source:gemma4
     $34  #40 déviation        19.10°C 🥶        ~37 used:0 [36]   source:gemma4
    $113  #17 entraînement     -0.02°C 🧊       ~113 used:0 [112]  source:gemma4
