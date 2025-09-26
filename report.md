# 2025-09-27

- 🔗 spaceword.org 🧩 2025-09-26 🏁 score 2173 ranked 7.4% 28/379 ⏱️ 2:49:10.153785
- 🔗 alfagok.diginaut.net 🧩 #329 🥳 24 ⏱️ 0:07:07.328822
- 🔗 alphaguess.com 🧩 #795 🥳 15 ⏱️ 0:00:35.895047
- 🔗 squareword.org 🧩 #1335 🥳 9 ⏱️ 0:03:06.437213
- 🔗 dictionary.com hurdle 🧩 #1365 🥳 18 ⏱️ 0:06:30.356092
- 🔗 dontwordle.com 🧩 #1222 🥳 6 ⏱️ 0:08:14.840370
- 🔗 cemantle.certitudes.org 🧩 #1272 🥳 135 ⏱️ 0:09:58.731840
- 🔗 cemantix.certitudes.org 🧩 #1305 🥳 488 ⏱️ 0:25:58.257169

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

# spaceword.org 🧩 2025-09-25 🏁 score 2168 ranked 40.9% 167/408 ⏱️ 0:34:04.411803

📜 6 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 167/408

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ Q _ _ _   
      _ _ _ Z E B U _ _ _   
      _ _ _ _ _ _ E _ _ _   
      _ _ _ _ F E E _ _ _   
      _ _ _ _ _ A R _ _ _   
      _ _ _ D O R _ _ _ _   
      _ _ _ A V E _ _ _ _   
      _ _ _ L A D Y _ _ _   
      _ _ _ _ _ _ _ _ _ _   




# alfagok.diginaut.net 🧩 #329 🥳 24 ⏱️ 0:07:07.328822

🤔 24 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+99750  [ 99750] ex        q1  ? after
    @+149453 [149453] huis      q2  ? after
    @+174563 [174563] kind      q3  ? after
    @+187202 [187202] kroon     q5  ? after
    @+193500 [193500] lavendel  q6  ? after
    @+194925 [194925] lees      q8  ? after
    @+195642 [195642] leid      q9  ? after
    @+195651 [195651] leiden    q23 ? it
    @+195651 [195651] leiden    done. it
    @+195660 [195660] leiders   q22 ? before
    @+195727 [195727] leidsel   q21 ? before
    @+195805 [195805] lek       q11 ? before
    @+196070 [196070] lengte    q10 ? before
    @+196516 [196516] les       q7  ? before
    @+199835 [199835] lijm      q0  ? before

# alphaguess.com 🧩 #795 🥳 15 ⏱️ 0:00:35.895047

🤔 15 attempts
📜 1 sessions

    @        [     0] aa       
    @+1      [     1] aah      
    @+2      [     2] aahed    
    @+3      [     3] aahing   
    @+98232  [ 98232] mach     q0  ? after
    @+147337 [147337] rho      q1  ? after
    @+150233 [150233] sal      q5  ? after
    @+151753 [151753] scan     q6  ? after
    @+152545 [152545] scombrid q7  ? after
    @+152561 [152561] scoop    q12 ? after
    @+152571 [152571] scoot    q13 ? after
    @+152577 [152577] scooter  q14 ? it
    @+152577 [152577] scooter  done. it
    @+152583 [152583] scop     q11 ? before
    @+152636 [152636] scorn    q10 ? before
    @+152736 [152736] scrag    q9  ? before
    @+152941 [152941] scried   q8  ? before
    @+153337 [153337] sea      q4  ? before
    @+159619 [159619] slug     q3  ? before
    @+171937 [171937] tag      q2  ? before

# squareword.org 🧩 #1335 🥳 9 ⏱️ 0:03:06.437213

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟩 🟩 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟨 🟩 🟩 🟩 🟩
    🟩 🟩 🟨 🟩 🟨
    🟩 🟩 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S T A M P
    H U G E R
    E L I T E
    A L L E Y
    F E E D S

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1365 🥳 18 ⏱️ 0:06:30.356092

