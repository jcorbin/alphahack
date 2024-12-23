# 2025-10-03

- 🔗 spaceword.org 🧩 2025-10-02 🏁 score 2173 ranked 4.7% 18/387 ⏱️ 4:18:13.456439
- 🔗 alfagok.diginaut.net 🧩 #335 🥳 17 ⏱️ 0:01:20.843245
- 🔗 alphaguess.com 🧩 #801 🥳 14 ⏱️ 0:02:07.767171
- 🔗 squareword.org 🧩 #1341 🥳 7 ⏱️ 0:05:55.262285
- 🔗 dictionary.com hurdle 🧩 #1371 🥳 17 ⏱️ 0:09:29.610937
- 🔗 dontwordle.com 🧩 #1228 🤷 6 ⏱️ 0:12:22.639176
- 🔗 cemantle.certitudes.org 🧩 #1278 🥳 945 ⏱️ 0:34:21.413094
- 🔗 cemantix.certitudes.org 🧩 #1311 🥳 79 ⏱️ 0:21:44.077657

# Dev

## WIP

- square: finish questioning work
- meta: output wrapping towards abstracting out a PromptUI output protocol
- meta: automate review phase via rebase plan editor

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







# spaceword.org 🧩 2025-10-02 🏁 score 2173 ranked 4.7% 18/387 ⏱️ 4:18:13.456439

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 18/387

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ Q _ O _ _ F A _ R   
      _ I _ P A P U L A E   
      _ S E A W A N T _ Z   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #335 🥳 17 ⏱️ 0:01:20.843245

🤔 17 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+24910  [ 24910] bad        q3  ? after
    @+27603  [ 27603] basis      q6  ? after
    @+28962  [ 28962] bed        q7  ? after
    @+29200  [ 29200] bedevaart  q9  ? after
    @+29323  [ 29323] bedil      q10 ? after
    @+29399  [ 29399] bedonder   q11 ? after
    @+29431  [ 29431] bedrag     q12 ? after
    @+29440  [ 29440] bedreig    q13 ? after
    @+29445  [ 29445] bedreigend q15 ? after
    @+29450  [ 29450] bedreiging q16 ? it
    @+29450  [ 29450] bedreiging done. it
    @+29455  [ 29455] bedreven   q14 ? before
    @+29474  [ 29474] bedrijf    q8  ? before
    @+31127  [ 31127] begeleid   q5  ? before
    @+37364  [ 37364] bescherm   q4  ? before
    @+49847  [ 49847] boks       q2  ? before
    @+99749  [ 99749] ex         q1  ? before
    @+199834 [199834] lijm       q0  ? before

# alphaguess.com 🧩 #801 🥳 14 ⏱️ 0:02:07.767171

🤔 14 attempts
📜 1 sessions

    @       [    0] aa            
    @+1     [    1] aah           
    @+2     [    2] aahed         
    @+3     [    3] aahing        
    @+11770 [11770] back          q4  ? after
    @+17672 [17672] blepharoplast q5  ? after
    @+20617 [20617] bridge        q6  ? after
    @+22095 [22095] burg          q7  ? after
    @+22732 [22732] cab           q8  ? after
    @+23156 [23156] calaboose     q10 ? after
    @+23363 [23363] caliph        q11 ? after
    @+23383 [23383] call          q13 ? it
    @+23383 [23383] call          done. it
    @+23461 [23461] calm          q12 ? before
    @+23579 [23579] cam           q3  ? before
    @+47392 [47392] dis           q2  ? before
    @+98231 [98231] mach          q0  ? after
    @+98231 [98231] mach          q1  ? before

# squareword.org 🧩 #1341 🥳 7 ⏱️ 0:05:55.262285

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T O A T
    M A C R O
    E N T E R
    A G E N T
    R O T A S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1371 🥳 17 ⏱️ 0:09:29.610937

