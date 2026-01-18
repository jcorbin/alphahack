# 2026-01-19

- 🔗 spaceword.org 🧩 2026-01-18 🏁 score 2173 ranked 7.7% 24/312 ⏱️ 0:19:59.137783
- 🔗 alfagok.diginaut.net 🧩 #443 🥳 16 ⏱️ 0:00:38.030611
- 🔗 alphaguess.com 🧩 #910 🥳 17 ⏱️ 0:00:41.343100
- 🔗 dontwordle.com 🧩 #1336 🥳 6 ⏱️ 0:01:37.244331
- 🔗 dictionary.com hurdle 🧩 #1479 🥳 18 ⏱️ 0:03:14.867684
- 🔗 Quordle Classic 🧩 #1456 🥳 score:22 ⏱️ 0:01:16.615856
- 🔗 Octordle Classic 🧩 #1456 🥳 score:57 ⏱️ 0:02:55.506257
- 🔗 squareword.org 🧩 #1449 🥳 8 ⏱️ 0:02:10.662924
- 🔗 cemantle.certitudes.org 🧩 #1386 🥳 1088 ⏱️ 2:27:01.879387
- 🔗 cemantix.certitudes.org 🧩 #1419 🥳 68 ⏱️ 0:00:44.104994
- 🔗 Quordle Rescue 🧩 #70 🥳 score:24 ⏱️ 0:01:51.030769
- 🔗 Octordle Rescue 🧩 #1456 🥳 score:8 ⏱️ 0:04:06.938956

# Dev

## WIP

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




# [spaceword.org](spaceword.org) 🧩 2026-01-18 🏁 score 2173 ranked 7.7% 24/312 ⏱️ 0:19:59.137783

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 24/312

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ T _ _ Z _ T A X I   
      _ E _ A E R O B I C   
      _ E V E N E R _ _ Y   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #443 🥳 16 ⏱️ 0:00:38.030611

🤔 16 attempts
📜 1 sessions

    @        [     0] &-teken           
    @+1      [     1] &-tekens          
    @+2      [     2] -cijferig         
    @+3      [     3] -e-mail           
    @+199832 [199832] lijm              q0  ? after
    @+223778 [223778] molest            q3  ? after
    @+235752 [235752] odeur             q4  ? after
    @+238792 [238792] on                q5  ? after
    @+239577 [239577] onder             q8  ? after
    @+240227 [240227] onderlossers      q9  ? after
    @+240551 [240551] ondersneeuw       q10 ? after
    @+240714 [240714] ondertunnelde     q11 ? after
    @+240794 [240794] ondervraging      q12 ? after
    @+240806 [240806] onderwater        q13 ? after
    @+240841 [240841] onderwaterzetting q14 ? after
    @+240854 [240854] onderwerp         q15 ? it
    @+240854 [240854] onderwerp         done. it
    @+240876 [240876] onderwijs         q7  ? before
    @+243262 [243262] onroerend         q6  ? before
    @+247734 [247734] op                q2  ? before
    @+299737 [299737] schub             q1  ? before

# [alphaguess.com](alphaguess.com) 🧩 #910 🥳 17 ⏱️ 0:00:41.343100

🤔 17 attempts
📜 3 sessions

    @        [     0] aa          
    @+1      [     1] aah         
    @+2      [     2] aahed       
    @+3      [     3] aahing      
    @+98220  [ 98220] mach        q0  ? after
    @+98220  [ 98220] mach        q1  ? after
    @+147373 [147373] rhotic      q2  ? after
    @+171643 [171643] ta          q3  ? after
    @+172223 [172223] tam         q8  ? after
    @+172300 [172300] tamper      q11 ? after
    @+172331 [172331] tang        q12 ? after
    @+172331 [172331] tang        q13 ? after
    @+172358 [172358] tanginesses q14 ? after
    @+172360 [172360] tangle      q16 ? it
    @+172360 [172360] tangle      done. it
    @+172371 [172371] tango       q15 ? before
    @+172385 [172385] tank        q10 ? before
    @+172558 [172558] tar         q9  ? before
    @+172904 [172904] taw         q7  ? before
    @+174192 [174192] term        q6  ? before
    @+176814 [176814] toil        q5  ? before
    @+182008 [182008] un          q4  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1336 🥳 6 ⏱️ 0:01:37.244331

📜 1 sessions
💰 score: 5

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:PYGMY n n n n n remain:6857
    ⬜⬜⬜⬜⬜ tried:BESES n n n n n remain:1221
    ⬜⬜⬜⬜⬜ tried:VOLVA n n n n n remain:129
    ⬜⬜⬜⬜⬜ tried:WHIFF n n n n n remain:11
    🟨🟨⬜⬜⬜ tried:KUDZU m m n n n remain:4
    ⬜🟩🟩⬜🟩 tried:CRUCK n Y Y n Y remain:1

    Undos used: 2

      1 words remaining
    x 5 unused letters
    = 5 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1479 🥳 18 ⏱️ 0:03:14.867684

