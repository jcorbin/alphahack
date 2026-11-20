# 2026-11-21

- 🔗 spaceword.org 🧩 2026-11-20 🏁 score 2173 ranked 9.0% 25/277 ⏱️ 1:46:06.250094
- 🔗 wordgrid 🧩 #903 🟪 rarity:0.17 ⏱️ 0:03:49.609832
- 🔗 alfagok.diginaut.net 🧩 #749 🥳 48 ⏱️ 0:03:55.406023
- 🔗 alphaguess.com 🧩 #1216 🥳 32 ⏱️ 0:00:43.991772
- 🔗 dontwordle.com 🧩 #1642 🥳 6 ⏱️ 0:01:32.289960
- 🔗 dictionary.com hurdle 🧩 #1785 😦 19 ⏱️ 0:03:54.034732
- 🔗 Quordle Classic 🧩 #1762 🥳 score:25 ⏱️ 0:01:55.216270
- 🔗 Octordle Classic 🧩 #1762 🥳 score:64 ⏱️ 0:02:02.240677
- 🔗 Sedecordle Classic 🧩 #1742 🥳 score:44 ⏱️ 0:03:10.917705
- 🔗 squareword.org 🧩 #1755 🥳 9 ⏱️ 0:02:30.843903
- 🔗 cemantle.certitudes.org 🧩 #1692 🥳 199 ⏱️ 0:00:48.060757
- 🔗 cemantix.certitudes.org 🧩 #1725 🥳 110 ⏱️ 0:00:30.783126

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










# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #892 🟪 rarity:0.32 ⏱️ 0:03:10.891631

📜 2 sessions
🌌 🦄 🦄
🌌 🌌 🌌
🦄 🌌 🌌
Rarity: 0.32 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-09 🏁 score 2168 ranked 49.8% 148/297 ⏱️ 0:22:41.164996

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 148/297

      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ G _ _ _ _ K _ L _
      _ O _ C A S A V A _
      _ A _ A _ _ S I G _
      _ D A W E N _ A _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _













# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #903 🟪 rarity:0.17 ⏱️ 0:03:49.609832

📜 2 sessions
🌌 🌌 🦄
🌌 🌌 🦄
🌌 🌌 🌌
Rarity: 0.17 🟪

# [spaceword.org](spaceword.org) 🧩 2026-11-20 🏁 score 2173 ranked 9.0% 25/277 ⏱️ 1:46:06.250094

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 25/277

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ L A _ _ _ _   
      _ _ _ _ _ H _ _ _ _   
      _ _ _ _ S E G _ _ _   
      _ _ _ _ E M O _ _ _   
      _ _ _ _ Q _ D _ _ _   
      _ _ _ _ U _ W _ _ _   
      _ _ _ _ O K A _ _ _   
      _ _ _ _ I _ R _ _ _   
      _ _ _ _ A I D _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #749 🥳 48 ⏱️ 0:03:55.406023

🤔 48 attempts
📜 2 sessions

    @       [    0] &-teken      
    @+49802 [49802] boks         q6  ? ␅
    @+49802 [49802] boks         q7  ? after
    @+74698 [74698] dc           q8  ? ␅
    @+74698 [74698] dc           q9  ? after
    @+87156 [87156] draag        q10 ? ␅
    @+87156 [87156] draag        q11 ? after
    @+90006 [90006] dubbel       q14 ? ␅
    @+90006 [90006] dubbel       q15 ? after
    @+90842 [90842] duivelskunst q18 ? ␅
    @+90842 [90842] duivelskunst q19 ? after
    @+91039 [91039] dum          q22 ? ␅
    @+91039 [91039] dum          q23 ? after
    @+91134 [91134] duo          q24 ? ␅
    @+91134 [91134] duo          q25 ? after
    @+91198 [91198] duratief     q36 ? ␅
    @+91198 [91198] duratief     q37 ? after
    @+91228 [91228] duro         q42 ? ␅
    @+91228 [91228] duro         q43 ? after
    @+91230 [91230] durven       q46 ? ␅
    @+91230 [91230] durven       q47 ? it
    @+91230 [91230] durven       done. it
    @+91235 [91235] dus          q44 ? ␅
    @+91235 [91235] dus          q45 ? before
    @+91255 [91255] dut          q20 ? ␅
    @+91255 [91255] dut          q21 ? before
    @+91676 [91676] dwerg        q16 ? ␅
    @+91676 [91676] dwerg        q17 ? before
    @+93361 [93361] eet          q12 ? ␅
    @+93361 [93361] eet          q13 ? before
    @+99665 [99665] ex           q5  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1216 🥳 32 ⏱️ 0:00:43.991772

