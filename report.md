# 2026-09-26

- 🔗 spaceword.org 🧩 2026-09-25 🏁 score 2168 ranked 35.7% 121/339 ⏱️ 1:35:43.088066
- 🔗 wordgrid 🧩 #847 🟪 rarity:0.25 ⏱️ 0:03:02.222830
- 🔗 alfagok.diginaut.net 🧩 #693 🥳 52 ⏱️ 0:01:17.280824
- 🔗 alphaguess.com 🧩 #1160 🥳 32 ⏱️ 0:00:43.775535
- 🔗 dontwordle.com 🧩 #1586 🥳 6 ⏱️ 0:01:52.176190
- 🔗 dictionary.com hurdle 🧩 #1729 🥳 16 ⏱️ 0:03:25.553513
- 🔗 Quordle Classic 🧩 #1706 🥳 score:24 ⏱️ 0:01:47.672478
- 🔗 Octordle Classic 🧩 #1706 🥳 score:55 ⏱️ 0:02:10.617335
- 🔗 Sedecordle Classic 🧩 #1686 🥳 score:52 ⏱️ 0:06:00.082441
- 🔗 squareword.org 🧩 #1699 🥳 8 ⏱️ 0:02:52.817629
- 🔗 cemantle.certitudes.org 🧩 #1636 🥳 100 ⏱️ 0:01:44.397729
- 🔗 cemantix.certitudes.org 🧩 #1669 🥳 168 ⏱️ 0:03:19.010190

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






# [spaceword.org](spaceword.org) 🧩 2026-09-25 🏁 score 2168 ranked 35.7% 121/339 ⏱️ 1:35:43.088066

📜 5 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 121/339

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ A Q U A _ _ _   
      _ _ _ _ _ _ I _ _ _   
      _ _ _ _ T W O _ _ _   
      _ _ _ P O O L _ _ _   
      _ _ _ _ K _ I _ _ _   
      _ _ _ R I F _ _ _ _   
      _ _ _ _ N _ _ _ _ _   
      _ _ _ _ G O T _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #847 🟪 rarity:0.25 ⏱️ 0:03:02.222830

📜 2 sessions
🦄 🦄 🌌
🌌 🌌 🌌
🌌 🌌 🌌
Rarity: 0.25 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #693 🥳 52 ⏱️ 0:01:17.280824

🤔 52 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+199531 [199531] lij          q0  ? ␅
    @+199531 [199531] lij          q1  ? after
    @+199531 [199531] lij          q2  ? ␅
    @+199531 [199531] lij          q3  ? after
    @+223517 [223517] molen        q16 ? ␅
    @+223517 [223517] molen        q17 ? after
    @+226502 [226502] mus          q26 ? ␅
    @+226502 [226502] mus          q27 ? after
    @+227608 [227608] na           q28 ? ␅
    @+227608 [227608] na           q29 ? after
    @+228048 [228048] nacht        q34 ? ␅
    @+228048 [228048] nacht        q35 ? after
    @+228048 [228048] nacht        q36 ? ␅
    @+228048 [228048] nacht        q37 ? after
    @+228048 [228048] nacht        q38 ? ␅
    @+228048 [228048] nacht        q39 ? after
    @+228287 [228287] nachtvlinder q40 ? ␅
    @+228287 [228287] nachtvlinder q41 ? after
    @+228342 [228342] nada         q44 ? ␅
    @+228342 [228342] nada         q45 ? after
    @+228371 [228371] naden        q46 ? ␅
    @+228371 [228371] naden        q47 ? after
    @+228373 [228373] nadenken     q50 ? ␅
    @+228373 [228373] nadenken     q51 ? it
    @+228373 [228373] nadenken     done. it
    @+228378 [228378] nader        q48 ? ␅
    @+228378 [228378] nader        q49 ? before
    @+228406 [228406] nadoe        q42 ? ␅
    @+228406 [228406] nadoe        q43 ? before
    @+228525 [228525] nagel        q33 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1160 🥳 32 ⏱️ 0:00:43.775535

