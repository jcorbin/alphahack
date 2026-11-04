# 2026-11-05

- 🔗 spaceword.org 🧩 2026-11-04 🏁 score 2168 ranked 46.3% 143/309 ⏱️ 0:24:58.850225
- 🔗 wordgrid 🧩 #887 🟪 rarity:0.19 ⏱️ 0:01:59.291799
- 🔗 alfagok.diginaut.net 🧩 #733 🥳 22 ⏱️ 0:00:34.418628
- 🔗 alphaguess.com 🧩 #1200 🥳 30 ⏱️ 0:00:39.443721
- 🔗 dontwordle.com 🧩 #1626 🥳 6 ⏱️ 0:01:05.812296
- 🔗 dictionary.com hurdle 🧩 #1769 🥳 17 ⏱️ 0:02:49.020154
- 🔗 cemantix.certitudes.org 🧩 #1709 🥳 71 ⏱️ 1:04:52.938169
- 🔗 cemantle.certitudes.org 🧩 #1676 🥳 207 ⏱️ 0:07:07.487668
- 🔗 Quordle Classic 🧩 #1746 🥳 score:26 ⏱️ 0:01:56.166190
- 🔗 Octordle Classic 🧩 #1746 🥳 score:72 ⏱️ 0:02:53.075436
- 🔗 Sedecordle Classic 🧩 #1726 🥳 score:39 ⏱️ 0:03:06.846178
- 🔗 squareword.org 🧩 #1739 🥳 8 ⏱️ 0:02:06.676505

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





# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #887 🟪 rarity:0.19 ⏱️ 0:01:59.291799

📜 2 sessions
🌌 🌌 🦄
🦄 🌌 🦄
🌌 🌌 🌌
Rarity: 0.19 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-04 🏁 score 2168 ranked 46.3% 143/309 ⏱️ 0:24:58.850225

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 143/309

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ J _ L O G O E D _   
      _ O _ O _ H M _ A _   
      _ E X U V I A _ L _   
      _ _ _ T _ _ S _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #733 🥳 22 ⏱️ 0:00:34.418628

🤔 22 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+1      [     1] &-tekens     
    @+2      [     2] -cijferig    
    @+3      [     3] -e-mail      
    @+199631 [199631] lijk         q0  ? ␅
    @+199631 [199631] lijk         q1  ? after
    @+299522 [299522] schroot      q2  ? ␅
    @+299522 [299522] schroot      q3  ? after
    @+349304 [349304] vakantie     q4  ? ␅
    @+349304 [349304] vakantie     q5  ? after
    @+352868 [352868] ver          q8  ? ␅
    @+352868 [352868] ver          q9  ? after
    @+353950 [353950] verdeel      q16 ? ␅
    @+353950 [353950] verdeel      q17 ? after
    @+354499 [354499] verduidelijk q18 ? ␅
    @+354499 [354499] verduidelijk q19 ? after
    @+354746 [354746] vereniging   q20 ? ␅
    @+354746 [354746] vereniging   q21 ? it
    @+354746 [354746] vereniging   done. it
    @+355048 [355048] verg         q14 ? ␅
    @+355048 [355048] verg         q15 ? before
    @+358161 [358161] verluiert    q12 ? ␅
    @+358161 [358161] verluiert    q13 ? before
    @+363453 [363453] verzout      q10 ? ␅
    @+363453 [363453] verzout      q11 ? before
    @+374038 [374038] vrij         q6  ? ␅
    @+374038 [374038] vrij         q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1200 🥳 30 ⏱️ 0:00:39.443721

