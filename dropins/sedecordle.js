// @ts-check

(() => {
  const DROPIN_INIT = '🤖 sedecordle dropin online';

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

  /** @typedef {[r: number, g: number, b: number]} Color */

  /** @type {Record<string, Color>} */
  const NAMED_COLORS = {
    black: [0, 0, 0],
    white: [255, 255, 255],
    gray: [128, 128, 128],
    silver: [192, 192, 192],

    red: [255, 0, 0],
    green: [0, 128, 0],
    blue: [0, 0, 255],

    yellow: [255, 255, 0],
    cyan: [0, 255, 255],
    magenta: [255, 0, 255],

    purple: [128, 0, 128],
    navy: [0, 0, 128],
    maroon: [128, 0, 0],
    teal: [0, 128, 128],
    olive: [128, 128, 0],

    orange: [255, 165, 0],
    pink: [255, 192, 203],
    brown: [165, 42, 42],
    lime: [0, 255, 0],

    aqua: [0, 255, 255],
    grey: [128, 128, 128],
  };

  /**
   * @param {number} h
   * @param {number} s
   * @param {number} l
   * @returns {Color}
   */
  function hslToRgb(h, s, l) {
    h = ((h % 360) + 360) % 360;
    s = Math.max(0, Math.min(100, s)) / 100;
    l = Math.max(0, Math.min(100, l)) / 100;
    const c = (1 - Math.abs(2 * l - 1)) * s;
    const x = c * (1 - Math.abs((h / 60) % 2 - 1));
    const m = l - c / 2;
    let r, g, b;
    if (h < 60) { r = c; g = x; b = 0; }
    else if (h < 120) { r = x; g = c; b = 0; }
    else if (h < 180) { r = 0; g = c; b = x; }
    else if (h < 240) { r = 0; g = x; b = c; }
    else if (h < 300) { r = x; g = 0; b = c; }
    else { r = c; g = 0; b = x; }
    return [r + m, g + m, b + m];
  }

  /** @param {string} color @returns {Color|null} */
  const parseColor = (color) => {
    if (!color || typeof color !== 'string') return null;
    const s = color.trim();

    // rgb(r, g, b) / rgba(r, g, b, a)
    let m = s.match(/^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/);
    if (m) return [+m[1], +m[2], +m[3]];

    // hsl(H, S%, L%) / hsla(H, S%, L%, a)
    // TODO isn't the "%" unit optional? can't they be specified as unit-float?
    m = s.match(/^hsla?\(\s*([\d.]+)\s*,\s*(\d+)%?\s*,\s*(\d+)%?/);
    if (m) {
      const [r, g, b] = hslToRgb(+m[1], +m[2], +m[3]);
      return [Math.round(r), Math.round(g), Math.round(b)];
    }

    // Hex: #RGB, #RRGGBB, #RGBA, #RRGGBBAA
    m = s.match(/^#([0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/);
    if (m) {
      let hex = m[1];
      if (hex.length === 3 || hex.length === 4) {
        hex = hex.split('').map(c => c + c).join('');
      }
      return [
        parseInt(hex.slice(0, 2), 16),
        parseInt(hex.slice(2, 4), 16),
        parseInt(hex.slice(4, 6), 16),
      ];
    }

    // Named colors (case-insensitive)
    const lc = s.toLowerCase();
    if (lc in NAMED_COLORS) return [...NAMED_COLORS[lc]];

    return null;
  };

  /** @param {Color} color @param {[label: string, target: Color][]} entries */
  const colorCat = ([r, g, b], ...entries) => entries
    .map(/** @returns {[name: string, dist: number]} */
      ([name, target]) => [name, Math.hypot(r - target[0], g - target[1], b - target[2])])
    .reduce(
      (best, [name, dist]) => dist < best.dist ? { name, dist } : best,
      { name: '', dist: Infinity }
    ).name;

  function* readBoxen() {
    const boxes = document.querySelectorAll('.box.button');
    for (const box of boxes) {
      if (!(box instanceof HTMLElement)) continue;
      const m = box.id.match(/^box(\d+),(\d+),(\d+)/);
      if (!m) continue;
      const [_, board_n, row_n, col_n] = m;
      const text = box.textContent.trim();
      if (!text) continue;
      const style = window.getComputedStyle(box);
      const bg = parseColor(style.backgroundColor);
      const cat = bg ? colorCat(bg,
        ['Y', [106, 170, 100]],
        ['M', [201, 180, 88]],
        ['n', [120, 124, 126]],
      ) : '';
      yield { board_n, row_n, col_n, text, bg, cat };
    }
  }

  function readData() {
    const cells = Array.from(readBoxen());
    const rows = Array.from(itMap(
      itGroupBy(cells, ({ board_n, row_n }) => `${board_n}:${row_n}`).entries(),
      ([key, cells]) => {
        const [board_n, row_n] = key.split(':');
        return {
          board_n: Number(board_n),
          row_n: Number(row_n),
          word: cells.map(c => c.text).join(''),
          resp: cells.map(c => c.cat).join(''),
        };
      }));

    const words = new Set(rows.map(({ word }) => word));
    const byWord = itGroupBy(rows, ({ word }) => word);
    return {
      cells,
      rows,
      words,
      byWord
    };
  }

  /**
   * TODO evolve this to be an options object, so that the caller may opt-in to things like modal (feature of <dialog>)
   *
   * @param {string|string[]} label
   */
  function showStatus(label) {
    const mine = '_sedecordle_status';
    document.body.querySelectorAll(`#${mine}`).forEach(el => el.remove());
    if (!label) return;
    if (Array.isArray(label)) {
      label = label.join('\n');
    }
    // TODO rework over a modern <dialog> element
    const el = document.createElement('div');
    el.id = mine;
    el.textContent = label;
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
    setTimeout(() => el.remove(), label.includes('\n') ? 3000 : 1500);
  }

  const keyTarget = document;

  const knownCodes = new Map([
    ['Backspace', 0x08],
    ['Enter', 0x0D],
    ['Escape', 0x1B],
    // TODO fill in more standard key codes
  ]);

  /** @param {string} key */
  const sendKey = key => {
    let code = '';
    let keyCode = 0;
    const known = knownCodes.get(key);
    if (known !== undefined) {
      code = key;
      keyCode = known;
    } else if (key.match(/^[a-zA-Z]$/)) {
      const ki = key.toUpperCase();
      code = `Key${ki}`;
      keyCode = ki.charCodeAt(0);
    }
    keyTarget.dispatchEvent(new KeyboardEvent('keydown', {
      key,
      code,
      keyCode,
      which: keyCode,
    }));
  };

  // ── Keymap registry ────────────────────────────────────────────────
  /** @typedef {[keys: string[], label: string, handle: (...a: any[]) => void]} KeymapEntry */
  /** @type {KeymapEntry[]} */
  const KEYMAP = [
    [['*', 'c'], '🔍 Inspect Cells', inspectCells],
    [['*', 'r'], '🔍 Inspect Rows', inspectRows],
    [['*', 'w'], '📋 Copy All', copyAll],
    [['$'], '📋 Copy Latest', copyLatest],
    [[':'], '📋 Send It', sendIt],
    [['^'], '🤖 Turn Up', turnup],
  ];

  async function turnup() {
    offerText([DROPIN_INIT]);
  }

  /** @param {number} delay */
  const after = delay => new Promise(resolve => setTimeout(resolve, delay));

  async function sendIt() {
    const raw = await navigator.clipboard.readText();

    const m = raw.match(/^([a-zA-Z]{5})$/);
    if (!m) throw new Error('invalid word input');

    const word = m[1].toLocaleUpperCase();

    for (const key of word) {
      sendKey(key);
      await after(50);
    }

    sendKey('Enter');
    await after(50);

    await copyWordRes(word);
  }

  async function inspectCells() {
    console.table(Array.from(readBoxen()));
  }

  async function inspectRows() {
    const { rows } = readData();
    console.table(rows);
  }

  /** @param {Iterable<string>} lines */
  async function offerText(lines) {
    const text = new Blob(Array.from(itMap(lines, line => `${line}\n`)));
    const item = new ClipboardItem({ ['text/plain']: text });
    await navigator.clipboard.write([item]);
    alert(`📋 ${await text.text()}`);
  }

  async function copyAll() {
    const { byWord } = readData();
    const ents = itMap(byWord.entries(), ([word, d]) => [word, toFrame(d, 'board_n', 'row_n', 'resp')]);
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
