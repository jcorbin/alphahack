# 2026-03-09

- 🔗 spaceword.org 🧩 2026-03-08 🏁 score 2168 ranked 33.6% 112/333 ⏱️ 3:31:57.465150
- 🔗 alfagok.diginaut.net 🧩 #492 🥳 46 ⏱️ 0:00:52.366474
- 🔗 alphaguess.com 🧩 #959 🥳 20 ⏱️ 0:00:25.423163
- 🔗 dontwordle.com 🧩 #1385 😳 6 ⏱️ 0:01:36.416220
- 🔗 dictionary.com hurdle 🧩 #1528 🥳 15 ⏱️ 0:02:35.368690
- 🔗 Quordle Classic 🧩 #1505 🥳 score:24 ⏱️ 0:01:21.952372
- 🔗 Octordle Classic 🧩 #1505 🥳 score:66 ⏱️ 0:02:56.680972
- 🔗 squareword.org 🧩 #1498 🥳 8 ⏱️ 0:01:57.440338
- 🔗 cemantle.certitudes.org 🧩 #1435 🥳 912 ⏱️ 0:44:51.562182
- 🔗 cemantix.certitudes.org 🧩 #1468 🥳 130 ⏱️ 0:02:15.189622

# Dev

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








# [spaceword.org](spaceword.org) 🧩 2026-03-08 🏁 score 2168 ranked 33.6% 112/333 ⏱️ 3:31:57.465150

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 112/333

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ L I _ _ _ _ _   
      _ _ _ Y _ T _ _ _ _   
      _ _ _ E A U X _ _ _   
      _ _ _ _ K I _ _ _ _   
      _ _ _ D E L I _ _ _   
      _ _ _ _ B E _ _ _ _   
      _ _ _ _ I _ _ _ _ _   
      _ _ _ W A D Y _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #492 🥳 46 ⏱️ 0:00:52.366474

🤔 46 attempts
📜 2 sessions

    @        [     0] &-teken    
    @+199812 [199812] lijm       q0  ? ␅
    @+199812 [199812] lijm       q1  ? after
    @+299699 [299699] schub      q2  ? ␅
    @+299699 [299699] schub      q3  ? after
    @+349467 [349467] vakantie   q4  ? ␅
    @+349467 [349467] vakantie   q5  ? after
    @+374208 [374208] vrij       q6  ? ␅
    @+374208 [374208] vrij       q7  ? after
    @+380420 [380420] weer       q10 ? ␅
    @+380420 [380420] weer       q11 ? after
    @+380889 [380889] weg        q14 ? ␅
    @+380889 [380889] weg        q15 ? after
    @+382074 [382074] wei        q16 ? ␅
    @+382074 [382074] wei        q17 ? after
    @+382391 [382391] weledel    q20 ? ␅
    @+382391 [382391] weledel    q21 ? after
    @+382468 [382468] welig      q26 ? ␅
    @+382468 [382468] welig      q27 ? after
    @+382486 [382486] welkomst   q28 ? ␅
    @+382486 [382486] welkomst   q29 ? after
    @+382519 [382519] welkt      q30 ? ␅
    @+382519 [382519] welkt      q31 ? after
    @+382533 [382533] wellevend  q34 ? ␅
    @+382533 [382533] wellevend  q35 ? after
    @+382536 [382536] wellicht   q44 ? ␅
    @+382536 [382536] wellicht   q45 ? it
    @+382536 [382536] wellicht   done. it
    @+382537 [382537] welling    q40 ? ␅
    @+382537 [382537] welling    q41 ? before
    @+382538 [382538] wellington q37 ? before

# [alphaguess.com](alphaguess.com) 🧩 #959 🥳 20 ⏱️ 0:00:25.423163

🤔 20 attempts
📜 1 sessions

    @       [    0] aa     
    @+1     [    1] aah    
    @+2     [    2] aahed  
    @+3     [    3] aahing 
    @+47381 [47381] dis    q2  ? ␅
    @+47381 [47381] dis    q3  ? after
    @+72800 [72800] gremmy q4  ? ␅
    @+72800 [72800] gremmy q5  ? after
    @+75956 [75956] haw    q10 ? ␅
    @+75956 [75956] haw    q11 ? after
    @+76083 [76083] head   q18 ? ␅
    @+76083 [76083] head   q19 ? it
    @+76083 [76083] head   done. it
    @+76291 [76291] heart  q16 ? ␅
    @+76291 [76291] heart  q17 ? before
    @+76699 [76699] helio  q14 ? ␅
    @+76699 [76699] helio  q15 ? before
    @+77500 [77500] hetero q12 ? ␅
    @+77500 [77500] hetero q13 ? before
    @+79132 [79132] hood   q8  ? ␅
    @+79132 [79132] hood   q9  ? before
    @+85504 [85504] ins    q6  ? ␅
    @+85504 [85504] ins    q7  ? before
    @+98218 [98218] mach   q0  ? ␅
    @+98218 [98218] mach   q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1385 😳 6 ⏱️ 0:01:36.416220

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:PAPAW n n n n n remain:5916
    ⬜⬜⬜⬜⬜ tried:EGGED n n n n n remain:1942
    ⬜⬜⬜⬜⬜ tried:BOOMS n n n n n remain:250
    ⬜⬜⬜⬜⬜ tried:THUNK n n n n n remain:19
    ⬜⬜⬜🟩🟩 tried:CIVIC n n n Y Y remain:2
    🟩🟩🟩🟩🟩 tried:LYRIC Y Y Y Y Y remain:0

    Undos used: 4

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1528 🥳 15 ⏱️ 0:02:35.368690

