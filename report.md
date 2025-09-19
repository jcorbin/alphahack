# 2025-09-20

- 🔗 spaceword.org 🧩 2025-09-19 🏁 score 2173 ranked 5.3% 20/379 ⏱️ 15:34:09.201736
- 🔗 alfagok.diginaut.net 🧩 #322 🥳 17 ⏱️ 7:29:25.560624
- 🔗 alphaguess.com 🧩 #788 🥳 17 ⏱️ 0:01:33.927531
- 🔗 squareword.org 🧩 #1328 🥳 8 ⏱️ 0:04:43.751561
- 🔗 dictionary.com hurdle 🧩 #1358 🥳 16 ⏱️ 0:08:12.125888
- 🔗 dontwordle.com 🧩 #1215 🥳 6 ⏱️ 0:09:51.169288
- 🔗 cemantle.certitudes.org 🧩 #1265 🥳 439 ⏱️ 0:19:19.199518
- 🔗 cemantix.certitudes.org 🧩 #1298 🥳 792 ⏱️ 1:45:27.017735

# Dev

## WIP

- [rc] tracing of logging-to state and cutover transition

- [dev] meta run / share / day works well enough
  - blink shell mangles pasted emoji... any way to workaround this?

## TODO

- square: finish questioning work

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

# spaceword.org 🧩 2025-09-19 🏁 score 2173 ranked 5.3% 20/379 ⏱️ 15:34:09.201736

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 20/379

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


# alfagok.diginaut.net 🧩 #322 🥳 17 ⏱️ 7:29:25.560624

🤔 17 attempts
📜 2 sessions

    @        [     0] &-teken         
    @+1      [     1] &-tekens        
    @+2      [     2] -cijferig       
    @+3      [     3] -e-mail         
    @+8648   [  8648] af              q4  ? after
    @+16156  [ 16156] am              q5  ? after
    @+18134  [ 18134] anti            q7  ? after
    @+18634  [ 18634] antithese       q9  ? after
    @+18754  [ 18754] antwoord        q12 ? after
    @+18768  [ 18768] antwoordde      q15 ? after
    @+18771  [ 18771] antwoorden      q16 ? it
    @+18771  [ 18771] antwoorden      done. it
    @+18781  [ 18781] antwoordenvelop q14 ? before
    @+18813  [ 18813] antwoordt       q13 ? before
    @+18873  [ 18873] apartheid       q10 ? before
    @+19131  [ 19131] app             q8  ? before
    @+20530  [ 20530] arg             q6  ? before
    @+24911  [ 24911] bad             q3  ? before
    @+49848  [ 49848] boks            q2  ? before
    @+99758  [ 99758] ex              q1  ? before
    @+199852 [199852] lijm            q0  ? before

# alphaguess.com 🧩 #788 🥳 17 ⏱️ 0:01:33.927531

🤔 17 attempts
📜 1 sessions

    @        [     0] aa       
    @+1      [     1] aah      
    @+2      [     2] aahed    
    @+3      [     3] aahing   
    @+98232  [ 98232] mach     q0  ? after
    @+147337 [147337] rho      q1  ? after
    @+171937 [171937] tag      q2  ? after
    @+182024 [182024] un       q3  ? after
    @+189287 [189287] vicar    q4  ? after
    @+191067 [191067] walk     q6  ? after
    @+191930 [191930] we       q7  ? after
    @+192039 [192039] weather  q10 ? after
    @+192099 [192099] webcast  q11 ? after
    @+192127 [192127] webs     q12 ? after
    @+192128 [192128] website  done. it
    @+192129 [192129] websites q16 ? before
    @+192131 [192131] websters q15 ? before
    @+192134 [192134] webworm  q14 ? before
    @+192140 [192140] wed      q13 ? before
    @+192165 [192165] wee      q9  ? before
    @+192400 [192400] wen      q8  ? before
    @+192891 [192891] whir     q5  ? before

# squareword.org 🧩 #1328 🥳 8 ⏱️ 0:04:43.751561

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟩 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S P L I T
    W H A L E
    E A T E N
    P S E U D
    T E R M S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1358 🥳 16 ⏱️ 0:08:12.125888

