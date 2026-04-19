# 2026-04-20

- 🔗 spaceword.org 🧩 2026-04-19 🏁 score 2173 ranked 5.0% 16/320 ⏱️ 2:25:07.929206
- 🔗 alfagok.diginaut.net 🧩 #534 🥳 32 ⏱️ 0:00:48.592021
- 🔗 alphaguess.com 🧩 #1001 🥳 32 ⏱️ 0:00:40.927140
- 🔗 dontwordle.com 🧩 #1427 🥳 6 ⏱️ 0:01:28.595483
- 🔗 dictionary.com hurdle 🧩 #1570 😦 17 ⏱️ 0:03:42.153337
- 🔗 Quordle Classic 🧩 #1547 🥳 score:25 ⏱️ 0:02:13.768990
- 🔗 Octordle Classic 🧩 #1547 🥳 score:60 ⏱️ 0:03:39.360755
- 🔗 squareword.org 🧩 #1540 🥳 7 ⏱️ 0:02:32.468561
- 🔗 cemantle.certitudes.org 🧩 #1477 🥳 193 ⏱️ 0:01:54.653526
- 🔗 cemantix.certitudes.org 🧩 #1510 🥳 145 ⏱️ 0:02:19.801649

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


















































# [spaceword.org](spaceword.org) 🧩 2026-04-19 🏁 score 2173 ranked 5.0% 16/320 ⏱️ 2:25:07.929206

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 16/320

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ S U K _ _ _   
      _ _ _ _ _ _ E _ _ _   
      _ _ _ _ F O R _ _ _   
      _ _ _ _ _ P A _ _ _   
      _ _ _ _ B A T _ _ _   
      _ _ _ _ _ Q I _ _ _   
      _ _ _ _ J U N _ _ _   
      _ _ _ _ _ E _ _ _ _   
      _ _ _ _ O D E _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #534 🥳 32 ⏱️ 0:00:48.592021

🤔 32 attempts
📜 1 sessions

    @        [     0] &-teken       
    @+199605 [199605] lij           q0  ? ␅
    @+199605 [199605] lij           q1  ? after
    @+247687 [247687] op            q4  ? ␅
    @+247687 [247687] op            q5  ? after
    @+273490 [273490] proef         q6  ? ␅
    @+273490 [273490] proef         q7  ? after
    @+279756 [279756] rechts        q10 ? ␅
    @+279756 [279756] rechts        q11 ? after
    @+283105 [283105] rel           q12 ? ␅
    @+283105 [283105] rel           q13 ? after
    @+284258 [284258] res           q14 ? ␅
    @+284258 [284258] res           q15 ? after
    @+284789 [284789] resultaat     q18 ? ␅
    @+284789 [284789] resultaat     q19 ? after
    @+285066 [285066] reuma         q20 ? ␅
    @+285066 [285066] reuma         q21 ? after
    @+285203 [285203] revalidatie   q22 ? ␅
    @+285203 [285203] revalidatie   q23 ? after
    @+285278 [285278] revier        q24 ? ␅
    @+285278 [285278] revier        q25 ? after
    @+285316 [285316] revitaliseren q26 ? ␅
    @+285316 [285316] revitaliseren q27 ? after
    @+285329 [285329] revolte       q28 ? ␅
    @+285329 [285329] revolte       q29 ? after
    @+285338 [285338] revolutie     q30 ? ␅
    @+285338 [285338] revolutie     q31 ? it
    @+285338 [285338] revolutie     done. it
    @+285358 [285358] revolver      q16 ? ␅
    @+285358 [285358] revolver      q17 ? before
    @+286474 [286474] rijns         q9  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1001 🥳 32 ⏱️ 0:00:40.927140

