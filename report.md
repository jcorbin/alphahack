# 2025-11-22

- 🔗 spaceword.org 🧩 2025-11-21 🏁 score 2151 ranked 78.3% 263/336 ⏱️ 4:26:45.139738
- 🔗 alfagok.diginaut.net 🧩 #385 🥳 12 ⏱️ 0:00:36.658229
- 🔗 alphaguess.com 🧩 #851 🥳 18 ⏱️ 0:00:37.521123
- 🔗 squareword.org 🧩 #1391 🥳 8 ⏱️ 0:02:09.086410
- 🔗 dictionary.com hurdle 🧩 #1421 🥳 19 ⏱️ 0:04:28.506025
- 🔗 dontwordle.com 🧩 #1278 🤷 6 ⏱️ 0:01:46.234746
- 🔗 cemantle.certitudes.org 🧩 #1328 🥳 662 ⏱️ 0:32:11.572452
- 🔗 cemantix.certitudes.org 🧩 #1361 🥳 197 ⏱️ 0:01:48.340443

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


















# spaceword.org 🧩 2025-11-21 🏁 score 2151 ranked 78.3% 263/336 ⏱️ 4:26:45.139738

📜 2 sessions
- tiles: 21/21
- score: 2151 bonus: +51
- rank: 263/336

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ H _ _ _ _   
      _ _ _ _ _ A _ _ _ _   
      _ _ _ _ _ P _ _ A _   
      _ _ _ _ _ L _ _ I _   
      _ _ J I V I E S T _   
      _ _ _ _ _ T _ K _ _   
      _ _ O U R E B I _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #385 🥳 12 ⏱️ 0:00:36.658229

🤔 12 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199763 [199763] lijn      q0  ? after
    @+299646 [299646] schudde   q1  ? after
    @+311908 [311908] spies     q4  ? after
    @+313127 [313127] sport     q7  ? after
    @+313938 [313938] sprenkel  q8  ? after
    @+314107 [314107] sprint    q10 ? after
    @+314204 [314204] sprong    q11 ? it
    @+314204 [314204] sprong    done. it
    @+314308 [314308] spuit     q9  ? before
    @+314765 [314765] staats    q6  ? before
    @+317975 [317975] stem      q5  ? before
    @+324177 [324177] sub       q3  ? before
    @+349377 [349377] vak       q2  ? before

# alphaguess.com 🧩 #851 🥳 18 ⏱️ 0:00:37.521123

🤔 18 attempts
📜 1 sessions

    @        [     0] aa         
    @+1      [     1] aah        
    @+2      [     2] aahed      
    @+3      [     3] aahing     
    @+98226  [ 98226] mach       q0  ? after
    @+122111 [122111] par        q2  ? after
    @+134642 [134642] prog       q3  ? after
    @+140528 [140528] rec        q4  ? after
    @+141213 [141213] record     q7  ? after
    @+141364 [141364] recto      q9  ? after
    @+141435 [141435] recycle    q10 ? after
    @+141442 [141442] red        q11 ? after
    @+141443 [141443] redact     q17 ? it
    @+141443 [141443] redact     done. it
    @+141444 [141444] redacted   q16 ? before
    @+141446 [141446] redaction  q15 ? before
    @+141450 [141450] redactors  q14 ? before
    @+141458 [141458] redargue   q13 ? before
    @+141479 [141479] redbreasts q12 ? before
    @+141515 [141515] rede       q8  ? before
    @+141910 [141910] ree        q6  ? before
    @+143792 [143792] rem        q5  ? before
    @+147331 [147331] rho        q1  ? before

# squareword.org 🧩 #1391 🥳 8 ⏱️ 0:02:09.086410

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    F R O S T
    L E P E R
    A S I D E
    S I N G E
    K N E E S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1421 🥳 19 ⏱️ 0:04:28.506025

