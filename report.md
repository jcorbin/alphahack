# 2026-08-25

- 🔗 spaceword.org 🧩 2026-08-24 🏁 score 2173 ranked 8.2% 28/340 ⏱️ 3:21:54.664907
- 🔗 wordgrid 🧩 #815 🟪 rarity:0.2 ⏱️ 0:01:54.764076
- 🔗 alfagok.diginaut.net 🧩 #661 🥳 28 ⏱️ 0:00:34.084488
- 🔗 alphaguess.com 🧩 #1128 🥳 32 ⏱️ 0:00:36.909334
- 🔗 dontwordle.com 🧩 #1554 🥳 6 ⏱️ 0:00:51.021654
- 🔗 dictionary.com hurdle 🧩 #1697 🥳 16 ⏱️ 0:02:41.211505
- 🔗 Quordle Classic 🧩 #1674 🥳 score:21 ⏱️ 0:01:23.863608
- 🔗 Octordle Classic 🧩 #1674 🥳 score:57 ⏱️ 0:01:36.293623
- 🔗 Sedecordle Classic 🧩 #1654 🥳 score:43 ⏱️ 0:02:52.707211
- 🔗 squareword.org 🧩 #1667 🥳 8 ⏱️ 0:03:19.308852
- 🔗 cemantle.certitudes.org 🧩 #1604 🥳 158 ⏱️ 0:02:20.274004
- 🔗 cemantix.certitudes.org 🧩 #1637 🥳 310 ⏱️ 0:05:36.342444

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





















# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #815 🟪 rarity:0.2 ⏱️ 0:01:54.764076

📜 2 sessions
🌌 🌌 🌌
🌌 🦄 🌌
🦄 🌌 🌌
Rarity: 0.2 🟪

# [spaceword.org](spaceword.org) 🧩 2026-08-24 🏁 score 2173 ranked 8.2% 28/340 ⏱️ 3:21:54.664907

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 28/340

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ S A Y _ _ _   
      _ _ _ _ I T _ _ _ _   
      _ _ _ _ _ W _ _ _ _   
      _ _ _ _ S A E _ _ _   
      _ _ _ _ T I X _ _ _   
      _ _ _ _ O N E _ _ _   
      _ _ _ _ G _ Q _ _ _   
      _ _ _ _ I _ U _ _ _   
      _ _ _ _ E _ Y _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #661 🥳 28 ⏱️ 0:00:34.084488

🤔 28 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+2      [     2] -cijferig 
    @+199649 [199649] lijk      q0  ? ␅
    @+199649 [199649] lijk      q1  ? after
    @+199649 [199649] lijk      q2  ? ␅
    @+199649 [199649] lijk      q3  ? after
    @+249566 [249566] opi       q6  ? ␅
    @+249566 [249566] opi       q7  ? after
    @+274482 [274482] prop      q8  ? ␅
    @+274482 [274482] prop      q9  ? after
    @+275928 [275928] punt      q16 ? ␅
    @+275928 [275928] punt      q17 ? after
    @+276652 [276652] quiz      q18 ? ␅
    @+276652 [276652] quiz      q19 ? after
    @+276742 [276742] raad      q22 ? ␅
    @+276742 [276742] raad      q23 ? after
    @+276877 [276877] raaf      q24 ? ␅
    @+276877 [276877] raaf      q25 ? after
    @+276921 [276921] raam      q26 ? ␅
    @+276921 [276921] raam      q27 ? it
    @+276921 [276921] raam      done. it
    @+277013 [277013] raap      q20 ? ␅
    @+277013 [277013] raap      q21 ? before
    @+277386 [277386] radio     q14 ? ␅
    @+277386 [277386] radio     q15 ? before
    @+280650 [280650] redding   q12 ? ␅
    @+280650 [280650] redding   q13 ? before
    @+286998 [286998] riool     q10 ? ␅
    @+286998 [286998] riool     q11 ? before
    @+299555 [299555] schroot   q4  ? ␅
    @+299555 [299555] schroot   q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1128 🥳 32 ⏱️ 0:00:36.909334

