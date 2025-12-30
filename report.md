# 2025-12-30

- 🔗 spaceword.org 🧩 2025-12-29 🏁 score 2170 ranked 39.9% 133/333 ⏱️ 0:20:28.830514
- 🔗 alfagok.diginaut.net 🧩 #423 🥳 17 ⏱️ 0:00:35.127190
- 🔗 alphaguess.com 🧩 #889 🥳 17 ⏱️ 0:00:34.622745
- 🔗 dontwordle.com 🧩 #1316 🥳 6 ⏱️ 0:01:43.447651
- 🔗 dictionary.com hurdle 🧩 #1459 🥳 18 ⏱️ 0:02:52.767405
- 🔗 Quordle Classic 🧩 #1436 🥳 score:26 ⏱️ 0:02:27.656128
- 🔗 Octordle Classic 🧩 #1436 🥳 score:60 ⏱️ 0:03:40.721603
- 🔗 squareword.org 🧩 #1429 🥳 7 ⏱️ 0:02:18.207864
- 🔗 cemantle.certitudes.org 🧩 #1366 🥳 89 ⏱️ 0:01:57.773284
- 🔗 cemantix.certitudes.org 🧩 #1399 🥳 89 ⏱️ 0:03:11.394200
- 🔗 Quordle Sequence 🧩 #1436 🥳 score:21 ⏱️ 0:01:57.111258
- 🔗 Quordle Rescue 🧩 #50 😦 score:31 ⏱️ 0:02:46.995687
- 🔗 Quordle Extreme 🧩 #519 🥳 score:24 ⏱️ 0:01:47.888455
- 🔗 Octordle Rescue 🧩 #1436 🥳 score:8 ⏱️ 0:06:06.762032
- 🔗 Octordle Sequence 🧩 #1436 🥳 score:73 ⏱️ 0:04:51.549111
- 🔗 Octordle Extreme 🧩 #1436 🥳 score:64 ⏱️ 0:03:56.848101

# Dev

## WIP

- ui:
  - Handle -- stabilizing core over Listing
  - Shell -- minimizing over Handle

- meta: rework command model over Shell

## TODO

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





# spaceword.org 🧩 2025-12-29 🏁 score 2170 ranked 39.9% 133/333 ⏱️ 0:20:28.830514

📜 4 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 133/333

      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ V E G I E S _ _
      _ _ _ _ E _ _ _ _ _
      _ _ _ _ M _ W _ _ _
      _ _ F O O D I E _ _
      _ _ E X T E N T _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _


# alfagok.diginaut.net 🧩 #423 🥳 17 ⏱️ 0:00:35.127190

🤔 17 attempts
📜 1 sessions

    @        [     0] &-teken
    @+1      [     1] &-tekens
    @+2      [     2] -cijferig
    @+3      [     3] -e-mail
    @+199833 [199833] lijm           q0  ? after
    @+223633 [223633] mol            q3  ? after
    @+235692 [235692] octopus        q4  ? after
    @+238809 [238809] on             q5  ? after
    @+243279 [243279] onroerend      q6  ? after
    @+243439 [243439] ont            q8  ? after
    @+244459 [244459] ontraad        q9  ? after
    @+244977 [244977] onttakeld      q10 ? after
    @+245236 [245236] ontwapen       q11 ? after
    @+245312 [245312] ontwerp        q12 ? after
    @+245404 [245404] ontwerpstudies q13 ? after
    @+245447 [245447] ontwijd        q14 ? after
    @+245467 [245467] ontwikkel      q15 ? after
    @+245480 [245480] ontwikkeld     q16 ? it
    @+245480 [245480] ontwikkeld     done. it
    @+245496 [245496] ontwikkeling   q7  ? before
    @+247751 [247751] op             q2  ? before
    @+299755 [299755] schub          q1  ? before

# alphaguess.com 🧩 #889 🥳 17 ⏱️ 0:00:34.622745

