# 2026-08-27

- 🔗 spaceword.org 🧩 2026-08-26 🏁 score 2168 ranked 45.0% 145/322 ⏱️ 1:37:14.899555
- 🔗 wordgrid 🧩 #817 🟪 rarity:0.19 ⏱️ 0:24:09.564372
- 🔗 alfagok.diginaut.net 🧩 #663 🥳 40 ⏱️ 0:00:46.091135
- 🔗 alphaguess.com 🧩 #1130 🥳 36 ⏱️ 0:00:34.185907
- 🔗 dontwordle.com 🧩 #1556 😳 6 ⏱️ 0:01:05.053377
- 🔗 dictionary.com hurdle 🧩 #1699 🥳 18 ⏱️ 0:03:01.924636
- 🔗 Quordle Classic 🧩 #1676 🥳 score:23 ⏱️ 0:01:45.463385
- 🔗 Octordle Classic 🧩 #1676 🥳 score:58 ⏱️ 0:02:00.823920
- 🔗 Sedecordle Classic 🧩 #1656 🥳 score:51 ⏱️ 0:02:19.630498
- 🔗 squareword.org 🧩 #1669 🥳 8 ⏱️ 0:02:11.000306
- 🔗 cemantle.certitudes.org 🧩 #1606 🥳 435 ⏱️ 0:26:10.649670
- 🔗 cemantix.certitudes.org 🧩 #1639 🥳 220 ⏱️ 0:02:59.245039

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























# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #817 🟪 rarity:0.19 ⏱️ 0:24:09.564372

📜 3 sessions
🌌 🌌 🌌
🌌 🦄 🌌
🦄 🦄 🌌
Rarity: 0.19 🟪

# [spaceword.org](spaceword.org) 🧩 2026-08-26 🏁 score 2168 ranked 45.0% 145/322 ⏱️ 1:37:14.899555

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 145/322

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ S A D E _ _ _   
      _ _ _ U _ I _ _ _ _   
      _ _ _ Q _ O R _ _ _   
      _ _ _ _ _ X I _ _ _   
      _ _ _ _ J A B _ _ _   
      _ _ _ _ _ N E _ _ _   
      _ _ _ P R E Y _ _ _   
      _ _ _ _ _ _ E _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #663 🥳 40 ⏱️ 0:00:46.091135

🤔 40 attempts
📜 1 sessions

    @       [    0] &-teken    
    @+8646  [ 8646] af         q12 ? ␅
    @+8646  [ 8646] af         q13 ? after
    @+12392 [12392] afsplits   q16 ? ␅
    @+12392 [12392] afsplits   q17 ? after
    @+14270 [14270] agribulk   q18 ? ␅
    @+14270 [14270] agribulk   q19 ? after
    @+15195 [15195] alge       q20 ? ␅
    @+15195 [15195] alge       q21 ? after
    @+15376 [15376] alle       q24 ? ␅
    @+15376 [15376] alle       q25 ? after
    @+15387 [15387] alleen     q28 ? ␅
    @+15387 [15387] alleen     q29 ? after
    @+15422 [15422] allegaar   q30 ? ␅
    @+15422 [15422] allegaar   q31 ? after
    @+15430 [15430] allegretto q36 ? ␅
    @+15430 [15430] allegretto q37 ? after
    @+15433 [15433] allemaal   q38 ? ␅
    @+15433 [15433] allemaal   q39 ? it
    @+15433 [15433] allemaal   done. it
    @+15436 [15436] alleman    q32 ? ␅
    @+15436 [15436] alleman    q33 ? before
    @+15453 [15453] aller      q26 ? ␅
    @+15453 [15453] aller      q27 ? before
    @+15669 [15669] allo       q22 ? ␅
    @+15669 [15669] allo       q23 ? before
    @+16147 [16147] am         q14 ? ␅
    @+16147 [16147] am         q15 ? before
    @+24880 [24880] bad        q10 ? ␅
    @+24880 [24880] bad        q11 ? before
    @+49808 [49808] boks       q9  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1130 🥳 36 ⏱️ 0:00:34.185907

