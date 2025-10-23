# 2025-10-24

- 🔗 spaceword.org 🧩 2025-10-23 🏁 score 2173 ranked 6.3% 23/363 ⏱️ 2:39:48.155707
- 🔗 alfagok.diginaut.net 🧩 #356 🥳 19 ⏱️ 0:01:25.033577
- 🔗 alphaguess.com 🧩 #822 🥳 13 ⏱️ 0:00:33.217476
- 🔗 squareword.org 🧩 #1362 🥳 7 ⏱️ 0:01:44.517274
- 🔗 dictionary.com hurdle 🧩 #1392 🥳 22 ⏱️ 0:03:43.927003
- 🔗 dontwordle.com 🧩 #1249 🥳 6 ⏱️ 0:01:37.403780
- 🔗 cemantle.certitudes.org 🧩 #1299 🥳 226 ⏱️ 0:12:56.012136
- 🔗 cemantix.certitudes.org 🧩 #1332 🥳 1027 ⏱️ 0:43:56.344357

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





# spaceword.org 🧩 2025-10-23 🏁 score 2173 ranked 6.3% 23/363 ⏱️ 2:39:48.155707

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 23/363

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ O N _ G A R C O N   
      _ R E N O _ _ _ K A   
      _ C _ E X U V I A _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #356 🥳 19 ⏱️ 0:01:25.033577

🤔 19 attempts
📜 3 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199830 [199830] lijm      q0  ? after
    @+205186 [205186] ma        q11 ? after
    @+206042 [206042] mach      q14 ? after
    @+206166 [206166] macht     q17 ? after
    @+206166 [206166] macht     q18 ? it
    @+206166 [206166] macht     done. it
    @+206597 [206597] mag       q15 ? after
    @+206597 [206597] mag       q16 ? before
    @+207420 [207420] man       q12 ? before
    @+210928 [210928] maïzena   q10 ? before
    @+211719 [211719] mdxxi     q7  ? .
    @+211719 [211719] mdxxi     q8  ? .
    @+223617 [223617] mol       q3  ? before
    @+247728 [247728] op        q2  ? before
    @+299732 [299732] schub     q1  ? before

# alphaguess.com 🧩 #822 🥳 13 ⏱️ 0:00:33.217476

🤔 13 attempts
📜 1 sessions

    @        [     0] aa       
    @+1      [     1] aah      
    @+2      [     2] aahed    
    @+3      [     3] aahing   
    @+98230  [ 98230] mach     q0  ? after
    @+147335 [147335] rho      q1  ? after
    @+153335 [153335] sea      q4  ? after
    @+154901 [154901] seraph   q6  ? after
    @+155642 [155642] sham     q7  ? after
    @+155702 [155702] shammies q10 ? after
    @+155715 [155715] shampoo  q12 ? it
    @+155715 [155715] shampoo  done. it
    @+155732 [155732] shanghai q11 ? before
    @+155761 [155761] shape    q9  ? before
    @+155919 [155919] she      q8  ? before
    @+156472 [156472] shit     q5  ? before
    @+159617 [159617] slug     q3  ? before
    @+171935 [171935] tag      q2  ? before

# squareword.org 🧩 #1362 🥳 7 ⏱️ 0:01:44.517274

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C R A P
    C R E D O
    R O V E R
    I N E P T
    P E L T S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1392 🥳 22 ⏱️ 0:03:43.927003

