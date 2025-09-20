# 2025-09-21

- 🔗 spaceword.org 🧩 2025-09-20 🏁 score 2170 ranked 24.7% 90/365 ⏱️ 15:36:57.302572
- 🔗 alfagok.diginaut.net 🧩 #323 🥳 24 ⏱️ 0:01:51.353329
- 🔗 alphaguess.com 🧩 #789 🥳 13 ⏱️ 0:02:21.839941
- 🔗 squareword.org 🧩 #1329 🥳 8 ⏱️ 0:04:59.470639
- 🔗 dictionary.com hurdle 🧩 #1359 🥳 18 ⏱️ 0:08:12.661684
- 🔗 dontwordle.com 🧩 #1216 🥳 6 ⏱️ 0:10:23.521353
- 🔗 cemantle.certitudes.org 🧩 #1266 🥳 143 ⏱️ 0:11:53.625347
- 🔗 cemantix.certitudes.org 🧩 #1299 🥳 451 ⏱️ 0:29:18.387825

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


# spaceword.org 🧩 2025-09-20 🏁 score 2170 ranked 24.7% 90/365 ⏱️ 15:36:57.302572

📜 6 sessions
- tiles: 21/21
- score: 2170 bonus: +70
- rank: 90/365

      _ _ _ _ A L _ _ _ _   
      _ _ _ _ H O W _ _ _   
      _ _ _ _ _ R E _ _ _   
      _ _ _ _ P Y A _ _ _   
      _ _ _ _ E _ Z _ _ _   
      _ _ _ _ R I A _ _ _   
      _ _ _ _ I _ N _ _ _   
      _ _ _ _ Q _ D _ _ _   
      _ _ _ _ U _ _ _ _ _   
      _ _ _ _ E _ _ _ _ _   


# alfagok.diginaut.net 🧩 #323 🥳 24 ⏱️ 0:01:51.353329

🤔 24 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+49848  [ 49848] boks      q2  ? after
    @+74761  [ 74761] dc        q3  ? after
    @+87223  [ 87223] draag     q4  ? after
    @+93451  [ 93451] eet       q5  ? after
    @+94980  [ 94980] eiwit     q7  ? after
    @+95313  [ 95313] elektro   q9  ? after
    @+95482  [ 95482] elf       q10 ? after
    @+95611  [ 95611] elite     q11 ? after
    @+95647  [ 95647] elixirs   q16 ? after
    @+95656  [ 95656] elk       q17 ? after
    @+95657  [ 95657] elkaar    done. it
    @+95658  [ 95658] elkaars   q23 ? before
    @+95659  [ 95659] elkander  q22 ? before
    @+95661  [ 95661] elke      q21 ? before
    @+95668  [ 95668] elks      q20 ? before
    @+95677  [ 95677] elleboog  q12 ? before
    @+95771  [ 95771] elo       q8  ? before
    @+96585  [ 96585] energiek  q6  ? before
    @+99753  [ 99753] ex        q1  ? before
    @+199847 [199847] lijm      q0  ? before

# alphaguess.com 🧩 #789 🥳 13 ⏱️ 0:02:21.839941

🤔 13 attempts
📜 1 sessions

    @       [    0] aa        
    @+1     [    1] aah       
    @+2     [    2] aahed     
    @+3     [    3] aahing    
    @+47393 [47393] dis       q1  ? after
    @+72813 [72813] gremolata q2  ? after
    @+85517 [85517] ins       q3  ? after
    @+91862 [91862] knot      q4  ? after
    @+94959 [94959] lib       q5  ? after
    @+95274 [95274] ligation  q8  ? after
    @+95427 [95427] lilt      q9  ? after
    @+95443 [95443] limb      q11 ? after
    @+95474 [95474] lime      q12 ? it
    @+95474 [95474] lime      done. it
    @+95507 [95507] limit     q10 ? before
    @+95589 [95589] lin       q7  ? before
    @+96592 [96592] locks     q6  ? before
    @+98232 [98232] mach      q0  ? before

# squareword.org 🧩 #1329 🥳 8 ⏱️ 0:04:59.470639

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟨 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    S W A M P
    L O P E S
    A R R A Y
    B R O N C
    S Y N T H

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1359 🥳 18 ⏱️ 0:08:12.661684

