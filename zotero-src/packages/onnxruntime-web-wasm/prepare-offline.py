#!/usr/bin/python3
"""Bind ONNX Runtime's FetchContent declarations to verified local sources."""

import argparse
import hashlib
from pathlib import Path
import shutil
import zipfile


def collect_licenses(root, archives):
    licenses = root / "rpm-licenses"
    licenses.mkdir(exist_ok=True)
    for name in ("LICENSE", "ThirdPartyNotices.txt"):
        shutil.copyfile(root / name, licenses / name)
    for archive in sorted(archives.glob("*.zip")):
        with zipfile.ZipFile(archive) as source:
            for member in source.infolist():
                path = Path(member.filename)
                if (not member.is_dir() and len(path.parts) == 2
                        and path.name.lower().startswith(("license", "copying", "copyright"))):
                    (licenses / f"{archive.stem}-{path.name}").write_bytes(source.read(member))
    # mp11 references Boost's license without carrying a copy. The complete
    # Boost text is included in upstream ThirdPartyNotices.txt.


def replace_once(path, old, new):
    text = path.read_text()
    if text.count(old) != 1:
        raise ValueError(f"Unexpected upstream source: {path}")
    path.write_text(text.replace(old, new))


def prepare(root, archives):
    manifest = root / "cmake/deps.txt"
    records = []
    for line in manifest.read_text().splitlines():
        if not line or line.startswith("#"):
            records.append(line)
            continue
        name, url, digest = line.split(";")
        archive = archives / f"{name}.zip"
        if archive.is_file():
            with archive.open("rb") as source:
                actual = hashlib.file_digest(source, "sha1").hexdigest()
            if actual != digest:
                raise ValueError(f"Source checksum mismatch: {name}")
        # Unselected dependencies point to absent local paths. The guard below
        # rejects their use rather than falling back to an upstream download.
        records.append(f"{name};{archive};{digest}")
    manifest.write_text("\n".join(records) + "\n")
    collect_licenses(root, archives)
    replace_once(
        root / "cmake/external/helper_functions.cmake",
        '    message(STATUS "Fetch ${contentName} from ${ARG_URL}")',
        '    if(NOT IS_ABSOLUTE "${ARG_URL}" OR NOT EXISTS "${ARG_URL}")\n'
        '      message(FATAL_ERROR "Missing offline source for ${contentName}: ${ARG_URL}")\n'
        '    endif()\n'
        '    message(STATUS "Use local source for ${contentName}: ${ARG_URL}")',
    )
    # Honor the existing LTO switch for WASM too. This lets builders bound link
    # memory without changing the operators or execution providers compiled in.
    replace_once(
        root / "cmake/adjust_global_compile_flags.cmake",
        '  if (NOT CMAKE_BUILD_TYPE STREQUAL "Debug")',
        '  if (onnxruntime_ENABLE_LTO AND NOT CMAKE_BUILD_TYPE STREQUAL "Debug")',
    )
    replace_once(root / "cmake/onnxruntime_webassembly.cmake", "--closure 1", "--closure 0")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("archives", type=Path)
    args = parser.parse_args()
    prepare(args.source.resolve(), args.archives.resolve())
