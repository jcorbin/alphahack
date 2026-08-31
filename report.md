# 2026-09-01

- 🔗 wordgrid 🧩 #822 🟪 rarity:0.15 ⏱️ 0:04:11.067062
- 🔗 spaceword.org 🧩 2026-08-31 🏁 score 2164 ranked 53.2% 197/370 ⏱️ 0:34:42.523238
- 🔗 alfagok.diginaut.net 🧩 #668 🥳 26 ⏱️ 0:03:48.188936
- 🔗 alphaguess.com 🧩 #1135 🥳 30 ⏱️ 0:00:38.988984
- 🔗 dontwordle.com 🧩 #1561 🥳 6 ⏱️ 0:01:27.814216
- 🔗 dictionary.com hurdle 🧩 #1704 🥳 18 ⏱️ 0:04:43.839728
- 🔗 Quordle Classic 🧩 #1681 🥳 score:25 ⏱️ 0:02:19.791808
- 🔗 Octordle Classic 🧩 #1681 🥳 score:60 ⏱️ 0:01:28.000547
- 🔗 Sedecordle Classic 🧩 #1661 🥳 score:51 ⏱️ 0:02:25.592124
- 🔗 squareword.org 🧩 #1674 🥳 8 ⏱️ 0:01:51.859914
- 🔗 cemantle.certitudes.org 🧩 #1611 🥳 274 ⏱️ 0:05:52.973470
- 🔗 cemantix.certitudes.org 🧩 #1644 🥳 25 ⏱️ 0:00:16.423178

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




























# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #822 🟪 rarity:0.15 ⏱️ 0:04:11.067062

📜 2 sessions
🦄 🦄 🌌
🦄 🌌 🌌
🌌 🦄 🌌
Rarity: 0.15 🟪

# [spaceword.org](spaceword.org) 🧩 2026-08-31 🏁 score 2164 ranked 53.2% 197/370 ⏱️ 0:34:42.523238

📜 4 sessions
- tiles: 21/21
- score: 2164 bonus: +64
- rank: 197/370

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ M U S K _ _ _   
      _ _ _ _ _ _ A _ _ _   
      _ _ _ _ _ A L _ _ _   
      _ _ _ _ Z E P _ _ _   
      _ _ _ _ _ N A _ _ _   
      _ _ _ _ _ E S _ _ _   
      _ _ _ E G O _ _ _ _   
      _ _ _ _ _ U _ _ _ _   
      _ _ _ V I S _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #668 🥳 26 ⏱️ 0:03:48.188936

🤔 26 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+24880  [ 24880] bad        q8  ? ␅
    @+24880  [ 24880] bad        q9  ? after
    @+37341  [ 37341] beschermen q10 ? ␅
    @+37341  [ 37341] beschermen q11 ? after
    @+37684  [ 37684] beslis     q20 ? ␅
    @+37684  [ 37684] beslis     q21 ? after
    @+37714  [ 37714] beslissing q24 ? ␅
    @+37714  [ 37714] beslissing q25 ? it
    @+37714  [ 37714] beslissing done. it
    @+37844  [ 37844] besmet     q22 ? ␅
    @+37844  [ 37844] besmet     q23 ? before
    @+38031  [ 38031] bespikkel  q18 ? ␅
    @+38031  [ 38031] bespikkel  q19 ? before
    @+38729  [ 38729] besturing  q16 ? ␅
    @+38729  [ 38729] besturing  q17 ? before
    @+40181  [ 40181] beurst     q14 ? ␅
    @+40181  [ 40181] beurst     q15 ? before
    @+43030  [ 43030] bij        q12 ? ␅
    @+43030  [ 43030] bij        q13 ? before
    @+49808  [ 49808] boks       q6  ? ␅
    @+49808  [ 49808] boks       q7  ? before
    @+99688  [ 99688] ex         q4  ? ␅
    @+99688  [ 99688] ex         q5  ? before
    @+199647 [199647] lijk       q0  ? ␅
    @+199647 [199647] lijk       q1  ? after
    @+199647 [199647] lijk       q2  ? ␅
    @+199647 [199647] lijk       q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1135 🥳 30 ⏱️ 0:00:38.988984