🤔 32 attempts
📜 1 sessions

    @        [     0] aa         
    @+98138  [ 98138] mac        q0  ? ␅
    @+98138  [ 98138] mac        q1  ? after
    @+122714 [122714] parol      q4  ? ␅
    @+122714 [122714] parol      q5  ? after
    @+134992 [134992] prop       q6  ? ␅
    @+134992 [134992] prop       q7  ? after
    @+141005 [141005] recon      q8  ? ␅
    @+141005 [141005] recon      q9  ? after
    @+142196 [142196] ref        q12 ? ␅
    @+142196 [142196] ref        q13 ? after
    @+143163 [143163] reinforce  q14 ? ␅
    @+143163 [143163] reinforce  q15 ? after
    @+143650 [143650] religious  q16 ? ␅
    @+143650 [143650] religious  q17 ? after
    @+143763 [143763] rem        q18 ? ␅
    @+143763 [143763] rem        q19 ? after
    @+143943 [143943] remiss     q20 ? ␅
    @+143943 [143943] remiss     q21 ? after
    @+144036 [144036] remorse    q22 ? ␅
    @+144036 [144036] remorse    q23 ? after
    @+144044 [144044] remortgage q28 ? ␅
    @+144044 [144044] remortgage q29 ? after
    @+144048 [144048] remote     q30 ? ␅
    @+144048 [144048] remote     q31 ? it
    @+144048 [144048] remote     done. it
    @+144057 [144057] remotivate q26 ? ␅
    @+144057 [144057] remotivate q27 ? before
    @+144082 [144082] remove     q24 ? ␅
    @+144082 [144082] remove     q25 ? before
    @+144138 [144138] rend       q11 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1642 🥳 6 ⏱️ 0:01:32.289960

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:TENNE n n n n n remain:4097
    ⬜⬜⬜⬜⬜ tried:MAGMA n n n n n remain:1333
    ⬜⬜⬜⬜⬜ tried:OPPOS n n n n n remain:181
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:50
    ⬜🟩⬜⬜⬜ tried:KUDZU n Y n n n remain:6
    🟩🟩⬜🟨⬜ tried:CURCH Y Y n m n remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1785 😦 19 ⏱️ 0:03:54.034732

📜 2 sessions
💰 score: 4760

    3/6
    AEONS 🟨⬜⬜⬜🟨
    SPLAT 🟩⬜⬜🟩⬜
    SUGAR 🟩🟩🟩🟩🟩
    5/6
    SUGAR ⬜⬜⬜🟨⬜
    ALIEN 🟨⬜⬜⬜⬜
    PATCH ⬜🟨⬜⬜⬜
    FAMED ⬜🟨⬜⬜🟨
    VODKA 🟩🟩🟩🟩🟩
    4/6
    VODKA ⬜🟩⬜⬜⬜
    EOSIN 🟨🟩⬜⬜⬜
    POLER ⬜🟩⬜🟩⬜
    COMET 🟩🟩🟩🟩🟩
    5/6
    COMET ⬜⬜⬜⬜⬜
    LIARS ⬜⬜🟩🟨⬜
    PRANK ⬜🟩🟩🟨⬜
    BRAWN ⬜🟩🟩🟩🟩
    DRAWN 🟩🟩🟩🟩🟩
    Final 2/2
    ????? ⬜⬜🟨⬜⬜
    ????? 🟩🟩🟩🟩⬜

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1762 🥳 score:25 ⏱️ 0:01:55.216270

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. GRIPE attempts:6 score:6
2. SOLID attempts:3 score:3
3. SHAME attempts:9 score:9
4. CRUEL attempts:7 score:7

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1762 🥳 score:64 ⏱️ 0:02:02.240677

📜 1 sessions

Octordle Classic

1. VERSO attempts:3 score:3
2. CRAZE attempts:10 score:10
3. TACKY attempts:8 score:8
4. STACK attempts:9 score:9
5. AXION attempts:12 score:12
6. ENNUI attempts:11 score:11
7. MORPH attempts:4 score:4
8. ABBOT attempts:7 score:7

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1742 🥳 score:44 ⏱️ 0:03:10.917705

