#!/usr/bin/python3
"""Retain notices from the actual TeX inputs used by KaTeX's font pipeline."""

import argparse
from pathlib import Path
import subprocess


def pfb_notice(data):
    if data[:2] != b"\x80\x01" or len(data) < 6:
        raise ValueError("Expected a PFB ASCII record")
    size = int.from_bytes(data[2:6], "little")
    if len(data) < 6 + size:
        raise ValueError("Truncated PFB ASCII record")
    header, separator, _ = data[6:6 + size].partition(b"%%EndComments")
    if not separator or b"%Copyright:" not in header or b"Open Font License" not in header:
        raise ValueError("Missing Euler font copyright/license notice")
    return header + separator + b"\n"


def collect(destination):
    def locate(name):
        filename = subprocess.check_output(["kpsewhich", name], text=True).strip()
        if not filename:
            raise ValueError(f"Missing TeX input: {name}")
        return Path(filename)

    cm = locate("cmr10.mf").read_bytes()
    euler = {name: pfb_notice(locate(name + ".pfb").read_bytes())
             for name in ("eufm10", "eufb10")}
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "cmr10.mf").write_bytes(cm)
    for name, notice in euler.items():
        (destination / (name + "-notice.txt")).write_bytes(notice)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    collect(parser.parse_args().destination)
