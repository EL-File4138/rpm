%global acorn_version 8.15.0
%global _smp_build_ncpus 1

Name:           emscripten-core
Version:        4.0.22
Release:        2%{?dist}
Summary:        Core C and C++ to WebAssembly compiler tools
License:        MIT AND Apache-2.0 WITH LLVM-exception AND BSD-2-Clause AND BSD-3-Clause AND Zlib
URL:            https://emscripten.org/
Source0:        https://github.com/emscripten-core/emscripten/archive/refs/tags/%{version}/emscripten-%{version}.tar.gz
Source1:        https://github.com/acornjs/acorn/archive/refs/tags/%{acorn_version}/acorn-%{acorn_version}.tar.gz
Source2:        install-core.py
Source3:        smoke-test.cpp
# Original inputs for the readable patched bundle in Source0. The bundled
# README's v4.8.0 branch reference is stale; this is the matching 5.18.2 fork.
Source4:        https://github.com/emscripten-core/terser/archive/692a6de2cfa9b741d8a857d8cccdb9b8564b429f/terser-692a6de2cfa9b741d8a857d8cccdb9b8564b429f.tar.gz
BuildArch:      noarch

BuildRequires:  python3
%if 0%{?fedora} > 44
BuildRequires:  clang22
BuildRequires:  llvm22
BuildRequires:  lld22
BuildRequires:  binaryen125
%else
BuildRequires:  clang >= 22
BuildRequires:  clang < 23
BuildRequires:  llvm >= 22
BuildRequires:  llvm < 23
BuildRequires:  lld >= 22
BuildRequires:  lld < 23
BuildRequires:  binaryen >= 125
BuildRequires:  binaryen < 127
%endif
BuildRequires:  nodejs >= 22

# These are runtime dependencies of the compiler. Packages compiling WASM
# declare emscripten-core in BuildRequires, not in their runtime Requires.
Requires:       python3
%if 0%{?fedora} > 44
Requires:       clang22
Requires:       llvm22
Requires:       lld22
Requires:       binaryen125
%else
Requires:       clang >= 22
Requires:       clang < 23
Requires:       llvm >= 22
Requires:       llvm < 23
Requires:       lld >= 22
Requires:       lld < 23
Requires:       binaryen >= 125
Requires:       binaryen < 127
%endif
Requires:       nodejs >= 22
Provides:       bundled(acorn) = %{acorn_version}
Provides:       bundled(terser) = 5.18.2
Provides:       bundled(musl) = 1.2.5
Provides:       bundled(mimalloc) = 2.1.7
# Emscripten carries patched snapshots of these target libraries. The sources
# ship with the compiler and are compiled for WASM, not linked to host libraries.
Provides:       bundled(compiler-rt)
Provides:       bundled(libcxx)
Provides:       bundled(libcxxabi)
Provides:       bundled(libunwind)
Provides:       bundled(llvm-libc)
Provides:       bundled(python3dist(leb128))

%description
Emscripten's core compiler, linker and build-system adapters for compiling C
and C++ to WebAssembly with system LLVM and Binaryen. Target system libraries
are compiled from the included sources into a writable cache on first use.

This package supports JavaScript and WebAssembly output. Optional npm-based
Closure compilation, Babel transpilation and HTML minification, WebIDL
bindings and third-party graphics/network ports are not included.

%prep
%autosetup -n emscripten-%{version}
%setup -q -T -D -a 1 -n emscripten-%{version}
%setup -q -T -D -a 4 -n emscripten-%{version}
# Test fixtures include executable artifacts; none are compiler inputs.
rm -rf test node_modules cache

%build
# Retain Emscripten's tested, readable Rollup output rather than introducing a
# different bundler's tree shaking/wrapper. Source4 carries its original inputs;
# the fork's nonstandard AST/TreeWalker exports rule out stock Terser replacement.
# The upstream launcher generator also writes test/runner.
mkdir -p test
%{__python3} tools/maint/create_entry_points.py
rm -rf test

%install
mkdir -p rpm-licenses/terser
cp third_party/terser/LICENSE rpm-licenses/terser/
%{__python3} %{SOURCE2} --destdir %{buildroot} --prefix %{_prefix} \
    --acorn acorn-%{acorn_version}/acorn \
%if 0%{?fedora} > 44
    --llvm-root %{_libdir}/llvm22/bin --binaryen-root %{_libdir}/binaryen125
%else
    --llvm-root %{_bindir} --binaryen-root %{_prefix}
%endif

%check
test -f terser-692a6de2cfa9b741d8a857d8cccdb9b8564b429f/lib/ast.js
test -f terser-692a6de2cfa9b741d8a857d8cccdb9b8564b429f/lib/parse.js
echo 'a3ba595680fa8a63400b1fb91b6f997b6c91585e97cfe3323d6b06903d326cc2  third_party/terser/terser.js' | sha256sum -c -
export EM_CACHE="$PWD/check-cache"
export EMCC_CORES=%{_smp_build_ncpus}
%{__python3} %{buildroot}%{_datadir}/emscripten/em++.py \
    --em-config %{buildroot}%{_datadir}/emscripten/.emscripten \
    -O2 %{SOURCE3} -o smoke-test.js
node smoke-test.js

%files
%license LICENSE rpm-licenses
%{_bindir}/emcc
%{_bindir}/em++
%{_bindir}/emar
%{_bindir}/emranlib
%{_bindir}/emstrip
%{_bindir}/emconfigure
%{_bindir}/emmake
%{_bindir}/emcmake
%{_bindir}/embuilder
%{_bindir}/em-config
%{_datadir}/emscripten/

%changelog
* Sat Oct 24 2026 Matrew File <elfile4138@elfile4138.moe> - 4.0.22-2
- Select coinstallable LLVM 22 and Binaryen 125 on Rawhide.

* Sun Sep 27 2026 Matrew File <elfile4138@elfile4138.moe> - 4.0.22-1
- Package the core compiler using system LLVM and Binaryen.
