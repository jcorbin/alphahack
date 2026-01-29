# 2026-01-30

- 🔗 spaceword.org 🧩 2026-01-29 🏁 score 2173 ranked 6.9% 25/363 ⏱️ 1:30:40.148733
- 🔗 alfagok.diginaut.net 🧩 #454 🥳 32 ⏱️ 0:00:36.928945
- 🔗 alphaguess.com 🧩 #921 🥳 18 ⏱️ 0:00:25.255131
- 🔗 dontwordle.com 🧩 #1347 🥳 6 ⏱️ 0:03:06.498522
- 🔗 dictionary.com hurdle 🧩 #1490 🥳 20 ⏱️ 0:04:01.312220
- 🔗 Quordle Classic 🧩 #1467 🥳 score:24 ⏱️ 0:01:43.959410
- 🔗 Octordle Classic 🧩 #1467 🥳 score:52 ⏱️ 0:02:23.527041
- 🔗 squareword.org 🧩 #1460 🥳 7 ⏱️ 0:01:40.723567
- 🔗 cemantle.certitudes.org 🧩 #1397 🥳 234 ⏱️ 0:09:52.199816
- 🔗 cemantix.certitudes.org 🧩 #1430 🥳 151 ⏱️ 1:06:16.148392
- 🔗 Quordle Rescue 🧩 #81 🥳 score:22 ⏱️ 0:01:11.360320
- 🔗 Octordle Rescue 🧩 #1467 🥳 score:9 ⏱️ 0:02:55.481618

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















# [spaceword.org](spaceword.org) 🧩 2026-01-29 🏁 score 2173 ranked 6.9% 25/363 ⏱️ 1:30:40.148733

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 25/363

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ K _ B E H A V E D   
      _ U N I S E X _ A I   
      _ E _ G _ _ _ U R D   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #454 🥳 32 ⏱️ 0:00:36.928945

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken          
    @+199833 [199833] lijm             q0  ? ␅
    @+199833 [199833] lijm             q1  ? after
    @+299738 [299738] schub            q2  ? ␅
    @+299738 [299738] schub            q3  ? after
    @+349512 [349512] vakantie         q4  ? ␅
    @+349512 [349512] vakantie         q5  ? after
    @+374253 [374253] vrij             q6  ? ␅
    @+374253 [374253] vrij             q7  ? after
    @+386794 [386794] wind             q8  ? ␅
    @+386794 [386794] wind             q9  ? after
    @+393211 [393211] zelfmoord        q10 ? ␅
    @+393211 [393211] zelfmoord        q11 ? after
    @+394806 [394806] zigzag           q14 ? ␅
    @+394806 [394806] zigzag           q15 ? after
    @+395583 [395583] zo               q16 ? ␅
    @+395583 [395583] zo               q17 ? after
    @+395985 [395985] zomer            q18 ? ␅
    @+395985 [395985] zomer            q19 ? after
    @+396192 [396192] zomert           q20 ? ␅
    @+396192 [396192] zomert           q21 ? after
    @+396273 [396273] zondag           q22 ? ␅
    @+396273 [396273] zondag           q23 ? after
    @+396307 [396307] zondags          q24 ? ␅
    @+396307 [396307] zondags          q25 ? after
    @+396363 [396363] zondagvoormiddag q26 ? ␅
    @+396363 [396363] zondagvoormiddag q27 ? after
    @+396367 [396367] zonde            q30 ? ␅
    @+396367 [396367] zonde            q31 ? it
    @+396367 [396367] zonde            done. it
    @+396388 [396388] zonderling       q29 ? before

# [alphaguess.com](alphaguess.com) 🧩 #921 🥳 18 ⏱️ 0:00:25.255131

