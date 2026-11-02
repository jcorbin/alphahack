# 2026-11-03

- 🔗 wordgrid 🧩 #885 🟪 rarity:0.42 ⏱️ 0:04:02.323598
- 🔗 spaceword.org 🧩 2026-11-02 🏁 score 2168 ranked 36.2% 108/298 ⏱️ 0:10:32.351445
- 🔗 alphaguess.com 🧩 #1198 🥳 22 ⏱️ 0:00:50.048020
- 🔗 dontwordle.com 🧩 #1624 🥳 6 ⏱️ 0:01:37.269758
- 🔗 cemantix.certitudes.org 🧩 #1707 🥳 93 ⏱️ 0:00:48.969164
- 🔗 dictionary.com hurdle 🧩 #1767 🥳 18 ⏱️ 0:04:03.327748
- 🔗 Quordle Classic 🧩 #1744 🥳 score:26 ⏱️ 0:02:13.600569
- 🔗 Octordle Classic 🧩 #1744 🥳 score:59 ⏱️ 0:02:49.891047
- 🔗 Sedecordle Classic 🧩 #1724 🥳 score:45 ⏱️ 0:02:49.128319
- 🔗 squareword.org 🧩 #1737 🥳 7 ⏱️ 0:04:29.865577
- 🔗 cemantle.certitudes.org 🧩 #1674 🥳 826 ⏱️ 1:54:06.723545

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



# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #885 🟪 rarity:0.42 ⏱️ 0:04:02.323598

📜 2 sessions
🌌 🌌 🌌
🦄 🌌 🦄
🦄 🌌 🦄
Rarity: 0.42 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-02 🏁 score 2168 ranked 36.2% 108/298 ⏱️ 0:10:32.351445

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 108/298

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ J O Y _ _ _ _   
      _ _ _ _ R _ _ _ _ _   
      _ _ _ R E F _ _ _ _   
      _ _ _ E _ U _ _ _ _   
      _ _ _ G I S T _ _ _   
      _ _ _ I _ I _ _ _ _   
      _ _ _ V O L E _ _ _   
      _ _ _ E X _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alphaguess.com](alphaguess.com) 🧩 #1198 🥳 22 ⏱️ 0:00:50.048020

🤔 22 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+49066 [49066] disturb   q2  ? ␅
    @+49066 [49066] disturb   q3  ? after
    @+61317 [61317] federal   q6  ? ␅
    @+61317 [61317] federal   q7  ? after
    @+62064 [62064] fey       q14 ? ␅
    @+62064 [62064] fey       q15 ? after
    @+62213 [62213] fiction   q18 ? ␅
    @+62213 [62213] fiction   q19 ? after
    @+62303 [62303] field     q20 ? ␅
    @+62303 [62303] field     q21 ? it
    @+62303 [62303] field     done. it
    @+62411 [62411] fil       q16 ? ␅
    @+62411 [62411] fil       q17 ? before
    @+62815 [62815] fire      q12 ? ␅
    @+62815 [62815] fire      q13 ? before
    @+64371 [64371] fluoresce q10 ? ␅
    @+64371 [64371] fluoresce q11 ? before
    @+67437 [67437] fur       q8  ? ␅
    @+67437 [67437] fur       q9  ? before
    @+73597 [73597] guide     q4  ? ␅
    @+73597 [73597] guide     q5  ? before
    @+98139 [98139] mac       q0  ? ␅
    @+98139 [98139] mac       q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1624 🥳 6 ⏱️ 0:01:37.269758

📜 1 sessions
💰 score: 72

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:ESSES n n n n n remain:3656
    ⬜⬜⬜⬜⬜ tried:GABBA n n n n n remain:1178
    ⬜⬜⬜⬜⬜ tried:MIMIC n n n n n remain:364
    ⬜⬜⬜⬜⬜ tried:PORNO n n n n n remain:26
    ⬜🟨⬜⬜⬜ tried:XYLYL n m n n n remain:11
    ⬜🟩⬜⬜🟩 tried:DUDDY n Y n n Y remain:8

    Undos used: 4

      8 words remaining
    x 9 unused letters
    = 72 total score

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1707 🥳 93 ⏱️ 0:00:48.969164

🤔 94 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 22 chat prompts
🤖 22 nemotron-3-nano:30b-cloud replies
🥵  3 😎  6 🥶 62 🧊 22

     $1 #94 expédition    100.00°C 🥳 1000‰ ~72 used:0 [71]  source:nemotron
     $2 #86 voyage         34.77°C 🥵  975‰  ~3 used:3 [2]   source:nemotron
     $3 #91 exploration    31.92°C 🥵  957‰  ~2 used:2 [1]   source:nemotron
     $4 #79 aventure       29.41°C 🥵  925‰  ~1 used:0 [0]   source:nemotron
     $5 #89 destination    25.60°C 😎  811‰  ~4 used:0 [3]   source:nemotron
     $6 #65 bivouac        24.72°C 😎  777‰  ~7 used:3 [6]   source:nemotron
     $7 #41 frais          23.71°C 😎  714‰  ~8 used:7 [7]   source:nemotron
     $8 #80 campement      22.03°C 😎  602‰  ~5 used:0 [4]   source:nemotron
     $9 #30 désert         20.94°C 😎  491‰  ~9 used:7 [8]   source:nemotron
    $10 #90 départ         20.14°C 😎  418‰  ~6 used:0 [5]   source:nemotron
    $11 #37 caravane       16.51°C 🥶       ~14 used:3 [13]  source:nemotron
    $12 #76 route          16.41°C 🥶       ~18 used:0 [17]  source:nemotron
    $13 #15 chameau        16.12°C 🥶       ~11 used:6 [10]  source:nemotron
    $73 #64 sécheresse     -0.26°C 🧊       ~73 used:0 [72]  source:nemotron

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1767 🥳 18 ⏱️ 0:04:03.327748

