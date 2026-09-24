# 2026-09-25

- 🔗 spaceword.org 🧩 2026-09-24 🏁 score 2168 ranked 48.0% 172/358 ⏱️ 0:51:37.032880
- 🔗 wordgrid 🧩 #846 🟪 rarity:0.34 ⏱️ 0:03:41.805184
- 🔗 alfagok.diginaut.net 🧩 #692 🥳 38 ⏱️ 0:00:48.375444
- 🔗 alphaguess.com 🧩 #1159 🥳 26 ⏱️ 0:00:55.192759
- 🔗 dontwordle.com 🧩 #1585 🥳 6 ⏱️ 0:01:45.129113
- 🔗 dictionary.com hurdle 🧩 #1728 😦 21 ⏱️ 0:05:04.493867
- 🔗 Quordle Classic 🧩 #1705 🥳 score:23 ⏱️ 0:01:59.529106
- 🔗 Octordle Classic 🧩 #1705 🥳 score:55 ⏱️ 0:02:37.776326
- 🔗 Sedecordle Classic 🧩 #1685 🥳 score:50 ⏱️ 0:02:13.321399
- 🔗 squareword.org 🧩 #1698 🥳 7 ⏱️ 0:02:24.866133
- 🔗 cemantle.certitudes.org 🧩 #1635 🥳 243 ⏱️ 0:06:56.499293
- 🔗 cemantix.certitudes.org 🧩 #1668 🥳 237 ⏱️ 2:16:47.973329

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





# [spaceword.org](spaceword.org) 🧩 2026-09-24 🏁 score 2168 ranked 48.0% 172/358 ⏱️ 0:51:37.032880

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 172/358

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ E K E _ _ _ _ A _   
      _ N _ _ J _ _ _ W _   
      _ G A L I O T _ E _   
      _ _ B O N F I R E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #846 🟪 rarity:0.34 ⏱️ 0:03:41.805184

📜 2 sessions
🌌 🌌 🦄
🌌 🌌 🌌
🌌 🌌 🌌
Rarity: 0.34 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #692 🥳 38 ⏱️ 0:00:48.375444

🤔 38 attempts
📜 1 sessions

    @       [    0] &-teken     
    @+49802 [49802] boks        q4  ? ␅
    @+49802 [49802] boks        q5  ? after
    @+74698 [74698] dc          q6  ? ␅
    @+74698 [74698] dc          q7  ? after
    @+87156 [87156] draag       q8  ? ␅
    @+87156 [87156] draag       q9  ? after
    @+90006 [90006] dubbel      q12 ? ␅
    @+90006 [90006] dubbel      q13 ? after
    @+91683 [91683] dwerg       q14 ? ␅
    @+91683 [91683] dwerg       q15 ? after
    @+92512 [92512] educatie    q16 ? ␅
    @+92512 [92512] educatie    q17 ? after
    @+92679 [92679] een         q18 ? ␅
    @+92679 [92679] een         q19 ? after
    @+93022 [93022] eenpersoons q20 ? ␅
    @+93022 [93022] eenpersoons q21 ? after
    @+93143 [93143] eer         q22 ? ␅
    @+93143 [93143] eer         q23 ? after
    @+93194 [93194] eergierig   q26 ? ␅
    @+93194 [93194] eergierig   q27 ? after
    @+93216 [93216] eerloos     q28 ? ␅
    @+93216 [93216] eerloos     q29 ? after
    @+93231 [93231] eerst       q36 ? ␅
    @+93231 [93231] eerst       q37 ? it
    @+93231 [93231] eerst       done. it
    @+93240 [93240] eerste      q24 ? ␅
    @+93240 [93240] eerste      q25 ? before
    @+93368 [93368] eet         q10 ? ␅
    @+93368 [93368] eet         q11 ? before
    @+99672 [99672] ex          q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1159 🥳 26 ⏱️ 0:00:55.192759

