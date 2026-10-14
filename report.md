# 2026-10-15

- 🔗 wordgrid 🧩 #866 🟪 rarity:0.23 ⏱️ 0:03:22.872792
- 🔗 spaceword.org 🧩 2026-10-14 🏁 score 2168 ranked 37.0% 118/319 ⏱️ 1:37:20.313618
- 🔗 alfagok.diginaut.net 🧩 #712 🥳 18 ⏱️ 0:00:27.908995
- 🔗 alphaguess.com 🧩 #1179 🥳 28 ⏱️ 0:00:37.991922
- 🔗 dontwordle.com 🧩 #1605 🥳 6 ⏱️ 0:01:49.522223
- 🔗 dictionary.com hurdle 🧩 #1748 🥳 16 ⏱️ 0:02:18.656862
- 🔗 Quordle Classic 🧩 #1725 🥳 score:24 ⏱️ 0:01:42.865135
- 🔗 Octordle Classic 🧩 #1725 🥳 score:61 ⏱️ 0:03:12.181613
- 🔗 Sedecordle Classic 🧩 #1705 🥳 score:44 ⏱️ 0:04:32.380364
- 🔗 squareword.org 🧩 #1718 🥳 7 ⏱️ 0:04:01.244000
- 🔗 cemantle.certitudes.org 🧩 #1655 🥳 267 ⏱️ 0:14:31.996805
- 🔗 cemantix.certitudes.org 🧩 #1688 🥳 74 ⏱️ 0:03:46.423885

## WIP

- new puzzle: https://fubargames.se/squardle/

- hurdle: add novel words to wordlist

- meta:
  - reprise SolverHarness around `do_sol_*`, re-use them under `do_solve`

- ui:
  - Handle -- stabilizing core over Listing
  - Shell -- minimizing over Handle
- meta: rework command model over Shell
- finish `StoredLog.load` decomposition

## TODO

- semantic:
  - allow "stop after next prompt done" interrupt
  - factor out executive multi-strategy full-auto loop around the current
    best/recent "broad" strategy
  - add a "spike"/"depth" strategy that just tried to chase top-N
  - add model attribution to progress table
  - add used/explored/exploited/attempted counts to prog table
  - ... use such count to get better coverage over hot words
  - ... may replace `~N` scoring

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











# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #866 🟪 rarity:0.23 ⏱️ 0:03:22.872792

📜 2 sessions
🦄 🌌 🌌
🌌 🌌 🌌
🌌 🌌 🦄
Rarity: 0.23 🟪

# [spaceword.org](spaceword.org) 🧩 2026-10-14 🏁 score 2168 ranked 37.0% 118/319 ⏱️ 1:37:20.313618

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 118/319

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ F E V E R S _ J _   
      _ E T _ U _ U _ E _   
      _ Y A H R Z E I T _   
      _ _ _ _ O _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #712 🥳 18 ⏱️ 0:00:27.908995

🤔 18 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199631 [199631] lijk      q0  ? ␅
    @+199631 [199631] lijk      q1  ? after
    @+299532 [299532] schroot   q2  ? ␅
    @+299532 [299532] schroot   q3  ? after
    @+349314 [349314] vakantie  q4  ? ␅
    @+349314 [349314] vakantie  q5  ? after
    @+352878 [352878] ver       q8  ? ␅
    @+352878 [352878] ver       q9  ? after
    @+363463 [363463] verzout   q10 ? ␅
    @+363463 [363463] verzout   q11 ? after
    @+365397 [365397] vis       q14 ? ␅
    @+365397 [365397] vis       q15 ? after
    @+366749 [366749] vlieg     q16 ? ␅
    @+366749 [366749] vlieg     q17 ? it
    @+366749 [366749] vlieg     done. it
    @+368470 [368470] voetbal   q12 ? ␅
    @+368470 [368470] voetbal   q13 ? before
    @+374048 [374048] vrij      q6  ? ␅
    @+374048 [374048] vrij      q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1179 🥳 28 ⏱️ 0:00:37.991922

