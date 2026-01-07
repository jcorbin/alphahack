# 2026-01-08

- 🔗 spaceword.org 🧩 2026-01-07 🏁 score 2172 ranked 17.2% 59/343 ⏱️ 1:13:35.452464
- 🔗 alfagok.diginaut.net 🧩 #432 🥳 18 ⏱️ 0:00:48.582942
- 🔗 alphaguess.com 🧩 #898 🥳 13 ⏱️ 0:00:34.262746
- 🔗 dontwordle.com 🧩 #1325 🥳 6 ⏱️ 0:01:37.615941
- 🔗 dictionary.com hurdle 🧩 #1468 🥳 17 ⏱️ 0:02:59.207646
- 🔗 Quordle Classic 🧩 #1445 🥳 score:24 ⏱️ 0:02:24.665144
- 🔗 Octordle Classic 🧩 #1445 🥳 score:53 ⏱️ 0:03:10.831157
- 🔗 squareword.org 🧩 #1438 🥳 7 ⏱️ 0:02:09.752056
- 🔗 cemantle.certitudes.org 🧩 #1375 🥳 24 ⏱️ 0:00:23.849494
- 🔗 cemantix.certitudes.org 🧩 #1408 🥳 69 ⏱️ 0:01:55.871586
- 🔗 Quordle Rescue 🧩 #59 🥳 score:22 ⏱️ 0:01:36.742311
- 🔗 Quordle Sequence 🧩 #1445 🥳 score:22 ⏱️ 0:01:20.135659
- 🔗 Octordle Rescue 🧩 #1445 🥳 score:8 ⏱️ 0:03:32.910236

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














# spaceword.org 🧩 2026-01-07 🏁 score 2172 ranked 17.2% 59/343 ⏱️ 1:13:35.452464

📜 5 sessions
- tiles: 21/21
- score: 2172 bonus: +72
- rank: 59/343

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ C U E _ W _ L _   
      _ _ U _ _ H I _ O _   
      _ _ T U P I K _ D _   
      _ _ _ N A T I V E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #432 🥳 18 ⏱️ 0:00:48.582942

🤔 18 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199833 [199833] lijm      q0  ? after
    @+205746 [205746] maas      q12 ? after
    @+205823 [205823] maat      q17 ? it
    @+205823 [205823] maat      done. it
    @+205898 [205898] maats     q16 ? before
    @+206170 [206170] macht     q15 ? before
    @+206970 [206970] mais      q14 ? before
    @+208258 [208258] mar       q13 ? before
    @+211730 [211730] me        q11 ? before
    @+223617 [223617] mol       q3  ? before
    @+247735 [247735] op        q2  ? before
    @+299739 [299739] schub     q1  ? before

# alphaguess.com 🧩 #898 🥳 13 ⏱️ 0:00:34.262746

🤔 13 attempts
📜 1 sessions

    @        [     0] aa         
    @+1      [     1] aah        
    @+2      [     2] aahed      
    @+3      [     3] aahing     
    @+98220  [ 98220] mach       q0  ? after
    @+122783 [122783] parr       q2  ? after
    @+135074 [135074] proper     q3  ? after
    @+135753 [135753] provincial q7  ? after
    @+136057 [136057] psycho     q8  ? after
    @+136241 [136241] pube       q9  ? after
    @+136253 [136253] public     q12 ? it
    @+136253 [136253] public     done. it
    @+136275 [136275] publish    q11 ? before
    @+136308 [136308] pud        q10 ? before
    @+136434 [136434] pul        q6  ? before
    @+137794 [137794] quart      q5  ? before
    @+140523 [140523] rec        q4  ? before
    @+147373 [147373] rhotic     q1  ? before

# dontwordle.com 🧩 #1325 🥳 6 ⏱️ 0:01:37.615941

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:SHUSH n n n n n remain:4857
    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:2640
    ⬜⬜⬜⬜⬜ tried:WOOPY n n n n n remain:778
    ⬜⬜⬜⬜🟨 tried:GRRRL n n n n m remain:122
    ⬜🟩🟩⬜⬜ tried:ALACK n Y Y n n remain:10
    ⬜🟩🟩⬜🟩 tried:ELATE n Y Y n Y remain:3

    Undos used: 2

      3 words remaining
    x 8 unused letters
    = 24 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1468 🥳 17 ⏱️ 0:02:59.207646

