"""Exercise the desktop-only minification adapter without webpack dependencies."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest


spec = importlib.util.spec_from_file_location("prepare", Path(__file__).resolve().parents[1] / "scripts/prepare-source.py")
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)


class EditorConfigTest(unittest.TestCase):
    def test_desktop_is_readable_without_changing_web_or_mobile_builds(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "note-editor/webpack.config.js"
            config.parent.mkdir()
            config.write_text("""const generate = build => ({
                name: build,
                mode: build === 'dev' ? 'development' : 'production',
                optimization: {
                    minimize: build !== 'dev',
                    minimizer: build === 'dev' ? [] : ['terser', 'css'],
                },
            });
            module.exports = ['dev', 'web', 'zotero', 'ios', 'android'].map(generate);
            """)
            prepare.prepare_editor(root)
            subprocess.run(["node", "-e", """
                const assert = require('node:assert/strict');
                for (const config of require(process.argv[1])) {
                    assert.equal(config.optimization.minimize,
                        !['dev', 'zotero'].includes(config.name), config.name);
                    assert.equal(config.optimization.minimizer.length,
                        ['dev', 'zotero'].includes(config.name) ? 0 : 2, config.name);
                    assert.equal(config.mode,
                        config.name === 'dev' ? 'development' : 'production');
                }
            """, str(config)], check=True)

    def test_unknown_upstream_setting_fails_explicitly(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "note-editor/webpack.config.js"
            config.parent.mkdir()
            config.write_text("unexpected upstream setting")
            with self.assertRaises(ValueError):
                prepare.prepare_editor(root)
            self.assertEqual(config.read_text(), "unexpected upstream setting")


if __name__ == "__main__":
    unittest.main()
