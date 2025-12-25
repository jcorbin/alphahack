# 2025-12-26

- 🔗 spaceword.org 🧩 2025-12-25 🏁 score 2172 ranked 13.3% 37/278 ⏱️ 5:57:03.580245
- 🔗 alfagok.diginaut.net 🧩 #419 🥳 19 ⏱️ 0:00:46.832584
- 🔗 alphaguess.com 🧩 #885 🥳 14 ⏱️ 0:00:45.999144
- 🔗 dontwordle.com 🧩 #1312 😳 6 ⏱️ 0:03:33.617257
- 🔗 dictionary.com hurdle 🧩 #1455 🥳 19 ⏱️ 0:03:39.519920
- 🔗 Quordle Classic 🧩 #1432 🥳 score:23 ⏱️ 0:01:50.739289
- 🔗 Octordle Classic 🧩 #1432 🥳 score:58 ⏱️ 0:05:17.839049
- 🔗 squareword.org 🧩 #1425 🥳 7 ⏱️ 0:02:59.987976
- 🔗 cemantle.certitudes.org 🧩 #1362 🥳 46 ⏱️ 0:03:05.127472
- 🔗 cemantix.certitudes.org 🧩 #1395 🥳 786 ⏱️ 0:57:46.803601

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



# spaceword.org 🧩 2025-12-25 🏁 score 2172 ranked 13.3% 37/278 ⏱️ 5:57:03.580245

📜 7 sessions
- tiles: 21/21
- score: 2172 bonus: +72
- rank: 37/278

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ Q U I T T E R _   
      _ _ U N _ H I _ O _   
      _ _ I _ W E D _ O _   
      _ _ Z _ _ Y E _ F _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #419 🥳 19 ⏱️ 0:00:46.832584

🤔 19 attempts
📜 1 sessions

    @        [     0] &-teken       >>> SEARCH
    @+1      [     1] &-tekens      
    @+2      [     2] -cijferig     
    @+3      [     3] -e-mail       
    @+24910  [ 24910] bad           q3  ? after
    @+37364  [ 37364] bescherm      q4  ? after
    @+37752  [ 37752] beslissing    q8  ? after
    @+37977  [ 37977] bespaar       q9  ? after
    @+38090  [ 38090] bespot        q10 ? after
    @+38106  [ 38106] bespreek      q12 ? after
    @+38117  [ 38117] besprek       q13 ? after
    @+38118  [ 38118] bespreken     q18 ? it
    @+38119  [ 38119] besprekend    q17 ? before
    @+38120  [ 38120] besprekende   q16 ? before
    @+38123  [ 38123] bespreking    q15 ? before
    @+38127  [ 38127] besprenkel    q14 ? before
    @+38138  [ 38138] besproei      q11 ? before
    @+38202  [ 38202] best          q7  ? before
    @+39999  [ 39999] beurs         q6  ? before
    @+43070  [ 43070] bij           q5  ? before
    @+49849  [ 49849] boks          q2  ? before
    @+99758  [ 99758] ex            q1  ? before
    @+199835 [199835] lijm          q0  ? before
    @+399711 [399711] €50-biljetten <<< SEARCH

# alphaguess.com 🧩 #885 🥳 14 ⏱️ 0:00:45.999144

🤔 14 attempts
📜 1 sessions

    @        [     0] aa           >>> SEARCH
    @+1      [     1] aah          
    @+2      [     2] aahed        
    @+3      [     3] aahing       
    @+23688  [ 23688] camp         q2  ? after
    @+35531  [ 35531] convention   q3  ? after
    @+35785  [ 35785] coop         q8  ? after
    @+35787  [ 35787] cooper       q10 ? after
    @+35813  [ 35813] coopt        q11 ? after
    @+35819  [ 35819] coordinate   q13 ? it
    @+35825  [ 35825] coordination q12 ? before
    @+35837  [ 35837] cop          q9  ? before
    @+36097  [ 36097] cor          q7  ? before
    @+36732  [ 36732] cos          q6  ? before
    @+38190  [ 38190] crazy        q5  ? before
    @+40847  [ 40847] da           q4  ? before
    @+47387  [ 47387] dis          q1  ? before
    @+98225  [ 98225] mach         q0  ? before
    @+196537 [196537] zzz          <<< SEARCH

# dontwordle.com 🧩 #1312 😳 6 ⏱️ 0:03:33.617257

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:SULUS n n n n n remain:4173
    ⬜⬜⬜⬜⬜ tried:KOOKY n n n n n remain:1848
    ⬜⬜⬜⬜⬜ tried:BIFID n n n n n remain:579
    ⬜⬜⬜🟩⬜ tried:PHPHT n n n Y n remain:4
    🟩🟩🟩🟩🟩 tried:CACHE Y Y Y Y Y remain:0
    ⬛⬛⬛⬛⬛ tried:????? remain:0

    Undos used: 3

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1455 🥳 19 ⏱️ 0:03:39.519920

