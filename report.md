# 2026-03-30

- 🔗 spaceword.org 🧩 2026-03-29 🏁 score 2168 ranked 35.9% 122/340 ⏱️ 0:23:43.927838
- 🔗 alfagok.diginaut.net 🧩 #513 🥳 32 ⏱️ 0:00:46.264150
- 🔗 alphaguess.com 🧩 #980 🥳 24 ⏱️ 0:00:34.334868
- 🔗 dontwordle.com 🧩 #1406 🥳 6 ⏱️ 0:01:48.145107
- 🔗 dictionary.com hurdle 🧩 #1549 🥳 17 ⏱️ 0:03:05.603315
- 🔗 Quordle Classic 🧩 #1526 😦 score:25 ⏱️ 0:02:00.768282
- 🔗 Octordle Classic 🧩 #1526 🥳 score:60 ⏱️ 0:03:22.011296
- 🔗 squareword.org 🧩 #1519 🥳 8 ⏱️ 0:02:24.041525
- 🔗 cemantle.certitudes.org 🧩 #1456 🥳 58 ⏱️ 0:00:27.220346
- 🔗 cemantix.certitudes.org 🧩 #1489 🥳 96 ⏱️ 0:01:48.680688

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





























# [spaceword.org](spaceword.org) 🧩 2026-03-29 🏁 score 2168 ranked 35.9% 122/340 ⏱️ 0:23:43.927838

📜 5 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 122/340

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ B R O _ _ _   
      _ _ _ V I E _ _ _ _   
      _ _ _ _ _ Q _ _ _ _   
      _ _ _ R O U X _ _ _   
      _ _ _ _ _ I _ _ _ _   
      _ _ _ G O R _ _ _ _   
      _ _ _ _ S E I _ _ _   
      _ _ _ H E R _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #513 🥳 32 ⏱️ 0:00:46.264150

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+199608 [199608] lij         q0  ? ␅
    @+199608 [199608] lij         q1  ? after
    @+199608 [199608] lij         q2  ? ␅
    @+199608 [199608] lij         q3  ? after
    @+299482 [299482] schro       q4  ? ␅
    @+299482 [299482] schro       q5  ? after
    @+324420 [324420] subsidie    q8  ? ␅
    @+324420 [324420] subsidie    q9  ? after
    @+335610 [335610] toe         q10 ? ␅
    @+335610 [335610] toe         q11 ? after
    @+342516 [342516] tunnel      q12 ? ␅
    @+342516 [342516] tunnel      q13 ? after
    @+344120 [344120] uit         q14 ? ␅
    @+344120 [344120] uit         q15 ? after
    @+344452 [344452] uitdeden    q22 ? ␅
    @+344452 [344452] uitdeden    q23 ? after
    @+344618 [344618] uitdrupte   q24 ? ␅
    @+344618 [344618] uitdrupte   q25 ? after
    @+344639 [344639] uiteen      q26 ? ␅
    @+344639 [344639] uiteen      q27 ? after
    @+344712 [344712] uiteenval   q28 ? ␅
    @+344712 [344712] uiteenval   q29 ? after
    @+344749 [344749] uiterst     q30 ? ␅
    @+344749 [344749] uiterst     q31 ? it
    @+344749 [344749] uiterst     done. it
    @+344783 [344783] uitga       q20 ? ␅
    @+344783 [344783] uitga       q21 ? before
    @+345454 [345454] uitgestoten q18 ? ␅
    @+345454 [345454] uitgestoten q19 ? before
    @+346788 [346788] uitschreeuw q17 ? before

# [alphaguess.com](alphaguess.com) 🧩 #980 🥳 24 ⏱️ 0:00:34.334868

🤔 24 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+23682 [23682] camp       q6  ? ␅
    @+23682 [23682] camp       q7  ? after
    @+35525 [35525] convention q8  ? ␅
    @+35525 [35525] convention q9  ? after
    @+40841 [40841] da         q10 ? ␅
    @+40841 [40841] da         q11 ? after
    @+41551 [41551] day        q16 ? ␅
    @+41551 [41551] day        q17 ? after
    @+41654 [41654] dead       q20 ? ␅
    @+41654 [41654] dead       q21 ? after
    @+41743 [41743] deal       q22 ? ␅
    @+41743 [41743] deal       q23 ? it
    @+41743 [41743] deal       done. it
    @+41836 [41836] deb        q18 ? ␅
    @+41836 [41836] deb        q19 ? before
    @+42376 [42376] deco       q14 ? ␅
    @+42376 [42376] deco       q15 ? before
    @+44073 [44073] den        q12 ? ␅
    @+44073 [44073] den        q13 ? before
    @+47381 [47381] dis        q4  ? ␅
    @+47381 [47381] dis        q5  ? before
    @+98217 [98217] mach       q0  ? ␅
    @+98217 [98217] mach       q1  ? after
    @+98217 [98217] mach       q2  ? ␅
    @+98217 [98217] mach       q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1406 🥳 6 ⏱️ 0:01:48.145107

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:PZAZZ n n n n n remain:6291
    ⬜⬜⬜⬜⬜ tried:YOBBY n n n n n remain:2686
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:1066
    ⬜⬜🟨⬜⬜ tried:CHUCK n n m n n remain:143
    ⬜🟨⬜⬜🟨 tried:FUNDI n m n n m remain:2
    🟨🟨⬜🟩🟨 tried:SITUS m m n Y m remain:1

    Undos used: 4

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1549 🥳 17 ⏱️ 0:03:05.603315

