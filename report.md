# 2026-08-09

- 🔗 spaceword.org 🧩 2026-08-08 🏁 score 2173 ranked 5.6% 17/302 ⏱️ 0:52:07.076884
- 🔗 wordgrid 🧩 #799 🟪 rarity:0.19 ⏱️ 0:03:57.340169
- 🔗 alfagok.diginaut.net 🧩 #645 🥳 46 ⏱️ 0:01:38.090664
- 🔗 alphaguess.com 🧩 #1112 🥳 28 ⏱️ 0:00:38.133868
- 🔗 dontwordle.com 🧩 #1538 🥳 6 ⏱️ 0:01:19.203056
- 🔗 dictionary.com hurdle 🧩 #1681 😦 16 ⏱️ 0:03:29.028472
- 🔗 Quordle Classic 🧩 #1658 😦 score:25 ⏱️ 0:03:27.066057
- 🔗 Octordle Classic 🧩 #1658 🥳 score:64 ⏱️ 0:02:25.710882
- 🔗 Sedecordle Classic 🧩 #1638 🥳 score:41 ⏱️ 0:03:05.962257
- 🔗 squareword.org 🧩 #1651 🥳 6 ⏱️ 0:01:51.581831
- 🔗 cemantle.certitudes.org 🧩 #1588 🥳 137 ⏱️ 0:01:10.619190
- 🔗 cemantix.certitudes.org 🧩 #1621 🥳 429 ⏱️ 0:11:06.725115

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





# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #799 🟪 rarity:0.19 ⏱️ 0:03:57.340169

📜 3 sessions
🌌 🌌 🌌
🦄 🌌 🦄
🦄 🦄 🦄
Rarity: 0.19 🟪

# [spaceword.org](spaceword.org) 🧩 2026-08-08 🏁 score 2173 ranked 5.6% 17/302 ⏱️ 0:52:07.076884

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 17/302

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ J _ Z A P P I E R   
      _ I _ _ T O Y _ _ I   
      _ N E W S I E R _ A   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #645 🥳 46 ⏱️ 0:01:38.090664

🤔 46 attempts
📜 2 sessions

    @        [     0] &-teken        
    @+199549 [199549] lij            q0  ? ␅
    @+199549 [199549] lij            q1  ? after
    @+199549 [199549] lij            q2  ? ␅
    @+199549 [199549] lij            q3  ? after
    @+299515 [299515] schrok         q4  ? ␅
    @+299515 [299515] schrok         q5  ? after
    @+349503 [349503] vakanties      q6  ? ␅
    @+349503 [349503] vakanties      q7  ? after
    @+374498 [374498] vrijst         q8  ? ␅
    @+374498 [374498] vrijst         q9  ? after
    @+386882 [386882] winkel         q10 ? ␅
    @+386882 [386882] winkel         q11 ? after
    @+392883 [392883] zelf           q12 ? ␅
    @+392883 [392883] zelf           q13 ? after
    @+396187 [396187] zonde          q14 ? ␅
    @+396187 [396187] zonde          q15 ? after
    @+396985 [396985] zout           q18 ? ␅
    @+396985 [396985] zout           q19 ? after
    @+397169 [397169] zuid           q20 ? ␅
    @+397169 [397169] zuid           q21 ? after
    @+397239 [397239] zuid-rhodesië  q36 ? ␅
    @+397239 [397239] zuid-rhodesië  q37 ? .
    @+397241 [397241] zuid-soedanese q34 ? ␅
    @+397241 [397241] zuid-soedanese q35 ? .
    @+397253 [397253] zuidas         q40 ? ␅
    @+397253 [397253] zuidas         q41 ? after
    @+397266 [397266] zuidelijk      q42 ? ␅
    @+397266 [397266] zuidelijk      q43 ? after
    @+397275 [397275] zuiden         q45 ? it
    @+397275 [397275] zuiden         done. it

# [alphaguess.com](alphaguess.com) 🧩 #1112 🥳 28 ⏱️ 0:00:38.133868

