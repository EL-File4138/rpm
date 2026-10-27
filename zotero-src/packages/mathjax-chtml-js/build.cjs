const fs = require('node:fs');
const path = require('node:path');

const [root, chemistry, compilerPath] = process.argv.slice(2).map(value => path.resolve(value));
const ts = require(compilerPath);
if (ts.version !== '5.0.2') throw new Error('Unexpected TypeScript compiler');
if (JSON.parse(fs.readFileSync(path.join(root, 'package.json'))).version !== '3.2.2' ||
    JSON.parse(fs.readFileSync(path.join(chemistry, 'package.json'))).version !== '4.2.1') {
    throw new Error('Unexpected source version');
}
const output = path.join(root, 'rpm-dist');
fs.mkdirSync(output, { recursive: true });
const config = ts.readConfigFile(path.join(root, 'tsconfig.json'), ts.sys.readFile);
if (config.error) throw new Error(ts.flattenDiagnosticMessageText(config.error.messageText, '\n'));
const parsed = ts.parseJsonConfigFileContent(config.config, ts.sys, root);
if (parsed.errors.length) throw new Error('Invalid upstream compiler configuration');
const options = { ...parsed.options, declaration: false, sourceMap: false };
function compile(source) {
    const result = ts.transpileModule(fs.readFileSync(source, 'utf8'), {
        compilerOptions: options, fileName: source, reportDiagnostics: true,
    });
    if (result.diagnostics.some(item => item.category === ts.DiagnosticCategory.Error)) {
        throw new Error(`Failed to compile ${source}`);
    }
    return result.outputText;
}
const queue = ['handlers/html', 'mathjax', 'input/tex', 'input/tex/AllPackages',
    'handlers/html/HTMLDocument', 'output/chtml', 'adaptors/HTMLAdaptor', 'adaptors/liteAdaptor'];
const seen = new Set();
while (queue.length) {
    const name = queue.shift();
    if (seen.has(name)) continue;
    if (name.startsWith('/') || name.split('/').includes('..')) throw new Error('Unsafe module path');
    seen.add(name);
    const source = path.join(root, 'ts', `${name}.ts`);
    const text = compile(source);
    const filename = path.join(output, 'js', `${name}.js`);
    fs.mkdirSync(path.dirname(filename), { recursive: true });
    fs.writeFileSync(filename, text);
    const tree = ts.createSourceFile(filename, text, ts.ScriptTarget.Latest, true);
    function visit(node) {
        if (ts.isCallExpression(node) && ts.isIdentifier(node.expression) && node.expression.text === 'require') {
            if (node.arguments.length !== 1 || !ts.isStringLiteral(node.arguments[0])) {
                throw new Error(`Dynamic import in ${name}`);
            }
            const dependency = node.arguments[0].text;
            if (dependency.startsWith('.')) {
                queue.push(path.posix.normalize(path.posix.join(path.posix.dirname(name), dependency))
                    .replace(/\.js$/, ''));
            } else if (!['mhchemparser', 'mhchemparser/dist/mhchemParser.js'].includes(dependency)) {
                throw new Error(`Unexpected external module: ${dependency}`);
            }
        }
        ts.forEachChild(node, visit);
    }
    visit(tree);
}
const chemistryOutput = path.join(output, 'node_modules/mhchemparser/dist');
fs.mkdirSync(chemistryOutput, { recursive: true });
fs.writeFileSync(path.join(chemistryOutput, 'mhchemParser.js'),
    compile(path.join(chemistry, 'src/mhchemParser.ts')));
fs.writeFileSync(path.join(chemistryOutput, '../package.json'), JSON.stringify({
    name: 'mhchemparser', version: '4.2.1', main: 'dist/mhchemParser.js', license: 'Apache-2.0',
}) + '\n');
fs.writeFileSync(path.join(root, 'rpm-source-inputs.json'), JSON.stringify({
    mathjax: [...seen].sort().map(name => `ts/${name}.ts`), chemistry: ['src/mhchemParser.ts'],
}, null, 2) + '\n');
console.log(`Compiled ${seen.size} original MathJax modules and the chemistry parser`);
