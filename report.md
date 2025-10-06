# 2025-10-07

- 🔗 spaceword.org 🧩 2025-10-06 🏁 score 2173 ranked 8.1% 32/397 ⏱️ 3 days, 19:12:25.331105
- 🔗 alfagok.diginaut.net 🧩 #339 🥳 21 ⏱️ 23:10:59.659463
- 🔗 alphaguess.com 🧩 #805 🥳 12 ⏱️ 23:11:34.017588
- 🔗 squareword.org 🧩 #1345 🥳 7 ⏱️ 23:13:57.916345
- 🔗 dictionary.com hurdle 🧩 #1375 🥳 12 ⏱️ 23:17:26.823378
- 🔗 dontwordle.com 🧩 #1232 🥳 6 ⏱️ 23:21:01.512312
- 🔗 cemantle.certitudes.org 🧩 #1282 🥳 264 ⏱️ 23:23:32.459002
- 🔗 cemantix.certitudes.org 🧩 #1315 🥳 287 ⏱️ 23:26:56.505983

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


# spaceword.org 🧩 2025-10-06 🏁 score 2173 ranked 8.1% 32/397 ⏱️ 3 days, 19:12:25.331105

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 32/397

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ E W E _ _ _   
      _ _ _ _ H A D _ _ _   
      _ _ _ _ _ V _ _ _ _   
      _ _ _ _ S E Z _ _ _   
      _ _ _ _ E Y E _ _ _   
      _ _ _ _ G _ A _ _ _   
      _ _ _ _ U _ T _ _ _   
      _ _ _ _ E _ I _ _ _   
      _ _ _ _ D _ N _ _ _   


# alfagok.diginaut.net 🧩 #339 🥳 21 ⏱️ 23:10:59.659463

🤔 21 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+1      [     1] &-tekens     
    @+2      [     2] -cijferig    
    @+3      [     3] -e-mail      
    @+199834 [199834] lijm         q0  ? after
    @+247745 [247745] op           q2  ? after
    @+273551 [273551] proef        q3  ? after
    @+280075 [280075] rechtst      q5  ? after
    @+280816 [280816] redding      q8  ? after
    @+280911 [280911] rede         q10 ? after
    @+281052 [281052] reduceer     q11 ? after
    @+281061 [281061] reductie     q13 ? after
    @+281090 [281090] reductionist q15 ? after
    @+281104 [281104] ree          q16 ? after
    @+281111 [281111] reed         q17 ? after
    @+281115 [281115] reeds        q20 ? it
    @+281115 [281115] reeds        done. it
    @+281117 [281117] reef         q12 ? before
    @+281191 [281191] ref          q9  ? before
    @+281584 [281584] regen        q7  ? before
    @+283166 [283166] rel          q6  ? before
    @+286619 [286619] rijs         q4  ? before
    @+299749 [299749] schub        q1  ? before

# alphaguess.com 🧩 #805 🥳 12 ⏱️ 23:11:34.017588

🤔 12 attempts
📜 1 sessions

    @       [    0] aa     
    @+1     [    1] aah    
    @+2     [    2] aahed  
    @+3     [    3] aahing 
    @+11770 [11770] back   q3  ? after
    @+17725 [17725] blind  q4  ? after
    @+19170 [19170] boot   q6  ? after
    @+19884 [19884] bra    q7  ? after
    @+20279 [20279] braze  q8  ? after
    @+20308 [20308] bread  q11 ? it
    @+20308 [20308] bread  done. it
    @+20342 [20342] break  q10 ? before
    @+20465 [20465] bree   q9  ? before
    @+20697 [20697] brill  q5  ? before
    @+23693 [23693] camp   q2  ? before
    @+47392 [47392] dis    q1  ? before
    @+98231 [98231] mach   q0  ? before

# squareword.org 🧩 #1345 🥳 7 ⏱️ 23:13:57.916345

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟨 🟩 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P O S I T
    L U C R E
    A N I O N
    I C O N S
    D E N S E

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1375 🥳 12 ⏱️ 23:17:26.823378

