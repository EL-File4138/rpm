#!/usr/bin/python3
"""Export the pinned Zotero release and every pinned recursive submodule.

Run after cloning https://github.com/zotero/zotero and initializing its
Linux submodules recursively. This exporter uses Git objects, excludes local
edits and Windows/macOS integration, and performs no network access. Remaining
binary replacements are handled in RPM prep.
"""

import argparse
from pathlib import Path
import subprocess
import tarfile
import tempfile


COMMIT = "35429ad62024032e0888b6cc1b6b51f96f8a8f1d"
VERSION = "10.0.7"
EXCLUDED = {
    "app/modules/zotero-word-for-mac-integration",
    "app/modules/zotero-word-for-windows-integration",
    "app/linux/updater.tar.xz",
    "app/mac/updater.tar.xz",
    "app/win/updater.exe.tar.xz",
    "app/win/zotero.exe.tar.xz",
}


def git_command(repository, *arguments):
    # git archive honors export filters. Disable LFS explicitly so it cannot
    # materialize binaries or contact a remote during an otherwise local export.
    return ["git", "-C", str(repository), "-c", "filter.lfs.process=",
            "-c", "filter.lfs.smudge=", "-c", "filter.lfs.required=false", *arguments]


def git(repository, *arguments):
    return subprocess.check_output(git_command(repository, *arguments))


def export(repository, revision, destination, relative, records):
    records.append(f"{relative.as_posix()};{revision}\n")
    with tempfile.TemporaryFile() as archive:
        exclusions = [f":(exclude){path}" for path in sorted(EXCLUDED)] if relative == Path(".") else []
        subprocess.run(git_command(repository, "archive", "--format=tar", revision, "--", ".", *exclusions),
                       stdout=archive, check=True)
        archive.seek(0)
        with tarfile.open(fileobj=archive) as source:
            source.extractall(destination, filter="data")
    for entry in git(repository, "ls-tree", "-rz", revision).split(b"\0"):
        if not entry:
            continue
        metadata, filename = entry.split(b"\t", 1)
        mode, kind, commit = metadata.decode().split()
        if mode != "160000":
            continue
        if kind != "commit":
            raise ValueError(f"Unexpected submodule object: {metadata!r}")
        path = Path(filename.decode())
        if (relative / path).as_posix() in EXCLUDED:
            continue
        child = repository / path
        if not (child / ".git").exists():
            raise ValueError(f"Submodule has not been initialized: {child}")
        target = destination / path
        target.mkdir(parents=True, exist_ok=True)
        export(child, commit, target, relative / path, records)


def prepare(repository, output):
    version = git(repository, "show", f"{COMMIT}:version").decode().strip()
    if version != f"{VERSION}.SOURCE":
        raise ValueError(f"Unexpected version at pinned commit: {version}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as temporary:
        root = Path(temporary) / f"zotero-{VERSION}"
        root.mkdir()
        records = []
        export(repository, COMMIT, root, Path("."), records)
        (root / "source-commits.txt").write_text("".join(records))
        partial = Path(temporary) / "source.tar.xz"
        with tarfile.open(partial, "w:xz") as archive:
            for path in [root, *sorted(root.rglob("*"))]:
                info = archive.gettarinfo(path, str(path.relative_to(root.parent)))
                info.uid = info.gid = info.mtime = 0
                info.uname = info.gname = "root"
                if info.isfile():
                    with path.open("rb") as source:
                        archive.addfile(info, source)
                else:
                    archive.addfile(info)
        partial.replace(output)
    print(f"Exported {len(records)} pinned repositories to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    prepare(args.checkout.resolve(), args.output.resolve())
