"""Check release staging without downloading or compiling upstream sources."""
import hashlib
import importlib.util
import io
import json
import subprocess
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    'stage_release', Path(__file__).with_name('stage-release.py'))
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseStagingTest(unittest.TestCase):
    def test_standalone_specs_parse_before_review_loads_target_macros(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'zotero-src.spec'
            for target in ('f44', 'rawhide'):
                path.write_text(release.standalone_spec(root, target))
                # Review parses on the host first, then again with target macros.
                for fedora in ('43', '44', '46'):
                    with self.subTest(target=target, host=fedora):
                        subprocess.run(['rpmspec', '--parse', '--define',
                                        f'fedora {fedora}', '--define',
                                        f'_sourcedir {temporary}', str(path)],
                                       stdout=subprocess.DEVNULL, check=True)

    def test_standalone_target_recipes_have_no_include_dependencies(self):
        root = Path(__file__).resolve().parents[1]
        for target in ('f44', 'rawhide'):
            text = release.standalone_spec(root, target)
            self.assertNotIn('%include', text)
            self.assertIn('Name:           zotero-src', text)
            self.assertIn('%{buildroot}', text)
            self.assertIn('cargo build --frozen', text)
            self.assertIn('zotero-common.inc', text)

    def fixture(self, root, checksum=None):
        (root / 'sources').mkdir()
        (root / 'spec').mkdir()
        (root / 'f44').mkdir()
        (root / 'zotero.spec').write_text('Version: 10.0.3\nRelease: 2%{?dist}\n# current shared recipe\n')
        (root / 'f44/zotero-src.spec').write_text('Source900: ../zotero.spec#/zotero-common.inc\n')
        (root / 'spec/components-sources.inc').write_text('# current fragment\n')
        (root / 'helper.py').write_text('# current helper\n')
        (root / 'sources/release-inputs.json').write_text(json.dumps({
            'version': '10.0.3', 'url': 'https://example.invalid/seed.src.rpm',
            'sha256': checksum or hashlib.sha256(b'seed').hexdigest(),
        }))

    def test_seed_checksum_failure_prevents_extraction(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root, '0' * 64)
            with patch.object(release.urllib.request, 'urlopen', return_value=io.BytesIO(b'seed')), \
                    patch.object(release.subprocess, 'run') as run:
                with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                    release.stage(root, 'f44', root / 'output')
                run.assert_not_called()

    def test_shared_recipe_and_aliased_helpers_replace_seed_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)

            def run(command, **kwargs):
                if command[0] == 'cpio':
                    sources = kwargs['cwd']
                    (sources / 'archive.tar.xz').write_bytes(b'reviewed upstream archive')
                    (sources / 'renamed-helper.py').write_text('# stale helper\n')
                if command[0] == 'rpmbuild':
                    sources = Path(command[command.index('--define') + 1].split(' ', 1)[1])
                    self.assertEqual((sources / 'zotero-common.inc').read_bytes(),
                                     (root / 'zotero.spec').read_bytes())
                    self.assertEqual((sources / 'renamed-helper.py').read_text(), '# current helper\n')
                    self.assertEqual((sources / 'components-sources.inc').read_text(), '# current fragment\n')

            expanded = ('Source900: ../zotero.spec#/zotero-common.inc\nSource0: archive.tar.xz\n'
                        'Source3: helper.py#/renamed-helper.py\n')
            with patch.object(release.urllib.request, 'urlopen', return_value=io.BytesIO(b'seed')), \
                    patch.object(release.subprocess, 'run', side_effect=run), \
                    patch.object(release.subprocess, 'check_output', side_effect=[
                        expanded, 'zotero-common.inc\nzotero-src.spec\narchive.tar.xz\n']):
                release.stage(root, 'f44', root / 'output')

    def test_two_spec_members_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            with patch.object(release.urllib.request, 'urlopen', return_value=io.BytesIO(b'seed')), \
                    patch.object(release.subprocess, 'run'), \
                    patch.object(release.subprocess, 'check_output', side_effect=[
                        'Source900: ../zotero.spec#/zotero-common.inc\n',
                        'zotero-src.spec\nzotero.spec\n']):
                with self.assertRaisesRegex(ValueError, 'exactly one'):
                    release.stage(root, 'f44', root / 'output')


if __name__ == '__main__':
    unittest.main()
