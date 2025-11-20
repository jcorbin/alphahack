# 2025-11-21

- 🔗 spaceword.org 🧩 2025-11-20 🏁 score 2172 ranked 22.1% 78/353 ⏱️ 1:37:32.838456
- 🔗 alfagok.diginaut.net 🧩 #384 🥳 14 ⏱️ 0:00:36.859104
- 🔗 alphaguess.com 🧩 #850 🥳 19 ⏱️ 0:00:46.396356
- 🔗 squareword.org 🧩 #1390 🥳 6 ⏱️ 0:01:46.418946
- 🔗 dictionary.com hurdle 🧩 #1420 🥳 19 ⏱️ 0:04:36.283352
- 🔗 dontwordle.com 🧩 #1277 🥳 6 ⏱️ 0:02:13.091078
- 🔗 cemantle.certitudes.org 🧩 #1327 🥳 135 ⏱️ 0:01:06.109893
- 🔗 cemantix.certitudes.org 🧩 #1360 😦 1838 ⏱️ 7:59:41.686626

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

















# spaceword.org 🧩 2025-11-20 🏁 score 2172 ranked 22.1% 78/353 ⏱️ 1:37:32.838456

📜 2 sessions
- tiles: 21/21
- score: 2172 bonus: +72
- rank: 78/353

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ A E _ _ _   
      _ _ _ J I N X _ _ _   
      _ _ _ _ N E E _ _ _   
      _ _ _ E C U S _ _ _   
      _ _ _ F A R _ _ _ _   
      _ _ _ _ G I _ _ _ _   
      _ _ _ K E N _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #384 🥳 14 ⏱️ 0:00:36.859104

🤔 14 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+49909  [ 49909] bol       q2  ? after
    @+74757  [ 74757] dc        q3  ? after
    @+80983  [ 80983] dijkt     q5  ? after
    @+81312  [ 81312] diode     q10 ? after
    @+81449  [ 81449] direct    q11 ? after
    @+81455  [ 81455] directeur q13 ? it
    @+81455  [ 81455] directeur done. it
    @+81484  [ 81484] directie  q12 ? before
    @+81647  [ 81647] disco     q8  ? before
    @+82364  [ 82364] divisie   q7  ? before
    @+83774  [ 83774] don       q6  ? before
    @+87214  [ 87214] draag     q4  ? before
    @+99838  [ 99838] examen    q1  ? before
    @+199762 [199762] lijn      q0  ? before

# alphaguess.com 🧩 #850 🥳 19 ⏱️ 0:00:46.396356

🤔 19 attempts
📜 1 sessions

    @        [     0] aa            
    @+1      [     1] aah           
    @+2      [     2] aahed         
    @+3      [     3] aahing        
    @+98226  [ 98226] mach          q0  ? after
    @+147331 [147331] rho           q1  ? after
    @+171931 [171931] tag           q2  ? after
    @+171931 [171931] tag           q3  ? after
    @+173171 [173171] technical     q7  ? after
    @+173395 [173395] tele          q9  ? after
    @+173591 [173591] teletype      q10 ? after
    @+173688 [173688] telome        q11 ? after
    @+173716 [173716] temp          q12 ? after
    @+173752 [173752] template      q13 ? after
    @+173759 [173759] tempo         q14 ? after
    @+173767 [173767] temporally    q16 ? after
    @+173771 [173771] temporariness q17 ? after
    @+173773 [173773] temporary     q18 ? it
    @+173773 [173773] temporary     done. it
    @+173774 [173774] temporise     q15 ? before
    @+173788 [173788] tempt         q8  ? before
    @+174417 [174417] test          q6  ? before
    @+176968 [176968] tom           q5  ? before
    @+182018 [182018] un            q4  ? before

# squareword.org 🧩 #1390 🥳 6 ⏱️ 0:01:46.418946

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P R A T
    A R O S E
    B E A T S
    R E S E T
    E N T R Y

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1420 🥳 19 ⏱️ 0:04:36.283352

