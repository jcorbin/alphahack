# 2026-08-24

- 🔗 spaceword.org 🧩 2026-08-23 🏁 score 2173 ranked 6.5% 21/324 ⏱️ 5:50:00.787609
- 🔗 wordgrid 🧩 #814 🟪 rarity:0.27 ⏱️ 0:05:06.113551
- 🔗 alfagok.diginaut.net 🧩 #660 🥳 24 ⏱️ 0:00:36.390163
- 🔗 alphaguess.com 🧩 #1127 🥳 32 ⏱️ 0:00:35.964210
- 🔗 dontwordle.com 🧩 #1553 🥳 6 ⏱️ 0:02:02.741239
- 🔗 dictionary.com hurdle 🧩 #1696 🥳 17 ⏱️ 0:02:53.535887
- 🔗 Quordle Classic 🧩 #1673 🥳 score:29 ⏱️ 0:01:33.717759
- 🔗 Octordle Classic 🧩 #1673 🥳 score:62 ⏱️ 0:02:03.137141
- 🔗 Sedecordle Classic 🧩 #1653 🥳 score:35 ⏱️ 0:02:50.867603
- 🔗 squareword.org 🧩 #1666 🥳 7 ⏱️ 0:02:20.561531
- 🔗 cemantle.certitudes.org 🧩 #1603 🥳 344 ⏱️ 1:20:15.289172
- 🔗 cemantix.certitudes.org 🧩 #1636 🥳 173 ⏱️ 3:48:42.999010

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




















# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #814 🟪 rarity:0.27 ⏱️ 0:05:06.113551

📜 2 sessions
🌌 🌌 🌌
🌌 🦄 🦄
🌌 🌌 🌌
Rarity: 0.27 🟪

# [spaceword.org](spaceword.org) 🧩 2026-08-23 🏁 score 2173 ranked 6.5% 21/324 ⏱️ 5:50:00.787609

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 21/324

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ R O C _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ _ _ Z A _ _ _   
      _ _ _ _ G O X _ _ _   
      _ _ _ _ _ O E _ _ _   
      _ _ _ _ Q I S _ _ _   
      _ _ _ _ _ D _ _ _ _   
      _ _ _ _ T A U _ _ _   
      _ _ _ _ A L P _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #660 🥳 24 ⏱️ 0:00:36.390163

🤔 24 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+786    [   786] aan        q10 ? ␅
    @+786    [   786] aan        q11 ? after
    @+4710   [  4710] aardappels q12 ? ␅
    @+4710   [  4710] aardappels q13 ? after
    @+5684   [  5684] abstinent  q20 ? ␅
    @+5684   [  5684] abstinent  q21 ? after
    @+6146   [  6146] acht       q22 ? ␅
    @+6146   [  6146] acht       q23 ? it
    @+6146   [  6146] acht       done. it
    @+6660   [  6660] achterop   q14 ? ␅
    @+6660   [  6660] achterop   q15 ? before
    @+8646   [  8646] af         q8  ? ␅
    @+8646   [  8646] af         q9  ? before
    @+24881  [ 24881] bad        q6  ? ␅
    @+24881  [ 24881] bad        q7  ? before
    @+49809  [ 49809] boks       q4  ? ␅
    @+49809  [ 49809] boks       q5  ? before
    @+99689  [ 99689] ex         q2  ? ␅
    @+99689  [ 99689] ex         q3  ? before
    @+199648 [199648] lijk       q0  ? ␅
    @+199648 [199648] lijk       q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1127 🥳 32 ⏱️ 0:00:35.964210

