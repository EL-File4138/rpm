const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const Zotero = { debug() {}, Utilities: { randomString: () => 'preview' } };
vm.runInNewContext(fs.readFileSync(process.argv[2], 'utf8'), { Zotero });
const engine = Object.create(Zotero.CiteprocRs.Engine.prototype);
engine._insertCitationReferences = () => [{ id: 'reference' }];
for (const [requested, expected] of [['text', 'plain'], ['plain', 'plain'], ['html', 'html'], ['rtf', 'rtf']]) {
    engine._driver = {
        previewCluster(cluster, order, format) {
            assert.equal(format, expected);
            assert.equal(cluster.cites[0].id, 'reference');
            assert.equal(order.length, 3);
            assert.equal(order[0].id, 'before');
            assert.equal(order[1].note, 2);
            assert.equal(order[2].id, 'after');
            return 'preview result';
        },
    };
    assert.equal(engine.previewCitationCluster(
        { properties: { noteIndex: '2' } }, [['before', 1]], [['after', 3]], requested),
        'preview result');
}
console.log('Citeproc-rs preview: text/plain mapping and other formats passed');
