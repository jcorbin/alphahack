# 2026-08-20

- 🔗 spaceword.org 🧩 2026-08-19 🏁 score 2164 ranked 53.0% 170/321 ⏱️ 0:40:43.998697
- 🔗 wordgrid 🧩 #810 🌌 rarity:0.09 ⏱️ 0:03:39.692930
- 🔗 alfagok.diginaut.net 🧩 #656 🥳 46 ⏱️ 0:01:13.903794
- 🔗 alphaguess.com 🧩 #1123 🥳 24 ⏱️ 0:00:30.481278
- 🔗 dontwordle.com 🧩 #1549 🥳 6 ⏱️ 0:01:14.038506
- 🔗 dictionary.com hurdle 🧩 #1692 🥳 16 ⏱️ 0:04:47.278478
- 🔗 Quordle Classic 🧩 #1669 🥳 score:19 ⏱️ 0:01:17.030621
- 🔗 Octordle Classic 🧩 #1669 🥳 score:66 ⏱️ 0:01:42.149668
- 🔗 Sedecordle Classic 🧩 #1649 🥳 score:46 ⏱️ 0:02:15.155641
- 🔗 squareword.org 🧩 #1662 🥳 7 ⏱️ 0:01:30.235502
- 🔗 cemantle.certitudes.org 🧩 #1599 🥳 275 ⏱️ 0:09:42.375885
- 🔗 cemantix.certitudes.org 🧩 #1632 🥳 167 ⏱️ 0:13:13.058719

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







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #781 🟪 rarity:0.15 ⏱️ 0:03:50.236694

📜 2 sessions
🌌 🦄 🦄
🌌 🦄 🦄
🌌 🌌 🌌
Rarity: 0.15 🟪


# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #-1 ❗ rarity:nan ⏱️ 0:05:19.095498

📜 2 sessions
🌌 🦄 🌌
🌌 🦄 🌌
🌌 🦄 🌌
Rarity: nan ❗







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #788 🟪 rarity:0.29 ⏱️ 0:03:24.033720

📜 2 sessions
🦄 🦄 🌌
🦄 🦄 🦄
🌌 🦄 🌌
Rarity: 0.29 🟪


# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #789 🟪 rarity:0.23 ⏱️ 0:02:56.015327

📜 2 sessions
🌌 🌌 🌌
🦄 🦄 🌌
🦄 🦄 🦄
Rarity: 0.23 🟪







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #795 🟪 rarity:0.27 ⏱️ 0:03:44.973967

📜 2 sessions
🦄 🌌 🌌
🌌 🌌 🌌
🦄 🦄 🌌
Rarity: 0.27 🟪
















# [spaceword.org](spaceword.org) 🧩 2026-08-19 🏁 score 2164 ranked 53.0% 170/321 ⏱️ 0:40:43.998697

📜 3 sessions
- tiles: 21/21
- score: 2164 bonus: +64
- rank: 170/321

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ A _ _ Y _ _ Q _ _   
      _ C _ J O L T I E R   
      _ T H O R I A _ _ U   
      _ _ _ _ E _ X _ _ E   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #810 🌌 rarity:0.09 ⏱️ 0:03:39.692930

📜 2 sessions
🦄 🦄 🌌
🦄 🦄 🌌
🦄 🦄 🌌
Rarity: 0.09 🌌


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #656 🥳 46 ⏱️ 0:01:13.903794

🤔 46 attempts
📜 1 sessions

    @        [     0] &-teken        
    @+199547 [199547] lij            q0  ? ␅
    @+199547 [199547] lij            q1  ? after
    @+199547 [199547] lij            q2  ? ␅
    @+199547 [199547] lij            q3  ? after
    @+199547 [199547] lij            q4  ? ␅
    @+199547 [199547] lij            q5  ? after
    @+299513 [299513] schrok         q6  ? ␅
    @+299513 [299513] schrok         q7  ? after
    @+349500 [349500] vakanties      q8  ? ␅
    @+349500 [349500] vakanties      q9  ? after
    @+374495 [374495] vrijst         q10 ? ␅
    @+374495 [374495] vrijst         q11 ? after
    @+386879 [386879] winkel         q12 ? ␅
    @+386879 [386879] winkel         q13 ? after
    @+392880 [392880] zelf           q14 ? ␅
    @+392880 [392880] zelf           q15 ? after
    @+396184 [396184] zonde          q16 ? ␅
    @+396184 [396184] zonde          q17 ? after
    @+396982 [396982] zout           q20 ? ␅
    @+396982 [396982] zout           q21 ? after
    @+397166 [397166] zuid           q22 ? ␅
    @+397166 [397166] zuid           q23 ? after
    @+397238 [397238] zuid-soedanese q36 ? ␅
    @+397238 [397238] zuid-soedanese q37 ? .
    @+397250 [397250] zuidas         q40 ? ␅
    @+397250 [397250] zuidas         q41 ? after
    @+397263 [397263] zuidelijk      q42 ? ␅
    @+397263 [397263] zuidelijk      q43 ? after
    @+397272 [397272] zuiden         q45 ? it
    @+397272 [397272] zuiden         done. it