🤔 36 attempts
📜 1 sessions

    @       [    0] aa       
    @+11763 [11763] back     q10 ? ␅
    @+11763 [11763] back     q11 ? after
    @+13801 [13801] be       q14 ? ␅
    @+13801 [13801] be       q15 ? after
    @+14164 [14164] bed      q20 ? ␅
    @+14164 [14164] bed      q21 ? after
    @+14390 [14390] bee      q22 ? ␅
    @+14390 [14390] bee      q23 ? after
    @+14471 [14471] beet     q26 ? ␅
    @+14471 [14471] beet     q27 ? after
    @+14512 [14512] beflower q28 ? ␅
    @+14512 [14512] beflower q29 ? after
    @+14520 [14520] befool   q32 ? ␅
    @+14520 [14520] befool   q33 ? after
    @+14524 [14524] before   q34 ? ␅
    @+14524 [14524] before   q35 ? it
    @+14524 [14524] before   done. it
    @+14527 [14527] befoul   q30 ? ␅
    @+14527 [14527] befoul   q31 ? before
    @+14553 [14553] beg      q24 ? ␅
    @+14553 [14553] beg      q25 ? before
    @+14778 [14778] bel      q18 ? ␅
    @+14778 [14778] bel      q19 ? before
    @+15757 [15757] bewrap   q16 ? ␅
    @+15757 [15757] bewrap   q17 ? before
    @+17714 [17714] blind    q12 ? ␅
    @+17714 [17714] blind    q13 ? before
    @+23680 [23680] camp     q7  ? bb
    @+23680 [23680] camp     q8  ? ␅
    @+23680 [23680] camp     q9  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1556 😳 6 ⏱️ 0:01:05.053377

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:TOOTS n n n n n remain:3618
    ⬜⬜⬜⬜⬜ tried:WHIFF n n n n n remain:1661
    ⬜⬜⬜⬜⬜ tried:PUPPY n n n n n remain:665
    ⬜⬜⬜⬜⬜ tried:GRRRL n n n n n remain:134
    ⬜⬜🟩⬜🟩 tried:BENNE n n Y n Y remain:3
    🟩🟩🟩🟩🟩 tried:DANCE Y Y Y Y Y remain:0

    Undos used: 2

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1699 🥳 18 ⏱️ 0:03:01.924636

📜 1 sessions
💰 score: 9800

    5/6
    SNARE ⬜⬜⬜🟨🟨
    DOTER ⬜⬜🟨🟨🟨
    CREPT ⬜🟨🟨⬜🟨
    BERTH ⬜🟩🟩🟩🟨
    HERTZ 🟩🟩🟩🟩🟩
    5/6
    HERTZ ⬜⬜🟨⬜⬜
    SOLAR ⬜⬜⬜🟨🟨
    DRAIN ⬜🟩🟩🟩🟩
    GRAIN ⬜🟩🟩🟩🟩
    BRAIN 🟩🟩🟩🟩🟩
    3/6
    BRAIN 🟨⬜⬜⬜⬜
    PUBES ⬜⬜🟩🟩⬜
    EMBED 🟩🟩🟩🟩🟩
    4/6
    EMBED 🟨⬜⬜⬜🟨
    SADHE ⬜⬜🟩⬜🟩
    NUDIE ⬜⬜🟩🟩🟩
    OLDIE 🟩🟩🟩🟩🟩
    Final 1/2
    BEGUN 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1676 🥳 score:23 ⏱️ 0:01:45.463385

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. SHEEN attempts:6 score:6
2. TRICE attempts:8 score:8
3. WAGON attempts:5 score:5
4. BEVEL attempts:4 score:4

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1676 🥳 score:58 ⏱️ 0:02:00.823920

📜 2 sessions

Octordle Classic

1. DREAD attempts:8 score:8
2. SIGMA attempts:3 score:3
3. EXTRA attempts:5 score:5
4. SCORN attempts:9 score:9
5. SHOOK attempts:12 score:12
6. RIGID attempts:4 score:4
7. OFTEN attempts:6 score:6
8. BRASS attempts:11 score:11

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1656 🥳 score:51 ⏱️ 0:02:19.630498

📜 1 sessions

Sedecordle Classic sedecordle.com

