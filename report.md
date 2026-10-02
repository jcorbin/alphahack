# 2026-10-03

- 🔗 spaceword.org 🧩 2026-10-02 🏁 score 2168 ranked 35.8% 112/313 ⏱️ 0:43:02.719052
- 🔗 wordgrid 🧩 #854 🟪 rarity:0.2 ⏱️ 0:03:30.438162
- 🔗 alfagok.diginaut.net 🧩 #700 🥳 26 ⏱️ 0:01:02.594403
- 🔗 alphaguess.com 🧩 #1167 🥳 28 ⏱️ 0:00:40.722438
- 🔗 dontwordle.com 🧩 #1593 🥳 6 ⏱️ 0:01:45.731222
- 🔗 dictionary.com hurdle 🧩 #1736 🥳 20 ⏱️ 0:04:14.575934
- 🔗 Quordle Classic 🧩 #1713 🥳 score:24 ⏱️ 0:01:45.259091
- 🔗 Octordle Classic 🧩 #1713 🥳 score:67 ⏱️ 0:02:51.121316
- 🔗 Sedecordle Classic 🧩 #1693 🥳 score:48 ⏱️ 0:04:13.725643
- 🔗 squareword.org 🧩 #1706 🥳 8 ⏱️ 0:03:19.044607
- 🔗 cemantle.certitudes.org 🧩 #1643 🥳 59 ⏱️ 0:03:15.107130
- 🔗 cemantix.certitudes.org 🧩 #1676 🥳 87 ⏱️ 0:04:09.419045

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













# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #854 🟪 rarity:0.2 ⏱️ 0:03:30.438162

📜 2 sessions
🦄 🦄 🌌
🦄 🌌 🌌
🦄 🌌 🌌
Rarity: 0.2 🟪

# [spaceword.org](spaceword.org) 🧩 2026-10-02 🏁 score 2168 ranked 35.8% 112/313 ⏱️ 0:43:02.719052

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 112/313

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ Q _ _ X _ R _   
      _ E _ U N C U T E _   
      _ N _ A _ U _ O I _   
      _ G U Y O T _ W _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #700 🥳 26 ⏱️ 0:01:02.594403

🤔 26 attempts
📜 2 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+199528 [199528] lij        q0  ? ␅
    @+199528 [199528] lij        q1  ? after
    @+299480 [299480] schrok     q2  ? ␅
    @+299480 [299480] schrok     q3  ? after
    @+302527 [302527] show       q12 ? ␅
    @+302527 [302527] show       q13 ? after
    @+304060 [304060] skateboard q14 ? ␅
    @+304060 [304060] skateboard q15 ? after
    @+304674 [304674] slag       q16 ? ␅
    @+304674 [304674] slag       q17 ? after
    @+305139 [305139] slavist    q20 ? ␅
    @+305139 [305139] slavist    q21 ? after
    @+305361 [305361] slenter    q22 ? ␅
    @+305361 [305361] slenter    q23 ? after
    @+305418 [305418] sleutel    q24 ? ␅
    @+305418 [305418] sleutel    q25 ? it
    @+305418 [305418] sleutel    done. it
    @+305601 [305601] slijk      q10 ? ␅
    @+305601 [305601] slijk      q11 ? before
    @+311721 [311721] spier      q8  ? ␅
    @+311721 [311721] spier      q9  ? before
    @+324115 [324115] sub        q6  ? ␅
    @+324115 [324115] sub        q7  ? before
    @+349464 [349464] vakanties  q4  ? ␅
    @+349464 [349464] vakanties  q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1167 🥳 28 ⏱️ 0:00:40.722438

