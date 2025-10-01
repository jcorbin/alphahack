# 2025-10-02

- 🔗 spaceword.org 🧩 2025-10-01 🏁 score 2173 ranked 6.4% 24/374 ⏱️ 1:11:00.371793
- 🔗 alfagok.diginaut.net 🧩 #334 🥳 19 ⏱️ 0:01:27.205814
- 🔗 alphaguess.com 🧩 #800 🥳 10 ⏱️ 0:01:49.969736
- 🔗 squareword.org 🧩 #1340 🥳 7 ⏱️ 0:03:49.634230
- 🔗 dictionary.com hurdle 🧩 #1370 🥳 20 ⏱️ 0:06:49.181144
- 🔗 dontwordle.com 🧩 #1227 🥳 6 ⏱️ 0:08:32.513772
- 🔗 cemantle.certitudes.org 🧩 #1277 🥳 197 ⏱️ 0:16:49.316711
- 🔗 cemantix.certitudes.org 🧩 #1310 🥳 90 ⏱️ 0:17:40.384036

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






# spaceword.org 🧩 2025-10-01 🏁 score 2173 ranked 6.4% 24/374 ⏱️ 1:11:00.371793

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 24/374

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ D E L _ _ _   
      _ _ _ _ _ T O _ _ _   
      _ _ _ _ M A C _ _ _   
      _ _ _ _ A _ K _ _ _   
      _ _ _ _ J U S _ _ _   
      _ _ _ _ A _ _ _ _ _   
      _ _ _ _ G E T _ _ _   
      _ _ _ _ U _ _ _ _ _   
      _ _ _ _ A Z O _ _ _   


# alfagok.diginaut.net 🧩 #334 🥳 19 ⏱️ 0:01:27.205814

🤔 19 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+1      [     1] &-tekens    
    @+2      [     2] -cijferig   
    @+3      [     3] -e-mail     
    @+199834 [199834] lijm        q0  ? after
    @+247745 [247745] op          q2  ? after
    @+260632 [260632] pater       q4  ? after
    @+267085 [267085] plomp       q5  ? after
    @+270158 [270158] pot         q6  ? after
    @+271819 [271819] prijs       q7  ? after
    @+272629 [272629] privé       q8  ? after
    @+272775 [272775] pro         q9  ? after
    @+272954 [272954] proces      q11 ? after
    @+273045 [273045] processor   q12 ? after
    @+273098 [273098] proconsuls  q13 ? after
    @+273123 [273123] produce     q14 ? after
    @+273131 [273131] producenten q15 ? after
    @+273142 [273142] producer    q16 ? after
    @+273143 [273143] produceren  done. it
    @+273144 [273144] producerend q18 ? before
    @+273146 [273146] producers   q17 ? before
    @+273150 [273150] product     q10 ? before
    @+273551 [273551] proef       q3  ? before
    @+299752 [299752] schub       q1  ? before

# alphaguess.com 🧩 #800 🥳 10 ⏱️ 0:01:49.969736

🤔 10 attempts
📜 1 sessions

    @       [    0] aa          
    @+1     [    1] aah         
    @+2     [    2] aahed       
    @+3     [    3] aahing      
    @+47393 [47393] dis         q1  ? after
    @+60096 [60096] face        q3  ? after
    @+66452 [66452] french      q4  ? after
    @+66836 [66836] front       q9  ? it
    @+66836 [66836] front       done. it
    @+67232 [67232] full        q8  ? before
    @+68018 [68018] gall        q7  ? before
    @+69633 [69633] geosyncline q5  ? after
    @+69633 [69633] geosyncline q6  ? before
    @+72813 [72813] gremolata   q2  ? before
    @+98232 [98232] mach        q0  ? before

# squareword.org 🧩 #1340 🥳 7 ⏱️ 0:03:49.634230

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟨
    🟩 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P A S T A
    A W A R D
    R A T I O
    T R I E R
    S E N S E

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1370 🥳 20 ⏱️ 0:06:49.181144

