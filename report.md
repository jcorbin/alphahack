# 2026-10-02

- 🔗 spaceword.org 🧩 2026-10-01 🏁 score 2165 ranked 54.6% 185/339 ⏱️ 0:42:24.456282
- 🔗 wordgrid 🧩 #853 🟪 rarity:0.32 ⏱️ 0:05:43.304025
- 🔗 alfagok.diginaut.net 🧩 #699 🥳 22 ⏱️ 0:00:34.401260
- 🔗 alphaguess.com 🧩 #1166 🥳 22 ⏱️ 0:00:26.916426
- 🔗 dontwordle.com 🧩 #1592 🥳 6 ⏱️ 0:01:45.565779
- 🔗 dictionary.com hurdle 🧩 #1735 🥳 22 ⏱️ 0:03:53.573273
- 🔗 Quordle Classic 🧩 #1712 🥳 score:19 ⏱️ 0:01:11.603970
- 🔗 Octordle Classic 🧩 #1712 🥳 score:64 ⏱️ 0:01:46.719120
- 🔗 Sedecordle Classic 🧩 #1692 🥳 score:51 ⏱️ 0:03:56.387526
- 🔗 squareword.org 🧩 #1705 🥳 7 ⏱️ 0:02:06.952559
- 🔗 cemantle.certitudes.org 🧩 #1642 😦 1064 ⏱️ 6:07:03.855533
- 🔗 cemantix.certitudes.org 🧩 #1675 🥳 198 ⏱️ 0:19:04.818939

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












# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #853 🟪 rarity:0.32 ⏱️ 0:05:43.304025

📜 2 sessions
🦄 🌌 🌌
🌌 🌌 🦄
🌌 🌌 🌌
Rarity: 0.32 🟪

# [spaceword.org](spaceword.org) 🧩 2026-10-01 🏁 score 2165 ranked 54.6% 185/339 ⏱️ 0:42:24.456282

📜 3 sessions
- tiles: 21/21
- score: 2165 bonus: +65
- rank: 185/339

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ W _ _ _ D _ _   
      _ _ _ A _ J _ E _ _   
      _ _ _ Z _ A _ N _ _   
      _ _ _ O _ P S I _ _   
      _ _ _ O L E A _ _ _   
      _ _ _ _ O R G _ _ _   
      _ _ _ _ _ Y O _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #699 🥳 22 ⏱️ 0:00:34.401260

🤔 22 attempts
📜 1 sessions

    @        [     0] &-teken        
    @+1      [     1] &-tekens       
    @+2      [     2] -cijferig      
    @+3      [     3] -e-mail        
    @+786    [   786] aan            q10 ? ␅
    @+786    [   786] aan            q11 ? after
    @+2747   [  2747] aanlokkelijk   q14 ? ␅
    @+2747   [  2747] aanlokkelijk   q15 ? after
    @+3705   [  3705] aanstel        q16 ? ␅
    @+3705   [  3705] aanstel        q17 ? after
    @+4209   [  4209] aanvloog       q18 ? ␅
    @+4209   [  4209] aanvloog       q19 ? after
    @+4461   [  4461] aanwijzing     q20 ? ␅
    @+4461   [  4461] aanwijzing     q21 ? it
    @+4461   [  4461] aanwijzing     done. it
    @+4713   [  4713] aardappelschil q12 ? ␅
    @+4713   [  4713] aardappelschil q13 ? before
    @+8646   [  8646] af             q8  ? ␅
    @+8646   [  8646] af             q9  ? before
    @+24874  [ 24874] bad            q6  ? ␅
    @+24874  [ 24874] bad            q7  ? before
    @+49802  [ 49802] boks           q4  ? ␅
    @+49802  [ 49802] boks           q5  ? before
    @+99672  [ 99672] ex             q2  ? ␅
    @+99672  [ 99672] ex             q3  ? before
    @+199528 [199528] lij            q0  ? ␅
    @+199528 [199528] lij            q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1166 🥳 22 ⏱️ 0:00:26.916426

