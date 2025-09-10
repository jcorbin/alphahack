# 2025-09-11

- 🔗 spaceword.org 🧩 2025-09-10 🏁 score 2173 ranked 2.1% 9/425 ⏱️ 2:32:00.988975
- 🔗 alfagok.diginaut.net 🧩 #313 🥳 13 ⏱️ 0:01:18.895399
- 🔗 alphaguess.com 🧩 #779 🥳 19 ⏱️ 0:02:19.065298
- 🔗 squareword.org 🧩 #1319 🥳 7 ⏱️ 0:04:24.674173
- 🔗 dictionary.com hurdle 🥳 19 ⏱️ 0:07:42.652044
- 🔗 dontwordle.com 🥳 6 ⏱️ 0:10:42.687591
- 🔗 cemantle.certitudes.org 🧩 #1256 🥳 756 ⏱️ 1:04:35.304753
- 🔗 cemantix.certitudes.org 🧩 #1289 🥳 2569 ⏱️ 4:30:43.168092

# Dev

## WIP

- meta is basically done
  - [ ] store daily share(d) state
  - [ ] better logic circa end of day early play, e.g. doing a CET timezone
        puzzle close late in the "prior" day local (EST) time

- semantic does not auto report before exit
  - trying finish -> store today

- semantic: unhandled chat http error:
  ```
  Traceback (most recent call last):
    ...
    File "/home/jcorbin/alphaguess/semantic.py", line 2277, in ideate
      st = self.do_ideate(ui)
    File "/home/jcorbin/alphaguess/semantic.py", line 2309, in do_ideate
      return self.chat_prompt(ui, '.') # TODO can this be an abbr?
             ~~~~~~~~~~~~~~~~^^^^^^^^^
    File "/home/jcorbin/alphaguess/semantic.py", line 3046, in chat_prompt
      for _, content in self.chat_say(ui, prompt):
                        ~~~~~~~~~~~~~^^^^^^^^^^^^
    File "/home/jcorbin/alphaguess/semantic.py", line 3094, in chat_say
      for resp in self.llm_client.chat(model=self.llm_model, messages=self.chat, stream=True):
    ...
  httpx.RemoteProtocolError: Server disconnected without sending a response.
  ```

## TODO

- ui: prompt default handler seems too stop-prone
- hurdle: report note lacks puzzle id
- dontwordle: report note lacks puzzle id
- store: fin is not quite right yet
- space: post fin `! store -> tail -> continue` implies `not run_done`
- square: finish questioning work

# spaceword.org 🧩 2025-09-10 🏁 score 2173 ranked 2.1% 9/425 ⏱️ 2:32:00.988975

📜 5 sessions
- tiles: 21/21
- score: 2173 bonus: +73
- rank: 9/425

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ O R G _ _ _   
      _ _ _ _ _ A _ _ _ _   
      _ _ _ _ _ J O _ _ _   
      _ _ _ _ Q A T _ _ _   
      _ _ _ _ _ S O _ _ _   
      _ _ _ _ E _ L _ _ _   
      _ _ _ _ U _ O _ _ _   
      _ _ _ _ R A G _ _ _   
      _ _ _ _ O X Y _ _ _   

# alfagok.diginaut.net 🧩 #313 🥳 13 ⏱️ 0:01:18.895399

🤔 13 attempts
📜 1 sessions

    @        [     0] &-teken   
    @+1      [     1] &-tekens  
    @+2      [     2] -cijferig 
    @+3      [     3] -e-mail   
    @+199855 [199855] lijm      q0  ? after
    @+299792 [299792] schub     q1  ? after
    @+349578 [349578] vakantie  q2  ? after
    @+374322 [374322] vrij      q3  ? after
    @+386863 [386863] wind      q4  ? after
    @+390072 [390072] wrik      q6  ? after
    @+390739 [390739] zaad      q8  ? after
    @+390885 [390885] zaai      q10 ? after
    @+390924 [390924] zaak      q12 ? it
    @+390924 [390924] zaak      done. it
    @+390962 [390962] zaal      q11 ? before
    @+391090 [391090] zadel     q9  ? before
    @+391494 [391494] zand      q7  ? before
    @+393280 [393280] zelfmoord q5  ? before

# alphaguess.com 🧩 #779 🥳 19 ⏱️ 0:02:19.065298

🤔 19 attempts
📜 1 sessions

    @       [    0] aa              
    @+1     [    1] aah             
    @+2     [    2] aahed           
    @+3     [    3] aahing          
    @+47394 [47394] dis             q1  ? after
    @+72814 [72814] gremolata       q2  ? after
    @+79146 [79146] hood            q4  ? after
    @+82323 [82323] immaterial      q5  ? after
    @+83254 [83254] in              q6  ? after
    @+83534 [83534] inch            q10 ? after
    @+83677 [83677] incomings       q11 ? after
    @+83710 [83710] incomplete      q13 ? after
    @+83730 [83730] incongruences   q14 ? after
    @+83740 [83740] inconscient     q15 ? after
    @+83744 [83744] inconsequent    q16 ? after
    @+83745 [83745] inconsequential done. it
    @+83746 [83746] inconsequently  q18 ? before
    @+83747 [83747] inconsiderable  q17 ? before
    @+83749 [83749] inconsiderate   q12 ? before
    @+83820 [83820] incorrupt       q9  ? before
    @+84386 [84386] indusia         q7  ? after
    @+84386 [84386] indusia         q8  ? before
    @+85518 [85518] ins             q3  ? before
    @+98233 [98233] mach            q0  ? before

