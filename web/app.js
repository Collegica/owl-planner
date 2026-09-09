// The page. Files in memory, configuration in IndexedDB, the engine in a
// worker. No request is made after the runtime has loaded.

const $ = (id) => document.getElementById(id);
const CFG = ['rules.yml', 'loans.yml', 'known-annual.yml'];

// ---------------------------------------------------------------- storage
// IndexedDB, one store, keyed by file name. Private to this origin and this
// browser; "Delete everything stored here" empties it.
const db = {
  open() {
    return new Promise((res, rej) => {
      const r = indexedDB.open('owl-planner', 1);
      r.onupgradeneeded = () => r.result.createObjectStore('files');
      r.onsuccess = () => res(r.result);
      r.onerror = () => rej(r.error);
    });
  },
  async get(key) {
    try {
      const d = await this.open();
      return await new Promise((res, rej) => {
        const t = d.transaction('files').objectStore('files').get(key);
        t.onsuccess = () => res(t.result); t.onerror = () => rej(t.error);
      });
    } catch { return undefined; }
  },
  async set(key, value) {
    try {
      const d = await this.open();
      await new Promise((res, rej) => {
        const t = d.transaction('files', 'readwrite').objectStore('files').put(value, key);
        t.onsuccess = res; t.onerror = () => rej(t.error);
      });
    } catch { /* storage unavailable: the page still works for this session */ }
  },
  async clear() {
    try {
      const d = await this.open();
      await new Promise((res, rej) => {
        const t = d.transaction('files', 'readwrite').objectStore('files').clear();
        t.onsuccess = res; t.onerror = () => rej(t.error);
      });
    } catch { /* nothing stored */ }
  },
};

// ---------------------------------------------------------------- state
const state = {
  files: [],                       // [{name, text, size, converted?: {from, bank, transactions}}]
  pending: [],                     // PDFs the worker is still converting, by name
  refused: [],                     // PDFs it would not use: [{name, why, extracted, stated, bank, banks}]
  config: { 'rules.yml': '', 'loans.yml': '', 'known-annual.yml': '' },
  examples: {},                    // the shipped *.example.yml, for reset and first run
  current: 'rules.yml',
  ready: false,
  result: null,
};

// ---------------------------------------------------------------- worker
const worker = new Worker('worker.js', { type: 'module' });
worker.onmessage = (e) => {
  const m = e.data;
  if (m.type === 'status') setRuntime('loading', m.text);
  else if (m.type === 'ready') {
    state.ready = true;
    setRuntime('ready', `Ready — Python loaded in ${m.seconds}s. Nothing leaves this tab.`);
    $('version').textContent = `Pyodide ${m.version}.`;
    updateRunButton();
    for (const send of waitingForRuntime.splice(0)) send();
  } else if (m.type === 'result') showResult(m);
  else if (m.type === 'converted') finishConvert(m);
  else if (m.type === 'error') {
    setRuntime('error', m.text);
    $('run').disabled = false; $('run').textContent = 'Build the budget';
  }
};

function setRuntime(cls, text) {
  const el = $('runtime'); el.className = `pill ${cls}`; el.textContent = text;
}

// ---------------------------------------------------------------- files
function human(n) { return n < 1024 ? `${n} B` : n < 1048576 ? `${(n / 1024).toFixed(0)} KB` : `${(n / 1048576).toFixed(1)} MB`; }

