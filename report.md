# 2026-10-17

- 🔗 spaceword.org 🧩 2026-10-16 🏁 score 2168 ranked 40.7% 129/317 ⏱️ 3:48:47.847068
- 🔗 wordgrid 🧩 #868 🟪 rarity:0.19 ⏱️ 0:02:06.741047
- 🔗 alfagok.diginaut.net 🧩 #714 🥳 32 ⏱️ 0:00:48.030015
- 🔗 alphaguess.com 🧩 #1181 🥳 16 ⏱️ 0:00:22.266603
- 🔗 dontwordle.com 🧩 #1607 🥳 6 ⏱️ 0:01:47.948424
- 🔗 dictionary.com hurdle 🧩 #1750 🥳 15 ⏱️ 0:02:36.643901
- 🔗 Quordle Classic 🧩 #1727 🥳 score:20 ⏱️ 0:01:15.277124
- 🔗 Octordle Classic 🧩 #1727 🥳 score:62 ⏱️ 0:02:07.488372
- 🔗 Sedecordle Classic 🧩 #1707 🥳 score:43 ⏱️ 0:02:38.909503
- 🔗 squareword.org 🧩 #1720 🥳 7 ⏱️ 0:02:16.260855
- 🔗 cemantle.certitudes.org 🧩 #1657 🥳 198 ⏱️ 0:11:08.404642
- 🔗 cemantix.certitudes.org 🧩 #1690 🥳 179 ⏱️ 0:09:16.672050

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













# [spaceword.org](spaceword.org) 🧩 2026-10-16 🏁 score 2168 ranked 40.7% 129/317 ⏱️ 3:48:47.847068

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 129/317

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ T U P _ _ _ _   
      _ _ _ _ _ E _ _ _ _   
      _ _ _ _ T O _ _ _ _   
      _ _ _ K I N E _ _ _   
      _ _ _ _ B A _ _ _ _   
      _ _ _ J I G _ _ _ _   
      _ _ _ _ A E _ _ _ _   
      _ _ _ Z E S T _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #868 🟪 rarity:0.19 ⏱️ 0:02:06.741047

📜 2 sessions
🌌 🌌 🌌
🌌 🦄 🌌
🌌 🦄 🌌
Rarity: 0.19 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #714 🥳 32 ⏱️ 0:00:48.030015

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken        
    @+199631 [199631] lijk           q0  ? ␅
    @+199631 [199631] lijk           q1  ? after
    @+299532 [299532] schroot        q2  ? ␅
    @+299532 [299532] schroot        q3  ? after
    @+311818 [311818] spiert         q8  ? ␅
    @+311818 [311818] spiert         q9  ? after
    @+314713 [314713] staats         q12 ? ␅
    @+314713 [314713] staats         q13 ? after
    @+314962 [314962] staatsolie     q18 ? ␅
    @+314962 [314962] staatsolie     q19 ? after
    @+315086 [315086] staatswinkels  q20 ? ␅
    @+315086 [315086] staatswinkels  q21 ? after
    @+315144 [315144] stad           q22 ? ␅
    @+315144 [315144] stad           q23 ? after
    @+315169 [315169] stadhuis       q24 ? ␅
    @+315169 [315169] stadhuis       q25 ? after
    @+315189 [315189] stadion        q26 ? ␅
    @+315189 [315189] stadion        q27 ? after
    @+315199 [315199] stadionterrein q28 ? ␅
    @+315199 [315199] stadionterrein q29 ? after
    @+315204 [315204] stadium        q30 ? ␅
    @+315204 [315204] stadium        q31 ? it
    @+315204 [315204] stadium        done. it
    @+315209 [315209] stads          q16 ? ␅
    @+315209 [315209] stads          q17 ? before
    @+316201 [316201] standaard      q14 ? ␅
    @+316201 [316201] standaard      q15 ? before
    @+317912 [317912] stem           q10 ? ␅
    @+317912 [317912] stem           q11 ? before
    @+324114 [324114] sub            q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1181 🥳 16 ⏱️ 0:00:22.266603

