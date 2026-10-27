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
    let flushes = 0, inFlush = false, created = 0, inserted = 0, removed = 0;
    const ReactDOM = { flushSync(callback) {
        flushes++;
        inFlush = true;
        try { callback(); } finally { inFlush = false; }
    } };
    const document = {
        createElement() { throw new Error('Expected a namespaced Gecko element'); },
        createElementNS(namespace, tag) {
            assert.equal(namespace, 'http://www.w3.org/1999/xhtml');
            assert.equal(tag, 'div');
            created++;
            return { style: {}, offsetWidth: 50, clientWidth: 35 };
        },
        documentElement: {
            appendChild() { inserted++; }, removeChild() { removed++; },
        },
    };
    const context = { React, ReactDOM, document, console, setTimeout, clearTimeout,
        performance, requestAnimationFrame: callback => setTimeout(callback, 0),
        cancelAnimationFrame: clearTimeout };
    context.window = context;
    let amdExport;
    if (mode === 'commonjs') {
        context.module = { exports: {} };
        context.exports = context.module.exports;
        context.require = name => {
            assert.ok(['react', 'react-dom'].includes(name));
            return name === 'react' ? React : ReactDOM;
        };
    } else if (mode === 'amd') {
        context.define = (dependencies, factory) => {
            assert.deepEqual(Array.from(dependencies), ['react', 'react-dom']);
            amdExport = factory(React, ReactDOM);
        };
        context.define.amd = true;
    }
    vm.runInNewContext(bundle, context);
    const api = mode === 'commonjs' ? context.module.exports
        : mode === 'amd' ? amdExport : context.ReactVirtualized;
    for (const name of ['List', 'Grid', 'Table', 'AutoSizer', 'Collection', 'CellMeasurerCache']) {
        assert.equal(typeof api[name], 'function', name);
    }
    const html = server.renderToStaticMarkup(React.createElement(api.List, {
        width: 200, height: 60, rowCount: 100, rowHeight: 20, overscanRowCount: 0,
        rowRenderer: ({ index, key, style }) => React.createElement('div', { key, style }, `<row ${index}>`),
    }));
    assert.match(html, /&lt;row 0&gt;/);
    assert.doesNotMatch(html, /&lt;row 99&gt;/);
    assert.ok(created > 0);
    assert.equal(inserted, created);
    assert.equal(removed, created);
    const cache = new api.CellMeasurerCache({ defaultHeight: 20, defaultWidth: 40, fixedWidth: true });
    assert.equal(cache.getHeight(0, 0), 20);
    cache.set(0, 0, 80, 35);
    assert.equal(cache.getHeight(0, 0), 35);
    cache.clear(0, 0);
    assert.equal(cache.getHeight(0, 0), 20);
    const collection = new api.Collection({ ...api.Collection.defaultProps,
        cellCount: 1, cellSizeAndPositionGetter: () => ({ x: 0, y: 0, height: 500, width: 500 }),
    });
    const element = collection.render();
    const props = { ...element.props, width: 100, height: 100,
        cellLayoutManager: { getTotalSize: () => ({ width: 500, height: 500 }) },
        isScrollingChange: scrolling => assert.equal(scrolling, true),
        onScroll() {},
    };
    const view = new element.type(props);
    view.props = props;
    view._scrollbarSize = 15;
    view._scrollingContainer = { scrollLeft: 12, scrollTop: 34 };
    view.setState = update => {
        assert.equal(inFlush, true, 'scroll state must be updated inside flushSync');
        Object.assign(view.state, update);
    };
    view._onScroll({ target: view._scrollingContainer, cancelable: false });
    assert.equal(flushes, 1);
    assert.equal(view.state.scrollLeft, 12);
    assert.equal(view.state.scrollTop, 34);
    view.componentWillUnmount();
}
console.log('React Virtualized: exports, visible rows, escaping, measurement cache, Gecko DOM and synchronous scrolling passed');
