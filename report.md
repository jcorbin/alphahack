# 2025-10-18

- 🔗 spaceword.org 🧩 2025-10-17 🏁 score 2173 ranked 3.4% 12/353 ⏱️ 2:37:22.343509
- 🔗 alfagok.diginaut.net 🧩 #350 🥳 12 ⏱️ 0:00:40.135791
- 🔗 alphaguess.com 🧩 #816 🥳 12 ⏱️ 0:00:24.370685
- 🔗 squareword.org 🧩 #1356 🥳 7 ⏱️ 0:01:40.613947
- 🔗 dictionary.com hurdle 🧩 #1386 🥳 17 ⏱️ 0:02:42.262112
- 🔗 dontwordle.com 🧩 #1243 🥳 6 ⏱️ 0:01:10.718365
- 🔗 cemantle.certitudes.org 🧩 #1293 🥳 86 ⏱️ 0:00:34.004266
- 🔗 cemantix.certitudes.org 🧩 #1326 🥳 301 ⏱️ 0:03:08.511131

# Dev

## WIP

## TODO

- meta: alfagok lines not getting collected
  ```
  pick 4754d78e # alfagok.diginaut.net day #345
  ```

- dontword:
  - upsteam site seems to be glitchy wrt generating result copy on mobile
  - workaround by synthesizing?
  - workaround by storing complete-but-unverified anyhow?

- hurdle: report wasn't right out of #1373 -- was missing first few rounds

- square: finish questioning work

- reuse input injection mechanism from store
  - wherever the current input injection usage is
  - and also to allow more seamless meta log continue ...

- meta:
  - `day` command needs to be able to progress even without all solvers done
  - `day` pruning should be more agro
  - rework command model
    * current `log <solver> ...` and `run <solver>` should instead
    * unify into `<solver> log|run ...`
    * with the same stateful sub-prompting so that we can just say `<solver>`
      and then `log ...` and then `run` obviating the `log continue` command
      separate from just `run`
  - review should progress main branch too
  - better logic circa end of day early play, e.g. doing a CET timezone puzzle
    close late in the "prior" day local (EST) time; similarly, early play of
    next-day spaceword should work gracefully
  - support other intervals like weekly/monthly for spaceword

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





# spaceword.org 🧩 2025-10-17 🏁 score 2173 ranked 3.4% 12/353 ⏱️ 2:37:22.343509

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 12/353

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ F _ _ U N _ Q _ J   
      _ R _ A T O M I Z E   
      _ O E D E M A S _ U   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #350 🥳 12 ⏱️ 0:00:40.135791

🤔 12 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199831 [199831] lijm      q0  ? after
    @+199831 [199831] lijm      q1  ? after
    @+199831 [199831] lijm      q2  ? after
    @+299738 [299738] schub     q3  ? after
    @+349513 [349513] vakantie  q4  ? after
    @+374256 [374256] vrij      q5  ? after
    @+374946 [374946] vrouwen   q10 ? after
    @+375231 [375231] vrucht    q11 ? it
    @+375231 [375231] vrucht    done. it
    @+375701 [375701] vuur      q9  ? before
    @+377319 [377319] wandel    q8  ? before
    @+380468 [380468] weer      q7  ? before
    @+386797 [386797] wind      q6  ? before

# alphaguess.com 🧩 #816 🥳 12 ⏱️ 0:00:24.370685

🤔 12 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+1398  [ 1398] acrogen   q6  ? after
    @+2097  [ 2097] ads       q7  ? after
    @+2171  [ 2171] adunc     q10 ? after
    @+2205  [ 2205] adventure q11 ? it
    @+2205  [ 2205] adventure done. it
    @+2245  [ 2245] advert    q9  ? before
    @+2391  [ 2391] aero      q8  ? before
    @+2802  [ 2802] ag        q5  ? before
    @+5882  [ 5882] angel     q4  ? before
    @+11770 [11770] back      q3  ? before
    @+23693 [23693] camp      q2  ? before
    @+47392 [47392] dis       q1  ? before
    @+98231 [98231] mach      q0  ? before

# squareword.org 🧩 #1356 🥳 7 ⏱️ 0:01:40.613947

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    G R A P H
    H E L L O
    O C T E T
    S T E A L
    T A R D Y

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1386 🥳 17 ⏱️ 0:02:42.262112

