# 2026-08-07

- 🔗 spaceword.org 🧩 2026-08-06 🏁 score 2168 ranked 51.3% 159/310 ⏱️ 2:00:38.116562
- 🔗 wordgrid 🧩 #797 🟪 rarity:0.17 ⏱️ 0:21:18.152344
- 🔗 alfagok.diginaut.net 🧩 #643 🥳 16 ⏱️ 0:00:26.887372
- 🔗 alphaguess.com 🧩 #1110 🥳 24 ⏱️ 0:00:35.733734
- 🔗 dontwordle.com 🧩 #1536 🥳 6 ⏱️ 0:01:14.297634
- 🔗 dictionary.com hurdle 🧩 #1679 😦 16 ⏱️ 0:02:32.821552
- 🔗 Quordle Classic 🧩 #1656 🥳 score:25 ⏱️ 0:02:00.225116
- 🔗 Octordle Classic 🧩 #1656 🥳 score:60 ⏱️ 0:02:18.216327
- 🔗 Sedecordle Classic 🧩 #1636 🥳 score:49 ⏱️ 0:02:40.741767
- 🔗 squareword.org 🧩 #1649 🥳 7 ⏱️ 0:02:05.245705
- 🔗 cemantle.certitudes.org 🧩 #1586 🥳 175 ⏱️ 0:04:01.448895
- 🔗 cemantix.certitudes.org 🧩 #1619 🥳 373 ⏱️ 0:05:17.695314

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



# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #797 🟪 rarity:0.17 ⏱️ 0:21:18.152344

📜 3 sessions
🌌 🌌 🦄
🌌 🌌 🦄
🦄 🦄 🦄
Rarity: 0.17 🟪

# [spaceword.org](spaceword.org) 🧩 2026-08-06 🏁 score 2168 ranked 51.3% 159/310 ⏱️ 2:00:38.116562

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 159/310

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ D I E _ _ _   
      _ _ _ _ _ _ X _ _ _   
      _ _ _ _ B O P _ _ _   
      _ _ _ U R S A _ _ _   
      _ _ _ _ E _ N _ _ _   
      _ _ _ H E A D _ _ _   
      _ _ _ _ Z _ _ _ _ _   
      _ _ _ _ E K E _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #643 🥳 16 ⏱️ 0:00:26.887372

🤔 16 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+99695  [ 99695] ex        q2  ? ␅
    @+99695  [ 99695] ex        q3  ? after
    @+111350 [111350] ge        q6  ? ␅
    @+111350 [111350] ge        q7  ? after
    @+115988 [115988] gek       q12 ? ␅
    @+115988 [115988] gek       q13 ? after
    @+118345 [118345] geluk     q14 ? ␅
    @+118345 [118345] geluk     q15 ? it
    @+118345 [118345] geluk     done. it
    @+120840 [120840] gepunt    q10 ? ␅
    @+120840 [120840] gepunt    q11 ? before
    @+130330 [130330] gracht    q8  ? ␅
    @+130330 [130330] gracht    q9  ? before
    @+149381 [149381] huis      q4  ? ␅
    @+149381 [149381] huis      q5  ? before
    @+199655 [199655] lijk      q0  ? ␅
    @+199655 [199655] lijk      q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1110 🥳 24 ⏱️ 0:00:35.733734

🤔 24 attempts
📜 1 sessions

    @        [     0] aa      
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98147  [ 98147] mac     q0  ? ␅
    @+98147  [ 98147] mac     q1  ? after
    @+122724 [122724] parol   q4  ? ␅
    @+122724 [122724] parol   q5  ? after
    @+135004 [135004] prop    q6  ? ␅
    @+135004 [135004] prop    q7  ? after
    @+138010 [138010] quetzal q10 ? ␅
    @+138010 [138010] quetzal q11 ? after
    @+138573 [138573] rad     q14 ? ␅
    @+138573 [138573] rad     q15 ? after
    @+138802 [138802] raft    q18 ? ␅
    @+138802 [138802] raft    q19 ? after
    @+138891 [138891] rail    q20 ? ␅
    @+138891 [138891] rail    q21 ? after
    @+138928 [138928] rain    q22 ? ␅
    @+138928 [138928] rain    q23 ? it
    @+138928 [138928] rain    done. it
    @+139039 [139039] rally   q16 ? ␅
    @+139039 [139039] rally   q17 ? before
    @+139510 [139510] rate    q12 ? ␅
    @+139510 [139510] rate    q13 ? before
    @+141017 [141017] recon   q8  ? ␅
    @+141017 [141017] recon   q9  ? before
    @+147311 [147311] rho     q2  ? ␅
    @+147311 [147311] rho     q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1536 🥳 6 ⏱️ 0:01:14.297634

📜 1 sessions
💰 score: 16

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:7600
    ⬜⬜⬜⬜⬜ tried:LLAMA n n n n n remain:2612
    ⬜⬜⬜⬜⬜ tried:DEEDS n n n n n remain:303
    ⬜⬜⬜⬜⬜ tried:YUKKY n n n n n remain:67
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:17
    ⬜🟨⬜⬜⬜ tried:BOFFO n m n n n remain:2

    Undos used: 2

      2 words remaining
    x 8 unused letters
    = 16 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1679 😦 16 ⏱️ 0:02:32.821552

