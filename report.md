# 2026-08-14

- 🔗 wordgrid 🧩 #804 🟪 rarity:0.27 ⏱️ 0:04:27.290641
- 🔗 spaceword.org 🧩 2026-08-13 🏁 score 2155 ranked 73.8% 237/321 ⏱️ 1:00:08.760529
- 🔗 alfagok.diginaut.net 🧩 #650 🥳 34 ⏱️ 0:00:56.423752
- 🔗 alphaguess.com 🧩 #1117 🥳 38 ⏱️ 0:00:59.779032
- 🔗 dontwordle.com 🧩 #1543 🤷 6 ⏱️ 0:01:49.704993
- 🔗 dictionary.com hurdle 🧩 #1686 🥳 17 ⏱️ 0:02:57.119157
- 🔗 Quordle Classic 🧩 #1663 🥳 score:26 ⏱️ 0:01:34.790969
- 🔗 Octordle Classic 🧩 #1663 🥳 score:68 ⏱️ 0:02:13.075039
- 🔗 Sedecordle Classic 🧩 #1643 🥳 score:48 ⏱️ 0:02:43.675503
- 🔗 squareword.org 🧩 #1656 🥳 8 ⏱️ 0:02:44.945075
- 🔗 cemantix.certitudes.org 🧩 #1626 🥳 134 ⏱️ 0:01:52.200025
- 🔗 cemantle.certitudes.org 🧩 #1593 🥳 163 ⏱️ 0:01:10.689913

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










# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #804 🟪 rarity:0.27 ⏱️ 0:04:27.290641

📜 2 sessions
🌌 🌌 🦄
🌌 🌌 🌌
🦄 🌌 🦄
Rarity: 0.27 🟪

# [spaceword.org](spaceword.org) 🧩 2026-08-13 🏁 score 2155 ranked 73.8% 237/321 ⏱️ 1:00:08.760529

📜 2 sessions
- tiles: 21/21
- score: 2155 bonus: +55
- rank: 237/321

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      Z I G _ _ _ _ _ _ _   
      _ _ R _ T _ _ _ _ _   
      _ _ O _ E W _ _ _ _   
      _ Q U A L I A _ _ _   
      _ _ P R E N A M E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #650 🥳 34 ⏱️ 0:00:56.423752

🤔 34 attempts
📜 1 sessions

    @       [    0] &-teken       
    @+49812 [49812] boks          q6  ? ␅
    @+49812 [49812] boks          q7  ? after
    @+74715 [74715] dc            q8  ? ␅
    @+74715 [74715] dc            q9  ? after
    @+87173 [87173] draag         q10 ? ␅
    @+87173 [87173] draag         q11 ? after
    @+93388 [93388] eet           q12 ? ␅
    @+93388 [93388] eet           q13 ? after
    @+96524 [96524] energiek      q14 ? ␅
    @+96524 [96524] energiek      q15 ? after
    @+97490 [97490] er            q16 ? ␅
    @+97490 [97490] er            q17 ? after
    @+98040 [98040] ernst         q20 ? ␅
    @+98040 [98040] ernst         q21 ? after
    @+98060 [98060] eroderen      q28 ? ␅
    @+98060 [98060] eroderen      q29 ? after
    @+98070 [98070] eronder       q30 ? ␅
    @+98070 [98070] eronder       q31 ? after
    @+98073 [98073] erop          q32 ? ␅
    @+98073 [98073] erop          q33 ? it
    @+98073 [98073] erop          done. it
    @+98082 [98082] erosie        q26 ? ␅
    @+98082 [98082] erosie        q27 ? before
    @+98150 [98150] erts          q24 ? ␅
    @+98150 [98150] erts          q25 ? before
    @+98278 [98278] es            q22 ? ␅
    @+98278 [98278] es            q23 ? before
    @+98591 [98591] etablissement q18 ? ␅
    @+98591 [98591] etablissement q19 ? before
    @+99692 [99692] ex            q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1117 🥳 38 ⏱️ 0:00:59.779032

