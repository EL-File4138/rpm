"""Check structured preparation retained outside the spec's compiler commands."""

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load(name, component, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'packages' / component / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bindings = load('bindings', 'onnxruntime-web-wasm', 'prepare-bindings.py')
extension = load('extension', 'zotero-libreoffice-integration', 'prepare-extension.py')


class ComponentPreparationTest(unittest.TestCase):
    def test_openjpeg_disables_relaxed_simd_in_both_build_stages(self):
        prep = (ROOT / 'spec/components-prep.inc').read_text()
        command = next(line for line in prep.splitlines()
                       if line.startswith('sed ') and '-mno-relaxed-simd' in line)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            wrapper = root / 'openjpeg-wrapper'
            wrapper.mkdir()
            for name in ('compile.sh', 'compile_lib.sh'):
                (wrapper / name).write_text('CFLAGS="-O3 -msimd128 -msse -mrelaxed-simd"\n')
            subprocess.run(['sh', '-ec', command], cwd=root, check=True)
            for script in wrapper.iterdir():
                self.assertIn('-msimd128 -msse -mno-relaxed-simd', script.read_text())
                self.assertNotIn(' -mrelaxed-simd', script.read_text())

    def test_loader_preserves_bootstrap_without_node_guards(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'wasm-build').mkdir()
            (root / 'js/web').mkdir(parents=True)
            environment = 'globalThis.process?.versions?.node&&globalThis.process?.type!="renderer"'
            text = ''.join(f'var {name}={environment};' for name in ('ENVIRONMENT_IS_NODE', 'isNode'))
            text += 'function ortWasmThreaded(){}export default ortWasmThreaded;await bootstrap();'
            (root / 'wasm-build/ort-wasm-simd-threaded.mjs').write_text(text)
            bindings.prepare(root)
            result = (root / 'js/web/dist/ort-wasm-simd-threaded.mjs').read_text()
            self.assertNotIn(environment, result)
            self.assertIn('void (async () => {await bootstrap();})();', result)
            (root / 'wasm-build/ort-wasm-simd-threaded.mjs').write_text('unexpected')
            with self.assertRaises(ValueError):
                bindings.prepare(root)

    def test_bundle_rejects_unexpected_inputs_and_imports(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / 'wasm-build'
            output.mkdir()
            (output / 'ort.wasm.mjs').write_text('export {};')
            metadata = {'inputs': {'js/common/lib/index.ts': {}}, 'outputs': {'bundle': {'imports': []}}}
            path = output / 'bindings-inputs.json'
            path.write_text(json.dumps(metadata))
            bindings.check(root)
            metadata['inputs']['node_modules/unexpected.js'] = {}
            path.write_text(json.dumps(metadata))
            with self.assertRaises(ValueError):
                bindings.check(root)
            del metadata['inputs']['node_modules/unexpected.js']
            metadata['outputs']['bundle']['imports'] = [{'path': 'unexpected'}]
            path.write_text(json.dumps(metadata))
            with self.assertRaises(ValueError):
                bindings.check(root)

    def test_extension_prepares_sources_resources_and_system_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'build/source/org/example'
            source.mkdir(parents=True)
            (source / 'Example.java').write_text('class Example {}')
            (source / 'resource.txt').write_bytes(b'unchanged resource')
            # Run in a child-like cwd without invoking a compiler.
            with patch.object(extension, 'Path', side_effect=lambda path: root / path):
                extension.prepare()
            self.assertIn('Example.java', (root / 'build/java-sources.list').read_text())
            self.assertEqual((root / 'build/bin/org/example/resource.txt').read_bytes(), b'unchanged resource')
            manifest = (root / 'build/system-manifest.mf').read_text()
            for library in extension.LIBRARIES:
                self.assertIn(f'file:/usr/share/java/{library}.jar', manifest)


if __name__ == '__main__':
    unittest.main()
