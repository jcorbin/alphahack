# 2026-08-26

- 🔗 spaceword.org 🧩 2026-08-25 🏁 score 2168 ranked 34.4% 118/343 ⏱️ 0:13:05.464017
- 🔗 wordgrid 🧩 #816 🟪 rarity:0.23 ⏱️ 0:02:52.407022
- 🔗 alfagok.diginaut.net 🧩 #662 🥳 36 ⏱️ 0:00:38.823337
- 🔗 alphaguess.com 🧩 #1129 🥳 34 ⏱️ 0:00:39.789657
- 🔗 dontwordle.com 🧩 #1555 🥳 6 ⏱️ 0:01:18.691532
- 🔗 dictionary.com hurdle 🧩 #1698 🥳 17 ⏱️ 0:04:38.824495
- 🔗 Quordle Classic 🧩 #1675 🥳 score:22 ⏱️ 0:02:18.624443
- 🔗 Octordle Classic 🧩 #1675 🥳 score:51 ⏱️ 0:01:32.494975
- 🔗 Sedecordle Classic 🧩 #1655 🥳 score:48 ⏱️ 0:02:07.122883
- 🔗 squareword.org 🧩 #1668 🥳 7 ⏱️ 0:01:47.970238
- 🔗 cemantle.certitudes.org 🧩 #1605 🥳 100 ⏱️ 0:01:21.853956
- 🔗 cemantix.certitudes.org 🧩 #1638 🥳 171 ⏱️ 0:06:18.220598

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






















# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #816 🟪 rarity:0.23 ⏱️ 0:02:52.407022

📜 4 sessions
🦄 🦄 🌌
🦄 🦄 🦄
🦄 🌌 🌌
Rarity: 0.23 🟪

# [spaceword.org](spaceword.org) 🧩 2026-08-25 🏁 score 2168 ranked 34.4% 118/343 ⏱️ 0:13:05.464017

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 118/343

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ C O I R _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ _ A _ Q _ _ _   
      _ _ _ _ Z _ U _ _ _   
      _ _ _ C O D E _ _ _   
      _ _ _ _ T A T _ _ _   
      _ _ _ F E _ _ _ _ _   
      _ _ _ _ D E X _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #662 🥳 36 ⏱️ 0:00:38.823337

🤔 36 attempts
📜 1 sessions

    @       [    0] &-teken   
    @+49809 [49809] boks      q4  ? ␅
    @+49809 [49809] boks      q5  ? after
    @+52651 [52651] bouw      q12 ? ␅
    @+52651 [52651] bouw      q13 ? after
    @+54234 [54234] brandstof q14 ? ␅
    @+54234 [54234] brandstof q15 ? after
    @+54643 [54643] breedband q18 ? ␅
    @+54643 [54643] breedband q19 ? after
    @+54834 [54834] brei      q20 ? ␅
    @+54834 [54834] brei      q21 ? after
    @+54949 [54949] bren      q22 ? ␅
    @+54949 [54949] bren      q23 ? after
    @+54954 [54954] breng     q28 ? ␅
    @+54954 [54954] breng     q29 ? after
    @+54956 [54956] brengen   q34 ? ␅
    @+54956 [54956] brengen   q35 ? it
    @+54956 [54956] brengen   done. it
    @+54960 [54960] brengers  q32 ? ␅
    @+54960 [54960] brengers  q33 ? before
    @+54965 [54965] brengt    q30 ? ␅
    @+54965 [54965] brengt    q31 ? before
    @+54975 [54975] bres      q26 ? ␅
    @+54975 [54975] bres      q27 ? before
    @+55005 [55005] breuk     q24 ? ␅
    @+55005 [55005] breuk     q25 ? before
    @+55065 [55065] brevet    q16 ? ␅
    @+55065 [55065] brevet    q17 ? before
    @+55901 [55901] bron      q10 ? ␅
    @+55901 [55901] bron      q11 ? before
    @+62248 [62248] cement    q9  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1129 🥳 34 ⏱️ 0:00:39.789657

