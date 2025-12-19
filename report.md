# 2025-12-20

- 🔗 spaceword.org 🧩 2025-12-19 🏁 score 2173 ranked 53.5% 174/325 ⏱️ 1:04:50.695140
- 🔗 alfagok.diginaut.net 🧩 #413 🥳 32 ⏱️ 0:01:32.000019
- 🔗 alphaguess.com 🧩 #879 🥳 14 ⏱️ 0:00:29.093923
- 🔗 squareword.org 🧩 #1419 🥳 8 ⏱️ 0:02:23.466836
- 🔗 dictionary.com hurdle 🧩 #1449 🥳 22 ⏱️ 0:03:53.175213
- 🔗 dontwordle.com 🧩 #1306 🥳 6 ⏱️ 0:01:44.185620
- 🔗 cemantle.certitudes.org 🧩 #1356 🥳 15 ⏱️ 0:00:39.088155
- 🔗 cemantix.certitudes.org 🧩 #1389 🥳 466 ⏱️ 0:15:14.792675

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
























# spaceword.org 🧩 2025-12-19 🏁 score 2173 ranked 53.5% 174/325 ⏱️ 1:04:50.695140

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 174/325

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ P E S _ W _ R _   
      _ _ E _ I _ A _ A _   
      _ _ C E C A L _ K _   
      _ _ _ R E X I N E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #413 🥳 32 ⏱️ 0:01:32.000019

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+1      [     1] &-tekens     
    @+2      [     2] -cijferig    
    @+3      [     3] -e-mail      
    @+49851  [ 49851] boks         q2  ? after
    @+74764  [ 74764] dc           q3  ? after
    @+80899  [ 80899] dijk         q5  ? after
    @+84005  [ 84005] donor        q6  ? after
    @+84684  [ 84684] door         q7  ? after
    @+85956  [ 85956] doorstroming q8  ? after
    @+86251  [ 86251] doorzak      q10 ? after
    @+86374  [ 86374] doping       q11 ? after
    @+86457  [ 86457] dopsleutel   q12 ? after
    @+86469  [ 86469] dor          q13 ? after
    @+86511  [ 86511] dormitoria   q27 ? after
    @+86518  [ 86518] dorp         q31 ? it
    @+86518  [ 86518] dorp         done. it
    @+86521  [ 86521] dorpel       q28 ? before
    @+86538  [ 86538] dorps        q9  ? before
    @+87211  [ 87211] draag        q4  ? before
    @+99746  [ 99746] ex           q1  ? before
    @+199824 [199824] lijm         q0  ? before

# alphaguess.com 🧩 #879 🥳 14 ⏱️ 0:00:29.093923

🤔 14 attempts
📜 1 sessions

    @       [    0] aa     
    @+1     [    1] aah    
    @+2     [    2] aahed  
    @+3     [    3] aahing 
    @+47387 [47387] dis    q1  ? after
    @+72806 [72806] gremmy q2  ? after
    @+75962 [75962] haw    q5  ? after
    @+77506 [77506] hetero q6  ? after
    @+77654 [77654] hex    q9  ? after
    @+77754 [77754] hic    q10 ? after
    @+77759 [77759] hiccup q13 ? it
    @+77759 [77759] hiccup done. it
    @+77768 [77768] hick   q12 ? before
    @+77781 [77781] hid    q11 ? before
    @+77859 [77859] high   q8  ? before
    @+78287 [78287] ho     q7  ? before
    @+79138 [79138] hood   q4  ? before
    @+85510 [85510] ins    q3  ? before
    @+98225 [98225] mach   q0  ? before

# squareword.org 🧩 #1419 🥳 8 ⏱️ 0:02:23.466836

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C H A R S
    R I V E N
    A P A C E
    S P I T E
    S O L A R

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1449 🥳 22 ⏱️ 0:03:53.175213

