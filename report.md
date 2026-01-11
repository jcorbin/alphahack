# 2026-01-12

- 🔗 spaceword.org 🧩 2026-01-11 🏁 score 2173 ranked 13.3% 42/316 ⏱️ 8:04:05.555971
- 🔗 alfagok.diginaut.net 🧩 #436 🥳 17 ⏱️ 0:00:46.967925
- 🔗 alphaguess.com 🧩 #903 🥳 15 ⏱️ 0:00:28.301780
- 🔗 dontwordle.com 🧩 #1329 🥳 6 ⏱️ 0:01:47.984840
- 🔗 dictionary.com hurdle 🧩 #1472 🥳 18 ⏱️ 0:03:10.047941
- 🔗 Quordle Classic 🧩 #1449 🥳 score:23 ⏱️ 0:01:46.809065
- 🔗 Octordle Classic 🧩 #1449 🥳 score:66 ⏱️ 0:03:54.169334
- 🔗 squareword.org 🧩 #1442 🥳 7 ⏱️ 0:01:53.296232
- 🔗 cemantle.certitudes.org 🧩 #1379 🥳 841 ⏱️ 0:20:14.888352
- 🔗 cemantix.certitudes.org 🧩 #1412 🥳 61 ⏱️ 0:02:40.612572
- 🔗 Quordle Rescue 🧩 #63 🥳 score:21 ⏱️ 0:01:14.719160
- 🔗 Quordle Sequence 🧩 #1449 🥳 score:28 ⏱️ 0:02:03.936217
- 🔗 Quordle Extreme 🧩 #532 🥳 score:24 ⏱️ 0:01:56.369103
- 🔗 Octordle Rescue 🧩 #1449 🥳 score:9 ⏱️ 0:03:18.736065
- 🔗 Octordle Sequence 🧩 #1449 🥳 score:64 ⏱️ 0:03:35.971420
- 🔗 Octordle Extreme 🧩 #1449 🥳 score:55 ⏱️ 0:03:16.721232

# Dev

## WIP

- hurdle: add novel words to wordlist

- meta:
  - rework SolverHarness => Solver{ Library, Scope }
  - variants: regression on 01-06 running quordle

- ui:
  - Handle -- stabilizing core over Listing
  - Shell -- minimizing over Handle
- meta: rework command model over Shell

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


















# spaceword.org 🧩 2026-01-11 🏗️ score 2173 current ranking 42/308 ⏱️ 8:04:00.125934

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 42/308

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ O P _ P O G O E D   
      _ W E K A _ _ _ _ O   
      _ L _ A D J U R E S   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# [spaceword.org](spaceword.org) 🧩 2026-01-11 🏁 score 2173 ranked 13.3% 42/316 ⏱️ 8:04:05.555971

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 42/316

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ O P _ P O G O E D   
      _ W E K A _ _ _ _ O   
      _ L _ A D J U R E S   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# [alfagok.diginaut.net](alfagok.diginaut.net) 🧩 #436 🥳 17 ⏱️ 0:00:46.967925

🤔 17 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199833 [199833] lijm      q0  ? after
    @+299739 [299739] schub     q1  ? after
    @+349523 [349523] vakantie  q2  ? after
    @+374265 [374265] vrij      q3  ? after
    @+374265 [374265] vrij      q4  ? after
    @+386806 [386806] wind      q5  ? after
    @+393223 [393223] zelfmoord q6  ? after
    @+394818 [394818] zigzag    q8  ? after
    @+395595 [395595] zo        q9  ? after
    @+395607 [395607] zoden     q13 ? after
    @+395615 [395615] zodiak    q14 ? after
    @+395619 [395619] zodra     q16 ? it
    @+395619 [395619] zodra     done. it
    @+395622 [395622] zoef      q15 ? before
    @+395626 [395626] zoek      q12 ? before
    @+395786 [395786] zoem      q11 ? before
    @+395998 [395998] zomer     q10 ? before
    @+396432 [396432] zone      q7  ? before

# [alphaguess.com](alphaguess.com) 🧩 #903 🥳 15 ⏱️ 0:00:28.301780