🤔 22 attempts
📜 1 sessions

    @       [    0] aa      
    @+1     [    1] aah     
    @+2     [    2] aahed   
    @+3     [    3] aahing  
    @+1398  [ 1398] acrogen q12 ? ␅
    @+1398  [ 1398] acrogen q13 ? after
    @+1616  [ 1616] ad      q16 ? ␅
    @+1616  [ 1616] ad      q17 ? after
    @+1857  [ 1857] adjudge q18 ? ␅
    @+1857  [ 1857] adjudge q19 ? after
    @+1971  [ 1971] admit   q20 ? ␅
    @+1971  [ 1971] admit   q21 ? it
    @+1971  [ 1971] admit   done. it
    @+2097  [ 2097] ads     q14 ? ␅
    @+2097  [ 2097] ads     q15 ? before
    @+2802  [ 2802] ag      q10 ? ␅
    @+2802  [ 2802] ag      q11 ? before
    @+5876  [ 5876] angel   q8  ? ␅
    @+5876  [ 5876] angel   q9  ? before
    @+11763 [11763] back    q6  ? ␅
    @+11763 [11763] back    q7  ? before
    @+23680 [23680] camp    q4  ? ␅
    @+23680 [23680] camp    q5  ? before
    @+47374 [47374] dis     q2  ? ␅
    @+47374 [47374] dis     q3  ? before
    @+98142 [98142] mac     q0  ? ␅
    @+98142 [98142] mac     q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1592 🥳 6 ⏱️ 0:01:45.565779

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:TUTUS n n n n n remain:4338
    ⬜⬜⬜⬜⬜ tried:MAGMA n n n n n remain:1564
    ⬜⬜⬜⬜⬜ tried:OXBOW n n n n n remain:565
    ⬜⬜⬜⬜⬜ tried:JINNI n n n n n remain:169
    ⬜🟩⬜⬜⬜ tried:DRYLY n Y n n n remain:7
    ⬜🟩🟩🟨⬜ tried:FREER n Y Y m n remain:2

    Undos used: 3

      2 words remaining
    x 7 unused letters
    = 14 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1735 🥳 22 ⏱️ 0:03:53.573273

📜 1 sessions
💰 score: 9400

    5/6
    SERAL ⬜⬜🟩⬜⬜
    TORIC ⬜🟩🟩⬜⬜
    PORNY ⬜🟩🟩🟨⬜
    KOMBU ⬜🟩🟨⬜⬜
    MORON 🟩🟩🟩🟩🟩
    6/6
    MORON ⬜⬜🟨⬜⬜
    RIALS 🟨⬜🟨⬜⬜
    GREAT ⬜🟩🟩🟩⬜
    CAFES ⬜🟨⬜🟨⬜
    BREAD ⬜🟩🟩🟩⬜
    WREAK 🟩🟩🟩🟩🟩
    6/6
    WREAK ⬜⬜🟨⬜⬜
    ISLET 🟨⬜⬜🟨⬜
    DOGIE ⬜🟩⬜🟩🟩
    BENCH ⬜🟨⬜⬜⬜
    MOVIE 🟩🟩⬜🟩🟩
    MOXIE 🟩🟩🟩🟩🟩
    4/6
    MOXIE ⬜🟨⬜🟨⬜
    ICONS 🟨🟨🟨⬜🟨
    PIKED ⬜🟩⬜⬜🟨
    DISCO 🟩🟩🟩🟩🟩
    Final 1/2
    COMMA 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1712 🥳 score:19 ⏱️ 0:01:11.603970

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. IVORY attempts:5 score:5
2. SADLY attempts:4 score:4
3. ANGEL attempts:3 score:3
4. LLAMA attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1712 🥳 score:64 ⏱️ 0:01:46.719120

📜 1 sessions

Octordle Classic

1. LITHE attempts:5 score:5
2. SHORT attempts:6 score:6
3. REFER attempts:9 score:9
4. VOUCH attempts:10 score:10
5. WRITE attempts:4 score:4
6. ANGEL attempts:7 score:7
7. SPEED attempts:12 score:12
8. PENNY attempts:11 score:11

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1692 🥳 score:51 ⏱️ 0:03:56.387526

📜 2 sessions

Sedecordle Classic sedecordle.com

1. BUSED attempts:7 score:0
2. HOMER attempts:9 score:7
3. BASIL attempts:6 score:0
4. MORON attempts:8 score:6
5. PLUSH attempts:5 score:0
6. PLANT attempts:10 score:5
7. NERDY attempts:11 score:1
8. LUMEN attempts:12 score:1
9. HEART attempts:17 score:1
10. FROST attempts:13 score:8
11. CHIEF attempts:14 score:1
12. SPARK attempts:15 score:4
13. SLUMP attempts:16 score:1
14. LEVER attempts:17 score:6
15. CANDY attempts:17 score:1
16. MELON attempts:17 score:9