🤔 16 attempts
📜 1 sessions

    @        [     0] aa      
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98142  [ 98142] mac     q0  ? ␅
    @+98142  [ 98142] mac     q1  ? after
    @+98142  [ 98142] mac     q2  ? ␅
    @+98142  [ 98142] mac     q3  ? after
    @+122718 [122718] parol   q6  ? ␅
    @+122718 [122718] parol   q7  ? after
    @+134997 [134997] prop    q8  ? ␅
    @+134997 [134997] prop    q9  ? after
    @+138003 [138003] quetzal q12 ? ␅
    @+138003 [138003] quetzal q13 ? after
    @+139503 [139503] rate    q14 ? ␅
    @+139503 [139503] rate    q15 ? it
    @+139503 [139503] rate    done. it
    @+141010 [141010] recon   q10 ? ␅
    @+141010 [141010] recon   q11 ? before
    @+147304 [147304] rho     q4  ? ␅
    @+147304 [147304] rho     q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1607 🥳 6 ⏱️ 0:01:47.948424

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:SILLS n n n n n remain:3590
    ⬜⬜⬜⬜⬜ tried:YUCKY n n n n n remain:1461
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:738
    ⬜🟨⬜⬜⬜ tried:FORGO n m n n n remain:25
    ⬜⬜🟩⬜🟩 tried:EXOME n n Y n Y remain:5
    🟩🟩🟩⬜🟩 tried:ABOVE Y Y Y n Y remain:1

    Undos used: 4

      1 words remaining
    x 6 unused letters
    = 6 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1750 🥳 15 ⏱️ 0:02:36.643901

📜 1 sessions
💰 score: 10100

    3/6
    AISLE 🟩🟨⬜⬜⬜
    AMNIC 🟩⬜🟨🟨🟨
    ACING 🟩🟩🟩🟩🟩
    3/6
    ACING 🟨⬜⬜🟨⬜
    NEARS 🟨🟨🟨🟨🟨
    SANER 🟩🟩🟩🟩🟩
    4/6
    SANER ⬜⬜⬜⬜⬜
    DOILY ⬜🟩⬜⬜⬜
    COUTH 🟨🟩🟩🟨🟩
    TOUCH 🟩🟩🟩🟩🟩
    4/6
    TOUCH ⬜⬜⬜⬜⬜
    PAIRS ⬜🟨🟩🟨⬜
    FRIAR ⬜🟩🟩🟩🟩
    BRIAR 🟩🟩🟩🟩🟩
    Final 1/2
    MOLDY 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1727 🥳 score:20 ⏱️ 0:01:15.277124

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. QUARK attempts:6 score:6
2. ENEMY attempts:4 score:4
3. SPASM attempts:3 score:3
4. BLOCK attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1727 🥳 score:62 ⏱️ 0:02:07.488372

📜 1 sessions

Octordle Classic

1. GRIME attempts:4 score:4
2. PHOTO attempts:7 score:7
3. BOXER attempts:11 score:11
4. ELATE attempts:9 score:9
5. TREND attempts:5 score:5
6. NOBLE attempts:6 score:6
7. COMIC attempts:12 score:12
8. AGILE attempts:8 score:8

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1707 🥳 score:43 ⏱️ 0:02:38.909503

📜 1 sessions

Sedecordle Classic sedecordle.com

1. HOTEL attempts:18 score:1
2. PIXIE attempts:17 score:8
3. GREET attempts:7 score:0
4. HUTCH attempts:16 score:7
5. CLOWN attempts:9 score:0
6. HURRY attempts:15 score:9
7. OCTAL attempts:3 score:0
8. ICILY attempts:4 score:3
9. BEGAN attempts:14 score:1
10. THROB attempts:10 score:4
11. DROLL attempts:5 score:0
12. SHINY attempts:13 score:5
13. PINEY attempts:12 score:1
14. DITTO attempts:6 score:2
15. THEME attempts:11 score:1
16. FLUNG attempts:8 score:1