📜 3 sessions
💰 score: 9700

    6/6
    TEARS ⬜🟨🟩⬜⬜
    WHALE ⬜⬜🟩🟨🟩
    GLADE ⬜🟩🟩⬜🟩
    PLANE ⬜🟩🟩⬜🟩
    BLAME ⬜🟩🟩⬜🟩
    FLAKE 🟩🟩🟩🟩🟩
    3/6
    FLAKE ⬜⬜🟨⬜⬜
    ASTIR 🟨🟨⬜⬜🟩
    SUGAR 🟩🟩🟩🟩🟩
    4/6
    SUGAR ⬜⬜⬜🟨⬜
    NAMED ⬜🟨⬜⬜🟨
    ACIDY 🟨⬜⬜🟨⬜
    VODKA 🟩🟩🟩🟩🟩
    4/6
    VODKA ⬜🟩⬜⬜⬜
    TORES 🟨🟩⬜🟩⬜
    MOTEL 🟨🟩🟨🟩⬜
    COMET 🟩🟩🟩🟩🟩
    Final 2/2
    DRAIN 🟩🟩🟩⬜🟩
    DRAWN 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1277 🥳 6 ⏱️ 0:02:13.091078

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:HALAL n n n n n remain:4961
    ⬜⬜⬜⬜⬜ tried:WOOZY n n n n n remain:2083
    ⬜⬜⬜⬜⬜ tried:UNCUT n n n n n remain:571
    ⬜🟨⬜⬜⬜ tried:VIVID n m n n n remain:65
    ⬜⬜🟩⬜🟩 tried:BEIGE n n Y n Y remain:5
    🟩🟩🟩⬜🟩 tried:SPIKE Y Y Y n Y remain:1

    Undos used: 3

      1 words remaining
    x 6 unused letters
    = 6 total score

# cemantle.certitudes.org 🧩 #1327 🥳 135 ⏱️ 0:01:06.109893

🤔 136 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 45 chat prompts
🤖 45 gemma3:latest replies
🔥   2 🥵   4 😎  20 🥶 107 🧊   2

      $1 #136   ~1 mild             100.00°C 🥳 1000‰
      $2  #37  ~18 slight            53.00°C 🔥  997‰
      $3  #67  ~12 minor             45.58°C 🔥  992‰
      $4  #15  ~25 muted             41.72°C 🥵  983‰
      $5  #17  ~24 gentle            38.40°C 🥵  933‰
      $6  #28  ~20 minimal           37.68°C 🥵  918‰
      $7  #13  ~26 quiet             37.57°C 🥵  914‰
      $8  #95   ~9 subdued           36.37°C 😎  887‰
      $9  #91  ~10 momentary         36.36°C 😎  886‰
     $10 #112   ~8 weak              34.10°C 😎  791‰
     $11  #24  ~21 subtle            33.82°C 😎  773‰
     $12  #29  ~19 faint             33.62°C 😎  756‰
     $28  #72      negligible        27.42°C 🥶
    $135  #41      shadowy           -5.93°C 🧊

# cemantix.certitudes.org 🧩 #1360 😦 1838 ⏱️ 7:59:41.686626

🤔 1837 attempts
📜 3 sessions
🫧 237 chat sessions
⁉️ 1501 chat prompts
🤖 921 llama3.2:latest replies
🤖 11 deepseek-r1:latest replies
🤖 568 gemma3:latest replies
😦 😱    1 🔥    6 🥵   40 😎  236 🥶 1262 🧊  292

       $1  #174  ~279 armée               64.88°C 😱  999‰
       $2  #224  ~255 commandant          59.98°C 🔥  998‰
       $3  #209  ~262 commandement        59.62°C 🔥  997‰
       $4  #803  ~130 interarmées         59.37°C 🔥  996‰
       $5  #193  ~268 militaire           58.22°C 🔥  995‰
       $6  #249  ~241 officier            53.43°C 🔥  993‰
       $7  #700  ~156 colonel             50.97°C 🔥  990‰
       $8  #815  ~127 généralissime       45.75°C 🥵  986‰
       $9  #190  ~269 escadron            45.06°C 🥵  983‰
      $10  #354  ~207 chef                43.65°C 🥵  982‰
      $11  #177  ~277 artillerie          43.44°C 🥵  981‰
      $48  #314  ~216 commando            34.03°C 😎  899‰
     $284 #1108       géopolitique        18.72°C 🥶
    $1546  #250       rifle               -0.01°C 🧊
