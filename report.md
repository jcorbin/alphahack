# 2025-12-11

- 🔗 spaceword.org 🧩 2025-12-10 🏁 score 2173 ranked 5.1% 18/352 ⏱️ 1:41:39.234567
- 🔗 alfagok.diginaut.net 🧩 #404 🥳 10 ⏱️ 0:00:28.431846
- 🔗 alphaguess.com 🧩 #870 🥳 13 ⏱️ 0:00:30.575002
- 🔗 squareword.org 🧩 #1410 🥳 7 ⏱️ 0:02:27.312636
- 🔗 dictionary.com hurdle 🧩 #1440 🥳 16 ⏱️ 0:02:49.303677
- 🔗 dontwordle.com 🧩 #1297 🥳 6 ⏱️ 0:01:39.848072
- 🔗 cemantle.certitudes.org 🧩 #1347 🥳 568 ⏱️ 1:20:01.659688
- 🔗 cemantix.certitudes.org 🧩 #1380 🥳 183 ⏱️ 0:05:14.497177

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















# spaceword.org 🧩 2025-12-10 🏁 score 2173 ranked 5.1% 18/352 ⏱️ 1:41:39.234567

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 18/352

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ J O E _ _ _   
      _ _ _ _ _ _ Q _ _ _   
      _ _ _ _ _ N U _ _ _   
      _ _ _ _ K O A _ _ _   
      _ _ _ _ _ U T _ _ _   
      _ _ _ _ E M E _ _ _   
      _ _ _ _ F E S _ _ _   
      _ _ _ _ _ N _ _ _ _   
      _ _ _ _ G A R _ _ _   


# alfagok.diginaut.net 🧩 #404 🥳 10 ⏱️ 0:00:28.431846

🤔 10 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199839 [199839] lijm      q0  ? after
    @+299764 [299764] schub     q1  ? after
    @+324341 [324341] sub       q3  ? after
    @+330526 [330526] televisie q5  ? after
    @+331213 [331213] tennist   q8  ? after
    @+331538 [331538] termijn   q9  ? it
    @+331538 [331538] termijn   done. it
    @+331921 [331921] terug     q7  ? before
    @+333731 [333731] these     q6  ? before
    @+336943 [336943] toetsing  q4  ? before
    @+349550 [349550] vakantie  q2  ? before

# alphaguess.com 🧩 #870 🥳 13 ⏱️ 0:00:30.575002

🤔 13 attempts
📜 1 sessions

    @        [     0] aa        
    @+1      [     1] aah       
    @+2      [     2] aahed     
    @+3      [     3] aahing    
    @+98225  [ 98225] mach      q0  ? after
    @+147330 [147330] rho       q1  ? after
    @+171930 [171930] tag       q2  ? after
    @+173170 [173170] technical q6  ? after
    @+173787 [173787] tempt     q7  ? after
    @+173801 [173801] ten       q9  ? after
    @+173948 [173948] tennis    q10 ? after
    @+173990 [173990] tens      q11 ? after
    @+174026 [174026] tent      q12 ? it
    @+174026 [174026] tent      done. it
    @+174102 [174102] tephrite  q8  ? before
    @+174416 [174416] test      q5  ? before
    @+176967 [176967] tom       q4  ? before
    @+182017 [182017] un        q3  ? before

# squareword.org 🧩 #1410 🥳 7 ⏱️ 0:02:27.312636

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S H O R T
    T A P I R
    A B I D E
    T I N G E
    S T E E D

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1440 🥳 16 ⏱️ 0:02:49.303677

