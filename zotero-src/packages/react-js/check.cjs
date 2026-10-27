const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {execFileSync} = require('node:child_process');

const root = path.resolve(process.argv[2]);
if (process.argv[3] === 'commonjs') {
  const React = require(path.join(root, 'react'));
  const jsx = require(path.join(root, 'react/jsx-runtime'));
  const server = require(path.join(root, 'react-dom/server.node'));
  assert.equal(server.renderToStaticMarkup(jsx.jsx('b', {children: '<safe>'})), '<b>&lt;safe&gt;</b>');
  assert.equal(typeof require(path.join(root, 'react-dom/client')).createRoot, 'function');
  assert.equal(typeof require(path.join(root, 'react-dom/profiling')).createRoot, 'function');
  assert.equal(typeof require(path.join(root, 'react-dom/test-utils')).Simulate.click, 'function');
  const scheduler = require(path.join(root, 'scheduler/unstable_mock'));
  let completed = false;
  scheduler.unstable_scheduleCallback(scheduler.unstable_NormalPriority, () => { completed = true; });
  scheduler.unstable_flushAll();
  assert.equal(completed, true);
  assert.equal(React.version, '18.3.1');
  assert.equal(require(path.join(root, 'scheduler/package.json')).version, '0.23.2');
  process.exit(0);
}
for (const mode of ['development', 'production']) {
  execFileSync(process.execPath, [__filename, root, 'commonjs'], {
    env: {...process.env, NODE_ENV: mode}, stdio: 'inherit',
  });
}
for (const variant of ['development', 'production.min']) {
  const context = vm.createContext({console, setTimeout, clearTimeout, TextEncoder});
  for (const [name, file] of [
    ['react', 'react'], ['react-dom', 'react-dom'],
    ['react-dom', 'react-dom-server-legacy.browser'], ['react-is', 'react-is'],
  ]) {
    vm.runInContext(fs.readFileSync(path.join(root, name, 'umd', `${file}.${variant}.js`), 'utf8'), context);
  }
  const React = context.React;
  assert.equal(React.version, '18.3.1');
  assert.equal(typeof context.ReactDOM.createRoot, 'function');
  const Value = React.createContext('fallback');
  function Example() {
    const [count] = React.useState(7);
    return React.createElement('p', null, `${React.useContext(Value)} ${count} <ok>`);
  }
  const tree = React.createElement(Value.Provider, {value: 'value'}, React.createElement(Example));
  assert.equal(context.ReactDOMServer.renderToStaticMarkup(tree), '<p>value 7 &lt;ok&gt;</p>');
  assert.equal(context.ReactIs.isElement(tree), true);
  assert.throws(() => context.ReactDOMServer.renderToStaticMarkup(
    React.createElement('p', null, {invalid: true})), /Objects are not valid|Minified React error/);
}
console.log('React: CommonJS/UMD exports, scheduling, rendering, context, hooks, escaping and invalid children passed');
