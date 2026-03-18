# 2026-03-19

- 🔗 spaceword.org 🧩 2026-03-18 🏁 score 2173 ranked 8.3% 28/338 ⏱️ 0:30:03.282756
- 🔗 alfagok.diginaut.net 🧩 #502 🥳 20 ⏱️ 0:00:32.175232
- 🔗 alphaguess.com 🧩 #969 🥳 26 ⏱️ 0:00:29.479887
- 🔗 dontwordle.com 🧩 #1395 🥳 6 ⏱️ 0:01:42.926808
- 🔗 dictionary.com hurdle 🧩 #1538 🥳 19 ⏱️ 0:02:39.734804
- 🔗 Quordle Classic 🧩 #1515 😦 score:29 ⏱️ 0:02:01.479836
- 🔗 Octordle Classic 🧩 #1515 🥳 score:59 ⏱️ 0:03:28.720225
- 🔗 squareword.org 🧩 #1508 🥳 7 ⏱️ 0:02:23.992819
- 🔗 cemantle.certitudes.org 🧩 #1445 🥳 165 ⏱️ 0:01:53.463860
- 🔗 cemantix.certitudes.org 🧩 #1478 🥳 43 ⏱️ 0:06:13.803805

# Dev

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


















# [spaceword.org](spaceword.org) 🧩 2026-03-18 🏁 score 2173 ranked 8.3% 28/338 ⏱️ 0:30:03.282756

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 28/338

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ R E I _ _ _   
      _ _ _ _ _ X _ _ _ _   
      _ _ _ _ J U N _ _ _   
      _ _ _ _ _ D O _ _ _   
      _ _ _ _ G A M _ _ _   
      _ _ _ _ _ T I _ _ _   
      _ _ _ _ H E N _ _ _   
      _ _ _ _ _ _ E _ _ _   
      _ _ _ _ V O E _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #502 🥳 20 ⏱️ 0:00:32.175232

🤔 20 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+1      [     1] &-tekens    
    @+2      [     2] -cijferig   
    @+3      [     3] -e-mail     
    @+199609 [199609] lij         q0  ? ␅
    @+199609 [199609] lij         q1  ? after
    @+247696 [247696] op          q4  ? ␅
    @+247696 [247696] op          q5  ? after
    @+273501 [273501] proef       q6  ? ␅
    @+273501 [273501] proef       q7  ? after
    @+276630 [276630] quarantaine q12 ? ␅
    @+276630 [276630] quarantaine q13 ? after
    @+277313 [277313] rad         q16 ? ␅
    @+277313 [277313] rad         q17 ? after
    @+277499 [277499] radio       q18 ? ␅
    @+277499 [277499] radio       q19 ? it
    @+277499 [277499] radio       done. it
    @+278111 [278111] ram         q14 ? ␅
    @+278111 [278111] ram         q15 ? before
    @+279767 [279767] rechts      q10 ? ␅
    @+279767 [279767] rechts      q11 ? before
    @+286485 [286485] rijns       q8  ? ␅
    @+286485 [286485] rijns       q9  ? before
    @+299483 [299483] schro       q2  ? ␅
    @+299483 [299483] schro       q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #969 🥳 26 ⏱️ 0:00:29.479887

🤔 26 attempts
📜 1 sessions

    @        [     0] aa     
    @+1      [     1] aah    
    @+2      [     2] aahed  
    @+3      [     3] aahing 
    @+98217  [ 98217] mach   q0  ? ␅
    @+98217  [ 98217] mach   q1  ? after
    @+147372 [147372] rhumb  q2  ? ␅
    @+147372 [147372] rhumb  q3  ? after
    @+147693 [147693] right  q16 ? ␅
    @+147693 [147693] right  q17 ? after
    @+147822 [147822] rin    q18 ? ␅
    @+147822 [147822] rin    q19 ? after
    @+147831 [147831] ring   q24 ? ␅
    @+147831 [147831] ring   q25 ? it
    @+147831 [147831] ring   done. it
    @+147866 [147866] rings  q22 ? ␅
    @+147866 [147866] rings  q23 ? before
    @+147916 [147916] rip    q20 ? ␅
    @+147916 [147916] rip    q21 ? before
    @+148078 [148078] river  q14 ? ␅
    @+148078 [148078] river  q15 ? before
    @+148804 [148804] rot    q12 ? ␅
    @+148804 [148804] rot    q13 ? before
    @+150338 [150338] sallow q10 ? ␅
    @+150338 [150338] sallow q11 ? before
    @+153316 [153316] sea    q8  ? ␅
    @+153316 [153316] sea    q9  ? before
    @+159484 [159484] slop   q6  ? ␅
    @+159484 [159484] slop   q7  ? before
    @+171637 [171637] ta     q4  ? ␅
    @+171637 [171637] ta     q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1395 🥳 6 ⏱️ 0:01:42.926808

📜 1 sessions
💰 score: 10

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:POTTO n n n n n remain:5809
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:2803
    ⬜⬜⬜⬜⬜ tried:YUMMY n n n n n remain:1182
    ⬜⬜⬜⬜🟩 tried:GRRRL n n n n Y remain:44
    🟨⬜⬜⬜🟩 tried:ANNAL m n n n Y remain:7
    🟨⬜🟨⬜🟩 tried:SCALL m n m n Y remain:1

    Undos used: 2

      1 words remaining
    x 10 unused letters
    = 10 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1538 🥳 19 ⏱️ 0:02:39.734804

