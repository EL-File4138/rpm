import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location('mathjax_notices',
                                              Path(__file__).resolve().parents[1] / 'scripts/collect-mathjax-notices.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class MathJaxNoticeTest(unittest.TestCase):
    def test_preserves_notices_and_strips_unassigned_template_copyright(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fonts = root / 'fonts'
            fonts.mkdir()
            for index in range(23):
                (fonts / f'font-{index}.woff').touch()
            license_file = root / 'OFL.txt'
            license_file.write_text('Copyright <placeholder>\n'
                                    'SIL OPEN FONT LICENSE Version 1.1 - 26 February 2007\n'
                                    'PERMISSION & CONDITIONS\nTERMINATION\nDISCLAIMER\n')
            with patch.object(module, 'TTFont') as font:
                from types import SimpleNamespace
                font.return_value.__enter__.return_value.__getitem__.return_value.names = [
                    SimpleNamespace(nameID=0, toUnicode=lambda: 'Copyright actual holder'),
                    SimpleNamespace(nameID=13, toUnicode=lambda: 'Actual font license notice')]
                module.collect(fonts, license_file, root / 'notices')
            self.assertNotIn('placeholder', (root / 'notices/OFL-1.1.txt').read_text())
            notices = (root / 'notices/FONT-NOTICES.txt').read_text()
            self.assertEqual(notices.count('Copyright actual holder'), 23)
            self.assertEqual(notices.count('Actual font license notice'), 23)

    def test_wrong_font_count_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            license_file = root / 'OFL.txt'
            license_file.write_text('SIL OPEN FONT LICENSE Version 1.1 - 26 February 2007\n'
                                    'PERMISSION & CONDITIONS\nTERMINATION\nDISCLAIMER\n')
            with self.assertRaises(ValueError):
                module.collect(root, license_file, root / 'notices')


if __name__ == '__main__':
    unittest.main()
