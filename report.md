# 2025-12-18

- 🔗 spaceword.org 🧩 2025-12-17 🏁 score 2173 ranked 8.0% 27/337 ⏱️ 0:13:54.443052
- 🔗 alfagok.diginaut.net 🧩 #411 🥳 13 ⏱️ 0:00:38.473932
- 🔗 alphaguess.com 🧩 #877 🥳 13 ⏱️ 0:00:39.854980
- 🔗 squareword.org 🧩 #1417 🥳 8 ⏱️ 0:02:51.355417
- 🔗 dictionary.com hurdle 🧩 #1447 🥳 17 ⏱️ 0:03:30.952236
- 🔗 dontwordle.com 🧩 #1304 🥳 6 ⏱️ 0:01:40.079707
- 🔗 cemantle.certitudes.org 🧩 #1354 🥳 429 ⏱️ 0:14:05.061219
- 🔗 cemantix.certitudes.org 🧩 #1387 🥳 184 ⏱️ 0:07:36.100376

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






















# spaceword.org 🧩 2025-12-17 🏁 score 2173 ranked 8.0% 27/337 ⏱️ 0:13:54.443052

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 27/337

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ H _ V A S C U L A   
      _ O _ _ _ O I _ O X   
      _ W A L R U S _ P E   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #411 🥳 13 ⏱️ 0:00:38.473932

🤔 13 attempts
📜 2 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+99760  [ 99760] ex        q1  ? after
    @+111415 [111415] ge        q3  ? after
    @+130436 [130436] gracieuze q4  ? after
    @+139793 [139793] hei       q5  ? after
    @+141150 [141150] her       q7  ? after
    @+142777 [142777] hert      q8  ? after
    @+143605 [143605] hij       q9  ? after
    @+144070 [144070] hit       q11 ? after
    @+144265 [144265] hobby     q12 ? it
    @+144265 [144265] hobby     done. it
    @+144562 [144562] hoek      q6  ? before
    @+149456 [149456] huis      q2  ? before
    @+199838 [199838] lijm      q0  ? before

# alphaguess.com 🧩 #877 🥳 13 ⏱️ 0:00:39.854980

🤔 13 attempts
📜 1 sessions

    @       [    0] aa           
    @+1     [    1] aah          
    @+2     [    2] aahed        
    @+3     [    3] aahing       
    @+47387 [47387] dis          q1  ? after
    @+60090 [60090] face         q3  ? after
    @+66446 [66446] french       q4  ? after
    @+69626 [69626] geosynclinal q5  ? after
    @+71216 [71216] gnomist      q6  ? after
    @+71232 [71232] go           q8  ? after
    @+71424 [71424] goglets      q10 ? after
    @+71444 [71444] gold         q12 ? it
    @+71444 [71444] gold         done. it
    @+71517 [71517] gombeen      q11 ? before
    @+71615 [71615] good         q9  ? before
    @+72011 [72011] gracioso     q7  ? before
    @+72806 [72806] gremmy       q2  ? before
    @+98225 [98225] mach         q0  ? before

# squareword.org 🧩 #1417 🥳 8 ⏱️ 0:02:51.355417

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟩 🟩 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B A S A L
    R U M B A
    A D I O S
    T I L D E
    S T E E R

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1447 🥳 17 ⏱️ 0:03:30.952236

📜 1 sessions
💰 score: 9900

    4/6
    REAIS ⬜⬜🟩⬜⬜
    CLAPT ⬜🟩🟩⬜⬜
    FLANK ⬜🟩🟩🟩🟩
    BLANK 🟩🟩🟩🟩🟩
    3/6
    BLANK ⬜⬜⬜🟨⬜
    SNORE ⬜🟩⬜⬜🟨
    UNWED 🟩🟩🟩🟩🟩
    4/6
    UNWED ⬜⬜⬜🟩⬜
    SOREL ⬜⬜⬜🟩⬜
    GAMEY ⬜🟩⬜🟩🟨
    PAYEE 🟩🟩🟩🟩🟩
    4/6
    PAYEE ⬜🟨⬜⬜⬜
    SLAIN ⬜⬜🟩🟩🟩
    GRAIN 🟨⬜🟩🟩🟩
    AGAIN 🟩🟩🟩🟩🟩
    Final 2/2
    FORAY ⬜🟩🟩🟩🟩
    MORAY 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1304 🥳 6 ⏱️ 0:01:40.079707

📜 1 sessions
💰 score: 12

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:8089
    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:4479
    ⬜⬜⬜⬜⬜ tried:EFFED n n n n n remain:1520
    ⬜⬜⬜⬜⬜ tried:KOOKS n n n n n remain:167
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:36
    ⬜⬜🟨🟨⬜ tried:BRUNG n n m m n remain:2

    Undos used: 5

      2 words remaining
    x 6 unused letters
    = 12 total score

# cemantle.certitudes.org 🧩 #1354 🥳 429 ⏱️ 0:14:05.061219

🤔 430 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 69 chat prompts
🤖 69 dolphin3:latest replies
🔥   2 🥵  21 😎  62 🥶 323 🧊  21

      $1 #430   ~1 swim            100.00°C 🥳 1000‰
      $2 #202  ~60 kayak            56.97°C 🔥  996‰
      $3 #198  ~62 paddle           52.38°C 🔥  992‰
      $4 #212  ~56 paddler          49.71°C 🥵  987‰
      $5 #422   ~4 dive             47.89°C 🥵  986‰
      $6 #224  ~51 freestyle        47.71°C 🥵  985‰
      $7 #200  ~61 canoe            46.56°C 🥵  982‰
      $8 #421   ~5 diving           45.99°C 🥵  980‰
      $9 #321  ~39 dinghy           44.72°C 🥵  974‰
     $10 #393  ~12 aquatic          43.53°C 🥵  968‰
     $11 #428   ~2 snorkel          43.50°C 🥵  967‰
     $25 #228  ~50 marathon         34.88°C 😎  898‰
     $87 #387      angling          22.99°C 🥶
    $410 #346      blitz            -0.02°C 🧊

# cemantix.certitudes.org 🧩 #1387 🥳 184 ⏱️ 0:07:36.100376

🤔 185 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 29 chat prompts
🤖 29 dolphin3:latest replies
🥵   5 😎  23 🥶 137 🧊  19

      $1 #185   ~1 sauvage        100.00°C 🥳 1000‰
      $2  #47  ~28 forêt           39.95°C 🥵  969‰
      $3 #122  ~16 toundra         38.65°C 🥵  952‰
      $4 #175   ~2 marécage        36.71°C 🥵  922‰
      $5 #142   ~7 paysage         36.24°C 🥵  906‰
      $6  #59  ~24 montagne        36.15°C 🥵  902‰
      $7 #132  ~11 faune           34.98°C 😎  855‰
      $8  #67  ~23 rocher          34.65°C 😎  833‰
      $9 #160   ~6 montagneux      34.34°C 😎  816‰
     $10  #37  ~29 nature          34.02°C 😎  797‰
     $11 #170   ~4 ravin           33.34°C 😎  751‰
     $12  #53  ~26 fleuve          32.35°C 😎  688‰
     $30 #174      marais          27.68°C 🥶
    $167  #16      kebab           -0.33°C 🧊
