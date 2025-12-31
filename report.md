# 2026-01-01

- 🔗 spaceword.org 🧩 2025-12-31 🏁 score 2168 ranked 29.4% 97/330 ⏱️ 0:18:24.126471
- 🔗 alfagok.diginaut.net 🧩 #425 🥳 15 ⏱️ 0:00:34.733039
- 🔗 alphaguess.com 🧩 #891 🥳 13 ⏱️ 0:00:25.294895
- 🔗 dontwordle.com 🧩 #1318 🥳 6 ⏱️ 0:01:53.968422
- 🔗 dictionary.com hurdle 🧩 #1461 🥳 19 ⏱️ 0:04:19.151438
- 🔗 Quordle Classic 🧩 #1438 🥳 score:20 ⏱️ 0:01:25.192336
- 🔗 Octordle Classic 🧩 #1438 🥳 score:62 ⏱️ 0:03:48.160921
- 🔗 squareword.org 🧩 #1431 🥳 8 ⏱️ 0:03:16.631799
- 🔗 cemantle.certitudes.org 🧩 #1368 🥳 161 ⏱️ 0:04:13.630716
- 🔗 cemantix.certitudes.org 🧩 #1401 🥳 117 ⏱️ 0:03:32.911476
- 🔗 Quordle Rescue 🧩 #52 🥳 score:22 ⏱️ 0:01:33.327882
- 🔗 Quordle Sequence 🧩 #1438 😦 score:28 ⏱️ 0:02:12.769069
- 🔗 Quordle Extreme 🧩 #521 😦 score:23 ⏱️ 0:01:51.740578
- 🔗 Octordle Rescue 🧩 #1438 😦 score:7 ⏱️ 0:04:51.656498
- 🔗 Octordle Sequence 🧩 #1438 🥳 score:67 ⏱️ 0:03:34.699492
- 🔗 Octordle Extreme 🧩 #1438 🥳 score:52 ⏱️ 0:03:22.761406

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







# spaceword.org 🧩 2025-12-31 🏁 score 2168 ranked 29.4% 97/330 ⏱️ 0:18:24.126471

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 97/330

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ A _ _ D _   
      _ C A Y _ J _ H I _   
      _ _ _ E L I X I R _   
      _ Q U A I S _ E L _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #425 🥳 15 ⏱️ 0:00:34.733039

🤔 15 attempts
📜 2 sessions

    @        [     0] &-teken       
    @+1      [     1] &-tekens      
    @+2      [     2] -cijferig     
    @+3      [     3] -e-mail       
    @+99758  [ 99758] ex            q1  ? after
    @+149454 [149454] huis          q2  ? after
    @+162009 [162009] izabel        q4  ? after
    @+168278 [168278] kano          q5  ? after
    @+171305 [171305] kennis        q6  ? after
    @+171519 [171519] kennisproject q9  ? after
    @+171611 [171611] kenteken      q10 ? after
    @+171672 [171672] keper         q11 ? after
    @+171701 [171701] keramist      q12 ? after
    @+171710 [171710] kerel         q14 ? it
    @+171710 [171710] kerel         done. it
    @+171716 [171716] keren         q13 ? before
    @+171732 [171732] kerk          q8  ? before
    @+172932 [172932] kervel        q7  ? before
    @+174561 [174561] kind          q3  ? before
    @+199833 [199833] lijm          q0  ? before

# alphaguess.com 🧩 #891 🥳 13 ⏱️ 0:00:25.294895

🤔 13 attempts
📜 1 sessions

    @        [     0] aa      
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98224  [ 98224] mach    q0  ? after
    @+147328 [147328] rho     q1  ? after
    @+159610 [159610] slug    q3  ? after
    @+165764 [165764] stint   q4  ? after
    @+168814 [168814] sulfur  q5  ? after
    @+170368 [170368] sustain q6  ? after
    @+171136 [171136] symbol  q7  ? after
    @+171519 [171519] synth   q8  ? after
    @+171581 [171581] syringe q10 ? after
    @+171595 [171595] syrup   q12 ? it
    @+171595 [171595] syrup   done. it
    @+171608 [171608] system  q11 ? before
    @+171650 [171650] tab     q9  ? before
    @+171928 [171928] tag     q2  ? before

