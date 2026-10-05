# 2026-10-06

- 🔗 wordgrid 🧩 #857 🟪 rarity:0.16 ⏱️ 0:03:51.379868
- 🔗 spaceword.org 🧩 2026-10-05 🏁 score 2160 ranked 64.5% 202/313 ⏱️ 0:56:05.125212
- 🔗 alfagok.diginaut.net 🧩 #703 🥳 16 ⏱️ 0:00:28.076626
- 🔗 alphaguess.com 🧩 #1170 🥳 28 ⏱️ 0:00:43.318279
- 🔗 dontwordle.com 🧩 #1596 🥳 6 ⏱️ 0:01:19.371442
- 🔗 dictionary.com hurdle 🧩 #1739 🥳 21 ⏱️ 0:03:25.132684
- 🔗 Quordle Classic 🧩 #1716 🥳 score:25 ⏱️ 0:01:49.174560
- 🔗 Octordle Classic 🧩 #1716 🥳 score:70 ⏱️ 0:02:21.404052
- 🔗 Sedecordle Classic 🧩 #1696 🥳 score:46 ⏱️ 0:03:32.357176
- 🔗 squareword.org 🧩 #1709 🥳 7 ⏱️ 0:01:56.470487
- 🔗 cemantle.certitudes.org 🧩 #1646 🥳 187 ⏱️ 0:17:13.138974
- 🔗 cemantix.certitudes.org 🧩 #1679 🥳 252 ⏱️ 0:56:52.529021

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


# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #857 🟪 rarity:0.16 ⏱️ 0:03:51.379868

📜 2 sessions
🦄 🦄 🌌
🌌 🌌 🌌
🌌 🦄 🌌
Rarity: 0.16 🟪

# [spaceword.org](spaceword.org) 🧩 2026-10-05 🏁 score 2160 ranked 64.5% 202/313 ⏱️ 0:56:05.125212

📜 3 sessions
- tiles: 21/21
- score: 2160 bonus: +60
- rank: 202/313

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ T _ _ _ C _   
      _ _ _ W O O L E R _   
      _ G O O N I E _ U _   
      _ _ _ _ G _ X _ _ _   
      _ E K E S _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #703 🥳 16 ⏱️ 0:00:28.076626

🤔 16 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199528 [199528] lij       q0  ? ␅
    @+199528 [199528] lij       q1  ? after
    @+299480 [299480] schrok    q2  ? ␅
    @+299480 [299480] schrok    q3  ? after
    @+349464 [349464] vakanties q4  ? ␅
    @+349464 [349464] vakanties q5  ? after
    @+361903 [361903] vervolg   q8  ? ␅
    @+361903 [361903] vervolg   q9  ? after
    @+365008 [365008] vind      q12 ? ␅
    @+365008 [365008] vind      q13 ? after
    @+366408 [366408] vlees     q14 ? ␅
    @+366408 [366408] vlees     q15 ? it
    @+366408 [366408] vlees     done. it
    @+368149 [368149] voedsel   q10 ? ␅
    @+368149 [368149] voedsel   q11 ? before
    @+374458 [374458] vrijsta   q6  ? ␅
    @+374458 [374458] vrijsta   q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1170 🥳 28 ⏱️ 0:00:43.318279

