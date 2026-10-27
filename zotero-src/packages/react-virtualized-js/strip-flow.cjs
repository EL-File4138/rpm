const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');
const requireBuild = createRequire(path.resolve(process.argv[2], '../package.json'));
const babel = requireBuild('@babel/core');
const preset = requireBuild.resolve('@babel/preset-flow');
const source = path.resolve(process.argv[3]);
const output = path.resolve(process.argv[4]);
for (const entry of fs.readdirSync(source, { recursive: true, withFileTypes: true })) {
    if (!entry.isFile() || !entry.name.endsWith('.js')) continue;
    const filename = path.join(entry.parentPath, entry.name);
    const relative = path.relative(source, filename);
    if (/\.(jest|e2e|ssr|example)\.js$/.test(relative) || relative.startsWith('demo/')) continue;
    const result = babel.transformFileSync(filename, {
        configFile: false, babelrc: false, presets: [preset],
        parserOpts: { plugins: ['jsx'] },
    });
    const destination = path.join(output, relative);
    fs.mkdirSync(path.dirname(destination), { recursive: true });
    fs.writeFileSync(destination, result.code + '\n');
}
