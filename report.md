# 2026-04-22

- 🔗 spaceword.org 🧩 2026-04-21 🏁 score 2173 ranked 12.5% 43/344 ⏱️ 3:12:11.470824
- 🔗 alfagok.diginaut.net 🧩 #536 🥳 50 ⏱️ 0:01:10.671543
- 🔗 alphaguess.com 🧩 #1003 🥳 40 ⏱️ 0:00:37.271743
- 🔗 dontwordle.com 🧩 #1429 🥳 6 ⏱️ 0:01:17.767524
- 🔗 dictionary.com hurdle 🧩 #1572 🥳 16 ⏱️ 0:02:22.328339
- 🔗 Quordle Classic 🧩 #1549 🥳 score:20 ⏱️ 0:02:35.361127
- 🔗 Octordle Classic 🧩 #1549 😦 score:74 ⏱️ 0:04:51.162540
- 🔗 squareword.org 🧩 #1542 🥳 9 ⏱️ 0:03:04.345161
- 🔗 cemantle.certitudes.org 🧩 #1479 🥳 148 ⏱️ 0:01:48.720821
- 🔗 cemantix.certitudes.org 🧩 #1512 🥳 194 ⏱️ 0:02:07.682230

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




















































# [spaceword.org](spaceword.org) 🧩 2026-04-21 🏁 score 2173 ranked 12.5% 43/344 ⏱️ 3:12:11.470824

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 43/344

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ O _ J _ _ _ E A T   
      _ D I A R Y _ G U Y   
      _ D _ R E E V O K E   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #536 🥳 50 ⏱️ 0:01:10.671543

🤔 50 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+199605 [199605] lij       q0  ? ␅
    @+199605 [199605] lij       q1  ? after
    @+199605 [199605] lij       q2  ? ␅
    @+199605 [199605] lij       q3  ? after
    @+199605 [199605] lij       q4  ? ␅
    @+199605 [199605] lij       q5  ? after
    @+199605 [199605] lij       q6  ? ␅
    @+199605 [199605] lij       q7  ? after
    @+199869 [199869] lijn      q46 ? ␅
    @+199869 [199869] lijn      q47 ? after
    @+199869 [199869] lijn      q48 ? ␅
    @+199869 [199869] lijn      q49 ? it
    @+199869 [199869] lijn      done. it
    @+200101 [200101] lik       q44 ? ␅
    @+200101 [200101] lik       q45 ? before
    @+200871 [200871] lis       q38 ? ␅
    @+200871 [200871] lis       q39 ? before
    @+202018 [202018] loo       q34 ? ␅
    @+202018 [202018] loo       q35 ? before
    @+205161 [205161] ma        q32 ? ␅
    @+205161 [205161] ma        q33 ? before
    @+210840 [210840] mazzelden q30 ? ␅
    @+210840 [210840] mazzelden q31 ? before
    @+211609 [211609] mdccxlv   q23 ? ^
    @+211609 [211609] mdccxlv   q24 ? ␅
    @+211609 [211609] mdccxlv   q25 ? ^
    @+211609 [211609] mdccxlv   q26 ? ␅
    @+211609 [211609] mdccxlv   q27 ? after
    @+211609 [211609] mdccxlv   q28 ? ␅
    @+211609 [211609] mdccxlv   q29 ? .

# [alphaguess.com](alphaguess.com) 🧩 #1003 🥳 40 ⏱️ 0:00:37.271743

🤔 40 attempts
📜 1 sessions

    @        [     0] aa        
    @+98216  [ 98216] mach      q0  ? ␅
    @+98216  [ 98216] mach      q1  ? after
    @+98216  [ 98216] mach      q2  ? ␅
    @+98216  [ 98216] mach      q3  ? after
    @+98216  [ 98216] mach      q4  ? ␅
    @+98216  [ 98216] mach      q5  ? after
    @+147366 [147366] rhotic    q6  ? ␅
    @+147366 [147366] rhotic    q7  ? after
    @+153315 [153315] sea       q12 ? ␅
    @+153315 [153315] sea       q13 ? after
    @+156351 [156351] ship      q14 ? ␅
    @+156351 [156351] ship      q15 ? after
    @+157115 [157115] shrub     q18 ? ␅
    @+157115 [157115] shrub     q19 ? after
    @+157260 [157260] si        q20 ? ␅
    @+157260 [157260] si        q21 ? after
    @+157552 [157552] sight     q22 ? ␅
    @+157552 [157552] sight     q23 ? after
    @+157716 [157716] silesia   q24 ? ␅
    @+157716 [157716] silesia   q25 ? after
    @+157788 [157788] sill      q26 ? ␅
    @+157788 [157788] sill      q27 ? after
    @+157797 [157797] silliest  q32 ? ␅
    @+157797 [157797] silliest  q33 ? after
    @+157801 [157801] silliness q34 ? ␅
    @+157801 [157801] silliness q35 ? after
    @+157803 [157803] sills     q36 ? ␅
    @+157803 [157803] sills     q37 ? after
    @+157804 [157804] silly     q39 ? it
    @+157804 [157804] silly     done. it

# [dontwordle.com](dontwordle.com) 🧩 #1429 🥳 6 ⏱️ 0:01:17.767524

📜 1 sessions
💰 score: 21

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:JUJUS n n n n n remain:5557
    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:2829
    ⬜⬜⬜⬜⬜ tried:TWEET n n n n n remain:747
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:282
    ⬜🟩⬜⬜⬜ tried:BOFFO n Y n n n remain:36
    🟨🟩⬜⬜⬜ tried:MORPH m Y n n n remain:3

    Undos used: 2

      3 words remaining
    x 7 unused letters
    = 21 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1572 🥳 16 ⏱️ 0:02:22.328339

