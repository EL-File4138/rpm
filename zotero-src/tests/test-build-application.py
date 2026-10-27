"""Regression checks for application assembly orchestration."""

import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    "prepare_application", Path(__file__).resolve().parents[1] / "scripts/prepare-application.py")
application = importlib.util.module_from_spec(spec)
spec.loader.exec_module(application)


class AssemblyTest(unittest.TestCase):
    def test_obsolete_module_outputs_are_removed_without_touching_other_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("reader", "note-editor", "document-worker", "unrelated"):
                target = root / "build/resource" / name
                target.mkdir(parents=True)
                (target / "old-font.woff2").write_text("old")
            application.clear_module_outputs(root)
            for name in ("reader", "note-editor", "document-worker"):
                self.assertFalse((root / "build/resource" / name).exists())
            self.assertEqual((root / "build/resource/unrelated/old-font.woff2").read_text(), "old")

    def test_module_output_symlinks_fail_before_removing_any_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reader = root / "build/resource/reader"
            reader.mkdir(parents=True)
            (reader / "preserved").touch()
            target = root / "source"
            target.mkdir()
            (root / "build/resource/note-editor").symlink_to(target, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "not a symlink"):
                application.clear_module_outputs(root)
            self.assertTrue((reader / "preserved").exists())
            self.assertTrue(target.is_dir())

    def test_assembly_commands_are_owned_by_the_spec(self):
        recipe = (Path(__file__).resolve().parents[1] / "zotero.spec").read_text()
        self.assertIn('mkdir -p rpm-prepared', recipe)
        self.assertIn('bash app/build.sh -d "$PWD/rpm-prepared"', recipe)
        self.assertIn('test ! -e app/staging/Zotero_linux-x86_64/updater', recipe)

    def test_check_rejects_unpatched_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "build/resource").mkdir(parents=True)
            (root / "build/resource/monacopilot.mjs").write_text('@monacopilot/core')
            (root / "build/resource/monacopilot-core.mjs").write_text('unpatched')
            with self.assertRaisesRegex(ValueError, "imports were not relocated"):
                application.check(root)


if __name__ == "__main__":
    unittest.main()
