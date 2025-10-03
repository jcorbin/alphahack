# 2025-10-04

- 🔗 spaceword.org 🧩 2025-10-03 🏁 score 2173 ranked 4.9% 18/366 ⏱️ 1 day, 0:32:11.591869
- 🔗 alfagok.diginaut.net 🧩 #336 🥳 7 ⏱️ 23:11:47.438857
- 🔗 alphaguess.com 🧩 #802 🥳 14 ⏱️ 23:12:19.623265
- 🔗 squareword.org 🧩 #1342 🥳 9 ⏱️ 23:16:45.730547
- 🔗 dictionary.com hurdle 🧩 #1372 😦 21 ⏱️ 23:21:06.771959
- 🔗 dontwordle.com 🧩 #1229 🥳 6 ⏱️ 23:22:43.043251
- 🔗 cemantle.certitudes.org 🧩 #1279 🥳 205 ⏱️ 23:24:14.181221
- 🔗 cemantix.certitudes.org 🧩 #1312 🥳 654 ⏱️ 23:34:55.901443

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








# spaceword.org 🧩 2025-10-03 🏁 score 2173 ranked 4.9% 18/366 ⏱️ 1 day, 0:32:11.591869

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 18/366

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ E R S _ _ _   
      _ _ _ _ _ _ Q _ _ _   
      _ _ _ _ V A U _ _ _   
      _ _ _ _ O N E _ _ _   
      _ _ _ _ E T A _ _ _   
      _ _ _ _ _ E L _ _ _   
      _ _ _ _ _ F _ _ _ _   
      _ _ _ _ P I C _ _ _   
      _ _ _ _ E X _ _ _ _   


# alfagok.diginaut.net 🧩 #336 🥳 7 ⏱️ 23:11:47.438857

🤔 7 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+99749  [ 99749] ex        q1 ? after
    @+149452 [149452] huis      q2 ? after
    @+162007 [162007] izabel    q4 ? after
    @+168279 [168279] kano      q5 ? after
    @+171306 [171306] kennis    q6 ? it
    @+171306 [171306] kennis    done. it
    @+174562 [174562] kind      q3 ? before
    @+199834 [199834] lijm      q0 ? before

# alphaguess.com 🧩 #802 🥳 14 ⏱️ 23:12:19.623265

🤔 14 attempts
📜 1 sessions

    @        [     0] aa         
    @+1      [     1] aah        
    @+2      [     2] aahed      
    @+3      [     3] aahing     
    @+98231  [ 98231] mach       q0  ? after
    @+147336 [147336] rho        q1  ? after
    @+153336 [153336] sea        q4  ? after
    @+156473 [156473] shit       q5  ? after
    @+156820 [156820] short      q8  ? after
    @+156887 [156887] shot       q10 ? after
    @+156903 [156903] shotmaking q12 ? after
    @+156911 [156911] should     q13 ? it
    @+156911 [156911] should     done. it
    @+156919 [156919] shout      q11 ? before
    @+156953 [156953] show       q9  ? before
    @+157226 [157226] shut       q7  ? before
    @+158042 [158042] sine       q6  ? before
    @+159618 [159618] slug       q3  ? before
    @+171936 [171936] tag        q2  ? before

# squareword.org 🧩 #1342 🥳 9 ⏱️ 23:16:45.730547

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟨
    🟨 🟩 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟩 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S H A R K
    C O L O N
    A M I G O
    R E B U T
    F R I E S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1372 😦 21 ⏱️ 23:21:06.771959