# [alphaguess.com](alphaguess.com) 🧩 #1123 🥳 24 ⏱️ 0:00:30.481278

🤔 24 attempts
📜 2 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+47378 [47378] dis        q4  ? ␅
    @+47378 [47378] dis        q5  ? after
    @+60017 [60017] eyewitness q8  ? ␅
    @+60017 [60017] eyewitness q9  ? after
    @+63151 [63151] fix        q12 ? ␅
    @+63151 [63151] fix        q13 ? after
    @+64725 [64725] fold       q14 ? ␅
    @+64725 [64725] fold       q15 ? after
    @+65094 [65094] forb       q18 ? ␅
    @+65094 [65094] forb       q19 ? after
    @+65125 [65125] force      q22 ? ␅
    @+65125 [65125] force      q23 ? it
    @+65125 [65125] force      done. it
    @+65161 [65161] fore       q20 ? ␅
    @+65161 [65161] fore       q21 ? before
    @+65511 [65511] forge      q16 ? ␅
    @+65511 [65511] forge      q17 ? before
    @+66309 [66309] free       q10 ? ␅
    @+66309 [66309] free       q11 ? before
    @+72662 [72662] green      q6  ? ␅
    @+72662 [72662] green      q7  ? before
    @+98147 [98147] mac        q0  ? ␅
    @+98147 [98147] mac        q1  ? after
    @+98147 [98147] mac        q2  ? ␅
    @+98147 [98147] mac        q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1549 🥳 6 ⏱️ 0:01:14.038506

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:PEWEE n n n n n remain:5634
    ⬜⬜⬜⬜⬜ tried:SUDDS n n n n n remain:1724
    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:667
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:277
    ⬜⬜🟨⬜⬜ tried:CHOTT n n m n n remain:41
    🟩⬜⬜⬜🟩 tried:MORRO Y n n n Y remain:1

    Undos used: 2

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1692 🥳 16 ⏱️ 0:04:47.278478

📜 1 sessions
💰 score: 10000

    4/6
    STALE ⬜🟨🟨⬜⬜
    APORT 🟨⬜⬜🟨🟨
    WARTY ⬜🟨🟨🟨⬜
    TRIAD 🟩🟩🟩🟩🟩
    3/6
    TRIAD ⬜🟩🟩⬜⬜
    PRISM 🟨🟩🟩⬜⬜
    GRIPE 🟩🟩🟩🟩🟩
    3/6
    GRIPE ⬜🟨⬜⬜🟩
    SHARE 🟨🟨⬜🟨🟩
    HORSE 🟩🟩🟩🟩🟩
    5/6
    HORSE ⬜⬜⬜🟩🟩
    PAUSE ⬜🟨⬜🟩🟩
    CEASE ⬜🟩🟩🟩🟩
    ALOFT 🟨⬜⬜⬜🟨
    TEASE 🟩🟩🟩🟩🟩
    Final 1/2
    DEFOG 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1669 🥳 score:19 ⏱️ 0:01:17.030621

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SPINE attempts:4 score:4
2. CLOSE attempts:5 score:5
3. ERUPT attempts:3 score:3
4. FINER attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1669 🥳 score:66 ⏱️ 0:01:42.149668

📜 1 sessions

Octordle Classic

1. HAVEN attempts:7 score:7
2. EXILE attempts:8 score:8
3. JOINT attempts:9 score:9
4. FINCH attempts:12 score:12
5. TENET attempts:4 score:4
6. RUDDY attempts:10 score:10
7. MELON attempts:5 score:5
8. SNOWY attempts:11 score:11

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1649 🥳 score:46 ⏱️ 0:02:15.155641

📜 1 sessions

Sedecordle Classic sedecordle.com

