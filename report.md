# 2025-10-01

- 🔗 spaceword.org 🧩 2025-09-30 🏁 score 2173 ranked 4.7% 19/404 ⏱️ 23:09:51.368078
- 🔗 alfagok.diginaut.net 🧩 #333 🥳 8 ⏱️ 22:07:20.821602
- 🔗 alphaguess.com 🧩 #799 🥳 17 ⏱️ 22:08:07.118920
- 🔗 squareword.org 🧩 #1339 🥳 8 ⏱️ 22:10:41.979470
- 🔗 dictionary.com hurdle 🧩 #1369 🥳 19 ⏱️ 22:14:03.845520
- 🔗 dontwordle.com 🧩 #1226 😳 6 ⏱️ 22:25:38.851186
- 🔗 cemantle.certitudes.org 🧩 #1276 🥳 49 ⏱️ 0:01:51.287506
- 🔗 cemantix.certitudes.org 🧩 #1309 🥳 228 ⏱️ 0:05:18.515941

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





# spaceword.org 🧩 2025-09-30 🏁 score 2173 ranked 4.7% 19/404 ⏱️ 23:09:51.368078

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 19/404

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ N _ S O V K H O Z   
      _ E _ O F _ _ O _ O   
      _ T O U T I N G _ A   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #333 🥳 8 ⏱️ 22:07:20.821602

🤔 8 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+99749  [ 99749] ex        q1 ? after
    @+105577 [105577] flemer    q4 ? after
    @+108478 [108478] fries     q5 ? after
    @+109091 [109091] functie   q7 ? it
    @+109091 [109091] functie   done. it
    @+109934 [109934] galerie   q6 ? before
    @+111404 [111404] ge        q3 ? before
    @+149452 [149452] huis      q2 ? before
    @+199834 [199834] lijm      q0 ? before

# alphaguess.com 🧩 #799 🥳 17 ⏱️ 22:08:07.118920

🤔 17 attempts
📜 1 sessions

    @       [    0] aa          
    @+1     [    1] aah         
    @+2     [    2] aahed       
    @+3     [    3] aahing      
    @+2802  [ 2802] ag          q6  ? after
    @+4336  [ 4336] alma        q7  ? after
    @+4477  [ 4477] als         q9  ? after
    @+4483  [ 4483] alt         q10 ? after
    @+4550  [ 4550] alto        q11 ? after
    @+4552  [ 4552] altocumulus q16 ? after
    @+4553  [ 4553] altogether  done. it
    @+4554  [ 4554] altogethers q15 ? before
    @+4557  [ 4557] altos       q14 ? before
    @+4563  [ 4563] altruist    q13 ? before
    @+4574  [ 4574] alumin      q12 ? before
    @+4625  [ 4625] am          q8  ? before
    @+5882  [ 5882] angel       q5  ? before
    @+11770 [11770] back        q4  ? before
    @+23580 [23580] cam         q3  ? before
    @+47393 [47393] dis         q2  ? before
    @+98232 [98232] mach        q0  ? after
    @+98232 [98232] mach        q1  ? before

# squareword.org 🧩 #1339 🥳 8 ⏱️ 22:10:41.979470

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟩 🟨
    🟨 🟨 🟨 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S W A R M
    M O V I E
    O M E G A
    T A R O T
    E N T R Y

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1369 🥳 19 ⏱️ 22:14:03.845520

