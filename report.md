# 2025-09-17

- 🔗 spaceword.org 🧩 2025-09-16 🏁 score 2168 ranked 40.3% 164/407 ⏱️ 0:58:56.777023
- 🔗 alfagok.diginaut.net 🧩 #319 🥳 14 ⏱️ 0:00:45.577637
- 🔗 alphaguess.com 🧩 #785 🥳 14 ⏱️ 0:01:18.882567
- 🔗 squareword.org 🧩 #1325 🥳 8 ⏱️ 0:04:57.925510
- 🔗 dictionary.com hurdle 🧩 #1355 🥳 17 ⏱️ 0:08:20.903579
- 🔗 dontwordle.com 🧩 #1212 😳 6 ⏱️ 0:05:41.556055
- 🔗 cemantle.certitudes.org 🧩 #1262 🥳 97 ⏱️ 0:07:03.228052
- 🔗 cemantix.certitudes.org 🧩 #1295 🥳 438 ⏱️ 0:13:59.774138

# Dev

## WIP

- [rc] missing puzzle id from hurdle and dontwordle should now be fixed
  - ... and follow on result handling improvement
- [rc] generalized { semantic => ui }.retry ; reuse for chat iteration
- [rc] clipboard attribution
- [rc] tracer evolution
- [rc] more comprehensive tracing
  - dispatcher token handling
  - ui log opening

- [testing] fin ephemeral stored log works now...
  - [ ] ... but dumps back into continue state, rather than stop-ing back
    out to the meta prompt
- [testing] standard /store command
- [testing] standard /site command with osc-8 linking for /site
- [testing] dynamic trace on/off used by meta

- [dev] meta run / share / day works well enough
  - blink shell mangles pasted emoji... any way to workaround this?

- [dev] binartic: pruned `press <Return> to finish` prompt

## TODO

- BUG infinite spin loop at tail of space store
  ```
  [prior:2168]> /store
  🔺 '/store' -> StoredLog.cmd_store
  🔺 -> StoredLog.store
  🔺 StoredLog.store
  🔗 spaceword.org 🧩 2025-09-15 📆 2025-09-15
  📁🪓 log/spaceword.org/2025-09-15
  📁🔗 spaceword.log -> log/spaceword.org/2025-09-15
  📜➕ log/spaceword.org/2025-09-15
  [dev 4f7bb3b9] spaceword.org day 2025-09-15
   1 file changed, 1723 insertions(+)
  🗃️ spaceword.org day 2025-09-15
  📁🪓 spaceword.log
  🔺 store <!- cutover
  🔺   cutover.next.append(StoredLog.do_report)
  🔺   cutover.next.append(StoredLog.review_do_cont)
  🔺 -!> CutoverLogError('cutover to log/spaceword.org/2025-09-15')
  🔺 call_state <!- cutover
  🔺 cutover.resolve
  🔺   set_log_file log/spaceword.org/2025-09-15
  ^C
  while loading 'num_letters: 21'
   <INT>
   <INT>
  ```

  stored log continues dirty:
  ```
   TDD1673940 [prior:2168]> /store
  +TDD-1640655 num_letters: 21
  +TDD726806 num_letters: 21
  +TDD-760885 num_letters: 21
  +TDD-17 num_letters: 21
  +TDD-2 num_letters: 21
  +TDD-1 num_letters: 21
  +TDD0 num_letters: 21
  +TDD0 num_letters: 21
  ...
  ```

- BUG another space `fin -> should <STOP> but keeps going`
  ```
  📋> 🔺 -> StoredLog.finalize
  🔺 StoredLog.finalize -> StoredLog.store
  🔺 StoredLog.store
  🔗 spaceword.org 🧩 2025-09-14 📆 2025-09-14
  📁🪓 log/spaceword.org/2025-09-14
  📁🔗 spaceword.log.fin -> log/spaceword.org/2025-09-14
  📜➕ log/spaceword.org/2025-09-14
  [dev 642c1ae4] spaceword.org day 2025-09-14
   1 file changed, 14 insertions(+)
  🗃️ spaceword.org day 2025-09-14
  📁🪓 spaceword.log.fin
  🔺 store <!- cutover .next.append(StoredLog.do_report) .next.append(StoredLog.review_do_cont)
  🔺 -!> CutoverLogError('cutover to new log file')
  🔺 restart <!- cutover -> cutover to new log file
  🔺 -> cutover to new log file
  🔺 cutover to new log file
  📜➕ report.md
  [dev 94d1f0d1] DAILY spaceword.org
   1 file changed, 9 insertions(+), 9 deletions(-)
  🔺 -> <AGAIN>
  🔺 cutover to new log file
  ```
  - [dev] also make those cutover .next.append-s nicer
  - [dev] also call-out the cutover next state loop better

