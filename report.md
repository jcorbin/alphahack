# 2025-12-24

- 🔗 spaceword.org 🧩 2025-12-23 🏁 score 2173 ranked 6.6% 23/347 ⏱️ 0:59:39.431299
- 🔗 alfagok.diginaut.net 🧩 #417 🥳 14 ⏱️ 0:00:50.319473
- 🔗 alphaguess.com 🧩 #883 🥳 10 ⏱️ 0:00:27.175523
- 🔗 squareword.org 🧩 #1423 🥳 9 ⏱️ 0:03:03.019816
- 🔗 dictionary.com hurdle 🧩 #1453 😦 18 ⏱️ 0:03:37.490338
- 🔗 dontwordle.com 🧩 #1310 🥳 6 ⏱️ 0:01:55.150697
- 🔗 Quordle Classic 🧩 #1430 🥳 score:20 ⏱️ 0:01:55.126245
- 🔗 Octordle Classic 🧩 #1430 🥳 score:58 ⏱️ 0:07:58.809067
- 🔗 cemantle.certitudes.org 🧩 #1360 🥳 113 ⏱️ 0:09:22.314930
- 🔗 cemantix.certitudes.org 🧩 #1393 🥳 118 ⏱️ 0:07:37.928284

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

# spaceword.org 🧩 2025-12-23 🏁 score 2173 ranked 6.6% 23/347 ⏱️ 0:59:39.431299

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 23/347

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ I _ J U S S I V E   
      _ R _ _ _ H O _ O W   
      _ E D U C A B L E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# alfagok.diginaut.net 🧩 #417 🥳 14 ⏱️ 0:00:50.319473

🤔 14 attempts
📜 1 sessions

    @        [     0] &-teken        
    @+1      [     1] &-tekens       
    @+2      [     2] -cijferig      
    @+3      [     3] -e-mail        
    @+99758  [ 99758] ex             q1  ? after
    @+111413 [111413] ge             q3  ? after
    @+130434 [130434] gracieuze      q4  ? after
    @+139791 [139791] hei            q5  ? after
    @+144560 [144560] hoek           q6  ? after
    @+146221 [146221] hoofd          q7  ? after
    @+147011 [147011] hoofdslagaders q9  ? after
    @+147293 [147293] hoog           q11 ? after
    @+147545 [147545] hoogopgeleid   q12 ? after
    @+147664 [147664] hoogte         q13 ? it
    @+147664 [147664] hoogte         done. it
    @+147799 [147799] hooi           q8  ? before
    @+149453 [149453] huis           q2  ? before
    @+199835 [199835] lijm           q0  ? before

# alphaguess.com 🧩 #883 🥳 10 ⏱️ 0:00:27.175523

🤔 10 attempts
📜 1 sessions

    @        [     0] aa      
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98225  [ 98225] mach    q0  ? after
    @+122110 [122110] par     q2  ? after
    @+134641 [134641] prog    q3  ? after
    @+140527 [140527] rec     q4  ? after
    @+143790 [143790] rem     q5  ? after
    @+145203 [145203] res     q6  ? after
    @+145733 [145733] respade q8  ? after
    @+145853 [145853] rest    q9  ? it
    @+145853 [145853] rest    done. it
    @+146262 [146262] retest  q7  ? before
    @+147329 [147329] rho     q1  ? before

# squareword.org 🧩 #1423 🥳 9 ⏱️ 0:03:03.019816

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟩 🟨
    🟨 🟩 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟩
    🟩 🟨 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P A G E D
    E L U D E
    A L I G N
    L O D E S
    S W E D E

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1453 😦 18 ⏱️ 0:03:37.490338

📜 1 sessions
💰 score: 4880

    3/6
    TESLA 🟨🟨⬜⬜⬜
    OUTER 🟨⬜🟨🟨⬜
    EMOTE 🟩🟩🟩🟩🟩
    3/6
    EMOTE 🟨🟨⬜⬜⬜
    DAMES 🟨⬜🟨🟨⬜
    MEDIC 🟩🟩🟩🟩🟩
    6/6
    MEDIC ⬜🟨⬜⬜⬜
    URASE ⬜🟨🟨⬜🟨
    WATER ⬜🟩⬜🟩🟩
    LAVER ⬜🟩⬜🟩🟩
    PAGER ⬜🟩⬜🟩🟩
    BAKER 🟩🟩🟩🟩🟩
    4/6
    BAKER ⬜⬜⬜🟩🟨
    DORES ⬜⬜🟩🟩⬜
    CURET ⬜🟩🟩🟩⬜
    PUREE 🟩🟩🟩🟩🟩
    Final 2/2
    PITON 🟩🟩🟨🟩⬜
    PILOT 🟩🟩⬜🟩🟩
    FAIL: PIVOT

