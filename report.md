# 2026-11-08

- 🔗 spaceword.org 🧩 2026-11-07 🏁 score 2170 ranked 29.2% 88/301 ⏱️ 1:18:12.250585
- 🔗 wordgrid 🧩 #890 🟪 rarity:0.24 ⏱️ 0:12:59.730057
- 🔗 alfagok.diginaut.net 🧩 #736 🥳 36 ⏱️ 0:00:57.905587
- 🔗 alphaguess.com 🧩 #1203 🥳 32 ⏱️ 0:00:43.464441
- 🔗 dontwordle.com 🧩 #1629 🥳 6 ⏱️ 0:01:52.750479
- 🔗 dictionary.com hurdle 🧩 #1772 🥳 16 ⏱️ 0:03:16.712566
- 🔗 Quordle Classic 🧩 #1749 🥳 score:19 ⏱️ 0:01:49.748279
- 🔗 Octordle Classic 🧩 #1749 🥳 score:52 ⏱️ 0:01:52.582063
- 🔗 Sedecordle Classic 🧩 #1729 🥳 score:44 ⏱️ 0:04:16.578778
- 🔗 squareword.org 🧩 #1742 🥳 8 ⏱️ 0:02:09.380365
- 🔗 cemantle.certitudes.org 🧩 #1679 🥳 143 ⏱️ 0:00:55.078225
- 🔗 cemantix.certitudes.org 🧩 #1712 🥳 75 ⏱️ 0:00:49.285978

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








# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #890 🟪 rarity:0.24 ⏱️ 0:12:59.730057

📜 2 sessions
🌌 🌌 🌌
🌌 🦄 🌌
🌌 🌌 🌌
Rarity: 0.24 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-07 🏁 score 2170 ranked 29.2% 88/301 ⏱️ 1:18:12.250585

📜 2 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 88/301

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ Q _ _ _ H _ _   
      _ _ N U N C I O _ _   
      _ _ _ A _ O _ U _ _   
      _ _ G R A Z E R _ _   
      _ _ O K E _ _ S _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #736 🥳 36 ⏱️ 0:00:57.905587

🤔 36 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+199631 [199631] lijk         q0  ? ␅
    @+199631 [199631] lijk         q1  ? after
    @+199631 [199631] lijk         q2  ? ␅
    @+199631 [199631] lijk         q3  ? after
    @+199631 [199631] lijk         q4  ? ␅
    @+199631 [199631] lijk         q5  ? after
    @+199649 [199649] lijken       q34 ? ␅
    @+199649 [199649] lijken       q35 ? it
    @+199649 [199649] lijken       done. it
    @+199672 [199672] lijkje       q32 ? ␅
    @+199672 [199672] lijkje       q33 ? before
    @+199712 [199712] lijkt        q30 ? ␅
    @+199712 [199712] lijkt        q31 ? before
    @+199792 [199792] lijn         q28 ? ␅
    @+199792 [199792] lijn         q29 ? before
    @+200202 [200202] lindaan      q26 ? ␅
    @+200202 [200202] lindaan      q27 ? before
    @+200770 [200770] liquiditeit  q18 ? ␅
    @+200770 [200770] liquiditeit  q19 ? before
    @+201937 [201937] loo          q16 ? ␅
    @+201937 [201937] loo          q17 ? before
    @+205795 [205795] maatschappij q14 ? ␅
    @+205795 [205795] maatschappij q15 ? before
    @+212014 [212014] media        q12 ? ␅
    @+212014 [212014] media        q13 ? before
    @+224520 [224520] moord        q10 ? ␅
    @+224520 [224520] moord        q11 ? before
    @+249538 [249538] opi          q8  ? ␅
    @+249538 [249538] opi          q9  ? before
    @+299519 [299519] schroot      q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1203 🥳 32 ⏱️ 0:00:43.464441

