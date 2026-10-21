# 2026-10-22

- 🔗 spaceword.org 🧩 2026-10-21 🏁 score 2168 ranked 39.9% 127/318 ⏱️ 0:02:24.349416
- 🔗 wordgrid 🧩 #873 🟪 rarity:0.14 ⏱️ 0:02:48.042436
- 🔗 alfagok.diginaut.net 🧩 #719 🥳 30 ⏱️ 0:00:39.907106
- 🔗 alphaguess.com 🧩 #1186 🥳 24 ⏱️ 0:00:41.708422
- 🔗 dontwordle.com 🧩 #1612 🥳 6 ⏱️ 0:01:37.863030
- 🔗 dictionary.com hurdle 🧩 #1755 🥳 22 ⏱️ 0:05:25.995578
- 🔗 Quordle Classic 🧩 #1732 🥳 score:20 ⏱️ 0:01:29.386769
- 🔗 Octordle Classic 🧩 #1732 🥳 score:53 ⏱️ 0:02:14.804923
- 🔗 Sedecordle Classic 🧩 #1712 🥳 score:39 ⏱️ 0:03:17.975347
- 🔗 squareword.org 🧩 #1725 🥳 8 ⏱️ 0:02:17.050366
- 🔗 cemantle.certitudes.org 🧩 #1662 🥳 115 ⏱️ 0:08:17.663565

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


















# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #873 🟪 rarity:0.14 ⏱️ 0:02:48.042436

📜 2 sessions
🌌 🌌 🦄
🌌 🌌 🦄
🌌 🦄 🦄
Rarity: 0.14 🟪

# [spaceword.org](spaceword.org) 🧩 2026-10-21 🏁 score 2168 ranked 39.9% 127/318 ⏱️ 0:02:24.349416

📜 2 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 127/318

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ Q U I Z _ _ _   
      _ _ _ _ _ _ E _ _ _   
      _ _ _ _ W _ C _ _ _   
      _ _ _ _ A _ H _ _ _   
      _ _ _ _ D _ I _ _ _   
      _ _ _ _ D O N _ _ _   
      _ _ _ A I D _ _ _ _   
      _ _ _ R E A M _ _ _   
      _ _ _ _ _ _ _ _ _ _   



# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #719 🥳 30 ⏱️ 0:00:39.907106

🤔 30 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+199631 [199631] lijk         q0  ? ␅
    @+199631 [199631] lijk         q1  ? after
    @+199631 [199631] lijk         q2  ? ␅
    @+199631 [199631] lijk         q3  ? after
    @+299529 [299529] schroot      q4  ? ␅
    @+299529 [299529] schroot      q5  ? after
    @+349311 [349311] vakantie     q6  ? ␅
    @+349311 [349311] vakantie     q7  ? after
    @+352875 [352875] ver          q10 ? ␅
    @+352875 [352875] ver          q11 ? after
    @+353957 [353957] verdeel      q18 ? ␅
    @+353957 [353957] verdeel      q19 ? after
    @+354010 [354010] verdelg      q26 ? ␅
    @+354010 [354010] verdelg      q27 ? after
    @+354047 [354047] verder       q28 ? ␅
    @+354047 [354047] verder       q29 ? it
    @+354047 [354047] verder       done. it
    @+354087 [354087] verdicht     q24 ? ␅
    @+354087 [354087] verdicht     q25 ? before
    @+354231 [354231] verdof       q22 ? ␅
    @+354231 [354231] verdof       q23 ? before
    @+354506 [354506] verduidelijk q20 ? ␅
    @+354506 [354506] verduidelijk q21 ? before
    @+355055 [355055] verg         q16 ? ␅
    @+355055 [355055] verg         q17 ? before
    @+358168 [358168] verluiert    q14 ? ␅
    @+358168 [358168] verluiert    q15 ? before
    @+363460 [363460] verzout      q12 ? ␅
    @+363460 [363460] verzout      q13 ? before
    @+374045 [374045] vrij         q9  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1186 🥳 24 ⏱️ 0:00:41.708422

🤔 24 attempts
📜 1 sessions

    @        [     0] aa       
    @+1      [     1] aah      
    @+2      [     2] aahed    
    @+3      [     3] aahing   
    @+98142  [ 98142] mac      q0  ? ␅
    @+98142  [ 98142] mac      q1  ? after
    @+147304 [147304] rho      q2  ? ␅
    @+147304 [147304] rho      q3  ? after
    @+171904 [171904] tag      q4  ? ␅
    @+171904 [171904] tag      q5  ? after
    @+181989 [181989] un       q6  ? ␅
    @+181989 [181989] un       q7  ? after
    @+189251 [189251] vicar    q8  ? ␅
    @+189251 [189251] vicar    q9  ? after
    @+190134 [190134] vivisect q14 ? ␅
    @+190134 [190134] vivisect q15 ? after
    @+190583 [190583] vouvray  q16 ? ␅
    @+190583 [190583] vouvray  q17 ? after
    @+190802 [190802] wae      q18 ? ␅
    @+190802 [190802] wae      q19 ? after
    @+190915 [190915] wail     q20 ? ␅
    @+190915 [190915] wail     q21 ? after
    @+190956 [190956] wait     q22 ? ␅
    @+190956 [190956] wait     q23 ? it
    @+190956 [190956] wait     done. it
    @+191031 [191031] walk     q12 ? ␅
    @+191031 [191031] walk     q13 ? before
    @+192855 [192855] whir     q10 ? ␅
    @+192855 [192855] whir     q11 ? before

