# 2026-04-02

- 🔗 spaceword.org 🧩 2026-04-01 🏁 score 2168 ranked 38.1% 134/352 ⏱️ 1:12:59.530887
- 🔗 alfagok.diginaut.net 🧩 2026-04-02 😦 66 ⏱️ 0:03:22.534076
- 🔗 alphaguess.com 🧩 #983 🥳 34 ⏱️ 0:00:40.535336
- 🔗 dontwordle.com 🧩 #1409 🤷 6 ⏱️ 0:01:38.752507
- 🔗 dictionary.com hurdle 🧩 #1552 😦 10 ⏱️ 0:02:03.840644
- 🔗 Quordle Classic 🧩 #1529 😦 score:27 ⏱️ 0:03:21.777867
- 🔗 Octordle Classic 🧩 #1529 🥳 score:67 ⏱️ 0:04:44.563034
- 🔗 squareword.org 🧩 #1522 🥳 7 ⏱️ 0:01:49.008767
- 🔗 cemantle.certitudes.org 🧩 #1459 🥳 168 ⏱️ 0:02:01.002471
- 🔗 cemantix.certitudes.org 🧩 #1492 🥳 130 ⏱️ 0:03:00.229201

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
































# [spaceword.org](spaceword.org) 🧩 2026-04-01 🏁 score 2168 ranked 38.1% 134/352 ⏱️ 1:12:59.530887

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 134/352

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ M _ F _ _ _ J _ _   
      _ A _ O V O L O S _   
      _ N _ E _ _ Y _ U _   
      _ E O S I N E _ Q _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 2026-04-02 😦 66 ⏱️ 0:03:22.534076

🤔 66 attempts
📜 2 sessions

    @        [     0] &-teken    
    @+199809 [199809] lijm       q0  ? ␅
    @+199809 [199809] lijm       q1  ? after
    @+211706 [211706] me         q8  ? ␅
    @+211706 [211706] me         q9  ? after
    @+217644 [217644] mijn       q10 ? ␅
    @+217644 [217644] mijn       q11 ? after
    @+217879 [217879] milieu     q36 ? ␅
    @+217879 [217879] milieu     q37 ? after
    @+217879 [217879] milieu     q38 ? ␅
    @+217879 [217879] milieu     q39 ? after
    @+218809 [218809] min        q40 ? ␅
    @+218809 [218809] min        q41 ? after
    @+218984 [218984] mini       q42 ? ␅
    @+218984 [218984] mini       q43 ? after
    @+219088 [219088] minimum    q44 ? ␅
    @+219088 [219088] minimum    q45 ? after
    @+219459 [219459] mir        q46 ? ␅
    @+219459 [219459] mir        q47 ? after
    @+219459 [219459] mir        q48 ? ␅
    @+219459 [219459] mir        q49 ? after
    @+219459 [219459] mir        <<< SEARCH
    @+219460 [219460] mirabel    q60 ? ␅
    @+219460 [219460] mirabel    q61 ? before
    @+219460 [219460] mirabel    q64 ? ␅
    @+219460 [219460] mirabel    q65 ? before
    @+219460 [219460] mirabel    >>> SEARCH
    @+219461 [219461] mirabellen q56 ? ␅
    @+219461 [219461] mirabellen q57 ? after
    @+219461 [219461] mirabellen q58 ? ␅
    @+219461 [219461] mirabellen q59 ? before

# [alphaguess.com](alphaguess.com) 🧩 #983 🥳 34 ⏱️ 0:00:40.535336

🤔 34 attempts
📜 1 sessions

    @       [    0] aa      
    @+47380 [47380] dis     q2  ? ␅
    @+47380 [47380] dis     q3  ? after
    @+72798 [72798] gremmy  q4  ? ␅
    @+72798 [72798] gremmy  q5  ? after
    @+85502 [85502] ins     q6  ? ␅
    @+85502 [85502] ins     q7  ? after
    @+91846 [91846] knot    q8  ? ␅
    @+91846 [91846] knot    q9  ? after
    @+93266 [93266] lar     q12 ? ␅
    @+93266 [93266] lar     q13 ? after
    @+93406 [93406] las     q18 ? ␅
    @+93406 [93406] las     q19 ? after
    @+93468 [93468] lat     q20 ? ␅
    @+93468 [93468] lat     q21 ? after
    @+93481 [93481] late    q24 ? ␅
    @+93481 [93481] late    q25 ? after
    @+93490 [93490] laten   q26 ? ␅
    @+93490 [93490] laten   q27 ? after
    @+93497 [93497] latens  q28 ? ␅
    @+93497 [93497] latens  q29 ? after
    @+93499 [93499] latent  q30 ? ␅
    @+93499 [93499] latent  q31 ? after
    @+93502 [93502] later   q32 ? ␅
    @+93502 [93502] later   q33 ? it
    @+93502 [93502] later   done. it
    @+93504 [93504] lateral q22 ? ␅
    @+93504 [93504] lateral q23 ? before
    @+93558 [93558] lati    q16 ? ␅
    @+93558 [93558] lati    q17 ? before
    @+93894 [93894] lea     q15 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1409 🤷 6 ⏱️ 0:01:38.752507

📜 1 sessions
💰 score: 0

