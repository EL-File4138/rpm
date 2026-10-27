"""Verify the recipe corrects font notices without changing upstream fonts."""
from pathlib import Path
import subprocess
import tempfile
import unittest


class FontNoticeTest(unittest.TestCase):
    def test_recipe_preserves_font_bytes_and_installs_matching_notices(self):
        spec = (Path(__file__).resolve().parents[1] / "zotero.spec").read_text()
        start = spec.index("for style in Bold BoldItalic Italic Regular; do")
        end = spec.index("%{__python3} %{SOURCE5}", start)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / ".rpm-font-sources/liberation"
            source.mkdir(parents=True)
            (source / "License.txt").write_text("Correct original-font license")
            projects = ("reader/pdfjs/pdf.js", "document-worker/pdf.js")
            for project in projects:
                target = root / project / "external/standard_fonts"
                target.mkdir(parents=True)
                for style in ("Bold", "BoldItalic", "Italic", "Regular"):
                    (target / f"LiberationSans-{style}.ttf").write_bytes(style.encode())
                (target / "LICENSE_LIBERATION").write_text("Wrong adjacent notice")
            subprocess.run(["bash", "-ec", spec[start:end]], cwd=root, check=True)
            for project in projects:
                target = root / project / "external/standard_fonts"
                self.assertEqual((target / "LICENSE_LIBERATION").read_text(),
                                 "Correct original-font license")
                for style in ("Bold", "BoldItalic", "Italic", "Regular"):
                    self.assertEqual((target / f"LiberationSans-{style}.ttf").read_bytes(), style.encode())


if __name__ == "__main__":
    unittest.main()
