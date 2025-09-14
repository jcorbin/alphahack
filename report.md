# 2025-09-15

- 🔗 spaceword.org 🧩 2025-09-14 🏁 score 2168 ranked 25.5% 102/400 ⏱️ 1:10:32.564710
- 🔗 alfagok.diginaut.net 🧩 #317 🥳 16 ⏱️ 0:01:03.394499
- 🔗 alphaguess.com 🧩 #783 🥳 14 ⏱️ 0:28:42.967004
- 🔗 squareword.org 🧩 #1323 🥳 6 ⏱️ 0:03:43.818870
- 🔗 dictionary.com hurdle 🧩 #1353 🥳 20 ⏱️ 0:13:40.746626
- 🔗 dontwordle.com 🧩 #1210 🥳 6 ⏱️ 0:06:47.054223
- 🔗 cemantle.certitudes.org 🧩 #1260 🥳 14 ⏱️ 0:07:38.181246
- 🔗 cemantix.certitudes.org 🧩 #1293 🥳 165 ⏱️ 0:10:14.375642

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

- long lines like these are hard to read; a line-breaking pretty formatter
  would be nice:
  ```
  🔺 -> functools.partial(<function Search.do_round.<locals>.wrap at 0x7f8ef4e0f100>, st=<wordlish.Question object at 0x7f8ef4e52e90>)
  🔺 functools.partial(<function Search.do_round.<locals>.wrap at 0x7f8ef4e0f100>, st=<wordlish.Question object at 0x7f8ef4e52e90>)#1 ____S ~E -ANT  📋 "elder" ? _L__S ~ ESD
  ```

