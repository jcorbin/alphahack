# 2025-09-24

- 🔗 spaceword.org 🧩 2025-09-23 🏁 score 2168 ranked 29.2% 117/401 ⏱️ 0:58:29.657789
- 🔗 alfagok.diginaut.net 🧩 #326 🥳 15 ⏱️ 0:01:06.842478
- 🔗 alphaguess.com 🧩 #792 🥳 17 ⏱️ 0:01:54.524229
- 🔗 squareword.org 🧩 #1332 🥳 7 ⏱️ 0:04:35.011239
- 🔗 dictionary.com hurdle 🧩 #1362 🥳 17 ⏱️ 0:09:35.136664
- 🔗 dontwordle.com 🧩 #1219 🥳 6 ⏱️ 0:11:51.565926
- 🔗 cemantle.certitudes.org 🧩 #1269 🥳 125 ⏱️ 0:12:55.504092
- 🔗 cemantix.certitudes.org 🧩 #1302 🥳 58 ⏱️ 0:13:35.320021

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





# spaceword.org 🧩 2025-09-23 🏁 score 2168 ranked 29.2% 117/401 ⏱️ 0:58:29.657789

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 117/401

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ D _ _   
      _ F _ O U T P U T _   
      _ O _ K _ O H I A _   
      _ E X E U N T _ V _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #326 🥳 15 ⏱️ 0:01:06.842478

🤔 15 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+1      [     1] &-tekens    
    @+2      [     2] -cijferig   
    @+3      [     3] -e-mail     
    @+199843 [199843] lijm        q0  ? after
    @+299768 [299768] schub       q1  ? az
    @+299768 [299768] schub       q2  ? after
    @+349552 [349552] vakantie    q3  ? after
    @+353120 [353120] ver         q5  ? after
    @+355301 [355301] verg        q8  ? after
    @+355955 [355955] verhaast    q10 ? after
    @+356279 [356279] verhoud     q11 ? after
    @+356449 [356449] verindischt q12 ? after
    @+356474 [356474] verjaardag  q14 ? it
    @+356474 [356474] verjaardag  done. it
    @+356531 [356531] verjagen    q13 ? before
    @+356618 [356618] verkeer     q9  ? before
    @+358413 [358413] verluieren  q7  ? before
    @+363705 [363705] verzot      q6  ? before
    @+374296 [374296] vrij        q4  ? before

# alphaguess.com 🧩 #792 🥳 17 ⏱️ 0:01:54.524229

🤔 17 attempts
📜 1 sessions

    @        [     0] aa        
    @+1      [     1] aah       
    @+2      [     2] aahed     
    @+3      [     3] aahing    
    @+98232  [ 98232] mach      q0  ? after
    @+122117 [122117] par       q2  ? after
    @+134648 [134648] prog      q3  ? after
    @+137531 [137531] quad      q5  ? after
    @+139029 [139029] rake      q6  ? after
    @+139330 [139330] rap       q8  ? after
    @+139412 [139412] rare      q10 ? after
    @+139453 [139453] rash      q11 ? after
    @+139464 [139464] rasp      q12 ? after
    @+139466 [139466] raspberry q16 ? it
    @+139466 [139466] raspberry done. it
    @+139468 [139468] rasper    q15 ? before
    @+139472 [139472] raspiness q14 ? before
    @+139480 [139480] rassle    q13 ? before
    @+139502 [139502] rat       q9  ? before
    @+139767 [139767] raw       q7  ? before
    @+140534 [140534] rec       q4  ? before
    @+147337 [147337] rho       q1  ? before

# squareword.org 🧩 #1332 🥳 7 ⏱️ 0:04:35.011239

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟨 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S H O R T
    T A P I R
    E L I D E
    M A N G A
    S L E E T

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1362 🥳 17 ⏱️ 0:09:35.136664