📜 1 sessions
💰 score: 9900

    5/6
    RATES 🟨🟨⬜⬜⬜
    ALGOR 🟨⬜⬜⬜🟨
    BRAID ⬜🟩🟩⬜⬜
    PRANK ⬜🟩🟩⬜⬜
    CRAZY 🟩🟩🟩🟩🟩
    4/6
    CRAZY ⬜⬜⬜⬜🟩
    LINDY ⬜⬜⬜⬜🟩
    EMPTY 🟩⬜🟨⬜🟩
    EPOXY 🟩🟩🟩🟩🟩
    4/6
    EPOXY ⬜⬜⬜⬜⬜
    TRAIL ⬜⬜🟩⬜⬜
    SNACK 🟨⬜🟩⬜⬜
    QUASH 🟩🟩🟩🟩🟩
    2/6
    QUASH ⬜⬜⬜🟨🟩
    SMITH 🟩🟩🟩🟩🟩
    Final 2/2
    UNCLE 🟨⬜🟨⬜🟩
    DEUCE 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1445 🥳 score:24 ⏱️ 0:02:24.665144

📜 3 sessions

Quordle Classic m-w.com/games/quordle/

1. STUDY attempts:5 score:5
2. COYLY attempts:8 score:8
3. UNTIE attempts:4 score:4
4. LOWLY attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1445 🥳 score:53 ⏱️ 0:03:10.831157

📜 1 sessions

Octordle Classic

1. ENSUE attempts:3 score:3
2. CHART attempts:6 score:6
3. ANGST attempts:7 score:7
4. AWAIT attempts:5 score:5
5. ISSUE attempts:2 score:2
6. CRIER attempts:9 score:9
7. TRAIT attempts:11 score:11
8. GAVEL attempts:10 score:10

# squareword.org 🧩 #1438 🥳 7 ⏱️ 0:02:09.752056

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S N E A K
    H O R D E
    E V A D E
    E A S E L
    R E E D S

# cemantle.certitudes.org 🧩 #1375 🥳 24 ⏱️ 0:00:23.849494

🤔 25 attempts
📜 1 sessions
🫧 1 chat sessions
⁉️ 5 chat prompts
🤖 5 dolphin3:latest replies
🔥  1 😎  3 🥶 17 🧊  3

     $1 #25  ~1 backup     100.00°C 🥳 1000‰
     $2 #24  ~2 storage     38.86°C 🔥  992‰
     $3  #6  ~5 computer    20.51°C 😎  487‰
     $4 #11  ~4 hardware    20.44°C 😎  482‰
     $5 #17  ~3 software    19.08°C 😎  302‰
     $6 #13     keyboard    17.59°C 🥶
     $7 #14     monitor     13.43°C 🥶
     $8 #15     mouse       12.06°C 🥶
     $9 #16     network     10.35°C 🥶
    $10  #7     guitar       8.71°C 🥶
    $11 #21     operating    8.68°C 🥶
    $12  #1     bird         7.00°C 🥶
    $13 #23     ram          6.28°C 🥶
    $23 #10     pizza       -1.93°C 🧊

# cemantix.certitudes.org 🧩 #1408 🥳 69 ⏱️ 0:01:55.871586

🤔 70 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 19 chat prompts
🤖 19 dolphin3:latest replies
🔥  1 🥵  4 😎 10 🥶 36 🧊 18

     $1 #70  ~1 transformation        100.00°C 🥳 1000‰
     $2 #68  ~3 changement             52.85°C 🔥  995‰
     $3 #42 ~13 construction           46.76°C 🥵  988‰
     $4 #41 ~14 développement          44.70°C 🥵  981‰
     $5 #69  ~2 métamorphose           42.20°C 🥵  970‰
     $6 #47 ~11 urbain                 38.75°C 🥵  924‰
     $7 #49 ~10 organisation           37.53°C 😎  897‰
     $8 #28 ~16 travail                35.00°C 😎  806‰
     $9 #60  ~7 internationalisation   34.32°C 😎  772‰
    $10 #62  ~5 innovation             33.10°C 😎  697‰
    $11 #61  ~6 économie               30.91°C 😎  523‰
    $12 #46 ~12 rénovation             30.00°C 😎  441‰
    $17 #37     culture                26.67°C 🥶
    $53  #5     musique                -0.47°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #59 🥳 score:22 ⏱️ 0:01:36.742311

📜 4 sessions

Quordle Rescue m-w.com/games/quordle/

1. WREAK attempts:5 score:5
2. GREED attempts:6 score:6
3. DIMLY attempts:7 score:7
4. WIDOW attempts:4 score:4

# [Quordle Sequence](m-w.com/games/quordle/#/sequence) 🧩 #1445 🥳 score:22 ⏱️ 0:01:20.135659

📜 1 sessions

Quordle Sequence m-w.com/games/quordle/

1. POUCH attempts:4 score:4
2. ASSAY attempts:5 score:5
3. HILLY attempts:6 score:6
4. TABLE attempts:7 score:7

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1445 🥳 score:8 ⏱️ 0:03:32.910236

📜 2 sessions

Octordle Rescue

1. WOULD attempts:5 score:5
2. BOSSY attempts:6 score:6
3. PRIMO attempts:11 score:11
4. SHOVE attempts:12 score:12
5. PECAN attempts:8 score:8
6. FORTH attempts:9 score:9
7. DOING attempts:13 score:13
8. BALER attempts:7 score:7
