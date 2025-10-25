# 2025-10-26

- 🔗 spaceword.org 🧩 2025-10-25 🏁 score 2173 ranked 5.6% 20/355 ⏱️ 0:46:38.266264
- 🔗 alfagok.diginaut.net 🧩 #358 🥳 10 ⏱️ 0:00:29.169879
- 🔗 alphaguess.com 🧩 #824 🥳 13 ⏱️ 0:00:29.728720
- 🔗 squareword.org 🧩 #1364 🥳 7 ⏱️ 0:02:23.956204
- 🔗 dictionary.com hurdle 🧩 #1394 🥳 15 ⏱️ 0:02:52.215496
- 🔗 dontwordle.com 🧩 #1251 🥳 6 ⏱️ 0:01:33.842881
- 🔗 cemantle.certitudes.org 🧩 #1301 🥳 764 ⏱️ 1:11:36.482315
- 🔗 cemantix.certitudes.org 🧩 #1334 😦 1250 ⏱️ 3:08:04.051197

# Dev

## WIP

## TODO

- meta: alfagok lines not getting collected
  ```
  pick 4754d78e # alfagok.diginaut.net day #345
  ```

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







# spaceword.org 🧩 2025-10-25 🏁 score 2173 ranked 5.6% 20/355 ⏱️ 0:46:38.266264

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 20/355

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ D O R _ _ _   
      _ _ _ _ A _ E _ _ _   
      _ _ _ _ W A X _ _ _   
      _ _ _ _ _ Q I _ _ _   
      _ _ _ _ N U N _ _ _   
      _ _ _ _ _ A E _ _ _   
      _ _ _ _ A T _ _ _ _   
      _ _ _ _ H I C _ _ _   
      _ _ _ _ _ C _ _ _ _   


# alfagok.diginaut.net 🧩 #358 🥳 10 ⏱️ 0:00:29.169879

🤔 10 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+199830 [199830] lijm       q0  ? after
    @+299732 [299732] schub      q1  ? after
    @+349507 [349507] vakantie   q2  ? after
    @+374250 [374250] vrij       q3  ? after
    @+375695 [375695] vuur       q7  ? after
    @+376491 [376491] waarneming q8  ? after
    @+376855 [376855] wagen      q9  ? it
    @+376855 [376855] wagen      done. it
    @+377313 [377313] wandel     q6  ? before
    @+380462 [380462] weer       q5  ? before
    @+386791 [386791] wind       q4  ? before

# alphaguess.com 🧩 #824 🥳 13 ⏱️ 0:00:29.728720

🤔 13 attempts
📜 1 sessions

    @        [     0] aa      
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98230  [ 98230] mach    q0  ? after
    @+147335 [147335] rho     q1  ? after
    @+171935 [171935] tag     q2  ? after
    @+182022 [182022] un      q3  ? after
    @+189285 [189285] vicar   q4  ? after
    @+192889 [192889] whir    q5  ? after
    @+194714 [194714] worship q6  ? after
    @+195628 [195628] yo      q7  ? after
    @+196086 [196086] zero    q8  ? after
    @+196311 [196311] zone    q9  ? after
    @+196333 [196333] zoo     q10 ? after
    @+196383 [196383] zoom    q12 ? it
    @+196383 [196383] zoom    done. it
    @+196440 [196440] zootier q11 ? before

# squareword.org 🧩 #1364 🥳 7 ⏱️ 0:02:23.956204

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟨 🟩 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P A R S E
    E D I T S
    C O D A S
    A R E N A
    N E R D Y

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1394 🥳 15 ⏱️ 0:02:52.215496

