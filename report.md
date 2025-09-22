# 2025-09-23

- 🔗 spaceword.org 🧩 2025-09-22 🏁 score 2173 ranked 3.8% 15/400 ⏱️ 0:51:32.683150
- 🔗 alfagok.diginaut.net 🧩 #325 🥳 17 ⏱️ 0:01:13.750417
- 🔗 alphaguess.com 🧩 #791 🥳 13 ⏱️ 0:02:05.981739
- 🔗 squareword.org 🧩 #1331 🥳 8 ⏱️ 0:05:28.493416
- 🔗 dictionary.com hurdle 🧩 #1361 🥳 18 ⏱️ 0:05:52.868062
- 🔗 dontwordle.com 🧩 #1218 🥳 6 ⏱️ 0:07:43.987221
- 🔗 cemantle.certitudes.org 🧩 #1268 🥳 86 ⏱️ 0:08:47.523420
- 🔗 cemantix.certitudes.org 🧩 #1301 🥳 13 ⏱️ 0:01:10.645041

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




# spaceword.org 🧩 2025-09-22 🏁 score 2173 ranked 3.8% 15/400 ⏱️ 0:51:32.683150

📜 3 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 15/400

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ H _ L _ _ _   
      _ _ _ _ A L E _ _ _   
      _ _ _ _ P I A _ _ _   
      _ _ _ _ P O _ _ _ _   
      _ _ _ _ I N K _ _ _   
      _ _ _ _ S I _ _ _ _   
      _ _ _ _ _ Z _ _ _ _   
      _ _ _ _ J E U _ _ _   
      _ _ _ _ O D _ _ _ _   


# alfagok.diginaut.net 🧩 #325 🥳 17 ⏱️ 0:01:13.750417

🤔 17 attempts
📜 1 sessions

    @        [     0] &-teken    
    @+1      [     1] &-tekens   
    @+2      [     2] -cijferig  
    @+3      [     3] -e-mail    
    @+99750  [ 99750] ex         q1  ? after
    @+111405 [111405] ge         q3  ? after
    @+130430 [130430] gracieus   q4  ? after
    @+139789 [139789] hei        q5  ? after
    @+141146 [141146] her        q7  ? after
    @+142774 [142774] hert       q8  ? after
    @+143602 [143602] hij        q9  ? after
    @+143826 [143826] hindoe     q12 ? after
    @+143922 [143922] hip        q13 ? after
    @+143994 [143994] hipt       q14 ? after
    @+144031 [144031] historie   q15 ? after
    @+144050 [144050] historisch q16 ? it
    @+144050 [144050] historisch done. it
    @+144067 [144067] hit        q11 ? before
    @+144559 [144559] hoek       q6  ? before
    @+149453 [149453] huis       q2  ? before
    @+199843 [199843] lijm       q0  ? before

# alphaguess.com 🧩 #791 🥳 13 ⏱️ 0:02:05.981739

🤔 13 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+47393 [47393] dis       q1  ? after
    @+72813 [72813] gremolata q2  ? after
    @+73585 [73585] guess     q7  ? after
    @+73773 [73773] gum       q9  ? after
    @+73829 [73829] gun       q10 ? after
    @+73903 [73903] gunrunner q11 ? after
    @+73940 [73940] gurgle    q12 ? it
    @+73940 [73940] gurgle    done. it
    @+73976 [73976] gusset    q8  ? before
    @+74374 [74374] had       q6  ? before
    @+75969 [75969] haw       q5  ? before
    @+79145 [79145] hood      q4  ? before
    @+85517 [85517] ins       q3  ? before
    @+98232 [98232] mach      q0  ? before

# squareword.org 🧩 #1331 🥳 8 ⏱️ 0:05:28.493416

📜 2 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟨 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C A R P S
    A L A R M
    M E D I A
    P R I O R
    S T I N T

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1361 🥳 18 ⏱️ 0:05:52.868062

