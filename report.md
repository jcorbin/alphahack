# 2026-01-03

- 🔗 spaceword.org 🧩 2026-01-02 🏁 score 2173 ranked 8.1% 27/332 ⏱️ 0:53:21.422451
- 🔗 alfagok.diginaut.net 🧩 #427 🥳 12 ⏱️ 0:00:35.518821
- 🔗 alphaguess.com 🧩 #893 🥳 16 ⏱️ 0:00:27.806830
- 🔗 dontwordle.com 🧩 #1320 😳 6 ⏱️ 0:01:07.999734
- 🔗 dictionary.com hurdle 🧩 #1463 🥳 17 ⏱️ 0:03:34.640025
- 🔗 Quordle Classic 🧩 #1440 🥳 score:25 ⏱️ 0:01:42.837464
- 🔗 Octordle Classic 🧩 #1440 🥳 score:51 ⏱️ 0:02:53.977151
- 🔗 squareword.org 🧩 #1433 🥳 8 ⏱️ 0:02:09.140304
- 🔗 cemantle.certitudes.org 🧩 #1370 🥳 98 ⏱️ 0:01:14.518608
- 🔗 cemantix.certitudes.org 🧩 #1403 🥳 131 ⏱️ 0:03:04.372882
- 🔗 Quordle Rescue 🧩 #54 🥳 score:24 ⏱️ 0:01:38.254952
- 🔗 Quordle Sequence 🧩 #1440 🥳 score:23 ⏱️ 0:01:33.428598
- 🔗 Quordle Extreme 🧩 #523 🥳 score:22 ⏱️ 0:01:29.798586
- 🔗 Octordle Rescue 🧩 #1440 😦 score:7 ⏱️ 0:03:25.429641
- 🔗 Octordle Sequence 🧩 #1440 🥳 score:59 ⏱️ 0:02:46.520934
- 🔗 Octordle Extreme 🧩 #1440 🥳 score:57 ⏱️ 0:03:50.015462

# Dev

## WIP

- ui:
  - Handle -- stabilizing core over Listing
  - Shell -- minimizing over Handle

- meta: rework command model over Shell

## TODO

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









# spaceword.org 🧩 2026-01-02 🏁 score 2173 ranked 8.1% 27/332 ⏱️ 0:53:21.422451

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 27/332

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ O _ B E F O U L S   
      _ W _ O R E _ S _ K   
      _ N O Y A U X _ _ A   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# alfagok.diginaut.net 🧩 #427 🥳 12 ⏱️ 0:00:35.518821

🤔 12 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+1      [     1] &-tekens     
    @+2      [     2] -cijferig    
    @+3      [     3] -e-mail      
    @+99758  [ 99758] ex           q1  ? after
    @+111413 [111413] ge           q3  ? after
    @+120924 [120924] gequeruleerd q5  ? after
    @+125678 [125678] gezeglijk    q6  ? after
    @+125755 [125755] gezicht      q11 ? it
    @+125755 [125755] gezicht      done. it
    @+125859 [125859] gezin        q10 ? before
    @+126059 [126059] gezon        q9  ? before
    @+126863 [126863] giek         q8  ? before
    @+128048 [128048] glazen       q7  ? before
    @+130434 [130434] gracieuze    q4  ? before
    @+149454 [149454] huis         q2  ? before
    @+199833 [199833] lijm         q0  ? before

# alphaguess.com 🧩 #893 🥳 16 ⏱️ 0:00:27.806830

🤔 16 attempts
📜 1 sessions

    @        [     0] aa         
    @+1      [     1] aah        
    @+2      [     2] aahed      
    @+3      [     3] aahing     
    @+98224  [ 98224] mach       q0  ? after
    @+147329 [147329] rho        q1  ? after
    @+171929 [171929] tag        q2  ? after
    @+176966 [176966] tom        q4  ? after
    @+179490 [179490] trifurcate q5  ? after
    @+180740 [180740] tune       q6  ? after
    @+181377 [181377] two        q7  ? after
    @+181691 [181691] ulcer      q8  ? after
    @+181741 [181741] ultra      q9  ? after
    @+181871 [181871] ultras     q10 ? after
    @+181921 [181921] um         q11 ? after
    @+181962 [181962] umbra      q12 ? after
    @+181971 [181971] umbrella   q15 ? it
    @+181971 [181971] umbrella   done. it
    @+181977 [181977] umiac      q14 ? before
    @+181989 [181989] umm        q13 ? before
    @+182015 [182015] un         q3  ? before

