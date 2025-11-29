# 2025-11-30

- 🔗 spaceword.org 🧩 2025-11-29 🏁 score 2173 ranked 3.0% 10/329 ⏱️ 0:23:17.141775
- 🔗 alfagok.diginaut.net 🧩 #393 🥳 30 ⏱️ 0:01:36.546389
- 🔗 alphaguess.com 🧩 #859 🥳 15 ⏱️ 0:00:39.426762
- 🔗 squareword.org 🧩 #1399 🥳 9 ⏱️ 0:04:09.235746
- 🔗 dictionary.com hurdle 🧩 #1429 😦 10 ⏱️ 0:02:37.485822
- 🔗 dontwordle.com 🧩 #1286 🥳 6 ⏱️ 0:01:57.160086
- 🔗 cemantle.certitudes.org 🧩 #1336 🥳 280 ⏱️ 1:17:52.376188
- 🔗 cemantix.certitudes.org 🧩 #1369 🥳 510 ⏱️ 1:59:49.056478

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




# spaceword.org 🧩 2025-11-29 🏁 score 2173 ranked 3.0% 10/329 ⏱️ 0:23:17.141775

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 10/329

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ J _ Y E _ _ A _ H   
      _ I V O R I E D _ U   
      _ N _ U N F R O Z E   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #393 🥳 30 ⏱️ 0:01:36.546389

🤔 30 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+1      [     1] &-tekens     
    @+2      [     2] -cijferig    
    @+3      [     3] -e-mail      
    @+199762 [199762] lijn         q0  ? after
    @+223475 [223475] mol          q3  ? after
    @+235528 [235528] octrooi      q4  ? after
    @+238642 [238642] on           q5  ? after
    @+243112 [243112] onroerend    q6  ? after
    @+245329 [245329] ontwikkeling q7  ? after
    @+246457 [246457] onzichtbaar  q8  ? after
    @+246878 [246878] oorlog       q9  ? after
    @+247229 [247229] oorverdovend q10 ? after
    @+247259 [247259] oost         q11 ? after
    @+247341 [247341] oosteinde    q27 ? after
    @+247351 [247351] oosten       q29 ? it
    @+247351 [247351] oosten       done. it
    @+247377 [247377] oosterburen  q28 ? before
    @+247413 [247413] oosterlengte q17 ? before
    @+247570 [247570] op           q2  ? before
    @+299616 [299616] schud        q1  ? before

# alphaguess.com 🧩 #859 🥳 15 ⏱️ 0:00:39.426762

🤔 15 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+47387 [47387] dis       q1  ? after
    @+72807 [72807] gremolata q2  ? after
    @+73183 [73183] ground    q8  ? after
    @+73374 [73374] gruff     q9  ? after
    @+73413 [73413] grump     q11 ? after
    @+73438 [73438] grunt     q12 ? after
    @+73458 [73458] guacamole q14 ? it
    @+73458 [73458] guacamole done. it
    @+73476 [73476] guan      q10 ? before
    @+73578 [73578] guess     q7  ? before
    @+74367 [74367] had       q6  ? before
    @+75962 [75962] haw       q5  ? before
    @+79138 [79138] hood      q4  ? before
    @+85510 [85510] ins       q3  ? before
    @+98225 [98225] mach      q0  ? before

# squareword.org 🧩 #1399 🥳 9 ⏱️ 0:04:09.235746

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟨 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟩
    🟩 🟩 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S L A P S
    H U R R Y
    A N I O N
    L A S S O
    T R E E D

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1429 😦 10 ⏱️ 0:02:37.485822

📜 1 sessions
💰 score: 1260

    4/6
    ASTER ⬜⬜⬜⬜⬜
    CLUNG ⬜⬜⬜⬜⬜
    WIMPY 🟩🟨⬜⬜⬜
    WHIFF 🟩🟩🟩🟩🟩
    6/6
    WHIFF ⬜⬜⬜⬜⬜
    LASER ⬜⬜⬜🟩🟩
    OUTER 🟨⬜⬜🟩🟩
    MOVER ⬜🟩⬜🟩🟩
    DOPER ⬜🟩⬜🟩🟩
    GONER ⬜🟩⬜🟩🟩
    FAIL: BOXER

# dontwordle.com 🧩 #1286 🥳 6 ⏱️ 0:01:57.160086

📜 1 sessions
💰 score: 49

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:KAPPA n n n n n remain:5707
    ⬜⬜⬜⬜⬜ tried:COMMO n n n n n remain:2459
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:1363
    ⬜⬜⬜⬜⬜ tried:JUJUS n n n n n remain:384
    ⬜🟩⬜⬜⬜ tried:BIFID n Y n n n remain:43
    ⬜🟩⬜⬜⬜ tried:NINTH n Y n n n remain:7

    Undos used: 3

      7 words remaining
    x 7 unused letters
    = 49 total score

# cemantle.certitudes.org 🧩 #1336 🥳 280 ⏱️ 1:17:52.376188

🤔 281 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 55 chat prompts
🤖 47 gemma3:27b replies
🤖 8 qwen3:32b replies
🥵  13 😎  46 🥶 202 🧊  19

      $1 #281   ~1 blame           100.00°C 🥳 1000‰
      $2 #192  ~23 absolve          47.26°C 🥵  989‰
      $3 #272   ~2 accuse           46.55°C 🥵  988‰
      $4 #211  ~15 excuse           43.21°C 🥵  984‰
      $5 #249   ~8 compensate       40.88°C 🥵  970‰
      $6 #196  ~21 forgive          38.95°C 🥵  959‰
      $7  #55  ~60 acknowledge      38.20°C 🥵  955‰
      $8 #119  ~44 speculate        38.13°C 🥵  954‰
      $9  #62  ~57 admit            38.06°C 🥵  951‰
     $10 #124  ~41 argue            36.47°C 🥵  942‰
     $11 #271   ~3 exculpate        35.57°C 🥵  934‰
     $15 #216  ~13 tolerate         33.47°C 😎  899‰
     $61 #130      defend           23.35°C 🥶
    $263 #277      enclose          -0.14°C 🧊

# cemantix.certitudes.org 🧩 #1369 🥳 510 ⏱️ 1:59:49.056478

🤔 511 attempts
📜 1 sessions
🫧 33 chat sessions
⁉️ 117 chat prompts
🤖 70 gpt-oss:20b replies
🤖 46 qwen3:32b replies
🔥   2 🥵  16 😎  94 🥶 338 🧊  60

      $1 #511   ~1 islamiste          100.00°C 🥳 1000‰
      $2 #442  ~19 islamisme           64.63°C 🔥  998‰
      $3 #469  ~11 extrémiste          59.94°C 🔥  995‰
      $4 #503   ~4 jihad               54.80°C 🥵  988‰
      $5 #433  ~22 terrorisme          52.16°C 🥵  982‰
      $6 #394  ~35 nationaliste        48.47°C 🥵  971‰
      $7 #420  ~29 extrémisme          45.94°C 🥵  960‰
      $8  #98 ~109 opposant            45.05°C 🥵  957‰
      $9 #470  ~10 islamisation        44.41°C 🥵  954‰
     $10 #377  ~37 séparatiste         43.73°C 🥵  947‰
     $11 #471   ~9 islamophobie        43.50°C 🥵  944‰
     $20 #427  ~25 dictature           38.65°C 😎  885‰
    $114  #91      contester           25.05°C 🥶
    $452 #153      réseau              -0.05°C 🧊