🤔 28 attempts
📜 1 sessions

    @       [    0] aa           
    @+2     [    2] aahed        
    @+23680 [23680] camp         q4  ? ␅
    @+23680 [23680] camp         q5  ? after
    @+35522 [35522] convention   q6  ? ␅
    @+35522 [35522] convention   q7  ? after
    @+40838 [40838] da           q8  ? ␅
    @+40838 [40838] da           q9  ? after
    @+44066 [44066] den          q10 ? ␅
    @+44066 [44066] den          q11 ? after
    @+45658 [45658] dev          q12 ? ␅
    @+45658 [45658] dev          q13 ? after
    @+46067 [46067] diagram      q16 ? ␅
    @+46067 [46067] diagram      q17 ? after
    @+46167 [46167] diamin       q20 ? ␅
    @+46167 [46167] diamin       q21 ? after
    @+46172 [46172] diamond      q26 ? ␅
    @+46172 [46172] diamond      q27 ? it
    @+46172 [46172] diamond      done. it
    @+46190 [46190] diaper       q24 ? ␅
    @+46190 [46190] diaper       q25 ? before
    @+46219 [46219] diapir       q22 ? ␅
    @+46219 [46219] diapir       q23 ? before
    @+46274 [46274] diastrophism q18 ? ␅
    @+46274 [46274] diastrophism q19 ? before
    @+46481 [46481] did          q14 ? ␅
    @+46481 [46481] did          q15 ? before
    @+47374 [47374] dis          q2  ? ␅
    @+47374 [47374] dis          q3  ? before
    @+98142 [98142] mac          q0  ? ␅
    @+98142 [98142] mac          q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1593 🥳 6 ⏱️ 0:01:45.731222

📜 2 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:TWEET n n n n n remain:5004
    ⬜⬜⬜⬜⬜ tried:MOSSO n n n n n remain:1208
    ⬜⬜⬜⬜⬜ tried:HIPPY n n n n n remain:229
    ⬜⬜⬜⬜⬜ tried:FLUFF n n n n n remain:60
    🟨⬜⬜⬜⬜ tried:ADDAX m n n n n remain:8
    ⬜🟩🟩⬜⬜ tried:GNARR n Y Y n n remain:1

    Undos used: 4

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1736 🥳 20 ⏱️ 0:04:14.575934

📜 1 sessions
💰 score: 9600

    5/6
    REAIS ⬜🟨🟩⬜⬜
    PLANE ⬜🟩🟩⬜🟩
    BLADE 🟩🟩🟩⬜🟩
    MATZA ⬜🟨⬜🟩⬜
    ????? 🟩🟩🟩🟩🟩
    4/6
    BLAZE ⬜🟨🟨⬜🟨
    LARES 🟨🟨🟨🟨⬜
    VYING ⬜⬜⬜⬜🟨
    REGAL 🟩🟩🟩🟩🟩
    4/6
    REGAL ⬜⬜⬜🟨🟩
    BASIL ⬜🟨⬜🟩🟩
    FLUNG ⬜🟨⬜🟨⬜
    ANVIL 🟩🟩🟩🟩🟩
    6/6
    ANVIL ⬜⬜⬜⬜⬜
    DORES ⬜⬜⬜⬜🟨
    TUSKY ⬜🟩🟩⬜🟩
    CLIMB ⬜⬜⬜⬜⬜
    AWFUL ⬜⬜🟨🟨⬜
    FUSSY 🟩🟩🟩🟩🟩
    Final 1/2
    BAGGY 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1713 🥳 score:24 ⏱️ 0:01:45.259091

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. CHORE attempts:6 score:6
2. FLYER attempts:3 score:3
3. STICK attempts:7 score:7
4. PURSE attempts:8 score:8

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1713 🥳 score:67 ⏱️ 0:02:51.121316

📜 2 sessions

Octordle Classic

1. SALLY attempts:10 score:10
2. CLACK attempts:7 score:7
3. CABIN attempts:4 score:4
4. SCALD attempts:9 score:9
5. CRISP attempts:11 score:11
6. GUILT attempts:12 score:12
7. FIBER attempts:8 score:8
8. VOMIT attempts:6 score:6

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1693 🥳 score:48 ⏱️ 0:04:13.725643

📜 4 sessions

Sedecordle Classic sedecordle.com

