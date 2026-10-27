import importlib.util
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location(
    "update_release", Path(__file__).with_name("update_release.py")
)
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)
ROOT = Path(__file__).resolve().parents[2]


class UpdateReleaseTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        for _, paths in release.PACKAGES.values():
            for relative in paths:
                target = self.root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text((ROOT / relative).read_text())

    def snapshot(self):
        return {p.relative_to(self.root): p.read_text() for p in self.root.rglob("*.spec")}

    def test_dispatch_and_manual_inputs(self):
        for event, key in [("repository_dispatch", "client_payload"), ("workflow_dispatch", "inputs")]:
            with self.subTest(event=event):
                self.assertEqual(
                    release.resolve_event(event, {key: {"package": "aegisub", "version": "v3.5.0-rc1"}}),
                    ("aegisub", "3.5.0~rc1", "aegisub-next"),
                )

    def test_untrusted_payloads_rejected(self):
        for payload in [None, {}, {"package": []}, {"package": "../zotero", "version": "9.1"},
                        {"package": "zotero", "version": 10},
                        {"package": "zotero", "version": "9.1\nbranch=other"},
                        {"package": "zotero", "version": "$(touch /tmp/injection)"},
                        {"package": "zotero", "version": "%{lua:print(1)}"},
                        {"package": "xpadneo", "version": "1.0-rc1"}]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                release.resolve_event("repository_dispatch", {"client_payload": payload})

    def test_zotero_resets_release_and_prepends_changelog(self):
        path = self.root / "zotero/zotero.spec"
        original = path.read_text().replace("1%{?dist}", "7%{?dist}", 1)
        path.write_text(original)
        old_log = original.split("%changelog\n")[1]
        self.assertTrue(release.update_specs(self.root, "zotero", "v99.0"))
        updated = path.read_text()
        self.assertEqual(release.field(updated, "Version")[2], "99.0")
        self.assertEqual(release.field(updated, "Release")[2], "1%{?dist}")
        self.assertIn(" - 99.0-1\n- Update to version 99.0.\n", updated)
        self.assertTrue(updated.endswith(old_log))

    def test_xpadneo_updates_both_specs(self):
        self.assertTrue(release.update_specs(self.root, "xpadneo", "99.0"))
        for relative in release.PACKAGES["xpadneo"][1]:
            self.assertEqual(release.field((self.root / relative).read_text(), "Version")[2], "99.0")

    def test_aegisub_preserves_automatic_release_and_changelog(self):
        path = self.root / "aegisub/aegisub.spec"
        original = path.read_text()
        self.assertTrue(release.update_specs(self.root, "aegisub", "99.0-rc1"))
        current = release.field(original, "Version")[2]
        self.assertEqual(path.read_text(), original.replace(current, "99.0~rc1", 1))
        self.assertTrue(release.update_specs(self.root, "aegisub", "99.0"))

    def test_duplicates_and_older_versions_do_not_write(self):
        for package, (_, paths) in release.PACKAGES.items():
            with self.subTest(package=package):
                current = release.field((self.root / paths[0]).read_text(), "Version")[2]
                before = self.snapshot()
                self.assertFalse(release.update_specs(self.root, package, current))
                self.assertFalse(release.update_specs(self.root, package, "0.0.1"))
                self.assertEqual(before, self.snapshot())

    def test_rpm_numeric_ordering(self):
        self.assertTrue(release.update_specs(self.root, "zotero", "99.9"))
        self.assertTrue(release.update_specs(self.root, "zotero", "99.10"))
        self.assertFalse(release.update_specs(self.root, "zotero", "99.9"))

    def test_invalid_second_spec_leaves_first_untouched(self):
        second = self.root / release.PACKAGES["xpadneo"][1][1]
        second.write_text(second.read_text().replace("%changelog", "%missing"))
        before = self.snapshot()
        with self.assertRaises(ValueError):
            release.update_specs(self.root, "xpadneo", "99.0")
        self.assertEqual(before, self.snapshot())

    def test_newer_second_spec_prevents_partial_downgrade(self):
        second = self.root / release.PACKAGES["xpadneo"][1][1]
        text = second.read_text()
        current = release.field(text, "Version")[2]
        second.write_text(text.replace(current, "100.0", 1))
        before = self.snapshot()
        self.assertFalse(release.update_specs(self.root, "xpadneo", "99.0"))
        self.assertEqual(before, self.snapshot())


if __name__ == "__main__":
    unittest.main()
