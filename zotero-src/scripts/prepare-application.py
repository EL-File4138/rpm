#!/usr/bin/python3
"""Prepare dependency files and check outputs; build commands live in the spec."""

import argparse
import json
from pathlib import Path
import shutil


def clear_module_outputs(root):
    directories = [root / "build/resource" / name
                   for name in ("reader", "note-editor", "document-worker")]
    for directory in directories:
        if directory.is_symlink():
            raise ValueError(f"Expected generated module directory, not a symlink: {directory}")
    for directory in directories:
        if directory.exists():
            shutil.rmtree(directory)


def prepare(root, data):
    preload = root / "rpm-node-jobs.cjs"
    preload.write_text("const os = require('node:os');\n"
                       "const cpu = os.cpus()[0];\n"
                       "os.cpus = () => [cpu];\n"
                       "os.availableParallelism = () => 1;\n")
    for filename in ("katex.js", "katex.mjs"):
        shutil.copyfile(data / "katex-js" / filename,
                        root / "note-editor/node_modules/katex/dist" / filename)
    fonts = root / "note-editor/node_modules/katex/dist/fonts"
    shutil.rmtree(fonts)
    shutil.copytree(data / "katex-js/fonts", fonts)
    mathjax = root / "reader/node_modules/mathjax-full/js"
    shutil.rmtree(mathjax)
    shutil.copytree(data / "mathjax-chtml-js/js", mathjax)
    shutil.copyfile(data / "mathjax-chtml-js/node_modules/mhchemparser/dist/mhchemParser.js",
                    root / "reader/node_modules/mhchemparser/dist/mhchemParser.js")
    for package, filename, target in (
        ("pako-js", "pako.min.js", "pako/dist/pako.min.js"),
        ("prop-types-js", "prop-types.js", "prop-types/prop-types.js"),
        ("react-intl-js", "react-intl.min.js", "react-intl/dist/react-intl.min.js"),
        ("react-virtualized-js", "react-virtualized.js", "react-virtualized/dist/umd/react-virtualized.js"),
        ("react-autosuggest-js", "autosuggest.min.js", "react-autosuggest/dist/dist/standalone/autosuggest.min.js"),
    ):
        shutil.copyfile(data / package / filename, root / "node_modules" / target)
    for source, target in (("monaco-editor-js/vs", "resource/vs"),
                           ("ace-js", "node_modules/ace-builds/src")):
        shutil.rmtree(root / target)
        shutil.copytree(data / source, root / target)
    for project in (root, root / "reader", root / "note-editor"):
        for package in ("react", "react-dom", "scheduler"):
            destination = project / "node_modules" / package
            shutil.rmtree(destination)
            shutil.copytree(data / "react-js" / package, destination)
        cache = project / "node_modules/.cache"
        if cache.exists():
            shutil.rmtree(cache)
    for package, destination in (
        ("citeproc-rs-wasm", "node_modules/@citeproc-rs/wasm/_zotero"),
        ("csl-validator-wasm", "node_modules/csl-validator-wasm"),
        ("monacopilot-js/core", "node_modules/@monacopilot/core/build"),
        ("monacopilot-js/monacopilot", "node_modules/monacopilot/build"),
    ):
        shutil.copytree(data / package, root / destination, dirs_exist_ok=True)
    ort = root / "document-worker/node_modules/onnxruntime-web"
    shutil.rmtree(ort / "dist")
    shutil.copytree(data / "onnxruntime-web-wasm", ort / "dist")
    manifest = json.loads((ort / "package.json").read_text())
    manifest["exports"] = {"./wasm": "./dist/ort.wasm.mjs"}
    (ort / "package.json").write_text(json.dumps(manifest, indent=2) + "\n")
    # Replaced runtime files invalidate webpack's immutable node_modules cache.
    cache = root / "document-worker/node_modules/.cache/webpack"
    if cache.exists():
        shutil.rmtree(cache)
    (root / "note-editor/node_modules/@benrbray/prosemirror-math/dist").mkdir(exist_ok=True)


def check(root):
    pilot = (root / "build/resource/monacopilot.mjs").read_text()
    core = (root / "build/resource/monacopilot-core.mjs").read_text()
    if "@monacopilot/core" in pilot or "./monacopilot-core.mjs" not in pilot:
        raise ValueError("Monacopilot core imports were not relocated")
    for module in (pilot, core):
        if "resource://gre/modules/Timer.sys.mjs" not in module:
            raise ValueError("Monacopilot Gecko timers were not added")
    if "api.mistral.ai" in core or "codestral.mistral.ai" not in core:
        raise ValueError("Monacopilot API endpoint was not patched")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--data", type=Path, default=Path("/usr/share"))
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--clear-outputs", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.clear_outputs:
        clear_module_outputs(root)
    elif args.check:
        check(root)
    else:
        prepare(root, args.data.resolve())
