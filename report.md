# 2026-08-29

- 🔗 spaceword.org 🧩 2026-08-28 🏁 score 2164 ranked 50.9% 166/326 ⏱️ 0:46:00.570648
- 🔗 wordgrid 🧩 #819 🟪 rarity:0.32 ⏱️ 0:02:27.970558
- 🔗 alfagok.diginaut.net 🧩 #665 🥳 44 ⏱️ 0:00:46.174584
- 🔗 alphaguess.com 🧩 #1132 🥳 28 ⏱️ 0:00:32.212086
- 🔗 dontwordle.com 🧩 #1558 🥳 6 ⏱️ 0:02:46.234191
- 🔗 dictionary.com hurdle 🧩 #1701 🥳 22 ⏱️ 0:03:37.256595
- 🔗 Quordle Classic 🧩 #1678 🥳 score:16 ⏱️ 0:01:37.243948
- 🔗 Octordle Classic 🧩 #1678 🥳 score:68 ⏱️ 0:02:19.677998
- 🔗 Sedecordle Classic 🧩 #1658 🥳 score:47 ⏱️ 0:02:38.094639
- 🔗 squareword.org 🧩 #1671 🥳 7 ⏱️ 0:01:44.518736
- 🔗 cemantle.certitudes.org 🧩 #1608 🥳 86 ⏱️ 0:00:33.426176
- 🔗 cemantix.certitudes.org 🧩 #1641 😦 499 ⏱️ 1:40:02.348602

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

























# [spaceword.org](spaceword.org) 🧩 2026-08-28 🏁 score 2164 ranked 50.9% 166/326 ⏱️ 0:46:00.570648

📜 4 sessions
- tiles: 21/21
- score: 2164 bonus: +64
- rank: 166/326

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ Q _ _ _ _   
      _ _ _ F O U _ _ _ _   
      _ _ _ _ _ A H _ _ _   
      _ _ _ A C R O _ _ _   
      _ _ _ _ _ T A _ _ _   
      _ _ _ _ D O T _ _ _   
      _ _ _ _ _ _ Z _ _ _   
      _ _ _ _ _ _ I _ _ _   
      _ _ _ J E O N _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #819 🟪 rarity:0.32 ⏱️ 0:02:27.970558

📜 2 sessions
🌌 🌌 🦄
🌌 🦄 🌌
🌌 🌌 🌌
Rarity: 0.32 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #665 🥳 44 ⏱️ 0:00:46.174584

🤔 44 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+199647 [199647] lijk         q0  ? ␅
    @+199647 [199647] lijk         q1  ? after
    @+199647 [199647] lijk         q2  ? ␅
    @+199647 [199647] lijk         q3  ? after
    @+199647 [199647] lijk         q4  ? ␅
    @+199647 [199647] lijk         q5  ? after
    @+199647 [199647] lijk         q6  ? ␅
    @+199647 [199647] lijk         q7  ? after
    @+299551 [299551] schroot      q8  ? ␅
    @+299551 [299551] schroot      q9  ? after
    @+311839 [311839] spiert       q14 ? ␅
    @+311839 [311839] spiert       q15 ? after
    @+313096 [313096] sport        q20 ? ␅
    @+313096 [313096] sport        q21 ? after
    @+313501 [313501] sportveld    q24 ? ␅
    @+313501 [313501] sportveld    q25 ? after
    @+313650 [313650] spraak       q26 ? ␅
    @+313650 [313650] spraak       q27 ? after
    @+313766 [313766] spreek       q28 ? ␅
    @+313766 [313766] spreek       q29 ? after
    @+313837 [313837] spreekwoord  q30 ? ␅
    @+313837 [313837] spreekwoord  q31 ? after
    @+313857 [313857] spreid       q32 ? ␅
    @+313857 [313857] spreid       q33 ? after
    @+313882 [313882] spreidvoeten q34 ? ␅
    @+313882 [313882] spreidvoeten q35 ? after
    @+313889 [313889] spreke       q36 ? ␅
    @+313889 [313889] spreke       q37 ? after
    @+313890 [313890] spreken      q43 ? it
    @+313890 [313890] spreken      done. it

# [alphaguess.com](alphaguess.com) 🧩 #1132 🥳 28 ⏱️ 0:00:32.212086