function renderFiles() {
  const ul = $('files'); ul.innerHTML = '';
  for (const f of state.files) {
    const li = document.createElement('li');
    if (f.converted) {
      // the CSV made from a PDF: say so, and offer it, so it can be kept and
      // dropped next time without converting again
      li.innerHTML = `<span class="name"></span><span class="size"></span><button class="btn small quiet" type="button" data-act="download">download CSV</button><button class="btn small quiet" type="button" data-act="remove">remove</button>`;
      li.querySelector('.size').textContent = `converted from ${f.converted.from} (${f.converted.bank}), ${f.converted.transactions} transactions, reconciled`;
      li.querySelector('[data-act="download"]').onclick = () => download(f.name, f.text, 'text/csv');
    } else {
      li.innerHTML = `<span class="name"></span><span class="size">${human(f.size)}</span><button class="btn small quiet" type="button" data-act="remove">remove</button>`;
    }
    li.querySelector('.name').textContent = f.name;
    li.querySelector('[data-act="remove"]').onclick = () => { state.files = state.files.filter((x) => x !== f); renderFiles(); };
    ul.appendChild(li);
  }
  for (const name of state.pending) {
    const li = document.createElement('li');
    li.innerHTML = '<span class="name"></span><span class="size">converting in this tab…</span>';
    li.querySelector('.name').textContent = name;
    ul.appendChild(li);
  }
  updateRunButton();
}

async function addFiles(list) {
  $('dropNotice').hidden = true;
  for (const file of list) {
    if (/\.pdf$/i.test(file.name)) { convertPdf(file); continue; }
    const text = await file.text();
    state.files = state.files.filter((x) => x.name !== file.name);
    state.files.push({ name: file.name, text, size: file.size });
  }
  renderFiles();
}

// ---------------------------------------------------------------- PDF statements
// A PDF goes to the worker as bytes. pdf.js reads it there, the same
// extractors as the local tool turn it into the normalised CSV, and the same
// gate refuses it unless the transactions add up to the totals the statement
// prints. What comes back joins the run like a dropped CSV, marked as
// converted; what is refused is named here with both figures and not used.
const waitingForRuntime = [];
function convertPdf(file) {
  const send = async () => {
    const bytes = await file.arrayBuffer();
    worker.postMessage({ type: 'convert', name: file.name, bytes }, [bytes]);
  };
  state.pending = state.pending.filter((n) => n !== file.name);
  state.pending.push(file.name);
  state.refused = state.refused.filter((r) => r.name !== file.name);
  if (state.ready) send(); else waitingForRuntime.push(send);
}

function finishConvert(m) {
  state.pending = state.pending.filter((n) => n !== m.name);
  if (m.reconciled) {
    const name = m.name.replace(/\.pdf$/i, '') + '.csv';
    state.files = state.files.filter((x) => x.name !== name);
    state.files.push({ name, text: m.csv, size: new Blob([m.csv]).size,
                       converted: { from: m.name, bank: m.bank, transactions: m.transactions } });
  } else {
    state.refused.push(m);
  }
  renderFiles(); renderRefusals();
}

