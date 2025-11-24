# 2025-11-25

- 🔗 spaceword.org 🧩 2025-11-24 🏁 score 2173 ranked 7.9% 28/353 ⏱️ 10:36:45.082917
- 🔗 alfagok.diginaut.net 🧩 #388 🥳 31 ⏱️ 0:01:28.946581
- 🔗 alphaguess.com 🧩 #854 🥳 13 ⏱️ 0:00:30.553131
- 🔗 squareword.org 🧩 #1394 🥳 7 ⏱️ 0:02:38.253127
- 🔗 dictionary.com hurdle 🧩 #1424 🥳 15 ⏱️ 0:02:49.906085
- 🔗 dontwordle.com 🧩 #1281 🥳 6 ⏱️ 0:02:09.087776
- 🔗 cemantle.certitudes.org 🧩 #1331 🥳 192 ⏱️ 0:11:53.966581
- 🔗 cemantix.certitudes.org 🧩 #1364 🥳 397 ⏱️ 0:36:15.092774

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





















# spaceword.org 🧩 2025-11-24 🏁 score 2173 ranked 7.9% 28/353 ⏱️ 10:36:45.082917

📜 6 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 28/353

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ S _ Y _ D A P _ J   
      _ E _ A G A T I Z E   
      _ V I R I L E _ _ E   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #388 🥳 31 ⏱️ 0:01:28.946581

🤔 31 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199762 [199762] lijn      q0  ? after
    @+199762 [199762] lijn      q1  ? after
    @+211608 [211608] me        q5  ? after
    @+214572 [214572] melodie   q7  ? after
    @+215905 [215905] met       q8  ? after
    @+216258 [216258] metro     q10 ? after
    @+216390 [216390] meubel    q11 ? after
    @+216513 [216513] meur      q12 ? after
    @+216526 [216526] meute     q25 ? after
    @+216537 [216537] mevrouw   q26 ? after
    @+216540 [216540] mevrouwt  q27 ? after
    @+216543 [216543] mezelf    q30 ? it
    @+216543 [216543] mezelf    done. it
    @+216544 [216544] mezen     q24 ? before
    @+216564 [216564] mi        q13 ? before
    @+216626 [216626] micro     q9  ? before
    @+217533 [217533] mijmer    q6  ? before
    @+223475 [223475] mol       q4  ? before
    @+247586 [247586] op        q3  ? before
    @+299633 [299633] schudde   q2  ? before

# alphaguess.com 🧩 #854 🥳 13 ⏱️ 0:00:30.553131

🤔 13 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+47387 [47387] dis        q1  ? after
    @+49434 [49434] do         q5  ? after
    @+49855 [49855] dom        q8  ? after
    @+49940 [49940] don        q10 ? after
    @+50037 [50037] doohickies q11 ? after
    @+50063 [50063] door       q12 ? it
    @+50063 [50063] door       done. it
    @+50133 [50133] dopiest    q9  ? before
    @+50411 [50411] dove       q7  ? before
    @+51408 [51408] drunk      q6  ? before
    @+53403 [53403] el         q4  ? before
    @+60090 [60090] face       q3  ? before
    @+72807 [72807] gremolata  q2  ? before
    @+98226 [98226] mach       q0  ? before

# squareword.org 🧩 #1394 🥳 7 ⏱️ 0:02:38.253127

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P S A L M
    A U D I O
    P E A K S
    E D G E S
    R E E D Y

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1424 🥳 15 ⏱️ 0:02:49.906085

📜 1 sessions
💰 score: 10100

    4/6
    AISLE ⬜🟨🟨⬜⬜
    SKIRT 🟩⬜🟨⬜⬜
    SONIC 🟩⬜⬜🟩⬜
    SQUID 🟩🟩🟩🟩🟩
    2/6
    SQUID ⬜⬜🟨🟨🟩
    BUILD 🟩🟩🟩🟩🟩
    5/6
    BUILD ⬜⬜🟩⬜⬜
    SHINE ⬜⬜🟩⬜🟩
    PRICE ⬜🟨🟩⬜🟩
    MOIRE ⬜⬜🟩🟩🟩
    AFIRE 🟩🟩🟩🟩🟩
    3/6
    AFIRE ⬜🟨⬜🟩🟨
    FERRY 🟨🟩🟨🟩🟩
    REFRY 🟩🟩🟩🟩🟩
    Final 1/2
    ROUND 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1281 🥳 6 ⏱️ 0:02:09.087776

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:COOCH n n n n n remain:6849
    ⬜⬜⬜⬜⬜ tried:DEKED n n n n n remain:2329
    ⬜⬜⬜⬜⬜ tried:MASAS n n n n n remain:269
    ⬜⬜⬜⬜⬜ tried:PIING n n n n n remain:39
    ⬜🟨🟨⬜⬜ tried:BUTUT n m m n n remain:3
    ⬜🟨🟩🟨🟩 tried:FLUTY n m Y m Y remain:1

    Undos used: 5

      1 words remaining
    x 7 unused letters
    = 7 total score

# cemantle.certitudes.org 🧩 #1331 🥳 192 ⏱️ 0:11:53.966581

🤔 193 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 25 chat prompts
🤖 25 gpt-oss:120b replies
🔥   1 🥵   4 😎  14 🥶 152 🧊  21

      $1 #193   ~1 restoration      100.00°C 🥳 1000‰
      $2 #184   ~6 preservation      58.39°C 🔥  998‰
      $3 #161  ~12 conservation      43.52°C 🥵  981‰
      $4 #186   ~5 reclamation       40.71°C 🥵  968‰
      $5 #188   ~3 reforestation     39.97°C 🥵  962‰
      $6 #187   ~4 recovery          36.18°C 🥵  939‰
      $7 #138  ~15 relocation        32.51°C 😎  888‰
      $8 #181   ~7 mitigation        31.04°C 😎  845‰
      $9  #61  ~19 reproduction      30.95°C 😎  842‰
     $10 #151  ~14 resettlement      30.06°C 😎  816‰
     $11  #84  ~18 translocation     27.26°C 😎  697‰
     $12 #157  ~13 habitat           27.04°C 😎  677‰
     $21  #21      fertilization     21.54°C 🥶
    $173  #19      boson             -0.14°C 🧊

# cemantix.certitudes.org 🧩 #1364 🥳 397 ⏱️ 0:36:15.092774

🤔 398 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 56 chat prompts
🤖 56 gpt-oss:120b replies
🔥   1 🥵   4 😎  72 🥶 207 🧊 113

      $1 #398   ~1 circonscription  100.00°C 🥳 1000‰
      $2 #394   ~3 député            45.03°C 🔥  994‰
      $3 #389   ~7 parlementaire     31.70°C 🥵  972‰
      $4 #317  ~32 mandat            29.27°C 🥵  955‰
      $5 #384   ~8 enseignant        26.55°C 🥵  929‰
      $6 #397   ~2 assemblée         26.31°C 🥵  926‰
      $7 #142  ~72 soutien           23.95°C 😎  882‰
      $8 #294  ~40 commission        23.52°C 😎  874‰
      $9 #286  ~43 administratif     22.81°C 😎  861‰
     $10 #300  ~36 inspection        22.76°C 😎  858‰
     $11 #221  ~55 adhérent          22.74°C 😎  857‰
     $12 #324  ~29 instance          22.37°C 😎  844‰
     $79  #18      ancrage           12.96°C 🥶
    $286 #386      mémoire           -0.01°C 🧊
