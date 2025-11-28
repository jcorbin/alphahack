# 2025-11-29

- 🔗 spaceword.org 🧩 2025-11-28 🏁 score 2173 ranked 3.8% 12/317 ⏱️ 0:44:08.415841
- 🔗 alfagok.diginaut.net 🧩 #392 🥳 15 ⏱️ 0:00:55.754073
- 🔗 alphaguess.com 🧩 #858 🥳 14 ⏱️ 0:00:40.239234
- 🔗 squareword.org 🧩 #1398 🥳 11 ⏱️ 0:06:56.844844
- 🔗 dictionary.com hurdle 🧩 #1428 🥳 19 ⏱️ 0:04:44.605704
- 🔗 dontwordle.com 🧩 #1285 🥳 6 ⏱️ 0:02:03.713237
- 🔗 cemantle.certitudes.org 🧩 #1335 🥳 1410 ⏱️ 6:04:01.080889
- 🔗 cemantix.certitudes.org 🧩 #1368 🥳 45 ⏱️ 0:05:13.238303

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



# spaceword.org 🧩 2025-11-28 🏁 score 2173 ranked 3.8% 12/317 ⏱️ 0:44:08.415841

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 12/317

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ T O O _ V _ F O O   
      _ _ _ R H I Z O I D   
      _ K I T E D _ G _ A   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# alfagok.diginaut.net 🧩 #392 🥳 15 ⏱️ 0:00:55.754073

🤔 15 attempts
📜 2 sessions

    @        [     0] &-teken     
    @+1      [     1] &-tekens    
    @+2      [     2] -cijferig   
    @+3      [     3] -e-mail     
    @+199762 [199762] lijn        q0  ? after
    @+247584 [247584] op          q2  ? after
    @+273390 [273390] proef       q3  ? after
    @+276519 [276519] quarantaine q6  ? after
    @+278003 [278003] ram         q7  ? after
    @+278826 [278826] ratio       q8  ? after
    @+279124 [279124] rea         q9  ? after
    @+279190 [279190] reactor     q12 ? after
    @+279215 [279215] reageer     q13 ? after
    @+279232 [279232] reageren    q14 ? it
    @+279232 [279232] reageren    done. it
    @+279254 [279254] realiseren  q11 ? before
    @+279387 [279387] recept      q10 ? before
    @+279659 [279659] rechts      q5  ? before
    @+286502 [286502] rijst       q4  ? before
    @+299630 [299630] schud       q1  ? before

# alphaguess.com 🧩 #858 🥳 14 ⏱️ 0:00:40.239234

🤔 14 attempts
📜 1 sessions

    @        [     0] aa           
    @+1      [     1] aah          
    @+2      [     2] aahed        
    @+3      [     3] aahing       
    @+98226  [ 98226] mach         q0  ? after
    @+122111 [122111] par          q2  ? after
    @+128373 [128373] place        q4  ? after
    @+131497 [131497] pots         q5  ? after
    @+132283 [132283] preconise    q7  ? after
    @+132328 [132328] precursor    q11 ? after
    @+132347 [132347] predator     q12 ? after
    @+132362 [132362] predecessor  q13 ? it
    @+132362 [132362] predecessor  done. it
    @+132377 [132377] predesignate q10 ? before
    @+132469 [132469] predominate  q9  ? before
    @+132661 [132661] preform      q8  ? before
    @+133070 [133070] prep         q6  ? before
    @+134642 [134642] prog         q3  ? before
    @+147331 [147331] rho          q1  ? before

# squareword.org 🧩 #1398 🥳 11 ⏱️ 0:06:56.844844

📜 3 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟧 🟨 🟨 🟧 🟨
    🟩 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P O O N
    C R A V E
    R I S E R
    A M E N D
    M E S S Y

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1428 🥳 19 ⏱️ 0:04:44.605704

