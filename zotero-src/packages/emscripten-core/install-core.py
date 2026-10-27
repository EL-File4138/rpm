#!/usr/bin/python3
"""Install the source-based Emscripten core without npm or SDK downloads."""

import argparse
import json
from pathlib import Path
import shutil


COMMANDS = (
    "emcc", "em++", "emar", "emranlib", "emstrip", "emconfigure",
    "emmake", "emcmake", "embuilder", "em-config",
)


def install(destdir, prefix, acorn, llvm_root=None, binaryen_root=None):
    root = destdir / prefix.relative_to("/")
    target = root / "share/emscripten"
    target.mkdir(parents=True)
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", ".git")
    for directory in ("tools", "system", "src", "cmake"):
        shutil.copytree(directory, target / directory, ignore=ignore)
    for filename in ("LICENSE", "AUTHORS", "emscripten-version.txt"):
        shutil.copyfile(filename, target / filename)
    # All Python compiler entry points are needed by internal subprocesses.
    for source in Path(".").glob("em*.py"):
        shutil.copyfile(source, target / source.name)
    for command in COMMANDS:
        shutil.copyfile(command, target / command)
        (target / command).chmod(0o755)
    for library in ("terser", "leb128"):
        shutil.copytree(Path("third_party") / library,
                        target / "third_party" / library, ignore=ignore)
    shutil.copyfile("third_party/__init__.py", target / "third_party/__init__.py")
    shutil.rmtree(target / "tools/maint")
    (target / "tools/install.py").unlink()
    (target / "tools/webidl_binder.py").unlink()

    module = target / "node_modules/acorn"
    shutil.copytree(acorn / "src", module / "src")
    shutil.copyfile(acorn / "LICENSE", module / "LICENSE")
    package = json.loads((acorn / "package.json").read_text())
    (module / "package.json").write_text(json.dumps({
        "name": "acorn", "version": package["version"], "type": "module",
        "exports": "./src/index.js",
    }) + "\n")
    # The compiler must never try to write its cache into /usr/share. RPM builds
    # override this per-user default with an EM_CACHE under their build tree.
    (target / ".emscripten").write_text(
        "import os\n"
        f"LLVM_ROOT = {str(llvm_root or prefix / 'bin')!r}\n"
        f"BINARYEN_ROOT = {str(binaryen_root or prefix)!r}\n"
        f"NODE_JS = [{str(prefix / 'bin/node')!r}]\n"
        "CACHE = os.path.join(os.environ.get('XDG_CACHE_HOME', "
        "os.path.expanduser('~/.cache')), 'emscripten-4.0.22')\n"
    )
    bindir = root / "bin"
    bindir.mkdir(parents=True, exist_ok=True)
    for command in COMMANDS:
        wrapper = bindir / command
        wrapper.write_text(
            "#!/bin/sh\nexec /usr/bin/python3 -E "
            f"'{prefix}/share/emscripten/{command}.py' \"$@\"\n"
        )
        wrapper.chmod(0o755)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destdir", type=Path, required=True)
    parser.add_argument("--prefix", type=Path, default=Path("/usr"))
    parser.add_argument("--acorn", type=Path, required=True)
    parser.add_argument("--llvm-root", type=Path)
    parser.add_argument("--binaryen-root", type=Path)
    args = parser.parse_args()
    install(args.destdir, args.prefix, args.acorn, args.llvm_root, args.binaryen_root)
