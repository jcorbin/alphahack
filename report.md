# 2026-08-15

- 🔗 wordgrid 🧩 #805 🟪 rarity:0.16 ⏱️ 0:02:22.872070
- 🔗 spaceword.org 🧩 2026-08-14 🏁 score 2168 ranked 34.5% 110/319 ⏱️ 0:20:50.308219
- 🔗 alfagok.diginaut.net 🧩 #651 🥳 30 ⏱️ 0:00:48.998009
- 🔗 alphaguess.com 🧩 #1118 🥳 30 ⏱️ 0:00:49.833583
- 🔗 dontwordle.com 🧩 #1544 😳 6 ⏱️ 0:02:13.735769
- 🔗 dictionary.com hurdle 🧩 #1687 🥳 19 ⏱️ 0:03:02.486149
- 🔗 Quordle Classic 🧩 #1664 🥳 score:20 ⏱️ 0:02:20.061678
- 🔗 Octordle Classic 🧩 #1664 🥳 score:57 ⏱️ 0:02:02.099090
- 🔗 Sedecordle Classic 🧩 #1644 🥳 score:43 ⏱️ 0:02:13.752479
- 🔗 squareword.org 🧩 #1657 🥳 7 ⏱️ 0:01:59.580716
- 🔗 cemantle.certitudes.org 🧩 #1594 🥳 316 ⏱️ 0:05:13.041862
- 🔗 cemantix.certitudes.org 🧩 #1627 🥳 371 ⏱️ 0:06:22.864969

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











