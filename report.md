# 2026-11-02

- 🔗 spaceword.org 🧩 2026-11-01 🏁 score 2168 ranked 38.0% 104/274 ⏱️ 1:09:28.595911
- 🔗 wordgrid 🧩 #884 🟪 rarity:0.26 ⏱️ 0:03:43.360708
- 🔗 alfagok.diginaut.net 🧩 #730 🥳 40 ⏱️ 0:00:57.277305
- 🔗 alphaguess.com 🧩 #1197 🥳 34 ⏱️ 0:00:37.668114
- 🔗 dontwordle.com 🧩 #1623 🥳 6 ⏱️ 0:01:22.337716
- 🔗 dictionary.com hurdle 🧩 #1766 🥳 16 ⏱️ 0:03:09.948352
- 🔗 Quordle Classic 🧩 #1743 🥳 score:21 ⏱️ 0:01:36.297936
- 🔗 Octordle Classic 🧩 #1743 🥳 score:59 ⏱️ 0:01:43.672389
- 🔗 Sedecordle Classic 🧩 #1723 🥳 score:40 ⏱️ 0:02:43.444693
- 🔗 squareword.org 🧩 #1736 🥳 8 ⏱️ 0:02:39.815003
- 🔗 cemantle.certitudes.org 🧩 #1673 🥳 69 ⏱️ 0:02:34.209174
- 🔗 cemantix.certitudes.org 🧩 #1706 🥳 186 ⏱️ 0:01:27.984901

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
























# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 2026-10-27 🤔 rarity:nan ⏱️ 0:01:43.563056

📜 1 sessions
🌌 🌌 🦄
🌌 🌌 🌌
🦄 🦄 🦄





# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 2026-10-31 🤔 rarity:nan ⏱️ 1:15:11.193607

📜 2 sessions
🌌 🌌 🌌
🌌 🦄 🦄
🦄 🦄 🌌


# [spaceword.org](spaceword.org) 🧩 2026-11-01 🏁 score 2168 ranked 38.0% 104/274 ⏱️ 1:09:28.595911

📜 2 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 104/274

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ O U T _ _ _ _   
      _ _ _ I _ A _ _ _ _   
      _ _ _ L I R E _ _ _   
      _ _ _ _ C O X _ _ _   
      _ _ _ _ K _ _ _ _ _   
      _ _ _ V I T A _ _ _   
      _ _ _ _ L A G _ _ _   
      _ _ _ _ Y _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #884 🟪 rarity:0.26 ⏱️ 0:03:43.360708

📜 2 sessions
🌌 🦄 🌌
🌌 🦄 🌌
🌌 🌌 🌌
Rarity: 0.26 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #730 🥳 40 ⏱️ 0:00:57.277305

🤔 40 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+199631 [199631] lijk        q0  ? ␅
    @+199631 [199631] lijk        q1  ? after
    @+249541 [249541] opi         q4  ? ␅
    @+249541 [249541] opi         q5  ? after
    @+274457 [274457] prop        q6  ? ␅
    @+274457 [274457] prop        q7  ? after
    @+280555 [280555] red         q10 ? ␅
    @+280555 [280555] red         q11 ? after
    @+280909 [280909] redzaamheid q20 ? ␅
    @+280909 [280909] redzaamheid q21 ? after
    @+280912 [280912] ree         q24 ? ␅
    @+280912 [280912] ree         q25 ? after
    @+280919 [280919] reed        q32 ? ␅
    @+280919 [280919] reed        q33 ? after
    @+280923 [280923] reeds       q38 ? ␅
    @+280923 [280923] reeds       q39 ? it
    @+280923 [280923] reeds       done. it
    @+280925 [280925] reef        q30 ? ␅
    @+280925 [280925] reef        q31 ? before
    @+280941 [280941] reek        q28 ? ␅
    @+280941 [280941] reek        q29 ? before
    @+280971 [280971] rees        q26 ? ␅
    @+280971 [280971] rees        q27 ? before
    @+281030 [281030] referentie  q22 ? ␅
    @+281030 [281030] referentie  q23 ? before
    @+281261 [281261] regel       q18 ? ␅
    @+281261 [281261] regel       q19 ? before
    @+282080 [282080] registreer  q16 ? ␅
    @+282080 [282080] registreer  q17 ? before
    @+283612 [283612] rente       q13 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1197 🥳 34 ⏱️ 0:00:37.668114