🤔 38 attempts
📜 1 sessions

    @        [     0] aa       
    @+98147  [ 98147] mac      q0  ? ␅
    @+98147  [ 98147] mac      q1  ? after
    @+98147  [ 98147] mac      q2  ? ␅
    @+98147  [ 98147] mac      q3  ? after
    @+147311 [147311] rho      q4  ? ␅
    @+147311 [147311] rho      q5  ? after
    @+171911 [171911] tag      q6  ? ␅
    @+171911 [171911] tag      q7  ? after
    @+181996 [181996] un       q8  ? ␅
    @+181996 [181996] un       q9  ? after
    @+189258 [189258] vicar    q10 ? ␅
    @+189258 [189258] vicar    q11 ? after
    @+191038 [191038] walk     q14 ? ␅
    @+191038 [191038] walk     q15 ? after
    @+191242 [191242] war      q20 ? ␅
    @+191242 [191242] war      q21 ? after
    @+191331 [191331] warm     q22 ? ␅
    @+191331 [191331] warm     q23 ? after
    @+191384 [191384] warrant  q24 ? ␅
    @+191384 [191384] warrant  q25 ? after
    @+191413 [191413] wars     q26 ? ␅
    @+191413 [191413] wars     q27 ? after
    @+191430 [191430] wart     q28 ? ␅
    @+191430 [191430] wart     q29 ? after
    @+191440 [191440] warts    q30 ? ␅
    @+191440 [191440] warts    q31 ? after
    @+191443 [191443] warworks q34 ? ␅
    @+191443 [191443] warworks q35 ? after
    @+191445 [191445] wary     q37 ? it
    @+191445 [191445] wary     done. it

# [dontwordle.com](dontwordle.com) 🧩 #1543 🤷 6 ⏱️ 0:01:49.704993

📜 1 sessions
💰 score: 0

ELIMINATED
> Well technically I didn't Wordle!

    ⬜⬜⬜⬜⬜ tried:MADAM n n n n n remain:5246
    ⬜⬜⬜⬜⬜ tried:BESES n n n n n remain:952
    ⬜⬜⬜⬜⬜ tried:LOOKY n n n n n remain:136
    ⬜⬜⬜⬜⬜ tried:PIPIT n n n n n remain:9
    ⬜⬜🟨🟨⬜ tried:WRUNG n n m m n remain:1
    ⬛⬛⬛⬛⬛ tried:????? remain:0

    Undos used: 5

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1686 🥳 17 ⏱️ 0:02:57.119157

📜 1 sessions
💰 score: 9900

    3/6
    SPARE ⬜⬜🟩🟨⬜
    TRAIN 🟨🟩🟩⬜⬜
    CRAFT 🟩🟩🟩🟩🟩
    4/6
    CRAFT 🟨🟨🟩⬜⬜
    REACH 🟨⬜🟩🟨⬜
    SCARP 🟩🟩🟩🟩⬜
    SCARY 🟩🟩🟩🟩🟩
    4/6
    SCARY ⬜🟨🟩⬜⬜
    CHALK 🟨🟨🟩⬜⬜
    PEACH 🟩⬜🟩🟩🟩
    POACH 🟩🟩🟩🟩🟩
    4/6
    POACH ⬜⬜⬜⬜⬜
    TRIED 🟨🟨⬜🟩⬜
    MUTER ⬜🟨🟩🟩🟩
    UTTER 🟩🟩🟩🟩🟩
    Final 2/2
    BLOWN 🟩🟩🟩⬜⬜
    BLOOD 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1663 🥳 score:26 ⏱️ 0:01:34.790969

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. SEIZE attempts:4 score:4
2. MYRRH attempts:6 score:6
3. SANER attempts:9 score:9
4. GLOAT attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1663 🥳 score:68 ⏱️ 0:02:13.075039

📜 1 sessions

Octordle Classic

1. STARE attempts:5 score:5
2. KAYAK attempts:7 score:7
3. WINDY attempts:8 score:8
4. AFIRE attempts:3 score:3
5. SWEEP attempts:9 score:9
6. HOMER attempts:11 score:11
7. RUDER attempts:12 score:12
8. MEDAL attempts:13 score:13

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1643 🥳 score:48 ⏱️ 0:02:43.675503

📜 1 sessions

Sedecordle Classic sedecordle.com