🤔 30 attempts
📜 1 sessions

    @       [    0] aa       
    @+1398  [ 1398] acrogen  q12 ? ␅
    @+1398  [ 1398] acrogen  q13 ? after
    @+1452  [ 1452] act      q18 ? ␅
    @+1452  [ 1452] act      q19 ? after
    @+1531  [ 1531] activize q20 ? ␅
    @+1531  [ 1531] activize q21 ? after
    @+1537  [ 1537] actor    q26 ? ␅
    @+1537  [ 1537] actor    q27 ? after
    @+1541  [ 1541] actress  q28 ? ␅
    @+1541  [ 1541] actress  q29 ? it
    @+1541  [ 1541] actress  done. it
    @+1545  [ 1545] actual   q24 ? ␅
    @+1545  [ 1545] actual   q25 ? before
    @+1574  [ 1574] aculeate q22 ? ␅
    @+1574  [ 1574] aculeate q23 ? before
    @+1616  [ 1616] ad       q16 ? ␅
    @+1616  [ 1616] ad       q17 ? before
    @+2097  [ 2097] ads      q14 ? ␅
    @+2097  [ 2097] ads      q15 ? before
    @+2802  [ 2802] ag       q10 ? ␅
    @+2802  [ 2802] ag       q11 ? before
    @+6114  [ 6114] anis     q8  ? ␅
    @+6114  [ 6114] anis     q9  ? before
    @+12254 [12254] bail     q6  ? ␅
    @+12254 [12254] bail     q7  ? before
    @+24517 [24517] car      q4  ? ␅
    @+24517 [24517] car      q5  ? before
    @+49066 [49066] disturb  q2  ? ␅
    @+49066 [49066] disturb  q3  ? before
    @+98139 [98139] mac      q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1626 🥳 6 ⏱️ 0:01:05.812296

📜 1 sessions
💰 score: 32

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:COOCH n n n n n remain:6849
    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:3430
    ⬜⬜⬜⬜⬜ tried:SUNNS n n n n n remain:892
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:380
    🟨⬜⬜⬜⬜ tried:AGAMA m n n n n remain:81
    ⬜🟩🟨🟩⬜ tried:DAWED n Y m Y n remain:4

    Undos used: 2

      4 words remaining
    x 8 unused letters
    = 32 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1769 🥳 17 ⏱️ 0:02:49.020154

📜 2 sessions
💰 score: 9900

    3/6
    LANES ⬜⬜⬜🟨🟨
    STORE 🟨🟨🟩⬜🟩
    THOSE 🟩🟩🟩🟩🟩
    3/6
    THOSE ⬜⬜⬜⬜🟩
    CARLE ⬜⬜🟨🟩🟩
    RIFLE 🟩🟩🟩🟩🟩
    6/6
    RIFLE ⬜⬜⬜⬜⬜
    SNOUT ⬜⬜⬜🟨⬜
    AMUCK ⬜⬜🟨⬜⬜
    PUDGY ⬜🟩🟩⬜🟩
    DWEEB 🟨⬜⬜⬜🟨
    BUDDY 🟩🟩🟩🟩🟩
    4/6
    BUDDY ⬜⬜🟨⬜⬜
    DINAR 🟩⬜⬜🟨⬜
    DALES 🟩🟨🟩🟨⬜
    DELTA 🟩🟩🟩🟩🟩
    Final 1/2
    BIOME 🟩🟩🟩🟩🟩

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1709 🥳 71 ⏱️ 1:04:52.938169

🤔 72 attempts
📜 2 sessions
🫧 8 chat sessions
⁉️ 46 chat prompts
🤖 46 dolphin3:latest replies
🔥  4 🥵  3 😎 18 🥶 42 🧊  4

     $1 #72 confus                100.00°C 🥳 1000‰ ~68 used:0  [67]  source:dolphin3
     $2 #49 incompréhensible       52.85°C 🔥  998‰  ~7 used:25 [6]   source:dolphin3
     $3 #63 ambigu                 52.03°C 🔥  996‰  ~2 used:4  [1]   source:dolphin3
     $4 #70 obscur                 51.75°C 🔥  994‰  ~1 used:2  [0]   source:dolphin3
     $5 #56 inintelligible         49.50°C 🔥  992‰  ~3 used:4  [2]   source:dolphin3
     $6 #67 inextricable           40.56°C 🥵  958‰  ~4 used:0  [3]   source:dolphin3
     $7 #65 incertain              39.31°C 🥵  941‰  ~5 used:0  [4]   source:dolphin3
     $8 #58 ambiguïté              38.72°C 🥵  929‰  ~6 used:0  [5]   source:dolphin3
     $9 #21 hallucination          36.36°C 😎  881‰ ~25 used:19 [24]  source:dolphin3
    $10 #60 incohérence            36.08°C 😎  873‰  ~8 used:0  [7]   source:dolphin3
    $11 #53 incompréhension        36.01°C 😎  871‰ ~20 used:5  [19]  source:dolphin3
    $12 #61 obscurité              35.81°C 😎  862‰  ~9 used:0  [8]   source:dolphin3
    $27 #64 ambivalent             27.13°C 🥶       ~29 used:0  [28]  source:dolphin3
    $69  #1 bonbon                 -2.09°C 🧊       ~69 used:0  [68]  source:dolphin3

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1676 🥳 207 ⏱️ 0:07:07.487668

