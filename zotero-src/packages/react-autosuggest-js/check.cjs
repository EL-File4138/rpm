const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const bundle = fs.readFileSync(process.argv[2], 'utf8');
const reactRoot = path.resolve(process.argv[3]);
const React = require(`${reactRoot}/react`);
const serverContext = { React, TextEncoder, console };
vm.runInNewContext(fs.readFileSync(
    `${reactRoot}/react-dom/umd/react-dom-server-legacy.browser.production.min.js`, 'utf8'
), serverContext);
const server = serverContext.ReactDOMServer;
for (const mode of ['global', 'commonjs', 'amd']) {
    const context = { console, setTimeout, clearTimeout, React };
    let amdExport;
    if (mode === 'commonjs') {
        context.module = { exports: {} };
        context.exports = context.module.exports;
        context.require = name => {
            assert.equal(name, 'React');
            return React;
        };
    } else if (mode === 'amd') {
        context.define = (dependencies, factory) => {
            assert.deepEqual(Array.from(dependencies), ['React']);
            amdExport = factory(React);
        };
        context.define.amd = true;
    }
    vm.runInNewContext(bundle, context);
    const Autosuggest = mode === 'commonjs' ? context.module.exports
        : mode === 'amd' ? amdExport : context.Autosuggest;
    assert.equal(typeof Autosuggest, 'function');
    const changes = [], fetches = [], selections = [];
    let clears = 0;
    const props = {
        ...Autosuggest.defaultProps,
        id: 'rpm-check',
        suggestions: ['<Alpha>', 'Beta'],
        alwaysRenderSuggestions: true,
        getSuggestionValue: value => value,
        renderSuggestion: value => React.createElement('span', null, value),
        inputProps: { value: 'A', onChange: (_, data) => changes.push(data) },
        onSuggestionsFetchRequested: data => fetches.push(data),
        onSuggestionsClearRequested: () => clears++,
        onSuggestionSelected: (_, data) => selections.push(data),
    };
    const html = server.renderToStaticMarkup(React.createElement(Autosuggest, props));
    assert.match(html, /role="combobox"/);
    assert.match(html, /role="listbox"/);
    assert.match(html, /&lt;Alpha&gt;/);
    assert.doesNotMatch(html, /<Alpha>/);
    assert.match(html, /aria-controls="react-autowhatever-rpm-check"/);
    const component = new Autosuggest({ ...props, alwaysRenderSuggestions: false });
    component.props = { ...props, alwaysRenderSuggestions: false };
    component.setState = (update, done) => {
        Object.assign(component.state, typeof update === 'function'
            ? update(component.state, component.props) : update);
        if (done) done();
    };
    component.render().props.inputProps.onFocus({});
    assert.equal(fetches.at(-1).reason, 'input-focused');
    component.render().props.inputProps.onChange({ target: { value: 'Be' } });
    assert.equal(changes.at(-1).newValue, 'Be');
    assert.equal(fetches.at(-1).reason, 'input-changed');
    let prevented = 0;
    component.render().props.inputProps.onKeyDown({ keyCode: 40, preventDefault() { prevented++; } }, {
        newHighlightedSectionIndex: null, newHighlightedItemIndex: 1,
    });
    assert.equal(changes.at(-1).newValue, 'Beta');
    component.render().props.inputProps.onKeyDown({ keyCode: 13, preventDefault() { prevented++; } });
    assert.equal(selections.at(-1).suggestion, 'Beta');
    assert.equal(selections.at(-1).method, 'enter');
    assert.equal(prevented, 2);
    assert.ok(clears > 0);
    component.render().props.inputProps.onChange({ target: { value: '' } });
    assert.equal(component.state.isCollapsed, true);
}
console.log('Autosuggest: UMD exports, rendering, escaping, typing and keyboard selection passed');