🤔 32 attempts
📜 1 sessions

    @       [    0] aa             
    @+47380 [47380] dis            q2  ? ␅
    @+47380 [47380] dis            q3  ? after
    @+72798 [72798] gremmy         q4  ? ␅
    @+72798 [72798] gremmy         q5  ? after
    @+79130 [79130] hood           q8  ? ␅
    @+79130 [79130] hood           q9  ? after
    @+79450 [79450] horse          q16 ? ␅
    @+79450 [79450] horse          q17 ? after
    @+79545 [79545] horticulturist q20 ? ␅
    @+79545 [79545] horticulturist q21 ? after
    @+79578 [79578] hospital       q22 ? ␅
    @+79578 [79578] hospital       q23 ? after
    @+79604 [79604] host           q24 ? ␅
    @+79604 [79604] host           q25 ? after
    @+79612 [79612] hostel         q26 ? ␅
    @+79612 [79612] hostel         q27 ? after
    @+79626 [79626] hostess        q28 ? ␅
    @+79626 [79626] hostess        q29 ? after
    @+79630 [79630] hostile        q30 ? ␅
    @+79630 [79630] hostile        q31 ? it
    @+79630 [79630] hostile        done. it
    @+79640 [79640] hot            q18 ? ␅
    @+79640 [79640] hot            q19 ? before
    @+79913 [79913] hoy            q14 ? ␅
    @+79913 [79913] hoy            q15 ? before
    @+80715 [80715] hydroxy        q12 ? ␅
    @+80715 [80715] hydroxy        q13 ? before
    @+82307 [82307] immaterial     q10 ? ␅
    @+82307 [82307] immaterial     q11 ? before
    @+85502 [85502] ins            q7  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1427 🥳 6 ⏱️ 0:01:28.595483

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:DOODY n n n n n remain:6216
    ⬜⬜⬜⬜⬜ tried:ZANZA n n n n n remain:2229
    ⬜⬜⬜⬜⬜ tried:VUGGS n n n n n remain:455
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:153
    ⬜🟨⬜⬜⬜ tried:BELLE n m n n n remain:19
    ⬜🟩🟨🟨⬜ tried:WRECK n Y m m n remain:1

    Undos used: 2

      1 words remaining
    x 6 unused letters
    = 6 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1570 😦 17 ⏱️ 0:03:42.153337

📜 1 sessions
💰 score: 4960

    5/6
    AEGIS ⬜🟨⬜🟨⬜
    RILED ⬜🟩🟨🟨🟩
    BIELD ⬜🟩🟩🟩🟩
    FIELD ⬜🟩🟩🟩🟩
    WIELD 🟩🟩🟩🟩🟩
    3/6
    WIELD ⬜⬜⬜🟨🟩
    ALOUD 🟨🟩⬜⬜🟩
    BLAND 🟩🟩🟩🟩🟩
    3/6
    BLAND ⬜⬜🟩⬜⬜
    TRAPS 🟨⬜🟩🟨🟨
    STAMP 🟩🟩🟩🟩🟩
    4/6
    STAMP ⬜⬜⬜⬜⬜
    WORLD ⬜🟩🟨⬜⬜
    YOURN ⬜🟩🟩🟨⬜
    ROUGH 🟩🟩🟩🟩🟩
    Final 2/2
    ????? 🟩🟩⬜⬜🟨
    ????? 🟩🟩⬜⬜🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1547 🥳 score:25 ⏱️ 0:02:13.768990

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. QUART attempts:5 score:5
2. TUMOR attempts:7 score:7
3. STAFF attempts:4 score:4
4. EAGLE attempts:9 score:9

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1547 🥳 score:60 ⏱️ 0:03:39.360755

📜 2 sessions

Octordle Classic

1. REFIT attempts:11 score:11
2. ABBEY attempts:4 score:4
3. NUDGE attempts:5 score:5
4. CHIEF attempts:9 score:9
5. CLOCK attempts:10 score:10
6. PRESS attempts:8 score:8
7. LEAPT attempts:7 score:7
8. YACHT attempts:6 score:6