🤔 26 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+47374 [47374] dis        q2  ? ␅
    @+47374 [47374] dis        q3  ? after
    @+60013 [60013] eyewitness q6  ? ␅
    @+60013 [60013] eyewitness q7  ? after
    @+60027 [60027] fa         q16 ? ␅
    @+60027 [60027] fa         q17 ? after
    @+60400 [60400] falces     q18 ? ␅
    @+60400 [60400] falces     q19 ? after
    @+60460 [60460] false      q24 ? ␅
    @+60460 [60460] false      q25 ? it
    @+60460 [60460] false      done. it
    @+60545 [60545] fan        q20 ? ␅
    @+60545 [60545] fan        q21 ? after
    @+60545 [60545] fan        q22 ? ␅
    @+60545 [60545] fan        q23 ? before
    @+60772 [60772] farm       q14 ? ␅
    @+60772 [60772] farm       q15 ? before
    @+61562 [61562] fem        q12 ? ␅
    @+61562 [61562] fem        q13 ? before
    @+63147 [63147] fix        q10 ? ␅
    @+63147 [63147] fix        q11 ? before
    @+66305 [66305] free       q8  ? ␅
    @+66305 [66305] free       q9  ? before
    @+72657 [72657] green      q4  ? ␅
    @+72657 [72657] green      q5  ? before
    @+98142 [98142] mac        q0  ? ␅
    @+98142 [98142] mac        q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1585 🥳 6 ⏱️ 0:01:45.129113

📜 1 sessions
💰 score: 80

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:BOFFO n n n n n remain:7320
    ⬜⬜⬜⬜⬜ tried:PEWEE n n n n n remain:2667
    ⬜⬜⬜⬜⬜ tried:DAGGA n n n n n remain:652
    ⬜⬜⬜⬜⬜ tried:MUMUS n n n n n remain:100
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:31
    ⬜🟨⬜⬜⬜ tried:JINNI n m n n n remain:10

    Undos used: 2

      10 words remaining
    x 8 unused letters
    = 80 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1728 😦 21 ⏱️ 0:05:04.493867

📜 2 sessions
💰 score: 4580

    6/6
    RATES 🟨🟩⬜⬜⬜
    LAIRD ⬜🟩⬜🟨⬜
    NARCO ⬜🟩🟩⬜⬜
    BLIMP ⬜⬜⬜⬜🟨
    HOPAK ⬜⬜🟨🟨🟨
    PARKA 🟩🟩🟩🟩🟩
    3/6
    PARKA ⬜🟨⬜⬜⬜
    LEAST ⬜🟨🟩⬜🟩
    ENACT 🟩🟩🟩🟩🟩
    6/6
    ENACT 🟨⬜🟩⬜⬜
    HEARS ⬜🟨🟩🟨⬜
    DEIGN ⬜🟨⬜⬜⬜
    BRAKE ⬜🟨⬜🟨⬜
    BRAVE 🟩🟩🟩⬜🟩
    ????? 🟩🟩🟩🟩🟩
    4/6
    BRAVE ⬜🟨🟨⬜⬜
    RANTS 🟨🟨🟨⬜⬜
    ADORN 🟩⬜⬜🟩🟨
    ANGRY 🟩🟩🟩🟩🟩
    Final 2/2
    ????? 🟨🟨⬜⬜🟩
    ????? ⬜🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1705 🥳 score:23 ⏱️ 0:01:59.529106

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SWEAR attempts:8 score:8
2. FLOOD attempts:4 score:4
3. GUPPY attempts:6 score:6
4. GROAN attempts:5 score:5

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1705 🥳 score:55 ⏱️ 0:02:37.776326

📜 1 sessions

Octordle Classic

1. POISE attempts:8 score:8
2. DINGO attempts:5 score:5
3. IVORY attempts:3 score:3
4. OVOID attempts:4 score:4
5. QUASH attempts:12 score:12
6. ICING attempts:6 score:6
7. VERVE attempts:7 score:7
8. APPLY attempts:10 score:10

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1685 🥳 score:50 ⏱️ 0:02:13.321399

📜 1 sessions

Sedecordle Classic sedecordle.com