- fin then eof seems okay for now
  ```
  📋> 🔺 -> StoredLog.finalize
  🔺 StoredLog.finalize -> StoredLog.store
  🔺 StoredLog.store📆 2025-09-15 ?
  🔗 squareword.org 🧩 #1323 📆 2025-09-15
  📁🔗 squareword.log -> log/squareword.org/#1323
  📜➕ log/squareword.org/#1323
  [dev 0333965a] squareword.org day #1323
   1 file changed, 94 insertions(+)
   create mode 100644 log/squareword.org/#1323
  🗃️ squareword.org day #1323
  📁🪓 squareword.log
  🔺 store <!- cutover
  🔺   cutover.next.append(StoredLog.do_report)
  🔺   cutover.next.append(PromptUI.then_eof)
  🔺 -!> CutoverLogError('cutover to log/squareword.org/#1323')
  🔺 -!> CutoverLogError('cutover to log/squareword.org/#1323')
  🔺 -!> CutoverLogError('cutover to log/squareword.org/#1323')
  🔺 -!> CutoverLogError('cutover to log/squareword.org/#1323')
  🔺 -!> CutoverLogError('cutover to log/squareword.org/#1323')
  🔺 -!> CutoverLogError('cutover to log/squareword.org/#1323')
  🔺 -!> CutoverLogError('cutover to log/squareword.org/#1323')
  🔺 call_state <!- cutover -> cutover to log/squareword.org/#1323
  🔺 -> cutover to log/squareword.org/#1323
  🔺 cutover to log/squareword.org/#1323
  🔺 cutover ( StoredLog.do_report
  📜➕ report.md
  [dev 1208758d] DAILY squareword.org
   1 file changed, 22 insertions(+)
  🔺 )
  🔺 -> <AGAIN>
  🔺 cutover to log/squareword.org/#1323
  🔺 cutover ( PromptUI.then_eof )
  🔺 -!> <EOF>
   <EOF>
  🔺 -> <AGAIN>
  🔺 <__main__.Meta object at 0x7f8ef5006cf0>
  ```
  - the `-!> CutoverLogError` stutter is actually a hint at lacking trace
    instrumentation as it unrolls many nested `call_state` loops

- hmm `cutover.next.append(StoredLog.handle)` may be pending over entire
  continued run then...

  ```
  📜➕ log/spaceword.org/2025-09-15
  [dev fc6dddd0] spaceword.org day 2025-09-15
   1 file changed, 15626 insertions(+)
  🗃️ spaceword.org day 2025-09-15
  📁🪓 spaceword.log
  🔺 store <!- cutover
  🔺   cutover.next.append(StoredLog.do_report)
  🔺   cutover.next.append(StoredLog.review_do_cont)
  🔺 -!> CutoverLogError('cutover to log/spaceword.org/2025-09-15')
  🔺 call_state <!- cutover
  🔺 cutover.resolve
  🔺   set_log_file log/spaceword.org/2025-09-15
  🔺   cutover.next.append(StoredLog.handle)
  🔺 -> cutover to log/spaceword.org/2025-09-15
  🔺 -> cutover to log/spaceword.org/2025-09-15
  🔺 cutover to log/spaceword.org/2025-09-15
  🔺 cutover ( StoredLog.do_report
  📜➕ report.md
  [dev 258d48e3] DAILY spaceword.org
   1 file changed, 16 insertions(+), 14 deletions(-)
  🔺 )
  🔺 -> <AGAIN>
  🔺 cutover to log/spaceword.org/2025-09-15
  🔺 cutover ( StoredLog.review_do_cont
  *** 46460. T82.2 [prior:2164]> /store
  log file (default: spaceword.log) ?
  ^^^ continuing from last line
  🔺 starting ui log to 'spaceword.log' implicit
  🔺 <spaceword.SpaceWord object at 0x731802300550> -> StoredLog.handle
  🔺 StoredLog.handle
  🔺 redundant store.log_to to 'spaceword.log' implicit
  🔺 StoredLog.run
  📜 spaceword.log with 5 prior sessions over 1:40:46.078053
  ⏰ Expires 2025-09-16 00:00:00-04:00
  🔺 -> SpaceWord.startup
  🔺 SpaceWord.startup -> <ui.Prompt object at 0x73180234d940>
  🔺 <ui.Prompt object at 0x73180234d940>
  -<0 0 X>----------------
  ```

  confirmed:
  ```
  [prior:2164]> 🔺 -!> <EOF>
  🔺 -!> <EOF>
  🔺 )
  🔺 -> <AGAIN>
  🔺 cutover to log/spaceword.org/2025-09-15
  🔺 cutover -> StoredLog.handle
  🔺 -> StoredLog.handle
  🔺 StoredLog.handle
  🔺 starting ui log to 'spaceword.log' implicit
  🔺 StoredLog.run
  📜 spaceword.log with 5 prior sessions over 1:40:46.078053
  ⏰ Expires 2025-09-16 00:00:00-04:00
  🔺 -> SpaceWord.startup
  🔺 SpaceWord.startup -> <ui.Prompt object at 0x73180234d940>
  🔺 <ui.Prompt object at 0x73180234d940>
  ```

