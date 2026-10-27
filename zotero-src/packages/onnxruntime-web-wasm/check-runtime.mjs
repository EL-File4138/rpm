import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const directory = resolve(process.argv[2]);
const { default: createRuntime } = await import(pathToFileURL(`${directory}/ort-wasm-simd-threaded.mjs`));
const runtime = await createRuntime({
  numThreads: 1,
  wasmBinary: await readFile(`${directory}/ort-wasm-simd-threaded.wasm`),
});
const allocations = [];
function allocate(bytes) {
  const pointer = runtime._malloc(bytes.length);
  assert.notEqual(pointer, 0);
  allocations.push(pointer);
  runtime.HEAPU8.set(bytes, pointer);
  return pointer;
}
function words(values) {
  return allocate(new Uint8Array(Uint32Array.from(values).buffer));
}
function string(value) {
  return allocate(new TextEncoder().encode(`${value}\0`));
}

assert.equal(runtime._OrtInit(1, 3), 0);
const options = runtime._OrtCreateSessionOptions(0, 1, 1, 0, 0, 0, 0, 3, 0, 0);
assert.notEqual(options, 0);
let session = 0;
let input = 0;
let output = 0;
try {
  const invalid = allocate(Uint8Array.of(255, 255, 255));
  assert.equal(runtime._OrtCreateSession(invalid, 3, options), 0);
  const model = await readFile(process.argv[3]);
  session = runtime._OrtCreateSession(allocate(model), model.length, options);
  assert.notEqual(session, 0, 'Source-built runtime must load the generated ONNX model');
  const data = allocate(new Uint8Array(Float32Array.of(19, 23).buffer));
  input = runtime._OrtCreateTensor(1, data, 8, words([2]), 1, 1);
  assert.notEqual(input, 0);
  const outputs = words([0]);
  assert.equal(runtime._OrtRun(session, words([string('x')]), words([input]), 1,
    words([string('y')]), 1, outputs, 0), 0);
  output = runtime.HEAPU32[outputs / 4];
  assert.notEqual(output, 0);
  const info = words([0, 0, 0, 0]);
  assert.equal(runtime._OrtGetTensorData(output, info, info + 4, info + 8, info + 12), 0);
  assert.equal(runtime.HEAPU32[info / 4], 1);
  const values = runtime.HEAPU32[(info + 4) / 4];
  assert.deepEqual(Array.from(new Float32Array(runtime.HEAPU8.buffer, values, 2)), [19, 23]);
  assert.equal(runtime.HEAPU32[(info + 12) / 4], 1);
  const dimensions = runtime.HEAPU32[(info + 8) / 4];
  assert.equal(runtime.HEAPU32[dimensions / 4], 2);
  runtime._OrtFree(dimensions);
} finally {
  if (output) runtime._OrtReleaseTensor(output);
  if (input) runtime._OrtReleaseTensor(input);
  if (session) runtime._OrtReleaseSession(session);
  runtime._OrtReleaseSessionOptions(options);
  for (const pointer of allocations) runtime._free(pointer);
}
console.log('ONNX model loading, inference and invalid-model checks passed');
