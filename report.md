# 2025-11-24

- 🔗 spaceword.org 🧩 2025-11-23 🏁 score 2173 ranked 8.0% 28/348 ⏱️ 7:29:50.897633
- 🔗 alfagok.diginaut.net 🧩 #387 🥳 19 ⏱️ 0:00:45.738619
- 🔗 alphaguess.com 🧩 #853 🥳 8 ⏱️ 0:00:20.174026
- 🔗 squareword.org 🧩 #1393 🥳 6 ⏱️ 0:02:19.748389
- 🔗 dictionary.com hurdle 🧩 #1423 🥳 18 ⏱️ 0:05:46.696221
- 🔗 dontwordle.com 🧩 #1280 🥳 6 ⏱️ 0:01:24.172579
- 🔗 cemantle.certitudes.org 🧩 #1330 🥳 184 ⏱️ 0:04:52.487038
- 🔗 cemantix.certitudes.org 🧩 #1363 🥳 58 ⏱️ 0:01:26.464437

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




















# spaceword.org 🧩 2025-11-23 🏁 score 2173 ranked 8.0% 28/348 ⏱️ 7:29:50.897633

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 28/348

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ F _ J _ A G _ E _   
      _ I D E A L I Z E R   
      _ B O U S E D _ W _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #387 🥳 19 ⏱️ 0:00:45.738619

🤔 19 attempts
📜 1 sessions

    @        [     0] &-teken         
    @+1      [     1] &-tekens        
    @+2      [     2] -cijferig       
    @+3      [     3] -e-mail         
    @+199762 [199762] lijn            q0  ? after
    @+199762 [199762] lijn            q1  ? after
    @+201914 [201914] loo             q7  ? after
    @+203392 [203392] lucht           q8  ? after
    @+204499 [204499] lul             q9  ? after
    @+205057 [205057] ma              q10 ? after
    @+205180 [205180] maai            q12 ? after
    @+205235 [205235] maal            q13 ? after
    @+205264 [205264] maaltijd        q14 ? after
    @+205299 [205299] maaltijdviering q15 ? after
    @+205307 [205307] maan            q16 ? after
    @+205320 [205320] maanbrieven     q17 ? after
    @+205325 [205325] maand           q18 ? it
    @+205325 [205325] maand           done. it
    @+205333 [205333] maandag         q11 ? before
    @+205614 [205614] maas            q6  ? before
    @+211608 [211608] me              q5  ? before
    @+223487 [223487] mol             q4  ? before
    @+247598 [247598] op              q3  ? before
    @+299645 [299645] schudde         q2  ? before

# alphaguess.com 🧩 #853 🥳 8 ⏱️ 0:00:20.174026

🤔 8 attempts
📜 1 sessions

    @        [     0] aa     
    @+1      [     1] aah    
    @+2      [     2] aahed  
    @+3      [     3] aahing 
    @+98226  [ 98226] mach   q0 ? after
    @+122111 [122111] par    q2 ? after
    @+122850 [122850] part   q7 ? it
    @+122850 [122850] part   done. it
    @+123654 [123654] pay    q6 ? before
    @+125239 [125239] perm   q5 ? before
    @+128373 [128373] place  q4 ? before
    @+134642 [134642] prog   q3 ? before
    @+147331 [147331] rho    q1 ? before

# squareword.org 🧩 #1393 🥳 6 ⏱️ 0:02:19.748389

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    A L O U D
    R E U S E
    S A T I N
    E V E N S
    S E R G E

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1423 🥳 18 ⏱️ 0:05:46.696221

📜 1 sessions
💰 score: 9800

    4/6
    AEONS 🟨⬜⬜🟩⬜
    HAUNT ⬜🟨⬜🟩⬜
    FRANK ⬜⬜🟩🟩🟩
    PLANK 🟩🟩🟩🟩🟩
    5/6
    PLANK ⬜⬜⬜🟩🟩
    BRINK ⬜⬜⬜🟩🟩
    CHUNK ⬜⬜🟩🟩🟩
    STUNK 🟩⬜🟩🟩🟩
    SKUNK 🟩🟩🟩🟩🟩
    3/6
    SKUNK 🟩⬜⬜🟩⬜
    STANE 🟩🟨🟨🟩⬜
    SAINT 🟩🟩🟩🟩🟩
    4/6
    SAINT ⬜⬜🟩⬜⬜
    ORIEL ⬜⬜🟩🟨⬜
    HEIGH ⬜🟨🟩⬜⬜
    JUICE 🟩🟩🟩🟩🟩
    Final 2/2
    VAULT ⬜🟩🟩🟩🟩
    FAULT 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1280 🥳 6 ⏱️ 0:01:24.172579

📜 1 sessions
💰 score: 77

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:DEKED n n n n n remain:5348
    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:2881
    ⬜⬜⬜⬜⬜ tried:FLUFF n n n n n remain:1274
    ⬜⬜⬜⬜⬜ tried:HONOR n n n n n remain:163
    🟨⬜⬜⬜⬜ tried:AGAMA m n n n n remain:32
    ⬜⬜⬜🟨🟩 tried:BYWAY n n n m Y remain:11

    Undos used: 3

      11 words remaining
    x 7 unused letters
    = 77 total score

# cemantle.certitudes.org 🧩 #1330 🥳 184 ⏱️ 0:04:52.487038

🤔 185 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 42 chat prompts
🤖 42 gemma3:27b replies
😱   1 🔥   4 🥵  17 😎  49 🥶 110 🧊   3

      $1 #185   ~1 wipe            100.00°C 🥳 1000‰
      $2 #170  ~12 erase            57.53°C 😱  999‰
      $3 #156  ~21 obliterate       56.11°C 🔥  998‰
      $4 #165  ~16 destroy          50.61°C 🔥  997‰
      $5 #169  ~13 eradicate        49.73°C 🔥  996‰
      $6 #177   ~8 eliminate        49.16°C 🔥  995‰
      $7 #159  ~20 decimate         45.45°C 🥵  985‰
      $8 #154  ~22 annihilate       43.90°C 🥵  981‰
      $9 #182   ~4 ruin             43.51°C 🥵  978‰
     $10 #144  ~29 vanquish         41.80°C 🥵  970‰
     $11 #181   ~5 remove           41.32°C 🥵  968‰
     $24 #166  ~15 dismantle        35.41°C 😎  895‰
     $73 #108      defeat           23.82°C 🥶
    $183  #28      calypso          -3.97°C 🧊

# cemantix.certitudes.org 🧩 #1363 🥳 58 ⏱️ 0:01:26.464437

🤔 59 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 10 chat prompts
🤖 10 gemma3:27b replies
😱  1 🥵  3 😎  6 🥶 42 🧊  6

     $1 #59  ~1 masque          100.00°C 🥳 1000‰
     $2 #42  ~6 déguisement      49.73°C 😱  999‰
     $3 #35  ~7 apparence        36.51°C 🥵  979‰
     $4 #58  ~2 costume          34.87°C 🥵  968‰
     $5 #57  ~3 camouflage       33.49°C 🥵  956‰
     $6 #46  ~5 figure           26.01°C 😎  588‰
     $7 #48  ~4 illusion         24.70°C 😎  406‰
     $8 #33  ~8 allégorie        24.20°C 😎  318‰
     $9 #32  ~9 dissimulation    23.96°C 😎  272‰
    $10 #22 ~10 masqué           23.92°C 😎  267‰
    $11 #15 ~11 caché            23.59°C 😎  181‰
    $12  #8     secret           22.22°C 🥶
    $13 #28     indéchiffrable   22.16°C 🥶
    $54  #9     vélo             -0.14°C 🧊
