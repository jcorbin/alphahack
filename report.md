# 2025-09-14

- 🔗 spaceword.org 🧩 2025-09-13 🏁 score 2173 ranked 8.2% 32/391 ⏱️ 4:54:12.403223
- 🔗 alfagok.diginaut.net 🧩 #316 🥳 22 ⏱️ 0:03:16.297266
- 🔗 alphaguess.com 🧩 #782 🥳 11 ⏱️ 0:02:44.677435
- 🔗 squareword.org 🧩 #1322 🥳 7 ⏱️ 0:09:45.328358
- 🔗 dictionary.com hurdle 🧩 #1352 🥳 19 ⏱️ 0:19:27.508632
- 🔗 dontwordle.com 🧩 #1209 🥳 6 ⏱️ 0:12:26.241902
- 🔗 cemantix.certitudes.org 🧩 #1292 🥳 169 ⏱️ 0:03:17.693601
- 🔗 cemantle.certitudes.org 🧩 #1259 🥳 233 ⏱️ 0:09:23.850265

# Dev

## WIP

- [rc] ui clipboard tweaks
- [rc] reuse semantic retry around chat iteration
  - [ ] TODO generalize the retry facility

- [testing] missing puzzle id from hurdle and dontwordle should now be fixed
  - ... and follow on result handling improvement
- [testing] clipboard attribution
  - [ ] TODO replay last paste to ease dev sometimes
- [testing] standard /store command
- [testing] fin ephemeral stored log works now...
  - [ ] ... but dumps back into continue state, rather than stop-ing back
    out to the meta prompt

- [testing] standard /site command with osc-8 linking for /site
  - [ ] hurdle also needs to squelch re-entrant link
  - [ ] ... also every other solver

- [dev] meta run / share / day works well enough
  - blink shell mangles pasted emoji... any way to workaround this?

## TODO

- binartic: prune `press <Return> to finish` prompt

- better meta
  - [ ] store daily share(d) state
  - [ ] better logic circa end of day early play, e.g. doing a CET timezone
        puzzle close late in the "prior" day local (EST) time
  - [ ] similarly, early play of next-day spaceword should work gracefully

- square: finish questioning work

- hurdle: spurious "next work" banner at end
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


# spaceword.org 🧩 2025-09-13 🏁 score 2173 ranked 8.2% 32/391 ⏱️ 4:54:12.403223

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 32/391

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ N _ _ _ H _ V E E   
      _ E _ E X A M I N E   
      _ B O N I T O S _ K   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #316 🥳 22 ⏱️ 0:03:16.297266

🤔 22 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199853 [199853] lijm      q0  ? after
    @+199853 [199853] lijm      q1  ? after
    @+223815 [223815] molest    q4  ? after
    @+235799 [235799] odium     q16 ? after
    @+236507 [236507] oh        q20 ? after
    @+236686 [236686] olie      q21 ? it
    @+236686 [236686] olie      done. it
    @+237211 [237211] om        q18 ? before
    @+238829 [238829] on        q17 ? before
    @+247771 [247771] op        q3  ? before
    @+299778 [299778] schub     q2  ? before

# alphaguess.com 🧩 #782 🥳 11 ⏱️ 0:02:44.677435

🤔 11 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+47394 [47394] dis        q1  ? after
    @+60097 [60097] face       q3  ? after
    @+63253 [63253] flag       q5  ? after
    @+64850 [64850] foment     q6  ? after
    @+65649 [65649] format     q7  ? after
    @+65838 [65838] foss       q9  ? after
    @+65924 [65924] four       q10 ? it
    @+65924 [65924] four       done. it
    @+66046 [66046] fractional q8  ? before
    @+66453 [66453] french     q4  ? before
    @+72814 [72814] gremolata  q2  ? before
    @+98233 [98233] mach       q0  ? before

# squareword.org 🧩 #1322 🥳 7 ⏱️ 0:09:45.328358

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    M A N I C
    A L O N E
    D I V E R
    A V E R T
    M E L T S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1352 🥳 19 ⏱️ 0:19:27.508632

