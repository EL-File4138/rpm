import assert from 'node:assert/strict';
import { validateStyle } from './csl-validator.mjs';

const validStyle = `<?xml version="1.0" encoding="utf-8"?>
<style xmlns="http://purl.org/net/xbiblio/csl" version="1.0" class="in-text">
  <info>
    <title>Package validation fixture</title>
    <id>http://www.zotero.org/styles/package-validation</id>
    <updated>2026-09-27T00:00:00+00:00</updated>
  </info>
  <citation><layout><text variable="title"/></layout></citation>
</style>`;

assert.equal(await validateStyle(validStyle), '');
assert.notEqual(await validateStyle('<style/>'), '');
// rnv returns a failure status for the deliberately invalid style above.
// Emscripten propagates it to Node even though the wrapper returns diagnostics.
process.exitCode = 0;