📜 1 sessions
💰 score: 9700

    4/6
    SOLAR ⬜⬜⬜⬜🟨
    QUIRT ⬜⬜⬜🟩⬜
    DECRY ⬜🟩⬜🟩⬜
    GENRE 🟩🟩🟩🟩🟩
    5/6
    GENRE ⬜⬜🟨⬜⬜
    NAILS 🟨⬜⬜🟨⬜
    CLUNK ⬜🟩⬜🟨⬜
    BLOWN ⬜🟩🟩🟩🟩
    FLOWN 🟩🟩🟩🟩🟩
    5/6
    FLOWN ⬜⬜⬜⬜⬜
    RAGES ⬜🟩⬜⬜⬜
    YACHT ⬜🟩⬜⬜⬜
    VAPID ⬜🟩⬜⬜🟨
    MADAM 🟩🟩🟩🟩🟩
    4/6
    MADAM ⬜⬜🟨⬜⬜
    SOLDI ⬜⬜⬜🟨🟨
    RICED 🟨🟨🟨🟩🟩
    CRIED 🟩🟩🟩🟩🟩
    Final 1/2
    SWARM 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1285 🥳 6 ⏱️ 0:02:03.713237

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:7042
    ⬜⬜⬜⬜⬜ tried:KOOKY n n n n n remain:3278
    ⬜⬜⬜⬜⬜ tried:JNANA n n n n n remain:1000
    ⬜⬜⬜⬜⬜ tried:EMMER n n n n n remain:86
    ⬜⬜🟩⬜⬜ tried:CLIFF n n Y n n remain:16
    ⬜🟨🟩⬜⬜ tried:PHIZZ n m Y n n remain:1

    Undos used: 4

      1 words remaining
    x 7 unused letters
    = 7 total score

# cemantle.certitudes.org 🧩 #1335 🥳 1410 ⏱️ 6:04:01.080889

🤔 1411 attempts
📜 4 sessions
🫧 74 chat sessions
⁉️ 473 chat prompts
🤖 31 llama4:latest replies
🤖 14 llama3.3:latest replies
🤖 258 gemma3:27b replies
🤖 24 gpt-oss:20b replies
🤖 2 deepseek-r1:70b replies
🤖 33 dolphin3:latest replies
🤖 7 qwen3:32b replies
🤖 103 gpt-oss:120b replies
😱    1 🔥    7 🥵   51 😎  232 🥶 1069 🧊   50

       $1 #1411    ~1 disappoint        100.00°C 🥳 1000‰
       $2  #206  ~253 dazzle             58.78°C 😱  999‰
       $3  #165  ~274 excite             57.89°C 🔥  998‰
       $4  #586  ~168 impress            57.14°C 🔥  997‰
       $5  #195  ~258 enthrall           51.40°C 🔥  994‰
       $6  #589  ~167 enthral            51.40°C 🔥  994‰
       $7  #955   ~71 daunt              50.44°C 🔥  993‰
       $8  #914   ~80 dishearten         48.89°C 🔥  992‰
       $9  #225  ~247 astonish           48.82°C 🔥  991‰
      $10  #318  ~223 mesmerize          47.51°C 🥵  988‰
      $11  #610  ~160 enamour            47.46°C 🥵  987‰
      $61  #596  ~164 resonate           36.19°C 😎  898‰
     $293  #944       impede             23.74°C 🥶
    $1362  #436       phosphorescence    -0.04°C 🧊

# cemantix.certitudes.org 🧩 #1368 🥳 45 ⏱️ 0:05:13.238303

🤔 46 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 13 chat prompts
🤖 13 gpt-oss:120b replies
😱  1 🔥  1 🥵  4 😎 14 🥶 20 🧊  5

     $1 #46  ~1 amical         100.00°C 🥳 1000‰
     $2 #37  ~7 amitié          58.37°C 😱  999‰
     $3 #39  ~6 camaraderie     45.79°C 🔥  993‰
     $4 #45  ~2 ami             43.59°C 🥵  989‰
     $5 #33  ~9 entente         34.79°C 🥵  968‰
     $6 #25 ~15 complicité      31.64°C 🥵  937‰
     $7 #43  ~4 affinité        28.53°C 🥵  903‰
     $8 #23 ~16 bienveillance   27.33°C 😎  884‰
     $9 #42  ~5 confraternité   26.60°C 😎  866‰
    $10 #44  ~3 altruiste       24.63°C 😎  820‰
    $11 #34  ~8 générosité      23.32°C 😎  771‰
    $12 #20 ~18 tendresse       22.97°C 😎  762‰
    $22 #41     compassion      15.14°C 🥶
    $42  #8     pomme           -1.88°C 🧊


