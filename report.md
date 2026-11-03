# 2026-11-04

- 🔗 spaceword.org 🧩 2026-11-03 🏁 score 2168 ranked 39.0% 127/326 ⏱️ 4:37:45.653131
- 🔗 wordgrid 🧩 #886 🟪 rarity:0.18 ⏱️ 0:02:24.000805
- 🔗 alfagok.diginaut.net 🧩 #732 🥳 34 ⏱️ 0:00:44.535579
- 🔗 alphaguess.com 🧩 #1199 🥳 36 ⏱️ 0:00:47.656931
- 🔗 dontwordle.com 🧩 #1625 🥳 6 ⏱️ 0:01:25.761195
- 🔗 dictionary.com hurdle 🧩 #1768 😦 16 ⏱️ 0:02:23.010746
- 🔗 Quordle Classic 🧩 #1745 🥳 score:23 ⏱️ 0:01:36.046498
- 🔗 Octordle Classic 🧩 #1745 🥳 score:52 ⏱️ 0:01:51.816712
- 🔗 Sedecordle Classic 🧩 #1725 🥳 score:45 ⏱️ 0:02:52.929800
- 🔗 squareword.org 🧩 #1738 🥳 7 ⏱️ 0:01:56.471301
- 🔗 cemantle.certitudes.org 🧩 #1675 🥳 1043 ⏱️ 0:53:29.010929
- 🔗 cemantix.certitudes.org 🧩 #1708 🥳 409 ⏱️ 0:03:48.654811

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




# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #886 🟪 rarity:0.18 ⏱️ 0:02:24.000805

📜 2 sessions
🌌 🌌 🌌
🦄 🌌 🌌
🦄 🦄 🦄
Rarity: 0.18 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-03 🏁 score 2168 ranked 39.0% 127/326 ⏱️ 4:37:45.653131

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 127/326

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ M _ _ _ _ F E _ _   
      _ H _ Q U A I L S _   
      _ O _ _ _ Z A _ A _   
      _ S A I L O R _ X _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #732 🥳 34 ⏱️ 0:00:44.535579

🤔 34 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+199631 [199631] lijk       q0  ? ␅
    @+199631 [199631] lijk       q1  ? after
    @+249541 [249541] opi        q4  ? ␅
    @+249541 [249541] opi        q5  ? after
    @+261927 [261927] peper      q8  ? ␅
    @+261927 [261927] peper      q9  ? after
    @+267940 [267940] politie    q10 ? ␅
    @+267940 [267940] politie    q11 ? after
    @+269540 [269540] post       q14 ? ␅
    @+269540 [269540] post       q15 ? after
    @+270343 [270343] praat      q16 ? ␅
    @+270343 [270343] praat      q17 ? after
    @+270516 [270516] praktijk   q20 ? ␅
    @+270516 [270516] praktijk   q21 ? after
    @+270624 [270624] prat       q22 ? ␅
    @+270624 [270624] prat       q23 ? after
    @+270625 [270625] praten     q32 ? ␅
    @+270625 [270625] praten     q33 ? it
    @+270625 [270625] praten     done. it
    @+270626 [270626] pratend    q30 ? ␅
    @+270626 [270626] pratend    q31 ? before
    @+270628 [270628] prater     q28 ? ␅
    @+270628 [270628] prater     q29 ? before
    @+270634 [270634] pratikeren q26 ? ␅
    @+270634 [270634] pratikeren q27 ? before
    @+270649 [270649] pre        q24 ? ␅
    @+270649 [270649] pre        q25 ? before
    @+270763 [270763] predikant  q18 ? ␅
    @+270763 [270763] predikant  q19 ? before
    @+271196 [271196] presente   q13 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1199 🥳 36 ⏱️ 0:00:47.656931

