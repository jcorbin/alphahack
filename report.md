# 2025-12-02

- 🔗 spaceword.org 🧩 2025-12-01 🏁 score 2173 ranked 8.0% 29/362 ⏱️ 3:31:18.828366
- 🔗 alfagok.diginaut.net 🧩 #395 🥳 24 ⏱️ 0:06:44.290969
- 🔗 alphaguess.com 🧩 #861 🥳 14 ⏱️ 0:00:29.253544
- 🔗 squareword.org 🧩 #1401 🥳 9 ⏱️ 0:03:36.336012
- 🔗 dictionary.com hurdle 🧩 #1431 🥳 17 ⏱️ 0:03:54.733480
- 🔗 dontwordle.com 🧩 #1288 🥳 6 ⏱️ 0:01:50.343540
- 🔗 cemantle.certitudes.org 🧩 #1338 🥳 48 ⏱️ 0:00:51.104236
- 🔗 cemantix.certitudes.org 🧩 #1371 🥳 125 ⏱️ 0:02:14.324460

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






# spaceword.org 🧩 2025-12-01 🏁 score 2173 ranked 8.0% 29/362 ⏱️ 3:31:18.828366

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 29/362

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ C _ _ _ _   
      _ _ _ _ U H _ _ _ _   
      _ _ _ _ _ O D _ _ _   
      _ _ _ _ A R E _ _ _   
      _ _ _ _ J A G _ _ _   
      _ _ _ _ I L L _ _ _   
      _ _ _ _ S E A _ _ _   
      _ _ _ _ _ _ Z _ _ _   
      _ _ _ _ E V E _ _ _   


# alfagok.diginaut.net 🧩 #395 🥳 24 ⏱️ 0:06:44.290969

🤔 24 attempts
📜 7 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+99761  [ 99761] ex        q2  ? after
    @+149465 [149465] huis      q3  ? after
    @+174575 [174575] kind      q4  ? after
    @+187214 [187214] kroon     q6  ? after
    @+193512 [193512] lavendel  q7  ? after
    @+194937 [194937] lees      q9  ? after
    @+195654 [195654] leid      q10 ? after
    @+195663 [195663] leiden    q22 ? after
    @+195667 [195667] leider    q23 ? it
    @+195667 [195667] leider    done. it
    @+195672 [195672] leiders   q21 ? before
    @+195739 [195739] leidsel   q20 ? before
    @+195817 [195817] lek       q12 ? before
    @+196082 [196082] lengte    q11 ? before
    @+196528 [196528] les       q8  ? before
    @+199847 [199847] lijm      q0  ? after
    @+199847 [199847] lijm      q1  ? before

# alphaguess.com 🧩 #861 🥳 14 ⏱️ 0:00:29.253544

🤔 14 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+23688 [23688] camp       q2  ? after
    @+29609 [29609] circuit    q4  ? after
    @+31084 [31084] coagencies q6  ? after
    @+31107 [31107] coal       q10 ? after
    @+31162 [31162] coannex    q11 ? after
    @+31190 [31190] coassist   q12 ? after
    @+31198 [31198] coast      q13 ? it
    @+31198 [31198] coast      done. it
    @+31220 [31220] coat       q9  ? before
    @+31382 [31382] cock       q8  ? before
    @+31817 [31817] coexist    q7  ? before
    @+32558 [32558] color      q5  ? before
    @+35531 [35531] convention q3  ? before
    @+47387 [47387] dis        q1  ? before
    @+98225 [98225] mach       q0  ? before

# squareword.org 🧩 #1401 🥳 9 ⏱️ 0:03:36.336012

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    O F T E N
    G R O V E
    T A K E R
    E M E N D
    D E N T S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1431 🥳 17 ⏱️ 0:03:54.733480

