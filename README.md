# Various Word Game Solvers

This repository is my ongoing fascination with solving word games semi-automatically.

1. originally started out as an [alphaguess.com](https://alphaguess.com/) binary search solver
  - was initially curious to modify mid point selection to try simpler prefix words first
  - this paired with an official scrabble word list proved very effective
  - later on paired with a dutch wordlist to solve [alfagok.diginaut.net](https://alfagok.diginaut.net/)

2. LLM assisted solver for [cemantle](https://cemantle.certitudes.org/) was made next
  - this later was applied to the twin [cemantix](https://cemantix.certitudes.org/) french puzzle
  - and even later became fully automated

3. regular expression driven solver for [squareword.org](https://squareword.org/) came next

4. and a similar regular expression solver for
   [dictionary.com hurdle](https://play.dictionary.com/games/todays-hurdle)
   was made shortly after

5. a randomized/heuristic search solver for
   [spaceword.org](https://spaceword.org/game/70836qp8h14zg6f) is working well
   enough to solve its daily puzzles, but doesn't yet work efficiently enough
   to solve weeklies

6. most recently, have been managing to "not solve wordle" (
   [dontwordle.com](https://dontwordle.com/) ), by a simplified and
   score-inverted descendent of hurdle solver

Throughout I've developed a few modules:
- `sortem.py` -- handles possible word scoring, sampling, and choice
- `store.py` -- every solver stores its state for the day in a log file
  - this log file also contains ans interactive user input and responses
  - in the case of the semantic solver, it contains all of the fully automated prompting
  - a report generation process gets hung off the back of these logs, allowing
    simplified/unified summarization for social sharing
- `ui.py` -- a prompt UI state module, oriented around a
  `State = Callable[[PromptUI], State|None]` monad
- `strkit.py` -- supporting to the log and ui, mostly oriented around a
  peek-able iterator, used to tokenize word, lines, and user input
  - ended up making a neat `MarkedSpec` unit test harness, which allows a test
    to be parameterized by easy to edit markdown content
