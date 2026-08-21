# 2026-08-22

- 🔗 spaceword.org 🧩 2026-08-21 🏁 score 2173 ranked 4.3% 14/328 ⏱️ 0:42:40.557229
- 🔗 wordgrid 🧩 #812 🌌 rarity:0.09 ⏱️ 0:02:29.017556
- 🔗 alfagok.diginaut.net 🧩 #658 🥳 44 ⏱️ 0:00:53.765102
- 🔗 alphaguess.com 🧩 #1125 🥳 32 ⏱️ 0:01:46.858789
- 🔗 dontwordle.com 🧩 #1551 🥳 6 ⏱️ 0:01:43.293338
- 🔗 dictionary.com hurdle 🧩 #1694 🥳 20 ⏱️ 0:04:40.965569
- 🔗 Quordle Classic 🧩 #1671 🥳 score:27 ⏱️ 0:03:07.302636
- 🔗 Octordle Classic 🧩 #1671 🥳 score:63 ⏱️ 0:01:44.353272
- 🔗 Sedecordle Classic 🧩 #1651 🥳 score:40 ⏱️ 0:03:21.949441
- 🔗 squareword.org 🧩 #1664 🥳 9 ⏱️ 0:02:39.604374
- 🔗 cemantle.certitudes.org 🧩 #1601 🥳 558 ⏱️ 0:18:58.056132
- 🔗 cemantix.certitudes.org 🧩 #1634 🥳 297 ⏱️ 0:02:31.550065

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


















# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #812 🌌 rarity:0.09 ⏱️ 0:02:29.017556

📜 3 sessions
🦄 🦄 🦄
🦄 🦄 🦄
🦄 🦄 🦄
Rarity: 0.09 🌌

# [spaceword.org](spaceword.org) 🧩 2026-08-21 🏁 score 2173 ranked 4.3% 14/328 ⏱️ 0:42:40.557229

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 14/328

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ S E C _ _ _   
      _ _ _ _ _ _ A _ _ _   
      _ _ _ _ Q _ L _ _ _   
      _ _ _ _ U _ Z _ _ _   
      _ _ _ _ A D O _ _ _   
      _ _ _ _ F O N _ _ _   
      _ _ _ _ F _ E _ _ _   
      _ _ _ _ E X _ _ _ _   
      _ _ _ _ D U E _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #658 🥳 44 ⏱️ 0:00:53.765102

🤔 44 attempts
📜 1 sessions

    @        [     0] &-teken 
    @+199650 [199650] lijk    q0  ? ␅
    @+199650 [199650] lijk    q1  ? after
    @+199650 [199650] lijk    q2  ? ␅
    @+199650 [199650] lijk    q3  ? after
    @+249572 [249572] opi     q6  ? ␅
    @+249572 [249572] opi     q7  ? after
    @+274493 [274493] prop    q8  ? ␅
    @+274493 [274493] prop    q9  ? after
    @+277397 [277397] radio   q14 ? ␅
    @+277397 [277397] radio   q15 ? after
    @+277703 [277703] radjes  q22 ? ␅
    @+277703 [277703] radjes  q23 ? after
    @+277844 [277844] rail    q24 ? ␅
    @+277844 [277844] rail    q25 ? after
    @+277844 [277844] rail    q26 ? ␅
    @+277844 [277844] rail    q27 ? after
    @+277877 [277877] raio    q32 ? ␅
    @+277877 [277877] raio    q33 ? after
    @+277892 [277892] rak     q34 ? ␅
    @+277892 [277892] rak     q35 ? after
    @+277894 [277894] rakel   q36 ? ␅
    @+277894 [277894] rakel   q37 ? after
    @+277902 [277902] rakelt  q38 ? ␅
    @+277902 [277902] rakelt  q39 ? after
    @+277904 [277904] raken   q40 ? ␅
    @+277904 [277904] raken   q41 ? iit
    @+277904 [277904] raken   q42 ? ␅
    @+277904 [277904] raken   q43 ? it
    @+277904 [277904] raken   done. it
    @+277909 [277909] raket   q29 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1125 🥳 32 ⏱️ 0:01:46.858789

