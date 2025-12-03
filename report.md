# 2025-12-04

- 🔗 spaceword.org 🧩 2025-12-03 🏁 score 2170 ranked 25.2% 88/349 ⏱️ 0:06:16.608621
- 🔗 alfagok.diginaut.net 🧩 #397 🥳 16 ⏱️ 0:00:40.879484
- 🔗 alphaguess.com 🧩 #863 🥳 14 ⏱️ 0:00:29.606472
- 🔗 squareword.org 🧩 #1403 🥳 7 ⏱️ 0:02:23.615927
- 🔗 dictionary.com hurdle 🧩 #1433 🥳 17 ⏱️ 0:04:07.614914
- 🔗 dontwordle.com 🧩 #1290 😳 6 ⏱️ 0:01:50.360917
- 🔗 cemantle.certitudes.org 🧩 #1340 🥳 590 ⏱️ 0:47:35.663786
- 🔗 cemantix.certitudes.org 🧩 #1373 🥳 234 ⏱️ 0:32:52.900695

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








# spaceword.org 🧩 2025-12-03 🏁 score 2170 ranked 25.2% 88/349 ⏱️ 0:06:16.608621

📜 3 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 88/349

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ J _ O U T F A C E   
      _ E _ _ _ A _ G _ W   
      R E Q U I N T O S _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #397 🥳 16 ⏱️ 0:00:40.879484

🤔 16 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+1      [     1] &-tekens    
    @+2      [     2] -cijferig   
    @+3      [     3] -e-mail     
    @+199846 [199846] lijm        q0  ? after
    @+299783 [299783] schub       q1  ? after
    @+324360 [324360] sub         q3  ? after
    @+336962 [336962] toetsing    q4  ? after
    @+338452 [338452] topt        q7  ? after
    @+339183 [339183] trac        q8  ? after
    @+339250 [339250] trad        q11 ? after
    @+339252 [339252] traditie    q15 ? it
    @+339252 [339252] traditie    done. it
    @+339259 [339259] traditional q14 ? before
    @+339271 [339271] trafiek     q13 ? before
    @+339291 [339291] tragisch    q12 ? before
    @+339336 [339336] training    q10 ? before
    @+339522 [339522] tram        q9  ? before
    @+339953 [339953] transport   q6  ? before
    @+343152 [343152] tv          q5  ? before
    @+349569 [349569] vakantie    q2  ? before

# alphaguess.com 🧩 #863 🥳 14 ⏱️ 0:00:29.606472

🤔 14 attempts
📜 1 sessions

    @        [     0] aa         
    @+1      [     1] aah        
    @+2      [     2] aahed      
    @+3      [     3] aahing     
    @+98225  [ 98225] mach       q0  ? after
    @+147330 [147330] rho        q1  ? after
    @+171930 [171930] tag        q2  ? after
    @+176967 [176967] tom        q4  ? after
    @+176976 [176976] tomatillo  q12 ? after
    @+176979 [176979] tomato     q13 ? it
    @+176979 [176979] tomato     done. it
    @+176982 [176982] tomb       q11 ? before
    @+177007 [177007] tomcat     q10 ? before
    @+177049 [177049] ton        q9  ? before
    @+177234 [177234] top        q8  ? before
    @+177587 [177587] tot        q7  ? before
    @+178213 [178213] tram       q6  ? before
    @+179491 [179491] trifurcate q5  ? before
    @+182017 [182017] un         q3  ? before

# squareword.org 🧩 #1403 🥳 7 ⏱️ 0:02:23.615927

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P R A T S
    L A D E N
    A D O R E
    C O P S E
    E N T E R

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1433 🥳 17 ⏱️ 0:04:07.614914

