# 2025-12-25

- 🔗 spaceword.org 🧩 2025-12-24 🏁 score 2173 ranked 5.1% 16/316 ⏱️ 1:15:19.579719
- 🔗 alfagok.diginaut.net 🧩 #418 🥳 17 ⏱️ 0:00:48.161968
- 🔗 alphaguess.com 🧩 #884 🥳 12 ⏱️ 0:00:26.458791
- 🔗 squareword.org 🧩 #1424 🥳 7 ⏱️ 0:02:26.684213
- 🔗 dictionary.com hurdle 🧩 #1454 😦 18 ⏱️ 0:03:14.087601
- 🔗 dontwordle.com 🧩 #1311 😳 6 ⏱️ 0:01:32.234405
- 🔗 Quordle Classic 🧩 #1431 😦 score:30 ⏱️ 0:02:59.718361
- 🔗 Octordle Classic 🧩 #1431 🥳 score:52 ⏱️ 0:03:51.271294
- 🔗 cemantle.certitudes.org 🧩 #1361 🥳 710 ⏱️ 0:30:59.946856
- 🔗 cemantix.certitudes.org 🧩 #1394 🥳 27 ⏱️ 0:01:22.216949

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


# spaceword.org 🧩 2025-12-24 🏁 score 2173 ranked 5.1% 16/316 ⏱️ 1:15:19.579719

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 16/316

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ S O X _ _ _   
      _ _ _ _ O R _ _ _ _   
      _ _ _ _ _ Z A _ _ _   
      _ _ _ _ F O U _ _ _   
      _ _ _ _ I _ G _ _ _   
      _ _ _ _ Q _ E _ _ _   
      _ _ _ _ U _ R _ _ _   
      _ _ _ _ E T _ _ _ _   
      _ _ _ _ S I G _ _ _   


# alfagok.diginaut.net 🧩 #418 🥳 17 ⏱️ 0:00:48.161968

🤔 17 attempts
📜 1 sessions

    @        [     0] &-teken       >>> SEARCH
    @+1      [     1] &-tekens      
    @+2      [     2] -cijferig     
    @+3      [     3] -e-mail       
    @+99758  [ 99758] ex            q1  ? after
    @+149454 [149454] huis          q2  ? after
    @+162009 [162009] izabel        q4  ? after
    @+163550 [163550] jeugd         q7  ? after
    @+164331 [164331] joe           q9  ? after
    @+164667 [164667] jongeren      q10 ? after
    @+164778 [164778] jonggeboren   q14 ? after
    @+164830 [164830] jonker        q15 ? after
    @+164862 [164862] jood          q16 ? it
    @+164891 [164891] jopenbier     q13 ? before
    @+165113 [165113] ju            q6  ? before
    @+168278 [168278] kano          q5  ? before
    @+174561 [174561] kind          q3  ? before
    @+199833 [199833] lijm          q0  ? before
    @+399709 [399709] €50-biljetten <<< SEARCH

# alphaguess.com 🧩 #884 🥳 12 ⏱️ 0:00:26.458791

🤔 12 attempts
📜 1 sessions

    @        [     0] aa      >>> SEARCH
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98225  [ 98225] mach    q0  ? after
    @+147329 [147329] rho     q1  ? after
    @+159611 [159611] slug    q3  ? after
    @+165765 [165765] stint   q4  ? after
    @+168815 [168815] sulfur  q5  ? after
    @+170369 [170369] sustain q6  ? after
    @+170742 [170742] swift   q8  ? after
    @+170834 [170834] swink   q10 ? after
    @+170871 [170871] switch  q11 ? it
    @+170932 [170932] swoon   q9  ? before
    @+171137 [171137] symbol  q7  ? before
    @+171929 [171929] tag     q2  ? before
    @+196537 [196537] zzz     <<< SEARCH

# squareword.org 🧩 #1424 🥳 7 ⏱️ 0:02:26.684213

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T A T S
    T U L I P
    U N I T E
    D I V A N
    S C E N T

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1454 😦 18 ⏱️ 0:03:14.087601

📜 1 sessions
💰 score: 4880

    3/6
    STARE ⬜🟨🟨⬜🟩
    LATHE 🟩🟩🟩⬜🟩
    LATTE 🟩🟩🟩🟩🟩
    5/6
    LATTE ⬜🟩⬜⬜⬜
    CAINS ⬜🟩⬜⬜⬜
    PARDY ⬜🟩⬜⬜🟨
    BAYOU ⬜🟩🟩⬜⬜
    KAYAK 🟩🟩🟩🟩🟩
    4/6
    KAYAK ⬜⬜⬜⬜⬜
    TOURS ⬜🟨⬜🟨⬜
    WRONG 🟨🟩🟩🟨⬜
    CROWN 🟩🟩🟩🟩🟩
    4/6
    CROWN 🟩🟩⬜⬜⬜
    CRAPE 🟩🟩⬜⬜⬜
    CRIBS 🟩🟩⬜⬜🟨
    CRUST 🟩🟩🟩🟩🟩
    Final 2/2
    FILTH ⬜🟨🟨🟩⬜
    BLITZ ⬜🟩🟩🟩🟩
    FAIL: GLITZ