📜 2 sessions
💰 score: 9400

    5/6
    LASER 🟨⬜⬜⬜⬜
    OCULI ⬜⬜🟩🟨⬜
    FLUNK ⬜🟩🟩⬜⬜
    PLUMB 🟩🟩🟩🟩⬜
    PLUMP 🟩🟩🟩🟩🟩
    5/6
    PLUMP ⬜⬜⬜⬜⬜
    ASIDE ⬜⬜🟨⬜⬜
    TONIC 🟨⬜🟨🟨⬜
    NIGHT 🟩🟩⬜⬜🟨
    NIFTY 🟩🟩🟩🟩🟩
    4/6
    NIFTY ⬜⬜⬜⬜⬜
    SOLAR ⬜🟩🟨🟨⬜
    WOALD ⬜🟩🟩🟩⬜
    KOALA 🟩🟩🟩🟩🟩
    6/6
    KOALA ⬜⬜🟩⬜⬜
    TRAMS ⬜🟩🟩⬜⬜
    GRAPE 🟩🟩🟩⬜🟩
    GRADE 🟩🟩🟩⬜🟩
    GRACE 🟩🟩🟩⬜🟩
    GRAVE 🟩🟩🟩🟩🟩
    Final 2/2
    WHALE ⬜🟩🟩🟩🟩
    SHALE 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1306 🥳 6 ⏱️ 0:01:44.185620

📜 1 sessions
💰 score: 48

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MUMUS n n n n n remain:4833
    ⬜⬜⬜⬜⬜ tried:DEKED n n n n n remain:1618
    ⬜⬜⬜⬜⬜ tried:HOOCH n n n n n remain:566
    ⬜⬜⬜⬜⬜ tried:JINNI n n n n n remain:165
    ⬜🟨⬜⬜⬜ tried:XYLYL n m n n n remain:40
    ⬜🟨⬜⬜🟩 tried:BAFFY n m n n Y remain:6

    Undos used: 4

      6 words remaining
    x 8 unused letters
    = 48 total score

# cemantle.certitudes.org 🧩 #1356 🥳 15 ⏱️ 0:00:39.088155

🤔 16 attempts
📜 1 sessions
🫧 1 chat sessions
⁉️ 2 chat prompts
🤖 2 dolphin3:latest replies
🔥  2 🥶 11 🧊  2

     $1 #16  ~1 meditation   100.00°C 🥳 1000‰
     $2 #13  ~3 yoga          68.96°C 🔥  996‰
     $3 #15  ~2 asana         57.64°C 🔥  990‰
     $4  #4     infinity      24.73°C 🥶
     $5  #8     mountain      16.02°C 🥶
     $6 #11     quantum       13.99°C 🥶
     $7  #7     medium         9.45°C 🥶
     $8  #2     automobile     7.63°C 🥶
     $9 #12     very           6.73°C 🥶
    $10  #9     pizza          6.51°C 🥶
    $11 #14     zero           4.23°C 🥶
    $12  #5     low            3.87°C 🥶
    $13  #1     apple          3.51°C 🥶
    $15 #10     probability   -1.74°C 🧊

# cemantix.certitudes.org 🧩 #1389 🥳 466 ⏱️ 0:15:14.792675

🤔 467 attempts
📜 2 sessions
🫧 19 chat sessions
⁉️ 100 chat prompts
🤖 100 dolphin3:latest replies
🔥   6 🥵  14 😎  63 🥶 301 🧊  82

      $1 #467   ~1 commandement        100.00°C 🥳 1000‰
      $2 #426  ~34 armée                59.37°C 🔥  998‰
      $3 #451  ~10 commandant           58.69°C 🔥  997‰
      $4 #454   ~7 officier             52.81°C 🔥  995‰
      $5 #439  ~22 militaire            50.47°C 🔥  994‰
      $6 #434  ~27 escadron             46.25°C 🔥  992‰
      $7 #427  ~33 bataillon            44.65°C 🔥  990‰
      $8 #452   ~9 lieutenant           44.22°C 🥵  988‰
      $9 #441  ~20 régiment             43.24°C 🥵  987‰
     $10 #436  ~25 garnison             42.95°C 🥵  984‰
     $11 #447  ~14 colonel              42.95°C 🥵  985‰
     $22 #287  ~53 mission              33.60°C 😎  898‰
     $85 #422      blitzkrieg           20.28°C 🥶
    $386 #333      détail               -0.11°C 🧊