const money = (v) => '$' + Number(v).toLocaleString('en-CA', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
function renderRefusals() {
  const notice = $('dropNotice');
  if (!state.refused.length) { notice.hidden = true; return; }
  const lines = state.refused.map((r) => {
    const name = `<b>${esc(r.name)}</b>`;
    if (r.why === 'unknown layout') {
      return `${name} is not a layout this page knows. It reads PDF statements from ${r.banks.join(', ')} (matched by the bank's name in the file name or the statement); for another bank, export the CSV from online banking and drop that instead.`;
    }
    if (r.why === 'unreadable') return `${name} could not be read as a PDF${r.error ? ` (${esc(r.error)})` : ''}.`;
    if (r.why === 'no summary found') return `${name} (${r.bank}) was refused: no totals line was found to reconcile against, so nothing from it is used.`;
    const what = r.why === 'deposits mismatch' ? 'deposits' : 'transactions';
    return `${name} (${r.bank}) was refused: its ${what} add up to ${money(r.extracted)} and the statement states ${money(r.stated)}. Nothing from it is used — a parsing error and a real transaction look the same until the totals agree.`;
  });
  notice.hidden = false; notice.className = 'notice bad';
  notice.innerHTML = lines.join('<br>');
}

const drop = $('drop');
drop.addEventListener('dragover', (e) => { e.preventDefault(); drop.classList.add('over'); });
drop.addEventListener('dragleave', () => drop.classList.remove('over'));
drop.addEventListener('drop', (e) => { e.preventDefault(); drop.classList.remove('over'); addFiles(e.dataTransfer.files); });
$('picker').addEventListener('change', (e) => { addFiles(e.target.files); e.target.value = ''; });

$('loadSample').onclick = async () => {
  const names = await (await fetch('sample/manifest.json')).json();
  const files = [];
  for (const name of names) {
    const text = await (await fetch(`sample/statements/${name}`)).text();
    files.push({ name, text, size: new Blob([text]).size });
  }
  state.files = files;
  for (const name of CFG) state.config[name] = await (await fetch(`sample/${name}`)).text();
  await persistConfig();
  renderFiles(); showEditor();
  $('dropNotice').hidden = false; $('dropNotice').className = 'notice';
  $('dropNotice').innerHTML = 'The invented household is loaded — its statements and its rules. Every name, date and amount is made up. Press <b>Build the budget</b>.';
};

// ---------------------------------------------------------------- config editors
async function loadConfig() {
  for (const name of CFG) {
    state.examples[name] = await (await fetch(`app/${name.replace('.yml', '.example.yml')}`)).text();
    const stored = await db.get(name);
    state.config[name] = typeof stored === 'string' ? stored : state.examples[name];
  }
  showEditor();
}

function showEditor() {
  for (const b of $('cfgTabs').querySelectorAll('button')) b.setAttribute('aria-selected', String(b.dataset.name === state.current));
  $('editor').value = state.config[state.current];
}

$('cfgTabs').addEventListener('click', (e) => {
  const b = e.target.closest('button'); if (!b) return;
  state.current = b.dataset.name; showEditor();
});

let saveTimer = null;
$('editor').addEventListener('input', () => {
  state.config[state.current] = $('editor').value;
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => db.set(state.current, state.config[state.current]), 400);
});

async function persistConfig() { for (const name of CFG) await db.set(name, state.config[name]); }

$('resetCfg').onclick = async () => {
  state.config[state.current] = state.examples[state.current];
  await db.set(state.current, state.config[state.current]);
  showEditor();
};

$('exportCfg').onclick = () => download(state.current, state.config[state.current], 'text/yaml');

$('importCfg').onclick = () => $('importPicker').click();
$('importPicker').addEventListener('change', async (e) => {
  const f = e.target.files[0]; if (!f) return;
  state.config[state.current] = await f.text();
  await db.set(state.current, state.config[state.current]);
  showEditor(); e.target.value = '';
});

$('wipe').onclick = async () => {
  await db.clear();
  for (const name of CFG) state.config[name] = state.examples[name];
  state.files = []; renderFiles(); showEditor();
  $('storedNote').textContent = 'Everything stored in this browser by this page has been deleted.';
};

function download(name, text, type) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], { type }));
  a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

// ---------------------------------------------------------------- run
function updateRunButton() {
  $('run').disabled = !(state.ready && state.files.length);
}

$('run').onclick = () => {
  $('run').disabled = true; $('run').textContent = 'Working…';
  const year = parseInt($('year').value, 10);
  worker.postMessage({ type: 'run', files: state.files, config: state.config, year: Number.isFinite(year) ? year : null });
};

// ---------------------------------------------------------------- output
function showResult(m) {
  state.result = m;
  $('run').disabled = false; $('run').textContent = 'Build the budget';
  // the two file lines mean something on a disk, not in a tab
  const text = m.console
    .replace(/^  wrote \/work\/budget\.md$/m, '  budget.md is in the next tab; download it from there')
    .replace(/^  wrote uncategorised\.csv — (.*)$/m, '  not yet categorised: $1 (third tab)');
  $('console').innerHTML = colourConsole(text);
  $('budget').innerHTML = m.budget ? renderMarkdown(m.budget) : '<p class="empty">No budget was written — see the headline.</p>';
  $('dlBudget').disabled = !m.budget;
  $('dlLedger').disabled = !m.ledger;
  $('unc').innerHTML = m.uncategorised ? renderUncategorised(m.uncategorised) : '<p class="empty">Everything was categorised.</p>';
  selectPane('console');
}