📜 1 sessions
💰 score: 9900

    6/6
    RATES 🟨⬜⬜🟩⬜
    FRIED ⬜🟨⬜🟩⬜
    HOMER ⬜🟩⬜🟩🟩
    LOWER 🟩🟩⬜🟩🟩
    LONER 🟩🟩⬜🟩🟩
    LOVER 🟩🟩🟩🟩🟩
    3/6
    LOVER ⬜⬜⬜🟩⬜
    SANED ⬜🟨🟩🟩⬜
    APNEA 🟩🟩🟩🟩🟩
    3/6
    APNEA 🟩⬜🟨🟩⬜
    ANTES 🟩🟨⬜🟩⬜
    ALIEN 🟩🟩🟩🟩🟩
    4/6
    ALIEN ⬜⬜⬜⬜⬜
    TUSKY 🟨⬜⬜⬜⬜
    FROTH ⬜⬜🟩🟩🟨
    PHOTO 🟩🟩🟩🟩🟩
    Final 1/2
    SPILT 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1243 🥳 6 ⏱️ 0:01:10.718365

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:PIPIT n n n n n remain:6049
    ⬜⬜⬜⬜⬜ tried:SHOOS n n n n n remain:1695
    ⬜⬜⬜⬜⬜ tried:CULLY n n n n n remain:481
    🟨⬜⬜⬜⬜ tried:ABAKA m n n n n remain:115
    ⬜🟩⬜🟨⬜ tried:RAZER n Y n m n remain:10
    🟨🟩⬜⬜🟩 tried:GAFFE m Y n n Y remain:3

    Undos used: 1

      3 words remaining
    x 8 unused letters
    = 24 total score

# cemantle.certitudes.org 🧩 #1293 🥳 86 ⏱️ 0:00:34.004266

🤔 87 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 17 chat prompts
🤖 17 gemma3:latest replies
🔥  1 🥵  4 😎 16 🥶 64 🧊  1

     $1 #87  ~1 romantic       100.00°C 🥳 1000‰
     $2 #32 ~13 dreamy          57.35°C 🔥  993‰
     $3  #4 ~22 melancholy      50.01°C 🥵  980‰
     $4 #78  ~4 melancholic     47.86°C 🥵  961‰
     $5 #15 ~19 brooding        45.48°C 🥵  935‰
     $6 #60  ~7 wistful         44.24°C 🥵  901‰
     $7 #25 ~17 ethereal        44.10°C 😎  898‰
     $8 #82  ~2 timeless        43.23°C 😎  874‰
     $9 #67  ~6 evocative       43.17°C 😎  872‰
    $10 #77  ~5 lyrical         41.24°C 😎  800‰
    $11 #53 ~10 contemplative   40.42°C 😎  742‰
    $12 #27 ~16 dreamlike       38.43°C 😎  627‰
    $23 #72     resonant        32.09°C 🥶
    $87 #43     shadow          -3.05°C 🧊

# cemantix.certitudes.org 🧩 #1326 🥳 301 ⏱️ 0:03:08.511131

🤔 302 attempts
📜 1 sessions
🫧 16 chat sessions
⁉️ 100 chat prompts
🤖 6 llama3.2:latest replies
🤖 94 gemma3:latest replies
🔥   1 🥵  13 😎  49 🥶 189 🧊  49

      $1 #302   ~1 format           100.00°C 🥳 1000‰
      $2 #139  ~45 bitmap            50.61°C 🔥  996‰
      $3 #176  ~26 encodeur          43.79°C 🥵  977‰
      $4 #126  ~51 pixel             43.74°C 🥵  976‰
      $5 #106  ~61 image             43.42°C 🥵  973‰
      $6 #295   ~4 graphique         42.47°C 🥵  965‰
      $7 #171  ~28 codage            41.97°C 🥵  960‰
      $8 #122  ~53 numérique         41.79°C 🥵  956‰
      $9 #252  ~16 logiciel          41.23°C 🥵  952‰
     $10 #140  ~44 codec             40.90°C 🥵  949‰
     $11 #141  ~43 compression       40.88°C 🥵  948‰
     $16 #137  ~46 vidéo             36.94°C 😎  896‰
     $65 #151      information       23.21°C 🥶
    $254 #138      étude             -0.32°C 🧊
