Name:           binaryen125
Version:        125
Release:        6%{?dist}
Summary:        Coinstallable Binaryen tools for Emscripten 4.0.22
License:        Apache-2.0 AND MIT AND (Apache-2.0 WITH LLVM-exception)
URL:            https://github.com/WebAssembly/binaryen
Source0:        https://github.com/WebAssembly/binaryen/archive/refs/tags/version_%{version}/binaryen-version_%{version}.tar.gz
# Initialize optional DWARF fields before copying the records (GCC 16/LTO).
Patch0:         initialize-dwarf-records.patch
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  python3

%description
Compatibility Binaryen toolchain for Emscripten 4.0.22, installed in a private
prefix without replacing Fedora's current Binaryen tools.

%prep
%autosetup -p1 -n binaryen-version_%{version}

%build
# GCC 16 LTO warns in libstdc++'s std::function copy of stateless Strip lambdas.
# Retain the diagnostic, LTO, and all other -Werror checks, including format-security.
export CXXFLAGS="%{build_cxxflags} -Wno-error=maybe-uninitialized"
# Match upstream's $ORIGIN/../lib runtime lookup inside the private prefix.
%cmake -DCMAKE_INSTALL_PREFIX=%{_libdir}/binaryen125 -DCMAKE_INSTALL_LIBDIR=lib -DBUILD_TESTS=OFF
%cmake_build

%install
%cmake_install

%check
test -f %{buildroot}%{_libdir}/binaryen125/lib/libbinaryen.so
unset LD_LIBRARY_PATH
%{buildroot}%{_libdir}/binaryen125/bin/wasm-opt --version | grep -w %{version}

%files
%license LICENSE third_party/FP16/LICENSE third_party/llvm-project/include/llvm/LICENSE.TXT
%{_libdir}/binaryen125/

%changelog
* Mon Oct 26 2026 Matrew File <elfile4138@elfile4138.moe> - 125-6
- Match the private library directory to upstream's relative runtime path.
- Preserve Fedora's complete C++ build flags.

* Sat Oct 24 2026 Matrew File <elfile4138@elfile4138.moe> - 125-5
- Keep GCC 16 LTO maybe-uninitialized diagnostics nonfatal.

* Sat Oct 24 2026 Matrew File <elfile4138@elfile4138.moe> - 125-4
- Apply the DWARF initialization patch with its declared path prefix.

* Sat Oct 24 2026 Matrew File <elfile4138@elfile4138.moe> - 125-3
- Initialize DWARF records without disabling compiler diagnostics.

* Sat Oct 24 2026 Matrew File <elfile4138@elfile4138.moe> - 125-2
- Preserve the FP16 and LLVM input licenses alongside the project license.

* Sat Oct 24 2026 Matrew File <elfile4138@elfile4138.moe> - 125-1
- Add a coinstallable compatibility toolchain for source-built Zotero.