📜 1 sessions
💰 score: 9700

    5/6
    MARES ⬜🟨🟨🟨⬜
    TRACE 🟨🟨🟨⬜🟨
    EXTRA 🟨⬜🟨🟩🟨
    ALERT 🟩⬜🟩🟩🟩
    AVERT 🟩🟩🟩🟩🟩
    4/6
    AVERT ⬜⬜⬜⬜⬜
    LYSIN 🟨⬜⬜🟨⬜
    FLICK 🟨🟩🟩🟨⬜
    CLIFF 🟩🟩🟩🟩🟩
    6/6
    CLIFF ⬜⬜⬜⬜⬜
    SUTRA ⬜⬜⬜⬜🟨
    MONAD ⬜🟨⬜🟨⬜
    ABOVE 🟨⬜🟨⬜⬜
    YAPOK 🟩🟩⬜🟩⬜
    YAHOO 🟩🟩🟩🟩🟩
    2/6
    YAHOO ⬜🟩🟨🟩⬜
    HAVOC 🟩🟩🟩🟩🟩
    Final 2/2
    CREPT 🟩🟩🟩⬜🟩
    CREST 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1278 🤷 6 ⏱️ 0:01:46.234746

📜 1 sessions
💰 score: 0

ELIMINATED
> Well technically I didn't Wordle!

    ⬜⬜⬜⬜⬜ tried:YUKKY n n n n n remain:7806
    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:4289
    ⬜⬜⬜⬜⬜ tried:SALSA n n n n n remain:614
    🟨⬜⬜⬜⬜ tried:PHPHT m n n n n remain:7
    ⬜🟩⬜🟩🟩 tried:CREPE n Y n Y Y remain:1
    ⬛⬛⬛⬛⬛ tried:????? remain:0

    Undos used: 5

      0 words remaining
    x 0 unused letters
    = 0 total score

# cemantle.certitudes.org 🧩 #1328 🥳 662 ⏱️ 0:32:11.572452

🤔 663 attempts
📜 1 sessions
🫧 37 chat sessions
⁉️ 235 chat prompts
🤖 68 llama3.2:latest replies
🤖 5 qwen3:8b replies
🤖 162 gemma3:latest replies
🔥   2 🥵  29 😎  82 🥶 515 🧊  34

      $1 #663   ~1 fantastic         100.00°C 🥳 1000‰
      $2 #658   ~2 marvelous          76.88°C 🔥  995‰
      $3 #496  ~77 phenomenal         73.93°C 🔥  992‰
      $4 #546  ~58 superb             67.72°C 🥵  988‰
      $5 #550  ~54 magnificent        66.78°C 🥵  987‰
      $6 #517  ~65 brilliant          64.24°C 🥵  985‰
      $7 #514  ~68 splendid           57.32°C 🥵  979‰
      $8 #652   ~6 perfect            52.70°C 🥵  977‰
      $9 #498  ~75 exceptional        52.66°C 🥵  976‰
     $10 #549  ~55 impressive         51.19°C 🥵  968‰
     $11 #552  ~52 spectacular        51.00°C 🥵  967‰
     $33 #571  ~43 astonishing        41.07°C 😎  897‰
    $115 #311      disappointment     24.18°C 🥶
    $630 #344      reproachful        -0.17°C 🧊

# cemantix.certitudes.org 🧩 #1361 🥳 197 ⏱️ 0:01:48.340443

🤔 198 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 53 chat prompts
🤖 53 gemma3:latest replies
🥵   5 😎  33 🥶 124 🧊  35

      $1 #198   ~1 portrait        100.00°C 🥳 1000‰
      $2 #189   ~3 personnage       40.94°C 🥵  983‰
      $3  #24  ~34 récit            36.11°C 🥵  940‰
      $4  #99  ~21 iconographie     35.67°C 🥵  935‰
      $5  #15  ~36 histoire         35.41°C 🥵  928‰
      $6  #70  ~27 allégorie        33.92°C 🥵  904‰
      $7  #26  ~33 anecdote         33.66°C 😎  896‰
      $8 #106  ~20 illustration     33.15°C 😎  886‰
      $9  #38  ~31 héros            32.38°C 😎  872‰
     $10 #125  ~16 scène            31.59°C 😎  849‰
     $11  #13  ~38 roman            31.48°C 😎  844‰
     $12  #48  ~29 figure           30.78°C 😎  816‰
     $40 #180      conte            22.09°C 🥶
    $164 #188      enjeu            -0.11°C 🧊
