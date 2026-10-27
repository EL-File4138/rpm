%global llvm_major 22
%global _smp_build_ncpus 1

Name:           wasi-cxx-runtime
Version:        22.1.8
Release:        2%{?dist}
Summary:        Static WASI C++ libraries and compiler builtins
License:        Apache-2.0 WITH LLVM-exception
URL:            https://llvm.org/
Source0:        https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/llvm-project-%{version}.src.tar.xz
Source1:        build-runtime.py
Source2:        check-runtime.cpp
BuildArch:      noarch

%if 0%{?fedora} > 44
BuildRequires:  clang22
BuildRequires:  llvm22
BuildRequires:  lld22
%else
BuildRequires:  clang >= %{llvm_major}
BuildRequires:  clang < 23
BuildRequires:  llvm
BuildRequires:  lld
%endif
BuildRequires:  cmake
BuildRequires:  make
BuildRequires:  python3
BuildRequires:  wasi-libc-devel
BuildRequires:  wasi-libc-static
Requires:       wasi-libc-devel
Requires:       wasi-libc-static

%description
LLVM compiler builtins, libc++ headers, and static libc++/libc++abi libraries
for wasm32-wasi. This variant has no C++ exceptions or threads and supports
building Gecko's WebAssembly sandbox libraries using Fedora's WASI C library.

%prep
%autosetup -n llvm-project-%{version}.src

%build
%if 0%{?fedora} > 44
export PATH="%{_libdir}/llvm22/bin:$PATH"
%endif
%{__python3} %{SOURCE1} --jobs %{_smp_build_ncpus}

%install
install -d %{buildroot}%{_prefix}/wasm32-wasi/include/c++
cp -pr build-wasi/sysroot/include/c++/v1 %{buildroot}%{_prefix}/wasm32-wasi/include/c++/
install -d %{buildroot}%{_prefix}/wasm32-wasi/lib/wasm32-wasi
install -pm 0644 build-wasi/sysroot/lib/wasm32-wasi/libc++{,abi}.a \
    %{buildroot}%{_prefix}/wasm32-wasi/lib/wasm32-wasi/
install -Dpm 0644 build-wasi/clang-resource/lib/wasm32-unknown-wasi/libclang_rt.builtins.a \
    %{buildroot}%{_prefix}/lib/clang/%{llvm_major}/lib/wasm32-unknown-wasi/libclang_rt.builtins.a
mkdir -p licenses
for component in llvm compiler-rt libcxx libcxxabi; do
    install -pm 0644 "$component/LICENSE.TXT" "licenses/$component-LICENSE.TXT"
done

%check
%if 0%{?fedora} > 44
export PATH="%{_libdir}/llvm22/bin:$PATH"
%endif
clang++ --target=wasm32-wasi --sysroot="$PWD/build-wasi/sysroot" \
    -resource-dir="$PWD/build-wasi/clang-resource" \
    -isystem "$PWD/build-wasi/sysroot/include/c++/v1" \
    -fno-exceptions -fno-rtti %{SOURCE2} -o check-runtime.wasm
llvm-readobj --file-headers check-runtime.wasm | grep -q WASM

%files
%license licenses
%{_prefix}/wasm32-wasi/include/c++/
%{_prefix}/wasm32-wasi/lib/wasm32-wasi/libc++.a
%{_prefix}/wasm32-wasi/lib/wasm32-wasi/libc++abi.a
%{_prefix}/lib/clang/%{llvm_major}/lib/wasm32-unknown-wasi/

%changelog
* Sat Oct 24 2026 Matrew File <elfile4138@elfile4138.moe> - 22.1.8-2
- Build and check with Fedora's coinstallable LLVM 22 tools on Rawhide.

* Sun Sep 27 2026 Matrew File <elfile4138@elfile4138.moe> - 22.1.8-1
- Build WASI C++ libraries and compiler builtins from LLVM sources.
