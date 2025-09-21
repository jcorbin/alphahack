# 2025-09-22

- 🔗 spaceword.org 🧩 2025-09-21 🏁 score 2168 ranked 31.8% 120/377 ⏱️ 0:46:17.678972
- 🔗 alfagok.diginaut.net 🧩 #324 🥳 14 ⏱️ 0:01:22.618746
- 🔗 alphaguess.com 🧩 #790 🥳 13 ⏱️ 0:01:55.731838
- 🔗 squareword.org 🧩 #1330 🥳 8 ⏱️ 0:05:01.971722
- 🔗 dictionary.com hurdle 🧩 #1360 🥳 15 ⏱️ 0:08:40.671464
- 🔗 dontwordle.com 🧩 #1217 🥳 6 ⏱️ 0:11:10.225608
- 🔗 cemantle.certitudes.org 🧩 #1267 🥳 142 ⏱️ 0:12:41.811156
- 🔗 cemantix.certitudes.org 🧩 #1300 🥳 138 ⏱️ 0:14:06.647659

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



# spaceword.org 🧩 2025-09-21 🏁 score 2168 ranked 31.8% 120/377 ⏱️ 0:46:17.678972

📜 3 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 120/377

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ Q _ V _ _ _   
      _ _ _ _ U _ I _ _ _   
      _ _ _ R E B S _ _ _   
      _ _ _ _ L I E _ _ _   
      _ _ _ _ E R _ _ _ _   
      _ _ _ W A D Y _ _ _   
      _ _ _ _ _ I _ _ _ _   
      _ _ _ I C E _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #324 🥳 14 ⏱️ 0:01:22.618746

🤔 14 attempts
📜 1 sessions

    @        [     0] &-teken             
    @+1      [     1] &-tekens            
    @+2      [     2] -cijferig           
    @+3      [     3] -e-mail             
    @+49848  [ 49848] boks                q2  ? after
    @+62287  [ 62287] cement              q5  ? after
    @+68521  [ 68521] connectie           q6  ? after
    @+70057  [ 70057] convulsie           q8  ? after
    @+70825  [ 70825] covariantiefuncties q11 ? after
    @+71207  [ 71207] creosoteer          q12 ? after
    @+71324  [ 71324] crisis              q13 ? it
    @+71324  [ 71324] crisis              done. it
    @+71590  [ 71590] cru                 q7  ? before
    @+74759  [ 74759] dc                  q4  ? before
    @+99750  [ 99750] ex                  q1  ? before
    @+199844 [199844] lijm                q0  ? before

# alphaguess.com 🧩 #790 🥳 13 ⏱️ 0:01:55.731838

🤔 13 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+47393 [47393] dis        q1  ? after
    @+53409 [53409] el         q4  ? after
    @+56754 [56754] equate     q5  ? after
    @+58370 [58370] ex         q6  ? after
    @+58476 [58476] excavate   q10 ? after
    @+58496 [58496] excel      q12 ? it
    @+58496 [58496] excel      done. it
    @+58526 [58526] excerpt    q11 ? before
    @+58583 [58583] excitation q9  ? before
    @+58795 [58795] exempt     q8  ? before
    @+59229 [59229] expel      q7  ? before
    @+60096 [60096] face       q3  ? before
    @+72813 [72813] gremolata  q2  ? before
    @+98232 [98232] mach       q0  ? before

# squareword.org 🧩 #1330 🥳 8 ⏱️ 0:05:01.971722

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟩 🟩 🟨 🟩
    🟨 🟨 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    W R I S T
    H E N C E
    I N D E X
    F A I N T
    F L E E S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1360 🥳 15 ⏱️ 0:08:40.671464