📜 1 sessions
💰 score: 9800

    4/6
    LEASH ⬜⬜⬜⬜🟨
    ICHOR 🟨🟨🟨⬜🟨
    SKIMP ⬜⬜🟩⬜🟩
    CHIRP 🟩🟩🟩🟩🟩
    4/6
    CHIRP ⬜🟨⬜⬜⬜
    OATHS ⬜🟨⬜🟨⬜
    HEADY 🟩🟩🟩⬜⬜
    HEAVE 🟩🟩🟩🟩🟩
    5/6
    HEAVE ⬜⬜🟨⬜⬜
    SORTA ⬜⬜⬜⬜🟨
    DAILY 🟩🟩⬜⬜🟩
    BENDY ⬜⬜⬜🟩🟩
    DADDY 🟩🟩🟩🟩🟩
    4/6
    DADDY ⬜🟨⬜⬜⬜
    PLEAS ⬜🟨🟨🟨⬜
    ANGEL 🟩🟩🟩🟨🟨
    ANGLE 🟩🟩🟩🟩🟩
    Final 1/2
    SHEIK 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1744 🥳 score:26 ⏱️ 0:02:13.600569

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. TRIAL attempts:6 score:6
2. STAID attempts:7 score:7
3. LEVEL attempts:9 score:9
4. BONUS attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1744 🥳 score:59 ⏱️ 0:02:49.891047

📜 1 sessions

Octordle Classic

1. JUICY attempts:4 score:4
2. PRIVY attempts:3 score:3
3. GLOVE attempts:6 score:6
4. COLOR attempts:5 score:5
5. GUMMY attempts:11 score:11
6. PUPPY attempts:13 score:13
7. ASKEW attempts:9 score:9
8. CHASE attempts:8 score:8

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1724 🥳 score:45 ⏱️ 0:02:49.128319

📜 2 sessions

Sedecordle Classic sedecordle.com

1. CUMIN attempts:17 score:1
2. SLING attempts:8 score:7
3. STEAL attempts:14 score:1
4. AGILE attempts:6 score:4
5. BOAST attempts:12 score:1
6. LEMON attempts:3 score:2
7. REBAR attempts:9 score:0
8. FISHY attempts:13 score:9
9. FLOWN attempts:15 score:1
10. BEGUN attempts:4 score:5
11. EASEL attempts:11 score:1
12. BENCH attempts:10 score:1
13. ABBEY attempts:5 score:0
14. WASTE attempts:16 score:5
15. ABORT attempts:7 score:0
16. LATCH attempts:17 score:7

# [squareword.org](squareword.org) 🧩 #1737 🥳 7 ⏱️ 0:04:29.865577

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟨 🟨
    🟩 🟨 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    T S A R S
    A T T I C
    P U R G E
    A N I O N
    A T T I C

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1674 🥳 826 ⏱️ 1:54:06.723545

🤔 827 attempts
📜 1 sessions
🫧 56 chat sessions
⁉️ 309 chat prompts
🤖 6 dolphin3:latest replies
🤖 145 llama3.2:latest replies
🤖 63 gemma4:12b replies
🤖 82 nemotron-3-nano:30b-cloud replies
🤖 13 nemotron-3-ultra:cloud replies
🔥   3 🥵  13 😎  97 🥶 678 🧊  35

      $1 #827 advertise        100.00°C 🥳 1000‰ ~792 used:0   [791]  source:dolphin3        
      $2  #11 advertising       53.06°C 🔥  995‰ ~112 used:321 [111]  source:nemotron-3-nano 
      $3 #114 advertisement     51.85°C 🔥  994‰ ~110 used:226 [109]  source:nemotron-3-nano 
      $4 #616 promote           47.42°C 🔥  991‰   ~1 used:79  [0]    source:llama3.2        
      $5 #215 promotional       42.55°C 🥵  985‰ ~113 used:51  [112]  source:nemotron-3-nano 
      $6  #79 ad                41.86°C 🥵  984‰ ~111 used:24  [110]  source:nemotron-3-nano 
      $7 #748 endorse           41.81°C 🥵  983‰  ~20 used:11  [19]   source:llama3.2        
      $8 #124 buy               40.66°C 🥵  979‰  ~26 used:14  [25]   source:nemotron-3-ultra
      $9 #168 advertiser        39.42°C 🥵  973‰  ~27 used:14  [26]   source:nemotron-3-ultra
     $10  #12 branding          38.51°C 🥵  965‰  ~28 used:14  [27]   source:nemotron-3-nano 
     $11  #98 signage           37.52°C 🥵  962‰  ~29 used:14  [28]   source:nemotron-3-nano 
     $18  #37 print             33.06°C 😎  889‰  ~31 used:2   [30]   source:nemotron-3-nano 
    $115  #42 affiliate         23.19°C 🥶       ~114 used:0   [113]  source:nemotron-3-nano 
    $793  #64 journey           -0.16°C 🧊       ~793 used:0   [792]  source:nemotron-3-nano 