📜 1 sessions
💰 score: 9900

    3/6
    NEARS ⬜🟨⬜⬜🟨
    STOLE 🟩🟩⬜🟨🟨
    STEEL 🟩🟩🟩🟩🟩
    4/6
    STEEL ⬜⬜🟩🟨🟨
    BLEAK ⬜🟨🟩⬜⬜
    FIELD ⬜🟩🟩🟨⬜
    LIEGE 🟩🟩🟩🟩🟩
    4/6
    LIEGE 🟨⬜⬜⬜⬜
    SALON ⬜⬜🟨⬜⬜
    CURLY 🟨🟨⬜🟨⬜
    PLUCK 🟩🟩🟩🟩🟩
    4/6
    PLUCK ⬜⬜⬜⬜🟨
    RAKES ⬜⬜🟨🟨⬜
    KNIFE 🟨⬜⬜⬜🟩
    EVOKE 🟩🟩🟩🟩🟩
    Final 2/2
    ALONG ⬜🟩🟩⬜🟨
    GLORY 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1288 🥳 6 ⏱️ 0:01:50.343540

📜 1 sessions
💰 score: 49

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:JINNI n n n n n remain:7302
    ⬜⬜⬜⬜⬜ tried:MASSA n n n n n remain:1549
    ⬜⬜⬜⬜⬜ tried:WHOOF n n n n n remain:478
    ⬜⬜⬜⬜⬜ tried:YUKKY n n n n n remain:118
    ⬜⬜⬜⬜🟩 tried:GRRRL n n n n Y remain:9
    🟨⬜⬜🟩🟩 tried:EXPEL m n n Y Y remain:7

    Undos used: 4

      7 words remaining
    x 7 unused letters
    = 49 total score

# cemantle.certitudes.org 🧩 #1338 🥳 48 ⏱️ 0:00:51.104236

🤔 49 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 9 chat prompts
🤖 9 mixtral:8x7b replies
🥵  1 😎  7 🥶 34 🧊  6

     $1 #49  ~1 transition     100.00°C 🥳 1000‰
     $2 #44  ~5 switching       33.55°C 🥵  952‰
     $3 #46  ~3 conversion      28.70°C 😎  885‰
     $4 #30  ~8 interaction     23.59°C 😎  652‰
     $5 #45  ~4 alternation     22.69°C 😎  565‰
     $6 #35  ~7 oriented        21.82°C 😎  457‰
     $7 #22  ~9 communication   21.29°C 😎  397‰
     $8 #47  ~2 movement        20.49°C 😎  280‰
     $9 #39  ~6 collaboration   19.88°C 😎  168‰
    $10 #23     balancing       18.64°C 🥶
    $11 #18     interface       18.53°C 🥶
    $12 #41     engagement      18.47°C 🥶
    $13 #28     encoding        16.99°C 🥶
    $44 #48     tolerance       -0.51°C 🧊

# cemantix.certitudes.org 🧩 #1371 🥳 125 ⏱️ 0:02:14.324460

🤔 126 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 23 chat prompts
🤖 23 mixtral:8x7b replies
🥵  2 😎  8 🥶 97 🧊 18

      $1 #126   ~1 matériau         100.00°C 🥳 1000‰
      $2 #116   ~5 isolant           47.15°C 🥵  965‰
      $3  #94   ~9 recyclabilité     45.40°C 🥵  950‰
      $4  #99   ~7 durabilité        41.24°C 😎  863‰
      $5  #95   ~8 thermique         37.11°C 😎  660‰
      $6 #122   ~2 phonique          36.29°C 😎  611‰
      $7  #27  ~11 densité           35.99°C 😎  588‰
      $8  #86  ~10 isolation         34.31°C 😎  445‰
      $9 #112   ~6 construction      34.01°C 😎  419‰
     $10 #121   ~3 étanchéité        33.06°C 😎  331‰
     $11 #117   ~4 acoustique        31.49°C 😎  143‰
     $12  #39      absorption        30.18°C 🥶
     $13  #48      nature            29.82°C 🥶
    $109  #33      ichtyologie       -0.05°C 🧊
