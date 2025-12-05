# 2025-12-06

- 🔗 spaceword.org 🧩 2025-12-05 🏁 score 2173 ranked 7.1% 24/337 ⏱️ 0:18:34.241685
- 🔗 alfagok.diginaut.net 🧩 #399 🥳 13 ⏱️ 0:00:43.716790
- 🔗 alphaguess.com 🧩 #865 🥳 13 ⏱️ 0:00:27.875560
- 🔗 squareword.org 🧩 #1405 🥳 8 ⏱️ 0:02:31.076637
- 🔗 dictionary.com hurdle 🧩 #1435 🥳 19 ⏱️ 0:04:29.065807
- 🔗 dontwordle.com 🧩 #1292 🥳 6 ⏱️ 0:02:39.113922
- 🔗 cemantle.certitudes.org 🧩 #1342 🥳 126 ⏱️ 0:01:59.262973
- 🔗 cemantix.certitudes.org 🧩 #1375 🥳 142 ⏱️ 0:02:08.397959

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










# spaceword.org 🧩 2025-12-05 🏁 score 2173 ranked 7.1% 24/337 ⏱️ 0:18:34.241685

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 24/337

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ C O E Q U A T E S   
      _ O _ T _ _ _ Y _ H   
      _ O X A Z I N E S _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #399 🥳 13 ⏱️ 0:00:43.716790

🤔 13 attempts
📜 1 sessions

    @        [     0] &-teken           
    @+1      [     1] &-tekens          
    @+2      [     2] -cijferig         
    @+3      [     3] -e-mail           
    @+99760  [ 99760] ex                q1  ? after
    @+111415 [111415] ge                q3  ? after
    @+130440 [130440] gracieus          q4  ? after
    @+139799 [139799] hei               q5  ? after
    @+141156 [141156] her               q7  ? after
    @+141499 [141499] heren             q11 ? after
    @+141635 [141635] herfst            q12 ? it
    @+141635 [141635] herfst            done. it
    @+141970 [141970] herkapitaliseerde q10 ? before
    @+142783 [142783] hert              q8  ? before
    @+144569 [144569] hoek              q6  ? before
    @+149463 [149463] huis              q2  ? before
    @+199845 [199845] lijm              q0  ? before

# alphaguess.com 🧩 #865 🥳 13 ⏱️ 0:00:27.875560

🤔 13 attempts
📜 1 sessions

    @        [     0] aa         
    @+1      [     1] aah        
    @+2      [     2] aahed      
    @+3      [     3] aahing     
    @+98225  [ 98225] mach       q0  ? after
    @+101020 [101020] med        q5  ? after
    @+102521 [102521] meth       q6  ? after
    @+103257 [103257] mid        q7  ? after
    @+103417 [103417] mig        q9  ? after
    @+103506 [103506] mile       q10 ? after
    @+103557 [103557] militarist q11 ? after
    @+103576 [103576] milk       q12 ? it
    @+103576 [103576] milk       done. it
    @+103608 [103608] mill       q8  ? before
    @+104173 [104173] miri       q4  ? before
    @+110130 [110130] need       q3  ? before
    @+122110 [122110] par        q2  ? before
    @+147330 [147330] rho        q1  ? before

# squareword.org 🧩 #1405 🥳 8 ⏱️ 0:02:31.076637

📜 2 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟩 🟩
    🟨 🟩 🟨 🟨 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S A F E R
    A L I V E
    T O N I C
    E N A C T
    D E L T A

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1435 🥳 19 ⏱️ 0:04:29.065807

📜 1 sessions
💰 score: 9700

    3/6
    OSIER ⬜⬜⬜⬜⬜
    FUGLY 🟩🟨🟨🟨⬜
    FLUNG 🟩🟩🟩🟩🟩
    4/6
    FLUNG ⬜⬜⬜⬜⬜
    TREAD ⬜🟨⬜⬜🟨
    WORDY 🟨🟩🟨🟩🟩
    ROWDY 🟩🟩🟩🟩🟩
    6/6
    ROWDY ⬜🟩⬜⬜🟩
    SOPHY ⬜🟩⬜⬜🟩
    MONEY ⬜🟩⬜⬜🟩
    LOFTY ⬜🟩🟨⬜🟩
    FOGGY 🟨🟩🟨⬜🟩
    GOOFY 🟩🟩🟩🟩🟩
    5/6
    GOOFY ⬜⬜🟩⬜⬜
    TRODE ⬜⬜🟩⬜🟩
    SWOLE ⬜⬜🟩⬜🟩
    PHONE ⬜🟩🟩⬜🟩
    CHOKE 🟩🟩🟩🟩🟩
    Final 1/2
    LEAPT 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1292 🥳 6 ⏱️ 0:02:39.113922

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:DEKED n n n n n remain:5348
    ⬜⬜⬜⬜⬜ tried:SWISS n n n n n remain:1549
    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:585
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:143
    ⬜⬜🟨⬜⬜ tried:CHOMP n n m n n remain:6
    ⬜🟨🟩🟩🟨 tried:FANON n m Y Y m remain:1

    Undos used: 3

      1 words remaining
    x 6 unused letters
    = 6 total score

# cemantle.certitudes.org 🧩 #1342 🥳 126 ⏱️ 0:01:59.262973

🤔 127 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 36 chat prompts
🤖 36 falcon3:10b replies
🔥  2 🥵  5 😎 15 🥶 99 🧊  5

      $1 #127   ~1 secondary        100.00°C 🥳 1000‰
      $2 #118   ~7 tertiary          47.09°C 😱  999‰
      $3 #120   ~5 education         38.09°C 🔥  997‰
      $4  #47  ~18 middle            30.63°C 🥵  979‰
      $5  #50  ~17 intermediate      30.59°C 🥵  977‰
      $6 #119   ~6 college           30.09°C 🥵  973‰
      $7 #121   ~4 academic          27.71°C 🥵  957‰
      $8 #124   ~3 graduate          24.89°C 🥵  904‰
      $9 #125   ~2 post              24.12°C 😎  873‰
     $10  #36  ~21 central           23.22°C 😎  830‰
     $11 #107   ~9 focal             23.14°C 😎  822‰
     $12  #92  ~12 tier              22.01°C 😎  738‰
     $24  #84      class             17.77°C 🥶
    $123  #39      harmony           -0.89°C 🧊

# cemantix.certitudes.org 🧩 #1375 🥳 142 ⏱️ 0:02:08.397959

🤔 143 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 30 chat prompts
🤖 30 falcon3:10b replies
🔥  3 🥵 16 😎 34 🥶 53 🧊 36

      $1 #143   ~1 télécommunication  100.00°C 🥳 1000‰
      $2 #102  ~25 réseau              51.31°C 🔥  998‰
      $3  #95  ~28 infrastructure      50.93°C 🔥  997‰
      $4 #117  ~14 interconnexion      47.29°C 🔥  992‰
      $5 #132   ~5 technologie         44.66°C 🥵  989‰
      $6  #77  ~38 communication       41.50°C 🥵  983‰
      $7  #98  ~26 maintenance         40.76°C 🥵  982‰
      $8 #120  ~11 service             40.66°C 🥵  980‰
      $9 #122  ~10 ingénierie          39.04°C 🥵  970‰
     $10  #91  ~30 application         37.44°C 🥵  963‰
     $11 #114  ~17 connectivité        35.45°C 🥵  944‰
     $21 #115  ~16 déploiement         31.74°C 😎  898‰
     $55 #101      projet              17.40°C 🥶
    $108   #9      ville               -0.39°C 🧊
