# 2026-06-30

- 🔗 spaceword.org 🧩 2026-06-29 🏁 score 2165 ranked 49.5% 150/303 ⏱️ 0:12:28.411001
- 🔗 alfagok.diginaut.net 🧩 #605 🥳 50 ⏱️ 0:00:54.268973
- 🔗 alphaguess.com 🧩 #1072 🥳 34 ⏱️ 0:00:49.688900
- 🔗 dontwordle.com 🧩 #1498 🥳 6 ⏱️ 0:01:48.106909
- 🔗 dictionary.com hurdle 🧩 #1641 🥳 17 ⏱️ 0:03:05.932734
- 🔗 Quordle Classic 🧩 #1618 🥳 score:22 ⏱️ 0:02:02.239110
- 🔗 Octordle Classic 🧩 #1618 🥳 score:49 ⏱️ 0:03:14.725481
- 🔗 Sedecordle Classic 🧩 #1598 🥳 score:47 ⏱️ 0:09:54.857467
- 🔗 squareword.org 🧩 #1611 🥳 7 ⏱️ 0:01:35.423577
- 🔗 cemantle.certitudes.org 🧩 #1548 🥳 312 ⏱️ 0:04:35.113370
- 🔗 cemantix.certitudes.org 🧩 #1581 🥳 727 ⏱️ 0:18:35.964119

# Dev

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





















# [spaceword.org](spaceword.org) 🧩 2026-06-29 🏁 score 2165 ranked 49.5% 150/303 ⏱️ 0:12:28.411001

📜 2 sessions
- tiles: 21/21
- score: 2165 bonus: +65
- rank: 150/303

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ J _ _ O _ _ _   
      _ _ _ U _ _ V _ _ _   
      _ _ _ N I T O N _ _   
      _ _ _ K _ _ L O _ _   
      _ _ _ I _ _ I _ _ _   
      _ _ _ E F _ _ _ _ _   
      _ _ _ S E P O Y _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #605 🥳 50 ⏱️ 0:00:54.268973

🤔 50 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+199556 [199556] lij        q0  ? ␅
    @+199556 [199556] lij        q1  ? after
    @+199556 [199556] lij        q2  ? ␅
    @+199556 [199556] lij        q3  ? after
    @+223552 [223552] molen      q8  ? ␅
    @+223552 [223552] molen      q9  ? after
    @+223699 [223699] molk       q22 ? ␅
    @+223699 [223699] molk       q23 ? after
    @+223776 [223776] mom        q36 ? ␅
    @+223776 [223776] mom        q37 ? after
    @+223810 [223810] mommerijen q38 ? ␅
    @+223810 [223810] mommerijen q39 ? after
    @+223814 [223814] mompel     q44 ? ␅
    @+223814 [223814] mompel     q45 ? after
    @+223817 [223817] mompelen   q48 ? ␅
    @+223817 [223817] mompelen   q49 ? it
    @+223817 [223817] mompelen   done. it
    @+223821 [223821] monachaal  q46 ? ␅
    @+223821 [223821] monachaal  q47 ? before
    @+223827 [223827] monarch    q42 ? ␅
    @+223827 [223827] monarch    q43 ? before
    @+223843 [223843] mond       q20 ? ␅
    @+223843 [223843] mond       q21 ? before
    @+224241 [224241] monster    q18 ? ␅
    @+224241 [224241] monster    q19 ? before
    @+225032 [225032] mos        q16 ? ␅
    @+225032 [225032] mos        q17 ? before
    @+226530 [226530] mus        q14 ? ␅
    @+226530 [226530] mus        q15 ? before
    @+229521 [229521] natuur     q13 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1072 🥳 34 ⏱️ 0:00:49.688900