📜 1 sessions
💰 score: 10000

    2/6
    SERAL 🟩🟨⬜⬜🟨
    SMILE 🟩🟩🟩🟩🟩
    4/6
    SMILE ⬜⬜⬜⬜🟨
    CARED ⬜⬜🟨🟨⬜
    TREYF 🟨🟩🟨⬜⬜
    ERUPT 🟩🟩🟩🟩🟩
    4/6
    ERUPT 🟨⬜⬜⬜🟩
    COSET ⬜⬜⬜🟨🟩
    DEALT ⬜🟨⬜🟩🟩
    KNELT 🟩🟩🟩🟩🟩
    5/6
    KNELT ⬜⬜🟨🟨⬜
    SEPAL ⬜🟨🟨🟨🟨
    PLACE 🟩🟨🟨⬜🟨
    PALED 🟩🟩🟩🟩⬜
    PALER 🟩🟩🟩🟩🟩
    Final 1/2
    AUDIT 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1297 🥳 6 ⏱️ 0:01:39.848072

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:YOBBY n n n n n remain:6682
    ⬜⬜⬜⬜⬜ tried:WIKIS n n n n n remain:1561
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:748
    ⬜⬜⬜⬜⬜ tried:JUGUM n n n n n remain:268
    ⬜⬜🟩🟩⬜ tried:ADDAX n n Y Y n remain:2
    🟨🟩🟩🟩⬜ tried:REDAN m Y Y Y n remain:1

    Undos used: 2

      1 words remaining
    x 6 unused letters
    = 6 total score

# cemantle.certitudes.org 🧩 #1347 🥳 568 ⏱️ 1:20:01.659688

🤔 569 attempts
📜 1 sessions
🫧 29 chat sessions
⁉️ 173 chat prompts
🤖 50 gemma3:27b replies
🤖 8 smallthinker:latest replies
🤖 114 falcon3:10b replies
🔥   3 🥵  14 😎  76 🥶 446 🧊  29

      $1 #569   ~1 interfere         100.00°C 🥳 1000‰
      $2 #565   ~3 impede             63.18°C 🔥  996‰
      $3 #566   ~2 obstruct           60.67°C 🔥  995‰
      $4 #561   ~7 hinder             59.12°C 🔥  993‰
      $5 #559   ~8 hamper             52.89°C 🥵  988‰
      $6 #548  ~15 inhibit            52.45°C 🥵  987‰
      $7 #525  ~23 alter              49.12°C 🥵  981‰
      $8 #529  ~22 restrict           46.60°C 🥵  974‰
      $9 #497  ~32 dictate            44.68°C 🥵  962‰
     $10 #535  ~20 constrain          44.59°C 🥵  960‰
     $11 #328  ~67 regulate           44.12°C 🥵  957‰
     $19 #326  ~68 synchronize        38.49°C 😎  888‰
     $95 #517      specify            25.41°C 🥶
    $541 #418      delivery           -0.03°C 🧊

# cemantix.certitudes.org 🧩 #1380 🥳 183 ⏱️ 0:05:14.497177

🤔 184 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 47 chat prompts
🤖 26 gemma3:27b replies
🤖 20 falcon3:10b replies
🔥   3 🥵  16 😎  42 🥶 115 🧊   7

      $1 #184   ~1 sagesse         100.00°C 🥳 1000‰
      $2 #136  ~26 bonté            58.21°C 😱  999‰
      $3 #176   ~4 humilité         56.43°C 🔥  998‰
      $4 #157  ~13 vertu            52.45°C 🔥  992‰
      $5 #159  ~11 droiture         50.32°C 🥵  987‰
      $6 #131  ~30 âme              49.90°C 🥵  986‰
      $7 #178   ~2 modestie         45.72°C 🥵  973‰
      $8 #135  ~27 compassion       45.36°C 🥵  969‰
      $9   #1  ~62 amour            45.09°C 🥵  967‰
     $10  #81  ~44 éternel          44.21°C 🥵  963‰
     $11 #132  ~29 bienveillance    43.25°C 🥵  956‰
     $21  #87  ~39 éternité         39.46°C 😎  896‰
     $63 #139      empathie         28.12°C 🥶
    $178  #49      passionné        -0.55°C 🧊