📜 1 sessions
💰 score: 4580

    5/6
    STARE 🟩🟩⬜⬜⬜
    STOMP 🟩🟩⬜⬜⬜
    STICK 🟩🟩⬜⬜⬜
    STUDY 🟩🟩🟩⬜⬜
    STUNT 🟩🟩🟩🟩🟩
    5/6
    STUNT 🟩⬜⬜⬜⬜
    SHALE 🟩⬜⬜⬜⬜
    SWORD 🟩⬜🟨⬜⬜
    SOCKS 🟩🟩⬜⬜⬜
    SOGGY 🟩🟩🟩🟩🟩
    4/6
    SOGGY ⬜⬜⬜⬜⬜
    LITER 🟨⬜⬜⬜⬜
    QUALM ⬜⬜🟩🟨🟨
    CLAMP 🟩🟩🟩🟩🟩
    5/6
    CLAMP ⬜⬜⬜⬜⬜
    RINSE ⬜🟩⬜⬜⬜
    DIGHT ⬜🟩⬜⬜🟨
    WIFTY ⬜🟩⬜🟨🟩
    TIZZY 🟩🟩🟩🟩🟩
    Final 2/2
    ABIDE 🟨⬜🟨🟨⬜
    RADIX 🟩🟩🟩🟩⬜
    FAIL: RADII

# dontwordle.com 🧩 #1229 🥳 6 ⏱️ 23:22:43.043251

📜 1 sessions
💰 score: 21

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:EGGER n n n n n remain:4505
    ⬜⬜⬜⬜⬜ tried:PUPPY n n n n n remain:2190
    ⬜⬜⬜⬜⬜ tried:OVOLO n n n n n remain:767
    ⬜⬜⬜⬜⬜ tried:DIXIT n n n n n remain:173
    ⬜⬜🟩⬜⬜ tried:ABACA n n Y n n remain:19
    🟩⬜🟩🟩🟩 tried:SWASH Y n Y Y Y remain:3

    Undos used: 2

      3 words remaining
    x 7 unused letters
    = 21 total score

# cemantle.certitudes.org 🧩 #1279 🥳 205 ⏱️ 23:24:14.181221

🤔 206 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 50 chat prompts
🤖 20 llama3.2:latest replies
🤖 30 gemma3:latest replies
🔥   1 🥵   4 😎  27 🥶 163 🧊  10

      $1 #206   ~1 directive         100.00°C 🥳 1000‰
      $2 #202   ~5 mandate            50.95°C 🔥  997‰
      $3 #204   ~3 prohibition        43.59°C 🥵  984‰
      $4 #203   ~4 order              41.51°C 🥵  976‰
      $5 #197   ~9 injunction         41.11°C 🥵  974‰
      $6 #201   ~6 petition           34.48°C 🥵  926‰
      $7 #176  ~14 concurrence        29.72°C 😎  849‰
      $8 #118  ~27 allegation         28.48°C 😎  818‰
      $9 #199   ~8 interlocutory      28.26°C 😎  814‰
     $10 #180  ~12 mandamus           27.68°C 😎  790‰
     $11  #70  ~33 objection          27.16°C 😎  770‰
     $12 #185  ~11 revocation         26.96°C 😎  756‰
     $34 #187      withdrawal         19.56°C 🥶
    $197  #17      complexity         -0.27°C 🧊

# cemantix.certitudes.org 🧩 #1312 🥳 654 ⏱️ 23:34:55.901443

🤔 655 attempts
📜 1 sessions
🫧 37 chat sessions
⁉️ 255 chat prompts
🤖 255 gemma3:latest replies
🔥   3 🥵   6 😎  52 🥶 485 🧊 108

      $1 #655   ~1 idiot              100.00°C 🥳 1000‰
      $2 #627  ~12 débile              62.67°C 🔥  997‰
      $3 #456  ~33 ridicule            56.48°C 🔥  994‰
      $4 #652   ~2 bêtise              54.50°C 🔥  990‰
      $5 #388  ~43 prétentieux         50.85°C 🥵  980‰
      $6 #478  ~27 détester            47.28°C 🥵  955‰
      $7 #530  ~21 absurde             46.22°C 🥵  944‰
      $8 #485  ~25 blague              44.47°C 🥵  915‰
      $9 #580  ~16 honte               44.01°C 🥵  904‰
     $10 #529  ~22 niais               43.90°C 🥵  901‰
     $11 #651   ~3 malin               43.02°C 😎  879‰
     $12 #649   ~5 ignorant            42.82°C 😎  871‰
     $62 #653      dérangé             32.18°C 🥶
    $548 #267      répétition          -0.24°C 🧊
