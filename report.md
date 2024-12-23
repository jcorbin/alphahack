# 2025-11-13

- 🔗 spaceword.org 🧩 2025-11-12 🏁 score 2168 ranked 28.3% 108/382 ⏱️ 1:57:18.766913
- 🔗 alfagok.diginaut.net 🧩 #376 🥳 13 ⏱️ 0:00:32.914889
- 🔗 alphaguess.com 🧩 #842 🥳 8 ⏱️ 0:00:21.006243
- 🔗 squareword.org 🧩 #1382 🥳 6 ⏱️ 0:01:30.996505
- 🔗 dictionary.com hurdle 🧩 #1412 🥳 17 ⏱️ 0:03:13.434753
- 🔗 dontwordle.com 🧩 #1269 🥳 6 ⏱️ 0:01:23.936741
- 🔗 cemantle.certitudes.org 🧩 #1319 🥳 204 ⏱️ 0:01:00.092599
- 🔗 cemantix.certitudes.org 🧩 #1352 🥳 218 ⏱️ 0:06:22.441797

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









# spaceword.org 🧩 2025-11-12 🏁 score 2168 ranked 28.3% 108/382 ⏱️ 1:57:18.766913

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 108/382

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ F O U _ _ _   
      _ _ _ J E O N _ _ _   
      _ _ _ _ _ Z _ _ _ _   
      _ _ _ O Y E R _ _ _   
      _ _ _ _ _ _ U _ _ _   
      _ _ _ R A I N _ _ _   
      _ _ _ _ _ _ N _ _ _   
      _ _ _ _ I V Y _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #376 🥳 13 ⏱️ 0:00:32.914889

🤔 13 attempts
📜 1 sessions

    @        [     0] &-teken       
    @+1      [     1] &-tekens      
    @+2      [     2] -cijferig     
    @+3      [     3] -e-mail       
    @+199766 [199766] lijn          q0  ? after
    @+299649 [299649] schudde       q1  ? after
    @+349380 [349380] vak           q2  ? after
    @+361749 [361749] vervijfvoudig q4  ? after
    @+367901 [367901] vocht         q5  ? after
    @+369077 [369077] vogel         q7  ? after
    @+369302 [369302] voldoen       q9  ? after
    @+369333 [369333] volg          q10 ? after
    @+369433 [369433] volgroeide    q11 ? after
    @+369477 [369477] volk          q12 ? it
    @+369477 [369477] volk          done. it
    @+369532 [369532] volks         q8  ? before
    @+370394 [370394] voor          q6  ? before
    @+374123 [374123] vrij          q3  ? before

# alphaguess.com 🧩 #842 🥳 8 ⏱️ 0:00:21.006243

🤔 8 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+47387 [47387] dis       q1 ? after
    @+49434 [49434] do        q5 ? after
    @+51408 [51408] drunk     q6 ? after
    @+52401 [52401] earth     q7 ? it
    @+52401 [52401] earth     done. it
    @+53403 [53403] el        q4 ? before
    @+60090 [60090] face      q3 ? before
    @+72807 [72807] gremolata q2 ? before
    @+98226 [98226] mach      q0 ? before

# squareword.org 🧩 #1382 🥳 6 ⏱️ 0:01:30.996505

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P A S T E
    A S P E N
    S H E R D
    T E A S E
    A S K E D

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1412 🥳 17 ⏱️ 0:03:13.434753

📜 1 sessions
💰 score: 9900

    2/6
    NARES ⬜🟩⬜🟨🟨
    SAUTE 🟩🟩🟩🟩🟩
    3/6
    SAUTE ⬜🟨⬜⬜⬜
    LINAC 🟨⬜⬜🟨🟨
    CHALK 🟩🟩🟩🟩🟩
    5/6
    CHALK ⬜⬜⬜⬜⬜
    RIOTS 🟩⬜🟨⬜⬜
    RODEO 🟩🟩⬜🟩⬜
    ROVER 🟩🟩⬜🟩🟩
    ROGER 🟩🟩🟩🟩🟩
    5/6
    ROGER ⬜🟨⬜🟨⬜
    LEMON ⬜🟩⬜🟩⬜
    DECOY ⬜🟩⬜🟩⬜
    BESOT 🟩🟩⬜🟩⬜
    BEBOP 🟩🟩🟩🟩🟩
    Final 2/2
    WOMEN ⬜🟩⬜🟩🟩
    DOZEN 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1269 🥳 6 ⏱️ 0:01:23.936741

📜 1 sessions
💰 score: 189

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MOTTO n n n n n remain:5765
    ⬜⬜⬜⬜⬜ tried:SILLS n n n n n remain:1315
    ⬜⬜⬜⬜⬜ tried:BUBBY n n n n n remain:559
    🟨⬜⬜⬜⬜ tried:ADDAX m n n n n remain:169
    ⬜⬜🟨⬜⬜ tried:PZAZZ n n m n n remain:71
    ⬜🟩⬜⬜🟨 tried:GAFFE n Y n n m remain:21

    Undos used: 2

      21 words remaining
    x 9 unused letters
    = 189 total score

# cemantle.certitudes.org 🧩 #1319 🥳 204 ⏱️ 0:01:00.092599

🤔 205 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 37 chat prompts
🤖 37 gemma3:latest replies
🔥   1 🥵   9 😎  29 🥶 155 🧊  10

      $1 #205   ~1 retail           100.00°C 🥳 1000‰
      $2 #186  ~13 consumer          55.39°C 🔥  996‰
      $3 #160  ~25 market            41.58°C 🥵  982‰
      $4 #189  ~10 customer          38.37°C 🥵  965‰
      $5 #166  ~21 investment        36.15°C 🥵  954‰
      $6 #197   ~5 brand             34.46°C 🥵  946‰
      $7 #193   ~7 price             34.14°C 🥵  942‰
      $8 #159  ~26 commerce          33.46°C 🥵  936‰
      $9  #76  ~36 growth            33.29°C 🥵  930‰
     $10 #195   ~6 discount          33.09°C 🥵  926‰
     $11 #161  ~24 portfolio         31.29°C 🥵  905‰
     $12 #201   ~2 inventory         30.84°C 😎  899‰
     $41 #156      assets            18.48°C 🥶
    $196 #131      fertile           -0.21°C 🧊

# cemantix.certitudes.org 🧩 #1352 🥳 218 ⏱️ 0:06:22.441797

🤔 219 attempts
📜 1 sessions
🫧 13 chat sessions
⁉️ 77 chat prompts
🤖 2 llama3.2:latest replies
🤖 75 gemma3:latest replies
😱   1 🔥   1 🥵   8 😎  33 🥶 133 🧊  42

      $1 #219   ~1 mention           100.00°C 🥳 1000‰
      $2 #127  ~17 mentionner         53.69°C 😱  999‰
      $3 #103  ~24 indication         50.81°C 🔥  997‰
      $4  #71  ~36 indiquer           41.75°C 🥵  985‰
      $5 #175  ~11 document           39.84°C 🥵  979‰
      $6  #88  ~30 préciser           38.00°C 🥵  974‰
      $7 #117  ~20 attester           37.82°C 🥵  971‰
      $8 #181   ~8 référence          33.48°C 🥵  937‰
      $9 #179   ~9 notice             32.81°C 🥵  922‰
     $10  #93  ~28 attribuer          32.42°C 🥵  913‰
     $11 #112  ~22 spécifier          31.97°C 🥵  904‰
     $12 #201   ~4 énumérer           28.58°C 😎  812‰
     $45 #125      consulter          19.12°C 🥶
    $178  #34      réputation         -0.19°C 🧊
