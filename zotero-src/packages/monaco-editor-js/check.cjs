const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { fileURLToPath, pathToFileURL } = require('node:url');

const root = path.resolve(process.argv[2]);
const registrations = new Map();
const modules = new Map();
const context = vm.createContext({ console, setTimeout, clearTimeout, URL, TextEncoder, TextDecoder,
    navigator: { userAgent: 'Mozilla/5.0 Linux', language: 'en-US' } });
context.define = (id, dependencies, factory) => {
    assert.equal(typeof id, 'string');
    assert(!registrations.has(id), `Duplicate AMD registration: ${id}`);
    registrations.set(id, { dependencies, factory });
};
function load(id, parent = '') {
    if (id.startsWith('.')) id = path.posix.normalize(path.posix.join(path.posix.dirname(parent), id));
    if (modules.has(id)) return modules.get(id);
    assert(id.startsWith('vs/') && !id.includes('..'), `Unexpected module: ${id}`);
    if (!registrations.has(id)) vm.runInContext(fs.readFileSync(path.join(root, `${id}.js`), 'utf8'), context, { filename: id });
    const registration = registrations.get(id);
    assert(registration, `No AMD registration: ${id}`);
    const exports = {};
    modules.set(id, exports);
    const require = (dependency, callback) => {
        if (Array.isArray(dependency)) {
            const values = dependency.map(name => load(name, id));
            if (callback) callback(...values);
            return;
        }
        return load(dependency, id);
    };
    const result = registration.factory(...registration.dependencies.map(name =>
        name === 'require' ? require : name === 'exports' ? exports : load(name, id)));
    if (result !== undefined) modules.set(id, result);
    return modules.get(id);
}

async function check() {
    const { URI } = load('vs/base/common/uri');
    const { Position } = load('vs/editor/common/core/position');
    const { Range } = load('vs/editor/common/core/range');
    assert.equal(URI.parse('https://example.org/a%20b').path, '/a b');
    assert.equal(URI.file('/tmp/source test.js').toString(), 'file:///tmp/source%20test.js');
    assert(new Range(1, 1, 3, 4).containsPosition(new Position(2, 2)));
    assert(!new Range(1, 1, 3, 4).containsPosition(new Position(4, 1)));
    modules.set('vs/editor/editor.api', { Uri: URI });
    const typescript = load('vs/language/typescript/tsWorker');
    let text = 'const answer: number = "wrong";\nanswer;';
    let version = 1;
    const uri = URI.parse('file:///source-test.ts');
    const worker = typescript.create({
        getMirrorModels: () => [{ uri, version, getValue: () => text }],
    }, { compilerOptions: { target: 99, strict: true }, extraLibs: {} });
    assert((await worker.getSemanticDiagnostics(uri.toString())).some(d => d.code === 2322));
    assert.equal((await worker.getSyntacticDiagnostics(uri.toString())).length, 0);
    const info = await worker.getQuickInfoAtPosition(uri.toString(), text.indexOf('answer'));
    assert(info.displayParts.map(p => p.text).join('').includes('answer: number'));
    text = 'const = ;';
    version++;
    assert((await worker.getSyntacticDiagnostics(uri.toString())).length > 0);
    function mirror(filename, value) {
        const uri = URI.parse(`file:///${filename}`);
        return { uri, context: { getMirrorModels: () => [{ uri, version: 1, getValue: () => value }] } };
    }
    const defaultModel = mirror('default.ts', 'const values: Array<number> = [1, 2];\nvalues.push("wrong");');
    const defaultWorker = typescript.create(defaultModel.context, { compilerOptions: { strict: true }, extraLibs: {} });
    assert.equal((await defaultWorker.getCompilerOptionsDiagnostics(defaultModel.uri.toString())).length, 0);
    const defaultDiagnostics = await defaultWorker.getSemanticDiagnostics(defaultModel.uri.toString());
    assert(!defaultDiagnostics.some(d => d.code === 2304), 'Default library must define Array');
    assert(defaultDiagnostics.some(d => d.code === 2345), 'Default library must type-check Array.push');
    const cssModel = mirror('test.css', 'body { colr: red; }');
    const css = load('vs/language/css/cssWorker').create(cssModel.context, { languageId: 'css', options: {} });
    assert((await css.doValidation(cssModel.uri.toString())).some(d => d.code === 'unknownProperties'));
    assert.deepEqual(Array.from(await css.doValidation('file:///missing.css')), []);
    const htmlModel = mirror('test.html', '<di');
    const html = load('vs/language/html/htmlWorker').create(htmlModel.context, { languageId: 'html', languageSettings: {} });
    assert((await html.doComplete(htmlModel.uri.toString(), { line: 0, character: 3 })).items.some(item => item.label === 'div'));
    const jsonModel = mirror('test.json', '{"answer": }');
    const json = load('vs/language/json/jsonWorker').create(jsonModel.context, {
        languageId: 'json', languageSettings: { validate: true }, enableSchemaRequest: false,
    });
    assert((await json.doValidation(jsonModel.uri.toString())).length > 0);
    assert.deepEqual(Array.from(await json.doValidation('file:///missing.json')), []);
    const loaderContext = vm.createContext({ console, setTimeout, clearTimeout, origin: 'https://example.invalid',
        navigator: { userAgent: 'Mozilla/5.0 Linux', language: 'en-US' } });
    loaderContext.self = loaderContext;
    loaderContext.importScripts = (...urls) => {
        for (const url of urls) {
            const filename = fileURLToPath(url);
            assert(filename.startsWith(root + path.sep), 'Loader requested a file outside the build');
            vm.runInContext(fs.readFileSync(filename, 'utf8'), loaderContext, { filename });
        }
    };
    vm.runInContext(fs.readFileSync(path.join(root, 'vs/loader.js'), 'utf8'), loaderContext);
    loaderContext.require.config({ baseUrl: pathToFileURL(root + path.sep).href });
    const [loadedUri, loadedRange] = await new Promise((resolve, reject) => {
        loaderContext.require(['vs/base/common/uri', 'vs/editor/common/core/range'], (...values) => resolve(values), reject);
    });
    assert.equal(loadedUri.URI.parse('file:///source.js').path, '/source.js');
    assert(new loadedRange.Range(1, 1, 3, 4).containsPosition({ lineNumber: 2, column: 2 }));
    console.log('Monaco: AMD modules, URI/range behavior and TypeScript/CSS/HTML/JSON workers passed');
}
check().catch(error => { console.error(error); process.exitCode = 1; });