📜 3 sessions
💰 score: 5080

    3/6
    DEANS ⬜⬜🟩🟨🟨
    SHARN 🟩⬜🟩⬜🟨
    SNACK 🟩🟩🟩🟩🟩
    3/6
    SNACK ⬜🟨🟩⬜⬜
    GRAIN 🟩🟩🟩⬜🟨
    GRAND 🟩🟩🟩🟩🟩
    4/6
    GRAND ⬜⬜🟨🟨⬜
    ACNES 🟨⬜🟨⬜⬜
    INLAY ⬜🟨⬜🟩⬜
    WOMAN 🟩🟩🟩🟩🟩
    4/6
    WOMAN ⬜⬜⬜⬜⬜
    SUITE ⬜⬜🟩🟨🟨
    EDICT 🟨🟨🟩⬜🟨
    TRIED 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜🟩🟩🟩🟩
    ????? ⬜🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1656 🥳 score:25 ⏱️ 0:02:00.225116

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. AMISS attempts:6 score:6
2. SHIRK attempts:8 score:8
3. SALSA attempts:7 score:7
4. RABBI attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1656 🥳 score:60 ⏱️ 0:02:18.216327

📜 1 sessions

Octordle Classic

1. CREST attempts:7 score:7
2. BLINK attempts:9 score:9
3. STICK attempts:6 score:6
4. SALTY attempts:4 score:4
5. ADOPT attempts:11 score:11
6. BLISS attempts:8 score:8
7. SULKY attempts:5 score:5
8. EVOKE attempts:10 score:10

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1636 🥳 score:49 ⏱️ 0:02:40.741767

📜 1 sessions

Sedecordle Classic sedecordle.com

1. HUNKY attempts:7 score:0
2. SKIFF attempts:10 score:7
3. SHANK attempts:6 score:0
4. THEFT attempts:11 score:6
5. ABBOT attempts:12 score:1
6. CHASE attempts:15 score:2
7. UNTIL attempts:3 score:0
8. STAND attempts:5 score:3
9. CACHE attempts:16 score:1
10. NYLON attempts:8 score:6
11. SNUFF attempts:9 score:0
12. MIRTH attempts:18 score:9
13. VERVE attempts:19 score:1
14. QUART attempts:13 score:9
15. UNDUE attempts:4 score:0
16. ACRID attempts:14 score:4

# [squareword.org](squareword.org) 🧩 #1649 🥳 7 ⏱️ 0:02:05.245705

📜 2 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    W A S T E
    A L P H A
    S O R E S
    P H A S E
    S A T E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1586 🥳 175 ⏱️ 0:04:01.448895

🤔 176 attempts
📜 1 sessions
🫧 14 chat sessions
⁉️ 71 chat prompts
🤖 71 dolphin3:latest replies
🥵   3 😎  11 🥶 147 🧊  14

      $1 #176 conspiracy          100.00°C 🥳 1000‰ ~162 used:0  [161]  source:dolphin3
      $2 #150 plotted              44.20°C 🥵  988‰   ~5 used:16 [4]    source:dolphin3
      $3 #133 orchestrated         35.60°C 🥵  944‰   ~6 used:26 [5]    source:dolphin3
      $4 #174 scheme               35.12°C 🥵  934‰   ~1 used:1  [0]    source:dolphin3
      $5 #152 deliberate           30.39°C 😎  863‰   ~7 used:3  [6]    source:dolphin3
      $6 #170 intentionally        26.04°C 😎  653‰   ~2 used:0  [1]    source:dolphin3
      $7 #157 contrived            24.39°C 😎  550‰   ~8 used:3  [7]    source:dolphin3
      $8  #59 concerted            23.74°C 😎  500‰  ~14 used:47 [13]   source:dolphin3
      $9 #162 deliberately         23.44°C 😎  472‰   ~3 used:1  [2]    source:dolphin3
     $10  #41 interrelated         22.49°C 😎  373‰  ~13 used:28 [12]   source:dolphin3
     $11 #169 intention            22.42°C 😎  360‰   ~4 used:0  [3]    source:dolphin3
     $12 #145 planned              21.70°C 😎  250‰   ~9 used:4  [8]    source:dolphin3
     $16 #149 scheduled            20.11°C 🥶        ~18 used:0  [17]   source:dolphin3
    $163 #121 precise              -0.38°C 🧊       ~163 used:0  [162]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1619 🥳 373 ⏱️ 0:05:17.695314

🤔 374 attempts
📜 1 sessions
🫧 15 chat sessions
⁉️ 70 chat prompts
🤖 70 dolphin3:latest replies
🔥   2 🥵  17 😎  55 🥶 257 🧊  42

      $1 #374 lot                100.00°C 🥳 1000‰ ~332 used:0  [331]  source:dolphin3
      $2 #355 gagnant             38.76°C 🔥  996‰   ~2 used:4  [1]    source:dolphin3
      $3 #358 adjudicataire       38.23°C 🔥  995‰   ~1 used:0  [0]    source:dolphin3
      $4 #357 tirage              33.99°C 🥵  987‰  ~12 used:3  [11]   source:dolphin3
      $5 #351 adjudication        33.98°C 🥵  986‰   ~6 used:2  [5]    source:dolphin3
      $6 #299 prix                32.02°C 🥵  983‰  ~60 used:12 [59]   source:dolphin3
      $7 #221 livraison           30.65°C 🥵  976‰  ~62 used:17 [61]   source:dolphin3
      $8 #147 quantité            30.20°C 🥵  971‰  ~66 used:25 [65]   source:dolphin3
      $9 #348 loterie             29.44°C 🥵  965‰   ~3 used:1  [2]    source:dolphin3
     $10 #305 vente               29.04°C 🥵  961‰  ~13 used:3  [12]   source:dolphin3
     $11 #244 commande            28.14°C 🥵  952‰  ~14 used:3  [13]   source:dolphin3
     $21 #267 réceptionner        24.85°C 😎  897‰  ~16 used:0  [15]   source:dolphin3
     $76 #283 magasin             16.24°C 🥶        ~80 used:0  [79]   source:dolphin3
    $333  #21 gastronomie         -0.04°C 🧊       ~333 used:0  [332]  source:dolphin3
