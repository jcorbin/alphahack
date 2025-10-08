# 2025-10-09

- 🔗 spaceword.org 🧩 2025-10-08 🏁 score 2173 ranked 3.9% 15/380 ⏱️ 6:39:54.661326
- 🔗 alfagok.diginaut.net 🧩 #341 🥳 11 ⏱️ 0:00:38.021873
- 🔗 alphaguess.com 🧩 #807 🥳 18 ⏱️ 0:00:41.552760
- 🔗 squareword.org 🧩 #1347 🥳 8 ⏱️ 0:02:25.964389
- 🔗 dictionary.com hurdle 🧩 #1377 😦 18 ⏱️ 0:03:07.727537
- 🔗 dontwordle.com 🧩 #1234 🥳 6 ⏱️ 0:01:42.109699
- 🔗 cemantle.certitudes.org 🧩 #1284 🥳 108 ⏱️ 0:00:50.274739
- 🔗 cemantix.certitudes.org 🧩 #1317 🥳 1923 ⏱️ 2:49:26.619732

# Dev

## WIP

- meta: review works up to rc branch progression

- StoredLog: added one-shot canned input from CLI args
  `python whatever.py some/log/maybe -- cmd1 -- cmd2 ...`
- StoredLog: fixed elapsed time reporting

## TODO

- hurdle: report wasn't right out of #1373 -- was missing first few rounds

- square: finish questioning work

- reuse input injection mechanism from store
  - wherever the current input injection usage is
  - and also to allow more seamless meta log continue ...

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


# spaceword.org 🧩 2025-10-08 🏁 score 2173 ranked 3.9% 15/380 ⏱️ 6:39:54.661326

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 15/380

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ K E G _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ _ O B I _ _ _   
      _ _ _ _ H A T _ _ _   
      _ _ _ _ _ R E _ _ _   
      _ _ _ _ D O R _ _ _   
      _ _ _ _ _ Q _ _ _ _   
      _ _ _ _ J U N _ _ _   
      _ _ _ _ O E _ _ _ _   


# alfagok.diginaut.net 🧩 #341 🥳 11 ⏱️ 0:00:38.021873

🤔 11 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+99749  [ 99749] ex         q2  ? after
    @+149452 [149452] huis       q3  ? after
    @+174562 [174562] kind       q4  ? after
    @+180872 [180872] koelt      q6  ? after
    @+183975 [183975] koren      q7  ? after
    @+185462 [185462] kracht     q8  ? after
    @+186309 [186309] kreuk      q9  ? after
    @+186704 [186704] kring      q10 ? it
    @+186704 [186704] kring      done. it
    @+187198 [187198] krontjongs q5  ? before
    @+199834 [199834] lijm       q0  ? after
    @+199834 [199834] lijm       q1  ? before

# alphaguess.com 🧩 #807 🥳 18 ⏱️ 0:00:41.552760

🤔 18 attempts
📜 1 sessions

    @       [    0] aa           
    @+1     [    1] aah          
    @+2     [    2] aahed        
    @+3     [    3] aahing       
    @+47392 [47392] dis          q1  ? after
    @+72812 [72812] gremolata    q2  ? after
    @+79144 [79144] hood         q4  ? after
    @+79927 [79927] hoy          q7  ? after
    @+80057 [80057] hum          q9  ? after
    @+80192 [80192] humor        q10 ? after
    @+80257 [80257] hundred      q11 ? after
    @+80264 [80264] hung         q13 ? after
    @+80271 [80271] hungriest    q15 ? after
    @+80274 [80274] hungrinesses q16 ? after
    @+80275 [80275] hungry       done. it
    @+80276 [80276] hunh         q17 ? before
    @+80277 [80277] hunk         q14 ? before
    @+80292 [80292] hunt         q12 ? before
    @+80327 [80327] hurrah       q8  ? before
    @+80729 [80729] hydroxy      q6  ? before
    @+82321 [82321] immaterial   q5  ? before
    @+85516 [85516] ins          q3  ? before
    @+98231 [98231] mach         q0  ? before

# squareword.org 🧩 #1347 🥳 8 ⏱️ 0:02:25.964389

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟨
    🟨 🟩 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    F L U S H
    A L P H A
    M A S O N
    E M E N D
    D A T E S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1377 😦 18 ⏱️ 0:03:07.727537

