# 2026-08-08

- 🔗 spaceword.org 🧩 2026-08-07 🏁 score 2160 ranked 54.2% 179/330 ⏱️ 0:04:15.970897
- 🔗 wordgrid 🧩 #798 🟪 rarity:0.17 ⏱️ 0:02:32.208054
- 🔗 alfagok.diginaut.net 🧩 #644 🥳 46 ⏱️ 0:00:58.119565
- 🔗 alphaguess.com 🧩 #1111 🥳 24 ⏱️ 0:00:34.963742
- 🔗 dontwordle.com 🧩 #1537 🥳 6 ⏱️ 0:01:25.764215
- 🔗 dictionary.com hurdle 🧩 #1680 🥳 18 ⏱️ 0:04:15.674542
- 🔗 Quordle Classic 🧩 #1657 🥳 score:24 ⏱️ 0:01:22.595705
- 🔗 Octordle Classic 🧩 #1657 🥳 score:56 ⏱️ 0:03:27.645421
- 🔗 Sedecordle Classic 🧩 #1637 🥳 score:47 ⏱️ 0:03:25.203599
- 🔗 squareword.org 🧩 #1650 🥳 7 ⏱️ 0:01:54.661454
- 🔗 cemantle.certitudes.org 🧩 #1587 🥳 108 ⏱️ 0:01:53.375352
- 🔗 cemantix.certitudes.org 🧩 #1620 🥳 291 ⏱️ 0:05:22.986378

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




# [spaceword.org](spaceword.org) 🧩 2026-08-07 🏁 score 2160 ranked 54.2% 179/330 ⏱️ 0:04:15.970897

📜 2 sessions
- tiles: 21/21
- score: 2160 bonus: +60
- rank: 179/330

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ H _ _ _   
      _ _ _ _ _ _ A _ Z _   
      _ W _ U R A N I A _   
      _ E _ _ U _ S _ X _   
      _ T A B B I E D _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #798 🟪 rarity:0.17 ⏱️ 0:02:32.208054

📜 2 sessions
🦄 🦄 🦄
🌌 🌌 🦄
🦄 🌌 🦄
Rarity: 0.17 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #644 🥳 46 ⏱️ 0:00:58.119565

🤔 46 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+199549 [199549] lij       q0  ? ␅
    @+199549 [199549] lij       q1  ? after
    @+199549 [199549] lij       q2  ? ␅
    @+199549 [199549] lij       q3  ? after
    @+199549 [199549] lij       q4  ? ␅
    @+199549 [199549] lij       q5  ? after
    @+299515 [299515] schrok    q6  ? ␅
    @+299515 [299515] schrok    q7  ? after
    @+311758 [311758] spier     q12 ? ␅
    @+311758 [311758] spier     q13 ? after
    @+314751 [314751] staats    q16 ? ␅
    @+314751 [314751] staats    q17 ? after
    @+316239 [316239] standaard q18 ? ␅
    @+316239 [316239] standaard q19 ? after
    @+316881 [316881] stat      q20 ? ␅
    @+316881 [316881] stat      q21 ? after
    @+317324 [317324] steen     q22 ? ␅
    @+317324 [317324] steen     q23 ? after
    @+317639 [317639] steg      q26 ? ␅
    @+317639 [317639] steg      q27 ? after
    @+317739 [317739] stek      q28 ? ␅
    @+317739 [317739] stek      q29 ? after
    @+317815 [317815] stel      q30 ? ␅
    @+317815 [317815] stel      q31 ? after
    @+317825 [317825] stele     q36 ? ␅
    @+317825 [317825] stele     q37 ? after
    @+317826 [317826] stelen    q44 ? ␅
    @+317826 [317826] stelen    q45 ? it
    @+317826 [317826] stelen    done. it
    @+317827 [317827] stelend   q43 ? before

# [alphaguess.com](alphaguess.com) 🧩 #1111 🥳 24 ⏱️ 0:00:34.963742