# dontwordle.com 🧩 #1318 🥳 6 ⏱️ 0:01:53.968422

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MAMBA n n n n n remain:5774
    ⬜⬜⬜⬜⬜ tried:ZOOKS n n n n n remain:1415
    ⬜⬜⬜⬜⬜ tried:TUFTY n n n n n remain:400
    ⬜⬜⬜⬜🟨 tried:GRRRL n n n n m remain:58
    ⬜🟨🟨⬜🟨 tried:CELLI n m m n m remain:8
    🟨🟨⬜🟨⬜ tried:LINEN m m n m n remain:1

    Undos used: 3

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1461 🥳 19 ⏱️ 0:04:19.151438

📜 1 sessions
💰 score: 9700

    4/6
    LASER ⬜⬜⬜🟩⬜
    TONED ⬜🟩🟨🟩⬜
    COVEN ⬜🟩🟩🟩🟩
    WOVEN 🟩🟩🟩🟩🟩
    4/6
    WOVEN ⬜🟩⬜🟨⬜
    ROUSE ⬜🟩🟩⬜🟩
    LOUIE 🟨🟩🟩⬜🟩
    JOULE 🟩🟩🟩🟩🟩
    6/6
    JOULE ⬜🟨⬜⬜⬜
    IRONY ⬜⬜🟩⬜⬜
    SHOCK 🟩⬜🟩🟨⬜
    SCOTS 🟩🟩🟩⬜⬜
    SCOOP 🟩🟩🟩⬜⬜
    SCOFF 🟩🟩🟩🟩🟩
    3/6
    SCOFF ⬜🟨⬜⬜⬜
    CRATE 🟩⬜🟨⬜🟩
    CABLE 🟩🟩🟩🟩🟩
    Final 2/2
    STRAP 🟩🟩⬜🟨⬜
    STASH 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1438 🥳 score:20 ⏱️ 0:01:25.192336

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. ANODE attempts:3 score:3
2. AROSE attempts:4 score:4
3. VYING attempts:6 score:6
4. GAMMA attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1438 🥳 score:62 ⏱️ 0:03:48.160921

📜 1 sessions

Octordle Classic

1. TRUER attempts:7 score:7
2. ADMIN attempts:8 score:8
3. ETHIC attempts:9 score:9
4. WOVEN attempts:11 score:11
5. LOUSE attempts:6 score:6
6. HASTY attempts:13 score:13
7. THORN attempts:5 score:5
8. ENDOW attempts:3 score:3

# squareword.org 🧩 #1431 🥳 8 ⏱️ 0:03:16.631799

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P A T T Y
    E E R I E
    A R O M A
    R I P E R
    L E E R S

# cemantle.certitudes.org 🧩 #1368 🥳 161 ⏱️ 0:04:13.630716

🤔 162 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 25 chat prompts
🤖 25 dolphin3:latest replies
🔥   2 🥵   5 😎  10 🥶 127 🧊  17

      $1 #162   ~1 pledge          100.00°C 🥳 1000‰
      $2 #157   ~6 promise          67.24°C 🔥  998‰
      $3 #159   ~4 commitment       59.83°C 🔥  996‰
      $4 #155   ~7 pact             38.95°C 🥵  988‰
      $5 #151  ~10 covenant         37.90°C 🥵  985‰
      $6 #147  ~13 accord           37.65°C 🥵  984‰
      $7 #141  ~14 agreement        34.91°C 🥵  967‰
      $8 #161   ~2 guarantee        32.89°C 🥵  957‰
      $9 #113  ~17 support          24.30°C 😎  778‰
     $10 #160   ~3 dedication       23.97°C 😎  759‰
     $11  #12  ~18 carrot           22.72°C 😎  705‰
     $12 #123  ~16 foundation       22.01°C 😎  662‰
     $19  #42      stand            16.93°C 🥶
    $146 #103      tennis           -0.27°C 🧊

