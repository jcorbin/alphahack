# 2025-12-29

- 🔗 spaceword.org 🧩 2025-12-28 🏁 score 2170 ranked 28.3% 98/346 ⏱️ 0:18:56.749060
- 🔗 alfagok.diginaut.net 🧩 #422 🥳 26 ⏱️ 0:01:30.064914
- 🔗 alphaguess.com 🧩 #888 🥳 13 ⏱️ 0:00:25.279099
- 🔗 dontwordle.com 🧩 #1315 🥳 6 ⏱️ 0:01:19.208368
- 🔗 dictionary.com hurdle 🧩 #1458 🥳 17 ⏱️ 0:03:12.759950
- 🔗 Quordle Classic 🧩 #1435 🥳 score:22 ⏱️ 0:01:26.464527
- 🔗 Octordle Classic 🧩 #1435 🥳 score:60 ⏱️ 0:05:44.279403
- 🔗 squareword.org 🧩 #1428 🥳 8 ⏱️ 0:02:17.854859
- 🔗 cemantle.certitudes.org 🧩 #1365 🥳 214 ⏱️ 1:31:25.037599
- 🔗 cemantix.certitudes.org 🧩 #1398 🥳 439 ⏱️ 3:00:28.224730
- 🔗 Quordle Rescue 🧩 #49 🥳 score:22 ⏱️ 0:01:41.470301
- 🔗 Quordle Extreme 🧩 #518 🥳 score:26 ⏱️ 0:02:03.845855
- 🔗 Quordle Sequence 🧩 #1435 🥳 score:25 ⏱️ 0:02:19.383202
- 🔗 Octordle Extreme 🧩 #1435 🥳 score:63 ⏱️ 0:08:27.302745
- 🔗 Octordle Rescue 🧩 #1435 🥳 score:9 ⏱️ 0:05:37.288634
- 🔗 Octordle Sequence 🧩 #1435 🥳 score:68 ⏱️ 0:04:39.116938

# Dev

## WIP

- ui:
  - Handle -- stabilizing core over Listing
  - Shell -- minimizing over Handle

- meta: rework command model over Shell

## TODO

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




# spaceword.org 🧩 2025-12-28 🏁 score 2170 ranked 28.3% 98/346 ⏱️ 0:18:56.749060

📜 3 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 98/346

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ U N F I X _ _   
      _ _ _ K _ E S _ _ _   
      _ _ _ E _ M O _ _ _   
      _ _ _ _ Z A P _ _ _   
      _ _ _ _ _ L O _ _ _   
      _ _ _ U R E D O _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #422 🥳 26 ⏱️ 0:01:30.064914

🤔 26 attempts
📜 4 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199833 [199833] lijm      q0  ? after
    @+211724 [211724] mdxxi     q12 ? .
    @+211724 [211724] mdxxi     q13 ? .
    @+211724 [211724] mdxxi     q14 ? .
    @+211737 [211737] me        q16 ? after
    @+214701 [214701] melodie   q18 ? after
    @+214776 [214776] memo      q22 ? after
    @+214814 [214814] men       q23 ? after
    @+214830 [214830] mende     q24 ? after
    @+214845 [214845] meneer    q25 ? it
    @+214845 [214845] meneer    done. it
    @+214859 [214859] meng      q21 ? before
    @+215034 [215034] mens      q20 ? before
    @+216034 [216034] met       q19 ? before
    @+217674 [217674] mijmer    q17 ? before
    @+223624 [223624] mol       q3  ? before
    @+247742 [247742] op        q2  ? before
    @+299746 [299746] schub     q1  ? before

# alphaguess.com 🧩 #888 🥳 13 ⏱️ 0:00:25.279099

🤔 13 attempts
📜 1 sessions

    @        [     0] aa      
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98224  [ 98224] mach    q0  ? after
    @+147328 [147328] rho     q1  ? after
    @+159610 [159610] slug    q3  ? after
    @+161112 [161112] sold    q6  ? after
    @+161875 [161875] sound   q7  ? after
    @+161915 [161915] soup    q11 ? after
    @+161931 [161931] sour    q12 ? it
    @+161931 [161931] sour    done. it
    @+161964 [161964] sous    q10 ? before
    @+162055 [162055] sovkhoz q9  ? before
    @+162236 [162236] span    q8  ? before
    @+162643 [162643] speed   q5  ? before
    @+165764 [165764] stint   q4  ? before
    @+171928 [171928] tag     q2  ? before