🤔 208 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 49 chat prompts
🤖 49 dolphin3:latest replies
🔥   2 🥵   7 😎  36 🥶 157 🧊   5

      $1 #208 worldwide          100.00°C 🥳 1000‰ ~203 used:0  [202]  source:dolphin3
      $2 #204 global              68.16°C 🔥  998‰   ~1 used:1  [0]    source:dolphin3
      $3 #205 international       41.85°C 🔥  993‰   ~2 used:0  [1]    source:dolphin3
      $4 #179 industry            36.95°C 🥵  987‰   ~5 used:7  [4]    source:dolphin3
      $5  #83 technology          30.69°C 🥵  967‰  ~45 used:37 [44]   source:dolphin3
      $6 #201 demand              27.46°C 🥵  934‰   ~4 used:5  [3]    source:dolphin3
      $7 #195 market              26.78°C 🥵  920‰   ~3 used:2  [2]    source:dolphin3
      $8  #91 network             26.74°C 🥵  919‰  ~44 used:25 [43]   source:dolphin3
      $9  #51 innovation          26.20°C 🥵  907‰  ~28 used:17 [27]   source:dolphin3
     $10  #19 software            26.08°C 🥵  905‰  ~27 used:12 [26]   source:dolphin3
     $11  #85 platform            25.69°C 😎  898‰  ~29 used:2  [28]   source:dolphin3
     $12  #87 internet            25.32°C 😎  889‰  ~30 used:2  [29]   source:dolphin3
     $47  #35 optimization        16.80°C 🥶        ~48 used:0  [47]   source:dolphin3
    $204  #99 wan                 -0.15°C 🧊       ~204 used:0  [203]  source:dolphin3

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1746 🥳 score:26 ⏱️ 0:01:56.166190

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. SHINE attempts:5 score:5
2. TAROT attempts:7 score:7
3. VERGE attempts:8 score:8
4. LANKY attempts:6 score:6

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1746 🥳 score:72 ⏱️ 0:02:53.075436

📜 1 sessions

Octordle Classic

1. PRONG attempts:11 score:13
2. BUGGY attempts:11 score:11
3. BADGE attempts:12 score:12
4. AROMA attempts:4 score:4
5. SWEPT attempts:7 score:7
6. EJECT attempts:9 score:9
7. CRAWL attempts:10 score:10
8. QUOTE attempts:6 score:6

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1726 🥳 score:39 ⏱️ 0:03:06.846178

📜 1 sessions

Sedecordle Classic sedecordle.com

1. PARER attempts:8 score:0
2. FLASH attempts:18 score:8
3. BREAD attempts:11 score:1
4. DENIM attempts:9 score:1
5. ANKLE attempts:16 score:1
6. VISTA attempts:6 score:6
7. JUDGE attempts:15 score:1
8. STRIP attempts:4 score:5
9. UNTIE attempts:12 score:1
10. IVORY attempts:5 score:2
11. ELFIN attempts:14 score:1
12. DOGMA attempts:13 score:4
13. ADULT attempts:10 score:1
14. FREED attempts:17 score:0
15. WROTE attempts:7 score:0
16. VOMIT attempts:3 score:7

# [squareword.org](squareword.org) 🧩 #1739 🥳 8 ⏱️ 0:02:06.676505

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B L A M E
    A L L O W
    N A I V E
    A M B E R
    L A I R S