🤔 28 attempts
📜 1 sessions

    @       [    0] aa      
    @+2     [    2] aahed   
    @+47378 [47378] dis     q6  ? ␅
    @+47378 [47378] dis     q7  ? after
    @+72662 [72662] green   q8  ? ␅
    @+72662 [72662] green   q9  ? after
    @+74223 [74223] gyve    q16 ? ␅
    @+74223 [74223] gyve    q17 ? after
    @+74991 [74991] hammer  q18 ? ␅
    @+74991 [74991] hammer  q19 ? after
    @+75047 [75047] hand    q22 ? ␅
    @+75047 [75047] hand    q23 ? after
    @+75181 [75181] hands   q24 ? ␅
    @+75181 [75181] hands   q25 ? after
    @+75242 [75242] hang    q26 ? ␅
    @+75242 [75242] hang    q27 ? it
    @+75242 [75242] hang    done. it
    @+75325 [75325] hap     q20 ? ␅
    @+75325 [75325] hap     q21 ? before
    @+75781 [75781] hat     q14 ? ␅
    @+75781 [75781] hat     q15 ? before
    @+79019 [79019] hone    q12 ? ␅
    @+79019 [79019] hone    q13 ? before
    @+85397 [85397] inocula q10 ? ␅
    @+85397 [85397] inocula q11 ? before
    @+98147 [98147] mac     q0  ? ␅
    @+98147 [98147] mac     q1  ? after
    @+98147 [98147] mac     q2  ? ␅
    @+98147 [98147] mac     q3  ? after
    @+98147 [98147] mac     q4  ? ␅
    @+98147 [98147] mac     q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1558 🥳 6 ⏱️ 0:02:46.234191

📜 1 sessions
💰 score: 21

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:7346
    ⬜⬜⬜⬜⬜ tried:SHUSH n n n n n remain:2262
    ⬜⬜⬜⬜⬜ tried:JOLLY n n n n n remain:574
    🟨⬜⬜⬜⬜ tried:ABAKA m n n n n remain:108
    ⬜🟩⬜🟩⬜ tried:EAGER n Y n Y n remain:9
    ⬜🟩⬜🟩⬜ tried:WAXEN n Y n Y n remain:3

    Undos used: 4

      3 words remaining
    x 7 unused letters
    = 21 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1701 🥳 22 ⏱️ 0:03:37.256595

📜 1 sessions
💰 score: 9400

    5/6
    LANES ⬜⬜⬜🟨⬜
    RIDGE 🟨⬜⬜⬜🟩
    FORTE ⬜🟨🟨⬜🟩
    CHORE 🟨🟨🟨🟩🟩
    OCHRE 🟩🟩🟩🟩🟩
    5/6
    OCHRE ⬜🟨🟨⬜⬜
    CHIAS 🟨🟨⬜⬜⬜
    LYNCH ⬜⬜🟩🟩🟩
    DUMBO ⬜🟩⬜🟨⬜
    BUNCH 🟩🟩🟩🟩🟩
    5/6
    BUNCH ⬜⬜⬜⬜⬜
    ASTER 🟨⬜⬜⬜🟩
    MOLAR ⬜🟨⬜🟨🟩
    VAPOR 🟨🟩⬜🟩🟩
    FAVOR 🟩🟩🟩🟩🟩
    5/6
    FAVOR ⬜⬜⬜🟨⬜
    NOMES ⬜🟩⬜⬜⬜
    LOTIC ⬜🟩🟨⬜⬜
    YOUTH 🟨🟩⬜🟨⬜
    TODDY 🟩🟩🟩🟩🟩
    Final 2/2
    FATLY 🟩🟩🟩⬜🟩
    FATTY 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1678 🥳 score:16 ⏱️ 0:01:37.243948

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. OVINE attempts:4 score:4
2. ALLOY attempts:7 score:7
3. VOICE attempts:3 score:3
4. CARVE attempts:2 score:2

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1678 🥳 score:68 ⏱️ 0:02:19.677998

📜 1 sessions

Octordle Classic

1. ATONE attempts:7 score:7
2. TAMER attempts:4 score:4
3. VISIT attempts:8 score:8
4. RACER attempts:10 score:10
5. SOOTY attempts:12 score:13
6. TIGER attempts:5 score:5
7. KNACK attempts:9 score:9
8. PUPPY attempts:12 score:12

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1658 🥳 score:47 ⏱️ 0:02:38.094639

📜 1 sessions

Sedecordle Classic sedecordle.com

