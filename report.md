# 2026-08-13

- 🔗 spaceword.org 🧩 2026-08-12 🏁 score 2168 ranked 29.9% 97/324 ⏱️ 0:38:10.144433
- 🔗 wordgrid 🧩 #803 🟪 rarity:0.13 ⏱️ 0:06:04.488957
- 🔗 alfagok.diginaut.net 🧩 #649 🥳 34 ⏱️ 0:00:37.280831
- 🔗 alphaguess.com 🧩 #1116 🥳 34 ⏱️ 0:00:35.212964
- 🔗 cemantix.certitudes.org 🧩 #1625 🥳 138 ⏱️ 0:05:07.229208
- 🔗 dontwordle.com 🧩 #1542 🥳 6 ⏱️ 0:01:17.028078
- 🔗 dictionary.com hurdle 🧩 #1685 🥳 19 ⏱️ 0:04:30.334903
- 🔗 Quordle Classic 🧩 #1662 🥳 score:18 ⏱️ 0:01:06.117978
- 🔗 Octordle Classic 🧩 #1662 🥳 score:52 ⏱️ 0:01:42.115398
- 🔗 Sedecordle Classic 🧩 #1642 🥳 score:48 ⏱️ 0:02:35.929127
- 🔗 squareword.org 🧩 #1655 🥳 8 ⏱️ 0:02:06.339055
- 🔗 cemantle.certitudes.org 🧩 #1592 🥳 178 ⏱️ 0:01:45.802134

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









# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #803 🟪 rarity:0.13 ⏱️ 0:06:04.488957

📜 2 sessions
🦄 🦄 🌌
🦄 🦄 🌌
🦄 🦄 🦄
Rarity: 0.13 🟪

# [spaceword.org](spaceword.org) 🧩 2026-08-12 🏁 score 2168 ranked 29.9% 97/324 ⏱️ 0:38:10.144433

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 97/324

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ J _ P O _ M _ R _   
      _ U _ I O N I Z E _   
      _ R U E F U L _ D _   
      _ A _ _ _ _ K _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #649 🥳 34 ⏱️ 0:00:37.280831

🤔 34 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+199548 [199548] lij       q0  ? ␅
    @+199548 [199548] lij       q1  ? after
    @+199548 [199548] lij       q2  ? ␅
    @+199548 [199548] lij       q3  ? after
    @+199548 [199548] lij       q4  ? ␅
    @+199548 [199548] lij       q5  ? after
    @+299514 [299514] schrok    q6  ? ␅
    @+299514 [299514] schrok    q7  ? after
    @+349501 [349501] vakanties q8  ? ␅
    @+349501 [349501] vakanties q9  ? after
    @+374496 [374496] vrijst    q10 ? ␅
    @+374496 [374496] vrijst    q11 ? after
    @+386880 [386880] winkel    q12 ? ␅
    @+386880 [386880] winkel    q13 ? after
    @+392881 [392881] zelf      q14 ? ␅
    @+392881 [392881] zelf      q15 ? after
    @+396185 [396185] zonde     q16 ? ␅
    @+396185 [396185] zonde     q17 ? after
    @+396983 [396983] zout      q22 ? ␅
    @+396983 [396983] zout      q23 ? after
    @+397167 [397167] zuid      q24 ? ␅
    @+397167 [397167] zuid      q25 ? after
    @+397457 [397457] zuig      q26 ? ␅
    @+397457 [397457] zuig      q27 ? after
    @+397599 [397599] zuivel    q28 ? ␅
    @+397599 [397599] zuivel    q29 ? after
    @+397697 [397697] zul       q30 ? ␅
    @+397697 [397697] zul       q31 ? after
    @+397747 [397747] zuster    q33 ? it
    @+397747 [397747] zuster    done. it

# [alphaguess.com](alphaguess.com) 🧩 #1116 🥳 34 ⏱️ 0:00:35.212964

