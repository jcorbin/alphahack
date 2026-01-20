# 2026-01-21

- 🔗 spaceword.org 🧩 2026-01-20 🏁 score 2168 ranked 44.1% 141/320 ⏱️ 0:17:49.523483
- 🔗 alfagok.diginaut.net 🧩 #445 🥳 21 ⏱️ 0:01:06.815627
- 🔗 alphaguess.com 🧩 #912 🥳 14 ⏱️ 0:01:05.312472
- 🔗 dontwordle.com 🧩 #1338 🥳 6 ⏱️ 0:02:03.184645
- 🔗 dictionary.com hurdle 🧩 #1481 🥳 18 ⏱️ 0:04:53.503693
- 🔗 Quordle Classic 🧩 #1458 🥳 score:23 ⏱️ 0:01:30.352418
- 🔗 Octordle Classic 🧩 #1458 🥳 score:67 ⏱️ 0:03:32.536541
- 🔗 squareword.org 🧩 #1451 🥳 7 ⏱️ 0:02:07.511793
- 🔗 cemantle.certitudes.org 🧩 #1388 🥳 195 ⏱️ 0:23:39.483962
- 🔗 cemantix.certitudes.org 🧩 #1421 🥳 375 ⏱️ 0:12:56.629565
- 🔗 Quordle Rescue 🧩 #72 🥳 score:22 ⏱️ 0:01:35.784242
- 🔗 Octordle Rescue 🧩 #1458 🥳 score:8 ⏱️ 0:05:52.962534

# Dev

## WIP

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






# [spaceword.org](spaceword.org) 🧩 2026-01-20 🏁 score 2168 ranked 44.1% 141/320 ⏱️ 0:17:49.523483

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 141/320

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ A _ T _ _   
      _ M _ P U N J I S _   
      _ O X O _ O _ E _ _   
      _ I _ W I N E R Y _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #445 🥳 21 ⏱️ 0:01:06.815627

🤔 21 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+1      [     1] &-tekens     
    @+2      [     2] -cijferig    
    @+3      [     3] -e-mail      
    @+199833 [199833] lijm         q0  ? after
    @+299738 [299738] schub        q1  ? after
    @+349515 [349515] vakantie     q2  ? after
    @+374256 [374256] vrij         q3  ? after
    @+386797 [386797] wind         q4  ? after
    @+393214 [393214] zelfmoord    q5  ? after
    @+394809 [394809] zigzag       q7  ? after
    @+395586 [395586] zo           q8  ? after
    @+395777 [395777] zoem         q10 ? after
    @+395878 [395878] zoets        q11 ? after
    @+395908 [395908] zoetwatervis q14 ? after
    @+395920 [395920] zog          q15 ? after
    @+395922 [395922] zogen        q16 ? after
    @+395923 [395923] zogenaamd    q20 ? it
    @+395923 [395923] zogenaamd    done. it
    @+395924 [395924] zogenaamde   q19 ? before
    @+395926 [395926] zogenoemd    q18 ? before
    @+395929 [395929] zogwater     q17 ? before
    @+395935 [395935] zolder       q13 ? before
    @+395988 [395988] zomer        q9  ? before
    @+396422 [396422] zone         q6  ? before

# [alphaguess.com](alphaguess.com) 🧩 #912 🥳 14 ⏱️ 0:01:05.312472

🤔 14 attempts
📜 1 sessions

    @       [    0] aa     
    @+1     [    1] aah    
    @+2     [    2] aahed  
    @+3     [    3] aahing 
    @+47382 [47382] dis    q1  ? after
    @+49429 [49429] do     q5  ? after
    @+50406 [50406] dove   q7  ? after
    @+50900 [50900] drawl  q8  ? after
    @+51132 [51132] drive  q9  ? after
    @+51180 [51180] droll  q11 ? after
    @+51202 [51202] drongo q12 ? after
    @+51208 [51208] drool  q13 ? it
    @+51208 [51208] drool  done. it
    @+51226 [51226] drop   q10 ? before
    @+51403 [51403] drunk  q6  ? before
    @+53398 [53398] el     q4  ? before
    @+60085 [60085] face   q3  ? before
    @+72801 [72801] gremmy q2  ? before
    @+98220 [98220] mach   q0  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1338 🥳 6 ⏱️ 0:02:03.184645

📜 1 sessions
💰 score: 16

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MUMUS n n n n n remain:4833
    ⬜⬜⬜⬜⬜ tried:WHOOP n n n n n remain:2013
    ⬜⬜⬜⬜⬜ tried:JINNI n n n n n remain:833
    ⬜⬜🟨⬜⬜ tried:XYLYL n n m n n remain:115
    ⬜🟩🟨⬜⬜ tried:BLAFF n Y m n n remain:10
    ⬜🟩⬜🟩🟨 tried:ALGAE n Y n Y m remain:2

    Undos used: 3

      2 words remaining
    x 8 unused letters
    = 16 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1481 🥳 18 ⏱️ 0:04:53.503693

