# 2026-11-19

- 🔗 wordgrid 🧩 #901 🟪 rarity:0.19 ⏱️ 0:03:20.272815
- 🔗 spaceword.org 🧩 2026-11-18 🏁 score 2165 ranked 45.6% 130/285 ⏱️ 11:54:09.476345
- 🔗 alfagok.diginaut.net 🧩 #747 🥳 44 ⏱️ 0:01:16.220189
- 🔗 alphaguess.com 🧩 #1214 🥳 42 ⏱️ 0:00:41.458899
- 🔗 dontwordle.com 🧩 #1640 🥳 6 ⏱️ 0:01:19.601130
- 🔗 dictionary.com hurdle 🧩 #1783 🥳 16 ⏱️ 0:02:54.209840
- 🔗 Quordle Classic 🧩 #1760 🥳 score:23 ⏱️ 0:01:38.121677
- 🔗 Octordle Classic 🧩 #1760 🥳 score:59 ⏱️ 0:01:43.414531
- 🔗 Sedecordle Classic 🧩 #1740 🥳 score:44 ⏱️ 0:03:23.912815
- 🔗 squareword.org 🧩 #1753 🥳 6 ⏱️ 0:01:44.959247
- 🔗 cemantle.certitudes.org 🧩 #1690 🥳 114 ⏱️ 0:00:31.144155
- 🔗 cemantix.certitudes.org 🧩 #1723 🥳 270 ⏱️ 0:02:21.877289

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











# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #901 🟪 rarity:0.19 ⏱️ 0:03:20.272815

📜 2 sessions
🌌 🌌 🌌
🌌 🌌 🦄
🦄 🌌 🌌
Rarity: 0.19 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-18 🏁 score 2165 ranked 45.6% 130/285 ⏱️ 11:54:09.476345

📜 1 sessions
- tiles: 21/21
- score: 2165 bonus: +65
- rank: 130/285

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ V I G A _ _ _ _ _   
      _ _ N O S E Y _ _ _   
      _ _ P _ _ _ U T _ _   
      _ _ U _ _ _ K I _ _   
      _ _ T O Q U E T _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #747 🥳 44 ⏱️ 0:01:16.220189

🤔 44 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+199628 [199628] lijk        q0  ? ␅
    @+199628 [199628] lijk        q1  ? after
    @+212011 [212011] media       q8  ? ␅
    @+212011 [212011] media       q9  ? after
    @+217767 [217767] milieu      q10 ? ␅
    @+217767 [217767] milieu      q11 ? after
    @+219407 [219407] mis         q14 ? ␅
    @+219407 [219407] mis         q15 ? after
    @+219793 [219793] miss        q28 ? ␅
    @+219793 [219793] miss        q29 ? after
    @+219894 [219894] mist        q30 ? ␅
    @+219894 [219894] mist        q31 ? after
    @+219894 [219894] mist        q32 ? ␅
    @+219894 [219894] mist        q33 ? after
    @+220031 [220031] mitra       q38 ? ␅
    @+220031 [220031] mitra       q39 ? after
    @+220037 [220037] mitrailleur q40 ? ␅
    @+220037 [220037] mitrailleur q41 ? after
    @+220049 [220049] mits        q42 ? ␅
    @+220049 [220049] mits        q43 ? it
    @+220049 [220049] mits        done. it
    @+220064 [220064] mix         q36 ? ␅
    @+220064 [220064] mix         q37 ? before
    @+220078 [220078] mixt        q26 ? ␅
    @+220078 [220078] mixt        q27 ? before
    @+220243 [220243] mmcccxxxv   q24 ? ␅
    @+220243 [220243] mmcccxxxv   q25 ? .
    @+221082 [221082] mmm         q12 ? ␅
    @+221082 [221082] mmm         q13 ? before
    @+224505 [224505] moord       q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1214 🥳 42 ⏱️ 0:00:41.458899

