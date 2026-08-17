# 2026-08-18

- 🔗 wordgrid 🧩 #808 🟪 rarity:0.18 ⏱️ 0:04:04.462274
- 🔗 spaceword.org 🧩 2026-08-17 🏁 score 2168 ranked 39.6% 134/338 ⏱️ 6:09:34.412878
- 🔗 alfagok.diginaut.net 🧩 #654 🥳 40 ⏱️ 0:00:51.359735
- 🔗 alphaguess.com 🧩 #1121 🥳 24 ⏱️ 0:00:26.570520
- 🔗 dontwordle.com 🧩 #1547 🥳 6 ⏱️ 0:01:14.299725
- 🔗 dictionary.com hurdle 🧩 #1690 😦 22 ⏱️ 0:03:55.277692
- 🔗 Quordle Classic 🧩 #1667 🥳 score:19 ⏱️ 0:01:14.265711
- 🔗 Octordle Classic 🧩 #1667 🥳 score:53 ⏱️ 0:02:07.806326
- 🔗 Sedecordle Classic 🧩 #1647 🥳 score:43 ⏱️ 0:02:15.973161
- 🔗 squareword.org 🧩 #1660 🥳 7 ⏱️ 0:02:13.738182
- 🔗 cemantle.certitudes.org 🧩 #1597 🥳 825 ⏱️ 0:45:42.543597
- 🔗 cemantix.certitudes.org 🧩 #1630 🥳 235 ⏱️ 0:04:13.071731

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














# [spaceword.org](spaceword.org) 🧩 2026-08-17 🏁 score 2168 ranked 39.6% 134/338 ⏱️ 6:09:34.412878

📜 6 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 134/338

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ N _ H _ J _ A Y _   
      _ A Q U A E _ D O _   
      _ B _ N A T I O N _   
      _ _ _ K _ _ _ _ I _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #808 🟪 rarity:0.18 ⏱️ 0:04:04.462274

📜 2 sessions
🌌 🌌 🌌
🦄 🌌 🦄
🦄 🌌 🦄
Rarity: 0.18 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #654 🥳 40 ⏱️ 0:00:51.359735

🤔 40 attempts
📜 1 sessions

    @        [     0] &-teken          
    @+199547 [199547] lij              q0  ? ␅
    @+199547 [199547] lij              q1  ? after
    @+199547 [199547] lij              q2  ? ␅
    @+199547 [199547] lij              q3  ? after
    @+247602 [247602] op               q6  ? ␅
    @+247602 [247602] op               q7  ? after
    @+273399 [273399] proef            q8  ? ␅
    @+273399 [273399] proef            q9  ? after
    @+279665 [279665] rechts           q12 ? ␅
    @+279665 [279665] rechts           q13 ? after
    @+283035 [283035] relatie          q14 ? ␅
    @+283035 [283035] relatie          q15 ? after
    @+283046 [283046] relatiebreuken   q28 ? ␅
    @+283046 [283046] relatiebreuken   q29 ? after
    @+283046 [283046] relatiebreuken   q30 ? ␅
    @+283046 [283046] relatiebreuken   q31 ? after
    @+283052 [283052] relatiedrama     q32 ? ␅
    @+283052 [283052] relatiedrama     q33 ? after
    @+283053 [283053] relatief         q38 ? ␅
    @+283053 [283053] relatief         q39 ? it
    @+283053 [283053] relatief         done. it
    @+283054 [283054] relatiegebied    q36 ? ␅
    @+283054 [283054] relatiegebied    q37 ? before
    @+283055 [283055] relatiegericht   q34 ? ␅
    @+283055 [283055] relatiegericht   q35 ? before
    @+283057 [283057] relatiegeschenk  q26 ? ␅
    @+283057 [283057] relatiegeschenk  q27 ? before
    @+283080 [283080] relatieperikelen q24 ? ␅
    @+283080 [283080] relatieperikelen q25 ? before
    @+283125 [283125] relax            q23 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1121 🥳 24 ⏱️ 0:00:26.570520

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
    @+98490  [ 98490] mag     q18 ? ␅
    @+98490  [ 98490] mag     q19 ? after
    @+98565  [ 98565] magnet  q22 ? ␅
    @+98565  [ 98565] magnet  q23 ? it
    @+98565  [ 98565] magnet  done. it
    @+98669  [ 98669] mahjong q20 ? ␅
    @+98669  [ 98669] mahjong q21 ? before
    @+98854  [ 98854] make    q16 ? ␅
    @+98854  [ 98854] make    q17 ? before
    @+99571  [ 99571] mans    q14 ? ␅
    @+99571  [ 99571] mans    q15 ? before
    @+101042 [101042] media   q12 ? ␅
    @+101042 [101042] media   q13 ? before
    @+104011 [104011] minis   q10 ? ␅
    @+104011 [104011] minis   q11 ? before
    @+109929 [109929] ne      q8  ? ␅
    @+109929 [109929] ne      q9  ? before
    @+122724 [122724] parol   q6  ? ␅
    @+122724 [122724] parol   q7  ? before
    @+147311 [147311] rho     q4  ? ␅
    @+147311 [147311] rho     q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1547 🥳 6 ⏱️ 0:01:14.299725

