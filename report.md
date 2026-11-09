# 2026-11-11

- 🔗 alfagok.diginaut.net 🧩 #739 🥳 36 ⏱️ 0:00:51.177243
- 🔗 alphaguess.com 🧩 #1206 🥳 38 ⏱️ 0:00:37.971292
- 🔗 dontwordle.com 🧩 #1632 🥳 6 ⏱️ 0:02:10.200144
- 🔗 dictionary.com hurdle 🧩 #1775 😦 15 ⏱️ 0:03:47.716208
- 🔗 Quordle Classic 🧩 #1752 🥳 score:19 ⏱️ 0:01:19.461137
- 🔗 Octordle Classic 🧩 #1752 🥳 score:55 ⏱️ 0:02:15.333198
- 🔗 Sedecordle Classic 🧩 #1732 🥳 score:36 ⏱️ 0:02:33.008253
- 🔗 squareword.org 🧩 #1745 🥳 7 ⏱️ 0:01:38.482403
- 🔗 cemantle.certitudes.org 🧩 #1682 🥳 104 ⏱️ 0:05:07.898032
- 🔗 cemantix.certitudes.org 🧩 #1715 🥳 91 ⏱️ 0:10:30.144069

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










# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #892 🟪 rarity:0.32 ⏱️ 0:03:10.891631

📜 2 sessions
🌌 🦄 🦄
🌌 🌌 🌌
🦄 🌌 🌌
Rarity: 0.32 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-09 🏁 score 2168 ranked 49.8% 148/297 ⏱️ 0:22:41.164996

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 148/297

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ G _ _ _ _ K _ L _   
      _ O _ C A S A V A _   
      _ A _ A _ _ S I G _   
      _ D A W E N _ A _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #739 🥳 36 ⏱️ 0:00:51.177243

🤔 36 attempts
📜 1 sessions

    @        [     0] &-teken       
    @+99672  [ 99672] ex            q2  ? ␅
    @+99672  [ 99672] ex            q3  ? after
    @+149358 [149358] huis          q4  ? ␅
    @+149358 [149358] huis          q5  ? after
    @+174465 [174465] kind          q6  ? ␅
    @+174465 [174465] kind          q7  ? after
    @+177544 [177544] kleur         q14 ? ␅
    @+177544 [177544] kleur         q15 ? after
    @+178168 [178168] klimaat       q20 ? ␅
    @+178168 [178168] klimaat       q21 ? after
    @+178283 [178283] klimaatregime q26 ? ␅
    @+178283 [178283] klimaatregime q27 ? after
    @+178341 [178341] klimatoloog   q28 ? ␅
    @+178341 [178341] klimatoloog   q29 ? after
    @+178370 [178370] klimmast      q30 ? ␅
    @+178370 [178370] klimmast      q31 ? after
    @+178375 [178375] klimmen       q34 ? ␅
    @+178375 [178375] klimmen       q35 ? it
    @+178375 [178375] klimmen       done. it
    @+178384 [178384] klimmuur      q32 ? ␅
    @+178384 [178384] klimmuur      q33 ? before
    @+178398 [178398] klimparcours  q24 ? ␅
    @+178398 [178398] klimparcours  q25 ? before
    @+178628 [178628] klok          q22 ? ␅
    @+178628 [178628] klok          q23 ? before
    @+179100 [179100] kluis         q18 ? ␅
    @+179100 [179100] kluis         q19 ? before
    @+180656 [180656] koel          q12 ? ␅
    @+180656 [180656] koel          q13 ? before
    @+187044 [187044] kronen        q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1206 🥳 38 ⏱️ 0:00:37.971292