🤔 34 attempts
📜 1 sessions

    @        [     0] aa          
    @+98147  [ 98147] mac         q0  ? ␅
    @+98147  [ 98147] mac         q1  ? after
    @+104011 [104011] minis       q8  ? ␅
    @+104011 [104011] minis       q9  ? after
    @+106934 [106934] mora        q10 ? ␅
    @+106934 [106934] mora        q11 ? after
    @+107078 [107078] morpho      q18 ? ␅
    @+107078 [107078] morpho      q19 ? after
    @+107116 [107116] mort        q20 ? ␅
    @+107116 [107116] mort        q21 ? after
    @+107179 [107179] mos         q22 ? ␅
    @+107179 [107179] mos         q23 ? after
    @+107207 [107207] mosh        q24 ? ␅
    @+107207 [107207] mosh        q25 ? after
    @+107224 [107224] moss        q26 ? ␅
    @+107224 [107224] moss        q27 ? after
    @+107236 [107236] mossinesses q28 ? ␅
    @+107236 [107236] mossinesses q29 ? after
    @+107236 [107236] mossinesses q30 ? ␅
    @+107236 [107236] mossinesses q31 ? after
    @+107241 [107241] most        q32 ? ␅
    @+107241 [107241] most        q33 ? it
    @+107241 [107241] most        done. it
    @+107247 [107247] mot         q16 ? ␅
    @+107247 [107247] mot         q17 ? before
    @+107674 [107674] mu          q14 ? ␅
    @+107674 [107674] mu          q15 ? before
    @+108413 [108413] mun         q12 ? ␅
    @+108413 [108413] mun         q13 ? before
    @+109929 [109929] ne          q7  ? before

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1625 🥳 138 ⏱️ 0:05:07.229208

🤔 139 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 42 chat prompts
🤖 42 dolphin3:latest replies
🔥  1 🥵  3 😎 21 🥶 94 🧊 19

      $1 #139 bar          100.00°C 🥳 1000‰ ~120 used:0  [119]  source:dolphin3
      $2   #2 café          58.38°C 🔥  998‰   ~4 used:67 [3]    source:dolphin3
      $3 #109 barman        50.67°C 🥵  985‰   ~1 used:2  [0]    source:dolphin3
      $4 #107 cocktail      45.26°C 🥵  967‰   ~3 used:5  [2]    source:dolphin3
      $5 #103 soir          36.54°C 🥵  901‰   ~2 used:3  [1]    source:dolphin3
      $6 #116 limonade      36.19°C 😎  895‰   ~5 used:0  [4]    source:dolphin3
      $7 #125 whisky        34.39°C 😎  863‰   ~6 used:0  [5]    source:dolphin3
      $8 #133 dîner         32.46°C 😎  814‰   ~7 used:0  [6]    source:dolphin3
      $9  #11 cappuccino    32.23°C 😎  807‰  ~25 used:20 [24]   source:dolphin3
     $10 #126 bouteille     31.15°C 😎  768‰   ~8 used:0  [7]    source:dolphin3
     $11 #117 martini       31.03°C 😎  763‰   ~9 used:0  [8]    source:dolphin3
     $12  #52 thé           30.80°C 😎  756‰  ~24 used:7  [23]   source:dolphin3
     $27 #134 fête          22.58°C 🥶        ~26 used:0  [25]   source:dolphin3
    $121  #96 cacao         -0.05°C 🧊       ~121 used:0  [120]  source:dolphin3

# [dontwordle.com](dontwordle.com) 🧩 #1542 🥳 6 ⏱️ 0:01:17.028078

📜 1 sessions
💰 score: 9

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:BACCA n n n n n remain:5655
    ⬜⬜⬜⬜⬜ tried:ZIZIT n n n n n remain:2662
    ⬜⬜⬜⬜⬜ tried:DUDDY n n n n n remain:1025
    ⬜⬜⬜⬜🟨 tried:GRRRL n n n n m remain:176
    ⬜🟨🟩⬜⬜ tried:FLOPS n m Y n n remain:3
    ⬜⬜🟩🟩⬜ tried:OVOLO n n Y Y n remain:1

    Undos used: 2

      1 words remaining
    x 9 unused letters
    = 9 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1685 🥳 19 ⏱️ 0:04:30.334903

