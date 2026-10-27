#!/usr/bin/python3
"""Build Codicons from original SVG artwork and the editor's source codepoints."""

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess


def build(icons, editor, output, dependencies):
    mapping = json.loads((icons / "src/template/mapping.json").read_text())
    artwork = {path.stem: path for path in (icons / "src/icons").glob("*.svg")}
    source = editor / "src/vs/base/common/codicons.ts"
    registrations = re.findall(r"register\('([^']+)', (0x[0-9a-f]+)\)", source.read_text())
    if not registrations:
        raise ValueError("Missing editor icon registrations")
    glyphs = {}
    for name, codepoint in registrations:
        number = int(codepoint, 16)
        candidates = [name] + [alias for alias, value in mapping.items() if value == number]
        original = next((artwork[alias] for alias in candidates if alias in artwork), None)
        if original is None:
            raise ValueError(f"No original SVG for editor icon {name} at {codepoint}")
        # Aliases share a codepoint; prefer the explicitly registered artwork.
        if number not in glyphs or name in artwork:
            glyphs[number] = original
    staging = icons / "rpm-svg-sources"
    staging.mkdir(parents=True, exist_ok=True)
    names = {}
    for codepoint, original in sorted(glyphs.items()):
        name = f"icon-{codepoint:04x}"
        shutil.copyfile(original, staging / f"{name}.svg")
        names[name] = codepoint
    codepoints = staging / "codepoints.json"
    codepoints.write_text(json.dumps(names) + "\n")
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["node", str(Path(__file__).with_suffix(".cjs")), str(icons),
                    str(staging), str(output.parent), str(dependencies), str(codepoints)], check=True)
    output.with_suffix(".inputs.json").write_text(json.dumps({
        "codepointSource": "src/vs/base/common/codicons.ts",
        "glyphs": {str(codepoint): str(path.relative_to(icons)) for codepoint, path in sorted(glyphs.items())},
    }, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("icons", type=Path)
    parser.add_argument("editor", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("dependencies", type=Path)
    args = parser.parse_args()
    build(args.icons.resolve(), args.editor.resolve(), args.output.resolve(), args.dependencies.resolve())
