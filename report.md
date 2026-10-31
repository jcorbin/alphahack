# 2026-11-01

- 🔗 spaceword.org 🧩 2026-10-31 🏁 score 2173 ranked 6.2% 17/275 ⏱️ 0:17:27.567518
- 🔗 wordgrid 🧩 #883 🟪 rarity:0.25 ⏱️ 1:15:27.235697
- 🔗 alfagok.diginaut.net 🧩 #729 🥳 28 ⏱️ 0:00:33.157480
- 🔗 alphaguess.com 🧩 #1196 🥳 38 ⏱️ 0:00:47.427713
- 🔗 dontwordle.com 🧩 #1622 🥳 6 ⏱️ 0:01:13.702761
- 🔗 dictionary.com hurdle 🧩 #1764 🥳 14 ⏱️ 0:02:31.465064
- 🔗 Quordle Classic 🧩 #1742 🥳 score:26 ⏱️ 0:01:54.835307
- 🔗 Octordle Classic 🧩 #1742 🥳 score:59 ⏱️ 0:01:59.489829
- 🔗 Sedecordle Classic 🧩 #1722 🥳 score:50 ⏱️ 0:02:47.567171
- 🔗 squareword.org 🧩 #1735 🥳 7 ⏱️ 0:01:52.053689
- 🔗 cemantle.certitudes.org 🧩 #1672 🥳 286 ⏱️ 0:18:01.343681
- 🔗 cemantix.certitudes.org 🧩 #1705 🥳 407 ⏱️ 0:02:54.557688

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
























# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 2026-10-27 🤔 rarity:nan ⏱️ 0:01:43.563056

📜 1 sessions
🌌 🌌 🦄
🌌 🌌 🌌
🦄 🦄 🦄





# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 2026-10-31 🤔 rarity:nan ⏱️ 1:15:11.193607

📜 2 sessions
🌌 🌌 🌌
🌌 🦄 🦄
🦄 🦄 🌌

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #883 🟪 rarity:0.25 ⏱️ 1:15:27.235697

📜 4 sessions
🌌 🌌 🌌
🌌 🦄 🦄
🦄 🦄 🌌
Rarity: 0.25 🟪

# [spaceword.org](spaceword.org) 🧩 2026-10-31 🏁 score 2173 ranked 6.2% 17/275 ⏱️ 0:17:27.567518

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 17/275

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ E _ S U A V I T Y   
      _ T _ U _ J _ S E A   
      _ A L E X I C _ _ H   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #729 🥳 28 ⏱️ 0:00:33.157480

🤔 28 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+2      [     2] -cijferig 
    @+199631 [199631] lijk      q0  ? ␅
    @+199631 [199631] lijk      q1  ? after
    @+249544 [249544] opi       q4  ? ␅
    @+249544 [249544] opi       q5  ? after
    @+274460 [274460] prop      q6  ? ␅
    @+274460 [274460] prop      q7  ? after
    @+275906 [275906] punt      q14 ? ␅
    @+275906 [275906] punt      q15 ? after
    @+276630 [276630] quiz      q16 ? ␅
    @+276630 [276630] quiz      q17 ? after
    @+276720 [276720] raad      q20 ? ␅
    @+276720 [276720] raad      q21 ? after
    @+276855 [276855] raaf      q22 ? ␅
    @+276855 [276855] raaf      q23 ? after
    @+276877 [276877] raak      q26 ? ␅
    @+276877 [276877] raak      q27 ? it
    @+276877 [276877] raak      done. it
    @+276899 [276899] raam      q24 ? ␅
    @+276899 [276899] raam      q25 ? before
    @+276991 [276991] raap      q18 ? ␅
    @+276991 [276991] raap      q19 ? before
    @+277364 [277364] radio     q12 ? ␅
    @+277364 [277364] radio     q13 ? before
    @+280558 [280558] red       q10 ? ␅
    @+280558 [280558] red       q11 ? before
    @+286974 [286974] riool     q8  ? ␅
    @+286974 [286974] riool     q9  ? before
    @+299528 [299528] schroot   q2  ? ␅
    @+299528 [299528] schroot   q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1196 🥳 38 ⏱️ 0:00:47.427713

