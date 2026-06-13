# 2026-06-14

- 🔗 spaceword.org 🧩 2026-06-13 🏁 score 2168 ranked 41.4% 133/321 ⏱️ 8:22:14.490358
- 🔗 alfagok.diginaut.net 🧩 #589 🥳 44 ⏱️ 0:01:02.855320
- 🔗 alphaguess.com 🧩 #1056 🥳 34 ⏱️ 0:00:34.567729
- 🔗 dontwordle.com 🧩 #1482 🥳 6 ⏱️ 0:01:54.768722
- 🔗 dictionary.com hurdle 🧩 #1625 😦 19 ⏱️ 0:03:44.521875
- 🔗 Quordle Classic 🧩 #1602 🥳 score:26 ⏱️ 0:01:49.104456
- 🔗 Octordle Classic 🧩 #1602 🥳 score:52 ⏱️ 0:03:06.409300
- 🔗 squareword.org 🧩 #1595 🥳 8 ⏱️ 0:01:54.991653
- 🔗 cemantle.certitudes.org 🧩 #1532 🥳 256 ⏱️ 0:04:37.872037
- 🔗 cemantix.certitudes.org 🧩 #1565 🥳 160 ⏱️ 0:02:37.626680

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





# [spaceword.org](spaceword.org) 🧩 2026-06-13 🏁 score 2168 ranked 41.4% 133/321 ⏱️ 8:22:14.490358

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 133/321

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ B O I L _ _ _   
      _ _ _ Y _ _ U _ _ _   
      _ _ _ _ Q _ N _ _ _   
      _ _ _ _ U _ G _ _ _   
      _ _ _ _ A J I _ _ _   
      _ _ _ A N _ _ _ _ _   
      _ _ _ _ T E W _ _ _   
      _ _ _ _ A D O _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #589 🥳 44 ⏱️ 0:01:02.855320

🤔 44 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+99704  [ 99704] ex           q4  ? ␅
    @+99704  [ 99704] ex           q5  ? after
    @+111359 [111359] ge           q8  ? ␅
    @+111359 [111359] ge           q9  ? after
    @+120849 [120849] gepunt       q12 ? ␅
    @+120849 [120849] gepunt       q13 ? after
    @+125591 [125591] gezapig      q14 ? ␅
    @+125591 [125591] gezapig      q15 ? after
    @+127752 [127752] glas         q16 ? ␅
    @+127752 [127752] glas         q17 ? after
    @+128763 [128763] goed         q18 ? ␅
    @+128763 [128763] goed         q19 ? after
    @+129543 [129543] gooi         q20 ? ␅
    @+129543 [129543] gooi         q21 ? after
    @+129808 [129808] goud         q22 ? ␅
    @+129808 [129808] goud         q23 ? after
    @+130072 [130072] gouvernement q24 ? ␅
    @+130072 [130072] gouvernement q25 ? after
    @+130140 [130140] graad        q28 ? ␅
    @+130140 [130140] graad        q29 ? after
    @+130153 [130153] graaf        q30 ? ␅
    @+130153 [130153] graaf        q31 ? after
    @+130181 [130181] graafwerk    q36 ? ␅
    @+130181 [130181] graafwerk    q37 ? after
    @+130187 [130187] graafwespen  q40 ? ␅
    @+130187 [130187] graafwespen  q41 ? after
    @+130189 [130189] graag        q42 ? ␅
    @+130189 [130189] graag        q43 ? it
    @+130189 [130189] graag        done. it
    @+130193 [130193] graai        q39 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1056 🥳 34 ⏱️ 0:00:34.567729

🤔 34 attempts
📜 1 sessions

    @        [     0] aa        
    @+98214  [ 98214] mach      q0  ? ␅
    @+98214  [ 98214] mach      q1  ? after
    @+104069 [104069] minor     q8  ? ␅
    @+104069 [104069] minor     q9  ? after
    @+104202 [104202] mis       q12 ? ␅
    @+104202 [104202] mis       q13 ? after
    @+105567 [105567] mitigator q14 ? ␅
    @+105567 [105567] mitigator q15 ? after
    @+106241 [106241] mongrel   q16 ? ␅
    @+106241 [106241] mongrel   q17 ? after
    @+106326 [106326] mono      q18 ? ␅
    @+106326 [106326] mono      q19 ? after
    @+106610 [106610] monos     q20 ? ␅
    @+106610 [106610] monos     q21 ? after
    @+106674 [106674] mons      q24 ? ␅
    @+106674 [106674] mons      q25 ? after
    @+106682 [106682] monsoon   q30 ? ␅
    @+106682 [106682] monsoon   q31 ? after
    @+106685 [106685] monster   q32 ? ␅
    @+106685 [106685] monster   q33 ? it
    @+106685 [106685] monster   done. it
    @+106693 [106693] monstrous q28 ? ␅
    @+106693 [106693] monstrous q29 ? before
    @+106709 [106709] monte     q26 ? ␅
    @+106709 [106709] monte     q27 ? before
    @+106745 [106745] moo       q22 ? ␅
    @+106745 [106745] moo       q23 ? before
    @+106935 [106935] mor       q10 ? ␅
    @+106935 [106935] mor       q11 ? before
    @+109931 [109931] ne        q7  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1482 🥳 6 ⏱️ 0:01:54.768722

📜 1 sessions
💰 score: 28

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:7870
    ⬜⬜⬜⬜⬜ tried:NANNA n n n n n remain:3327
    ⬜⬜⬜⬜⬜ tried:DOGGO n n n n n remain:1163
    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:375
    ⬜⬜⬜⬜🟩 tried:WRYLY n n n n Y remain:7
    ⬜⬜🟨⬜🟩 tried:CHEVY n n m n Y remain:4

    Undos used: 2

      4 words remaining
    x 7 unused letters
    = 28 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1625 😦 19 ⏱️ 0:03:44.521875

