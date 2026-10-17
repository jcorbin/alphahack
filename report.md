# 2026-10-18

- 🔗 spaceword.org 🧩 2026-10-17 🏁 score 2170 ranked 31.3% 93/297 ⏱️ 0:05:17.036917
- 🔗 wordgrid 🧩 #869 🟪 rarity:0.23 ⏱️ 0:02:38.935309
- 🔗 alfagok.diginaut.net 🧩 #715 🥳 28 ⏱️ 0:00:36.111157
- 🔗 alphaguess.com 🧩 #1182 🥳 24 ⏱️ 0:00:27.375289
- 🔗 dontwordle.com 🧩 #1608 🥳 6 ⏱️ 0:01:44.834752
- 🔗 dictionary.com hurdle 🧩 #1751 🥳 15 ⏱️ 0:02:18.533299
- 🔗 Quordle Classic 🧩 #1728 🥳 score:24 ⏱️ 0:01:49.457445
- 🔗 Octordle Classic 🧩 #1728 🥳 score:59 ⏱️ 0:02:00.595581
- 🔗 Sedecordle Classic 🧩 #1708 🥳 score:52 ⏱️ 0:03:12.868267
- 🔗 cemantix.certitudes.org 🧩 #1691 🥳 656 ⏱️ 1:35:26.979455
- 🔗 squareword.org 🧩 #1721 🥳 7 ⏱️ 0:02:17.273840
- 🔗 cemantle.certitudes.org 🧩 #1658 🥳 598 ⏱️ 2:36:09.870410

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














# [spaceword.org](spaceword.org) 🧩 2026-10-17 🏁 score 2170 ranked 31.3% 93/297 ⏱️ 0:05:17.036917

📜 2 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 93/297

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ N A _ _ _ C _ _   
      _ _ E _ _ M _ Y _ _   
      _ _ I _ W E _ A _ _   
      _ _ S _ A Z O N _ _   
      _ _ T U X E D O _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #869 🟪 rarity:0.23 ⏱️ 0:02:38.935309

📜 2 sessions
🌌 🦄 🦄
🌌 🦄 🦄
🌌 🌌 🌌
Rarity: 0.23 🟪



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #715 🥳 28 ⏱️ 0:00:36.111157

🤔 28 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+49802  [ 49802] boks       q4  ? ␅
    @+49802  [ 49802] boks       q5  ? after
    @+74698  [ 74698] dc         q6  ? ␅
    @+74698  [ 74698] dc         q7  ? after
    @+77670  [ 77670] der        q12 ? ␅
    @+77670  [ 77670] der        q13 ? after
    @+77700  [ 77700] derde      q26 ? ␅
    @+77700  [ 77700] derde      q27 ? it
    @+77700  [ 77700] derde      done. it
    @+77767  [ 77767] dereguleer q24 ? ␅
    @+77767  [ 77767] dereguleer q25 ? before
    @+77871  [ 77871] des        q20 ? ␅
    @+77871  [ 77871] des        q21 ? after
    @+77871  [ 77871] des        q22 ? ␅
    @+77871  [ 77871] des        q23 ? before
    @+78412  [ 78412] detentie   q16 ? ␅
    @+78412  [ 78412] detentie   q17 ? before
    @+79171  [ 79171] dicht      q14 ? ␅
    @+79171  [ 79171] dicht      q15 ? before
    @+80829  [ 80829] dijk       q10 ? ␅
    @+80829  [ 80829] dijk       q11 ? before
    @+87155  [ 87155] draag      q8  ? ␅
    @+87155  [ 87155] draag      q9  ? before
    @+99671  [ 99671] ex         q2  ? ␅
    @+99671  [ 99671] ex         q3  ? before
    @+199630 [199630] lijk       q0  ? ␅
    @+199630 [199630] lijk       q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1182 🥳 24 ⏱️ 0:00:27.375289

