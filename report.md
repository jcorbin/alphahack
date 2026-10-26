# 2026-10-26

- 🔗 spaceword.org 🧩 2026-10-25 🏁 score 2168 ranked 48.3% 142/294 ⏱️ 0:49:40.605898
- 🔗 wordgrid 🧩 #877 🟪 rarity:0.31 ⏱️ 0:02:02.907051
- 🔗 alfagok.diginaut.net 🧩 #723 🥳 24 ⏱️ 0:00:34.139207
- 🔗 alphaguess.com 🧩 #1190 🥳 30 ⏱️ 0:00:33.127110
- 🔗 dontwordle.com 🧩 #1616 🥳 6 ⏱️ 0:01:29.050478
- 🔗 dictionary.com hurdle 🧩 #1759 🥳 16 ⏱️ 0:02:04.707848
- 🔗 Quordle Classic 🧩 #1736 🥳 score:26 ⏱️ 0:01:35.566202
- 🔗 Octordle Classic 🧩 #1736 🥳 score:60 ⏱️ 0:01:47.386824
- 🔗 Sedecordle Classic 🧩 #1716 🥳 score:34 ⏱️ 0:03:16.807825
- 🔗 squareword.org 🧩 #1729 🥳 8 ⏱️ 0:02:09.554843
- 🔗 cemantle.certitudes.org 🧩 #1666 🥳 104 ⏱️ 0:05:11.762353
- 🔗 cemantix.certitudes.org 🧩 #1699 🥳 621 ⏱️ 2:24:41.713473

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






















# [spaceword.org](spaceword.org) 🧩 2026-10-25 🏁 score 2168 ranked 48.3% 142/294 ⏱️ 0:49:40.605898

📜 2 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 142/294

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ J _ _ Q _ A _ O _   
      _ O _ K A H U N A _   
      _ G O I T E R _ T _   
      _ _ _ _ S _ A _ Y _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #877 🟪 rarity:0.31 ⏱️ 0:02:02.907051

📜 2 sessions
🦄 🌌 🌌
🦄 🦄 🌌
🌌 🌌 🌌
Rarity: 0.31 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #723 🥳 24 ⏱️ 0:00:34.139207

🤔 24 attempts
📜 1 sessions

    @        [     0] &-teken       
    @+1      [     1] &-tekens      
    @+2      [     2] -cijferig     
    @+3      [     3] -e-mail       
    @+199631 [199631] lijk          q0  ? ␅
    @+199631 [199631] lijk          q1  ? after
    @+299528 [299528] schroot       q2  ? ␅
    @+299528 [299528] schroot       q3  ? after
    @+349310 [349310] vakantie      q4  ? ␅
    @+349310 [349310] vakantie      q5  ? after
    @+374044 [374044] vrij          q6  ? ␅
    @+374044 [374044] vrij          q7  ? after
    @+374387 [374387] vrijmacht     q18 ? ␅
    @+374387 [374387] vrijmacht     q19 ? after
    @+374528 [374528] vrijwilligers q20 ? ␅
    @+374528 [374528] vrijwilligers q21 ? after
    @+374608 [374608] vroeg         q22 ? ␅
    @+374608 [374608] vroeg         q23 ? it
    @+374608 [374608] vroeg         done. it
    @+374733 [374733] vrouwen       q16 ? ␅
    @+374733 [374733] vrouwen       q17 ? before
    @+375487 [375487] vuur          q14 ? ␅
    @+375487 [375487] vuur          q15 ? before
    @+377105 [377105] wandel        q12 ? ␅
    @+377105 [377105] wandel        q13 ? before
    @+380254 [380254] weer          q10 ? ␅
    @+380254 [380254] weer          q11 ? before
    @+386579 [386579] wind          q8  ? ␅
    @+386579 [386579] wind          q9  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1190 🥳 30 ⏱️ 0:00:33.127110