# cemantix.certitudes.org 🧩 #1401 🥳 117 ⏱️ 0:03:32.911476

🤔 118 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 18 chat prompts
🤖 18 dolphin3:latest replies
🔥  1 🥵  5 😎  5 🥶 67 🧊 39

      $1 #118   ~1 camarade        100.00°C 🥳 1000‰
      $2  #74   ~6 ami              47.00°C 🔥  996‰
      $3  #11  ~11 classe           36.48°C 🥵  977‰
      $4  #16   ~8 élève            36.28°C 🥵  975‰
      $5 #108   ~3 amitié           35.86°C 🥵  969‰
      $6  #15   ~9 récréation       34.59°C 🥵  953‰
      $7 #115   ~2 camaraderie      33.41°C 🥵  934‰
      $8 #102   ~4 amical           31.26°C 😎  868‰
      $9  #14  ~10 professeur       27.74°C 😎  674‰
     $10  #79   ~5 car              24.46°C 😎  302‰
     $11  #10  ~12 école            24.27°C 😎  273‰
     $12  #66   ~7 meeting          23.52°C 😎  119‰
     $13 #103      amicale          22.62°C 🥶
     $80  #89      montagne         -0.94°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #52 🥳 score:22 ⏱️ 0:01:33.327882

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. ADMIT attempts:5 score:5
2. BLURT attempts:6 score:6
3. WINDY attempts:7 score:7
4. STOMP attempts:4 score:4

# [Quordle Sequence](m-w.com/games/quordle/#/sequence) 🧩 #1438 😦 score:28 ⏱️ 0:02:12.769069

📜 1 sessions

Quordle Sequence m-w.com/games/quordle/

1. BEAST attempts:3 score:3
2. GRAVE attempts:7 score:7
3. GLYPH attempts:8 score:8
4. _ATCH -BDEFGLMPRSVWY attempts:10 score:-1

# [Quordle Extreme](m-w.com/games/quordle/#/extreme) 🧩 #521 😦 score:23 ⏱️ 0:01:51.740578

📜 2 sessions

Quordle Extreme m-w.com/games/quordle/

1. HAVEN attempts:3 score:3
2. STRAY attempts:4 score:4
3. BLARE attempts:8 score:8
4. _O__H ~C -ABEFGILMNRSTUVY attempts:8 score:-1

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1438 😦 score:7 ⏱️ 0:04:51.656498

📜 1 sessions

Octordle Rescue

1. GIVEN attempts:5 score:5
2. DENIM attempts:6 score:6
3. RENAL attempts:7 score:7
4. SHALL attempts:11 score:11
5. WHI__ -ACDEGLMNOPRSTUVY attempts:13 score:-1
6. STRAY attempts:10 score:10
7. DRAIN attempts:8 score:8
8. GULLY attempts:12 score:12

# [Octordle Sequence](britannica.com/games/octordle/daily-sequence) 🧩 #1438 🥳 score:67 ⏱️ 0:03:34.699492

📜 1 sessions

Octordle Sequence

1. TITHE attempts:4 score:4
2. AXIAL attempts:6 score:6
3. MANLY attempts:7 score:7
4. GRIEF attempts:8 score:8
5. ELITE attempts:9 score:9
6. DUCHY attempts:10 score:10
7. TRUTH attempts:11 score:11
8. FEWER attempts:12 score:12

# [Octordle Extreme](britannica.com/games/octordle/extreme) 🧩 #1438 🥳 score:52 ⏱️ 0:03:22.761406

📜 1 sessions

Octordle Extreme

1. ANNOY attempts:6 score:6
2. WISPY attempts:5 score:5
3. RISKY attempts:7 score:7
4. POLAR attempts:4 score:4
5. CODEX attempts:10 score:10
6. MISTY attempts:8 score:8
7. PINCH attempts:9 score:9
8. PLAIT attempts:3 score:3
