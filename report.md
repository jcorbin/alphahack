# 2025-10-08

- 🔗 spaceword.org 🧩 2025-10-07 🏁 score 2173 ranked 6.4% 24/374 ⏱️ 0:48:37.812185
- 🔗 alfagok.diginaut.net 🧩 #340 🥳 13 ⏱️ 0:00:40.737095
- 🔗 alphaguess.com 🧩 #806 🥳 13 ⏱️ 0:00:42.991556
- 🔗 squareword.org 🧩 #1346 🥳 7 ⏱️ 0:01:53.873615
- 🔗 dictionary.com hurdle 🧩 #1376 🥳 14 ⏱️ 0:03:11.212753
- 🔗 dontwordle.com 🧩 #1233 🥳 6 ⏱️ 0:01:32.564676
- 🔗 cemantle.certitudes.org 🧩 #1283 🥳 192 ⏱️ 0:01:27.319124
- 🔗 cemantix.certitudes.org 🧩 #1316 🥳 173 ⏱️ 0:02:16.048941

# Dev

## WIP

- meta: review works up to rc branch progression

- StoredLog: ability to easily one-shot report
  - would be nice if it were easier to one-shot report to stdout for dev loop
    i.e. we want to be able to:
    ```shell
    $ LOG_FILE=log/play.dictionary.com_games_todays-hurdle/#1373
    $ python hurdle.py $LOG_FILE -- report
    ```
    to get there:
    1. [X] stored main needs to collect rest args
    2. [ ] rest args need to be passed as first round input
    3. [ ] input injection needs to be reliable, memory is that it's not?
    4. [ ] how to know when to one-shot vs interact? probably "if state calls
           input, let it trampoline normally, but output-only is one-shot"
    5. [ ] expired prompt may get in the way here?

## TODO

- StoredLog: reported elapsed times are wrong; fixing this will probably pull
  down the report-re-run mused about for hurdle report debugging
  - elapsed time is sum of session elapsed
  - ...session elapsed is its last `T` value
  - ...as tracked by `LogParser.log_time.t2`
- hurdle: report wasn't right out of #1373 -- was missing first few rounds

- square: finish questioning work

- meta:
  - review should progress main branch too
  - rework command model
    * current `log <solver> ...` and `run <solver>` should instead
    * unify into `<solver> log|run ...`
    * with the same stateful sub-prompting so that we can just say `<solver>`
      and then `log ...` and then `run` obviating the `log continue` command
      separate from just `run`
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

# spaceword.org 🧩 2025-10-07 🏁 score 2173 ranked 6.4% 24/374 ⏱️ 0:48:37.812185

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 24/374

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ E _ _ _ J _ R A N   
      _ M _ L I O N I Z E   
      _ O X I D E _ B O B   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# alfagok.diginaut.net 🧩 #340 🥳 13 ⏱️ 0:00:40.737095

🤔 13 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+199834 [199834] lijm       q0  ? after
    @+247745 [247745] op         q2  ? after
    @+260632 [260632] pater      q4  ? after
    @+263688 [263688] pi         q6  ? after
    @+265366 [265366] plaatsing  q7  ? after
    @+265450 [265450] plaatsvind q11 ? after
    @+265489 [265489] plafond    q12 ? it
    @+265489 [265489] plafond    done. it
    @+265541 [265541] plag       q10 ? before
    @+265791 [265791] plannen    q9  ? before
    @+266222 [266222] platen     q8  ? before
    @+267085 [267085] plomp      q5  ? before
    @+273551 [273551] proef      q3  ? before
    @+299749 [299749] schub      q1  ? before

# alphaguess.com 🧩 #806 🥳 13 ⏱️ 0:00:42.991556

🤔 13 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+47392 [47392] dis       q1  ? after
    @+72812 [72812] gremolata q2  ? after
    @+85516 [85516] ins       q3  ? after
    @+88676 [88676] jacks     q5  ? after
    @+89069 [89069] jeep      q8  ? after
    @+89109 [89109] jejunum   q11 ? after
    @+89125 [89125] jelly     q12 ? it
    @+89125 [89125] jelly     done. it
    @+89149 [89149] jeopard   q10 ? before
    @+89232 [89232] jet       q9  ? before
    @+89467 [89467] jive      q7  ? before
    @+90266 [90266] kaf       q6  ? before
    @+91861 [91861] knot      q4  ? before
    @+98231 [98231] mach      q0  ? before

