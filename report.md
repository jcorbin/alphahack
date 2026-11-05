# 2026-11-06

- 🔗 wordgrid 🧩 #888 🟪 rarity:0.14 ⏱️ 0:06:16.140448
- 🔗 spaceword.org 🧩 2026-11-05 🏁 score 2173 ranked 5.2% 15/286 ⏱️ 2:40:58.702248
- 🔗 alfagok.diginaut.net 🧩 #734 🥳 32 ⏱️ 0:00:41.275580
- 🔗 alphaguess.com 🧩 #1201 🥳 28 ⏱️ 0:00:34.711608
- 🔗 dontwordle.com 🧩 #1627 🥳 6 ⏱️ 0:02:02.391995
- 🔗 dictionary.com hurdle 🧩 #1770 🥳 21 ⏱️ 0:03:30.659352
- 🔗 Quordle Classic 🧩 #1747 🥳 score:26 ⏱️ 0:01:59.734468
- 🔗 Octordle Classic 🧩 #1747 🥳 score:62 ⏱️ 0:02:28.866379
- 🔗 Sedecordle Classic 🧩 #1727 🥳 score:44 ⏱️ 0:03:05.311672
- 🔗 squareword.org 🧩 #1740 🥳 7 ⏱️ 0:01:35.555892
- 🔗 cemantle.certitudes.org 🧩 #1677 🥳 55 ⏱️ 0:00:15.403811
- 🔗 cemantix.certitudes.org 🧩 #1710 🥳 266 ⏱️ 0:01:52.840037

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






# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #888 🟪 rarity:0.14 ⏱️ 0:06:16.140448

📜 4 sessions
🌌 🌌 🌌
🦄 🦄 🌌
🦄 🦄 🌌
Rarity: 0.14 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-05 🏁 score 2173 ranked 5.2% 15/286 ⏱️ 2:40:58.702248

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 15/286

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ G _ F A C T U A L   
      _ A J I _ R _ _ N O   
      _ L _ Z O U A V E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   




# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #734 🥳 32 ⏱️ 0:00:41.275580

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+49802  [ 49802] boks      q6  ? ␅
    @+49802  [ 49802] boks      q7  ? after
    @+74698  [ 74698] dc        q8  ? ␅
    @+74698  [ 74698] dc        q9  ? after
    @+77670  [ 77670] der       q14 ? ␅
    @+77670  [ 77670] der       q15 ? after
    @+78413  [ 78413] detentie  q18 ? ␅
    @+78413  [ 78413] detentie  q19 ? after
    @+78557  [ 78557] deur      q22 ? ␅
    @+78557  [ 78557] deur      q23 ? after
    @+78677  [ 78677] deuterium q24 ? ␅
    @+78677  [ 78677] deuterium q25 ? after
    @+78728  [ 78728] deviezen  q26 ? ␅
    @+78728  [ 78728] deviezen  q27 ? after
    @+78761  [ 78761] devoties  q28 ? ␅
    @+78761  [ 78761] devoties  q29 ? after
    @+78777  [ 78777] deze      q30 ? ␅
    @+78777  [ 78777] deze      q31 ? it
    @+78777  [ 78777] deze      done. it
    @+78794  [ 78794] dia       q20 ? ␅
    @+78794  [ 78794] dia       q21 ? before
    @+79172  [ 79172] dicht     q16 ? ␅
    @+79172  [ 79172] dicht     q17 ? before
    @+80830  [ 80830] dijk      q12 ? ␅
    @+80830  [ 80830] dijk      q13 ? before
    @+87156  [ 87156] draag     q10 ? ␅
    @+87156  [ 87156] draag     q11 ? before
    @+99672  [ 99672] ex        q4  ? ␅
    @+99672  [ 99672] ex        q5  ? before
    @+199631 [199631] lijk      q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1201 🥳 28 ⏱️ 0:00:34.711608

