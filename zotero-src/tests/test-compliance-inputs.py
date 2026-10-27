"""Exercise the spec's original-source checks without compiling dependencies."""

from pathlib import Path
import json
import re
import subprocess
import sys
import tempfile
import unittest


SPEC = (Path(__file__).resolve().parents[1] / "zotero.spec").read_text()
CHECK = SPEC.split("%check\n", 1)[1].split("%{__python3} - <<'PY'\n", 1)[1].split("\nPY\n", 1)[0]


class OriginalInputTest(unittest.TestCase):
    def fixture(self, root):
        for directory, manifest, version, implementation in (
            ('fluent-bundle', 'fluent-bundle/package.json', '0.19.1', 'fluent-bundle/src/bundle.ts'),
            ('fluent-react', 'fluent-react/package.json', '0.15.2', 'fluent-react/src/index.ts'),
            ('darkreader', 'package.json', '4.9.83', 'src/api/index.ts'),
            ('sentencex-ts', 'package.json', '0.1.13-ts', 'src/index.ts'),
            ('fflate', 'package.json', '0.8.2', 'src/index.ts'),
            ('fastest-levenshtein', 'package.json', '1.0.16', 'mod.ts'),
            ('sorted-btree', 'package.json', '1.8.0', 'b+tree.ts'),
            ('tinymce', 'package.json', '4.9.4', 'src/core/main/ts/api/Editor.ts'),
            ('tinymce-paste', 'package.json', '4.6.7', 'src/plugins/paste/src/main/js/Plugin.js'),
        ):
            source = root / '.rpm-original-sources' / directory
            for filename, body in ((manifest, json.dumps({'version': version})),
                                   (implementation, '// original implementation\n')):
                path = source / filename
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(body)
        for name in ('b+tree.js', 'sorted-array.js'):
            (root / '.rpm-original-sources/sorted-btree' / name).write_bytes(b'original();\n')
            path = root / 'reader/node_modules/sorted-btree' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'original();\r\n')
        for filename in ('resource/tinymce/license.txt', 'rpm-licenses/tinymce/license.txt',
                         '.rpm-original-sources/tinymce-paste/LICENSE.TXT',
                         'rpm-licenses/tinymce/paste-LICENSE.TXT'):
            path = root / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('Authentic upstream LGPL notice\n')

    def run_check(self, root):
        return subprocess.run([sys.executable, '-c', CHECK], cwd=root,
                              capture_output=True, text=True)

    def test_corresponding_inputs_and_crlf_only_difference_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            result = self.run_check(root)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_wrong_source_version_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            (root / '.rpm-original-sources/fflate/package.json').write_text('{"version":"wrong"}')
            self.assertNotEqual(self.run_check(root).returncode, 0)

    def test_missing_original_implementation_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            (root / '.rpm-original-sources/fastest-levenshtein/mod.ts').unlink()
            self.assertNotEqual(self.run_check(root).returncode, 0)

    def test_changed_sorted_btree_implementation_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            (root / 'reader/node_modules/sorted-btree/b+tree.js').write_text('different();\n')
            self.assertNotEqual(self.run_check(root).returncode, 0)

    def test_wrong_rpm_license_copy_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            (root / 'rpm-licenses/tinymce/license.txt').write_text('wrong notice')
            self.assertNotEqual(self.run_check(root).returncode, 0)

    def test_wrong_paste_license_copy_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            (root / 'rpm-licenses/tinymce/paste-LICENSE.TXT').write_text('wrong notice')
            self.assertNotEqual(self.run_check(root).returncode, 0)


class NumericRuntimeNoticeTest(unittest.TestCase):
    packages = {'inherits': '2.0.4', 'd': '1.0.1', 'es5-ext': '0.10.62',
                'util-deprecate': '1.0.2', 'cssesc': '3.0.0'}

    def test_numeric_module_packages_are_declared(self):
        for name, version in self.packages.items():
            self.assertRegex(SPEC, rf'(?m)^Provides:\s+bundled\({re.escape(name)}\) = {re.escape(version)}$')

    def test_spec_copies_numeric_module_notices(self):
        loop = 'for entry in ' + SPEC.split('for entry in ', 1)[1].split('\ndone\n', 1)[0] + '\ndone\n'
        entries = loop.split('; do', 1)[0].removeprefix('for entry in ').replace('\\\n', '').split()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for entry in entries:
                project, name = entry.split(':', 1)
                notice = root / project / 'node_modules' / name / (
                    'LICENSE-MIT.txt' if name == 'cssesc' else 'LICENSE')
                notice.parent.mkdir(parents=True, exist_ok=True)
                notice.write_text(f'Authentic notice for {entry}\n')
            subprocess.run(['sh', '-ec', loop], cwd=root, check=True)
            for name in self.packages:
                directory = root / 'rpm-licenses/runtime/reader' / name
                self.assertEqual([file.read_text() for file in directory.iterdir()],
                                 [f'Authentic notice for reader:{name}\n'])


if __name__ == '__main__':
    unittest.main()
