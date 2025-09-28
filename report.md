# 2025-09-29

- 🔗 spaceword.org 🧩 2025-09-28 🏁 score 2173 ranked 6.8% 27/398 ⏱️ 1:19:22.310993
- 🔗 alfagok.diginaut.net 🧩 #331 🥳 17 ⏱️ 0:01:21.202960
- 🔗 alphaguess.com 🧩 #797 🥳 16 ⏱️ 0:02:15.993488
- 🔗 squareword.org 🧩 #1337 🥳 7 ⏱️ 0:04:55.505833
- 🔗 dictionary.com hurdle 🧩 #1367 🥳 17 ⏱️ 0:08:10.036088
- 🔗 dontwordle.com 🧩 #1224 🥳 6 ⏱️ 0:09:52.346268
- 🔗 cemantle.certitudes.org 🧩 #1274 🥳 287 ⏱️ 0:22:08.311034
- 🔗 cemantix.certitudes.org 🧩 #1307 🥳 127 ⏱️ 0:13:54.132645

# Dev

## WIP

- square: finish questioning work
- meta: output wrapping towards abstracting out a PromptUI output protocol

## TODO

- long lines like these are hard to read; a line-breaking pretty formatter
  would be nice:
  ```
  🔺 -> functools.partial(<function Search.do_round.<locals>.wrap at 0x7f8ef4e0f100>, st=<wordlish.Question object at 0x7f8ef4e52e90>)
  🔺 functools.partial(<function Search.do_round.<locals>.wrap at 0x7f8ef4e0f100>, st=<wordlish.Question object at 0x7f8ef4e52e90>)#1 ____S ~E -ANT  📋 "elder" ? _L__S ~ ESD
  ```

- meta:
  - [ ] store daily share(d) state
  - [ ] better logic circa end of day early play, e.g. doing a CET timezone
        puzzle close late in the "prior" day local (EST) time
  - [ ] similarly, early play of next-day spaceword should work gracefully
  - [ ] support other intervals like weekly/monthly for spaceword

- ui: [disabled] thrash detection works too well
  - triggers on semantic's extract-next-token tight loop
  - best way to reliably fix it is to capture per-round output, and only count
    thrash if output is looping

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

- expired prompt could be better:
  ```
  🔺 -> <ui.Prompt object at 0x754fdf9f6190>
  🔺 <ui.Prompt object at 0x754fdf9f6190>[f]inalize, [a]rchive, [r]emove, or [c]ontinue? rem
  🔺 'rem' -> StoredLog.expired_do_remove
  ```
  - `rm` alias
  - dynamically generated suggestion prompt, or at least one that's correct ( as "r" is ambiguously actually )

# spaceword.org 🧩 2025-09-26 🏁 score 2173 ranked 7.4% 28/379 ⏱️ 2:49:10.153785

📜 6 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 28/379

      _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ D _ _ _ _
      _ _ _ _ Z O A _ _ _
      _ _ _ _ _ U N _ _ _
      _ _ _ _ T R Y _ _ _
      _ _ _ _ H A W _ _ _
      _ _ _ _ I _ I _ _ _
      _ _ _ _ E M S _ _ _
      _ _ _ _ V O E _ _ _
      _ _ _ _ E _ _ _ _ _



# spaceword.org 🧩 2025-09-28 🏁 score 2173 ranked 6.8% 27/398 ⏱️ 1:19:22.310993

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 27/398

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ K E G _ _ _   
      _ _ _ _ I _ I _ _ _   
      _ _ _ _ R E V _ _ _   
      _ _ _ _ _ M E _ _ _   
      _ _ _ _ W E N _ _ _   
      _ _ _ _ _ U S _ _ _   
      _ _ _ _ _ T _ _ _ _   
      _ _ _ _ F E U _ _ _   
      _ _ _ _ A S _ _ _ _   


# alfagok.diginaut.net 🧩 #331 🥳 17 ⏱️ 0:01:21.202960

🤔 17 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+1      [     1] &-tekens    
    @+2      [     2] -cijferig   
    @+3      [     3] -e-mail     
    @+8648   [  8648] af          q4  ? after
    @+12394  [ 12394] afsplits    q6  ? after
    @+12403  [ 12403] afspoel     q14 ? after
    @+12413  [ 12413] afsponst    q15 ? after
    @+12418  [ 12418] afspraak    q16 ? it
    @+12418  [ 12418] afspraak    done. it
    @+12423  [ 12423] afspraken   q13 ? before
    @+12485  [ 12485] afstand     q12 ? before
    @+12593  [ 12593] afstem      q11 ? before
    @+12848  [ 12848] aftap       q10 ? before
    @+13331  [ 13331] afvlak      q9  ? before
    @+14275  [ 14275] agricultuur q8  ? before
    @+16155  [ 16155] am          q5  ? before
    @+24910  [ 24910] bad         q3  ? before
    @+49847  [ 49847] boks        q2  ? before
    @+99749  [ 99749] ex          q1  ? before
    @+199834 [199834] lijm        q0  ? before

# alphaguess.com 🧩 #797 🥳 16 ⏱️ 0:02:15.993488

