# 2026-10-28

- 🔗 spaceword.org 🧩 2026-10-27 🏁 score 2165 ranked 50.8% 155/305 ⏱️ 1:37:05.336958
- 🔗 wordgrid 🧩 #879 🟪 rarity:0.19 ⏱️ 0:02:00.186836
- 🔗 alfagok.diginaut.net 🧩 #725 🥳 34 ⏱️ 0:00:42.538284
- 🔗 alphaguess.com 🧩 #1192 🥳 24 ⏱️ 0:00:41.345312
- 🔗 dontwordle.com 🧩 #1618 🥳 6 ⏱️ 0:01:53.860818
- 🔗 dictionary.com hurdle 🧩 #1761 🥳 15 ⏱️ 0:02:37.117046
- 🔗 Quordle Classic 🧩 #1738 🥳 score:24 ⏱️ 0:01:51.915235
- 🔗 Octordle Classic 🧩 #1738 🥳 score:60 ⏱️ 0:02:20.832802
- 🔗 Sedecordle Classic 🧩 #1718 🥳 score:49 ⏱️ 0:03:34.641946
- 🔗 squareword.org 🧩 #1731 🥳 8 ⏱️ 0:03:05.422935
- 🔗 cemantle.certitudes.org 🧩 #1668 🥳 191 ⏱️ 0:09:22.572161
- 🔗 cemantix.certitudes.org 🧩 #1701 🥳 69 ⏱️ 0:03:51.861302

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
























# [spaceword.org](spaceword.org) 🧩 2026-10-27 🏁 score 2165 ranked 50.8% 155/305 ⏱️ 1:37:05.336958

📜 5 sessions
- tiles: 21/21
- score: 2165 bonus: +65
- rank: 155/305

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ A G E _ _ _ _   
      _ _ _ M O N D E _ _   
      _ _ _ _ _ T O _ _ _   
      _ _ _ _ _ W O _ _ _   
      _ _ _ Q U I Z _ _ _   
      _ _ _ _ _ N E _ _ _   
      _ _ _ _ H E R _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 2026-10-27 🤔 rarity:nan ⏱️ 0:01:43.563056

📜 1 sessions
🌌 🌌 🦄
🌌 🌌 🌌
🦄 🦄 🦄

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #879 🟪 rarity:0.19 ⏱️ 0:02:00.186836

📜 3 sessions
🌌 🌌 🦄
🌌 🌌 🌌
🦄 🦄 🦄
Rarity: 0.19 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #725 🥳 34 ⏱️ 0:00:42.538284

🤔 34 attempts
📜 1 sessions

    @        [     0] &-teken          
    @+199631 [199631] lijk             q0  ? ␅
    @+199631 [199631] lijk             q1  ? after
    @+299528 [299528] schroot          q2  ? ␅
    @+299528 [299528] schroot          q3  ? after
    @+324110 [324110] sub              q6  ? ␅
    @+324110 [324110] sub              q7  ? after
    @+330293 [330293] televisie        q10 ? ␅
    @+330293 [330293] televisie        q11 ? after
    @+333499 [333499] thesis           q12 ? ␅
    @+333499 [333499] thesis           q13 ? after
    @+333905 [333905] ti               q14 ? ␅
    @+333905 [333905] ti               q15 ? after
    @+335303 [335303] tjingel          q16 ? ␅
    @+335303 [335303] tjingel          q17 ? after
    @+335949 [335949] toekomst         q18 ? ␅
    @+335949 [335949] toekomst         q19 ? after
    @+335963 [335963] toekomstgericht  q28 ? ␅
    @+335963 [335963] toekomstgericht  q29 ? after
    @+335968 [335968] toekomstig       q32 ? ␅
    @+335968 [335968] toekomstig       q33 ? it
    @+335968 [335968] toekomstig       done. it
    @+335972 [335972] toekomstmodellen q30 ? ␅
    @+335972 [335972] toekomstmodellen q31 ? before
    @+335981 [335981] toekomstplannen  q26 ? ␅
    @+335981 [335981] toekomstplannen  q27 ? before
    @+336013 [336013] toekunnen        q24 ? ␅
    @+336013 [336013] toekunnen        q25 ? before
    @+336077 [336077] toeleverancier   q22 ? ␅
    @+336077 [336077] toeleverancier   q23 ? before
    @+336204 [336204] toer             q21 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1192 🥳 24 ⏱️ 0:00:41.345312

