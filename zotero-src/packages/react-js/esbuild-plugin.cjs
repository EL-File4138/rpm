'use strict';

const {execFileSync} = require('child_process');

// Keep React's Rollup transforms and forks; use Fedora's source-built minifier.
module.exports = function esbuild(flags = {}) {
  return {
    name: 'rpm-esbuild',
    renderChunk(code) {
      const args = ['--target=es2015', '--minify-syntax', '--minify-whitespace'];
      if (flags.renaming) args.push('--minify-identifiers');
      return {
        code: execFileSync(process.env.RPM_ESBUILD || 'esbuild', args, {
          input: code,
          encoding: 'utf8',
          maxBuffer: 32 * 1024 * 1024,
        }),
        map: null,
      };
    },
  };
};