📜 1 sessions
💰 score: 10000

    3/6
    LASER 🟩🟩⬜🟩⬜
    LATED 🟩🟩⬜🟩🟨
    LADEN 🟩🟩🟩🟩🟩
    3/6
    LADEN 🟨🟨🟨⬜⬜
    DOULA 🟨⬜🟩🟩🟨
    ADULT 🟩🟩🟩🟩🟩
    4/6
    ADULT ⬜🟨⬜⬜⬜
    SIRED ⬜⬜🟩🟨🟨
    DERBY 🟨🟩🟩⬜🟩
    NERDY 🟩🟩🟩🟩🟩
    4/6
    NERDY 🟨⬜🟨⬜⬜
    GROAN 🟨🟩⬜⬜🟨
    BRUNG ⬜🟩⬜🟩🟩
    WRING 🟩🟩🟩🟩🟩
    Final 2/2
    SEXER ⬜🟩⬜🟩🟩
    FEVER 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1549 🥳 score:20 ⏱️ 0:02:35.361127

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. WEEDY attempts:4 score:4
2. OMEGA attempts:6 score:6
3. CLEFT attempts:3 score:3
4. GAVEL attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1549 😦 score:74 ⏱️ 0:04:51.162540

📜 2 sessions

Octordle Classic

1. PIXIE attempts:5 score:5
2. DAUNT attempts:6 score:6
3. SAUTE attempts:7 score:7
4. OVOID attempts:8 score:8
5. HEDGE attempts:13 score:13
6. PETTY attempts:3 score:-1
7. FLECK attempts:10 score:10
8. ADOBE attempts:11 score:11

# [squareword.org](squareword.org) 🧩 #1542 🥳 9 ⏱️ 0:03:04.345161

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟨 🟨 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A B B O T
    G R A P E
    L A S T S
    O C T E T
    W E E D Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1479 🥳 148 ⏱️ 0:01:48.720821

🤔 149 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 42 chat prompts
🤖 42 dolphin3:latest replies
😱   1 🔥   1 🥵  10 😎  20 🥶 101 🧊  15

      $1 #149 authorize       100.00°C 🥳 1000‰ ~134 used:0  [133]  source:dolphin3
      $2 #107 approve          67.56°C 😱  999‰   ~1 used:22 [0]    source:dolphin3
      $3 #103 endorse          44.78°C 🔥  992‰   ~6 used:14 [5]    source:dolphin3
      $4 #110 allow            43.20°C 🥵  989‰  ~10 used:5  [9]    source:dolphin3
      $5  #96 propose          40.69°C 🥵  983‰  ~11 used:5  [10]   source:dolphin3
      $6 #113 certify          40.45°C 🥵  982‰   ~7 used:2  [6]    source:dolphin3
      $7  #99 recommend        37.39°C 🥵  965‰   ~8 used:2  [7]    source:dolphin3
      $8 #139 ratify           37.27°C 🥵  962‰   ~2 used:1  [1]    source:dolphin3
      $9  #70 resolution       36.90°C 🥵  961‰  ~27 used:18 [26]   source:dolphin3
     $10 #118 permit           35.48°C 🥵  949‰   ~3 used:1  [2]    source:dolphin3
     $11 #119 sanction         34.56°C 🥵  942‰   ~4 used:1  [3]    source:dolphin3
     $14  #81 decide           31.50°C 😎  899‰  ~32 used:6  [31]   source:dolphin3
     $34  #52 judgment         19.65°C 🥶        ~35 used:4  [34]   source:dolphin3
    $135  #17 innovation       -0.41°C 🧊       ~135 used:0  [134]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1512 🥳 194 ⏱️ 0:02:07.682230

🤔 195 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 29 chat prompts
🤖 29 dolphin3:latest replies
😱  1 🔥  1 🥵  4 😎 12 🥶 96 🧊 80

      $1 #195 magazine         100.00°C 🥳 1000‰ ~115 used:0  [114]  source:dolphin3
      $2 #193 journal           62.09°C 😱  999‰   ~1 used:0  [0]    source:dolphin3
      $3 #185 revue             52.74°C 🔥  995‰   ~2 used:1  [1]    source:dolphin3
      $4 #192 gazette           37.03°C 🥵  965‰   ~3 used:0  [2]    source:dolphin3
      $5 #194 journaliste       36.03°C 🥵  958‰   ~4 used:0  [3]    source:dolphin3
      $6 #191 édition           35.61°C 🥵  957‰   ~5 used:0  [4]    source:dolphin3
      $7 #180 livre             32.49°C 🥵  933‰   ~6 used:0  [5]    source:dolphin3
      $8 #163 collection        27.11°C 😎  842‰  ~15 used:2  [14]   source:dolphin3
      $9 #170 salon             24.57°C 😎  752‰   ~7 used:1  [6]    source:dolphin3
     $10  #77 festival          21.32°C 😎  604‰  ~17 used:19 [16]   source:dolphin3
     $11 #178 design            20.12°C 😎  523‰   ~8 used:0  [7]    source:dolphin3
     $12 #175 automobile        17.95°C 😎  332‰   ~9 used:0  [8]    source:dolphin3
     $20 #130 aventure          15.17°C 🥶        ~24 used:0  [23]   source:dolphin3
    $116  #44 tendresse         -0.01°C 🧊       ~116 used:0  [115]  source:dolphin3
