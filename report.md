# 2026-09-06

- 🔗 spaceword.org 🧩 2026-09-05 🏁 score 2168 ranked 36.2% 117/323 ⏱️ 0:07:50.716125
- 🔗 wordgrid 🧩 #827 🟪 rarity:0.29 ⏱️ 0:02:40.306882
- 🔗 alfagok.diginaut.net 🧩 #673 🥳 20 ⏱️ 0:00:30.553685
- 🔗 alphaguess.com 🧩 #1140 🥳 28 ⏱️ 0:00:40.472790
- 🔗 dontwordle.com 🧩 #1566 🥳 6 ⏱️ 0:02:45.096387
- 🔗 dictionary.com hurdle 🧩 #1709 🥳 13 ⏱️ 0:02:42.060905
- 🔗 Quordle Classic 🧩 #1686 🥳 score:22 ⏱️ 0:02:22.807227
- 🔗 Octordle Classic 🧩 #1686 🥳 score:67 ⏱️ 0:03:26.685487
- 🔗 Sedecordle Classic 🧩 #1666 🥳 score:36 ⏱️ 0:03:12.035197
- 🔗 squareword.org 🧩 #1679 🥳 8 ⏱️ 0:02:30.515011
- 🔗 cemantle.certitudes.org 🧩 #1616 🥳 110 ⏱️ 0:01:13.795287
- 🔗 cemantix.certitudes.org 🧩 #1649 🥳 125 ⏱️ 0:01:39.384450

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







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #781 🟪 rarity:0.15 ⏱️ 0:03:50.236694

📜 2 sessions
🌌 🦄 🦄
🌌 🦄 🦄
🌌 🌌 🌌
Rarity: 0.15 🟪


# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #-1 ❗ rarity:nan ⏱️ 0:05:19.095498

📜 2 sessions
🌌 🦄 🌌
🌌 🦄 🌌
🌌 🦄 🌌
Rarity: nan ❗







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #788 🟪 rarity:0.29 ⏱️ 0:03:24.033720

📜 2 sessions
🦄 🦄 🌌
🦄 🦄 🦄
🌌 🦄 🌌
Rarity: 0.29 🟪


# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #789 🟪 rarity:0.23 ⏱️ 0:02:56.015327

📜 2 sessions
🌌 🌌 🌌
🦄 🦄 🌌
🦄 🦄 🦄
Rarity: 0.23 🟪







# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #795 🟪 rarity:0.27 ⏱️ 0:03:44.973967

📜 2 sessions
🦄 🌌 🌌
🌌 🌌 🌌
🦄 🦄 🌌
Rarity: 0.27 🟪

































# [spaceword.org](spaceword.org) 🧩 2026-09-05 🏁 score 2168 ranked 36.2% 117/323 ⏱️ 0:07:50.716125

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 117/323

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ A B Y _ _ _ _   
      _ _ _ _ R _ O _ _ _   
      _ _ _ Q U I Z _ _ _   
      _ _ _ I T _ O _ _ _   
      _ _ _ _ E _ N _ _ _   
      _ _ _ _ L _ I _ _ _   
      _ _ _ W Y E S _ _ _   
      _ _ _ _ _ _ E _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #827 🟪 rarity:0.29 ⏱️ 0:02:40.306882

📜 2 sessions
🌌 🦄 🌌
🦄 🌌 🦄
🦄 🌌 🌌
Rarity: 0.29 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #673 🥳 20 ⏱️ 0:00:30.553685

🤔 20 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199640 [199640] lijk      q0  ? ␅
    @+199640 [199640] lijk      q1  ? after
    @+199640 [199640] lijk      q2  ? ␅
    @+199640 [199640] lijk      q3  ? after
    @+199640 [199640] lijk      q4  ? ␅
    @+199640 [199640] lijk      q5  ? after
    @+224537 [224537] moord     q10 ? ␅
    @+224537 [224537] moord     q11 ? after
    @+230458 [230458] neer      q14 ? ␅
    @+230458 [230458] neer      q15 ? after
    @+233683 [233683] nood      q16 ? ␅
    @+233683 [233683] nood      q17 ? after
    @+235346 [235346] oceaan    q18 ? ␅
    @+235346 [235346] oceaan    q19 ? it
    @+235346 [235346] oceaan    done. it
    @+237027 [237027] om        q12 ? ␅
    @+237027 [237027] om        q13 ? before
    @+249561 [249561] opinie    q8  ? ␅
    @+249561 [249561] opinie    q9  ? before
    @+299544 [299544] schroot   q6  ? ␅
    @+299544 [299544] schroot   q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1140 🥳 28 ⏱️ 0:00:40.472790

