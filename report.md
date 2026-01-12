# 2026-01-13

- 🔗 spaceword.org 🧩 2026-01-12 🏁 score 2172 ranked 28.6% 94/329 ⏱️ 0:05:12.736375
- 🔗 alfagok.diginaut.net 🧩 #437 🥳 21 ⏱️ 0:00:49.233684
- 🔗 alphaguess.com 🧩 #904 🥳 12 ⏱️ 0:00:23.900843
- 🔗 dictionary.com hurdle 🧩 #1473 🥳 20 ⏱️ 0:03:46.784244
- 🔗 dontwordle.com 🧩 #1330 🥳 6 ⏱️ 0:01:37.304900
- 🔗 squareword.org 🧩 #1443 🥳 9 ⏱️ 0:03:33.688838
- 🔗 cemantle.certitudes.org 🧩 #1380 🥳 161 ⏱️ 0:03:12.823433
- 🔗 cemantix.certitudes.org 🧩 #1413 🥳 86 ⏱️ 0:02:00.725156
- 🔗 Quordle Classic 🧩 #1450 🥳 score:23 ⏱️ 0:01:19.800467
- 🔗 Octordle Classic 🧩 #1450 🥳 score:53 ⏱️ 0:02:45.745829
- 🔗 Quordle Rescue 🧩 #64 🥳 score:25 ⏱️ 0:01:46.891715
- 🔗 Octordle Rescue 🧩 #1450 🥳 score:8 ⏱️ 0:05:50.171942
- 🔗 Quordle Sequence 🧩 #1450 🥳 score:27 ⏱️ 0:02:02.228062
- 🔗 Octordle Sequence 🧩 #1450 🥳 score:58 ⏱️ 0:03:07.499281

# Dev

## WIP

- hurdle: add novel words to wordlist

- meta:
  - rework SolverHarness => Solver{ Library, Scope }
  - variants: regression on 01-06 running quordle

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


















# spaceword.org 🧩 2026-01-11 🏗️ score 2173 current ranking 42/308 ⏱️ 8:04:00.125934

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 42/308

      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ O P _ P O G O E D
      _ W E K A _ _ _ _ O
      _ L _ A D J U R E S
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _



# [spaceword.org](spaceword.org) 🧩 2026-01-12 🏁 score 2172 ranked 28.6% 94/329 ⏱️ 0:05:12.736375

📜 2 sessions
- tiles: 21/21
- score: 2172 bonus: +72
- rank: 94/329

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ H _ _ Y O D _   
      _ _ _ I N H E R E _   
      _ _ _ K A I Z E N _   
      _ _ W E E S _ _ E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #437 🥳 21 ⏱️ 0:00:49.233684

🤔 21 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+1      [     1] &-tekens     
    @+2      [     2] -cijferig    
    @+3      [     3] -e-mail      
    @+24910  [ 24910] bad          q3  ? after
    @+31127  [ 31127] begeleid     q5  ? after
    @+34010  [ 34010] beleid       q6  ? after
    @+35661  [ 35661] beoordeling  q7  ? after
    @+36500  [ 36500] berichten    q8  ? after
    @+36588  [ 36588] berk         q10 ? after
    @+36680  [ 36680] berm         q11 ? after
    @+36739  [ 36739] bernhardtiti q15 ? after
    @+36756  [ 36756] beroem       q16 ? after
    @+36757  [ 36757] beroemd      q20 ? it
    @+36757  [ 36757] beroemd      done. it
    @+36758  [ 36758] beroemde     q19 ? before
    @+36764  [ 36764] beroemdst    q18 ? before
    @+36771  [ 36771] beroepen     q17 ? before
    @+36795  [ 36795] beroeps      q9  ? before
    @+37361  [ 37361] bescherm     q4  ? before
    @+49846  [ 49846] boks         q2  ? before
    @+99755  [ 99755] ex           q1  ? before
    @+199830 [199830] lijm         q0  ? before

