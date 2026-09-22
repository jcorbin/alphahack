# 2026-09-23

- 🔗 spaceword.org 🧩 2026-09-22 🏁 score 2168 ranked 35.5% 127/358 ⏱️ 0:33:47.338085
- 🔗 wordgrid 🧩 #844 🟪 rarity:0.31 ⏱️ 0:12:26.490183
- 🔗 alfagok.diginaut.net 🧩 #690 🥳 36 ⏱️ 0:01:00.149951
- 🔗 alphaguess.com 🧩 #1157 🥳 32 ⏱️ 0:02:12.801484
- 🔗 dontwordle.com 🧩 #1583 🥳 6 ⏱️ 0:01:57.929990
- 🔗 dictionary.com hurdle 🧩 #1726 🥳 18 ⏱️ 0:03:38.630157
- 🔗 Quordle Classic 🧩 #1703 🥳 score:27 ⏱️ 0:02:12.182096
- 🔗 Octordle Classic 🧩 #1703 🥳 score:61 ⏱️ 0:02:54.653177
- 🔗 Sedecordle Classic 🧩 #1683 🥳 score:34 ⏱️ 0:03:25.726519
- 🔗 squareword.org 🧩 #1696 🥳 9 ⏱️ 0:05:53.943231
- 🔗 cemantle.certitudes.org 🧩 #1633 🥳 133 ⏱️ 0:04:07.877464
- 🔗 cemantix.certitudes.org 🧩 #1666 🥳 1160 ⏱️ 7:18:54.743341

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



# [spaceword.org](spaceword.org) 🧩 2026-09-22 🏁 score 2168 ranked 35.5% 127/358 ⏱️ 0:33:47.338085

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 127/358

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ O _ _ _ R _ Y O _   
      _ N _ H O O K E Y _   
      _ S Q U I D _ T E _   
      _ _ _ E _ E _ _ Z _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #844 🟪 rarity:0.31 ⏱️ 0:12:26.490183

📜 2 sessions
🦄 🌌 🌌
🦄 🌌 🌌
🟪 🌌 🌌
Rarity: 0.31 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #690 🥳 36 ⏱️ 0:01:00.149951

🤔 36 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+99675  [ 99675] ex         q4  ? ␅
    @+99675  [ 99675] ex         q5  ? after
    @+124574 [124574] gevoel     q8  ? ␅
    @+124574 [124574] gevoel     q9  ? after
    @+127652 [127652] glamour    q14 ? ␅
    @+127652 [127652] glamour    q15 ? after
    @+128007 [128007] gletsjer   q20 ? ␅
    @+128007 [128007] gletsjer   q21 ? after
    @+128079 [128079] glim       q24 ? ␅
    @+128079 [128079] glim       q25 ? after
    @+128080 [128080] glimlach   q34 ? ␅
    @+128080 [128080] glimlach   q35 ? it
    @+128080 [128080] glimlach   done. it
    @+128081 [128081] glimlachen q32 ? ␅
    @+128081 [128081] glimlachen q33 ? before
    @+128089 [128089] glimmen    q30 ? ␅
    @+128089 [128089] glimmen    q31 ? before
    @+128102 [128102] glimworm   q28 ? ␅
    @+128102 [128102] glimworm   q29 ? before
    @+128126 [128126] glit       q26 ? ␅
    @+128126 [128126] glit       q27 ? before
    @+128179 [128179] gloei      q22 ? ␅
    @+128179 [128179] gloei      q23 ? before
    @+128396 [128396] go         q18 ? ␅
    @+128396 [128396] go         q19 ? before
    @+129140 [129140] gok        q16 ? ␅
    @+129140 [129140] gok        q17 ? before
    @+130744 [130744] gras       q12 ? ␅
    @+130744 [130744] gras       q13 ? before
    @+137060 [137060] handt      q11 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1157 🥳 32 ⏱️ 0:02:12.801484

