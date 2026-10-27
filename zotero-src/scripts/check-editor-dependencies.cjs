const assert = require('node:assert/strict');
const { createRequire } = require('node:module');
const { readFileSync } = require('node:fs');
const { resolve } = require('node:path');
const { pathToFileURL } = require('node:url');
const root = resolve(process.argv[2]);
const requireEditor = createRequire(`${root}/note-editor/package.json`);
const { schema } = requireEditor('prosemirror-schema-basic');
const { EditorState, TextSelection } = requireEditor('prosemirror-state');
const { history, undo, redo } = requireEditor('prosemirror-history');
const { toggleMark } = requireEditor('prosemirror-commands');
const { findParentNode } = requireEditor('prosemirror-utils');
let state = EditorState.create({ schema, plugins: [history()] });
const dispatch = transaction => { state = state.apply(transaction); };
dispatch(state.tr.insertText('Source-built editor'));
assert.equal(state.doc.textContent, 'Source-built editor');
assert(undo(state, dispatch));
assert.equal(state.doc.textContent, '');
assert(redo(state, dispatch));
assert.equal(state.doc.textContent, 'Source-built editor');
dispatch(state.tr.setSelection(TextSelection.create(state.doc, 1, 7)));
assert.equal(state.selection.visible, true, 'Text selections must retain prototype visibility');
assert(toggleMark(schema.marks.strong)(state, dispatch));
assert.equal(state.doc.firstChild.firstChild.marks[0].type.name, 'strong');
assert.equal(findParentNode(node => node.type.name === 'paragraph')(state.selection).node.type.name,
    'paragraph');
const { tableNodes, TableMap } = requireEditor('prosemirror-tables');
const { Schema } = requireEditor('prosemirror-model');
const tableSchema = new Schema({
    nodes: schema.spec.nodes.append(tableNodes({ tableGroup: 'block', cellContent: 'paragraph+' })),
    marks: schema.spec.marks,
});
const table = tableSchema.node('table', null, [tableSchema.node('table_row', null, [
    tableSchema.node('table_cell', null, [tableSchema.node('paragraph', null, tableSchema.text('cell'))]),
])]);
assert.equal(TableMap.get(table).width, 1);
assert.equal(TableMap.get(table).height, 1);
const { defaultMarkdownParser } = requireEditor('prosemirror-markdown');
assert.equal(defaultMarkdownParser.parse('**safe** <script>').textContent, 'safe <script>');
for (const name of ['dropcursor', 'gapcursor', 'inputrules', 'keymap', 'schema-list', 'transform', 'view']) {
    assert(Object.keys(requireEditor(`prosemirror-${name}`)).length > 0, name);
}
console.log('Source-built editor: editing, history, marks, selections, tables, Markdown and exports passed');
const inventory = JSON.parse(readFileSync(`${root}/rpm-editor-source-inputs.json`, 'utf8'));
for (const [name, record] of Object.entries(inventory)) {
    const manifest = requireEditor(`${root}/note-editor/node_modules/${name}/package.json`);
    const entry = manifest.exports?.['.'] || manifest.exports;
    const path = entry?.import;
    if (path) {
        assert(record.builds.some(build => build.output === path.replace(/^\.\//, '')),
            `${name}: exported ESM entry must be source-built`);
    }
}
async function checkESM() {
    for (const name of Object.keys(inventory)) {
        const manifest = requireEditor(`${root}/note-editor/node_modules/${name}/package.json`);
        const entry = manifest.exports?.['.'] || manifest.exports;
        const namespace = await import(pathToFileURL(
            resolve(root, 'note-editor/node_modules', name, entry.import)).href);
        assert(Object.keys(namespace).length > 0, `${name}: ESM exports`);
        if (name === 'prosemirror-state') {
            assert.equal(namespace.TextSelection.create(state.doc, 1).visible, true);
        }
        if (name === 'prosemirror-utils') {
            assert.equal(typeof namespace.findParentNode, 'function');
        }
    }
    console.log('Source-built editor: exported ESM entries and selection visibility passed');
}
checkESM().catch(error => { console.error(error); process.exitCode = 1; });