🤔 38 attempts
📜 1 sessions

    @        [     0] aa         
    @+98139  [ 98139] mac        q0  ? ␅
    @+98139  [ 98139] mac        q1  ? after
    @+99563  [ 99563] mans       q12 ? ␅
    @+99563  [ 99563] mans       q13 ? after
    @+100168 [100168] mas        q14 ? ␅
    @+100168 [100168] mas        q15 ? after
    @+100398 [100398] mat        q16 ? ␅
    @+100398 [100398] mat        q17 ? after
    @+100553 [100553] matron     q20 ? ␅
    @+100553 [100553] matron     q21 ? after
    @+100570 [100570] matt       q24 ? ␅
    @+100570 [100570] matt       q25 ? after
    @+100586 [100586] mattocks   q28 ? ␅
    @+100586 [100586] mattocks   q29 ? after
    @+100590 [100590] mattrasses q32 ? ␅
    @+100590 [100590] mattrasses q33 ? after
    @+100591 [100591] mattress   q36 ? ␅
    @+100591 [100591] mattress   q37 ? it
    @+100591 [100591] mattress   done. it
    @+100592 [100592] mattresses q34 ? ␅
    @+100592 [100592] mattresses q35 ? before
    @+100594 [100594] maturate   q30 ? ␅
    @+100594 [100594] maturate   q31 ? before
    @+100601 [100601] mature     q26 ? ␅
    @+100601 [100601] mature     q27 ? before
    @+100631 [100631] maul       q22 ? ␅
    @+100631 [100631] maul       q23 ? before
    @+100708 [100708] maxim      q18 ? ␅
    @+100708 [100708] maxim      q19 ? before
    @+101034 [101034] media      q11 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1622 🥳 6 ⏱️ 0:01:13.702761

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:7042
    ⬜⬜⬜⬜⬜ tried:HOOCH n n n n n remain:3467
    ⬜⬜⬜⬜⬜ tried:DIVVY n n n n n remain:1075
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:304
    🟩⬜⬜⬜⬜ tried:AMASS Y n n n n remain:3
    🟩⬜⬜🟩⬜ tried:APEEK Y n n Y n remain:1

    Undos used: 2

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1764 🥳 14 ⏱️ 0:02:31.465064

📜 1 sessions
💰 score: 10200

    2/6
    SNARE 🟩🟩⬜⬜⬜
    SNOUT 🟩🟩🟩🟩🟩
    4/6
    SNOUT ⬜🟨⬜⬜⬜
    EYING ⬜🟩🟩🟩🟩
    AHOLD ⬜⬜⬜🟨⬜
    LYING 🟩🟩🟩🟩🟩
    4/6
    LYING ⬜⬜⬜🟨⬜
    ARSON ⬜⬜⬜⬜🟨
    TUNED 🟨🟨🟨🟩⬜
    UNMET 🟩🟩🟩🟩🟩
    3/6
    UNMET ⬜🟨⬜🟨⬜
    NOISE 🟨⬜🟨🟩🟩
    RINSE 🟩🟩🟩🟩🟩
    Final 1/2
    ALONG 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1742 🥳 score:26 ⏱️ 0:01:54.835307

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. DROVE attempts:5 score:5
2. PRIED attempts:8 score:8
3. SHELL attempts:9 score:9
4. BEGIN attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1742 🥳 score:59 ⏱️ 0:01:59.489829

📜 1 sessions

Octordle Classic

1. SEDAN attempts:11 score:11
2. GAUGE attempts:4 score:4
3. EGRET attempts:5 score:5
4. MUCKY attempts:8 score:8
5. OUTGO attempts:3 score:3
6. SNORT attempts:12 score:12
7. BROKE attempts:9 score:9
8. BAGEL attempts:7 score:7

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1722 🥳 score:50 ⏱️ 0:02:47.567171

📜 1 sessions

Sedecordle Classic sedecordle.com

