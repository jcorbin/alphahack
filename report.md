# 2025-09-18

- 🔗 spaceword.org 🧩 2025-09-17 🏁 score 2173 ranked 5.4% 23/429 ⏱️ 10:27:51.141296
- 🔗 alfagok.diginaut.net 🧩 #320 🥳 17 ⏱️ 0:02:23.561190
- 🔗 alphaguess.com 🧩 #786 🥳 17 ⏱️ 0:03:28.283299
- 🔗 squareword.org 🧩 #1326 🥳 9 ⏱️ 0:06:39.667616
- 🔗 dictionary.com hurdle 🧩 #1356 🥳 21 ⏱️ 0:11:12.754962
- 🔗 dontwordle.com 🧩 #1213 🥳 6 ⏱️ 0:12:38.716561
- 🔗 cemantle.certitudes.org 🧩 #1263 🥳 129 ⏱️ 0:01:31.924221
- 🔗 cemantix.certitudes.org 🧩 #1296 🥳 122 ⏱️ 0:05:50.888091

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



# spaceword.org 🧩 2025-09-17 🏁 score 2173 ranked 5.4% 23/429 ⏱️ 10:27:51.141296

📜 7 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 23/429

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ K I D _ _ _   
      _ _ _ _ _ _ U _ _ _   
      _ _ _ _ Q A T _ _ _   
      _ _ _ _ _ X I _ _ _   
      _ _ _ _ _ O F _ _ _   
      _ _ _ _ _ N U _ _ _   
      _ _ _ _ M E L _ _ _   
      _ _ _ _ U M _ _ _ _   
      _ _ _ _ S E E _ _ _   


# alfagok.diginaut.net 🧩 #320 🥳 17 ⏱️ 0:02:23.561190

🤔 17 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+199853 [199853] lijm       q0  ? after
    @+299778 [299778] schub      q1  ? after
    @+349564 [349564] vakantie   q2  ? after
    @+353132 [353132] ver        q4  ? after
    @+363717 [363717] verzot     q5  ? after
    @+368730 [368730] voetbal    q6  ? after
    @+369439 [369439] vol        q8  ? after
    @+369518 [369518] volg       q10 ? after
    @+369543 [369543] volgeling  q13 ? after
    @+369550 [369550] volgen     q14 ? after
    @+369551 [369551] volgend    done. it
    @+369552 [369552] volgende   q16 ? before
    @+369559 [369559] volgeplakt q15 ? before
    @+369567 [369567] volger     q12 ? before
    @+369618 [369618] volgroeide q11 ? before
    @+369717 [369717] volks      q9  ? before
    @+370579 [370579] voor       q7  ? before
    @+374308 [374308] vrij       q3  ? before

# alphaguess.com 🧩 #786 🥳 17 ⏱️ 0:03:28.283299

🤔 17 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+47393 [47393] dis       q1  ? after
    @+72813 [72813] gremolata q2  ? after
    @+85517 [85517] ins       q3  ? after
    @+91862 [91862] knot      q4  ? after
    @+93282 [93282] lar       q6  ? after
    @+93910 [93910] lea       q7  ? after
    @+94030 [94030] lean      q10 ? after
    @+94056 [94056] learn     q12 ? after
    @+94072 [94072] leas      q13 ? after
    @+94074 [94074] lease     q14 ? after
    @+94085 [94085] leash     q15 ? after
    @+94091 [94091] least     q16 ? it
    @+94091 [94091] least     done. it
    @+94095 [94095] leather   q11 ? before
    @+94164 [94164] lecithin  q9  ? before
    @+94423 [94423] leis      q8  ? before
    @+94959 [94959] lib       q5  ? before
    @+98232 [98232] mach      q0  ? before

# squareword.org 🧩 #1326 🥳 9 ⏱️ 0:06:39.667616

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟨 🟨 🟨
    🟨 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S W A T H
    M I T R E
    O D O U R
    T O N E D
    E W E R S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1356 🥳 21 ⏱️ 0:11:12.754962