# [dontwordle.com](dontwordle.com) 🧩 #1612 🥳 6 ⏱️ 0:01:37.863030

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today! I didn't even use a hint!

    ⬜⬜⬜⬜⬜ tried:MASSA n n n n n remain:3350
    ⬜⬜⬜⬜⬜ tried:DEKED n n n n n remain:988
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:439
    ⬜⬜⬜⬜⬜ tried:CIVIC n n n n n remain:124
    ⬜⬜🟨⬜⬜ tried:BUTUT n n m n n remain:17
    🟩⬜🟩⬜⬜ tried:THONG Y n Y n n remain:2

    Undos used: 4

      2 words remaining
    x 7 unused letters
    = 14 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1755 🥳 22 ⏱️ 0:05:25.995578

📜 2 sessions
💰 score: 9400

    5/6
    TOEAS ⬜🟩⬜⬜🟨
    NOISY ⬜🟩⬜🟩🟩
    BELCH ⬜⬜⬜⬜⬜
    GAMPS ⬜⬜🟨⬜🟨
    MOSSY 🟩🟩🟩🟩🟩
    6/6
    MOSSY ⬜⬜⬜⬜🟩
    INLAY ⬜⬜⬜🟨🟩
    DEARY ⬜⬜🟨⬜🟩
    TACKY 🟨🟩⬜⬜🟩
    UPBOW ⬜🟨⬜⬜⬜
    PATTY 🟩🟩🟩🟩🟩
    5/6
    PATTY ⬜⬜🟨🟩⬜
    VOLTE ⬜⬜⬜🟩🟩
    SHITE ⬜⬜🟩🟩🟩
    TRANQ 🟩🟩⬜⬜⬜
    ????? 🟩🟩🟩🟩🟩
    4/6
    TRITE ⬜⬜⬜⬜🟨
    ALOES 🟩🟨⬜🟩⬜
    ANGEL 🟩⬜⬜🟩🟨
    ABLED 🟩🟩🟩🟩🟩
    Final 2/2
    FUNKS ⬜🟩⬜⬜⬜
    QUELL 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1732 🥳 score:20 ⏱️ 0:01:29.386769

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. DECAL attempts:4 score:4
2. WIDTH attempts:3 score:3
3. WOKEN attempts:7 score:7
4. LEVER attempts:6 score:6

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1732 🥳 score:53 ⏱️ 0:02:14.804923

📜 1 sessions

Octordle Classic

1. TRUCE attempts:5 score:5
2. PEACH attempts:11 score:11
3. NOMAD attempts:8 score:8
4. CARGO attempts:9 score:9
5. LATCH attempts:6 score:6
6. QUOTH attempts:7 score:7
7. NASAL attempts:4 score:4
8. NOISE attempts:3 score:3

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1712 🥳 score:39 ⏱️ 0:03:17.975347

📜 1 sessions

Sedecordle Classic sedecordle.com

1. GIRTH attempts:15 score:1
2. FLAKE attempts:17 score:5
3. ANGST attempts:4 score:0
4. SCARY attempts:3 score:4
5. BEGAT attempts:5 score:0
6. QUEST attempts:14 score:5
7. VALID attempts:11 score:1
8. LATTE attempts:18 score:1
9. LINER attempts:12 score:1
10. DITTO attempts:10 score:2
11. RIGHT attempts:6 score:0
12. SMILE attempts:18 score:6
13. STEEP attempts:9 score:0
14. RIGOR attempts:7 score:9
15. LOVER attempts:13 score:1
16. WHERE attempts:8 score:3

# [squareword.org](squareword.org) 🧩 #1725 🥳 8 ⏱️ 0:02:17.050366

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    M E L D S
    A D I E U
    R E N A L
    S M E L L
    H A S T Y

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1662 🥳 115 ⏱️ 0:08:17.663565

🤔 116 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 21 chat prompts
🤖 21 gemma4:12b replies
😱  1 🔥  3 🥵 10 😎 15 🥶 82 🧊  4

      $1 #116 inspire         100.00°C 🥳 1000‰ ~112 used:0  [111]  source:gemma4
      $2 #114 motivate         73.75°C 😱  999‰   ~1 used:0  [0]    source:gemma4
      $3  #97 galvanize        60.95°C 🔥  996‰   ~4 used:3  [3]    source:gemma4
      $4 #115 encourage        57.45°C 🔥  994‰   ~2 used:0  [1]    source:gemma4
      $5 #110 energize         56.47°C 🔥  991‰   ~3 used:0  [2]    source:gemma4
      $6  #95 empower          53.87°C 🥵  987‰  ~10 used:2  [9]    source:gemma4
      $7 #101 propel           50.83°C 🥵  983‰   ~5 used:1  [4]    source:gemma4
      $8  #99 incite           49.85°C 🥵  979‰   ~6 used:1  [5]    source:gemma4
      $9  #28 inspiration      49.74°C 🥵  977‰  ~24 used:18 [23]   source:gemma4
     $10  #86 ignite           49.33°C 🥵  974‰  ~12 used:6  [11]   source:gemma4
     $11  #20 spark            48.27°C 🥵  965‰  ~23 used:14 [22]   source:gemma4
     $16  #39 motivation       37.59°C 😎  832‰  ~29 used:4  [28]   source:gemma4
     $31  #43 ambition         26.12°C 🥶        ~30 used:0  [29]   source:gemma4
    $113  #12 agent            -2.55°C 🧊       ~113 used:0  [112]  source:gemma4
