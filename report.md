# 2025-12-21

- 🔗 spaceword.org 🧩 2025-12-20 🏁 score 2173 ranked 9.5% 22/231 ⏱️ 0:51:15.954018
- 🔗 alfagok.diginaut.net 🧩 #414 🥳 17 ⏱️ 0:00:52.823692
- 🔗 alphaguess.com 🧩 #880 🥳 17 ⏱️ 0:00:40.029643
- 🔗 squareword.org 🧩 #1420 🥳 8 ⏱️ 0:02:54.111997
- 🔗 dictionary.com hurdle 🧩 #1450 🥳 19 ⏱️ 0:03:56.031761
- 🔗 dontwordle.com 🧩 #1307 🥳 6 ⏱️ 0:01:47.799756
- 🔗 cemantle.certitudes.org 🧩 #1357 🥳 64 ⏱️ 0:00:56.333564
- 🔗 cemantix.certitudes.org 🧩 #1390 🥳 373 ⏱️ 0:06:47.481674

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

























# spaceword.org 🧩 2025-12-20 🏁 score 2173 ranked 9.5% 22/231 ⏱️ 0:51:15.954018

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 22/231

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ J _ V _ _ _ G I N   
      _ O _ O B E L I S E   
      _ T U X E D O _ M E   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #414 🥳 17 ⏱️ 0:00:52.823692

🤔 17 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+1      [     1] &-tekens    
    @+2      [     2] -cijferig   
    @+3      [     3] -e-mail     
    @+8648   [  8648] af          q4  ? after
    @+12394  [ 12394] afsplits    q6  ? after
    @+14275  [ 14275] agricultuur q8  ? after
    @+15201  [ 15201] alge        q9  ? after
    @+15209  [ 15209] algemeen    q16 ? it
    @+15209  [ 15209] algemeen    done. it
    @+15219  [ 15219] algen       q15 ? before
    @+15241  [ 15241] algoed      q14 ? before
    @+15282  [ 15282] alimentatie q12 ? before
    @+15382  [ 15382] alle        q11 ? before
    @+15676  [ 15676] allo        q10 ? before
    @+16154  [ 16154] am          q5  ? before
    @+24910  [ 24910] bad         q3  ? before
    @+49849  [ 49849] boks        q2  ? before
    @+99758  [ 99758] ex          q1  ? before
    @+199836 [199836] lijm        q0  ? before

# alphaguess.com 🧩 #880 🥳 17 ⏱️ 0:00:40.029643

🤔 17 attempts
📜 1 sessions

    @        [     0] aa          
    @+1      [     1] aah         
    @+2      [     2] aahed       
    @+3      [     3] aahing      
    @+98225  [ 98225] mach        q0  ? after
    @+122110 [122110] par         q2  ? after
    @+134641 [134641] prog        q3  ? after
    @+140527 [140527] rec         q4  ? after
    @+141212 [141212] record      q7  ? after
    @+141288 [141288] recrements  q11 ? after
    @+141319 [141319] recruit     q12 ? after
    @+141336 [141336] recta       q13 ? after
    @+141339 [141339] rectangle   q16 ? it
    @+141339 [141339] rectangle   done. it
    @+141341 [141341] rectangular q15 ? before
    @+141344 [141344] recti       q14 ? before
    @+141362 [141362] recto       q9  ? before
    @+141513 [141513] rede        q8  ? before
    @+141908 [141908] ree         q6  ? before
    @+143790 [143790] rem         q5  ? before
    @+147329 [147329] rho         q1  ? before

# squareword.org 🧩 #1420 🥳 8 ⏱️ 0:02:54.111997

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟨 🟨 🟨
    🟨 🟩 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P A M S
    T I D A L
    A L O N E
    G O R G E
    S T E A K

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1450 🥳 19 ⏱️ 0:03:56.031761