🤔 30 attempts
📜 1 sessions

    @        [     0] aa       
    @+98147  [ 98147] mac      q0  ? ␅
    @+98147  [ 98147] mac      q1  ? after
    @+147311 [147311] rho      q2  ? ␅
    @+147311 [147311] rho      q3  ? after
    @+159593 [159593] slug     q6  ? ␅
    @+159593 [159593] slug     q7  ? after
    @+165747 [165747] stint    q8  ? ␅
    @+165747 [165747] stint    q9  ? after
    @+166103 [166103] stop     q16 ? ␅
    @+166103 [166103] stop     q17 ? after
    @+166148 [166148] storax   q22 ? ␅
    @+166148 [166148] storax   q23 ? after
    @+166150 [166150] store    q24 ? ␅
    @+166150 [166150] store    q25 ? after
    @+166168 [166168] storey   q26 ? ␅
    @+166168 [166168] storey   q27 ? after
    @+166178 [166178] storm    q28 ? ␅
    @+166178 [166178] storm    q29 ? it
    @+166178 [166178] storm    done. it
    @+166192 [166192] story    q20 ? ␅
    @+166192 [166192] story    q21 ? before
    @+166301 [166301] straight q18 ? ␅
    @+166301 [166301] straight q19 ? before
    @+166506 [166506] streak   q14 ? ␅
    @+166506 [166506] streak   q15 ? before
    @+167271 [167271] sub      q12 ? ␅
    @+167271 [167271] sub      q13 ? before
    @+168797 [168797] sulfur   q10 ? ␅
    @+168797 [168797] sulfur   q11 ? before
    @+171911 [171911] tag      q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1561 🥳 6 ⏱️ 0:01:27.814216

📜 1 sessions
💰 score: 56

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:YUKKY n n n n n remain:7806
    ⬜⬜⬜⬜⬜ tried:BABOO n n n n n remain:1994
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:948
    ⬜🟩⬜⬜⬜ tried:CIVIC n Y n n n remain:217
    ⬜🟩⬜⬜⬜ tried:DIFFS n Y n n n remain:32
    ⬜🟩⬜⬜🟨 tried:GIMME n Y n n m remain:7

    Undos used: 4

      7 words remaining
    x 8 unused letters
    = 56 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1704 🥳 18 ⏱️ 0:04:43.839728

📜 1 sessions
💰 score: 9800

    5/6
    STELA ⬜🟨⬜⬜🟩
    YURTA ⬜⬜⬜🟨🟩
    TONGA 🟩⬜⬜⬜🟩
    TIKKA 🟩🟩⬜⬜🟩
    TIBIA 🟩🟩🟩🟩🟩
    3/6
    TIBIA 🟩⬜⬜⬜🟨
    TARES 🟩🟨⬜🟨⬜
    TEACH 🟩🟩🟩🟩🟩
    4/6
    TEACH 🟨⬜🟨🟩🟩
    AITCH 🟨⬜🟩🟩🟩
    GOLEM ⬜⬜🟨⬜⬜
    LATCH 🟩🟩🟩🟩🟩
    4/6
    LATCH 🟨⬜🟨🟨⬜
    CLITS 🟩🟩⬜🟨⬜
    CLEFT 🟩🟩⬜⬜🟩
    CLOUT 🟩🟩🟩🟩🟩
    Final 2/2
    NUDGE ⬜⬜⬜🟨🟨
    GREET 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1681 🥳 score:25 ⏱️ 0:02:19.791808

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. NASAL attempts:7 score:7
2. ROUTE attempts:3 score:3
3. ANKLE attempts:6 score:6
4. MIGHT attempts:9 score:9

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1681 🥳 score:60 ⏱️ 0:01:28.000547

📜 1 sessions

Octordle Classic

1. CHEER attempts:8 score:8
2. MINUS attempts:7 score:7
3. NYLON attempts:4 score:4
4. SMELT attempts:6 score:6
5. SWORE attempts:9 score:9
6. WHINE attempts:10 score:10
7. SKIMP attempts:5 score:5
8. SWELL attempts:11 score:11

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1661 🥳 score:51 ⏱️ 0:02:25.592124

📜 1 sessions

Sedecordle Classic sedecordle.com