1. MINIM attempts:9 score:0
2. WOMAN attempts:12 score:9
3. FROTH attempts:5 score:0
4. CLOSE attempts:3 score:5
5. MAGMA attempts:13 score:1
6. GUEST attempts:14 score:3
7. SIXTH attempts:6 score:0
8. RIVAL attempts:17 score:6
9. SLICE attempts:4 score:0
10. SCRAM attempts:10 score:4
11. WIGHT attempts:15 score:1
12. TIDAL attempts:11 score:5
13. ADAGE attempts:16 score:1
14. CRAZE attempts:18 score:6
15. CREST attempts:7 score:0
16. TRUMP attempts:8 score:7

# [squareword.org](squareword.org) 🧩 #1706 🥳 8 ⏱️ 0:03:19.044607

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟩 🟨
    🟨 🟩 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C A L D
    L A G E R
    A N O D E
    C O N G A
    K E Y E D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1643 🥳 59 ⏱️ 0:03:15.107130

🤔 60 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 8 chat prompts
🤖 8 gemma4:12b replies
🥵  5 😎  9 🥶 39 🧊  6

     $1 #60 supplier       100.00°C 🥳 1000‰ ~54 used:0 [53]  source:gemma4
     $2 #41 manufacturing   42.84°C 🥵  973‰  ~1 used:1 [0]   source:gemma4
     $3 #53 industry        39.97°C 🥵  963‰  ~2 used:0 [1]   source:gemma4
     $4 #51 factory         37.51°C 🥵  951‰  ~3 used:0 [2]   source:gemma4
     $5 #43 component       37.48°C 🥵  950‰  ~4 used:0 [3]   source:gemma4
     $6 #58 production      31.36°C 🥵  900‰  ~5 used:0 [4]   source:gemma4
     $7 #57 processing      29.81°C 😎  867‰  ~6 used:0 [5]   source:gemma4
     $8 #50 fabrication     27.30°C 😎  784‰  ~7 used:0 [6]   source:gemma4
     $9 #54 logistics       27.24°C 😎  780‰  ~8 used:0 [7]   source:gemma4
    $10 #16 fiber           25.26°C 😎  672‰ ~14 used:4 [13]  source:gemma4
    $11 #48 design          24.40°C 😎  604‰  ~9 used:0 [8]   source:gemma4
    $12 #56 millwork        22.80°C 😎  437‰ ~10 used:0 [9]   source:gemma4
    $16 #17 fabric          18.29°C 🥶       ~16 used:3 [15]  source:gemma4
    $55  #9 whisper         -0.05°C 🧊       ~55 used:0 [54]  source:gemma4

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1676 🥳 87 ⏱️ 0:04:09.419045

🤔 88 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 12 chat prompts
🤖 12 gemma4:12b replies
🔥  2 😎 10 🥶 47 🧊 28

     $1 #88 équité          100.00°C 🥳 1000‰ ~60 used:0 [59]  source:gemma4
     $2 #82 égalité          58.79°C 🔥  998‰  ~1 used:2 [0]   source:gemma4
     $3 #70 équilibre        47.46°C 🔥  994‰  ~2 used:3 [1]   source:gemma4
     $4 #85 parité           31.28°C 😎  829‰  ~3 used:0 [2]   source:gemma4
     $5 #54 stabilité        29.80°C 😎  757‰  ~4 used:1 [3]   source:gemma4
     $6 #34 système          27.82°C 😎  635‰ ~12 used:2 [11]  source:gemma4
     $7 #78 mesure           27.53°C 😎  614‰  ~5 used:0 [4]   source:gemma4
     $8 #38 autonomie        27.12°C 😎  588‰  ~6 used:1 [5]   source:gemma4
     $9 #87 uniformité       26.70°C 😎  544‰  ~7 used:0 [6]   source:gemma4
    $10 #58 état             24.50°C 😎  350‰  ~8 used:0 [7]   source:gemma4
    $11 #75 harmonie         23.24°C 😎  204‰  ~9 used:0 [8]   source:gemma4
    $12 #81 régularité       22.49°C 😎  104‰ ~10 used:0 [9]   source:gemma4
    $14 #57 échelon          21.41°C 🥶       ~20 used:0 [19]  source:gemma4
    $61 #23 appoint          -0.13°C 🧊       ~61 used:0 [60]  source:gemma4