- BUG infinite spin loop at tail of space store
  ```
  📁🪓 spaceword.log
  🔺 -!> CutoverLogError('cutover to new log file')
  
  ^Cwhile loading 'num_letters: 21'
   <INT>
   <INT>
  (alphaguess) ~/alphaguess dev 2231dff7 !?%
  ```

  stored log continues dirty:
  ```
   TDD2758166 [prior:2168]> /store
  +TDD-2742579 num_letters: 21
  +TDD114658 num_letters: 21
  +TDD-131058 num_letters: 21
  +TDD-9 num_letters: 21
  +TDD-3 num_letters: 21
  +TDD-1 num_letters: 21
  +TDD0 num_letters: 21
  +TDD0 num_letters: 21
  +TDD0 num_letters: 21
  +TDD0 num_letters: 21
  +TDD0 num_letters: 21
  +TDD0 num_letters: 21
  +TDD0 num_letters: 21
  +TDD0 num_letters: 21
  +TDD0 num_letters: 21
  +TDD0 num_letters: 21
  +TDD0 num_letters: 21
  +TDD0 num_letters: 21
  +TDD0 num_letters: 21
  +TDD0 num_letters: 21
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



# spaceword.org 🧩 2025-09-14 🏁 score 2168 ranked 25.5% 102/400 ⏱️ 1:10:32.564710

📜 6 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 102/400

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ Z _ _ _ J _ Q _ _   
      _ O _ N I O B I C _   
      _ O _ _ _ L A _ U _   
      _ M I T I E R _ T _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #317 🥳 16 ⏱️ 0:01:03.394499

🤔 16 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199853 [199853] lijm      q0  ? after
    @+223653 [223653] mol       q3  ? after
    @+235712 [235712] octetten  q4  ? after
    @+237211 [237211] om        q6  ? after
    @+238020 [238020] ompalen   q7  ? after
    @+238422 [238422] omtover   q8  ? after
    @+238428 [238428] omtrek    q12 ? after
    @+238439 [238439] omtrekt   q13 ? after
    @+238443 [238443] omtrent   q15 ? it
    @+238443 [238443] omtrent   done. it
    @+238446 [238446] omtuind   q14 ? before
    @+238453 [238453] omvaamt   q11 ? before
    @+238483 [238483] omver     q10 ? before
    @+238622 [238622] omwikkel  q9  ? before
    @+238829 [238829] on        q5  ? before
    @+247771 [247771] op        q2  ? before
    @+299778 [299778] schub     q1  ? before

# alphaguess.com 🧩 #783 🥳 14 ⏱️ 0:28:42.967004

🤔 14 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+23694 [23694] camp       q2  ? after
    @+35537 [35537] convention q3  ? after
    @+38196 [38196] crazy      q5  ? after
    @+38848 [38848] crop       q7  ? after
    @+38872 [38872] cross      q9  ? after
    @+38974 [38974] crostini   q11 ? after
    @+38991 [38991] crouch     q13 ? it
    @+38991 [38991] crouch     done. it
    @+39013 [39013] crow       q12 ? before
    @+39074 [39074] cru        q8  ? before
    @+39514 [39514] cud        q6  ? before
    @+40853 [40853] da         q4  ? before
    @+47393 [47393] dis        q1  ? before
    @+98232 [98232] mach       q0  ? before

# squareword.org 🧩 #1323 🥳 6 ⏱️ 0:03:43.818870

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S L E D S
    T I B I A
    A B B O T
    R E E D Y
    E L D E R

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1353 🥳 20 ⏱️ 0:13:40.746626

📜 2 sessions
💰 score: 9600

    3/6
    STOAE 🟩⬜⬜🟨🟩
    SCARE 🟩⬜🟩⬜🟩
    SHAKE 🟩🟩🟩🟩🟩
    5/6
    SHAKE 🟨⬜⬜⬜⬜
    TORSI ⬜🟩⬜🟨⬜
    DOUMS ⬜🟩⬜🟩🟩
    BOOMS ⬜🟩🟩🟩🟩
    ZOOMS 🟩🟩🟩🟩🟩
    5/6
    ZOOMS ⬜⬜⬜⬜⬜
    DEAIR ⬜⬜⬜🟨🟨
    FRITH ⬜🟨🟨🟩🟩
    BIRTH ⬜🟩🟩🟩🟩
    GIRTH 🟩🟩🟩🟩🟩
    6/6
    GIRTH ⬜⬜🟨⬜⬜
    DEARS 🟨🟨⬜🟨⬜
    UREDO ⬜🟨🟨🟨🟨
    ROWED 🟨🟨⬜🟩🟨
    OLDER 🟩⬜🟩🟩🟩
    ODDER 🟩🟩🟩🟩🟩
    Final 1/2
    ISSUE 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1210 🥳 6 ⏱️ 0:06:47.054223

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:REBBE n n n n n remain:4579
    ⬜⬜⬜⬜⬜ tried:JUJUS n n n n n remain:1530
    ⬜⬜⬜⬜⬜ tried:KININ n n n n n remain:481
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:182
    ⬜🟩⬜⬜⬜ tried:DOGGO n Y n n n remain:28
    ⬜🟩⬜⬜🟨 tried:COMMA n Y n n m remain:1

    Undos used: 3

      1 words remaining
    x 8 unused letters
    = 8 total score

# cemantle.certitudes.org 🧩 #1260 🥳 14 ⏱️ 0:07:38.181246

🤔 15 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 4 chat prompts
🤖 4 gemma3:12b replies
🔥 1 🥵 1 😎 1 🥶 8 🧊 3

     $1 #15  ~1 arena       100.00°C 🥳 1000‰
     $2 #14  ~2 stadium      60.31°C 😱  999‰
     $3 #12  ~3 pavilion     40.65°C 🥵  988‰
     $4  #3  ~4 gazebo       17.97°C 😎  205‰
     $5 #13     canopy       13.80°C 🥶
     $6  #8     synergy      10.01°C 🥶
     $7  #2     azure         5.10°C 🥶
     $8 #11     garden        4.66°C 🥶
     $9 #10     xenophobia    4.51°C 🥶
    $10  #6     pylon         4.33°C 🥶
    $11  #5     oboe          2.96°C 🥶
    $12  #7     quartz        0.90°C 🥶
    $13  #4     melancholy   -0.48°C 🧊
    $14  #9     velocity     -3.83°C 🧊

# cemantix.certitudes.org 🧩 #1293 🥳 165 ⏱️ 0:10:14.375642

🤔 166 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 33 chat prompts
🤖 33 gemma3:12b replies
😱  1 🔥  2 🥵 14 😎 48 🥶 88 🧊 12

      $1 #166   ~1 espérance        100.00°C 🥳 1000‰
      $2 #108  ~29 espoir            61.70°C 😱  999‰
      $3  #87  ~40 foi               49.19°C 🔥  998‰
      $4  #29  ~63 joie              43.62°C 🔥  990‰
      $5 #115  ~26 consolation       40.70°C 🥵  982‰
      $6  #50  ~56 bonheur           40.57°C 🥵  981‰
      $7  #40  ~59 promesse          40.02°C 🥵  978‰
      $8 #112  ~27 communion         39.34°C 🥵  972‰
      $9 #162   ~4 optimisme         39.21°C 🥵  970‰
     $10  #83  ~42 certitude         38.80°C 🥵  968‰
     $11  #57  ~54 éternel           37.57°C 🥵  961‰
     $19  #88  ~39 générosité        33.18°C 😎  886‰
     $67  #26      déclin            21.92°C 🥶
    $155   #3      chocolat          -0.91°C 🧊