🤔 16 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+47393 [47393] dis        q1  ? after
    @+72813 [72813] gremolata  q2  ? after
    @+79145 [79145] hood       q4  ? after
    @+79465 [79465] horse      q8  ? after
    @+79655 [79655] hot        q9  ? after
    @+79755 [79755] house      q10 ? after
    @+79842 [79842] houser     q11 ? after
    @+79876 [79876] hove       q12 ? after
    @+79895 [79895] how        q13 ? after
    @+79913 [79913] howk       q14 ? after
    @+79917 [79917] howl       q15 ? it
    @+79917 [79917] howl       done. it
    @+79928 [79928] hoy        q7  ? before
    @+80730 [80730] hydroxy    q6  ? before
    @+82322 [82322] immaterial q5  ? before
    @+85517 [85517] ins        q3  ? before
    @+98232 [98232] mach       q0  ? before

# squareword.org 🧩 #1337 🥳 7 ⏱️ 0:04:55.505833

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    D I A L S
    E G R E T
    A L G A E
    L O O S E
    T O T E R

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1367 🥳 17 ⏱️ 0:08:10.036088

📜 1 sessions
💰 score: 9900

    4/6
    AEONS ⬜🟩⬜⬜⬜
    RELIC 🟩🟩⬜🟩⬜
    REFIT 🟩🟩⬜🟩🟩
    REMIT 🟩🟩🟩🟩🟩
    4/6
    REMIT ⬜🟨⬜⬜⬜
    SANED ⬜🟨⬜🟩⬜
    ABBEY 🟩⬜⬜🟩🟩
    ALLEY 🟩🟩🟩🟩🟩
    4/6
    ALLEY ⬜⬜⬜🟨⬜
    RESIN 🟨🟨⬜⬜⬜
    ERGOT 🟨🟨🟨🟨⬜
    FORGE 🟩🟩🟩🟩🟩
    4/6
    FORGE ⬜⬜🟩⬜⬜
    YURTS ⬜⬜🟩⬜🟨
    SCRAP 🟨⬜🟩🟨⬜
    MARSH 🟩🟩🟩🟩🟩
    Final 1/2
    CLEAN 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1224 🥳 6 ⏱️ 0:09:52.346268

📜 1 sessions
💰 score: 9

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:NANNA n n n n n remain:5978
    ⬜⬜⬜⬜⬜ tried:POTTO n n n n n remain:2153
    ⬜⬜⬜⬜⬜ tried:MUMMY n n n n n remain:963
    ⬜⬜⬜⬜⬜ tried:SIBBS n n n n n remain:122
    ⬜⬜⬜⬜🟩 tried:GRRRL n n n n Y remain:9
    ⬜⬜🟩🟩🟩 tried:KVELL n n Y Y Y remain:1

    Undos used: 2

      1 words remaining
    x 9 unused letters
    = 9 total score

# cemantle.certitudes.org 🧩 #1274 🥳 287 ⏱️ 0:22:08.311034

🤔 288 attempts
📜 2 sessions
🫧 12 chat sessions
⁉️ 66 chat prompts
🤖 19 llama3.2:latest replies
🤖 46 gemma3:latest replies
🥵   3 😎  34 🥶 239 🧊  11

      $1 #288   ~1 assault             100.00°C 🥳 1000‰
      $2 #287   ~2 invasion             44.99°C 🥵  977‰
      $3 #274   ~6 incursion            38.32°C 🥵  949‰
      $4 #278   ~4 intimidation         35.91°C 🥵  926‰
      $5 #262  ~11 aggression           32.91°C 😎  884‰
      $6 #200  ~21 expulsion            32.85°C 😎  882‰
      $7 #206  ~19 neglect              32.45°C 😎  873‰
      $8 #238  ~14 conquest             29.90°C 😎  801‰
      $9 #149  ~33 subdue               29.86°C 😎  798‰
     $10 #222  ~18 dismissal            28.39°C 😎  739‰
     $11 #179  ~27 abandonment          28.13°C 😎  731‰
     $12 #205  ~20 mutilation           28.08°C 😎  728‰
     $39 #209      oppression           20.55°C 🥶
    $278  #41      portal               -0.58°C 🧊

# cemantix.certitudes.org 🧩 #1307 🥳 127 ⏱️ 0:13:54.132645

🤔 128 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 28 chat prompts
🤖 28 gemma3:latest replies
🔥  2 🥵  6 😎 20 🥶 52 🧊 47

      $1 #128   ~1 diplôme           100.00°C 🥳 1000‰
      $2 #124   ~4 qualification      55.50°C 🔥  996‰
      $3 #121   ~6 formation          54.64°C 🔥  994‰
      $4 #112  ~12 certificat         51.09°C 🥵  988‰
      $5 #100  ~18 spécialisation     48.16°C 🥵  981‰
      $6 #117  ~10 professionnel      47.44°C 🥵  977‰
      $7 #111  ~13 attestation        44.26°C 🥵  963‰
      $8 #105  ~17 validation         44.08°C 🥵  962‰
      $9 #110  ~14 compétence         41.45°C 🥵  954‰
     $10  #54  ~27 perfectionnement   33.37°C 😎  896‰
     $11 #114  ~11 connaissance       31.34°C 😎  871‰
     $12  #67  ~23 maîtrise           29.78°C 😎  846‰
     $30 #113      conformité         15.81°C 🥶
     $82  #53      intensifier        -0.09°C 🧊