🤔 34 attempts
📜 1 sessions

    @        [     0] aa        
    @+98139  [ 98139] mac       q0  ? ␅
    @+98139  [ 98139] mac       q1  ? after
    @+98139  [ 98139] mac       q2  ? ␅
    @+98139  [ 98139] mac       q3  ? after
    @+122715 [122715] parol     q6  ? ␅
    @+122715 [122715] parol     q7  ? after
    @+128833 [128833] play      q10 ? ␅
    @+128833 [128833] play      q11 ? after
    @+130047 [130047] poly      q14 ? ␅
    @+130047 [130047] poly      q15 ? after
    @+130512 [130512] pons      q20 ? ␅
    @+130512 [130512] pons      q21 ? after
    @+130548 [130548] poo       q26 ? ␅
    @+130548 [130548] poo       q27 ? after
    @+130573 [130573] pool      q28 ? ␅
    @+130573 [130573] pool      q29 ? after
    @+130589 [130589] poop      q30 ? ␅
    @+130589 [130589] poop      q31 ? after
    @+130596 [130596] poor      q32 ? ␅
    @+130596 [130596] poor      q33 ? it
    @+130596 [130596] poor      done. it
    @+130616 [130616] pop       q24 ? ␅
    @+130616 [130616] pop       q25 ? before
    @+130744 [130744] poriferal q22 ? ␅
    @+130744 [130744] poriferal q23 ? before
    @+130975 [130975] possess   q16 ? ␅
    @+130975 [130975] possess   q17 ? before
    @+131913 [131913] prealter  q12 ? ␅
    @+131913 [131913] prealter  q13 ? before
    @+134993 [134993] prop      q9  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1623 🥳 6 ⏱️ 0:01:22.337716

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:KOOKS n n n n n remain:4279
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:2335
    ⬜⬜⬜⬜⬜ tried:ADDAX n n n n n remain:654
    ⬜⬜⬜⬜⬜ tried:YUMMY n n n n n remain:235
    🟨⬜⬜⬜⬜ tried:GRRRL m n n n n remain:13
    🟨⬜⬜🟨🟨 tried:ICING m n n m m remain:3

    Undos used: 4

      3 words remaining
    x 8 unused letters
    = 24 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1766 🥳 16 ⏱️ 0:03:09.948352

📜 1 sessions
💰 score: 10000

    3/6
    STARE ⬜🟨⬜⬜⬜
    YOUTH ⬜⬜🟨🟨⬜
    UNTIL 🟩🟩🟩🟩🟩
    4/6
    UNTIL ⬜⬜⬜⬜⬜
    ORCAS ⬜🟩🟨🟨⬜
    CRAKE 🟩🟩🟩⬜⬜
    CRAMP 🟩🟩🟩🟩🟩
    4/6
    CRAMP ⬜⬜🟨⬜🟨
    SEPAL ⬜⬜🟨🟨⬜
    PAINT 🟨🟨⬜⬜🟩
    ADOPT 🟩🟩🟩🟩🟩
    4/6
    ADOPT 🟨⬜⬜🟨🟨
    TAPES 🟨🟨🟨⬜🟨
    STAMP 🟩🟩🟨⬜🟩
    STRAP 🟩🟩🟩🟩🟩
    Final 1/2
    AFOUL 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1743 🥳 score:21 ⏱️ 0:01:36.297936

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. EXTRA attempts:5 score:5
2. AMITY attempts:6 score:6
3. LUPUS attempts:7 score:7
4. EAGLE attempts:3 score:3

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1743 🥳 score:59 ⏱️ 0:01:43.672389

📜 1 sessions

Octordle Classic

1. SOOTH attempts:9 score:9
2. APHID attempts:5 score:5
3. GRAIN attempts:11 score:11
4. SPIRE attempts:8 score:8
5. POUND attempts:6 score:6
6. UNCUT attempts:10 score:10
7. ANGER attempts:3 score:3
8. GODLY attempts:7 score:7

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1723 🥳 score:40 ⏱️ 0:02:43.444693

📜 1 sessions

Sedecordle Classic sedecordle.com

