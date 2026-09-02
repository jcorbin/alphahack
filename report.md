# 2026-09-03

- 🔗 spaceword.org 🧩 2026-09-02 🏁 score 2165 ranked 43.9% 154/351 ⏱️ 0:41:25.857282
- 🔗 wordgrid 🧩 #824 🟪 rarity:0.12 ⏱️ 0:06:03.578889
- 🔗 alfagok.diginaut.net 🧩 #670 🥳 54 ⏱️ 0:01:43.777017
- 🔗 alphaguess.com 🧩 #1137 🥳 40 ⏱️ 0:00:55.358801
- 🔗 dontwordle.com 🧩 #1563 🥳 6 ⏱️ 0:01:33.809454
- 🔗 dictionary.com hurdle 🧩 #1706 🥳 16 ⏱️ 0:02:36.869690
- 🔗 Quordle Classic 🧩 #1683 🥳 score:20 ⏱️ 0:01:16.661081
- 🔗 Octordle Classic 🧩 #1683 😦 score:75 ⏱️ 0:03:00.244729
- 🔗 Sedecordle Classic 🧩 #1663 🥳 score:41 ⏱️ 0:03:07.203638
- 🔗 squareword.org 🧩 #1676 🥳 7 ⏱️ 0:02:12.684854
- 🔗 cemantle.certitudes.org 🧩 #1613 🥳 582 ⏱️ 0:22:21.648613
- 🔗 cemantix.certitudes.org 🧩 #1646 🥳 444 ⏱️ 0:19:13.455277

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






























# [spaceword.org](spaceword.org) 🧩 2026-09-02 🏁 score 2165 ranked 43.9% 154/351 ⏱️ 0:41:25.857282

📜 3 sessions
- tiles: 21/21
- score: 2165 bonus: +65
- rank: 154/351

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ Q _ _ _ _ _ E _   
      _ _ U P _ J E R K _   
      _ _ I L I A _ A E _   
      _ _ T O _ B O D _ _   
      _ _ _ D _ _ P _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #824 🟪 rarity:0.12 ⏱️ 0:06:03.578889

📜 4 sessions
🦄 🦄 🦄
🦄 🌌 🌌
🦄 🦄 🦄
Rarity: 0.12 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #670 🥳 54 ⏱️ 0:01:43.777017

🤔 54 attempts
📜 1 sessions

    @       [    0] &-teken      
    @+49808 [49808] boks         q8  ? ␅
    @+49808 [49808] boks         q9  ? after
    @+62247 [62247] cement       q12 ? ␅
    @+62247 [62247] cement       q13 ? after
    @+68479 [68479] connaisseurs q14 ? ␅
    @+68479 [68479] connaisseurs q15 ? after
    @+71552 [71552] cru          q16 ? ␅
    @+71552 [71552] cru          q17 ? after
    @+71659 [71659] cue          q28 ? ␅
    @+71659 [71659] cue          q29 ? after
    @+71699 [71699] cult         q30 ? ␅
    @+71699 [71699] cult         q31 ? after
    @+71731 [71731] cultivéparel q32 ? ␅
    @+71731 [71731] cultivéparel q33 ? after
    @+71740 [71740] culture      q34 ? ␅
    @+71740 [71740] culture      q35 ? after
    @+71741 [71741] cultureel    q52 ? ␅
    @+71741 [71741] cultureel    q53 ? it
    @+71741 [71741] cultureel    done. it
    @+71743 [71743] cultureels   q42 ? ␅
    @+71743 [71743] cultureels   q43 ? before
    @+71743 [71743] cultureels   q50 ? ␅
    @+71743 [71743] cultureels   q51 ? .
    @+71746 [71746] culturen     q36 ? ␅
    @+71746 [71746] culturen     q37 ? before
    @+71757 [71757] cultuur      q22 ? ␅
    @+71757 [71757] cultuur      q23 ? before
    @+72188 [72188] curie        q20 ? ␅
    @+72188 [72188] curie        q21 ? before
    @+72835 [72835] dag          q19 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1137 🥳 40 ⏱️ 0:00:55.358801

