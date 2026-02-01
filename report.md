# 2026-02-02

- 🔗 spaceword.org 🧩 2026-02-01 🏁 score 2170 ranked 16.6% 58/349 ⏱️ 0:45:33.078759
- 🔗 alfagok.diginaut.net 🧩 #457 🥳 42 ⏱️ 0:00:43.431538
- 🔗 alphaguess.com 🧩 #924 🥳 28 ⏱️ 0:00:26.535572
- 🔗 dontwordle.com 🧩 #1350 🥳 6 ⏱️ 0:02:24.720110
- 🔗 dictionary.com hurdle 🧩 #1493 🥳 21 ⏱️ 0:03:27.288914
- 🔗 Quordle Classic 🧩 #1470 🥳 score:30 ⏱️ 0:01:54.265545
- 🔗 Octordle Classic 🧩 #1470 🥳 score:65 ⏱️ 0:04:16.402173
- 🔗 squareword.org 🧩 #1463 🥳 8 ⏱️ 0:02:06.440163
- 🔗 cemantle.certitudes.org 🧩 #1400 🥳 336 ⏱️ 0:03:38.520357
- 🔗 cemantix.certitudes.org 🧩 #1433 🥳 14 ⏱️ 0:00:08.419409
- 🔗 Quordle Rescue 🧩 #84 🥳 score:23 ⏱️ 0:01:44.977066
- 🔗 Octordle Rescue 🧩 #1470 😦 score:5 ⏱️ 0:04:20.115130

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


















# [spaceword.org](spaceword.org) 🧩 2026-02-01 🏁 score 2170 ranked 16.6% 58/349 ⏱️ 0:45:33.078759

📜 3 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 58/349

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      O R T _ Y _ B _ _ R   
      X I _ P I R O Q U E   
      _ A Z I N E _ _ _ I   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #457 🥳 42 ⏱️ 0:00:43.431538

🤔 42 attempts
📜 1 sessions

    @        [     0] &-teken            
    @+99750  [ 99750] ex                 q2  ? ␅
    @+99750  [ 99750] ex                 q3  ? after
    @+149446 [149446] huis               q4  ? ␅
    @+149446 [149446] huis               q5  ? after
    @+153617 [153617] in                 q10 ? ␅
    @+153617 [153617] in                 q11 ? after
    @+154661 [154661] indruis            q16 ? ␅
    @+154661 [154661] indruis            q17 ? after
    @+155132 [155132] info               q18 ? ␅
    @+155132 [155132] info               q19 ? after
    @+155416 [155416] informaties        q20 ? ␅
    @+155416 [155416] informaties        q21 ? after
    @+155538 [155538] infra              q22 ? ␅
    @+155538 [155538] infra              q23 ? after
    @+155571 [155571] infrastructuur     q26 ? ␅
    @+155571 [155571] infrastructuur     q27 ? after
    @+155589 [155589] infusie            q28 ? ␅
    @+155589 [155589] infusie            q29 ? after
    @+155593 [155593] infuus             q30 ? ␅
    @+155593 [155593] infuus             q31 ? after
    @+155603 [155603] infuusvloeistoffen q32 ? ␅
    @+155603 [155603] infuusvloeistoffen q33 ? after
    @+155606 [155606] inga               q34 ? ␅
    @+155606 [155606] inga               q35 ? after
    @+155607 [155607] ingaan             q40 ? ␅
    @+155607 [155607] ingaan             q41 ? it
    @+155607 [155607] ingaan             done. it
    @+155608 [155608] ingaand            q38 ? ␅
    @+155608 [155608] ingaand            q39 ? before
    @+155609 [155609] ingaande           q37 ? before

# [alphaguess.com](alphaguess.com) 🧩 #924 🥳 28 ⏱️ 0:00:26.535572