📜 1 sessions
💰 score: 10100

    4/6
    EOSIN ⬜⬜⬜🟨⬜
    PICAL ⬜🟨🟨⬜⬜
    BRICK ⬜⬜🟩🟩🟩
    THICK 🟩🟩🟩🟩🟩
    3/6
    THICK ⬜⬜⬜⬜🟨
    UKASE ⬜🟨🟨⬜🟩
    ANKLE 🟩🟩🟩🟩🟩
    3/6
    ANKLE ⬜⬜⬜⬜🟨
    DREST ⬜⬜🟨🟨🟩
    UPSET 🟩🟩🟩🟩🟩
    4/6
    UPSET ⬜⬜⬜⬜⬜
    NOILY ⬜⬜⬜⬜⬜
    MARCH ⬜🟨🟨🟩⬜
    CRACK 🟩🟩🟩🟩🟩
    Final 1/2
    MERCY 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1217 🥳 6 ⏱️ 0:11:10.225608

📜 1 sessions
💰 score: 5

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:7300
    ⬜⬜⬜⬜⬜ tried:DOODY n n n n n remain:3177
    ⬜⬜⬜⬜⬜ tried:JAVAS n n n n n remain:474
    ⬜⬜⬜⬜⬜ tried:CRUCK n n n n n remain:99
    ⬜⬜⬜⬜🟩 tried:NGWEE n n n n Y remain:3
    ⬜🟩⬜🟩🟩 tried:MILLE n Y n Y Y remain:1

    Undos used: 2

      1 words remaining
    x 5 unused letters
    = 5 total score

# cemantle.certitudes.org 🧩 #1267 🥳 142 ⏱️ 0:12:41.811156

🤔 143 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 25 chat prompts
🤖 25 gemma3:12b replies
😱   1 🥵   6 😎  19 🥶 113 🧊   3

      $1 #143   ~1 sensor             100.00°C 🥳 1000‰
      $2 #103   ~9 detector            63.50°C 😱  999‰
      $3 #106   ~8 optics              52.44°C 🥵  971‰
      $4  #68  ~19 calibration         50.79°C 🥵  962‰
      $5  #94  ~13 spectrometer        50.26°C 🥵  957‰
      $6 #126   ~6 electromagnetic     48.49°C 🥵  935‰
      $7  #74  ~15 absorbance          48.07°C 🥵  927‰
      $8  #37  ~24 chemiluminescence   47.77°C 🥵  925‰
      $9  #72  ~17 detection           45.73°C 😎  876‰
     $10 #100  ~10 measurement         44.89°C 😎  855‰
     $11  #35  ~25 adjustable          44.03°C 😎  826‰
     $12  #73  ~16 amplifier           42.93°C 😎  790‰
     $28  #46      luciferin           33.44°C 🥶
    $141 #124      uncertainty         -1.47°C 🧊

# cemantix.certitudes.org 🧩 #1300 🥳 138 ⏱️ 0:14:06.647659

🤔 139 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 18 chat prompts
🤖 18 gemma3:12b replies
🔥  1 🥵  6 😎 25 🥶 65 🧊 41

      $1 #139   ~1 résidence       100.00°C 🥳 1000‰
      $2  #88  ~21 hébergement      41.14°C 🔥  991‰
      $3  #70  ~24 lieu             40.88°C 🥵  989‰
      $4 #138   ~2 logement         39.01°C 🥵  986‰
      $5 #100  ~14 location         32.69°C 🥵  955‰
      $6 #128   ~4 pavillon         31.27°C 🥵  944‰
      $7  #85  ~22 accueil          29.24°C 🥵  920‰
      $8  #89  ~20 chambre          28.47°C 🥵  910‰
      $9 #127   ~5 parking          27.43°C 😎  887‰
     $10 #117  ~10 jardin           27.35°C 😎  882‰
     $11  #91  ~19 gîte             26.97°C 😎  861‰
     $12 #106  ~11 touristique      26.05°C 😎  828‰
     $34  #98      hospitalité      16.34°C 🥶
     $99  #31      mouvement        -0.19°C 🧊
