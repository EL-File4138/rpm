#!/usr/bin/python3
"""Build Autosuggest's standalone module from original JavaScript sources."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess


def build(root, dependencies, esbuild):
    aliases = {
        "react-themeable": dependencies / "react-themeable/src/index.js",
        "section-iterator": dependencies / "section-iterator/index.js",
        "shallow-equal/arrays": dependencies / "shallow-equal/src/arrays.js",
        "prop-types": dependencies / "prop-types/index.js",
        "object-assign": dependencies / "object-assign/index.js",
    }
    banner = '''(function(root, factory) {
    if (typeof exports === "object" && typeof module === "object") {
        module.exports = factory(require("React"));
    } else if (typeof define === "function" && define.amd) {
        define(["React"], factory);
    } else if (typeof exports === "object") {
        exports.Autosuggest = factory(require("React"));
    } else {
        root.Autosuggest = factory(root.React);
    }
})(this, function(React) {
    var module = { exports: {} };
    var exports = module.exports;
    function require(name) {
        if (name === "react") return React;
        throw new Error("Unexpected Autosuggest import: " + name);
    }
'''
    output = root / "rpm-dist"
    output.mkdir(exist_ok=True)
    metadata = output / "inputs.json"
    command = [esbuild, "src/index.js", "--bundle", "--platform=browser",
               "--format=cjs", "--target=firefox140", "--loader:.js=jsx",
               "--define:process.env.NODE_ENV=\"production\"", "--external:react",
               "--minify", f"--banner:js={banner}",
               "--footer:js=return module.exports; });",
               f"--outfile={output}/autosuggest.min.js", f"--metafile={metadata}"]
    command.extend(f"--alias:{name}={path}" for name, path in aliases.items())
    subprocess.run(command, cwd=root, env=os.environ | {"GOMAXPROCS": "1"}, check=True)
    graph = json.loads(metadata.read_text())
    source_roots = [root / "src"] + [
        (dependencies / name).resolve() for name in
        ("react-themeable", "section-iterator", "shallow-equal", "prop-types", "object-assign")
    ]
    for name in graph["inputs"]:
        path = (root / name).resolve()
        if not any(path.is_relative_to(source) for source in source_roots):
            raise ValueError(f"Unexpected bundled source: {name}")
    for item in graph["outputs"].values():
        if any(i["path"] != "react" or not i["external"] for i in item["imports"]):
            raise ValueError("Unexpected external imports")
    licenses = root / "rpm-licenses"
    licenses.mkdir(exist_ok=True)
    for name, filename in (("prop-types", "LICENSE"), ("object-assign", "license"),
                           ("shallow-equal", "LICENSE"), ("section-iterator", "LICENSE")):
        shutil.copyfile(dependencies / name / filename, licenses / f"{name}-LICENSE")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("dependencies", type=Path)
    parser.add_argument("--esbuild", default="esbuild")
    args = parser.parse_args()
    build(args.root.resolve(), args.dependencies.resolve(), args.esbuild)