📜 2 sessions
💰 score: 9800

    3/6
    SERAC ⬜🟨🟩⬜⬜
    FORTE ⬜⬜🟩🟨🟩
    THREE 🟩🟩🟩🟩🟩
    5/6
    THREE ⬜⬜⬜⬜⬜
    AMINO 🟩⬜⬜⬜⬜
    AGLUS 🟩⬜🟨⬜⬜
    ALWAY 🟩🟨⬜⬜🟩
    APPLY 🟩🟩🟩🟩🟩
    4/6
    APPLY ⬜🟩⬜⬜⬜
    SPIRE 🟩🟩⬜⬜🟨
    SPEND 🟩🟩🟩🟩⬜
    SPENT 🟩🟩🟩🟩🟩
    5/6
    SPENT ⬜⬜⬜⬜⬜
    RADIO 🟨⬜⬜🟨⬜
    MIRKY ⬜🟨🟨⬜⬜
    CHIRU ⬜🟩🟩🟩⬜
    WHIRL 🟩🟩🟩🟩🟩
    Final 1/2
    HARPY 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1458 🥳 score:23 ⏱️ 0:01:30.352418

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. PRIVY attempts:4 score:4
2. SHADY attempts:8 score:8
3. REMIT attempts:6 score:6
4. AORTA attempts:5 score:5

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1458 🥳 score:67 ⏱️ 0:03:32.536541

📜 1 sessions

Octordle Classic

1. PRUDE attempts:4 score:4
2. SLUSH attempts:13 score:13
3. EYING attempts:11 score:11
4. BANAL attempts:7 score:7
5. TONGA attempts:8 score:8
6. PLUNK attempts:5 score:5
7. JOINT attempts:9 score:9
8. LARVA attempts:10 score:10

# [squareword.org](squareword.org) 🧩 #1451 🥳 7 ⏱️ 0:02:07.511793

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P L E B S
    L I L A C
    O M E G A
    T I G E R
    S T Y L E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1388 🥳 195 ⏱️ 0:23:39.483962

🤔 196 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 37 chat prompts
🤖 37 ministral-3:14b replies
🔥   2 🥵  12 😎  36 🥶 141 🧊   4

      $1 #196   ~1 ultimate          100.00°C 🥳 1000‰
      $2 #165  ~18 absolute           44.61°C 🔥  996‰
      $3 #137  ~34 paramount          42.93°C 🔥  991‰
      $4 #164  ~19 unquestionable     41.60°C 🥵  987‰
      $5 #134  ~35 supreme            41.06°C 🥵  985‰
      $6 #157  ~23 unparalleled       40.86°C 🥵  984‰
      $7 #188   ~7 pinnacle           40.85°C 🥵  983‰
      $8 #144  ~30 preeminent         38.27°C 🥵  973‰
      $9 #183   ~9 definitive         36.94°C 🥵  962‰
     $10  #18  ~51 elusive            36.72°C 🥵  960‰
     $11 #124  ~37 divine             35.52°C 🥵  946‰
     $16 #162  ~21 unmatched          33.03°C 😎  899‰
     $52  #77      beyond             23.43°C 🥶
    $193   #7      zinfandel          -0.81°C 🧊

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1421 🥳 375 ⏱️ 0:12:56.629565

🤔 376 attempts
📜 3 sessions
🫧 28 chat sessions
⁉️ 117 chat prompts
🤖 97 dolphin3:latest replies
🤖 20 ministral-3:14b replies
🔥   5 🥵  29 😎  74 🥶 210 🧊  57

      $1 #376   ~1 éventualité        100.00°C 🥳 1000‰
      $2 #221  ~49 probable            55.32°C 🔥  998‰
      $3 #109  ~83 envisager           53.92°C 🔥  997‰
      $4 #116  ~79 envisageable        48.70°C 🔥  996‰
      $5 #155  ~64 hypothèse           47.85°C 🔥  995‰
      $6  #68  ~98 conséquence         47.11°C 🔥  994‰
      $7 #297  ~18 prévisible          45.05°C 🥵  989‰
      $8 #265  ~32 opportun            43.90°C 🥵  988‰
      $9 #206  ~57 hypothétique        43.08°C 🥵  986‰
     $10 #315  ~15 inévitable          42.70°C 🥵  983‰
     $11 #143  ~70 possible            42.48°C 🥵  982‰
     $36 #228  ~48 probablement        34.28°C 😎  898‰
    $110 #365      démontrer           21.85°C 🥶
    $320   #8      trombone            -0.43°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #72 🥳 score:22 ⏱️ 0:01:35.784242

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. FLEET attempts:6 score:6
2. SLICE attempts:5 score:5
3. BERRY attempts:8 score:8
4. GRAPE attempts:3 score:3

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1458 🥳 score:8 ⏱️ 0:05:52.962534

📜 1 sessions

Octordle Rescue

1. BERTH attempts:5 score:5
2. SANDY attempts:12 score:12
3. GRAPE attempts:6 score:6
4. MOWER attempts:10 score:10
5. LOUSE attempts:11 score:11
6. HORSE attempts:8 score:8
7. LEDGE attempts:7 score:7
8. FRITZ attempts:13 score:13