# squareword.org 🧩 #1346 🥳 7 ⏱️ 0:01:53.873615

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S U R F S
    P S A L M
    A U D I O
    T R I C K
    S P O K E


# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1376 🥳 14 ⏱️ 0:03:11.212753

📜 1 sessions
💰 score: 10200

    3/6
    REAIS ⬜⬜🟨⬜⬜
    TONAL ⬜⬜⬜🟨🟩
    AWFUL 🟩🟩🟩🟩🟩
    3/6
    AWFUL 🟨🟩⬜⬜⬜
    TWEAK 🟨🟩⬜🟨⬜
    SWATH 🟩🟩🟩🟩🟩
    4/6
    SWATH ⬜⬜⬜⬜⬜
    DECOR ⬜🟩⬜⬜⬜
    BEGUN ⬜🟩🟨⬜🟩
    FEIGN 🟩🟩🟩🟩🟩
    3/6
    FEIGN ⬜⬜🟨🟨⬜
    GIRLS 🟩🟩🟩🟩⬜
    GIRLY 🟩🟩🟩🟩🟩
    Final 1/2
    STALL 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1233 🥳 6 ⏱️ 0:01:32.564676

📜 1 sessions
💰 score: 21

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:EFFED n n n n n remain:5680
    ⬜⬜⬜⬜⬜ tried:KOOKS n n n n n remain:1422
    ⬜⬜⬜⬜⬜ tried:MIMIC n n n n n remain:473
    ⬜⬜⬜⬜⬜ tried:TRUTH n n n n n remain:94
    ⬜🟨⬜⬜⬜ tried:XYLYL n m n n n remain:14
    🟨🟩⬜⬜🟩 tried:GAPPY m Y n n Y remain:3

    Undos used: 3

      3 words remaining
    x 7 unused letters
    = 21 total score

# cemantle.certitudes.org 🧩 #1283 🥳 192 ⏱️ 0:01:27.319124

🤔 193 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 54 chat prompts
🤖 54 gemma3:latest replies
🔥   1 🥵  21 😎  49 🥶 115 🧊   6

      $1 #193   ~1 justify       100.00°C 🥳 1000‰
      $2 #128  ~41 negate         49.33°C 🔥  990‰
      $3 #189   ~4 vindicate      47.40°C 🥵  987‰
      $4 #116  ~48 resist         47.10°C 🥵  985‰
      $5 #141  ~33 refute         44.90°C 🥵  976‰
      $6  #89  ~58 imply          44.75°C 🥵  974‰
      $7 #129  ~40 obviate        44.43°C 🥵  973‰
      $8 #161  ~19 undermine      44.02°C 🥵  971‰
      $9  #80  ~65 conceal        43.96°C 🥵  970‰
     $10 #124  ~44 deter          43.45°C 🥵  968‰
     $11 #184   ~8 disprove       43.36°C 🥵  966‰
     $24  #92  ~56 obfuscate      38.23°C 😎  899‰
     $73  #49      displace       27.31°C 🥶
    $188  #56      imprint        -0.14°C 🧊

# cemantix.certitudes.org 🧩 #1316 🥳 173 ⏱️ 0:02:16.048941

🤔 174 attempts
📜 2 sessions
🫧 7 chat sessions
⁉️ 45 chat prompts
🤖 45 gemma3:latest replies
😱   1 🥵  12 😎  28 🥶 125 🧊   7

      $1 #174   ~1 onde             100.00°C 🥳 1000‰
      $2 #134  ~14 vibration         49.89°C 😱  999‰
      $3 #147  ~10 amplitude         44.53°C 🥵  988‰
      $4 #133  ~15 spectral          41.48°C 🥵  973‰
      $5 #168   ~4 fréquence         41.02°C 🥵  971‰
      $6 #158   ~6 interférence      40.72°C 🥵  968‰
      $7 #129  ~17 réfraction        40.67°C 🥵  967‰
      $8  #72  ~27 spectre           38.91°C 🥵  952‰
      $9 #169   ~3 déphasage         38.63°C 🥵  945‰
     $10 #137  ~13 ondulation        38.45°C 🥵  943‰
     $11  #43  ~37 luminescence      38.02°C 🥵  938‰
     $15 #150   ~9 harmonique        35.25°C 😎  887‰
     $43  #60      prisme            23.39°C 🥶
    $168   #7      secret            -0.09°C 🧊