# dontwordle.com 🧩 #1320 😳 6 ⏱️ 0:01:07.999734

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:MOTTO n n n n n remain:5765
    ⬜⬜⬜⬜⬜ tried:VIZIR n n n n n remain:2251
    ⬜⬜⬜⬜⬜ tried:WUDDY n n n n n remain:738
    ⬜🟨⬜⬜⬜ tried:BEECH n m n n n remain:79
    🟨⬜⬜⬜🟩 tried:AGAPE m n n n Y remain:4
    🟩🟩🟩🟩🟩 tried:FALSE Y Y Y Y Y remain:0

    Undos used: 1

      0 words remaining
    x 0 unused letters
    = 0 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1463 🥳 17 ⏱️ 0:03:34.640025

📜 1 sessions
💰 score: 9900

    4/6
    ARISE ⬜⬜🟩🟨🟩
    STIPE 🟩⬜🟩⬜🟩
    SWINE 🟩⬜🟩🟨🟩
    SNIDE 🟩🟩🟩🟩🟩
    3/6
    SNIDE 🟨⬜⬜⬜🟨
    TEARS ⬜🟨⬜⬜🟨
    FLESH 🟩🟩🟩🟩🟩
    5/6
    FLESH ⬜⬜⬜🟩⬜
    ANTSY 🟨⬜⬜🟩⬜
    DORSA ⬜⬜⬜🟩🟨
    MIASM ⬜⬜🟩🟩🟩
    SPASM 🟩🟩🟩🟩🟩
    4/6
    SPASM 🟨⬜⬜⬜⬜
    LOINS ⬜⬜⬜⬜🟨
    DUSTY ⬜🟩🟩🟩🟩
    RUSTY 🟩🟩🟩🟩🟩
    Final 1/2
    FLORA 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1440 🥳 score:25 ⏱️ 0:01:42.837464

📜 2 sessions

Quordle Classic m-w.com/games/quordle/

1. SPORE attempts:3 score:3
2. FLAIR attempts:6 score:6
3. BOBBY attempts:9 score:9
4. TEACH attempts:7 score:7

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1440 🥳 score:51 ⏱️ 0:02:53.977151

📜 1 sessions

Octordle Classic

1. ADULT attempts:5 score:5
2. ORDER attempts:10 score:10
3. AVOID attempts:9 score:9
4. QUAIL attempts:8 score:8
5. AZURE attempts:2 score:2
6. ASSET attempts:7 score:7
7. SNIDE attempts:6 score:6
8. THREE attempts:4 score:4

# squareword.org 🧩 #1433 🥳 8 ⏱️ 0:02:09.140304

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T A R S
    L I M I T
    A B O D E
    B I N G E
    S A G E R

# cemantle.certitudes.org 🧩 #1370 🥳 98 ⏱️ 0:01:14.518608

🤔 99 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 23 chat prompts
🤖 23 dolphin3:latest replies
🔥  4 🥵  7 😎  7 🥶 79 🧊  1

     $1 #99  ~1 vocabulary       100.00°C 🥳 1000‰
     $2 #91  ~9 lexicon           61.20°C 😱  999‰
     $3 #81 ~14 comprehension     60.06°C 🔥  998‰
     $4 #74 ~18 grammar           57.35°C 🔥  997‰
     $5 #93  ~7 dictionary        53.70°C 🔥  991‰
     $6 #85 ~12 idiom             52.95°C 🥵  989‰
     $7 #73 ~19 syntax            52.59°C 🥵  988‰
     $8 #94  ~6 lexical           49.78°C 🥵  975‰
     $9 #96  ~4 punctuation       49.17°C 🥵  968‰
    $10 #98  ~2 slang             47.88°C 🥵  960‰
    $11 #76 ~17 phonetics         47.28°C 🥵  956‰
    $13 #86 ~11 colloquialism     41.44°C 😎  883‰
    $20 #55     formalism         29.35°C 🥶
    $99 #31     deployment        -0.64°C 🧊