# [squareword.org](squareword.org) 🧩 #1540 🥳 7 ⏱️ 0:02:32.468561

📜 2 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P O O N
    C R A V E
    R I S E R
    A M E N D
    M O S S Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1477 🥳 193 ⏱️ 0:01:54.653526

🤔 194 attempts
📜 1 sessions
🫧 7 chat sessions
⁉️ 31 chat prompts
🤖 31 dolphin3:latest replies
🥵   7 😎  16 🥶 140 🧊  30

      $1 #194 compliance      100.00°C 🥳 1000‰ ~164 used:0  [163]  source:dolphin3
      $2 #159 management       36.59°C 🥵  968‰   ~7 used:4  [6]    source:dolphin3
      $3 #183 monitoring       35.82°C 🥵  957‰   ~4 used:2  [3]    source:dolphin3
      $4 #151 automate         35.38°C 🥵  954‰   ~6 used:3  [5]    source:dolphin3
      $5 #155 efficiency       35.22°C 🥵  953‰   ~1 used:0  [0]    source:dolphin3
      $6 #148 workflow         34.76°C 🥵  951‰   ~5 used:2  [4]    source:dolphin3
      $7 #152 automation       34.00°C 🥵  938‰   ~2 used:1  [1]    source:dolphin3
      $8 #178 integration      33.98°C 🥵  937‰   ~3 used:0  [2]    source:dolphin3
      $9 #164 simplification   29.96°C 😎  884‰   ~8 used:0  [7]    source:dolphin3
     $10 #133 streamline       29.08°C 😎  863‰  ~22 used:5  [21]   source:dolphin3
     $11 #172 productivity     28.80°C 😎  851‰   ~9 used:0  [8]    source:dolphin3
     $12 #119 reduction        27.70°C 😎  819‰  ~23 used:5  [22]   source:dolphin3
     $25 #143 operations       19.84°C 🥶        ~31 used:0  [30]   source:dolphin3
    $165 #101 bell             -0.74°C 🧊       ~165 used:0  [164]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1510 🥳 145 ⏱️ 0:02:19.801649

🤔 146 attempts
📜 1 sessions
🫧 8 chat sessions
⁉️ 38 chat prompts
🤖 38 dolphin3:latest replies
😱  1 🔥  1 🥵  9 😎 25 🥶 56 🧊 53

      $1 #146 actualité        100.00°C 🥳 1000‰  ~93 used:0  [92]   source:dolphin3
      $2 #104 rubrique          58.02°C 😱  999‰   ~2 used:17 [1]    source:dolphin3
      $3 #139 presse            47.92°C 🔥  994‰   ~1 used:1  [0]    source:dolphin3
      $4 #142 thème             45.15°C 🥵  985‰   ~3 used:0  [2]    source:dolphin3
      $5 #126 thématique        44.55°C 🥵  983‰   ~7 used:3  [6]    source:dolphin3
      $6  #35 information       42.34°C 🥵  980‰  ~35 used:28 [34]   source:dolphin3
      $7 #129 panorama          35.16°C 🥵  950‰   ~6 used:2  [5]    source:dolphin3
      $8  #74 ligne             35.05°C 🥵  948‰   ~8 used:8  [7]    source:dolphin3
      $9 #121 article           34.08°C 🥵  939‰   ~4 used:0  [3]    source:dolphin3
     $10 #145 vidéo             32.83°C 🥵  927‰   ~5 used:0  [4]    source:dolphin3
     $11  #19 accueil           32.57°C 🥵  923‰  ~29 used:16 [28]   source:dolphin3
     $13 #132 sujet             29.54°C 😎  899‰   ~9 used:0  [8]    source:dolphin3
     $38 #107 illustration      13.26°C 🥶        ~39 used:0  [38]   source:dolphin3
     $94  #17 impôt             -0.17°C 🧊        ~94 used:0  [93]   source:dolphin3