🤔 24 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+24517 [24517] car       q4  ? ␅
    @+24517 [24517] car       q5  ? after
    @+30620 [30620] clitoric  q10 ? ␅
    @+30620 [30620] clitoric  q11 ? after
    @+33648 [33648] computer  q12 ? ␅
    @+33648 [33648] computer  q13 ? after
    @+33696 [33696] con       q18 ? ␅
    @+33696 [33696] con       q19 ? after
    @+34047 [34047] condition q20 ? ␅
    @+34047 [34047] condition q21 ? after
    @+34214 [34214] confess   q22 ? ␅
    @+34214 [34214] confess   q23 ? it
    @+34214 [34214] confess   done. it
    @+34401 [34401] conge     q16 ? ␅
    @+34401 [34401] conge     q17 ? before
    @+35182 [35182] content   q14 ? ␅
    @+35182 [35182] content   q15 ? before
    @+36722 [36722] cos       q6  ? ␅
    @+36722 [36722] cos       q7  ? before
    @+49066 [49066] disturb   q2  ? ␅
    @+49066 [49066] disturb   q3  ? before
    @+98139 [98139] mac       q0  ? ␅
    @+98139 [98139] mac       q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1618 🥳 6 ⏱️ 0:01:53.860818

📜 2 sessions
💰 score: 72

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:PENNE n n n n n remain:4618
    ⬜⬜⬜⬜⬜ tried:JUJUS n n n n n remain:1583
    ⬜⬜⬜⬜⬜ tried:DOGGO n n n n n remain:606
    ⬜⬜⬜⬜⬜ tried:VILLI n n n n n remain:161
    ⬜🟨⬜⬜⬜ tried:MYRRH n m n n n remain:24
    🟨⬜⬜🟨⬜ tried:ABAYA m n n m n remain:9

    Undos used: 5

      9 words remaining
    x 8 unused letters
    = 72 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1761 🥳 15 ⏱️ 0:02:37.117046

📜 1 sessions
💰 score: 10100

    4/6
    TESLA ⬜🟨⬜⬜🟨
    DRAKE ⬜🟩🟩⬜🟩
    GRACE ⬜🟩🟩🟩🟩
    BRACE 🟩🟩🟩🟩🟩
    3/6
    BRACE ⬜⬜⬜⬜⬜
    DINTS 🟩⬜⬜⬜⬜
    DOUGH 🟩🟩🟩🟩🟩
    3/6
    DOUGH 🟩⬜⬜⬜⬜
    DAISY 🟩⬜🟩⬜🟩
    DEIFY 🟩🟩🟩🟩🟩
    4/6
    DEIFY ⬜🟨⬜⬜⬜
    PASTE 🟩⬜🟨⬜🟩
    PULSE 🟩⬜⬜🟩🟩
    PROSE 🟩🟩🟩🟩🟩
    Final 1/2
    BLACK 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1738 🥳 score:24 ⏱️ 0:01:51.915235

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. DEALT attempts:4 score:4
2. FLUME attempts:8 score:8
3. SLEEK attempts:7 score:7
4. RELIC attempts:5 score:5

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1738 🥳 score:60 ⏱️ 0:02:20.832802

📜 1 sessions

Octordle Classic

1. STASH attempts:10 score:10
2. EVOKE attempts:4 score:4
3. GRILL attempts:6 score:6
4. PRIDE attempts:5 score:5
5. BARON attempts:8 score:8
6. BLEEP attempts:7 score:7
7. FUNKY attempts:11 score:11
8. THEME attempts:9 score:9

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1718 🥳 score:49 ⏱️ 0:03:34.641946

📜 1 sessions

Sedecordle Classic sedecordle.com