🤔 18 attempts
📜 1 sessions

    @        [     0] aa     
    @+1      [     1] aah    
    @+2      [     2] aahed  
    @+3      [     3] aahing 
    @+98220  [ 98220] mach   q0  ? ␅
    @+98220  [ 98220] mach   q1  ? after
    @+147373 [147373] rhotic q2  ? ␅
    @+147373 [147373] rhotic q3  ? after
    @+159490 [159490] slop   q6  ? ␅
    @+159490 [159490] slop   q7  ? after
    @+162477 [162477] spec   q10 ? ␅
    @+162477 [162477] spec   q11 ? after
    @+164003 [164003] squab  q12 ? ␅
    @+164003 [164003] squab  q13 ? after
    @+164357 [164357] stack  q16 ? ␅
    @+164357 [164357] stack  q17 ? it
    @+164357 [164357] stack  done. it
    @+164731 [164731] star   q14 ? ␅
    @+164731 [164731] star   q15 ? before
    @+165532 [165532] stick  q8  ? ␅
    @+165532 [165532] stick  q9  ? before
    @+171643 [171643] ta     q4  ? ␅
    @+171643 [171643] ta     q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1347 🥳 6 ⏱️ 0:03:06.498522

📜 2 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:ALLAY n n n n n remain:4781
    ⬜⬜⬜⬜⬜ tried:WIDOW n n n n n remain:1025
    ⬜🟨⬜⬜🟨 tried:BECKS n m n n m remain:64
    🟩⬜🟨⬜⬜ tried:STENT Y n m n n remain:9
    🟩⬜🟨🟩⬜ tried:SQUEG Y n m Y n remain:3
    🟩🟩⬜🟩🟩 tried:SURER Y Y n Y Y remain:1

    Undos used: 4

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1490 🥳 20 ⏱️ 0:04:01.312220

📜 1 sessions
💰 score: 9600

    4/6
    ROSET ⬜⬜🟨🟩⬜
    PANES ⬜⬜⬜🟩🟨
    SKIED 🟩🟨⬜🟩⬜
    SLEEK 🟩🟩🟩🟩🟩
    5/6
    SLEEK ⬜⬜⬜⬜⬜
    AMINO ⬜⬜⬜⬜⬜
    CRWTH ⬜⬜⬜⬜⬜
    FUDGY ⬜🟩⬜🟨🟩
    GUPPY 🟩🟩🟩🟩🟩
    5/6
    GUPPY ⬜⬜⬜⬜⬜
    TIRES ⬜🟨🟨⬜⬜
    CHAIR ⬜🟩⬜🟨🟨
    WHIRL ⬜🟩🟩🟨⬜
    RHINO 🟩🟩🟩🟩🟩
    4/6
    RHINO ⬜🟩🟩⬜⬜
    CHIPS 🟨🟩🟩⬜⬜
    THICK ⬜🟩🟩🟩⬜
    WHICH 🟩🟩🟩🟩🟩
    Final 2/2
    KIDDY 🟩🟩⬜⬜🟩
    KITTY 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1467 🥳 score:24 ⏱️ 0:01:43.959410

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. STOKE attempts:8 score:8
2. BLOKE attempts:7 score:7
3. RENEW attempts:4 score:4
4. OVERT attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1467 🥳 score:52 ⏱️ 0:02:23.527041

📜 2 sessions

Octordle Classic

1. HOARD attempts:9 score:9
2. FLUNG attempts:3 score:3
3. GULCH attempts:4 score:4
4. EQUIP attempts:5 score:5
5. STERN attempts:6 score:6
6. WHARF attempts:7 score:7
7. GRIND attempts:8 score:8
8. NOVEL attempts:10 score:10

# [squareword.org](squareword.org) 🧩 #1460 🥳 7 ⏱️ 0:01:40.723567

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟩 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A S C O T
    S H O N E
    S A L S A
    E L D E R
    T E S T Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1397 🥳 234 ⏱️ 0:09:52.199816

