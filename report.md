# 2025-11-06

- 🔗 spaceword.org 🧩 2025-11-05 🏁 score 2173 ranked 6.4% 24/374 ⏱️ 0:18:37.880600
- 🔗 alfagok.diginaut.net 🧩 #369 🥳 10 ⏱️ 0:00:35.553707
- 🔗 alphaguess.com 🧩 #835 🥳 14 ⏱️ 0:00:36.530024
- 🔗 squareword.org 🧩 #1375 🥳 8 ⏱️ 0:03:52.927972
- 🔗 dictionary.com hurdle 🧩 #1405 🥳 21 ⏱️ 0:03:35.830431
- 🔗 dontwordle.com 🧩 #1262 🥳 6 ⏱️ 0:01:27.329154
- 🔗 cemantle.certitudes.org 🧩 #1312 🥳 740 ⏱️ 0:20:04.585691
- 🔗 cemantix.certitudes.org 🧩 #1345 🥳 618 ⏱️ 0:30:47.659182

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


# spaceword.org 🧩 2025-11-05 🏁 score 2173 ranked 6.4% 24/374 ⏱️ 0:18:37.880600

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 24/374

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ A _ V E T O I N G   
      _ G _ _ K I _ _ O I   
      _ S N E E Z E R _ F   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #369 🥳 10 ⏱️ 0:00:35.553707

🤔 10 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+99842  [ 99842] examen    q1  ? after
    @+112129 [112129] geboorte  q4  ? after
    @+115176 [115176] gehand    q6  ? after
    @+116697 [116697] gelaat    q7  ? after
    @+116819 [116819] geld      q9  ? it
    @+116819 [116819] geld      done. it
    @+117444 [117444] gelijk    q8  ? before
    @+118273 [118273] geluk     q5  ? before
    @+124522 [124522] gevoel    q3  ? before
    @+149326 [149326] huis      q2  ? before
    @+199766 [199766] lijn      q0  ? before

# alphaguess.com 🧩 #835 🥳 14 ⏱️ 0:00:36.530024

🤔 14 attempts
📜 1 sessions

    @       [    0] aa       
    @+1     [    1] aah      
    @+2     [    2] aahed    
    @+3     [    3] aahing   
    @+5877  [ 5877] angel    q4  ? after
    @+8324  [ 8324] ar       q5  ? after
    @+8499  [ 8499] arch     q8  ? after
    @+8662  [ 8662] arciform q9  ? after
    @+8743  [ 8743] argal    q10 ? after
    @+8783  [ 8783] argot    q11 ? after
    @+8788  [ 8788] argue    q13 ? it
    @+8788  [ 8788] argue    done. it
    @+8800  [ 8800] argument q12 ? before
    @+8825  [ 8825] arid     q7  ? before
    @+9342  [ 9342] as       q6  ? before
    @+11765 [11765] back     q3  ? before
    @+23688 [23688] camp     q2  ? before
    @+47387 [47387] dis      q1  ? before
    @+98226 [98226] mach     q0  ? before

# squareword.org 🧩 #1375 🥳 8 ⏱️ 0:03:52.927972

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟩
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    G R A M S
    R E F I T
    A S I D E
    D I R G E
    S N E E R

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1405 🥳 21 ⏱️ 0:03:35.830431

📜 1 sessions
💰 score: 9500

    3/6
    RALES 🟩⬜⬜🟩⬜
    ROVEN 🟩⬜🟩🟩⬜
    RIVET 🟩🟩🟩🟩🟩
    4/6
    RIVET ⬜⬜⬜🟨🟨
    HASTE 🟨⬜⬜🟨🟨
    LETCH ⬜🟩🟩🟩🟩
    FETCH 🟩🟩🟩🟩🟩
    6/6
    FETCH ⬜⬜🟨⬜🟨
    HOIST 🟨⬜🟨⬜🟩
    RIGHT ⬜🟩🟩🟩🟩
    NIGHT ⬜🟩🟩🟩🟩
    LIGHT ⬜🟩🟩🟩🟩
    MIGHT 🟩🟩🟩🟩🟩
    6/6
    MIGHT ⬜⬜⬜⬜⬜
    AROSE ⬜🟨🟨⬜🟨
    ROBED 🟨🟩⬜🟩⬜
    POWER ⬜🟩🟩🟩🟩
    COWER ⬜🟩🟩🟩🟩
    LOWER 🟩🟩🟩🟩🟩
    Final 2/2
    EMPTY 🟨🟨⬜🟨⬜
    STEMS 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1262 🥳 6 ⏱️ 0:01:27.329154

