#!/usr/bin/python3
"""Build Ace's browser modules from the pinned release sources."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess


def build(root, dependencies, esbuild):
    modules = root / 'node_modules'
    modules.mkdir(exist_ok=True)
    for package in dependencies.iterdir():
        destination = modules / package.name
        if not destination.exists():
            destination.symlink_to(package, target_is_directory=True)
    environment = os.environ | {'NODE_OPTIONS': '--max-old-space-size=1400',
                                'UV_THREADPOOL_SIZE': '1', 'GOMAXPROCS': '1'}
    # The upstream Ace archive embeds a pre-relicensing JSHint bundle.
    # Rebuild its AMD module from the MIT-licensed JSHint source instead.
    # Gecko workers provide console; the legacy browser shim pulls in Node APIs.
    console_module = root / 'rpm-console.cjs'
    console_module.write_text('module.exports = globalThis.console;\n')
    subprocess.run([
        esbuild, str(dependencies / 'jshint/src/jshint.js'), '--bundle',
        '--platform=browser', '--format=cjs', '--target=es2015',
        '--define:define=undefined',
        f'--alias:console-browserify={console_module}',
        '--banner:js=define(function(require, exports, module) {', '--footer:js=});',
        '--metafile=rpm-jshint-inputs.json',
        '--outfile=lib/ace/mode/javascript/jshint.js',
    ], cwd=root, env=environment, check=True)
    graph = json.loads((root / 'rpm-jshint-inputs.json').read_text())
    if any(output['imports'] for output in graph['outputs'].values()):
        raise ValueError('JSHint contains unresolved imports')
    licenses = root / 'rpm-licenses'
    licenses.mkdir(exist_ok=True)
    for package in ('jshint', 'lodash', 'events'):
        shutil.copyfile(dependencies / package / 'LICENSE', licenses / f'{package}-LICENSE')
    subprocess.run(['node', 'Makefile.dryice.js', 'minimal'], cwd=root,
                   env=environment, check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('dependencies', type=Path)
    parser.add_argument('--esbuild', default='esbuild')
    args = parser.parse_args()
    build(args.root.resolve(), args.dependencies.resolve(), args.esbuild)
