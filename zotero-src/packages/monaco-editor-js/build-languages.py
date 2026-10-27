#!/usr/bin/python3
"""Build Monaco's AMD language modules with original dependency sources."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess


PACKAGES = {
    "vscode-css-languageservice": ("5.4.1", "src/cssLanguageService.ts"),
    "vscode-html-languageservice": ("4.2.4", "src/htmlLanguageService.ts"),
    "vscode-json-languageservice": ("4.2.1", "src/jsonLanguageService.ts"),
    "vscode-languageserver-textdocument": ("1.0.4", "src/main.ts"),
    "vscode-languageserver-types": ("3.16.0", "src/main.ts"),
    "vscode-uri": ("3.0.3", "src/index.ts"),
    "jsonc-parser": ("3.0.0", "src/main.ts"),
}


def build(root, dependencies, typescript, output, esbuild, vscode):
    if json.loads((root / "package.json").read_text())["version"] != "0.47.0":
        raise ValueError("Expected Monaco 0.47.0 source")
    if "5.0.2" not in subprocess.check_output([
        "node", "-e", "process.stdout.write(require(process.argv[1]).version)",
        str(typescript / "typescript.js"),
    ], text=True):
        raise ValueError("Expected source-built TypeScript 5.0.2")
    lib = root / "src/language/typescript/lib"
    lib.mkdir(exist_ok=True)
    original = (root / "build/importTypescript.ts").read_text()
    exports = re.search(r"// MONACOCHANGE\n(export var createClassifier.*?)(?:// END MONACOCHANGE)", original, re.S)
    if not exports:
        raise ValueError("Unknown upstream TypeScript embedding recipe")
    (lib / "typescriptServices.js").write_text(
        "var require = undefined;\nvar module = { exports: {} };\n"
        + (typescript / "typescript.js").read_text() + "\n" + exports[1])
    (lib / "typescriptServicesMetadata.ts").write_text('export const typescriptVersion = "5.0.2";\n')
    libraries = sorted(typescript.glob("lib*.d.ts"))
    if not libraries:
        raise ValueError("Missing source-built standard library declarations")
    (lib / "lib.ts").write_text("export const libFileMap: Record<string, string> = {};\n" + "".join(
        f"libFileMap[{json.dumps(p.name)}] = {json.dumps(p.read_text())};\n" for p in libraries))
    (lib / "lib.index.ts").write_text("export const libFileSet: Record<string, boolean> = {};\n" + "".join(
        f"libFileSet[{json.dumps(p.name)}] = true;\n" for p in libraries))
    aliases = {
        "monaco-editor-core": root / "src/fillers/monaco-editor-core-amd.ts",
        "vscode-nls": root / "build/fillers/vscode-nls.ts",
        # The matching VS Code tree contains the original browser path implementation.
        "path": vscode / "src/vs/base/common/path.ts",
        "vs/base/common/process": vscode / "src/vs/base/common/process.ts",
        "vs/base/common/platform": vscode / "src/vs/base/common/platform.ts",
        "vs/nls": vscode / "src/vs/nls.ts",
    }
    allowed = [root / "src", root / "build/fillers", vscode / "src"]
    licenses = output.parent / "rpm-licenses"
    licenses.mkdir(exist_ok=True)
    for package, (version, entry) in PACKAGES.items():
        source = (dependencies / package).resolve()
        if json.loads((source / "package.json").read_text())["version"] != version:
            raise ValueError(f"Unexpected {package} source version")
        aliases[package] = source / entry
        allowed.append(source / "src")
        license_files = [p for p in source.iterdir() if p.is_file() and p.name.lower() in ("license", "license.txt", "license.md")]
        if not license_files:
            # Language-server subpackages share the repository-root license.
            license_files = [p for p in source.parent.iterdir() if p.is_file() and p.name.lower() in ("license", "license.txt", "license.md")]
        if not license_files:
            raise ValueError(f"Missing {package} license")
        shutil.copyfile(license_files[0], licenses / f"{package}-LICENSE")
    entries = []
    for language, mode, worker in (("css", "cssMode", "cssWorker"), ("html", "htmlMode", "htmlWorker"),
                                  ("json", "jsonMode", "jsonWorker"), ("typescript", "tsMode", "tsWorker")):
        for name in ("monaco.contribution", mode, worker):
            entries.append((f"language/{language}/{name}", name == "monaco.contribution", name == mode))
    entries.append(("basic-languages/monaco.contribution", True, False))
    for source in sorted((root / "src/basic-languages").glob("*/*.contribution.ts")):
        language = source.parent.name
        entries.append((f"basic-languages/{language}/{language}", False, False))
    for entry, api, mode in entries:
        target = output / "vs" / f"{entry}.js"
        target.parent.mkdir(parents=True, exist_ok=True)
        metadata = target.with_suffix(".inputs.json")
        dependencies_ = ["require"] + (["vs/editor/editor.api"] if api else [])
        command = [esbuild, str(root / "src" / f"{entry}.ts"), "--bundle", "--platform=browser",
                   "--target=es2022", "--format=iife", "--global-name=moduleExports", "--define:AMD=true",
                   "--tsconfig-raw={}", "--external:vs/editor/editor.api", "--external:*/monaco.contribution",
                   f"--banner:js=define({json.dumps('vs/' + entry)}, {json.dumps(dependencies_)}, (require)=>{{",
                   "--footer:js=return moduleExports;\n});", f"--outfile={target}", f"--metafile={metadata}"]
        command += [f"--alias:{name}={path}" for name, path in aliases.items()]
        subprocess.run(command, cwd=root, env=os.environ | {"GOMAXPROCS": "1"}, check=True)
        graph = json.loads(metadata.read_text())
        for name in graph["inputs"]:
            source = (root / name).resolve()
            if not any(source.is_relative_to(directory.resolve()) for directory in allowed):
                raise ValueError(f"Unexpected bundled language input: {name}")
        for item in graph["outputs"].values():
            for dependency in item["imports"]:
                if dependency["path"] != "vs/editor/editor.api" and not dependency["path"].endswith("/monaco.contribution"):
                    raise ValueError(f"Unexpected language import: {dependency}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "dependencies", "typescript", "output"):
        parser.add_argument(name, type=Path)
    parser.add_argument("--esbuild", default="esbuild")
    parser.add_argument("--vscode", required=True, type=Path)
    args = parser.parse_args()
    build(*(getattr(args, name).resolve() for name in ("root", "dependencies", "typescript", "output")),
          args.esbuild, args.vscode.resolve())
