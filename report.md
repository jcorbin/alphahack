# 2025-11-05

- 🔗 spaceword.org 🧩 2025-11-04 🏁 score 2173 ranked 6.5% 24/367 ⏱️ 0:20:32.980979
- 🔗 alfagok.diginaut.net 🧩 2025-11-05 😦 173 ⏱️ 0:18:36.063343
- 🔗 alphaguess.com 🧩 #834 🥳 15 ⏱️ 0:00:32.684839
- 🔗 squareword.org 🧩 #1374 🥳 9 ⏱️ 0:02:33.404740
- 🔗 dictionary.com hurdle 🧩 #1404 🥳 16 ⏱️ 0:03:51.946731
- 🔗 dontwordle.com 🧩 #1261 🥳 6 ⏱️ 0:01:44.032821
- 🔗 cemantle.certitudes.org 🧩 #1311 🥳 80 ⏱️ 0:02:14.458703
- 🔗 cemantix.certitudes.org 🧩 #1344 🥳 218 ⏱️ 0:07:28.713083

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

# spaceword.org 🧩 2025-11-03 🏁 score 2173 ranked 8.0% 31/389 ⏱️ 0:26:44.989244

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 31/389

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ K E N _ _ _   
      _ _ _ _ A X _ _ _ _   
      _ _ _ _ S U P _ _ _   
      _ _ _ _ _ D O _ _ _   
      _ _ _ _ _ A G _ _ _   
      _ _ _ _ _ T O _ _ _   
      _ _ _ _ Y E N _ _ _   
      _ _ _ _ _ _ I _ _ _   
      _ _ _ _ Z O A _ _ _   


# alfagok.diginaut.net 🧩 2025-11-05 😦 173 ⏱️ 0:18:36.063343

🤔 173 attempts
📜 5 sessions

    @       [    0] &-teken   
    @+49847 [49847] boks      q2   ? after
    @+74758 [74758] dc        q3   ? after
    @+87218 [87218] draag     q4   ? after
    @+90070 [90070] dubbel    q6   ? after
    @+91758 [91758] dwerg     q7   ? after
    @+91966 [91966] dégénéré  q11  ? after
    @+91971 [91971] déjà      q24  ? after
    @+91971 [91971] déjà      q46  ? @+3
    @+91971 [91971] déjà      q47  ? .
    @+91974 [91974] délégué   q48  ? after
    @+91978 [91978] dénk      q33  ? after
    @+91979 [91979] détail    q63  ? after
    @+91979 [91979] détail    <<< SEARCH
    @+91980 [91980] earmarken q123 ? before
    @+91980 [91980] earmarken q145 ? before
    @+91980 [91980] earmarken q157 ? before
    @+91980 [91980] earmarken q164 ? before
    @+91980 [91980] earmarken q168 ? before
    @+91980 [91980] earmarken q170 ? before
    @+91980 [91980] earmarken q172 ? before
    @+91980 [91980] earmarken >>> SEARCH
    @+91998 [91998] ebben     q98  ? before
    @+92006 [92006] ebde      q91  ? before
    @+92007 [92007] ebden     q86  ? before
    @+92008 [92008] ebdeur    q83  ? after
    @+92008 [92008] ebdeur    q84  ? before
    @+92050 [92050] ecart     q9   ? before
    @+92465 [92465] educatie  q8   ? before
    @+93324 [93324] eet       q5   ? before
    @+99623 [99623] ex        q1   ? before

# alphaguess.com 🧩 #834 🥳 15 ⏱️ 0:00:32.684839

🤔 15 attempts
📜 1 sessions

    @        [     0] aa        
    @+1      [     1] aah       
    @+2      [     2] aahed     
    @+3      [     3] aahing    
    @+98226  [ 98226] mach      q0  ? after
    @+147331 [147331] rho       q1  ? after
    @+171931 [171931] tag       q2  ? after
    @+182018 [182018] un        q3  ? after
    @+189281 [189281] vicar     q4  ? after
    @+189691 [189691] viol      q8  ? after
    @+189877 [189877] vis       q9  ? after
    @+190004 [190004] vital     q10 ? after
    @+190024 [190024] vitally   q13 ? after
    @+190030 [190030] vitamin   q14 ? it
    @+190030 [190030] vitamin   done. it
    @+190043 [190043] vitelli   q12 ? before
    @+190084 [190084] vitrified q11 ? before
    @+190164 [190164] vivisect  q7  ? before
    @+191061 [191061] walk      q6  ? before
    @+192885 [192885] whir      q5  ? before