📜 1 sessions
💰 score: 9800

    4/6
    ARISE ⬜⬜⬜🟨⬜
    STUCK 🟨⬜🟨🟨⬜
    FOCUS ⬜⬜🟩🟩🟩
    MUCUS 🟩🟩🟩🟩🟩
    5/6
    MUCUS ⬜⬜⬜🟩⬜
    FRAUD ⬜⬜🟨🟩⬜
    ABOUT 🟨⬜⬜🟩⬜
    VAGUE 🟩🟩⬜🟩🟩
    VALUE 🟩🟩🟩🟩🟩
    2/6
    VALUE 🟨🟨🟨🟨⬜
    UVULA 🟩🟩🟩🟩🟩
    5/6
    UVULA ⬜⬜⬜⬜⬜
    TIERS ⬜🟨⬜⬜⬜
    DOING ⬜⬜🟩🟩⬜
    CHINK ⬜🟩🟩🟩⬜
    WHINY 🟩🟩🟩🟩🟩
    Final 2/2
    SPANK 🟩⬜🟩🟩⬜
    STAND 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1222 🥳 6 ⏱️ 0:08:14.840370

📜 1 sessions
💰 score: 10

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:BOBOS n n n n n remain:4159
    ⬜⬜⬜⬜⬜ tried:FUZZY n n n n n remain:2179
    ⬜⬜⬜⬜⬜ tried:CRWTH n n n n n remain:504
    ⬜⬜🟩⬜⬜ tried:DJINN n n Y n n remain:18
    ⬜🟨🟩⬜⬜ tried:KAIAK n m Y n n remain:3
    🟩🟨🟩⬜🟩 tried:ALIVE Y m Y n Y remain:2

    Undos used: 3

      2 words remaining
    x 5 unused letters
    = 10 total score

# cemantle.certitudes.org 🧩 #1272 🥳 135 ⏱️ 0:09:58.731840

🤔 136 attempts
📜 2 sessions
🫧 5 chat sessions
⁉️ 28 chat prompts
🤖 28 gemma3:latest replies
🔥  1 🥵  6 😎 23 🥶 98 🧊  7

      $1 #136   ~1 propaganda         100.00°C 🥳 1000‰
      $2  #66  ~28 falsehood           54.62°C 🔥  994‰
      $3 #129   ~6 rhetoric            51.27°C 🥵  989‰
      $4 #123   ~9 sophistry           44.97°C 🥵  959‰
      $5  #78  ~23 subterfuge          44.82°C 🥵  957‰
      $6 #109  ~12 stratagem           42.92°C 🥵  941‰
      $7 #115  ~11 fallacious          41.92°C 🥵  924‰
      $8  #81  ~22 deception           40.82°C 😎  899‰
      $9  #69  ~27 deceit              40.15°C 😎  886‰
     $10  #83  ~20 duplicity           39.43°C 😎  872‰
     $11 #128   ~7 obfuscation         39.23°C 😎  866‰
     $12 #120  ~10 pernicious          38.10°C 😎  840‰
     $32  #94      illusionary         29.18°C 🥶
    $130   #5      nebula              -0.15°C 🧊

# cemantix.certitudes.org 🧩 #1305 🥳 488 ⏱️ 0:25:58.257169

🤔 489 attempts
📜 3 sessions
🫧 22 chat sessions
⁉️ 136 chat prompts
🤖 62 llama3.2:latest replies
🤖 74 gemma3:latest replies
🔥   3 🥵  22 😎 109 🥶 298 🧊  56

      $1 #489   ~1 requête           100.00°C 🥳 1000‰
      $2 #408  ~29 demande            42.98°C 🔥  996‰
      $3 #111 ~103 saisie             40.56°C 🔥  992‰
      $4 #392  ~34 fichier            40.51°C 🔥  991‰
      $5  #62 ~122 donnée             39.84°C 🥵  989‰
      $6 #266  ~64 indexer            38.71°C 🥵  980‰
      $7 #104 ~107 indexation         36.89°C 🥵  972‰
      $8 #469  ~10 annulation         36.72°C 🥵  970‰
      $9 #385  ~36 procédure          36.02°C 🥵  967‰
     $10 #114 ~102 formulaire         35.13°C 🥵  961‰
     $11 #252  ~66 pertinent          34.33°C 🥵  955‰
     $27 #391  ~35 authentification   30.50°C 😎  896‰
    $136 #348      enquête            18.43°C 🥶
    $434  #13      brillance          -0.23°C 🧊