# squareword.org 🧩 #1319 🥳 7 ⏱️ 0:04:24.674173

📜 1 sessions

Guesses:

Score Heatmap:
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩 🟩 🟩 🟩 🟩
    🟨 🟨 🟨 🟨 🟨
    🟩 🟩 🟩 🟩 🟩
    🟩:<6 🟨:<11 🟧:<16 🟥:16+

Solution:
    C L A M P
    R A D I I
    I R O N S
    E G R E T
    D E N S E

# [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle) 🧩 #1349 🥳 19 ⏱️ 0:07:42.652044

📜 1 sessions
💰 score: 9700

    5/6
    TAELS ⬜🟨⬜🟨⬜
    ARGOL 🟨⬜⬜⬜🟩
    PIBAL ⬜🟨⬜🟨🟩
    FLAIL ⬜⬜🟩🟩🟩
    QUAIL 🟩🟩🟩🟩🟩
    5/6
    QUAIL ⬜⬜🟨⬜⬜
    AGERS 🟨⬜⬜⬜⬜
    YAPON 🟨🟩⬜⬜⬜
    BAWTY ⬜🟩⬜🟩🟩
    CATTY 🟩🟩🟩🟩🟩
    4/6
    CATTY ⬜⬜⬜⬜🟩
    NOILY ⬜⬜🟨🟩🟩
    DIMLY 🟩🟩⬜🟩🟩
    DILLY 🟩🟩🟩🟩🟩
    4/6
    DILLY 🟨⬜⬜⬜⬜
    HOARD ⬜⬜🟨⬜🟩
    ACTED 🟩⬜⬜🟨🟩
    AMEND 🟩🟩🟩🟩🟩
    Final 1/2
    ETUDE 🟩🟩🟩🟩🟩

# dontwordle.com 🧩 #1206 🥳 6 ⏱️ 0:10:42.687591

📜 1 sessions
💰 score: 16

SURVIVED
> Hooray! I didn't Wordle today!

    ⬜⬜⬜⬜⬜ tried:OVOLO n n n n n remain:6447
    ⬜⬜⬜⬜⬜ tried:YUKKY n n n n n remain:3535
    ⬜⬜⬜⬜⬜ tried:TIMID n n n n n remain:816
    ⬜⬜⬜⬜🟩 tried:BENNE n n n n Y remain:50
    ⬜⬜🟩🟨🟩 tried:AGAPE n n Y m Y remain:5
    🟨⬜🟩🟨🟩 tried:PHASE m n Y m Y remain:2

    Undos used: 2

      2 words remaining
    x 8 unused letters
    = 16 total score


# cemantle.certitudes.org 🧩 #1256 🥳 756 ⏱️ 1:04:35.304753

🤔 757 attempts
📜 5 sessions
🫧 32 chat sessions
⁉️ 214 chat prompts
🤖 71 llama3.2:latest replies
🤖 143 gemma3:12b replies
🔥   6 🥵  24 😎 130 🥶 590 🧊   6

      $1 #757   ~1 tendency            100.00°C 🥳 1000‰
      $2 #754   ~3 propensity           74.04°C 😱  999‰
      $3 #752   ~4 inclination          64.44°C 🔥  997‰
      $4 #751   ~5 proclivity           64.01°C 🔥  996‰
      $5 #182 ~138 reluctance           57.35°C 🔥  995‰
      $6 #193 ~135 disinclination       57.27°C 🔥  994‰
      $7 #190 ~136 unwillingness        51.85°C 🔥  990‰
      $8 #348  ~82 hesitance            50.09°C 🥵  988‰
      $9 #199 ~133 reticence            48.52°C 🥵  984‰
     $10 #183 ~137 aversion             47.51°C 🥵  980‰
     $11 #130 ~150 preoccupation        46.90°C 🥵  978‰
     $32 #269 ~107 pusillanimity        38.64°C 😎  899‰
    $161 #344      discouragement       29.78°C 🥶
    $752 #225      resignation          -0.33°C 🧊

# cemantix.certitudes.org 🧩 #1289 🥳 2569 ⏱️ 4:30:43.168092

🤔 2570 attempts
📜 3 sessions
🫧 125 chat sessions
⁉️ 784 chat prompts
🤖 353 llama3.2:latest replies
🤖 427 gemma3:12b replies
🤖 3 deepseek-r1:latest replies
🔥    4 🥵   33 😎  217 🥶 2107 🧊  208

       $1 #2570    ~1 extrémité          100.00°C 🥳 1000‰
       $2 #1587  ~106 hampe               61.48°C 🔥  998‰
       $3 #2164   ~34 recourber           58.41°C 🔥  996‰
       $4  #768  ~177 tige                54.73°C 🔥  993‰
       $5 #2100   ~41 incurver            54.30°C 🔥  991‰
       $6  #326  ~207 épaulement          53.54°C 🥵  989‰
       $7   #90  ~248 concavité           53.32°C 🥵  987‰
       $8  #993  ~157 concave             52.78°C 🥵  986‰
       $9  #126  ~237 entaille            52.35°C 🥵  983‰
      $10 #1524  ~112 latéral             52.07°C 🥵  982‰
      $11  #139  ~234 enroulement         51.96°C 🥵  981‰
      $38  #442  ~200 évasement           46.21°C 😎  899‰
     $256 #2245       cintrer             34.95°C 🥶
    $2363  #252       insertion           -0.16°C 🧊