🤔 28 attempts
📜 1 sessions

    @       [    0] aa     
    @+2     [    2] aahed  
    @+47382 [47382] dis    q2  ? ␅
    @+47382 [47382] dis    q3  ? after
    @+72801 [72801] gremmy q4  ? ␅
    @+72801 [72801] gremmy q5  ? after
    @+73573 [73573] guess  q14 ? ␅
    @+73573 [73573] guess  q15 ? after
    @+73964 [73964] gusset q16 ? ␅
    @+73964 [73964] gusset q17 ? after
    @+73994 [73994] gut    q22 ? ␅
    @+73994 [73994] gut    q23 ? after
    @+74004 [74004] guts   q26 ? ␅
    @+74004 [74004] guts   q27 ? it
    @+74004 [74004] guts   done. it
    @+74018 [74018] gutter q24 ? ␅
    @+74018 [74018] gutter q25 ? before
    @+74058 [74058] gweduc q20 ? ␅
    @+74058 [74058] gweduc q21 ? before
    @+74160 [74160] gyps   q18 ? ␅
    @+74160 [74160] gyps   q19 ? before
    @+74362 [74362] had    q12 ? ␅
    @+74362 [74362] had    q13 ? before
    @+75957 [75957] haw    q10 ? ␅
    @+75957 [75957] haw    q11 ? before
    @+79133 [79133] hood   q8  ? ␅
    @+79133 [79133] hood   q9  ? before
    @+85505 [85505] ins    q6  ? ␅
    @+85505 [85505] ins    q7  ? before
    @+98220 [98220] mach   q0  ? ␅
    @+98220 [98220] mach   q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1350 🥳 6 ⏱️ 0:02:24.720110

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:YAPPY n n n n n remain:5357
    ⬜⬜⬜⬜⬜ tried:BIBBS n n n n n remain:1225
    ⬜⬜⬜⬜⬜ tried:JUGUM n n n n n remain:593
    ⬜⬜🟨⬜⬜ tried:CHOCK n n m n n remain:149
    ⬜🟨⬜⬜⬜ tried:LOTTO n m n n n remain:16
    🟩⬜⬜🟩⬜ tried:OFFED Y n n Y n remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1493 🥳 21 ⏱️ 0:03:27.288914

📜 1 sessions
💰 score: 9500

    5/6
    ARLES ⬜🟨⬜🟨⬜
    PETRI ⬜🟩⬜🟨⬜
    REDUB 🟩🟩⬜🟩⬜
    RECUR 🟩🟩⬜🟩🟨
    RERUN 🟩🟩🟩🟩🟩
    6/6
    RERUN ⬜⬜⬜🟩⬜
    AFOUL ⬜⬜🟩🟩⬜
    SPOUT 🟩⬜🟩🟩🟩
    SCOUT 🟩⬜🟩🟩🟩
    SHOUT 🟩⬜🟩🟩🟩
    STOUT 🟩🟩🟩🟩🟩
    4/6
    STOUT 🟩⬜⬜⬜⬜
    SPEAR 🟩⬜⬜🟨⬜
    SCALD 🟩⬜🟩🟩⬜
    SMALL 🟩🟩🟩🟩🟩
    5/6
    SMALL 🟩⬜⬜⬜⬜
    SPORT 🟩⬜⬜⬜⬜
    SNICK 🟩⬜🟩⬜⬜
    SEIZE 🟩🟨🟩⬜⬜
    SHIED 🟩🟩🟩🟩🟩
    Final 1/2
    SADLY 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1470 🥳 score:30 ⏱️ 0:01:54.265545

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. TIARA attempts:6 score:6
2. THANK attempts:7 score:7
3. SEVER attempts:9 score:9
4. STINT attempts:8 score:8

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1470 🥳 score:65 ⏱️ 0:04:16.402173

📜 1 sessions

Octordle Classic

1. SURER attempts:12 score:12
2. ULCER attempts:8 score:8
3. FLECK attempts:6 score:6
4. MIDST attempts:5 score:5
5. NOISE attempts:3 score:3
6. CRAFT attempts:7 score:7
7. HELLO attempts:11 score:11
8. ALTER attempts:6 score:13

# [squareword.org](squareword.org) 🧩 #1463 🥳 8 ⏱️ 0:02:06.440163

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P I K Y
    M A N N A
    O D D E R
    C R I E D
    K E E L S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1400 🥳 336 ⏱️ 0:03:38.520357