🤔 235 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 70 chat prompts
🤖 70 dolphin3:latest replies
🔥   2 🥵  10 😎  21 🥶 189 🧊  12

      $1 #235   ~1 opposite        used: 0 source:dolphin3  100.00°C 🥳 1000‰
      $2  #71  ~32 right           used:36 source:dolphin3   38.70°C 🔥  994‰
      $3 #227   ~5 diametrically   used: 1 source:dolphin3   37.81°C 🔥  992‰
      $4 #203  ~14 different       used: 1 source:dolphin3   35.83°C 🥵  983‰
      $5 #223   ~8 opposing        used: 1 source:dolphin3   35.05°C 🥵  981‰
      $6 #208  ~12 dissimilar      used: 1 source:dolphin3   34.95°C 🥵  979‰
      $7 #206  ~13 contrasting     used: 1 source:dolphin3   34.89°C 🥵  978‰
      $8 #193  ~17 divergent       used: 1 source:dolphin3   32.78°C 🥵  972‰
      $9 #228   ~4 antipodal       used: 0 source:dolphin3   32.65°C 🥵  971‰
     $10 #221  ~10 antithetical    used: 0 source:dolphin3   32.42°C 🥵  969‰
     $11 #229   ~3 contrary        used: 0 source:dolphin3   32.01°C 🥵  967‰
     $14 #108  ~28 true            used:26 source:dolphin3   27.82°C 😎  897‰
     $35  #50      correct         used: 4 source:dolphin3   20.88°C 🥶
    $224   #2      cat             used: 0 source:dolphin3   -1.07°C 🧊

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1430 🥳 151 ⏱️ 1:06:16.148392

🤔 152 attempts
📜 7 sessions
🫧 8 chat sessions
⁉️ 41 chat prompts
🤖 41 dolphin3:latest replies
🥵  4 😎 18 🥶 99 🧊 30

      $1 #152     pétrolier  100.00°C 🥳 1000‰  ~1  used:0  [233] source:dolphin3
      $2  #53     cargaison   41.67°C 🥵  971‰ ~13 used:17    [6] source:dolphin3
      $3  #49        navire   40.19°C 🥵  964‰ ~15 used:12    [4] source:dolphin3
      $4  #76      maritime   38.28°C 🥵  948‰  ~9  used:7    [2] source:dolphin3
      $5  #51         cargo   35.37°C 🥵  931‰ ~14  used:5    [0] source:dolphin3
      $6  #47        flotte   32.66°C 😎  897‰ ~17  used:1    [8] source:dolphin3
      $7 #122    remorqueur   31.30°C 😎  869‰  ~5  used:4   [40] source:dolphin3
      $8  #36      naufrage   30.45°C 😎  850‰ ~20  used:2   [30] source:dolphin3
      $9  #54          fret   28.09°C 😎  771‰ ~12  used:1   [10] source:dolphin3
     $10  #48     flottille   25.41°C 😎  629‰ ~16  used:1   [12] source:dolphin3
     $11  #85   marchandise   25.06°C 😎  602‰  ~8  used:1   [14] source:dolphin3
     $12  #38      littoral   25.05°C 😎  600‰ ~19  used:2   [32] source:dolphin3
     $24  #26        guerre   19.63°C 🥶            used:0   [44] source:dolphin3
    $123  #86        métier   -0.15°C 🧊            used:0  [234] source:dolphin3

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #81 🥳 score:22 ⏱️ 0:01:11.360320

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. RATTY attempts:4 score:4
2. BADGE attempts:6 score:6
3. AWFUL attempts:7 score:7
4. FLUNG attempts:5 score:5

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1467 🥳 score:9 ⏱️ 0:02:55.481618

📜 1 sessions

Octordle Rescue

1. FLINT attempts:9 score:9
2. DATUM attempts:5 score:5
3. NOOSE attempts:10 score:10
4. FLUID attempts:6 score:6
5. FILTH attempts:7 score:7
6. MYRRH attempts:8 score:8
7. SCOLD attempts:11 score:11
8. WINCE attempts:12 score:12
