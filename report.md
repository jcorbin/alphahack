# 2026-09-24

- 🔗 spaceword.org 🧩 2026-09-23 🏁 score 2164 ranked 49.1% 186/379 ⏱️ 0:07:32.101805
- 🔗 wordgrid 🧩 #845 🟪 rarity:0.16 ⏱️ 0:03:53.015584
- 🔗 alfagok.diginaut.net 🧩 #691 🥳 28 ⏱️ 0:01:08.240096
- 🔗 alphaguess.com 🧩 #1158 🥳 26 ⏱️ 0:00:37.198200
- 🔗 dontwordle.com 🧩 #1584 🥳 6 ⏱️ 0:01:22.151359
- 🔗 dictionary.com hurdle 🧩 #1727 😦 19 ⏱️ 0:04:18.735424
- 🔗 Quordle Classic 🧩 #1704 😦 score:29 ⏱️ 0:02:45.971713
- 🔗 Octordle Classic 🧩 #1704 🥳 score:60 ⏱️ 0:02:15.571876
- 🔗 Sedecordle Classic 🧩 #1684 🥳 score:35 ⏱️ 0:03:26.731211
- 🔗 squareword.org 🧩 #1697 🥳 7 ⏱️ 0:02:59.927548
- 🔗 cemantle.certitudes.org 🧩 #1634 🥳 408 ⏱️ 0:18:33.048168
- 🔗 cemantix.certitudes.org 🧩 #1667 🥳 195 ⏱️ 0:02:29.123341

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




# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #845 🟪 rarity:0.16 ⏱️ 0:03:53.015584

📜 3 sessions
🌌 🌌 🌌
🦄 🌌 🌌
🌌 🦄 🌌
Rarity: 0.16 🟪

# [spaceword.org](spaceword.org) 🧩 2026-09-23 🏁 score 2164 ranked 49.1% 186/379 ⏱️ 0:07:32.101805

📜 2 sessions
- tiles: 21/21
- score: 2164 bonus: +64
- rank: 186/379

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ T O E _ _ _   
      _ _ _ V I E D _ _ _   
      _ _ _ _ _ _ I _ _ _   
      _ _ _ _ Q _ F _ _ _   
      _ _ _ _ U _ I _ _ _   
      _ _ _ _ A R C _ _ _   
      _ _ _ _ K Y E _ _ _   
      _ _ _ _ E N _ _ _ _   
      _ _ _ _ _ D _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #691 🥳 28 ⏱️ 0:01:08.240096

🤔 28 attempts
📜 1 sessions

    @        [     0] &-teken       
    @+2      [     2] -cijferig     
    @+99675  [ 99675] ex            q2  ? ␅
    @+99675  [ 99675] ex            q3  ? after
    @+149570 [149570] huishoud      q4  ? ␅
    @+149570 [149570] huishoud      q5  ? after
    @+161954 [161954] jaar          q8  ? ␅
    @+161954 [161954] jaar          q9  ? after
    @+168195 [168195] kanon         q10 ? ␅
    @+168195 [168195] kanon         q11 ? after
    @+168681 [168681] kap           q16 ? ␅
    @+168681 [168681] kap           q17 ? after
    @+168931 [168931] kapitalisatie q20 ? ␅
    @+168931 [168931] kapitalisatie q21 ? after
    @+168953 [168953] kapitein      q26 ? ␅
    @+168953 [168953] kapitein      q27 ? it
    @+168953 [168953] kapitein      done. it
    @+168979 [168979] kapittel      q24 ? ␅
    @+168979 [168979] kapittel      q25 ? before
    @+169036 [169036] kapot         q22 ? ␅
    @+169036 [169036] kapot         q23 ? before
    @+169184 [169184] kar           q18 ? ␅
    @+169184 [169184] kar           q19 ? before
    @+169692 [169692] karton        q14 ? ␅
    @+169692 [169692] karton        q15 ? before
    @+171212 [171212] kennis        q12 ? ␅
    @+171212 [171212] kennis        q13 ? before
    @+174468 [174468] kind          q6  ? ␅
    @+174468 [174468] kind          q7  ? before
    @+199531 [199531] lij           q0  ? ␅
    @+199531 [199531] lij           q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1158 🥳 26 ⏱️ 0:00:37.198200