- long lines like these are hard to read; a line-breaking pretty formatter
  would be nice:
  ```
  🔺 -> functools.partial(<function Search.do_round.<locals>.wrap at 0x7f8ef4e0f100>, st=<wordlish.Question object at 0x7f8ef4e52e90>)
  🔺 functools.partial(<function Search.do_round.<locals>.wrap at 0x7f8ef4e0f100>, st=<wordlish.Question object at 0x7f8ef4e52e90>)#1 ____S ~E -ANT  📋 "elder" ? _L__S ~ ESD
  ```

- better meta
  - [ ] store daily share(d) state
  - [ ] better logic circa end of day early play, e.g. doing a CET timezone
        puzzle close late in the "prior" day local (EST) time
  - [ ] similarly, early play of next-day spaceword should work gracefully

- square: finish questioning work

- replay last paste to ease dev sometimes

- hurdle: spurious "next word" banner at end
  ```
  --- next word
  🔺 -!> <STOP>
  🔺 -> <SELF>
  🔺 Search.display -> Search.finish
  🔺 Search.finish -> StoredLog.finalize
  🔺 StoredLog.finalize
  Provide share result, then <EOF>
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

- expired prompt could be better:
  ```
  🔺 -> <ui.Prompt object at 0x754fdf9f6190>
  🔺 <ui.Prompt object at 0x754fdf9f6190>[f]inalize, [a]rchive, [r]emove, or [c]ontinue? rem
  🔺 'rem' -> StoredLog.expired_do_remove
  ```
  - `rm` alias
  - dynamically generated suggestion prompt, or at least one that's correct ( as "r" is ambiguously actually )


# spaceword.org 🧩 2025-09-16 🏁 score 2168 ranked 40.3% 164/407 ⏱️ 0:58:56.777023

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 164/407

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ P _ _ D _ _   
      _ F _ J O U K E D _   
      _ E _ _ U _ _ M O _   
      _ E X E R T I O N _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #319 🥳 14 ⏱️ 0:00:45.577637

🤔 14 attempts
📜 1 sessions

    @        [     0] &-teken       
    @+1      [     1] &-tekens      
    @+2      [     2] -cijferig     
    @+3      [     3] -e-mail       
    @+199853 [199853] lijm          q0  ? after
    @+299778 [299778] schub         q1  ? after
    @+349564 [349564] vakantie      q2  ? after
    @+353132 [353132] ver           q4  ? after
    @+363717 [363717] verzot        q5  ? after
    @+365657 [365657] vis           q7  ? after
    @+367009 [367009] vlieg         q8  ? after
    @+367049 [367049] vliegen       q13 ? it
    @+367049 [367049] vliegen       done. it
    @+367098 [367098] vlieger       q12 ? before
    @+367207 [367207] vliegt        q11 ? before
    @+367431 [367431] vliezig       q10 ? before
    @+367852 [367852] vluchtelingen q9  ? before
    @+368730 [368730] voetbal       q6  ? before
    @+374308 [374308] vrij          q3  ? before

# alphaguess.com 🧩 #785 🥳 14 ⏱️ 0:01:18.882567

🤔 14 attempts
📜 1 sessions

    @        [     0] aa       
    @+1      [     1] aah      
    @+2      [     2] aahed    
    @+3      [     3] aahing   
    @+98232  [ 98232] mach     q0  ? after
    @+147337 [147337] rho      q1  ? after
    @+159619 [159619] slug     q3  ? after
    @+162652 [162652] speed    q5  ? after
    @+163028 [163028] spin     q8  ? after
    @+163228 [163228] spit     q9  ? after
    @+163270 [163270] spiv     q11 ? after
    @+163279 [163279] splash   q13 ? it
    @+163279 [163279] splash   done. it
    @+163297 [163297] splat    q12 ? before
    @+163324 [163324] splendid q10 ? before
    @+163432 [163432] spodosol q7  ? before
    @+164212 [164212] squilgee q6  ? before
    @+165773 [165773] stint    q4  ? before
    @+171937 [171937] tag      q2  ? before

# squareword.org 🧩 #1325 🥳 8 ⏱️ 0:04:57.925510

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C A M S
    C A B I N
    A N O D E
    R O U G E
    E N T E R

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1355 🥳 17 ⏱️ 0:08:20.903579

📜 2 sessions
💰 score: 9900

    3/6
    TEALS ⬜🟨⬜🟩⬜
    OBELI ⬜⬜🟩🟩🟨
    YIELD 🟩🟩🟩🟩🟩
    4/6
    YIELD ⬜⬜⬜🟨⬜
    LOAMS 🟨🟨⬜⬜⬜
    GROWL ⬜🟩🟩🟩🟩
    PROWL 🟩🟩🟩🟩🟩
    4/6
    PROWL ⬜⬜⬜⬜🟨
    TAELS 🟨⬜🟨🟩⬜
    IXTLE ⬜🟩🟨🟩🟨
    EXULT 🟩🟩🟩🟩🟩
    4/6
    EXULT ⬜⬜🟨⬜⬜
    NURDS 🟨🟨⬜⬜🟩
    UNAIS 🟨🟨⬜🟨🟩
    MINUS 🟩🟩🟩🟩🟩
    Final 2/2
    ABMHO ⬜🟨🟩⬜🟩
    COMBO 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1212 😳 6 ⏱️ 0:05:41.556055

📜 1 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:REFER n n n n n remain:4802
    ⬜⬜⬜⬜⬜ tried:SLYLY n n n n n remain:1084
    ⬜⬜⬜⬜⬜ tried:MOTTO n n n n n remain:273
    ⬜⬜⬜⬜⬜ tried:HUNCH n n n n n remain:37
    ⬜🟩⬜⬜⬜ tried:KIBBI n Y n n n remain:3
    🟩🟩🟩🟩🟩 tried:PIZZA Y Y Y Y Y remain:0

    Undos used: 4

      0 words remaining
    x 0 unused letters
    = 0 total score

# cemantle.certitudes.org 🧩 #1262 🥳 97 ⏱️ 0:07:03.228052

🤔 98 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 20 chat prompts
🤖 20 gemma3:12b replies
🔥  1 🥵  5 😎 14 🥶 72 🧊  5

     $1 #98  ~1 motivate         100.00°C 🥳 1000‰
     $2 #94  ~4 energize          59.21°C 🔥  996‰
     $3 #97  ~2 excite            53.04°C 🥵  989‰
     $4 #83 ~13 invigorate        44.79°C 🥵  971‰
     $5 #76 ~17 elevate           43.08°C 🥵  963‰
     $6 #90  ~8 propel            41.35°C 🥵  954‰
     $7 #89  ~9 promote           39.01°C 🥵  925‰
     $8 #93  ~5 reinforce         37.88°C 😎  893‰
     $9 #91  ~7 push              37.45°C 😎  885‰
    $10 #73 ~19 amplify           35.56°C 😎  849‰
    $11 #82 ~14 improve           34.95°C 😎  827‰
    $12 #72 ~20 boost             31.59°C 😎  702‰
    $22 #57     hasten            24.78°C 🥶
    $94 #69     synchronization   -0.07°C 🧊

# cemantix.certitudes.org 🧩 #1295 🥳 438 ⏱️ 0:13:59.774138

🤔 439 attempts
📜 1 sessions
🫧 14 chat sessions
⁉️ 84 chat prompts
🤖 84 gemma3:12b replies
🔥   2 🥵  21 😎  59 🥶 346 🧊  10

      $1 #439   ~1 épais           100.00°C 🥳 1000‰
      $2  #91  ~77 grisâtre         56.12°C 🔥  997‰
      $3 #366  ~14 pelucheux        53.92°C 🔥  990‰
      $4 #327  ~26 floconneux       52.19°C 🥵  983‰
      $5 #280  ~39 spongieux        52.14°C 🥵  982‰
      $6 #344  ~22 écailleux        51.90°C 🥵  981‰
      $7 #354  ~18 alvéolé          51.86°C 🥵  980‰
      $8 #346  ~21 granuleux        51.75°C 🥵  978‰
      $9 #226  ~55 gélatineux       51.07°C 🥵  972‰
     $10 #275  ~41 lisse            50.51°C 🥵  971‰
     $11 #324  ~27 laineux          50.33°C 🥵  967‰
     $25 #110  ~73 sombre           45.23°C 😎  898‰
     $84  #37      brindille        33.78°C 🥶
    $430 #391      confiant         -0.56°C 🧊
