#!/usr/bin/python3
"""Rebuild PropTypes' development UMD module from original sources."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess


def build(root, object_assign, react, esbuild):
    for directory, version in ((root, "15.8.1"), (object_assign, "4.1.1"),
                               (react / "react-is", "18.3.1")):
        if json.loads((directory / "package.json").read_text())["version"] != version:
            raise ValueError(f"Unexpected source version: {directory}")
    output = root / "rpm-dist"
    output.mkdir(exist_ok=True)
    banner = '''(function(root, factory) {
    if (typeof module === "object" && module.exports) module.exports = factory();
    else if (typeof define === "function" && define.amd) define([], factory);
    else root.PropTypes = factory();
})(this, function() { var module = {exports: {}}; var exports = module.exports;
'''
    subprocess.run([esbuild, "index.js", "--bundle", "--platform=browser",
                    "--format=cjs", "--target=firefox140", "--minify",
                    '--define:process.env.NODE_ENV="development"',
                    f"--alias:object-assign={object_assign}/index.js",
                    f"--alias:react-is={react}/react-is/index.js",
                    f"--banner:js={banner}", "--footer:js=return module.exports; });",
                    "--outfile=rpm-dist/prop-types.js", "--metafile=rpm-dist/inputs.json"],
                   cwd=root, env=os.environ | {"GOMAXPROCS": "1"}, check=True)
    graph = json.loads((output / "inputs.json").read_text())
    allowed = (root, object_assign, react / "react-is")
    for name in graph["inputs"]:
        source = (root / name).resolve()
        if not any(source.is_relative_to(directory.resolve()) for directory in allowed):
            raise ValueError(f"Unexpected bundled input: {name}")
    if any(item["imports"] for item in graph["outputs"].values()):
        raise ValueError("Unexpected runtime import")
    licenses = root / "rpm-licenses"
    licenses.mkdir(exist_ok=True)
    shutil.copyfile(object_assign / "license", licenses / "object-assign-LICENSE")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("object_assign", type=Path)
    parser.add_argument("--react", type=Path, default=Path("/usr/share/react-js"))
    parser.add_argument("--esbuild", default="esbuild")
    args = parser.parse_args()
    build(args.root.resolve(), args.object_assign.resolve(), args.react.resolve(), args.esbuild)
