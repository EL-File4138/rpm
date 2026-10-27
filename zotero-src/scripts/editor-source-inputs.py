#!/usr/bin/python3
"""Plan and verify editor source inputs; esbuild is invoked by the spec."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil


PACKAGES = {
    "commands": ("1.7.1", "commands.ts"),
    "dropcursor": ("1.8.2", "dropcursor.ts"),
    "gapcursor": ("1.3.2", "index.ts"),
    "history": ("1.4.1", "history.ts"),
    "inputrules": ("1.5.0", "index.ts"),
    "keymap": ("1.2.3", "keymap.ts"),
    "markdown": ("1.13.2", "index.ts"),
    "model": ("1.25.2", "index.ts"),
    "schema-basic": ("1.2.4", "schema-basic.ts"),
    "schema-list": ("1.5.1", "schema-list.ts"),
    "state": ("1.4.3", "index.ts"),
    "tables": ("1.7.1", "index.ts"),
    "transform": ("1.10.4", "index.ts"),
    "utils": ("1.2.2", "index.ts"),
    "view": ("1.40.1", "index.ts"),
}


def check_graph(graph, source, manifest):
    source = source.resolve()
    allowed = set(manifest.get("dependencies", {})) | set(manifest.get("peerDependencies", {}))
    inputs = {}
    for filename in graph["inputs"]:
        path = (source / filename).resolve()
        relative = path.relative_to(source / "src")
        if path.suffix not in (".ts", ".js"):
            raise ValueError(f"Unexpected editor source input: {path}")
        inputs[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    for output in graph["outputs"].values():
        for item in output["imports"]:
            name = item["path"]
            package = "/".join(name.split("/")[:2]) if name.startswith("@") else name.split("/")[0]
            if not item["external"] or package not in allowed:
                raise ValueError(f"Unexpected editor runtime import: {name}")
    return inputs


def runtime_outputs(manifest):
    outputs = {manifest["main"]: "cjs", manifest["module"]: "esm"}
    exports = manifest.get("exports", {})
    entry = exports.get(".", exports)
    for condition, format_ in (("require", "cjs"), ("import", "esm")):
        if condition in entry:
            filename = entry[condition].removeprefix("./")
            if filename in outputs and outputs[filename] != format_:
                raise ValueError(f"Conflicting editor output format: {filename}")
            outputs[filename] = format_
    return outputs


def plan(root):
    modules = root / "note-editor/node_modules"
    sources = root / ".rpm-editor-sources"
    packages = []
    # Validate every pin before replacing any previously installed output.
    for suffix, (version, entry) in PACKAGES.items():
        name = f"prosemirror-{suffix}"
        destination = modules / name
        source = sources / name if suffix in ("tables", "utils") else destination
        manifest = json.loads((source / "package.json").read_text())
        installed = json.loads((destination / "package.json").read_text())
        if manifest["version"] != version or installed["version"] != version:
            raise ValueError(f"Unexpected {name} version; expected {version}")
        if not (source / "src" / entry).is_file() or not (source / "LICENSE").is_file():
            raise ValueError(f"Missing original sources or license for {name}")
        packages.append((name, source, destination, manifest, entry))

    return packages


def commands(root):
    rows = []
    for name, source, destination, manifest, entry in plan(root):
        for filename, format_ in runtime_outputs(manifest).items():
            output = destination / filename
            if not output.resolve().is_relative_to(destination.resolve() / "dist"):
                raise ValueError(f"Unexpected editor output path: {filename}")
            rows.append('\t'.join((str(source), entry, format_, str(output))))
    return '\n'.join(rows) + '\n'


def collect(root):
    packages = plan(root)
    licenses = root / "rpm-licenses/editor-dependencies"
    licenses.mkdir(parents=True, exist_ok=True)
    inventory = {}
    for name, source, destination, manifest, entry in packages:
        outputs = runtime_outputs(manifest)
        records = []
        for filename, format_ in outputs.items():
            output = destination / filename
            if not output.resolve().is_relative_to(destination.resolve() / "dist"):
                raise ValueError(f"Unexpected editor output path: {filename}")
            output.parent.mkdir(parents=True, exist_ok=True)
            metadata = output.with_suffix(output.suffix + ".inputs.json")
            inputs = check_graph(json.loads(metadata.read_text()), source, manifest)
            records.append({"output": filename, "inputs": inputs})
        shutil.copyfile(source / "LICENSE", licenses / f"{name}-LICENSE")
        inventory[name] = {"version": manifest["version"], "license": manifest["license"],
                           "builds": records}
    (root / "rpm-editor-source-inputs.json").write_text(json.dumps(inventory, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--collect", action="store_true")
    args = parser.parse_args()
    if args.collect:
        collect(args.root.resolve())
    else:
        print(commands(args.root.resolve()), end='')
