#!/usr/bin/python3
"""Build React Virtualized with Zotero's Gecko and React 18 compatibility changes."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess


def replace(path, old, new):
    contents = path.read_text()
    if contents.count(old) != 1:
        raise ValueError(f"Expected one patch location in {path}: {old}")
    path.write_text(contents.replace(old, new))


def build(root, dependencies, build_dependencies, esbuild):
    output = root / "rpm-dist"
    source = root / "rpm-source"
    if source.exists():
        shutil.rmtree(source)
    shutil.copytree(root / "source", source)
    view = source / "Collection/CollectionView.js"
    replace(view, "import * as React from 'react';",
            "import * as React from 'react';\nimport {flushSync} from 'react-dom';")
    replace(view, """      this.setState({
        isScrolling: true,
        scrollLeft,
        scrollPositionChangeReason,
        scrollTop,
      });""", """      flushSync(() => this.setState({
        isScrolling: true,
        scrollLeft,
        scrollPositionChangeReason,
        scrollTop,
      }));""")
    scrollbar = root / "rpm-scrollbarSize.ts"
    shutil.copyfile(dependencies / "dom-helpers/src/scrollbarSize.ts", scrollbar)
    replace(scrollbar, "'./canUseDOM'", json.dumps(str(dependencies / "dom-helpers/src/canUseDOM.ts")))
    replace(scrollbar, "document.createElement('div')",
            "document.createElementNS('http://www.w3.org/1999/xhtml', 'div')")
    replace(scrollbar, "document.body.appendChild", "document.documentElement.appendChild")
    replace(scrollbar, "document.body.removeChild", "document.documentElement.removeChild")
    env = os.environ | {"GOMAXPROCS": "1", "UV_THREADPOOL_SIZE": "1",
                        "NODE_OPTIONS": "--max-old-space-size=1400"}
    transpiled = root / "rpm-transpiled"
    if transpiled.exists():
        shutil.rmtree(transpiled)
    subprocess.run(["node", str(Path(__file__).with_name("strip-flow.cjs")),
                    str(build_dependencies), str(source), str(transpiled)], env=env, check=True)
    output.mkdir(exist_ok=True)
    banner = '''/* Zotero source compatibility patches applied. */
(function(root, factory) {
    if (typeof exports === "object" && typeof module === "object") {
        module.exports = factory(require("react"), require("react-dom"));
    } else if (typeof define === "function" && define.amd) {
        define(["react", "react-dom"], factory);
    } else {
        root.ReactVirtualized = factory(root.React, root.ReactDOM);
    }
})(this, function(React, ReactDOM) {
    var module = { exports: {} };
    var exports = module.exports;
    function require(name) {
        if (name === "react") return React;
        if (name === "react-dom") return ReactDOM;
        throw new Error("Unexpected React Virtualized import: " + name);
    }
'''
    aliases = {
        "clsx": dependencies / "clsx/src/index.js",
        "react-lifecycles-compat": dependencies / "react-lifecycles-compat/index.js",
        "dom-helpers/scrollbarSize": scrollbar,
        "prop-types": dependencies / "prop-types/index.js",
    }
    metadata = output / "inputs.json"
    command = [esbuild, str(transpiled / "index.js"), "--bundle", "--format=cjs",
               "--platform=browser", "--target=firefox140", "--loader:.js=jsx",
               "--tsconfig-raw={}",
               "--define:process.env.NODE_ENV=\"production\"", "--external:react",
               "--external:react-dom", "--minify", f"--banner:js={banner}",
               "--footer:js=return module.exports; });", f"--metafile={metadata}",
               f"--outfile={output}/react-virtualized.js"]
    command.extend(f"--alias:{name}={path}" for name, path in aliases.items())
    subprocess.run(command, cwd=root, env=env, check=True)
    graph = json.loads(metadata.read_text())
    allowed = [transpiled] + [(dependencies / name).resolve() for name in
                             ("clsx", "react-lifecycles-compat", "dom-helpers", "prop-types")]
    for name in graph["inputs"]:
        path = (root / name).resolve()
        if path != scrollbar and not any(path.is_relative_to(base) for base in allowed):
            raise ValueError(f"Unexpected source: {name}")
    for entry in graph["outputs"].values():
        if any(i["path"] not in ("react", "react-dom") or not i["external"] for i in entry["imports"]):
            raise ValueError("Unexpected external imports")
    licenses = root / "rpm-licenses"
    licenses.mkdir(exist_ok=True)
    for name, filename in (("clsx", "license"), ("react-lifecycles-compat", "LICENSE.md"),
                           ("dom-helpers", "LICENSE"), ("prop-types", "LICENSE")):
        shutil.copyfile(dependencies / name / filename, licenses / f"{name}-LICENSE")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("dependencies", type=Path)
    parser.add_argument("build_dependencies", type=Path)
    parser.add_argument("--esbuild", default="esbuild")
    args = parser.parse_args()
    build(args.root.resolve(), args.dependencies.resolve(), args.build_dependencies.resolve(), args.esbuild)