📜 2 sessions

Sedecordle Classic sedecordle.com

1. DEBIT attempts:17 score:1
2. VERGE attempts:18 score:7
3. ALIVE attempts:12 score:1
4. ABBEY attempts:7 score:2
5. FAULT attempts:18 score:1
6. GUMBO attempts:15 score:9
7. FETAL attempts:6 score:0
8. TRACE attempts:11 score:6
9. BAGGY attempts:13 score:1
10. ENSUE attempts:3 score:3
11. FLUFF attempts:16 score:1
12. SOOTY attempts:9 score:6
13. DEUCE attempts:10 score:1
14. BLEAT attempts:8 score:0
15. HEFTY attempts:14 score:1
16. FLAKE attempts:5 score:4

# [squareword.org](squareword.org) 🧩 #1755 🥳 9 ⏱️ 0:02:30.843903

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟨 🟩
    🟨 🟩 🟨 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T O P S
    N O V A E
    I N A N E
    P A R E D
    S L Y L Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1692 🥳 199 ⏱️ 0:00:48.060757

🤔 200 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 26 chat prompts
🤖 26 glm-5.3-flash:cloud replies
🥵   2 😎  11 🥶 173 🧊  13

      $1 #200 metropolitan   100.00°C 🥳 1000‰ ~187 used:0  [186]  source:glm
      $2 #121 affluent        37.93°C 🥵  982‰   ~6 used:16 [5]    source:glm
      $3 #172 in              30.19°C 🥵  938‰   ~1 used:5  [0]    source:glm
      $4 #119 upscale         27.92°C 😎  887‰  ~13 used:8  [12]   source:glm
      $5 #183 uptown          26.68°C 😎  861‰   ~2 used:1  [1]    source:glm
      $6 #136 prosperous      23.18°C 😎  731‰   ~9 used:3  [8]    source:glm
      $7 #112 posh            23.07°C 😎  726‰  ~10 used:3  [9]    source:glm
      $8 #152 thriving        22.87°C 😎  719‰   ~3 used:1  [2]    source:glm
      $9 #115 ritzy           21.51°C 😎  641‰   ~7 used:2  [6]    source:glm
     $10 #153 upmarket        20.20°C 😎  523‰   ~4 used:1  [3]    source:glm
     $11 #134 moneyed         19.77°C 😎  479‰   ~5 used:0  [4]    source:glm
     $12  #73 velvety         19.35°C 😎  434‰  ~12 used:4  [11]   source:glm
     $15 #158 wealthy         16.91°C 🥶        ~18 used:0  [17]   source:glm
    $188   #5 guitar          -0.06°C 🧊       ~188 used:0  [187]  source:glm

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1725 🥳 110 ⏱️ 0:00:30.783126

🤔 111 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 13 chat prompts
🤖 13 glm-5.3-flash:cloud replies
🔥  4 🥵  7 😎 19 🥶 59 🧊 21

      $1 #111 acheteur        100.00°C 🥳 1000‰  ~90 used:0 [89]   source:glm
      $2  #99 achat            57.26°C 🔥  997‰   ~2 used:2 [1]    source:glm
      $3  #81 client           54.67°C 🔥  996‰   ~4 used:6 [3]    source:glm
      $4 #110 marché           50.79°C 🔥  991‰   ~1 used:0 [0]    source:glm
      $5  #84 consommateur     48.17°C 🔥  990‰   ~3 used:4 [2]    source:glm
      $6  #83 commande         47.69°C 🥵  989‰   ~5 used:1 [4]    source:glm
      $7  #62 utilisateur      41.23°C 🥵  980‰  ~10 used:4 [9]    source:glm
      $8  #89 litige           40.29°C 🥵  975‰   ~6 used:0 [5]    source:glm
      $9  #95 rétractation     40.06°C 🥵  974‰   ~7 used:0 [6]    source:glm
     $10  #93 remboursement    35.51°C 🥵  936‰   ~8 used:0 [7]    source:glm
     $11  #94 réclamation      35.11°C 🥵  930‰   ~9 used:0 [8]    source:glm
     $13  #97 souscripteur     30.77°C 😎  855‰  ~12 used:0 [11]   source:glm
     $32  #33 fichier          19.63°C 🥶        ~34 used:1 [33]   source:glm
     $91  #60 sigle            -0.58°C 🧊        ~91 used:0 [90]   source:glm
