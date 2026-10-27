const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { resolve } = require('node:path');
const vm = require('node:vm');

const root = resolve(process.argv[2]);
const reactRoot = resolve(process.argv[3]);
const React = require(`${reactRoot}/react`);
const bundle = readFileSync(`${root}/react-intl.min.js`, 'utf8');
const serverContext = vm.createContext({ React, console, TextEncoder, setTimeout, clearTimeout });
vm.runInContext(readFileSync(
    `${reactRoot}/react-dom/umd/react-dom-server-legacy.browser.production.min.js`, 'utf8'),
    serverContext);
const server = serverContext.ReactDOMServer;

for (const mode of ['global', 'commonjs', 'amd']) {
    const context = vm.createContext({ React, console, Intl, setTimeout, clearTimeout });
    let loaded;
    if (mode === 'commonjs') {
        context.exports = {};
        context.module = { exports: context.exports };
        context.require = name => { assert.equal(name, 'react'); return React; };
    }
    if (mode === 'amd') {
        context.define = (dependencies, factory) => {
            assert.deepEqual(Array.from(dependencies), ['react']);
            loaded = factory(React);
        };
        context.define.amd = {};
    }
    vm.runInContext(bundle, context);
    const api = mode === 'global' ? context.ReactIntl
        : mode === 'commonjs' ? context.module.exports : loaded;
    const errors = [];
    const intl = api.createIntl({ locale: 'en', onError: error => errors.push(error), messages: {
        items: '{count, plural, one {# item} other {# items}} for {name}',
        choice: '{value, select, yes {accepted} other {rejected}}',
        broken: '{count, plural, one {unfinished}',
    } });
    assert.equal(intl.formatMessage({ id: 'items' }, { count: 2, name: '<Alice>' }),
        '2 items for <Alice>');
    assert.equal(intl.formatMessage({ id: 'items' }, { count: 1, name: 'Bob' }), '1 item for Bob');
    assert.equal(intl.formatMessage({ id: 'choice' }, { value: 'yes' }), 'accepted');
    assert.equal(intl.formatNumber(1234.5), '1,234.5');
    assert.equal(intl.formatDate(Date.UTC(2020, 0, 2), {
        year: 'numeric', month: '2-digit', day: '2-digit', timeZone: 'UTC',
    }), '01/02/2020');
    assert.equal(intl.formatMessage({ id: 'missing', defaultMessage: 'Fallback {name}' },
        { name: 'text' }), 'Fallback text');
    assert.equal(intl.formatMessage({ id: 'broken', defaultMessage: 'Recovered' }), 'Recovered');
    assert.ok(errors.length > 0, 'Malformed ICU input must reach onError');
    const html = server.renderToStaticMarkup(React.createElement(api.IntlProvider,
        { locale: 'en', messages: { hello: 'Hello {name}' } },
        React.createElement(api.FormattedMessage, { id: 'hello', values: { name: '<Alice>' } })));
    assert.equal(html, 'Hello &lt;Alice&gt;');
    function Greeting() {
        return React.createElement('strong', null,
            api.useIntl().formatMessage({ id: 'hello' }, { name: 'Hooks' }));
    }
    const Wrapped = api.injectIntl(props => React.createElement('em', null,
        props.intl.formatMessage({ id: 'hello' }, { name: 'Injected' })));
    assert.equal(server.renderToStaticMarkup(React.createElement(api.IntlProvider,
        { locale: 'en', messages: { hello: 'Hello {name}' } },
        React.createElement(React.Fragment, null,
            React.createElement(Greeting), React.createElement(Wrapped)))),
    '<strong>Hello Hooks</strong><em>Hello Injected</em>');
}
console.log('React Intl: UMD exports, ICU grammar, formatting, recovery, SSR, hooks and injection passed');
