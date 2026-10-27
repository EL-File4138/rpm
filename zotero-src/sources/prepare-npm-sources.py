#!/usr/bin/python3
"""Fetch lockfile archives before RPM execution; preserve URL and integrity pins.

The result is an input archive collection, not a source-compliance assertion.
Packages containing generated code or executables still require replacement
or rebuilding by their consuming RPM recipe.
"""

import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile
import time
import urllib.request


def integrity_matches(data, integrity):
    tokens = [token.split("-", 1) for token in integrity.split()]
    for algorithm in ("sha512", "sha384", "sha256", "sha1"):
        expected = [value for name, value in tokens if name == algorithm]
        if expected:
            actual = base64.b64encode(hashlib.new(algorithm, data).digest()).decode()
            return actual in expected
    raise ValueError(f"Unsupported integrity algorithm: {integrity}")


def download(record, directory):
    path = directory / record["file"]
    if path.exists():
        data = path.read_bytes()
    else:
        for attempt in range(3):
            try:
                with urllib.request.urlopen(record["url"], timeout=90) as response:
                    data = response.read()
                break
            except OSError:
                if attempt == 2:
                    raise
                time.sleep(attempt + 1)
    for pin in record["integrities"]:
        if not integrity_matches(data, pin):
            raise ValueError(f"Checksum mismatch: {record['resolved']}")
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        if not any(Path(member.name).name == "package.json" for member in archive):
            raise ValueError(f"Missing package manifest: {record['resolved']}")
    record["integrity"] = "sha512-" + base64.b64encode(hashlib.sha512(data).digest()).decode()
    record["sha256"] = hashlib.sha256(data).hexdigest()
    if not path.exists():
        partial = path.with_suffix(".partial")
        partial.write_bytes(data)
        partial.replace(path)
    return record


def prepare(locks, directory, jobs, output=None):
    directory.mkdir(parents=True, exist_ok=True)
    records = {}
    for lock in locks:
        data = json.loads(lock.read_text())
        if data.get("lockfileVersion", 0) < 2:
            raise ValueError(f"Unsupported lockfile version: {lock}")
        for package in data["packages"].values():
            resolved = package.get("resolved")
            if not resolved or package.get("link"):
                continue
            url = resolved
            if resolved.startswith("https://registry.npmjs.org/"):
                if not package.get("integrity"):
                    raise ValueError(f"Missing registry checksum: {resolved}")
            else:
                match = re.fullmatch(r"git\+ssh://git@github.com/([\w.-]+/[\w.-]+)\.git#([0-9a-f]{40})", resolved)
                tarball = re.fullmatch(r"https://codeload\.github\.com/([\w.-]+/[\w.-]+)/tar\.gz/([0-9a-f]{40})", resolved)
                if match:
                    url = f"https://codeload.github.com/{match[1]}/tar.gz/{match[2]}"
                elif not tarball or not package.get("integrity"):
                    raise ValueError(f"Unsupported package origin: {resolved}")
            record = records.setdefault(resolved, {
                "resolved": resolved, "url": url,
                "file": hashlib.sha256(resolved.encode()).hexdigest() + ".tgz",
                "integrities": [],
            })
            if package.get("integrity") and package["integrity"] not in record["integrities"]:
                record["integrities"].append(package["integrity"])
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        result = list(pool.map(lambda record: download(record, directory), records.values()))
    result.sort(key=lambda record: record["resolved"])
    (directory / "sources.json").write_text(json.dumps(result, indent=2) + "\n")
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        partial = output.with_suffix(output.suffix + ".partial")

        def normalize(member):
            member.uid = member.gid = member.mtime = 0
            member.uname = member.gname = ""
            member.mode = 0o644
            return member

        with tarfile.open(partial, "w:xz", preset=1) as archive:
            for filename in ["sources.json", *sorted(record["file"] for record in result)]:
                archive.add(directory / filename, arcname=f"npm-sources/{filename}",
                            recursive=False, filter=normalize)
        partial.replace(output)
    print(f"Verified {len(result)} dependency archives in {directory}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--output", type=Path, help="Write a reproducible RPM source archive")
    parser.add_argument("lockfiles", nargs="+", type=Path)
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    prepare(args.lockfiles, args.directory.resolve(), args.jobs, args.output)