🤔 24 attempts
📜 1 sessions

    @        [     0] aa           
    @+1      [     1] aah          
    @+2      [     2] aahed        
    @+3      [     3] aahing       
    @+98142  [ 98142] mac          q0  ? ␅
    @+98142  [ 98142] mac          q1  ? after
    @+147304 [147304] rho          q2  ? ␅
    @+147304 [147304] rho          q3  ? after
    @+171904 [171904] tag          q4  ? ␅
    @+171904 [171904] tag          q5  ? after
    @+181989 [181989] un           q6  ? ␅
    @+181989 [181989] un           q7  ? after
    @+185619 [185619] unretire     q10 ? ␅
    @+185619 [185619] unretire     q11 ? after
    @+186510 [186510] unwarinesses q14 ? ␅
    @+186510 [186510] unwarinesses q15 ? after
    @+186660 [186660] up           q16 ? ␅
    @+186660 [186660] up           q17 ? after
    @+186819 [186819] upheave      q20 ? ␅
    @+186819 [186819] upheave      q21 ? after
    @+186886 [186886] upper        q22 ? ␅
    @+186886 [186886] upper        q23 ? it
    @+186886 [186886] upper        done. it
    @+186978 [186978] ups          q18 ? ␅
    @+186978 [186978] ups          q19 ? before
    @+187400 [187400] us           q12 ? ␅
    @+187400 [187400] us           q13 ? before
    @+189251 [189251] vicar        q8  ? ␅
    @+189251 [189251] vicar        q9  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1608 🥳 6 ⏱️ 0:01:44.834752

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:MAMMA n n n n n remain:6571
    ⬜⬜⬜⬜⬜ tried:CEDED n n n n n remain:2074
    ⬜⬜⬜⬜⬜ tried:LUSUS n n n n n remain:373
    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:110
    ⬜🟨⬜⬜⬜ tried:FOGGY n m n n n remain:16
    ⬜🟩🟨⬜⬜ tried:PHONO n Y m n n remain:1

    Undos used: 3

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1751 🥳 15 ⏱️ 0:02:18.533299

📜 1 sessions
💰 score: 10100

    3/6
    AEONS 🟩🟨⬜🟨⬜
    ANGLE 🟩🟨⬜⬜🟨
    APNEA 🟩🟩🟩🟩🟩
    3/6
    APNEA 🟩⬜🟨🟩⬜
    ANGEL 🟩🟨⬜🟩🟨
    ALIEN 🟩🟩🟩🟩🟩
    4/6
    ALIEN ⬜⬜⬜⬜⬜
    TRUCK 🟨⬜⬜⬜⬜
    MYTHS ⬜⬜🟨🟨⬜
    PHOTO 🟩🟩🟩🟩🟩
    4/6
    PHOTO 🟨⬜⬜🟨⬜
    SETUP 🟩⬜🟨⬜🟨
    SPLIT 🟩🟩🟨🟨🟩
    SPILT 🟩🟩🟩🟩🟩
    Final 1/2
    SCOPE 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1728 🥳 score:24 ⏱️ 0:01:49.457445

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. FLINT attempts:8 score:8
2. FUROR attempts:7 score:7
3. WEDGE attempts:4 score:4
4. RODEO attempts:5 score:5

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1728 🥳 score:59 ⏱️ 0:02:00.595581

📜 1 sessions

Octordle Classic

1. NYMPH attempts:3 score:3
2. KITTY attempts:11 score:11
3. GAZER attempts:7 score:7
4. DOPEY attempts:5 score:5
5. TOPAZ attempts:6 score:6
6. CHAOS attempts:8 score:8
7. PRANK attempts:10 score:10
8. CRIED attempts:9 score:9

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1708 🥳 score:52 ⏱️ 0:03:12.868267

📜 1 sessions

Sedecordle Classic sedecordle.com

1. JAZZY attempts:17 score:1
2. BONUS attempts:14 score:7
3. SQUAD attempts:6 score:0
4. THING attempts:16 score:6
5. RAYON attempts:5 score:0
6. SONIC attempts:3 score:5
7. MONTH attempts:9 score:0
8. APRON attempts:7 score:9
9. DRYLY attempts:4 score:0
10. ABOUT attempts:8 score:4
11. ABBOT attempts:10 score:1
12. SHEET attempts:13 score:0
13. FREER attempts:18 score:1
14. STILT attempts:11 score:8
15. MADLY attempts:18 score:1
16. MODAL attempts:12 score:9

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1691 🥳 656 ⏱️ 1:35:26.979455