🤔 32 attempts
📜 1 sessions

    @        [     0] aa             
    @+98142  [ 98142] mac            q0  ? ␅
    @+98142  [ 98142] mac            q1  ? after
    @+122719 [122719] parol          q4  ? ␅
    @+122719 [122719] parol          q5  ? after
    @+128837 [128837] play           q8  ? ␅
    @+128837 [128837] play           q9  ? after
    @+129433 [129433] plush          q14 ? ␅
    @+129433 [129433] plush          q15 ? after
    @+129727 [129727] point          q16 ? ␅
    @+129727 [129727] point          q17 ? after
    @+129799 [129799] pol            q18 ? ␅
    @+129799 [129799] pol            q19 ? after
    @+129924 [129924] politic        q20 ? ␅
    @+129924 [129924] politic        q21 ? after
    @+129925 [129925] political      q30 ? ␅
    @+129925 [129925] political      q31 ? it
    @+129925 [129925] political      done. it
    @+129926 [129926] politicalize   q28 ? ␅
    @+129926 [129926] politicalize   q29 ? before
    @+129933 [129933] politicisation q26 ? ␅
    @+129933 [129933] politicisation q27 ? before
    @+129941 [129941] politicize     q24 ? ␅
    @+129941 [129941] politicize     q25 ? before
    @+129963 [129963] poll           q22 ? ␅
    @+129963 [129963] poll           q23 ? before
    @+130051 [130051] poly           q12 ? ␅
    @+130051 [130051] poly           q13 ? before
    @+131918 [131918] prealter       q10 ? ␅
    @+131918 [131918] prealter       q11 ? before
    @+134999 [134999] prop           q7  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1583 🥳 6 ⏱️ 0:01:57.929990

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:JUJUS n n n n n remain:5557
    ⬜⬜⬜⬜⬜ tried:MAGMA n n n n n remain:2127
    ⬜⬜⬜⬜⬜ tried:ICTIC n n n n n remain:698
    ⬜⬜⬜⬜⬜ tried:HOOKY n n n n n remain:102
    ⬜⬜🟩⬜⬜ tried:FEEZE n n Y n n remain:2
    🟨⬜🟩🟨⬜ tried:DWELL m n Y m n remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1726 🥳 18 ⏱️ 0:03:38.630157

📜 1 sessions
💰 score: 9800

    5/6
    NEARS 🟨⬜⬜⬜⬜
    COIGN ⬜⬜🟨⬜🟨
    LINDY ⬜🟨🟨⬜⬜
    INPUT 🟨🟩⬜🟨🟩
    UNFIT 🟩🟩🟩🟩🟩
    4/6
    UNFIT ⬜⬜⬜🟩🟩
    AMRIT ⬜🟨⬜🟩🟩
    VOMIT ⬜⬜🟩🟩🟩
    LIMIT 🟩🟩🟩🟩🟩
    3/6
    LIMIT ⬜🟨⬜⬜🟨
    THINS 🟨⬜🟩⬜🟨
    SPITE 🟩🟩🟩🟩🟩
    4/6
    SPITE ⬜⬜⬜⬜🟨
    DERAY ⬜🟩🟩⬜🟩
    FERNY 🟩🟩🟩⬜🟩
    FERRY 🟩🟩🟩🟩🟩
    Final 2/2
    AGLOW 🟨⬜⬜⬜⬜
    BRAKE 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1703 🥳 score:27 ⏱️ 0:02:12.182096

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SHEET attempts:6 score:6
2. BLAND attempts:5 score:5
3. JOIST attempts:9 score:9
4. GUAVA attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1703 🥳 score:61 ⏱️ 0:02:54.653177

📜 2 sessions

Octordle Classic

1. QUEEN attempts:10 score:10
2. CLANG attempts:7 score:7
3. POLKA attempts:3 score:3
4. FLORA attempts:5 score:5
5. CATCH attempts:11 score:12
6. DUSKY attempts:9 score:9
7. ALLOT attempts:4 score:4
8. GROSS attempts:11 score:11

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1683 🥳 score:34 ⏱️ 0:03:25.726519

📜 1 sessions

Sedecordle Classic sedecordle.com

1. SPOIL attempts:6 score:0
2. FETCH attempts:15 score:6
3. SANER attempts:4 score:0
4. ENEMY attempts:7 score:4
5. GAVEL attempts:11 score:1
6. IGLOO attempts:12 score:1
7. GOUGE attempts:10 score:1
8. FINER attempts:18 score:0
9. BUSED attempts:14 score:1
10. PANEL attempts:5 score:4
11. MAMBO attempts:13 score:1
12. SAUCY attempts:9 score:3
13. ASSET attempts:3 score:0
14. DECOR attempts:8 score:3
15. ROWER attempts:18 score:1
16. SHYLY attempts:16 score:8