🤔 36 attempts
📜 1 sessions

    @       [    0] aa        
    @+49066 [49066] disturb   q4  ? ␅
    @+49066 [49066] disturb   q5  ? after
    @+73597 [73597] guide     q6  ? ␅
    @+73597 [73597] guide     q7  ? after
    @+85490 [85490] ins       q8  ? ␅
    @+85490 [85490] ins       q9  ? after
    @+91803 [91803] knock     q10 ? ␅
    @+91803 [91803] knock     q11 ? after
    @+94966 [94966] liberal   q12 ? ␅
    @+94966 [94966] liberal   q13 ? after
    @+95139 [95139] lie       q20 ? ␅
    @+95139 [95139] lie       q21 ? after
    @+95172 [95172] life      q24 ? ␅
    @+95172 [95172] life      q25 ? after
    @+95209 [95209] lifestyle q26 ? ␅
    @+95209 [95209] lifestyle q27 ? after
    @+95211 [95211] lifetime  q34 ? ␅
    @+95211 [95211] lifetime  q35 ? it
    @+95211 [95211] lifetime  done. it
    @+95212 [95212] lifetimes q32 ? ␅
    @+95212 [95212] lifetimes q33 ? before
    @+95214 [95214] lifeways  q30 ? ␅
    @+95214 [95214] lifeways  q31 ? before
    @+95219 [95219] lift      q28 ? ␅
    @+95219 [95219] lift      q29 ? before
    @+95246 [95246] ligation  q22 ? ␅
    @+95246 [95246] ligation  q23 ? before
    @+95353 [95353] likable   q18 ? ␅
    @+95353 [95353] likable   q19 ? before
    @+95746 [95746] lino      q17 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1625 🥳 6 ⏱️ 0:01:25.761195

📜 1 sessions
💰 score: 18

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:YOBBY n n n n n remain:6682
    ⬜⬜⬜⬜⬜ tried:ESSES n n n n n remain:1338
    ⬜⬜⬜⬜⬜ tried:LININ n n n n n remain:248
    ⬜⬜⬜⬜⬜ tried:JUGUM n n n n n remain:86
    🟨⬜⬜⬜⬜ tried:ADDAX m n n n n remain:32
    🟩⬜🟨⬜⬜ tried:PZAZZ Y n m n n remain:2

    Undos used: 4

      2 words remaining
    x 9 unused letters
    = 18 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1768 😦 16 ⏱️ 0:02:23.010746

📜 2 sessions
💰 score: 5080

    4/6
    DEARS ⬜⬜⬜⬜⬜
    IMPLY ⬜🟨⬜🟨⬜
    MOGUL 🟩⬜⬜🟨🟨
    MULCH 🟩🟩🟩🟩🟩
    4/6
    MULCH ⬜⬜⬜⬜⬜
    RAGES 🟨🟨⬜🟨🟨
    SPEAR 🟩⬜🟩🟩🟩
    SWEAR 🟩🟩🟩🟩🟩
    4/6
    SWEAR ⬜⬜⬜🟨🟨
    TRAIL ⬜🟨🟩⬜⬜
    HOARD ⬜🟨🟩🟩⬜
    OVARY 🟩🟩🟩🟩🟩
    2/6
    OVARY ⬜🟨⬜⬜🟨
    VINYL 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜🟨🟩🟨🟨
    ????? ⬜🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1745 🥳 score:23 ⏱️ 0:01:36.046498

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. JOIST attempts:9 score:9
2. CROOK attempts:5 score:5
3. DELAY attempts:6 score:6
4. ICILY attempts:3 score:3

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1745 🥳 score:52 ⏱️ 0:01:51.816712

📜 1 sessions

Octordle Classic

1. TACKY attempts:6 score:6
2. STACK attempts:5 score:5
3. AXION attempts:9 score:9
4. ENNUI attempts:4 score:4
5. MORPH attempts:3 score:3
6. ABBOT attempts:10 score:10
7. BATON attempts:7 score:7
8. BUNNY attempts:8 score:8

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1725 🥳 score:45 ⏱️ 0:02:52.929800

📜 1 sessions

Sedecordle Classic sedecordle.com

1. ENACT attempts:17 score:1
2. DITTY attempts:18 score:7
3. GROVE attempts:11 score:1
4. TRIAL attempts:15 score:1
5. MANGO attempts:5 score:0
6. PRICK attempts:12 score:5
7. BLOOD attempts:9 score:0
8. TANGY attempts:7 score:9
9. PLUMB attempts:14 score:1
10. FACET attempts:3 score:4
11. ASCOT attempts:2 score:0
12. BRAND attempts:10 score:2
13. PLANT attempts:6 score:0
14. BRAID attempts:13 score:6
15. PARTY attempts:8 score:0
16. CHEAT attempts:16 score:8

