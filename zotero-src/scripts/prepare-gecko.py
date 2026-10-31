#!/usr/bin/python3
"""Apply checked Gecko compatibility edits; compilation belongs to the spec."""

import argparse
import hashlib
import json
import re
from pathlib import Path


def prepare_native_threads(source):
    header = source / "third_party/rust/glslopt/glsl-optimizer/include/c11/threads_posix.h"
    contents = header.read_text()
    if "typedef pthread_once_t  once_flag;" not in contents and "glslopt_once_flag" not in contents:
        raise ValueError("Cannot patch glslopt C11 threading header")
    # These unused emulated APIs collide with modern glibc's stdlib.h.
    # Keep the other APIs, including Mesa's nonstandard static mutex initializer.
    for name in ("once_flag", "call_once"):
        contents = re.sub(r"\b" + name + r"\b", "glslopt_" + name, contents)
    header.write_text(contents)
    update_thread_checksum(source, header)


def update_thread_checksum(source, header):
    update_vendor_checksum(source / "third_party/rust/glslopt", header)


def update_vendor_checksum(crate, header):
    path = crate / ".cargo-checksum.json"
    checksums = json.loads(path.read_text())
    name = str(header.relative_to(crate))
    checksums["files"][name] = hashlib.sha256(header.read_bytes()).hexdigest()
    path.write_text(json.dumps(checksums, separators=(",", ":")) + "\n")


def replace_source(path, original, replacement):
    contents = path.read_text()
    if replacement in contents:
        return
    if contents.count(original) != 1:
        raise ValueError(f"Cannot apply Gecko compatibility patch: {path}")
    path.write_text(contents.replace(original, replacement))


def prepare_compatibility(source):
    crate = source / "third_party/rust/bindgen"
    compound = crate / "ir/comp.rs"
    # libclang 22 can return a forward declaration for a complete record type.
    replace_source(compound, "        let mut cursor = ty.declaration();",
                   "        let mut cursor = ty.declaration();\n"
                   "        if let Some(definition) = cursor.definition() {\n"
                   "            cursor = definition;\n"
                   "        }")
    update_vendor_checksum(crate, compound)
    crate = source / "third_party/rust/nss-gk-api"
    bindings = crate / "bindings/bindings.toml"
    replace_source(bindings, '    "SECItemStr",\n    "SECStatus",',
                   '    "SECItemStr",\n    "SECItemType",\n    "SECStatus",')
    update_vendor_checksum(crate, bindings)
    # Non-unified builds cannot rely on another translation unit's includes.
    protocol = source / "dom/webbrowserpersist/PWebBrowserPersistDocument.ipdl"
    replace_source(protocol, 'include "mozilla/dom/ReferrerInfoUtils.h";',
                   'include "mozilla/dom/PermissionMessageUtils.h";\n'
                   'include "mozilla/dom/ReferrerInfoUtils.h";')
    replace_source(source / "dom/base/PointerLockManager.cpp",
                   '#include "mozilla/dom/Document.h"',
                   '#include "mozilla/dom/Document.h"\n'
                   '#include "mozilla/dom/DocumentInlines.h"')
    transform = source / "gfx/skia/skia/modules/skcms/src/Transform_inl.h"
    # Use the public intrinsic rather than Clang's removed internal builtin.
    replace_source(transform,
                   "    typedef int16_t __attribute__((vector_size(16))) I16;\n"
                   "    return __builtin_ia32_vcvtph2ps256((I16)half);",
                   "    return (F)_mm256_cvtph_ps((__m128i)half);")
    seccomp = source / "security/sandbox/chromium/sandbox/linux/system_headers/linux_seccomp.h"
    # Read glibc's SYS_SECCOMP definition before supplying an older-libc fallback.
    replace_source(seccomp,
                   "#define SANDBOX_LINUX_SYSTEM_HEADERS_LINUX_SECCOMP_H_",
                   "#define SANDBOX_LINUX_SYSTEM_HEADERS_LINUX_SECCOMP_H_\n\n#include <signal.h>")
    pipewire = source / "third_party/libwebrtc/modules/video_capture/linux/pipewire_session.cc"
    replace_source(pipewire, "#include <spa/pod/parser.h>",
                    "#include <spa/pod/iter.h>\n#include <spa/pod/parser.h>")
    prepare_rust_targets(source)
    prepare_rust_debug_symbols(source)
    prepare_rust_lto(source)


