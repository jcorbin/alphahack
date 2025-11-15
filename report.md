# 2025-11-16

- 🔗 spaceword.org 🧩 2025-11-15 🏁 score 2168 ranked 41.0% 136/332 ⏱️ 0:26:54.621037
- 🔗 alfagok.diginaut.net 🧩 #379 🥳 14 ⏱️ 0:00:45.177278
- 🔗 alphaguess.com 🧩 #845 🥳 10 ⏱️ 0:00:22.996636
- 🔗 squareword.org 🧩 #1385 🥳 8 ⏱️ 0:02:00.527775
- 🔗 dictionary.com hurdle 🧩 #1415 🥳 18 ⏱️ 0:03:42.912329
- 🔗 dontwordle.com 🧩 #1272 🥳 6 ⏱️ 0:01:06.483474
- 🔗 cemantle.certitudes.org 🧩 #1322 🥳 58 ⏱️ 0:00:23.026139
- 🔗 cemantix.certitudes.org 🧩 #1355 🥳 257 ⏱️ 0:02:11.471815

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












# spaceword.org 🧩 2025-11-15 🏁 score 2168 ranked 41.0% 136/332 ⏱️ 0:26:54.621037

📜 5 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 136/332

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ J E E _ Y _ G O _   
      _ E _ A B O D E S _   
      _ S Q U I D _ E _ _   
      _ S _ _ _ _ _ Z _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #379 🥳 14 ⏱️ 0:00:45.177278

🤔 14 attempts
📜 1 sessions

    @        [     0] &-teken        
    @+1      [     1] &-tekens       
    @+2      [     2] -cijferig      
    @+3      [     3] -e-mail        
    @+8648   [  8648] af             q4  ? after
    @+16155  [ 16155] am             q5  ? after
    @+20529  [ 20529] arg            q6  ? after
    @+20557  [ 20557] argument       q13 ? it
    @+20557  [ 20557] argument       done. it
    @+20584  [ 20584] aria           q12 ? before
    @+20668  [ 20668] arm            q11 ? before
    @+21032  [ 21032] arrondissement q10 ? before
    @+21538  [ 21538] asiel          q8  ? before
    @+22704  [ 22704] audit          q7  ? before
    @+24909  [ 24909] bad            q3  ? before
    @+49909  [ 49909] bol            q2  ? before
    @+99839  [ 99839] examen         q1  ? before
    @+199763 [199763] lijn           q0  ? before

# alphaguess.com 🧩 #845 🥳 10 ⏱️ 0:00:22.996636

🤔 10 attempts
📜 1 sessions

    @        [     0] aa      
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98226  [ 98226] mach    q0  ? after
    @+122111 [122111] par     q2  ? after
    @+134642 [134642] prog    q3  ? after
    @+140528 [140528] rec     q4  ? after
    @+140699 [140699] recess  q9  ? it
    @+140699 [140699] recess  done. it
    @+140867 [140867] reclean q8  ? before
    @+141213 [141213] record  q7  ? before
    @+141910 [141910] ree     q6  ? before
    @+143792 [143792] rem     q5  ? before
    @+147331 [147331] rho     q1  ? before

# squareword.org 🧩 #1385 🥳 8 ⏱️ 0:02:00.527775

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟩 🟨
    🟨 🟨 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C O F F
    H A L L O
    A D D E R
    F R E E D
    T E N T S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1415 🥳 18 ⏱️ 0:03:42.912329

📜 2 sessions
💰 score: 9800

    5/6
    EARLS 🟨⬜🟨🟨⬜
    RELIC 🟨🟩🟨⬜⬜
    LEMUR 🟩🟩⬜⬜🟩
    LEGER 🟩🟩⬜🟩🟩
    LEVER 🟩🟩🟩🟩🟩
    5/6
    LEVER ⬜⬜⬜⬜⬜
    ANTIS 🟨⬜⬜⬜🟨
    PSHAW ⬜🟨⬜🟩⬜
    SQUAD 🟩🟩🟩🟩⬜
    SQUAB 🟩🟩🟩🟩🟩
    4/6
    SQUAB ⬜⬜⬜⬜🟨
    ROBIN ⬜⬜🟨🟨⬜
    BIGLY 🟩🟨🟨⬜⬜
    BEIGE 🟩🟩🟩🟩🟩
    3/6
    BEIGE ⬜⬜⬜⬜⬜
    ROAST 🟨⬜⬜🟩⬜
    CRUSH 🟩🟩🟩🟩🟩
    Final 1/2
    SHRUG 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1272 🥳 6 ⏱️ 0:01:06.483474

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:YUKKY n n n n n remain:7806
    ⬜⬜⬜⬜⬜ tried:PAPAW n n n n n remain:3134
    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:1319
    ⬜⬜⬜⬜⬜ tried:DOGGO n n n n n remain:319
    ⬜🟨⬜⬜⬜ tried:BELLE n m n n n remain:16
    🟨⬜🟩⬜⬜ tried:THEFT m n Y n n remain:3

    Undos used: 2

      3 words remaining
    x 8 unused letters
    = 24 total score

# cemantle.certitudes.org 🧩 #1322 🥳 58 ⏱️ 0:00:23.026139

🤔 59 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 13 chat prompts
🤖 13 gemma3:latest replies
🥵  7 😎  5 🥶 43 🧊  3

     $1 #59  ~1 minor          100.00°C 🥳 1000‰
     $2 #43  ~8 unintentional   41.54°C 🥵  988‰
     $3 #45  ~7 incidental      39.41°C 🥵  985‰
     $4 #23 ~11 accidental      32.61°C 🥵  954‰
     $5 #46  ~6 sporadic        31.93°C 🥵  941‰
     $6 #52  ~5 fleeting        30.82°C 🥵  923‰
     $7 #53  ~4 intermittent    29.73°C 🥵  906‰
     $8 #42  ~9 unforeseen      29.59°C 🥵  901‰
     $9 #22 ~12 unexpected      29.24°C 😎  890‰
    $10 #13 ~13 fortuity        24.23°C 😎  637‰
    $11 #56  ~2 transient       23.03°C 😎  499‰
    $12 #35 ~10 fortuitous      22.68°C 😎  450‰
    $14 #40     remarkable      19.68°C 🥶
    $57 #55     offshoot        -1.51°C 🧊

# cemantix.certitudes.org 🧩 #1355 🥳 257 ⏱️ 0:02:11.471815

🤔 258 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 61 chat prompts
🤖 61 gemma3:latest replies
🥵   6 😎  24 🥶 203 🧊  24

      $1 #258   ~1 écu             100.00°C 🥳 1000‰
      $2 #248   ~6 écusson          54.26°C 🥵  979‰
      $3 #208  ~13 écartelé         51.86°C 🥵  972‰
      $4 #202  ~14 blason           50.23°C 🥵  970‰
      $5 #211  ~12 vair             45.66°C 🥵  955‰
      $6 #191  ~17 héraldique       42.80°C 🥵  937‰
      $7 #201  ~15 armoiries        40.56°C 🥵  918‰
      $8  #19  ~31 or               34.96°C 😎  848‰
      $9 #213  ~11 chevron          33.75°C 😎  821‰
     $10  #36  ~26 ornement         32.67°C 😎  793‰
     $11 #229   ~8 symbole          31.27°C 😎  743‰
     $12 #250   ~4 sceau            30.98°C 😎  736‰
     $32  #89      motif            22.15°C 🥶
    $235 #153      nuancier         -0.38°C 🧊