📜 1 sessions
💰 score: 9800

    4/6
    REAIS ⬜⬜⬜⬜⬜
    LUCKY 🟨⬜⬜⬜🟩
    GODLY 🟩🟩⬜🟩🟩
    GOLLY 🟩🟩🟩🟩🟩
    4/6
    GOLLY ⬜⬜⬜⬜⬜
    STAIR ⬜🟨⬜🟩⬜
    TEPID 🟨⬜⬜🟩⬜
    UNFIT 🟩🟩🟩🟩🟩
    4/6
    UNFIT ⬜⬜⬜🟩🟩
    SPRIT ⬜⬜⬜🟩🟩
    LEGIT 🟩⬜⬜🟩🟩
    LIMIT 🟩🟩🟩🟩🟩
    4/6
    LIMIT ⬜🟨⬜⬜🟨
    STINK 🟩🟨🟩⬜⬜
    SUITE 🟩⬜🟩🟩🟩
    SPITE 🟩🟩🟩🟩🟩
    Final 2/2
    FAKEY 🟩⬜⬜🟨🟩
    FERRY 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1218 🥳 6 ⏱️ 0:07:43.987221

📜 1 sessions
💰 score: 6

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:BACCA n n n n n remain:5655
    ⬜⬜⬜⬜⬜ tried:SEEMS n n n n n remain:875
    ⬜⬜⬜⬜⬜ tried:TOOTH n n n n n remain:218
    ⬜⬜⬜⬜⬜ tried:WIGGY n n n n n remain:11
    🟨🟨⬜⬜⬜ tried:KUDZU m m n n n remain:2
    ⬜🟩🟩🟩🟩 tried:FLUNK n Y Y Y Y remain:1

    Undos used: 4

      1 words remaining
    x 6 unused letters
    = 6 total score

# cemantle.certitudes.org 🧩 #1268 🥳 86 ⏱️ 0:08:47.523420

🤔 87 attempts
📜 2 sessions
🫧 3 chat sessions
⁉️ 17 chat prompts
🤖 17 gemma3:12b replies
🥵  2 😎  6 🥶 74 🧊  4

     $1 #87  ~1 accountability  100.00°C 🥳 1000‰
     $2 #71  ~7 leadership       40.10°C 🥵  961‰
     $3 #83  ~4 coordination     35.86°C 🥵  920‰
     $4 #44  ~9 authority        31.62°C 😎  782‰
     $5 #86  ~2 facilitation     26.22°C 😎  293‰
     $6 #77  ~5 management       26.01°C 😎  253‰
     $7 #73  ~6 regulation       25.62°C 😎  174‰
     $8 #70  ~8 jurisdiction     25.27°C 😎  111‰
     $9 #84  ~3 alignment        25.14°C 😎   90‰
    $10 #43     control          23.31°C 🥶
    $11 #61     operational      23.31°C 🥶
    $12 #23     automation       22.94°C 🥶
    $13 #65     real             22.20°C 🥶
    $84  #5     pancake          -3.48°C 🧊

# cemantix.certitudes.org 🧩 #1301 🥳 13 ⏱️ 0:01:10.645041

🤔 14 attempts
📜 1 sessions
🫧 2 chat sessions
⁉️ 3 chat prompts
🤖 3 gemma3:12b replies
🥵  1 😎  2 🥶 10

     $1 #14  ~1 peintre   100.00°C 🥳 1000‰
     $2 #11  ~4 artiste    58.45°C 🥵  988‰
     $3 #13  ~2 musicien   37.57°C 😎  841‰
     $4 #12  ~3 créateur   25.04°C 😎  149‰
     $5  #2     chanson    16.75°C 🥶
     $6  #9     voyage     14.76°C 🥶
     $7  #7     parfum     12.61°C 🥶
     $8 #10     étoile     12.16°C 🥶
     $9  #8     table       9.38°C 🥶
    $10  #1     bateau      8.51°C 🥶
    $11  #6     horizon     7.85°C 🥶
    $12  #5     feuille     3.67°C 🥶
    $13  #3     citron      3.25°C 🥶
    $14  #4     courage     1.64°C 🥶
