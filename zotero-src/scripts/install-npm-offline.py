#!/usr/bin/python3
"""Install verified local npm archives without lifecycle scripts or network."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


def install(root, archives):
    sources = json.loads((archives / "sources.json").read_text())
    records = {}
    for record in sources:
        filename = record["file"]
        if Path(filename).name != filename or not filename.endswith(".tgz"):
            raise ValueError(f"Invalid archive filename: {filename}")
        if record["resolved"] in records:
            raise ValueError(f"Duplicate source record: {record['resolved']}")
        records[record["resolved"]] = record
    path = root / "package-lock.json"
    lock = json.loads(path.read_text())
    if lock.get("lockfileVersion", 0) < 2:
        raise ValueError("A package-lock.json with version >= 2 is required")
    manifest_path = root / "package.json"
    manifest = json.loads(manifest_path.read_text())
    # Git and direct URL specifiers are checked by npm even during ci. Relocate
    # the root declaration as well, preserving the archive's locked commit.
    for section in ("dependencies", "devDependencies", "optionalDependencies"):
        for name, specifier in manifest.get(section, {}).items():
            package = lock["packages"].get(f"node_modules/{name}", {})
            resolved = package.get("resolved", "")
            if resolved.startswith(("git+", "https://codeload.github.com/")):
                if lock["packages"][""].get(section, {}).get(name) != specifier:
                    raise ValueError(f"Manifest and lockfile disagree: {name}")
                local = (archives / records[resolved]["file"]).as_uri()
                manifest[section][name] = local
                lock["packages"][""][section][name] = local
    verified = set()
    for package in lock["packages"].values():
        resolved = package.get("resolved")
        if not resolved or package.get("link"):
            continue
        record = records[resolved]
        archive = archives / record["file"]
        if archive not in verified:
            with archive.open("rb") as source:
                digest = hashlib.file_digest(source, "sha256").hexdigest()
            if digest != record["sha256"]:
                raise ValueError(f"Checksum mismatch: {archive}")
            verified.add(archive)
        if package.get("integrity") and package["integrity"] not in record["integrities"]:
            raise ValueError(f"Lockfile pin not present in source manifest: {resolved}")
        package["resolved"] = archive.as_uri()
        package["integrity"] = record["integrity"]
    # npm >= 7 uses packages; remove the redundant v2 dependency graph so it
    # cannot retain network URLs after relocation.
    lock.pop("dependencies", None)
    lock["lockfileVersion"] = 3
    path.write_text(json.dumps(lock, indent=2) + "\n")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    environment = os.environ | {
        "npm_config_offline": "true",
        "npm_config_ignore_scripts": "true",
        "npm_config_audit": "false",
        "npm_config_fund": "false",
        "npm_config_update_notifier": "false",
        "npm_config_cache": str(archives.parent / "npm-cache-offline"),
    }
    subprocess.run(["npm", "ci", "--offline", "--ignore-scripts", "--omit=optional"],
                   cwd=root, env=environment, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("archives", type=Path)
    args = parser.parse_args()
    install(args.root.resolve(), args.archives.resolve())
