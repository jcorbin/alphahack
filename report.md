# 2025-10-05

- 🔗 spaceword.org 🧩 2025-10-04 🏁 score 2173 ranked 3.3% 12/368 ⏱️ 3 days, 17:45:33.324021
- 🔗 alfagok.diginaut.net 🧩 #337 🥳 19 ⏱️ 13:23:30.371102
- 🔗 alphaguess.com 🧩 #803 🥳 13 ⏱️ 0:00:33.496935
- 🔗 squareword.org 🧩 #1343 🥳 9 ⏱️ 0:04:28.509647
- 🔗 dictionary.com hurdle 🧩 #1373 😦 17 ⏱️ 0:04:46.020221
- 🔗 dontwordle.com 🧩 #1230 🥳 6 ⏱️ 0:07:03.107357
- 🔗 cemantle.certitudes.org 🧩 #1280 🥳 155 ⏱️ 0:08:28.737212
- 🔗 cemantix.certitudes.org 🧩 #1313 🥳 232 ⏱️ 0:12:37.460660

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









# spaceword.org 🧩 2025-10-04 🏁 score 2173 ranked 3.3% 12/368 ⏱️ 3 days, 17:45:33.324021

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 12/368

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ D E Y _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ _ C A W _ _ _   
      _ _ _ _ O I L _ _ _   
      _ _ _ _ Q _ E _ _ _   
      _ _ _ _ U _ R _ _ _   
      _ _ _ _ I S _ _ _ _   
      _ _ _ _ N I X _ _ _   
      _ _ _ _ A G _ _ _ _   


# alfagok.diginaut.net 🧩 #337 🥳 19 ⏱️ 13:23:30.371102

🤔 19 attempts
📜 2 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+49847  [ 49847] boks      q2  ? after
    @+74758  [ 74758] dc        q3  ? after
    @+87219  [ 87219] draag     q4  ? after
    @+93447  [ 93447] eet       q5  ? after
    @+94976  [ 94976] eiwit     q8  ? after
    @+95309  [ 95309] elektro   q10 ? after
    @+95478  [ 95478] elf       q11 ? after
    @+95607  [ 95607] elite     q12 ? after
    @+95640  [ 95640] elixer    q14 ? after
    @+95652  [ 95652] elk       q15 ? after
    @+95653  [ 95653] elkaar    done. it
    @+95654  [ 95654] elkaars   q18 ? before
    @+95655  [ 95655] elkander  q17 ? before
    @+95657  [ 95657] elke      q16 ? before
    @+95673  [ 95673] elleboog  q13 ? before
    @+95767  [ 95767] elo       q9  ? before
    @+96581  [ 96581] energiek  q6  ? before
    @+96581  [ 96581] energiek  q7  ? before
    @+99749  [ 99749] ex        q1  ? before
    @+199834 [199834] lijm      q0  ? before

# alphaguess.com 🧩 #803 🥳 13 ⏱️ 0:00:33.496935

🤔 13 attempts
📜 1 sessions

    @        [     0] aa      
    @+1      [     1] aah     
    @+2      [     2] aahed   
    @+3      [     3] aahing  
    @+98231  [ 98231] mach    q0  ? after
    @+122116 [122116] par     q2  ? after
    @+134647 [134647] prog    q3  ? after
    @+137530 [137530] quad    q5  ? after
    @+138263 [138263] quip    q7  ? after
    @+138283 [138283] quirk   q12 ? it
    @+138283 [138283] quirk   done. it
    @+138302 [138302] quit    q11 ? before
    @+138343 [138343] quiz    q10 ? before
    @+138445 [138445] rabble  q9  ? before
    @+138634 [138634] radical q8  ? before
    @+139028 [139028] rake    q6  ? before
    @+140533 [140533] rec     q4  ? before
    @+147336 [147336] rho     q1  ? before

# squareword.org 🧩 #1343 🥳 9 ⏱️ 0:04:28.509647

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟨 🟨
    🟨 🟩 🟨 🟨 🟨
    🟨 🟨 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S H A G S
    W A G O N
    A B A T E
    P I T T A
    S T E A K

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1373 😦 17 ⏱️ 0:04:46.020221