🤔 28 attempts
📜 1 sessions

    @       [    0] aa      
    @+2     [    2] aahed   
    @+49066 [49066] disturb q2  ? ␅
    @+49066 [49066] disturb q3  ? after
    @+51987 [51987] dusk    q10 ? ␅
    @+51987 [51987] dusk    q11 ? after
    @+52688 [52688] eco     q14 ? ␅
    @+52688 [52688] eco     q15 ? after
    @+52865 [52865] ed      q18 ? ␅
    @+52865 [52865] ed      q19 ? after
    @+52881 [52881] edema   q24 ? ␅
    @+52881 [52881] edema   q25 ? after
    @+52890 [52890] edge    q26 ? ␅
    @+52890 [52890] edge    q27 ? it
    @+52890 [52890] edge    done. it
    @+52899 [52899] edgiest q22 ? ␅
    @+52899 [52899] edgiest q23 ? before
    @+52932 [52932] edit    q20 ? ␅
    @+52932 [52932] edit    q21 ? before
    @+53049 [53049] effect  q16 ? ␅
    @+53049 [53049] effect  q17 ? before
    @+53442 [53442] elater  q12 ? ␅
    @+53442 [53442] elater  q13 ? before
    @+54908 [54908] end     q8  ? ␅
    @+54908 [54908] end     q9  ? before
    @+61317 [61317] federal q6  ? ␅
    @+61317 [61317] federal q7  ? before
    @+73597 [73597] guide   q4  ? ␅
    @+73597 [73597] guide   q5  ? before
    @+98139 [98139] mac     q0  ? ␅
    @+98139 [98139] mac     q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1627 🥳 6 ⏱️ 0:02:02.391995

📜 1 sessions
💰 score: 72

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:7266
    ⬜⬜⬜⬜⬜ tried:HEEZE n n n n n remain:2896
    ⬜⬜⬜⬜⬜ tried:WANNA n n n n n remain:868
    ⬜⬜⬜⬜⬜ tried:TOOTS n n n n n remain:79
    ⬜⬜⬜⬜🟨 tried:GRRRL n n n n m remain:15
    ⬜🟨🟨⬜⬜ tried:FLUFF n m m n n remain:8

    Undos used: 4

      8 words remaining
    x 9 unused letters
    = 72 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1770 🥳 21 ⏱️ 0:03:30.659352

📜 1 sessions
💰 score: 9500

    4/6
    SERAI ⬜🟩⬜⬜⬜
    VELDT ⬜🟩⬜⬜🟨
    TENCH 🟨🟩⬜🟩🟩
    FETCH 🟩🟩🟩🟩🟩
    6/6
    FETCH ⬜⬜🟨⬜🟨
    SHOUT ⬜🟨⬜⬜🟩
    HABIT 🟨⬜⬜🟨🟩
    DWELT ⬜⬜⬜⬜🟩
    MANOR 🟩⬜⬜⬜⬜
    MIGHT 🟩🟩🟩🟩🟩
    6/6
    MIGHT ⬜⬜⬜⬜⬜
    SNARE ⬜⬜⬜🟨🟨
    BORED ⬜🟩🟨🟩⬜
    POWER ⬜🟩🟩🟩🟩
    CAROL ⬜⬜🟨🟨🟨
    LOWER 🟩🟩🟩🟩🟩
    4/6
    LOWER ⬜⬜⬜🟨⬜
    STEAD 🟩🟩🟩🟩⬜
    STEAK 🟩🟩🟩🟩⬜
    STEAM 🟩🟩🟩🟩🟩
    Final 1/2
    GRUNT 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1747 🥳 score:26 ⏱️ 0:01:59.734468

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. CHARD attempts:9 score:9
2. THORN attempts:4 score:4
3. COVER attempts:6 score:6
4. OUTER attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1747 🥳 score:62 ⏱️ 0:02:28.866379

📜 1 sessions

Octordle Classic

1. WINCH attempts:11 score:11
2. SINGE attempts:12 score:12
3. MAMBO attempts:7 score:7
4. SHEEP attempts:8 score:8
5. IDEAL attempts:3 score:3
6. SMOKY attempts:6 score:6
7. DUVET attempts:10 score:10
8. BELIE attempts:5 score:5

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1727 🥳 score:44 ⏱️ 0:03:05.311672

📜 1 sessions

Sedecordle Classic sedecordle.com