📜 1 sessions
💰 score: 16

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:NANNA n n n n n remain:5978
    ⬜⬜⬜⬜⬜ tried:BOOBY n n n n n remain:2514
    ⬜⬜⬜⬜⬜ tried:KIWIS n n n n n remain:386
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:85
    ⬜⬜⬜⬜🟩 tried:HUMPH n n n n Y remain:3
    🟨🟩⬜⬜🟩 tried:TEETH m Y n n Y remain:2

    Undos used: 3

      2 words remaining
    x 8 unused letters
    = 16 total score

# cemantle.certitudes.org 🧩 #1312 🥳 740 ⏱️ 0:20:04.585691

🤔 741 attempts
📜 1 sessions
🫧 27 chat sessions
⁉️ 176 chat prompts
🤖 103 llama3.2:latest replies
🤖 73 gemma3:latest replies
🔥   1 🥵  10 😎  88 🥶 631 🧊  10

      $1 #741   ~1 salt             100.00°C 🥳 1000‰
      $2 #210  ~62 sand              46.77°C 🔥  991‰
      $3 #125  ~80 grain             45.84°C 🔥  990‰
      $4 #524  ~13 water             39.86°C 🥵  957‰
      $5  #85  ~86 sediment          39.84°C 🥵  956‰
      $6  #86  ~85 slurry            39.68°C 🥵  953‰
      $7 #372  ~34 nutrient          39.57°C 🥵  949‰
      $8 #229  ~60 gravel            38.73°C 🥵  938‰
      $9 #383  ~31 topsoil           38.04°C 🥵  923‰
     $10 #200  ~65 caliche           37.71°C 🥵  916‰
     $11 #167  ~75 crust             37.46°C 🥵  907‰
     $13  #47  ~95 moisture          36.97°C 😎  898‰
    $101 #685      crusher           27.78°C 🥶
    $732 #303      launder           -0.09°C 🧊

# cemantix.certitudes.org 🧩 #1345 🥳 618 ⏱️ 0:30:47.659182

🤔 619 attempts
📜 1 sessions
🫧 33 chat sessions
⁉️ 199 chat prompts
🤖 89 llama3.2:latest replies
🤖 110 gemma3:latest replies
😱   1 🔥   3 🥵  14 😎  85 🥶 392 🧊 123

      $1 #619   ~1 multinational       100.00°C 🥳 1000‰
      $2 #582  ~13 multinationale       61.59°C 😱  999‰
      $3 #592  ~10 transnational        43.72°C 🔥  997‰
      $4 #381  ~34 international        39.46°C 🔥  992‰
      $5 #372  ~37 mondial              38.61°C 🔥  991‰
      $6 #390  ~33 globalisation        36.25°C 🥵  987‰
      $7 #338  ~46 industriel           35.53°C 🥵  983‰
      $8 #565  ~16 américain            34.77°C 🥵  979‰
      $9  #75  ~94 stratégique          34.67°C 🥵  978‰
     $10 #209  ~68 armement             34.64°C 🥵  976‰
     $11 #617   ~3 européen             33.81°C 🥵  973‰
     $20 #607   ~8 corporation          28.18°C 😎  896‰
    $105 #590      multidisciplinaire   17.51°C 🥶
    $497  #43      noblesse             -0.09°C 🧊