📜 1 sessions
💰 score: 9600

    4/6
    YEARS ⬜🟨🟨⬜⬜
    LATED ⬜🟩🟩🟨⬜
    BATHE ⬜🟩🟩⬜🟩
    MATTE 🟩🟩🟩🟩🟩
    3/6
    MATTE 🟩⬜⬜⬜⬜
    MINUS 🟩⬜🟨⬜⬜
    MORON 🟩🟩🟩🟩🟩
    6/6
    MORON ⬜⬜🟨⬜⬜
    RAILS 🟨🟨⬜⬜⬜
    GRACE ⬜🟩🟨⬜🟨
    BREAD ⬜🟩🟩🟩⬜
    FREAK ⬜🟩🟩🟩🟩
    WREAK 🟩🟩🟩🟩🟩
    5/6
    WREAK ⬜⬜🟨⬜⬜
    ISTLE 🟨⬜⬜⬜🟩
    NICHE ⬜🟨⬜⬜🟩
    OXIDE 🟨🟨🟨⬜🟩
    MOXIE 🟩🟩🟩🟩🟩
    Final 2/2
    IDOLS 🟨🟨🟨⬜🟨
    DISCO 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1227 🥳 6 ⏱️ 0:08:32.513772

📜 1 sessions
💰 score: 14

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:JINNI n n n n n remain:7302
    ⬜⬜⬜⬜⬜ tried:CUDDY n n n n n remain:2984
    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:1352
    ⬜🟩⬜⬜⬜ tried:GRRRL n Y n n n remain:58
    ⬜🟩🟨⬜⬜ tried:BRAVA n Y m n n remain:4
    ⬜🟩🟨🟨⬜ tried:FREAK n Y m m n remain:2

    Undos used: 2

      2 words remaining
    x 7 unused letters
    = 14 total score

# cemantle.certitudes.org 🧩 #1277 🥳 197 ⏱️ 0:16:49.316711

🤔 198 attempts
📜 1 sessions
🫧 14 chat sessions
⁉️ 92 chat prompts
🤖 8 llama3.2:latest replies
🤖 84 gemma3:latest replies
😱   1 🥵  15 😎  56 🥶 113 🧊  12

      $1 #198   ~1 boat           100.00°C 🥳 1000‰
      $2 #130  ~36 sailboat        79.27°C 😱  999‰
      $3 #114  ~47 vessel          69.85°C 🥵  987‰
      $4 #182   ~6 watercraft      64.46°C 🥵  982‰
      $5 #150  ~23 tugboat         63.14°C 🥵  981‰
      $6 #111  ~49 ship            61.69°C 🥵  978‰
      $7  #87  ~64 marina          58.11°C 🥵  965‰
      $8 #143  ~26 paddle          55.52°C 🥵  960‰
      $9  #90  ~62 sailing         54.69°C 🥵  956‰
     $10 #101  ~57 dock            54.49°C 🥵  955‰
     $11  #98  ~59 deckhand        54.41°C 🥵  953‰
     $18 #104  ~55 harbor          47.61°C 😎  891‰
     $74 #136      liner           25.78°C 🥶
    $187  #65      chromatic       -0.41°C 🧊

# cemantix.certitudes.org 🧩 #1310 🥳 90 ⏱️ 0:17:40.384036

🤔 91 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 19 chat prompts
🤖 19 gemma3:latest replies
🥵  1 😎 11 🥶 75 🧊  3

     $1 #91  ~1 fragile         100.00°C 🥳 1000‰
     $2 #61  ~7 profond          35.06°C 🥵  930‰
     $3 #63  ~6 profondément     32.62°C 😎  869‰
     $4 #64  ~5 puissant         32.12°C 😎  851‰
     $5 #82  ~3 déchirant        29.49°C 😎  714‰
     $6 #50 ~10 intense          27.99°C 😎  589‰
     $7 #84  ~2 mélancolique     26.53°C 😎  424‰
     $8 #73  ~4 tourment         26.46°C 😎  415‰
     $9 #57  ~8 dramatique       26.42°C 😎  409‰
    $10 #29 ~13 lucide           25.66°C 😎  304‰
    $11 #54  ~9 brûlant          24.93°C 😎  174‰
    $12 #41 ~12 éclat            24.90°C 😎  166‰
    $14 #70     subtil           23.57°C 🥶
    $89 #38     irisé            -0.89°C 🧊