🤔 17 attempts
📜 1 sessions

    @        [     0] aa
    @+1      [     1] aah
    @+2      [     2] aahed
    @+3      [     3] aahing
    @+98224  [ 98224] mach          q0  ? after
    @+147328 [147328] rho           q1  ? after
    @+159610 [159610] slug          q3  ? after
    @+165764 [165764] stint         q4  ? after
    @+167288 [167288] sub           q6  ? after
    @+168029 [168029] subs          q7  ? after
    @+168418 [168418] subway        q8  ? after
    @+168606 [168606] suffer        q9  ? after
    @+168618 [168618] suffice       q13 ? after
    @+168623 [168623] sufficiencies q14 ? after
    @+168625 [168625] sufficient    q16 ? it
    @+168625 [168625] sufficient    done. it
    @+168626 [168626] sufficiently  q15 ? before
    @+168628 [168628] suffix        q12 ? before
    @+168659 [168659] suffuse       q11 ? before
    @+168709 [168709] sugh          q10 ? before
    @+168814 [168814] sulfur        q5  ? before
    @+171928 [171928] tag           q2  ? before

# dontwordle.com 🧩 #1316 🥳 6 ⏱️ 0:01:43.447651

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:SEEPS n n n n n remain:3094
    ⬜⬜⬜⬜⬜ tried:YABBY n n n n n remain:736
    ⬜⬜⬜⬜⬜ tried:KUDZU n n n n n remain:308
    🟨⬜⬜⬜⬜ tried:CRWTH m n n n n remain:12
    ⬜⬜⬜🟩🟩 tried:MIMIC n n n Y Y remain:2
    ⬜🟩🟨🟩🟩 tried:FOLIC n Y m Y Y remain:1

    Undos used: 4

      1 words remaining
    x 6 unused letters
    = 6 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1459 🥳 18 ⏱️ 0:02:52.767405

📜 1 sessions
💰 score: 9800

    4/6
    STELA ⬜⬜⬜🟩⬜
    DOILY ⬜⬜🟨🟩🟩
    GIRLY ⬜🟨⬜🟩🟩
    IMPLY 🟩🟩🟩🟩🟩
    5/6
    IMPLY ⬜⬜⬜🟩⬜
    SABLE 🟩🟨⬜🟩⬜
    SCALD 🟩⬜🟩🟩⬜
    SHALT 🟩🟩🟩🟩⬜
    SHALL 🟩🟩🟩🟩🟩
    4/6
    SHALL ⬜⬜🟨⬜⬜
    DREAM ⬜⬜🟨🟨⬜
    WAKEN ⬜🟩⬜🟩🟩
    EATEN 🟩🟩🟩🟩🟩
    4/6
    EATEN 🟨⬜⬜⬜⬜
    POISE ⬜⬜⬜⬜🟨
    MERCY ⬜🟨⬜⬜⬜
    DWELL 🟩🟩🟩🟩🟩
    Final 1/2
    TAPER 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1436 🥳 score:26 ⏱️ 0:02:27.656128

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. ALLOT attempts:3 score:3
2. CAGEY attempts:6 score:6
3. BLINK attempts:8 score:8
4. BUNNY attempts:8 score:9

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1436 🥳 score:60 ⏱️ 0:03:40.721603

📜 1 sessions

Octordle Classic

1. SWASH attempts:11 score:11
2. FACET attempts:10 score:10
3. ROOST attempts:9 score:9
4. TOTAL attempts:8 score:8
5. LILAC attempts:7 score:7
6. ACRID attempts:4 score:4
7. UNION attempts:6 score:6
8. CLUMP attempts:5 score:5

# squareword.org 🧩 #1429 🥳 7 ⏱️ 0:02:18.207864

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C L A I M
    L I T R E
    E N R O L
    F E I N T
    T R A Y S

# cemantle.certitudes.org 🧩 #1366 🥳 89 ⏱️ 0:01:57.773284

🤔 90 attempts
📜 3 sessions
🫧 3 chat sessions
⁉️ 17 chat prompts
🤖 17 dolphin3:latest replies
🔥  2 🥵  2 😎 12 🥶 67 🧊  6

     $1 #90  ~1 navigation       100.00°C 🥳 1000‰
     $2 #71  ~5 intuitive         43.19°C 🔥  991‰
     $3 #63  ~8 functionality     42.47°C 🔥  990‰
     $4 #67  ~7 usability         41.96°C 🥵  988‰
     $5 #88  ~2 interactive       35.64°C 🥵  924‰
     $6 #68  ~6 accessibility     33.21°C 😎  884‰
     $7 #37 ~13 software          32.42°C 😎  864‰
     $8 #49 ~12 desktop           31.31°C 😎  824‰
     $9 #54 ~10 ergonomic         30.66°C 😎  804‰
    $10 #51 ~11 keyboard          29.82°C 😎  752‰
    $11 #56  ~9 design            29.76°C 😎  746‰
    $12 #76  ~4 user              27.76°C 😎  620‰
    $18 #66     reliability       23.17°C 🥶
    $85 #22     book              -0.13°C 🧊