🤔 28 attempts
📜 1 sessions

    @       [    0] aa      
    @+2     [    2] aahed   
    @+1398  [ 1398] acrogen q12 ? ␅
    @+1398  [ 1398] acrogen q13 ? after
    @+2097  [ 2097] ads     q14 ? ␅
    @+2097  [ 2097] ads     q15 ? after
    @+2391  [ 2391] aero    q16 ? ␅
    @+2391  [ 2391] aero    q17 ? after
    @+2544  [ 2544] aff     q18 ? ␅
    @+2544  [ 2544] aff     q19 ? after
    @+2549  [ 2549] affair  q26 ? ␅
    @+2549  [ 2549] affair  q27 ? it
    @+2549  [ 2549] affair  done. it
    @+2553  [ 2553] affect  q24 ? ␅
    @+2553  [ 2553] affect  q25 ? before
    @+2606  [ 2606] affine  q22 ? ␅
    @+2606  [ 2606] affine  q23 ? before
    @+2666  [ 2666] afford  q20 ? ␅
    @+2666  [ 2666] afford  q21 ? before
    @+2802  [ 2802] ag      q10 ? ␅
    @+2802  [ 2802] ag      q11 ? before
    @+5876  [ 5876] angel   q8  ? ␅
    @+5876  [ 5876] angel   q9  ? before
    @+11763 [11763] back    q6  ? ␅
    @+11763 [11763] back    q7  ? before
    @+23680 [23680] camp    q4  ? ␅
    @+23680 [23680] camp    q5  ? before
    @+47374 [47374] dis     q2  ? ␅
    @+47374 [47374] dis     q3  ? before
    @+98142 [98142] mac     q0  ? ␅
    @+98142 [98142] mac     q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1605 🥳 6 ⏱️ 0:01:49.522223

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:8089
    ⬜⬜⬜⬜⬜ tried:AMASS n n n n n remain:1773
    ⬜⬜⬜⬜⬜ tried:PEWEE n n n n n remain:483
    ⬜⬜⬜⬜⬜ tried:ZIZIT n n n n n remain:137
    ⬜🟩⬜⬜⬜ tried:BUNCH n Y n n n remain:2
    ⬜🟩🟩🟩🟩 tried:FUROR n Y Y Y Y remain:1

    Undos used: 4

      1 words remaining
    x 6 unused letters
    = 6 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1748 🥳 16 ⏱️ 0:02:18.656862

📜 1 sessions
💰 score: 10000

    3/6
    PRASE 🟨⬜🟨⬜🟨
    TAPED 🟨🟨🟨🟨🟨
    ADEPT 🟩🟩🟩🟩🟩
    3/6
    ADEPT ⬜⬜🟨⬜⬜
    REINS 🟩🟩🟨🟨🟨
    RESIN 🟩🟩🟩🟩🟩
    4/6
    RESIN 🟩🟩⬜⬜⬜
    RECTA 🟩🟩⬜⬜🟨
    RELAY 🟩🟩🟩🟩⬜
    RELAX 🟩🟩🟩🟩🟩
    5/6
    RELAX 🟨🟨⬜🟨⬜
    ASPER 🟨⬜⬜🟨🟨
    TRADE ⬜🟩🟩⬜🟩
    BRACE ⬜🟩🟩⬜🟩
    FRAME 🟩🟩🟩🟩🟩
    Final 1/2
    OWLET 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1725 🥳 score:24 ⏱️ 0:01:42.865135

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. STALE attempts:4 score:4
2. EPOCH attempts:7 score:7
3. PIANO attempts:5 score:5
4. CORNY attempts:8 score:8

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1725 🥳 score:61 ⏱️ 0:03:12.181613

📜 1 sessions

Octordle Classic

1. CHILD attempts:7 score:7
2. PHONE attempts:8 score:8
3. CAPER attempts:9 score:9
4. PUSHY attempts:10 score:10
5. CLEAR attempts:4 score:4
6. FEMME attempts:5 score:5
7. SEDAN attempts:6 score:6
8. GAUGE attempts:12 score:12

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1705 🥳 score:44 ⏱️ 0:04:32.380364

📜 1 sessions

Sedecordle Classic sedecordle.com

