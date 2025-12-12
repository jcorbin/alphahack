# 2025-12-13

- 🔗 spaceword.org 🧩 2025-12-12 🏁 score 2173 ranked 9.7% 33/341 ⏱️ 0:03:43.925994
- 🔗 alfagok.diginaut.net 🧩 #406 🥳 43 ⏱️ 0:02:42.848342
- 🔗 alphaguess.com 🧩 #872 🥳 13 ⏱️ 0:00:35.110531
- 🔗 squareword.org 🧩 #1412 🥳 9 ⏱️ 0:03:13.744084
- 🔗 dictionary.com hurdle 🧩 #1442 😦 15 ⏱️ 0:02:46.271898
- 🔗 dontwordle.com 🧩 #1299 🥳 6 ⏱️ 0:01:25.806077
- 🔗 cemantle.certitudes.org 🧩 #1349 🥳 106 ⏱️ 0:00:58.363510
- 🔗 cemantix.certitudes.org 🧩 #1382 🥳 147 ⏱️ 0:02:47.897507

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

















# spaceword.org 🧩 2025-12-12 🏁 score 2173 ranked 9.7% 33/341 ⏱️ 0:03:43.925994

📜 2 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 33/341

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ J _ _ _ _ E S _ P   
      _ A Z O T E M I A S   
      _ R _ H E X E R E I   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #406 🥳 43 ⏱️ 0:02:42.848342

🤔 43 attempts
📜 1 sessions

    @        [     0] &-teken           
    @+1      [     1] &-tekens          
    @+2      [     2] -cijferig         
    @+3      [     3] -e-mail           
    @+99760  [ 99760] ex                q1  ? after
    @+111415 [111415] ge                q3  ? after
    @+116053 [116053] gek               q6  ? after
    @+116641 [116641] gekramd           q9  ? after
    @+116929 [116929] gelat             q10 ? after
    @+116956 [116956] geld              q11 ? after
    @+117012 [117012] geldelijke        q34 ? after
    @+117013 [117013] gelden            q42 ? it
    @+117013 [117013] gelden            done. it
    @+117014 [117014] geldend           q41 ? before
    @+117015 [117015] geldende          q39 ? before
    @+117018 [117018] gelderland-midden q38 ? .
    @+117022 [117022] geldersmannen     q33 ? .
    @+117024 [117024] geldezel          q36 ? before
    @+117038 [117038] geldhandel        q35 ? before
    @+117071 [117071] geldinkomen       q12 ? before
    @+117207 [117207] geldt             q8  ? before
    @+118389 [118389] geluk             q7  ? before
    @+120905 [120905] gequeruleerd      q5  ? before
    @+130415 [130415] gracieuze         q4  ? before
    @+149436 [149436] huis              q2  ? before
    @+199818 [199818] lijm              q0  ? before

# alphaguess.com 🧩 #872 🥳 13 ⏱️ 0:00:35.110531

🤔 13 attempts
📜 1 sessions

    @        [     0] aa       
    @+1      [     1] aah      
    @+2      [     2] aahed    
    @+3      [     3] aahing   
    @+98225  [ 98225] mach     q0  ? after
    @+147330 [147330] rho      q1  ? after
    @+159612 [159612] slug     q3  ? after
    @+165766 [165766] stint    q4  ? after
    @+166122 [166122] stop     q8  ? after
    @+166167 [166167] storax   q11 ? after
    @+166169 [166169] store    q12 ? it
    @+166169 [166169] store    done. it
    @+166211 [166211] story    q10 ? before
    @+166320 [166320] straight q9  ? before
    @+166525 [166525] streak   q7  ? before
    @+167290 [167290] sub      q6  ? before
    @+168816 [168816] sulfur   q5  ? before
    @+171930 [171930] tag      q2  ? before

# squareword.org 🧩 #1412 🥳 9 ⏱️ 0:03:13.744084

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟩 🟩
    🟨 🟩 🟩 🟨 🟩
    🟨 🟨 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C R I E S
    H O R D E
    A D A G E
    M E T E D
    P O E S Y

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1442 😦 15 ⏱️ 0:02:46.271898