📜 1 sessions
💰 score: 10100

    5/6
    SLATE ⬜⬜🟨🟨⬜
    TORAH 🟨⬜⬜🟨🟩
    BATCH ⬜🟩🟩🟩🟩
    MATCH ⬜🟩🟩🟩🟩
    WATCH 🟩🟩🟩🟩🟩
    3/6
    WATCH ⬜🟩⬜⬜⬜
    NARES 🟨🟩⬜⬜⬜
    MANGY 🟩🟩🟩🟩🟩
    3/6
    MANGY ⬜🟨🟩⬜⬜
    AUNTS 🟨⬜🟩⬜⬜
    FINAL 🟩🟩🟩🟩🟩
    3/6
    FINAL ⬜🟨⬜🟨🟨
    ALIST 🟨🟩🟨⬜⬜
    CLAIM 🟩🟩🟩🟩🟩
    Final 1/2
    YOUNG 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1505 🥳 score:24 ⏱️ 0:01:21.952372

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. WORDY attempts:7 score:7
2. PLUCK attempts:4 score:4
3. MOTTO attempts:5 score:5
4. DUMPY attempts:8 score:8

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1505 🥳 score:66 ⏱️ 0:02:56.680972

📜 1 sessions

Octordle Classic

1. FLAKE attempts:6 score:6
2. WAGON attempts:8 score:8
3. NINTH attempts:9 score:9
4. STOIC attempts:3 score:3
5. FLING attempts:7 score:7
6. CLANK attempts:10 score:10
7. MUCUS attempts:11 score:11
8. TATTY attempts:12 score:12

# [squareword.org](squareword.org) 🧩 #1498 🥳 8 ⏱️ 0:01:57.440338

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟨 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A E R I E
    O M E N S
    R A N T S
    T I A R A
    A L L O Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1435 🥳 912 ⏱️ 0:44:51.562182

🤔 913 attempts
📜 1 sessions
🫧 74 chat sessions
⁉️ 285 chat prompts
🤖 222 llama3.1:8b replies
🤖 26 falcon3:10b replies
🤖 37 dolphin3:latest replies
🔥   7 🥵  22 😎  56 🥶 814 🧊  13

      $1 #913 nonetheless        100.00°C 🥳 1000‰ ~900 used:0   [899]  source:llama3  
      $2 #906 though              60.16°C 🔥  998‰   ~4 used:2   [3]    source:llama3  
      $3 #893 admittedly          59.91°C 🔥  997‰   ~1 used:1   [0]    source:llama3  
      $4 #782 somewhat            58.22°C 🔥  995‰  ~27 used:31  [26]   source:llama3  
      $5 #891 however             57.49°C 🔥  994‰   ~5 used:4   [4]    source:llama3  
      $6 #892 but                 56.38°C 🔥  992‰   ~2 used:1   [1]    source:llama3  
      $7 #905 surprisingly        55.26°C 🔥  991‰   ~3 used:0   [2]    source:llama3  
      $8 #843 similarly           55.10°C 🔥  990‰  ~21 used:12  [20]   source:llama3  
      $9 #601 even                53.70°C 🥵  989‰  ~81 used:101 [80]   source:llama3  
     $10 #784 mildly              53.47°C 🥵  988‰  ~22 used:2   [21]   source:llama3  
     $11 #867 equally             53.06°C 🥵  987‰  ~23 used:2   [22]   source:llama3  
     $31 #900 notwithstanding     41.74°C 😎  897‰  ~28 used:0   [27]   source:llama3  
     $88 #546 unambitious         27.87°C 🥶       ~110 used:0   [109]  source:llama3  
    $901 #400 transport           -0.03°C 🧊       ~901 used:0   [900]  source:llama3  

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1468 🥳 130 ⏱️ 0:02:15.189622

🤔 131 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 31 chat prompts
🤖 31 dolphin3:latest replies
🔥  1 🥵  8 😎 16 🥶 96 🧊  9

      $1 #131 temple          100.00°C 🥳 1000‰ ~122 used:0  [121]  source:dolphin3
      $2 #127 mausolée         49.96°C 🔥  992‰   ~1 used:0  [0]    source:dolphin3
      $3 #100 basilique        45.17°C 🥵  973‰   ~6 used:4  [5]    source:dolphin3
      $4 #130 statue           44.46°C 🥵  968‰   ~2 used:0  [1]    source:dolphin3
      $5 #101 autel            43.13°C 🥵  959‰   ~8 used:5  [7]    source:dolphin3
      $6  #90 édifice          42.71°C 🥵  953‰   ~9 used:6  [8]    source:dolphin3
      $7 #105 chapelle         41.69°C 🥵  940‰   ~3 used:1  [2]    source:dolphin3
      $8 #122 tombeau          40.96°C 🥵  930‰   ~4 used:0  [3]    source:dolphin3
      $9  #98 monument         39.76°C 🥵  910‰   ~7 used:4  [6]    source:dolphin3
     $10 #121 tabernacle       39.54°C 🥵  906‰   ~5 used:0  [4]    source:dolphin3
     $11 #128 palais           38.52°C 😎  889‰  ~10 used:0  [9]    source:dolphin3
     $12 #104 cathédrale       38.29°C 😎  880‰  ~11 used:0  [10]   source:dolphin3
     $27  #56 antre            25.09°C 🥶        ~29 used:0  [28]   source:dolphin3
    $123   #8 tarte            -1.73°C 🧊       ~123 used:0  [122]  source:dolphin3
