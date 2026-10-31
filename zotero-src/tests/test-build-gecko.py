"""Regression checks for Gecko source compatibility patches."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock


spec = importlib.util.spec_from_file_location("prepare_gecko", Path(__file__).resolve().parents[1] / "scripts/prepare-gecko.py")
gecko = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gecko)


class BuildEnvironmentTest(unittest.TestCase):
    def test_system_libffi_is_selected_and_the_private_bundle_is_removed(self):
        configuration = (Path(__file__).resolve().parents[1] / "config/gecko.mozconfig").read_text()
        recipe = (Path(__file__).resolve().parents[1] / "zotero.spec").read_text()
        self.assertIn("ac_add_options --with-system-ffi\n", configuration)
        self.assertIn("BuildRequires:  pkgconfig(libffi)", recipe)
        command = next(line for line in recipe.splitlines()
                       if line.startswith("rm -rf .rpm-gecko/") and line.endswith("/js/src/ctypes/libffi"))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / ".rpm-gecko/firefox-test/js/src/ctypes/libffi"
            bundle.mkdir(parents=True)
            (bundle / "bundled.c").touch()
            sibling = bundle.parent / "moz.build"
            sibling.write_text("preserve")
            subprocess.run(["bash", "-ec", command.replace("%{gecko_version}", "test")],
                           cwd=root, check=True)
            self.assertFalse(bundle.exists())
            self.assertEqual(sibling.read_text(), "preserve")

    def test_gecko_owns_rust_flags_without_changing_parent_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ipdl = root / "ipc/ipdl/ipdl.py"
            ipdl.parent.mkdir(parents=True)
            ipdl.write_text("processes = min(processes, 8)\n")
            configuration = root / "config"
            configuration.write_text("ac_add_options --disable-debug-symbols\n")
            inherited = {"RUSTFLAGS": "-Copt-level=3 -Cdebuginfo=2",
                         "CARGO_ENCODED_RUSTFLAGS": "-Cdebuginfo=2",
                         "CFLAGS": "-O2 -flto=auto", "CXXFLAGS": "-O2 -flto=auto -fexceptions",
                         "TMPDIR": str(root / "persistent-tmp")}
            recipe = (Path(__file__).resolve().parents[1] / "zotero.spec").read_text()
            commands = recipe.split('# Level 1:', 1)[1].split('# Level 2:', 1)[0]
            commands = commands[commands.index('(\n'):]
            commands = commands.replace('%{gecko_version}', 'test')
            commands = commands.replace('%{_smp_build_ncpus}', '1')
            commands = commands.replace('%{SOURCE6}', str(configuration))
            (root / '.rpm-gecko/firefox-test').mkdir(parents=True)
            binary = root / 'bin'
            binary.mkdir()
            fake_python = binary / 'python3.11'
            fake_python.write_text('#!/bin/sh\nenv > environment\nmkdir -p obj-rpm/dist\n'
                                   'touch obj-rpm/dist/firefox-test.tar.xz\n')
            fake_python.chmod(0o755)
            environment = os.environ | inherited | {'PATH': str(binary) + ':' + os.environ['PATH']}
            Path(inherited['TMPDIR']).mkdir()
            subprocess.run(['bash', '-ec', commands], cwd=root, env=environment, check=True)
            values = dict(line.split('=', 1) for line in
                          (root / '.rpm-gecko/firefox-test/environment').read_text().splitlines()
                          if '=' in line)
            self.assertNotIn('RUSTFLAGS', values)
            self.assertNotIn('CARGO_ENCODED_RUSTFLAGS', values)
            self.assertEqual(values['CFLAGS'], inherited['CFLAGS'] + ' -fno-lto')
            self.assertEqual(values['CXXFLAGS'], inherited['CXXFLAGS'] + ' -fno-lto -fno-exceptions')


class NativeThreadsTest(unittest.TestCase):
    def test_native_threads_checksum_and_idempotence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            crate = root / "third_party/rust/glslopt"
            header = crate / "glsl-optimizer/include/c11/threads_posix.h"
            header.parent.mkdir(parents=True)
            header.write_text('''#include <pthread.h>
typedef pthread_once_t  once_flag;
typedef pthread_mutex_t mtx_t;
#define _MTX_INITIALIZER_NP PTHREAD_MUTEX_INITIALIZER
static inline void call_once(once_flag *flag, void (*func)(void)) {
    pthread_once(flag, func);
}
''')
            checksum = crate / ".cargo-checksum.json"
            checksum.write_text(json.dumps({"package": "unchanged", "files": {
                str(header.relative_to(crate)): "old", "other": "preserved",
            }}))
            gecko.prepare_native_threads(root)
            contents = header.read_bytes()
            gecko.prepare_native_threads(root)
            self.assertEqual(contents, header.read_bytes())
            manifest = json.loads(checksum.read_text())
            self.assertEqual(manifest["package"], "unchanged")
            self.assertEqual(manifest["files"]["other"], "preserved")
            self.assertEqual(manifest["files"][str(header.relative_to(crate))],
                             hashlib.sha256(contents).hexdigest())
            compiler = shutil.which("clang")
            if compiler:
                source = f'''#include <stdlib.h>
#include "{header}"
static glslopt_once_flag flag = PTHREAD_ONCE_INIT;
static mtx_t mutex = _MTX_INITIALIZER_NP;
void callback(void) {{}}
int main(void) {{
    pthread_barrier_t barrier;
    pthread_barrier_init(&barrier, 0, 1);
    glslopt_call_once(&flag, callback);
    return pthread_barrier_wait(&barrier);
}}
'''
                subprocess.run([compiler, "-std=gnu17", "-D_GNU_SOURCE", "-x", "c",
                                "-fsyntax-only", "-"], input=source, text=True, check=True)

    def test_unknown_header_fails_without_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            header = root / "third_party/rust/glslopt/glsl-optimizer/include/c11/threads_posix.h"
            header.parent.mkdir(parents=True)
            header.write_text("unexpected upstream header\n")
            with self.assertRaises(ValueError):
                gecko.prepare_native_threads(root)
            self.assertEqual(header.read_text(), "unexpected upstream header\n")


class RustTargetTest(unittest.TestCase):
    def test_pc_linux_vendor_mapping_preserves_other_vendors_and_platforms(self):
        from types import SimpleNamespace

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "build/moz.configure/rust.configure"
            path.parent.mkdir(parents=True)
            path.write_text(
                "def select(host_or_target, candidates):\n"
                "        narrowed = [c for c in candidates if c.target.vendor == host_or_target.vendor]\n"
                "        return [c.rust_target for c in narrowed]\n"
            )
            candidates = [SimpleNamespace(target=SimpleNamespace(vendor=vendor),
                                          rust_target=f"x86_64-{vendor}-linux-gnu")
                          for vendor in ("unknown", "oe")]
            original = {}
            exec(path.read_text(), original)
            host = SimpleNamespace(vendor="pc", kernel="Linux")
            self.assertEqual(original["select"](host, candidates), [])
            gecko.prepare_rust_targets(root)
            before = path.read_bytes()
            gecko.prepare_rust_targets(root)
            self.assertEqual(before, path.read_bytes())
            patched = {}
            exec(path.read_text(), patched)
            self.assertEqual(patched["select"](host, candidates),
                             ["x86_64-unknown-linux-gnu"])
            self.assertEqual(patched["select"](SimpleNamespace(vendor="oe", kernel="Linux"),
                                              candidates), ["x86_64-oe-linux-gnu"])
            self.assertEqual(patched["select"](SimpleNamespace(vendor="pc", kernel="WINNT"),
                                              candidates), [])


class RustDebugSymbolsTest(unittest.TestCase):
    def test_minimal_symbols_preserve_default_and_disabled_modes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "build/moz.configure/rust.configure"
            path.parent.mkdir(parents=True)
            path.write_text('def flags(debug_symbols):\n'
                            '    debug_info = None\n'
                            '    if debug_symbols:\n        debug_info = "2"\n'
                            '    return debug_info\n')
            original = {}
            exec(path.read_text(), original)
            self.assertEqual(original["flags"](("-g1",)), "2")
            gecko.prepare_rust_debug_symbols(root)
            before = path.read_bytes()
            gecko.prepare_rust_debug_symbols(root)
            self.assertEqual(before, path.read_bytes())
            patched = {}
            exec(path.read_text(), patched)
            self.assertEqual(patched["flags"](("-g1",)), "1")
            self.assertEqual(patched["flags"](("-g",)), "2")
            self.assertIsNone(patched["flags"](()))
            class Enabled(tuple):
                def __bool__(self):
                    return True
            self.assertEqual(patched["flags"](Enabled()), "2")


class RustLtoTest(unittest.TestCase):
    def test_disabled_lto_preserves_enabled_modes_and_existing_flags(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "config/makefiles/rust.mk"
            path.parent.mkdir(parents=True)
            path.write_text("cargo_rustc_flags = $(CARGO_RUSTCFLAGS)\n"
                            "cargo_rustc_flags += -Clto$(if $(filter full,$(MOZ_LTO_RUST_CROSS)),=fat)\n"
                            "all:\n\t@echo '$(cargo_rustc_flags)'\n")
            def flags(lto, cross=""):
                return subprocess.check_output(
                    ["make", "--no-print-directory", "-f", str(path),
                     f"MOZ_LTO={lto}", f"MOZ_LTO_RUST_CROSS={cross}",
                     "CARGO_RUSTCFLAGS=-Cdebuginfo=1"], text=True).strip()

            self.assertEqual(flags(""), "-Cdebuginfo=1 -Clto")
            gecko.prepare_rust_lto(root)
            before = path.read_bytes()
            gecko.prepare_rust_lto(root)
            self.assertEqual(before, path.read_bytes())
            self.assertEqual(flags(""), "-Cdebuginfo=1 -Clto=off")
            self.assertEqual(flags("1"), "-Cdebuginfo=1 -Clto")
            self.assertEqual(flags("1", "full"), "-Cdebuginfo=1 -Clto=fat")


class CompatibilityTest(unittest.TestCase):
    def test_patches_and_checksums_are_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixtures = {
                "third_party/rust/bindgen/ir/comp.rs": "        let mut cursor = ty.declaration();\n",
                "third_party/rust/nss-gk-api/bindings/bindings.toml": '    "SECItemStr",\n    "SECStatus",\n',
                "dom/webbrowserpersist/PWebBrowserPersistDocument.ipdl": 'include "mozilla/dom/ReferrerInfoUtils.h";\n',
                "gfx/skia/skia/modules/skcms/src/Transform_inl.h":
                    "    typedef int16_t __attribute__((vector_size(16))) I16;\n"
                    "    return __builtin_ia32_vcvtph2ps256((I16)half);\n",
                "security/sandbox/chromium/sandbox/linux/system_headers/linux_seccomp.h":
                    "#ifndef SANDBOX_LINUX_SYSTEM_HEADERS_LINUX_SECCOMP_H_\n"
                    "#define SANDBOX_LINUX_SYSTEM_HEADERS_LINUX_SECCOMP_H_\n"
                    "#ifndef SYS_SECCOMP\n#define SYS_SECCOMP 1\n#endif\n#endif\n",
                "third_party/libwebrtc/modules/video_capture/linux/pipewire_session.cc":
                    "#include <spa/pod/parser.h>\n",
                "build/moz.configure/rust.configure":
                    "        narrowed = [c for c in candidates if c.target.vendor == host_or_target.vendor]\n"
                    '    if debug_symbols:\n        debug_info = "2"\n',
                "config/makefiles/rust.mk":
                    "cargo_rustc_flags += -Clto$(if $(filter full,$(MOZ_LTO_RUST_CROSS)),=fat)\n",
                "dom/base/PointerLockManager.cpp": '#include "mozilla/dom/Document.h"\n',
            }
            for name, contents in fixtures.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(contents)
            for name in ("bindgen", "nss-gk-api"):
                crate = root / "third_party/rust" / name
                (crate / ".cargo-checksum.json").write_text(json.dumps({
                    "package": "preserved", "files": {"unrelated": "preserved"},
                }))
            gecko.prepare_compatibility(root)
            before = {name: (root / name).read_bytes() for name in fixtures}
            gecko.prepare_compatibility(root)
            self.assertEqual(before, {name: (root / name).read_bytes() for name in fixtures})
            self.assertIn(b"cursor.definition()", before[next(iter(fixtures))])
            self.assertIn(b"PermissionMessageUtils.h", before[list(fixtures)[2]])
            self.assertIn(b'#include "mozilla/dom/DocumentInlines.h"',
                          before["dom/base/PointerLockManager.cpp"])
            self.assertIn(b"#include <spa/pod/iter.h>", before[list(fixtures)[5]])
            compiler = shutil.which("clang++")
            if compiler:
                header = root / list(fixtures)[4]
                subprocess.run([compiler, "-std=c++17", "-x", "c++", "-fsyntax-only", "-"],
                               input=f'#include "{header}"\n#include <signal.h>\nstatic_assert(SYS_SECCOMP == 1);\n',
                               text=True, check=True)
            for name in ("bindgen", "nss-gk-api"):
                crate = root / "third_party/rust" / name
                manifest = json.loads((crate / ".cargo-checksum.json").read_text())
                self.assertEqual(manifest["package"], "preserved")
                self.assertEqual(manifest["files"]["unrelated"], "preserved")
                for filename, digest in manifest["files"].items():
                    if filename != "unrelated":
                        self.assertEqual(digest, hashlib.sha256((crate / filename).read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