1. MUCUS attempts:17 score:1
2. STAVE attempts:11 score:8
3. WREST attempts:8 score:0
4. UPPER attempts:9 score:8
5. LUCID attempts:5 score:0
6. STERN attempts:4 score:5
7. BRAWL attempts:7 score:0
8. SOUND attempts:6 score:7
9. MOTTO attempts:12 score:1
10. STEEL attempts:2 score:2
11. MINUS attempts:13 score:1
12. OVARY attempts:10 score:3
13. HOVER attempts:17 score:1
14. SAPPY attempts:14 score:7
15. BIDDY attempts:15 score:1
16. DANDY attempts:16 score:5

# [squareword.org](squareword.org) 🧩 #1698 🥳 7 ⏱️ 0:02:24.866133

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟩 🟩 🟩
    🟩 🟩 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A R G O T
    M O U T H
    A B A T E
    S I N E S
    S N O R E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1635 🥳 243 ⏱️ 0:06:56.499293

🤔 244 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 63 chat prompts
🤖 63 gemma4:12b replies
🔥   1 🥵   5 😎  39 🥶 186 🧊  12

      $1 #244 prisoner        100.00°C 🥳 1000‰ ~232 used:0  [231]  source:gemma4
      $2 #142 soldier          56.31°C 🔥  996‰   ~2 used:68 [1]    source:gemma4
      $3 #153 corporal         39.80°C 🥵  960‰  ~39 used:24 [38]   source:gemma4
      $4 #124 combatant        39.10°C 🥵  955‰  ~34 used:20 [33]   source:gemma4
      $5 #152 colonel          36.51°C 🥵  933‰  ~32 used:11 [31]   source:gemma4
      $6 #240 hostage          36.39°C 🥵  929‰   ~1 used:0  [0]    source:gemma4
      $7 #162 sergeant         34.85°C 🥵  910‰  ~33 used:11 [32]   source:gemma4
      $8 #149 infantryman      33.33°C 😎  893‰  ~35 used:2  [34]   source:gemma4
      $9 #129 fighter          32.66°C 😎  885‰  ~40 used:3  [39]   source:gemma4
     $10 #242 peacekeeper      32.57°C 😎  884‰   ~3 used:0  [2]    source:gemma4
     $11  #95 citizen          31.87°C 😎  869‰  ~45 used:12 [44]   source:gemma4
     $12 #195 lieutenant       30.68°C 😎  847‰  ~36 used:2  [35]   source:gemma4
     $48 #165 troop            20.88°C 🥶        ~55 used:0  [54]   source:gemma4
    $233 #231 company          -0.20°C 🧊       ~233 used:0  [232]  source:gemma4

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1668 🥳 237 ⏱️ 2:16:47.973329

🤔 238 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 58 chat prompts
🤖 58 nemotron-3-nano:30b-cloud replies
😱   1 🔥   5 🥵  17 😎  46 🥶 148 🧊  20

      $1 #238 comparable           100.00°C 🥳 1000‰ ~218 used:0  [217]  source:nemotron
      $2 #132 comparaison           63.58°C 😱  999‰   ~1 used:47 [0]    source:nemotron
      $3 #171 similaire             62.45°C 🔥  998‰  ~15 used:14 [14]   source:nemotron
      $4  #79 analogue              56.99°C 🔥  996‰  ~18 used:29 [17]   source:nemotron
      $5 #196 identique             56.87°C 🔥  995‰   ~3 used:6  [2]    source:nemotron
      $6 #190 équivalent            54.79°C 🔥  994‰   ~4 used:6  [3]    source:nemotron
      $7 #165 semblable             52.57°C 🔥  992‰   ~2 used:5  [1]    source:nemotron
      $8 #200 proportion            48.99°C 🥵  987‰   ~5 used:0  [4]    source:nemotron
      $9 #184 différence            47.93°C 🥵  983‰   ~6 used:0  [5]    source:nemotron
     $10 #167 différer              45.36°C 🥵  977‰   ~7 used:0  [6]    source:nemotron
     $11 #178 proportionnellement   44.38°C 🥵  975‰   ~8 used:0  [7]    source:nemotron
     $25  #82 modèle                34.56°C 😎  874‰  ~23 used:1  [22]   source:nemotron
     $71 #137 rapprochement         23.69°C 🥶        ~71 used:0  [70]   source:nemotron
    $219 #229 jumelage              -0.69°C 🧊       ~219 used:0  [218]  source:nemotron