📜 1 sessions
💰 score: 9900

    4/6
    EARLS 🟨🟨⬜⬜🟨
    SHAPE 🟩⬜🟨⬜🟨
    STEAK 🟩⬜🟩🟩🟩
    SNEAK 🟩🟩🟩🟩🟩
    4/6
    SNEAK 🟩⬜⬜⬜🟩
    SMOCK 🟩⬜🟩⬜🟩
    SPORK 🟩⬜🟩🟩🟩
    STORK 🟩🟩🟩🟩🟩
    4/6
    STORK ⬜⬜⬜⬜🟩
    BLACK ⬜⬜⬜🟩🟩
    QUICK ⬜🟨⬜🟩🟩
    CHUCK 🟩🟩🟩🟩🟩
    4/6
    CHUCK ⬜⬜🟩⬜⬜
    LEUDS ⬜🟨🟩⬜⬜
    PRUNE ⬜🟩🟩⬜🟨
    TRUER 🟩🟩🟩🟩🟩
    Final 1/2
    TEETH 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1219 🥳 6 ⏱️ 0:11:51.565926

📜 1 sessions
💰 score: 7

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:EMMER n n n n n remain:4337
    ⬜⬜⬜⬜⬜ tried:KIBBI n n n n n remain:2049
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:838
    ⬜⬜⬜⬜⬜ tried:SYNCS n n n n n remain:71
    ⬜🟨⬜⬜⬜ tried:DOGGO n m n n n remain:5
    ⬜🟨🟩⬜🟩 tried:QUOLL n m Y n Y remain:1

    Undos used: 3

      1 words remaining
    x 7 unused letters
    = 7 total score

# cemantle.certitudes.org 🧩 #1269 🥳 125 ⏱️ 0:12:55.504092

🤔 126 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 18 chat prompts
🤖 18 gemma3:12b replies
🔥   1 🥵   1 😎   9 🥶 106 🧊   8

      $1 #126   ~1 rough             100.00°C 🥳 1000‰
      $2 #123   ~3 stormy             43.53°C 🔥  990‰
      $3 #116   ~5 turbulent          41.22°C 🥵  983‰
      $4  #96   ~8 chaotic            32.82°C 😎  896‰
      $5  #95   ~9 erratic            32.02°C 😎  884‰
      $6  #74  ~10 turbulence         30.65°C 😎  858‰
      $7 #125   ~2 fierce             29.14°C 😎  808‰
      $8  #99   ~7 fickle             27.79°C 😎  729‰
      $9 #114   ~6 tumult             26.86°C 😎  653‰
     $10 #120   ~4 unsettled          26.20°C 😎  588‰
     $11  #21  ~12 draft              23.72°C 😎  306‰
     $12  #71  ~11 whirlwind          22.81°C 😎  132‰
     $13  #82      preliminary        22.18°C 🥶
    $119  #22      airflow            -0.15°C 🧊

# cemantix.certitudes.org 🧩 #1302 🥳 58 ⏱️ 0:13:35.320021

🤔 59 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 12 chat prompts
🤖 12 gemma3:12b replies
😎  6 🥶 37 🧊 15

     $1 #59  ~1 parcours       100.00°C 🥳 1000‰
     $2 #56  ~3 chemin          29.56°C 😎  887‰
     $3 #54  ~4 distance        25.40°C 😎  770‰
     $4 #57  ~2 espace          23.86°C 😎  707‰
     $5 #42  ~5 horizon         18.73°C 😎  241‰
     $6 #33  ~7 saison          18.41°C 😎  199‰
     $7 #40  ~6 chantier        17.19°C 😎    2‰
     $8 #39     forêt           14.45°C 🥶
     $9 #55     ligne           14.29°C 🥶
    $10 #51     terroir         14.02°C 🥶
    $11 #16     branche         12.24°C 🥶
    $12 #21     ambiance        11.75°C 🥶
    $13 #20     nature          10.30°C 🥶
    $45  #3     chien           -0.13°C 🧊