📜 1 sessions
💰 score: 9800

    4/6
    AGERS ⬜⬜🟨⬜🟨
    STOPE 🟨⬜🟨⬜🟩
    DOUSE ⬜🟩⬜🟩🟩
    NOISE 🟩🟩🟩🟩🟩
    3/6
    NOISE 🟨⬜⬜🟩🟩
    MANSE ⬜⬜🟩🟩🟩
    TENSE 🟩🟩🟩🟩🟩
    5/6
    TENSE 🟨🟨⬜⬜🟨
    LITER ⬜⬜🟨🟨🟨
    AVERT ⬜⬜🟩🟨🟩
    CREPT 🟨🟩🟩⬜🟩
    ERECT 🟩🟩🟩🟩🟩
    5/6
    ERECT 🟨🟨⬜⬜⬜
    RAPES 🟨⬜⬜🟨⬜
    DIRGE ⬜⬜🟩⬜🟨
    FERNY ⬜🟩🟩🟨⬜
    HERON 🟩🟩🟩🟩🟩
    Final 1/2
    BORNE 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1456 🥳 score:22 ⏱️ 0:01:16.615856

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. EBONY attempts:4 score:4
2. ALTAR attempts:6 score:6
3. SALTY attempts:5 score:5
4. FALSE attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1456 🥳 score:57 ⏱️ 0:02:55.506257

📜 1 sessions

Octordle Classic

1. CHUNK attempts:3 score:3
2. UTTER attempts:8 score:8
3. ADORE attempts:9 score:9
4. REHAB attempts:5 score:5
5. SNEAK attempts:4 score:4
6. TRAIN attempts:7 score:7
7. PENNY attempts:11 score:11
8. MANGY attempts:10 score:10

# [squareword.org](squareword.org) 🧩 #1449 🥳 8 ⏱️ 0:02:10.662924

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟩
    🟩 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B A S I L
    E L U D E
    A G I L E
    T A T E R
    S E E D Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1386 🥳 1088 ⏱️ 2:27:01.879387

🤔 1089 attempts
📜 2 sessions
🫧 91 chat sessions
⁉️ 431 chat prompts
🤖 343 dolphin3:latest replies
🤖 20 llama3.3:latest replies
🤖 9 gemma3:27b replies
🤖 34 mixtral:8x7b replies
🤖 24 falcon3:10b replies
😱   1 🔥   6 🥵  38 😎 122 🥶 817 🧊 104

       $1 #1089    ~1 soccer           100.00°C 🥳 1000‰
       $2 #1080   ~10 football          73.14°C 😱  999‰
       $3 #1073   ~16 basketball        68.11°C 🔥  998‰
       $4 #1085    ~5 lacrosse          64.38°C 🔥  995‰
       $5 #1082    ~8 hockey            62.71°C 🔥  994‰
       $6  #310  ~115 tennis            61.63°C 🔥  993‰
       $7 #1075   ~14 baseball          58.14°C 🔥  992‰
       $8  #885   ~37 athletics         51.15°C 🔥  991‰
       $9  #460   ~78 gymnastics        48.76°C 🥵  989‰
      $10  #168  ~149 golf              48.32°C 🥵  988‰
      $11 #1088    ~2 rugby             47.84°C 🥵  987‰
      $47  #419   ~91 nordic            30.69°C 😎  894‰
     $169   #99       drama             16.93°C 🥶
     $986  #574       sole              -0.10°C 🧊

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1419 🥳 68 ⏱️ 0:00:44.104994

🤔 69 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 10 chat prompts
🤖 10 dolphin3:latest replies
🥵  2 😎  9 🥶 52 🧊  5

     $1 #69  ~1 aile           100.00°C 🥳 1000‰
     $2 #12 ~11 ciel            39.04°C 🥵  967‰
     $3 #24  ~8 vent            37.10°C 🥵  947‰
     $4 #44  ~5 tourbillon      32.63°C 😎  832‰
     $5 #51  ~3 firmament       32.61°C 😎  829‰
     $6 #45  ~4 air             30.65°C 😎  719‰
     $7 #27  ~7 bourrasque      30.55°C 😎  712‰
     $8 #14 ~10 nuage           30.24°C 😎  694‰
     $9  #7 ~12 soleil          27.75°C 😎  428‰
    $10 #29  ~6 crête           27.61°C 😎  413‰
    $11 #63  ~2 vol             26.11°C 😎  201‰
    $12 #20  ~9 brume           25.38°C 😎   57‰
    $13 #15     étoile          24.71°C 🥶
    $65 #65     éclatement      -0.83°C 🧊


# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #70 🥳 score:24 ⏱️ 0:01:51.030769

📜 2 sessions

Quordle Rescue m-w.com/games/quordle/

1. PITHY attempts:4 score:4
2. SHYLY attempts:5 score:5
3. TRACK attempts:8 score:8
4. HUMAN attempts:7 score:7

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1456 🥳 score:8 ⏱️ 0:04:06.938956

📜 1 sessions

Octordle Rescue

1. TRACT attempts:7 score:7
2. VOILA attempts:12 score:12
3. PEDAL attempts:13 score:13
4. SWASH attempts:9 score:9
5. BUTTE attempts:5 score:5
6. CROSS attempts:10 score:10
7. STRUT attempts:11 score:11
8. KEBAB attempts:8 score:8