🤔 15 attempts
📜 1 sessions

    @       [    0] aa     
    @+1     [    1] aah    
    @+2     [    2] aahed  
    @+3     [    3] aahing 
    @+47382 [47382] dis    q1  ? after
    @+72801 [72801] gremmy q2  ? after
    @+85505 [85505] ins    q3  ? after
    @+91850 [91850] knot   q4  ? after
    @+93270 [93270] lar    q6  ? after
    @+93410 [93410] las    q9  ? after
    @+93431 [93431] lash   q11 ? after
    @+93443 [93443] lass   q12 ? after
    @+93451 [93451] lasso  q13 ? after
    @+93459 [93459] last   q14 ? it
    @+93459 [93459] last   done. it
    @+93472 [93472] lat    q10 ? before
    @+93562 [93562] lati   q8  ? before
    @+93898 [93898] lea    q7  ? before
    @+94947 [94947] lib    q5  ? before
    @+98220 [98220] mach   q0  ? before

# [dontwordle.com](dontwordle.com) 🧩 #1329 🥳 6 ⏱️ 0:01:47.984840

📜 1 sessions
💰 score: 88

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MIMIC n n n n n remain:6772
    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:3545
    ⬜⬜⬜⬜⬜ tried:KOOKY n n n n n remain:1135
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:545
    ⬜⬜⬜⬜⬜ tried:LULUS n n n n n remain:70
    🟨⬜⬜🟩⬜ tried:EBBED m n n Y n remain:11

    Undos used: 3

      11 words remaining
    x 8 unused letters
    = 88 total score

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1472 🥳 18 ⏱️ 0:03:10.047941

📜 1 sessions
💰 score: 9800

    3/6
    UREAS 🟨🟨⬜⬜🟨
    HURTS ⬜🟨🟩⬜🟨
    SCRUB 🟩🟩🟩🟩🟩
    5/6
    SCRUB 🟩⬜⬜⬜⬜
    SHINE 🟩⬜🟩🟩⬜
    SLING 🟩⬜🟩🟩⬜
    STINK 🟩⬜🟩🟩⬜
    SPINY 🟩🟩🟩🟩🟩
    4/6
    SPINY 🟩⬜⬜🟨⬜
    SENOR 🟩🟩🟨⬜⬜
    SEDAN 🟩🟩⬜⬜🟩
    SEVEN 🟩🟩🟩🟩🟩
    4/6
    SEVEN ⬜⬜⬜⬜⬜
    MORAL ⬜⬜⬜⬜🟩
    QUILL ⬜⬜🟩🟩🟩
    CHILL 🟩🟩🟩🟩🟩
    Final 2/2
    SHARE 🟩🟩⬜🟩🟩
    SHORE 🟩🟩🟩🟩🟩

# [Quordle Classic](m-w.com/games/quordle/#/) 🧩 #1449 🥳 score:23 ⏱️ 0:01:46.809065

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. BRINE attempts:5 score:5
2. ROUND attempts:4 score:4
3. FLUME attempts:8 score:8
4. REBUS attempts:6 score:6

# [Octordle Classic](britannica.com/games/octordle/daily) 🧩 #1449 🥳 score:66 ⏱️ 0:03:54.169334

📜 1 sessions

Octordle Classic

1. ELATE attempts:12 score:12
2. READY attempts:4 score:4
3. GRAVY attempts:8 score:8
4. CORNY attempts:7 score:7
5. FORUM attempts:9 score:9
6. HUMAN attempts:10 score:10
7. POWER attempts:11 score:11
8. THETA attempts:5 score:5

# [squareword.org](squareword.org) 🧩 #1442 🥳 7 ⏱️ 0:01:53.296232

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    B R A S H
    A E R I E
    S T O R E
    A R M E D
    L O A N S

# [cemantle.certitudes.org](cemantle.certitudes.org) 🧩 #1379 🥳 841 ⏱️ 0:20:14.888352

🤔 842 attempts
📜 1 sessions
🫧 55 chat sessions
⁉️ 273 chat prompts
🤖 273 dolphin3:latest replies
🔥   6 🥵  36 😎 181 🥶 585 🧊  33

      $1 #842   ~1 residential      100.00°C 🥳 1000‰
      $2 #330 ~166 housing           59.71°C 🔥  998‰
      $3 #332 ~164 condominium       57.70°C 🔥  997‰
      $4 #353 ~152 property          52.44°C 🔥  996‰
      $5 #453 ~120 subdivision       51.05°C 🔥  994‰
      $6 #346 ~158 condo             50.56°C 🔥  993‰
      $7 #589  ~85 commercial        50.53°C 🔥  992‰
      $8 #632  ~71 dwelling          44.72°C 🥵  988‰
      $9 #345 ~159 urban             44.31°C 🥵  987‰
     $10 #438 ~126 neighborhood      43.10°C 🥵  986‰
     $11 #125 ~214 construction      42.91°C 🥵  985‰
     $44 #347 ~157 villa             32.76°C 😎  896‰
    $226 #410      lawn              20.41°C 🥶
    $810  #58      duelist           -0.07°C 🧊

