# 2025-09-30

- 🔗 spaceword.org 🧩 2025-09-29 🏁 score 2173 ranked 4.3% 18/420 ⏱️ 2:07:31.758168
- 🔗 alfagok.diginaut.net 🧩 #332 🥳 11 ⏱️ 0:02:02.105850
- 🔗 alphaguess.com 🧩 #798 🥳 11 ⏱️ 0:02:36.573469
- 🔗 squareword.org 🧩 #1338 🥳 7 ⏱️ 0:04:52.948025
- 🔗 dictionary.com hurdle 🧩 #1368 🥳 23 ⏱️ 0:08:58.120502
- 🔗 dontwordle.com 🧩 #1225 🥳 6 ⏱️ 0:11:01.847498
- 🔗 cemantle.certitudes.org 🧩 #1275 🥳 852 ⏱️ 0:27:49.077810
- 🔗 cemantix.certitudes.org 🧩 #1308 🥳 155 ⏱️ 0:10:16.292477

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




# spaceword.org 🧩 2025-09-29 🏁 score 2173 ranked 4.3% 18/420 ⏱️ 2:07:31.758168

📜 4 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 18/420

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ O _ B E Z I Q U E   
      _ R _ E _ _ V I N Y   
      _ S A L A R Y _ _ E   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #332 🥳 11 ⏱️ 0:02:02.105850

🤔 11 attempts
📜 1 sessions

    @        [     0] &-teken            
    @+1      [     1] &-tekens           
    @+2      [     2] -cijferig          
    @+3      [     3] -e-mail            
    @+199834 [199834] lijm               q0  ? after
    @+247745 [247745] op                 q2  ? after
    @+273551 [273551] proef              q3  ? after
    @+286622 [286622] rijs               q4  ? after
    @+292850 [292850] samen              q5  ? after
    @+296284 [296284] schepping          q6  ? after
    @+297870 [297870] school             q7  ? after
    @+298324 [298324] schoolverenigingen q9  ? after
    @+298380 [298380] schoon             q10 ? it
    @+298380 [298380] schoon             done. it
    @+298778 [298778] schot              q8  ? before
    @+299752 [299752] schub              q1  ? before

# alphaguess.com 🧩 #798 🥳 11 ⏱️ 0:02:36.573469

🤔 11 attempts
📜 1 sessions

    @        [     0] aa        
    @+1      [     1] aah       
    @+2      [     2] aahed     
    @+3      [     3] aahing    
    @+98232  [ 98232] mach      q0  ? after
    @+147337 [147337] rho       q1  ? after
    @+171937 [171937] tag       q2  ? after
    @+173177 [173177] technical q6  ? after
    @+173794 [173794] tempt     q7  ? after
    @+173808 [173808] ten       q9  ? after
    @+173955 [173955] tennis    q10 ? it
    @+173955 [173955] tennis    done. it
    @+174109 [174109] tephrite  q8  ? before
    @+174423 [174423] test      q5  ? before
    @+176974 [176974] tom       q4  ? before
    @+182024 [182024] un        q3  ? before

# squareword.org 🧩 #1338 🥳 7 ⏱️ 0:04:52.948025

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S C R A M
    P R I S E
    R E N T S
    E A S E S
    E M E R Y

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1368 🥳 23 ⏱️ 0:08:58.120502