🤔 34 attempts
📜 1 sessions

    @       [    0] aa            
    @+47380 [47380] dis           q2  ? ␅
    @+47380 [47380] dis           q3  ? after
    @+53396 [53396] el            q8  ? ␅
    @+53396 [53396] el            q9  ? after
    @+56739 [56739] equate        q10 ? ␅
    @+56739 [56739] equate        q11 ? after
    @+58355 [58355] ex            q12 ? ␅
    @+58355 [58355] ex            q13 ? after
    @+58780 [58780] exempt        q16 ? ␅
    @+58780 [58780] exempt        q17 ? after
    @+58869 [58869] exhibit       q20 ? ␅
    @+58869 [58869] exhibit       q21 ? after
    @+58928 [58928] exile         q22 ? ␅
    @+58928 [58928] exile         q23 ? after
    @+58928 [58928] exile         q24 ? ␅
    @+58928 [58928] exile         q25 ? after
    @+58940 [58940] exist         q28 ? ␅
    @+58940 [58940] exist         q29 ? after
    @+58944 [58944] existent      q30 ? ␅
    @+58944 [58944] existent      q31 ? after
    @+58954 [58954] exit          q32 ? ␅
    @+58954 [58954] exit          q33 ? it
    @+58954 [58954] exit          done. it
    @+58962 [58962] exobiologists q26 ? ␅
    @+58962 [58962] exobiologists q27 ? before
    @+58996 [58996] exogen        q18 ? ␅
    @+58996 [58996] exogen        q19 ? before
    @+59214 [59214] expel         q14 ? ␅
    @+59214 [59214] expel         q15 ? before
    @+60081 [60081] face          q7  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1498 🥳 6 ⏱️ 0:01:48.106909

📜 2 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:PZAZZ n n n n n remain:6291
    ⬜⬜⬜⬜⬜ tried:ROTOR n n n n n remain:1818
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:663
    ⬜⬜⬜⬜⬜ tried:JUJUS n n n n n remain:107
    ⬜🟨🟩⬜⬜ tried:BEECH n m Y n n remain:9
    🟩⬜🟩⬜🟩 tried:ENEMY Y n Y n Y remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1641 🥳 17 ⏱️ 0:03:05.932734

📜 1 sessions
💰 score: 9900

    3/6
    EARLS 🟨🟨🟨🟨⬜
    ALERT 🟩🟩🟨🟨🟨
    ALTER 🟩🟩🟩🟩🟩
    4/6
    ALTER 🟨⬜🟨⬜⬜
    GIANT ⬜⬜🟨⬜🟩
    SABOT 🟩🟨⬜⬜🟩
    SQUAT 🟩🟩🟩🟩🟩
    5/6
    SQUAT ⬜⬜⬜🟨⬜
    YEARN ⬜⬜🟨⬜⬜
    VOILA ⬜⬜🟨⬜🟨
    MAGIC ⬜🟨⬜🟩⬜
    AFFIX 🟩🟩🟩🟩🟩
    4/6
    AFFIX ⬜⬜⬜⬜⬜
    SPORT ⬜⬜🟨⬜⬜
    MODEL 🟩🟨⬜🟨🟨
    MELON 🟩🟩🟩🟩🟩
    Final 1/2
    FARCE 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1618 🥳 score:22 ⏱️ 0:02:02.239110

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. HALVE attempts:5 score:5
2. DRYER attempts:7 score:7
3. THERE attempts:4 score:4
4. MINTY attempts:6 score:6

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1618 🥳 score:49 ⏱️ 0:03:14.725481

📜 1 sessions

Octordle Classic

1. PAPER attempts:11 score:11
2. AVAIL attempts:4 score:4
3. APRON attempts:2 score:2
4. SCOPE attempts:3 score:3
5. BELCH attempts:7 score:7
6. QUALM attempts:5 score:5
7. ELBOW attempts:8 score:8
8. LILAC attempts:9 score:9

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1598 🥳 score:47 ⏱️ 0:09:54.857467

📜 1 sessions

Sedecordle Classic sedecordle.com

1. PICKY attempts:9 score:0
2. HELIX attempts:4 score:9
3. LOCAL attempts:8 score:0
4. INBOX attempts:3 score:8
5. KNEED attempts:11 score:1
6. PAINT attempts:12 score:1
7. PROWL attempts:13 score:1
8. LORRY attempts:6 score:3
9. ALPHA attempts:7 score:0
10. FOCUS attempts:10 score:7
11. BRUSH attempts:5 score:0
12. LOUSY attempts:6 score:5
13. CREME attempts:14 score:1
14. CHILL attempts:15 score:4
15. LIVID attempts:16 score:1
16. TRULY attempts:17 score:6

