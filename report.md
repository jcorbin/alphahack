# 2026-03-31

- 🔗 spaceword.org 🧩 2026-03-30 🏁 score 2168 ranked 51.2% 172/336 ⏱️ 0:15:03.388904
- 🔗 alfagok.diginaut.net 🧩 #514 🥳 22 ⏱️ 0:00:37.608263
- 🔗 alphaguess.com 🧩 #981 🥳 32 ⏱️ 0:00:38.367651
- 🔗 dontwordle.com 🧩 #1407 🥳 6 ⏱️ 0:01:46.009150
- 🔗 dictionary.com hurdle 🧩 #1550 🥳 16 ⏱️ 0:02:50.408590
- 🔗 Quordle Classic 🧩 #1527 🥳 score:26 ⏱️ 0:01:45.777110
- 🔗 Octordle Classic 🧩 #1527 🥳 score:75 ⏱️ 0:03:53.994269
- 🔗 squareword.org 🧩 #1520 🥳 8 ⏱️ 0:02:12.743793
- 🔗 cemantle.certitudes.org 🧩 #1457 🥳 131 ⏱️ 0:05:35.730892
- 🔗 cemantix.certitudes.org 🧩 #1490 🥳 87 ⏱️ 0:04:41.149916

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






























# [spaceword.org](spaceword.org) 🧩 2026-03-30 🏁 score 2168 ranked 51.2% 172/336 ⏱️ 0:15:03.388904

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 172/336

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ J _ Y _ _ M _ H _   
      _ U _ E _ _ A _ E _   
      _ S N O O Z E _ R _   
      _ _ _ W E A S O N _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #514 🥳 22 ⏱️ 0:00:37.608263

🤔 22 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+99737  [ 99737] ex        q4  ? ␅
    @+99737  [ 99737] ex        q5  ? after
    @+149431 [149431] huis      q6  ? ␅
    @+149431 [149431] huis      q7  ? after
    @+161986 [161986] izabel    q10 ? ␅
    @+161986 [161986] izabel    q11 ? after
    @+168255 [168255] kano      q12 ? ␅
    @+168255 [168255] kano      q13 ? after
    @+171282 [171282] kennis    q14 ? ␅
    @+171282 [171282] kennis    q15 ? after
    @+171709 [171709] kerk      q18 ? ␅
    @+171709 [171709] kerk      q19 ? after
    @+172207 [172207] kern      q20 ? ␅
    @+172207 [172207] kern      q21 ? it
    @+172207 [172207] kern      done. it
    @+172909 [172909] kervel    q16 ? ␅
    @+172909 [172909] kervel    q17 ? before
    @+174538 [174538] kind      q8  ? ␅
    @+174538 [174538] kind      q9  ? before
    @+199809 [199809] lijm      q0  ? ␅
    @+199809 [199809] lijm      q1  ? 1
    @+199809 [199809] lijm      q2  ? ␅
    @+199809 [199809] lijm      q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #981 🥳 32 ⏱️ 0:00:38.367651

🤔 32 attempts
📜 1 sessions

    @        [     0] aa     
    @+98216  [ 98216] mach   q0  ? ␅
    @+98216  [ 98216] mach   q1  ? after
    @+147371 [147371] rhumb  q2  ? ␅
    @+147371 [147371] rhumb  q3  ? after
    @+171636 [171636] ta     q4  ? ␅
    @+171636 [171636] ta     q5  ? after
    @+182000 [182000] un     q6  ? ␅
    @+182000 [182000] un     q7  ? after
    @+189262 [189262] vicar  q8  ? ␅
    @+189262 [189262] vicar  q9  ? after
    @+192866 [192866] whir   q10 ? ␅
    @+192866 [192866] whir   q11 ? after
    @+193482 [193482] win    q14 ? ␅
    @+193482 [193482] win    q15 ? after
    @+193737 [193737] winter q18 ? ␅
    @+193737 [193737] winter q19 ? after
    @+193795 [193795] wire   q22 ? ␅
    @+193795 [193795] wire   q23 ? after
    @+193844 [193844] wirra  q24 ? ␅
    @+193844 [193844] wirra  q25 ? after
    @+193849 [193849] wise   q26 ? ␅
    @+193849 [193849] wise   q27 ? after
    @+193871 [193871] wisent q28 ? ␅
    @+193871 [193871] wisent q29 ? after
    @+193878 [193878] wish   q30 ? ␅
    @+193878 [193878] wish   q31 ? it
    @+193878 [193878] wish   done. it
    @+193893 [193893] wisp   q20 ? ␅
    @+193893 [193893] wisp   q21 ? before
    @+194062 [194062] wo     q17 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1407 🥳 6 ⏱️ 0:01:46.009150

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:BUBUS n n n n n remain:4942
    ⬜⬜⬜⬜⬜ tried:WHIZZ n n n n n remain:2312
    ⬜⬜⬜⬜⬜ tried:POOPY n n n n n remain:770
    ⬜⬜⬜🟩⬜ tried:CEDED n n n Y n remain:62
    🟨⬜⬜🟩⬜ tried:ANNEX m n n Y n remain:34
    ⬜🟩🟩🟩🟩 tried:GAGER n Y Y Y Y remain:3

    Undos used: 2

      3 words remaining
    x 8 unused letters
    = 24 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1550 🥳 16 ⏱️ 0:02:50.408590