1. ROACH attempts:7 score:0
2. RECAP attempts:8 score:7
3. PARRY attempts:9 score:0
4. ERUPT attempts:5 score:9
5. BOWEL attempts:3 score:0
6. SCRUM attempts:10 score:3
7. PEARL attempts:6 score:0
8. SPIEL attempts:11 score:6
9. BEZEL attempts:18 score:1
10. OFTEN attempts:12 score:8
11. RUSTY attempts:4 score:0
12. CLOAK attempts:13 score:4
13. SIGMA attempts:14 score:1
14. CHOCK attempts:15 score:4
15. VOWEL attempts:17 score:1
16. HAVEN attempts:16 score:7

# [squareword.org](squareword.org) 🧩 #1674 🥳 8 ⏱️ 0:01:51.859914

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S W A T S
    L O G I C
    O M E G A
    P A N E L
    E N T R Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1611 🥳 274 ⏱️ 0:05:52.973470

🤔 275 attempts
📜 1 sessions
🫧 17 chat sessions
⁉️ 94 chat prompts
🤖 94 dolphin3:latest replies
🔥   3 🥵   8 😎  36 🥶 206 🧊  21

      $1 #275 recipient       100.00°C 🥳 1000‰ ~254 used:0  [253]  source:dolphin3
      $2 #271 beneficiary      49.11°C 🔥  998‰   ~2 used:4  [1]    source:dolphin3
      $3 #256 benefactor       48.95°C 🔥  997‰   ~3 used:6  [2]    source:dolphin3
      $4 #261 donor            43.40°C 🔥  993‰   ~1 used:2  [0]    source:dolphin3
      $5 #273 grantee          41.17°C 🥵  989‰   ~4 used:0  [3]    source:dolphin3
      $6 #264 patron           38.34°C 🥵  981‰   ~5 used:0  [4]    source:dolphin3
      $7 #233 originator       33.42°C 🥵  966‰  ~24 used:14 [23]   source:dolphin3
      $8 #265 philanthropist   32.42°C 🥵  960‰   ~6 used:0  [5]    source:dolphin3
      $9 #260 contributor      32.13°C 🥵  957‰   ~7 used:0  [6]    source:dolphin3
     $10 #272 generosity       29.76°C 🥵  930‰   ~8 used:0  [7]    source:dolphin3
     $11 #268 supporter        28.28°C 🥵  905‰   ~9 used:0  [8]    source:dolphin3
     $13 #259 charitable       27.69°C 😎  898‰  ~11 used:0  [10]   source:dolphin3
     $49  #38 repeater         17.91°C 🥶        ~48 used:12 [47]   source:dolphin3
    $255 #102 upstream         -0.25°C 🧊       ~255 used:0  [254]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1644 🥳 25 ⏱️ 0:00:16.423178

🤔 26 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 4 chat prompts
🤖 4 dolphin3:latest replies
😱 1 🥵 1 😎 6 🥶 9 🧊 8

     $1 #26 bassin      100.00°C 🥳 1000‰ ~18 used:0 [17]  source:dolphin3
     $2  #5 eau          49.57°C 😱  999‰  ~1 used:5 [0]   source:dolphin3
     $3 #16 rivière      40.42°C 🥵  977‰  ~2 used:1 [1]   source:dolphin3
     $4 #18 fleuve       34.03°C 😎  860‰  ~3 used:0 [2]   source:dolphin3
     $5 #21 réservoir    33.33°C 😎  830‰  ~4 used:0 [3]   source:dolphin3
     $6 #25 barrage      29.35°C 😎  663‰  ~5 used:0 [4]   source:dolphin3
     $7 #24 aqueduc      29.14°C 😎  647‰  ~6 used:0 [5]   source:dolphin3
     $8 #23 écoulement   29.05°C 😎  642‰  ~7 used:0 [6]   source:dolphin3
     $9 #19 hydro        24.13°C 😎  134‰  ~8 used:0 [7]   source:dolphin3
    $10 #13 water        22.65°C 🥶        ~9 used:0 [8]   source:dolphin3
    $11 #14 lac          22.57°C 🥶       ~10 used:0 [9]   source:dolphin3
    $12 #15 mer          22.34°C 🥶       ~11 used:0 [10]  source:dolphin3
    $13 #17 arrosage     21.59°C 🥶       ~12 used:0 [11]  source:dolphin3
    $19  #9 pomme        -1.03°C 🧊       ~19 used:0 [18]  source:dolphin3
