import assert from 'node:assert/strict';
import { readFile, mkdtemp, writeFile, rm } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import vm from 'node:vm';
import { tmpdir } from 'node:os';

const root = resolve(process.argv[2]);
const require = createRequire(import.meta.url);
for (const core of [
    await import(pathToFileURL(`${root}/core/index.mjs`)),
    require(`${root}/core/index.js`),
]) {
    class LocalCopilot extends core.Copilot {
        getDefaultPrompt(metadata) { return { prompt: metadata.text }; }
        complete(metadata, options) { return this.makeAIRequest(metadata, options); }
    }
    assert.throws(() => new LocalCopilot(undefined, { model: 'codestral' }), /API key/);
    assert.throws(() => new LocalCopilot(undefined, {
        model: () => ({}), provider: 'mistral',
    }), /Provider should not be specified/);
    const copilot = new LocalCopilot(undefined, {
        model: async ({ prompt }) => ({ text: prompt.toUpperCase() }),
    });
    assert.deepEqual(await copilot.complete({ text: 'local completion' }), {
        text: 'LOCAL COMPLETION',
    });
    assert.deepEqual(await copilot.complete({ text: 'default' }, {
        customPrompt: () => ({ prompt: 'override' }),
    }), { text: 'OVERRIDE' });
}
const context = vm.createContext({ console });
vm.runInContext(await readFile(`${root}/monacopilot/index.global.js`, 'utf8'), context);
assert.equal(typeof context.monacopilot.registerCompletion, 'function');
assert.equal(typeof context.monacopilot.CompletionCopilot, 'function');
const temporary = await mkdtemp(`${tmpdir()}/monacopilot-check-`);
try {
    const source = await readFile(`${root}/monacopilot/index.mjs`, 'utf8');
    const patched = source.replace(/from\s*['"]@monacopilot\/core['"]/g,
        `from ${JSON.stringify(pathToFileURL(`${root}/core/index.mjs`).href)}`);
    assert.notEqual(patched, source, 'ESM consumer must retain the separate core import');
    await writeFile(`${temporary}/index.mjs`, patched);
    for (const exports of [
        await import(pathToFileURL(`${temporary}/index.mjs`)),
        require(`${root}/monacopilot/index.js`),
    ]) {
        assert.equal(typeof exports.registerCompletion, 'function');
        assert.equal(typeof exports.CompletionCopilot, 'function');
    }
} finally {
    await rm(temporary, { recursive: true, force: true });
}
console.log('Monacopilot: local completion, validation, CJS/ESM and browser exports passed');