🤔 28 attempts
📜 1 sessions

    @       [    0] aa       
    @+2     [    2] aahed    
    @+11763 [11763] back     q6  ? ␅
    @+11763 [11763] back     q7  ? after
    @+13801 [13801] be       q10 ? ␅
    @+13801 [13801] be       q11 ? after
    @+15757 [15757] bewrap   q12 ? ␅
    @+15757 [15757] bewrap   q13 ? after
    @+16727 [16727] bios     q14 ? ␅
    @+16727 [16727] bios     q15 ? after
    @+17209 [17209] blab     q16 ? ␅
    @+17209 [17209] blab     q17 ? after
    @+17222 [17222] black    q20 ? ␅
    @+17222 [17222] black    q21 ? after
    @+17341 [17341] blacktop q22 ? ␅
    @+17341 [17341] blacktop q23 ? after
    @+17359 [17359] blade    q26 ? ␅
    @+17359 [17359] blade    q27 ? it
    @+17359 [17359] blade    done. it
    @+17391 [17391] blame    q24 ? ␅
    @+17391 [17391] blame    q25 ? before
    @+17458 [17458] blarney  q18 ? ␅
    @+17458 [17458] blarney  q19 ? before
    @+17714 [17714] blind    q8  ? ␅
    @+17714 [17714] blind    q9  ? before
    @+23680 [23680] camp     q4  ? ␅
    @+23680 [23680] camp     q5  ? before
    @+47374 [47374] dis      q2  ? ␅
    @+47374 [47374] dis      q3  ? before
    @+98142 [98142] mac      q0  ? ␅
    @+98142 [98142] mac      q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1596 🥳 6 ⏱️ 0:01:19.371442

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:KABAB n n n n n remain:5942
    ⬜⬜⬜⬜⬜ tried:MIMIC n n n n n remain:2754
    ⬜⬜⬜⬜⬜ tried:LULUS n n n n n remain:639
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:263
    ⬜🟨⬜⬜⬜ tried:FOGGY n m n n n remain:23
    🟩⬜⬜⬜🟨 tried:OZONE Y n n n m remain:2

    Undos used: 3

      2 words remaining
    x 7 unused letters
    = 14 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1739 🥳 21 ⏱️ 0:03:25.132684

📜 1 sessions
💰 score: 9500

    5/6
    SNARE ⬜⬜⬜⬜🟨
    HOLED ⬜⬜⬜🟩⬜
    BICEP ⬜⬜⬜🟩⬜
    AWFUL ⬜🟩⬜⬜⬜
    TWEET 🟩🟩🟩🟩🟩
    4/6
    TWEET ⬜🟨⬜⬜⬜
    ADOWN ⬜⬜🟩🟩🟩
    CHUGS ⬜🟩⬜⬜🟨
    SHOWN 🟩🟩🟩🟩🟩
    4/6
    SHOWN ⬜⬜⬜⬜⬜
    ARIEL ⬜🟩⬜⬜⬜
    FRUMP ⬜🟩⬜⬜🟨
    CRYPT 🟩🟩🟩🟩🟩
    6/6
    CRYPT ⬜🟨⬜⬜⬜
    RAKES 🟨⬜⬜🟩⬜
    MIRED ⬜⬜🟨🟩🟨
    FIGHT ⬜⬜⬜⬜⬜
    WALTZ ⬜⬜🟨⬜⬜
    OLDER 🟩🟩🟩🟩🟩
    Final 2/2
    HULKY 🟩⬜🟩⬜🟩
    HILLY 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1716 🥳 score:25 ⏱️ 0:01:49.174560

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. FRESH attempts:4 score:4
2. SKULK attempts:7 score:7
3. BATCH attempts:9 score:9
4. ENSUE attempts:5 score:5

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1716 🥳 score:70 ⏱️ 0:02:21.404052

📜 4 sessions

Octordle Classic

1. NURSE attempts:5 score:5
2. CHIEF attempts:6 score:6
3. CLOCK attempts:8 score:8
4. PRICE attempts:7 score:7
5. LEAPT attempts:10 score:10
6. YEARN attempts:9 score:9
7. STOOP attempts:12 score:12
8. ODDER attempts:13 score:13

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1696 🥳 score:46 ⏱️ 0:03:32.357176

📜 2 sessions

Sedecordle Classic sedecordle.com

1. REACT attempts:9 score:0
2. CARRY attempts:10 score:9
3. RUGBY attempts:12 score:1
4. PLIER attempts:17 score:2
5. FOLIO attempts:18 score:1
6. GOURD attempts:11 score:8
7. STAGE attempts:13 score:1
8. PLIED attempts:18 score:3
9. GROSS attempts:14 score:1
10. NAIVE attempts:3 score:4
11. ROUSE attempts:18 score:2
12. BLOOD attempts:15 score:0
13. DRUNK attempts:8 score:0
14. ROCKY attempts:7 score:8
15. EDICT attempts:6 score:0
16. SEMEN attempts:5 score:6

