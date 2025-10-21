# 2025-10-22

- 🔗 spaceword.org 🧩 2025-10-21 🏁 score 2173 ranked 5.0% 20/398 ⏱️ 0:18:19.532521
- 🔗 alfagok.diginaut.net 🧩 #354 🥳 15 ⏱️ 0:00:41.238493
- 🔗 alphaguess.com 🧩 #820 🥳 17 ⏱️ 0:00:36.955779
- 🔗 squareword.org 🧩 #1360 🥳 6 ⏱️ 0:01:48.692800
- 🔗 dictionary.com hurdle 🧩 #1390 🥳 21 ⏱️ 0:04:42.366695
- 🔗 dontwordle.com 🧩 #1247 🥳 6 ⏱️ 0:01:33.791529
- 🔗 cemantle.certitudes.org 🧩 #1297 🥳 716 ⏱️ 0:29:09.578201
- 🔗 cemantix.certitudes.org 🧩 #1330 🥳 1832 ⏱️ 5:06:38.313559

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



# spaceword.org 🧩 2025-10-21 🏁 score 2173 ranked 5.0% 20/398 ⏱️ 0:18:19.532521

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 20/398

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ E F _ P A _ R _ D   
      _ R A J A H _ A _ I   
      _ N _ O X I D I Z E   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #354 🥳 15 ⏱️ 0:00:41.238493

🤔 15 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+1      [     1] &-tekens    
    @+2      [     2] -cijferig   
    @+3      [     3] -e-mail     
    @+199830 [199830] lijm        q0  ? after
    @+299737 [299737] schub       q1  ? after
    @+324311 [324311] sub         q3  ? after
    @+336905 [336905] toetsing    q4  ? after
    @+343095 [343095] tv          q5  ? after
    @+344166 [344166] uit         q6  ? after
    @+344498 [344498] uitdeden    q10 ? after
    @+344664 [344664] uitdrupte   q11 ? after
    @+344685 [344685] uiteen      q12 ? after
    @+344758 [344758] uiteenval   q13 ? after
    @+344795 [344795] uiterst     q14 ? it
    @+344795 [344795] uiterst     done. it
    @+344829 [344829] uitga       q9  ? before
    @+345500 [345500] uitgestoten q8  ? before
    @+346834 [346834] uitschreeuw q7  ? before
    @+349512 [349512] vakantie    q2  ? before

# alphaguess.com 🧩 #820 🥳 17 ⏱️ 0:00:36.955779

🤔 17 attempts
📜 2 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+11769 [11769] back      q4  ? after
    @+13811 [13811] be        q6  ? after
    @+14174 [14174] bed       q9  ? after
    @+14400 [14400] bee       q10 ? after
    @+14563 [14563] beg       q11 ? after
    @+14676 [14676] begun     q12 ? after
    @+14696 [14696] behaviour q14 ? after
    @+14707 [14707] behead    q15 ? after
    @+14721 [14721] behind    q16 ? it
    @+14721 [14721] behind    done. it
    @+14732 [14732] behoove   q13 ? before
    @+14788 [14788] bel       q8  ? before
    @+15767 [15767] bewrap    q7  ? before
    @+17724 [17724] blind     q5  ? before
    @+23692 [23692] camp      q3  ? before
    @+47391 [47391] dis       q2  ? before
    @+98230 [98230] mach      q0  ? after
    @+98230 [98230] mach      q1  ? before

# squareword.org 🧩 #1360 🥳 6 ⏱️ 0:01:48.692800

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S L A S H
    T A S T E
    O T H E R
    A H E A D
    T E N D S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1390 🥳 21 ⏱️ 0:04:42.366695