🤔 40 attempts
📜 1 sessions

    @       [    0] aa      
    @+11763 [11763] back    q8  ? ␅
    @+11763 [11763] back    q9  ? after
    @+17714 [17714] blind   q10 ? ␅
    @+17714 [17714] blind   q11 ? after
    @+18426 [18426] bobs    q16 ? ␅
    @+18426 [18426] bobs    q17 ? after
    @+18790 [18790] bombe   q18 ? ␅
    @+18790 [18790] bombe   q19 ? after
    @+18969 [18969] boob    q20 ? ␅
    @+18969 [18969] boob    q21 ? after
    @+19025 [19025] book    q22 ? ␅
    @+19025 [19025] book    q23 ? after
    @+19086 [19086] books   q24 ? ␅
    @+19086 [19086] books   q25 ? after
    @+19105 [19105] boom    q26 ? ␅
    @+19105 [19105] boom    q27 ? after
    @+19129 [19129] boon    q28 ? ␅
    @+19129 [19129] boon    q29 ? after
    @+19143 [19143] boor    q30 ? ␅
    @+19143 [19143] boor    q31 ? after
    @+19149 [19149] boos    q32 ? ␅
    @+19149 [19149] boos    q33 ? after
    @+19150 [19150] boost   q38 ? ␅
    @+19150 [19150] boost   q39 ? it
    @+19150 [19150] boost   done. it
    @+19151 [19151] boosted q36 ? ␅
    @+19151 [19151] boosted q37 ? before
    @+19152 [19152] booster q34 ? ␅
    @+19152 [19152] booster q35 ? before
    @+19159 [19159] boot    q15 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1563 🥳 6 ⏱️ 0:01:33.809454

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:EGGER n n n n n remain:4505
    ⬜⬜⬜⬜⬜ tried:ONION n n n n n remain:1223
    ⬜⬜⬜⬜⬜ tried:KUDZU n n n n n remain:494
    ⬜⬜⬜⬜🟨 tried:PHPHT n n n n m remain:77
    ⬜🟩🟨⬜⬜ tried:FATWA n Y m n n remain:20
    ⬜🟩🟨🟩⬜ tried:VASTS n Y m Y n remain:1

    Undos used: 3

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1706 🥳 16 ⏱️ 0:02:36.869690

📜 1 sessions
💰 score: 10000

    4/6
    DARES 🟩⬜⬜🟨⬜
    DOGIE 🟩⬜⬜🟩🟨
    DEMIT 🟩🟩🟨🟩⬜
    DENIM 🟩🟩🟩🟩🟩
    4/6
    DENIM ⬜🟨⬜⬜⬜
    AURES 🟨⬜🟨🟨⬜
    GRACE ⬜🟨🟨🟨🟨
    CLEAR 🟩🟩🟩🟩🟩
    4/6
    CLEAR ⬜🟨⬜⬜🟨
    ROILY 🟨🟨⬜🟨⬜
    PROWL ⬜🟩🟩🟩🟩
    GROWL 🟩🟩🟩🟩🟩
    3/6
    GROWL 🟨⬜⬜⬜🟩
    ANGEL 🟨⬜🟩🟨🟩
    LEGAL 🟩🟩🟩🟩🟩
    Final 1/2
    CORNY 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1683 🥳 score:20 ⏱️ 0:01:16.661081

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SIGMA attempts:3 score:3
2. ESSAY attempts:6 score:6
3. MERRY attempts:7 score:7
4. LLAMA attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1683 😦 score:75 ⏱️ 0:03:00.244729

📜 2 sessions

Octordle Classic

1. SPACE attempts:4 score:4
2. FRUIT attempts:7 score:7
3. SCALP attempts:5 score:5
4. AMISS attempts:11 score:11
5. TIGER attempts:12 score:12
6. SIEVE attempts:13 score:13
7. WRECK attempts:9 score:9
8. _AR_Y ~M -BCDEFGHIKLNOPSTUVW attempts:13 score:-1

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1663 🥳 score:41 ⏱️ 0:03:07.203638

📜 1 sessions

Sedecordle Classic sedecordle.com

1. TWINE attempts:6 score:0
2. MASSE attempts:3 score:6
3. CHOSE attempts:7 score:0
4. MODEL attempts:8 score:7
5. ADMIT attempts:9 score:0
6. METRO attempts:4 score:9
7. CANDY attempts:10 score:1
8. HAIRY attempts:17 score:0
9. WHINY attempts:11 score:1
10. PIGGY attempts:12 score:1
11. SLATE attempts:13 score:1
12. PETTY attempts:17 score:3
13. DRUNK attempts:14 score:1
14. FLECK attempts:15 score:4
15. COULD attempts:16 score:1
16. HUMOR attempts:17 score:6