# [squareword.org](squareword.org) 🧩 #1709 🥳 7 ⏱️ 0:01:56.470487

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C L A S H
    H I P P O
    A V I A N
    S I N C E
    E D G E S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1646 🥳 187 ⏱️ 0:17:13.138974

🤔 188 attempts
📜 2 sessions
🫧 13 chat sessions
⁉️ 69 chat prompts
🤖 30 gemma4:12b replies
🤖 39 dolphin3:latest replies
🔥   1 🥵   6 😎  26 🥶 125 🧊  29

      $1 #188 withdrawal       100.00°C 🥳 1000‰ ~159 used:0  [158]  source:gemma4  
      $2  #55 deployment        40.61°C 🔥  990‰   ~2 used:86 [1]    source:dolphin3
      $3 #186 resumption        38.94°C 🥵  987‰   ~1 used:0  [0]    source:gemma4  
      $4 #173 reinstatement     35.30°C 🥵  971‰  ~24 used:11 [23]   source:gemma4  
      $5 #177 reversal          32.26°C 🥵  945‰   ~4 used:10 [3]    source:gemma4  
      $6 #165 reversion         31.98°C 🥵  941‰   ~3 used:9  [2]    source:gemma4  
      $7 #114 implementation    31.52°C 🥵  933‰  ~30 used:28 [29]   source:dolphin3
      $8 #125 transition        30.18°C 🥵  904‰  ~25 used:16 [24]   source:dolphin3
      $9 #176 recovery          29.90°C 😎  899‰   ~5 used:0  [4]    source:gemma4  
     $10 #147 stabilization     28.33°C 😎  854‰  ~26 used:2  [25]   source:gemma4  
     $11 #143 finalization      28.24°C 😎  850‰   ~6 used:1  [5]    source:gemma4  
     $12 #157 completion        28.07°C 😎  847‰   ~7 used:0  [6]    source:gemma4  
     $35 #135 migration         19.71°C 🥶        ~40 used:0  [39]   source:gemma4  
    $160  #49 equipment         -0.03°C 🧊       ~160 used:0  [159]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1679 🥳 252 ⏱️ 0:56:52.529021

🤔 253 attempts
📜 1 sessions
🫧 15 chat sessions
⁉️ 86 chat prompts
🤖 60 gemma4:12b replies
🤖 26 dolphin3:latest replies
🔥   3 🥵  14 😎  53 🥶 172 🧊  10

      $1 #253 grandeur         100.00°C 🥳 1000‰ ~243 used:0  [242]  source:gemma4  
      $2  #53 absolu            45.55°C 🔥  996‰  ~15 used:53 [14]   source:gemma4  
      $3  #95 infini            43.72°C 🔥  994‰  ~14 used:41 [13]   source:gemma4  
      $4 #217 intrinsèque       41.93°C 🔥  991‰   ~1 used:17 [0]    source:gemma4  
      $5 #116 suprême           40.49°C 🥵  985‰  ~16 used:10 [15]   source:gemma4  
      $6 #156 invariable        39.93°C 🥵  982‰   ~9 used:4  [8]    source:gemma4  
      $7 #243 divin             39.66°C 🥵  981‰  ~10 used:4  [9]    source:gemma4  
      $8 #140 entier            38.95°C 🥵  976‰  ~11 used:4  [10]   source:gemma4  
      $9 #139 prodigieux        38.48°C 🥵  972‰   ~2 used:3  [1]    source:gemma4  
     $10 #119 constant          38.14°C 🥵  970‰  ~12 used:4  [11]   source:gemma4  
     $11 #229 admirable         37.84°C 🥵  969‰  ~13 used:4  [12]   source:gemma4  
     $19  #93 immuable          33.89°C 😎  890‰  ~17 used:0  [16]   source:gemma4  
     $72  #78 évident           24.88°C 🥶        ~71 used:0  [70]   source:gemma4  
    $244 #200 plénier           -1.06°C 🧊       ~244 used:0  [243]  source:gemma4  
