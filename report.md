# 2026-08-21

- 🔗 wordgrid 🧩 #811 🟪 rarity:0.17 ⏱️ 0:02:25.316506
- 🔗 spaceword.org 🧩 2026-08-20 🏁 score 2173 ranked 7.4% 24/326 ⏱️ 0:34:52.355918
- 🔗 alfagok.diginaut.net 🧩 #657 🥳 48 ⏱️ 0:00:56.368331
- 🔗 alphaguess.com 🧩 #1124 🥳 30 ⏱️ 0:00:36.695268
- 🔗 dontwordle.com 🧩 #1550 🥳 6 ⏱️ 0:01:26.426855
- 🔗 dictionary.com hurdle 🧩 #1693 😦 20 ⏱️ 0:10:13.156790
- 🔗 Quordle Classic 🧩 #1670 🥳 score:18 ⏱️ 0:01:04.446241
- 🔗 Octordle Classic 🧩 #1670 🥳 score:57 ⏱️ 0:01:39.067270
- 🔗 Sedecordle Classic 🧩 #1650 🥳 score:51 ⏱️ 0:02:29.229125
- 🔗 squareword.org 🧩 #1663 🥳 9 ⏱️ 0:02:26.148355
- 🔗 cemantle.certitudes.org 🧩 #1600 🥳 43 ⏱️ 0:00:38.421280
- 🔗 cemantix.certitudes.org 🧩 #1633 🥳 90 ⏱️ 0:01:31.906394

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

















# [spaceword.org](spaceword.org) 🧩 2026-08-20 🏁 score 2173 ranked 7.4% 24/326 ⏱️ 0:34:52.355918

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 24/326

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ D E W _ _ H A K U   
      _ O R A T E _ X I _   
      _ G _ G O R I E R _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #811 🟪 rarity:0.17 ⏱️ 0:02:25.316506

📜 2 sessions
🦄 🌌 🌌
🌌 🦄 🌌
🦄 🌌 🌌
Rarity: 0.17 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #657 🥳 48 ⏱️ 0:00:56.368331

🤔 48 attempts
📜 1 sessions

    @        [     0] &-teken          
    @+199650 [199650] lijk             q0  ? ␅
    @+199650 [199650] lijk             q1  ? after
    @+199650 [199650] lijk             q2  ? ␅
    @+199650 [199650] lijk             q3  ? after
    @+199650 [199650] lijk             q4  ? ␅
    @+199650 [199650] lijk             q5  ? after
    @+249567 [249567] opi              q8  ? ␅
    @+249567 [249567] opi              q9  ? after
    @+254188 [254188] over             q14 ? ␅
    @+254188 [254188] over             q15 ? after
    @+254941 [254941] overheids        q20 ? ␅
    @+254941 [254941] overheids        q21 ? after
    @+255175 [255175] overheidsstukken q24 ? ␅
    @+255175 [255175] overheidsstukken q25 ? after
    @+255292 [255292] overijverig      q36 ? ␅
    @+255292 [255292] overijverig      q37 ? after
    @+255347 [255347] overkoken        q38 ? ␅
    @+255347 [255347] overkoken        q39 ? after
    @+255350 [255350] overkom          q44 ? ␅
    @+255350 [255350] overkom          q45 ? after
    @+255353 [255353] overkomen        q46 ? ␅
    @+255353 [255353] overkomen        q47 ? it
    @+255353 [255353] overkomen        done. it
    @+255360 [255360] overkook         q42 ? ␅
    @+255360 [255360] overkook         q43 ? before
    @+255374 [255374] overlaad         q40 ? ␅
    @+255374 [255374] overlaad         q41 ? before
    @+255404 [255404] overlast         q22 ? ␅
    @+255404 [255404] overlast         q23 ? before
    @+255878 [255878] overs            q19 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1124 🥳 30 ⏱️ 0:00:36.695268