📜 1 sessions
💰 score: 16

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:TENNE n n n n n remain:4097
    ⬜⬜⬜⬜⬜ tried:MAMMA n n n n n remain:1590
    ⬜⬜⬜⬜⬜ tried:YUPPY n n n n n remain:614
    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:182
    ⬜⬜⬜🟩⬜ tried:GRRRL n n n Y n remain:7
    ⬜⬜🟩🟩🟩 tried:CHORD n n Y Y Y remain:2

    Undos used: 3

      2 words remaining
    x 8 unused letters
    = 16 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1690 😦 22 ⏱️ 0:03:55.277692

📜 2 sessions
💰 score: 4430

    4/6
    BASER ⬜🟩⬜⬜⬜
    PATLY ⬜🟩⬜🟩🟩
    DAILY 🟨🟩⬜🟩🟩
    MADLY 🟩🟩🟩🟩🟩
    5/6
    MADLY ⬜⬜⬜🟩⬜
    COILS ⬜⬜⬜🟩⬜
    BUGLE ⬜⬜⬜🟩🟨
    KNELT ⬜⬜🟩🟩⬜
    WHELP 🟩🟩🟩🟩🟩
    6/6
    WHELP ⬜⬜⬜⬜⬜
    ROADS ⬜⬜🟨⬜⬜
    CABIN ⬜🟩⬜⬜⬜
    GAUZY ⬜🟩⬜⬜🟩
    MOTIF ⬜⬜🟨⬜🟨
    TAFFY 🟩🟩🟩🟩🟩
    5/6
    TAFFY ⬜🟩⬜⬜⬜
    EARNS ⬜🟩🟨⬜⬜
    LAIRD 🟨🟩⬜🟨⬜
    VALOR ⬜🟩🟩⬜🟨
    RALPH 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜🟨⬜⬜🟨
    ????? 🟨🟨⬜🟨⬜

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1667 🥳 score:19 ⏱️ 0:01:14.265711

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. ALGAE attempts:7 score:7
2. MANOR attempts:5 score:5
3. DONOR attempts:4 score:4
4. DEALT attempts:3 score:3

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1667 🥳 score:53 ⏱️ 0:02:07.806326

📜 1 sessions

Octordle Classic

1. UPSET attempts:4 score:4
2. DRESS attempts:6 score:6
3. SETUP attempts:3 score:3
4. AMUSE attempts:5 score:5
5. MACHO attempts:8 score:8
6. RARER attempts:11 score:11
7. AWASH attempts:7 score:7
8. GRUFF attempts:9 score:9

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1647 🥳 score:43 ⏱️ 0:02:15.973161

📜 1 sessions

Sedecordle Classic sedecordle.com

1. LEACH attempts:11 score:1
2. NURSE attempts:4 score:1
3. MELON attempts:3 score:0
4. VYING attempts:16 score:3
5. JUICE attempts:12 score:1
6. ROOMY attempts:5 score:2
7. PALSY attempts:6 score:0
8. PRONE attempts:7 score:6
9. BOOTY attempts:17 score:1
10. TREAT attempts:14 score:7
11. QUEUE attempts:8 score:0
12. TRAMP attempts:9 score:8
13. FLANK attempts:18 score:1
14. CUMIN attempts:10 score:8
15. CHANT attempts:13 score:1
16. NEEDY attempts:15 score:3

