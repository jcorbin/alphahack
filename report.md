# 2025-12-03

- 🔗 spaceword.org 🧩 2025-12-02 🏁 score 2173 ranked 6.0% 20/334 ⏱️ 0:17:19.836116
- 🔗 alfagok.diginaut.net 🧩 #396 🥳 17 ⏱️ 0:01:04.200880
- 🔗 alphaguess.com 🧩 #862 🥳 15 ⏱️ 0:00:42.311210
- 🔗 squareword.org 🧩 #1402 🥳 7 ⏱️ 0:02:23.232375
- 🔗 dictionary.com hurdle 🧩 #1432 😦 17 ⏱️ 0:03:38.308786
- 🔗 dontwordle.com 🧩 #1289 🥳 6 ⏱️ 0:01:46.023067
- 🔗 cemantle.certitudes.org 🧩 #1339 🥳 221 ⏱️ 0:14:32.431403
- 🔗 cemantix.certitudes.org 🧩 #1372 🥳 113 ⏱️ 0:14:43.499391

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







# spaceword.org 🧩 2025-12-02 🏁 score 2173 ranked 6.0% 20/334 ⏱️ 0:17:19.836116

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 20/334

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ A X E _ G E L _ J   
      _ _ _ A M O R I N O   
      _ S Q U I R E _ _ G   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #396 🥳 17 ⏱️ 0:01:04.200880

🤔 17 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+49851  [ 49851] boks      q2  ? after
    @+49851  [ 49851] boks      q3  ? after
    @+74764  [ 74764] dc        q4  ? after
    @+80899  [ 80899] dijk      q6  ? after
    @+81250  [ 81250] ding      q11 ? after
    @+81371  [ 81371] dip       q12 ? after
    @+81431  [ 81431] diplomeer q14 ? after
    @+81461  [ 81461] direct    q15 ? after
    @+81467  [ 81467] directeur q16 ? it
    @+81467  [ 81467] directeur done. it
    @+81496  [ 81496] directie  q13 ? before
    @+81629  [ 81629] dis       q10 ? before
    @+82415  [ 82415] dj        q8  ? before
    @+84005  [ 84005] donor     q7  ? before
    @+87225  [ 87225] draag     q5  ? before
    @+99760  [ 99760] ex        q1  ? before
    @+199846 [199846] lijm      q0  ? before

# alphaguess.com 🧩 #862 🥳 15 ⏱️ 0:00:42.311210

🤔 15 attempts
📜 1 sessions

    @       [    0] aa       
    @+1     [    1] aah      
    @+2     [    2] aahed    
    @+3     [    3] aahing   
    @+47387 [47387] dis      q1  ? after
    @+72806 [72806] gremmy   q2  ? after
    @+85510 [85510] ins      q3  ? after
    @+91855 [91855] knot     q4  ? after
    @+93275 [93275] lar      q6  ? after
    @+93903 [93903] lea      q7  ? after
    @+94157 [94157] lecithin q9  ? after
    @+94245 [94245] leg      q10 ? after
    @+94286 [94286] legato   q12 ? after
    @+94290 [94290] legend   q14 ? it
    @+94290 [94290] legend   done. it
    @+94301 [94301] leger    q13 ? before
    @+94328 [94328] legion   q11 ? before
    @+94416 [94416] leis     q8  ? before
    @+94952 [94952] lib      q5  ? before
    @+98225 [98225] mach     q0  ? before

# squareword.org 🧩 #1402 🥳 7 ⏱️ 0:02:23.232375

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P I K E
    M A N N A
    A S T E R
    S T E A L
    H A R D Y

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1432 😦 17 ⏱️ 0:03:38.308786