🤔 32 attempts
📜 1 sessions

    @       [    0] aa            
    @+5876  [ 5876] angel         q8  ? ␅
    @+5876  [ 5876] angel         q9  ? after
    @+8323  [ 8323] ar            q10 ? ␅
    @+8323  [ 8323] ar            q11 ? after
    @+9341  [ 9341] as            q12 ? ␅
    @+9341  [ 9341] as            q13 ? after
    @+9460  [ 9460] ash           q20 ? ␅
    @+9460  [ 9460] ash           q21 ? after
    @+9494  [ 9494] ashram        q24 ? ␅
    @+9494  [ 9494] ashram        q25 ? after
    @+9511  [ 9511] ask           q26 ? ␅
    @+9511  [ 9511] ask           q27 ? after
    @+9516  [ 9516] asked         q30 ? ␅
    @+9516  [ 9516] asked         q31 ? it
    @+9516  [ 9516] asked         done. it
    @+9521  [ 9521] askew         q28 ? ␅
    @+9521  [ 9521] askew         q29 ? before
    @+9535  [ 9535] asp           q22 ? ␅
    @+9535  [ 9535] asp           q23 ? before
    @+9644  [ 9644] ass           q18 ? ␅
    @+9644  [ 9644] ass           q19 ? before
    @+9947  [ 9947] asthenosphere q16 ? ␅
    @+9947  [ 9947] asthenosphere q17 ? before
    @+10552 [10552] audiences     q14 ? ␅
    @+10552 [10552] audiences     q15 ? before
    @+11763 [11763] back          q6  ? ␅
    @+11763 [11763] back          q7  ? before
    @+23680 [23680] camp          q4  ? ␅
    @+23680 [23680] camp          q5  ? before
    @+47374 [47374] dis           q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1586 🥳 6 ⏱️ 0:01:52.176190

📜 1 sessions
💰 score: 35

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:JUJUS n n n n n remain:5557
    ⬜⬜⬜⬜⬜ tried:FEOFF n n n n n remain:1344
    ⬜⬜⬜⬜⬜ tried:PHIZZ n n n n n remain:370
    ⬜⬜🟩⬜⬜ tried:GRRRL n n Y n n remain:34
    ⬜🟩🟩⬜⬜ tried:BARCA n Y m n n remain:8
    ⬜🟩🟩⬜🟩 tried:MARVY n Y Y n Y remain:5

    Undos used: 3

      5 words remaining
    x 7 unused letters
    = 35 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1729 🥳 16 ⏱️ 0:03:25.553513

📜 1 sessions
💰 score: 10000

    2/6
    OSIER 🟩⬜🟩⬜⬜
    OPIUM 🟩🟩🟩🟩🟩
    5/6
    OPIUM ⬜⬜⬜🟨⬜
    URGES 🟨⬜⬜⬜🟨
    SAUCY 🟩⬜🟩🟩⬜
    CHANT 🟨⬜⬜⬜🟨
    STUCK 🟩🟩🟩🟩🟩
    4/6
    STUCK 🟨⬜⬜⬜⬜
    NARES 🟨⬜⬜🟨🟨
    CHILD ⬜⬜⬜⬜🟨
    DENSE 🟩🟩🟩🟩🟩
    3/6
    DENSE ⬜⬜🟨⬜⬜
    INGOT 🟩🟩⬜⬜🟩
    INPUT 🟩🟩🟩🟩🟩
    Final 2/2
    AWFUL ⬜⬜⬜⬜⬜
    BOOST 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1706 🥳 score:24 ⏱️ 0:01:47.672478

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SNORT attempts:7 score:7
2. BIBLE attempts:5 score:5
3. LAPSE attempts:4 score:4
4. CRANE attempts:8 score:8

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1706 🥳 score:55 ⏱️ 0:02:10.617335

📜 1 sessions

Octordle Classic

1. OVERT attempts:4 score:4
2. ABATE attempts:12 score:12
3. IONIC attempts:8 score:8
4. QUERY attempts:3 score:3
5. TREAT attempts:10 score:10
6. UNTIL attempts:5 score:5
7. EXERT attempts:6 score:6
8. MOTEL attempts:7 score:7

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1686 🥳 score:52 ⏱️ 0:06:00.082441

📜 2 sessions

Sedecordle Classic sedecordle.com