📜 2 sessions
💰 score: 9500

    4/6
    EARLS ⬜⬜⬜🟩🟨
    STYLI 🟩⬜🟨🟩⬜
    SONLY 🟩⬜⬜🟩🟩
    SULLY 🟩🟩🟩🟩🟩
    5/6
    SULLY 🟨⬜⬜⬜🟩
    TIPSY ⬜⬜⬜🟩🟩
    DONSY ⬜🟩⬜🟩🟩
    HORSY ⬜🟩⬜🟩🟩
    MOSSY 🟩🟩🟩🟩🟩
    6/6
    MOSSY ⬜⬜⬜⬜🟩
    INLAY ⬜⬜⬜🟨🟩
    CHARY ⬜⬜🟨⬜🟩
    PAWKY 🟩🟩⬜⬜🟩
    PADDY 🟩🟩⬜⬜🟩
    PATTY 🟩🟩🟩🟩🟩
    5/6
    PATTY ⬜⬜🟨🟩⬜
    MENTO ⬜🟨⬜🟩⬜
    CHUTE ⬜⬜⬜🟩🟩
    FLITE ⬜⬜🟩🟩🟩
    TRITE 🟩🟩🟩🟩🟩
    Final 1/2
    ABLED 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1247 🥳 6 ⏱️ 0:01:33.791529

📜 2 sessions
💰 score: 35

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:JEEZE n n n n n remain:6889
    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:3452
    ⬜⬜⬜⬜⬜ tried:HOWFF n n n n n remain:1203
    ⬜⬜⬜⬜⬜ tried:SULUS n n n n n remain:178
    🟨⬜⬜⬜⬜ tried:ADDAX m n n n n remain:57
    ⬜🟨⬜⬜⬜ tried:CANNY n m n n n remain:5

    Undos used: 2

      5 words remaining
    x 7 unused letters
    = 35 total score

# cemantle.certitudes.org 🧩 #1297 🥳 716 ⏱️ 0:29:09.578201

🤔 717 attempts
📜 1 sessions
🫧 34 chat sessions
⁉️ 219 chat prompts
🤖 58 gemma3:latest replies
🤖 160 llama3.2:latest replies
🔥   5 🥵  33 😎 165 🥶 462 🧊  51

      $1 #717   ~1 utilize           100.00°C 🥳 1000‰
      $2 #191 ~168 augment            56.54°C 🔥  996‰
      $3 #300 ~135 integrate          55.77°C 🔥  994‰
      $4 #315 ~129 combine            54.13°C 🔥  993‰
      $5 #279 ~151 develop            53.93°C 🔥  992‰
      $6 #401 ~107 complement         53.00°C 🔥  990‰
      $7 #285 ~145 optimize           51.70°C 🥵  989‰
      $8 #104 ~172 enable             51.51°C 🥵  988‰
      $9 #709   ~4 leverage           50.70°C 🥵  987‰
     $10 #700  ~10 maximize           50.32°C 🥵  986‰
     $11 #228 ~163 enhance            48.75°C 🥵  982‰
     $40 #708   ~5 access             38.37°C 😎  896‰
    $205 #652      morph              25.09°C 🥶
    $667  #90      conciliator        -0.07°C 🧊

# cemantix.certitudes.org 🧩 #1330 🥳 1832 ⏱️ 5:06:38.313559

🤔 1833 attempts
📜 1 sessions
🫧 106 chat sessions
⁉️ 647 chat prompts
🤖 432 llama3.2:latest replies
🤖 214 gemma3:latest replies
🔥    8 🥵   33 😎  196 🥶 1392 🧊  203

       $1 #1833    ~1 familier           100.00°C 🥳 1000‰
       $2  #158  ~205 étrange             48.00°C 🔥  998‰
       $3  #167  ~202 inconnu             47.58°C 🔥  997‰
       $4  #287  ~169 étrangeté           45.94°C 🔥  996‰
       $5  #439  ~152 langage             45.93°C 🔥  995‰
       $6 #1740   ~11 vocabulaire         45.93°C 🔥  994‰
       $7  #163  ~203 déroutant           44.31°C 🔥  993‰
       $8  #391  ~156 personnage          43.23°C 🔥  991‰
       $9   #58  ~228 lointain            43.18°C 🔥  990‰
      $10  #188  ~191 curieux             42.94°C 🥵  989‰
      $11  #183  ~194 singulier           42.10°C 🥵  985‰
      $43  #377  ~159 récit               35.29°C 😎  897‰
     $239 #1325       rhétorique          25.85°C 🥶
    $1631  #959       libre               -0.03°C 🧊