# [spaceword.org](spaceword.org) 🧩 2026-08-14 🏁 score 2168 ranked 34.5% 110/319 ⏱️ 0:20:50.308219

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 110/319

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ N _ J _ _ _   
      _ _ _ L U R E _ _ _   
      _ _ _ _ C _ E _ _ _   
      _ _ _ C H I D _ _ _   
      _ _ _ O A R _ _ _ _   
      _ _ _ Z _ O _ _ _ _   
      _ _ _ I _ K _ _ _ _   
      _ _ _ E _ O _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [wordgrid](https://wordgrid.clevergoat.com/) 🧩 #805 🟪 rarity:0.16 ⏱️ 0:02:22.872070

📜 3 sessions
🦄 🦄 🦄
🌌 🌌 🦄
🦄 🌌 🌌
Rarity: 0.16 🟪


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #651 🥳 30 ⏱️ 0:00:48.998009

🤔 30 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+49812  [ 49812] boks         q6  ? ␅
    @+49812  [ 49812] boks         q7  ? after
    @+74715  [ 74715] dc           q8  ? ␅
    @+74715  [ 74715] dc           q9  ? after
    @+87173  [ 87173] draag        q10 ? ␅
    @+87173  [ 87173] draag        q11 ? after
    @+93388  [ 93388] eet          q12 ? ␅
    @+93388  [ 93388] eet          q13 ? after
    @+96524  [ 96524] energiek     q14 ? ␅
    @+96524  [ 96524] energiek     q15 ? after
    @+96941  [ 96941] enkel        q18 ? ␅
    @+96941  [ 96941] enkel        q19 ? after
    @+96956  [ 96956] enkele       q28 ? ␅
    @+96956  [ 96956] enkele       q29 ? it
    @+96956  [ 96956] enkele       done. it
    @+96971  [ 96971] enkelletsels q26 ? ␅
    @+96971  [ 96971] enkelletsels q27 ? before
    @+97001  [ 97001] enkelvoud    q24 ? ␅
    @+97001  [ 97001] enkelvoud    q25 ? before
    @+97068  [ 97068] ens          q22 ? ␅
    @+97068  [ 97068] ens          q23 ? before
    @+97207  [ 97207] entree       q20 ? ␅
    @+97207  [ 97207] entree       q21 ? before
    @+97490  [ 97490] er           q16 ? ␅
    @+97490  [ 97490] er           q17 ? before
    @+99692  [ 99692] ex           q4  ? ␅
    @+99692  [ 99692] ex           q5  ? before
    @+199548 [199548] lij          q1  ? after
    @+199548 [199548] lij          q2  ? ␅
    @+199548 [199548] lij          q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1118 🥳 30 ⏱️ 0:00:49.833583

🤔 30 attempts
📜 1 sessions

    @       [    0] aa         
    @+23680 [23680] camp       q6  ? ␅
    @+23680 [23680] camp       q7  ? after
    @+35522 [35522] convention q8  ? ␅
    @+35522 [35522] convention q9  ? after
    @+40838 [40838] da         q10 ? ␅
    @+40838 [40838] da         q11 ? after
    @+44070 [44070] den        q12 ? ␅
    @+44070 [44070] den        q13 ? after
    @+44866 [44866] derogate   q16 ? ␅
    @+44866 [44866] derogate   q17 ? after
    @+45060 [45060] desi       q20 ? ␅
    @+45060 [45060] desi       q21 ? after
    @+45109 [45109] desinences q24 ? ␅
    @+45109 [45109] desinences q25 ? after
    @+45131 [45131] desist     q26 ? ␅
    @+45131 [45131] desist     q27 ? after
    @+45137 [45137] desk       q28 ? ␅
    @+45137 [45137] desk       q29 ? it
    @+45137 [45137] desk       done. it
    @+45158 [45158] desolate   q22 ? ␅
    @+45158 [45158] desolate   q23 ? before
    @+45262 [45262] dessert    q18 ? ␅
    @+45262 [45262] dessert    q19 ? before
    @+45662 [45662] dev        q14 ? ␅
    @+45662 [45662] dev        q15 ? before
    @+47378 [47378] dis        q4  ? ␅
    @+47378 [47378] dis        q5  ? before
    @+98147 [98147] mac        q1  ? after
    @+98147 [98147] mac        q2  ? ␅
    @+98147 [98147] mac        q3  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1544 😳 6 ⏱️ 0:02:13.735769

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:NANNA n n n n n remain:5978
    ⬜⬜⬜⬜⬜ tried:STOSS n n n n n remain:1246
    ⬜⬜⬜⬜⬜ tried:FUDDY n n n n n remain:335
    ⬜⬜⬜⬜🟩 tried:GRRRL n n n n Y remain:21
    ⬜⬜🟨⬜🟩 tried:CHILL n n m n Y remain:6
    🟩🟩🟩🟩🟩 tried:PIXEL Y Y Y Y Y remain:0

    Undos used: 2

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1687 🥳 19 ⏱️ 0:03:02.486149

📜 1 sessions
💰 score: 9700

    5/6
    LOSER ⬜⬜🟨⬜⬜
    PIANS ⬜⬜🟩🟨🟨
    SHAWN 🟩⬜🟩⬜🟨
    SNACK 🟩🟩🟩⬜⬜
    SNAFU 🟩🟩🟩🟩🟩
    4/6
    SNAFU ⬜⬜🟨⬜⬜
    ALERT 🟨⬜🟨⬜⬜
    DECAY 🟨🟩⬜🟨⬜
    MEDIA 🟩🟩🟩🟩🟩
    4/6
    MEDIA ⬜🟨⬜⬜🟨
    ARLES 🟨🟩⬜🟨⬜
    CRATE ⬜🟩🟨⬜🟨
    BREAK 🟩🟩🟩🟩🟩
    5/6
    BREAK ⬜⬜⬜⬜⬜
    TULIP ⬜⬜⬜⬜⬜
    DOWNS 🟨🟩⬜🟨⬜
    CODON 🟩🟩🟨🟨🟨
    CONDO 🟩🟩🟩🟩🟩
    Final 1/2
    UNLIT 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1664 🥳 score:20 ⏱️ 0:02:20.061678

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. RIDER attempts:8 score:8
2. MOLDY attempts:4 score:4
3. MEALY attempts:3 score:3
4. LYMPH attempts:5 score:5

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1664 🥳 score:57 ⏱️ 0:02:02.099090

📜 1 sessions

Octordle Classic

1. STAIR attempts:6 score:6
2. STEED attempts:8 score:8
3. SPICE attempts:10 score:10
4. LYING attempts:3 score:3
5. GULLY attempts:12 score:12
6. CHEER attempts:9 score:9
7. MINTY attempts:4 score:4
8. NUTTY attempts:5 score:5

# [Sedecordle Classic](https://www.sedecordle.com/?mode=daily) 🧩 #1644 🥳 score:43 ⏱️ 0:02:13.752479

📜 1 sessions

Sedecordle Classic sedecordle.com

1. EIGHT attempts:10 score:1
2. ALLOW attempts:12 score:0
3. VODKA attempts:6 score:0
4. DRYLY attempts:5 score:6
5. BASAL attempts:7 score:0
6. STINK attempts:8 score:7
7. LIKEN attempts:9 score:0
8. MOLAR attempts:13 score:9
9. ASIDE attempts:4 score:0
10. NIECE attempts:16 score:4
11. AZURE attempts:14 score:1
12. POLKA attempts:11 score:4
13. ASSET attempts:3 score:0
14. SPEAR attempts:15 score:3
15. WEIRD attempts:17 score:1
16. ROUND attempts:18 score:7

# [squareword.org](squareword.org) 🧩 #1657 🥳 7 ⏱️ 0:01:59.580716

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    K A R T S
    I L E U M
    N O B L E
    D O U L A
    A F T E R

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1594 🥳 316 ⏱️ 0:05:13.041862

🤔 317 attempts
📜 1 sessions
🫧 16 chat sessions
⁉️ 86 chat prompts
🤖 86 dolphin3:latest replies
🥵   2 😎  24 🥶 288 🧊   2

      $1 #317 golden         100.00°C 🥳 1000‰ ~315 used:0  [314]  source:dolphin3
      $2  #88 sweet           33.06°C 🥵  940‰  ~23 used:70 [22]   source:dolphin3
      $3  #91 brown           32.55°C 🥵  925‰  ~22 used:54 [21]   source:dolphin3
      $4 #304 tantalizing     31.03°C 😎  880‰   ~8 used:3  [7]    source:dolphin3
      $5 #229 tempting        30.16°C 😎  842‰  ~24 used:7  [23]   source:dolphin3
      $6 #212 luscious        29.64°C 😎  808‰  ~19 used:4  [18]   source:dolphin3
      $7 #209 irresistible    28.37°C 😎  710‰   ~9 used:3  [8]    source:dolphin3
      $8 #211 heavenly        28.23°C 😎  695‰  ~10 used:3  [9]    source:dolphin3
      $9 #253 sugarplum       28.18°C 😎  690‰  ~11 used:3  [10]   source:dolphin3
     $10 #282 frosted         28.07°C 😎  679‰  ~12 used:3  [11]   source:dolphin3
     $11 #257 mint            27.98°C 😎  669‰  ~13 used:3  [12]   source:dolphin3
     $12 #231 alluring        27.68°C 😎  637‰  ~14 used:3  [13]   source:dolphin3
     $28  #61 pie             24.36°C 🥶        ~28 used:5  [27]   source:dolphin3
    $316   #3 ecosystem       -3.34°C 🧊       ~316 used:0  [315]  source:dolphin3

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1627 🥳 371 ⏱️ 0:06:22.864969

🤔 372 attempts
📜 1 sessions
🫧 17 chat sessions
⁉️ 86 chat prompts
🤖 86 dolphin3:latest replies
😱   1 🔥   3 🥵   7 😎  33 🥶 246 🧊  81

      $1 #372 change            100.00°C 🥳 1000‰ ~291 used:0  [290]  source:dolphin3
      $2 #371 devise             53.11°C 😱  999‰   ~1 used:0  [0]    source:dolphin3
      $3 #369 monnaie            50.24°C 🔥  997‰   ~2 used:0  [1]    source:dolphin3
      $4 #359 monétaire          46.81°C 🔥  996‰   ~3 used:1  [2]    source:dolphin3
      $5 #352 dévaluation        40.22°C 🔥  991‰   ~4 used:0  [3]    source:dolphin3
      $6 #347 inflation          36.04°C 🥵  979‰  ~10 used:5  [9]    source:dolphin3
      $7 #368 banque             34.80°C 🥵  974‰   ~5 used:0  [4]    source:dolphin3
      $8 #351 déflation          30.10°C 🥵  943‰   ~9 used:3  [8]    source:dolphin3
      $9 #253 ajustement         29.72°C 🥵  938‰  ~36 used:46 [35]   source:dolphin3
     $10 #364 récession          28.77°C 🥵  924‰   ~6 used:0  [5]    source:dolphin3
     $11 #348 marché             28.12°C 🥵  915‰   ~7 used:1  [6]    source:dolphin3
     $13 #360 monétarisme        25.70°C 😎  877‰  ~11 used:0  [10]   source:dolphin3
     $46 #293 élargissement      14.14°C 🥶        ~54 used:0  [53]   source:dolphin3
    $292 #133 séance             -0.02°C 🧊       ~292 used:0  [291]  source:dolphin3
