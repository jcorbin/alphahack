# 2025-09-28

- 🔗 spaceword.org 🧩 2025-09-27 🏁 score 2173 ranked 4.5% 17/374 ⏱️ 1:55:14.315492
- 🔗 alfagok.diginaut.net 🧩 #330 🥳 24 ⏱️ 0:02:02.907887
- 🔗 alphaguess.com 🧩 #796 🥳 13 ⏱️ 0:03:16.393783
- 🔗 squareword.org 🧩 #1336 🥳 7 ⏱️ 0:06:05.935713
- 🔗 dictionary.com hurdle 🧩 #1366 🥳 17 ⏱️ 0:09:23.521783
- 🔗 dontwordle.com 🧩 #1223 🥳 6 ⏱️ 0:10:40.383506
- 🔗 cemantle.certitudes.org 🧩 #1273 🥳 26 ⏱️ 0:00:52.268049
- 🔗 cemantix.certitudes.org 🧩 #1306 🥳 998 ⏱️ 0:11:08.530814

# Dev

## WIP

- square: finish questioning work
- meta: improve solver log ux

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


# spaceword.org 🧩 2025-09-27 🏁 score 2173 ranked 4.5% 17/374 ⏱️ 1:55:14.315492

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 17/374

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ P U R _ _ _   
      _ _ _ _ _ _ O _ _ _   
      _ _ _ _ M O T _ _ _   
      _ _ _ _ O B I _ _ _   
      _ _ _ _ W E N _ _ _   
      _ _ _ _ _ L I _ _ _   
      _ _ _ _ Q I _ _ _ _   
      _ _ _ _ _ Z _ _ _ _   
      _ _ _ _ S E I _ _ _   


# alfagok.diginaut.net 🧩 #330 🥳 24 ⏱️ 0:02:02.907887

🤔 24 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199835 [199835] lijm      q0  ? after
    @+199835 [199835] lijm      q1  ? after
    @+223635 [223635] mol       q4  ? after
    @+229654 [229654] natuur    q6  ? after
    @+232671 [232671] niets     q7  ? after
    @+233394 [233394] ninja     q14 ? after
    @+233471 [233471] nitwits   q18 ? after
    @+233475 [233475] niveau    q23 ? it
    @+233475 [233475] niveau    done. it
    @+233489 [233489] nivelleer q22 ? before
    @+233509 [233509] njonja    q21 ? before
    @+233545 [233545] nobel     q17 ? before
    @+233727 [233727] non       q15 ? after
    @+233727 [233727] non       q16 ? before
    @+234109 [234109] noord     q8  ? before
    @+235687 [235687] octetten  q5  ? before
    @+247746 [247746] op        q3  ? before
    @+299753 [299753] schub     q2  ? before

# alphaguess.com 🧩 #796 🥳 13 ⏱️ 0:03:16.393783

🤔 13 attempts
📜 1 sessions

    @       [    0] aa         
    @+1     [    1] aah        
    @+2     [    2] aahed      
    @+3     [    3] aahing     
    @+23580 [23580] cam        q2  ? after
    @+28646 [28646] chloroform q4  ? after
    @+29911 [29911] civvies    q6  ? after
    @+30544 [30544] climes     q7  ? after
    @+30839 [30839] cloud      q8  ? after
    @+30909 [30909] club       q10 ? after
    @+30957 [30957] cluck      q11 ? after
    @+30974 [30974] clump      q12 ? it
    @+30974 [30974] clump      done. it
    @+31007 [31007] cluster    q9  ? before
    @+31176 [31176] coapt      q5  ? before
    @+33712 [33712] con        q3  ? before
    @+47393 [47393] dis        q1  ? before
    @+98232 [98232] mach       q0  ? before

# squareword.org 🧩 #1336 🥳 7 ⏱️ 0:06:05.935713

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟨 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    L E A P T
    A L T E R
    B U R L Y
    E D I T S
    L E A S T

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1366 🥳 17 ⏱️ 0:09:23.521783