🤔 30 attempts
📜 1 sessions

    @        [     0] aa        
    @+98142  [ 98142] mac       q0  ? ␅
    @+98142  [ 98142] mac       q1  ? after
    @+147304 [147304] rho       q2  ? ␅
    @+147304 [147304] rho       q3  ? after
    @+153304 [153304] sea       q8  ? ␅
    @+153304 [153304] sea       q9  ? after
    @+154870 [154870] seraph    q12 ? ␅
    @+154870 [154870] seraph    q13 ? after
    @+155611 [155611] sham      q14 ? ␅
    @+155611 [155611] sham      q15 ? after
    @+155888 [155888] she       q16 ? ␅
    @+155888 [155888] she       q17 ? after
    @+156165 [156165] shetlands q18 ? ␅
    @+156165 [156165] shetlands q19 ? after
    @+156285 [156285] shin      q20 ? ␅
    @+156285 [156285] shin      q21 ? after
    @+156293 [156293] shine     q28 ? ␅
    @+156293 [156293] shine     q29 ? it
    @+156293 [156293] shine     done. it
    @+156298 [156298] shingle   q26 ? ␅
    @+156298 [156298] shingle   q27 ? before
    @+156313 [156313] shiningly q24 ? ␅
    @+156313 [156313] shiningly q25 ? before
    @+156340 [156340] ship      q22 ? ␅
    @+156340 [156340] ship      q23 ? before
    @+156441 [156441] shit      q10 ? ␅
    @+156441 [156441] shit      q11 ? before
    @+159586 [159586] slug      q6  ? ␅
    @+159586 [159586] slug      q7  ? before
    @+171904 [171904] tag       q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1616 🥳 6 ⏱️ 0:01:29.050478

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:BUZZY n n n n n remain:7558
    ⬜⬜⬜⬜⬜ tried:DAGGA n n n n n remain:2841
    ⬜⬜⬜⬜⬜ tried:JEFES n n n n n remain:309
    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:60
    ⬜⬜🟨⬜⬜ tried:KNOLL n n m n n remain:13
    🟨🟩⬜⬜⬜ tried:POTTO m Y n n n remain:1

    Undos used: 5

      1 words remaining
    x 6 unused letters
    = 6 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1759 🥳 16 ⏱️ 0:02:04.707848

📜 2 sessions
💰 score: 10000

    4/6
    SAICE ⬜🟨⬜⬜⬜
    MORAL ⬜🟨⬜🟨🟨
    ALONG 🟩🟨🟩⬜⬜
    AHOLD 🟩🟩🟩🟩🟩
    4/6
    AHOLD ⬜⬜⬜⬜⬜
    RINSE 🟨⬜⬜⬜🟨
    TUYER 🟩🟩⬜🟩🟩
    TUBER 🟩🟩🟩🟩🟩
    3/6
    TUBER ⬜🟨⬜🟨⬜
    AMUSE ⬜🟨🟩🟩🟩
    MOUSE 🟩🟩🟩🟩🟩
    4/6
    MOUSE ⬜⬜⬜⬜🟨
    IDLER ⬜⬜🟨🟨⬜
    LEPTA 🟨🟨🟨🟨🟨
    PLEAT 🟩🟩🟩🟩🟩
    Final 1/2
    EXUDE 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1736 🥳 score:26 ⏱️ 0:01:35.566202

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. ASSAY attempts:4 score:4
2. GLEAM attempts:6 score:6
3. MUCUS attempts:7 score:7
4. WRING attempts:9 score:9

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1736 🥳 score:60 ⏱️ 0:01:47.386824

📜 1 sessions

Octordle Classic

1. FORGO attempts:9 score:9
2. GAUDY attempts:11 score:11
3. SHUSH attempts:4 score:4
4. MISSY attempts:5 score:5
5. ILIAC attempts:6 score:6
6. HOVER attempts:7 score:7
7. RACER attempts:8 score:8
8. FRAUD attempts:10 score:10

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1716 🥳 score:34 ⏱️ 0:03:16.807825

📜 1 sessions

Sedecordle Classic sedecordle.com

1. LOATH attempts:4 score:0
2. CRAZY attempts:18 score:4
3. FLUTE attempts:13 score:1
4. PHOTO attempts:5 score:3
5. ETHIC attempts:16 score:1
6. CHAIR attempts:8 score:6
7. WILLY attempts:11 score:1
8. FETID attempts:9 score:1
9. CLEFT attempts:17 score:1
10. ISLET attempts:3 score:7
11. ODDER attempts:12 score:1
12. SPIED attempts:7 score:2
13. PYGMY attempts:14 score:1
14. GOLLY attempts:15 score:4
15. WHELP attempts:10 score:1
16. APHID attempts:6 score:0