📜 1 sessions
💰 score: 3780

    4/6
    RATES ⬜⬜⬜🟨⬜
    LEMON ⬜🟨⬜⬜⬜
    CHIVE 🟨⬜🟨⬜🟩
    PIECE 🟩🟩🟩🟩🟩
    3/6
    PIECE ⬜🟨⬜🟨🟩
    CHIVE 🟩🟩🟩⬜🟩
    CHIME 🟩🟩🟩🟩🟩
    4/6
    CHIME ⬜🟨⬜⬜⬜
    HORST 🟨⬜🟨⬜⬜
    GRAPH ⬜🟨🟨⬜🟩
    RAJAH 🟩🟩🟩🟩🟩
    6/6
    RAJAH ⬜🟨⬜⬜⬜
    STALK ⬜⬜🟩🟨⬜
    LEAFY 🟨🟨🟩⬜⬜
    GLADE ⬜🟩🟩⬜🟩
    BLAME ⬜🟩🟩⬜🟩
    PLANE 🟩🟩🟩⬜🟩
    FAIL: PLACE

# dontwordle.com 🧩 #1230 🥳 6 ⏱️ 0:07:03.107357

📜 1 sessions
💰 score: 9

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:JNANA n n n n n remain:5846
    ⬜⬜⬜⬜⬜ tried:PEEPS n n n n n remain:960
    ⬜⬜⬜⬜⬜ tried:CHUFF n n n n n remain:304
    ⬜⬜⬜⬜🟩 tried:XYLYL n n n n Y remain:12
    ⬜🟩⬜⬜🟩 tried:GRRRL n Y n n Y remain:5
    ⬜🟩🟩⬜🟩 tried:DROOL n Y Y n Y remain:1

    Undos used: 4

      1 words remaining
    x 9 unused letters
    = 9 total score

# cemantle.certitudes.org 🧩 #1280 🥳 155 ⏱️ 0:08:28.737212

🤔 156 attempts
📜 1 sessions
🫧 9 chat sessions
⁉️ 57 chat prompts
🤖 57 gemma3:latest replies
🔥   6 🥵   4 😎  32 🥶 108 🧊   5

      $1 #156   ~1 trace          100.00°C 🥳 1000‰
      $2 #154   ~3 locate          52.41°C 🔥  997‰
      $3 #153   ~4 pinpoint        50.85°C 🔥  996‰
      $4 #142  ~12 identify        48.29°C 🔥  994‰
      $5 #131  ~18 detect          46.92°C 🔥  993‰
      $6 #120  ~24 unearth         46.62°C 🔥  992‰
      $7 #130  ~19 uncover         45.56°C 🔥  991‰
      $8 #138  ~14 discern         41.31°C 🥵  984‰
      $9 #155   ~2 find            39.47°C 🥵  980‰
     $10 #128  ~21 discover        36.90°C 🥵  971‰
     $11  #36  ~37 origin          34.67°C 🥵  953‰
     $12  #42  ~36 roots           30.66°C 😎  893‰
     $44  #14      clone           21.52°C 🥶
    $152  #88      canopy          -0.08°C 🧊

# cemantix.certitudes.org 🧩 #1313 🥳 232 ⏱️ 0:12:37.460660

🤔 233 attempts
📜 1 sessions
🫧 12 chat sessions
⁉️ 80 chat prompts
🤖 80 gemma3:latest replies
😱   1 🥵  13 😎  35 🥶 149 🧊  34

      $1 #233   ~1 courageux      100.00°C 🥳 1000‰
      $2 #222   ~3 courage         66.50°C 😱  999‰
      $3 #156  ~27 honnête         47.39°C 🥵  989‰
      $4 #169  ~20 sincère         46.94°C 🥵  987‰
      $5 #176  ~16 généreux        46.28°C 🥵  985‰
      $6 #163  ~23 digne           40.33°C 🥵  953‰
      $7  #50  ~47 timide          40.02°C 🥵  950‰
      $8 #159  ~25 loyal           39.55°C 🥵  945‰
      $9 #232   ~2 bravoure        39.28°C 🥵  942‰
     $10 #202   ~6 respectable     38.10°C 🥵  931‰
     $11 #184  ~14 perspicace      37.19°C 🥵  919‰
     $16 #171  ~18 altruiste       35.69°C 😎  894‰
     $51  #19      loin            24.99°C 🥶
    $200 #106      posé            -0.17°C 🧊