📜 1 sessions
💰 score: 9900

    4/6
    DATES ⬜⬜🟨⬜🟨
    HOIST 🟨🟨⬜🟨🟩
    SHOUT 🟩🟩🟩⬜🟩
    SHORT 🟩🟩🟩🟩🟩
    4/6
    SHORT 🟩⬜⬜⬜🟩
    SLEPT 🟩⬜⬜⬜🟩
    SAINT 🟩⬜🟩⬜🟩
    SWIFT 🟩🟩🟩🟩🟩
    4/6
    SWIFT 🟩⬜⬜⬜⬜
    SOREL 🟩🟨🟨⬜⬜
    SAVOR 🟩⬜⬜🟨🟩
    SCOUR 🟩🟩🟩🟩🟩
    4/6
    SCOUR ⬜⬜⬜⬜⬜
    LITHE ⬜⬜⬜⬜🟨
    BANED ⬜⬜🟨🟨🟨
    NEEDY 🟩🟩🟩🟩🟩
    Final 1/2
    TRASH 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1223 🥳 6 ⏱️ 0:10:40.383506

📜 1 sessions
💰 score: 40

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:XYLYL n n n n n remain:8089
    ⬜⬜⬜⬜⬜ tried:MINIM n n n n n remain:3549
    ⬜⬜⬜⬜⬜ tried:HOOCH n n n n n remain:1490
    ⬜⬜🟨⬜⬜ tried:BUTUT n n m n n remain:183
    🟨🟨⬜⬜⬜ tried:TAZZA m m n n n remain:43
    🟨⬜⬜🟨🟩 tried:ARETE m n n m Y remain:4

    Undos used: 1

      4 words remaining
    x 10 unused letters
    = 40 total score

# cemantle.certitudes.org 🧩 #1273 🥳 26 ⏱️ 0:00:52.268049

🤔 27 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 6 chat prompts
🤖 6 gemma3:latest replies
😎  3 🥶 22 🧊  1

     $1 #27  ~1 ritual       100.00°C 🥳 1000‰
     $2 #15  ~3 ancient       37.88°C 😎  898‰
     $3 #17  ~2 lore          35.76°C 😎  843‰
     $4  #7  ~4 quill         27.14°C 😎    8‰
     $5 #22     legend        23.52°C 🥶
     $6  #4     labyrinth     19.90°C 🥶
     $7  #5     melancholy    19.52°C 🥶
     $8 #24     parchment     18.55°C 🥶
     $9  #3     ephemeral     18.43°C 🥶
    $10  #6     mosaic        18.14°C 🥶
    $11  #1     crimson       17.85°C 🥶
    $12 #23     oracle        17.30°C 🥶
    $13 #18     chronicle     16.75°C 🥶
    $27  #9     velocity      -1.20°C 🧊

# cemantix.certitudes.org 🧩 #1306 🥳 998 ⏱️ 0:11:08.530814

🤔 999 attempts
📜 1 sessions
🫧 42 chat sessions
⁉️ 271 chat prompts
🤖 142 llama3.2:latest replies
🤖 129 gemma3:latest replies
🔥   6 🥵  43 😎 179 🥶 660 🧊 110

      $1 #999   ~1 explicite            100.00°C 🥳 1000‰
      $2 #264 ~193 implicite             73.40°C 🔥  998‰
      $3 #275 ~188 implicitement         54.24°C 🔥  995‰
      $4 #831  ~29 formel                51.86°C 🔥  994‰
      $5 #740  ~51 formulation           51.54°C 🔥  993‰
      $6 #518 ~103 précis                50.45°C 🔥  991‰
      $7 #359 ~159 pertinent             50.33°C 🔥  990‰
      $8 #472 ~116 explicitation         49.43°C 🥵  988‰
      $9 #608  ~75 énoncé                48.87°C 🥵  987‰
     $10 #575  ~86 manière               48.58°C 🥵  986‰
     $11 #844  ~27 prescriptif           47.61°C 🥵  985‰
     $51 #361 ~158 essentiel             37.53°C 😎  899‰
    $230 #386      clarté                26.43°C 🥶
    $890  #12      paix                  -0.04°C 🧊
