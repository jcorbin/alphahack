// @ts-check

(() => {

  /** @template T @param {Iterable<T>} it */
  function itLast(it) { let x; for (x of it) { } return x; }

  /** @template T, V @param {Iterable<T>} it @param {(t: T, i: number) => V} fn */
  function* itMap(it, fn) { let i = 0; for (const x of it) yield fn(x, i++); }

  /**
   * @template {{[name: string]: any}} U
   * @param {U[]} data
   * @param {string[]} names
   */
  const toFrame = (data, ...names) => Object.fromEntries(
    names.map(name => [name, data.map(um => um[name])]));

  /**
   * @param {DOMTokenList} classList
   * @param {string[]} classLabels
   */
  const classIfy = (classList, ...classLabels) => {
    let i = 0;
    while (i < classLabels.length) {
      const className = classLabels[i++], label = classLabels[i++];
      if (!className) {
        return label;
      } else if (className.startsWith('!')) {
        if (!classList.contains(className.slice(1))) return label;
      } else {
        if (classList.contains(className)) return label;
      }
    }
    return '';
  };

  function* readBoards() {
    const boards = document.querySelectorAll('.board');
    for (let board_i = 0; board_i < boards.length; board_i++) {
      const board = boards[board_i];
      const rows = board.querySelectorAll('.board-row');
      for (let row_i = 0; row_i < rows.length; row_i++) {
        const row = rows[row_i];
        const letters = row.querySelectorAll('.letter');
        const resp = Array.from(itMap(letters,
          el => classIfy(el.classList,
            '!past-guess', '', // XXX 'current-guess'
            'exact-match', 'Y',
            'word-match', 'M',
            '', 'n'))).join('');
        if (!resp) continue;
        const word = Array.from(itMap(letters, el => el.textContent.trim())).join('');
        if (!word) continue;
        yield { board_n: board_i + 1, row_n: row_i + 1, word, resp };
      }
    }
  }

  function readData() {
    const data = Array.from(readBoards());
    const words = new Set(data.map(({ word }) => word));
    const byWord = new Map(Array.from(words).map(word => [word,
      data.filter(({ word: w }) => w == word)
    ]));
    return { data, words, byWord };
  }

  window.addEventListener('keypress', async ({ key }) => {
    switch (key) {

      case '*': {
        const { byWord } = readData();
        const ents = itMap(byWord.entries(), ([word, d]) => [word, toFrame(d, 'board_n', 'resp')]);
        const text = JSON.stringify(Object.fromEntries(ents));
        await navigator.clipboard.write([
          new ClipboardItem({ ['text/plain']: text })
        ]);
        alert(`📋 ${text}`);
        break;
      }

      case '$': {
        const { words, byWord } = readData();
        const latest = itLast(words.values());
        const forLatest = latest && byWord.get(latest);
        const text = forLatest ? forLatest.map(({ board_n, resp }) => `#${board_n} ${resp}\n`).join('') : '';
        await navigator.clipboard.write([
          new ClipboardItem({ ['text/plain']: text })
        ]);
        alert(`📋 ${text}`);
        break;
      }

      case '*': {
        console.table(Array.from(readBoards()));
        break;
      }
    }
  });

})()
