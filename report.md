# 2026-09-07

- 🔗 spaceword.org 🧩 2026-09-06 🏁 score 2168 ranked 36.6% 115/314 ⏱️ 0:28:28.689081
- 🔗 wordgrid 🧩 #828 🟪 rarity:0.21 ⏱️ 0:04:23.336370
- 🔗 alfagok.diginaut.net 🧩 #674 🥳 32 ⏱️ 0:00:43.487482
- 🔗 alphaguess.com 🧩 #1141 🥳 24 ⏱️ 0:00:36.678445
- 🔗 dontwordle.com 🧩 #1567 🥳 6 ⏱️ 0:02:08.064489
- 🔗 dictionary.com hurdle 🧩 #1710 🥳 21 ⏱️ 0:05:50.290779
- 🔗 Quordle Classic 🧩 #1687 🥳 score:25 ⏱️ 0:02:57.403534
- 🔗 Octordle Classic 🧩 #1687 🥳 score:61 ⏱️ 0:02:13.014211
- 🔗 Sedecordle Classic 🧩 #1667 🥳 score:49 ⏱️ 0:02:12.430696
- 🔗 squareword.org 🧩 #1680 🥳 9 ⏱️ 0:02:34.403183
- 🔗 cemantle.certitudes.org 🧩 #1617 🥳 64 ⏱️ 0:00:42.007113

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


































# [spaceword.org](spaceword.org) 🧩 2026-09-06 🏁 score 2168 ranked 36.6% 115/314 ⏱️ 0:28:28.689081

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 115/314

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ B _ Q _ _ _ _   
      _ _ _ E M U _ _ _ _   
      _ _ _ _ H I T _ _ _   
      _ _ _ _ O N O _ _ _   
      _ _ _ _ _ T O _ _ _   
      _ _ _ _ Z E N _ _ _   
      _ _ _ _ _ _ I _ _ _   
      _ _ _ L E K E _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #828 🟪 rarity:0.21 ⏱️ 0:04:23.336370

📜 2 sessions
🦄 🦄 🌌
🦄 🦄 🦄
🦄 🌌 🌌
Rarity: 0.21 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #674 🥳 32 ⏱️ 0:00:43.487482

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken 
    @+199640 [199640] lijk    q0  ? ␅
    @+199640 [199640] lijk    q1  ? after
    @+199640 [199640] lijk    q2  ? ␅
    @+199640 [199640] lijk    q3  ? after
    @+224537 [224537] moord   q8  ? ␅
    @+224537 [224537] moord   q9  ? after
    @+230458 [230458] neer    q12 ? ␅
    @+230458 [230458] neer    q13 ? after
    @+233683 [233683] nood    q14 ? ␅
    @+233683 [233683] nood    q15 ? after
    @+234507 [234507] notaris q18 ? ␅
    @+234507 [234507] notaris q19 ? after
    @+234707 [234707] ns      q22 ? ␅
    @+234707 [234707] ns      q23 ? after
    @+234805 [234805] nul     q24 ? ␅
    @+234805 [234805] nul     q25 ? after
    @+234860 [234860] numero  q28 ? ␅
    @+234860 [234860] numero  q29 ? after
    @+234874 [234874] nummer  q30 ? ␅
    @+234874 [234874] nummer  q31 ? it
    @+234874 [234874] nummer  done. it
    @+234914 [234914] nun     q20 ? ␅
    @+234914 [234914] nun     q21 ? before
    @+235345 [235345] oceaan  q16 ? ␅
    @+235345 [235345] oceaan  q17 ? before
    @+237026 [237026] om      q10 ? ␅
    @+237026 [237026] om      q11 ? before
    @+249560 [249560] opinie  q6  ? ␅
    @+249560 [249560] opinie  q7  ? before
    @+299543 [299543] schroot q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1141 🥳 24 ⏱️ 0:00:36.678445

🤔 24 attempts
📜 1 sessions

    @        [     0] aa      
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98147  [ 98147] mac     q0  ? ␅
    @+98147  [ 98147] mac     q1  ? after
    @+98147  [ 98147] mac     q2  ? ␅
    @+98147  [ 98147] mac     q3  ? after
    @+98147  [ 98147] mac     q4  ? ␅
    @+98147  [ 98147] mac     q5  ? after
    @+147311 [147311] rho     q6  ? ␅
    @+147311 [147311] rho     q7  ? after
    @+171911 [171911] tag     q8  ? ␅
    @+171911 [171911] tag     q9  ? after
    @+181996 [181996] un      q10 ? ␅
    @+181996 [181996] un      q11 ? after
    @+189258 [189258] vicar   q12 ? ␅
    @+189258 [189258] vicar   q13 ? after
    @+192862 [192862] whir    q14 ? ␅
    @+192862 [192862] whir    q15 ? after
    @+193477 [193477] win     q18 ? ␅
    @+193477 [193477] win     q19 ? after
    @+194057 [194057] wo      q20 ? ␅
    @+194057 [194057] wo      q21 ? after
    @+194258 [194258] wood    q22 ? ␅
    @+194258 [194258] wood    q23 ? it
    @+194258 [194258] wood    done. it
    @+194686 [194686] worship q16 ? ␅
    @+194686 [194686] worship q17 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1567 🥳 6 ⏱️ 0:02:08.064489