📜 2 sessions
💰 score: 9900

    4/6
    EARNS 🟨⬜⬜⬜⬜
    EDICT 🟨🟨⬜⬜⬜
    EPHOD 🟨🟨⬜🟨🟨
    DOPEY 🟩🟩🟩🟩🟩
    4/6
    DOPEY ⬜⬜⬜⬜⬜
    RIALS ⬜🟨🟨🟨⬜
    LAICH 🟨🟨🟩⬜⬜
    ALIGN 🟩🟩🟩🟩🟩
    4/6
    ALIGN ⬜🟨🟨⬜⬜
    TILDE ⬜🟩🟩⬜⬜
    FILMS ⬜🟩🟩🟨⬜
    MILKY 🟩🟩🟩🟩🟩
    4/6
    MILKY 🟨🟨⬜⬜⬜
    ADMIT 🟨⬜🟨🟨⬜
    IMAGE 🟩🟩🟩🟩⬜
    IMAGO 🟩🟩🟩🟩🟩
    Final 1/2
    DINGY 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1526 😦 score:25 ⏱️ 0:02:00.768282

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. CHE_S -ADFILMNOPRTUWY attempts:9 score:-1
2. ALLOT attempts:5 score:5
3. SCONE attempts:4 score:4
4. DITTY attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1526 🥳 score:60 ⏱️ 0:03:22.011296

📜 2 sessions

Octordle Classic

1. HELIX attempts:7 score:7
2. PANEL attempts:8 score:8
3. AMPLY attempts:10 score:10
4. SMELL attempts:11 score:11
5. AXIAL attempts:9 score:9
6. IDIOM attempts:6 score:6
7. PINCH attempts:5 score:5
8. LIPID attempts:4 score:4

# [squareword.org](squareword.org) 🧩 #1519 🥳 8 ⏱️ 0:02:24.041525

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C A L D
    W A G E R
    I N L A Y
    M O O S E
    S E W E R

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1456 🥳 58 ⏱️ 0:00:27.220346

🤔 59 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 8 chat prompts
🤖 8 dolphin3:latest replies
😱  1 🥵  1 😎 10 🥶 44 🧊  2

     $1 #59 bubble       100.00°C 🥳 1000‰ ~57 used:0 [56]  source:dolphin3
     $2 #18 boom          55.31°C 😱  999‰  ~1 used:6 [0]   source:dolphin3
     $3 #32 balloon       35.33°C 🥵  970‰  ~2 used:2 [1]   source:dolphin3
     $4 #21 burst         29.74°C 😎  882‰ ~11 used:3 [10]  source:dolphin3
     $5 #35 cork          27.67°C 😎  817‰  ~3 used:0 [2]   source:dolphin3
     $6 #13 explosive     25.55°C 😎  671‰ ~12 used:3 [11]  source:dolphin3
     $7 #41 popping       24.91°C 😎  619‰  ~4 used:0 [3]   source:dolphin3
     $8 #16 explosion     24.23°C 😎  536‰  ~5 used:0 [4]   source:dolphin3
     $9 #55 blimp         23.60°C 😎  429‰  ~6 used:0 [5]   source:dolphin3
    $10 #29 shell         23.39°C 😎  387‰  ~7 used:0 [6]   source:dolphin3
    $11 #30 thunderclap   22.88°C 😎  282‰  ~8 used:0 [7]   source:dolphin3
    $12 #12 eruption      22.26°C 😎  150‰  ~9 used:0 [8]   source:dolphin3
    $14 #43 ricochet      20.73°C 🥶       ~13 used:0 [12]  source:dolphin3
    $58 #52 animal        -2.92°C 🧊       ~58 used:0 [57]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1489 🥳 96 ⏱️ 0:01:48.680688

🤔 97 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 21 chat prompts
🤖 21 dolphin3:latest replies
🥵  4 😎  8 🥶 71 🧊 13

     $1 #97 oiseau          100.00°C 🥳 1000‰ ~84 used:0 [83]  source:dolphin3
     $2 #92 moineau          53.77°C 🥵  958‰  ~1 used:3 [0]   source:dolphin3
     $3 #85 oiselle          51.93°C 🥵  942‰  ~2 used:4 [1]   source:dolphin3
     $4 #69 nid              51.77°C 🥵  940‰  ~4 used:9 [3]   source:dolphin3
     $5 #77 nidification     51.07°C 🥵  932‰  ~3 used:5 [2]   source:dolphin3
     $6 #76 nichoir          46.44°C 😎  868‰  ~5 used:0 [4]   source:dolphin3
     $7 #95 chant            39.27°C 😎  703‰  ~6 used:0 [5]   source:dolphin3
     $8 #96 nuage            35.31°C 😎  540‰  ~7 used:0 [6]   source:dolphin3
     $9 #89 caille           34.35°C 😎  481‰  ~8 used:0 [7]   source:dolphin3
    $10 #52 murmurant        32.45°C 😎  351‰ ~12 used:2 [11]  source:dolphin3
    $11 #75 graine           31.90°C 😎  306‰  ~9 used:0 [8]   source:dolphin3
    $12 #79 nidicole         31.24°C 😎  251‰ ~10 used:0 [9]   source:dolphin3
    $14 #28 doux             29.07°C 🥶       ~16 used:5 [15]  source:dolphin3
    $85 #18 propre           -0.74°C 🧊       ~85 used:0 [84]  source:dolphin3