📜 1 sessions
💰 score: 9500

    4/6
    SORTA ⬜⬜⬜⬜⬜
    KYLIN ⬜⬜🟨🟨⬜
    GLIDE ⬜🟨🟩⬜🟩
    WHILE 🟩🟩🟩🟩🟩
    5/6
    WHILE ⬜⬜⬜⬜🟨
    PRESA ⬜⬜🟨⬜⬜
    GODET ⬜🟨🟨🟨⬜
    DEMON 🟩🟩⬜🟩⬜
    DECOY 🟩🟩🟩🟩🟩
    4/6
    DECOY 🟩⬜⬜⬜⬜
    DUNTS 🟩⬜⬜⬜⬜
    DIRAM 🟩⬜🟨🟨🟨
    DRAMA 🟩🟩🟩🟩🟩
    6/6
    DRAMA ⬜⬜⬜⬜⬜
    LENTO ⬜🟨⬜⬜🟨
    COZES ⬜🟩⬜🟩⬜
    KOPEK ⬜🟩⬜🟩⬜
    FOGEY ⬜🟩🟨🟩🟩
    GOOEY 🟩🟩🟩🟩🟩
    Final 2/2
    RESAT 🟩🟩⬜🟩⬜
    REBAR 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1213 🥳 6 ⏱️ 0:12:38.716561

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:7042
    ⬜⬜⬜⬜⬜ tried:ADDAX n n n n n remain:2862
    ⬜⬜⬜⬜⬜ tried:JEEPS n n n n n remain:363
    ⬜⬜⬜⬜⬜ tried:VIGIL n n n n n remain:72
    ⬜⬜⬜⬜🟩 tried:MYRRH n n n n Y remain:3
    🟩🟩⬜🟩🟩 tried:COOCH Y Y n Y Y remain:1

    Undos used: 3

      1 words remaining
    x 6 unused letters
    = 6 total score

# cemantle.certitudes.org 🧩 #1263 🥳 129 ⏱️ 0:01:31.924221

🤔 130 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 24 chat prompts
🤖 24 gemma3:12b replies
😱  1 🔥  5 🥵 10 😎 26 🥶 84 🧊  3

      $1 #130   ~1 reflectance    100.00°C 🥳 1000‰
      $2  #50  ~27 reflectivity    69.82°C 😱  999‰
      $3  #82  ~16 transmittance   66.99°C 🔥  998‰
      $4  #73  ~21 illuminance     63.57°C 🔥  997‰
      $5  #74  ~20 luminance       59.75°C 🔥  993‰
      $6  #33  ~37 brightness      59.40°C 🔥  992‰
      $7  #47  ~30 photometry      57.55°C 🔥  990‰
      $8 #115   ~3 diffraction     55.63°C 🥵  986‰
      $9 #107   ~6 specular        55.40°C 🥵  983‰
     $10  #57  ~26 spectral        54.53°C 🥵  978‰
     $11  #43  ~32 luminosity      54.49°C 🥵  977‰
     $18  #59  ~25 translucency    48.12°C 😎  884‰
     $44 #108      ambient         34.97°C 🥶
    $128  #23      expansion       -1.01°C 🧊

# cemantix.certitudes.org 🧩 #1296 🥳 122 ⏱️ 0:05:50.888091

🤔 123 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 18 chat prompts
🤖 18 gemma3:12b replies
🔥  3 🥵  4 😎 19 🥶 75 🧊 21

      $1 #123   ~1 sauvetage       100.00°C 🥳 1000‰
      $2  #93   ~8 bouée            46.02°C 🔥  995‰
      $3 #113   ~5 canot            42.94°C 🔥  992‰
      $4  #33  ~20 remorqueur       41.67°C 🔥  991‰
      $5  #67  ~12 chalutier        37.78°C 🥵  977‰
      $6 #120   ~2 gilet            34.63°C 🥵  961‰
      $7  #51  ~19 hélicoptère      34.53°C 🥵  960‰
      $8  #11  ~26 marin            30.40°C 🥵  925‰
      $9  #24  ~22 amarrage         27.58°C 😎  899‰
     $10   #2  ~27 bateau           26.45°C 😎  876‰
     $11  #82  ~10 protection       24.15°C 😎  810‰
     $12  #63  ~15 atterrissage     23.35°C 😎  778‰
     $28  #25      coque            15.54°C 🥶
    $103  #56      stabilisateur    -0.14°C 🧊