# [cemantix.certitudes.org](cemantix.certitudes.org) 🧩 #1412 🥳 61 ⏱️ 0:02:40.612572

🤔 62 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 16 chat prompts
🤖 16 dolphin3:latest replies
🥵  4 😎  4 🥶 35 🧊 18

     $1 #62  ~1 ambition        100.00°C 🥳 1000‰
     $2 #54  ~4 objectif         48.40°C 🥵  981‰
     $3 #37  ~7 exigence         42.86°C 🥵  950‰
     $4 #58  ~2 effort           41.65°C 🥵  942‰
     $5 #45  ~6 projet           39.60°C 🥵  918‰
     $6 #55  ~3 attente          35.48°C 😎  836‰
     $7 #23  ~9 discipline       28.07°C 😎  440‰
     $8 #35  ~8 cadre            28.05°C 😎  437‰
     $9 #48  ~5 vie              26.61°C 😎  282‰
    $10 #32     rigueur          24.24°C 🥶
    $11 #50     budget           23.82°C 🥶
    $12 #59     performance      23.45°C 🥶
    $13 #60     qualité          22.81°C 🥶
    $45 #14     cours            -1.95°C 🧊

# [Quordle Rescue](m-w.com/games/quordle/#/rescue) 🧩 #63 🥳 score:21 ⏱️ 0:01:14.719160

📜 1 sessions

Quordle Rescue m-w.com/games/quordle/

1. DROWN attempts:7 score:7
2. HIPPO attempts:6 score:6
3. DAIRY attempts:5 score:5
4. REACT attempts:3 score:3

# [Quordle Sequence](m-w.com/games/quordle/#/sequence) 🧩 #1449 🥳 score:28 ⏱️ 0:02:03.936217

📜 1 sessions

Quordle Sequence m-w.com/games/quordle/

1. BRING attempts:4 score:4
2. CHUNK attempts:5 score:5
3. PAPER attempts:9 score:9
4. SPICE attempts:10 score:10

# [Quordle Extreme](m-w.com/games/quordle/#/extreme) 🧩 #532 🥳 score:24 ⏱️ 0:01:56.369103

📜 1 sessions

Quordle Extreme m-w.com/games/quordle/

1. JAZZY attempts:7 score:7
2. LODGE attempts:8 score:8
3. NEWLY attempts:5 score:5
4. ALOFT attempts:4 score:4

# [Octordle Rescue](britannica.com/games/octordle/daily-rescue) 🧩 #1449 🥳 score:9 ⏱️ 0:03:18.736065

📜 1 sessions

Octordle Rescue

1. AWOKE attempts:5 score:5
2. FLOOD attempts:7 score:7
3. MANOR attempts:8 score:8
4. FERRY attempts:9 score:9
5. SWORD attempts:6 score:6
6. LIKEN attempts:10 score:10
7. STOLE attempts:11 score:11
8. PURER attempts:12 score:12

# [Octordle Sequence](britannica.com/games/octordle/daily-sequence) 🧩 #1449 🥳 score:64 ⏱️ 0:03:35.971420

📜 1 sessions

Octordle Sequence

1. STERN attempts:3 score:3
2. RUMBA attempts:5 score:5
3. NIGHT attempts:6 score:6
4. WORLD attempts:8 score:8
5. CHAMP attempts:9 score:9
6. ADMIN attempts:10 score:10
7. SPRAY attempts:11 score:11
8. MANGY attempts:12 score:12

# [Octordle Extreme](britannica.com/games/octordle/extreme) 🧩 #1449 🥳 score:55 ⏱️ 0:03:16.721232

📜 1 sessions

Octordle Extreme

1. MESSY attempts:6 score:6
2. COAST attempts:2 score:2
3. THROB attempts:8 score:8
4. DIRGE attempts:4 score:4
5. RHYME attempts:5 score:5
6. BLEEP attempts:9 score:9
7. BROTH attempts:10 score:10
8. HUNKY attempts:11 score:11
