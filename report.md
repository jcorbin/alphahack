# 2026-06-11

- 🔗 spaceword.org 🧩 2026-06-10 🏁 score 2168 ranked 52.8% 169/320 ⏱️ 0:23:01.959436
- 🔗 alfagok.diginaut.net 🧩 #586 🥳 30 ⏱️ 0:00:33.078615
- 🔗 alphaguess.com 🧩 #1053 🥳 24 ⏱️ 0:00:24.710585
- 🔗 dontwordle.com 🧩 #1479 🥳 6 ⏱️ 0:01:33.020211
- 🔗 cemantle.certitudes.org 🧩 #1529 😦 1143 ⏱️ 13:21:44.074669
- 🔗 dictionary.com hurdle 🧩 #1622 🥳 16 ⏱️ 0:02:27.816174
- 🔗 Quordle Classic 🧩 #1599 🥳 score:25 ⏱️ 0:01:23.223729
- 🔗 Octordle Classic 🧩 #1599 🥳 score:66 ⏱️ 0:03:21.173965
- 🔗 squareword.org 🧩 #1592 🥳 7 ⏱️ 0:01:36.519471

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


# [spaceword.org](spaceword.org) 🧩 2026-06-10 🏁 score 2168 ranked 52.8% 169/320 ⏱️ 0:23:01.959436

📜 2 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 169/320

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ A B _ _ S _ _ T _   
      _ D O _ Y E _ _ A _   
      _ Z O W E E _ _ K _   
      _ _ _ E N N U Y E _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #586 🥳 30 ⏱️ 0:00:33.078615

🤔 30 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+2      [     2] -cijferig 
    @+199766 [199766] lijm      q0  ? ␅
    @+199766 [199766] lijm      q1  ? after
    @+247637 [247637] op        q4  ? ␅
    @+247637 [247637] op        q5  ? after
    @+273434 [273434] proef     q6  ? ␅
    @+273434 [273434] proef     q7  ? after
    @+286502 [286502] rijs      q8  ? ␅
    @+286502 [286502] rijs      q9  ? after
    @+288046 [288046] roemrucht q14 ? ␅
    @+288046 [288046] roemrucht q15 ? after
    @+288370 [288370] rok       q18 ? ␅
    @+288370 [288370] rok       q19 ? after
    @+288374 [288374] rokeer    q26 ? ␅
    @+288374 [288374] rokeer    q27 ? after
    @+288378 [288378] roken     q28 ? ␅
    @+288378 [288378] roken     q29 ? it
    @+288378 [288378] roken     done. it
    @+288381 [288381] roker     q22 ? ␅
    @+288381 [288381] roker     q23 ? before
    @+288434 [288434] rol       q20 ? ␅
    @+288434 [288434] rol       q21 ? before
    @+288787 [288787] rommel    q16 ? ␅
    @+288787 [288787] rommel    q17 ? before
    @+289596 [289596] roof      q12 ? ␅
    @+289596 [289596] roof      q13 ? before
    @+292729 [292729] samen     q10 ? ␅
    @+292729 [292729] samen     q11 ? before
    @+299628 [299628] schub     q2  ? ␅
    @+299628 [299628] schub     q3  ? before

# [alphaguess.com](alphaguess.com) 🧩 #1053 🥳 24 ⏱️ 0:00:24.710585

🤔 24 attempts
📜 1 sessions

    @        [     0] aa     
    @+1      [     1] aah    
    @+2      [     2] aahed  
    @+3      [     3] aahing 
    @+98214  [ 98214] mach   q0  ? ␅
    @+98214  [ 98214] mach   q1  ? after
    @+98214  [ 98214] mach   q2  ? ␅
    @+98214  [ 98214] mach   q3  ? after
    @+122775 [122775] parr   q6  ? ␅
    @+122775 [122775] parr   q7  ? after
    @+125807 [125807] petti  q12 ? ␅
    @+125807 [125807] petti  q13 ? after
    @+127320 [127320] pidgin q14 ? ␅
    @+127320 [127320] pidgin q15 ? after
    @+127404 [127404] pig    q20 ? ␅
    @+127404 [127404] pig    q21 ? after
    @+127526 [127526] pile   q22 ? ␅
    @+127526 [127526] pile   q23 ? it
    @+127526 [127526] pile   done. it
    @+127657 [127657] pin    q18 ? ␅
    @+127657 [127657] pin    q19 ? before
    @+128073 [128073] pis    q16 ? ␅
    @+128073 [128073] pis    q17 ? before
    @+128844 [128844] play   q10 ? ␅
    @+128844 [128844] play   q11 ? before
    @+135066 [135066] proper q8  ? ␅
    @+135066 [135066] proper q9  ? before
    @+147364 [147364] rhotic q4  ? ␅
    @+147364 [147364] rhotic q5  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1479 🥳 6 ⏱️ 0:01:33.020211