📜 1 sessions
💰 score: 3680

    4/6
    SABER ⬜⬜⬜⬜🟩
    INCUR ⬜⬜⬜⬜🟩
    MOTOR ⬜🟩🟩🟩🟩
    ROTOR 🟩🟩🟩🟩🟩
    4/6
    ROTOR ⬜⬜⬜⬜⬜
    LEANS 🟨🟨🟩⬜⬜
    GLADE ⬜🟩🟩⬜🟩
    BLAME 🟩🟩🟩🟩🟩
    4/6
    BLAME ⬜🟨⬜⬜⬜
    COILS ⬜⬜⬜🟩⬜
    HURLY ⬜⬜🟨🟩🟩
    WRYLY 🟩🟩🟩🟩🟩
    6/6
    WRYLY ⬜⬜⬜⬜⬜
    STANE ⬜⬜⬜🟩⬜
    MOUND ⬜🟩🟩🟩🟩
    POUND ⬜🟩🟩🟩🟩
    BOUND ⬜🟩🟩🟩🟩
    FOUND ⬜🟩🟩🟩🟩
    FAIL: HOUND

# dontwordle.com 🧩 #1234 🥳 6 ⏱️ 0:01:42.109699

📜 2 sessions
💰 score: 42

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:VILLI n n n n n remain:6812
    ⬜⬜⬜⬜⬜ tried:SETTS n n n n n remain:1174
    ⬜⬜⬜⬜⬜ tried:GONZO n n n n n remain:293
    ⬜⬜⬜⬜⬜ tried:CHURR n n n n n remain:45
    🟨⬜⬜⬜⬜ tried:ABAKA m n n n n remain:12
    ⬜🟩⬜⬜🟩 tried:DADDY n Y n n Y remain:6

    Undos used: 3

      6 words remaining
    x 7 unused letters
    = 42 total score

# cemantle.certitudes.org 🧩 #1284 🥳 108 ⏱️ 0:00:50.274739

🤔 109 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 32 chat prompts
🤖 32 gemma3:latest replies
😱  1 🔥  2 🥵 12 😎 19 🥶 60 🧊 14

      $1 #109   ~1 relieve        100.00°C 🥳 1000‰
      $2  #99  ~10 alleviate       81.84°C 😱  999‰
      $3 #103   ~6 ease            62.03°C 🔥  998‰
      $4 #104   ~5 lessen          61.60°C 🔥  997‰
      $5 #105   ~4 mitigate        45.93°C 🥵  983‰
      $6  #96  ~13 remedy          45.00°C 🥵  980‰
      $7  #74  ~23 stabilize       41.42°C 🥵  964‰
      $8  #65  ~29 rectify         38.15°C 🥵  939‰
      $9  #86  ~19 fortify         37.99°C 🥵  937‰
     $10  #94  ~15 bolster         37.16°C 🥵  929‰
     $11  #98  ~11 fix             37.05°C 🥵  927‰
     $17 #102   ~7 dampen          34.90°C 😎  888‰
     $36  #57      equilibrate     22.82°C 🥶
     $96  #11      mimicry         -0.04°C 🧊

# cemantix.certitudes.org 🧩 #1317 🥳 1923 ⏱️ 2:49:26.619732

🤔 1924 attempts
📜 4 sessions
🫧 165 chat sessions
⁉️ 837 chat prompts
🤖 36 deepseek-r1:latest replies
🤖 49 gemma2:latest replies
🤖 2 gemma3:12b replies
🤖 636 llama3.2:latest replies
🤖 113 gemma3:latest replies
🔥   6 🥵  34 😎 118 🥶 935 🧊 830

       $1 #1924    ~1 docteur              100.00°C 🥳 1000‰
       $2 #1645   ~26 immunologiste         53.74°C 🔥  998‰
       $3 #1557   ~49 pharmacologue         52.03°C 🔥  995‰
       $4 #1556   ~50 endocrinologue        51.76°C 🔥  994‰
       $5 #1643   ~28 infectiologue         51.61°C 🔥  993‰
       $6  #519  ~151 médecine              49.37°C 🔥  991‰
       $7 #1106   ~90 anesthésiologie       49.26°C 🔥  990‰
       $8 #1644   ~27 biophysicien          49.00°C 🥵  989‰
       $9 #1107   ~89 endocrinologie        46.59°C 🥵  985‰
      $10  #777  ~126 hématologue           45.81°C 🥵  984‰
      $11 #1580   ~42 oncologue             45.32°C 🥵  982‰
      $42  #730  ~138 néphrologie           37.46°C 😎  894‰
     $160  #320       laboratoire           23.68°C 🥶
    $1095 #1349       pancréas              -0.01°C 🧊
