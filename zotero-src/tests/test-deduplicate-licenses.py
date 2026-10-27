import importlib.util
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location(
    'notices', Path(__file__).resolve().parents[1] / 'scripts/deduplicate-licenses.py')
notices = importlib.util.module_from_spec(spec)
spec.loader.exec_module(notices)


class DeduplicateTest(unittest.TestCase):
    def test_preserves_bytes_and_paths_with_relative_links(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            expected = {'a/LICENSE': b'full notice\n', 'b/nested/LICENSE': b'full notice\n',
                        'c/LICENSE': b'different notice\n'}
            for name, data in expected.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            self.assertEqual(notices.deduplicate(root), len(b'full notice\n'))
            duplicate = root / 'b/nested/LICENSE'
            self.assertTrue(duplicate.is_symlink())
            self.assertFalse(duplicate.readlink().is_absolute())
            for name, data in expected.items():
                self.assertEqual((root / name).read_bytes(), data)
            self.assertEqual(notices.deduplicate(root), 0)

    def test_existing_symlinks_are_not_followed_or_replaced(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'LICENSE').write_text('notice')
            (root / 'alias').symlink_to('LICENSE')
            (root / 'missing').symlink_to('absent')
            self.assertEqual(notices.deduplicate(root), 0)
            self.assertEqual((root / 'alias').readlink(), Path('LICENSE'))
            self.assertTrue((root / 'missing').is_symlink())


if __name__ == '__main__':
    unittest.main()