def prepare_rust_lto(source):
    # ESR enables release Rust LTO even when mozconfig explicitly disables LTO.
    replace_source(source / "config/makefiles/rust.mk",
                   "cargo_rustc_flags += -Clto$(if $(filter full,$(MOZ_LTO_RUST_CROSS)),=fat)",
                   "cargo_rustc_flags += $(if $(MOZ_LTO),"
                   "-Clto$(if $(filter full,$(MOZ_LTO_RUST_CROSS)),=fat),-Clto=off)")


def prepare_rust_debug_symbols(source):
    # ESR otherwise expands C/C++'s minimal debug setting to full Rust debuginfo.
    replace_source(source / "build/moz.configure/rust.configure",
                   '    if debug_symbols:\n        debug_info = "2"',
                   '    if debug_symbols:\n'
                   '        debug_info = "1" if "-g1" in debug_symbols else "2"')


def prepare_rust_targets(source):
    # New Rust targets include OpenEmbedded GNU/Linux alongside unknown-vendor
    # GNU/Linux. Autoconf's pc vendor denotes the latter, not OpenEmbedded.
    configuration = source / "build/moz.configure/rust.configure"
    replace_source(configuration,
                   "        narrowed = [c for c in candidates if c.target.vendor == host_or_target.vendor]",
                   "        vendor = host_or_target.vendor\n"
                   '        if host_or_target.kernel == "Linux" and vendor == "pc":\n'
                   '            vendor = "unknown"\n'
                    "        narrowed = [c for c in candidates if c.target.vendor == vendor]")


def prepare_debug_source_paths(source):
    # Generated directives are otherwise relative to Gecko's object directory.
    # Preserve original input lines where that input exists; otherwise expose
    # the physical generated source that is actually present in the SRPM.
    files = {
        'gfx/angle/checkout/src/compiler/preprocessor/preprocessor_lex_autogen.cpp': {'preprocessor.l'},
        'gfx/angle/checkout/src/compiler/translator/glslang_lex_autogen.cpp': {'glslang.l'},
        'third_party/sqlite3/ext/fts5.c': None,
    }
    for name in ('hb-number-parser', 'hb-ot-shaper-indic-machine',
                 'hb-ot-shaper-khmer-machine', 'hb-ot-shaper-myanmar-machine',
                 'hb-ot-shaper-use-machine'):
        files[f'gfx/harfbuzz/src/{name}.hh'] = {f'{name}.hh', f'{name}.rl', 'NONE'}
    directive = re.compile(r'^(\s*#\s*line\s+)(\d+)(\s+)"([^"\n]+)"(.*)$')
    prepared = {}
    for relative, allowed in files.items():
        path = (source / relative).resolve()
        lines = path.read_text().splitlines(keepends=True)
        count = 0
        for index, line in enumerate(lines):
            match = directive.match(line.rstrip('\n'))
            if not match:
                continue
            original = match[4]
            if allowed is not None and original not in allowed:
                raise ValueError(f'Unexpected generated debug source: {relative}: {original}')
            if allowed is None and (Path(original).name != original or not original.startswith('fts5')):
                raise ValueError(f'Unexpected SQLite debug source: {original}')
            target = path.parent / original
            number = int(match[2])
            if not target.is_file():
                target, number = path, index + 2
            lines[index] = f'{match[1]}{number}{match[3]}"{target}"{match[5]}\n'
            count += 1
        if not count:
            raise ValueError(f'Missing generated debug directives: {relative}')
        prepared[path] = ''.join(lines)
    for path, contents in prepared.items():
        path.write_text(contents)


def prepare(source):
    prepare_native_threads(source)
    prepare_compatibility(source)
    prepare_debug_source_paths(source)
    ipdl = source / "ipc/ipdl/ipdl.py"
    original = "processes = min(processes, 8)"
    bounded = 'processes = min(processes, int(os.environ["RPM_BUILD_JOBS"]))'
    contents = ipdl.read_text()
    if original in contents:
        ipdl.write_text(contents.replace(original, bounded))
    elif bounded not in contents:
        raise ValueError("Cannot limit the IPDL worker pool")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    prepare(args.source.resolve())