📜 1 sessions
💰 score: 9400

    6/6
    STEAL ⬜⬜⬜🟩🟩
    BORAL ⬜⬜⬜🟩🟩
    NIDAL ⬜⬜⬜🟩🟩
    FUGAL ⬜⬜⬜🟩🟩
    HALAL ⬜🟩⬜🟩🟩
    PAPAL 🟩🟩🟩🟩🟩
    5/6
    PAPAL ⬜🟩⬜⬜⬜
    NARES ⬜🟩⬜🟨⬜
    CADGE ⬜🟩⬜🟨🟩
    GAUZE 🟩🟩⬜⬜🟩
    GAFFE 🟩🟩🟩🟩🟩
    5/6
    GAFFE ⬜⬜⬜⬜🟨
    DRIES ⬜⬜⬜🟨⬜
    MELTY ⬜🟨⬜⬜🟩
    CHEVY ⬜⬜🟨🟨🟩
    ENVOY 🟩🟩🟩🟩🟩
    5/6
    ENVOY 🟨⬜⬜🟨🟩
    POSEY ⬜🟩⬜🟩🟩
    HOLEY ⬜🟩⬜🟩🟩
    FOGEY ⬜🟩🟩🟩🟩
    BOGEY 🟩🟩🟩🟩🟩
    Final 1/2
    CLOWN 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1249 🥳 6 ⏱️ 0:01:37.403780

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:JUJUS n n n n n remain:5557
    ⬜⬜⬜⬜⬜ tried:ZIZIT n n n n n remain:2711
    ⬜⬜⬜⬜⬜ tried:BOFFO n n n n n remain:1213
    ⬜⬜🟨⬜⬜ tried:NYMPH n n m n n remain:71
    ⬜⬜🟨🟨⬜ tried:CREME n n m m n remain:5
    🟩🟨⬜🟨🟨 tried:MAXED Y m n m m remain:1

    Undos used: 2

      1 words remaining
    x 6 unused letters
    = 6 total score

# cemantle.certitudes.org 🧩 #1299 🥳 226 ⏱️ 0:12:56.012136

🤔 227 attempts
📜 1 sessions
🫧 15 chat sessions
⁉️ 99 chat prompts
🤖 99 gemma3:latest replies
🔥   1 🥵   2 😎  16 🥶 192 🧊  15

      $1 #227   ~1 random            100.00°C 🥳 1000‰
      $2 #149  ~14 randomness         52.64°C 🔥  998‰
      $3 #183   ~9 sequence           30.26°C 🥵  929‰
      $4 #201   ~6 factorial          29.67°C 🥵  909‰
      $5 #208   ~3 nonlinear          29.26°C 😎  894‰
      $6 #205   ~4 sample             29.13°C 😎  889‰
      $7 #143  ~15 entropy            29.08°C 😎  887‰
      $8 #161  ~12 algorithm          27.98°C 😎  844‰
      $9 #181  ~10 probability        26.76°C 😎  747‰
     $10  #13  ~19 mayhem             25.21°C 😎  572‰
     $11 #202   ~5 fractal            25.10°C 😎  561‰
     $12 #198   ~7 digit              24.67°C 😎  514‰
     $20 #153      erratic            22.20°C 🥶
    $213  #36      revolt             -0.03°C 🧊

# cemantix.certitudes.org 🧩 #1332 🥳 1027 ⏱️ 0:43:56.344357

🤔 1028 attempts
📜 1 sessions
🫧 45 chat sessions
⁉️ 288 chat prompts
🤖 141 llama3.2:latest replies
🤖 147 gemma3:latest replies
🔥   3 🥵  24 😎 144 🥶 536 🧊 320

       $1 #1028    ~1 section             100.00°C 🥳 1000‰
       $2  #911   ~42 comité               37.66°C 🔥  995‰
       $3  #968   ~23 département          36.51°C 🔥  993‰
       $4  #843   ~65 conseil              36.03°C 🔥  991‰
       $5  #952   ~27 commission           35.81°C 🔥  990‰
       $6 #1006    ~7 départemental        35.04°C 🥵  988‰
       $7 #1003    ~9 collège              34.93°C 🥵  987‰
       $8  #934   ~31 fédération           34.86°C 🥵  986‰
       $9  #889   ~51 établissement        34.82°C 🥵  985‰
      $10  #885   ~52 enseignement         32.46°C 🥵  974‰
      $11  #159  ~153 affectation          32.35°C 🥵  972‰
      $29  #937   ~30 circonscription      26.52°C 😎  898‰
     $173  #185       pilotage             16.56°C 🥶
     $709  #208       stratégie            -0.01°C 🧊