🤔 30 attempts
📜 1 sessions

    @        [     0] aa         
    @+98147  [ 98147] mac        q0  ? ␅
    @+98147  [ 98147] mac        q1  ? after
    @+98147  [ 98147] mac        q2  ? ␅
    @+98147  [ 98147] mac        q3  ? after
    @+109929 [109929] ne         q10 ? ␅
    @+109929 [109929] ne         q11 ? after
    @+111479 [111479] no         q14 ? ␅
    @+111479 [111479] no         q15 ? after
    @+111582 [111582] nog        q24 ? ␅
    @+111582 [111582] nog        q25 ? after
    @+111601 [111601] noise      q28 ? ␅
    @+111601 [111601] noise      q29 ? it
    @+111601 [111601] noise      done. it
    @+111627 [111627] nom        q26 ? ␅
    @+111627 [111627] nom        q27 ? before
    @+111704 [111704] nona       q22 ? ␅
    @+111704 [111704] nona       q23 ? before
    @+112064 [112064] nonconform q20 ? ␅
    @+112064 [112064] nonconform q21 ? before
    @+112661 [112661] nonlegumes q18 ? ␅
    @+112661 [112661] nonlegumes q19 ? before
    @+113842 [113842] nu         q16 ? ␅
    @+113842 [113842] nu         q17 ? before
    @+116323 [116323] orb        q12 ? ␅
    @+116323 [116323] orb        q13 ? before
    @+122724 [122724] parol      q8  ? ␅
    @+122724 [122724] parol      q9  ? before
    @+147311 [147311] rho        q5  ? after
    @+147311 [147311] rho        q6  ? ␅
    @+147311 [147311] rho        q7  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1550 🥳 6 ⏱️ 0:01:26.426855

📜 1 sessions
💰 score: 56

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:VILLI n n n n n remain:6812
    ⬜⬜⬜⬜⬜ tried:JESSE n n n n n remain:1562
    ⬜⬜⬜⬜⬜ tried:KNOCK n n n n n remain:341
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:144
    ⬜🟩⬜⬜⬜ tried:DUDDY n Y n n n remain:12
    ⬜🟩🟨⬜⬜ tried:QUAFF n Y m n n remain:8

    Undos used: 4

      8 words remaining
    x 7 unused letters
    = 56 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1693 😦 20 ⏱️ 0:10:13.156790

📜 4 sessions
💰 score: 4660

    6/6
    TAELS ⬜⬜⬜🟩⬜
    DOILY ⬜⬜🟨🟩🟩
    BIGLY ⬜🟩⬜🟩🟩
    HIPLY ⬜🟩⬜🟩🟩
    WILLY ⬜🟩🟩🟩🟩
    FILLY 🟩🟩🟩🟩🟩
    4/6
    FILLY ⬜🟨⬜⬜⬜
    IRADE 🟩⬜🟩⬜🟩
    IMAGE 🟩⬜🟩⬜🟩
    INANE 🟩🟩🟩🟩🟩
    5/6
    INANE ⬜⬜⬜⬜🟨
    MULCH ⬜⬜⬜⬜⬜
    RESOD 🟨🟨🟨⬜⬜
    WREST ⬜🟩🟩🟩⬜
    PRESS 🟩🟩🟩🟩🟩
    3/6
    PRESS ⬜🟨🟩⬜⬜
    THERM 🟩🟩🟩🟩⬜
    THERE 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜⬜🟩🟩🟩
    ????? ⬜⬜🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1670 🥳 score:18 ⏱️ 0:01:04.446241

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SPURN attempts:4 score:4
2. STALL attempts:5 score:5
3. NASAL attempts:3 score:3
4. POSSE attempts:6 score:6

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1670 🥳 score:57 ⏱️ 0:01:39.067270

📜 1 sessions

Octordle Classic

1. BULKY attempts:10 score:10
2. SNIFF attempts:3 score:3
3. SPIRE attempts:7 score:7
4. TALON attempts:4 score:4
5. TRULY attempts:5 score:5
6. MIGHT attempts:9 score:9
7. OWNER attempts:11 score:11
8. SUPER attempts:8 score:8

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1650 🥳 score:51 ⏱️ 0:02:29.229125

📜 1 sessions

Sedecordle Classic sedecordle.com

