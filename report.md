# 2026-01-06

- 🔗 spaceword.org 🧩 2026-01-05 🏁 score 2168 ranked 38.8% 124/320 ⏱️ 0:12:05.887018
- 🔗 alfagok.diginaut.net 🧩 #430 🥳 10 ⏱️ 0:00:52.951182
- 🔗 alphaguess.com 🧩 #896 🥳 17 ⏱️ 0:00:57.511116
- 🔗 dontwordle.com 🧩 #1323 🥳 6 ⏱️ 0:03:37.824987
- 🔗 dictionary.com hurdle 🧩 #1466 🥳 17 ⏱️ 0:04:29.566548
- 🔗 Quordle Classic 🧩 #1443 🥳 score:19 ⏱️ 0:01:38.391871
- 🔗 Octordle Classic 🧩 #1443 🥳 score:57 ⏱️ 0:03:52.728559
- 🔗 squareword.org 🧩 #1436 🥳 8 ⏱️ 0:03:58.492845
- 🔗 cemantle.certitudes.org 🧩 #1373 🥳 55 ⏱️ 0:04:05.133782
- 🔗 cemantix.certitudes.org 🧩 #1406 🥳 153 ⏱️ 0:02:35.117019
- 🔗 Quordle Rescue 🧩 #57 🥳 score:25 ⏱️ 0:02:21.623913
- 🔗 Quordle Sequence 🧩 #1443 🥳 score:25 ⏱️ 0:01:32.353367

# Dev

## WIP

- hurdle: add novel words to wordlist

- meta: rework SolverHarness => Solver{ Library, Scope }

- ui:
  - Handle -- stabilizing core over Listing
  - Shell -- minimizing over Handle
- meta: rework command model over Shell

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












# spaceword.org 🧩 2026-01-05 🏁 score 2168 ranked 38.8% 124/320 ⏱️ 0:12:05.887018

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 124/320

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ O I K _ _ _ _   
      _ _ _ _ _ A A _ _ _   
      _ _ _ _ F U R _ _ _   
      _ _ _ M O R T _ _ _   
      _ _ _ _ X I S _ _ _   
      _ _ _ _ I _ Y _ _ _   
      _ _ _ _ E _ _ _ _ _   
      _ _ _ _ R E Z _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #430 🥳 10 ⏱️ 0:00:52.951182

🤔 10 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199833 [199833] lijm      q0  ? after
    @+247742 [247742] op        q2  ? after
    @+248072 [248072] opdracht  q9  ? it
    @+248072 [248072] opdracht  done. it
    @+248418 [248418] opening   q8  ? before
    @+249337 [249337] opgespeld q7  ? before
    @+250931 [250931] oproep    q6  ? before
    @+254147 [254147] out       q5  ? before
    @+260629 [260629] pater     q4  ? before
    @+273548 [273548] proef     q3  ? before
    @+299746 [299746] schub     q1  ? before

# alphaguess.com 🧩 #896 🥳 17 ⏱️ 0:00:57.511116

🤔 17 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+11764 [11764] back      q3  ? after
    @+11957 [11957] backs     q8  ? after
    @+12013 [12013] backstamp q12 ? after
    @+12042 [12042] backswing q15 ? after
    @+12054 [12054] backward  q16 ? it
    @+12054 [12054] backward  done. it
    @+12069 [12069] backwood  q11 ? before
    @+12179 [12179] baff      q7  ? before
    @+12598 [12598] ban       q6  ? before
    @+13802 [13802] be        q5  ? before
    @+17715 [17715] blind     q4  ? before
    @+23683 [23683] camp      q2  ? before
    @+47382 [47382] dis       q1  ? before
    @+98220 [98220] mach      q0  ? before

# dontwordle.com 🧩 #1323 🥳 6 ⏱️ 0:03:37.824987

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:7870
    ⬜⬜⬜⬜⬜ tried:FEEZE n n n n n remain:3607
    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:1544
    ⬜⬜⬜⬜⬜ tried:SHUSH n n n n n remain:250
    ⬜🟨⬜⬜⬜ tried:GRRRL n m n n n remain:10
    🟩🟩⬜⬜⬜ tried:ROBOT Y Y n n n remain:3

    Undos used: 4

      3 words remaining
    x 8 unused letters
    = 24 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1466 🥳 17 ⏱️ 0:04:29.566548