📜 1 sessions
💰 score: 4770

    4/6
    SAICE 🟩⬜🟩⬜🟩
    SPITE 🟩⬜🟩🟩🟩
    SMITE 🟩⬜🟩🟩🟩
    SUITE 🟩🟩🟩🟩🟩
    4/6
    SUITE 🟨⬜⬜⬜🟨
    LEARS ⬜🟨🟨⬜🟨
    ASKED 🟩🟩⬜🟩⬜
    ASHEN 🟩🟩🟩🟩🟩
    5/6
    ASHEN ⬜⬜🟨🟨⬜
    FETCH ⬜🟩⬜🟩🟩
    BELCH ⬜🟩⬜🟩🟩
    MERCH ⬜🟩🟩🟩🟩
    PERCH 🟩🟩🟩🟩🟩
    4/6
    PERCH ⬜⬜⬜⬜⬜
    LOGIN ⬜🟨⬜🟨⬜
    ADIOS ⬜⬜🟨🟨🟨
    KIOSK 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜🟩⬜🟩🟩
    ????? 🟨🟩⬜🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1602 🥳 score:26 ⏱️ 0:01:49.104456

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. WIMPY attempts:7 score:7
2. WISPY attempts:6 score:6
3. VIRAL attempts:9 score:9
4. NYLON attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1602 🥳 score:52 ⏱️ 0:03:06.409300

📜 1 sessions

Octordle Classic

1. EPOXY attempts:4 score:4
2. PURGE attempts:9 score:9
3. GLARE attempts:10 score:10
4. MODAL attempts:5 score:5
5. STOVE attempts:7 score:7
6. SPARK attempts:6 score:6
7. ETHIC attempts:8 score:8
8. IMPLY attempts:3 score:3

# [squareword.org](squareword.org) 🧩 #1595 🥳 8 ⏱️ 0:01:54.991653

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟨 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A P A C E
    M O C H A
    A U T O S
    S C O R E
    S H R E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1532 🥳 256 ⏱️ 0:04:37.872037

🤔 257 attempts
📜 1 sessions
🫧 16 chat sessions
⁉️ 76 chat prompts
🤖 76 dolphin3:latest replies
😱   1 🔥   3 🥵  14 😎  41 🥶 190 🧊   7

      $1 #257 prefer            100.00°C 🥳 1000‰ ~250 used:0  [249]  source:dolphin3
      $2 #221 want               63.87°C 😱  999‰   ~1 used:10 [0]    source:dolphin3
      $3 #255 opt                56.26°C 🔥  997‰   ~2 used:0  [1]    source:dolphin3
      $4 #226 choose             55.02°C 🔥  994‰   ~3 used:3  [2]    source:dolphin3
      $5 #224 preference         51.04°C 🔥  991‰   ~4 used:3  [3]    source:dolphin3
      $6  #61 crave              50.14°C 🥵  989‰  ~58 used:61 [57]   source:dolphin3
      $7  #95 wish               47.74°C 🥵  982‰  ~55 used:32 [54]   source:dolphin3
      $8 #223 need               47.04°C 🥵  979‰   ~5 used:0  [4]    source:dolphin3
      $9  #91 yearn              46.72°C 🥵  978‰  ~42 used:17 [41]   source:dolphin3
     $10 #155 hanker             43.26°C 🥵  968‰  ~38 used:11 [37]   source:dolphin3
     $11  #70 covet              43.16°C 🥵  967‰  ~39 used:11 [38]   source:dolphin3
     $20 #252 decide             35.36°C 😎  890‰  ~12 used:0  [11]   source:dolphin3
     $61  #68 longing            23.53°C 🥶        ~62 used:0  [61]   source:dolphin3
    $251 #190 ambitious          -0.47°C 🧊       ~251 used:0  [250]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1565 🥳 160 ⏱️ 0:02:37.626680

🤔 161 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 38 chat prompts
🤖 38 dolphin3:latest replies
🔥  1 🥵 13 😎 44 🥶 82 🧊 20

      $1 #161 sélection         100.00°C 🥳 1000‰ ~141 used:0  [140]  source:dolphin3
      $2 #119 critère            52.62°C 🔥  996‰   ~3 used:13 [2]    source:dolphin3
      $3 #160 référence          36.92°C 🥵  981‰   ~1 used:0  [0]    source:dolphin3
      $4 #130 classement         36.80°C 🥵  980‰   ~7 used:5  [6]    source:dolphin3
      $5 #137 présentation       34.82°C 🥵  969‰   ~4 used:2  [3]    source:dolphin3
      $6  #63 évaluation         34.15°C 🥵  963‰  ~58 used:24 [57]   source:dolphin3
      $7 #121 sélectivité        33.24°C 🥵  951‰   ~5 used:2  [4]    source:dolphin3
      $8  #58 recherche          31.87°C 🥵  942‰  ~56 used:15 [55]   source:dolphin3
      $9  #38 pédagogique        31.37°C 🥵  938‰  ~12 used:8  [11]   source:dolphin3
     $10  #43 académique         30.92°C 🥵  931‰  ~10 used:7  [9]    source:dolphin3
     $11  #37 programme          30.81°C 🥵  930‰  ~11 used:7  [10]   source:dolphin3
     $16 #155 catégorie          28.61°C 😎  893‰  ~13 used:0  [12]   source:dolphin3
     $60  #65 analytique         17.64°C 🥶        ~60 used:0  [59]   source:dolphin3
    $142 #142 sécurité           -0.33°C 🧊       ~142 used:0  [141]  source:dolphin3