🤔 32 attempts
📜 1 sessions

    @        [     0] aa            
    @+98147  [ 98147] mac           q0  ? ␅
    @+98147  [ 98147] mac           q1  ? after
    @+109929 [109929] ne            q8  ? ␅
    @+109929 [109929] ne            q9  ? after
    @+111479 [111479] no            q12 ? ␅
    @+111479 [111479] no            q13 ? after
    @+113842 [113842] nu            q14 ? ␅
    @+113842 [113842] nu            q15 ? after
    @+113982 [113982] null          q22 ? ␅
    @+113982 [113982] null          q23 ? after
    @+114058 [114058] numerologists q24 ? ␅
    @+114058 [114058] numerologists q25 ? after
    @+114086 [114086] nun           q26 ? ␅
    @+114086 [114086] nun           q27 ? after
    @+114109 [114109] nuptial       q28 ? ␅
    @+114109 [114109] nuptial       q29 ? after
    @+114120 [114120] nurse         q30 ? ␅
    @+114120 [114120] nurse         q31 ? it
    @+114120 [114120] nurse         done. it
    @+114134 [114134] nurslings     q20 ? ␅
    @+114134 [114134] nurslings     q21 ? before
    @+114426 [114426] object        q18 ? ␅
    @+114426 [114426] object        q19 ? before
    @+115072 [115072] odor          q16 ? ␅
    @+115072 [115072] odor          q17 ? before
    @+116323 [116323] orb           q10 ? ␅
    @+116323 [116323] orb           q11 ? before
    @+122724 [122724] parol         q6  ? ␅
    @+122724 [122724] parol         q7  ? before
    @+147311 [147311] rho           q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1554 🥳 6 ⏱️ 0:00:51.021654

📜 2 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:7600
    ⬜⬜⬜⬜⬜ tried:MORRO n n n n n remain:2719
    ⬜⬜⬜⬜⬜ tried:FUZZY n n n n n remain:1278
    ⬜🟨⬜⬜⬜ tried:PHPHT n m n n n remain:75
    🟨🟩⬜⬜⬜ tried:HEDGE m Y n n n remain:5
    ⬜🟩🟨🟩🟩 tried:WELSH n Y m Y Y remain:1

    Undos used: 1

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1697 🥳 16 ⏱️ 0:02:41.211505

📜 1 sessions
💰 score: 10000

    5/6
    SERAI ⬜⬜⬜⬜🟨
    PITON ⬜🟩🟨⬜⬜
    FILTH ⬜🟩⬜🟨⬜
    DIGIT 🟨🟩⬜🟩🟨
    TIMID 🟩🟩🟩🟩🟩
    3/6
    TIMID ⬜⬜⬜⬜⬜
    AROSE 🟩⬜🟩⬜🟩
    ALONE 🟩🟩🟩🟩🟩
    3/6
    ALONE ⬜⬜⬜⬜⬜
    SPURT ⬜⬜⬜🟨🟨
    BIRTH 🟩🟩🟩🟩🟩
    4/6
    BIRTH ⬜⬜🟨🟨⬜
    RATES 🟨⬜🟨🟨⬜
    OVERT ⬜⬜🟨🟨🟨
    TRUCE 🟩🟩🟩🟩🟩
    Final 1/2
    GROIN 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1674 🥳 score:21 ⏱️ 0:01:23.863608

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. BLESS attempts:4 score:4
2. FELON attempts:8 score:8
3. PORCH attempts:6 score:6
4. CHOSE attempts:3 score:3

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1674 🥳 score:57 ⏱️ 0:01:36.293623

📜 1 sessions

Octordle Classic

1. PANEL attempts:3 score:3
2. LLAMA attempts:10 score:10
3. IDIOM attempts:11 score:11
4. WHELP attempts:5 score:5
5. BIBLE attempts:7 score:7
6. FLUTE attempts:8 score:8
7. PLANK attempts:4 score:4
8. AWARD attempts:9 score:9

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1654 🥳 score:43 ⏱️ 0:02:52.707211

📜 1 sessions

Sedecordle Classic sedecordle.com