# [squareword.org](squareword.org) 🧩 #1705 🥳 7 ⏱️ 0:02:06.952559

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A C T E D
    V O I L A
    A R M O R
    I N E P T
    L Y R E S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1642 😦 1064 ⏱️ 6:07:03.855533

🤔 1063 attempts
📜 8 sessions
🫧 85 chat sessions
⁉️ 446 chat prompts
🤖 52 nemotron-3-nano:30b-cloud replies
🤖 80 gemma4:26b replies
🤖 83 gemma4:12b replies
🤖 55 dolphin3:latest replies
🤖 23 ornith-1.5:35b replies
🤖 152 llama3.2:latest replies
🤖 1 qwen3.8:latest replies
😦 😱    1 🔥    5 🥵   52 😎  166 🥶  831 🧊    8

       $1  #219 miraculously         59.13°C 😱  999‰   ~22 used:583 [21]    source:gemma4:12b
       $2  #190 magically            54.12°C 🔥  998‰  ~213 used:252 [212]   source:gemma4:12b
       $3  #884 actually             53.22°C 🔥  997‰    ~8 used:26  [7]     source:gemma4:26b
       $4  #609 hopelessly           49.70°C 🔥  994‰   ~49 used:76  [48]    source:llama3.2  
       $5 #1033 supposedly           49.61°C 🔥  993‰    ~1 used:10  [0]     source:nemotron  
       $6  #904 evidently            49.31°C 🔥  992‰    ~7 used:21  [6]     source:nemotron  
       $7  #902 seemingly            48.78°C 🥵  989‰    ~9 used:3   [8]     source:nemotron  
       $8  #865 simply               48.65°C 🥵  988‰   ~16 used:4   [15]    source:gemma4:26b
       $9  #974 surely               48.33°C 🥵  986‰   ~10 used:3   [9]     source:nemotron  
      $10  #772 horribly             47.69°C 🥵  985‰   ~38 used:7   [37]    source:gemma4:26b
      $11  #684 ultimately           47.61°C 🥵  984‰   ~39 used:7   [38]    source:llama3.2  
      $59  #188 mystically           40.17°C 😎  899‰  ~217 used:4   [216]   source:gemma4:12b
     $225  #324 wondrous             30.40°C 🥶        ~231 used:0   [230]   source:dolphin3  
    $1056  #742 outstanding          -0.60°C 🧊       ~1056 used:0   [1055]  source:dolphin3  

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1675 🥳 198 ⏱️ 0:19:04.818939

🤔 199 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 57 chat prompts
🤖 37 dolphin3:latest replies
🤖 20 gemma4:12b replies
😱   1 🔥   2 🥵  11 😎  28 🥶 130 🧊  26

      $1 #199 micro           100.00°C 🥳 1000‰ ~173 used:0  [172]  source:dolphin3
      $2 #185 microphone       57.46°C 😱  999‰   ~1 used:2  [0]    source:dolphin3
      $3 #191 écouteur         43.76°C 🔥  996‰   ~2 used:2  [1]    source:dolphin3
      $4 #145 stéréophonique   41.51°C 🔥  993‰   ~8 used:31 [7]    source:dolphin3
      $5 #186 mixage           39.14°C 🥵  988‰   ~3 used:0  [2]    source:dolphin3
      $6 #139 stéréo           38.71°C 🥵  986‰  ~32 used:19 [31]   source:dolphin3
      $7 #140 ampli            38.23°C 🥵  983‰  ~12 used:6  [11]   source:dolphin3
      $8 #130 audio            36.76°C 🥵  977‰  ~13 used:6  [12]   source:dolphin3
      $9 #132 sonorisation     34.96°C 🥵  968‰   ~9 used:4  [8]    source:dolphin3
     $10 #149 amplificateur    33.95°C 🥵  961‰  ~10 used:4  [9]    source:dolphin3
     $11 #174 hifi             33.36°C 🥵  955‰   ~4 used:1  [3]    source:dolphin3
     $16 #143 surround         28.35°C 😎  888‰  ~14 used:0  [13]   source:dolphin3
     $44 #133 sonorité         16.81°C 🥶        ~45 used:0  [44]   source:dolphin3
    $174   #1 brouillon        -0.06°C 🧊       ~174 used:0  [173]  source:gemma4  

