"""Check readable TinyMCE substitution and preservation of Zotero patches."""
import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile
import unittest


spec = importlib.util.spec_from_file_location('prepare_tinymce',
                                              Path(__file__).resolve().parents[1] / 'scripts/prepare-tinymce.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TinyMCETest(unittest.TestCase):
    def fixture(self, root):
        files = {'tinymce.min.js': b'core();', 'plugins/paste/plugin.min.js': b'oldPaste();',
                 'plugins/link/plugin.min.js': b'!/^\\w+:/i.test(r);else s(e.href)'}
        readable = {'tinymce.js': b'// readable core\ncore();\n',
                    'plugins/paste/plugin.js': b'// readable old paste\noldPaste();\n',
                    'plugins/link/plugin.js': b'!/^\\w+:/i.test(href); OpenUrl.open(a.href);'}
        for name in ('autolink', 'code', 'contextmenu', 'directionality', 'lists',
                     'nonbreaking', 'searchreplace', 'textcolor'):
            files[f'plugins/{name}/plugin.min.js'] = b'plugin();'
            readable[f'plugins/{name}/plugin.js'] = b'// readable plugin\nplugin();\n'
        files['themes/modern/theme.min.js'] = b'theme();'
        readable['themes/modern/theme.js'] = b'// readable theme\ntheme();\n'
        for name, body in files.items():
            path = root / 'resource/tinymce' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            if 'link/' in name:
                body = body.replace(b'\\w+:', b'\\w+:|^#').replace(
                    b'else s(e.href)', b'else t.execCommand("ZoteroLinkClick", false, e.href)')
            path.write_bytes(body)
        for filename in ('current.tgz', 'paste.tgz'):
            with tarfile.open(root / filename, 'w:gz') as archive:
                for name, body in (files | readable).items():
                    member = tarfile.TarInfo('package/' + name)
                    member.size = len(body)
                    archive.addfile(member, io.BytesIO(body))

    def test_readable_files_keep_loader_paths_and_customizations(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            module.prepare(root, root / 'current.tgz', root / 'paste.tgz')
            link = (root / 'resource/tinymce/plugins/link/plugin.min.js').read_text()
            self.assertIn('\\w+:|^#', link)
            self.assertIn('editor.execCommand("ZoteroLinkClick", false, a.href)', link)
            self.assertIn('readable old paste',
                          (root / 'resource/tinymce/plugins/paste/plugin.min.js').read_text())
            module.prepare(root, root / 'current.tgz', root / 'paste.tgz', check=True)
            (root / 'resource/tinymce/plugins/paste/plugin.min.js').write_bytes(b'wrong paste();')
            with self.assertRaises(ValueError):
                module.prepare(root, root / 'current.tgz', root / 'paste.tgz', check=True)

    def test_unknown_customization_fails_before_any_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            (root / 'resource/tinymce/tinymce.min.js').write_bytes(b'unknown();')
            before = {p: p.read_bytes() for p in (root / 'resource').rglob('*.js')}
            with self.assertRaises(ValueError):
                module.prepare(root, root / 'current.tgz', root / 'paste.tgz')
            self.assertEqual(before, {p: p.read_bytes() for p in before})


if __name__ == '__main__':
    unittest.main()
