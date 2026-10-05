// Path-only instrumentation for the development harness. No file contents,
// request bodies, credentials, or child-process arguments are recorded.
// This observes Node filesystem calls; it is not an OS sandbox.
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const url = require('node:url');
const log = process.env.CF_FILE_TRACE;
const append = fs.appendFileSync.bind(fs);
const seen = new Set();
function record(operation, value) {
  if (!log || typeof value === 'number' || value == null) return;
  let name;
  try { name = path.resolve(value instanceof URL ? url.fileURLToPath(value) : String(value)); }
  catch { return; }
  if (name === log) return;
  const key = operation + '\0' + name;
  if (seen.has(key)) return;
  seen.add(key);
  append(log, JSON.stringify({operation, path: name}) + '\n');
}
for (const name of ['readFileSync','readFile','readdirSync','readdir','openSync','open',
                    'statSync','stat','lstatSync','lstat','accessSync','access',
                    'existsSync','realpathSync','realpath','createReadStream']) {
  const original = fs[name];
  fs[name] = function(...args) { record(name, args[0]); return original.apply(this, args); };
}
for (const name of ['readFile','readdir','open','stat','lstat','access','realpath']) {
  const original = fs.promises[name];
  fs.promises[name] = function(...args) { record('promises.' + name, args[0]); return original.apply(this, args); };
}
require('node:module').syncBuiltinESMExports();
