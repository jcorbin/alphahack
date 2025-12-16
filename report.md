# 2025-12-17

- 🔗 spaceword.org 🧩 2025-12-16 🏁 score 2172 ranked 26.7% 90/337 ⏱️ 0:25:31.949390
- 🔗 alfagok.diginaut.net 🧩 #410 🥳 18 ⏱️ 0:02:18.614255
- 🔗 alphaguess.com 🧩 #876 🥳 11 ⏱️ 0:00:35.542769
- 🔗 squareword.org 🧩 #1416 🥳 9 ⏱️ 0:04:05.175555
- 🔗 dictionary.com hurdle 🧩 #1446 🥳 20 ⏱️ 0:03:22.702427
- 🔗 dontwordle.com 🧩 #1303 🥳 6 ⏱️ 0:02:40.775414
- 🔗 cemantle.certitudes.org 🧩 #1353 🥳 52 ⏱️ 0:03:32.592577
- 🔗 cemantix.certitudes.org 🧩 #1386 🥳 44 ⏱️ 0:02:05.245163

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





















# spaceword.org 🧩 2025-12-16 🏁 score 2172 ranked 26.7% 90/337 ⏱️ 0:25:31.949390

📜 5 sessions
- tiles: 21/21
- score: 2172 bonus: +72
- rank: 90/337

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ W E A N _ _ O _   
      _ _ _ _ G _ L _ Y _   
      _ _ Q U I N A T E _   
      _ _ _ H O O V E R _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #410 🥳 18 ⏱️ 0:02:18.614255

🤔 18 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+1      [     1] &-tekens    
    @+2      [     2] -cijferig   
    @+3      [     3] -e-mail     
    @+199839 [199839] lijm        q0  ? after
    @+299761 [299761] schub       q1  ? after
    @+324337 [324337] sub         q3  ? after
    @+336939 [336939] toetsing    q4  ? after
    @+343129 [343129] tv          q5  ? after
    @+344200 [344200] uit         q6  ? after
    @+346868 [346868] uitschreeuw q7  ? after
    @+347524 [347524] uitvind     q9  ? after
    @+347525 [347525] uitvinden   q17 ? it
    @+347525 [347525] uitvinden   done. it
    @+347526 [347526] uitvindend  q16 ? before
    @+347528 [347528] uitvinder   q15 ? before
    @+347529 [347529] uitvinders  q14 ? before
    @+347541 [347541] uitvis      q13 ? before
    @+347564 [347564] uitvloei    q12 ? before
    @+347632 [347632] uitvoering  q11 ? before
    @+347866 [347866] uitwiedt    q10 ? before
    @+348207 [348207] uitzuig     q8  ? before
    @+349546 [349546] vakantie    q2  ? before

# alphaguess.com 🧩 #876 🥳 11 ⏱️ 0:00:35.542769

🤔 11 attempts
📜 1 sessions

    @        [     0] aa        
    @+1      [     1] aah       
    @+2      [     2] aahed     
    @+3      [     3] aahing    
    @+98225  [ 98225] mach      q0  ? after
    @+147330 [147330] rho       q1  ? after
    @+159612 [159612] slug      q3  ? after
    @+162645 [162645] speed     q5  ? after
    @+164205 [164205] squilgee  q6  ? after
    @+164595 [164595] staminody q8  ? after
    @+164632 [164632] stand     q10 ? it
    @+164632 [164632] stand     done. it
    @+164739 [164739] star      q9  ? before
    @+164985 [164985] stay      q7  ? before
    @+165766 [165766] stint     q4  ? before
    @+171930 [171930] tag       q2  ? before

# squareword.org 🧩 #1416 🥳 9 ⏱️ 0:04:05.175555

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B L A S E
    A L B U M
    S A H I B
    E M O T E
    R A R E R

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1446 🥳 20 ⏱️ 0:03:22.702427

