#!/usr/bin/python3
"""Cross-build LLVM's WASI builtins and C++ libraries with Fedora's C library."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess


def run(*args):
    subprocess.run(list(map(str, args)), check=True)


def configure(source, build, settings):
    run("cmake", "-S", source, "-B", build,
        *(f"-D{name}={value}" for name, value in settings.items()))


def build_runtime(source, output, libc, jobs):
    output.mkdir(parents=True, exist_ok=True)
    sysroot = output / "sysroot"
    sysroot.mkdir(exist_ok=True)
    # Copy packaged C headers/libraries into a writable build sysroot. Only the
    # newly compiled C++ headers/libraries and compiler builtins are installed.
    for directory in ("include", "lib"):
        shutil.copytree(libc / directory, sysroot / directory, dirs_exist_ok=True)
    resource = output / "clang-resource"
    resource.mkdir(exist_ok=True)
    host_resource = Path(subprocess.check_output(["clang", "-print-resource-dir"], text=True).strip())
    if not (resource / "include").exists():
        (resource / "include").symlink_to(host_resource / "include", target_is_directory=True)
    common = {
        "CMAKE_SYSTEM_NAME": "Generic",
        "CMAKE_SYSTEM_PROCESSOR": "wasm32",
        "CMAKE_C_COMPILER": "clang",
        "CMAKE_CXX_COMPILER": "clang++",
        "CMAKE_ASM_COMPILER": "clang",
        "CMAKE_C_COMPILER_TARGET": "wasm32-wasi",
        "CMAKE_CXX_COMPILER_TARGET": "wasm32-wasi",
        "CMAKE_ASM_COMPILER_TARGET": "wasm32-wasi",
        "CMAKE_SYSROOT": str(sysroot),
        "CMAKE_TRY_COMPILE_TARGET_TYPE": "STATIC_LIBRARY",
        "CMAKE_BUILD_TYPE": "Release",
        "CMAKE_INSTALL_PREFIX": str(sysroot),
        "CMAKE_C_FLAGS": f"-resource-dir={resource}",
        "CMAKE_CXX_FLAGS": f"-resource-dir={resource}",
        "LLVM_INCLUDE_TESTS": "OFF",
    }
    builtins = output / "builtins"
    settings = common | {
        "COMPILER_RT_BAREMETAL_BUILD": "ON",
        "COMPILER_RT_DEFAULT_TARGET_ONLY": "ON",
        "COMPILER_RT_BUILD_BUILTINS": "ON",
        "COMPILER_RT_INCLUDE_TESTS": "OFF",
        "LLVM_ENABLE_PER_TARGET_RUNTIME_DIR": "ON",
        "COMPILER_RT_HAS_FPIC_FLAG": "OFF",
    }
    for component in ("SANITIZERS", "XRAY", "LIBFUZZER", "PROFILE", "CTX_PROFILE",
                      "MEMPROF", "ORC", "GWP_ASAN"):
        settings[f"COMPILER_RT_BUILD_{component}"] = "OFF"
    configure(source / "compiler-rt", builtins, settings)
    run("cmake", "--build", builtins, "--target", "builtins", "--parallel", jobs)
    libraries = list((builtins / "lib").rglob("libclang_rt.builtins*.a"))
    if len(libraries) != 1:
        raise ValueError(f"Expected one WASI builtins archive, found {libraries}")
    destination = resource / "lib/wasm32-unknown-wasi"
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(libraries[0], destination / "libclang_rt.builtins.a")
    cxx = output / "cxx"
    settings = common | {
        "LLVM_ENABLE_RUNTIMES": "libcxx;libcxxabi",
        "LLVM_ENABLE_PER_TARGET_RUNTIME_DIR": "OFF",
        "LIBCXX_CXX_ABI": "libcxxabi",
        "LIBCXX_ABI_VERSION": "2",
        "LIBCXX_ENABLE_ABI_LINKER_SCRIPT": "OFF",
        "LIBCXX_INCLUDE_BENCHMARKS": "OFF",
        "LIBCXXABI_ENABLE_STATIC_UNWINDER": "OFF",
        "LIBCXXABI_USE_LLVM_UNWINDER": "OFF",
        "LIBCXXABI_SILENT_TERMINATE": "ON",
    }
    for library in ("LIBCXX", "LIBCXXABI"):
        for feature in ("SHARED", "EXCEPTIONS", "THREADS"):
            settings[f"{library}_ENABLE_{feature}"] = "OFF"
        settings[f"{library}_ENABLE_STATIC"] = "ON"
        settings[f"{library}_INCLUDE_TESTS"] = "OFF"
        settings[f"{library}_INSTALL_LIBRARY_DIR"] = "lib/wasm32-wasi"
    configure(source / "runtimes", cxx, settings)
    run("cmake", "--build", cxx, "--target", "cxx", "cxxabi", "--parallel", jobs)
    run("cmake", "--install", cxx, "--component", "cxx-headers")
    run("cmake", "--install", cxx, "--component", "cxx")
    run("cmake", "--install", cxx, "--component", "cxxabi")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=Path("build-wasi"))
    parser.add_argument("--libc", type=Path, default=Path("/usr/wasm32-wasi"))
    parser.add_argument("--jobs", type=int, default=1)
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    os.environ["CMAKE_BUILD_PARALLEL_LEVEL"] = str(args.jobs)
    build_runtime(args.source.resolve(), args.output.resolve(), args.libc.resolve(), args.jobs)