📜 1 sessions
💰 score: 9700

    3/6
    SANER 🟨⬜🟨🟨⬜
    NOELS 🟨⬜🟨⬜🟨
    ENSUE 🟩🟩🟩🟩🟩
    5/6
    ENSUE ⬜⬜⬜🟨⬜
    TRULY ⬜⬜🟩🟨⬜
    CLUMP ⬜🟩🟩⬜⬜
    FLUID 🟨🟩🟩⬜⬜
    BLUFF 🟩🟩🟩🟩🟩
    6/6
    BLUFF ⬜⬜⬜⬜⬜
    RATES ⬜🟩🟨🟨🟨
    WASTE ⬜🟩🟩🟩🟩
    HASTE ⬜🟩🟩🟩🟩
    CASTE ⬜🟩🟩🟩🟩
    PASTE 🟩🟩🟩🟩🟩
    4/6
    PASTE ⬜⬜⬜🟨🟨
    INTER 🟨⬜🟨🟩🟩
    TIGER 🟩🟩⬜🟩🟩
    TIMER 🟩🟩🟩🟩🟩
    Final 1/2
    MOUNT 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1226 😳 6 ⏱️ 22:25:38.851186

📜 2 sessions
💰 score: 0

WORDLED
> I must admit that I Wordled!

    ⬜⬜⬜⬜⬜ tried:ZIZIT n n n n n remain:6979
    ⬜⬜⬜⬜⬜ tried:MOJOS n n n n n remain:1785
    ⬜⬜⬜⬜⬜ tried:PUPPY n n n n n remain:741
    ⬜⬜⬜🟩⬜ tried:GRRRL n n n Y n remain:26
    ⬜⬜🟨🟩⬜ tried:WHERE n n m Y n remain:2
    🟩🟩🟩🟩🟩 tried:BEARD Y Y Y Y Y remain:0

    Undos used: 3

      0 words remaining
    x 0 unused letters
    = 0 total score

# cemantle.certitudes.org 🧩 #1276 🥳 49 ⏱️ 0:01:51.287506

🤔 50 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 10 chat prompts
🤖 10 gemma3:latest replies
🥵  4 😎  2 🥶 37 🧊  6

     $1 #50  ~1 venture         100.00°C 🥳 1000‰
     $2 #25  ~5 adventure        34.42°C 🥵  980‰
     $3 #46  ~2 trek             33.98°C 🥵  976‰
     $4 #31  ~4 journey          33.30°C 🥵  971‰
     $5 #23  ~6 expedition       33.26°C 🥵  969‰
     $6 #21  ~7 exploration      25.22°C 😎  827‰
     $7 #44  ~3 quest            18.33°C 😎  198‰
     $8 #42     traverse         17.22°C 🥶
     $9  #8     serendipity      16.00°C 🥶
    $10 #18     curiosity        15.77°C 🥶
    $11 #30     investigation    13.66°C 🥶
    $12 #33     nomad            13.32°C 🥶
    $13 #15     discovery        13.29°C 🥶
    $45 #10     velocity         -0.74°C 🧊

# cemantix.certitudes.org 🧩 #1309 🥳 228 ⏱️ 0:05:18.515941

🤔 229 attempts
📜 1 sessions
🫧 13 chat sessions
⁉️ 80 chat prompts
🤖 11 llama3.2:latest replies
🤖 69 gemma3:latest replies
🔥  6 🥵 14 😎 53 🥶 99 🧊 56

      $1 #229   ~1 rapporteur      100.00°C 🥳 1000‰
      $2  #89  ~47 proposition      48.80°C 🔥  997‰
      $3 #225   ~4 sénat            47.70°C 🔥  996‰
      $4 #123  ~33 rapport          47.23°C 🔥  994‰
      $5  #83  ~49 examiner         46.93°C 🔥  993‰
      $6 #228   ~2 parlementaire    44.62°C 🔥  991‰
      $7 #116  ~36 conclusion       44.34°C 🔥  990‰
      $8  #82  ~50 délibérer        41.01°C 🥵  983‰
      $9 #209  ~11 assemblée        37.04°C 🥵  974‰
     $10 #206  ~13 approuver        36.70°C 🥵  972‰
     $11 #215   ~6 délibération     35.99°C 🥵  967‰
     $22  #32  ~72 contester        29.43°C 😎  885‰
     $75  #20      controverse      17.13°C 🥶
    $174 #211      certitude        -0.37°C 🧊