📜 1 sessions
💰 score: 9600

    4/6
    MARES ⬜⬜⬜⬜🟨
    SCION 🟩⬜⬜⬜🟨
    SHUNT 🟩⬜🟨🟩⬜
    SUNNY 🟩🟩🟩🟩🟩
    5/6
    SUNNY ⬜⬜⬜⬜⬜
    ALTER 🟩⬜⬜⬜⬜
    AMIGO 🟩⬜🟨⬜⬜
    AFFIX 🟩⬜⬜🟩⬜
    APHID 🟩🟩🟩🟩🟩
    5/6
    APHID ⬜⬜⬜⬜🟨
    DOSER 🟨🟩⬜⬜⬜
    GODLY ⬜🟩🟨⬜🟩
    WOODY ⬜🟩🟩🟩🟩
    MOODY 🟩🟩🟩🟩🟩
    4/6
    MOODY ⬜⬜⬜⬜⬜
    RESIT ⬜⬜⬜⬜⬜
    CHUNK 🟩⬜⬜⬜⬜
    CABAL 🟩🟩🟩🟩🟩
    Final 2/2
    OWLET 🟨⬜🟩🟨⬜
    JELLO 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1303 🥳 6 ⏱️ 0:02:40.775414

📜 1 sessions
💰 score: 18

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:7870
    ⬜⬜⬜⬜⬜ tried:JEEZE n n n n n remain:3879
    ⬜⬜⬜⬜⬜ tried:DADAS n n n n n remain:564
    ⬜⬜⬜⬜⬜ tried:OVOLO n n n n n remain:111
    ⬜⬜⬜⬜🟩 tried:BUTUT n n n n Y remain:3
    🟨⬜⬜⬜🟩 tried:PHPHT m n n n Y remain:2

    Undos used: 4

      2 words remaining
    x 9 unused letters
    = 18 total score

# cemantle.certitudes.org 🧩 #1353 🥳 52 ⏱️ 0:03:32.592577

🤔 53 attempts
📜 1 sessions
🫧 1 chat sessions
⁉️ 12 chat prompts
🤖 12 dolphin3:latest replies
😎  7 🥶 40 🧊  5

     $1 #53  ~1 spin          100.00°C 🥳 1000‰
     $2 #35  ~8 arm            26.88°C 😎  848‰
     $3 #50  ~3 rotate         26.38°C 😎  824‰
     $4 #41  ~7 axis           25.53°C 😎  768‰
     $5 #45  ~5 revolve        25.34°C 😎  757‰
     $6 #51  ~2 gyration       23.43°C 😎  570‰
     $7 #44  ~6 inertia        21.94°C 😎  279‰
     $8 #49  ~4 pivot          21.72°C 😎  235‰
     $9 #48     orbit          20.85°C 🥶
    $10 #34     manipulator    19.54°C 🥶
    $11  #8     robot          18.07°C 🥶
    $12 #38     hand           17.25°C 🥶
    $13 #23     artificial     16.74°C 🥶
    $49 #30     language       -0.38°C 🧊

# cemantix.certitudes.org 🧩 #1386 🥳 44 ⏱️ 0:02:05.245163

🤔 45 attempts
📜 1 sessions
🫧 1 chat sessions
⁉️ 9 chat prompts
🤖 9 dolphin3:latest replies
🔥  1 🥵  2 😎 14 🥶 23 🧊  4

     $1 #45  ~1 demeure     100.00°C 🥳 1000‰
     $2  #1 ~18 château      45.42°C 🔥  996‰
     $3 #41  ~4 logis        35.27°C 🥵  974‰
     $4 #22 ~11 jardin       33.01°C 🥵  954‰
     $5 #31  ~8 hôtel        30.48°C 😎  896‰
     $6 #16 ~14 porche       30.22°C 😎  883‰
     $7 #20 ~12 terrasse     28.70°C 😎  810‰
     $8 #10 ~16 cour         27.40°C 😎  737‰
     $9 #29 ~10 bosquet      27.37°C 😎  735‰
    $10 #43  ~2 bastide      25.82°C 😎  624‰
    $11 #39  ~5 gîte         25.06°C 😎  544‰
    $12 #42  ~3 palais       24.90°C 😎  526‰
    $19 #24     potager      21.08°C 🥶
    $42  #8     vélo         -1.65°C 🧊
