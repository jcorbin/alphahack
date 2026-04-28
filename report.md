# 2026-04-29

- 🔗 spaceword.org 🧩 2026-04-28 🏁 score 2168 ranked 44.6% 158/354 ⏱️ 0:13:41.584211
- 🔗 alfagok.diginaut.net 🧩 #543 🥳 56 ⏱️ 0:01:08.215459
- 🔗 alphaguess.com 🧩 #1010 🥳 28 ⏱️ 0:00:36.983451
- 🔗 dontwordle.com 🧩 #1436 🥳 6 ⏱️ 0:01:22.008061
- 🔗 dictionary.com hurdle 🧩 #1579 🥳 17 ⏱️ 0:02:50.000849
- 🔗 Quordle Classic 🧩 #1556 🥳 score:24 ⏱️ 0:01:25.112061
- 🔗 Octordle Classic 🧩 #1556 🥳 score:66 ⏱️ 0:03:59.193563
- 🔗 squareword.org 🧩 #1549 🥳 8 ⏱️ 0:02:11.937300
- 🔗 cemantle.certitudes.org 🧩 #1486 🥳 45 ⏱️ 0:00:21.798990
- 🔗 cemantix.certitudes.org 🧩 #1519 🥳 81 ⏱️ 0:01:21.446565

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



























































# [spaceword.org](spaceword.org) 🧩 2026-04-28 🏁 score 2168 ranked 44.6% 158/354 ⏱️ 0:13:41.584211

📜 2 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 158/354

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ F I Z _ _ _ _   
      _ _ _ E _ _ P _ _ _   
      _ _ _ U _ Y A _ _ _   
      _ _ _ D E A L _ _ _   
      _ _ _ _ _ W E _ _ _   
      _ _ _ _ _ N A _ _ _   
      _ _ _ _ J E T _ _ _   
      _ _ _ _ _ R E _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #543 🥳 56 ⏱️ 0:01:08.215459

🤔 56 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+199704 [199704] lijk       q0  ? ␅
    @+199704 [199704] lijk       q1  ? after
    @+199704 [199704] lijk       q2  ? ␅
    @+199704 [199704] lijk       q3  ? after
    @+199704 [199704] lijk       q4  ? ␅
    @+199704 [199704] lijk       q5  ? after
    @+299649 [299649] schroot    q6  ? ␅
    @+299649 [299649] schroot    q7  ? after
    @+349441 [349441] vakantie   q8  ? ␅
    @+349441 [349441] vakantie   q9  ? after
    @+374181 [374181] vrij       q10 ? ␅
    @+374181 [374181] vrij       q11 ? after
    @+386718 [386718] wind       q12 ? ␅
    @+386718 [386718] wind       q13 ? after
    @+393135 [393135] zelfmoord  q14 ? ␅
    @+393135 [393135] zelfmoord  q15 ? after
    @+393929 [393929] zeug       q20 ? ␅
    @+393929 [393929] zeug       q21 ? after
    @+394083 [394083] zeventig   q24 ? ␅
    @+394083 [394083] zeventig   q25 ? after
    @+394104 [394104] zever      q28 ? ␅
    @+394104 [394104] zever      q29 ? after
    @+394122 [394122] zich       q54 ? ␅
    @+394122 [394122] zich       q55 ? it
    @+394122 [394122] zich       done. it
    @+394125 [394125] zicht      q26 ? ␅
    @+394125 [394125] zicht      q27 ? before
    @+394233 [394233] ziekenhuis q22 ? ␅
    @+394233 [394233] ziekenhuis q23 ? before
    @+394718 [394718] zigzag     q19 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1010 🥳 28 ⏱️ 0:00:36.983451

🤔 28 attempts
📜 1 sessions

    @       [    0] aa      
    @+2     [    2] aahed   
    @+47380 [47380] dis     q2  ? ␅
    @+47380 [47380] dis     q3  ? after
    @+49427 [49427] do      q10 ? ␅
    @+49427 [49427] do      q11 ? after
    @+51401 [51401] drunk   q12 ? ␅
    @+51401 [51401] drunk   q13 ? after
    @+52394 [52394] earth   q14 ? ␅
    @+52394 [52394] earth   q15 ? after
    @+52874 [52874] ed      q16 ? ␅
    @+52874 [52874] ed      q17 ? after
    @+53047 [53047] eff     q18 ? ␅
    @+53047 [53047] eff     q19 ? after
    @+53200 [53200] egg     q20 ? ␅
    @+53200 [53200] egg     q21 ? after
    @+53291 [53291] eide    q22 ? ␅
    @+53291 [53291] eide    q23 ? after
    @+53342 [53342] eirenic q24 ? ␅
    @+53342 [53342] eirenic q25 ? after
    @+53363 [53363] eject   q26 ? ␅
    @+53363 [53363] eject   q27 ? it
    @+53363 [53363] eject   done. it
    @+53396 [53396] el      q8  ? ␅
    @+53396 [53396] el      q9  ? before
    @+60083 [60083] face    q6  ? ␅
    @+60083 [60083] face    q7  ? before
    @+72798 [72798] gremmy  q4  ? ␅
    @+72798 [72798] gremmy  q5  ? before
    @+98216 [98216] mach    q0  ? ␅
    @+98216 [98216] mach    q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1436 🥳 6 ⏱️ 0:01:22.008061

📜 1 sessions
💰 score: 40

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:JUJUS n n n n n remain:5557
    ⬜⬜⬜⬜⬜ tried:FEDEX n n n n n remain:1973
    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:825
    ⬜⬜⬜⬜⬜ tried:GLOGG n n n n n remain:173
    ⬜⬜⬜⬜🟨 tried:PHPHT n n n n m remain:32
    🟨🟨⬜⬜⬜ tried:ATTAR m m n n n remain:5

    Undos used: 2

      5 words remaining
    x 8 unused letters
    = 40 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1579 🥳 17 ⏱️ 0:02:50.000849

