#!/usr/bin/python3
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest


spec = importlib.util.spec_from_file_location("prepare", Path(__file__).resolve().parents[1] / "scripts/prepare-source.py")
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)


class RuntimeCacheTest(unittest.TestCase):
    def test_local_archive_content_invalidates_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scripts = root / "app/scripts"
            scripts.mkdir(parents=True)
            runtime = root / "app/xulrunner/firefox-140.15.0esr-x86_64.tar.xz"
            runtime.parent.mkdir()
            runtime.write_bytes(b"first source build")
            script = scripts / "xulrunner_hash"
            script.write_text('''#!/bin/bash
set -euo pipefail
APP_ROOT_DIR="$(dirname "$(dirname "$0")")"
platform=l; arch=x86_64; components_hash=; GECKO_VERSION=140.15.0esr; xulrunner_content=scripts
input_string="${platform}-${arch}-${components_hash}|${GECKO_VERSION}|${xulrunner_content}"
printf "%s" "$input_string" | openssl dgst -sha256 | awk '{print $NF}'
''')
            prepare.prepare_runtime_cache(root)
            def digest():
                return subprocess.check_output(["bash", str(script)], text=True).strip()
            first = digest()
            self.assertEqual(first, digest())
            runtime.write_bytes(b"second source build")
            self.assertNotEqual(first, digest())
            runtime.unlink()
            missing = subprocess.run(["bash", str(script)], capture_output=True)
            self.assertNotEqual(missing.returncode, 0)


if __name__ == "__main__":
    unittest.main()
