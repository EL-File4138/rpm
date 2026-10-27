import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    "editor_dependencies", Path(__file__).resolve().parents[1] / "scripts/editor-source-inputs.py")
editor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(editor)


class EditorSourceTest(unittest.TestCase):
    def test_exported_runtime_entries_include_non_module_entry(self):
        manifest = {"main": "dist/index.cjs", "module": "dist/index.esm.js",
                    "exports": {".": {"types": "./dist/index.d.ts",
                                      "import": "./dist/index.js",
                                      "require": "./dist/index.cjs"}}}
        self.assertEqual(editor.runtime_outputs(manifest), {
            "dist/index.cjs": "cjs", "dist/index.esm.js": "esm", "dist/index.js": "esm"})

    def test_original_inputs_and_declared_imports(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            (source / "src").mkdir()
            body = b"export const value = 1;\n"
            (source / "src/index.ts").write_bytes(body)
            graph = {"inputs": {"src/index.ts": {}}, "outputs": {"bundle": {"imports": [
                {"path": "prosemirror-state", "external": True},
            ]}}}
            manifest = {"peerDependencies": {"prosemirror-state": "^1"}}
            self.assertEqual(editor.check_graph(graph, source, manifest),
                             {"index.ts": hashlib.sha256(body).hexdigest()})
            graph["outputs"]["bundle"]["imports"][0]["path"] = "undeclared-package"
            with self.assertRaisesRegex(ValueError, "Unexpected editor runtime import"):
                editor.check_graph(graph, source, manifest)

    def test_generated_inputs_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            for name in ("dist/index.js", "src/data.wasm"):
                path = source / name
                path.parent.mkdir(exist_ok=True)
                path.write_bytes(b"generated")
                with self.assertRaises(ValueError):
                    editor.check_graph({"inputs": {name: {}}, "outputs": {}}, source, {})

    def test_all_pins_checked_before_any_build(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for suffix, (version, entry) in editor.PACKAGES.items():
                name = f"prosemirror-{suffix}"
                destination = root / "note-editor/node_modules" / name
                source = root / ".rpm-editor-sources" / name if suffix in ("tables", "utils") else destination
                manifest = {"version": version}
                for directory in {destination, source}:
                    directory.mkdir(parents=True, exist_ok=True)
                    (directory / "package.json").write_text(json.dumps(manifest))
                (source / "src").mkdir()
                (source / "src" / entry).write_text("export const value = 1;")
                (source / "LICENSE").write_text("Test fixture license")
            last = root / "note-editor/node_modules/prosemirror-view/package.json"
            last.write_text('{"version":"unexpected"}')
            with self.assertRaisesRegex(ValueError, "Unexpected prosemirror-view version"):
                editor.commands(root)
            self.assertFalse((root / "rpm-licenses").exists())


if __name__ == "__main__":
    unittest.main()
