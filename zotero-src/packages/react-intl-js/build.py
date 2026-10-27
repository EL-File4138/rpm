#!/usr/bin/python3
"""Build React Intl from TypeScript and regenerate its ICU parser grammar."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess


def build(root, sources, tools, react, esbuild):
    if json.loads((root / "package.json").read_text())["version"] != "3.12.1":
        raise ValueError("Expected React Intl 3.12.1")
    parser = root / "rpm-parser"
    shutil.copytree(sources / "intl-messageformat-parser", parser, dirs_exist_ok=True)
    subprocess.run(["node", str(Path(__file__).with_name("generate-parser.cjs")),
                    str(parser), str(tools)], check=True)
    aliases = {
        "intl-messageformat": sources / "intl-messageformat/src/index.ts",
        "intl-messageformat-parser": parser / "src/index.ts",
        "intl-format-cache": sources / "intl-format-cache/index.ts",
        # React Intl uses only invariant; avoid unrelated polyfill data exports.
        "@formatjs/intl-utils": sources / "intl-utils/src/invariant.ts",
        "hoist-non-react-statics": sources / "hoist-non-react-statics/src/index.js",
        "shallow-equal/objects": sources / "shallow-equal/src/objects.js",
        "react-is": react / "react-is/index.js",
    }
    for name, version in (("intl-messageformat", "7.8.4"),
                          ("intl-messageformat-parser", "3.6.4"),
                          ("intl-format-cache", "4.3.1"), ("intl-utils", "2.3.0"),
                          ("hoist-non-react-statics", "3.3.2"),
                          ("shallow-equal", "1.2.1")):
        if json.loads((sources / name / "package.json").read_text())["version"] != version:
            raise ValueError(f"Unexpected source version: {name}")
    output = root / "dist"
    output.mkdir(exist_ok=True)
    metadata = output / "inputs.json"
    inner = output / "react-intl.cjs"
    command = [esbuild, str(root / "src/index.ts"), "--bundle", "--platform=browser",
               "--format=cjs", "--target=firefox140", "--minify", "--tsconfig-raw={}",
               '--define:process.env.NODE_ENV="production"', "--external:react",
               f"--outfile={inner}", f"--metafile={metadata}"]
    command.extend(f"--alias:{name}={path}" for name, path in aliases.items())
    subprocess.run(command, cwd=root, env=os.environ | {"GOMAXPROCS": "1"}, check=True)
    allowed = [root / "src", parser / "src", react / "react-is"]
    allowed.extend((sources / name).resolve() for name in (
        "intl-messageformat", "intl-format-cache", "intl-utils",
        "hoist-non-react-statics", "shallow-equal"))
    graph = json.loads(metadata.read_text())
    for name in graph["inputs"]:
        path = (root / name).resolve()
        if not any(path.is_relative_to(directory.resolve()) for directory in allowed):
            raise ValueError(f"Unexpected bundled input: {name}")
    for record in graph["outputs"].values():
        if any(item["path"] != "react" for item in record["imports"]):
            raise ValueError("Unexpected external dependency")
    wrapper = '''(function(root, factory) {
if (typeof exports === 'object' && typeof module === 'object') module.exports = factory(require('react'));
else if (typeof define === 'function' && define.amd) define(['react'], factory);
else root.ReactIntl = factory(root.React);
})(typeof globalThis !== 'undefined' ? globalThis : this, function(React) {
var module = { exports: {} }, exports = module.exports;
function require(name) { if (name === 'react') return React; throw new Error(name); }
'''
    (output / "react-intl.min.js").write_text(wrapper + inner.read_text()
                                             + '\nreturn module.exports;\n});\n')
    licenses = root / "rpm-licenses"
    licenses.mkdir(exist_ok=True)
    for name in ("intl-messageformat", "intl-messageformat-parser", "intl-format-cache",
                 "intl-utils", "hoist-non-react-statics", "shallow-equal"):
        directory = sources / name
        files = [path for path in directory.iterdir()
                 if path.is_file() and path.name.lower().startswith(("license", "copying"))]
        if not files:
            raise ValueError(f"Missing license: {name}")
        for path in files:
            shutil.copy2(path, licenses / f"{name}-{path.name}")
    shutil.copy2(react / "react-is/LICENSE", licenses / "react-is-LICENSE")


if __name__ == "__main__":
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument("root", type=Path)
    arg.add_argument("sources", type=Path)
    arg.add_argument("tools", type=Path)
    arg.add_argument("react", type=Path)
    arg.add_argument("--esbuild", default="esbuild")
    args = arg.parse_args()
    build(args.root.resolve(), args.sources.resolve(), args.tools.resolve(),
          args.react.resolve(), args.esbuild)