📜 1 sessions
💰 score: 9700

    4/6
    ACRES ⬜⬜⬜🟨⬜
    GLIDE ⬜⬜🟨🟨🟨
    IDENT 🟨🟨🟨⬜🟩
    DEBIT 🟩🟩🟩🟩🟩
    4/6
    DEBIT ⬜🟩⬜⬜🟨
    TESLA 🟩🟩⬜⬜⬜
    TENON 🟩🟩🟩🟩⬜
    TENOR 🟩🟩🟩🟩🟩
    4/6
    TENOR 🟨⬜🟨🟨⬜
    COUNT ⬜🟩⬜🟩🟩
    POINT ⬜🟩🟩🟩🟩
    JOINT 🟩🟩🟩🟩🟩
    6/6
    JOINT ⬜🟩⬜⬜⬜
    YORES 🟨🟩⬜⬜⬜
    COPAY ⬜🟩⬜⬜🟩
    MOLDY ⬜🟩⬜🟩🟩
    HOWDY ⬜🟩⬜🟩🟩
    GOODY 🟩🟩🟩🟩🟩
    Final 1/2
    DRYER 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1307 🥳 6 ⏱️ 0:01:47.799756

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:PIPIT n n n n n remain:6049
    ⬜⬜⬜⬜⬜ tried:FEMME n n n n n remain:2224
    ⬜⬜⬜⬜⬜ tried:GABBA n n n n n remain:595
    ⬜⬜⬜🟨⬜ tried:DRYLY n n n m n remain:50
    🟨🟨🟨⬜⬜ tried:CLUCK m m m n n remain:2
    🟨🟨⬜🟩🟨 tried:SCHUL m m n Y m remain:1

    Undos used: 4

      1 words remaining
    x 8 unused letters
    = 8 total score

# cemantle.certitudes.org 🧩 #1357 🥳 64 ⏱️ 0:00:56.333564

🤔 65 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 11 chat prompts
🤖 11 dolphin3:latest replies
😎  3 🥶 58 🧊  3

     $1 #65  ~1 biblical       100.00°C 🥳 1000‰
     $2 #30  ~4 apocalyptic     42.92°C 😎  869‰
     $3 #32  ~3 apocalypse      30.60°C 😎  121‰
     $4 #63  ~2 rapture         29.77°C 😎    6‰
     $5 #58     doomsday        27.49°C 🥶
     $6 #15     fiction         26.61°C 🥶
     $7 #37     cyberpunk       26.34°C 🥶
     $8 #38     desolation      26.18°C 🥶
     $9 #50     singularity     25.45°C 🥶
    $10 #12     literature      24.27°C 🥶
    $11 #31     alien           23.94°C 🥶
    $12  #2     book            22.94°C 🥶
    $13 #29     dystopian       22.90°C 🥶
    $63 #57     days            -0.52°C 🧊

# cemantix.certitudes.org 🧩 #1390 🥳 373 ⏱️ 0:06:47.481674

🤔 374 attempts
📜 1 sessions
🫧 19 chat sessions
⁉️ 89 chat prompts
🤖 89 dolphin3:latest replies
🔥   2 🥵  17 😎  79 🥶 190 🧊  85

      $1 #374   ~1 gratuit            100.00°C 🥳 1000‰
      $2 #367   ~5 abonnement          49.26°C 🔥  996‰
      $3 #260  ~32 accès               43.99°C 🔥  990‰
      $4 #295  ~19 inscription         42.91°C 🥵  988‰
      $5 #287  ~21 internet            41.47°C 🥵  983‰
      $6 #247  ~35 site                39.04°C 🥵  975‰
      $7 #330  ~15 ligne               36.32°C 🥵  965‰
      $8 #371   ~3 abonné              35.83°C 🥵  962‰
      $9 #222  ~49 service             35.37°C 🥵  958‰
     $10 #228  ~45 hébergement         35.02°C 🥵  956‰
     $11 #366   ~6 abonner             34.03°C 🥵  948‰
     $21 #261  ~31 adresse             30.63°C 😎  892‰
    $100 #144      accompagnateur      16.90°C 🥶
    $290 #317      accordéoniste       -0.01°C 🧊
