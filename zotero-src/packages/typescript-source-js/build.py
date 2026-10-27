#!/usr/bin/python3
"""Bundle TypeScript 5.0.2 from its original TypeScript sources."""

import argparse
import json
import os
from pathlib import Path
import subprocess


def build(root, esbuild, source_version="5.0.2"):
    package = json.loads((root / "package.json").read_text())
    if source_version not in ("5.0.2", "5.4.0") or package["version"] != source_version:
        raise ValueError(f"Expected TypeScript {source_version} source")
    environment = os.environ | {"GOMAXPROCS": "1", "UV_THREADPOOL_SIZE": "1"}
    subprocess.run(["node", "scripts/processDiagnosticMessages.mjs",
                    "src/compiler/diagnosticMessages.json"],
                   cwd=root, env=environment, check=True)
    output = root / "dist"
    output.mkdir(exist_ok=True)
    copyright_ = (root / "scripts/CopyrightNotice.txt").read_text()
    metadata = output / "typescript.inputs.json"
    # Match upstream createBundler(exportIsTsObject), without an npm binary wrapper.
    subprocess.run([esbuild, "src/typescript/typescript.ts", "--bundle",
                    "--platform=node", "--target=es2018", "--format=iife",
                    "--global-name=ts", "--packages=external", "--define:require=$$require",
                    f"--banner:js={copyright_}",
                    "--footer:js=if (typeof module !== 'undefined' && module.exports) { module.exports = ts; }",
                    "--outfile=dist/typescript.js", f"--metafile={metadata}"],
                   cwd=root, env=environment, check=True)
    graph = json.loads(metadata.read_text())
    if any(not name.startswith("src/") for name in graph["inputs"]):
        raise ValueError("TypeScript bundle contains a non-source input")
    path = output / "typescript.js"
    path.write_text(path.read_text().replace("$$require", "  require"))
    # The upstream library manifest uses JSON comments; use its own parser.
    libraries = json.loads(subprocess.check_output([
        "node", "-e",
        "const ts=require(process.argv[1]);"
        "const result=ts.readConfigFile(process.argv[2],ts.sys.readFile);"
        "if(result.error)throw new Error(result.error.messageText);"
        "process.stdout.write(JSON.stringify(result.config));",
        str(path), str(root / "src/lib/libs.json"),
    ], text=True))
    for name in libraries["libs"]:
        filename = libraries.get("paths", {}).get(name) or f"lib.{name}.d.ts"
        contents = copyright_
        for fragment in ("header.d.ts", f"{name}.d.ts"):
            contents += "\n" + (root / "src/lib" / fragment).read_text()
        (output / filename).write_text(contents)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--esbuild", default="esbuild")
    parser.add_argument("--source-version", choices=("5.0.2", "5.4.0"), default="5.0.2")
    args = parser.parse_args()
    build(args.root.resolve(), args.esbuild, args.source_version)
