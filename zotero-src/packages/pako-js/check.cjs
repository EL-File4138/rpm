const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const zlib = require('node:zlib');

const source = fs.readFileSync(path.join(process.argv[2], 'pako.min.js'), 'utf8');
for (const variant of ['global', 'commonjs', 'amd']) {
    const context = vm.createContext({ TextEncoder, TextDecoder });
    let pako;
    if (variant === 'commonjs') context.module = { exports: {} };
    if (variant === 'amd') {
        context.define = (dependencies, factory) => { assert.equal(dependencies.length, 0); pako = factory(); };
        context.define.amd = true;
    }
    vm.runInContext(source, context);
    pako ??= variant === 'commonjs' ? context.module.exports : context.pako;
    const input = Buffer.from('Compression round-trip: café 数据\n'.repeat(300));
    for (const [compress, decompress, nativeCompress, nativeDecompress] of [
        ['deflate', 'inflate', zlib.deflateSync, zlib.inflateSync],
        ['deflateRaw', 'inflateRaw', zlib.deflateRawSync, zlib.inflateRawSync],
        ['gzip', 'ungzip', zlib.gzipSync, zlib.gunzipSync],
    ]) {
        assert.deepEqual(nativeDecompress(pako[compress](input)), input);
        assert.deepEqual(Buffer.from(pako[decompress](nativeCompress(input))), input);
    }
    const compressor = new pako.Deflate();
    compressor.push(input.subarray(0, 200), false);
    compressor.push(input.subarray(200), true);
    assert.equal(compressor.err, 0);
    const inflater = new pako.Inflate();
    inflater.push(compressor.result.subarray(0, 5), false);
    inflater.push(compressor.result.subarray(5), true);
    assert.equal(inflater.err, 0);
    assert.deepEqual(Buffer.from(inflater.result), input);
    assert.throws(() => pako.inflate(Buffer.from('invalid stream')));
}
console.log('Pako: global/CJS/AMD exports, native interoperability, streaming and invalid input passed');
