# 2025-09-13

- 🔗 spaceword.org 🧩 2025-09-12 🏁 score 2173 ranked 8.6% 34/397 ⏱️ 11:07:21.318954
- 🔗 alfagok.diginaut.net 🧩 #315 🥳 15 ⏱️ 0:01:45.101661
- 🔗 alphaguess.com 🧩 #781 🥳 16 ⏱️ 0:02:57.103300
- 🔗 squareword.org 🧩 #1321 🥳 9 ⏱️ 0:07:47.317332
- 🔗 dictionary.com hurdle 🧩 #1351 😦 23 ⏱️ 0:04:58.057336
- 🔗 dontwordle.com 🧩 #1208 🥳 6 ⏱️ 0:06:55.321033
- 🔗 cemantle.certitudes.org 🧩 #1258 🥳 376 ⏱️ 0:08:27.043420
- 🔗 cemantix.certitudes.org 🧩 #1291 🥳 840 ⏱️ 0:57:41.845363

# Dev

## WIP

- [rc] missing puzzle id from hurdle and dontwordle should now be fixed

- [testing] share conversion is scuffed wrt "dictionary.com hurdle 🧩" ;
  needs to skip any number of tokens up to the puzzle

- [dev reverted] fin on ephemeral stored log should cutover to a non-ephemeral log, whether
  stored or working copy

## TODO

- better meta
  - [ ] store daily share(d) state
  - [ ] better logic circa end of day early play, e.g. doing a CET timezone
        puzzle close late in the "prior" day local (EST) time
  - [ ] similarly, early play of next-day spaceword should work gracefully

- square: finish questioning work

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

# spaceword.org 🧩 2025-09-12 🏁 score 2173 ranked 8.6% 34/397 ⏱️ 11:07:21.318954

📜 10 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 34/397

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ H _ V _ J O _ B A   
      _ I _ O P U N T I A   
      _ S K E A N E _ _ L   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #315 🥳 15 ⏱️ 0:01:45.101661

🤔 15 attempts
📜 1 sessions

    @        [     0] &-teken      
    @+1      [     1] &-tekens     
    @+2      [     2] -cijferig    
    @+3      [     3] -e-mail      
    @+24912  [ 24912] bad          q3  ? after
    @+37366  [ 37366] bescherm     q4  ? after
    @+43072  [ 43072] bij          q5  ? after
    @+44589  [ 44589] binnen       q7  ? after
    @+45522  [ 45522] bisschop     q8  ? after
    @+45844  [ 45844] blad         q9  ? after
    @+46152  [ 46152] blasfemeerde q12 ? after
    @+46167  [ 46167] blauw        q14 ? it
    @+46167  [ 46167] blauw        done. it
    @+46305  [ 46305] bleek        q13 ? before
    @+46458  [ 46458] blief        q6  ? before
    @+49849  [ 49849] boks         q2  ? before
    @+99759  [ 99759] ex           q1  ? before
    @+199853 [199853] lijm         q0  ? before

# alphaguess.com 🧩 #781 🥳 16 ⏱️ 0:02:57.103300

🤔 16 attempts
📜 1 sessions

    @        [     0] aa         
    @+1      [     1] aah        
    @+2      [     2] aahed      
    @+3      [     3] aahing     
    @+98233  [ 98233] mach       q0  ? after
    @+98233  [ 98233] mach       q1  ? after
    @+98480  [ 98480] mae        q9  ? after
    @+98511  [ 98511] mag        q11 ? after
    @+98531  [ 98531] magi       q12 ? after
    @+98534  [ 98534] magic      q15 ? it
    @+98534  [ 98534] magic      done. it
    @+98544  [ 98544] magister   q14 ? before
    @+98556  [ 98556] magistrate q13 ? before
    @+98586  [ 98586] magnet     q10 ? before
    @+98741  [ 98741] mail       q8  ? before
    @+99248  [ 99248] man        q7  ? before
    @+101028 [101028] med        q6  ? before
    @+104181 [104181] miri       q5  ? before
    @+110138 [110138] need       q4  ? before
    @+122118 [122118] par        q3  ? before
    @+147338 [147338] rho        q2  ? before

# squareword.org 🧩 #1321 🥳 9 ⏱️ 0:07:47.317332

📜 2 sessions

Guesses:

Score Heatmap:
    🟨 🟩 🟩 🟩 🟨
    🟨 🟩 🟩 🟨 🟨
    🟨 🟩 🟨 🟩 🟨
    🟩 🟩 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    P A S T S
    S E T U P
    A R E N A
    L I N E D
    M E T R E


# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1351 😦 23 ⏱️ 0:04:58.057336

