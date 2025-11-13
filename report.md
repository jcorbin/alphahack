# 2025-11-14

- 🔗 spaceword.org 🧩 2025-11-13 🏁 score 2173 ranked 3.4% 13/388 ⏱️ 0:52:03.879630
- 🔗 alfagok.diginaut.net 🧩 #377 🥳 11 ⏱️ 0:01:00.329426
- 🔗 alphaguess.com 🧩 #843 🥳 14 ⏱️ 0:00:37.815288
- 🔗 squareword.org 🧩 #1383 🥳 7 ⏱️ 0:01:45.805114
- 🔗 dictionary.com hurdle 🧩 #1413 🥳 18 ⏱️ 0:04:06.944983
- 🔗 dontwordle.com 🧩 #1270 🥳 6 ⏱️ 0:01:24.155131
- 🔗 cemantle.certitudes.org 🧩 #1320 🥳 1602 ⏱️ 0:21:10.315515
- 🔗 cemantix.certitudes.org 🧩 #1353 🥳 167 ⏱️ 0:01:36.376410

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

# spaceword.org 🧩 2025-11-04 🏁 score 2173 ranked 6.5% 24/367 ⏱️ 0:20:32.980979

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 24/367

      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ H I P _ _ _
      _ _ _ _ _ _ O _ _ _
      _ _ _ _ S O D _ _ _
      _ _ _ _ E _ U _ _ _
      _ _ _ _ I _ N _ _ _
      _ _ _ _ Z E K _ _ _
      _ _ _ _ U M S _ _ _
      _ _ _ _ R _ _ _ _ _
      _ _ _ _ E V E _ _ _










# spaceword.org 🧩 2025-11-13 🏁 score 2173 ranked 3.4% 13/388 ⏱️ 0:52:03.879630

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 13/388

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ Z _ A U C T I O N   
      _ O _ R _ _ A _ Y E   
      _ O U T J I N X _ B   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #377 🥳 11 ⏱️ 0:01:00.329426

🤔 11 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+1      [     1] &-tekens    
    @+2      [     2] -cijferig   
    @+3      [     3] -e-mail     
    @+199766 [199766] lijn        q0  ? after
    @+299649 [299649] schudde     q1  ? after
    @+324180 [324180] sub         q3  ? after
    @+327171 [327171] tafel       q6  ? after
    @+328761 [328761] technologie q7  ? after
    @+328914 [328914] teen        q10 ? it
    @+328914 [328914] teen        done. it
    @+329087 [329087] tegen       q9  ? before
    @+329518 [329518] teken       q8  ? before
    @+330365 [330365] televisie   q5  ? before
    @+336774 [336774] toetsing    q4  ? before
    @+349380 [349380] vak         q2  ? before

# alphaguess.com 🧩 #843 🥳 14 ⏱️ 0:00:37.815288

🤔 14 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+47387 [47387] dis       q1  ? after
    @+72807 [72807] gremolata q2  ? after
    @+74368 [74368] had       q6  ? after
    @+74714 [74714] halachas  q8  ? after
    @+74757 [74757] hale      q11 ? after
    @+74757 [74757] hale      q12 ? after
    @+74766 [74766] half      q13 ? it
    @+74766 [74766] half      done. it
    @+74799 [74799] halid     q10 ? before
    @+74884 [74884] halo      q9  ? before
    @+75060 [75060] hand      q7  ? before
    @+75963 [75963] haw       q5  ? before
    @+79139 [79139] hood      q4  ? before
    @+85511 [85511] ins       q3  ? before
    @+98226 [98226] mach      q0  ? before

# squareword.org 🧩 #1383 🥳 7 ⏱️ 0:01:45.805114

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C A R S
    C A N O N
    A M I G O
    D E M U R
    S L E E T

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1413 🥳 18 ⏱️ 0:04:06.944983