# [squareword.org](squareword.org) 🧩 #1696 🥳 9 ⏱️ 0:05:53.943231

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟨 🟨
    🟨 🟩 🟨 🟨 🟨
    🟨 🟨 🟩 🟨 🟨
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T A M P
    P A P A L
    E R A S E
    C O C O A
    S T E N T

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1633 🥳 133 ⏱️ 0:04:07.877464

🤔 134 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 16 chat prompts
🤖 16 gemma4:12b replies
🔥   2 🥵   6 😎  16 🥶 103 🧊   6

      $1 #134 comfortable   100.00°C 🥳 1000‰ ~128 used:0 [127]  source:gemma4
      $2 #130 comfy          57.50°C 🔥  997‰   ~1 used:0 [0]    source:gemma4
      $3 #108 snug           47.02°C 🔥  992‰   ~2 used:3 [1]    source:gemma4
      $4  #96 comfort        43.55°C 🥵  987‰   ~7 used:4 [6]    source:gemma4
      $5 #126 relaxing       42.50°C 🥵  980‰   ~3 used:0 [2]    source:gemma4
      $6 #116 easy           41.08°C 🥵  972‰   ~4 used:0 [3]    source:gemma4
      $7  #86 cushy          39.49°C 🥵  955‰   ~8 used:4 [7]    source:gemma4
      $8  #88 luxurious      39.32°C 🥵  953‰   ~6 used:3 [5]    source:gemma4
      $9  #84 cozy           38.45°C 🥵  946‰   ~5 used:2 [4]    source:gemma4
     $10  #89 padded         35.86°C 😎  896‰   ~9 used:0 [8]    source:gemma4
     $11  #70 smooth         34.69°C 😎  862‰  ~24 used:3 [23]   source:gemma4
     $12  #83 plush          33.86°C 😎  834‰  ~23 used:2 [22]   source:gemma4
     $26 #107 refined        24.37°C 🥶        ~32 used:0 [31]   source:gemma4
    $129   #4 molecule       -1.07°C 🧊       ~129 used:0 [128]  source:gemma4

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1666 🥳 1160 ⏱️ 7:18:54.743341

🤔 1161 attempts
📜 1 sessions
🫧 94 chat sessions
⁉️ 534 chat prompts
🤖 67 llama3.2:latest replies
🤖 20 dolphin3:latest replies
🤖 447 gemma4:12b replies
🔥   5 🥵  28 😎 204 🥶 865 🧊  58

       $1 #1161 assimiler         100.00°C 🥳 1000‰ ~1103 used:0   [1102]  source:llama3.2
       $2  #940 considérer         51.82°C 🔥  997‰   ~14 used:64  [13]    source:llama3.2
       $3  #942 admettre           49.07°C 🔥  996‰   ~13 used:40  [12]    source:llama3.2
       $4  #952 justifier          46.73°C 🔥  993‰    ~3 used:23  [2]     source:llama3.2
       $5  #928 exclure            46.59°C 🔥  992‰    ~1 used:22  [0]     source:dolphin3
       $6 #1048 supposer           46.00°C 🔥  991‰    ~2 used:22  [1]     source:llama3.2
       $7  #343 constitutif        44.02°C 🥵  983‰  ~237 used:364 [236]   source:gemma4  
       $8 #1085 déterminer         41.10°C 🥵  975‰    ~4 used:3   [3]     source:llama3.2
       $9  #967 reconnaître        39.95°C 🥵  972‰    ~5 used:3   [4]     source:llama3.2
      $35  #242 fondement          35.98°C 😎  899‰   ~67 used:2   [66]    source:gemma4  
     $237  #103 administration     25.16°C 🥶        ~230 used:2   [229]   source:gemma4  
     $238  #576 congruent          25.16°C 😎    1‰  ~229 used:2   [228]   source:gemma4  
     $239   #69 influence          25.15°C 🥶        ~244 used:0   [243]   source:gemma4  
    $1104  #520 exemplaire         -0.18°C 🧊       ~1104 used:0   [1103]  source:gemma4  