# dontwordle.com 🧩 #1310 🥳 6 ⏱️ 0:01:55.150697

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MANNA n n n n n remain:5040
    ⬜⬜⬜⬜⬜ tried:COHOG n n n n n remain:1898
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:959
    ⬜⬜🟨⬜⬜ tried:BRUSK n n m n n remain:24
    🟩🟩🟩⬜⬜ tried:QUIFF Y Y Y n n remain:3
    🟩🟩🟩⬜⬜ tried:QUIPU Y Y Y n n remain:2

    Undos used: 4

      2 words remaining
    x 7 unused letters
    = 14 total score

# [Quordle Classic](m-w.com/games/quordle) 🧩 #1430 🥳 score:20 ⏱️ 0:01:55.126245

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. FLOUR attempts:4 score:4
2. CHAIR attempts:3 score:3
3. OCTAL attempts:6 score:6
4. ADAPT attempts:7 score:7

# [Octordle Classic](https://www.britannica.com/games/octordle/daily) 🧩 #1430 🥳 score:58 ⏱️ 0:07:58.809067

📜 1 sessions

Octordle Classic

1. WROTE attempts:11 score:11
2. GOOFY attempts:9 score:9
3. LIGHT attempts:5 score:5
4. PSALM attempts:3 score:3
5. COAST attempts:4 score:4
6. LAUGH attempts:6 score:6
7. FIERY attempts:8 score:8
8. RATTY attempts:12 score:12


# cemantle.certitudes.org 🧩 #1360 🥳 113 ⏱️ 0:09:22.314930

🤔 114 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 35 chat prompts
🤖 35 falcon3:10b replies
🔥  3 🥵 12 😎 22 🥶 74 🧊  2

      $1 #114   ~1 grammar        100.00°C 🥳 1000‰
      $2  #88  ~17 phonetics       53.62°C 🔥  992‰
      $3 #113   ~2 syntax          52.65°C 🔥  991‰
      $4  #83  ~20 scansion        51.42°C 🔥  990‰
      $5 #111   ~3 language        51.13°C 🥵  987‰
      $6  #92  ~14 pronunciation   50.66°C 🥵  984‰
      $7  #94  ~12 phonological    48.17°C 🥵  979‰
      $8 #110   ~4 intonation      46.21°C 🥵  970‰
      $9  #91  ~15 phonology       45.76°C 🥵  967‰
     $10  #78  ~22 prosody         42.50°C 🥵  938‰
     $11 #107   ~7 alliteration    42.27°C 🥵  935‰
     $17  #33  ~37 text            39.17°C 😎  882‰
     $39  #76      cadence         27.91°C 🥶
    $113  #20      concert         -0.56°C 🧊

# cemantix.certitudes.org 🧩 #1393 🥳 118 ⏱️ 0:07:37.928284

🤔 119 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 35 chat prompts
🤖 35 falcon3:10b replies
🥵  2 😎 20 🥶 68 🧊 28

      $1 #119   ~1 hiérarchie      100.00°C 🥳 1000‰
      $2  #80  ~16 fonction         41.49°C 🥵  970‰
      $3 #108   ~3 niveau           38.50°C 🥵  929‰
      $4  #91   ~9 processus        36.79°C 😎  881‰
      $5  #35  ~23 devoir           36.49°C 😎  874‰
      $6  #87  ~12 rôle             35.62°C 😎  846‰
      $7 #103   ~4 exigence         35.52°C 😎  840‰
      $8  #86  ~13 responsabilité   35.41°C 😎  837‰
      $9  #88  ~11 définition       34.48°C 😎  796‰
     $10  #69  ~19 salariat         33.26°C 😎  734‰
     $11  #70  ~18 employé          31.25°C 😎  585‰
     $12  #46  ~22 travail          31.06°C 😎  570‰
     $24  #42      contenu          26.48°C 🥶
     $92  #15      éclair           -0.04°C 🧊
