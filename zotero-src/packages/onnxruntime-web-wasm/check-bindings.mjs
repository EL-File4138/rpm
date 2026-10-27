import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const directory = resolve(process.argv[2]);
const ort = await import(pathToFileURL(`${directory}/ort.wasm.mjs`).href);
ort.env.wasm.numThreads = 1;
ort.env.wasm.proxy = false;
// Match Zotero's worker: bytes come from its data provider and the loader is
// embedded in the JavaScript bundle, without an external module URL.
ort.env.wasm.wasmBinary = await readFile(`${directory}/ort-wasm-simd-threaded.wasm`);
ort.env.wasm.wasmPaths = undefined;
await assert.rejects(ort.InferenceSession.create(new Uint8Array([1, 2, 3]), {
    executionProviders: ['wasm'],
}));
const model = await readFile(process.argv[3]);
const session = await ort.InferenceSession.create(model, { executionProviders: ['wasm'] });
const values = new Float32Array([1.25, -2.5]);
const input = new ort.Tensor('float32', values, [2]);
try {
    const results = await session.run({ [session.inputNames[0]]: input });
    const result = results[session.outputNames[0]];
    assert.deepEqual(result.dims, [2]);
    assert.deepEqual(Array.from(result.data), Array.from(values));
    result.dispose();
} finally {
    input.dispose();
    await session.release();
}
console.log('ONNX JavaScript API: invalid-model rejection and identity inference passed');
