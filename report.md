# 2025-09-26

- 🔗 spaceword.org 🧩 2025-09-25 🏁 score 2168 ranked 40.9% 167/408 ⏱️ 0:33:28.723284
- 🔗 alfagok.diginaut.net 🧩 #328 🥳 12 ⏱️ 0:00:42.208779
- 🔗 alphaguess.com 🧩 #794 🥳 17 ⏱️ 0:01:20.475692
- 🔗 squareword.org 🧩 #1334 🥳 8 ⏱️ 0:04:25.346336
- 🔗 dictionary.com hurdle 🧩 #1364 🥳 14 ⏱️ 0:07:00.624353
- 🔗 dontwordle.com 🧩 #1221 🥳 6 ⏱️ 0:08:42.817568
- 🔗 cemantle.certitudes.org 🧩 #1271 🥳 340 ⏱️ 0:20:08.184117
- 🔗 cemantix.certitudes.org 🧩 #1304 🥳 163 ⏱️ 0:22:23.297410

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







# spaceword.org 🧩 2025-09-25 🏁 score 2168 ranked 40.9% 167/408 ⏱️ 0:33:28.723284

📜 4 sessions
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


# alfagok.diginaut.net 🧩 #328 🥳 12 ⏱️ 0:00:42.208779

🤔 12 attempts
📜 1 sessions

    @        [     0] &-teken     
    @+1      [     1] &-tekens    
    @+2      [     2] -cijferig   
    @+3      [     3] -e-mail     
    @+24911  [ 24911] bad         q3  ? after
    @+31128  [ 31128] begeleid    q5  ? after
    @+34011  [ 34011] beleid      q6  ? after
    @+34829  [ 34829] belucht     q8  ? after
    @+35211  [ 35211] beneden     q9  ? after
    @+35437  [ 35437] benodigd    q10 ? after
    @+35530  [ 35530] benzine     q11 ? it
    @+35530  [ 35530] benzine     done. it
    @+35662  [ 35662] beoordeling q7  ? before
    @+37365  [ 37365] bescherm    q4  ? before
    @+49848  [ 49848] boks        q2  ? before
    @+99750  [ 99750] ex          q1  ? before
    @+199843 [199843] lijm        q0  ? before

# alphaguess.com 🧩 #794 🥳 17 ⏱️ 0:01:20.475692

🤔 17 attempts
📜 1 sessions

    @        [     0] aa         
    @+1      [     1] aah        
    @+2      [     2] aahed      
    @+3      [     3] aahing     
    @+98232  [ 98232] mach       q0  ? after
    @+101027 [101027] med        q5  ? after
    @+102528 [102528] meth       q6  ? after
    @+103264 [103264] mid        q7  ? after
    @+103615 [103615] mill       q8  ? after
    @+103755 [103755] milliwatts q10 ? after
    @+103794 [103794] mim        q11 ? after
    @+103846 [103846] mince      q12 ? after
    @+103858 [103858] mind       q13 ? after
    @+103873 [103873] mindful    q14 ? after
    @+103882 [103882] minds      q15 ? after
    @+103887 [103887] mine       q16 ? it
    @+103887 [103887] mine       done. it
    @+103895 [103895] mineral    q9  ? before
    @+104180 [104180] miri       q4  ? before
    @+110137 [110137] need       q3  ? before
    @+122117 [122117] par        q2  ? before
    @+147337 [147337] rho        q1  ? before

# squareword.org 🧩 #1334 🥳 8 ⏱️ 0:04:25.346336

📜 1 sessions

Guesses:

Score Heatmap:
    🟩 🟨 🟩 🟨 🟨
    🟨 🟨 🟩 🟨 🟩
    🟨 🟨 🟨 🟨 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    T R A M S
    E E R I E
    A L O N E
    T I M E D
    S C A R Y

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1364 🥳 14 ⏱️ 0:07:00.624353