🤔 42 attempts
📜 1 sessions

    @       [    0] aa             
    @+49065 [49065] disturb        q6  ? ␅
    @+49065 [49065] disturb        q7  ? after
    @+73596 [73596] guide          q8  ? ␅
    @+73596 [73596] guide          q9  ? after
    @+85489 [85489] ins            q10 ? ␅
    @+85489 [85489] ins            q11 ? after
    @+91802 [91802] knock          q12 ? ␅
    @+91802 [91802] knock          q13 ? after
    @+93253 [93253] lar            q16 ? ␅
    @+93253 [93253] lar            q17 ? after
    @+93881 [93881] lea            q18 ? ␅
    @+93881 [93881] lea            q19 ? after
    @+94415 [94415] lek            q20 ? ␅
    @+94415 [94415] lek            q21 ? after
    @+94544 [94544] leopard        q24 ? ␅
    @+94544 [94544] leopard        q25 ? after
    @+94613 [94613] less           q26 ? ␅
    @+94613 [94613] less           q27 ? after
    @+94630 [94630] let            q28 ? ␅
    @+94630 [94630] let            q29 ? after
    @+94653 [94653] letter         q30 ? ␅
    @+94653 [94653] letter         q31 ? after
    @+94667 [94667] letterings     q32 ? ␅
    @+94667 [94667] letterings     q33 ? after
    @+94672 [94672] letters        q34 ? ␅
    @+94672 [94672] letters        q35 ? after
    @+94674 [94674] letterspacings q38 ? ␅
    @+94674 [94674] letterspacings q39 ? after
    @+94675 [94675] letting        q41 ? it
    @+94675 [94675] letting        done. it

# [dontwordle.com](dontwordle.com) 🧩 #1640 🥳 6 ⏱️ 0:01:19.601130

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:FEEZE n n n n n remain:6482
    ⬜⬜⬜⬜⬜ tried:KABAB n n n n n remain:2366
    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:1111
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:414
    ⬜⬜🟩⬜⬜ tried:WRUNG n n Y n n remain:9
    🟨⬜🟩⬜⬜ tried:SCUDS m n Y n n remain:1

    Undos used: 3

      1 words remaining
    x 6 unused letters
    = 6 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1783 🥳 16 ⏱️ 0:02:54.209840

📜 1 sessions
💰 score: 10000

    2/6
    RATES ⬜🟩🟨🟨🟨
    WASTE 🟩🟩🟩🟩🟩
    4/6
    WASTE ⬜⬜🟩⬜⬜
    HUSKY ⬜⬜🟩⬜🟩
    CLIMB ⬜⬜⬜⬜🟨
    BOSSY 🟩🟩🟩🟩🟩
    4/6
    BOSSY ⬜⬜🟨⬜⬜
    ASTER 🟨🟨🟨🟨⬜
    STALE 🟩🟨🟩🟨🟩
    SLATE 🟩🟩🟩🟩🟩
    5/6
    SLATE ⬜⬜⬜⬜🟩
    BRINE ⬜🟨⬜⬜🟩
    PURGE ⬜⬜🟩⬜🟩
    CHILD ⬜⬜⬜⬜⬜
    VERVE 🟩🟩🟩🟩🟩
    Final 1/2
    SETUP 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1760 🥳 score:23 ⏱️ 0:01:38.121677

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. GREEN attempts:5 score:5
2. COCOA attempts:8 score:8
3. ROWDY attempts:4 score:4
4. ALIBI attempts:6 score:6

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1760 🥳 score:59 ⏱️ 0:01:43.414531

📜 1 sessions

Octordle Classic

1. ANGER attempts:10 score:10
2. GODLY attempts:9 score:9
3. MURKY attempts:5 score:5
4. ACTOR attempts:3 score:3
5. GUAVA attempts:8 score:8
6. DEBUG attempts:7 score:7
7. SPICE attempts:11 score:11
8. TIMER attempts:6 score:6

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1740 🥳 score:44 ⏱️ 0:03:23.912815

📜 1 sessions

Sedecordle Classic sedecordle.com