📜 1 sessions
💰 score: 10400

    2/6
    ACRES 🟨⬜🟨⬜🟨
    ROAST 🟩🟩🟩🟩🟩
    3/6
    ROAST ⬜⬜🟨🟨🟨
    TAPES 🟨🟩⬜🟨🟨
    CASTE 🟩🟩🟩🟩🟩
    2/6
    CASTE ⬜🟩🟩⬜⬜
    BASIL 🟩🟩🟩🟩🟩
    4/6
    BASIL ⬜⬜⬜⬜🟩
    GROWL ⬜🟨⬜⬜🟩
    KNURL ⬜⬜⬜🟨🟩
    REPEL 🟩🟩🟩🟩🟩
    Final 1/2
    ENJOY 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1232 🥳 6 ⏱️ 23:21:01.512312

📜 1 sessions
💰 score: 10

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:ZIZIT n n n n n remain:6979
    ⬜⬜⬜⬜⬜ tried:KABAB n n n n n remain:2765
    ⬜⬜⬜⬜⬜ tried:DUMMY n n n n n remain:870
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:241
    ⬜⬜⬜⬜🟩 tried:FENCE n n n n Y remain:8
    ⬜🟩🟩🟨🟩 tried:WHOSE n Y Y m Y remain:2

    Undos used: 4

      2 words remaining
    x 5 unused letters
    = 10 total score

# cemantle.certitudes.org 🧩 #1282 🥳 264 ⏱️ 23:23:32.459002

🤔 265 attempts
📜 1 sessions
🫧 15 chat sessions
⁉️ 88 chat prompts
🤖 15 llama3.2:latest replies
🤖 73 gemma3:latest replies
🔥   1 🥵  11 😎  48 🥶 203 🧊   1

      $1 #265   ~1 parallel         100.00°C 🥳 1000‰
      $2 #216  ~17 analogous         47.31°C 🔥  998‰
      $3  #11  ~59 contradiction     38.28°C 🥵  977‰
      $4 #140  ~30 divergent         37.85°C 🥵  976‰
      $5 #237  ~10 opposite          37.64°C 🥵  975‰
      $6 #106  ~38 intersect         36.68°C 🥵  962‰
      $7 #228  ~13 similar           36.37°C 🥵  959‰
      $8 #258   ~4 alternating       36.07°C 🥵  955‰
      $9  #61  ~47 binary            35.69°C 🥵  952‰
     $10  #45  ~51 disjunction       35.04°C 🥵  946‰
     $11 #162  ~25 asymmetrical      34.49°C 🥵  937‰
     $14  #95  ~40 overlap           33.29°C 😎  898‰
     $62  #71      divide            25.14°C 🥶
    $265   #7      rust              -8.14°C 🧊

# cemantix.certitudes.org 🧩 #1315 🥳 287 ⏱️ 23:26:56.505983

🤔 288 attempts
📜 1 sessions
🫧 14 chat sessions
⁉️ 89 chat prompts
🤖 10 llama3.2:latest replies
🤖 79 gemma3:latest replies
😱   1 🔥   5 🥵  40 😎  79 🥶 143 🧊  19

      $1 #288   ~1 comparaison       100.00°C 🥳 1000‰
      $2  #72 ~101 comparer           80.63°C 😱  999‰
      $3 #187  ~37 similitude         51.89°C 🔥  995‰
      $4  #45 ~119 analyse            51.74°C 🔥  994‰
      $5  #49 ~116 corrélation        51.69°C 🔥  993‰
      $6 #227  ~15 similarité         51.25°C 🔥  992‰
      $7 #164  ~56 différence         50.29°C 🔥  991‰
      $8 #162  ~58 similaire          47.60°C 🥵  989‰
      $9  #64 ~108 résultat           47.34°C 🥵  988‰
     $10 #146  ~67 extrapolation      47.20°C 🥵  987‰
     $11 #191  ~34 analogie           47.05°C 🥵  986‰
     $48 #100  ~84 distinguer         36.94°C 😎  891‰
    $127  #53      gradient           25.10°C 🥶
    $270 #161      revenir            -0.07°C 🧊
