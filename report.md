# 2026-10-11

- 🔗 wordgrid 🧩 #862 🟪 rarity:0.22 ⏱️ 0:03:32.504164
- 🔗 spaceword.org 🧩 2026-10-10 🏁 score 2173 ranked 6.5% 19/294 ⏱️ 0:37:22.432334
- 🔗 alfagok.diginaut.net 🧩 #708 🥳 40 ⏱️ 0:01:31.906313
- 🔗 alphaguess.com 🧩 #1175 🥳 36 ⏱️ 0:01:17.770343
- 🔗 dontwordle.com 🧩 #1601 🤷 6 ⏱️ 0:02:14.627874
- 🔗 dictionary.com hurdle 🧩 #1744 🥳 21 ⏱️ 0:04:14.851706
- 🔗 Quordle Classic 🧩 #1721 🥳 score:20 ⏱️ 0:01:41.091323
- 🔗 Octordle Classic 🧩 #1721 🥳 score:52 ⏱️ 0:02:06.268904
- 🔗 Sedecordle Classic 🧩 #1701 🥳 score:52 ⏱️ 0:03:26.036918
- 🔗 squareword.org 🧩 #1714 🥳 8 ⏱️ 0:02:50.470539
- 🔗 cemantle.certitudes.org 🧩 #1651 🥳 469 ⏱️ 0:21:51.212003
- 🔗 cemantix.certitudes.org 🧩 #1684 🥳 633 ⏱️ 1:20:06.899693

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







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #862 🟪 rarity:0.22 ⏱️ 0:03:32.504164

📜 4 sessions
🦄 🌌 🌌
🌌 🌌 🌌
🌌 🦄 🦄
Rarity: 0.22 🟪

# [spaceword.org](spaceword.org) 🧩 2026-10-10 🏁 score 2173 ranked 6.5% 19/294 ⏱️ 0:37:22.432334

📜 6 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 19/294

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ A V O _ _ _   
      _ _ _ _ _ A _ _ _ _   
      _ _ _ _ F R Y _ _ _   
      _ _ _ _ O _ U _ _ _   
      _ _ _ _ O _ T _ _ _   
      _ _ _ _ T I Z _ _ _   
      _ _ _ _ A T E _ _ _   
      _ _ _ _ G _ S _ _ _   
      _ _ _ _ E X _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #708 🥳 40 ⏱️ 0:01:31.906313

🤔 40 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+199528 [199528] lij         q0  ? ␅
    @+199528 [199528] lij         q1  ? after
    @+299479 [299479] schrok      q2  ? ␅
    @+299479 [299479] schrok      q3  ? after
    @+349463 [349463] vakanties   q4  ? ␅
    @+349463 [349463] vakanties   q5  ? after
    @+349986 [349986] vals        q16 ? ␅
    @+349986 [349986] vals        q17 ? after
    @+350124 [350124] van         q18 ? ␅
    @+350124 [350124] van         q19 ? after
    @+350133 [350133] vancomycine q32 ? ␅
    @+350133 [350133] vancomycine q33 ? after
    @+350135 [350135] vandaag     q38 ? ␅
    @+350135 [350135] vandaag     q39 ? it
    @+350135 [350135] vandaag     done. it
    @+350136 [350136] vandaal     q34 ? ␅
    @+350136 [350136] vandaal     q35 ? before
    @+350146 [350146] vandalisme  q30 ? ␅
    @+350146 [350146] vandalisme  q31 ? before
    @+350179 [350179] vandoen     q28 ? ␅
    @+350179 [350179] vandoen     q29 ? before
    @+350232 [350232] vangst      q22 ? ␅
    @+350232 [350232] vangst      q23 ? before
    @+350348 [350348] varia       q20 ? ␅
    @+350348 [350348] varia       q21 ? before
    @+350580 [350580] vast        q14 ? ␅
    @+350580 [350580] vast        q15 ? before
    @+352228 [352228] vel         q12 ? ␅
    @+352228 [352228] vel         q13 ? before
    @+355664 [355664] verhaal     q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1175 🥳 36 ⏱️ 0:01:17.770343

