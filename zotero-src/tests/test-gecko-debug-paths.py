"""Generated debug locations must resolve to real, faithful SRPM inputs."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('prepare_gecko', Path(__file__).resolve().parents[1] / 'scripts/prepare-gecko.py')
gecko = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gecko)


class DebugPathsTest(unittest.TestCase):
    def fixture(self, root):
        for relative, label in (
            ('gfx/angle/checkout/src/compiler/preprocessor/preprocessor_lex_autogen.cpp', 'preprocessor.l'),
            ('gfx/angle/checkout/src/compiler/translator/glslang_lex_autogen.cpp', 'glslang.l'),
            ('third_party/sqlite3/ext/fts5.c', 'fts5parse.y'),
        ):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f'// generated\n#line 90 "{label}"\nint value;\n')
        directory = root / 'gfx/harfbuzz/src'
        directory.mkdir(parents=True)
        for name in ('hb-number-parser', 'hb-ot-shaper-indic-machine',
                     'hb-ot-shaper-khmer-machine', 'hb-ot-shaper-myanmar-machine',
                     'hb-ot-shaper-use-machine'):
            (directory / f'{name}.hh').write_text(f'#line 12 "{name}.rl"\nint value;\n#line 1 "NONE"\n')
            (directory / f'{name}.rl').write_text('// actual original input\n')

    def test_real_inputs_keep_lines_and_missing_inputs_use_physical_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            gecko.prepare_debug_source_paths(root)
            path = root / 'third_party/sqlite3/ext/fts5.c'
            self.assertIn(f'#line 3 "{path}"\nint value;', path.read_text())
            header = root / 'gfx/harfbuzz/src/hb-number-parser.hh'
            self.assertIn(f'#line 12 "{header.with_suffix(".rl")}"', header.read_text())
            self.assertIn(f'#line 4 "{header}"', header.read_text())
            self.assertFalse((header.parent / 'NONE').exists())

    def test_unknown_directive_fails_before_any_file_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            header = root / 'gfx/harfbuzz/src/hb-number-parser.hh'
            header.write_text('#line 1 "unexpected.rl"\n')
            before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
            with self.assertRaises(ValueError):
                gecko.prepare_debug_source_paths(root)
            self.assertEqual(before, {p: p.read_bytes() for p in before})


if __name__ == '__main__':
    unittest.main()