📜 1 sessions
💰 score: 9800

    3/6
    REAIS ⬜⬜⬜⬜🟨
    FUSTY ⬜🟩🟨⬜🟩
    SULKY 🟩🟩🟩🟩🟩
    5/6
    SULKY ⬜⬜🟨⬜⬜
    LIANE 🟨🟨⬜⬜⬜
    WHIRL ⬜⬜🟩⬜🟨
    CLIFT 🟩🟩🟩⬜⬜
    CLIMB 🟩🟩🟩🟩🟩
    4/6
    CLIMB ⬜⬜⬜⬜⬜
    DORSA ⬜⬜🟨⬜⬜
    TUNER ⬜⬜🟨🟩🟨
    PREEN 🟩🟩🟩🟩🟩
    4/6
    PREEN ⬜⬜⬜⬜🟨
    TAINS ⬜🟩🟨🟨⬜
    CANID ⬜🟩🟩🟩⬜
    MANIA 🟩🟩🟩🟩🟩
    Final 2/2
    BOUND 🟨🟨🟨🟨⬜
    UNBOX 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1216 🥳 6 ⏱️ 0:10:23.521353

📜 1 sessions
💰 score: 8

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:CIRRI n n n n n remain:5436
    ⬜⬜⬜⬜⬜ tried:BOBOS n n n n n remain:1305
    ⬜⬜⬜⬜⬜ tried:YUMMY n n n n n remain:505
    ⬜⬜🟩⬜⬜ tried:GNAWN n n Y n n remain:36
    ⬜🟩🟩⬜⬜ tried:FLAVA n Y Y n n remain:3
    ⬜🟩🟩🟩🟩 tried:ELATE n Y Y Y Y remain:1

    Undos used: 3

      1 words remaining
    x 8 unused letters
    = 8 total score

# cemantle.certitudes.org 🧩 #1266 🥳 143 ⏱️ 0:11:53.625347

🤔 144 attempts
📜 1 sessions
🫧 5 chat sessions
⁉️ 23 chat prompts
🤖 23 gemma3:12b replies
🔥   2 🥵   5 😎  16 🥶 115 🧊   5

      $1 #144   ~1 creator        100.00°C 🥳 1000‰
      $2 #137   ~7 producer        47.66°C 🔥  997‰
      $3 #136   ~8 originator      45.67°C 🔥  993‰
      $4 #140   ~5 author          42.00°C 🥵  989‰
      $5  #17  ~24 creation        38.07°C 🥵  980‰
      $6 #142   ~3 composer        36.46°C 🥵  970‰
      $7 #127  ~10 architect       34.32°C 🥵  955‰
      $8 #141   ~4 choreographer   33.43°C 🥵  949‰
      $9 #139   ~6 visionary       30.75°C 😎  899‰
     $10  #48  ~20 genesis         30.50°C 😎  891‰
     $11 #113  ~14 muse            29.74°C 😎  875‰
     $12 #106  ~15 inspiration     29.58°C 😎  872‰
     $25  #74      artistry        21.15°C 🥶
    $140  #83      construction    -0.65°C 🧊

# cemantix.certitudes.org 🧩 #1299 🥳 451 ⏱️ 0:29:18.387825

🤔 452 attempts
📜 1 sessions
🫧 20 chat sessions
⁉️ 123 chat prompts
🤖 123 gemma3:12b replies
😱   1 🔥   2 🥵  14 😎  71 🥶 302 🧊  61

      $1 #452   ~1 mécontent        100.00°C 🥳 1000‰
      $2 #137  ~67 mécontentement    56.34°C 😱  999‰
      $3 #101  ~83 colère            46.21°C 🔥  995‰
      $4 #437   ~3 récrimination     44.67°C 🔥  991‰
      $5 #359  ~16 grogne            41.32°C 🥵  981‰
      $6 #161  ~58 désapprobation    38.92°C 🥵  964‰
      $7 #139  ~66 insatisfaction    38.86°C 🥵  963‰
      $8 #125  ~74 dépit             38.64°C 🥵  962‰
      $9 #145  ~63 grève             38.62°C 🥵  961‰
     $10  #91  ~86 exaspération      37.48°C 🥵  955‰
     $11 #140  ~65 protestation      37.48°C 🥵  954‰
     $19 #299  ~25 reproche          34.17°C 😎  883‰
     $90 #158      regret            24.13°C 🥶
    $392 #442      contrôle          -0.24°C 🧊