1. HATER attempts:6 score:0
2. TITHE attempts:8 score:6
3. BLITZ attempts:9 score:0
4. USUAL attempts:10 score:9
5. MIDGE attempts:11 score:1
6. MACRO attempts:12 score:1
7. CRIMP attempts:13 score:1
8. SCRUB attempts:14 score:3
9. MACAW attempts:15 score:1
10. DUCHY attempts:16 score:5
11. WREST attempts:17 score:1
12. RACER attempts:19 score:7
13. FIELD attempts:18 score:1
14. OVATE attempts:3 score:8
15. LARVA attempts:4 score:0
16. MANGE attempts:7 score:4

# [squareword.org](squareword.org) 🧩 #1656 🥳 8 ⏱️ 0:02:44.945075

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C R A M
    P R I D E
    L A P E L
    I N E P T
    T E N T S

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1626 🥳 134 ⏱️ 0:01:52.200025

🤔 135 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 25 chat prompts
🤖 25 dolphin3:latest replies
🥵  2 😎 26 🥶 77 🧊 29

      $1 #135 scénario       100.00°C 🥳 1000‰ ~106 used:0  [105]  source:dolphin3
      $2  #79 anticipation    35.88°C 🥵  937‰  ~20 used:15 [19]   source:dolphin3
      $3  #93 adaptation      33.33°C 🥵  914‰  ~19 used:13 [18]   source:dolphin3
      $4  #59 tactique        30.05°C 😎  831‰  ~28 used:7  [27]   source:dolphin3
      $5  #49 stratégie       29.47°C 😎  819‰  ~26 used:5  [25]   source:dolphin3
      $6  #41 approche        28.45°C 😎  778‰  ~21 used:2  [20]   source:dolphin3
      $7 #114 situation       28.36°C 😎  772‰   ~1 used:1  [0]    source:dolphin3
      $8 #133 prédiction      28.17°C 😎  765‰   ~2 used:0  [1]    source:dolphin3
      $9 #132 perspective     27.77°C 😎  752‰   ~3 used:0  [2]    source:dolphin3
     $10 #125 anticiper       26.73°C 😎  702‰   ~4 used:0  [3]    source:dolphin3
     $11  #67 élément         26.67°C 😎  696‰  ~22 used:2  [21]   source:dolphin3
     $12  #46 méthode         25.36°C 😎  619‰  ~23 used:2  [22]   source:dolphin3
     $30  #77 objectif        19.97°C 🥶        ~32 used:0  [31]   source:dolphin3
    $107  #76 initiative      -0.34°C 🧊       ~107 used:0  [106]  source:dolphin3

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1593 🥳 163 ⏱️ 0:01:10.689913

🤔 164 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 21 chat prompts
🤖 21 dolphin3:latest replies
🔥   1 🥵   5 😎  31 🥶 115 🧊  11

      $1 #164 expansion       100.00°C 🥳 1000‰ ~153 used:0  [152]  source:dolphin3
      $2 #132 development      52.34°C 🔥  996‰   ~1 used:5  [0]    source:dolphin3
      $3  #92 project          41.51°C 🥵  981‰  ~30 used:15 [29]   source:dolphin3
      $4 #104 implementation   36.82°C 🥵  956‰   ~5 used:7  [4]    source:dolphin3
      $5 #133 infrastructure   36.07°C 🥵  948‰   ~4 used:2  [3]    source:dolphin3
      $6 #142 integration      35.57°C 🥵  939‰   ~2 used:0  [1]    source:dolphin3
      $7 #125 phase            34.04°C 🥵  920‰   ~3 used:1  [2]    source:dolphin3
      $8 #140 deployment       31.53°C 😎  871‰   ~6 used:0  [5]    source:dolphin3
      $9 #112 innovation       31.41°C 😎  867‰  ~31 used:2  [30]   source:dolphin3
     $10 #107 strategy         30.49°C 😎  852‰   ~7 used:1  [6]    source:dolphin3
     $11 #124 milestone        29.44°C 😎  829‰   ~8 used:0  [7]    source:dolphin3
     $12  #68 proposal         28.56°C 😎  804‰  ~35 used:3  [34]   source:dolphin3
     $39  #62 major            19.29°C 🥶        ~41 used:0  [40]   source:dolphin3
    $154   #2 banana           -1.31°C 🧊       ~154 used:0  [153]  source:dolphin3