1. FORUM attempts:6 score:0
2. FLOAT attempts:7 score:6
3. JAZZY attempts:17 score:1
4. MYRRH attempts:5 score:7
5. BUTTE attempts:11 score:1
6. SHOOT attempts:8 score:1
7. SHADY attempts:4 score:0
8. BEING attempts:14 score:4
9. DROIT attempts:10 score:1
10. GROOM attempts:16 score:0
11. LIEGE attempts:15 score:1
12. BOTCH attempts:12 score:5
13. STINT attempts:18 score:1
14. TARDY attempts:3 score:8
15. BLAZE attempts:13 score:1
16. BATCH attempts:18 score:3

# [squareword.org](squareword.org) 🧩 #1736 🥳 8 ⏱️ 0:02:39.815003

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟨 🟨 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S H E L F
    N O V A E
    E R O D E
    A S K E D
    K E E N S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1673 🥳 69 ⏱️ 0:02:34.209174

🤔 70 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 10 chat prompts
🤖 10 nemotron-3-nano:30b-cloud replies
😎  7 🥶 62

     $1 #70 fossil         100.00°C 🥳 1000‰ ~70 used:0 [69]  source:nemotron
     $2 #41 carbon          39.81°C 😎  818‰  ~1 used:1 [0]   source:nemotron
     $3 #43 conservation    35.00°C 😎  606‰  ~2 used:0 [1]   source:nemotron
     $4 #49 habitat         34.74°C 😎  579‰  ~3 used:0 [2]   source:nemotron
     $5 #40 biodiversity    34.53°C 😎  566‰  ~4 used:0 [3]   source:nemotron
     $6 #54 renewable       32.03°C 😎  363‰  ~5 used:0 [4]   source:nemotron
     $7 #67 wildlife        30.91°C 😎  231‰  ~6 used:0 [5]   source:nemotron
     $8 #38 deforestation   30.06°C 😎  119‰  ~7 used:1 [6]   source:nemotron
     $9 #15 forest          29.15°C 🥶        ~8 used:4 [7]   source:nemotron
    $10 #69 emission        26.77°C 🥶       ~12 used:0 [11]  source:nemotron
    $11 #14 wood            25.99°C 🥶        ~9 used:4 [8]   source:nemotron
    $12 #23 timber          24.59°C 🥶       ~10 used:3 [9]   source:nemotron
    $13 #25 forestry        24.47°C 🥶       ~11 used:2 [10]  source:nemotron
    $14 #58 warming         24.22°C 🥶       ~13 used:0 [12]  source:nemotron

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1706 🥳 186 ⏱️ 0:01:27.984901

🤔 187 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 32 chat prompts
🤖 32 nemotron-3-nano:30b-cloud replies
🔥   2 🥵   4 😎  25 🥶 105 🧊  50

      $1 #187 rassemblement    100.00°C 🥳 1000‰ ~137 used:0  [136]  source:nemotron
      $2 #184 manifestation     56.09°C 😱  999‰   ~1 used:0  [0]    source:nemotron
      $3 #186 mobilisation      50.39°C 🔥  997‰   ~2 used:0  [1]    source:nemotron
      $4 #162 manifester        40.69°C 🥵  988‰   ~5 used:3  [4]    source:nemotron
      $5 #181 mouvement         34.69°C 🥵  951‰   ~4 used:2  [3]    source:nemotron
      $6 #169 revendication     34.10°C 🥵  943‰   ~3 used:1  [2]    source:nemotron
      $7  #82 débat             32.85°C 🥵  933‰  ~22 used:17 [21]   source:nemotron
      $8  #70 affrontement      28.90°C 😎  878‰  ~30 used:9  [29]   source:nemotron
      $9 #157 conviction        28.39°C 😎  866‰   ~6 used:0  [5]    source:nemotron
     $10 #134 opposition        28.17°C 😎  859‰  ~28 used:4  [27]   source:nemotron
     $11 #147 combat            28.01°C 😎  856‰  ~23 used:2  [22]   source:nemotron
     $12 #159 engagement        26.37°C 😎  807‰   ~7 used:0  [6]    source:nemotron
     $33 #136 querelle          16.99°C 🥶        ~39 used:0  [38]   source:nemotron
    $138  #88 approche          -0.38°C 🧊       ~138 used:0  [137]  source:nemotron