🤔 32 attempts
📜 1 sessions

    @        [     0] aa      
    @+98147  [ 98147] mac     q0  ? ␅
    @+98147  [ 98147] mac     q1  ? after
    @+98147  [ 98147] mac     q2  ? ␅
    @+98147  [ 98147] mac     q3  ? after
    @+147311 [147311] rho     q4  ? ␅
    @+147311 [147311] rho     q5  ? after
    @+171911 [171911] tag     q6  ? ␅
    @+171911 [171911] tag     q7  ? after
    @+181996 [181996] un      q8  ? ␅
    @+181996 [181996] un      q9  ? after
    @+189258 [189258] vicar   q10 ? ␅
    @+189258 [189258] vicar   q11 ? after
    @+191038 [191038] walk    q14 ? ␅
    @+191038 [191038] walk    q15 ? after
    @+191901 [191901] we      q16 ? ␅
    @+191901 [191901] we      q17 ? after
    @+192136 [192136] wee     q20 ? ␅
    @+192136 [192136] wee     q21 ? after
    @+192157 [192157] week    q26 ? ␅
    @+192157 [192157] week    q27 ? after
    @+192160 [192160] weekend q30 ? ␅
    @+192160 [192160] weekend q31 ? it
    @+192160 [192160] weekend done. it
    @+192171 [192171] weeks   q28 ? ␅
    @+192171 [192171] weeks   q29 ? before
    @+192185 [192185] weep    q24 ? ␅
    @+192185 [192185] weep    q25 ? before
    @+192234 [192234] weight  q22 ? ␅
    @+192234 [192234] weight  q23 ? before
    @+192371 [192371] wen     q19 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1551 🥳 6 ⏱️ 0:01:43.293338

📜 1 sessions
💰 score: 15

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:7419
    ⬜⬜⬜⬜⬜ tried:NENES n n n n n remain:1175
    ⬜⬜⬜⬜⬜ tried:OVOLO n n n n n remain:339
    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:95
    ⬜⬜⬜⬜⬜ tried:CRWTH n n n n n remain:24
    🟩⬜⬜⬜🟩 tried:PYGMY Y n n n Y remain:3

    Undos used: 4

      3 words remaining
    x 5 unused letters
    = 15 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1694 🥳 20 ⏱️ 0:04:40.965569

📜 1 sessions
💰 score: 9600

    4/6
    ANISE ⬜🟨⬜⬜🟨
    TONER ⬜🟨🟨🟨⬜
    LEMON ⬜🟩🟩🟩🟩
    DEMON 🟩🟩🟩🟩🟩
    4/6
    DEMON ⬜🟩⬜⬜🟨
    RENTS 🟨🟩🟨⬜⬜
    NERVY 🟩🟩🟩🟩⬜
    NERVE 🟩🟩🟩🟩🟩
    5/6
    NERVE ⬜⬜🟨⬜⬜
    ABORT ⬜⬜⬜🟨🟨
    RUSTY 🟨⬜⬜🟨⬜
    TRICK 🟩🟩🟩⬜⬜
    TRILL 🟩🟩🟩🟩🟩
    5/6
    TRILL ⬜⬜⬜⬜⬜
    KANES ⬜⬜🟩⬜⬜
    DUNCH ⬜🟩🟩⬜⬜
    MUNGO ⬜🟩🟩⬜⬜
    BUNNY 🟩🟩🟩🟩🟩
    Final 2/2
    GAWPS ⬜⬜🟩⬜🟨
    SOWER 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1671 🥳 score:27 ⏱️ 0:03:07.302636

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SPOUT attempts:8 score:8
2. BRAID attempts:4 score:4
3. FLASH attempts:9 score:9
4. GUSTY attempts:6 score:6

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1671 🥳 score:63 ⏱️ 0:01:44.353272

📜 1 sessions

Octordle Classic

1. BELLY attempts:12 score:12
2. ELITE attempts:7 score:7
3. RISKY attempts:3 score:3
4. SWUNG attempts:5 score:5
5. RABID attempts:11 score:11
6. EXULT attempts:6 score:6
7. ENVOY attempts:9 score:9
8. PRIOR attempts:10 score:10

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1651 🥳 score:40 ⏱️ 0:03:21.949441

📜 1 sessions

Sedecordle Classic sedecordle.com

1. VALET attempts:3 score:0
2. OUNCE attempts:8 score:3
3. SPINY attempts:9 score:0
4. SAUCY attempts:7 score:9
5. STUFF attempts:10 score:1
6. CLASH attempts:11 score:0
7. BLAME attempts:5 score:0
8. CHAFF attempts:6 score:5
9. GRANT attempts:12 score:1
10. ESTER attempts:13 score:2
11. DELAY attempts:14 score:1
12. SOLID attempts:19 score:4
13. QUART attempts:15 score:1
14. SHEEP attempts:16 score:5
15. LUNAR attempts:17 score:1
16. HELIX attempts:18 score:7

