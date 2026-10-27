#!/usr/bin/python3
"""Build Pako's browser bundle from its original JavaScript modules."""

import argparse
import json
import os
from pathlib import Path
import subprocess


def build(root, esbuild):
    if json.loads((root / "package.json").read_text())["version"] != "2.1.0":
        raise ValueError("Unexpected Pako source version")
    output = root / "rpm-dist"
    output.mkdir(exist_ok=True)
    banner = '''(function(root, factory) {
    if (typeof module === "object" && module.exports) module.exports = factory();
    else if (typeof define === "function" && define.amd) define([], factory);
    else root.pako = factory();
})(this, function() { var module = {exports: {}}; var exports = module.exports;
'''
    subprocess.run([esbuild, "index.js", "--bundle", "--platform=browser",
                    "--format=cjs", "--target=firefox140", "--minify",
                    f"--banner:js={banner}", "--footer:js=return module.exports; });",
                    "--outfile=rpm-dist/pako.min.js", "--metafile=rpm-dist/inputs.json"],
                   cwd=root, env=os.environ | {"GOMAXPROCS": "1"}, check=True)
    graph = json.loads((output / "inputs.json").read_text())
    if any(name != "index.js" and not name.startswith("lib/") for name in graph["inputs"]):
        raise ValueError("Unexpected bundled source")
    if any(item["imports"] for item in graph["outputs"].values()):
        raise ValueError("Unexpected runtime import")
    source = (root / "lib/zlib/deflate.js").read_text()
    notice = source[source.index("// (C)"):source.index("\n\nconst ")]
    (root / "ZLIB-LICENSE").write_text(notice + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--esbuild", default="esbuild")
    args = parser.parse_args()
    build(args.root.resolve(), args.esbuild)