# [squareword.org](squareword.org) 🧩 #1660 🥳 7 ⏱️ 0:02:13.738182

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S H A M E
    N O M A D
    A M O N G
    R E U S E
    L Y R E S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1597 🥳 825 ⏱️ 0:45:42.543597

🤔 826 attempts
📜 3 sessions
🫧 83 chat sessions
⁉️ 476 chat prompts
🤖 14 gemma4:12b replies
🤖 92 qwen3.8:latest replies
🤖 370 dolphin3:latest replies
😱   1 🔥   7 🥵  30 😎 126 🥶 642 🧊  19

      $1 #826 trait              100.00°C 🥳 1000‰ ~807 used:0   [806]  source:gemma4  
      $2 #798 characteristic      65.77°C 😱  999‰   ~1 used:7   [0]    source:gemma4  
      $3 #799 innate              50.76°C 🔥  998‰   ~4 used:4   [3]    source:gemma4  
      $4 #102 stubbornness        46.95°C 🔥  996‰ ~158 used:453 [157]  source:dolphin3
      $5 #423 temperament         46.24°C 🔥  994‰  ~88 used:151 [87]   source:dolphin3
      $6 #230 attitude            46.21°C 🔥  993‰ ~155 used:210 [154]  source:dolphin3
      $7 #809 inborn              45.82°C 🔥  992‰   ~2 used:2   [1]    source:gemma4  
      $8 #789 instinct            44.66°C 🔥  991‰   ~3 used:3   [2]    source:gemma4  
      $9 #777 predisposition      44.29°C 🔥  990‰   ~5 used:4   [4]    source:qwen3   
     $10 #780 tendency            43.65°C 🥵  986‰   ~6 used:1   [5]    source:gemma4  
     $11 #179 contrariness        43.12°C 🥵  985‰ ~161 used:51  [160]  source:dolphin3
     $40 #405 snobbishness        37.90°C 😎  899‰  ~96 used:2   [95]   source:dolphin3
    $166 #270 arrogant            28.98°C 🥶       ~167 used:0   [166]  source:dolphin3
    $808  #15 chill               -0.16°C 🧊       ~808 used:0   [807]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1630 🥳 235 ⏱️ 0:04:13.071731

🤔 236 attempts
📜 1 sessions
🫧 13 chat sessions
⁉️ 69 chat prompts
🤖 69 dolphin3:latest replies
🥵   7 😎  38 🥶 159 🧊  31

      $1 #236 pilote           100.00°C 🥳 1000‰ ~205 used:0  [204]  source:dolphin3
      $2 #227 avion             42.87°C 🥵  981‰   ~1 used:0  [0]    source:dolphin3
      $3  #11 roulage           39.52°C 🥵  965‰  ~44 used:68 [43]   source:dolphin3
      $4  #76 mécanicien        38.82°C 🥵  961‰  ~43 used:41 [42]   source:dolphin3
      $5 #199 aérodynamisme     35.00°C 🥵  924‰   ~4 used:8  [3]    source:dolphin3
      $6 #198 aérodynamique     34.04°C 🥵  916‰   ~2 used:6  [1]    source:dolphin3
      $7 #185 simulateur        33.50°C 🥵  909‰   ~5 used:10 [4]    source:dolphin3
      $8 #194 vol               32.82°C 🥵  900‰   ~3 used:7  [2]    source:dolphin3
      $9  #73 constructeur      30.18°C 😎  856‰  ~45 used:10 [44]   source:dolphin3
     $10 #103 prototype         29.87°C 😎  848‰  ~16 used:2  [15]   source:dolphin3
     $11 #182 propulseur        27.05°C 😎  790‰  ~17 used:2  [16]   source:dolphin3
     $12 #149 contrôleur        26.47°C 😎  779‰  ~18 used:2  [17]   source:dolphin3
     $47  #32 soute             16.67°C 🥶        ~47 used:0  [46]   source:dolphin3
    $206 #213 moulage           -0.28°C 🧊       ~206 used:0  [205]  source:dolphin3