# [squareword.org](squareword.org) 🧩 #1611 🥳 7 ⏱️ 0:01:35.423577

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟩 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T A R T
    T I G E R
    O L I V E
    V E N U E
    E D G E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1548 🥳 312 ⏱️ 0:04:35.113370

🤔 313 attempts
📜 1 sessions
🫧 14 chat sessions
⁉️ 75 chat prompts
🤖 75 dolphin3:latest replies
🔥   1 🥵  14 😎  36 🥶 249 🧊  12

      $1 #313 exposure          100.00°C 🥳 1000‰ ~301 used:0  [300]  source:dolphin3
      $2 #112 toxicity           43.99°C 🔥  997‰   ~4 used:59 [3]    source:dolphin3
      $3 #127 toxic              35.23°C 🥵  984‰  ~51 used:30 [50]   source:dolphin3
      $4 #296 cytotoxicity       34.47°C 🥵  980‰  ~12 used:7  [11]   source:dolphin3
      $5 #182 nephrotoxic        33.58°C 🥵  974‰  ~13 used:9  [12]   source:dolphin3
      $6 #220 teratogen          32.75°C 🥵  969‰   ~5 used:6  [4]    source:dolphin3
      $7  #99 contamination      32.74°C 🥵  968‰   ~6 used:6  [5]    source:dolphin3
      $8 #183 carcinogen         32.12°C 🥵  961‰   ~7 used:6  [6]    source:dolphin3
      $9 #159 toxicant           32.10°C 🥵  960‰   ~8 used:6  [7]    source:dolphin3
     $10 #100 contagion          31.53°C 🥵  951‰   ~9 used:6  [8]    source:dolphin3
     $11 #175 teratogenic        31.09°C 🥵  947‰  ~10 used:6  [9]    source:dolphin3
     $17 #209 radiation          28.71°C 😎  893‰  ~15 used:0  [14]   source:dolphin3
     $53 #177 viral              21.33°C 🥶        ~59 used:0  [58]   source:dolphin3
    $302   #1 banana             -0.11°C 🧊       ~302 used:0  [301]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1581 🥳 727 ⏱️ 0:18:35.964119

🤔 728 attempts
📜 1 sessions
🫧 47 chat sessions
⁉️ 240 chat prompts
🤖 240 dolphin3:latest replies
🔥   2 🥵  22 😎  70 🥶 526 🧊 107

      $1 #728 balancer         100.00°C 🥳 1000‰ ~621 used:0   [620]  source:dolphin3
      $2 #162 cogner            53.11°C 🔥  998‰  ~83 used:233 [82]   source:dolphin3
      $3 #453 hurler            51.51°C 🔥  994‰  ~19 used:90  [18]   source:dolphin3
      $4 #459 sauter            50.66°C 🥵  989‰  ~84 used:27  [83]   source:dolphin3
      $5 #463 jeter             50.32°C 🥵  988‰   ~7 used:7   [6]    source:dolphin3
      $6 #578 cracher           50.13°C 🥵  987‰   ~8 used:7   [7]    source:dolphin3
      $7 #610 fracasser         48.40°C 🥵  978‰   ~9 used:7   [8]    source:dolphin3
      $8 #499 lâcher            48.31°C 🥵  977‰  ~10 used:7   [9]    source:dolphin3
      $9 #411 tomber            48.21°C 🥵  975‰  ~59 used:15  [58]   source:dolphin3
     $10 #540 empoigner         48.12°C 🥵  974‰  ~11 used:7   [10]   source:dolphin3
     $11 #594 sautiller         47.86°C 🥵  971‰  ~12 used:7   [11]   source:dolphin3
     $26 #560 crisser           43.80°C 😎  894‰  ~20 used:0   [19]   source:dolphin3
     $96 #539 cogneur           33.99°C 🥶       ~102 used:0   [101]  source:dolphin3
    $622 #302 coacher           -0.09°C 🧊       ~622 used:0   [621]  source:dolphin3