1. CLACK attempts:8 score:0
2. CATCH attempts:9 score:8
3. MOODY attempts:17 score:1
4. ALLOY attempts:4 score:7
5. CHAFE attempts:10 score:1
6. AWASH attempts:11 score:0
7. DIRTY attempts:12 score:1
8. ARISE attempts:2 score:2
9. PETTY attempts:13 score:1
10. SPIKE attempts:5 score:3
11. NOBLY attempts:6 score:0
12. NATAL attempts:14 score:6
13. HAZEL attempts:15 score:1
14. CRATE attempts:18 score:5
15. THUMP attempts:16 score:1
16. HOVER attempts:18 score:6

# [squareword.org](squareword.org) 🧩 #1667 🥳 8 ⏱️ 0:03:19.308852

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟨 🟩 🟨 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T R I P
    A R E N A
    B A I L S
    L I K E S
    E L I T E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1604 🥳 158 ⏱️ 0:02:20.274004

🤔 159 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 41 chat prompts
🤖 41 dolphin3:latest replies
🔥  3 🥵  8 😎 42 🥶 97 🧊  8

      $1 #159 designer           100.00°C 🥳 1000‰ ~151 used:0  [150]  source:dolphin3
      $2  #56 design              57.81°C 🔥  998‰  ~10 used:35 [9]    source:dolphin3
      $3 #134 milliner            56.33°C 🔥  996‰   ~3 used:16 [2]    source:dolphin3
      $4 #112 couture             56.27°C 🔥  995‰   ~4 used:16 [3]    source:dolphin3
      $5 #156 chic                46.64°C 🥵  978‰   ~1 used:0  [0]    source:dolphin3
      $6 #114 knitwear            45.06°C 🥵  973‰  ~11 used:4  [10]   source:dolphin3
      $7  #97 fashion             44.30°C 🥵  966‰   ~8 used:3  [7]    source:dolphin3
      $8 #155 boutique            43.23°C 🥵  962‰   ~2 used:1  [1]    source:dolphin3
      $9 #140 millinery           43.10°C 🥵  961‰   ~9 used:3  [8]    source:dolphin3
     $10 #154 stylish             41.76°C 🥵  949‰   ~5 used:2  [4]    source:dolphin3
     $11 #133 craftsmanship       41.19°C 🥵  940‰   ~6 used:2  [5]    source:dolphin3
     $13 #149 artistic            38.03°C 😎  897‰  ~12 used:0  [11]   source:dolphin3
     $55  #40 style               25.19°C 🥶        ~55 used:0  [54]   source:dolphin3
    $152  #19 neck                -0.53°C 🧊       ~152 used:0  [151]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1637 🥳 310 ⏱️ 0:05:36.342444

🤔 311 attempts
📜 1 sessions
🫧 18 chat sessions
⁉️ 89 chat prompts
🤖 89 dolphin3:latest replies
🔥   1 🥵   8 😎  32 🥶 133 🧊 136

      $1 #311 confirmation      100.00°C 🥳 1000‰ ~175 used:0  [174]  source:dolphin3
      $2 #301 confirmer          55.63°C 🔥  998‰   ~1 used:1  [0]    source:dolphin3
      $3 #233 annuler            37.27°C 🥵  971‰  ~36 used:22 [35]   source:dolphin3
      $4 #190 annulation         34.51°C 🥵  956‰  ~40 used:41 [39]   source:dolphin3
      $5 #231 rétractation       34.06°C 🥵  949‰  ~30 used:13 [29]   source:dolphin3
      $6 #225 résilier           33.24°C 🥵  943‰  ~28 used:11 [27]   source:dolphin3
      $7 #197 résiliation        32.84°C 🥵  941‰  ~31 used:20 [30]   source:dolphin3
      $8 #206 modification       31.89°C 🥵  929‰  ~29 used:11 [28]   source:dolphin3
      $9 #292 renvoyer           31.50°C 🥵  926‰   ~2 used:2  [1]    source:dolphin3
     $10 #274 réclamation        30.04°C 🥵  904‰   ~3 used:6  [2]    source:dolphin3
     $11 #204 démenti            27.47°C 😎  845‰  ~37 used:3  [36]   source:dolphin3
     $12 #242 réinitialisation   27.04°C 😎  830‰  ~32 used:2  [31]   source:dolphin3
     $43 #209 révision           16.11°C 🥶        ~57 used:0  [56]   source:dolphin3
    $176 #100 arc                -0.09°C 🧊       ~176 used:0  [175]  source:dolphin3