# dontwordle.com 🧩 #1315 🥳 6 ⏱️ 0:01:19.208368

📜 1 sessions
💰 score: 27

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:COOCH n n n n n remain:6849
    ⬜⬜⬜⬜⬜ tried:ABAKA n n n n n remain:2618
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:990
    ⬜⬜⬜⬜⬜ tried:TUTUS n n n n n remain:158
    🟨⬜⬜⬜⬜ tried:IMMIX m n n n n remain:55
    ⬜🟩⬜🟩⬜ tried:NINNY n Y n Y n remain:3

    Undos used: 3

      3 words remaining
    x 9 unused letters
    = 27 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1458 🥳 17 ⏱️ 0:03:12.759950

📜 1 sessions
💰 score: 9900

    3/6
    REALS ⬜🟨⬜⬜⬜
    MONDE ⬜🟩🟨⬜🟨
    WOKEN 🟩🟩🟩🟩🟩
    4/6
    WOKEN ⬜⬜⬜⬜⬜
    TAILS ⬜⬜⬜🟨🟨
    BLUSH ⬜🟩🟩🟩🟩
    PLUSH 🟩🟩🟩🟩🟩
    4/6
    PLUSH ⬜🟩🟩⬜⬜
    FLUME 🟩🟩🟩⬜⬜
    FLUYT 🟩🟩🟩⬜⬜
    FLUID 🟩🟩🟩🟩🟩
    5/6
    FLUID ⬜⬜⬜⬜⬜
    ROAMS ⬜⬜⬜⬜⬜
    CHEWY ⬜⬜🟨⬜⬜
    BEGET ⬜🟩⬜🟩🟨
    TEPEE 🟩🟩🟩🟩🟩
    Final 1/2
    PULSE 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1435 🥳 score:22 ⏱️ 0:01:26.464527

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. DOUBT attempts:4 score:4
2. BLISS attempts:5 score:5
3. TIGER attempts:6 score:6
4. AMONG attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1435 🥳 score:60 ⏱️ 0:05:44.279403

📜 2 sessions

Octordle Classic

1. TITLE attempts:9 score:9
2. COUPE attempts:5 score:5
3. ALIBI attempts:10 score:10
4. LUPUS attempts:7 score:7
5. OPINE attempts:6 score:6
6. SLURP attempts:4 score:4
7. MANGA attempts:11 score:11
8. LOWLY attempts:8 score:8

# squareword.org 🧩 #1428 🥳 8 ⏱️ 0:02:17.854859

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S L A M S
    L E G A L
    A G A P E
    T I T L E
    S T E E P

# cemantle.certitudes.org 🧩 #1365 🥳 214 ⏱️ 1:31:25.037599

🤔 215 attempts
📜 2 sessions
🫧 17 chat sessions
⁉️ 33 chat prompts
🤖 33 qwq:latest replies
😱   1 🔥   6 🥵   6 😎  23 🥶 170 🧊   8

      $1 #215   ~1 lodge          100.00°C 🥳 1000‰
      $2 #214   ~2 inn             54.84°C 😱  999‰
      $3 #213   ~3 guesthouse      52.61°C 🔥  997‰
      $4 #203  ~12 lodging         51.22°C 🔥  996‰
      $5 #172  ~18 campground      50.63°C 🔥  995‰
      $6 #171  ~19 campsite        49.06°C 🔥  994‰
      $7 #208   ~8 hotel           46.82°C 🔥  992‰
      $8 #207   ~9 hostel          46.33°C 🔥  991‰
      $9 #118  ~28 camping         40.62°C 🥵  983‰
     $10 #209   ~7 motel           39.76°C 🥵  979‰
     $11 #206  ~10 accommodation   38.27°C 🥵  976‰
     $15 #116  ~29 trail           30.41°C 😎  862‰
     $38  #14      cathedral       20.83°C 🥶
    $208 #119      bag             -0.47°C 🧊