📜 1 sessions
💰 score: 9900

    4/6
    ASIDE 🟨⬜⬜⬜⬜
    ROYAL ⬜🟩🟨🟨⬜
    GOATY ⬜🟩🟩⬜🟩
    FOAMY 🟩🟩🟩🟩🟩
    5/6
    FOAMY ⬜⬜🟩⬜⬜
    SCARE ⬜⬜🟩⬜⬜
    THANK 🟨⬜🟩⬜⬜
    ADAPT 🟩⬜🟩⬜🟩
    AWAIT 🟩🟩🟩🟩🟩
    4/6
    AWAIT 🟨⬜⬜🟨⬜
    VIRAL ⬜🟨⬜🟨⬜
    CHINA ⬜🟨🟩⬜🟨
    HAIKU 🟩🟩🟩🟩🟩
    3/6
    HAIKU ⬜⬜⬜🟩⬜
    NECKS ⬜🟩⬜🟩🟨
    PESKY 🟩🟩🟩🟩🟩
    Final 1/2
    CHORD 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1290 😳 6 ⏱️ 0:01:50.360917

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:MIMIC n n n n n remain:6772
    ⬜⬜⬜⬜⬜ tried:SEXES n n n n n remain:1480
    ⬜⬜⬜⬜⬜ tried:HOOKY n n n n n remain:303
    ⬜⬜⬜⬜🟩 tried:BUTUT n n n n Y remain:13
    ⬜🟨🟩⬜🟩 tried:ADAPT n m Y n Y remain:2
    🟩🟩🟩🟩🟩 tried:DRAFT Y Y Y Y Y remain:0

    Undos used: 3

      0 words remaining
    x 0 unused letters
    = 0 total score

# cemantle.certitudes.org 🧩 #1340 🥳 590 ⏱️ 0:47:35.663786

🤔 591 attempts
📜 1 sessions
🫧 35 chat sessions
⁉️ 213 chat prompts
🤖 118 falcon3:10b replies
🤖 4 wizardlm2:8x22b replies
🤖 90 mixtral:8x22b replies
😱   1 🔥   3 🥵  14 😎  74 🥶 463 🧊  35

      $1 #591   ~1 ounce           100.00°C 🥳 1000‰
      $2 #588   ~2 gram             55.43°C 😱  999‰
      $3 #177  ~49 barrel           52.78°C 🔥  998‰
      $4 #562   ~8 pennyweight      49.68°C 🔥  997‰
      $5 #586   ~3 pound            44.54°C 🔥  992‰
      $6 #316  ~30 copper           42.09°C 🥵  988‰
      $7 #448  ~23 bullion          41.92°C 🥵  987‰
      $8 #445  ~24 gold             41.67°C 🥵  986‰
      $9 #582   ~4 kilogram         39.62°C 🥵  981‰
     $10 #542  ~12 silver           38.03°C 🥵  975‰
     $11 #346  ~28 tin              35.87°C 🥵  966‰
     $20 #212  ~38 pail             29.63°C 😎  899‰
     $94 #455      indicator        21.47°C 🥶
    $557 #372      development      -0.02°C 🧊

# cemantix.certitudes.org 🧩 #1373 🥳 234 ⏱️ 0:32:52.900695

🤔 235 attempts
📜 1 sessions
🫧 15 chat sessions
⁉️ 67 chat prompts
🤖 67 mixtral:8x22b replies
🔥  4 🥵 34 😎 80 🥶 92 🧊 24

      $1 #235   ~1 intervenant        100.00°C 🥳 1000‰
      $2 #130  ~58 formateur           55.60°C 🔥  997‰
      $3 #120  ~64 animateur           52.65°C 🔥  995‰
      $4 #156  ~40 professionnel       48.27°C 🔥  992‰
      $5 #140  ~51 formation           47.63°C 🔥  991‰
      $6 #182  ~23 atelier             44.75°C 🥵  984‰
      $7 #116  ~68 coordinateur        44.72°C 🥵  983‰
      $8 #148  ~45 pédagogique         44.39°C 🥵  981‰
      $9 #134  ~56 enseignant          44.20°C 🥵  979‰
     $10  #86  ~86 organisation        44.15°C 🥵  978‰
     $11 #160  ~39 consultant          43.64°C 🥵  976‰
     $40  #99  ~78 programme           35.09°C 😎  899‰
    $120 #128      négociation         20.21°C 🥶
    $212  #31      introspection       -0.59°C 🧊
