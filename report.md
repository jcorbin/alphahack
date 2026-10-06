# 2026-10-07

- 🔗 spaceword.org 🧩 2026-10-06 🏁 score 2164 ranked 47.3% 165/349 ⏱️ 0:05:35.182338
- 🔗 wordgrid 🧩 #858 🟪 rarity:0.25 ⏱️ 0:02:00.436910
- 🔗 alfagok.diginaut.net 🧩 #704 🥳 36 ⏱️ 0:00:40.808085
- 🔗 alphaguess.com 🧩 #1171 🥳 28 ⏱️ 0:00:30.428851
- 🔗 dontwordle.com 🧩 #1597 🥳 6 ⏱️ 0:01:16.201812
- 🔗 dictionary.com hurdle 🧩 #1740 🥳 20 ⏱️ 0:03:47.232937
- 🔗 Quordle Classic 🧩 #1717 🥳 score:18 ⏱️ 0:02:04.919327
- 🔗 Octordle Classic 🧩 #1717 🥳 score:60 ⏱️ 0:01:37.519527
- 🔗 Sedecordle Classic 🧩 #1697 🥳 score:42 ⏱️ 0:02:40.388178
- 🔗 squareword.org 🧩 #1710 🥳 11 ⏱️ 0:03:44.839908
- 🔗 cemantle.certitudes.org 🧩 #1647 🥳 226 ⏱️ 0:09:00.866709
- 🔗 cemantix.certitudes.org 🧩 #1680 🥳 133 ⏱️ 0:03:48.796107

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



# [spaceword.org](spaceword.org) 🧩 2026-10-06 🏁 score 2164 ranked 47.3% 165/349 ⏱️ 0:05:35.182338

📜 2 sessions
- tiles: 21/21
- score: 2164 bonus: +64
- rank: 165/349

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ E X I T _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ _ Q _ W _ _ _   
      _ _ _ _ U _ I _ _ _   
      _ _ _ _ O _ N _ _ _   
      _ _ _ _ T E G _ _ _   
      _ _ _ H I _ _ _ _ _   
      _ _ _ E N O L _ _ _   
      _ _ _ _ G _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #858 🟪 rarity:0.25 ⏱️ 0:02:00.436910

📜 2 sessions
🌌 🌌 🌌
🌌 🦄 🌌
🌌 🌌 🌌
Rarity: 0.25 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #704 🥳 36 ⏱️ 0:00:40.808085

🤔 36 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+199528 [199528] lij          q0  ? ␅
    @+199528 [199528] lij          q1  ? after
    @+223512 [223512] molen        q6  ? ␅
    @+223512 [223512] molen        q7  ? after
    @+235519 [235519] octrooi      q8  ? ␅
    @+235519 [235519] octrooi      q9  ? after
    @+238633 [238633] on           q10 ? ␅
    @+238633 [238633] on           q11 ? after
    @+239418 [239418] onder        q16 ? ␅
    @+239418 [239418] onder        q17 ? after
    @+239740 [239740] onderhand    q22 ? ␅
    @+239740 [239740] onderhand    q23 ? after
    @+239836 [239836] onderhoud    q24 ? ␅
    @+239836 [239836] onderhoud    q25 ? after
    @+239949 [239949] onderin      q26 ? ␅
    @+239949 [239949] onderin      q27 ? after
    @+240006 [240006] onderkruip   q28 ? ␅
    @+240006 [240006] onderkruip   q29 ? after
    @+240035 [240035] onderlig     q30 ? ␅
    @+240035 [240035] onderlig     q31 ? after
    @+240047 [240047] onderlijn    q32 ? ␅
    @+240047 [240047] onderlijn    q33 ? after
    @+240056 [240056] onderling    q34 ? ␅
    @+240056 [240056] onderling    q35 ? it
    @+240056 [240056] onderling    done. it
    @+240068 [240068] onderlossers q18 ? ␅
    @+240068 [240068] onderlossers q19 ? n
    @+240068 [240068] onderlossers q20 ? ␅
    @+240068 [240068] onderlossers q21 ? before
    @+240717 [240717] onderwijs    q15 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1171 🥳 28 ⏱️ 0:00:30.428851

