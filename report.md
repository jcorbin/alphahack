# 2026-10-09

- 🔗 spaceword.org 🧩 2026-10-08 🏁 score 2173 ranked 5.5% 18/327 ⏱️ 0:06:38.802436
- 🔗 wordgrid 🧩 #860 🟪 rarity:0.24 ⏱️ 0:02:14.512994
- 🔗 alfagok.diginaut.net 🧩 #706 🥳 24 ⏱️ 0:00:31.005826
- 🔗 alphaguess.com 🧩 #1173 🥳 26 ⏱️ 0:00:31.172276
- 🔗 dontwordle.com 🧩 #1599 🥳 6 ⏱️ 0:00:57.312363
- 🔗 dictionary.com hurdle 🧩 #1742 🥳 17 ⏱️ 0:04:31.357340
- 🔗 Quordle Classic 🧩 #1719 🥳 score:24 ⏱️ 0:01:21.451928
- 🔗 Octordle Classic 🧩 #1719 🥳 score:59 ⏱️ 0:03:14.789540
- 🔗 Sedecordle Classic 🧩 #1699 🥳 score:43 ⏱️ 0:02:51.896051
- 🔗 squareword.org 🧩 #1712 🥳 7 ⏱️ 0:03:16.526096
- 🔗 cemantle.certitudes.org 🧩 #1649 🥳 48 ⏱️ 0:00:58.966616
- 🔗 cemantix.certitudes.org 🧩 #1682 🥳 121 ⏱️ 0:09:00.268608

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





# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #860 🟪 rarity:0.24 ⏱️ 0:02:14.512994

📜 2 sessions
🌌 🌌 🌌
🌌 🦄 🦄
🦄 🌌 🌌
Rarity: 0.24 🟪

# [spaceword.org](spaceword.org) 🧩 2026-10-08 🏁 score 2173 ranked 5.5% 18/327 ⏱️ 0:06:38.802436

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 18/327

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ V _ P I R O Q U E   
      _ I _ A _ O _ I _ D   
      _ D U Y K E R S _ H   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #706 🥳 24 ⏱️ 0:00:31.005826

🤔 24 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+99672  [ 99672] ex         q2  ? ␅
    @+99672  [ 99672] ex         q3  ? after
    @+124571 [124571] gevoel     q6  ? ␅
    @+124571 [124571] gevoel     q7  ? after
    @+125268 [125268] gewild     q16 ? ␅
    @+125268 [125268] gewild     q17 ? after
    @+125433 [125433] gewrocht   q20 ? ␅
    @+125433 [125433] gewrocht   q21 ? after
    @+125466 [125466] gezag      q22 ? ␅
    @+125466 [125466] gezag      q23 ? it
    @+125466 [125466] gezag      done. it
    @+125604 [125604] gezel      q18 ? ␅
    @+125604 [125604] gezel      q19 ? before
    @+125981 [125981] gezondheid q14 ? ␅
    @+125981 [125981] gezondheid q15 ? before
    @+127649 [127649] glamour    q12 ? ␅
    @+127649 [127649] glamour    q13 ? before
    @+130741 [130741] gras       q10 ? ␅
    @+130741 [130741] gras       q11 ? before
    @+137057 [137057] handt      q8  ? ␅
    @+137057 [137057] handt      q9  ? before
    @+149567 [149567] huishoud   q4  ? ␅
    @+149567 [149567] huishoud   q5  ? before
    @+199528 [199528] lij        q0  ? ␅
    @+199528 [199528] lij        q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1173 🥳 26 ⏱️ 0:00:31.172276

