import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const root = path.resolve(process.argv[2] || 'dist');
// The generated glue targets browsers. Supply its browser globals and WASM
// bytes explicitly so the test performs no network requests.
const errors = [];
globalThis.window = {
  location: { href: 'http://localhost/' },
  console: { ...console, error: message => errors.push(message) },
  alert: message => errors.push(message),
  JSON,
};

async function loadEmscripten(directory, filename, wasm) {
  const { default: factory } = await import(pathToFileURL(path.join(root, directory, filename)));
  return factory(wasm ? { wasmBinary: await readFile(path.join(root, directory, wasm)) } : {});
}

for (const [js, wasm] of [
  ['openjpeg.js', 'openjpeg.wasm'],
  ['openjpeg_nowasm_fallback.js', null],
]) {
  const codec = await loadEmscripten('openjpeg', js, wasm);
  const data = codec._malloc(16);
  try {
    codec.writeArrayToMemory(new Uint8Array(16), data);
    assert.equal(codec._jp2_decode(data, 16, 3, 0, 0, 0), 1);
    assert.match(codec.errorMessages, /Unknown format/);
  } finally {
    codec._free(data);
  }
}

for (const [js, wasm] of [
  ['jbig2.js', 'jbig2.wasm'],
  ['jbig2_nowasm_fallback.js', null],
]) {
  const codec = await loadEmscripten('jbig2', js, wasm);
  const data = codec._malloc(1);
  try {
    // CCITT Group 3 terminating code 10011 encodes a white run of 8 pixels.
    codec.writeArrayToMemory(new Uint8Array([0x98]), data);
    codec._ccitt_decode(data, 1, 8, 1, 0, 0, 0, 0, 8, 1);
    assert.deepEqual(Array.from(codec.imageData), [255]);
  } finally {
    codec._free(data);
  }
}

const sandbox = await loadEmscripten('quickjs', 'quickjs-eval.js', 'quickjs-eval.wasm');
assert.equal(sandbox.ccall('init', 'number', ['string', 'number'], [
  '(name, value) => { if (name !== "sum" || value.a + value.b !== 42) throw new Error("bad result"); }', 0,
]), 1);
sandbox.ccall('commFun', null, ['string', 'string'], ['sum', '{"a":19,"b":23}']);
assert.deepEqual(errors, []);
sandbox.ccall('evalInSandbox', null, ['string', 'number'], ['throw new Error("expected failure")', 0]);
assert.equal(errors.length, 1);
assert.match(errors[0], /expected failure/);
sandbox._nukeSandbox();

const qcms = await import(pathToFileURL(path.join(root, 'qcms/qcms.js')));
const qcmsModule = qcms.initSync({ module: await readFile(path.join(root, 'qcms/qcms_bg.wasm')) });
assert.equal(qcms.qcms_transformer_from_memory(new Uint8Array(16), qcms.DataType.RGB8, qcms.Intent.Perceptual), 0);
// A minimal ICC v2 grayscale profile with an identity tone curve. Construct
// the fixture from fields so no external profile or generated binary is needed.
const profile = Buffer.alloc(156);
profile.writeUInt32BE(profile.length, 0);
profile.writeUInt32BE(0x02100000, 8);
profile.write('mntr', 12);
profile.write('GRAY', 16);
profile.write('XYZ ', 20);
profile.write('acsp', 36);
profile.writeUInt32BE(1, 128);
profile.write('kTRC', 132);
profile.writeUInt32BE(144, 136);
profile.writeUInt32BE(12, 140);
profile.write('curv', 144);
const transform = qcms.qcms_transformer_from_memory(profile, qcms.DataType.Gray8, qcms.Intent.Perceptual);
assert.notEqual(transform, 0);
const { QCMS } = await import(pathToFileURL(path.join(root, 'qcms/qcms_utils.js')));
QCMS._memory = qcmsModule.memory;
QCMS._makeHexColor = (r, g, b) => `#${[r, g, b].map(c => c.toString(16).padStart(2, '0')).join('')}`;
try {
  qcms.qcms_convert_one(transform, 0, true);
  assert.equal(QCMS._cssColor, '#000000');
  QCMS._destBuffer = new Uint8Array(3);
  qcms.qcms_convert_one(transform, 255, false);
  assert.deepEqual(Array.from(QCMS._destBuffer), [255, 255, 255]);
  QCMS._mustAddAlpha = true;
  QCMS._destBuffer = new Uint8Array(8);
  QCMS._destLength = 8;
  qcms.qcms_convert_array(transform, new Uint8Array([0, 255]));
  assert.deepEqual(Array.from(QCMS._destBuffer), [0, 0, 0, 255, 255, 255, 255, 255]);
} finally {
  qcms.qcms_drop_transformer(transform);
}
console.log('PDF.js codec loading, fax decoding, sandbox, color callbacks and invalid-input checks passed');
