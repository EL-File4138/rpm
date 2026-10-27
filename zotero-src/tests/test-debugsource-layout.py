#!/usr/bin/python3
"""Verify that Gecko source paths are visible to RPM's debugedit source root."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


@unittest.skipUnless(shutil.which("clang") and shutil.which("debugedit"),
                     "clang and debugedit are required")
class DebugsourceLayoutTest(unittest.TestCase):
    @unittest.skipUnless(shutil.which("cpio"), "cpio is required")
    def test_exported_zstd_header_retains_hardlink_in_debugsource_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            original = source / "third_party/zstd/lib/zstd.h"
            exported = source / "obj-rpm/dist/include/zstd/zstd.h"
            original.parent.mkdir(parents=True)
            exported.parent.mkdir(parents=True)
            original.write_text("/* source header */\n")
            exported.symlink_to(original)
            recipe = (Path(__file__).resolve().parents[1] / "zotero.spec").read_text()
            commands = recipe.partition("# Preserve both debugsource header paths")[2]
            commands = commands.partition("\n")[2]
            commands = commands.partition("\n# These prerequisites")[0]
            commands = commands.replace(".rpm-gecko/firefox-%{gecko_version}", ".")
            subprocess.run(["sh", "-ec", commands], cwd=source, check=True)
            destination = root / "debugsource"
            destination.mkdir()
            subprocess.run(["cpio", "-pd0mL", str(destination)], cwd=source,
                           input=b"third_party/zstd/lib/zstd.h\0obj-rpm/dist/include/zstd/zstd.h\0",
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            self.assertEqual((destination / original.relative_to(source)).stat().st_ino,
                             (destination / exported.relative_to(source)).stat().st_ino)

    def test_gecko_sources_must_be_inside_application_build_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            application = root / "zotero"
            application.mkdir()
            for name, gecko in [("sibling", root / "firefox"),
                                ("nested", application / ".rpm-gecko/firefox")]:
                gecko.mkdir(parents=True)
                source = gecko / "sample.c"
                source.write_text("int answer(void) { return 42; }\n")
                obj = root / f"{name}.o"
                listing = root / f"{name}.sources"
                subprocess.run(["clang", "-g1", "-c", str(source), "-o", str(obj)],
                               cwd=gecko, check=True)
                subprocess.run(["debugedit", "-b", str(application), "-d",
                                "/usr/src/debug/zotero-test", "-l", str(listing),
                                str(obj)], check=True)
                entries = listing.read_bytes().split(b"\0")
                if name == "sibling":
                    self.assertFalse(any(entries))
                else:
                    self.assertIn(b".rpm-gecko/firefox/sample.c", entries)


if __name__ == "__main__":
    unittest.main()