📜 2 sessions
💰 score: 9700

    5/6
    LASER 🟩⬜⬜🟩⬜
    TILDE ⬜🟩🟨⬜🟨
    LIKEN 🟩🟩⬜🟩🟩
    LIVEN 🟩🟩⬜🟩🟩
    LINEN 🟩🟩🟩🟩🟩
    5/6
    LINEN ⬜⬜⬜⬜⬜
    STORM 🟩🟩⬜🟨⬜
    STRAW 🟩🟩🟩🟩⬜
    STRAP 🟩🟩🟩🟩⬜
    STRAY 🟩🟩🟩🟩🟩
    3/6
    STRAY ⬜⬜🟨⬜🟨
    CYDER ⬜🟨⬜🟨🟨
    RHYME 🟩🟩🟩🟩🟩
    5/6
    RHYME ⬜⬜⬜⬜⬜
    SATIN ⬜🟨⬜🟨🟨
    ACING 🟩⬜🟩🟩🟩
    AGING 🟩⬜🟩🟩🟩
    AXING 🟩🟩🟩🟩🟩
    Final 1/2
    EERIE 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1209 🥳 6 ⏱️ 0:12:26.241902

📜 2 sessions
💰 score: 9

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:GAMMA n n n n n remain:5731
    ⬜⬜⬜⬜⬜ tried:BENNE n n n n n remain:1678
    ⬜⬜⬜⬜⬜ tried:ICTIC n n n n n remain:501
    ⬜⬜⬜⬜⬜ tried:DOODY n n n n n remain:68
    ⬜🟩🟩⬜⬜ tried:FLUFF n Y Y n n remain:4
    🟩🟩🟩⬜⬜ tried:SLUSH Y Y Y n n remain:1

    Undos used: 3

      1 words remaining
    x 9 unused letters
    = 9 total score

# cemantix.certitudes.org 🧩 #1292 🥳 169 ⏱️ 0:03:17.693601

🤔 170 attempts
📜 2 sessions
🫧 4 chat sessions
⁉️ 27 chat prompts
🤖 27 gemma3:12b replies
🥵  2 😎 17 🥶 83 🧊 67

      $1 #170   ~1 record           100.00°C 🥳 1000‰
      $2  #29  ~19 chiffre           32.48°C 🥵  975‰
      $3 #153   ~4 dernier           28.00°C 🥵  935‰
      $4 #109   ~9 score             25.13°C 😎  874‰
      $5 #159   ~3 succès            24.44°C 😎  857‰
      $6  #57  ~17 progression       24.38°C 😎  856‰
      $7  #76  ~11 vitesse           23.79°C 😎  837‰
      $8  #63  ~13 croissance        21.64°C 😎  757‰
      $9 #100  ~10 performance       21.25°C 😎  735‰
     $10  #22  ~20 compteur          21.24°C 😎  733‰
     $11 #116   ~7 compétition       20.76°C 😎  701‰
     $12  #58  ~16 augmentation      19.58°C 😎  621‰
     $21 #113      ascension         14.95°C 🥶
    $104 #128      position          -0.04°C 🧊

# cemantle.certitudes.org 🧩 #1259 🥳 233 ⏱️ 0:09:23.850265

🤔 234 attempts
📜 1 sessions
🫧 10 chat sessions
⁉️ 63 chat prompts
🤖 63 gemma3:12b replies
🔥   5 🥵   6 😎  37 🥶 183 🧊   2

      $1 #234   ~1 compromise         100.00°C 🥳 1000‰
      $2 #232   ~3 accord              51.63°C 🔥  998‰
      $3 #180  ~18 impasse             50.45°C 🔥  997‰
      $4 #231   ~4 agreement           46.33°C 🔥  994‰
      $5 #230   ~5 negotiation         45.47°C 🔥  992‰
      $6 #194  ~14 stalemate           44.86°C 🔥  991‰
      $7 #233   ~2 bargaining          40.25°C 🥵  973‰
      $8  #23  ~44 disagreement        38.84°C 🥵  963‰
      $9  #50  ~34 wrangling           38.55°C 🥵  961‰
     $10 #182  ~17 deadlock            37.96°C 🥵  957‰
     $11 #185  ~16 gridlock            33.32°C 🥵  903‰
     $12  #63  ~28 acrimony            33.22°C 😎  899‰
     $50 #211      restraint           22.00°C 🥶
    $233 #151      tirade              -0.24°C 🧊