📜 1 sessions
💰 score: 4370

    6/6
    HEARS ⬜⬜⬜⬜⬜
    LUPIN ⬜⬜⬜🟨🟨
    MINGY ⬜🟩🟩⬜🟩
    ZINKY ⬜🟩🟩⬜🟩
    WINDY ⬜🟩🟩⬜🟩
    NINNY 🟩🟩🟩🟩🟩
    6/6
    NINNY ⬜⬜⬜⬜🟩
    LEARY ⬜⬜⬜🟨🟩
    RUSHY 🟨🟩⬜⬜🟩
    TURFY ⬜🟩🟩⬜🟩
    GURDY ⬜🟩🟩⬜🟩
    CURVY 🟩🟩🟩🟩🟩
    4/6
    CURVY ⬜🟨🟨⬜⬜
    ROUST 🟨🟨🟨⬜⬜
    AMOUR ⬜⬜🟩🟩🟨
    GROUP 🟩🟩🟩🟩🟩
    5/6
    GROUP ⬜⬜🟩⬜⬜
    STOLE 🟨⬜🟩⬜🟩
    WHOSE ⬜⬜🟩🟩🟩
    NOOSE ⬜🟩🟩🟩🟩
    MOOSE 🟩🟩🟩🟩🟩
    Final 2/2
    TOWER ⬜🟩⬜🟩🟩
    JOKER ⬜🟩⬜🟩🟩
    FAIL: HOMER

# dontwordle.com 🧩 #1208 🥳 6 ⏱️ 0:06:55.321033

📜 3 sessions
💰 score: 40

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:JINNI n n n n n remain:7302
    ⬜⬜⬜⬜⬜ tried:ADDAX n n n n n remain:3105
    ⬜⬜⬜⬜⬜ tried:YUPPY n n n n n remain:1306
    ⬜⬜⬜⬜⬜ tried:LEVEL n n n n n remain:303
    ⬜🟨⬜⬜⬜ tried:BOFFO n m n n n remain:58
    ⬜🟨🟩⬜⬜ tried:CROCK n m Y n n remain:5

    Undos used: 2

      5 words remaining
    x 8 unused letters
    = 40 total score

# cemantle.certitudes.org 🧩 #1258 🥳 376 ⏱️ 0:08:27.043420

🤔 377 attempts
📜 1 sessions
🫧 16 chat sessions
⁉️ 96 chat prompts
🤖 4 llama3.2:latest replies
🤖 92 gemma3:12b replies
😱   1 🔥   6 🥵  23 😎  59 🥶 285 🧊   2

      $1 #377   ~1 afraid           100.00°C 🥳 1000‰
      $2 #236  ~53 scared            79.47°C 😱  999‰
      $3 #194  ~64 fearful           69.92°C 🔥  998‰
      $4 #247  ~45 worried           64.94°C 🔥  997‰
      $5 #238  ~51 frightened        64.76°C 🔥  996‰
      $6 #114  ~87 hesitant          62.42°C 🔥  995‰
      $7 #240  ~49 terrified         61.77°C 🔥  994‰
      $8 #126  ~82 reluctant         58.76°C 🔥  993‰
      $9 #231  ~56 intimidated       53.19°C 🥵  986‰
     $10 #115  ~86 apprehensive      52.68°C 🥵  982‰
     $11 #158  ~71 wary              51.80°C 🥵  979‰
     $32 #127  ~81 skittish          39.75°C 😎  892‰
     $91 #337      unprotected       27.14°C 🥶
    $376 #121      introductory      -3.84°C 🧊

# cemantix.certitudes.org 🧩 #1291 🥳 840 ⏱️ 0:57:41.845363

🤔 841 attempts
📜 1 sessions
🫧 41 chat sessions
⁉️ 252 chat prompts
🤖 149 llama3.2:latest replies
🤖 103 gemma3:12b replies
😱   1 🔥   4 🥵  25 😎  82 🥶 648 🧊  80

      $1 #841   ~1 bilatéral            100.00°C 🥳 1000‰
      $2 #689  ~21 multilatéral          62.88°C 😱  999‰
      $3 #115 ~104 coopération           61.15°C 🔥  998‰
      $4 #190  ~79 négociation           43.23°C 🔥  993‰
      $5 #545  ~40 diplomatique          41.16°C 🔥  991‰
      $6 #253  ~67 échange               41.12°C 🔥  990‰
      $7 #181  ~81 renforcement          40.32°C 🥵  987‰
      $8 #837   ~3 intergouvernemental   40.08°C 🥵  986‰
      $9 #127 ~100 partenariat           40.03°C 🥵  985‰
     $10 #609  ~36 international         39.99°C 🥵  984‰
     $11  #98 ~110 accord                39.82°C 🥵  983‰
     $32 #125 ~101 harmonisation         31.05°C 😎  896‰
    $114 #776      conflit               22.50°C 🥶
    $762 #648      convenant             -0.23°C 🧊