1. BROWN attempts:18 score:1
2. STONY attempts:8 score:8
3. SHOUT attempts:12 score:1
4. MORPH attempts:4 score:2
5. SUITE attempts:11 score:1
6. FOCAL attempts:15 score:1
7. TRACT attempts:19 score:1
8. CHIME attempts:5 score:9
9. DISCO attempts:6 score:0
10. HILLY attempts:7 score:6
11. FOLLY attempts:19 score:2
12. SCOUT attempts:13 score:0
13. HARPY attempts:9 score:0
14. FLICK attempts:16 score:9
15. VIPER attempts:17 score:1
16. RHYME attempts:10 score:7

# [squareword.org](squareword.org) 🧩 #1731 🥳 8 ⏱️ 0:03:05.422935

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S O L E S
    P L E A T
    A D A G E
    R I F L E
    K E Y E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1668 🥳 191 ⏱️ 0:09:22.572161

🤔 192 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 26 chat prompts
🤖 26 gemma4:12b replies
🔥   3 🥵  10 😎  42 🥶 115 🧊  21

      $1 #192 reporting       100.00°C 🥳 1000‰ ~171 used:0  [170]  source:gemma4
      $2 #128 report           42.60°C 🔥  994‰   ~3 used:10 [2]    source:gemma4
      $3 #190 monitoring       39.09°C 🔥  991‰   ~1 used:0  [0]    source:gemma4
      $4 #151 forecasting      38.98°C 🔥  990‰   ~2 used:8  [1]    source:gemma4
      $5  #89 analysis         35.61°C 🥵  985‰  ~13 used:8  [12]   source:gemma4
      $6 #111 verification     34.74°C 🥵  980‰  ~12 used:5  [11]   source:gemma4
      $7 #135 audit            30.43°C 🥵  958‰   ~4 used:1  [3]    source:gemma4
      $8  #98 documentation    30.03°C 🥵  952‰  ~10 used:3  [9]    source:gemma4
      $9 #187 assessment       29.39°C 🥵  947‰   ~5 used:0  [4]    source:gemma4
     $10 #118 filing           28.75°C 🥵  942‰   ~6 used:0  [5]    source:gemma4
     $11  #85 data             28.02°C 🥵  929‰  ~11 used:4  [10]   source:gemma4
     $15  #81 statistics       26.23°C 😎  898‰  ~14 used:1  [13]   source:gemma4
     $57 #170 digest           16.12°C 🥶        ~64 used:0  [63]   source:gemma4
    $172  #21 dynamics         -0.40°C 🧊       ~172 used:0  [171]  source:gemma4

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1701 🥳 69 ⏱️ 0:03:51.861302

🤔 70 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 12 chat prompts
🤖 12 gemma4:12b replies
🥵  4 😎  9 🥶 48 🧊  8

     $1 #70 barrage        100.00°C 🥳 1000‰ ~62 used:0 [61]  source:gemma4
     $2 #58 rivière         42.01°C 🥵  982‰  ~4 used:4 [3]   source:gemma4
     $3 #62 fleuve          38.95°C 🥵  968‰  ~3 used:3 [2]   source:gemma4
     $4 #63 affluent        36.58°C 🥵  957‰  ~1 used:1 [0]   source:gemma4
     $5 #61 eau             36.54°C 🥵  956‰  ~2 used:1 [1]   source:gemma4
     $6 #64 bassin          29.35°C 😎  854‰  ~5 used:0 [4]   source:gemma4
     $7 #68 ruisseau        28.08°C 😎  826‰  ~6 used:0 [5]   source:gemma4
     $8 #65 débit           26.36°C 😎  757‰  ~7 used:0 [6]   source:gemma4
     $9 #67 nappe           25.07°C 😎  696‰  ~8 used:0 [7]   source:gemma4
    $10 #21 vallée          24.63°C 😎  656‰ ~13 used:5 [12]  source:gemma4
    $11 #66 estuaire        20.67°C 😎  304‰  ~9 used:0 [8]   source:gemma4
    $12 #52 tourbière       20.17°C 😎  225‰ ~10 used:0 [9]   source:gemma4
    $15 #38 montagneux      18.45°C 🥶       ~17 used:2 [16]  source:gemma4
    $63 #24 décor           -0.62°C 🧊       ~63 used:0 [62]  source:gemma4