# [squareword.org](squareword.org) 🧩 #1676 🥳 7 ⏱️ 0:02:12.684854

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    L A P S E
    E R R E D
    A M O N G
    P O S S E
    T R E E S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1613 🥳 582 ⏱️ 0:22:21.648613

🤔 583 attempts
📜 1 sessions
🫧 32 chat sessions
⁉️ 184 chat prompts
🤖 184 dolphin3:latest replies
😱   1 🔥   4 🥵  30 😎  73 🥶 450 🧊  24

      $1 #583 neighbor        100.00°C 🥳 1000‰ ~559 used:0   [558]  source:dolphin3
      $2 #548 friend           55.94°C 😱  999‰   ~1 used:9   [0]    source:dolphin3
      $3 #545 cousin           55.79°C 🔥  998‰   ~2 used:4   [1]    source:dolphin3
      $4 #544 aunt             54.86°C 🔥  997‰   ~3 used:4   [2]    source:dolphin3
      $5 #152 backyard         51.79°C 🔥  995‰  ~99 used:159 [98]   source:dolphin3
      $6 #419 roommate         50.64°C 🔥  993‰  ~16 used:100 [15]   source:dolphin3
      $7 #397 landlord         49.13°C 🥵  989‰ ~103 used:30  [102]  source:dolphin3
      $8 #555 stepfather       48.97°C 🥵  987‰   ~4 used:0   [3]    source:dolphin3
      $9 #557 uncle            48.75°C 🥵  985‰   ~5 used:0   [4]    source:dolphin3
     $10 #399 homeowner        48.37°C 🥵  984‰  ~96 used:12  [95]   source:dolphin3
     $11 #575 acquaintance     48.34°C 🥵  983‰   ~6 used:0   [5]    source:dolphin3
     $37  #75 kitten           36.24°C 😎  893‰ ~107 used:6   [106]  source:dolphin3
    $110 #388 living           23.95°C 🥶       ~118 used:0   [117]  source:dolphin3
    $560 #527 information      -0.03°C 🧊       ~560 used:0   [559]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1646 🥳 444 ⏱️ 0:19:13.455277

🤔 445 attempts
📜 1 sessions
🫧 40 chat sessions
⁉️ 216 chat prompts
🤖 216 dolphin3:latest replies
🔥   3 🥵  36 😎  99 🥶 258 🧊  48

      $1 #445 plaider            100.00°C 🥳 1000‰ ~397 used:0   [396]  source:dolphin3
      $2 #121 défendre            54.62°C 🔥  998‰ ~134 used:181 [133]  source:dolphin3
      $3 #416 affirmer            54.25°C 🔥  997‰   ~4 used:25  [3]    source:dolphin3
      $4 #442 réclamer            51.62°C 🔥  995‰   ~1 used:3   [0]    source:dolphin3
      $5 #130 opposer             44.88°C 🔥  990‰ ~132 used:102 [131]  source:dolphin3
      $6  #73 défenseur           44.69°C 🥵  989‰ ~138 used:47  [137]  source:dolphin3
      $7 #425 réaffirmer          43.81°C 🥵  988‰   ~5 used:3   [4]    source:dolphin3
      $8 #417 arguer              42.78°C 🥵  984‰   ~6 used:3   [5]    source:dolphin3
      $9 #176 contester           42.27°C 🥵  982‰  ~20 used:8   [19]   source:dolphin3
     $10  #40 gouvernement        42.04°C 🥵  980‰ ~133 used:12  [132]  source:dolphin3
     $11 #154 dénoncer            41.30°C 🥵  978‰  ~21 used:8   [20]   source:dolphin3
     $41  #98 plaidoirie          33.75°C 😎  896‰  ~36 used:0   [35]   source:dolphin3
    $140 #159 incriminer          23.57°C 🥶       ~141 used:0   [140]  source:dolphin3
    $398 #271 mémoire             -0.05°C 🧊       ~398 used:0   [397]  source:dolphin3
