const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const directory = path.resolve(process.argv[2]);
const glue = fs.readFileSync(path.join(directory, 'citeproc_rs_wasm.js'), 'utf8');
for (const document of [undefined, {}, { currentScript: null }, {
    currentScript: { src: 'https://example.test/citeproc.js' },
}]) {
    const module = { exports: {} };
    vm.runInNewContext(glue, {
        document, module, URL, TextEncoder, TextDecoder,
        location: { href: 'https://example.test/' },
    });
    assert.equal(typeof module.exports, 'function');
    assert.equal(typeof module.exports.Driver, 'function');
}
global.Zotero = { CiteprocRs: {} };
require(path.join(directory, 'citeproc_rs_wasm_include.js'));
const bindings = require(path.join(directory, 'citeproc_rs_wasm.js'));
bindings.initSync({ module: fs.readFileSync(path.join(directory, 'citeproc_rs_wasm_bg.wasm')) });

const style = `<style xmlns="http://purl.org/net/xbiblio/csl" version="1.0" class="in-text">
<info><title>Package check</title><id>https://example.org/package-check</id>
<updated>2026-09-27T00:00:00Z</updated></info>
<citation><layout><text variable="title"/></layout></citation>
<bibliography><layout><text variable="title"/></layout></bibliography>
</style>`;
const driver = new bindings.Driver({ style, format: 'html' });
try {
    driver.insertReference({ id: 'book', type: 'book', title: 'Source build' });
    driver.initClusters([{ id: 'one', cites: [{ id: 'book' }] }]);
    driver.setClusterOrder([{ id: 'one' }]);
    assert.equal(driver.builtCluster('one'), 'Source build');
    assert.deepEqual(driver.fullRender().bibEntries, [{ id: 'book', value: 'Source build' }]);
    // Exercise Result<String, Error> repeatedly, then verify the same driver
    // still works. The old upstream bindgen fork fixed this error-return path.
    for (let index = 0; index < 10; index++) {
        assert.throws(
            () => driver.previewCluster({ cites: [{ id: 'book' }] }, [{}], 'plaintext'),
            error => error instanceof Zotero.CiteprocRs.CiteprocRsDriverError
                && /Unknown output format/.test(error.message)
        );
        assert.equal(driver.builtCluster('one'), 'Source build');
    }
    assert.throws(() => driver.setStyle('<style/>'), Zotero.CiteprocRs.CslStyleError);
    assert.equal(driver.builtCluster('one'), 'Source build');
} finally {
    driver.free();
}
// Odd-length heap-backed macro names expose the old smartstring dependency's
// reliance on Rust String field ordering when cloning CSL attributes.
for (const length of [27, 31, 63]) {
    const name = 'a'.repeat(length);
    const macroStyle = style.replaceAll('<text variable="title"/>', `<text macro="${name}"/>`)
        .replace('<citation>', `<macro name="${name}"><text variable="title"/></macro><citation>`);
    const macroDriver = new bindings.Driver({ style: macroStyle, format: 'html' });
    try {
        macroDriver.insertReference({ id: 'book', type: 'book', title: 'Heap-backed macro' });
        macroDriver.initClusters([{ id: 'one', cites: [{ id: 'book' }] }]);
        macroDriver.setClusterOrder([{ id: 'one' }]);
        assert.equal(macroDriver.builtCluster('one'), 'Heap-backed macro');
        assert.deepEqual(macroDriver.fullRender().bibEntries, [
            { id: 'book', value: 'Heap-backed macro' },
        ]);
    } finally {
        macroDriver.free();
    }
}
console.log('Citeproc citation, bibliography, heap-backed macros and error-return checks passed');