# [squareword.org](squareword.org) 🧩 #1729 🥳 8 ⏱️ 0:02:09.554843

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C A L D
    C A N O E
    O R G A N
    O V E N S
    T E R S E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1666 🥳 104 ⏱️ 0:05:11.762353

🤔 105 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 16 chat prompts
🤖 16 dolphin3:latest replies
🔥  1 🥵  6 😎  8 🥶 84 🧊  5

      $1 #105 mortality       100.00°C 🥳 1000‰ ~100 used:0 [99]   source:dolphin3
      $2 #104 maternal         47.73°C 🔥  992‰   ~1 used:0 [0]    source:dolphin3
      $3  #54 survival         45.76°C 🥵  983‰   ~7 used:6 [6]    source:dolphin3
      $4  #99 fecundity        43.79°C 🥵  973‰   ~2 used:0 [1]    source:dolphin3
      $5  #88 birthrate        43.63°C 🥵  970‰   ~5 used:3 [4]    source:dolphin3
      $6  #91 fertility        42.71°C 🥵  964‰   ~3 used:1 [2]    source:dolphin3
      $7  #72 population       42.18°C 🥵  956‰   ~4 used:2 [3]    source:dolphin3
      $8  #45 predation        41.46°C 🥵  946‰   ~6 used:3 [5]    source:dolphin3
      $9  #77 reproductive     33.83°C 😎  598‰   ~8 used:0 [7]    source:dolphin3
     $10  #87 speciation       32.46°C 😎  458‰   ~9 used:0 [8]    source:dolphin3
     $11  #30 species          32.00°C 😎  411‰  ~15 used:5 [14]   source:dolphin3
     $12 #101 health           31.67°C 😎  378‰  ~10 used:0 [9]    source:dolphin3
     $17  #66 life             28.85°C 🥶        ~21 used:1 [20]   source:dolphin3
    $101  #28 plant            -0.28°C 🧊       ~101 used:0 [100]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1699 🥳 621 ⏱️ 2:24:41.713473

🤔 622 attempts
📜 1 sessions
🫧 36 chat sessions
⁉️ 187 chat prompts
🤖 70 nemotron-3-nano:30b-cloud replies
🤖 23 dolphin3:latest replies
🤖 94 gemma4:12b replies
😱   1 🔥   4 🥵  48 😎 159 🥶 350 🧊  59

      $1 #622 externe             100.00°C 🥳 1000‰ ~563 used:0   [562]  source:nemotron
      $2 #513 interne              82.86°C 😱  999‰   ~1 used:39  [0]    source:nemotron
      $3  #47 gestion              42.73°C 🔥  996‰ ~211 used:160 [210]  source:gemma4  
      $4 #143 support              41.38°C 🔥  994‰  ~52 used:90  [51]   source:gemma4  
      $5  #31 interface            40.75°C 🔥  993‰  ~40 used:47  [39]   source:gemma4  
      $6 #495 fonctionnement       40.68°C 🔥  991‰   ~6 used:11  [5]    source:nemotron
      $7 #293 fonction             40.28°C 🥵  989‰  ~41 used:5   [40]   source:gemma4  
      $8 #192 structure            40.25°C 🥵  988‰  ~42 used:5   [41]   source:gemma4  
      $9 #171 technique            39.16°C 🥵  986‰  ~43 used:5   [42]   source:gemma4  
     $10  #71 communication        38.72°C 🥵  982‰  ~44 used:5   [43]   source:gemma4  
     $11 #427 organisationnel      38.64°C 🥵  981‰  ~45 used:5   [44]   source:nemotron
     $55 #174 expertise            32.99°C 😎  899‰  ~53 used:0   [52]   source:gemma4  
    $214  #23 infrastructure       23.16°C 🥶       ~213 used:0   [212]  source:gemma4  
    $564 #156 plateau              -0.11°C 🧊       ~564 used:0   [563]  source:gemma4  
