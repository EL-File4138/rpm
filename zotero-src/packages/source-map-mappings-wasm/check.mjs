import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const callbacks = [];
const { instance } = await WebAssembly.instantiate(await readFile(process.argv[2]), {
    env: { mapping_callback: (...mapping) => callbacks.push(mapping) },
});
const api = instance.exports;
function parse(text) {
    const bytes = new TextEncoder().encode(text);
    const pointer = api.allocate_mappings(bytes.length);
    new Uint8Array(api.memory.buffer, pointer, bytes.length).set(bytes);
    return api.parse_mappings(pointer);
}
const pointer = parse('AAAA;AACA');
assert.notEqual(pointer, 0);
api.by_generated_location(pointer);
assert.equal(callbacks.length, 2);
assert.deepEqual(callbacks.map(m => [m[0], m[1], m[4], m[5], m[6], m[7]]), [
    [0, 0, 1, 0, 0, 0], [1, 0, 1, 0, 1, 0],
]);
api.compute_column_spans(pointer);
api.free_mappings(pointer);
assert.equal(parse('!'), 0);
assert.notEqual(api.get_last_error(), 0);
const recovered = parse('AAAA');
assert.notEqual(recovered, 0);
api.free_mappings(recovered);
console.log('Source-map WASM: mapping callbacks, column spans, rejection and recovery passed');