# [squareword.org](squareword.org) 🧩 #1664 🥳 9 ⏱️ 0:02:39.604374

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟨 🟩 🟨 🟨 🟩
    🟨 🟨 🟨 🟩 🟨
    🟨 🟨 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C L A S P
    R A D I O
    E R O D E
    E G R E T
    D E E D S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1601 🥳 558 ⏱️ 0:18:58.056132

🤔 559 attempts
📜 1 sessions
🫧 47 chat sessions
⁉️ 244 chat prompts
🤖 2 nemotron-3.5-lightning:latest replies
🤖 6 qwen3.5:9b replies
🤖 13 muse-glimmer:latest replies
🤖 130 ornith-1.5:35b replies
🤖 54 qwen3:8b replies
🤖 7 gemma4:12b replies
🤖 31 dolphin3:latest replies
🔥   3 🥵   7 😎  63 🥶 470 🧊  15

      $1 #559 passive           100.00°C 🥳 1000‰ ~544 used:0   [543]  source:nemotron
      $2 #443 reactive           49.38°C 🔥  998‰   ~3 used:84  [2]    source:qwen3:8b
      $3 #232 active             43.62°C 🔥  995‰  ~26 used:179 [25]   source:ornith  
      $4 #282 aggressive         42.29°C 🔥  993‰  ~25 used:128 [24]   source:ornith  
      $5 #520 reflexive          36.35°C 🥵  963‰   ~4 used:9   [3]    source:ornith  
      $6 #312 proactive          35.91°C 🥵  960‰  ~53 used:29  [52]   source:ornith  
      $7 #446 adaptive           35.72°C 🥵  955‰   ~5 used:10  [4]    source:qwen3:8b
      $8 #524 unthinking         35.62°C 🥵  953‰   ~2 used:8   [1]    source:ornith  
      $9 #283 assertive          34.56°C 🥵  930‰  ~23 used:11  [22]   source:ornith  
     $10 #545 inattentive        34.43°C 🥵  924‰   ~1 used:5   [0]    source:muse    
     $11 #432 anticipatory       34.05°C 🥵  916‰  ~24 used:11  [23]   source:qwen3:8b
     $12 #420 coercive           32.93°C 😎  873‰  ~27 used:2   [26]   source:qwen3:8b
     $75 #521 conditioned        26.07°C 🥶        ~83 used:0   [82]   source:ornith  
    $545 #362 attacker           -0.13°C 🧊       ~545 used:0   [544]  source:gemma4  

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1634 🥳 297 ⏱️ 0:02:31.550065

🤔 298 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 51 chat prompts
🤖 51 ornith-1.5:35b replies
🔥   4 🥵  13 😎  46 🥶 133 🧊 101

      $1 #298 salon            100.00°C 🥳 1000‰ ~197 used:0  [196]  source:ornith
      $2 #288 expo              58.27°C 🔥  997‰   ~8 used:13 [7]    source:ornith
      $3 #232 exposition        49.10°C 🔥  996‰  ~12 used:23 [11]   source:ornith
      $4 #294 foire             47.64°C 🔥  995‰   ~1 used:1  [0]    source:ornith
      $5 #280 festival          40.23°C 🔥  990‰   ~2 used:9  [1]    source:ornith
      $6 #262 manifestation     39.51°C 🥵  989‰  ~15 used:6  [14]   source:ornith
      $7 #295 conférence        36.93°C 🥵  981‰   ~3 used:0  [2]    source:ornith
      $8 #236 trophée           36.62°C 🥵  978‰  ~14 used:5  [13]   source:ornith
      $9 #237 vitrine           35.73°C 🥵  976‰  ~13 used:3  [12]   source:ornith
     $10 #282 fête              34.92°C 🥵  972‰   ~9 used:2  [8]    source:ornith
     $11 #244 gala              34.36°C 🥵  971‰  ~10 used:2  [9]    source:ornith
     $19 #200 antiquaire        27.44°C 😎  896‰  ~61 used:3  [60]   source:ornith
     $65 #229 sellerie          16.03°C 🥶        ~68 used:0  [67]   source:ornith
    $198  #77 expertise         -0.02°C 🧊       ~198 used:0  [197]  source:ornith