1. SOLVE attempts:15 score:1
2. STAKE attempts:16 score:5
3. EPOXY attempts:9 score:0
4. AVIAN attempts:13 score:9
5. BLOAT attempts:16 score:1
6. STEER attempts:4 score:8
7. BRAKE attempts:11 score:1
8. MERGE attempts:14 score:1
9. CLOAK attempts:6 score:0
10. GLIDE attempts:5 score:6
11. MOODY attempts:16 score:1
12. PLEAT attempts:10 score:7
13. WOODY attempts:16 score:1
14. GUILE attempts:7 score:6
15. SHOUT attempts:12 score:1
16. TORCH attempts:8 score:2

# [squareword.org](squareword.org) 🧩 #1735 🥳 7 ⏱️ 0:01:52.053689

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S H R E W
    W E A V E
    I N D I E
    S N A C K
    H A R T S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1672 🥳 286 ⏱️ 0:18:01.343681

🤔 287 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 56 chat prompts
🤖 17 nemotron-3-nano:30b-cloud replies
🤖 39 gemma4:12b replies
🔥   2 🥵   5 😎  50 🥶 191 🧊  38

      $1 #287 enrol         100.00°C 🥳 1000‰ ~249 used:0  [248]  source:nemotron
      $2 #286 enlist         43.81°C 🔥  992‰   ~1 used:0  [0]    source:nemotron
      $3 #269 register       43.48°C 🔥  991‰   ~2 used:2  [1]    source:nemotron
      $4 #138 initiate       35.60°C 🥵  951‰  ~53 used:38 [52]   source:gemma4  
      $5 #136 implement      35.14°C 🥵  947‰  ~50 used:27 [49]   source:gemma4  
      $6 #126 administer     34.30°C 🥵  939‰  ~34 used:17 [33]   source:gemma4  
      $7 #252 introduce      34.04°C 🥵  937‰   ~3 used:4  [2]    source:nemotron
      $8 #232 submit         34.00°C 🥵  935‰   ~4 used:4  [3]    source:nemotron
      $9 #203 fulfill        29.95°C 😎  874‰  ~35 used:2  [34]   source:gemma4  
     $10 #216 prescribe      29.10°C 😎  853‰  ~36 used:2  [35]   source:gemma4  
     $11 #247 develop        28.96°C 😎  848‰   ~5 used:0  [4]    source:nemotron
     $12 #108 deploy         28.80°C 😎  846‰  ~51 used:3  [50]   source:gemma4  
     $59 #134 execute        19.59°C 🥶        ~64 used:0  [63]   source:gemma4  
    $250  #63 periodicity    -0.14°C 🧊       ~250 used:0  [249]  source:gemma4  

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1705 🥳 407 ⏱️ 0:02:54.557688

🤔 408 attempts
📜 1 sessions
🫧 11 chat sessions
⁉️ 53 chat prompts
🤖 53 nemotron-3-nano:30b-cloud replies
🥵  24 😎 101 🥶 209 🧊  73

      $1 #408 décret           100.00°C 🥳 1000‰ ~335 used:0  [334]  source:nemotron
      $2 #243 modalité          55.27°C 🥵  987‰ ~124 used:22 [123]  source:nemotron
      $3  #86 disposition       51.49°C 🥵  983‰ ~125 used:34 [124]  source:nemotron
      $4 #207 règlement         50.25°C 🥵  981‰ ~121 used:12 [120]  source:nemotron
      $5  #19 obligation        49.76°C 🥵  980‰ ~122 used:18 [121]  source:nemotron
      $6 #214 article           47.86°C 🥵  974‰   ~8 used:4  [7]    source:nemotron
      $7  #97 dérogation        47.83°C 🥵  973‰  ~20 used:7  [19]   source:nemotron
      $8  #54 application       47.57°C 🥵  972‰  ~19 used:6  [18]   source:nemotron
      $9 #381 statut            47.25°C 🥵  968‰   ~5 used:3  [4]    source:nemotron
     $10 #185 réglementaire     47.17°C 🥵  967‰   ~9 used:4  [8]    source:nemotron
     $11 #407 directive         46.64°C 🥵  964‰   ~1 used:0  [0]    source:nemotron
     $26 #120 approbation       36.93°C 😎  894‰  ~21 used:0  [20]   source:nemotron
    $127 #165 caractère         21.70°C 🥶       ~126 used:0  [125]  source:nemotron
    $336 #103 accommodation     -0.43°C 🧊       ~336 used:0  [335]  source:nemotron