📜 1 sessions
💰 score: 5160

    3/6
    CANES ⬜⬜🟨⬜⬜
    ROUND 🟨🟨⬜🟩⬜
    WRONG 🟩🟩🟩🟩🟩
    4/6
    WRONG ⬜🟨⬜⬜⬜
    PEARS ⬜🟩⬜🟨⬜
    RECUT 🟩🟩🟨⬜⬜
    RELIC 🟩🟩🟩🟩🟩
    2/6
    RELIC 🟨⬜🟨🟩🟩
    LYRIC 🟩🟩🟩🟩🟩
    4/6
    LYRIC ⬜⬜🟩⬜⬜
    EARNS 🟨⬜🟩⬜⬜
    FORTE ⬜🟩🟩🟩🟩
    TORTE 🟩🟩🟩🟩🟩
    Final 2/2
    FENCE ⬜🟩🟩🟩🟩
    HENCE ⬜🟩🟩🟩🟩
    FAIL: PENCE

# dontwordle.com 🧩 #1299 🥳 6 ⏱️ 0:01:25.806077

📜 1 sessions
💰 score: 21

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:YUMMY n n n n n remain:7572
    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:4016
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:2082
    ⬜⬜⬜⬜⬜ tried:LEVEL n n n n n remain:439
    ⬜⬜⬜⬜⬜ tried:DISCS n n n n n remain:20
    ⬜🟨⬜⬜⬜ tried:BOFFO n m n n n remain:3

    Undos used: 2

      3 words remaining
    x 7 unused letters
    = 21 total score

# cemantle.certitudes.org 🧩 #1349 🥳 106 ⏱️ 0:00:58.363510

🤔 107 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 17 chat prompts
🤖 17 falcon3:10b replies
🥵  1 😎  6 🥶 95 🧊  4

      $1 #107   ~1 cluster         100.00°C 🥳 1000‰
      $2  #93   ~7 nebula           36.01°C 🥵  974‰
      $3 #106   ~2 center           29.80°C 😎  766‰
      $4  #71   ~8 galaxy           29.15°C 😎  713‰
      $5 #104   ~3 galactic         27.99°C 😎  597‰
      $6  #96   ~4 formation        26.41°C 😎  357‰
      $7  #95   ~5 dust             26.37°C 😎  347‰
      $8  #94   ~6 cloud            24.96°C 😎   64‰
      $9  #75      mushroom         24.23°C 🥶
     $10  #39      interface        23.81°C 🥶
     $11 #102      disk             22.86°C 🥶
     $12  #44      network          21.73°C 🥶
     $13  #79      rainbow          21.59°C 🥶
    $104  #18      card             -0.36°C 🧊

# cemantix.certitudes.org 🧩 #1382 🥳 147 ⏱️ 0:02:47.897507

🤔 148 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 42 chat prompts
🤖 42 falcon3:10b replies
🔥  2 🥵  5 😎 28 🥶 90 🧊 22

      $1 #148   ~1 coûteux          100.00°C 🥳 1000‰
      $2 #128   ~9 rentable          55.17°C 🔥  996‰
      $3 #144   ~4 coût              54.40°C 🔥  995‰
      $4  #73  ~30 réduire           47.16°C 🥵  979‰
      $5 #115  ~19 efficace          46.90°C 🥵  977‰
      $6  #91  ~24 économiser        39.49°C 🥵  916‰
      $7 #132   ~6 investissement    39.29°C 🥵  914‰
      $8 #145   ~3 moins             38.48°C 🥵  901‰
      $9 #130   ~8 effet             38.13°C 😎  894‰
     $10 #137   ~5 productif         37.18°C 😎  871‰
     $11 #118  ~16 avantage          36.60°C 😎  853‰
     $12 #131   ~7 efficient         36.44°C 😎  848‰
     $37 #136      optimal           24.55°C 🥶
    $127  #48      formation         -0.56°C 🧊