🤔 38 attempts
📜 1 sessions

    @       [    0] aa         
    @+24517 [24517] car        q8  ? ␅
    @+24517 [24517] car        q9  ? after
    @+36722 [36722] cos        q10 ? ␅
    @+36722 [36722] cos        q11 ? after
    @+38246 [38246] creativity q16 ? ␅
    @+38246 [38246] creativity q17 ? after
    @+38434 [38434] crepuscule q24 ? ␅
    @+38434 [38434] crepuscule q25 ? after
    @+38516 [38516] crib       q26 ? ␅
    @+38516 [38516] crib       q27 ? after
    @+38532 [38532] crick      q30 ? ␅
    @+38532 [38532] crick      q31 ? after
    @+38543 [38543] cricoid    q32 ? ␅
    @+38543 [38543] cricoid    q33 ? after
    @+38548 [38548] cries      q34 ? ␅
    @+38548 [38548] cries      q35 ? after
    @+38550 [38550] crime      q36 ? ␅
    @+38550 [38550] crime      q37 ? it
    @+38550 [38550] crime      done. it
    @+38553 [38553] criminal   q28 ? ␅
    @+38553 [38553] criminal   q29 ? before
    @+38622 [38622] crinite    q22 ? ␅
    @+38622 [38622] crinite    q23 ? before
    @+38996 [38996] crow       q18 ? ␅
    @+38996 [38996] crow       q19 ? before
    @+39768 [39768] cup        q14 ? ␅
    @+39768 [39768] cup        q15 ? before
    @+42889 [42889] defi       q12 ? ␅
    @+42889 [42889] defi       q13 ? before
    @+49065 [49065] disturb    q7  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1632 🥳 6 ⏱️ 0:02:10.200144

📜 2 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:FEEZE n n n n n remain:6482
    ⬜⬜⬜⬜⬜ tried:TITIS n n n n n remain:1531
    ⬜⬜⬜⬜⬜ tried:DULLY n n n n n remain:360
    ⬜⬜🟨⬜⬜ tried:KNOWN n n m n n remain:73
    🟩⬜⬜⬜🟩 tried:MORRO Y n n n Y remain:2
    🟩🟩⬜⬜🟩 tried:MAMBO Y Y n n Y remain:1

    Undos used: 4

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1775 😦 15 ⏱️ 0:03:47.716208

📜 1 sessions
💰 score: 5160

    4/6
    STARE ⬜⬜⬜🟨⬜
    IRONY ⬜🟩⬜⬜⬜
    BLACK ⬜⬜⬜⬜⬜
    GRUMP 🟩🟩🟩🟩🟩
    3/6
    GRUMP ⬜🟨⬜⬜⬜
    RAKES 🟨⬜🟨🟨⬜
    JERKY 🟩🟩🟩🟩🟩
    3/6
    JERKY ⬜⬜⬜⬜⬜
    NAILS 🟨⬜⬜🟨⬜
    CLUNG 🟩🟩🟩🟩🟩
    3/6
    CLUNG ⬜⬜⬜🟨⬜
    ARSON ⬜🟩⬜🟨🟩
    BROWN 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜🟨🟨⬜🟨
    ????? 🟨⬜🟨🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1752 🥳 score:19 ⏱️ 0:01:19.461137

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. OVERT attempts:2 score:2
2. SOLAR attempts:7 score:7
3. REVEL attempts:6 score:6
4. BRAVO attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1752 🥳 score:55 ⏱️ 0:02:15.333198

📜 1 sessions

Octordle Classic

1. CANOE attempts:3 score:3
2. DIZZY attempts:7 score:7
3. SAPPY attempts:4 score:4
4. BROOM attempts:10 score:10
5. LEVEL attempts:12 score:12
6. DEITY attempts:6 score:6
7. PARRY attempts:8 score:8
8. NADIR attempts:5 score:5

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1732 🥳 score:36 ⏱️ 0:02:33.008253

📜 1 sessions

Sedecordle Classic sedecordle.com

1. LASSO attempts:5 score:0
2. FERRY attempts:17 score:5
3. GAMMA attempts:13 score:1
4. BEFIT attempts:7 score:3
5. PAYER attempts:15 score:1
6. SILLY attempts:12 score:5
7. AWFUL attempts:8 score:0
8. BOSOM attempts:6 score:8
9. BUDGE attempts:16 score:1
10. SHIRE attempts:4 score:6
11. YIELD attempts:10 score:1
12. UNDER attempts:14 score:0
13. RIGHT attempts:3 score:0
14. MADLY attempts:17 score:3
15. VAUNT attempts:11 score:1
16. NAVEL attempts:9 score:1

