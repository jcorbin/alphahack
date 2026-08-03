// @ts-check

(() => {
  const DROPIN_INIT = '🤖 octordle dropin online';

  /** @template T @param {Iterable<T>} it */
  function itLast(it) { let x; for (x of it) { } return x; }

  /** @template T, V @param {Iterable<T>} it @param {(t: T, i: number) => V} fn */
  function* itMap(it, fn) { let i = 0; for (const x of it) yield fn(x, i++); }

  /**
   * @template T, K
   * @param {Iterable<T>} it
   * @param {(x: T) => K} keyFn
   */
  function itGroupBy(it, keyFn) {
    /** @type {Map<K, T[]>} */
    const map = new Map();
    for (const item of it) {
      const key = keyFn(item);
      let bucket = map.get(key);
      if (!bucket) map.set(key, bucket = []);
      bucket.push(item);
    }
    return map;
  }

  /**
   * @template {{[name: string]: any}} U
   * @param {U[]} data
   * @param {string[]} names
   */
  const toFrame = (data, ...names) => Object.fromEntries(
    names.map(name => [name, data.map(um => um[name])]));

  /**
   * @param {string|string[]} label
   */
  function showStatus(label) {
    const mine = 'octordle-status';
    let el = document.getElementById(mine);
    if (!el) {
      el = document.createElement('dialog');
      el.id = mine;
      Object.assign(el.style, {
        position: 'fixed',
        top: '8px',
        left: '50%',
        transform: 'translateX(-50%)',
        background: '#222',
        color: '#fff',
        padding: '6px 14px',
        borderRadius: '4px',
        zIndex: '9999',
        fontFamily: 'sans-serif',
        fontSize: '13px',
        pointerEvents: 'none',
        whiteSpace: 'pre',
      });
      document.body.appendChild(el);
    }
    if (!(el instanceof HTMLDialogElement)) return;
    if (label) {
      if (Array.isArray(label)) label = label.join('\n');
      el.textContent = label;
      if (!el.open) {
        el.showModal();
        // TODO fix the reentrancy hazard here: if we spam showStatus() faster than this delay, then the old timer will still fire, and close the next re-show prematurely
        setTimeout(() => el.close(), label.includes('\n') ? 3000 : 1500);
      }
    } else {
      el.textContent = '';
      el.close();
    }
  }

  const keyTarget = document;

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
    const byWord = itGroupBy(data, ({ word }) => word);
    return {
      data,
      words,
      byWord
    };
  }

  // ── Keymap registry (evolved from manual listener) ───────────────
  /** @typedef {[keys: string[], label: string, handle: (...a: any[]) => void]} KeymapEntry */
  /** @type {KeymapEntry[]} */
  const KEYMAP = [
    [['*', '*'], '🔍 Inspect Boards', inspectBoards],
    [['*', 'w'], '📋 Copy All', copyAll],
    [['$'], '', copyLatest],
    [['^'], '🤖 Turn Up', turnup],
  ];

  // ── Action handlers ──────────────────────────────────────────────

  async function turnup() { offerText([DROPIN_INIT]); }

  /** @param {Iterable<string>} lines */
  async function offerText(lines) {
    const text = new Blob(Array.from(itMap(lines, line => `${line}\n`)), { type: 'text/plain' });
    const item = new ClipboardItem({ ['text/plain']: text });
    await navigator.clipboard.write([item]);
    alert(`📋 ${await text.text()}`);
  }

  async function inspectBoards() { console.table(Array.from(readBoards())); }

  async function copyAll() {
    const { byWord } = readData();
    const ents = itMap(byWord.entries(), ([word, d]) => [word, toFrame(d, 'board_n', 'resp')]);
    const text = JSON.stringify(Object.fromEntries(ents));
    return offerText([text]);
  }

  async function copyLatest() {
    const { words, byWord } = readData();
    const latest = itLast(words.values());
    if (latest) return copyWordRes(latest, byWord);
  }

  /**
   * @typedef {{
   *   board_n: number;
   *   row_n: number;
   *   word: string;
   *   resp: string;
   * }} WordEnt
   *
   * @param {string} word
   * @param {Map<string, WordEnt[]>} [byWord]
   */
  async function copyWordRes(word, byWord = undefined) {
    return offerText(function*() {
      if (!byWord) ({ byWord } = readData());
      const dat = byWord.get(word);
      if (!dat) throw new Error(`no result for word ${JSON.stringify(word)}`);
      for (const { board_n, resp } of dat) {
        yield `#${board_n} ${resp}`;
      }
    }());
  }

  // ── Event listener (keymap-driven) ───────────────────────────────

  /** @param {string[]} keys */
  function dispatch(keys) {
    const want = keys.join('');
    const entry = KEYMAP.find(([k]) => k.join('') === want);
    if (entry) {
      const [, , fn] = entry;
      try {
        fn();
      } catch (e) {
        showStatus(`⚠️ ${e}`);
        console.error(`KEYMAP[${keys}]`, e);
      }
    }
  }

  /** @type {string[]} */
  let pending = [];

  /** @param {string} key @returns {boolean} */
  const procKey = key => {
    switch (key) {
      case 'Escape':
      case 'Backspace': {
        pending = [];
        showStatus('');
        return true;
      }
      case '?': {
        const prefix = pending.join('');
        const mayb = prefix
          ? KEYMAP.filter(([keys]) => keys.join('').startsWith(prefix))
          : KEYMAP;
        showStatus(mayb
          .map(([keys, label]) => `${keys.join('')} → ${label}`));
        return true;
      }
    }

    if (key.length !== 1) return false;

    pending.push(key);
    const have = pending.length;
    const prefix = pending.join('');

    let any = false;
    for (const [keys] of KEYMAP) {
      const would = keys.join('');
      if (would === prefix) {
        pending = [];
        dispatch(keys);
        return true;
      }
      any = any || would.startsWith(prefix);
    }

    const MAX_LEN = Math.max(...KEYMAP.map(([k]) => k.length), 0);
    if (any && have < MAX_LEN) {
      showStatus(`${pending} ...`);
      return true;
    }

    pending = [];
    if (have > 1) {
      showStatus(`${pending} => abort`);
      return true;
    }

    return false;
  };

  keyTarget.addEventListener('keydown', async ev => {
    if (procKey(ev.key)) {
      ev.preventDefault();
      ev.stopPropagation();
    }
  });

  showStatus('💧 Online <Press ^ For 📋-back>');
})()