📜 1 sessions
💰 score: 9700

    4/6
    SAYER ⬜⬜⬜🟩🟩
    TILER ⬜🟨⬜🟩🟩
    INKER 🟩🟩⬜🟩🟩
    INFER 🟩🟩🟩🟩🟩
    5/6
    INFER ⬜⬜⬜🟨⬜
    SLAKE ⬜🟩⬜⬜🟩
    GLOBE ⬜🟩🟩⬜🟩
    CLOVE ⬜🟩🟩⬜🟩
    ELOPE 🟩🟩🟩🟩🟩
    4/6
    ELOPE ⬜⬜🟨🟩⬜
    CORPS ⬜🟨⬜🟩⬜
    HIPPO ⬜🟨⬜🟩🟨
    OKAPI 🟩🟩🟩🟩🟩
    5/6
    OKAPI 🟨⬜⬜⬜⬜
    DOTES ⬜🟨🟨⬜⬜
    THROB 🟨⬜⬜🟨⬜
    GLOUT ⬜🟩🟩🟩🟩
    FLOUT 🟩🟩🟩🟩🟩
    Final 1/2
    INTER 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle) 🧩 #1432 🥳 score:23 ⏱️ 0:01:50.739289

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. STRAP attempts:3 score:3
2. SQUIB attempts:7 score:7
3. FLUNK attempts:8 score:8
4. NOMAD attempts:5 score:5

# [Octordle Classic](https://www.britannica.com/games/octordle/daily) 🧩 #1432 🥳 score:58 ⏱️ 0:05:17.839049

📜 2 sessions

Octordle Classic

1. QUIRK attempts:10 score:10
2. APRON attempts:3 score:3
3. LEFTY attempts:9 score:9
4. VALOR attempts:4 score:4
5. STICK attempts:11 score:11
6. TREAD attempts:8 score:8
7. SASSY attempts:6 score:6
8. POESY attempts:7 score:7

# squareword.org 🧩 #1425 🥳 7 ⏱️ 0:02:59.987976

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟩
    🟩 🟨 🟩 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    T H E R E
    R U L E R
    A M O U R
    C O P S E
    T R E E D

# cemantle.certitudes.org 🧩 #1362 🥳 46 ⏱️ 0:03:05.127472

🤔 47 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 22 chat prompts
🤖 22 dolphin3:latest replies
🥵  2 😎 22 🥶 22

     $1 #47  ~1 milk         100.00°C 🥳 1000‰
     $2 #12 ~23 fruit         42.68°C 🥵  939‰
     $3 #21 ~15 strawberry    41.48°C 🥵  925‰
     $4 #13 ~22 grape         39.24°C 😎  865‰
     $5 #26 ~12 cantaloupe    37.99°C 😎  835‰
     $6 #17 ~19 mango         36.22°C 😎  765‰
     $7 #40  ~4 coconut       35.95°C 😎  755‰
     $8 #20 ~16 blueberry     35.68°C 😎  744‰
     $9 #11 ~24 apple         35.63°C 😎  741‰
    $10 #38  ~5 tomato        35.05°C 😎  717‰
    $11 #16 ~20 berry         34.93°C 😎  708‰
    $12  #1 ~25 banana        34.77°C 😎  697‰
    $13 #15 ~21 pineapple     33.29°C 😎  591‰
    $26 #37     pomegranate   27.47°C 🥶

# cemantix.certitudes.org 🧩 #1395 🥳 786 ⏱️ 0:57:46.803601

🤔 787 attempts
📜 2 sessions
🫧 103 chat sessions
⁉️ 416 chat prompts
🤖 416 dolphin3:latest replies
🔥   2 🥵  19 😎 116 🥶 472 🧊 177

      $1 #787   ~1 rétablissement        100.00°C 🥳 1000‰
      $2 #780   ~4 maintien               51.05°C 🔥  998‰
      $3 #216 ~117 gouvernement           39.70°C 🔥  993‰
      $4 #497  ~56 renforcement           35.81°C 🥵  982‰
      $5 #650  ~17 urgence                35.31°C 🥵  980‰
      $6 #320  ~87 état                   34.80°C 🥵  977‰
      $7 #557  ~40 redressement           34.29°C 🥵  976‰
      $8 #537  ~47 paix                   33.76°C 🥵  975‰
      $9 #605  ~26 abandon                33.75°C 🥵  974‰
     $10 #742   ~9 immédiat               33.24°C 🥵  971‰
     $11 #194 ~127 loi                    33.01°C 🥵  970‰
     $23 #539  ~46 réconciliation         28.28°C 😎  895‰
    $139 #254      recours                19.10°C 🥶
    $611  #83      abbaye                 -0.01°C 🧊