1. TWIST attempts:4 score:0
2. GRAPE attempts:7 score:4
3. PECAN attempts:14 score:1
4. INNER attempts:20 score:4
5. PAPER attempts:19 score:1
6. CRANK attempts:12 score:9
7. TUMOR attempts:8 score:0
8. MUMMY attempts:21 score:8
9. GRAIL attempts:10 score:1
10. CAROL attempts:9 score:0
11. QUIET attempts:3 score:0
12. CRICK attempts:11 score:3
13. RUDDY attempts:15 score:1
14. HERON attempts:13 score:5
15. NICER attempts:16 score:1
16. PROBE attempts:6 score:6

# [squareword.org](squareword.org) 🧩 #1740 🥳 7 ⏱️ 0:01:35.555892

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟩 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B E A R D
    A N G E R
    I R O N Y
    T O N A L
    S L Y L Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1677 🥳 55 ⏱️ 0:00:15.403811

🤔 56 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 9 chat prompts
🤖 9 nemotron-3-nano:30b-cloud replies
🥵  1 😎  4 🥶 47 🧊  3

     $1 #56 relevance       100.00°C 🥳 1000‰ ~53 used:0 [52]  source:nemotron
     $2 #19 context          50.40°C 🥵  987‰  ~1 used:5 [0]   source:nemotron
     $3 #36 semantics        36.95°C 😎  889‰  ~2 used:0 [1]   source:nemotron
     $4 #55 relation         36.89°C 😎  885‰  ~3 used:0 [2]   source:nemotron
     $5 #13 scope            32.87°C 😎  711‰  ~5 used:3 [4]   source:nemotron
     $6 #26 linkage          30.35°C 😎  475‰  ~4 used:1 [3]   source:nemotron
     $7 #46 visibility       26.44°C 🥶        ~8 used:0 [7]   source:nemotron
     $8  #4 function         25.17°C 🥶        ~6 used:4 [5]   source:nemotron
     $9 #51 basis            24.70°C 🥶        ~9 used:0 [8]   source:nemotron
    $10 #33 metadata         24.03°C 🥶       ~10 used:0 [9]   source:nemotron
    $11 #35 recursion        22.58°C 🥶       ~11 used:0 [10]  source:nemotron
    $12  #6 syntax           21.80°C 🥶        ~7 used:4 [6]   source:nemotron
    $13 #48 interpretation   20.31°C 🥶       ~12 used:0 [11]  source:nemotron
    $54 #44 statement        -0.26°C 🧊       ~54 used:0 [53]  source:nemotron

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1710 🥳 266 ⏱️ 0:01:52.840037

🤔 267 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 41 chat prompts
🤖 41 nemotron-3-nano:30b-cloud replies
🥵   6 😎  30 🥶 195 🧊  35

      $1 #267 château        100.00°C 🥳 1000‰ ~232 used:0  [231]  source:nemotron
      $2 #234 orangerie       48.11°C 🥵  983‰  ~29 used:11 [28]   source:nemotron
      $3 #163 jardin          44.86°C 🥵  967‰  ~31 used:24 [30]   source:nemotron
      $4 #228 colombage       42.08°C 🥵  942‰   ~3 used:10 [2]    source:nemotron
      $5 #131 maison          41.62°C 🥵  937‰  ~30 used:14 [29]   source:nemotron
      $6 #223 parc            40.37°C 🥵  922‰   ~2 used:7  [1]    source:nemotron
      $7 #264 tourelle        39.41°C 🥵  904‰   ~1 used:1  [0]    source:nemotron
      $8 #253 promenade       38.56°C 😎  891‰   ~4 used:0  [3]    source:nemotron
      $9 #183 fontaine        36.22°C 😎  836‰  ~32 used:3  [31]   source:nemotron
     $10 #225 bosquet         35.65°C 😎  821‰   ~5 used:1  [4]    source:nemotron
     $11  #73 pierre          35.43°C 😎  817‰  ~36 used:8  [35]   source:nemotron
     $12 #215 étang           34.90°C 😎  794‰   ~6 used:0  [5]    source:nemotron
     $38 #239 girandole       25.48°C 🥶        ~43 used:0  [42]   source:nemotron
    $233  #25 montre          -0.17°C 🧊       ~233 used:0  [232]  source:nemotron