🤔 24 attempts
📜 1 sessions

    @       [    0] aa       
    @+1     [    1] aah      
    @+2     [    2] aahed    
    @+3     [    3] aahing   
    @+11763 [11763] back     q6  ? ␅
    @+11763 [11763] back     q7  ? after
    @+17714 [17714] blind    q8  ? ␅
    @+17714 [17714] blind    q9  ? after
    @+20685 [20685] brill    q10 ? ␅
    @+20685 [20685] brill    q11 ? after
    @+22025 [22025] bur      q12 ? ␅
    @+22025 [22025] bur      q13 ? after
    @+22155 [22155] burl     q18 ? ␅
    @+22155 [22155] burl     q19 ? after
    @+22182 [22182] burn     q22 ? ␅
    @+22182 [22182] burn     q23 ? it
    @+22182 [22182] burn     done. it
    @+22221 [22221] burr     q20 ? ␅
    @+22221 [22221] burr     q21 ? before
    @+22286 [22286] bus      q16 ? ␅
    @+22286 [22286] bus      q17 ? before
    @+22853 [22853] cachalot q14 ? ␅
    @+22853 [22853] cachalot q15 ? before
    @+23680 [23680] camp     q4  ? ␅
    @+23680 [23680] camp     q5  ? before
    @+47378 [47378] dis      q2  ? ␅
    @+47378 [47378] dis      q3  ? before
    @+98147 [98147] mac      q0  ? ␅
    @+98147 [98147] mac      q1  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1537 🥳 6 ⏱️ 0:01:25.764215

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:PAPAW n n n n n remain:5916
    ⬜⬜⬜⬜⬜ tried:EFFED n n n n n remain:2037
    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:704
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:240
    ⬜🟨⬜⬜⬜ tried:CIVIC n m n n n remain:22
    🟨⬜🟩⬜⬜ tried:SHIMS m n Y n n remain:1

    Undos used: 3

      1 words remaining
    x 8 unused letters
    = 8 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1680 🥳 18 ⏱️ 0:04:15.674542

📜 1 sessions
💰 score: 9800

    3/6
    AROSE 🟨⬜🟨🟩⬜
    FATSO ⬜🟨🟨🟩🟨
    BOAST 🟩🟩🟩🟩🟩
    4/6
    BOAST ⬜⬜⬜⬜⬜
    RINDY ⬜🟨🟨⬜⬜
    INGLE 🟨🟨🟨⬜⬜
    CUING 🟩🟩🟩🟩🟩
    5/6
    CUING ⬜⬜⬜🟨⬜
    NEARS 🟨⬜🟨⬜⬜
    MONAD ⬜⬜🟩🟨🟨
    BUMPH ⬜⬜⬜⬜⬜
    DANDY 🟩🟩🟩🟩🟩
    4/6
    DANDY ⬜⬜🟨⬜⬜
    RISEN ⬜🟩⬜🟨🟨
    NICHE 🟩🟩🟨⬜🟩
    NIECE 🟩🟩🟩🟩🟩
    Final 2/2
    FORBY ⬜🟩⬜🟩🟩
    HOBBY 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1657 🥳 score:24 ⏱️ 0:01:22.595705

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. FUROR attempts:7 score:7
2. BUGLE attempts:5 score:5
3. REUSE attempts:4 score:4
4. SCOOP attempts:8 score:8

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1657 🥳 score:56 ⏱️ 0:03:27.645421

📜 1 sessions

Octordle Classic

1. STOKE attempts:10 score:10
2. RETRY attempts:6 score:6
3. GUPPY attempts:13 score:13
4. LAPEL attempts:7 score:7
5. SPOIL attempts:3 score:3
6. HARPY attempts:5 score:5
7. SLOTH attempts:4 score:4
8. HORDE attempts:8 score:8

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1637 🥳 score:47 ⏱️ 0:03:25.203599

📜 1 sessions

Sedecordle Classic sedecordle.com

1. ROUTE attempts:18 score:1
2. FIELD attempts:8 score:8
3. NYLON attempts:6 score:0
4. WALTZ attempts:12 score:6
5. GLORY attempts:3 score:0
6. CRAFT attempts:7 score:3
7. REFIT attempts:9 score:0
8. SMELT attempts:10 score:9
9. WRITE attempts:13 score:1
10. SHARK attempts:11 score:3
11. JEWEL attempts:14 score:1
12. FLAIL attempts:18 score:4
13. SMOKE attempts:15 score:1
14. MIRTH attempts:16 score:5
15. PENNY attempts:5 score:0
16. VERSE attempts:17 score:5

