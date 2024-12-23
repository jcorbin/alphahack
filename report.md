# 2025-09-19

- 🔗 spaceword.org 🧩 2025-09-18 🏁 score 2170 ranked 19.5% 76/390 ⏱️ 2:07:43.747698
- 🔗 alfagok.diginaut.net 🧩 #321 🥳 21 ⏱️ 0:05:34.018623
- 🔗 alphaguess.com 🧩 #787 🥳 12 ⏱️ 0:16:51.058037
- 🔗 squareword.org 🧩 #1327 🥳 9 ⏱️ 0:21:38.974094
- 🔗 dictionary.com hurdle 🧩 #1357 🥳 20 ⏱️ 0:07:28.520670
- 🔗 dontwordle.com 🧩 #1214 🥳 6 ⏱️ 0:09:53.959130
- 🔗 cemantle.certitudes.org 🧩 #1264 🥳 438 ⏱️ 0:20:26.604629
- 🔗 cemantix.certitudes.org 🧩 #1297 🥳 450 ⏱️ 0:33:36.337306

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




# spaceword.org 🧩 2025-09-18 🏁 score 2170 ranked 19.5% 76/390 ⏱️ 2:07:43.747698

📜 2 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 76/390

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ F O Y _ _ _ _   
      _ _ _ _ U _ U M _ _   
      _ _ _ _ R _ N A _ _   
      _ _ _ V A R I X _ _   
      _ _ _ O R E _ _ _ _   
      _ _ _ W I D E _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #321 🥳 21 ⏱️ 0:05:34.018623

🤔 21 attempts
📜 1 sessions

    @        [     0] &-teken        
    @+1      [     1] &-tekens       
    @+2      [     2] -cijferig      
    @+3      [     3] -e-mail        
    @+199853 [199853] lijm           q0  ? after
    @+299778 [299778] schub          q1  ? after
    @+311948 [311948] spier          q5  ? after
    @+314657 [314657] st             q6  ? after
    @+319452 [319452] stik           q7  ? after
    @+321900 [321900] straten        q8  ? after
    @+323125 [323125] structuralist  q9  ? after
    @+323208 [323208] struikel       q12 ? after
    @+323254 [323254] struis         q13 ? after
    @+323285 [323285] stuc           q16 ? after
    @+323294 [323294] studeer        q17 ? after
    @+323300 [323300] studeerkamer   q18 ? after
    @+323306 [323306] studeervertrek q19 ? after
    @+323308 [323308] student        q20 ? it
    @+323308 [323308] student        done. it
    @+323312 [323312] studenten      q11 ? before
    @+323512 [323512] studie         q10 ? before
    @+324353 [324353] sub            q3  ? after
    @+324353 [324353] sub            q4  ? before
    @+349562 [349562] vakantie       q2  ? before

# alphaguess.com 🧩 #787 🥳 12 ⏱️ 0:16:51.058037

🤔 12 attempts
📜 1 sessions

    @        [     0] aa      
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98232  [ 98232] mach    q0  ? after
    @+147337 [147337] rho     q1  ? after
    @+171937 [171937] tag     q2  ? after
    @+182024 [182024] un      q3  ? after
    @+189287 [189287] vicar   q4  ? after
    @+192891 [192891] whir    q5  ? after
    @+193507 [193507] win     q7  ? after
    @+194087 [194087] wo      q8  ? after
    @+194288 [194288] wood    q9  ? after
    @+194501 [194501] word    q10 ? after
    @+194531 [194531] work    q11 ? it
    @+194531 [194531] work    done. it
    @+194716 [194716] worship q6  ? before

# squareword.org 🧩 #1327 🥳 9 ⏱️ 0:21:38.974094

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟨 🟨 🟨 🟨 🟩
    🟩 🟨 🟨 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C R E P T
    L E V E E
    A V E R S
    M E R I T
    S L Y L Y

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1357 🥳 20 ⏱️ 0:07:28.520670