🤔 26 attempts
📜 1 sessions

    @        [     0] aa         
    @+1      [     1] aah        
    @+2      [     2] aahed      
    @+3      [     3] aahing     
    @+98142  [ 98142] mac        q0  ? ␅
    @+98142  [ 98142] mac        q1  ? after
    @+147306 [147306] rho        q2  ? ␅
    @+147306 [147306] rho        q3  ? after
    @+150202 [150202] sal        q10 ? ␅
    @+150202 [150202] sal        q11 ? after
    @+151722 [151722] scan       q12 ? ␅
    @+151722 [151722] scan       q13 ? after
    @+152514 [152514] scombrid   q14 ? ␅
    @+152514 [152514] scombrid   q15 ? after
    @+152910 [152910] scried     q16 ? ␅
    @+152910 [152910] scried     q17 ? after
    @+153009 [153009] scrotal    q20 ? ␅
    @+153009 [153009] scrotal    q21 ? after
    @+153026 [153026] scrub      q24 ? ␅
    @+153026 [153026] scrub      q25 ? it
    @+153026 [153026] scrub      done. it
    @+153052 [153052] scrum      q22 ? ␅
    @+153052 [153052] scrum      q23 ? before
    @+153107 [153107] scrutinize q18 ? ␅
    @+153107 [153107] scrutinize q19 ? before
    @+153306 [153306] sea        q8  ? ␅
    @+153306 [153306] sea        q9  ? before
    @+159588 [159588] slug       q6  ? ␅
    @+159588 [159588] slug       q7  ? before
    @+171906 [171906] tag        q4  ? ␅
    @+171906 [171906] tag        q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1584 🥳 6 ⏱️ 0:01:22.151359

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:ZIZIT n n n n n remain:6979
    ⬜⬜⬜⬜⬜ tried:PEWEE n n n n n remain:2666
    ⬜⬜⬜⬜⬜ tried:HOOCH n n n n n remain:982
    ⬜⬜⬜⬜⬜ tried:FUDDY n n n n n remain:243
    ⬜⬜⬜⬜🟨 tried:GRRRL n n n n m remain:37
    🟨⬜🟨⬜🟩 tried:LLAMA m n m n Y remain:3

    Undos used: 2

      3 words remaining
    x 8 unused letters
    = 24 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1727 😦 19 ⏱️ 0:04:18.735424

📜 1 sessions
💰 score: 4780

    4/6
    EARLS ⬜⬜🟨⬜🟨
    SPORT 🟩⬜🟩🟩🟨
    DUMKY ⬜⬜⬜🟨⬜
    STORK 🟩🟩🟩🟩🟩
    4/6
    STORK ⬜⬜⬜⬜🟩
    BANJO ⬜⬜⬜⬜⬜
    PULIK ⬜🟨⬜⬜🟩
    CHUCK 🟩🟩🟩🟩🟩
    4/6
    CHUCK ⬜⬜🟩⬜⬜
    TOURS 🟩⬜🟩🟨⬜
    DUMPY ⬜🟨⬜⬜⬜
    TRUER 🟩🟩🟩🟩🟩
    5/6
    TRUER 🟩⬜⬜🟨⬜
    TESLA 🟩🟩⬜⬜⬜
    ACING ⬜⬜⬜⬜⬜
    TEMPO 🟩🟩⬜⬜⬜
    TEETH 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜⬜🟩⬜🟨
    ????? 🟩🟩🟩⬜🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1704 😦 score:29 ⏱️ 0:02:45.971713

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. TOPIC attempts:5 score:5
2. METRO attempts:7 score:7
3. __A_P ~CLS -BDEFGIMNORTUW attempts:9 score:-1
4. FREED attempts:8 score:8

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1704 🥳 score:60 ⏱️ 0:02:15.571876

📜 1 sessions

Octordle Classic

1. SNOUT attempts:10 score:10
2. LEASH attempts:3 score:3
3. DITTY attempts:8 score:8
4. CROAK attempts:5 score:5
5. GRAPE attempts:11 score:11
6. CROWD attempts:7 score:7
7. LIPID attempts:12 score:12
8. LIMBO attempts:4 score:4

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1684 🥳 score:35 ⏱️ 0:03:26.731211

📜 1 sessions

Sedecordle Classic sedecordle.com

1. RUDER attempts:6 score:0
2. AGILE attempts:18 score:6
3. REEDY attempts:7 score:0
4. ROTOR attempts:8 score:7
5. SNAKY attempts:10 score:1
6. RIPEN attempts:9 score:0
7. CHEEK attempts:11 score:1
8. BARON attempts:12 score:1
9. CLIFF attempts:13 score:1
10. BASIS attempts:14 score:3
11. SHIRE attempts:3 score:0
12. OVINE attempts:15 score:3
13. LYRIC attempts:4 score:0
14. FLANK attempts:16 score:4
15. BROTH attempts:17 score:1
16. OLDER attempts:18 score:7