📜 1 sessions
💰 score: 10000

    4/6
    RATES ⬜🟩⬜⬜⬜
    LAWNY ⬜🟩⬜🟨⬜
    CAPON 🟨🟩⬜🟩🟩
    BACON 🟩🟩🟩🟩🟩
    3/6
    BACON ⬜⬜🟨🟨🟩
    COVIN 🟩🟩🟩⬜🟩
    COVEN 🟩🟩🟩🟩🟩
    4/6
    COVEN ⬜⬜⬜🟨🟨
    ENTIA 🟨🟨⬜⬜⬜
    RENDS ⬜🟨🟨🟨⬜
    NUDGE 🟩🟩🟩🟩🟩
    4/6
    NUDGE ⬜⬜🟨⬜⬜
    AROID 🟨⬜⬜🟨🟨
    DAISY 🟩🟩🟩⬜🟩
    DAILY 🟩🟩🟩🟩🟩
    Final 1/2
    KNEED 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1527 🥳 score:26 ⏱️ 0:01:45.777110

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. SMACK attempts:5 score:5
2. HAPPY attempts:8 score:8
3. LYING attempts:6 score:6
4. PULPY attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1527 🥳 score:75 ⏱️ 0:03:53.994269

📜 1 sessions

Octordle Classic

1. BLACK attempts:7 score:7
2. CHUMP attempts:8 score:8
3. JUMPY attempts:9 score:9
4. FLOAT attempts:10 score:10
5. ILIAC attempts:11 score:11
6. BIDDY attempts:5 score:5
7. HEART attempts:12 score:12
8. GIVER attempts:13 score:13

# [squareword.org](squareword.org) 🧩 #1520 🥳 8 ⏱️ 0:02:12.743793

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T A F F
    T O N E R
    E X I L E
    A I S L E
    K N E A D

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1457 🥳 131 ⏱️ 0:05:35.730892

🤔 132 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 44 chat prompts
🤖 11 gemma3:27b replies
🤖 33 dolphin3:latest replies
🔥   1 🥵   5 😎  13 🥶 106 🧊   6

      $1 #132 accumulate       100.00°C 🥳 1000‰ ~126 used:0  [125]  source:gemma3  
      $2  #77 multiply          46.35°C 🔥  991‰   ~2 used:35 [1]    source:dolphin3
      $3 #125 proliferate       40.04°C 🥵  977‰   ~5 used:8  [4]    source:dolphin3
      $4  #68 grow              38.09°C 🥵  957‰   ~6 used:10 [5]    source:dolphin3
      $5 #124 inflate           36.25°C 🥵  930‰   ~4 used:7  [3]    source:dolphin3
      $6 #131 calculate         35.48°C 🥵  919‰   ~1 used:1  [0]    source:gemma3  
      $7  #72 magnify           35.03°C 🥵  914‰   ~3 used:5  [2]    source:dolphin3
      $8  #75 develop           33.03°C 😎  872‰   ~7 used:0  [6]    source:dolphin3
      $9  #89 propagate         32.27°C 😎  849‰   ~8 used:0  [7]    source:dolphin3
     $10  #86 evolve            31.76°C 😎  833‰   ~9 used:0  [8]    source:dolphin3
     $11  #79 reproduce         30.77°C 😎  794‰  ~10 used:0  [9]    source:dolphin3
     $12 #122 burgeon           29.30°C 😎  728‰  ~11 used:0  [10]   source:dolphin3
     $21  #70 intensify         23.08°C 🥶        ~25 used:0  [24]   source:dolphin3
    $127  #44 field             -0.26°C 🧊       ~127 used:0  [126]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1490 🥳 87 ⏱️ 0:04:41.149916

🤔 88 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 16 chat prompts
🤖 16 dolphin3:latest replies
🔥  3 🥵  7 😎 19 🥶 56 🧊  2

     $1 #88 magnifique      100.00°C 🥳 1000‰ ~86 used:0  [85]  source:dolphin3
     $2 #82 beau             80.97°C 🔥  997‰  ~1 used:2  [0]   source:dolphin3
     $3 #76 merveilleux      68.87°C 🔥  994‰  ~3 used:4  [2]   source:dolphin3
     $4 #81 fabuleux         66.24°C 🔥  991‰  ~2 used:3  [1]   source:dolphin3
     $5 #57 merveille        58.29°C 🥵  985‰ ~10 used:3  [9]   source:dolphin3
     $6 #83 charmant         56.75°C 🥵  984‰  ~4 used:0  [3]   source:dolphin3
     $7 #86 impressionnant   55.42°C 🥵  982‰  ~5 used:0  [4]   source:dolphin3
     $8 #75 incroyable       51.94°C 🥵  974‰  ~6 used:0  [5]   source:dolphin3
     $9 #80 admirable        48.61°C 🥵  957‰  ~7 used:0  [6]   source:dolphin3
    $10 #68 magique          48.25°C 🥵  956‰  ~8 used:0  [7]   source:dolphin3
    $11 #78 extraordinaire   46.89°C 🥵  943‰  ~9 used:0  [8]   source:dolphin3
    $12 #87 magnificence     41.93°C 😎  895‰ ~11 used:0  [10]  source:dolphin3
    $31 #28 couchant         27.93°C 🥶       ~30 used:0  [29]  source:dolphin3
    $87 #46 satellite        -7.28°C 🧊       ~87 used:0  [86]  source:dolphin3
