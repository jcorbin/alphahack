# 2025-10-20

- 🔗 spaceword.org 🧩 2025-10-19 🏁 score 2173 ranked 2.1% 8/375 ⏱️ 0:27:02.990519
- 🔗 alfagok.diginaut.net 🧩 #352 🥳 21 ⏱️ 0:00:52.096515
- 🔗 alphaguess.com 🧩 #818 🥳 11 ⏱️ 0:00:30.877458
- 🔗 squareword.org 🧩 #1358 🥳 8 ⏱️ 0:03:44.873675
- 🔗 dictionary.com hurdle 🧩 #1388 🥳 19 ⏱️ 0:04:59.751968
- 🔗 dontwordle.com 🧩 #1245 🥳 6 ⏱️ 0:01:53.383513
- 🔗 cemantle.certitudes.org 🧩 #1295 🥳 268 ⏱️ 0:07:38.883875
- 🔗 cemantix.certitudes.org 🧩 #1328 🥳 61 ⏱️ 0:01:32.013834

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

# spaceword.org 🧩 2025-10-19 🏁 score 2173 ranked 2.1% 8/375 ⏱️ 0:27:02.990519

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 8/375

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ W _ F _ O Y _ A I   
      _ E _ A Q U A F I T   
      _ D I X I T S _ S _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #352 🥳 21 ⏱️ 0:00:52.096515

🤔 21 attempts
📜 1 sessions

    @        [     0] &-teken        
    @+1      [     1] &-tekens       
    @+2      [     2] -cijferig      
    @+3      [     3] -e-mail        
    @+199830 [199830] lijm           q0  ? after
    @+199830 [199830] lijm           q1  ? after
    @+299737 [299737] schub          q2  ? after
    @+349512 [349512] vakantie       q3  ? after
    @+353080 [353080] ver            q5  ? after
    @+358373 [358373] verluieren     q7  ? after
    @+359623 [359623] verre          q9  ? after
    @+360311 [360311] verslechter    q10 ? after
    @+360664 [360664] versprekingen  q11 ? after
    @+360763 [360763] verste         q12 ? after
    @+360890 [360890] verstijven     q13 ? after
    @+360954 [360954] verstook       q14 ? after
    @+360968 [360968] verstoot       q16 ? after
    @+360971 [360971] verstop        q17 ? after
    @+360972 [360972] verstoppen     done. it
    @+360973 [360973] verstoppende   q20 ? before
    @+360975 [360975] verstoppertjes q19 ? before
    @+360978 [360978] verstoppinkje  q18 ? before
    @+360984 [360984] verstoren      q15 ? before
    @+361016 [361016] verstrak       q8  ? before
    @+363665 [363665] verzot         q6  ? before
    @+374255 [374255] vrij           q4  ? before

# alphaguess.com 🧩 #818 🥳 11 ⏱️ 0:00:30.877458

🤔 11 attempts
📜 1 sessions

    @        [     0] aa         
    @+1      [     1] aah        
    @+2      [     2] aahed      
    @+3      [     3] aahing     
    @+98231  [ 98231] mach       q0  ? after
    @+147336 [147336] rho        q1  ? after
    @+171936 [171936] tag        q2  ? after
    @+176973 [176973] tom        q4  ? after
    @+179497 [179497] trifurcate q5  ? after
    @+180748 [180748] tune       q6  ? after
    @+180899 [180899] turf       q9  ? after
    @+180948 [180948] turn       q10 ? it
    @+180948 [180948] turn       done. it
    @+181056 [181056] tusk       q8  ? before
    @+181385 [181385] two        q7  ? before
    @+182023 [182023] un         q3  ? before

# squareword.org 🧩 #1358 🥳 8 ⏱️ 0:03:44.873675

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟩 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S L A M S
    W O M A N
    A C U T E
    P A S T A
    S L E E K

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1388 🥳 19 ⏱️ 0:04:59.751968