🤔 32 attempts
📜 1 sessions

    @       [    0] aa      
    @+47378 [47378] dis     q2  ? ␅
    @+47378 [47378] dis     q3  ? after
    @+72662 [72662] green   q4  ? ␅
    @+72662 [72662] green   q5  ? after
    @+85397 [85397] inocula q6  ? ␅
    @+85397 [85397] inocula q7  ? after
    @+91772 [91772] knight  q8  ? ␅
    @+91772 [91772] knight  q9  ? after
    @+93262 [93262] lar     q12 ? ␅
    @+93262 [93262] lar     q13 ? after
    @+93890 [93890] lea     q14 ? ␅
    @+93890 [93890] lea     q15 ? after
    @+94399 [94399] lei     q16 ? ␅
    @+94399 [94399] lei     q17 ? after
    @+94527 [94527] lent    q20 ? ␅
    @+94527 [94527] lent    q21 ? after
    @+94590 [94590] lept    q22 ? ␅
    @+94590 [94590] lept    q23 ? after
    @+94622 [94622] less    q24 ? ␅
    @+94622 [94622] less    q25 ? after
    @+94627 [94627] lessen  q28 ? ␅
    @+94627 [94627] lessen  q29 ? after
    @+94632 [94632] lesson  q30 ? ␅
    @+94632 [94632] lesson  q31 ? it
    @+94632 [94632] lesson  done. it
    @+94639 [94639] let     q26 ? ␅
    @+94639 [94639] let     q27 ? before
    @+94662 [94662] letter  q18 ? ␅
    @+94662 [94662] letter  q19 ? before
    @+94949 [94949] libel   q11 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1553 🥳 6 ⏱️ 0:02:02.741239

📜 1 sessions
💰 score: 153

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:HEEZE n n n n n remain:5957
    ⬜⬜⬜⬜⬜ tried:PAMPA n n n n n remain:2027
    ⬜⬜⬜⬜⬜ tried:JUJUS n n n n n remain:544
    ⬜⬜⬜⬜⬜ tried:ROTOR n n n n n remain:88
    ⬜🟩⬜⬜⬜ tried:CIVIC n Y n n n remain:32
    ⬜🟩⬜⬜🟩 tried:NINNY n Y n n Y remain:17

    Undos used: 3

      17 words remaining
    x 9 unused letters
    = 153 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1696 🥳 17 ⏱️ 0:02:53.535887

📜 1 sessions
💰 score: 9900

    5/6
    AROSE ⬜🟨⬜⬜🟨
    LITER 🟨🟨⬜🟩🟩
    IDLER 🟨⬜🟨🟩🟩
    FLIER ⬜🟩🟩🟩🟩
    PLIER 🟩🟩🟩🟩🟩
    4/6
    PLIER ⬜⬜⬜🟨🟨
    RESAY 🟩🟩🟨⬜⬜
    RENDS 🟩🟩⬜⬜🟨
    REUSE 🟩🟩🟩🟩🟩
    3/6
    REUSE 🟨⬜⬜⬜⬜
    ABORT 🟨⬜🟩🟨⬜
    CROAK 🟩🟩🟩🟩🟩
    3/6
    CROAK ⬜⬜🟨⬜⬜
    SETON 🟩🟨⬜🟨⬜
    SOLVE 🟩🟩🟩🟩🟩
    Final 2/2
    DONOR ⬜🟩⬜🟩🟩
    MOTOR 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1673 🥳 score:29 ⏱️ 0:01:33.717759

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. MAJOR attempts:8 score:8
2. VERGE attempts:5 score:5
3. CRUSH attempts:7 score:7
4. SCOFF attempts:9 score:9

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1673 🥳 score:62 ⏱️ 0:02:03.137141

📜 2 sessions

Octordle Classic

1. OPTIC attempts:4 score:4
2. ROOST attempts:10 score:10
3. WIELD attempts:8 score:8
4. REVEL attempts:11 score:11
5. CLING attempts:5 score:5
6. SPOOF attempts:9 score:9
7. TASTY attempts:3 score:3
8. CURRY attempts:12 score:12

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1653 🥳 score:35 ⏱️ 0:02:50.867603

📜 1 sessions

Sedecordle Classic sedecordle.com

1. SENSE attempts:5 score:0
2. BELLY attempts:19 score:5
3. SHIRT attempts:4 score:0
4. HUMPH attempts:15 score:4
5. ETHER attempts:6 score:0
6. FINER attempts:16 score:6
7. TIPSY attempts:7 score:0
8. LADEN attempts:12 score:7
9. NERDY attempts:13 score:1
10. GLARE attempts:8 score:3
11. RIGHT attempts:3 score:0
12. ASSAY attempts:9 score:3
13. MAGIC attempts:10 score:1
14. GIDDY attempts:11 score:0
15. CIDER attempts:14 score:1
16. SWELL attempts:17 score:4