📜 1 sessions
💰 score: 9700

    4/6
    TAELS ⬜⬜🟩🟨⬜
    BLECH 🟨🟩🟩⬜⬜
    GLEBE ⬜🟩🟩🟩🟩
    PLEBE 🟩🟩🟩🟩🟩
    5/6
    PLEBE ⬜⬜⬜🟨🟩
    OMBRE ⬜⬜🟨⬜🟩
    BINGE 🟩⬜⬜🟩🟩
    BADGE 🟩⬜🟩🟩🟩
    BUDGE 🟩🟩🟩🟩🟩
    3/6
    BUDGE 🟨⬜🟨⬜🟨
    REBID ⬜🟨🟨⬜🟨
    DWEEB 🟩🟩🟩🟩🟩
    5/6
    DWEEB ⬜⬜⬜⬜⬜
    ARILS 🟨⬜⬜⬜⬜
    CONGA ⬜⬜🟩⬜🟩
    JUNTA ⬜⬜🟩🟩🟩
    MANTA 🟩🟩🟩🟩🟩
    Final 2/2
    FIRST ⬜🟨🟨🟨🟩
    SHIRT 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1515 😦 score:29 ⏱️ 0:02:01.479836

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. DIRGE attempts:4 score:4
2. VERVE attempts:9 score:9
3. _AKER -BDFGILNOPSTVZ E:1 attempts:9 score:-1
4. FROZE attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1515 🥳 score:59 ⏱️ 0:03:28.720225

📜 1 sessions

Octordle Classic

1. PRUNE attempts:3 score:3
2. SOUND attempts:8 score:8
3. OUTGO attempts:10 score:10
4. KNEEL attempts:11 score:11
5. BREAD attempts:9 score:9
6. SHAME attempts:7 score:7
7. MOUTH attempts:6 score:6
8. SHINE attempts:5 score:5

# [squareword.org](squareword.org) 🧩 #1508 🥳 7 ⏱️ 0:02:23.992819

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    W A T T S
    A S H E N
    S C O R E
    P O S S E
    S T E E R

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1445 🥳 165 ⏱️ 0:01:53.463860

🤔 166 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 42 chat prompts
🤖 42 dolphin3:latest replies
🔥   2 🥵   2 😎  32 🥶 125 🧊   4

      $1 #166 senator         100.00°C 🥳 1000‰ ~162 used:0  [161]  source:dolphin3
      $2 #165 lawmaker         67.40°C 🔥  998‰   ~1 used:0  [0]    source:dolphin3
      $3 #164 governor         59.47°C 🔥  996‰   ~2 used:0  [1]    source:dolphin3
      $4  #30 jurist           38.94°C 🥵  962‰  ~33 used:37 [32]   source:dolphin3
      $5 #124 prosecutor       32.96°C 🥵  910‰  ~18 used:11 [17]   source:dolphin3
      $6 #134 state            32.10°C 😎  891‰  ~19 used:2  [18]   source:dolphin3
      $7  #20 attorney         31.71°C 😎  883‰  ~36 used:19 [35]   source:dolphin3
      $8 #163 government       31.12°C 😎  876‰   ~3 used:0  [2]    source:dolphin3
      $9  #83 secretary        30.59°C 😎  864‰  ~35 used:7  [34]   source:dolphin3
     $10  #19 lawyer           30.42°C 😎  860‰  ~34 used:5  [33]   source:dolphin3
     $11  #16 law              27.85°C 😎  785‰  ~20 used:2  [19]   source:dolphin3
     $12  #14 judge            27.60°C 😎  770‰  ~21 used:2  [20]   source:dolphin3
     $38  #72 student          20.67°C 🥶        ~37 used:0  [36]   source:dolphin3
    $163   #1 algorithm        -0.03°C 🧊       ~163 used:0  [162]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1478 🥳 43 ⏱️ 0:06:13.803805

🤔 44 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 11 chat prompts
🤖 11 dolphin3:latest replies
🥵  4 😎 12 🥶 22 🧊  5

     $1 #44 nourriture     100.00°C 🥳 1000‰ ~39 used:0 [38]  source:dolphin3
     $2 #35 alimentation    44.11°C 🥵  976‰  ~3 used:5 [2]   source:dolphin3
     $3 #37 alimentaire     43.39°C 🥵  973‰  ~1 used:2 [0]   source:dolphin3
     $4 #18 animal          41.89°C 🥵  963‰  ~4 used:7 [3]   source:dolphin3
     $5 #27 omnivore        41.42°C 🥵  957‰  ~2 used:3 [1]   source:dolphin3
     $6 #25 herbivore       33.34°C 😎  828‰  ~5 used:0 [4]   source:dolphin3
     $7 #20 carnivore       33.28°C 😎  826‰  ~6 used:1 [5]   source:dolphin3
     $8 #15 chiens          32.70°C 😎  807‰ ~16 used:2 [15]  source:dolphin3
     $9 #42 digestion       32.47°C 😎  789‰  ~7 used:0 [6]   source:dolphin3
    $10 #39 comestible      32.01°C 😎  765‰  ~8 used:0 [7]   source:dolphin3
    $11 #32 oiseau          30.38°C 😎  687‰  ~9 used:0 [8]   source:dolphin3
    $12 #12 chien           29.87°C 😎  656‰ ~10 used:0 [9]   source:dolphin3
    $18 #33 reptile         22.68°C 🥶       ~17 used:0 [16]  source:dolphin3
    $40 #13 medium          -0.45°C 🧊       ~40 used:0 [39]  source:dolphin3