🤔 337 attempts
📜 2 sessions
🫧 13 chat sessions
⁉️ 59 chat prompts
🤖 59 dolphin3:latest replies
🔥   2 🥵   7 😎  26 🥶 289 🧊  12

      $1 #337            rat  100.00°C 🥳 1000‰ ~325  used:0  [324] source:dolphin3
      $2 #328          snake   56.20°C 🔥  997‰   ~1  used:2    [0] source:dolphin3
      $3   #3            cat   53.28°C 🔥  994‰   ~4 used:95    [3] source:dolphin3
      $4 #336         lizard   48.19°C 🥵  982‰   ~2  used:0    [1] source:dolphin3
      $5 #333           frog   46.99°C 🥵  979‰   ~3  used:0    [2] source:dolphin3
      $6  #73          mouse   46.51°C 🥵  975‰  ~35 used:32   [34] source:dolphin3
      $7 #193         kitten   45.88°C 🥵  970‰  ~34 used:12   [33] source:dolphin3
      $8   #5            dog   43.94°C 🥵  959‰   ~5 used:10    [4] source:dolphin3
      $9  #11         feline   42.76°C 🥵  951‰   ~6 used:10    [5] source:dolphin3
     $10  #22         animal   42.68°C 🥵  950‰   ~7 used:10    [6] source:dolphin3
     $11 #325       elephant   39.46°C 😎  894‰   ~8  used:0    [7] source:dolphin3
     $12 #270      carnivore   38.67°C 😎  872‰   ~9  used:0    [8] source:dolphin3
     $37  #16            fur   28.64°C 🥶        ~36  used:0   [35] source:dolphin3
    $326 #150        history   -0.21°C 🧊       ~326  used:0  [325] source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1433 🥳 14 ⏱️ 0:00:08.419409

🤔 15 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 2 chat prompts
🤖 2 dolphin3:latest replies
🥶 11 🧊  3

     $1 #15 brillant  100.00°C 🥳 1000‰ ~12 used:0  [11] source:dolphin3
     $2 #11   soleil   24.79°C 🥶        ~1 used:1   [0] source:dolphin3
     $3  #1    amour   18.47°C 🥶        ~2 used:0   [1] source:dolphin3
     $4  #3      car   16.43°C 🥶        ~3 used:0   [2] source:dolphin3
     $5  #8    livre   13.97°C 🥶        ~4 used:0   [3] source:dolphin3
     $6 #10    river    7.51°C 🥶        ~5 used:0   [4] source:dolphin3
     $7  #6   fleuve    6.49°C 🥶        ~6 used:0   [5] source:dolphin3
     $8  #5     city    5.10°C 🥶        ~7 used:0   [6] source:dolphin3
     $9 #14    école    4.91°C 🥶        ~8 used:0   [7] source:dolphin3
    $10  #9     pain    3.13°C 🥶        ~9 used:0   [8] source:dolphin3
    $11 #13  voiture    2.46°C 🥶       ~10 used:0   [9] source:dolphin3
    $12  #4    chien    2.00°C 🥶       ~11 used:0  [10] source:dolphin3
    $13  #7   jardin   -0.84°C 🧊       ~13 used:0  [12] source:dolphin3
    $14  #2     book   -2.00°C 🧊       ~14 used:0  [13] source:dolphin3

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #84 🥳 score:23 ⏱️ 0:01:44.977066

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. SPOIL attempts:5 score:5
2. UNFIT attempts:6 score:6
3. GRAZE attempts:8 score:8
4. WHINE attempts:4 score:4

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1470 😦 score:5 ⏱️ 0:04:20.115130

📜 3 sessions

Octordle Rescue

1. GIDDY attempts:6 score:6
2. UNION attempts:7 score:7
3. FUNKY attempts:8 score:8
4. HAIRY attempts:9 score:9
5. S__A_ ~R -CDEFGHIKLMNOPTUVWY A:1 R:1 attempts:13 score:-1
6. ROVER attempts:11 score:11
7. LAGER attempts:10 score:-1
8. _ASTE -CDFGHIKLMNOPRUVWY attempts:13 score:-1