# dontwordle.com 🧩 #1311 😳 6 ⏱️ 0:01:32.234405

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:7870
    ⬜⬜⬜⬜⬜ tried:DOODY n n n n n remain:3300
    ⬜⬜⬜⬜⬜ tried:BULBS n n n n n remain:582
    ⬜🟩⬜⬜⬜ tried:PHPHT n Y n n n remain:25
    ⬜🟩🟨⬜⬜ tried:WHEEN n Y m n n remain:4
    🟩🟩🟩🟩🟩 tried:CHAFE Y Y Y Y Y remain:0

    Undos used: 3

      0 words remaining
    x 0 unused letters
    = 0 total score

# [Quordle Classic](m-w.com/games/quordle) 🧩 #1431 😦 score:30 ⏱️ 0:02:59.718361

📜 1 sessions

Quordle Classic m-w.com/games/quordle/

1. WARTY attempts:9 score:9
2. HARRY attempts:5 score:5
3. BLOND attempts:7 score:7
4. A_ION -BCDEHLPRSTVWY attempts:9 score:-1

# [Octordle Classic](https://www.britannica.com/games/octordle/daily) 🧩 #1431 🥳 score:52 ⏱️ 0:03:51.271294

📜 1 sessions

Octordle Classic

1. CLOSE attempts:8 score:8
2. BRING attempts:10 score:10
3. SLOOP attempts:9 score:9
4. BRAVO attempts:6 score:6
5. BIRTH attempts:7 score:7
6. SALON attempts:3 score:3
7. STONE attempts:4 score:4
8. KNACK attempts:5 score:5

# cemantle.certitudes.org 🧩 #1361 🥳 710 ⏱️ 0:30:59.946856

🤔 711 attempts
📜 1 sessions
🫧 42 chat sessions
⁉️ 218 chat prompts
🤖 124 dolphin3:latest replies
🤖 82 falcon3:10b replies
🤖 5 qwen3:32b replies
🤖 7 gemma3:27b replies
😱   1 🔥   6 🥵  16 😎 131 🥶 531 🧊  25

      $1 #711   ~1 organism          100.00°C 🥳 1000‰
      $2 #590  ~42 bacterium          77.45°C 😱  999‰
      $3 #613  ~32 microorganism      72.61°C 🔥  998‰
      $4 #584  ~45 microbe            71.73°C 🔥  997‰
      $5 #580  ~46 bacteria           67.59°C 🔥  996‰
      $6 #569  ~48 pathogen           65.00°C 🔥  994‰
      $7 #607  ~35 prokaryote         64.27°C 🔥  993‰
      $8 #649  ~17 parasite           63.48°C 🔥  991‰
      $9 #566  ~50 bacterial          62.05°C 🥵  989‰
     $10 #610  ~33 unicellular        61.87°C 🥵  988‰
     $11 #564  ~51 microbial          59.00°C 🥵  979‰
     $25 #289 ~107 epistasis          51.16°C 😎  899‰
    $156 #283      homozygote         37.90°C 🥶
    $687  #68      note               -0.23°C 🧊

# cemantix.certitudes.org 🧩 #1394 🥳 27 ⏱️ 0:01:22.216949

🤔 28 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 6 chat prompts
🤖 6 falcon3:10b replies
😎  3 🥶 18 🧊  6

     $1 #28  ~1 aube          100.00°C 🥳 1000‰
     $2  #4  ~4 lune           23.09°C 😎  702‰
     $3 #23  ~2 rêve           20.21°C 😎  334‰
     $4 #21  ~3 fleuve         19.67°C 😎  223‰
     $5 #10     étoile         17.75°C 🥶
     $6 #27     amour          15.81°C 🥶
     $7 #15     arbre          13.19°C 🥶
     $8 #11     lunaire        13.09°C 🥶
     $9  #5     montagne       12.94°C 🥶
    $10 #22     plume          12.83°C 🥶
    $11  #3     jardin         11.27°C 🥶
    $12 #26     étoffe          8.69°C 🥶
    $13  #1     bateau          8.43°C 🥶
    $23  #7     poisson        -0.26°C 🧊