🤔 28 attempts
📜 1 sessions

    @       [    0] aa      
    @+2     [    2] aahed   
    @+47374 [47374] dis     q2  ? ␅
    @+47374 [47374] dis     q3  ? after
    @+72657 [72657] green   q4  ? ␅
    @+72657 [72657] green   q5  ? after
    @+75776 [75776] hat     q10 ? ␅
    @+75776 [75776] hat     q11 ? after
    @+77392 [77392] heroic  q12 ? ␅
    @+77392 [77392] heroic  q13 ? after
    @+77764 [77764] hid     q16 ? ␅
    @+77764 [77764] hid     q17 ? after
    @+77956 [77956] hillo   q18 ? ␅
    @+77956 [77956] hillo   q19 ? after
    @+78042 [78042] hip     q20 ? ␅
    @+78042 [78042] hip     q21 ? after
    @+78095 [78095] hipster q22 ? ␅
    @+78095 [78095] hipster q23 ? after
    @+78103 [78103] hire    q26 ? ␅
    @+78103 [78103] hire    q27 ? it
    @+78103 [78103] hire    done. it
    @+78124 [78124] hirsle  q24 ? ␅
    @+78124 [78124] hirsle  q25 ? before
    @+78156 [78156] hist    q14 ? ␅
    @+78156 [78156] hist    q15 ? before
    @+79014 [79014] hone    q8  ? ␅
    @+79014 [79014] hone    q9  ? before
    @+85392 [85392] inocula q6  ? ␅
    @+85392 [85392] inocula q7  ? before
    @+98142 [98142] mac     q0  ? ␅
    @+98142 [98142] mac     q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1597 🥳 6 ⏱️ 0:01:16.201812

📜 1 sessions
💰 score: 24

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:BOOBY n n n n n remain:6682
    ⬜⬜⬜⬜⬜ tried:VIVID n n n n n remain:3260
    ⬜⬜⬜⬜⬜ tried:JUGUM n n n n n remain:1637
    ⬜⬜🟨⬜⬜ tried:CLEEK n n m n n remain:173
    ⬜🟨⬜🟩⬜ tried:NERTZ n m n Y n remain:9
    🟨🟩🟩🟩⬜ tried:EASTS m Y Y Y n remain:4

    Undos used: 3

      4 words remaining
    x 6 unused letters
    = 24 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1740 🥳 20 ⏱️ 0:03:47.232937

📜 1 sessions
💰 score: 9600

    4/6
    EARLS 🟨🟩⬜⬜🟨
    SATED 🟨🟩🟨🟨⬜
    BATCH ⬜🟩🟨🟨⬜
    CASTE 🟩🟩🟩🟩🟩
    6/6
    CASTE ⬜🟩🟩⬜⬜
    MASHY ⬜🟩🟩⬜⬜
    GIVER ⬜🟨⬜⬜⬜
    ABHOR 🟨🟨⬜⬜⬜
    ALIGN 🟨🟨🟨⬜⬜
    BASIL 🟩🟩🟩🟩🟩
    4/6
    BASIL ⬜⬜⬜⬜🟩
    ENROL 🟨⬜🟨⬜🟩
    CRAFT ⬜🟨⬜⬜⬜
    REPEL 🟩🟩🟩🟩🟩
    5/6
    REPEL ⬜🟨⬜⬜⬜
    STANE ⬜⬜⬜🟨🟨
    EIKON 🟩⬜⬜🟩🟨
    JIVED 🟨⬜⬜🟨⬜
    ENJOY 🟩🟩🟩🟩🟩
    Final 1/2
    LOGIC 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1717 🥳 score:18 ⏱️ 0:02:04.919327

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. PALER attempts:3 score:3
2. FROTH attempts:4 score:4
3. DOZEN attempts:6 score:6
4. ERASE attempts:5 score:5

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1717 🥳 score:60 ⏱️ 0:01:37.519527

📜 1 sessions

Octordle Classic

1. SATIN attempts:3 score:3
2. ADEPT attempts:5 score:5
3. WIGHT attempts:12 score:12
4. FUNNY attempts:7 score:7
5. ENJOY attempts:8 score:8
6. GORGE attempts:9 score:9
7. POPPY attempts:10 score:10
8. PLANK attempts:6 score:6

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1697 🥳 score:42 ⏱️ 0:02:40.388178

📜 1 sessions

Sedecordle Classic sedecordle.com

