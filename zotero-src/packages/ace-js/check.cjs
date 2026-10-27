const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(process.argv[2]);
const context = vm.createContext({console, setTimeout, clearTimeout, setInterval, clearInterval});
context.window = context;
for (const name of ['ace', 'mode-javascript']) {
  vm.runInContext(fs.readFileSync(path.join(root, `${name}.js`), 'utf8'), context);
}
const {Document} = context.ace.require('ace/document');
const document = new Document('first\nsecond');
document.insert({row: 1, column: 6}, '!');
assert.equal(document.getValue(), 'first\nsecond!');
const {Mode} = context.ace.require('ace/mode/javascript');
const tokens = new Mode().getTokenizer().getLineTokens('const answer = 42;', 'start').tokens;
assert(tokens.some(token => token.type === 'constant.numeric' && token.value === '42'));
assert(tokens.some(token => token.type === 'storage.type' && token.value === 'const'));
const worker = vm.createContext({console, setTimeout, clearTimeout, postMessage() {}});
worker.self = worker;
const workerSource = fs.readFileSync(path.join(root, 'worker-javascript.js'), 'utf8');
assert(!workerSource.includes('The Software shall be used for Good, not Evil'));
vm.runInContext(workerSource, worker);
const lint = worker.require('ace/mode/javascript/jshint').JSHINT;
assert.equal(lint('const answer = 42;', {esversion: 6}), true);
assert.equal(lint('const = ;', {esversion: 6}), false);
assert(lint.errors.some(error => error && error.reason));
console.log('Ace: browser/worker loaders, editing, tokenization and lint success/error handling passed');