# [squareword.org](squareword.org) 🧩 #1666 🥳 7 ⏱️ 0:02:20.561531

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C A R F
    T A T E R
    A R O S E
    F O N T S
    F L E S H

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1603 🥳 344 ⏱️ 1:20:15.289172

🤔 345 attempts
📜 2 sessions
🫧 29 chat sessions
⁉️ 172 chat prompts
🤖 90 dolphin3:latest replies
🤖 46 gemma4:12b replies
🤖 36 ornith:35b replies
🥵  14 😎  36 🥶 285 🧊   9

      $1 #345 strip           100.00°C 🥳 1000‰ ~336 used:0  [335]  source:dolphin3
      $2 #283 alley            30.67°C 🥵  976‰  ~44 used:50 [43]   source:gemma4  
      $3 #274 street           30.58°C 🥵  975‰  ~31 used:38 [30]   source:ornith  
      $4 #275 thoroughfare     28.50°C 🥵  955‰  ~26 used:16 [25]   source:ornith  
      $5 #196 enclave          28.43°C 🥵  954‰  ~30 used:34 [29]   source:ornith  
      $6 #261 corridor         28.07°C 🥵  949‰  ~21 used:11 [20]   source:ornith  
      $7 #331 boardwalk        27.96°C 🥵  946‰   ~2 used:10 [1]    source:gemma4  
      $8 #259 boulevard        27.59°C 🥵  939‰  ~22 used:11 [21]   source:ornith  
      $9 #338 runway           27.39°C 🥵  934‰   ~1 used:4  [0]    source:dolphin3
     $10 #284 curb             26.95°C 🥵  924‰  ~23 used:11 [22]   source:gemma4  
     $11 #108 area             26.75°C 🥵  918‰  ~47 used:71 [46]   source:dolphin3
     $16 #166 stretch          25.99°C 😎  884‰  ~32 used:4  [31]   source:dolphin3
     $52 #149 slice            19.54°C 🥶        ~58 used:0  [57]   source:dolphin3
    $337 #180 quarter          -0.28°C 🧊       ~337 used:0  [336]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1636 🥳 173 ⏱️ 3:48:42.999010

🤔 174 attempts
📜 1 sessions
🫧 43 chat sessions
⁉️ 177 chat prompts
🤖 27 ornith-1.5:35b replies
🤖 139 dolphin3:latest replies
🤖 11 gemma4:12b replies
🔥  3 🥵 16 😎 30 🥶 98 🧊 26

      $1 #174 couronner        100.00°C 🥳 1000‰ ~148 used:0   [147]  source:ornith  
      $2 #158 couronne          42.94°C 🔥  992‰   ~3 used:5   [2]    source:ornith  
      $3 #157 triomphateur      41.61°C 🔥  991‰   ~2 used:3   [1]    source:ornith  
      $4 #156 triomphal         41.36°C 🔥  990‰   ~1 used:1   [0]    source:ornith  
      $5 #159 diadème           39.52°C 🥵  986‰   ~4 used:0   [3]    source:ornith  
      $6 #164 gloire            38.58°C 🥵  984‰   ~5 used:0   [4]    source:ornith  
      $7  #49 éclatant          38.25°C 🥵  983‰  ~50 used:145 [49]   source:dolphin3
      $8  #37 brillant          35.73°C 🥵  978‰  ~47 used:74  [46]   source:dolphin3
      $9 #168 vainqueur         35.68°C 🥵  977‰   ~6 used:0   [5]    source:ornith  
     $10  #53 étincelant        35.28°C 🥵  974‰  ~45 used:30  [44]   source:dolphin3
     $11 #134 glorieux          35.12°C 🥵  971‰  ~42 used:21  [41]   source:dolphin3
     $21 #111 éminent           29.43°C 😎  892‰  ~17 used:2   [16]   source:ornith  
     $52 #138 élégance          20.55°C 🥶        ~52 used:0   [51]   source:dolphin3
    $149  #31 la                -0.39°C 🧊       ~149 used:0   [148]  source:dolphin3
