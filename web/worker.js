// The engine runs here, off the main thread. The page sends files and
// configuration; this worker writes them into Pyodide's virtual filesystem,
// runs the same budget.py the CLI runs, and sends the text back. Nothing here
// touches the network after loadPyodide() has fetched the runtime.

import { loadPyodide } from './pyodide/pyodide.mjs';

const WORK = '/work';
let pyodide = null;

function post(type, data = {}) { self.postMessage({ type, ...data }); }

async function boot() {
  post('status', { phase: 'download', text: 'Downloading the Python runtime (about 13 MB, once; cached after that)…' });
  const t0 = performance.now();
  pyodide = await loadPyodide({ indexURL: './pyodide/', packages: ['pyyaml'] });
  post('status', { phase: 'start', text: 'Starting Python…' });

  // the engine and its example files, exactly as shipped
  const app = ['budget.py', 'categories.yml', 'rules.example.yml', 'loans.example.yml', 'known-annual.example.yml'];
  pyodide.FS.mkdirTree('/app');
  for (const name of app) {
    const r = await fetch(`./app/${name}`);
    pyodide.FS.writeFile(`/app/${name}`, await r.text());
  }
  pyodide.FS.mkdirTree(`${WORK}/statements`);
  await pyodide.runPythonAsync(`import sys; sys.path.insert(0, '/app'); import budget`);
  post('ready', { seconds: ((performance.now() - t0) / 1000).toFixed(1), version: pyodide.version });
}

function clearDir(dir) {
  for (const name of pyodide.FS.readdir(dir)) {
    if (name === '.' || name === '..') continue;
    pyodide.FS.unlink(`${dir}/${name}`);
  }
}

function readIfExists(path) {
  try { return pyodide.FS.readFile(path, { encoding: 'utf8' }); } catch { return ''; }
}

async function run({ files, config, year }) {
  clearDir(`${WORK}/statements`);
  for (const f of files) pyodide.FS.writeFile(`${WORK}/statements/${f.name}`, f.text);
  for (const name of ['rules.yml', 'loans.yml', 'known-annual.yml']) {
    const path = `${WORK}/${name}`;
    if (config[name] && config[name].trim()) pyodide.FS.writeFile(path, config[name]);
    else { try { pyodide.FS.unlink(path); } catch { /* absent already */ } }
  }
  try { pyodide.FS.unlink(`${WORK}/budget.md`); } catch { /* first run */ }
  try { pyodide.FS.unlink(`${WORK}/uncategorised.csv`); } catch { /* first run */ }
  try { pyodide.FS.unlink(`${WORK}/ledger.csv`); } catch { /* first run */ }

  const argv = ['--dir', `${WORK}/statements`, '--config', WORK, '--out', `${WORK}/budget.md`];
  if (year) argv.push('--year', String(year));
  pyodide.globals.set('argv', pyodide.toPy(argv));
  const console_ = await pyodide.runPythonAsync(`
import importlib, budget
importlib.reload(budget)
budget.run(argv)
`);
  post('result', {
    console: console_,
    budget: readIfExists(`${WORK}/budget.md`),
    uncategorised: readIfExists(`${WORK}/uncategorised.csv`),
    ledger: readIfExists(`${WORK}/ledger.csv`),
  });
}

self.onmessage = async (e) => {
  const m = e.data;
  try {
    if (m.type === 'run') await run(m);
  } catch (err) {
    post('error', { text: String(err && err.message ? err.message : err) });
  }
};

boot().catch((err) => post('error', { text: `The runtime failed to load: ${err && err.message ? err.message : err}` }));