📜 1 sessions
💰 score: 9900

    4/6
    URSAE ⬜🟨⬜🟨🟩
    GLARE ⬜⬜🟨🟩🟩
    CADRE ⬜🟨🟨🟩🟩
    ADORE 🟩🟩🟩🟩🟩
    4/6
    ADORE ⬜⬜⬜⬜🟨
    ISLET ⬜⬜⬜🟨🟨
    TECHY 🟨🟩⬜🟨🟩
    HEFTY 🟩🟩🟩🟩🟩
    4/6
    HEFTY ⬜🟨⬜⬜⬜
    LOSER ⬜⬜⬜🟩⬜
    MANED ⬜⬜⬜🟩🟩
    BIPED 🟩🟩🟩🟩🟩
    4/6
    BIPED ⬜⬜⬜🟨⬜
    EARLS 🟨🟨⬜⬜⬜
    THANE ⬜🟨🟩⬜🟨
    HEAVY 🟩🟩🟩🟩🟩
    Final 1/2
    SHARP 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1556 🥳 score:24 ⏱️ 0:01:25.112061

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. TRAIL attempts:3 score:3
2. RENEW attempts:7 score:7
3. BELLE attempts:6 score:6
4. GREED attempts:8 score:8

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1556 🥳 score:66 ⏱️ 0:03:59.193563

📜 1 sessions

Octordle Classic

1. FROTH attempts:11 score:12
2. CRACK attempts:8 score:8
3. GAMUT attempts:9 score:9
4. FLICK attempts:11 score:11
5. CATTY attempts:4 score:4
6. SMEAR attempts:7 score:7
7. ROUGE attempts:10 score:10
8. CLOTH attempts:5 score:5

# [squareword.org](squareword.org) 🧩 #1549 🥳 8 ⏱️ 0:02:11.937300

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟩 🟩
    🟩 🟨 🟩 🟨 🟨
    🟨 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P L I T
    A L O N E
    L A G E R
    A C O R N
    D E N T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1486 🥳 45 ⏱️ 0:00:21.798990

🤔 46 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 6 chat prompts
🤖 6 dolphin3:latest replies
🥵  1 😎  5 🥶 36 🧊  3

     $1 #46 calendar       100.00°C 🥳 1000‰ ~43 used:0 [42]  source:dolphin3
     $2 #43 zodiac          30.98°C 🥵  967‰  ~1 used:2 [0]   source:dolphin3
     $3 #45 astrology       23.45°C 😎  776‰  ~2 used:0 [1]   source:dolphin3
     $4 #11 astronomy       19.47°C 😎  427‰  ~6 used:4 [5]   source:dolphin3
     $5 #16 celestial       18.40°C 😎  273‰  ~5 used:2 [4]   source:dolphin3
     $6 #21 observatory     17.57°C 😎  122‰  ~3 used:1 [2]   source:dolphin3
     $7  #9 telescope       17.33°C 😎   56‰  ~4 used:1 [3]   source:dolphin3
     $8 #12 constellation   16.65°C 🥶        ~7 used:0 [6]   source:dolphin3
     $9 #23 space           16.20°C 🥶        ~8 used:0 [7]   source:dolphin3
    $10 #27 astronomical    15.97°C 🥶        ~9 used:0 [8]   source:dolphin3
    $11 #26 alignment       14.78°C 🥶       ~10 used:0 [9]   source:dolphin3
    $12 #22 solar           13.04°C 🥶       ~11 used:0 [10]  source:dolphin3
    $13 #24 sphere          12.75°C 🥶       ~12 used:0 [11]  source:dolphin3
    $44 #30 collision       -0.22°C 🧊       ~44 used:0 [43]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1519 🥳 81 ⏱️ 0:01:21.446565

🤔 82 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 22 chat prompts
🤖 22 dolphin3:latest replies
🥵  3 😎 10 🥶 62 🧊  6

     $1 #82 herbe          100.00°C 🥳 1000‰ ~76 used:0  [75]  source:dolphin3
     $2 #38 fleur           38.88°C 🥵  967‰  ~8 used:16 [7]   source:dolphin3
     $3 #50 arbre           38.61°C 🥵  960‰  ~7 used:13 [6]   source:dolphin3
     $4 #49 plante          36.84°C 🥵  933‰  ~6 used:11 [5]   source:dolphin3
     $5 #59 soleil          33.96°C 😎  836‰  ~9 used:2  [8]   source:dolphin3
     $6 #75 ciel            33.96°C 😎  835‰  ~1 used:0  [0]   source:dolphin3
     $7 #58 terre           32.61°C 😎  766‰ ~10 used:2  [9]   source:dolphin3
     $8 #78 jardin          32.43°C 😎  754‰  ~2 used:0  [1]   source:dolphin3
     $9 #57 graine          31.47°C 😎  672‰  ~3 used:0  [2]   source:dolphin3
    $10 #26 feuille         30.92°C 😎  626‰ ~12 used:5  [11]  source:dolphin3
    $11  #7 escargot        29.92°C 😎  538‰ ~13 used:6  [12]  source:dolphin3
    $12 #79 nuage           28.71°C 😎  393‰  ~4 used:0  [3]   source:dolphin3
    $15 #68 bois            25.32°C 🥶       ~16 used:0  [15]  source:dolphin3
    $77  #6 croissant       -2.18°C 🧊       ~77 used:0  [76]  source:dolphin3