📜 1 sessions
💰 score: 9300

    6/6
    PRASE ⬜🟨🟨⬜⬜
    GATOR ⬜🟩⬜⬜🟨
    DAIRY ⬜🟩⬜🟨⬜
    RANCH 🟨🟩⬜⬜⬜
    LARVA ⬜🟩🟩⬜🟩
    KARMA 🟩🟩🟩🟩🟩
    5/6
    KARMA ⬜⬜🟨🟨⬜
    MOURN 🟨🟨🟨🟨⬜
    HUMOR ⬜🟩🟩🟩🟩
    TUMOR ⬜🟩🟩🟩🟩
    RUMOR 🟩🟩🟩🟩🟩
    6/6
    RUMOR 🟨🟩⬜⬜⬜
    BURLS ⬜🟩🟩⬜🟨
    HURST ⬜🟩🟩🟩⬜
    PURSE ⬜🟩🟩🟩🟩
    CURSE ⬜🟩🟩🟩🟩
    NURSE 🟩🟩🟩🟩🟩
    5/6
    NURSE ⬜⬜⬜⬜🟩
    ALIVE 🟨🟩⬜⬜🟩
    BLAME ⬜🟩🟩⬜🟩
    GLADE 🟩🟩🟩⬜🟩
    GLAZE 🟩🟩🟩🟩🟩
    Final 1/2
    GOFER 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1225 🥳 6 ⏱️ 0:11:01.847498

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:COOCH n n n n n remain:6849
    ⬜⬜⬜⬜⬜ tried:SLYLY n n n n n remain:1854
    ⬜⬜⬜⬜⬜ tried:IMMIX n n n n n remain:844
    ⬜⬜⬜⬜⬜ tried:GRUFF n n n n n remain:179
    ⬜⬜🟩⬜⬜ tried:ADAPT n n Y n n remain:3
    ⬜⬜🟩🟩🟩 tried:WEAVE n n Y Y Y remain:1

    Undos used: 2

      1 words remaining
    x 6 unused letters
    = 6 total score

# cemantle.certitudes.org 🧩 #1275 🥳 852 ⏱️ 0:27:49.077810

🤔 853 attempts
📜 3 sessions
🫧 49 chat sessions
⁉️ 291 chat prompts
🤖 9 deepseek-r1:latest replies
🤖 44 gemma3:12b replies
🤖 168 llama3.2:latest replies
🤖 70 gemma3:latest replies
😱   1 🔥   6 🥵  45 😎 127 🥶 649 🧊  24

      $1 #853   ~1 tire             100.00°C 🥳 1000‰
      $2 #293 ~147 gearbox           52.92°C 😱  999‰
      $3 #307 ~143 driveshaft        52.83°C 🔥  998‰
      $4 #382 ~128 brake             52.56°C 🔥  997‰
      $5 #409 ~109 radiator          49.99°C 🔥  996‰
      $6 #286 ~148 axle              48.64°C 🔥  993‰
      $7 #508  ~75 chassis           47.77°C 🔥  991‰
      $8 #428 ~101 muffler           47.22°C 🔥  990‰
      $9 #342 ~136 camber            46.82°C 🥵  989‰
     $10 #680  ~33 alternator        46.53°C 🥵  988‰
     $11 #387 ~123 gasket            46.14°C 🥵  987‰
     $54 #716  ~24 impeller          34.19°C 😎  898‰
    $181 #762      condenser         21.62°C 🥶
    $830 #644      conduit           -0.20°C 🧊

# cemantix.certitudes.org 🧩 #1308 🥳 155 ⏱️ 0:10:16.292477

🤔 156 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 23 chat prompts
🤖 23 gemma3:12b replies
🔥  1 🥵  6 😎 24 🥶 88 🧊 36

      $1 #156   ~1 tonne              100.00°C 🥳 1000‰
      $2 #152   ~2 kilogramme          49.97°C 🔥  997‰
      $3 #120  ~14 camion              44.25°C 🥵  986‰
      $4  #86  ~24 cargaison           39.22°C 🥵  963‰
      $5  #79  ~26 conteneur           37.34°C 🥵  949‰
      $6  #93  ~22 fret                36.94°C 🥵  942‰
      $7  #71  ~27 exportation         35.43°C 🥵  915‰
      $8 #142   ~6 remorque            34.11°C 🥵  901‰
      $9 #124  ~12 grue                33.13°C 😎  880‰
     $10 #127  ~11 carburant           32.59°C 😎  863‰
     $11  #54  ~29 récolte             32.47°C 😎  862‰
     $12 #107  ~18 importation         32.10°C 😎  855‰
     $33  #95      manutention         21.79°C 🥶
    $121  #28      gourmandise         -0.17°C 🧊
