#!/usr/bin/python3
"""Build KaTeX's JavaScript API from pinned Flow source modules."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess


def build(root, dependencies, esbuild):
    if json.loads((root / "package.json").read_text())["version"] != "0.16.22":
        raise ValueError("Unexpected KaTeX source version")
    source = root / "rpm-source"
    shutil.copytree(root / "src", source / "src", dirs_exist_ok=True)
    shutil.copy2(root / "katex.js", source / "katex.js")
    # Preserve upstream preval behavior without executing a Babel macro plugin.
    for name in ("unicodeAccents", "unicodeSymbols"):
        value = subprocess.check_output([
            "node", "-e", "console.log(JSON.stringify(require(process.argv[1])))",
            str(root / "src" / f"{name}.js"),
        ], text=True)
        (source / "src" / f"{name}.js").write_text(f"module.exports = {value.strip()};\n")
    transpiled = root / "rpm-transpiled"
    subprocess.run(["node", str(Path(__file__).with_name("strip-flow.cjs")),
                    str(dependencies), str(source), str(transpiled)], check=True)
    output = root / "rpm-dist"
    output.mkdir(exist_ok=True)
    banner = '''(function(root, factory) {
    if (typeof module === "object" && module.exports) module.exports = factory();
    else if (typeof define === "function" && define.amd) define([], factory);
    else root.katex = factory();
})(this, function() { var module = {exports: {}}; var exports = module.exports;
'''
    for format_, filename in (("cjs", "katex.js"), ("esm", "katex.mjs")):
        metadata = output / f"{filename}.inputs.json"
        command = [esbuild, "rpm-transpiled/katex.js", "--bundle", "--platform=browser",
                   f"--format={format_}", "--target=firefox140", "--minify",
                   '--define:__VERSION__="0.16.22"', f"--outfile={output / filename}",
                   f"--metafile={metadata}"]
        if format_ == "cjs":
            command += [f"--banner:js={banner}", "--footer:js=return module.exports.default; });"]
        subprocess.run(command, cwd=root, env=os.environ | {"GOMAXPROCS": "1"}, check=True)
        graph = json.loads(metadata.read_text())
        if any(not name.startswith("rpm-transpiled/") for name in graph["inputs"]):
            raise ValueError("Unexpected bundled source")
        if any(item["imports"] for item in graph["outputs"].values()):
            raise ValueError("Unexpected runtime import")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("dependencies", type=Path)
    parser.add_argument("--esbuild", default="esbuild")
    args = parser.parse_args()
    build(args.root.resolve(), args.dependencies.resolve(), args.esbuild)