1. VITAL attempts:14 score:1
2. BEGAN attempts:15 score:4
3. NINTH attempts:7 score:0
4. MELEE attempts:4 score:7
5. DINER attempts:6 score:0
6. CANAL attempts:13 score:6
7. SUPER attempts:11 score:1
8. CLEFT attempts:12 score:1
9. GUARD attempts:9 score:0
10. WELCH attempts:16 score:9
11. ARMOR attempts:8 score:0
12. GOOFY attempts:17 score:8
13. ENEMA attempts:5 score:0
14. PAYEE attempts:10 score:5
15. WHIFF attempts:18 score:1
16. ROOST attempts:18 score:8

# [squareword.org](squareword.org) 🧩 #1669 🥳 8 ⏱️ 0:02:11.000306

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟨 🟩 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B O A S T
    A L T E R
    G I R L Y
    E V I L S
    L E A S T

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1606 🥳 435 ⏱️ 0:26:10.649670

🤔 436 attempts
📜 2 sessions
🫧 32 chat sessions
⁉️ 175 chat prompts
🤖 46 llama3.2:latest replies
🤖 97 dolphin3:latest replies
🤖 10 gemma4:12b replies
🤖 22 ornith-1.5:35b replies
😱   1 🔥   2 🥵  23 😎  86 🥶 314 🧊   9

      $1 #436 tear             100.00°C 🥳 1000‰ ~427 used:0   [426]  source:llama3  
      $2 #244 tearing           69.61°C 😱  999‰   ~1 used:164 [0]    source:dolphin3
      $3 #283 torn              54.74°C 🔥  998‰  ~17 used:45  [16]   source:dolphin3
      $4 #247 ripping           46.08°C 🔥  995‰  ~18 used:51  [17]   source:dolphin3
      $5 #313 cracking          38.52°C 🥵  988‰  ~15 used:4   [14]   source:llama3  
      $6 #401 cracked           38.18°C 🥵  987‰   ~3 used:3   [2]    source:llama3  
      $7 #327 damage            37.64°C 🥵  986‰   ~4 used:3   [3]    source:llama3  
      $8 #277 rend              36.13°C 🥵  972‰  ~16 used:4   [15]   source:gemma4  
      $9 #284 rupture           35.95°C 🥵  971‰   ~5 used:3   [4]    source:dolphin3
     $10 #364 raveling          35.49°C 🥵  967‰   ~6 used:3   [5]    source:llama3  
     $11 #396 scrape            34.98°C 🥵  965‰   ~7 used:3   [6]    source:llama3  
     $28 #299 shredded          30.91°C 😎  895‰  ~20 used:0   [19]   source:dolphin3
    $114  #55 suffocate         22.17°C 🥶       ~113 used:8   [112]  source:dolphin3
    $428  #97 execute           -0.32°C 🧊       ~428 used:0   [427]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1639 🥳 220 ⏱️ 0:02:59.245039

🤔 221 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 47 chat prompts
🤖 47 dolphin3:latest replies
🔥   2 🥵  18 😎  61 🥶 120 🧊  19

      $1 #221 infraction       100.00°C 🥳 1000‰ ~202 used:0  [201]  source:dolphin3
      $2 #220 délit             63.25°C 😱  999‰   ~1 used:0  [0]    source:dolphin3
      $3 #217 contravention     62.37°C 🔥  998‰   ~2 used:1  [1]    source:dolphin3
      $4 #193 obligation        43.06°C 🥵  979‰  ~15 used:7  [14]   source:dolphin3
      $5 #148 procédure         42.34°C 🥵  976‰  ~74 used:15 [73]   source:dolphin3
      $6 #119 code              41.56°C 🥵  972‰  ~73 used:12 [72]   source:dolphin3
      $7 #118 législation       41.30°C 🥵  971‰  ~14 used:5  [13]   source:dolphin3
      $8 #169 prescription      41.24°C 🥵  969‰  ~13 used:3  [12]   source:dolphin3
      $9 #190 juridiction       40.90°C 🥵  967‰   ~5 used:2  [4]    source:dolphin3
     $10 #219 juge              40.78°C 🥵  966‰   ~3 used:0  [2]    source:dolphin3
     $11 #175 réglementation    39.60°C 🥵  957‰   ~6 used:2  [5]    source:dolphin3
     $22 #212 recours           35.40°C 😎  898‰  ~16 used:0  [15]   source:dolphin3
     $83  #66 assurance         20.89°C 🥶        ~87 used:0  [86]   source:dolphin3
    $203  #45 mécanicien        -0.07°C 🧊       ~203 used:0  [202]  source:dolphin3
