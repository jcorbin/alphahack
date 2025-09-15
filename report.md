# 2025-09-16

- 🔗 spaceword.org 🧩 2025-09-15 🏁 score 2168 ranked 39.5% 170/430 ⏱️ 4:41:33.381056
- 🔗 alfagok.diginaut.net 🧩 #318 🥳 8 ⏱️ 0:04:15.957492
- 🔗 alphaguess.com 🧩 #784 🥳 8 ⏱️ 0:07:12.125705
- 🔗 cemantix.certitudes.org 🧩 #1294 🥳 1169 ⏱️ 0:30:21.671576
- 🔗 squareword.org 🧩 #1324 🥳 8 ⏱️ 0:42:44.540615
- 🔗 dictionary.com hurdle 🧩 #1354 🥳 19 ⏱️ 0:50:19.654455
- 🔗 dontwordle.com 🧩 #1211 🥳 6 ⏱️ 0:53:45.853719
- 🔗 cemantle.certitudes.org 🧩 #1261 🥳 50 ⏱️ 0:54:25.393065

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

# spaceword.org 🧩 2025-09-15 🏁 score 2168 ranked 39.5% 170/430 ⏱️ 4:41:33.381056

📜 8 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 170/430

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ K N A R _ _ _   
      _ _ _ _ _ _ A _ _ _   
      _ _ _ Q U I D _ _ _   
      _ _ _ _ N _ O _ _ _   
      _ _ _ _ R U M _ _ _   
      _ _ _ _ O _ E _ _ _   
      _ _ _ _ O F _ _ _ _   
      _ _ _ _ F E Z _ _ _   
      _ _ _ _ _ _ _ _ _ _   

# alfagok.diginaut.net 🧩 #318 🥳 8 ⏱️ 0:04:15.957492

🤔 8 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199853 [199853] lijm      q0 ? after
    @+299778 [299778] schub     q1 ? after
    @+349564 [349564] vakantie  q2 ? after
    @+374308 [374308] vrij      q3 ? after
    @+375753 [375753] vuur      q7 ? it
    @+375753 [375753] vuur      done. it
    @+377371 [377371] wandel    q6 ? before
    @+380520 [380520] weer      q5 ? before
    @+386849 [386849] wind      q4 ? before

# alphaguess.com 🧩 #784 🥳 8 ⏱️ 0:07:12.125705

🤔 8 attempts
📜 1 sessions

    @        [     0] aa     
    @+1      [     1] aah    
    @+2      [     2] aahed  
    @+3      [     3] aahing 
    @+98232  [ 98232] mach   q0 ? after
    @+104180 [104180] miri   q4 ? after
    @+107136 [107136] mort   q5 ? after
    @+108596 [108596] mus    q6 ? after
    @+109363 [109363] nail   q7 ? it
    @+109363 [109363] nail   done. it
    @+110137 [110137] need   q3 ? before
    @+122117 [122117] par    q2 ? before
    @+147337 [147337] rho    q1 ? before

# cemantix.certitudes.org 🧩 #1294 🥳 1169 ⏱️ 0:30:21.671576

🤔 1170 attempts
📜 1 sessions
🫧 51 chat sessions
⁉️ 305 chat prompts
🤖 229 llama3.2:latest replies
🤖 76 gemma3:12b replies
😱   1 🔥   3 🥵  22 😎 157 🥶 856 🧊 130

       $1 #1170    ~1 impuissant         100.00°C 🥳 1000‰
       $2 #1137    ~8 incapable           64.11°C 😱  999‰
       $3  #161  ~152 impuissance         61.96°C 🔥  998‰
       $4  #768   ~54 vain                51.91°C 🔥  995‰
       $5  #126  ~164 désespoir           47.98°C 🔥  991‰
       $6 #1064   ~21 malheureux          47.74°C 🥵  988‰
       $7   #94  ~177 désastre            47.23°C 🥵  984‰
       $8  #935   ~33 force               45.83°C 🥵  980‰
       $9  #119  ~167 fatalité            45.31°C 🥵  978‰
      $10   #99  ~173 malheur             44.89°C 🥵  976‰
      $11  #399  ~107 lutter              44.21°C 🥵  973‰
      $28  #200  ~138 oppression          40.59°C 😎  897‰
     $185  #114       anarchie            31.45°C 🥶
    $1041 #1147       étalon              -0.02°C 🧊

# squareword.org 🧩 #1324 🥳 8 ⏱️ 0:42:44.540615

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P U D S
    P A N E L
    A G I L E
    M A T T E
    S N E A K

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1354 🥳 19 ⏱️ 0:50:19.654455

📜 1 sessions
💰 score: 9700

    4/6
    SABER ⬜🟨⬜⬜⬜
    LIANG 🟩⬜🟩⬜⬜
    LOATH 🟩⬜🟩⬜⬜
    LLAMA 🟩🟩🟩🟩🟩
    5/6
    LLAMA ⬜⬜⬜⬜⬜
    CORES ⬜⬜⬜⬜⬜
    INPUT 🟨🟨⬜⬜🟨
    THING 🟩⬜🟩🟩🟩
    TYING 🟩🟩🟩🟩🟩
    4/6
    TYING ⬜⬜🟩⬜⬜
    SLICE 🟩⬜🟩⬜⬜
    SKIMP 🟩🟨🟩🟨⬜
    SMIRK 🟩🟩🟩🟩🟩
    5/6
    SMIRK ⬜⬜🟨⬜⬜
    TELIC 🟨⬜⬜🟨⬜
    NIGHT ⬜🟩⬜⬜🟨
    BIOTA ⬜🟩⬜🟩⬜
    FIFTY 🟩🟩🟩🟩🟩
    Final 1/2
    SLIDE 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1211 🥳 6 ⏱️ 0:53:45.853719

📜 1 sessions
💰 score: 10

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:YUMMY n n n n n remain:7572
    ⬜⬜⬜⬜⬜ tried:NANAS n n n n n remain:1373
    ⬜⬜⬜⬜⬜ tried:WOWEE n n n n n remain:122
    ⬜⬜⬜⬜🟩 tried:PHPHT n n n n Y remain:13
    ⬜🟨⬜⬜🟩 tried:ZIZIT n m n n Y remain:8
    ⬜🟨🟩⬜🟩 tried:BRITT n m Y n Y remain:1

    Undos used: 4

      1 words remaining
    x 10 unused letters
    = 10 total score

# cemantle.certitudes.org 🧩 #1261 🥳 50 ⏱️ 0:54:25.393065

🤔 51 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 10 chat prompts
🤖 10 gemma3:12b replies
🥵  3 😎  2 🥶 41 🧊  4

     $1 #51  ~1 shine          100.00°C 🥳 1000‰
     $2 #38  ~5 luster          44.50°C 🥵  988‰
     $3 #49  ~3 glow            44.03°C 🥵  987‰
     $4 #50  ~2 radiance        37.28°C 🥵  963‰
     $5 #48  ~4 brilliance      32.11°C 😎  887‰
     $6 #28  ~6 dark            32.00°C 😎  884‰
     $7 #37     gloom           22.81°C 🥶
     $8 #31     celestial       22.38°C 🥶
     $9 #16     bang            18.89°C 🥶
    $10 #40     murk            18.40°C 🥶
    $11 #14     astronomy       16.97°C 🥶
    $12 #46     progression     16.44°C 🥶
    $13 #43     penumbra        15.44°C 🥶
    $48 #22     hypothesis      -1.07°C 🧊