📜 1 sessions
💰 score: 9700

    4/6
    SNAKE ⬜⬜⬜⬜⬜
    DIRTY ⬜🟨⬜⬜⬜
    CHOIL ⬜⬜🟨🟩🟨
    FOLIO 🟩🟩🟩🟩🟩
    3/6
    FOLIO 🟨⬜⬜⬜⬜
    AFTER 🟨🟨⬜🟨⬜
    CHAFE 🟩🟩🟩🟩🟩
    6/6
    CHAFE ⬜⬜🟨⬜🟨
    RESAT 🟨🟨⬜🟨⬜
    PAGER 🟩🟩⬜🟩🟩
    PROWL 🟩🟨⬜⬜⬜
    VAMPY ⬜🟩⬜🟨🟨
    PAYER 🟩🟩🟩🟩🟩
    5/6
    PAYER ⬜⬜⬜⬜🟨
    NITRO ⬜⬜🟨🟨🟨
    TORUS 🟨🟩🟩⬜⬜
    FORTH ⬜🟩🟩🟩🟩
    WORTH 🟩🟩🟩🟩🟩
    Final 1/2
    GHOUL 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1662 🥳 score:18 ⏱️ 0:01:06.117978

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. TOPAZ attempts:5 score:5
2. PURGE attempts:3 score:3
3. WHINE attempts:6 score:6
4. SIGHT attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1662 🥳 score:52 ⏱️ 0:01:42.115398

📜 1 sessions

Octordle Classic

1. LOAMY attempts:3 score:3
2. EBONY attempts:4 score:4
3. HUMPH attempts:6 score:6
4. SCOFF attempts:8 score:8
5. CHAMP attempts:5 score:5
6. ATTIC attempts:7 score:7
7. STAFF attempts:9 score:10
8. MICRO attempts:9 score:9

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1642 🥳 score:48 ⏱️ 0:02:35.929127

📜 1 sessions

Sedecordle Classic sedecordle.com

1. FLANK attempts:11 score:1
2. SNARL attempts:3 score:1
3. MERCY attempts:5 score:0
4. WRING attempts:14 score:5
5. CLASS attempts:18 score:1
6. AXIOM attempts:9 score:9
7. CHINA attempts:6 score:0
8. DEUCE attempts:7 score:6
9. OPIUM attempts:8 score:0
10. FIRST attempts:10 score:8
11. INEPT attempts:12 score:1
12. WHOOP attempts:13 score:2
13. AMUSE attempts:15 score:1
14. KNEAD attempts:16 score:5
15. DUSKY attempts:17 score:1
16. BURNT attempts:18 score:7

# [squareword.org](squareword.org) 🧩 #1655 🥳 8 ⏱️ 0:02:06.339055

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩 🟨 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C O F F
    H A L L O
    A D D E R
    G R E E T
    S E N S E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1592 🥳 178 ⏱️ 0:01:45.802134

🤔 179 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 30 chat prompts
🤖 30 dolphin3:latest replies
🔥   1 🥵   5 😎  14 🥶 154 🧊   4

      $1 #179 diabetes         100.00°C 🥳 1000‰ ~175 used:0 [174]  source:dolphin3
      $2 #175 arthritis         58.90°C 🔥  990‰   ~1 used:0 [0]    source:dolphin3
      $3 #174 disease           57.77°C 🥵  988‰   ~2 used:2 [1]    source:dolphin3
      $4 #163 hypothyroidism    51.80°C 🥵  968‰   ~6 used:3 [5]    source:dolphin3
      $5 #159 autoimmune        48.78°C 🥵  954‰   ~3 used:2 [2]    source:dolphin3
      $6 #162 hyperthyroidism   45.07°C 🥵  917‰   ~4 used:2 [3]    source:dolphin3
      $7 #158 thyroid           43.97°C 🥵  902‰   ~5 used:2 [4]    source:dolphin3
      $8 #155 metabolic         42.63°C 😎  875‰   ~7 used:1 [6]    source:dolphin3
      $9 #170 thyrotoxicosis    42.20°C 😎  860‰   ~8 used:0 [7]    source:dolphin3
     $10 #134 dietary           41.68°C 😎  843‰  ~14 used:2 [13]   source:dolphin3
     $11  #75 health            41.18°C 😎  828‰  ~20 used:8 [19]   source:dolphin3
     $12  #78 diet              41.09°C 😎  825‰  ~19 used:5 [18]   source:dolphin3
     $22  #85 healthy           29.29°C 🥶        ~28 used:1 [27]   source:dolphin3
    $176 #100 clean             -0.25°C 🧊       ~176 used:0 [175]  source:dolphin3