🤔 28 attempts
📜 1 sessions

    @       [    0] aa      
    @+2     [    2] aahed   
    @+11763 [11763] back    q8  ? ␅
    @+11763 [11763] back    q9  ? after
    @+17714 [17714] blind   q10 ? ␅
    @+17714 [17714] blind   q11 ? after
    @+19159 [19159] boot    q14 ? ␅
    @+19159 [19159] boot    q15 ? after
    @+19408 [19408] bot     q18 ? ␅
    @+19408 [19408] bot     q19 ? after
    @+19520 [19520] boubous q22 ? ␅
    @+19520 [19520] boubous q23 ? after
    @+19575 [19575] boult   q24 ? ␅
    @+19575 [19575] boult   q25 ? after
    @+19592 [19592] bound   q26 ? ␅
    @+19592 [19592] bound   q27 ? it
    @+19592 [19592] bound   done. it
    @+19631 [19631] bourg   q20 ? ␅
    @+19631 [19631] bourg   q21 ? before
    @+19873 [19873] bra     q16 ? ␅
    @+19873 [19873] bra     q17 ? before
    @+20685 [20685] brill   q12 ? ␅
    @+20685 [20685] brill   q13 ? before
    @+23680 [23680] camp    q6  ? ␅
    @+23680 [23680] camp    q7  ? before
    @+47378 [47378] dis     q4  ? ␅
    @+47378 [47378] dis     q5  ? before
    @+98147 [98147] mac     q0  ? ␅
    @+98147 [98147] mac     q1  ? after
    @+98147 [98147] mac     q2  ? ␅
    @+98147 [98147] mac     q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1566 🥳 6 ⏱️ 0:02:45.096387

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:MINIM n n n n n remain:6310
    ⬜⬜⬜⬜⬜ tried:TOOTH n n n n n remain:2558
    ⬜⬜⬜⬜⬜ tried:VUGGS n n n n n remain:651
    ⬜⬜⬜🟩⬜ tried:DRYLY n n n Y n remain:14
    🟨⬜⬜🟩🟩 tried:APPLE m n n Y Y remain:2
    ⬜🟩🟩🟩🟩 tried:CABLE n Y Y Y Y remain:1

    Undos used: 5

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1709 🥳 13 ⏱️ 0:02:42.060905

📜 1 sessions
💰 score: 10300

    2/6
    NARES 🟨⬜🟨⬜⬜
    BRUIN 🟩🟩🟩🟩🟩
    4/6
    BRUIN 🟩⬜⬜⬜⬜
    BLOKE 🟩⬜⬜⬜🟨
    BEAST 🟩🟩⬜⬜🟩
    BEGET 🟩🟩🟩🟩🟩
    3/6
    BEGET ⬜⬜🟨⬜🟩
    GROAT 🟩🟩⬜⬜🟩
    GRIFT 🟩🟩🟩🟩🟩
    2/6
    GRIFT ⬜⬜🟩⬜🟨
    UNITE 🟩🟩🟩🟩🟩
    Final 2/2
    SMOLT ⬜⬜🟨🟨🟩
    ALLOT 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1686 🥳 score:22 ⏱️ 0:02:22.807227

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. PILOT attempts:5 score:5
2. HONOR attempts:3 score:3
3. BOWEL attempts:6 score:6
4. TAUNT attempts:8 score:8

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1686 🥳 score:67 ⏱️ 0:03:26.685487

📜 1 sessions

Octordle Classic

1. RUDER attempts:10 score:10
2. MERCY attempts:7 score:7
3. LIBEL attempts:12 score:12
4. CREAK attempts:5 score:5
5. LATER attempts:12 score:13
6. OCEAN attempts:3 score:3
7. MOURN attempts:8 score:8
8. REVUE attempts:9 score:9

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1666 🥳 score:36 ⏱️ 0:03:12.035197

📜 1 sessions

Sedecordle Classic sedecordle.com