📜 1 sessions
💰 score: 5

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:FEEZE n n n n n remain:6482
    ⬜⬜⬜⬜⬜ tried:JINNI n n n n n remain:3273
    ⬜⬜⬜⬜⬜ tried:WUSHU n n n n n remain:685
    ⬜⬜⬜⬜⬜ tried:PYGMY n n n n n remain:186
    ⬜⬜⬜🟩⬜ tried:ADDAX n n n Y n remain:27
    ⬜🟩🟩🟩⬜ tried:BLOAT n Y Y Y n remain:1

    Undos used: 3

      1 words remaining
    x 5 unused letters
    = 5 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1710 🥳 21 ⏱️ 0:05:50.290779

📜 1 sessions
💰 score: 9500

    5/6
    RAPES ⬜🟨⬜⬜⬜
    ALOIN 🟩⬜⬜🟨🟨
    ACING 🟩⬜🟩🟩🟩
    AWASH 🟩⬜⬜⬜⬜
    AGING 🟩🟩🟩🟩🟩
    6/6
    AGING ⬜⬜⬜⬜⬜
    SCORE 🟩⬜🟩⬜⬜
    SLOTH 🟩⬜🟩🟨⬜
    STOUP 🟩🟩🟩⬜⬜
    BIKED ⬜⬜⬜⬜🟩
    STOOD 🟩🟩🟩🟩🟩
    4/6
    STOOD ⬜⬜⬜⬜🟨
    DAIRY 🟨⬜🟨⬜⬜
    INDUE 🟨🟨🟩⬜🟨
    WIDEN 🟩🟩🟩🟩🟩
    4/6
    WIDEN ⬜⬜⬜🟨⬜
    HASTE ⬜⬜⬜⬜🟨
    LEMUR 🟨🟨⬜⬜🟨
    CLERK 🟩🟩🟩🟩🟩
    Final 2/2
    HALVE ⬜🟨🟨⬜⬜
    TOTAL 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1687 🥳 score:25 ⏱️ 0:02:57.403534

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. VISIT attempts:8 score:8
2. CLANK attempts:5 score:5
3. FEVER attempts:9 score:9
4. OCEAN attempts:3 score:3

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1687 🥳 score:61 ⏱️ 0:02:13.014211

📜 1 sessions

Octordle Classic

1. MILKY attempts:8 score:8
2. EMAIL attempts:5 score:5
3. PASTE attempts:13 score:13
4. CAIRN attempts:3 score:3
5. DANCE attempts:4 score:4
6. TUTOR attempts:10 score:10
7. SNOUT attempts:11 score:11
8. LEASH attempts:7 score:7

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1667 🥳 score:49 ⏱️ 0:02:12.430696

📜 1 sessions

Sedecordle Classic sedecordle.com

1. SAUTE attempts:9 score:0
2. DERBY attempts:11 score:9
3. PRONG attempts:7 score:0
4. VOMIT attempts:14 score:7
5. APPLE attempts:15 score:1
6. BELLY attempts:12 score:5
7. WIDER attempts:4 score:0
8. BASIN attempts:10 score:4
9. WREAK attempts:5 score:0
10. SNACK attempts:8 score:5
11. OCTAL attempts:13 score:1
12. COMET attempts:16 score:3
13. RANGE attempts:17 score:1
14. EERIE attempts:18 score:7
15. WAXEN attempts:6 score:0
16. SLICE attempts:19 score:6

# [squareword.org](squareword.org) 🧩 #1680 🥳 9 ⏱️ 0:02:34.403183

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟨
    🟨 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C A R F
    E L D E R
    D I O D E
    A M B I T
    N E E D S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1617 🥳 64 ⏱️ 0:00:42.007113

🤔 65 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 14 chat prompts
🤖 14 dolphin3:latest replies
😱  1 🔥  2 🥵  3 😎 11 🥶 47

     $1 #65 intense        100.00°C 🥳 1000‰ ~65 used:0 [64]  source:dolphin3
     $2 #48 fierce          68.43°C 😱  999‰  ~1 used:8 [0]   source:dolphin3
     $3 #63 unrelenting     56.14°C 🔥  997‰  ~2 used:3 [1]   source:dolphin3
     $4 #49 ferocious       51.53°C 🔥  992‰  ~3 used:3 [2]   source:dolphin3
     $5 #54 brutal          40.49°C 🥵  957‰  ~4 used:0 [3]   source:dolphin3
     $6 #45 furious         37.69°C 🥵  935‰  ~5 used:0 [4]   source:dolphin3
     $7 #50 harsh           35.09°C 🥵  902‰  ~6 used:0 [5]   source:dolphin3
     $8 #51 savage          32.53°C 😎  839‰  ~7 used:0 [6]   source:dolphin3
     $9 #62 merciless       32.41°C 😎  837‰  ~8 used:0 [7]   source:dolphin3
    $10 #57 vicious         31.12°C 😎  789‰  ~9 used:0 [8]   source:dolphin3
    $11 #56 ruthless        30.43°C 😎  765‰ ~10 used:0 [9]   source:dolphin3
    $12 #46 angry           30.38°C 😎  763‰ ~11 used:0 [10]  source:dolphin3
    $13 #52 violent         28.79°C 😎  670‰ ~12 used:0 [11]  source:dolphin3
    $19 #59 bloodthirsty    22.76°C 🥶       ~22 used:0 [21]  source:dolphin3
