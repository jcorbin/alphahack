# 2025-09-25

- 🔗 spaceword.org 🧩 2025-09-24 🏁 score 2168 ranked 31.3% 127/406 ⏱️ 1:04:45.217347
- 🔗 alfagok.diginaut.net 🧩 #327 🥳 10 ⏱️ 0:00:35.554940
- 🔗 alphaguess.com 🧩 #793 🥳 9 ⏱️ 0:01:05.840377
- 🔗 squareword.org 🧩 #1333 🥳 9 ⏱️ 0:04:27.521269
- 🔗 dictionary.com hurdle 🧩 #1363 🥳 16 ⏱️ 0:07:31.371067
- 🔗 dontwordle.com 🧩 #1220 🥳 6 ⏱️ 0:10:19.474229
- 🔗 cemantle.certitudes.org 🧩 #1270 🥳 19 ⏱️ 0:13:22.322943
- 🔗 cemantix.certitudes.org 🧩 #1303 🥳 1367 ⏱️ 5:35:07.358210

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






# spaceword.org 🧩 2025-09-24 🏁 score 2168 ranked 31.3% 127/406 ⏱️ 1:04:45.217347

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 127/406

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ D U H _ _ _ _ E _   
      _ A _ _ F I Q U E _   
      _ N I X E _ _ _ L _   
      _ _ D I Z E N _ Y _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   


# alfagok.diginaut.net 🧩 #327 🥳 10 ⏱️ 0:00:35.554940

🤔 10 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+24911  [ 24911] bad       q3  ? after
    @+37365  [ 37365] bescherm  q4  ? after
    @+43071  [ 43071] bij       q5  ? after
    @+44588  [ 44588] binnen    q7  ? after
    @+45483  [ 45483] bis       q8  ? after
    @+45843  [ 45843] blad      q9  ? it
    @+45843  [ 45843] blad      done. it
    @+46457  [ 46457] blief     q6  ? before
    @+49848  [ 49848] boks      q2  ? before
    @+99750  [ 99750] ex        q1  ? before
    @+199843 [199843] lijm      q0  ? before

# alphaguess.com 🧩 #793 🥳 9 ⏱️ 0:01:05.840377

🤔 9 attempts
📜 1 sessions

    @        [     0] aa        
    @+1      [     1] aah       
    @+2      [     2] aahed     
    @+3      [     3] aahing    
    @+98232  [ 98232] mach      q0 ? after
    @+147337 [147337] rho       q1 ? after
    @+171937 [171937] tag       q2 ? after
    @+172499 [172499] tap       q7 ? after
    @+172835 [172835] tattle    q8 ? it
    @+172835 [172835] tattle    done. it
    @+173177 [173177] technical q6 ? before
    @+174423 [174423] test      q5 ? before
    @+176974 [176974] tom       q4 ? before
    @+182024 [182024] un        q3 ? before

# squareword.org 🧩 #1333 🥳 9 ⏱️ 0:04:27.521269

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟩 🟨 🟨
    🟨 🟩 🟨 🟨 🟩
    🟨 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T O V E
    P A L E D
    U S I N G
    R E V U E
    T R E E D

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1363 🥳 16 ⏱️ 0:07:31.371067

📜 1 sessions
💰 score: 10000

    3/6
    STARE 🟩⬜⬜⬜🟩
    SINCE 🟩⬜🟩⬜🟩
    SENSE 🟩🟩🟩🟩🟩
    4/6
    SENSE ⬜⬜⬜⬜⬜
    FLIRT ⬜⬜⬜🟨⬜
    MORPH ⬜⬜🟩🟨⬜
    PARKA 🟩🟩🟩🟩🟩
    4/6
    PARKA ⬜🟨⬜⬜⬜
    HEALS ⬜🟨🟩⬜⬜
    INANE ⬜🟩🟩⬜🟨
    ENACT 🟩🟩🟩🟩🟩
    4/6
    ENACT 🟨⬜🟩⬜⬜
    READS 🟨🟨🟩⬜⬜
    GRAVE ⬜🟩🟩🟩🟩
    BRAVE 🟩🟩🟩🟩🟩
    Final 1/2
    ANGRY 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1220 🥳 6 ⏱️ 0:10:19.474229

📜 1 sessions
💰 score: 4

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:PHPHT n n n n n remain:7300
    ⬜⬜⬜⬜⬜ tried:CIRRI n n n n n remain:2838
    ⬜⬜⬜⬜⬜ tried:EGGED n n n n n remain:833
    ⬜⬜⬜⬜⬜ tried:FLUNK n n n n n remain:105
    ⬜⬜⬜🟩⬜ tried:OXBOW n n n Y n remain:3
    ⬜🟩🟨🟩🟨 tried:MAYOS n Y m Y m remain:1

    Undos used: 3

      1 words remaining
    x 4 unused letters
    = 4 total score

# cemantle.certitudes.org 🧩 #1270 🥳 19 ⏱️ 0:13:22.322943

🤔 20 attempts
📜 2 sessions
🫧 2 chat sessions
⁉️ 6 chat prompts
🤖 6 gemma3:12b replies
🥵  1 😎  1 🥶 17

     $1 #20  ~1 carbon        100.00°C 🥳 1000‰
     $2 #18  ~2 biodiversity   37.82°C 🥵  968‰
     $3 #16  ~3 algae          28.73°C 😎  682‰
     $4  #8     ocean          21.45°C 🥶
     $5 #15     coral          21.44°C 🥶
     $6 #13     sea            15.11°C 🥶
     $7  #2     bicycle        14.63°C 🥶
     $8  #4     candle         13.64°C 🥶
     $9  #5     galaxy         13.22°C 🥶
    $10 #12     fish           12.72°C 🥶
    $11  #3     brick          12.69°C 🥶
    $12 #19     archipelago     9.18°C 🥶
    $13 #14     abyss           8.83°C 🥶
    $14  #6     melody          7.95°C 🥶

# cemantix.certitudes.org 🧩 #1303 🥳 1367 ⏱️ 5:35:07.358210

🤔 1368 attempts
📜 6 sessions
🫧 64 chat sessions
⁉️ 388 chat prompts
🤖 134 llama3.2:latest replies
🤖 254 gemma3:12b replies
😱   1 🔥   6 🥵  35 😎 154 🥶 999 🧊 172

       $1 #1368    ~1 suspens           100.00°C 🥳 1000‰
       $2   #89  ~172 suspense           65.00°C 😱  999‰
       $3  #104  ~162 rebondissement     50.10°C 🔥  998‰
       $4   #96  ~167 dénouement         48.19°C 🔥  997‰
       $5   #30  ~191 intrigue           46.91°C 🔥  996‰
       $6 #1325    ~5 haletant           45.61°C 🔥  995‰
       $7  #262  ~122 palpitant          39.50°C 🔥  993‰
       $8   #19  ~194 protagoniste       37.40°C 🔥  990‰
       $9   #81  ~175 énigme             36.61°C 🥵  987‰
      $10  #532   ~88 thriller           36.22°C 🥵  986‰
      $11  #550   ~86 finalement         35.86°C 🥵  985‰
      $44  #801   ~66 crucial            27.39°C 😎  898‰
     $198  #733       soubresaut         17.91°C 🥶
    $1197  #435       complet            -0.05°C 🧊