📜 2 sessions
💰 score: 9900

    5/6
    TALES ⬜⬜⬜⬜🟨
    SIRUP 🟨🟩⬜⬜⬜
    FISHY ⬜🟩🟩⬜⬜
    GISMO ⬜🟩🟩⬜🟨
    BISON 🟩🟩🟩🟩🟩
    3/6
    BISON 🟨⬜⬜🟨🟨
    EBONY ⬜🟨🟨🟨🟩
    NOBLY 🟩🟩🟩🟩🟩
    4/6
    NOBLY ⬜⬜⬜⬜⬜
    STAIR ⬜⬜⬜🟨🟨
    PRICE ⬜🟨🟩⬜🟨
    WEIRD 🟩🟩🟩🟩🟩
    4/6
    WEIRD ⬜⬜⬜🟨⬜
    ACROS ⬜⬜🟨🟩⬜
    TUMOR ⬜⬜🟨🟩🟨
    BROOM 🟩🟩🟩🟩🟩
    Final 1/2
    BOWIE 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1443 🥳 score:19 ⏱️ 0:01:38.391871

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. AMITY attempts:4 score:4
2. IMAGE attempts:3 score:3
3. LOATH attempts:5 score:5
4. WRUNG attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1443 🥳 score:57 ⏱️ 0:03:52.728559

📜 1 sessions

Octordle Classic

1. USAGE attempts:9 score:9
2. BOOZE attempts:10 score:10
3. ROWDY attempts:7 score:7
4. CARRY attempts:13 score:13
5. SPLAT attempts:3 score:3
6. SLEPT attempts:4 score:4
7. SPRAY attempts:5 score:5
8. RENEW attempts:6 score:6

# squareword.org 🧩 #1436 🥳 8 ⏱️ 0:03:58.492845

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C E D A R
    A R O S E
    V O D K A
    E D G E D
    R E E D Y

# cemantle.certitudes.org 🧩 #1373 🥳 55 ⏱️ 0:04:05.133782

🤔 56 attempts
📜 2 sessions
🫧 4 chat sessions
⁉️ 15 chat prompts
🤖 15 dolphin3:latest replies
🔥  1 🥵  3 😎  7 🥶 41 🧊  3

     $1 #56  ~1 dinner           100.00°C 🥳 1000‰
     $2 #53  ~4 supper            75.96°C 🔥  998‰
     $3 #55  ~2 dessert           58.27°C 🥵  985‰
     $4 #54  ~3 appetizer         50.03°C 🥵  969‰
     $5 #44  ~8 evening           47.46°C 🥵  957‰
     $6 #10 ~11 greet             32.41°C 😎  608‰
     $7 #52  ~5 sunset            28.77°C 😎  364‰
     $8  #5 ~12 greeting          26.74°C 😎  174‰
     $9 #12 ~10 hello             25.68°C 😎   47‰
    $10 #22  ~9 handshake         25.59°C 😎   37‰
    $11 #47  ~6 gown              25.44°C 😎   16‰
    $12 #45  ~7 bedtime           25.35°C 😎    8‰
    $13 #34     kiss              23.28°C 🥶
    $54  #7     oracle            -1.26°C 🧊

# cemantix.certitudes.org 🧩 #1406 🥳 153 ⏱️ 0:02:35.117019

🤔 154 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 27 chat prompts
🤖 27 dolphin3:latest replies
🔥   1 🥵   4 😎  16 🥶 114 🧊  18

      $1 #154   ~1 fondateur        100.00°C 🥳 1000‰
      $2  #53  ~13 fondation         45.57°C 🔥  994‰
      $3 #140   ~4 tradition         34.41°C 🥵  952‰
      $4 #146   ~3 historique        33.85°C 🥵  947‰
      $5  #35  ~16 héritage          32.40°C 🥵  916‰
      $6  #51  ~14 concept           32.33°C 🥵  913‰
      $7  #60  ~11 fondement         30.81°C 😎  875‰
      $8 #102   ~6 création          30.53°C 😎  864‰
      $9  #85  ~10 penseur           30.11°C 😎  844‰
     $10 #130   ~5 institution       28.07°C 😎  732‰
     $11  #20  ~20 philosophie       27.92°C 😎  722‰
     $12  #59  ~12 fondamental       27.83°C 😎  719‰
     $23  #82      filiation         22.05°C 🥶
    $137 #108      restauration      -0.07°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #57 🥳 score:25 ⏱️ 0:02:21.623913

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. CHOIR attempts:7 score:7
2. STINT attempts:9 score:9
3. BADLY attempts:5 score:5
4. ANGRY attempts:4 score:4

# [Quordle Sequence](m-w.com/games/quordle/#/sequence) 🧩 #1443 🥳 score:25 ⏱️ 0:01:32.353367

📜 1 sessions

Quordle Sequence m-w.com/games/quordle/

1. WEIGH attempts:4 score:4
2. NAVAL attempts:6 score:6
3. LURCH attempts:7 score:7
4. ABOUT attempts:8 score:8