1. SAPPY attempts:17 score:1
2. SLASH attempts:17 score:7
3. TEACH attempts:7 score:0
4. MAMMY attempts:16 score:7
5. ANNOY attempts:5 score:0
6. ETUDE attempts:6 score:5
7. JAZZY attempts:15 score:1
8. GLASS attempts:14 score:5
9. STUMP attempts:13 score:1
10. SALTY attempts:2 score:3
11. DEBIT attempts:12 score:1
12. FORGO attempts:10 score:2
13. PUFFY attempts:11 score:1
14. CAMEL attempts:4 score:1
15. AGATE attempts:9 score:0
16. LIMBO attempts:8 score:9

# [squareword.org](squareword.org) 🧩 #1718 🥳 7 ⏱️ 0:04:01.244000

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P E L L
    C U R I O
    A R O M A
    R E D I D
    F R E T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1655 🥳 267 ⏱️ 0:14:31.996805

🤔 268 attempts
📜 2 sessions
🫧 10 chat sessions
⁉️ 53 chat prompts
🤖 12 gemma4:12b replies
🤖 41 dolphin3:latest replies
😱   1 🔥   2 🥵  22 😎  53 🥶 173 🧊  16

      $1 #268 seller          100.00°C 🥳 1000‰ ~252 used:0  [251]  source:gemma4  
      $2 #218 buyer            60.62°C 😱  999‰   ~2 used:31 [1]    source:dolphin3
      $3 #239 purchaser        53.76°C 🔥  997‰  ~12 used:15 [11]   source:dolphin3
      $4 #258 retailer         45.48°C 🔥  990‰   ~1 used:2  [0]    source:gemma4  
      $5 #164 sale             44.05°C 🥵  986‰  ~76 used:18 [75]   source:dolphin3
      $6 #259 dealer           43.80°C 🥵  985‰   ~3 used:0  [2]    source:gemma4  
      $7 #260 distributor      43.22°C 🥵  983‰   ~4 used:0  [3]    source:gemma4  
      $8 #217 broker           42.60°C 🥵  980‰  ~13 used:2  [12]   source:dolphin3
      $9 #143 price            41.04°C 🥵  977‰  ~75 used:12 [74]   source:dolphin3
     $10  #26 sales            40.26°C 🥵  976‰  ~78 used:24 [77]   source:dolphin3
     $11 #204 bidder           40.12°C 🥵  975‰  ~14 used:2  [13]   source:dolphin3
     $27 #247 investor         30.40°C 😎  894‰  ~23 used:0  [22]   source:dolphin3
     $80 #265 outlet           18.62°C 🥶        ~79 used:0  [78]   source:gemma4  
    $253  #38 operations       -0.39°C 🧊       ~253 used:0  [252]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1688 🥳 74 ⏱️ 0:03:46.423885

🤔 75 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 22 chat prompts
🤖 22 dolphin3:latest replies
🔥  2 🥵  6 😎 10 🥶 30 🧊 26

     $1 #75 alerte          100.00°C 🥳 1000‰ ~49 used:0  [48]  source:dolphin3
     $2 #74 vigilance        45.85°C 🔥  996‰  ~1 used:2  [0]   source:dolphin3
     $3 #62 surveillance     45.51°C 🔥  995‰  ~2 used:4  [1]   source:dolphin3
     $4 #73 veille           39.08°C 🥵  987‰  ~3 used:0  [2]   source:dolphin3
     $5 #50 sécurité         37.45°C 🥵  985‰  ~8 used:4  [7]   source:dolphin3
     $6 #54 détection        35.14°C 🥵  976‰  ~4 used:0  [3]   source:dolphin3
     $7 #59 prévention       31.91°C 🥵  955‰  ~5 used:0  [4]   source:dolphin3
     $8 #68 monitoring       28.12°C 🥵  916‰  ~6 used:0  [5]   source:dolphin3
     $9 #51 contrôle         27.91°C 🥵  912‰  ~7 used:3  [6]   source:dolphin3
    $10 #58 protection       27.18°C 😎  898‰  ~9 used:0  [8]   source:dolphin3
    $11 #57 intervention     25.30°C 😎  835‰ ~10 used:0  [9]   source:dolphin3
    $12 #55 identification   23.49°C 😎  771‰ ~11 used:0  [10]  source:dolphin3
    $20 #60 régulation       15.99°C 🥶       ~27 used:0  [26]  source:dolphin3
    $50 #19 bourgeon         -0.32°C 🧊       ~50 used:0  [49]  source:dolphin3