1. MAYOR attempts:17 score:1
2. UNWED attempts:9 score:7
3. SCOLD attempts:5 score:0
4. TAROT attempts:7 score:5
5. FORGO attempts:16 score:1
6. SHOWN attempts:10 score:6
7. ECLAT attempts:6 score:0
8. BRAWL attempts:8 score:6
9. CYCLE attempts:14 score:1
10. LIMIT attempts:15 score:4
11. GRAIL attempts:13 score:1
12. OWNER attempts:12 score:3
13. QUIRK attempts:3 score:0
14. DUSTY attempts:11 score:3
15. GUILD attempts:4 score:0
16. SPENT attempts:18 score:4

# [squareword.org](squareword.org) 🧩 #1710 🥳 11 ⏱️ 0:03:44.839908

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟧 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟨 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    N A M E D
    E L I D E
    W O N G A
    S H E E R
    Y A R D S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1647 🥳 226 ⏱️ 0:09:00.866709

🤔 227 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 44 chat prompts
🤖 44 dolphin3:latest replies
🥵   6 😎  30 🥶 185 🧊   5

      $1 #227 tissue            100.00°C 🥳 1000‰ ~222 used:0  [221]  source:dolphin3
      $2 #225 epithelial         54.42°C 🥵  989‰   ~1 used:0  [0]    source:dolphin3
      $3  #92 membrane           53.44°C 🥵  981‰  ~35 used:32 [34]   source:dolphin3
      $4 #206 endothelium        50.08°C 🥵  942‰   ~3 used:6  [2]    source:dolphin3
      $5 #201 endothelial        49.56°C 🥵  931‰   ~2 used:4  [1]    source:dolphin3
      $6  #99 myelin             48.21°C 🥵  903‰  ~27 used:20 [26]   source:dolphin3
      $7 #127 protein            48.19°C 🥵  902‰  ~26 used:13 [25]   source:dolphin3
      $8 #112 vesicle            47.92°C 😎  894‰  ~28 used:2  [27]   source:dolphin3
      $9 #164 enzyme             47.35°C 😎  874‰  ~29 used:2  [28]   source:dolphin3
     $10 #190 phagocytosis       47.32°C 😎  872‰  ~30 used:2  [29]   source:dolphin3
     $11 #179 enzymatic          46.93°C 😎  855‰  ~31 used:2  [30]   source:dolphin3
     $12  #51 cell               46.12°C 😎  823‰  ~36 used:6  [35]   source:dolphin3
     $38 #191 phenotype          36.51°C 🥶        ~42 used:0  [41]   source:dolphin3
    $223 #118 coupled            -0.27°C 🧊       ~223 used:0  [222]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1680 🥳 133 ⏱️ 0:03:48.796107

🤔 134 attempts
📜 2 sessions
🫧 5 chat sessions
⁉️ 23 chat prompts
🤖 23 dolphin3:latest replies
🔥  2 🥵 18 😎 56 🥶 50 🧊  7

      $1 #134 déploiement         100.00°C 🥳 1000‰ ~127 used:0  [126]  source:dolphin3
      $2 #131 développement        48.45°C 🔥  995‰   ~1 used:2  [0]    source:dolphin3
      $3  #70 intégration          47.98°C 🔥  993‰  ~11 used:17 [10]   source:dolphin3
      $4  #10 réseau               45.33°C 🥵  988‰  ~75 used:15 [74]   source:dolphin3
      $5  #47 processus            43.80°C 🥵  986‰  ~19 used:8  [18]   source:dolphin3
      $6  #64 optimisation         42.00°C 🥵  980‰  ~18 used:3  [17]   source:dolphin3
      $7  #52 système              41.47°C 🥵  977‰  ~12 used:2  [11]   source:dolphin3
      $8  #36 application          40.77°C 🥵  969‰  ~13 used:2  [12]   source:dolphin3
      $9  #72 paramétrage          40.62°C 🥵  967‰  ~14 used:2  [13]   source:dolphin3
     $10  #22 interconnexion       40.29°C 🥵  963‰  ~15 used:2  [14]   source:dolphin3
     $11  #57 gestion              40.14°C 🥵  961‰  ~16 used:2  [15]   source:dolphin3
     $22  #51 service              34.70°C 😎  891‰  ~20 used:0  [19]   source:dolphin3
     $78  #60 traitement           21.17°C 🥶        ~78 used:0  [77]   source:dolphin3
    $128  #14 arête                -1.82°C 🧊       ~128 used:0  [127]  source:dolphin3