🤔 657 attempts
📜 2 sessions
🫧 49 chat sessions
⁉️ 243 chat prompts
🤖 51 llama3.2:latest replies
🤖 137 dolphin3:latest replies
🤖 55 gemma4:12b replies
🔥   3 🥵   5 😎  53 🥶 192 🧊 403

      $1 #657 interview        100.00°C 🥳 1000‰ ~255 used:0   [254]  source:llama3.2
      $2 #607 reportage         57.40°C 🔥  998‰   ~4 used:14  [3]    source:llama3.2
      $3 #340 extrait           45.01°C 🔥  992‰  ~21 used:137 [20]   source:dolphin3
      $4 #653 journal           44.21°C 🔥  990‰   ~1 used:1   [0]    source:llama3.2
      $5 #645 presse            37.82°C 🥵  978‰   ~2 used:0   [1]    source:llama3.2
      $6 #344 extraire          32.76°C 🥵  957‰  ~54 used:61  [53]   source:dolphin3
      $7 #102 passionnant       32.48°C 🥵  954‰  ~59 used:145 [58]   source:gemma4  
      $8 #206 express           32.20°C 🥵  953‰  ~55 used:65  [54]   source:gemma4  
      $9 #634 entretien         29.22°C 🥵  920‰   ~3 used:0   [2]    source:llama3.2
     $10 #654 conférence        26.98°C 😎  899‰   ~5 used:0   [4]    source:llama3.2
     $11 #621 journalisme       26.84°C 😎  895‰   ~6 used:1   [5]    source:llama3.2
     $12 #618 rédaction         25.77°C 😎  873‰   ~7 used:0   [6]    source:llama3.2
     $63 #357 compilation       14.62°C 🥶        ~72 used:0   [71]   source:dolphin3
    $255 #120 novateur          -0.02°C 🧊       ~256 used:0   [255]  source:gemma4  

# [squareword.org](squareword.org) 🧩 #1721 🥳 7 ⏱️ 0:02:17.273840

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
    C H A F E
    L I V E D
    A P I N G
    S P A C E
    H O N E S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1658 🥳 598 ⏱️ 2:36:09.870410

🤔 599 attempts
📜 1 sessions
🫧 45 chat sessions
⁉️ 260 chat prompts
🤖 20 gemma4:12b replies
🤖 238 dolphin3:latest replies
🔥   1 🥵  18 😎  80 🥶 482 🧊  17

      $1 #599 density           100.00°C 🥳 1000‰ ~582 used:0   [581]  source:gemma4  
      $2 #554 anisotropy         45.75°C 🔥  990‰  ~10 used:52  [9]    source:dolphin3
      $3 #575 permeability       45.66°C 🥵  989‰  ~34 used:14  [33]   source:dolphin3
      $4 #244 ellipsoidal        43.53°C 🥵  982‰  ~98 used:159 [97]   source:dolphin3
      $5 #322 topography         42.95°C 🥵  974‰  ~95 used:79  [94]   source:dolphin3
      $6 #181 toroidal           42.94°C 🥵  973‰  ~94 used:78  [93]   source:dolphin3
      $7 #591 spatial            42.42°C 🥵  968‰   ~3 used:5   [2]    source:dolphin3
      $8 #598 conductivity       42.40°C 🥵  966‰   ~1 used:1   [0]    source:gemma4  
      $9 #538 anisotropic        41.99°C 🥵  959‰   ~4 used:5   [3]    source:dolphin3
     $10 #130 topology           41.80°C 🥵  956‰  ~93 used:47  [92]   source:dolphin3
     $11 #559 inhomogeneity      41.53°C 🥵  949‰   ~5 used:5   [4]    source:dolphin3
     $21 #527 thickness          38.76°C 😎  893‰  ~12 used:1   [11]   source:dolphin3
    $102 #545 unidirectional     29.26°C 🥶       ~103 used:0   [102]  source:dolphin3
    $583  #41 charge             -0.20°C 🧊       ~583 used:0   [582]  source:gemma4  