🤔 28 attempts
📜 1 sessions

    @       [    0] aa           
    @+2     [    2] aahed        
    @+23680 [23680] camp         q6  ? ␅
    @+23680 [23680] camp         q7  ? after
    @+29600 [29600] circuit      q10 ? ␅
    @+29600 [29600] circuit      q11 ? after
    @+29957 [29957] clairaudient q18 ? ␅
    @+29957 [29957] clairaudient q19 ? after
    @+30131 [30131] classic      q20 ? ␅
    @+30131 [30131] classic      q21 ? after
    @+30222 [30222] clave        q22 ? ␅
    @+30222 [30222] clave        q23 ? after
    @+30258 [30258] clay         q24 ? ␅
    @+30258 [30258] clay         q25 ? after
    @+30279 [30279] clean        q26 ? ␅
    @+30279 [30279] clean        q27 ? it
    @+30279 [30279] clean        done. it
    @+30314 [30314] clear        q16 ? ␅
    @+30314 [30314] clear        q17 ? before
    @+31075 [31075] coagencies   q14 ? ␅
    @+31075 [31075] coagencies   q15 ? before
    @+32549 [32549] color        q12 ? ␅
    @+32549 [32549] color        q13 ? before
    @+35522 [35522] convention   q8  ? ␅
    @+35522 [35522] convention   q9  ? before
    @+47378 [47378] dis          q4  ? ␅
    @+47378 [47378] dis          q5  ? before
    @+98147 [98147] mac          q0  ? ␅
    @+98147 [98147] mac          q1  ? after
    @+98147 [98147] mac          q2  ? ␅
    @+98147 [98147] mac          q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1538 🥳 6 ⏱️ 0:01:19.203056

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:COCOS n n n n n remain:3958
    ⬜⬜⬜⬜⬜ tried:DUDDY n n n n n remain:1746
    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:769
    ⬜⬜⬜⬜🟩 tried:PHPHT n n n n Y remain:59
    🟩⬜⬜⬜🟩 tried:ABAFT Y n n n Y remain:7
    🟩⬜🟩⬜🟩 tried:AGENT Y n Y n Y remain:3

    Undos used: 2

      3 words remaining
    x 8 unused letters
    = 24 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1681 😦 16 ⏱️ 0:03:29.028472

📜 1 sessions
💰 score: 5060

    4/6
    ARLES 🟨⬜⬜🟨⬜
    MENTA ⬜🟩⬜🟩🟨
    DEATH ⬜🟩🟩🟩🟩
    HEATH 🟩🟩🟩🟩🟩
    3/6
    HEATH ⬜⬜⬜🟨🟩
    TOUGH 🟨⬜🟨⬜🟩
    DUTCH 🟩🟩🟩🟩🟩
    4/6
    DUTCH ⬜⬜🟩⬜🟨
    HATES 🟨🟩🟩🟨⬜
    LATHE ⬜🟩🟩🟩🟩
    BATHE 🟩🟩🟩🟩🟩
    3/6
    BATHE ⬜⬜⬜⬜🟨
    OLDER 🟨⬜🟩🟨⬜
    ENDOW 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜🟩⬜🟩🟩
    ????? ⬜🟩⬜🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1658 😦 score:25 ⏱️ 0:03:27.066057

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. _APP_ -CDEFGHILNORSTUWXY attempts:9 score:-1
2. WIDEN attempts:7 score:7
3. FOLIO attempts:4 score:4
4. STEEP attempts:5 score:5

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1658 🥳 score:64 ⏱️ 0:02:25.710882

📜 1 sessions

Octordle Classic

1. STORK attempts:7 score:7
2. RELAX attempts:8 score:8
3. SILKY attempts:9 score:9
4. LUNCH attempts:10 score:10
5. REVUE attempts:4 score:4
6. SAPPY attempts:11 score:11
7. CROOK attempts:12 score:12
8. DROIT attempts:3 score:3

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1638 🥳 score:41 ⏱️ 0:03:05.962257

📜 1 sessions

Sedecordle Classic sedecordle.com

1. SPUNK attempts:6 score:0
2. UNITE attempts:3 score:6
3. SHORE attempts:9 score:0
4. MOIST attempts:7 score:9
5. BEGUN attempts:4 score:0
6. CRASH attempts:8 score:4
7. NEWLY attempts:10 score:1
8. BONEY attempts:11 score:0
9. HUMUS attempts:12 score:1
10. SHINY attempts:18 score:2
11. ENEMA attempts:13 score:1
12. CHIRP attempts:14 score:3
13. WOMEN attempts:15 score:1
14. MOWER attempts:16 score:5
15. POSIT attempts:17 score:1
16. PHOTO attempts:18 score:7

