# 2025-09-05

- 🔗 spaceword.org 🧩 2025-09-04 🏁 score 2172 ranked 16.2% 67/413 ⏱️ 0:09:39.872734
- 🔗 alfagok.diginaut.net 🧩 #307 🥳 9 ⏱️ 0:01:05.287298
- 🔗 alphaguess.com 🧩 #773 🥳 15 ⏱️ 0:00:37.667278
- 🔗 squareword.org 🧩 #1313 🥳 7 ⏱️ 0:02:16.301840
- 🔗 dictionary.com hurdle 🧩  🥳 16 ⏱️ 0:02:57.819977
- 🔗 dontwordle.com 🧩  🥳 6 ⏱️ 0:02:33.236871
- 🔗 cemantix.certitudes.org 🧩 #1283 🥳 73 ⏱️ 0:00:41.720296
- 🔗 cemantle.certitudes.org 🧩 #1250 🥳 102 ⏱️ 0:12:43.213224

```ex
'<,'>norm ^f dt f🧩2f dt 0f P
```

- 🏁 spaceword.org 🧩 2025-09-04 score 2172 ranked 16.2% 67/413 ⏱️ 0:09:39.872734
- 🥳 alfagok.diginaut.net 🧩 #307 9 ⏱️ 0:01:05.287298
- 🥳 alphaguess.com 🧩 #773 15 ⏱️ 0:00:37.667278
- 🥳 squareword.org 🧩 #1313 7 ⏱️ 0:02:16.301840
- 🥳 dictionary.com hurdle 🧩  16 ⏱️ 0:02:57.819977
- 🥳 dontwordle.com 🧩  6 ⏱️ 0:02:33.236871
- 🥳 cemantix.certitudes.org 🧩 #1283 73 ⏱️ 0:00:41.720296
- 🥳 cemantle.certitudes.org 🧩 #1250 102 ⏱️ 0:12:43.213224

Details spoilers: https://matrix.to/#/!AkdGQweeqaUUXrVkrk:aelf.land/$MBf1QCYjrFWuawPaT7u3j3PZE0iAW0tb24SAuZC-PKE?via=aelf.land&via=matrix.org

# Dev

## WIP

- space search eof no longer works
  ```
  search 722964 [ 1400 cap:1400 prune:88 dead:2 reject:1 ]> ! <__main__.Search object at 0x7e043b5a4190> -!> Search.__call__.<locals>.<lambda>
  ```

- store fin
  - doesn't commit
  - should auto report
  - ... from review, but seems fine under cont

## TODO

- both hurdle and dontwordle lack puzzle id in report notes

- semantic does not auto report before exit
  - auto seems to just `<STOP>`, but not trace to confirm yet
  - rerun insta stores with trace:
    ```
    ! __call__ -> load_log
    ! load_log -> set_log_file
    ! set_log_file -*> load
    ! __call__ -> handle
    ! handle -> store
    ```

- space
  - post fin `! store -> tail -> continue` implies `not run_done`

- meta script
  - daily init
  - launch next
  - daily fin
  - daily report

- finish square questioning work

# spaceword.org 🧩 2025-09-04 🏁 score 2172 ranked 16.2% 67/413 ⏱️ 0:09:39.872734

📜 4 sessions
- tiles: 21/21
- score: 2172 bonus: +72
- rank: 67/413

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ Q _ _ C _ _ _   
      _ _ _ U N C O _ _ _   
      _ _ _ A _ A I _ _ _   
      _ _ _ _ _ E N _ _ _   
      _ _ _ _ J O T _ _ _   
      _ _ _ T O M E _ _ _   
      _ _ _ _ W A R _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #307 🥳 9 ⏱️ 0:01:05.287298

🤔 9 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199855 [199855] lijm      q0 ? after
    @+299794 [299794] schub     q1 ? after
    @+349580 [349580] vakantie  q2 ? after
    @+353148 [353148] ver       q4 ? after
    @+363733 [363733] verzot    q5 ? after
    @+365673 [365673] vis       q7 ? after
    @+367025 [367025] vlieg     q8 ? it
    @+367025 [367025] vlieg     done. it
    @+368746 [368746] voetbal   q6 ? before
    @+374324 [374324] vrij      q3 ? before

# alphaguess.com 🧩 #773 🥳 15 ⏱️ 0:00:37.667278

🤔 15 attempts
📜 1 sessions

    @       [    0] aa          
    @+1     [    1] aah         
    @+2     [    2] aahed       
    @+3     [    3] aahing      
    @+47394 [47394] dis         q2  ? after
    @+60097 [60097] face        q4  ? after
    @+66453 [66453] french      q5  ? after
    @+69634 [69634] geosyncline q6  ? after
    @+71225 [71225] gnomon      q7  ? after
    @+72020 [72020] gracious    q8  ? after
    @+72157 [72157] grand       q10 ? after
    @+72283 [72283] grant       q11 ? after
    @+72310 [72310] granules    q13 ? after
    @+72325 [72325] grape       q14 ? it
    @+72325 [72325] grape       done. it
    @+72337 [72337] graph       q12 ? before
    @+72411 [72411] grass       q9  ? before
    @+72814 [72814] gremolata   q3  ? before
    @+98233 [98233] mach        q0  ? after
    @+98233 [98233] mach        q1  ? before