📜 1 sessions
💰 score: 10200

    3/6
    RAISE ⬜⬜⬜🟨🟩
    STOVE 🟩🟩⬜⬜🟩
    STYLE 🟩🟩🟩🟩🟩
    4/6
    STYLE ⬜⬜⬜⬜⬜
    INCUR 🟨⬜⬜🟩⬜
    MIXUP 🟨🟨⬜🟩🟨
    OPIUM 🟩🟩🟩🟩🟩
    3/6
    OPIUM ⬜⬜⬜🟨⬜
    CLUES 🟨⬜🟩⬜🟨
    STUCK 🟩🟩🟩🟩🟩
    3/6
    STUCK 🟨⬜⬜⬜⬜
    DEARS 🟩🟩⬜⬜🟨
    DENSE 🟩🟩🟩🟩🟩
    Final 1/2
    INPUT 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1221 🥳 6 ⏱️ 0:08:42.817568

📜 1 sessions
💰 score: 88

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:QAJAQ n n n n n remain:7419
    ⬜⬜⬜⬜⬜ tried:YOBBO n n n n n remain:3170
    ⬜⬜⬜⬜⬜ tried:CIRRI n n n n n remain:870
    ⬜⬜⬜⬜⬜ tried:FLUFF n n n n n remain:308
    ⬜🟨⬜🟩⬜ tried:DEKED n m n Y n remain:29
    ⬜⬜⬜🟩🟨 tried:NGWEE n n n Y m remain:11

    Undos used: 2

      11 words remaining
    x 8 unused letters
    = 88 total score

# cemantle.certitudes.org 🧩 #1271 🥳 340 ⏱️ 0:20:08.184117

🤔 341 attempts
📜 1 sessions
🫧 16 chat sessions
⁉️ 107 chat prompts
🤖 16 llama3.2:latest replies
🤖 91 gemma3:latest replies
😱   1 🔥   5 🥵  15 😎  38 🥶 274 🧊   7

      $1 #341   ~1 governmental     100.00°C 🥳 1000‰
      $2 #327   ~3 regulatory        58.78°C 😱  999‰
      $3 #313   ~8 legislative       49.57°C 🔥  998‰
      $4 #297  ~14 bureaucratic      45.29°C 🔥  996‰
      $5 #174  ~40 government        44.03°C 🔥  994‰
      $6 #241  ~25 civic             42.51°C 🥵  989‰
      $7 #294  ~15 administrative    42.51°C 🔥  990‰
      $8 #300  ~12 municipal         41.87°C 🥵  987‰
      $9 #175  ~39 bureaucracy       40.25°C 🥵  981‰
     $10 #251  ~23 institutional     38.42°C 🥵  978‰
     $11 #287  ~17 local             38.31°C 🥵  974‰
     $23 #112  ~51 accountability    32.49°C 😎  868‰
     $61 #104      mandate           23.38°C 🥶
    $335  #15      rivalry           -0.08°C 🧊

# cemantix.certitudes.org 🧩 #1304 🥳 163 ⏱️ 0:22:23.297410

🤔 164 attempts
📜 1 sessions
🫧 6 chat sessions
⁉️ 34 chat prompts
🤖 34 gemma3:latest replies
🔥  2 🥵 12 😎 37 🥶 78 🧊 34

      $1 #164   ~1 approbation     100.00°C 🥳 1000‰
      $2 #110  ~25 convention       49.03°C 🔥  996‰
      $3 #124  ~20 autorisation     45.24°C 🔥  992‰
      $4  #48  ~48 règlement        40.61°C 🥵  982‰
      $5 #116  ~24 désignation      38.32°C 🥵  978‰
      $6 #144   ~9 décision         37.26°C 🥵  974‰
      $7 #131  ~16 assemblée        37.22°C 🥵  973‰
      $8 #107  ~27 accord           36.52°C 🥵  963‰
      $9 #149   ~6 prévoir          35.47°C 🥵  955‰
     $10 #158   ~3 proposition      34.34°C 🥵  948‰
     $11  #76  ~35 exécution        34.21°C 🥵  947‰
     $16 #139  ~13 protocole        29.28°C 😎  866‰
     $53 #155      dénomination     16.90°C 🥶
    $131  #49      détail           -0.15°C 🧊