# [squareword.org](squareword.org) 🧩 #1745 🥳 7 ⏱️ 0:01:38.482403

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟩 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    D E M O S
    E L E C T
    P I N T O
    O D D E R
    T E S T Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1682 🥳 104 ⏱️ 0:05:07.898032

🤔 105 attempts
📜 2 sessions
🫧 2 chat sessions
⁉️ 28 chat prompts
🤖 28 MichelRosselli/apertus-v1.1:latest replies
🔥  2 🥵  3 😎 18 🥶 78 🧊  3

      $1 #105 laser          100.00°C 🥳 1000‰ ~102 used:0 [101]  source:MichelRosselli
      $2  #89 optic           50.59°C 🔥  994‰   ~1 used:3 [0]    source:MichelRosselli
      $3  #76 optical         50.53°C 🔥  993‰   ~2 used:4 [1]    source:MichelRosselli
      $4  #93 optics          48.22°C 🥵  989‰   ~3 used:1 [2]    source:MichelRosselli
      $5  #80 refractive      44.51°C 🥵  962‰   ~5 used:5 [4]    source:MichelRosselli
      $6 #102 beam            43.20°C 🥵  950‰   ~4 used:0 [3]    source:MichelRosselli
      $7  #68 robotic         40.23°C 😎  885‰   ~6 used:1 [5]    source:MichelRosselli
      $8  #84 bifocal         38.94°C 😎  854‰   ~7 used:0 [6]    source:MichelRosselli
      $9  #79 refraction      37.86°C 😎  829‰   ~8 used:0 [7]    source:MichelRosselli
     $10  #72 lens            37.20°C 😎  807‰   ~9 used:1 [8]    source:MichelRosselli
     $11  #20 device          35.41°C 😎  738‰  ~23 used:4 [22]   source:MichelRosselli
     $12  #78 light           35.17°C 😎  721‰  ~10 used:0 [9]    source:MichelRosselli
     $25  #70 equipment       27.69°C 🥶        ~24 used:0 [23]   source:MichelRosselli
    $103  #67 programming     -0.02°C 🧊       ~103 used:0 [102]  source:MichelRosselli

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1715 🥳 91 ⏱️ 0:10:30.144069

🤔 92 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 44 chat prompts
🤖 44 MichelRosselli/apertus-v1.1:latest replies
😱  1 🥵  2 😎  7 🥶 66 🧊 15

     $1 #92 béton           100.00°C 🥳 1000‰ ~77 used:0  [76]  source:MichelRosselli
     $2 #90 ciment           62.10°C 😱  999‰  ~1 used:0  [0]   source:MichelRosselli
     $3 #87 bitume           43.86°C 🥵  956‰  ~5 used:13 [4]   source:MichelRosselli
     $4 #83 bitumineux       42.67°C 🥵  942‰  ~4 used:12 [3]   source:MichelRosselli
     $5 #89 asphalte         37.01°C 😎  874‰  ~2 used:0  [1]   source:MichelRosselli
     $6 #82 construction     36.76°C 😎  868‰  ~6 used:3  [5]   source:MichelRosselli
     $7 #47 sable            31.52°C 😎  682‰ ~10 used:17 [9]   source:MichelRosselli
     $8 #85 chaux            30.98°C 😎  656‰  ~3 used:0  [2]   source:MichelRosselli
     $9 #35 auvent           28.70°C 😎  501‰  ~9 used:15 [8]   source:MichelRosselli
    $10 #28 barrage          26.68°C 😎  323‰  ~8 used:14 [7]   source:MichelRosselli
    $11 #66 routier          25.34°C 😎  169‰  ~7 used:9  [6]   source:MichelRosselli
    $12 #81 hydraulique      23.74°C 🥶       ~16 used:0  [15]  source:MichelRosselli
    $13 #55 sableux          22.06°C 🥶       ~17 used:0  [16]  source:MichelRosselli
    $78  #2 lion             -0.24°C 🧊       ~78 used:0  [77]  source:MichelRosselli