# [alphaguess.com](alphaguess.com) 🧩 #904 🥳 12 ⏱️ 0:00:23.900843

🤔 12 attempts
📜 1 sessions

    @        [     0] aa      
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98220  [ 98220] mach    q0  ? after
    @+147373 [147373] rhotic  q1  ? after
    @+171643 [171643] ta      q2  ? after
    @+182008 [182008] un      q3  ? after
    @+189270 [189270] vicar   q4  ? after
    @+192874 [192874] whir    q5  ? after
    @+192911 [192911] whisk   q10 ? after
    @+192923 [192923] whisper q11 ? it
    @+192923 [192923] whisper done. it
    @+192950 [192950] whit    q9  ? before
    @+193182 [193182] wicca   q8  ? before
    @+193490 [193490] win     q7  ? before
    @+194699 [194699] worship q6  ? before

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1473 🥳 20 ⏱️ 0:03:46.784244

📜 1 sessions
💰 score: 9600

    4/6
    READS ⬜🟨⬜⬜⬜
    TONEY ⬜🟨⬜🟨⬜
    GLOVE ⬜🟩🟩🟩🟩
    CLOVE 🟩🟩🟩🟩🟩
    4/6
    CLOVE 🟨⬜🟨⬜⬜
    TORCH 🟩🟩⬜🟨⬜
    TONIC 🟩🟩⬜🟩🟩
    TOPIC 🟩🟩🟩🟩🟩
    6/6
    TOPIC ⬜⬜⬜⬜⬜
    DEARS 🟨🟨🟨🟨⬜
    BREAD ⬜🟨🟨🟨🟨
    FADER ⬜🟨🟩🟩🟩
    ALDER 🟩⬜🟩🟩🟩
    ADDER 🟩🟩🟩🟩🟩
    4/6
    ADDER 🟨⬜⬜⬜🟨
    TAROS ⬜🟨🟨⬜⬜
    BRAIN ⬜🟨🟩⬜⬜
    CHARM 🟩🟩🟩🟩🟩
    Final 2/2
    ERECT 🟨🟨⬜🟨🟩
    RECUT 🟩🟩🟩🟩🟩

# [dontwordle.com](dontwordle.com) 🧩 #1330 🥳 6 ⏱️ 0:01:37.304900

📜 1 sessions
💰 score: 21

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:EDGED n n n n n remain:5334
    ⬜⬜⬜⬜⬜ tried:MIMIC n n n n n remain:2330
    ⬜⬜⬜⬜⬜ tried:JUKUS n n n n n remain:531
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:178
    ⬜⬜⬜⬜🟩 tried:PHPHT n n n n Y remain:20
    🟩⬜⬜⬜🟩 tried:AVANT Y n n n Y remain:3

    Undos used: 3

      3 words remaining
    x 7 unused letters
    = 21 total score

# [squareword.org](squareword.org) 🧩 #1443 🥳 9 ⏱️ 0:03:33.688838

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P A S M
    L O T T O
    O P T E D
    O P I N E
    P A C T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1380 🥳 161 ⏱️ 0:03:12.823433

🤔 162 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 26 chat prompts
🤖 26 dolphin3:latest replies
😱   1 🔥   3 🥵  18 😎  31 🥶 105 🧊   3

      $1 #162   ~1 molecular         100.00°C 🥳 1000‰
      $2 #148   ~5 molecule           71.30°C 😱  999‰
      $3 #131  ~12 intracellular      62.99°C 🔥  996‰
      $4  #58  ~34 protein            61.57°C 🔥  995‰
      $5  #44  ~38 enzyme             59.53°C 🔥  991‰
      $6  #78  ~23 enzymatic          58.00°C 🥵  986‰
      $7  #87  ~21 protease           57.13°C 🥵  981‰
      $8  #34  ~42 receptor           56.78°C 🥵  980‰
      $9  #40  ~39 metabolic          56.63°C 🥵  977‰
     $10  #53  ~35 kinase             56.02°C 🥵  965‰
     $11 #101  ~17 gene               54.90°C 🥵  953‰
     $24 #107  ~14 operon             51.32°C 😎  890‰
     $55 #137      cellular           38.80°C 🥶
    $160 #152      raft               -0.39°C 🧊

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1413 🥳 86 ⏱️ 0:02:00.725156