📜 2 sessions
💰 score: 9800

    5/6
    LASER 🟨⬜⬜🟨⬜
    INKLE ⬜⬜⬜🟩🟩
    BUTLE ⬜🟩🟨🟩🟩
    TULLE 🟩🟩⬜🟩🟩
    TUPLE 🟩🟩🟩🟩🟩
    5/6
    TUPLE ⬜🟨⬜⬜🟩
    URSAE 🟨⬜⬜🟨🟩
    MAUVE ⬜🟩🟩⬜🟩
    DAUBE ⬜🟩🟩⬜🟩
    GAUGE 🟩🟩🟩🟩🟩
    3/6
    GAUGE 🟩🟨⬜⬜⬜
    GRADS 🟩🟩🟩⬜⬜
    GRANT 🟩🟩🟩🟩🟩
    3/6
    GRANT 🟨⬜⬜⬜🟨
    TOUGH 🟩⬜⬜🟩🟩
    THIGH 🟩🟩🟩🟩🟩
    Final 2/2
    BUDGE ⬜🟩🟩🟩🟩
    JUDGE 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1270 🥳 6 ⏱️ 0:01:24.155131

📜 1 sessions
💰 score: 18

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:JINNI n n n n n remain:7302
    ⬜⬜⬜⬜⬜ tried:AYAYA n n n n n remain:3074
    ⬜⬜⬜⬜⬜ tried:BUBUS n n n n n remain:725
    ⬜⬜⬜⬜⬜ tried:KEEVE n n n n n remain:116
    🟩⬜⬜⬜⬜ tried:PHPHT Y n n n n remain:4
    🟩🟩🟩⬜⬜ tried:PROMO Y Y Y n n remain:2

    Undos used: 3

      2 words remaining
    x 9 unused letters
    = 18 total score

# cemantle.certitudes.org 🧩 #1320 🥳 1602 ⏱️ 0:21:10.315515

🤔 1603 attempts
📜 1 sessions
🫧 98 chat sessions
⁉️ 664 chat prompts
🤖 638 llama3.2:latest replies
🤖 1 qwen3:8b replies
🤖 25 gemma3:latest replies
😱    1 🔥    1 🥵   25 😎  130 🥶 1358 🧊   87

       $1 #1603    ~1 afford             100.00°C 🥳 1000‰
       $2 #1318   ~33 subsidize           51.16°C 😱  999‰
       $3 #1061   ~81 want                45.53°C 🔥  993‰
       $4  #494  ~128 paying              42.67°C 🥵  989‰
       $5  #604  ~123 subsidized          42.28°C 🥵  988‰
       $6  #789  ~113 affordable          41.85°C 🥵  987‰
       $7  #300  ~143 cost                41.41°C 🥵  986‰
       $8 #1058   ~83 need                41.20°C 🥵  985‰
       $9  #785  ~114 rent                41.06°C 🥵  984‰
      $10 #1502    ~6 sustain             40.10°C 🥵  979‰
      $11  #984   ~91 exorbitant          38.72°C 🥵  969‰
      $29 #1018   ~85 even                33.91°C 😎  895‰
     $159  #120       detrimental         23.28°C 🥶
    $1517  #462       distribution        -0.01°C 🧊

# cemantix.certitudes.org 🧩 #1353 🥳 167 ⏱️ 0:01:36.376410

🤔 168 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 49 chat prompts
🤖 49 gemma3:latest replies
🔥  1 🥵 12 😎 49 🥶 97 🧊  8

      $1 #168   ~1 attentif        100.00°C 🥳 1000‰
      $2  #46  ~49 écoute           53.39°C 🔥  997‰
      $3  #31  ~56 respect          40.87°C 🥵  969‰
      $4  #72  ~37 confiance        39.44°C 🥵  959‰
      $5  #20  ~58 fidèle           38.45°C 🥵  950‰
      $6 #108  ~19 son              38.14°C 🥵  948‰
      $7 #103  ~23 bienveillance    38.07°C 🥵  947‰
      $8  #35  ~53 discernement     37.51°C 🥵  939‰
      $9 #122  ~15 attente          36.72°C 🥵  933‰
     $10  #60  ~43 respecter        36.16°C 🥵  925‰
     $11  #91  ~28 réceptivité      35.49°C 🥵  912‰
     $15 #149   ~9 sérénité         34.11°C 😎  881‰
     $64  #27      authenticité     22.51°C 🥶
    $161 #109      frisson          -0.07°C 🧊
