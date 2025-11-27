# 2025-11-28

- 🔗 spaceword.org 🧩 2025-11-27 🏁 score 2172 ranked 20.7% 69/334 ⏱️ 7:08:17.843971
- 🔗 alfagok.diginaut.net 🧩 #391 🥳 12 ⏱️ 0:00:46.396771
- 🔗 alphaguess.com 🧩 #857 🥳 10 ⏱️ 0:00:32.121264
- 🔗 squareword.org 🧩 #1397 🥳 7 ⏱️ 0:03:08.790068
- 🔗 dictionary.com hurdle 🧩 #1427 😦 19 ⏱️ 0:03:56.761465
- 🔗 dontwordle.com 🧩 #1284 🥳 6 ⏱️ 0:05:30.885799
- 🔗 cemantle.certitudes.org 🧩 #1334 🥳 283 ⏱️ 0:14:04.669476
- 🔗 cemantix.certitudes.org 🧩 #1367 🥳 83 ⏱️ 0:04:14.397636

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


# spaceword.org 🧩 2025-11-27 🏁 score 2172 ranked 20.7% 69/334 ⏱️ 7:08:17.843971

📜 4 sessions
- tiles: 21/21
- score: 2172 bonus: +72
- rank: 69/334

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ R _ J _ H U T _   
      _ _ A B U S I V E _   
      _ _ P I N E N E _ _   
      _ _ E _ _ Z _ A _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #391 🥳 12 ⏱️ 0:00:46.396771

🤔 12 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199762 [199762] lijn      q0  ? after
    @+299630 [299630] schud     q1  ? after
    @+349362 [349362] vak       q2  ? after
    @+374105 [374105] vrij      q3  ? after
    @+380317 [380317] weer      q5  ? after
    @+380786 [380786] weg       q7  ? after
    @+381971 [381971] wei       q8  ? after
    @+382125 [382125] weinig    q11 ? it
    @+382125 [382125] weinig    done. it
    @+382288 [382288] weledel   q10 ? before
    @+382613 [382613] welzijn   q9  ? before
    @+383293 [383293] werk      q6  ? before
    @+386646 [386646] wind      q4  ? before

# alphaguess.com 🧩 #857 🥳 10 ⏱️ 0:00:32.121264

🤔 10 attempts
📜 1 sessions

    @        [     0] aa     
    @+1      [     1] aah    
    @+2      [     2] aahed  
    @+3      [     3] aahing 
    @+98226  [ 98226] mach   q0  ? after
    @+147331 [147331] rho    q1  ? after
    @+153331 [153331] sea    q4  ? after
    @+153661 [153661] sect   q8  ? after
    @+153835 [153835] seed   q9  ? it
    @+153835 [153835] seed   done. it
    @+154055 [154055] sel    q7  ? before
    @+154897 [154897] seraph q6  ? before
    @+156468 [156468] shit   q5  ? before
    @+159613 [159613] slug   q3  ? before
    @+171931 [171931] tag    q2  ? before

# squareword.org 🧩 #1397 🥳 7 ⏱️ 0:03:08.790068

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    L A S S I
    A U T O S
    K R I L L
    H A L V E
    S L E E T

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1427 😦 19 ⏱️ 0:03:56.761465

📜 1 sessions
💰 score: 4760

    3/6
    PARES ⬜⬜⬜⬜⬜
    ONTIC 🟨⬜🟨🟨⬜
    BIGOT 🟩🟩🟩🟩🟩
    5/6
    BIGOT ⬜⬜⬜🟨🟨
    STONE ⬜🟨🟨⬜⬜
    LOATH ⬜🟩⬜🟩⬜
    DORTY ⬜🟩🟩🟩🟩
    FORTY 🟩🟩🟩🟩🟩
    4/6
    FORTY ⬜⬜⬜🟨⬜
    ISLET 🟨🟨🟨⬜🟨
    TAILS 🟨⬜🟩🟩🟨
    STILL 🟩🟩🟩🟩🟩
    5/6
    STILL 🟩🟩⬜⬜⬜
    STAKE 🟩🟩⬜⬜⬜
    STOMP 🟩🟩⬜⬜⬜
    STUDY 🟩🟩🟩⬜⬜
    STUNG 🟩🟩🟩🟩🟩
    Final 2/2
    CHIDE 🟩🟩🟩⬜⬜
    CHIMP 🟩🟩🟩⬜⬜
    FAIL: CHICK

# dontwordle.com 🧩 #1284 🥳 6 ⏱️ 0:05:30.885799

📜 2 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:OPPOS n n n n n remain:4100
    ⬜⬜⬜⬜⬜ tried:DAGGA n n n n n remain:1211
    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:420
    ⬜⬜⬜⬜⬜ tried:MYTHY n n n n n remain:73
    ⬜⬜⬜⬜🟩 tried:FEEZE n n n n Y remain:5
    🟨🟨⬜⬜🟩 tried:CURVE m m n n Y remain:1

    Undos used: 2

      1 words remaining
    x 6 unused letters
    = 6 total score

# cemantle.certitudes.org 🧩 #1334 🥳 283 ⏱️ 0:14:04.669476

🤔 284 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 33 chat prompts
🤖 33 gpt-oss:120b replies
🔥   2 🥵   6 😎  47 🥶 199 🧊  29

      $1 #284   ~1 pace           100.00°C 🥳 1000‰
      $2 #278   ~2 speed           45.05°C 🔥  991‰
      $3 #249  ~10 momentum        44.82°C 🔥  990‰
      $4  #87  ~38 track           39.73°C 🥵  981‰
      $5 #259   ~7 acceleration    38.72°C 🥵  977‰
      $6 #137  ~30 record          36.11°C 🥵  969‰
      $7 #197  ~21 tally           33.46°C 🥵  948‰
      $8 #110  ~36 trajectory      33.19°C 🥵  944‰
      $9 #146  ~29 score           31.08°C 🥵  916‰
     $10 #206  ~17 progress        29.70°C 😎  893‰
     $11 #212  ~15 growth          29.70°C 😎  892‰
     $12 #200  ~19 trend           29.23°C 😎  879‰
     $57 #275      dynamics        19.43°C 🥶
    $256  #21      separation      -0.22°C 🧊

# cemantix.certitudes.org 🧩 #1367 🥳 83 ⏱️ 0:04:14.397636

🤔 84 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 11 chat prompts
🤖 11 gpt-oss:120b replies
🥵  1 😎 18 🥶 49 🧊 15

     $1 #84  ~1 révélation     100.00°C 🥳 1000‰
     $2 #65  ~6 prophétie       39.98°C 🥵  974‰
     $3 #41 ~14 complot         34.31°C 😎  881‰
     $4 #76  ~2 témoin          34.00°C 😎  871‰
     $5 #49 ~11 conspiration    33.55°C 😎  857‰
     $6 #61  ~8 intrigant       32.70°C 😎  830‰
     $7 #51 ~10 drame           32.44°C 😎  817‰
     $8 #48 ~12 cabale          31.86°C 😎  790‰
     $9 #47 ~13 destin          31.78°C 😎  787‰
    $10 #33 ~16 intrigue        31.04°C 😎  749‰
    $11 #62  ~7 intriguer       29.01°C 😎  581‰
    $12 #27 ~17 histoire        28.67°C 😎  557‰
    $21 #26     critique        24.16°C 🥶
    $70 #35     arc             -0.05°C 🧊
