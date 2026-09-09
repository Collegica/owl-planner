// Parity: the engine in Pyodide must produce what the CLI produces.
//
//     pixi run web-parity
//
// Loads web/dist/pyodide/ in Node, writes the sample household into the
// virtual filesystem the way worker.js does, runs budget.run(), and compares
// the console text and budget.md with the CLI's. The only lines allowed to
// differ are the two that print a path.

import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const DIST = resolve(ROOT, 'web', 'dist');
if (!existsSync(resolve(DIST, 'pyodide', 'pyodide.mjs'))) {
  console.error('web/dist/ is missing — run `pixi run web-build` first');
  process.exit(2);
}

const { loadPyodide } = await import(pathToFileURL(resolve(DIST, 'pyodide', 'pyodide.mjs')).href);
const pyodide = await loadPyodide({ indexURL: resolve(DIST, 'pyodide') + '/', packages: ['pyyaml'] });

pyodide.FS.mkdirTree('/app');
for (const name of readdirSync(resolve(DIST, 'app'))) {
  pyodide.FS.writeFile(`/app/${name}`, readFileSync(resolve(DIST, 'app', name), 'utf8'));
}
pyodide.FS.mkdirTree('/work/statements');
for (const name of readdirSync(resolve(ROOT, 'sample', 'statements'))) {
  pyodide.FS.writeFile(`/work/statements/${name}`, readFileSync(resolve(ROOT, 'sample', 'statements', name), 'utf8'));
}
for (const name of ['rules.yml', 'loans.yml', 'known-annual.yml']) {
  pyodide.FS.writeFile(`/work/${name}`, readFileSync(resolve(ROOT, 'sample', name), 'utf8'));
}

pyodide.globals.set('argv', pyodide.toPy(['--dir', '/work/statements', '--config', '/work', '--out', '/work/budget.md']));
const webConsole = await pyodide.runPythonAsync(`
import sys; sys.path.insert(0, '/app')
import budget
budget.run(argv)
`);
const webBudget = pyodide.FS.readFile('/work/budget.md', { encoding: 'utf8' });

// the CLI, on the same inputs
const cliConsole = execFileSync('python', ['budget.py', '--dir', 'sample/statements', '--config', 'sample', '--out', 'sample/budget.md'], { cwd: ROOT, encoding: 'utf8' });
const cliBudget = readFileSync(resolve(ROOT, 'sample', 'budget.md'), 'utf8');

const strip = (s) => s.split('\n').filter((l) => !/^  wrote /.test(l)).join('\n');
let failed = 0;
if (strip(webConsole) !== strip(cliConsole)) {
  failed++;
  console.error('console output differs between the browser engine and the CLI:');
  const a = strip(cliConsole).split('\n'), b = strip(webConsole).split('\n');
  for (let i = 0; i < Math.max(a.length, b.length); i++) {
    if (a[i] !== b[i]) console.error(`  line ${i + 1}\n    cli: ${a[i]}\n    web: ${b[i]}`);
  }
}
if (webBudget !== cliBudget) {
  failed++;
  console.error('budget.md differs between the browser engine and the CLI');
}
if (failed) process.exit(1);
const recurring = (cliConsole.match(/RECURRING\s+(\S+)/) || [])[1];
console.log(`parity: browser engine and CLI agree on the sample (RECURRING ${recurring}, ${cliBudget.length} bytes of budget.md)`);