📜 2 sessions
💰 score: 4960

    2/6
    ANTES ⬜🟩🟨🟩⬜
    INLET 🟩🟩🟩🟩🟩
    4/6
    INLET 🟨⬜🟨⬜🟩
    GUILT ⬜⬜🟩🟩🟩
    SPILT 🟩⬜🟩🟩🟩
    STILT 🟩🟩🟩🟩🟩
    5/6
    STILT ⬜⬜⬜⬜⬜
    DREAM ⬜⬜⬜🟨🟨
    MANGO 🟩🟩🟩🟩⬜
    MANGY 🟩🟩🟩🟩⬜
    MANGA 🟩🟩🟩🟩🟩
    4/6
    MANGA ⬜⬜⬜⬜⬜
    STOLE 🟨⬜🟨⬜⬜
    WORDS ⬜🟨🟨⬜🟨
    VISOR 🟩🟩🟩🟩🟩
    Final 2/2
    UPEND ⬜⬜🟨🟨⬜
    BENCH ⬜🟩🟩🟩⬜
    FAIL: FENCE

# dontwordle.com 🧩 #1289 🥳 6 ⏱️ 0:01:46.023067

📜 2 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:BOFFO n n n n n remain:7320
    ⬜⬜⬜⬜⬜ tried:DADAS n n n n n remain:1286
    ⬜⬜⬜⬜⬜ tried:PHIZZ n n n n n remain:366
    ⬜⬜🟨⬜⬜ tried:XYLYL n n m n n remain:44
    ⬜🟨🟨⬜⬜ tried:CLUCK n m m n n remain:9
    🟩🟨⬜⬜🟨 tried:LUNGE Y m n n m remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# cemantle.certitudes.org 🧩 #1339 🥳 221 ⏱️ 0:14:32.431403

🤔 222 attempts
📜 2 sessions
🫧 8 chat sessions
⁉️ 41 chat prompts
🤖 41 mixtral:8x22b replies
🔥   1 🥵   2 😎  22 🥶 186 🧊  10

      $1 #222   ~1 raw             100.00°C 🥳 1000‰
      $2 #216   ~2 visceral         39.94°C 🔥  990‰
      $3 #211   ~5 searing          38.58°C 🥵  984‰
      $4 #154  ~17 vivid            34.50°C 🥵  927‰
      $5 #213   ~4 fiery            33.07°C 😎  897‰
      $6 #186  ~10 emotionality     30.86°C 😎  795‰
      $7 #192   ~8 stirring         29.69°C 😎  708‰
      $8 #129  ~21 richness         29.62°C 😎  699‰
      $9 #187   ~9 emotive          29.34°C 😎  673‰
     $10  #90  ~24 emotion          28.82°C 😎  625‰
     $11 #125  ~22 insightfulness   28.74°C 😎  613‰
     $12 #131  ~20 soulful          28.59°C 😎  597‰
     $27 #145      sensitive        25.26°C 🥶
    $213  #53      optics           -0.21°C 🧊

# cemantix.certitudes.org 🧩 #1372 🥳 113 ⏱️ 0:14:43.499391

🤔 114 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 30 chat prompts
🤖 30 mixtral:8x22b replies
🔥  3 🥵  4 😎 21 🥶 55 🧊 30

      $1 #114   ~1 mérite           100.00°C 🥳 1000‰
      $2  #66  ~21 méritant          54.32°C 🔥  998‰
      $3 #112   ~2 méritocratique    45.11°C 🔥  993‰
      $4  #64  ~23 méritoire         42.39°C 🔥  991‰
      $5 #100   ~8 louable           39.68°C 🥵  985‰
      $6  #71  ~18 honorable         36.87°C 🥵  956‰
      $7 #103   ~5 flatteur          36.09°C 🥵  943‰
      $8  #85  ~14 honorifique       34.37°C 🥵  913‰
      $9 #101   ~7 élogieux          33.51°C 😎  893‰
     $10  #35  ~29 légitime          33.26°C 😎  886‰
     $11  #98  ~10 éminent           32.78°C 😎  870‰
     $12  #70  ~19 estimable         32.63°C 😎  865‰
     $30 #105      éclatant          22.56°C 🥶
     $85  #34      terre             -0.20°C 🧊
