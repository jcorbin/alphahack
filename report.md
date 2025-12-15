# 2025-12-16

- 🔗 spaceword.org 🧩 2025-12-15 🏁 score 2168 ranked 43.0% 144/335 ⏱️ 0:12:28.640530
- 🔗 alfagok.diginaut.net 🧩 #409 🥳 12 ⏱️ 0:01:02.504660
- 🔗 alphaguess.com 🧩 #875 🥳 18 ⏱️ 0:00:56.910967
- 🔗 squareword.org 🧩 #1415 🥳 7 ⏱️ 0:02:38.048863
- 🔗 dictionary.com hurdle 🧩 #1445 🥳 16 ⏱️ 0:03:49.631375
- 🔗 dontwordle.com 🧩 #1302 🥳 6 ⏱️ 0:01:18.215445
- 🔗 cemantle.certitudes.org 🧩 #1352 🥳 486 ⏱️ 0:18:38.152006
- 🔗 cemantix.certitudes.org 🧩 #1385 🥳 156 ⏱️ 0:12:00.661721

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




















# spaceword.org 🧩 2025-12-15 🏁 score 2168 ranked 43.0% 144/335 ⏱️ 0:12:28.640530

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 144/335

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ B _ _ _   
      _ _ _ _ _ L O _ _ _   
      _ _ _ J A I L _ _ _   
      _ _ _ _ _ Q I _ _ _   
      _ _ _ G A U D _ _ _   
      _ _ _ _ W A E _ _ _   
      _ _ _ _ A T _ _ _ _   
      _ _ _ R Y E _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #409 🥳 12 ⏱️ 0:01:02.504660

🤔 12 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199839 [199839] lijm      q0  ? after
    @+199839 [199839] lijm      q1  ? after
    @+247757 [247757] op        q3  ? after
    @+273563 [273563] proef     q4  ? after
    @+276825 [276825] quitte    q10 ? after
    @+278399 [278399] rand      q11 ? it
    @+278399 [278399] rand      done. it
    @+280084 [280084] rechtst   q6  ? before
    @+286631 [286631] rijs      q5  ? before
    @+299761 [299761] schub     q2  ? before

# alphaguess.com 🧩 #875 🥳 18 ⏱️ 0:00:56.910967

🤔 18 attempts
📜 1 sessions

    @       [    0] aa           
    @+1     [    1] aah          
    @+2     [    2] aahed        
    @+3     [    3] aahing       
    @+23688 [23688] camp         q2  ? after
    @+35531 [35531] convention   q3  ? after
    @+35543 [35543] conventual   q13 ? after
    @+35546 [35546] converge     q14 ? after
    @+35548 [35548] convergence  q17 ? it
    @+35548 [35548] convergence  done. it
    @+35549 [35549] convergences q16 ? before
    @+35552 [35552] convergent   q15 ? before
    @+35557 [35557] conversances q12 ? before
    @+35583 [35583] convert      q11 ? before
    @+35647 [35647] convo        q9  ? bn
    @+35647 [35647] convo        q10 ? before
    @+35785 [35785] coop         q8  ? before
    @+36097 [36097] cor          q7  ? before
    @+36732 [36732] cos          q6  ? before
    @+38190 [38190] crazy        q5  ? before
    @+40847 [40847] da           q4  ? before
    @+47387 [47387] dis          q1  ? before
    @+98225 [98225] mach         q0  ? before

# squareword.org 🧩 #1415 🥳 7 ⏱️ 0:02:38.048863

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T R A P
    P E E V E
    O R D E R
    U S U R P
    T E X T S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1445 🥳 16 ⏱️ 0:03:49.631375

📜 1 sessions
💰 score: 10000

    3/6
    PARSE 🟨⬜🟩🟨⬜
    STRIP 🟩⬜🟩⬜🟩
    SYRUP 🟩🟩🟩🟩🟩
    2/6
    SYRUP 🟩⬜⬜🟨🟩
    STUMP 🟩🟩🟩🟩🟩
    4/6
    STUMP ⬜⬜🟨⬜⬜
    QUERY ⬜🟨⬜⬜🟩
    UNLAY 🟩🟩⬜⬜🟩
    UNIFY 🟩🟩🟩🟩🟩
    5/6
    UNIFY ⬜⬜⬜⬜⬜
    ROADS ⬜⬜⬜⬜⬜
    LETCH 🟨🟩⬜⬜⬜
    JEBEL ⬜🟩🟨🟩🟩
    BEVEL 🟩🟩🟩🟩🟩
    Final 2/2
    DINER ⬜🟩🟨🟩🟩
    NICER 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1302 🥳 6 ⏱️ 0:01:18.215445

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:EBBET n n n n n remain:4685
    ⬜⬜⬜⬜⬜ tried:RAGGA n n n n n remain:1384
    ⬜⬜⬜⬜⬜ tried:VILLI n n n n n remain:535
    ⬜⬜⬜⬜⬜ tried:POPPY n n n n n remain:68
    🟨🟨⬜⬜⬜ tried:KUDZU m m n n n remain:5
    🟩⬜🟩⬜🟩 tried:SKUNK Y n Y n Y remain:1

    Undos used: 3

      1 words remaining
    x 8 unused letters
    = 8 total score

# cemantle.certitudes.org 🧩 #1352 🥳 486 ⏱️ 0:18:38.152006

🤔 487 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 104 chat prompts
🤖 104 dolphin3:latest replies
🔥   1 🥵  12 😎  68 🥶 376 🧊  29

      $1 #487   ~1 municipal        100.00°C 🥳 1000‰
      $2 #168  ~53 sewer             51.00°C 🔥  991‰
      $3 #485   ~2 district          47.08°C 🥵  986‰
      $4 #164  ~54 sewerage          44.89°C 🥵  981‰
      $5 #159  ~59 wastewater        44.70°C 🥵  980‰
      $6 #161  ~57 sewage            43.02°C 🥵  979‰
      $7 #220  ~37 public            42.66°C 🥵  977‰
      $8 #184  ~48 sanitation        36.72°C 🥵  957‰
      $9  #71  ~80 water             34.31°C 🥵  948‰
     $10 #477   ~4 transportation    33.33°C 🥵  934‰
     $11 #181  ~50 sanitary          33.09°C 🥵  931‰
     $15 #197  ~44 construction      30.31°C 😎  892‰
     $83 #266      waterway          18.59°C 🥶
    $459   #2      book              -0.14°C 🧊

# cemantix.certitudes.org 🧩 #1385 🥳 156 ⏱️ 0:12:00.661721

🤔 157 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 35 chat prompts
🤖 35 dolphin3:latest replies
🥵   3 😎  22 🥶 123 🧊   8

      $1 #157   ~1 glace          100.00°C 🥳 1000‰
      $2 #136   ~5 glacé           43.28°C 🥵  978‰
      $3 #116  ~15 profiterole     37.72°C 🥵  940‰
      $4  #45  ~23 croûte          34.50°C 🥵  909‰
      $5  #36  ~25 mousse          32.99°C 😎  892‰
      $6 #112  ~17 chocolat        32.28°C 😎  873‰
      $7 #125   ~9 caramel         32.12°C 😎  869‰
      $8 #143   ~3 meringue        31.49°C 😎  845‰
      $9  #59  ~21 paroi           30.25°C 😎  811‰
     $10  #93  ~18 manteau         29.46°C 😎  783‰
     $11 #117  ~14 dessert         28.96°C 😎  763‰
     $12 #123  ~11 tiramisu        28.12°C 😎  717‰
     $27 #106      beignet         22.79°C 🥶
    $150 #152      format          -0.04°C 🧊