1. MISSY attempts:11 score:1
2. CRASH attempts:4 score:1
3. CLASS attempts:17 score:1
4. CHURN attempts:5 score:8
5. BRISK attempts:10 score:1
6. SMASH attempts:12 score:0
7. SANER attempts:6 score:0
8. ULCER attempts:3 score:6
9. HEADY attempts:7 score:0
10. CACTI attempts:8 score:7
11. BICEP attempts:9 score:0
12. PHONY attempts:13 score:9
13. DRAKE attempts:14 score:1
14. ANGER attempts:15 score:4
15. NAVEL attempts:16 score:1
16. VAPOR attempts:17 score:6

# [squareword.org](squareword.org) 🧩 #1662 🥳 7 ⏱️ 0:01:30.235502

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P A S M
    P H O N E
    R A R E R
    A S T E R
    T E A R Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1599 🥳 275 ⏱️ 0:09:42.375885

🤔 276 attempts
📜 1 sessions
🫧 14 chat sessions
⁉️ 76 chat prompts
🤖 10 ornith-1.5:35b replies
🤖 21 muse-glimmer:latest replies
🤖 44 dolphin3:latest replies
🔥   3 🥵  21 😎  42 🥶 200 🧊   9

      $1 #276 invade          100.00°C 🥳 1000‰ ~267 used:0  [266]  source:ornith  
      $2 #119 invasion         55.63°C 🔥  998‰  ~20 used:62 [19]   source:dolphin3
      $3 #157 colonize         52.86°C 🔥  997‰  ~15 used:29 [14]   source:dolphin3
      $4 #155 subjugate        43.93°C 🔥  991‰  ~14 used:21 [13]   source:dolphin3
      $5 #150 conquer          42.54°C 🥵  988‰  ~16 used:3  [15]   source:dolphin3
      $6 #153 overrun          42.14°C 🥵  985‰  ~17 used:3  [16]   source:dolphin3
      $7 #210 ravage           41.60°C 🥵  984‰  ~18 used:3  [17]   source:muse    
      $8 #203 despoil          40.96°C 🥵  980‰   ~5 used:2  [4]    source:muse    
      $9 #106 colonized        40.33°C 🥵  977‰  ~58 used:15 [57]   source:dolphin3
     $10 #269 occupy           40.29°C 🥵  976‰   ~6 used:2  [5]    source:ornith  
     $11 #128 incursion        39.02°C 🥵  963‰  ~21 used:9  [20]   source:dolphin3
     $25 #159 oppress          33.77°C 😎  899‰  ~13 used:2  [12]   source:dolphin3
     $68 #102 subjugation      22.95°C 🥶        ~72 used:0  [71]   source:dolphin3
    $268 #121 settlement       -0.24°C 🧊       ~268 used:0  [267]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1632 🥳 167 ⏱️ 0:13:13.058719

🤔 168 attempts
📜 5 sessions
🫧 29 chat sessions
⁉️ 80 chat prompts
🤖 38 dolphin3:latest replies
🤖 41 ornith-1.5:35b replies
🥵  6 😎 48 🥶 98 🧊 15

      $1 #168 toit           100.00°C 🥳 1000‰ ~153 used:0  [152]  source:dolphin3
      $2 #105 vitre           41.88°C 🥵  975‰  ~52 used:37 [51]   source:dolphin3
      $3  #72 imposte         37.94°C 🥵  926‰  ~53 used:40 [52]   source:ornith  
      $4  #95 porte           37.55°C 🥵  920‰  ~38 used:14 [37]   source:ornith  
      $5  #77 chambranle      37.43°C 🥵  918‰  ~37 used:12 [36]   source:ornith  
      $6  #82 galandage       37.09°C 🥵  907‰  ~35 used:11 [34]   source:ornith  
      $7  #87 fenêtre         36.75°C 🥵  902‰  ~36 used:11 [35]   source:ornith  
      $8  #91 lucarne         36.44°C 😎  892‰  ~39 used:2  [38]   source:ornith  
      $9  #23 voûter          35.79°C 😎  879‰  ~54 used:23 [53]   source:ornith  
     $10 #125 dôme            35.53°C 😎  872‰  ~40 used:2  [39]   source:dolphin3
     $11 #124 charpente       34.56°C 😎  854‰  ~41 used:2  [40]   source:dolphin3
     $12  #71 linteau         34.51°C 😎  853‰  ~42 used:2  [41]   source:ornith  
     $56  #24 arcade          24.70°C 🥶        ~55 used:0  [54]   source:ornith  
    $154 #102 imposteur       -0.88°C 🧊       ~154 used:0  [153]  source:dolphin3