# cemantix.certitudes.org 🧩 #1403 🥳 131 ⏱️ 0:03:04.372882

🤔 132 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 29 chat prompts
🤖 29 dolphin3:latest replies
🥵  5 😎 22 🥶 79 🧊 25

      $1 #132   ~1 révolutionnaire  100.00°C 🥳 1000‰
      $2 #127   ~5 réformiste        55.91°C 🥵  987‰
      $3 #131   ~2 progressiste      50.10°C 🥵  970‰
      $4 #104  ~22 idéologique       47.96°C 🥵  959‰
      $5 #106  ~20 nationaliste      47.58°C 🥵  954‰
      $6  #97  ~23 idéologie         46.93°C 🥵  945‰
      $7 #130   ~3 bourgeois         42.90°C 😎  884‰
      $8 #110  ~16 collectiviste     42.14°C 😎  871‰
      $9 #122   ~8 monarchique       41.93°C 😎  865‰
     $10 #105  ~21 idéologue         38.98°C 😎  797‰
     $11  #95  ~25 idéaliste         38.12°C 😎  770‰
     $12  #92  ~26 idéalisme         36.81°C 😎  730‰
     $29 #120      conservateur      27.62°C 🥶
    $108   #7      montagne          -0.03°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #54 🥳 score:24 ⏱️ 0:01:38.254952

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. SLINK attempts:5 score:5
2. SCENE attempts:6 score:6
3. BUGGY attempts:9 score:9
4. SHACK attempts:4 score:4

# [Quordle Sequence](m-w.com/games/quordle/#/sequence) 🧩 #1440 🥳 score:23 ⏱️ 0:01:33.428598

📜 2 sessions

Quordle Sequence m-w.com/games/quordle/

1. COLOR attempts:4 score:4
2. REGAL attempts:5 score:5
3. TONAL attempts:6 score:6
4. BUDDY attempts:8 score:8

# [Quordle Extreme](m-w.com/games/quordle/#/extreme) 🧩 #523 🥳 score:22 ⏱️ 0:01:29.798586

📜 1 sessions

Quordle Extreme m-w.com/games/quordle/

1. GEESE attempts:7 score:7
2. FILTH attempts:6 score:6
3. BRISK attempts:5 score:5
4. BAYOU attempts:4 score:4

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1440 😦 score:7 ⏱️ 0:03:25.429641

📜 2 sessions

Octordle Rescue

1. ANGER attempts:6 score:9
2. ELIDE attempts:3 score:6
3. ROBIN attempts:4 score:7
4. OPINE attempts:7 score:10
5. OVOID attempts:8 score:11
6. COUNT attempts:10 score:13
7. _____ ~PU -ABCDEGHILMNORSTV attempts:10 score:-1
8. INANE attempts:5 score:8

# [Octordle Sequence](britannica.com/games/octordle/daily-sequence) 🧩 #1440 🥳 score:59 ⏱️ 0:02:46.520934

📜 1 sessions

Octordle Sequence

1. INTER attempts:3 score:3
2. JOUST attempts:5 score:5
3. BEGAT attempts:6 score:6
4. PROBE attempts:7 score:7
5. CHAIN attempts:8 score:8
6. BULGE attempts:9 score:9
7. THEME attempts:10 score:10
8. TEARY attempts:11 score:11

# [Octordle Extreme](britannica.com/games/octordle/extreme) 🧩 #1440 🥳 score:57 ⏱️ 0:03:50.015462

📜 1 sessions

Octordle Extreme

1. LUCRE attempts:3 score:3
2. CREPE attempts:5 score:5
3. HAZEL attempts:6 score:6
4. RUMBA attempts:8 score:8
5. ABATE attempts:9 score:9
6. DAIRY attempts:10 score:10
7. TRUTH attempts:4 score:4
8. GENUS attempts:12 score:12
