// Compile the editor's reachable original sources without upstream's size-only tree shaking.
const fs = require('node:fs');
const path = require('node:path');
const ts = require(path.resolve(process.argv[4]));
const root = path.resolve(process.argv[2]);
const output = path.resolve(process.argv[3]);
const loader = path.resolve(process.argv[5]);
if (ts.versionMajorMinor !== '5.4') throw new Error('Expected the pinned editor build compiler');
const queue = ['vs/editor/editor.main', 'vs/editor/editor.worker', 'vs/base/worker/workerMain'];
const inputs = new Set();
const copied = new Set();
const generated = new Set();
const visited = new Set();
const dynamic = [];

function checked(id) {
    if (!id.startsWith('vs/') || id.split('/').some(part => part === '..' || part === '.')) {
        throw new Error(`Unexpected editor module: ${id}`);
    }
    return id;
}

function copy(relative) {
    checked(relative);
    if (copied.has(relative)) return;
    copied.add(relative);
    const source = path.join(root, 'src', relative);
    const target = path.join(output, relative);
    if (relative.endsWith('.ttf')) {
        if (!fs.existsSync(target) || !fs.existsSync(target.replace(/\.ttf$/, '.inputs.json'))) {
            throw new Error(`Build the font from original SVG artwork first: ${relative}`);
        }
        generated.add(relative);
        return;
    }
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.copyFileSync(source, target);
    inputs.add(`src/${relative}`);
    if (relative.endsWith('.css')) {
        for (const match of fs.readFileSync(source, 'utf8').matchAll(/url\(\s*['"]?([^\s)'"?#]+)[^)]*\)/g)) {
            if (!match[1].startsWith('data:')) copy(path.posix.normalize(path.posix.join(path.posix.dirname(relative), match[1])));
        }
    }
}

function enqueue(dependency, parent) {
    if (dependency === 'require' || dependency === 'exports' || dependency === 'module') return;
    if (dependency.startsWith('vs/css!')) {
        let asset = dependency.slice('vs/css!'.length);
        if (asset.startsWith('.')) asset = path.posix.normalize(path.posix.join(path.posix.dirname(parent), asset));
        copy(`${asset}.css`);
        queue.push('vs/css');
        return;
    }
    if (dependency.startsWith('vs/nls!')) {
        throw new Error(`Unexpected prebuilt localization dependency: ${dependency}`);
    }
    if (dependency.startsWith('.')) dependency = path.posix.normalize(path.posix.join(path.posix.dirname(parent), dependency));
    queue.push(checked(dependency));
}

while (queue.length) {
    const id = checked(queue.shift());
    if (visited.has(id)) continue;
    visited.add(id);
    const relative = `src/${id}.ts`;
    const source = path.join(root, relative);
    if (!fs.existsSync(source)) {
        if (fs.existsSync(path.join(root, `src/${id}.js`))) {
            copy(`${id}.js`);
            continue;
        }
        throw new Error(`Missing original source: ${source}`);
    }
    const result = ts.transpileModule(fs.readFileSync(source, 'utf8'), {
        fileName: source, moduleName: id, reportDiagnostics: true,
        compilerOptions: {
            module: ts.ModuleKind.AMD, target: ts.ScriptTarget.ES2022,
            experimentalDecorators: true, useDefineForClassFields: false,
            preserveConstEnums: true, removeComments: false,
        },
    });
    const errors = (result.diagnostics || []).filter(d => d.category === ts.DiagnosticCategory.Error);
    if (errors.length) throw new Error(ts.formatDiagnosticsWithColorAndContext(errors, {
        getCanonicalFileName: f => f, getCurrentDirectory: () => root, getNewLine: () => '\n',
    }));
    inputs.add(relative);
    const target = path.join(output, `${id}.js`);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, result.outputText);
    const emitted = ts.createSourceFile(target, result.outputText, ts.ScriptTarget.Latest, true, ts.ScriptKind.JS);
    function visit(node) {
        if (ts.isCallExpression(node) && ts.isIdentifier(node.expression) && ['define', 'require'].includes(node.expression.text)) {
            for (const argument of node.arguments) {
                if (ts.isArrayLiteralExpression(argument)) {
                    for (const element of argument.elements) {
                        if (!ts.isStringLiteral(element)) {
                            if (node.expression.text === 'define') throw new Error(`Nonliteral module declaration in ${id}`);
                            dynamic.push({ module: id, expression: element.getText(emitted) });
                            continue;
                        }
                        enqueue(element.text, id);
                    }
                }
            }
        }
        ts.forEachChild(node, visit);
    }
    visit(emitted);
}
const loaderConfig = path.join(loader, 'src/core/tsconfig.json');
const loaderSettings = ts.readConfigFile(loaderConfig, ts.sys.readFile);
if (loaderSettings.error) throw new Error(loaderSettings.error.messageText);
const parsed = ts.parseJsonConfigFileContent(loaderSettings.config, ts.sys, path.dirname(loaderConfig));
const loaderProgram = ts.createProgram(parsed.fileNames, {
    ...parsed.options, outFile: path.join(output, 'vs/loader.js'), declaration: false,
});
const diagnostics = [...parsed.errors, ...ts.getPreEmitDiagnostics(loaderProgram)];
if (diagnostics.length) throw new Error(ts.formatDiagnosticsWithColorAndContext(diagnostics, {
    getCanonicalFileName: f => f, getCurrentDirectory: () => loader, getNewLine: () => '\n',
}));
if (loaderProgram.emit().emitSkipped) throw new Error('Loader source compilation failed');
const printer = ts.createPrinter({ removeComments: true });
function normalized(filename) {
    return printer.printFile(ts.createSourceFile(filename, fs.readFileSync(filename, 'utf8'), ts.ScriptTarget.Latest, true));
}
if (normalized(path.join(output, 'vs/loader.js')) !== normalized(path.join(root, 'src/vs/loader.js'))) {
    throw new Error('Source-built loader differs from the pinned editor loader beyond comments/formatting');
}
fs.writeFileSync(path.join(output, 'core-source-inputs.json'), JSON.stringify({
    inputs: [...inputs].sort(), dynamicImports: dynamic,
    loaderInputs: parsed.fileNames.map(filename => path.relative(loader, filename)).sort(),
    generatedResources: [...generated].sort(),
}, null, 2) + '\n');
console.log(`Compiled ${visited.size} editor modules from original sources; copied ${copied.size} resources`);