🤔 34 attempts
📜 1 sessions

    @       [    0] aa        
    @+11763 [11763] back      q6  ? ␅
    @+11763 [11763] back      q7  ? after
    @+13801 [13801] be        q10 ? ␅
    @+13801 [13801] be        q11 ? after
    @+15757 [15757] bewrap    q12 ? ␅
    @+15757 [15757] bewrap    q13 ? after
    @+15813 [15813] bi        q18 ? ␅
    @+15813 [15813] bi        q19 ? after
    @+15841 [15841] bib       q22 ? ␅
    @+15841 [15841] bib       q23 ? after
    @+15926 [15926] bicarb    q24 ? ␅
    @+15926 [15926] bicarb    q25 ? after
    @+15971 [15971] bicorn    q26 ? ␅
    @+15971 [15971] bicorn    q27 ? after
    @+15981 [15981] bicuspid  q30 ? ␅
    @+15981 [15981] bicuspid  q31 ? after
    @+15984 [15984] bicycle   q32 ? ␅
    @+15984 [15984] bicycle   q33 ? it
    @+15984 [15984] bicycle   done. it
    @+15993 [15993] bid       q28 ? ␅
    @+15993 [15993] bid       q29 ? before
    @+16018 [16018] bidi      q20 ? ␅
    @+16018 [16018] bidi      q21 ? before
    @+16231 [16231] bilingual q16 ? ␅
    @+16231 [16231] bilingual q17 ? before
    @+16727 [16727] bios      q14 ? ␅
    @+16727 [16727] bios      q15 ? before
    @+17714 [17714] blind     q8  ? ␅
    @+17714 [17714] blind     q9  ? before
    @+23680 [23680] camp      q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1555 🥳 6 ⏱️ 0:01:18.691532

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:7419
    ⬜⬜⬜⬜⬜ tried:SKEES n n n n n remain:1466
    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:640
    ⬜⬜⬜⬜🟩 tried:PHPHT n n n n Y remain:32
    ⬜⬜🟩⬜🟩 tried:FRONT n n Y n Y remain:3
    🟩🟩🟩⬜🟩 tried:CLOOT Y Y Y n Y remain:1

    Undos used: 3

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1698 🥳 17 ⏱️ 0:04:38.824495

📜 1 sessions
💰 score: 9900

    4/6
    AEONS ⬜🟨⬜⬜⬜
    GRIDE ⬜🟨⬜⬜🟨
    TUBER 🟩⬜⬜🟩🟨
    THREW 🟩🟩🟩🟩🟩
    6/6
    THREW ⬜⬜🟨🟩⬜
    AIDER ⬜⬜⬜🟩🟩
    LOVER ⬜🟩⬜🟩🟩
    COPER ⬜🟩⬜🟩🟩
    JUNKS ⬜⬜🟩⬜⬜
    GONER 🟩🟩🟩🟩🟩
    3/6
    GONER ⬜⬜⬜⬜⬜
    SILTY ⬜🟨⬜🟩⬜
    FAITH 🟩🟩🟩🟩🟩
    2/6
    FAITH 🟩🟨🟩⬜⬜
    FRIAR 🟩🟩🟩🟩🟩
    Final 2/2
    VAMPS ⬜🟨🟨⬜⬜
    MOLAR 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1675 🥳 score:22 ⏱️ 0:02:18.624443

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. OPIUM attempts:4 score:4
2. EPOCH attempts:6 score:6
3. BESET attempts:5 score:5
4. FINER attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1675 🥳 score:51 ⏱️ 0:01:32.494975

📜 1 sessions

Octordle Classic

1. BOBBY attempts:12 score:12
2. FREED attempts:9 score:9
3. STRAP attempts:5 score:5
4. RAISE attempts:1 score:1
5. INEPT attempts:3 score:3
6. NINJA attempts:10 score:10
7. CHIDE attempts:7 score:7
8. SPURT attempts:4 score:4

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1655 🥳 score:48 ⏱️ 0:02:07.122883

📜 1 sessions

Sedecordle Classic sedecordle.com

