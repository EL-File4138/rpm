#!/usr/bin/python3
"""Build Monacopilot JavaScript from its TypeScript release sources."""

import argparse
import json
import os
from pathlib import Path
import subprocess


def build(root, esbuild):
    for package in ("core", "monacopilot"):
        source = root / "packages" / package / "src/index.ts"
        directory = root / "dist" / package
        directory.mkdir(parents=True, exist_ok=True)
        variants = [("cjs", "index.js"), ("esm", "index.mjs")]
        if package == "monacopilot":
            variants.append(("iife", "index.global.js"))
        for format_, filename in variants:
            metadata = directory / (filename + ".inputs.json")
            command = [esbuild, str(source), "--bundle", "--target=es2021",
                       "--platform=browser", "--minify", f"--format={format_}",
                       f"--outfile={directory / filename}", f"--metafile={metadata}"]
            external_core = package == "monacopilot" and format_ == "esm"
            if external_core:
                command.append("--external:@monacopilot/core")
            else:
                command.append(f"--alias:@monacopilot/core={root}/packages/core/src/index.ts")
            if format_ == "iife":
                command.append("--global-name=monacopilot")
            subprocess.run(command, cwd=root, env=os.environ | {"GOMAXPROCS": "1"}, check=True)
            graph = json.loads(metadata.read_text())
            for name in graph["inputs"]:
                if not name.startswith(("packages/core/src/", "packages/monacopilot/src/")):
                    raise ValueError(f"Unexpected bundled input: {name}")
            for output in graph["outputs"].values():
                for dependency in output["imports"]:
                    if not external_core or dependency["path"] != "@monacopilot/core":
                        raise ValueError(f"Unexpected bundle import: {dependency}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--esbuild", default="esbuild")
    args = parser.parse_args()
    build(args.root.resolve(), args.esbuild)