# cemantix.certitudes.org 🧩 #1399 🥳 89 ⏱️ 0:03:11.394200

🤔 90 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 19 chat prompts
🤖 19 dolphin3:latest replies
😱  1 🔥  3 🥵  6 😎  9 🥶 48 🧊 22

     $1 #90  ~1 hôte          100.00°C 🥳 1000‰
     $2 #73  ~9 gîte           57.57°C 😱  999‰
     $3 #77  ~7 auberge        38.68°C 🔥  993‰
     $4 #88  ~3 chambre        37.10°C 🔥  992‰
     $5 #67 ~12 hôtel          36.84°C 🔥  991‰
     $6 #14 ~20 château        28.69°C 🥵  948‰
     $7 #65 ~13 demeure        28.25°C 🥵  939‰
     $8 #71 ~10 manoir         28.10°C 🥵  937‰
     $9 #78  ~6 chalet         27.89°C 🥵  931‰
    $10 #23 ~19 clos           26.81°C 🥵  920‰
    $11 #89  ~2 ferme          26.44°C 🥵  905‰
    $12 #86  ~4 villa          26.00°C 😎  891‰
    $21  #1     ami            16.20°C 🥶
    $69 #52     on             -0.08°C 🧊

# [Quordle Sequence](m-w.com/games/quordle/#/sequence) 🧩 #1436 🥳 score:21 ⏱️ 0:01:57.111258

📜 1 sessions

Quordle Sequence m-w.com/games/quordle/

1. WHIRL attempts:3 score:3
2. SWOOP attempts:5 score:5
3. TRACK attempts:6 score:6
4. TANGY attempts:7 score:7

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #50 😦 score:31 ⏱️ 0:02:46.995687

📜 2 sessions

Quordle Rescue m-w.com/games/quordle/

1. LO_ER ~W -ABCDHINSTUY attempts:9 score:-1
2. DETER attempts:6 score:6
3. WHICH attempts:9 score:9
4. BELLE attempts:7 score:7

# [Quordle Extreme](m-w.com/games/quordle/#/extreme) 🧩 #519 🥳 score:24 ⏱️ 0:01:47.888455

📜 1 sessions

Quordle Extreme m-w.com/games/quordle/

1. CLINK attempts:7 score:7
2. DONUT attempts:5 score:5
3. PHASE attempts:8 score:8
4. CLIMB attempts:4 score:4

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1436 🥳 score:8 ⏱️ 0:06:06.762032

📜 1 sessions

Octordle Rescue

1. SOOTH attempts:5 score:7
2. SCORN attempts:6 score:6
3. SCION attempts:11 score:11
4. NORTH attempts:10 score:10
5. QUEST attempts:13 score:13
6. WORRY attempts:9 score:9
7. PARTY attempts:5 score:5
8. TENTH attempts:8 score:8

# [Octordle Sequence](britannica.com/games/octordle/daily-sequence) 🧩 #1436 🥳 score:73 ⏱️ 0:04:51.549111

📜 2 sessions

Octordle Sequence


1. EXILE attempts:4 score:4
2. VOICE attempts:6 score:6
3. SHADY attempts:8 score:8
4. VAULT attempts:9 score:9
5. FOCAL attempts:10 score:10
6. THROW attempts:11 score:11
7. RELIC attempts:12 score:12
8. FISHY attempts:13 score:13

# [Octordle Extreme](britannica.com/games/octordle/extreme) 🧩 #1436 🥳 score:64 ⏱️ 0:03:56.848101

📜 1 sessions

Octordle Extreme

1. AGAVE attempts:12 score:12
2. BUILD attempts:6 score:6
3. NEWLY attempts:11 score:11
4. REPEL attempts:10 score:10
5. CHUTE attempts:5 score:5
6. AGILE attempts:3 score:3
7. VALOR attempts:9 score:9
8. CAPON attempts:8 score:8