🤔 32 attempts
📜 1 sessions

    @        [     0] aa        
    @+98139  [ 98139] mac       q0  ? ␅
    @+98139  [ 98139] mac       q1  ? after
    @+147300 [147300] rho       q2  ? ␅
    @+147300 [147300] rho       q3  ? after
    @+159582 [159582] slug      q6  ? ␅
    @+159582 [159582] slug      q7  ? after
    @+161084 [161084] sold      q12 ? ␅
    @+161084 [161084] sold      q13 ? after
    @+161847 [161847] sound     q14 ? ␅
    @+161847 [161847] sound     q15 ? after
    @+162208 [162208] span      q16 ? ␅
    @+162208 [162208] span      q17 ? after
    @+162409 [162409] spazz     q18 ? ␅
    @+162409 [162409] spazz     q19 ? after
    @+162455 [162455] spec      q20 ? ␅
    @+162455 [162455] spec      q21 ? after
    @+162493 [162493] specie    q26 ? ␅
    @+162493 [162493] specie    q27 ? after
    @+162500 [162500] specific  q30 ? ␅
    @+162500 [162500] specific  q31 ? it
    @+162500 [162500] specific  done. it
    @+162513 [162513] specimen  q28 ? ␅
    @+162513 [162513] specimen  q29 ? before
    @+162533 [162533] spectacle q24 ? ␅
    @+162533 [162533] spectacle q25 ? before
    @+162614 [162614] speed     q10 ? ␅
    @+162614 [162614] speed     q11 ? before
    @+165735 [165735] stint     q8  ? ␅
    @+165735 [165735] stint     q9  ? before
    @+171899 [171899] tag       q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1629 🥳 6 ⏱️ 0:01:52.750479

📜 1 sessions
💰 score: 18

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:LULUS n n n n n remain:4173
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:1955
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:888
    ⬜🟨⬜⬜⬜ tried:BOBBY n m n n n remain:122
    ⬜⬜🟨⬜⬜ tried:KNOCK n n m n n remain:20
    🟨⬜⬜🟨⬜ tried:ERROR m n n m n remain:2

    Undos used: 4

      2 words remaining
    x 9 unused letters
    = 18 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1772 🥳 16 ⏱️ 0:03:16.712566

📜 1 sessions
💰 score: 10000

    3/6
    REALS ⬜⬜⬜⬜🟨
    STONK 🟨🟨🟩⬜⬜
    GHOST 🟩🟩🟩🟩🟩
    4/6
    GHOST ⬜⬜🟩⬜⬜
    PROBE ⬜🟩🟩⬜⬜
    CROWN 🟩🟩🟩⬜🟨
    CRONY 🟩🟩🟩🟩🟩
    4/6
    CRONY ⬜⬜⬜⬜⬜
    TELIA ⬜⬜🟨⬜⬜
    FLUMP ⬜🟨🟩⬜⬜
    SKULL 🟩🟩🟩🟩🟩
    3/6
    SKULL ⬜⬜⬜🟩⬜
    DEALT ⬜🟨🟨🟩⬜
    AMPLE 🟩🟩🟩🟩🟩
    Final 2/2
    DOING ⬜🟨🟩🟩🟩
    OWING 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1749 🥳 score:19 ⏱️ 0:01:49.748279

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. GREED attempts:7 score:7
2. SPINE attempts:3 score:3
3. STONY attempts:5 score:5
4. OPIUM attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1749 🥳 score:52 ⏱️ 0:01:52.582063

📜 1 sessions

Octordle Classic

1. PROXY attempts:10 score:10
2. KNOWN attempts:7 score:7
3. BROWN attempts:5 score:5
4. MEATY attempts:9 score:9
5. EPOCH attempts:6 score:6
6. ASCOT attempts:3 score:3
7. NAVAL attempts:8 score:8
8. AMBER attempts:4 score:4

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1729 🥳 score:44 ⏱️ 0:04:16.578778

📜 3 sessions

Sedecordle Classic sedecordle.com