📜 1 sessions
💰 score: 9900

    4/6
    AISLE 🟨⬜⬜🟨🟩
    LARGE 🟨🟨⬜⬜🟩
    CLADE ⬜🟩🟩⬜🟩
    PLATE 🟩🟩🟩🟩🟩
    2/6
    PLATE ⬜🟩🟩⬜🟩
    BLAZE 🟩🟩🟩🟩🟩
    6/6
    BLAZE ⬜🟨🟨⬜🟨
    LADES 🟨🟨⬜🟨⬜
    PETAL ⬜🟩⬜🟩🟩
    VENAL ⬜🟩⬜🟩🟩
    FERAL ⬜🟩🟨🟩🟩
    REGAL 🟩🟩🟩🟩🟩
    3/6
    REGAL ⬜⬜⬜🟨🟩
    BASIL ⬜🟨⬜🟩🟩
    ANVIL 🟩🟩🟩🟩🟩
    Final 2/2
    DUCKY ⬜🟩⬜⬜🟩
    FUSSY 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1228 🤷 6 ⏱️ 0:12:22.639176

📜 1 sessions
💰 score: 0

ELIMINATED
> Well technically I didn't Wordle!

    ⬜⬜⬜⬜⬜ tried:YAPPY n n n n n remain:5357
    ⬜⬜⬜⬜⬜ tried:EDGED n n n n n remain:1667
    ⬜⬜⬜⬜⬜ tried:SUNNS n n n n n remain:266
    🟨🟩⬜⬜⬜ tried:TOROT m Y n n n remain:7
    ⬜🟩🟩⬜⬜ tried:HOTCH n Y Y n n remain:1
    ⬛⬛⬛⬛⬛ tried:????? remain:0

    Undos used: 5

      0 words remaining
    x 0 unused letters
    = 0 total score

# cemantle.certitudes.org 🧩 #1278 🥳 945 ⏱️ 0:34:21.413094

🤔 946 attempts
📜 2 sessions
🫧 37 chat sessions
⁉️ 241 chat prompts
🤖 163 llama3.2:latest replies
🤖 78 gemma3:latest replies
🔥   1 🥵   8 😎 121 🥶 773 🧊  42

      $1 #946   ~1 golf             100.00°C 🥳 1000‰
      $2 #856  ~16 tournament        48.43°C 🔥  990‰
      $3 #772  ~23 course            46.65°C 🥵  985‰
      $4 #943   ~2 clubhouse         39.68°C 🥵  963‰
      $5 #615  ~65 equestrian        36.34°C 🥵  947‰
      $6 #780  ~21 layout            33.55°C 🥵  920‰
      $7 #646  ~53 spa               33.26°C 🥵  916‰
      $8 #611  ~66 resort            33.07°C 🥵  911‰
      $9 #370 ~103 gardening         32.49°C 🥵  906‰
     $10 #740  ~39 fishing           32.46°C 🥵  905‰
     $11 #625  ~61 recreation        31.18°C 😎  890‰
     $12 #339 ~108 groundskeeper     31.16°C 😎  889‰
    $132 #571      scouting          18.74°C 🥶
    $905 #821      line              -0.06°C 🧊

# cemantix.certitudes.org 🧩 #1311 🥳 79 ⏱️ 0:21:44.077657

🤔 80 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 20 chat prompts
🤖 20 gemma3:latest replies
🔥  2 🥵  4 😎 10 🥶 42 🧊 21

     $1 #80  ~1 souplesse      100.00°C 🥳 1000‰
     $2 #64  ~7 facilité        56.87°C 🔥  994‰
     $3 #58 ~10 fluidité        55.85°C 🔥  993‰
     $4 #71  ~5 simplicité      51.24°C 🥵  987‰
     $5 #20 ~16 confort         43.73°C 🥵  967‰
     $6 #70  ~6 légèreté        38.65°C 🥵  931‰
     $7 #56 ~11 équilibre       36.99°C 🥵  911‰
     $8 #76  ~3 souci           33.73°C 😎  845‰
     $9 #72  ~4 clarté          33.09°C 😎  825‰
    $10 #39 ~13 sérénité        32.11°C 😎  797‰
    $11 #14 ~17 douceur         31.61°C 😎  782‰
    $12 #78  ~2 élégance        30.85°C 😎  747‰
    $18 #77     tonique         20.95°C 🥶
    $60 #27     lien            -0.23°C 🧊
