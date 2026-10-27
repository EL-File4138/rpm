import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import vm from 'node:vm';

const root = resolve(process.argv[2]);
const require = createRequire(import.meta.url);
const text = await readFile(`${root}/katex.js`, 'utf8');
const global = vm.createContext({ console });
vm.runInContext(text, global);
let amd;
const define = (dependencies, factory) => { assert.deepEqual([...dependencies], []); amd = factory(); };
define.amd = true;
vm.runInNewContext(text, { console, define });
for (const api of [global.katex, amd, require(`${root}/katex.js`),
                  (await import(pathToFileURL(`${root}/katex.mjs`))).default]) {
    assert.equal(api.version, '0.16.22');
    const fraction = api.renderToString('\\frac{a}{b}', { output: 'mathml' });
    assert.match(fraction, /<mfrac>/);
    assert.match(fraction, /<mi>a<\/mi>/);
    assert.match(fraction, /<mi>b<\/mi>/);
    const html = api.renderToString('x^2 + \\sqrt{y}');
    assert.match(html, /class="katex-html"/);
    assert.match(api.renderToString('\\twice{z}', {
        output: 'mathml', macros: { '\\twice': '#1+#1' },
    }), /<mi>z<\/mi><mo>\+<\/mo><mi>z<\/mi>/);
    assert.throws(() => api.renderToString('\\frac{a}'), error => error.name === 'ParseError');
    assert.match(api.renderToString('\\frac{a}', { throwOnError: false }), /katex-error/);
    assert.doesNotMatch(api.renderToString('\\href{javascript:alert(1)}{x}', {
        trust: false, strict: false,
    }), /href="javascript:/);
    assert.match(api.renderToString('x', { output: 'mathml' }), /<mi>x<\/mi>/);
}
console.log('KaTeX: UMD/CJS/ESM exports, HTML/MathML, macros, errors and untrusted links passed');
