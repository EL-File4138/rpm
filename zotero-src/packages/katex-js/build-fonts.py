#!/usr/bin/python3
"""Rebuild KaTeX font outlines and renderer metrics with upstream tools."""

import argparse
import json
from pathlib import Path
import shutil
import subprocess


def build(root):
    source = root / "src/fonts"
    config = (source / "default.cfg").read_text()
    for variable, filename in (("TETEXENCODING", "aae443f0.enc"),
                               ("BASEENCODING", "tex256.enc")):
        path = Path(subprocess.check_output(["kpsewhich", filename], text=True).strip())
        if not path.is_file():
            raise ValueError(f"Missing TeX encoding {filename}")
        lines = config.splitlines()
        config = "\n".join(f"{variable}={path.parent}/" if line.startswith(variable + "=")
                           else line for line in lines) + "\n"
    (source / "custom.cfg").write_text(config)
    makefile = source / "Makefile"
    text = makefile.read_text()
    old = "@for file in `ls ff/*.ff"
    if text.count(old) != 1:
        raise ValueError("Unexpected upstream font build loop")
    makefile.write_text(text.replace(old, "@set -e; for file in `ls ff/*.ff"))
    subprocess.run(["make", "-j1", "all"], cwd=source, check=True)
    output = root / "fonts"
    output.mkdir(exist_ok=True)
    for format_ in ("ttf", "woff", "woff2"):
        files = sorted((source / format_).glob(f"KaTeX_*.{format_}"))
        if len(files) != 20:
            raise ValueError(f"Expected 20 {format_} fonts, found {len(files)}")
        for filename in files:
            shutil.copy2(filename, output / filename.name)
    metrics = root / "src/metrics"
    value = subprocess.check_output(["perl", "mapping.pl"], cwd=metrics)
    families = set(json.loads(value))
    for script in ("extract_tfms.py", "extract_ttfs.py"):
        value = subprocess.check_output(["python3", script], input=value, cwd=metrics)
    data = json.loads(value)
    if set(data) != families or "Main-Regular" not in data:
        raise ValueError("Unexpected generated font metrics")
    value = subprocess.check_output(["python3", "format_json.py", "--width"],
                                    input=value, cwd=metrics)
    (root / "src/fontMetricsData.js").write_bytes(value)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    build(parser.parse_args().root.resolve())