🤔 36 attempts
📜 1 sessions

    @        [     0] aa           
    @+98142  [ 98142] mac          q0  ? ␅
    @+98142  [ 98142] mac          q1  ? after
    @+110110 [110110] need         q6  ? ␅
    @+110110 [110110] need         q7  ? after
    @+111474 [111474] no           q10 ? ␅
    @+111474 [111474] no           q11 ? after
    @+112524 [112524] noni         q14 ? ␅
    @+112524 [112524] noni         q15 ? after
    @+113142 [113142] nonsocial    q16 ? ␅
    @+113142 [113142] nonsocial    q17 ? after
    @+113451 [113451] norm         q18 ? ␅
    @+113451 [113451] norm         q19 ? after
    @+113463 [113463] normalizable q26 ? ␅
    @+113463 [113463] normalizable q27 ? after
    @+113466 [113466] normalize    q28 ? ␅
    @+113466 [113466] normalize    q29 ? after
    @+113471 [113471] normalizing  q30 ? ␅
    @+113471 [113471] normalizing  q31 ? after
    @+113472 [113472] normally     q34 ? ␅
    @+113472 [113472] normally     q35 ? it
    @+113472 [113472] normally     done. it
    @+113473 [113473] normals      q32 ? ␅
    @+113473 [113473] normals      q33 ? before
    @+113475 [113475] normative    q24 ? ␅
    @+113475 [113475] normative    q25 ? before
    @+113497 [113497] north        q22 ? ␅
    @+113497 [113497] north        q23 ? before
    @+113542 [113542] nos          q20 ? ␅
    @+113542 [113542] nos          q21 ? before
    @+113766 [113766] novel        q13 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1601 🤷 6 ⏱️ 0:02:14.627874

📜 1 sessions
💰 score: 0

ELIMINATED
> Well technically I didn't Wordle!

    ⬜⬜⬜⬜⬜ tried:EBBET n n n n n remain:4685
    ⬜⬜⬜⬜⬜ tried:ZANZA n n n n n remain:1624
    ⬜⬜⬜⬜⬜ tried:WOOFS n n n n n remain:240
    ⬜⬜⬜⬜⬜ tried:DURUM n n n n n remain:42
    🟨⬜🟩⬜⬜ tried:CHICK m n Y n n remain:1
    ⬛⬛⬛⬛⬛ tried:????? remain:0

    Undos used: 5

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1744 🥳 21 ⏱️ 0:04:14.851706

📜 1 sessions
💰 score: 9500

    5/6
    PRASE ⬜⬜⬜🟨⬜
    SOLID 🟨⬜⬜⬜⬜
    TUSKY ⬜🟩🟩🟩🟩
    HUSKY ⬜🟩🟩🟩🟩
    MUSKY 🟩🟩🟩🟩🟩
    5/6
    MUSKY ⬜⬜⬜⬜⬜
    NORIA 🟨⬜🟨🟨⬜
    REIGN 🟨🟨🟨⬜🟨
    FINER ⬜🟨🟩🟩🟩
    INNER 🟩🟩🟩🟩🟩
    6/6
    INNER ⬜⬜⬜⬜⬜
    BLOAT ⬜⬜⬜⬜🟨
    UMPTY 🟨⬜⬜🟩🟩
    FACED ⬜⬜⬜⬜⬜
    GOJIS 🟩⬜⬜⬜🟨
    GUSTY 🟩🟩🟩🟩🟩
    4/6
    GUSTY ⬜⬜⬜⬜⬜
    DRAIL ⬜🟨🟩⬜🟨
    REALM 🟨🟨🟩🟨⬜
    BLARE 🟩🟩🟩🟩🟩
    Final 1/2
    KLUTZ 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1721 🥳 score:20 ⏱️ 0:01:41.091323

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. LILAC attempts:3 score:3
2. INLET attempts:4 score:4
3. TRIAD attempts:5 score:5
4. SHAPE attempts:8 score:8

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1721 🥳 score:52 ⏱️ 0:02:06.268904

📜 1 sessions

Octordle Classic

1. TALON attempts:8 score:8
2. REPLY attempts:3 score:3
3. TEPID attempts:4 score:4
4. TONGA attempts:7 score:7
5. POSIT attempts:5 score:5
6. GIVER attempts:9 score:9
7. BUILT attempts:10 score:10
8. ODDLY attempts:6 score:6

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1701 🥳 score:52 ⏱️ 0:03:26.036918

📜 1 sessions

Sedecordle Classic sedecordle.com