ELIMINATED
> Well technically I didn't Wordle!

    ⬜⬜⬜⬜⬜ tried:WALLA n n n n n remain:5351
    ⬜⬜⬜⬜⬜ tried:DOGGO n n n n n remain:2190
    ⬜⬜⬜⬜⬜ tried:XYSTS n n n n n remain:367
    ⬜🟨⬜⬜⬜ tried:BUMPH n m n n n remain:20
    ⬜🟨🟨🟨⬜ tried:KNURR n m m m n remain:1
    ⬛⬛⬛⬛⬛ tried:????? remain:0

    Undos used: 5

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1552 😦 10 ⏱️ 0:02:03.840644

📜 1 sessions
💰 score: 1280

    4/6
    LEARS 🟨🟨⬜⬜⬜
    TILED ⬜⬜🟨🟩⬜
    VOWEL ⬜🟩🟩🟩🟩
    BOWEL 🟩🟩🟩🟩🟩
    6/6
    ????? ⬜⬜⬜🟨⬜
    ????? ⬜⬜⬜🟨🟨
    ????? ⬜🟨🟨🟨🟨
    ????? ⬜🟨🟨🟨🟨
    ????? 🟩🟩🟩🟩⬜
    ????? 🟩🟩🟩🟩⬜

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1529 😦 score:27 ⏱️ 0:03:21.777867

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. LEAPT attempts:4 score:4
2. _E__A ~M -BDFGIKLNOPRSTW M:1 attempts:9 score:-1
3. TRAIT attempts:6 score:6
4. REFER attempts:8 score:8

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1529 🥳 score:67 ⏱️ 0:04:44.563034

📜 1 sessions

Octordle Classic

1. ROUND attempts:6 score:6
2. COVER attempts:9 score:9
3. SPELT attempts:4 score:4
4. ASHEN attempts:7 score:7
5. VIGOR attempts:10 score:10
6. ABLED attempts:11 score:11
7. CAGEY attempts:10 score:12
8. DOUGH attempts:8 score:8

# [squareword.org](squareword.org) 🧩 #1522 🥳 7 ⏱️ 0:01:49.008767

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A P A R T
    M O W E R
    A P A C E
    S P I C E
    S A T E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1459 🥳 168 ⏱️ 0:02:01.002471

🤔 169 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 22 chat prompts
🤖 22 dolphin3:latest replies
🔥   1 🥵  10 😎  33 🥶 123 🧊   1

      $1 #169 jet              100.00°C 🥳 1000‰ ~168 used:0  [167]  source:dolphin3
      $2 #124 aircraft          71.71°C 🔥  998‰   ~2 used:5  [1]    source:dolphin3
      $3 #168 helicopter        53.84°C 🔥  990‰   ~1 used:0  [0]    source:dolphin3
      $4 #167 airship           44.33°C 🥵  974‰   ~3 used:0  [2]    source:dolphin3
      $5 #133 fuselage          44.04°C 🥵  971‰   ~8 used:2  [7]    source:dolphin3
      $6 #147 cockpit           42.42°C 🥵  965‰   ~4 used:0  [3]    source:dolphin3
      $7 #127 cabin             39.36°C 🥵  951‰   ~5 used:1  [4]    source:dolphin3
      $8 #138 landing           38.46°C 🥵  944‰   ~6 used:0  [5]    source:dolphin3
      $9  #18 engine            36.97°C 🥵  933‰  ~42 used:18 [41]   source:dolphin3
     $10 #139 lavatory          34.89°C 🥵  918‰   ~7 used:0  [6]    source:dolphin3
     $11  #22 air               34.35°C 🥵  909‰  ~41 used:13 [40]   source:dolphin3
     $13 #103 locomotive        33.20°C 😎  895‰  ~43 used:2  [42]   source:dolphin3
     $46  #47 valve             18.04°C 🥶        ~45 used:0  [44]   source:dolphin3
    $169  #76 block             -0.39°C 🧊       ~169 used:0  [168]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1492 🥳 130 ⏱️ 0:03:00.229201

🤔 131 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 15 chat prompts
🤖 15 dolphin3:latest replies
🔥  1 🥵  6 😎 29 🥶 65 🧊 29

      $1 #131 équitable           100.00°C 🥳 1000‰ ~102 used:0 [101]  source:dolphin3
      $2 #105 durable              49.99°C 🔥  996‰   ~1 used:5 [0]    source:dolphin3
      $3 #112 égalité              42.50°C 🥵  989‰   ~2 used:1 [1]    source:dolphin3
      $4 #111 transparence         36.85°C 🥵  972‰   ~3 used:0 [2]    source:dolphin3
      $5 #120 pérenne              36.72°C 🥵  971‰   ~4 used:0 [3]    source:dolphin3
      $6 #101 solidarité           36.27°C 🥵  968‰   ~5 used:0 [4]    source:dolphin3
      $7 #109 responsabilisation   32.28°C 🥵  932‰   ~6 used:0 [5]    source:dolphin3
      $8  #91 engagement           30.94°C 🥵  901‰   ~7 used:0 [6]    source:dolphin3
      $9 #107 gouvernance          30.49°C 😎  893‰   ~8 used:0 [7]    source:dolphin3
     $10  #60 développement        29.90°C 😎  879‰  ~35 used:5 [34]   source:dolphin3
     $11 #117 durablement          29.30°C 😎  857‰   ~9 used:0 [8]    source:dolphin3
     $12 #127 pérennité            28.89°C 😎  849‰  ~10 used:0 [9]    source:dolphin3
     $38  #56 amélioration         18.21°C 🥶        ~41 used:0 [40]   source:dolphin3
    $103 #114 résistant            -0.33°C 🧊       ~103 used:0 [102]  source:dolphin3