🤔 87 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 28 chat prompts
🤖 28 dolphin3:latest replies
🔥  3 🥵  2 😎 14 🥶 52 🧊 15

     $1 #87  ~1 pause            100.00°C 🥳 1000‰
     $2 #39 ~16 minute            45.34°C 🔥  996‰
     $3 #38 ~17 heure             43.30°C 🔥  994‰
     $4 #51 ~12 temps             42.33°C 🔥  993‰
     $5 #69  ~4 moment            32.98°C 🥵  966‰
     $6 #37 ~18 semaine           29.38°C 🥵  906‰
     $7 #62  ~8 instant           27.50°C 😎  842‰
     $8 #40 ~15 seconde           25.61°C 😎  771‰
     $9 #61  ~9 minuterie         24.41°C 😎  695‰
    $10 #59 ~10 minuteur          23.79°C 😎  662‰
    $11 #86  ~2 interruption      23.55°C 😎  643‰
    $12 #63  ~7 bref              23.11°C 😎  612‰
    $21 #31     mois              18.45°C 🥶
    $73  #3     champ             -0.27°C 🧊

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1450 🥳 score:23 ⏱️ 0:01:19.800467

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. BILLY attempts:8 score:8
2. BOSSY attempts:5 score:5
3. EXIST attempts:4 score:4
4. BIRTH attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1450 🥳 score:53 ⏱️ 0:02:45.745829

📜 1 sessions

Octordle Classic

1. ZEBRA attempts:6 score:6
2. GRILL attempts:4 score:4
3. ETHER attempts:8 score:8
4. IMPEL attempts:11 score:11
5. SPURT attempts:9 score:9
6. BEGUN attempts:3 score:3
7. ESTER attempts:7 score:7
8. ULTRA attempts:5 score:5

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #64 🥳 score:25 ⏱️ 0:01:46.891715

📜 2 sessions

Quordle Rescue m-w.com/games/quordle/

1. RELAY attempts:7 score:7
2. RIGHT attempts:7 score:8
3. MODEL attempts:6 score:6
4. BLEEP attempts:4 score:4

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1450 🥳 score:8 ⏱️ 0:05:50.171942

📜 2 sessions

Octordle Rescue

1. NOOSE attempts:10 score:13
2. FLUID attempts:5 score:5
3. FILTH attempts:6 score:6
4. MYRRH attempts:7 score:7
5. SCOLD attempts:8 score:8
6. WINCE attempts:11 score:11
7. FLAKY attempts:12 score:12
8. MOUSE attempts:9 score:9

# [Quordle Sequence](m-w.com/games/quordle/#/sequence) 🧩 #1450 🥳 score:27 ⏱️ 0:02:02.228062

📜 2 sessions

Quordle Sequence m-w.com/games/quordle/

1. TROVE attempts:5 score:5
2. TIGER attempts:6 score:6
3. RUGBY attempts:7 score:7
4. TRITE attempts:9 score:9

# [Octordle Sequence](britannica.com/games/octordle/daily-sequence) 🧩 #1450 🥳 score:58 ⏱️ 0:03:07.499281

📜 1 sessions

Octordle Sequence

1. DUMPY attempts:3 score:3
2. SKIMP attempts:4 score:4
3. ABHOR attempts:6 score:6
4. SUPER attempts:7 score:7
5. SLUMP attempts:8 score:8
6. PLATE attempts:9 score:9
7. LANCE attempts:10 score:10
8. TILDE attempts:11 score:11