1. TAKER attempts:17 score:1
2. RERUN attempts:16 score:7
3. GLINT attempts:15 score:1
4. ZONAL attempts:14 score:5
5. WILLY attempts:18 score:1
6. GEESE attempts:13 score:8
7. SHONE attempts:12 score:1
8. RIPEN attempts:6 score:2
9. LIMIT attempts:11 score:1
10. MOSSY attempts:10 score:1
11. UNCLE attempts:8 score:0
12. RESIN attempts:5 score:8
13. STEEP attempts:7 score:0
14. REPLY attempts:4 score:7
15. THUMB attempts:9 score:0
16. DEIGN attempts:3 score:9

# [squareword.org](squareword.org) 🧩 #1714 🥳 8 ⏱️ 0:02:50.470539

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟩 🟩 🟨 🟩 🟩
    🟩 🟨 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P L A N T
    A U G U R
    S P I K Y
    T I N E S
    A N G S T

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1651 🥳 469 ⏱️ 0:21:51.212003

🤔 470 attempts
📜 1 sessions
🫧 25 chat sessions
⁉️ 144 chat prompts
🤖 144 dolphin3:latest replies
🔥   1 🥵   5 😎  32 🥶 409 🧊  22

      $1 #470 hell               100.00°C 🥳 1000‰ ~448 used:0  [447]  source:dolphin3
      $2 #433 heaven              55.09°C 🔥  996‰   ~2 used:16 [1]    source:dolphin3
      $3 #434 hellfire            47.76°C 🥵  969‰   ~5 used:6  [4]    source:dolphin3
      $4 #416 purgatory           45.71°C 🥵  956‰   ~6 used:9  [5]    source:dolphin3
      $5 #435 infernal            42.67°C 🥵  926‰   ~3 used:2  [2]    source:dolphin3
      $6 #438 god                 41.86°C 🥵  915‰   ~4 used:2  [3]    source:dolphin3
      $7 #451 eternity            41.36°C 🥵  904‰   ~1 used:1  [0]    source:dolphin3
      $8 #439 paradise            40.82°C 😎  896‰   ~7 used:0  [6]    source:dolphin3
      $9 #428 perdition           39.28°C 😎  858‰   ~8 used:0  [7]    source:dolphin3
     $10 #419 damnation           38.81°C 😎  834‰  ~26 used:3  [25]   source:dolphin3
     $11 #394 nightmare           38.65°C 😎  827‰  ~28 used:11 [27]   source:dolphin3
     $12 #405 torment             38.13°C 😎  812‰  ~25 used:2  [24]   source:dolphin3
     $40 #318 unreal              29.38°C 🥶        ~54 used:0  [53]   source:dolphin3
    $449 #336 function            -0.22°C 🧊       ~449 used:0  [448]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1684 🥳 633 ⏱️ 1:20:06.899693

🤔 634 attempts
📜 1 sessions
🫧 53 chat sessions
⁉️ 280 chat prompts
🤖 113 dolphin3:latest replies
🤖 64 llama3.2:latest replies
🤖 103 gemma4:12b replies
😱   1 🔥   5 🥵  44 😎 175 🥶 356 🧊  52

      $1 #634 pertinent        100.00°C 🥳 1000‰ ~582 used:0   [581]  source:dolphin3
      $2 #469 pertinence        69.06°C 😱  999‰   ~1 used:85  [0]    source:llama3.2
      $3 #503 utile             58.56°C 🔥  997‰  ~13 used:25  [12]   source:llama3.2
      $4 #520 intéressant       56.78°C 🔥  995‰   ~8 used:15  [7]    source:llama3.2
      $5 #123 analyser          56.51°C 🔥  994‰ ~220 used:191 [219]  source:dolphin3
      $6 #416 argumenter        54.30°C 🔥  991‰  ~14 used:25  [13]   source:gemma4  
      $7  #83 analyse           53.97°C 🔥  990‰ ~219 used:120 [218]  source:dolphin3
      $8 #142 expliciter        52.69°C 🥵  986‰ ~221 used:40  [220]  source:dolphin3
      $9 #234 structurer        52.28°C 🥵  984‰  ~37 used:8   [36]   source:gemma4  
     $10 #267 hiérarchiser      52.23°C 🥵  983‰  ~38 used:8   [37]   source:gemma4  
     $11 #145 identifier        52.20°C 🥵  982‰  ~39 used:8   [38]   source:dolphin3
     $52 #447 hypothèse         42.49°C 😎  895‰  ~48 used:0   [47]   source:llama3.2
    $227 #418 discuter          27.48°C 🥶       ~226 used:0   [225]  source:gemma4  
    $583 #446 fidèle            -0.09°C 🧊       ~583 used:0   [582]  source:llama3.2