1. TERSE attempts:3 score:0
2. CHOCK attempts:16 score:3
3. THOSE attempts:5 score:0
4. QUEUE attempts:8 score:5
5. UNDER attempts:6 score:0
6. VIGOR attempts:11 score:6
7. BOUGH attempts:7 score:0
8. JOUST attempts:4 score:7
9. IRONY attempts:9 score:0
10. VOTER attempts:10 score:9
11. SHAFT attempts:12 score:1
12. DYING attempts:13 score:2
13. ALOFT attempts:14 score:1
14. KNEED attempts:15 score:4
15. MOODY attempts:18 score:1
16. PHASE attempts:17 score:8

# [squareword.org](squareword.org) 🧩 #1671 🥳 7 ⏱️ 0:01:44.518736

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C R A P S
    Z E B R A
    A B O U T
    R U D D Y
    S T E E R

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1608 🥳 86 ⏱️ 0:00:33.426176

🤔 87 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 13 chat prompts
🤖 13 dolphin3:latest replies
🥵  3 😎  8 🥶 74 🧊  1

     $1 #87 atomic            100.00°C 🥳 1000‰ ~86 used:0 [85]  source:dolphin3
     $2 #69 electromagnetism   40.12°C 🥵  959‰  ~3 used:3 [2]   source:dolphin3
     $3 #85 radioactivity      39.55°C 🥵  954‰  ~2 used:2 [1]   source:dolphin3
     $4 #78 radiation          38.42°C 🥵  946‰  ~1 used:0 [0]   source:dolphin3
     $5 #42 electromagnetic    34.21°C 😎  879‰  ~4 used:1 [3]   source:dolphin3
     $6 #82 photon             33.92°C 😎  866‰  ~5 used:0 [4]   source:dolphin3
     $7 #77 electromagnet      32.88°C 😎  839‰  ~6 used:0 [5]   source:dolphin3
     $8 #75 transistor         31.33°C 😎  777‰  ~7 used:0 [6]   source:dolphin3
     $9 #81 gamma              30.09°C 😎  704‰  ~8 used:0 [7]   source:dolphin3
    $10 #71 magnetic           27.55°C 😎  473‰  ~9 used:0 [8]   source:dolphin3
    $11 #33 power              25.78°C 😎  237‰ ~11 used:2 [10]  source:dolphin3
    $12 #37 capacitance        24.53°C 😎    4‰ ~10 used:0 [9]   source:dolphin3
    $13 #19 microchip          23.38°C 🥶       ~12 used:4 [11]  source:dolphin3
    $87 #26 board              -4.11°C 🧊       ~87 used:0 [86]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1641 😦 499 ⏱️ 1:40:02.348602

🤔 498 attempts
📜 1 sessions
🫧 49 chat sessions
⁉️ 270 chat prompts
🤖 270 dolphin3:latest replies
😦 🔥   3 🥵  21 😎  81 🥶 309 🧊  84

      $1 #333 totalité            48.31°C 🔥  998‰  ~83 used:119 [82]   source:dolphin3
      $2 #175 total               44.53°C 🔥  997‰  ~84 used:127 [83]   source:dolphin3
      $3 #446 répartir            41.13°C 🔥  992‰   ~2 used:45  [1]    source:dolphin3
      $4 #172 partie              39.37°C 🥵  987‰  ~99 used:51  [98]   source:dolphin3
      $5 #155 pourcentage         38.36°C 🥵  983‰  ~86 used:29  [85]   source:dolphin3
      $6 #228 montant             38.09°C 🥵  981‰   ~3 used:9   [2]    source:dolphin3
      $7 #160 fraction            37.86°C 🥵  979‰  ~15 used:10  [14]   source:dolphin3
      $8 #494 allouer             37.79°C 🥵  978‰   ~1 used:3   [0]    source:dolphin3
      $9 #202 totaliser           36.65°C 🥵  972‰   ~4 used:9   [3]    source:dolphin3
     $10 #450 diviser             35.16°C 🥵  966‰   ~5 used:9   [4]    source:dolphin3
     $11 #229 nombre              35.07°C 🥵  965‰   ~6 used:9   [5]    source:dolphin3
     $25 #191 séparément          30.16°C 😎  896‰  ~16 used:0   [15]   source:dolphin3
    $106 #283 complètement        19.85°C 🥶       ~108 used:0   [107]  source:dolphin3
    $415 #124 quadruple           -0.05°C 🧊       ~415 used:0   [414]  source:dolphin3