1. STEER attempts:3 score:0
2. CAGEY attempts:7 score:3
3. FILTH attempts:10 score:1
4. SKULL attempts:11 score:0
5. ENEMY attempts:6 score:0
6. SMOCK attempts:9 score:6
7. SUMAC attempts:12 score:1
8. UPSET attempts:4 score:2
9. BROAD attempts:13 score:1
10. WITTY attempts:14 score:3
11. LOOSE attempts:15 score:1
12. ORBIT attempts:16 score:5
13. EXIST attempts:17 score:1
14. THROB attempts:18 score:7
15. PESKY attempts:5 score:0
16. YEARN attempts:8 score:5

# [squareword.org](squareword.org) 🧩 #1679 🥳 8 ⏱️ 0:02:30.515011

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    R E A M S
    A L L O W
    G U I D E
    E D G E D
    D E N S E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1616 🥳 110 ⏱️ 0:01:13.795287

🤔 111 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 22 chat prompts
🤖 22 dolphin3:latest replies
🔥   1 😎   3 🥶 100 🧊   6

      $1 #111 composition    100.00°C 🥳 1000‰ ~105 used:0 [104]  source:dolphin3
      $2  #90 structure       43.85°C 🔥  994‰   ~1 used:7 [0]    source:dolphin3
      $3  #63 particle        29.92°C 😎  307‰   ~4 used:5 [3]    source:dolphin3
      $4  #83 matrix          29.25°C 😎  192‰   ~2 used:1 [1]    source:dolphin3
      $5  #99 arrangement     28.83°C 😎   93‰   ~3 used:0 [2]    source:dolphin3
      $6  #49 fragment        28.25°C 🥶         ~7 used:5 [6]    source:dolphin3
      $7  #91 substructure    28.15°C 🥶        ~14 used:0 [13]   source:dolphin3
      $8  #97 subatomic       26.73°C 🥶        ~15 used:0 [14]   source:dolphin3
      $9  #56 piece           26.06°C 🥶         ~8 used:4 [7]    source:dolphin3
     $10  #85 molecular       25.49°C 🥶        ~16 used:0 [15]   source:dolphin3
     $11  #82 granule         24.17°C 🥶        ~17 used:0 [16]   source:dolphin3
     $12 #109 molecule        23.80°C 🥶        ~18 used:0 [17]   source:dolphin3
     $13 #100 design          23.36°C 🥶        ~19 used:0 [18]   source:dolphin3
    $106  #87 organization    -0.14°C 🧊       ~106 used:0 [105]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1649 🥳 125 ⏱️ 0:01:39.384450

🤔 126 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 30 chat prompts
🤖 30 dolphin3:latest replies
🔥  3 🥵 13 😎 19 🥶 71 🧊 19

      $1 #126 certificat        100.00°C 🥳 1000‰ ~107 used:0  [106]  source:dolphin3
      $2  #93 attestation        70.68°C 😱  999‰   ~1 used:22 [0]    source:dolphin3
      $3  #76 certification      53.12°C 🔥  997‰  ~10 used:18 [9]    source:dolphin3
      $4  #44 diplôme            51.09°C 🔥  995‰   ~9 used:14 [8]    source:dolphin3
      $5  #85 validation         42.09°C 🥵  981‰  ~15 used:3  [14]   source:dolphin3
      $6  #91 aptitude           41.73°C 🥵  979‰  ~11 used:2  [10]   source:dolphin3
      $7 #112 vérification       38.56°C 🥵  965‰  ~12 used:2  [11]   source:dolphin3
      $8  #28 examen             37.92°C 🥵  963‰  ~16 used:3  [15]   source:dolphin3
      $9 #119 inscription        36.93°C 🥵  955‰   ~2 used:1  [1]    source:dolphin3
     $10  #69 qualification      34.92°C 🥵  942‰  ~13 used:2  [12]   source:dolphin3
     $11 #103 authentification   34.84°C 🥵  941‰  ~14 used:2  [13]   source:dolphin3
     $18 #116 dossier            31.60°C 😎  891‰  ~17 used:0  [16]   source:dolphin3
     $37  #82 approbation        18.59°C 🥶        ~39 used:0  [38]   source:dolphin3
    $108  #47 innovation         -0.22°C 🧊       ~108 used:0  [107]  source:dolphin3