🤔 26 attempts
📜 1 sessions

    @        [     0] aa           
    @+1      [     1] aah          
    @+2      [     2] aahed        
    @+3      [     3] aahing       
    @+98142  [ 98142] mac          q0  ? ␅
    @+98142  [ 98142] mac          q1  ? after
    @+122089 [122089] par          q4  ? ␅
    @+122089 [122089] par          q5  ? after
    @+134684 [134684] progress     q6  ? ␅
    @+134684 [134684] progress     q7  ? after
    @+140506 [140506] rec          q8  ? ␅
    @+140506 [140506] rec          q9  ? after
    @+143769 [143769] rem          q10 ? ␅
    @+143769 [143769] rem          q11 ? after
    @+143778 [143778] remain       q24 ? ␅
    @+143778 [143778] remain       q25 ? it
    @+143778 [143778] remain       done. it
    @+143791 [143791] reman        q22 ? ␅
    @+143791 [143791] reman        q23 ? before
    @+143842 [143842] remate       q20 ? ␅
    @+143842 [143842] remate       q21 ? before
    @+143926 [143926] remineralize q18 ? ␅
    @+143926 [143926] remineralize q19 ? before
    @+144086 [144086] removal      q16 ? ␅
    @+144086 [144086] removal      q17 ? before
    @+144402 [144402] rep          q14 ? ␅
    @+144402 [144402] rep          q15 ? before
    @+145182 [145182] res          q12 ? ␅
    @+145182 [145182] res          q13 ? before
    @+147305 [147305] rho          q2  ? ␅
    @+147305 [147305] rho          q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1599 🥳 6 ⏱️ 0:00:57.312363

📜 1 sessions
💰 score: 16

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:BOFFO n n n n n remain:7320
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:4452
    ⬜⬜⬜⬜⬜ tried:CIRRI n n n n n remain:1396
    ⬜⬜⬜⬜⬜ tried:MUMUS n n n n n remain:246
    ⬜⬜⬜⬜🟩 tried:PHPHT n n n n Y remain:11
    🟩⬜⬜🟩🟩 tried:AVANT Y n n Y Y remain:2

    Undos used: 1

      2 words remaining
    x 8 unused letters
    = 16 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1742 🥳 17 ⏱️ 0:04:31.357340

📜 1 sessions
💰 score: 9900

    3/6
    SNORE ⬜⬜⬜⬜🟩
    PLATE ⬜🟩🟩⬜🟩
    BLAME 🟩🟩🟩🟩🟩
    5/6
    BLAME ⬜🟨⬜⬜⬜
    LOUIS 🟨⬜⬜⬜⬜
    GHYLL ⬜⬜🟩🟩⬜
    DRYLY ⬜🟩🟩🟩🟩
    WRYLY 🟩🟩🟩🟩🟩
    4/6
    WRYLY ⬜⬜⬜⬜⬜
    STOAE ⬜⬜🟨⬜⬜
    CHINO ⬜🟨⬜🟩🟨
    HOUND 🟩🟩🟩🟩🟩
    4/6
    HOUND ⬜🟨⬜⬜⬜
    TELOS 🟨⬜⬜🟨⬜
    ORBIT 🟩⬜⬜🟩🟨
    OPTIC 🟩🟩🟩🟩🟩
    Final 1/2
    BLESS 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1719 🥳 score:24 ⏱️ 0:01:21.451928

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. OLDEN attempts:5 score:5
2. DUNCE attempts:4 score:4
3. SWATH attempts:7 score:7
4. HILLY attempts:8 score:8

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1719 🥳 score:59 ⏱️ 0:03:14.789540

📜 1 sessions

Octordle Classic

1. DRIFT attempts:8 score:8
2. HAVOC attempts:9 score:9
3. GRIMY attempts:5 score:5
4. ABYSS attempts:6 score:6
5. NASTY attempts:3 score:3
6. HEADY attempts:10 score:10
7. TOPIC attempts:7 score:7
8. BONGO attempts:11 score:11

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1699 🥳 score:43 ⏱️ 0:02:51.896051

📜 1 sessions

Sedecordle Classic sedecordle.com

1. PEACH attempts:7 score:0
2. MOVER attempts:17 score:7
3. SCOUR attempts:16 score:1
4. SOOTH attempts:17 score:6
5. SPIKY attempts:15 score:1
6. CUBIC attempts:12 score:5
7. SHELL attempts:11 score:1
8. BLARE attempts:14 score:1
9. INEPT attempts:3 score:0
10. SMITE attempts:10 score:3
11. SOBER attempts:13 score:1
12. DOWNY attempts:9 score:3
13. HILLY attempts:6 score:0
14. WRECK attempts:17 score:6
15. WHACK attempts:8 score:0
16. QUOTE attempts:5 score:8

