#!/usr/bin/python3
"""Prepare ONNX Runtime's pinned CPU/WASM dependency sources before RPM builds."""

import argparse
import hashlib
from pathlib import Path
import shutil
import tarfile
import tempfile
import urllib.request


DEPENDENCIES = {
    "abseil_cpp", "date", "eigen", "flatbuffers", "fp16", "json",
    "microsoft_gsl", "mp11", "onnx", "protobuf", "re2", "safeint",
}


def prepare(source, output):
    records = {}
    for line in (source / "cmake/deps.txt").read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        name, url, digest = line.split(";")
        if name in DEPENDENCIES:
            if not url.startswith("https://") or len(digest) != 40:
                raise ValueError(f"Invalid upstream source record: {name}")
            records[name] = (url, digest)
    if records.keys() != DEPENDENCIES:
        raise ValueError(f"Missing dependencies: {DEPENDENCIES - records.keys()}")

    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as directory:
        root = Path(directory)
        mirror = root / "onnx-sources"
        mirror.mkdir()
        manifest = []
        for name, (url, digest) in sorted(records.items()):
            target = mirror / f"{name}.zip"
            with urllib.request.urlopen(url, timeout=120) as response, target.open("wb") as dest:
                shutil.copyfileobj(response, dest)
            with target.open("rb") as data:
                actual = hashlib.file_digest(data, "sha1").hexdigest()
            if actual != digest:
                raise ValueError(f"Upstream checksum mismatch: {name}")
            manifest.append(f"{name};{url};{digest}\n")
            print(f"Verified {name}", flush=True)
        (mirror / "sources.txt").write_text("".join(manifest))
        partial = root / "sources.tar.xz"
        with tarfile.open(partial, "w:xz") as archive:
            for path in sorted(mirror.iterdir()):
                info = archive.gettarinfo(path, f"onnx-sources/{path.name}")
                info.uid = info.gid = info.mtime = 0
                info.uname = info.gname = "root"
                info.mode = 0o644
                with path.open("rb") as data:
                    archive.addfile(info, data)
        partial.replace(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    prepare(args.source, args.output)
