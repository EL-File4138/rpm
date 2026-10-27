const { readFileSync, writeFileSync } = require('node:fs');
const { resolve } = require('node:path');
const { createRequire } = require('node:module');

const root = resolve(process.argv[2]);
const dependencies = createRequire(resolve(process.argv[3], 'package.json'));
const peg = dependencies('pegjs');
const source = peg.generate(readFileSync(`${root}/src/parser.pegjs`, 'utf8'), {
    output: 'source', format: 'commonjs',
});
// Grammar actions use these enums from the original TypeScript source.
writeFileSync(`${root}/src/parser.ts`,
    "import { TYPE, SKELETON_TYPE } from './types';\n"
    + source.replace('module.exports = {', 'const generatedParser = {')
    + '\nexport const pegParse = generatedParser.parse;\n'
    + 'export const SyntaxError = generatedParser.SyntaxError;\n');