# [squareword.org](squareword.org) 🧩 #1651 🥳 6 ⏱️ 0:01:51.581831

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P O I L
    T O N N E
    A L I E N
    F I O R D
    F O N T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1588 🥳 137 ⏱️ 0:01:10.619190

🤔 138 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 17 chat prompts
🤖 17 dolphin3:latest replies
🔥  2 🥵  9 😎 24 🥶 96 🧊  6

      $1 #138 timing         100.00°C 🥳 1000‰ ~132 used:0  [131]  source:dolphin3
      $2  #92 coincidental    47.19°C 🔥  998‰   ~2 used:10 [1]    source:dolphin3
      $3 #107 coincidence     38.21°C 🔥  993‰   ~1 used:6  [0]    source:dolphin3
      $4 #100 unanticipated   36.31°C 🥵  982‰   ~3 used:1  [2]    source:dolphin3
      $5  #89 unforeseen      34.02°C 🥵  971‰  ~10 used:4  [9]    source:dolphin3
      $6  #94 fortuitous      33.91°C 🥵  970‰   ~4 used:0  [3]    source:dolphin3
      $7 #119 serendipity     31.67°C 🥵  951‰   ~5 used:0  [4]    source:dolphin3
      $8 #113 happenstance    31.65°C 🥵  949‰   ~6 used:0  [5]    source:dolphin3
      $9  #66 unpredictable   30.52°C 🥵  932‰  ~11 used:7  [10]   source:dolphin3
     $10 #101 unexpected      29.95°C 🥵  924‰   ~7 used:0  [6]    source:dolphin3
     $11  #98 serendipitous   29.90°C 🥵  921‰   ~8 used:0  [7]    source:dolphin3
     $13  #19 uncertainty     28.68°C 😎  883‰  ~35 used:6  [34]   source:dolphin3
     $37  #36 geometry        20.43°C 🥶        ~36 used:0  [35]   source:dolphin3
    $133 #127 poisoning       -0.70°C 🧊       ~133 used:0  [132]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1621 🥳 429 ⏱️ 0:11:06.725115

🤔 430 attempts
📜 1 sessions
🫧 32 chat sessions
⁉️ 166 chat prompts
🤖 166 dolphin3:latest replies
🥵   6 😎  36 🥶 242 🧊 145

      $1 #430 photographe         100.00°C 🥳 1000‰ ~285 used:0  [284]  source:dolphin3
      $2 #429 peintre              41.22°C 🥵  970‰   ~1 used:0  [0]    source:dolphin3
      $3 #424 illustrateur         41.21°C 🥵  969‰   ~2 used:0  [1]    source:dolphin3
      $4 #419 graphiste            39.70°C 🥵  958‰   ~5 used:2  [4]    source:dolphin3
      $5 #408 artiste              38.65°C 🥵  951‰   ~6 used:8  [5]    source:dolphin3
      $6 #421 dessinateur          33.68°C 🥵  925‰   ~3 used:0  [2]    source:dolphin3
      $7 #425 maquettiste          33.59°C 🥵  923‰   ~4 used:0  [3]    source:dolphin3
      $8 #360 talentueux           29.86°C 😎  870‰  ~39 used:32 [38]   source:dolphin3
      $9 #284 superbe              29.24°C 😎  863‰  ~42 used:68 [41]   source:dolphin3
     $10 #214 passionné            29.10°C 😎  862‰  ~41 used:66 [40]   source:dolphin3
     $11 #420 designer             29.09°C 😎  861‰   ~7 used:0  [6]    source:dolphin3
     $12 #256 magnifique           28.62°C 😎  851‰  ~37 used:20 [36]   source:dolphin3
     $44 #249 attachant            16.84°C 🥶        ~55 used:0  [54]   source:dolphin3
    $286  #37 écologie             -0.02°C 🧊       ~286 used:0  [285]  source:dolphin3