# [squareword.org](squareword.org) 🧩 #1720 🥳 7 ⏱️ 0:02:16.260855

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    G L O B E
    R A V E N
    E X A L T
    E E R I E
    D R Y E R

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1657 🥳 198 ⏱️ 0:11:08.404642

🤔 199 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 60 chat prompts
🤖 60 dolphin3:latest replies
🥵   5 😎   6 🥶 168 🧊  19

      $1 #199 celebration    100.00°C 🥳 1000‰ ~180 used:0  [179]  source:dolphin3
      $2 #194 ceremony        56.41°C 🥵  988‰   ~3 used:6  [2]    source:dolphin3
      $3 #193 event           49.14°C 🥵  976‰   ~4 used:6  [3]    source:dolphin3
      $4 #198 anniversary     42.13°C 🥵  944‰   ~1 used:2  [0]    source:dolphin3
      $5 #197 birthday        41.63°C 🥵  938‰   ~2 used:3  [1]    source:dolphin3
      $6 #183 concert         40.81°C 🥵  930‰   ~5 used:8  [4]    source:dolphin3
      $7 #138 dance           33.85°C 😎  840‰  ~11 used:16 [10]   source:dolphin3
      $8 #168 grand           31.40°C 😎  773‰  ~10 used:6  [9]    source:dolphin3
      $9 #196 baptism         23.29°C 😎  218‰   ~6 used:0  [5]    source:dolphin3
     $10 #177 symphony        23.26°C 😎  210‰   ~9 used:3  [8]    source:dolphin3
     $11 #180 grandeur        23.12°C 😎  191‰   ~8 used:2  [7]    source:dolphin3
     $12 #170 tour            22.78°C 😎  127‰   ~7 used:1  [6]    source:dolphin3
     $13 #171 movement        21.15°C 🥶        ~25 used:0  [24]   source:dolphin3
    $181  #16 buoyancy        -0.03°C 🧊       ~181 used:0  [180]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1690 🥳 179 ⏱️ 0:09:16.672050

🤔 180 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 49 chat prompts
🤖 49 dolphin3:latest replies
🔥  1 🥵  8 😎 24 🥶 96 🧊 50

      $1 #180 illégal         100.00°C 🥳 1000‰ ~130 used:0  [129]  source:dolphin3
      $2 #177 illégalité       59.86°C 🔥  997‰   ~1 used:3  [0]    source:dolphin3
      $3 #134 interdiction     44.77°C 🥵  980‰  ~25 used:15 [24]   source:dolphin3
      $4 #169 infraction       42.03°C 🥵  966‰   ~6 used:6  [5]    source:dolphin3
      $5 #179 détournement     42.02°C 🥵  965‰   ~2 used:0  [1]    source:dolphin3
      $6 #131 sanction         40.19°C 🥵  948‰   ~7 used:10 [6]    source:dolphin3
      $7 #170 délit            39.08°C 🥵  939‰   ~4 used:2  [3]    source:dolphin3
      $8 #154 prohibition      39.05°C 🥵  938‰   ~5 used:5  [4]    source:dolphin3
      $9 #178 contrefaçon      37.87°C 🥵  927‰   ~3 used:0  [2]    source:dolphin3
     $10  #88 législation      37.57°C 🥵  921‰  ~26 used:18 [25]   source:dolphin3
     $11 #142 restriction      33.64°C 😎  861‰   ~8 used:0  [7]    source:dolphin3
     $12 #132 amende           33.28°C 😎  850‰   ~9 used:0  [8]    source:dolphin3
     $35  #91 instruction      20.68°C 🥶        ~43 used:0  [42]   source:dolphin3
    $131  #51 aptitude         -0.13°C 🧊       ~131 used:0  [130]  source:dolphin3