📜 1 sessions
💰 score: 10000

    4/6
    CESTA ⬜🟨⬜⬜🟨
    RAYED ⬜🟩⬜🟨⬜
    NAEVI 🟨🟩🟨⬜⬜
    MANGE 🟩🟩🟩🟩🟩
    4/6
    MANGE ⬜🟨⬜⬜⬜
    ASTIR 🟨🟨⬜⬜⬜
    ODAHS 🟨⬜🟩🟨🟩
    CHAOS 🟩🟩🟩🟩🟩
    3/6
    CHAOS 🟨⬜⬜⬜⬜
    TUNIC 🟩🟨⬜⬜🟨
    TRUCK 🟩🟩🟩🟩🟩
    4/6
    TRUCK ⬜⬜⬜⬜⬜
    LIANE 🟨🟨⬜⬜⬜
    SPOIL 🟩🟩⬜🟨🟩
    SPILL 🟩🟩🟩🟩🟩
    Final 1/2
    ONSET 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1215 🥳 6 ⏱️ 0:09:51.169288

📜 1 sessions
💰 score: 28

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:MIMIC n n n n n remain:6772
    ⬜⬜⬜⬜⬜ tried:BENNE n n n n n remain:2101
    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:907
    ⬜⬜⬜⬜⬜ tried:SHUSH n n n n n remain:141
    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:22
    ⬜🟨⬜🟩⬜ tried:KOTOW n m n Y n remain:4

    Undos used: 4

      4 words remaining
    x 7 unused letters
    = 28 total score

# cemantle.certitudes.org 🧩 #1265 🥳 439 ⏱️ 0:19:19.199518

🤔 440 attempts
📜 2 sessions
🫧 15 chat sessions
⁉️ 90 chat prompts
🤖 11 llama3.2:latest replies
🤖 79 gemma3:12b replies
🥵   8 😎  53 🥶 358 🧊  20

      $1 #440   ~1 fold             100.00°C 🥳 1000‰
      $2 #275  ~33 multiply          34.73°C 🥵  988‰
      $3 #325  ~27 grow              28.86°C 🥵  970‰
      $4 #254  ~37 increase          28.13°C 🥵  962‰
      $5 #240  ~40 percent           27.98°C 🥵  960‰
      $6 #314  ~29 figure            27.38°C 🥵  955‰
      $7  #88  ~59 join              25.95°C 🥵  924‰
      $8 #437   ~2 double            25.57°C 🥵  911‰
      $9 #245  ~38 add               25.24°C 🥵  903‰
     $10 #331  ~24 distend           24.95°C 😎  895‰
     $11 #210  ~46 attach            24.50°C 😎  878‰
     $12 #236  ~41 proportion        24.21°C 😎  865‰
     $63 #199      transfuse         18.26°C 🥶
    $421 #167      overlay           -0.19°C 🧊

# cemantix.certitudes.org 🧩 #1298 🥳 792 ⏱️ 1:45:27.017735

🤔 793 attempts
📜 1 sessions
🫧 35 chat sessions
⁉️ 229 chat prompts
🤖 61 llama3.2:latest replies
🤖 168 gemma3:12b replies
🔥   1 🥵  23 😎 161 🥶 562 🧊  45

      $1 #793   ~1 intermédiaire     100.00°C 🥳 1000‰
      $2 #458  ~69 organisme          47.48°C 🔥  996‰
      $3 #612  ~30 spécifique         43.19°C 🥵  985‰
      $4 #118 ~155 structure          40.87°C 🥵  968‰
      $5 #520  ~52 entité             40.59°C 🥵  964‰
      $6 #778   ~4 par                40.31°C 🥵  962‰
      $7 #149 ~146 fonction           40.21°C 🥵  961‰
      $8 #542  ~44 service            39.61°C 🥵  955‰
      $9 #719  ~16 fournisseur        39.52°C 🥵  954‰
     $10 #212 ~119 relation           39.19°C 🥵  950‰
     $11 #374  ~82 liaison            38.75°C 🥵  944‰
     $26  #99 ~164 opération          35.39°C 😎  892‰
    $187 #471      intégration        24.07°C 🥶
    $749 #153      conduit            -0.03°C 🧊
