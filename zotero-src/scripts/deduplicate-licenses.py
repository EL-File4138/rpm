#!/usr/bin/python3
"""Keep identical notices once, preserving every path with a relative symlink."""

import argparse
import hashlib
import os
from pathlib import Path


def deduplicate(root):
    originals = {}
    saved = 0
    for path in sorted(root.rglob('*')):
        if path.is_symlink() or not path.is_file():
            continue
        data = path.read_bytes()
        key = (len(data), hashlib.sha256(data).digest())
        candidates = originals.setdefault(key, [])
        original = next((item for item in candidates if item.read_bytes() == data), None)
        if original is None:
            candidates.append(path)
            continue
        target = os.path.relpath(original, path.parent)
        path.unlink()
        path.symlink_to(target)
        saved += len(data)
    return saved


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    print(f'Removed {deduplicate(parser.parse_args().directory)} duplicate notice bytes')