1. HANDY attempts:8 score:0
2. KEBAB attempts:3 score:8
3. STATE attempts:18 score:1
4. HARSH attempts:18 score:9
5. HUMAN attempts:12 score:1
6. FROST attempts:6 score:2
7. HOTLY attempts:13 score:1
8. SAVOY attempts:14 score:3
9. SNAIL attempts:5 score:0
10. VENOM attempts:15 score:5
11. MANLY attempts:10 score:1
12. PINCH attempts:17 score:0
13. FORTH attempts:9 score:0
14. AMAZE attempts:11 score:9
15. OLDER attempts:4 score:0
16. SWILL attempts:18 score:4

# [squareword.org](squareword.org) 🧩 #1742 🥳 8 ⏱️ 0:02:09.380365

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P A L E D
    E D E M A
    C A V E R
    A G E N T
    N E R D S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1679 🥳 143 ⏱️ 0:00:55.078225

🤔 144 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 40 chat prompts
🤖 40 nemotron-3-nano:30b-cloud replies
🥵   2 😎  13 🥶 117 🧊  11

      $1 #144 legend         100.00°C 🥳 1000‰ ~133 used:0  [132]  source:nemotron
      $2  #85 king            39.59°C 🥵  954‰  ~10 used:19 [9]    source:nemotron
      $3  #80 dynasty         39.15°C 🥵  951‰   ~9 used:15 [8]    source:nemotron
      $4 #118 conqueror       35.79°C 😎  883‰  ~15 used:4  [14]   source:nemotron
      $5 #123 legacy          34.65°C 😎  850‰  ~11 used:2  [10]   source:nemotron
      $6  #95 lineage         30.70°C 😎  682‰  ~12 used:2  [11]   source:nemotron
      $7  #82 empire          29.89°C 😎  628‰  ~13 used:2  [12]   source:nemotron
      $8  #89 queen           28.20°C 😎  476‰  ~14 used:2  [13]   source:nemotron
      $9 #143 majestic        28.10°C 😎  463‰   ~1 used:0  [0]    source:nemotron
     $10 #132 era             27.59°C 😎  406‰   ~2 used:0  [1]    source:nemotron
     $11 #105 majesty         27.40°C 😎  381‰   ~3 used:1  [2]    source:nemotron
     $12 #135 knighthood      26.82°C 😎  302‰   ~4 used:0  [3]    source:nemotron
     $17  #84 heraldry        24.67°C 🥶        ~23 used:0  [22]   source:nemotron
    $134   #1 astigmatism     -0.32°C 🧊       ~134 used:0  [133]  source:nemotron

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1712 🥳 75 ⏱️ 0:00:49.285978

🤔 76 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 41 chat prompts
🤖 41 nemotron-3-nano:30b-cloud replies
😎 10 🥶 45 🧊 20

     $1 #76 faculté         100.00°C 🥳 1000‰ ~56 used:0  [55]  source:nemotron
     $2 #69 aptitude         24.80°C 😎  817‰  ~2 used:6  [1]   source:nemotron
     $3 #63 intelligence     22.54°C 😎  689‰  ~8 used:11 [7]   source:nemotron
     $4 #15 discernement     20.95°C 😎  538‰ ~10 used:31 [9]   source:nemotron
     $5 #72 capacité         19.46°C 😎  368‰  ~1 used:2  [0]   source:nemotron
     $6 #20 clairvoyance     19.14°C 😎  320‰  ~9 used:17 [8]   source:nemotron
     $7 #22 décision         18.65°C 😎  234‰  ~5 used:8  [4]   source:nemotron
     $8 #23 esprit           18.53°C 😎  209‰  ~6 used:8  [5]   source:nemotron
     $9 #18 jugement         18.35°C 😎  171‰  ~7 used:8  [6]   source:nemotron
    $10 #17 distinction      17.96°C 😎   94‰  ~3 used:7  [2]   source:nemotron
    $11 #24 intuition        17.49°C 😎    2‰  ~4 used:7  [3]   source:nemotron
    $12 #71 spirituel        17.42°C 🥶       ~11 used:0  [10]  source:nemotron
    $13 #19 perception       16.16°C 🥶       ~12 used:0  [11]  source:nemotron
    $57  #2 croissant        -0.01°C 🧊       ~57 used:0  [56]  source:nemotron