# [squareword.org](squareword.org) 🧩 #1650 🥳 7 ⏱️ 0:01:54.661454

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S L E E T
    C A L V E
    O R D E R
    O V E N S
    P A R S E

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1587 🥳 108 ⏱️ 0:01:53.375352

🤔 109 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 25 chat prompts
🤖 25 dolphin3:latest replies
🥵  6 😎 12 🥶 86 🧊  4

      $1 #109 clip           100.00°C 🥳 1000‰ ~105 used:0  [104]  source:dolphin3
      $2   #3 camera          37.88°C 🥵  985‰  ~18 used:24 [17]   source:dolphin3
      $3  #56 photo           35.17°C 🥵  974‰  ~17 used:13 [16]   source:dolphin3
      $4  #26 film            33.40°C 🥵  961‰   ~3 used:10 [2]    source:dolphin3
      $5  #34 reel            33.11°C 🥵  957‰   ~1 used:8  [0]    source:dolphin3
      $6  #42 slide           32.34°C 🥵  950‰   ~4 used:10 [3]    source:dolphin3
      $7  #13 photograph      31.37°C 🥵  935‰   ~2 used:8  [1]    source:dolphin3
      $8  #93 screen          28.25°C 😎  856‰   ~5 used:0  [4]    source:dolphin3
      $9  #15 flash           26.13°C 😎  741‰   ~6 used:0  [5]    source:dolphin3
     $10  #36 frame           26.12°C 😎  739‰   ~7 used:0  [6]    source:dolphin3
     $11  #37 projector       25.50°C 😎  698‰   ~8 used:0  [7]    source:dolphin3
     $12  #97 flashgun        25.43°C 😎  693‰   ~9 used:0  [8]    source:dolphin3
     $20  #83 enlarger        20.78°C 🥶        ~19 used:0  [18]   source:dolphin3
    $106  #81 contact         -1.18°C 🧊       ~106 used:0  [105]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1620 🥳 291 ⏱️ 0:05:22.986378

🤔 292 attempts
📜 1 sessions
🫧 15 chat sessions
⁉️ 69 chat prompts
🤖 69 dolphin3:latest replies
🔥   2 🥵  17 😎  28 🥶 186 🧊  58

      $1 #292 honteux          100.00°C 🥳 1000‰ ~234 used:0  [233]  source:dolphin3
      $2 #208 indigne           63.12°C 🔥  997‰  ~12 used:29 [11]   source:dolphin3
      $3 #215 indigner          58.40°C 🔥  996‰  ~11 used:25 [10]   source:dolphin3
      $4 #284 déshonorant       53.01°C 🥵  987‰   ~1 used:1  [0]    source:dolphin3
      $5 #210 indécent          51.92°C 🥵  982‰  ~18 used:7  [17]   source:dolphin3
      $6 #260 infamie           50.78°C 🥵  977‰   ~5 used:2  [4]    source:dolphin3
      $7 #187 inadmissible      50.25°C 🥵  971‰  ~19 used:7  [18]   source:dolphin3
      $8 #216 indécence         49.99°C 🥵  968‰  ~13 used:3  [12]   source:dolphin3
      $9 #245 mépris            49.66°C 🥵  966‰   ~6 used:2  [5]    source:dolphin3
     $10 #259 impudence         48.29°C 🥵  960‰   ~2 used:1  [1]    source:dolphin3
     $11 #190 insupportable     47.63°C 🥵  955‰  ~16 used:5  [15]   source:dolphin3
     $20 #235 injustement       43.95°C 😎  899‰  ~10 used:2  [9]    source:dolphin3
     $50 #146 crime             31.09°C 🥶        ~63 used:1  [62]   source:dolphin3
    $235  #98 cornemuse         -0.14°C 🧊       ~235 used:0  [234]  source:dolphin3