# [squareword.org](squareword.org) 🧩 #1738 🥳 7 ⏱️ 0:01:56.471301

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C H A M P
    R A D I O
    E L I T E
    S L E E T
    T O U R S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1675 🥳 1043 ⏱️ 0:53:29.010929

🤔 1044 attempts
📜 1 sessions
🫧 52 chat sessions
⁉️ 301 chat prompts
🤖 5 dolphin3:latest replies
🤖 296 nemotron-3-nano:30b-cloud replies
😱   1 🔥   9 🥵  44 😎 198 🥶 771 🧊  20

       $1 #1044 emotion            100.00°C 🥳 1000‰ ~1024 used:0   [1023]  source:dolphin3
       $2  #602 emotional           60.23°C 😱  999‰    ~2 used:191 [1]     source:nemotron
       $3  #825 emotionality        58.04°C 🔥  998‰   ~34 used:56  [33]    source:nemotron
       $4  #495 grief               57.43°C 🔥  997‰   ~37 used:74  [36]    source:nemotron
       $5  #603 feelings            56.57°C 🔥  996‰    ~3 used:20  [2]     source:nemotron
       $6  #129 excitement          55.83°C 🔥  995‰  ~250 used:139 [249]   source:nemotron
       $7  #567 anguish             55.42°C 🔥  994‰    ~4 used:20  [3]     source:nemotron
       $8  #511 sadness             55.25°C 🔥  993‰    ~5 used:20  [4]     source:nemotron
       $9  #103 elation             54.55°C 🔥  992‰   ~50 used:96  [49]    source:nemotron
      $10  #538 empathy             54.32°C 🔥  991‰    ~1 used:19  [0]     source:nemotron
      $12  #873 sentimentality      52.87°C 🥵  989‰    ~6 used:2   [5]     source:nemotron
      $56  #128 effervescence       41.98°C 😎  899‰   ~52 used:0   [51]    source:nemotron
     $254  #962 melancholic         29.59°C 🥶        ~257 used:0   [256]   source:nemotron
    $1025    #5 library             -0.04°C 🧊       ~1025 used:0   [1024]  source:nemotron

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1708 🥳 409 ⏱️ 0:03:48.654811

🤔 410 attempts
📜 1 sessions
🫧 20 chat sessions
⁉️ 100 chat prompts
🤖 100 nemotron-3-nano:30b-cloud replies
🔥   5 🥵  34 😎 148 🥶 181 🧊  41

      $1 #410 modalité         100.00°C 🥳 1000‰ ~369 used:0  [368]  source:nemotron
      $2 #356 condition         60.73°C 🔥  998‰  ~10 used:18 [9]    source:nemotron
      $3 #137 procédure         59.61°C 🔥  997‰  ~34 used:63 [33]   source:nemotron
      $4 #252 attribution       57.99°C 🔥  993‰  ~31 used:21 [30]   source:nemotron
      $5 #369 disposition       57.43°C 🔥  992‰   ~1 used:9  [0]    source:nemotron
      $6 #304 établissement     57.21°C 🔥  990‰   ~9 used:12 [8]    source:nemotron
      $7 #385 dispositif        55.76°C 🥵  988‰   ~2 used:1  [1]    source:nemotron
      $8 #174 évaluation        55.43°C 🥵  986‰ ~180 used:15 [179]  source:nemotron
      $9 #180 décret            55.27°C 🥵  985‰  ~32 used:4  [31]   source:nemotron
     $10 #277 déroulement       52.75°C 🥵  978‰  ~11 used:2  [10]   source:nemotron
     $11 #196 règlement         52.47°C 🥵  977‰  ~12 used:2  [11]   source:nemotron
     $41 #278 désignation       43.96°C 😎  898‰  ~37 used:0  [36]   source:nemotron
    $189  #56 compatibilité     26.48°C 🥶       ~188 used:0  [187]  source:nemotron
    $370 #208 procès            -0.10°C 🧊       ~370 used:0  [369]  source:nemotron