1. SQUIB attempts:14 score:1
2. WAGER attempts:18 score:4
3. RIVET attempts:15 score:1
4. DADDY attempts:12 score:5
5. ALPHA attempts:7 score:0
6. WRING attempts:17 score:7
7. FUNKY attempts:13 score:1
8. SLEPT attempts:9 score:3
9. AORTA attempts:3 score:0
10. RABBI attempts:16 score:3
11. GHOUL attempts:10 score:1
12. ORGAN attempts:6 score:0
13. SLOPE attempts:8 score:0
14. SHELF attempts:11 score:8
15. MOIST attempts:19 score:1
16. KAYAK attempts:5 score:9

# [squareword.org](squareword.org) 🧩 #1753 🥳 6 ⏱️ 0:01:44.959247

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    H A T E R
    A B O D E
    R A N G E
    S T E E L
    H E R D S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1690 🥳 114 ⏱️ 0:00:31.144155

🤔 115 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 18 chat prompts
🤖 18 glm-5.3-flash:cloud replies
🔥  1 🥵  7 😎 26 🥶 72 🧊  8

      $1 #115 laugh         100.00°C 🥳 1000‰ ~107 used:0 [106]  source:glm
      $2  #70 funny          62.87°C 🔥  996‰   ~1 used:8 [0]    source:glm
      $3  #96 goofy          51.43°C 🥵  979‰   ~7 used:2 [6]    source:glm
      $4 #111 deadpan        48.62°C 🥵  971‰   ~2 used:0 [1]    source:glm
      $5  #72 hilarious      48.38°C 🥵  967‰   ~8 used:3 [7]    source:glm
      $6  #87 silly          46.88°C 🥵  956‰   ~3 used:1 [2]    source:glm
      $7  #63 humorous       46.02°C 🥵  944‰   ~4 used:1 [3]    source:glm
      $8  #94 facetious      44.84°C 🥵  928‰   ~5 used:0 [4]    source:glm
      $9  #71 comical        43.73°C 🥵  910‰   ~6 used:0 [5]    source:glm
     $10 #113 jesting        42.86°C 😎  899‰   ~9 used:0 [8]    source:glm
     $11  #55 lighthearted   42.35°C 😎  890‰  ~33 used:2 [32]   source:glm
     $12  #59 amusing        42.27°C 😎  889‰  ~10 used:0 [9]    source:glm
     $36  #76 tickling       31.34°C 🥶        ~37 used:0 [36]   source:glm
    $108 #106 adjacent       -0.67°C 🧊       ~108 used:0 [107]  source:glm

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1723 🥳 270 ⏱️ 0:02:21.877289

🤔 271 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 52 chat prompts
🤖 52 glm-5.3-flash:cloud replies
🔥   2 🥵  14 😎  69 🥶 163 🧊  22

      $1 #271 continental      100.00°C 🥳 1000‰ ~249 used:0  [248]  source:glm
      $2 #263 océanique         49.23°C 🔥  998‰   ~1 used:0  [0]    source:glm
      $3 #216 orogenèse         45.21°C 🔥  994‰   ~5 used:13 [4]    source:glm
      $4 #232 graben            43.12°C 🥵  989‰   ~9 used:5  [8]    source:glm
      $5  #81 sédimentaire      41.87°C 🥵  984‰  ~83 used:39 [82]   source:glm
      $6 #222 lithosphère       41.05°C 🥵  978‰   ~6 used:2  [5]    source:glm
      $7  #90 détritique        40.44°C 🥵  974‰  ~82 used:22 [81]   source:glm
      $8 #200 pléistocène       40.02°C 🥵  972‰   ~8 used:3  [7]    source:glm
      $9 #225 subduction        38.68°C 🥵  956‰   ~2 used:1  [1]    source:glm
     $10  #79 périglaciaire     38.52°C 🥵  954‰  ~79 used:11 [78]   source:glm
     $11 #147 lacustre          38.46°C 🥵  952‰  ~13 used:7  [12]   source:glm
     $18 #135 interglaciaire    35.15°C 😎  895‰  ~14 used:0  [13]   source:glm
     $87 #127 torrentiel        22.32°C 🥶        ~89 used:0  [88]   source:glm
    $250 #188 méandre           -0.10°C 🧊       ~250 used:0  [249]  source:glm