$('dlBudget').onclick = () => state.result && download('budget.md', state.result.budget, 'text/markdown');
$('dlLedger').onclick = () => state.result && download('ledger.csv', state.result.ledger, 'text/csv');

function esc(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }

function colourConsole(text) {
  return esc(text)
    .replace(/^(  )([A-Z][A-Z -]+?)(\s{2,})/gm, '$1<span class="k">$2</span>$3')
    .replace(/\$[\d,]+(?:\.\d+)?(?:\/(?:month|year))?/g, (m) => `<span class="amt">${m}</span>`)
    .replace(/\bsteady\b/g, '<span class="ok">steady</span>')
    .replace(/UNEVEN[^\n]*/g, (m) => `<span class="warn">${m}</span>`)
    .replace(/MEASURED over [^\n]*/g, (m) => `<span class="ok">${m}</span>`)
    .replace(/ESTIMATE — [^\n]*/g, (m) => `<span class="warn">${m}</span>`)
    .replace(/UNKNOWN — [^\n]*/g, (m) => `<span class="bad">${m}</span>`)
    .replace(/^(  )(<span class="k">COVERAGE<\/span>)/m, '$1<span class="bad">COVERAGE</span>');
}

// budget.md is headings, paragraphs and pipe tables. That is all this renders.
function renderMarkdown(md) {
  const out = []; const lines = md.split('\n'); let i = 0;
  const inline = (s) => esc(s).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/\*(.+?)\*/g, '<em>$1</em>').replace(/`(.+?)`/g, '<code>$1</code>');
  while (i < lines.length) {
    const l = lines[i];
    const h = l.match(/^(#{1,3})\s+(.*)$/);
    if (h) { out.push(`<h${h[1].length}>${inline(h[2])}</h${h[1].length}>`); i++; continue; }
    if (l.startsWith('|')) {
      const rows = [];
      while (i < lines.length && lines[i].startsWith('|')) { rows.push(lines[i]); i++; }
      const cells = (r) => r.replace(/^\|/, '').replace(/\|$/, '').split('|').map((c) => c.trim());
      const header = cells(rows[0]);
      const body = rows.slice(2).map(cells);
      const num = (c) => /^[-–]?\$?[\d,]+(\.\d+)?%?$/.test(c) || c === '' && false;
      out.push('<table><thead><tr>' + header.map((c, k) => `<th class="${k > 0 ? 'num' : ''}">${inline(c)}</th>`).join('') + '</tr></thead><tbody>'
        + body.map((r) => '<tr>' + r.map((c, k) => `<td class="${k > 0 && (num(c) || c === '') ? 'num' : ''}">${inline(c)}</td>`).join('') + '</tr>').join('')
        + '</tbody></table>');
      continue;
    }
    if (l.trim() === '') { i++; continue; }
    const para = [];
    while (i < lines.length && lines[i].trim() !== '' && !lines[i].startsWith('|') && !/^#{1,3}\s/.test(lines[i])) { para.push(lines[i]); i++; }
    out.push(`<p>${inline(para.join(' '))}</p>`);
  }
  return out.join('\n');
}

function renderUncategorised(csv) {
  const rows = csv.trim().split('\n').slice(1).map((r) => {
    const k = r.indexOf(','); return [r.slice(0, k), r.slice(k + 1)];
  });
  return '<table class="unc"><thead><tr><th>Description</th><th class="num">Total</th></tr></thead><tbody>'
    + rows.map(([t, d]) => `<tr><td>${esc(d.replace(/^"|"$/g, ''))}</td><td class="num">$${Number(t).toLocaleString('en-CA', { maximumFractionDigits: 0 })}</td></tr>`).join('')
    + '</tbody></table>';
}

function selectPane(name) {
  for (const b of $('outTabs').querySelectorAll('button')) b.setAttribute('aria-selected', String(b.dataset.pane === name));
  for (const p of ['console', 'budget', 'unc']) $(`pane-${p}`).hidden = p !== name;
}
$('outTabs').addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) selectPane(b.dataset.pane); });

// ---------------------------------------------------------------- go
loadConfig();
