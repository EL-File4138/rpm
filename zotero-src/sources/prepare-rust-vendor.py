#!/usr/bin/python3
"""Prepare an offline RPM source archive from a prepared, locked Cargo tree.

Run before rpmbuild, with network access. Apply packaging patches and the
packaged Cargo.lock to the source tree first. No host packages are installed.
"""

import argparse
from pathlib import Path
import subprocess
import tarfile
import tempfile
import tomllib


def rpm_version(version):
    # Match cargo2rpm: build metadata has no ordering significance, and RPM
    # sorts a tilde prerelease before the corresponding final version.
    release, separator, prerelease = version.split("+", 1)[0].partition("-")
    return release + ("~" + prerelease.replace("-", "_") if separator else "")


def prepare(source, output, metadata):
    source = source.resolve()
    if not (source / "Cargo.lock").is_file():
        raise ValueError("A checked-in Cargo.lock is required")
    output = output.resolve()
    metadata.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="rpm-cargo-vendor-") as temporary:
        work = Path(temporary)
        vendor = work / "vendor"
        result = subprocess.run([
            "cargo", "vendor", "--locked", "--versioned-dirs", str(vendor),
        ], cwd=source, check=True, text=True, stdout=subprocess.PIPE)
        config = result.stdout.replace(str(vendor), "vendor")
        tomllib.loads(config)
        (work / "vendor-config.toml").write_text(config)
        provides = []
        licenses = []
        for manifest in sorted(vendor.glob("*/Cargo.toml")):
            package = tomllib.loads(manifest.read_text())["package"]
            name, version = package["name"], package["version"]
            license_id = package.get("license")
            license_file = package.get("license-file")
            if not license_id and not license_file:
                raise ValueError(f"Missing license metadata for {name} {version}")
            provides.append(f"Provides: bundled(crate({name})) = {rpm_version(version)}")
            licenses.append(f"\n{'=' * 72}\n{name} {version}: {license_id or license_file}\n")
            # Preserve every supplied license/notice with its crate sources.
            # The inventory covers the complete source closure, including
            # dependencies for other targets and tests.
            notices = set()
            if license_file:
                notices.add(manifest.parent / license_file)
            for candidate in manifest.parent.rglob("*"):
                if candidate.is_file() and candidate.name.upper().startswith(
                    ("LICENSE", "LICENCE", "COPYING", "COPYRIGHT", "NOTICE")
                ):
                    notices.add(candidate)
            for notice in sorted(notices):
                licenses.append(f"--- {notice.relative_to(manifest.parent)} ---\n"
                                + notice.read_text(errors="strict"))
        (metadata / "bundled-provides.inc").write_text("\n".join(provides) + "\n")
        (metadata / "bundled-licenses.txt").write_text("\n".join(licenses) + "\n")

        def normalize(info):
            info.uid = info.gid = 0
            info.uname = info.gname = "root"
            info.mtime = 0
            return info

        output.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(output, "w:xz") as archive:
            for entry in sorted(work.iterdir()):
                archive.add(entry, arcname=entry.name, filter=normalize)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--metadata", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.source, args.output, args.metadata)