📜 1 sessions
💰 score: 10100

    3/6
    TASER 🟩⬜⬜🟨⬜
    THEIN 🟩⬜🟨🟩⬜
    TEPID 🟩🟩🟩🟩🟩
    3/6
    TEPID ⬜⬜⬜⬜🟩
    ALMUD 🟩🟨⬜⬜🟩
    AHOLD 🟩🟩🟩🟩🟩
    5/6
    AHOLD ⬜⬜⬜⬜⬜
    UTERI 🟨🟨🟨🟨⬜
    RECUT 🟨🟨⬜🟨🟨
    BRUTE 🟨🟨🟨🟨🟨
    TUBER 🟩🟩🟩🟩🟩
    3/6
    TUBER ⬜🟨⬜🟨⬜
    AMUSE ⬜🟨🟩🟩🟩
    MOUSE 🟩🟩🟩🟩🟩
    Final 1/2
    PLEAT 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1251 🥳 6 ⏱️ 0:01:33.842881

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:DUDDY n n n n n remain:7232
    ⬜⬜⬜⬜⬜ tried:TAZZA n n n n n remain:2619
    ⬜⬜⬜⬜⬜ tried:SWOPS n n n n n remain:407
    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:73
    ⬜🟩⬜⬜🟨 tried:FEMME n Y n n m remain:9
    ⬜🟩⬜🟩🟨 tried:HEXER n Y n Y m remain:2

    Undos used: 3

      2 words remaining
    x 7 unused letters
    = 14 total score

# cemantle.certitudes.org 🧩 #1301 🥳 764 ⏱️ 1:11:36.482315

🤔 765 attempts
📜 1 sessions
🫧 28 chat sessions
⁉️ 191 chat prompts
🤖 124 llama3.2:latest replies
🤖 67 gemma3:latest replies
🔥   2 🥵  18 😎  99 🥶 613 🧊  32

      $1 #765   ~1 scare               100.00°C 🥳 1000‰
      $2 #746   ~7 fright               52.31°C 🔥  998‰
      $3 #203  ~83 panic                47.91°C 🔥  997‰
      $4 #604  ~29 terrorize            41.77°C 🥵  986‰
      $5 #694  ~17 jitters              41.52°C 🥵  985‰
      $6 #744   ~9 intimidate           40.19°C 🥵  978‰
      $7 #476  ~44 attack               39.55°C 🥵  976‰
      $8 #238  ~74 frightened           38.10°C 🥵  972‰
      $9 #306  ~65 ruckus               38.05°C 🥵  971‰
     $10 #373  ~57 jittery              37.98°C 🥵  970‰
     $11 #212  ~81 hysteria             37.92°C 🥵  969‰
     $22 #722  ~15 alarm                33.06°C 😎  898‰
    $121 #245      lackluster           22.90°C 🥶
    $734 #340      desolate             -0.09°C 🧊

# cemantix.certitudes.org 🧩 #1334 😦 1250 ⏱️ 3:08:04.051197

🤔 1249 attempts
📜 1 sessions
🫧 98 chat sessions
⁉️ 595 chat prompts
🤖 205 gemma3:latest replies
🤖 390 llama3.2:latest replies
😦 🔥    5 🥵   27 😎  139 🥶  903 🧊  175

       $1   #59  ~159 détente              46.79°C 🔥  998‰
       $2  #135  ~136 ressourcement        44.41°C 🔥  996‰
       $3 #1219    ~2 quiétude             42.71°C 🔥  994‰
       $4   #50  ~162 serein               40.93°C 🔥  992‰
       $5  #121  ~143 épanouissement       39.39°C 🔥  990‰
       $6 #1146   ~17 fertile              38.77°C 🥵  989‰
       $7  #215  ~113 climat               38.21°C 🥵  987‰
       $8  #147  ~132 convivialité         37.40°C 🥵  983‰
       $9 #1182    ~9 reposant             37.34°C 🥵  981‰
      $10 #1127   ~19 recueillement        36.75°C 🥵  980‰
      $11   #44  ~165 paisible             36.09°C 🥵  978‰
      $33  #100  ~150 esprit               28.73°C 😎  892‰
     $172  #270       imagination          19.66°C 🥶
    $1075  #561       réfection            -0.02°C 🧊