# [squareword.org](squareword.org) 🧩 #1697 🥳 7 ⏱️ 0:02:59.927548

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P L A T
    A R O S E
    K O O K S
    I N S E T
    S E E D Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1634 🥳 408 ⏱️ 0:18:33.048168

🤔 409 attempts
📜 2 sessions
🫧 15 chat sessions
⁉️ 75 chat prompts
🤖 69 nemotron-3-nano:30b-cloud replies
🤖 3 nemotron-3-nano:latest replies
🤖 1 gemma4:12b replies
😱   1 🔥   2 🥵  15 😎  57 🥶 311 🧊  22

      $1 #409 proceed          100.00°C 🥳 1000‰ ~387 used:0   [386]  source:nemotron-3-nano:30b   
      $2  #57 proceeding        64.64°C 😱  999‰   ~7 used:105 [6]    source:nemotron-3-nano:30b   
      $3 #222 defer             48.40°C 🔥  994‰  ~15 used:24  [14]   source:nemotron-3-nano:30b   
      $4 #393 postpone          47.85°C 🔥  992‰   ~1 used:7   [0]    source:nemotron-3-nano:30b   
      $5 #179 expedite          46.66°C 🥵  989‰  ~68 used:12  [67]   source:nemotron-3-nano:30b   
      $6 #223 adjourn           42.74°C 🥵  984‰   ~8 used:2   [7]    source:nemotron-3-nano:30b   
      $7 #407 continue          39.16°C 🥵  967‰   ~2 used:0   [1]    source:nemotron-3-nano:30b   
      $8 #346 expeditious       39.12°C 🥵  966‰   ~9 used:2   [8]    source:nemotron-3-nano:30b   
      $9 #260 discontinue       38.64°C 🥵  963‰  ~10 used:2   [9]    source:nemotron-3-nano:30b   
     $10 #271 delay             38.19°C 🥵  959‰  ~11 used:2   [10]   source:nemotron-3-nano:30b   
     $11 #366 suspend           37.46°C 🥵  952‰  ~12 used:2   [11]   source:nemotron-3-nano:30b   
     $20 #202 prosecute         33.28°C 😎  899‰  ~17 used:0   [16]   source:nemotron-3-nano:30b   
     $77 #156 schedule          21.55°C 🥶        ~76 used:0   [75]   source:nemotron-3-nano:30b   
    $388  #63 patriarchal       -0.07°C 🧊       ~388 used:0   [387]  source:nemotron-3-nano:30b   

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1667 🥳 195 ⏱️ 0:02:29.123341

🤔 196 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 40 chat prompts
🤖 40 nemotron-3-nano:30b-cloud replies
🔥   2 🥵   9 😎  31 🥶 125 🧊  28

      $1 #196 légende          100.00°C 🥳 1000‰ ~168 used:0  [167]  source:nemotron
      $2 #193 mythe             53.40°C 🔥  997‰   ~1 used:2  [0]    source:nemotron
      $3 #187 récit             48.72°C 🔥  994‰   ~2 used:4  [1]    source:nemotron
      $4 #194 conte             44.91°C 🥵  988‰   ~3 used:0  [2]    source:nemotron
      $5 #167 allégorique       42.22°C 🥵  980‰   ~5 used:3  [4]    source:nemotron
      $6  #83 mystérieux        42.13°C 🥵  979‰  ~36 used:25 [35]   source:nemotron
      $7 #135 fantastique       40.61°C 🥵  972‰   ~9 used:10 [8]    source:nemotron
      $8  #94 énigmatique       39.41°C 🥵  961‰  ~34 used:11 [33]   source:nemotron
      $9 #127 imaginaire        38.90°C 🥵  955‰   ~6 used:7  [5]    source:nemotron
     $10 #166 allégorie         38.51°C 🥵  948‰   ~4 used:1  [3]    source:nemotron
     $11 #101 symbole           38.46°C 🥵  947‰   ~8 used:9  [7]    source:nemotron
     $13 #140 merveilleux       34.76°C 😎  890‰  ~10 used:0  [9]    source:nemotron
     $44 #108 irréel            25.57°C 🥶        ~46 used:0  [45]   source:nemotron
    $169 #114 opposant          -0.41°C 🧊       ~169 used:0  [168]  source:nemotron
