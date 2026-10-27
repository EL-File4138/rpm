const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { resolve } = require('node:path');
const vm = require('node:vm');

const filename = resolve(process.argv[2], 'typescript.js');
assert.match(readFileSync(resolve(process.argv[2], 'lib.es5.d.ts'), 'utf8'), /interface Array<T>/);
const browser = vm.createContext({ console });
vm.runInContext(readFileSync(filename, 'utf8'), browser);
for (const ts of [require(filename), browser.ts]) {
    assert.equal(ts.version, '5.0.2');
    const result = ts.transpileModule('const answer: number = 42;', {
        compilerOptions: { target: ts.ScriptTarget.ES2018 },
    });
    assert.match(result.outputText, /const answer = 42/);
    const source = ts.createSourceFile('test.ts', 'const = ;', ts.ScriptTarget.Latest, true);
    assert.ok(source.parseDiagnostics.length > 0);
    const files = { 'test.ts': 'const answer: number = "wrong";' };
    const host = {
        getScriptFileNames: () => Object.keys(files),
        getScriptVersion: () => '1',
        getScriptSnapshot: name => files[name] ? ts.ScriptSnapshot.fromString(files[name]) : undefined,
        getCurrentDirectory: () => '',
        getCompilationSettings: () => ({ noLib: true }),
        getDefaultLibFileName: () => 'lib.d.ts',
        fileExists: name => name in files,
        readFile: name => files[name],
    };
    const service = ts.createLanguageService(host);
    assert.ok(service.getSemanticDiagnostics('test.ts').some(error => error.code === 2322));
    assert.match(service.getQuickInfoAtPosition('test.ts', 8).displayParts.map(part => part.text).join(''), /answer: number/);
    service.dispose();
}
console.log('TypeScript: CommonJS/browser exports, transpilation, parsing and language service passed');