# squareword.org 🧩 #1313 🥳 7 ⏱️ 0:02:16.301840

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟨 🟩 🟩
    🟨 🟨 🟨 🟩 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    O P A L S
    B E G O T
    I R A T E
    T R I T E
    S Y N O D

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1343 🥳 16 ⏱️ 0:02:57.819977

📜 1 sessions
💰 score: 10000

    3/6
    RASED ⬜⬜🟨⬜⬜
    LIONS ⬜🟩🟩⬜🟩
    PIOUS 🟩🟩🟩🟩🟩
    3/6
    PIOUS 🟨⬜🟩⬜🟨
    SCOPE 🟩🟩🟩🟨⬜
    SCOOP 🟩🟩🟩🟩🟩
    5/6
    SCOOP ⬜⬜⬜⬜⬜
    BLARE ⬜⬜⬜🟩🟩
    MITRE ⬜⬜⬜🟩🟩
    ENURE 🟨⬜⬜🟩🟩
    WHERE 🟩🟩🟩🟩🟩
    3/6
    WHERE ⬜⬜⬜⬜🟩
    SLIME ⬜⬜🟨🟨🟩
    MINCE 🟩🟩🟩🟩🟩
    Final 2/2
    BAWTY 🟩🟨🟩⬜🟩
    BYWAY 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1200 🥳 6 ⏱️ 0:02:33.236871

📜 2 sessions
💰 score: 35

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:YAPPY n n n n n remain:5357
    ⬜⬜⬜⬜⬜ tried:BUTUT n n n n n remain:2563
    ⬜⬜⬜⬜⬜ tried:WHOOF n n n n n remain:858
    ⬜⬜⬜⬜⬜ tried:VILLI n n n n n remain:198
    ⬜🟩⬜⬜🟩 tried:MERGE n Y n n Y remain:9
    ⬜🟩⬜⬜🟩 tried:JEEZE n Y n n Y remain:5

    Undos used: 4

      5 words remaining
    x 7 unused letters
    = 35 total score

# cemantix.certitudes.org 🧩 #1283 🥳 73 ⏱️ 0:00:41.720296

🤔 74 attempts
📜 1 sessions
🫧 3 chat sessions
⁉️ 17 chat prompts
🤖 17 gemma3:latest replies
🔥  1 🥵  3 😎 10 🥶 31 🧊 28

     $1 #74  ~1 détention      100.00°C 🥳 1000‰
     $2 #60  ~6 prison          57.49°C 🔥  996‰
     $3 #58  ~7 captivité       42.54°C 🥵  979‰
     $4 #22 ~13 réclusion       42.44°C 🥵  978‰
     $5 #51  ~8 enfermement     33.96°C 🥵  933‰
     $6 #35 ~10 restriction     30.32°C 😎  878‰
     $7 #14 ~15 retrait         25.77°C 😎  734‰
     $8 #38  ~9 évasion         25.74°C 😎  733‰
     $9 #17 ~14 isolement       25.59°C 😎  727‰
    $10 #70  ~3 clandestin      23.66°C 😎  609‰
    $11 #28 ~12 absence         23.65°C 😎  608‰
    $12 #29 ~11 confinement     22.91°C 😎  539‰
    $16 #63     châtiment       18.08°C 🥶
    $47 #13     cache           -0.15°C 🧊

# cemantle.certitudes.org 🧩 #1250 🥳 102 ⏱️ 0:12:43.213224

🤔 103 attempts
📜 1 sessions
🫧 4 chat sessions
⁉️ 19 chat prompts
🤖 19 gemma3:latest replies
🥵  1 😎  7 🥶 91 🧊  3

      $1 #103   ~1 neutral     100.00°C 🥳 1000‰
      $2  #92   ~4 soft         27.83°C 🥵  935‰
      $3  #85   ~5 muted        24.45°C 😎  837‰
      $4  #97   ~3 taupe        21.86°C 😎  648‰
      $5  #62   ~8 tone         21.05°C 😎  535‰
      $6  #41   ~9 hue          20.42°C 😎  420‰
      $7  #78   ~6 cool         19.28°C 😎  192‰
      $8  #77   ~7 beige        18.86°C 😎   79‰
      $9  #99   ~2 calm         18.60°C 😎    5‰
     $10  #49      shade        17.50°C 🥶
     $11  #28      rosy         17.36°C 🥶
     $12  #34      sienna       16.30°C 🥶
     $13  #12      red          16.08°C 🥶
    $101  #31      persimmon    -0.44°C 🧊