📜 1 sessions
💰 score: 9700

    5/6
    RENOS ⬜🟩⬜⬜🟨
    TESLA ⬜🟩🟨⬜⬜
    SEDUM 🟩🟩🟨⬜⬜
    SEXED 🟩🟩⬜🟨🟨
    SEEDY 🟩🟩🟩🟩🟩
    4/6
    SEEDY 🟨⬜⬜⬜🟩
    ANTSY ⬜⬜⬜🟨🟩
    HUSKY 🟨⬜🟩⬜🟩
    FISHY 🟩🟩🟩🟩🟩
    4/6
    FISHY ⬜⬜⬜⬜⬜
    ADORN 🟨⬜⬜⬜⬜
    LEAPT ⬜🟩🟩⬜⬜
    WEAVE 🟩🟩🟩🟩🟩
    4/6
    WEAVE ⬜⬜🟨🟨⬜
    AVISO 🟨🟨🟨⬜⬜
    RIVAL ⬜🟩🟨🟨🟨
    VILLA 🟩🟩🟩🟩🟩
    Final 2/2
    STUCK 🟩⬜⬜🟨⬜
    SCORN 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1245 🥳 6 ⏱️ 0:01:53.383513

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:SEXES n n n n n remain:3586
    ⬜⬜⬜⬜⬜ tried:RAGGA n n n n n remain:955
    ⬜⬜⬜⬜⬜ tried:KOOKY n n n n n remain:207
    ⬜⬜⬜⬜⬜ tried:FLUFF n n n n n remain:48
    ⬜🟩🟩⬜⬜ tried:BINDI n Y Y n n remain:6
    🟨🟩🟩⬜⬜ tried:TINCT m Y Y n n remain:1

    Undos used: 3

      1 words remaining
    x 8 unused letters
    = 8 total score

# cemantle.certitudes.org 🧩 #1295 🥳 268 ⏱️ 0:07:38.883875

🤔 269 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 65 chat prompts
🤖 40 llama3.2:latest replies
🤖 25 gemma3:latest replies
🔥   3 🥵   9 😎  31 🥶 179 🧊  46

      $1 #269   ~1 cancel            100.00°C 🥳 1000‰
      $2 #226  ~21 reschedule         72.11°C 🔥  998‰
      $3 #237  ~19 postpone           71.19°C 🔥  997‰
      $4 #190  ~30 postponement       55.14°C 🔥  992‰
      $5 #265   ~5 reconsider         50.46°C 🥵  988‰
      $6 #266   ~4 abandon            49.43°C 🥵  986‰
      $7 #251  ~10 reinstate          46.20°C 🥵  980‰
      $8 #213  ~26 delay              43.09°C 🥵  974‰
      $9 #112  ~42 delayed            41.72°C 🥵  971‰
     $10 #238  ~18 rearrange          41.13°C 🥵  968‰
     $11 #256   ~8 reassess           35.05°C 🥵  926‰
     $14 #159  ~37 renewing           33.35°C 😎  895‰
     $45 #177      reinstatement      19.37°C 🥶
    $224 #206      obstruction        -0.03°C 🧊

# cemantix.certitudes.org 🧩 #1328 🥳 61 ⏱️ 0:01:32.013834

🤔 62 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 12 chat prompts
🤖 12 gemma3:latest replies
🔥  1 🥵  6 😎 10 🥶 40 🧊  4

     $1 #62  ~1 fantôme          100.00°C 🥳 1000‰
     $2 #39  ~9 ombre             50.77°C 🔥  992‰
     $3 #21 ~14 cauchemar         46.70°C 🥵  984‰
     $4 #61  ~2 sombre            44.86°C 🥵  977‰
     $5 #33 ~11 invisible         43.30°C 🥵  972‰
     $6 #15 ~16 brume             41.38°C 🥵  948‰
     $7 #50  ~5 ténèbres          40.46°C 🥵  936‰
     $8 #31 ~12 horreur           39.58°C 🥵  916‰
     $9 #42  ~8 pénombre          37.66°C 😎  866‰
    $10 #59  ~3 obscur            37.33°C 😎  853‰
    $11 #58  ~4 nuit              33.60°C 😎  658‰
    $12 #22 ~13 crépuscule        33.51°C 😎  652‰
    $19 #19     brisé             28.09°C 🥶
    $59 #44     rupture           -2.46°C 🧊