# [squareword.org](squareword.org) 🧩 #1712 🥳 7 ⏱️ 0:03:16.526096

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    M E N D S
    A D I E U
    R E N A L
    S M E L L
    H A S T Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1649 🥳 48 ⏱️ 0:00:58.966616

🤔 49 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 7 chat prompts
🤖 7 dolphin3:latest replies
🔥  1 🥵  6 😎 13 🥶 28

     $1 #49 sheep      100.00°C 🥳 1000‰ ~49 used:0 [48]  source:dolphin3
     $2 #23 cow         60.82°C 🔥  992‰  ~1 used:4 [0]   source:dolphin3
     $3 #47 pig         58.36°C 🥵  989‰  ~2 used:0 [1]   source:dolphin3
     $4 #48 rabbit      51.15°C 🥵  971‰  ~3 used:0 [2]   source:dolphin3
     $5 #44 horse       47.62°C 🥵  942‰  ~4 used:0 [3]   source:dolphin3
     $6 #31 farm        47.45°C 🥵  940‰  ~5 used:0 [4]   source:dolphin3
     $7 #10 animal      47.14°C 🥵  938‰  ~7 used:7 [6]   source:dolphin3
     $8 #27 deer        46.64°C 🥵  936‰  ~6 used:2 [5]   source:dolphin3
     $9 #25 bull        40.21°C 😎  812‰  ~8 used:0 [7]   source:dolphin3
    $10 #13 dog         39.55°C 😎  794‰  ~9 used:1 [8]   source:dolphin3
    $11 #29 beef        38.83°C 😎  765‰ ~10 used:0 [9]   source:dolphin3
    $12 #11 bird        38.32°C 😎  746‰ ~11 used:0 [10]  source:dolphin3
    $13 #12 cat         38.32°C 😎  745‰ ~12 used:0 [11]  source:dolphin3
    $22 #38 mountain    28.59°C 🥶       ~21 used:0 [20]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1682 🥳 121 ⏱️ 0:09:00.268608

🤔 122 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 36 chat prompts
🤖 6 gemma4:12b replies
🤖 30 dolphin3:latest replies
🔥  1 🥵  5 😎 10 🥶 94 🧊 11

      $1 #122 paquet        100.00°C 🥳 1000‰ ~111 used:0  [110]  source:gemma4  
      $2   #1 bonbon         39.41°C 🔥  993‰   ~2 used:55 [1]    source:dolphin3
      $3 #104 boîte          37.94°C 🥵  988‰   ~1 used:2  [0]    source:gemma4  
      $4  #74 carambar       33.98°C 🥵  975‰  ~14 used:18 [13]   source:dolphin3
      $5  #32 biscuit        33.97°C 🥵  974‰  ~13 used:12 [12]   source:dolphin3
      $6  #80 sucette        31.03°C 🥵  942‰   ~3 used:8  [2]    source:dolphin3
      $7  #64 friandise      29.57°C 🥵  911‰   ~4 used:8  [3]    source:dolphin3
      $8  #39 petit          28.03°C 😎  864‰  ~15 used:2  [14]   source:dolphin3
      $9  #78 sandwich       27.51°C 😎  843‰   ~5 used:0  [4]    source:dolphin3
     $10  #34 feuille        26.78°C 😎  808‰   ~6 used:1  [5]    source:dolphin3
     $11  #11 chocolat       24.20°C 😎  587‰  ~16 used:2  [15]   source:dolphin3
     $12  #13 gâteau         24.05°C 😎  563‰   ~7 used:1  [6]    source:dolphin3
     $18 #114 assortiment    20.14°C 🥶        ~17 used:0  [16]   source:gemma4  
    $112  #69 campagne       -0.17°C 🧊       ~112 used:0  [111]  source:dolphin3
