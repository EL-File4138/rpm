const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');

const [icons, staging, output, dependencies, codepointFile] = process.argv.slice(2).map(p => path.resolve(p));
const tools = createRequire(path.join(dependencies, 'package.json'));
if (tools('svgo/package.json').version !== '2.7.0' || tools('fantasticon/package.json').version !== '1.2.3') {
    throw new Error('Unexpected upstream font tool versions');
}
const config = require(path.join(icons, 'svgo.config.js'));
const { optimize } = tools('svgo');
for (const filename of fs.readdirSync(staging).filter(p => p.endsWith('.svg'))) {
    const source = path.join(staging, filename);
    const result = optimize(fs.readFileSync(source, 'utf8'), { ...config, path: source });
    if (result.error) throw new Error(result.error);
    fs.writeFileSync(source, result.data);
}
const upstream = require(path.join(icons, '.fantasticonrc.js'));
tools('fantasticon').generateFonts({
    ...upstream, inputDir: staging, outputDir: output, assetTypes: [], fontTypes: ['ttf'],
    codepoints: JSON.parse(fs.readFileSync(codepointFile, 'utf8')),
}).catch(error => { console.error(error); process.exitCode = 1; });
