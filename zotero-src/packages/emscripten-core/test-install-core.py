"""Check compiler selection without running a compiler or installing on the host."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location(
    'install_core', Path(__file__).with_name('install-core.py'))
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)


class CompilerConfigurationTest(unittest.TestCase):
    def test_standard_and_compatibility_toolchain_roots(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'source'
            source.mkdir()
            for directory in ('tools/maint', 'system', 'src', 'cmake',
                              'third_party/terser', 'third_party/leb128', 'acorn/src'):
                (source / directory).mkdir(parents=True, exist_ok=True)
            for name in ('LICENSE', 'AUTHORS', 'emscripten-version.txt',
                         'third_party/__init__.py', 'tools/install.py',
                         'tools/webidl_binder.py', 'acorn/LICENSE', *core.COMMANDS):
                (source / name).write_text('fixture\n')
            (source / 'emcc.py').write_text('# compiler entry point\n')
            (source / 'acorn/package.json').write_text(json.dumps({'version': '8.15.0'}))
            previous = Path.cwd()
            try:
                os.chdir(source)
                for name, llvm, binaryen in (
                    ('standard', None, None),
                    ('compat', Path('/usr/lib64/llvm22/bin'), Path('/usr/lib64/binaryen125')),
                ):
                    destination = root / name
                    core.install(destination, Path('/usr'), source / 'acorn', llvm, binaryen)
                    config = {}
                    exec((destination / 'usr/share/emscripten/.emscripten').read_text(), config)
                    self.assertEqual(config['LLVM_ROOT'], str(llvm or '/usr/bin'))
                    self.assertEqual(config['BINARYEN_ROOT'], str(binaryen or '/usr'))
                    self.assertEqual(config['NODE_JS'], ['/usr/bin/node'])
                    self.assertNotIn(str(destination), config['LLVM_ROOT'])
                    self.assertTrue((destination / 'usr/bin/emcc').stat().st_mode & 0o111)
            finally:
                os.chdir(previous)


if __name__ == '__main__':
    unittest.main()