1. STAVE attempts:17 score:1
2. OUTGO attempts:16 score:7
3. NERDY attempts:15 score:1
4. WHOLE attempts:13 score:5
5. BUXOM attempts:7 score:0
6. SATIN attempts:3 score:7
7. BACON attempts:8 score:0
8. TAWNY attempts:14 score:8
9. HEADY attempts:17 score:1
10. UTILE attempts:6 score:8
11. SMITE attempts:9 score:0
12. SLICK attempts:5 score:9
13. SPOIL attempts:4 score:0
14. SMOTE attempts:17 score:4
15. HUMOR attempts:10 score:1
16. DITTY attempts:12 score:0

# [squareword.org](squareword.org) 🧩 #1699 🥳 8 ⏱️ 0:02:52.817629

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟩 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    G H A T S
    A U D I T
    S M O K E
    P A R K A
    S N E A K

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1636 🥳 100 ⏱️ 0:01:44.397729

🤔 101 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 14 chat prompts
🤖 14 gemma4:12b replies
😱  1 🥵  5 😎 13 🥶 75 🧊  6

      $1 #101 setup            100.00°C 🥳 1000‰  ~95 used:0 [94]   source:gemma4
      $2  #89 configuration     51.33°C 😱  999‰   ~1 used:2 [0]    source:gemma4
      $3  #76 calibration       35.61°C 🥵  986‰   ~6 used:3 [5]    source:gemma4
      $4  #98 initialization    35.04°C 🥵  982‰   ~2 used:0 [1]    source:gemma4
      $5  #96 arrangement       33.30°C 🥵  975‰   ~3 used:0 [2]    source:gemma4
      $6  #94 tuning            33.09°C 🥵  972‰   ~4 used:0 [3]    source:gemma4
      $7  #75 alignment         29.22°C 🥵  918‰   ~5 used:1 [4]    source:gemma4
      $8  #87 adjustment        28.27°C 😎  882‰   ~7 used:0 [6]    source:gemma4
      $9  #54 tweak             27.81°C 😎  862‰  ~16 used:4 [15]   source:gemma4
     $10  #97 design            27.03°C 😎  810‰   ~8 used:0 [7]    source:gemma4
     $11  #93 synchronization   26.33°C 😎  758‰   ~9 used:0 [8]    source:gemma4
     $12 #100 parameter         24.01°C 😎  515‰  ~10 used:0 [9]    source:gemma4
     $21  #19 inconsistency     19.02°C 🥶        ~20 used:0 [19]   source:gemma4
     $96  #49 jar               -0.71°C 🧊        ~96 used:0 [95]   source:gemma4

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1669 🥳 168 ⏱️ 0:03:19.010190

🤔 169 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 29 chat prompts
🤖 29 gemma4:12b replies
🔥  5 🥵 20 😎 58 🥶 72 🧊 13

      $1 #169 pénal           100.00°C 🥳 1000‰ ~156 used:0  [155]  source:gemma4
      $2 #130 juridique        50.82°C 🔥  997‰   ~5 used:8  [4]    source:gemma4
      $3 #136 justice          50.65°C 🔥  996‰   ~4 used:6  [3]    source:gemma4
      $4 #103 sanction         49.71°C 🔥  994‰   ~3 used:5  [2]    source:gemma4
      $5 #109 délit            48.49°C 🔥  991‰   ~2 used:4  [1]    source:gemma4
      $6 #111 infraction       48.39°C 🔥  990‰   ~1 used:3  [0]    source:gemma4
      $7 #161 délictuel        46.42°C 🥵  984‰   ~6 used:0  [5]    source:gemma4
      $8 #131 jurisprudence    46.23°C 🥵  983‰   ~7 used:0  [6]    source:gemma4
      $9 #112 juge             46.11°C 🥵  982‰   ~8 used:0  [7]    source:gemma4
     $10 #166 magistrat        45.89°C 🥵  981‰   ~9 used:0  [8]    source:gemma4
     $11 #133 droit            44.55°C 🥵  978‰  ~10 used:0  [9]    source:gemma4
     $27  #81 autorité         33.30°C 😎  898‰  ~25 used:0  [24]   source:gemma4
     $85 #148 gravité          19.88°C 🥶        ~86 used:0  [85]   source:gemma4
    $157   #1 brouillon        -2.26°C 🧊       ~157 used:1  [156]  source:gemma4