1. CRUMB attempts:7 score:0
2. RULER attempts:14 score:7
3. GOLLY attempts:9 score:0
4. HINGE attempts:11 score:9
5. AMONG attempts:8 score:0
6. GOURD attempts:10 score:8
7. BLEAK attempts:12 score:1
8. PLUME attempts:13 score:2
9. PURER attempts:15 score:1
10. MOIST attempts:6 score:5
11. VIOLA attempts:3 score:0
12. FAVOR attempts:4 score:3
13. HENCE attempts:16 score:1
14. CHILL attempts:19 score:6
15. AXIOM attempts:5 score:0
16. SHREW attempts:17 score:5

# [squareword.org](squareword.org) 🧩 #1668 🥳 7 ⏱️ 0:01:47.970238

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P E C A N
    A E R I E
    T R A D E
    C I T E D
    H E E D S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1605 🥳 100 ⏱️ 0:01:21.853956

🤔 101 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 27 chat prompts
🤖 27 dolphin3:latest replies
😎  5 🥶 91 🧊  4

      $1 #101 antibiotic      100.00°C 🥳 1000‰  ~97 used:0  [96]   source:dolphin3
      $2  #94 bronchodilator   49.39°C 😎  859‰   ~3 used:5  [2]    source:dolphin3
      $3  #99 glucocorticoid   47.59°C 😎  799‰   ~2 used:3  [1]    source:dolphin3
      $4  #95 albuterol        44.12°C 😎  634‰   ~4 used:5  [3]    source:dolphin3
      $5  #93 asthma           40.38°C 😎  394‰   ~1 used:1  [0]    source:dolphin3
      $6  #89 inhaler          38.44°C 😎  206‰   ~5 used:5  [4]    source:dolphin3
      $7  #90 inhalation       35.67°C 🥶        ~12 used:3  [11]   source:dolphin3
      $8  #75 flavoring        34.75°C 🥶         ~6 used:10 [5]    source:dolphin3
      $9  #96 nebulizer        33.07°C 🥶        ~16 used:0  [15]   source:dolphin3
     $10  #72 aerosol          31.54°C 🥶         ~7 used:9  [6]    source:dolphin3
     $11  #56 spray            30.80°C 🥶         ~8 used:6  [7]    source:dolphin3
     $12  #65 syrup            30.68°C 🥶        ~13 used:3  [12]   source:dolphin3
     $13  #60 rinse            30.40°C 🥶        ~17 used:1  [16]   source:dolphin3
     $98  #69 pool             -1.24°C 🧊        ~98 used:0  [97]   source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1638 🥳 171 ⏱️ 0:06:18.220598

🤔 172 attempts
📜 1 sessions
🫧 14 chat sessions
⁉️ 73 chat prompts
🤖 73 dolphin3:latest replies
🔥   2 🥵   5 😎  22 🥶 124 🧊  18

      $1 #172 prêtre            100.00°C 🥳 1000‰ ~154 used:0  [153]  source:dolphin3
      $2 #168 diacre             61.76°C 🔥  998‰   ~1 used:0  [0]    source:dolphin3
      $3 #170 ordination         51.50°C 🔥  990‰   ~2 used:0  [1]    source:dolphin3
      $4 #147 messe              46.32°C 🥵  973‰   ~6 used:4  [5]    source:dolphin3
      $5 #162 sacrement          45.55°C 🥵  961‰   ~5 used:3  [4]    source:dolphin3
      $6 #150 prière             44.02°C 🥵  950‰   ~7 used:4  [6]    source:dolphin3
      $7 #146 communion          43.88°C 🥵  949‰   ~3 used:1  [2]    source:dolphin3
      $8 #164 archevêque         41.02°C 🥵  910‰   ~4 used:0  [3]    source:dolphin3
      $9 #135 liturgie           38.77°C 😎  882‰  ~24 used:2  [23]   source:dolphin3
     $10 #144 eucharistie        38.27°C 😎  872‰   ~8 used:1  [7]    source:dolphin3
     $11 #161 offrande           37.51°C 😎  854‰   ~9 used:0  [8]    source:dolphin3
     $12 #171 pape               37.47°C 😎  853‰  ~10 used:0  [9]    source:dolphin3
     $31 #155 psaume             23.29°C 🥶        ~40 used:0  [39]   source:dolphin3
    $155  #72 élégant            -0.01°C 🧊       ~155 used:0  [154]  source:dolphin3