# cemantix.certitudes.org 🧩 #1398 🥳 439 ⏱️ 3:00:28.224730

🤔 440 attempts
📜 1 sessions
🫧 72 chat sessions
⁉️ 155 chat prompts
🤖 63 dolphin3:latest replies
🤖 92 qwq:latest replies
🔥   2 🥵  11 😎  53 🥶 288 🧊  85

      $1 #440   ~1 élite              100.00°C 🥳 1000‰
      $2 #431   ~7 bourgeoisie         55.67°C 😱  999‰
      $3 #436   ~4 aristocratie        52.66°C 🔥  995‰
      $4 #324  ~29 idéologie           46.14°C 🥵  984‰
      $5 #189  ~52 minorité            45.94°C 🥵  983‰
      $6 #386  ~17 nation              45.57°C 🥵  982‰
      $7 #284  ~35 démocratisation     45.09°C 🥵  981‰
      $8 #350  ~26 idéologique         43.92°C 🥵  973‰
      $9 #318  ~31 politique           43.40°C 🥵  968‰
     $10  #97  ~63 populaire           43.14°C 🥵  963‰
     $11 #432   ~6 dominant            39.65°C 🥵  932‰
     $15 #387  ~16 nationalisme        37.58°C 😎  893‰
     $68 #264      cohésion            26.53°C 🥶
    $356 #335      climatique          -0.30°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #49 🥳 score:22 ⏱️ 0:01:41.470301

📜 2 sessions

Quordle Rescue m-w.com/games/quordle/

1. FRAUD attempts:5 score:5
2. AGENT attempts:4 score:4
3. TEMPO attempts:7 score:7
4. SWORN attempts:6 score:6

# [Quordle Extreme](m-w.com/games/quordle/#/extreme) 🧩 #518 🥳 score:26 ⏱️ 0:02:03.845855

📜 2 sessions

Quordle Extreme m-w.com/games/quordle/

1. ROUND attempts:6 score:6
2. SWEET attempts:8 score:8
3. RUMOR attempts:5 score:5
4. ROYAL attempts:7 score:7

# [Quordle Sequence](m-w.com/games/quordle/#/sequence) 🧩 #1435 🥳 score:25 ⏱️ 0:02:19.383202

📜 2 sessions

Quordle Sequence m-w.com/games/quordle/

1. SHOVE attempts:4 score:4
2. TRACE attempts:5 score:5
3. BOSSY attempts:7 score:7
4. WEEDY attempts:9 score:9

# [Octordle Extreme](britannica.com/games/octordle/extreme) 🧩 #1435 🥳 score:63 ⏱️ 0:08:27.302745

📜 4 sessions

Octordle Extreme

1. CHESS attempts:4 score:4
2. BOSUN attempts:5 score:5
3. GLAND attempts:7 score:7
4. EXTRA attempts:12 score:12
5. RAZOR attempts:10 score:10
6. GAFFE attempts:8 score:8
7. JUDGE attempts:6 score:6
8. SMOTE attempts:11 score:11

# [Octordle Rescue](britannica.com/games/octordle/rescue) 🧩 #1435 🥳 score:9 ⏱️ 0:05:37.288634

📜 2 sessions

Octordle Rescue

1. MUNCH attempts:6 score:6
2. LAUGH attempts:7 score:7
3. CAROL attempts:8 score:8
4. COAST attempts:9 score:9
5. NATAL attempts:10 score:10
6. OLDEN attempts:3 score:5
7. THIRD attempts:11 score:11
8. DOWNY attempts:12 score:12

# [Octordle Sequence](britannica.com/games/octordle/sequence) 🧩 #1435 🥳 score:68 ⏱️ 0:04:39.116938

📜 3 sessions

Octordle Sequence

1. RAJAH attempts:5 score:5
2. WHEEL attempts:6 score:6
3. LLAMA attempts:7 score:7
4. GRAND attempts:8 score:8
5. EVENT attempts:9 score:9
6. VERGE attempts:10 score:10
7. CREED attempts:8 score:11
8. SHAWL attempts:9 score:12