1. FOCAL attempts:16 score:1
2. BETEL attempts:8 score:6
3. BLESS attempts:9 score:0
4. THOSE attempts:7 score:9
5. CRAWL attempts:10 score:1
6. SLOOP attempts:3 score:0
7. BAKER attempts:13 score:1
8. CABBY attempts:11 score:3
9. SANDY attempts:17 score:1
10. VODKA attempts:12 score:8
11. IRONY attempts:5 score:0
12. MINUS attempts:17 score:5
13. DOWNY attempts:6 score:0
14. GRUEL attempts:14 score:6
15. DRONE attempts:17 score:1
16. GRUFF attempts:15 score:9

# [squareword.org](squareword.org) 🧩 #1663 🥳 9 ⏱️ 0:02:26.148355

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟩 🟨
    🟨 🟨 🟩 🟨 🟩
    🟩 🟨 🟨 🟨 🟩
    🟩 🟩 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S O B E R
    C L I M E
    A D O B E
    M I M E D
    P E E R S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1600 🥳 43 ⏱️ 0:00:38.421280

🤔 44 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 7 chat prompts
🤖 7 ornith-1.5:35b replies
🔥  2 🥵  2 😎  4 🥶 32 🧊  3

     $1 #44 wedding     100.00°C 🥳 1000‰ ~41 used:0 [40]  source:ornith
     $2 #28 bride        71.04°C 🔥  998‰  ~1 used:0 [0]   source:ornith
     $3 #25 bridal       63.95°C 🔥  997‰  ~2 used:2 [1]   source:ornith
     $4 #17 gown         37.90°C 🥵  928‰  ~3 used:3 [2]   source:ornith
     $5 #16 dress        37.04°C 🥵  919‰  ~4 used:3 [3]   source:ornith
     $6 #36 reception    29.46°C 😎  765‰  ~5 used:0 [4]   source:ornith
     $7 #27 bouquet      29.45°C 😎  764‰  ~6 used:0 [5]   source:ornith
     $8 #42 tulle        24.70°C 😎  384‰  ~7 used:0 [6]   source:ornith
     $9 #26 beaded       24.58°C 😎  365‰  ~8 used:1 [7]   source:ornith
    $10 #37 rhinestone   20.64°C 🥶       ~10 used:0 [9]   source:ornith
    $11 #13 silk         20.29°C 🥶        ~9 used:4 [8]   source:ornith
    $12 #14 satin        20.20°C 🥶       ~11 used:1 [10]  source:ornith
    $13 #29 corset       20.14°C 🥶       ~12 used:0 [11]  source:ornith
    $42 #34 line         -2.79°C 🧊       ~42 used:0 [41]  source:ornith

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1633 🥳 90 ⏱️ 0:01:31.906394

🤔 91 attempts
📜 2 sessions
🫧 6 chat sessions
⁉️ 29 chat prompts
🤖 29 ornith-1.5:35b replies
🔥  1 🥵  6 😎 17 🥶 59 🧊  7

     $1 #91 sensibilité       100.00°C 🥳 1000‰ ~84 used:0  [83]  source:ornith
     $2 #72 finesse            43.79°C 🔥  991‰  ~2 used:16 [1]   source:ornith
     $3 #88 nuance             41.33°C 🥵  984‰  ~5 used:3  [4]   source:ornith
     $4 #39 justesse           41.26°C 🥵  983‰ ~18 used:18 [17]  source:ornith
     $5 #78 esprit             41.01°C 🥵  980‰  ~3 used:2  [2]   source:ornith
     $6 #80 expression         37.68°C 🥵  951‰  ~4 used:2  [3]   source:ornith
     $7 #68 résonance          36.15°C 🥵  925‰  ~6 used:4  [5]   source:ornith
     $8 #73 délicatesse        35.07°C 🥵  906‰  ~1 used:1  [0]   source:ornith
     $9 #86 netteté            34.08°C 😎  887‰  ~7 used:0  [6]   source:ornith
    $10 #74 subtilité          33.93°C 😎  885‰  ~8 used:0  [7]   source:ornith
    $11 #90 délicat            32.49°C 😎  835‰  ~9 used:0  [8]   source:ornith
    $12 #31 équilibre          30.90°C 😎  778‰ ~24 used:8  [23]  source:ornith
    $26 #77 dextérité          24.27°C 🥶       ~27 used:0  [26]  source:ornith
    $85  #3 cascade            -0.06°C 🧊       ~85 used:0  [84]  source:ornith
