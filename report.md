# 2025-09-20

- 🔗 spaceword.org 🧩 2025-09-19 🏗️ score 2173 current ranking 16/284 ⏱️ 15:33:45.014345

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





# spaceword.org 🧩 2025-09-19 🏗️ score 2173 current ranking 16/284 ⏱️ 15:33:45.014345

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 16/284

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ J _ H E X A G O N   
      _ U _ O _ _ V _ N E   
      _ G E O I D A L _ T   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

