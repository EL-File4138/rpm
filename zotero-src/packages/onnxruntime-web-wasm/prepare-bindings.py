#!/usr/bin/python3
"""Adapt the generated browser loader and validate the compiled bindings."""

import argparse
import json
from pathlib import Path


def prepare(root):
    loader = 'ort-wasm-simd-threaded.mjs'
    text = (root / 'wasm-build' / loader).read_text()
    environment = 'globalThis.process?.versions?.node&&globalThis.process?.type!="renderer"'
    for name in ('ENVIRONMENT_IS_NODE', 'isNode'):
        declaration = f'var {name}={environment};'
        if text.count(declaration) != 1:
            raise ValueError(f'Unexpected Emscripten environment guard: {name}')
        text = text.replace(declaration, '')
    marker = 'export default ortWasmThreaded;'
    if text.count(marker) != 1:
        raise ValueError('Unexpected Emscripten module export')
    implementation, bootstrap = text.split(marker)
    # require() cannot consume an async ESM module. The factory already exposes
    # readiness; retain the pthread bootstrap inside an async function instead.
    destination = root / 'js/web/dist'
    destination.mkdir(exist_ok=True)
    (destination / loader).write_text(
        implementation + marker + '\nvoid (async () => {' + bootstrap + '})();\n')


def check(root):
    output = root / 'wasm-build'
    metadata = json.loads((output / 'bindings-inputs.json').read_text())
    for name in metadata['inputs']:
        if not name.startswith(('js/common/lib/', 'js/web/lib/')) and name != 'js/web/dist/ort-wasm-simd-threaded.mjs':
            raise ValueError(f'Unexpected bundled dependency: {name}')
    if 'BUILD_DEFS' in (output / 'ort.wasm.mjs').read_text():
        raise ValueError('Unresolved ONNX build definitions')
    for artifact in metadata['outputs'].values():
        for dependency in artifact['imports']:
            if dependency['path'] not in ('node:fs/promises', 'node:fs', 'node:os'):
                raise ValueError(f'Unexpected browser bundle import: {dependency}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'check'))
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    globals()[args.action](args.root.resolve())