📜 1 sessions
💰 score: 9600

    5/6
    OSTIA 🟨⬜⬜⬜⬜
    VOMER ⬜🟩⬜🟨⬜
    YODLE ⬜🟩⬜🟩🟩
    JOULE ⬜🟩⬜🟩🟩
    NOBLE 🟩🟩🟩🟩🟩
    4/6
    NOBLE 🟨⬜⬜🟨⬜
    LIGAN 🟨⬜🟨🟨🟨
    GLANS 🟨🟩🟩🟩🟨
    SLANG 🟩🟩🟩🟩🟩
    6/6
    SLANG 🟨⬜🟩⬜⬜
    DEARS ⬜⬜🟩⬜🟨
    QUASI ⬜⬜🟩🟩⬜
    CHASM ⬜⬜🟩🟩⬜
    BOAST ⬜⬜🟩🟩🟩
    AVAST 🟩🟩🟩🟩🟩
    4/6
    AVAST 🟨⬜🟨⬜⬜
    LARUM ⬜🟩⬜⬜⬜
    CAPON ⬜🟩🟨⬜🟩
    PAGAN 🟩🟩🟩🟩🟩
    Final 1/2
    PECAN 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1214 🥳 6 ⏱️ 0:09:53.959130

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:JUJUS n n n n n remain:5557
    ⬜⬜⬜⬜⬜ tried:RADAR n n n n n remain:1383
    ⬜⬜⬜⬜⬜ tried:INFIX n n n n n remain:453
    ⬜⬜⬜⬜⬜ tried:GHYLL n n n n n remain:76
    ⬜🟩⬜⬜⬜ tried:KEEVE n Y n n n remain:5
    🟨🟩🟨⬜🟩 tried:PETTO m Y m n Y remain:1

    Undos used: 5

      1 words remaining
    x 6 unused letters
    = 6 total score

# cemantle.certitudes.org 🧩 #1264 🥳 438 ⏱️ 0:20:26.604629

🤔 439 attempts
📜 1 sessions
🫧 16 chat sessions
⁉️ 102 chat prompts
🤖 15 llama3.2:latest replies
🤖 87 gemma3:12b replies
😱   1 🔥   3 🥵  19 😎  50 🥶 335 🧊  30

      $1 #439   ~1 specialize       100.00°C 🥳 1000‰
      $2 #316  ~33 specialized       65.36°C 😱  999‰
      $3 #427   ~4 specialization    52.74°C 🔥  997‰
      $4 #340  ~28 niche             42.42°C 🔥  994‰
      $5 #392   ~8 specialist        39.82°C 🔥  990‰
      $6 #342  ~26 dedicated         39.45°C 🥵  989‰
      $7 #368  ~12 concentrated      38.78°C 🥵  987‰
      $8 #433   ~3 focus             38.14°C 🥵  984‰
      $9 #434   ~2 concentrate       37.76°C 🥵  982‰
     $10 #315  ~34 focused           37.71°C 🥵  981‰
     $11 #403   ~6 expertise         37.25°C 🥵  979‰
     $25 #154  ~55 carpentry         29.09°C 😎  897‰
     $75 #297      distinct          19.54°C 🥶
    $410 #332      measured          -0.07°C 🧊

# cemantix.certitudes.org 🧩 #1297 🥳 450 ⏱️ 0:33:36.337306

🤔 451 attempts
📜 1 sessions
🫧 18 chat sessions
⁉️ 106 chat prompts
🤖 15 llama3.2:latest replies
🤖 91 gemma3:12b replies
😱   1 🔥   3 🥵  21 😎  88 🥶 288 🧊  49

      $1 #451   ~1 confortable       100.00°C 🥳 1000‰
      $2 #115  ~92 confort            69.51°C 😱  999‰
      $3 #262  ~45 agréable           59.19°C 🔥  997‰
      $4 #366  ~15 élégant            50.01°C 🔥  992‰
      $5 #345  ~20 luxueux            49.78°C 🔥  991‰
      $6 #314  ~28 douillet           49.40°C 🥵  989‰
      $7 #261  ~46 accueillant        45.29°C 🥵  979‰
      $8 #202  ~67 maniable           44.34°C 🥵  976‰
      $9 #413   ~8 couchette          44.31°C 🥵  975‰
     $10 #221  ~58 facile             43.86°C 🥵  972‰
     $11 #264  ~43 chaleureux         43.10°C 🥵  970‰
     $27  #51 ~106 rangement          36.73°C 😎  898‰
    $115 #106      fonctionnel        22.58°C 🥶
    $403 #162      rationalité        -0.06°C 🧊