📜 1 sessions
💰 score: 18

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:GABBA n n n n n remain:5913
    ⬜⬜⬜⬜⬜ tried:OVOLO n n n n n remain:2552
    ⬜⬜⬜⬜⬜ tried:JIFFS n n n n n remain:501
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:185
    ⬜⬜⬜⬜⬜ tried:CRUCK n n n n n remain:26
    ⬜🟨⬜🟨⬜ tried:DEWED n m n m n remain:3

    Undos used: 3

      3 words remaining
    x 6 unused letters
    = 18 total score

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1529 😦 1143 ⏱️ 13:21:44.074669

🤔 1142 attempts
📜 2 sessions
🫧 96 chat sessions
⁉️ 511 chat prompts
🤖 510 dolphin3:latest replies
😦 🔥    2 🥵   21 😎  115 🥶  941 🧊   63

       $1 #1097 zoster                56.41°C 🔥  998‰    ~1 used:66  [0]     source:dolphin3
       $2  #763 myelitis              53.43°C 🔥  995‰  ~130 used:236 [129]   source:dolphin3
       $3  #762 meningoencephalitis   51.32°C 🥵  988‰  ~135 used:114 [134]   source:dolphin3
       $4  #702 orchitis              49.12°C 🥵  975‰  ~133 used:57  [132]   source:dolphin3
       $5  #426 pleurisy              46.44°C 🥵  964‰  ~136 used:117 [135]   source:dolphin3
       $6 #1038 neurosyphilis         46.29°C 🥵  963‰   ~24 used:11  [23]    source:dolphin3
       $7  #316 influenza             45.95°C 🥵  959‰  ~134 used:89  [133]   source:dolphin3
       $8 #1045 pyogenic              45.73°C 🥵  956‰   ~25 used:11  [24]    source:dolphin3
       $9  #470 nosocomial            45.02°C 🥵  948‰  ~131 used:28  [130]   source:dolphin3
      $10  #644 enteritis             44.92°C 🥵  945‰   ~26 used:11  [25]    source:dolphin3
      $11  #662 tracheitis            44.22°C 🥵  935‰   ~27 used:11  [26]    source:dolphin3
      $24  #646 ileitis               42.21°C 😎  898‰   ~39 used:2   [38]    source:dolphin3
     $139  #588 nasopharynx           30.72°C 🥶        ~159 used:0   [158]   source:dolphin3
    $1080  #274 presentation          -0.13°C 🧊       ~1080 used:0   [1079]  source:dolphin3

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1622 🥳 16 ⏱️ 0:02:27.816174

📜 1 sessions
💰 score: 10000

    3/6
    ROLES ⬜⬜⬜⬜🟨
    MISTY 🟩🟩🟨🟨⬜
    MIDST 🟩🟩🟩🟩🟩
    5/6
    MIDST ⬜⬜⬜🟨⬜
    ASPER 🟨🟨🟨🟨⬜
    SNEAP 🟩⬜🟨🟨🟨
    SCAPE 🟩⬜🟩🟩🟩
    SHAPE 🟩🟩🟩🟩🟩
    4/6
    SHAPE ⬜⬜⬜⬜🟩
    OLDIE 🟨⬜⬜⬜🟩
    TRONE 🟨⬜🟨🟨🟩
    MONTE 🟩🟩🟩🟩🟩
    3/6
    MONTE ⬜⬜⬜🟨⬜
    SPIRT ⬜⬜🟨🟨🟩
    FRUIT 🟩🟩🟩🟩🟩
    Final 1/2
    SWIPE 🟩🟩🟩🟩🟩

# [Quordle Classic](https://www.merriam-webster.com/games/quordle/#/) 🧩 #1599 🥳 score:25 ⏱️ 0:01:23.223729

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. GAMMA attempts:9 score:9
2. SPILL attempts:6 score:6
3. SALVE attempts:7 score:7
4. RURAL attempts:3 score:3

# [Octordle Classic](https://www.merriam-webster.com/games/octordle/daily) 🧩 #1599 🥳 score:66 ⏱️ 0:03:21.173965

📜 2 sessions

Octordle Classic

1. SCION attempts:7 score:7
2. CURVY attempts:10 score:10
3. WEIGH attempts:11 score:11
4. BROOK attempts:6 score:6
5. SYNOD attempts:3 score:3
6. OZONE attempts:9 score:9
7. HOLLY attempts:12 score:12
8. STOMP attempts:8 score:8

# [squareword.org](squareword.org) 🧩 #1592 🥳 7 ⏱️ 0:01:36.519471

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C H E W S
    A E R I E
    C R U D E
    H O P E D
    E N T R Y