# squareword.org 🧩 #1374 🥳 9 ⏱️ 0:02:33.404740

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟨 🟩 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    E G G E D
    G R I M E
    R A V E N
    E V E N T
    T E N D S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1404 🥳 16 ⏱️ 0:03:51.946731

📜 1 sessions
💰 score: 10000

    2/6
    RESAT ⬜⬜⬜🟨🟩
    GAUNT 🟩🟩🟩🟩🟩
    3/6
    GAUNT ⬜⬜⬜⬜🟨
    TELOS 🟩🟨⬜🟨🟨
    THOSE 🟩🟩🟩🟩🟩
    4/6
    THOSE ⬜⬜⬜⬜🟩
    GRAVE ⬜🟨⬜⬜🟩
    FIBRE 🟨🟩⬜🟨🟩
    RIFLE 🟩🟩🟩🟩🟩
    6/6
    RIFLE ⬜⬜⬜⬜⬜
    AUNTY ⬜🟩⬜⬜🟩
    DUCKY 🟨🟩⬜⬜🟩
    PUDGY ⬜🟩🟩⬜🟩
    MUDDY ⬜🟩🟩🟩🟩
    BUDDY 🟩🟩🟩🟩🟩
    Final 1/2
    DELTA 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1261 🥳 6 ⏱️ 0:01:44.032821

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:SEXES n n n n n remain:3586
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:1856
    ⬜⬜⬜⬜⬜ tried:YABBY n n n n n remain:333
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:100
    ⬜⬜🟨⬜⬜ tried:CRUCK n n m n n remain:9
    🟨⬜⬜🟨⬜ tried:UNWON m n n m n remain:2

    Undos used: 4

      2 words remaining
    x 7 unused letters
    = 14 total score

# cemantle.certitudes.org 🧩 #1311 🥳 80 ⏱️ 0:02:14.458703

🤔 81 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 16 chat prompts
🤖 16 gemma3:latest replies
🔥  2 🥵  3 😎  4 🥶 67 🧊  4

     $1 #81  ~1 indication    100.00°C 🥳 1000‰
     $2 #73  ~5 hint           57.18°C 🔥  998‰
     $3 #80  ~2 clue           51.64°C 🔥  996‰
     $4 #79  ~3 glimpse        36.51°C 🥵  960‰
     $5 #67  ~6 glimmer        34.69°C 🥵  938‰
     $6 #28 ~10 reflection     34.63°C 🥵  935‰
     $7 #74  ~4 illusion       23.07°C 😎  556‰
     $8 #32  ~8 diminution     22.94°C 😎  538‰
     $9 #65  ~7 slight         20.48°C 😎  220‰
    $10 #30  ~9 diminish       20.15°C 😎  156‰
    $11 #36     lingering      19.19°C 🥶
    $12 #58     ebb            19.06°C 🥶
    $13 #31     diminished     19.04°C 🥶
    $78 #68     delicate       -0.32°C 🧊

# cemantix.certitudes.org 🧩 #1344 🥳 218 ⏱️ 0:07:28.713083

🤔 219 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 54 chat prompts
🤖 54 gemma3:latest replies
🔥   1 🥵  29 😎  68 🥶 105 🧊  15

      $1 #219   ~1 rigueur           100.00°C 🥳 1000‰
      $2 #130  ~37 honnêteté          48.33°C 🔥  993‰
      $3 #119  ~42 discrétion         46.32°C 🥵  988‰
      $4  #77  ~66 esprit             45.64°C 🥵  985‰
      $5 #216   ~3 ténacité           45.12°C 🥵  984‰
      $6  #71  ~70 clarté             44.11°C 🥵  979‰
      $7 #165  ~12 modestie           44.01°C 🥵  978‰
      $8  #53  ~79 discernement       43.30°C 🥵  973‰
      $9  #61  ~73 sens               43.00°C 🥵  972‰
     $10  #52  ~80 perspicacité       42.05°C 🥵  971‰
     $11 #142  ~28 humilité           41.24°C 🥵  968‰
     $33  #54  ~78 intelligence       34.75°C 😎  897‰
    $100  #17      subtil             21.39°C 🥶
    $205 #199      détaché            -0.78°C 🧊
